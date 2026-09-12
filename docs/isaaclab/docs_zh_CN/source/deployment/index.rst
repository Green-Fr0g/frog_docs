.. _container-deployment:

容器部署
====================

Docker 是一种用于创建容器的工具，容器是可以用来运行应用程序的隔离环境。它们有助于确保
应用程序能够在任何安装了 Docker 的机器上运行，而与宿主机的操作系统或已安装的库无关。

我们提供了一个 Dockerfile 和 docker-compose.yaml 文件，可用于构建一个包含 Isaac Lab 及其
全部依赖的 Docker 镜像。随后即可使用该镜像在容器中运行 Isaac Lab。该 Dockerfile 基于
NVIDIA 提供的 Isaac Sim 镜像，其中包含 Omniverse 应用程序启动器和 Isaac Sim 应用程序。
Dockerfile 会在此镜像之上安装 Isaac Lab 及其依赖。

克隆仓库
----------------------

在构建容器之前，请先克隆 Isaac Lab 仓库（如果尚未克隆）：

.. tab-set::

   .. tab-item:: SSH

      .. code:: bash

         git clone git@github.com:isaac-sim/IsaacLab.git

   .. tab-item:: HTTPS

      .. code:: bash

         git clone https://github.com/isaac-sim/IsaacLab.git

后续步骤
----------

克隆完成后，你可以选择符合自身需求的部署工作流：

- :doc:`docker`

  - 了解如何在 Docker 容器中构建、配置和运行 Isaac Lab。
  - 介绍仓库的 ``docker/`` 目录结构、 ``container.py`` 辅助脚本、挂载的卷、
    镜像扩展（如 ROS 2）以及可选的 CloudXR 串流支持。
  - 涵盖如何运行来自 NVIDIA NGC 的预构建 Isaac Lab 容器以进行无头训练。

- :doc:`run_docker_example`

  - 了解如何在 Isaac Lab Docker 容器内运行开发工作流。
  - 演示如何构建容器、进入容器、执行示例 Python 脚本（`log_time.py` ）以及
    使用挂载的卷获取日志。
  - 重点介绍用于实时代码编辑的绑定挂载目录，并说明如何在保留镜像和产物的同时
    停止或移除容器。

- :doc:`cluster`

  - 了解如何在高性能计算（HPC）集群上运行 Isaac Lab。
  - 介绍如何将 Docker 镜像导出为 Singularity（Apptainer）镜像、配置集群专属参数，
    以及使用常见的工作负载管理器（SLURM 或 PBS）提交作业。
  - 包含针对 ETH Zurich 的 Euler 集群和 IIT Genoa 的 Franklin 集群验证过的工作流，
    并提供适配其他环境的说明。

- :doc:`cloudxr_teleoperation_cluster`

  - 在 Kubernetes 集群上部署 Isaac Lab 的 CloudXR 遥操作。
  - 涵盖系统需求、软件依赖以及包括 RBAC 权限在内的准备步骤。
  - 演示如何安装并验证 Helm chart、运行 pod 以及卸载。


.. toctree::
   :maxdepth: 1
   :hidden:

   docker
   run_docker_example
   cluster
   cloudxr_teleoperation_cluster
