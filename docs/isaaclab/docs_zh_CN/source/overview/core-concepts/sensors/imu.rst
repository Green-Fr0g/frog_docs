.. _overview_sensors_imu:

.. currentmodule:: isaaclab

惯性测量单元（IMU）
===================================

.. figure:: ../../../_static/overview/sensors/imu_diagram.jpg
    :align: center
    :figwidth: 100%
    :alt: A diagram outlining the basic force relationships for the IMU sensor

惯性测量单元（IMU）是一种用于测量物体加速度的传感器。传统上，这类传感器被设计为报告线性加速度和角速度，其工作原理与电子秤类似：它们报告由**作用在传感器上的净力**导出的加速度。

一个朴素的 IMU 实现会在传感器静止于某个局部重力场中时，报告一个由重力引起的负加速度。这对大多数实际应用来说通常并不需要，因此大多数实际的 IMU 传感器通常包含一个**重力偏置（gravity bias）**，并假设设备在地球表面上工作。我们在 Isaac Lab 中提供的 IMU 包含一个类似的偏置项，其默认值为 +g。这意味着如果你在仿真中添加一个 IMU 而不改变这个偏置项，你将检测到一个与重力加速度反平行的 :math:`+ 9.81 m/s^{2}` 加速度。

考虑一个简单的环境，其中一只 Anymal 四足机器人的两只前脚各装有一个 IMU。

.. literalinclude:: ../../../../../scripts/demos/sensors/imu_sensor.py
  :language: python
  :lines: 39-63

这里我们显式地移除了其中一个传感器的偏置，运行示例脚本并通过可视化，就可以看到这对报告值的影响。

.. figure:: ../../../_static/overview/sensors/imu_visualizer.jpg
    :align: center
    :figwidth: 100%
    :alt: IMU visualized

注意，右前脚的偏置被显式设置为 (0,0,0)。在可视化中，你应该能看到表示右侧 IMU 加速度的箭头随时间快速变化，而表示左侧 IMU 的箭头则始终指向垂直轴方向。

按常规方式从传感器检索数值

.. code-block:: python

  def run_simulator(sim: sim_utils.SimulationContext, scene: InteractiveScene):
    .
    .
    .
    # Simulate physics
    while simulation_app.is_running():
      .
      .
      .
      # print information from the sensors
      print("-------------------------------")
      print(scene["imu_LF"])
      print("Received linear velocity: ", scene["imu_LF"].data.lin_vel_b)
      print("Received angular velocity: ", scene["imu_LF"].data.ang_vel_b)
      print("Received linear acceleration: ", scene["imu_LF"].data.lin_acc_b)
      print("Received angular acceleration: ", scene["imu_LF"].data.ang_acc_b)
      print("-------------------------------")
      print(scene["imu_RF"])
      print("Received linear velocity: ", scene["imu_RF"].data.lin_vel_b)
      print("Received angular velocity: ", scene["imu_RF"].data.ang_vel_b)
      print("Received linear acceleration: ", scene["imu_RF"].data.lin_acc_b)
      print("Received angular acceleration: ", scene["imu_RF"].data.ang_acc_b)

传感器报告值的波动是传感器计算加速度方式的直接结果，即通过对仿真报告的相邻真值速度值做有限差分近似来计算。我们可以在报告的结果中看到这一点（注意**线性加速度**），因为右脚的加速度虽然很小，但显式为零。

.. code-block:: bash

  Imu sensor @ '/World/envs/env_.*/Robot/LF_FOOT':
          view type         : <class 'omni.physics.tensors.impl.api.RigidBodyView'>
          update period (s) : 0.0
          number of sensors : 1

  Received linear velocity:  tensor([[ 0.0203, -0.0054,  0.0380]], device='cuda:0')
  Received angular velocity:  tensor([[-0.0104, -0.1189,  0.0080]], device='cuda:0')
  Received linear acceleration:  tensor([[ 4.8344, -0.0205,  8.5305]], device='cuda:0')
  Received angular acceleration:  tensor([[-0.0389, -0.0262, -0.0045]], device='cuda:0')
  -------------------------------
  Imu sensor @ '/World/envs/env_.*/Robot/RF_FOOT':
          view type         : <class 'omni.physics.tensors.impl.api.RigidBodyView'>
          update period (s) : 0.0
          number of sensors : 1

  Received linear velocity:  tensor([[0.0244, 0.0077, 0.0431]], device='cuda:0')
  Received angular velocity:  tensor([[ 0.0122, -0.1360, -0.0042]], device='cuda:0')
  Received linear acceleration:  tensor([[-0.0018,  0.0010, -0.0032]], device='cuda:0')
  Received angular acceleration:  tensor([[-0.0373, -0.0050, -0.0053]], device='cuda:0')
  -------------------------------

.. dropdown:: imu_sensor.py 的代码
   :icon: code

   .. literalinclude:: ../../../../../scripts/demos/sensors/imu_sensor.py
      :language: python
      :linenos:
