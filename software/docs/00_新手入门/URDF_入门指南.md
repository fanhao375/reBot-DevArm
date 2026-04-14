# URDF 入门指南

> 面向机械工程师/硬件工程师的 URDF 快速入门

---

## 一、什么是 URDF？

### 1.1 一句话解释

**URDF = 机器人的"数字图纸"**，用 XML 格式描述机器人的结构、尺寸、质量、关节类型等信息。

就像你画机械图纸时会标注：
- 零件的形状（3D 模型）
- 零件之间的连接方式（螺栓/轴承/铰链）
- 运动范围（转动角度限制）
- 物理属性（质量、惯性）

URDF 把这些信息写成计算机能读懂的格式，让软件知道"这台机器人长什么样、怎么动"。

### 1.2 为什么需要 URDF？

| 场景 | 没有 URDF | 有了 URDF |
|------|-----------|----------|
| **可视化** | 手动画 3D 模型 | 软件自动显示机器人姿态 |
| **运动学计算** | 手算 DH 参数 + 矩阵 | Pinocchio 自动算 FK/IK |
| **仿真** | 无法仿真 | Gazebo/Isaac Sim 直接导入 |
| **ROS 控制** | 手写控制器 | ROS 自动识别关节 |

**核心价值**：写一次 URDF，所有工具都能用（可视化、仿真、控制）。

---

## 二、URDF 的基本结构

### 2.1 两个核心概念

#### Link（连杆）= 机器人的"零件"

就像机械图纸里的"零件号"，每个 link 是一个刚体部件。

```xml
<link name="base_link">
  <!-- 外观：用什么 3D 模型显示 -->
  <visual>
    <geometry>
      <mesh filename="package://.../meshes/base_link.STL"/>
    </geometry>
    <material name="gray">
      <color rgba="0.5 0.5 0.5 1.0"/>
    </material>
  </visual>

  <!-- 物理属性：质量、惯性 -->
  <inertial>
    <mass value="0.5"/>  <!-- 单位：kg -->
    <inertia ixx="0.01" ixy="0" ixz="0"
             iyy="0.01" iyz="0" izz="0.01"/>
  </inertial>

  <!-- 碰撞体积（仿真用） -->
  <collision>
    <geometry>
      <mesh filename="package://.../meshes/base_link.STL"/>
    </geometry>
  </collision>
</link>
```

**类比**：
- `<visual>` = 零件的外观图（给人看的）
- `<collision>` = 零件的碰撞包络（给仿真引擎算碰撞用的）
- `<inertial>` = 零件的物理参数（质量、转动惯量）

#### Joint（关节）= 零件之间的"连接方式"

就像机械图纸里的"装配关系"，定义两个 link 怎么连接、怎么运动。

```xml
<joint name="joint1" type="revolute">
  <!-- 父子关系 -->
  <parent link="base_link"/>
  <child link="link1"/>

  <!-- 关节位置（相对父 link 的坐标） -->
  <origin xyz="0 0 0.1" rpy="0 0 0"/>

  <!-- 转动轴 -->
  <axis xyz="0 0 1"/>  <!-- 绕 Z 轴转 -->

  <!-- 运动范围 -->
  <limit lower="-3.14159" upper="3.14159"  <!-- 单位：弧度 -->
         effort="100"                       <!-- 最大扭矩：N·m -->
         velocity="2.0"/>                   <!-- 最大速度：rad/s -->

  <!-- 动力学参数 -->
  <dynamics damping="0.1" friction="0.05"/>
</joint>
```

**关节类型**：

| 类型 | 机械对应 | 自由度 |
|------|---------|-------|
| `revolute` | 铰链/轴承（有限转角） | 1（转动） |
| `continuous` | 连续旋转轴承 | 1（无限转） |
| `prismatic` | 滑轨/气缸 | 1（平移） |
| `fixed` | 螺栓固定 | 0（不动） |
| `planar` | 平面滑动 | 2（XY 平移） |
| `floating` | 自由漂浮 | 6（3 平移 + 3 转动） |

### 2.2 树状结构

机器人是一棵"树"：

```
base_link (底座)
   ↓ joint1
link1 (大臂)
   ↓ joint2
link2 (小臂)
   ↓ joint3
link3 (腕部)
   ↓ ...
end_link (末端)
```

**规则**：
- 每个 joint 连接一个 parent link 和一个 child link
- 从 base_link（根）开始，逐级向下
- 不能有环路（不是闭链机构）

---

## 三、reBot-DevArm 的 URDF 详解

### 3.1 文件位置

