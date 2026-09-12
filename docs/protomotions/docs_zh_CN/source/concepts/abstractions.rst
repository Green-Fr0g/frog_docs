核心抽象
========

本文详细介绍 ProtoMotions 的主要组件。

MotionLib
---------

**位置：** ``protomotions/components/motion_lib.py``

MotionLib（动作库）存储用于模仿学习的参考动作数据。

**为什么要把动作打包成张量？**

当运行 4096 个并行环境时，每个环境需要在不同的时刻查询不同的动作。
朴素的按动作存储方式需要 4096 次独立查找。

因此，我们将所有动作拼接成连续张量：

.. code-block:: python

   gts: Tensor[total_frames, num_bodies, 3]   # positions
   grs: Tensor[total_frames, num_bodies, 4]   # rotations (quaternion)
   gvs: Tensor[total_frames, num_bodies, 3]   # linear velocities
   gavs: Tensor[total_frames, num_bodies, 3]  # angular velocities
   dps: Tensor[total_frames, num_dofs]        # DOF positions
   dvs: Tensor[total_frames, num_dofs]        # DOF velocities
   contacts: Tensor[total_frames, num_bodies] # contact labels

帧边界通过以下方式记录：

.. code-block:: python

   length_starts: Tensor[num_motions]      # Start index of each motion
   motion_num_frames: Tensor[num_motions]  # Number of frames per motion
   motion_lengths: Tensor[num_motions]     # Duration in seconds

**查询动作：**

.. code-block:: python

   # Get state for multiple envs at once
   state = motion_lib.get_motion_state(
       motion_ids=torch.tensor([0, 1, 2, ...]),  # Which motion per env
       motion_times=torch.tensor([0.5, 1.2, ...])  # Time in seconds
   )
   # Returns RobotState with interpolated values

帧插值保证了即使在非整数时刻也能得到平滑的动作状态。

Terrain
-------

**位置：** ``protomotions/components/terrains/``

Terrain（地形）通过程序化生成高度场来提升训练的鲁棒性。

**配置：**

.. code-block:: python

   TerrainConfig(
       sim_config=TerrainSimConfig(
           static_friction=1.0,
           dynamic_friction=1.0,
       ),
       # Subterrain types, proportions, etc.
   )

复杂地形是可选的——基础训练时我们会使用平坦地形。

SceneLib
--------

**位置：** ``protomotions/components/scene_lib.py``

SceneLib 管理环境中的物体，用于交互任务。

**物体类型：**

* **Box**：简单立方体图元
* **Sphere**：球体图元
* **Mesh**：从文件加载的自定义网格

**示例：**

.. code-block:: python

   scene = Scene(objects=[
       SceneObject(
           object_type="box",
           position=[1.0, 0.0, 0.5],
           dimensions=[0.5, 0.5, 1.0],
           fix_base_link=True,  # Static object
       )
   ])

**点云生成**：SceneLib 可以为物体生成点云，供基于感知的策略使用。

Robot Config
------------

**位置：** ``protomotions/robot_configs/``

机器人配置在 MJCF 文件之外，进一步定义"仿真什么"。

**为什么不直接用 MJCF？**

MJCF 定义了机器人的物理结构，但我们还需要额外的信息：

1. **语义身体映射**：哪些刚体是脚、手、头？
2. **仿真器特定设置**：不同求解器需要不同的迭代次数
3. **控制参数**：PD 增益、动作缩放
4. **资产路径**：物理仿真用 MJCF，IsaacLab 用 USD

**关键字段：**

.. code-block:: python

   @dataclass
   class RobotConfig:
       # Semantic mappings (used for contact detection, observations)
       common_naming_to_robot_body_names: Dict[str, List[str]]
       
       # Physics assets
       asset: RobotAssetConfig
       
       # Control (PD gains, action scaling)
       control: ControlConfig
       
       # Per-simulator physics settings
       simulation_params: SimulatorParams
       
       # Populated from MJCF (auto-extracted)
       kinematic_info: KinematicInfo  # Body hierarchy, joint info

**与 PoseLib 的关系：**

``pose_lib.extract_kinematic_info()`` 解析 MJCF 并填充 ``kinematic_info``，
提供 FK/IK 和观测计算所需的身体层级结构。

Simulator
---------

**位置：** ``protomotions/simulator/base_simulator/``

仿真器抽象封装了不同的物理后端。

**接口：**

.. code-block:: python

   class BaseSimulator:
       def step(self, actions: Tensor) -> None: ...
       def get_state(self) -> SimulatorState: ...
       def set_state(self, state: SimulatorState) -> None: ...
       def reset_envs(self, env_ids: Tensor) -> None: ...

所有后端（IsaacGym、IsaacLab、Newton、Genesis、MuJoCo）都实现该接口，
使环境代码与具体仿真器解耦。

**SimulatorState：**

这是数据准备、仿真器和环境之间共享的核心数据结构，
详见 :doc:`simulator_state`。

Environment
-----------

**位置：** ``protomotions/envs/``

环境通过模块化组件编排训练循环。基础环境将观测、奖励、终止和控制
委托给专门的管理器处理。

**结构：**

* ``BaseEnv``：包含各组件管理器的核心环境
* ``MimicEnv``：扩展 BaseEnv，用于动作模仿
* ``SteeringEnv``：扩展 BaseEnv，用于运动控制

组件系统
--------

