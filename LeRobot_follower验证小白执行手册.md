# LeRobot follower 验证小白执行手册

这份文档只做一件事：验证 reBot Arm B601-DM follower 能不能被 LeRobot 识别、连接和校准。

当前推荐主路径：

- WSL Ubuntu 里运行 LeRobot。
- 用 Hugging Face LeRobot 主线仓库。
- 用 Seeed 外置 follower 适配器：`lerobot-robot-seeed-b601`。
- follower 类型名用：`seeed_b601_dm_follower`。

这一步暂时不需要：

- 不需要 reBot 102 leader。
- 不需要 SO-101 leader。
- 不需要摄像头。
- 不训练模型。
- 不采集数据。

成功标准很简单：

1. LeRobot 命令能看到 `seeed_b601_dm_follower`。
2. WSL 能看到达妙 USB-CAN 串口，例如 `/dev/ttyACM0`。
3. `lerobot-calibrate` 能跑完 follower 校准。
4. 校准文件能写到 `~/.cache/huggingface/lerobot/calibration/robots/`。

## 当前本机进度（2026-05-29）

这台机器已经完成 follower 基础验证：

- LeRobot conda 环境已装好：`lerobot 0.5.2`。
- Seeed B601 follower 适配器已装好：`lerobot_robot_seeed_b601 0.1.2`。
- LeRobot 环境里的 `motorbridge` 是 `0.3.7`，这是本次 follower 校准和键盘 jog 实测版本。
- WSL 串口使用 `/dev/ttyACM0`。
- 总线扫描已扫到 7 个电机：`0x01..0x07`，反馈 ID 是 `0x11..0x17`。
- follower 校准已完成，校准文件在：

```bash
~/.cache/huggingface/lerobot/calibration/robots/seeed_b601_dm_follower/follower1.json
```

- 校准后只读位置检查，7 个关节都在 `0 deg` 附近。
- 官方 `--teleop.type=keyboard` 不适合直接拿来做 B601 关节 jog，本仓已加本地工具：

```bash
python tools/lerobot_b601_keyboard_jog.py --port /dev/ttyACM0
```

默认每按一次动 `1` 度。

---

## 0. 先看懂两个终端

Windows PowerShell 长这样：

```powershell
PS D:\Robot\reBot-DevArm>
```

WSL Ubuntu 终端长这样：

```bash
pc@xxx:~$
```

文档里：

- 标了 `powershell` 的命令，在 Windows PowerShell 里执行。
- 标了 `bash` 的命令，在 WSL Ubuntu 里执行。
- 不要把 PowerShell 命令粘到 WSL，也不要把 WSL 命令粘到 PowerShell。

---

## 1. 开跑前检查

先确认这些事已经完成：

- 7 个电机 ID 已经烧录：`0x01` 到 `0x07`。
- 7 个关节零点已经设置。
- MotorBridge Web UI 已经能控制整机。
- 普通重力补偿 `9_gravity_compensation.py` 已经能跑。
- 带锁重力补偿 `10_gravity_compensation_lock.py` 已经能跑。
- 24V 电源、USB-CAN、CAN 总线都接好。
- 机械臂活动范围内没有手、线、工具、杯子等东西。

LeRobot follower 验证会占用串口，所以先关掉 Web UI gateway。

Windows PowerShell：

```powershell
Get-Process ws_gateway,motorbridge-gateway -ErrorAction SilentlyContinue
```

如果有输出，关掉它：

```powershell
Get-Process ws_gateway,motorbridge-gateway -ErrorAction SilentlyContinue | Stop-Process
```

---

## 2. 第一次安装 LeRobot 环境

这一节只需要做一次。

### 2.1 进入 WSL

Windows PowerShell：

```powershell
wsl
```

进入后提示符应该变成类似：

```bash
pc@xxx:~$
```

### 2.2 安装基础工具

WSL：

```bash
sudo apt update
sudo apt install -y git wget
```

### 2.3 检查有没有 conda

WSL：

```bash
conda --version
```

如果能看到版本号，跳到 2.4。

