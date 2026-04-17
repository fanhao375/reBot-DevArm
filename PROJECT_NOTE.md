# reBot-DevArm 项目笔记

这是 SeeedStudio 开源的 reBot Arm B601 机械臂项目的本地学习仓库。
在官方仓库基础上，补充了电机资料、硬件总结、以及官方新发布的软件代码。

> 官方仓库：https://github.com/Seeed-Projects/reBot-DevArm
> 最后同步：2026.04.12

---

## 项目结构

```
reBot-DevArm/
│
├── hardware/                       硬件资料（官方）
│   ├── reBot_B601_DM/              达妙电机版本（主力版本）
│   │   ├── 3D_Printed_Parts/       3D打印件 STEP 源文件（17件）
│   │   ├── Metal_Parts/            CNC金属加工件 STEP 源文件（21件）
│   │   ├── Purchased_Parts/        外购件参考图
│   │   ├── Motor_Datasheets/       ★ 电机说明书 PDF + 参数汇总（自己补充的）
│   │   ├── Motor_Wiki/             ★ 电机厂商 wiki 离线版（达妙/RobStride/夹爪）
│   │   ├── performance_testing/    真机性能测试数据
│   │   ├── Hardware_Summary_zh.md  ★ 硬件总结文档（自己整理的）
│   │   ├── readme_zh.md            BOM 物料清单（含淘宝链接）
│   │   └── *.step                  整机装配文件
│   └── reBot_B601_RS/              RobStride 电机版本（待发布）
│
├── software/                       ★ 软件资料（自己拉取整理的）
│   ├── MotorBridge/                底层电机控制库
│   ├── reBotArm_control_py/        上层运动学控制库
│   ├── docs/                       ★ 文档中心（新手入门/URDF详解/架构说明）
│   ├── wiki_docs/                  ★ wiki 教程离线版（8 个页面，含图片缓存）
│   └── README_zh.md                软件部分详细说明
│
├── media/                          项目宣传图片
├── README_zh.md                    官方中文说明（含路线图）
├── README.md                       官方英文说明
├── PROJECT_NOTE.md                 ★ 本文件（项目总览）
├── CHANGELOG.md                    ★ 操作日志（每次改动记录）
├── LEARNING_LOG.md                 ★ 学习笔记（踩坑、理解、发现）
├── LEARNING_GUIDE_01.md            ★ 复现教程（给别人看的学习指南）
└── GIT_GUIDE.md                    ★ Git 操作指南（Fork/同步/推送教程）
```

> 标 ★ 的是自己补充的内容，不属于官方仓库。
> 本地工具目录：`.codex/` — Codex 专用项目记忆（已加入 `.gitignore`，不上传 GitHub）

---

## 各部分说明

### hardware/ — 硬件（造一台机械臂需要什么）

包含造出一台 reBot Arm 所需的全部机械设计文件和采购清单。

| 内容 | 说明 |
|------|------|
| STEP 文件 | 3D打印件 + CNC金属件，可以直接拿去加工 |
| BOM 清单 | 每个零件的规格、数量、参考价格、淘宝链接 |
| 电机说明书 | DM-J4310 和 DM-J4340P 的完整参数和 CAN 协议 |
| 硬件总结 | 一份文档看完整机所有参数 |
| 性能测试 | 不同负载下机械臂能跑多久、温度多高 |

整机自行加工成本约 **7,500 元**。

### software/ — 软件（让机械臂动起来需要什么）

官方 2026年4月 新发布的两个代码仓库，拉取到本地方便学习。

| 仓库 | 来源 | 干什么的 |
|------|------|---------|
| **MotorBridge** | github.com/tianrking/MotorBridge | 底层：通过 CAN 总线控制电机旋转 |
| **reBotArm_control_py** | github.com/vectorBH6/reBotArm_control_py | 上层：运动学解算、轨迹规划、重力补偿 |

两者的关系：
```
你的指令 → reBotArm_control_py（算出关节角度）→ MotorBridge（发CAN帧）→ 电机转动
```

详细说明见 `software/README_zh.md`。

---

## 这台机械臂的核心参数

| 参数 | 数值 |
|------|------|
| 自由度 | 6轴 + 1夹爪 |
| 电机 | 达妙 DM4340P×3（大关节）+ DM4310×4（小关节） |
| 通信 | CAN 总线 @ 1Mbps |
| 供电 | 24V / 350W |
| 推荐负载 | ≤ 1.5 kg |
| 推荐臂展 | < 70%（约 450mm）|
| 控制频率 | 500 Hz |

