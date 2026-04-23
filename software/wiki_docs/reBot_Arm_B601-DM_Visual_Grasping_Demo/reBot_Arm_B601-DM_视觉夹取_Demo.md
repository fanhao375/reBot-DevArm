# reBot Arm B601-DM 视觉夹取 Demo

> 发布时间: 2026-04-22T00:00:00.000Z
> 原文链接: https://wiki.seeedstudio.com/cn/rebot_arm_b601_dm_grasping_demo/

---
On this page

![reBot Arm B601-DM](images/img_001.png)

[![License: MIT](images/img_002.svg)](./LICENSE)![Python Version](images/img_003.svg)![Platform](images/img_004.svg)![Camera](images/img_005.svg)![YOLO](images/img_006.svg)

**深度感知 · 目标检测 · 手眼标定 · 自主抓取 · 全开源**

YOLO是一类广泛使用的实时目标检测模型，能够在单次前向推理中同时完成目标定位与类别识别。本教程基于YOLO、Orbbec Gemini 2深度相机，搭建一个可运行的reBot Arm B601-DM桌面视觉夹取Demo，并完成从环境安装、相机接入、手眼标定到抓取调试的完整流程。

## 项目特点[​](#项目特点 "Direct link to 项目特点")

1.  **YOLO + OBB 直接估计抓取姿态**
    直接利用检测框或 OBB 最小外接矩形，使用短轴作为夹爪开合方向，避免复杂 3D 点云处理。

2.  **机械臂与夹爪驱动轻量封装**
    主抓取脚本统一复用 `RebotArm` 接口，集成 IK、轨迹控制和夹爪状态机。

3.  **开源 & 可扩展**
    所有代码开源，支持用户根据需求自定义控制算法和效果。


## 规格参数[​](#规格参数 "Direct link to 规格参数")

