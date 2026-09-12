Kimodo 生成动作的准备
=====================

本指南介绍如何将
`Kimodo <https://research.nvidia.com/labs/sil/projects/kimodo/>`_ （NVIDIA 的文本生成动作模型）
生成的动作转换为基于物理仿真可用的 ProtoMotions 格式。

概述
----

Kimodo 可以根据文本提示生成两种骨架格式的动作：

* **SOMA 骨架** （77 关节）：以 ``.npz`` 文件输出，30 fps
* **G1 骨架**：Unitree G1 机器人，以 ``.csv`` 文件输出，30 fps

两种格式都可以转换为 ProtoMotions ``.motion`` 文件，并打包为
动作库（MotionLib）``.pt`` 文件用于训练。

.. code-block:: text

   Kimodo text-to-motion generation
        │
        ├── SOMA skeleton (.npz)  ──▶  convert_soma23_npz_to_proto.py
        │                                    │
        └── G1 skeleton (.csv)    ──▶  convert_g1_csv_to_proto.py
                                             │
                                             ▼
                                    ProtoMotions .motion files
                                             │
                                             ▼ (motion_lib.py)
                                    Packaged .pt MotionLib

SOMA 骨架动作（.npz）
---------------------

Kimodo 以 ``.npz`` 文件生成 SOMA 格式的动作，包含以下字段：

* ``local_rot_mats``：``(T, 77, 3, 3)`` —— 完整 SOMA 骨架的局部旋转矩阵
* ``posed_joints``：``(T, 77, 3)`` —— 全局关节位置（索引 0 为根节点位置）
* ``foot_contacts``：``(T, 4)`` —— 脚部接触标签（可选）

转换器会从 77 个关节中筛选出 MJCF 中的 23 个受驱动关节，
丢弃手部、手指细节、面部关节和脚趾末端。

.. note::

   仓库中包含一个 Kimodo 生成的 SOMA ``.npz`` 示例文件，位于
   ``data/soma-kimodo-generated/``，这样无需自己运行 Kimodo
   也能体验整条管线。

**转换一个 NPZ 文件目录：**

.. code-block:: bash

   python data/scripts/convert_soma23_npz_to_proto.py \
       --input-dir data/soma-kimodo-generated/ \
       --output-dir data/soma-kimodo-generated/proto \
       --input-fps 30 \
       --output-fps 30

**关键参数：**

* ``--input-dir``：包含 ``.npz`` 文件的目录（扁平结构，不递归）
* ``--output-dir``：保存 ``.motion`` 文件的目录
* ``--input-fps``：生成帧率（默认：30）
* ``--output-fps``：目标输出帧率（默认：30）
* ``--ignore-motion-filter``：跳过质量过滤
* ``--force-remake``：覆盖已存在的文件

所有转换器还会基于高度和速度阈值，为每个 body 计算启发式的地面接触标签。
这些标签在训练中被某些奖励函数和观测使用
（例如接触感知的跟踪奖励）。

**打包并验证：**

.. code-block:: bash

   # Package
   python protomotions/components/motion_lib.py \
       --motion-path data/soma-kimodo-generated/proto/ \
       --output-file data/soma-kimodo-generated/kimodo_soma_motions.pt

   # Visualize
   python examples/motion_libs_visualizer.py \
       --motion_files data/soma-kimodo-generated/kimodo_soma_motions.pt \
       --robot soma23 \
       --simulator isaacgym

G1 骨架动作（.csv）
-------------------

Kimodo 和 `ARDY <https://github.com/nv-tlabs/ardy>`_ 可以为
Unitree G1 骨架生成 CSV 格式的动作。两者的约定与 BONES-SEED 重定向的 CSV 不同：
位置单位为米，根节点朝向为 wxyz 四元数，关节角度为弧度，
且没有表头行和帧索引列。Kimodo 以 30 fps 生成动作，而 ARDY 以
25 fps 生成动作。

.. note::

   ``data/g1-kimodo-generated/`` 中包含 Kimodo 生成的 G1 CSV 示例和已转换好的 ``.motion`` 文件，可以直接体验管线。
   它们也正是 Kimodo 首页展示真机 G1 部署的同一批动作。

**转换一个 Kimodo CSV 文件目录：**

.. code-block:: bash

   python data/scripts/convert_g1_csv_to_proto.py \
       --input-dir data/g1-kimodo-generated/ \
       --output-dir data/g1-kimodo-generated/proto \
       --input-fps 30 \
       --output-fps 30 \
       --pos-units m \
       --rot-format quat_wxyz \
       --joint-units rad \
       --no-has-header \
       --no-has-frame-column \
       --force-remake

