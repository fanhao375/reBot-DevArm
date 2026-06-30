#!/usr/bin/env python3
# reBot MuJoCo 仿真 · 一键自检（不需要 ROS）。[Added by fanhao375 2026-07-01]
# 验证模型层：能加载、关节/执行器解析(节点靠它映射)、物理不发散、执行器能驱动关节。
# ROS 收发那层要在 Linux 上用 ros2 topic echo/pub 验（见 README），本脚本不碰 ROS。
# 用法:  python selfcheck.py [reBot_scene.xml]    或   MJCF_SCENE=路径 python selfcheck.py
import os
import sys
import numpy as np
import mujoco

JOINTS = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6']


def main():
    scene = os.environ.get('MJCF_SCENE') or (sys.argv[1] if len(sys.argv) > 1 else 'reBot_scene.xml')
    if not os.path.isfile(scene):
        sys.exit('找不到 %s，先跑 urdf_to_mjcf.py 生成。' % scene)
    fails = []

    def check(name, ok, detail=''):
        print(('[PASS] ' if ok else '[FAIL] ') + name + (('  —  ' + detail) if detail else ''))
        if not ok:
            fails.append(name)

    # 1. 加载
    try:
        m = mujoco.MjModel.from_xml_path(os.path.abspath(scene))
        d = mujoco.MjData(m)
        check('模型加载', True, '%d 关节 / %d 执行器 / %d 几何体' % (m.njnt, m.nu, m.ngeom))
    except Exception as e:
        check('模型加载', False, str(e)[:200])
        print('\n模型加载不了，后面免谈。')
        sys.exit(1)

    # 2. 关节 + 执行器解析（ROS 节点就靠 mj_name2id 这样映射）
    qadr, act = {}, {}
    for jn in JOINTS:
        jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, jn)
        aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, jn)
        if jid >= 0:
            qadr[jn] = m.jnt_qposadr[jid]
        if aid >= 0:
            act[jn] = aid
    check('6 个关节都在', len(qadr) == 6, '解析到 ' + ','.join(qadr.keys()))
    check('6 个执行器都在', len(act) == 6, '解析到 ' + ','.join(act.keys()))

    # 3. 物理稳定：ctrl = 当前 qpos，跑 2 秒，别炸别飞走
    for jn, aid in act.items():
        d.ctrl[aid] = d.qpos[qadr[jn]]
    for _ in range(int(2.0 / m.opt.timestep)):
        mujoco.mj_step(m, d)
    finite = bool(np.all(np.isfinite(d.qpos)) and np.all(np.isfinite(d.qvel)))
    bounded = float(np.max(np.abs(d.qpos))) < 100
    settled = float(np.max(np.abs(d.qvel))) < 5
    check('物理不发散（2s 后有限 + 有界）', finite and bounded, 'max|qpos|=%.2f' % float(np.max(np.abs(d.qpos))))
    check('执行器托得住自重（2s 后基本静止）', settled, 'max|qvel|=%.3f rad/s' % float(np.max(np.abs(d.qvel))))

    # 4. 控制：命令 joint1 → +0.5 rad，跑 1.5 秒，看它有没有靠近
    if 'joint1' in act:
        tgt = 0.5
        d.ctrl[act['joint1']] = tgt
        for _ in range(int(1.5 / m.opt.timestep)):
            mujoco.mj_step(m, d)
        reached = float(d.qpos[qadr['joint1']])
        check('执行器能驱动关节（joint1 → 0.5）', abs(reached - tgt) < 0.15, 'joint1 实到 %.3f rad' % reached)

    print('')
    if not fails:
        print('==> 全部通过 ✅  模型 + 物理 + 控制逻辑 OK。剩 ROS 收发(/joint_states、cmd/pos_vel)与网页跟随，需在 Linux+ROS 上验。')
        sys.exit(0)
    else:
        print('==> 有 %d 项没过：%s（把上面 [FAIL] 行贴给我修）' % (len(fails), ', '.join(fails)))
        sys.exit(2)


if __name__ == '__main__':
    main()
