.. _sensors:

传感器
======

如 :ref:`entity` 所述，在 mjlab 的数据访问层次中，传感器位于 ``EntityData`` 与
原始仿真数组之间。最简单的情况下，它们将 MuJoCo 传感器原语封装在一个清晰的
接口中，该接口可对应真实的机器人硬件。除此之外，它们还是一种通用抽象，用于
将仿真数据转换为结构化输出：``ContactSensor`` 对接触对进行聚合，并支持归约
和腾空时间跟踪；``RayCastSensor`` 执行 GPU 加速的地形扫描；``CameraSensor``
在 GPU 上渲染 RGB 和深度图像；而基类 ``Sensor`` 可以被子类化，以实现自定义
测量逻辑。

传感器是在 **场景级别** 上配置的，而不是在单个实体上。传感器可以引用实体的
某个元素（例如机器人脚上的接触传感器、附着在 body site 上的加速度计），但它
也完全可以独立于任何实体。这正是传感器位于 ``SceneCfg`` 而非 ``EntityCfg``
中的原因。

.. code-block:: python

    from mjlab.sensor import (
        BuiltinSensorCfg, ContactSensorCfg, ContactMatch, ObjRef,
    )

    # A robot with an IMU accelerometer and foot contact detection.
    scene_cfg = SceneCfg(
        entities={"robot": robot_cfg},
        sensors=(
            BuiltinSensorCfg(
                name="imu_acc",
                sensor_type="accelerometer",
                obj=ObjRef(type="site", name="imu_site", entity="robot"),
            ),
            ContactSensorCfg(
                name="feet_contact",
                primary=ContactMatch(
                    mode="geom", pattern=r".*_foot$", entity="robot",
                ),
                secondary=ContactMatch(mode="body", pattern="terrain"),
                fields=("found", "force"),
            ),
        ),
    )

    # Access at runtime.
    imu = env.scene["robot/imu_acc"].data        # [B, 3] acceleration
    feet = env.scene["feet_contact"].data         # ContactData
    feet.found                                    # [B, P] contact count per foot
    feet.force                                    # [B, P, 3] contact force per foot

mjlab 提供四种传感器类型：``BuiltinSensor`` 用于 MuJoCo 原生测量，
``ContactSensor`` 用于结构化接触检测，``RayCastSensor`` 用于 GPU 加速的
光线投射，``CameraSensor`` 用于 RGB-D 渲染。基类 ``Sensor`` 可以被子类化，
以实现自定义测量逻辑；参见下文 `扩展：自定义传感器`_ 。


BuiltinSensor
-------------

``BuiltinSensor`` 封装了 MuJoCo 的原生传感器类型。每个传感器通过 ``ObjRef``
附着到某个 MuJoCo 元素（site、joint、body 等）上，并返回形状为
``[num_envs, dim]`` 的 ``torch.Tensor``，其中 ``dim`` 取决于传感器类型
（向量为 3，四元数为 4，标量为 1）。

+---------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| 类别                | 可用传感器                                                                                                                                         |
+=====================+====================================================================================================================================================+
| **站点（Site）**    | ``accelerometer``, ``velocimeter``, ``gyro``, ``force``, ``torque``, ``magnetometer``, ``rangefinder``                                             |
+---------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| **关节（Joint）**   | ``jointpos``, ``jointvel``, ``jointlimitpos``, ``jointlimitvel``, ``jointlimitfrc``, ``jointactuatorfrc``                                          |
+---------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| **坐标系（Frame）** | ``framepos``, ``framequat``, ``framexaxis``, ``frameyaxis``, ``framezaxis``, ``framelinvel``, ``frameangvel``, ``framelinacc``, ``frameangacc``    |
+---------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| **其他（Other）**   | ``actuatorpos``, ``actuatorvel``, ``actuatorfrc``, ``subtreecom``, ``subtreelinvel``, ``subtreeangmom``, ``clock``, ``e_potential``, ``e_kinetic`` |
+---------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+

``ObjRef`` 标识传感器附着到哪个 MuJoCo 元素。``entity`` 字段将查找范围限定
在特定实体的命名空间内，传感器名称会相应地自动加上前缀（例如，实体
``"robot"`` 上的 ``"imu_acc"`` 会变成 ``"robot/imu_acc"``）。