```
urdf/reBot-DevArm_fixend_description/
├── urdf/
│   └── reBot-DevArm_fixend.urdf  ← 主文件（打开看这个）
├── meshes/                        ← 3D 模型文件
│   ├── base_link.STL              ← 底座
│   ├── link1.STL                  ← 大臂（肩部）
│   ├── link2.STL                  ← 小臂（肘部）
│   ├── link3.STL                  ← 腕部 1
│   ├── link4.STL                  ← 腕部 2
│   ├── link5.STL                  ← 腕部 3
│   └── end_link.STL               ← 末端法兰
└── config/
    └── joint_limits.yaml          ← 关节限位配置
```

### 3.2 机械结构对应关系

| URDF 名称 | 实体零件 | 电机型号 | 关节类型 |
|-----------|---------|---------|---------|
| `base_link` | 底座（固定在桌面） | — | — |
| `joint1` | 底座旋转轴（腰） | DM4340P | revolute |
| `link1` | 大臂（肩部连杆） | — | — |
| `joint2` | 肩关节 | DM4340P | revolute |
| `link2` | 小臂（肘部连杆） | — | — |
| `joint3` | 肘关节 | DM4340P | revolute |
| `link3` | 前臂（腕部连杆 1） | — | — |
| `joint4` | 腕关节 1（俯仰） | DM4310 | revolute |
| `link4` | 腕部连杆 2 | — | — |
| `joint5` | 腕关节 2（翻转） | DM4310 | revolute |
| `link5` | 腕部连杆 3 | — | — |
| `joint6` | 腕关节 3（旋转） | DM4310 | revolute |
| `end_link` | 末端法兰（装夹爪） | — | — |

**总结**：6 个 revolute 关节 = 6 自由度机械臂

### 3.3 关键参数解读

打开 `reBot-DevArm_fixend.urdf`，找到 `joint1`：

```xml
<joint name="joint1" type="revolute">
  <parent link="base_link"/>
  <child link="link1"/>
  <origin xyz="0 0 0.0935" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
  <limit lower="-3.14159" upper="3.14159" effort="27" velocity="10"/>
</joint>
```

**参数含义**：

| 参数 | 值 | 含义 |
|------|---|------|
| `xyz="0 0 0.0935"` | Z 方向偏移 93.5mm | 关节轴心距离底座顶面的高度 |
| `axis="0 0 1"` | Z 轴 | 绕竖直轴旋转（腰转） |
| `lower="-3.14159"` | -180° | 最小转角 |
| `upper="3.14159"` | +180° | 最大转角 |
| `effort="27"` | 27 N·m | DM4340P 的额定扭矩 |
| `velocity="10"` | 10 rad/s | 最大角速度（约 573°/s） |

### 3.4 质量和惯性

```xml
<inertial>
  <mass value="0.5"/>
  <origin xyz="0 0 0.05" rpy="0 0 0"/>
  <inertia ixx="0.001" ixy="0" ixz="0"
           iyy="0.001" iyz="0" izz="0.001"/>
</inertial>
```

**如何测量/估算**：
1. **质量**：用电子秤称零件重量
2. **质心位置** (`origin xyz`)：用 CAD 软件（SolidWorks/Fusion 360）查看质心坐标
3. **转动惯量** (`ixx/iyy/izz`)：CAD 软件自动计算，或用公式估算

**为什么重要**：
- 动力学仿真需要准确的惯性参数
- 重力补偿控制需要知道质量分布
- 轨迹规划需要考虑惯性力

---

## 四、常见操作

### 4.1 修改关节限位

**场景**：你发现 joint2 实际只能转 -120° ~ +120°，但 URDF 里写的是 -180° ~ +180°。

**步骤**：
1. 打开 `reBot-DevArm_fixend.urdf`
2. 找到 `<joint name="joint2">`
3. 修改 `<limit lower="-2.094" upper="2.094" .../>`（-120° = -2.094 rad）
4. 保存

**验证**：
```bash
python3 example/sim/fk_sim.py
# 输入 0 130 0 0 0 0，看是否超限
```

### 4.2 更新零件质量

**场景**：你换了更重的夹爪，末端质量从 0.2kg 变成 0.5kg。

**步骤**：
1. 找到 `<link name="end_link">`
2. 修改 `<mass value="0.5"/>`
3. 如果有 CAD 模型，同步更新 `<inertia>` 参数

**影响**：
- 重力补偿控制会自动调整扭矩输出
- 动力学仿真更准确

### 4.3 添加新的末端工具

**场景**：你想在 URDF 里加一个夹爪。

