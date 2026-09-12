课程工具
====================

.. currentmodule:: isaaclab.managers

本指南介绍可用于在 Isaac Lab 中为强化学习（RL）环境创建灵活课程（curriculum）的常用课程辅助函数
和 term。这些工具可以传递给 :class:`~isaaclab.managers.CurriculumTermCfg` 对象，
以便在训练期间动态修改奖励权重和环境参数。

.. note::

   本指南涵盖三个工具：
   - 修改奖励的简单函数 :func:`modify_reward_weight`
   - 修改任意环境参数的 term :class:`modify_env_param`
   - 修改 term_cfg 的 term :class:`modify_term_cfg`

.. dropdown:: 课程工具的完整源代码
   :icon: code

   .. literalinclude:: ../../../source/isaaclab/isaaclab/envs/mdp/curriculums.py
      :language: python


修改奖励权重
------------------------

函数 :func:`modify_reward_weight` 在指定的仿真步数之后更新奖励 term 的权重。它可以作为
``CurriculumTermCfg`` 中的 ``func`` 直接传入。

.. literalinclude:: ../../../source/isaaclab/isaaclab/envs/mdp/curriculums.py
   :language: python
   :pyobject: modify_reward_weight

**使用示例**：

.. code-block:: python

   from isaaclab.managers import CurriculumTermCfg
   import isaaclab.managers.mdp as mdp

   # After 100k steps, set the "sparse_reward" term weight to 0.5
   sparse_reward_schedule = CurriculumTermCfg(
       func=mdp.modify_reward_weight,
       params={
           "term_name": "sparse_reward",
           "weight": 0.5,
           "num_steps": 100_000,
       }
   )


动态修改环境参数
--------------------------------------------

类 :class:`modify_env_param` 是 :class:`~isaaclab.managers.ManagerTermBase` 的子类，
它允许您以点号属性路径的形式定位环境中的任意属性，并在运行时应用用户提供的函数来计算新值。
它支持嵌套属性、字典键、列表或元组索引，并且在不需要更新时遵循 ``NO_CHANGE`` 哨兵值。

.. literalinclude:: ../../../source/isaaclab/isaaclab/envs/mdp/curriculums.py
   :language: python
   :pyobject: modify_env_param

**使用示例**：

.. code-block:: python

   import torch
   from isaaclab.managers import CurriculumTermCfg
   import isaaclab.managers.mdp as mdp

   def resample_friction(env, env_ids, old_value, low, high, num_steps):
       # After num_steps, sample a new friction coefficient uniformly
       if env.common_step_counter > num_steps:
           return torch.empty((len(env_ids),), device="cpu").uniform_(low, high)
       return mdp.modify_env_param.NO_CHANGE

   friction_curriculum = CurriculumTermCfg(
       func=mdp.modify_env_param,
       params={
           "address": "event_manager.cfg.object_physics_material.func.material_buckets",
           "modify_fn": resample_friction,
           "modify_params": {
               "low": 0.3,
               "high": 1.0,
               "num_steps": 120_000,
           }
       }
   )


修改 Term 配置
-------------------------

子类 :class:`modify_term_cfg` 提供了一种更简洁的 address 语法，与 hydra 配置语法保持一致。
除此之外，它的行为与 :class:`modify_env_param` 完全相同。

.. literalinclude:: ../../../source/isaaclab/isaaclab/envs/mdp/curriculums.py
   :language: python
   :pyobject: modify_term_cfg

**使用示例**：

.. code-block:: python

   def override_command_range(env, env_ids, old_value, value, num_steps):
       # Override after num_steps
       if env.common_step_counter > num_steps:
           return value
       return mdp.modify_term_cfg.NO_CHANGE

   range_override = CurriculumTermCfg(
       func=mdp.modify_term_cfg,
       params={
           "address": "commands.object_pose.ranges.pos_x",
           "modify_fn": override_command_range,
           "modify_params": {
               "value": (-0.75, -0.25),
               "num_steps": 12_000,
           }
       }
   )
