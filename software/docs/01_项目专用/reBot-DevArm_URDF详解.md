# reBot-DevArm URDF 详解

> 逐行解读 reBot-DevArm_fixend.urdf 文件

---

## 文件概览

**文件位置**：`urdf/reBot-DevArm_fixend_description/urdf/reBot-DevArm_fixend.urdf`

**生成方式**：SolidWorks URDF Exporter 自动导出（从 CAD 模型）

**机器人结构**：
- 7 个 link（连杆）：base_link + link1~6 + end_link
- 7 个 joint（关节）：joint1~6（可动）+ end_joint（固定）
- 6 自由度机械臂

---

## 第一部分：文件头

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- This URDF was automatically created by SolidWorks to URDF Exporter! -->
<robot name="reBot-DevArm_fixend">
```

**解读**：
- `<?xml ...?>` — XML 文件声明，UTF-8 编码
- `<!-- ... -->` — 注释，说明这是 SolidWorks 自动导出的
- `<robot name="...">` — 机器人名称，`fixend` 表示"固定末端"（相对于可换末端版本）

---

## 第二部分：base_link（底座）

### 2.1 惯性参数

```xml
<link name="base_link">
  <inertial>
    <origin xyz="-1.857e-05 -3.149e-08 0.02357" rpy="0 0 0" />
    <mass value="0.83660000" />
    <inertia
      ixx="0.00133040"
      ixy="0.00000001"
      ixz="0.00000000"
      iyy="0.00213119"
      iyz="0.00000000"
      izz="0.00275877" />
  </inertial>
```

**逐行解读**：

| 参数 | 值 | 含义 |
|------|---|------|
| `<origin xyz="...">` | `(-0.0000186, -0.00000003, 0.02357)` | **质心位置**（相对 link 坐标系原点），单位：米 |
| | | 质心在 Z 方向偏移 23.57mm（底座重心略高于底面） |
| `<mass value="...">` | `0.8366 kg` | **质量**，从 SolidWorks 测量得到 |
| `ixx` | `0.00133` | **绕 X 轴的转动惯量**，单位：kg·m² |
| `iyy` | `0.00213` | **绕 Y 轴的转动惯量** |
| `izz` | `0.00276` | **绕 Z 轴的转动惯量**（最大，因为底座是圆盘状） |
| `ixy, ixz, iyz` | `≈0` | **惯性积**（几乎为 0，说明质量分布对称） |

**为什么重要**：
- 动力学仿真需要准确的惯性参数
- 重力补偿控制需要知道质心位置
- 轨迹规划需要考虑惯性力

### 2.2 视觉外观

```xml
  <visual>
    <origin xyz="0 0 0" rpy="0 0 0" />
    <geometry>
      <mesh filename="package://reBot-DevArm_description_fixend/meshes/base_link.STL" />
    </geometry>
    <material name="">
      <color rgba="0.753 0.753 0.753 1" />
    </material>
  </visual>
```

**逐行解读**：

| 参数 | 值 | 含义 |
|------|---|------|
| `<origin xyz="0 0 0">` | 原点 | 视觉模型的位置（相对 link 坐标系） |
| `<mesh filename="...">` | `base_link.STL` | **3D 模型文件路径** |
| `package://...` | ROS 包路径 | `package://` 会被替换成实际目录 |
| `<color rgba="...">` | `(0.753, 0.753, 0.753, 1)` | **颜色**：灰色（RGB 各 0.753），不透明（Alpha=1） |

**为什么这么写**：
- `package://` 是 ROS 约定，方便跨平台移植
- STL 文件是从 SolidWorks 导出的零件外形
- 灰色是默认材质颜色

### 2.3 碰撞体积

```xml
  <collision>
    <origin xyz="0 0 0" rpy="0 0 0" />
    <geometry>
      <mesh filename="package://reBot-DevArm_description_fixend/meshes/base_link.STL" />
    </geometry>
  </collision>
</link>
```

**解读**：
- `<collision>` — 用于仿真引擎计算碰撞检测
- 这里直接用 STL 文件作为碰撞体（精确但计算量大）
- 优化方案：用简化的几何体（box/cylinder）代替复杂 mesh

---

## 第三部分：joint1（底座旋转轴）

```xml
<joint name="joint1" type="revolute">
  <origin xyz="0 0 0.0708" rpy="0 0 0" />
  <parent link="base_link" />
  <child link="link1" />
  <axis xyz="0 0 1" />
  <limit
    lower="-3.14"
    upper="3.14"
    effort="27"
    velocity="50" />
</joint>
```

**逐行解读**：

