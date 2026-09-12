添加自定义机器人
=====================

本指南以 H1_2 机器人为参考，介绍如何在 ProtoMotions 中添加新机器人。
我们聚焦于**需要改动的部分**，而非面面俱到的细节。

概述：需要改什么
------------------------------

添加一个机器人需要在以下几个方面进行改动：

1. **MJCF 文件** - 机器人物理定义
2. **机器人配置** - ProtoMotions 配置
3. **工厂注册** - 让机器人可以按名称使用
4. **重定向脚本** （可选）- 用于动作迁移
5. **动作转换** （可选）- 用于重定向后的动作

全文将以 H1_2（Unitree H1 v2）和 G1 作为参考。

步骤 1：MJCF 文件
-----------------

在 ``protomotions/data/assets/mjcf/`` 中创建你的机器人的 MJCF 文件。

**关键要求：**

* 根刚体带有 ``<freejoint/>``，形成浮动基座
* 所有关节具有正确的限位和轴
* 用于物理仿真的碰撞几何体

**参考：** 对比 ``h1_2_no_mesh_box_feet.xml`` 与 ``g1_bm_no_mesh_box_feet.xml``，
了解命名约定。

.. note::

   如果你只有 URDF，请先转换为 MJCF。MJCF 是基准真值的机器人规格说明。

步骤 2：机器人配置
--------------------

创建 ``protomotions/robot_configs/<your_robot>.py``。需要定义的关键字段：

**刚体名称映射：**

将通用名称映射到你的机器人的刚体名称，用于接触检测、观测等。

.. code-block:: python

   # From H1_2 config
   common_naming_to_robot_body_names: Dict[str, List[str]] = field(
       default_factory=lambda: {
           "all_left_foot_bodies": ["left_ankle_roll_link"],  # Your foot link
           "all_right_foot_bodies": ["right_ankle_roll_link"],
           "all_left_hand_bodies": ["left_wrist_yaw_link"],   # Your hand link
           "all_right_hand_bodies": ["right_wrist_yaw_link"],
           "head_body_name": ["head_aux"],                     # Your head link
           "torso_body_name": ["torso_link"],                  # Your torso link
       }
   )

**G1 与 H1_2 对比：**

* G1 的手使用 ``left_rubber_hand``，H1_2 使用 ``left_wrist_yaw_link``
* G1 的头使用 ``head``，H1_2 使用 ``head_aux``
* 关节名称不同但结构相同

**可跟踪刚体：**

MaskedMimic 使用的刚体：

.. code-block:: python

   trackable_bodies_subset: List[str] = field(
       default_factory=lambda: [
           "torso_link", "head_aux",
           "right_ankle_roll_link", "left_ankle_roll_link",
           "left_wrist_yaw_link", "right_wrist_yaw_link",
       ]
   )

**资产配置：**

.. code-block:: python

   asset: RobotAssetConfig = field(
       default_factory=lambda: RobotAssetConfig(
           asset_file_name="mjcf/your_robot.xml",  # MJCF is the source of truth; IsaacLab converts to USD
           self_collisions=False,  # Enable if needed
       )
   )

**默认根节点高度：**

用于重置/初始化的站立高度：

.. code-block:: python

   default_root_height: float = 1.03  # H1_2 is taller than G1 (0.8)

**PD 控制参数：**

使用正则表达式模式按关节定义刚度/阻尼：

.. code-block:: python

   control: ControlConfig = field(
       default_factory=lambda: ControlConfig(
           control_type=ControlType.BUILT_IN_PD,
           override_control_info={
               # Hip joints - high torque
               ".*_hip_(yaw|pitch|roll)_joint": ControlInfo(
                   stiffness=STIFFNESS_200,
                   damping=DAMPING_200,
                   effort_limit=200,
                   velocity_limit=50,
               ),
               # Knee joints - highest torque
               ".*_knee_joint": ControlInfo(
                   stiffness=STIFFNESS_300,
                   damping=DAMPING_300,
                   effort_limit=300,
               ),
               # ... more joints
           },
       )
   )

**特定于仿真器的参数：**

.. code-block:: python

   simulation_params: SimulatorParams = field(
       default_factory=lambda: SimulatorParams(
           isaacgym=IsaacGymSimParams(
               fps=100, decimation=2, substeps=2,
               physx=IsaacGymPhysXParams(
                   num_position_iterations=8,
                   num_velocity_iterations=4,
               ),
           ),
           newton=NewtonSimParams(fps=200, decimation=4),
       )
   )

步骤 3：注册到工厂
---------------------------

添加到 ``protomotions/robot_configs/factory.py``：

.. code-block:: python

   elif robot_name == "your_robot":
       from protomotions.robot_configs.your_robot import YourRobotConfig
       config = YourRobotConfig()

步骤 4：用随机姿态可视化器测试
----------------------------------------

训练前，先验证你的机器人能正确加载：

.. code-block:: bash

   python examples/random_pose_visualizer.py \
       --robot your_robot \
       --simulator isaacgym

这会在**零重力和零力矩**下将机器人设置为随机姿态。
机器人应能保持其重置姿态（按 R 键重置）。


步骤 5：重定向脚本（可选）
-------------------------------------

要将动作重定向到你的机器人，需要创建一个重定向脚本。

详情参见 :doc:`retargeting_pyroki`。

多仿真器（IsaacLab）注意事项
-----------------------------------------

对于 IsaacLab，你还需要一个 USD 资产。MJCF→USD 转换在单独的教程中介绍。

修改 MJCF 后，确保所有仿真器看到的是同一个机器人：

1. 从更新后的 MJCF 重新导出 USD
2. 用 ``random_pose_visualizer.py`` 在每个仿真器上测试
3. 验证关节顺序和限位是否一致

下一步
----------

* :doc:`retargeting_pyroki` - 将动作重定向到你的机器人
* :doc:`../../concepts/pose_lib` - 了解正向运动学/逆运动学（FK/IK）工具
* :doc:`../../concepts/abstractions` - 机器人配置架构
