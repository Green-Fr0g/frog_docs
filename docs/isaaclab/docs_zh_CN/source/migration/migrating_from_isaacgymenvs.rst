.. _migrating-from-isaacgymenvs:

从 IsaacGymEnvs 迁移
====================

.. currentmodule:: isaaclab


`IsaacGymEnvs`_ 是一个为 `Isaac Gym Preview Release`_ 设计的强化学习框架。
由于 IsaacGymEnvs 和 Isaac Gym Preview Release 均已弃用，以下指南介绍了 IsaacGymEnvs 与 Isaac Lab 之间的
主要差异，以及 Isaac Gym Preview Release 与 Isaac Sim 之间在 API 上的差异。

.. note::

  以下变更基于 Isaac Lab 1.0 版本。未来版本中的任何变更，
  请参阅 `release notes`_ 。


任务配置设置
~~~~~~~~~~~~~~~~~

在 IsaacGymEnvs 中，任务配置文件以 ``.yaml`` 格式定义。而在 Isaac Lab 中，配置现在使用
专门的 Python 类 :class:`~isaaclab.utils.configclass` 来指定。 :class:`~isaaclab.utils.configclass`
模块在 Python 的 ``dataclasses`` 模块之上提供了一个封装。每个环境都应指定自己的配置
类，用 ``@configclass`` 注解并继承自 :class:`~envs.DirectRLEnvCfg` ，其中可以包含仿真
参数、环境场景参数、机器人参数和任务特定参数。

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

在 Isaac Lab 中， ``substeps`` 的用法已被
仿真 ``dt`` 和 ``decimation`` 参数的组合所取代。例如，在 IsaacGymEnvs 中，
``dt=1/60`` 和 ``substeps=2`` 等价于以 ``dt=1/120`` 执行 2 个仿真步，但任务步以
``1/60`` 秒运行。 ``decimation`` 参数是一个任务参数，控制每个任务（或 RL）步执行的仿真步数，
取代了 IsaacGymEnvs 中的 ``controlFrequencyInv`` 参数。
因此，相同的设置在 Isaac Lab 中将变为 ``dt=1/120`` 和 ``decimation=2`` 。

在 Isaac Sim 中， ``num_position_iterations`` 、 ``num_velocity_iterations`` 、
``contact_offset`` 、 ``rest_offset`` 、 ``bounce_threshold_velocity`` 、 ``max_depenetration_velocity`` 等 physx 仿真参数都可以
按 actor 单独指定。这些参数已从 physx 仿真配置
移至每个单独的关节体（articulation）和刚体配置中。

在 GPU 上运行仿真时，PhysX 中的缓冲区需要预先分配，用于计算和存储
接触、碰撞和聚合对等信息。这些缓冲区可能需要根据
环境的复杂程度、预期的接触和碰撞数量以及
环境中的 actor 数量进行调整。 :class:`~isaaclab.sim.PhysxCfg` 类提供了
设置 GPU 缓冲区维度的途径。

+--------------------------------------------------------------+-------------------------------------------------------------------+
|                                                              |                                                                   |
|.. code-block:: yaml                                          |.. code-block:: python                                             |
|                                                              |                                                                   |
|  # IsaacGymEnvs                                              | # IsaacLab                                                        |
|  sim:                                                        | sim: SimulationCfg = SimulationCfg(                               |
|                                                              |    device = "cuda:0" # can be "cpu", "cuda", "cuda:<device_id>"   |
|    dt: 0.0166 # 1/60 s                                       |    dt=1 / 120,                                                    |
|    substeps: 2                                               |    # decimation will be set in the task config                    |
|    up_axis: "z"                                              |    # up axis will always be Z in isaac sim                        |
|    use_gpu_pipeline: ${eq:${...pipeline},"gpu"}              |    # use_gpu_pipeline is deduced from the device                  |
|    gravity: [0.0, 0.0, -9.81]                                |    gravity=(0.0, 0.0, -9.81),                                     |
|    physx:                                                    |    physx: PhysxCfg = PhysxCfg(                                    |
|      num_threads: ${....num_threads}                         |        # num_threads is no longer needed                          |
|      solver_type: ${....solver_type}                         |        solver_type=1,                                             |
|      use_gpu: ${contains:"cuda",${....sim_device}}           |        # use_gpu is deduced from the device                       |
|      num_position_iterations: 4                              |        max_position_iteration_count=4,                            |
|      num_velocity_iterations: 0                              |        max_velocity_iteration_count=0,                            |
|      contact_offset: 0.02                                    |        # moved to actor config                                    |
|      rest_offset: 0.001                                      |        # moved to actor config                                    |
|      bounce_threshold_velocity: 0.2                          |        bounce_threshold_velocity=0.2,                             |
|      max_depenetration_velocity: 100.0                       |        # moved to actor config                                    |
|      default_buffer_size_multiplier: 2.0                     |        # default_buffer_size_multiplier is no longer needed       |
|      max_gpu_contact_pairs: 1048576 # 1024*1024              |        gpu_max_rigid_contact_count=2**23                          |
|      num_subscenes: ${....num_subscenes}                     |        # num_subscenes is no longer needed                        |
|      contact_collection: 0                                   |        # contact_collection is no longer needed                   |
|                                                              | ))                                                                |
+--------------------------------------------------------------+-------------------------------------------------------------------+

场景配置
------------

:class:`~isaaclab.scene.InteractiveSceneCfg` 类可用于指定与场景相关的参数，
例如环境数量和环境之间的间距。每个任务配置必须定义一个名为
``scene`` 的变量，其类型为 :class:`~isaaclab.scene.InteractiveSceneCfg` 。

+--------------------------------------------------------------+-------------------------------------------------------------------+
|                                                              |                                                                   |
|.. code-block:: yaml                                          |.. code-block:: python                                             |
|                                                              |                                                                   |
|  # IsaacGymEnvs                                              | # IsaacLab                                                        |
|  env:                                                        | scene: InteractiveSceneCfg = InteractiveSceneCfg(                 |
|    numEnvs: ${resolve_default:512,${...num_envs}}            |    num_envs=512,                                                  |
|    envSpacing: 4.0                                           |    env_spacing=4.0)                                               |
+--------------------------------------------------------------+-------------------------------------------------------------------+

