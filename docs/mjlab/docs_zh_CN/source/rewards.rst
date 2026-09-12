.. _rewards:

奖励
====

奖励是塑造策略行为的训练信号。每个奖励项（term）都是一个函数，每步为每个环境返回一个标量。奖励管理器计算所有项的加权和，并把结果返回给训练框架。

每一项都以名称注册，对应的 ``RewardTermCfg`` 携带可调用对象和一个 ``weight``。负权重会产生惩罚。额外的关键字参数通过 ``params`` 提供。

.. code-block:: python

    from mjlab.envs.mdp import rewards
    from mjlab.managers.reward_manager import RewardTermCfg
    from mjlab.managers.scene_entity_config import SceneEntityCfg

    rewards_cfg = {
        "alive": RewardTermCfg(func=rewards.is_alive, weight=1.0),
        "joint_torques": RewardTermCfg(
            func=rewards.joint_torques_l2,
            weight=-1e-4,
            params={"asset_cfg": SceneEntityCfg("robot")},
        ),
    }


内置奖励函数
------------

以下函数可在 ``mjlab.envs.mdp.rewards`` 中使用，并在各任务之间共享。单个任务还会定义自己的、针对任务目标定制的奖励函数（例如移动任务的速度跟踪）。所有奖励函数都返回形状为 ``[num_envs]`` 的张量。

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - 函数
     - 描述
   * - ``is_alive``
     - 对本步尚未终止的环境返回 ``1.0``。以正权重使用，作为生存奖励。
   * - ``is_terminated``
     - 对因非超时条件而终止的环境返回 ``1.0``。以负权重使用，惩罚失败。
   * - ``joint_torques_l2``
     - 执行器力的平方和。惩罚高能耗的动作。
   * - ``joint_vel_l2``
     - 关节速度的平方和。
   * - ``joint_acc_l2``
     - 关节加速度的平方和。
   * - ``action_rate_l2``
     - 当前动作与上一步动作之差的平方和。惩罚策略输出的剧烈变化。
   * - ``action_acc_l2``
     - 动作二阶差分的平方和。惩罚动作信号中的高频抖动。
   * - ``joint_pos_limits``
     - 对超出软限位的关节位置的惩罚。所有关节都在限位内时为零。
   * - ``posture`` *(class)*
     - 以指数核度量相对默认关节位置的偏差：``exp(-mean(error^2 / std^2))``。
   * - ``electrical_power_cost`` *(class)*
     - 执行器消耗的正机械功率之和。再生功率不计入惩罚。
   * - ``flat_orientation_l2``
     - 投影重力向量在基座坐标系下 x、y 分量的平方和。完全竖直时为零。


按 dt 缩放奖励
--------------

``ManagerBasedRlEnvCfg.scale_rewards_by_dt`` 默认为 ``True``。启用后，奖励管理器在累加之前会把每一项乘以环境步的时长。这使得回合奖励总量与仿真频率无关：以 50 Hz 运行的任务与以 200 Hz 运行的同一任务产生相同的期望回合回报，因为每步对总量的贡献按比例变小。

各项的回合累加值会以 ``Episode_Reward/<term_name>`` 为名记录，并且总是除以回合时长，得到一个可在不同回合长度的运行之间比较的奖励速率。


编写自定义奖励函数
------------------

奖励函数的第一个参数是 ``env``，返回一个 ``[num_envs]`` 张量。额外的参数声明为函数参数，并通过 ``RewardTermCfg(params={...})`` 提供。当某个项需要缓存初始化结果或维护回合级状态时，请将其实现为类。通用模式参见 :ref:`env-config-term-pattern` 一节。
