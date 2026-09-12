.. _haply-teleoperation:

设置 Haply 遥操作
===============================

.. currentmodule:: isaaclab

`Haply Devices`_ 提供的触觉设备能够以方向性力反馈实现直观的机器人遥操作。
Haply Inverse3 与 VerseGrip 搭配使用，可以构成一个具备力反馈能力的末端执行器控制系统。

Isaac Lab 支持 Haply 设备，用于需要精确空间控制和触觉反馈的遥操作工作流。这让操作者在操作任务中
能够感受到接触力，从而提升控制质量和任务表现。

本指南介绍如何在 Isaac Lab 中设置并使用 Haply 设备进行机器人遥操作。

.. _Haply Devices: https://haply.co/


概述
--------

将 Haply 与 Isaac Lab 结合使用涉及以下组件：

* **Isaac Lab** 仿真机器人环境，并将接触力串流回操作者

* **Haply Inverse3** 在操作者的工作空间中提供 3 自由度位置追踪和力反馈

* **Haply VerseGrip** 增加了姿态感知和用于夹爪控制的按键输入

* **Haply SDK** 管理 Isaac Lab 与 Haply 硬件之间的 WebSocket 通信

本指南将带您了解：

* :ref:`haply-system-requirements`
* :ref:`haply-installation`
* :ref:`haply-device-setup`
* :ref:`haply-running-demo`
* :ref:`haply-troubleshooting`


.. _haply-system-requirements:

系统要求
-------------------

硬件要求
~~~~~~~~~~~~~~~~~~~~~

* **Isaac Lab 工作站**

  * Ubuntu 22.04 或 Ubuntu 24.04
  * 200Hz 物理仿真的硬件要求：

    * CPU：8 核 Intel Core i7 或 AMD Ryzen 7（或更高）
    * 内存：32GB RAM（推荐 64GB）
    * GPU：RTX 3090 或更高

  * 网络：与 Haply 设备处于同一局域网，以便进行 WebSocket 通信

* **Haply 设备**

  * Haply Inverse3 - 用于位置追踪和力反馈的触觉设备
  * Haply VerseGrip - 用于姿态和按键输入的无线控制器
  * 两个设备都必须已开机并连接到 Haply SDK

软件要求
~~~~~~~~~~~~~~~~~~~~~

* Isaac Lab（请遵循 :ref:`安装指南 <isaaclab-installation-root>`）
* Haply SDK（由 Haply Robotics 提供）
* Python 3.10+
* ``websockets`` Python 包（随 Isaac Lab 自动安装）


.. _haply-installation:

安装
------------

1. 安装 Isaac Lab
~~~~~~~~~~~~~~~~~~~~

请按照 Isaac Lab :ref:`安装指南 <isaaclab-installation-root>` 设置您的环境。

``websockets`` 依赖已自动包含在 Isaac Lab 的依赖项中。

2. 安装 Haply SDK
~~~~~~~~~~~~~~~~~~~~

从 `Haply Devices`_ 网站下载 Haply SDK。
安装 SDK 软件并配置设备。

3. 验证安装
~~~~~~~~~~~~~~~~~~~~~~

测试 Haply Device Manager 是否能检测到您的 Haply 设备。
您应该会看到 Inverse3 和 VerseGrip 均显示为已连接。


.. _haply-device-setup:

设备设置
------------

1. 物理布置
~~~~~~~~~~~~~~~~~

* 将 Haply Inverse3 放置在稳定的表面上
* 确保 VerseGrip 已充电并完成配对
* 以舒适的姿势就位，使您能够触及 Inverse3 的工作空间
* 保持工作空间内没有障碍物

2. 启动 Haply SDK
~~~~~~~~~~~~~~~~~~

按照 Haply 的文档启动 Haply SDK。SDK 通常会：

* 在 ``localhost:10001`` 上运行一个 WebSocket 服务器
* 以 200Hz 的频率串流设备数据
* 显示两个设备的连接状态

3. 测试通信
~~~~~~~~~~~~~~~~~~~~~

您可以使用以下 Python 脚本测试 WebSocket 连接：

.. code:: python

   import asyncio
   import websockets
   import json

   async def test_haply():
       uri = "ws://localhost:10001"
       async with websockets.connect(uri) as ws:
           response = await ws.recv()
           data = json.loads(response)
           print("Inverse3:", data.get("inverse3", []))
           print("VerseGrip:", data.get("wireless_verse_grip", []))

   asyncio.run(test_haply())

您应该会看到来自 Inverse3 和 VerseGrip 的设备数据流。


.. _haply-running-demo:

运行演示
----------------

Haply 遥操作演示展示了使用 Franka Panda 机械臂进行带力反馈的机器人操作。

基本用法
~~~~~~~~~~~

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code:: bash

         # Ensure Haply SDK is running
         ./isaaclab.sh -p scripts/demos/haply_teleoperation.py --websocket_uri ws://localhost:10001 --pos_sensitivity 1.65

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code:: batch

         REM Ensure Haply SDK is running
         isaaclab.bat -p scripts\demos\haply_teleoperation.py --websocket_uri ws://localhost:10001 --pos_sensitivity 1.65

该演示将会：

1. 通过 WebSocket 连接到 Haply 设备
2. 在仿真中生成一个 Franka Panda 机器人和一个立方体
3. 将 Haply 的位置映射到机器人末端执行器位置
4. 将接触力串流回 Inverse3 以提供触觉反馈

控制方式
~~~~~~~~

* **移动 Inverse3**：控制机器人末端执行器位置
* **VerseGrip 按钮 A**：张开夹爪
* **VerseGrip 按钮 B**：闭合夹爪
* **VerseGrip 按钮 C**：将末端执行器旋转 60°

高级选项
~~~~~~~~~~~~~~~~

使用命令行参数自定义演示：

.. code:: bash

   # Use custom WebSocket URI
   ./isaaclab.sh -p scripts/demos/haply_teleoperation.py \
       --websocket_uri ws://192.168.1.100:10001

   # Adjust position sensitivity (default: 1.0)
   ./isaaclab.sh -p scripts/demos/haply_teleoperation.py \
        --websocket_uri ws://localhost:10001 \
        --pos_sensitivity 2.0

演示特性
~~~~~~~~~~~~~

* **工作空间映射**：将 Haply 工作空间映射到机器人可达空间，并带有安全限制
* **逆运动学**：逆运动学（IK）为期望的末端执行器位姿计算关节位置
* **力反馈**：来自末端执行器传感器的接触力被发送到 Inverse3 以提供触觉反馈


.. _haply-troubleshooting:

故障排查
---------------

没有触觉反馈
~~~~~~~~~~~~~~~~~~

**问题**：在 Inverse3 上感觉不到触觉反馈

解决方法：

* 确认 Inverse3 是 Haply SDK 中的活动设备
* 检查仿真中的接触力是否非零（尝试抓取立方体）
* 确保 ``limit_force`` 没有设置得过低（默认：2.0N）


后续步骤
----------

* **自定义演示**：修改工作空间映射或添加自定义按键行为
* **实现您自己的控制器**：在您自己的脚本中使用 :class:`~isaaclab.devices.HaplyDevice`

有关设备 API 的更多信息，请参阅 API 文档中的 :class:`~isaaclab.devices.HaplyDevice`。
