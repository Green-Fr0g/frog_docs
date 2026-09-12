.. _how-to-write-articulation-config:


编写资产配置
==============================

.. currentmodule:: isaaclab

本指南介绍创建 :class:`~assets.ArticulationCfg` 的过程。
:class:`~assets.ArticulationCfg` 是一个配置对象，用于定义
Isaac Lab 中 :class:`~assets.Articulation` 的属性。

.. note::

   虽然本指南只介绍如何创建 :class:`~assets.ArticulationCfg` ，
   但创建任何其他资产配置对象的过程都是类似的。

我们将使用 Cartpole 示例来演示如何创建 :class:`~assets.ArticulationCfg` 。
Cartpole 是一个简单的机器人，由一个带杆的小车组成。小车
可以沿轨道自由移动，杆可以绕小车自由旋转。此配置示例的文件位于
``source/isaaclab_assets/isaaclab_assets/robots/cartpole.py`` 。

.. dropdown:: Cartpole 配置的代码
   :icon: code

   .. literalinclude:: ../../../source/isaaclab_assets/isaaclab_assets/robots/cartpole.py
      :language: python
      :linenos:


定义生成配置
--------------------------------

如 :ref:`tutorial-spawn-prims` 教程所述，生成配置定义了
要生成的资产的属性。生成可以通过程序化方式进行，也可以
通过现有的资产文件（例如 USD 或 URDF）进行。在本例中，我们将从 USD 文件生成
Cartpole。

从 USD 文件生成资产时，我们定义其 :class:`~sim.spawners.from_files.UsdFileCfg` 。
该配置对象接受以下参数：

* :class:`~sim.spawners.from_files.UsdFileCfg.usd_path`：用于生成的 USD 文件路径
* :class:`~sim.spawners.from_files.UsdFileCfg.rigid_props`：关节体根（root）的属性
* :class:`~sim.spawners.from_files.UsdFileCfg.articulation_props`：关节体所有连杆的属性

最后两个参数是可选的。如果不指定，它们将保持在 USD 文件中的默认值。

.. literalinclude:: ../../../source/isaaclab_assets/isaaclab_assets/robots/cartpole.py
   :language: python
   :lines: 19-35
   :dedent:

如果要从 URDF 文件（而不是 USD 文件）导入关节体，可以将
:class:`~sim.spawners.from_files.UsdFileCfg` 替换为 :class:`~sim.spawners.from_files.UrdfFileCfg` 。
更多细节请查看 API 文档。


定义初始状态
--------------------------

每个资产都需要通过其配置定义在仿真中的初始状态或*默认*状态。
该配置存储在资产的默认状态缓冲区中，当需要重置资产
状态时可以访问这些缓冲区。

.. note::
   资产的初始状态是相对于其局部环境坐标系定义的。在重置资产状态时，需要
   将其变换到全局仿真坐标系。更多
   细节请查看 :ref:`tutorial-interact-articulation` 教程。


对于关节体，:class:`~assets.ArticulationCfg.InitialStateCfg` 对象定义了
关节体根的初始状态以及其所有关节的初始状态。在本
例中，我们将在 XY 平面原点、Z 高度 2.0 米处生成 Cartpole。
同时，关节位置和速度设置为 0.0。

.. literalinclude:: ../../../source/isaaclab_assets/isaaclab_assets/robots/cartpole.py
   :language: python
   :lines: 36-38
   :dedent:

定义执行器配置
-----------------------------------

执行器（actuator）是关节体的关键组件。通过此配置，可以
定义要使用的执行器模型类型。我们可以使用物理引擎提供的内部执行器模型
（即隐式执行器模型），也可以使用由用户自定义方程组控制的
自定义执行器模型（即显式执行器模型）。
有关执行器的更多细节，请参见 :ref:`overview-actuators` 。

Cartpole 的关节体有两个执行器，每个执行器对应它的一个关节：
``cart_to_pole`` 和 ``slider_to_cart`` 。作为示例，我们为这些执行器使用两种不同的执行器模型。
不过，由于它们都使用相同的执行器模型，也可以
将它们合并为单个执行器模型。

.. dropdown:: 使用多个执行器模型的执行器模型配置
   :icon: code

   .. literalinclude:: ../../../source/isaaclab_assets/isaaclab_assets/robots/cartpole.py
      :language: python
      :lines: 39-49
      :dedent:


.. dropdown:: 使用单个执行器模型的执行器模型配置
   :icon: code

   .. code-block:: python

      actuators={
         "all_joints": ImplicitActuatorCfg(
            joint_names_expr=[".*"],
            effort_limit=400.0,
            velocity_limit=100.0,
            stiffness={"slider_to_cart": 0.0, "cart_to_pole": 0.0},
            damping={"slider_to_cart": 10.0, "cart_to_pole": 0.0},
         ),
      },


