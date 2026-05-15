# AI 机器人路径选择扫盲

> 给"刚接触 AI 机器人就被一堆名词砸晕"的人看的概念地图。
> 把 LeRobot / ROS2 / Isaac Sim / sim-to-real / MoveIt 这些名词的**关系和取舍**讲清楚。
> 建立时间：2026-05-15

---

## 0. 这文档为啥存在

新手看 AI 机器人入门特别容易蒙圈：

- 抖音 B 站说"做 AI 机器人要学 ROS2"
- HuggingFace 教程说"用 LeRobot 1 周跑通 AI 抓东西"
- 论文里满是 Isaac Sim / sim-to-real / domain randomization
- Unitree、特斯拉视频又是另一套
- 看到 reBot Arm 仓里同时有 LeRobot 集成 + ROS2 工作区，**到底用哪个？**

**结论先行**：AI 机器人有**两个完全不同的世界**，工具栈不通用。看你做啥决定走哪条。

---

## 1. 真相：两个完全不同的世界

```
┌────────────────────────────────────┐    ┌────────────────────────────────────┐
│   世界 1：LeRobot 简化路径           │    │   世界 2：工业级 AI 机器人          │
│  （学生 / 爱好者 / Demo 玩家）       │    │  （Unitree / 特斯拉 / 谷歌）        │
├────────────────────────────────────┤    ├────────────────────────────────────┤
│                                    │    │                                    │
│  1 台机械臂 + 1 个摄像头             │    │  全身机器人 + 多传感器              │
│  Python 直接闭环                    │    │  ROS2 串多模块                     │
│  imitation learning（模仿示范）      │    │  reinforcement learning（强化学习）│
│  1 个 GPU 跑通                      │    │  GPU 集群训练几亿步                 │
│  1 周入门                          │    │  6 个月-1 年入门                   │
│                                    │    │                                    │
└────────────────────────────────────┘    └────────────────────────────────────┘
        ↑                                          ↑
        │                                          │
        │  这两个用的工具栈完全不同，                │
        │  不通用，不能"混着学"                     │
        └──────────────────────────────────────────┘
```

### 1.1 世界 1：LeRobot 简化路径

| 维度 | 内容 |
|---|---|
| 目标 | 让"非机器人专业"的人 1-2 周入门 AI 机器人 |
| 核心库 | **LeRobot**（HuggingFace 出品） |
| 训练方法 | 模仿学习（imitation learning）—— 人手示范，AI 学映射 |
| 数据格式 | `LeRobotDataset`（自家定义）|
| 仿真器 | `gym-aloha` / `gym-xarm`（LeRobot 自带，简单） |
| 通信 | 纯 Python 直接闭环 |
| 是否用 ROS2 | ❌ **不用** |
| 部署 | `lerobot-eval` 命令直接跑 |
| 典型 demo | 抓杯子、堆积木、推方块、叠衣服 |
| 学习曲线 | 中（python + GPU 训练基础够用）|
| 入门时间 | 1-2 周 |
| 典型用户 | 学生、爱好者、Hugging Face 社区、demo 玩家 |

### 1.2 世界 2：工业级 AI 机器人

| 维度 | 内容 |
|---|---|
| 目标 | 量产产品、商业部署、严肃科研 |
| 核心库 | **Isaac Lab**（NVIDIA）+ **ROS2** + 自家代码 |
| 训练方法 | 强化学习（RL）+ 大规模仿真 + sim-to-real |
| 数据格式 | rosbag2 / 自家二进制 / Isaac Sim 格式 |
| 仿真器 | **Isaac Sim**（NVIDIA，高保真）/ Gazebo（开源）|
| 通信 | **ROS2 DDS**（消息总线，每秒几千条消息）|
| 是否用 ROS2 | ✅ **必须**（多模块串联的骨架）|
| 部署 | AI 模型打包成 ROS2 node + 整套系统 |
| 典型 demo | Unitree G1 走路、特斯拉 Optimus 整理、波士顿动力 Atlas 跑酷 |
| 学习曲线 | 陡（ROS2 + 强化学习 + 仿真 + 工程化）|
| 入门时间 | 6 个月-1 年 |
| 典型用户 | 机器人公司、博士、研究所 |

