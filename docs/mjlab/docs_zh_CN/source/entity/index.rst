.. _entity:

实体（Entity）
==============

``Entity`` 表示仿真中的一个物理对象：机器人、被操作的物体，或桌子这类固定装置。
它是 mjlab 物理层的核心抽象。

一个 ``Entity`` 类覆盖了所有变体（相比之下，Isaac Lab 将其拆分为
``Articulation``、``RigidObject`` 以及 ``AssetBase`` 的其他若干子类）。
两个相互独立的布尔属性刻画了每个实例的类型：

**基座类型。**
  *固定基座*（fixed-base）实体被焊接在世界中，没有自由关节。*浮动基座*
  （floating-base）实体带有一个自由关节，可以做 6 自由度运动。

**铰接。**
  *铰接* 实体拥有内部关节（转动关节、滑动关节等）。*非铰接* 实体除了可能
  存在的自由关节之外没有其他关节。

.. list-table::
   :header-rows: 1
   :widths: 30 25 15 15 15

   * - 类型
     - 示例
     - ``is_fixed_base``
     - ``is_articulated``
     - ``is_actuated``
   * - 固定基座、非铰接
     - 桌子、墙壁
     - True
     - False
     - False
   * - 固定基座、铰接
     - 机械臂、门
     - True
     - True
     - True/False
   * - 浮动基座、非铰接
     - 盒子、球、马克杯
     - False
     - False
     - False
   * - 浮动基座、铰接
     - 人形机器人、四足机器人
     - False
     - True
     - True/False

.. note::

   mjlab 会自动把每个固定基座实体包装成一个
   `mocap 主体 <https://mujoco.readthedocs.io/en/stable/modeling.html#mocap-bodies>`_，
   使每个并行环境都能把该实体放置在不同的位置。如果没有这层包装，所有
   固定基座实体都会被焊死在世界原点。这层包装是透明的，但**只有在重置
   事件运行时才会进行定位**。你必须在事件配置中包含
   ``reset_root_state_uniform`` 之类的重置事件；否则每个固定基座实体都会
   停留在原点。完整示例见 :ref:`FAQ <faq>`。mocap 实体也可以在运行时通过
   ``entity.write_mocap_pose_to_sim()`` 重新定位。


配置实体
--------

每个实体都由一个 ``EntityCfg`` 描述。实践中只有 ``spec_fn`` 是必填的，
其余字段都有合理的默认值。一个被动的浮动物体只需要：

.. code-block:: python

    from mjlab.entity import EntityCfg

    cube_cfg = EntityCfg(spec_fn=get_cube_spec)

带执行器的机器人会用到更多接口：

.. code-block:: python

    from mjlab.entity import EntityCfg, EntityArticulationInfoCfg
    from mjlab.actuator import IdealPDActuatorCfg

    robot_cfg = EntityCfg(
        spec_fn=get_spec,
        init_state=EntityCfg.InitialStateCfg(
            pos=(0.0, 0.0, 0.8),
            joint_pos={".*_hip_.*": 0.5, ".*": 0.0},
        ),
        articulation=EntityArticulationInfoCfg(
            actuators=(
                IdealPDActuatorCfg(
                    target_names_expr=(".*",),
                    stiffness={".*": 50.0},
                    damping={".*": 5.0},
                ),
            ),
        ),
        collisions=(my_collision_cfg,),
    )

后续小节将逐一介绍各个字段。

``spec_fn``
^^^^^^^^^^^

一个返回 ``mujoco.MjSpec`` 的可调用对象。场景在组合阶段调用它，把返回的
spec 加上名称前缀后挂载进来，并最终编译成一个共享的 ``MjModel``。

简单场景下一个 lambda 就够了：

.. code-block:: python

    spec_fn = lambda: mujoco.MjSpec.from_file("robot.xml")

更复杂的情况请使用普通函数。MuJoCo 会自动从磁盘解析网格资源，因此
``get_spec`` 只需要加载 XML：

