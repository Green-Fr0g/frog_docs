.. _deployment-cluster:


集群指南
========

集群是加速学习算法训练与评估的好方法。虽然 Isaac Lab Docker 镜像可以用于在集群上运行作业，但许多集群只支持 singularity 镜像。这是因为 `singularity`_ 专为共享多用户系统和高性能计算（HPC）环境的易用性而设计。它运行容器不需要 root 权限，并且可以运行用户自定义的容器。

Singularity 兼容所有 Docker 镜像。在本节中，我们将介绍如何将 Isaac Lab Docker 镜像转换为 singularity 镜像，并用它向集群提交作业。

.. attention::

    不同机构的集群配置各不相同。以下说明已在 `ETH Zurich Euler`_ 集群（使用 SLURM 工作负载管理器）和 IIT Genoa Franklin 集群（使用 PBS 工作负载管理器）上测试通过。

    这些说明可能需要针对其他集群进行调整。如果你已成功将说明适配到其他集群，请考虑为文档做出贡献。


设置说明
--------

要将 Docker 镜像导出为 singularity 镜像，需要 `apptainer`_。``apptainer`` 的安装流程详见其 `documentation`_。为方便起见，这里概述本地安装的步骤：

.. code:: bash

    sudo apt update
    sudo apt install -y software-properties-common
    sudo add-apt-repository -y ppa:apptainer/ppa
    sudo apt update
    sudo apt install -y apptainer

为简单起见，我们建议在本地开发机与集群之间建立 SSH 连接。这样的连接可以简化文件传输，并避免多次请求输入集群用户密码。

.. attention::
  该工作流已在以下版本组合下测试通过：

  - ``apptainer version 1.2.5-1.el7`` 和 ``docker version 24.0.7``
  - ``apptainer version 1.3.4`` 和 ``docker version 27.3.1``

  如遇问题，请尝试切换到这些版本。


配置集群参数
~~~~~~~~~~~~

首先，你需要在 ``docker/cluster/.env.cluster`` 文件中配置集群特有的参数。以下是需要配置的参数说明：

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - 参数
     - 说明
   * - CLUSTER_JOB_SCHEDULER
     - 你的集群使用的作业调度器/工作负载管理器。目前我们支持 'SLURM' 和 'PBS' 工作负载管理器。
   * - CLUSTER_ISAAC_SIM_CACHE_DIR
     - 集群上存储 Isaac Sim 缓存的目录。该目录必须以 ``docker-isaac-sim`` 结尾。它会被复制到计算节点并挂载到 singularity 容器中。这应能加快仿真的启动速度。
   * - CLUSTER_ISAACLAB_DIR
     - 集群上存储 Isaac Lab 日志的目录。该目录必须以 ``isaaclab`` 结尾。它会被复制到计算节点并挂载到 singularity 容器中。提交作业时，最新的本地改动会被复制到集群上一个新目录，目录名格式为 ``${CLUSTER_ISAACLAB_DIR}_${datetime}``，其中包含作业提交的日期和时间。这样便可以同时运行多个使用不同代码版本的作业。
   * - CLUSTER_LOGIN
     - 集群的登录信息。通常为用户名和集群名，例如 ``your_user@euler.ethz.ch``。
   * - CLUSTER_SIF_PATH
     - 集群上存储 singularity 镜像的路径。该镜像会被复制到计算节点，但在提交作业时不会重新上传到集群。
   * - REMOVE_CODE_COPY_AFTER_JOB
     - 作业结束后是否删除所复制的代码。作业产生的日志不会被删除，因为它们保存在永久的 ``CLUSTER_ISAACLAB_DIR`` 下。该功能有助于节省集群上的磁盘空间。如果设为 ``true``，将删除代码副本。
   * - CLUSTER_PYTHON_EXECUTABLE
     - Isaac Lab 内部要在所提交作业中执行的 Python 可执行文件的路径。

提交 ``job`` 时，还会使用 ``docker/.env.base`` 中定义的变量，不过这些变量默认应该是正确的。

导出为 singularity 镜像
~~~~~~~~~~~~~~~~~~~~~~~

接下来，我们需要将 Docker 镜像导出为 singularity 镜像并上传到集群。该步骤只在首次提交作业或 Docker 镜像更新时（例如由于 Isaac Sim 版本升级或项目新增依赖）才需要执行。

