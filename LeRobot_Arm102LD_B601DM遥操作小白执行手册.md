# LeRobot：Arm102 LD 主臂控制 reBot Arm B601-DM 小白执行手册

这份文档只讲你现在这套硬件：

- **Leader 主臂**：华馨京 / FashionStar `Arm102 LD`，也叫 `StarArm102` / `reBot Arm 102 leader`
- **Follower 从臂**：`reBot Arm B601-DM`，达妙电机版本
- **运行环境**：Windows 工作站 + WSL Ubuntu + LeRobot conda 环境

目标很清楚：

1. 让 WSL 同时看到两个 USB 串口：leader 和 follower。
2. 确认 LeRobot 环境能识别 B601 follower 和 Arm102 leader。
3. 校准 Arm102 leader。
4. 优先运行本仓 direct follow 脚本，用 Arm102 LD 控制 B601-DM。
5. 成功后再考虑摄像头、数据采集和训练。

注意：官方 `lerobot-teleoperate` 能连接，但本机 WSL 下会被每帧 B601 feedback 读取拖到约 2Hz，目前只作为对照，不作为首选入口。

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

### 2026-06-12 本机实测状态

当前这台工作站已经切回 Seeed 官方教程路线。官方教程明确建议使用 `https://github.com/Seeed-Projects/lerobot.git`，不要混用 Hugging Face 实时主线仓库。

已经确认：

- WSL 发行版：`Ubuntu-22.04`。
- Miniforge 路径：`~/miniforge3`。
- conda 环境：`lerobot`。
- 官方工作目录：`~/rebot_lerobot`。
- `lerobot`：`0.4.4`，editable 指向 `/home/pc/rebot_lerobot/lerobot`。
- `lerobot_teleoperator_rebot_arm_102`：`1.0.0`，editable 指向 `/home/pc/rebot_lerobot/lerobot-teleoperator-rebot-arm-102`。
- `lerobot_robot_seeed_b601`：`1.0.0`，editable 指向 `/home/pc/rebot_lerobot/lerobot-robot-seeed-b601`。
- `motorbridge`：`0.4.5`。
- `python -m pip check`：`No broken requirements found`。
- `lerobot-calibrate` 和 `lerobot-teleoperate` 都来自 `/home/pc/miniforge3/envs/lerobot/bin/`。

当前串口对应关系：

```text
Windows COM11 / CH340      -> WSL /dev/ttyUSB0   -> Arm102 LD leader
Windows COM8 / 2e88:4603   -> WSL /dev/ttyACM0   -> B601-DM follower
```

注意：COM 号和 BUSID 会随 USB 口变化。2026-06-12 晚间换口后，B601 从 `1-8` 变成 `1-7`，但仍然是 Windows `COM8`；102 主臂是 `1-6 / COM11`。

校准文件已经确认存在：

```text
~/.cache/huggingface/lerobot/calibration/teleoperators/rebot_arm_102_leader/rebot_arm_102_leader.json
~/.cache/huggingface/lerobot/calibration/robots/seeed_b601_dm_follower/follower1.json
```

今天新增确认：

- Arm102 LD 之前读不了角度，是因为示例脚本缺 `fashionstar-uart-sdk`。
- 安装 `fashionstar-uart-sdk==1.3.12` 后，`read_raw_angles.py` 已经能正常连续输出 102 主臂角度。
- B601 也能读到一次状态，但 WSL USB/IP 对 `/dev/ttyACM0` 写命令仍会 `Operation timed out`。
- 当前 B601 的 `shoulder_pan` 读数约 `90.00`，而 102 主臂映射目标约 `-0.30`，两臂初始姿态差约 90 度。这个状态下不能直接遥操作。

当前阶段结论：

1. Arm102 和 B601 零位已经重新校准并对齐。
2. B601 换 USB 口后，Windows COM8 原生读取稳定，WSL 慢速逐个读取稳定。
3. B601 在 WSL + LeRobot 下可以单独执行动作，说明 follower 的 `send_action()`、电机 ID、模式和基础通信是通的。
4. 官方 `lerobot-teleoperate` 能连接，但循环会反复读 B601 反馈，当前实测约 `614ms / 2Hz`，并出现 `request_feedback failed: dm-serial write failed: Operation timed out`。
5. 所以现在不要把“2、3 电机不跟”直接判断成电机问题。更准确的判断是：官方 teleop 循环太慢/反馈读取超时，再叠加 102 主臂角度方向和 follower 限位裁剪，导致部分轴看起来不跟。

### 2026-06-12 晚间最新进度

本轮实际操作：

