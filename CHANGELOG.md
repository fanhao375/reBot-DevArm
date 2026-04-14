# 更新日志

记录本仓库的所有本地修改和操作，方便后续 AI 或协作者理解上下文。

---

## 2026-04-12

### 1. 同步官方仓库
- `git pull origin main` 拉取最新代码（11个新提交）
- 主要变化：Python SDK 和 Pinocchio 标记为✅完成，指向外部仓库

### 2. 补充硬件资料
- 新建 `hardware/reBot_B601_DM/Motor_Datasheets/`
  - 下载 `DM-J4310-2EC_V1.1_Manual.pdf`（达妙小电机说明书）
  - 下载 `DM-J4340P-2EC_Manual.pdf`（达妙大电机说明书）
  - 编写 `README.md` 电机参数汇总 + CAN 协议整理
- 编写 `hardware/reBot_B601_DM/Hardware_Summary_zh.md` 硬件总结文档

### 3. 拉取软件仓库
- 新建 `software/` 目录
- 克隆 `MotorBridge`（github.com/tianrking/MotorBridge）→ `software/MotorBridge/`
  - 底层通用电机控制栈，Rust 核心 + Python/C++ 绑定
  - 支持达妙、RobStride、MyActuator、HighTorque、Hexfellow 五个品牌
- 克隆 `reBotArm_control_py`（github.com/vectorBH6/reBotArm_control_py）→ `software/reBotArm_control_py/`
  - 上层运动学控制库，基于 Pinocchio
  - 注意：代码在 **develop 分支**，main 分支只有一个空 README
  - 包含 URDF 模型、正逆运动学、轨迹规划、重力补偿、示例程序

### 4. 抓取 wiki 教程
- 用 OpenCLI 抓取 Pinocchio 教程页面 → `software/wiki_docs/`
- 原始 URL：https://wiki.seeedstudio.com/rebot_arm_b601_dm_pinocchio_meshcat/

### 5. 编写说明文档
- `PROJECT_NOTE.md` — 项目总览，文件结构说明
- `software/README_zh.md` — 软件部分详细说明 + 学习路径
- `software/architecture_diagram.md` — 控制架构说明（Mermaid 格式）
- `software/architecture_diagram.png` — 控制架构图（PNG 渲染）
- `software/architecture_diagram.drawio` — 控制架构图（可编辑 Draw.io 格式）

### 6. 环境调整
- `software/reBotArm_control_py/pyproject.toml` 中 `requires-python` 从 `==3.10.*` 改为 `>=3.10`
  - 原因：本机只有 Python 3.12/3.13，放宽版本限制
- 安装依赖：meshcat、numpy、pyyaml、matplotlib
- pinocchio (pin) 待安装

### 7. VS Code 插件
- 安装 `bierner.markdown-mermaid`（Mermaid 预览）
- 安装 `hediet.vscode-drawio`（Draw.io 可视化编辑）
- 以上插件装在 VS Code（F:\vscode\），不是 Cursor（D:\cursor\）

### 8. 文档体系建立
- 新建 `LEARNING_LOG.md` — 学习笔记（踩坑、理解、发现）
- 新建 `LEARNING_GUIDE_01.md` — 复现教程（环境搭建 + 运动学 + 电机控制）
- 确立 5 个文档的分工规则，写入 AI 记忆

---

## 2026-04-13

### 1. WSL2 Ubuntu 22.04 安装
- 目标：Pinocchio 在 Windows pip 编译卡死，改用 WSL2 Linux 环境
- 开启 WSL 功能：`wsl --install --no-distribution`，重启电脑
- 下载 Ubuntu 22.04 镜像：从微软官方下载 appx 包（1.1GB），需设置代理端口 7890
- 安装位置：**F:\WSL\Ubuntu**（C 盘空间不足，通过 --import 直接装到 F 盘）
- 安装步骤：appx → 解压 → 找到 install.tar.gz → `wsl --import` 到 F 盘
- 状态：✅ Ubuntu 已进入，Python 环境待配置

### 2. WSL2 Python 环境配置
- Ubuntu 自带 Python 3.10.12
- 用清华镜像安装全部依赖：`pip3 install pin numpy pyyaml matplotlib meshcat motorbridge -i https://pypi.tuna.tsinghua.edu.cn/simple`
- Pinocchio 3.9.0 安装成功（Linux 下有预编译二进制，秒装）
- 状态：✅ 环境就绪

### 3. 正运动学测试通过
- 运行 `python3 example/5_fk_test.py`
- 归零位置末端：X=0.253m, Y=0, Z=0.172m，URDF 模型验证正确
- 状态：✅ 通过

