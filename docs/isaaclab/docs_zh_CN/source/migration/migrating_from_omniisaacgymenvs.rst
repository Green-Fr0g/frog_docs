.. _migrating-from-omniisaacgymenvs:

从 OmniIsaacGymEnvs 迁移
========================

.. currentmodule:: isaaclab


`OmniIsaacGymEnvs`_ 是一个基于 Isaac Sim 平台的强化学习框架。
OmniIsaacGymEnvs 的功能已被集成到 Isaac Lab 框架中。
我们已将 OmniIsaacGymEnvs 更新到 Isaac Sim 4.0.0 版本，以支持迁移到
Isaac Lab 的过程。接下来，OmniIsaacGymEnvs 将被弃用，后续开发
将在 Isaac Lab 中继续进行。

.. note::

  以下变更基于 Isaac Lab 1.0 版本。未来版本中的任何变更，
  请参阅 `release notes`_ 。

任务配置设置
~~~~~~~~~~~~~~~~~

在 OmniIsaacGymEnvs 中，任务配置文件以 ``.yaml`` 格式定义。而在 Isaac Lab 中，配置现在使用
专门的 Python 类 :class:`~isaaclab.utils.configclass` 来指定。
:class:`~isaaclab.utils.configclass` 模块在 Python 的 ``dataclasses`` 模块之上提供了一个封装。
每个环境都应指定自己的配置类，用 ``@configclass`` 注解并继承自
:class:`~envs.DirectRLEnvCfg` 类，其中可以包含仿真参数、环境场景参数、
机器人参数和任务特定参数。

下面是任务配置类的一个示例骨架：

.. code-block:: python

   from isaaclab.envs import DirectRLEnvCfg
   from isaaclab.scene import InteractiveSceneCfg
   from isaaclab.sim import SimulationCfg

   @configclass
   class MyEnvCfg(DirectRLEnvCfg):
      # simulation
      sim: SimulationCfg = SimulationCfg()
      # robot
      robot_cfg: ArticulationCfg = ArticulationCfg()
      # scene
      scene: InteractiveSceneCfg = InteractiveSceneCfg()
      # env
      decimation = 2
      episode_length_s = 5.0
      action_space = 1
      observation_space = 4
      state_space = 0
      # task-specific parameters
      ...

仿真配置
-----------------

仿真相关参数作为 :class:`~isaaclab.sim.SimulationCfg` 类的一部分定义，
它是一个 :class:`~isaaclab.utils.configclass` 模块，保存 ``dt`` 、
``device`` 和 ``gravity`` 等仿真参数。每个任务配置必须定义一个名为 ``sim`` 的变量，其类型为
:class:`~isaaclab.sim.SimulationCfg` 。

关节体和刚体的仿真参数，例如 ``num_position_iterations`` 、 ``num_velocity_iterations`` 、
``contact_offset`` 、 ``rest_offset`` 、 ``bounce_threshold_velocity`` 、 ``max_depenetration_velocity`` ，都可以
在每个单独的关节体和刚体的配置类中按 actor 单独指定。

在 GPU 上运行仿真时，PhysX 中的缓冲区需要预先分配，用于计算和存储
接触、碰撞和聚合对等信息。这些缓冲区可能需要根据
环境的复杂程度、预期的接触和碰撞数量以及
环境中的 actor 数量进行调整。 :class:`~isaaclab.sim.PhysxCfg` 类提供了
设置 GPU 缓冲区维度的途径。

+--------------------------------------------------+---------------------------------------------------------------+
||                                                 ||                                                              |
||                                                 ||                                                              |
|| # OmniIsaacGymEnvs                              || # IsaacLab                                                   |
|| sim:                                            || sim: SimulationCfg = SimulationCfg(                          |
||                                                 || device = "cuda:0" # can be "cpu", "cuda", "cuda:<device_id>" |
|| dt: 0.0083 # 1/120 s                            || dt=1 / 120,                                                  |
|| use_gpu_pipeline: ${eq:${...pipeline},"gpu"}    || # use_gpu_pipeline is deduced from the device                |
|| use_fabric: True                                || use_fabric=True,                                             |
|| enable_scene_query_support: False               || enable_scene_query_support=False,                            |
|| disable_contact_processing: False               ||                                                              |
|| gravity: [0.0, 0.0, -9.81]                      || gravity=(0.0, 0.0, -9.81),                                   |
||                                                 ||                                                              |
|| default_physics_material:                       || physics_material=RigidBodyMaterialCfg(                       |
|| static_friction: 1.0                            || static_friction=1.0,                                         |
|| dynamic_friction: 1.0                           || dynamic_friction=1.0,                                        |
|| restitution: 0.0                                || restitution=0.0                                              |
||                                                 || )                                                            |
|| physx:                                          || physx: PhysxCfg = PhysxCfg(                                  |
|| worker_thread_count: ${....num_threads}         || # worker_thread_count is no longer needed                    |
|| solver_type: ${....solver_type}                 || solver_type=1,                                               |
|| use_gpu: ${contains:"cuda",${....sim_device}}   || # use_gpu is deduced from the device                         |
|| solver_position_iteration_count: 4              || max_position_iteration_count=4,                              |
|| solver_velocity_iteration_count: 0              || max_velocity_iteration_count=0,                              |
|| contact_offset: 0.02                            || # moved to actor config                                      |
|| rest_offset: 0.001                              || # moved to actor config                                      |
|| bounce_threshold_velocity: 0.2                  || bounce_threshold_velocity=0.2,                               |
|| friction_offset_threshold: 0.04                 || friction_offset_threshold=0.04,                              |
|| friction_correlation_distance: 0.025            || friction_correlation_distance=0.025,                         |
|| enable_sleeping: True                           || # enable_sleeping is no longer needed                        |
|| enable_stabilization: True                      || enable_stabilization=True,                                   |
|| max_depenetration_velocity: 100.0               || # moved to RigidBodyPropertiesCfg                            |
||                                                 ||                                                              |
|| gpu_max_rigid_contact_count: 524288             || gpu_max_rigid_contact_count=2**23,                           |
|| gpu_max_rigid_patch_count: 81920                || gpu_max_rigid_patch_count=5 * 2**15,                         |
|| gpu_found_lost_pairs_capacity: 1024             || gpu_found_lost_pairs_capacity=2**21,                         |
|| gpu_found_lost_aggregate_pairs_capacity: 262144 || gpu_found_lost_aggregate_pairs_capacity=2**25,               |
|| gpu_total_aggregate_pairs_capacity: 1024        || gpu_total_aggregate_pairs_capacity=2**21,                    |
|| gpu_heap_capacity: 67108864                     || gpu_heap_capacity=2**26,                                     |
|| gpu_temp_buffer_capacity: 16777216              || gpu_temp_buffer_capacity=2**24,                              |
|| gpu_max_num_partitions: 8                       || gpu_max_num_partitions=8,                                    |
|| gpu_max_soft_body_contacts: 1048576             || gpu_max_soft_body_contacts=2**20,                            |
|| gpu_max_particle_contacts: 1048576              || gpu_max_particle_contacts=2**20,                             |
||                                                 || )                                                            |
||                                                 || )                                                            |
+--------------------------------------------------+---------------------------------------------------------------+