---

## 2. 为啥工具栈分裂成两个世界

不是技术问题，是**应用场景的复杂度**逼出来的：

### LeRobot 场景：单臂 demo

```
摄像头  →  LeRobot Python   →  机械臂
           （imitation 模型）
```

数据流简单，1 个 GPU 一台机械臂 1 个摄像头，纯 Python 够用。

### 工业场景：Unitree G1 整套系统

```
头部相机     ┐
RGBD 相机    ┤
IMU         ┼─→  ROS2 DDS 总线（实时消息） ─→  AI policy node ──→  23 个关节电机
力矩传感器   ┤                                   ↓
脚底压力     ┤                              安全监控 node
WiFi / 5G    ┘                                   ↓
                                            紧急停止 node
```

几十个模块要协调，**ROS2 是唯一成熟的方案**做消息总线。纯 Python 扛不住实时性和可靠性。

**简单说**：LeRobot 是"写个 Python 脚本"，工业级是"架构一个微服务系统"。两个尺度不一样。

---

## 3. sim-to-real 是个独立概念（**特别容易被误解**）

### 3.1 sim-to-real 到底是啥

> **sim-to-real = simulation to real，仿真到实机迁移**
>
> 在仿真器里训练 AI 模型 → 让它在真机上也能跑

**目的**：省钱省时间。实机采 1000 个 episode 要几天，仿真采 100,000 个 episode 几小时。

### 3.2 sim-to-real **不是** "AI + ROS2 混合部署"

很多人（**包括我之前也讲混了**）以为 sim-to-real 是：

```
LeRobot 训练 → 给仿真平台 → 再训练 → 迁移到 ROS2 实机
                                       ↑
                                  这是误解
```

**实际不是这样**。sim-to-real 是**训练方法**，不是"用 ROS2 部署"。

### 3.3 sim-to-real 的真实工作流

**纯 LeRobot 路径**（简单版）：

```
LeRobot 自带 gym → 仿真训练 → LeRobot 部署到真机
            （全程不用 ROS2）
```

**Isaac Lab 路径**（主流工业版）：

```
Isaac Sim 仿真 + 并行训练 → 导出策略 → 真机部署
         （ROS2 可能在仿真和真机之间做通信，但不是必需）
```

### 3.4 sim-to-real 的难度

被认为是机器人 AI 最难的几个问题之一：

| 难点 | 现象 |
|---|---|
| 物理不匹配（Reality Gap）| 仿真摩擦/重力跟真机差，AI 学的策略在真机上失效 |
| 视觉不匹配 | 仿真画面 ≠ 真实画面（光照/纹理/色差），AI 看不懂 |
| 域随机化（Domain Randomization）| 必备技术，但调参极困难 |
| 柔性物体（衣服/布料）| 仿真器几乎仿不出真实物理 |

**典型工作量**：

| 玩家 | 入门时间 |
|---|---|
| 学校研究生 + 导师 | 半年-1 年做一个能跑的 demo |
| 个人 DIY 玩家 | **通常失败**，sim 跑通但实机跑不动 |
| 工业团队（特斯拉/谷歌）| 多人月 |

---

## 4. 三个常见误解集中纠正

### 误解 1：ROS2 是 LeRobot 的"部署阶段"

❌ **错**。LeRobot 训练完直接用 `lerobot-eval` 部署，全程 Python，不需要 ROS2。

ROS2 是**另一条路**，不是 LeRobot 的下游。

### 误解 2：sim-to-real = AI 输出 + ROS2 执行

❌ **错**。这是两个独立概念：
- **sim-to-real** = 用仿真数据替代实机数据训练（训练方法）
- **AI + ROS2** = 工业级系统架构（部署方式）

这两个**可以同时做**也可以**只做一个**，但**不是同义词**。

### 误解 3：学了 LeRobot 就能做 Unitree 那种

