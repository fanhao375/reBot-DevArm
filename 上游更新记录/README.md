# 上游更新记录

专门记录从上游仓库 [`Seeed-Projects/reBot-DevArm`](https://github.com/Seeed-Projects/reBot-DevArm) 同步过来的每一次更新的**详细内容**。

## 📌 这个文件夹的用途

- CHANGELOG.md 只记录"何时做了同步"（操作日志）
- 本文件夹记录"上游**具体更新了什么**"（内容分析）
- 方便以后回溯原作者的更新轨迹，不用再去翻 GitHub

## 📂 命名规则

每次同步后，新建一个 Markdown 文件：

```
YYYY-MM-DD_同步详情.md
```

文件内结构建议：
1. **基本信息**：commit 范围、数量、本地 merge commit
2. **更新分类总结**：按功能块归类（购买/路线图/硬件/文档/...）
3. **每个 commit 的内容**（可选，逐条展开）
4. **观察与备注**（比如上游写错的地方、值得关注的新链接等）

## 📚 历史记录

| 日期 | 文件 | 上游 commit 范围 | 合并 commit |
|---|---|---|---|
| 2026-04-21 | [2026-04-21_同步详情.md](./2026-04-21_同步详情.md) | `4420c46..b837833`（2 个 commit） | `50a52ee` |
| 2026-04-17 | [2026-04-17_同步详情.md](./2026-04-17_同步详情.md) | `b876c69..4420c46`（10 个 commit） | `36c42ce` |

## 🔄 同步流程速查

```bash
# 1. 查看上游
git fetch upstream
git log --oneline main..upstream/main

# 2. 合并
git stash push -u                    # 有未提交修改时先 stash
git merge upstream/main
git stash pop

# 3. 记录本次更新内容到这个文件夹
# 4. commit + push
git add .
git commit -m "同步上游 YYYY-MM-DD"
git push origin main
```
