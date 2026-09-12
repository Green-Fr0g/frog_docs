SEED G1 CSV 数据准备
====================

本指南介绍如何将 BONES-SEED 重定向到 G1 的 CSV 动作数据
转换为 Unitree G1 人形机器人可用的 ProtoMotions 格式。

.. note::

   BONES-SEED 数据集包含**约 14.2 万条动作**——规模远大于 AMASS
   （约 1.5 万条）。在这种规模下：

   * **转换** 应在多个 CPU 上并行进行（参见
     :ref:`seed-g1-scaling-up`）。
   * **训练** 应使用分片（sharded）MotionLib 的 chunk 文件，使每张 GPU 只加载一部分动作，
     避免 GPU 显存耗尽（参见 :ref:`seed-g1-training`）。

概述
----

`BONES-SEED <https://huggingface.co/datasets/bones-studio/seed>`_ 数据集中包含已重定向到
Unitree G1 骨架并以 CSV 文件导出的动作。转换管线将这些 CSV 文件
转换为 ProtoMotions ``.motion`` 格式。

.. code-block:: text

   Retargeted G1 .csv files (joint angles in degrees, 120 fps)
        │
        ▼ (convert_g1_csv_to_proto.py)
   ProtoMotions .motion files (30 fps)
        │
        ▼ (motion_lib.py --motion-path)
   Packaged .pt MotionLib (one per chunk, or single file for small sets)

前置条件
--------

1. **下载 BONES-SEED**：从
   `Hugging Face <https://huggingface.co/datasets/bones-studio/seed>`_ 下载数据集。
   下载后，解压 G1 的 tar 归档：

   .. code-block:: bash

      cd bones-seed
      tar -xf g1.tar

   期望的目录结构如下：

   .. code-block:: text

      bones-seed/
        └── g1/
            └── csv/
                ├── <date_1>/
                │   ├── motion_001.csv
                │   └── motion_002.csv
                └── <date_2>/
                    └── ...

CSV 格式
--------

每个 CSV 文件包含以下列：

* ``Frame``：帧索引
* ``root_translateX/Y/Z``：根节点位置（厘米）
* ``root_rotateX/Y/Z``：根节点朝向，外旋（extrinsic）XYZ 欧拉角（度）
* ``<joint>_dof``：关节角度（度），与 G1 MJCF 的关节顺序一致

快速上手：小型子集
------------------

对于少量 CSV 文件（例如只用几个动作做测试）：

.. code-block:: bash

   # Convert
   python data/scripts/convert_g1_csv_to_proto.py \
       --input-dir /path/to/bones-seed/g1/csv \
       --output-dir /path/to/output/motions \
       --input-fps 120 \
       --output-fps 30

   # Package into a single .pt
   python protomotions/components/motion_lib.py \
       --motion-path /path/to/output/motions/ \
       --output-file /path/to/seed_g1_motions.pt

   # Verify visually
   python examples/motion_libs_visualizer.py \
       --motion_files /path/to/seed_g1_motions.pt \
       --robot g1 \
       --simulator isaacgym

**关键参数：**

* ``--input-dir``：递归搜索 ``.csv`` 文件的根目录
* ``--output-dir``：保存 ``.motion`` 文件的目录
* ``--input-fps``：源 CSV 帧率（默认：30）
* ``--output-fps``：目标输出帧率（默认：30）
* ``--robot-type``：机器人类型（默认：``g1``）
* ``--euler-order``：根节点旋转的欧拉角约定（默认：``xyz``）
* ``--apply-motion-filter``：启用质量过滤
* ``--force-remake``：覆盖已存在的文件

转换器还会为所有 body 计算启发式的地面接触标签（基于
高度和速度阈值）。这些标签在训练中被某些奖励函数和
观测使用（例如接触感知的跟踪奖励）。

.. _seed-g1-scaling-up:

规模化：并行转换
----------------

对于完整的 BONES-SEED 数据集（约 14.2 万个 CSV 文件），转换器通过
``--num-rank`` 和 ``--slurm-rank`` 支持**基于分块的并行**。每个 rank
处理一个确定性的文件子集，因此所有 rank 可以独立运行。

