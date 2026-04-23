# reBot-DevArm 软件资料总览

> 整理日期：2026.04.14
> 来源：reBot-DevArm 项目 2026年4月更新，新增 Python SDK 和 Pinocchio 适配

---

## 这些东西从哪来的？

reBot-DevArm 主仓库（hardware/）从一开始就有硬件资料，但**一直没有软件代码**。
2026年4月更新后，路线图中两项标记为✅完成，指向了两个独立的外部仓库：

| 仓库 | 来源 | 说明 |
|------|------|------|
| **MotorBridge** | https://github.com/tianrking/MotorBridge | Python SDK 完成后指向的通用电机控制栈 |
| **reBotArm_control_py** | https://github.com/vectorBH6/reBotArm_control_py | Pinocchio 完成后指向的运动学控制库 |
| **wiki_docs** | https://wiki.seeedstudio.com/ | 官方 wiki 教程离线存档（10 个页面，OpenCLI 抓取） |

这些仓库本质上仍是独立项目；当前仓库通过 `git submodule` 方式固定它们的版本，方便学习、同步和复现。

说明：
- `MotorBridge` 当前直接跟踪上游仓库
- `reBotArm_control_py` 的源码上游是 `vectorBH6/reBotArm_control_py`，但本项目当前 submodule 指向 `fanhao375/reBotArm_control_py` 的 `develop`，用于承接本地修复并保证远端可复现

---

## 目录结构

```
software/
├── docs/                        📚 文档中心（新增）
│   ├── README.md                文档导航（推荐学习路径）
│   ├── 00_新手入门/
│   │   ├── URDF_入门指南.md     什么是 URDF、Link、Joint
│   │   ├── MeshCat_可视化指南.md 浏览器 3D 预览工具
│   │   └── README.md
│   ├── 01_项目专用/
│   │   ├── reBot-DevArm_URDF详解.md  逐行解读本项目 URDF（448 行注释）
│   │   └── README.md
│   ├── 02_reBotArm_control_py/
│   │   ├── reBotArm_control_py_说明.md  Python 上层控制库架构
│   │   ├── reBotArm_control_py_architecture.drawio  架构图
│   │   ├── reBotArm_control_py_运行流程.drawio  数据流图
│   │   └── README.md
│   └── 03_MotorBridge/
│       ├── MotorBridge_说明.md  Rust 底层电机库架构
│       ├── MotorBridge_architecture.drawio  架构图
│       ├── MotorBridge_运行流程.drawio  发送/反馈流程图
│       └── README.md
│
├── MotorBridge/                 底层：通用电机控制栈
│   ├── motor_core/              Rust 核心（CAN 通信抽象）
│   ├── motor_vendors/
│   │   ├── damiao/              达妙电机驱动（reBot DM版用这个）
│   │   ├── robstride/           RobStride 电机驱动（reBot RS版用这个）
│   │   ├── myactuator/          MyActuator 电机
│   │   ├── hightorque/          HighTorque 电机
│   │   ├── hexfellow/           Hexfellow 电机（CANopen）
│   │   └── template/            新厂商接入模板
│   ├── motor_cli/               命令行工具（扫描/使能/控制电机）
│   ├── motor_abi/               C ABI 稳定接口
│   ├── bindings/
│   │   ├── python/              Python 绑定
│   │   └── cpp/                 C++ 绑定
│   ├── integrations/            ROS2 等集成
│   └── examples/                使用示例
│
├── reBotArm_control_py/         上层：运动学控制库（develop 分支）
│   ├── config/
│   │   └── robot.yaml           关节配置（电机ID/型号/PID参数）
│   ├── reBotArm_control_py/     核心库
│   │   ├── actuator/            电机执行器封装
│   │   ├── kinematics/          正/逆运动学（Pinocchio）
│   │   ├── dynamics/            动力学（重力补偿）
│   │   ├── trajectory/          轨迹规划（SE3测地线）
│   │   └── controllers/         控制器
│   ├── example/                 示例程序（按学习顺序排列）
│   │   ├── 0x01damiao_text.py       单电机调试
│   │   ├── 2_zero_and_read.py       零位校准 + 角度监控
│   │   ├── 3_mit_control.py         MIT 模式控制
│   │   ├── 4_pos_vel_control.py     位置速度模式控制
│   │   ├── 5_fk_test.py             正运动学测试
│   │   ├── 6_ik_test.py             逆运动学测试
│   │   ├── 7_arm_ik_control.py      IK 实时控制真机
│   │   ├── 8_arm_traj_control.py    轨迹规划控制
│   │   ├── 9_gravity_compensation.py    重力补偿（自由拖动）
│   │   └── 10_gravity_compensation_lock.py  重力补偿+锁定
│   ├── urdf/                    URDF 模型
│   │   └── reBot-DevArm_fixend_description/
│   │       ├── urdf/            URDF 描述文件
│   │       ├── meshes/          3D 网格（base_link ~ link6 + end_link）
│   │       ├── launch/          ROS launch 文件
│   │       └── config/          关节名称配置
│   └── pyproject.toml           Python 项目配置
│
├── wiki_docs/                   官方 wiki 教程离线存档（OpenCLI 抓取）
│   ├── Getting_Started_with_Pinocchio_.../  Pinocchio + MeshCat 入门
│   ├── 达妙系列电机/                        达妙 43 系列电机完整教程
│   ├── RobStride_电机控制完整指南/          RobStride 电机多语言控制
│   ├── DM_Gripper_.../                      达妙夹爪组装指南
│   ├── SoArm_in_Lerobot/                   SO100 机械臂 LeRobot 教程
│   ├── Starai_Arm_in_ROS2_MoveIt/          StarAI 机械臂 MoveIt2 教程
│   ├── Install_the_ROS2_Humble/            ROS2 Humble 安装教程
│   └── Robotics/                            Seeed Studio 机器人资源总索引
│
└── README_zh.md                 本文件
```