诸如 ``add_ground_plane`` 和 ``add_distant_light`` 之类的参数现在属于创建场景时的任务逻辑。
``enable_cameras`` 现在是一个命令行参数 ``--enable_cameras`` ，可以直接传递给训练脚本。


场景配置
------------

:class:`~isaaclab.scene.InteractiveSceneCfg` 类可用于指定与场景相关的参数，
例如环境数量和环境之间的间距。每个任务配置必须定义一个名为
``scene`` 的变量，其类型为 :class:`~isaaclab.scene.InteractiveSceneCfg` 。

+--------------------------------------------------------------+-------------------------------------------------------------------+
|                                                              |                                                                   |
|.. code-block:: yaml                                          |.. code-block:: python                                             |
|                                                              |                                                                   |
|  # OmniIsaacGymEnvs                                          | # IsaacLab                                                        |
|  env:                                                        | scene: InteractiveSceneCfg = InteractiveSceneCfg(                 |
|    numEnvs: ${resolve_default:512,${...num_envs}}            |    num_envs=512,                                                  |
|    envSpacing: 4.0                                           |    env_spacing=4.0)                                               |
+--------------------------------------------------------------+-------------------------------------------------------------------+

任务配置
-----------

每个环境应指定自己的配置类，其中保存任务特定参数，例如观测和动作缓冲区的维度。奖励项缩放参数也可以在配置类中指定。

在 Isaac Lab 中， ``controlFrequencyInv`` 参数已被重命名为 ``decimation`` ，
必须在配置类中将其指定为参数。

此外，最大回合长度参数（现在为 ``episode_length_s``）以秒为单位，而不是像
OmniIsaacGymEnvs 中那样以步数为单位。要在步数和秒之间转换，请使用以下等式：
``episode_length_s = dt * decimation * num_steps`` 。

每个环境配置必须设置以下参数：

.. code-block:: python

   decimation = 2
   episode_length_s = 5.0
   action_space = 1
   observation_space = 4
   state_space = 0


RL 配置设置
~~~~~~~~~~~~~~~

rl_games 库的 RL 配置文件在 Isaac Lab 中仍可以 ``.yaml`` 文件的形式定义。
配置文件的大部分内容可以直接从 OmniIsaacGymEnvs 复制。
请注意，在 Isaac Lab 中，我们不使用 hydra 来解析配置文件中的相对路径。
请将诸如 ``${....device}`` 之类的相对路径替换为参数的实际值。

此外，观测和动作的截断范围已被移至 RL 配置文件。
在 IsaacGymEnvs 任务配置文件中定义的所有 ``clipObservations`` 和 ``clipActions`` 参数，
都应移至 Isaac Lab 的 RL 配置文件中。

+--------------------------+----------------------------+
|                          |                            |
| IsaacGymEnvs Task Config | Isaac Lab RL Config        |
+--------------------------+----------------------------+
|.. code-block:: yaml      |.. code-block:: yaml        |
|                          |                            |
|  # OmniIsaacGymEnvs      | # IsaacLab                 |
|  env:                    | params:                    |
|    clipObservations: 5.0 |   env:                     |
|    clipActions: 1.0      |     clip_observations: 5.0 |
|                          |     clip_actions: 1.0      |
+--------------------------+----------------------------+

环境创建
~~~~~~~~~~~~~~~~~~~~

在 OmniIsaacGymEnvs 中，环境创建通常在 ``set_up_scene()`` API 中进行，
它包括创建初始环境、克隆环境、过滤碰撞、
添加地平面和灯光，以及为 actor 创建 ``View`` 类。

类似的功能在 Isaac Lab 中由 ``_setup_scene()`` API 完成。
主要区别在于，基类的 ``_setup_scene()`` 不再执行
克隆环境、添加地平面和灯光的操作。这些操作
现在应在各个任务的 ``_setup_scene`` 实现中实现，以便为场景设置过程提供更多
灵活性。

另请注意，通过定义 ``Articulation`` 或 ``RigidObject`` 对象，actor 将
通过解析 actor 配置中的 ``spawn`` 参数被添加到场景中，并且会自动为该
actor 创建一个 ``View`` 类。这避免了为 actor 单独定义
``ArticulationView`` 或 ``RigidPrimView`` 对象的需要。


+------------------------------------------------------------------------------+------------------------------------------------------------------------+
| OmniIsaacGymEnvs                                                             | Isaac Lab                                                              |
+------------------------------------------------------------------------------+------------------------------------------------------------------------+
|.. code-block:: python                                                        |.. code-block:: python                                                  |
|                                                                              |                                                                        |
|   def set_up_scene(self, scene) -> None:                                     |   def _setup_scene(self):                                              |
|     self.get_cartpole()                                                      |     self.cartpole = Articulation(self.cfg.robot_cfg)                   |
|     super().set_up_scene(scene)                                              |     # add ground plane                                                 |
|                                                                              |     spawn_ground_plane(prim_path="/World/ground", cfg=GroundPlaneCfg() |
|     self._cartpoles = ArticulationView(                                      |     # clone, filter, and replicate                                     |
|                  prim_paths_expr="/World/envs/.*/Cartpole",                  |     self.scene.clone_environments(copy_from_source=False)              |
|                  name="cartpole_view", reset_xform_properties=False          |     self.scene.filter_collisions(global_prim_paths=[])                 |
|     )                                                                        |     # add articulation to scene                                        |
|     scene.add(self._cartpoles)                                               |     self.scene.articulations["cartpole"] = self.cartpole               |
|                                                                              |     # add lights                                                       |
|                                                                              |     light_cfg = sim_utils.DomeLightCfg(intensity=2000.0)               |
|                                                                              |     light_cfg.func("/World/Light", light_cfg)                          |
+------------------------------------------------------------------------------+------------------------------------------------------------------------+


地平面
------------

除上述示例外，还可以使用 :class:`~terrains.TerrainImporterCfg` 类定义更复杂的地平面。

.. code-block:: python

   from isaaclab.terrains import TerrainImporterCfg

   terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="plane",
        collision_group=-1,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
    )

然后，通过引用 ``TerrainImporterCfg`` 对象，可以在 ``_setup_scene(self)`` 中将地形添加到场景中：

.. code-block::python

   def _setup_scene(self):
      ...
      self.cfg.terrain.num_envs = self.scene.cfg.num_envs
      self.cfg.terrain.env_spacing = self.scene.cfg.env_spacing
      self._terrain = self.cfg.terrain.class_type(self.cfg.terrain)


Actor
------

在 Isaac Lab 中，每个关节体和刚体 actor 都可以有自己的配置类。
:class:`~isaaclab.assets.ArticulationCfg` 类可用于定义关节体 actor 的参数，
包括文件路径、仿真参数、执行器属性和初始状态。

