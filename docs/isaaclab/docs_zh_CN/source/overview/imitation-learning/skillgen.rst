.. _skillgen:

用于自动生成演示数据的 SkillGen
===============================================

SkillGen 是一种先进的演示数据生成系统，它通过集成运动规划来增强 Isaac Lab Mimic。它通过将人工提供的子任务片段与自动运动规划相结合，生成高质量、自适应、无碰撞的机器人演示数据。

什么是 SkillGen？
~~~~~~~~~~~~~~~~~

SkillGen 解决了传统演示数据生成中的几个关键局限：

* **运动质量** ：使用 cuRobo 的 GPU 加速运动规划器生成平滑、无碰撞的轨迹
* **有效性** ：在技能片段之间生成运动学上可行的规划
* **多样性** ：通过可配置的采样和规划参数生成多样化的演示数据
* **适应性** ：生成的演示数据可在数据生成期间适配新的物体摆放和场景配置

该系统的工作方式是：获取人工标注的人类演示数据，提取局部的子任务技能（参见 `SkillGen 中的子任务`_ ），然后使用 cuRobo 在这些技能片段之间规划可行的运动，同时遵循机器人运动学和碰撞约束。

前提条件
~~~~~~~~~~~~~

在使用 SkillGen 之前，您必须了解：

1. **遥操作** ：如何使用键盘、SpaceMouse 或手部追踪来控制机器人并录制演示数据
2. **Isaac Lab Mimic** ：完整的工作流，包括数据收集、标注、生成和策略训练

.. important::

   在继续使用 SkillGen 之前，请仔细阅读 :ref:`teleoperation-imitation-learning` 文档。

.. _skillgen-installation:

安装
~~~~~~~~~~~~

SkillGen 需要 Isaac Lab、Isaac Sim 和 cuRobo。请在您的 Isaac Lab conda 环境中按照以下步骤操作。

步骤 1：安装并验证 Isaac Sim 和 Isaac Lab
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

官方的 Isaac Sim 和 Isaac Lab 安装指南请参见 `此处 <https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/pip_installation.html#installing-isaac-lab>`__ 。

步骤 2：安装 cuRobo
^^^^^^^^^^^^^^^^^^^^^^

cuRobo 为 SkillGen 提供运动规划能力。此安装已验证可与 Isaac Lab 的 PyTorch 和 CUDA 依赖要求协同工作：

.. code:: bash

   # One line installation of cuRobo (formatted for readability)
   conda install -c nvidia cuda-toolkit=12.8 -y && \
   export CUDA_HOME="$CONDA_PREFIX" && \
   export PATH="$CUDA_HOME/bin:$PATH" && \
   export LD_LIBRARY_PATH="$CUDA_HOME/lib:$LD_LIBRARY_PATH" && \
   export TORCH_CUDA_ARCH_LIST="8.0+PTX" && \
   pip install -e "git+https://github.com/NVlabs/curobo.git@ebb71702f3f70e767f40fd8e050674af0288abe8#egg=nvidia-curobo" --no-build-isolation

.. note::
   * commit 哈希 ``ebb71702f3f70e767f40fd8e050674af0288abe8`` 已针对 Isaac Lab 进行过测试——使用其他版本可能会导致兼容性问题。该 commit 支持四边面网格三角剖分，这是 cuRobo 将 USD 解析为碰撞对象所必需的。

   * cuRobo 从源码安装并采用可编辑（editable）方式安装。这意味着 cuRobo 源代码将被克隆到当前目录下的 ``src/nvidia-curobo`` 中。用户可以选择自己的工作目录来安装 cuRobo。

   * 上述命令中的 ``TORCH_CUDA_ARCH_LIST`` 应与您 GPU 的 CUDA 算力相匹配（例如 A100 为 ``8.0`` ，许多 RTX 30 系列为 ``8.6`` ，RTX 4090 为 ``8.9`` ）； ``+PTX`` 后缀嵌入了用于前向兼容的 PTX，以便在未包含原生 SASS 时，较新的 GPU 可以进行 JIT 编译。

