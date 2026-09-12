SEED BVH 数据准备（SOMA 骨架）
==============================

本指南介绍如何将 BONES-SEED BVH 动作数据（SOMA 格式，77 关节）
转换为 soma23 人形可用的 ProtoMotions 格式。

.. note::

   BONES-SEED 数据集包含**约 14.2 万条动作**——规模远大于 AMASS
   （约 1.5 万条）。在这种规模下，转换和训练都需要特殊处理：

   * **转换** 应在多个 CPU 上并行进行（参见
     :ref:`seed-bvh-scaling-up`）。
   * **训练** 应使用分片（sharded）MotionLib 的 chunk 文件，使每张 GPU 只加载一部分动作，
     避免 GPU 显存耗尽（参见 :ref:`seed-bvh-training`）。

概述
----

`BONES-SEED <https://huggingface.co/datasets/bones-studio/seed>`_ 数据集包含
BVH 格式的动作捕捉数据，使用 77 关节的 SOMA 骨架。
BONES-SEED 提供两种 BVH 变体：**SOMA Uniform**（所有动作共享的标准化骨架）和
**SOMA Proportional**（按演员个体比例的骨架）。请使用
**SOMA Uniform**——它与 ProtoMotions 使用的单个 ``soma23_humanoid.xml`` MJCF 模型相匹配。

转换管线：

1. 解析 BVH 文件，得到局部旋转矩阵和根节点平移
2. 使用预先计算好的全局旋转偏移，将 BVH 的骨骼轴对齐零位姿态（zero-pose）转换为标准 T-pose
3. 从 77 个关节中筛选出 ``soma23_humanoid.xml`` MJCF 中的 23 个受驱动关节
4. 施加 Y-up 到 Z-up 的坐标变换，并计算完整的刚体状态

.. code-block:: text

   BONES-SEED .bvh files (77 joints, 120 fps, Y-up)
        │
        ▼ (convert_soma23_bvh_to_proto.py)
   ProtoMotions .motion files (23 bodies, 30 fps, Z-up)
        │
        ▼ (motion_lib.py --motion-path)
   Packaged .pt MotionLib (one per chunk, or single file for small sets)

前置条件
--------

1. **下载 BONES-SEED**：从
   `Hugging Face <https://huggingface.co/datasets/bones-studio/seed>`_ 下载数据集。
   下载后，解压 SOMA Uniform 的 tar 归档：

   .. code-block:: bash

      cd bones-seed
      tar -xf soma_uniform.tar

   期望的目录结构如下：

   .. code-block:: text

      bones-seed/
        └── soma_uniform/
            └── bvh/
                ├── <date_1>/
                │   ├── motion_001.bvh
                │   └── motion_002.bvh
                └── <date_2>/
                    └── ...

2. **T-pose 偏移**：文件 ``data/soma/standard_t_pose_global_offsets_rots.p``
   已包含在仓库中。其中存放了预先计算好的、每个 body 的全局旋转偏移，
   用于将 BVH 的骨骼轴对齐零位姿态转换为标准 T-pose。

快速上手：小型子集
------------------

对于少量 BVH 文件（例如只用几个动作做测试），可以直接转换并
打包为单个动作库文件：

.. code-block:: bash

   # Convert
   python data/scripts/convert_soma23_bvh_to_proto.py \
       --input-dir /path/to/bones-seed/soma_uniform/bvh \
       --output-dir /path/to/output/motions \
       --input-fps 120 \
       --output-fps 30

   # Package into a single .pt
   python protomotions/components/motion_lib.py \
       --motion-path /path/to/output/motions/ \
       --output-file /path/to/seed_bvh_motions.pt

   # Verify visually
   python examples/motion_libs_visualizer.py \
       --motion_files /path/to/seed_bvh_motions.pt \
       --robot soma23 \
       --simulator isaacgym

**关键参数：**

* ``--input-dir``：递归搜索 ``.bvh`` 文件的根目录
* ``--output-dir``：保存 ``.motion`` 文件的目录（保留子目录结构）
* ``--input-fps``：源 BVH 帧率（默认：120）
* ``--output-fps``：目标输出帧率（默认：30）
* ``--force-remake``：覆盖已存在的 ``.motion`` 文件
* ``--ignore-motion-filter``：跳过质量过滤（调试时有用）

转换器做了什么
--------------

1. **解析 BVH**：读取 BVH 层级结构（不包括虚拟的 ``Root`` 关节），得到
   以厘米为单位的局部旋转矩阵 ``(T, 77, 3, 3)`` 和根节点平移 ``(T, 3)``。
   根节点平移会被换算为米。

