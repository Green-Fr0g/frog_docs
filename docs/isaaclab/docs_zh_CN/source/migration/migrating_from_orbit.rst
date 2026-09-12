.. _migrating-from-orbit:

从 Orbit 迁移
==============

.. currentmodule:: isaaclab

由于 Isaac Lab 以 `Orbit`_ 为基础开发，因此从 Orbit 迁移到 Isaac Lab 非常简单。
以下各节介绍了将你的代码从 Orbit 迁移到 Isaac Lab 时需要做的修改。

.. note::

  以下变更基于 Isaac Lab 1.0 版本。未来版本中的任何变更，
  请参阅 `release notes`_ 。


启动脚本的重命名
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

脚本 ``orbit.sh`` 已被重命名为 ``isaaclab.sh``。


扩展的更新
~~~~~~~~~~~~~~~~~~~~~

扩展 ``omni.isaac.orbit`` 、 ``omni.isaac.orbit_tasks`` 和 ``omni.isaac.orbit_assets`` 已分别被重命名
为 ``isaaclab`` 、 ``isaaclab_tasks`` 和 ``isaaclab_assets``。因此，
新的文件夹结构如下所示：

- ``source/isaaclab/isaaclab``
- ``source/isaaclab_tasks/isaaclab_tasks``
- ``source/isaaclab_assets/isaaclab_assets``

高层导入也需要相应更新：

+-------------------------------------+-----------------------------------+
| Orbit                               | Isaac Lab                         |
+=====================================+===================================+
| ``from omni.isaac.orbit...``        | ``from isaaclab...``              |
+-------------------------------------+-----------------------------------+
| ``from omni.isaac.orbit_tasks...``  | ``from isaaclab_tasks...``        |
+-------------------------------------+-----------------------------------+
| ``from omni.isaac.orbit_assets...`` | ``from isaaclab_assets...``       |
+-------------------------------------+-----------------------------------+


类名的更新
~~~~~~~~~~~~~~~~~~~~~~

Isaac Lab 引入了任务设计工作流的概念（参见 :ref:`feature-workflows` ）。Orbit 代码使用的是
管理器式工作流，与环境相关的类名已更新以反映这一变化：

+------------------------+---------------------------------------------------------+
| Orbit                  | Isaac Lab                                               |
+========================+=========================================================+
| ``BaseEnv``            | :class:`isaaclab.envs.ManagerBasedEnv`                  |
+------------------------+---------------------------------------------------------+
| ``BaseEnvCfg``         | :class:`isaaclab.envs.ManagerBasedEnvCfg`               |
+------------------------+---------------------------------------------------------+
| ``RLTaskEnv``          | :class:`isaaclab.envs.ManagerBasedRLEnv`                |
+------------------------+---------------------------------------------------------+
| ``RLTaskEnvCfg``       | :class:`isaaclab.envs.ManagerBasedRLEnvCfg`             |
+------------------------+---------------------------------------------------------+
| ``RLTaskEnvWindow``    | :class:`isaaclab.envs.ui.ManagerBasedRLEnvWindow`       |
+------------------------+---------------------------------------------------------+


任务文件夹结构的更新
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

为了支持管理器式工作流和直接式工作流，我们在任务扩展中新增了两个文件夹：

- ``source/isaaclab_tasks/isaaclab_tasks/manager_based``
- ``source/isaaclab_tasks/isaaclab_tasks/direct``

Orbit 中的任务现在可以在 ``manager_based`` 文件夹下找到。
这一变化也必须体现在你的任务导入语句中。例如，

.. code-block:: python

  from omni.isaac.orbit_tasks.locomotion.velocity.velocity_env_cfg ...

应改为：

.. code-block:: python

  from isaaclab_tasks.manager_based.locomotion.velocity.velocity_env_cfg ...


其他破坏性变更
~~~~~~~~~~~~~~~~~~~~~~

设置设备
------------------

参数 ``--cpu`` 已被移除，由 ``--device device_name`` 取代。 ``device_name`` 的有效选项为：

- ``cpu`` ：使用 CPU。
- ``cuda`` ：使用设备 ID 为 ``0`` 的 GPU。
- ``cuda:N`` ：使用 GPU，其中 N 为设备 ID。例如 ``cuda:0``。

默认值为 ``cuda:0``。


离屏渲染
-------------------

传递给 :class:`isaaclab.app.AppLauncher` 的输入参数 ``--offscreen_render`` 以及环境变量
``OFFSCREEN_RENDER`` 已分别被重命名为 ``--enable_cameras`` 和 ``ENABLE_CAMERAS``。


事件项分布配置
-------------------------------------

`events.py <https://github.com/isaac-sim/IsaacLab/blob/main/source/isaaclab/isaaclab/envs/mdp/events.py>`_
中的部分事件函数接受一个 ``distribution`` 参数以及一个用于采样的 ``range``。为了支持任意分布，
我们已将这些函数的输入参数 ``AAA_range`` 重命名为 ``AAA_distribution_params``。
因此，函数带有 ``distribution`` 参数的事件项配置应当更新。例如，

.. code-block:: python
  :emphasize-lines: 6

  add_base_mass = EventTerm(
      func=mdp.randomize_rigid_body_mass,
      mode="startup",
      params={
          "asset_cfg": SceneEntityCfg("robot", body_names="base"),
          "mass_range": (-5.0, 5.0),
          "operation": "add",
      },
  )

应改为：

.. code-block:: python
  :emphasize-lines: 6

  add_base_mass = EventTerm(
      func=mdp.randomize_rigid_body_mass,
      mode="startup",
      params={
          "asset_cfg": SceneEntityCfg("robot", body_names="base"),
          "mass_distribution_params": (-5.0, 5.0),
          "operation": "add",
      },
  )


.. _Orbit: https://isaac-orbit.github.io/
.. _release notes: https://github.com/isaac-sim/IsaacLab/releases
