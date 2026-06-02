# 遥操作与 LeRobot 待办

> 给自己看的笔记。**遥操作 + LeRobot 数据采集 + 模型训练**这条线的现状、决策点、未知问题清单。
> 建立时间：2026-05-15
> 配套探索区：`_lerobot_experiment/`（gitignored）
>
> ⭐ **如果你对"LeRobot vs ROS2 vs Isaac"这堆概念关系搞不清**，先看 [`AI机器人路径选择扫盲.md`](./AI机器人路径选择扫盲.md) 建立全局观再回来看本文。

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

## 1. 当前状态（2026-06-01）

### 1.1 已有硬件

| 物品 | 状态 |
|---|---|
| reBot Arm B601-DM follower（达妙电机 6+1 DOF） | ✅ 装机、ID、零点、Web UI、重力补偿、LeRobot follower 校准都已通过 |
| reBot Arm 102 leader（Seeed 配套主臂，FashionStar RA8 舵机） | 🟡 **决定做 102（2026-06-01）**：舵机已到货 + 自己 3D 打印结构件完成，**进入装配阶段**（⚠️ 官方装配教程尚未发布，见 §3.7） |
| SO-ARM101 leader（Feetech 国产舵机替代方案） | ❌ 不做（已选 102） |

> ⭐ **Leader 选型已落定（2026-06-01）：做 reBot Arm 102**。理由是要 7 DOF 完整匹配 + Seeed 配套设计（见 §2 决策矩阵"展示全部 7 关节 + 复杂任务"场景）。接受代价：~¥1k-2k + RA8 定制舵机的硬件 lock-in。当前在装配阶段。

### 1.2 已有软件

| 项目 | 当前版本 |
|---|---|
| 主仓源码基线 | `baseline-2026-05-28`，MotorBridge submodule 指向 v0.3.9 |
| WSL 重力补偿环境 `motorbridge` Python 包 | 0.3.7（本次真机验证版本） |
| LeRobot conda 环境 `motorbridge` Python 包 | 0.3.7（本次 follower 校准版本） |
| `motorbridge-gateway` 命令行 | 0.3.7/0.3.9 需按实际终端环境确认 |
| `reBotArm_control_py` | submodule `062bef9`（含 `RobotArm.fresh()`） |
| LeRobot 主线 | clone 在 `_lerobot_experiment/lerobot/`，conda 环境已装，`lerobot 0.5.2` |
| `lerobot-robot-seeed-b601`（follower 适配器） | 已装，`lerobot_robot_seeed_b601 0.1.2` |
| `lerobot-teleoperator-rebot-arm-102`（leader 适配器） | clone 在探索区，未装 |

### 1.3 已确认的事实

- 🟢 `reBotArm_control_py` 是**单臂控制库**，**没有多臂/teleop 底层代码**（2026-05-15 grep 确认 0 匹配）—— 多臂逻辑完全在 LeRobot 框架层
- 🟢 `lerobot-robot-seeed-b601` 是为 reBot Arm B601-DM 写的 LeRobot Robot follower 适配器
  - 真的 `import motorbridge`，调 `add_damiao_motor()`
  - 关节配置 3×DM4340P + 4×DM4310，跟 `arm.yaml` 完全一致
  - 继承 `lerobot.robots.Robot` 主线接口
- 🟢 本机已用 `seeed_b601_dm_follower` 完成 follower 校准，校准文件为 `~/.cache/huggingface/lerobot/calibration/robots/seeed_b601_dm_follower/follower1.json`
- 🟢 本机已确认总线扫描可发现 7 个达妙电机：`0x01..0x07`，反馈 ID `0x11..0x17`
- 🟢 本机已确认官方 LeRobot `--teleop.type=keyboard` 不适合直接做 B601 关节 jog；本仓新增 `tools/lerobot_b601_keyboard_jog.py`，默认每按一次动 1 度
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

> ✅ **已决策（2026-06-01）：做 reBot Arm 102 leader**。舵机到货 + 3D 件打印完成，进入装配。下面的决策矩阵作为历史依据保留。

**历史（2026-05-15）**：用户确认两台 leader 都没买，决定哪个就 3D 打印 + 买配件。

