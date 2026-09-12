.. _cloud-training:

云端训练
========

本指南介绍如何使用 `SkyPilot <https://skypilot.readthedocs.io/>`_ 在
`Lambda Cloud <https://lambdalabs.com/>`_ 上启动训练任务。SkyPilot 会申请
GPU 实例、同步你的代码、运行任务，并在任务结束后释放机器。

``scripts/cloud/`` 中有两个 SkyPilot 任务文件：

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - 文件
     - 说明
   * - ``train.yaml``
     - 使用 uv 直接安装 mjlab。
   * - ``train-docker.yaml``
     - 从 GHCR 拉取预构建的 Docker 镜像，以获得可复现的环境。


前提条件
--------

**1. 安装 SkyPilot**

SkyPilot 是一个本地 CLI 工具，并非项目依赖。请使用以下命令安装：

.. code-block:: bash

   uv tool install "skypilot[lambda]"

**2. Lambda Cloud API 密钥**

在 `Lambda Cloud API keys
<https://cloud.lambda.ai/api-keys/cloud-api>`_ 页面生成一个密钥。建议用你的
机器名来命名 (例如 ``kevins-macbook``)，以便日后区分各个密钥。

.. code-block:: bash

   mkdir -p ~/.lambda_cloud && chmod 700 ~/.lambda_cloud
   echo "api_key = <your-api-key>" > ~/.lambda_cloud/lambda_keys
   chmod 600 ~/.lambda_cloud/lambda_keys

**3. 验证安装**

.. code-block:: bash

   sky check lambda

你应该能看到 Lambda 被列为已启用的云。

**4. W&B 凭据** *(可选)*

如果你使用 Weights & Biases 记录日志，请安装 ``wandb`` CLI 并登录：

.. code-block:: bash

   uv tool install wandb
   wandb login

这会把你的凭据存入 ``~/.netrc``。SkyPilot 任务文件会通过 ``file_mounts``
把该文件挂载到远程实例上，因此 ``wandb`` 会自动完成认证，无需设置环境
变量。


快速上手
--------

在仓库根目录下执行：

.. code-block:: bash

   sky launch scripts/cloud/train.yaml \
     --env TASK=Mjlab-Velocity-Flat-Unitree-G1

   # Or with Docker:
   sky launch scripts/cloud/train-docker.yaml \
     --env TASK=Mjlab-Velocity-Flat-Unitree-G1
背后的流程如下：

1. SkyPilot 找到一台具备所请求 GPU 的可用 Lambda 实例。
2. 申请该实例，并通过 rsync 上传你的本地代码。
3. 运行 ``setup`` 步骤 (uv 安装或 Docker 拉取)。
4. 运行 ``run`` 步骤 (即训练)。
5. 空闲 5 分钟后，实例会自动销毁。

.. warning::

   Lambda 实例只支持 **启动** 与 **终止** 两种操作，没有暂停或挂起选项。
   不要在实例内部执行 ``sudo shutdown`` ，这会让机器进入告警状态，计费仍
   会继续。请始终使用 ``sky down`` 来终止实例。


常用操作
--------

**列出可用 GPU**

.. code-block:: bash

   sky show-gpus --infra lambda

**选择其他 GPU**

.. code-block:: bash

   sky launch scripts/cloud/train.yaml --gpus H100:1    # 1x H100
   sky launch scripts/cloud/train.yaml --gpus A100:8    # 8x A100
   sky launch scripts/cloud/train.yaml --gpus A10:1     # 1x A10 (cheaper)

.. note::

   两个任务文件都传入了 ``--gpu-ids all`` ，因此多 GPU 实例会自动启用
   :ref:`分布式训练 <distributed-training>` 。申请多于一块 GPU 时，建议
   按比例调低 ``MAX_ITERATIONS`` 。缩放行为的细节请参见
   :ref:`distributed-training` 。

**覆盖训练参数**

YAML ``envs`` 块中的每个变量都可以在命令行上用 ``--env`` 覆盖：

.. code-block:: bash

   sky launch scripts/cloud/train.yaml \
     --env TASK=Mjlab-Velocity-Flat-Unitree-Go1 \
     --env NUM_ENVS=8192 \
     --env MAX_ITERATIONS=10000
**运行自己的任务**

.. code-block:: bash

   sky launch scripts/cloud/train.yaml \
     --env TASK=Mjlab-Velocity-Flat-Unitree-Go1

查看所有已注册的任务：

.. code-block:: bash

   uv run list-envs
   uv run list-envs --keyword Velocity  # filter by keyword


超参数搜索
----------

可以将 `W&B Sweeps <https://docs.wandb.ai/models/sweeps/>`_ 与 SkyPilot
结合，在多 GPU 实例上搜索超参数。sweep 控制器运行在 W&B 服务器上；实例上
的每块 GPU 各运行一个独立的 sweep agent，负责拉取一份超参数配置、进行
训练并上报指标。

