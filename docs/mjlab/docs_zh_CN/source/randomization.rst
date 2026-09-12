.. _domain_randomization:

域随机化
====================

域随机化（domain randomization）在训练过程中对物理参数进行随机化，使策略对建模误差和现实世界的差异具有鲁棒性。本指南介绍如何使用 ``EventTermCfg`` 和 ``dr`` 模块为环境附加随机化项。

快速上手
-----------

使用一个 ``EventTermCfg`` ，调用 ``dr`` 中类型化的函数，并指定一个 **取值范围** 和一个 **操作方式** ，用于描述如何施加采样值。

.. code-block:: python

    from mjlab.envs.mdp import dr
    from mjlab.managers.event_manager import EventTermCfg
    from mjlab.managers.scene_entity_config import SceneEntityCfg

    foot_friction: EventTermCfg = EventTermCfg(
        mode="reset",  # randomize each episode
        func=dr.geom_friction,
        params={
            "asset_cfg": SceneEntityCfg("robot", geom_names=[".*_foot.*"]),
            "ranges": (0.3, 1.2),
            "operation": "abs",
        },
    )

每个 ``dr`` 函数都带有 ``@requires_model_fields`` 装饰器，它会自动追踪两类信息：需要为逐世界存储而展开的字段， **以及** 保持 :ref:`派生量 <dr-recomputation>` 一致所需的 ``RecomputeLevel`` 级别。

``mode`` 参数控制事件何时触发：

* ``"startup"`` 在初始化时随机化一次
* ``"reset"`` 在每次回合重置时随机化
* ``"interval"`` 按固定时间间隔随机化


可用函数
-------------------

模型字段函数
^^^^^^^^^^^^^^^^^^^^^

本节中的每个函数都写入 ``sim.model`` (即 MuJoCo Warp 模型)上的单个字段。例如， ``dr.geom_friction`` 写入 ``sim.model.geom_friction`` ， ``dr.body_mass`` 写入 ``sim.model.body_mass`` ，依此类推。大多数函数共享 ``(env, env_ids, ranges, ...)`` 签名，由 ``distribution`` 和 ``operation`` 控制采样与应用方式(参见 :ref:`dr-parameters`)。某些函数的名字比底层 MuJoCo 字段名更易读；此时原始字段名会作为别名提供(``dr.body_com_offset`` 与 ``dr.body_ipos`` 是同一个函数)。

.. rubric:: Geom 字段

.. list-table::
   :header-rows: 1
   :widths: 28 18 34 20

   * - 函数
     - MuJoCo 字段
     - 说明
     - 备注
   * - ``dr.geom_friction``
     - ``geom_friction``
     - 滑动、扭转和滚动摩擦系数
     - 默认轴：0(仅切向)
   * - ``dr.geom_pos``
     - ``geom_pos``
     - geom 在父 body 坐标系中的位置
     -
   * - ``dr.geom_quat``
     - ``geom_quat``
     - geom 坐标系的朝向
     - 接受 roll/pitch/yaw 范围(弧度)；与默认值叠加复合
   * - ``dr.geom_rgba``
     - ``geom_rgba``
     - 颜色与透明度(RGBA)
     -
   * - ``dr.geom_size``
     - ``geom_size``
     - geom 特定的尺寸参数(半径、半长等)
     - 自动重算 ``geom_rbound`` 和 ``geom_aabb``
   * - ``dr.geom_matid``
     - ``geom_matid``
     - geom 渲染时使用的烘焙材质
     - 从 ``asset_cfg.material_names`` 中均匀采样

.. rubric:: Body 字段

.. list-table::
   :header-rows: 1
   :widths: 28 18 34 20

   * - 函数
     - MuJoCo 字段
     - 说明
     - 备注
   * - ``dr.body_mass``
     - ``body_mass``
     - body 的质量
     - 触发 ``set_const`` 重算
   * - ``dr.body_com_offset`` (别名 ``body_ipos``)
     - ``body_ipos``
     - 质心相对于 body 坐标系的位置
     - 触发 ``set_const``
   * - ``dr.body_pos``
     - ``body_pos``
     - body 坐标系在父坐标系中的位置
     - 触发 ``set_const_0``
   * - ``dr.body_quat``
     - ``body_quat``
     - body 坐标系的朝向
     - 接受 roll/pitch/yaw 范围(弧度)；与默认值叠加复合；
       触发 ``set_const_0``

.. rubric:: Joint 字段

.. list-table::
   :header-rows: 1
   :widths: 28 18 34 20

   * - 函数
     - MuJoCo 字段
     - 说明
     - 备注
   * - ``dr.joint_damping`` (别名 ``dof_damping``)
     - ``dof_damping``
     - 与速度成正比的阻尼力(被动)
     -
   * - ``dr.joint_armature`` (别名 ``dof_armature``)
     - ``dof_armature``
     - 附加的转子惯量(用于建模带减速器的传动)
     - 触发 ``set_const_0``
   * - ``dr.joint_friction`` (别名 ``dof_frictionloss``)
     - ``dof_frictionloss``
     - 关节中的干摩擦损耗
     -
   * - ``dr.joint_stiffness`` (别名 ``jnt_stiffness``)
     - ``jnt_stiffness``
     - 将关节拉向参考位置的弹簧刚度
     -
   * - ``dr.joint_limits`` (别名 ``jnt_range``)
     - ``jnt_range``
     - 关节位置的下限和上限
     -
   * - ``dr.joint_default_pos`` (别名 ``qpos0``)
     - ``qpos0``
     - 参考关节位置(零弹簧平衡点)
     - 触发 ``set_const_0``

.. rubric:: Site 字段

.. list-table::
   :header-rows: 1
   :widths: 28 18 34 20

   * - 函数
     - MuJoCo 字段
     - 说明
     - 备注
   * - ``dr.site_pos``
     - ``site_pos``
     - site 坐标系在父 body 坐标系中的位置
     -
   * - ``dr.site_quat``
     - ``site_quat``
     - site 坐标系的朝向
     - 接受 roll/pitch/yaw 范围(弧度)；与默认值叠加复合

.. rubric:: Camera 字段

.. list-table::
   :header-rows: 1
   :widths: 28 18 34 20

   * - 函数
     - MuJoCo 字段
     - 说明
     - 备注
   * - ``dr.cam_fovy``
     - ``cam_fovy``
     - 垂直视场角(度)
     -
   * - ``dr.cam_pos``
     - ``cam_pos``
     - 相机在父 body 坐标系中的位置
     -
   * - ``dr.cam_quat``
     - ``cam_quat``
     - 相机朝向
     - 接受 roll/pitch/yaw 范围(弧度)；与默认值叠加复合
   * - ``dr.cam_intrinsic``
     - ``cam_intrinsic``
     - 焦距与主点 ``[fx, fy, cx, cy]``
     -