| 场景 | 推荐 |
|---|---|
| 学习 LeRobot 框架 + 跑通官方 demo + 简单任务 AI 训练 | SO-101 起步（省钱 + 标准品 + LeRobot 一等公民支持） |
| 展示 reBot Arm 全部 7 关节能力 + 复杂任务 + 严肃科研 | **102 必需**（不省那点钱浪费一个关节）← **最终选择走这条** |
| 介于两者 / 还没想好 | SO-101 起步——leader/follower 解耦，未来要升级 102 不动 reBot Arm |

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

### 3.7 官方 102 装配教程状态 ⚠️ 未发布（2026-06-01 查证）

- `遥操作/StarArm_102/Hardware/assembly/README.md` 当前内容只有一句："✨ 装配教程正在产出中，敬请期待。/ The assembly guide is currently in progress. Stay tuned."
- 🟡 意味着：3D 件已打印、舵机已到货，但**官方图文装配步骤还没出**。装配可参考来源：
  - `遥操作/StarArm_102/Hardware/cad/`（CAD 源文件）+ `Hardware/parts/`
  - `遥操作/StarArm_102/Media/images/`（可能有装配参考图）
  - B 站 / Seeed wiki 视频（需另找）
- 🟡 **待办**：定期看 `servodevelop/Star-Arm-102` 上游 `Hardware/assembly/` 有没有更新（这正是我们 fork 跟踪的仓）。

### 3.8 跨系统遥操作：102 leader 控 B601-DM follower，用哪个适配器 ❓

⚠️ **关键集成点**：`遥操作/StarArm_102/Lerobot/lerobot-teleoperator-stararm102/README.md` 自带的例子是 **102 leader → 102 follower**（整套 StarArm）：

```bash
lerobot-teleoperate \
    --robot.type=lerobot_robot_stararm102 \      # ← 102 follower，不是我们的 B601
    --teleop.type=lerobot_teleoperator_stararm102 \
    ...
```

但我们要的是 **102 leader → reBot Arm B601-DM（达妙/CAN）follower**，正确组合应该是：

```bash
lerobot-teleoperate \
    --robot.type=seeed_b601_dm_follower \        # ← 我们已校准的达妙 follower
    --robot.port=/dev/ttyACM0 --robot.can_adapter=damiao \
    --teleop.type=<102 leader 适配器> \           # ← 待确认是哪个
    --teleop.port=/dev/ttyUSB0 --teleop.id=...
```

❓ **待确认**：102 leader 适配器到底用哪个 / 关节名能不能跟 `seeed_b601_dm_follower` 对上：
- 候选 A：`遥操作/StarArm_102/Lerobot/lerobot-teleoperator-stararm102`（servodevelop/FashionStar 官方）
- 候选 B：`_lerobot_experiment/lerobot-teleoperator-rebot-arm-102`（Seeed 写的，§1.2 提到的，专门给 reBot Arm 配的）
- ⭐ 直觉：**候选 B（Seeed 的 rebot-arm-102）更可能跟 b601 follower 关节名对齐**，因为它是 Seeed 为 reBot 生态写的。装配完成后实测确认。
- 关联已知风险见 §3.5（Seeed 适配器接口跟主线对齐度）。

### 3.9 摄像头选型：主线用普通 RGB USB 即可，深度相机非必需 🟢 已查清（2026-06-01）

#### 结论先行

| 你的目标 | 该买啥 |
|---|---|
| **LeRobot AI 主线**（102 leader 遥操作 → 采数据 → 训 π0/ACT）← 你的实际目标 | **2 个普通 USB 摄像头**（腕部 + 俯视），深度相机**不用买** |
| 想顺便玩官方 YOLO 抓取 demo（支线） | 再单加 **1 个深度相机**（Gemini2）装腕部 |

#### 为什么主线不需要深度相机

- 🟢 LeRobot 的具身大模型（**π0 / π0.5 / π0.6 / ACT / SmolVLA / GR00T / OpenVLA**）视觉输入**都是 RGB**。它们站在 VLM（如 PaliGemma）肩膀上，VLM 用互联网海量 RGB 图预训练，天生吃彩色图、不吃深度。
- 🟢 你用普通 USB 摄像头采的「几路 RGB 视频 + 关节动作时序」**正是喂这类大模型的标准数据格式**，LeRobot 已集成 pi0 可直接微调。
- ⚠️ 深度相机（RealSense/Gemini2）只对**传统 CV 路线**是硬需求 —— 见下。

