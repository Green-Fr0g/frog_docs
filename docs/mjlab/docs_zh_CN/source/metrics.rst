.. _metrics:

指标
=======

指标管理器将每步的标量值以回合平均值的形式记录下来。与奖励不同，指标不带权重，
也不会按步长进行缩放。它们纯粹用于诊断：在不影响优化的情况下，与奖励曲线一起
跟踪诸如跟踪误差、接触力或能耗之类的量。

指标在每个环境步计算，按环境累加，并在环境重置时对回合长度求平均。得到的平均值
以 ``Episode_Metrics/`` 前缀写入训练日志记录器（TensorBoard 或
Weights & Biases）。

如果 ``ManagerBasedRlEnvCfg`` 上的 ``metrics`` 字典为空，环境会替换为一个轻量的
no-op 管理器，开销为零。


注册
------------

每个指标项通过名称注册到 ``ManagerBasedRlEnvCfg`` 的 ``metrics`` 字典中。其配置
非常精简：一个可调用对象和一个可选的 ``params`` 字典。

.. code-block:: python

    from mjlab.managers.metrics_manager import MetricsTermCfg

    metrics = {
        "base_height": MetricsTermCfg(
            func=base_height,
            params={"asset_cfg": SceneEntityCfg("robot")},
        ),
    }

该可调用对象接收 ``env`` 作为第一个参数，``params`` 中的条目则作为关键字参数传入。
它必须返回一个形状为 ``[num_envs]`` 的张量，即每步每个环境一个标量。


指标的计算方式
-------------------------

管理器为每个环境维护一个累计和与一个步数计数器。每次调用 ``compute()`` 时：

1. 所有环境的步数计数器递增。
2. 以当前环境状态调用每个指标项函数。
3. 返回的逐环境值会被累加到累计和中。

当某个环境重置时，管理器将每个指标项的累计值归约为一个标量，对所有正在重置的
环境求平均，并以 ``Episode_Metrics/<term_name>`` 为键返回。随后，这些累计和与
计数器会被清零（针对重置的环境）。

归约方式由 ``MetricsTermCfg`` 上的 ``reduce`` 字段控制：

- ``"mean"`` （默认）：将累计和除以每个环境的步数。除法按环境独立进行，因此提前
  终止的环境不会被运行更久的环境稀释。
- ``"last"``：报告回合最后一步的值。这适用于不应随时间平均的二元成功指标
  （例如机器人是否站立）。

这些标量经由 ``env.extras["log"]`` 流入训练 runner，由其写入所配置的日志记录器。
在典型的训练运行中，它们显示为：

.. code-block:: text

    Episode_Metrics/base_height
    Episode_Metrics/contact_force

与奖励管理器产生的 ``Episode_Reward/`` 条目并列。


编写自定义指标函数
--------------------------------

指标函数遵循与奖励函数和观测函数相同的模式。它以环境作为第一个参数，读取所需的
任意状态，并返回一个 ``[num_envs]`` 张量。

.. code-block:: python

    import torch
    from mjlab.envs import ManagerBasedRlEnv
    from mjlab.managers.scene_entity_config import SceneEntityCfg

    def base_height(
        env: ManagerBasedRlEnv,
        asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
    ) -> torch.Tensor:
        robot = env.scene[asset_cfg.name]
        return robot.data.root_link_pos_w[:, 2]

对于需要缓存设置或每回合状态的指标，可将该指标项实现为一个类，提供
``__init__(self, cfg, env)`` 和一个 ``__call__`` 方法。如果该类定义了
``reset(env_ids)`` 方法，管理器会在回合重置时自动调用它。
