.. _tutorial-add-sensors-on-robot:

为机器人添加传感器
=========================

.. currentmodule:: isaaclab


资产类允许我们创建并仿真机器人的物理实体，
而传感器则帮助我们获取关于环境的信息。它们通常以比仿真更低的
频率更新，适用于获取各种本体感受（proprioceptive）和外感受（exteroceptive）信息。例如，相机传感器可用于获取环境的视觉
信息，接触传感器可用于获取机器人与环境的接触
信息。

在本教程中，我们将了解如何向机器人添加不同的传感器。本教程将使用
ANYmal-C 机器人。ANYmal-C 是一个具有 12 个自由度的四足机器人。
它有 4 条腿，每条腿有 3 个自由度。该机器人拥有以下
传感器：

- 机器人头部的一个相机传感器，提供 RGB-D 图像
- 一个提供地形高度信息的高度扫描传感器
- 机器人足部的接触传感器，提供接触信息

我们从前一篇关于 :ref:`tutorial-interactive-scene` 的教程继续本教程，
在那篇教程中我们学习了 :class:`scene.InteractiveScene` 类。


代码
~~~~~~~~

本教程对应
``scripts/tutorials/04_sensors`` 目录中的 ``add_sensors_on_robot.py`` 脚本。

.. dropdown:: Code for add_sensors_on_robot.py
   :icon: code

   .. literalinclude:: ../../../../scripts/tutorials/04_sensors/add_sensors_on_robot.py
      :language: python
      :emphasize-lines: 72-95, 143-153, 167-168
      :linenos:


代码解析
~~~~~~~~~~~~~~~~~~

与前面教程中向场景添加资产的方式类似，传感器也通过场景配置添加
到场景中。所有传感器都继承自 :class:`sensors.SensorBase` 类，
并通过各自的配置类进行配置。每个传感器实例可以定义自己的
更新周期，即传感器更新的频率。更新周期通过 :attr:`sensors.SensorBaseCfg.update_period` 属性以秒为单位
指定。

传感器根据指定的路径和传感器类型被附着到场景中的 prim 上。
它们可能有一个在场景中创建的关联 prim，也可能被附着到现有的 prim 上。
例如，相机传感器有对应的在场景中创建的 prim，而对于
接触传感器来说，启用接触报告是刚体 prim 上的一个属性。

下面，我们介绍本教程中使用的不同传感器及其配置方式。
关于它们的更多描述，请查阅 :mod:`sensors` 模块。

相机传感器
-------------

相机使用 :class:`sensors.CameraCfg` 定义。它基于 USD Camera 传感器，
不同的数据类型通过 Omniverse Replicator API 采集。由于它在场景中有对应的 prim，
因此这些 prim 会在场景中指定的 prim 路径处被创建。

相机传感器的配置包括以下参数：

* :attr:`~sensors.CameraCfg.spawn`：要创建的 USD 相机的类型。可以是
  :class:`~sim.spawners.sensors.PinholeCameraCfg` 或 :class:`~sim.spawners.sensors.FisheyeCameraCfg`。
* :attr:`~sensors.CameraCfg.offset`：相机传感器相对于父级 prim 的偏移。
* :attr:`~sensors.CameraCfg.data_types`：要采集的数据类型。可以是 ``rgb``、
  ``distance_to_image_plane``、``normals`` 或 USD Camera 传感器支持的其他类型。

为了将 RGB-D 相机传感器附着到机器人头部，我们指定一个相对于机器人基座
坐标系的偏移。该偏移以相对于基座坐标系的平移和旋转指定，
并使用 :attr:`~sensors.CameraCfg.OffsetCfg.convention` 指定偏移的约定。

下面我们展示本教程中使用的相机传感器的配置。我们将
更新周期设置为 0.1 秒，这意味着相机传感器以 10Hz 的频率更新。prim 路径表达式
设置为 ``{ENV_REGEX_NS}/Robot/base/front_cam``，其中 ``{ENV_REGEX_NS}`` 是环境命名空间，
``"Robot"`` 是机器人的名称，``"base"`` 是相机所附着 prim 的名称，
``"front_cam"`` 是与相机传感器关联的 prim 的名称。

