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

| 维度 | reBot Arm 102 leader（贵但配套）| SO-ARM101 leader（便宜但要自调）|
|---|---|---|
| 价格 | 估 ¥1k-2k | ~¥800-900 |
| 跟 B601-DM follower 几何匹配 | 🟢 Seeed 配套出的**理论上**已验证 | ⚠️ **未知**，要实测 |
| LeRobot 集成成熟度 | Seeed `rebot_arm_102_leader`（9 commit 早期工程） | HuggingFace 主线 `so_leader` 一等公民 |
| 校准复杂度 | `lerobot-calibrate` 跑一次理论上就用 | 跑完可能还要手调 joint_limits |
| 后续保养 | 跟 Seeed 早期工程绑定，bug 自己修 | 跟 HuggingFace 主线，社区维护 |

**决策推荐**：先用 102（如果在手），别上来就买 SO-101。

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

### 3.4 motorbridge-smart-servo 是啥 ❓

- leader 适配器 `lerobot-teleoperator-rebot-arm-102` 最近从 `fashionstar-uart-sdk` 迁到 `motorbridge-smart-servo`
- 这说明 MotorBridge **可能扩展支持了 FashionStar 舵机**（不只达妙/RobStride）
- ❓ 待查：MotorBridge 项目里有没有 smart-servo 模块？什么状态？

### 3.5 Seeed 写的 leader 适配器跟 huggingface 主线 SO leader 接口完全对得上吗 ❓

- LeRobot 主线 Teleoperator 接口稳定，理论上一致
- ❓ 但 Seeed 自己魔改的 lerobot fork 落后主线 208 commit，意味着如果主线 Teleoperator 接口最近改过，Seeed 包可能跟不上

---

## 4. 分阶段路线图

### 阶段 0：装机烧录（**进行中**）

- 焊线 + 检线 + 烧 7 个 motor_id + 标零点 + 跑 `0x01damiao_test.py` 单电机
- 详见 `装机烧录指南.md`

### 阶段 1：单臂基础验证（装机后立刻）

- 跑 `0x01damiao_test.py`（MIT/POS_VEL/VEL 三种模式）
- 跑 `9_gravity_compensation.py` 重力补偿（最有成就感的 demo）
- 跑 MotorBridge Web UI 拖滑块整机控制
- **不涉及 LeRobot**

### 阶段 2：LeRobot follower 验证（无 leader 也能做）

- 装环境：`pip install -e _lerobot_experiment/lerobot && pip install -e _lerobot_experiment/lerobot-robot-seeed-b601`
- 跑 `lerobot-calibrate --robot.type=seeed_b601_dm_follower --robot.port=/dev/ttyACM0 --robot.can_adapter=damiao`
- 用键盘 teleoperator（`--teleop.type=keyboard`）当 leader 测一次——能转动每个关节
- **验证目标**：follower 适配器在我们这套硬件上能跑

### 阶段 3：决策 Leader 选型

| 路径 | 触发条件 |
|---|---|
| 用 102 leader | reBot Arm 102 在手 → 直接装它的 leader 适配器（`lerobot-teleoperator-rebot-arm-102`）做遥操作 |
| 买 SO-101 leader | 102 不在手 / 操控不舒服 / 想用更主流硬件 → 评估买 SO-101 |
| 都不买 | 只做"键盘控+数据采集"路径，跳过物理 leader |

### 阶段 4：升级到方案 A（fork + submodule）

只有"阶段 2 + 3 都跑通"才执行：

- GitHub fork `lerobot-robot-seeed-b601` 到 `fanhao375`
- （如果用 102）GitHub fork `lerobot-teleoperator-rebot-arm-102` 到 `fanhao375`
- 主仓加 submodule、配置 origin/upstream、走 sync 分支、baseline tag
- 详见 `复刻基线维护原则.md` 流程

### 阶段 5：数据采集 + 模型训练

- `lerobot-record --dataset.num_episodes=N` 采集真机数据
- `lerobot-train --policy.type=act --steps=300000` 训练 ACT 策略
- 评估、部署

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
| Seeed 的 leader/follower 适配器都是早期工程（9 commit / 8 commit、零 star、单作者） | 中 | 升级前先 fork pin 版本；定期看上游 commit |
| Seeed lerobot fork 落后主线 208 commit | 低 | 不用 Seeed fork，直接用 huggingface 主线 |
| motorbridge 是 wheel 手装、pyproject 没声明 | 中 | 复刻基线不可重现，需要写明确的安装步骤 |
| reBot Arm 102 leader 跟 B601-DM 几何对齐**没看到明文确认**（只是合理推断） | 中 | 实操跑通后回头补这条事实 |

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