| 参数 | 值 | 含义 |
|------|---|------|
| `type="revolute"` | 旋转关节 | 有限转角的旋转关节（相对 `continuous` 无限转） |
| `<origin xyz="0 0 0.0708">` | Z 偏移 70.8mm | **关节轴心距离 base_link 原点的高度** |
| | | 这是底座顶面到 joint1 轴心的距离 |
| `<parent link="base_link">` | 父连杆 | joint1 连接 base_link 和 link1 |
| `<child link="link1">` | 子连杆 | link1 会随 joint1 转动 |
| `<axis xyz="0 0 1">` | Z 轴 | **绕竖直轴旋转**（腰转） |
| `lower="-3.14"` | -180° | **最小转角**（-π 弧度） |
| `upper="3.14"` | +180° | **最大转角**（+π 弧度） |
| `effort="27"` | 27 N·m | **最大扭矩**（DM4340P 额定扭矩） |
| `velocity="50"` | 50 rad/s | **最大角速度**（约 2865°/s，这是理论值） |

**为什么这么写**：
- `xyz="0 0 0.0708"` 是从 CAD 模型测量的实际尺寸
- `axis="0 0 1"` 表示绕 Z 轴转，符合底座旋转的物理结构
- `effort="27"` 来自 DM4340P 电机规格书
- `velocity="50"` 是保守估计（实际控制时会限制更低）

---

## 第四部分：link1（大臂）

```xml
<link name="link1">
  <inertial>
    <origin xyz="0.00947 -0.000917 0.02658" rpy="0 0 0" />
    <mass value="0.16130000" />
    <inertia
      ixx="0.00025207"
      ixy="0.00000000"
      ixz="-0.00002832"
      iyy="0.00015464"
      iyz="0.00000000"
      izz="0.00023416" />
  </inertial>
  <visual>
    <geometry>
      <mesh filename="package://reBot-DevArm_description_fixend/meshes/link1.STL" />
    </geometry>
    <material name="">
      <color rgba="0.753 0.753 0.753 1" />
    </material>
  </visual>
  <collision>
    <geometry>
      <mesh filename="package://reBot-DevArm_description_fixend/meshes/link1.STL" />
    </geometry>
  </collision>
</link>
```

**关键参数**：
- **质量**：0.161 kg（比底座轻很多）
- **质心**：`(0.00947, -0.000917, 0.02658)` m
- **转动惯量**：`ixx=0.000252`（link1 是细长杆状，绕 X 轴惯量最大）

**结构说明**：
- link1 是连接底座和肩关节的短连杆
- 主要作用是把 joint1（腰转）和 joint2（肩抬）的轴心错开

---

## 第五部分：joint2（肩关节）

```xml
<joint name="joint2" type="revolute">
  <origin xyz="0.02 0.035625 0.0497" rpy="-1.5708 0 0" />
  <parent link="link1" />
  <child link="link2" />
  <axis xyz="0 0 -1" />
  <limit
    lower="-3.14"
    upper="0"
    effort="27"
    velocity="50" />
</joint>
```

**重点解读**：

| 参数 | 值 | 含义 |
|------|---|------|
| `xyz="0.02 0.035625 0.0497"` | 3D 偏移 | 相对 link1 坐标系的位置 |
| | X: 20mm | 向前偏移 |
| | Y: 35.625mm | 向侧面偏移 |
| | Z: 49.7mm | 向上偏移 |
| `rpy="-1.5708 0 0"` | Roll -90° | **坐标系旋转**（-π/2 弧度） |
| | | 把 link2 的 Z 轴转到水平方向 |
| `axis="0 0 -1"` | -Z 轴 | 绕负 Z 轴转（因为坐标系转了 90°） |
| `lower="-3.14"` | -180° | 最小转角 |
| `upper="0"` | 0° | **最大转角只能到 0°**（不能往上抬超过水平） |

**为什么 `rpy="-1.5708 0 0"`**：
- SolidWorks 导出时，link2 的局部坐标系 Z 轴是竖直的
- 但实际肩关节是水平转动的
- 所以用 Roll -90° 把坐标系转过来，让 Z 轴变成水平
- 这样 `axis="0 0 -1"` 就表示绕水平轴转

**为什么 `upper="0"`**：
- 这是机械限位
- joint2 只能从 -180° 转到 0°（大臂从竖直向下到水平）
- 不能往上抬超过水平面（会撞到底座）

---

## 第六部分：link2（小臂）

```xml
<link name="link2">
  <inertial>
    <origin xyz="-0.1329 -0.00326 -0.0349" rpy="0 0 0" />
    <mass value="1.32660000" />
    <inertia
      ixx="0.00073374"
      ixy="-0.00000043"
      ixz="0.00000851"
      iyy="0.01255987"
      iyz="0.00000128"
      izz="0.01281387" />
  </inertial>
  ...
</link>
```