- 102 主臂重新校准成功，生成 `rebot_arm_102_leader.json`。
- B601 通过 WSL 官方 `lerobot-calibrate` 校准时在 `disable_all` 超时，未能直接完成。
- B601 改用 Windows COM8 + `motorbridge` 原生通道执行 7 个电机 `set_zero_position()`，7 个电机反馈约 `-0.01°`。
- 随后把 LeRobot 的 `follower1.json` 校准文件恢复到 `~/.cache/huggingface/lerobot/calibration/robots/seeed_b601_dm_follower/follower1.json`。
- B601 换到新 USB 口后，BUSID 从 `1-8` 变成 `1-7`，WSL 需要重新 `attach`，必要时手动 `modprobe cdc_acm ch341`。

已经通过的验证：

```text
B601 Windows COM8 读取：7 个电机接近 -0.01°
B601 WSL 慢速逐个读取：3 轮 7 个电机都接近 -0.01°
102 + B601 被动对比：所有 delta 约 -0.01°
官方 follower 类 get_observation：3 轮 7 个电机都接近 -0.01°
单次安全动作测试：leader 输出 0，follower 接收 0，反馈仍约 -0.01°
B601 LeRobot 2 度动作测试：shoulder_pan 能动并能回零
B601 LeRobot 循环动作测试：shoulder_pan 能按循环动作运动
B601 LeRobot 2/3 轴动作测试：shoulder_lift 和 elbow_flex 都能单独运动
direct follow 单轴测试：1/4/5/6/7 轴都有有效 follower_target
direct follow 单轴测试：2/3 轴加 --invert-raw-joints shoulder_lift,elbow_flex 后可用
官方 lerobot-teleoperate：能连接，但循环约 2Hz，并反复出现 shoulder_pan request_feedback timeout
```

为了适配 WSL USB/IP，已经在本机 Seeed 外置包里做了本地补丁：

```text
~/rebot_lerobot/lerobot-robot-seeed-b601/lerobot_robot_seeed_b601/seeed_b601_follower.py
```

补丁内容：

- `get_observation()` 改成逐个电机 `request_feedback()`，中间加短延时和多次 `poll_feedback_once()`。
- 没有新状态时缓存上一帧观测，避免偶发 `NO_STATE` 直接变成 0。
- `send_pos_vel()` 后加短延时，降低 WSL 串口连续写压力。
- `disconnect()` 对 `disable / clear_error / close` 超时做 warning，不让退出时崩掉。

当前官方 `lerobot-teleoperate` 不稳定的关键日志：

```text
Teleop loop time: 613.xxms (2 Hz)
shoulder_pan request_feedback failed (1/3): request_feedback failed: dm-serial write failed: Operation timed out
```

这个日志说明官方 teleop 每帧都被 B601 的反馈读取拖慢。B601 单独动作脚本已经证明电机能动，所以当前最值得测的是：跳过每帧 B601 反馈读取，只读 102 主臂动作，然后直接给 B601 发 `send_action()`。

---

## 1. 两套命名别搞混

现在官方资料里有两套命名，容易把人绕晕。

### 官方教程路径

这是 Seeed 官方《reBot Arm B601-DM 入门 LeRobot》教程使用的命令体系，也是本文默认路径。

```text
follower: seeed_b601_dm_follower
leader:   rebot_arm_102_leader
```

原因：

- Seeed 官方教程使用这套类型名。
- 你的 B601 follower 已经按 `seeed_b601_dm_follower/follower1.json` 完成校准。
- Arm102 LD 需要安装 Seeed 的 `lerobot-teleoperator-rebot-arm-102` 后才会出现 `rebot_arm_102_leader`。

### Hugging Face 主线内置路径

```text
follower: rebot_b601_follower
leader:   rebot_102_leader
```

这套路径来自 Hugging Face LeRobot 主线，和 Seeed 外置适配器的 calibration 目录不同。除非官方教程路径跑不通，否则不要主动切。

### 本文实际使用

```text
follower: seeed_b601_dm_follower
leader:   rebot_arm_102_leader
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
python -m pip check
python -m pip show lerobot lerobot-teleoperator-rebot-arm-102 lerobot-robot-seeed-b601 motorbridge
```

本机 2026-06-12 已验证的状态应该类似：

```text
No broken requirements found.
lerobot 0.4.4
Editable project location: /home/pc/rebot_lerobot/lerobot
lerobot_teleoperator_rebot_arm_102 1.0.0
Editable project location: /home/pc/rebot_lerobot/lerobot-teleoperator-rebot-arm-102
lerobot_robot_seeed_b601 1.0.0
Editable project location: /home/pc/rebot_lerobot/lerobot-robot-seeed-b601
motorbridge 0.4.5
```

---

## 7. 安装并检查 Seeed 官方 LeRobot 支持

