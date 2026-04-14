# MotorBridge 代码说明

> 对应仓库：`software/MotorBridge/`（来源 github.com/tianrking/MotorBridge）
> 作者：tianrking  版本：0.1.3  License：MIT

---

## 一句话总结

**MotorBridge 是一个跨厂商、跨语言、跨总线的 CAN 电机控制中间层**。
Rust 写核心 → 导出 C ABI → Python/C++ 通过 FFI 调用 → 支持达妙/RobStride/MyActuator/HighTorque/Hexfellow 五家电机 → 支持 Linux SocketCAN / CAN-FD / Windows PCAN / 达妙 USB-CAN 串口桥四种硬件链路。

`reBotArm_control_py` 就是它上面的一个用户。

---

## 项目本质：Rust Cargo workspace

从根 `Cargo.toml` 看，这是一个多 crate 的工作区：

```
motor_core           核心抽象（总线、设备、控制器）
motor_vendors/
    damiao/          达妙驱动（reBot 用这个）
    robstride/       RobStride
    myactuator/      MyActuator
    hexfellow/       Hexfellow
    hightorque/      HighTorque
    template/        给新厂商参考
motor_abi            C ABI 导出层（给 Python/C++ 用）
motor_cli            Rust 命令行工具
integrations/
    ws_gateway/      WebSocket 网关
bindings/
    python/          Python 包（motorbridge）
    cpp/             C++ 头文件
```

---

## 目录结构

```
MotorBridge/
├── Cargo.toml              workspace 定义
├── motor_core/             ★ 核心层
│   └── src/
│       ├── lib.rs          模块入口
│       ├── bus.rs          CanBus trait + CanFrame 结构
│       ├── controller.rs   CoreController（后台接收线程 + 设备表）
│       ├── device.rs       MotorDevice trait（电机必须实现这个）
│       ├── error.rs        MotorError / Result
│       ├── model.rs        MotorModelSpec / PvTLimits / 型号目录
│       ├── dm_serial.rs    达妙 USB-CAN 串口桥实现
│       ├── socketcan.rs    Linux SocketCAN 实现
│       ├── socketcanfd.rs  Linux SocketCAN-FD 实现
│       └── pcan.rs         Windows PEAK CAN 实现
│
├── motor_abi/              ★ C ABI 导出层
│   ├── include/            生成的 C 头文件
│   └── src/
│       ├── lib.rs
│       ├── controller_lifecycle_ffi.rs   new_*/free/shutdown
│       ├── controller_add_motor_ffi.rs   add_damiao_motor 等
│       ├── motor_lifecycle_ffi.rs        enable/disable/clear_error/set_zero
│       ├── motor_control_ffi.rs          send_mit/pos_vel/vel/force_pos
│       ├── motor_register_ffi.rs         寄存器读写
│       ├── state_ffi.rs                  get_state
│       ├── param_ffi/                    参数传递
│       └── vendor_params/                厂商专用参数
│
├── motor_vendors/
│   └── damiao/             ★ 达妙驱动（reBot 用）
│       └── src/
│           ├── lib.rs
│           ├── motor.rs       MotorDevice 实现（型号表：4310/4340P 等 9 款）
│           ├── controller.rs  厂商控制器封装
│           ├── protocol.rs    CAN 帧编解码：encode_mit_cmd / decode_feedback 等
│           └── registers.rs   寄存器 ID + 访问类型
│
├── bindings/
│   ├── python/             ★ Python 包（就是 pip install motorbridge 装的东西）
│   │   └── src/motorbridge/
│   │       ├── __init__.py       对外导出
│   │       ├── abi.py            ctypes 加载 .so/.dll + 函数签名
│   │       ├── core.py           Controller / Motor 类（主入口）
│   │       ├── models.py         Mode 枚举 + MotorState dataclass
│   │       ├── errors.py         异常定义
│   │       ├── damiao_registers.py   达妙寄存器 ID 常量
│   │       └── cli.py            命令行
│   └── cpp/                C++ 头文件
│
├── examples/               多语言示例（c/cpp/python/web）
├── docs/                   文档
├── scripts/                构建脚本
└── tools/
```

---

## 五层调用栈