.. rubric:: Light 字段

.. list-table::
   :header-rows: 1
   :widths: 28 18 34 20

   * - 函数
     - MuJoCo 字段
     - 说明
     - 备注
   * - ``dr.light_pos``
     - ``light_pos``
     - 光源在父 body 坐标系中的位置
     -
   * - ``dr.light_dir``
     - ``light_dir``
     - 光源方向向量
     -

.. rubric:: Material 字段

.. list-table::
   :header-rows: 1
   :widths: 28 18 34 20

   * - 函数
     - MuJoCo 字段
     - 说明
     - 备注
   * - ``dr.mat_rgba``
     - ``mat_rgba``
     - 材质 RGBA 颜色(为纹理着色)
     -
   * - ``dr.mat_emission``
     - ``mat_emission``
     - 自发光系数
     - 用于 MuJoCo Warp RGB 渲染
   * - ``dr.mat_specular``
     - ``mat_specular``
     - ``[0, 1]`` 范围内的镜面反射强度
     - 缩放 MuJoCo Warp RGB 的镜面反射分量
   * - ``dr.mat_shininess``
     - ``mat_shininess``
     - ``[0, 1]`` 范围内的表面光泽度
     - 用于 MuJoCo Warp RGB 渲染
   * - ``dr.mat_texrepeat``
     - ``mat_texrepeat``
     - 纹理在 S/T 方向上的重复次数
     - 仅对带纹理的材质生效；取值应保持为正

.. rubric:: 接触对字段

.. list-table::
   :header-rows: 1
   :widths: 28 18 34 20

   * - 函数
     - MuJoCo 字段
     - 说明
     - 备注
   * - ``dr.pair_friction``
     - ``pair_friction``
     - 每个接触对的摩擦覆盖值 ``[tangent1, tangent2, spin, roll1, roll2]``
     - 默认轴：0(tangent1，要求 ``condim >= 3`` )。使用 ``isotropic=True``
       可令 tangent2 = tangent1(以及 roll2 = roll1)同步镜像。会覆盖显式
       定义的 `<contact><pair> <https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-pair>`_
       元素的逐 geom 摩擦。参见 :ref:`dr-pair-friction` 。

.. rubric:: 肌腱字段

.. list-table::
   :header-rows: 1
   :widths: 28 18 34 20

   * - 函数
     - MuJoCo 字段
     - 说明
     - 备注
   * - ``dr.tendon_damping``
     - ``tendon_damping``
     - 沿肌腱方向、与速度成正比的阻尼
     -
   * - ``dr.tendon_stiffness``
     - ``tendon_stiffness``
     - 沿肌腱的弹簧刚度
     -
   * - ``dr.tendon_friction`` (别名 ``tendon_frictionloss``)
     - ``tendon_frictionloss``
     - 沿肌腱的干摩擦损耗
     -
   * - ``dr.tendon_armature``
     - ``tendon_armature``
     - 与肌腱速度相关的惯量
     - 触发 ``set_const_0``

实体级函数
^^^^^^^^^^^^^^^^^^^^^^

上面的函数都写入单个 ``sim.model`` 字段。下面的函数则作用于 mjlab 实体级别，因为它们一次会触及多个模型字段，或者修改的不是 MuJoCo 模型上的实体状态。

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - 函数
     - 功能说明
   * - ``dr.pseudo_inertia``
     - 通过伪惯量矩阵参数化(Rucker & Wensing 2022)对 ``body_mass`` 、
       ``body_ipos`` 、 ``body_inertia`` 和 ``body_iquat`` 进行物理一致的
       联合随机化。保证惯性张量正定且质量为正。详见
       :ref:`dr-pseudo-inertia` 一节。
   * - ``dr.pd_gains``
     - 同时随机化刚度(kp)和阻尼(kd)。对 ``BuiltinPositionActuator`` 和
       ``XmlActuator`` 会写入 ``actuator_gainprm`` 和 ``actuator_biasprm`` ；
       对 ``IdealPdActuator`` 则直接在实体上设置增益。三者均支持内联
       延迟字段。
   * - ``dr.effort_limits``
     - 随机化执行器力范围(``actuator_forcerange``)。对
       ``IdealPdActuator`` 还会更新实体内部的力限制。支持
       ``BuiltinPositionActuator`` 、 ``XmlActuator`` 和
       ``IdealPdActuator`` 。
   * - ``dr.encoder_bias``
     - 为位置读数添加每个关节固定的偏置，以模拟编码器标定误差。
       写入 ``entity.data.encoder_bias`` ，而非 MuJoCo 模型。


.. _dr-pseudo-inertia:

伪惯量随机化
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``dr.pseudo_inertia`` 联合随机化 ``body_mass`` 、 ``body_ipos`` 、
``body_inertia`` 和 ``body_iquat`` ，并对任意扰动幅度都保证物理一致性。
与独立随机化这些字段(可能产生负质量、虚数主惯量或违反三角不等式)不同，
``pseudo_inertia`` 通过 *伪惯量矩阵* :math:`J \succ 0` 对惯性进行参数化，
确保结果始终物理有效。

伪惯量矩阵 :math:`J` 是一个 :math:`4 \times 4` 的对称正定矩阵，它把质量、
质心和完整的转动惯性张量编码在同一个对象中：

.. math::

   J = \begin{bmatrix}
     \Sigma & h \\
     h^\top & m
   \end{bmatrix}, \qquad
   \Sigma = \tfrac{1}{2}\operatorname{tr}(I)\,I_3 - I, \qquad
   h = m\,c

其中 :math:`m` 为质量(``body_mass``)， :math:`c` 为质心(``body_ipos``)，
:math:`d` 为主惯量矩向量(``body_inertia``)， :math:`I` 为 body 坐标系
原点处的 :math:`3 \times 3` 惯性张量。惯性张量的构造方式是：先将对角的
主惯量矩旋转到 body 坐标系，再应用平行轴定理：

.. math::

   I_{\text{com}} &= V \operatorname{diag}(d)\, V^\top,
   \qquad V = R(q)^\top \\
   I &= I_{\text{com}} + m\bigl(\lVert c \rVert^2 I_3 - c\,c^\top\bigr)

其中 :math:`q` 是从 body 坐标系到主轴坐标系的四元数(``body_iquat``)，
:math:`R(q)` 是其旋转矩阵。

