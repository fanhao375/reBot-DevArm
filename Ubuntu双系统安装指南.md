# Ubuntu 22.04 双系统安装指南（Windows 用户向）

> 给自己看的实操笔记。在一台 **Windows + 单块 SSD** 的电脑上，**压缩 C 盘分出空间，装 Ubuntu 22.04 双系统**，到能跑机器人为止。
> 建立时间：2026-06-13
> 触发：WSL 走 usbipd-win 转 USB，**每帧逐电机读 feedback 的往返延迟太大**（实测官方 `lerobot-teleoperate` 在 WSL 下 ~614ms / 2Hz + 反复 timeout）。官方闭环遥操作 + Gemini2/YOLO 抓取 demo 都要**原生 Linux**。详见 [`遥操作与LeRobot待办.md`](./遥操作与LeRobot待办.md) §平行支线 + [`Gemini2视觉抓取上手指南.md`](./Gemini2视觉抓取上手指南.md)。
>
> 适用：**就在 D:\Robot 这台遥操作机上做**（组装台式机、单块 477G SATA SSD，从 D: 末尾压分区装双系统）。本机实测配置与定制方案见下方 ★ 节。

**符号约定**：🟢 照做 / 🟡 看你机器 / ⚠️ 不做会出事 / ❓ 不确定

> ⚠️ **先读一遍再动手**。动分区有风险，照 §1 把 3 个安全项做了再装。装完每次开机会跳菜单让你选 Ubuntu 还是 Windows，**Windows 不会丢**。

---

## ★ 本机配置 & 定制方案（D:\Robot 这台，2026-06-18 实测）

> 目标改为**就在这台遥操作机上装双系统**（不是当初设想的另一台）。以下是直接读硬件得出的实情和定制方案。

| 项 | 实测 | 结论 |
|---|---|---|
| 机型 | 组装台式机（SMBIOS 是 "Default string"），主板 **Intel SKYBAY**，BIOS 5.12 (2020) | 台式机，随时重试启动键无压力 |
| 启动固件 | **UEFI** + 磁盘 **GPT** | Rufus 用 **GPT/UEFI**；Ubuntu 走 UEFI 安装 |
| 硬盘 | 单块 **477GB SATA SSD**（SATA CVB-CD512） | 单盘双系统，符合本指南场景 |
| 分区 | EFI 0.3G / MSR / **C: 225G(剩165G)** / **D: 251G(剩207G，末尾分区)** | ⭐ **从 D: 末尾压空间最干净** |
| 页面文件 | 在 **C:\pagefile.sys**（不在 D:） | 压 D: 不会被页面文件挡 ✅ |
| D: 占用 | 仅 ~44G（其中 **WSL 占 40G**，上原生后可删回收） | 压 150G 绰绰有余 |
| 内存 | 16 GB | swap 给 8~16G |
| 快速启动 | ✅ **已关**（2026-06-18 reg HiberbootEnabled=0） | 完成 |
| BitLocker | ✅ **没开**（2026-06-18 manage-bde：版本=无、完全解密、保护关闭） | 完成，盘可安全动 |

**本机定制方案**：
1. **空间从 D: 末尾压 150GB**（D: 是磁盘最后一个分区，压出来的未分配空间正好在盘尾，Ubuntu 安装器最好认）。C:(Windows) 完全不动。磁盘管理 → 右键 D: → 压缩卷 → 输 `153600`。
2. **启动键**：Intel 主板，开机狂按 **F10（启动菜单）**；进 BIOS 设置是 **F2 / Del**。认不到就看开机自检画面提示的键，或试 F12/F8/Esc（台式机随便重试）。
3. **Rufus**：GPT / UEFI（默认即对）。
4. **安装**：§6 选"与 Windows Boot Manager 共存"，自动用盘尾那 150G。swap 8~16G。
5. 装完照 §8：原生设备直连，conda 装 `motorbridge==0.4.7`。

**装前两件必做（需管理员 PowerShell）**：
```powershell
# 右键“以管理员身份运行” PowerShell
manage-bde -status C:     # 看 BitLocker：Conversion Status 显示 "Fully Decrypted" = 没开，安全
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v HiberbootEnabled /t REG_DWORD /d 0 /f   # 关快速启动
```