WSL：

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
```

如果还没有下载 Seeed 官方仓库：

```bash
mkdir -p ~/rebot_lerobot
cd ~/rebot_lerobot
git clone https://github.com/Seeed-Projects/lerobot.git
git clone https://github.com/Seeed-Projects/lerobot-teleoperator-rebot-arm-102.git
git clone https://github.com/Seeed-Projects/lerobot-robot-seeed-b601.git
```

如果目录已经存在：

```bash
cd ~/rebot_lerobot
git -C lerobot pull --ff-only
git -C lerobot-teleoperator-rebot-arm-102 pull --ff-only
git -C lerobot-robot-seeed-b601 pull --ff-only
```

安装到当前 conda 环境：

```bash
cd ~/rebot_lerobot
python -m pip install -e ./lerobot -i https://pypi.tuna.tsinghua.edu.cn/simple
python -m pip install -e ./lerobot-teleoperator-rebot-arm-102
python -m pip install -e ./lerobot-robot-seeed-b601
```

检查：

```bash
which lerobot-calibrate
lerobot-calibrate --help | grep -E "rebot_arm_102|seeed_b601"
lerobot-teleoperate --help | grep -E "rebot_arm_102|seeed_b601"
```

你要看到：

```text
rebot_arm_102_leader
seeed_b601_dm_follower
```

如果 `which lerobot-calibrate` 仍然是：

```text
/home/pc/.local/bin/lerobot-calibrate
```

说明你现在用的是用户目录旧命令，不是 conda 环境里的命令。先确认 pip 已安装并安装 LeRobot：

```bash
conda install -y pip
cd ~/rebot_lerobot
python -m pip install -e ./lerobot
python -m pip install -e ./lerobot-robot-seeed-b601
python -m pip install -e ./lerobot-teleoperator-rebot-arm-102
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
  --teleop.type=rebot_arm_102_leader \
  --teleop.port=/dev/ttyUSB0 \
  --teleop.id=rebot_arm_102_leader
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
cd ~/rebot_lerobot
python ./lerobot-teleoperator-rebot-arm-102/examples/read_raw_angles.py --port /dev/ttyUSB0
```

如果报错：

```text
ModuleNotFoundError: No module named 'fashionstar_uart_sdk'
```

安装缺的 102 舵机 SDK：

```bash
python -m pip install fashionstar-uart-sdk -i https://pypi.tuna.tsinghua.edu.cn/simple
python -c "from fashionstar_uart_sdk.uart_pocket_handler import PortHandler; print('fashionstar sdk ok')"
```

期望现象：

- 终端连续打印各关节角度。
- 你轻轻动 Arm102，数字跟着变化。
- 在零位附近，各关节接近 `0`。
- 本机 2026-06-12 已经确认能输出 `shoulder_pan / shoulder_lift / elbow_flex / wrist_flex / wrist_yaw / wrist_roll / gripper`。

示例输出：

```text
shoulder_pan=    0.30  shoulder_lift=   -0.10  elbow_flex=    0.00  wrist_flex=   -0.20  wrist_yaw=   -5.00  wrist_roll=   -2.20  gripper=    0.30
```

如果没有这个示例文件，跳过这步，直接进入第 11 节，但第一次遥操作时动作要更慢。`rebot_arm_102_leader` 会在校准/遥操作时读取 leader 角度。

---

## 10.5 只读对比 leader 和 follower

正式遥操作前，先做一次主从只读对比：

```bash
cd ~/rebot_lerobot
python ./lerobot-teleoperator-rebot-arm-102/examples/read_leader_follower_compare.py \
  --leader-port /dev/ttyUSB0 \
  --follower-port /dev/ttyACM0 \
  --follower-type dm \
  --follower-can-adapter damiao
```

看两件事：

- 是否能连续输出表格。
- `mapped` 和 `follower` 是否大致接近，特别是 `shoulder_pan` 不要差几十度。

本机 2026-06-12 的实测结果：

```text
shoulder_pan mapped=-0.30 follower=90.00 delta=90.30
```

这表示 B601 和 Arm102 初始姿态差约 90 度。这个状态下不要直接遥操作，先把两个臂都摆回官方零位附近。

同时还出现过：

```text
motorbridge.errors.CallError: clear_error failed: dm-serial write failed: Operation timed out
```

这说明 WSL USB/IP 对 B601 `/dev/ttyACM0` 的写命令仍不稳定。见第 14.8 节。

---

## 11. 正式遥操作：Arm102 LD 控 B601-DM

先摆好：

- B601-DM 在安全姿态，别贴桌面、别贴墙。
- Arm102 LD 在零位附近。
- 两个臂的底座朝向、手臂姿态尽量一致；如果只读对比里 `shoulder_pan delta` 差几十度，不要跑遥操作。
- 人站在旁边，准备 `Ctrl+C`。
- 如果 B601-DM 乱动，马上 `Ctrl+C` 或断 24V。

### 11.1 官方教程路径命令

```bash
lerobot-teleoperate \
  --robot.type=seeed_b601_dm_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=follower1 \
  --robot.can_adapter=damiao \
  --teleop.type=rebot_arm_102_leader \
  --teleop.port=/dev/ttyUSB0 \
  --teleop.id=rebot_arm_102_leader
