代码教程（渐进式系列）
====================================

通过 ``examples/tutorial/`` 中的 8 个渐进式 Python 教程学习 ProtoMotions。

.. warning::

   **需要 GPU**：这些仿真器（IsaacGym、IsaacLab、Genesis、Newton）为 GPU 加速而设计。
   虽然提供了 ``--cpu-only`` 选项，但它**高度实验性**，不推荐在大多数场景下使用。

概述
--------

这些教程教你从零开始构建 ProtoMotions 系统。每个教程都是一个完整、可运行的
Python 脚本，并在此前介绍的概念之上逐步递进。

**使用方法**：

1. 阅读下方的教程文档
2. 运行对应的 Python 文件
3. 阅读代码以理解实现
4. 动手修改、做实验

**前置条件**：已安装 ProtoMotions 以及某个仿真器（isaacgym、isaaclab、genesis 或 newton）

教程 0：创建仿真器
-----------------------------

.. raw:: html

   <video width="100%" controls>
     <source src="../_static/tutorial_0.mp4" type="video/mp4">
     Your browser does not support the video tag.
   </video>

**文件**：``examples/tutorial/0_create_simulator.py``

学习 ProtoMotions 的基础 —— 创建一个加载 G1 机器人的物理仿真器。

**你将学到**：

* 在导入 torch 之前先导入仿真器（IsaacGym/IsaacLab 的必需要求）
* 针对每个后端配置机器人及其仿真参数
* 创建地形和仿真器实例
* 用随机动作运行一个基本的仿真循环

**运行方式**：

.. code-block:: bash

   python examples/tutorial/0_create_simulator.py --simulator isaacgym

**代码要点**：

.. code-block:: python

   # Robot configuration with per-simulator params
   robot_cfg = RobotConfig(
       semantic_forward_axis_xy=(1.0, 0.0),
       asset=RobotAssetConfig(asset_file_name="mjcf/g1_bm.xml", ...),
       simulation_params=SimulatorParams(
           isaacgym=IsaacGymSimParams(fps=100, decimation=2, substeps=2),
           isaaclab=IsaacLabSimParams(fps=200, decimation=4),
           ...
       ),
   )
   
   # Create simulator via factory
   simulator_cfg = simulator_config(args.simulator, robot_cfg, headless=False, num_envs=4)
   SimulatorClass = get_class(simulator_cfg._target_)
   simulator = SimulatorClass(config=simulator_cfg, robot_config=robot_cfg, ...)

教程 1：添加地形
------------------------

.. raw:: html

   <video width="100%" controls>
     <source src="../_static/tutorial_1.mp4" type="video/mp4">
     Your browser does not support the video tag.
   </video>

**文件**：``examples/tutorial/1_add_terrain.py``

学习创建复杂地形，用于鲁棒的运动控制训练。

**你将学到**：

* 使用 ``ComplexTerrainConfig`` 生成程序化地形
* 配置各地形类型的占比（斜坡、楼梯、踏石、立柱）
* 在地形上采样有效的出生位置
* 在仿真过程中查询地形高度

**运行方式**：

.. code-block:: bash

   python examples/tutorial/1_add_terrain.py --simulator isaacgym

**代码要点**：

.. code-block:: python

   # Terrain types: [smooth slope, rough slope, stairs up, stairs down, discrete, stepping, poles, flat]
   terrain_config = ComplexTerrainConfig(
       terrain_proportions=[0.2, 0.1, 0.1, 0.1, 0.05, 0.2, 0.3, 0.1],
   )
   TerrainClass = get_class(terrain_config._target_)
   terrain = TerrainClass(config=terrain_config, num_envs=num_envs, device=device)

教程 2：加载机器人
-----------------------

.. raw:: html

   <video width="100%" controls>
     <source src="../_static/tutorial_2.mp4" type="video/mp4">
     Your browser does not support the video tag.
   </video>

**文件**：``examples/tutorial/2_load_robot.py``

学习使用机器人工厂加载不同的机器人。

**你将学到**：

* 使用 ``robot_config()`` 工厂按名称加载机器人
* 对比不同机器人配置（自由度、刚体、动作）
* 访问机器人状态（位置、速度、关节信息）

**运行方式**：

.. code-block:: bash

   # Load G1 humanoid
   python examples/tutorial/2_load_robot.py --simulator isaacgym --robot g1
   
   # Load SMPL humanoid
   python examples/tutorial/2_load_robot.py --simulator isaacgym --robot smpl