.. code-block:: python

    def get_spec() -> mujoco.MjSpec:
        return mujoco.MjSpec.from_file(str(ROBOT_XML))

由于 ``spec_fn`` 是任意的可调用对象，你可以在返回之前对
`MjSpec 编辑 <https://mujoco.readthedocs.io/en/stable/python.html#spec>`_
做任意修改：添加 body、修改关节限位、替换材质，甚至完全不使用 XML
文件、以纯编程方式构建整个模型。

``init_state``
^^^^^^^^^^^^^^

默认的根位姿、根速度和关节位置/速度。这些值以 MuJoCo 关键帧的形式存储，
重置事件会用它们把实体恢复到初始配置。

``joint_pos`` 和 ``joint_vel`` 是把正则模式映射到取值的字典。模式按顺序
与关节名匹配，因此当某个关节同时匹配多个模式时，靠后的条目会覆盖靠前的：

.. code-block:: python

    init_state = EntityCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.8),       # root position
        rot=(1.0, 0.0, 0.0, 0.0),  # root quaternion (w, x, y, z)
        joint_pos={
            ".*": 0.0,              # all joints to zero
            ".*_hip_.*": 0.5,       # then override hips to 0.5
        },
    )

把 ``joint_pos`` 设为 ``None``，可以改用 MJCF 模型中已有的关键帧，而不是
在这里定义取值。

``articulation``
^^^^^^^^^^^^^^^^

执行器配置。只有带驱动关节的实体才需要。被动对象（盒子、桌子、墙壁）
可以完全省略该字段。执行器类型的详细说明见 :ref:`actuators`。

``soft_joint_pos_limit_factor`` (默认 1.0) 会收缩软限位惩罚奖励所使用的
关节范围，使策略在到达物理硬限位之前就受到惩罚。它不会修改 MuJoCo 模型中
实际的关节限位。

Spec 编辑器
^^^^^^^^^^^

其余字段是可选的 spec 编辑器配置元组，会在编译之前修改 ``MjSpec``：

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - 字段
     - 用途
   * - ``collisions``
     - 按 geom 设置接触参数（contype、conaffinity、friction）。
   * - ``lights``
     - 向指定 body 添加光源。
   * - ``cameras``
     - 向指定 body 添加相机。
   * - ``textures``
     - 添加程序化纹理（棋盘格、渐变等）。
   * - ``materials``
     - 添加材质，并可通过正则表达式将其指定给 geom。

每种编辑器都接受正则模式来定位特定元素。例如，一个
``geom_names_expr=(".*_foot.*",)`` 的 ``CollisionCfg`` 只会为脚部 geom
设置接触参数。完整示例见资产库（``mjlab.asset_zoo.robots``）。

异构世界
^^^^^^^^

如果场景需要在不同的并行世界中使用不同的网格资源（例如训练一个能泛化到
不同物体形状的操作策略），请使用 ``VariantEntityCfg`` 而不是
``EntityCfg``。每个世界会按可配置的权重被分配一个变体，而依赖网格的编译
常量（碰撞边界、body 惯性、子树质量）会以按世界数组的形式存储，从而保证
域随机化和查看器的一致性。详见 :ref:`heterogeneous_worlds`。

子类化 Entity
^^^^^^^^^^^^^

可以继承 ``Entity`` 和 ``EntityCfg`` 来实现定制行为。mjlab 自身在地形上
就使用了这一机制：``TerrainEntity`` 扩展了 ``Entity``，加入程序化地形
生成和逐环境原点计算；``TerrainEntityCfg`` 则增加了 ``terrain_type``、
``env_spacing`` 和 ``terrain_generator`` 等字段。任何需要超出 ``EntityCfg``
与 spec 编辑器所提供能力的领域专属实体，都可以采用同样的模式。

查找元素
^^^^^^^^

Entity 提供了一系列 ``find_*`` 方法，它们接受正则模式并返回匹配元素的
索引和名称：

.. code-block:: python

    ids, names = entity.find_joints((".*_hip_.*", ".*_knee_.*"))
    ids, names = entity.find_geoms((".*foot.*",))
    ids, names = entity.find_bodies((".*",))