任务配置
-----------

每个环境应指定自己的配置类，其中保存任务特定参数，例如观测和动作缓冲区的维度。奖励项缩放参数也可以在配置类中指定。

每个环境配置必须设置以下参数：

.. code-block:: python

   decimation = 2
   episode_length_s = 5.0
   action_space = 1
   observation_space = 4
   state_space = 0

请注意，最大回合长度参数（现在为 ``episode_length_s``）以秒为单位，而不是像
IsaacGymEnvs 中那样以步数为单位。要在步数和秒之间转换，请使用以下等式：
``episode_length_s = dt * decimation * num_steps``


RL 配置设置
~~~~~~~~~~~~~~~

rl_games 库的 RL 配置文件在 Isaac Lab 中仍可以 ``.yaml`` 文件的形式定义。
配置文件的大部分内容可以直接从 IsaacGymEnvs 复制。
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
|  # IsaacGymEnvs          | # IsaacLab                 |
|  env:                    | params:                    |
|    clipObservations: 5.0 |   env:                     |
|    clipActions: 1.0      |     clip_observations: 5.0 |
|                          |     clip_actions: 1.0      |
+--------------------------+----------------------------+

环境创建
~~~~~~~~~~~~~~~~~~~~

在 IsaacGymEnvs 中，环境创建通常包括四个部分：使用 ``create_sim()`` 创建 sim 对象、
创建地平面、从 MJCF 或 URDF 文件导入资产，最后通过遍历每个环境并将 actor 添加到环境中来创建环境。

Isaac Lab 不再需要调用 ``create_sim()`` 方法来获取 sim 对象，仿真
上下文由框架自动获取。仿真 API 也不再需要将 ``sim`` 作为
参数传入。

作为 ``create_sim()`` 的替代，任务可以在 Isaac Lab 中实现 ``_setup_scene()`` 方法。
该方法可用于向场景中添加 actor、添加地平面、克隆 actor，以及
向场景中添加任何其他可选对象（例如灯光）。

+------------------------------------------------------------------------------+------------------------------------------------------------------------+
| IsaacGymEnvs                                                                 | Isaac Lab                                                              |
+------------------------------------------------------------------------------+------------------------------------------------------------------------+
|.. code-block:: python                                                        |.. code-block:: python                                                  |
|                                                                              |                                                                        |
|   def create_sim(self):                                                      |   def _setup_scene(self):                                              |
|     # set the up axis to be z-up                                             |     self.cartpole = Articulation(self.cfg.robot_cfg)                   |
|     self.up_axis = self.cfg["sim"]["up_axis"]                                |     # add ground plane                                                 |
|                                                                              |     spawn_ground_plane(prim_path="/World/ground", cfg=GroundPlaneCfg() |
|     self.sim = super().create_sim(self.device_id, self.graphics_device_id,   |     # clone, filter, and replicate                                     |
|                                     self.physics_engine, self.sim_params)    |     self.scene.clone_environments(copy_from_source=False)              |
|     self._create_ground_plane()                                              |     self.scene.filter_collisions(global_prim_paths=[])                 |
|     self._create_envs(self.num_envs, self.cfg["env"]['envSpacing'],          |     # add articulation to scene                                        |
|                         int(np.sqrt(self.num_envs)))                         |     self.scene.articulations["cartpole"] = self.cartpole               |
|                                                                              |     # add lights                                                       |
|                                                                              |     light_cfg = sim_utils.DomeLightCfg(intensity=2000.0)               |
|                                                                              |     light_cfg.func("/World/Light", light_cfg)                          |
+------------------------------------------------------------------------------+------------------------------------------------------------------------+


地平面
------------

在 Isaac Lab 中，环境创建过程的大部分已通过 :class:`~isaaclab.utils.configclass` 模块简化为配置。

地平面可以使用 :class:`~terrains.TerrainImporterCfg` 类来定义。

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

Isaac Lab 和 Isaac Sim 都使用 `USD (Universal Scene Description) <https://github.com/PixarAnimationStudios/OpenUSD>`_
库来描述场景。以 MJCF 和 URDF 格式定义的资产可以使用
`Importing a New Asset <../how-to/import_new_asset.html>`_ 教程中描述的导入
工具导入到 USD。

每个关节体和刚体 actor 也可以有自己的配置类。
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
               effort_limit=400.0,
               velocity_limit=100.0,
               stiffness=0.0,
               damping=10.0,
           ),
           "pole_actuator": ImplicitActuatorCfg(
               joint_names_expr=["cart_to_pole"], effort_limit=400.0, velocity_limit=100.0, stiffness=0.0, damping=0.0
           ),
       },
   )

在 :class:`~assets.ArticulationCfg` 中， ``spawn`` 属性可通过
指定机器人文件的路径将机器人添加到场景中。此外， :class:`~isaaclab.sim.schemas.RigidBodyPropertiesCfg` 可
用于指定关节体中刚体的仿真属性。
类似地， :class:`~isaaclab.sim.schemas.ArticulationRootPropertiesCfg` 类可用于指定
关节体的仿真属性。关节属性现在作为 ``actuators``
字典的一部分，使用 :class:`~actuators.ImplicitActuatorCfg` 来指定。具有相同属性的关节可以组合成
正则表达式，或以名称或表达式列表的形式提供。

只需调用 ``self.cartpole = Articulation(self.cfg.robot_cfg)`` 即可将 actor 添加到场景中，
其中 ``self.cfg.robot_cfg`` 是一个 :class:`~assets.ArticulationCfg` 对象。初始化后，还应
通过调用 ``self.scene.articulations["cartpole"] = self.cartpole`` 将它们
添加到 :class:`~scene.InteractiveScene` 中，
以便 :class:`~scene.InteractiveScene` 能够遍历场景中的 actor，用于向
仿真写入数值和重置。

Actor 的仿真参数
""""""""""""""""""""""""""""""""

与刚体和关节体相关的一些仿真参数，其默认值在 Isaac Gym Preview Release 和 Isaac Sim 之间可能不同。
最好仔细检查 USD 资产，确保默认值
适用于该资产。

例如， ``RigidBodyAPI`` 中的以下参数在
Isaac Gym Preview Release 和 Isaac Sim 之间可能不同：

