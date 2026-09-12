.. _heterogeneous_worlds:

异构世界
========

mjlab 可以在单一批量仿真中运行这样的场景：不同的并行世界为同一个逻辑
实体使用不同的网格资源。世界 0 可能仿真一个立方体，世界 1 一个球体，
世界 2 一个碗。所有世界共享同一份编译后的场景以及相同的 body 和关节
结构；只有网格以及随网格而来的按 geom 属性（friction、contact bits、
mass、density 等少数几项）在不同世界之间不同。铰接的道具同样支持
（你可以在变体根 body 之下再放一个铰链或滑动关节），只要关节拓扑在各个
变体之间一致即可。该功能通过 ``VariantEntityCfg`` 暴露。下一节详细列出
了各变体之间哪些可以不同、哪些必须一致。


快速上手
--------

假设你想让一部分并行世界放置球体，另一部分放置圆锥体，并由同一个共享
场景同时运行两者。把每个变体定义为一个返回 ``MjSpec`` 的函数，然后在
同一个 ``VariantEntityCfg`` 下组合它们：

.. code-block:: python

    import mujoco

    from mjlab.entity import EntityCfg, VariantEntityCfg


    def make_sphere_spec() -> mujoco.MjSpec:
        spec = mujoco.MjSpec()
        mesh = spec.add_mesh(name="visual")
        mesh.make_sphere(subdivision=3)
        mesh.scale[:] = (0.05,) * 3
        body = spec.worldbody.add_body(name="prop")
        body.add_freejoint()
        body.add_geom(type=mujoco.mjtGeom.mjGEOM_MESH, meshname="visual")
        return spec


    def make_cone_spec() -> mujoco.MjSpec:
        spec = mujoco.MjSpec()
        mesh = spec.add_mesh(name="visual")
        mesh.make_cone(nedge=16, radius=0.04)
        body = spec.worldbody.add_body(name="prop")
        body.add_freejoint()
        body.add_geom(type=mujoco.mjtGeom.mjGEOM_MESH, meshname="visual")
        return spec


    object_cfg = VariantEntityCfg(
        variants={
            "sphere": make_sphere_spec,
            "cone":   make_cone_spec,
        },
        assignment={"cone": 2.0},  # twice as many cones as spheres
        init_state=EntityCfg.InitialStateCfg(pos=(0.0, 0.0, 0.2)),
    )

把这个变体实体像普通 ``EntityCfg`` 一样接入 :ref:`scene`：

.. code-block:: python

    from mjlab.scene import SceneCfg

    scene_cfg = SceneCfg(
        num_envs=4096,
        entities={"object": object_cfg},
    )

持有圆锥体的世界数量将是球体的两倍。未在 ``assignment`` 字典中列出的
变体默认权重为 1.0；完全省略 ``assignment`` 则在所有变体之间均匀分配。


变体之间可以有哪些不同
----------------------

**变体之间可以自由不同的部分：** 每个槽位分配到的网格资源、变体 body 上
每个 ``(body, role)`` 桶中网格 geom 的数量（一个变体可以比另一个拥有更多
碰撞网格）、随网格而来的按网格 geom 属性（friction、contact bits、mass、
density、``condim`` 以及其他少数几项），以及在各个变体对每个 body 达成
一致的那一种惯性表示方式之内的显式 body 惯性值。

**变体之间必须一致的部分：** body 树、关节拓扑、图元（非网格）geom，
以及所有执行器/传感器/肌腱/等式约束。各变体还必须对每个 body 的惯性
表示方式达成一致（网格推导、对角或 fullinertia），并且不得在任何元素上
使用保留的 ``mjlab/pad/`` 名称前缀。变体实体还必须是浮动基座的：根 body
上声明了 freejoint。

验证器在实体构建时运行，并抛出 ``ValueError``，指明出错的变体和具体的
不匹配之处。


变体如何组装
------------

