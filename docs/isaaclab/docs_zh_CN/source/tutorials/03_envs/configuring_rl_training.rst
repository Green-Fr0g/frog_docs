.. _tutorial-configure-rl-training:

配置强化学习智能体
=======================

.. currentmodule:: isaaclab

在前一篇教程中，我们了解了如何使用 `Stable-Baselines3`_ 库训练强化学习智能体来解决 cartpole 平衡任务。
在本教程中，我们将了解如何配置
训练过程，以使用不同的强化学习库和不同的训练算法。

在 ``scripts/reinforcement_learning`` 目录中，你会找到
不同强化学习库的脚本。它们按库名命名的子目录组织。
每个子目录包含该库的训练和运行脚本。

要将学习库配置到特定任务，你需要为学习智能体创建一个配置文件。
该配置文件用于创建学习智能体的实例，
并用于配置训练过程。与 :ref:`tutorial-register-rl-env-gym` 教程中展示的环境注册类似，你可以使用
``gymnasium.register`` 方法注册学习智能体。

代码
--------

作为示例，我们将查看 ``isaaclab_tasks`` 包中为任务 ``Isaac-Cartpole-v0``
包含的配置。这与我们在
:ref:`tutorial-run-rl-training` 教程中使用的任务相同。

.. literalinclude:: ../../../../source/isaaclab_tasks/isaaclab_tasks/manager_based/classic/cartpole/__init__.py
   :language: python
   :lines: 18-29

代码解析
------------------

在 ``kwargs`` 属性下，我们可以看到不同学习库的配置。
键是库的名称，值是配置实例的路径。
该配置实例可以是字符串、类或类的实例。
例如，键 ``"rl_games_cfg_entry_point"`` 的值是一个字符串，指向
RL-Games 库的配置 YAML 文件。与此同时，键
``"rsl_rl_cfg_entry_point"`` 的值指向 RSL-RL 库的配置类。

指定智能体配置类所用的模式与
指定环境配置入口点所用的模式非常接近。这意味着下面两种
写法是等价的：


.. dropdown:: Specifying the configuration entry point as a string
   :icon: code

   .. code-block:: python

      from . import agents

      gym.register(
         id="Isaac-Cartpole-v0",
         entry_point="isaaclab.envs:ManagerBasedRLEnv",
         disable_env_checker=True,
         kwargs={
            "env_cfg_entry_point": f"{__name__}.cartpole_env_cfg:CartpoleEnvCfg",
            "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:CartpolePPORunnerCfg",
         },
      )

.. dropdown:: Specifying the configuration entry point as a class
   :icon: code

   .. code-block:: python

      from . import agents

      gym.register(
         id="Isaac-Cartpole-v0",
         entry_point="isaaclab.envs:ManagerBasedRLEnv",
         disable_env_checker=True,
         kwargs={
            "env_cfg_entry_point": f"{__name__}.cartpole_env_cfg:CartpoleEnvCfg",
            "rsl_rl_cfg_entry_point": agents.rsl_rl_ppo_cfg.CartpolePPORunnerCfg,
         },
      )

第一种代码块是指定配置入口点的首选方式。
第二种代码块与第一种等价，但它会导致配置
类被导入，从而拖慢导入时间。这就是我们建议对配置
入口点使用字符串的原因。

``scripts/reinforcement_learning`` 目录中的所有脚本默认配置为从 ``kwargs`` 字典读取
``<library_name>_cfg_entry_point`` 来获取配置实例。

例如，下面的代码块展示了 ``train.py`` 脚本如何读取
Stable-Baselines3 库的配置实例：

.. dropdown:: Code for train.py with SB3
    :icon: code

    .. literalinclude:: ../../../../scripts/reinforcement_learning/sb3/train.py
      :language: python
      :emphasize-lines: 26-28, 102-103
      :linenos:

参数 ``--agent`` 用于指定要使用的学习库。它用于
从 ``kwargs`` 字典中获取配置实例。你可以通过传入 ``--agent`` 参数手动指定
其他配置实例。

代码执行
------------------

由于针对 cartpole 平衡任务，RSL-RL 库提供了两个配置实例，
我们可以使用 ``--agent`` 参数指定要使用的配置实例。

* 使用标准 PPO 配置进行训练：

  .. code-block:: bash

    # standard PPO training
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Cartpole-v0 --headless \
      --run_name ppo

* 使用带对称性增强的 PPO 配置进行训练：

  .. code-block:: bash

    # PPO training with symmetry augmentation
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Cartpole-v0 --headless \
      --agent rsl_rl_with_symmetry_cfg_entry_point \
      --run_name ppo_with_symmetry_data_augmentation

    # you can use hydra to disable symmetry augmentation but enable mirror loss computation
    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Cartpole-v0 --headless \
      --agent rsl_rl_with_symmetry_cfg_entry_point \
      --run_name ppo_without_symmetry_data_augmentation \
      agent.algorithm.symmetry_cfg.use_data_augmentation=false

``--run_name`` 参数用于指定本次运行的名称。它用于
在 ``logs/rsl_rl/cartpole`` 目录中为该运行创建一个目录。

.. _Stable-Baselines3: https://stable-baselines3.readthedocs.io/en/master/
.. _RL-Games: https://github.com/Denys88/rl_games
.. _RSL-RL: https://github.com/leggedrobotics/rsl_rl
.. _SKRL: https://skrl.readthedocs.io
