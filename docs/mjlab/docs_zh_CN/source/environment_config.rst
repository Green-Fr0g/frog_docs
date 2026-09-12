.. _environment_config:

环境配置
=========================

单个 ``ManagerBasedRlEnvCfg`` 数据类完整地定义了一个 mjlab 环境：物理世界、智能体与
物理世界的接口，以及构建在其上的 MDP。由于所有内容都位于一个扁平的对象中，环境可以
被检查、复制和修改，而无需遍历类层次结构。

在阅读本页之前，如果想对 mjlab 有一个整体了解，请先阅读
:ref:`architecture_overview`。


.. _env-config-skeleton:

带注释的骨架
------------------

``ManagerBasedRlEnvCfg`` 的完整字段集如下所示，附有行内注释。标记为 ``...`` 的字段
必须显式提供；其余字段均有默认值。

.. code-block:: python

    from dataclasses import dataclass, field

    from mjlab.envs import ManagerBasedRlEnvCfg
    from mjlab.managers.action_manager import ActionTermCfg
    from mjlab.managers.command_manager import CommandTermCfg
    from mjlab.managers.curriculum_manager import CurriculumTermCfg
    from mjlab.managers.event_manager import EventTermCfg
    from mjlab.managers.metrics_manager import MetricsTermCfg
    from mjlab.managers.observation_manager import ObservationGroupCfg
    from mjlab.managers.reward_manager import RewardTermCfg
    from mjlab.managers.termination_manager import TerminationTermCfg
    from mjlab.scene.scene import SceneCfg
    from mjlab.sim.sim import SimulationCfg
    from mjlab.viewer.viewer_config import ViewerConfig


    @dataclass
    class MyEnvCfg(ManagerBasedRlEnvCfg):

        # --- Physics ---

        decimation: int = 4
        # Number of physics steps per policy step.
        # Environment step duration = sim.mujoco.timestep * decimation.

        sim: SimulationCfg = field(default_factory=SimulationCfg)
        # Physics parameters: timestep, integrator, solver, contact settings.
        # Default timestep is 0.002 s (500 Hz). Override with MujocoCfg.

        scene: SceneCfg = ...
        # Terrain, entities, and sensors. Also sets num_envs.
        # Required; there is no default.

        # --- Episode ---

        episode_length_s: float = 20.0
        # Episode duration in seconds.
        # Steps = ceil(episode_length_s / (sim.mujoco.timestep * decimation)).

        is_finite_horizon: bool = False
        # False (default): time limit is an artificial cutoff. The agent
        #   receives a truncated signal and bootstraps value beyond the limit.
        # True: time limit defines the task boundary. The agent receives a
        #   terminal done signal with no future value beyond it.

        scale_rewards_by_dt: bool = True
        # When True (default), each reward term is multiplied by step_dt so
        # that cumulative episodic sums are invariant to simulation frequency.
        # Set to False for algorithms that expect unscaled reward signals.

        # --- Managers ---

        observations: dict[str, ObservationGroupCfg] = field(default_factory=dict)
        # Observation groups. Each key is a group name (e.g. "actor", "critic").
        # Groups can differ in noise, history, delay, and concatenation.

        actions: dict[str, ActionTermCfg] = field(default_factory=dict)
        # Action terms. Each term controls one slice of the policy output
        # and routes it to a specific entity's actuators.

        rewards: dict[str, RewardTermCfg] = field(default_factory=dict)
        # Reward terms. The manager computes a weighted sum each step.

        terminations: dict[str, TerminationTermCfg] = field(default_factory=dict)
        # Termination conditions. If empty, episodes never terminate early.
        # Add a time_out term to enforce the episode length limit.

        events: dict[str, EventTermCfg] = field(
            default_factory=lambda: {
                "reset_scene_to_default": EventTermCfg(
                    func=reset_scene_to_default,
                    mode="reset",
                )
            }
        )
        # Event terms for domain randomization and state resets.
        # The default includes reset_scene_to_default, which resets all
        # entities to their initial pose each episode. Override this dict
        # to replace or extend the default reset behavior.

        commands: dict[str, CommandTermCfg] = field(default_factory=dict)
        # Command generators (e.g. velocity targets for locomotion).
        # Commands are resampled at configurable intervals and on reset.

        curriculum: dict[str, CurriculumTermCfg] = field(default_factory=dict)
        # Curriculum terms that adjust training conditions based on performance.

        metrics: dict[str, MetricsTermCfg] = field(default_factory=dict)
        # Custom metrics logged as episode averages alongside reward terms.

        # --- Misc ---

        seed: int | None = None
        # Random seed for reproducibility. If None, a random seed is chosen
        # and stored back into this field after initialization.

        viewer: ViewerConfig = field(default_factory=ViewerConfig)
        # Camera position, resolution, and tracking target for rendering.