.. list-table::
   :widths: 50 50 50
   :header-rows: 1

   * - RigidBodyAPI 参数
     - Isaac Sim 中的默认值
     - Isaac Gym Preview Release 中的默认值
   * - 线性阻尼
     - 0.00
     - 0.00
   * - 角阻尼
     - 0.05
     - 0.0
   * - 最大线速度
     - inf
     - 1000
   * - 最大角速度
     - 5729.58008 (degree/s)
     - 64.0 (rad/s)
   * - 最大接触冲量
     - inf
     - 1e32

``JointAPI`` 和 ``DriveAPI`` 的关节体参数也可能有所不同。请注意，
Isaac Sim UI 假定角度单位为度。特别值得
注意的是， ``DriveAPI`` 中的 ``Damping`` 和 ``Stiffness`` 参数的单位
在 Isaac Sim UI 中为 ``1/deg`` ，而在 Isaac Gym Preview Release 中为 ``1/rad`` 。

.. list-table::
   :widths: 50 50 50
   :header-rows: 1

   * - 关节参数
     - Isaac Sim 中的默认值
     - Isaac Gym Preview Release 中的默认值
   * - 最大关节速度
     - 1000000.0 (deg)
     - 100.0 (rad)


有关在 Isaac Gym 和 Isaac Lab 之间进行彻底仿真比较的更多详细信息，
请参阅 :ref:`migrating-from-isaacgymenvs-comparing-simulation` 章节。


Cloner
------

Isaac Sim 引入了 ``Cloner`` 的概念，这是一个专为场景创建过程中的复制而设计的类。
在 IsaacGymEnvs 中，场景必须通过遍历环境数量来创建。
在每次迭代中，将 actor 添加到每个环境中，并且必须缓存它们的句柄。
Isaac Lab 通过使用 ``Cloner`` API 消除了遍历环境的需要。
场景创建过程如下：

#. 构建单个环境（即环境数量为 1 时场景的样子）
#. 调用 ``clone_environments()`` 复制该单个环境
#. 调用 ``filter_collisions()`` 过滤环境之间的碰撞（如果需要）


.. code-block:: python

   # construct a single environment with the Cartpole robot
   self.cartpole = Articulation(self.cfg.robot_cfg)
   # clone the environment
   self.scene.clone_environments(copy_from_source=False)
   # filter collisions
   self.scene.filter_collisions(global_prim_paths=[self.cfg.terrain.prim_path])


从仿真中访问状态
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在 Isaac Lab 中，访问物理状态的 API 需要创建 :class:`~assets.Articulation` 或 :class:`~assets.RigidObject`
对象。可以按照上一节所述，通过定义
相应的 :class:`~assets.ArticulationCfg` 或 :class:`~assets.RigidObjectCfg` 配置，为场景中不同的关节体或刚体初始化多个对象。
这种方法无需再获取刚体句柄来切片场景中特定刚体的状态。


.. code-block:: python

   self._robot = Articulation(self.cfg.robot)
   self._cabinet = Articulation(self.cfg.cabinet)
   self._object = RigidObject(self.cfg.object_cfg)


我们在 Isaac Lab 中还移除了 ``acquire`` 和 ``refresh`` API。物理状态可以使用为关节体和刚体对象定义的 API 直接应用或获取。

Isaac Lab 提供的 API 不再需要显式地封装和解封装底层缓冲区。
API 现在可以直接使用张量来读取和写入数据。

+------------------------------------------------------------------+-----------------------------------------------------------------+
| IsaacGymEnvs                                                     | Isaac Lab                                                       |
+------------------------------------------------------------------+-----------------------------------------------------------------+
|.. code-block:: python                                            |.. code-block:: python                                           |
|                                                                  |                                                                 |
|   dof_state_tensor = self.gym.acquire_dof_state_tensor(self.sim) |   self.joint_pos = self._robot.data.joint_pos                   |
|   self.dof_state = gymtorch.wrap_tensor(dof_state_tensor)        |   self.joint_vel = self._robot.data.joint_vel                   |
|   self.gym.refresh_dof_state_tensor(self.sim)                    |                                                                 |
+------------------------------------------------------------------+-----------------------------------------------------------------+

请注意 Isaac Gym Preview Release 与 Isaac Lab 的 API 之间的一些命名差异。大多数与 ``dof`` 相关的 API 在 Isaac Lab 中被
命名为 ``joint`` 。
Isaac Lab 的 API 也不再使用显式的 ``_tensors`` 或 ``_tensor_indexed`` 后缀命名。
API 的索引版本现在通过可选的 ``indices`` 参数隐式实现。

Isaac Lab 中的大多数 API 还提供
了指定 ``indices`` 参数的选项，在读取或写入部分
环境的数据时可以使用该参数。请注意，使用 ``indices`` 参数设置状态时，状态缓冲区的形状
应与 ``indices`` 列表的维度匹配。

+---------------------------------------------------------------------------+---------------------------------------------------------------+
| IsaacGymEnvs                                                              | Isaac Lab                                                     |
+---------------------------------------------------------------------------+---------------------------------------------------------------+
|.. code-block:: python                                                     |.. code-block:: python                                         |
|                                                                           |                                                               |
|   env_ids_int32 = env_ids.to(dtype=torch.int32)                           |   self._robot.write_joint_state_to_sim(joint_pos, joint_vel,  |
|   self.gym.set_dof_state_tensor_indexed(self.sim,                         |                                    joint_ids, env_ids)        |
|       gymtorch.unwrap_tensor(self.dof_state),                             |                                                               |
|       gymtorch.unwrap_tensor(env_ids_int32), len(env_ids_int32))          |                                                               |
+---------------------------------------------------------------------------+---------------------------------------------------------------+

四元数约定
---------------------

Isaac Lab 和 Isaac Sim 都采用 ``wxyz`` 作为四元数约定。然而，Isaac Gym Preview Release 中使用的四元数
约定是 ``xyzw`` 。
在处理旋转数据索引时，请记得将所有四元数切换为使用 ``xyzw`` 约定。
同样，在将四元数传递给 Isaac Lab API 之前，请确保它们都采用 ``wxyz`` 格式。


关节体关节顺序
------------------------

