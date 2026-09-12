仿真器状态
==========

**位置：** ``protomotions/simulator/base_simulator/simulator_state.py``

仿真器状态类为所有物理后端提供了统一的仿真状态表示。

RobotState
----------

``RobotState`` 包含机器人的完整状态：

.. code-block:: python

   @dataclass
   class RobotState:
       # Maximal coordinates (world-space)
       rigid_body_pos: Tensor[num_envs, num_bodies, 3]
       # quaternion xyzw ordering for the common state shared by all simulators
       # see conversion to different sim backends discussed later.
       rigid_body_rot: Tensor[num_envs, num_bodies, 4]
       rigid_body_vel: Tensor[num_envs, num_bodies, 3]
       rigid_body_ang_vel: Tensor[num_envs, num_bodies, 3]
       
       # Reduced coordinates (joint-space)
       dof_pos: Tensor[num_envs, num_dofs]
       dof_vel: Tensor[num_envs, num_dofs]
       
       # Forces
       dof_forces: Tensor[num_envs, num_dofs]  # Applied torques
       
       # Contacts
       rigid_body_contacts: Tensor[num_envs, num_bodies]  # Binary contact

**为什么同时需要最大化坐标和简化坐标？**

* **最大化坐标** （rigid_body_*）：用于奖励计算，以及需要世界坐标的观测
  （例如到目标的距离、身体高度）
* **简化坐标** （dof_*）：用于动作空间和部分观测类型
  （真实机器人可能只能提供简化坐标的观测）

访问状态字段
~~~~~~~~~~~~

常见模式：

.. code-block:: python

   # Root position (body 0)
   root_pos = robot_state.rigid_body_pos[:, 0, :]  # [num_envs, 3]
   
   # Root height
   root_height = robot_state.rigid_body_pos[:, 0, 2]  # [num_envs]
   
   # Foot positions
   left_foot_pos = robot_state.rigid_body_pos[:, left_foot_idx, :]
   
   # All body velocities
   body_vels = robot_state.rigid_body_vel  # [num_envs, num_bodies, 3]

ObjectState
-----------

``ObjectState`` 包含场景物体的状态：

.. code-block:: python

   @dataclass
   class ObjectState:
       object_pos: Tensor[num_envs, num_objects, 3]
       object_rot: Tensor[num_envs, num_objects, 4]
       object_vel: Tensor[num_envs, num_objects, 3]
       object_ang_vel: Tensor[num_envs, num_objects, 3]

在带可交互物体的训练中（跨越障碍、物体操作）使用。

StateConversion
---------------

用于在通用（基础仿真器）状态表示与各仿真器专属状态表示之间转换的工具类，
因为不同仿真器可能采用不同的四元数约定和/或刚体/自由度顺序。

常见操作
--------

**克隆状态：**

.. code-block:: python

   state_copy = robot_state.clone()

**转换为字典（用于保存）：**

.. code-block:: python

   state_dict = robot_state.to_dict()
   torch.save(state_dict, "state.motion")
   
   # Loading
   loaded_dict = torch.load("state.motion")
   robot_state = RobotState.from_dict(loaded_dict)


动作库状态
----------

MotionLib 使用相同的结构存储参考状态：

.. code-block:: python

   # Query reference state at specific time
   ref_state: RobotState = motion_lib.get_motion_state(motion_ids, motion_times)
   
   # Compare to current state for rewards
   pos_error = current_state.rigid_body_pos - ref_state.rigid_body_pos

这使得仿真状态与参考动作之间可以直接比较。

下一步
------

* :doc:`abstractions` - 完整系统概览
