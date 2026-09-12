.. _entity_data:

实体数据
===========

本页面是 ``EntityData`` 的属性参考。关于 ``entity.data`` 如何融入整体数据访问体系的
概览，参见 :ref:`entity`。

所有属性都是 PyTorch 张量，直接基于 MuJoCo Warp 的 GPU 缓冲区，没有任何拷贝开销。
第一维始终是 ``num_envs``，即并行仿真的世界数量。

.. warning::

   读属性反映的是 ``sim.forward()`` 被调用之后的状态。如果你在同一个事件项中先写入
   仿真状态、再读取派生属性，请在写入和读取之间调用 ``sim.forward()``。环境步进序列
   已经这样做了；该警告只针对自定义的、混合了读写的 event 项。详细解释参见
   :ref:`FAQ <faq-sim-forward>`。


参考：根状态
-------------

根（root）属性描述实体根刚体的位置、姿态和速度。以 ``_w`` 结尾的属性在世界坐标系下
表示。以 ``_b`` 结尾的属性在实体的基座坐标系下表示。详见 :ref:`frame-conventions`。

每个实体有两个根参考点：**连杆原点** 和 **质心（COM）**，前者是 MJCF 中定义的 body
坐标系原点。哪一个适用取决于具体任务。

.. admonition:: MuJoCo 的混合坐标系 ``qvel``

   对于浮动基座实体，自由关节在 ``qvel`` 中存储 6 个自由度。MuJoCo 将 **线性** 分量
   表示在 **世界坐标系** 中，而将 **角** 分量表示在 **局部 body 坐标系** 中。
   EntityData 避开了这个陷阱：所有 ``_w`` 速度属性都由 ``cvel`` 计算得出（参见下文的
   :ref:`cvel-section`），并且完全在世界坐标系下表示。如果你直接读取
   ``env.sim.data.qvel``，请注意这一混合约定。

.. rubric:: 根连杆属性

.. list-table::
   :header-rows: 1
   :widths: 35 20 15 30

   * - 属性
     - 形状
     - 坐标系
     - 说明
   * - ``root_link_pose_w``
     - ``[num_envs, 7]``
     - world
     - 根连杆位置（3）与四元数（4）拼接
   * - ``root_link_pos_w``
     - ``[num_envs, 3]``
     - world
     - 根连杆位置
   * - ``root_link_quat_w``
     - ``[num_envs, 4]``
     - world
     - 根连杆姿态，四元数形式 (w, x, y, z)
   * - ``root_link_vel_w``
     - ``[num_envs, 6]``
     - world
     - 根连杆线速度（3）与角速度（3）拼接
   * - ``root_link_lin_vel_w``
     - ``[num_envs, 3]``
     - world
     - 根连杆线速度
   * - ``root_link_ang_vel_w``
     - ``[num_envs, 3]``
     - world
     - 根连杆角速度
   * - ``root_link_lin_vel_b``
     - ``[num_envs, 3]``
     - body
     - 基座坐标系下的根连杆线速度
   * - ``root_link_ang_vel_b``
     - ``[num_envs, 3]``
     - body
     - 基座坐标系下的根连杆角速度

.. rubric:: 根质心属性

.. list-table::
   :header-rows: 1
   :widths: 35 20 15 30

   * - 属性
     - 形状
     - 坐标系
     - 说明
   * - ``root_com_pose_w``
     - ``[num_envs, 7]``
     - world
     - 根质心位置（3）与四元数（4）拼接
   * - ``root_com_pos_w``
     - ``[num_envs, 3]``
     - world
     - 根质心位置
   * - ``root_com_quat_w``
     - ``[num_envs, 4]``
     - world
     - 根质心姿态，四元数形式 (w, x, y, z)
   * - ``root_com_vel_w``
     - ``[num_envs, 6]``
     - world
     - 根质心线速度（3）与角速度（3）拼接
   * - ``root_com_lin_vel_w``
     - ``[num_envs, 3]``
     - world
     - 根质心线速度
   * - ``root_com_ang_vel_w``
     - ``[num_envs, 3]``
     - world
     - 根质心角速度
   * - ``root_com_lin_vel_b``
     - ``[num_envs, 3]``
     - body
     - 基座坐标系下的根质心线速度
   * - ``root_com_ang_vel_b``
     - ``[num_envs, 3]``
     - body
     - 基座坐标系下的根质心角速度

.. rubric:: 派生根属性

