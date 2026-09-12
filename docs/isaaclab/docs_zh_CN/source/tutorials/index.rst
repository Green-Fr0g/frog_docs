.. _tutorials:

教程
====

欢迎阅读 Isaac Lab 教程！这些教程提供了分步指南，帮助你理解和使用框架的各种功能。所有教程均以
Python 脚本的形式编写。你可以在 Isaac Lab 仓库的 ``scripts/tutorials`` 目录中找到每个教程的
源代码。

.. note::

    我们希望扩展教程以覆盖更多主题和使用场景，因此如果有任何建议，请告诉我们。

我们建议你按照此处列出的顺序依次完成教程。


搭建简单仿真
-------------------------------

这些教程向你展示如何以不同的设置启动仿真，并在仿真场景中生成物体。它们涵盖以下 API：:class:`~isaaclab.app.AppLauncher`、
:class:`~isaaclab.sim.SimulationContext` 和 :class:`~isaaclab.sim.spawners`。

.. toctree::
    :maxdepth: 1
    :titlesonly:

    00_sim/create_empty
    00_sim/spawn_prims
    00_sim/launch_app

操作资产
-----------------------

在场景中生成物体之后，这些教程向你展示如何为这些物体创建物理句柄并与它们交互。它们围绕
:class:`~isaaclab.assets.AssetBase` 类及其派生类展开，例如 :class:`~isaaclab.assets.RigidObject`、
:class:`~isaaclab.assets.Articulation` 和 :class:`~isaaclab.assets.DeformableObject`。

.. toctree::
    :maxdepth: 1
    :titlesonly:

    01_assets/add_new_robot
    01_assets/run_rigid_object
    01_assets/run_articulation
    01_assets/run_deformable_object
    01_assets/run_surface_gripper

创建场景
----------------

在介绍完框架的基本概念之后，教程将转向更直观的场景接口，即使用 :class:`~isaaclab.scene.InteractiveScene` 类。该类
提供了更高层的抽象，便于轻松创建场景。

.. toctree::
    :maxdepth: 1
    :titlesonly:

    02_scene/create_scene

设计环境
------------------------

以下教程介绍管理器式环境的概念：:class:`~isaaclab.envs.ManagerBasedEnv`
及其派生类 :class:`~isaaclab.envs.ManagerBasedRLEnv`，以及直接式工作流的基类
:class:`~isaaclab.envs.DirectRLEnv`。这些环境将框架的不同方面整合在一起，
构建用于智能体交互的仿真环境。

.. toctree::
    :maxdepth: 1
    :titlesonly:

    03_envs/create_manager_base_env
    03_envs/create_manager_rl_env
    03_envs/create_direct_rl_env
    03_envs/register_rl_env_gym
    03_envs/run_rl_training
    03_envs/configuring_rl_training
    03_envs/modify_direct_rl_env
    03_envs/policy_inference_in_usd

集成传感器
-------------------

以下教程向你展示如何将传感器集成到仿真环境中。这些教程介绍 :class:`~isaaclab.sensors.SensorBase` 类及其派生类，
例如 :class:`~isaaclab.sensors.Camera` 和 :class:`~isaaclab.sensors.RayCaster`。

.. toctree::
    :maxdepth: 1
    :titlesonly:

    04_sensors/add_sensors_on_robot

使用运动生成器
-----------------------

虽然仿真环境中的机器人可以在关节层级进行控制，但以下教程向你展示如何使用运动生成器在任务层级控制机器人。

.. toctree::
    :maxdepth: 1
    :titlesonly:

    05_controllers/run_diff_ik
    05_controllers/run_osc