**位置：** ``protomotions/envs/component_manager.py``、
``protomotions/envs/component_factories.py`` 和 ``protomotions/envs/control/``

ProtoMotions 采用基于组件的架构：观测、奖励、终止和控制都被定义为
模块化、可复用的组件。

**为什么用组件？**

与其把观测和奖励硬编码在环境类里，组件化让你可以：

* 通过配置自由组合不同的观测/奖励方案
* 无需修改环境代码即可添加新奖励
* 在不同类型的环境间复用组件
* 在实验文件中完成所有配置

控制组件
~~~~~~~~

**位置：** ``protomotions/envs/control/``

控制组件是**有状态**的任务管理器，决定环境的行为。

.. code-block:: python

   class ControlComponent(ABC):
       def reset(self, env_ids: Tensor): ...
       def step(self): ...
       def get_context(self) -> Dict[str, Any]: ...
       def should_terminate(self) -> Tuple[Tensor, Tensor]: ...

**关键特性：**

* 跨时间步维护状态（例如当前目标动作、路径路径点）
* 为观测和奖励提供上下文变量
* 可以定义自定义终止条件
* 可以访问完整的环境

**内置组件：**

* ``MimicControlComponent``：动作跟踪（采样动作、跟踪进度）
* ``SteeringControlComponent``：朝向与速度目标
* ``PathFollowerControlComponent``：路径生成与跟随

**配置：**

.. code-block:: python

   control_components = {
       "mimic": MimicControlConfig(
           bootstrap_on_episode_end=True,
       )
   }

观测组件
~~~~~~~~

**位置：** ``protomotions/envs/obs/``

观测组件是**无状态**函数，从上下文变量计算观测。

.. code-block:: python

   @dataclass
   class ObservationComponentConfig:
       function: Callable[..., Tensor]  # Pure function
       variables: Dict[str, str]  # Maps args to context keys

**关键特性：**

* 无副作用的纯函数
* 从控制组件接收上下文
* 可通过 ``indices_subset`` 指定刚体子集
* 支持观测噪声注入

**配置：**

.. code-block:: python

   from protomotions.envs.obs import (
       max_coords_obs_factory,
       mimic_target_poses_max_coords_factory,
   )
   
   observation_components = {
       "max_coords_obs": max_coords_obs_factory(),
       "target_poses": mimic_target_poses_max_coords_factory(),
   }

工厂函数创建预先配置好的 ``ObservationComponentConfig`` 实例。

奖励组件
~~~~~~~~

**位置：** ``protomotions/envs/utils/rewards.py``

奖励组件是**无状态**函数，计算各项奖励项。

.. code-block:: python

   @dataclass
   class RewardComponentConfig:
       function: Callable[..., Tensor]
       variables: Dict[str, str]
       weight: float = 1.0
       grace_period: float = 0.0  # Seconds before reward activates
       reward_type: str = "multiplicative"  # or "additive"

**配置：**

.. code-block:: python

   from protomotions.envs.rewards import (
       gt_rew_factory,
       action_smoothness_factory,
   )
   
   reward_components = {
       "gt_rew": gt_rew_factory(weight=0.5, coefficient=-100.0),
       "action_smoothness": action_smoothness_factory(weight=-0.02),
   }

**奖励类型：**

* ``multiplicative``：以乘积方式组合（跟踪奖励的默认类型）
* ``additive``：直接求和（用于动作平滑度等惩罚项）

终止组件
~~~~~~~~

**位置：** ``protomotions/envs/utils/terminations.py``

终止组件检查回合是否满足终止条件。

.. code-block:: python

   @dataclass
   class TerminationComponentConfig:
       function: Callable[..., Tensor]
       variables: Dict[str, str]

**配置：**

.. code-block:: python

   from protomotions.envs.terminations import tracking_error_factory
   
   termination_components = {
       "tracking_error": tracking_error_factory(threshold=0.5),
   }

**内置终止条件：**

* ``tracking_error``：跟踪误差超过阈值时终止回合
* 高度终止和最大回合长度由 ``BaseEnv`` 直接处理

组件运行时
~~~~~~~~~~

**位置：** ``protomotions/envs/component_manager.py`` 和
``protomotions/envs/control/manager.py``

运行时负责编排组件的求值：

* ``ControlManager`` 初始化并逐步推进各任务控制组件。
* ``ComponentManager`` 从当前 ``EnvContext`` 出发，执行观测、奖励和终止
  的 ``MdpComponent`` 核函数。
* ``BaseEnv`` 汇总原始奖励和终止输出，应用宽限期，并为智能体保存观测。

**数据流：**

.. code-block:: text

   Control Components → EnvContext → Observation/Reward/Termination Components
          │                                         │
          └─────────────────────────────────────────┘
                          ↓
                   Environment Step

Agent
-----

**位置：** ``protomotions/agents/``

Agent（智能体）实现强化学习算法。

**结构：**

* ``BaseAgent``：训练循环、检查点管理
* ``PPOAgent``：近端策略优化（PPO）
* ``AMPAgent``：对抗运动先验（AMP）
* ``ASEAgent``：对抗技能嵌入（ASE）
* ``MaskedMimicAgent``：带跟踪奖励的掩码动作模仿

下一步
------

* :doc:`environment_context` - 连接各组件的上下文字典
* :doc:`pose_lib` - MJCF 解析与 FK/IK 工具
* :doc:`simulator_state` - 状态表示详解