#### 为什么官方 YOLO 抓取 demo 必须用深度相机

- demo 模型：**YOLO**（`yoloe-26l-seg.pt`，开放词汇分割版）+ **OBB**（带方向最小外接矩形，短轴=夹爪开合方向），**Eye-in-Hand** 手眼标定。
- 原因：YOLO 是 **2D 模型**，只给「物体在画面哪个像素 + 朝向」，**不知道距离**。深度相机补上「距离」→ 算出 3D 抓取点 → 手眼标定换算机械臂坐标 → IK → 抓。
- 对比：LeRobot 的 AI 是端到端学「RGB 像素 → 动作」，几何关系从大量 2D 演示里隐式学会，不需要显式深度。
- demo 文档：`software/wiki_docs/reBot_Arm_B601-DM_Visual_Grasping_Demo/`。

#### 安装位置（两种，别搞混）

| 装法 | 位置 | 看到啥 |
|---|---|---|
| **腕部相机**（Eye-in-Hand） | 装手腕，跟夹爪一起动 | 夹爪正前方近距离特写 |
| **俯视/固定相机**（Eye-to-Hand） | 三脚架/夹子，不动，俯瞰桌面 | 整个工作台全景 |

- LeRobot 标准 = 2 个（腕部 + 俯视）；3 个（腕部 + 2 俯视角度）略好，边际收益递减、可选。
- ❌ **别买 2 个深度相机**：第二个深度的「深度」LeRobot 根本不用，纯浪费钱。

#### ⚠️ 关键坑（社区血泪）

**腕部和俯视千万别买两个一模一样的型号** —— 两个相同 USB 摄像头会导致 **USB 路径冲突，直接搞崩 LeRobot 数据录制程序**。必须用**两个不同厂家/型号**。

#### 购物清单（直接抄）

| 位置 | 买啥 / 淘宝关键词 | 参考价 | 备注 |
|---|---|---|---|
| 腕部 | 小 USB 摄像头模组：`USB摄像头模组 免驱 UVC 2MP 带3米线` / `32x32 摄像头模组` | ¥30-80 | ⭐ 正好配仓里 `hardware/reBot_B601_DM/3D_Printed_Parts/UVC32_mount.step`（32×32 UVC 模组支架）；线要长 |
| 俯视 | 普通网络摄像头：`罗技 C270` / `1080p USB摄像头 免驱` + `摄像头三脚架` | ¥100-300 | 跟腕部不同型号即可 |

**选购认 3 条**：① UVC 免驱（Linux 直接认 `/dev/video*`）② 720p 起步、1080p 足够（别为 4K 多花钱）③ 两个不同型号。

