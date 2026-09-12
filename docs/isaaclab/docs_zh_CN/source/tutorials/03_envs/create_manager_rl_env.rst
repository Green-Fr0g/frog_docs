.. _tutorial-create-manager-rl-env:


创建管理器式强化学习环境
=======================================

.. currentmodule:: isaaclab

在 :ref:`tutorial-create-manager-base-env` 中学习了如何创建基础环境之后，我们现在来看看如何为强化学习创建管理器式
任务环境。

基础环境被设计为一个「感知-行动」环境，智能体可以向环境发送命令
并从环境接收观测。这一最小化接口对许多应用（例如
传统运动规划和控制）已经足够。然而，许多应用需要一个任务规范（task specification），它通常
作为智能体的学习目标。例如，在导航任务中，可能要求智能体
到达目标位置。为此，我们使用 :class:`envs.ManagerBasedRLEnv` 类，它扩展了基础环境
以包含任务规范。

与 Isaac Lab 中的其他组件类似，我们不鼓励直接修改基类 :class:`envs.ManagerBasedRLEnv`，而是
鼓励用户为自己的任务环境实现一个配置 :class:`envs.ManagerBasedRLEnvCfg`。
这种做法使我们可以将任务规范与环境实现分离，从而更轻松地
将同一环境的组件复用于不同任务。

在本教程中，我们将使用 :class:`envs.ManagerBasedRLEnvCfg` 配置 cartpole 环境，创建一个将杆保持直立平衡的管理器式任务。
我们将学习如何使用奖励项、终止条件、
课程和命令来指定任务。


代码
~~~~~~~~

在本教程中，我们使用 ``isaaclab_tasks.manager_based.classic.cartpole`` 模块中定义的 cartpole 环境。

.. dropdown:: Code for cartpole_env_cfg.py
   :icon: code

   .. literalinclude:: ../../../../source/isaaclab_tasks/isaaclab_tasks/manager_based/classic/cartpole/cartpole_env_cfg.py
      :language: python
      :emphasize-lines: 117-141, 144-154, 172-174
      :linenos:

用于运行环境的脚本 ``run_cartpole_rl_env.py`` 位于
``isaaclab/scripts/tutorials/03_envs`` 目录。该脚本与前一篇教程中的
``cartpole_base_env.py`` 脚本类似，只是它使用
:class:`envs.ManagerBasedRLEnv` 而不是 :class:`envs.ManagerBasedEnv`。

.. dropdown:: Code for run_cartpole_rl_env.py
   :icon: code

   .. literalinclude:: ../../../../scripts/tutorials/03_envs/run_cartpole_rl_env.py
      :language: python
      :emphasize-lines: 38-42, 56-57
      :linenos:


代码解析
~~~~~~~~~~~~~~~~~~

我们已经在 :ref:`tutorial-create-manager-base-env` 教程中介绍了上述部分内容，了解了
如何指定场景、观测、动作和事件。因此，在本教程中，我们将
只关注环境的强化学习组件。

在 Isaac Lab 中，我们在 :mod:`envs.mdp` 模块中提供了各种项的不同实现。本教程将使用
其中一些项，但用户也可以自由定义自己的项。这些项
通常放置在任务专属的子包中
（例如 :mod:`isaaclab_tasks.manager_based.classic.cartpole.mdp`）。


定义奖励
----------------

:class:`managers.RewardManager` 用于为智能体计算奖励项。与其他
管理器类似，它的各项使用 :class:`managers.RewardTermCfg` 类进行配置。
:class:`managers.RewardTermCfg` 类指定计算奖励的函数或可调用类，
以及与之相关的权重。它还接受一个参数字典 ``"params"``，
在奖励函数被调用时传递给它。

对于 cartpole 任务，我们将使用以下奖励项：

* **存活奖励（Alive Reward）**：鼓励智能体尽可能长时间保持存活。
* **终止奖励（Terminating Reward）**：类似地对智能体的终止进行惩罚。
* **杆角度奖励（Pole Angle Reward）**：鼓励智能体将杆保持在期望的直立位置。
* **小车速度奖励（Cart Velocity Reward）**：鼓励智能体使小车速度尽可能小。
* **杆速度奖励（Pole Velocity Reward）**：鼓励智能体使杆速度尽可能小。

.. literalinclude:: ../../../../source/isaaclab_tasks/isaaclab_tasks/manager_based/classic/cartpole/cartpole_env_cfg.py
   :language: python
   :pyobject: RewardsCfg

定义终止条件
-----------------------------