.. warning::

   **如果在 source 了 Isaac Sim 环境脚本的情况下安装，cuRobo 可能会失败**

   source Omniverse Kit/Isaac Sim 环境脚本（例如 ``setup_conda_env.sh`` ）会为 Kit 运行时及其预捆绑的 Python 包导出 ``PYTHONHOME`` 和 ``PYTHONPATH`` 。在安装 cuRobo 期间，这可能导致 ``conda`` 在初始化之前导入 Omniverse 捆绑的库（例如 ``requests``/``urllib3`` ），从而导致崩溃（常见表现为引用 ``omni.kit.pip_archive`` 的 ``TypeError`` ）。

   请执行以下操作之一：

   - 在未 source 任何 Omniverse/Isaac Sim 脚本的干净 shell 中安装 cuRobo。
   - 在调用 Conda 之前，临时重置或忽略继承的 Python 环境变量（尤其是 ``PYTHONPATH`` 和 ``PYTHONHOME`` ），以免 Kit 的 Python 遮蔽您的 Conda 环境。
   - 使用不依赖 shell 激活的 Conda 机制，避免继承当前 shell 的 Python 变量。

   安装完成后，您可以重新 source Isaac Lab/Isaac Sim 脚本以正常使用。



步骤 3：安装 Rerun
^^^^^^^^^^^^^^^^^^^^^

用于开发过程中的轨迹可视化：

.. code:: bash

   pip install rerun-sdk==0.23

.. note::

   **Rerun 可视化设置：**

   * Rerun 是可选的，但强烈建议在开发过程中使用它来调试和验证规划出的轨迹
   * 通过在 cuRobo 规划器配置中设置 ``visualize_plan = True`` 来启用轨迹可视化
   * 启用后，cuRobo 规划器接口会将规划出的末端执行器轨迹、路径点和碰撞数据流式传输到 Rerun，以便进行交互式检查
   * 可视化有助于在完整数据集生成之前发现规划问题、碰撞问题和轨迹平滑度问题
   * 也可以配合 ``--headless`` 运行，以禁用 isaacsim 可视化，但仍可对末端执行器轨迹进行可视化和调试

步骤 4：验证安装
^^^^^^^^^^^^^^^^^^^^^^^^^^^

测试 cuRobo 是否能与 Isaac Lab 协同工作：

.. code:: bash

   # This should run without import errors
   python -c "import curobo; print('cuRobo installed successfully')"

.. tip::

   如果遇到 ``libstdc++.so.6: version 'GLIBCXX_3.4.30' not found`` 错误，可以尝试以下命令来修复：

   .. code:: bash

      conda config --env --set channel_priority strict
      conda config --env --add channels conda-forge
      conda install -y -c conda-forge "libstdcxx-ng>=12" "libgcc-ng>=12"

下载 SkillGen 数据集
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

我们提供了一个预先标注好的数据集，帮助您快速上手 SkillGen。

数据集内容
^^^^^^^^^^^^^^^^

该数据集包含：

* Franka 机械臂立方体堆叠的人类演示数据
* 每条演示数据的人工标注子任务边界
* 同时兼容基础立方体堆叠和自适应料箱立方体堆叠任务

下载与设置
^^^^^^^^^^^^^^^^^^

1. 点击 `此处 <https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.0/Isaac/IsaacLab/Mimic/franka_stack_datasets/annotated_dataset_skillgen.hdf5>`__ 下载预先标注好的数据集。

2. 准备 datasets 目录并移动下载的文件：

.. code:: bash

   # Make sure you are in the root directory of your Isaac Lab workspace
   cd /path/to/your/IsaacLab

   # Create the datasets directory if it does not exist
   mkdir -p datasets

   # Move the downloaded dataset into the datasets directory
   mv /path/to/annotated_dataset_skillgen.hdf5 datasets/annotated_dataset_skillgen.hdf5

.. tip::

   SkillGen 的一大优势是，同一份标注数据集可以在多个相关任务之间复用（例如基础堆叠和自适应料箱堆叠）。这避免了为每个任务变体重新收集和标注数据。

.. admonition:: {本教程中任务的可选步骤} 收集全新的数据集（原始 + 标注）

      如果您想收集一份全新的原始数据集，然后为 SkillGen 创建标注数据集，请按照以下命令操作。用户应已了解 Isaac Lab Mimic 工作流。

   **开始之前的重要提示**

   * 使用提供的标注数据集是开始本教程中 SkillGen 任务的最快途径。
   * 如果您创建自己的数据集，SkillGen 需要人工标注子任务的开始和终止边界（不支持自动标注）。
   * 开始边界信号对 SkillGen 是必需的；请在标注时使用 ``--annotate_subtask_start_signals`` ，否则数据生成将失败。
   * 保持您的子任务定义（ ``object_ref`` 、 ``subtask_term_signal`` ）与 SkillGen 环境配置一致。

   **录制演示数据** （支持任何遥操作设备；如有需要可替换 ``spacemouse`` ）：

   .. code:: bash

      ./isaaclab.sh -p scripts/tools/record_demos.py \
      --task Isaac-Stack-Cube-Franka-IK-Rel-Skillgen-v0 \
      --teleop_device spacemouse \
      --dataset_file ./datasets/dataset_skillgen.hdf5 \
      --num_demos 10

   **为 SkillGen 标注演示数据** （同时写入终止和开始边界）：

   .. code:: bash

      ./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/annotate_demos.py \
      --device cpu \
      --task Isaac-Stack-Cube-Franka-IK-Rel-Skillgen-v0 \
      --input_file ./datasets/dataset_skillgen.hdf5 \
      --output_file ./datasets/annotated_dataset_skillgen.hdf5 \
      --annotate_subtask_start_signals

