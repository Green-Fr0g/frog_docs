.. _scene:

场景
====

场景把实体、地形和传感器合并到一次仿真中。``SceneCfg`` 描述世界的内容，而 ``Scene`` 类负责 MJCF 组合、编译以及运行时状态管理。

.. code-block:: python

    from mjlab.scene import SceneCfg
    from mjlab.terrains import TerrainEntityCfg

    # A robot on a flat ground plane with 4096 parallel environments.
    scene_cfg = SceneCfg(
        num_envs=4096,
        env_spacing=2.5,
        terrain=TerrainEntityCfg(terrain_type="plane"),
        entities={"robot": robot_cfg},
    )

一个带程序化地形、传感器和多个实体的场景：

.. code-block:: python

    from mjlab.scene import SceneCfg
    from mjlab.terrains import TerrainEntityCfg
    from mjlab.terrains.config import ROUGH_TERRAINS_CFG
    from mjlab.sensor import RayCastSensorCfg, ContactSensorCfg

    scene_cfg = SceneCfg(
        num_envs=4096,
        terrain=TerrainEntityCfg(
            terrain_type="generator",
            terrain_generator=ROUGH_TERRAINS_CFG,
            max_init_terrain_level=5,
        ),
        entities={
            "robot": robot_cfg,
            "cube": cube_cfg,
        },
        sensors=(
            RayCastSensorCfg(name="terrain_scan", ...),
            ContactSensorCfg(name="feet_contact", ...),
        ),
    )


组合
----

场景从一个根 ``MjSpec`` 出发，把每个实体的 spec 以唯一名称前缀
`附加 <https://mujoco.readthedocs.io/en/stable/python.html#attachment>`_
进来。名为 ``"robot"`` 的机器人实体，其所有内部 MuJoCo 元素（body、关节、geom、执行器、传感器）都会加上 ``robot/`` 前缀，于是 ``base_link`` 变成 ``robot/base_link``，``joint0`` 变成 ``robot/joint0``，依此类推。加前缀可以避免多个实体共享元素名称时的命名冲突，也为观测项和奖励项提供了统一的命名空间。

地形（如果存在）不带前缀附加（其元素位于全局命名空间）。传感器在实体之后添加，可以通过带前缀的名称引用实体的元素。

``scene.compile()`` 把组合好的 ``MjSpec`` 转换为单个 ``MjModel``。随后 ``Simulation`` 类通过 MuJoCo Warp 把该模型上传到 GPU。仿真创建之后，``scene.initialize()`` 会把每个实体的元素索引解析到编译后的模型中，分配状态缓冲区，并为相机与光线投射传感器设置 GPU 渲染资源。

``scene.to_zip(path)`` 把编译后的模型导出为 ``.zip`` 文件，便于在独立的 MuJoCo 查看器中离线查看。每个实体的初始状态 keyframe 会合并进导出结果，因此模型会以默认位姿打开。

在运行时，可以通过名称访问实体和传感器：

.. code-block:: python

    robot = env.scene["robot"]              # Entity
    scan = env.scene["terrain_scan"]        # Sensor
    contact = env.scene["feet_contact"]     # Sensor

    robot.data.joint_pos                    # [B, num_joints]
    scan.data.distances                     # [B, N]
    contact.data.force                      # [B, N, 3]

实体 XML 中定义的内置传感器会在组合过程中被自动发现，并以实体名称前缀访问：

.. code-block:: python

    imu = env.scene["robot/trunk_imu"]      # Auto-discovered sensor


环境原点
--------

MuJoCo Warp 中的每个环境都是一个拥有独立状态的 world。各环境之间不共享物理空间，也无法相互影响。环境原点有两个用途：一是把实体在世界中分散开以便可视化（让查看器把机器人并排显示，而不是堆叠在原点）；二是对于带程序化地形的移动任务，把每个环境放置到特定的子地形块上。

**平坦地形。** 原点构成一个以世界原点为中心的规则网格，相邻环境间隔 ``env_spacing`` 米。

**程序化地形。** 地形生成器产出一个 ``num_rows x num_cols`` 的子地形块网格，每个块都有自己的中心点。每个环境被分配到一个块上，地形课程系统会随着表现提升把环境移动到更难的块上。详见 :ref:`terrain` 一节。

.. note::

   目前所有环境共享同一个 ``MjModel`` (相同的网格、几何体和运动学树)。异构仿真——即不同 world 可以拥有不同的网格或几何体——
   `正在 MuJoCo Warp 中推进 <https://github.com/google-deepmind/mujoco_warp/pull/1009>`_ 。
   上游落地后 mjlab 将提供支持。

重置事件项会读取 ``scene.env_origins`` 来摆放实体：

.. code-block:: python

    # Inside a reset event term.
    robot.write_root_pose_to_sim(
        default_root_pose + env_origins[env_ids]
    )

每个原点都用一个不可见的球形 site（geom group 4）标记，启用 group 4 后它会出现在 MuJoCo 查看器中，便于在开发阶段检查摆放位置。


自定义 spec 编辑
----------------

大多数场景完全由其实体、地形和传感器描述。偶尔也会有跨多个实体的修改。例如，一根连接天花板龙门架与机器人的肌腱，无法在任何一个实体的 MJCF 内定义，因为它同时引用了双方的 site。

``SceneCfg`` 上的 ``spec_fn`` 回调就是为这种情况准备的。它在所有实体和传感器都以带前缀的名称附加完毕之后、编译之前，接收完整组合好的 ``MjSpec``：

.. code-block:: python

    import mujoco

    def add_gantry(spec: mujoco.MjSpec):
        spec.worldbody.add_site(name="gantry", pos=(0, 0, 2))
        for side in ["left", "right"]:
            tendon = spec.add_tendon(
                name=f"{side}_rope",
                limited=True,
                range=(0, 1),
            )
            tendon.wrap_site("gantry")
            tendon.wrap_site(f"robot/{side}_hook")

    scene_cfg = SceneCfg(
        entities={"robot": robot_cfg},
        spec_fn=add_gantry,
    )

其他常见用途包括全局等式约束、自定义可视化几何体，以及任何需要访问完整组合场景的修改。
