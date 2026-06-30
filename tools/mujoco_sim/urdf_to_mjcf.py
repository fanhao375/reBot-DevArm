#!/usr/bin/env python3
# reBot B601-DM：URDF → MuJoCo MJCF 转换 + 加执行器/阻尼/场景。
# [Added by fanhao375 2026-07-01] 物理仿真(第4件)用。在装了 mujoco 的机器上跑一次，产出 reBot_scene.xml。
#
# 为什么用脚本而不是手写 MJCF：让 mujoco 自己的 URDF 导入器去做 body/joint/inertial/mesh 的转换（可靠），
# 我们只在它产出的基础上加 ① 执行器(position) ② 关节阻尼/armature ③ 地面/光/天空盒。kp/阻尼是先验值，
# 必须在 `python -m mujoco.viewer reBot_scene.xml` 里看着调（见 README）。
#
# 用法:
#   python urdf_to_mjcf.py \
#     --urdf  ../../software/reBotArmController_ROS2/src/rebotarm_bringup/description/urdf/reBot-DevArm_fixend.urdf \
#     --meshes ../../software/reBotArmController_ROS2/src/rebotarm_bringup/description/meshes \
#     --out   reBot_scene.xml
import argparse, os, re, sys, tempfile
import xml.etree.ElementTree as ET