.. _env-config-term-pattern:

项配置模式
--------------------------

.. note::
   这里的"项"（term）沿用了 Isaac Lab 的术语，指的是配置字典中登记的一个条目：
   每一项绑定一个函数（或类实例）和它自己的配置。管理器每步逐个调用这些项，并按各自
   的方式汇总其输出——观测项被拼接成向量，奖励项加权求和，终止项做逻辑或，等等。
   下文各管理器页面中出现的"观测项""奖励项""事件项"都是这个意思。

所有管理器的字典都遵循相同的模式。每个条目将一个字符串名称映射到一个项配置对象。
该配置至少包含一个 ``func`` 字段，指向实现该项的可调用对象，以及一个 ``params``
字典，其中的额外关键字参数会被转发给该可调用对象。

管理器每步调用一次 ``func(env, **params)`` （当 ``func`` 是一个已被实例化的类时，
则调用 ``term(env, **params)``）。项的名称是任意的；它们会出现在训练日志中，仅用于
标识。

.. rubric:: 奖励项

.. code-block:: python

    from mjlab.envs import mdp
    from mjlab.managers.reward_manager import RewardTermCfg
    from mjlab.managers.scene_entity_config import SceneEntityCfg

    rewards = {
        "alive": RewardTermCfg(
            func=mdp.is_alive,
            weight=1.0,
        ),
        "joint_torques": RewardTermCfg(
            func=mdp.joint_torques_l2,
            weight=-1e-4,
            params={"asset_cfg": SceneEntityCfg("robot")},
        ),
        "action_rate": RewardTermCfg(
            func=mdp.action_rate_l2,
            weight=-0.1,
        ),
    }

``weight`` 会在函数输出被累加进总奖励之前对其进行缩放。负的权重会产生惩罚项。

``params`` 映射到函数的关键字参数。例如，``mdp.joint_torques_l2(env, asset_cfg=...)``
从 ``params`` 字典中接收 ``asset_cfg``。任何未在 ``params`` 中列出的参数必须在函数
签名中具有默认值。

.. rubric:: 终止项

.. code-block:: python

    from mjlab.envs import mdp
    from mjlab.managers.termination_manager import TerminationTermCfg

    terminations = {
        "time_out": TerminationTermCfg(
            func=mdp.time_out,
            time_out=True,   # marks this as a truncation, not a failure
        ),
        "fell_over": TerminationTermCfg(
            func=mdp.bad_orientation,
            params={"limit_angle": 1.22},   # ~70 degrees in radians
        ),
    }

``TerminationTermCfg`` 上的 ``time_out`` 标志告诉管理器将此条件视为截断而非终端失败。
截断对应 Gym 接口中的 ``truncated`` 信号；失败对应 ``terminated``。这一区别对于 RL
算法中的价值自举（value bootstrapping）非常重要。

.. rubric:: 事件项

.. code-block:: python

    from mjlab.managers.event_manager import EventTermCfg

    events = {
        "reset_base": EventTermCfg(
            func=mdp.reset_root_state_uniform,
            mode="reset",
            params={
                "pose_range": {"yaw": (-3.14, 3.14)},
                "velocity_range": {},
            },
        ),
    }

``EventTermCfg`` 上的 ``mode`` 字段控制该项何时触发：在启动时、在回合重置时，或以
固定间隔触发。有关生命周期模式、内置事件函数以及事件与域随机化之间关系的完整说明，
请参阅 :ref:`events`。

.. rubric:: 基于函数与基于类的项

项可以是普通函数或类。函数适用于无状态计算；当某个项需要缓存开销较大的设置或在
多个步骤之间维护状态时，类会更有用。

基于函数的项具有 ``func(env, **params) -> Tensor`` 的签名。基于类的项会用
``(cfg, env)`` 实例化一次，随后以相同的签名被调用。类可以选择性地实现
``reset(env_ids)`` 钩子，用于在每个回合清除状态。

.. code-block:: python

    # Function-based (stateless)
    RewardTermCfg(func=mdp.joint_torques_l2, weight=-0.01)

    # Class-based (caches joint indices at init)
    class MyReward:
        def __init__(self, cfg, env):
            self.joint_ids = resolve_joint_ids(cfg.params, env)

        def __call__(self, env) -> torch.Tensor:
            return compute_reward(env, self.joint_ids)

    RewardTermCfg(func=MyReward, weight=1.0)


