Hydra 配置系统
==========================

.. currentmodule:: isaaclab

Isaac Lab 支持 `Hydra <https://hydra.cc/docs/intro/>`_ 配置系统，可以通过命令行参数修改任务的配置，这对于自动化实验和执行超参数调优非常有用。

通过在命令行输入中添加一个或多个形如 ``env.a.b.param1=value`` 的元素，可以修改环境的任意参数，其中 ``a.b.param1`` 反映了参数的层级结构，例如 ``env.actions.joint_effort.scale=10.0`` 。类似地，可以使用 ``agent`` 前缀修改智能体的参数，例如 ``agent.seed=2024`` 。

这些命令行参数的设置方式与配置文件的结构完全一致。由于不同的 RL 框架使用不同的约定，参数的设置方式可能存在差异。例如，对于 *rl_games* ，随机种子将通过 ``agent.params.seed`` 设置，而对于 *rsl_rl* 、 *skrl* 和 *sb3* ，则通过 ``agent.seed`` 设置。

因此，可以使用以下语法通过 hydra 参数进行训练：

.. tab-set::
    :sync-group: rl-train

    .. tab-item:: rsl_rl
        :sync: rsl_rl

        .. code-block:: shell

            python scripts/reinforcement_learning/rsl_rl/train.py --task=Isaac-Cartpole-v0 --headless env.actions.joint_effort.scale=10.0 agent.seed=2024

    .. tab-item:: rl_games
        :sync: rl_games

        .. code-block:: shell

            python scripts/reinforcement_learning/rl_games/train.py --task=Isaac-Cartpole-v0 --headless env.actions.joint_effort.scale=10.0 agent.params.seed=2024

    .. tab-item:: skrl
        :sync: skrl

        .. code-block:: shell

            python scripts/reinforcement_learning/skrl/train.py --task=Isaac-Cartpole-v0 --headless env.actions.joint_effort.scale=10.0 agent.seed=2024

    .. tab-item:: sb3
        :sync: sb3

        .. code-block:: shell

            python scripts/reinforcement_learning/sb3/train.py --task=Isaac-Cartpole-v0 --headless env.actions.joint_effort.scale=10.0 agent.seed=2024

上述命令将以无头（headless）模式运行任务 ``Isaac-Cartpole-v0`` 的训练脚本，并将 ``env.actions.joint_effort.scale`` 参数设置为 10.0，将 ``agent.seed`` 参数设置为 2024。

.. note::

    为了保持向后兼容并提供更友好的用户体验，我们保留了形如 ``--param`` 的旧命令行参数，例如 ``--num_envs`` 、 ``--seed`` 和 ``--max_iterations`` 。这些参数的优先级高于 hydra 参数，并将覆盖 hydra 参数设置的值。


修改高级参数
-----------------------------

可调用对象
^^^^^^^^^^

可以使用 ``module:attribute_name`` 语法修改配置文件中的函数和类。例如，在 Cartpole 环境中：

.. literalinclude:: ../../../source/isaaclab_tasks/isaaclab_tasks/manager_based/classic/cartpole/cartpole_env_cfg.py
    :language: python
    :start-at: class ObservationsCfg
    :end-at: policy: PolicyCfg = PolicyCfg()
    :emphasize-lines: 9

我们可以通过 ``env.observations.policy.joint_pos_rel.func=isaaclab.envs.mdp:joint_pos`` 将 ``joint_pos_rel`` 修改为计算绝对位置而非相对位置。

将参数设置为 None
^^^^^^^^^^^^^^^^^^^^^^^^^^

要将参数设置为 None，请使用 ``null`` 关键字，它是 Hydra 中的一个特殊关键字，会自动转换为 None。在上面的示例中，我们也可以通过将其设置为 None 来禁用 ``joint_pos_rel`` 观测，即 ``env.observations.policy.joint_pos_rel=null`` 。

字典
^^^^^^^^^^^^
字典中的元素会作为层级结构中的参数来处理。例如，在 Cartpole 环境中：

.. literalinclude:: ../../../source/isaaclab_tasks/isaaclab_tasks/manager_based/classic/cartpole/cartpole_env_cfg.py
    :language: python
    :lines: 90-114
    :emphasize-lines: 11

可以使用 ``env.events.reset_cart_position.params.position_range="[-2.0, 2.0]"`` 修改 ``position_range`` 参数。这个示例展示了两点值得注意的地方：

- 我们设置的参数包含空格，因此必须用引号括起来。
- 该参数是列表，而在配置中它是元组。这是因为 Hydra 不支持元组。


修改相互依赖的参数
------------------------------------

使用命令行参数修改参数时需要特别小心。某些配置会基于其他参数执行中间计算。当参数被修改时，这些计算不会随之更新。

例如，对于 Cartpole 相机深度环境的配置：

.. literalinclude:: ../../../source/isaaclab_tasks/isaaclab_tasks/direct/cartpole/cartpole_camera_env.py
    :language: python
    :start-at: class CartpoleDepthCameraEnvCfg
    :end-at: tiled_camera.width
    :emphasize-lines: 10, 15

如果用户修改相机的宽度，即 ``env.tiled_camera.width=128`` ，那么还必须更新并输入参数 ``env.observation_space=[80,128,1]`` 。

类似地， ``__post_init__`` 方法不会随命令行输入而更新。以 ``LocomotionVelocityRoughEnvCfg`` 为例，其 post init 更新如下：

.. literalinclude:: ../../../source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/velocity_env_cfg.py
    :language: python
    :start-at: class LocomotionVelocityRoughEnvCfg
    :emphasize-lines: 23, 29, 31

这里，当修改 ``env.decimation`` 或 ``env.sim.dt`` 时，用户还需要输入更新后的 ``env.sim.render_interval`` 、 ``env.scene.height_scanner.update_period`` 和 ``env.scene.contact_forces.update_period`` 。