.. code-block::python

   from isaaclab.actuators import ImplicitActuatorCfg
   from isaaclab.assets import ArticulationCfg

   CARTPOLE_CFG = ArticulationCfg(
       spawn=sim_utils.UsdFileCfg(
           usd_path=f"{ISAACLAB_NUCLEUS_DIR}/Robots/Classic/Cartpole/cartpole.usd",
           rigid_props=sim_utils.RigidBodyPropertiesCfg(
               rigid_body_enabled=True,
               max_linear_velocity=1000.0,
               max_angular_velocity=1000.0,
               max_depenetration_velocity=100.0,
               enable_gyroscopic_forces=True,
           ),
           articulation_props=sim_utils.ArticulationRootPropertiesCfg(
               enabled_self_collisions=False,
               solver_position_iteration_count=4,
               solver_velocity_iteration_count=0,
               sleep_threshold=0.005,
               stabilization_threshold=0.001,
           ),
       ),
       init_state=ArticulationCfg.InitialStateCfg(
           pos=(0.0, 0.0, 2.0), joint_pos={"slider_to_cart": 0.0, "cart_to_pole": 0.0}
       ),
       actuators={
           "cart_actuator": ImplicitActuatorCfg(
               joint_names_expr=["slider_to_cart"],
               effort_limit_sim=400.0,
               velocity_limit_sim=100.0,
               stiffness=0.0,
               damping=10.0,
           ),
           "pole_actuator": ImplicitActuatorCfg(
               joint_names_expr=["cart_to_pole"], effort_limit=400.0, velocity_limit=100.0, stiffness=0.0, damping=0.0
           ),
       },
   )

在 :class:`~assets.ArticulationCfg` 中， ``spawn`` 属性可通过
指定机器人文件的路径将机器人添加到场景中。此外， :class:`~isaaclab.sim.schemas.RigidBodyPropertiesCfg`
类可用于指定关节体中刚体的仿真属性。类似地，
:class:`~isaaclab.sim.schemas.ArticulationRootPropertiesCfg` 类可用于指定
关节体的仿真属性。关节属性现在作为 ``actuators`` 字典的一部分，使用
:class:`~actuators.ImplicitActuatorCfg` 来指定。具有相同属性的关节可以组合成正则表达式或
以名称或表达式列表的形式提供。

只需调用 ``self.cartpole = Articulation(self.cfg.robot_cfg)`` 即可将 actor 添加到场景中，其中
``self.cfg.robot_cfg`` 是一个 :class:`~assets.ArticulationCfg` 对象。初始化后，还应将其
添加到 :class:`~scene.InteractiveScene` 中，方法是调用 ``self.scene.articulations["cartpole"] = self.cartpole`` ，这样
:class:`~scene.InteractiveScene` 便能够遍历场景中的 actor，用于向仿真
写入数值和重置。


从仿真中访问状态
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在 Isaac Lab 中，访问物理状态的 API 需要创建 :class:`~assets.Articulation` 或
:class:`~assets.RigidObject` 对象。可以按照上一节所述，通过定义相应的 :class:`~assets.ArticulationCfg` 或 :class:`~assets.RigidObjectCfg` 配置，
为场景中不同的关节体或刚体初始化多个对象。
这取代了 OmniIsaacGymEnvs 中先前使用的 :class:`~omni.isaac.core.articulations.ArticulationView`
和 :class:`omni.isaac.core.prims.RigidPrimView` 类。

不过，这些类之间的功能是类似的：

+------------------------------------------------------------------+-----------------------------------------------------------------+
| OmniIsaacGymEnvs                                                 | Isaac Lab                                                       |
+------------------------------------------------------------------+-----------------------------------------------------------------+
|.. code-block:: python                                            |.. code-block:: python                                           |
|                                                                  |                                                                 |
|   dof_pos = self._cartpoles.get_joint_positions(clone=False)     |   self.joint_pos = self._robot.data.joint_pos                   |
|   dof_vel = self._cartpoles.get_joint_velocities(clone=False)    |   self.joint_vel = self._robot.data.joint_vel                   |
+------------------------------------------------------------------+-----------------------------------------------------------------+

在 Isaac Lab 中， :class:`~assets.Articulation` 和 :class:`~assets.RigidObject` 类都有一个 ``data`` 类。
这些数据类（ :class:`~assets.ArticulationData` 和 :class:`~assets.RigidObjectData` ）包含
保存关节体和刚体对象状态的缓冲区，并提供
一种性能更好的从 actor 获取状态的方式。

除了一些 API 重命名之外，在 OmniIsaacGymEnvs 和 Isaac Lab 中设置 actor 状态的方式也是类似的。

+---------------------------------------------------------------------------+---------------------------------------------------------------+
| OmniIsaacGymEnvs                                                          | Isaac Lab                                                     |
+---------------------------------------------------------------------------+---------------------------------------------------------------+
|.. code-block:: python                                                     |.. code-block:: python                                         |
|                                                                           |                                                               |
|   indices = env_ids.to(dtype=torch.int32)                                 |   self._robot.write_joint_state_to_sim(joint_pos, joint_vel,  |
|   self._cartpoles.set_joint_positions(dof_pos, indices=indices)           |                                    joint_ids, env_ids)        |
|   self._cartpoles.set_joint_velocities(dof_vel, indices=indices)          |                                                               |
+---------------------------------------------------------------------------+---------------------------------------------------------------+

在 Isaac Lab 中， ``root_pose`` 和 ``root_velocity`` 已被合并为单个缓冲区，不再拆分为
``root_position`` 、 ``root_orientation`` 、 ``root_linear_velocity`` 和 ``root_angular_velocity`` 。

.. code-block::python

    self.cartpole.write_root_pose_to_sim(default_root_state[:, :7], env_ids)
    self.cartpole.write_root_velocity_to_sim(default_root_state[:, 7:], env_ids)


创建新环境
~~~~~~~~~~~~~~~~~~~~~~~~~~

Isaac Lab 中的每个环境都应位于其自己的目录中，并遵循以下结构：

.. code-block:: none

    my_environment/
        - agents/
            - __init__.py
            - rl_games_ppo_cfg.py
        - __init__.py
        my_env.py

* ``my_environment`` 是任务的根目录。
* ``my_environment/agents`` 是包含该任务所有 RL 配置文件的目录。Isaac Lab 支持多个
  RL 库，每个库可以有自己的单独配置文件。
* ``my_environment/__init__.py`` 是向 Gymnasium 接口注册环境的主文件。
  这使得训练和推理脚本能够按名称查找任务。
  该文件的内容应如下：

  .. code-block:: python

    import gymnasium as gym

    from . import agents
    from .cartpole_env import CartpoleEnv, CartpoleEnvCfg

    ##
    # Register Gym environments.
    ##

    gym.register(
        id="Isaac-Cartpole-Direct-v0",
        entry_point="isaaclab_tasks.direct_workflow.cartpole:CartpoleEnv",
        disable_env_checker=True,
        kwargs={
            "env_cfg_entry_point": CartpoleEnvCfg,
            "rl_games_cfg_entry_point": f"{agents.__name__}:rl_games_ppo_cfg.yaml"
        },
    )

* ``my_environment/my_env.py`` 是实现该环境任务逻辑和任务配置类的主
  Python 脚本。


任务逻辑
~~~~~~~~~~

OmniIsaacGymEnvs 中的 ``post_reset`` API 在 Isaac Lab 中不再需要。之前在 ``post_reset`` 中
完成的所有工作都可以在执行基类的
``__init__`` 之后在 ``__init__`` 方法中完成。此时，仿真已经启动。