.. _env-config-timing:

时序：decimation、timestep 与回合长度
-------------------------------------------------

三个参数共同决定了环境的时间结构。

``sim.mujoco.timestep``
    物理积分步长，单位为秒。默认值为 0.002 s（500 Hz）。这是任何环境中最重要
    的参数之一：较小的值会产生更稳定的物理效果，但会降低仿真速度。关于选择
    timestep 与求解器设置的实用建议，请参阅 MuJoCo 的
    `性能调优 <https://mujoco.readthedocs.io/en/stable/modeling.html#performance-tuning>`_
    指南。

``decimation``
    每个策略步执行的物理步数。策略的运行频率为 ``1 / (timestep * decimation)`` Hz。

``episode_length_s``
    回合时长，单位为秒。每个回合的最大策略步数为
    ``ceil(episode_length_s / (timestep * decimation))``。

**具体示例。** 速度任务使用 ``timestep=0.005`` （200 Hz 物理）和 ``decimation=4``，
从而策略频率为 50 Hz。在 ``episode_length_s=20.0`` 的情况下，每个回合恰好运行
1000 个策略步。

.. code-block:: python

    physics_dt  = 0.005        # seconds per physics step (200 Hz)
    decimation  = 4            # physics steps per policy step
    step_dt     = 0.005 * 4   # = 0.02 s per policy step (50 Hz)
    episode_len = 20.0 / 0.02  # = 1000 policy steps per episode

要在运行时读取这些值，请使用环境的属性：

.. code-block:: python

    env.physics_dt          # = cfg.sim.mujoco.timestep
    env.step_dt             # = cfg.sim.mujoco.timestep * cfg.decimation
    env.max_episode_length  # steps (int)
    env.max_episode_length_s  # seconds (float)

当 ``scale_rewards_by_dt=True`` （默认值）时，每个奖励项在返回前都会乘以
``step_dt``。一个返回常量值 1.0 的奖励函数每步贡献 ``step_dt``，在整个回合中
大约贡献 ``episode_length_s``，而无论 ``decimation`` 和 ``timestep`` 如何设置。
在不禁用该缩放的情况下更改仿真频率，奖励的量级保持不变。


.. _env-config-subclassing:

子类化模式
-------------------

mjlab 使用普通的数据类继承，而不是深层嵌套的类层次结构。要构建特定任务的配置，
可以继承 ``ManagerBasedRlEnvCfg`` 并覆盖其字段。

推荐的做法是：在一个工厂函数中定义完整配置，然后从各机器人的特定配置中调用它，
只覆盖有差异的字段。速度任务就采用了这种模式：``make_velocity_env_cfg`` 返回一个
完整装配好的 ``ManagerBasedRlEnvCfg``，而每个机器人配置都调用该工厂并补入机器人
特定的值，例如场景、关节名称模式和动作缩放。

一个精简版的工厂函数展示了完整的装配模式：

