# software/sim_extras/ — 自建学习用仿真脚本

这个目录放**我自己写的扩展仿真脚本**，作为主仓库正式跟踪的文件。

不像 `software/reBotArm_control_py/`（是嵌套的第三方代码仓，我不往里推改动），这里的脚本会随主仓库一起 `clone` 下来。

## 📂 当前内容

| 脚本 | 对应真机例程 | 用途 |
|------|-------------|------|
| `gravity_sim.py` | `example/9_gravity_compensation.py`（基础重力补偿） | 交互式调节关节角，用 MeshCat 显示每个 link 质心和重力方向，打印 τ_g 条形图 |
| `gravity_lock_sim.py` | `example/10_gravity_compensation_lock.py`（末端速度锁止） | 静态解剖 10 号算法：雅可比 → 末端速度 → 阈值判断 → 锁定/跟随 → τ 分解，配套 MeshCat 可视化 |

## 🔧 运行方式（WSL2 Ubuntu）

```bash
cd /mnt/f/chengshenzhilu/Robot/reBot-DevArm
python3 software/sim_extras/gravity_sim.py
# 或
python3 software/sim_extras/gravity_lock_sim.py
```

脚本运行时会动态把 `software/reBotArm_control_py/` 加到 `sys.path`，借用其中的：
- `reBotArm_control_py.dynamics`（动力学模型加载、重力计算）
- `example.sim.visualizer.Visualizer`（MeshCat 可视化器）

## 📌 依赖

- Python 3.10+（WSL2 默认 python3）
- `pinocchio >= 3.9`
- `meshcat`
- `numpy`

依赖已在 `reBotArm_control_py` 的 pyproject.toml 里声明过，只要按 `复现教程_01.md` 第三步搭好环境，这些脚本直接可跑。

## ⚠️ 路径约定

脚本里用这种方式找到隔壁的 `reBotArm_control_py/`：

```python
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "reBotArm_control_py"))
```

只要 `sim_extras/` 和 `reBotArm_control_py/` 都在 `software/` 下就能正常工作。**不要单独把脚本挪到别的地方运行**。
