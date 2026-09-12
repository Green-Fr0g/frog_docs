.. _isaaclab-installation-root:

本地安装
==================

.. image:: https://img.shields.io/badge/IsaacSim-5.1.0-silver.svg
   :target: https://developer.nvidia.com/isaac-sim
   :alt: IsaacSim 5.1.0

.. image:: https://img.shields.io/badge/python-3.11-blue.svg
   :target: https://www.python.org/downloads/release/python-31013/
   :alt: Python 3.11

.. image:: https://img.shields.io/badge/platform-linux--64-orange.svg
   :target: https://releases.ubuntu.com/22.04/
   :alt: Ubuntu 22.04

.. image:: https://img.shields.io/badge/platform-windows--64-orange.svg
   :target: https://www.microsoft.com/en-ca/windows/windows-11
   :alt: Windows 11


Isaac Lab 支持 Windows 和 Linux 安装。由于它构建在 Isaac Sim 之上，因此在安装 Isaac Lab 之前必须先安装
Isaac Sim。本指南介绍了 Isaac Sim 和 Isaac Lab 的推荐安装方法。

.. caution::

   我们已不再支持 Isaac Sim 4.2.0 及更早的版本。我们建议使用最新的 Isaac Sim 5.1.0 版本，
   以获得最新的特性和改进。

   更多信息请参阅
   `Isaac Sim release notes <https://docs.isaacsim.omniverse.nvidia.com/latest/overview/release_notes.html#>`__。


系统要求
-------------------

一般要求
~~~~~~~~~~~~~~~~~~~~

详细要求请参阅
`Isaac Sim system requirements <https://docs.isaacsim.omniverse.nvidia.com/latest/installation/requirements.html>`_。
基本要求如下：

- **操作系统：** Ubuntu 22.04（Linux x64）或 Windows 11（x64）
- **内存：** 32 GB 或更多
- **GPU 显存：** 16 GB 或更多（渲染工作流可能需要额外显存）

**Isaac Sim 是针对特定 Python 版本构建的**，因此在安装 Isaac Lab 时必须使用相同的 Python 版本。
所需的 Python 版本如下：

- 对于 Isaac Sim 5.X，所需的 Python 版本为 3.11。
- 对于 Isaac Sim 4.X，所需的 Python 版本为 3.10。


驱动要求
~~~~~~~~~~~~~~~~~~~

除 `Omniverse Technical Requirements <https://docs.omniverse.nvidia.com/materials-and-rendering/latest/common/technical-requirements.html>`_
上推荐的驱动外，其他驱动也许可以工作，但尚未通过所有 Omniverse 测试的验证。

- 使用 **最新的 NVIDIA production branch 驱动**。
- 在 Linux 上，推荐使用 ``580.65.06`` 或更高版本，尤其是在升级到
  **Ubuntu 22.04.5（内核 6.8.0-48-generic）** 或更新版本时。
- 在 Spark 上，推荐使用 ``580.95.05`` 版本。
- 在 Windows 上，推荐使用 ``580.88`` 版本。
- 如果你使用的是新 GPU 或遇到驱动问题，请使用 ``.run`` 安装程序从
  `Unix Driver Archive <https://www.nvidia.com/en-us/drivers/unix/>`_
  安装最新的 production branch 驱动。

DGX Spark：细节与限制
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

DGX Spark 是一台采用 aarch64 架构的独立机器学习设备。因此，Isaac Lab 的部分特性目前不支持在
DGX Spark 上使用。最值得注意的是，该架构 *要求* CUDA ≥ 13，因而需要 cu13 或更新版本的 PyTorch 构建。
与 Isaac Lab 相关的其他显著限制包括……

#. `SkillGen <https://isaac-sim.github.io/IsaacLab/main/source/overview/imitation-learning/skillgen.html>`_ 无法开箱即用。这是因为
   cuRobo 会构建原生 CUDA/C++ 扩展，需要特定的工具链和库版本，而这些尚未经过与 DGX Spark 配合使用的验证。

#. `OpenXR <https://isaac-sim.github.io/IsaacLab/v2.3.2/source/api/lab/isaaclab.devices.html#openxr>`_ 等扩展现实（XR）遥操作工具不受支持。这是由于
   编码性能限制尚未得到充分研究。

#. 基于 `JAX <https://docs.jax.dev/en/latest/notebooks/thinking_in_jax.html>`_ 的 SKRL 训练尚未在 DGX Spark 上的 Isaac Lab 中进行过明确验证或测试。
   JAX 仅为 x86_64 的 Linux 提供预构建的 CUDA wheel，因此在 aarch64 系统（例如 DGX Spark）上默认只能在 CPU 上运行。
   GPU 支持需要从源码构建 JAX，而这尚未在 Isaac Lab 中经过验证。

