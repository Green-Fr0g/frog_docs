.. _feature-workflows:


任务设计工作流
=====================

.. currentmodule:: isaaclab

**任务（Task）** 由一个环境定义，该环境为特定智能体（机器人）提供了用于获取观测和接收动作的特定接口。环境为智能体提供当前观测，并通过在时间上向前推进仿真来执行该智能体的动作。无论你想让机器人做什么、或者如何训练它去做，在环境中仿真机器人都有许多共同的组件。

这在强化学习（RL）中尤为明显：在向量化 GPU 仿真中管理动作、观测、奖励等，光是想想就令人生畏。为满足这一需求，Isaac Lab 提供了在**管理器式（Manager-based）**系统中构建 RL 环境的能力，让你可以将相应管理器类的各种细节放心交由系统处理。然而，我们也认识到需要对环境进行细粒度控制的需求，尤其是在开发阶段。针对这一需求，我们还提供了直接接入仿真的**直接式（Direct）**接口，让你拥有完全的控制权。

* **Manager-based（管理器式）**：环境被分解为处理环境不同方面的独立组件（或管理器）（例如计算观测、应用动作和应用随机化）。
  用户为每个组件定义配置类，环境负责协调各管理器并调用它们的函数。

* **Direct（直接式）**：用户定义单个类，直接实现整个环境，而无需独立的管理器。该类负责计算观测、应用动作和计算奖励。

两种工作流各有优劣。管理器式工作流更加模块化，允许轻松替换环境的不同组件。这在为环境构建原型和尝试不同配置时非常有用。另一方面，直接式工作流更高效，允许对环境逻辑进行更细粒度的控制。这在针对性能优化环境、或实现难以分解为独立组件的复杂逻辑时非常有用。


管理器式环境
--------------------------

.. image:: ../../_static/task-workflows/manager-based-light.svg
    :class: only-light
    :align: center
    :alt: Manager-based Task Workflow

.. image:: ../../_static/task-workflows/manager-based-dark.svg
    :class: only-dark
    :align: center
    :alt: Manager-based Task Workflow

管理器式环境通过将任务分解为单独管理的组件来促进任务的模块化实现。任务的每个组件（例如计算奖励、观测等）都可以指定为相应管理器的配置。这些管理器定义了可配置的函数，负责按需执行具体的计算。协调一组不同的管理器由继承自 :class:`envs.ManagerBasedEnv` 的 Environment 类处理。配置同样必须全部继承自 :class:`envs.ManagerBasedEnvCfg`。

在开发新的训练环境时，将环境拆分为独立组件往往是有益的。这对协作非常有效，因为它让不同的开发者可以专注于环境的不同方面，同时又能将各自的工作重新组合成一个可运行的任务。例如，你可能拥有多个具备不同传感配置的机器人，需要不同的观测管理器将这些传感数据处理成对下游组件有用的形式。团队中不同成员可能对奖励应如何设计才能达成目标有不同想法，让每个人开发自己的奖励管理器，你就可以按需替换和测试。管理器式工作流的模块化特性对于更复杂的项目至关重要。

对于强化学习来说，其中大部分工作已经为你完成了。在大多数情况下，只需让你的环境继承 :class:`envs.ManagerBasedRLEnv`，并让你的配置继承 :class:`envs.ManagerBasedRLEnvCfg` 即可。

.. dropdown:: 使用管理器式风格为 Cartpole 任务定义奖励函数的示例
    :icon: plus

    下面的类是 Cartpole 环境配置类的一部分。:class:`RewardsCfg` 类
    定义了构成奖励函数的各项条目。每个奖励项由其函数实现、权重以及传递给该函数的额外参数定义。用户可以定义多个
    奖励项及其在奖励函数中使用的权重。

    .. literalinclude:: ../../../../source/isaaclab_tasks/isaaclab_tasks/manager_based/classic/cartpole/cartpole_env_cfg.py
        :language: python
        :pyobject: RewardsCfg

.. seealso::

    我们在 :ref:`tutorial-create-manager-rl-env` 提供了使用管理器式工作流搭建环境的更详细教程。


直接式环境
-------------------

.. image:: ../../_static/task-workflows/direct-based-light.svg
    :class: only-light
    :align: center
    :alt: Direct-based Task Workflow

.. image:: ../../_static/task-workflows/direct-based-dark.svg
    :class: only-dark
    :align: center
    :alt: Direct-based Task Workflow

直接式环境与其他库中环境的传统实现方式更为接近。单个类实现了奖励函数、观测函数、重置以及环境的所有其他组件。这种方式不需要管理器类。相反，用户可以通过 :class:`envs.DirectRLEnv` 或 :class:`envs.DirectMARLEnv` 的 API 获得完全的自由来实现自己的任务。所有直接式任务环境都必须继承这两个类之一。
直接式环境仍需要定义配置，具体通过继承 :class:`envs.DirectRLEnvCfg` 或 :class:`envs.DirectMARLEnvCfg` 来实现。
对于从 `IsaacGymEnvs`_ 和 `OmniIsaacGymEnvs`_ 框架迁移过来的用户，这种工作流可能是最熟悉的。

.. dropdown:: 使用直接式风格为 Cartpole 任务定义奖励函数的示例
    :icon: plus

    下面的函数是 Cartpole 环境类的一部分，负责计算奖励。

    .. literalinclude:: ../../../../source/isaaclab_tasks/isaaclab_tasks/direct/cartpole/cartpole_env.py
        :language: python
        :pyobject: CartpoleEnv._get_rewards
        :dedent: 4

    它调用了 :meth:`compute_rewards` 函数，该函数通过 Torch JIT 编译以获得性能提升。

    .. literalinclude:: ../../../../source/isaaclab_tasks/isaaclab_tasks/direct/cartpole/cartpole_env.py
        :language: python
        :pyobject: compute_rewards

这种方式在环境实现上提供了更多的透明性，因为逻辑直接定义在任务类中，而不是通过管理器进行抽象。这在实现难以分解为独立组件的复杂逻辑时可能更有利。此外，直接式实现可能为环境带来更多的性能收益，因为它允许使用 `PyTorch JIT`_ 或 `Warp`_ 等优化框架来实现大块逻辑。当大幅扩展训练规模、需要优化环境中的单个操作时，这可能很有价值。

.. seealso::

    我们在 :ref:`tutorial-create-direct-rl-env` 提供了使用直接式工作流搭建 RL 环境的更详细教程。


.. _IsaacGymEnvs: https://github.com/isaac-sim/IsaacGymEnvs
.. _OmniIsaacGymEnvs: https://github.com/isaac-sim/OmniIsaacGymEnvs
.. _Pytorch JIT: https://pytorch.org/docs/stable/jit.html
.. _Warp: https://github.com/NVIDIA/warp