在 OmniIsaacGymEnvs 中，由于 GPU API 的限制，无法基于当前
步的状态执行重置。相反，重置必须在下一个时间步开始时执行。
这一限制在 Isaac Lab 中已被消除，因此任务遵循正确的工作流：应用动作、
步进仿真、收集状态、计算 done、计算奖励、执行重置，最后计算
观测。此工作流由框架自动完成，因此任务中不需要 ``post_physics_step`` API。
不过，单个任务可以覆盖 ``step()`` API 来控制该工作流。

在 Isaac Lab 中，我们还将用于处理策略动作的 ``pre_physics_step`` API 与
将动作设置到仿真中的 ``apply_action`` API 分开。这在使用 ``decimation`` 时为控制
动作何时写入仿真提供了更大的灵活性。
``pre_physics_step`` 方法会在每步仿真之前调用一次。
``apply_actions`` 方法在每个 RL 步中被调用 ``decimation`` 次，
在每次仿真步调用之前各调用一次。

调用的顺序如下：

+----------------------------------+----------------------------------+
| OmniIsaacGymEnvs                 | Isaac Lab                        |
+----------------------------------+----------------------------------+
|.. code-block:: none              |.. code-block:: none              |
|                                  |                                  |
|   pre_physics_step               |   pre_physics_step               |
|     |-- reset_idx()              |     |-- _pre_physics_step(action)|
|     |-- apply_action             |     |-- _apply_action()          |
|                                  |                                  |
|   post_physics_step              |   post_physics_step              |
|     |-- get_observations()       |     |-- _get_dones()             |
|     |-- calculate_metrics()      |     |-- _get_rewards()           |
|     |-- is_done()                |     |-- _reset_idx()             |
|                                  |     |-- _get_observations()      |
+----------------------------------+----------------------------------+

采用这种方法后，重置将基于当前步的动作而不是上一步的动作执行。
观测也将在重置后使用正确的状态进行计算。

我们还对一些 API 进行了重命名：

* ``set_up_scene(self, scene)`` --> ``_setup_scene(self)``
* ``post_reset(self)`` --> ``__init__(...)``
* ``pre_physics_step(self, actions)`` --> ``_pre_physics_step(self, actions)`` 和 ``_apply_action(self)``
* ``reset_idx(self, env_ids)`` --> ``_reset_idx(self, env_ids)``
* ``get_observations(self)`` --> ``_get_observations(self)`` - ``_get_observations()`` 现在应返回字典 ``{"policy": obs}``
* ``calculate_metrics(self)`` --> ``_get_rewards(self)`` - ``_get_rewards()`` 现在应返回奖励缓冲区
* ``is_done(self)`` --> ``_get_dones(self)`` - ``_get_dones()`` 现在应返回 2 个缓冲区： ``reset`` 和 ``time_out`` 缓冲区



整合所有内容
~~~~~~~~~~~~~~~~~~~~~~~

这里完整展示了 Cartpole 环境，以充分展示 OmniIsaacGymEnvs
实现与 Isaac Lab 实现之间的比较。

任务配置
-----------

Isaac Lab 中的任务配置可以拆分为主任务配置类和各个 actor 的单独配置对象。

+-----------------------------------------------------------------+-----------------------------------------------------------------+
| OmniIsaacGymEnvs                                                | Isaac Lab                                                       |
+-----------------------------------------------------------------+-----------------------------------------------------------------+
|.. code-block:: yaml                                             |.. code-block:: python                                           |
|                                                                 |                                                                 |
| # used to create the object                                     | @configclass                                                    |
|                                                                 | class CartpoleEnvCfg(DirectRLEnvCfg):                           |
| name: Cartpole                                                  |                                                                 |
|                                                                 |     # simulation                                                |
| physics_engine: ${..physics_engine}                             |     sim: SimulationCfg = SimulationCfg(dt=1 / 120)              |
|                                                                 |     # robot                                                     |
| # if given, will override the device setting in gym.            |     robot_cfg: ArticulationCfg = CARTPOLE_CFG.replace(          |
| env:                                                            |         prim_path="/World/envs/env_.*/Robot")                   |
|                                                                 |     cart_dof_name = "slider_to_cart"                            |
|   numEnvs: ${resolve_default:512,${...num_envs}}                |     pole_dof_name = "cart_to_pole"                              |
|   envSpacing: 4.0                                               |     # scene                                                     |
|   resetDist: 3.0                                                |     scene: InteractiveSceneCfg = InteractiveSceneCfg(           |
|   maxEffort: 400.0                                              |       num_envs=4096, env_spacing=4.0, replicate_physics=True)   |
|                                                                 |     # env                                                       |
|   clipObservations: 5.0                                         |     decimation = 2                                              |
|   clipActions: 1.0                                              |     episode_length_s = 5.0                                      |
|   controlFrequencyInv: 2 # 60 Hz                                |     action_scale = 100.0  # [N]                                 |
|                                                                 |     action_space = 1                                            |
| sim:                                                            |     observation_space = 4                                       |
|                                                                 |     state_space = 0                                             |
|   dt: 0.0083 # 1/120 s                                          |     # reset                                                     |
|   use_gpu_pipeline: ${eq:${...pipeline},"gpu"}                  |     max_cart_pos = 3.0                                          |
|   gravity: [0.0, 0.0, -9.81]                                    |     initial_pole_angle_range = [-0.25, 0.25]                    |
|   add_ground_plane: True                                        |     # reward scales                                             |
|   add_distant_light: False                                      |     rew_scale_alive = 1.0                                       |
|   use_fabric: True                                              |     rew_scale_terminated = -2.0                                 |
|   enable_scene_query_support: False                             |     rew_scale_pole_pos = -1.0                                   |
|   disable_contact_processing: False                             |     rew_scale_cart_vel = -0.01                                  |
|                                                                 |     rew_scale_pole_vel = -0.005                                 |
|   enable_cameras: False                                         |                                                                 |
|                                                                 |                                                                 |
|   default_physics_material:                                     | CARTPOLE_CFG = ArticulationCfg(                                 |
|     static_friction: 1.0                                        |   spawn=sim_utils.UsdFileCfg(                                   |
|     dynamic_friction: 1.0                                       |     usd_path=f"{ISAACLAB_NUCLEUS_DIR}/.../cartpole.usd",        |
|     restitution: 0.0                                            |     rigid_props=sim_utils.RigidBodyPropertiesCfg(               |
|                                                                 |       rigid_body_enabled=True,                                  |
|   physx:                                                        |       max_linear_velocity=1000.0,                               |
|     worker_thread_count: ${....num_threads}                     |       max_angular_velocity=1000.0,                              |
|     solver_type: ${....solver_type}                             |       max_depenetration_velocity=100.0,                         |
|     use_gpu: ${eq:${....sim_device},"gpu"} # set to False to... |       enable_gyroscopic_forces=True,                            |
|     solver_position_iteration_count: 4                          |     ),                                                          |
|     solver_velocity_iteration_count: 0                          |     articulation_props=sim_utils.ArticulationRootPropertiesCfg( |
|     contact_offset: 0.02                                        |       enabled_self_collisions=False,                            |
|     rest_offset: 0.001                                          |       solver_position_iteration_count=4,                        |
|     bounce_threshold_velocity: 0.2                              |       solver_velocity_iteration_count=0,                        |
|     friction_offset_threshold: 0.04                             |       sleep_threshold=0.005,                                    |
|     friction_correlation_distance: 0.025                        |       stabilization_threshold=0.001,                            |
|     enable_sleeping: True                                       |     ),                                                          |
|     enable_stabilization: True                                  |   ),                                                            |
|     max_depenetration_velocity: 100.0                           |   init_state=ArticulationCfg.InitialStateCfg(                   |
|                                                                 |     pos=(0.0, 0.0, 2.0),                                        |
|     # GPU buffers                                               |     joint_pos={"slider_to_cart": 0.0, "cart_to_pole": 0.0}      |
|     gpu_max_rigid_contact_count: 524288                         |   ),                                                            |
|     gpu_max_rigid_patch_count: 81920                            |   actuators={                                                   |
|     gpu_found_lost_pairs_capacity: 1024                         |     "cart_actuator": ImplicitActuatorCfg(                       |
|     gpu_found_lost_aggregate_pairs_capacity: 262144             |        joint_names_expr=["slider_to_cart"],                     |
|     gpu_total_aggregate_pairs_capacity: 1024                    |        effort_limit=400.0,                                      |
|     gpu_max_soft_body_contacts: 1048576                         |        velocity_limit=100.0,                                    |
|     gpu_max_particle_contacts: 1048576                          |        stiffness=0.0,                                           |
|     gpu_heap_capacity: 67108864                                 |        damping=10.0,                                            |
|     gpu_temp_buffer_capacity: 16777216                          |     ),                                                          |
|     gpu_max_num_partitions: 8                                   |     "pole_actuator": ImplicitActuatorCfg(                       |
|                                                                 |        joint_names_expr=["cart_to_pole"], effort_limit=400.0,   |
|     Cartpole:                                                   |        velocity_limit=100.0, stiffness=0.0, damping=0.0         |
|       override_usd_defaults: False                              |     ),                                                          |
|       enable_self_collisions: False                             |   },                                                            |
|       enable_gyroscopic_forces: True                            | )                                                               |
|       solver_position_iteration_count: 4                        |                                                                 |
|       solver_velocity_iteration_count: 0                        |                                                                 |
|       sleep_threshold: 0.005                                    |                                                                 |
|       stabilization_threshold: 0.001                            |                                                                 |
|       density: -1                                               |                                                                 |
|       max_depenetration_velocity: 100.0                         |                                                                 |
|       contact_offset: 0.02                                      |                                                                 |
|       rest_offset: 0.001                                        |                                                                 |
+-----------------------------------------------------------------+-----------------------------------------------------------------+



