# MeshCat 可视化指南

> 面向机械工程师/硬件工程师的 MeshCat 快速上手教程

---

## 一、什么是 MeshCat？

### 1.1 一句话解释

**MeshCat = 浏览器里的 3D 机器人预览工具**，不需要装专门的 3D 软件，打开网页就能看到机器人模型。

### 1.2 为什么用 MeshCat？

| 对比项 | 传统方式 | MeshCat |
|--------|---------|---------|
| **安装** | 装 RViz / Gazebo（仅 Linux） | `pip install meshcat`（跨平台） |
| **显示** | 独立窗口 | 浏览器（Chrome/Edge/Firefox） |
| **远程访问** | 需要 VNC / X11 转发 | 直接访问 URL |
| **录屏** | 需要屏幕录制软件 | 浏览器自带开发者工具 |
| **调试** | 日志 + 终端 | 实时 3D + 交互 |

**核心优势**：
- ✅ **轻量**：不需要装 ROS / Gazebo
- ✅ **跨平台**：Windows / Mac / Linux / WSL2 都能用
- ✅ **远程友好**：服务器跑代码，本地浏览器看结果
- ✅ **易分享**：把 URL 发给同事，他也能看到同一个 3D 场景

### 1.3 工作原理

```
┌─────────────────┐         ┌──────────────────┐
│  Python 代码     │         │   浏览器          │
│                 │         │                  │
│ viz = Visualizer()  ──→  启动 Web 服务器     │
│                 │         │ (端口 7000)       │
│ viz.update(q)   │  ──→   │ 更新 3D 模型      │
│                 │         │                  │
│ viz.show_ik_pose() ──→   │ 显示红球+坐标轴   │
└─────────────────┘         └──────────────────┘
         ↑                           ↓
         └───── WebSocket 实时通信 ───┘
```

**技术栈**：
- **后端**：Python + ZMQ（消息队列）
- **前端**：Three.js（WebGL 3D 渲染）
- **通信**：WebSocket（实时双向）

---

## 二、快速上手

### 2.1 环境准备

**前提条件**：
- Python 3.10+
- 已安装 `pinocchio` 和 `meshcat`

**检查是否安装**：
```bash
python3 -c "import meshcat; print(meshcat.__version__)"
```

如果报错 `ModuleNotFoundError`，安装：
```bash
pip3 install meshcat
```

### 2.2 第一个例子：显示机械臂

**步骤 1：启动脚本**

在 WSL2 或 Linux 终端里：
```bash
cd /path/to/reBotArm_control_py
python3 example/sim/fk_sim.py
```

**步骤 2：打开浏览器**

终端会打印：
```
You can open the visualizer by visiting the following URL:
http://127.0.0.1:7000/static/
```

复制这个 URL，在 **Windows 浏览器**里打开（WSL2 的 localhost 可以直通 Windows）。

**步骤 3：输入关节角**

终端提示：
```
关节角度 > 
```

输入 6 个数字（空格分隔），单位是度：
```
0 0 0 0 0 0
```

按回车，浏览器里机械臂会摆到归零姿态。

**步骤 4：试试其他姿态**

```
0 -90 0 0 0 0    # 大臂水平
45 -30 15 -60 90 180  # 复杂姿态
```

### 2.3 浏览器操作

| 操作 | 效果 |
|------|------|
| **左键拖动** | 旋转视角 |
| **右键拖动** | 平移视角 |
| **滚轮** | 缩放 |
| **双击** | 聚焦到模型中心 |

**提示**：如果模型跑出视野，双击画布重新聚焦。

---

## 三、三个可视化工具详解

reBot-DevArm 提供了 3 个 MeshCat 可视化脚本，功能递进：

### 3.1 fk_sim.py — 正运动学可视化

**用途**：验证"给定关节角 → 末端位置"是否正确

**启动**：
```bash
python3 example/sim/fk_sim.py
```

**操作**：
1. 输入 6 个关节角（度）
2. 浏览器显示机械臂姿态
3. 终端打印末端位置 (x, y, z) 和姿态 (roll, pitch, yaw)

**示例**：
```
关节角度 > 0 0 0 0 0 0
  末端位置: [+0.253, +0.000, +0.172] m
  末端姿态: [+0.00, +0.00, +0.00] deg
```

**适用场景**：
- ✅ 检查 URDF 模型是否正确
- ✅ 验证关节限位
- ✅ 手动摆姿态拍照/录屏

