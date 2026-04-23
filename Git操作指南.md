# Git 操作指南 — 零基础 Fork 开源项目

> 本文档记录如何 Fork 一个开源项目、添加自己的内容、并保持与官方同步。
> 以本仓库（reBot-DevArm）为实际案例，适合完全不懂 Git 的新手。

---

## 为什么要 Fork？

当你想学习一个开源项目，并在上面添加自己的笔记、文档、改进时，有三种做法：

| 做法 | 优点 | 缺点 |
|------|------|------|
| **直接下载 ZIP** | 简单 | 无法同步官方更新，无法分享给别人 |
| **直接 Clone 官方仓库** | 能拉取更新 | 无法推送自己的修改（没有权限） |
| **Fork 到自己账号** ✅ | 能改、能推送、能同步、能分享 | 需要学一点 Git |

**Fork = 在 GitHub 上复制一份到你的账号，你拥有完全控制权。**

---

## 第一步：在 GitHub 上 Fork 仓库

### 1.1 打开官方仓库

访问你想 Fork 的项目，例如：
```
https://github.com/Seeed-Projects/reBot-DevArm
```

### 1.2 点击右上角的 "Fork" 按钮

![Fork 按钮位置](https://docs.github.com/assets/cb-40742/mw-1440/images/help/repository/fork-button.webp)

### 1.3 填写 Fork 信息

- **Owner**：你的 GitHub 用户名（自动选中）
- **Repository name**：保持和官方一样就行（例如 `reBot-DevArm`）
- **Description**：官方的描述会自动复制过来
- **Copy the main branch only**：✅ 勾选（只复制主分支，够用了）

![Fork 创建页面示例](https://i.imgur.com/example.png)

### 1.4 点击 "Create fork"

等待几秒，GitHub 会自动复制整个仓库到你的账号下。

完成后，你会看到：
- URL 变成了 `https://github.com/你的用户名/reBot-DevArm`
- 顶部显示 "forked from Seeed-Projects/reBot-DevArm"

---

## 第二步：把本地仓库关联到你的 Fork

### 2.1 如果你还没有本地仓库

直接 Clone 你的 Fork：
```bash
git clone --recurse-submodules https://github.com/你的用户名/reBot-DevArm.git
cd reBot-DevArm
```

然后添加官方仓库作为 upstream（方便以后同步）：
```bash
git remote add upstream https://github.com/Seeed-Projects/reBot-DevArm.git
```

如果你已经先用普通 `git clone` 拉下来了，也可以补执行：
```bash
git submodule update --init --recursive
```

### 2.2 如果你已经有本地仓库（本文档的情况）

查看当前 remote 配置：
```bash
git remote -v
```

如果显示的是官方仓库，需要改成你的 Fork：
```bash
# 将 origin 改为你的 Fork
git remote set-url origin https://github.com/你的用户名/reBot-DevArm.git

# 添加官方仓库为 upstream
git remote add upstream https://github.com/Seeed-Projects/reBot-DevArm.git
```

再次检查：
```bash
git remote -v
```

应该显示：
```
origin    https://github.com/你的用户名/reBot-DevArm.git (fetch)
origin    https://github.com/你的用户名/reBot-DevArm.git (push)
upstream  https://github.com/Seeed-Projects/reBot-DevArm.git (fetch)
upstream  https://github.com/Seeed-Projects/reBot-DevArm.git (push)
```

**理解**：
- `origin` = 你的 Fork（你有写权限，可以 push）
- `upstream` = 官方仓库（只读，用来同步更新）

---

## 第三步：配置 Git 用户信息（首次使用）

Git 需要知道你是谁，才能记录提交者信息：

```bash
git config --global user.name "你的GitHub用户名"
git config --global user.email "你的邮箱"
```

例如：
```bash
git config --global user.name "fanhao375"
git config --global user.email "fanhao375@gmail.com"
```

**注意**：邮箱要和 GitHub 账号绑定的邮箱一致，或者使用 GitHub 提供的隐私邮箱：
```
你的用户名@users.noreply.github.com
```

---

## 第四步：提交你的修改

### 4.1 查看当前状态

```bash
git status
```

会显示哪些文件被修改了、哪些是新文件。

### 4.2 添加文件到暂存区

```bash
# 添加所有修改
git add .

# 或者只添加特定文件
git add 项目总览.md 操作日志.md
```

### 4.3 提交到本地仓库

```bash
git commit -m "添加学习笔记和补充资料"
```

**提交信息建议**：
- 第一行简短说明（50 字以内）
- 空一行
- 详细说明（可选）

例如：
```bash
git commit -m "添加学习笔记和补充资料

- 新增项目文档体系（项目总览/操作日志/学习笔记）
- 补充硬件资料（电机说明书、硬件总结）
- 新增完整文档中心（docs/）
- 抓取并修复 8 个 wiki 教程页面

本仓库 Fork 自 Seeed-Projects/reBot-DevArm
标注 ★ 的内容为个人学习补充，非官方资料"
```

---

## 第五步：推送到 GitHub

### 5.1 首次推送

```bash
git push -u origin main
```

`-u` 参数会设置上游分支，以后只需要 `git push` 就行。

### 5.2 如果推送被拒绝

可能是因为远程仓库有你本地没有的提交（比如你 Fork 后官方又更新了）。

解决方法：
```bash
# 拉取远程更新并变基
git pull origin main --rebase

# 同步子模块到主仓库记录的版本
git submodule update --init --recursive

# 再次推送
git push
```

### 5.3 推送成功

访问你的 GitHub 仓库，刷新页面，应该能看到你的提交了。

---

## 第六步：同步官方仓库的更新

官方仓库会不断更新，你需要定期同步到你的 Fork。

### 6.1 拉取官方更新

```bash
git pull upstream main
```

这会把官方 `main` 分支的最新提交合并到你的本地。

### 6.2 推送到你的 Fork

```bash
git submodule update --init --recursive
git push origin main
```

这样你的 GitHub Fork 也同步了官方的最新内容。

### 6.3 完整流程（推荐）

```bash
# 1. 确保在 main 分支
git checkout main

# 2. 拉取官方更新
git pull upstream main

# 3. 推送到你的 Fork
git push origin main
```

---

## 常见问题

### Q1: 我改了文件，但 `git status` 显示很多不相关的修改？

可能是换行符问题（Windows 用 CRLF，Linux/Mac 用 LF）。

解决方法：
```bash
# 让 Git 自动处理换行符
git config --global core.autocrlf true
```

### Q2: 提示 "embedded git repository"？

你添加的文件夹里有 `.git` 子目录（嵌套仓库）。

**本仓库当前已正式使用 submodule 管理这些外部项目：**
- `software/MotorBridge`
- `software/reBotArm_control_py`
- `遥操作/StarArm_102`

所以对这些目录，不要再手动删 `.git` 或重新 `git add` 整个目录。

如果你需要长期修改某个 submodule，正确流程是：
1. 先 fork 那个子仓库到自己账号
2. 在子仓库里提交并推送修改
3. 回到主仓库，更新 `.gitmodules`（如需改到你的 fork）和 submodule 指针
4. 再提交主仓库

两种处理方式：
1. **作为子模块**（推荐，如果是外部项目）：
   ```bash
   git rm --cached software/MotorBridge
   git submodule add https://github.com/tianrking/MotorBridge software/MotorBridge
   ```

2. **直接包含代码**（如果你要修改它）：
   ```bash
   rm -rf software/MotorBridge/.git
   git add software/MotorBridge
   ```

如果你只是拉了主仓库但目录是空的，正确做法是：
```bash
git submodule update --init --recursive
```

### Q3: 推送时要求输入用户名密码？

GitHub 已经不支持密码登录了，需要用 Personal Access Token (PAT)。

**方法 1：使用 SSH（推荐）**
```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "你的邮箱"

# 添加到 GitHub：Settings → SSH and GPG keys → New SSH key
# 然后改用 SSH URL
git remote set-url origin git@github.com:你的用户名/reBot-DevArm.git
```

**方法 2：使用 Personal Access Token**
1. GitHub → Settings → Developer settings → Personal access tokens → Generate new token
2. 勾选 `repo` 权限
3. 复制生成的 token
4. 推送时用 token 代替密码

### Q4: 如何撤销还没 push 的提交？

```bash
# 撤销最后一次提交，但保留修改
git reset --soft HEAD~1

# 撤销最后一次提交，丢弃修改
git reset --hard HEAD~1
```

### Q5: 我想删除 Fork，重新来？

GitHub 仓库页面 → Settings → 拉到最底部 → Delete this repository

---

## 开源协议注意事项

本项目使用 **CC BY-NC-SA 4.0** 协议，你需要遵守：

| 要求 | 说明 |
|------|------|
| **Attribution（署名）** | 必须标明原作者和来源 |
| **NonCommercial（非商用）** | 不能用于商业目的 |
| **ShareAlike（相同方式共享）** | 你的衍生作品也必须用相同协议 |

**Fork 自动满足这些要求**：
- GitHub 会显示 "forked from 官方仓库"（署名）
- 协议文件 `LICENSE` 会自动继承（相同方式共享）
- 只要你不卖这个项目，就符合非商用

---

## 推荐工作流程

### 日常开发

```bash
# 1. 修改文件
# 2. 查看修改
git status
git diff

# 3. 提交
git add .
git commit -m "更新说明"

# 4. 推送
git push
```

### 定期同步官方

```bash
# 每周或每次开始工作前
git pull upstream main
git push origin main
```

### 分支开发（进阶）

如果你想尝试大改动，但不想影响主分支：

```bash
# 创建新分支
git checkout -b feature-new-docs

# 修改、提交
git add .
git commit -m "实验性文档"

# 推送到你的 Fork
git push -u origin feature-new-docs

# 如果满意，合并回 main
git checkout main
git merge feature-new-docs
git push
```

---

## 学习资源

- **Git 官方教程**：https://git-scm.com/book/zh/v2
- **GitHub 官方文档**：https://docs.github.com/zh
- **交互式 Git 教程**：https://learngitbranching.js.org/?locale=zh_CN
- **Git 速查表**：https://training.github.com/downloads/zh_CN/github-git-cheat-sheet/

---

## 本文档的由来

这份指南是在 2026-04-14 实际 Fork reBot-DevArm 项目时，根据真实操作过程整理而成。

目标是让零基础的人也能：
1. Fork 一个开源项目
2. 添加自己的学习笔记
3. 推送到 GitHub 分享给别人
4. 保持与官方同步

如果你在操作过程中遇到问题，欢迎提 Issue 或 PR 改进这份文档。

---

**记住**：Git 一开始可能有点难，但掌握这几个命令后，你就能自由地参与开源项目了。加油！🚀
