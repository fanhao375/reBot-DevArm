# reBot-DevArm MeshCat 仿真代码详解

> 逐文件解读 `example/sim/` 下的 4 个仿真脚本
> 目标读者：懂 Python 基础，但不熟悉 Pinocchio / MeshCat 的工程师

---

## 这些代码干什么的？

`example/sim/` 文件夹提供了 **无需硬件** 即可验证运动学算法的仿真工具：

| 脚本 | 功能 | 对应的真机程序 |
|------|------|-------------|
| `fk_sim.py` | 输入关节角度 → 看末端到哪了 | `5_fk_test.py` |
| `ik_sim.py` | 输入目标位置 → 解出关节角度 | `6_ik_test.py` / `7_arm_ik_control.py` |
| `traj_sim.py` | 输入目标 → 规划完整运动轨迹 | `8_arm_traj_control.py` |
| `visualizer.py` | 底层封装：加载 URDF + MeshCat 渲染 | 被上面三个脚本调用 |

它们和真机程序的**唯一区别**：真机通过 MotorBridge 发 CAN 指令控制电机，仿真通过 MeshCat 在浏览器里显示 3D 模型。**算法完全一样**。

---

## 整体调用关系

```
fk_sim.py / ik_sim.py / traj_sim.py
         │
         ▼
    visualizer.py  ─────────────────────────┐
         │                                   │
         ▼                                   ▼
  Pinocchio (pin)                     MeshCat (meshcat)
  ├─ buildModelFromUrdf()             ├─ 启动 WebSocket 服务器
  ├─ buildGeomFromUrdf()              ├─ 加载 STL 模型到浏览器
  └─ MeshcatVisualizer.display(q)     └─ 实时更新 3D 姿态
         │
         ▼
  reBotArm_control_py/kinematics/
  ├─ compute_fk()       正运动学
  ├─ compute_ik()       逆运动学
  └─ plan_cartesian_geodesic_trajectory()  轨迹规划
```

---

## 文件 1：visualizer.py — 可视化器封装

> 📂 `example/sim/visualizer.py`（261 行）

### 核心职责

把 Pinocchio 模型加载和 MeshCat 渲染封装成一个简单的 `Visualizer` 类，上层脚本只需要：
```python
viz = Visualizer()       # 自动加载 URDF、启动 MeshCat
viz.update(q)            # 传入关节角度，浏览器里的模型就动了
```

### 初始化过程（`__init__`，第 40-66 行）

```python
def __init__(self, open_browser=True):
    # 1. 找到 URDF 文件路径
    urdf_path = _get_default_urdf_path()
    
    # 2. 用 Pinocchio 加载机器人模型（运动学模型 + 可视化模型）
    self._model = pin.buildModelFromUrdf(urdf_path)           # 运动学：关节、连杆、质量
    self._visual_model = pin.buildGeomFromUrdf(...)            # 可视化：STL 网格文件
    
    # 3. 启动 MeshCat WebSocket 服务器
    self._meshcat_viz = meshcat.Visualizer(zmq_url=None)       # zmq_url=None → 新开服务器
    
    # 4. 把 Pinocchio 模型加载到 MeshCat 浏览器
    self._viz = MeshcatVisualizer(self._model, ...)
    self._viz.initViewer(self._meshcat_viz, loadModel=False)
    self._viz.loadViewerModel()                                # 发送 STL 到浏览器
```

**关键理解**：
- `pin.buildModelFromUrdf()` 解析 URDF → 得到关节连接关系、质量、惯量
- `pin.buildGeomFromUrdf()` 解析 URDF → 得到每个 Link 对应的 STL 文件路径
- MeshCat 通过 WebSocket 把 STL 推到浏览器，后续 `display(q)` 只发关节角度，浏览器自己算位姿

### 主要方法

| 方法 | 作用 | 调用者 |
|------|------|--------|
| `update(q)` | 更新机器人姿态（核心方法） | 所有脚本 |
| `neutral()` | 恢复到零位 | ik_sim, traj_sim |
| `show_ik_pose(xyz, R, q)` | 显示 IK 目标（红球 + 三色轴）+ 更新姿态 | ik_sim |
| `draw_ref_path(points)` | 画灰色参考路径 | traj_sim |
| `draw_actual_path(points)` | 画绿色实际路径 | traj_sim |
| `clear_paths()` | 清除路径线 | traj_sim |
| `play_trajectory(name, dt, q_list)` | 逐帧播放轨迹动画 | 通用 |

### IK 目标可视化（`show_ik_pose`，第 136-170 行）