大多数学习任务都在有限步数内进行，我们称之为一个回合（episode）。例如，在 cartpole
任务中，我们希望智能体尽可能长时间地平衡杆。然而，如果智能体进入不稳定的
或不安全的状态，我们希望终止该回合。另一方面，如果智能体能够长时间平衡杆，
我们希望终止该回合并开始新的回合，以便智能体能够学习从不同的初始配置开始平衡
杆。

:class:`managers.TerminationsCfg` 配置什么情况构成回合终止。在本示例中，
我们希望任务在满足以下任一条件时终止：

* **回合长度**：回合长度大于定义的 max_episode_length
* **小车越界**：小车超出边界 [-3, 3]

标志 :attr:`managers.TerminationsCfg.time_out` 指定该项是超时（截断）项
还是终止项。它们用于指示 `Gymnasium's documentation
<https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/>`_ 中描述的两种终止类型。

.. literalinclude:: ../../../../source/isaaclab_tasks/isaaclab_tasks/manager_based/classic/cartpole/cartpole_env_cfg.py
   :language: python
   :pyobject: TerminationsCfg

定义命令
-----------------

对于各种目标条件任务，为智能体指定目标或命令非常有用。这些通过
:class:`managers.CommandManager` 处理。命令管理器负责在每一步重新采样和更新
命令。它还可以用于将命令作为观测提供给智能体。

对于这个简单任务，我们不使用任何命令。因此，我们将该属性保留为其默认值 None。
你可以在其他运动（locomotion）或操作（manipulation）任务中查看如何定义命令管理器的示例。

定义课程
-------------------

在训练学习智能体时，从简单任务开始，并随着智能体训练的进行逐渐增加
任务难度，通常是有帮助的。这就是课程学习背后的思想。在 Isaac Lab 中，
我们提供了 :class:`managers.CurriculumManager` 类，可用于为你的环境定义课程。

为简单起见，本教程不实现课程，但你可以在其他运动或操作任务中查看
课程定义的示例。

整合在一起
---------------------

在定义了上述所有组件之后，我们现在可以为
cartpole 环境创建 :class:`ManagerBasedRLEnvCfg` 配置。它类似于 :ref:`tutorial-create-manager-base-env` 中定义的 :class:`ManagerBasedEnvCfg`，
只是增加了上面各节解释的强化学习组件。

.. literalinclude:: ../../../../source/isaaclab_tasks/isaaclab_tasks/manager_based/classic/cartpole/cartpole_env_cfg.py
   :language: python
   :pyobject: CartpoleEnvCfg

运行仿真循环
---------------------------

回到 ``run_cartpole_rl_env.py`` 脚本，其仿真循环与前一篇教程类似。
唯一的区别是我们创建 :class:`envs.ManagerBasedRLEnv` 的实例而不是
:class:`envs.ManagerBasedEnv`。因此，现在 :meth:`envs.ManagerBasedRLEnv.step` 方法会返回额外的信号，
例如奖励和终止状态。信息字典还维护诸如各个项的奖励贡献、每项的终止状态、回合长度等的日志。

.. literalinclude:: ../../../../scripts/tutorials/03_envs/run_cartpole_rl_env.py
   :language: python
   :pyobject: main


代码执行
~~~~~~~~~~~~~~~~~~


与前一篇教程类似，我们可以通过执行 ``run_cartpole_rl_env.py`` 脚本来运行环境。

.. code-block:: bash

   ./isaaclab.sh -p scripts/tutorials/03_envs/run_cartpole_rl_env.py --num_envs 32


这应该会打开一个与前一篇教程类似的仿真。不过，这一次，环境
会返回更多信号，用于指定奖励和终止状态。此外，各个
环境会在根据配置中指定的终止条件终止时自行重置。

.. figure:: ../../_static/tutorials/tutorial_create_manager_rl_env.jpg
    :align: center
    :figwidth: 100%
    :alt: result of run_cartpole_rl_env.py

要停止仿真，你可以关闭窗口，或在启动仿真的终端中
按 ``Ctrl+C``。

在本教程中，我们学习了如何为强化学习创建任务环境。我们通过
扩展基础环境来加入奖励、终止、命令和课程项来完成这一工作。
我们还学习了如何使用 :class:`envs.ManagerBasedRLEnv` 类运行环境并从中接收各种
信号。

虽然可以手动为期望的任务创建 :class:`envs.ManagerBasedRLEnv` 类的实例，
但这不具备可扩展性，因为它需要为每个任务编写专门的脚本。因此，我们利用
:meth:`gymnasium.make` 函数通过 gym 接口创建环境。我们将在下一篇教程中学习
如何做到这一点。
