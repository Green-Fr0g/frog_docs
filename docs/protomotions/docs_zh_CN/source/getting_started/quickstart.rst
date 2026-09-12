快速上手
========

本指南帮助你运行预训练模型，并开始训练自己的智能体。

运行预训练模型
--------------

我们为多个机器人和控制策略族提供了预训练检查点。
请查看 :doc:`pretrained_models` 目录以获得简要概览，以及指向各检查点旁详细模型卡的链接。

以下命令使用推荐的 IsaacLab 检查点。
目前只有经过域随机化的 G1 部署跟踪器预期可以迁移到兼容的仿真器或硬件上。

**示例动作数据：**

我们提供了用于机器人模型测试的小型示例动作文件：

* ``data/motion_for_trackers/g1_random_subset_tiny.pt`` - 重定向到 G1 的 AMASS 小型子集
* ``data/motion_for_trackers/g1_bones_seed_mini.pt`` - 重定向到 G1 的 BONES-SEED 动作小型子集
* ``data/motion_for_trackers/soma23_bones_seed_mini.pt`` - SOMA 23 身体人形（数字人）的 BONES-SEED 动作小型子集
* ``data/motion_for_trackers/crouch_soma23.pt`` - 用于 GPC 和 PEFT 示例的小型 SOMA 下蹲数据集
* ``data/motion_for_trackers/h1_2_random_subset_tiny.pt`` - 重定向到 H1-2 的 AMASS 小型子集

关于 SMPL 动作数据，请参阅 :doc:`amass_preparation`，从 AMASS 生成你自己的动作库（MotionLib）。
如果你的本地 GPU 显存不足以加载整个 AMASS 动作库，可以使用简单的脚本
``scripts/subset_motion_lib.py`` 将动作库缩减到更小的规模。

**运行推理：**

.. code-block:: bash

   # Run G1 on BONES-SEED motions
   python protomotions/inference_agent.py \
       --checkpoint data/pretrained_models/motion_tracker/g1-bones-deploy/last.ckpt \
       --motion-file data/motion_for_trackers/g1_bones_seed_mini.pt \
       --simulator isaaclab

   # Headless validation on a server or VM
   python protomotions/inference_agent.py \
       --checkpoint data/pretrained_models/motion_tracker/g1-bones-deploy/last.ckpt \
       --motion-file data/motion_for_trackers/g1_bones_seed_mini.pt \
       --simulator isaaclab \
       --num-envs 100 \
       --headless \
       --full-eval

   # Run SOMA 23-body humanoid on BONES-SEED motions
   python protomotions/inference_agent.py \
       --checkpoint data/pretrained_models/motion_tracker/soma-bones/last_lab.ckpt \
       --motion-file data/motion_for_trackers/soma23_bones_seed_mini.pt \
       --simulator isaaclab

   # Run the SOMA BONES-SEED FSQ tracker used by GPC
   python protomotions/inference_agent.py \
       --checkpoint data/pretrained_models/motion_tracker/soma_bones_fsq/inference_last.ckpt \
       --motion-file data/motion_for_trackers/soma23_bones_seed_mini.pt \
       --simulator isaaclab

   # Run the SOMA GPC prior with its SOMA BONES-SEED FSQ decoder
   python protomotions/inference_agent.py \
       --checkpoint data/pretrained_models/gpc_prior/soma_bones/inference_last.ckpt \
       --motion-file data/motion_for_trackers/crouch_soma23.pt \
       --simulator isaaclab \
       --num-envs 1

   # Run SMPL on flat terrain (requires AMASS MotionLib, see amass_preparation)
   python protomotions/inference_agent.py \
       --checkpoint data/pretrained_models/motion_tracker/smpl/last.ckpt \
       --motion-file path/to/your/amass_motionlib.pt \
       --simulator isaaclab

   # Run SMPL on complex terrain
   python protomotions/inference_agent.py \
       --checkpoint data/pretrained_models/motion_tracker/smpl-terrains/last.ckpt \
       --motion-file path/to/your/amass_motionlib.pt \
       --simulator isaaclab

   # Test the domain-randomized G1 tracker in MuJoCo
   python protomotions/inference_agent.py \
       --checkpoint data/pretrained_models/motion_tracker/g1-bones-deploy/last.ckpt \
       --motion-file data/motion_for_trackers/g1_bones_seed_mini.pt \
       --simulator mujoco \
       --num-envs 1