```python
def show_ik_pose(self, xyz, R, q):
    # 1. 构建 4x4 齐次变换矩阵
    H = np.eye(4)
    H[:3, :3] = R          # 旋转部分
    H[:3, 3] = xyz          # 平移部分
    
    # 2. 在目标位置显示三色坐标轴（RGB = XYZ）
    self._meshcat_viz["target/frame"].set_object(mcg.triad())
    self._meshcat_viz["target/frame"].set_transform(H)
    
    # 3. 在目标位置显示红色小球（半径 15mm）
    self._meshcat_viz["target/ball"].set_object(
        mcg.Sphere(0.015),
        mcg.MeshLambertMaterial(color=0xFF3300)
    )
    
    # 4. 更新机械臂到解算出的关节角度
    self.update(q)
```

**这就是你在浏览器里看到的红球和三色轴的来源。**

---

## 文件 2：fk_sim.py — 正运动学仿真

> 📂 `example/sim/fk_sim.py`（78 行）

### 功能

**输��� 6 个关节角度（度）→ 算出末端位置和姿态 → 浏览器实时显示**

这是最简单的仿真脚本，用来验证"关节转多少度 → 末端跑到哪"。

### 核心流程

```
用户输入: 45 -30 15 -60 90 180
    │
    ▼ np.radians() 转弧度
    │
    ▼ viz.update(q)          → MeshCat 更新 3D 模型
    │
    ▼ compute_fk(model, q)   ��� 返回 (位置, 旋转矩阵, 齐次矩阵)
    │
    ▼ 打印末端位置和姿态
```

### 关键代码（第 58-73 行）

```python
q = np.radians(q_deg)                              # 度 → 弧度
viz.update(q)                                       # 更新浏览器显示

pos, rot, _ = compute_fk(viz.model, q)              # 正运动学计算
euler = np.degrees(pin.rpy.matrixToRpy(rot))         # 旋转矩阵 → RPY 欧拉角
print(f"  末端位置: [{pos[0]:+.4f}, {pos[1]:+.4f}, {pos[2]:+.4f}] m")
print(f"  末端姿态: [{euler[0]:+.2f}, {euler[1]:+.2f}, {euler[2]:+.2f}] deg")
```

**`compute_fk` 内部做了什么**：Pinocchio 根据 URDF 定义的关节链，从 base_link 开始逐个计算每个 Link 的位姿（DH 参数 → 齐次变换矩阵连乘），最终得到 end_link 的位置和旋转。

---

## 文件 3：ik_sim.py — 逆运动学仿真

> 📂 `example/sim/ik_sim.py`（98 行）

### 功能

**输入目标位置 (x, y, z) → 解出 6 个关节角度 → 浏览器显示目标点 + 机械臂姿态**

和 FK 相反：FK 是"已知关节角 → 求末端位置"，IK 是"已知目标位置 → 求关节角"。

### 核心流程

```
用户输入: 0.25 0.0 0.15
    │
    ▼ target_pos = [0.25, 0.0, 0.15]
    │
    ▼ compute_ik(q_current, target_pos, target_rot)
    │   ├─ 从 q_current（上次的解）开始迭代
    │   ├─ 每步：算 Jacobian → 求增量 → 更新关节角
    │   └─ 返回 result.q（关节角）、result.success（是否收敛）
    │
    ▼ viz.show_ik_pose(target_pos, target_rot, result.q)
    │   ├─ 画红球 + 三色轴（目标位置）
    │   └─ 更新机械臂到解出的姿态
    │
    ▼ q_current = result.q.copy()   ← 保存，供下次使用
```

### 连续初值策略（第 44-89 行）

这是我们之前改进的核心功能。原版代码每次都从零位开始求解，容易掉进局部最小值导致不收敛。改进后：

```python
# 第 45 行：初始化
q_current = pin.neutral(viz._model)           # 第一次从零位开始

# 第 81 行：使用上次的解作为初值
result = compute_ik(q_current, target_pos, target_rot)

# 第 89 行：保存当前解
q_current = result.q.copy()                    # 下次从这个位置开始
```

**为什么有效**：IK 是迭代算法（CLIK），初始值越接近目标，收敛越快。连续输入的目标点通常不会跳太远，用上次的解作为起点比每次从零位开始好得多。

### 输入格式

```
0.25 0.0 0.15                  # 仅位置（3 个值，旋转不限制）
0.25 0.0 0.15 0 0.5 0.3        # 位置 + 姿态（6 个值，RPY 弧度）
```

---

## 文件 4：traj_sim.py — 轨迹规划仿真

> 📂 `example/sim/traj_sim.py`（234 行）

### 功能

**输入目标位姿 → SE(3) 测地线规划 → CLIK 关节空间跟踪 → 动画回放**

这是最复杂的仿真脚本，对应真机的 `move_to_traj()` 功能。它不是"一步到位"，而是规划一条从当前位置到目标位置的**平滑连续���迹**。

### 核心流程