```

注意：`rebot_arm_102_leader` 不支持在命令行传 `--teleop.joint_directions`。之前加这个参数会报：

```text
DecodingError: `teleop`: The fields `joint_directions` are not valid for RebotArm102LeaderConfig
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

### 11.2 Hugging Face 主线备用命令

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

---

## 12. 如果某个关节方向反了

不要立刻重新校准。

当前 Seeed 官方 `rebot_arm_102_leader` 不能在 `lerobot-teleoperate` 命令里直接加 `--teleop.joint_directions`。

先用第 10.5 节的只读对比脚本确认是哪一轴反了，再检查配置文件：

```bash
cd ~/rebot_lerobot
grep -R "joint_directions\|joint_ranges" -n lerobot-teleoperator-rebot-arm-102 lerobot-robot-seeed-b601
```

一般原则：

- leader 侧量程在 `lerobot-teleoperator-rebot-arm-102/lerobot_teleoperator_rebot_arm_102/config_rebot_arm_102_leader.py`。
- follower 侧方向/比例在 `lerobot-robot-seeed-b601` 的配置里。
- 改配置前先备份文件，改完重新安装对应 editable 包或重开终端。

下面是历史思路，仅用于理解方向含义，不要直接复制到当前官方遥操命令里。

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

## 13. 这次真实踩坑记录

这一节是按 2026-06-11 这台工作站实际踩过的坑写的。以后如果重装环境，优先按这里排查。

### 13.1 Windows PowerShell 和 WSL 命令不能混用

错误例子：

```powershell
wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
source ~/.bashrc
```

这个是在 Windows PowerShell 里执行了 Linux 命令，所以会报：

```text
uname : 无法将“uname”项识别为 cmdlet
source : 无法将“source”项识别为 cmdlet
```

正确做法：

```powershell
wsl -d Ubuntu-22.04
```

进入 WSL 后再执行 Linux 命令：

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
```

### 13.2 进入 WSL 后不要再输入 `wsl -d Ubuntu-22.04`

如果提示符长这样：

```bash
pc@DESKTOP-xxxx:/mnt/d/Robot/reBot-DevArm$
```

说明已经在 WSL 里了。再输入 `wsl -d Ubuntu-22.04` 会出现：

```text
Command 'wsl' not found
```

这是正常的，因为 `wsl` 是 Windows 命令，不是 Linux 命令。

### 13.3 `python -m pip` 不存在

这次 `lerobot` conda 环境里一开始没有 pip，报过：

```text
/home/pc/miniforge3/envs/lerobot/bin/python: No module named pip
```

处理：

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
conda install -y pip setuptools wheel
```

### 13.4 `setuptools` 元数据损坏

这是旧环境里遇到过的历史坑。当前 2026-06-12 已经重建/切换到 Seeed 官方环境，`python -m pip check` 已经通过；如果你以后又遇到类似报错，再看这一节。

旧环境安装 `lerobot` 时遇到：

```text
ERROR: Could not install packages due to an OSError:
No such file or directory:
.../setuptools-80.10.2.dist-info/INSTALLERxxxx.tmp
```

原因是环境里的 `setuptools` 元数据处于半损坏状态。

不要随手安装太新的 `setuptools>=82`，因为可能和当时环境里的 LeRobot/Torch 冲突：

```text
lerobot 0.5.2 requires setuptools<81.0.0,>=71.0.0
torch 2.11.0 requires setuptools<82
```

正确修复：

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
python -m pip install --force-reinstall "setuptools==80.9.0" -i https://pypi.tuna.tsinghua.edu.cn/simple
python -m pip show setuptools
```

看到 `Version: 80.9.0` 后，再重新安装：

```bash
cd ~/rebot_lerobot/lerobot
python -m pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 13.4.1 不要混装 LeRobot 0.5.x 和 Seeed 官方教程路线

这次一开始走过 Hugging Face 主线 `lerobot 0.5.2`，后来切回 Seeed 官方教程路线。当前稳定环境是：

```text
~/rebot_lerobot
lerobot 0.4.4
lerobot_teleoperator_rebot_arm_102 1.0.0
lerobot_robot_seeed_b601 1.0.0
motorbridge 0.4.5
```

经验：

- 不要在同一个 conda 环境里来回混装主线 0.5.x 和 Seeed 教程包。
- 如果命令能找到但参数报 `DecodingError`，先检查 `python -m pip show lerobot lerobot-teleoperator-rebot-arm-102 lerobot-robot-seeed-b601 motorbridge`。
- `lerobot-calibrate` / `lerobot-teleoperate` 必须来自 `/home/pc/miniforge3/envs/lerobot/bin/`，不是 `/home/pc/.local/bin/`。

