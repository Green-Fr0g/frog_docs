.. _augmented-imitation-learning:

增强模仿学习
============================

本节介绍如何将 Isaac Lab 的模仿学习能力与 `Cosmos <https://www.nvidia.com/en-us/ai/cosmos/>`_ 模型的视觉增强能力相结合，以大规模生成演示数据，用于训练对视觉变化具有鲁棒性的视觉运动策略。

生成演示数据
~~~~~~~~~~~~~~~~~~~~~~~~~

我们使用 Isaac Lab Mimic 功能，它可以从少量人工标注的演示数据中自动生成更多演示数据。

.. note::
    本节假定您已经拥有一份收集好的、经过标注的演示数据集。如果没有，您可以按照 :ref:`teleoperation-imitation-learning` 中的说明来收集并标注您自己的演示数据。

在下面的示例中，我们将向您展示如何使用 Isaac Lab Mimic 生成额外的演示数据，这些数据既可以直接用于训练视觉运动策略，也可以使用 Cosmos 进行视觉变化增强（使用 ``Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Cosmos-Mimic-v0`` 环境）。

.. note::
    ``Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Cosmos-Mimic-v0`` 环境与标准视觉运动环境（ ``Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Mimic-v0`` ）类似，但在生成的数据集中额外添加了分割掩码、深度图和法线图。这些额外的模态对于从使用 Cosmos 进行的视觉增强中获得最佳效果是必需的。

.. code:: bash

    ./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \
    --device cpu --enable_cameras --headless --num_envs 10 --generation_num_trials 1000 \
    --input_file ./datasets/annotated_dataset.hdf5 --output_file ./datasets/mimic_dataset_1k.hdf5 \
    --task Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Cosmos-Mimic-v0 \
    --rendering_mode performance

可以增加或减少演示数据的数量，已有结果表明 1000 条演示数据能为该任务提供良好的训练效果。

此外，可以调整 ``--num_envs`` 参数中的环境数量以加快数据生成速度。
建议的 10 个环境数量可以在中等配置的笔记本 CPU 上运行。
在性能更强的台式机上，使用更多的环境数量可以显著加快此步骤的速度。

Cosmos 增强
~~~~~~~~~~~~~~~~~~~

HDF5 转 MP4
^^^^^^^^^^^^^^^^^^^^^^

``hdf5_to_mp4.py`` 脚本将存储在 HDF5 演示文件中的相机帧转换为 MP4 视频。它支持多种相机模态，包括 RGB、分割掩码、深度图和法线图。此转换对于使用 Cosmos 进行视觉增强是必需的，因为 Cosmos 只能处理视频文件，而不能处理 HDF5 数据。

.. rubric:: 必需参数

.. list-table::
    :widths: 30 70
    :header-rows: 0

    * - ``--input_file``
      - 输入 HDF5 文件的路径。
    * - ``--output_dir``
      - 用于保存输出 MP4 文件的目录。

.. rubric:: 可选参数

.. list-table::
    :widths: 30 70
    :header-rows: 0

    * - ``--input_keys``
      - 要从 HDF5 文件中处理的输入键列表。（默认值：["table_cam", "wrist_cam", "table_cam_segmentation", "table_cam_normals", "table_cam_shaded_segmentation", "table_cam_depth"]）
    * - ``--video_height``
      - 输出视频的高度（像素）。（默认值：704）
    * - ``--video_width``
      - 输出视频的宽度（像素）。（默认值：1280）
    * - ``--framerate``
      - 输出视频的帧率。（默认值：30）

.. note::
    默认的输入键遵循 ``Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Cosmos-Mimic-v0`` 环境所采用的命名约定，覆盖了所有相机模态。我们还包含了一个额外的模态 "table_cam_shaded_segmentation"，它并不属于 HDF5 数据文件中从仿真生成的模态，而是由此脚本自动生成的：它将分割掩码与法线图相结合，得到伪纹理化的分割视频，以便更好地控制 Cosmos 增强。

.. note::
    我们建议使用上面给出的输出视频高度、宽度和帧率的默认值，以便在 Cosmos 增强中获得最佳效果。

立方体堆叠任务的使用示例：

.. code:: bash

    python scripts/tools/hdf5_to_mp4.py \
    --input_file datasets/mimic_dataset_1k.hdf5 \
    --output_dir datasets/mimic_dataset_1k_mp4

