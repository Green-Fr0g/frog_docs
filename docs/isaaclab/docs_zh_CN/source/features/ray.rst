===========================
Ray 作业派发与调优
===========================

.. currentmodule:: isaaclab

Isaac Lab 支持 `Ray <https://docs.ray.io/en/latest/index.html>`_ ，用于简化多个训练任务（并行和串行）的派发以及超参数调优，本地和远程配置均可。

这个 `由社区独立贡献的分步演示视频 <https://youtu.be/z7MDgSga2Ho?feature=shared>`_
展示了本概述中介绍的 Ray 集成的部分核心功能。虽然自视频制作以来代码库可能存在一些
差异（例如文件名被缩短），但总体工作流是相同的。

.. attention::

  该功能为实验性功能，仅在 Linux 上经过测试。

.. warning::

  **安全提示** ：由于 Ray 存在相关安全风险，
  此工作流不适用于严格受控的网络环境之外的场合。Ray 集群只应部署在可信、
  隔离的网络中，并配备适当的访问控制和安全措施。



概述
--------

Ray 集成在以下方面非常有用。

- 以尽可能少的交互并行或按顺序派发多个训练任务。
- 调优超参数；支持并行或按顺序进行，并支持多 GPU 和/或多 GPU 节点。
- 以极小的开销在任何地方（云端和本地）使用相同的训练设置。
- 训练任务的资源隔离（resource-wrapped 任务）。

Ray 工作流的核心功能由两个主要脚本组成，用于编排
resource-wrapped 聚合任务和调优聚合任务。在 resource-wrapped 聚合任务中，每个子任务及其
资源需求都是手动定义的，从而实现资源隔离。
对于调优聚合任务，各个任务会根据超参数
扫描配置自动生成。

resource-wrapped 聚合任务和调优聚合任务都会将各个任务派发到指定的 Ray
集群，该集群利用自身的资源（例如单个工作站节点或多个节点），
通过 worker 并行和/或按顺序执行这些任务。

默认情况下，每个子任务 worker 会使用每个可用 GPU 节点上的所有 \
可用资源。可以通过为 resource-wrapped 任务指定 ``--num_workers`` 参数、或为调优任务指定
``--num_workers_per_node`` 参数来改变这一点，这对于在本地/虚拟多 GPU 机器上进行并行聚合
任务处理尤为关键。调优任务假定含有 GPU 的节点具有同构的资源配置。

以下三个文件包含了 Ray 集成的核心功能。

.. dropdown:: scripts/reinforcement_learning/ray/wrap_resources.py
  :icon: code

  .. literalinclude:: ../../../scripts/reinforcement_learning/ray/wrap_resources.py
    :language: python
    :emphasize-lines: 10-63

.. dropdown:: scripts/reinforcement_learning/ray/tuner.py
  :icon: code

  .. literalinclude:: ../../../scripts/reinforcement_learning/ray/tuner.py
    :language: python
    :emphasize-lines: 18-59

.. dropdown:: scripts/reinforcement_learning/ray/task_runner.py
  :icon: code

  .. literalinclude:: ../../../scripts/reinforcement_learning/ray/task_runner.py
    :language: python
    :emphasize-lines: 13-105

以下脚本可用于将聚合
任务提交到一个或多个 Ray 集群，可用于
在远程集群上运行任务，或运行具有异构
资源需求的并行任务。

.. dropdown:: scripts/reinforcement_learning/ray/submit_job.py
  :icon: code

  .. literalinclude:: ../../../scripts/reinforcement_learning/ray/submit_job.py
    :language: python
    :emphasize-lines: 13-61

以下脚本可用于提取 KubeRay 集群信息，以进行聚合任务提交。

.. dropdown:: scripts/reinforcement_learning/ray/grok_cluster_with_kubectl.py
  :icon: code

  .. literalinclude:: ../../../scripts/reinforcement_learning/ray/grok_cluster_with_kubectl.py
    :language: python
    :emphasize-lines: 14-26