```
用户输入: 0.3 0.0 0.25
    │
    ▼ (1) IK 预解算
    │   _solve_ik() → 确认目标可达，得到 q_end
    │
    ▼ (2) 计算运动时长
    │   duration = 距离 / 线速度（0.1 m/s），最短 1 秒
    │
    ▼ (3) run_trajectory()
    │   │
    │   ├─ SE(3) 测地线插值
    │   │   plan_cartesian_geodesic_trajectory(T_start, T_end, duration)
    │   │   → 在位置空间和旋转空间同时做平滑插值
    │   │   → 生成 N 个中间位姿点（笛卡尔空间）
    │   │
    │   ├─ CLIK 关节空间跟踪
    │   │   track_trajectory(model, cart_result, q_start)
    │   │   → 对每个中间位姿求 IK，得到关节角序列
    │   │   → 使用零空间优化保持关节接近中位
    │   │
    │   ├─ 统计信息
    │   │   compute_traj_stats() → IK 成功率、跟踪误差
    │   │
    │   └─ MeshCat 回放
    │       → 灰色线 = 笛卡尔规划路径
    │       → 绿色线 = 实际末端轨迹
    │       → 逐帧更新机械臂姿态
    │
    ▼ q_last = 最后一帧的关节角 ← 作为下次的起点
```

### 轨迹规划参数（第 64-71 行）

```python
dt = 1.0 / 50.0           # 采样间隔 = 20ms（50 Hz）
profile = TrajProfile.MIN_JERK    # 速度曲线：最小加加速度（最平滑）
accel_ratio = 0.25         # 加速段占总时长的 25%
null_gain = 0.1            # 零空间增益（关节趋向中位的力度）
ik_params = IKParams(
    max_iter=200,           # 每个点最多迭代 200 次
    tolerance=1e-4,         # 收敛精度 0.1mm
    damping=1e-6,           # 阻尼因子（防止 Jacobian 奇异）
    step_size=0.8,          # 步长（0.8 = 较激进，收敛快）
)
```

### SE(3) 测地线是什么？

普通的轨迹插值（分别对位置和旋转线性插值）会导致末端走弧线。SE(3) 测地线在**刚体运动群**上做插值，保证末端走最短路径（直线 + 最短旋转），物理意义上最合理。

### 回放动画（第 117-134 行）

```python
# 画参考路径（灰色）
viz.draw_ref_path(ref_positions)

# 逐帧回放
for i, pt in enumerate(joint_traj):
    viz.update(pt.q)                              # 更新机械臂姿态
    visited.append(ee_positions[i])
    viz.draw_actual_path(visited)                  # 画已走路径（绿色）
    time.sleep(max(0.002, times[i+1] - times[i])) # 按实际时间间隔播放
```

**浏览器里看到的效果**：灰色线是计划走的路径，绿色线是实际走的路径。两条线越接近，说明 CLIK 跟踪精度越高。

---

## 关键概念速查

| 概念 | 说明 | 在哪里用 |
|------|------|---------|
| **FK（正运动学）** | 关节角度 → 末端位姿 | fk_sim.py |
| **IK（逆运动学）** | 末端位姿 → 关节角度 | ik_sim.py |
| **CLIK** | 闭环迭代 IK，每步用 Jacobian 修正 | compute_ik() 内部 |
| **SE(3) 测地线** | 刚体运动群上的最短路径插值 | traj_sim.py |
| **零空间优化** | IK 有多解时，选择关节角接近中位的那个 | track_trajectory() |
| **MeshCat** | 浏览器 3D 可视化（WebSocket + Three.js） | visualizer.py |
| **齐次变换矩阵** | 4x4 矩阵，同时包含旋转 + 平移 | 所有文件 |

---

## 运行方法

```bash
cd software/reBotArm_control_py

# 正运动学
uv run python example/sim/fk_sim.py

# 逆运动学
uv run python example/sim/ik_sim.py

# 轨迹规划
uv run python example/sim/traj_sim.py
```

启动后自动打开浏览器 `http://127.0.0.1:7000/static/`，在终端输入数值即可交互。

---

## 与真机代码的对应关系

| 仿真代码 | 真机代码 | 区别 |
|----------|---------|------|
| `viz.update(q)` | `robot_arm.pos_vel(q, v)` | 仿真更新浏览器，真机发 CAN 指令 |
| `compute_fk(model, q)` | 相同 | 算法完全一样 |
| `compute_ik(q_init, pos, rot)` | 相同 | 算法完全一样 |
| `plan_cartesian_geodesic_trajectory()` | 相同 | 算法完全一样 |
| `track_trajectory()` | 相同 | 算法完全一样 |
| 手动输入目标 | `move_to_traj(target)` | 真机用控制器封装 |

**理解了仿真代码 = 理解了真机控制的核心算法**，差别只在最后一步：是推给浏览器还是推给电机。
