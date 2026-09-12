GPC 与 PEFT
============

GPC 实验先训练一个可复用的离散潜变量先验，再用 PEFT 将该先验适配到具体任务技能。
其结构与 ProtoMotions 其余部分刻意保持一致：实验文件掌控数据流，智能体配置描述模型，
观测键始终保持显式。

训练阶段
---------------

跟踪器
~~~~~~~

首先训练一个动作跟踪器。GPC 将跟踪器的 actor 模块当作冻结的潜变量自编码器使用：

* 跟踪器编码器将目标姿态映射为 FSQ 编码；
* 跟踪器量化器将编码转换为离散 token 索引；
* 跟踪器解码器将生成的编码映射回机器人动作。

.. note::

   用于 GPC 的跟踪器必须带 FSQ 瓶颈：其编码器将目标姿态映射为有限标量量化编码，
   其解码器将生成的 FSQ 编码映射回机器人动作。具体训练配置参见
   ``examples/experiments/mimic/fsq.py``。该实验训练出的动作跟踪器，
   其 token 和解码器会被 GPC 先验复用。

先验
~~~~~

``examples/experiments/gpc/prior.py`` 训练自回归先验。它使用
``DiscreteAutoregressiveLatentSupervisedAgentConfig``，以冻结跟踪器产生的专家采样轮数据为输入。
模型学习根据先验上下文观测（如 ``max_coords_obs``）预测跟踪器的 FSQ token。

保存的先验检查点是完整的
``DiscreteAutoregressiveLatentPriorModel``。PEFT 配置应通过
``pretrained_modules["prior"]`` 加载整个模型。不要把 PEFT 指向旧的
``actor.mu`` 子模块路径；PEFT 需要先验 transformer、潜变量分组、冻结解码器以及 SFT 目标编码器。

SFT
~~~

``examples/experiments/gpc/sft_target_prior_peft.py`` 用监督微调引导出一个任务适配器。
跟踪器从 ``mimic_target_poses`` 提供目标 FSQ token。PEFT actor 接收的
``task_obs`` 来自与 RLFT 相同的目标观测工厂，但目标取自参考片段上未来的根节点
XY 点并叠加抖动。这样使 SFT 数据路径与后续任务学习路径保持接近。

SFT 使用 ``DiscretePriorPEFTSFTAgentConfig``，不含 critic。主要损失是
生成的潜变量 logits 与冻结编码器目标 token 之间按配置计算的有监督损失。SFT 与
RLFT 都通过共享的 ``pretrained_modules`` 生命周期加载冻结先验，因此在两个训练循环中修改先验检查点路径使用相同的配置形式。

RLFT
~~~~

``examples/experiments/gpc/target_prior_peft.py`` 用 PPO 基于任务奖励微调适配器。
actor 配置与 SFT 配置保持兼容，因此可以用 SFT 检查点热启动 RLFT。环境通常会把
SFT 的 mimic 目标来源切换为任务控制来源，例如随机目标到达。

``examples/experiments/gpc/task_target_prior_peft_amp.py`` 在密集风格奖励有用时，
为同一 PEFT actor 和任务 critic 附加 AMP 奖励。

PEFT 配置契约
--------------------

公开的离散先验 PEFT actor 配置形式如下：

.. code-block:: python

   DiscretePriorPEFTActorConfig(
       in_keys=["task_obs"],
       out_keys=["action", "mean_action", "neglogp", "prior_tokens"],
       peft=DiscretePriorPEFTConfig(
           model=ModuleContainerConfig(
               in_keys=["task_obs"],
               out_keys=["task_cond"],
               models=[...],
           ),
           condition_key="task_cond",
           ...
       ),
   )

``actor.in_keys`` 声明构建 PEFT 条件输入所需的任务观测。
``actor.peft.model`` 是一个 TensorDict 模块，消费这些键并写出
``actor.peft.condition_key``。该条件键是公开配置产生的唯一任务条件张量。
``DiscretePriorWithPEFT`` 随后将其与从检查点中发现的冻结先验上下文键组合。

