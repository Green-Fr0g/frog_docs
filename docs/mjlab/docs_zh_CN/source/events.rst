.. _events:

事件
====

事件管理器在环境生命周期的特定时点执行钩子。任何需要在启动时、回合重置时或训练过程中按固定间隔运行的逻辑，都注册为事件项 (event term)。常见的例子包括：把实体重置到初始状态、对模型参数施加域随机化、用随机速度扰动推动机器人，以及从参考运动片段初始化机器人状态。所有这些都通过同一个 ``EventTermCfg`` 接口配置，区别仅在于控制各项何时触发的 ``mode`` 字段。

域随机化是事件最常见的用途之一，它有专门的参考页面。完整的 ``dr`` 模块、可用函数以及内部机制，请参阅 :ref:`domain_randomization` 一页。

.. code-block:: python

    from mjlab.envs.mdp import events as event_fns, dr
    from mjlab.managers.event_manager import EventTermCfg
    from mjlab.managers.scene_entity_config import SceneEntityCfg

    events = {
        # Reset all entities to their default state each episode.
        "reset_scene": EventTermCfg(
            func=event_fns.reset_scene_to_default,
            mode="reset",
        ),
        # Randomize foot friction once at startup.
        "foot_friction": EventTermCfg(
            func=dr.geom_friction,
            mode="startup",
            params={
                "asset_cfg": SceneEntityCfg("robot", geom_names=[".*foot.*"]),
                "ranges": (0.3, 1.2),
                "operation": "abs",
            },
        ),
        # Push the robot at random intervals during the episode.
        "push_robot": EventTermCfg(
            func=event_fns.push_by_setting_velocity,
            mode="interval",
            interval_range_s=(1.0, 3.0),
            params={
                "velocity_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5)},
            },
        ),
        # Transient random impulses with duration and cooldown.
        "impulse": EventTermCfg(
            func=event_fns.apply_body_impulse,
            mode="step",
            params={
                "force_range": (-50.0, 50.0),
                "torque_range": (0.0, 0.0),
                "duration_s": (0.1, 0.2),
                "cooldown_s": (1.0, 3.0),
                "asset_cfg": SceneEntityCfg("robot", body_names=("base",)),
            },
        ),
    }


生命周期模式
------------

``EventTermCfg`` 的 ``mode`` 字段决定各项何时触发。四种模式对应一次 RL 训练运行的不同时间尺度：进程启动时一次、每个回合一次、回合内周期性触发，以及每个环境步触发一次。

``"startup"``
    在环境初始化期间触发一次，此时所有管理器均已构造完成。每个环境同时收到该事件。此模式适用于那些应在环境之间有所差异、但在整个训练过程中保持固定的参数，例如通过 ``dr`` 模块随机化的连杆质量或关节 armature。

``"reset"``
    在每次回合重置时触发，针对每个正在被重置的环境。这是最常用的模式。状态初始化（把机器人写回默认位姿）以及回合级的域随机化都属于这里。

    可选的 ``min_step_count_between_reset`` 字段可防止该项在回合非常短时触发得过于频繁。对于自上次触发以来步数尚未达到该值的环境，该项会被跳过。但首次调用始终会触发。

``"interval"``
    在训练过程中按固定时间间隔触发，与回合边界无关。触发频率由 ``interval_range_s`` 控制，它是一个以秒为单位的 ``(min, max)`` 区间。每次触发后，管理器会从该区间中均匀采样一个新的等待时间。默认情况下每个环境都有自己独立的计时器；设置 ``is_global_time=True`` 可以让所有环境同步到同一个共享计时器。回合中段的扰动（如外部推力或逐渐漂移的模型参数）天然适合放在 interval 事件中。

``"step"``
    在每个环境步触发，作用于所有环境。此模式适用于必须每步求值的持续性效果，例如自带内部时长与冷却计时器的 ``apply_body_impulse``。由于 step 事件每步都会运行，它们应当足够轻量，或者在内部自行管理激活逻辑，以避免不必要的计算。

