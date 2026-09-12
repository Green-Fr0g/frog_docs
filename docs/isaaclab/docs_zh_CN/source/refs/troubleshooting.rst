技巧与故障排查
==============

.. note::

    以下列出我们在常见工作流中使用的一些常用技巧和故障排查方法。
    如需更多帮助，也请查阅 `Omniverse 上的故障排查页面
    <https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/linux_troubleshooting.html>`__。


调试物理仿真稳定性问题
----------------------

在向 Isaac Lab 导入新机器人或搭建新环境时，如果资产没有用合理的仿真参数进行调优，
经常会出现仿真不稳定的情况。在强化学习场景中，这通常会导致无效的仿真状态产生 NaN，
并传播到整个学习流水线中。

如果出现这种情况，我们建议查阅
`关节体与机器人仿真稳定性指南 <https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/dev_guide/guides/articulation_stability_guide.html>`_，
其中推荐了各种仿真参数和最佳实践，可帮助机器人仿真获得更好的稳定性。

此外，`Omniverse PhysX 可视化调试器 <https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/extensions/ux/source/omni.physx.pvd/docs/dev_guide/physx_visual_debugger.html>`_
可以记录 PhysX 仿真的数据，这通常有助于定位仿真问题并辅助调试过程。

要在 Isaac Lab 中启用 OmniPVD 录制，请在启动 Isaac Lab 进程时，向命令行添加相关的 kit 参数

.. code:: bash

    ./isaaclab.sh -p scripts/demos/bipeds.py --kit_args "--/persistent/physics/omniPvdOvdRecordingDirectory=/tmp/ --/physics/omniPvdOutputEnabled=true" --headless


查看仿真器的内部日志
--------------------

从独立脚本运行仿真器时，它会把警告和错误打印到终端。同时，
它还会把内部消息写入一个文件。这些内容对于调试和理解仿真器的
内部状态很有用。根据你的系统不同，日志文件的位置可参见
`此处 <https://docs.isaacsim.omniverse.nvidia.com/latest/installation/install_faq.html#common-path-locations>`_。

要获取日志文件的确切位置，你需要查看运行独立脚本时终端输出的
前几行。日志文件位置会在终端输出的开头打印出来。例如：

.. code:: bash

    [INFO] Using python from: /home/${USER}/git/IsaacLab/_isaac_sim/python.sh
    ...
    Passing the following args to the base kit application:  []
    Loading user config located at: '.../data/Kit/Isaac-Sim/2023.1/user.config.json'
    [Info] [carb] Logging to file: '.../logs/Kit/Isaac-Sim/2023.1/kit_20240328_183346.log'


在上面的示例中，日志文件位于 ``.../logs/Kit/Isaac-Sim/2023.1/kit_20240328_183346.log``，
``...`` 是用户日志目录的路径。该日志文件的文件名为 ``kit_20240328_183346.log``

你可以打开该文件来查看仿真器的内部日志。另外，在报告问题时，请附上
这个日志文件，以便帮助我们调试问题。

修改仿真器的日志通道级别
------------------------

默认情况下，仿真器在终端中记录 ``WARN`` 级别及以上的消息。你可以修改日志
通道级别以获得更详细的日志。日志通道级别可以通过 Omniverse 的日志系统进行设置。

要获得更详细的日志，你可以使用以下标志运行应用：

* ``--info``：该标志记录 ``INFO`` 级别及以上的消息。
* ``--verbose``：该标志记录 ``VERBOSE`` 级别及以上的消息。

例如，要以 verbose 日志级别运行独立脚本，可以使用以下命令：

.. code-block:: bash

    # Run the standalone script with info logging
    ./isaaclab.sh -p scripts/tutorials/00_sim/create_empty.py --headless --info

如需更细粒度的控制，你可以通过 ``logger`` 模块修改日志通道。
更多信息请参阅其 `文档 <https://docs.python.org/3/library/logging.html>`__。


仿真启动时加载时间过长
----------------------

第一次运行仿真器时，加载会花费很长时间。这是因为
仿真器需要编译着色器并加载资产。后续运行的启动应该会更快，
但仍可能需要一些时间。