任务设置
----------

OmniIsaacGymEnvs 中的 ``post_reset`` API 在 Isaac Lab 中不再需要。
之前在 ``post_reset`` 中完成的所有工作都可以在执行基类的 ``__init__`` 之后在
``__init__`` 方法中完成。此时，仿真已经启动。

+-------------------------------------------------------------------------+-------------------------------------------------------------+
| OmniIsaacGymEnvs                                                        | Isaac Lab                                                   |
+-------------------------------------------------------------------------+-------------------------------------------------------------+
|.. code-block:: python                                                   |.. code-block:: python                                       |
|                                                                         |                                                             |
| class CartpoleTask(RLTask):                                             | class CartpoleEnv(DirectRLEnv):                             |
|                                                                         |     cfg: CartpoleEnvCfg                                     |
|     def __init__(self, name, sim_config, env, offset=None) -> None:     |     def __init__(self, cfg: CartpoleEnvCfg,                 |
|                                                                         |              render_mode: str | None = None, **kwargs):     |
|         self.update_config(sim_config)                                  |         super().__init__(cfg, render_mode, **kwargs)        |
|         self._max_episode_length = 500                                  |                                                             |
|                                                                         |                                                             |
|         self._num_observations = 4                                      |         self._cart_dof_idx, _ = self.cartpole.find_joints(  |
|         self._num_actions = 1                                           |               self.cfg.cart_dof_name)                       |
|                                                                         |         self._pole_dof_idx, _ = self.cartpole.find_joints(  |
|         RLTask.__init__(self, name, env)                                |                self.cfg.pole_dof_name)                      |
|                                                                         |         self.action_scale=self.cfg.action_scale             |
|         def update_config(self, sim_config):                            |                                                             |
|             self._sim_config = sim_config                               |         self.joint_pos = self.cartpole.data.joint_pos       |
|             self._cfg = sim_config.config                               |         self.joint_vel = self.cartpole.data.joint_vel       |
|             self._task_cfg = sim_config.                                |                                                             |
|             task_config                                                 |                                                             |
|                                                                         |                                                             |
|             self._num_envs = self._task_cfg["env"]["numEnvs"]           |                                                             |
|             self._env_spacing = self._task_cfg["env"]["envSpacing"]     |                                                             |
|             self._cartpole_positions = torch.tensor([0.0, 0.0, 2.0])    |                                                             |
|                                                                         |                                                             |
|             self._reset_dist = self._task_cfg["env"]["resetDist"]       |                                                             |
|             self._max_push_effort = self._task_cfg["env"]["maxEffort"]  |                                                             |
|                                                                         |                                                             |
|                                                                         |                                                             |
|         def post_reset(self):                                           |                                                             |
|             self._cart_dof_idx = self._cartpoles.get_dof_index(         |                                                             |
|                 "cartJoint")                                            |                                                             |
|             self._pole_dof_idx = self._cartpoles.get_dof_index(         |                                                             |
|                 "poleJoint")                                            |                                                             |
|             # randomize all envs                                        |                                                             |
|             indices = torch.arange(                                     |                                                             |
|                 self._cartpoles.count, dtype=torch.int64,               |                                                             |
|                 device=self._device)                                    |                                                             |
|             self.reset_idx(indices)                                     |                                                             |
+-------------------------------------------------------------------------+-------------------------------------------------------------+



场景设置
-----------

OmniIsaacGymEnvs 中的 ``set_up_scene`` 方法已被 Isaac Lab 任务类中的 ``_setup_scene`` API 取代。
此外，场景克隆和碰撞过滤已作为 API 提供，任务类可以在需要时
调用。同样，添加地平面和灯光也应在任务类中处理。
向场景添加 actor 已被 ``self.scene.articulations["cartpole"] = self.cartpole`` 取代。

