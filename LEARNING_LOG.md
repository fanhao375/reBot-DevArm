# 学习笔记

记录学习 reBot-DevArm 过程中的发现、踩坑和理解。

---

## 2026-04-12

### 项目认识

- reBot-DevArm 是 SeeedStudio 的开源 6DOF 机械臂项目，目标是降低具身智能学习门槛
- 有两个版本：B601 DM（达妙电机）和 B601 RS（RobStride 电机），外观结构一样，只是电机不同
- 截至今天，仓库里硬件资料齐全，软件代码刚发布（Python SDK + Pinocchio）

### 电机相关

- 两款电机都是**驱动一体化**（电机+FOC驱动器+双编码器集成在一个壳里），不需要单独买驱动器
- DM4340P（大电机）：27Nm 峰值扭矩，减速比 40:1，用在底座/肩部/大臂
- DM4310（小电机）：7Nm 峰值扭矩，减速比 10:1，用在小臂/腕部
- 4340P 比 4310 多一个"力位混控模式"，可以同时控制位置和限制力矩
- 所有电机通过 CAN 总线 @ 1Mbps 菊花链串联，协议是基于 MIT Mini Cheetah 的私有协议，不是 CANopen
- 反馈 ID 规则：feedback_id = motor_id + 0x10

### 通信协议

- 这台臂用的是达妙私有 CAN 协议（MIT 兼容），不是工业标准 CANopen
- 对于 7 个关节的桌面机械臂，CAN 总线完全够用
- 人形机器人（20+关节）才需要 EtherCAT，那是另一个层级的东西
- 达妙电机支持 CAN FD（波特率 > 1Mbps 自动切换），但默认 CAN 2.0B

### 供电

- 24V / 14.6A / 350W 电源，日常够用
- 7 个电机理论峰值总功耗 1296W，但不可能同时满载
- 正常工作 100-200W，高负载 200-300W

### 性能瓶颈

- 2 号电机（肩部 DM4340P）是瓶颈，长时间高负载容易过热
- 推荐：负载 ≤ 1.5kg，臂展 < 70%，连续工作 2 小时休息 15 分钟
- 建议加主动散热

### 环境踩坑

- `pyproject.toml` 里 `requires-python = "==3.10.*"` 太严格，改成 `>=3.10` 就能用 3.12
- **pip install pin 在 Windows 上会卡死**，因为要从源码编译 C++ 库
- 解决方案：用 WSL2（Ubuntu）或 conda 安装，有编译好的二进制包
- WSL2 默认装 C 盘，但可以通过 import/export 方式装到 F 盘

### 待做

- [ ] 安装 WSL2 Ubuntu 到 F 盘
- [ ] 在 WSL2 里装 Python + Pinocchio 环境
- [ ] 跑通正运动学测试（example/5_fk_test.py）
- [ ] 跑通逆运动学测试（example/6_ik_test.py）
- [ ] 深入读 reBotArm_control_py 源码

---

## 2026-04-13

### WSL2 安装踩坑

- `pip install pin` 在 Windows 上从源码编译 C++，会卡死不动，根本装不上
- 解决方案：用 WSL2 Ubuntu，Linux 下 pip 有预编译的二进制包
- WSL2 默认装 C 盘，但 C 盘空间不足，需要装到 F 盘
- **装到 F 盘的方法**：不能直接指定路径安装，需要先下载 appx 包 → 解压 → 找到 install.tar.gz → 用 `wsl --import` 指定 F 盘路径导入
- PowerShell 的 `curl` 不是真 curl，要用 `Invoke-WebRequest`
- PowerShell 默认不走 VPN 代理，需要手动设置：`$env:HTTP_PROXY="http://127.0.0.1:7890"` + `-Proxy` 参数
- 微软 appx 包里套了两层：外层 appx 里有 ARM64 和 x64 两个子 appx，要解压 x64 那个才能找到 install.tar.gz
- 进入 WSL 后提示代理警告（localhost proxy not mirrored），不影响使用

### 正运动学测试通过

