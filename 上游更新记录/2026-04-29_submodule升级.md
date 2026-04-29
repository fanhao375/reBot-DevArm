# 2026-04-29 Submodule 升级

**结论：MotorBridge 和 StarArm_102 全部升级到上游最新**

---

## 📌 升级信息

- 升级时间：2026-04-29
- 决策反转：之前在 `2026-04-29_同步详情.md` 记录为"暂不同步"，本次决策追新（符合复刻基线维护原则的"持续追上游最新进展"定位）
- 升级前 baseline：`baseline-2026-04-29` tag（保留为回滚点）

---

## 📦 升级前后对比

| Submodule | 升级前 | 升级后 | 新增提交数 |
|-----------|--------|--------|-----------|
| `software/MotorBridge` | f63896a | f7037b0 (v0.2.4) | 50 |
| `software/reBotArm_control_py` | (不变) | (不变) | 0 |
| `遥操作/StarArm_102` | aaa80d7 | d777473 | 4 |

---

## 🔍 MotorBridge 详细变化（50 个 commit）

### 🏗️ 架构重构（重大）

| commit | 说明 |
|--------|------|
| `73c9949` | **Studio UI 拆分到独立仓库 `motorbridge/motorbridge-studio`**（factory_calib_ui_ws/ 大量文件被删除） |
| `b2b67bf` | refactor(ws_gateway): 统一 vendor 命名 + 命令模块布局 |
| `9e982ae` | refactor(ws_gateway): 操作拆分到 < 300 行的模块 |
| `9db93e2` | refactor(ws_gateway): 解耦 websocket 路由和操作处理器 |
| `6d90be3` | refactor(ws_gateway): 拆分共享 model 和 session 层 |
| `2f72734` | refactor(factory-ui): P0 共享 hooks/components 加固 |
| `ba36354` | refactor(factory-ui): 模块化 hooks 和基础设施 |

### 📦 版本发布

```
0.1.8 (509397c) → 0.1.9 (541e34c) → 0.2.0 → 0.2.1 → 0.2.2 (30fa4d3) → 0.2.3 (2fd913c) → 0.2.4 (1472242)
```

### 🔧 与达妙/RobStride 电机相关的修复（直接受益）

| commit | 说明 | 对你 |
|--------|------|------|
| `cc1117e` | factory-calib-ui-ws: **同步最新达妙寄存器值** | ⭐ 直接相关 |
| `99ecc65` | RobStride: 改进参数兼容性 + 扫描默认值 | ⭐ 相关 |
| `822dffe` | ws+ui: RobStride 模式切换稳定化 + pos_vel flow 恢复 | ⭐ 模式切换更稳 |
| `7289487` | core: 多电机循环 paced tx + 可配置 bulk op gap | 多电机更稳 |
| `fee4cad` | core: enable/disable burst 节流 | 启停更稳 |

### 🆕 新增功能

| commit | 说明 |
|--------|------|
| `5723c20` | feat(macos): 添加 PCBUSB PCAN 后端支持 |
| `5c4b2ec` | macos: 打包 PCBUSB archive + 一键 setup 脚本 |
| `4aa3050` | docs(mintlify): macOS DYLD fallback for gateway |
| `70ab6a0` | docs(gateway): 跨平台 macOS ws_gateway 启动指引 |
| `fcda29f` | feat(python): 独立 motorbridge-gateway 入口 |
| `cf87ecb` | refactor: WebSocket req_id 匹配 + python scan 复用 controllers |
| `7b1bd80` | feat(factory-ui): 实时滑块移动模式 |
| `faae4ed` | feat(ui): 升级 reBot arm 安全流程、参数工具、帮助中心 |
| `3581ded` | feat(ui): 改进帮助中心 UX、零位安全刷新、高级风险弹窗 |
| `18827d0` | feat(factory-ui): 增强 robot-arm 重放工作流和序列库 |
| `ef686e0` | feat(robot-arm): 安全演示序列 + 非阻塞 beta 警告 |
| `dd3fd85` | feat(factory-calib-ui-ws): 品牌 logo 和取证水印背景 |
| `777c5f5` | feat(ui,docs): 扩展电机高级控制 + 同步 python mintlify API |
| `97e531f` | python-cli: 添加 RobStride zero/set-zero + 同步文档 |

### 📚 文档与 CI（10+ 个 commit）