理解数据集标注
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SkillGen 要求数据集包含已标注的子任务开始和终止边界。不支持自动标注。

SkillGen 中的子任务
^^^^^^^^^^^^^^^^^^^^

**技术定义：** 子任务是完成某个操作目标的连续演示片段，通过 ``SubTaskConfig`` 定义：

* ``object_ref`` ：用作该子任务空间参考的物体（或 ``None`` ）
* ``subtask_term_signal`` ：二值终止信号的名称（子任务完成时从 0 变为 1）
* ``subtask_start_signal`` ：二值开始信号的名称（子任务开始时从 0 变为 1；SkillGen 必需）

子任务定位过程包括：

* 检测信号跳变点（从 0 变为 1）以确定子任务边界 ``[t_start, t_end]`` ；
* 提取边界之间的子任务片段；
* 在物体相对或任务相对的坐标系中计算末端执行器轨迹和关键位姿（如果提供了 ``object_ref`` 则使用它）；

这将绝对的、与场景相关的运动转换为物体相对的技能片段，这些片段可以在数据生成期间适配新的物体摆放和场景配置。

人工标注工作流
^^^^^^^^^^^^^^^^^^^^^^^^^^
与 Isaac Lab Mimic 工作流不同，SkillGen 需要人工标注子任务的开始和终止边界。例如，对于抓取立方体，开始信号位于夹爪闭合之前，终止信号位于物体被抓取之后。您可以调整开始和终止信号以适应您的子任务定义。

.. tip::

   **人工标注控制按键：**

   * 按 ``N`` 开始/继续播放
   * 按 ``B`` 暂停
   * 按 ``S`` 标记子任务边界
   * 按 ``Q`` 跳过当前演示数据

   在为技能片段（例如抓取、堆叠等）标注开始和结束信号时，先使用 ``B`` 在技能开始前几步暂停，使用 ``S`` 标注开始信号，然后使用 ``N`` 继续播放。技能完成后，稍过几步再次暂停，使用 ``S`` 标注结束信号。

使用 SkillGen 生成数据
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SkillGen 使用运动规划将标注好的演示数据转化为多样化、高质量的数据集。

SkillGen 的工作原理
^^^^^^^^^^^^^^^^^^^^^^

SkillGen 流水线使用您的标注数据集和环境的 Mimic API 来合成新的演示数据：

1. **子任务边界的使用** ：从标注数据集中读取每个子任务的开始和终止索引
2. **目标采样** ：根据任务约束和数据生成配置为每个子任务采样目标位姿
3. **轨迹规划** ：使用 cuRobo 在子任务片段之间规划无碰撞运动（当使用 ``--use_skillgen`` 时）
4. **轨迹拼接** ：将技能片段和规划出的轨迹拼接成完整的演示数据。
5. **成功评估** ：验证任务成功条件；只有成功的尝试才会写入输出数据集

使用参数
^^^^^^^^^^^^^^^^

SkillGen 数据生成的关键参数：

* ``--use_skillgen`` ：启用 SkillGen 规划器（必需）
* ``--generation_num_trials`` ：要生成的演示数据数量
* ``--num_envs`` ：并行环境数量（根据 GPU 内存调整）
* ``--device`` ：计算设备（cpu/cuda）。为获得稳定的物理效果请使用 cpu
* ``--headless`` ：禁用可视化以加快生成速度

.. _task-basic-cube-stacking:

任务 1：基础立方体堆叠
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

为标准的 Isaac Lab Mimic 立方体堆叠任务生成演示数据。在该任务中，Franka 机器人必须：

1. 拿起红色立方体并将其放到蓝色立方体上
2. 拿起绿色立方体并将其放到红色立方体上
3. 最终堆叠顺序：蓝色（底部）、红色（中层）、绿色（顶部）。