示例采用 ``method: random`` ，即每个 agent 独立采样。贝叶斯搜索同样适合
并行 agent：agent 完成后会回报结果，控制器会在各轮之间更新其模型。如果
使用贝叶斯搜索，请把 ``run_cap`` 设置得足够高，让优化器能经历多轮迭代。

共涉及四个文件：

.. list-table::
   :widths: 35 65
   :header-rows: 1

   * - 文件
     - 说明
   * - ``sweep.yaml``
     - W&B sweep 配置 (参数、搜索方法、指标)。
   * - ``sweep-cluster.yaml``
     - SkyPilot 集群定义 (资源、setup，无 run 部分)。
   * - ``sweep-agent.yaml``
     - 在单块 GPU 上运行 ``wandb agent`` 的 SkyPilot 任务定义。
   * - ``sweep-launch.sh``
     - 便捷脚本：创建 sweep、申请集群，并为每块 GPU 提交一个 agent。

**快速上手**

.. code-block:: bash

   ./scripts/cloud/sweep-launch.sh A100:8   # 8 agents on an 8xA100

该命令会创建一个 W&B sweep、申请一个集群，并为每块 GPU 提交一个 agent。
每个 agent 使用由 sweep 控制器采样出的一组不同超参数来运行训练。

**手动操作** (如果你希望有更多控制)：

.. code-block:: bash

   # 1. Create the sweep (returns a SWEEP_ID).
   wandb sweep scripts/cloud/sweep.yaml

   # 2. Provision the cluster (runs setup, no agents yet).
   sky launch scripts/cloud/sweep-cluster.yaml \
     -c mjlab-sweep --gpus A100:8

   # 3. Submit one agent per GPU.
   sky exec mjlab-sweep scripts/cloud/sweep-agent.yaml \
     --gpus A100:1 --env SWEEP_ID=<entity/project/sweep_id> -d

可以在 W&B 仪表盘上或通过 ``sky queue mjlab-sweep`` 监控进度。结束后用
``sky down mjlab-sweep`` 销毁集群。


监控
----

Lambda 分配实例可能需要五分钟甚至更久。可以另开一个终端随时查看情况：

.. code-block:: bash

   sky status                               # cluster state (INIT, UP, ...)
   sky logs sky-<cluster-name>              # stream logs in real time
   sky logs sky-<cluster-name> --no-follow  # print current logs and exit
   sky queue sky-<cluster-name>             # job queue for the cluster

.. tip::

   如果集群长时间停留在 ``INIT`` 状态，很可能是该 GPU 类型已售罄。可以用
   ``sky down`` 取消并换一种 GPU 重试，或者加上 ``--retry-until-up`` 让
   SkyPilot 持续轮询，直到有可用容量。

.. code-block:: bash

   sky down sky-<cluster-name>
   sky launch scripts/cloud/train.yaml --retry-until-up


在失败的任务上迭代
------------------

任务失败后，集群会继续运行 (并继续计费)。你可以在本地修复问题后重新提交，
无需等待新实例：

.. code-block:: bash

   sky exec sky-<cluster-name> scripts/cloud/train.yaml
.. important::

   ``sky exec`` 会 rsync 你的最新代码，并且只重跑 ``run`` 步骤， **不会**
   重跑 ``setup`` 。如果你的修复涉及依赖变更，请重新使用 ``sky launch`` ，
   或者 SSH 进入实例手动执行 setup 命令。

其他有用的命令：

.. code-block:: bash

   sky down sky-<cluster-name>  # terminate the instance immediately
   ssh sky-<cluster-name>       # SSH in (SkyPilot configures this for you)


成本管理
--------

.. warning::

   每次使用后务必运行 ``sky status`` ，确认没有仍在运行的实例。被遗忘的
   实例是意外扣费最常见的原因。要一次性终止所有实例： ``sky down -a`` 。

- 实例默认在空闲 5 分钟后自动销毁。可以在 YAML 中修改 (``idle_minutes``) ，
  也可以在启动时用 ``--idle-minutes-to-autostop`` 设置。
- YAML 中的 ``down: true`` 配置表示实例停止时会被彻底销毁，而不仅仅是
  暂停，计费会完全停止。


故障排查
--------

**没有可用实例**

Lambda 的 GPU 经常售罄。可以尝试以下几种办法：

- 使用 ``--retry-until-up`` 自动轮询。
- 尝试其他 GPU 类型： ``--gpus A100:1`` 、 ``--gpus A10:1`` 等。
- 如果你拥有其他云 (GCP、AWS) 的凭据，SkyPilot 可以自动回退到这些云。