.. note::

   在无界面（headless）机器上，通常用 ``--full-eval`` 更容易进行验证，因为它会在评估完动作集后退出并打印指标。
   不加 ``--full-eval`` 时，推理会持续运行直到被手动中断。

   只有当模型卡说明该策略使用了完整的面向迁移的域随机化方案时，才可以预期跨仿真器迁移能够成功。
   详见 :doc:`pretrained_models` 与
   :doc:`../tutorials/workflows/domain_randomization`。

训练你的第一个智能体
--------------------

使用 DeepMimic 进行动作模仿训练
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

使用 MLP 策略训练一个动作模仿智能体：

.. code-block:: bash

   python protomotions/train_agent.py \
       --robot-name smpl \
       --simulator isaaclab \
       --experiment-path examples/experiments/mimic/mlp.py \
       --experiment-name smpl_mimic_example \
       --motion-file path/to/your/motion_lib.pt \
       --num-envs 4096 \
       --batch-size 16384 \
       --ngpu 1

动作数据准备请参阅 :doc:`amass_preparation`。

选择仿真器与机器人
------------------

仿真器选择
~~~~~~~~~~

通过 ``--simulator`` 参数选择：

* ``isaacgym`` - NVIDIA IsaacGym 旧版 GPU 后端
* ``isaaclab`` - NVIDIA IsaacLab/IsaacSim（推荐用于训练）
* ``newton`` - NVIDIA Newton 1.0.0（基于 MuJoCo Warp 构建）
* ``genesis`` - Genesis 仿真器
* ``mujoco`` - MuJoCo 仅 CPU（单环境，用于快速测试/调试）

机器人选择
~~~~~~~~~~

通过 ``--robot-name`` 参数选择：

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - 机器人
     - 说明
   * - ``smpl``
     - SMPL 人形（数字人）
   * - ``smplx``
     - 带手部的 SMPL-X 人形
   * - ``g1``
     - Unitree G1 人形机器人
   * - ``h1_2``
     - Unitree H1 人形机器人（第 2 版）
   * - ``amp``
     - AMP 人形
   * - ``soma23``
     - SOMA 23 身体人形（数字人）

添加自己的机器人请参阅 :doc:`../tutorials/workflows/custom_robot`。

实验管理
--------

``--experiment-name`` 决定结果的保存位置。当使用已存在的实验名进行训练时，
训练会自动从最近的检查点恢复训练。

结果保存到：

.. code-block:: text

   results/<experiment_name>/
   ├── config.yaml                      # CLI arguments and wandb ID
   ├── resolved_configs.pt              # Full config objects (for exact reproducibility)
   ├── resolved_configs.yaml            # Human-readable configs
   ├── resolved_configs_inference.pt    # Inference-time configs (largely same as training configs)
   ├── resolved_configs_inference.yaml  # Human-readable inference configs
   ├── experiment_config.py             # Copy of experiment file
   ├── last.ckpt                        # Latest model checkpoint
   ├── score_based.ckpt                 # Best-performing checkpoint (by eval score)
   ├── epoch_100.ckpt                   # Intermediate checkpoints (if configured)
   └── env_<task_id>.ckpt               # Environment state for exact resume

.. note::

   恢复训练（实验名相同时）会使用精确保存的配置——恢复期间忽略 CLI 覆盖。这一设计有助于在集群上使用多 GPU 运行时自动恢复训练。

   如需修改配置，请使用新的实验名。在云端/集群上训练时，也可以把源码复制到新目录，在那里以任意实验名进行训练。

.. warning::

   **不要修改 resolved_configs.yaml 文件。** 它们仅供人阅读——真正的配置来源是 ``.pt`` 文件。
   修改配置时，小改动用 ``--overrides``，大改动用 ``--create-config-only`` 并把新的
   ``.pt`` 复制到检查点目录。详见 :doc:`/user_guide/configuration`。

训练配置
--------

常用配置选项：

.. code-block:: bash

   python protomotions/train_agent.py \
       --robot-name smpl \
       --simulator isaaclab \
       --experiment-path examples/experiments/mimic/mlp.py \
       --experiment-name my_experiment \
       --motion-file path/to/motions.pt \
       --num-envs 4096 \
       --batch-size 16384 \
       --ngpu 1 \
       --training-max-steps 10000000

