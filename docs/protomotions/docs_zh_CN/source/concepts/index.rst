核心概念
========

本节介绍 ProtoMotions 的核心抽象与设计原则。

概述
----

ProtoMotions 的设计目标是支持多种组合：

* **仿真器**：IsaacGym、IsaacLab、Newton、Genesis
* **机器人**：SMPL、G1、H1、自定义形体结构
* **算法**：PPO、AMP、ASE、MaskedMimic
* **环境**：Mimic、Steering、PathFollower

这就要求系统具备模块化的抽象，使各组件能够自由组合搭配，而无需修改代码。

快速参考
--------

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - 概念
     - 用途
     - 位置
   * - :doc:`architecture`
     - 系统高层设计
     - 概述
   * - :doc:`abstractions`
     - 核心组件类
     - ``protomotions/components/``、``envs/``、``simulator/``
   * - :doc:`environment_context`
     - 连接各组件的上下文字典
     - ``protomotions/envs/base_env/env.py``
   * - :doc:`pose_lib`
     - MJCF 解析、FK/IK 工具
     - ``protomotions/components/pose_lib.py``
   * - :doc:`simulator_state`
     - 机器人与物体的状态表示
     - ``protomotions/simulator/base_simulator/simulator_state.py``
