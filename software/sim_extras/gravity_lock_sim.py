#!/usr/bin/env python3
"""重力补偿 + 末端速度锁止仿真（静态解剖版）。

这是 example/10_gravity_compensation_lock.py 的无硬件教学版本。
不做动力学积分（不模拟"推了之后机械臂怎么弹回来"），
而是把锁止控制算法的每一步打印出来，帮助理解：

    雅可比 J(q) → 末端速度 J·q̇ → 阈值判断 → 锁定 / 跟随

每次迭代输入当前关节角 q 和关节速度 q̇（模拟"真机运行到某一瞬间"的状态），
代码就走一遍 10 号的控制律：

    v_ee = J_lin(q) · q̇      （末端线速度，3 维）
    w_ee = J_ang(q) · q̇      （末端角速度，3 维）
    if ‖v_ee‖ > V_TH or ‖w_ee‖ > W_TH:
        q_target = q          （跟随：用力推才能改位置）
    else:
        q_target 保持不变      （锁定：小扰动被 kp 拉回来）
    tau = g(q) + kp·(q_target - q) + kd·(0 - q̇)

用法:
    python software/sim_extras/gravity_lock_sim.py

交互格式:
    每行输入 "q1 q2 q3 q4 q5 q6 | qd1 qd2 qd3 qd4 qd5 qd6"
    - | 前 6 个是关节角（deg），| 后 6 个是关节角速度（deg/s）
    - 只写 6 个值时 q̇ 默认 0

    或用预设场景:
      s0  归零静止                 →  LOCKED
      s1  大臂水平 + 微扰动         →  看阈值判断
      s2  大臂水平 + 人在推         →  UPDATE
      s3  折叠姿态 + 末端快转        →  UPDATE（角速度触发）
      r   重置 q_target 到当前 q
      q   退出

可视化（MeshCat）:
    - 机械臂当前姿态
    - 末端线速度箭头（蓝色，长度 ∝ ‖v_ee‖）
    - 末端角速度箭头（橙色，长度 ∝ ‖w_ee‖）
    - 锁止状态球：绿色 = LOCKED，红色 = UPDATE
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

# ── 控制参数（和 10 号真机版保持一致）─────────────────────────────────────────
V_TH = 0.04          # 末端线速度阈值 (m/s)
W_TH = 0.08          # 末端角速度阈值 (rad/s)
KP = 8.0             # 比例增益
KD = 1.5             # 阻尼增益
EE_FRAME = "end_link"

# ── 可视化参数 ────────────────────────────────────────────────────────────────
V_ARROW_SCALE = 0.6          # 线速度箭头长度 = ‖v‖ * scale (1 m/s → 0.6 m)
W_ARROW_SCALE = 0.15         # 角速度箭头长度 = ‖w‖ * scale
V_COLOR = 0x3080FF           # 蓝 —— 线速度
W_COLOR = 0xFF9030           # 橙 —— 角速度
STATUS_LOCK_COLOR = 0x30C050   # 绿 —— LOCKED
STATUS_UPDATE_COLOR = 0xE04040  # 红 —— UPDATE
STATUS_RADIUS = 0.025

# ── 预设场景 ──────────────────────────────────────────────────────────────────
# 每个预设: (q_deg, qd_deg_per_s, 描述)
PRESETS = {
    "s0": (
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        "归零 + 静止。q̇=0，线速度/角速度都是 0，必然 LOCKED。",
    ),
    "s1": (
        [0, -90, 0, 0, 0, 0],
        [0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
        "大臂水平 + 每个关节 0.5°/s 微扰动。观察末端速度是否超阈值。",
    ),
    "s2": (
        [0, -90, 0, 0, 0, 0],
        [5, 5, 5, 0, 0, 0],
        "大臂水平 + 肩/肘/腕以 5°/s 旋转（人在推）。预期 UPDATE。",
    ),
    "s3": (
        [0, -45, -90, 0, 0, 0],
        [0, 0, 0, 0, 30, 0],
        "折叠姿态 + 末端腕 30°/s 快转。线速度可能很小，但角速度会触发 UPDATE。",
    ),
}

should_exit = False


def signal_handler(sig, frame):
    global should_exit
    should_exit = True
    print("\n退出.")


# ── 末端速度箭头 ─────────────────────────────────────────────────────────────
def draw_velocity_arrows(viz, ee_pos, v_ee, w_ee):
    """在末端位置画两根箭头：线速度（蓝）和角速度（橙）。"""
    mc = viz.meshcat

    try:
        del mc["vel_viz"]
    except Exception:
        pass

    def draw_arrow(node_name, origin, vec, scale, color):
        vnorm = float(np.linalg.norm(vec))
        if vnorm < 1e-9:
            return
        end = origin + vec * scale
        pts = np.array([origin, end], dtype=np.float32).T
        mc[node_name].set_object(
            mcg.Line(
                mcg.PointsGeometry(pts),
                mcg.LineBasicMaterial(color=color, linewidth=6),
            )
        )
        # 末端画个小球标记方向
        T = np.eye(4)
        T[:3, 3] = end
        mc[node_name + "_tip"].set_object(
            mcg.Sphere(0.01),
            mcg.MeshLambertMaterial(color=color),
        )
        mc[node_name + "_tip"].set_transform(T)

    draw_arrow("vel_viz/v_ee", ee_pos, v_ee, V_ARROW_SCALE, V_COLOR)
    draw_arrow("vel_viz/w_ee", ee_pos, w_ee, W_ARROW_SCALE, W_COLOR)


def draw_status_ball(viz, ee_pos, is_locked):
    """在末端附近画一个小球表示锁止状态。"""
    mc = viz.meshcat
    color = STATUS_LOCK_COLOR if is_locked else STATUS_UPDATE_COLOR
    try:
        del mc["vel_viz/status"]
    except Exception:
        pass
    mc["vel_viz/status"].set_object(
        mcg.Sphere(STATUS_RADIUS),
        mcg.MeshLambertMaterial(color=color, opacity=0.9),
    )
    T = np.eye(4)
    T[:3, 3] = ee_pos + np.array([0, 0, 0.05])  # 在末端上方 5cm
    mc["vel_viz/status"].set_transform(T)


# ── 条形图打印（复用 gravity_sim 的风格）──────────────────────────────────────
def print_bar_chart(title, values, joint_names, unit="N·m", width=30):
    print(f"\n  ┌─ {title} ─".ljust(55, "─"))
    max_abs = max(np.max(np.abs(values)), 1e-9)
    for i, v in enumerate(values):
        bar_len = int(round(abs(v) / max_abs * width))
        bar = "█" * bar_len
        sign = "+" if v >= 0 else "-"
        name = joint_names[i] if i < len(joint_names) else f"j{i+1}"
        print(f"  │ [{i+1}] {name:>14s}: {sign}{abs(v):7.3f}  {bar}")
    print(f"  │ max |·| = {max_abs:.3f} {unit}")
    print("  └" + "─" * 52)


# ── 主循环 ────────────────────────────────────────────────────────────────────
def parse_line(line):
    """解析输入：'q1..q6 | qd1..qd6' 或 'q1..q6'（qd 默认 0）。返回 (q_deg, qd_deg)。"""
    if "|" in line:
        q_part, qd_part = line.split("|", 1)
    else:
        q_part, qd_part = line, ""
    q_deg = [float(x) for x in q_part.split()]
    if qd_part.strip():
        qd_deg = [float(x) for x in qd_part.split()]
    else:
        qd_deg = [0.0] * len(q_deg)
    return q_deg, qd_deg


def run_one_step(viz, model, data, ee_frame_id, q, qd, q_target, joint_names):
    """走一遍 10 号的算法，返回更新后的 q_target。"""
    # Step 1: 正运动学 + 雅可比
    pin.computeJointJacobians(model, data, q)
    pin.updateFramePlacements(model, data)
    J = pin.getFrameJacobian(model, data, ee_frame_id, pin.ReferenceFrame.WORLD)

    print(f"\n  [1] 雅可比 J(q) 形状: {J.shape}  (6 = 线速度3 + 角速度3, {J.shape[1]} = 关节数)")

    # Step 2: 末端 spatial velocity = J · q̇
    v_spatial = J @ qd
    v_ee = v_spatial[:3]
    w_ee = v_spatial[3:]
    v_norm = float(np.linalg.norm(v_ee))
    w_norm = float(np.linalg.norm(w_ee))

    print(f"  [2] 末端线速度 v_ee = J[:3] @ q̇ = {v_ee.round(4)}  →  ‖v_ee‖ = {v_norm:.4f} m/s")
    print(f"      末端角速度 w_ee = J[3:] @ q̇ = {w_ee.round(4)}  →  ‖w_ee‖ = {w_norm:.4f} rad/s")

    # Step 3: 阈值判断
    v_over = v_norm > V_TH
    w_over = w_norm > W_TH
    will_update = v_over or w_over

    print(f"  [3] 阈值判断:")
    print(f"      ‖v_ee‖ {v_norm:.4f} {'>' if v_over else '≤'} V_TH={V_TH} m/s   {'← 触发' if v_over else ''}")
    print(f"      ‖w_ee‖ {w_norm:.4f} {'>' if w_over else '≤'} W_TH={W_TH} rad/s {'← 触发' if w_over else ''}")

    # Step 4: 更新或保持 q_target
    if will_update:
        q_target_new = q.copy()
        print(f"  [4] → UPDATE: q_target 跟随当前 q（'人在推，换位置'）")
    else:
        q_target_new = q_target
        print(f"  [4] → LOCKED: q_target 保持不变（'小扰动，被 kp 拉回去'）")

    # Step 5: 最终控制力矩 τ = τ_g + kp(q_target - q) + kd(0 - q̇)
    tau_g = compute_generalized_gravity(model=model, q=q, data=data)
    q_error = q_target_new - q
    tau_kp = KP * q_error
    tau_kd = KD * (0 - qd)
    tau = tau_g + tau_kp + tau_kd

    print(f"\n  [5] 控制律分解: τ = τ_g + kp·(q_target - q) + kd·(0 - q̇)")
    print_bar_chart("τ_g（重力前馈）", tau_g, joint_names)
    print_bar_chart(f"kp·(q_target - q)  kp={KP}", tau_kp, joint_names)
    print_bar_chart(f"kd·(0 - q̇)  kd={KD}", tau_kd, joint_names)
    print_bar_chart("τ 最终（发给电机）", tau, joint_names)

    # 可视化
    ee_pos = data.oMf[ee_frame_id].translation
    draw_velocity_arrows(viz, ee_pos, v_ee, w_ee)
    draw_status_ball(viz, ee_pos, is_locked=not will_update)

    return q_target_new


def main():
    signal.signal(signal.SIGINT, signal_handler)

    print("=" * 65)
    print("  重力补偿 + 末端速度锁止仿真（静态解剖版）")
    print(f"  阈值: V_TH={V_TH} m/s   W_TH={W_TH} rad/s")
    print(f"  增益: KP={KP}   KD={KD}")
    print("=" * 65)

    viz = Visualizer()
    model = load_dynamics_model()
    data = model.createData()
    ee_frame_id = model.getFrameId(EE_FRAME)
    joint_names = [model.names[i] for i in range(1, model.njoints)]
    nq = viz.nq

    # 初始 q_target = 归零
    q = np.zeros(nq)
    q_target = q.copy()
    viz.update(q)
    print(f"\n[初始] q_target 锁定在归零位置")
    print("\n可用命令:")
    print("  直接输入: '0 -90 0 0 0 0 | 1 0 0 0 0 0'  (6 个 q + | + 6 个 q̇)")
    print("  预设:    s0 / s1 / s2 / s3 / list")
    print("  r        重置 q_target 到当前 q")
    print("  q        退出\n")

    while not should_exit:
        time.sleep(0.01)
        try:
            line = input("q(deg) | q̇(deg/s) > ").strip().lower()
        except EOFError:
            break

        if line in ("q", "quit", "exit"):
            break
        if line == "":
            continue

        if line == "list":
            print("\n预设场景:")
            for key, (qd, qdd, desc) in PRESETS.items():
                print(f"  {key}: {desc}")
                print(f"       q  = {qd}")
                print(f"       q̇ = {qdd}")
            continue

        if line == "r":
            q_target = q.copy()
            print(f"  [重置] q_target ← 当前 q = {np.rad2deg(q).round(2)} deg")
            continue

        # 预设场景
        if line in PRESETS:
            q_deg, qd_deg, desc = PRESETS[line]
            print(f"\n[预设 {line}] {desc}")
        else:
            try:
                q_deg, qd_deg = parse_line(line)
                if len(q_deg) != nq or len(qd_deg) != nq:
                    print(f"  需要 {nq} 个 q 和 {nq} 个 q̇（或只给 q）\n")
                    continue
            except ValueError:
                print("  无效输入（必须是数字）\n")
                continue

        q = np.radians(q_deg)
        qd = np.radians(qd_deg)  # deg/s → rad/s
        viz.update(q)
        q_target = run_one_step(viz, model, data, ee_frame_id, q, qd, q_target, joint_names)

        print(f"\n  [状态] q       = {np.rad2deg(q).round(2)} deg")
        print(f"         q_target= {np.rad2deg(q_target).round(2)} deg")


if __name__ == "__main__":
    main()
