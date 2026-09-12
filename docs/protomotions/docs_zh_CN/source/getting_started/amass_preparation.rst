AMASS 数据准备
==============

本指南介绍如何将原始 AMASS 动作数据转换为 ProtoMotions 训练格式。

概述
----

转换管线将 AMASS ``.npz`` 文件（轴角姿态 + 根节点平移）
转换为包含完整刚体状态（位置、旋转、速度、接触）的 ProtoMotions ``.motion`` 文件。
随后这些文件会被打包成单个 ``.pt`` 动作库（MotionLib）文件，
以便高效训练。

.. code-block:: text

   AMASS .npz files
        │
        ▼ (convert_amass_to_proto.py)
   ProtoMotions .motion files
        │
        ▼ (motion_lib.py --motion-path)
   Packaged .pt MotionLib

前置条件
--------

1. **下载 AMASS**：在 `AMASS 网站 <https://amass.is.tue.mpg.de/>`_ 注册并下载
2. **SMPL/SMPL-X 模型**：身体模型转换所需（见下文）

下载 SMPL 身体模型
~~~~~~~~~~~~~~~~~~

从 `SMPL <https://smpl.is.tue.mpg.de/>`_ 和
`SMPL-X <https://smpl-x.is.tue.mpg.de/>`_ 下载身体模型。将其解压到 ``data/smpl/`` 文件夹。

**SMPL**：下载 **v1.1.0** 版本（包含中性模型）。重命名文件：

* ``basicmodel_neutral_lbs_10_207_0_v1.1.0.pkl`` → ``SMPL_NEUTRAL.pkl``
* ``basicmodel_m_lbs_10_207_0_v1.1.0.pkl`` → ``SMPL_MALE.pkl``
* ``basicmodel_f_lbs_10_207_0_v1.1.0.pkl`` → ``SMPL_FEMALE.pkl``

**SMPL-X**：下载 **v1.1** 版本。将文件重命名为 ``SMPLX_NEUTRAL.pkl``、
``SMPLX_MALE.pkl``、``SMPLX_FEMALE.pkl``。

文件结构应如下所示：

.. code-block:: text

   data/smpl/
     ├── SMPL_NEUTRAL.pkl
     ├── SMPL_MALE.pkl
     ├── SMPL_FEMALE.pkl
     ├── SMPLX_NEUTRAL.pkl   # Only needed for --humanoid-type smplx
     ├── SMPLX_MALE.pkl
     └── SMPLX_FEMALE.pkl

快速上手：便捷脚本
------------------

如需一键完成，可以使用提供的便捷脚本，它会运行完整的转换和打包管线：

.. code-block:: bash

   python data/scripts/convert_amass_to_motionlib.py <amass_root_dir> <output_dir> \
       --motion-config <config1.yaml> [--motion-config <config2.yaml> ...]

**参数：**

* ``amass_root_dir``：包含 AMASS 子文件夹（内含 ``.npz`` 文件）的根目录
* ``output_dir``：存放打包后的 ``.pt`` 动作库文件的目录
* ``--motion-config``：包含动作配置的 YAML 文件。每个文件生成一个单独的 ``.pt`` 文件。可多次指定。
* ``--humanoid-type``: ``smpl`` （24 关节）或 ``smplx`` （52 关节）。默认：``smpl``
* ``--output-fps``：动作文件的目标输出帧率（FPS）。默认：30
* ``--force-remake``：覆盖已存在的 ``.motion`` 文件
* ``--device``：打包时使用的设备（``cpu`` 或 ``cuda``）。默认：``cpu``

**示例：**