上述数学推导来自 `Rucker & Wensing, "Smooth Parameterization of Rigid-Body
Inertia," IEEE RA-L 2022 <https://par.nsf.gov/servlets/purl/10347458>`_ 。
:math:`J` 通过 Cholesky 分解为 :math:`J = LL^\top` 。扰动通过一个上三角
矩阵 :math:`U` 施加：

.. math::

   J' = (UL)(UL)^\top

该式对任意 :math:`U` 都保证正定。随后将扰动后的惯性张量分解回 MuJoCo
字段：用平行轴定理的逆变换把 :math:`I` 移回质心，再用特征分解提取主惯量矩
(``body_inertia``)和主轴坐标系的旋转(``body_iquat``)。这一过程对任意
扰动幅度都是精确的。

:math:`U` 的 10 个参数各自控制不同的物理效应：

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - 参数
     - 物理效应
   * - ``alpha``
     - 全局质量密度的对数缩放。质量与所有主惯量矩按 :math:`e^{2\alpha}`
       缩放，质心不变。
   * - ``d1, d2, d3``
     - 在惯性坐标系中沿 x、y、z 轴的拉伸/压缩。使用 ``d_range`` 可将
       三者设为相同范围(各向同性)。
   * - ``s12, s13, s23``
     - xy、xz、yz 平面内的剪切扰动。非对称地重新分布质量，产生非对角
       惯性项。
   * - ``t1, t2, t3``
     - 沿 x、y、z(body 坐标系)平移质心。纯 ``t1`` 平移时质量不变，
       ``body_ipos[0]`` 恰好平移 ``t1`` 。使用 ``t_range`` 可将三者
       设为相同范围。

.. rubric:: 示例

.. code-block:: python

    events = {
        # Isotropic mass scaling + small COM variation.
        "body_inertia_dr": EventTermCfg(
            mode="reset",
            func=dr.pseudo_inertia,
            params={
                "asset_cfg": SceneEntityCfg("robot", body_names=["torso"]),
                "alpha_range": (-0.1, 0.1),   # ±10% mass/inertia scaling
                "t_range": (-0.02, 0.02),     # ±2 cm COM shift
            },
        ),
        # Anisotropic stretching (x stiffer than y/z).
        "body_inertia_aniso_dr": EventTermCfg(
            mode="startup",
            func=dr.pseudo_inertia,
            params={
                "asset_cfg": SceneEntityCfg("robot", body_names=[".*"]),
                "alpha_range": (-0.2, 0.2),
                "d1_range": (-0.1, 0.1),
                "d2_range": (-0.3, 0.3),
                "d3_range": (-0.3, 0.3),
            },
        ),
    }


.. _dr-safety:

运行时修改模型的安全性
-------------------------------

在 C MuJoCo 中，运行时修改 ``mjModel`` 字段可能不安全：某些修改会使内部
加速结构(BVH)失效，或导致派生量过期。MuJoCo Warp 的碰撞管线不同，因此
这些顾虑大多并不适用。

有两点架构差异最为关键：

1. **没有碰撞 BVH。** C MuJoCo 会为中间阶段(midphase)碰撞裁剪构建静态
   包围盒层级(BVH)。修改静态 body 的 ``body_pos``/``body_quat`` 会使该树
   失效。MuJoCo Warp 改用 NxN 或 sweep-and-prune 宽相检测，因此不存在
   会失效的静态树。

2. **局部包围盒。** MuJoCo Warp 中的 ``geom_aabb`` 是 *局部* 包围盒
   (geom 坐标系下的中心加半尺寸)。宽相检测每一步都会用前向运动学得到的
   ``geom_xpos``/``geom_xmat`` 将其变换到世界坐标系。而 C MuJoCo 的
   BVH 缓存的是世界坐标系下的包围盒，因此任何对 ``geom_pos``/``geom_quat``
   的修改都会使其过期。

下表列出了在 mjlab 中哪些字段可以安全随机化，以及与 C MuJoCo 的对比。

.. list-table::
   :header-rows: 1
   :widths: 22 20 20 38

   * - 字段
     - C MuJoCo
     - mjlab / MuJoCo Warp
     - 差异原因
   * - ``body_pos`` 、 ``body_quat``
     - 使用 ``mj_setConst`` 时安全，但对静态 body **不安全**
       (会使 midphase BVH 失效)
     - 使用 ``set_const_0`` 时 **安全**
     - 不存在会失效的碰撞 BVH(见上)。无论 ``body_treeid`` 如何，
       所有 body 都会执行前向运动学。参见下文
       :ref:`静态 body 注意事项 <dr-static-body-caveat>` 。
   * - ``body_mass`` 、 ``body_inertia`` 、 ``body_ipos`` 、 ``body_iquat``
     - 使用 ``mj_setConst`` 时安全
     - 使用 ``set_const`` 时 **安全**
     - 方法相同。 ``dr.pseudo_inertia`` 在保证物理一致性的前提下
       联合随机化全部四个字段。
   * - ``geom_pos`` 、 ``geom_quat``
     - **不安全** (不支持 ``mj_setConst`` )
     - 对动态 body 上的 geom **安全**
     - 前向运动学每一步都会根据 ``geom_pos``/``geom_quat`` 重算
       ``geom_xpos``/``geom_xmat`` ，局部 ``geom_aabb`` 保持有效
       (见上)。参见下文
       :ref:`静态 body 注意事项 <dr-static-body-caveat>` 。
   * - ``geom_size``
     - **不安全**
     - **安全** (自动重算包围盒)
     - ``dr.geom_size`` 在写入新尺寸后内联重算 ``geom_rbound`` 和
       ``geom_aabb`` 。仅支持图元类型(球体、胶囊体、椭球体、
       圆柱体、长方体)。
   * - ``geom_rbound`` 、 ``geom_aabb``
     - **不安全** (内部派生量)
     - **不进行随机化** (派生量)
     - 宽相加速数据。仅在模型加载时设置一次。若 ``geom_size`` 变化
       则需要重算。
   * - ``geom_friction`` 、 ``geom_rgba``
     - 安全
     - **安全**
     - 无派生量。接触摩擦每一步直接读取。
   * - ``dof_armature``
     - 使用 ``mj_setConst`` 时安全
     - 使用 ``set_const_0`` 时 **安全**
     - 方法相同。
   * - ``dof_damping`` 、 ``dof_frictionloss`` 、 ``jnt_stiffness`` 、
       ``jnt_range``
     - 安全
     - **安全**
     - 无派生量。
   * - ``qpos0``
     - 使用 ``mj_setConst`` 时安全
     - 使用 ``set_const_0`` 时 **安全**
     - 方法相同。
   * - ``tendon_stiffness`` 、 ``tendon_damping`` 、 ``tendon_frictionloss``
     - 基本安全(从零变为非零或反向时需 ``mj_setConst`` )
     - **安全**
     - MuJoCo Warp 不使用休眠机制，而在 C MuJoCo 中正是该机制使
       零/非零转换变得特殊。
   * - ``tendon_armature``
     - 使用 ``mj_setConst`` 时安全
     - 使用 ``set_const_0`` 时 **安全**
     - 通过 ``smooth.tendon_armature()`` 对质量矩阵有贡献。
       处理方式与 ``dof_armature`` 相同。
   * - ``actuator_gainprm`` 、 ``actuator_biasprm``
     - 基本安全(dampratio 执行器需 ``mj_setConst`` )
     - **安全**
     - mjlab 的 ``dr.pd_gains`` 在内部处理了 dampratio。
   * - ``site_pos`` 、 ``site_quat``
     - 基本安全(跟踪相机/光源需 ``mj_setConst`` )
     - **安全**
     - site 通过前向运动学重算。典型 RL 用法中不涉及跟踪相机问题。
   * - ``bvh_aabb`` 、 ``oct_aabb`` 、 ``oct_coeff``
     - **不安全**
     - 不适用 / 不随机化
     - MuJoCo Warp 仅在渲染中使用 BVH，不用于碰撞。八叉树数据
       ( ``oct_*`` )用于 SDF 碰撞，不应修改。