---

### 3.2 ik_sim.py — 逆运动学可视化

**用途**：验证"给定目标位置 → 关节角"求解是否正确

**启动**：
```bash
python3 example/sim/ik_sim.py
```

**操作**：
1. 输入目标位置 `x y z`（米）
2. 或输入目标位姿 `x y z roll pitch yaw`（米 + 弧度）
3. 浏览器显示：
   - **红色小球**：目标位置
   - **三色坐标轴**（RGB = XYZ）：目标姿态
   - **机械臂**：自动摆到求解出的姿态

**示例**：
```
目标位姿 > 0.25 0.0 0.2
  [收敛] 迭代=9 误差=5.57e-05m
  关节角度(deg): [-0.046, -2.981, -6.408, 3.427, -0.046, 0.006]
```

**浏览器画面**：
- 红球出现在 (0.25, 0, 0.2) 位置
- 机械臂末端伸过去"够"到红球

**适用场景**：
- ✅ 测试某个点是否在工作空间内
- ✅ 验证 IK 求解器精度
- ✅ 调试姿态约束

**改进版特性**（已修复原版问题）：
- ✅ 显示目标点标记（红球 + 坐标轴）
- ✅ 连续求解时从上一个位置出发（不会每次从零位重启）
- ✅ 收敛率大幅提升

---

### 3.3 traj_sim.py — 轨迹规划可视化 ⭐⭐⭐

**用途**：验证"从当前位置 → 目标位置"的完整轨迹规划

**启动**：
```bash
python3 example/sim/traj_sim.py
```

**操作**：
1. 终端显示当前末端位置：`pos[0.253 0.000 0.172]`
2. 输入目标位姿（同 ik_sim）
3. 程序自动：
   - 规划 SE(3) 测地线轨迹（笛卡尔空间直线）
   - CLIK 逐帧跟踪（关节空间）
   - 浏览器动画回放

**示例**：
```
pos[0.253 0.000 0.172] rpy[-0.000 -0.000 0.000]> 0.3 0.0 0.25

============================================================
  轨迹: min_jerk  耗时=31.8ms  点数=51
  时长=1.00s  dt=0.02s  零空间=0.1
  关节: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] → [-0.0, -32.3, -17.7, -14.6, -0.0, 0.0]
============================================================
  IK 成功率: 96.1%  最大误差: 3.376e-04  平均误差: 5.237e-05

  播放动画 (MeshCat)...
```

**浏览器画面**：
1. **灰色路径线**：规划的参考轨迹（直线）
2. **机械臂动画**：1 秒内从起点移动到终点
3. **绿色路径线**：实际走过的轨迹（应该几乎重合灰色线）

**统计信息**：
```
--- 统计摘要 ---
  关节角度 (deg):
    j1: [-0.0, 0.0]
    j2: [-32.3, 0.0]
    j3: [-17.7, 0.0]
    ...
  笛卡尔误差 (m): avg=5.237e-05, max=3.376e-04
```

**适用场景**：
- ✅ 验证轨迹规划算法
- ✅ 检查跟踪精度（误差 < 0.1mm 说明算法质量高）
- ✅ 录制演示视频
- ✅ 调试零空间优化（避免关节限位）

**这是什么的"无硬件版"**：
- 对应 `reBotArm_control_py_运行流程.drawio` 里的**路径 A（move_to_traj）**
- 完整流程：IK → SE(3) 测地线 → CLIK → 动画播放

---

## 四、常见问题

### 4.1 浏览器打不开 MeshCat 地址

**现象**：访问 `http://127.0.0.1:7000/static/` 显示"无法访问此网站"

**原因 1：Windows 代理拦截**
- WSL2 启动时提示：`检测到 localhost 代理配置，但未镜像到 WSL`
- 浏览器的代理设置会拦截 localhost 访问

**解决方案**：
1. 打开浏览器代理设置
2. 在"请勿对以下列条目使用代理"里添加：`127.0.0.1;localhost`
3. 或者用无痕/隐身模式打开（通常不走代理）

**原因 2：端口被占用**
- 另一个程序已经占用 7000 端口

**解决方案**：
```bash
# 查看 7000 端口占用
netstat -ano | grep 7000
# 或者让 MeshCat 用其他端口（修改代码）
```

