# reBotArm_control_py 代码详解

> 基于 `develop` 分支阅读，`main` 分支几乎是空的。
> 配套架构图：`reBotArm_control_py_architecture.drawio`

---

## 一句话总结

这个库做一件事：**把「末端要到达 (x,y,z)」翻译成「6 个电机各转多少度、发多大力矩」**，然后通过 MotorBridge SDK 发 CAN 帧给电机。

---

## 目录结构

```
reBotArm_control_py/
│
├── config/robot.yaml              ← 6 个关节的电机参数、CAN ID、PID 增益
├── urdf/                          ← URDF 机器人模型 + 3D mesh 文件（Pinocchio 读取）
│
├── reBotArm_control_py/           ← 库本体（4 个子模块）
│   ├── kinematics/                ← 正/逆运动学（位置层面：角度↔末端坐标）
│   ├── dynamics/                  ← 动力学（力的层面：力矩、重力、惯量）
│   ├── trajectory/                ← 轨迹规划（时间层面：怎么平滑地走过去）
│   ├── actuator/                  ← 执行器封装（硬件层面：和电机对话）
│   └── controllers/               ← 控制器（把上面几个粘起来，给用户用）
│
└── example/                       ← 示例程序（从简到难编号 0~10）
    ├── 0x01~4_*.py                ← 底层电机测试（不需要运动学）
    ├── 5~6_*.py                   ← 纯运动学测试（不需要真电机）
    ├── 7~8_*.py                   ← 完整控制（IK + 真机）
    ├── 9~10_*.py                  ← 重力补偿（动力学 + 真机）
    └── sim/                       ← 仿真可视化（Meshcat，不需要真机）
```

---

## 四个核心子模块

### 1. kinematics/ — 运动学（"角度和位置的互算"）

解决的问题：**6 个关节角度** ⇄ **末端在空间里的位置/姿态**

| 文件 | 核心函数 | 干什么的 |
|------|---------|---------|
| `robot_model.py` | `load_robot_model()` | 读 URDF 文件，构建 Pinocchio 模型 |
| | `get_joint_limits()` | 查询每个关节的角度范围 |
| | `get_end_effector_frame_id()` | 找到"末端"在 URDF 模型中的坐标帧 ID |
| `forward_kinematics.py` | `compute_fk(model, q)` | **正运动学**：6 个角度 → 末端 (x,y,z) + 旋转矩阵 |
| | `joint_to_pose(q)` | 便捷版：角度 → (位置, 欧拉角) |
| `inverse_kinematics.py` | `compute_ik(target_pos, target_rot, q_init)` | **逆运动学**：目标位姿 → 解出 6 个角度 |
| | `solve_ik_with_retry(...)` | 多初始值重试的 IK（更鲁棒） |

**调用示例**（你已经跑通的）：
```python
from reBotArm_control_py.kinematics import load_robot_model, compute_fk
model = load_robot_model()
pos, rot, T = compute_fk(model, [0,0,0,0,0,0])  # 归零 → (0.253, 0, 0.172)
```

### 2. dynamics/ — 动力学（"力和力矩的计算"）

解决的问题：知道关节角度/速度/加速度，算出需要多大的力矩

| 文件 | 核心函数 | 干什么的 |
|------|---------|---------|
| `robot_model.py` | `load_dynamics_model()` | 加载动力学模型（和 kinematics 的分开） |
| | `set_gravity(g)` | 设置重力方向（默认 [0,0,-9.81]） |
| `inertia.py` | `compute_mass_matrix(q)` | 质量矩阵 M(q)，6×6 |
| | `compute_coriolis_matrix(q, v)` | 科氏力矩阵 C(q,v) |
| | `compute_gravity_vector(q)` | **重力向量 g(q)**（重力补偿的核心） |
| | `compute_nle(q, v)` | 非线性项 = C(q,v)·v + g(q) |
| `forward_dynamics.py` | `compute_forward_dynamics(q, v, tau)` | 正动力学：给力矩 → 算加速度 |
| `inverse_dynamics.py` | `compute_inverse_dynamics(q, v, a)` | 逆动力学 (RNEA)：给加速度 → 算所需力矩 |
| | `compute_generalized_gravity(q)` | 广义重力（和 inertia 里的类似，快捷接口） |
| | `compute_static_torque(q)` | 静态保持力矩 |
| `derivatives.py` | `compute_rnea_derivatives(...)` | 动力学对 q/v/a 的偏导（高级用途） |
| `centroidal.py` | `compute_center_of_mass(q)` | 质心位置 |
| | `compute_centroidal_momentum(q, v)` | 质心动量 |
| `energy.py` | `compute_kinetic/potential/total_energy()` | 动能/势能/总能量 |

