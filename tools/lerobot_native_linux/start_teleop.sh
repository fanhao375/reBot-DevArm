#!/bin/bash
# 原生 Ubuntu 下启动 Arm102 -> B601-DM 官方遥操作（60Hz 全 7 轴）。
# 前提：① conda 环境 lerobot 已装好  ② 已 apply_patches.py 打过补丁
#       ③ 串口已授权：sudo chmod 666 /dev/ttyUSB0 /dev/ttyACM0
# 串口：/dev/ttyUSB0 = 102 leader(CH340) ; /dev/ttyACM0 = B601 follower(达妙桥)
set -e
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot

if [ ! -e /dev/ttyUSB0 ] || [ ! -e /dev/ttyACM0 ]; then
  echo "!! 缺串口设备。确认两臂已插USB上电；102=/dev/ttyUSB0  B601=/dev/ttyACM0"
  echo "   若 ttyUSB0 不出现：可能 brltty 抢占，sudo apt remove -y brltty 后重插。"
  exit 1
fi

echo ">>> 启动官方遥操作（60Hz，max_relative_target=12 防跳变）。"
echo ">>> 动 102 主臂，B601 跟随。人站旁边，手放 Ctrl+C / 断电旁。Ctrl+C 停止。"
exec lerobot-teleoperate \
  --robot.type=seeed_b601_dm_follower --robot.port=/dev/ttyACM0 --robot.id=follower1 --robot.can_adapter=damiao \
  --teleop.type=rebot_arm_102_leader --teleop.port=/dev/ttyUSB0 --teleop.id=rebot_arm_102_leader
