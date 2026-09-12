基于种群的训练（Population Based Training）
===========================================

PBT 做什么
----------
* 在 **同一任务** 上并行训练 *N* 个策略（一个“种群”）。
* 每隔 ``interval_steps`` 步：

  #. 保存每个策略的检查点和目标值。
  #. 对种群进行评分，识别 **领导者** 和 **表现不佳者** 。
  #. 对于表现不佳者，用随机选取的领导者的权重替换其权重，并 **变异** 选定的超参数。
  #. 自动使用新的权重/参数重启该进程。

领导者与表现不佳者的选择
---------------------------------

设 ``o_i`` 为每个已初始化策略的目标值，其均值为 ``μ`` ，标准差为 ``σ`` 。

性能上下界的截断值定义如下： ::

  upper_cut = max(μ + threshold_std * σ, μ + threshold_abs)
  lower_cut = min(μ - threshold_std * σ, μ - threshold_abs)

* **领导者** ： ``o_i > upper_cut``
* **表现不佳者** ： ``o_i < lower_cut``

“自然选择”规则：

1. 只对表现不佳者进行操作（变异或替换）。
2. 如果存在领导者，则用随机选取的领导者替换表现不佳者；否则，进行自我变异。

变异（超参数）
--------------------------

* 每个参数都有一个变异函数（例如 ``mutate_float`` 、 ``mutate_discount`` 等）。
* 参数以 ``mutation_rate`` 的概率被变异。
* 当被变异时，其值会在 ``change_range = (min, max)`` 范围内受到扰动。
* 只考虑白名单中的键（来自 PBT 配置）。

配置示例
--------------

.. code-block:: yaml

   pbt:
     enabled: True
     policy_idx: 0
     num_policies: 8
     directory: .
     workspace: "pbt_workspace"
     objective: episode.Curriculum/difficulty_level
     interval_steps: 50000000
     threshold_std: 0.1
     threshold_abs: 0.025
     mutation_rate: 0.25
     change_range: [1.1, 2.0]
     mutation:
       agent.params.config.learning_rate: "mutate_float"
       agent.params.config.grad_norm: "mutate_float"
       agent.params.config.entropy_coef: "mutate_float"
       agent.params.config.critic_coef: "mutate_float"
       agent.params.config.bounds_loss_coef: "mutate_float"
       agent.params.config.kl_threshold: "mutate_float"
       agent.params.config.gamma: "mutate_discount"
       agent.params.config.tau: "mutate_discount"


``objective: episode.Curriculum/difficulty_level`` 是一个点分表达式，它使用
``infos["episode"]["Curriculum/difficulty_level"]`` 作为标量来 **对策略进行排序** （值越高越好）。
使用 ``num_policies: 8`` 时，将启动八个进程，它们共享相同的 ``workspace`` 并拥有各自唯一的 ``policy_idx`` （0-7）。


启动 PBT
-------------

你必须为每个策略启动 **一个进程** ，并将它们指向 **同一个工作区** 。为每个进程设置唯一的
``policy_idx`` 以及共同的 ``num_policies`` 。

所需的最小参数集：

* ``agent.pbt.enabled=True``
* ``agent.pbt.directory=<path/to/shared_folder>``
* ``agent.pbt.policy_idx=<0..num_policies-1>``

.. note::
   所有进程必须使用相同的 ``agent.pbt.workspace`` ，以便它们能看到彼此的检查点。

.. caution::
   PBT 目前 **仅** 支持 **rl_games** 库。尚不支持其他 RL 库。

技巧
----
* 保持合理的检查点设置：只有在确实需要更紧凑的 PBT 节奏时才减小 ``interval_steps`` 。
* 使用更大的 ``threshold_std`` 和 ``threshold_abs`` 以获得更大的种群多样性。
* 建议运行 6 个以上的 worker，以体现 pbt 的收益。


训练示例
----------------

我们在此为任务
`Isaac-Dexsuite-Kuka-Allegro-Lift-v0 <https://github.com/isaac-sim/IsaacLab/blob/main/source/isaaclab_tasks/isaaclab_tasks/manager_based/manipulation/dexsuite/config/kuka_allegro/agents/rl_games_ppo_cfg.yaml>`_
提供了参考 PPO 配置。为获得最佳的日志体验，我们建议在脚本中使用 wandb 进行日志记录。

启动 *N* 个 worker，其中 *n* 表示每个 worker 的索引：

.. code-block:: bash

   # Run this once per worker (n = 0..N-1), all pointing to the same directory/workspace
   ./isaaclab.sh -p scripts/reinforcement_learning/rl_games/train.py \
     --seed=<n> \
     --task=Isaac-Dexsuite-Kuka-Allegro-Lift-v0 \
     --num_envs=8192 \
     --headless \
     --track \
     --wandb-name=idx<n> \
     --wandb-entity=<**entity**> \
     --wandb-project-name=<**project**>
     agent.pbt.enabled=True \
     agent.pbt.num_policies=<N> \
     agent.pbt.policy_idx=<n> \
     agent.pbt.workspace=<**pbt_workspace_name**> \
     agent.pbt.directory=<**/path/to/shared_folder**>


参考文献
----------

该 PBT 实现重新实现并受启发于 *Dexpbt: Scaling up dexterous manipulation for hand-arm systems with population based training* （Petrenko et al., 2023）。

.. code-block:: bibtex

   @article{petrenko2023dexpbt,
     title={Dexpbt: Scaling up dexterous manipulation for hand-arm systems with population based training},
     author={Petrenko, Aleksei and Allshire, Arthur and State, Gavriel and Handa, Ankur and Makoviychuk, Viktor},
     journal={arXiv preprint arXiv:2305.12127},
     year={2023}
   }
