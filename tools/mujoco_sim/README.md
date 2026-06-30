# reBot MuJoCo 物理仿真（外部 MuJoCo + rosbridge）

物理仿真第 4 件。**核心思路：让 MuJoCo 在 ROS 上「装成另一台 reBot 机器人」**——发和真机同名的
`/rebotarm/joint_states`、收同样的 `/rebotarm/joints/<j>/cmd/pos_vel`。这样网页驾驶舱（经 rosbridge）
的镜像/命令链路**一行不用改**：网页分不清关节状态来自真臂还是 MuJoCo。中间桥 = 你已经在用的 rosbridge。

```
浏览器 cockpit ──(rosbridge ws://:9090)── /rebotarm/joint_states ◄── MuJoCo 物理(本节点)
   ▲ 3D 跟随(镜像)                          /rebotarm/joints/*/cmd/pos_vel ──► MuJoCo ctrl
   └ 发命令 ───────────────────────────────────────────────────────────────────┘
```

## 跑在哪
装了 **ROS2 + mujoco + 编了 `rebotarm_msgs`(含 JointPosVelCmd)** 的机器（机器人机 / WSL）。
**不在网页那台跑物理**——网页只是经 rosbridge 看/控这台。

## 一次性准备
```bash
pip install mujoco                              # 物理引擎(python)
sudo apt install ros-$ROS_DISTRO-rosbridge-suite   # 网页靠 rosbridge 连进来（如没装）
# 确保 rebotarm_msgs 已编：在你的 ROS2 工作区 colcon build 后 source install/setup.bash
```

## 步骤
1. **生成物理模型**（用 mujoco 自己的 URDF 导入器转，再加执行器/阻尼/地面）：
   ```bash
   cd tools/mujoco_sim
   python urdf_to_mjcf.py \
     --urdf  ../../software/reBotArmController_ROS2/src/rebotarm_bringup/description/urdf/reBot-DevArm_fixend.urdf \
     --meshes ../../software/reBotArmController_ROS2/src/rebotarm_bringup/description/meshes \
     --out reBot_scene.xml
   ```
2. **先自检/桌面验证再上 ROS**（最值的一步：模型/物理/控制问题在这全暴露，已在开发机 Windows 上跑通）：
   ```bash
   python selfcheck.py reBot_scene.xml      # 一键自检(不需 ROS)：加载/关节解析/物理不发散/执行器能驱动关节 → 全 PASS 才往下
   python -m mujoco.viewer reBot_scene.xml   # 有桌面的话再肉眼看一眼(可选)
   ```
   - selfcheck 全 PASS = 模型+物理+控制逻辑没问题。有 [FAIL] 把那行贴出来。
   - viewer 里：臂应**站住**（执行器托得住自重、不软趴不抖）。软趴=调大 `urdf_to_mjcf.py` 顶部 `KP`；抖/迟钝=调 `KV`/`DAMP`/`ARMATURE`。
   - **注意**：MVP 已**关闭接触**（`<flag contact="disable">`），因为 URDF 全分辨率碰撞网格相邻连杆会自碰把臂"焊死"。所以现在臂**穿过自己/地面不挡**是正常的；以后做抓取再开接触 + 加相邻连杆 `<contact><exclude>`。
3. **起 rosbridge**（另一个终端，网页靠它连进来）：
   ```bash
   ros2 launch rosbridge_server rosbridge_websocket_launch.xml
   ```
4. **起仿真节点**：
   ```bash
   ROS_SETUP=~/你的ws/install/setup.bash bash run_mujoco_sim.sh
   #   想同时开本地 MuJoCo 窗口看： MUJOCO_VIEWER=1 ROS_SETUP=... bash run_mujoco_sim.sh
   #   mujoco 在 venv/conda 里： 再加 SIM_VENV=/path/venv 或 SIM_CONDA_ENV=名字
   ```
5. **网页连上**：浏览器开 cockpit → ROS 面板 WebSocket 填 `ws://<这台IP>:9090` → 连接 →
   顶栏开 **「跟随」** → MuJoCo 的关节实时映射进 3D。要让网页驱动仿真：勾「允许网页发控制」+ 模式选
   `仿真驱动 (fake)` 或直接发滑块/IK → 命令经 `cmd/pos_vel` 进 MuJoCo，物理算完再 joint_states 回来。

## MVP 范围（这版有/没有）
- ✅ 关节镜像（MuJoCo→3D）、6 轴 `cmd/pos_vel` 驱动（网页→MuJoCo）、重力下的真实下垂/超调。
- ❌ 夹爪（reBot URDF 里没有夹爪关节，物理模型暂无；网页夹爪按钮对仿真无效）。
- ❌ enable/disable / 重力补偿 / IK / move_to_pose 等**服务**——那些是真控制器的，仿真没起这些 service，
  网页点了会报「服务不存在」，**属正常**（仿真只实现 joint_states + pos_vel 这条最小链路）。
- ⚠️ 网页诊断面板里 **「臂状态」「夹爪」两格会一直红/等待**——仿真不发 `arm_status` / `gripper/state` 话题，**正常**，不影响跟随/控制。
- ⚠️ **`vlim`(限速)被忽略**：仿真里关节速度由 kp/kv/forcerange 决定，网页的 vlim 滑块对仿真无效（真机才用它限速）。

## 注意
- **别同时**把真机和这个仿真都连到同一个 `rebotarm` namespace（话题会打架）。要么连真机、要么连仿真。
- kp/阻尼/armature 是先验值，**必须在 viewer 里按手感调**（见步骤 2）。调好的值填回 `urdf_to_mjcf.py` 顶部常量重生成。
- 这套是「写好你来跑/调」：物理要在 Linux+ROS+mujoco 上才跑得起来，开发机(Windows)只出代码。
