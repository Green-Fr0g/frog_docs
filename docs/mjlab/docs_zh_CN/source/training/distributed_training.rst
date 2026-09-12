.. _distributed-training:

分布式训练
==========

mjlab 借助 `torchrunx <https://github.com/apoorvkh/torchrunx>`_ 支持多 GPU
分布式训练。每块 GPU 使用自己的环境独立运行 rollout ，并在策略更新时同步
梯度。吞吐量随 GPU 数量接近线性扩展。


用法
----

.. code-block:: bash

    # Single GPU (default).
    uv run train <task-name> --gpu-ids "[0]"

    # Two GPUs.
    uv run train <task-name> --gpu-ids "[0, 1]"

    # All available GPUs.
    uv run train <task-name> --gpu-ids all

    # CPU mode.
    uv run train <task-name> --gpu-ids None

要点：

- 如果设置了 ``CUDA_VISIBLE_DEVICES`` ，GPU 索引会相对于它来解释。例如
  ``CUDA_VISIBLE_DEVICES=2,3 uv run train ... --gpu-ids "[0, 1]"`` 使用的
  是物理 GPU 2 和 3。
- 单 GPU 与 CPU 模式直接运行，不经过 torchrunx。


缩放行为
--------

多 GPU 训练是 **数据并行，而非任务切分** 。每块 GPU 都独立运行完整的
``num-envs`` 数量，因此每次迭代采集的总经验量为：

.. code-block:: text

    experience per iteration = num_envs x num_steps_per_env x num_gpus

迭代速度基本保持不变，因为每块 GPU 做的工作量相同。收益在于每次策略更新
能看到更多样的经验，从而让策略在实际时间 (wall-clock time) 内更快收敛。

.. important::

   由于 ``max-iterations`` 不会自动调整，使用更多 GPU 训练会按比例耗费
   更长的实际时间。如果希望总训练时长不变，请按 GPU 数量调低
   ``max-iterations`` (例如从 1 块 GPU 增加到 2 块时将其减半) 。


工作原理
--------

mjlab 的角色是借助 ``wp.ScopedDevice`` **在每块 GPU 上隔离 MuJoCo Warp
仿真** ，其余工作都由 torchrunx 完成。

**进程派生。** ``torchrunx.Launcher`` 为每块 GPU 派生一个进程，并设置
``RANK`` 、 ``LOCAL_RANK`` 和 ``WORLD_SIZE`` 来协调它们。每个进程使用分配
给它的 GPU 执行训练函数。

**独立 rollout。** 每个进程各自维护：

- 环境实例 (含 ``num-envs`` 个并行环境) ，通过 ``wp.ScopedDevice`` 隔离
  在分配给它的 GPU 上
- 策略网络副本
- 经验缓冲区 (大小为 ``num_steps_per_env * num_envs``)

每个进程使用 ``seed = cfg.seed + local_rank`` ，以确保各 GPU 上的随机经验
互不相同，提高样本多样性。

**梯度同步。** 在更新阶段，RSL-RL 通过 ``reduce_parameters()`` 方法在每个
mini-batch 之后同步梯度：

1. 每个进程在自己的本地 mini-batch 上独立计算梯度
2. 所有策略梯度被展平成一个张量
3. ``torch.distributed.all_reduce`` 对所有 GPU 上的梯度取平均
4. 平均后的梯度被复制回每个参数，使各策略保持同步

**单写者 I/O。** 只有 rank 0 写入配置文件、视频和 W&B 日志，以避免竞争
条件。


日志
----

默认情况下，torchrunx 的进程日志保存在 ``{log_dir}/torchrunx/`` 。该路径
可以自定义：

.. code-block:: bash

    # Disable torchrunx file logging.
    uv run train <task-name> --gpu-ids "[0, 1]" --torchrunx-log-dir ""

    # Custom log directory.
    uv run train <task-name> --gpu-ids "[0, 1]" --torchrunx-log-dir /path/to/logs

    # Environment variable (takes precedence over the flag).
    TORCHRUNX_LOG_DIR=/tmp/logs uv run train <task-name> --gpu-ids "[0, 1]"
