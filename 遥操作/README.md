# 遥操作系统

## 什么是遥操作？

遥操作（Teleoperation）是指用一台**主动臂（Leader Arm）**手动示教，另一台**从动臂（Follower Arm）**实时跟随复现动作的方式。

在机器人学习领域，遥操作是采集高质量动作数据的标准方案：
```
人手持主动臂 → 做出动作 → 从动臂同步复现 → 记录数据 → 训练 AI 模型
```

这套数据采集流程目前的主流框架是 [LeRobot](https://github.com/huggingface/lerobot)（HuggingFace 出品）。

---

## 本目录的内容

| 子目录 | 内容 |
|--------|------|
| `StarArm_102/` | Star Arm 102-LD 遥操作主动臂（git submodule） |

---

## Star Arm 102-LD — 主动臂

**仓库**：[servodevelop/Star-Arm-102](https://github.com/servodevelop/Star-Arm-102)

Star Arm 102-LD 是一款低成本、轻量级的遥操作**主动臂**，用廉价舵机制作，专门用于配合 LeRobot 进行人类示教数据采集。

### 与 reBot Arm B601 的配对关系

| 角色 | 设备 | 驱动方式 |
|------|------|---------|
| **主动臂（Leader）** | Star Arm 102-LD | 舵机，手动运动 |
| **从动臂（Follower）** | reBot Arm B601 DM | 达妙减速电机，CAN 总线 |

工作流程：
1. 手持 Star Arm 102-LD 做出动作
2. LeRobot 读取主动臂各关节角度
3. LeRobot 控制 reBot Arm B601 实时跟随
4. 同步录制图像和关节角数据
5. 用采集的数据训练 ACT / Diffusion Policy 等 AI 模型

### Star Arm 102 子目录结构

```
StarArm_102/
├── Hardware/           硬件：CAD 文件（DWG + PDF）+ BOM 清单
├── Lerobot/            软件：LeRobot 兼容 Python 包
│   ├── lerobot-robot-stararm102/       从动臂接口（给 reBot 用的是这个逻辑）
│   ├── lerobot-teleoperator-stararm102/  主动臂接口（Star Arm 102-LD）
│   ├── stararm102.md                   中文使用说明
│   └── stararm102_en.md                英文使用说明
├── ROS2_HUMBLE/        ROS2 + MoveIt2 配置（可选，进阶用）
└── Media/              产品图片
```

---

## 快速上手

### 前提条件

- Python 3.10+
- 已安装 LeRobot：`pip install lerobot`
- reBot Arm B601 通电、CAN 总线连接正常
- Star Arm 102-LD 通过 USB 连接到电脑

### 详细步骤

参考 `StarArm_102/Lerobot/stararm102.md`（中文）或 `stararm102_en.md`（英文）。

LeRobot 官方的 reBot 遥操作教程将在官方 wiki 更新，目前可关注：
- [SeeedStudio Wiki](https://wiki.seeedstudio.com/)
- [LeRobot 官方仓库](https://github.com/huggingface/lerobot)

---

## 更新 submodule

首次克隆本仓库后，需要初始化 submodule：

```bash
git submodule update --init --recursive
```

更新 Star Arm 102 到最新版：

```bash
cd 遥操作/StarArm_102
git pull origin main
cd ../..
git add 遥操作/StarArm_102
git commit -m "更新 StarArm_102 submodule"
```