---

## 两个仓库的关系

```
用户指令："移动到 x=0.3, y=0, z=0.2"
      │
      ▼
┌─────────────────────────────────────┐
│  reBotArm_control_py（上层控制）     │
│                                     │
│  逆运动学 → 6个关节该转多少度        │
│  轨迹规划 → 每个时间点的关节角度     │
│  重力补偿 → 抵消自重的力矩           │
└──────────────┬──────────────────────┘
               │ 调用
               ▼
┌─────────────────────────────────────┐
│  MotorBridge（底层电机控制）          │
│                                     │
│  把关节角度/力矩 → CAN 帧           │
│  通过 CAN 总线 → 发给 7 个电机      │
│  接收电机反馈 → 位置/速度/温度       │
└──────────────┬──────────────────────┘
               │ CAN 总线
               ▼
         7 个达妙电机转动
```

---

## 关节配置（来自 config/robot.yaml）

之前硬件文档里缺失的**关节-电机对应关系**，在这里找到了：

| 关节 | 电机型号 | CAN ID | 反馈 ID | 位置 | 控制参数 |
|------|---------|--------|---------|------|---------|
| joint1 | **DM4340P** | 0x01 | 0x11 | 底座旋转 | Kp=120, Kd=8 |
| joint2 | **DM4340P** | 0x02 | 0x12 | 肩部俯仰 | Kp=120, Kd=8 |
| joint3 | **DM4340P** | 0x03 | 0x13 | 大臂 | Kp=120, Kd=8 |
| joint4 | **DM4310** | 0x04 | 0x14 | 小臂 | Kp=18, Kd=2 |
| joint5 | **DM4310** | 0x05 | 0x15 | 腕部俯仰 | Kp=18, Kd=2 |
| joint6 | **DM4310** | 0x06 | 0x16 | 腕部旋转 | Kp=18, Kd=2 |

- 通信方式：串口桥 `/dev/ttyACM0`（达妙 USB2CAN）
- 控制频率：500 Hz
- 反馈 ID 规则：`feedback_id = motor_id + 0x10`

---

## 建议学习路径

### 📚 第零阶段：看文档（推荐新手先看）

> 目标：理解基本概念，不需要硬件

**强烈推荐先看 `docs/` 文件夹的文档！**