### 13.5 B601 已经 attach，但 WSL 没有 `/dev/ttyACM0`

这次 Windows 里看到：

```text
1-8    2e88:4603  USB 串行设备 (COM8)    Attached
```

但 WSL 里只有：

```text
/dev/ttyUSB0
```

没有：

```text
/dev/ttyACM0
```

原因是 WSL 里 `cdc_acm` 驱动没有加载。

处理：

```powershell
wsl -d Ubuntu-22.04 -u root -- modprobe cdc_acm
wsl -d Ubuntu-22.04 -u root -- chmod 666 /dev/ttyACM0 /dev/ttyUSB0
```

再检查：

```powershell
wsl -d Ubuntu-22.04 -- ls -l /dev/ttyUSB0 /dev/ttyACM0
```

目标输出类似：

```text
crw-rw-rw- ... /dev/ttyACM0
crw-rw-rw- ... /dev/ttyUSB0
```

### 13.6 B601 的 `brltty` 不是本机问题

官方教程说初次连接可能被 `brltty` 占用。这台工作站已经查过，`brltty` 没装，所以这次不是它的问题。

如果以后别的机器出现断开重连，可以再查：

```bash
dpkg -l | grep brltty
dmesg | grep -E "ttyACM|ttyUSB|brltty" | tail -n 50
```

如果确实安装了 `brltty`，再执行：

```bash
sudo apt remove brltty
```

### 13.7 安装成功后的最终确认命令

WSL 里执行：

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot

python -m pip show lerobot lerobot-robot-seeed-b601 lerobot-teleoperator-rebot-arm-102 motorbridge motorbridge-smart-servo
lerobot-calibrate --help | grep -E "rebot_arm_102|seeed_b601"
lerobot-teleoperate --help | grep -E "rebot_arm_102|seeed_b601"
ls -l /dev/ttyUSB0 /dev/ttyACM0
```

这次最终确认结果：

```text
imports ok
/dev/ttyUSB0 存在，权限 crw-rw-rw-
/dev/ttyACM0 存在，权限 crw-rw-rw-
rebot_arm_102_leader 存在
seeed_b601_dm_follower 存在
```

### 13.8 官方 `lerobot-teleoperate` 能连接，但不等于适合 WSL 实时遥操

这次官方命令可以连上：

```bash
lerobot-teleoperate --robot.type=seeed_b601_dm_follower --robot.port=/dev/ttyACM0 --robot.id=follower1 --robot.can_adapter=damiao --teleop.type=rebot_arm_102_leader --teleop.port=/dev/ttyUSB0 --teleop.id=rebot_arm_102_leader
```

但实测会出现：

```text
Teleop loop time: 613.xxms (2 Hz)
shoulder_pan request_feedback failed (1/3): request_feedback failed: dm-serial write failed: Operation timed out
```

原因不是命令写错，而是官方 `teleop_loop()` 每帧都会先 `robot.get_observation()`，也就是向 B601 逐个电机读 feedback。WSL USB/IP 下这个动作很容易拖慢整轮循环。

当前策略：

- 官方 `lerobot-teleoperate` 暂时只作为对照。
- 真机 WSL 遥操优先用本仓 `arm102_to_b601_direct_follow.py`，跳过每帧 B601 feedback。

### 13.9 `--send-joints` 只测试指定轴，不代表其他轴不行

这次为了排查 2/3 轴，跑过：

```bash
python -u /mnt/d/Robot/reBot-DevArm/tools/lerobot_debug/arm102_to_b601_direct_follow.py --leader-port /dev/ttyUSB0 --follower-port /dev/ttyACM0 --fps 5 --send-joints shoulder_lift,elbow_flex --invert-raw-joints shoulder_lift,elbow_flex
```

这条命令只发送 `shoulder_lift` 和 `elbow_flex`，所以不能据此说“其他轴不行”。其他轴要用各自的 `--send-joints` 单独测。

### 13.10 2/3 轴“不动”的真实原因：方向和限位裁剪

一开始 2/3 轴看起来不跟，实际不是电机坏。日志里能看到：

```text
leader shoulder_lift = -1.00
leader elbow_flex    =  1.00
```

B601 follower 的限位是：

```text
shoulder_lift [-170, 0]
elbow_flex    [-200, 0]
```

如果 102 原始角度先被 leader 自己裁剪，再经过 follower 方向映射，很容易变成正数，最后被 B601 限位裁成 `0.00`。肉眼看就是“不动”。

修复方式是在 102 原始角度裁剪前反向：

```bash
--invert-raw-joints shoulder_lift,elbow_flex
```

当前全轴 direct follow 推荐命令：

```bash
python -u /mnt/d/Robot/reBot-DevArm/tools/lerobot_debug/arm102_to_b601_direct_follow.py --leader-port /dev/ttyUSB0 --follower-port /dev/ttyACM0 --fps 5 --invert-raw-joints shoulder_lift,elbow_flex
```

### 13.11 `clear_error failed during disconnect` 多数是退出时串口超时

按 `Ctrl+C` 停止时，偶尔会看到：

```text
motor clear_error failed during disconnect: clear_error failed: dm-serial write failed: Operation timed out
```

这通常发生在程序退出、尝试清错误/关闭电机时。只要机械臂已经停止、下一次上电/连接能正常，不要把它误判成“电机坏”。如果连续出现控制异常，再断电 5 秒、重新 attach USB、重新进入 WSL 环境。

---

## 14. 常见问题

### 14.1 `wsl: command not found`

你在 WSL 里输入了 Windows 命令。

正确做法：

- `wsl -d Ubuntu-22.04` 在 Windows PowerShell 里执行。
- 进入 WSL 后，不要再输入 `wsl`。

### 14.2 `/dev/ttyACM0` 不存在

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

如果 Windows 已经显示 `Attached`，但 WSL 还是没有 `/dev/ttyACM0`，加载驱动：

```powershell
wsl -d Ubuntu-22.04 -u root -- modprobe cdc_acm
wsl -d Ubuntu-22.04 -u root -- chmod 666 /dev/ttyACM0
```

### 14.3 `/dev/ttyUSB0` 不存在

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

### 14.4 `brltty` 占用串口

现象可能是设备插上又断开，或者 `dmesg` 里看到 disconnected。

处理：

```bash
sudo apt remove brltty
```

然后拔插 Arm102 USB，再重新 `usbipd attach`。

### 14.5 `rebot_arm_102_leader` 找不到

安装 Seeed 102 leader 包：

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
cd ~/rebot_lerobot
git clone https://github.com/Seeed-Projects/lerobot-teleoperator-rebot-arm-102.git
python -m pip install -e ./lerobot-teleoperator-rebot-arm-102
lerobot-calibrate --help | grep -E "rebot_arm_102|102"
```

