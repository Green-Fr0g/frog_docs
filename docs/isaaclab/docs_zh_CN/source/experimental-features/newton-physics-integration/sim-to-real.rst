.. _sim2real:

Sim-to-Real 策略迁移
====================
将策略从仿真部署到真实机器人涉及一些必须处理的重要细节。
本节提供了一份高层次指南，介绍如何训练可部署到真实 Unitree G1 机器人上的策略。
关键的挑战在于：仿真中可用的观测并非都能由真实机器人传感器直接测量。
这意味着，除非 RL 训练出的策略只使用传感器可获得的观测，否则无法直接部署。例如，虽然真实机器人的 IMU 传感器能提供角加速度（可积分得到角速度），但它们无法直接测量线速度。因此，如果策略在训练时依赖基座线速度，那么在部署到真实机器人之前必须移除该信息。


前提条件
~~~~~~~~

我们假定该工作流产出的策略在部署到真实机器人之前，会先通过 sim-to-sim 迁移进行验证。
更多信息请见 :ref:`此处 <sim2sim>`。


概述
----

本节以 Unitree G1 的速度跟踪任务为例，演示在 Newton 后端下使用教师—学生蒸馏的 sim-to-real 工作流。

教师—学生蒸馏工作流包含三个阶段：

1. 使用真实世界传感器无法获得的特权观测训练教师策略。
2. 通过从教师策略进行行为克隆，蒸馏出排除特权项（例如根线速度）的学生策略。
3. 仅使用真实传感器观测，通过 RL 对学生策略进行微调。

教师和学生的观测组实现于 velocity 任务配置中。详见以下源码：

- 教师观测：`velocity_env_cfg.py <https://github.com/isaac-sim/IsaacLab/blob/main/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/velocity_env_cfg.py>`__ 中的 ``PolicyCfg(ObsGroup)``
- 学生观测：`velocity_env_cfg.py <https://github.com/isaac-sim/IsaacLab/blob/main/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/velocity_env_cfg.py>`__ 中的 ``StudentPolicyCfg(ObsGroup)``


1. 训练教师策略
~~~~~~~~~~~~~~~

使用 Newton 后端为 G1 速度任务训练教师策略。任务 ID 为 ``Isaac-Velocity-Flat-G1-v1``

.. code-block:: bash

   ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task=Isaac-Velocity-Flat-G1-v1 --num_envs=4096

教师策略包含在 ``PolicyCfg(ObsGroup)`` 中定义的特权观测（例如根线速度）。


2. 蒸馏学生策略（移除特权项）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在蒸馏过程中，学生策略通过行为克隆来模仿教师，即最小化二者动作之间的均方误差：
:math:`loss = MSE(\pi(O_{teacher}), \pi(O_{student}))`。

学生策略只使用真实传感器可获得的观测（参见
`velocity_env_cfg.py <https://github.com/isaac-sim/IsaacLab/blob/main/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/velocity_env_cfg.py>`__ 中的 ``StudentPolicyCfg(ObsGroup)``）。
具体来说： **根角速度** 和 **投影重力** 来自 IMU 传感器，**关节位置与速度** 来自关节编码器，**动作** 则是控制器施加的关节力矩。

运行学生蒸馏任务 ``Velocity-G1-Distillation-v1``，使用 ``--load_run`` 和 ``--checkpoint`` 指定你希望从中蒸馏的教师策略。

.. code-block:: bash

   ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task=Velocity-G1-Distillation-v1 --num_envs=4096 --load_run 2025-08-13_23-53-28 --checkpoint model_1499.pt

.. note::

   请使用正确的 ``--load_run`` 和 ``--checkpoint``，以确保你是从预期的教师策略进行蒸馏。


3. 使用 RL 微调学生策略
~~~~~~~~~~~~~~~~~~~~~~~

使用 ``Velocity-G1-Student-Finetune-v1`` 任务，通过 RL 对蒸馏得到的学生策略进行微调。
使用 ``--load_run`` 和 ``--checkpoint`` 从蒸馏后的策略进行初始化。

.. code-block:: bash

   ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task=Velocity-G1-Student-Finetune-v1 --num_envs=4096 --load_run 2025-08-20_16-06-52_distillation --checkpoint model_1499.pt

这会从蒸馏后的学生策略开始，并通过 RL 训练进一步提升它。

.. note::

   请确保 ``--load_run`` 和 ``--checkpoint`` 指向正确的初始策略（通常是蒸馏步骤产出的最新检查点）。

你可以通过以下命令回放学生策略：

.. code-block:: bash

   ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task=Velocity-G1-Student-Finetune-v1 --num_envs=32 --visualizer newton


这会将策略以 ``.pt`` 和 ``.onnx`` 文件的形式导出到该次运行的 export 目录中，供真实机器人部署使用。