本教程硬件由 [矽递科技 Seeed Studio](https://www.seeedstudio.com/) 提供

参数

规格

机械臂型号

reBot Arm B601-DM

自由度

6-DOF + 夹爪

相机型号

Orbbec Gemini 2

检测方式

YOLO + OBB 最小外接矩形

通信方式

CAN Bus via USB2CAN 适配器；USB 3.0 相机连接

工作电压

24V DC

控制主机

Ubuntu 22.04+ PC

推荐 Python 版本

Python 3.10

## 材料清单（BOM）[​](#材料清单bom "Direct link to 材料清单（BOM）")

部件

数量

是否包含

reBot Arm B601-DM 机械臂

1

✅

夹爪

1

✅

USB2CAN 串口桥

1

✅

电源适配器（24V）

1

✅

USB-C / 通信线缆

1

✅

Orbbec Gemini 2 深度相机

1

✅

Gemini 2 摄像头连接件 / 安装支架

1

✅

### 接线说明[​](#接线说明 "Direct link to 接线说明")

1.  将 Gemini 2 通过 USB 3.0 连接到主机。
2.  将 USB2CAN 适配器连接到机械臂 CAN 总线。
3.  确认 24V 电源、相机和机械臂全部连接可靠。
4.  配置权限：

```
sudo chmod a+rw /dev/bus/usb/*/*sudo chmod 666 /dev/ttyUSB0
```

## 环境要求[​](#环境要求 "Direct link to 环境要求")

项目

要求

操作系统

Ubuntu 22.04+

Python

3.10

推荐环境

conda

推荐工作区目录名

`rebot_grasp`

推荐 conda 环境名

`rebotarm`

## 安装步骤[​](#安装步骤 "Direct link to 安装步骤")

### 步骤 0. 先完成机械臂基础准备[​](#步骤-0-先完成机械臂基础准备 "Direct link to 步骤 0. 先完成机械臂基础准备")

开始本教程前，请先完成 [reBot Arm B601-DM 快速入门](https://wiki.seeedstudio.com/cn/rebot_b601_dm_getting_started/) 中的内容，包括机械臂组装、零点初始化、电机 ID 配置与基础连通性确认。

### 步骤 1. 克隆仓库[​](#步骤-1-克隆仓库 "Direct link to 步骤 1. 克隆仓库")

```
git clone https://github.com/Seeed-Projects/reBot-DevArm-Grasp.git rebot_graspcd rebot_grasp
```

### 步骤 2. 创建 Python 环境[​](#步骤-2-创建-python-环境 "Direct link to 步骤 2. 创建 Python 环境")

```
conda create -n rebotarm python=3.10 -yconda activate rebotarm
```

### 步骤 3. 安装项目依赖[​](#步骤-3-安装项目依赖 "Direct link to 步骤 3. 安装项目依赖")

```
pip install -r requirements.txt
```

### 步骤 4. 安装机械臂 SDK[​](#步骤-4-安装机械臂-sdk "Direct link to 步骤 4. 安装机械臂 SDK")

```
git clone https://github.com/vectorBH6/reBotArm_control_py.git sdk/reBotArm_control_pycd sdk/reBotArm_control_pypip install -e .cd ../..
```

### 步骤 5. 安装 Orbbec Gemini 2 SDK[​](#步骤-5-安装-orbbec-gemini-2-sdk "Direct link to 步骤 5. 安装 Orbbec Gemini 2 SDK")

本项目依赖 `pyorbbecsdk`。仓库默认不包含 `sdk/pyorbbecsdk`，需要你自行进入 `sdk/` 目录拉取官方仓库，或通过其他方式安装。

```
sudo apt-get updatesudo apt-get install -y cmake build-essential libusb-1.0-0-devcd sdkgit clone https://github.com/orbbec/pyorbbecsdk.gitcd pyorbbecsdkpip install -e .
```

也可以使用国内镜像：

```
cd sdkgit clone https://gitee.com/orbbecdeveloper/pyorbbecsdk.gitcd pyorbbecsdkpip install -e .
```

首次使用建议安装 udev 规则：

```
sudo bash scripts/install_udev_rules.shsudo udevadm control --reload-rulessudo udevadm trigger
```

### 步骤 6. 验证依赖[​](#步骤-6-验证依赖 "Direct link to 步骤 6. 验证依赖")

```
python -c "import pyorbbecsdk; print('pyorbbecsdk OK')"python -c "import motorbridge; print('motorbridge OK')"
```

首次使用 Orbbec 相机时，建议在你安装的 `pyorbbecsdk` 目录内执行 `scripts/install_udev_rules.sh` 安装 udev 规则，否则可能无法正常打开设备。

## 手眼标定[​](#手眼标定 "Direct link to 手眼标定")

第一次运行完整抓取前，先完成 Eye-in-Hand 手眼标定。

```
python scripts/collect_handeye_eih.py
```

开始前，请先在 `config/default.yaml` 中确认以下ArUco尺寸参数与你实际打印的标记一致：

```
calibration:  aruco:    marker_length_m: 0.1
```

自动模式下，机械臂会自动遍历 50 个预设姿态，检测到ArUco稳定后自动采样。即使中途按 `c` 或 `q` 中断，脚本也会尝试基于当前已有样本计算标定结果。

如果你希望手动推动机械臂采集，可以使用手动模式：

```
python scripts/collect_handeye_eih.py --manual
```

手动模式下，机械臂会进入重力补偿状态。你可以将末端推到合适视角后按 `Enter` 采集，按 `c` 或 `q` 结束并计算结果。

标定结果保存到：

```
config/calibration/orbbec_gemini2/hand_eye.npz
```

样本数建议：

-   最少 5 个样本
-   建议不少于 15 个样本

## 运行与调试[​](#运行与调试 "Direct link to 运行与调试")

### 1\. 仅验证目标检测[​](#1-仅验证目标检测 "Direct link to 1. 仅验证目标检测")

```
python scripts/object_detection.py
```

若需调整检测模型或类别，可在 `config/default.yaml` 中修改：

```
yolo:  model_name: "yoloe-26l-seg.pt"  device: "cpu"  use_world: true  custom_classes:    - "yellow banana"    - "water bottle"    - "cup"
```

用于确认：

-   相机可以正常打开
-   YOLO 模型加载正常
-   YOLO 目标检测功能正常

### 2\. 仅验证抓取估计[​](#2-仅验证抓取估计 "Direct link to 2. 仅验证抓取估计")

```
python scripts/ordinary_grasp_pipeline.py
```

若需要调整抓取估计频率或预抓取回退距离，可修改：

```
grasp_pipeline:  infer_every_live: 3  grasp:    depth_quantile: 0.6    pregrasp_offset_m: 0.080
```

这个脚本不会连接机械臂，只用于验证：

-   OBB 或最小外接矩形是否合理
-   抓取点是否位于目标中央区域
-   短轴方向是否符合夹爪开合方向预期

按键说明：

-   鼠标左键：点测深度
-   `G`：打印当前最佳抓取姿态
-   `Q` / `Esc`：退出

### 3\. 执行主抓取程序[​](#3-执行主抓取程序 "Direct link to 3. 执行主抓取程序")

```
python scripts/main.py
```

如果只想先验证目标位姿，不让机械臂真实动作：

```
python scripts/main.py --dry-run
```

建议先通过 `--dry-run` 验证位姿和工作空间，再执行真实抓取。

如果 `reBotArm_control_py` 不在默认位置，请在 `config/default.yaml` 中指定：

```
robot:  repo_root: null
```

默认保持 `null` 即可，程序会优先自动查找 `sdk/reBotArm_control_py`。

主程序执行流程：

1.  初始化机械臂与夹爪
2.  移动到预备位，如果需要调整机械臂启动后的预备位置，请在 `config/default.yaml` 中修改：

```
robot:  ready_pose:    x: 0.3    y: 0.0    z: 0.3    roll: 0.0    pitch: 1.0    duration: 3.0
```

3.  实时检测桌面目标
4.  基于短轴估计抓取姿态
5.  按 `G` 采当前帧并执行抓取

运行时按键：

-   `G`：抓取当前最佳目标
-   `R`：恢复实时预览
-   `Q` / `Esc`：退出程序

## FAQ[​](#faq "Direct link to FAQ")

### 1\. `ModuleNotFoundError: No module named 'motorbridge'`[​](#1-modulenotfounderror-no-module-named-motorbridge "Direct link to 1-modulenotfounderror-no-module-named-motorbridge")

表示当前 Python 环境还没有安装机械臂 SDK 依赖。请确认：

```
conda activate rebotarmpip install -r requirements.txtcd sdk/reBotArm_control_py && pip install -e .
```

### 2\. 按 `G` 后不执行抓取[​](#2-按-g-后不执行抓取 "Direct link to 2-按-g-后不执行抓取")

常见原因：

-   `hand_eye.npz` 不存在
-   手眼标定模式不是 `eye_in_hand`
-   当前目标位姿 IK 不可达

建议先运行：

```
python scripts/main.py --dry-run
```

### 3\. 抓取点深度不稳定[​](#3-抓取点深度不稳定 "Direct link to 3. 抓取点深度不稳定")

可以适当调整：

-   `grasp_pipeline.grasp.depth_quantile`
-   相机与目标的安装高度
-   目标表面的反光情况

## 联系方式[​](#联系方式 "Direct link to 联系方式")

-   技术支持：[提交 Issue](https://github.com/EclipseaHime017/reBot-DevArm-Grasp/issues)
-   项目地址：[Github](https://github.com/EclipseaHime017/reBot-DevArm-Grasp)
-   论坛：[Seeed Studio Forum](https://forum.seeedstudio.com/)

## 参考文档[​](#参考文档 "Direct link to 参考文档")

-   [reBot Arm B601-DM 快速入门](https://wiki.seeedstudio.com/cn/rebot_b601_dm_getting_started/)
-   [reBot Arm B601-DM Pinocchio 与 MeshCat](https://wiki.seeedstudio.com/cn/rebot_arm_b601_dm_pinocchio_meshcat/)
-   [reBot Arm B601-DM LeRobot 教程](https://wiki.seeedstudio.com/cn/rebot_arm_b601_dm_lerobot/)
-   [Orbbec Gemini 2 产品页](https://www.orbbec.com.cn/index/Product/info.html?cate=38&id=51)
-   [Orbbec 开发资料总链接](https://www.orbbec.com.cn/index/Download2025/info.html?cate=121&id=1)
-   [Orbbec SDK v2](https://github.com/orbbec/OrbbecSDK_v2)
-   [Orbbec SDK v2 API 文档](https://orbbec.github.io/docs/OrbbecSDKv2_API_User_Guide/)
-   [pyorbbecsdk 仓库](https://github.com/orbbec/pyorbbecsdk)
-   [pyorbbecsdk 文档](https://orbbec.github.io/pyorbbecsdk/index.html)
-   [Orbbec ROS2 Wrapper](https://github.com/orbbec/OrbbecSDK_ROS2/tree/v2-main)