如果提示 `conda: command not found`，用国内镜像安装 Miniforge：

```bash
cd ~
rm -f Miniforge3-Linux-x86_64.sh
wget -O Miniforge3-Linux-x86_64.sh https://mirror.zju.edu.cn/miniforge/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh
~/miniforge3/bin/conda init bash
exec bash
```

安装过程中：

- 看到 license 时可以按空格翻页。
- 问是否接受 license，输入 `yes`。
- 安装路径默认即可，直接按 Enter。
- 问是否初始化 conda，输入 `yes`。

如果浙大镜像临时不可用，再试 GitHub 官方链接：

```bash
cd ~
rm -f Miniforge3-Linux-x86_64.sh
wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-Linux-x86_64.sh
~/miniforge3/bin/conda init bash
exec bash
```

### 2.4 创建 LeRobot 专用环境

WSL：

```bash
conda create -y -n lerobot python=3.12
conda activate lerobot
conda install -y -c conda-forge ffmpeg evdev
python -V
```

期望看到 Python 3.12。

注意：

- 这个环境叫 `lerobot`。
- 它和你跑重力补偿用的 Python 环境分开。
- 以后每次跑 LeRobot，都要先 `conda activate lerobot`。

### 2.5 创建探索区

WSL：

```bash
cd /mnt/d/Robot/reBot-DevArm
mkdir -p _lerobot_experiment
cd _lerobot_experiment
```

这个目录已经在 `.gitignore` 里，不会进主仓库。

### 2.6 clone LeRobot 主线和 Seeed follower 适配器

WSL：

```bash
cd /mnt/d/Robot/reBot-DevArm/_lerobot_experiment
git clone https://github.com/huggingface/lerobot.git
git clone https://github.com/Seeed-Projects/lerobot-robot-seeed-b601.git
```

如果以后目录已经存在，不要重复 clone，用更新命令：

```bash
cd /mnt/d/Robot/reBot-DevArm/_lerobot_experiment
git -C lerobot pull --ff-only
git -C lerobot-robot-seeed-b601 pull --ff-only
```

### 2.7 安装 Python 包

WSL：

```bash
conda activate lerobot
cd /mnt/d/Robot/reBot-DevArm/_lerobot_experiment

python -m pip install -U pip setuptools wheel

cd lerobot
pip install -e ".[core_scripts]"

cd ..
pip install --upgrade motorbridge==0.3.7
pip install -e ./lerobot-robot-seeed-b601
```

这一步可能下载很多包，等它跑完。

---

## 3. 验证软件安装是否成功

WSL：

```bash
conda activate lerobot
cd /mnt/d/Robot/reBot-DevArm/_lerobot_experiment
```

检查 Python import：

```bash
python - <<'PY'
import importlib.metadata as m
import lerobot
import motorbridge
import lerobot_robot_seeed_b601

print("LeRobot import OK")
print("MotorBridge", m.version("motorbridge"))
print("Seeed B601 follower adapter import OK")
PY
```

检查命令行能不能看到 Seeed follower：

```bash
which lerobot-calibrate
lerobot-calibrate --help | grep -E "seeed_b601|SeeedB601"
lerobot-teleoperate --help | grep -E "seeed_b601|SeeedB601"
```

正常现象：

- `which lerobot-calibrate` 能显示一个路径。
- 后两条命令里能看到 `seeed_b601_dm_follower` 或 `SeeedB601DMFollowerConfig`。

如果看不到，先不要接机械臂，去看第 9 节排错。

---

## 4. 每次开机后：把 USB-CAN 转给 WSL

这一节每次重启电脑、拔插 USB-CAN 后都可能要做。

### 4.1 Windows 找 USB 设备 BUSID

Windows PowerShell：

```powershell
usbipd list
```

在 `Connected:` 下面找类似这些名字的设备：

- USB Serial
- USB-SERIAL CH340
- CP210x
- USB-CAN
- Damiao
- CDC

记下它前面的 `BUSID`，例如：

```text
2-1
```

下面命令里都把 `2-1` 换成你的真实 BUSID。

