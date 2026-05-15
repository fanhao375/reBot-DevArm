# 遥操作与 LeRobot 待办

> 给自己看的笔记。**遥操作 + LeRobot 数据采集 + 模型训练**这条线的现状、决策点、未知问题清单。
> 建立时间：2026-05-15
> 配套探索区：`_lerobot_experiment/`（gitignored）

---

## 0. 这是啥

reBot Arm B601-DM 整机装起来跑通电机控制只是**第一阶段**。**第二阶段**是接 LeRobot 框架，做：
- 遥操作（leader 主臂控 follower 跟动）
- 数据采集（采集"看到 + 动作"的轨迹数据）
- 模型训练（ACT / SmolVLA / Pi0 / GR00T 等策略）
- 自主执行（训练好的模型替代 leader）

**这条线现在不紧迫**，但**复杂度比装机更高**——涉及硬件选型、几何匹配、框架集成、上游版本追踪等多维不确定性。本文档记录决策过程和待解决的未知。

**符号约定**（同装机烧录指南）：
- 🟢 已确认事实
- 🟡 TODO / 待实操验证
- ⚠️ 已知风险 / 坑
- ❓ 未知，需要查证

---

## 1. 当前状态（2026-05-15）

### 1.1 已有硬件

| 物品 | 状态 |
|---|---|
| reBot Arm B601-DM follower（达妙电机 6+1 DOF） | 🟡 电机已到，结构件待装 |
| reBot Arm 102 leader（Seeed 配套主臂，FashionStar RA8 舵机） | ❌ **没有**（2026-05-15 用户确认） |
| SO-ARM101 leader（Feetech 国产舵机替代方案） | ❌ **没有**（2026-05-15 用户确认） |

> ⚠️ **Leader 端完全空白**：用户原话"102 也没有。没决定。用哪个就去打"——意思是决定哪个 leader 就 3D 打印 + 买配件。这变成一次**完整的新装**决策，不是"已有 X 再加 Y"的增量决策。

### 1.2 已有软件

| 项目 | 当前版本 |
|---|---|
| `motorbridge` Python 包 | 0.2.8（Win + WSL 双端） |
| `motorbridge-gateway` 命令行 | 0.2.8 |
| `reBotArm_control_py` | submodule `062bef9`（含 `RobotArm.fresh()`） |
| LeRobot 主线 | clone 在 `_lerobot_experiment/lerobot/`（未装） |
| `lerobot-robot-seeed-b601`（follower 适配器） | clone 在探索区，未装 |
| `lerobot-teleoperator-rebot-arm-102`（leader 适配器） | clone 在探索区，未装 |

### 1.3 已确认的事实

- 🟢 `reBotArm_control_py` 是**单臂控制库**，**没有多臂/teleop 底层代码**（2026-05-15 grep 确认 0 匹配）—— 多臂逻辑完全在 LeRobot 框架层
- 🟢 `lerobot-robot-seeed-b601` 是为 reBot Arm B601-DM 写的 LeRobot Robot follower 适配器
  - 真的 `import motorbridge`，调 `add_damiao_motor()`
  - 关节配置 3×DM4340P + 4×DM4310，跟 `arm.yaml` 完全一致
  - 继承 `lerobot.robots.Robot` 主线接口
- 🟢 HuggingFace LeRobot 主线**官方支持 SO-100/SO-101 leader**（`src/lerobot/teleoperators/so_leader/`，一等公民）
- 🟢 `lerobot-robot-seeed-b601` 代码里有**"6 DOF leader 兼容"处理**（`if 'wrist_yaw' not in goal_pos: goal_pos['wrist_yaw'] = 0.0`），说明 SO-101 leader 控 reBot Arm follower 这条路**作者已经设计支持**

---

## 2. 决策矩阵：Leader 选型（SO-101 vs reBot 102）

参见 [memory: 遥操作 leader 选型风险](C:\Users\12440\.claude\projects\F--chengshenzhilu-Robot-reBot-DevArm\memory\project_teleop_leader_choice_risk.md)