```
  ┌────────────────────────────────────────────┐
  │ 第 5 层 用户代码                            │
  │   import motorbridge                       │
  │   reBotArm_control_py 在这一层              │
  └─────────────────┬──────────────────────────┘
                    ↓
  ┌────────────────────────────────────────────┐
  │ 第 4 层 Python 绑定层                       │
  │   bindings/python/src/motorbridge/         │
  │   core.py: Controller / Motor              │
  │   abi.py:  ctypes FFI                      │
  └─────────────────┬──────────────────────────┘
                    ↓  ctypes 调用 motor_abi.so
  ┌────────────────────────────────────────────┐
  │ 第 3 层 C ABI 导出层                        │
  │   motor_abi/src/*.rs                       │
  │   extern "C" fn motor_handle_send_mit(...) │
  └─────────────────┬──────────────────────────┘
                    ↓  trait dispatch
  ┌────────────────────────────────────────────┐
  │ 第 2 层 厂商驱动层                          │
  │   motor_vendors/damiao/src/                │
  │   impl MotorDevice for DamiaoMotor         │
  │   protocol.rs 把参数编码成 CAN 帧           │
  └─────────────────┬──────────────────────────┘
                    ↓  CanBus trait
  ┌────────────────────────────────────────────┐
  │ 第 1 层 核心 + 硬件层                       │
  │   motor_core/src/                          │
  │   dm_serial.rs / socketcan.rs / pcan.rs    │
  │   → 串口 / Linux 驱动 / Windows 驱动         │
  └─────────────────┬──────────────────────────┘
                    ↓
              [ CAN 总线 1Mbps ]
                    ↓
              [ 达妙电机 ]
```

---

## 核心 API（Python 层）

### 1. 创建 Controller — 三种总线选一种

```python
from motorbridge import Controller, Motor, Mode

# 方式 A：Linux SocketCAN
ctrl = Controller("can0")

# 方式 B：Linux SocketCAN-FD
ctrl = Controller.from_socketcanfd("can0")

# 方式 C：达妙 USB-CAN 串口桥（★ reBot 用这个）
ctrl = Controller.from_dm_serial("/dev/ttyACM0", 921600)
```

### 2. 添加电机

```python
motor = ctrl.add_damiao_motor(
    motor_id=1,           # 电机 ID
    feedback_id=0x11,     # 反馈帧的 arbitration ID
    model="4340P"         # 型号（决定 pmax/vmax/tmax）
)

# 其他厂商
ctrl.add_robstride_motor(...)
ctrl.add_myactuator_motor(...)
ctrl.add_hexfellow_motor(...)
ctrl.add_hightorque_motor(...)
```

### 3. 使能 + 设置模式

```python
ctrl.enable_all()              # 使能所有电机
motor.ensure_mode(Mode.MIT)    # 切换到 MIT 模式
```

### 4. 发送控制命令（4 种模式）

```python
# MIT 模式（位置+速度+阻抗+前馈力矩，最灵活）
motor.send_mit(pos=0.0, vel=0.0, kp=10, kd=1, tau=0.5)

# POS_VEL 模式（位置 + 速度上限）
motor.send_pos_vel(pos=1.57, vlim=5.0)

# VEL 模式（纯速度）
motor.send_vel(vel=2.0)

# FORCE_POS 模式（有力限的位置）
motor.send_force_pos(pos=1.0, vlim=3.0, ratio=0.5)
```

### 5. 读取状态

```python
state = motor.get_state()   # MotorState 或 None
# state.pos, state.vel, state.torq, state.t_mos, state.t_rotor, state.status_code
```

### 6. 寄存器操作（高级）

```python
from motorbridge import RID_KP_APR, RID_KI_APR

motor.write_register_f32(RID_KP_APR, 1.0)
val = motor.get_register_f32(RID_KP_APR, timeout_ms=1000)
motor.store_parameters()  # 写入 Flash 永久保存
```

### 7. 清理

```python
ctrl.shutdown()
ctrl.close()

# 或用 context manager
with Controller.from_dm_serial("/dev/ttyACM0") as ctrl:
    ...  # 退出自动 shutdown + close
```

---

## 支持的电机（达妙）

从 `motor_vendors/damiao/src/motor.rs` 抓出来的型号表：

| 型号 | pmax (rad) | vmax (rad/s) | tmax (Nm) | 备注 |
|------|-----------|--------------|-----------|------|
| 3507 | 12.566 | 50.0 | 5.0 | 小型 |
| 4310 | 12.5 | 30.0 | 10.0 | ★ reBot 小关节 J4~J6 |
| 4310P | 12.5 | 50.0 | 10.0 | Plus 版（高速） |
| 4340 | 12.5 | 10.0 | 28.0 | 大扭矩 |
| **4340P** | 12.5 | 10.0 | 28.0 | ★ reBot 大关节 J1~J3 |
| 6006 | 12.5 | 45.0 | 20.0 | |
| 8006 | 12.5 | 45.0 | 40.0 | |
| 8009 | 12.5 | 45.0 | 54.0 | |
| 10010L | 12.5 | ... | ... | 超大扭矩 |

这些参数用于 MIT 模式的编码（把 float 映射到 CAN 帧的 16bit 整数域）。

---

## 四种控制模式对比

