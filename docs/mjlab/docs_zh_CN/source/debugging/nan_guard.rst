.. _nan-guard:

NaN 守护
========

NaN 守护 (NaN guard) 会在检测到 NaN/Inf 时捕获仿真状态，帮助调试数值不稳定问题。


快速开始
--------

用一个 CLI 标志即可启用 NaN 守护：

.. code-block:: bash

    uv run train <task-name> --enable-nan-guard True

检测到 NaN/Inf 时会自动捕获并保存仿真状态。也可以通过编程方式启用：

.. code-block:: python

    from mjlab.sim.sim import SimulationCfg
    from mjlab.utils.nan_guard import NanGuardCfg

    cfg = SimulationCfg(
        nan_guard=NanGuardCfg(
            enabled=True,
            buffer_size=100,
            output_dir="/tmp/mjlab/nan_dumps",
            max_envs_to_dump=5,
        ),
    )


配置
----

``enabled`` *(default: False)*
    启用/禁用 NaN 检测与转储。

``buffer_size`` *(default: 100)*
    滚动缓冲区中保留的最近仿真状态数量。

``output_dir`` *(default: "/tmp/mjlab/nan_dumps")*
    NaN 转储文件的保存目录。

``max_envs_to_dump`` *(default: 5)*
    转储到磁盘的 NaN 环境数量上限。所有环境都会被跟踪进缓冲区，但只有前 N 个会被保存，以减小转储体积。


行为
----

- **捕获** 每一步之前的仿真状态 (``qpos``, ``qvel``；若模型含执行器激活则还有 ``act``，若模型含 mocap body 则还有 ``mocap_pos``/``mocap_quat``)
- **检测** 每一步之后 ``qpos``, ``qvel``, ``qacc``, ``qacc_warmstart``, ``sensordata`` 中的 NaN/Inf
- **转储** 首次检测到时，把滚动缓冲区和模型转储到磁盘
- **停止** 首次转储后即停止，避免刷屏

禁用时所有操作都是空操作，开销可以忽略不计。


输出格式
--------

每次检测到 NaN 都会生成带时间戳的文件，以及指向最新文件的符号链接：

- ``nan_dump_TIMESTAMP.npz``: 压缩的状态缓冲区

  - ``states_step_NNNNNN``: 每步捕获的状态 (形状为 ``[num_envs_dumped, state_size]``)
  - ``_metadata``: 包含 ``num_envs_total``, ``nan_env_ids``, ``dumped_env_ids`` 等字段的字典

- ``model_TIMESTAMP.mjb``: 二进制格式的 MuJoCo 模型
- ``nan_dump_latest.npz``: 指向最近一次转储的符号链接
- ``model_latest.mjb``: 指向最新模型的符号链接


可视化转储
----------

使用交互式查看器浏览捕获的状态：

.. code-block:: bash

    # View latest dump.
    uv run viz-nan /tmp/mjlab/nan_dumps/nan_dump_latest.npz

    # View a specific dump.
    uv run viz-nan /tmp/mjlab/nan_dumps/nan_dump_20251014_123456.npz


.. figure:: ../_static/content/nan_debug.gif
   :alt: NaN 调试查看器

   NaN 调试查看器。

查看器提供：

- 步数滑块，用于在缓冲区中前后浏览
- 环境滑块，用于比较不同环境
- 信息面板，显示哪些环境存在 NaN/Inf
- 每个状态下机器人与地形的三维可视化


NaN 检测终止
------------

NaN 守护通过捕获状态帮助 **调试** NaN 问题；此外，你还可以使用 ``nan_detection`` 终止项来 **预防** 训练崩溃。它会把出现 NaN 的环境标记为终止，使其得以重置，而训练继续进行：

.. code-block:: python

    from mjlab.envs.mdp.terminations import nan_detection
    from mjlab.managers.termination_manager import TerminationTermCfg

    nan_term: TerminationTermCfg = field(
        default_factory=lambda: TerminationTermCfg(
            func=nan_detection,
            time_out=False,
        )
    )

终止情况会以 ``Episode_Termination/nan_term`` 为名记录到你的指标中。

.. important::

   ``nan_detection`` 是权宜之计，而非根治之道。如果 NaN 出现在任务目标本身（例如抓取时发生 NaN），策略将永远学不会完成任务，因为它会在获得奖励之前就被重置。请密切关注 ``Episode_Termination/nan_term`` 指标。

**何时使用哪一个：**

- ``nan_guard``: 调试并弄清 NaN 为何出现（请务必先做这一步）
- ``nan_detection``: 在着手永久修复期间保持训练稳定