.. figure:: https://download.isaacsim.omniverse.nvidia.com/isaaclab/images/cube_stack_data_gen_skillgen.gif
   :width: 75%
   :align: center
   :alt: Cube stacking task generated with SkillGen
   :figclass: align-center

   立方体堆叠数据集示例。

小规模生成
^^^^^^^^^^^^^^^^^^^^^^

先用小数据集验证一切正常：

.. code:: bash

   ./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \
   --device cpu \
   --num_envs 1 \
   --generation_num_trials 10 \
   --input_file ./datasets/annotated_dataset_skillgen.hdf5 \
   --output_file ./datasets/generated_dataset_small_skillgen_cube_stack.hdf5 \
   --task Isaac-Stack-Cube-Franka-IK-Rel-Skillgen-v0 \
   --use_skillgen

全量生成
^^^^^^^^^^^^^^^^^^^^^

小规模结果满意后，生成完整的训练数据集：

.. code:: bash

   ./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \
   --device cpu \
   --headless \
   --num_envs 1 \
   --generation_num_trials 1000 \
   --input_file ./datasets/annotated_dataset_skillgen.hdf5 \
   --output_file ./datasets/generated_dataset_skillgen_cube_stack.hdf5 \
   --task Isaac-Stack-Cube-Franka-IK-Rel-Skillgen-v0 \
   --use_skillgen

.. note::

   * 使用 ``--headless`` 禁用可视化以加快生成速度。在启用 ``--headless`` 的同时，还可以在 cuRobo 规划器配置中设置 ``visualize_plan = True`` 来启用 Rerun 可视化，以便进行调试。
   * 根据 GPU 内存调整 ``--num_envs`` （从 1 开始，逐步增加）。当 num_envs 大于 1 时，性能提升并不显著。对大多数 GPU 而言，5 似乎是在 cuRobo 实例与仿真环境之间平衡性能和内存占用的最佳值。
   * 生成时间：在 RTX 6000 Ada GPU 上，启用 ``--headless`` 时，单个环境生成 1000 条演示数据约需 90 到 120 分钟。时间取决于 GPU、环境数量以及演示数据的成功率（后者取决于标注数据集的质量）。
   * cuRobo 规划器接口和配置在 :ref:`cuRobo-interface-features` 中有描述。

.. _task-bin-cube-stacking:

任务 2：料箱中的自适应立方体堆叠
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SkillGen 还可用于为自适应任务生成数据集。在本示例中，我们为狭窄料箱中的自适应立方体堆叠生成数据集。料箱以固定的位置和朝向放置在工作区中，一个蓝色立方体放置在料箱中央。机器人必须在不与料箱发生碰撞的情况下，生成将红色和绿色立方体堆叠到蓝色立方体上的成功演示数据。

.. figure:: https://download.isaacsim.omniverse.nvidia.com/isaaclab/images/bin_cube_stack_data_gen_skillgen.gif
   :width: 75%
   :align: center
   :alt: Adaptive bin cube stacking task generated with SkillGen
   :figclass: align-center

   自适应料箱堆叠数据生成示例。

小规模生成
^^^^^^^^^^^^^^^^^^^^^^

测试自适应堆叠设置：

.. code:: bash

   ./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \
   --device cpu \
   --num_envs 1 \
   --generation_num_trials 10 \
   --input_file ./datasets/annotated_dataset_skillgen.hdf5 \
   --output_file ./datasets/generated_dataset_small_skillgen_bin_cube_stack.hdf5 \
   --task Isaac-Stack-Cube-Bin-Franka-IK-Rel-Mimic-v0 \
   --use_skillgen

全量生成
^^^^^^^^^^^^^^^^^^^^^

生成完整的自适应堆叠数据集：

.. code:: bash

   ./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \
   --device cpu \
   --headless \
   --num_envs 1 \
   --generation_num_trials 1000 \
   --input_file ./datasets/annotated_dataset_skillgen.hdf5 \
   --output_file ./datasets/generated_dataset_skillgen_bin_cube_stack.hdf5 \
   --task Isaac-Stack-Cube-Bin-Franka-IK-Rel-Mimic-v0 \
   --use_skillgen

.. warning::

   自适应任务通常成功率较低且数据生成时间更长，这是因为复杂度增加。与基础立方体堆叠相比，由于成功率较低且规划问题更困难，生成数据集所需的时间也更长。