ActuatorCfg 速度/力限制的注意事项
-------------------------------------------------

在 IsaacLab v1.4.0 中，朴素的 ``velocity_limit`` 和 ``effort_limit`` 属性**并没有**一致地
推送到物理求解器中：

- **隐式执行器**
  - velocity_limit 被忽略（从未在仿真中设置）
  - effort_limit 会被设置到仿真中

- **显式执行器**
  - velocity_limit 和 effort_limit 都只被驱动模型使用，而不被求解器使用


在 v2.0.1 中我们意外地改变了这一点：所有 velocity_limit 和 effort_limit，无论隐式还是
显式，都被应用到了求解器。这导致许多在旧的默认无上限求解器
限制下进行的训练失效。

为了在恢复原有行为的同时仍让用户能够完全控制求解器限制，我们引入了两个新标志：

* **velocity_limit_sim**
  在仿真中设置物理求解器的最大关节速度上限。

* **effort_limit_sim**
  在仿真中设置物理求解器的最大关节力上限。


这些标志在仿真层面显式设置求解器的关节速度和关节力上限。

另一方面，对于所有显式执行器，velocity_limit 和 effort_limit 建模的是电机的硬件级约束，
用于力矩计算，而不是限制仿真级别的约束。
对于隐式执行器，由于它们不建模电机硬件限制，``velocity_limit`` 已在 v2.1.1 中
移除并标记为弃用。这保持了与 v1.4.0 中相同的行为。最终，隐式执行器的
``velocity_limit`` 和 ``effort_limit`` 将被弃用，只保留 ``velocity_limit_sim`` 和
``effort_limit_sim`` 。


.. table:: 限制选项对比

    .. list-table::
      :header-rows: 1
      :widths: 20 40 40

      * - **属性**
        - **隐式执行器**
        - **显式执行器**
      * - ``velocity_limit``
        - 已弃用（是 ``velocity_limit_sim`` 的别名）
        - 由模型（例如 DC 电机）使用，不设置到仿真中
      * - ``effort_limit``
        - 已弃用（是 ``effort_limit_sim`` 的别名）
        - 由模型使用，不设置到仿真中
      * - ``velocity_limit_sim``
        - 设置到仿真中
        - 设置到仿真中
      * - ``effort_limit_sim``
        - 设置到仿真中
        - 设置到仿真中



想要调优底层物理求解器限制的用户应设置 ``_sim`` 标志。


USD 与 ActuatorCfg 差异的解决规则
------------------------------------------

USD 存在默认值，而且 ActuatorCfg 可以指定为 None 或某个覆盖值，这有时会让人
困惑到底什么值会被写入仿真。解决规则遵循以下简单规则，逐关节、逐
属性生效：

.. table:: USD 与 ActuatorCfg 的解决规则

    +------------------------+------------------------+--------------------+
    | **条件**               | **ActuatorCfg 值**     | **应用的值**       |
    +========================+========================+====================+
    | 未提供覆盖值           | 未指定                 | USD 值             |
    +------------------------+------------------------+--------------------+
    | 提供了覆盖值           | 用户的 ActuatorCfg     | 与 ActuatorCfg 相同|
    +------------------------+------------------------+--------------------+


深入查看 USD 有时不方便。为了帮助澄清到底写入了什么值，我们设计了一个标志
:attr:`~isaaclab.assets.ArticulationCfg.actuator_value_resolution_debug_print` ，
帮助用户弄清仿真中实际使用的确切值。

每当用户在 ActuatorCfg 中覆盖了某个执行器参数（或未指定）时，
我们将其与从 USD 定义读取的值进行比较，并记录任何差异。对于每个关节和每个属性，
如果发现不匹配的值，我们会记录解决结果：

  1. **USD 值**
     从 USD 资产解析出的默认限制或增益。

  2. **ActuatorCfg 值**
     用户提供的覆盖值（如果未提供则为 "Not Specified"）。

  3. **应用的值**
     仿真实际使用的最终值：如果用户没有覆盖，则与 USD 值一致；
     否则反映用户的设置。