.. _running-cosmos:

运行 Cosmos 进行视觉增强
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

将演示数据转换为 MP4 格式后，您可以使用 `Cosmos`_ 模型对视频进行视觉增强。增强过程的细节请遵循 Cosmos 文档。视觉增强可以包括对光照、纹理、背景和其他视觉元素的更改，同时保留与任务相关的关键特征。

我们将上一步生成的 RGB、深度和着色分割视频作为 Cosmos 模型的输入，如下所示：

.. figure:: https://download.isaacsim.omniverse.nvidia.com/isaaclab/images/cosmos_inputs.gif
   :width: 100%
   :align: center
   :alt: RGB, depth and segmentation control inputs to Cosmos

下面是来自 `Cosmos Transfer1 <https://github.com/nvidia-cosmos/cosmos-transfer1/tree/e4055e39ee9c53165e85275bdab84ed20909714a>`_ 的增强输出示例：

.. figure:: https://download.isaacsim.omniverse.nvidia.com/isaaclab/images/cosmos_output.gif
   :width: 100%
   :align: center
   :alt: Cosmos Transfer1 augmentation output

我们推荐使用 `Cosmos Transfer1 <https://github.com/nvidia-cosmos/cosmos-transfer1/tree/e4055e39ee9c53165e85275bdab84ed20909714a>`_ 模型进行视觉增强，因为我们发现它能够生成具有广泛视觉变化的高度多样化数据集，效果最佳。您可以参考 `安装说明 <https://github.com/nvidia-cosmos/cosmos-transfer1/blob/e4055e39ee9c53165e85275bdab84ed20909714a/INSTALL.md#environment-setup>`_ 、 `检查点下载说明 <https://github.com/nvidia-cosmos/cosmos-transfer1/blob/e4055e39ee9c53165e85275bdab84ed20909714a/examples/inference_cosmos_transfer1_7b.md#download-checkpoints>`_ 以及 `此示例 <https://github.com/nvidia-cosmos/cosmos-transfer1/blob/e4055e39ee9c53165e85275bdab84ed20909714a/examples/inference_cosmos_transfer1_7b.md#example-2-multimodal-control>`_ ，了解如何在此用例中使用 Transfer1。针对该任务，我们进一步建议在 Transfer1 模型中使用以下设置：

.. note::
    此工作流已在 Cosmos Transfer1 仓库的 commit ``e4055e39ee9c53165e85275bdab84ed20909714a`` 上进行了测试，该版本也是推荐的版本。克隆 Cosmos Transfer1 仓库后，请通过运行 ``git checkout e4055e39ee9c53165e85275bdab84ed20909714a`` 切换到该特定 commit。

.. rubric:: 超参数

.. list-table::
    :widths: 30 70
    :header-rows: 0

    * - ``negative_prompt``
      - "The video captures a game playing, with bad crappy graphics and cartoonish frames. It represents a recording of old outdated games. The images are very pixelated and of poor CG quality. There are many subtitles in the footage. Overall, the video is unrealistic and appears cg. Plane background."
    * - ``sigma_max``
      - 50
    * - ``control_weight``
      - "0.3,0.3,0.6,0.7"
    * - ``hint_key``
      - "blur,canny,depth,segmentation"

获得良好增强效果的另一个关键方面是用于控制 Cosmos 生成的一组提示词（prompt）。我们提供了一个脚本 ``cosmos_prompt_gen.py`` ，它可以从一组精心挑选的模板中构建提示词，这些模板涵盖了增强过程的各个方面。

.. rubric:: 必需参数

.. list-table::
    :widths: 30 70
    :header-rows: 0

    * - ``--templates_path``
      - 包含提示词模板的文件路径。

.. rubric:: 可选参数

.. list-table::
    :widths: 30 70
    :header-rows: 0

    * - ``--num_prompts``
      - 要生成的提示词数量（默认值：1）。
    * - ``--output_path``
      - 用于写入所生成提示词的输出文件路径。（默认值：prompts.txt）

.. code:: bash

    python scripts/tools/cosmos/cosmos_prompt_gen.py \
    --templates_path scripts/tools/cosmos/transfer1_templates.json \
    --num_prompts 10 --output_path prompts.txt