请注意，一旦 Isaac Sim 应用加载完成，环境创建时间可能会随
环境数量线性增长。如果以数千个环境运行，或者每个环境包含大量
资产，请预期更长的加载时间。我们正在持续
改进这方面所需的时间。

当已有一个 Isaac Sim 实例在运行时，在另一个进程中再启动一个 Isaac Sim 实例，
首次启动时可能会看起来卡住。请耐心等待一段时间，因为
第二个进程由于着色器编译更慢，启动会花费更长时间。


在 GPU 上运行仿真时出现「PhysX error」
---------------------------------------

使用 GPU 流水线时，用于物理仿真的缓冲区只会在仿真开始时
在 GPU 上分配一次。这意味着它们不会随着场景中碰撞数量或物体数量的
变化而动态增长。如果场景中的碰撞或物体数量
超出缓冲区大小，仿真就会失败，并报出类似以下的错误：

.. code:: bash

    PhysX error: the application need to increase the PxgDynamicsMemoryConfig::foundLostPairsCapacity
    parameter to 3072, otherwise the simulation will miss interactions

在这种情况下，你需要增大传递给
:class:`~isaaclab.sim.SimulationContext` 类的缓冲区大小。缓冲区大小可以通过在
:class:`~isaaclab.sim.PhysxCfg` 类中设置
:attr:`~isaaclab.sim.PhysxCfg.gpu_found_lost_pairs_capacity` 参数来增大。例如，要将缓冲区大小增大到
4096，可以使用以下代码：

.. code:: python

    import isaaclab.sim as sim_utils

    sim_cfg = sim_utils.SimulationConfig()
    sim_cfg.physx.gpu_found_lost_pairs_capacity = 4096
    sim = SimulationContext(sim_params=sim_cfg)

关于可用于配置仿真的参数，更多细节请参阅 :class:`~isaaclab.sim.SimulationCfg` 的文档。


避免仿真器中的内存泄漏
----------------------

当 C++ 回调注册到 Python 对象上时，Isaac Sim 仿真器可能会出现内存泄漏。
发生这种情况的原因是，类中的回调函数持有与其关联的 Python 对象的引用。
结果，Python 的垃圾回收机制无法回收与这些对象关联的内存，
导致相应的 C++ 对象无法被销毁。随着时间推移，这会导致
内存泄漏和资源占用增加。

要避免 Isaac Sim 仿真器中的内存泄漏，在向仿真器注册回调时
必须使用弱引用。这样可以确保 Python 对象在不再需要时能够被垃圾回收，
从而避免内存泄漏。可以使用 Python 标准库中的
`weakref <https://docs.python.org/3/library/weakref.html>`_ 模块来实现这一点。


例如，考虑一个带有回调函数 ``on_event_callback`` 的类，该回调需要注册到
仿真器中。如果在传递回调时使用对 ``MyClass`` 对象的强引用，
``MyClass`` 对象的引用计数就会增加。这会阻止 ``MyClass`` 对象
在不再需要时被垃圾回收，也就是说，``__del__`` 析构函数不会被
调用。

.. code:: python

    import omni.kit

    class MyClass:
        def __init__(self):
            app_interface = omni.kit.app.get_app_interface()
            self._handle = app_interface.get_post_update_event_stream().create_subscription_to_pop(
                self.on_event_callback
            )

        def __del__(self):
            self._handle.unsubscribe()
            self._handle = None

        def on_event_callback(self, event):
            # do something with the message


要解决这个问题，关键是在注册回调时使用弱引用。虽然这种方式
会让代码稍显冗长，但它可以确保 ``MyClass`` 对象在不再使用时
能够被垃圾回收。修改后的代码如下：

.. code:: python

    import omni.kit
    import weakref

    class MyClass:
        def __init__(self):
            app_interface = omni.kit.app.get_app_interface()
            self._handle = app_interface.get_post_update_event_stream().create_subscription_to_pop(
                lambda event, obj=weakref.proxy(self): obj.on_event_callback(event)
            )

        def __del__(self):
            self._handle.unsubscribe()
            self._handle = None

        def on_event_callback(self, event):
            # do something with the message