.. code-block:: python

    from mjlab.sensor import BuiltinSensorCfg, ObjRef

    # Accelerometer attached to a site.
    BuiltinSensorCfg(
        name="imu_acc",
        sensor_type="accelerometer",
        obj=ObjRef(type="site", name="imu_site", entity="robot"),
    )

    # Joint limit sensor with output clamping.
    BuiltinSensorCfg(
        name="knee_limit",
        sensor_type="jointlimitpos",
        obj=ObjRef(type="joint", name="knee_joint", entity="robot"),
        cutoff=0.1,
    )

    # Relative frame position (end-effector w.r.t. base).
    BuiltinSensorCfg(
        name="ee_pos",
        sensor_type="framepos",
        obj=ObjRef(type="body", name="end_effector", entity="robot"),
        ref=ObjRef(type="body", name="base", entity="robot"),
    )


自动发现
^^^^^^^^

实体 XML 中已经定义的传感器会在场景组合期间被自动发现，并加上实体名称前缀。
无需为这些传感器创建 ``BuiltinSensorCfg``。

.. code-block:: xml

    <!-- In robot.xml -->
    <sensor>
        <accelerometer name="trunk_imu" site="imu_site"/>
        <jointpos name="hip_sensor" joint="hip_joint"/>
    </sensor>

.. code-block:: python

    # Access by prefixed name.
    imu = env.scene["robot/trunk_imu"]
    hip = env.scene["robot/hip_sensor"]


ContactSensor
-------------

每个物理步中，MuJoCo 都会为整个场景生成一个扁平、无结构的接触对列表。单个
脚部 geom 可能会同时产生多个与地面的接触，并与其他实体的接触交错在一起。
``ContactSensor`` 会从这个原始列表中筛选出你关心的接触对，将每个元素的多个
接触归约到固定数量，并把结果打包成策略可以直接使用的、整洁的批量化张量。它
构建在 MuJoCo 原生的
`接触传感器 <https://mujoco.readthedocs.io/en/stable/XMLreference.html#sensor-contact>`_ 之上。

主元素与次元素
^^^^^^^^^^^^^^

接触是成对的：你通常想知道的是“机器人的脚是否碰到了地形？”，而不只是
“是否有东西碰到了东西”。``primary`` 定义你要测量的元素（脚），
``secondary`` 可选地限制它们接触的对象（地形）。当 ``secondary`` 为
``None`` 时，与主元素的任何接触都会被计入。

每一侧都通过 ``ContactMatch`` 指定。``mode`` 选择 MuJoCo 元素类型
（``"geom"``、``"body"`` 或 ``"subtree"``），``pattern`` 接受一个正则表达式
或正则表达式元组，与实体内的元素名称进行匹配。

.. code-block:: python

    from mjlab.sensor import ContactSensorCfg, ContactMatch

    # Foot geoms contacting the terrain body.
    ContactSensorCfg(
        name="feet_ground",
        primary=ContactMatch(
            mode="geom", pattern=r".*_foot$", entity="robot",
        ),
        secondary=ContactMatch(mode="body", pattern="terrain"),
        fields=("found", "force"),
    )

    # Self-collision: pelvis subtree against itself.
    ContactSensorCfg(
        name="self_collision",
        primary=ContactMatch(
            mode="subtree", pattern="pelvis", entity="robot",
        ),
        secondary=ContactMatch(
            mode="subtree", pattern="pelvis", entity="robot",
        ),
        fields=("found",),
    )

输出形状
^^^^^^^^

类似 ``r".*_foot$"`` 的模式会解析出 ``P`` 个主元素（例如四足机器人的四只
脚）。每个主元素在输出张量的按接触（per-contact）轴上占据一列：

.. list-table::
   :header-rows: 1
   :widths: 35 25 40

   * - 字段组
     - 形状
     - 说明
   * - 按接触
       (``found``, ``force``, ``torque``, ``dist``, ``pos``, ``normal``,
       ``tangent``)
     - ``[B, P * num_slots, ...]``
     - 以主元素为主（primary-major）：索引
       ``[i * num_slots : (i + 1) * num_slots]`` 属于主元素 ``i``。
   * - 按主元素
       (``current_air_time``, ``last_air_time``,
       ``current_contact_time``, ``last_contact_time``)
     - ``[B, P]``
     - 腾空时间字段按主元素累积，并跨 slot 归约（只要任一 slot 处于接触
       状态，即视为该主元素处于接触状态）。