+-----------------------------------------------------------+----------------------------------------------------------+
| OmniIsaacGymEnvs                                          | Isaac Lab                                                |
+-----------------------------------------------------------+----------------------------------------------------------+
|.. code-block:: python                                     |.. code-block:: python                                    |
|                                                           |                                                          |
| def set_up_scene(self, scene) -> None:                    | def _setup_scene(self):                                  |
|                                                           |     self.cartpole = Articulation(self.cfg.robot_cfg)     |
|     self.get_cartpole()                                   |     # add ground plane                                   |
|     super().set_up_scene(scene)                           |     spawn_ground_plane(prim_path="/World/ground",        |
|     self._cartpoles = ArticulationView(                   |         cfg=GroundPlaneCfg())                            |
|         prim_paths_expr="/World/envs/.*/Cartpole",        |     # clone, filter, and replicate                       |
|         name="cartpole_view",                             |     self.scene.clone_environments(                       |
|         reset_xform_properties=False                      |         copy_from_source=False)                          |
|     )                                                     |     self.scene.filter_collisions(                        |
|     scene.add(self._cartpoles)                            |         global_prim_paths=[])                            |
|     return                                                |     # add articulation to scene                          |
|                                                           |     self.scene.articulations["cartpole"] = self.cartpole |
| def get_cartpole(self):                                   |                                                          |
|     cartpole = Cartpole(                                  |     # add lights                                         |
|         prim_path=self.default_zero_env_path+"/Cartpole", |     light_cfg = sim_utils.DomeLightCfg(                  |
|         name="Cartpole",                                  |         intensity=2000.0, color=(0.75, 0.75, 0.75))      |
|         translation=self._cartpole_positions              |     light_cfg.func("/World/Light", light_cfg)            |
|     )                                                     |                                                          |
|     # applies articulation settings from the              |                                                          |
|     # task configuration yaml file                        |                                                          |
|     self._sim_config.apply_articulation_settings(         |                                                          |
|         "Cartpole", get_prim_at_path(cartpole.prim_path), |                                                          |
|         self._sim_config.parse_actor_config("Cartpole")   |                                                          |
|     )                                                     |                                                          |
+-----------------------------------------------------------+----------------------------------------------------------+


物理步前处理
----------------

请注意， ``pre_physics_step`` API 中不再执行重置。此外，
``_pre_physics_step`` 和 ``_apply_action`` 方法的分离为处理动作缓冲区
和将动作设置到仿真中提供了更多灵活性。

+------------------------------------------------------------------+-------------------------------------------------------------+
| OmniIsaacGymEnvs                                                 | IsaacLab                                                    |
+------------------------------------------------------------------+-------------------------------------------------------------+
|.. code-block:: python                                            |.. code-block:: python                                       |
|                                                                  |                                                             |
| def pre_physics_step(self, actions) -> None:                     | def _pre_physics_step(self,                                 |
|     if not self.world.is_playing():                              |         actions: torch.Tensor) -> None:                     |
|         return                                                   |     self.actions = self.action_scale * actions              |
|                                                                  |                                                             |
|     reset_env_ids = self.reset_buf.nonzero(                      | def _apply_action(self) -> None:                            |
|         as_tuple=False).squeeze(-1)                              |     self.cartpole.set_joint_effort_target(                  |
|     if len(reset_env_ids) > 0:                                   |         self.actions, joint_ids=self._cart_dof_idx)         |
|         self.reset_idx(reset_env_ids)                            |                                                             |
|                                                                  |                                                             |
|     actions = actions.to(self._device)                           |                                                             |
|                                                                  |                                                             |
|     forces = torch.zeros((self._cartpoles.count,                 |                                                             |
|         self._cartpoles.num_dof),                                |                                                             |
|         dtype=torch.float32, device=self._device)                |                                                             |
|     forces[:, self._cart_dof_idx] =                              |                                                             |
|         self._max_push_effort * actions[:, 0]                    |                                                             |
|                                                                  |                                                             |
|     indices = torch.arange(self._cartpoles.count,                |                                                             |
|         dtype=torch.int32, device=self._device)                  |                                                             |
|     self._cartpoles.set_joint_efforts(                           |                                                             |
|         forces, indices=indices)                                 |                                                             |
+------------------------------------------------------------------+-------------------------------------------------------------+


Done 与重置
----------------

在 Isaac Lab 中， ``dones`` 在 ``_get_dones()`` 方法中计算，应返回两个变量： ``resets`` 和
``time_out`` 。 ``_reset_idx()`` 方法也是在步进仿真之后调用，而不是像
OmniIsaacGymEnvs 中那样在之前调用。 ``progress_buf`` 张量在 Isaac Lab 中已被重命名为 ``episode_length_buf`` ，并且
簿记工作现在由框架自动完成。任务实现不再需要递增或
重置 ``episode_length_buf`` 缓冲区。

+------------------------------------------------------------------+--------------------------------------------------------------------------+
| OmniIsaacGymEnvs                                                 | Isaac Lab                                                                |
+------------------------------------------------------------------+--------------------------------------------------------------------------+
|.. code-block:: python                                            |.. code-block:: python                                                    |
|                                                                  |                                                                          |
| def is_done(self) -> None:                                       | def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:               |
|   resets = torch.where(                                          |     self.joint_pos = self.cartpole.data.joint_pos                        |
|     torch.abs(self.cart_pos) > self._reset_dist, 1, 0)           |     self.joint_vel = self.cartpole.data.joint_vel                        |
|   resets = torch.where(                                          |                                                                          |
|     torch.abs(self.pole_pos) > math.pi / 2, 1, resets)           |     time_out = self.episode_length_buf >= self.max_episode_length - 1    |
|   resets = torch.where(                                          |     out_of_bounds = torch.any(torch.abs(                                 |
|     self.progress_buf >= self._max_episode_length, 1, resets)    |         self.joint_pos[:, self._cart_dof_idx]) > self.cfg.max_cart_pos,  |
|   self.reset_buf[:] = resets                                     |         dim=1)                                                           |
|                                                                  |     out_of_bounds = out_of_bounds | torch.any(                           |
|                                                                  |         torch.abs(self.joint_pos[:, self._pole_dof_idx]) > math.pi / 2,  |
|                                                                  |         dim=1)                                                           |
|                                                                  |     return out_of_bounds, time_out                                       |
|                                                                  |                                                                          |
| def reset_idx(self, env_ids):                                    | def _reset_idx(self, env_ids: Sequence[int] | None):                     |
|   num_resets = len(env_ids)                                      |     if env_ids is None:                                                  |
|                                                                  |         env_ids = self.cartpole._ALL_INDICES                             |
|   # randomize DOF positions                                      |     super()._reset_idx(env_ids)                                          |
|   dof_pos = torch.zeros((num_resets, self._cartpoles.num_dof),   |                                                                          |
|       device=self._device)                                       |     joint_pos = self.cartpole.data.default_joint_pos[env_ids]            |
|   dof_pos[:, self._cart_dof_idx] = 1.0 * (                       |     joint_pos[:, self._pole_dof_idx] += sample_uniform(                  |
|       1.0 - 2.0 * torch.rand(num_resets, device=self._device))   |         self.cfg.initial_pole_angle_range[0] * math.pi,                  |
|   dof_pos[:, self._pole_dof_idx] = 0.125 * math.pi * (           |         self.cfg.initial_pole_angle_range[1] * math.pi,                  |
|       1.0 - 2.0 * torch.rand(num_resets, device=self._device))   |         joint_pos[:, self._pole_dof_idx].shape,                          |
|                                                                  |         joint_pos.device,                                                |
|   # randomize DOF velocities                                     |     )                                                                    |
|   dof_vel = torch.zeros((num_resets, self._cartpoles.num_dof),   |     joint_vel = self.cartpole.data.default_joint_vel[env_ids]            |
|       device=self._device)                                       |                                                                          |
|   dof_vel[:, self._cart_dof_idx] = 0.5 * (                       |     default_root_state = self.cartpole.data.default_root_state[env_ids]  |
|       1.0 - 2.0 * torch.rand(num_resets, device=self._device))   |     default_root_state[:, :3] += self.scene.env_origins[env_ids]         |
|   dof_vel[:, self._pole_dof_idx] = 0.25 * math.pi * (            |                                                                          |
|       1.0 - 2.0 * torch.rand(num_resets, device=self._device))   |     self.joint_pos[env_ids] = joint_pos                                  |
|                                                                  |     self.joint_vel[env_ids] = joint_vel                                  |
|   # apply resets                                                 |                                                                          |
|   indices = env_ids.to(dtype=torch.int32)                        |     self.cartpole.write_root_pose_to_sim(                                |
|   self._cartpoles.set_joint_positions(dof_pos, indices=indices)  |         default_root_state[:, :7], env_ids)                              |
|   self._cartpoles.set_joint_velocities(dof_vel, indices=indices) |     self.cartpole.write_root_velocity_to_sim(                            |
|                                                                  |         default_root_state[:, 7:], env_ids)                              |
|   # bookkeeping                                                  |     self.cartpole.write_joint_state_to_sim(                              |
|   self.reset_buf[env_ids] = 0                                    |         joint_pos, joint_vel, None, env_ids)                             |
|   self.progress_buf[env_ids] = 0                                 |                                                                          |
|                                                                  |                                                                          |
|                                                                  |                                                                          |
+------------------------------------------------------------------+--------------------------------------------------------------------------+