Isaac Sim 和 Isaac Lab 的物理仿真假定给定运动学树中的关节采用广度优先
排序。
然而，Isaac Gym Preview Release 假定运动学树中的关节采用深度优先排序。
这意味着基于排序对关节进行索引在 IsaacGymEnvs 和 Isaac Lab 中可能不同。

在 Isaac Lab 中，可以通过 ``Articulation.data.joint_names`` 获取关节名称列表，它
也对应于关节体中关节的排序。


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
* ``my_environment/agents`` 是包含该任务所有 RL 配置文件的目录。Isaac Lab 支持多个 RL 库，每个库可以有自己的单独配置文件。
* ``my_environment/__init__.py`` 是向 Gymnasium 接口注册环境的主文件。这使得训练和推理脚本能够按名称查找任务。该文件的内容应如下：

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

* ``my_environment/my_env.py`` 是实现该环境任务逻辑和任务配置类的主 Python 脚本。


任务逻辑
~~~~~~~~~~

在 Isaac Lab 中， ``post_physics_step`` 函数已被移至基类中的框架内。
任务不需要实现该方法，但如果需要不同的工作流，可以选择覆盖它。

默认情况下，Isaac Lab 遵循以下逻辑流程：

+----------------------------------+----------------------------------+
| IsaacGymEnvs                     | Isaac Lab                        |
+----------------------------------+----------------------------------+
|.. code-block:: none              |.. code-block:: none              |
|                                  |                                  |
|   pre_physics_step               |   pre_physics_step               |
|     |-- apply_action             |     |-- _pre_physics_step(action)|
|                                  |     |-- _apply_action()          |
|                                  |                                  |
|   post_physics_step              |   post_physics_step              |
|     |-- reset_idx()              |     |-- _get_dones()             |
|     |-- compute_observation()    |     |-- _get_rewards()           |
|     |-- compute_reward()         |     |-- _reset_idx()             |
|                                  |     |-- _get_observations()      |
+----------------------------------+----------------------------------+

在 Isaac Lab 中，我们还将用于处理策略动作的 ``pre_physics_step`` API 与
将动作设置到仿真中的 ``apply_action`` API 分开。这在使用 ``decimation`` 时为控制
动作何时写入仿真提供了更大的灵活性。
``pre_physics_step`` 会在每步仿真之前调用一次。
``apply_actions`` 在每个 RL 步中被调用 ``decimation`` 次，在每次仿真步调用之前各调用一次。

采用这种方法后，重置将基于当前步的动作而不是上一步的动作执行。
观测也将在重置后使用正确的状态进行计算。

我们还对一些 API 进行了重命名：

* ``create_sim(self)`` --> ``_setup_scene(self)``
* ``pre_physics_step(self, actions)`` --> ``_pre_physics_step(self, actions)`` 和 ``_apply_action(self)``
* ``reset_idx(self, env_ids)`` --> ``_reset_idx(self, env_ids)``
* ``compute_observations(self)`` --> ``_get_observations(self)`` - ``_get_observations()`` 现在应返回字典 ``{"policy": obs}``
* ``compute_reward(self)`` --> ``_get_rewards(self)`` - ``_get_rewards()`` 现在应返回奖励缓冲区
* ``post_physics_step(self)`` --> 已移至基类
* 此外，Isaac Lab 要求实现 ``_is_done(self)``，它应返回两个缓冲区： ``reset`` 缓冲区和 ``time_out`` 缓冲区。


整合所有内容
~~~~~~~~~~~~~~~~~~~~~~~

这里完整展示了 Cartpole 环境，以充分展示 IsaacGymEnvs 实现与 Isaac Lab 实现之间的比较。

任务配置
-----------

+--------------------------------------------------------+---------------------------------------------------------------------+
| IsaacGymEnvs                                           | Isaac Lab                                                           |
+--------------------------------------------------------+---------------------------------------------------------------------+
|.. code-block:: yaml                                    |.. code-block:: python                                               |
|                                                        |                                                                     |
| # used to create the object                            | @configclass                                                        |
| name: Cartpole                                         | class CartpoleEnvCfg(DirectRLEnvCfg):                               |
|                                                        |                                                                     |
| physics_engine: ${..physics_engine}                    |     # simulation                                                    |
|                                                        |     sim: SimulationCfg = SimulationCfg(dt=1 / 120)                  |
| # if given, will override the device setting in gym.   |     # robot                                                         |
| env:                                                   |     robot_cfg: ArticulationCfg = CARTPOLE_CFG.replace(              |
|   numEnvs: ${resolve_default:512,${...num_envs}}       |         prim_path="/World/envs/env_.*/Robot")                       |
|   envSpacing: 4.0                                      |     cart_dof_name = "slider_to_cart"                                |
|   resetDist: 3.0                                       |     pole_dof_name = "cart_to_pole"                                  |
|   maxEffort: 400.0                                     |     # scene                                                         |
|                                                        |     scene: InteractiveSceneCfg = InteractiveSceneCfg(               |
|   clipObservations: 5.0                                |         num_envs=4096, env_spacing=4.0, replicate_physics=True)     |
|   clipActions: 1.0                                     |     # env                                                           |
|                                                        |     decimation = 2                                                  |
|   asset:                                               |     episode_length_s = 5.0                                          |
|     assetRoot: "../../assets"                          |     action_scale = 100.0  # [N]                                     |
|     assetFileName: "urdf/cartpole.urdf"                |     action_space = 1                                                |
|                                                        |     observation_space = 4                                           |
|   enableCameraSensors: False                           |     state_space = 0                                                 |
|                                                        |     # reset                                                         |
| sim:                                                   |     max_cart_pos = 3.0                                              |
|   dt: 0.0166 # 1/60 s                                  |     initial_pole_angle_range = [-0.25, 0.25]                        |
|   substeps: 2                                          |     # reward scales                                                 |
|   up_axis: "z"                                         |     rew_scale_alive = 1.0                                           |
|   use_gpu_pipeline: ${eq:${...pipeline},"gpu"}         |     rew_scale_terminated = -2.0                                     |
|   gravity: [0.0, 0.0, -9.81]                           |     rew_scale_pole_pos = -1.0                                       |
|   physx:                                               |     rew_scale_cart_vel = -0.01                                      |
|     num_threads: ${....num_threads}                    |     rew_scale_pole_vel = -0.005                                     |
|     solver_type: ${....solver_type}                    |                                                                     |
|     use_gpu: ${contains:"cuda",${....sim_device}}      |                                                                     |
|     num_position_iterations: 4                         |                                                                     |
|     num_velocity_iterations: 0                         |                                                                     |
|     contact_offset: 0.02                               |                                                                     |
|     rest_offset: 0.001                                 |                                                                     |
|     bounce_threshold_velocity: 0.2                     |                                                                     |
|     max_depenetration_velocity: 100.0                  |                                                                     |
|     default_buffer_size_multiplier: 2.0                |                                                                     |
|     max_gpu_contact_pairs: 1048576 # 1024*1024         |                                                                     |
|     num_subscenes: ${....num_subscenes}                |                                                                     |
|     contact_collection: 0                              |                                                                     |
+--------------------------------------------------------+---------------------------------------------------------------------+