.. code-block:: python

    import math
    from dataclasses import replace

    from mjlab.envs import ManagerBasedRlEnvCfg
    from mjlab.envs.mdp import dr
    from mjlab.envs.mdp.actions import JointPositionActionCfg
    from mjlab.managers.event_manager import EventTermCfg
    from mjlab.managers.observation_manager import ObservationGroupCfg, ObservationTermCfg
    from mjlab.managers.reward_manager import RewardTermCfg
    from mjlab.managers.scene_entity_config import SceneEntityCfg
    from mjlab.managers.termination_manager import TerminationTermCfg
    from mjlab.scene import SceneCfg
    from mjlab.sim import MujocoCfg, SimulationCfg
    from mjlab.tasks.velocity import mdp
    from mjlab.tasks.velocity.mdp import UniformVelocityCommandCfg
    from mjlab.terrains import TerrainEntityCfg
    from mjlab.terrains.config import ROUGH_TERRAINS_CFG
    from mjlab.viewer import ViewerConfig


    def make_velocity_env_cfg() -> ManagerBasedRlEnvCfg:

        observations = {
            "actor": ObservationGroupCfg(
                terms={
                    "base_lin_vel": ObservationTermCfg(
                        func=mdp.builtin_sensor,
                        params={"sensor_name": "robot/imu_lin_vel"},
                    ),
                    "joint_pos": ObservationTermCfg(func=mdp.joint_pos_rel),
                    "command": ObservationTermCfg(
                        func=mdp.generated_commands,
                        params={"command_name": "twist"},
                    ),
                    # additional terms omitted for brevity
                },
                concatenate_terms=True,
                enable_corruption=True,
            ),
            "critic": ObservationGroupCfg(
                terms={...},
                concatenate_terms=True,
                enable_corruption=False,
            ),
        }

        actions = {
            "joint_pos": JointPositionActionCfg(
                entity_name="robot",
                actuator_names=(".*",),
                scale=0.5,
                use_default_offset=True,
            )
        }

        commands = {
            "twist": UniformVelocityCommandCfg(
                entity_name="robot",
                resampling_time_range=(3.0, 8.0),
                ranges=UniformVelocityCommandCfg.Ranges(
                    lin_vel_x=(-1.0, 1.0),
                    lin_vel_y=(-1.0, 1.0),
                    ang_vel_z=(-0.5, 0.5),
                    heading=(-math.pi, math.pi),
                ),
            )
        }

        events = {
            "reset_base": EventTermCfg(
                func=mdp.reset_root_state_uniform,
                mode="reset",
                params={
                    "pose_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5), "yaw": (-3.14, 3.14)},
                    "velocity_range": {},
                },
            ),
            "foot_friction": EventTermCfg(
                mode="startup",
                func=dr.geom_friction,
                params={
                    "asset_cfg": SceneEntityCfg("robot", geom_names=[]),
                    "operation": "abs",
                    "ranges": (0.3, 1.2),
                },
            ),
            "push_robot": EventTermCfg(
                func=mdp.push_by_setting_velocity,
                mode="interval",
                interval_range_s=(1.0, 3.0),
                params={"velocity_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5)}},
            ),
        }

        rewards = {
            "track_linear_velocity": RewardTermCfg(
                func=mdp.track_linear_velocity,
                weight=2.0,
                params={"command_name": "twist", "std": math.sqrt(0.25)},
            ),
            "dof_pos_limits": RewardTermCfg(func=mdp.joint_pos_limits, weight=-1.0),
            "action_rate_l2": RewardTermCfg(func=mdp.action_rate_l2, weight=-0.1),
        }

        terminations = {
            "time_out": TerminationTermCfg(func=mdp.time_out, time_out=True),
            "fell_over": TerminationTermCfg(
                func=mdp.bad_orientation,
                params={"limit_angle": math.radians(70.0)},
            ),
        }

        return ManagerBasedRlEnvCfg(
            decimation=4,
            episode_length_s=20.0,
            sim=SimulationCfg(
                nconmax=35,
                njmax=1500,
                mujoco=MujocoCfg(timestep=0.005, iterations=10, ls_iterations=20),
            ),
            scene=SceneCfg(
                terrain=TerrainEntityCfg(
                    terrain_type="generator",
                    terrain_generator=replace(ROUGH_TERRAINS_CFG),
                    max_init_terrain_level=5,
                ),
                num_envs=1,
            ),
            observations=observations,
            actions=actions,
            commands=commands,
            events=events,
            rewards=rewards,
            terminations=terminations,
        )

机器人特定配置会调用该工厂，并使用 ``dataclasses.replace`` 或直接赋值来修补字段。
常见的每机器人覆盖包括 ``scene`` （用于添加机器人实体和传感器）、``SceneEntityCfg``
中的关节名称模式、动作 ``scale``，以及奖励项中的 body 名称。

.. note::

   Isaac Lab 使用深层嵌套的 ``__post_init__`` 覆盖来实现配置继承。mjlab 避免了这种
   模式：每个 ``ManagerBasedRlEnvCfg`` 都是一个扁平、可检查的数据类。拼写错误的字段
   名会在构造时抛出 ``TypeError``，而不是静默地创建一个新属性。完整对比请参阅
   :ref:`migration_isaac_lab`。


后续阅读
----------------

Manager Layer（管理器层）部分的其余页面将详细介绍各个管理器：

- :ref:`observations`：观测组、处理流水线（裁剪、缩放、噪声、延迟、历史）以及
  内置观测函数。
- :ref:`actions`：动作类型，以及动作管理器如何将策略输出路由到执行器。
- :ref:`rewards`：奖励项以及按 dt 缩放。
- :ref:`terminations`：回合结束条件，以及截断/失败的区别。
- :ref:`commands`：指令生成器与基于目标的任务设置。
- :ref:`events`：事件管理器的生命周期（startup、reset、interval）。
- :ref:`domain_randomization`：用于域随机化的完整 ``dr`` 模块。
- :ref:`curriculum`：基于策略表现的难度递进。
- :ref:`metrics`：以回合平均值形式记录的自定义每步指标。
