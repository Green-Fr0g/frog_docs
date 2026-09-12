实验
===========

ProtoMotions 实现了多种面向基于物理的角色动画的前沿算法。
本页对每种方法及其适用场景做高层概述。

Mimic
-----

.. raw:: html

   <video width="100%" controls>
     <source src="../_static/smpl_mimic.mp4" type="video/mp4">
     Your browser does not support the video tag.
   </video>

**论文**：`DeepMimic: Example-Guided Deep Reinforcement Learning of Physics-Based Character Skills <https://arxiv.org/abs/1804.02717>`__ （Peng et al., 2018）

Mimic 通过强化学习训练智能体模仿参考动作片段。
智能体在每个时间步匹配参考姿态即可获得奖励，从而学会在保持物理合理性的
前提下复现动作。

**实验变体**：

* ``mlp.py`` - 用于平坦地形的 MLP 策略
* ``mlp_complex_terrain.py`` - 用于复杂地形（楼梯、斜坡等）的 MLP 策略
* ``mlp_bm_l2c2.py`` - 带躯干锚点和 L2C2 平滑正则化的 BeyondMimic 策略，面向 sim2real
* ``fsq.py`` - 基于最大化坐标本体感觉与目标姿态的 FSQ 跟踪器

**示例命令**：

.. code-block:: bash

   python protomotions/train_agent.py \
       --experiment-path examples/experiments/mimic/mlp.py \
       --robot-name smpl \
       --simulator isaacgym \
       --motion-file <path_to_motion_file> \
       --experiment-name smpl_mimic

ADD（Adversarial Differential Discriminators）
--------------------------------------------------

**论文**：`ADD: Physics-Based Motion Imitation with Adversarial Differential Discriminators <https://add-moo.github.io/>`__

ADD 是一种对抗式的动作跟踪方法，能够自动平衡多个跟踪目标，无需手动调节奖励权重。
它使用判别器学习如何动态组合跟踪误差。

**示例命令**：

.. code-block:: bash

   python protomotions/train_agent.py \
       --experiment-path examples/experiments/add/mlp.py \
       --robot-name smpl \
       --simulator isaacgym \
       --motion-file <path_to_motion_file> \
       --experiment-name smpl_add

MaskedMimic
-----------

.. raw:: html

   <video width="100%" controls>
     <source src="../_static/smpl_masked_mimic.mp4" type="video/mp4">
     Your browser does not support the video tag.
   </video>

**论文**：`MaskedMimic: Unified Physics-Based Character Control Through Masked Motion Inpainting <https://research.nvidia.com/labs/par/maskedmimic/>`__ （Tessler et al., SIGGRAPH Asia 2024）

MaskedMimic 将角色控制表述为动作补全问题。一个统一的控制器学会从部分观测
（被掩码的关键帧、文本描述或场景信息）合成全身动作。

.. note::

   MaskedMimic 需要一个预训练的 Mimic 专家模型。请先在多个动作上训练 Mimic，
   然后通过 ``--overrides`` 提供检查点路径。

**示例命令**：

.. code-block:: bash

   python protomotions/train_agent.py \
       --experiment-path examples/experiments/masked_mimic/transformer.py \
       --robot-name smpl \
       --simulator isaacgym \
       --motion-file <path_to_motions> \
       --overrides "agent.config.expert_model_path='<path_to_expert_model>/last.ckpt'" \
       --experiment-name smpl_masked_mimic

GPC 与 PEFT
------------

GPC 从跟踪器导出的 FSQ token 训练一个可复用的离散潜变量先验，
然后通过 PEFT（参数高效微调）将冻结先验适配到具体任务技能。
当你想要一个可通过 SFT、RLFT 或 RLFT+AMP 适配器加以专门化、
且可复用的生成式动作先验时，选择这条路线。

分阶段的跟踪器、先验、SFT、RLFT、检查点与推理工作流
参见 :doc:`gpc`。

.. raw:: html

   <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; align-items: start;">
     <figure style="margin: 0;">
       <video width="100%" controls>
         <source src="../_static/gpc_prior_unconditional.mp4" type="video/mp4">
         Your browser does not support the video tag.
       </video>
       <figcaption>Unconditional GPC prior</figcaption>
     </figure>
     <figure style="margin: 0;">
       <video width="100%" controls>
         <source src="../_static/gpc_location_peft.mp4" type="video/mp4">
         Your browser does not support the video tag.
       </video>
       <figcaption>Location task after PEFT</figcaption>
     </figure>
   </div>

AMP（对抗运动先验）
-------------------------------

.. raw:: html

   <video width="100%" controls>
     <source src="../_static/g1_amp.mp4" type="video/mp4">
     Your browser does not support the video tag.
   </video>

**论文**：`AMP: Adversarial Motion Priors for Stylized Physics-Based Character Control <https://arxiv.org/abs/2104.02180>`__ （Peng et al., 2021）

AMP 使用判别器从参考数据中学习运动先验。智能体不追踪特定姿态，
而是在完成任务目标的同时，学会以与参考动作相似的风格运动。

**示例命令**：

.. code-block:: bash

   python protomotions/train_agent.py \
       --experiment-path examples/experiments/amp/mlp.py \
       --robot-name g1 \
       --simulator isaacgym \
       --motion-file <path_to_motion> \
       --experiment-name g1_amp

Steering（方向控制）
--------------------

.. raw:: html

   <video width="100%" controls>
     <source src="../_static/g1_steering.mp4" type="video/mp4">
     Your browser does not support the video tag.
   </video>

Steering 将 AMP 风格的运动先验与方向控制目标相结合。智能体学会沿用户指定的
方向行走/奔跑，同时保持自然的动作风格。

**示例命令**：

.. code-block:: bash

   python protomotions/train_agent.py \
       --experiment-path examples/experiments/steering/mlp.py \
       --robot-name g1 \
       --simulator isaacgym \
       --motion-file <path_to_motion> \
       --experiment-name g1_steering

ASE（对抗技能嵌入）
----------------------------------

.. raw:: html

   <video width="100%" controls>
     <source src="../_static/smpl_ase.mp4" type="video/mp4">
     Your browser does not support the video tag.
   </video>

**论文**：`ASE: Large-Scale Reusable Adversarial Skill Embeddings for Physically Simulated Characters <https://arxiv.org/abs/2205.01906>`__ （Peng et al., 2022）

ASE 在 AMP 的基础上学习一个潜变量技能空间。策略以潜变量编码为条件，
使单一控制器能够通过改变潜变量输入执行多种不同的技能。

.. note::

   ASE 需要**多样化的动作数据集**，包含许多不同类型的动作。
   它无法只用单个动作片段训练——技能嵌入依赖多样的行为
   才能学到有意义的潜变量编码。

**示例命令**：

.. code-block:: bash

   python protomotions/train_agent.py \
       --experiment-path examples/experiments/ase/mlp.py \
       --robot-name smpl \
       --simulator isaacgym \
       --motion-file <path_to_motions> \
       --experiment-name smpl_ase

另请参阅
--------

* :doc:`configuration` - 配置系统
* :doc:`gpc` - GPC 与 PEFT 工作流
* :doc:`../tutorials/code_tutorials` - 逐步教程
* :doc:`../getting_started/quickstart` - 快速上手指南
