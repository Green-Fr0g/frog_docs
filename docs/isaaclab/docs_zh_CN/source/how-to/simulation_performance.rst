仿真性能与调优
====================================

仿真的性能会受到多种因素的影响，包括场景中对象的数量、物理仿真的复杂度以及所使用的硬件。
以下是一些提升性能的技巧：

1. **使用无头模式**：以无头（headless）模式运行仿真可以显著提升性能，尤其是在
   不需要渲染的情况下。可以在运行仿真器时使用 ``--headless`` 标志来启用无头模式。
2. **避免不必要的碰撞**：如果可能，减少对象之间的重叠数量，以降低仿真开销。
   仿真中过多的接触和碰撞在碰撞检测阶段开销可能很高。
3. **使用简化的物理**：考虑使用简化的物理碰撞几何体或降低仿真保真度，以获得更好的性能。
   这可以通过修改资产以及调整仿真配置中的物理参数来实现。
4. **使用 CPU/GPU 仿真**：如果您的场景只包含少量关节体或刚体，考虑使用 CPU 仿真
   以获得更好的性能。对于较大的场景，使用 GPU 仿真可以显著提升性能。

碰撞几何体
--------------------

碰撞几何体用于定义仿真中对象在碰撞检测时的形状。使用
简化的碰撞几何体可以提升性能并降低仿真的复杂度。

例如，如果您有一个复杂的网格（mesh），可以创建一个近似该网格形状的简化碰撞几何体。
这可以在 Isaac Sim 中通过 UI 修改碰撞网格和近似方法来完成。

此外，我们通常可以移除机器人上对训练不重要的部位的碰撞几何体。
在 Anymal-C 机器人上，我们保留了膝盖和脚部的碰撞几何体，但移除了
腿部其他部位的碰撞几何体，以优化性能。

更简单的碰撞几何体（例如球体等图元形状）也会比复杂网格带来更好的性能。
例如，SDF 网格碰撞体的开销会比一个简单球体高。

注意，圆柱体和圆锥体碰撞几何体对与三角网格的平滑碰撞有特殊支持，
以获得更好的轮式仿真行为。这会带来性能开销，并且不一定总是需要的。要禁用此特性，
可以设置 Stage 参数 ``--/physics/collisionApproximateCylinders=true`` 和 ``--/physics/collisionApproximateCones=true`` 。

在 GPU RL 工作负载中，另一个需要注意的是有关 ``Convex Hull`` （凸包）近似网格碰撞几何体
的 GPU 兼容性警告。如果输入网格具有较高的纵横比（例如细长的形状），凸包近似可能与 GPU 仿真不兼容，
从而触发会显著影响性能的 CPU 回退。

CPU 回退警告如下所示：``[Warning] [omni.physx.cooking.plugin] ConvexMeshCookingTask: failed to cook GPU-compatible mesh,
collision detection will fall back to CPU. Collisions with particles and deformables will not work with this mesh.`` 。
合适的变通方法包括切换到包围盒（bounding cube）近似，或者在该几何体不属于动态刚体时
使用静态三角网格碰撞体。

Linux 上的 CPU Governor 设置
------------------------------

CPU governor 决定 CPU 的工作时钟频率范围和调节方式。这可能是 Isaac Sim 性能的一个限制因素。为获得最大性能，CPU governor 应设置为 ``performance`` 。要修改 CPU governor，请运行以下命令：

.. code-block:: bash

    sudo apt-get install linux-tools-common
    cpupower frequency-info # Check available governors
    sudo cpupower frequency-set -g performance # Set governor with root permissions

.. note::

    并非所有系统都提供所有 governor。启用更高时钟频率的 governor 通常更侧重于性能，
    会为 Isaac Sim 带来更好的性能。

其他性能指南
-----------------------------

有许多方法可以「调优」仿真的性能，但您选择的方式很大程度上取决于您要仿真的内容。一般来说，
您首先应该从 `physics engine <https://docs.omniverse.nvidia.com/kit/docs/omni_physics/107.3/dev_guide/guides.html>`_
（物理引擎）寻找性能提升空间。仅次于渲染和运行深度学习模型，
物理引擎是计算开销最大的部分。调优物理仿真，将其范围限制在仅涉及目标任务，是寻找性能提升的绝佳起点。

我们最近发布了新的 `gripper tuning guide <https://docs.omniverse.nvidia.com/kit/docs/omni_physics/107.3/dev_guide/guides/gripper_tuning_example.html>`_
（夹爪调优指南），专门针对接触与抓取调优。如果您打算使用机器人夹爪，请先阅读它。
更多细节，您还应该查看这些指南！

* `Isaac Sim Performance Optimization Handbook <https://docs.isaacsim.omniverse.nvidia.com/latest/reference_material/sim_performance_optimization_handbook.html>`_
* `Omni Physics Simulation Performance Guide <https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/dev_guide/guides/physics-performance.html>`_
