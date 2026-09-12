.. _rsl_rl:

使用 RSL-RL 进行训练
====================

mjlab 使用 `RSL-RL <https://github.com/leggedrobotics/rsl_rl>`_ 进行
on-policy 强化学习。集成由三部分组成：**任务注册表** 把环境配置和训练配置
打包在一个名称之下；**VecEnv 封装器** 把 mjlab 环境适配成 RSL-RL 期望的
接口；以及一组 **配置 dataclass** ，用于控制训练运行。


任务注册
--------

mjlab 中的每个任务都是一个二元组：环境配置 (``ManagerBasedRlEnvCfg``) 和
训练配置 (``RslRlOnPolicyRunnerCfg``)。任务注册表把一个字符串名称映射到这
对配置，从而可以从 CLI 按名称启动训练。

任务通过在任务的 ``__init__.py`` 中调用 ``register_mjlab_task`` 来注册：

.. code-block:: python

    from mjlab.tasks.registry import register_mjlab_task
    from mjlab.tasks.velocity.rl import VelocityOnPolicyRunner

    from .env_cfgs import unitree_g1_rough_env_cfg, unitree_g1_flat_env_cfg
    from .rl_cfg import unitree_g1_ppo_runner_cfg

    register_mjlab_task(
      task_id="Mjlab-Velocity-Rough-Unitree-G1",
      env_cfg=unitree_g1_rough_env_cfg(),
      play_env_cfg=unitree_g1_rough_env_cfg(play=True),
      rl_cfg=unitree_g1_ppo_runner_cfg(),
      runner_cls=VelocityOnPolicyRunner,
    )

每次注册需要提供：

- ``task_id`` ：遵循 ``Mjlab-{Category}-{Terrain}-{Robot}`` 命名约定的
  唯一名称
- ``env_cfg`` ：用于训练的 ``ManagerBasedRlEnvCfg``
- ``play_env_cfg`` ：关闭随机化并将回合长度设为无穷的变体，用于评估
- ``rl_cfg`` ：包含 PPO 超参数和网络结构的 ``RslRlOnPolicyRunnerCfg``
- ``runner_cls`` ：可选的自定义 runner 类 (默认为 ``MjlabOnPolicyRunner``)

``src/mjlab/tasks/`` 下的所有任务包都会在导入时被自动发现，因此新增任务
只需创建配置包并调用 ``register_mjlab_task``。


训练与回放
----------

**启动训练：**

.. code-block:: bash

    uv run train Mjlab-Velocity-Flat-Unitree-G1 --num-envs 4096

任务名是第一个位置参数。整个配置层级 (环境、场景、奖励、PPO 超参数等) 都
通过 `tyro <https://brentyi.github.io/tyro/>`_ 暴露为 CLI 标志。
``ManagerBasedRlEnvCfg`` 和 ``RslRlOnPolicyRunnerCfg`` 中的每个字段都可以
用点号分隔的路径在命令行上覆盖：

.. code-block:: bash

    uv run train Mjlab-Velocity-Flat-Unitree-G1 \
        --num-envs 4096 \
        --agent.max-iterations 10000 \
        --agent.algorithm.learning-rate 3e-4 \
        --env.decimation 2

.. important::

   - **用连字符，而非下划线** ：Python 字段名使用下划线 (``num_envs``) ，
     但 CLI 标志采用 POSIX 风格的连字符 (``--num-envs``) 。
   - **布尔值需显式给出** ：布尔标志必须显式写 ``True`` 或 ``False``
     (例如 ``--agent.resume True`` ，而不是 ``--agent.resume``) 。这是为了
     兼容 W&B sweep 配置而有意为之的。

要发现可用的标志，可以使用 ``--help`` 并通过 ``grep`` 过滤：

.. code-block:: bash

    # See all flags.
    uv run train Mjlab-Velocity-Flat-Unitree-G1 --help

    # Search for a specific field.
    uv run train Mjlab-Velocity-Flat-Unitree-G1 --help | grep learning-rate

一些常用的顶层标志：

``--num-envs``
    并行仿真环境的数量。

``--gpu-ids``
    要使用的 GPU 索引。传入多个索引即可进行多 GPU 训练 (参见
    :ref:`distributed-training`) ，或传 ``None`` 进入 CPU 模式。

``--video``
    将训练 rollout 视频录制到 ``{log_dir}/videos/train/`` 。

``--enable-nan-guard``
    启用 NaN 检测与状态捕获 (参见 :ref:`nan-guard`) 。


**回放训练好的策略：**

.. code-block:: bash

    # From W&B.
    uv run play Mjlab-Velocity-Flat-Unitree-G1 \
        --wandb-run-path your-entity/mjlab/run-id

    # From a local checkpoint.
    uv run play Mjlab-Velocity-Flat-Unitree-G1 \
        --checkpoint-file logs/rsl_rl/g1_velocity/2025-01-27_14-30-00/model_1000.pt

``play`` 的关键参数：