2. **T-pose 转换**：BVH 的零位姿态（所有旋转 = 单位矩阵）会把骨骼沿其主轴摆放，
   这并不是自然的 T-pose。``change_tpose()`` 函数使用预先计算的全局旋转偏移，
   将局部旋转重新表达为标准 T-pose 约定。

3. **身体筛选（subselection）**：将 77 个 SOMASkeleton 关节筛选为
   ``soma23_humanoid.xml`` 中的 23 个 body。被丢弃的 54 个关节是末端叶子节点
   （手指细节、面部关节、脚趾末端等），没有执行器。

4. **坐标变换 + 正向运动学（FK）**：将 Y-up 的局部旋转变换为 Z-up，
   再经过 MJCF 正向运动学计算，得到世界坐标位置、旋转、速度、
   自由度（DOF）位置/速度以及地面接触标签。

5. **接触标签估计**：基于高度和速度阈值，为所有 body 计算启发式的地面接触标签。
   这些标签在训练中被某些奖励函数和观测使用
   （例如接触感知的跟踪奖励）。

6. **质量过滤** （默认启用）：如果动作存在极端速度、身体部位低于地面，
   或出现不自然的腾空片段，则将其剔除。使用 ``--ignore-motion-filter`` 可关闭该过滤。

.. _seed-bvh-scaling-up:

规模化：并行转换
----------------

对于完整的 BONES-SEED 数据集（约 14.2 万个 BVH 文件），单进程转换会很慢。
转换器通过 ``--num-rank`` 和 ``--slurm-rank`` 支持**基于分块的并行**：
每个 rank 处理一个确定性的文件子集（通过 SHA-256 哈希分配），因此所有 rank 可以独立运行。

分块还能让每个打包后的 ``.pt`` 文件保持在可控的大小。
把整个数据集加载到单个文件中会占用过多内存。

**示例：使用 SLURM 的 15 个并行 worker**

.. code-block:: bash

   #!/bin/bash
   #SBATCH --job-name=seed_bvh_to_proto
   #SBATCH --array=0-14
   #SBATCH --cpus-per-task=8
   #SBATCH --mem=64G
   #SBATCH --time=8:00:00

   CHUNK=${SLURM_ARRAY_TASK_ID}
   CHUNK_DIR=/path/to/output/chunk_$(printf '%02d' $CHUNK)
   CHUNK_PT=/path/to/output/chunk_$(printf '%02d' $CHUNK).pt

   python data/scripts/convert_soma23_bvh_to_proto.py \
       --input-dir /path/to/bones-seed/soma_uniform/bvh \
       --output-dir $CHUNK_DIR \
       --input-fps 120 --output-fps 30 \
       --num-rank 15 --slurm-rank $CHUNK

   python protomotions/components/motion_lib.py \
       --motion-path $CHUNK_DIR/ \
       --output-file $CHUNK_PT

**不使用 SLURM（GNU parallel / shell 循环）：**

.. code-block:: bash

   for RANK in $(seq 0 14); do
       python data/scripts/convert_soma23_bvh_to_proto.py \
           --input-dir /path/to/bones-seed/soma_uniform/bvh \
           --output-dir /path/to/output/chunk_$(printf '%02d' $RANK) \
           --input-fps 120 --output-fps 30 \
           --num-rank 15 --slurm-rank $RANK &
   done
   wait

   for RANK in $(seq 0 14); do
       python protomotions/components/motion_lib.py \
           --motion-path /path/to/output/chunk_$(printf '%02d' $RANK)/ \
           --output-file /path/to/output/chunk_$(printf '%02d' $RANK).pt
   done

.. _seed-bvh-training:

使用动作库训练
--------------

**单文件动作库** （小型数据集）：

.. code-block:: bash

   python protomotions/train_agent.py \
       --robot-name soma23 \
       --simulator isaacgym \
       --experiment-path examples/experiments/mimic/mlp.py \
       --experiment-name soma23_seed_bvh \
       --motion-file /path/to/seed_bvh_motions.pt \
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
       --robot-name soma23 \
       --simulator isaaclab \
       --experiment-path examples/experiments/mimic/mlp.py \
       --experiment-name soma23_seed_bvh_allchunks \
       --motion-file /path/to/output/chunk_slurmrank.pt \
       --ngpu 8 --nodes 3 \
       --num-envs 8192 \
       --batch-size 16384 \
       --training-max-steps 10000000000000 \
       --use-slurm --use-wandb

这会启动 24 张 GPU（3 节点 × 8 GPU），每张加载 15 个 chunk 中的一个
（通过 ``rank % 15`` 回绕）。每张 GPU 在自己的动作子集上训练，
从而将单 GPU 显存占用控制在合理范围内。

后续步骤
--------

* :doc:`kimodo_preparation` - 准备由 Kimodo 生成的动作
* :doc:`../tutorials/workflows/amass_smpl` - SMPL 训练工作流
