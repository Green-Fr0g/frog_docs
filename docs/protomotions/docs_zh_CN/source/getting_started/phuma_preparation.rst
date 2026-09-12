PHUMA 数据准备
==============

本指南介绍如何将原始 PHUMA 动作数据转换为 ProtoMotions 训练格式。

概述
----

转换管线将 PHUMA ``.npy`` 文件（根节点平移、根节点朝向、自由度（DOF）位置和帧率）
转换为包含完整刚体状态（位置、旋转、速度、接触）的 ProtoMotions ``.motion`` 文件。
随后这些文件会被打包成单个 ``.pt`` 动作库（MotionLib）文件，
以便高效训练。

.. code-block:: text

   PHUMA .npy files
        │
        ▼ (convert_phuma_to_proto.py)
   ProtoMotions .motion files
        │
        ▼ (motion_lib.py --motion-path)
   Packaged .pt MotionLib

前置条件
--------

下载 PHUMA 数据集
~~~~~~~~~~~~~~~~~

从 `DAVIAN-Robotics/PHUMA <https://huggingface.co/datasets/DAVIAN-Robotics/PHUMA>`_ 下载 PHUMA 数据集。

按以下步骤下载 PHUMA 数据集：

1. 克隆 `PHUMA <https://github.com/DAVIAN-Robotics/PHUMA>`_ 仓库，并按照 PHUMA 仓库中的安装说明操作。建议使用干净的 conda 环境。
2. 运行 `bash setup_phuma.sh`

与 huggingface 相关的错误可以通过运行以下命令解决：

.. code-block:: bash

   conda install -c conda-forge huggingface_hub

数据集会下载到 ``data/PHUMA/data`` 文件夹，其中包含针对两种人形的重定向数据：``g1`` 和 ``h1_2``。

快速上手：便捷脚本
------------------

如需一键完成，可以使用提供的便捷脚本，它会运行完整的转换和打包管线：

.. code-block:: bash

   cd /path/to/ProtoMotions
   python data/scripts/convert_phuma_to_motionlib.py <phuma_root_dir> <output_dir> \
        --humanoid-type <humanoid_type> \
        --motion-config <config1.yaml> [--motion-config <config2.yaml> ...]

**参数：**

* ``phuma_root_dir``：包含 PHUMA 子文件夹（含 ``g1`` 和 ``h1_2`` 文件夹）的根目录。
* ``output_dir``：存放打包后的 ``.pt`` 动作库文件的目录
* ``--motion-config``：包含动作配置的 YAML 文件。每个文件生成一个单独的 ``.pt`` 文件。可多次指定。
* ``--humanoid-type``：``g1`` 或 ``h1_2``。默认：``g1``
* ``--force-remake``：覆盖已存在的 ``.motion`` 文件
* ``--device``：打包时使用的设备（``cpu`` 或 ``cuda``）。默认：``cpu``


**示例：**

.. code-block:: bash

    # Use g1 humanoid
    python data/scripts/convert_phuma_to_motionlib.py /path/to/PHUMA/data /path/to/output \
        --humanoid-type g1 \
        --motion-config data/yaml_files/g1_phuma_train.yaml \
        --motion-config data/yaml_files/g1_phuma_val.yaml \
        --motion-config data/yaml_files/g1_phuma_unseen_video.yaml

    # Use h1_2 humanoid
    python data/scripts/convert_phuma_to_motionlib.py /path/to/PHUMA/data /path/to/output \
        --humanoid-type h1_2 \
        --motion-config data/yaml_files/h1_2_phuma_train.yaml \
        --motion-config data/yaml_files/h1_2_phuma_val.yaml \
        --motion-config data/yaml_files/h1_2_phuma_unseen_video.yaml

脚本会自动运行所有步骤，并输出最终的 MotionLib ``.pt`` 文件：

.. code-block:: text

    output/
       ├── g1_phuma_train.pt
       ├── g1_phuma_val.pt
       ├── g1_phuma_unseen_video.pt
       ├── h1_2_phuma_train.pt
       ├── h1_2_phuma_val.pt
       └── h1_2_phuma_unseen_video.pt

分步指南
--------

步骤 1：将 PHUMA 转换为 .motion 文件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

将 PHUMA ``.npy`` 文件转换为 ProtoMotions ``.motion`` 格式：

.. code-block:: bash

   # Convert the PHUMA data to ProtoMotions format for the g1 humanoid
   python data/scripts/convert_phuma_to_proto.py \
        /path/to/PHUMA/data \
        --humanoid-type g1 \
        --force-remake

   # Convert the PHUMA data to ProtoMotions format for the h1_2 humanoid
   python data/scripts/convert_phuma_to_proto.py \
        /path/to/PHUMA/data \
        --humanoid-type h1_2 \
        --force-remake

**参数：**

* ``phuma_root_dir``：包含 PHUMA 子文件夹（含 ``g1`` 和 ``h1_2`` 文件夹）的根目录。
* ``--output-dir``：存放 ``.motion`` 文件的目录。默认：``phuma_root_dir/data/humanoid_type``。
* ``--humanoid-type``：``g1`` 或 ``h1_2``。默认：``g1``
* ``--force-remake``：覆盖已存在的 ``.motion`` 文件