冻结先验自身的上下文键从加载的先验检查点中发现，并在运行时由
``DiscretePriorPEFTActor`` 追加。实验配置不再需要遗留的路由字段，例如
``task_conditioning_keys``、``terrain_key``、``conditioning_model``，
也不需要 ``DiscretePriorPEFTActorConfig`` 或 ``DiscretePriorPEFTConfig`` 上的
actor 级目标/地形上下文键。具体的 ``actor.peft.model`` 仍可以有自己的模块专属字段，
例如地形编码器的输入键。

如果省略 ``actor.peft.model``，``DiscretePriorPEFTConfig`` 会构建一个小的默认
``ObsProcessorConfig``，将 ``actor.in_keys`` 归一化并拼接为
``condition_key``。当任务需要真正的条件网络或额外预处理时，请使用显式的
``actor.peft.model``。

KL 与先验约束采样
--------------------------------

在 RLFT 期间，``DiscretePriorPEFTRLFTAgent`` 会在训练开始时，从检查点加载的
PEFT 包装先验中固定一个锚点（anchor）。当 ``kl_coeff > 0`` 时，KL 项在同一批次上
比较当前适配器 logits 与该锚点。在 ``sampling_mode="prior_constraint"`` 下，
生成时从当前适配器采样，同时把支持范围约束在锚点先验的 top-p 核内。

恢复训练会先加载最新检查点状态，再从该加载状态固定锚点。用 SFT 检查点热启动新的
RLFT 实验时，锚点固定为 SFT 适配器；恢复 RLFT 运行时，锚点固定为被恢复的
RLFT 适配器。

常用命令
---------------

示例使用随附的 SOMA 蹲伏动作与 FSQ 跟踪器：
``data/motion_for_trackers/crouch_soma23.pt`` 和
``data/pretrained_models/motion_tracker/soma_bones_fsq/inference_last.ckpt``。
随附的 GPC 先验位于
``data/pretrained_models/gpc_prior/soma_bones/inference_last.ckpt``。
SFT 与 RLFT 可直接使用它，也可以用下面的第一条命令自行训练先验。

训练离散 GPC 先验：

.. code-block:: bash

   python protomotions/train_agent.py \
       --robot-name soma23 \
       --simulator isaaclab \
       --motion-file data/motion_for_trackers/crouch_soma23.pt \
       --experiment-path examples/experiments/gpc/prior.py \
       --tracker-checkpoint data/pretrained_models/motion_tracker/soma_bones_fsq/inference_last.ckpt \
       --num-envs 1024 \
       --batch-size 1024 \
       --experiment-name prior_gpc_soma23

用 SFT 引导出目标到达适配器：

.. code-block:: bash

   python protomotions/train_agent.py \
       --robot-name soma23 \
       --simulator isaaclab \
       --motion-file data/motion_for_trackers/crouch_soma23.pt \
       --experiment-path examples/experiments/gpc/sft_target_prior_peft.py \
       --prior-checkpoint results/prior_gpc_soma23/last.ckpt \
       --tracker-checkpoint data/pretrained_models/motion_tracker/soma_bones_fsq/inference_last.ckpt \
       --num-envs 1024 \
       --batch-size 1024 \
       --training-max-steps 50000000 \
       --experiment-name sft_target_peft_crouch_soma

从 SFT 检查点启动 RLFT：

.. code-block:: bash

   python protomotions/train_agent.py \
       --robot-name soma23 \
       --simulator isaaclab \
       --motion-file data/motion_for_trackers/crouch_soma23.pt \
       --experiment-path examples/experiments/gpc/target_prior_peft.py \
       --prior-checkpoint results/prior_gpc_soma23/last.ckpt \
       --checkpoint results/sft_target_peft_crouch_soma/last.ckpt \
       --num-envs 512 \
       --batch-size 512 \
       --experiment-name rlft_target_peft_crouch_soma

使用 ``--peft-sampling-mode nucleus`` 可以从学生模型的核中采样，并用 KL
向先验正则化。默认的 ``prior_constraint`` 模式使用冻结先验的核作为采样轮约束。