可用方法包括 ``find_bodies()``、``find_joints()``、``find_geoms()``、
``find_sites()`` 和 ``find_tendons()``。它们在场景构建和管理器初始化过程
中被内部使用。在奖励和观测项中，请优先使用下文描述的带名称模式的
``SceneEntityCfg``。


读取运行时状态
--------------

实体被加入 ``SceneCfg`` 且环境构建完成后，可以通过三个抽象层次逐级降低的
接口访问其状态。

EntityData
^^^^^^^^^^

``entity.data`` 是奖励、观测和终止函数的主要接口。它以形状为
``(num_envs, ...)`` 的 PyTorch 张量形式，暴露运动学状态（位姿、速度、
加速度）、执行器力、广义力，以及投影重力等派生的 body 系量。完整的属性
参考见 :ref:`entity_data`。

``SceneEntityCfg`` 用于选择一个项所作用的实体以及该实体内部的元素。
``joint_names``、``body_names``、``site_names`` 等正则模式会在管理器
初始化时一次性解析为整数索引，因此运行时没有正则开销：

.. code-block:: python

    from mjlab.managers.scene_entity_config import SceneEntityCfg

    def flat_orientation_l2(
        env,
        asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
    ) -> torch.Tensor:
        """Penalize non-flat base orientation using projected gravity."""
        asset = env.scene[asset_cfg.name]
        return torch.sum(
            torch.square(asset.data.projected_gravity_b[:, :2]), dim=1
        )

``SceneEntityCfg`` 还支持通过 ``joint_names``、``body_names``、
``site_names`` 等进行正则元素选择。解析得到的整数索引（例如
``asset_cfg.joint_ids``）使运行时只需读取单个张量切片，没有任何正则
开销。

传感器
^^^^^^

传感器在**场景**上配置，而不是在单个实体上。传感器可以引用实体元素
（例如机器人脚上的接触传感器、附着在某个 body site 上的加速度计），但也
可以独立于任何实体。这就是传感器位于 ``SceneCfg`` 而非 ``EntityCfg``
中的原因。

在运行时，传感器通过 ``env.scene`` 按名称访问，方式与实体相同：

.. code-block:: python

    def angular_momentum_penalty(env, sensor_name: str) -> torch.Tensor:
        sensor = env.scene[sensor_name]
        return torch.sum(torch.square(sensor.data), dim=-1)

内置传感器封装了 MuJoCo 的传感器类型（accelerometer、gyro、framepos、
subtreeangmom 等）。``ContactSensor``、``RayCastSensor`` 和
``CameraSensor`` 为接触检测、地形扫描和 RGB-D 渲染提供了更高层的抽象。
详见 :ref:`sensors`。

原始仿真数据
^^^^^^^^^^^^

对于 ``EntityData`` 和传感器未覆盖的内容，可以通过 ``env.sim.data`` 和
``env.sim.model`` 访问底层的 MuJoCo Warp 数组。它们以 PyTorch 张量
（零拷贝）的形式暴露完整的 ``mjData`` 和 ``mjModel`` 字段，索引使用全局
MuJoCo ID 而非按实体的 ID：

.. code-block:: python

    # Global joint positions across all entities.
    qpos = env.sim.data.qpos          # (num_envs, nq)

    # All body positions.
    xpos = env.sim.data.xpos          # (num_envs, nbody, 3)

    # Model-level constants.
    body_mass = env.sim.model.body_mass  # (nbody,)

当你需要进行底层操作，或需要跨多个实体的量时，这会非常有用。

.. note::

   原始仿真数据的主要限制在于你必须自行管理全局 MuJoCo 索引。未来我们
   计划支持 MuJoCo 的
   `bind <https://mujoco.readthedocs.io/en/latest/python.html#relationship-to-pymjcf-and-bind>`_
   功能，它可以把 spec 元素直接绑定到对应的数据视图，免去手工维护索引。

.. toctree::
   :maxdepth: 1

   entity_data
   per_world_mesh