| 模式 | IntEnum | 参数 | 底层 CAN 命令 | 适用场景 |
|------|---------|------|--------------|---------|
| MIT | 1 | pos, vel, kp, kd, tau | `encode_mit_cmd` | 重力补偿、阻抗、力控 |
| POS_VEL | 2 | pos, vlim | `encode_pos_vel_cmd` | 平滑运动（reBot 默认） |
| VEL | 3 | vel | `encode_vel_cmd` | 连续转动 |
| FORCE_POS | 4 | pos, vlim, ratio | `encode_force_pos_cmd` | 带力限的位置 |

---

## 多线程模型

`CoreController::new(bus)` 创建后，**自动启动后台接收线程**（`polling_thread`）：

```rust
// motor_core/src/controller.rs 的 polling 线程做的事：
loop {
    let frame = bus.recv(timeout);           // 阻塞读一帧
    let motor_id = decode_arbitration(frame);
    let device = devices.get(&motor_id);
    device.on_feedback(frame);               // 把反馈塞给对应电机的缓存
}
```

- 用户调 `motor.get_state()` 时，是从**缓存**读的，不阻塞 CAN
- 用户调 `motor.send_mit()` 时，直接 `bus.send(frame)`，发送和接收互不干扰
- `devices: HashMap<u16, Arc<dyn MotorDevice>>` 用 Mutex 保护

---

## 与 reBotArm_control_py 的关系

reBotArm_control_py 是 MotorBridge 的用户，包装关系如下：

| reBotArm_control_py | MotorBridge |
|---------------------|-------------|
| `RobotArm.connect()` | `Controller.from_dm_serial("/dev/ttyACM0", 921600)` |
| `RobotArm.enable()` | `ctrl.enable_all()` |
| `RobotArm.mode_mit()` | 每个 motor `ensure_mode(Mode.MIT)` |
| `RobotArm.mit(pos_array, ...)` | 遍历每个 motor `send_mit(pos[i], ...)` |
| `RobotArm.pos_vel(pos_array, vlim_array)` | 遍历 `send_pos_vel(pos[i], vlim[i])` |
| `RobotArm.get_state()` | 遍历 `motor.get_state()` 聚合成 np.array |
| `RobotArm.poll_feedback()` | `ctrl.poll_feedback_once()` |

换句话说 `reBotArm_control_py/actuator/arm.py` 里的 `RobotArm` 类基本上就是「6 个 Motor 打包成数组接口」。

---

## 一次完整调用链（发 MIT 命令）

以 `motor.send_mit(1.5, 0, 10, 1, 0.5)` 为例，自上而下：

```
1. [Python] core.py Motor.send_mit
   └─ self._abi.lib.motor_handle_send_mit(self._ptr, 1.5, 0, 10, 1, 0.5)

2. [FFI] ctypes 调用 libmotor_abi.so 的 motor_handle_send_mit 函数

3. [Rust C ABI] motor_abi/src/motor_control_ffi.rs
   └─ 把 *mut Handle 转成 &DamiaoMotor
   └─ motor.send_mit(pos, vel, kp, kd, tau)

4. [Rust vendor] motor_vendors/damiao/src/motor.rs
   └─ protocol::encode_mit_cmd(pos, vel, kp, kd, tau, limits)
       把 5 个 f32 压成 8 字节 CAN data：
       [pos_16bit, vel_12bit+kp_12bit, kd_12bit+tau_12bit]
   └─ self.bus.send(CanFrame { arbitration_id: 0x01, data, dlc: 8, ... })

5. [Rust bus] motor_core/src/dm_serial.rs (因为 reBot 用 USB-CAN 串口桥)
   └─ 构造达妙串口协议帧（AT 头 + CAN ID + CAN data + 校验）
   └─ serial.write(bytes)

6. [硬件] USB → 达妙 USB-CAN 桥接板 → CAN 总线 → 电机
```

电机执行后，反馈帧沿原路返回，但走的是 `polling_thread` 异步路径，不是 send 的调用链。

---

## 入口文件索引

想读源码从哪开始？

| 想了解 | 读这个文件 |
|-------|-----------|
| Python API 全貌 | `bindings/python/src/motorbridge/core.py` |
| C ABI 函数列表 | `motor_abi/src/*.rs`（每个文件对应一类 API） |
| CAN 协议编解码 | `motor_vendors/damiao/src/protocol.rs` |
| 达妙电机如何实现 MotorDevice | `motor_vendors/damiao/src/motor.rs` |
| 后台接收线程 | `motor_core/src/controller.rs` |
| 达妙 USB-CAN 串口协议 | `motor_core/src/dm_serial.rs` |
| 寄存器 ID 清单 | `bindings/python/src/motorbridge/damiao_registers.py` |
| 使用示例 | `examples/python/python_ctypes_demo.py` |
| 官方快速入门 | `bindings/python/DAMIAO_API.zh-CN.md` |

---

## 配套图表

- `MotorBridge_architecture.drawio` — 项目层次架构图
- `MotorBridge_运行流程.drawio` — 「Python 调用 → 电机转动」完整数据流