---

## 0. 装完长啥样（先消除恐惧）

开机先出一个菜单（GRUB），方向键选、回车进：
```
*Ubuntu
 Windows Boot Manager
（默认 10 秒进第一个）
```
- 跑机器人 → 选 Ubuntu
- 干别的 → 选 Windows Boot Manager
- 两系统各占各的分区，文件都在，互不影响。

---

## 1. ⚠️ 动手前必做的 3 件安全事（Windows 这台上操作）

### 1.1 备份重要文件
分区正常不丢数据，但万一。重要东西先拷到移动硬盘/网盘。

### 1.2 关 BitLocker（最容易锁死自己的雷）
- 开始菜单搜 **"BitLocker"** 或 **"设备加密"**。
- 如果 C 盘是"已开启/已加密"，**先关闭（解密）或至少导出恢复密钥**。
- ⚠️ 不关的话，装完双系统**开机可能要你输一长串恢复密钥，输不出就进不去 Windows**。
- 关闭后等它"解密完成"再继续。

### 1.3 关 Windows 快速启动（Fast Startup）
- 控制面板 → 硬件和声音 → 电源选项 → **"选择电源按钮的功能"** → 点 **"更改当前不可用的设置"** → **取消勾选"启用快速启动"** → 保存。
- ⚠️ 不关的话 Linux 可能读不了/搞坏共享分区。

---

## 2. 在 Windows 里压缩 C 盘，腾出空间给 Ubuntu

1. 右键 **"此电脑" → 管理 → 磁盘管理**（或开始菜单搜"创建并格式化硬盘分区"）。
2. 右键 **C: 盘 → 压缩卷（Shrink Volume）**。
3. 输入压缩量（MB）：
   - 🟢 **建议 ≥ 100 GB = 输入 `102400`**（只遥操作够用）
   - ⭐ 要采数据/训练/装 YOLO 模型 → **150~200 GB（`153600`~`204800`）**更稳
4. 压缩后会多出一块 **"未分配（黑色条）"** 空间——**别动它、别格式化**，留给 Ubuntu 安装器自己用。

> 🟡 压缩不出那么大？多半是 Windows 末尾有不可移动文件，先关休眠（管理员 CMD 跑 `powercfg /h off`）+ 关 BitLocker + 重启再压。

---

## 3. 去哪下载（两个文件）

