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
| 快速启动 | **开着**（HiberbootEnabled=1） | ⚠️ 装前必关（见 §1.3 / 下方命令） |
| BitLocker | 读不到（需管理员确认；组装台式机大概率没开） | 🟡 装前用管理员跑 `manage-bde -status C:` 确认 |

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
| ⭐高 | BitLocker 是否开 | 🟡 待管理员 `manage-bde -status C:` 确认（组装台式机大概率没开） |
| ⭐高 | 关快速启动 | 🟡 待跑 ★ 节那条 reg 命令（当前 HiberbootEnabled=1 开着） |
| 中 | Ubuntu 分多大 | ✅ 定 150G，从 D: 末尾压（`153600`） |
| 中 | 装完验证官方 teleoperate 不再卡 2Hz | ⬜ 装完做 |
| 低 | 上原生后回收 WSL 占的 40G（D:\WSL） | ⬜ 稳定后清 |

---

## 11. 参考链接

- [Ubuntu 22.04 LTS 下载（官方）](https://releases.ubuntu.com/22.04/) / [Ubuntu Desktop 下载页](https://ubuntu.com/download/desktop)
- [Rufus（启动盘工具）](https://rufus.ie/)
- 本仓：[`LeRobot_Arm102LD_B601DM遥操作小白执行手册.md`](./LeRobot_Arm102LD_B601DM遥操作小白执行手册.md) / [`Gemini2视觉抓取上手指南.md`](./Gemini2视觉抓取上手指南.md) / [`遥操作与LeRobot待办.md`](./遥操作与LeRobot待办.md)
