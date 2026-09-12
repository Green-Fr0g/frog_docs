Showroom 演示
==============

Isaac Lab 的核心接口扩展 ``isaaclab`` 提供了执行器、物体、机器人和传感器的主要模块。我们提供
了一系列演示脚本和教程，以最简的方式展示如何在代码中使用所提供的接口。

以下是一些可以快速运行并查看效果的 Showroom 脚本：


-  生成不同的机械臂并施加随机关节位置指令：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            ./isaaclab.sh -p scripts/demos/arms.py

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            isaaclab.bat -p scripts\demos\arms.py

   .. image:: ../_static/demos/arms.jpg
      :width: 100%
      :alt: Isaac Lab 中的机械臂


-  生成不同的双足机器人：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            ./isaaclab.sh -p scripts/demos/bipeds.py

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            isaaclab.bat -p scripts\demos\bipeds.py

   .. image:: ../_static/demos/bipeds.jpg
      :width: 100%
      :alt: Isaac Lab 中的双足机器人


-  生成不同的可变形（柔软）物体并让它们从高处落下：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            ./isaaclab.sh -p scripts/demos/deformables.py

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            isaaclab.bat -p scripts\demos\deformables.py

   .. image:: ../_static/demos/deformables.jpg
      :width: 100%
      :alt: Isaac Lab 中的可变形基本形状物体


-  交互式推理已训练的 H1 粗糙地形运动（locomotion）策略：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            ./isaaclab.sh -p scripts/demos/h1_locomotion.py

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            isaaclab.bat -p scripts\demos\h1_locomotion.py

   .. image:: ../_static/demos/h1_locomotion.jpg
      :width: 100%
      :alt: Isaac Lab 中的 H1 运动

   这是一个可以使用鼠标和键盘运行的交互式演示。要进入第三人称视角，
   请点击场景中的一个类人角色。进入第三人称视角后，可以使用键盘控制该类人角色：

   * ``UP``：前进
   * ``LEFT``：向左转
   * ``RIGHT``：向右转
   * ``DOWN``：停止
   * ``C``：在第三人称视角和第一人称视角之间切换
   * ``ESC``：退出当前第三人称视角

   如果在选择类人角色时误点到了角色主体之外，控制台会打印一条指示错误的
   信息，例如 ``The selected prim was not a H1 robot`` 或
   ``Multiple prims are selected. Please only select one!``。


-  生成不同的灵巧手并指令其张开和闭合：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            ./isaaclab.sh -p scripts/demos/hands.py

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            isaaclab.bat -p scripts\demos\hands.py

   .. image:: ../_static/demos/hands.jpg
      :width: 100%
      :alt: Isaac Lab 中的灵巧手


-  定义多个可用于可视化的标记（marker）：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            ./isaaclab.sh -p scripts/demos/markers.py

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            isaaclab.bat -p scripts\demos\markers.py

   .. image:: ../_static/demos/markers.jpg
      :width: 100%
      :alt: Isaac Lab 中的标记


-  使用交互式场景（interactive scene）并在各个环境中生成不同的资产：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            ./isaaclab.sh -p scripts/demos/multi_asset.py

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            isaaclab.bat -p scripts\demos\multi_asset.py

   .. image:: ../_static/demos/multi_asset.jpg
      :width: 100%
      :alt: 通过相同仿真句柄管理的多个资产


-  使用 RigidObjectCollection 的生成与查看操作来演示装箱（bin-packing）示例：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            ./isaaclab.sh -p scripts/demos/bin_packing.py

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            isaaclab.bat -p scripts\demos\bin_packing.py

   .. image:: ../_static/demos/bin_packing.jpg
      :width: 100%
      :alt: 使用 MultiAssetSpawner 和 RigidObjectCollection 组合在每个 env_id 中生成随机数量的随机资产



-  使用交互式场景并生成一个简单的并联机器人进行抓取和放置：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            ./isaaclab.sh -p scripts/demos/pick_and_place.py

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            isaaclab.bat -p scripts\demos\pick_and_place.py

   .. image:: ../_static/demos/pick_and_place.jpg
      :width: 100%
      :alt: 用户控制的并联机器人抓取与放置

   这是一个可以使用鼠标和键盘运行的交互式演示。
   你的目标是抓起紫色立方体并将其放到红色球体上。
   使用以下按键与仿真进行交互：

   * 按住 ``A`` 键，让夹爪跟踪立方体的位置。
   * 按住 ``D`` 键，让夹爪跟踪目标位置
   * 按 ``W`` 或 ``S`` 键，分别向上或向下移动龙门架
   * 按 ``Q`` 或 ``E`` 键，分别张开或闭合夹爪



-  使用带力反馈的 Haply 触觉设备遥操作 Franka Panda 机器人：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            ./isaaclab.sh -p scripts/demos/haply_teleoperation.py --websocket_uri ws://localhost:10001 --pos_sensitivity 1.65

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            isaaclab.bat -p scripts\demos\haply_teleoperation.py --websocket_uri ws://localhost:10001 --pos_sensitivity 1.65

   .. image:: ../_static/demos/haply_teleop_franka.jpg
      :width: 100%
      :alt: 带力反馈的 Haply 遥操作

   此演示需要 Haply Inverse3 和 VerseGrip 设备。
   演示的目标是抓起立方体，或使用末端执行器触碰它。
   Haply 设备提供：

   * 三维位置跟踪，用于控制末端执行器
   * 方向性力反馈，用于感知接触
   * 按键输入，用于控制夹爪和末端执行器的旋转

   详细的设置说明请参见 :ref:`haply-teleoperation`。



-  创建并生成具有不同配置的程序化地形：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            ./isaaclab.sh -p scripts/demos/procedural_terrain.py

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            isaaclab.bat -p scripts\demos\procedural_terrain.py

   .. image:: ../_static/demos/procedural_terrain.jpg
      :width: 100%
      :alt: Isaac Lab 中的程序化地形



-  在默认环境中生成一架四旋翼无人机：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            ./isaaclab.sh -p scripts/demos/quadcopter.py

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            isaaclab.bat -p scripts\demos\quadcopter.py

   .. image:: ../_static/demos/quadcopter.jpg
      :width: 100%
      :alt: Isaac Lab 中的四旋翼无人机


-  生成不同的四足机器人，并使用位置指令让机器人站立：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            ./isaaclab.sh -p scripts/demos/quadrupeds.py

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            isaaclab.bat -p scripts\demos\quadrupeds.py

   .. image:: ../_static/demos/quadrupeds.jpg
      :width: 100%
      :alt: Isaac Lab 中的四足机器人


-  生成一个使用 Warp 内核进行光线投射的多网格光线投射传感器（ray caster）

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            ./isaaclab.sh -p scripts/demos/sensors/multi_mesh_raycaster.py --num_envs 16 --asset_type objects

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            isaaclab.bat -p scripts\demos\sensors\multi_mesh_raycaster.py --num_envs 16 --asset_type objects

   .. image:: ../_static/demos/multi-mesh-raycast.jpg
      :width: 100%
      :alt: Isaac Lab 中的多网格光线投射传感器