**代码要点**：

.. code-block:: python

   from protomotions.robot_configs.factory import robot_config
   
   robot_cfg = robot_config(args.robot)  # "g1", "smpl", "smplx", etc.
   print(f"Robot has {robot_cfg.number_of_actions} actions, {robot_cfg.kinematic_info.num_dofs} DOFs")

教程 3：场景创建
---------------------------

.. raw:: html

   <video width="100%" controls>
     <source src="../_static/tutorial_3.mp4" type="video/mp4">
     Your browser does not support the video tag.
   </video>

**文件**：``examples/tutorial/3_scene_creation.py``

学习添加物体并创建可供机器人交互的场景。

**你将学到**：

* 创建带有物理属性的 ``MeshSceneObject`` 和 ``BoxSceneObject``
* 配置物体选项（质量/密度、阻尼、材质、VHACD 碰撞）
* 组合包含多个物体的场景
* 在仿真过程中访问物体状态

**运行方式**：

.. code-block:: bash

   python examples/tutorial/3_scene_creation.py --simulator isaacgym --robot smpl

**代码要点**：

.. code-block:: python

   elephant = MeshSceneObject(
       object_path="examples/data/elephant.urdf",
       options=ObjectOptions(
           fix_base_link=False,
           density=1000,  # Use mass=... instead for explicit kg.
           static_friction=0.8,
           dynamic_friction=0.6,
           restitution=0.0,
           vhacd_enabled=True,
       ),
       translation=(0.0, 0.0, 1.5),
   )
   table = BoxSceneObject(width=1.0, depth=1.0, height=0.1, ...)
   
   scene = Scene(objects=[elephant, table], humanoid_motion_id=0)
   scene_lib = SceneLib(config=scene_lib_config, scenes=[scene], ...)

教程 4：基础环境
------------------------------

.. raw:: html

   <video width="100%" controls>
     <source src="../_static/tutorial_4.mp4" type="video/mp4">
     Your browser does not support the video tag.
   </video>

**文件**：``examples/tutorial/4_basic_environment.py``

学习使用 ``BaseEnv`` 创建完整的 RL 环境。

**你将学到**：

* 使用 ``EnvConfig`` 和观测设置配置 ``BaseEnv``
* 使用标准 RL 接口：``reset()``、``step()``、``get_obs()``
* 访问结构化观测（人形状态、地形）
* 处理回合终止与自动重置

**运行方式**：

.. code-block:: bash

   python examples/tutorial/4_basic_environment.py --simulator isaacgym --robot smpl

**代码要点**：

.. code-block:: python

   env_config = EnvConfig(
       max_episode_length=1000,
       observation_components={
           "max_coords_obs": max_coords_obs_factory(),
       },
   )

   env = BaseEnv(
       config=env_config,
       robot_config=robot_cfg,
       device=device,
       simulator=simulator,
       terrain=terrain,
       scene_lib=scene_lib,
   )
   obs, rewards, dones, terminated, extras = env.step(actions)

教程 5：动作管理器
---------------------------

.. raw:: html

   <video width="100%" controls>
     <source src="../_static/tutorial_5.mp4" type="video/mp4">
     Your browser does not support the video tag.
   </video>

**文件**：``examples/tutorial/5_motion_manager.py``

学习使用动作库播放参考动作。

**你将学到**：

* 从 ``.motion`` 文件（torch 格式）加载动作数据
* 从 numpy 文件加载物体轨迹
* 配置动作管理器参数（``init_start_prob``）
* 在仿真过程中跟踪动作进度（ID、时间）

**运行方式**：

.. code-block:: bash

   python examples/tutorial/5_motion_manager.py --simulator isaacgym

.. note::

   本教程使用硬编码的 SMPLX 机器人（含手部关节的 52 个刚体），
   以匹配倒茶动作数据。

**代码要点**：

.. code-block:: python

   motion_lib_config = MotionLibConfig(motion_file="examples/data/grab_teapot_pour/s1_teapot_pour_1.motion")
   motion_lib = MotionLib(config=motion_lib_config, device=device)
   
   # Motion manager controls sampling
   motion_manager = MimicMotionManagerConfig(init_start_prob=1.0)  # Always start from t=0

教程 6：Mimic 环境
------------------------------

