# Orbbec Gemini 2 + YOLO 视觉抓取 Demo 上手指南

> 给自己看的执行笔记。**用 Orbbec Gemini 2 深度相机 + YOLO 跑通官方 reBot Arm B601-DM 桌面视觉抓取 Demo**，从相机点亮 → 装环境 → 手眼标定 → 抓取调试。
> 建立时间：2026-06-11
> 触发：Gemini 2 已到货（¥1750，2026-06-07 下单），用户确定走**官方 YOLO 抓取 demo**（深度相机的主用途；LeRobot 主线只用 RGB，见 [`遥操作与LeRobot待办.md`](./遥操作与LeRobot待办.md) §3.9）。
>
> 官方依据：仓内 [`software/wiki_docs/reBot_Arm_B601-DM_Visual_Grasping_Demo/reBot_Arm_B601-DM_视觉夹取_Demo.md`](./software/wiki_docs/reBot_Arm_B601-DM_Visual_Grasping_Demo/reBot_Arm_B601-DM_视觉夹取_Demo.md)（Seeed 官方 wiki 离线版）。本指南 = 官方流程 + 本机（WSL2）适配 + 坑。

**符号约定**：🟢 已确认 / 🟡 待实操 / ⚠️ 坑 / ❓ 未知

---

## 0. 全景路线（4 步）

```
① 点亮相机（Windows，Orbbec Viewer，不写代码）
        ↓
② 装环境（Linux/WSL：grasp 仓 + conda + pyorbbecsdk + 机械臂 SDK）
        ↓
③ Eye-in-Hand 手眼标定（打印 ArUco + 跑标定脚本 → hand_eye.npz）
        ↓
④ 跑抓取（先 object_detection 测相机/YOLO → grasp_pipeline 测姿态 → main.py --dry-run → 真抓）
```

🟢 **前提已满足**：B601-DM 已装机/烧 ID/零点/重力补偿验证通过（手动标定模式正好用重力补偿）。

---

## 1. ⚠️ 先准备好这几样（不齐活下面会卡）

| 要准备 | 说明 | 状态 |
|---|---|---|
| **ArUco 标记（10cm）** | 手眼标定用，`config/default.yaml` 默认 `marker_length_m: 0.1`（=10cm）。需生成 + **打印到准确尺寸**（打印别缩放！量一下实际边长，对不上就改 yaml） | 🟡 待打印 |
| **grasp demo 仓** | 独立仓 `github.com/Seeed-Projects/reBot-DevArm-Grasp`（≠ 本仓），步骤1 clone | 🟡 待 clone |
| **跑在哪台 Linux** | demo 要 Ubuntu 22.04+。你是 WSL2 → 见 §2 的 ⚠️ USB 转发问题，可能要权衡原生 Ubuntu | ❓ 待决策 |
| **USB 3.0 口 + 自带 USB-C 线** | 相机 USB 供电+数据，必须 3.0 蓝口 | 🟢 有 |
| **打印 Gemini2 腕部支架** | `hardware/reBot_B601_DM/3D_Printed_Parts/D435_Gemini2_Mount.step`，eye-in-hand 装 wrist_roll | 🟡 待打印装 |

---

## 2. 步骤①：点亮相机（Windows，先确认硬件好）

1. USB-C 插电脑 **USB 3.0** 口（Gemini 2 USB 供电，无单独电源）。
2. 下 **Orbbec Viewer**（Orbbec GitHub releases），打开 → 确认认到设备 → 点 **Color** / **Depth** 看两路画面。
3. 出画面 = 相机 OK。认不到：换线/换 3.0 口/重插。

> ✅ 这步在 Windows 原生做最省事，纯验证硬件。**跟后面跑 demo 的 Linux 环境无关**。

