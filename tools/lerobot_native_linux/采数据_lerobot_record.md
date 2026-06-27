# 原生 Ubuntu 采数据（lerobot-record，B601-DM 从臂 + Arm102 leader 遥操）

2026-06-27 在原生 Ubuntu 上把 `lerobot-record` 视觉采数据全链路跑通，踩平一堆非显然的坑。
**这台 Linux 只采数据，训练在另一台 5060Ti 16G。** 相机硬件/路径见 [README.md](./README.md) 与记忆 `project-native-linux-cameras`。

## 可用命令（已规避全部坑）

```bash
conda activate lerobot
lerobot-record \
  --robot.type=seeed_b601_dm_follower --robot.port=/dev/ttyACM0 --robot.id=follower1 --robot.can_adapter=damiao \
  --robot.cameras="{ top: {type: opencv, index_or_path: /dev/v4l/by-id/usb-Insta360_Insta360_Link_2-video-index0, width: 1280, height: 720, fps: 30, fourcc: MJPG, warmup_s: 6}, wrist: {type: opencv, index_or_path: /dev/v4l/by-path/pci-0000:00:14.0-usb-0:8.2:1.4-video-index0, width: 640, height: 480, fps: 30, fourcc: MJPG, warmup_s: 3}}" \
  --teleop.type=rebot_arm_102_leader --teleop.port=/dev/ttyUSB0 --teleop.id=rebot_arm_102_leader \
  --dataset.repo_id=fanhao375/<数据集名> --dataset.single_task="任务描述" --dataset.num_episodes=N \
  --dataset.episode_time_s=30 --dataset.reset_time_s=10 \
  --dataset.num_image_writer_processes=2 --dataset.vcodec=h264 --dataset.push_to_hub=false
```

续录（在现有数据集上加条，不丢已有）：加 `--resume=true`，`num_episodes` 设成**目标总数**。

## 踩过的 6 个坑

| # | 现象 | 原因 / 修法 |
|---|------|------------|
| 1 | 连接时 `TimeoutError: Timed out waiting for frame` | 默认 `warmup_s=1`(首帧超时 1s)，**Insta360 首帧要 ~2.7s**。给 top `warmup_s:6`、wrist `warmup_s:3` |
| 2 | 双相机同跑时 Gemini `select() timeout` 卡死 | 两台同在一条 USB2.0 总线，**Gemini 默认 YUYV 640x480@30=18MB/s** 抢爆带宽。给 Gemini 加 **`fourcc: MJPG`**(它支持)→ 两台都稳 30fps |
| 3 | Insta360 设 640x480 报 `failed to set capture_width` | Insta360 MJPG 只给 1280x720，俯视图只能这个分辨率 |
| 4 | 录制时从臂明显延时、~14fps | `--display_data=true`(rerun 实时显示)+ 大图每帧写盘拖垮控制环。**采数据别开 display_data** + `num_image_writer_processes=2` → ~25fps |
| 5 | `video_encoding_batch_size>1` 结尾崩 `'NoneType' object is not subscriptable` | 这版 `_batch_save_episode_video` 的 bug，**保持默认 batch_size=1** |
| 6 | ⚠️ **`--dataset.video=false` 把相机整个丢掉** | 这版含义是"剔除所有图像特征只留关节"(`pipeline_features.py:120`)，**不是存 PNG**！要画面**必须 `video=true`** |

## 固有限制：每条之间约 20-80 秒"编码冻结"（无法消除，只能缩短）

`video=true` 下每录完一条同步把 N 帧 PNG 刷盘 + 读回编码 MP4（`vcodec=h264` 比默认 libsvtav1 快些，但读 PNG 的 I/O 是大头，这台 CPU 扛不动实时；冻结时长 ∝ 帧数：~15s 条冻 ~25s，60s 条冻 ~80s）。冻结期间**主线程占住、遥操作停摆、601 不动**。

- **缓解**：每条录短——任务 10-15 秒做完**立刻按 `→`** 提前结束这条，帧少冻结短。
- **判别法（后台跑看不到 Recording/Reset 提示时）**：**601 跟手=正在录，做任务；601 卡住不动=在编码/reset，停手等恢复。** 从臂状态就是信号灯。
- **键盘控制**（非 headless，pynput + DISPLAY 可用，焦点在哪都能按）：`→`=提前结束当前条 / `←`=重录当前条 / `ESC`=停止收尾。

## 验收 + 清理 + 打包

```bash
# 验收：读 parquet 按 episode 算 action(主臂指令) 与 observation.state(从臂) 的 max-min 幅度
#   主臂≈0° = 你没动 102(录了空条)；主臂动了但从臂没动 = 601 没跟(真问题)；幅度<30° 判废
# 删废条(会自动把原数据备份成 <repo_id>_old，再重建——耐心等编码完，别中途查以为删空了)
lerobot-edit-dataset --repo_id=fanhao375/<名> --operation.type=delete_episodes --operation.episode_indices="[0,4,17]"
# 打包给训练机
tar -czf ~/<名>_dataset.tar.gz -C ~/.cache/huggingface/lerobot/fanhao375 <名>
```

数据集落地 `~/.cache/huggingface/lerobot/<repo_id>`；视频在 `videos/observation.images.{top,wrist}/chunk-000/*.mp4`。
训练机解压到同路径后 `lerobot-train --dataset.repo_id=... --policy.type=act --policy.device=cuda`。