.. code-block:: bash

   # Create train/test/validation splits from YAML configs
   python data/scripts/convert_amass_to_motionlib.py /path/to/amass_root /path/to/output \
       --motion-config data/yaml_files/amass_smpl_train.yaml \
       --motion-config data/yaml_files/amass_smpl_test.yaml \
       --motion-config data/yaml_files/amass_smpl_validation.yaml

   # Use SMPL-X humanoid
   python data/scripts/convert_amass_to_motionlib.py /path/to/amass_root /path/to/output \
       --humanoid-type smplx \
       --motion-config data/yaml_files/amass_smplx_train.yaml

脚本会自动运行所有步骤，并输出最终的 MotionLib ``.pt`` 文件：

.. code-block:: text

   output/
     ├── amass_smpl_train.pt
     ├── amass_smpl_test.pt
     └── amass_smpl_validation.pt

分步指南
--------

步骤 1：将 AMASS 转换为 .motion 文件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

将 AMASS ``.npz`` 文件转换为 ProtoMotions ``.motion`` 格式：

.. code-block:: bash

   python data/scripts/convert_amass_to_proto.py \
       /path/to/amass_root \
       --humanoid-type smpl \
       --output-fps 30 \
       --motion-config data/yaml_files/amass_smpl_train.yaml \
       --motion-config data/yaml_files/amass_smpl_test.yaml \
       --motion-config data/yaml_files/amass_smpl_validation.yaml \
       --force-remake

**参数：**

* ``amass_root_dir``：包含 AMASS 子文件夹的根目录
* ``--humanoid-type``: ``smpl`` （24 关节）或 ``smplx`` （52 关节）
* ``--output-fps``：目标输出帧率（FPS）（默认：30）
* ``--force-remake``：覆盖已存在的转换结果文件
* ``--motion-config``：用于动作选择与切片的 YAML 文件。可多次指定。

``--motion-config`` YAML 文件定义了每个动作的起止时间。
这些时间段指定了每段原始 AMASS 录制中物理上合理的片段
（例如排除 T-pose 标定帧或有问题的段落）。

**脚本做了什么：**

1. **加载 AMASS 数据**：读取包含以下内容的 ``.npz`` 文件：

   * ``poses``：轴角格式的关节旋转
   * ``trans``：根节点平移
   * ``mocap_framerate``：原始采集帧率

2. **降采样**：找到源帧率中大于等于目标帧率的最大约数。
   例如，120 FPS 的源数据以 30 FPS 为目标时，每 4 帧取 1 帧。

3. **正向运动学（FK）**：计算完整的刚体状态：

   * 所有关节体（body）的世界坐标位置和旋转
   * 线速度和角速度（通过有限差分计算）
   * 自由度（DOF）位置和速度

4. **接触检测**：使用阈值标记地面接触：

   * 速度阈值：0.15 m/s
   * 高度阈值：0.1 m

5. **高度修正**：调整动作，使双脚既不穿透地面也不悬浮于地面上方。
   将整个动作垂直平移，使动作过程中最低的关节与脚尖偏移量
   （T-pose 下脚尖离地的高度）对齐：SMPL 为 0.015m，SMPL-X 为 0.017m。

步骤 2：打包为动作库
~~~~~~~~~~~~~~~~~~~~

将单个 ``.motion`` 文件打包为单个 ``.pt`` 文件。YAML 配置决定每个包中包含哪些动作：

.. code-block:: bash

   # Package training set
   python protomotions/components/motion_lib.py \
       --motion-path data/yaml_files/amass_smpl_train.yaml \
       --output-file /path/to/amass_smpl_train.pt \
       --device cpu

   # Package test set
   python protomotions/components/motion_lib.py \
       --motion-path data/yaml_files/amass_smpl_test.yaml \
       --output-file /path/to/amass_smpl_test.pt \
       --device cpu

**参数：**

* ``--motion-path``：列出待打包动作的 YAML 配置文件路径（或 ``.motion`` 文件目录）
* ``--output-file``：打包后 ``.pt`` 文件的输出路径
* ``--device``：使用的设备（``cpu`` 或 ``cuda``）