**关键参数**：
- **质量**：1.327 kg（**最重的连杆**，因为包含大臂和肘关节电机）
- **质心**：`(-0.1329, -0.00326, -0.0349)` m
  - X: -132.9mm（质心在大臂中段偏后）
  - 这个偏移很重要，影响重力补偿计算
- **转动惯量**：`iyy=0.01256`（绕 Y 轴最大，因为是长杆）

---

## 第七部分：joint3（肘关节）

```xml
<joint name="joint3" type="revolute">
  <origin xyz="-0.2405 0 0" rpy="0 0 0" />
  <parent link="link2" />
  <child link="link3" />
  <axis xyz="0 0 -1" />
  <limit
    lower="-3.14"
    upper="0"
    effort="27"
    velocity="50" />
</joint>
```

**重点**：
- `xyz="-0.2405 0 0"` — X 方向偏移 -240.5mm（**大臂长度**）
- `axis="0 0 -1"` — 绕 -Z 轴转（和 joint2 同方向）
- `upper="0"` — 同样只能弯到 0°，不能反向弯曲

---

## 第八部分：link3~link6（腕部三连杆）

```xml
<link name="link3">
  <mass value="0.83530000" />
  ...
</link>

<joint name="joint4" type="revolute">
  <origin xyz="-0.2405 0 0" rpy="0 1.5708 0" />
  <axis xyz="0 0 1" />
  <limit lower="-3.14" upper="3.14" effort="7" velocity="50" />
</joint>

<link name="link4">
  <mass value="0.14970000" />
  ...
</link>

<joint name="joint5" type="revolute">
  <origin xyz="0 0 0" rpy="0 -1.5708 0" />
  <axis xyz="0 0 1" />
  <limit lower="-3.14" upper="3.14" effort="7" velocity="50" />
</joint>

<link name="link5">
  <mass value="0.14970000" />
  ...
</link>

<joint name="joint6" type="revolute">
  <origin xyz="0 0 0" rpy="0 1.5708 0" />
  <axis xyz="0 0 1" />
  <limit lower="-3.14" upper="3.14" effort="7" velocity="50" />
</joint>

<link name="link6">
  <mass value="0.14970000" />
  ...
</link>
```

**腕部结构总结**：

| 关节 | 偏移 | 转轴方向 | 扭矩 | 电机 | 作用 |
|------|------|---------|------|------|------|
| joint4 | X: -240.5mm | Z 轴 | 7 N·m | DM4310 | 腕部俯仰 |
| joint5 | 0 | Z 轴 | 7 N·m | DM4310 | 腕部翻转 |
| joint6 | 0 | Z 轴 | 7 N·m | DM4310 | 腕部旋转 |

**为什么 joint4/5/6 的 `origin xyz="0 0 0"` 或只有一个方向偏移**：
- 腕部三个关节是**球腕结构**（三轴交于一点）
- joint4 在小臂末端（X 偏移 -240.5mm）
- joint5 和 joint6 的轴心重合（`xyz="0 0 0"`）
- 通过 `rpy` 旋转坐标系，让三个轴互相垂直

**为什么 `effort="7"`**：
- joint4/5/6 用的是 DM4310 小电机
- 额定扭矩 7 N·m（比 DM4340P 的 27 N·m 小很多）
- 因为腕部负载轻，不需要大扭矩

---

## 第九部分：end_link（末端法兰）

```xml
<link name="end_link">
  <inertial>
    <origin xyz="0.00018697 5.9452E-05 0.0074605" rpy="0 0 0" />
    <mass value="0.14970000" />
    <inertia
      ixx="0.00045353"
      ixy="0.00000000"
      ixz="0.00000000"
      iyy="0.00045353"
      iyz="0.00000000"
      izz="0.00045353" />
  </inertial>
  ...
</link>

<joint name="end_joint" type="fixed">
  <origin xyz="-0.00018697 -5.9452E-05 0.14921" rpy="0 -1.5708 3.1415" />
  <parent link="link6" />
  <child link="end_link" />
  <axis xyz="0 0 0" />
</joint>
```

**重点解读**：

| 参数 | 值 | 含义 |
|------|---|------|
| `type="fixed"` | 固定关节 | **不可动**（0 自由度） |
| `xyz="... ... 0.14921"` | Z: 149.21mm | 末端法兰距离 link6 的高度 |
| `rpy="0 -1.5708 3.1415"` | Pitch -90°, Yaw 180° | 坐标系旋转，让 end_link 的 Z 轴朝前 |
| `<axis xyz="0 0 0">` | 无轴 | fixed 关节不需要转轴 |

**为什么需要 end_link**：
- 这是**末端执行器的安装法兰**
- 夹爪/工具会固定在 end_link 上
- IK 计算的目标位姿就是 end_link 的位姿

