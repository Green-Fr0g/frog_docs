.. _how-to-estimate-how-cameras-can-run:


查找您应当使用多少个/哪种相机进行训练
================================================

.. currentmodule:: isaaclab

目前 Isaac Lab 中有多种相机类型：USD 相机（标准相机）、Tiled Camera（平铺相机）
和 Ray Caster（光线投射）相机。这些相机类型在功能和性能上各有不同。``benchmark_cameras.py``
脚本可用于了解各相机类型之间的差异，也可以表征它们在不同参数（如相机数量、图像尺寸和数据类型）
下的相对性能。

提供此工具是为了让用户能够方便地找到在满足其场景要求的同时性能最佳的相机类型/参数。该工具还有助于
估算实际可以运行的相机数量上限，前提是您希望在最大化环境数量的同时最小化单步耗时。

此工具可以将相机注入来自 gym registry 的现有任务中，这对于在特定场景下对相机进行基准测试很有用。
此外，如果您安装了 ``pynvml`` ，还可以让该工具自动找出在您的任务环境中、在指定的系统资源利用率
阈值内可以运行的相机数量上限（无需训练；在每个时间步采取零动作）。

本指南随附 ``scripts/benchmarks`` 目录中的 ``benchmark_cameras.py`` 脚本。

.. dropdown:: benchmark_cameras.py 的代码
   :icon: code

   .. literalinclude:: ../../../scripts/benchmarks/benchmark_cameras.py
      :language: python
      :linenos:


可用参数
-------------------

首先，运行

.. code-block:: bash

   ./isaaclab.sh -p scripts/benchmarks/benchmark_cameras.py -h

以查看此工具支持调整的所有参数。


有关 ``autotune`` 相关命令行参数的更多信息，请查看其帮助说明，
以了解如何自动确定相机数量上限。


在任务环境中比较性能并自动确定任务的相机数量上限
------------------------------------------------------------------------------------------

目前，Tiled Camera 是能够处理多个动态对象的相机中性能最好的。

例如，要查看您的系统在 cartpole 环境中、每个环境 2 个相机（即共 50 个环境）、
仅 RGB 模式下处理 100 个 Tiled Camera 的能力，可运行

.. code-block:: bash

   ./isaaclab.sh -p scripts/benchmarks/benchmark_cameras.py \
   --task Isaac-Cartpole-v0 --num_tiled_cameras 100 \
   --task_num_cameras_per_env 2 \
   --tiled_camera_data_types rgb

如果您安装了 pynvml（``./isaaclab.sh -p -m pip install pynvml``），还可以找出在指定环境中、
在某一性能阈值（由最大 CPU 利用率百分比、最大内存利用率百分比、最大 GPU 计算百分比和最大 GPU
显存利用率百分比指定）内可以运行的相机数量上限。例如，要找出使用 cartpole 时可以运行的相机数量上限，
可以运行：

.. code-block:: bash

   ./isaaclab.sh -p scripts/benchmarks/benchmark_cameras.py \
   --task Isaac-Cartpole-v0 --num_tiled_cameras 100 \
   --task_num_cameras_per_env 2 \
   --tiled_camera_data_types rgb --autotune \
   --autotune_max_percentage_util 100 80 50 50

Autotune 可能导致程序崩溃，这意味着它尝试一次性运行过多的相机。
不过，最大利用率百分比参数的目的正是防止这种情况发生。

基准测试的输出不包含训练网络的开销，因此请考虑降低最大利用率百分比以预留这部分开销。
最终输出的相机数量是所有相机的总数，因此要将输出相机数量除以每个环境的相机数，
才能得到环境总数。


比较相机类型与性能（不指定任务）
--------------------------------------------------------------

该工具也可以在没有任务环境的情况下评估性能。
例如，要查看 100 个随机对象和 2 个标准相机，可以运行

.. code-block:: bash

   ./isaaclab.sh -p scripts/benchmarks/benchmark_cameras.py \
   --height 100 --width 100 --num_standard_cameras 2 \
   --standard_camera_data_types instance_segmentation_fast normals --num_objects 100 \
   --experiment_length 100

如果由于性能原因您的系统无法承受，进程会被终止。
建议在运行此脚本时监控 CPU/内存利用率和 GPU 利用率，以了解渲染所需相机需要多少资源。
在 Ubuntu 上，您可以在运行脚本时使用 ``htop`` 和 ``nvtop`` 等工具实时监控资源；
在 Windows 上，可以使用任务管理器。

如果您的系统难以承受所需的相机数量，可以尝试以下方法

   - 切换到无头（headless）模式（提供 ``--headless`` 参数）
   - 确保您使用的是 GPU 流水线而不是 CPU！
   - 如果您没有使用 Tiled Camera，请切换到 Tiled Camera
   - 降低相机分辨率
   - 减少每个相机的 data_types 数量。
   - 减少相机数量
   - 减少场景中的对象数量

如果您的系统能够承受这些相机数量，时间统计数据将被打印到终端。
仿真停止后，可以使用 CTRL+C 关闭。
