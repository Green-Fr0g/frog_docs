.. _tutorial-run-rl-training:

使用强化学习智能体训练
=========================

.. currentmodule:: isaaclab

在前面的教程中，我们介绍了如何定义强化学习任务环境、将其注册到
``gym`` 注册表中，并使用随机智能体与之交互。现在我们进入
下一步：训练一个强化学习智能体来解决该任务。

虽然 :class:`envs.ManagerBasedRLEnv` 符合 :class:`gymnasium.Env` 接口，
但它并不是一个严格意义上的 ``gym`` 环境。环境的输入和输出
不是 numpy 数组，而是基于 torch 张量，其第一维度为
环境实例的数量。

此外，大多数强化学习库期望各自版本的环境接口。
例如，`Stable-Baselines3`_ 期望环境符合其
`VecEnv API`_，它期望一个 numpy 数组列表而不是单个张量。类似地，
`RSL-RL`_、`RL-Games`_ 和 `SKRL`_ 期望不同的接口。由于不存在放之四海而皆准的
方案，我们不会将 :class:`envs.ManagerBasedRLEnv` 建立在某个特定的学习库之上。
相反，我们实现 wrapper 将环境转换为期望的接口。
这些 wrapper 在 :mod:`isaaclab_rl` 模块中指定。

在本教程中，我们将使用 `Stable-Baselines3`_ 训练一个强化学习智能体来解决
cartpole 平衡任务。

.. caution::

  使用相应学习框架的 wrapper 封装环境应当放在最后进行，
  即在所有其他 wrapper 都已应用之后。这是因为学习框架的 wrapper
  会修改环境 API 的解释方式，可能导致其不再与 :class:`gymnasium.Env` 兼容。

代码
--------

在本教程中，我们使用 ``scripts/reinforcement_learning/sb3`` 目录中
`Stable-Baselines3`_ 工作流的训练脚本。

.. dropdown:: Code for train.py
    :icon: code

    .. literalinclude:: ../../../../scripts/reinforcement_learning/sb3/train.py
      :language: python
      :emphasize-lines: 57, 66, 68-70, 81, 90-98, 100, 105-113, 115-116, 121-126, 133-136
      :linenos:

代码解析
------------------

.. currentmodule:: isaaclab_rl.utils

上面的大部分代码都是用于创建日志目录、保存解析后的配置
以及设置不同 Stable-Baselines3 组件的样板代码。对于本教程，重要的部分是创建
环境并用 Stable-Baselines3 wrapper 封装它。

上面的代码中使用了三个 wrapper：

1. :class:`gymnasium.wrappers.RecordVideo`：该 wrapper 录制环境的视频
   并保存到指定目录。这有助于在训练期间可视化智能体的行为。
2. :class:`wrappers.sb3.Sb3VecEnvWrapper`：该 wrapper 将环境
   转换为 Stable-Baselines3 兼容的环境。
3. `stable_baselines3.common.vec_env.VecNormalize`_：该 wrapper 对
   环境的观测和奖励进行归一化。

每个 wrapper 都按照 ``env = wrapper(env, *args, **kwargs)`` 的方式依次封装前一个 wrapper。
最终的环境随后用于训练智能体。有关这些 wrapper 工作原理的更多信息，请参阅 :ref:`how-to-env-wrappers` 文档。

代码执行
------------------

我们使用 Stable-Baselines3 的 PPO 智能体来解决 cartpole 平衡任务。

训练智能体
~~~~~~~~~~~~~~~~~~

训练智能体有三种主要方式。每种方式都有其优缺点。
你可以根据使用场景自行决定偏好哪一种。

无界面执行
""""""""""""""""""

如果设置了 ``--headless`` 标志，训练期间将不渲染仿真。这在
远程服务器上训练或不希望查看仿真时非常有用。通常，由于只执行物理仿真步，
它可以加快训练过程。

.. code-block:: bash

  ./isaaclab.sh -p scripts/reinforcement_learning/sb3/train.py --task Isaac-Cartpole-v0 --num_envs 64 --headless


无界面执行 + 离屏渲染
"""""""""""""""""""""""""""""""""""""""""""""""

由于上述命令不渲染仿真，因此无法在训练期间可视化智能体的
行为。要可视化智能体的行为，我们传入 ``--enable_cameras`` 来
启用离屏渲染。此外，我们传入 ``--video`` 标志，用于录制训练期间
智能体行为的视频。

.. code-block:: bash

  ./isaaclab.sh -p scripts/reinforcement_learning/sb3/train.py --task Isaac-Cartpole-v0 --num_envs 64 --headless --video

视频保存到 ``logs/sb3/Isaac-Cartpole-v0/<run-dir>/videos/train`` 目录。你可以使用任何视频播放器
打开这些视频。

交互式执行
"""""""""""""""""""""

.. currentmodule:: isaaclab

虽然上述两种方法对训练智能体很有用，但它们不允许你与
仿真交互以查看正在发生的情况。在这种情况下，你可以忽略 ``--headless`` 标志，按如下方式运行
训练脚本：

.. code-block:: bash

  ./isaaclab.sh -p scripts/reinforcement_learning/sb3/train.py --task Isaac-Cartpole-v0 --num_envs 64

这会打开 Isaac Sim 窗口，你可以看到智能体在环境中训练。不过，由于仿真是渲染在屏幕上的，
这会拖慢训练过程。作为一种变通办法，你可以停靠在屏幕右下角的
``"Isaac Lab"`` 窗口中切换不同的渲染模式。要了解有关这些渲染模式的更多信息，请查看
:class:`sim.SimulationContext.RenderMode` 类。

查看日志
~~~~~~~~~~~~~~~~

在另一个终端中，你可以通过执行以下命令来监控训练进度：

.. code:: bash

   # execute from the root directory of the repository
   ./isaaclab.sh -p -m tensorboard.main --logdir logs/sb3/Isaac-Cartpole-v0

运行训练好的智能体
~~~~~~~~~~~~~~~~~~~~~~~~~

训练完成后，你可以通过执行以下命令来可视化训练好的智能体：

.. code:: bash

   # execute from the root directory of the repository
   ./isaaclab.sh -p scripts/reinforcement_learning/sb3/play.py --task Isaac-Cartpole-v0 --num_envs 32 --use_last_checkpoint

上述命令会从 ``logs/sb3/Isaac-Cartpole-v0``
目录加载最新的检查点。你也可以通过传入 ``--checkpoint`` 标志来指定某个特定的检查点。

.. _Stable-Baselines3: https://stable-baselines3.readthedocs.io/en/master/
.. _VecEnv API: https://stable-baselines3.readthedocs.io/en/master/guide/vec_envs.html#vecenv-api-vs-gym-api
.. _`stable_baselines3.common.vec_env.VecNormalize`: https://stable-baselines3.readthedocs.io/en/master/guide/vec_envs.html#vecnormalize
.. _RL-Games: https://github.com/Denys88/rl_games
.. _RSL-RL: https://github.com/leggedrobotics/rsl_rl
.. _SKRL: https://skrl.readthedocs.io