如果您想创建自己的提示词，建议参考以下指南：

1. 尽可能保持提示词的详细程度。最好针对生成应如何处理每个可见对象或感兴趣区域给出一些指示。例如，我们提供的提示词对桌面、光照、背景、机械臂、立方体以及整体场景设置都给出了明确的细节。

2. 尽量使增强指令尽可能真实且连贯。提示词越不现实或越不合常规，模型在保留输入控制视频关键特征方面的表现就越差。

3. 保持各个方面的增强指令相互一致。也就是说，对所有对象或感兴趣区域的增强应彼此连贯且符合常规。例如，最好使用诸如 "The table is of old dark wood with faded polish and food stains and the background consists of a suburban home" 这样的提示词，而不是类似 "The table is of old dark wood with faded polish and food stains and the background consists of a spaceship hurtling through space" 的提示词。

4. 必须包含关于输入控制视频的关键方面中哪些内容应予保留或保持不变的细节。在我们的提示词中，我们非常明确地指出立方体的颜色应保持不变，即底部为蓝色、中间为红色、顶部为绿色。请注意，我们不仅说明了应保持不变的内容，还给出了该方面当前形态的细节。

使用 Cosmos Transfer1 模型执行此用例的示例命令：

.. code:: bash

    export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:=0}"
    export CHECKPOINT_DIR="${CHECKPOINT_DIR:=./checkpoints}"
    export NUM_GPU="${NUM_GPU:=1}"
    PYTHONPATH=$(pwd) torchrun --nproc_per_node=$NUM_GPU --nnodes=1 --node_rank=0 cosmos_transfer1/diffusion/inference/transfer.py \
        --checkpoint_dir $CHECKPOINT_DIR \
        --video_save_folder outputs/cosmos_dataset_1k_mp4 \
        --controlnet_specs ./controlnet_specs/demo_0.json \
        --offload_text_encoder_model \
        --offload_guardrail_models \
        --num_gpus $NUM_GPU

与上述命令配合使用的 ``./controlnet_specs/demo_0.json`` json 文件示例：

.. code:: json

    {
        "prompt": "A robotic arm is picking up and stacking cubes inside a foggy industrial scrapyard at dawn, surrounded by piles of old robotic parts and twisted metal. The background includes large magnetic cranes, rusted conveyor belts, and flickering yellow floodlights struggling to penetrate the fog. The robot arm is bright teal with a glossy surface and silver stripes on the outer edges; the joints rotate smoothly and the pistons reflect a pale cyan hue. The robot arm is mounted on a table that is light oak wood with a natural grain pattern and a glossy varnish that reflects overhead lights softly; small burn marks dot one corner. The arm is connected to the base mounted on the table. The bottom cube is deep blue, the second cube is bright red, and the top cube is vivid green, maintaining their correct order after stacking. Sunlight pouring in from a large, open window bathes the table and robotic arm in a warm golden light. The shadows are soft, and the scene feels natural and inviting with a slight contrast between light and shadow.",
        "negative_prompt": "The video captures a game playing, with bad crappy graphics and cartoonish frames. It represents a recording of old outdated games. The images are very pixelated and of poor CG quality. There are many subtitles in the footage. Overall, the video is unrealistic and appears cg. Plane background.",
        "input_video_path" : "mimic_dataset_1k_mp4/demo_0_table_cam.mp4",
        "sigma_max": 50,
        "vis": {
            "input_control": "mimic_dataset_1k_mp4/demo_0_table_cam.mp4",
            "control_weight": 0.3
        },
        "edge": {
            "control_weight": 0.3
        },
        "depth": {
            "input_control": "mimic_dataset_1k_mp4/demo_0_table_cam_depth.mp4",
            "control_weight": 0.6
        },
        "seg": {
            "input_control": "mimic_dataset_1k_mp4/demo_0_table_cam_shaded_segmentation.mp4",
            "control_weight": 0.7
        }
    }

MP4 转 HDF5
^^^^^^^^^^^^^^^^^^^^^^

``mp4_to_hdf5.py`` 脚本将经过视觉增强的 MP4 视频转换回用于训练的 HDF5 格式。这一步至关重要，因为它确保增强后的视觉数据具有在 Isaac Lab 中训练视觉运动策略所需的正确格式，并将视频与原始数据集中相应的演示数据配对。