以下脚本可用于在 Google GKE 上轻松创建集群。

.. dropdown:: scripts/reinforcement_learning/ray/launch.py
  :icon: code

  .. literalinclude:: ../../../scripts/reinforcement_learning/ray/launch.py
    :language: python
    :emphasize-lines: 15-36

基于 Docker 的本地快速入门
-----------------------------

首先，按照 `Docker Guide <https://isaac-sim.github.io/IsaacLab/main/source/deployment/docker.html>`_
设置 NVIDIA Container Toolkit 和 Docker Compose。

然后，运行以下步骤以启动一次调优运行。

.. code-block:: bash

  # Build the base image, but we don't need to run it
  python3 docker/container.py start && python3 docker/container.py stop
  # Build the tuning image with extra deps
  docker build -t isaacray -f scripts/reinforcement_learning/ray/cluster_configs/Dockerfile .
  # Start the tuning image - symlink so that changes in the source folder show up in the container
  docker run -v $(pwd)/source:/workspace/isaaclab/source -it --gpus all --net=host --entrypoint /bin/bash isaacray
  # Start the Ray server within the tuning image
  echo "import ray; ray.init(); import time; [time.sleep(10) for _ in iter(int, 1)]" | ./isaaclab.sh -p



在另一个终端中，运行以下命令。


.. code-block:: bash

  # In a new terminal (don't close the above) , enter the image with a new shell.
  docker container ps
  docker exec -it <ISAAC_RAY_IMAGE_ID_FROM_CONTAINER_PS> /bin/bash
  # Start a tuning run, with one parallel worker per GPU
  ./isaaclab.sh -p scripts/reinforcement_learning/ray/tuner.py \
    --cfg_file scripts/reinforcement_learning/ray/hyperparameter_tuning/vision_cartpole_cfg.py \
    --cfg_class CartpoleTheiaJobCfg \
    --run_mode local \
    --workflow scripts/reinforcement_learning/rl_games/train.py \
    --num_workers_per_node <NUMBER_OF_GPUS_IN_COMPUTER>


要查看训练日志，在另一个终端中运行以下命令，然后在浏览器中访问 ``localhost:6006`` 。

.. code-block:: bash

  # In a new terminal (don't close the above) , enter the image with a new shell.
  docker container ps
  docker exec -it <ISAAC_RAY_IMAGE_ID_FROM_CONTAINER_PS> /bin/bash
  # Start a tuning run, with one parallel worker per GPU
  tensorboard --logdir=.


以下文件描述了如何提交 resource-wrapped 单个任务，而不是自动调优运行。

.. dropdown:: scripts/reinforcement_learning/ray/wrap_resources.py
  :icon: code

  .. literalinclude:: ../../../scripts/reinforcement_learning/ray/wrap_resources.py
    :language: python
    :emphasize-lines: 10-63

``task_runner.py`` 通过单个声明式 YAML 文件将 Python 任务派发到 Ray 集群。这种方式允许用户为每次运行指定额外的 pip 包和 Python 模块。它支持细粒度的资源分配，可以显式控制分配给每个任务的 CPU、GPU 和内存数量。该运行器还提供高级调度功能：可以通过主机名或节点 ID 将任务限制在特定节点上，并支持两种启动模式：任务可以在资源可用时独立执行，也可以分组为同时执行的批次——非常适合多节点训练任务——这确保只有在集群中资源充足时，所有任务才会一起启动。

.. dropdown:: scripts/reinforcement_learning/ray/task_runner.py
  :icon: code

  .. literalinclude:: ../../../scripts/reinforcement_learning/ray/task_runner.py
    :language: python
    :emphasize-lines: 13-105

要使用此脚本，请运行类似以下的命令（将 ``tasks.yaml`` 替换为你的实际配置文件）：

.. code-block:: bash

  python3 scripts/reinforcement_learning/ray/submit_job.py --aggregate_jobs task_runner.py --task_cfg tasks.yaml