### 4.2 第一次 bind

第一次需要管理员 PowerShell：

```powershell
usbipd bind --busid 2-1
```

如果之前 bind 过，可以跳过。

### 4.3 attach 到 WSL

Windows PowerShell：

```powershell
usbipd attach --wsl --busid 2-1
```

确认状态：

```powershell
usbipd list
```

正常应该看到这个设备状态类似 `Attached`。

### 4.4 WSL 里确认串口

WSL：

```bash
ls -l /dev/ttyACM* /dev/ttyUSB*
```

常见结果：

```text
/dev/ttyACM0
```

给权限：

```bash
sudo chmod 666 /dev/ttyACM0
```

如果你的设备是 `/dev/ttyUSB0`，就执行：

```bash
sudo chmod 666 /dev/ttyUSB0
```

本手册后面默认用 `/dev/ttyACM0`。如果你实际是 `/dev/ttyUSB0`，把命令里的 `/dev/ttyACM0` 全部替换成 `/dev/ttyUSB0`。

---

## 5. 跑 follower 校准

### 5.0 先做总线只读扫描

在真正校准前，先确认 WSL + MotorBridge 能扫到电机。这一步不发运动命令。

WSL：

```bash
conda activate lerobot
python -m motorbridge.cli scan \
  --vendor damiao \
  --transport dm-serial \
  --serial-port /dev/ttyACM0 \
  --serial-baud 921600 \
  --model 4310 \
  --start-id 1 \
  --end-id 16 \
  --feedback-base 16 \
  --timeout-ms 200
```

正常应该至少扫到 `0x01..0x07` 里的电机。

如果输出全是：

```text
no reply
scan done: 0 motor(s) found
```

先不要跑校准，更不要跑键盘控制。优先检查：

- 24V 电源是否打开。
- CAN-H / CAN-L / GND 是否接到整机总线。
- USB-CAN 是否接在正确的 CAN 口。
- Windows Web UI gateway 是否真的关闭。
- USB-CAN 是否被 attach 到 WSL 后，Windows 端没有同时占用。
- 用 Windows Web UI 重新验证是否还能扫到 7 个电机。

只有扫描能看到电机后，才继续下面的校准。

### 5.1 摆好机械臂

先断开危险姿态，手扶机械臂，摆到校准零位：

- 用你之前装机/设零点时的收起姿态。
- 不要让大臂水平伸出去。
- 夹爪完全闭合。
- 机械臂保持稳定，不要晃。
- 手放在电源或急停位置附近。

如果不确定零位长什么样，先看官方 reBot B601-DM LeRobot 文档里的 zero position 图片。

### 5.2 执行校准命令

WSL：

```bash
conda activate lerobot
cd /mnt/d/Robot/reBot-DevArm/_lerobot_experiment

lerobot-calibrate \
  --robot.type=seeed_b601_dm_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=follower1 \
  --robot.can_adapter=damiao
```

运行过程中：

- 终端让你按 Enter，就保持机械臂不动再按 Enter。
- 如果机械臂明显乱动、下坠、反向猛拉，立刻 `Ctrl+C`，必要时断 24V。
- 不要在机械臂运动范围内伸手调整细节。

### 5.3 校准成功后检查文件

WSL：

```bash
find ~/.cache/huggingface/lerobot/calibration/robots -maxdepth 3 -type f | grep follower1
```

如果能看到和 `follower1` 有关的 JSON 文件，说明校准信息已经保存。

---

## 6. 验收清单

跑完第 5 节后，逐项打勾：

- [x] `lerobot-calibrate --help` 能看到 `seeed_b601_dm_follower`。
- [x] WSL 能看到 `/dev/ttyACM0`。
- [x] 已经执行过 `sudo chmod 666 /dev/ttyACM0`。
- [x] Web UI gateway 已经关闭。
- [x] `lerobot-calibrate` 没有报错退出。
- [x] `~/.cache/huggingface/lerobot/calibration/robots/` 下有 `follower1` 相关文件。

