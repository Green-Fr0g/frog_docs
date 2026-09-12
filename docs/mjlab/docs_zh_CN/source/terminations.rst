.. _terminations:

终止
============

终止项定义了回合何时结束。每个终止项都是一个函数，每步为每个环境返回一个布尔值
的张量。终止管理器聚合所有终止项，并将结果作为终端失败或截断报告给训练框架。

每个终止项通过 ``TerminationTermCfg`` 按名称注册。设置 ``time_out=True`` 会将该
条件标记为截断而非终端失败。截断对应 Gym 接口中的 ``truncated`` 信号；失败对应
``terminated``。这一区别对价值自举（value bootstrapping）很重要：智能体应当在
截断之后估计未来价值，但在失败之后则不应如此。

.. code-block:: python

    from mjlab.envs.mdp import terminations
    from mjlab.managers.termination_manager import TerminationTermCfg

    terminations_cfg = {
        "time_out": TerminationTermCfg(
            func=terminations.time_out, time_out=True,
        ),
        "fallen": TerminationTermCfg(
            func=terminations.bad_orientation,
            params={"limit_angle": 1.0},
        ),
    }


内置终止函数
-------------------------------

以下函数位于 ``mjlab.envs.mdp.terminations`` 中，并在各任务间共享。单个任务可以
针对自身目标定义额外的终止函数。所有终止函数都返回形状为 ``[num_envs]`` 的布尔
张量。

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - 函数
     - 描述
   * - ``time_out``
     - 当回合长度达到 ``env.max_episode_length`` 时返回 ``True``。注册时应设置
       ``time_out=True``，以便管理器将其视为截断。
   * - ``bad_orientation``
     - 当实体的上轴与世界竖直方向之间的夹角超过 ``limit_angle`` （弧度）时返回
       ``True``。
   * - ``root_height_below_minimum``
     - 当实体的根连杆高度低于 ``minimum_height`` （米）时返回 ``True``。
   * - ``nan_detection``
     - 当物理状态中任何位置出现 NaN 或 Inf 值时返回 ``True``。这是一个安全网，
       用于干净地终止已经发散的仿真。


编写自定义终止函数
-------------------------------------

自定义终止函数遵循与奖励函数相同的模式。普通函数接受 ``env`` 并返回一个布尔
``[num_envs]`` 张量。一般模式请参阅 :ref:`env-config-term-pattern`。