❌ **错**。Unitree / 特斯拉用的是**世界 2 的工具栈**（Isaac Lab + ROS2），LeRobot **完全不是同一条路**。

LeRobot **入门简单 + 上限有限**；Unitree 那条路**入门难 + 上限工业级**。

---

## 5. 应用场景对照表

按你**真实想做的事**找对应路径：

| 你想干啥 | 走哪条路 | 用 ROS2 吗 |
|---|---|---|
| **学了一晚上跑个 demo 拍小视频** | LeRobot 主线 | ❌ |
| **理解 AI 机器人是啥，写个简单抓取模型** | LeRobot 主线 | ❌ |
| **采集自己机械臂数据训练 ACT 模型** | LeRobot 主线 | ❌ |
| **想让机械臂"看到物体自己抓"**（不需要严格规划） | LeRobot 主线 | ❌ |
| **想做精确轨迹规划（画方/沿直线）** | ROS2 + MoveIt 2 | ✅ |
| **多机械臂协作 / 多设备协同** | ROS2 多机协调 | ✅ |
| **想模仿 Unitree G1 / 特斯拉 Optimus** | Isaac Lab + ROS2 + RL | ✅ |
| **想做 sim-to-real 学术研究** | Isaac Sim + Isaac Lab（ROS2 可选）| ⚠️ 视方法 |
| **想发 IROS/ICRA 论文** | 大概率 Isaac Lab + ROS2 | ✅ |
| **想找机器人公司工作** | 两个都学 | ⚠️ 至少懂 ROS2 |
| **工厂部署 / 上量产** | 必须 ROS2 | ✅ |

---

## 6. 跟 reBot Arm 硬件的对应

你的硬件能跑哪条路：

### 走 LeRobot 路径

| 阶段 | 工具 |
|---|---|
| 装环境 | `pip install lerobot motorbridge` |
| 数据采集 | `lerobot-record --robot.type=seeed_b601_dm_follower --teleop.type=so101_leader` |
| 训练 | `lerobot-train --policy.type=act` |
| 部署 | `lerobot-eval` |

需要硬件：
- ✅ reBot Arm B601-DM（你已有）
- ❌ leader 主动臂（102 or SO-101，没买）
- ❌ 摄像头（RealSense / Orbbec，没买）

### 走 Isaac Lab + ROS2 路径

| 阶段 | 工具 |
|---|---|
| 装环境 | Isaac Sim + Isaac Lab + ROS2 Humble |
| URDF 导入 | reBot Arm URDF → Isaac Sim |
| 仿真训练 | 强化学习几亿步 |
| 部署 | ROS2 hardware_interface 连真机 |

需要：
- ✅ reBot Arm 硬件
- ✅ 强大 GPU（RTX 4090 起步）
- ❌ Isaac Sim 环境（要学）
- ❌ ROS2 工作流（要学）

仓内已 submodule：
- `software/reBotArmController_ROS2/`（含 MoveIt 2 集成 + URDF + 控制 node）

---

## 7. 我的实际选择建议（对你的场景）

### 起步阶段（**最先做**）

跑 LeRobot 主线，**不碰 ROS2**：

```
1. 跑通重力补偿 demo（装机烧录指南 §6.4）
2. pip install LeRobot + follower 适配器
3. 用键盘 teleop 测一次（不花钱）
4. 看心情决定下一步
```

详见 `遥操作与LeRobot待办.md §4 阶段 1-2`。

### 看个人方向分叉

| 你的兴趣 | 下一步 |
|---|---|
| **AI / demo / 拍视频** | LeRobot 一条路走到底（阶段 3-7）—— 买 leader + 摄像头 + 数据采集 + 训练 + 部署 |
| **学术研究 / 论文** | LeRobot 跑通后 → 学 Isaac Lab + ROS2，做 sim-to-real |
| **找机器人工作 / 工业方向** | 跟上面一样，但 ROS2 是基础盘，必须懂 |
| **就想自己玩没明确目标** | LeRobot 跑通，**别折腾 ROS2**——很多概念学了用不上 |