| 维度 | reBot Arm 102 leader | SO-ARM101 leader |
|---|---|---|
| **整机散件价格** | 估 ¥1k-2k（含 7 个 RA8 舵机 + PCBD + 结构件）| ¥685 单臂（含 6 个 Feetech STS3215 + 电气小件，**不含 3D 打印**），加 3D 打印 ~¥800-900 |
| **关节数** | ✅ **7（6 DOF + gripper）跟 reBot Arm 1:1 对齐** | ⚠️ **6（5 DOF + gripper），少 wrist_yaw** — 0x05 那个电机锁死在 0°（follower 代码已 fallback） |
| **舵机是否标准品** | ❌ **RA8 定制款**（只能从 Seeed/FashionStar 整套买，无 pin-to-pin 替代） | ✅ **Feetech STS3215 通用品**（淘宝/AliExpress/Amazon 现货，Dynamixel/SCS 系列协议相近）|
| **舵机协议公开度** | 🟢 **完全公开**（`fashionstar_uart_sdk` MIT + motorbridge `motorbridge-smart-servo` MIT 重新实现）—— 详见附录 §A | 🟢 Feetech 协议社区多年逆向，HuggingFace LeRobot 主线**原生驱动** |
| **PCBD/接线板** | ✅ 简单 USB→RS485 板，市面通用品可替代（不算 lock-in） | ✅ 同（标准 USB→TTL 转换器） |
| **B601-DM 几何匹配** | 🟢 Seeed 配套出，**很可能已调**（未看到 wiki 明文确认） | ⚠️ **未实测**，关节范围/末端位置不一致，靠 `lerobot-calibrate` 归一化映射 |
| **LeRobot 集成成熟度** | Seeed `rebot_arm_102_leader`（9 commit 早期工程，单作者 Jack Shao） | ✅ HuggingFace `so_leader` 主线一等公民 |
| **校准复杂度** | `lerobot-calibrate` 一次基本可用 | 同 + 可能手调 joint_limits 让操作手感舒服 |
| **后续保养** | 跟 Seeed 早期工程绑定，bug 自己修 | HuggingFace 主线 + Feetech 社区维护 |
| **典型任务可用性** | ✅ 完整 6 DOF + 夹爪，**复杂动作**（斜插/拧瓶盖/装配）能做 | ⚠️ 5 DOF + 夹爪，**基础动作**（pick-place/堆积木/推拉）能做，**复杂动作有限** |

### 决策路径

**当前状态（2026-05-15）**：用户确认**两台 leader 都没买**，决定哪个就 3D 打印 + 买配件。

| 场景 | 推荐 |
|---|---|
| 学习 LeRobot 框架 + 跑通官方 demo + 简单任务 AI 训练 | **SO-101 起步**（省钱 + 标准品 + LeRobot 一等公民支持） |
| 展示 reBot Arm 全部 7 关节能力 + 复杂任务 + 严肃科研 | **102 必需**（不省那点钱浪费一个关节） |
| 介于两者 / 还没想好 | **SO-101 起步**——leader/follower 解耦，未来要升级 102 不动 reBot Arm |

> ⭐ **真正的 lock-in 在 RA8 舵机本身（硬件层），不在协议/PCB/SDK 层**——这是评估开源硬件的核心标准。SO-101 在"供应链开放性"上结构性优势明显。

---

## 3. 关键技术未知 ❓

### 3.1 "手调比例"具体指什么 🟢 已查清

实际是 3 类参数（在 `lerobot-robot-seeed-b601/.../seeed_b601_follower.py`）：

| 参数 | 含义 | 调整方式 |
|---|---|---|
| `joint_limits`（dict） | 每个关节软限位（度数）| `config_seeed_b601_dm_follower.py` 默认值；命令行 `--robot.joint_limits=...` override |
| `range_min` / `range_max` | 校准时每个电机物理可达范围 | `lerobot-calibrate` **自动生成**，存 `.cache/calibration/<id>.json` |
| `homing_offset` | 零点偏移 | `lerobot-calibrate` **自动生成** |

**B601-DM 默认 `joint_limits`**：

```python
"shoulder_pan":  (-145.0, 145.0),
"shoulder_lift": (-170.0, 1.0),
"elbow_flex":    (-200.0, 1.0),
"wrist_flex":    (-80.0, 90.0),
"wrist_yaw":     (-90.0, 90.0),
"wrist_roll":    (-90.0, 90.0),
"gripper":       (-270.0, 0.0),
```

**"调比例"实际上不是字面意义的"乘以一个比例系数"，而是改这些范围参数**。LeRobot 框架自动把 leader/follower 归一化到各自范围然后映射。

### 3.2 SO-101 leader 控 reBot Arm follower 实际能不能跑 ❓