在默认的 ``num_slots=1`` 下，这两种形状家族重合（``N == P``），这就是为什么
大多数代码可以把两者都当作 ``[B, P, ...]`` 来处理。

使用 :attr:`mjlab.sensor.contact_sensor.ContactSensor.primary_names` 可以在
模式展开后恢复索引到名称的映射：

.. code-block:: python

    sensor = env.scene["feet_contact"]
    sensor.primary_names                # ["FR_foot", "FL_foot", "RR_foot", "RL_foot"]
    sensor.data.current_air_time[:, 0]  # air time for FR_foot

归约
^^^^

单个主元素可能与次元素同时存在多个接触（例如，平底脚放在粗糙地形上会有多个
接触点）。``reduce`` 模式将这些原始接触坍缩为 ``num_slots`` 个代表性接触：

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - 模式
     - 行为
   * - ``"none"``
     - 快速、非确定性地选择至多 ``num_slots`` 个接触。
   * - ``"mindist"``
     - 保留最深的 ``num_slots`` 个接触。
   * - ``"maxforce"``
     - 按力的大小保留最强的 ``num_slots`` 个接触。
   * - ``"netforce"``
     - 将所有接触求和为力加权质心处的一个净力螺旋（net wrench）。无论
       ``num_slots`` 为多少，每个主元素始终只输出一个 slot。

何时设置 ``num_slots > 1``
""""""""""""""""""""""""""

绝大多数配置都将 ``num_slots`` 保持为默认值 ``1``，因为模式展开已经为每个
感兴趣的元素生成一列（每只脚一列、每根手指一列、每个 body link 一列）。只有
当单个主元素可能存在多个物理上相互独立、且你希望分别检查的接触点时，才需要
增大 ``num_slots``，例如：

- 根据平底脚的角部接触计算压力中心。
- 根据多个指尖与物体之间的接触点推断抓取质量。
- 通过观察接触区域某一角是否失去接触来检测倾翻。

在这些情况下，应将 ``num_slots`` 与 ``{"mindist", "maxforce", "none"}`` 中的
``reduce`` 搭配使用。当 ``reduce="netforce"`` 时它不起作用。

.. note::

   ``num_slots`` 是传感器存储数量的上限，并不保证 MuJoCo 真的会产生这么多
   接触。碰撞检测器会根据所涉及的 geom 类型，限制每个 geom 对生成的接触点
   数量。例如，球体与平面的 geom 对最多产生一个接触，而盒体与盒体的 geom 对
   最多产生四个。因此，在球体主元素对平面次元素的配置上设置
   ``num_slots=8``，会有七个 slot 永远为零。每个 geom 对的限制请查阅
   `MuJoCo 的碰撞文档 <https://mujoco.readthedocs.io/en/stable/computation/index.html#collision-detection>`_ 。

字段
^^^^

``fields`` 元组选择要提取哪些接触量。只有请求的字段会被分配内存；其余字段在
输出 dataclass 上为 ``None``。可用字段为 ``"found"``、``"force"``、
``"torque"``、``"dist"``、``"pos"``、``"normal"`` 和 ``"tangent"``。

.. note::

   除非接触对启用了摩擦（这要求接触对中至少有一个 geom 的 ``condim >= 3``），
   否则 ``torque`` 以及 ``force`` 的摩擦切向分量都为零。当 ``condim=1``
   （无摩擦）时，接触只会产生法向力。这是接触的物理属性，而不是传感器的
   限制。

腾空时间跟踪
^^^^^^^^^^^^

运动（locomotion）任务通常需要知道脚何时落地、何时离地，以用于步态奖励。
设置 ``track_air_time=True`` 即可启用按主元素的计时。传感器会在
``ContactData`` 上额外维护四个形状均为 ``[B, P]`` 的张量：
``current_air_time``、``last_air_time``、``current_contact_time`` 和
``last_contact_time``。两个辅助方法为状态切换事件提供边沿检测：

.. code-block:: python

    sensor = env.scene["feet_air"]
    first_contact = sensor.compute_first_contact(dt)  # [B, P], True for primaries that just landed
    first_air = sensor.compute_first_air(dt)           # [B, P], True for primaries that just took off

即使 ``num_slots > 1``，腾空时间也是按主元素统计的：传感器会跨 slot 对
``found`` 进行归约，只要任一 slot 处于接触，该主元素即被视为处于接触。

.. _contact-sensor-history:

历史（decimation 安全接触）
^^^^^^^^^^^^^^^^^^^^^^^^^^^