**原因 3：防火墙阻止**
- Windows 防火墙阻止 WSL2 访问

**解决方案**：
```powershell
# 在 Windows PowerShell（管理员）里运行
New-NetFirewallRule -DisplayName "WSL2" -Direction Inbound -Action Allow
```

### 4.2 看不到 3D 模型 / 显示空白

**现象**：浏览器打开了，但只有蓝色背景，没有机械臂

**原因 1：URDF 路径错误**
- 终端报错：`Mesh package://... could not be found`

**解决方案**：
- 检查 `urdf/reBot-DevArm_description_fixend` 是否是软链接
- WSL2 下需要手动重建：
  ```bash
  cd urdf
  rm reBot-DevArm_description_fixend
  ln -s reBot-DevArm_fixend_description reBot-DevArm_description_fixend
  ```

**原因 2：STL 文件缺失**
- `meshes/` 目录里的 `.STL` 文件不完整

**解决方案**：
```bash
ls urdf/reBot-DevArm_fixend_description/meshes/
# 应该看到 base_link.STL, link1.STL, ..., end_link.STL
```

**原因 3：浏览器 WebGL 未启用**
- 老旧浏览器或禁用了硬件加速

**解决方案**：
- 访问 `chrome://gpu/` 检查 WebGL 状态
- 或换用 Chrome / Edge 最新版

### 4.3 输入关节角后没反应

**现象**：终端输入数字回车，浏览器里机械臂不动

**原因 1：输入格式错误**
- 空格不是普通空格（全角空格 / Tab）
- 数字格式错误（逗号分隔 / 中文数字）

**解决方案**：
- 用英文输入法
- 确保是 6 个数字，空格分隔
- 例如：`0 -90 0 0 0 0`（不是 `0,-90,0,0,0,0`）

**原因 2：WebSocket 连接断开**
- 网络问题或浏览器休眠

**解决方案**：
- 刷新浏览器页面
- 或重启 Python 脚本

### 4.4 机械臂显示不完整 / 零件缺失

**现象**：只看到部分连杆，其他零件不见了

**原因**：某些 STL 文件加载失败

**解决方案**：
1. 检查终端是否有警告信息
2. 确认 `meshes/` 目录里所有 STL 文件都存在
3. 检查 URDF 里的 `<mesh filename="..."/>` 路径是否正确

### 4.5 动画播放卡顿

**现象**：`traj_sim.py` 播放轨迹时一卡一卡的

**原因 1：电脑性能不足**
- 浏览器渲染 3D 需要 GPU

**解决方案**：
- 关闭其他占用 GPU 的程序
- 降低轨迹点数（修改代码里的 `dt` 参数）

**原因 2：网络延迟**
- 远程访问 MeshCat（SSH 转发）

**解决方案**：
- 用本地浏览器访问
- 或录制视频后再看

---

## 五、进阶技巧

### 5.1 录制演示视频

**方法 1：浏览器自带录屏**
- Chrome：按 `F12` → 右上角三点 → More tools → Recorder
- 录制操作过程 → 导出视频

**方法 2：OBS Studio**
- 免费开源录屏软件
- 可以同时录制浏览器 + 终端

**方法 3：代码导出**
- MeshCat 支持导出为 HTML 文件（离线查看）
  ```python
  viz.meshcat.static_html()  # 生成 standalone HTML
  ```

### 5.2 自定义显示内容

**添加自定义几何体**（例如：目标点、障碍物）

```python
import meshcat.geometry as mcg

# 添加红色球体
viz.meshcat["target"].set_object(
    mcg.Sphere(0.02),  # 半径 2cm
    mcg.MeshLambertMaterial(color=0xff0000)  # 红色
)
viz.meshcat["target"].set_transform(
    tf.translation_matrix([0.3, 0, 0.25])  # 位置
)

# 添加绿色立方体（障碍物）
viz.meshcat["obstacle"].set_object(
    mcg.Box([0.1, 0.1, 0.1]),  # 10cm 立方体
    mcg.MeshLambertMaterial(color=0x00ff00)  # 绿色
)
```

**绘制路径线**

```python
# 灰色参考路径
points = [[0.2, 0, 0.2], [0.3, 0, 0.25], [0.25, 0.1, 0.3]]
viz.draw_ref_path(points)

# 绿色实际路径
viz.draw_actual_path(points)
```

### 5.3 多机器人同时显示