**关键理解**：重力补偿（example 9/10）只用了 `compute_generalized_gravity(q)`，算出当前姿态下每个关节该出多大力矩来抵消重力，然后通过 MIT 模式前馈给电机。

### 3. trajectory/ — 轨迹规划（"怎么平滑地走过去"）

解决的问题：不是直接跳到目标，而是规划一条平滑路径，让末端沿曲线运动。

| 文件 | 核心函数 | 干什么的 |
|------|---------|---------|
| `sampler.py` | `plan_cartesian_geodesic_trajectory()` | 在 SE(3) 空间（位置+姿态）规划测地线轨迹 |
| | `TrajProfile` | 时间轮廓：`LINEAR` / `MIN_JERK`（最小加加速度，最平滑）|
| | `TrajPlanParams` | 规划参数：dt、轮廓类型 |
| `clik_tracker.py` | `track_trajectory(cart_traj, q_init, ...)` | **CLIK 跟踪器**：把笛卡尔轨迹转成关节轨迹 |
| | `JointTrajectoryPoint` | 轨迹点数据结构（q + 时间戳） |
| `trajectory_planner.py` | `plan_joint_space_trajectory(...)` | 关节空间轨迹规划（直接插值关节角度） |
| | `compute_traj_stats()` | 轨迹统计信息 |

**数据流**（move_to_traj 的完整路径）：
```
目标位姿 → IK 解出目标角度
       → plan_cartesian_geodesic_trajectory() 规划笛卡尔轨迹
       → track_trajectory() 用 CLIK 转成关节轨迹
       → 逐点 pos_vel() 发给电机
```

### 4. actuator/ — 执行器封装（"和电机对话"）

| 文件 | 核心类/函数 | 干什么的 |
|------|---------|---------|
| `arm.py` | `RobotArm` 类 | 机械臂控制句柄，管理 6 个电机的全生命周期 |
| | `JointCfg` | 关节配置数据类 |
| | `load_cfg(yaml_path)` | 解析 robot.yaml |

**RobotArm 的关键操作**：

```
生命周期: connect() → enable() → [控制] → disable() → disconnect()
             ↑                                                 ↑
          mode_mit() / mode_pos_vel() / mode_vel()       stop_control_loop()
```

| 方法 | 作用 |
|------|------|
| `mode_mit()` | 切 MIT 模式（位置+速度+力矩前馈，适合重力补偿） |
| `mode_pos_vel()` | 切 POS_VEL 模式（位置+速度 PI 环，适合轨迹跟踪） |
| `mit(pos, vel, kp, kd, tau)` | 发送 MIT 控制命令 |
| `pos_vel(pos, vlim)` | 发送位置速度命令 |
| `get_state()` → `(pos, vel, torq)` | 读回 6 个关节的位置/速度/力矩 |
| `start_control_loop(callback, rate)` | 启动 500Hz 多线程控制循环 |
| `set_zero()` | 设当前位置为零点 |
| `estop()` | 紧急停止（= disable） |

---

## 控制器层：ArmEndPos

`controllers/arm_endpos_controller.py` 是目前唯一的高层控制器，把运动学、轨迹、执行器粘在一起：

```python
arm = RobotArm()
ctrl = ArmEndPos(arm)
ctrl.start()                               # 连接 + 使能 + POS_VEL 模式

ctrl.move_to_ik(x=0.3, y=0, z=0.3)        # 方式一：IK 直达（快但不平滑）
ctrl.move_to_traj(x=0.3, y=0, z=0.3,      # 方式二：轨迹规划（平滑、可控时长）
                  duration=2.0)

ctrl.end()                                  # safe_home() → disconnect()
```

- `move_to_ik`：只做 IK 解算，把目标角度设好，POS_VEL 模式自己走过去。简单快速，但路径不可控。
- `move_to_traj`：先 IK → 再规划笛卡尔测地线 → CLIK 转关节轨迹 → 逐点发送。末端走直线，平滑可控。

---

## 示例程序索引

从简到难，学习顺序建议照编号走：

| 编号 | 文件 | 需要真机？ | 干什么 |
|------|------|-----------|--------|
| 0x01 | `0x01damiao_text.py` | ✅ | 达妙电机底层通信测试 |
| 2 | `2_zero_and_read.py` | ✅ | 设零点 + 读取当前位置 |
| 3 | `3_mit_control.py` | ✅ | MIT 模式手动控制 |
| 4 | `4_pos_vel_control.py` | ✅ | POS_VEL 模式控制 |
| **5** | **`5_fk_test.py`** | ❌ | **正运动学测试**（你已跑通） |
| **6** | **`6_ik_test.py`** | ❌ | **逆运动学测试**（你已修 bug 并跑通） |
| 7 | `7_arm_ik_control.py` | ✅ | ArmEndPos + IK 交互控制 |
| 8 | `8_arm_traj_control.py` | ✅ | ArmEndPos + 轨迹规划控制 |
| 9 | `9_gravity_compensation.py` | ✅ | 重力补偿（动力学前馈） |
| 10 | `10_gravity_compensation_lock.py` | ✅ | 重力补偿 + 锁定位置 |
| sim | `sim/fk_sim.py` 等 | ❌ | Meshcat 3D 可视化仿真 |

