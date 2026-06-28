# LeRobot 模仿学习全流程小白教程（采集 → 训练 → 部署）

> 本教程把"教机械臂自己干活"的全过程从零讲清楚，照着做就能复现。
> 实测环境：达妙版 B601 从臂 + Arm102 leader 主臂 + 2 个相机，原生 Ubuntu 采数据、另一台 5060Ti(WSL2) 训练。
> 配套技术速记见 [`tools/lerobot_native_linux/采数据_lerobot_record.md`](./tools/lerobot_native_linux/采数据_lerobot_record.md)；遥操作环境搭建见 [`LeRobot_Arm102LD_B601DM遥操作小白执行手册.md`](./LeRobot_Arm102LD_B601DM遥操作小白执行手册.md)。

---

## 〇、先搞懂这是在干嘛（30 秒看懂）

我们用的是 **模仿学习（Imitation Learning）**，说人话就是 **"你手把手示范几十遍，AI 看着学会自己干"**。

整个过程就 **3 步**，这是 LeRobot/Seeed **官方标准流程**，一步不多一步不少：

```
①  采集数据          ②  训练模型          ③  部署
  你遥操作机械臂   →    GPU 机器看你的     →    模型自己看摄像头
  做几十遍任务         示范学出一个模型        驱动机械臂干活
  (lerobot-record)    (lerobot-train)        (lerobot-record
   + 遥操作            --policy.type=act       --policy.path=模型)
```

- **第①步**在**采数据这台**做（接机械臂 + 相机的那台 Linux）。
- **第②步**在**有显卡的训练机**做（我们用 5060Ti / WSL2）。GPU 才跑得动训练。
- **第③步**回到**采数据这台**做（要接真机械臂）。

**为什么要两台机器？** 采数据要接机械臂和相机（在 Linux 那台），训练要大显卡（在 5060Ti 那台）。数据用 U 盘/网络拷过去，模型再拷回来。

---

## 一、准备工作（每次开工前检查）

### 硬件
- [ ] **主臂 Arm102**（你手动拖动的那个）插好 USB → `/dev/ttyUSB0`
- [ ] **从臂 B601**（干活的那个）插好 USB → `/dev/ttyACM0`，**而且电机电源要开**（达妙供电那一路，不是 USB；电机红灯常亮=正常）
- [ ] **俯视相机 Insta360** 插好（USB 容易松，插到底）
- [ ] **腕部相机 Gemini 2** 插好
- [ ] 桌上摆好**积木**和**盒子**，在两个相机都看得见的位置

### 软件（一次性装好，之后不用管）
- conda 环境 `lerobot`（Python 3.10），命令前先 `conda activate lerobot`
- 装环境的坑见记忆/手册，这里假设已装好。

### 每次开工第一件事：验证设备都在
```bash
# 相机路径（认序列号/USB口，比 /dev/videoN 稳；插拔后会变，所以用这个）
ls /dev/v4l/by-id/usb-Insta360_Insta360_Link_2-video-index0          # 俯视
ls /dev/v4l/by-path/pci-0000:00:14.0-usb-0:8.2:1.4-video-index0      # 腕部
ls /dev/ttyUSB0 /dev/ttyACM0                                          # 主臂、从臂
lsusb | grep -i insta                                                 # 确认俯视相机在 USB 上
```
任何一个不在 → 重插那个设备。**Insta360 特别爱掉线，没有就重插。**

---

## 二、第①步：采集数据（教 AI 的"教材"）

### 原理
你用主臂 102 遥操作从臂 601 做任务，**同时**程序录下：
- 每一帧两个相机的**画面**（top 俯视 + wrist 腕部）
- 每一帧机械臂 7 个关节的**角度**（observation.state）
- 你下达的**动作指令**（action）

录几十遍 → 就是 AI 的"教材"。**教得好不好，直接决定 AI 学得好不好。**