### 4. 逆运动学测试 — 修复官方 bug 后通过
- `example/6_ik_test.py` 原始代码有 bug，接口参数名与库不匹配：
  - `model=model` → 函数不接受此参数（内部自动加载）
  - `target_position` → 实际参数名为 `target_pos`
  - `target_rotation` → 实际参数名为 `target_rot`
  - 返回值字段 `converged` → 实际为 `success`
  - 返回值字段 `residual_trans/residual_rot` → 实际为 `error`
- 修复后测试：输入归零位置坐标 (0.253, 0, 0.172) → 解出 (0,0,0,0,0,0)，结果正确
- 状态：✅ 修复并通过

### 5. reBotArm_control_py 代码架构梳理
- 通读 develop 分支代码（main 分支是空的）
- 更新 `software/reBotArm_control_py_architecture.drawio` 架构图
  - 原图 dynamics 只画了 4 个功能框，实际有 7 个文件（补全 forward_dynamics / inertia / centroidal / derivatives / energy）
  - trajectory 子模块文件名修正为实际文件：sampler.py / clik_tracker.py / trajectory_planner.py
  - 补充 kinematics 和 dynamics **各有一个** robot_model.py 的说明
  - 硬件接口层细化：motorbridge.Controller + Mode 枚举 + 串口桥 + CAN
  - 增加外部依赖：motorbridge SDK、matplotlib
- 新建 `software/reBotArm_control_py_说明.md`
  - 一句话总结 + 目录结构 + 四个核心子模块详解（每个文件的核心函数）
  - 控制器 ArmEndPos 用法 + 三种控制模式对比（MIT / POS_VEL / VEL）
  - 示例程序索引（0~10）+ robot.yaml 配置说明
  - 完整调用链路（move_to_traj 为例）+ 外部依赖一览

### 6. 运行流程图（末端坐标 → 电机转动）
- 新建 `software/reBotArm_control_py_运行流程.drawio`
  - 回答「这个库怎么把 (x,y,z) 翻译成电机指令」的问题
  - 三条执行路径并列展示：
    - **路径 A（红）**：`move_to_traj()` 轨迹规划 — IK → FK → SE(3)测地线 → CLIK → _send_loop
    - **路径 B（蓝）**：`move_to_ik()` 直达模式 — 只做 IK，一步到位
    - **路径 C（绿）**：重力补偿 — MIT 模式 + g(q) 前馈力矩
  - 三条路径最终汇入 500Hz 公共控制循环 → MotorBridge → CAN → 电机
- 每个流程节点都标注了**源文件路径 + 函数名**，方便对照代码阅读
  - 例如 IK 步骤标注 `controllers/arm_endpos_controller.py → _solve_ik()` + `kinematics/inverse_kinematics.py → solve_ik()`
  - 重力计算标注 `dynamics/inverse_dynamics.py → compute_generalized_gravity()`
  - 底层指令标注 `actuator/arm.py → RobotArm.pos_vel() / mit() / get_state()`

### 7. MotorBridge 代码架构梳理
- 通读 MotorBridge 仓库（Rust workspace 多 crate 结构）
- 新建 `software/MotorBridge_说明.md`
  - 一句话总结 + 项目本质（Rust Cargo workspace）
  - 完整目录结构（motor_core / motor_abi / motor_vendors/{damiao,robstride,...} / bindings/{python,cpp}）
  - **五层调用栈** ASCII 图：用户代码 → Python 绑定 → C ABI → 厂商驱动 → 核心+硬件层 → CAN 总线
  - Python API 7 大块（创建 Controller / 添加电机 / 使能 / 4 种控制模式 / 读状态 / 寄存器 / 清理）
  - 达妙 9 款电机型号表（pmax/vmax/tmax，标注 reBot 用 4310 + 4340P）
  - 4 种控制模式对比表（MIT / POS_VEL / VEL / FORCE_POS）
  - 多线程模型说明（polling_thread 后台接收，缓存 + 直发互不干扰）
  - **与 reBotArm_control_py 的映射关系表**（RobotArm 方法 ↔ MotorBridge API）
  - 完整调用链示例（send_mit 6 层穿透到 CAN 帧）
  - 入口文件索引（按需读什么文件）
- 新建 `software/MotorBridge_architecture.drawio`
  - 5 层水平横条架构图（用户代码 / Python 绑定 / C ABI / 厂商 / 核心+总线 / 硬件）
  - 每层列出所有构成文件，并展开 damiao 子框（motor.rs/protocol.rs/controller.rs/registers.rs）
  - 层间用箭头标注转换方式（ctypes FFI / trait dispatch / CAN encode 等）
