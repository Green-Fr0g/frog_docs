环境上下文
==========

环境上下文为观测、奖励和终止所需的全部仿真状态与任务变量提供带类型的访问。
ProtoMotions 采用基于描述符（descriptor）的模式实现类型安全的上下文路径，
并支持 IDE 自动补全。

概述
----

每个时间步，环境都会构建一个 ``EnvContext`` 实例，其中包含：

1. **当前状态** - 机器人状态的真实值视图与带噪视图
2. **历史状态** - 来自历史缓冲区的过往状态
3. **任务上下文** - 来自控制组件的任务专属变量
4. **环境参数** - dt、接触跟踪等

组件通过 ``MdpComponent`` 将自己的核函数绑定到上下文路径：

.. code-block:: text

   ┌─────────────────────────────────────────────────────────────┐
   │                      EnvContext                             │
   ├─────────────────────────────────────────────────────────────┤
   │  Current State Views   │  Historical State Views            │
   │  ───────────────────   │  ──────────────────────            │
   │  current: CurrentState │  historical: HistoricalView        │
   │  noisy: CurrentState   │  noisy_historical: NoisyHistView   │
   ├─────────────────────────────────────────────────────────────┤
   │  Control Context       │  Environment Parameters            │
   │  ───────────────────   │  ──────────────────────            │
   │  mimic: MimicContext      │  dt: float                         │
   │  steering: SteeringContext│  ground_heights: Tensor            │
   │  path: PathContext        │  contact_body_ids: Tensor          │
   └─────────────────────────────────────────────────────────────┘
                                     │
            ┌────────────────────────┼────────────────────────┐
            ▼                        ▼                        ▼
   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
   │  Observations   │    │     Rewards     │    │  Terminations   │
   │  (MdpComponent) │    │  (MdpComponent) │    │  (MdpComponent) │
   └─────────────────┘    └─────────────────┘    └─────────────────┘

MdpComponent 模式
-----------------

组件使用 ``MdpComponent`` 将纯张量核函数绑定到上下文路径：

.. code-block:: python

   from protomotions.envs.context_views import EnvContext
   from protomotions.envs.mdp_component import MdpComponent
   from protomotions.envs.rewards import compute_gt_rew
   
   reward_components = {
       "gt_rew": MdpComponent(
           compute_func=compute_gt_rew,                      # Pure tensor function
           dynamic_vars={                                  # Map params to context paths
               "current_rigid_body_pos": EnvContext.current.rigid_body_pos,
               "ref_rigid_body_pos": EnvContext.mimic.ref_state.rigid_body_pos,
           },
           static_params={"weight": 0.5, "coefficient": -100.0},  # Static parameters
       ),
   }

**主要优势：**

- **类型安全**：上下文路径支持 IDE 自动补全（``EnvContext.current.rigid_body_pos``）
- **显式声明**：绑定关系清楚地表明每个核函数需要哪些数据
- **易于测试**：核函数是纯函数，可以独立测试
- **可导出**：ONNX 导出通过 ``get_bindings_dict()`` 建立输入映射

上下文视图
----------

EnvContext 提供对仿真状态的带类型视图：

CurrentStateView
~~~~~~~~~~~~~~~~

当前机器人状态（critic/奖励使用真值，actor 使用带噪版本）：

.. code-block:: python

   # Access via EnvContext.current or EnvContext.noisy
   
   # Rigid body state
   .rigid_body_pos        # [num_envs, num_bodies, 3]
   .rigid_body_rot        # [num_envs, num_bodies, 4] quaternion (w-last)
   .rigid_body_vel        # [num_envs, num_bodies, 3]
   .rigid_body_ang_vel    # [num_envs, num_bodies, 3]
   .rigid_body_contacts   # [num_envs, num_bodies] boolean
   
   # DOF state
   .dof_pos               # [num_envs, num_dofs]
   .dof_vel               # [num_envs, num_dofs]
   .dof_forces            # [num_envs, num_dofs]
   
   # Root properties (precomputed)
   .root_pos              # [num_envs, 3]
   .root_rot              # [num_envs, 4]
   .root_vel              # [num_envs, 3]
   .root_ang_vel          # [num_envs, 3]
   .root_height           # [num_envs]
   .root_local_ang_vel    # [num_envs, 3] in local frame
   
   # Anchor properties (typically pelvis, precomputed)
   .anchor_pos            # [num_envs, 3]
   .anchor_rot            # [num_envs, 4]
   .anchor_vel            # [num_envs, 3]
   .anchor_ang_vel        # [num_envs, 3]
   .anchor_local_ang_vel  # [num_envs, 3]

HistoricalView
~~~~~~~~~~~~~~

用于时序观测的过往状态：

.. code-block:: python

   # Access via EnvContext.historical or EnvContext.noisy_historical
   
   .rigid_body_pos        # [num_envs, history_steps, num_bodies, 3]
   .rigid_body_rot        # [num_envs, history_steps, num_bodies, 4]
   .dof_pos               # [num_envs, history_steps, num_dofs]
   .dof_vel               # [num_envs, history_steps, num_dofs]
   .actions               # [num_envs, history_steps, action_dim]
   .processed_actions     # [num_envs, history_steps, action_dim]
   .ground_heights        # [num_envs, history_steps]
   .body_contacts         # [num_envs, history_steps, num_contact_bodies]

控制组件视图
------------

控制组件向上下文填充任务专属的视图。

MimicContext
~~~~~~~~~~~~