.. list-table::
   :header-rows: 1
   :widths: 35 20 15 30

   * - 属性
     - 形状
     - 坐标系
     - 说明
   * - ``projected_gravity_b``
     - ``[num_envs, 3]``
     - body
     - 重力向量 (0, 0, -1) 旋转到基座坐标系后的结果。用于度量倾角：完全竖直的机器人
       读数为 ``[0, 0, -1]``。
   * - ``heading_w``
     - ``[num_envs]``
     - world
     - 根刚体前向轴投影到 XY 平面上的朝向角（弧度）。


参考：body 状态
----------------

body 属性给出实体所属全部刚体的运动学状态。第二维是 ``num_bodies``，即实体运动学树
中除世界之外的所有 body 数量。

.. list-table::
   :header-rows: 1
   :widths: 35 25 15 25

   * - 属性
     - 形状
     - 坐标系
     - 说明
   * - ``body_link_pose_w``
     - ``[num_envs, num_bodies, 7]``
     - world
     - 每个 body 的连杆位置（3）与四元数（4）
   * - ``body_link_pos_w``
     - ``[num_envs, num_bodies, 3]``
     - world
     - 每个 body 的连杆位置
   * - ``body_link_quat_w``
     - ``[num_envs, num_bodies, 4]``
     - world
     - 每个 body 的连杆姿态
   * - ``body_link_vel_w``
     - ``[num_envs, num_bodies, 6]``
     - world
     - 每个 body 的连杆线速度（3）与角速度（3）
   * - ``body_link_lin_vel_w``
     - ``[num_envs, num_bodies, 3]``
     - world
     - 每个 body 的连杆线速度
   * - ``body_link_ang_vel_w``
     - ``[num_envs, num_bodies, 3]``
     - world
     - 每个 body 的连杆角速度
   * - ``body_com_pose_w``
     - ``[num_envs, num_bodies, 7]``
     - world
     - 每个 body 的质心位置（3）与四元数（4）
   * - ``body_com_pos_w``
     - ``[num_envs, num_bodies, 3]``
     - world
     - 每个 body 的质心位置
   * - ``body_com_quat_w``
     - ``[num_envs, num_bodies, 4]``
     - world
     - 每个 body 的质心姿态
   * - ``body_com_vel_w``
     - ``[num_envs, num_bodies, 6]``
     - world
     - 每个 body 的质心线速度（3）与角速度（3）
   * - ``body_com_lin_vel_w``
     - ``[num_envs, num_bodies, 3]``
     - world
     - 每个 body 的质心线速度
   * - ``body_com_ang_vel_w``
     - ``[num_envs, num_bodies, 3]``
     - world
     - 每个 body 的质心角速度
   * - ``body_external_wrench``
     - ``[num_envs, num_bodies, 6]``
     - world
     - 施加到每个 body 上的外力（3）与外力矩（3）
   * - ``body_external_force``
     - ``[num_envs, num_bodies, 3]``
     - world
     - 施加到每个 body 上的外力
   * - ``body_external_torque``
     - ``[num_envs, num_bodies, 3]``
     - world
     - 施加到每个 body 上的外力矩


参考：关节状态
---------------

关节属性覆盖单自由度的转动关节和移动关节。自由关节（根部的浮动基座自由度）不包含在
内，请改用根状态属性。

.. list-table::
   :header-rows: 1
   :widths: 35 25 40

   * - 属性
     - 形状
     - 说明
   * - ``joint_pos``
     - ``[num_envs, num_joints]``
     - 关节位置，单位为弧度（转动关节）或米（移动关节）
   * - ``joint_pos_biased``
     - ``[num_envs, num_joints]``
     - 叠加了编码器偏置的关节位置。用于通过域随机化模拟编码器标定误差。
   * - ``joint_vel``
     - ``[num_envs, num_joints]``
     - 关节速度，单位为 rad/s 或 m/s
   * - ``joint_acc``
     - ``[num_envs, num_joints]``
     - 关节加速度，单位为 rad/s² 或 m/s²
   * - ``actuator_force``
     - ``[num_envs, num_actuators]``
     - 执行器空间中的标量输出（每个执行器一个）。这是经过传动雅可比投影之前的力。
       若需要关节空间中的执行器力，请使用 ``qfrc_actuator``。


.. _generalized-forces:

参考：广义力
-------------