训练期间各检查点的角色
--------------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - 产物
     - 用途
     - 说明
   * - 跟踪器检查点
     - 先验训练与 SFT 目标时序
     - 先验训练会把跟踪器解码器和目标编码器嵌入保存的先验产物中。SFT 读取
       跟踪器配置只是为了对齐参考目标的前瞻时序。
   * - 先验检查点
     - SFT/RLFT 的冻结基础先验
     - 可使用完整的 ``last.ckpt`` 或先验的 ``inference_last.ckpt``。PEFT
       智能体加载整个先验模型，而不是 ``actor.mu`` 子模块。
   * - SFT/RLFT ``last.ckpt``
     - 恢复训练与热启动
     - RLFT 应从 SFT 的 ``last.ckpt`` 热启动，以获得优化器/训练状态和完整的
       PEFT 模型。
   * - SFT/RLFT ``inference_last.ckpt``
     - 推理与分享
     - 这是只含 PEFT 的精简产物。不要用它恢复训练。

对于随附的 SOMA 资产，对应路径为
``data/pretrained_models/motion_tracker/soma_bones_fsq/inference_last.ckpt`` 和
``data/pretrained_models/gpc_prior/soma_bones/inference_last.ckpt``。跟踪器和
先验都提供面向推理的检查点；完整的 ``last.ckpt`` 只用于训练或恢复。

推理
---------

PEFT 检查点契约保留两个产物：

* ``last.ckpt`` 是完整的训练/恢复检查点。它包含完整 PEFT 模型状态以及
  优化器/训练状态。恢复 SFT 或 RLFT 时使用它。
* ``inference_last.ckpt`` 是可分享的精简检查点。它只包含由
  ``actor.adapter_state_dict()`` 选出的可训练 PEFT/任务状态
  （``actor_peft_model.*``、PEFT 适配器的 ``lora`` / ``gamma`` / ``beta`` /
  ``m`` 条目，以及 PEFT 条件归一化器状态）。它不复制冻结的基础先验、critic、
  优化器或跟踪器解码器。

``DiscretePriorPEFTRLFTAgentConfig`` 默认启用推理检查点保存，因此常规的
SFT/RLFT 检查点写入会同时产出两个文件。两者的大小差异是有意为之：完整检查点用于
训练连续性，精简检查点则是跨机器搬运或部署时使用的产物。

直接从 PEFT 运行的精简检查点运行推理：

.. code-block:: bash

   python protomotions/inference_agent.py \
       --robot-name soma23 \
       --simulator isaaclab \
       --motion-file data/motion_for_trackers/crouch_soma23.pt \
       --checkpoint results/rlft_target_peft_crouch_soma/inference_last.ckpt \
       --num-envs 16

推理时，PEFT 运行的 ``resolved_configs_inference.pt`` 会构建 PEFT
智能体并将其指向冻结先验检查点。精简 PEFT 检查点作为适配器/任务状态加载到该先验上。
新版先验检查点内嵌了自己的 ``latent_decoder`` 配置（最初在先验训练时取自跟踪器），
因此 PEFT 推理时不再需要单独的跟踪器文件。

如果把 PEFT 运行迁移到另一台机器，请把 PEFT 的
``resolved_configs_inference.pt`` 放在 ``inference_last.ckpt`` 旁边，并只覆盖先验路径：

.. code-block:: bash

   --overrides agent.pretrained_modules.prior.checkpoint_path=data/pretrained_models/gpc_prior/soma_bones/inference_last.ckpt

离散先验 PEFT 的推理产物是自描述的：``--checkpoint`` 应指向 PEFT 运行的
``inference_last.ckpt``。

关键文件
---------

* ``examples/experiments/gpc/prior.py`` - 训练离散潜变量先验。
* ``examples/experiments/gpc/sft_target_prior_peft.py`` - 面向目标到达的有监督
  PEFT 引导。
* ``examples/experiments/gpc/target_prior_peft.py`` - 基于 PPO 的 RLFT 目标
  到达。
* ``examples/experiments/gpc/task_target_prior_peft_amp.py`` - 带 AMP
  奖励的 RLFT。
* ``protomotions/agents/supervised/latent_prior_model.py`` - 冻结跟踪器解码器加
  可训练自回归先验。
* ``protomotions/agents/peft/`` - 离散先验 PEFT actor、agent、适配器及 AMP
  变体。
