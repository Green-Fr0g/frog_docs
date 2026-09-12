开发者技巧
==============

使用 ProtoMotions 时的实用技巧。

测试仿真器配置
-----------------------

使用 ``random_pose_visualizer.py`` 验证机器人能否正确加载：

.. code-block:: bash

   python examples/random_pose_visualizer.py \
       --robot g1 \
       --simulator isaacgym

它会设置随机关节姿态，使用**零重力和零力矩**。
机器人应当能保持其重置姿态（按 R 键重置）。

添加新机器人或新仿真后端时，这是第一件要测试的事。

对比动作库
--------------------------

使用 ``motion_libs_visualizer.py`` 对比真值动作与学习到的动作：

.. code-block:: bash

   python examples/motion_libs_visualizer.py \
       --motion_files gt_motions.pt predicted_motions.pt \
       --robot g1 \
       --simulator isaacgym

**功能：**

* 并排播放
* 黄色标记突出抖动的身体部位（归一化加加速度较高）
* 紫色标记突出与地面的接触点
* 平滑度指标（归一化加加速度、振荡指数）
* 可调节播放速度

.. image:: ../_static/motion_libs_viz.png
   :width: 600
   :alt: Motion Libs Visualizer

**保存预测动作：**

以完整评估（full-eval）模式运行推理，即可保存预测动作库：

.. code-block:: bash

   python protomotions/inference_agent.py \
       --checkpoint results/my_exp/last.ckpt \
       --simulator isaacgym \
       --full-eval \
       --headless \
       --num-envs 1024

理解优先级采样
--------------------------

动作模仿使用优先级采样来聚焦更难的动作：

**工作原理：**

1. 评估器定期对所有动作运行完整评估
2. 计算每个动作的成功率
3. 为失败/困难的动作分配更高的采样权重
4. 训练时会更多地采样困难样本

**代码中对应的位置：**

.. code-block:: python

   def update_motion_sampling_weights(self, metrics: Dict[str, MotionMetrics]):
       """
       Update motion sampling weights based on success/failure rates.
       """
       pass

**现象：**

* ``Train/episode_reward`` 略有下降

**实际情况：**

训练现在聚焦于更难的动作。策略并没有变差——
它只是在练习更困难的情形。

**应该关注什么：**

* ``Eval/gt_err`` - 无偏位置误差（对所有动作等权评估）
* ``Eval/success_rate`` - 无偏成功率

这些评估指标不使用优先级采样，能够反映真实性能。

Train Agent 模式
-----------------

``--training-max-iterations N`` 为实验设定采样与优化迭代的绝对次数上限。
每次迭代会从每个环境收集一轮 ``num_steps`` 的采样，并执行所配置的优化更新。
如果实验在第 20 次迭代时恢复训练、上限为 100，训练会继续进行到第 100 次迭代；
而不是额外再跑 100 次迭代。

``train_agent.py`` 有三种模式：

**1. 全新开始（Fresh Start）：**

新的实验名称 → 从实验文件构建配置

.. code-block:: bash

   python protomotions/train_agent.py \
       --experiment-name new_experiment \
       ...

**2. 恢复训练（Resume）：**

相同实验名称且已有检查点 → 加载完全相同的已保存配置

.. code-block:: bash

   # First run
   python protomotions/train_agent.py --experiment-name my_exp ...
   
   # Resume (uses saved configs, ignores CLI overrides!)
   python protomotions/train_agent.py --experiment-name my_exp ...

.. warning::

   恢复训练期间 CLI 覆盖（``--overrides``）会被**忽略**。系统会严格使用
   第一次运行时保存的配置。

**3. 热启动（Warm Start）：**

``--checkpoint`` 配合新的实验名称 → 旧权重 + 新配置

.. code-block:: bash

   python protomotions/train_agent.py \
       --experiment-name new_exp_with_changes \
       --checkpoint results/old_exp/last.ckpt \
       ...

仅生成配置模式
-----------------------

在不训练的情况下生成配置：

.. code-block:: bash

   python protomotions/train_agent.py \
       --experiment-name migration_test \
       ... \
       --create-config-only

适用场景：

* 配置 API 变更后迁移旧检查点
* 在长时间训练前验证配置
* 调试配置的组合过程

用于调试的运动学回放
--------------------------------

在不涉及物理的情况下测试动作与场景的对齐：

.. code-block:: bash

   python examples/env_kinematic_playback.py \
       --experiment-path examples/experiments/mimic/mlp.py \
       --motion-file my_motions.pt \
       --robot-name g1 \
       --simulator isaacgym \
       --scenes-file my_scenes.pt

它以运动学方式播放动作（直接设置姿态，不进行仿真）。可用于验证：

* 动作数据是否正确
* 场景物体位置是否正确
* 动作重定向没有破坏任何东西
