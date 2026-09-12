.. _rl-frameworks:

强化学习库对比
=========================================

在本节中，我们将概述 Isaac Lab 支持的强化学习库，
并对各个库进行性能基准测试对比。

支持的库包括：

- `SKRL <https://skrl.readthedocs.io>`__
- `RSL-RL <https://github.com/leggedrobotics/rsl_rl>`__
- `RL-Games <https://github.com/Denys88/rl_games>`__
- `Stable-Baselines3 <https://stable-baselines3.readthedocs.io/en/master/index.html>`__

功能对比
------------------

.. list-table::
   :widths: 20 20 20 20 20
   :header-rows: 1

   * - 功能
     - RL-Games
     - RSL RL
     - SKRL
     - Stable Baselines3
   * - 包含的算法
     - PPO, SAC, A2C
     - PPO, 蒸馏
     - `丰富的算法列表 <https://skrl.readthedocs.io/en/latest/#agents>`__
     - `丰富的算法列表 <https://github.com/DLR-RM/stable-baselines3?tab=readme-ov-file#implemented-algorithms>`__
   * - 向量化训练
     - 是
     - 是
     - 是
     - 否
   * - 分布式训练
     - 是
     - 是
     - 是
     - 否
   * - 支持的 ML 框架
     - PyTorch
     - PyTorch
     - PyTorch, JAX
     - PyTorch
   * - 多智能体支持
     - PPO
     - PPO
     - PPO + 多智能体算法
     - 由外部项目支持
   * - 文档
     - 较少
     - 较少
     - 全面
     - 丰富
   * - 社区支持
     - 社区较小
     - 社区较小
     - 社区较小
     - 社区庞大
   * - Isaac Lab 中的可用示例
     - 多
     - 多
     - 多
     - 少


训练性能
--------------------

我们在单个 NVIDIA GeForce RTX 4090 上使用 ``--headless`` 参数，在相同的
``Isaac-Humanoid-v0`` 环境中使用各个 RL 库进行训练，并记录了 65.5M 步
（4096 个环境 x 32 个 rollout 步 x 500 次迭代）的总训练时间。

+--------------------+-----------------+
| RL 库              | 时间（秒）      |
+====================+=================+
| RL-Games           | 201             |
+--------------------+-----------------+
| SKRL               | 201             |
+--------------------+-----------------+
| RSL RL             | 198             |
+--------------------+-----------------+
| Stable-Baselines3  | 287             |
+--------------------+-----------------+

训练命令（请在终端输出中查看 *'Training time: XXX seconds'* 一行）：

.. code:: bash

    python scripts/reinforcement_learning/rl_games/train.py --task Isaac-Humanoid-v0 --max_iterations 500 --headless
    python scripts/reinforcement_learning/skrl/train.py --task Isaac-Humanoid-v0 --max_iterations 500 --headless
    python scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Humanoid-v0 --max_iterations 500 --headless
    python scripts/reinforcement_learning/sb3/train.py --task Isaac-Humanoid-v0 --max_iterations 500 --headless