.. note::

   如果使用预先标注的数据集，并在启用 ``--headless`` 的情况下运行数据生成命令，在 RTX 6000 Ada GPU 上为单个环境生成 1000 条演示数据通常需要约 220 分钟。

.. note::

   **显存占用与 GPU 建议**

   以下数据是在 RTX 6000 Ada 上生成 10 条演示数据时测得的：
    * 基础立方体堆叠（Vanilla Cube Stacking）：1 个环境稳定状态约 9.3–9.6 GB；5 个环境稳定状态约 21.8–22.2 GB（初始化期间会短暂更高）。
    * 自适应料箱立方体堆叠（Adaptive Bin Cube Stacking）：1 个环境稳定状态约 9.3–9.6 GB；5 个环境稳定状态约 22.0–22.3 GB（初始化期间会短暂更高）。
    * 最低 GPU 建议： ``--num_envs`` 为 1–2 时需要 ≥24 GB 显存； ``--num_envs`` 最多到约 5 时需要 ≥48 GB 显存。
    * 要降低显存占用：建议使用 ``--headless`` 并保持 ``--num_envs`` 适中。具体数值会随场景资产和演示数据数量而变化。

从 SkillGen 数据学习策略
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

与 Isaac Lab Mimic 工作流类似，您可以使用 Robomimic 基于生成的 SkillGen 数据集训练模仿学习策略。

基础立方体堆叠策略
^^^^^^^^^^^^^^^^^^^^^^^^^^^

为基础立方体堆叠任务训练基于状态的策略：

.. code:: bash

   ./isaaclab.sh -p scripts/imitation_learning/robomimic/train.py \
   --task Isaac-Stack-Cube-Franka-IK-Rel-Skillgen-v0 \
   --algo bc \
   --dataset ./datasets/generated_dataset_skillgen_cube_stack.hdf5

自适应料箱立方体堆叠策略
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

为更复杂的自适应料箱堆叠训练策略：

.. code:: bash

   ./isaaclab.sh -p scripts/imitation_learning/robomimic/train.py \
   --task Isaac-Stack-Cube-Bin-Franka-IK-Rel-Mimic-v0 \
   --algo bc \
   --dataset ./datasets/generated_dataset_skillgen_bin_cube_stack.hdf5

.. note::

   训练脚本会将模型检查点保存在 ``IssacLab/logs/robomimic`` 下的 model 目录中。

评估训练好的策略
^^^^^^^^^^^^^^^^^^^^^^^^^^^

测试您训练好的策略：

.. code:: bash

   # Basic cube stacking evaluation
   ./isaaclab.sh -p scripts/imitation_learning/robomimic/play.py \
   --device cpu \
   --task Isaac-Stack-Cube-Franka-IK-Rel-Skillgen-v0 \
   --num_rollouts 50 \
   --checkpoint /path/to/model_checkpoint.pth

.. code:: bash

   # Adaptive bin cube stacking evaluation
   ./isaaclab.sh -p scripts/imitation_learning/robomimic/play.py \
   --device cpu \
   --task Isaac-Stack-Cube-Bin-Franka-IK-Rel-Mimic-v0 \
   --num_rollouts 50 \
   --checkpoint /path/to/model_checkpoint.pth

.. note::

   **立方体堆叠和料箱立方体堆叠任务的预期成功率与建议**

   * SkillGen 数据生成和下游策略的成功率对任务和数据集标注质量非常敏感，可能表现出较大的方差。
   * 对于立方体堆叠和料箱立方体堆叠任务，如果数据集按照说明正确标注，数据生成成功率通常为 40% 到 70%。
   * 使用 1000 条生成的演示数据训练 2000 个周期（默认值）后，行为克隆（BC）策略在这些任务上的成功率通常为 40% 到 85%，具体取决于数据质量。
   * 在 RTX 6000 Ada GPU 上，使用 1000 条演示数据训练 2000 个周期大约需要 30 到 35 分钟。训练时间随演示数据数量和周期数的增加而增长。
   * 关于数据集生成时间，请参见 :ref:`task-basic-cube-stacking` 和 :ref:`task-bin-cube-stacking` 。
   * 建议：使用约 1000 条生成的演示数据训练默认的 2000 个周期，并评估在第 1000 个周期之后保存的多个检查点，以选择表现最佳的策略。

.. _cuRobo-interface-features:

cuRobo 接口特性
~~~~~~~~~~~~~~~~~~~~~~~~~