.. _dr-static-body-caveat:

.. admonition:: 关于 ``geom_pos``/``geom_quat`` 与 ``body_pos``/``body_quat`` 的静态 body 注意事项

   MuJoCo Warp 的前向运动学会跳过同时满足以下条件的 geom： **焊接于世界
   坐标系** ( ``body_weldid == 0`` )且 **不是 mocap body 的后代**
   ( ``body_mocapid[root] == -1`` )。对这类 geom，
   ``geom_xpos``/``geom_xmat`` 只在 ``make_data`` 时计算一次，之后不再
   更新。此时修改 ``geom_pos`` 或父 body 的 ``body_pos`` 会使世界坐标系
   下的碰撞位置过期。

   实践中，这只影响直接放在 XML ``<worldbody>`` 下的裸 ``<geom>`` 元素
   (例如地面)，且它们不属于任何 mjlab 实体。所有 mjlab 实体(包括固定
   基座的实体)都会被 ``auto_wrap_fixed_base_mocap`` 自动包进一个
   mocap body，从而免于前向运动学的跳过。内置 ``dr`` 函数针对的是实体上
   具名的 body/geom，因此始终安全。

.. _dr-geom-size:

``geom_size`` 重算的工作原理
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

运行时修改 ``geom_size`` 需要更新宽相检测每一步都会读取的两个派生字段：

- ``geom_rbound``: 包围球半径(用于球体过滤裁剪)
- ``geom_aabb``: 局部轴对齐包围盒(用于 AABB/OBB 裁剪)

两者都在模型加载时从 ``MjModel`` 复制而来，之后 MuJoCo Warp 从不重算。
``dr.geom_size`` 的处理方式是：在写入新尺寸之后内联重算这两个字段
(纯 PyTorch 实现，无需 Warp kernel)。

具体公式因 geom 类型而异：

.. list-table::
   :header-rows: 1
   :widths: 18 30 30

   * - geom 类型
     - ``geom_rbound``
     - ``geom_aabb`` 半尺寸
   * - 球体
     - ``s[0]``
     - ``(s[0], s[0], s[0])``
   * - 胶囊体
     - ``s[0] + s[1]``
     - ``(s[0], s[0], s[0] + s[1])``
   * - 圆柱体
     - ``sqrt(s[0]² + s[1]²)``
     - ``(s[0], s[0], s[1])``
   * - 椭球体
     - ``max(s[0], s[1], s[2])``
     - ``(s[0], s[1], s[2])``
   * - 长方体
     - ``sqrt(s[0]² + s[1]² + s[2]²)``
     - ``(s[0], s[1], s[2])``

平面(plane)、高度场(heightfield)、网格(mesh)和 SDF geom 不受支持，
因为它们的包围盒来自顶点数据或为无穷大，无法由 ``geom_size`` 推导。


.. _dr-pair-friction:

``pair_friction`` 与各向同性摩擦
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``pair_friction`` 为每个接触对存储五个摩擦系数：

.. list-table::
   :header-rows: 1
   :widths: 10 20 20 50

   * - 索引
     - 名称
     - 生效条件
     - 含义
   * - 0
     - tangent1
     - ``condim >= 3``
     - 沿接触坐标系第一切向轴的滑动摩擦
   * - 1
     - tangent2
     - ``condim >= 3``
     - 沿第二切向轴的滑动摩擦
   * - 2
     - spin
     - ``condim >= 4``
     - 绕接触法线的扭转摩擦
   * - 3
     - roll1
     - ``condim = 6``
     - 绕第一切向轴的滚动摩擦
   * - 4
     - roll2
     - ``condim = 6``
     - 绕第二切向轴的滚动摩擦

MuJoCo 标准的 geom 摩擦是一个 3 维向量 ``[tangential, torsional,
rolling]`` ，会自动扩展为 5 维向量：把切向系数复制到 tangent1 和
tangent2，把滚动系数复制到 roll1 和 roll2。而接触对覆盖(pair override)
的五个值是独立存储的，因此必须显式维护这种对称性。传入
``isotropic=True`` 即可强制满足：采样之后，tangent2 会被覆写为 tangent1；
而当目标是轴 3 或轴 4 时，roll2 会被覆写为 roll1。

**按 condim 给出的建议。**

**condim = 3。** 两个切向轴都生效。采样 tangent1，并用 ``isotropic=True``
令 tangent2 与之相等。传入 ``shared_random=True`` 可让 ``asset_cfg``
选中的所有接触对在每个环境内获得相同的采样值(各环境之间仍然相互独立)：

.. code-block:: python

   dr.pair_friction(
       env,
       env_ids=None,
       ranges=(0.4, 1.0),
       operation="abs",
       asset_cfg=SceneEntityCfg("robot", pair_names=("foot1_floor", "foot2_floor")),
       axes=[0],           # sample tangent1
       shared_random=True, # all pairs selected by asset_cfg share one value per env
       isotropic=True,     # tangent2 = tangent1
   )

**condim = 4。** 自旋(轴 2)也生效。按上文方式随机化滑动摩擦。如果还需要
随机化自旋摩擦，请用单独的调用并指定各自的取值范围：