### 启动采集
```bash
conda activate lerobot
lerobot-record \
  --robot.type=seeed_b601_dm_follower --robot.port=/dev/ttyACM0 --robot.id=follower1 --robot.can_adapter=damiao \
  --robot.cameras="{ top: {type: opencv, index_or_path: /dev/v4l/by-id/usb-Insta360_Insta360_Link_2-video-index0, width: 1280, height: 720, fps: 30, fourcc: MJPG, warmup_s: 6}, wrist: {type: opencv, index_or_path: /dev/v4l/by-path/pci-0000:00:14.0-usb-0:8.2:1.4-video-index0, width: 640, height: 480, fps: 30, fourcc: MJPG, warmup_s: 3}}" \
  --teleop.type=rebot_arm_102_leader --teleop.port=/dev/ttyUSB0 --teleop.id=rebot_arm_102_leader \
  --dataset.repo_id=fanhao375/我的数据集名字 \
  --dataset.single_task="把积木放进盒子" \
  --dataset.num_episodes=30 \
  --dataset.episode_time_s=30 --dataset.reset_time_s=10 \
  --dataset.num_image_writer_processes=2 --dataset.vcodec=h264 \
  --dataset.push_to_hub=false
```

**逐个参数说人话：**
| 参数 | 意思 |
|---|---|
| `--robot.*` | 从臂 601 怎么连（达妙电机、ttyACM0） |
| `--robot.cameras` | 两个相机：top 俯视 1280x720、wrist 腕部 640x480。**`fourcc: MJPG` 和 `warmup_s` 必须有**（见坑表） |
| `--teleop.*` | 主臂 102 怎么连（你拖它，601 跟着动） |
| `--dataset.repo_id` | 数据集名字，随便起，存本地 `~/.cache/huggingface/lerobot/这个名字` |
| `--single_task` | 任务文字描述 |
| `--num_episodes=30` | 打算录 30 条 |
| `--episode_time_s=30` | 每条最多 30 秒（做完按 → 提前结束，见下） |
| `--vcodec=h264` | 视频用 h264 编码（**别用默认的 av1，会有解码麻烦**） |
| `--push_to_hub=false` | 只存本地，不传网上 |

### 录制时怎么操作（最关键，决定数据质量）

程序跑起来后是**一条一条循环**录的。**用从臂 601 当信号灯**（后台跑看不到屏幕提示时）：

| 601 状态 | 含义 | 你该干嘛 |
|---|---|---|
| 🟢 **跟手（你动102它动）** | 正在录这一条 | **做任务！** 抓积木→移到盒子→**张开夹爪→停留1-2秒**→收回 |
| 🔴 **卡住不动 ~20-40秒** | 在编码上一条的视频（CPU 忙） | **停手，趁机把积木摆回原位**，等它"活过来" |
| 🟢 又跟手了 | 下一条开始 | 再做一遍 |

**键盘控制（重要）：**
- **`→` 右箭头**：这一条任务做完了，**立刻按 →** 结束这条、进下一条（不用等满 30 秒）
- **`←` 左箭头**：这条做砸了，重录
- **`ESC`**：全部停止、保存收尾

**⚠️ 三条铁律（血泪教训）：**
1. **必须先动 102 采到画面了再按 →**。一进录制还没动就按 → = 0 帧 = **程序直接崩溃**。
2. **601 跟手了才算在录**。如果你在"卡住期"动 102，601 不动 = 这条录的是空的（白录）。
3. **做满再按 →**。别手抖瞬间按 →（会录个 0-1 秒的废条）。

### 怎么录出好教材（直接影响 AI 学得好不好）
- **每条积木位置稍微变一变**（左一点、右一点、转个角度）→ AI 才学得会"泛化"，而不是死记一个位置。
- **关键动作要"演清楚"**：比如"松开夹爪"这一下，**要明显、要停留**，不然一闪而过 AI 学不到（我们第一次就栽在这——AI 会抓不会放）。
- **每条的节奏/时机尽量一致**（别有的早放有的晚放，AI 会迷糊）。
- **数量**：先录 10 条试管线，确认没问题再冲 **30~50 条**（越多越好，单任务 ACT 建议 50+）。

### 录完验收（挑出有效条 / 废条）
```bash
python3 - <<'PY'
import glob,pandas as pd,numpy as np
D="/home/pc/.cache/huggingface/lerobot/fanhao375/我的数据集名字"
df=pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(D+"/data/**/*.parquet",recursive=True))],ignore_index=True)
for ep in sorted(df['episode_index'].unique()):
    s=df[df['episode_index']==ep]
    act=np.stack(s['action'].values); st=np.stack(s['observation.state'].values)
    a=(act.max(0)-act.min(0)).max(); sm=(st.max(0)-st.min(0)).max()
    print(f"ep{ep}: {len(s)}帧 主臂={a:.0f}° 从臂={sm:.0f}° {'✅有效' if a>30 and sm>30 else '⚠️废条'}")
PY
```
- **主臂 ≈ 0°** = 你那条没动 102（空条，废）
- **主臂动了、从臂没动** = 601 当时没跟上（真问题）
- **幅度 < 30°** = 判废

