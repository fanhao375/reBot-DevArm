#!/bin/bash
# 起 reBot MuJoCo 仿真 ROS 节点（物理仿真第4件）。[Added by fanhao375 2026-07-01]
# env：
#   ROS_SETUP       编了 rebotarm_msgs 的工作区 setup.bash（如 ~/rebot_ws/install/setup.bash）
#   MJCF_SCENE      场景文件（默认本目录 reBot_scene.xml；没有就先跑 urdf_to_mjcf.py）
#   MUJOCO_VIEWER=1 同时开本地 MuJoCo 窗口看（调试用）
#   SIM_VENV / SIM_CONDA_ENV  提供 mujoco 的 venv/conda（二选一，可不填若系统 python 已有 mujoco）
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
export MJCF_SCENE="${MJCF_SCENE:-$DIR/reBot_scene.xml}"

if [ -n "${ROS_SETUP:-}" ]; then
  # shellcheck disable=SC1090
  source "$ROS_SETUP"
fi
if [ -n "${SIM_VENV:-}" ]; then
  # shellcheck disable=SC1091
  source "$SIM_VENV/bin/activate"
elif [ -n "${SIM_CONDA_ENV:-}" ]; then
  # shellcheck disable=SC1091
  source ~/miniforge3/etc/profile.d/conda.sh
  conda activate "$SIM_CONDA_ENV"
fi

if [ ! -f "$MJCF_SCENE" ]; then
  echo "找不到 $MJCF_SCENE —— 先生成模型：" >&2
  echo "  python3 $DIR/urdf_to_mjcf.py --urdf <reBot.urdf> --meshes <meshes目录> --out $MJCF_SCENE" >&2
  exit 1
fi

echo ">>> 场景: $MJCF_SCENE"
echo ">>> 网页要连得上，需另开一个终端起 rosbridge："
echo "    ros2 launch rosbridge_server rosbridge_websocket_launch.xml"
echo ">>> 然后浏览器 cockpit 里把 ROS WebSocket 填 ws://<本机IP>:9090 → 连接 → 开「跟随」"
exec python3 "$DIR/mujoco_ros_node.py"