---

## 配置文件 config/robot.yaml

```yaml
channel: /dev/ttyACM0     # 串口路径（也可以改成 can0）
rate: 500                  # 控制循环频率 Hz

joints:
  - name: joint1
    motor_id: 0x01         # 电机 CAN ID
    feedback_id: 0x11      # 反馈 CAN ID
    model: "4340P"         # 电机型号
    vendor: "damiao"       # 电机品牌
    MIT:                   # MIT 模式参数
      kp: 120.0            # 位置比例增益
      kd: 8.0              # 速度阻尼增益
    POS_VEL:               # 位置速度模式参数
      vel_kp / vel_ki      # 速度环 PI
      pos_kp / pos_ki      # 位置环 PI
      vlim: 5.0            # 最大速度限制 (rad/s)
```

- **J1~J3**（大关节）：DM4340P，kp=120, kd=8
- **J4~J6**（小关节）：DM4310，kp=18, kd=2

---

## 两个 robot_model.py 的区别

`kinematics/robot_model.py` 和 `dynamics/robot_model.py` 各有一个，功能类似但职责不同：

| | kinematics/robot_model.py | dynamics/robot_model.py |
|---|---|---|
| 加载函数 | `load_robot_model()` | `load_dynamics_model()` |
| 返回 | Pinocchio Model（用于 FK/IK） | Pinocchio Model（用于动力学） |
| 附加功能 | `get_joint_names/limits/frame_id` | `get/set_gravity()` |
| 谁调用 | kinematics 模块、ArmEndPos 控制器 | dynamics 模块、重力补偿示例 |

实际上底层都是同一个 URDF，但分开维护可以各自缓存 `model` 和 `data`，避免状态混乱。

---

## 三种控制模式对比

| 模式 | 切换方法 | 发送命令 | 适用场景 |
|------|---------|---------|---------|
| **MIT** | `arm.mode_mit(kp, kd)` | `arm.mit(pos, vel, kp, kd, tau)` | 力控、重力补偿、阻抗控制 |
| **POS_VEL** | `arm.mode_pos_vel()` | `arm.pos_vel(pos, vlim)` | 位置跟踪、轨迹执行 |
| **VEL** | `arm.mode_vel()` | `arm.set_vel(vel)` | 纯速度控制 |

- MIT 模式最灵活：`tau_motor = kp*(pos_target - pos) + kd*(vel_target - vel) + tau_ff`
- POS_VEL 模式最简单：给目标位置和速度限制，电机内部 PI 环自动跟踪
- 重力补偿用 MIT：kp 设小（2）、kd 设小（1），tau 前馈 g(q)

---

## 完整调用链路（以轨迹控制为例）

```
用户输入 (x, y, z, roll, pitch, yaw, duration)
    │
    ▼
ArmEndPos.move_to_traj()
    │
    ├─ 1. solve_ik()                    ← 逆运动学，算目标关节角
    ├─ 2. compute_fk() × 2              ← 算起点和终点的 SE(3) 变换
    ├─ 3. plan_cartesian_geodesic()     ← SE(3) 测地线，生成笛卡尔轨迹点
    ├─ 4. track_trajectory()            ← CLIK，每个笛卡尔点转成关节角度
    │
    └─ 5. 轨迹发送线程 _send_loop()
           │
           ├─ 逐点设置 _q_target
           │
           └─ 控制循环 _loop_cb()（500Hz）
                  │
                  └─ arm.pos_vel(_q_target, vlim)
                         │
                         └─ MotorBridge SDK → CAN → 电机转动
```

---

## 外部依赖一览

| 依赖 | 版本 | 作用 | 安装 |
|------|------|------|------|
| pinocchio (pin) | 3.9.0 | 运动学/动力学引擎 | `pip install pin`（Linux 推荐） |
| motorbridge | — | 底层电机控制 SDK | `pip install motorbridge` |
| numpy | — | 数值计算 | `pip install numpy` |
| pyyaml | — | 解析 robot.yaml | `pip install pyyaml` |
| meshcat | — | 3D 可视化（仅 sim 需要） | `pip install meshcat` |
| matplotlib | — | 绘图（可选） | `pip install matplotlib` |

> Pinocchio 在 Windows 下编译困难，建议使用 WSL2 Ubuntu（你已配好）。
