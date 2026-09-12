.. _raycast_sensor:

光线投射传感器
==============

``RayCastSensor`` 提供 GPU 加速的光线投射，用于地形扫描、障碍物检测和深度
感知。光线从附着于场景中某个 body、site 或 geom 的坐标系发出，传感器报告
命中距离、世界坐标系下的命中位置以及表面法线。

.. raw:: html

   <video controls style="display: block; margin: 0 auto; max-width: 100%; height: auto;">
     <source src="../../_static/raycast_demo.mp4" type="video/mp4">
   </video>


快速上手
--------

.. code-block:: python

    from mjlab.sensor import RayCastSensorCfg, GridPatternCfg, ObjRef

    # Downward-facing grid for terrain height scanning.
    raycast_cfg = RayCastSensorCfg(
        name="terrain_scan",
        frame=ObjRef(type="body", name="base", entity="robot"),
        pattern=GridPatternCfg(size=(1.0, 1.0), resolution=0.1),
        max_distance=5.0,
    )

    scene_cfg = SceneCfg(
        entities={"robot": robot_cfg},
        sensors=(raycast_cfg,),
    )

    # Access at runtime.
    data = env.scene["terrain_scan"].data
    data.distances      # [B, N] distance to hit, -1 if miss
    data.hit_pos_w      # [B, N, 3] world-space hit positions
    data.normals_w      # [B, N, 3] surface normals


光线模式
--------

光线模式定义从传感器坐标系发出的光线在空间中的分布和方向。

.. grid:: 2

   .. grid-item-card:: 网格模式

      以固定空间分辨率排列在二维网格中的平行光线。由于光线间距以世界单位
      （米）定义，地面覆盖范围不会随传感器高度变化。是高度图和地形扫描的
      自然选择。

      .. raw:: html

         <video autoplay loop muted playsinline style="width: 100%; height: auto;">
           <source src="../../_static/pattern_grid.mp4" type="video/mp4">
         </video>

   .. grid-item-card:: 针孔相机模式

      从单一原点发出的发散光线，类似于深度相机。由于视场以角度单位固定，
      地面覆盖范围随传感器高度增加而增大。

      .. raw:: html

         <video autoplay loop muted playsinline style="width: 100%; height: auto;">
           <source src="../../_static/pattern_pinhole.mp4" type="video/mp4">
         </video>

.. code-block:: python

    from mjlab.sensor import GridPatternCfg, PinholeCameraPatternCfg

    # Parallel grid: fixed footprint, height-invariant.
    grid = GridPatternCfg(
        size=(1.0, 1.0),              # Grid dimensions in meters
        resolution=0.1,               # Spacing between rays
        direction=(0.0, 0.0, -1.0),   # Ray direction (down)
    )

    # Pinhole: perspective projection, diverging rays.
    pinhole = PinholeCameraPatternCfg(
        width=16,
        height=12,
        fovy=45.0,  # Vertical FOV in degrees
    )

    # Pinhole from a MuJoCo camera definition.
    pinhole = PinholeCameraPatternCfg.from_mujoco_camera("robot/depth_cam")

    # Pinhole from an intrinsic matrix.
    pinhole = PinholeCameraPatternCfg.from_intrinsic_matrix(
        intrinsic_matrix=[500, 0, 320, 0, 500, 240, 0, 0, 1],
        width=640,
        height=480,
    )


模式对比
^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - 对比维度
     - 网格
     - 针孔
   * - 光线方向
     - 平行
     - 发散
   * - 间距单位
     - 米
     - 角度（FOV）
   * - 高度影响覆盖范围
     - 否
     - 是
   * - 投影模型
     - 正交投影
     - 透视投影


坐标系附着
----------

光线从场景中由 ``ObjRef`` 指定的坐标系发出。该坐标系可以是任意实体上的
body、site 或 geom。

.. code-block:: python

    frame = ObjRef(type="body", name="base", entity="robot")
    frame = ObjRef(type="site", name="scan_site", entity="robot")
    frame = ObjRef(type="geom", name="sensor_mount", entity="robot")

``exclude_parent_body`` 默认为 ``True``，可防止光线命中传感器所附着
的 body。


光线对齐
--------

``ray_alignment`` 设置控制当 body 旋转时光线如何相对附着坐标系定向。

.. raw:: html

   <video autoplay loop muted playsinline
          style="display: block; margin: 0 auto; max-width: 100%; height: auto;">
     <source src="../../_static/ray_alignment_comparison.mp4" type="video/mp4">
   </video>

