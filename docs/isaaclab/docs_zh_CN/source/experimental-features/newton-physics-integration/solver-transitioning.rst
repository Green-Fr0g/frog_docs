求解器切换
==========

迁移到 Newton 物理引擎会引入新的物理求解器，它们通过不同的数值方法处理仿真。
虽然 Newton 支持多种不同的求解器，但我们在 Isaac Lab 中最初的重点是使用 Google DeepMind 的 MuJoCo-Warp 求解器。

物理场景本身的定义方式并没有变化——我们仍然使用 USD 作为设置场景中物体和机器人基本参数的主要方式，
并且对于当前的环境，使用的是与基于 PhysX 的 Isaac Lab 完全相同的 USD 文件。
未来这一点可能会变化，因为正在开发能够记录更多物理参数的新 USD schema。

真正需要改变的是某些求解器特定设置的配置方式。
调优这些参数可能会对仿真性能和行为都产生显著影响。

目前，我们将展示一个设置这些参数的示例，帮助你感受这些变化。
请注意，:class:`~isaaclab.sim.NewtonCfg` 取代了 :class:`~isaaclab.sim.PhysxCfg`，用于设置除 ``dt`` 之外的一切与物理仿真参数相关的内容：

.. code-block:: python

    from isaaclab.sim._impl.newton_manager_cfg import NewtonCfg
    from isaaclab.sim._impl.solvers_cfg import MJWarpSolverCfg

    solver_cfg = MJWarpSolverCfg(
        nefc_per_env=35,
        ls_iterations=10,
        cone="pyramidal",
        ls_parallel=True,
        impratio=1,
    )
    newton_cfg = NewtonCfg(
        solver_cfg=solver_cfg,
        num_substeps=1,
        debug_mode=False,
    )
    sim: SimulationCfg = SimulationCfg(dt=1 / 120, render_interval=decimation, newton_cfg=newton_cfg)


以下是对上面一些关键参数的简要说明：

* ``nefc_per_env``：这是我们希望 MuJoCo Warp 为给定环境
  预分配的约束缓冲区大小。较大的值会拖慢仿真，
  而过小的值则可能导致某些接触被遗漏。

* ``ls_iterations``：MuJoCo Warp 求解器执行的线搜索次数。
  线搜索用于寻找最优步长，对于每个求解器步，最多会执行
  ``ls_iterations`` 次线搜索。保持该数值较低
  对性能很重要。当未设置 ``ls_parallel`` 时，该数值也是上界。

* ``cone``：该参数用于在接触处理中为摩擦锥选择
  金字塔形或椭圆形近似。关于接触的更多信息，请参阅
  MuJoCo 文档：
  https://mujoco.readthedocs.io/en/stable/computation/index.html#contact

* ``ls_parallel``：该参数将线搜索从迭代执行切换为并行执行。
  启用 ``ls_parallel`` 能带来性能提升，但代价是
  仿真稳定性有所下降。为了在启用时保证良好的仿真行为，需要设置更高的
  ``ls_iterations``。相比禁用 ``ls_parallel`` 时的 ``ls_iterations`` 设置，
  通常增加约 50% 效果最佳。

* ``impratio``：这是摩擦力约束与法向力约束的阻抗比，
  可以更细粒度地控制切向力相对于法向力的
  重要程度。较大的值表示更强调更硬的
  摩擦约束以避免打滑。关于如何调优该参数（以及
  ``cone``）的更多内容，可参见 MuJoCo 文档：
  https://mujoco.readthedocs.io/en/stable/XMLreference.html#option-impratio

* ``num_substeps``：运行仿真时执行的子步数量。
  将其设置为大于 1 的值，可以在不需要 Isaac Lab 在两个子步之间处理数据的情况下
  对仿真进行抽取（decimate）。例如，在使用隐式执行器时，
  这可能很有价值。


一份更详细的迁移指南将会在后续版本中发布，其中涵盖全部可用参数并描述调优方法。