.. code-block:: python

   dr.pair_friction(
       env,
       env_ids=None,
       ranges=(0.4, 1.0),
       operation="abs",
       asset_cfg=SceneEntityCfg("robot", pair_names=("foot1_floor", "foot2_floor")),
       axes=[0],
       shared_random=True,
       isotropic=True,
   )
   dr.pair_friction(
       env,
       env_ids=None,
       ranges=(0.003, 0.01),
       operation="abs",
       asset_cfg=SceneEntityCfg("robot", pair_names=("foot1_floor", "foot2_floor")),
       axes=[2],
       shared_random=True,
   )

**condim = 6。** 全部五个轴都生效。按上文方式随机化滑动摩擦。若要对称地
随机化滚动摩擦，以 ``isotropic=True`` 作用于轴 3，使 roll2 被设为与
roll1 相等：

.. code-block:: python

   dr.pair_friction(
       env,
       env_ids=None,
       ranges=(0.4, 1.0),
       operation="abs",
       asset_cfg=SceneEntityCfg("robot", pair_names=("foot1_floor", "foot2_floor")),
       axes=[0],
       shared_random=True,
       isotropic=True,
   )
   dr.pair_friction(
       env,
       env_ids=None,
       ranges=(0.0001, 0.001),
       operation="abs",
       asset_cfg=SceneEntityCfg("robot", pair_names=("foot1_floor", "foot2_floor")),
       axes=[3],
       shared_random=True,
       isotropic=True,  # roll2 = roll1
   )


尚无 ``dr`` 函数的字段
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

按需添加
""""""""""""""""

这些连续型模型字段本可以有标准的 ``dr.*`` 函数，但目前还没有。它们会
随需求增加而补充。

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - 类别
     - 字段
     - 备注
   * - Body
     - ``body_gravcomp``
     - 重力补偿权重。需要 ``set_const_fixed`` 。
   * - 关节 / DOF
     - ``jnt_margin``
     - 关节限位检测的距离阈值。
   * - 肌腱
     - ``tendon_range``
     - 肌腱长度限制。
   * -
     - ``tendon_margin``
     - 肌腱限位检测的距离阈值。
   * -
     - ``tendon_lengthspring``
     - 弹簧原长范围。
   * - 执行器
     - ``actuator_dynprm`` 、 ``actuator_gear`` 、
       ``actuator_ctrlrange`` 、 ``actuator_actrange``
     - 常见场景已由 ``pd_gains`` 和 ``effort_limits`` 覆盖。

更适合自定义代码实现
"""""""""""""""""""""

这些字段的语义相互耦合，通用的 ``dr.*`` 函数反而容易造成误导。例如
``solref`` 的含义取决于求解器类型(elliptic 还是 direct)， ``solimp``
有顺序约束(dmin < dmax，width > 0)， ``qpos_spring`` 与 ``qpos0``
相互耦合。合适的取值范围取决于具体的建模选择。请改为编写自定义事件项
(参见 :ref:`自定义基于类的事件项 <dr-custom-event-terms>` 一节)，或使用
``@requires_model_fields`` 自动处理字段展开。

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - 类别
     - 字段
     - 备注
   * - 求解器参数
     - ``geom_solref`` 、 ``geom_solimp`` 、 ``geom_solmix`` 、
       ``jnt_solref`` 、 ``jnt_solimp`` 、 ``dof_solref`` 、
       ``dof_solimp`` 、 ``pair_solref`` 、 ``pair_solimp`` 、
       ``eq_solref`` 、 ``eq_solimp``
     - 语义取决于求解器类型和时间步长。
   * - 接触阈值
     - ``geom_margin`` 、 ``geom_gap`` 、 ``pair_margin`` 、 ``pair_gap``
     - 与上述求解器参数相互影响。
   * - 成对覆盖
     - ``eq_data``
     - 约束锚点的覆盖设置。
   * - 弹簧参考位
     - ``qpos_spring``
     - 与 ``qpos0`` 耦合；独立随机化容易出错。

需要专门 API 支持
""""""""""""""""""""""

这些字段需要专门处理，因为它们是整数/类别型、涉及顶点数据，或者缺少
独立逐环境取值所需的每世界维度。

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - 类别
     - 字段
     - 备注
   * - 纹理角色切换
     - ``mat_texid``
     - 暂未实现，因为 mujoco 的查看器在上下文创建后不会重新读取
       ``mat_texid`` ；替代方案是使用 ``geom_matid`` 并为每种纹理
       烘焙一个材质来随机化纹理。
   * - 网格
     - ``mesh_vert`` 、 ``mesh_normal`` 、 ``mesh_face`` 等
     - 用于操作(manipulation)物体的形状变化。这些字段缺少每世界维度，
       因此当前的展开基础设施无法实现逐世界变化。异构世界支持
       `开发中 <https://github.com/google-deepmind/mujoco_warp/pull/1009>`_ 。
   * - 可变形体
     - ``flex_*``
     - 用于软体物体操作的可变形体参数。与网格字段一样，大多数
       ``flex_*`` 字段缺少每世界维度。

不适合 DR 的字段
""""""""""""""""

- ``light_active`` 、 ``light_castshadow`` 、 ``light_type`` 、
  ``cam_projection``: 布尔/整数开关，不是连续参数。
- ``jnt_pos`` 、 ``jnt_axis``: 结构性的关节几何；运行时修改很脆弱，
  也非标准用法。
- ``hfield_data`` 、 ``hfield_size``: 地形数据；请改用地形系统。


.. _dr-parameters:

参数
----------

模型字段函数共享三个控制随机化的参数： ``distribution`` 控制如何从
``ranges`` 中采样取值， ``operation`` 控制采样值如何施加到模型字段。
( ``dr.pseudo_inertia`` 、 ``dr.pd_gains`` 等实体级函数有各自的签名，
详见其 docstring。)

分布
^^^^^^^^^^^^

``distribution`` 参数控制如何从给定的 ``ranges`` 中采样随机值。它接受
内置字符串，或用于自定义采样逻辑的 ``dr.Distribution`` 实例。

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - 取值
     - 行为
   * - ``"uniform"`` (默认)
     - 在 ``ranges[0]`` 和 ``ranges[1]`` 之间均匀采样
   * - ``"log_uniform"``
     - 在对数空间采样，适用于跨多个数量级的参数(例如扭转摩擦)。
       两个范围端点都必须大于 0。
   * - ``"gaussian"``
     - ``ranges`` 被解释为 ``(mean, std)``

要定义自定义分布，创建一个 ``dr.Distribution`` 实例。 ``sample`` 可调用
对象接收 ``(lower, upper, shape, device)`` 并返回一个张量。例如，将采样
值截断到给定边界的截断正态分布：

