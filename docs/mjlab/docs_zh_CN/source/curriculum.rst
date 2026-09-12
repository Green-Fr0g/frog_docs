.. _curriculum:

课程
====

课程管理器根据策略表现调整训练条件。训练从一个较简单的问题开始，随着策略证明自己能够应对当前条件，难度逐步提升。常见用途包括：把机器人推进到更难的地形、放宽指令速度范围，以及在训练过程中逐步加大奖励惩罚项的权重。

课程项在每次环境重置时被调用。每一项都会接收环境以及正在被重置的环境 ID 集合，检查某个表现信号，然后直接修改环境参数。

.. code-block:: python

    from mjlab.managers.curriculum_manager import CurriculumTermCfg

    curriculum = {
        "terrain_levels": CurriculumTermCfg(
            func=mdp.terrain_levels_vel,
            params={"command_name": "twist"},
        ),
    }

课程函数的返回值会以 ``Curriculum/<term_name>`` 为名记录到训练指标中。


内置课程函数
--------------

.. list-table::
   :header-rows: 1
   :widths: 24 76

   * - 函数
     - 描述
   * - ``terrain_levels_vel``
     - 统计每个机器人在回合内行进的距离。行进距离足够远的机器人会在地形网格中上移一个难度行；未达标的机器人则下移。参见下文的地形课程部分。
   * - ``commands_vel``
     - 根据训练步数放宽速度指令范围。每个阶段指定一个步数阈值，以及超过该阈值后要应用的新范围。
   * - ``reward_curriculum``
     - 根据训练步数阈值调整某个奖励项的权重和/或参数。它取代了旧的 ``reward_weight`` 函数，并且还支持修改奖励函数的参数。
   * - ``termination_curriculum``
     - 根据训练步数阈值调整某个终止项的参数。适用于随着训练推进逐渐收紧终止条件（例如能量上限）。


奖励课程
--------

``reward_curriculum`` 随训练进程安排对某个奖励项的权重或关键字参数的修改。每个阶段指定一个 ``step`` 阈值，以及可选的 ``weight`` 或 ``params`` 更新。各阶段按顺序求值，所有阈值已达到的阶段都会被应用。

**逐步加大惩罚权重**

一种常见模式是：训练初期以较低权重引入惩罚项，待策略学会基本技能后再逐步加大：

.. code-block:: python

    from mjlab.managers.curriculum_manager import CurriculumTermCfg

    curriculum = {
        "joint_vel_hinge_weight": CurriculumTermCfg(
            func=mdp.reward_curriculum,
            params={
                "reward_name": "joint_vel_hinge",
                "stages": [
                    {"step": 0, "weight": -0.01},
                    {"step": 12000, "weight": -0.1},
                    {"step": 24000, "weight": -1.0},
                ],
            },
        ),
    }

**调整奖励参数**

也可以修改传给奖励函数的参数。例如，随训练推进收紧跟踪容差：

.. code-block:: python

    curriculum = {
        "track_lin_vel_tighten": CurriculumTermCfg(
            func=mdp.reward_curriculum,
            params={
                "reward_name": "track_linear_velocity",
                "stages": [
                    {"step": 0, "params": {"std": 0.5}},
                    {"step": 20000, "params": {"std": 0.3}},
                    {"step": 50000, "params": {"std": 0.1}},
                ],
            },
        ),
    }

**同时调整权重和参数**

单个阶段可以同时更新权重和参数：

.. code-block:: python

    {"step": 24000, "weight": -1.0, "params": {"max_vel": 1.0}}


终止课程
--------

``termination_curriculum`` 随训练进程安排对某个终止项参数的修改。当策略已学会基本行为后，可以用它来逐渐收紧终止条件。

**收紧能量上限**

先从一个宽松的能量阈值开始，再在训练中逐步降低：

.. code-block:: python

    from mjlab.managers.curriculum_manager import CurriculumTermCfg

    curriculum = {
        "energy_threshold": CurriculumTermCfg(
            func=mdp.termination_curriculum,
            params={
                "termination_name": "energy",
                "stages": [
                    {"step": 12000, "params": {"threshold": 1000.0}},
                    {"step": 24000, "params": {"threshold": 700.0}},
                    {"step": 36000, "params": {"threshold": 400.0}},
                ],
            },
        ),
    }

如有需要，``TerminationTermCfg`` 的 ``time_out`` 字段也可以通过阶段来切换，不过这在实际中并不常见。


地形课程
--------

程序化地形使用的地形网格是一个 ``num_rows x num_cols`` 的地块矩阵。列代表地形类型变体；行代表难度等级，第 0 行最简单，第 ``num_rows - 1`` 行最难。当 ``TerrainGeneratorCfg.curriculum=True`` 时，每一列恰好分配一种地形类型，使得难度沿行单调递增。

在环境构建时，每个环境会在 ``[0, max_init_terrain_level]`` 内被分配一个随机的起始行。``terrain_levels_vel`` 课程项会在每次重置时根据回合内行进的距离升降环境所处难度。到达最高等级的环境会被随机重新分配到任意一行，从而保持所有难度等级都有覆盖。有关地形网格本身的配置细节，参见 :ref:`terrain` 一节。


编写自定义课程函数
--------------------

课程函数接受 ``env`` 和 ``env_ids``，执行参数修改，并返回一个用于记录的值（标量张量、张量字典或 ``None``）。典型的实现会读取某个表现指标，决定提高还是降低难度，就地修改相关配置，并返回当前难度等级。通用模式参见 :ref:`env-config-term-pattern` 一节。