- 🟢 **代码层兼容**：follower 适配器已经做了"6 DOF leader fallback"
- ❓ 但 **没人实测过**——0 个 GitHub issue 提到这个组合
- ❓ 关节几何映射后操控**手感**舒不舒服，只能买回来试

### 3.3 reBot Arm 102 leader 跟 B601-DM follower 的几何**真的**对齐了吗 ❓

- 推断：Seeed 自己配套出的应该对齐
- ❓ 但**没看到 Seeed wiki 明文确认**这点
- 🟡 等实操后才能确认

### 3.4 motorbridge-smart-servo 是啥 🟢 已查清

**结论**：是 MotorBridge 团队（tianrking 主导）**独立重新实现**的 FashionStar UART smart-servo 协议 Python 包，**MIT 开源** + PyPI 公开发布（pip install motorbridge-smart-servo）。

- **PyPI**：版本 0.0.3 / 0.0.4
- **架构**：Python wrapper + Rust core（PyO3 编译成 native 模块）
- **License**：MIT
- **Author**：tianrking（同 motorbridge 主项目）
- **当前状态**（METADATA 明文）：
  - ✅ Read/monitor APIs 支持（足够做 leader 用途）
  - ⏳ Write/control commands 暂时不支持（不影响 leader）
- **重大意义**：协议**不算 lock-in**——任何人能 pip install 用，源码 MIT 协议开放

### 3.5 Seeed 写的 leader 适配器跟 huggingface 主线 SO leader 接口完全对得上吗 ❓

- LeRobot 主线 Teleoperator 接口稳定，理论上一致
- ❓ 但 Seeed 自己魔改的 lerobot fork 落后主线 208 commit，意味着如果主线 Teleoperator 接口最近改过，Seeed 包可能跟不上

### 3.6 102 leader 能不能加重力补偿（"漂浮"手感）🟢 已查清

**结论：做不到达妙级别的"漂浮"重力补偿，只能 damping 近似**。

#### 真重力补偿（达妙级别）要的硬件能力

`tau = g(q)` 前馈，电机能"指定输出力矩值"——这需要：
- 力矩/电流环主动控制
- 上位机能下发"力矩目标"

#### RA8 舵机的实际能力（来自 [附录 §A](#附录-aFashionStar-uartrs485-协议完整规格) 命令码全表）

| 操作 | RA8 支持？ |
|---|---|
| 读位置 | ✅ CODE 10/16 |
| **读电流**（监控）| ✅ CODE 22 返回 Monitor_data 含 `current` 字段（mA） |
| 写位置 | ✅ CODE 8/11/12/13/14/15 |
| **写力矩 / 写电流** | ❌ **协议命令码 1-25 全表里没有 `SET_TORQUE` / `SET_CURRENT`** |
| Damping 模式 | ✅ CODE 9 `SET_DAMPING`（StopMode 0x12）|

⭐ 关键：RA8 是**位置伺服**电机，**不是力矩电机**。能告诉你它现在受多大外力（读电流），但不能让你"主动设力矩"——这两件事不是一回事。

#### 软替代方案对比

| 方案 | 原理 | 手感 | 工作量 |
|---|---|---|---|
| **A. 阻尼模式** | CODE 9 `SET_DAMPING`（mode=0x12，调整 power 参数） | 推得动有阻力但**仍下坠**（重力没补偿）| 1 行代码改 mode |
| **B. 实时位置追随**（hack）| 高频读位置 + 立刻发同位置作 target | 等价"零位置误差"，舵机维持当前位 | 简单但等价 lock |
| **C. 电流反馈估外力**（更难）| 读电流 → 反推外力 → 调位置 target 抵消 | 复杂、效果不稳，需专门调试 | 难，研究级 |
| **D. 机械配重 / 弹簧**（硬件方案）| leader 关节加扭簧抵消重力 | 物理方案，跟软件无关 | 需要硬件改造 |

#### ⚠️ 一个有意思的现状

`StarArm_102/Python_SDK/stararm102_ro.py` 当前用的是：

```python
leader_control.stop_on_control_mode(0xff, 0x10, 0x00)
#                                          ^^^^
#                                          0x10 = unlocked（完全松开，无阻尼）
```

**官方示例用的是"完全松开"，不是阻尼**！意思是当前 102 leader 推起来**比阻尼模式更"松"，但也没重力补偿**。

参考 mode 定义（来自 `uart_pocket_handler.py:StopOptions`）：
- `0x10 = unlocked` ← **当前用这个**（完全松开能自由推动）
- `0x11 = locked` （锁死不能推）
- `0x12 = damping` （**阻尼模式 ← 可以试一下**）