### 删废条
```bash
# 比如废条是 1、4、17
lerobot-edit-dataset --repo_id=fanhao375/我的数据集名字 \
  --operation.type=delete_episodes --operation.episode_indices="[1,4,17]"
```
> ⚠️ 这个删除工具**默认会把重编码的视频转成 AV1**（训练机可能解不动）。要全 h264 得用脚本 monkeypatch（见技术速记文档），或者干脆**采集时就别按错、少产生废条**。

### 打包，传给训练机
```bash
cd ~/.cache/huggingface/lerobot/fanhao375
tar -czf ~/我的数据集.tar.gz 我的数据集名字     # 用 tar，别用 7z
md5sum ~/我的数据集.tar.gz                       # 记下这个 MD5！
```
> ⚠️ **传过去后训练机上必须核对 MD5 一致**（防传输/打包损坏——我们就被坑过：7z 边编码边打包，把没写完的视频打进去了，训练机一读就报 `moov atom not found`）。
> ⚠️ **别用 7z 在录制刚结束时打包**（视频可能还没编码完）。

---

## 三、第②步：训练模型（在 GPU 机器上）

> 这步在**有显卡的训练机**做（我们用 5060Ti + WSL2）。把上一步的 `.tar.gz` 拷过去。

### 解压数据到 lerobot 能找到的地方
```bash
md5sum 我的数据集.tar.gz     # 先核对 MD5 和采集机一致！
mkdir -p ~/.cache/huggingface/lerobot/fanhao375
tar -xzf 我的数据集.tar.gz -C ~/.cache/huggingface/lerobot/fanhao375/
```

### 开始训练
```bash
HF_HUB_OFFLINE=1 lerobot-train \
  --dataset.repo_id=fanhao375/我的数据集名字 \
  --policy.type=act \
  --output_dir=outputs/train/我的模型 \
  --batch_size=8 --steps=80000 \
  --policy.device=cuda \
  --dataset.video_backend=pyav \
  --wandb.enable=false
```
**说人话：**
- `--policy.type=act`：用 **ACT** 算法（适合这种抓取任务的经典模仿学习模型，约 5000 万参数）
- `--steps=80000`：训练 8 万步（我们 5 万步 loss 就到 0.063 了）
- `--video_backend=pyav`：视频解码用 pyav（比默认的 torchcodec 在多进程下稳）
- `HF_HUB_OFFLINE=1`：纯用本地数据，不联网

### 训练时看什么
- **loss（损失）一路往下掉** = 在学（我们从 6.8 → 0.063）。loss 越低，模型越"贴合"你的示范。
- 每隔一段存一个 **checkpoint**（断点），在 `outputs/train/我的模型/checkpoints/`。
- 看到 **`End of training`** = 训练正常跑完。

### 断点续训（中途断了不怕）
训练几小时，中途**电脑睡眠/关 WSL** 会把训练打断。续训：
```bash
lerobot-train --config_path=outputs/train/我的模型/checkpoints/last/pretrained_model/train_config.json --resume=true
```
> ⚠️ 训练期间把 **Windows 睡眠设成"从不"**（WSL 会随宿主睡眠挂起）。

### 打包模型，传回采集机
**部署只需要 `pretrained_model/` 这个子目录**（约 200M；那个 591M 的是带优化器的、只续训才用）：
```bash
cd outputs/train/我的模型/checkpoints/0080000/
tar -czf ~/我的模型.tar.gz pretrained_model
md5sum ~/我的模型.tar.gz
```

---

## 四、第③步：部署（让机械臂自己干）

> 回到**采集那台 Linux**，接好真机械臂。把 `我的模型.tar.gz` 拷回来。

### 解压模型
```bash
md5sum 我的模型.tar.gz      # 核对 MD5
mkdir -p ~/act_models
tar -xzf 我的模型.tar.gz -C ~/act_models/
# 模型路径 = ~/act_models/pretrained_model
```

