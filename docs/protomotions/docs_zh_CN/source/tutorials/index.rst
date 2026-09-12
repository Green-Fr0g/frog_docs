教程
=====

这些教程完整演示了常见任务的端到端工作流程。

部署工作流
----------

* :doc:`workflows/g1_deployment` - G1 全身跟踪器：从数据到真机（完整管线）

训练工作流
----------

* :doc:`workflows/amass_smpl` - 在 AMASS 动作数据上训练 SMPL 人形角色
* :doc:`workflows/retargeting_pyroki` - 将 AMASS/SMPL 动作重定向到机器人
* :doc:`workflows/domain_randomization` - Sim2sim 迁移技术
* :doc:`../user_guide/gpc` - 训练 GPC 并用 PEFT 进行适配

机器人与环境搭建
----------------

* :doc:`workflows/custom_robot` - 添加你自己的机器人形体结构

代码教程
--------

想从零开始学习 ProtoMotions 的内部机制，请参阅 :doc:`code_tutorials` ——
``examples/tutorial/`` 中的 8 个渐进式 Python 脚本，讲解仿真器、地形、机器人、
场景和环境等核心概念。

快速参考
--------

.. list-table::
   :header-rows: 1
   :widths: 25 50 25

   * - 工作流
     - 说明
     - 前置条件
   * - :doc:`workflows/g1_deployment`
     - 完整管线：从数据到真机（G1 跟踪器）
     - 预训练模型或 BONES-SEED 数据
   * - :doc:`workflows/amass_smpl`
     - 在 AMASS 动作上训练 SMPL
     - 已准备好 AMASS 数据
   * - :doc:`workflows/retargeting_pyroki`
     - 将 AMASS/SMPL 重定向到机器人
     - 已打包的 AMASS .pt 文件
   * - :doc:`workflows/domain_randomization`
     - Sim2sim 迁移
     - 已训练的策略
   * - :doc:`../user_guide/gpc`
     - GPC 先验与 PEFT 任务适配
     - FSQ 动作跟踪器
   * - :doc:`workflows/custom_robot`
     - 添加新的机器人形体结构
     - MJCF 文件

更多示例
--------

其他实验族，包括 AMP、ASE、MaskedMimic、Steering 以及目标到达任务，
均列在 :doc:`../user_guide/experiments` 中。