#### 实操建议

等你买 102 leader 后：
1. **默认体验**（unlocked）— 推感"松软"，垂下来
2. **试改 damping 模式**——把 `stararm102_ro.py` 第 41 行 / 43 行的 `0x10` 改 `0x12`，调 power 参数（4-255），找推感最舒服的值
3. **方案 C/D 不建议折腾**——投入产出比低

#### 跟 reBot Arm follower（达妙）对比

| | 102 leader（RA8） | reBot Arm follower（达妙）|
|---|---|---|
| 真重力补偿（漂浮） | ❌ 协议不支持 | ✅ 阶段 1 要跑的 `9_gravity_compensation.py` 就是这个 |
| 阻尼 leader 手感 | ✅ damping 模式可调 | — |
| 写代码即可 | 改 1 行 | 跑 demo 即可 |

> **意味着**：reBot Arm B601-DM 能"漂浮"是因为它是**力矩电机**，而 102 leader 永远不能"漂浮"是因为它是**位置伺服舵机**。这不是软件问题，是**硬件本质区别**。

---

## 4. 分阶段路线图

> 主线 = LeRobot AI 工作流。摄像头跟 ROS2 是**支线**，看后面说明。

### 主线：LeRobot AI 工作流

#### 阶段 0：装机烧录 ✅ 已完成（2026-05-15）

- 7 电机 ID + 7 零点 + 拼装 + Web UI 整机控制 + 24V 短路检查
- 详见 `装机烧录指南.md`

#### 阶段 1：单臂基础验证 🟡 当前

- 跑 `9_gravity_compensation.py` 重力补偿（**最有成就感的 demo**）
- 详见 `装机烧录指南.md §6.4`（完整 WSL cookbook + usbipd-win 流程）
- 跑 MotorBridge Web UI 拖滑块整机控制（已做过 ✅）
- 单电机命令行测试可跳过（Web UI 覆盖了）
- **不涉及 LeRobot**

#### 阶段 2：LeRobot follower 验证（无 leader，**不花钱**）

- 装环境：`pip install -e _lerobot_experiment/lerobot && pip install -e _lerobot_experiment/lerobot-robot-seeed-b601`
- 跑 `lerobot-calibrate --robot.type=seeed_b601_dm_follower --robot.port=/dev/ttyACM0 --robot.can_adapter=damiao`
- 用键盘 teleoperator（`--teleop.type=keyboard`）当 leader 测一次——能转动每个关节
- **验证目标**：follower 适配器在我们这套硬件上能跑
- **决策点**：跑通后判断是否真喜欢 LeRobot 路径——决定要不要往阶段 3 走

#### 阶段 3：决策 Leader 选型 + 买

| 路径 | 触发 |
|---|---|
| 买 102 leader | 想要 7 DOF 完整匹配 + 配套设计；接受 ~¥1k-2k + 定制舵机锁定 |
| **买 SO-101 leader**（推荐起步）| 6 DOF 够用 + 标准 Feetech 舵机 + ~¥800-900 + LeRobot 主线一等公民 |
| 都不买 | 走"键盘控+数据采集"路径，跳过物理 leader |

详见 §2 决策矩阵。

#### 阶段 4：装摄像头 + LeRobot 视觉集成

LeRobot **数据采集需要摄像头**——AI 学的是"看到啥 → 怎么动"的映射，纯关节角度不够。

- 选型：RealSense（深度+RGB）/ Orbbec（性价比）/ 普通 USB camera（最简）
- LeRobot 主线支持 RealSense 和 Orbbec
- Seeed wiki 教程 §11 有具体配置方法

> 没有摄像头：**只能采集关节空间数据**，能训练简单的"关节序列重现"模型，但学不出对环境的反应。

#### 阶段 5：数据采集

- `lerobot-record --robot.type=seeed_b601_dm_follower --teleop.type=so101_leader --dataset.num_episodes=N`
- 你手动遥操作 N 个 episode（每个 episode 完成一次任务）
- 每个 episode 录：摄像头视频 + 7 关节角度时序

#### 阶段 6：模型训练

- `lerobot-train --policy.type=act --steps=300000`（ACT 是 SOTA 入门模型）
- 也可以试 SmolVLA / Pi0 / GR00T（不同复杂度）
- 训练需要 GPU（本机或租云）

