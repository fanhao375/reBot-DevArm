# Getting Started with Pinocchio and MeshCat for reBot Arm B601-DM

> 发布时间: 2026-03-24T00:00:00.000Z
> 原文链接: https://wiki.seeedstudio.com/rebot_arm_b601_dm_pinocchio_meshcat/

---
On this page

![traj\_sim\_geodesic](images/img_001.png)

[![License: MIT](images/img_002.svg)](./LICENSE)![Python Version](images/img_003.svg)![Platform](images/img_004.svg)![Pinocchio](images/img_005.svg)

**6-DOF Robotic Arm · Multi-Motor Support · Kinematics Solver · Trajectory Planning · Fully Open Source**

* * *

## 📖 Introduction[​](#-introduction "Direct link to 📖 Introduction")

**reBotArm Control** is a Python control library for the reBot Arm B601 robotic arm, providing a complete solution from low-level motor control to high-level kinematics computation.

### ✨ Core Features[​](#-core-features "Direct link to ✨ Core Features")

-   🦾 **Dual Model Support** — B601-DM (Damiao motors) and B601-RS (RobStride motors)
-   🧮 **Kinematics Solver** — Forward/Inverse kinematics based on Pinocchio
-   🛤️ **Trajectory Planning** — SE(3) geodesic trajectory + CLIK tracking
-   🔧 **Flexible Configuration** — YAML configuration file for quick hardware adaptation

* * *

## ⚙️ Quick Start[​](#️-quick-start "Direct link to ⚙️ Quick Start")

### Requirements[​](#requirements "Direct link to Requirements")

Item

Requirement

**Python**

3.10+

**Operating System**

Ubuntu 22.04+

**Communication Interface**

USB2CAN Serial Bridge or CAN Interface

### Installation Steps[​](#installation-steps "Direct link to Installation Steps")