参考来源：[WowRobo SO-ARM 2MP 模组](https://shop.wowrobo.com/products/2mp-usb-camera-module-for-so-arm100-101-30fps-3m-cable)、[SO-ARM100 Overhead Cam Mount 32x32 UVC](https://github.com/TheRobotStudio/SO-ARM100/blob/main/Optional/Overhead_Cam_Mount_32x32_UVC_Module/README.md)、[Seeed SoArm in LeRobot wiki](https://wiki.seeedstudio.com/lerobot_so100m_new/)。

---

## 4. 分阶段路线图

> 主线 = LeRobot AI 工作流。摄像头跟 ROS2 是**支线**，看后面说明。

### 主线：LeRobot AI 工作流

#### 阶段 0：装机烧录 ✅ 已完成（2026-05-15）

- 7 电机 ID + 7 零点 + 拼装 + Web UI 整机控制 + 24V 短路检查
- 详见 `装机烧录指南.md`

#### 阶段 1：单臂基础验证 ✅ 已完成（2026-05-29）

- 跑 `9_gravity_compensation.py` 无锁重力补偿（已通过）
- 跑 `10_gravity_compensation_lock.py` 带锁重力补偿（已通过）
- 详见 `装机烧录指南.md §6.4`（完整 WSL cookbook + usbipd-win 流程）
- 跑 MotorBridge Web UI 拖滑块整机控制（已通过）
- 单电机命令行测试可跳过（Web UI 覆盖了）
- **不涉及 LeRobot**

#### 阶段 2：LeRobot follower 验证 ✅ 已完成（2026-05-29）

- 已装环境：`lerobot 0.5.2` + `lerobot_robot_seeed_b601 0.1.2` + `motorbridge 0.3.7`
- 已跑 `lerobot-calibrate --robot.type=seeed_b601_dm_follower --robot.port=/dev/ttyACM0 --robot.id=follower1 --robot.can_adapter=damiao`
- 已保存 follower 校准文件
- 已新增本地键盘 jog 工具：`tools/lerobot_b601_keyboard_jog.py`
- **验证目标已达成**：follower 适配器在我们这套硬件上能跑
- **当前决策点**：要不要进入阶段 3，选 SO-101 还是 reBot 102 leader

#### 阶段 3：决策 Leader 选型 + 买 ✅ 已决策（2026-06-01）

**选择：做 reBot Arm 102 leader**（7 DOF 完整匹配 + Seeed 配套设计；接受 ~¥1k-2k + RA8 定制舵机锁定）。详见 §2 决策矩阵。

进入装配阶段，子步骤：

| 子步骤 | 状态 |
|---|---|
| 买舵机（7×FashionStar RA8） | ✅ 到货（2026-06-01） |
| 3D 打印结构件 | ✅ 完成（2026-06-01，自己打印） |
| 机械装配 | 🟡 待做（⚠️ 官方装配教程未发布，见 §3.7） |
| 舵机 ID 烧录（7 个，UART/RS485） | 🟡 待做（参考 `Python_SDK/` + FashionStar SDK） |
| 接线 + USB→RS485 转换器 + 上电测试 | 🟡 待做 |
| 单臂 Python SDK 跑通（`Python_SDK/stararm102_ro.py` 读各关节角度） | 🟡 待做 |

完成后进入跨系统遥操作集成（见 §3.8）。

#### 阶段 4：装摄像头 + LeRobot 视觉集成

LeRobot **数据采集需要摄像头**——AI 学的是"看到啥 → 怎么动"的映射，纯关节角度不够。

> ✅ **选型已定调（2026-06-01）：主线买普通 RGB USB 摄像头即可，不需要深度相机**。完整论证见 §3.9。一句话：LeRobot 的具身大模型（π0 / ACT / SmolVLA）只吃 RGB，深度相机只有传统 YOLO 抓取 demo 才用（支线，可选）。
>
> **标准配置 = 2 个普通 USB 摄像头**：腕部（eye-in-hand）+ 俯视（eye-to-hand）。详细购物清单见 §3.9 / 支线1。

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

**不是独立项目**——是阶段 4-5 的硬件依赖。

> ✅ **选型结论见 §3.9**：主线买**普通 RGB USB 摄像头 ×2**（腕部小模组 + 俯视罗技，两个别同款），深度相机非必需。下表为全部候选对比，供参考。

| 摄像头 | 价格 | 特点 | LeRobot 支持 | 用途 |
|---|---|---|---|---|
| **小 USB 摄像头模组**（UVC 免驱，带长线） | ~¥30-80 | 只 RGB，小体积可上腕部 | ✅ OpenCV | ⭐ **腕部首选** |
| **普通 USB Webcam**（罗技 C270/C920） | ~¥100-300 | 只 RGB | ✅ OpenCV | ⭐ **俯视首选** |
| **Intel RealSense D435/D435i** | ~¥1500-2000 | 深度+RGB | ✅ 一等公民 | 仅传统抓取 demo 才需要 |
| **Orbbec Gemini 2** | ~¥800-1200 | 深度+RGB，国产 | ✅ 一等公民 | 官方 YOLO 抓取 demo 用这个 |
| **iPhone/iPad（DroidCam）** | 零成本 | 只 RGB | ⚠️ 需要 wrapper | 应急可用 |

⚠️ **腕部和俯视别买同款型号**（USB 路径冲突会搞崩录制，详见 §3.9）。

reBot Arm 主仓的**腕部相机支架** STEP 文件（`hardware/reBot_B601_DM/3D_Printed_Parts/`）：
- `UVC32_mount.step` —— ⭐ 给 **32×32 UVC 小模组** 用（配主线腕部那个小模组，正合适）
- `D435_Gemini2_Mount.step` / `D405_305_Mount.step` —— 给深度相机用（玩抓取 demo 时才用）

都可 3D 打印挂在 wrist_roll 上。

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
