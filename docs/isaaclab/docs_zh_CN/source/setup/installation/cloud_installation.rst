云端部署
================

借助
`Isaac Automator <https://github.com/isaac-sim/IsaacAutomator>`__，
Isaac Lab 可以在各种云基础设施中运行。

Isaac Automator 支持将 Isaac Sim 和 Isaac Lab 快速部署到
公有云上（目前支持 AWS、GCP、Azure 和阿里云）。
其结果是一台完全配置好的远程桌面云工作站，可以在几分钟内、以较低成本
用于 Isaac Lab 的开发和测试。Isaac Automator 支持多种 GPU 实例，并具备停止-启动功能
以节省云成本，还提供多种辅助工作流的工具
（例如上传和下载数据、自动运行、部署管理等）。


系统要求
-------------------

Isaac Automator 要求系统上预先安装 ``docker``。

* 要安装 Docker，请在 `Docker website`_ 上按照适用于你操作系统的说明操作。与 Isaac Automator 配合使用
  要求 Docker Engine 最低版本为 26.0.0，Docker
  Compose 最低版本为 2.25.0。
* 请在 `post-installation steps`_ 页面上完成 Docker 的安装后步骤。
  这些步骤让你无需使用 ``sudo`` 即可运行 Docker。


安装 Isaac Automator
--------------------------

要获取最新、最完整的安装说明，请参阅
`Isaac Automator <https://github.com/isaac-sim/IsaacAutomator?tab=readme-ov-file#installation>`__。

要使用 Isaac Automator，首先克隆仓库：

.. tab-set::

   .. tab-item:: HTTPS

      .. code-block:: bash

         git clone https://github.com/isaac-sim/IsaacAutomator.git

   .. tab-item:: SSH

      .. code-block:: bash

         git clone git@github.com:isaac-sim/IsaacAutomator.git


Isaac Automator 需要获取一个 NGC API 密钥。

* 通过加入 NVIDIA Developer Program 的凭证，获得对 `Isaac Sim container`_ 的访问权限。
* 生成你的 `NGC API key`_，以便从 NVIDIA GPU Cloud（NGC）访问受锁定的容器镜像。

  * 如果你还没有 NGC 账户，此步骤要求你先创建一个。
  * 生成 API 密钥后，你需要从终端
    登录 NGC。

    .. code:: bash

         docker login nvcr.io

  * 用户名请原样输入 ``$oauthtoken``。这是一个特殊用户名，用于
    向 NGC 进行身份验证。

    .. code:: text

        Username: $oauthtoken
        Password: <Your NGC API Key>


构建容器
----------------------

要运行 Isaac Automator，首先构建 Isaac Automator 容器：

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code-block:: bash

         ./build

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code-block:: batch

         docker build --platform linux/x86_64 -t isa .


这会构建 Isaac Automator 容器，并将其标记为 ``isa``。


运行 Automator 命令
------------------------------

首先，进入 Automator 容器：

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code-block:: bash

         ./run

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code-block:: batch

         docker run --platform linux/x86_64 -it --rm -v .:/app isa bash

接下来，针对你偏好的云平台运行部署脚本：

.. note::

   ``--isaaclab`` 标志用于指定要部署的 Isaac Lab 版本。
   ``v2.3.0`` 标签是 Isaac Lab 的最新发布版本。

.. tab-set::
   :sync-group: cloud

   .. tab-item:: AWS
      :sync: aws

      .. code-block:: bash

         ./deploy-aws --isaaclab v2.3.2

   .. tab-item:: Azure
      :sync: azure

      .. code-block:: bash

         ./deploy-azure --isaaclab v2.3.2

   .. tab-item:: GCP
      :sync: gcp

      .. code-block:: bash

         ./deploy-gcp --isaaclab v2.3.2

   .. tab-item:: Alibaba Cloud
      :sync: alicloud

      .. code-block:: bash

         ./deploy-alicloud --isaaclab v2.3.2

按照提示输入有关环境设置和凭证的信息。
成功后，连接到云实例的说明将显示在终端中。部署好的 Isaac Sim 实例可以通过以下方式访问：

- SSH
- noVCN（基于浏览器的 VNC 客户端）
- NoMachine（远程桌面客户端）

请在部署命令输出的末尾查找连接说明。此外，这些信息会保存在
``state/<deployment-name>/info.txt`` 文件中。

有关每种云平台所需的凭证和设置的详细信息，请访问
`Isaac Automator <https://github.com/isaac-sim/IsaacAutomator?tab=readme-ov-file#deploying-isaac-sim>`__
页面获取更多说明。


在云端运行 Isaac Lab
------------------------------

连接到云实例后，桌面上会有一个显示 ``isaaclab.sh`` 的图标。
启动 ``isaaclab.sh`` 可执行文件，它会打开一个新的终端。在该终端中，
Isaac Lab 命令的执行方式与本地运行完全相同。

例如：

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code-block:: bash

         ./isaaclab.sh -p scripts/reinforcement_learning/rl_games/train.py --task=Isaac-Cartpole-v0

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code-block:: batch

         isaaclab.bat -p scripts/reinforcement_learning/rl_games/train.py --task=Isaac-Cartpole-v0


销毁部署
-----------------------

为了节省成本，可以在不使用时销毁部署。
这可以在 Automator 容器内完成。

使用上一节介绍的命令进入 Automator 容器：

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code-block:: bash

         ./run

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code-block:: batch

         docker run --platform linux/x86_64 -it --rm -v .:/app isa bash


要销毁一个部署，请在容器内运行以下命令：

.. code:: bash

   ./destroy <deployment-name>


.. _`Docker website`: https://docs.docker.com/desktop/install/linux-install/
.. _`post-installation steps`: https://docs.docker.com/engine/install/linux-postinstall/
.. _`Isaac Sim container`: https://catalog.ngc.nvidia.com/orgs/nvidia/containers/isaac-sim
.. _`NGC API key`: https://docs.nvidia.com/ngc/gpu-cloud/ngc-user-guide/index.html#generating-api-key
