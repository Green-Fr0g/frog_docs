.. _observations:

观测
============

观测定义了智能体在每一步感知到的内容。观测管理器将各个观测项（term，即配置字典中
登记的一个条目，每项绑定一个函数和它自己的配置，详见 :ref:`env-config-term-pattern`）
组装成策略接收的输入张量。每个观测项都会经过一条可配置的处理流水线：噪声注入、裁剪、
缩放、传感器延迟和历史堆叠。


观测组
------------------

每个组都是一个 ``ObservationGroupCfg``，其中包含一个 ``terms`` 字典，将字符串
名称映射到 ``ObservationTermCfg`` 条目。管理器按注册顺序沿最后一个维度拼接各组
项的输出。

.. code-block:: python

    from mjlab.managers.observation_manager import (
        ObservationGroupCfg,
        ObservationTermCfg,
    )
    from mjlab.envs.mdp import observations as obs_fns

    observations = {
        "policy": ObservationGroupCfg(
            terms={
                "base_lin_vel": ObservationTermCfg(func=obs_fns.base_lin_vel),
                "base_ang_vel": ObservationTermCfg(func=obs_fns.base_ang_vel),
                "projected_gravity": ObservationTermCfg(
                    func=obs_fns.projected_gravity
                ),
                "joint_pos": ObservationTermCfg(func=obs_fns.joint_pos_rel),
                "joint_vel": ObservationTermCfg(func=obs_fns.joint_vel_rel),
                "last_action": ObservationTermCfg(func=obs_fns.last_action),
            },
            enable_corruption=True,
        ),
    }

该字典被传递给 ``ManagerBasedRlEnvCfg(observations=...)``。观测管理器在初始化时
解析各项函数，并在那时分配所需的任何历史或延迟缓冲区。

默认情况下，组内各观测项的输出沿最后一个维度拼接成一个 ``[num_envs, D]``
张量。设置 ``concatenate_terms=False`` 则会返回一个将观测项名称映射到各自张量的
字典。

``enable_corruption`` 标志控制整个组的噪声应用：当为 ``False`` 时，各观测项上的
噪声配置会被忽略。这使得在带噪声的 actor 组与无噪声的 critic 组之间共享观测项
定义变得非常直接，如下文 :ref:`非对称 actor-critic <obs-asymmetric>` 一节所示。

历史和延迟也可以在组级别设置，从而统一应用于所有观测项；参见
:ref:`obs-history-delay`。


处理流水线
-------------------

每一步中，每个组中的每个观测项都按顺序经过以下流水线：

.. code-block:: text

    compute → noise → clip → scale → delay → history

1. **compute**：调用观测项函数。它必须返回一个 ``[num_envs, D]`` 张量。

2. **noise**：如果组上设置了 ``enable_corruption=True`` 且该观测项具有 ``noise``
   配置，则应用噪声。无状态噪声（``NoiseCfg``）直接应用；有状态噪声
   （``NoiseModelCfg``）由管理器跨步骤维护。

3. **clip**：如果观测项上设置了 ``clip=(lo, hi)``，则将数值裁剪到该范围。

4. **scale**：如果设置了 ``scale``，则按元素相乘。接受标量、元组或张量。

5. **delay**：如果 ``delay_max_lag > 0``，观测项的输出会被存入环形缓冲区，
   并返回来自较早步骤的值。参见 :ref:`obs-history-delay`。

6. **history**：如果 ``history_length > 0``，则堆叠过去的输出。参见
   :ref:`obs-history-delay`。

.. note::

   延迟在历史之前应用。这模拟了真实系统中旧传感器读数被缓冲的情况：历史堆叠
   的是延迟后的观测，而不是未来的观测。


.. _obs-history-delay:

观测历史与延迟
------------------------------

观测支持两个时序特性：历史和延迟。历史堆叠过去的帧，为策略提供时间上下文；
延迟通过返回较早时间步的观测来建模传感器延迟。

两者都通过 ``ObservationTermCfg`` 上的字段按观测项进行配置。它们也可以在
``ObservationGroupCfg`` 上的组级别设置，从而统一应用于组内的所有观测项。
观测项级别的设置会覆盖组级别的设置。

历史
^^^^^^^

设置 ``history_length=N`` 会把一个观测项最近 N 个输出堆叠起来。当
``flatten_history_dim=True`` （默认值）时，历史维度被折叠进特征维度，产生适合
MLP 的 ``[num_envs, N * D]`` 张量。当 ``flatten_history_dim=False`` 时，输出保留
时间维度，形如 ``[num_envs, N, D]``，适合 RNN。

历史缓冲区会在环境重置时被清空。重置后的第一个观测会回填到所有历史槽位中，
因此策略从第零步开始就能收到有效数据。

当 ``flatten_history_dim=True`` 且 ``concatenate_terms=True`` 时，mjlab 使用
**term-major** 排序：先展平每个观测项的完整历史，再跨观测项拼接。

.. code-block:: text

    Term A (D=4, history=3), Term B (D=2, history=3):
    [A_t0, A_t1, A_t2, B_t0, B_t1, B_t2]
     └─ A history ──┘  └─ B history ─┘

有些框架改用 **time-major** 排序，即在每个时间步先构建完整帧，再沿时间维度
拼接。在具有不同排序的框架之间迁移策略时，需要对观测向量重新排序索引。