奖励
-------

在 Isaac Lab 中，奖励在 ``_get_rewards`` API 中实现，应返回奖励缓冲区，而不是直接将其赋值给
``self.rew_buf`` 。奖励函数中的计算也可以通过定义带有 ``@torch.jit.script`` 注解的函数来使用 pytorch jit
执行。

+-------------------------------------------------------+-----------------------------------------------------------------------+
| OmniIsaacGymEnvs                                      | Isaac Lab                                                             |
+-------------------------------------------------------+-----------------------------------------------------------------------+
|.. code-block:: python                                 |.. code-block:: python                                                 |
|                                                       |                                                                       |
| def calculate_metrics(self) -> None:                  | def _get_rewards(self) -> torch.Tensor:                               |
|     reward = (1.0 - self.pole_pos * self.pole_pos     |     total_reward = compute_rewards(                                   |
|         - 0.01 * torch.abs(self.cart_vel) - 0.005     |         self.cfg.rew_scale_alive,                                     |
|         * torch.abs(self.pole_vel))                   |         self.cfg.rew_scale_terminated,                                |
|     reward = torch.where(                             |         self.cfg.rew_scale_pole_pos,                                  |
|         torch.abs(self.cart_pos) > self._reset_dist,  |         self.cfg.rew_scale_cart_vel,                                  |
|         torch.ones_like(reward) * -2.0, reward)       |         self.cfg.rew_scale_pole_vel,                                  |
|     reward = torch.where(                             |         self.joint_pos[:, self._pole_dof_idx[0]],                     |
|         torch.abs(self.pole_pos) > np.pi / 2,         |         self.joint_vel[:, self._pole_dof_idx[0]],                     |
|         torch.ones_like(reward) * -2.0, reward)       |         self.joint_pos[:, self._cart_dof_idx[0]],                     |
|                                                       |         self.joint_vel[:, self._cart_dof_idx[0]],                     |
|     self.rew_buf[:] = reward                          |         self.reset_terminated,                                        |
|                                                       |     )                                                                 |
|                                                       |     return total_reward                                               |
|                                                       |                                                                       |
|                                                       | @torch.jit.script                                                     |
|                                                       | def compute_rewards(                                                  |
|                                                       |     rew_scale_alive: float,                                           |
|                                                       |     rew_scale_terminated: float,                                      |
|                                                       |     rew_scale_pole_pos: float,                                        |
|                                                       |     rew_scale_cart_vel: float,                                        |
|                                                       |     rew_scale_pole_vel: float,                                        |
|                                                       |     pole_pos: torch.Tensor,                                           |
|                                                       |     pole_vel: torch.Tensor,                                           |
|                                                       |     cart_pos: torch.Tensor,                                           |
|                                                       |     cart_vel: torch.Tensor,                                           |
|                                                       |     reset_terminated: torch.Tensor,                                   |
|                                                       | ):                                                                    |
|                                                       |     rew_alive = rew_scale_alive * (1.0 - reset_terminated.float())    |
|                                                       |     rew_termination = rew_scale_terminated * reset_terminated.float() |
|                                                       |     rew_pole_pos = rew_scale_pole_pos * torch.sum(                    |
|                                                       |         torch.square(pole_pos), dim=-1)                               |
|                                                       |     rew_cart_vel = rew_scale_cart_vel * torch.sum(                    |
|                                                       |         torch.abs(cart_vel), dim=-1)                                  |
|                                                       |     rew_pole_vel = rew_scale_pole_vel * torch.sum(                    |
|                                                       |         torch.abs(pole_vel), dim=-1)                                  |
|                                                       |     total_reward = (rew_alive + rew_termination                       |
|                                                       |         + rew_pole_pos + rew_cart_vel + rew_pole_vel)                 |
|                                                       |     return total_reward                                               |
+-------------------------------------------------------+-----------------------------------------------------------------------+


观测
------------

在 Isaac Lab 中， ``_get_observations()`` API 必须返回一个字典，其中包含键 ``policy`` ，对应的值为观测缓冲区。
在使用非对称 actor-critic 状态时，critic 的状态应使用键 ``critic`` ，并与观测缓冲区一起在
同一个字典中返回。

+------------------------------------------------------------------+-------------------------------------------------------------+
| OmniIsaacGymEnvs                                                 | Isaac Lab                                                   |
+------------------------------------------------------------------+-------------------------------------------------------------+
|.. code-block:: python                                            |.. code-block::                                              |
|                                                                  |                                                             |
| def get_observations(self) -> dict:                              | def _get_observations(self) -> dict:                        |
|     dof_pos = self._cartpoles.get_joint_positions(clone=False)   |     obs = torch.cat(                                        |
|     dof_vel = self._cartpoles.get_joint_velocities(clone=False)  |                  (                                          |
|                                                                  |            self.joint_pos[:, self._pole_dof_idx[0]],        |
|     self.cart_pos = dof_pos[:, self._cart_dof_idx]               |            self.joint_vel[:, self._pole_dof_idx[0]],        |
|     self.cart_vel = dof_vel[:, self._cart_dof_idx]               |            self.joint_pos[:, self._cart_dof_idx[0]],        |
|     self.pole_pos = dof_pos[:, self._pole_dof_idx]               |            self.joint_vel[:, self._cart_dof_idx[0]],        |
|     self.pole_vel = dof_vel[:, self._pole_dof_idx]               |         ),                                                  |
|     self.obs_buf[:, 0] = self.cart_pos                           |         dim=-1,                                             |
|     self.obs_buf[:, 1] = self.cart_vel                           |     )                                                       |
|     self.obs_buf[:, 2] = self.pole_pos                           |     observations = {"policy": obs}                          |
|     self.obs_buf[:, 3] = self.pole_vel                           |     return observations                                     |
|                                                                  |                                                             |
|     observations = {self._cartpoles.name:                        |                                                             |
|         {"obs_buf": self.obs_buf}}                               |                                                             |
|     return observations                                          |                                                             |
+------------------------------------------------------------------+-------------------------------------------------------------+


