在 AMASS 上训练 SMPL
======================

本工作流介绍如何训练 SMPL 人形角色来模仿 AMASS 数据集中的动作。

前置条件
-------------

* 已转换为 ProtoMotions 格式的 AMASS 数据（参见 :doc:`../../getting_started/amass_preparation`）
* 已打包的 MotionLib ``.pt`` 文件

训练
--------

基础训练命令
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python protomotions/train_agent.py \
       --robot-name smpl \
       --simulator isaacgym \
       --experiment-path examples/experiments/mimic/mlp.py \
       --experiment-name smpl_amass_flat \
       --motion-file /path/to/amass_train.pt \
       --num-envs 8192 \
       --batch-size 8192 \
       --ngpu 4

这会在平坦地形上训练一个 MLP 策略。

在复杂地形上训练
~~~~~~~~~~~~~~~~~~~~~~~~~~~

要在不平坦的地形上获得鲁棒的运动控制：

.. code-block:: bash

   python protomotions/train_agent.py \
       --robot-name smpl \
       --simulator isaacgym \
       --experiment-path examples/experiments/mimic/mlp_complex_terrain.py \
       --experiment-name smpl_amass_terrain \
       --motion-file /path/to/amass_train.pt \
       --num-envs 8192 \
       --batch-size 8192 \
       --ngpu 4


预期训练时长
~~~~~~~~~~~~~~~~~~~~~~

在 4 张 A100 GPU 上使用完整 AMASS（40+ 小时的动作数据）：
约 2 小时达到 90% 成功率。
约 12 小时达到 99% 成功率，继续训练可以进一步提升成功率和奖励。

需要关注的关键指标
----------------------

使用 ``--use-wandb`` 时，可以跟踪以下指标：

* **Eval/gt_err**: 位置跟踪误差（越低越好）。该指标是无偏的 ——
  对所有动作等权评估。
* **Eval/success_rate**: 动作完成且不摔倒的比例。
* **Train/episode_reward**: 训练奖励。可能因优先级采样聚焦于更难的动作而波动。
* **Train/clip_frac**: 被 PPO 裁剪的策略更新比例。保持在约 0.3 以下训练才稳定。
  如果持续偏高，考虑调低学习率。
* **Train/actor_grad_norm** 与 **Train/critic_grad_norm**: 监控这两项以确保梯度没有爆炸。
  突然的尖峰可能表明你的改动或奖励配置有问题。

.. note::

   如果 ``Train/episode_reward`` 下降，可能意味着评估器重新加权了各动作
   （参见 mimic_evaluator.py），训练现在聚焦于更难的样本。请查看 ``Eval/gt_err``
   这一无偏指标，其中每个动作都会完整评估一次。

.. tip::

   Weights & Biases 除了基础的指标绘图外还有许多实用功能。你可以按任意配置参数
   搜索和筛选运行、并排对比多个运行、创建自定义仪表盘。花些时间探索一下 UI，
   以充分利用实验跟踪功能。

实验配置
-------------------------

``mlp.py`` 实验定义了：

**环境配置：**

* 1000 步的回合
* 跟踪误差过大时提前终止（最大关节误差 >0.5 rad）
* 回合结束时自举，用于价值估计

**奖励组件：**

* ``gt_rew``：全身位置跟踪
* ``gr_rew``：全身旋转跟踪
* ``gv_rew``、``gav_rew``：速度跟踪
* ``rh_rew``：根节点高度跟踪
* ``pow_rew``：功耗惩罚
* ``contact_match_rew``：足部接触匹配
* ``action_smoothness``：动作平滑度惩罚

**网络：**

* 6 层 MLP，每层 1024 个单元
* actor 与 critic 网络分离
* 观测的滑动均值/标准差归一化

定制训练示例
-----------------------------

调整迷你轮次
~~~~~~~~~~~~~~~~~~

更多的迷你轮次可以提升样本效率：

.. code-block:: bash

   --overrides "agent.num_mini_epochs=4"

禁用接触奖励
~~~~~~~~~~~~~~~~~~~~~~~

如果想要纯粹的动作模仿（DeepMimic）奖励：

.. code-block:: bash

   --overrides "env.reward_config.contact_match_rew.weight=0.0" \

（是的，这类基于字符串的覆盖对工厂方法创建的奖励同样有效）

可视化动作
-------------------

训练前或调试时，你可以用动作可视化器查看打包好的 MotionLib：

.. code-block:: bash

   python examples/motion_libs_visualizer.py \
       --motion_files /path/to/amass_train.pt \
       --robot smpl \
       --simulator isaacgym

可视化器支持并排对比多个 MotionLib，适合用来比较源动作与重定向或预测出的动作：

.. code-block:: bash

   python examples/motion_libs_visualizer.py \
       --motion_files /path/to/amass_train.pt /path/to/predicted_motions.pt \
       --robot smpl \
       --simulator isaacgym

**操作按键：**

* **R**：切换到下一个动作
* **1/2**：加快/减慢回放速度
* **3/4**：调整抖动高亮显示的平滑度阈值

评估
----------

对训练好的模型运行推理：

.. code-block:: bash

   python protomotions/inference_agent.py \
       --checkpoint results/smpl_amass_flat/last.ckpt \
       --simulator isaacgym

对所有动作做完整评估：

.. code-block:: bash

   python protomotions/inference_agent.py \
       --checkpoint results/smpl_amass_flat/last.ckpt \
       --simulator isaacgym \
       --num-envs 1024 \
       --full-eval

这会把动作 0 分配给环境 0、动作 1 分配给环境 1，依此类推，并汇总报告指标。

.. note::

   做 full-eval 时，请把 ``--num-envs`` 设为较大的值（例如 1024 或更多），
   以便并行评估大量动作。默认值为 1，会让完整评估非常慢。可能还需要
   ``--headless`` 来节省内存。

下一步
----------

* :doc:`retargeting_pyroki` - 将这些动作重定向到 G1 等机器人
* :doc:`domain_randomization` - 添加域随机化以实现 sim2sim
* :doc:`../../concepts/abstractions` - 理解底层架构
