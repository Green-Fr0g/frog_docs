.. _sim2sim:

Sim-to-Sim 策略迁移
===================
本节提供了在 PhysX 与 Newton 后端之间进行 sim-to-sim 策略迁移的示例。sim-to-sim 迁移是部署到真实机器人之前必不可少的步骤，
因为它能验证策略在不同仿真器之间都能正常工作。通过 sim-to-sim 验证的策略，在真实机器人上成功的可能性要大得多。


概述
----

本指南展示如何在 PhysX 与 Newton 后端之间双向迁移策略。主要的挑战在于：不同的物理引擎在解析同一个机器人模型时，可能会得到不同的关节和连杆顺序。

在某个后端中训练的策略，会按照该后端解析机器人模型的方式，期望关节和连杆具有特定的顺序。迁移到另一个后端时，关节顺序可能不同，因此需要对观测和动作进行重映射。

未来，我们计划通过**机器人 schema** 来解决这个问题，它会统一不同后端之间的关节与连杆顺序。

目前，我们通过使用 YAML 文件中定义的关节映射来重映射观测和动作，从而解决这一问题。这些文件按源后端和目标后端的顺序分别指定关节名称。在策略执行期间，我们使用该映射对观测和动作重新排序，使它们能在目标后端下正确工作。

该方法已在 Unitree G1、Unitree Go2、Unitree H1 和 ANYmal-D 机器人上对两个迁移方向进行了测试。


你需要准备什么
~~~~~~~~~~~~~~~

- 使用 PhysX 或 Newton（RSL-RL）训练得到的策略检查点。
- 位于 ``scripts/sim2sim_transfer/config/`` 下、适用于你的机器人的关节映射 YAML 文件。
- 提供的回放脚本：``scripts/sim2sim_transfer/rsl_rl_transfer.py``。

要添加一个新机器人，请创建一个包含两个列表的 YAML 文件，其中每个关节名称在两个列表中都必须恰好出现一次：

.. code-block:: yaml

   # Example structure
   source_joint_names:  # Source backend joint order
     - joint_1
     - joint_2
     # ...
   target_joint_names:  # Target backend joint order
     - joint_1
     - joint_2
     # ...

该脚本会自动为运动任务计算所需的映射。


PhysX 到 Newton 的迁移
~~~~~~~~~~~~~~~~~~~~~~

要使用 Newton 后端运行 PhysX 训练出的策略，请使用以下命令模板：

.. code-block:: bash

   ./isaaclab.sh -p scripts/sim2sim_transfer/rsl_rl_transfer.py \
       --task=<TASK_ID> \
       --num_envs=32 \
       --checkpoint <PATH_TO_PHYSX_CHECKPOINT> \
       --policy_transfer_file <PATH_TO_MAPPING_YAML> \
       --visualizer newton

以下是针对不同机器人的示例：

1. Unitree G1

.. code-block:: bash

   ./isaaclab.sh -p scripts/sim2sim_transfer/rsl_rl_transfer.py \
       --task=Isaac-Velocity-Flat-G1-v0 \
       --num_envs=32 \
       --checkpoint <PATH_TO_PHYSX_CHECKPOINT> \
       --policy_transfer_file scripts/sim2sim_transfer/config/physx_to_newton_g1.yaml \
       --visualizer newton

2. Unitree H1


.. code-block:: bash

   ./isaaclab.sh -p scripts/sim2sim_transfer/rsl_rl_transfer.py \
       --task=Isaac-Velocity-Flat-H1-v0 \
       --num_envs=32 \
       --checkpoint <PATH_TO_PHYSX_CHECKPOINT> \
       --policy_transfer_file scripts/sim2sim_transfer/config/physx_to_newton_h1.yaml \
       --visualizer newton


3. Unitree Go2

