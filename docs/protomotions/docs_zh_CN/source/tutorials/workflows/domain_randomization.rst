域随机化与 Sim2Sim
==============================

本工作流介绍如何用域随机化进行训练，以获得能在不同仿真器之间迁移（sim2sim）
或迁移到真机（sim2real）的鲁棒策略。

关于从数据到部署的完整端到端管线，参见 :doc:`g1_deployment`。

为什么需要域随机化？
-------------------------

在仿真中训练的策略，部署到不同的物理引擎或真实硬件时常常会失败，
原因在于"现实差距"。域随机化通过以下方式解决这一问题：

1. **随机化物理参数** （摩擦力、质心）
2. **添加动作噪声** （电机执行不精确）
3. **添加观测噪声** （IMU、编码器的传感器噪声）
4. **施加外部扰动** （推撞、速度脉冲）
5. **迫使策略** 对参数变化保持鲁棒

使用域随机化训练
-----------------------------------

BeyondMimic L2C2 实验配置（``examples/experiments/mimic/mlp_bm_l2c2.py``）
是域随机化训练的一个很好的起点：

.. code-block:: bash

   python protomotions/train_agent.py \
       --robot-name g1 \
       --simulator isaaclab \
       --experiment-path examples/experiments/mimic/mlp_bm_l2c2.py \
       --experiment-name g1_bm_dr \
       --motion-file /path/to/bones_seed_g1_motions.pt \
       --num-envs 4096 \
       --batch-size 16384

你也可以自行创建带域随机化设置的实验配置。下文介绍的各种随机化类型都是
通用的，可以混入任何实验配置。


域随机化的类型
--------------------------

ProtoMotions 通过 ``DomainRandomizationConfig`` 支持多种随机化类型。
以下是预训练的 G1 BeyondMimic 跟踪器
（``data/pretrained_models/motion_tracker/g1-bones-deploy/experiment_config.py``）
所使用的设置。你可以根据你的机器人和部署条件调整取值范围。

**动作噪声：**

.. code-block:: python

   ActionNoiseDomainRandomizationConfig(
       action_noise_range=(-0.025, 0.025),  # +/-2.5% noise on PD targets
       dof_names=[".*"],  # Apply to all joints
   )

**摩擦力随机化：**

.. code-block:: python

   FrictionDomainRandomizationConfig(
       num_buckets=64,
       static_friction_range=(0.3, 1.6),
       dynamic_friction_range=(0.3, 1.2),
       restitution_range=(0.0, 0.5),
       body_names=[".*"],  # Apply to all bodies
   )

.. note::

   **默认值**：在未显式设置数值时，ProtoMotions 假定所有实体
   （机器人刚体和地形）的默认摩擦系数为 **1.0**、恢复系数为 **0.0**。
   这保证了各仿真器之间的行为一致。

**场景物体资产随机化：**

场景物体可以通过 ``ObjectOptions`` 定义确定性的基础属性。在场景库中，
网格物体和图元物体可以设置 ``mass`` 或 ``density``（二者只能取其一），
以及 ``static_friction``、``dynamic_friction`` 和 ``restitution``。
``ObjectAssetDomainRandomizationConfig`` 会对这些属性采样绝对覆盖值；
对选中的资产分桶，采样值会替换场景库中的基础值。
它们不是加性或乘性的偏移量。这些范围对所有场景物体资产全局生效；
目前不支持按资产配置范围。

.. code-block:: python

   DomainRandomizationConfig(
       object_assets=ObjectAssetDomainRandomizationConfig(
           num_buckets=32,
           static_friction_range=(0.4, 1.4),
           dynamic_friction_range=(0.3, 1.0),
           restitution_range=(0.0, 0.2),
           mass_range=(0.5, 3.0),
           center_of_mass_range={
               "x": (-0.05, 0.05),
               "y": (-0.02, 0.02),
               "z": (0.00, 0.10),
           },
       )
   )

``mass_range`` 与 ``density_range`` 互斥，与 ``ObjectOptions`` 保持一致。
``center_of_mass_range`` 只能通过域随机化设置；它是绝对的局部质心值，
省略的轴默认为 ``0.0``。IsaacLab 和 IsaacGym 会将这些场景物体资产属性
同时应用于图元物体和网格物体。Newton 目前不生成场景库物体，
因此物体资产随机化在 Newton 上不生效。

**质心随机化：**

.. code-block:: python

   CenterOfMassDomainRandomizationConfig(
       com_range={"x": (-0.025, 0.025), "y": (-0.05, 0.05), "z": (-0.05, 0.05)},
       body_names=["torso_link"],  # Apply to torso
   )

**观测噪声：**

为观测添加高斯噪声，以提升策略对真实世界传感器缺陷的鲁棒性。
噪声水平是根据经验设定的，目的是让策略保持鲁棒——
并非针对特定传感器数据手册校准。

BM 跟踪器配置通过 ``RobotNoiseConfig`` 使用逐组件噪声：

.. code-block:: python

   RobotNoiseConfig(
       dof_pos_noise=0.01,         # Joint encoder noise (radians)
       dof_vel_noise=0.5,          # Joint velocity noise (rad/s)
       anchor_rot_noise=0.05,      # Torso IMU orientation noise (quat components)
       anchor_ang_vel_noise=0.2,   # Pelvis IMU gyroscope noise (rad/s)
   )

推理时（以及导出的 ONNX 模型中）所有噪声都会被禁用——
策略看到的是干净的传感器数据，但它已经学会了应对训练中出现的噪声水平。