任务设置
----------

Isaac Lab 不再需要通过 IsaacGymEnvs 中使用的 ``acquire_*`` API 预初始化缓冲区。
也不再需要 ``wrap`` 和 ``unwrap`` 张量。

+-------------------------------------------------------------------------+-------------------------------------------------------------+
| IsaacGymEnvs                                                            | Isaac Lab                                                   |
+-------------------------------------------------------------------------+-------------------------------------------------------------+
|.. code-block:: python                                                   |.. code-block:: python                                       |
|                                                                         |                                                             |
|   class Cartpole(VecTask):                                              |   class CartpoleEnv(DirectRLEnv):                           |
|                                                                         |     cfg: CartpoleEnvCfg                                     |
|     def __init__(self, cfg, rl_device, sim_device, graphics_device_id,  |     def __init__(self, cfg: CartpoleEnvCfg,                 |
|      headless, virtual_screen_capture, force_render):                   |             render_mode: str | None = None, **kwargs):      |
|         self.cfg = cfg                                                  |                                                             |
|                                                                         |         super().__init__(cfg, render_mode, **kwargs)        |
|         self.reset_dist = self.cfg["env"]["resetDist"]                  |                                                             |
|                                                                         |         self._cart_dof_idx, _ = self.cartpole.find_joints(  |
|         self.max_push_effort = self.cfg["env"]["maxEffort"]             |             self.cfg.cart_dof_name)                         |
|         self.max_episode_length = 500                                   |         self._pole_dof_idx, _ = self.cartpole.find_joints(  |
|                                                                         |             self.cfg.pole_dof_name)                         |
|         self.cfg["env"]["numObservations"] = 4                          |         self.action_scale = self.cfg.action_scale           |
|         self.cfg["env"]["numActions"] = 1                               |                                                             |
|                                                                         |         self.joint_pos = self.cartpole.data.joint_pos       |
|         super().__init__(config=self.cfg,                               |         self.joint_vel = self.cartpole.data.joint_vel       |
|            rl_device=rl_device, sim_device=sim_device,                  |                                                             |
|            graphics_device_id=graphics_device_id, headless=headless,    |                                                             |
|            virtual_screen_capture=virtual_screen_capture,               |                                                             |
|            force_render=force_render)                                   |                                                             |
|                                                                         |                                                             |
|         dof_state_tensor = self.gym.acquire_dof_state_tensor(self.sim)  |                                                             |
|         self.dof_state = gymtorch.wrap_tensor(dof_state_tensor)         |                                                             |
|         self.dof_pos = self.dof_state.view(                             |                                                             |
|             self.num_envs, self.num_dof, 2)[..., 0]                     |                                                             |
|         self.dof_vel = self.dof_state.view(                             |                                                             |
|             self.num_envs, self.num_dof, 2)[..., 1]                     |                                                             |
+-------------------------------------------------------------------------+-------------------------------------------------------------+



场景设置
-----------

场景设置现在通过 ``Cloner`` API 以及在配置对象中指定 actor 属性来完成。
这消除了遍历环境数量来设置环境的需要，也避免
了在任务实现中为 actor 设置仿真参数。