- 跑通了 `example/5_fk_test.py`
- 归零位置 (0 0 0 0 0 0) 末端：X=0.253m, Y=0, Z=0.172m
  - 约 25cm 正前方、17cm 高，姿态几乎为单位矩阵，说明 URDF 模型正确
- 自定义角度 (1 25 30 45 60 79) 末端：X=0.135m, Y=-0.150m, Z=-0.088m
  - 末端往下往右移了，姿态有旋转，符合预期

### 待做
- [x] WSL2 里装 Python + Pinocchio
- [x] 跑通正运动学测试
- [x] 跑通逆运动学测试（修了官方 bug）
- [x] 跑通 MeshCat 可视化三件套
- [ ] 读运动学源码理解 Pinocchio 调用方式
- [ ] 深入读 reBotArm_control_py 源码
- [ ] 等 04.20 Isaac Sim 官方教程发布

### 逆运动学测试 — 官方示例有 bug

- `example/6_ik_test.py` 调用 `compute_ik()` 传的参数名全是错的
- 说明 develop 分支的示例代码和库接口还没对齐，代码还在开发中
- 修复后验证：输入 FK 归零坐标 (0.253, 0, 0.172) → IK 解出 (0,0,0,0,0,0)，正确
- 收敛状态显示"否"，但误差只有 3.80e-04（阈值 1e-4），实际已经非常接近，结果可用
- **教训**：开源项目的 develop 分支不一定稳定，跑之前要有心理准备会遇到 bug

### MeshCat 可视化三件套（无硬件学习的最佳工具）

#### 环境问题：WSL2 访问 Windows 文件的 Git symlink 失效

- **现象**：`python3 example/sim/fk_sim.py` 报错 `Mesh package://reBot-DevArm_description_fixend/meshes/base_link.STL could not be found`
- **原因**：仓库里 `urdf/reBot-DevArm_description_fixend` 是指向 `reBot-DevArm_fixend_description` 的软链接（两个目录名只是单词顺序不同）
  - Linux/Mac 下 git clone 会还原成真·软链接 → Pinocchio 正常工作
  - **Windows 下 Git 把软链接存成了纯文本文件**（31 字节，内容就是目标路径字符串）
  - WSL2 通过 `/mnt/f` 访问 Windows NTFS 文件系统时，看到的是那个文本文件，不是目录
- **解决方案**：在 WSL2 里手动重建软链接
  ```bash
  cd urdf
  rm reBot-DevArm_description_fixend
  ln -s reBot-DevArm_fixend_description reBot-DevArm_description_fixend
  ```
- **验证**：`ls -la` 看到 `lrwxrwxrwx ... reBot-DevArm_description_fixend -> reBot-DevArm_fixend_description` 就对了
- **教训**：WSL2 + Windows Git 混用时，软链接是个坑；遇到"文件找不到"先检查是否是 symlink 问题

#### 1. fk_sim.py — 正运动学交互式可视化

- **功能**：输入 6 个关节角（度）→ 浏览器里实时显示机械臂 3D 姿态
- **启动**：`python3 example/sim/fk_sim.py` → 终端打印 `http://127.0.0.1:7000/static/` → Windows 浏览器打开
- **操作**：
  - 输入 `0 0 0 0 0 0` → 归零姿态（竖直）
  - 输入 `0 -90 0 0 0 0` → J2 弯 90 度（大臂水平）
  - 输入 `45 -30 15 -60 90 180` → 六关节复杂姿态
- **浏览器操作**：左键拖 = 旋转视角，右键拖 = 平移，滚轮 = 缩放
- **价值**：把光秃秃的 FK 坐标数字变成肉眼可见的 3D 模型，直观验证运动学正确性

#### 2. ik_sim.py — 逆运动学交互式可视化（已改进）⭐