- 新建 `software/MotorBridge_运行流程.drawio`
  - 双列布局：**左列发送流（红，自上而下 10 步）** + **右列反馈流（蓝，自下而上 7 步）**
  - 每个步骤标注源文件路径 + 函数名（📂 风格与 reBotArm_control_py 流程图一致）
  - 中间共享状态缓存框（💾）连接两条路径（写：on_feedback；读：get_state）
  - 跨列耦合箭头：电机执行 → 反馈广播
  - 底部 4 条关键理解注释（异步、缓存、多线程安全、跨厂商通用性）

### 8. MeshCat 可视化三件套（无硬件学习）
- **环境修复**：WSL2 访问 Windows 文件时 Git symlink 失效
  - `urdf/reBot-DevArm_description_fixend` 在 Windows 下被存成文本文件（31 字节）
  - 手动在 WSL2 里重建软链接：`ln -s reBot-DevArm_fixend_description reBot-DevArm_description_fixend`
- 跑通 `example/sim/fk_sim.py`（正运动学可视化）
  - 输入关节角 → 浏览器 `http://127.0.0.1:7000/static/` 实时显示 3D 机械臂姿态
  - 测试归零位 `0 0 0 0 0 0` 和复杂姿态 `45 -30 15 -60 90 180`
- **改进 `example/sim/ik_sim.py`（逆运动学可视化）**
  - 原版问题：缺少目标点可视化，每次从零位出发导致不收敛
  - 改进 1：添加 `viz.show_ik_pose()` 调用，显示红球 + 三色坐标轴
  - 改进 2：保存 `q_current`，使用上一次的解作为下一次初值（连续求解策略）
  - 改进 3：增强调试输出，解析失败时显示原始输入
  - 测试结果：三个点全部收敛（`0.25 0.0 0.2` / `0.3 0.0 0.25` / `0.2 0.15 0.3`），迭代 9-12 次，误差 < 0.07mm
- **跑通 `example/sim/traj_sim.py`（SE(3) 测地线轨迹规划 + CLIK 跟踪）⭐**
  - 测试 1：`0.3 0.0 0.25` → IK 成功率 96.1%，误差 0.05mm，51 点 1.0s
  - 测试 2：`0.2 0.15 0.35 0 0.5 0.3`（含姿态）→ **IK 成功率 100%**，误差 0.057mm，121 点 2.4s，6 关节全动
  - 测试 3：`0.15 0.2 0.3` → IK 无解（超出工作空间）
  - 浏览器显示：灰色参考路径 + 绿色实际路径 + 机械臂动画回放
  - **这是 `reBotArm_control_py_运行流程.drawio` 里路径 A（move_to_traj）的无硬件版**
- 关键收获：
  - MeshCat = 浏览器里的"数字孪生"，无需硬件即可验证运动学算法
  - 零位末端位置 `(0.253, 0.000, 0.172)` m
  - 推荐工作半径 < 450mm（70% reach）
  - CLIK 跟踪精度 < 0.1mm，算法实现质量高

### 9. 新手友好文档编写
- 新建 `software/URDF_入门指南.md`
  - 面向机械工程师/硬件工程师的 URDF 快速入门
  - 用机械图纸类比解释 Link（零件）和 Joint（连接方式）
  - reBot-DevArm URDF 结构详解（6 个关节对应的实体零件和电机型号）
  - 关键参数解读（关节轴心位置、转动范围、扭矩限制、质量惯性）
  - 常见操作（修改关节限位、更新零件质量、添加末端工具）
  - 工具推荐（urdf_viz / RViz / check_urdf）
  - 常见问题排查（mesh 找不到、关节限位冲突、质量参数不准）
- 新建 `software/MeshCat_可视化指南.md`
  - 面向机械工程师/硬件工程师的 MeshCat 快速上手教程
  - 什么是 MeshCat（浏览器里的 3D 预览工具）
  - 工作原理（Python 后端 + WebSocket + Three.js 前端）
  - 三个可视化工具详解（fk_sim / ik_sim / traj_sim）
  - 浏览器操作指南（旋转/平移/缩放视角）
  - 常见问题排查（代理拦截、URDF 路径错误、WebGL 未启用、动画卡顿）
  - 高级技巧（录屏、自定义标记、多机器人同时显示）
- 新建 `software/reBot-DevArm_URDF详解.md`
  - 逐行解读 `reBot-DevArm_fixend.urdf` 文件（448 行完整注释）
  - 每个 link 的惯性参数含义（质量、质心、转动惯量）
  - 每个 joint 的关键参数（origin 位置、rpy 旋转、axis 转轴、limit 限位）
  - 为什么 joint2 的 `rpy="-1.5708 0 0"`（坐标系旋转 90°）
  - 为什么 joint2 的 `upper="0"`（机械限位，不能往上抬超过水平）
  - 为什么 link2 质量最重（1.327kg，包含大臂和肘关节电机）
  - 末端 end_joint 为什么是 `type="fixed"`（法兰固定连接）
  - 完整的机械结构对应关系（URDF 名称 ↔ 实体零件 ↔ 电机型号）
