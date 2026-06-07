# LeRobot：Arm102 LD 主臂控制 reBot Arm B601-DM 小白执行手册

这份文档只讲你现在这套硬件：

- **Leader 主臂**：华馨京 / FashionStar `Arm102 LD`，也叫 `StarArm102` / `reBot Arm 102 leader`
- **Follower 从臂**：`reBot Arm B601-DM`，达妙电机版本
- **运行环境**：Windows 工作站 + WSL Ubuntu + LeRobot conda 环境

目标很清楚：

1. 让 WSL 同时看到两个 USB 串口：leader 和 follower。
2. 确认 LeRobot 环境能识别 B601 follower 和 Arm102 leader。
3. 校准 Arm102 leader。
4. 运行 `lerobot-teleoperate`，用 Arm102 LD 控制 B601-DM。
5. 成功后再考虑摄像头、数据采集和训练。

---

## 0. 先看结论

你之前已经完成：

- B601-DM Web UI 控制。
- B601-DM 重力补偿。
- B601-DM 重力补偿锁止。
- LeRobot follower 基础验证。
- B601-DM follower 校准文件已有：`follower1`。

现在新增的是：

- 接入 Arm102 LD 主臂。
- 校准 leader。
- 用 leader 遥操作 follower。

---

## 1. 两套命名别搞混

现在官方资料里有两套命名，容易把人绕晕。

### 本机推荐路径

这是按你当前电脑里已经装好的环境来写的。

```text
follower: seeed_b601_dm_follower
leader:   rebot_102_leader
```

原因：

- `seeed_b601_dm_follower` 已经在你这台机器上完成 follower 校准。
- 当前 `lerobot-calibrate --help` / `lerobot-teleoperate --help` 已经能看到 `rebot_102_leader`。
- 不需要为了主臂再重装一套 Seeed 外置 leader 包。

### 另一套 Seeed wiki 命名

```text
follower: seeed_b601_dm_follower
leader:   rebot_arm_102_leader
```

这套写法来自 Seeed 的部分入门文档和独立 leader 包：

```text
lerobot-teleoperator-rebot-arm-102
```

如果你本机找不到 `rebot_102_leader`，再考虑这套备用路径。

### Hugging Face 主线完整内置路径

```text
follower: rebot_b601_follower
leader:   rebot_102_leader
```

这条路径会重新用 Hugging Face 内置 B601 follower 配置，校准文件目录也会变。你现在已经有 `seeed_b601_dm_follower/follower1.json`，所以本文不默认切过去。

### 本文实际使用

```text
follower: seeed_b601_dm_follower
leader:   rebot_102_leader
```

---

## 2. 每次开跑前安全检查

先确认：

- B601-DM 24V 已接好。
- Arm102 LD 供电/USB 已接好。
- B601-DM 和 Arm102 周围没有手、线缆、工具、杯子。
- Web UI gateway 已关闭。
- 重力补偿脚本没有在跑。
- 机械臂出问题时，你能立刻按 `Ctrl+C` 或断电。

Windows PowerShell 里先杀掉可能占串口的 gateway：

```powershell
Get-Process ws_gateway,motorbridge-gateway -ErrorAction SilentlyContinue | Stop-Process
```

如果没有输出，不是错误，表示本来就没开。

---

## 3. Windows 端：把两个 USB 设备转发给 WSL

这一步在 **Windows PowerShell** 里执行，不是在 WSL 里执行。

先看设备：

```powershell
usbipd list
```

你应该看到至少两个和机器人有关的 USB 串口设备：

```text
BUSID  VID:PID    DEVICE                         STATE
1-5    2e88:4603  USB 串行设备 (COM8)             Not shared / Shared / Attached
1-7    xxxx:xxxx  USB-SERIAL / CH340 / CP210x     Not shared / Shared / Attached
```

一般判断：

- B601-DM 达妙串口桥：Windows 里常见为 `USB 串行设备 (COM8)`，WSL 里常变成 `/dev/ttyACM0`。
- Arm102 LD 主臂 USB-UART：Windows 里常见为 `CH340` / `CP210x` / `USB-SERIAL`，WSL 里常变成 `/dev/ttyUSB0`。

把两个 BUSID 都 bind + attach。下面用例子写，实际替换成你的 BUSID。

```powershell
usbipd bind --busid 1-5
usbipd attach --wsl --busid 1-5

usbipd bind --busid 1-7
usbipd attach --wsl --busid 1-7
```

再检查：

```powershell
usbipd list
```

两个机器人相关设备都应该是：

