.. _commands:

指令
====

指令规定策略在每个时刻应当达成的目标：目标速度、参考轨迹、目标位置等。指令
管理器生成这些信号，按可配置的间隔重新采样，并通过观测系统传递给策略。


注册
----

指令以字典形式注册在 ``ManagerBasedRlEnvCfg`` 中，将字符串名称映射到
``CommandTermCfg`` 实例。与其他管理器所用的基于函数的项不同，每个指令项都是
一个继承自 ``CommandTerm`` 的类。

``resampling_time_range`` 字段控制指令多久变化一次。每次重采样后，该项会从
给定的 ``(min, max)`` 范围 (以秒为单位) 中均匀抽取一个新的计时器值。此外，
在每个回合重置时，指令也会被无条件地重新采样。

.. code-block:: python

    commands = {
        "twist": UniformVelocityCommandCfg(
            entity_name="robot",
            resampling_time_range=(3.0, 8.0),
            ranges=UniformVelocityCommandCfg.Ranges(
                lin_vel_x=(-1.0, 1.0),
                lin_vel_y=(-1.0, 1.0),
                ang_vel_z=(-0.5, 0.5),
            ),
        ),
    }

``generated_commands`` 观测函数按名称读取当前指令张量，并将其传递给策略：

.. code-block:: python

    ObservationTermCfg(
        func=mdp.generated_commands,
        params={"command_name": "twist"},
    )

如果环境中没有指令，管理器会将所有操作变为空操作并返回空张量，无需任何特殊
处理。


内置指令项
----------

每个任务都附带针对其目标定制的指令项。

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - 项
     - 描述
   * - ``UniformVelocityCommand``
     - 从可配置范围内均匀采样，生成平面速度指令 ``[v_x, v_y, omega_z]`` 。
       支持站立模式 (一部分环境接收零速度) 和航向模式 (偏航角速度由跟踪采样
       航向角的比例控制器替代)。用于速度任务。
   * - ``LiftingCommand``
     - 为被操作物体生成 3D 目标位置。支持固定难度和动态难度两种模式。跟踪
       位置误差、回合成功率等指标。用于操作 (manipulation) 任务。
   * - ``MotionCommand``
     - 从预录制的 ``.npz`` 运动片段中流式提供参考关节位置、速度和身体位姿。
       支持三种起始帧采样模式：``"start"`` (始终为第 0 帧)、``"uniform"``
       (随机) 和 ``"adaptive"`` (偏向困难区域)。重置时机器人从采样帧初始化，
       并可施加可选扰动。用于跟踪任务。

当配置中设置了 ``debug_vis=True`` 时，每个项都可以在交互式查看器中渲染调试
可视化。下图展示了 ``MotionCommand`` 的幽灵 (ghost) 可视化：它在参考位姿处
渲染一个半透明的机器人副本，与真实机器人并列显示。

.. figure:: _static/ghost_visualization.png
   :align: center
   :width: 100%

   G1 跟踪任务中指令参考运动的 Viser 可视化。


编写自定义指令项
----------------

自定义指令项是一个继承自 ``CommandTerm`` 的类，搭配一个继承自
``CommandTermCfg`` 的配置 dataclass。该项必须实现四个方法：
``_resample_command(env_ids)`` 用于采样新目标，``_update_command()`` 用于
每步更新，``_update_metrics()`` 用于记录指标，以及一个返回当前目标张量的
``command`` 属性。基类会自动管理重采样计时器和重置逻辑。

配置必须实现 ``build(env)`` 方法，用于构造配套的项实例。