配置了观测噪声后，环境会在上下文中同时提供状态变量的干净版本与带噪版本。
观测组件可以通过 ``use_noisy`` 参数请求带噪输入（供 actor 使用）
或干净输入（供 critic 使用）：

.. code-block:: python

   # Noisy observations for actor (helps sim-to-real transfer)
   "noisy_obs": reduced_coords_obs_factory(use_noisy=True),

   # Clean observations for critic (asymmetric actor-critic)
   "clean_obs": reduced_coords_obs_factory(use_noisy=False),

**推撞/扰动随机化：**

.. code-block:: python

   PushDomainRandomizationConfig(
       push_interval_range=(1.0, 3.0),         # Seconds between pushes
       max_linear_velocity=(0.5, 0.5, 0.2),    # Max push velocity (x, y, z) m/s
       max_angular_velocity=(0.52, 0.52, 0.78), # Max angular impulse (rad/s)
   )

这能帮助策略学会从意外扰动中恢复，提升其在真实硬件上的鲁棒性——
真机上机器人可能被碰撞或推挤。

**重置噪声（初始状态扰动）：**

.. code-block:: python

   RobotNoiseConfig(
       dof_pos_noise=0.1,
       root_pos_noise=[0.05, 0.05, 0.01],
       root_rot_noise=[0.1, 0.1, 0.2],
       root_vel_noise=[0.1, 0.1, 0.05],
       root_ang_vel_noise=[0.1, 0.1, 0.1],
   )

在每个回合开始时，机器人的初始状态会在参考动作第一帧附近受到扰动。
这能防止策略依赖一个完美的起始姿态。


摩擦力组合模式的自动转换
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

不同的物理引擎使用不同的摩擦力组合模式：

* **IsaacGym / IsaacLab (PhysX)**：使用 ``AVERAGE`` —— 有效摩擦力是
  机器人摩擦力与地形摩擦力的平均值：``(robot + terrain) / 2``
* **MuJoCo**：使用 ``MAX`` —— 有效摩擦力是二者的最大值：
  ``max(robot, terrain)``

当切换仿真器时，ProtoMotions 会通过 ``convert_friction_for_simulator()``
**自动转换** 摩擦力设置。你可以用任意组合模式配置摩擦力，
系统会保证各仿真器之间具有等效的有效摩擦力行为。

**工作原理：**

当仿真器使用 ``MAX`` 组合模式时：

1. 角色形状的摩擦力由 ``simulator.default_robot_friction`` 设定
2. 调整地形摩擦力，以保持配置的有效值
3. 域随机化得到的角色摩擦力会针对选中的刚体覆盖基线值

即使禁用域随机化，配置的角色摩擦力也能保持显式生效。

这一转换是透明的——你不需要为不同的仿真器修改配置。
同一个实验配置可以在 IsaacGym、IsaacLab 和 MuJoCo 上以等效的
摩擦力行为运行。


L2C2 平滑正则化
------------------------------

BM 跟踪器配置还使用了 **L2C2** （局部 Lipschitz 连续约束，
Kobayashi 2022），在观测带噪的情况下鼓励策略输出平滑：

* 同时计算每个 actor 观测的带噪版本和干净版本
* 策略对两者分别前向，得到 ``mu_noisy`` 和 ``mu_clean``
* 一个辅助损失惩罚 ``MSE(mu_noisy, mu_clean)``
* 这鼓励策略无论传感器噪声如何都输出相近的动作

推理时只使用干净的（无噪声）观测，L2C2 组件会被移除。


Sim2Sim 测试
---------------

完成域随机化训练后，先在 MuJoCo 上测试迁移效果，再进行真机部署：

.. code-block:: bash

   python protomotions/inference_agent.py \
       --checkpoint results/g1_bm_dr/last.ckpt \
       --simulator mujoco \
       --motion-file /path/to/motion.motion

MuJoCo 的接触动力学、求解器和摩擦力组合模式都与训练仿真器（IsaacLab）不同。
一个能在两者上都正常工作的策略，学到的才是鲁棒的动力学，
而不是对某个物理引擎的过拟合。

.. warning::

   **球形关节限制**：sim2sim 迁移目前仅适用于使用铰链（转动）关节的机器人，
   例如 G1 和 H1。使用球形（球窝）关节的机器人——如 SMPL 和 SMPL-X——
   其球形关节在不同仿真器（IsaacGym/IsaacLab 与 Newton/MuJoCo）中的
   表示不同，尚不支持跨仿真器迁移这些形体结构。

更完整的部署验证，参见 :doc:`g1_deployment` （步骤 4）中介绍的独立 MuJoCo
测试脚本，它可以在完全不依赖 ProtoMotions 训练框架的情况下运行导出的 ONNX 模型。


训练建议
-------------

**先不加 DR 训练**：先训练一个不带域随机化的基线。这能确认你的动作数据和
奖励工作正常。根据我们的经验，DR 并不会让训练明显变难。

**观测历史**：一些配置会使用观测历史，帮助策略从最近的状态转移中推断物理参数。
BM 跟踪器配置使用上一步处理后的动作作为单步历史。

**噪声水平**：上述噪声值是根据经验设定的，用于训练出鲁棒的策略。
如果你的真机传感器特别嘈杂或特别干净，请相应调整噪声范围。
拿不准时，宁可噪声偏大——过度正则化总好过一个脆弱的策略。


下一步
----------

* :doc:`g1_deployment` - 从数据到真机部署的完整管线
* :doc:`custom_robot` - 添加你的机器人进行 DR 训练
* :doc:`../../concepts/abstractions` - 理解仿真器抽象