.. code-block:: python

    import torch
    from mjlab.envs.mdp import dr

    truncated_normal = dr.Distribution(
        name="truncated_normal",
        sample=lambda lo, hi, shape, device: torch.clamp(
            torch.normal(
                mean=(lo + hi) / 2,
                std=(hi - lo) / 4,  # 95% of samples within bounds
            ).expand(shape),
            min=lo,
            max=hi,
        ),
    )

    params={"distribution": truncated_normal, "ranges": (0.3, 1.2)}

操作
^^^^^^^^^

``operation`` 参数控制采样值如何施加到模型字段。它接受内置字符串，或用于
自定义逻辑的 ``dr.Operation`` 实例。

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - 取值
     - 行为
   * - ``"abs"`` (默认)
     - 直接把字段设为采样值
   * - ``"scale"``
     - 将原始默认值乘以采样值
   * - ``"add"``
     - 将采样值加到原始默认值上

对于 ``"scale"`` 和 ``"add"`` ，DR 引擎总是把随机抽取施加到从 CPU 上
编译好的 ``MjModel`` 捕获的 **原始默认值** 上，而不是当前值。这避免了
累积：连续三次把摩擦缩放 2 倍，得到的是原始值的 2 倍，而不是 8 倍。

要定义自定义操作，创建一个 ``dr.Operation`` 实例。它有四个字段：

- ``name``: 用于错误消息的人类可读标签。
- ``initialize``: 创建结果张量，随后逐轴填入采样值。例如 ``scale``
  从全 1 开始，未采样的轴乘以 1(不变)，而 ``add`` 从全 0 开始。
- ``combine``: 接收 ``(base_values, random_values)`` 并返回写入模型字段
  的最终张量。例如 ``scale`` 返回 ``base * random`` ， ``add`` 返回
  ``base + random`` 。
- ``uses_defaults``: 为 ``True`` 时，基准值是编译期默认值(避免多次调用
  之间累积)；为 ``False`` 时，基准值是当前模型值。

举例来说，内置的 ``add`` 总是加到 *默认值* 上，因此重复调用是重置而非
漂移。而把值加到 *当前值* 上的自定义 ``drift`` 操作，则适用于
``mode="interval"`` 事件中参数随时间缓慢游走的场景：

.. code-block:: python

    import torch
    from mjlab.envs.mdp import dr

    drift = dr.Operation(
        name="drift",
        initialize=torch.zeros_like,
        combine=torch.add,
        uses_defaults=False,  # read current values, not defaults
    )

    # Friction slowly wanders each interval step.
    friction_drift: EventTermCfg = EventTermCfg(
        mode="interval",
        interval_range_s=(0.5, 1.0),
        func=dr.geom_friction,
        params={
            "asset_cfg": SceneEntityCfg("robot", geom_names=[".*_foot.*"]),
            "ranges": (-0.01, 0.01),
            "operation": drift,
        },
    )

轴选择
^^^^^^^^^^^^^^

许多模型字段是多维的。例如 ``geom_friction`` 有三个分量
``[tangential, torsional, rolling]`` ， ``body_pos`` 有三个空间轴
``[x, y, z]`` 。可以使用 ``axes`` 参数，或为 ``ranges`` 传入字典来
指定具体轴。

对于 ``condim=3`` (标准摩擦接触)的 ``geom_friction`` ，只有
**轴 0(切向)** 会影响接触行为。关于 condim 和摩擦系数的细节，参见
`MuJoCo 接触文档
<https://mujoco.readthedocs.io/en/stable/computation/index.html#contact>`_
。

.. code-block:: python

    # Tangential friction only (this is the default for geom_friction)
    params={"ranges": {0: (0.3, 1.2)}}

    # Tangential + torsional (torsional matters for condim >= 4)
    params={"ranges": {0: (0.5, 1.0), 1: (0.001, 0.01)}}

    # X and Y position with the same range
    params={"axes": [0, 1], "ranges": (-0.1, 0.1)}

按组件使用字符串键的 ranges
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

可以在一次调用中用正则模式作为字典键，对不同实体施加不同的范围：

.. code-block:: python

    dr.joint_damping(
        env, env_ids,
        ranges={".*knee.*": (0.5, 1.5), ".*hip.*": (0.8, 1.2)},
        operation="scale",
        asset_cfg=SceneEntityCfg("robot", joint_names=[".*"]),
    )

每个模式都会与实体名称(关节名、geom 名等)进行匹配，匹配到的组件会应用
对应的范围。在这个例子里，膝关节的阻尼被缩放 0.5 倍到 1.5 倍，而髋关节
使用更窄的 0.8 倍到 1.2 倍范围，全部在同一个事件项中完成。


示例
--------

摩擦(reset)
^^^^^^^^^^^^^^^^

.. code-block:: python

    foot_friction: EventTermCfg = EventTermCfg(
        mode="reset",
        func=dr.geom_friction,
        params={
            "asset_cfg": SceneEntityCfg("robot", geom_names=[".*_foot.*"]),
            "ranges": (0.3, 1.2),
            "operation": "abs",
        },
    )

.. note::

     为机器人碰撞 geom 设置比地形更高的 **priority** (geom 的 priority
     默认为 0)。这样只需随机化机器人自身的摩擦即可。在(机器人, 地形)
     接触中，MuJoCo 会使用 priority 较高的 geom 的摩擦。

.. code-block:: python

    from mjlab.utils.spec_config import CollisionCfg

    robot_collision = CollisionCfg(
        geom_names_expr=[".*_foot.*"],
        priority=1,
        friction=(0.6,),
        condim=3,
    )


关节偏置(startup)
^^^^^^^^^^^^^^^^^^^^^^

随机化默认关节位置，以模拟关节偏置标定误差：

.. code-block:: python

    joint_offset: EventTermCfg = EventTermCfg(
        mode="startup",
        func=dr.joint_default_pos,
        params={
            "asset_cfg": SceneEntityCfg("robot", joint_names=[".*"]),
            "ranges": (-0.01, 0.01),
            "operation": "add",
        },
    )


质心(COM)(startup)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    com: EventTermCfg = EventTermCfg(
        mode="startup",
        func=dr.body_com_offset,
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=["torso"]),
            "ranges": {0: (-0.02, 0.02), 1: (-0.02, 0.02)},
            "operation": "add",
        },
    )


常见陷阱
---------------

``dr.body_mass`` 不会缩放惯量
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

只缩放质量而不缩放惯量，只有在建模“在质心处添加一个质点”(其转动惯量为
零)时才物理正确。对于常见的 DR 用例——模拟制造偏差或连杆密度的不确定性
——质量和惯量应当一起缩放。请改用带 ``alpha_range`` 的
:func:`dr.pseudo_inertia` ：