#### 阶段 7：部署

- 训练好的模型加载 → 替代 leader 自主执行
- `lerobot-eval` 评估准确率
- 真机部署，AI 自主完成 demo 任务

#### 阶段 8：升级到方案 A（fork + submodule）

只有阶段 2+3 都跑通才执行：

- GitHub fork `lerobot-robot-seeed-b601` 到 `fanhao375`
- （如果用 102）GitHub fork `lerobot-teleoperator-rebot-arm-102` 到 `fanhao375`
- 主仓加 submodule、配置 origin/upstream、走 sync 分支、baseline tag
- 详见 `复刻基线维护原则.md` 流程

---

### 平行支线 1：摄像头（跟主线绑定）

**不是独立项目**——是阶段 4-5 的硬件依赖。但选型可以提前考虑：

| 摄像头 | 价格 | 特点 | LeRobot 支持 |
|---|---|---|---|
| **Intel RealSense D435/D435i** | ~¥1500-2000 | 深度+RGB，最主流 | ✅ 一等公民 |
| **Orbbec Gemini 2** | ~¥800-1200 | 深度+RGB，国产 | ✅ 一等公民 |
| **普通 USB Webcam** | ~¥50-200 | 只 RGB | ✅ 通过 OpenCV |
| **iPhone/iPad（DroidCam）** | 零成本（手机现成）| 只 RGB | ⚠️ 需要 wrapper |

reBot Arm 主仓 4-26 同步时加入了**腕部相机支架**设计（D435/Gemini2、D405/Gemini305 都有 STEP 文件），可以 3D 打印挂在 wrist_roll 上。

---

### 平行支线 2：ROS2 + MoveIt 2（独立路径，可选）

跟 LeRobot 路径**完全独立**——传统机器人工作流，不依赖摄像头/AI 训练。

#### 跟 LeRobot 的差异

| 维度 | LeRobot 主线 | ROS2 支线 |
|---|---|---|
| 目的 | 让 AI 学会自己动 | 用传统算法精确控制（路径规划/碰撞检测）|
| 代表工具 | ACT / SmolVLA / Pi0 模型 | MoveIt 2 / Rviz |
| 输入 | leader 演示 + 摄像头 | URDF + 规划目标点 |
| 输出 | 端到端 AI 策略 | 关节空间/笛卡尔空间轨迹 |
| 学习曲线 | 中 | 陡 |

#### 你仓里的现状

- `software/reBotArmController_ROS2/`（submodule，已同步到 5-14 的 92ceb76）
- 含 MoveIt 2 集成包 `rebotarm_moveit_demos`：`demo_common.py` / `draw_square.py` / `pick_place.py`
- 含 4 种语言消息接口（`JointMitCmd` / `JointPosVelCmd` / `JointVelCmd` / `GripperCommand.srv`）

#### 入手路径（如果想学）

1. 装 ROS2 Humble（Ubuntu 22.04 / WSL）
2. `colcon build` 编译 reBotArmController_ROS2 workspace
3. 跑 `ros2 launch rebotarmcontroller driver.launch.py`（注意 5-14 重命名了，原来叫 `driver_only.launch.py`）
4. Rviz 看机械臂模型
5. 跑 `rebotarm_moveit_demos.pick_place` 试 MoveIt 2 规划
6. **不需要 leader / 不需要摄像头**

#### 建议时机

- 想做**严肃科研**或**找机器人工作**：**必学**
- 只想跑 LeRobot AI demo：**可以先不学**，等 LeRobot 跑通后回头补
- 想做**真机部署**（不是 demo 级别）：**几乎必学**（ROS2 是工业标准）

---

## 5. 待查证问题清单 🟡

按优先级排：

| 优先级 | 问题 | 怎么验证 |
|---|---|---|
| ⭐ 高 | follower 适配器在我们硬件上能不能 calibrate 成功 | 阶段 2 实操 |
| ⭐ 高 | **leader 选哪条线**（102 vs SO-101 vs 跳过物理 leader） | 阶段 3 决策点；触发条件是阶段 2 跑通 + 想做遥操作时 |
| 中 | `motorbridge-smart-servo` 是不是 MotorBridge 的新模块 | grep MotorBridge 仓 + 看 PyPI |
| 中 | LeRobot 主线 vs Seeed lerobot fork 落后 208 commit 是否影响 follower 适配器使用 | 阶段 2 装环境时遇到 import 报错就知道 |
| 中 | 7 关节 joint_limits 默认值是否合理（特别 elbow_flex (-200, 1) 是不是写反了？） | 实操跟达妙说明书对照 |
| 低 | SO-101 leader 控 reBot Arm 的操控手感 | 阶段 3 决策后买回来测 |

