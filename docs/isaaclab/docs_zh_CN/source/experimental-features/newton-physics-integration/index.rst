Newton 物理集成
===============

`Newton <https://newton-physics.github.io/newton/guide/overview.html>`_ 是一款面向机器人、科研和高级仿真工作流的 GPU 加速、可扩展、可微分的物理仿真引擎。它构建在 `NVIDIA Warp <https://nvidia.github.io/warp/>`_ 之上并集成了 MuJoCo Warp，为用户和开发者提供高性能仿真、现代 Python API 和灵活的架构。

Newton 是一个开源的社区驱动项目，由 NVIDIA、Google Deep Mind 和 Disney Research 共同贡献，并通过 Linux Foundation 管理。

Isaac Lab 的这个 `实验特性分支 <https://github.com/isaac-sim/IsaacLab/tree/feature/newton>`_ 提供了与 Newton 物理引擎的初步集成，目前处于活跃开发中。许多功能尚不支持，现阶段仅包含少量经典 RL 和平地运动强化学习示例。

这个 Isaac Lab 集成分支和 Newton 本身都在高强度开发中。我们计划在未来支持其他强化学习和模仿学习工作流的更多功能，但上述任务应足以作为理解 Newton 集成在 Isaac Lab 中如何工作的切入点。

我们已经通过在 Newton 与 PhysX 之间相互迁移训练好的策略，验证了 Newton 仿真的正确性。此外，我们还成功地将 Newton 训练的运动策略部署到了 G1 机器人上。更多信息请见 :ref:`此处 <sim2real>`。

Newton 可以支持 `多种求解器 <https://newton-physics.github.io/newton/api/newton_solvers.html>`_ 来处理不同类型的物理仿真，但目前 Isaac Lab 的集成主要聚焦于 MuJoCo-Warp 求解器。

该分支和 Newton 的后续更新将包括持续的性能改进以及对更多求解器的集成。

请注意，该分支不支持 PhysX 物理引擎——仅支持 Newton。我们正在考虑在 Lab 中继续支持 PhysX 的多种可行路径，欢迎用户反馈相关需求。

在 Newton 和这个 Isaac Lab 集成的早期开发阶段，你可能会遇到破坏性变更以及不完善的文档。在框架正式发布之前，我们无法提供官方支持或调试协助。感谢你在我们打造稳健、完善框架的过程中给予理解与耐心。


.. toctree::
  :maxdepth: 2
  :titlesonly:

  installation
  isaaclab_newton-beta-2
  training-environments
  visualization
  limitations-and-known-bugs
  solver-transitioning
  sim-to-sim
  sim-to-real
