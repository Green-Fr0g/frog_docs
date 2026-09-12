PoseLib 工具集
==============

**位置：** ``protomotions/components/pose_lib.py``

PoseLib 是一组实用工具，用于衔接 MJCF 机器人定义与仿真状态。
代码库中在 FK/IK、动作处理和坐标转换时都会用到它。

PoseLib 做什么
--------------

1. **解析 MJCF → KinematicInfo**：从 MJCF 文件中提取机器人结构
2. **坐标转换**：在简化坐标（qpos）与最大化坐标之间变换
3. **正向/逆向运动学**：由关节角计算刚体位姿，或反向求解
4. **速度计算**：从位姿序列通过有限差分计算速度

MJCF 解析
---------

``extract_kinematic_info()`` 解析 MJCF 文件，返回包含机器人运动学结构的
``KinematicInfo`` dataclass：

.. code-block:: python

   from protomotions.components.pose_lib import extract_kinematic_info
   
   kinematic_info = extract_kinematic_info(
       "protomotions/data/assets/mjcf/g1_bm_no_mesh_box_feet.xml"
   )

**KinematicInfo 字段：**

.. code-block:: python

   @dataclass
   class KinematicInfo:
       body_names: List[str]          # All body names in order
       dof_names: List[str]           # Joint names (excluding root)
       parent_indices: List[int]      # Parent body index for each body
       local_pos: Tensor              # Local position offsets
       local_rot_ref_mat: Tensor      # Reference local rotations
       hinge_axes_map: Dict           # Hinge joint axes
       nq: int                        # Dimension of qpos
       nv: int                        # Dimension of qvel
       num_bodies: int
       num_dofs: int
       dof_limits_lower: Tensor
       dof_limits_upper: Tensor

创建机器人配置时会自动填充这些信息。

坐标系
------

动作数据与仿真使用不同的坐标表示：

**简化坐标（qpos）：**

MuJoCo 风格的广义坐标：

.. code-block:: text

   qpos = [root_pos(3), root_quat_wxyz(4), joint_angles(...)]

表示紧凑——每个自由度一个值。

**最大化坐标：**

每个刚体在世界坐标系下的位置与旋转：

.. code-block:: python

   rigid_body_pos: Tensor[num_envs, num_bodies, 3]
   rigid_body_rot: Tensor[num_envs, num_bodies, 4]

更便于奖励计算（在笛卡尔空间中度量距离）。

坐标转换
--------

**简化坐标 → 最大化坐标（正向运动学）：**

.. code-block:: python

   from protomotions.components.pose_lib import (
       extract_transforms_from_qpos,
       compute_forward_kinematics_from_transforms
   )
   
   # qpos → local transforms
   root_pos, local_rot_mats = extract_transforms_from_qpos(
       kinematic_info, qpos
   )
   
   # local transforms → world poses
   world_pos, world_rot_mat = compute_forward_kinematics_from_transforms(
       kinematic_info, root_pos, local_rot_mats
   )

**最大化坐标 → 简化坐标（逆向）：**

.. code-block:: python

   from protomotions.components.pose_lib import extract_qpos_from_transforms
   
   qpos = extract_qpos_from_transforms(
       kinematic_info, root_pos, local_rot_mats,
       multi_dof_decomposition_method="exp_map"
   )

速度计算
--------

从位姿序列通过有限差分计算速度：

.. code-block:: python

   from protomotions.components.pose_lib import (
       compute_cartesian_velocity,
       compute_angular_velocity
   )
   
   # Linear velocity from position sequence
   linear_vel = compute_cartesian_velocity(positions, fps=30)
   
   # Angular velocity from rotation sequence
   angular_vel = compute_angular_velocity(rotation_mats, fps=30)

高层函数
--------

动作处理可以使用高层封装函数：

.. code-block:: python

   from protomotions.components.pose_lib import fk_from_transforms_with_velocities
   
   # Compute full state (positions, rotations, velocities)
   state = fk_from_transforms_with_velocities(
       kinematic_info=kinematic_info,
       root_pos=root_positions,
       joint_rot_mats=local_rotations,
       fps=30,
       compute_velocities=True
   )
   # Returns RobotState with all fields populated

ControlInfo
-----------

PoseLib 还定义了用于 PD 控制参数的 ``ControlInfo``：

.. code-block:: python

   @dataclass
   class ControlInfo:
       stiffness: float      # P gain
       damping: float        # D gain
       armature: float       # Motor inertia
       friction: float       # Joint friction
       effort_limit: float   # Max torque
       velocity_limit: float # Max velocity

在机器人配置中用于指定各关节的控制属性。

测试
----

将 FK/IK 与 MuJoCo 进行对照验证：

.. code-block:: python

   from protomotions.components.pose_lib import test_fk_against_mujoco
   
   test_fk_against_mujoco("path/to/robot.xml")

该函数将 PoseLib 的 FK 输出与 MuJoCo 内部的 FK 结果进行对比。

下一步
------

* :doc:`simulator_state` - 仿真中状态如何表示
* :doc:`abstractions` - PoseLib 在架构中的位置