mjlab 把所有变体的网格资源合并进同一个 ``MjSpec``，并为变体 body 提供足够
多的网格 geom *槽位*，以覆盖每个 ``(body, role)`` 桶在所有变体中出现的
最大网格数量。一个槽位由 ``(body_path, role, ordinal)`` 标识。``role``
是 "visual" 或 "collision"，由 ``contype``/``conaffinity`` 推导得出；
mujoco_warp 的 ``geom_contype``/``geom_conaffinity`` 是一维共享的（并非
按世界区分），因此槽位的 role 在构造上就是跨世界固定的。

一个具体例子
~~~~~~~~~~~~

假设变体 ``sphere`` 在 prop body 上有 1 个视觉网格 geom 和 2 个碰撞网格
geom，而变体 ``cone`` 在同一 body 上有 1 个视觉网格 geom 和 4 个碰撞网格
geom。

.. code-block:: text

    sphere variant body              cone variant body
    -------------------              -------------------
    prop body                        prop body
      [visual] sphere_vis              [visual] cone_vis
      [coll]   sphere_col_0            [coll]   cone_col_0
      [coll]   sphere_col_1            [coll]   cone_col_1
                                       [coll]   cone_col_2
                                       [coll]   cone_col_3

mjlab 遍历每个变体的 body 树，按 ``(body_path, role)`` 对网格 geom 分桶，
并把并集铺排成槽位：

.. list-table::
   :header-rows: 1
   :widths: 8 18 8 12 27 27

   * - 槽位
     - body_path
     - role
     - ordinal
     - sphere 填入
     - cone 填入
   * - 0
     - /prop
     - visual
     - 0
     - sphere_vis
     - cone_vis
   * - 1
     - /prop
     - collision
     - 0
     - sphere_col_0
     - cone_col_0
   * - 2
     - /prop
     - collision
     - 1
     - sphere_col_1
     - cone_col_1
   * - 3
     - /prop
     - collision
     - 2
     - *(unfilled)*
     - cone_col_2
   * - 4
     - /prop
     - collision
     - 3
     - *(unfilled)*
     - cone_col_3

共 5 个槽位。合并后场景的 prop body 拥有 5 个网格 geom：槽位 0 加上
4 个碰撞槽位（sphere 的 2 个与 cone 的 4 个的并集）。在合并时，每个变体
的网格资源都会以唯一名称加入合并后的 spec（例如 ``sphere/sphere_vis``、
``cone/cone_col_2``）。

合并后的场景只编译一次，得到一份所有世界在布局上完全一致的规范化
``MjModel``：相同的 nbody、ngeom，相同的 body 和 geom ID。mjlab 在这份
模型之上施加的按世界覆盖，正是让世界彼此异构的原因。

运行时每个世界看到什么
~~~~~~~~~~~~~~~~~~~~~~

``sphere`` 生效的世界只看到它的 3 个网格；多出来的 2 个碰撞槽位通过按
世界的 ``geom_dataid = -1`` 被禁用，mujoco_warp 会跳过它们。``cone``
生效的世界则看到全部 5 个接好的网格。

.. list-table::
   :header-rows: 1
   :widths: 14 14 12 12 12 12 12

   * - 世界
     - 变体
     - 槽位 0
     - 槽位 1
     - 槽位 2
     - 槽位 3
     - 槽位 4
   * - 0
     - sphere
     - sphere_vis
     - sphere_col_0
     - sphere_col_1
     - **关闭 (-1)**
     - **关闭 (-1)**
   * - 1
     - cone
     - cone_vis
     - cone_col_0
     - cone_col_1
     - cone_col_2
     - cone_col_3

三类按世界覆盖承载了这些差异：

* **geom_dataid** 是一张 ``(num_envs, ngeom)`` 表。世界 W 对应的行决定
  每个槽位指向哪个编译后的网格。``-1`` 是 mujoco_warp 本来就理解的
  "跳过我"哨兵值。