如果 clone 失败但本地已有目录：

```bash
cd ~/rebot_lerobot
git -C lerobot-teleoperator-rebot-arm-102 pull --ff-only
python -m pip install -e ./lerobot-teleoperator-rebot-arm-102
lerobot-calibrate --help | grep -E "rebot_arm_102|102"
```

### 14.6 follower 能动，leader 读不到

排查顺序：

1. `ls -l /dev/ttyUSB*`
2. `sudo chmod 666 /dev/ttyUSB*`
3. `dmesg | grep ttyUSB | tail`
4. 确认 Arm102 USB-UART 线没松。
5. 确认不是插到了 Windows 但没 attach 到 WSL。

### 14.7 102 示例脚本缺 `fashionstar_uart_sdk`

现象：

```text
ModuleNotFoundError: No module named 'fashionstar_uart_sdk'
```

处理：

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
python -m pip install fashionstar-uart-sdk -i https://pypi.tuna.tsinghua.edu.cn/simple
```

本机已验证：安装后 `read_raw_angles.py` 可以正常读取 102 主臂角度。

### 14.8 B601 在 WSL 里 `Operation timed out`

现象：

```text
motorbridge.errors.CallError: request_feedback failed: dm-serial write failed: Operation timed out
motorbridge.errors.CallError: clear_error failed: dm-serial write failed: Operation timed out
```

同时 `dmesg | tail -80` 里能看到大量：

```text
vhci_hcd: urb->status -104
```

这不是 LeRobot 命令写错，而是 WSL 通过 `usbipd` 转发 USB 串口时，B601 达妙串口桥的实时读写不稳定。官方教程默认是 Ubuntu/Linux 原生环境，WSL 可以安装和调试，但连续实时控制更容易遇到这个问题。

临时处理：

```powershell
usbipd list
usbipd detach --busid B601的BUSID
usbipd attach --wsl --busid B601的BUSID
```

然后 WSL：

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
cd ~/rebot_lerobot
sudo chmod 666 /dev/ttyACM* /dev/ttyUSB*
dmesg | tail -30
```

如果仍然频繁 `Operation timed out`，不要继续遥操作。更稳的方案是用原生 Ubuntu/Jetson 跑 B601，或者等 Windows 侧稳定桥接方案。

### 14.9 follower 乱动

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

## 15. 另一条 follower 也切到主线内置的方案

本文默认使用 Seeed 官方教程路径：

```text
follower: seeed_b601_dm_follower
leader:   rebot_arm_102_leader
```

如果你想完全跟 Hugging Face 主线文档一致，也可以把 follower 改成内置的 `rebot_b601_follower`。

先安装 reBot extra：

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
cd ~/rebot_lerobot/lerobot
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

校准 leader：

