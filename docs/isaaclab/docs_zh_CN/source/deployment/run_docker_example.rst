使用 Docker 运行示例
====================

在 Isaac Lab 仓库的根目录下，``docker`` 目录包含所有与 Docker 相关的文件。其中包括 Docker 使用的三个文件（**Dockerfile**、**docker-compose.yaml**、**.env**），以及我们用于与它们交互的附加脚本 **container.py**。

在本教程中，我们将学习如何使用 Isaac Lab Docker 容器进行开发。有关 Docker 设置的详细说明（包括安装以及获取 Isaac Sim 镜像的访问权限），请参阅 :ref:`deployment-docker`。有关 Docker 本身的一般性介绍，请参阅其 `官方文档 <https://docs.docker.com/get-started/overview/>`_。


构建容器
~~~~~~~~

要从 Isaac Lab 仓库根目录构建 Isaac Lab 容器，我们运行以下命令：


.. code-block:: console

   python docker/container.py start


终端将首先拉取基础的 IsaacSim 镜像，在其上构建 Isaac Lab 镜像的附加层，然后运行 Isaac Lab 容器。首次构建需要几分钟时间，但后续运行会更快，因为 Docker 的缓存机制避免了重复工作。如果我们在终端运行 ``docker container ls`` 命令，输出将列出系统中正在运行的容器。如果一切设置正确，应会出现一个 ``NAME`` 为 **isaac-lab-base** 的容器，如下所示：


.. code-block:: console

   CONTAINER ID   IMAGE               COMMAND   CREATED           STATUS         PORTS     NAMES
   483d1d5e2def   isaac-lab-base      "bash"    30 seconds ago   Up 30 seconds             isaac-lab-base


容器启动并运行后，我们可以在终端中进入该容器。

.. code-block:: console

   python docker/container.py enter


进入 Isaac Lab 容器后，我们以超级用户 ``root`` 的身份处于终端中。该环境中包含 Isaac Lab 仓库的一份副本，同时还能访问 Isaac Sim 的目录和库。我们可以使用 ``root`` 的 **.bashrc** 中预置的若干便捷别名在该环境中运行实验。例如，我们通过别名 ``isaaclab`` 使 **isaaclab.sh** 脚本可以在任意位置使用。

此外，容器中还从宿主机 `bind mounted`_ 了 ``IsaacLab/source`` 目录。这意味着如果我们从宿主机上的编辑器修改该目录下的文件，改动会立即反映到容器内，无需重新构建 Docker 镜像。

现在我们将在容器内运行一个示例脚本，演示如何从 Isaac Lab Docker 容器中提取产物。

代码
~~~~

本教程对应 ``IsaacLab/scripts/tutorials/00_sim`` 目录中的 ``log_time.py`` 脚本。

.. dropdown:: log_time.py 的代码
   :icon: code

   .. literalinclude:: ../../../scripts/tutorials/00_sim/log_time.py
      :language: python
      :emphasize-lines: 46-55, 72-79
      :linenos:


代码讲解
~~~~~~~~

Isaac Lab Docker 容器配有多个 `volumes`_，用于在宿主机与容器之间实现持久化存储。其中一个卷是 ``/workspace/isaaclab/logs`` 目录。``log_time.py`` 脚本将该目录指定为 ``log.txt`` 的写入位置：

.. literalinclude:: ../../../scripts/tutorials/00_sim/log_time.py
   :language: python
   :start-at: # Specify that the logs must be in logs/docker_tutorial
   :end-at: print(f"[INFO] Logging experiment to directory: {log_dir_path}")


正如注释所述，:func:`os.path.abspath()` 会自动加上 ``/workspace/isaaclab`` 前缀，因为在 Docker 容器中，所有 Python 执行都是通过 ``/workspace/isaaclab/isaaclab.sh`` 完成的。输出将是一个 ``log.txt`` 文件，在每个仿真步骤将 ``sim_time`` 写入新的一行：

.. literalinclude:: ../../../scripts/tutorials/00_sim/log_time.py
   :language: python
   :start-at: # Prepare to count sim_time
   :end-at: sim_time += sim_dt


执行脚本
~~~~~~~~

我们将执行该脚本来生成日志，并在执行时加上 ``--headless`` 标志以避免启动 GUI：

.. code-block:: bash

  isaaclab -p scripts/tutorials/00_sim/log_time.py --headless


现在 ``log.txt`` 已生成于 ``/workspace/isaaclab/logs/docker_tutorial``。如果我们输入 ``exit`` 退出容器，将返回宿主机终端环境中的 ``IsaacLab/docker`` 目录。然后我们可以输入以下命令，从 Docker 容器中取回日志并放到宿主机上：

.. code-block:: console

  ./container.py copy


我们将看到终端输出报告了从容器中取回的产物。如果导航到 ``/isaaclab/docker/artifacts/logs/docker_tutorial``，就会看到上述脚本生成的 ``log.txt`` 文件的副本。

``artifacts`` 下的每个目录都对应映射到容器内目录的 Docker `volumes`_，``container.py copy`` 命令会将它们从这些 `volumes`_ 复制到这些目录中。

我们可以再次运行 ``container.py enter`` 回到 Isaac Lab Docker 终端环境，但日志已经取回，我们想去查看它们。可以使用以下命令停止 Isaac Lab Docker 容器：

.. code-block:: console

  ./container.py stop


这将关闭 Docker 的 Isaac Lab 容器。镜像会保留并可供后续使用，任何 `volumes`_ 中的内容同样会保留。如果我们希望释放该镜像占用的磁盘空间（约 20.1GB），并且不介意下次运行 ``./container.py start`` 时重新经历构建过程，可以输入以下命令删除 **isaac-lab-base** 镜像：

.. code-block:: console

  docker image rm isaac-lab-base

随后再运行 ``docker image ls`` 将显示标记为 **isaac-lab-base** 的镜像已不存在。如果希望释放更多空间，可以对底层 NVIDIA 容器重复上述过程。若需要更强大的 Docker 资源清理方法，请参阅 `docker prune`_ 命令的文档。


.. _volumes: https://docs.docker.com/storage/volumes/
.. _bind mounted: https://docs.docker.com/storage/bind-mounts/
.. _docker prune: https://docs.docker.com/config/pruning/