```python
viz1 = Visualizer()
viz1.meshcat["robot1"].set_object(...)

viz2 = Visualizer()
viz2.meshcat["robot2"].set_object(...)
```

### 5.4 远程访问

**场景**：服务器跑代码，本地浏览器看结果

**步骤**：
1. 服务器启动 MeshCat（会打印 `http://127.0.0.1:7000/static/`）
2. 本地 SSH 端口转发：
   ```bash
   ssh -L 7000:localhost:7000 user@server
   ```
3. 本地浏览器访问 `http://localhost:7000/static/`

---

## 六、与其他工具对比

| 工具 | 平台 | 安装难度 | 功能 | 适用场景 |
|------|------|---------|------|---------|
| **MeshCat** | 跨平台 | ⭐ 简单 | 3D 可视化 | 快速验证、远程调试 |
| **RViz** | Linux | ⭐⭐ 中等 | 3D + 传感器 + TF 树 | ROS 开发、多传感器融合 |
| **Gazebo** | Linux | ⭐⭐⭐ 复杂 | 物理仿真 | 动力学仿真、碰撞检测 |
| **Isaac Sim** | Linux/Win | ⭐⭐⭐⭐ 很复杂 | 高精度仿真 + AI 训练 | 强化学习、数字孪生 |
| **MATLAB Robotics** | 跨平台 | ⭐⭐ 中等 | 算法验证 | 学术研究、算法原型 |

**选择建议**：
- 🎯 **无硬件学习** → MeshCat（本教程）
- 🎯 **ROS 开发** → RViz
- 🎯 **物理仿真** → Gazebo / Isaac Sim
- 🎯 **算法研究** → MATLAB

---

## 七、总结

### 7.1 MeshCat 的核心价值

1. **零门槛**：不需要装 ROS / Gazebo，`pip install` 即可
2. **跨平台**：Windows / Mac / Linux / WSL2 通吃
3. **实时反馈**：改代码 → 刷新浏览器 → 立刻看到效果
4. **易分享**：把 URL 发给同事，远程协作

### 7.2 三个脚本的定位

| 脚本 | 用途 | 难度 | 推荐指数 |
|------|------|------|---------|
| `fk_sim.py` | 验证 FK 正确性 | ⭐ | ⭐⭐⭐ |
| `ik_sim.py` | 测试单点 IK 求解 | ⭐⭐ | ⭐⭐⭐⭐ |
| `traj_sim.py` | 完整轨迹规划演示 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**学习路径**：
1. 先跑 `fk_sim.py` 熟悉操作
2. 再跑 `ik_sim.py` 理解 IK
3. 最后跑 `traj_sim.py` 看完整流程

### 7.3 下一步

- ✅ 掌握 MeshCat 基本操作
- ✅ 理解 URDF 结构（参考《URDF 入门指南.md》）
- ⏳ 等待 Isaac Sim 官方教程（预计 2026-04-20）
- ⏳ 拿到真机后，结合 MeshCat 调试实机控制

---

## 附录：快速参考

### 常用命令

```bash
# 启动正运动学可视化
python3 example/sim/fk_sim.py

# 启动逆运动学可视化
python3 example/sim/ik_sim.py

# 启动轨迹规划可视化
python3 example/sim/traj_sim.py

# 检查 MeshCat 是否安装
python3 -c "import meshcat; print('OK')"

# 重建 URDF 软链接（WSL2）
cd urdf
rm reBot-DevArm_description_fixend
ln -s reBot-DevArm_fixend_description reBot-DevArm_description_fixend
```

### 浏览器快捷键

| 快捷键 | 功能 |
|--------|------|
| `F12` | 打开开发者工具（查看错误） |
| `Ctrl + R` | 刷新页面 |
| `Ctrl + Shift + R` | 强制刷新（清除缓存） |
| `F11` | 全屏 |

### 故障排查清单

- [ ] Python 环境是否正确（`python3 --version`）
- [ ] meshcat 是否安装（`pip3 list | grep meshcat`）
- [ ] URDF 软链接是否正确（`ls -la urdf/`）
- [ ] 浏览器代理是否排除 localhost
- [ ] 防火墙是否允许 7000 端口
- [ ] WebGL 是否启用（`chrome://gpu/`）

---

**🌟 如果遇到问题，先检查终端错误信息，90% 的问题都能从报错里找到线索！**