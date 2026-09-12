# 坐标系与旋转约定

本页记录 SONIC 代码库中使用的坐标系、四元数与旋转约定。这些约定搞错了会导致隐蔽的 bug —— 机器人会动，但方向或姿态是错的。

## 坐标系

### Isaac Lab / MuJoCo（仿真）

- **Z-up（Z 轴朝上）**：重力沿 -Z 方向。地面为 XY 平面。
- **右手系**：X 朝前，Y 朝左，Z 朝上。
- 这是训练和评估阶段使用的约定。

### SMPL / BVH（人体运动数据）

- **Y-up（Y 轴朝上）**：重力沿 -Y 方向。地面为 XZ 平面。
- 加载 SMPL 或 BVH 数据时，需在动作库配置中设置 `smpl_y_up: true`。动作库会在内部自动将 Y-up 转换为 Z-up。

### 汇总

| 系统 | 朝上轴 | 约定 |
|--------|---------|------------|
| Isaac Lab | Z | Z-up（Z 轴朝上），右手系 |
| MuJoCo | Z | Z-up（Z 轴朝上），右手系 |
| SMPL 人体模型 | Y | Y-up（Y 轴朝上） |
| BVH 动作文件 | Y | Y-up（Y 轴朝上） |
| 重定向后的 PKL 数据 | Z | Z-up（Z 轴朝上，已完成转换） |

## 四元数约定

### 标量在前（wxyz）—— SONIC 全程默认

SONIC 代码库中处处使用**标量在前（wxyz）**四元数：

```
q = [w, x, y, z]
```

适用于：

- `gear_sonic/trl/utils/torch_transform.py` — 全部旋转工具函数
- `gear_sonic/isaac_utils/rotations.py` — Isaac Lab 旋转辅助函数（使用 `w_last=False`）
- Isaac Lab API（`body_quat_w`、`root_quat_w` 等）
- 动作库内部存储
- 重定向后的 PKL 数据（`root_rot` 字段）

### 标量在后（xyzw）—— 仅限 SciPy

[SciPy 的 Rotation 类](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html)
使用**标量在后（xyzw）**约定：

```
q = [x, y, z, w]
```

该约定仅在**数据处理脚本**（`data_process/`）调用 `scipy.spatial.transform.Rotation` 时使用。这些脚本在保存前会先转换为 wxyz：

```python
# In data processing (scipy xyzw → wxyz for storage)
root_quat_xyzw = Rotation.from_euler("xyz", euler_angles).as_quat()  # scipy: xyzw
root_quat_wxyz = root_quat_xyzw[:, [3, 0, 1, 2]]                    # convert to wxyz
```

### `w_last` 参数

`gear_sonic/isaac_utils/rotations.py` 中的函数接受一个 `w_last` 布尔参数：

```python
quat_rotate(q, v, w_last=False)   # q is wxyz (scalar-first) — this is the default
quat_rotate(q, v, w_last=True)    # q is xyzw (scalar-last)
```

**除非**你在对接 scipy 或某个明确使用 xyzw 的系统，**否则请始终使用 `w_last=False`**。

### 速查表

| 系统 | 约定 | 顺序 | 单位四元数 |
|--------|-----------|-------|----------|
| SONIC (torch_transform.py) | wxyz | `[w, x, y, z]` | `[1, 0, 0, 0]` |
| Isaac Lab | wxyz | `[w, x, y, z]` | `[1, 0, 0, 0]` |
| SciPy | xyzw | `[x, y, z, w]` | `[0, 0, 0, 1]` |
| MuJoCo | wxyz | `[w, x, y, z]` | `[1, 0, 0, 0]` |
| ROS | xyzw | `[x, y, z, w]` | `[0, 0, 0, 1]` |

### 两种约定之间的转换

```python
# wxyz → xyzw
q_xyzw = q_wxyz[..., [1, 2, 3, 0]]

# xyzw → wxyz
q_wxyz = q_xyzw[..., [3, 0, 1, 2]]
```

## 旋转表示

代码库根据上下文使用多种旋转表示：

| 表示形式 | 形状 | 使用场景 |
|---------------|-------|---------|
| 四元数（wxyz） | `(..., 4)` | 仿真、动作库、观测 |
| 轴角 | `(..., 3)` | 动作 PKL 中的 `pose_aa` 字段 |
| 旋转矩阵 | `(..., 3, 3)` | 正运动学、6D 旋转编码 |
| 6D 旋转 | `(..., 6)` | 部分观测项（旋转矩阵的前 2 列） |
| 欧拉角 | `(..., 3)` | CSV 动作数据输入（立即转换） |

### 动作数据中的轴角

重定向后 PKL 文件中的 `pose_aa` 字段以轴角向量存储每个刚体的**局部**旋转。向量方向为旋转轴，模长为以弧度表示的角度：

```python
pose_aa  # (T, num_bodies, 3) — axis-angle per body, MuJoCo body order
```

## 关节顺序

Isaac Lab 与 MuJoCo 遍历运动学树的顺序不同。代码库为每个机器人提供了双向索引映射：

```python
from gear_sonic.envs.manager_env.robots.g1 import (
    G1_ISAACLAB_TO_MUJOCO_DOF,   # Reorder DOFs: IsaacLab → MuJoCo
    G1_MUJOCO_TO_ISAACLAB_DOF,   # Reorder DOFs: MuJoCo → IsaacLab
)

# Convert joint positions from IsaacLab order to MuJoCo order:
mujoco_joints = isaaclab_joints[..., G1_ISAACLAB_TO_MUJOCO_DOF]
```

动作 PKL 数据（`dof`、`pose_aa`）按 **MuJoCo 顺序**存储。Isaac Lab 仿真使用 **IsaacLab 顺序**。训练流水线通过 `order_converter.py` 自动完成转换。

参见[在新机器人本体上训练](../user_guide/new_embodiments.md)，了解如何为新机器人定义这些映射。