---

## 6. 探索区内容速查

```
_lerobot_experiment/                              ← gitignored，本地评估区
├── README.md                                     ← 探索区评估清单
├── lerobot/                                      ← huggingface/lerobot 主线 clone
├── lerobot-robot-seeed-b601/                     ← 关键：reBot Arm follower 适配器（410 行）
│   └── lerobot_robot_seeed_b601/
│       ├── seeed_b601_follower.py                ← 基类
│       ├── seeed_b601_dm_follower.py             ← 达妙子类（用这个）
│       ├── seeed_b601_rs_follower.py             ← RobStride 子类（不用）
│       ├── config_seeed_b601_dm_follower.py      ← 默认配置（joint_limits 等）
│       └── config_seeed_b601_rs_follower.py
├── lerobot-teleoperator-rebot-arm-102/           ← reBot 102 leader 适配器
│   └── lerobot_teleoperator_rebot_arm_102/       ← 用 motorbridge-smart-servo SDK
└── SO-ARM100/                                    ← TheRobotStudio SO-100/SO-101 硬件仓
    ├── STEP/SO101/                               ← 13 个 CAD 源文件（含 Seeed_Mounting_Plate）
    ├── STL/SO101/{Leader,Follower}/              ← 已合并打印件（Ender/Prusa）
    ├── Optional/                                 ← 相机支架/柔顺夹爪等扩展
    └── 3DPRINT.md                                ← 打印教程
```

> 🟢 SO-ARM100 仓内 `Seeedstudio_Mounting_Plate_SO101.step` 表明 **Seeed 官方认可 SO-ARM 跟 reBot 混搭**，并主动提供配套安装板设计

---

## 7. 风险登记

来自 memory 和实际调研：

| 风险 | 影响 | 应对 |
|---|---|---|
| SO-101 leader 跟 B601-DM 几何不匹配，操控手感差 | 中 | 决策前必须实物买回来测；不能凭便宜直接买 |
| **SO-101 leader 缺 wrist_yaw（6 关节 vs follower 7 关节）** | **中** | follower 代码有 fallback 锁 wrist_yaw=0°；基础任务影响小，复杂任务（斜插/装配/曲面）受限 |
| **102 leader 没法做真重力补偿（RA8 是位置伺服不是力矩电机）** | **低** | 接受这是硬件本质限制；只能用 damping 模式（CODE 9）做阻尼近似；详见 §3.6 |
| Seeed 的 leader/follower 适配器都是早期工程（9 commit / 8 commit、零 star、单作者） | 中 | 升级前先 fork pin 版本；定期看上游 commit |
| Seeed lerobot fork 落后主线 208 commit | 低 | 不用 Seeed fork，直接用 huggingface 主线 |
| motorbridge 是 wheel 手装、pyproject 没声明 | 中 | 复刻基线不可重现，需要写明确的安装步骤 |
| reBot Arm 102 leader 跟 B601-DM 几何对齐**没看到明文确认**（只是合理推断） | 中 | 实操跑通后回头补这条事实 |
| **RA8 舵机是定制款，没法用通用品替代** | **中** | 真正的硬件 lock-in；考虑 SO-101 这类标准品方案；详见 §2 决策矩阵 |

---

## 8. 关联文档

- `装机烧录指南.md`（阶段 0 详细流程）
- `复刻基线维护原则.md`（阶段 4 fork + submodule 规则）
- `_lerobot_experiment/README.md`（探索区评估清单 + 三仓详细评估）
- `项目总览.md`（整体项目结构）
- Memory：[遥操作 leader 选型风险](C:\Users\12440\.claude\projects\F--chengshenzhilu-Robot-reBot-DevArm\memory\project_teleop_leader_choice_risk.md)

---

## 9. 维护

- 阶段 2/3 跑通后回来更新 §1.3 已确认事实 + §5 待查证清单
- 决策 leader 后更新 §2 决策矩阵的实际选择
- 升级到方案 A 后把这条记到 §4 阶段 4 完成
- 风险点踩到了就移到 `装机烧录指南.md` §7 已知坑表

---

## 附录 §A：FashionStar UART/RS485 协议完整规格