.. code-block:: python

    # Wrong: mass changes, inertia stays fixed (physically inconsistent).
    EventTermCfg(func=dr.body_mass, params={"ranges": (0.8, 1.2)})

    # Correct: mass and inertia both scale by e^{2alpha} (uniform density change).
    EventTermCfg(func=dr.pseudo_inertia, params={"alpha_range": (-0.1, 0.1)})

``dr.body_mass`` 会在运行时发出 ``UserWarning`` 来提示这一点。

``*_quat`` 的范围单位是弧度，不是角度
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

所有四元数随机化函数( :func:`dr.geom_quat` 、 :func:`dr.body_quat` 、
:func:`dr.site_quat` 、 :func:`dr.cam_quat` )接受的 roll/pitch/yaw
范围单位都是 **弧度** 。如果传入角度值，会静默产生大约 57 倍于预期的
旋转，且没有任何运行时检查。

``*_quat`` 扰动相对于默认值而非当前值
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

采样得到的 RPY 扰动会与 **默认** 四元数复合，而不是与当前四元数复合。
这与所有其他 ``dr`` 函数的无累积保证一致，但也意味着重复调用不会叠加
旋转。每次调用都独立地从默认朝向采样一个新的扰动。

``dr.geom_friction`` 默认只随机化切向摩擦
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

默认轴是 0(切向摩擦)。轴 1(扭转)和轴 2(滚动)只对 ``condim >= 4`` 的
接触生效，因此该默认值对标准 ``condim=3`` 接触是正确的。如果模型使用
高维接触，请显式传入 ``axes=[0, 1, 2]`` 。

``dr.geom_size`` 对非图元 geom 会抛出异常
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:func:`dr.geom_size` 只支持图元 geom 类型(球体、胶囊体、椭球体、
圆柱体、长方体)，因为网格、平面和高度场 geom 的宽相包围盒无法解析地
重算。选中非图元 geom 会抛出 ``ValueError`` 。请将 ``SceneEntityCfg``
过滤为只包含图元 geom：

.. code-block:: python

    # Select only primitive geoms by name pattern.
    geom_cfg = SceneEntityCfg("robot", geom_names=(".*sphere.*", ".*box.*"))

底层实现原理
---------------------------

了解内部机制有助于编写自定义 DR 项或排查意外行为。

逐世界存储
^^^^^^^^^^^^^^^^^

MuJoCo Warp 将数千个世界批量放入一次仿真中。为节省内存，
``geom_friction`` 这类模型数组只存储一份，形状为 ``(1, ngeom, 3)`` ，
且在第一个(世界)维度上 **stride 为 0** 。GPU kernel 使用
``worldid % arr.shape[0]`` 对这些数组取索引。当 ``shape[0]`` 为 1 时，
所有世界读取同一行，因此共享完全相同的模型参数。

在 PyTorch 侧，mjlab 用 ``torch.expand`` 包装这些 stride 为 0 的数组，
使其看起来形状为 ``(num_envs, ngeom, 3)`` ，但底层仍只有一行内存。用
``tensor[env_id]`` 索引时看起来每个世界都有自己的数据，但由于它们都指向
同一块底层内存，写入任何一个世界都会影响所有世界。

要让每个世界拥有独立的值，需要把底层 Warp 数组从形状 ``(1, N)``
**展开** 为 ``(num_worlds, N)`` ，配备真实的逐世界内存和正常 stride。
``sim.expand_model_fields()`` 会分配一个新数组，把共享数据复制到每个
世界的行中，并替换模型上的旧数组。展开之后，对某个世界的写入不再影响
其他世界，每个世界都可以拥有自己的摩擦、质量或阻尼值。

每个 ``dr`` 函数都通过 ``@requires_model_fields`` 装饰器声明自己需要的
字段， ``EventManager`` 会在启动时收集这些信息，从而自动完成展开。
直接修改模型数组的自定义 DR 项必须确保这些数组已被展开：要么用
``@requires_model_fields`` 装饰函数，要么手动调用
``sim.expand_model_fields()`` 。

.. note::

   展开字段会分配新的 GPU 内存，并使已捕获的 CUDA graph 失效，因为
   graph 中保存着指向旧数组的指针。mjlab 会在展开后自动重建 graph。
   这是环境启动时的一次性开销，而不是每个回合都发生。

为什么不直接重新编译模型？
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

要实现逐世界变化，最“干净”的方式是为每个世界修改 ``MjSpec`` ，把每个
都编译成各自的 ``MjModel`` ，再全部传到 GPU。由于 ``mj_setConst`` 在
编译期间就会运行，这样可以免费获得完全一致的派生量。

mjlab 没有这样做，原因有二：

1. **开销。** 编译 ``MjSpec`` 是 CPU 操作。每次回合重置都对每个世界
   编译一次，对数千个环境来说太慢了。

2. **架构。** MuJoCo Warp 期望所有世界共享单个 ``Model`` 。目前没有
   把 N 个独立模型加载进一次仿真的机制。

因此，mjlab 选择在 GPU 上原地修改展开后的数组，并只选择性地重算受改动
影响的派生量。这正是 ``RecomputeLevel`` 系统负责的事情。

.. _dr-recomputation:

派生字段的重算
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

有些模型字段是从其他字段 **派生** 出来的。例如 ``body_subtreemass``
(某个 body 及其所有后代的总质量)依赖于 ``body_mass`` 。如果修改了
``body_mass`` 却不更新 ``body_subtreemass`` ，约束求解器会使用过期的
阻抗值，仿真结果会出现细微的错误。

在 C MuJoCo 中，解决办法是在运行时修改模型参数后调用 `mj_setConst
<https://mujoco.readthedocs.io/en/latest/programming/simulation.html#mjmodel-changes>`_
。MuJoCo Warp 提供了一组等价的函数( ``set_const`` 、 ``set_const_0`` 、
``set_const_fixed`` )，它们在 GPU 上运行并对所有世界并行操作。mjlab 会
自动调用它们。

三个重算级别，从最便宜到最昂贵：

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - 级别
     - 重算内容
     - 使用时机
   * - ``set_const_fixed``
     - ``body_subtreemass``
     - 修改 ``body_gravcomp`` 之后
   * - ``set_const_0``
     - ``dof_invweight0`` 、 ``body_invweight0`` 、 ``tendon_length0`` 、
       ``tendon_invweight0`` ，以及相机和光源的参考量
     - 修改 ``dof_armature`` 、 ``tendon_armature`` 、
       ``body_inertia`` 、 ``body_pos`` 、 ``body_quat`` 或
       ``qpos0`` 之后
   * - ``set_const``
     - 以上全部
     - 修改 ``body_mass`` 或 ``body_ipos`` (质心)之后

