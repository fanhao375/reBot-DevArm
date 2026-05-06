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
- `software/reBotArmController_ROS2`
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

## 进阶：复刻工程的 Git 操作

> 本章节适合做"复刻工程"（如本仓库）的场景：主仓库 + 多个 submodule，需要长期维护、版本可回滚。
>
> 详见 [`复刻基线维护原则.md`](./复刻基线维护原则.md)。

### 1. 检查上游有没有更新

**主仓库**：
```bash
git fetch upstream
git log HEAD..upstream/main --oneline       # 看上游有几个新 commit
git rev-list --count HEAD..upstream/main    # 数量统计（0 = 无更新）
```

**所有 submodule 一起检查**：
```bash
git submodule foreach 'git fetch && git log HEAD..@{upstream} --oneline | head -5'
git submodule foreach 'git rev-list --count HEAD..@{upstream}'
```

输出 `0` 表示该 submodule 已是最新。

### 2. 把 submodule 切换到自己的 fork

适用场景：原来 submodule 直连原作者仓库，你 fork 后想让主仓库指向自己的 fork（保证依赖永远可控）。

**步骤**：

```bash
# (1) 修改 .gitmodules 中的 url（用编辑器手动改，或用 git config）
# 例：把 software/MotorBridge 的 url 改成你的 fork
git config -f .gitmodules submodule.software/MotorBridge.url \
  https://github.com/你的用户名/motorbridge.git

# (2) 同步 .gitmodules 变更到 .git/config
git submodule sync

# (3) 进入 submodule，把 origin 改成你的 fork，再加一个 upstream 指向原作者
cd software/MotorBridge
git remote set-url origin https://github.com/你的用户名/motorbridge.git
git remote add upstream https://github.com/原作者/motorbridge.git
git remote -v   # 验证

# (4) 验证连通性
git fetch origin
git fetch upstream

# (5) 回主仓库提交 .gitmodules 变更
cd ../..
git add .gitmodules
git commit -m "切换 MotorBridge submodule 到个人 fork"
```

**注意**：
- submodule 锁定的 commit 不变（fork 是从同一 commit 创建的，无需重新 checkout）
- `.git/config` 里的 submodule URL 变化是本地的，不会被 git 跟踪
- `.gitmodules` 才是入库的，必须 commit

### 3. 打 baseline tag（阶段性可复现快照）

适用场景：完成一个阶段性里程碑（比如所有 submodule 都已 fork 并验证），打 tag 锁定这个状态，将来出问题能回滚。

```bash
# 打带说明的 tag（推荐）
git tag -a baseline-2026-04-29 -m "复刻基线 2026-04-29

五个核心仓库的 submodule 锁定状态：
- Seeed/reBot-DevArm: <commit hash>
- fanhao375/motorbridge: <commit hash>
- fanhao375/reBotArm_control_py: <commit hash>
- fanhao375/reBotArmController_ROS2: <commit hash>
- fanhao375/Star-Arm-102: <commit hash>

阶段性可复现基线：所有 submodule 都已 fork 并指向 fanhao375 账号。"

# 查看所有 baseline tag
git tag -l "baseline-*"

# 查看 tag 详情
git show baseline-2026-04-29

# 将来回滚到某个 baseline
git checkout baseline-2026-04-29
git submodule update --init --recursive
```

**push tag 到 GitHub**（需要时）：
```bash
git push origin baseline-2026-04-29       # push 单个 tag
git push origin --tags                    # push 所有 tag
```

### 4. submodule 升级走 sync 分支（不直接在 main 上做）

适用场景：要升级某个 submodule 到新版本，但又怕搞坏复刻基线。

**完整流程**：

```bash
# (1) 在自己的 fork 里合入上游最新代码（在 submodule 目录内）
cd software/MotorBridge
git fetch upstream
git checkout main
git merge upstream/main         # 或 git rebase upstream/main
git push origin main            # 推送到自己的 fork

# (2) 回主仓库，新建 sync 分支（不动 main）
cd ../..
git checkout -b sync/motorbridge-2026-04-29

# (3) 在 sync 分支更新 submodule 指针
cd software/MotorBridge
git pull origin main           # 把 fork 最新拉下来
cd ../..
git add software/MotorBridge   # 主仓库把 submodule 指针更新
git commit -m "升级 MotorBridge submodule 到 <版本号>"

# (4) 跑最小验证（每个仓库的验证门槛见复刻基线维护原则.md）
# - Python 包能装吗？能 import 吗？示例能跑吗？

# (5) 验证通过后合入 main
git checkout main
git merge sync/motorbridge-2026-04-29
git tag -a baseline-<日期> -m "升级 MotorBridge 到 <版本> 后的新基线"

# (6) 验证失败的话直接丢弃 sync 分支
git branch -D sync/motorbridge-2026-04-29
# 然后写记录到 上游更新记录/<日期>_同步详情.md，说明为什么没升
```

### 5. 中文 commit message：用文件而非 HEREDOC

**踩过的坑**：`git commit -m "$(cat <<'EOF' ... EOF)"` 在 Windows 上传中文会出现字符截断乱码（"快照" → "快�"）。

**正确做法**：
```bash
# (1) 把 commit message 写到临时文件
cat > .git/COMMIT_MSG_TEMP.txt <<'EOF'
切换 MotorBridge submodule 到个人 fork

详细说明...

Co-Authored-By: ...
EOF

# (2) 用 -F 指定文件提交
git commit -F .git/COMMIT_MSG_TEMP.txt

# (3) 删除临时文件
rm .git/COMMIT_MSG_TEMP.txt

# (4) 验证 commit message 没乱码
git log -1 --format=%B
```

或者直接用 `Write` 工具写文件，再用 `git commit -F` 提交（更可靠）。

### 6. 撤销刚刚的 commit（还没 push 时）

适用场景：commit 后发现 message 写错了，或者文件没全部加进去。

```bash
# 撤销最后一次 commit，但保留所有改动（最常用）
git reset --soft HEAD~1

# 改完后重新 commit
git commit -F .git/COMMIT_MSG_TEMP.txt
```

**为什么不用 `git commit --amend`？**
- amend 会改写历史 commit，对已 push 的 commit 危险
- 本项目的规则是"创建新 commit 而非 amend"，养成 reset + 重 commit 的习惯更稳

### 7. commit 要分层（不要把多类工作混一起）

**反面教材**：
```
git commit -m "整理电机文档 + 修策略 + 升级 submodule + 改 .gitignore"
```

**正面做法**：分成多个独立 commit
```bash
git commit -m "整理达妙电机说明书为 Markdown"          # 第 1 个
git commit -m "确立复刻基线维护原则"                  # 第 2 个
git commit -m "切换 MotorBridge submodule 到个人 fork"  # 第 3 个
git commit -m "升级 MotorBridge 到 v0.2.4"           # 第 4 个
```

**为什么**：以后用 `git bisect` 定位 bug、用 `git revert` 回滚某个变更时，分层 commit 能精准定位到一类工作，混在一起就只能整体回滚。

### 8. 保护 upstream 不被误推送

适用场景：fork 后在 submodule 里加了 upstream remote（指向原作者），如果不小心 `git push upstream` 会试图推到原作者仓库（虽然没权限）。

**保险做法**：把 upstream 的 push URL 设成无效地址
```bash
cd software/MotorBridge
git remote set-url --push upstream DISABLED
# 之后 git push upstream 会直接报错，永远推不到原作者那
```

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