这些属性暴露了 MuJoCo 广义力分解中选定的分量，切片为本实体的铰接关节自由度。自由
关节的自由度不包含在内。所有形状均为 ``[num_envs, nv]``，其中 ``nv`` 是属于本实体的
铰接自由度数量。

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - 属性
     - 说明
   * - ``qfrc_actuator``
     - 所有执行器产生并映射到关节空间的力。对于电机，这是指令力矩乘以减速比。对于
       位置和速度执行器，这是由内部 PD 控制律计算出的力。当关节启用了
       ``actuatorgravcomp`` 时，重力补偿力也包含在此项中。
   * - ``qfrc_external``
     - 通过 ``xfrc_applied`` 施加到 body 上的笛卡尔力/力矩在关节上产生的力。即
       :math:`J^\top F` 映射。MuJoCo 并不单独存储这一项；该属性在 ``forward()``
       之后从其他力分量中恢复得到。

参考：geom 和 site 状态
------------------------

.. list-table::
   :header-rows: 1
   :widths: 35 25 40

   * - 属性
     - 形状
     - 说明
   * - ``geom_pose_w``
     - ``[num_envs, num_geoms, 7]``
     - 世界坐标系下每个 geom 的位置（3）与四元数（4）
   * - ``geom_pos_w``
     - ``[num_envs, num_geoms, 3]``
     - 世界坐标系下每个 geom 的位置
   * - ``geom_quat_w``
     - ``[num_envs, num_geoms, 4]``
     - 世界坐标系下每个 geom 的姿态
   * - ``geom_vel_w``
     - ``[num_envs, num_geoms, 6]``
     - 世界坐标系下每个 geom 的线速度（3）与角速度（3）
   * - ``geom_lin_vel_w``
     - ``[num_envs, num_geoms, 3]``
     - 世界坐标系下每个 geom 的线速度
   * - ``geom_ang_vel_w``
     - ``[num_envs, num_geoms, 3]``
     - 世界坐标系下每个 geom 的角速度
   * - ``site_pose_w``
     - ``[num_envs, num_sites, 7]``
     - 世界坐标系下每个 site 的位置（3）与四元数（4）
   * - ``site_pos_w``
     - ``[num_envs, num_sites, 3]``
     - 世界坐标系下每个 site 的位置
   * - ``site_quat_w``
     - ``[num_envs, num_sites, 4]``
     - 世界坐标系下每个 site 的姿态
   * - ``site_vel_w``
     - ``[num_envs, num_sites, 6]``
     - 世界坐标系下每个 site 的线速度（3）与角速度（3）
   * - ``site_lin_vel_w``
     - ``[num_envs, num_sites, 3]``
     - 世界坐标系下每个 site 的线速度
   * - ``site_ang_vel_w``
     - ``[num_envs, num_sites, 3]``
     - 世界坐标系下每个 site 的角速度


参考：肌腱状态
---------------

肌腱属性仅在配备肌腱驱动执行器的实体上才会被填充。

.. list-table::
   :header-rows: 1
   :widths: 35 25 40

   * - 属性
     - 形状
     - 说明
   * - ``tendon_len``
     - ``[num_envs, num_tendons]``
     - 肌腱长度
   * - ``tendon_vel``
     - ``[num_envs, num_tendons]``
     - 肌腱速度


.. _frame-conventions:

坐标系约定
----------

属性名通过后缀标明其参考坐标系。

``_w`` (世界坐标系)
    一个固定的全局坐标系。原点通常位于场景原点，其坐标轴在整个回合内保持不变。当你
    需要绝对位置时，世界坐标系的量很有用，例如判断机器人是否跌落到某个高度阈值以下。

``_b`` (body 坐标系 / 基座坐标系)
    实体的根 body 坐标系。它随机器人一起平移和旋转。大多数观测项使用 body 坐标系的
    量，因为它们对机器人的朝向不敏感。在 body 坐标系下表示的速度，无论机器人朝北还是
    朝南，读数都相同，这让策略更容易泛化。

``projected_gravity_b`` 是体现坐标系后缀重要性的一个好例子。它取世界坐标系下的重力
向量 ``[0, 0, -1]``，将其旋转到基座坐标系。机器人竖直时结果为 ``[0, 0, -1]``；随着
机器人倾斜，x 和 y 分量逐渐增大，为策略提供了直接用于姿态纠正的信号。

四元数约定
^^^^^^^^^^

所有四元数都采用 ``(w, x, y, z)`` 约定，与 MuJoCo 一致。

约减状态与派生量
^^^^^^^^^^^^^^^^^

EntityData 的属性分为两类，它们相对于 ``sim.forward()`` 的行为不同：

**约减状态。** ``joint_pos`` 和 ``joint_vel`` 直接读取 MuJoCo 的 ``qpos`` 和
``qvel`` 数组。``write_joint_state_to_sim()`` 等写方法会直接修改这些数组，因此读取
总是最新的。