``--agent``
    策略模式： ``"trained"`` (默认)、 ``"zero"`` (零动作) 或 ``"random"``
    (均匀随机) 。

``--viewer``
    查看器后端： ``"native"`` (MuJoCo viewer) 或 ``"viser"``
    (基于浏览器) 。

``--no-terminations``
    禁用终止条件，让策略无限运行下去。


VecEnv 封装器
-------------

``RslRlVecEnvWrapper`` 将 ``ManagerBasedRlEnv`` 适配到 RSL-RL 的 ``VecEnv``
接口。它做三件事：

1. **观测格式** ：把观测字典转换成 RSL-RL 期望的 ``TensorDict`` 格式。
2. **结束信号** ：将 ``terminated`` 和 ``truncated`` 合并为单个 ``dones``
   张量，并通过 ``extras`` 传递 ``time_outs`` ，使 RSL-RL 能在截断的回合上
   正确进行 bootstrap。
3. **动作裁剪** ：当 runner 配置中设置了 ``clip_actions`` 时，应用可选的
   动作裁剪。

封装器还会在构造期间调用 ``env.reset()`` ，因为 RSL-RL 在开始采集 rollout
之前不会调用 reset。

在常规使用中你不需要直接与封装器交互，训练脚本会自动完成封装。


配置
----

``RslRlOnPolicyRunnerCfg`` 是顶层的训练配置。它将 runner 设置、网络结构
(``RslRlModelCfg``) 和 PPO 超参数 (``RslRlPpoAlgorithmCfg``) 组织在一起。
下面这个来自 Unitree G1 velocity 任务的示例展示了一个典型的配置：

.. code-block:: python

    from mjlab.rl import (
        RslRlModelCfg,
        RslRlOnPolicyRunnerCfg,
        RslRlPpoAlgorithmCfg,
    )

    def unitree_g1_ppo_runner_cfg() -> RslRlOnPolicyRunnerCfg:
        return RslRlOnPolicyRunnerCfg(
            actor=RslRlModelCfg(
                hidden_dims=(512, 256, 128),
                activation="elu",
                obs_normalization=True,
            ),
            critic=RslRlModelCfg(
                hidden_dims=(512, 256, 128),
                activation="elu",
                obs_normalization=True,
            ),
            algorithm=RslRlPpoAlgorithmCfg(
                value_loss_coef=1.0,
                use_clipped_value_loss=True,
                clip_param=0.2,
                entropy_coef=0.01,
                num_learning_epochs=5,
                num_mini_batches=4,
                learning_rate=1.0e-3,
                schedule="adaptive",
                gamma=0.99,
                lam=0.95,
                desired_kl=0.01,
                max_grad_norm=1.0,
            ),
            experiment_name="g1_velocity",
            save_interval=50,
            num_steps_per_env=24,
            max_iterations=30_000,
        )

所有字段都有合理的默认值，并且可以在命令行上覆盖 (例如
``--agent.algorithm.learning-rate 3e-4``)。使用 ``--help`` 可以查看全部
可用字段及其默认值。


检查点与日志
------------

训练产物会写入：

.. code-block:: text

    logs/rsl_rl/{experiment_name}/{timestamp}/
        model_{iteration}.pt      # policy checkpoints
        params/
            env.yaml              # full environment config
            agent.yaml            # full runner config

默认情况下，每隔 ``save_interval`` 次迭代保存一次检查点，并作为模型
artifact 上传到 W&B。若想在保留指标日志的同时禁用上传，可在 runner 配置
中设置 ``upload_model=False`` 。

.. rubric:: 从检查点恢复

.. code-block:: bash

    uv run train Mjlab-Velocity-Flat-Unitree-G1 \
        --num-envs 4096 \
        --agent.resume True

runner 会在 ``logs/rsl_rl/{experiment_name}/`` 下搜索最近的 run 目录，并
加载编号最大的检查点。可以用 ``--agent.load-run`` (对目录名做正则匹配) 和
``--agent.load-checkpoint`` (对检查点文件名做正则匹配) 来缩小搜索范围。

``--agent.max-iterations`` 控制从检查点继续时再运行多少 *额外* 的迭代。
如果你从第 11500 次迭代恢复，并使用 ``--agent.max-iterations 300`` (默认
值) ，训练将运行第 11500 到 11800 次迭代。把它设成你想要的新增迭代数
即可。

要从 W&B run 恢复：

.. code-block:: bash

    uv run train Mjlab-Velocity-Flat-Unitree-G1 \
        --num-envs 4096 \
        --agent.resume True \
        --wandb-run-path your-entity/mjlab/run-id


引用
----

如果你在研究中使用了 RSL-RL，请考虑引用：

.. code-block:: bibtex

    @article{schwarke2025rslrl,
        title={RSL-RL: A Learning Library for Robotics Research},
        author={Schwarke, Clemens and Mittal, Mayank and Rudin, Nikita and Hoeller, David and Hutter, Marco},
        journal={arXiv preprint arXiv:2509.10771},
        year={2025}
    }

.. toctree::
   :maxdepth: 1

   motion_imitation
