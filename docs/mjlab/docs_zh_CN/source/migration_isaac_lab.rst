.. _migration_isaac_lab:

从 Isaac Lab 迁移
=================

.. warning::

   本指南仍在编写中。随着更多用户完成迁移，我们会在本页补充更多模式与
   边界情况。如果有未覆盖的内容，请在 GitHub 上提交 issue 或发起讨论：

   - Issues: https://github.com/mujocolab/mjlab/issues
   - Discussions: https://github.com/mujocolab/mjlab/discussions

速览
----

大多数 Isaac Lab *manager-based* 任务配置只需少量改动即可移植到
``mjlab`` ：

- 整体 **MDP 结构是相同的** (奖励、观测、动作、指令、终止、事件、课程各
  有对应的管理器) 。
- **环境基类是相似的** ，只是命名略有不同。
- 最大的变化在于 **配置风格** ：Isaac Lab 使用嵌套的 ``@configclass``
  定义； ``mjlab`` 使用配置对象组成的字典。

如果你已经熟悉 Isaac Lab 的 manager-based API，迁移基本上是机械性的
工作。

主要差异
--------

1. 导入路径
~~~~~~~~~~~~

Isaac Lab:

.. code-block:: python

   from isaaclab.envs import ManagerBasedRLEnv

mjlab:

.. code-block:: python

   from mjlab.envs import ManagerBasedRlEnvCfg

.. note::

   ``mjlab`` 采用一致的 ``CamelCase`` 命名约定 (例如用 ``RlEnv`` 而不是
   ``RLEnv``) 。

2. 配置结构
~~~~~~~~~~~

Isaac Lab 对管理器项使用嵌套的 ``@configclass`` 块。 ``mjlab`` 则改用
**普通字典** 将名称映射到配置对象，这样便于构造变体、合并配置或以编程
方式生成配置。这一设计决策的完整背景参见
`PR #292 <https://github.com/mujocolab/mjlab/pull/292>`_ 。

**Isaac Lab:**

.. code-block:: python

   @configclass
   class RewardsCfg:
       """Reward terms for the MDP."""

       motion_global_anchor_pos = RewTerm(
           func=mdp.motion_global_anchor_position_error_exp,
           weight=0.5,
           params={"command_name": "motion", "std": 0.3},
       )
       motion_global_anchor_ori = RewTerm(
           func=mdp.motion_global_anchor_orientation_error_exp,
           weight=0.5,
           params={"command_name": "motion", "std": 0.4},
       )

**mjlab:**

.. code-block:: python

   rewards = {
       "motion_global_anchor_pos": RewardTermCfg(
           func=mdp.motion_global_anchor_position_error_exp,
           weight=0.5,
           params={"command_name": "motion", "std": 0.3},
       ),
       "motion_global_anchor_ori": RewardTermCfg(
           func=mdp.motion_global_anchor_orientation_error_exp,
           weight=0.5,
           params={"command_name": "motion", "std": 0.4},
       ),
   }

   cfg = ManagerBasedRlEnvCfg(
       scene=scene,
       rewards=rewards,
       # ... other manager dictionaries:
       # observations=..., actions=..., commands=..., terminations=...,
       # events=..., curriculum=...
   )

这一模式适用于所有管理器：

- ``rewards``
- ``observations``
- ``actions``
- ``commands``
- ``terminations``
- ``events``
- ``curriculum``

3. 场景配置
~~~~~~~~~~~

``mjlab`` 中的场景搭建 **更简单** ：

- 没有 Omniverse / USD 场景图，也不需要管理 ``prim_path`` 。
- 资产是纯 MuJoCo (MJCF) ，并通过修饰用 dataclass 作用到
  ``mujoco.MjSpec`` 上。
- 灯光、材质、纹理和传感器都作为 ``SceneCfg`` 和机器人配置的一部分来
  设置。

**Isaac Lab:**

.. code-block:: python

   from whole_body_tracking.robots.g1 import G1_ACTION_SCALE, G1_CYLINDER_CFG
   from isaaclab.scene import InteractiveSceneCfg
   from isaaclab.sensors import ContactSensorCfg
   from isaaclab.terrains import TerrainImporterCfg
   import isaaclab.sim as sim_utils
   from isaaclab.assets import ArticulationCfg, AssetBaseCfg

   @configclass
   class MySceneCfg(InteractiveSceneCfg):
       """Configuration for the terrain scene with a legged robot."""

       # ground terrain
       terrain = TerrainEntityCfg(
           prim_path="/World/ground",
           terrain_type="plane",
           collision_group=-1,
           physics_material=sim_utils.RigidBodyMaterialCfg(
               friction_combine_mode="multiply",
               restitution_combine_mode="multiply",
               static_friction=1.0,
               dynamic_friction=1.0,
           ),
           visual_material=sim_utils.MdlFileCfg(
               mdl_path="{NVIDIA_NUCLEUS_DIR}/Materials/Base/Architecture/Shingles_01.mdl",
               project_uvw=True,
           ),
       )
       # lights
       light = AssetBaseCfg(
           prim_path="/World/light",
           spawn=sim_utils.DistantLightCfg(
               color=(0.75, 0.75, 0.75), intensity=3000.0
           ),
       )
       sky_light = AssetBaseCfg(
           prim_path="/World/skyLight",
           spawn=sim_utils.DomeLightCfg(
               color=(0.13, 0.13, 0.13), intensity=1000.0
           ),
       )
       robot = G1_CYLINDER_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")

