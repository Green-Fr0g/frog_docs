挑战
====

这些开放式的挑战帮助你通过实现新功能来熟悉代码库。每个挑战都附有帮你上手的提示。

挑战 1：添加投射物 API
--------------------------------

**目标：** 为仿真器添加一个 API，用于生成并向机器人发射投射物（用于鲁棒性测试）。

**难度：** 中等

**你将学到：**

* 仿真器抽象层
* 动态生成物体
* 设置物体状态

**提示：**

1. 看看每个仿真器是如何添加物体的。投射物不需要用到 SceneLib
2. 同时考虑 IsaacGym 和 Newton 两种实现

**起点：**

添加类似这样的方法：

.. code-block:: python

   class BaseSimulator:
       def spawn_projectile(self, position, velocity, mass=1.0):
           """Spawn a projectile at position with initial velocity."""
           pass
       
       def update_projectiles(self):
           """Step projectile physics and check for collisions."""
           pass

挑战 2：走廊场景
---------------------------

**目标：** 使用 SceneLib 的长方体在一段行走动作周围创建走廊环境，
迫使角色穿过狭窄通道。

**难度：** 中等偏易

**你将学到：**

* SceneLib API
* 场景与动作的对齐
* 环境定制

**提示：**

1. 场景创建参见 ``examples/tutorial/3_scene_creation.py``
2. 使用 ``object_type="box"`` 的 ``SceneObject`` 充当墙壁
3. 训练前先用 ``env_kinematic_playback.py`` 测试

**示例场景结构：**

.. code-block:: python

   left_wall = SceneObject(
       object_type="box",
       position=[-1.0, 0.0, 1.0],
       dimensions=[0.1, 10.0, 2.0],  # thin, long, tall
       fix_base_link=True,
   )
   right_wall = SceneObject(
       object_type="box",
       position=[1.0, 0.0, 1.0],
       dimensions=[0.1, 10.0, 2.0],
       fix_base_link=True,
   )

挑战 3：添加 T1 机器人支持
---------------------------------

**目标：** 按照自定义机器人指南添加 Booster T1 人形机器人。

**难度：** 中等偏难

**你将学到：**

* 机器人配置系统
* MJCF 文件要求
* 重定向管线

**提示：**

1. 参考自定义机器人指南和重定向指南

挑战 4：Steering 的下蹲奖励
------------------------------------------

**目标：** 修改纯 RL 的 Steering 任务，加入下蹲奖励，
教会机器人在保持低姿态的同时行走。

**难度：** 简单

**你将学到：**

* 奖励配置
* 环境定制
* 奖励函数设计

**提示：**

1. Steering 配置参见 ``examples/experiments/steering/mlp.py``
2. 添加一个惩罚过高根节点高度的奖励组件
3. 考虑把目标高度做成参数

**示例奖励：**

.. code-block:: python

   from protomotions.envs.context_views import EnvContext
   from protomotions.envs.mdp_component import MdpComponent
   from protomotions.envs.rewards.base import mean_squared_error_exp
   
   # Add a simple crouch reward kernel
   def compute_crouch_rew(root_height, target_height, coefficient):
       return mean_squared_error_exp(root_height, target_height, coefficient)
   
   # Then in reward_components:
   "crouch_rew": MdpComponent(
       compute_func=compute_crouch_rew,
       dynamic_vars={
           "root_height": EnvContext.current.root_height,
           "target_height": EnvContext.current.root_height,  # Will broadcast scalar
       },
       static_params={"weight": 1.0, "coefficient": -10.0, "target_height": 0.6},
   )

挑战 5：扩展 Agent 类
----------------------------------

**目标：** 实现一种新的 RL 算法，作为自定义智能体。

**难度：** 困难

**你将学到：**

* Agent 抽象
* 训练循环设计
* 算法实现

**起点：**

1. 研究 ``protomotions/agents/mimic/agent_add.py`` 中 ADD 的实现方式
2. 看看其他 Agent 是如何扩展 BaseAgent 的

挑战 6：OMOMO 数据集加载器
---------------------------------

**目标：** 为 `OMOMO dataset <https://omomo.stanford.edu/>`_ 创建一个数据加载器，
将 SMPL/AMASS 格式的人体动作与对应的物体形状和动作配对，
生成与每个动作片段匹配的 SceneLib 场景。

**难度：** 中等偏难

**你将学到：**

* AMASS/SMPL 动作数据格式
* 用于网格和运动物体的 SceneLib API
* 动作与场景的同步
* 数据管线设计

**背景：**

OMOMO 包含人-物交互数据，其中：

* SMPL 格式的人体动作（与 AMASS 管线兼容）
* 物体网格（OBJ 文件）
* 物体运动轨迹（随时间变化的 6 自由度位姿）

**提示：**

1. 从 :doc:`workflows/amass_smpl` 中现有的 AMASS 工作流入手
2. 使用 ``MeshSceneObject`` 加载 OBJ 文件表示的物体形状
3. SceneLib 支持运动物体 —— 以序列形式提供平移/旋转
4. 让物体运动的 FPS 与人形动作的 FPS 保持一致
5. 场景创建模式参见 ``examples/tutorial/3_scene_creation.py``

**示例场景结构：**

.. code-block:: python

   from protomotions.components.scene_lib import (
       Scene, MeshSceneObject, ObjectOptions, SceneLib
   )
   
   def create_omomo_scene(motion_id, obj_mesh_path, obj_translations, obj_rotations, fps):
       """Create a scene pairing humanoid motion with object motion."""
       
       options = ObjectOptions(
           density=500,
           fix_base_link=False,  # Object moves
       )
       
       obj = MeshSceneObject(
           mesh_file=obj_mesh_path,
           translation=obj_translations,  # (N, 3) array for N frames
           rotation=obj_rotations,         # (N, 4) array, quaternion xyzw
           options=options,
           fps=fps,
       )
       
       return Scene(objects=[obj], humanoid_motion_id=motion_id)
   
   # Build scenes for all OMOMO clips
   scenes = []
   for clip in omomo_clips:
       scene = create_omomo_scene(
           motion_id=clip.motion_id,
           obj_mesh_path=clip.object_mesh,
           obj_translations=clip.object_positions,
           obj_rotations=clip.object_orientations,
           fps=clip.fps,
       )
       scenes.append(scene)
   
   SceneLib.save_scenes_to_file(scenes, "omomo_scenes.pt")

**验证步骤：**

1. 用 ``env_kinematic_playback.py`` 可视化，验证对齐是否正确
2. 检查物体运动是否与人体接触时机吻合
3. 确保人体数据与物体数据的坐标系一致