### ⚠️ WSL2 用户的关键岔路（USB 透传）
demo 跑在 Linux。你之前重力补偿是 WSL2 + `usbipd-win` 把 USB-CAN 转发进 WSL。现在抓取要 **同时转发两个 USB 设备**：USB-CAN（控臂）+ Gemini 2（USB 3.0 相机）。
- ❓ **未知风险**：USB 3.0 深度相机过 usbipd-win 进 WSL2，带宽/帧率/稳定性可能掉，社区有踩坑。
- 🟡 **备选**：装个**原生 Ubuntu 22.04**（双系统/U盘/旧机）跑 demo，相机和 CAN 都直连，最省心。
- 🟡 **先试 WSL**：`usbipd list` → `usbipd attach --wsl --busid <相机的>`，跑 §4 `object_detection.py` 看相机在 WSL 里出不出图，不行再上原生。

---

## 3. 步骤②：装环境（Linux/WSL，conda）

> 照官方 demo doc 步骤 1-6（仓内 `视觉夹取_Demo.md`）。下面是命令 + 本地注意。

```bash
# 1. clone demo 仓（独立仓，不是本仓）
git clone https://github.com/Seeed-Projects/reBot-DevArm-Grasp.git rebot_grasp
cd rebot_grasp

# 2. conda 环境（独立，别跟 lerobot env 混）
conda create -n rebotarm python=3.10 -y && conda activate rebotarm

# 3. 项目依赖
pip install -r requirements.txt

# 4. 机械臂 SDK（demo 克隆 vectorBH6 main 到 sdk/）
git clone https://github.com/vectorBH6/reBotArm_control_py.git sdk/reBotArm_control_py
cd sdk/reBotArm_control_py && pip install -e . && cd ../..

# 5. Orbbec SDK（pyorbbecsdk，要编译）
sudo apt-get update && sudo apt-get install -y cmake build-essential libusb-1.0-0-dev
cd sdk && git clone https://github.com/orbbec/pyorbbecsdk.git   # 国内慢用 gitee.com/orbbecdeveloper/pyorbbecsdk
cd pyorbbecsdk && pip install -e .
sudo bash scripts/install_udev_rules.sh && sudo udevadm control --reload-rules && sudo udevadm trigger
cd ../..

# 6. 验证
python -c "import pyorbbecsdk; print('pyorbbecsdk OK')"
python -c "import motorbridge; print('motorbridge OK')"
```

**本地注意**：
- 🟢 **`reBotArm_control_py` 版本一致性**：demo 克隆 vectorBH6 **main**（含 `idx_q` 关节限位修复）；本仓 submodule 的 fork develop 我 2026-06-11 也 cherry-pick 了同一修复（见操作日志），两边一致，IK 限位都对。
- ⚠️ `motorbridge` 这个 conda env 要单独装（`pip install -U motorbridge`）；别假设跟 WSL 系统 python / lerobot env 共用。
- ⚠️ 权限：`sudo chmod a+rw /dev/bus/usb/*/*`（相机）+ `sudo chmod 666 /dev/ttyUSB0`（CAN）。
- 🟡 **是否 fork demo 仓进 submodule**：按复刻基线原则，先 clone 探索跑通，再决定 fork（同 LeRobot 探索区做法），暂不进主仓 submodule。

---

## 4. 步骤③：手眼标定（Eye-in-Hand）

```bash
# 自动模式：臂自动遍历 50 个预设姿态，检测到 ArUco 稳定后自动采样
python scripts/collect_handeye_eih.py
# 手动模式：臂进重力补偿，手推末端到合适视角按 Enter 采，c/q 结束
python scripts/collect_handeye_eih.py --manual
```
- 先在 `config/default.yaml` 确认 `calibration.aruco.marker_length_m` 跟你打印的 ArUco 实测边长一致。
- 样本：最少 5，建议 ≥15。中途 `c`/`q` 也会用已采样本算结果。
- 结果存 `config/calibration/orbbec_gemini2/hand_eye.npz`。
- 🟢 **手动模式用重力补偿**——你已验证过 B601 重力补偿能跑，正好用上。

---

