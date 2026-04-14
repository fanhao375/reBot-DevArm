# 03_MotorBridge

> Rust 底层电机控制库架构文档

## 文档列表

| 文档 | 类型 | 说明 |
|------|------|------|
| **MotorBridge_说明.md** | 文字 | Rust workspace 架构、Python API、达妙电机协议 |
| **MotorBridge_architecture.drawio** | 架构图 | 5 层架构可视化（用户代码 → Python 绑定 → C ABI → 厂商驱动 → 核心+硬件） |
| **MotorBridge_运行流程.drawio** | 流程图 | 双列布局：发送流（红）+ 反馈流（蓝），每步标注源文件路径 |

## 核心内容

### 架构图（architecture.drawio）
- 5 层水平横条：用户代码 / Python 绑定 / C ABI / 厂商驱动 / 核心+总线
- 展开 damiao 子框：motor.rs / protocol.rs / controller.rs / registers.rs
- 层间箭头标注转换方式（ctypes FFI / trait dispatch / CAN encode）

### 运行流程图（运行流程.drawio）
- **左列发送流（红）**：Python 调用 → C ABI → 厂商驱动 → CAN 帧 → 电机执行（10 步）
- **右列反馈流（蓝）**：电机反馈 → CAN 帧 → 解析 → 缓存 → Python 读取（7 步）
- **中间共享状态缓存**（💾）：连接两条路径
- 每个步骤标注源文件路径 + 函数名

### 说明文档（说明.md）
- 项目本质：Rust Cargo workspace（多 crate 结构）
- 五层调用栈：用户代码 → Python 绑定 → C ABI → 厂商驱动 → 核心+硬件
- Python API 7 大块：创建 Controller / 添加电机 / 使能 / 4 种控制模式 / 读状态 / 寄存器 / 清理
- 达妙 9 款电机型号表（pmax/vmax/tmax）
- 4 种控制模式对比（MIT / POS_VEL / VEL / FORCE_POS）
- 多线程模型：polling_thread 后台接收，缓存 + 直发互不干扰
- 与 reBotArm_control_py 的映射关系表

## 学习路径

1. **先看 说明.md** — 理解 Rust workspace 结构和 Python API
2. **再看 architecture.drawio** — 看 5 层架构
3. **最后看 运行流程.drawio** — 理解发送/反馈双路径
4. **读源码** — 按"入口文件索引"找对应文件

## 相关资源

- 代码仓库：`../MotorBridge/`
- Python 绑定：`../MotorBridge/bindings/python/`
- 达妙驱动：`../MotorBridge/motor_vendors/damiao/`
- 电机规格书：`../../hardware/reBot_B601_DM/Motor_Datasheets/`