.. raw:: html

   <video width="100%" controls>
     <source src="../_static/tutorial_6.mp4" type="video/mp4">
     Your browser does not support the video tag.
   </video>

*红色球体表示目标动作姿态，机器人则在随机动作的驱动下进行物理仿真。*

**文件**：``examples/tutorial/6_mimic_environment.py``

学习使用 ``Mimic`` 创建动作模仿环境。

**你将学到**：

* 配置 Mimic 专属观测（相位、剩余时间、目标姿态）
* 理解 ``sync_motion`` 的两种模式：运动学回放与策略训练
* 使用 ``init_start_prob`` 设置参考状态初始化（RSI）

**运行方式**：

.. code-block:: bash

   python examples/tutorial/6_mimic_environment.py --simulator isaacgym

.. note::

   本教程使用硬编码的 SMPL 人形角色，以匹配坐椅子动作数据。

**代码要点**：

.. code-block:: python

   control_components = {
       "mimic": MimicControlConfig(bootstrap_on_episode_end=True),
   }
   observation_components = {
       "max_coords_obs": max_coords_obs_factory(),
       "previous_actions": previous_actions_factory(history_steps=1),
       "mimic_target_poses": mimic_target_poses_max_coords_factory(with_velocities=True),
   }
   reward_components = {
       "action_smoothness": action_smoothness_factory(weight=-0.02),
       **mimic_tracking_rewards_factory(
           gt_weight=0.5,
           gr_weight=0.3,
           gv_weight=0.1,
           gav_weight=0.1,
       ),
   }

   env_config = EnvConfig(
       max_episode_length=300,
       num_state_history_steps=2,
       control_components=control_components,
       observation_components=observation_components,
       reward_components=reward_components,
       motion_manager=MimicMotionManagerConfig(init_start_prob=0.5),
   )

   env = BaseEnv(
       config=env_config,
       robot_config=robot_cfg,
       device=device,
       simulator=simulator,
       motion_lib=motion_lib,
       terrain=terrain,
       scene_lib=scene_lib,
   )

教程 7：DeepMimic 智能体
----------------------------

**文件**：``examples/tutorial/7_deepmimic.py``

学习使用 PPO 训练一个完整的动作跟踪智能体。

**你将学到**：

* 使用 ``MLPWithConcatConfig`` 配置 PPO 的 actor-critic 网络
* 设置模仿学习奖励（位置、旋转、速度跟踪）
* 基于跟踪误差配置提前终止
* 通过智能体的 ``fit()`` 方法启动训练

**运行方式**：

.. code-block:: bash

   python examples/tutorial/7_deepmimic.py --simulator isaacgym

.. note::

   本教程使用硬编码的 SMPL 人形角色，以匹配坐椅子动作数据。

**代码要点**：

.. code-block:: python

   reward_components = {
       "action_smoothness": action_smoothness_factory(weight=-0.02),
       **mimic_tracking_rewards_factory(
           gt_weight=0.5,
           gr_weight=0.3,
           gv_weight=0.1,
           gav_weight=0.1,
       ),
   }
   termination_components = {
       "tracking_error": tracking_error_term_factory(threshold=0.5),
   }

   env_config = EnvConfig(
       max_episode_length=200,
       num_state_history_steps=2,
       control_components=control_components,
       observation_components=observation_components,
       reward_components=reward_components,
       termination_components=termination_components,
       action_config=make_pd_action_config(robot_cfg),
       motion_manager=MimicMotionManagerConfig(init_start_prob=1.0),
   )

   obs_keys = ["max_coords_obs", "mimic_target_poses"]
   actor_config = PPOActorConfig(
       in_keys=obs_keys,
       num_out=robot_cfg.kinematic_info.num_dofs,
       mu_model=MLPWithConcatConfig(
           in_keys=obs_keys,
           out_keys=["actor_trunk_out"],
           num_out=robot_cfg.number_of_actions,
       ),
   )
   critic_config = MLPWithConcatConfig(
       in_keys=obs_keys,
       out_keys=["value"],
       num_out=1,
   )
   agent_config = PPOAgentConfig(
       model=PPOModelConfig(actor=actor_config, critic=critic_config),
       batch_size=128,
       num_steps=32,
   )

   agent = PPO(fabric=fabric, env=env, config=agent_config)
   agent.fit()

**这是一个完整的训练示例！**