## 5. 步骤④：跑 + 调试（三段递进）

```bash
# 1) 只测相机 + YOLO（不连臂）：确认相机能开、模型加载、检测正常
python scripts/object_detection.py
# 2) 只测抓取姿态估计（不连臂）：看 OBB 短轴/抓取点是否合理
python scripts/ordinary_grasp_pipeline.py
# 3) 主抓取程序：先 dry-run 验证位姿/工作空间，再真抓
python scripts/main.py --dry-run
python scripts/main.py
```
- YOLO 模型 `yoloe-26l-seg.pt`（开放词汇分割），`config/default.yaml` 改 `custom_classes`（如 "cup"/"water bottle"）。device 默认 cpu。
- 运行键：`G` 抓当前最佳目标 / `R` 恢复预览 / `Q`/`Esc` 退出。
- 预备位/抓取参数在 `config/default.yaml`（`robot.ready_pose`、`grasp_pipeline`）。

---

## 6. 坑 + FAQ（官方 + 预判）

| 现象 | 原因 / 解决 |
|---|---|
| `No module named 'motorbridge'` | conda env 没装 SDK：`pip install -r requirements.txt` + `cd sdk/reBotArm_control_py && pip install -e .` |
| 按 `G` 不抓 | `hand_eye.npz` 不存在 / 标定模式不是 eye_in_hand / 目标 IK 不可达 → 先 `--dry-run` |
| 抓取点深度不稳 | 调 `grasp.depth_quantile` / 相机高度 / 目标别太反光 |
| 相机打不开（Linux） | 没装 udev 规则 → 跑 `install_udev_rules.sh` |
| ❓ WSL 里相机没图 | usbipd 透传 USB3.0 带宽问题 → 试原生 Ubuntu |

---

## 7. 待办 / 未知 🟡

| 优先级 | 事项 |
|---|---|
| ⭐高 | 决定跑在 **WSL2（usbipd 双设备透传）还是原生 Ubuntu**——先 §4 `object_detection.py` 在 WSL 测相机出图 |
| ⭐高 | 打印 10cm ArUco（尺寸要准）+ 打印装 `D435_Gemini2_Mount.step` 腕部支架 |
| 中 | demo 仓 `reBot-DevArm-Grasp` 跑通后是否 fork 进 submodule（复刻基线原则） |
| 中 | conda env `rebotarm` 里 motorbridge 装哪个版本（跟主仓 baseline 0.4.5 对齐？） |
| 低 | YOLO 跑 cpu 够不够快，要不要上 GPU |

---

## 8. 参考链接

- 仓内：[`reBot_Arm_B601-DM_视觉夹取_Demo.md`](./software/wiki_docs/reBot_Arm_B601-DM_Visual_Grasping_Demo/reBot_Arm_B601-DM_视觉夹取_Demo.md)（官方教程离线版）
- demo 仓：[Seeed-Projects/reBot-DevArm-Grasp](https://github.com/Seeed-Projects/reBot-DevArm-Grasp)（[EclipseaHime017 镜像](https://github.com/EclipseaHime017/reBot-DevArm-Grasp)）
- [Orbbec Gemini 2 产品页](https://www.orbbec.com/products/stereo-vision-camera/gemini-2/) / [Seeed Wiki Gemini2](https://wiki.seeedstudio.com/orbbec_gemini2/)
- [pyorbbecsdk 仓库](https://github.com/orbbec/pyorbbecsdk) / [文档](https://orbbec.github.io/pyorbbecsdk/index.html)
- [Orbbec SDK v2](https://github.com/orbbec/OrbbecSDK_v2) / [ROS2 Wrapper](https://github.com/orbbec/OrbbecSDK_ROS2/tree/v2-main)
- 相关：[`遥操作与LeRobot待办.md`](./遥操作与LeRobot待办.md) §3.9 摄像头选型 / [`装机烧录指南.md`](./装机烧录指南.md) §6.4 WSL+usbipd 流程