这 6 项都满足，就算 LeRobot follower 验证通过。

这一步通过以后，才进入下一阶段：

- 买/装 leader。
- 跑 leader 校准。
- 跑 leader 控 follower 的 `lerobot-teleoperate`。
- 加摄像头。
- 采集数据。

---

## 7. 每次以后怎么重新进入

Windows PowerShell：

```powershell
wsl
```

WSL：

```bash
conda activate lerobot
cd /mnt/d/Robot/reBot-DevArm/_lerobot_experiment
```

如果要接真机，再重复第 4 节 USB attach 和权限步骤。

---

## 8. 如果需要重新校准

不要一上来就乱删文件。先把旧校准文件备份。

WSL：

```bash
mkdir -p ~/.cache/huggingface/lerobot/calibration_backup
mv ~/.cache/huggingface/lerobot/calibration/robots \
   ~/.cache/huggingface/lerobot/calibration_backup/robots_$(date +%Y%m%d_%H%M%S)
```

然后重新跑第 5 节的 `lerobot-calibrate`。

如果提示 `No such file or directory`，说明本来就没有旧校准文件，可以直接重新校准。

---

## 9. 常见报错

### 9.1 `conda: command not found`

说明 Miniforge 没装好，回到第 2.3 重新安装。

### 9.2 `Could not open serial port '/dev/ttyACM0'`

常见原因：

- USB-CAN 没有 attach 到 WSL。
- 设备实际不是 `/dev/ttyACM0`，而是 `/dev/ttyUSB0`。
- 没有执行 `sudo chmod 666 /dev/ttyACM0`。
- Windows Web UI gateway 还占着串口。

排查：

```bash
ls -l /dev/ttyACM* /dev/ttyUSB*
```

Windows PowerShell：

```powershell
usbipd list
Get-Process ws_gateway,motorbridge-gateway -ErrorAction SilentlyContinue
```

### 9.3 `seeed_b601_dm_follower` 找不到

说明 Seeed follower 适配器没有装到当前 conda 环境。

WSL：

```bash
conda activate lerobot
cd /mnt/d/Robot/reBot-DevArm/_lerobot_experiment
pip install -e ./lerobot-robot-seeed-b601
lerobot-calibrate --help | grep -E "seeed_b601|SeeedB601"
```

### 9.4 `No module named motorbridge`

WSL：

```bash
conda activate lerobot
pip install --upgrade motorbridge==0.3.7
```

### 9.5 校准时机械臂动作不对

立刻处理：

- `Ctrl+C`
- 手扶住机械臂
- 必要时断 24V

不要反复硬试。优先检查：

- 7 个电机 ID 是否还是 `0x01..0x07`。
- 电机型号是否和默认配置一致：J1-J3 是 DM4340P，J4-J6 和夹爪是 DM4310。
- 机械臂零位是否和你之前设零点时一致。
- 是否误用了 RobStride 类型或官方内置类型。

---

## 10. 备用路径：Hugging Face 内置 reBot 支持

如果 Seeed 外置适配器长期装不上，可以改用 Hugging Face LeRobot 主线已经内置的 reBot 支持。

只在主路径失败时看这一节。

WSL：

```bash
conda activate lerobot
cd /mnt/d/Robot/reBot-DevArm/_lerobot_experiment/lerobot
pip install -e ".[rebot]"
```

校准命令改成：

```bash
lerobot-calibrate \
  --robot.type=rebot_b601_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=follower \
  --robot.can_adapter=damiao
```

注意区别：

| 路径 | follower 类型名 |
|---|---|
| Seeed 外置适配器 | `seeed_b601_dm_follower` |
| Hugging Face 内置支持 | `rebot_b601_follower` |

这两个不要混着用。先按主路径跑。

---

## 11. 下一步

本机 follower 验证已经通过。下一步才是遥操作：

1. 决定 leader 路线：reBot 102 或 SO-101。
2. 安装/校准 leader。
3. 跑 `lerobot-teleoperate`，让 leader 控 follower。
4. 再接摄像头。
5. 再做 `lerobot-record` 数据采集。

