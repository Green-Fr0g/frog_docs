将物理 Prim 在仿真中固定
=============================================

.. currentmodule:: isaaclab

当一个 USD prim 上应用了物理 schema 后，它就会受到物理仿真的影响。
这意味着该 prim 可以在仿真世界中移动、旋转，并与其他 prim 发生碰撞。
然而，在某些情况下，我们希望让某些 prim 在仿真世界中保持静止，
即该 prim 仍然参与碰撞，但其位置和朝向不应发生变化。

以下各节介绍如何生成带有物理 schema 的 prim，并使其在仿真世界中保持静止。

静态碰撞体
----------------

静态碰撞体是不受物理影响、但可以与仿真世界中的其他 prim 发生碰撞的 prim。
它们没有应用任何刚体属性。不过，这也意味着它们无法通过物理张量 API
（即通过 :class:`assets.RigidObject` 类）访问。

例如，要在仿真世界中生成一个静止的圆锥体，可以使用以下代码：

.. code-block:: python

    import isaaclab.sim as sim_utils

    cone_spawn_cfg = sim_utils.ConeCfg(
        radius=0.15,
        height=0.5,
        collision_props=sim_utils.CollisionPropertiesCfg(),
        visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.0, 1.0, 0.0)),
    )
    cone_spawn_cfg.func(
        "/World/Cone", cone_spawn_cfg, translation=(0.0, 0.0, 2.0), orientation=(0.5, 0.0, 0.5, 0.0)
    )


刚体对象
------------

刚体对象（即仅由单个刚体组成的对象）可以通过将参数
:attr:`sim.schemas.RigidBodyPropertiesCfg.kinematic_enabled` 设置为 True 来使其静止。
这会使该对象成为运动学（kinematic）对象，从而不受物理影响。

例如，要在仿真世界中生成一个静止的、但带有刚体 schema 的圆锥体，
可以使用以下代码：

.. code-block:: python

    import isaaclab.sim as sim_utils

    cone_spawn_cfg = sim_utils.ConeCfg(
        radius=0.15,
        height=0.5,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(kinematic_enabled=True),
        mass_props=sim_utils.MassPropertiesCfg(mass=1.0),
        collision_props=sim_utils.CollisionPropertiesCfg(),
        visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.0, 1.0, 0.0)),
    )
    cone_spawn_cfg.func(
        "/World/Cone", cone_spawn_cfg, translation=(0.0, 0.0, 2.0), orientation=(0.5, 0.0, 0.5, 0.0)
    )


关节体
------------

固定关节体（articulation）的根需要在该关节体的根刚体连杆上有一个固定关节。
这可以通过将参数 :attr:`sim.schemas.ArticulationRootPropertiesCfg.fix_root_link`
设置为 True 来实现。根据该参数的取值，可能出现以下几种情况：

* 如果设置为 :obj:`None`，则不修改根连杆。
* 如果关节体已有固定的根连杆，此标志将启用或禁用该固定关节。
* 如果关节体没有固定的根连杆，此标志将在世界坐标系与根连杆之间创建一个固定关节。
  该关节以 "FixedJoint" 命名，创建在根连杆之下。

例如，要生成一个 ANYmal 机器人并使其在仿真世界中保持静止，可以使用以下代码：

.. code-block:: python

    import isaaclab.sim as sim_utils
    from isaaclab.utils.assets import ISAACLAB_NUCLEUS_DIR

    anymal_spawn_cfg = sim_utils.UsdFileCfg(
        usd_path=f"{ISAACLAB_NUCLEUS_DIR}/Robots/ANYbotics/ANYmal-C/anymal_c.usd",
        activate_contact_sensors=True,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            retain_accelerations=False,
            linear_damping=0.0,
            angular_damping=0.0,
            max_linear_velocity=1000.0,
            max_angular_velocity=1000.0,
            max_depenetration_velocity=1.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=True,
            solver_position_iteration_count=4,
            solver_velocity_iteration_count=0,
            fix_root_link=True,
        ),
    )
    anymal_spawn_cfg.func(
        "/World/ANYmal", anymal_spawn_cfg, translation=(0.0, 0.0, 0.8), orientation=(1.0, 0.0, 0.0, 0.0)
    )


由于 ANYmal 机器人的根连杆位于 ``"/World/ANYmal/base"`` 路径，
这会在世界坐标系与 ANYmal 机器人根连杆之间的 prim 路径 ``"/World/ANYmal/base/FixedJoint"`` 处
创建一个固定关节。


补充说明
-------------

考虑到 USD 资产设计的灵活性，通常会遇到以下几种情形：

1. **刚体 prim 上有 关节体根 schema，且没有固定关节**：

   这是浮动基座关节体最常见且推荐的情形。根 prim 同时具有刚体属性和关节体根属性。
   在这种情况下，关节体根被解析为浮动基座，关节体的根 prim 为 ``Link0Xform``。

   .. code-block:: text

       ArticulationXform
           └── Link0Xform  (RigidBody and ArticulationRoot schema)

2. **父 prim 上有 关节体根 schema，且有固定关节**：

   这是固定基座关节体的预期结构。根 prim 只有刚体属性，而关节体根属性应用于其父 prim。
   在这种情况下，关节体根被解析为固定基座，关节体的根 prim 为 ``Link0Xform``。

   .. code-block:: text

       ArticulationXform (ArticulationRoot schema)
           └── Link0Xform  (RigidBody schema)
           └── FixedJoint (connecting the world frame and Link0Xform)

3. **父 prim 上有 关节体根 schema，且没有固定关节**：

   这是根 prim 只有刚体属性、而关节体根属性应用于其父 prim 的情形。
   但是，世界坐标系与根连杆之间没有创建固定关节。
   在这种情况下，关节体被解析为浮动基座系统。然而，PhysX 解析器会使用自己的
   启发式规则（例如字母顺序）来确定关节体的根 prim。它可能会选择 ``Link0Xform``
   处的 prim 作为根 prim，也可能选择其他 prim 作为根 prim。

   .. code-block:: text

       ArticulationXform (ArticulationRoot schema)
           └── Link0Xform  (RigidBody schema)

4. **刚体 prim 上有 关节体根 schema，且有固定关节**：

   虽然这是一种有效的情形，但不推荐使用，因为它可能导致非预期的行为。在这种情况下，
   关节体仍被解析为浮动基座系统。然而，在世界坐标系与根连杆之间创建的固定关节
   被视为最大坐标树（maximal coordinate tree）的一部分。这与 PhysX 将关节体视为
   固定基座系统不同。因此，仿真的行为可能不符合预期。

   .. code-block:: text

       ArticulationXform
           └── Link0Xform  (RigidBody and ArticulationRoot schema)
           └── FixedJoint (connecting the world frame and Link0Xform)

对于浮动基座关节体，根 prim 通常同时具有刚体属性和关节体根属性。
但是，直接将该 prim 连接到世界坐标系会导致仿真把固定关节视为最大坐标树的一部分。
这与 PhysX 将关节体视为固定基座系统不同。

在内部，当参数 :attr:`sim.schemas.ArticulationRootPropertiesCfg.fix_root_link` 被设置为 True
且关节体被检测为浮动基座系统时，固定关节会创建在世界坐标系与该关节体的根刚体连杆之间。
但是，为了让 PhysX 解析器将关节体视为固定基座系统，关节体根属性会从根刚体 prim 上移除，
并改为应用到其父 prim 上。

.. note::

    在未来的 Isaac Sim 版本中，PhysX 的关节体根 schema 中将添加一个显式标志，
    用于在固定基座和浮动基座系统之间切换。这将消除对上述变通方法的需要。
