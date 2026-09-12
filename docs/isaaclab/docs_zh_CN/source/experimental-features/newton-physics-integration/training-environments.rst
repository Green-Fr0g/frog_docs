训练环境
========

运行训练时，我们遵循标准的 Isaac Lab 工作流。如果你刚接触 Isaac Lab，建议先阅读 `快速上手指南 <https://isaac-sim.github.io/IsaacLab/main/source/setup/quickstart.html#>`_。

当前支持的任务如下：

* Isaac-Cartpole-Direct-v0
* Isaac-Cartpole-v0
* Isaac-Cartpole-RGB-Camera-Direct-v0
* Isaac-Cartpole-Depth-Camera-Direct-v0
* Isaac-Ant-Direct-v0
* Isaac-Ant-v0
* Isaac-Humanoid-Direct-v0
* Isaac-Humanoid-v0
* Isaac-Velocity-Flat-Anymal-B-v0
* Isaac-Velocity-Flat-Anymal-C-v0
* Isaac-Velocity-Flat-Anymal-D-v0
* Isaac-Velocity-Flat-Cassie-v0
* Isaac-Velocity-Flat-G1-v0
* Isaac-Velocity-Flat-G1-v1（经过 sim-to-real 验证）
* Isaac-Velocity-Flat-H1-v0
* Isaac-Velocity-Flat-Unitree-A1-v0
* Isaac-Velocity-Flat-Unitree-Go1-v0
* Isaac-Velocity-Flat-Unitree-Go2-v0
* Isaac-Reach-Franka-v0
* Isaac-Reach-UR10-v0
* Isaac-Repose-Cube-Allegro-Direct-v0

新的实验性基于 warp 的环境：

* Isaac-Cartpole-Direct-Warp-v0
* Isaac-Ant-Direct-Warp-v0
* Isaac-Humanoid-Direct-Warp-v0

要启动一个环境并检查其是否按预期加载，可以先向执行器发送零动作进行尝试。做法如下，其中 ``TASK_NAME`` 是你想运行的任务名称，``NUM_ENVS`` 是你想创建的任务实例数量。

.. code-block:: shell

    ./isaaclab.sh -p scripts/environments/zero_agent.py --task TASK_NAME --num_envs NUM_ENVS

对于 128 个实例的 cartpole，命令如下：

.. code-block:: shell

    ./isaaclab.sh -p scripts/environments/zero_agent.py --task Isaac-Cartpole-Direct-v0 --num_envs 128

要以随机动作运行同一环境，可以使用另一个脚本：

.. code-block:: shell

    ./isaaclab.sh -p scripts/environments/random_agent.py --task Isaac-Cartpole-Direct-v0 --num_envs 128

要训练环境，我们提供了对接不同 RL 框架的入口。更多信息请参阅 `强化学习脚本文档 <https://isaac-sim.github.io/IsaacLab/main/source/overview/reinforcement-learning/rl_existing_scripts.html>`_。

以下是在多个不同 RL 框架上运行训练的示例。注意，我们显式地将环境数量设为 4096，以便更多地受益于 GPU 并行化。

默认情况下，环境将以无头模式训练。如果需要可视化，请使用 ``--visualizer`` 并指定所需的可视化器。可用选项有 ``newton``、``rerun`` 和 ``omniverse`` （需要安装 Isaac Sim）。注意，可以选择并启动多个可视化器。

.. code-block:: shell

    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Cartpole-Direct-v0 --num_envs 4096

.. code-block:: shell

    ./isaaclab.sh -p scripts/reinforcement_learning/skrl/train.py --task Isaac-Cartpole-Direct-v0 --num_envs 4096

.. code-block:: shell

    ./isaaclab.sh -p scripts/reinforcement_learning/rl_games/train.py --task Isaac-Cartpole-Direct-v0 --num_envs 4096

策略训练完成后，我们可以使用 play 脚本将其可视化。但首先需要找到所训练策略的检查点。通常它们存储在 ``logs/NAME_OF_RL_FRAMEWORK/TASK_NAME/DATE`` 下。

例如，对于我们的 rsl_rl 示例，路径可能像这样：
``logs/rsl_rl/cartpole_direct/2025-08-21_15-45-30/model_299.pt``

然后可以使用以下命令运行该策略。注意，我们减少了环境数量并添加了 ``--visualizer newton`` 选项，以便看到策略的实际运行效果。

.. code-block:: shell

    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task Isaac-Cartpole-Direct-v0 --num_envs 128 --visualizer newton --checkpoint logs/rsl_rl/cartpole_direct/2025-08-21_15-45-30/model_299.pt

同样的方法适用于所有其他框架。

注意，并非所有环境在所有框架中都受支持。例如，部分运动环境仅在 rsl_rl 框架中受支持。
