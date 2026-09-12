可复现性与确定性
-------------------------------

在相同的硬件和 Isaac Sim（进而 PhysX）版本下，对于包含刚体和关节体（articulation）的场景，仿真会产生
完全相同的结果。然而，由于浮点精度和舍入误差，仿真结果可能
因不同的硬件配置而有所差异。
目前，PhysX 不保证任何包含非刚体（例如布料
或软体）的场景具有确定性。更多信息，请参阅 `PhysX Determinism documentation`_ 。

基于上述内容，Isaac Lab 提供了确定性仿真，确保不同运行之间的仿真
结果一致。这是通过为
仿真环境和物理引擎使用相同的随机种子来实现的。在构建环境时，随机种子
通过 :meth:`~isaaclab.utils.seed.configure_seed` 方法被设置为一个固定值。该方法会全局地为 CPU 和
GPU 设置随机种子，涵盖包括 PyTorch 和
NumPy 在内的不同库。

在随附的工作流脚本中，学习智能体配置文件或
命令行参数中指定的种子用于设置环境的随机种子。这确保了
仿真结果在不同运行之间可复现。根据采用管理器式（manager-based）还是直接式（direct）环境实现，
种子分别被设置到环境参数 :attr:`isaaclab.envs.ManagerBasedEnvCfg.seed` 或 :attr:`isaaclab.envs.DirectRLEnvCfg.seed` 中。

关于我们对 RL 训练进行确定性测试的结果，请查看 GitHub Pull Request `#940`_ 。

.. tip::

  由于 GPU 的工作调度，在运行时修改仿真参数
  可能会改变操作的执行顺序。这是因为环境更新可能
  发生在 GPU 正忙于其他任务时。由于浮点
  数值存储的固有特性，任何对执行顺序的修改都可能导致输出数据最低
  有效位的细微变化。在模拟数千个环境和仿真帧的过程中，
  这些变化可能导致执行结果发散。

  物体物理材质的运行时域随机化是观察到此问题的一个典型示例。
  由于这些参数在底层 API 中从 CPU 传递到 GPU 的方式，
  在 GPU 上执行该过程可能同时引入确定性和仿真问题。
  因此，强烈建议仅在设置阶段、即环境开始步进之前执行此操作。


.. _PhysX Determinism documentation: https://nvidia-omniverse.github.io/PhysX/physx/5.4.1/docs/API.html#determinism
.. _#940: https://github.com/isaac-sim/IsaacLab/pull/940