有关如何编写 ``tasks.yaml`` 文件的详细说明，请参阅 ``task_runner.py`` 中的注释。

**提示：** 将 ``tasks.yaml`` 文件放在 ``scripts/reinforcement_learning/ray`` 目录中，以便在上传 ``working_dir`` 时将其包含在内。之后就可以在命令中使用相对路径引用它。

可以从正在运行的容器中传输文件，方法如下。

.. code-block:: bash

  docker container ps
  docker cp <ISAAC_RAY_IMAGE_ID_FROM_CONTAINER_PS>:</path/in/container/file>  </path/on/host/>


对于调优任务，请将调优任务 / 超参数扫描指定为 :class:`JobCfg` 的子类。
由于环境入口点和 hydra 参数存在差异，
内置的 :class:`JobCfg` 仅支持 ``rl_games`` 工作流；不过，只要提供兼容的
:class:`JobCfg` ，其他工作流也可以正常工作。

.. dropdown:: scripts/reinforcement_learning/ray/tuner.py (JobCfg definition)
  :icon: code

  .. literalinclude:: ../../../scripts/reinforcement_learning/ray/tuner.py
    :language: python
    :start-at: class JobCfg
    :end-at: self.cfg = cfg

例如，请参见以下 Cartpole 示例配置。

.. dropdown:: scripts/reinforcement_learning/ray/hyperparameter_tuning/vision_cartpole_cfg.py
  :icon: code

  .. literalinclude:: ../../../scripts/reinforcement_learning/ray/hyperparameter_tuning/vision_cartpole_cfg.py
    :language: python


远程集群
---------------

选择以下方法之一来创建一个 Ray 集群，以接受并执行派发的任务。

KubeRay 设置
~~~~~~~~~~~~~

如果在 Google GKE 上使用 KubeRay 集群以及开箱即用的集群启动文件，
还需要以下依赖。

.. code-block:: bash

  python3 -p -m pip install kubernetes Jinja2

在带有 KubeRay 的 Kubernetes 集群上使用时，
例如 Google Kubernetes Engine 或 Amazon Elastic Kubernetes Service，需要 ``kubectl`` ，它
可以通过 `Kubernetes 网站 <https://kubernetes.io/docs/tasks/tools/>`_ 安装。

Google Cloud 是目前唯一经过测试的平台，不过
只要配置好以下内容，任何云服务商都应该可以正常工作。

.. attention::
  应修改 ``ray`` 命令以使用 Isaac Python，可以采用与
  ``sed -i "1i $(echo "#!/workspace/isaaclab/_isaac_sim/python.sh")" \
  /isaac-sim/kit/python/bin/ray && ln -s /isaac-sim/kit/python/bin/ray /usr/local/bin/ray`` 类似的方式实现。

- 一个容器镜像仓库（NGC、GCS artifact registry、AWS ECR 等），其中
  配置了支持 Ray 的 Isaac Lab 镜像。参见 ``cluster_configs/Dockerfile`` 以了解如何修改 ``isaac-lab-base``
  容器使其兼容 Ray。Ray 应使用 isaac sim Python 的 shebang，并且 ``nvidia-smi``
  应能在容器内正常工作。此处的设置需要小心，因为
  必须正确配置路径才能使一切正常工作。示例 dockerfile 很可能
  开箱即用并可以直接推送到仓库，
  只要基础镜像已按照容器指南中的方法构建完成。
- 一个 Kubernetes 环境，具有可用的 NVIDIA RTX（可能是 ``l4`` 或 ``l40`` 或 ``tesla-t4`` 或 ``a10``）GPU 直通节点池资源，
  能够访问你的容器镜像仓库/存储桶，并且已启用 Ray operator 并具有正确的 IAM
  权限。只要你的账户或组织已获得 GPU 配额，使用 Google GKE 或 AWS EKS
  等服务即可轻松实现。建议
  使用手动管理的 Kubernetes 服务而非“autopilot”服务，以进行经济的
  实验，因为这样可以在不使用时完全关闭集群，
  不过这可能需要安装 `Nvidia GPU Operator <https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/google-gke.html>`_ 。
