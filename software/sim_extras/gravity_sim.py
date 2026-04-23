#!/usr/bin/env python3
"""重力补偿仿真 — 交互式可视化每个 link 的质心和重力作用 + 实时打印 τ_g。

这是 example/9_gravity_compensation.py 的无硬件可视化版本，
对应作者已有的 example/sim/{fk,ik,traj}_sim.py 教学路径。

用法:
    python software/sim_extras/gravity_sim.py

控制:
    输入 6 个关节角度（度），空格分隔
    例: 0 0 0 0 0 0          (归零)
    例: 0 -90 0 0 0 0        (大臂水平伸出，最大重力工况)
    例: 0 -45 90 0 0 0       (大小臂折叠)
    q / quit / exit: 退出

可视化:
    - 红色球：每个 link 的质心（半径 ∝ 质量）
    - 绿色线段：重力作用方向（长度 ∝ m·g，从质心向下）
    - 终端输出：6 个关节的重力补偿力矩 τ_g（带条形图）
"""

import sys
import signal
import time
from pathlib import Path

import numpy as np
import pinocchio as pin
import meshcat.geometry as mcg

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "reBotArm_control_py"))

from reBotArm_control_py.dynamics import (
    compute_generalized_gravity,
    load_dynamics_model,
)
from example.sim.visualizer import Visualizer

# ── 可视化参数 ────────────────────────────────────────────────────────────────
COM_BASE_RADIUS = 0.012      # 质心球基础半径（米）
ARROW_SCALE = 0.012          # 重力箭头长度缩放（米 / N）
COM_COLOR = 0xFF3030         # 红色（质心）
ARROW_COLOR = 0x00CC44       # 绿色（重力方向）
GRAVITY_NORM = 9.81          # m/s²

should_exit = False


def signal_handler(sig, frame):
    global should_exit
    should_exit = True
    print("\n退出.")


# ── 重力可视化绘制 ────────────────────────────────────────────────────────────
def draw_gravity_visualization(viz, model, data):
    """在每个 link 质心位置画红球 + 向下的绿色重力线段。

    依赖：调用前必须先用 q 调用过 forwardKinematics 或 computeGeneralizedGravity，
    使 data.oMi 已更新。
    """
    mc = viz.meshcat

    # 收集所有非零质量 link 的 (世界坐标质心, 质量, link_idx, name)
    items = []
    for i in range(1, model.njoints):  # 跳过 universe (0)
        inertia = model.inertias[i]
        mass = inertia.mass
        if mass < 1e-6:
            continue
        com_world = data.oMi[i].act(inertia.lever)
        items.append((com_world, mass, i, model.names[i]))

    if not items:
        return

    masses = np.array([m for _, m, _, _ in items])
    max_mass = masses.max()

    # 清掉旧节点
    try:
        del mc["gravity_viz"]
    except Exception:
        pass

    for com_world, mass, link_idx, name in items:
        # 质心球：半径 ∝ √(m / m_max)，避免大小差距过夸张
        radius = COM_BASE_RADIUS * (0.5 + np.sqrt(mass / max_mass))
        sphere_node = f"gravity_viz/com_{link_idx}"
        mc[sphere_node].set_object(
            mcg.Sphere(radius),
            mcg.MeshLambertMaterial(color=COM_COLOR, opacity=0.9),
        )
        T = np.eye(4)
        T[:3, 3] = com_world
        mc[sphere_node].set_transform(T)

        # 重力线段：从质心向下，长度 ∝ m * g
        arrow_len = ARROW_SCALE * mass * GRAVITY_NORM
        arrow_node = f"gravity_viz/arrow_{link_idx}"
        pts = np.array(
            [
                com_world,
                com_world + np.array([0.0, 0.0, -arrow_len]),
            ],
            dtype=np.float32,
        ).T
        mc[arrow_node].set_object(
            mcg.Line(
                mcg.PointsGeometry(pts),
                mcg.LineBasicMaterial(color=ARROW_COLOR, linewidth=4),
            )
        )