.. rubric:: 必需参数

.. list-table::
    :widths: 30 70
    :header-rows: 0

    * - ``--input_file``
      - 包含原始演示数据的输入 HDF5 文件路径。
    * - ``--videos_dir``
      - 包含经过视觉增强的 MP4 视频的目录。
    * - ``--output_file``
      - 用于保存包含增强视频的新 HDF5 文件的路径。

.. note::
    输入的 HDF5 文件用于保留非视觉数据（例如机器人状态和动作），同时将视觉数据替换为增强后的版本。

.. important::
    经过视觉增强的 MP4 文件必须遵循命名约定 ``demo_{demo_id}_*.mp4`` ，其中：

    - ``demo_id`` 与原始 MP4 文件中的演示数据 ID 相匹配

    - ``*`` 表示从该位置起的文件名可以由用户自行决定

    脚本需要此命名约定才能将增强后的视频与其对应的演示数据正确配对。

立方体堆叠任务的使用示例：

.. code:: bash

    python scripts/tools/mp4_to_hdf5.py \
    --input_file datasets/mimic_dataset_1k.hdf5 \
    --videos_dir datasets/cosmos_dataset_1k_mp4 \
    --output_file datasets/cosmos_dataset_1k.hdf5

预生成数据集
^^^^^^^^^^^^^^^^^^^^^

我们提供了一个 HDF5 格式的预生成数据集，其中包含针对立方体堆叠任务经过视觉增强的演示数据。如果您不希望在本地运行 Cosmos 来生成自己的增强数据，可以使用该数据集。该数据集可在 `Hugging Face <https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Augmented>`_ 上获取，其中同时包含原始演示数据和增强后的演示数据（作为单独的数据集文件），可用于训练视觉运动策略。

合并数据集
^^^^^^^^^^^^^^^^

``merge_hdf5_datasets.py`` 脚本将多个 HDF5 数据集合并为一个文件。当您希望将原始演示数据与增强后的演示数据合并，以创建更大、更多样化的训练数据集时，此脚本非常有用。

.. rubric:: 必需参数

.. list-table::
    :widths: 30 70
    :header-rows: 0

    * - ``--input_files``
      - 要合并的 HDF5 文件路径列表。

.. rubric:: 可选参数

.. list-table::
    :widths: 30 70
    :header-rows: 0

    * - ``--output_file``
      - 合并后输出的文件路径。（默认值：merged_dataset.hdf5）

.. tip::
    合并数据集可以让模型在训练期间同时接触原始和增强的视觉条件，从而有助于提高策略的鲁棒性。

立方体堆叠任务的使用示例：

.. code:: bash

    python scripts/tools/merge_hdf5_datasets.py \
    --input_files datasets/mimic_dataset_1k.hdf5 datasets/cosmos_dataset_1k.hdf5 \
    --output_file datasets/mimic_cosmos_dataset.hdf5

模型训练与评估
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robomimic 设置
^^^^^^^^^^^^^^^

作为示例，我们将训练一个由 `Robomimic <https://robomimic.github.io/>`__ 实现的 BC 智能体来训练策略。也可以使用任何其他框架或训练方法。

要安装 robomimic 框架，请使用以下命令：

.. code:: bash

   # install the dependencies
   sudo apt install cmake build-essential
   # install python module (for robomimic)
   ./isaaclab.sh -i robomimic

训练智能体
^^^^^^^^^^^^^^^^^

使用生成的数据，我们现在可以为 ``Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Cosmos-v0`` 训练一个视觉运动 BC 智能体：

.. code:: bash

    ./isaaclab.sh -p scripts/imitation_learning/robomimic/train.py \
    --task Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Cosmos-v0 --algo bc \
    --dataset ./datasets/mimic_cosmos_dataset.hdf5 \
    --name bc_rnn_image_franka_stack_mimic_cosmos

.. note::
   默认情况下，训练得到的模型和日志将保存到 ``IssacLab/logs/robomimic`` 。

评估
^^^^^^^^^^

``robust_eval.py`` 脚本在仿真中评估训练好的视觉运动策略。该评估有助于衡量策略对不同视觉变化的泛化能力，以及经过视觉增强的数据是否提高了策略的鲁棒性。

下面是评估中使用的不同设置的说明：

.. rubric:: 评估设置