- 一个集群可以访问的 `MLFlow 服务器 <https://mlflow.org/docs/latest/getting-started/logging-first-model/step1-tracking-server.html>`_
  （Google Cloud 已包含该项，可参考其格式和 MLFlow 集成）。
- 一个描述如何分配资源的 ``kuberay.yaml.ninja`` 文件（Google Cloud 已包含该项，
  可参考其格式和 MLFlow 集成）。

Ray 集群（不使用 Kubernetes）设置
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. attention::
  像在 KubeRay 集群中那样修改 Ray 命令以使用 Isaac Python，并按照相同的
  步骤创建镜像/集群权限。

更多信息请参阅 `Ray Clusters Overview <https://docs.ray.io/en/latest/cluster/getting-started.html>`_ 或
`Anyscale <https://www.anyscale.com/product>`_ 。

此外，创建一个本地主机和集群都可以访问的 `MLFlow 服务器 <https://mlflow.org/docs/latest/getting-started/logging-first-model/step1-tracking-server.html>`_ 。

KubeRay 与纯 Ray 的共享步骤（第一部分）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1.) 在本地机器上安装 Ray。

.. code-block:: bash

  python3 -p -m pip install ray[default]==2.31.0

2.) 构建 Isaac Ray 镜像，并将其上传到你选择的容器镜像仓库。

.. code-block:: bash

  # Login with NGC (nvcr.io) registry first, see docker steps in repo.
  python3 docker/container.py start
  # Build the special Isaac Lab Ray Image
  docker build -t <REGISTRY/IMAGE_NAME> -f scripts/reinforcement_learning/ray/cluster_configs/Dockerfile .
  # Push the image to your registry of choice.
  docker push <REGISTRY/IMAGE_NAME>

仅限 KubeRay 集群
~~~~~~~~~~~~~~~~~~~~~
`k9s <https://github.com/derailed/k9s>`_ 是一个很好的集群监控工具，可以
通过 ``snap install k9s --devmode`` 轻松安装。

1.) 验证集群访问权限，以及是否安装了正确的 operator。

.. code-block:: bash

  # Verify cluster access
  kubectl cluster-info
  # If using a manually managed cluster (not Autopilot or the like)
  # verify that there are node pools
  kubectl get nodes
  # Check that the ray operator is installed on the cluster
  # should list rayclusters.ray.io , rayjobs.ray.io , and rayservices.ray.io
  kubectl get crds | grep ray
  # Check that the NVIDIA Driver Operator is installed on the cluster
  # should list clusterpolicies.nvidia.com
  kubectl get crds | grep nvidia

2.) 创建 KubeRay 集群和一个用于接收日志的 MLFlow 服务器，
并确保集群可以访问它。
对于 Google GKE，这一步可以自动完成，
具体说明包含在以下创建文件中。

.. dropdown:: scripts/reinforcement_learning/ray/launch.py
  :icon: code

  .. literalinclude:: ../../../scripts/reinforcement_learning/ray/launch.py
    :language: python
    :emphasize-lines: 15-36

对于其他云服务， ``kuberay.yaml.ninja`` 将与 Google 的类似。


.. dropdown:: scripts/reinforcement_learning/ray/cluster_configs/google_cloud/kuberay.yaml.ninja
  :icon: code

  .. literalinclude:: ../../../scripts/reinforcement_learning/ray/cluster_configs/google_cloud/kuberay.yaml.jinja
      :language: python



3.) 获取 KubeRay 集群 IP 地址以及 MLFLow 服务器 IP。
对于 KubeRay 集群，这一步可以自动完成，
具体说明包含在以下获取文件中。
KubeRay 集群信息会保存到文件中，而 MLFLow 服务器 IP 则
会打印出来。