---

## 官方更新进度（截至 2026.04.12）

| 模块 | 状态 |
|------|------|
| 硬件 BOM + STEP | ✅ 完成 |
| 电机基础控制 | ✅ 完成 |
| 性能测试 | ✅ 完成 |
| Python SDK (MotorBridge) | ✅ 完成 |
| Pinocchio 运动学 | ✅ 完成 |
| 组装视频 | 🚧 预计 04.20 |
| ROS2 + MoveIt2 | 🚧 预计 04.20 |
| Isaac Sim 仿真 | 🚧 预计 04.20 |
| LeRobot AI训练 | 🚧 预计 04.30 |
| RS版硬件 | 🚧 预计 05月 |

---

## 更新记录

| 日期 | 内容 |
|------|------|
| 2026.04.12 | 同步官方最新代码；拉取 MotorBridge 和 reBotArm_control_py；下载电机说明书；整理硬件总结文档 |
| 2026.04.13 | WSL2 Ubuntu 环境搭建；Pinocchio 安装；正/逆运动学测试通过（修复官方 IK 示例 bug） |
| 2026.04.13 | 梳理 reBotArm_control_py 代码架构；更新架构图 drawio；编写代码详解文档 `software/reBotArm_control_py_说明.md` |
| 2026.04.13 | 新建运行流程图 `software/reBotArm_control_py_运行流程.drawio`（末端坐标→电机转动完整数据流，每步标注源文件路径） |
| 2026.04.13 | 梳理 MotorBridge 代码架构；编写 `software/MotorBridge_说明.md`（五层调用栈+Python API+与 reBotArm_control_py 映射关系）；新建 `MotorBridge_architecture.drawio`（5 层架构图）+ `MotorBridge_运行流程.drawio`（双列发送/反馈流，每步标注源文件） |
| 2026.04.13 | 跑通 MeshCat 可视化三件套（`fk_sim.py` / `ik_sim.py` / `traj_sim.py`）；修复 WSL2 访问 Windows 文件时 Git symlink 失效问题；改进 `ik_sim.py` 添加目标点可视化+连续初值策略；验证 SE(3) 测地线轨迹规划 + CLIK 跟踪（IK 成功率 100%，误差 < 0.1mm） |
| 2026.04.13 | 编写新手友好文档：`software/URDF_入门指南.md`（面向机械工程师，用机械图纸类比解释 Link/Joint）+ `software/MeshCat_可视化指南.md`（浏览器 3D 预览工具快速上手，三个 sim 脚本详解）+ `software/reBot-DevArm_URDF详解.md`（逐行解读 URDF 文件，448 行完整注释） |
| 2026.04.13 | 文档归类整理：将文档移入 `software/docs/` 分类文件夹（00_新手入门/01_项目专用/02_reBotArm_control_py/03_MotorBridge），编写各级 README 索引 |
| 2026.04.14 | 用 OpenCLI 抓取 7 个 wiki 页面（达妙电机/RobStride/DM夹爪/LeRobot/MoveIt2/ROS2/机器人总页面）；电机 wiki 双份存放（hardware/Motor_Wiki + software/wiki_docs）；修复全部 5 个文档的表格和代码格式 |
| 2026.04.14 | Fork 官方仓库到 GitHub（fanhao375/reBot-DevArm）；配置 git remote（origin=个人Fork, upstream=官方仓库）；推送所有补充内容到 GitHub；编写 `GIT_GUIDE.md`（零基础 Git 操作指南，Fork/Clone/Push/Pull/同步上游完整教程） |
| 2026.04.16 | 新建本地 `.codex/PROJECT_MEMORY_项目记忆.md`，把 `小红书进度/AI_HANDOFF_AI接手指南.md` 中的项目规则、环境约定、图表规范、小红书分离规则和工具使用说明同步为 Codex 专用项目记忆；更新 `.gitignore` 忽略 `.codex/` |
| 2026.04.16 | 补齐 `software/reBotArm_control_py/example/sim/gravity_sim.py`（重力补偿仿真版，对应真机例程 9 号）；交互输入关节角 + MeshCat 显示质心球/重力线段 + 终端打印 6 个 τ_g（带条形图）；填补作者教学路径中缺失的 sim 仿真坑位 |