# 关节力矩(URDF effort)：J1-3=27N·m, J4-6=7N·m。forcerange 用它；kp/阻尼按大小分两档先验，viewer 里再调。
EFFORT = {'joint1': 27, 'joint2': 27, 'joint3': 27, 'joint4': 7, 'joint5': 7, 'joint6': 7}
KP = {'joint1': 2200, 'joint2': 2600, 'joint3': 1600, 'joint4': 500, 'joint5': 400, 'joint6': 300}
KV = {'joint1': 80, 'joint2': 90, 'joint3': 60, 'joint4': 20, 'joint5': 16, 'joint6': 12}
DAMP = {'joint1': 4, 'joint2': 6, 'joint3': 4, 'joint4': 1.2, 'joint5': 1.0, 'joint6': 0.8}
# armature(转子等效惯量)：先验值。原来 0.1+ 太大(臂显得沉/迟钝，比连杆自身惯量大一两个量级)，下调。viewer 里再调。
ARMATURE = {'joint1': 0.03, 'joint2': 0.04, 'joint3': 0.025, 'joint4': 0.012, 'joint5': 0.01, 'joint6': 0.008}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--urdf', required=True)
    ap.add_argument('--meshes', required=True, help='STL 网格目录')
    ap.add_argument('--out', default='reBot_scene.xml')
    args = ap.parse_args()

    try:
        import mujoco
    except Exception as e:
        sys.exit('需要 mujoco：pip install mujoco  （错误：%s）' % e)

    meshes_abs = os.path.abspath(args.meshes).replace('\\', '/')  # 正斜杠：跨平台 + 避免 re/属性里反斜杠转义
    urdf_text = open(args.urdf, 'r', encoding='utf-8').read()
    # MuJoCo 的 URDF 加载器不认 package://，去掉前缀只留文件名（配合 compiler meshdir）。
    urdf_text = re.sub(r'package://[^"]*?/meshes/', '', urdf_text)
    # 注入 <mujoco> 编译块：meshdir 指网格目录；balanceinertia 修 SolidWorks 惯量校验；autolimits 用 URDF 限位。
    mj_block = ('<mujoco><compiler meshdir="%s" balanceinertia="true" '
                'discardvisual="false" autolimits="true"/></mujoco>' % meshes_abs)
    # 用函数替换，别用模板字符串——meshdir 路径里的反斜杠会被 re 当转义(\c 之类)炸掉。
    urdf_text = re.sub(r'(<robot\b[^>]*>)', lambda m: m.group(1) + '\n  ' + mj_block, urdf_text, count=1)

    tmp = tempfile.NamedTemporaryFile('w', suffix='.urdf', delete=False, encoding='utf-8')
    tmp.write(urdf_text); tmp.close()

    print('>>> 用 mujoco 编译 URDF…')
    model = mujoco.MjModel.from_xml_path(tmp.name)        # 编译失败会在这抛错(惯量/mesh/限位)
    robot_xml = os.path.join(os.path.dirname(os.path.abspath(args.out)), 'reBot_robot.xml')
    mujoco.mj_saveLastXML(robot_xml, model)
    print('>>> 机器人本体 MJCF 已存:', robot_xml)

    # 收集 hinge 关节名 + 限位（从已编译模型，最可靠）
    joints = []
    for j in range(model.njnt):
        if model.jnt_type[j] == mujoco.mjtJoint.mjJNT_HINGE:
            name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, j)
            lo, hi = model.jnt_range[j]
            joints.append((name, float(lo), float(hi)))
    print('>>> hinge 关节:', [n for n, _, _ in joints])

    # 在本体基础上：给关节加阻尼/armature、加执行器、加场景，写成单文件 reBot_scene.xml
    tree = ET.parse(robot_xml)
    root = tree.getroot()

    # [S1 修复] 强制 compiler autolimits=true：执行器只写了 ctrlrange/forcerange 没写 *limited，
    # autolimits=false 时 MuJoCo 会编译报错。不赌 mj_saveLastXML 有没有保留我们注入的设置，这里直接坐实。
    comp = root.find('compiler')
    if comp is None:
        comp = ET.SubElement(root, 'compiler')
    comp.set('autolimits', 'true')

    # [M1 修复] 关闭接触：URDF 的相邻连杆全分辨率碰撞网格凸包化后在关节处互相穿透 → 自碰约束力把臂"焊死"
    # (实测 qfrc_actuator 27 被 qfrc_constraint -27 抵消，关节不动)。MVP 是固定底座、无物体、不抓取，不需要接触；
    # 以后做抓取再开接触并加相邻连杆 <contact><exclude> 过滤。
    opt = root.find('option')
    if opt is None:
        opt = ET.SubElement(root, 'option')
    flag = opt.find('flag')
    if flag is None:
        flag = ET.SubElement(opt, 'flag')
    flag.set('contact', 'disable')

    for jel in root.iter('joint'):
        nm = jel.get('name')
        if nm in DAMP:
            jel.set('damping', str(DAMP[nm]))
            jel.set('armature', str(ARMATURE[nm]))
            jel.set('frictionloss', '0.2')

    act = ET.SubElement(root, 'actuator')
    for nm, lo, hi in joints:
        if nm not in KP:
            continue
        f = EFFORT.get(nm, 10)
        ET.SubElement(act, 'position', {
            'name': nm, 'joint': nm, 'kp': str(KP[nm]), 'kv': str(KV[nm]),
            'ctrlrange': '%.4f %.4f' % (lo, hi), 'forcerange': '-%d %d' % (f, f),
        })

    vis = root.find('visual')                 # [M2 修复] 先 find 再建，和 asset/worldbody 一致，避免重复段
    if vis is None:
        vis = ET.SubElement(root, 'visual')
    ET.SubElement(vis, 'headlight', {'diffuse': '0.6 0.6 0.6', 'ambient': '0.3 0.3 0.3', 'specular': '0 0 0'})
    ET.SubElement(vis, 'global', {'azimuth': '160', 'elevation': '-20'})

    asset = root.find('asset')
    if asset is None:
        asset = ET.SubElement(root, 'asset')
    ET.SubElement(asset, 'texture', {'type': 'skybox', 'builtin': 'gradient', 'rgb1': '0.3 0.5 0.7', 'rgb2': '0 0 0', 'width': '512', 'height': '3072'})
    ET.SubElement(asset, 'texture', {'type': '2d', 'name': 'groundplane', 'builtin': 'checker', 'mark': 'edge', 'rgb1': '0.2 0.3 0.4', 'rgb2': '0.1 0.2 0.3', 'markrgb': '0.8 0.8 0.8', 'width': '300', 'height': '300'})
    ET.SubElement(asset, 'material', {'name': 'groundplane', 'texture': 'groundplane', 'texuniform': 'true', 'texrepeat': '5 5', 'reflectance': '0.2'})

    wb = root.find('worldbody')
    if wb is None:
        wb = ET.SubElement(root, 'worldbody')
    ET.SubElement(wb, 'light', {'pos': '0 0 3.5', 'dir': '0 0 -1', 'directional': 'true'})
    ET.SubElement(wb, 'geom', {'name': 'floor', 'size': '0 0 0.05', 'pos': '0 0 0', 'type': 'plane', 'material': 'groundplane'})

    tree.write(args.out, encoding='unicode', xml_declaration=False)
    print('>>> 完成 → %s' % os.path.abspath(args.out))
    print('>>> 下一步：python -m mujoco.viewer %s  看臂是否站住、执行器托得住自重；不对就调本文件顶部 KP/DAMP/ARMATURE。' % args.out)


if __name__ == '__main__':
    main()