* **网格派生字段** (``geom_size``、``geom_rbound``、``geom_aabb``、
  ``geom_pos``、``geom_quat``、``body_mass``、``body_subtreemass``、
  ``body_inertia``、``body_invweight0``、``body_ipos``、``body_iquat``）
  以 ``(num_envs, ...)`` 数组存储。sphere 世界的取值反映球形的惯性张量
  和球体大小的 AABB；cone 世界的取值反映圆锥体。完整列表见
  ``mjlab.entity.variants.VARIANT_DEPENDENT_FIELDS``。
* **按网格 geom 属性** (contact bits、friction、mass、density、condim、
  group、priority、rgba、solref、solimp、margin、gap）在合并时按变体
  记录在 ``VariantGeomSpec`` 中，并在按变体的参考编译期间原样恢复到槽位
  geom 上。因此，如果 sphere 的碰撞 geom 是 ``friction=0.5`` 而 cone 的
  是 ``friction=1.2``，那么世界 W 每一步使用的 friction 反映的是它所
  分配变体的原始取值。唯一的例外是 ``material``：它不会跨变体传播；如果
  需要按世界的外观变化，请对 ``geom_rgba`` / ``mat_rgba`` 使用 DR。

如果 ``sphere`` 添加了 ``cone`` 没有的 body（或反过来），验证器会在任何
合并逻辑运行之前拒绝该配置。槽位机制只允许在匹配的 body 内伸缩网格 geom
的数量；geom 层级以上的所有结构性内容都必须一致。

.. note::

   **合并场景编译后不会破坏 prop body 的惯性吗？**

   不会，但值得弄清楚原因，因为朴素的直觉认为会。如果你把每个变体的网格
   geom 都堆到 prop body 上再调用 ``spec.compile()``，MuJoCo 会把每个
   geom 的惯性贡献加总，得到一个质量和惯性张量毫无意义地混杂了所有变体
   形状的 body。

   mjlab 用两层机制避免这个问题：

   * **合并场景并不会把所有变体的 geom 都堆到 body 上。** 合并 spec 中
     的 prop body 携带的是变体 0 的网格 geom（保留其原始的 mass 和
     density），对于任何变体 0 未填满的槽位，则补上一个 ``mass = 0``、
     ``density = 0`` 的合成填充 geom。填充物对 body 惯性没有任何贡献。
     其他变体的网格只以**网格资源**的形式存在于合并 spec 中（位于
     assets 部分，而不是作为任何 body 上的 geom）。它们在运行时通过按
     世界的 ``geom_dataid`` 接入，永远不会影响宿主编译的惯性求和。
   * **按世界覆盖来自按变体的源 spec 编译。** 即便有上述机制，合并场景
     编译得到的 prop body 惯性也只对变体 0 正确。对于其他每个变体，
     mjlab 会把该变体原始的源 spec 单独编译（一个 body、一个变体份量的
     网格），读取得到的 ``body_mass``、``body_inertia``、``body_ipos``、
     ``body_iquat``、``body_invweight0`` 和 ``body_subtreemass``，并写入
     prop body 索引处的按世界数组。

   最终效果：世界 W 的 prop body 惯性与你单独编译变体 W 的源 spec 得到的
   结果逐字节相等。有一个回归测试（``tests/test_variants.py`` 中的
   ``test_visual_collision_split_inertia_matches_independent_compile``）
   正是针对这一点、与各变体的独立编译结果进行断言的。


世界分配
--------

世界如何映射到变体，由 ``VariantEntityCfg`` 上的 ``assignment`` 字段
控制。它接受三种形式：

* ``None`` (默认)：在所有变体之间均匀分配。
* ``dict[str, float]``：按变体设置权重。未列出的变体默认权重为 1.0。
* ``Callable[[int], Sequence[int]]``：显式的分配函数，在仿真初始化时以
  ``num_envs`` 调用。

``None`` 和字典两种情况都使用
`最大余数法 <https://en.wikipedia.org/wiki/Largest_remainder_method>`_。
每个变体的配额是 ``q_i = (w_i / sum(w)) * num_envs``；每个变体先获得
``floor(q_i)`` 个世界，剩余的 ``num_envs - sum(floors)`` 个世界分配给
小数余数最大的变体，平局时按声明顺序打破。对 ``num_envs = 10`` 和权重
``(1.0, 2.0, 1.0)``，得到每个变体 ``(3, 5, 2)`` 个世界。权重会在内部
归一化，因此 ``{"a": 1, "b": 2, "c": 1}`` 和
``{"a": 0.25, "b": 0.5, "c": 0.25}`` 产生完全相同的分配。允许权重为零，
此时该变体获得 0 个世界；但至少要有一个变体的权重为正。

默认路径和字典路径在给定 ``(assignment, num_envs)`` 的情况下是完全
确定性的。取 ``assignment={"a": 1, "b": 1}`` 和 ``num_envs = 8``，你总是
得到 ``[0, 0, 0, 0, 1, 1, 1, 1]``。这里不涉及随机种子；同样的配置每次
重跑都会产生同样的划分。注意，划分的*边界*取决于 ``num_envs``，因此当你
改变 ``num_envs`` 时，世界 W 对应的变体不一定保持稳定。如果你需要跨批次
大小的显式按世界稳定性（例如"无论启动多少个环境，世界 0 永远是变体 0，
世界 1 永远是变体 1"），请使用下面的可调用分配。

变体分配在 ``Simulation`` 初始化时固定，不会在回合重置时重新采样。其
设计用途是跨批次的异构训练，而不是按回合的网格随机化。

用户代码可以通过 ``env.sim.world_to_variant`` 读取解析后的分配：

.. code-block:: python

    >>> env.sim.world_to_variant["object"]
    tensor([0, 0, 0, 1, 1, 1, 1, 1, 1, 1])

该映射以实体名（不带末尾斜杠）为键，返回一个 ``(num_envs,)`` 张量，其中
是按 ``VariantEntityCfg.variants`` 中的声明顺序排列的变体索引。对于非
变体场景，该字典为空。


用可调用对象自定义分配
~~~~~~~~~~~~~~~~~~~~~~

当按权重的默认行为不符合需求时，可以向 ``assignment`` 传入一个可调用
对象。该可调用对象接收 ``num_envs``，必须返回一个长度为 ``num_envs``、
取值在 ``[0, len(variants))`` 范围内的变体索引序列。返回序列的长度和
取值范围会在仿真初始化时校验；不匹配会抛出 ``ValueError`` 并指明出错的
实体。

几种常见模式：

**轮询（Round-robin）** - 按世界索引在变体之间循环。

.. code-block:: python

    cfg = VariantEntityCfg(
        variants={"a": make_a, "b": make_b, "c": make_c},
        assignment=lambda n: [w % 3 for w in range(n)],
    )

**分层对半（Stratified halves）** - 前一半是变体 0，后一半是变体 1。

.. code-block:: python

    cfg = VariantEntityCfg(
        variants={"easy": make_easy, "hard": make_hard},
        assignment=lambda n: [0] * (n // 2) + [1] * (n - n // 2),
    )

域随机化
--------

变体场景上的域随机化会自动保留每个变体的基线。仿真初始化时，mjlab 会把
依赖变体的字段快照为 ``(num_envs, ...)`` 张量，并注册到
``sim.per_world_default_fields`` 中。读取默认值的 DR 操作（缩放、加性
偏移）会检测到这一注册，并按环境索引每世界的默认值数组，因此对一个同时
包含 100 g 球体变体和 1 kg 立方体变体的批次施加 10% 的质量缩放，产生的
是*围绕每个变体自身质量*的 10% 扰动，而不是相对某个共享模板质量的
10%。

不依赖变体的字段（``geom_friction``、``dof_armature``、``dof_damping``
等）在变体场景和非变体场景上的行为完全相同。

对于惯性随机化，推荐使用 ``dr.pseudo_inertia``，它通过
`Rucker 和 Wensing (2022) <https://par.nsf.gov/servlets/purl/10347458>`_
的伪惯性矩阵分解，同时随机化质量、质心偏移、主惯性矩和主轴姿态。它对
任意扰动幅度都是精确的，并且在尺度不同的各个变体之间保持物理一致性。
``dr.body_mass`` 只修改 ``body_mass`` 而不改动惯性张量，调用时会发出
``UserWarning``；它只适合模拟在质心处添加的一个点质量，不适合密度类
随机化。在变体场景上，这个区别比单一资产场景更重要，因为不同变体的质量
常常相差一个数量级。


查看器
------

原生查看器、离屏渲染器和 Viser 查看器都会在渲染之前把所选环境的按世界
字段同步到宿主 ``MjModel``，因此渲染出的几何体与所查看环境被分配的变体
一致。在原生查看器中切换环境（``,`` 和 ``.`` 键）会相应更新显示的网格。

Viser 把网格数据烘焙进批量句柄，无法依赖对 ``geom_dataid`` 的实时视图。
它按视觉指纹（网格选择、局部 geom 坐标系、烘焙的外观）对世界分组，并为
每组构建一个批量句柄，每个环境都分配到自己的句柄。一个有 N 个变体的场景
通常每个 body 最多产生 N 个句柄。凸包可视化则按变体、基于该变体的网格
顶点计算。


性能
----

**每步开销不受变体数量影响。** 依赖变体的字段以按世界数组的形式存储，
在现有内核中按世界索引访问，没有任何按变体的分支或分发。

**构建开销与变体总数呈线性关系。** mjlab 先把合并场景编译一次，得到
规范化 ``MjModel``，然后单独编译每个变体原始的（未合并的）源 spec，以
恢复该变体按 body 和按 geom 的网格派生字段。每次按变体编译只看到该变体
的单个 body 和网格，因此其开销与场景中变体总数无关。

对于一个声明了 k 个变体的变体实体场景，构建会运行 ``1 + k`` 次编译。
有多个变体实体时，编译在各实体之间解耦：两个各含 5 个变体的变体实体的
开销是 ``1 + 5 + 5 = 11`` 次编译，而不是 ``1 + 5 * 5 = 26`` 次。作为
数量级参考，在 CPU 上使用典型程序化网格时，每次按变体编译约需 1-2 ms，
因此 100 个变体的场景在启动时要多花几百毫秒，1000 个变体的场景约需
两秒。

合并 spec 同时包含所有变体的网格资源，因此场景构建时的内存开销与所有
变体的网格顶点/面片总数成正比。这笔开销只在启动时支付一次，不会影响
训练吞吐。


限制
----

**仅支持浮动基座。** 每个变体的根 body 必须声明自由关节。固定基座的
变体会被拒绝；适用于非变体实体的 mocap 自动包装在这里不会生效。

**材质资源不会传播。** 每个变体的 ``contype``、``conaffinity``、
``condim``、``friction``、``mass``、``density``、``group``、
``priority``、``rgba``、``solref``、``solimp``、``margin`` 和 ``gap``
会在编译期间按世界恢复，但槽位 geom 上的 ``material`` 引用继承的是模板
变体所设置的材质。如需按世界的外观变化，请对 ``geom_rgba`` /
``mat_rgba`` 使用 DR。

**分配在仿真初始化时固定。** 目前没有 API 可以在回合重置时把某个世界
切换到另一个变体。在仿真的整个生命周期内，世界 W 的网格资源就是它初始化
时被分配的那个。目前不支持按回合的网格随机化；DR 可以在固定的变体上改变
标量属性（质量、摩擦、颜色、缩放），但无法把一个网格换成另一个。

**不支持按世界不同的运动学拓扑。** 各变体必须共享相同的 body 树、关节
以及执行器/传感器数量，因此无法配置诸如：

* 每个世界的物体数量不同（世界 0 的桌上有两个道具，世界 1 有三个）；
* 每个世界的铰接不同（世界 0 的道具是带滑动关节的铰接抽屉，世界 1 的
  道具是刚性方块）。

真正的异构拓扑需要 mujoco_warp 上游的支持，而目前尚不存在。