域随机化
~~~~~~~~~~~~~~~~~~~~

在 OmniIsaacGymEnvs 中，域随机化通过任务 ``.yaml`` 配置文件指定。
在 Isaac Lab 中，域随机化配置使用 :class:`~isaaclab.utils.configclass` 模块
来指定一个由 :class:`~managers.EventTermCfg` 变量组成的配置类。

下面是一个域随机化配置类的示例：

.. code-block:: python

  @configclass
  class EventCfg:
    robot_physics_material = EventTerm(
        func=mdp.randomize_rigid_body_material,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=".*"),
            "static_friction_range": (0.7, 1.3),
            "dynamic_friction_range": (1.0, 1.0),
            "restitution_range": (1.0, 1.0),
            "num_buckets": 250,
        },
    )
    robot_joint_stiffness_and_damping = EventTerm(
        func=mdp.randomize_actuator_gains,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("robot", joint_names=".*"),
            "stiffness_distribution_params": (0.75, 1.5),
            "damping_distribution_params": (0.3, 3.0),
            "operation": "scale",
            "distribution": "log_uniform",
        },
    )
    reset_gravity = EventTerm(
        func=mdp.randomize_physics_scene_gravity,
        mode="interval",
        is_global_time=True,
        interval_range_s=(36.0, 36.0),  # time_s = num_steps * (decimation * dt)
        params={
            "gravity_distribution_params": ([0.0, 0.0, 0.0], [0.0, 0.0, 0.4]),
            "operation": "add",
            "distribution": "gaussian",
        },
    )

每个 ``EventTerm`` 对象都是 :class:`~managers.EventTermCfg` 类的实例，它接受一个 ``func`` 参数
用于指定随机化期间要调用的函数，以及一个 ``mode`` 参数，可以是 ``startup`` 、
``reset`` 或 ``interval`` 。 ``params`` 字典应向
``func`` 参数中指定的函数提供必要的参数。
``EventTerm`` 的 ``func`` 所指定的函数可以在 :class:`~envs.mdp.events` 模块中找到。

请注意，在 ``"asset_cfg": SceneEntityCfg("robot", body_names=".*")`` 参数中，
提供了 actor 的名称 ``"robot"`` ，以及以正则表达式形式指定的刚体或关节名称，
它们将是应用随机化的 actor 和刚体/关节。

与 OmniIsaacGymEnvs 的一个区别是， ``interval`` 随机化现在以秒而不是
步数来指定。当 ``mode="interval"`` 时，还必须提供 ``interval_range_s`` 参数，它指定
应用随机化的秒数范围。然后该范围会被随机化，
以确定该项下一次随机化发生的时间（以秒为单位）。
要在步数和秒之间转换，请使用等式 ``time_s = num_steps * (decimation * dt)`` 。

与 OmniIsaacGymEnvs 类似，随机化 API 可用于随机化关节体属性，
例如关节刚度和阻尼、关节限制、刚体材质、固定腱（fixed tendon）属性，
以及刚体属性，例如质量和刚体材质。物理场景重力的随机化
也受支持。请注意，Isaac Lab 目前不支持缩放的随机化。
要随机化缩放，请在设置场景时让每个环境以不同的缩放比例持有 actor。

设置好随机化项的 ``configclass`` 后，必须将该类添加到
任务的基础配置类中，并将其赋值给变量 ``events`` 。

.. code-block:: python

  @configclass
  class MyTaskConfig:
    events: EventCfg = EventCfg()


动作与观测噪声
----------------------------

也可以使用 :class:`~utils.configclass` 模块添加动作和观测噪声。
动作和观测噪声配置必须通过
``action_noise_model`` 和 ``observation_noise_model`` 变量添加到主任务配置中：

.. code-block:: python

  @configclass
  class MyTaskConfig:
      # at every time-step add gaussian noise + bias. The bias is a gaussian sampled at reset
      action_noise_model: NoiseModelWithAdditiveBiasCfg = NoiseModelWithAdditiveBiasCfg(
        noise_cfg=GaussianNoiseCfg(mean=0.0, std=0.05, operation="add"),
        bias_noise_cfg=GaussianNoiseCfg(mean=0.0, std=0.015, operation="abs"),
      )
      # at every time-step add gaussian noise + bias. The bias is a gaussian sampled at reset
      observation_noise_model: NoiseModelWithAdditiveBiasCfg = NoiseModelWithAdditiveBiasCfg(
        noise_cfg=GaussianNoiseCfg(mean=0.0, std=0.002, operation="add"),
        bias_noise_cfg=GaussianNoiseCfg(mean=0.0, std=0.0001, operation="abs"),
      )


:class:`~.utils.noise.NoiseModelWithAdditiveBiasCfg` 可用于采样每步不相关的噪声
以及在重置时重新采样的相关噪声。
``noise_cfg`` 项指定每个
步为所有环境采样的高斯分布。此噪声将在每一步被添加到相应的动作和
观测缓冲区中。
``bias_noise_cfg`` 项指定相关噪声的高斯分布，
它会在重置时为被重置的环境采样。在回合的剩余时间内，
每个步都会为这些环境应用相同的噪声，
并在下一次重置时重新采样。

这取代了 OmniIsaacGymEnvs 中的以下设置：

.. code-block:: yaml

   domain_randomization:
   randomize: True
   randomization_params:
    observations:
      on_reset:
        operation: "additive"
        distribution: "gaussian"
        distribution_parameters: [0, .0001]
      on_interval:
        frequency_interval: 1
        operation: "additive"
        distribution: "gaussian"
        distribution_parameters: [0, .002]
    actions:
      on_reset:
        operation: "additive"
        distribution: "gaussian"
        distribution_parameters: [0, 0.015]
      on_interval:
        frequency_interval: 1
        operation: "additive"
        distribution: "gaussian"
        distribution_parameters: [0., 0.05]


启动训练
~~~~~~~~~~~~~~~~~~

要在 Isaac Lab 中启动训练，请使用以下命令：

.. code-block:: bash

   python scripts/reinforcement_learning/rl_games/train.py --task=Isaac-Cartpole-Direct-v0 --headless

启动推理
~~~~~~~~~~~~~~~~~~~~~

要在 Isaac Lab 中启动推理，请使用以下命令：

.. code-block:: bash

   python scripts/reinforcement_learning/rl_games/play.py --task=Isaac-Cartpole-Direct-v0 --num_envs=25 --checkpoint=<path/to/checkpoint>


.. _`OmniIsaacGymEnvs`: https://github.com/isaac-sim/OmniIsaacGymEnvs
.. _release notes: https://github.com/isaac-sim/IsaacLab/releases