现在可以开始认真决策 leader 路线；摄像头和数据采集放在 leader 决策之后。

---

## 11.1 键盘小步进控制

官方 LeRobot 的 `--teleop.type=keyboard` 不是给 B601 这种 7 关节 follower 直接做关节 jog 的，直接套用会出现 action 字段不匹配。

本仓提供了一个更保守的本地脚本：

```bash
python tools/lerobot_b601_keyboard_jog.py --port /dev/ttyACM0
```

使用前必须满足：

- 第 5.0 节总线扫描能扫到电机。
- 第 5.2 节 follower 校准已经通过。
- 机械臂周围清空。
- 手放在电源或急停附近。

按键：

| 按键 | 关节 | 方向 |
|---|---|---|
| `1` / `q` | shoulder_pan | - / + |
| `2` / `w` | shoulder_lift | - / + |
| `3` / `e` | elbow_flex | - / + |
| `4` / `r` | wrist_flex | - / + |
| `5` / `t` | wrist_yaw | - / + |
| `6` / `y` | wrist_roll | - / + |
| `7` / `u` | gripper | - / + |
| `s` | 打印当前位置 | |
| `x` | 安全退出 | |

默认每次按键只动 `1` 度，并且启用了 `max_relative_target=2` 度的相对目标保护。

---

## 12. 资料来源

- Hugging Face LeRobot Installation：`https://huggingface.co/docs/lerobot/main/installation`
- Hugging Face LeRobot reBot B601-DM：`https://huggingface.co/docs/lerobot/main/rebot_b601`
- Seeed reBot Arm B601-DM 入门 LeRobot：`https://wiki.seeedstudio.com/cn/rebot_arm_b601_dm_lerobot/`
- PyPI `lerobot-robot-seeed-b601`：`https://pypi.org/project/lerobot-robot-seeed-b601/`

---

## 13. 2026-05-28 实操补充

这一节是按本机真实跑通过程补的，优先级高于前面没落地过的猜测性描述。

### 13.1 本机已验证的软件版本

在 `lerobot` conda 环境里，当前已验证：

- `lerobot 0.5.2`
- `motorbridge 0.3.7`
- `lerobot_robot_seeed_b601 0.1.2`

验证命令：

```bash
python - <<'PY'
import importlib.metadata as m
import lerobot
import motorbridge
import lerobot_robot_seeed_b601

print("LeRobot", m.version("lerobot"))
print("MotorBridge", m.version("motorbridge"))
print("Seeed B601 follower", m.version("lerobot_robot_seeed_b601"))
PY
```

### 13.2 安装时更稳的命令

本机实际安装时，用清华 PyPI 镜像更顺：

```bash
conda activate lerobot
cd /mnt/d/Robot/reBot-DevArm/_lerobot_experiment

conda install -y pip setuptools wheel

python -m pip install -U pip setuptools wheel -i https://pypi.tuna.tsinghua.edu.cn/simple

cd lerobot
pip install -e ".[core_scripts]" -i https://pypi.tuna.tsinghua.edu.cn/simple

cd ..
pip install --upgrade motorbridge==0.3.7 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -e ./lerobot-robot-seeed-b601 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

如果你已经在 `lerobot` 环境里，但 `python -m pip` 报：

```text
No module named pip
```

先执行：

```bash
conda install -y pip setuptools wheel
```

### 13.3 只读扫描的正常输出

本机在硬件链路正常时，下面命令能扫到 7 个电机：

```bash
python -m motorbridge.cli scan \
  --vendor damiao \
  --transport dm-serial \
  --serial-port /dev/ttyACM0 \
  --serial-baud 921600 \
  --model 4310 \
  --start-id 1 \
  --end-id 16 \
  --feedback-base 16 \
  --timeout-ms 200