在这段修改后的代码中，注册回调时使用了弱引用 ``weakref.proxy(self)``，
从而使 ``MyClass`` 对象能够被正确地垃圾回收。

遵循这一模式，你就可以避免内存泄漏，保持更高效、更稳定的仿真。


理解崩溃时的错误日志
--------------------

很多时候仿真器会因为实现中的缺陷而崩溃。
这会让终端被大量异常信息淹没，其中一部分来自
Python 解释器调用仿真应用的 ``__del__()`` 析构函数。
这些信息通常形如下例：

.. code:: bash

    ...

    [INFO]: Completed setting up the environment...

    Traceback (most recent call last):
    File "scripts/imitation_learning/robomimic/collect_demonstrations.py", line 166, in <module>
        main()
    File "scripts/imitation_learning/robomimic/collect_demonstrations.py", line 126, in main
        actions = pre_process_actions(delta_pose, gripper_command)
    File "scripts/imitation_learning/robomimic/collect_demonstrations.py", line 57, in pre_process_actions
        return torch.concat([delta_pose, gripper_vel], dim=1)
    TypeError: expected Tensor as element 1 in argument 0, but got int
    Exception ignored in: <function _make_registry.<locals>._Registry.__del__ at 0x7f94ac097f80>
    Traceback (most recent call last):
    File "../IsaacLab/_isaac_sim/kit/extscore/omni.kit.viewport.registry/omni/kit/viewport/registry/registry.py", line 103, in __del__
    File "../IsaacLab/_isaac_sim/kit/extscore/omni.kit.viewport.registry/omni/kit/viewport/registry/registry.py", line 98, in destroy
    TypeError: 'NoneType' object is not callable
    Exception ignored in: <function _make_registry.<locals>._Registry.__del__ at 0x7f94ac097f80>
    Traceback (most recent call last):
    File "../IsaacLab/_isaac_sim/kit/extscore/omni.kit.viewport.registry/omni/kit/viewport/registry/registry.py", line 103, in __del__
    File "../IsaacLab/_isaac_sim/kit/extscore/omni.kit.viewport.registry/omni/kit/viewport/registry/registry.py", line 98, in destroy
    TypeError: 'NoneType' object is not callable
    Exception ignored in: <function SettingChangeSubscription.__del__ at 0x7fa2ea173e60>
    Traceback (most recent call last):
    File "../IsaacLab/_isaac_sim/kit/kernel/py/omni/kit/app/_impl/__init__.py", line 114, in __del__
    AttributeError: 'NoneType' object has no attribute 'get_settings'
    Exception ignored in: <function RegisteredActions.__del__ at 0x7f935f5cae60>
    Traceback (most recent call last):
    File "../IsaacLab/_isaac_sim/extscache/omni.kit.viewport.menubar.lighting-104.0.7/omni/kit/viewport/menubar/lighting/actions.py", line 345, in __del__
    File "../IsaacLab/_isaac_sim/extscache/omni.kit.viewport.menubar.lighting-104.0.7/omni/kit/viewport/menubar/lighting/actions.py", line 350, in destroy
    TypeError: 'NoneType' object is not callable
    2022-12-02 15:41:54 [18,514ms] [Warning] [carb.audio.context] 1 contexts were leaked
    ../IsaacLab/_isaac_sim/python.sh: line 41: 414372 Segmentation fault      (core dumped) $python_exe "$@" $args
    There was an error running python

这是使用 Isaac Sim 仿真器运行独立脚本时的一个已知错误。
请在带有 ``registry`` 的异常信息之上继续向上滚动，
以查看真正的错误日志。

在上面的情况中，真正的错误是：

.. code:: bash

    Traceback (most recent call last):
    File "scripts/imitation_learning/robomimic/tools/collect_demonstrations.py", line 166, in <module>
        main()
    File "scripts/imitation_learning/robomimic/tools/collect_demonstrations.py", line 126, in main
        actions = pre_process_actions(delta_pose, gripper_command)
    File "scripts/imitation_learning/robomimic/tools/collect_demonstrations.py", line 57, in pre_process_actions
        return torch.concat([delta_pose, gripper_vel], dim=1)
    TypeError: expected Tensor as element 1 in argument 0, but got int