```text
Attached
```

如果 attach 后 Windows COM 口消失，这是正常现象。设备已经交给 WSL 了。

---

## 4. 进入 WSL

Windows PowerShell：

```powershell
wsl -d Ubuntu-22.04
```

进去后提示符类似：

```bash
pc@DESKTOP-xxxx:/mnt/d/Robot/reBot-DevArm$
```

注意：

- `wsl -d Ubuntu-22.04` 是 Windows 命令。
- 进入 WSL 后不要再输入 `wsl -d Ubuntu-22.04`。

---

## 5. WSL 端：确认两个串口

在 WSL 里执行：

```bash
lsusb
ls -l /dev/ttyACM* /dev/ttyUSB*
```

目标是看到：

```text
/dev/ttyACM0    # B601-DM follower
/dev/ttyUSB0    # Arm102 LD leader
```

给权限：

```bash
sudo chmod 666 /dev/ttyACM* /dev/ttyUSB*
```

如果 `sudo` 密码不记得，别在这里硬试三次。可以回 Windows PowerShell 让我用下面这种方式代跑：

```powershell
wsl -d Ubuntu-22.04 -u root -- chmod 666 /dev/ttyACM0 /dev/ttyUSB0
```

如果 `/dev/ttyUSB0` 不出现：

```bash
sudo modprobe usbserial
sudo modprobe ch341
sudo modprobe cp210x
dmesg | grep -E "ttyUSB|ch341|cp210|usbserial" | tail -n 30
```

如果提示 `brltty` 占用串口：

```bash
sudo apt remove brltty
```

---

## 6. 激活 LeRobot 环境

WSL：

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
```

确认版本：

```bash
python -m pip show lerobot
python -m pip show lerobot-robot-seeed-b601
python -m pip show motorbridge
```

本机之前已验证的状态应该类似：

```text
lerobot 0.5.2
lerobot_robot_seeed_b601 0.1.2
motorbridge 0.3.7
```

---

## 7. 检查 Arm102 leader 支持

WSL：

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
lerobot-calibrate --help | grep -E "rebot_102|102"
lerobot-teleoperate --help | grep -E "rebot_102|102"
```

你要看到：

```text
rebot_102_leader
```

如果能看到，跳到第 8 节。

如果看不到，先安装 Hugging Face LeRobot 的 reBot extra：

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
cd /mnt/d/Robot/reBot-DevArm/_lerobot_experiment
cd lerobot
python -m pip install -e ".[rebot]"
```

再确认：

```bash
lerobot-calibrate --help | grep -E "rebot_102|102"
```

如果你明确想用 Seeed 外置包的 `rebot_arm_102_leader`，备用安装方式是：

```bash
cd /mnt/d/Robot/reBot-DevArm/_lerobot_experiment
git clone https://github.com/Seeed-Projects/lerobot-teleoperator-rebot-arm-102.git
python -m pip install -e ./lerobot-teleoperator-rebot-arm-102
```

但本文主命令仍然用本机已识别的：

```text
rebot_102_leader
```

---

## 8. 确认 follower 校准还在

你之前已经完成 follower 校准，先确认文件还在：

```bash
find ~/.cache/huggingface/lerobot/calibration/robots -maxdepth 4 -type f | grep -E "seeed_b601|follower1"
```

期望看到类似：

```text
.../seeed_b601_dm_follower/follower1.json
```

如果没有，重新校准 follower：

```bash
lerobot-calibrate \
  --robot.type=seeed_b601_dm_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=follower1 \
  --robot.can_adapter=damiao
```

校准时把 B601-DM 摆到官方零位，夹爪闭合，然后按提示操作。

---

## 9. 校准 Arm102 LD leader

这是最关键步骤。

校准开始时，Arm102 的每个舵机会把**当前位置当作零点**。所以姿态必须摆对。

校准前：

- 把 Arm102 LD 摆到官方零位图对应姿态。
- 夹爪闭合。
- 手不要一直推着关节。
- 校准时尽量保持静止。

```bash
lerobot-calibrate \
  --teleop.type=rebot_102_leader \
  --teleop.port=/dev/ttyUSB0 \
  --teleop.id=leader