分块还能让每个打包后的 ``.pt`` 文件保持在可控的大小。
把整个数据集加载到单个文件中会占用过多 GPU 显存。

**SLURM 数组任务示例（24 个 chunk）：**

.. code-block:: bash

   #!/bin/bash
   #SBATCH --job-name=seed_g1_csv_to_proto
   #SBATCH --array=0-23
   #SBATCH --cpus-per-task=24
   #SBATCH --mem=64G
   #SBATCH --time=8:00:00

   CHUNK=${SLURM_ARRAY_TASK_ID}
   CHUNK_DIR=/path/to/output/chunk_$(printf '%02d' $CHUNK)
   CHUNK_PT=/path/to/output/chunk_$(printf '%02d' $CHUNK).pt

   python data/scripts/convert_g1_csv_to_proto.py \
       --input-dir /path/to/bones-seed/g1/csv \
       --output-dir $CHUNK_DIR \
       --input-fps 120 --output-fps 30 \
       --apply-motion-filter \
       --robot-type g1 --euler-order xyz \
       --num-rank 24 --slurm-rank $CHUNK

   python protomotions/components/motion_lib.py \
       --motion-path $CHUNK_DIR/ \
       --output-file $CHUNK_PT

**不使用 SLURM（shell 循环）：**

.. code-block:: bash

   for RANK in $(seq 0 23); do
       python data/scripts/convert_g1_csv_to_proto.py \
           --input-dir /path/to/bones-seed/g1/csv \
           --output-dir /path/to/output/chunk_$(printf '%02d' $RANK) \
           --input-fps 120 --output-fps 30 \
           --apply-motion-filter \
           --robot-type g1 --euler-order xyz \
           --num-rank 24 --slurm-rank $RANK &
   done
   wait

   for RANK in $(seq 0 23); do
       python protomotions/components/motion_lib.py \
           --motion-path /path/to/output/chunk_$(printf '%02d' $RANK)/ \
           --output-file /path/to/output/chunk_$(printf '%02d' $RANK).pt
   done

.. _seed-g1-training:

使用动作库训练
--------------

**单文件动作库** （小型数据集）：

.. code-block:: bash

   python protomotions/train_agent.py \
       --robot-name g1 \
       --simulator isaacgym \
       --experiment-path examples/experiments/mimic/mlp.py \
       --experiment-name g1_seed_csv \
       --motion-file /path/to/seed_g1_motions.pt \
       --num-envs 4096 \
       --batch-size 16384

**分片动作库** （完整 BONES-SEED，多 GPU）：

对于完整数据集，请使用分片 chunk，使每张 GPU 只把一个 chunk 加载进内存。
用 ``slurmrank`` 占位符模式为 chunk 文件命名，例如
``chunk_slurmrank.pt``。运行时，``MotionLib``（参见
``protomotions/components/motion_lib.py:process_packaged_motion_file_name_multi_gpu``）
会发现所有匹配的文件（``chunk_00.pt``、``chunk_01.pt``、……），并通过轮询
（``rank % num_chunks``）为每个 GPU rank 分配一个 chunk。

.. code-block:: bash

   python protomotions/train_agent.py \
       --robot-name g1 \
       --simulator isaaclab \
       --experiment-path examples/experiments/mimic/mlp.py \
       --experiment-name g1_seed_csv_allchunks \
       --motion-file /path/to/output/chunk_slurmrank.pt \
       --ngpu 8 --nodes 3 \
       --num-envs 8192 \
       --batch-size 16384 \
       --training-max-steps 10000000000000 \
       --use-slurm --use-wandb

这会启动 24 张 GPU（3 节点 × 8 GPU），每张加载 24 个 chunk 中的一个。
每张 GPU 在自己的动作子集上训练，从而将单 GPU 显存占用控制在合理范围内。

后续步骤
--------

* :doc:`seed_bvh_preparation` - 准备用于 `SOMA <https://github.com/NVlabs/SOMA-X>`_ 骨架的 SEED BVH 数据
* :doc:`kimodo_preparation` - 准备由 Kimodo 生成的动作
