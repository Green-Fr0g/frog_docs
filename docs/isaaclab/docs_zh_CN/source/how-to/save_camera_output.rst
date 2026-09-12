.. _how-to-save-images-and-3d-reprojection:


保存渲染图像与 3D 重投影
===========================================

.. currentmodule:: isaaclab

本指南随附 ``IsaacLab/scripts/tutorials/04_sensors`` 目录中的
``run_usd_camera.py`` 脚本。

.. dropdown:: run_usd_camera.py 的代码
   :icon: code

   .. literalinclude:: ../../../scripts/tutorials/04_sensors/run_usd_camera.py
      :language: python
      :emphasize-lines: 171-179, 229-247, 251-264
      :linenos:


使用 Replicator Basic Writer 保存
------------------------------------

要保存相机输出，我们使用 Omniverse Replicator 的 basic writer 类。该类允许我们将
图像保存为 numpy 格式。有关 basic writer 的更多信息，请查看
`documentation <https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator/writer_examples.html>`_ 。

.. literalinclude:: ../../../scripts/tutorials/04_sensors/run_usd_camera.py
   :language: python
   :start-at: rep_writer = rep.BasicWriter(
   :end-before: # Camera positions, targets, orientations

在推进仿真器的过程中，图像可以保存到定义的文件夹中。由于 BasicWriter 仅支持
使用 NumPy 格式保存数据，我们首先需要将 PyTorch 传感器数据转换为 NumPy 数组，
然后再将它们打包进一个字典。

.. literalinclude:: ../../../scripts/tutorials/04_sensors/run_usd_camera.py
   :language: python
   :start-at: # Save images from camera at camera_index
   :end-at: single_cam_info = camera.data.info[camera_index]

完成此步骤后，我们就可以使用 BasicWriter 保存图像。

.. literalinclude:: ../../../scripts/tutorials/04_sensors/run_usd_camera.py
   :language: python
   :start-at: # Pack data back into replicator format to save them using its writer
   :end-at: rep_writer.write(rep_output)


投影到 3D 空间
------------------------

我们提供了将深度图像投影到 3D 空间的实用工具。重投影操作使用
PyTorch 运算完成，从而实现更快的计算。

.. code-block:: python

   from isaaclab.utils.math import transform_points, unproject_depth

   # Pointcloud in world frame
   points_3d_cam = unproject_depth(
      camera.data.output["distance_to_image_plane"], camera.data.intrinsic_matrices
   )

   points_3d_world = transform_points(points_3d_cam, camera.data.pos_w, camera.data.quat_w_ros)

或者，我们可以使用 :meth:`isaaclab.sensors.camera.utils.create_pointcloud_from_depth` 函数
从深度图像创建点云，并将其变换到世界坐标系。

.. literalinclude:: ../../../scripts/tutorials/04_sensors/run_usd_camera.py
   :language: python
   :start-at: # Derive pointcloud from camera at camera_index
   :end-before: # In the first few steps, things are still being instanced and Camera.data

得到的点云可以使用 Isaac Sim 的 :mod:`isaacsim.util.debug_draw` 扩展进行可视化。
这使得在 3D 空间中可视化点云变得非常容易。

.. literalinclude:: ../../../scripts/tutorials/04_sensors/run_usd_camera.py
   :language: python
   :start-at: # In the first few steps, things are still being instanced and Camera.data
   :end-at: pc_markers.visualize(translations=pointcloud)


运行脚本
--------------------

要运行随附的脚本，请执行以下命令：

.. code-block:: bash

   # Usage with saving and drawing
   ./isaaclab.sh -p scripts/tutorials/04_sensors/run_usd_camera.py --save --draw --enable_cameras

   # Usage with saving only in headless mode
   ./isaaclab.sh -p scripts/tutorials/04_sensors/run_usd_camera.py --save --headless --enable_cameras


仿真应当会启动，您可以观察到不同对象下落。会在 ``IsaacLab/scripts/tutorials/04_sensors``
目录中创建一个输出文件夹，图像将保存在其中。此外，
您应该会看到点云绘制在 viewport 的 3D 空间中。

要停止仿真，请关闭窗口，或在终端中使用 ``Ctrl+C`` 。