```bash
lerobot-calibrate \
  --teleop.type=rebot_arm_102_leader \
  --teleop.port=/dev/ttyUSB0 \
  --teleop.id=rebot_arm_102_leader
```

遥操作：

```bash
lerobot-teleoperate \
  --robot.type=rebot_b601_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=follower \
  --robot.can_adapter=damiao \
  --teleop.type=rebot_arm_102_leader \
  --teleop.port=/dev/ttyUSB0 \
  --teleop.id=rebot_arm_102_leader
```

注意：这条路径会生成另一套 follower calibration 文件，和 `seeed_b601_dm_follower/follower1.json` 不是同一个目录。没必要主动切，除非 Seeed 外置 follower 遇到兼容问题。

---

## 16. 遥操作成功后，下一步做什么

先不要急着训练。

建议顺序：

1. 无摄像头遥操作 5 分钟，确认每个关节方向和幅度都对。
2. 修正 `joint_directions`，直到手感自然。
3. 接摄像头。
4. 用 `lerobot-find-cameras` 找相机。
5. 跑 `lerobot-record` 采集少量演示数据。
6. 再考虑训练 ACT / Diffusion Policy / SmolVLA。

---

## 17. 每次开机后的最短流程

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
cd ~/rebot_lerobot
sudo modprobe cdc_acm
sudo chmod 666 /dev/ttyACM* /dev/ttyUSB*
ls -l /dev/ttyUSB* /dev/ttyACM*
```

先只读检查 102 主臂：

```bash
python ./lerobot-teleoperator-rebot-arm-102/examples/read_raw_angles.py --port /dev/ttyUSB0
```

再只读对比主从臂：

```bash
python ./lerobot-teleoperator-rebot-arm-102/examples/read_leader_follower_compare.py \
  --leader-port /dev/ttyUSB0 \
  --follower-port /dev/ttyACM0 \
  --follower-type dm \
  --follower-can-adapter damiao
```

只有在下面两个条件都满足时，才启动遥操作：

- 没有 `Operation timed out`。
- 两个臂初始姿态已经对齐，`shoulder_pan delta` 不再差几十度。

遥操作：

```bash
lerobot-teleoperate \
  --robot.type=seeed_b601_dm_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=follower1 \
  --robot.can_adapter=damiao \
  --teleop.type=rebot_arm_102_leader \
  --teleop.port=/dev/ttyUSB0 \
  --teleop.id=rebot_arm_102_leader
```

如果你改用 Hugging Face 主线 `rebot_102_leader`，把 teleop 相关参数换成第 11.2 节的版本。

---

## 17.5 当前下一步怎么继续

当前不要再直接硬跑官方 `lerobot-teleoperate`。原因不是 2、3 电机坏，而是官方 teleop 循环每帧都会先读 B601 反馈，实测会卡到约 2Hz 并反复 `request_feedback timeout`。

下次继续时按这个顺序：

1. B601 断电 5 秒再上电，102 主臂也保持零位。
2. 换口后先看 BUSID，B601 当前更可能是 `1-7 / COM8`，102 是 `1-6 / COM11`。
3. attach 到 WSL 后，进入环境：

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
cd ~/rebot_lerobot
sudo modprobe ch341
sudo modprobe cdc_acm
sudo chmod 666 /dev/ttyUSB* /dev/ttyACM*
ls -l /dev/ttyUSB* /dev/ttyACM*
```

4. 先读 102 主臂，确认主臂角度会跟着你手动转动变化：

```bash
python -u ./lerobot-teleoperator-rebot-arm-102/examples/read_raw_angles.py --port /dev/ttyUSB0
```

看到连续角度输出后按 `Ctrl+C` 停止。

5. 跑 B601 慢速只读：

```bash
python -u /mnt/d/Robot/reBot-DevArm/tools/lerobot_debug/b601_read_slow.py
```

6. 跑被动对比，确认 102 映射目标和 B601 当前姿态没有差几十度：

```bash
python -u /mnt/d/Robot/reBot-DevArm/tools/lerobot_debug/b601_passive_compare.py
```

7. 如果怀疑 2、3 电机不动，先跑 2、3 轴单独动作测试：

```bash
python -u /mnt/d/Robot/reBot-DevArm/tools/lerobot_debug/b601_lerobot_joint23_test.py
```

8. 如果要验证跟随，不要先用官方 `lerobot-teleoperate`，先跑 direct follow 对照脚本。这个脚本仍然使用 Seeed 官方 102 leader 类和 B601 follower 类，但控制循环里不每帧读 B601 反馈：

```bash
python -u /mnt/d/Robot/reBot-DevArm/tools/lerobot_debug/arm102_to_b601_direct_follow.py --leader-port /dev/ttyUSB0 --follower-port /dev/ttyACM0 --fps 8
```

