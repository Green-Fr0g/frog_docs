.. _actions:

动作
====

动作定义策略如何控制仿真。动作管理器每步接收策略的输出张量，将其切分给各个已注册的动作项，并把每个片段路由到相应实体的执行器。每一项把策略输出中一段连续的部分映射为某组关节、肌腱或 site 上的一种控制模式（位置、速度、力）。

.. code-block:: python

    from mjlab.envs.mdp.actions import JointPositionActionCfg

    actions = {
        "joint_pos": JointPositionActionCfg(
            entity_name="robot",
            actuator_names=(".*",),   # regex matching actuator names
            scale=0.5,
            use_default_offset=True,  # action 0 = default pose
        ),
    }


通用参数
--------

所有动作类型都共享从 ``BaseActionCfg`` 继承的一组基础参数。

``entity_name`` 指定要控制的场景实体。``actuator_names`` 是一个正则模式元组，会与执行器（或肌腱/site）的名称进行匹配，以选出受控目标。

``scale`` 在应用任何偏移之前先乘以策略的原始输出。它接受一个标量，或一个把执行器名称模式映射到逐目标取值的字典。这样既能让策略输出保持在归一化范围内，又能映射到具有物理意义的单位。``offset`` 在缩放之后相加；关节类动作还提供 ``use_default_offset``，它会自动加载实体的默认关节位置或速度作为偏移，使原始输出为零时正好产生默认位姿。

``clip`` 可选地对处理后的动作（经过缩放与偏移之后）在送入执行器之前进行钳位。它接受一个把执行器名称模式映射到 ``(min, max)`` 元组的字典，解析方式与 ``scale`` 和 ``offset`` 相同。

.. code-block:: python

    JointPositionActionCfg(
        entity_name="robot",
        actuator_names=(".*",),
        scale=0.5,
        clip={".*_hip_.*": (-1.0, 1.0), ".*_knee_.*": (-0.5, 2.0)},
    )

动作会在每个 decimation 子步（物理步）都写入执行器目标，而不是每个策略步只写一次。这一点与观测延迟不同，后者以策略步为单位。


动作类型
--------

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - 类型
     - 描述
   * - ``JointPositionAction``
     - 设置关节位置目标。当 ``use_default_offset=True`` (默认值) 时，策略输出为零即对应默认位姿。来自 ``dr.encoder_bias`` 的编码器偏置会自动扣除，使随机化偏移能正确传播到控制命令。
   * - ``RelativeJointPositionAction``
     - 相对当前关节位置设置关节位置目标。目标为 ``current_pos + action * scale``，因此无论机器人当前处于何种构型，策略输出为零都会使其保持原地不动。
   * - ``JointVelocityAction``
     - 设置关节速度目标。``use_default_offset=True`` 使用默认关节速度（通常为零）。
   * - ``JointEffortAction``
     - 直接设置关节力（力矩）目标。没有默认偏移。
   * - ``TendonLengthAction``
     - 设置肌腱长度目标。目标通过将 ``actuator_names`` 与肌腱名称匹配来解析。
   * - ``TendonVelocityAction``
     - 设置肌腱速度目标。
   * - ``TendonEffortAction``
     - 设置肌腱力目标。
   * - ``SiteEffortAction``
     - 在指定 site 上施加力和力矩。适用于四旋翼等无人机——其推力施加在旋翼 site 上，而非通过关节执行器。


任务空间动作
------------

``DifferentialIKAction`` 通过阻尼最小二乘逆运动学，把笛卡尔位置与姿态命令转换为关节空间的位置目标。每个 decimation 子步执行一次 IK 迭代，因此末端执行器在子步之间持续跟踪目标，而不只是在策略频率上跟踪。

动作维度根据配置自动选择：

- ``orientation_weight == 0``: **3D** (仅位置)
- ``orientation_weight > 0, use_relative_mode=True``: **6D** (位置增量 + 轴角增量)
- ``orientation_weight > 0, use_relative_mode=False``: **7D** (绝对位置 + 四元数)

所有目标（位置、姿态、关节限位、姿态偏好）都被堆叠进单个 DLS 系统。把某个权重设为零即可禁用对应目标，且不增加求解开销。

``compute_dq()`` 方法只返回关节位移而不写入执行器目标，从而支持在 RL 训练之外的独立脚本中进行多轮迭代 IK。


动作维度与历史
--------------

呈现给策略的总动作维度是各已注册项 ``action_dim`` 之和。对于关节、肌腱和 site 动作，它等于匹配到的目标数量。对于 ``DifferentialIKAction``，则视激活的目标为 3、6 或 7。

动作管理器会跟踪最近三个动作向量：``action``、``prev_action`` 和 ``prev_prev_action``。诸如 ``last_action`` 的观测项，以及诸如 ``action_rate_l2`` 和 ``action_acc_l2`` 的奖励项，都从这些缓冲区读取。动作历史会在环境重置时清零，以免回合边界泄漏信息。


多个动作项
----------

一个环境可以注册任意数量的项。动作管理器按注册顺序拼接各项目的维度，在相应边界处切分策略的输出张量，并独立路由每个片段。

.. code-block:: python

    from mjlab.envs.mdp.actions import (
        JointPositionActionCfg,
        JointVelocityActionCfg,
    )

    actions = {
        "arm_joints": JointPositionActionCfg(
            entity_name="robot",
            actuator_names=(".*_arm_.*",),
            scale=0.5,
        ),
        "wheel_joints": JointVelocityActionCfg(
            entity_name="robot",
            actuator_names=(".*_wheel_.*",),
            scale=10.0,
        ),
    }

策略输出一个张量，其宽度等于所有项匹配到的目标总数。各项也可以面向不同的实体，例如一项控制机器人，另一项控制被操作的对象。