| 下载啥 | 地址 | 说明 |
|---|---|---|
| **Ubuntu 22.04.5 LTS 桌面版 ISO**（~5GB） | [releases.ubuntu.com/22.04/](https://releases.ubuntu.com/22.04/) 选 `ubuntu-22.04.5-desktop-amd64.iso`；或 [ubuntu.com/download/desktop](https://ubuntu.com/download/desktop) | ⭐ **要 22.04**（对得上 Seeed lerobot 0.4.4），不是 24.04 |
| **Rufus**（做启动盘的小工具） | [rufus.ie](https://rufus.ie/) 下 `rufus-x.x.exe`（便携版免安装） | Windows 上把 ISO 写进 U 盘 |

还要准备：一个 **≥8GB 的 U 盘**（做启动盘会**清空它**，里面东西先拷走）。

---

## 4. 用 Rufus 把 ISO 写进 U 盘（做启动盘）

1. 插 U 盘，打开 Rufus。
2. **设备**：选你那个 U 盘（别选错成移动硬盘！）。
3. **引导类型选择**：点"选择"，挑刚下的 `ubuntu-22.04.5-desktop-amd64.iso`。
4. **分区类型**：🟡 现代电脑选 **GPT**（UEFI）；很老的机器才用 MBR。一般默认就对。
5. 点 **"开始"** → 弹"以 ISO 镜像模式写入" → 默认确定 → 警告会清空 U 盘 → 确定。
6. 等进度跑完（几分钟），关掉。

---

## 5. 从 U 盘启动那台电脑

1. U 盘**插着**，重启电脑。
2. 开机一出现 logo，**狂按启动菜单键**（按品牌）：
   | 品牌 | 启动菜单键 |
   |---|---|
   | 联想 Lenovo | F12（或 Fn+F12）|
   | 戴尔 Dell | F12 |
   | 惠普 HP | F9（BIOS 是 Esc/F10）|
   | 华硕 ASUS | F8 或 Esc |
   | 微星 MSI / 技嘉 Gigabyte | F11 / F12 |
   | 宏碁 Acer | F12 |
3. 菜单里选 **带 "USB" / U 盘名 / "UEFI: U盘"** 那一项，回车。
4. 进到 Ubuntu 界面，选 **"Try or Install Ubuntu"**。

> 🟡 **Secure Boot**：Ubuntu 22.04 支持，一般**不用关**。要是 U 盘启动失败，进 BIOS（开机按 Del/F2）把 Secure Boot 关掉再试。

---

## 6. 安装 Ubuntu（关键一步：选"和 Windows 共存"）

1. 语言选中文/英文 → **Install Ubuntu**。
2. 键盘默认、联网（可跳过）、**"Normal installation"**，勾上 "Download updates"（可选）。
3. ⭐ **安装类型——最重要的一屏**：
   - 选 **"Install Ubuntu alongside Windows Boot Manager"（与 Windows 共存）** ← **新手选这个**
   - 它会**自动用你 §2 压出来的未分配空间**装 Ubuntu，**不动 Windows 分区**，引导也自动配好。
   - ⚠️ **千万别选** "Erase disk and install Ubuntu"（那是**抹掉整盘**，Windows 没了）！
   - 🟡 如果没出现"共存"选项（有时认不到），就选 **"Something else（手动）"**，在那块**未分配空间**上手动建：`/`（根，ext4，≥40GB）、`swap`（≈内存大小，可选）、剩下给 `/home`——这步不确定就**停下来问我**，别瞎点。
4. 拖滑块分配 Windows/Ubuntu 空间（用共存模式时）→ **Install Now** → 确认写入。
5. 设时区、用户名密码（**记牢这个密码，以后 `sudo` 要用**）。
6. 装完 → 重启 → **拔掉 U 盘** → 回车。

---

## 7. 开机选系统（GRUB）

重启后出 GRUB 菜单：
- 选 **Ubuntu** 进 Linux
- 选 **Windows Boot Manager** 回 Windows

> 🟡 **如果重启直接进了 Windows、没看到菜单**：UEFI 启动顺序把 Windows 排前面了。开机进 BIOS（Del/F2）→ Boot 顺序把 **ubuntu** 调到第一；或每次开机用启动菜单键临时选 ubuntu。

---

## 8. 装完之后：接机器人（指回已有指南）

进了 Ubuntu，USB-CAN / 相机**直接插就是原生设备**（`/dev/ttyACM*`、`/dev/ttyUSB*`、相机），**没有 WSL 那套 usbipd 延迟了**。接下来：

1. **遥操作环境**（102 + B601 LeRobot）：照 [`LeRobot_Arm102LD_B601DM遥操作小白执行手册.md`](./LeRobot_Arm102LD_B601DM遥操作小白执行手册.md) 装 Seeed 路线（Miniforge + conda env `lerobot` + lerobot 0.4.4）。
   - 🟢 原生 Linux 下官方 `lerobot-teleoperate` 的每帧 feedback 应该不再卡 2Hz（这正是上原生的原因）。
2. **Gemini2 + YOLO 抓取 demo**：照 [`Gemini2视觉抓取上手指南.md`](./Gemini2视觉抓取上手指南.md)（pyorbbecsdk + 手眼标定 + 抓取）。相机直连，不用再 usbipd 透传。
3. **wheel**：这台新 Ubuntu 的 conda 环境记得 `pip install -U motorbridge==0.4.7`（跟主仓 `baseline-2026-06-18` 对齐；v0.4.7 含 dm-serial 超时放宽 1ms→10ms + 达妙模式切换加固，正好对症之前 WSL 下的串口写超时）。

---

## ★ 装完实战踩坑：联网代理 + Claude Code / git 上 Linux（2026-06-19 实录）

> 🟢 **双系统装成功（2026-06-19）**：研华 **MIC-7700Q** 工业机，**从 BIOS「Boot」标签**把 U 盘（`UEFI: Lenovo UFD X3CPro`）设第一启动（不是 F10）→ 与 Windows Boot Manager 共存 → 安装器在盘尾 150G 新建**第 5 分区(ext4)** → 用户名 `pc` / 密码 `admin123`（用户名 `pc` 正好对上手册里 `/home/pc/...` 路径）。

装完联网/装工具踩了一整天坑，**核心教训记下来**：

### 1. ⚠️ Linux 上 GUI 和终端是两套独立的"走不走代理"机制
- **浏览器**自动读"系统代理"设置 → 开了系统代理就能上外网。
- **终端 curl/npm 不读系统代理** → 默认直连撞墙，报 `SSL routines::unexpected eof while reading`。
- 要让终端走代理：① `export https_proxy=http://127.0.0.1:端口` ② 或开**透明代理/TUN**（网络层全接管，推荐）。

### 2. ⚠️ Clash Verge 不稳，换 v2rayA 才搞定终端代理
- Clash Verge 反复切「系统代理/TUN」会把核心状态搞坏（[已知 bug #2767/#6380](https://github.com/clash-verge-rev/clash-verge-rev/issues/2767)）；加上节点不稳 + OpenSSL 3.0 严格 → 间歇性 `unexpected eof`（[curl #5138](https://github.com/curl/curl/issues/5138) / [Xray #1485](https://github.com/XTLS/Xray-core/issues/1485)，浏览器自动重试所以没事、curl 不重试就报错）。
- **✅ 解法：装 v2rayA**（`installer_debian_x64_*.deb`，apt 装）+ 用现成 v2ray-core（`/usr/local/bin/v2ray` + `/usr/local/share/v2ray/*.dat`）+ 导**「Trojan 通用订阅」**+ 关键设置：
  - **透明代理/系统代理 = 启用: 不进行分流**（全走代理，不让流量漏直连被掐）
  - **防止DNS污染 = 转发DNS请求**
  - → 终端代理通：`curl -I https://api.anthropic.com` 出 **`HTTP/2 403`**（403=摸到 Anthropic 了，对的）。
- ⚠️ **节点选低延迟美/日**（英国 IEPL 761ms 太慢、丢包抽风）；curl 加 **`--retry 5 --retry-all-errors`** 自动重试穿过抽风。

### 3. 🟢 Claude Code 上 Linux：走 npm 绕开被地区拦的 claude.ai
- `claude.ai/install.sh` 被**地区拦**（返回 `App unavailable in region` 网页），但 `api.anthropic.com` 通（Claude Code 运行时用的是它）。
- **✅ 解法：npm 装，不碰 claude.ai**：
  ```bash
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -   # 装 Node 20（NodeSource）
  sudo apt install -y nodejs
  sudo npm config set registry https://registry.npmmirror.com        # npm 换国内镜像
  sudo npm install -g @anthropic-ai/claude-code
  claude --version                                                    # 验证
  ```
- 🟡 **待办：`claude` 首次登录**——claude.ai 被地区拦，OAuth 登录可能要换节点 / 或用 API key（下次处理）。

### 4. 🟢 git 等常用工具：apt 直接装（已是清华镜像）
```bash
sudo apt install -y git    # apt 走 mirrors.tuna.tsinghua.edu.cn，快、不用代理
```

---

## 9. ⚠️ 避雷速查

| 现象 | 解法 |
|---|---|
| 装完开机要 BitLocker 恢复密钥 | 没提前关 BitLocker → 输你导出的恢复密钥进 Windows，再关掉 BitLocker |
| 压缩卷压不出大空间 | `powercfg /h off` 关休眠 + 关 BitLocker + 重启再压 |
| U 盘启动不了 | BIOS 关 Secure Boot；确认 Rufus 用了 GPT/UEFI；换 USB 口（用 2.0 口有时更稳） |
| 重启没 GRUB 菜单直进 Windows | BIOS 里把 ubuntu 启动项调到第一 |
| 没看到"与 Windows 共存"选项 | 确认 §2 留了未分配空间 + 关了快速启动；实在没有走"Something else"手动分区（不确定先问） |
| Ubuntu 里看不到 Windows 的文件/盘打不开 | Windows 没关快速启动（回 Windows 关掉，别用"休眠/快速关机"） |

---

## 10. 待办 / 未知 🟡

| 优先级 | 事项 | 状态 |
|---|---|---|
| ⭐高 | 机型/启动键 | ✅ 已实测：Intel SKYBAY 主板，F10 启动菜单 / F2-Del 设置（见 ★ 节） |
| ⭐高 | BitLocker 是否开 | ✅ 2026-06-18 确认没开（完全解密/保护关闭），盘可安全动 |
| ⭐高 | 关快速启动 | ✅ 2026-06-18 已关（HiberbootEnabled=0） |
| 中 | Ubuntu 分多大 + 压分区 | ✅ **已压**：D: 251.5→101.5G，盘尾 **150G 未分配**到位（2026-06-18，Resize-Partition） |
| 中 | 下载 ISO + Rufus + ≥8G U 盘 | ✅ ISO(desktop 4.4G) + Rufus 4.14 + X3CPRO 32G U 盘就位 |
| 中 | Rufus 做启动盘 | ✅ 设好 GPT/UEFI(非CSM) 写盘（2026-06-18） |
| ⭐高 | 进 U 盘 → 共存安装 | ✅ **完成（2026-06-19）**：BIOS Boot 标签设 U 盘启动 → 共存 → 盘尾第5分区 ext4 → 用户 `pc`/`admin123`（见 ★ 节） |
| ⭐高 | 联网代理（终端能走代理） | ✅ **完成**：Clash 不稳 → 换 **v2rayA**（透明代理"不进行分流"+防DNS污染），`curl api.anthropic.com` 出 403（见 ★ 节） |
| ⭐高 | Claude Code 上 Linux | ✅ **装上**（npm 绕开被地区拦的 claude.ai）；🟡 `claude` 登录待处理 |
| 中 | git | ✅ `sudo apt install -y git`（清华镜像） |
| ⭐高 | 遥操作环境（Miniforge+conda lerobot+motorbridge 0.4.7）| ⬜ 待装（照执行手册）|
| 中 | 装完验证官方 teleoperate 不再卡 2Hz | ⬜ 装完做 |
| 低 | 上原生后回收 WSL 占的 40G（D:\WSL） | ⬜ 稳定后清 |

---

## 11. 装完后异地远程访问（机器人机 ↔ 你的笔记本）

> 想从外地 / 另一台笔记本远程操作这台 Ubuntu 机器人机。**异地（不在同一局域网）也能连**，方法见下。

**⚠️ 先认清边界**：遥操作要用手摆主臂 Arm102（主从臂都插在这台机器上），**动臂必须人在现场**，远程替不了。异地远程能做的是：开关脚本、看运行画面/数据、采集后训练模型、调试、传文件——**不能异地手控机械臂动**。

| 方案 | 干啥 | 说明 |
|---|---|---|
| 🥇 **Tailscale + SSH** | 命令行主力 | 两台都装 Tailscale 登同账号 → 各得虚拟 IP(`100.x`) → 异地变同局域网 → SSH 连虚拟 IP，跟在家一个 WiFi 下一样。免费、低延迟、不用动路由器 |
| Tailscale + **NoMachine** | 图形桌面 | 要看 MeshCat 仿真 / 相机画面时，NoMachine 连那个虚拟 IP |
| **向日葵 / RustDesk / TeamViewer** | 纯图形零配置 | Ubuntu+Windows 都有版本，装上登录输 ID+密码就连，最省心；国内向日葵最稳，开源选 RustDesk |

**推荐组合**：跑训练 / 采数据 / 监控 / 传文件用 **Tailscale + SSH**；偶尔要图形界面再加 **NoMachine 或向日葵**。装完系统再配（Tailscale ~5 分钟搞定）。

---

## 12. 参考链接

- [Ubuntu 22.04 LTS 下载（官方）](https://releases.ubuntu.com/22.04/) / [Ubuntu Desktop 下载页](https://ubuntu.com/download/desktop)
- [Rufus（启动盘工具）](https://rufus.ie/)
- 本仓：[`LeRobot_Arm102LD_B601DM遥操作小白执行手册.md`](./LeRobot_Arm102LD_B601DM遥操作小白执行手册.md) / [`Gemini2视觉抓取上手指南.md`](./Gemini2视觉抓取上手指南.md) / [`遥操作与LeRobot待办.md`](./遥操作与LeRobot待办.md)