```

校准完成后检查校准文件：

```bash
find ~/.cache/huggingface/lerobot/calibration/teleoperators -maxdepth 4 -type f | grep -E "102|leader"
```

---

## 10. 先只读 leader 角度

正式遥操作前，先确认 Arm102 读数正常。

如果你安装了 Seeed 外置包，可能有示例：

```bash
cd /mnt/d/Robot/reBot-DevArm/_lerobot_experiment
python ./lerobot-teleoperator-rebot-arm-102/examples/read_raw_angles.py --port /dev/ttyUSB0
```

期望现象：

- 终端连续打印各关节角度。
- 你轻轻动 Arm102，数字跟着变化。
- 在零位附近，各关节接近 `0`。

如果没有这个示例文件，跳过这步，直接进入第 11 节，但第一次遥操作时动作要更慢。`rebot_102_leader` 本身会在校准/遥操作时读取 leader 角度。

---

## 11. 正式遥操作：Arm102 LD 控 B601-DM

先摆好：

- B601-DM 在安全姿态，别贴桌面、别贴墙。
- Arm102 LD 在零位附近。
- 人站在旁边，准备 `Ctrl+C`。
- 如果 B601-DM 乱动，马上 `Ctrl+C` 或断 24V。

### 11.1 本机推荐命令

```bash
lerobot-teleoperate \
  --robot.type=seeed_b601_dm_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=follower1 \
  --robot.can_adapter=damiao \
  --teleop.type=rebot_102_leader \
  --teleop.port=/dev/ttyUSB0 \
  --teleop.id=leader \
  --teleop.joint_directions='{"shoulder_pan":-1,"shoulder_lift":-1,"elbow_flex":1,"wrist_flex":1,"wrist_yaw":1,"wrist_roll":-1,"gripper":-6}'
```

正常现象：

- 程序连接 follower。
- 程序连接 leader。
- 动 Arm102，B601-DM 跟着动。
- 夹爪也跟着开合。

停止：

```text
Ctrl+C
```

### 11.2 如果你已安装 Seeed 外置包并想用 `rebot_arm_102_leader`

```bash
lerobot-teleoperate \
  --robot.type=seeed_b601_dm_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=follower1 \
  --robot.can_adapter=damiao \
  --teleop.type=rebot_arm_102_leader \
  --teleop.port=/dev/ttyUSB0 \
  --teleop.id=rebot_arm_102_leader \
  --teleop.joint_directions='{"shoulder_pan":-1,"shoulder_lift":-1,"elbow_flex":1,"wrist_flex":1,"wrist_yaw":1,"wrist_roll":-1,"gripper":-4}'
```

---

## 12. 如果某个关节方向反了

不要立刻重新校准。

先改 `joint_directions`。

例如 `wrist_roll` 反了，把：

```json
"wrist_roll": -1
```

改成：

```json
"wrist_roll": 1
```

如果夹爪开合太大或太小，改 `gripper` 的数值：

```json
"gripper": -4
```

可试：

```json
"gripper": -3
"gripper": -5
"gripper": -6
```

经验：

- 方向反了，改正负号。
- 幅度不合适，改绝对值大小。
- 零位错了，才重新校准。

---

## 13. 常见问题

### 13.1 `wsl: command not found`

你在 WSL 里输入了 Windows 命令。

正确做法：

- `wsl -d Ubuntu-22.04` 在 Windows PowerShell 里执行。
- 进入 WSL 后，不要再输入 `wsl`。

### 13.2 `/dev/ttyACM0` 不存在

B601-DM 没 attach 到 WSL。

回 Windows PowerShell：

```powershell
usbipd list
usbipd attach --wsl --busid B601的BUSID
```

WSL：

```bash
ls -l /dev/ttyACM*
sudo chmod 666 /dev/ttyACM*
```

### 13.3 `/dev/ttyUSB0` 不存在

Arm102 LD 没 attach 到 WSL，或者 USB-UART 驱动没加载。

Windows PowerShell：

```powershell
usbipd list
usbipd attach --wsl --busid Arm102的BUSID
```

WSL：

```bash
sudo modprobe usbserial
sudo modprobe ch341
sudo modprobe cp210x
ls -l /dev/ttyUSB*
sudo chmod 666 /dev/ttyUSB*
```

### 13.4 `brltty` 占用串口

现象可能是设备插上又断开，或者 `dmesg` 里看到 disconnected。

处理：

```bash
sudo apt remove brltty
```

然后拔插 Arm102 USB，再重新 `usbipd attach`。

### 13.5 `rebot_102_leader` 找不到

先安装 Hugging Face LeRobot 的 reBot extra：

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
cd /mnt/d/Robot/reBot-DevArm/_lerobot_experiment
cd lerobot
python -m pip install -e ".[rebot]"
lerobot-calibrate --help | grep -E "rebot_102|102"
```