YAML 配置指定了每个划分（训练/测试/验证）包含哪些动作，
因此每个配置需要运行一次本步骤，生成单独的 ``.pt`` 文件。

**为什么要打包？** 虽然可以直接从 YAML 文件加载动作，但打包会把数据集预先处理一次并保存为单个 ``.pt`` 文件。
这样后续加载会快得多，因为动作无需每次重新处理。

**输出：**

.. code-block:: text

   Loading motions from yaml/npy file or Directory of motions which is slower
   Loaded 1234 motions with a total length of 12345.6s.
   Motion library saved to amass_train.pt

步骤 3：使用动作可视化工具验证
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

训练之前，使用动作可视化工具确认转换后的动作看起来正确：

.. code-block:: bash

   python examples/motion_libs_visualizer.py \
       --motion_files /path/to/amass_smpl_train.pt \
       --robot smpl \
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
     - file: CMU/45/45_01_poses.motion
       fps: 120.0
       weight: 1.0
       sub_motions:
         - timings:
             start: 0.0
             end: 3.8
     - file: CMU/138/138_06_poses.motion
       fps: 120.0
       weight: 2.0  # Sample this motion twice as often
       sub_motions:
         - timings:
             start: 0.5
             end: 3.0

**字段：**

* ``file``：动作文件路径（相对于 amass_root_dir）
* ``fps``：原始动作采集帧率
* ``weight``：采样权重（越高表示训练时被采样得越频繁）
* ``sub_motions``：要提取的时间片段列表
* ``timings.start``：起始时间（秒）
* ``timings.end``：结束时间（秒）

.. tip::

   标准 AMASS 训练/测试/验证划分的现成 YAML 配置位于 ``data/yaml_files/``：

   * ``amass_smpl_train.yaml``
   * ``amass_smpl_test.yaml``
   * ``amass_smpl_validation.yaml``
   * ``amass_smplx_train.yaml``
   * ``amass_smplx_test.yaml``
   * ``amass_smplx_validation.yaml``

SMPL 与 SMPL-X
--------------

* **SMPL**：24 关节（非根节点 23 个）。身体模型较简单。
* **SMPL-X**：52 关节（非根节点 51 个）。包含带手指的手部。

当 ``.npz`` 文件中没有帧率信息时，SMPL-X 会从 ``data/yaml_files/motion_fps_amassx.yaml``
加载 FPS 信息。

使用动作库训练
--------------

打包完成后，即可在训练中使用：

.. code-block:: bash

   python protomotions/train_agent.py \
       --robot-name smpl \
       --simulator isaacgym \
       --experiment-path examples/experiments/mimic/mlp.py \
       --experiment-name smpl_amass \
       --motion-file /path/to/amass_train.pt \
       --num-envs 4096 \
       --batch-size 16384

使用分片动作库进行多 GPU 训练
-----------------------------

对于非常大的数据集，可以将动作库分片到多张 GPU 上。用 ``*_slurmrank.pt``
模式为文件命名：

.. code-block:: text

   amass_0.pt  # Loaded by rank 0
   amass_1.pt  # Loaded by rank 1
   amass_2.pt  # Loaded by rank 2
   amass_3.pt  # Loaded by rank 3

将 ``amass_slurmrank.pt`` 用作动作文件路径，每个 rank 会自动加载对应的分片。

故障排查
--------

**SMPL-X 文件缺少 FPS**：确认 ``data/yaml_files/motion_fps_amassx.yaml``
中包含你的动作的 FPS 条目。

**内存不足**：只处理动作的子集，或使用 ``--device cpu``。

**动作看起来不对**：确认人形类型与你的 AMASS 下载版本匹配
（SMPL 还是 SMPL-X）。

后续步骤
--------

* :doc:`../tutorials/workflows/amass_smpl` - 完整的 SMPL 训练工作流
* :doc:`../tutorials/workflows/retargeting_pyroki` - 将动作重定向到机器人