# ── 力矩漂亮打印 ──────────────────────────────────────────────────────────────
def print_gravity_torques(tau_g, joint_names):
    """终端打印 6 个关节的 τ_g，带条形图直观感受大小。"""
    print("\n  ┌─ 重力补偿力矩 τ_g (N·m) ──────────────────────")
    max_abs = max(np.max(np.abs(tau_g)), 1e-6)
    for i, t in enumerate(tau_g):
        bar_len = int(round(abs(t) / max_abs * 30))
        bar = "█" * bar_len
        sign = "+" if t >= 0 else "-"
        name = joint_names[i] if i < len(joint_names) else f"j{i+1}"
        print(f"  │ [{i+1}] {name:>14s}: {sign}{abs(t):6.3f}  {bar}")
    print(f"  │ Σ |τ_g| = {np.sum(np.abs(tau_g)):.3f} N·m"
          f"   |  max = {max_abs:.3f} N·m")
    print("  └────────────────────────────────────────────────\n")


# ── 关节限位检查 ──────────────────────────────────────────────────────────────
def check_joint_limits(q_rad, lower, upper, joint_names):
    """检查 q 是否在 URDF 限位内，返回越界提示列表（空表示全部合法）。"""
    warnings = []
    for i, qi in enumerate(q_rad):
        if qi < lower[i] - 1e-6 or qi > upper[i] + 1e-6:
            qi_deg = np.degrees(qi)
            lo_deg = np.degrees(lower[i])
            up_deg = np.degrees(upper[i])
            name = joint_names[i] if i < len(joint_names) else f"j{i+1}"
            warnings.append(
                f"  ⚠️  [{i+1}] {name}: 输入 {qi_deg:+.1f}° "
                f"超出 URDF 限位 [{lo_deg:+.1f}°, {up_deg:+.1f}°]"
            )
    return warnings


# ── 主循环 ────────────────────────────────────────────────────────────────────
def main():
    signal.signal(signal.SIGINT, signal_handler)

    print("加载可视化器和动力学模型...")
    viz = Visualizer()
    model = load_dynamics_model()
    data = model.createData()

    g_vec = np.asarray(model.gravity.linear)  # 绕开上游 get_gravity 的 .x 属性 bug
    print(f"重力方向: {g_vec} (norm={np.linalg.norm(g_vec):.3f} m/s²)")

    joint_names = [model.names[i] for i in range(1, model.njoints)]

    # 读取 URDF 关节限位（pinocchio model 自带）
    lower = np.asarray(model.lowerPositionLimit)
    upper = np.asarray(model.upperPositionLimit)
    print("\n关节限位（URDF）:")
    for i in range(viz.nq):
        print(
            f"  [{i+1}] {joint_names[i]:>14s}: "
            f"[{np.degrees(lower[i]):+7.1f}°, {np.degrees(upper[i]):+7.1f}°]"
        )

    # 初始姿态：归零
    q = np.zeros(viz.nq)
    viz.update(q)
    tau_g = compute_generalized_gravity(model=model, q=q, data=data)
    draw_gravity_visualization(viz, model, data)
    print_gravity_torques(tau_g, joint_names)

    print("MeshCat 已打开. 输入 6 个关节角度（度）:")
    print("  推荐姿态（全部满足 URDF 限位）:")
    print("    0 0 0 0 0 0          (归零，重力沿 link 轴向，力矩小)")
    print("    0 -90 0 0 0 0        (大臂水平外伸，最大重力工况)")
    print("    0 -45 -90 0 0 0      (大小臂折叠，肘往后收)")
    print("    0 -60 -60 30 30 0    (随手姿态)")
    print("    0 -120 -30 0 0 0     (抓低位)")
    print("  注意：j2/j3 上限为 0°（只能往负方向弯）")
    print("  q / quit / exit: 退出\n")

    while not should_exit:
        time.sleep(0.01)
        try:
            line = input("关节角度 (deg) > ").strip().lower()
        except EOFError:
            break

        if line in ("q", "quit", "exit"):
            break
        if line == "":
            continue

        try:
            q_deg = [float(x) for x in line.split()]
            if len(q_deg) != viz.nq:
                print(f"  需要 {viz.nq} 个值，收到 {len(q_deg)} 个\n")
                continue
        except ValueError:
            print("  无效输入（必须是数字）\n")
            continue

        q = np.radians(q_deg)

        # 检查限位（不阻止仿真，只警告——这样可以学习"超限会怎样"）
        warnings = check_joint_limits(q, lower, upper, joint_names)
        if warnings:
            print("\n  超出 URDF 关节限位（仿真仍会执行，但真机做不到）:")
            for w in warnings:
                print(w)

        viz.update(q)
        # 计算重力补偿力矩（同时更新 data.oMi）
        tau_g = compute_generalized_gravity(model=model, q=q, data=data)
        draw_gravity_visualization(viz, model, data)
        print_gravity_torques(tau_g, joint_names)


if __name__ == "__main__":
    main()