延迟
^^^^^

设置 ``delay_max_lag > 0`` 会启用一个环形缓冲区，用于存储过去的输出并返回其中
较早的一个。滞后量以整数步从 ``[delay_min_lag, delay_max_lag]`` 中均匀采样。
滞后为零返回当前观测；滞后为二返回两步之前的观测。

.. code-block:: text

    50Hz control (20ms/step), lag=2:

    Sensor captures:  A     B     C     D     E     F     G     H
    Control steps:    0     1     2     3     4     5     6     7

    Policy sees:      A     A     A     B     C     D     E     F
                      └clamp┘     └ 40ms delay from here on

    Steps 0-1: lag clamped because the buffer is not yet full.
    Step 2 onward: each step returns the observation from 2 steps ago.

将现实世界的延迟换算为滞后步数：``lag = latency_seconds / step_dt``。在
50 Hz 控制（每步 20 ms）下，40 ms 的传感器延迟对应滞后 2。延迟被量化为整数步；
要近似落在两步之间的延迟，可将 ``delay_min_lag`` 和 ``delay_max_lag`` 设为最
接近的两个整数。

默认情况下，每个环境独立采样自己的滞后（``delay_per_env=True``）。其他参数
控制重采样频率（``delay_update_period``）、保持概率（``delay_hold_prob``）
以及相位错开（``delay_per_env_phase``）。

历史和延迟缓冲区都只在启用时才分配；使用默认设置的观测项不会产生额外开销。


内置观测函数
--------------------------------

以下函数位于 ``mjlab.envs.mdp.observations`` （同时通过 ``mjlab.envs.mdp``
再导出）。它们都返回 ``[num_envs, D]`` 张量。

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - 函数
     - 描述
   * - ``base_lin_vel``
     - 机器人基座在本体系（base frame）中的线速度。
   * - ``base_ang_vel``
     - 机器人基座在本体系中的角速度。
   * - ``projected_gravity``
     - 投影到本体系中的重力向量。无需显式的姿态表示即可提供横滚与俯仰信息。
   * - ``joint_pos_rel``
     - 相对默认位姿的关节位置。传入 ``biased=True`` 可获得带编码器偏置的位置
       （配合 ``dr.encoder_bias`` 做 sim2real）。
   * - ``joint_vel_rel``
     - 相对默认速度的关节速度。
   * - ``last_action``
     - 最近一次的动作张量。可选传入 ``action_name`` 以选择单个动作项。
   * - ``generated_commands``
     - 来自指定指令项的当前指令张量。需要 ``params={"command_name": "<name>"}``。
   * - ``builtin_sensor``
     - 指定 ``BuiltinSensor`` 的原始数据（MuJoCo ``sensordata`` 切片）。需要
       ``params={"sensor_name": "<entity>/<sensor>"}``。
   * - ``height_scan``
     - 来自 ``RayCastSensor`` 的各光线击中点上方的高度。需要
       ``params={"sensor_name": "<name>"}``。

对于 ``builtin_sensor`` 和 ``height_scan``，``sensor_name`` 参数必须与场景中
注册的某个传感器匹配。传感器的配置方式请参阅 :ref:`sensors`。


.. _obs-asymmetric:

非对称 actor-critic
-----------------------

多个观测组可以实现非对称 actor-critic 架构。actor 组只包含真实硬件上可获取的
观测；critic 组则可以包含仅在训练期间可访问的特权仿真状态。

速度运动任务采用了这种模式。actor 组接收带噪声的 IMU 读数和关节状态；critic
组则额外加入无噪声的高度扫描数据和足部接触信息。``enable_corruption`` 标志使
这种分离非常干净：actor 的观测项携带噪声配置，而 critic 组将噪声完全禁用。

.. code-block:: python

    observations = {
        "actor": ObservationGroupCfg(
            terms=actor_terms,
            concatenate_terms=True,
            enable_corruption=True,   # Noise active during training.
        ),
        "critic": ObservationGroupCfg(
            terms={**actor_terms, **privileged_terms},
            concatenate_terms=True,
            enable_corruption=False,  # No noise on critic.
        ),
    }

训练框架会接收这两个组。策略网络在推理时读取 ``obs["actor"]``；价值网络仅在
训练期间读取 ``obs["critic"]``。


编写自定义观测函数
--------------------------------------

观测函数接受 ``env`` 作为第一个参数，并返回一个 ``[num_envs, D]`` 张量。额外的
参数声明为函数参数，并通过 ``ObservationTermCfg(params={...})`` 提供。

.. code-block:: python

    import torch
    from mjlab.envs import ManagerBasedRlEnv
    from mjlab.managers.scene_entity_config import SceneEntityCfg


    def my_observation(
        env: ManagerBasedRlEnv,
        asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
    ) -> torch.Tensor:
        robot = env.scene[asset_cfg.name]
        return robot.data.root_lin_vel_b

当某个观测项需要缓存设置工作或维护每回合状态时，可将其实现为一个类，提供
``__init__(self, cfg, env)`` 和 ``__call__(self, env, ...)``。如果该类具有
``reset(env_ids)`` 方法，管理器会在回合重置时自动调用它。一般模式请参阅
:ref:`env-config-term-pattern`。