模仿学习的动作跟踪上下文：

.. code-block:: python

   # Access via EnvContext.mimic
   
   # Reference state (at current time)
   .ref_state             # RobotState with rigid_body_pos, dof_pos, etc.
   .ref_root_height       # [num_envs] precomputed
   .ref_anchor_pos        # [num_envs, 3] precomputed
   .ref_anchor_rot        # [num_envs, 4] precomputed
   
   # Future target poses (multi-step)
   .future_pos            # [num_envs, future_steps, num_bodies, 3]
   .future_rot            # [num_envs, future_steps, num_bodies, 4]
   .future_vel            # [num_envs, future_steps, num_bodies, 3]
   .future_ang_vel        # [num_envs, future_steps, num_bodies, 3]
   .future_dof_pos        # [num_envs, future_steps, num_dofs]
   .future_dof_vel        # [num_envs, future_steps, num_dofs]
   
   # Convenience properties (precomputed)
   .future_root_pos       # [num_envs, future_steps, 3]
   .future_anchor_pos     # [num_envs, future_steps, 3]

SteeringContext
~~~~~~~~~~~~~~~

运动控制指令上下文：

.. code-block:: python

   # Access via EnvContext.steering
   
   .tar_dir               # [num_envs, 2] target heading direction
   .tar_dir_theta         # [num_envs] target direction as angle
   .tar_speed             # [num_envs] target speed
   .tar_face_dir          # [num_envs, 2] target facing direction
   .prev_root_pos         # [num_envs, 3] root position from previous step

PathContext
~~~~~~~~~~~

路径跟随上下文：

.. code-block:: python

   # Access via EnvContext.path
   
   .tar_pos               # [num_envs, 3] current target position
   .head_pos              # [num_envs, 3] head body position
   .traj_samples          # [num_envs, num_samples, 3] future waypoints
   .height_conditioned    # bool - whether height tracking is enabled
   .head_body_id          # int - index of head body

环境参数
~~~~~~~~

EnvContext 上的直接字段：

.. code-block:: python

   .dt                                # float - simulation timestep
   .ground_heights                    # [num_envs] terrain height
   .noisy_ground_heights              # [num_envs] noisy terrain height
   .body_contacts                     # [num_envs, num_contact_bodies]
   .contact_body_ids                  # [num_contact_bodies] tracked body indices
   .current_processed_action          # [num_envs, action_dim]
   .previous_action                   # [num_envs, action_dim]
   .previous_processed_action         # [num_envs, action_dim]
   .current_contact_force_magnitudes  # [num_envs, num_bodies]
   .prev_contact_force_magnitudes     # [num_envs, num_bodies]

在 MdpComponent 中使用上下文
-----------------------------

**类访问** （用于配置）：

.. code-block:: python

   # Returns FieldPath objects with .path property
   EnvContext.current.rigid_body_pos           # FieldPath("current.rigid_body_pos")
   EnvContext.mimic.future_pos                 # FieldPath("mimic.future_pos")
   EnvContext.ground_heights                   # FieldPath("ground_heights")

**实例访问** （运行时）：

.. code-block:: python

   # Returns actual tensor values
   ctx = env.context                           # EnvContext instance
   ctx.current.rigid_body_pos                  # Tensor [num_envs, num_bodies, 3]
   ctx.mimic.future_pos                        # Tensor [num_envs, future_steps, ...]

**在实验配置中**：

.. code-block:: python

   from protomotions.envs.context_views import EnvContext
   from protomotions.envs.mdp_component import MdpComponent
   from protomotions.envs.obs import compute_humanoid_max_coords_observations
   
   observation_components = {
       "max_coords_obs": MdpComponent(
           compute_func=compute_humanoid_max_coords_observations,
           dynamic_vars={
               "body_pos": EnvContext.current.rigid_body_pos,     # Type-safe!
               "body_rot": EnvContext.current.rigid_body_rot,
               "body_vel": EnvContext.current.rigid_body_vel,
               "body_ang_vel": EnvContext.current.rigid_body_ang_vel,
               "ground_height": EnvContext.ground_heights,
               "body_contacts": EnvContext.body_contacts,
           },
           static_params={"local_obs": True, "root_height_obs": True, "w_last": True},
       ),
   }

添加自定义上下文视图
--------------------

要向上下文添加自定义变量，可以编写一个控制组件，
用自定义视图填充 EnvContext：

.. code-block:: python

   from protomotions.envs.context_paths import FieldPath, NestedField
   
   class MyCustomView:
       """Custom view for my task."""
       
       # Define fields as FieldPath descriptors
       target_pos: Tensor = FieldPath()
       target_vel: Tensor = FieldPath()
       
       def __init__(self, target_pos, target_vel):
           self.target_pos = target_pos
           self.target_vel = target_vel
   
   class MyControlComponent(ControlComponent):
       def populate_context(self, ctx: EnvContext) -> None:
           # Add your custom view to the context
           ctx.my_custom = MyCustomView(
               target_pos=self._compute_target_pos(),
               target_vel=self._compute_target_vel(),
           )

然后在 MdpComponent 绑定中使用它：

.. code-block:: python

   observation_components = {
       "custom_obs": MdpComponent(
           compute_func=compute_custom_obs,
           dynamic_vars={
               "target_pos": EnvContext.my_custom.target_pos,  # Type-safe!
           },
       ),
   }

下一步
------

* :doc:`abstractions` - 组件系统详解
* :doc:`simulator_state` - SimulatorState 状态表示
