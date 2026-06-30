#!/bin/bash
# 网页"采数据站"调用：起 LeRobot 视觉采数据（lerobot-record，B601-DM 从臂 + Arm102 leader 遥操）。
# [Added by fanhao375 2026-06-30] env 由 /api/record/start 传入。命令体与 6 个坑来自
#   tools/lerobot_native_linux/采数据_lerobot_record.md（已踩平：warmup / MJPG / 不开 display_data /
#   video=true / batch_size=1 / 编码冻结）。
# 前提（真采集）：原生 Ubuntu 机器人机，conda 环境 lerobot，臂+双相机已接、串口已授权。
#   激活方式按你机器实际，用环境变量指定其一：
#     RECORD_VENV=/path/to/venv         # venv：source $RECORD_VENV/bin/activate
#     RECORD_CONDA_ENV=lerobot          # conda：conda activate 它（默认 lerobot）
# 联调/演示：RECORD_MOCK=1 不接硬件，发假"录制/编码"进度行，供网页联调进度与状态机。
set -e

DATASET_REPO_ID="${DATASET_REPO_ID:-fanhao375/demo_pick}"
SINGLE_TASK="${SINGLE_TASK:-pick the block and put it in the box}"
NUM_EPISODES="${NUM_EPISODES:-10}"
EPISODE_TIME_S="${EPISODE_TIME_S:-30}"
RESET_TIME_S="${RESET_TIME_S:-10}"
FOLLOWER_PORT="${FOLLOWER_PORT:-/dev/ttyACM0}"
LEADER_PORT="${LEADER_PORT:-/dev/ttyUSB0}"
# 相机：top=俯视(Insta360 只给 1280x720 MJPG)，wrist=腕部(640x480 MJPG)。坑①warmup 首帧超时，坑②MJPG 抢带宽。
TOP_CAM="${TOP_CAM:-/dev/v4l/by-id/usb-Insta360_Insta360_Link_2-video-index0}"
WRIST_CAM="${WRIST_CAM:-/dev/v4l/by-path/pci-0000:00:14.0-usb-0:8.2:1.4-video-index0}"

# ---- 演示/联调模式：发假录制进度，不接硬件 ----
if [ "${RECORD_MOCK:-0}" = "1" ]; then
  echo ">>> [MOCK] 演示采集：数据集=$DATASET_REPO_ID 任务=\"$SINGLE_TASK\" 目标条数=$NUM_EPISODES（假数据，不接硬件）"
  i=0
  while [ "$i" -lt "$NUM_EPISODES" ]; do
    echo "Recording episode $i"           # 601 跟手中：做任务
    sleep 1.2
    echo "Encoding episode $i"             # 坑：编码冻结期，601 卡住=正常
    sleep 0.6
    i=$((i + 1))
  done
  echo ">>> [MOCK] 采集结束，共 $NUM_EPISODES 条"
  exit 0
fi

# ---- 真采集 ----
if [ -n "${RECORD_VENV:-}" ]; then
  # shellcheck disable=SC1091
  source "$RECORD_VENV/bin/activate"
else
  # shellcheck disable=SC1091
  source ~/miniforge3/etc/profile.d/conda.sh 2>/dev/null || true
  conda activate "${RECORD_CONDA_ENV:-lerobot}"
fi

# --resume=true 时 num_episodes 设成"目标总数"，在现有数据集上加条不丢已有。
RESUME_ARG=""
if [ "${RESUME:-0}" = "1" ] || [ "${RESUME:-}" = "true" ]; then
  RESUME_ARG="--resume=true"
fi

echo ">>> 启动 lerobot-record：数据集=$DATASET_REPO_ID 任务=\"$SINGLE_TASK\" 目标条数=$NUM_EPISODES"
echo ">>> 键位：→ 提前结束本条 / ← 重录本条 / ESC 停止收尾。任务 10-15 秒做完就按 → 缩短编码冻结。"
echo ">>> 判别：601 跟手=正在录；601 卡住不动=在编码/reset，停手等恢复（坑：编码冻结无法消除，只能缩短）。"
# 坑④ 不开 display_data；坑⑤ batch_size 保持默认 1；坑⑥ 要画面必须靠默认 video=true（别传 video=false，那会把相机整个丢掉）。
# SINGLE_TASK/路径全部加引号展开，值来自 env 不被 shell 二次解释。
exec env HF_HUB_OFFLINE=1 lerobot-record \
  --robot.type=seeed_b601_dm_follower --robot.port="$FOLLOWER_PORT" --robot.id=follower1 --robot.can_adapter=damiao \
  --robot.cameras="{ top: {type: opencv, index_or_path: $TOP_CAM, width: 1280, height: 720, fps: 30, fourcc: MJPG, warmup_s: 6}, wrist: {type: opencv, index_or_path: $WRIST_CAM, width: 640, height: 480, fps: 30, fourcc: MJPG, warmup_s: 3}}" \
  --teleop.type=rebot_arm_102_leader --teleop.port="$LEADER_PORT" --teleop.id=rebot_arm_102_leader \
  --dataset.repo_id="$DATASET_REPO_ID" --dataset.single_task="$SINGLE_TASK" --dataset.num_episodes="$NUM_EPISODES" \
  --dataset.episode_time_s="$EPISODE_TIME_S" --dataset.reset_time_s="$RESET_TIME_S" \
  --dataset.num_image_writer_processes=2 --dataset.vcodec=h264 --dataset.push_to_hub=false \
  $RESUME_ARG
