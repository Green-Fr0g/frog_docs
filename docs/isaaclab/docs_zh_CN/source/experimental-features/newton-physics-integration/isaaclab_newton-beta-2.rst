Isaac Lab - Newton Beta 2
=========================

Isaac Lab - Newton Beta 2（feature/newton 分支）为 Isaac Lab 提供了 Newton 物理引擎集成。我们重构了代码，使其不仅能支持 PhysX 和 Newton，还能支持任何其他物理引擎，让用户可以在需要时将自己的物理引擎接入 Isaac Lab。为此，我们引入了各「仿真接口」的基类实现，例如 :class:`~isaaclab.assets.articulation.Articulation` 和 :class:`~isaaclab.sensors.ContactSensor`。它们提供了一组所有物理引擎都必须实现的抽象方法。这进而使所有默认的 Isaac Lab 环境都能与任何物理引擎协同工作。这也让我们能够确保 Isaac Lab - Newton Beta 2 与 Isaac Lab 2.X 向后兼容。对于引擎特有的调用，用户可以获取物理引擎的底层视图并直接调用该引擎特有的 API。

不过，在重构代码的同时，我们也在设法降低 Isaac Lab 本身的开销。为了将开销降到最低，我们正在将所有底层代码从 torch 迁移出去，转而大量依赖 warp。这让我们能编写更高效的底层代码，并利用 cuda-graph 技术。但这意味着 ``data classes`` （如 :class:`~isaaclab.assets.articulation.ArticulationData` 或 :class:`~isaaclab.sensors.ContactSensorData`）将只返回 warp 数组。因此，用户如果有需要，必须调用 ``wp.to_torch`` 将其转换为 torch 张量。我们的 setter/writer 将同时支持 warp 数组和 torch 张量，并在底层使用最优策略更新 warp 数组。这能将用户迁移到 Isaac Lab - Newton Beta 2 所需的改动降到最低。

writer 和 setter 的另一个新特性是支持传入掩码和完整数据（不同于 Isaac Lab 2.X 中的索引和部分数据）。注意，该特性与提供索引和部分数据的能力并存，默认行为仍是提供索引和部分数据。但如果使用 warp，用户必须提供掩码和完整数据。总体而言，我们鼓励用户采用这一新特性，因为使用得当的话，它能减少运行时的内存分配，并带来更好的性能。

在优化方面，我们决定更改四元数约定。原本 Isaac Lab 和 Isaac Sim 都采用 ``wxyz`` 约定，但由于 PhysX 使用 ``xyzw`` 约定，我们的 setter/writer 中存在多次与 ``xyzw`` 之间的来回转换。既然 Newton 和 Warp 也都使用 ``xyzw`` 约定，我们决定将默认约定改为 ``xyzw``。这意味着我们所有的 API 现在都将以 ``xyzw`` 约定返回四元数。对于没有使用我们 :mod:`~isaaclab.utils.math` 模块的自定义 mdp 来说，这可能是一个破坏性变更。虽然这个改动很大，但它能让用户直接使用仿真视图时的体验更加一致，并消除不必要的转换。

最后，除了新的 isaaclab_newton 扩展之外，我们还引入了新的 isaaclab_experimental 和 isaaclab_task_experimental 扩展。这些扩展让我们能够快速将新功能带入 Isaac Lab 主线，同时给它们足够的时间成熟，之后再完全集成到核心 Isaac Lab 扩展中。在本版本中，我们为直接式 RL 任务引入了 cuda-graph 支持。这大幅降低了 Isaac Lab 的开销，使训练更快。欢迎试用并告诉我们你的想法。

.. code-block:: bash

    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Cartpole-Direct-Warp-v0 --num_envs 4096 --headless

.. code-block:: bash

    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Ant-Direct-Warp-v0 --num_envs 4096 --headless

.. code-block:: bash

    ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Humanoid-Direct-Warp-v0 --num_envs 4096 --headless


后续计划
========

Isaac Lab 3.0 是 Isaac Lab 即将发布的版本，它将兼容 Isaac Sim 6.0，同时支持新的 Newton 物理引擎。用户将可以在 Newton 物理引擎或 PhysX 上训练策略。为适应这一点，需要进行大规模代码重构。在本节中，我们将介绍其中一些改动、它们对 Isaac Lab 2.X 用户的影响，以及如何迁移到 Isaac Lab 3.0。当前的 ``feature/newton`` 分支可以让读者预先一窥未来。虽然内部代码结构的改动很大，但用户 API 的改动很小。