脚本做了什么：

1. 加载 PHUMA 数据：读取包含以下内容的 ``.npy`` 文件：

   - ``root_trans``：根节点平移（T, 3）
   - ``root_ori``：根节点朝向（T, 4），（x, y, z, w）格式
   - ``dof_pos``：自由度位置（T, 29）
   - ``fps``：每秒帧数

2. 将 PHUMA 数据转换为 ProtoMotions 格式：

   - 将四元数从 PHUMA 的（xyzw）格式转换为 MuJoCo 的（wxyz）格式
   - 构建 qpos：[root_pos(3), root_quat_wxyz(4), dof_pos(29)] = (T, 36)
   - 将 dof_pos 转换为张量
   - 执行正向运动学（FK），得到刚体位置和旋转
   - 通过有限差分计算 dof_vel
   - 基于位置和速度计算接触标签
   - 返回动作数据

3. 将动作数据保存到输出目录：

   - 将动作数据以 ``.motion`` 文件的形式保存到输出目录

步骤 2：将 .motion 文件打包为 .pt 动作库文件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

将 ``.motion`` 文件打包为 ``.pt`` 动作库文件：

.. note::
   YAML 配置文件中包含相对路径（例如 ``g1/animation/...``）。
   ``motion_lib.py`` 会以 YAML 文件所在目录为基准解析这些路径。
   因此，必须先把 YAML 文件复制到 PHUMA 数据目录中。

.. code-block:: bash

   # Package the g1 humanoid motion files into a .pt MotionLib file for the training set
   cp data/yaml_files/g1_phuma_train.yaml /path/to/PHUMA/data/
   python protomotions/components/motion_lib.py \
        --motion-path /path/to/PHUMA/data/g1_phuma_train.yaml \
        --output-file /path/to/g1_phuma_train.pt \
        --device cpu

   # Package the g1 humanoid motion files into a .pt MotionLib file for the validation set
   cp data/yaml_files/g1_phuma_val.yaml /path/to/PHUMA/data/
   python protomotions/components/motion_lib.py \
        --motion-path /path/to/PHUMA/data/g1_phuma_val.yaml \
        --output-file /path/to/g1_phuma_val.pt \
        --device cpu

   # Package the g1 humanoid motion files into a .pt MotionLib file for the unseen video set
   cp data/yaml_files/g1_phuma_unseen_video.yaml /path/to/PHUMA/data/
   python protomotions/components/motion_lib.py \
        --motion-path /path/to/PHUMA/data/g1_phuma_unseen_video.yaml \
        --output-file /path/to/g1_phuma_unseen_video.pt \
        --device cpu

**参数：**

* ``--motion-path``：列出待打包动作的 YAML 配置文件路径（或 ``.motion`` 文件目录）
* ``--output-file``：打包后 ``.pt`` 文件的输出路径
* ``--device``：使用的设备（``cpu`` 或 ``cuda``）


步骤 3：使用动作可视化工具验证
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

训练之前，使用动作可视化工具确认转换后的动作看起来正确：

.. code-block:: bash

   python examples/motion_libs_visualizer.py \
       --motion_files /path/to/g1_phuma_train.pt \
       --robot g1 \
       --simulator isaaclab

**控制按键：**

* **R**：切换到下一个动作
* **1/2**：提高/降低回放速度
* **3/4**：调整高亮显示的平滑度阈值

YAML 动作配置格式
-----------------

YAML 配置文件定义要包含哪些动作，并支持可选的时间切片和采样权重：

.. code-block:: yaml

   motions:
     - file: g1/animation/Ways_to_Stand_Winded_clip1_chunk_0000.motion
       fps: 30.0
       weight: 1.0
     - file: g1/animation/Ways_to_Sit_Buying_a_Chair_clip1_chunk_0000.motion
       fps: 30.0
       weight: 1.0
     - file: g1/animation/Ways_to_Open_a_Christmas_Gift_the_boss_clip1_chunk_0000.motion
       fps: 30.0
       weight: 1.0

字段：

* ``file``：动作文件路径（相对于 phuma_root_dir）
* ``fps``：原始动作采集帧率
* ``weight``：采样权重（越高表示训练时被采样得越频繁）

.. tip::
   标准 PHUMA g1 和 h1_2 的训练/验证/unseen_video 划分的现成 YAML 配置位于 ``data/yaml_files/``：

   * ``g1_phuma_train.yaml``
   * ``g1_phuma_val.yaml``
   * ``g1_phuma_unseen_video.yaml``
   * ``h1_2_phuma_train.yaml``
   * ``h1_2_phuma_val.yaml``
   * ``h1_2_phuma_unseen_video.yaml``


G1 与 H1-2
----------

* **G1**：29 关节（非根节点 28 个）。
* **H1-2**：27 关节（非根节点 26 个）。


使用动作库训练
--------------

打包完成后，即可在训练中使用：

.. code-block:: bash

   python protomotions/train_agent.py \
       --robot-name g1 \
       --simulator isaacgym \
       --experiment-path examples/experiments/mimic/mlp.py \
       --experiment-name g1_phuma \
       --motion-file /path/to/g1_phuma_train.pt \
       --num-envs 4096 \
       --batch-size 16384