- **功能**：输入目标位置 (x, y, z) 或位姿 (x, y, z, roll, pitch, yaw) → 机械臂自动求解关节角并摆到目标位置
- **启动**：`python3 example/sim/ik_sim.py`
- **原版问题**：
  - 代码里只调用了 `viz.update(result.q)`，**没调用 `viz.show_ik_pose()` 显示目标点标记**（红球 + 三色坐标轴）
  - 每次从零位 `[0,0,0,0,0,0]` 开始求解（`q_init=None`），不使用上一次的解作为初值
  - 这导致很多点容易陷入局部最优 → 报 `[未收敛]`
  - 例如 `(0.25, 0.0, 0.15)` 误差 2.15cm，`(0.2, 0.0, 0.25)` 误差 9.46cm
- **改进方案**（已实施）：
  1. **添加目标点可视化**：调用 `viz.show_ik_pose(target_pos, target_rot, result.q)` 显示红球 + 坐标轴
  2. **连续初值策略**：保存 `q_current`，每次从上一个解出发求解下一个目标
  3. **调试输出增强**：解析失败时显示原始输入和分割结果
- **改进后测试结果**：
  - `0.25 0.0 0.2` → ✅ 收敛，9 次迭代，误差 0.056mm
  - `0.3 0.0 0.25` → ✅ 收敛，10 次迭代，误差 0.069mm（J2 -32°, J3 -18°）
  - `0.2 0.15 0.3` → ✅ 收敛，12 次迭代，误差 0.063mm（J1 腰转 81°）
  - **三个点全部收敛**，浏览器里红球正确显示并跟随移动
- **价值**：改进后成为真正可用的交互式 IK 调试工具，适合快速验证单点 IK 求解

#### 3. traj_sim.py — SE(3) 测地线轨迹规划 + CLIK 跟踪（最有料）⭐⭐⭐

- **功能**：输入目标位姿 → 规划 SE(3) 测地线轨迹 → CLIK 逐帧跟踪 → 浏览器动画回放
- **启动**：`python3 example/sim/traj_sim.py` → 显示当前末端位置 `pos[0.253 0.000 0.172]`
- **测试 1（简单平移）**：
  - 输入：`0.3 0.0 0.25`（往前 + 往上）
  - 结果：IK 成功率 96.1%，最大误差 0.34mm，平均误差 0.05mm
  - 关节运动：J2 -32.3°, J3 -17.7°, J4 -14.6°（肩/肘/腕弯曲）
  - 轨迹：51 点，1.0 秒，dt=0.02s
- **测试 2（复杂姿态变化）**：
  - 输入：`0.2 0.15 0.35 0 0.5 0.3`（位置 + pitch 0.5 + yaw 0.3 弧度）
  - 结果：**IK 成功率 100%** 🎉，最大误差 0.099mm，平均误差 0.057mm
  - 关节运动：**6 个关节全动**，J1 转 63.4°（腰转），J5/J6 转腕
  - 轨迹：121 点，2.4 秒
- **测试 3（超出工作空间）**：
  - 输入：`0.15 0.2 0.3`
  - 结果：`IK 无解` ❌
- **浏览器画面**：
  - **灰色路径线**：规划的参考轨迹（SE(3) 测地线）
  - **绿色路径线**：实际跟踪轨迹（CLIK 输出）
  - **机械臂动画**：沿轨迹逐帧播放，肉眼验证跟踪精度
- **价值**：
  - 这是 `reBotArm_control_py_运行流程.drawio` 里**路径 A（move_to_traj）的无硬件版**
  - 完整展示了 IK → SE(3) 测地线 → CLIK → 动画播放 的全流程
  - 跟踪误差 < 0.1mm，说明 Pinocchio + CLIK 算法实现质量很高

#### 关键收获

1. **MeshCat = 无硬件版的"数字孪生"**，浏览器里实时 3D 预览机械臂运动
2. **三个脚本的定位**：
   - `fk_sim.py`：最简单，验证 FK 正确性
   - `ik_sim.py`：有 bug，跳过
   - `traj_sim.py`：最有料，完整展示轨迹规划 + 跟踪