**mjlab:**

.. code-block:: python

   from dataclasses import replace

   from mjlab.scene import SceneCfg
   from mjlab.asset_zoo.robots.unitree_g1.g1_constants import get_g1_robot_cfg
   from mjlab.utils.spec_config import ContactSensorCfg
   from mjlab.terrains import TerrainEntityCfg

   # Configure contact sensor
   self_collision_sensor = ContactSensorCfg(
       name="self_collision",
       subtree1="pelvis",
       subtree2="pelvis",
       data=("found",),
       reduce="netforce",
       num=10,  # report up to 10 contacts
   )

   # Add sensor to robot config
   g1_cfg = replace(get_g1_robot_cfg(), sensors=(self_collision_sensor,))

   # Create scene
   SCENE_CFG = SceneCfg(
       terrain=TerrainEntityCfg(terrain_type="plane"),
       entities={"robot": g1_cfg},
   )

主要变化：

- 没有 USD ``prim_path`` 和克隆；场景直接用 MuJoCo 描述。
- 材质、灯光和视觉属性通过 ``MjSpec`` 修饰 dataclass 来应用。
- 仓库中的 ``mjlab.utils.spec_config`` 提供了帮你完成这些修改的辅助
  工具。
- 所有配置中的 ``asset_name`` 已统一更名为 ``entity_name`` 。

完整示例对比
------------

学习这一模式的好办法，是对比已经完成移植的具体任务：

- Isaac Lab 实现 (Beyond Mimic)：

  - https://github.com/HybridRobotics/whole_body_tracking/blob/main/source/whole_body_tracking/whole_body_tracking/tasks/tracking/tracking_env_cfg.py

- mjlab 实现：

  - https://github.com/mujocolab/mjlab/blob/main/src/mjlab/tasks/tracking/tracking_env_cfg.py

对比之后你会发现：

- ``mjlab`` 中的管理器字典与 Isaac Lab 的配置类一一对应，
- 奖励、观测、指令和终止逻辑几乎完全相同，
- 场景和资产设置被简化为纯 MuJoCo。

迁移清单
--------

移植任务时，可以对照下面这份快速清单：

1. **基类与导入**

   - 将 Isaac Lab 的导入 (例如
     ``from isaaclab.envs import ManagerBasedRLEnv``) 替换为对应的
     ``mjlab`` 导入 (例如
     ``from mjlab.envs import ManagerBasedRlEnvCfg``) 。

2. **管理器配置**

   - 把每个 Isaac Lab ``@configclass`` 管理器 (``RewardsCfg`` 、
     ``ObservationsCfg`` 等) 转换成配置对象组成的字典。
   - 将这些字典传入 ``ManagerBasedRlEnvCfg`` 。

3. **场景与资产**

   - 将 ``InteractiveSceneCfg`` 替换为 ``SceneCfg`` 实例。
   - 将 USD / ``prim_path`` 逻辑替换为 MuJoCo 资产配置和场景实体 (例如
     来自 ``asset_zoo`` 的机器人) 。

4. **传感器与接触处理**

   - 将 Isaac Lab 的 ``ContactSensorCfg`` 转换为
     ``mjlab.utils.spec_config.ContactSensorCfg`` ，并挂载到机器人配置
     上。

5. **RL 入口**

   - 确保你的训练脚本或入口使用正确的任务 ID 和环境配置 (例如通过
     Gymnasium 注册或直接构造，取决于你的项目组织方式) 。

提示与支持
----------

1. 查看仓库中的示例：

   - ``src/mjlab/tasks/``

2. 如果遇到问题：

   - 提交 issue： https://github.com/mujocolab/mjlab/issues
   - 发起讨论： https://github.com/mujocolab/mjlab/discussions

3. 记住 MuJoCo 与 Isaac Sim 之间的差异：

   - 一些 Omniverse / USD 渲染特性没有直接对应物。
   - 先专注于对齐 **物理与观测** ，之后再视需要打磨视觉效果。
