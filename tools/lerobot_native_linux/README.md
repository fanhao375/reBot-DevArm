# 原生 Ubuntu 遥操作（Arm102 LD → B601-DM）

2026-06-19/20 从 WSL 迁到**原生 Ubuntu** 跑通的一套。原生 Linux 串口直连,
不需要 usbipd——彻底解决了 WSL 下官方 `lerobot-teleoperate` 卡 2Hz +
`request_feedback timeout` 的老问题。当前状态:**官方 teleoperate 60Hz,全 7 轴跟手。**

完整小白流程见上级目录 [`../../LeRobot_Arm102LD_B601DM遥操作小白执行手册.md`](../../LeRobot_Arm102LD_B601DM遥操作小白执行手册.md)。
这里只放原生 Linux 专属的补丁和启动脚本。

## 环境（一次性）

- conda 环境 `lerobot`(miniforge,Python 3.10),Seeed 三仓克隆在 `~/rebot_lerobot/`
- **CPU 版 torch/torchvision**(本机有 RTX A2000 但无驱动,遥操作不需要 GPU):
  `torch==2.7.1` / `torchvision==0.22.1` 从 `https://download.pytorch.org/whl/cpu` 装
- 关键 pip 坑:**走代理(127.0.0.1:7897)+ 官方 PyPI 最稳**,直连清华会被 USB-WiFi 抽风掉线;
  适配器要 `--no-deps` 装(否则 `lerobot>=0.4` 会把 torch 拽升到 2.10 CUDA 915MB)。
  详见记忆 `project-native-linux-lerobot-env`。

## 两个本地补丁（重装后必须重打）

补丁文件在 `patches/`,改的是 `~/rebot_lerobot` 里的 Seeed 适配器(不在本仓 git,重装会丢)。
**重装环境后跑一次即可幂等恢复:**

```bash
conda activate lerobot
python tools/lerobot_native_linux/apply_patches.py
```

| 补丁 | 文件 | 解决什么 |
|------|------|---------|
| 1. 取反 2/3 轴 | `rebot_arm_102_leader.py` `get_action` | 102 的 shoulder_lift/elbow_flex 物理装反,默认映射把它们裁到 ~0("不动")。解缠后取反 → 全轴跟手 |
| 2. 量程对称 | `config_rebot_arm_102_leader.py` `joint_ranges` | 默认 `(-200,1)`/`(-1,170)` 让解缠窗口(=中点±180)落在 ~80°,过 90° 角度 ±360 翻转 → 从臂猛跳回 0。改 `(-200,200)`/`(-170,170)` 把窗口移到 ±180,活动范围内永不翻转 |

> ⚠️ **曾有第 3 个补丁 `max_relative_target=12`(限速安全网),2026-06-25 已撤销。** 原因:
> 那条代码路径**每帧要读 7 个电机状态 + 把目标钳制在"当前±12°"**,导致**从臂明显延时**。
> 而"过 90°猛跳"的根因已被补丁 2 在源头修掉,这个安全网就不需要了 ——
> **保持上游默认 `None`**(不钳制、不每帧读状态),延时明显改善。`apply_patches.py` 已移除该补丁。

## 启动遥操作

```bash
# 1) 两臂插 USB 上电；2) 串口授权（每次开机/拔插后）:
sudo chmod 666 /dev/ttyUSB0 /dev/ttyACM0
# 3) 启动:
bash tools/lerobot_native_linux/start_teleop.sh
```

- `/dev/ttyUSB0` = 102 leader(CH340);`/dev/ttyACM0` = B601 follower(达妙桥)
- `ttyUSB0` 不出现 → brltty 抢占,`sudo apt remove -y brltty` 后重插
- 校准文件(全新机器需重建):`lerobot-calibrate` 见小白手册第 8/9 节

## 已知遗留（非故障）

- 2/3 大臂(4340P)在**满伸展高负载点力矩很高(~18)**,这是真实重力负载,
  电机一直使能、不掉力、不跳。若要再降负载/抖动,方向是**重力补偿/MIT 模式**
  (本仓 `software/reBotArm_control_py` 有重力补偿例程),属另一条线。
