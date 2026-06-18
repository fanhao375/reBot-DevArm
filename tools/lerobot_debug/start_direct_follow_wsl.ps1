# 一键遥操：Arm102 LD 主动臂 -> B601 DM 跟随臂 direct follow
#
# 本脚本自动完成：
#   1. 按 VID:PID 解析当前 BUSID（换 USB 口后 BUSID 会变，这里不写死）
#   2. 把主臂 / 从臂两个串口 attach 到 WSL
#   3. 在 WSL 里修权限 + 启动 direct follow 遥操作
#
# 设备：
#   主臂 Arm102 LD  CH340  VID 1A86:7523 -> /dev/ttyUSB0
#   从臂 B601  DM   桥      VID 2E88:4603 -> /dev/ttyACM0
#
# 用法：右键“使用 PowerShell 运行”，或在终端执行：
#   powershell -ExecutionPolicy Bypass -File start_direct_follow_wsl.ps1

$ErrorActionPreference = 'Continue'

$LeaderVidPid   = '1a86:7523'   # Arm102 LD CH340
$FollowerVidPid = '2e88:4603'   # B601 DM 串口桥
$Distro         = 'Ubuntu-22.04'

function Get-BusId([string]$VidPid) {
    # 从 usbipd list 文本里按 VID:PID 找当前 BUSID
    $line = (usbipd list) -split "`r?`n" | Where-Object { $_ -match $VidPid } | Select-Object -First 1
    if (-not $line) { return $null }
    if ($line -match '^\s*(\d+-\d+)\s') { return $Matches[1] }
    return $null
}

function Attach-Device([string]$Name, [string]$VidPid) {
    $busid = Get-BusId $VidPid
    if (-not $busid) {
        throw "找不到 $Name ($VidPid)。请确认 USB 已插好，并已 usbipd bind（共享）过。"
    }
    Write-Host "[$Name] BUSID = $busid，attach 到 WSL..."
    # 已经 attach 时 usbipd 会报错，这里吞掉
    usbipd attach --busid $busid --wsl $Distro 2>$null
    return $busid
}

Write-Host "=== 一键遥操：Arm102 -> B601 direct follow ===" -ForegroundColor Cyan

# 0) 先把 WSL 拉起来（usbipd attach 要求目标发行版正在运行）
Write-Host "启动 WSL ($Distro)..."
wsl -d $Distro -- echo "wsl up" | Out-Null

# 1) attach 两个串口
Attach-Device 'Arm102 主臂' $LeaderVidPid   | Out-Null
Attach-Device 'B601 从臂'   $FollowerVidPid | Out-Null

# 1.5) 加载串口内核驱动（attach 后节点不一定自动出现）
wsl -d $Distro -u root -- modprobe -a ch341 cdc_acm 2>$null

# 2) 等设备节点出现并修权限
Write-Host "等待 /dev/ttyUSB0 与 /dev/ttyACM0 就绪..."
$ok = $false
foreach ($i in 1..15) {
    $check = wsl -d $Distro -- bash -lc 'test -e /dev/ttyUSB0 && test -e /dev/ttyACM0 && echo READY' 2>$null
    if ($check -match 'READY') { $ok = $true; break }
    Start-Sleep -Seconds 1
}
if (-not $ok) {
    Write-Host "设备节点未出现。常见处理：" -ForegroundColor Yellow
    Write-Host "  wsl -d $Distro -u root -- modprobe -a ch341 cdc_acm"
    Write-Host "  再重跑本脚本。"
    Read-Host "按回车退出"
    exit 1
}
wsl -d $Distro -u root -- chmod 666 /dev/ttyUSB0 /dev/ttyACM0

# 3) 启动遥操作
Write-Host "设备就绪，启动遥操作。慢慢动主臂，Ctrl+C 停止。" -ForegroundColor Green

wsl -d $Distro -- bash -lc @'
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
cd ~/rebot_lerobot
python -u /mnt/d/Robot/reBot-DevArm/tools/lerobot_debug/arm102_to_b601_direct_follow.py --leader-port /dev/ttyUSB0 --follower-port /dev/ttyACM0 --fps 5 --invert-raw-joints shoulder_lift,elbow_flex
'@

Write-Host ""
Write-Host "遥操作已退出。按回车关闭窗口。"
Read-Host
