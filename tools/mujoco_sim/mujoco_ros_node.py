#!/usr/bin/env python3
# reBot B601-DM · MuJoCo 物理仿真 ROS2 节点（物理仿真第4件的"桥后端"）。
# [Added by fanhao375 2026-07-01]
# 思路：让 MuJoCo 在 ROS 上"装成另一台 reBot 机器人"——发和真机同名的 /rebotarm/joint_states、
# 收和真机同样的 /rebotarm/joints/<j>/cmd/pos_vel。这样网页驾驶舱(经 rosbridge)的镜像/命令链路
# 一行不用改：连上这台的 rosbridge、开「跟随」，MuJoCo 的关节就映射进网页 3D；网页发命令就驱动 MuJoCo。
#
# 跑在哪：装了 ROS2 + mujoco + 编了 rebotarm_msgs(含 JointPosVelCmd) 的机器（机器人机/WSL）。见 README。
# 话题（必须和网页一致，已核对 rebot-ros-ui.js / rebot-ros-client.js）：
#   pub  /rebotarm/joint_states                         sensor_msgs/msg/JointState
#   sub  /rebotarm/joints/<joint>/cmd/pos_vel           rebotarm_msgs/msg/JointPosVelCmd  {pos, vlim, stamp}
import os
import sys
import threading

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

try:
    from rebotarm_msgs.msg import JointPosVelCmd
except Exception as e:  # noqa
    sys.exit('找不到 rebotarm_msgs（JointPosVelCmd）。先 source 编了该包的 ROS2 工作区再跑。错误：%s' % e)

try:
    import mujoco
except Exception as e:  # noqa
    sys.exit('需要 mujoco：pip install mujoco（错误：%s）' % e)

JOINTS = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6']
NS = 'rebotarm'


class MujocoRosNode(Node):
    def __init__(self, scene_path):
        super().__init__('rebotarm_mujoco_sim')
        self.model = mujoco.MjModel.from_xml_path(scene_path)
        self.data = mujoco.MjData(self.model)
        self._lock = threading.Lock()

        # 关节名 → qpos 地址 / dof 地址 / 执行器 id（按名字解析，模型顺序无关）
        self.qadr, self.dadr, self.act = {}, {}, {}
        for jn in JOINTS:
            jid = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_JOINT, jn)
            if jid < 0:
                self.get_logger().warn('模型里没有关节 %s（检查 MJCF 关节命名）' % jn)
                continue
            self.qadr[jn] = self.model.jnt_qposadr[jid]
            self.dadr[jn] = self.model.jnt_dofadr[jid]
            aid = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_ACTUATOR, jn)
            if aid >= 0:
                self.act[jn] = aid
        # 初始 ctrl = 当前 qpos（别一上来就往 0 冲）
        for jn, aid in self.act.items():
            self.data.ctrl[aid] = self.data.qpos[self.qadr[jn]]

        self.pub = self.create_publisher(JointState, '/%s/joint_states' % NS, 10)
        self.subs = []
        for jn in JOINTS:
            topic = '/%s/joints/%s/cmd/pos_vel' % (NS, jn)
            self.subs.append(self.create_subscription(
                JointPosVelCmd, topic, self._make_cb(jn), 10))

        self.dt_pub = 0.02  # 50Hz 发布 + 推进物理
        self.substeps = max(1, int(round(self.dt_pub / self.model.opt.timestep)))
        self.create_timer(self.dt_pub, self._tick)

        self.viewer = None
        if os.environ.get('MUJOCO_VIEWER', '0') == '1':
            import mujoco.viewer
            self.viewer = mujoco.viewer.launch_passive(self.model, self.data)
        self.get_logger().info('reBot MuJoCo 仿真起来了：发 /%s/joint_states，收 6 路 cmd/pos_vel，%d 倍子步/帧'
                               % (NS, self.substeps))

    def _make_cb(self, jn):
        def cb(msg):
            aid = self.act.get(jn)
            if aid is None:
                return
            lo, hi = self.model.actuator_ctrlrange[aid]
            with self._lock:
                self.data.ctrl[aid] = float(min(max(msg.pos, lo), hi))  # 钳到限位
        return cb

    def _tick(self):
        with self._lock:
            for _ in range(self.substeps):
                mujoco.mj_step(self.model, self.data)
            js = JointState()
            js.header.stamp = self.get_clock().now().to_msg()
            js.name = list(self.qadr.keys())
            js.position = [float(self.data.qpos[self.qadr[jn]]) for jn in js.name]
            js.velocity = [float(self.data.qvel[self.dadr[jn]]) for jn in js.name]
        self.pub.publish(js)
        if self.viewer is not None:
            try:
                self.viewer.sync()
            except Exception:
                self.viewer = None


def main():
    scene = os.environ.get('MJCF_SCENE') or (sys.argv[1] if len(sys.argv) > 1 else 'reBot_scene.xml')
    if not os.path.isfile(scene):
        sys.exit('找不到场景文件 %s。先跑 urdf_to_mjcf.py 生成，或用 MJCF_SCENE/参数指定。' % scene)
    rclpy.init()
    node = MujocoRosNode(os.path.abspath(scene))
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