> **来源**：`fashionstar_uart_sdk` v1.3.9 PyPI wheel 源码（`uservo.py`），MIT License。补充参考 `motorbridge-smart-servo` v0.0.4（同 MIT）。
> **更新日期**：2026-05-15
> **用途**：理解 102 leader 怎么工作；自己写驱动时查规格；评估开源透明度。

### A.1 物理层

| 参数 | 默认值 |
|---|---|
| 信号 | UART / RS485 差分 |
| 波特率 | **115200**（`fashionstar_uart_sdk` 默认）/ **1,000,000**（`motorbridge-smart-servo` 默认）—— 看舵机固件配置 |
| 校验位 | None |
| 停止位 | 1 |
| 数据位 | 8 |
| 多机共线 | 是（RS485 总线特性）|
| 舵机 ID 范围 | 0 ~ 253（254/255 保留为广播/特殊用途）|

### A.2 帧结构

```
┌─────────┬──────┬──────┬─────────────┬──────────┐
│ Header  │ CODE │ SIZE │   Payload   │ Checksum │
│  2 字节  │ 1 字 │ 1 字 │   N 字节    │   1 字   │
└─────────┴──────┴──────┴─────────────┴──────────┘
```

| 字段 | 字节数 | 内容 |
|---|---|---|
| Header | 2 | **请求**: `0x12 0x4C`<br>**响应**: `0x05 0x1C` |
| CODE | 1 | 命令码（见 A.3）|
| SIZE | 1 | Payload 字节数（不含本字段、不含 Header/CODE/Checksum） |
| Payload | SIZE | 命令参数，小端序 |
| Checksum | 1 | `sum(Header + CODE + SIZE + Payload) % 256` |

**校验算法**：简单求和模 256。⚠️ **不是 CRC**——抗位错能力较弱，依赖 RS485 短距电气环境。

### A.3 完整命令码表（CODE）

| CODE | 名称 | 类别 | 作用 |
|---|---|---|---|
| 1 | `CODE_PING` | 读 | 检测舵机在不在线 |
| 2 | `CODE_RESET_USER_DATA` | 写 | 用户表数据重置 |
| 3 | `CODE_READ_DATA` | 读 | 读内存表（任意寄存器）|
| 4 | `CODE_WRITE_DATA` | 写 | 写内存表（任意寄存器）|
| 5 | `CODE_QUERY_SERVO_INFO` | 读 | 查询所有信息（uservo.py 标注"未使用"）|
| 7 | `CODE_SET_SPIN` | 写 | 设置轮式模式（连续旋转） |
| **8** | **`CODE_SET_SERVO_ANGLE`** | **写** | **设置目标角度（基础写）** |
| 9 | `CODE_SET_DAMPING` | 写 | 阻尼模式（软挡，可被手动推动）|
| **10** | **`CODE_QUERY_SERVO_ANGLE`** | **读** | **查询单圈角度（基础读）** |
| 11 | `CODE_SET_SERVO_ANGLE_BY_INTERVAL` | 写 | 角度+到位时长(ms) |
| 12 | `CODE_SET_SERVO_ANGLE_BY_VELOCITY` | 写 | 角度+目标转速 |
| 13 | `CODE_SET_SERVO_ANGLE_MTURN` | 写 | 多圈角度直接到位 |
| 14 | `CODE_SET_SERVO_ANGLE_MTURN_BY_INTERVAL` | 写 | 多圈+周期 |
| 15 | `CODE_SET_SERVO_ANGLE_MTURN_BY_VELOCITY` | 写 | 多圈+转速 |
| **16** | **`CODE_QUERY_SERVO_ANGLE_MTURN`** | **读** | **查询多圈角度** |
| 17 | `CODE_RESET_MULTI_TURN_ANGLE` | 写 | 多圈角度计数重置 |
| 18 | `CODE_BEGIN_ASYNC` | 控 | 开始异步命令组（缓存命令不立即执行）|
| 19 | `CODE_END_ASYNC` | 控 | 结束异步命令组（一起执行）|
| **22** | **`CODE_QUERY_SERVO_MONITOR`** | **读** | **完整监控数据**（位置+电流+电压+功率+温度+状态）|
| 23 | `CODE_SET_ORIGIN_POINT` | 写 | 设当前位置为原点 |
| 24 | `CODE_SET_STOP_ON_CONTROL` | 写 | 控制模式停止指令 |
| **25** | **`CODE_SYNC_COMMAND`** | **同步** | **一次问/控多个舵机（leader 高频读用这个）** |

