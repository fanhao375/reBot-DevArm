# reBot-DevArm 软件文档中心

> 所有软件相关的文档集中在这里，按学习路径组织

---

## 📚 文档目录

| 文件夹 | 定位 | 适合人群 |
|--------|------|---------|
| **[00_新手入门](./00_新手入门/)** | 通用概念，不懂 ROS/URDF 的人先看 | 机械工程师、硬件工程师 |
| **[01_项目专用](./01_项目专用/)** | reBot-DevArm 专用解读 | 看完通用入门后，想深入理解本项目 |
| **[02_reBotArm_control_py](./02_reBotArm_control_py/)** | Python 上层运动学控制库 | 想理解运动学算法、轨迹规划 |
| **[03_MotorBridge](./03_MotorBridge/)** | Rust 底层电机控制库 | 想理解 CAN 协议、电机驱动 |

---

## 🎯 推荐学习路径

### 路径 1：无硬件学习（推荐新手）

```
1. 00_新手入门/URDF_入门指南.md
   ↓ 理解什么是 Link、Joint
   
2. 00_新手入门/MeshCat_可视化指南.md
   ↓ 学会用浏览器看 3D 模型
   
3. 跑 MeshCat 三件套（fk_sim / ik_sim / traj_sim）
   ↓ 动手验证理解
   
4. 01_项目专用/reBot-DevArm_URDF详解.md
   ↓ 看懂本项目的 URDF 为什么这么写

5. 01_项目专用/reBot-DevArm_MeshCat仿真代码详解.md
   ↓ 理解仿真代码每一步在做什么
   
6. 02_reBotArm_control_py/ 文档
   ↓ 理解运动学算法
```

### 路径 2：有硬件 / 想深入源码

```
1. 先走完路径 1（理解基础概念）
   ↓
   
2. 02_reBotArm_control_py/ 文档
   ↓ 理解上层控制逻辑
   
3. 03_MotorBridge/ 文档
   ↓ 理解底层电机驱动
   
4. 读源码 + 跑真机测试
```

### 路径 3：只想快速上手（跳过理论）

```
1. 看 ../../复现教程_01.md（主教程）
   ↓ 按步骤操作
   
2. 遇到不懂的概念，回来查对应文档
```

---

## 📖 文档速查表

| 我想... | 看哪个文档 |
|---------|-----------|
| 理解什么是 URDF | `00_新手入门/URDF_入门指南.md` |
| 在浏览器里看 3D 模型 | `00_新手入门/MeshCat_可视化指南.md` |
| 看懂 reBot URDF 每一行 | `01_项目专用/reBot-DevArm_URDF详解.md` |
| 理解 MeshCat 仿真代码怎么工作 | `01_项目专用/reBot-DevArm_MeshCat仿真代码详解.md` |
| 理解运动学算法（FK/IK/轨迹规划） | `02_reBotArm_control_py/reBotArm_control_py_说明.md` |
| **理解重力补偿原理和代码** | `02_reBotArm_control_py/重力补偿详解/README.md` |
| 看数据流（末端坐标→电机转动） | `02_reBotArm_control_py/reBotArm_control_py_运行流程.drawio` |
| 理解 CAN 协议和电机驱动 | `03_MotorBridge/MotorBridge_说明.md` |
| 看电机控制的发送/反馈流程 | `03_MotorBridge/MotorBridge_运行流程.drawio` |

---

## 🛠️ 相关资源

- **主教程**：`../../复现教程_01.md`
- **学习笔记**：`../../学习笔记.md`
- **操作日志**：`../../操作日志.md`
- **代码仓库**：
  - `../reBotArm_control_py/` — Python 上层控制
  - `../MotorBridge/` — Rust 底层驱动
- **硬件资料**：`../../hardware/reBot_B601_DM/`

---

## 💡 文档编写原则

这些文档的目标读者是**懂硬件/机械，但不懂 ROS/Pinocchio 的工程师**。

编写原则：
- ✅ 用机械工程师熟悉的语言（机械图纸、零件、装配关系）
- ✅ 类比解释抽象概念（Link = 零件，Joint = 连接方式）
- ✅ 标注实体对应关系（URDF 名称 ↔ 实体零件 ↔ 电机型号）
- ✅ 提供可执行的示例（MeshCat 可视化、代码片段）
- ✅ 常见问题排查（symlink 失效、代理拦截、WebGL）

---

## 📝 贡献指南

如果你发现文档有错误或不清楚的地方，欢迎：
1. 提 Issue 到主仓库
2. 或直接修改文档并提 PR

文档更新记录在 `../../操作日志.md`。