### 启动部署
**和采集命令几乎一样，就是把 `--teleop.*` 换成 `--policy.path`**（不再遥操作，模型自己出动作）：
```bash
conda activate lerobot
lerobot-record \
  --robot.type=seeed_b601_dm_follower --robot.port=/dev/ttyACM0 --robot.id=follower1 --robot.can_adapter=damiao \
  --robot.cameras="{ top: {type: opencv, index_or_path: /dev/v4l/by-id/usb-Insta360_Insta360_Link_2-video-index0, width: 1280, height: 720, fps: 30, fourcc: MJPG, warmup_s: 6}, wrist: {type: opencv, index_or_path: /dev/v4l/by-path/pci-0000:00:14.0-usb-0:8.2:1.4-video-index0, width: 640, height: 480, fps: 30, fourcc: MJPG, warmup_s: 3}}" \
  --policy.path=/home/pc/act_models/pretrained_model \
  --dataset.repo_id=fanhao375/eval_测试 --dataset.single_task="把积木放进盒子" \
  --dataset.num_episodes=3 --dataset.episode_time_s=30 --dataset.reset_time_s=10 \
  --dataset.push_to_hub=false
```

### ⚠️ 安全（自主运动，务必！）
- **手一直放在电源开关上** —— 模型不一定准，可能会撞/抖，随时准备断电
- **工作区清空、手别伸进去**，桌上摆好一块积木
- 出问题 → 立刻断电，或在终端 `Ctrl-C`（会优雅断开、关扭矩、夹爪松开，臂会变软，**扶住**）

### 怎么算成功
- 601 自己动起来、靠近积木、夹住、移向盒子、张开 = 全程跑通
- 我们第一次：**抓✅ 放❌**（夹爪不松开）——这是数据问题（"松开"教得不够），不是部署 bug。下次采集强化"松开"动作 + 多采数据就能修。

---

## 五、常见坑速查表（我们踩过的）

| 现象 | 原因 | 解决 |
|---|---|---|
| 连接时 `Timed out waiting for frame` | 相机首帧慢（Insta360 要 2.7 秒） | 加 `warmup_s: 6` |
| 双相机一起跑 Gemini 卡死 | USB 2.0 带宽被抢 | Gemini 加 `fourcc: MJPG`（压缩） |
| Insta360 设 640x480 报错 | 它 MJPG 只支持 1280x720 | 俯视就用 1280x720 |
| 录制延时大、~14fps | rerun 显示 + 大图写盘拖累 | 别开 `--display_data`、加 `num_image_writer_processes=2` |
| 一按 → 程序崩 `You must add one or several frames` | 0 帧 episode | **先动臂采到帧再按 →** |
| 每条之间卡 40-80 秒 | CPU 编码视频慢（固有） | 录短点（任务做完即按 →）；601 卡住=在编码，别动 |
| `--dataset.video=false` 录完没画面 | 这版它会**剔除相机只留关节** | **要画面必须 `video=true`** |
| 训练机报视频 `moov atom not found` | 7z 边编码边打包/传输截断 | 用 tar、核对 MD5、别在编码没完时打包 |
| 删条后视频变 AV1 解不动 | 删除工具默认转 av1 | monkeypatch 强制 h264（见技术速记） |
| 部署 `ensure_mode register 10 write ack` 失败 | **从臂电机电源没开** | 开达妙供电（电机红灯常亮）再跑 |
| Insta360 `lsusb` 找不到 | USB 接触不良/松了 | 重插（插到底、换 USB3.0 口/换线） |

---

## 六、名词小词典（完全新手看这里）

- **模仿学习 / Imitation Learning**：给 AI 看人类示范，让它模仿。我们这套就是。
- **ACT**：一种模仿学习的模型结构，适合机械臂抓取，预测"接下来一小段连续动作"。
- **episode（一条 / 一集）**：一次完整的任务演示（抓一次放一次）。数据集 = 几十条 episode。
- **observation（观测）**：模型的"眼睛和本体感觉"——相机画面 + 关节角度。
- **action（动作）**：模型/你输出的指令——让关节转到哪。
- **checkpoint（断点 / 存档）**：训练到某一步存下的模型快照，可续训、可部署。
- **loss（损失）**：模型预测和你示范的差距，越小越贴合。
- **遥操作 / teleoperation**：你拖主臂、从臂跟着动（用来采数据）。
- **部署 / 推理 / inference**：模型自己上岗干活（不再有人遥操作）。
- **leader / follower（主臂 / 从臂）**：leader=你手动拖的 102，follower=干活的 601。

---

**一句话总结**：`lerobot-record`(采) → `lerobot-train`(训) → `lerobot-record --policy.path`(部署)，这就是 LeRobot 官方全套。教材（数据）质量决定一切——多采、演清楚关键动作、位置多变化，AI 就能学会。
