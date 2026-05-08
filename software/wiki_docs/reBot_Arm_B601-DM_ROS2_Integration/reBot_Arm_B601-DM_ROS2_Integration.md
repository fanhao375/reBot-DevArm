# reBot Arm B601-DM ROS2 Integration

> 发布时间: 2026-04-29T00:00:00.000Z
> 原文链接: https://wiki.seeedstudio.com/rebot_arm_b601_dm_ros2_integration/

---
On this page

![reBot Arm B601-DM](https://raw.githubusercontent.com/Seeed-Projects/reBot-DevArm/main/media/v1.0.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)![ROS2 Jazzy](https://img.shields.io/badge/ROS2-Jazzy-blue.svg)![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)![Platform](https://img.shields.io/badge/Platform-Ubuntu%2024.04-orange.svg)![Hardware](images/img_006.svg)

**ROS2 Control · Gripper Control · Standard Trajectory Interface · Gravity Compensation · RViz Visualization · Fully Open Source**

This tutorial shows how to run the ROS2 control workspace `rebotarm_ros2` for the reBot Arm B601-DM. The workspace wraps the low-level `reBotArm_control_py` Python SDK into ROS2 topics, services, and actions, making it easier to integrate upper-level planning, visual grasping, RViz visualization, and custom application development.

note

This tutorial uses `Ubuntu 24.04 + ROS2 Jazzy + Python 3.12` as the main reference environment. ROS2 Humble / Ubuntu 22.04 can follow the same workflow with the corresponding ROS2 distribution.

## Project Features[​](#project-features "Direct link to Project Features")

1.  **Standard ROS2 Interfaces**
    Provides common ROS2 interfaces such as `/joint_states`, `FollowJointTrajectory`, `GripperCommand`, and `MoveToPose`, making it easier to integrate with MoveIt2, visual grasping pipelines, or task-level systems.

2.  **Ready-to-use Kinematics, Trajectory, and Gravity Compensation Nodes**
    Provides out-of-the-box forward/inverse kinematics, trajectory execution, gravity compensation, and RViz visualization support.


## Specifications[​](#specifications "Direct link to Specifications")

The hardware for this tutorial is provided by [Seeed Studio](https://www.seeedstudio.com/).

Parameter

Specification

Robot Arm Model

reBot Arm B601-DM

Degrees of Freedom

6-DOF + Gripper

Motor Version

DAMIAO motor version

Communication

CAN Bus via USB2CAN serial bridge

Default Serial Port

`/dev/ttyACM0`

Recommended System

Ubuntu 24.04 + ROS2 Jazzy + Python 3.12

Reference System

Ubuntu 22.04 + ROS2 Humble + Python 3.10

## Bill of Materials (BOM)[​](#bill-of-materials-bom "Direct link to Bill of Materials (BOM)")

Component

Quantity

Included

reBot Arm B601-DM Robotic Arm

1

✅

Gripper

1

✅

USB2CAN Serial Bridge

1

✅

Power Adapter (24V)

1

✅

USB-C / Communication Cable

1

✅

Ubuntu Host PC

1

Self-prepared

## Wiring[​](#wiring "Direct link to Wiring")

1.  Connect the USB2CAN serial bridge to the robot arm CAN bus.
2.  Connect the 24V power supply and plug the USB2CAN adapter into the host PC.
3.  Confirm that the host recognizes the serial device:

```
ls /dev/ttyACM*
```

If you need to temporarily grant serial port permission:

```
sudo chmod 666 /dev/ttyACM0
```

It is recommended to add the current user to the `dialout` group instead. Log out and log back in for the change to take effect:

```
sudo usermod -a -G dialout $USER
```

## Environment Requirements[​](#environment-requirements "Direct link to Environment Requirements")

Item

Recommended Requirement

Operating System

Ubuntu 24.04, Ubuntu 22.04 can be used as reference

ROS2

Jazzy, Humble can be used as reference

Python

System Python. Jazzy usually uses 3.12, while Humble usually uses 3.10

## Installation Steps[​](#installation-steps "Direct link to Installation Steps")

### Step 0. Complete Basic Robot Arm Setup[​](#step-0-complete-basic-robot-arm-setup "Direct link to Step 0. Complete Basic Robot Arm Setup")

Before starting the ROS2 integration, please complete the [reBot Arm B601-DM Getting Started Guide](https://wiki.seeedstudio.com/rebot_b601_dm_getting_started/), including assembly, motor ID configuration, zero-position initialization, and basic connectivity verification.

### Step 1. Install the ROS2 Version for Your Ubuntu System[​](#step-1-install-the-ros2-version-for-your-ubuntu-system "Direct link to Step 1. Install the ROS2 Version for Your Ubuntu System")

Please refer to the official ROS2 documentation:

-   [ROS2 Jazzy Ubuntu Installation](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)
-   [ROS2 Humble Ubuntu Installation](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html)

### Step 2. Install Build Tools and ROS Dependencies[​](#step-2-install-build-tools-and-ros-dependencies "Direct link to Step 2. Install Build Tools and ROS Dependencies")

Install colcon, pip, Git, and the ROS packages required by this workspace:

```
sudo apt updatesudo apt install -y python3-colcon-common-extensions python3-pip gitsudo apt install -y \  ros-jazzy-control-msgs \  ros-jazzy-trajectory-msgs \  ros-jazzy-tf-transformations \  ros-jazzy-robot-state-publisher \  ros-jazzy-rviz2 \  ros-jazzy-pinocchio
```

Verify the installation:

```
source /opt/ros/jazzy/setup.bashpython3 -c "import pinocchio; print('pinocchio', pinocchio.__version__)"
```

If you use ROS2 Humble, replace the `ros-jazzy-*` package names with `ros-humble-*` and source `/opt/ros/humble/setup.bash`.

### Step 3. Clone the Code Repository[​](#step-3-clone-the-code-repository "Direct link to Step 3. Clone the Code Repository")

Use the Seeed-Projects official repository by default:

```
mkdir -p ~/seeedcd ~/seeedgit clone https://github.com/Seeed-Projects/reBotArmController_ROS2.git rebotarm_ros2cd rebotarm_ros2
```

You can also use the current development repository:

```
mkdir -p ~/seeedcd ~/seeedgit clone https://github.com/EclipseaHime017/reBotArmController_ROS2.git rebotarm_ros2cd rebotarm_ros2
```

### Step 4. Install motorbridge[​](#step-4-install-motorbridge "Direct link to Step 4. Install motorbridge")

Install `motorbridge` from the official PyPI source:

```
python3 -m pip install --user --break-system-packages --index-url https://pypi.org/simple motorbridge
```

### Step 5. Get the Low-level SDK[​](#step-5-get-the-low-level-sdk "Direct link to Step 5. Get the Low-level SDK")

```
cd ~/seeed/rebotarm_ros2mkdir -p third_partygit clone https://github.com/vectorBH6/reBotArm_control_py.git third_party/reBotArm_control_py
```

### Step 6. Build the Workspace[​](#step-6-build-the-workspace "Direct link to Step 6. Build the Workspace")

```
cd ~/seeed/rebotarm_ros2source /opt/ros/jazzy/setup.bashcolcon build --symlink-installsource install/setup.bash
```

Verify the executable entries:

```
ros2 pkg executables rebotarmcontroller
```

Expected entries include:

```
rebotarmcontroller reBotArmControllerrebotarmcontroller GravityCompensationrebotarmcontroller GripperControlrebotarmcontroller MoveTorebotarmcontroller MoveToPose
```

## Quick Start[​](#quick-start "Direct link to Quick Start")

### Start the Full System[​](#start-the-full-system "Direct link to Start the Full System")

The full bringup launches:

-   `reBotArmController` control node
-   `robot_state_publisher`
-   Optional RViz

```
cd ~/seeed/rebotarm_ros2source /opt/ros/jazzy/setup.bashsource install/setup.bashros2 launch rebotarm_bringup bringup.launch.py channel:=/dev/ttyACM0
```

If your serial port is not `/dev/ttyACM0`, replace it with the actual device name:

```
ros2 launch rebotarm_bringup bringup.launch.py channel:=/dev/ttyACM1
```

### Start RViz Visualization[​](#start-rviz-visualization "Direct link to Start RViz Visualization")

```
ros2 launch rebotarm_bringup bringup.launch.py channel:=/dev/ttyACM0 use_rviz:=true
```

If the model appears too small in RViz, adjust the view from the `Views` panel on the left:

-   Set `Target Frame` to `base_link`
-   Adjust `Distance`, for example to `1.0` or `1.5`
-   Use the mouse wheel to zoom
-   Confirm that `Fixed Frame` is set to `base_link`

### Start Only the Control Node[​](#start-only-the-control-node "Direct link to Start Only the Control Node")

If URDF and RViz are not needed:

```
ros2 launch rebotarm_bringup driver_only.launch.py channel:=/dev/ttyACM0
```

You can also run the node directly:

```
ros2 run rebotarmcontroller reBotArmController
```

## ROS2 Namespace[​](#ros2-namespace "Direct link to ROS2 Namespace")

The default namespace is:

```
/rebotarm
```

Therefore, all topics, services, and actions are prefixed with `/rebotarm`, for example:

```
/rebotarm/joint_states/rebotarm/enable/rebotarm/move_to_pose
```

If you need multiple robot arms or want to run alongside other ROS2 systems, you can change the namespace at launch time:

```
ros2 launch rebotarm_bringup bringup.launch.py arm_namespace:=left_arm
```

In this case, `/rebotarm/joint_states` becomes `/left_arm/joint_states`. The namespace only affects topic, service, and action names in the ROS graph. It does not automatically change TF frame names in the URDF.

## Common APIs[​](#common-apis "Direct link to Common APIs")

### Status Topics[​](#status-topics "Direct link to Status Topics")

API

Type

Description

`/rebotarm/joint_states`

`sensor_msgs/msg/JointState`

6-axis joint positions, velocities, and efforts

`/rebotarm/arm_status`

`rebotarm_msgs/msg/ArmStatus`

Control mode, enabled state, state machine, and error codes

`/rebotarm/joints/<joint>/state`

`rebotarm_msgs/msg/JointMotorState`

Single-joint motor state

`/rebotarm/gripper/state`

`rebotarm_msgs/msg/JointMotorState`

Gripper motor state

Examples:

```
ros2 topic echo /rebotarm/joint_states --onceros2 topic echo /rebotarm/arm_status --once
```

### Services[​](#services "Direct link to Services")

API

Type

Description

`/rebotarm/enable`

`std_srvs/srv/Trigger`

Enable the robot arm

`/rebotarm/disable`

`std_srvs/srv/Trigger`

Disable the robot arm

`/rebotarm/safe_home`

`std_srvs/srv/Trigger`

Move back to the safe home position

`/rebotarm/set_mode`

`rebotarm_msgs/srv/SetMode`

Switch between `mit`, `pos_vel`, and `vel`

`/rebotarm/set_zero`

`rebotarm_msgs/srv/SetZero`

Set zero position for all joints or a single joint

`/rebotarm/move_to_pose_ik`

`rebotarm_msgs/srv/MoveToPoseIK`

IK pre-check and target joint solution

`/rebotarm/gripper/set`

`rebotarm_msgs/srv/SetGripper`

Set gripper motor position in rad

`/rebotarm/gravity_compensation/start`

`std_srvs/srv/Trigger`

Start gravity compensation

`/rebotarm/gravity_compensation/stop`

`std_srvs/srv/Trigger`

Stop gravity compensation

### Actions[​](#actions "Direct link to Actions")

API

Type

Description

`/rebotarm/move_to_pose`

`rebotarm_msgs/action/MoveToPose`

End-effector pose motion

`/rebotarm/follow_joint_trajectory`

`control_msgs/action/FollowJointTrajectory`

Standard joint trajectory compatible entry point

`/rebotarm/gripper/command`

`control_msgs/action/GripperCommand`

Standard gripper action

## Basic Control Examples[​](#basic-control-examples "Direct link to Basic Control Examples")

### 1\. Enable the Robot Arm[​](#1-enable-the-robot-arm "Direct link to 1. Enable the Robot Arm")

```
ros2 service call /rebotarm/enable std_srvs/srv/Trigger
```

### 2\. Move to an End-effector Pose[​](#2-move-to-an-end-effector-pose "Direct link to 2. Move to an End-effector Pose")

```
ros2 action send_goal /rebotarm/move_to_pose rebotarm_msgs/action/MoveToPose \  "{target_pose: {position: {x: 0.30, y: 0.0, z: 0.30}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}, duration: 2.0}"
```

### 3\. Send a Joint Target[​](#3-send-a-joint-target "Direct link to 3. Send a Joint Target")

```
ros2 action send_goal /rebotarm/follow_joint_trajectory \  control_msgs/action/FollowJointTrajectory \  "{trajectory: {joint_names: ['joint1','joint2','joint3','joint4','joint5','joint6'],    points: [{positions: [0.1,0,0,0,0,0], time_from_start: {sec: 5}}]}}"
```

### 4\. Safe Home and Disable[​](#4-safe-home-and-disable "Direct link to 4. Safe Home and Disable")

```
ros2 service call /rebotarm/safe_home std_srvs/srv/Triggerros2 service call /rebotarm/disable std_srvs/srv/Trigger
```

## Demo Examples[​](#demo-examples "Direct link to Demo Examples")

All examples assume that `reBotArmController` is already running:

```
cd ~/seeed/rebotarm_ros2source /opt/ros/jazzy/setup.bashsource install/setup.bashros2 launch rebotarm_bringup bringup.launch.py channel:=/dev/ttyACM0
```

### Joint Motion Example[​](#joint-motion-example "Direct link to Joint Motion Example")

Control all 6 joints at once. The unit is rad:

```
ros2 run rebotarmcontroller MoveTo -- \  0.20 -0.20 -0.20 -0.20 0.10 -0.10 \  --duration 8.0
```

Control only one joint:

```
ros2 run rebotarmcontroller MoveTo -- --joint joint3 --position -0.20 --duration 5.0
```

### End-effector Pose Example[​](#end-effector-pose-example "Direct link to End-effector Pose Example")

```
ros2 run rebotarmcontroller MoveToPose -- --x 0.30 --y 0.0 --z 0.30 --qw 1.0 --duration 2.0
```

### Gravity Compensation Example[​](#gravity-compensation-example "Direct link to Gravity Compensation Example")

```
ros2 run rebotarmcontroller GravityCompensation
```

The script first calls `/rebotarm/enable`, then starts gravity compensation. When you press `Ctrl+C`, the script calls the following services in order:

1.  `/rebotarm/gravity_compensation/stop`
2.  `/rebotarm/safe_home`
3.  `/rebotarm/disable`

This stops gravity compensation first, then moves the arm back to the safe home position and disables it.

You can also call the services manually:

```
ros2 service call /rebotarm/enable std_srvs/srv/Triggerros2 service call /rebotarm/gravity_compensation/start std_srvs/srv/Triggerros2 service call /rebotarm/gravity_compensation/stop std_srvs/srv/Triggerros2 service call /rebotarm/safe_home std_srvs/srv/Triggerros2 service call /rebotarm/disable std_srvs/srv/Trigger
```

### Interactive Gripper Example[​](#interactive-gripper-example "Direct link to Interactive Gripper Example")

```
ros2 run rebotarmcontroller GripperControl
```

After launch, enter:

```
o / open    Open the gripperc / close   Close the gripperq / quit    Quit
```

## Configuration[​](#configuration "Direct link to Configuration")

Default configuration files are located at:

```
src/rebotarm_bringup/config/
```

File

Description

`arm.yaml`

Motor, feedback ID, and control parameters for the 6 arm joints

`gripper.yaml`

Gripper motor ID, feedback ID, vendor, and control parameters

`driver_params.yaml`

ROS parameter examples

Common launch parameters:

Parameter

Default

Description

`arm_config`

Built-in `arm.yaml` from bringup

Arm configuration path

`gripper_config`

Built-in `gripper.yaml` from bringup

Gripper configuration path

`channel`

Empty string

Use YAML by default. Override the serial port when non-empty

`joint_state_rate`

`100.0`

Publish rate of `/rebotarm/joint_states`

`cmd_arbitration`

`reject`

Arbitration policy for low-level commands during trajectory execution

`arm_namespace`

`rebotarm`

ROS namespace prefix

`frame_id`

`base_link`

Robot arm base frame

`ee_frame_id`

`end_link`

End-effector frame

`use_rviz`

`false`

Whether to start RViz

## Low-level Command Topics[​](#low-level-command-topics "Direct link to Low-level Command Topics")

The ROS2 workspace also provides low-level motor debugging topics:

API

Type

Description

`/rebotarm/joints/<joint>/cmd/mit`

`rebotarm_msgs/msg/JointMitCmd`

Single-joint MIT raw command

`/rebotarm/joints/<joint>/cmd/pos_vel`

`rebotarm_msgs/msg/JointPosVelCmd`

Single-joint position-velocity raw command

`/rebotarm/joints/<joint>/cmd/vel`

`rebotarm_msgs/msg/JointVelCmd`

Single-joint velocity raw command

`/rebotarm/gripper/cmd/mit`

`rebotarm_msgs/msg/JointMitCmd`

Gripper MIT raw command

`/rebotarm/gripper/cmd/pos_vel`

`rebotarm_msgs/msg/JointPosVelCmd`

Gripper position-velocity raw command

`/rebotarm/gripper/cmd/vel`

`rebotarm_msgs/msg/JointVelCmd`

Gripper velocity raw command

caution

Low-level command topics are intended for debugging and experiments. They do not perform IK, trajectory planning, or URDF limit checks. For application-level motion, prefer services and actions such as `/move_to_pose`, `/follow_joint_trajectory`, and `/gripper/set`.

## FAQ[​](#faq "Direct link to FAQ")

### 1\. `open serial port /dev/ttyACM0 failed` appears at startup[​](#1-open-serial-port-devttyacm0-failed-appears-at-startup "Direct link to 1-open-serial-port-devttyacm0-failed-appears-at-startup")

This means the default serial port does not exist or the device name has changed. First check the actual serial device:

```
ls /dev/ttyACM*
```

Then specify it with `channel`:

```
ros2 launch rebotarm_bringup bringup.launch.py channel:=/dev/ttyACM1
```

### 2\. `Device or resource busy` appears at startup[​](#2-device-or-resource-busy-appears-at-startup "Direct link to 2-device-or-resource-busy-appears-at-startup")

This means the serial port is already occupied by another process. Common causes include a previously launched ROS2 node, an SDK example, or a debugging script that has not exited. Check the processes first:

```
ps aux | grep -E "reBotArmController|ros2|python"
```

Stop the process occupying the serial port and restart. The arm and gripper should share the same low-level Controller. Do not open the same serial port separately for the arm and gripper.

### 3\. Permission denied[​](#3-permission-denied "Direct link to 3. Permission denied")

If the serial device exists but permission is denied:

```
sudo usermod -a -G dialout $USER
```

Log out and log back in for the change to take effect. For temporary debugging, you can also run:

```
sudo chmod 666 /dev/ttyACM0
```

### 4\. Robot model is not displayed in RViz[​](#4-robot-model-is-not-displayed-in-rviz "Direct link to 4. Robot model is not displayed in RViz")

Check the following:

-   Whether the workspace has been sourced: `source install/setup.bash`
-   Whether `Fixed Frame` is set to `base_link`
-   Whether `robot_state_publisher` started correctly
-   Whether the URDF mesh path is `package://rebotarm_bringup/description/meshes/...`

### 5\. FastDDS SHM port warning appears[​](#5-fastdds-shm-port-warning-appears "Direct link to 5. FastDDS SHM port warning appears")

If the terminal shows something like:

```
[RTPS_TRANSPORT_SHM Error] Failed init_port fastrtps_port7002: open_and_lock_file failed
```

This is usually caused by leftover FastDDS shared-memory lock files after a previous ROS2 process exited abnormally. If services and actions still respond normally, this warning usually does not affect control.

To clean it up, stop the related ROS2 processes first, then run:

```
pkill -f ros2pkill -f reBotArmControllerrm -f /dev/shm/fastrtps_port*
```

If you want to temporarily bypass shared memory transport, set the following before launching ROS2:

```
export FASTDDS_BUILTIN_TRANSPORTS=UDPv4
```

### 6\. What if I use Humble?[​](#6-what-if-i-use-humble "Direct link to 6. What if I use Humble?")

Humble users can follow the same workflow, replace `jazzy` with `humble` in the commands, and install the corresponding dependencies according to the Humble official documentation. After switching ROS2 distributions, run `colcon build` again.

### 7\. `pinocchio` cannot be found[​](#7-pinocchio-cannot-be-found "Direct link to 7-pinocchio-cannot-be-found")

If a node or verification command reports:

```
ModuleNotFoundError: No module named 'pinocchio'
```

First make sure the Pinocchio package for your ROS2 distribution is installed:

```
sudo apt install -y ros-jazzy-pinocchio
```

Then make sure the current terminal has sourced the ROS2 environment:

```
source /opt/ros/jazzy/setup.bashpython3 -c "import pinocchio; print(pinocchio.__version__)"
```

If it still cannot be found, check whether the current Python search path contains the ROS2 Python package path:

```
python3 -c "import sys; print('\n'.join(sys.path))"
```

After sourcing Jazzy, you should see a path similar to `/opt/ros/jazzy/lib/python3.12/site-packages`. If you use Humble, replace `jazzy` with `humble` in the commands.

## Contact[​](#contact "Direct link to Contact")

-   Technical Support: [Submit an Issue](https://github.com/EclipseaHime017/reBotArmController_ROS2/issues)
-   Project Repository: [Github](https://github.com/EclipseaHime017/reBotArmController_ROS2)
-   Forum: [Seeed Studio Forum](https://forum.seeedstudio.com/)

## References[​](#references "Direct link to References")

-   [reBot Arm B601-DM Getting Started](https://wiki.seeedstudio.com/rebot_b601_dm_getting_started/)
-   [reBot Arm B601-DM Visual Grasping Demo](https://wiki.seeedstudio.com/rebot_arm_b601_dm_grasping_demo/)
-   [reBot Arm B601-DM Pinocchio and MeshCat](https://wiki.seeedstudio.com/rebot_arm_b601_dm_pinocchio_meshcat/)
-   [reBot Arm B601-DM LeRobot Tutorial](https://wiki.seeedstudio.com/rebot_arm_b601_dm_lerobot/)
-   [ROS2 Humble Documentation](https://docs.ros.org/en/humble/)
-   [ROS2 Jazzy Documentation](https://docs.ros.org/en/jazzy/)
-   [reBotArm\_control\_py](https://github.com/vectorBH6/reBotArm_control_py)