**为什么 `rpy="0 -1.5708 3.1415"`**：
- 让 end_link 的 Z 轴指向前方（工具朝向）
- 让 X 轴指向下方（方便定义夹爪开合方向）
- 这是 ROS 的约定（末端 Z 轴 = approach 方向）

---

## 总结：URDF 的关键设计

### 1. 坐标系约定

- **base_link 原点**：底座底面中心
- **Z 轴向上**：符合右手坐标系
- **关节轴心**：通过 `<origin xyz="...">` 定义相对位置

### 2. 质量分布

| 连杆 | 质量 (kg) | 占比 | 备注 |
|------|----------|------|------|
| base_link | 0.837 | 22% | 底座 + joint1 电机 |
| link1 | 0.161 | 4% | 短连杆 |
| link2 | 1.327 | 35% | **最重**（大臂 + joint2/3 电机） |
| link3 | 0.835 | 22% | 小臂 + joint4 电机 |
| link4/5/6 | 0.150 各 | 4% 各 | 腕部轻量化 |
| end_link | 0.150 | 4% | 末端法兰 |
| **总计** | **3.76 kg** | 100% | 不含夹爪 |

### 3. 关节限位

| 关节 | 下限 | 上限 | 备注 |
|------|------|------|------|
| joint1 | -180° | +180° | 腰转，全范围 |
| joint2 | -180° | **0°** | 肩抬，不能超过水平 |
| joint3 | -180° | **0°** | 肘弯，不能反向 |
| joint4/5/6 | -180° | +180° | 腕部，全范围 |

### 4. 电机配置

| 位置 | 关节 | 电机型号 | 额定扭矩 | 数量 |
|------|------|---------|---------|------|
| 底座/肩/肘 | joint1/2/3 | DM4340P | 27 N·m | 3 |
| 腕部 | joint4/5/6 | DM4310 | 7 N·m | 3 |

### 5. 工作空间估算

- **大臂长度**：240.5mm（link2 的 X 偏移）
- **小臂长度**：240.5mm（link3 的 X 偏移）
- **腕部长度**：149.21mm（end_joint 的 Z 偏移）
- **理论最大伸展**：≈ 630mm
- **推荐工作半径**：< 450mm（70% reach）

---

## 常见修改场景

### 场景 1：更换更重的夹爪

**问题**：夹爪从 0.2kg 换成 0.5kg

**修改**：
1. 在 `<link name="end_link">` 下找到 `<mass value="0.14970000" />`
2. 改成 `<mass value="0.64970000" />`（0.150 + 0.500 - 0.200）
3. 如果有夹爪的 CAD 模型，同步更新 `<inertia>` 参数

### 场景 2：限制 joint2 的转动范围

**问题**：实测 joint2 只能转 -120° ~ 0°，但 URDF 里写的是 -180° ~ 0°

**修改**：
```xml
<joint name="joint2" type="revolute">
  ...
  <limit
    lower="-2.094"  <!-- 改成 -120° = -2.094 rad -->
    upper="0"
    effort="27"
    velocity="50" />
</joint>
```

### 场景 3：添加夹爪的 STL 模型

**步骤**：
1. 导出夹爪 STL：`gripper.STL`
2. 放到 `meshes/` 目录
3. 在 `<link name="end_link">` 的 `<visual>` 里改 `<mesh filename="...gripper.STL" />`

---

## 调试技巧

### 1. 检查 URDF 语法

```bash
check_urdf reBot-DevArm_fixend.urdf
```

输出应该是：
```
robot name is: reBot-DevArm_fixend
---------- Successfully Parsed XML ---------------
root Link: base_link has 1 child(ren)
    child(1):  link1
        child(1):  link2
            child(1):  link3
                ...
```

### 2. 可视化 URDF

```bash
urdf_viz reBot-DevArm_fixend.urdf
```

或者用 MeshCat：
```bash
python3 example/sim/fk_sim.py
```

### 3. 验证质量参数

```python
import pinocchio as pin
model = pin.buildModelFromUrdf("reBot-DevArm_fixend.urdf")
print(f"总质量: {sum([model.inertias[i].mass for i in range(1, model.njoints)])} kg")
```

---

## 参考资料

- [ROS URDF 官方教程](http://wiki.ros.org/urdf/Tutorials)
- [SolidWorks URDF Exporter](http://wiki.ros.org/sw_urdf_exporter)
- [Pinocchio 文档](https://gepettoweb.laas.fr/doc/stack-of-tasks/pinocchio/master/doxygen-html/)
- reBot-DevArm 硬件规格：`hardware/reBot_B601_DM/Hardware_Summary_zh.md`
