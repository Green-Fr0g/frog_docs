已知问题
========

.. attention::

    关于已知问题及其解决方法，也请参阅 `Omniverse Isaac Sim 文档`_。

重置环境后数据值陈旧
--------------------

重置环境时，资产和传感器的部分数据字段不会更新。
这些包括运动链中各连杆的位姿、相机图像、接触传感器读数
以及激光雷达点云。这是一个已知问题，与 PhysX 和
渲染引擎在 Omniverse 中的工作方式有关。

许多物理引擎将仿真步进实现为两级调用：``forward()`` 和 ``simulate()``，
分别用于更新运动学状态和动力学状态。遗憾的是，PhysX 只有
一个单独的 ``step()`` 调用，将这两个操作合并在一起。由于计算需要经过 GPU
内核，要拆分这些操作对它们来说并不容易。因此，目前
无法在设置根状态和/或关节状态后，通过一次 forward 调用来更新
各连杆的运动学状态。这既影响初始化，也影响按回合进行的重置。

同样，对于与 RTX 渲染相关的传感器（例如相机），在设置传感器状态后，
其数据不会立即更新。渲染引擎的更新与
仿真器的 ``step()`` 调用绑定在一起，而该调用只有在仿真向前步进时才会被执行。
这意味着重置后传感器数据不会立即更新，而是会保留
过时的值。

虽然上述行为是错误的，但目前没有直接的解决方法。根据我们
使用 IsaacGym 的经验，重置值对智能体学习的影响程度，关键取决于
环境终止的频率。最终，如果智能体能够成功学习，这个频率会下降，
也就不会那么明显地影响性能。

我们已向 Omniverse 相应团队提交了功能请求，希望能完全控制
仿真应用不同部分的步进。不过，目前该功能请求还没有
确定的时间表。

.. note::
    从 Isaac Lab 1.2 开始，我们在
    :attr:`~isaaclab.assets.ArticulationData.body_state_w` 属性内部引入了 PhysX 运动学更新调用。这一变通方法
    确保在设置关节体的根状态或关节状态时，各连杆的状态
    会被更新。


相机初始帧出现空白
------------------

在独立脚本中使用 :class:`~isaaclab.sensors.Camera` 传感器时，最开始的几帧
可能是空白的。这是仿真器的一个已知问题：它需要经过若干步才能正确加载材质
纹理并填充渲染目标。

一种变通的做法是：在初始化相机传感器并设置
其位姿之后，加入以下代码：

.. code-block:: python

    from isaaclab.sim import SimulationContext

    sim = SimulationContext.instance()

    # note: the number of steps might vary depending on how complicated the scene is.
    for _ in range(12):
        sim.render()


对标记（marker）使用可实例化资产
--------------------------------

对标记使用 `可实例化资产`_ 时，标记无法正常工作，因为 Omniverse 在使用
:class:`UsdGeom.PointInstancer` schema 时不支持可实例化资产。这是一个已知问题，希望在
未来的版本中能够修复。

如果对标记使用可实例化资产，标记类会移除该资产的所有物理属性。
由于可实例化资产的物理属性存储在可实例化资产自身的 USD 文件中，
而不是存储在其 Stage 引用的 USD 文件中，因此这一移除操作会沿该资产的
其他引用被复制扩散。

.. _可实例化资产: https://docs.omniverse.nvidia.com/app_isaacsim/app_isaacsim/tutorial_gym_instanceable_assets.html
.. _Omniverse Isaac Sim 文档: https://docs.isaacsim.omniverse.nvidia.com/latest/overview/known_issues.html#


退出进程
--------

使用 ``Ctrl+C`` 退出进程时，偶尔会出现以下错误：

.. code-block:: bash

	[Error] [omni.physx.plugin] Subscription cannot be changed during the event call.

这是由于进程终止发生在某个物理事件调用过程中，
不会影响 Isaac Lab 的功能。可以安全地忽略该错误
消息并继续终止进程。在 Windows 系统上，请使用
``Ctrl+Break`` 或 ``Ctrl+fn+B`` 来终止进程。


URDF 导入器：固定关节的未解析引用
---------------------------------

从 Isaac Sim 5.1 开始，当通过 ``fixed_joint`` 元素连接的连杆在其 URDF 连杆条目中指定了质量和惯量时，
即使 ``merge-joint`` 设为 True，这些连杆也不再被合并。
这是预期行为——这些连杆被视为完整刚体，而不是零质量的参考坐标系。
不过，目前的 USD 导入器在检测到这类连杆缺少视觉或碰撞体时，会抛出
``ReportError`` 警告，提示存在未解析的引用。这是导入器的一个已知缺陷；
它会创建指向并不存在的视觉元素的引用。在导入器更新之前，可以安全地忽略
这些警告。


Conda 中的 GLIBCXX 错误
-----------------------

在 Isaac Sim 5.0 中，我们观察到从 conda 环境运行某些工作流时，会以 ``OSError`` 退出，
并提示 ``version 'GLIBCXX_3.4.30' not found``。
该问题似乎源于在启动 ``AppLauncher`` 之前导入 torch 或与 torch 相关的软件包
（例如 tensorboard）。作为一种变通方法，请确保所有 torch 导入都发生在
``AppLauncher`` 实例创建之后，这样应该可以解决该错误。