.. list-table::
   :header-rows: 1
   :widths: 15 45 40

   * - 模式
     - 描述
     - 适用场景
   * - ``"base"``
     - 完整跟随位置和旋转
     - 安装在 body 上的传感器
   * - ``"yaw"``
     - 跟随偏航（yaw），忽略俯仰和滚转
     - 地形高度图
   * - ``"world"``
     - 固定的世界坐标系方向
     - 与重力对齐的感知

.. code-block:: python

    RayCastSensorCfg(
        name="height_scan",
        frame=ObjRef(type="body", name="base", entity="robot"),
        pattern=GridPatternCfg(size=(1.0, 1.0), resolution=0.1),
        ray_alignment="yaw",
    )


Geom 组过滤
-----------

MuJoCo 将 geom 分配到 0 至 5 组。使用 ``include_geom_groups`` 可以限制光线
能命中哪些 geom。这对于忽略纯视觉 geom 或隔离地形几何很有用。

.. code-block:: python

    RayCastSensorCfg(
        name="terrain_only",
        frame=ObjRef(type="body", name="base", entity="robot"),
        pattern=GridPatternCfg(),
        include_geom_groups=(0, 1),
    )


输出
----

``RayCastData`` 是一个 dataclass，其形状标注中的 ``B`` 表示环境数量，
``N`` 表示光线数量。

.. code-block:: python

    @dataclass
    class RayCastData:
        distances: Tensor   # [B, N] distance to hit, -1 if miss
        hit_pos_w: Tensor   # [B, N, 3] world-space hit positions
        normals_w: Tensor   # [B, N, 3] surface normals
        pos_w: Tensor       # [B, 3] sensor frame position
        quat_w: Tensor      # [B, 4] sensor frame orientation (w, x, y, z)

.. note::

   在配置上设置 ``debug_vis=True`` 即可在运行时可视化光线命中情况。


示例
----

.. code-block:: python

    from mjlab.sensor import (
        RayCastSensorCfg, GridPatternCfg, PinholeCameraPatternCfg, ObjRef,
    )

    # Dense height map for terrain-aware locomotion.
    height_scan = RayCastSensorCfg(
        name="height_scan",
        frame=ObjRef(type="body", name="base", entity="robot"),
        pattern=GridPatternCfg(
            size=(1.6, 1.0),
            resolution=0.1,
            direction=(0.0, 0.0, -1.0),
        ),
        ray_alignment="yaw",
        max_distance=2.0,
    )

    # Simulated depth camera using pinhole projection.
    depth_cam = RayCastSensorCfg(
        name="depth",
        frame=ObjRef(type="site", name="camera_site", entity="robot"),
        pattern=PinholeCameraPatternCfg.from_mujoco_camera("robot/depth_cam"),
        max_distance=10.0,
    )

    # Forward-facing obstacle scan.
    obstacle_scan = RayCastSensorCfg(
        name="obstacle",
        frame=ObjRef(type="body", name="head", entity="robot"),
        pattern=GridPatternCfg(
            size=(0.5, 0.3),
            resolution=0.1,
            direction=(-1.0, 0.0, 0.0),
        ),
        max_distance=3.0,
        include_geom_groups=(0,),
    )


TerrainHeightSensor
-------------------

``TerrainHeightSensor`` 是 ``RayCastSensor`` 的一个轻量子类，它在传感器数据
中为每个坐标系增加垂直净空。它对每条光线计算 ``frame_z - hit_z``，将未命中
的光线替换为 ``max_distance``，并按坐标系跨光线归约。

.. code-block:: python

    from mjlab.sensor import TerrainHeightSensorCfg, RingPatternCfg, ObjRef

    cfg = TerrainHeightSensorCfg(
        name="foot_height",
        frame=(
            ObjRef(type="site", name="left_foot", entity="robot"),
            ObjRef(type="site", name="right_foot", entity="robot"),
        ),
        pattern=RingPatternCfg.single_ring(radius=0.04, num_samples=4),
        max_distance=1.0,
        include_geom_groups=(0,),
    )

    # At runtime:
    sensor = env.scene["foot_height"]
    sensor.data.heights    # [B, F] vertical clearance per foot
    sensor.data.distances  # [B, N] raw ray distances (inherited)

``reduction`` 配置字段控制每个坐标系内的光线如何聚合，默认为 ``"min"``，
也可以选择 ``"max"`` 或 ``"mean"``。