本节总结 cuRobo 规划器接口及其特性。SkillGen 流水线使用 cuRobo 规划器在子任务片段之间生成无碰撞运动。不过，用户也可以将 cuRobo 作为独立的运动规划器用于自己的任务。用户还可以通过继承基础运动规划器并实现相同的 API 来实现自己的运动规划器。

基础运动规划器（可扩展）
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* 位置： ``isaaclab_mimic/motion_planners/base_motion_planner.py``
* 用途：为 SkillGen 使用的所有运动规划器提供统一接口
* 可扩展性：可以通过继承并实现相同的 API 来添加新的规划器；SkillGen 无需修改代码即可使用该 API

cuRobo 规划器（GPU，具备碰撞感知）
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* 位置： ``isaaclab_mimic/motion_planners/curobo``
* 多阶段规划：

  * 每个子任务包含撤离（Retreat）→ 接触（Contact）→ 接近（Approach）阶段
  * 接触阶段的碰撞过滤可配置
  * 对于 SkillGen，撤离和接近阶段是无碰撞的。转移（transit）阶段会进行碰撞检查。

* 世界同步：

  * 每次尝试都会从 Isaac Lab 场景更新机器人状态、附着物体和碰撞球体
  * 在抓取/放置期间动态附着/分离物体

* 碰撞表示：

  * 具备接触感知的球体集合，支持按阶段启用/过滤

* 输出：

  * 经过时间参数化和碰撞检查的轨迹，用于拼接

* 测试：

  * ``source/isaaclab_mimic/test/test_curobo_planner_cube_stack.py``
  * ``source/isaaclab_mimic/test/test_curobo_planner_franka.py``
  * ``source/isaaclab_mimic/test/test_generate_dataset_skillgen.py``

.. list-table::
   :widths: 50 50
   :header-rows: 0

   * - .. figure:: https://download.isaacsim.omniverse.nvidia.com/isaaclab/images/cube_stack_end_to_end_curobo.gif
         :height: 260px
         :align: center
         :alt: cuRobo planner test on cube stack using Franka Panda robot

         立方体堆叠规划器测试。
     - .. figure:: https://download.isaacsim.omniverse.nvidia.com/isaaclab/images/obstacle_avoidance_curobo.gif
         :height: 260px
         :align: center
         :alt: cuRobo planner test on obstacle avoidance using Franka Panda robot

         Franka 规划器测试。

这些测试也可以作为如何将 cuRobo 用作独立运动规划器的参考。

.. note::

   有关 cuRobo 配置创建和参数的详细信息，请参见文件 ``isaaclab_mimic/motion_planners/curobo/curobo_planner_config.py`` 。

生成流水线集成
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

当 ``generate_dataset.py`` 中启用 ``--use_skillgen`` 时，将执行以下流水线：

1. **随机化子任务边界** ：使用任务配置的偏移范围，对每条演示数据的每个子任务随机化开始和终止索引。

2. **构建每个子任务的轨迹** ：
   对于每个末端执行器和子任务：

   - 选择一个源演示数据片段（由策略驱动；遵循协调/顺序约束）
   - 将该片段变换到当前场景（物体相对或协调增量；可选首个位姿插值）
   - 将变换后的片段封装为路径点轨迹

3. **子任务之间的过渡** ：
   - 使用 cuRobo 规划一条具备碰撞感知的过渡运动到子任务的第一个路径点（世界同步，可选附着/分离），执行规划出的路径点，然后恢复子任务轨迹

4. **在约束下执行** ：
   - 在末端执行器之间逐步执行路径点，同时强制执行子任务约束（顺序执行、带同步步的协调执行）；可选地，如果启用了可视化则更新规划器可视化

5. **记录与导出** ：
   - 累积状态/观测/动作，设置回合成功标志，并导出该回合（外层流水线会过滤/使用成功的回合）

可视化与调试
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

用户可以使用基于 Rerun 的规划可视化器来查看规划出的轨迹并调试碰撞问题。可以通过在 cuRobo 规划器配置中设置 ``visualize_plan = True`` 来启用它。请注意，需要安装 rerun 才能查看规划出的轨迹。安装说明请参见 :ref:`skillgen-installation` 中的步骤 3。

.. figure:: https://download.isaacsim.omniverse.nvidia.com/isaaclab/images/rerun_cube_stack.gif
   :width: 80%
   :align: center
   :alt: Rerun visualization of planned trajectories and collisions
   :figclass: align-center

   Rerun 集成：带碰撞球体的规划轨迹。

.. note::

   请在 ``docs/licenses/dependencies/cuRobo-license.txt`` 中查看 cuRobo 的使用许可。