#. Livestream 和 Hub Workstation Cache 不支持在 DGX Spark 上使用。

#. :ref:`Running Cosmos Transfer1 <running-cosmos>` 目前不支持在 DGX Spark 上运行。

故障排除
~~~~~~~~~~~~~~~

如需解决 Linux 下的安装问题，请参阅
`Linux Troubleshooting <https://docs.omniverse.nvidia.com/dev-guide/latest/linux-troubleshooting.html>`_。

你可以使用 `Isaac Sim Compatibility Checker <https://docs.isaacsim.omniverse.nvidia.com/latest/installation/install_workstation.html#isaac-sim-compatibility-checker>`_
自动检查你的系统是否满足运行 Isaac Sim 的上述要求。

快速上手（推荐）
-------------------------

对大多数用户而言，安装 Isaac Lab 最简单、最快捷的方式是按照
:doc:`pip_installation` 指南操作。

该方法通过 pip 安装 Isaac Sim，并通过源码安装 Isaac Lab。
如果你刚开始接触 Isaac Lab，请从这里开始。


选择安装方法
-------------------------------

不同的工作流需要不同的安装方法。
请使用下表来做出决定：

+-------------------+------------------------------+------------------------------+---------------------------+------------+
| 方法              | Isaac Sim                    | Isaac Lab                    | 最适合                    | 难度       |
+===================+==============================+==============================+===========================+============+
| **推荐**          | |:package:| pip install      | |:floppy_disk:| 源码（git）  | 初学者、常规使用          | 简单       |
+-------------------+------------------------------+------------------------------+---------------------------+------------+
| 二进制 + 源码     | |:inbox_tray:| 二进制包      | |:floppy_disk:| 源码（git）  | 偏好二进制安装            | 简单       |
|                   | 下载                         |                              | Isaac Sim 的用户          |            |
+-------------------+------------------------------+------------------------------+---------------------------+------------+
| 全源码构建        | |:floppy_disk:| 源码（git）  | |:floppy_disk:| 源码（git）  | 同时修改两者的开发者      | 进阶       |
+-------------------+------------------------------+------------------------------+---------------------------+------------+
| 仅 Pip            | |:package:| pip install      | |:package:| pip install      | 仅外部扩展                | 特殊情况   |
|                   |                              |                              | （无训练/示例）           |            |
+-------------------+------------------------------+------------------------------+---------------------------+------------+
| Docker            | |:whale:| Docker             | |:floppy_disk:| 源码（git）  | Docker 用户               | 进阶       |
+-------------------+------------------------------+------------------------------+---------------------------+------------+

后续步骤
----------

查看安装方法后，请继续阅读与你的工作流相匹配的指南：

- |:smiley:| :doc:`pip_installation`

  - 通过 pip 安装 Isaac Sim，并从源码安装 Isaac Lab。
  - 最适合初学者和大多数用户。

- :doc:`binaries_installation`

  - 从二进制包（官网下载）安装 Isaac Sim。
  - 从源码安装 Isaac Lab。
  - 如果你不想通过 pip 安装 Isaac Sim（例如在 Ubuntu 20.04 上），请选择此项。

- :doc:`source_installation`

  - 从源码构建 Isaac Sim。
  - 从源码安装 Isaac Lab。
  - 仅在你计划修改 Isaac Sim 本身时推荐使用。

- :doc:`isaaclab_pip_installation`

  - 将 Isaac Sim 和 Isaac Lab 作为 pip 包安装。
  - 最适合使用自定义运行脚本构建 **外部扩展** 的高级用户。
  - 注意：此方法 **不** 包含训练或示例脚本。

- :ref:`container-deployment`

  - 在 Docker 容器中安装 Isaac Sim 和 Isaac Lab。
  - 最适合希望在容器化环境中使用 Isaac Lab 的用户。


资产缓存
-------------

Isaac Lab 的资产托管在 **AWS S3 云存储** 上。加载时间会因你的 **网络连接** 和 **地理位置** 而异，
某些情况下，每次运行时资产可能需要几分钟才能加载完成。为了提升性能或支持 **离线工作流**，
我们建议启用 **资产缓存**。

- 缓存的资产会存储在本地，减少重复下载。
- 如果你的网络连接较慢或不稳定，或者部署环境处于离线状态，这一点尤其有用。

请按照 :doc:`asset_caching` 中的步骤启用资产缓存，加快你的工作流。


.. toctree::
   :maxdepth: 1
   :hidden:

   pip_installation
   binaries_installation
   source_installation
   isaaclab_pip_installation
   asset_caching
