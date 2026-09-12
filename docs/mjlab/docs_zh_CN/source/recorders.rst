.. _recorders:

记录器
=========

记录器管理器提供了在 rollout 期间记录数据的生命周期钩子。与奖励不同，记录器对
优化循环没有任何影响。它们的存在纯粹是为了让你能够捕获观测、动作或任何其他
环境状态，而无需修改 mjlab 内部实现。

每个记录器项都是你实现的一个类。mjlab 会在恰当的时机调用其方法，并把所有 I/O
决策留给你。如果 ``ManagerBasedRlEnvCfg`` 上的 ``recorders`` 字典为空，环境会
替换为一个轻量的 no-op 管理器，开销为零。


生命周期钩子
---------------

管理器为每个项暴露三个钩子：

``record_pre_reset(env_ids)``
    在 ``env.step()`` 内部、即将重置已终止的环境之前调用。``obs_buf`` 保存的是
    *上一步* 结束时的观测（即智能体用来选择终端动作的输入，而不是动作执行后的
    终端状态）。``action_manager.action`` 保存终端动作，在这里仍然有效；紧随
    其后的 ``_reset_idx`` 会将这些环境上的动作清零。``reward_buf`` 保存终端奖励。
    这里是记录终端转移 ``(obs_t, action_t, reward_t, done=True)`` 的正确位置。

``record_post_reset(env_ids)``
    在重置完成且新观测可用之后调用。它在 ``env.reset()`` 结束时（针对所有环境）
    以及 ``env.step()`` 内每批已终止的环境被重置之后触发。``obs_buf[env_ids]``
    保存新回合的初始观测；``action_manager.action[env_ids]`` 为零。用它来初始化
    每回合状态或记录第一个观测。

``record_post_step()``
    在每个 ``env.step()`` 结束时、观测更新后调用。对于本步中发生重置的环境，
    ``action_manager.action`` 已被清零，且 ``obs_buf`` 保存的是新回合的初始状态，
    而不是动作执行后的终端观测。请使用 ``record_pre_reset`` 记录这些环境的终端
    转移，并用 ``self._env.reset_buf`` 来识别哪些环境发生了重置。

``close()``
    在环境关闭时调用。在这里释放文件句柄并刷新缓冲区。


编写记录器项
------------------------

继承 :class:`~mjlab.managers.RecorderTerm` 并覆盖所需的钩子。环境可以通过
``self._env`` 访问，从而可以使用 ``self._env.obs_buf``、
``self._env.action_manager.action`` 以及所有其他管理器。

.. code-block:: python

    import csv
    from mjlab.managers import RecorderTerm, RecorderTermCfg

    class CsvRecorder(RecorderTerm):
        def __init__(self, cfg, env):
            super().__init__(cfg, env)
            self._file = open(cfg.params["path"], "w", newline="")
            self._writer = csv.writer(self._file)

        def record_pre_reset(self, env_ids):
            # Terminal transition: action is still intact here.
            # It will be zeroed by _reset_idx immediately after this returns.
            obs = self._env.obs_buf["actor"][env_ids].cpu().numpy()
            act = self._env.action_manager.action[env_ids].cpu().numpy()
            for o, a in zip(obs, act):
                self._writer.writerow(o.tolist() + a.tolist())

        def record_post_step(self):
            # Skip envs that just reset: their terminal pair was written
            # in record_pre_reset and their action is now zeroed.
            mask = ~self._env.reset_buf
            obs = self._env.obs_buf["actor"][mask].cpu().numpy()
            act = self._env.action_manager.action[mask].cpu().numpy()
            for o, a in zip(obs, act):
                self._writer.writerow(o.tolist() + a.tolist())

        def close(self):
            self._file.close()

该记录器项会收到完整的 ``cfg`` 对象，因此可以读取你在 ``cfg.params`` 中放入的
任何值。


注册
------------

将该记录器项添加到环境配置的 ``recorders`` 字典中：

.. code-block:: python

    from dataclasses import dataclass, field
    from mjlab.managers import RecorderTermCfg

    @dataclass
    class MyEnvCfg(SomeTaskEnvCfg):
        recorders: dict = field(default_factory=lambda: {
            "csv": RecorderTermCfg(
                func=CsvRecorder,
                params={"path": "rollout.csv"},
            )
        })

多个记录器项可以注册在不同的键下并一起运行。

.. note::

    ``func`` 必须是 :class:`~mjlab.managers.RecorderTerm` 的子类。不支持基于
    函数的记录器项，因为记录器项是有状态的。