内置 ``dr`` 函数已经声明了正确的级别。当 ``EventManager`` 在一次
``apply()`` 调用中触发多个 DR 项时，它会追踪其中最强的级别，并在最后
统一调用一次 ``sim.recompute_constants()`` 。除非在编写自定义 DR 逻辑，
否则无需手动调用。

只直接影响接触或关节行为的字段( ``geom_friction`` 、 ``dof_damping`` 、
``dof_frictionloss`` 等)没有派生量，无需重算。

.. note::

   出于性能考虑，mjlab 把 ``sim.step()`` 、 ``sim.forward()`` 、
   ``sim.reset()`` 和 ``sim.sense()`` 分别捕获为独立的 CUDA graph。
   包括 ``recompute_constants`` 在内的所有事件管理器逻辑，都在这些
   graph 重放之间以普通 Python 代码运行，因此不会破坏 graph 捕获。

   不过， ``set_const`` 的开销很大：它要在所有世界上运行前向运动学、
   复合刚体算法和质量矩阵分解。通过 ``interval`` 事件每一步都调用它会
   带来显著开销。实践中，需要重算的字段( ``body_mass`` 、
   ``body_com_offset`` 、 ``joint_armature`` 等)最好用 ``startup`` 或
   ``reset`` 模式随机化；无需重算的字段( ``geom_friction`` 、
   ``dof_damping`` 等)则以任意频率随机化都很便宜。


.. _dr-custom-event-terms:

自定义基于类的事件项
------------------------------

自定义事件项也可以用类而不是函数来实现。这对于需要维护状态或执行初始化
逻辑的事件项很有用：

.. code-block:: python

    class RandomizeTerrainFriction:
        """Custom event term that randomizes terrain friction."""

        def __init__(self, cfg, env):
            # Find the terrain geom index during initialization
            self._terrain_idx = None
            for idx, geom in enumerate(env.scene.spec.geoms):
                if geom.name == "terrain":
                    self._terrain_idx = idx

            if self._terrain_idx is None:
                raise ValueError("Terrain geom not found in the model.")

        def __call__(self, env, env_ids, ranges):
            """Called each time the event is triggered."""
            from mjlab.utils.math import sample_uniform
            env.sim.model.geom_friction[env_ids, self._terrain_idx, 0] = (
                sample_uniform(ranges[0], ranges[1], len(env_ids), env.device)
            )


    # Register in the environment config.
    terrain_friction: EventTermCfg = EventTermCfg(
        mode="reset",
        func=RandomizeTerrainFriction,
        params={"ranges": (0.3, 1.2)},
    )


可视化 DR 变化
----------------------

两种查看器都能反映 DR 变化，但覆盖范围不同。

**原生查看器**

原生查看器在每次渲染前把逐世界模型字段从 GPU 同步到本地 ``MjModel`` 。
这样 MuJoCo 内置的所有可视化开关都能在随机化后的模型上正常工作：

- Geom 外观( ``geom_rgba`` 、 ``geom_size`` 、 ``geom_pos`` 、
  ``geom_quat`` 、 ``geom_matid`` )
- 材质外观( ``mat_rgba`` 、 ``mat_emission`` 、 ``mat_specular`` 、
  ``mat_shininess`` 、 ``mat_texrepeat`` )
- Body 与 site 位姿( ``body_pos`` 、 ``body_quat`` 、 ``body_ipos`` 、
  ``site_pos`` 、 ``site_quat`` )
- 惯量( ``body_inertia`` 、 ``body_iquat`` 、 ``body_mass`` ): 按
  ``I`` 切换惯性框显示
- 相机参数( ``cam_pos`` 、 ``cam_quat`` 、 ``cam_fovy`` 、
  ``cam_intrinsic`` ): 按 ``Q`` 切换相机视锥显示
- 光源( ``light_pos`` 、 ``light_dir`` )

.. grid:: 2

   .. grid-item-card::

      .. image:: _static/dr_combined_rand.gif
         :alt: 每次重置时随机化立方体的颜色、尺寸和连杆朝向

      每个回合重置时随机化立方体颜色( ``dr.geom_rgba`` )、立方体尺寸
      ( ``dr.geom_size`` )以及连杆 2/3 的朝向( ``dr.body_quat`` )。
      尺寸变化后会自动重算宽相包围盒。

   .. grid-item-card::

      .. image:: _static/dr_pseudo_inertia.gif
         :alt: 每次回合重置时惯性椭球重新调整大小

      对连杆 2 和 3 施加 ``alpha_range=(-0.5, 0.5)`` 的
      ``dr.pseudo_inertia`` 。每个回合重置时惯性椭球都会重新调整大小，
      而其他连杆保持不变。

.. note::

   对于使用内参的相机(在 XML 中设置了 ``sensorsize`` / ``focal`` )，
   ``cam_fovy`` 不起作用。这一点同时适用于渲染图像和视锥可视化。此时
   MuJoCo 改为根据 ``cam_intrinsic`` 和 ``cam_sensorsize`` 计算投影。
   要随机化这类相机的视场，请使用 ``dr.cam_intrinsic`` 。关于内参与
   ``fovy`` 如何相互作用，参见 `MuJoCo 相机文档
   <https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-camera>`_
   中的说明。

**Viser**

相机视锥和 body 位姿始终是最新的，因为 viser 每一帧都直接从 GPU 仿真
数据( ``cam_xpos`` 、 ``body_xpos`` )读取世界坐标系位置。


.. note::

   ``geom_rgba`` 和 ``geom_size`` 的 DR **不会** 反映到 viser 中。geom
   的颜色和尺寸在构建时就烘焙进了场景的 GLB 网格。底层 viser API
   ( ``add_batched_meshes_simple`` )支持通过 ``batched_colors`` 进行
   逐实例颜色更新，但这需要把仅涉及颜色的 geom 走与当前的
   ``add_batched_meshes_trimesh`` 不同的句柄类型。此项支持推迟到未来
   更新。


从 Isaac Lab 迁移
------------------------

Isaac Lab 提供显式的摩擦组合模式( ``multiply`` 、 ``average`` 、
``min`` 、 ``max`` )。MuJoCo 则采用 **基于 priority 的选择** ：如果其中
一个接触 geom 的 ``priority`` 更高，就使用它的摩擦；否则使用
**逐元素最大值** 。详情参见 `MuJoCo 接触文档
<https://mujoco.readthedocs.io/en/stable/computation/index.html#contact>`_
。