#### Step 1. Install uv (if not installed)[​](#step-1-install-uv-if-not-installed "Direct link to Step 1. Install uv (if not installed)")

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Step 2. Sync Environment (Install All Dependencies)[​](#step-2-sync-environment-install-all-dependencies "Direct link to Step 2. Sync Environment (Install All Dependencies)")

```
git clone https://github.com/vectorBH6/reBotArm_control_py.gitcd reBotArm_control_pyuv sync
```

tip

`uv sync` will automatically create a virtual environment (if it doesn't exist) and install all dependencies according to `pyproject.toml` and `uv.lock`.

* * *

## 🔌 Hardware Configuration[​](#-hardware-configuration "Direct link to 🔌 Hardware Configuration")

### Default: Damiao USB2CAN Serial Bridge[​](#default-damiao-usb2can-serial-bridge "Direct link to Default: Damiao USB2CAN Serial Bridge")

reBot Arm B601-DM uses the Damiao USB2CAN serial bridge module by default.

**Hardware Connection**:

1.  Connect the USB2CAN module to your computer via USB cable
2.  The system will automatically recognize it as `/dev/ttyACM0` device

**Configuration Verification**:

```
ls /dev/ttyACM0motorbridge-cli scan --vendor damiao --transport dm-serial \    --serial-port /dev/ttyACM0 --serial-baud 921600
```

### Optional: Standard CAN Interface[​](#optional-standard-can-interface "Direct link to Optional: Standard CAN Interface")

Using other USB-CAN adapters (CANable, PCAN, etc.):

```
sudo ip link set can0 up type can bitrate 500000ip -details link show can0
```

### Motor Brand Configuration[​](#motor-brand-configuration "Direct link to Motor Brand Configuration")

Motor Brand

Transmission

Configuration

Baud Rate

**Damiao**

Serial Bridge

`dm-serial`

921600

**Damiao**

CAN Interface

`socketcan`

500000

**RobStride**

CAN Interface

`socketcan`

500000

tip

-   For Damiao motors using serial bridge, must set `--transport dm-serial`
-   Feedback ID rule: `feedback_id = motor_id + 0x10`

* * *

## 📁 Project Structure[​](#-project-structure "Direct link to 📁 Project Structure")

```
reBotArm_control_py/├── config/                     # Configuration files│   └── robot.yaml              # Joint parameter configuration├── example/                    # Example programs│   ├── Debug Tools/│   │   ├── 1_damiao_text.py        # Single motor console│   │   └── 2_zero_and_read.py      # Zero calibration│   ├── Kinematics Tests/│   │   ├── 5_fk_test.py            # Forward kinematics│   │   └── 6_ik_test.py            # Inverse kinematics│   ├── Real Machine Control/│   │   ├── 7_arm_ik_control.py     # IK real-time control│   │   ├── 8_arm_traj_control.py   # Trajectory planning│   │   └── 9_gravity_compensation.py  # Gravity compensation│   └── sim/                    # Simulation tools├── reBotArm_control_py/        # Core library│   ├── actuator/               # Actuator module│   ├── kinematics/             # Kinematics module│   ├── controllers/            # Controller module│   └── trajectory/             # Trajectory planning module├── urdf/                       # URDF model└── README.md
```

* * *

## 🎮 Example Programs[​](#-example-programs "Direct link to 🎮 Example Programs")

### Debug Tools[​](#debug-tools "Direct link to Debug Tools")

#### 1️⃣ Single Motor Console (`1_damiao_text.py`)[​](#1️⃣-single-motor-console-1_damiao_textpy "Direct link to 1️⃣-single-motor-console-1_damiao_textpy")

Direct motorbridge SDK single motor testing with three control modes.

**Usage**:

```
uv run python example/1_damiao_text.py
```

**Interactive Commands**:

Command

Description

`mit <pos_deg> [vel kp kd tau]`

MIT mode

`posvel <pos_deg> [vlim]`

POS\_VEL mode

`vel <vel_rad_s>`

Velocity mode

`enable` / `disable`

Enable/Disable

`set_zero`

Set zero position

`state`

View state

* * *

#### 2️⃣ Zero Calibration & Angle Monitor (`2_zero_and_read.py`)[​](#2️⃣-zero-calibration--angle-monitor-2_zero_and_readpy "Direct link to 2️⃣-zero-calibration--angle-monitor-2_zero_and_readpy")

Automatically set all joint zeros and display joint angles in real-time.

**Usage**:

```
uv run python example/2_zero_and_read.py
```

* * *

### Kinematics Tests[​](#kinematics-tests "Direct link to Kinematics Tests")

#### 5️⃣ Forward Kinematics Test (`5_fk_test.py`)[​](#5️⃣-forward-kinematics-test-5_fk_testpy "Direct link to 5️⃣-forward-kinematics-test-5_fk_testpy")

Calculate end-effector pose from joint angles.

**Input**: 6 joint angles (degrees)

**Output**:

-   End-effector position (X, Y, Z) — Unit: meters
-   Rotation matrix (3×3)
-   Euler angles (Roll/Pitch/Yaw) — Unit: degrees

**Example**:

```
uv run python example/5_fk_test.py> 0 0 0 0 0 0> 45 -30 15 -60 90 180
```

* * *

#### 6️⃣ Inverse Kinematics Test (`6_ik_test.py`)[​](#6��️⃣-inverse-kinematics-test-6_ik_testpy "Direct link to 6️⃣-inverse-kinematics-test-6_ik_testpy")

Solve joint angles from desired end-effector pose.

**Input Format**:

-   Position only: `<x> <y> <z>` (meters)
-   Position + Orientation: `<x> <y> <z> <roll> <pitch> <yaw>` (degrees)

**Example**:

```
uv run python example/6_ik_test.py> 0.25 0.0 0.15              > 0.25 0.0 0.15 0 0 0
```

* * *

### Real Machine Control[​](#real-machine-control "Direct link to Real Machine Control")

Permission Setup

Before running real machine control examples, you need to set device permissions:

```
sudo chmod 666 /dev/ttyACM0sudo chmod 666 /dev/can0
```

#### 7️⃣ IK Real-time Control (`7_arm_ik_control.py`)[​](#7️⃣-ik-real-time-control-7_arm_ik_controlpy "Direct link to 7️⃣-ik-real-time-control-7_arm_ik_controlpy")

Real-time end-effector control based on IK solver.

**Interactive Commands**:

Command

Description

`x y z [roll pitch yaw]`

Target end-effector pose

`state`

View current/target state

`pos`

Current end-effector position

`q/quit/exit`

Quit

**Usage**:

```
uv run python example/7_arm_ik_control.py> 0.3 0.0 0.2> 0.3 0.1 0.25 0 0.5 0
```

* * *

#### 8️⃣ Trajectory Planning Control (`8_arm_traj_control.py`)[​](#8️⃣-trajectory-planning-control-8_arm_traj_controlpy "Direct link to 8️⃣-trajectory-planning-control-8_arm_traj_controlpy")

SE(3) geodesic trajectory planning + CLIK tracking.

**Input Format**:

```
x y z [roll pitch yaw] [duration]
```

**Parameters**:

-   `x, y, z`: Target position (meters)
-   `roll, pitch, yaw`: Target orientation (radians)
-   `duration`: Movement duration (seconds), default 2.0s

**Usage**:

```
uv run python example/8_arm_traj_control.py> 0.3 0.0 0.3 0 0.4 0 2.0
```

* * *

#### 9️⃣ Gravity Compensation Control (`9_gravity_compensation.py`)[​](#9️⃣-gravity-compensation-control-9_gravity_compensationpy "Direct link to 9️⃣-gravity-compensation-control-9_gravity_compensationpy")

Compensates for joint gravity using Pinocchio dynamics model.

**Control Law**:

```
tau = g(q)          — Gravity feedforwardpos = current motor position  — Joint position follows current positionkp = 2,  kd = 1     — Unified stiffness/damping for all motors
```

**Expected Behavior**:

-   The robotic arm can "float" in any posture
-   Won't fall due to its own weight when released
-   Can be manually moved to any position

**Usage**:

```
uv run python example/9_gravity_compensation.py
```

**Output**:

-   Real-time display of expected torque for each joint (N·m)
-   Press `Ctrl+C` to stop and disconnect

* * *

## 📄 License[​](#-license "Direct link to 📄 License")

This project is open source under the **MIT License**.

* * *

## ☎ Contact Us[​](#-contact-us "Direct link to ☎ Contact Us")

-   **Technical Support**: [Submit Issue](https://github.com/vectorBH6/reBotArm_control_py/issues)
-   **Repository**: [GitHub](https://github.com/vectorBH6/reBotArm_control_py)

* * *

**🌟 If this project helps you, please give us a Star!**