+------------------------------------------------------------------------+---------------------------------------------------------------------+
| IsaacGymEnvs                                                           | Isaac Lab                                                           |
+------------------------------------------------------------------------+---------------------------------------------------------------------+
|.. code-block:: python                                                  |.. code-block:: python                                               |
|                                                                        |                                                                     |
| def create_sim(self):                                                  | def _setup_scene(self):                                             |
|     # set the up axis to be z-up given that assets are y-up by default |     self.cartpole = Articulation(self.cfg.robot_cfg)                |
|     self.up_axis = self.cfg["sim"]["up_axis"]                          |     # add ground plane                                              |
|                                                                        |     spawn_ground_plane(prim_path="/World/ground",                   |
|     self.sim = super().create_sim(self.device_id,                      |         cfg=GroundPlaneCfg())                                       |
|         self.graphics_device_id, self.physics_engine,                  |     # clone, filter, and replicate                                  |
|         self.sim_params)                                               |     self.scene.clone_environments(                                  |
|     self._create_ground_plane()                                        |         copy_from_source=False)                                     |
|     self._create_envs(self.num_envs,                                   |     self.scene.filter_collisions(                                   |
|         self.cfg["env"]['envSpacing'],                                 |         global_prim_paths=[])                                       |
|         int(np.sqrt(self.num_envs)))                                   |     # add articulation to scene                                     |
|                                                                        |     self.scene.articulations["cartpole"] = self.cartpole            |
| def _create_ground_plane(self):                                        |     # add lights                                                    |
|     plane_params = gymapi.PlaneParams()                                |     light_cfg = sim_utils.DomeLightCfg(                             |
|     # set the normal force to be z dimension                           |         intensity=2000.0, color=(0.75, 0.75, 0.75))                 |
|     plane_params.normal = (gymapi.Vec3(0.0, 0.0, 1.0)                  |     light_cfg.func("/World/Light", light_cfg)                       |
|         if self.up_axis == 'z'                                         |                                                                     |
|         else gymapi.Vec3(0.0, 1.0, 0.0))                               | CARTPOLE_CFG = ArticulationCfg(                                     |
|     self.gym.add_ground(self.sim, plane_params)                        |     spawn=sim_utils.UsdFileCfg(                                     |
|                                                                        |         usd_path=f"{ISAACLAB_NUCLEUS_DIR}/.../cartpole.usd",        |
| def _create_envs(self, num_envs, spacing, num_per_row):                |         rigid_props=sim_utils.RigidBodyPropertiesCfg(               |
|     # define plane on which environments are initialized               |             rigid_body_enabled=True,                                |
|     lower = (gymapi.Vec3(0.5 * -spacing, -spacing, 0.0)                |             max_linear_velocity=1000.0,                             |
|         if self.up_axis == 'z'                                         |             max_angular_velocity=1000.0,                            |
|         else gymapi.Vec3(0.5 * -spacing, 0.0, -spacing))               |             max_depenetration_velocity=100.0,                       |
|     upper = gymapi.Vec3(0.5 * spacing, spacing, spacing)               |             enable_gyroscopic_forces=True,                          |
|                                                                        |         ),                                                          |
|     asset_root = os.path.join(os.path.dirname(                         |         articulation_props=sim_utils.ArticulationRootPropertiesCfg( |
|         os.path.abspath(__file__)), "../../assets")                    |             enabled_self_collisions=False,                          |
|     asset_file = "urdf/cartpole.urdf"                                  |             solver_position_iteration_count=4,                      |
|                                                                        |             solver_velocity_iteration_count=0,                      |
|     if "asset" in self.cfg["env"]:                                     |             sleep_threshold=0.005,                                  |
|         asset_root = os.path.join(os.path.dirname(                     |             stabilization_threshold=0.001,                          |
|             os.path.abspath(__file__)),                                |         ),                                                          |
|             self.cfg["env"]["asset"].get("assetRoot", asset_root))     |     ),                                                              |
|         asset_file = self.cfg["env"]["asset"].get(                     |     init_state=ArticulationCfg.InitialStateCfg(                     |
|             "assetFileName", asset_file)                               |         pos=(0.0, 0.0, 2.0),                                        |
|                                                                        |         joint_pos={"slider_to_cart": 0.0, "cart_to_pole": 0.0}      |
|     asset_path = os.path.join(asset_root, asset_file)                  |     ),                                                              |
|     asset_root = os.path.dirname(asset_path)                           |     actuators={                                                     |
|     asset_file = os.path.basename(asset_path)                          |         "cart_actuator": ImplicitActuatorCfg(                       |
|                                                                        |             joint_names_expr=["slider_to_cart"],                    |
|     asset_options = gymapi.AssetOptions()                              |             effort_limit_sim=400.0,                                 |
|     asset_options.fix_base_link = True                                 |             velocity_limit_sim=100.0,                               |
|     cartpole_asset = self.gym.load_asset(self.sim,                     |             stiffness=0.0,                                          |
|         asset_root, asset_file, asset_options)                         |             damping=10.0,                                           |
|     self.num_dof = self.gym.get_asset_dof_count(                       |         ),                                                          |
|         cartpole_asset)                                                |         "pole_actuator": ImplicitActuatorCfg(                       |
|                                                                        |             joint_names_expr=["cart_to_pole"],                      |
|     pose = gymapi.Transform()                                          |             effort_limit_sim=400.0, velocity_limit_sim=100.0,       |
|     if self.up_axis == 'z':                                            |             stiffness=0.0, damping=0.0                              |
|         pose.p.z = 2.0                                                 |         ),                                                          |
|         pose.r = gymapi.Quat(0.0, 0.0, 0.0, 1.0)                       |     },                                                              |
|     else:                                                              | )                                                                   |
|         pose.p.y = 2.0                                                 |                                                                     |
|         pose.r = gymapi.Quat(                                          |                                                                     |
|             -np.sqrt(2)/2, 0.0, 0.0, np.sqrt(2)/2)                     |                                                                     |
|                                                                        |                                                                     |
|     self.cartpole_handles = []                                         |                                                                     |
|     self.envs = []                                                     |                                                                     |
|     for i in range(self.num_envs):                                     |                                                                     |
|         # create env instance                                          |                                                                     |
|         env_ptr = self.gym.create_env(                                 |                                                                     |
|             self.sim, lower, upper, num_per_row                        |                                                                     |
|         )                                                              |                                                                     |
|         cartpole_handle = self.gym.create_actor(                       |                                                                     |
|             env_ptr, cartpole_asset, pose,                             |                                                                     |
|             "cartpole", i, 1, 0)                                       |                                                                     |
|                                                                        |                                                                     |
|         dof_props = self.gym.get_actor_dof_properties(                 |                                                                     |
|             env_ptr, cartpole_handle)                                  |                                                                     |
|         dof_props['driveMode'][0] = gymapi.DOF_MODE_EFFORT             |                                                                     |
|         dof_props['driveMode'][1] = gymapi.DOF_MODE_NONE               |                                                                     |
|         dof_props['stiffness'][:] = 0.0                                |                                                                     |
|         dof_props['damping'][:] = 0.0                                  |                                                                     |
|         self.gym.set_actor_dof_properties(env_ptr, c                   |                                                                     |
|             artpole_handle, dof_props)                                 |                                                                     |
|                                                                        |                                                                     |
|         self.envs.append(env_ptr)                                      |                                                                     |
|         self.cartpole_handles.append(cartpole_handle)                  |                                                                     |
+------------------------------------------------------------------------+---------------------------------------------------------------------+


物理步前与步后处理
-------------------------

在 IsaacGymEnvs 中，由于 GPU API 的限制，当环境需要执行重置时，观测中会有过时的数据。
这一限制在 Isaac Lab 中已被消除，因此任务遵循正确的工作流：应用动作、步进仿真、
收集状态、计算 done、计算奖励、执行重置，最后计算观测。
此工作流由框架自动完成，因此任务中不需要 ``post_physics_step`` API。
不过，单个任务可以覆盖 ``step()`` API 来控制该工作流。

+------------------------------------------------------------------+-------------------------------------------------------------+
| IsaacGymEnvs                                                     | IsaacLab                                                    |
+------------------------------------------------------------------+-------------------------------------------------------------+
|.. code-block:: python                                            |.. code-block:: python                                       |
|                                                                  |                                                             |
| def pre_physics_step(self, actions):                             | def _pre_physics_step(self, actions: torch.Tensor) -> None: |
|     actions_tensor = torch.zeros(                                |     self.actions = self.action_scale * actions              |
|         self.num_envs * self.num_dof,                            |                                                             |
|         device=self.device, dtype=torch.float)                   | def _apply_action(self) -> None:                            |
|     actions_tensor[::self.num_dof] = actions.to(                 |     self.cartpole.set_joint_effort_target(                  |
|         self.device).squeeze() * self.max_push_effort            |          self.actions, joint_ids=self._cart_dof_idx)        |
|     forces = gymtorch.unwrap_tensor(actions_tensor)              |                                                             |
|     self.gym.set_dof_actuation_force_tensor(                     |                                                             |
|         self.sim, forces)                                        |                                                             |
|                                                                  |                                                             |
| def post_physics_step(self):                                     |                                                             |
|     self.progress_buf += 1                                       |                                                             |
|                                                                  |                                                             |
|     env_ids = self.reset_buf.nonzero(                            |                                                             |
|         as_tuple=False).squeeze(-1)                              |                                                             |
|     if len(env_ids) > 0:                                         |                                                             |
|         self.reset_idx(env_ids)                                  |                                                             |
|                                                                  |                                                             |
|     self.compute_observations()                                  |                                                             |
|     self.compute_reward()                                        |                                                             |
+------------------------------------------------------------------+-------------------------------------------------------------+


Done 与重置
----------------

在 Isaac Lab 中， ``dones`` 在 ``_get_dones()`` 方法中计算，应返回两个变量： ``resets`` 和 ``time_out`` 。
``progress_buf`` 的跟踪已移至基类，现在由框架自动递增和重置。
``progress_buf`` 变量也被重命名为 ``episode_length_buf`` 。

+-----------------------------------------------------------------------+---------------------------------------------------------------------------+
| IsaacGymEnvs                                                          | Isaac Lab                                                                 |
+-----------------------------------------------------------------------+---------------------------------------------------------------------------+
|.. code-block:: python                                                 |.. code-block:: python                                                     |
|                                                                       |                                                                           |
| def reset_idx(self, env_ids):                                         | def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:                |
|     positions = 0.2 * (torch.rand((len(env_ids), self.num_dof),       |     self.joint_pos = self.cartpole.data.joint_pos                         |
|         device=self.device) - 0.5)                                    |     self.joint_vel = self.cartpole.data.joint_vel                         |
|     velocities = 0.5 * (torch.rand((len(env_ids), self.num_dof),      |                                                                           |
|         device=self.device) - 0.5)                                    |     time_out = self.episode_length_buf >= self.max_episode_length - 1     |
|                                                                       |     out_of_bounds = torch.any(torch.abs(                                  |
|     self.dof_pos[env_ids, :] = positions[:]                           |         self.joint_pos[:, self._cart_dof_idx]) > self.cfg.max_cart_pos,   |
|     self.dof_vel[env_ids, :] = velocities[:]                          |         dim=1)                                                            |
|                                                                       |     out_of_bounds = out_of_bounds | torch.any(                            |
|     env_ids_int32 = env_ids.to(dtype=torch.int32)                     |         torch.abs(self.joint_pos[:, self._pole_dof_idx]) > math.pi / 2,   |
|     self.gym.set_dof_state_tensor_indexed(self.sim,                   |         dim=1)                                                            |
|         gymtorch.unwrap_tensor(self.dof_state),                       |     return out_of_bounds, time_out                                        |
|         gymtorch.unwrap_tensor(env_ids_int32), len(env_ids_int32))    |                                                                           |
|     self.reset_buf[env_ids] = 0                                       | def _reset_idx(self, env_ids: Sequence[int] | None):                      |
|     self.progress_buf[env_ids] = 0                                    |     if env_ids is None:                                                   |
|                                                                       |         env_ids = self.cartpole._ALL_INDICES                              |
|                                                                       |     super()._reset_idx(env_ids)                                           |
|                                                                       |                                                                           |
|                                                                       |     joint_pos = self.cartpole.data.default_joint_pos[env_ids]             |
|                                                                       |     joint_pos[:, self._pole_dof_idx] += sample_uniform(                   |
|                                                                       |         self.cfg.initial_pole_angle_range[0] * math.pi,                   |
|                                                                       |         self.cfg.initial_pole_angle_range[1] * math.pi,                   |
|                                                                       |         joint_pos[:, self._pole_dof_idx].shape,                           |
|                                                                       |         joint_pos.device,                                                 |
|                                                                       |     )                                                                     |
|                                                                       |     joint_vel = self.cartpole.data.default_joint_vel[env_ids]             |
|                                                                       |                                                                           |
|                                                                       |     default_root_state = self.cartpole.data.default_root_state[env_ids]   |
|                                                                       |     default_root_state[:, :3] += self.scene.env_origins[env_ids]          |
|                                                                       |                                                                           |
|                                                                       |     self.joint_pos[env_ids] = joint_pos                                   |
|                                                                       |                                                                           |
|                                                                       |     self.cartpole.write_root_pose_to_sim(                                 |
|                                                                       |         default_root_state[:, :7], env_ids)                               |
|                                                                       |     self.cartpole.write_root_velocity_to_sim(                             |
|                                                                       |         default_root_state[:, 7:], env_ids)                               |
|                                                                       |     self.cartpole.write_joint_state_to_sim(                               |
|                                                                       |         joint_pos, joint_vel, None, env_ids)                              |
+-----------------------------------------------------------------------+---------------------------------------------------------------------------+


观测
------------

在 Isaac Lab 中， ``_get_observations()`` API 现在应返回一个字典，其中包含 ``policy`` 键，对应的值为观测
缓冲区。
对于非对称策略，字典还应包含一个保存状态缓冲区的 ``critic`` 键。

+--------------------------------------------------------------------------+---------------------------------------------------------------------------------------+
| IsaacGymEnvs                                                             | Isaac Lab                                                                             |
+--------------------------------------------------------------------------+---------------------------------------------------------------------------------------+
|.. code-block:: python                                                    |.. code-block:: python                                                                 |
|                                                                          |                                                                                       |
| def compute_observations(self, env_ids=None):                            | def _get_observations(self) -> dict:                                                  |
|     if env_ids is None:                                                  |     obs = torch.cat(                                                                  |
|         env_ids = np.arange(self.num_envs)                               |         (                                                                             |
|                                                                          |             self.joint_pos[:, self._pole_dof_idx[0]],                                 |
|     self.gym.refresh_dof_state_tensor(self.sim)                          |             self.joint_vel[:, self._pole_dof_idx[0]],                                 |
|                                                                          |             self.joint_pos[:, self._cart_dof_idx[0]],                                 |
|     self.obs_buf[env_ids, 0] = self.dof_pos[env_ids, 0]                  |             self.joint_vel[:, self._cart_dof_idx[0]],                                 |
|     self.obs_buf[env_ids, 1] = self.dof_vel[env_ids, 0]                  |         ),                                                                            |
|     self.obs_buf[env_ids, 2] = self.dof_pos[env_ids, 1]                  |         dim=-1,                                                                       |
|     self.obs_buf[env_ids, 3] = self.dof_vel[env_ids, 1]                  |     )                                                                                 |
|                                                                          |     observations = {"policy": obs}                                                    |
|     return self.obs_buf                                                  |     return observations                                                               |
+--------------------------------------------------------------------------+---------------------------------------------------------------------------------------+


奖励
-------

在 Isaac Lab 中，奖励方法 ``_get_rewards`` 应返回奖励缓冲区作为返回值。
与 IsaacGymEnvs 类似，奖励函数中的计算也可以通过添加 ``@torch.jit.script`` 注解来使用 pytorch jit
执行。

+--------------------------------------------------------------------------+----------------------------------------------------------------------------------------+
| IsaacGymEnvs                                                             | Isaac Lab                                                                              |
+--------------------------------------------------------------------------+----------------------------------------------------------------------------------------+
|.. code-block:: python                                                    |.. code-block:: python                                                                  |
|                                                                          |                                                                                        |
| def compute_reward(self):                                                | def _get_rewards(self) -> torch.Tensor:                                                |
|     # retrieve environment observations from buffer                      |     total_reward = compute_rewards(                                                    |
|     pole_angle = self.obs_buf[:, 2]                                      |         self.cfg.rew_scale_alive,                                                      |
|     pole_vel = self.obs_buf[:, 3]                                        |         self.cfg.rew_scale_terminated,                                                 |
|     cart_vel = self.obs_buf[:, 1]                                        |         self.cfg.rew_scale_pole_pos,                                                   |
|     cart_pos = self.obs_buf[:, 0]                                        |         self.cfg.rew_scale_cart_vel,                                                   |
|                                                                          |         self.cfg.rew_scale_pole_vel,                                                   |
|     self.rew_buf[:], self.reset_buf[:] = compute_cartpole_reward(        |         self.joint_pos[:, self._pole_dof_idx[0]],                                      |
|         pole_angle, pole_vel, cart_vel, cart_pos,                        |         self.joint_vel[:, self._pole_dof_idx[0]],                                      |
|         self.reset_dist, self.reset_buf,                                 |         self.joint_pos[:, self._cart_dof_idx[0]],                                      |
|         self.progress_buf, self.max_episode_length                       |         self.joint_vel[:, self._cart_dof_idx[0]],                                      |
|     )                                                                    |         self.reset_terminated,                                                         |
|                                                                          |     )                                                                                  |
| @torch.jit.script                                                        |     return total_reward                                                                |
| def compute_cartpole_reward(pole_angle, pole_vel,                        |                                                                                        |
|                             cart_vel, cart_pos,                          | @torch.jit.script                                                                      |
|                             reset_dist, reset_buf,                       | def compute_rewards(                                                                   |
|                             progress_buf, max_episode_length):           |     rew_scale_alive: float,                                                            |
|                                                                          |     rew_scale_terminated: float,                                                       |
|     reward = (1.0 - pole_angle * pole_angle -                            |     rew_scale_pole_pos: float,                                                         |
|         0.01 * torch.abs(cart_vel) -                                     |     rew_scale_cart_vel: float,                                                         |
|         0.005 * torch.abs(pole_vel))                                     |     rew_scale_pole_vel: float,                                                         |
|                                                                          |     pole_pos: torch.Tensor,                                                            |
|     # adjust reward for reset agents                                     |     pole_vel: torch.Tensor,                                                            |
|     reward = torch.where(torch.abs(cart_pos) > reset_dist,               |     cart_pos: torch.Tensor,                                                            |
|         torch.ones_like(reward) * -2.0, reward)                          |     cart_vel: torch.Tensor,                                                            |
|     reward = torch.where(torch.abs(pole_angle) > np.pi / 2,              |     reset_terminated: torch.Tensor,                                                    |
|         torch.ones_like(reward) * -2.0, reward)                          | ):                                                                                     |
|                                                                          |     rew_alive = rew_scale_alive * (1.0 - reset_terminated.float())                     |
|     reset = torch.where(torch.abs(cart_pos) > reset_dist,                |     rew_termination = rew_scale_terminated * reset_terminated.float()                  |
|         torch.ones_like(reset_buf), reset_buf)                           |     rew_pole_pos = rew_scale_pole_pos * torch.sum(                                     |
|     reset = torch.where(torch.abs(pole_angle) > np.pi / 2,               |         torch.square(pole_pos), dim=-1)                                                |
|         torch.ones_like(reset_buf), reset_buf)                           |     rew_cart_vel = rew_scale_cart_vel * torch.sum(                                     |
|     reset = torch.where(progress_buf >= max_episode_length - 1,          |         torch.abs(cart_vel), dim=-1)                                                   |
|         torch.ones_like(reset_buf), reset)                               |     rew_pole_vel = rew_scale_pole_vel * torch.sum(                                     |
|                                                                          |         torch.abs(pole_vel), dim=-1)                                                   |
|                                                                          |     total_reward = (rew_alive + rew_termination                                        |
|                                                                          |                      + rew_pole_pos + rew_cart_vel + rew_pole_vel)                     |
|                                                                          |     return total_reward                                                                |
+--------------------------------------------------------------------------+----------------------------------------------------------------------------------------+



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


附加资源
~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   comparing_simulation_isaacgym


.. _IsaacGymEnvs: https://github.com/isaac-sim/IsaacGymEnvs
.. _Isaac Gym Preview Release: https://developer.nvidia.com/isaac-gym
.. _release notes: https://github.com/isaac-sim/IsaacLab/releases