**转换一个 ARDY CSV 文件目录：**

将 ARDY 生成的 G1 CSV 文件放在 ``data/g1-ardy-generated/`` 下，然后运行：

.. code-block:: bash

   python data/scripts/convert_g1_csv_to_proto.py \
       --input-dir data/g1-ardy-generated/ \
       --output-dir data/g1-ardy-generated/proto \
       --input-fps 25 \
       --output-fps 25 \
       --pos-units m \
       --rot-format quat_wxyz \
       --joint-units rad \
       --no-has-header \
       --no-has-frame-column \
       --force-remake

**打包并验证：**

.. code-block:: bash

   # Package Kimodo motions
   python protomotions/components/motion_lib.py \
       --motion-path data/g1-kimodo-generated/proto/ \
       --output-file data/g1-kimodo-generated/kimodo_g1_motions.pt

   # Package ARDY motions
   python protomotions/components/motion_lib.py \
       --motion-path data/g1-ardy-generated/proto/ \
       --output-file data/g1-ardy-generated/ardy_g1_motions.pt

   # Visualize ARDY motions
   python examples/motion_libs_visualizer.py \
       --motion_files data/g1-ardy-generated/ardy_g1_motions.pt \
       --robot g1 \
       --simulator isaacgym

示例：从文本到基于物理的动作
----------------------------

使用 G1 机器人的典型端到端工作流：

1. 用 Kimodo 或 ARDY 根据文本提示**生成**动作
2. **转换** 为 ProtoMotions 格式
3. **打包** 为动作库 ``.pt`` 文件
4. **训练** 基于物理的策略来跟踪生成的动作
5. 将策略**部署**到真实机器人或在仿真中测试

.. code-block:: bash

   # Step 1: Generate with Kimodo or ARDY (see the respective generator docs)
   # Kimodo output: kimodo_output/*.csv (G1 skeleton, 30 fps)
   # ARDY output: data/g1-ardy-generated/*.csv (G1 skeleton, 25 fps)
   # This example uses Kimodo; see the ARDY conversion command above.

   # Step 2: Convert (Kimodo G1 CSV format)
   python data/scripts/convert_g1_csv_to_proto.py \
       --input-dir data/g1-kimodo-generated/ \
       --output-dir data/g1-kimodo-generated/proto \
       --input-fps 30 --output-fps 30 \
       --pos-units m --rot-format quat_wxyz --joint-units rad \
       --no-has-header --no-has-frame-column --force-remake

   # Step 3: Package
   python protomotions/components/motion_lib.py \
       --motion-path data/g1-kimodo-generated/proto/ \
       --output-file data/g1-kimodo-generated/kimodo_g1_motions.pt

   # Step 4: Train
   python protomotions/train_agent.py \
       --robot-name g1 \
       --simulator isaacgym \
       --experiment-path examples/experiments/mimic/mlp.py \
       --experiment-name kimodo_g1 \
       --motion-file data/g1-kimodo-generated/kimodo_g1_motions.pt \
       --num-envs 4096 \
       --batch-size 16384

   # Step 5: Test in simulation / deploy to real robot
   python protomotions/inference_agent.py \
       --checkpoint results/kimodo_g1/last.ckpt \
       --simulator isaacgym --num-envs 16

   # For real robot deployment, see the G1 Deployment guide:
   # https://protomotions.github.io/tutorials/workflows/g1_deployment.html

支持的骨架格式
--------------

.. list-table::
   :header-rows: 1
   :widths: 20 20 15 20 25

   * - 来源
     - 格式
     - 关节
     - 转换器
     - ProtoMotions 机器人
   * - Kimodo SOMA
     - ``.npz``
     - 77
     - ``convert_soma23_npz_to_proto.py``
     - ``soma23``
   * - Kimodo / ARDY G1
     - ``.csv``
     - 29 个自由度
     - ``convert_g1_csv_to_proto.py``
     - ``g1``
   * - BONES-SEED BVH
     - ``.bvh``
     - 77
     - ``convert_soma23_bvh_to_proto.py``
     - ``soma23``
   * - BONES-SEED G1 CSV
     - ``.csv``
     - 29 个自由度
     - ``convert_g1_csv_to_proto.py``
     - ``g1``

后续步骤
--------

* :doc:`../tutorials/workflows/g1_deployment` - 将训练好的 G1 策略部署到真实硬件
* :doc:`seed_bvh_preparation` - 准备 BONES-SEED BVH 数据
* :doc:`seed_g1_csv_preparation` - 准备 BONES-SEED G1 CSV 数据
* :doc:`amass_preparation` - 为 SMPL 人形准备 AMASS 数据