### ⚠️ 避免的陷阱

| 陷阱 | 后果 |
|---|---|
| **一上来想做 sim-to-real** | 大概率 6 个月还没跑通，劝退 |
| **同时学 LeRobot + ROS2 + Isaac** | 概念太多，学习曲线叠加，信心崩盘 |
| **看 Unitree 视频想模仿** | 工业级团队几年的工作，个人做不出 |
| **跳过 LeRobot 直接学工业级** | 没有"AI 机器人是啥"的直观，从头学 ROS2 + 仿真 + RL 极痛苦 |

**推荐顺序**：

```
阶段 0：装机 ✅
        ↓
阶段 1-2：跑通 LeRobot 主线（重力补偿 + follower 验证）
        ↓
阶段 3-7：LeRobot 完整工作流（采集 + 训练 + 部署）—— 这是"AI 机器人入门"
        ↓
（可选分叉）
        │
        ├─→ 想止步于此：拿成就感、拍视频、转其他兴趣
        ├─→ 想深入：学 Isaac Lab + ROS2 + RL，目标 sim-to-real
        └─→ 想就业：补 ROS2 基础 + MoveIt 2 + 1-2 个工业项目
```

---

## 8. 名词速查表

按字母排序，常见名词一句话解释：

| 名词 | 一句话解释 |
|---|---|
| **ACT** | Action Chunking Transformer，LeRobot 主推的 imitation learning 模型 |
| **Behavior Cloning** | 模仿学习的基础，AI 学"看到 X → 输出 Y"的映射 |
| **Domain Randomization** | 仿真训练时随机改参数（光/摩擦/颜色），让 AI 学到鲁棒策略，sim-to-real 必备技术 |
| **DDS** | Data Distribution Service，ROS2 的底层消息中间件 |
| **Gazebo** | 开源机器人仿真器，跟 ROS2 集成深 |
| **Imitation Learning（模仿学习）** | 人手示范，AI 学映射，LeRobot 主路径 |
| **Isaac Sim** | NVIDIA 出的高保真机器人仿真器，业界主流 |
| **Isaac Lab** | NVIDIA 出的强化学习训练框架，配合 Isaac Sim |
| **LeRobot** | HuggingFace 出的 AI 机器人简化框架，imitation learning 为主 |
| **MoveIt 2** | ROS2 的运动规划库，业界标准，做碰撞检测/路径规划/IK |
| **Pi0** | LeRobot 集成的另一个 SOTA 模型 |
| **Reinforcement Learning（强化学习/RL）** | 让 AI 自己试错学习，工业级机器人主路径 |
| **ROS2** | Robot Operating System 2，机器人软件标准框架，消息总线 |
| **Rviz** | ROS2 的可视化工具，显示机械臂模型和轨迹 |
| **sim-to-real** | 仿真训练后迁移到真机的方法 |
| **SmolVLA** | 小型 VLA 模型，LeRobot 支持 |
| **URDF** | Unified Robot Description Format，机器人结构描述文件，两个世界通用 |
| **VLA** | Vision-Language-Action 模型，看到画面 + 听懂指令 → 做动作 |

---

## 9. 关联文档

- `装机烧录指南.md` —— reBot Arm 装机到能动的全流程
- `遥操作与LeRobot待办.md` —— LeRobot 路径的详细路线图 + leader 选型决策
- `复刻基线维护原则.md` —— submodule 同步规则
- `项目总览.md` —— 整体项目结构

---

## 10. 一句话总结

> **AI 机器人不是单一技术栈，是两个独立的世界**：
> - LeRobot 是"AI 机器人的 OpenAI Gym + Hugging Face"——爱好者入门快、上限有限
> - Isaac Lab + ROS2 是"工业级 AI 机器人的真正栈"——Unitree、特斯拉走这条路
>
> **它们不互相依赖也不互相需要**。看你做啥决定走哪条。
>
> **新手别一次铺太多**：先 LeRobot 跑通 demo 拿成就感，再判断要不要深入工业级。