1. **`docs/00_新手入门/URDF_入门指南.md`** — 理解什么是 URDF、Link、Joint
2. **`docs/00_新手入门/MeshCat_可视化指南.md`** — 学会用浏览器看 3D 模型
3. **跑 MeshCat 三件套**（无硬件）：
   ```bash
   cd reBotArm_control_py
   python3 example/sim/fk_sim.py    # 正运动学可视化
   python3 example/sim/ik_sim.py    # 逆运动学可视化
   python3 example/sim/traj_sim.py  # 轨迹规划可视化
   ```
4. **`docs/01_项目专用/reBot-DevArm_URDF详解.md`** — 看懂本项目 URDF 为什么这么写
5. **`docs/02_reBotArm_control_py/`** — 理解运动学算法架构
6. **`docs/03_MotorBridge/`** — 理解电机控制架构

**完成第零阶段后，你会对整个系统有清晰的认识，再往下学会轻松很多。**

---

### 第一阶段：理解底层（MotorBridge）

> 目标：搞懂怎么让一个电机转起来

1. 读 `MotorBridge/README.zh-CN.md` — 了解架构
2. 读 `motor_vendors/damiao/src/protocol.rs` — 理解 CAN 协议实现
3. 用 CLI 工具试试扫描电机（需要硬件）：
   ```bash
   motorbridge-cli scan --vendor damiao --transport dm-serial \
     --serial-port /dev/ttyACM0 --serial-baud 921600
   ```

### 第二阶段：单电机控制（reBotArm example 1-4）

> 目标：控制单个电机的位置/速度/力矩

1. `0x01damiao_text.py` — 单电机交互调试（MIT/位置速度/速度模式）
2. `2_zero_and_read.py` — 零位校准 + 实时读取角度
3. `3_mit_control.py` — MIT 模式（位置+速度+Kp+Kd+力矩前馈）
4. `4_pos_vel_control.py` — 位置速度模式

### 第三阶段：运动学（reBotArm example 5-6）

> 目标：理解正/逆运动学

1. `5_fk_test.py` — 输入 6 个关节角 → 算出末端位姿（不需要硬件）
2. `6_ik_test.py` — 输入末端位姿 → 解出关节角（不需要硬件）
3. 读 `reBotArm_control_py/kinematics/` 源码 — 理解 Pinocchio 的用法

### 第四阶段：真机控制（reBotArm example 7-10）

> 目标：让机械臂真正动起来

1. `7_arm_ik_control.py` — 输入末端位置，IK 解算后控制真机
2. `8_arm_traj_control.py` — SE(3) 轨迹规划，平滑运动
3. `9_gravity_compensation.py` — 重力补偿，机械臂可自由拖动
4. `10_gravity_compensation_lock.py` — 重力补偿 + 位置锁定

### 第五阶段：深入源码

> 目标：能修改和扩展

- `reBotArm_control_py/actuator/` — 电机抽象层
- `reBotArm_control_py/kinematics/` — Pinocchio 正/逆运动学封装
- `reBotArm_control_py/dynamics/` — 动力学计算（重力补偿）
- `reBotArm_control_py/trajectory/` — SE(3) 测地线轨迹规划
- `reBotArm_control_py/controllers/` — CLIK 控制器
- `urdf/` — URDF 模型（可用于 ROS/仿真）

---

## 环境要求

| 项目 | 要求 |
|------|------|
| Python | 3.10+ |
| 操作系统 | Ubuntu 22.04+（推荐），Windows 可用 WSL2 |
| 硬件通信 | 达妙 USB2CAN 串口桥 或 标准 CAN 接口 |
| 包管理 | uv（推荐）或 pip |

### 安装步骤（无硬件也可学习运动学部分）

```bash
# 1. 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 进入项目
cd software/reBotArm_control_py

# 3. 安装依赖
uv sync

# 4. 测试正运动学（不需要硬件）
uv run python example/5_fk_test.py
```

---

## 待发布内容（截至 2026.04.12）

| 模块 | 状态 | 预计时间 |
|------|------|---------|
| 组装视频 | 🚧 进行中 | 2026.04.20 |
| ROS2 (Humble) + MoveIt2 | 🚧 进行中 | 2026.04.20 |
| Isaac Sim 仿真 | 🚧 进行中 | 2026.04.20 |
| LeRobot 适配 | 🚧 进行中 | 2026.04.30 |
| B601 RS 版硬件 | 🚧 进行中 | 2026.05 |