与其他所有管理器项一样，``func`` 指向可调用对象，``params`` 保存会连同 ``env`` 和 ``env_ids`` 一起转发给它的关键字参数。``params`` 中的所有 ``SceneEntityCfg`` 值都在管理器构造时解析一次（正则模式在该时点匹配到模型索引，而不是每次调用时才匹配）。项可以是普通函数，也可以是类；通用模式参见 :ref:`env-config-term-pattern` 一节。


内置事件函数
------------

以下函数可在 ``mjlab.envs.mdp.events`` 中使用。

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - 函数
     - 描述
   * - ``reset_scene_to_default``
     - 将所有实体重置到默认状态：浮动基 (floating-base) 实体的根位姿与速度、固定基实体的 mocap 位姿，以及铰接实体的关节位置与速度。环境原点会自动应用。这是 ``ManagerBasedRlEnvCfg`` 的默认事件；大多数环境会保留它，并在其基础上追加其他项。
   * - ``reset_root_state_uniform``
     - 以相对默认值的均匀随机偏移重置单个实体的根位姿与速度。接受 ``pose_range`` 和 ``velocity_range`` 字典，键为 ``"x"`` / ``"y"`` / ``"z"`` / ``"roll"`` / ``"pitch"`` / ``"yaw"``。姿态扰动与默认四元数复合。对于固定基机器人，这是把它们放置到各自环境原点的唯一方式；否则它们会堆叠在世界原点。
   * - ``reset_root_state_from_flat_patches``
     - 根据环境被分配的地形等级和类型，把实体放置到随机选取的平坦地形块上。当没有可用的平坦地块时，回退到 ``reset_root_state_uniform``。适用于机器人应在其被分配的子地形内、在平整地面上生成的移动任务。
   * - ``reset_joints_by_offset``
     - 在实体默认关节位置和速度的基础上叠加均匀随机偏移来重置关节，并钳位到软关节限位。
   * - ``push_by_setting_velocity``
     - 在实体当前根速度上叠加一个随机速度增量，模拟外部推动。通常与 ``mode="interval"`` 搭配使用，以测试抗扰能力。
   * - ``apply_external_force_torque``
     - 通过 MuJoCo 外部 wrench 机制对一个或多个 body 施加随机力和力矩。
   * - ``apply_body_impulse``
     - 对 body 施加持续短暂的外部 wrench，时长与冷却均可配置。每个环境独立采样一个随机力方向并保持采样得到的时长，然后经过冷却期后再次触发。支持可选的 ``body_point_offset``，把施力点从质心移开。内置调试可视化，可在查看器中绘制力箭头。请与 ``mode="step"`` 搭配使用。
   * - ``randomize_terrain``
     - 把每个环境分配到随机的子地形行和列，忽略课程。适用于评估或 play 模式。


编写自定义事件项
----------------

事件函数的前两个参数是 ``env`` 和 ``env_ids``，其余参数来自 ``EventTermCfg.params``。它直接修改仿真状态，不返回任何值。对于需要一次性昂贵初始化的项（例如从磁盘加载数据），请将其实现为类，使初始化只在构造时执行一次，而不是每次调用都执行。例如，下面这个自定义事件项会把机器人重置为从预先录制的数据集中采样出的随机位姿：

.. code-block:: python

    import torch
    from mjlab.managers.manager_base import ManagerTermBase
    from mjlab.managers.scene_entity_config import SceneEntityCfg

    class ResetFromDataset(ManagerTermBase):
        """Reset the robot to a random pose from a dataset."""

        def __init__(self, cfg, env):
            super().__init__(env)
            self._robot = env.scene["robot"]
            self._poses = torch.load(
                cfg.params["dataset_path"],
                map_location=env.device,
            )

        def __call__(self, env, env_ids, **kwargs):
            # Sample with replacement: each env gets an independent pose.
            indices = torch.randint(
                len(self._poses), (len(env_ids),), device=env.device,
            )
            self._robot.write_joint_position_to_sim(
                self._poses[indices], env_ids=env_ids,
            )

当某个项需要维护状态或执行开销较大的初始化时，请将其实现为类。通用模式参见 :ref:`env-config-term-pattern` 一节。对于写入模型字段的自定义 DR 项，参见 :ref:`domain_randomization` 一节。
