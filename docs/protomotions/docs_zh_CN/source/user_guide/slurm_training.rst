使用 SLURM 进行可扩展训练
============================

本指南介绍如何在 SLURM 管理的 HPC 集群上运行 ProtoMotions 训练任务。

什么是 SLURM？
--------------

`SLURM <https://slurm.schedmd.com/>`_ （Simple Linux Utility for Resource Management）是
高性能计算集群中广泛使用的作业调度器。它管理计算资源、排队作业，并处理多节点
分布式工作负载。大多数学术和企业 GPU 集群都使用 SLURM 进行作业调度。

概述
--------

ProtoMotions 提供了 ``train_slurm.py``，这是一个启动脚本，可以：

1. **同步你的代码** 到集群（通过基于 SSH 的 rsync）
2. **生成 SLURM 批处理脚本**，包含正确的作业参数
3. **提交作业** 到集群队列
4. **通过 SLURM 作业数组实现自动恢复训练** （超时后作业继续运行）

该脚本是一个**模板**，旨在针对你的具体集群环境进行定制。

针对你的集群进行配置
----------------------------

在使用 SLURM 训练之前，请编辑 ``protomotions/train_slurm.py``
顶部的配置部分：

.. code-block:: python

   # =============================================================================
   # CLUSTER CONFIGURATION - EDIT THIS SECTION FOR YOUR CLUSTER
   # =============================================================================

   # Login node hostname (e.g., "login.mycluster.edu")
   CLUSTER_LOGIN_NODE = "YOUR_CLUSTER_LOGIN_NODE"

   # Base directory for experiments on the cluster filesystem
   CLUSTER_BASE_DIR = "/path/to/your/experiments/directory"

   # Container images (Singularity .sif or Enroot .sqsh format)
   CONTAINER_IMAGES = {
       "isaacgym": "/path/to/containers/isaacgym.sqsh",
       "isaaclab": "/path/to/containers/isaaclab.sqsh",
       "newton": "/path/to/containers/newton.sqsh",
   }

   # Default SLURM account (your allocation/project)
   DEFAULT_SLURM_ACCOUNT = "your_account"

   # Default SLURM partitions
   DEFAULT_SLURM_PARTITION = "gpu"

   # Filesystem mounts for container
   CONTAINER_MOUNTS = "/scratch:/scratch:rw"

**需要配置的关键设置：**

* ``CLUSTER_LOGIN_NODE``：集群登录节点的 SSH 主机名
* ``CLUSTER_BASE_DIR``：实验代码将同步到的目录
* ``CONTAINER_IMAGES``：容器镜像的路径（Singularity/Enroot）
* ``DEFAULT_SLURM_ACCOUNT``：你的 SLURM 配额或项目名称
* ``CONTAINER_MOUNTS``：要挂载进容器内的文件系统路径

容器环境搭建
~~~~~~~~~~~~~~~

你需要带有 ProtoMotions 依赖的容器化环境。请按集群要求，将你的 Docker 镜像
转换为 Singularity（``.sif``）或 Enroot（``.sqsh``）格式。

通过作业数组实现自动恢复训练
-------------------------------

长时间的训练任务往往会超过集群的时间限制（例如 4 小时的 walltime）。
ProtoMotions 通过两种机制自动处理这一问题：

**1. SLURM 作业数组**

启动脚本以数组形式提交作业（``--array=0-5%1``），即最多依次运行 5 个作业。
当某个作业超时后，下一个数组任务随即启动，并从最近的检查点恢复训练。

**2. AutoResume 回调**

启用 ``--use-slurm`` 后，训练会注册 ``AutoResumeCallbackSrun`` 回调。该回调会：

* 追踪已消耗的训练时间
* 在 SLURM 时间限制之前保存检查点（默认：3.5 小时后）
* 优雅地停止训练，让下一个数组作业得以恢复

.. code-block:: python

   # From protomotions/agents/callbacks/slurm_autoresume_srun.py
   class AutoResumeCallbackSrun(Callback):
       def __init__(self, autoresume_after=12600):  # 3.5 hours in seconds
           self.autoresume_after = autoresume_after
       
       def _check_autoresume(self, agent):
           if time.time() - self.start_time >= self.autoresume_after:
               agent.save()           # Save checkpoint
               agent._should_stop = True  # Signal graceful stop