.. list-table::
    :widths: 30 70
    :header-rows: 0

    * - ``Vanilla``
      - 与 Mimic 数据生成期间使用的设置完全相同。
    * - ``Light Intensity``
      - 光照强度/亮度发生变化，其他所有方面保持不变。
    * - ``Light Color``
      - 光照颜色发生变化，其他所有方面保持不变。
    * - ``Light Texture (Background)``
      - 光照纹理/背景发生变化，其他所有方面保持不变。
    * - ``Table Texture``
      - 桌面的视觉纹理发生变化，其他所有方面保持不变。
    * - ``Robot Arm Texture``
      - 机械臂的视觉纹理发生变化，其他所有方面保持不变。

.. rubric:: 必需参数

.. list-table::
    :widths: 30 70
    :header-rows: 0

    * - ``--task``
      - 环境名称。
    * - ``--input_dir``
      - 包含要评估的模型检查点的目录。

.. rubric:: 可选参数

.. list-table::
    :widths: 30 70
    :header-rows: 0

    * - ``--start_epoch``
      - 开始评估的检查点周期。（默认值：100）
    * - ``--horizon``
      - 每次 rollout 的步数跨度。（默认值：400）
    * - ``--num_rollouts``
      - 每个模型在每个设置下的 rollout 次数。（默认值：15）
    * - ``--num_seeds``
      - 要评估的随机种子数量。（默认值：3）
    * - ``--seeds``
      - 要使用的特定种子列表（替代随机种子）。
    * - ``--log_dir``
      - 结果写入的目录。（默认值：/tmp/policy_evaluation_results）
    * - ``--log_file``
      - 输出文件的名称。（默认值：results）
    * - ``--norm_factor_min``
      - 动作空间归一化因子的最小值。
    * - ``--norm_factor_max``
      - 动作空间归一化因子的最大值。
    * - ``--disable_fabric``
      - 是否禁用 fabric 并使用 USD I/O 操作。
    * - ``--enable_pinocchio``
      - 是否为 IK 控制器启用 Pinocchio。

.. note::
    评估结果将帮助您了解视觉增强是否提升了策略的性能和鲁棒性。请将这些结果与在原始数据集上的评估结果进行比较，以衡量增强带来的影响。

立方体堆叠任务的使用示例：

.. code:: bash

    ./isaaclab.sh -p scripts/imitation_learning/robomimic/robust_eval.py \
    --task Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Cosmos-v0 \
    --input_dir logs/robomimic/Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Cosmos-v0/bc_rnn_image_franka_stack_mimic_cosmos/*/models \
    --log_dir robust_results/bc_rnn_image_franka_stack_mimic_cosmos \
    --log_file result \
    --enable_cameras \
    --seeds 0 \
    --num_rollouts 15 \
    --rendering_mode performance

.. note::
   此脚本可能需要一天甚至更长时间才能运行完毕（取决于所使用的硬件）。这是预期的行为。

我们使用上述脚本分别比较了使用 1000 条 Mimic 生成演示数据、2000 条 Mimic 生成演示数据以及 2000 条 Cosmos-Mimic 生成演示数据（1000 条原始 Mimic + 1000 条 Cosmos 增强）训练的模型。我们对这三个模型使用相同的种子（0、1000 和 5000），并给出以下指标（对每个种子的最佳检查点取平均）：

.. rubric:: 模型对比

.. list-table::
    :widths: 25 25 25 25
    :header-rows: 0

    * - **评估设置**
      - **Mimic 1k 基线**
      - **Mimic 2k 基线**
      - **Cosmos-Mimic 2k**
    * - ``Vanilla``
      - 62%
      - 96.6%
      - 86.6%
    * - ``Light Intensity``
      - 11.1%
      - 20%
      - 62.2%
    * - ``Light Color``
      - 24.6%
      - 30%
      - 77.7%
    * - ``Light Texture (Background)``
      - 16.6%
      - 20%
      - 68.8%
    * - ``Table Texture``
      - 0%
      - 0%
      - 20%
    * - ``Robot Arm Texture``
      - 0%
      - 0%
      - 4.4%

上述训练模型的检查点可以在 `这里 <https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Augmented/tree/main/robomimic_bc_rnn_visuomotor_models>`_ 获取，以便您直接使用这些模型。