**步骤**：
1. 导出夹爪的 STL 文件（从 CAD）
2. 放到 `meshes/gripper.STL`
3. 在 URDF 里添加：

```xml
<link name="gripper_link">
  <visual>
    <geometry>
      <mesh filename="package://.../meshes/gripper.STL"/>
    </geometry>
  </visual>
  <inertial>
    <mass value="0.3"/>
    <inertia ixx="0.001" iyy="0.001" izz="0.001"/>
  </inertial>
</link>

<joint name="gripper_joint" type="fixed">
  <parent link="end_link"/>
  <child link="gripper_link"/>
  <origin xyz="0 0 0.05" rpy="0 0 0"/>
</joint>
```

4. 保存后，MeshCat 会自动显示夹爪

---

## 五、工具推荐

### 5.1 查看 URDF

**方法 1：文本编辑器**
- 直接用 VS Code / Notepad++ 打开 `.urdf` 文件
- 优点：看得清楚，方便修改
- 缺点：不直观

**方法 2：URDF 可视化工具**
- **urdf_viz**（Rust 工具）：`cargo install urdf-viz`
  ```bash
  urdf-viz urdf/reBot-DevArm_fixend_description/urdf/reBot-DevArm_fixend.urdf
  ```
- **RViz**（ROS 工具，仅 Linux）：
  ```bash
  roslaunch urdf_tutorial display.launch model:=reBot-DevArm_fixend.urdf
  ```

**方法 3：MeshCat（本项目自带）**
```bash
python3 example/sim/fk_sim.py
# 输入 0 0 0 0 0 0 查看归零姿态
```

### 5.2 验证 URDF 正确性

```bash
# 检查 XML 语法
check_urdf reBot-DevArm_fixend.urdf

# 查看关节树
urdf_to_graphiz reBot-DevArm_fixend.urdf
```

---

## 六、常见问题

### Q1：为什么路径是 `package://...`？

**A**：这是 ROS 的路径约定。
- `package://reBot-DevArm_description_fixend/meshes/base_link.STL`
- 会被替换成实际路径：`/path/to/urdf/reBot-DevArm_fixend_description/meshes/base_link.STL`

Pinocchio 需要你在代码里指定 `package_dirs`：
```python
pkg_dir = str(Path(urdf_path).parents[2])
model = pin.buildModelFromUrdf(urdf_path, package_dirs=[pkg_dir])
```

### Q2：STL 文件找不到怎么办？

**A**：检查三个地方：
1. STL 文件是否存在：`ls urdf/.../meshes/base_link.STL`
2. URDF 里的路径是否正确：`<mesh filename="package://..."/>`
3. 软链接是否失效（Windows + WSL 常见问题）：
   ```bash
   ls -la urdf/  # 看是否有 l 开头的符号链接
   ```

### Q3：修改 URDF 后不生效？

**A**：
1. 确认保存了文件
2. 重启 Python 脚本（Pinocchio 会缓存模型）
3. 检查是否改错了文件（有些项目有多个 URDF）

### Q4：如何从 CAD 导出 URDF？

**A**：
- **SolidWorks**：安装 `sw_urdf_exporter` 插件
- **Fusion 360**：安装 `fusion2urdf` 插件
- **Onshape**：使用 `onshape-to-robot` 工具

导出后需要手动调整：
- 关节限位（插件可能估算不准）
- 质量和惯性（需要设置材料密度）
- 碰撞体积（简化为基本几何体）

---

## 七、进阶阅读

- [ROS URDF 官方教程](http://wiki.ros.org/urdf/Tutorials)
- [URDF XML 规范](http://wiki.ros.org/urdf/XML)
- [Pinocchio URDF 加载文档](https://gepettoweb.laas.fr/doc/stack-of-tasks/pinocchio/master/doxygen-html/md_doc_b-examples_display_b-gepetto-viewer.html)

---

## 八、总结

| 概念 | 机械工程师的理解 |
|------|----------------|
| **URDF** | 装配图 + 零件表 + 物理参数表 |
| **Link** | 零件（刚体） |
| **Joint** | 连接方式（铰链/滑轨/固定） |
| **STL** | 零件的 3D 模型 |
| **origin** | 坐标系原点（装配基准） |
| **axis** | 运动轴线 |
| **limit** | 行程限位 |

**核心思想**：把机械图纸翻译成 XML 格式，让软件能"读懂"机器人的结构。

---

**下一步**：阅读 `MeshCat_可视化指南.md`，学习如何用浏览器查看 URDF 模型。