.. literalinclude:: ../../../../scripts/tutorials/04_sensors/add_sensors_on_robot.py
   :language: python
   :start-at: camera = CameraCfg(
   :end-before: height_scanner = RayCasterCfg(

高度扫描传感器
--------------

高度扫描传感器（height-scanner）是使用 NVIDIA Warp 光线投射内核实现的虚拟传感器。
通过 :class:`sensors.RayCasterCfg`，我们可以指定要投射的光线模式以及
要对其投射光线的网格。由于它们是虚拟传感器，场景中不会为它们创建对应的
prim。它们被附着到场景中的某个 prim 上，该 prim
用于指定传感器的位置。

在本教程中，基于光线投射的高度扫描传感器被附着到机器人的基座坐标系。光线模式通过 :attr:`~sensors.RayCasterCfg.pattern` 属性指定。
对于均匀网格模式，我们使用 :class:`~sensors.patterns.GridPatternCfg` 指定该模式。
由于我们只关心高度信息，因此不需要考虑机器人的横滚（roll）和俯仰（pitch）。
所以，我们将 :attr:`~sensors.RayCasterCfg.ray_alignment` 设置为 "yaw"。

对于高度扫描传感器，你可以可视化光线命中网格的点。这是
通过将 :attr:`~sensors.SensorBaseCfg.debug_vis` 属性设置为 true 来完成的。

高度扫描传感器的完整配置如下：

.. literalinclude:: ../../../../scripts/tutorials/04_sensors/add_sensors_on_robot.py
   :language: python
   :start-at: height_scanner = RayCasterCfg(
   :end-before: contact_forces = ContactSensorCfg(

接触传感器
--------------

接触传感器封装了 PhysX 接触报告 API，用于获取机器人与环境的接触信息。由于它依赖于 PhysX，接触传感器要求在机器人的刚体上启用接触报告 API。
这可以通过在资产配置中将
:attr:`~sim.spawners.RigidObjectSpawnerCfg.activate_contact_sensors` 设置为 true 来完成。

通过 :class:`sensors.ContactSensorCfg`，可以指定我们想
获取接触信息的 prim。还可以设置额外的标志来获取关于接触的更多信息，
例如接触腾空时间（contact air time）、被过滤 prim 之间的接触力等。

在本教程中，我们将接触传感器附着到机器人的足部。机器人的足部
命名为 ``"LF_FOOT"``、``"RF_FOOT"``、``"LH_FOOT"`` 和 ``"RH_FOOT"``。我们传入正则表达式
``".*_FOOT"`` 来简化 prim 路径的指定。该正则表达式匹配所有
以 ``"_FOOT"`` 结尾的 prim。

我们将更新周期设置为 0，以与仿真相同的频率更新传感器。此外，
对于接触传感器，我们可以指定要存储的接触信息的历史长度。在本
教程中，我们将历史长度设置为 6，这意味着会存储最近 6 个
仿真步的接触信息。

接触传感器的完整配置如下：

.. literalinclude:: ../../../../scripts/tutorials/04_sensors/add_sensors_on_robot.py
   :language: python
   :start-at: contact_forces = ContactSensorCfg(
   :lines: 1-3

运行仿真循环
---------------------------

与使用资产时类似，传感器的缓冲区和物理句柄只在
仿真播放时才会初始化，也就是说，在创建场景之后调用 ``sim.reset()`` 非常重要。

.. literalinclude:: ../../../../scripts/tutorials/04_sensors/add_sensors_on_robot.py
   :language: python
   :start-at: # Play the simulator
   :end-at: sim.reset()

除此之外，仿真循环与前面的教程类似。传感器作为场景更新的
一部分被更新，它们内部会根据各自的更新
周期处理缓冲区的更新。

传感器的数据可以通过其 ``data`` 属性访问。作为示例，我们展示如何
访问本教程中创建的不同传感器的数据：

.. literalinclude:: ../../../../scripts/tutorials/04_sensors/add_sensors_on_robot.py
   :language: python
   :start-at: # print information from the sensors
   :end-at: print("Received max contact force of: ", torch.max(scene["contact_forces"].data.net_forces_w).item())


代码执行
~~~~~~~~~~~~~~~~~~


现在我们已经通读了代码，接下来运行脚本并查看结果：

.. code-block:: bash

   ./isaaclab.sh -p scripts/tutorials/04_sensors/add_sensors_on_robot.py --num_envs 2 --enable_cameras


该命令应该会打开一个包含地面平面、灯光和两个四足机器人的 Stage。
在机器人周围，你应该会看到红色球体，它们指示光线命中网格的点。
此外，你可以将视口切换到相机视图，查看相机
传感器采集的 RGB 图像。关于如何将视口切换到相机视图的更多信息，请查看
`here <https://youtu.be/htPbcKkNMPs?feature=shared>`_ 。

.. figure:: ../../_static/tutorials/tutorial_add_sensors. jpg
    :align: center
    :figwidth: 100%
    :alt: result of add_sensors_on_robot.py

要停止仿真，你可以关闭窗口，或在终端中按 ``Ctrl+C``。

在本教程中，我们介绍了如何创建和使用不同的传感器，此外 :mod:`sensors` 模块中还有更多可用的传感器。
我们在
``scripts/tutorials/04_sensors`` 目录中提供了使用这些传感器的最小示例。为完整起见，可以使用以下命令运行这些脚本：

.. code-block:: bash

   # Frame Transformer
   ./isaaclab.sh -p scripts/tutorials/04_sensors/run_frame_transformer.py

   # Ray Caster
   ./isaaclab.sh -p scripts/tutorials/04_sensors/run_ray_caster.py

   # Ray Caster Camera
   ./isaaclab.sh -p scripts/tutorials/04_sensors/run_ray_caster_camera.py

   # USD Camera
   ./isaaclab.sh -p scripts/tutorials/04_sensors/run_usd_camera.py --enable_cameras