```

正常输出类似：

```text
[hit] vendor=damiao probe=0x01 esc_id=0x1 mst_id=0x11
[hit] vendor=damiao probe=0x02 esc_id=0x2 mst_id=0x12
[hit] vendor=damiao probe=0x03 esc_id=0x3 mst_id=0x13
[hit] vendor=damiao probe=0x04 esc_id=0x4 mst_id=0x14
[hit] vendor=damiao probe=0x05 esc_id=0x5 mst_id=0x15
[hit] vendor=damiao probe=0x06 esc_id=0x6 mst_id=0x16
[hit] vendor=damiao probe=0x07 esc_id=0x7 mst_id=0x17
scan done: 7 motor(s) found
```

如果还是 `scan done: 0 motor(s) found`，先别往下做。

### 13.4 已有校准文件时会怎么提示

如果之前已经校准过 `follower1`，再跑：

```bash
lerobot-calibrate \
  --robot.type=seeed_b601_dm_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=follower1 \
  --robot.can_adapter=damiao
```

终端会先问：

```text
Press ENTER to use provided calibration file associated with the id follower1,
or type 'c' and press ENTER to run calibration:
```

含义：

- 直接按 `Enter`：继续用旧校准
- 输入 `c` 再按 `Enter`：重新校准，把当前姿态重写成新的零位

如果你这次就是要把“当前收起姿态”重新写成零位，就输入：

```text
c
```

然后再按一次 `Enter` 确认。

### 13.5 本机校准后的只读位置

本机重新校准后，用只读检查能看到 7 个关节都在零位附近，接近 `0 deg`：

```text
elbow_flex.pos: -0.01
gripper.pos: -0.01
shoulder_lift.pos: -0.01
shoulder_pan.pos: -0.01
wrist_flex.pos: -0.01
wrist_roll.pos: -0.01
wrist_yaw.pos: -0.01
```

只读检查命令：

```bash
python - <<'PY'
import lerobot_robot_seeed_b601
from lerobot.robots import make_robot_from_config
from lerobot_robot_seeed_b601 import SeeedB601DMFollowerConfig

cfg = SeeedB601DMFollowerConfig(
    port='/dev/ttyACM0',
    can_adapter='damiao',
    id='follower1',
    disable_torque_on_disconnect=True,
)
robot = make_robot_from_config(cfg)
robot.connect()
obs = robot.get_observation()
for key in sorted(k for k in obs if k.endswith('.pos')):
    print(f'{key}: {obs[key]:.2f}')
robot.disconnect()
PY
```

### 13.6 官方 `keyboard` 不适合 B601 关节 jog

本机已确认：LeRobot 官方的

```text
--teleop.type=keyboard
```

不是给 B601 这种 7 关节 follower 直接做关节 jog 的。它的 action 结构和 B601 关节控制不匹配，不建议直接硬套。

所以本仓改用本地脚本：

```bash
python tools/lerobot_b601_keyboard_jog.py --port /dev/ttyACM0
```

### 13.7 键盘 jog 的推荐起手顺序

默认每按一次动 `1` 度：

```bash
python tools/lerobot_b601_keyboard_jog.py --port /dev/ttyACM0
```

如果想更细一点，每按一次 `0.5` 度：

```bash
python tools/lerobot_b601_keyboard_jog.py --port /dev/ttyACM0 --step-deg 0.5
```

推荐第一次这样试：

1. 先启动脚本
2. 先按 `s`，只打印位置，不会动
3. 再试 `6` 或 `y`，先动 wrist_roll
4. 不要一上来就按 `2/w` 或 `3/e`
5. 退出按 `x`

### 13.8 串口被占用怎么处理

如果报：

```text
Device or resource busy
Unable to acquire exclusive lock on serial port
```

说明 `/dev/ttyACM0` 正被别的程序占用。

先查：

```bash
fuser /dev/ttyACM0
ps -ef | grep -E 'lerobot|motorbridge|keyboard_jog|python' | grep -v grep
```

本机真实遇到过的情况是：

```text
python tools/lerobot_b601_keyboard_jog.py --port /dev/ttyACM0 --step-deg 0.5
```

还在跑，导致后面的扫描/校准打不开串口。

如果就是 jog 脚本没退，优先回到那个终端按：

```text
x
```

让它安全退出。
