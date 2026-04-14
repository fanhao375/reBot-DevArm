# 01_项目专用

> reBot-DevArm 专用文档，针对本项目的 URDF 模型和仿真代码的深度解读

## 文档列表

| 文档 | 说明 | 适合人群 |
|------|------|---------|
| **reBot-DevArm_URDF详解.md** | 逐行解读 `reBot-DevArm_fixend.urdf`（448 行完整注释） | 看完通用 URDF 入门后，想深入理解本项目的人 |
| **reBot-DevArm_MeshCat仿真代码详解.md** | 4 个仿真文件的逐函数解读（visualizer / fk_sim / ik_sim / traj_sim） | 想理解仿真代码如何工作、如何改造的人 |

## 内容亮点

### URDF 详解
- ✅ 每个 link 的惯性参数含义（质量、质心、转动惯量）
- ✅ 每个 joint 的关键参数（origin 位置、rpy 旋转、axis 转轴、limit 限位）
- ✅ 为什么 joint2 的 `rpy="-1.5708 0 0"`（坐标系旋转 90°）
- ✅ 为什么 joint2 的 `upper="0"`（机械限位，不能往上抬超过水平）
- ✅ 为什么 link2 质量最重（1.327kg，包含大臂和肘关节电机）
- ✅ 完整的机械结构对应关系（URDF 名称 ↔ 实体零件 ↔ 电机型号）

### MeshCat 仿真代码详解
- ✅ 4 个文件的调用关系图（visualizer 被其他三个 sim 调���）
- ✅ Visualizer 类初始化流程（URDF 加载 → MeshCat 服务 → Pinocchio 模型）
- ✅ FK/IK/轨迹仿真的完整工作流程和关键参数
- ✅ 仿真代码 ↔ 真机代码的对应关系（sim 版 vs 真机版函数映射）
- ✅ 核心概念速查（SE(3)、CLIK、测地线插值等）

## 学习路径

1. **先看 `../00_新手入门/URDF_入门指南.md`** — 理解通用概念
2. **再看本文件夹的 reBot-DevArm_URDF详解.md** — 看实例
3. **跑 MeshCat 三件套** — 在浏览器里验证理解
4. **看 reBot-DevArm_MeshCat仿真代码详解.md** — 理解仿真代码每一步在做什么

## 相关资源

- URDF 文件位置：`../../reBotArm_control_py/urdf/reBot-DevArm_fixend_description/urdf/reBot-DevArm_fixend.urdf`
- 3D 模型文件：`../../reBotArm_control_py/urdf/reBot-DevArm_fixend_description/meshes/*.STL`
- 仿真代码位置：`../../reBotArm_control_py/example/sim/`
- 可视化工具入门：`../00_新手入门/MeshCat_可视化指南.md`