**派生量。** 所有位姿和速度属性（``*_pose_w``、``*_vel_w``、``*_vel_b``）都由
MuJoCo 的内部数组（``xpos``、``xquat``、``cvel``、``subtree_com`` 等）计算得出，而
这些数组只在 ``sim.forward()`` 运行时才更新。如果你先写入 ``qpos``/``qvel``，然后
在没有中间 ``forward()`` 的情况下读取派生属性，读到的将是过期的值。

环境步进序列会在恰当的时机调用 ``forward()``，所以只有当你编写在同一函数中既写又读的
自定义 event 项时才需要注意这一点。详见 :ref:`FAQ <faq-sim-forward>`。

.. _cvel-section:

速度属性如何由 ``cvel`` 计算得出
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

MuJoCo 并不直接存储世界坐标系下的线速度。它为每个 body 存储一个称为 ``cvel`` 的 6 维
空间速度（基于质心的速度），按 ``(angular[3], linear[3])`` 排列。该向量表示在
**c 系** 中：一个以 ``subtree_com`` 为中心（即 body 运动学子树的质心）、方向与世界
坐标系一致的坐标系。MuJoCo 使用这种表示来提高远离世界原点的
机构的数值精度。背景知识参见
`c-frame variables <https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#c-frame-variables>`_
和 Featherstone 的
`Spatial Algebra <http://royfeatherstone.org/spatial/>`_。

要恢复刚体上任意一点 :math:`\mathbf{p}` 处的世界坐标系线速度，我们使用标准的刚体速度
传递公式。设 :math:`\boldsymbol{\omega}` 和 :math:`\mathbf{v}_c` 分别为 ``cvel``
的角速度和线速度分量，:math:`\mathbf{c}` 表示 ``subtree_com``。由于 c 系与世界坐标系
方向一致，:math:`\boldsymbol{\omega}` 已经处于世界坐标系中。点
:math:`\mathbf{p}` 处的线速度为：

.. math::

   \mathbf{v}_p
     = \mathbf{v}_c
       - \boldsymbol{\omega} \times (\mathbf{c} - \mathbf{p})

EntityData 在 ``compute_velocity_from_cvel()`` 中应用此公式：

.. code-block:: python

   def compute_velocity_from_cvel(pos, subtree_com, cvel):
       lin_vel_c = cvel[..., 3:6]
       ang_vel_c = cvel[..., 0:3]
       offset = subtree_com - pos
       lin_vel_w = lin_vel_c - torch.cross(ang_vel_c, offset, dim=-1)
       ang_vel_w = ang_vel_c
       return torch.cat([lin_vel_w, ang_vel_w], dim=-1)

EntityData 中的每个速度属性（``root_link_vel_w``、``body_link_vel_w``、
``geom_vel_w``、``site_vel_w`` 及其 COM 变体）都使用该函数，只是代入相应的点：

- **连杆速度** 使用 ``xpos``，即 body 坐标系原点。
- **COM 速度** 使用 ``xipos``，即 body 质心。
- **geom/site 速度** 使用 ``geom_xpos``/``site_xpos``，其中 ``cvel`` 从其父 body
  查得。


默认位姿与相对量
-----------------

``entity.data.default_joint_pos`` 保存来自实体初始状态配置的关节位置
（``EntityCfg`` 的 ``init_state.joint_pos`` 字段）。它的形状为
``[num_envs, num_joints]``，并在初始化时复制到所有环境。

相对关节位置是当前关节位置相对该默认值的偏差：

.. code-block:: python

    joint_pos_rel = joint_pos - default_joint_pos

这正是 ``joint_pos_rel`` 观测函数所计算的内容：

.. code-block:: python

    def joint_pos_rel(env, asset_cfg):
        asset = env.scene[asset_cfg.name]
        jnt_ids = asset_cfg.joint_ids
        return (
            asset.data.joint_pos[:, jnt_ids]
            - asset.data.default_joint_pos[:, jnt_ids]
        )

相对关节位置为策略提供了姿态偏差的紧凑表示。当机器人处于默认位姿时，所有元素均为零。

类似地，``default_joint_vel`` 被 ``joint_vel_rel`` 观测函数使用。对大多数配置而言，
默认速度为零，因此 ``joint_vel_rel`` 与 ``joint_vel`` 完全相同。这层间接引用的存在，
是为了在动作模仿等任务中允许使用非零的参考速度。

关节位置动作配置中的 ``use_default_offset=True`` 选项以 ``default_joint_pos`` 作为
动作空间的零点，因此网络输出为零即表示命令机器人回到默认位姿。这是运动控制任务的
标准配置。