3. **工作空间限制**：推荐半径 < 450mm（70% reach），超出会 IK 无解
4. **零位末端位置**：`(0.253, 0.000, 0.172)` m，约 25cm 正前方、17cm 高
5. **下一步**：等 04.20 Isaac Sim 官方教程发布，到时候已经有 Pinocchio + URDF 基础，上手会很快


---

## 2026-04-16

### 重力补偿深入学习

#### 1. 安装可视化工具集

- 克隆 `markdown-viewer/skills` 仓库到 `/tmp/`
- 软链接 4 个 skills 到 `~/.claude/skills/`:
  - `uml` — PlantUML 类图/序列图/活动图
  - `architecture` — HTML/CSS 分层架构图
  - `infographic` — YAML 流程图/时间线/对比图
  - `mindmap` — PlantUML 思维导图
- **目的**: 以后读代码时可以快速生成可视化图表辅助理解

#### 2. 重力补偿代码解析

- **核心文件**: `example/9_gravity_compensation.py` (基础漂浮版)
- **控制律**: `τ = g(q) + kp·(q_target - q) + kd·(0 - q̇)`
  - `g(q)` — 重力补偿项 (前馈)
  - `kp·Δq` — 位置误差反馈 (刚度)
  - `kd·Δq̇` — 速度阻尼 (避免震荡)
- **效果**: 机械臂漂浮在空中,松手不掉,轻推会移动
- **底层**: Pinocchio 的 `computeGeneralizedGravity()` 函数,基于 RNEA 算法

#### 3. 代码架构梳理

生成了 3 张可视化图表:

**3.1 分层架构图** (`architecture_代码架构.md`)


**3.2 函数调用序列图** (`sequence_函数调用序列.md`)
- 用户代码 → 500Hz 控制循环 → `compute_generalized_gravity()` → `pin.computeGeneralizedGravity()` → RNEA 算法
- 完整展示了从业务代码到底层算法的调用链

**3.3 控制循环流程图** (`control_loop_控制循环流程.md`)
- 5 个步骤: 读取关节位置 → 计算重力补偿 → MIT 控制律 → 打印力矩 → 循环
- 频率: 500Hz (2ms 周期)

#### 4. 文档整理

- 新建 `software/docs/02_reBotArm_control_py/重力补偿详解/` 目录
- 生成 4 个文档:
  - `README.md` — 完整教程 (7789 字节)
    - 什么是重力补偿 (问题 + 解决方案)
    - 物理原理 (动力学方程 τ = M·q̈ + C·q̇ + g(q))
    - 数学推导 (RNEA 算法 + MIT 控制律)
    - 代码架构 (4 层架构)
    - 代码详解 (核心代码逐行解释)
    - 实战示例 (9 号和 10 号例程)
    - 常见问题 (FAQ)
  - `architecture_代码架构.md` — 4 层架构图
  - `sequence_函数调用序列.md` — UML 序列图
  - `control_loop_控制循环流程.md` — Infographic 流程图
- 更新 `software/docs/README.md` 和 `software/docs/02_reBotArm_control_py/README.md` 索引

#### 5. 同步 upstream 更新

- 配置 git 代理 (端口 10808)
- `git fetch upstream` 发现 2 个新提交:
  - `b876c69` Merge pull request #15
  - `c3cee75` Create DISCLAIMER.md (免责声明文档)
- **DISCLAIMER.md 要点**:
  - 产品定位: DIY 套件,需自行组装调试
  - 安全风险: 高速高扭矩,可能夹伤/撞击/砸伤
  - 责任划分: 厂家只对出厂材料缺陷负责
  - 禁止场景: 医疗/生命支持/载人/水下/工业高危等
  - 免保条款: 拆机/改装/进水/过保/无发票等不保修

#### 关键收获

1. **重力补偿 = 前馈控制**: 提前算出重力力矩 `g(q)`,让电机不用对抗重力
2. **RNEA 算法**: Recursive Newton-Euler Algorithm,O(n) 复杂度,适合实时控制
3. **MIT 控制律**: `τ = g(q) + kp·Δq + kd·Δq̇`,简单但有效
4. **代码分层清晰**: 业务层 → 封装层 → 计算层 → 底层,易于理解和维护
5. **可视化工具**: 以后读代码可以快速生成架构图/序列图/流程图