默认的 ``autoresume_after=12600`` （3.5 小时）与 4 小时的作业时限配合良好，
为保存检查点预留了缓冲时间。

理解扩展参数
--------------------------------

``--num-envs`` 和 ``--batch-size`` 参数是**按每张 GPU** 指定的。在多 GPU 和
多节点训练中，有效总量会相应放大：

.. code-block:: text

   Total GPUs = ngpu × nodes
   Effective num-envs = num-envs × Total GPUs
   Effective batch-size = batch-size × Total GPUs

**示例：**

使用 ``--ngpu=4 --nodes=2 --num-envs=4096 --batch-size=16384`` 时：

* **GPU 总数**：4 × 2 = 8 张 GPU
* **有效环境数**：4,096 × 8 = **32,768 个并行环境**
* **有效批大小**：16,384 × 8 = **每次更新 131,072 个样本**

这一扩展是自动完成的——你只需指定每张 GPU 的数值，分布式训练会处理
所有进程间的聚合。

运行训练任务
----------------------

完成配置后，即可从本地机器启动训练：

.. code-block:: bash

   python protomotions/train_slurm.py \
       --robot-name=g1 \
       --simulator=isaaclab \
       --num-envs=4096 \
       --batch-size=16384 \
       --motion-file=/cluster/path/to/motions.pt \
       --experiment-path=examples/experiments/mimic/mlp_bm_l2c2.py \
       --experiment-name=g1_motion_tracker \
       --user=myusername \
       --ngpu=4 \
       --nodes=1 \
       --slurm-time=4:00:00 \
       --use-wandb

**关键参数：**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - 参数
     - 说明
   * - ``--robot-name``
     - 要训练的机器人（如 ``g1``、``smpl``、``h1_2``）
   * - ``--simulator``
     - 物理后端（``isaacgym``、``isaaclab``、``newton``）
   * - ``--num-envs``
     - 并行环境数（随 GPU 显存扩展）
   * - ``--batch-size``
     - PPO 批大小（通常为 num-envs 的 2-4 倍）
   * - ``--motion-file``
     - 动作数据路径（**集群上的路径**）
   * - ``--experiment-path``
     - 实验配置文件（相对于仓库根目录）
   * - ``--experiment-name``
     - 本次实验的唯一名称
   * - ``--user``
     - 你的集群用户名
   * - ``--ngpu``
     - 每个节点的 GPU 数
   * - ``--nodes``
     - 计算节点数
   * - ``--slurm-time``
     - 作业时限（HH:MM:SS）
   * - ``--array-size``
     - 自动恢复训练的尝试次数（默认：5）
   * - ``--training-max-iterations``
     - 完整采样与优化迭代的最大次数
   * - ``--use-wandb``
     - 启用 Weights & Biases 日志记录
   * - ``--wandb-project``
     - Weights & Biases 项目名称（默认：``physical_animation``）

多节点训练
-------------------

跨多节点的大规模训练：

.. code-block:: bash

   python protomotions/train_slurm.py \
       --robot-name=smpl \
       --simulator=isaacgym \
       --num-envs=8192 \
       --batch-size=16384 \
       --motion-file=/cluster/path/to/amass_train.pt \
       --experiment-path=examples/experiments/mimic/mlp.py \
       --experiment-name=smpl_motion_tracker_4node \
       --user=myusername \
       --ngpu=8 \
       --nodes=4 \
       --slurm-time=4:00:00 \
       --use-wandb

ProtoMotions 使用 PyTorch Fabric 进行分布式训练。每个节点运行 ``--ngpu`` 个
进程，梯度在所有节点间同步。

监控任务
---------------

提交后，脚本会打印监控命令：

.. code-block:: bash

   # Monitor live output
   ssh myusername@cluster 'tail -f /path/to/exp/slurm_output.log'
   
   # Check job status
   ssh myusername@cluster 'squeue -u myusername'
   
   # Cancel a job
   ssh myusername@cluster 'scancel <job_id>'

后续步骤
----------

* :doc:`configuration` - 配置系统详情
* :doc:`experiments` - 创建自定义实验
* :doc:`../tutorials/workflows/domain_randomization` - 用于训练鲁棒策略的域随机化