要导出为 singularity 镜像，请执行以下命令：

.. code:: bash

    ./docker/cluster/cluster_interface.sh push [profile]

该命令会在 ``docker/exports`` 目录下创建 singularity 镜像，并将其上传到集群上指定的位置。它要求你之前已经通过 ``container.py`` 接口构建过镜像。请注意，创建 singularity 镜像可能需要一段时间。``[profile]`` 是可选参数，用于指定要使用的容器 profile。如果未指定 profile，将使用默认的 ``base`` profile。

.. note::
  默认情况下，singularity 镜像通过向 ``apptainer build`` 命令传入 ``--fakeroot`` 标志以无 root 权限的方式创建。如果镜像创建失败，可以尝试在 ``docker/cluster/cluster_interface.sh`` 中移除该标志，以 root 权限创建。


定义作业参数
------------

作业参数需要根据你的集群所使用的作业调度器来定义。你只需更新所用调度器对应的脚本。

- 对于 SLURM，更新 ``docker/cluster/submit_job_slurm.sh`` 中的参数。
- 对于 PBS，更新 ``docker/cluster/submit_job_pbs.sh`` 中的参数。

SLURM
~~~~~

作业参数定义在 ``docker/cluster/submit_job_slurm.sh`` 中。典型的 SLURM 操作需要指定 CPU 和 GPU 数量、内存以及时间限制。更多信息请查阅 `SLURM documentation`_。

默认配置如下：

.. literalinclude:: ../../../docker/cluster/submit_job_slurm.sh
  :language: bash
  :lines: 12-19
  :linenos:
  :lineno-start: 12

集群的一项基本要求是计算节点必须始终能够访问互联网。这是从 Nucleus 服务器加载资产所必需的。对于某些集群架构，必须加载额外的模块才能访问互联网。

例如，在 ETH Zurich Euler 集群上，需要加载 ``eth_proxy`` 模块。可以通过在 ``submit_job_slurm.sh`` 脚本中添加以下行来实现：

.. literalinclude:: ../../../docker/cluster/submit_job_slurm.sh
  :language: bash
  :lines: 3-5
  :linenos:
  :lineno-start: 3

PBS
~~~

作业参数定义在 ``docker/cluster/submit_job_pbs.sh`` 中。典型的 PBS 操作需要指定 CPU 和 GPU 数量以及时间限制。更多信息请查阅 `PBS Official Site`_。

默认配置如下：

.. literalinclude:: ../../../docker/cluster/submit_job_pbs.sh
  :language: bash
  :lines: 11-17
  :linenos:
  :lineno-start: 11


提交作业
--------

要在集群上提交作业，可以使用以下命令：

.. code:: bash

    ./docker/cluster/cluster_interface.sh job [profile] "argument1" "argument2" ...

该命令会将你代码中的最新改动复制到集群并提交一个作业。请确保你的 Python 可执行文件的输出存储在 ``isaaclab/logs`` 下，因为该目录会在计算节点与 ``CLUSTER_ISAACLAB_DIR`` 之间同步。

``[profile]`` 是可选参数，用于指定使用哪个与容器 profile 对应的 singularity 镜像。如果未指定 profile，将使用默认的 ``base`` profile。profile 必须紧跟在 ``job`` 命令之后定义。其余所有参数都会传递给 Python 可执行文件。如果未定义 profile，则所有参数都会传递给 Python 可执行文件。

训练参数会传递给 Python 可执行文件。举例来说，标准的 ANYmal 粗糙地形运动训练可以用以下命令执行：

.. code:: bash

    ./docker/cluster/cluster_interface.sh job --task Isaac-Velocity-Rough-Anymal-C-v0 --headless --video --enable_cameras

上述命令还会渲染训练过程的视频并将其存储在 ``isaaclab/logs`` 目录下。

.. _Singularity: https://docs.sylabs.io/guides/2.6/user-guide/index.html
.. _ETH Zurich Euler: https://www.gdc-docs.ethz.ch/EulerManual/site/overview/
.. _PBS Official Site: https://openpbs.org/
.. _apptainer: https://apptainer.org/
.. _documentation: https://www.apptainer.org/docs/admin/main/installation.html#install-ubuntu-packages
.. _SLURM documentation: https://www.slurm.schedmd.com/sbatch.html