#### 下一步

- 继续学习 10 号例程 (进阶锁止版):
  - 末端速度锁止 (v_ee > 0.04 或 w_ee > 0.08 时更新目标)
  - 积分项 (抵消重力补偿误差)
  - 更高刚度 (kp=8, kd=1.5)
- 深入 Pinocchio 的 `computeGeneralizedGravity()` 实现
- 理解动力学模型的 M、C、g 三项

#### 6. 踩坑：Markdown 流程图渲染器选型

**问题**：用 markdown-viewer/skills 生成的 3 个图，在 VS Code 里只有 `architecture_代码架构.md`（HTML/CSS）能直接看，另外两个都是空白：
- `sequence_函数调用序列.md` 用 PlantUML（` ```plantuml `）→ 不渲染
- `control_loop_控制循环流程.md` 用 Infographic（` ```infographic `）→ 不渲染

**原因**：
| 引擎 | VS Code 原生支持 | 备注 |
|------|----------------|------|
| HTML/CSS | ✅ 是 | universal，任何渲染器都行 |
| Mermaid | ✅ 是（已装 `bierner.markdown-mermaid`） | GitHub/Typora 也原生支持 |
| PlantUML | ❌ 否 | 需要 `jebbs.plantuml` 插件 + Java + Graphviz |
| Infographic | ❌ 否 | YAML 自定义语法，只有特定浏览器扩展能渲染 |

**解决**：把两个不渲染的图都改成 mermaid 格式
- `sequenceDiagram` 替代 PlantUML 序列图（保留 actor / participant / activate / Note）
- `flowchart TD` 替代 infographic 流程图（用 `classDef` 着色）

**关键收获**：
1. **选图表引擎要先看渲染器**：图再漂亮，渲染不出来等于零
2. **mermaid 是最稳的跨平台选择**：VS Code、GitHub、Typora、Obsidian 都原生支持
3. **HTML/CSS 是 fallback**：复杂图（带颜色块、装饰）走 HTML/CSS 最稳
4. **PlantUML 适合本地工具链**：如果要导出 PNG/SVG 用 PlantUML 更强，但写在 md 里看就别用了

#### 7. 踩坑：上游 `get_gravity()` 函数与 Pinocchio 3.9 不兼容

**症状**：跑 `example/sim/gravity_sim.py` 报错
```
AttributeError: 'numpy.ndarray' object has no attribute 'x'
  File "...dynamics/robot_model.py", line 133, in get_gravity
    return np.array([g.linear.x, g.linear.y, g.linear.z])
```

**原因**：上游代码（`reBotArm_control_py/dynamics/robot_model.py:133`）写的是
```python
return np.array([g.linear.x, g.linear.y, g.linear.z])  # 假设 .linear 有 .x .y .z
```
这套 API 是**老版 Pinocchio**（2.x 时代）的，`pin.Motion.linear` 返回 `pin.Vector3`，可以用 `.x/.y/.z` 取分量。

**新版 Pinocchio 3.9.0**（CHANGELOG 2026-04-13 第 2 条装的版本）已经把 `pin.Motion.linear` 改成直接返回 `numpy.ndarray`，没有 `.x` 属性了。所以上游函数在新版 Pinocchio 上必崩。

**正确写法**（任一种都行）：
```python
g_vec = np.asarray(model.gravity.linear)              # 最简
g_vec = np.array([g.linear[0], g.linear[1], g.linear[2]])  # 索引访问
```

**怎么处理的**：
1. **没动上游库** —— 改了就和官方分叉，将来同步麻烦
2. **在我们自己的 `gravity_sim.py` 里绕开**：把 `get_gravity(model)` 调用换成 `np.asarray(model.gravity.linear)`，记一行注释说明原因
3. **可选**：将来给上游提 issue/PR