运行时手放在 `Ctrl+C` 或电源旁边。看到异常运动就立刻停止。

9. 如果某个轴不跟，先不要说电机坏，先看 `follower_target`。如果 `leader` 在变，但 `follower_target` 总是 `0.00`，就是方向或限位裁剪问题。

已经确认 2、3 轴需要在 102 原始角度裁剪前反向：

```bash
python -u /mnt/d/Robot/reBot-DevArm/tools/lerobot_debug/arm102_to_b601_direct_follow.py --leader-port /dev/ttyUSB0 --follower-port /dev/ttyACM0 --fps 5 --send-joints shoulder_lift,elbow_flex --invert-raw-joints shoulder_lift,elbow_flex
```

注意：`--send-joints` 是“只发送这些轴”。上面这条只测试 2、3 轴，不代表其他轴收到命令。

10. 逐个确认其他轴时，用下面这种格式，一次只测一个轴：

```bash
python -u /mnt/d/Robot/reBot-DevArm/tools/lerobot_debug/arm102_to_b601_direct_follow.py --leader-port /dev/ttyUSB0 --follower-port /dev/ttyACM0 --fps 5 --send-joints shoulder_pan
python -u /mnt/d/Robot/reBot-DevArm/tools/lerobot_debug/arm102_to_b601_direct_follow.py --leader-port /dev/ttyUSB0 --follower-port /dev/ttyACM0 --fps 5 --send-joints wrist_flex
python -u /mnt/d/Robot/reBot-DevArm/tools/lerobot_debug/arm102_to_b601_direct_follow.py --leader-port /dev/ttyUSB0 --follower-port /dev/ttyACM0 --fps 5 --send-joints wrist_yaw
python -u /mnt/d/Robot/reBot-DevArm/tools/lerobot_debug/arm102_to_b601_direct_follow.py --leader-port /dev/ttyUSB0 --follower-port /dev/ttyACM0 --fps 5 --send-joints wrist_roll
```

如果某个轴 `follower_target` 一直是 0 或方向反了，再给那个轴加 `--invert-raw-joints 轴名` 单独试一次。

当前单轴测试结论：

```text
1 shoulder_pan：有效，follower_target = -leader
2 shoulder_lift：需要 --invert-raw-joints shoulder_lift
3 elbow_flex：需要 --invert-raw-joints elbow_flex
4 wrist_flex：有效，follower_target = leader
5 wrist_yaw：有效，follower_target = leader
6 wrist_roll：有效，follower_target = -leader
7 gripper：有效，follower_target = -6 * leader，并裁剪到 [-270, 0]
```

11. 单轴都确认后，跑全轴 direct follow。注意这条命令没有 `--send-joints`，会发送全部 7 个轴：

```bash
python -u /mnt/d/Robot/reBot-DevArm/tools/lerobot_debug/arm102_to_b601_direct_follow.py --leader-port /dev/ttyUSB0 --follower-port /dev/ttyACM0 --fps 5 --invert-raw-joints shoulder_lift,elbow_flex
```

先小幅慢慢动，不要一上来大幅摆动。看到异常运动就立刻 `Ctrl+C` 或断电。

12. 如果 direct follow 全轴能跟，说明问题基本就在官方 `lerobot-teleoperate` 的每帧 `robot.get_observation()`。这时再考虑两条路：

- 继续用 direct follow 作为 WSL 临时遥操作入口。
- 给官方 `lerobot-teleoperate` 增加一个“跳过每帧 follower observation”的本地补丁。

13. 如果 direct follow 也不跟，再回到单关节动作和主臂读数，分别排查方向、限位和主臂输出角度。

官方完整遥操作命令保留如下，但目前只作为对照，不作为首选：

```bash
lerobot-teleoperate \
  --robot.type=seeed_b601_dm_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=follower1 \
  --robot.can_adapter=damiao \
  --teleop.type=rebot_arm_102_leader \
  --teleop.port=/dev/ttyUSB0 \
  --teleop.id=rebot_arm_102_leader
```

如果官方命令仍然显示 `Teleop loop time: 600ms` 左右，并反复 `request_feedback timeout`，不要继续纠结 2、3 轴，先回到 direct follow 或修改官方循环。

---

## 18. 参考资料

- Seeed Studio：reBot Arm B601-DM 入门 LeRobot
  - `https://wiki.seeedstudio.com/cn/rebot_arm_b601_dm_lerobot/`
- Hugging Face LeRobot：reBot B601-DM
  - `https://huggingface.co/docs/lerobot/main/rebot_b601`
- Seeed `lerobot-teleoperator-rebot-arm-102`
  - `https://github.com/Seeed-Projects/lerobot-teleoperator-rebot-arm-102`
- PyPI `lerobot-teleoperator-rebot-arm-102`
  - `https://pypi.org/project/lerobot-teleoperator-rebot-arm-102/`
