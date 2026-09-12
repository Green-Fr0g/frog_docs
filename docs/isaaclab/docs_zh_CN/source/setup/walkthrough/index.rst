.. _walkthrough:

分步演示
========================

你已经完成了 Isaac Sim 和 Isaac Lab 的安装，并验证了一切按预期运行……

接下来该做什么？

以下分步演示将引导你完成设置 Isaac Lab 扩展项目、向 Lab 中添加新机器人、设计环境，以及为该机器人训练策略的全过程。
在本次分步演示中，我们将从 Jetbot 开始——这是一种简单的两轮差速底盘机器人，顶部装有一个摄像头——
但这些指南的设计意图是足够通用，让你可以用它们向 Isaac Lab 添加自己的机器人和环境！

本次分步演示的最终成果可以在我们的教程项目仓库
`这里 <https://github.com/isaac-sim/IsaacLabTutorial/tree/main>`_ 找到。该仓库的每个分支
代表将默认模板项目改造以达到我们目标的某个不同阶段。

.. toctree::
  :maxdepth: 1
  :titlesonly:

  concepts_env_design
  api_env_design
  technical_env_design
  training_jetbot_gt
  training_jetbot_reward_exploration