**关键收获**：
1. **Pinocchio 2.x → 3.x 有 API breaking change**：老代码（特别是 GitHub 上 2-3 年前的项目）很可能踩
2. **类似踩坑可能还有**：所有形如 `motion.linear.x / motion.angular.x / placement.translation.x` 的代码，在新版都要改成索引或 numpy
3. **遇到外部库 bug 的处理顺序**：能在自己代码里绕开 → 绕开（不动上游）；不能绕开 → 提 issue + 本地 monkey patch；最后才考虑 fork 改源码
4. **类比踩过的坑**：之前 `6_ik_test.py` 也是上游 bug（参数名不匹配），那次直接改了 example 文件（属于 example 不是核心库，改了不影响同步），这次是核心库（`dynamics/`），就不动它

#### 8. 踩坑：仿真不会自动检查关节限位（用户发现 ⭐）

**现场**：跑 `gravity_sim.py` 时输入 `0 -45 90 0 0 0` 和 `0 -60 60 -30 30 0`，看到 j2 暴增到 -8.7 N·m，CC 直觉地问"是不是有些超脱了物理极限呀，有些B它并不能那么弯折吧"。

**结论：CC 直觉对，这两个姿态真机做不到。**

**URDF 里 reBot-DevArm 的关节限位**（`urdf/reBot-DevArm_fixend.urdf`）：

| 关节 | URDF 字段 | 实际范围 | 备注 |
|------|----------|---------|------|
| j1 base_yaw       | `[-3.14, +3.14]` | -180° ~ +180° | 全圈 |
| **j2 shoulder**   | `[-3.14, **0**]`  | **-180° ~ 0°** | ⚠️ 只能往下 |
| **j3 elbow**      | `[-3.14, **0**]`  | **-180° ~ 0°** | ⚠️ 只能往下 |
| j4 wrist_roll     | `[-1.87, +1.57]`  | -107° ~ +90°   | |
| j5 wrist_pitch    | `[-1.57, +1.57]`  | -90° ~ +90°    | |
| j6 end_roll       | `[-6.28, +6.28]`  | -360° ~ +360°  | 多圈 |

**关键**：**j2 / j3 的 upper = 0**，意味着这两个关节**只能往负方向弯**。这不是 URDF 配错，是真实机械限制——大臂和小臂背后有挡块、肘关节有偏置盖板，物理上不允许往反方向折。

**为什么超限会让 τ_g 暴涨？**
仿真把机械臂掰成了真机不可能的姿态，质心被甩到肩关节后方，杠杆变长，力矩自然爆表。

**Pinocchio 的默认行为**：
- `pin.forwardKinematics()` / `pin.computeGeneralizedGravity()` **不会检查限位**，给什么 q 算什么
- 限位信息存在 `model.lowerPositionLimit` / `model.upperPositionLimit`（np.ndarray，弧度）
- 用户代码自己负责 validate

**修复方案**（已应用到 `gravity_sim.py`）：
1. 启动时打印所有关节的 URDF 限位
2. 每次输入后用 `check_joint_limits()` 检查，超限**只警告不阻止**（仿真允许"看一下超限会怎样"是有学习价值的）
3. 推荐姿态全部改成满足限位的版本：
   ```
   0 0 0 0 0 0
   0 -90 0 0 0 0
   0 -45 -90 0 0 0      # 原来错写成 +90，肘要往后收
   0 -60 -60 30 30 0    # 原来错写成 +60
   0 -120 -30 0 0 0
   ```

**更深层收获**：
1. **运动学/动力学计算都不带限位检查**——这是工业惯例（计算和约束分离）
2. **真机 vs 仿真的鸿沟**：仿真能算的，真机未必做得到（限位、碰撞、奇异点）
3. **直觉是好滤镜**：当数据"看起来不对劲"时，先怀疑物理边界，再怀疑算法
4. **效率对比工具**：URDF 里 `effort` 字段是单关节扭矩上限（j2/j3 = 27 N·m，j4/j5/j6 = 7 N·m）。下次可以加一个"超 effort 警告"，提示这个姿态真机也撑不住