.. dropdown:: scripts/reinforcement_learning/ray/grok_cluster_with_kubectl.py
  :icon: code

  .. literalinclude:: ../../../scripts/reinforcement_learning/ray/grok_cluster_with_kubectl.py
    :language: python
    :emphasize-lines: 14-26

仅限 Ray 集群（不使用 Kubernetes）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


1.) 验证集群访问权限。

2.) 创建一个 ``~/.cluster_config`` 文件，每个唯一集群的 ``name: <NAME> address: http://<IP>:<PORT>`` 各占
一行。对于单个集群，该文件中应只有一行。

3.) 启动一个 MLFLow 服务器来接收 ray 集群可访问的日志，
并确定服务器 URI。

KubeRay 与纯 Ray 的共享派发步骤（第二部分）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


1.) 使用以下命令测试集群是否正常运行。

.. code-block:: bash

  # Test that NVIDIA GPUs are visible and that Ray is operation with the following command:
  python3 scripts/reinforcement_learning/ray/submit_job.py --aggregate_jobs wrap_resources.py --test

2.) 提交调优和/或 resource-wrapped 任务的方法在 :file:`submit_job.py` 文件中有描述。

.. dropdown:: scripts/reinforcement_learning/ray/submit_job.py
  :icon: code

  .. literalinclude:: ../../../scripts/reinforcement_learning/ray/submit_job.py
    :language: python
    :emphasize-lines: 13-61

3.) 对于调优任务，请将调优任务 / 超参数扫描指定为 :class:`JobCfg` 。
由于环境入口点和 hydra 参数存在差异，
内置的 :class:`JobCfg` 仅支持 ``rl_games`` 工作流；不过，只要提供兼容的
:class:`JobCfg` ，其他工作流也可以正常工作。

.. dropdown:: scripts/reinforcement_learning/ray/tuner.py (JobCfg definition)
  :icon: code

  .. literalinclude:: ../../../scripts/reinforcement_learning/ray/tuner.py
    :language: python
    :start-at: class JobCfg
    :end-at: self.cfg = cfg

例如，请参见以下 Cartpole 示例配置。

.. dropdown:: scripts/reinforcement_learning/ray/hyperparameter_tuning/vision_cartpole_cfg.py
  :icon: code

  .. literalinclude:: ../../../scripts/reinforcement_learning/ray/hyperparameter_tuning/vision_cartpole_cfg.py
    :language: python


要查看调优结果，请查看你所创建服务器的 MLFlow 仪表板。
对于 KubeRay，可以通过以下命令对 MLFlow 仪表板进行端口转发。

``kubectl port-forward service/isaacray-mlflow 5000:5000``

然后在浏览器中访问以下地址。

``localhost:5000``

如果 MLFlow 端口已按上述方式转发，可以使用
以下命令将其转换为 tensorboard 日志。

``./isaaclab.sh -p scripts/reinforcement_learning/ray/mlflow_to_local_tensorboard.py \
--uri http://localhost:5000 --experiment-name IsaacRay-<CLASS_JOB_CFG>-tune --download-dir test``


Kubernetes 集群清理
''''''''''''''''''''''''''

为了节约资源，并可能将宝贵的 GPU 资源释放出来供共享计算平台上的其他人使用，
请在使用后销毁 Ray 集群。它们可以轻松地重新创建。
对于 KubeRay 集群，可以按如下方式进行。

.. code-block:: bash

  kubectl get raycluster | egrep 'isaacray' | awk '{print $1}' | xargs kubectl delete raycluster &&
  kubectl get deployments | egrep 'mlflow' | awk '{print $1}' | xargs kubectl delete deployment &&
  kubectl get services | egrep 'mlflow' | awk '{print $1}' | xargs kubectl delete service &&
  kubectl get services | egrep 'isaacray' | awk '{print $1}' | xargs kubectl delete service