.. code-block:: bash

   ./isaaclab.sh -p scripts/sim2sim_transfer/rsl_rl_transfer.py \
       --task=Isaac-Velocity-Flat-Go2-v0 \
       --num_envs=32 \
       --checkpoint <PATH_TO_PHYSX_CHECKPOINT> \
       --policy_transfer_file scripts/sim2sim_transfer/config/physx_to_newton_go2.yaml \
       --visualizer newton


4. ANYmal-D


.. code-block:: bash

   ./isaaclab.sh -p scripts/sim2sim_transfer/rsl_rl_transfer.py \
       --task=Isaac-Velocity-Flat-Anymal-D-v0 \
       --num_envs=32 \
       --checkpoint <PATH_TO_PHYSX_CHECKPOINT> \
       --policy_transfer_file scripts/sim2sim_transfer/config/physx_to_newton_anymal_d.yaml \
       --visualizer newton

请注意，要运行以上命令，你需要检出基于 Newton 的 IsaacLab 分支，例如 ``feature/newton``。

Newton 到 PhysX 的迁移
~~~~~~~~~~~~~~~~~~~~~~

要将 Newton 训练出的策略迁移到基于 PhysX 的 IsaacLab，请使用反向的映射文件：

以下是针对不同机器人的示例：

1. Unitree G1

.. code-block:: bash

   ./isaaclab.sh -p scripts/sim2sim_transfer/rsl_rl_transfer.py \
       --task=Isaac-Velocity-Flat-G1-v0 \
       --num_envs=32 \
       --checkpoint <PATH_TO_NEWTON_CHECKPOINT> \
       --policy_transfer_file scripts/sim2sim_transfer/config/newton_to_physx_g1.yaml


2. Unitree H1

.. code-block:: bash

   ./isaaclab.sh -p scripts/sim2sim_transfer/rsl_rl_transfer.py \
       --task=Isaac-Velocity-Flat-H1-v0 \
       --num_envs=32 \
       --checkpoint <PATH_TO_NEWTON_CHECKPOINT> \
       --policy_transfer_file scripts/sim2sim_transfer/config/newton_to_physx_h1.yaml


3. Unitree Go2

.. code-block:: bash

   ./isaaclab.sh -p scripts/sim2sim_transfer/rsl_rl_transfer.py \
       --task=Isaac-Velocity-Flat-Go2-v0 \
       --num_envs=32 \
       --checkpoint <PATH_TO_NEWTON_CHECKPOINT> \
       --policy_transfer_file scripts/sim2sim_transfer/config/newton_to_physx_go2.yaml


4. ANYmal-D

.. code-block:: bash

   ./isaaclab.sh -p scripts/sim2sim_transfer/rsl_rl_transfer.py \
       --task=Isaac-Velocity-Flat-Anymal-D-v0 \
       --num_envs=32 \
       --checkpoint <PATH_TO_NEWTON_CHECKPOINT> \
       --policy_transfer_file scripts/sim2sim_transfer/config/newton_to_physx_anymal_d.yaml

关键区别在于使用 ``newton_to_physx_*.yaml`` 映射文件，而不是 ``physx_to_newton_*.yaml`` 文件。另外请注意，你需要检出基于 PhysX 的 IsaacLab 分支，例如 ``main``。

说明与局限性
~~~~~~~~~~~~~

- 两个迁移方向都已在 Unitree G1、Unitree Go2、Unitree H1 和 ANYmal-D 机器人上测试过。
- PhysX 到 Newton 的迁移使用 ``physx_to_newton_*.yaml`` 映射文件。
- Newton 到 PhysX 的迁移需要相应的 ``newton_to_physx_*.yaml`` 映射文件以及 IsaacLab 的 PhysX 分支。
- 观测重映射假定运动任务的观测布局为基座观测在前、关节观测在后。对于不同的观测布局，你需要修改 ``scripts/sim2sim_transfer/rsl_rl_transfer.py`` 中的 ``get_joint_mappings`` 函数。
- 在添加新机器人或后端时，请确保源和目标具有完全相同的关节名称，并且 YAML 列表反映了各后端对这些关节的排序方式。