- **目标**：让不懂 ROS/Pinocchio 的硬件工程师也能快速上手可视化工具，看懂 URDF 每一行的物理含义

### 10. 文档归类整理
- 将新手文档从 `software/` 根目录移入 `software/docs/` 分类文件夹：
  - `docs/00_新手入门/` — URDF 入门指南、MeshCat 可视化指南
  - `docs/01_项目专用/` — reBot-DevArm URDF 详解
  - `docs/02_reBotArm_control_py/` — 运动学控制库架构说明、架构图、运行流程图
  - `docs/03_MotorBridge/` — 底层电机库架构说明、架构图、运行流程图
- 每个文件夹编写 `README.md` 索引
- 编写 `software/docs/README.md` 文档中心导航（3 条学习路径 + 速查表）
- 更新 `software/README_zh.md` 目录结构和学习路径（新增"第零阶段：看文档"）

---

## 2026-04-14

### 1. 抓取 Wiki 文档（OpenCLI）
- 修复 OpenCLI 使用问题：`generate/explore` 命令在当前环境报错，改用 `web read` 命令成功
- 正确命令：`opencli web read --url <URL> --output <DIR> --download-images true`
- 抓取以下页面到 `software/wiki_docs/`：

| 页面 | 大小 | 关系 |
|------|------|------|
| 达妙系列电机 | 41.5 KB | 直接相关 — 项目使用的电机 |
| RobStride 电机控制完整指南 | 20.2 KB | 直接相关 — RS 版本会用 |
| DM Gripper 夹爪组装指南 | 6.2 KB | 直接相关 — 末端执行器 |
| SoArm in LeRobot | 85.1 KB | 参考 — 路线图 LeRobot 适配 |
| StarAI Arm in ROS2 MoveIt | 7.7 KB | 参考 — 路线图 MoveIt2 适配 |
| ROS2 Humble 安装教程 | 3.8 KB | 参考 — ROS2 基础环境 |
| Robotics 总页面 | 5.4 KB | 索引 — 全部机器人资源导航 |

### 2. 电机 Wiki 双份存放
- 硬件相关的 wiki（达妙电机、RobStride、DM Gripper）复制到 `hardware/reBot_B601_DM/Motor_Wiki/`
- `software/wiki_docs/` 保留完整副本
- 两处各编写 `README.md` 索引文档

### 3. Wiki 文档格式修复
- OpenCLI 抓取的 HTML 表格全部变成了一行一个值的纯文本，代码块被压成单行
- 逐个修复全部 5 个有问题的文档：

| 文档 | 修复内容 |
|------|---------|
| 达妙系列电机 | 规格参数表拆成 3 个表格（基础规格/电气参数/控制参数），Python 代码（damiao_motor.py + damiao_test.py）恢复缩进 |
| RobStride 电机控制完整指南 | 5 个表格重建（电机型号/语言对比/CAN帧格式/性能基准/错误代码），30+ 处代码块恢复换行 |
| DM Gripper 夹爪 | 5 个 BOM 分类表格重建，警告块格式化 |
| StarAI Arm MoveIt | 规格表重建（3 款机械臂对比），C++ 代码恢复，shell 命令拆行 |
| SoArm LeRobot | 7 个表格重建，50+ 处代码块恢复，JSON 配置恢复缩进，警告块修复 |

- 同步修复后的电机文档到 `hardware/reBot_B601_DM/Motor_Wiki/` 副本

### 4. MeshCat 仿真代码详解文档
- 新建 `software/docs/01_项目专用/reBot-DevArm_MeshCat仿真代码详解.md`
- 对 4 个仿真文件逐函数解读：
  - `visualizer.py` — Visualizer 类初始化流程、6 个核心方法（update/show_ik_pose/draw_path/play_trajectory 等）
  - `fk_sim.py` — 正运动学可视化流程（输入关节角 → 计算末端位姿 → 浏览器显示）
  - `ik_sim.py` — 逆运动学可视化流程（输入目标位姿 → 解算关节角 → 连续初值策略）
  - `traj_sim.py` — 轨迹规划仿真流程（SE(3)测地线 → CLIK跟踪 → MeshCat动画回放）
- 包含调用关系图、关键参数说明、仿真 ↔ 真机代码映射表、核心概念速查
- 更新 `software/docs/01_项目专用/README.md` 索引和 `software/docs/README.md` 速查表及学习路径