| commit | 说明 |
|--------|------|
| `f7037b0` | chore: mdx/md 文件 linguist-detectable=false |
| `a9667da` | docs(readme): 添加 motorbridge-studio repo 链接 |
| `c87ebc / e30af00 / 96c88f5 / 5347c46` | docs(mintlify): 中英文章节同步 + RobStride 文档对齐 |
| `900d7fc` | docs: 修复 mojibake（中文乱码）+ 对齐 RobStride CLI 指引 |
| `86f26c0` | docs(readme): 添加手动 PCBUSB 下载步骤 + 修复 zh-cn 编码 |
| `663ae5b` | docs(python-mintlify): 文档化 standalone motorbridge-gateway 用法 |
| `406795a` | docs: 同步 release/versioning + bindings/examples 设置指引 |
| `f95de96` | ci(release): 添加 macos arm64 wheel job |
| `3474323` | docs+ui: 重命名 assistant + 扩展跨平台 install/transport 指引 |
| `836700d` | docs: 完整审计 + 对齐 CLI/gateway 能力文档 |
| `b022d5b` | 改进跨平台 gateway UX + factory calib UI |
| `6e69efd` | docs/release: 对齐 ws bind 安全 + python 打包流程 |
| `d217778` | chore: checkpoint 当前 bindings 和 factory ui TODO |
| `0241dc7` | chore(factory-ui): 移除重复的 urdf asset tree |
| `ec29e47` | fix(ci): 在 factory-ui TODO 中添加 can_debugging.md 引用 |
| `701fbf3` | ui(ws): 改进 robot-arm 安全流程 + 扩展帮助设置文档 |

---

## 🔍 StarArm_102 详细变化（4 个 commit）

| commit | 类型 | 说明 |
|--------|------|------|
| `195e105` | docs | update README and hardware overview |
| `028d737` | **重要** | **更新新的模型** |
| `a8248e5` | docs | update README |
| `d777473` | **重要** | **README Joint Limit**（关节限位） |

### 模型文件变化

```
ROS2_HUMBLE/src/stararm102_gazebo/meshes/
  link6.STL         700684 → 700684 bytes（重新生成，大小不变）
  link7_left.STL    151484 → 110284 bytes（变小 27%）
  link7_right.STL   228584 → 204484 bytes（变小 11%）

ROS2_HUMBLE/src/stararm102_gazebo/urdf/
  stararm102_gazebo.urdf  216 行重写
```

### 配置变化

```
ROS2_HUMBLE/.../config/moveit_controllers.yaml      更新
ROS2_HUMBLE/.../config/ros2_controllers.yaml        新增（14 行）
ROS2_HUMBLE/.../config/stararm102_description.srdf  更新
ROS2_HUMBLE/.../launch/gazebo_demo.launch.py        调整
```

### 其他

- `Python_SDK/stararm102_ro.py` 改为可执行（chmod +x）

**变更范围**：32 个文件，+454 / -354 行

---

## ✅ 已完成的动作

- [x] 在两个 fork（fanhao375/motorbridge、fanhao375/Star-Arm-102）拉取上游最新（fork 的 main 已追平上游）
- [x] 主仓库 software/MotorBridge submodule 升级到 f7037b0
- [x] 主仓库 遥操作/StarArm_102 submodule 升级到 d777473
- [x] 独立 commit 各自一个：
  - `7a1bacc` 升级 MotorBridge submodule: f63896a → f7037b0 (v0.2.4)
  - `a132345` 升级 StarArm_102 submodule: aaa80d7 → d777473

---

## ⚠️ 未完成的验证（待用户做）

### MotorBridge 验证 checklist
- [ ] Python 包能安装（`pip install -e software/MotorBridge` 或类似）
- [ ] 能 `import motorbridge` 不报错
- [ ] 示例程序能跑到初始化阶段
- [ ] **不破坏当前 reBotArm_control_py 的代码**（关键！）
- [ ] 有硬件时：CAN 通信 / 电机扫描 / 速度模式 / 位置模式
- [ ] **特别关注**：cc1117e 同步了最新达妙寄存器值，配合 DMTool v2.1.6.0-FD 验证一遍

### StarArm_102 验证 checklist
- [ ] 模型文件完整（link6/link7_left/link7_right STL 能加载）
- [ ] URDF 一致性（关节数、命名）
- [ ] **关节限位（Joint Limit）变化已阅读 README 并记录**
- [ ] 不影响现有遥操作坐标系/控制映射（如有）

---

## 🔄 出问题怎么回滚

如果验证发现问题，回滚到升级前的基线：

```bash
# 回到升级前的 baseline tag
git checkout baseline-2026-04-29
git submodule update --init --recursive

# 或者只回滚某一个 submodule
cd software/MotorBridge
git checkout f63896a   # 升级前的 commit
cd ../..
git add software/MotorBridge
git commit -m "回滚 MotorBridge 到升级前状态"
```

---

## 📝 下次检查触发条件

- 当 reBotArm_control_py 与新版 MotorBridge 出现 API 不兼容时
- 当达妙寄存器值再次变化时（持续观察 motorbridge/motorbridge）
- 6 个月后强制评估一次（2026-10-29 左右）
- 当遥操作开发启动，需要重新验证 StarArm_102 模型 / 关节限位时

---

## 🔗 相关 commit

| commit | 说明 |
|--------|------|
| `7a1bacc` | 升级 MotorBridge submodule |
| `a132345` | 升级 StarArm_102 submodule |
| 本文件 | 详细变化记录 |
| `baseline-2026-04-29` tag | 升级前的回滚点 |