如果你想试 Seeed 外置包的名字 `rebot_arm_102_leader`：

```bash
cd /mnt/d/Robot/reBot-DevArm/_lerobot_experiment
git clone https://github.com/Seeed-Projects/lerobot-teleoperator-rebot-arm-102.git
python -m pip install -e ./lerobot-teleoperator-rebot-arm-102
lerobot-calibrate --help | grep -E "rebot_arm_102|102"
```

### 13.6 follower 能动，leader 读不到

排查顺序：

1. `ls -l /dev/ttyUSB*`
2. `sudo chmod 666 /dev/ttyUSB*`
3. `dmesg | grep ttyUSB | tail`
4. 确认 Arm102 USB-UART 线没松。
5. 确认不是插到了 Windows 但没 attach 到 WSL。

### 13.7 follower 乱动

立即：

```text
Ctrl+C
```

必要时断 B601-DM 24V。

然后检查：

- leader 是否在正确零位校准。
- follower 是否用 `follower1` 校准文件。
- `joint_directions` 是否有方向反了。
- B601-DM 零点是否之前设错。

---

## 14. 另一条 follower 也切到主线内置的方案

本文默认混合使用：

```text
follower: seeed_b601_dm_follower
leader:   rebot_102_leader
```

如果你想完全跟 Hugging Face 主线文档一致，也可以把 follower 改成内置的 `rebot_b601_follower`。

先安装 reBot extra：

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
cd /mnt/d/Robot/reBot-DevArm/_lerobot_experiment/lerobot
python -m pip install -e ".[rebot]"
```

校准 follower：

```bash
lerobot-calibrate \
  --robot.type=rebot_b601_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=follower \
  --robot.can_adapter=damiao
```

校准 leader 仍然是：

```bash
lerobot-calibrate \
  --teleop.type=rebot_102_leader \
  --teleop.port=/dev/ttyUSB0 \
  --teleop.id=leader
```

遥操作：

```bash
lerobot-teleoperate \
  --robot.type=rebot_b601_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=follower \
  --robot.can_adapter=damiao \
  --teleop.type=rebot_102_leader \
  --teleop.port=/dev/ttyUSB0 \
  --teleop.id=leader
```

注意：这条路径会生成另一套 follower calibration 文件，和 `seeed_b601_dm_follower/follower1.json` 不是同一个目录。没必要主动切，除非 Seeed 外置 follower 遇到兼容问题。

---

## 15. 遥操作成功后，下一步做什么

先不要急着训练。

建议顺序：

1. 无摄像头遥操作 5 分钟，确认每个关节方向和幅度都对。
2. 修正 `joint_directions`，直到手感自然。
3. 接摄像头。
4. 用 `lerobot-find-cameras` 找相机。
5. 跑 `lerobot-record` 采集少量演示数据。
6. 再考虑训练 ACT / Diffusion Policy / SmolVLA。

---

## 16. 每次开机后的最短流程

Windows PowerShell：

```powershell
usbipd list
usbipd attach --wsl --busid B601的BUSID
usbipd attach --wsl --busid Arm102的BUSID
wsl -d Ubuntu-22.04
```

WSL：

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
sudo chmod 666 /dev/ttyACM* /dev/ttyUSB*

lerobot-teleoperate \
  --robot.type=seeed_b601_dm_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=follower1 \
  --robot.can_adapter=damiao \
  --teleop.type=rebot_102_leader \
  --teleop.port=/dev/ttyUSB0 \
  --teleop.id=leader \
  --teleop.joint_directions='{"shoulder_pan":-1,"shoulder_lift":-1,"elbow_flex":1,"wrist_flex":1,"wrist_yaw":1,"wrist_roll":-1,"gripper":-6}'
```

如果你改用 Seeed 外置 `rebot_arm_102_leader`，把 teleop 相关参数换成第 11.2 节的版本。

---

## 17. 参考资料

- Seeed Studio：reBot Arm B601-DM 入门 LeRobot
  - `https://wiki.seeedstudio.com/cn/rebot_arm_b601_dm_lerobot/`
- Hugging Face LeRobot：reBot B601-DM
  - `https://huggingface.co/docs/lerobot/main/rebot_b601`
- Seeed `lerobot-teleoperator-rebot-arm-102`
  - `https://github.com/Seeed-Projects/lerobot-teleoperator-rebot-arm-102`
- PyPI `lerobot-teleoperator-rebot-arm-102`
  - `https://pypi.org/project/lerobot-teleoperator-rebot-arm-102/`