只有当存在差异时，才会以警告表格的形式输出此解决信息。
下面是您会看到的内容的示例::

    +----------------+--------------------+---------------------+----+-------------+--------------------+----------+
    |     Group      |      Property      |         Name        | ID |  USD Value  | ActuatorCfg Value  | Applied  |
    +----------------+--------------------+---------------------+----+-------------+--------------------+----------+
    | panda_shoulder | velocity_limit_sim |    panda_joint1     |  0 |    2.17e+00 |   Not Specified    | 2.17e+00 |
    |                |                    |    panda_joint2     |  1 |    2.17e+00 |   Not Specified    | 2.17e+00 |
    |                |                    |    panda_joint3     |  2 |    2.17e+00 |   Not Specified    | 2.17e+00 |
    |                |                    |    panda_joint4     |  3 |    2.17e+00 |   Not Specified    | 2.17e+00 |
    |                |     stiffness      |    panda_joint1     |  0 |    2.29e+04 |      8.00e+01      | 8.00e+01 |
    |                |                    |    panda_joint2     |  1 |    2.29e+04 |      8.00e+01      | 8.00e+01 |
    |                |                    |    panda_joint3     |  2 |    2.29e+04 |      8.00e+01      | 8.00e+01 |
    |                |                    |    panda_joint4     |  3 |    2.29e+04 |      8.00e+01      | 8.00e+01 |
    |                |      damping       |    panda_joint1     |  0 |    4.58e+03 |      4.00e+00      | 4.00e+00 |
    |                |                    |    panda_joint2     |  1 |    4.58e+03 |      4.00e+00      | 4.00e+00 |
    |                |                    |    panda_joint3     |  2 |    4.58e+03 |      4.00e+00      | 4.00e+00 |
    |                |                    |    panda_joint4     |  3 |    4.58e+03 |      4.00e+00      | 4.00e+00 |
    |                |      armature      |    panda_joint1     |  0 |    0.00e+00 |   Not Specified    | 0.00e+00 |
    |                |                    |    panda_joint2     |  1 |    0.00e+00 |   Not Specified    | 0.00e+00 |
    |                |                    |    panda_joint3     |  2 |    0.00e+00 |   Not Specified    | 0.00e+00 |
    |                |                    |    panda_joint4     |  3 |    0.00e+00 |   Not Specified    | 0.00e+00 |
    | panda_forearm  | velocity_limit_sim |    panda_joint5     |  4 |    2.61e+00 |   Not Specified    | 2.61e+00 |
    |                |                    |    panda_joint6     |  5 |    2.61e+00 |   Not Specified    | 2.61e+00 |
    |                |                    |    panda_joint7     |  6 |    2.61e+00 |   Not Specified    | 2.61e+00 |
    |                |     stiffness      |    panda_joint5     |  4 |    2.29e+04 |      8.00e+01      | 8.00e+01 |
    |                |                    |    panda_joint6     |  5 |    2.29e+04 |      8.00e+01      | 8.00e+01 |
    |                |                    |    panda_joint7     |  6 |    2.29e+04 |      8.00e+01      | 8.00e+01 |
    |                |      damping       |    panda_joint5     |  4 |    4.58e+03 |      4.00e+00      | 4.00e+00 |
    |                |                    |    panda_joint6     |  5 |    4.58e+03 |      4.00e+00      | 4.00e+00 |
    |                |                    |    panda_joint7     |  6 |    4.58e+03 |      4.00e+00      | 4.00e+00 |
    |                |      armature      |    panda_joint5     |  4 |    0.00e+00 |   Not Specified    | 0.00e+00 |
    |                |                    |    panda_joint6     |  5 |    0.00e+00 |   Not Specified    | 0.00e+00 |
    |                |                    |    panda_joint7     |  6 |    0.00e+00 |   Not Specified    | 0.00e+00 |
    |                |      friction      |    panda_joint5     |  4 |    0.00e+00 |   Not Specified    | 0.00e+00 |
    |                |                    |    panda_joint6     |  5 |    0.00e+00 |   Not Specified    | 0.00e+00 |
    |                |                    |    panda_joint7     |  6 |    0.00e+00 |   Not Specified    | 0.00e+00 |
    |  panda_hand    | velocity_limit_sim | panda_finger_joint1 |  7 |    2.00e-01 |   Not Specified    | 2.00e-01 |
    |                |                    | panda_finger_joint2 |  8 |    2.00e-01 |   Not Specified    | 2.00e-01 |
    |                |     stiffness      | panda_finger_joint1 |  7 |    1.00e+06 |      2.00e+03      | 2.00e+03 |
    |                |                    | panda_finger_joint2 |  8 |    1.00e+06 |      2.00e+03      | 2.00e+03 |
    |                |      armature      | panda_finger_joint1 |  7 |    0.00e+00 |   Not Specified    | 0.00e+00 |
    |                |                    | panda_finger_joint2 |  8 |    0.00e+00 |   Not Specified    | 0.00e+00 |
    |                |      friction      | panda_finger_joint1 |  7 |    0.00e+00 |   Not Specified    | 0.00e+00 |
    |                |                    | panda_finger_joint2 |  8 |    0.00e+00 |   Not Specified    | 0.00e+00 |
    +----------------+--------------------+---------------------+----+-------------+--------------------+----------+

为了保持日志输出的整洁，:attr:`~isaaclab.assets.ArticulationCfg.actuator_value_resolution_debug_print`
默认为 False，需要时请记得将其打开。
