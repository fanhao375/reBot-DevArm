# 重力补偿原理与代码详解

> 从零理解重力补偿的物理原理、数学推导和代码实现

---

## 📚 目录

1. [什么是重力补偿](#什么是重力补偿)
2. [物理原理](#物理原理)
3. [数学推导](#数学推导)
4. [代码架构](#代码架构)
5. [代码详解](#代码详解)
6. [实战示例](#实战示例)

---

## 什么是重力补偿

### 问题：机械臂为什么会下坠？

机械臂在重力场中，如果不施加任何力矩，它会因为自重而下坠。想象一下：
- 你伸直手臂拿着一瓶水 → 手臂会感到很累，因为肌肉在对抗重力
- 机械臂伸出去 → 电机需要输出力矩来对抗重力

### 解决方案：重力补偿

**重力补偿** = 计算出"对抗重力所需的力矩"，然后前馈给电机。

**效果**：
- ✅ 机械臂可以在任意姿态下"漂浮"（松手不会掉）
- ✅ 你可以轻松推动机械臂到任何位置
- ✅ 电机只需要很小的刚度就能保持位置

---

## 物理原理

### 机械臂的动力学方程

$$\tau = M(q)\ddot{q} + C(q,\dot{q})\dot{q} + g(q)$$

其中：
- $\tau$ — 关节力矩（电机输出）
- $M(q)$ — 质量矩阵（惯性）
- $C(q,\dot{q})$ — 科氏力和离心力矩阵
- $g(q)$ — **重力项**（我们要补偿的）
- $q, \dot{q}, \ddot{q}$ — 关节位置、速度、加速度

### 静止时的特例

如果机械臂静止（$\dot{q}=0, \ddot{q}=0$），动力学方程简化为：

$$\tau = g(q)$$

**这就是重力补偿力矩**：在当前姿态 $q$ 下，保持静止所需的力矩。

---

## 数学推导

### 重力项 g(q) 的计算

Pinocchio 使用 **RNEA（递归牛顿欧拉算法）** 计算 $g(q)$：

1. **前向递归**：从基座到末端，计算每个连杆的速度和加速度
2. **后向递归**：从末端到基座，累加每个连杆受到的重力和惯性力
3. **投影到关节空间**：得到每个关节需要的力矩

**时间复杂度**：O(n)，n 为关节数（对于 6 轴机械臂，约 0.1ms）

### MIT 模式控制律

达妙电机的 MIT 模式控制律：

$$\tau_{motor} = k_p \cdot (q_{target} - q) + k_d \cdot (v_{target} - v) + \tau_{feedforward}$$

**重力补偿的关键**：
- $q_{target} = q$（位置目标 = 当前位置）
- $v_{target} = 0$（速度目标 = 0）
- $\tau_{feedforward} = g(q)$（前馈重力力矩）
- $k_p = 2$（很弱的位置刚度）
- $k_d = 1$（阻尼）

实际输出力矩：

$$\tau_{motor} = 2 \cdot (q - q) + 1 \cdot (0 - \dot{q}) + g(q) = -\dot{q} + g(q)$$

**效果**：
- 重力被 $g(q)$ 完全抵消 → 不会下坠
- 位置刚度很弱（kp=2）→ 轻松推动
- 有阻尼（kd=1）→ 推动时有阻力，松手平稳停下

---

## 代码架构

### 4 层架构

![代码架构图](./architecture_代码架构.md)

1. **业务层** (`example/9_gravity_compensation.py`)
   - 500Hz 控制循环
   - 读 q → 算 g(q) → MIT 控制

2. **封装层** (`dynamics/__init__.py`, `dynamics/robot_model.py`)
   - 统一 API 接口
   - 加载 URDF，设置重力 (0,0,-9.81)

3. **计算层** (`dynamics/inverse_dynamics.py`, `dynamics/inertia.py`)
   - 逆动力学：$\tau = M\ddot{q} + C\dot{q} + g$
   - 质量矩阵、科氏力、重力向量

4. **底层** (Pinocchio)
   - `pin.computeGeneralizedGravity` — RNEA 算法
   - `pin.crba` — 质量矩阵
   - `pin.rnea` — 完整逆动力学

### 函数调用序列

![函数调用序列图](./sequence_函数调用序列.md)

### 控制循环流程

![控制循环流程图](./control_loop_控制循环流程.md)

---

## 代码详解

### 核心代码（9_gravity_compensation.py）

```python
def gravity_compensation_controller(arm: RobotArm, dt: float) -> None:
    """重力补偿控制回调（每 2ms 调用一次）"""
    
    # ① 读取当前关节位置（6 个关节角度，单位：弧度）
    q = arm.get_positions()          # shape=(6,)
    
    # ② Pinocchio 计算广义重力向量（6 个关节的重力补偿力矩，单位：N·m）
    tau_g = compute_generalized_gravity(q=q)   # shape=(6,)
    
    # ③ MIT 模式控制：位置目标 = 当前位置，前馈重力力矩
    arm.mit(
        pos=q,                                   # 位置目标跟随当前位置
        vel=np.zeros(arm.num_joints),            # 速度目标 = 0
        kp=np.full(arm.num_joints, 2.0),         # 位置刚度 kp=2（很弱）
        kd=np.full(arm.num_joints, 1.0),         # 速度阻尼 kd=1
        tau=tau_g,                               # 前馈力矩 = 重力补偿
        request_feedback=True,
    )
```

### compute_generalized_gravity 实现

```python
# dynamics/inverse_dynamics.py:86-126
def compute_generalized_gravity(
    model: Optional[pin.Model] = None,
    q: Optional[np.ndarray] = None,
    data: Optional[pin.Data] = None,
) -> np.ndarray:
    """计算广义重力向量 g(q)。
    
    本质上等价于 compute_inverse_dynamics(q, 0, 0)，
    但使用专用算法，不计算完整的 RNEA。
    """
    if model is None:
        model = load_dynamics_model()
    if data is None:
        data = create_data(model)
    if q is None:
        q = pin.neutral(model)
    
    # Pinocchio 底层调用
    pin.computeGeneralizedGravity(model, data, q)
    return data.g.copy()
```

---

## 实战示例

### 示例 1：基础重力补偿（漂浮版）

**文件**：`example/9_gravity_compensation.py`

**效果**：
- 机械臂在任意姿态下"漂浮"
- 手推可以轻松改变位置
- 松手后不会下坠

**运行**：
```bash
cd software/reBotArm_control_py
python example/9_gravity_compensation.py
```

**终端输出**：
```
[  20] tau_g = +2.345  -1.234  +0.876  +0.123  +0.045  +0.012  N·m
[  40] tau_g = +2.356  -1.245  +0.889  +0.125  +0.046  +0.013  N·m
...
```

### 示例 2：末端速度锁止版（进阶）

**文件**：`example/10_gravity_compensation_lock.py`

**效果**：
- 机械臂锁定在当前位置
- 用力推才能改变位置
- 松手后立即锁定

**新增功能**：
1. **末端速度检测**：计算末端执行器的线速度和角速度
2. **速度阈值判断**：超过阈值才更新目标位置
3. **积分项**：修正重力补偿误差，避免长期下垂

**运行**：
```bash
python example/10_gravity_compensation_lock.py
```

---

## 常见问题

### Q1：为什么 kp=2 这么小？

**A**：因为重力已经被 $g(q)$ 完全抵消了，电机只需要很小的刚度就能保持位置。如果 kp 太大（比如 50），机械臂会变得很"硬"，推不动。

### Q2：如果没有重力补偿会怎样？

**A**：如果 `tau=0`（不前馈重力），控制律变成纯阻尼 $\tau = -k_d \dot{q}$，机械臂会因为重力而慢慢下坠。

### Q3：为什么需要 500Hz 这么高的频率？

**A**：
- 重力补偿需要实时计算 $g(q)$，姿态变化时力矩也要跟着变
- 500Hz = 每 2ms 更新一次，保证控制的实时性和平滑性
- Pinocchio 的 RNEA 算法很快（O(n)），6 轴机械臂约 0.1ms

### Q4：可以在仿真里看重力补偿效果吗？

**A**：可以！我们可以写一个 MeshCat 仿真版，在浏览器里可视化：
- 显示机械臂当前姿态
- 实时显示每个关节的 $\tau_g$
- 用滑块改变姿态，看 $\tau_g$ 如何变化

---

## 下一步学习

1. **深入 Pinocchio**：理解 RNEA 算法的递归过程
2. **动力学三要素**：M(q)、C(q,q̇)、g(q) 的物理意义
3. **完整逆动力学**：$\tau = M\ddot{q} + C\dot{q} + g$ 的应用场景
4. **轨迹跟踪控制**：重力补偿 + PD 控制 + 前馈加速度

---

## 参考资料

- [Pinocchio 官方文档](https://gepettoweb.laas.fr/doc/stack-of-tasks/pinocchio/master/doxygen-html/)
- [RNEA 算法论文](https://link.springer.com/article/10.1007/BF00356078)
- [达妙电机 MIT 模式说明](https://wiki.seeedstudio.com/cn/damiao_series/)