在使用 decimation（每个策略步包含多个物理子步）时，一次短暂的碰撞可能完全
在子步循环内发生并结束。等到策略读取传感器时，接触已经消失，``found`` 报告
为零。在传感器配置上设置 ``history_length``，可以让传感器为力、力矩和距离
字段保留最近 *N* 个子步的滚动缓冲区。策略随后可以检查完整的历史，判断是否
真的发生了接触。

将 ``history_length`` 设置为与你的 decimation 值相等，使缓冲区恰好覆盖一个
策略步：

.. code-block:: python

    ContactSensorCfg(
        name="self_collision",
        primary=ContactMatch(mode="subtree", pattern="pelvis", entity="robot"),
        secondary=ContactMatch(mode="subtree", pattern="pelvis", entity="robot"),
        fields=("found", "force"),
        history_length=4,  # matches decimation=4
    )

历史张量与常规字段一起存放在 ``ContactData`` 上：

.. code-block:: python

    data = sensor.data
    data.force_history   # [B, N, H, 3]  (H = history_length)
    data.torque_history  # [B, N, H, 3]
    data.dist_history    # [B, N, H]

索引 0 是最近的子步。要检查是否有任一子步的接触力超过某个阈值：

.. code-block:: python

    force_mag = torch.norm(data.force_history, dim=-1)  # [B, N, H]
    had_contact = (force_mag > 10.0).any(dim=1).any(dim=-1)  # [B]

.. note::

   ``track_air_time=True`` 已经会为步态奖励跨子步累积接触状态，因此脚部
   地面传感器通常不需要 ``history_length``。历史缓冲适用于需要检测否则会被
   遗漏的短暂碰撞的传感器（自碰撞、非法接触终止）。


输出
^^^^

``ContactData`` 是一个 dataclass，其字段与配置中的 ``fields`` 元组一一对应。
未请求的字段为 ``None``。

.. code-block:: python

    @dataclass
    class ContactData:
        found: Tensor | None     # [B, N] contact count
        force: Tensor | None     # [B, N, 3]
        torque: Tensor | None    # [B, N, 3]
        dist: Tensor | None      # [B, N] penetration depth
        pos: Tensor | None       # [B, N, 3] contact position
        normal: Tensor | None    # [B, N, 3] surface normal
        tangent: Tensor | None   # [B, N, 3]

        # With track_air_time=True.
        current_air_time: Tensor | None
        last_air_time: Tensor | None
        current_contact_time: Tensor | None
        last_contact_time: Tensor | None


RayCastSensor
-------------

``RayCastSensor`` 提供 GPU 加速的光线投射，用于地形扫描和深度感知。它支持
网格和针孔相机两种光线模式，并具有可配置的对齐方式。完整文档参见
:ref:`raycast_sensor` 。


RGB-D 相机
----------

``CameraSensor`` 使用 MuJoCo 相机渲染 RGB 和深度图像。完整文档参见
:ref:`rgbd_camera` 。


扩展：自定义传感器
------------------

所有传感器都继承自 ``Sensor[T]``，这是一个泛型基类，其中 ``T`` 是 ``data``
属性返回的数据类型（例如 ``BuiltinSensor`` 返回 ``torch.Tensor``，
``ContactSensor`` 返回 ``ContactData``）。

基类提供自动的按步缓存。``data`` 属性在每步首次访问时调用
``_compute_data()`` 并缓存结果。当 ``update()`` 或 ``reset()`` 被调用时，
缓存会自动失效，因此同一步内的多次读取（来自不同的观测项或奖励项）只需支付
一次计算开销。

**生命周期方法：**

- ``edit_spec``：在场景构建期间向 MjSpec 添加传感器元素。
- ``initialize``：编译后的设置。缓存传感器索引、分配缓冲区、解析引用。
- ``update``：每个物理步调用一次。使数据缓存失效。可重写以维护按步状态
  （例如腾空时间计数器）。
- ``reset``：在环境重置时调用。使数据缓存失效。可重写以清除按环境的
  状态。
- ``_compute_data``：计算并返回传感器输出。当缓存过期时由 ``data`` 属性
  延迟调用。

``ContactSensor`` 和 ``RayCastSensor`` 是开发自定义传感器时最完整的参考
实现。

.. toctree::
   :maxdepth: 1
   :hidden:

   raycast_sensor
   rgbd_camera