### A.4 实例：读 ID=1 舵机的单圈角度（CODE 10）

**请求帧**（电脑→舵机）：
```
0x12 0x4C          ← Header 请求
0x0A               ← CODE = 10 (QUERY_SERVO_ANGLE)
0x01               ← SIZE = 1 字节 payload
0x01               ← Payload: servo_id = 1
0x6A               ← Checksum: (0x12+0x4C+0x0A+0x01+0x01) % 256 = 0x6A
```
**总共 6 字节**。

**响应帧**（舵机→电脑）：
```
0x05 0x1C          ← Header 响应
0x0A               ← CODE = 10 (echo)
0x03               ← SIZE = 3 字节
0x01 0xXX 0xXX     ← Payload: id + 角度低位 + 角度高位（int16 度数×10）
0xXX               ← Checksum
```

### A.5 数据编码约定

- **角度单位**：度 × 10 的 int16
  - 范围 -3276.8° ~ 3276.7°
  - 单圈实际用 -1800 ~ 1800（即 -180.0° ~ 180.0°）
- **多圈角度**：int32 度 × 10（范围 -214,748,364.8° ~ 214,748,364.7°）
- **时长**：uint16 毫秒
- **转速**：int16 (deg/s × 10)
- **舵机 ID**：uint8

### A.6 关键代码引用

```python
# fashionstar_uart_sdk/uservo.py
class Packet:
    HEADER_LEN = 2
    HEADERS = [b'\x12\x4c', b'\x05\x1c']    # 请求 / 响应

    @classmethod
    def calc_checksum(cls, code, param_bytes=b'', pkt_type=1):
        header = cls.HEADERS[pkt_type]
        return sum(header + struct.pack('<BB', code, len(param_bytes)) + param_bytes) % 256

    @classmethod
    def pack(cls, code, param_bytes=b''):
        size = len(param_bytes)
        checksum = cls.calc_checksum(code, param_bytes, pkt_type=cls.PKT_TYPE_REQUEST)
        return cls.HEADERS[cls.PKT_TYPE_REQUEST] + struct.pack('<BB', code, size) + param_bytes + struct.pack('<B', checksum)
```

### A.7 协议开源状态总结

| 项 | 开源情况 |
|---|---|
| **完整帧格式** | ✅ MIT（uservo.py 源码）|
| **完整命令码表** | ✅ MIT（同上）|
| **校验算法** | ✅ MIT（同上）|
| **读命令（leader 用途）** | ✅ FashionStar SDK + motorbridge-smart-servo 都实现 |
| **写命令（follower / 控制运动）** | ✅ FashionStar SDK 已有；motorbridge-smart-servo 待补 |
| **RA8 特有寄存器/状态位** | ⚠️ 通用协议覆盖大部分，型号特有的少量行为可能需要逆向 |
| **三方实现可行性** | ✅ 任何人能基于这份规格写自己的驱动 |

### A.8 跟其他舵机协议的对比

| 协议 | 厂家 | 特点 |
|---|---|---|
| **FashionStar UART/RS485**（本附录）| 华馨京 | 校验和简单求和，单字节命令码 |
| **Dynamixel** | Robotis（韩国）| CRC16，工业标准，最丰富生态 |
| **Feetech SMS/STS**（SO-101 用）| Feetech（中国）| 类 Dynamixel 简化版，社区文档丰富 |

### A.9 自己写驱动的入手路径

如果你想脱离 FashionStar 官方 SDK 自己写：

1. **读这份附录** + 看 `uservo.py` 源码（不到 1000 行 Python，注释中文）
2. **实测**：插上 USB→RS485 转换器，先发 `CODE_PING` 帧给舵机，验证能收到响应
3. **逐个命令测试**：从 CODE 10（读位置）开始，确认字节流跟自己的实现匹配
4. **抓包对比**：用 `tio` / `screen` / `minicom` 监控串口字节流，跟 `uservo.py` 发出的对比
5. **写入命令验证**：CODE 8 / CODE 13 让舵机动起来确认控制链路

参考实现：
- Python 完整版：`fashionstar_uart_sdk` (PyPI)
- Rust 重写版（部分）：`motorbridge-smart-servo` (PyPI)
- C++ / Arduino / STM32 / ROS2：[servodevelop/servo-uart-rs485-sdk](https://github.com/servodevelop/servo-uart-rs485-sdk)
