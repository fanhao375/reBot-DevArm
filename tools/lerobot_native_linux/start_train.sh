#!/bin/bash
# 网页"训练站"调用：起 LeRobot 训练（lerobot-train）。env 由 /api/train/start 传入。
# [Added by fanhao375 2026-06-30]
# 前提（真训练）：训练机(WSL 5060Ti)已装 lerobot 0.4.4 训练环境，数据集已在 ~/.cache/huggingface/lerobot/。
#   激活方式按你机器实际，用环境变量指定其一：
#     TRAIN_VENV=/path/to/venv        # venv：会 source $TRAIN_VENV/bin/activate
#     TRAIN_CONDA_ENV=lerobot         # conda：会 conda activate 它
# 联调/演示：TRAIN_MOCK=1 时不跑真训练，发假 loss 行（从 6.8 平滑降到 ~0.06），供网页联调曲线。
set -e

DATASET_REPO_ID="${DATASET_REPO_ID:-fanhao375/block_in_box}"
POLICY_TYPE="${POLICY_TYPE:-act}"
STEPS="${STEPS:-80000}"
BATCH="${BATCH:-8}"
# [M2 修复] 输出目录默认带时间戳：lerobot-train 对已存在且非空的 --output_dir 会拒跑（除非 --resume）。
# 不带时间戳的话第二次起训必挂。要续训就显式传 OUTPUT_DIR=旧目录 + RESUME=1。
OUTPUT_DIR="${OUTPUT_DIR:-outputs/train/web_run_$(date +%Y%m%d_%H%M%S)}"

# ---- 演示/联调模式：发假 loss，不动 GPU ----
if [ "${TRAIN_MOCK:-0}" = "1" ]; then
  echo ">>> [MOCK] 演示训练：数据集=$DATASET_REPO_ID 策略=$POLICY_TYPE 步数=$STEPS（假数据，不跑真训练）"
  i=0
  while [ "$i" -lt "$STEPS" ]; do
    i=$((i + 200))
    loss=$(awk "BEGIN{printf \"%.4f\", 6.8*exp(-$i/12000.0)+0.05}")
    echo "step: $i loss: $loss"
    sleep 0.12
  done
  echo ">>> [MOCK] End of training"
  exit 0
fi

# ---- 真训练 ----
if [ -n "${TRAIN_VENV:-}" ]; then
  # shellcheck disable=SC1091
  source "$TRAIN_VENV/bin/activate"
elif [ -n "${TRAIN_CONDA_ENV:-}" ]; then
  # shellcheck disable=SC1091
  source ~/miniforge3/etc/profile.d/conda.sh
  conda activate "$TRAIN_CONDA_ENV"
fi

# 续训：RESUME=1 时从 $OUTPUT_DIR 现有 checkpoint 接着跑（要配合显式 OUTPUT_DIR=旧目录）。
RESUME_ARGS=()
if [ "${RESUME:-0}" = "1" ] || [ "${RESUME:-}" = "true" ]; then
  RESUME_ARGS=(--config_path="$OUTPUT_DIR/checkpoints/last/pretrained_model/train_config.json" --resume=true)
  echo ">>> 续训模式：从 $OUTPUT_DIR 现有 checkpoint 接着跑到 $STEPS 步"
fi

echo ">>> 启动 lerobot-train：数据集=$DATASET_REPO_ID 策略=$POLICY_TYPE 步数=$STEPS batch=$BATCH 输出=$OUTPUT_DIR"
echo ">>> 看 loss 一路下掉、出现 'End of training' 即完成；checkpoint 落在 $OUTPUT_DIR/checkpoints/"
exec env HF_HUB_OFFLINE=1 lerobot-train \
  --dataset.repo_id="$DATASET_REPO_ID" \
  --policy.type="$POLICY_TYPE" \
  --output_dir="$OUTPUT_DIR" \
  --batch_size="$BATCH" \
  --steps="$STEPS" \
  --policy.device=cuda \
  --dataset.video_backend=pyav \
  --wandb.enable=false \
  "${RESUME_ARGS[@]}"
