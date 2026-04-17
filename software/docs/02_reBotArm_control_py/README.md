# 02_reBotArm_control_py

> Python 上层运动学控制库架构文档

## 文档列表

| 文档 | 类型 | 说明 |
|------|------|------|
| **reBotArm_control_py_说明.md** | 文字 | 代码架构、模块职责、API 说明 |
| **重力补偿详解/** | 文字+图表 | 重力补偿原理、数学推导、代码详解（含架构图/序列图/流程图） |
| **reBotArm_control_py_architecture.drawio** | 架构图 | 5 层架构可视化（用户代码 → RobotArm → Kinematics → Pinocchio → MotorBridge） |
| **reBotArm_control_py_运行流程.drawio** | 流程图 | 从"末端坐标"到"电机转动"的完整数据流，每步标注源文件路径 |

## 核心内容

### 架构图（architecture.drawio）
- 5 层水平横条：用户代码 / RobotArm / Kinematics / Pinocchio / MotorBridge
- 每层列出关键模块和文件
- 层间箭头标注数据流向

### 运行流程图（运行流程.drawio）
- **路径 A（move_to_traj）**：末端坐标 → SE(3) 测地线 → CLIK → 电机指令
- **路径 B（move_joints）**：关节角 → 重力补偿 → 电机指令
- 每个步骤标注源文件路径（📂 风格）

### 说明文档（说明.md）
- 项目定位：上层运动学控制库
- 目录结构：kinematics / control / utils / example
- 核心模块：FK/IK、轨迹规划、重力补偿、CLIK
- 与 MotorBridge 的接口映射

## 学习路径

### 路径 1：运动学入门（FK/IK/轨迹规划）
1. **先看 说明.md** — 理解整体架构
2. **再看 architecture.drawio** — 看模块关系
3. **最后看 运行流程.drawio** — 理解数据流
4. **跑 example/sim/** — 无硬件验证理解

### 路径 2：动力学进阶（重力补偿）
1. **先完成路径 1** — 理解运动学基础
2. **看 重力补偿详解/README.md** — 理解物理原理和数学推导
3. **跑 example/9_gravity_compensation.py** — 验证基础重力补偿（需要真机）
4. **跑 example/10_gravity_compensation_lock.py** — 验证进阶版（末端速度锁止）

## 相关资源

- 代码仓库：`../reBotArm_control_py/`
- 示例代码：`../reBotArm_control_py/example/`
- MeshCat 可视化：`../00_新手入门/MeshCat_可视化指南.md`