配置覆盖
~~~~~~~~

使用 ``--overrides`` 在运行时修改配置值：

.. code-block:: bash

   --overrides "agent.num_mini_epochs=4" "env.max_episode_length=500"

**支持的覆盖格式：** ``config_type.field.subfield=value``

支持的配置类型：``env``、``simulator``、``robot``、``agent``、``terrain``、``motion_lib``、``scene_lib``

支持的值类型：``int``、``float``、``bool``、``str``、``None``

**限制：** 覆盖只支持简单的标量值。列表、嵌套对象或 dataclass 实例等复杂类型无法通过 CLI 覆盖。
对于这类修改，请创建新的实验文件——这也是管理和跟踪不同实验配置的良好实践。

配置系统的更多细节请参阅 :doc:`../user_guide/configuration`。

使用 Weights & Biases 记录日志
------------------------------

首先，设置 wandb 认证：

.. code-block:: bash

   wandb login

然后启用实验跟踪：

.. code-block:: bash

   python protomotions/train_agent.py \
       ... \
       --use-wandb \
       --wandb-project my_project

默认的 W&B 项目是 ``physical_animation``。

需要关注的关键指标：

* ``Eval/gt_err`` - 位置跟踪误差（无偏，对所有动作等权评估）
* ``Eval/success_rate`` - 动作完成率（无偏）
* ``Train/episode_reward`` - 训练奖励（可能因优先级采样而波动）
* ``Train/clip_frac`` - 保持在大约 0.3 以下训练才稳定（若持续偏高则调低学习率）
* ``Train/actor_grad_norm`` / ``Train/critic_grad_norm`` - 留意梯度爆炸

.. tip::

   除了基础的指标曲线，Weights & Biases 还有很多实用功能。你可以按任意配置参数搜索和筛选运行、并排比较多个运行、创建自定义仪表盘。花些时间探索它的界面，充分利用实验跟踪。

评估
----

评估训练好的智能体：

.. code-block:: bash

   # Evaluate G1 pretrained model
   python protomotions/inference_agent.py \
       --checkpoint data/pretrained_models/motion_tracker/g1-bones-deploy/last.ckpt \
       --motion-file data/motion_for_trackers/g1_bones_seed_mini.pt \
       --simulator isaaclab

   # Evaluate SOMA pretrained model
   python protomotions/inference_agent.py \
       --checkpoint data/pretrained_models/motion_tracker/soma-bones/last_lab.ckpt \
       --motion-file data/motion_for_trackers/soma23_bones_seed_mini.pt \
       --simulator isaaclab

   # Evaluate SMPL pretrained model (flat terrain)
   python protomotions/inference_agent.py \
       --checkpoint data/pretrained_models/motion_tracker/smpl/last.ckpt \
       --motion-file path/to/your/amass_motionlib.pt \
       --simulator isaaclab

   # Evaluate SMPL pretrained model (complex terrain)
   python protomotions/inference_agent.py \
       --checkpoint data/pretrained_models/motion_tracker/smpl-terrains/last.ckpt \
       --motion-file path/to/your/amass_motionlib.pt \
       --simulator isaaclab

   # Or evaluate your own trained model
   python protomotions/inference_agent.py \
       --checkpoint results/my_experiment/last.ckpt \
       --motion-file data/motion_for_trackers/g1_random_subset_tiny.pt \
       --simulator isaaclab

键盘控制
~~~~~~~~

在可视化过程中：

.. list-table::
   :header-rows: 1
   :widths: 10 90

   * - 按键
     - 说明
   * - ``J``
     - 对所有机器人施加物理力（测试鲁棒性）
   * - ``R``
     - 重置任务
   * - ``O``
     - 切换相机（在各个实体间循环）
   * - ``L``
     - 开关视频录制
   * - ``Q``
     - 退出

后续步骤
--------

* :doc:`amass_preparation` - 准备 AMASS 动作数据
* :doc:`../tutorials/index` - 端到端工作流教程
* :doc:`../concepts/index` - 理解核心抽象
* :doc:`../user_guide/configuration` - 深入了解配置系统
