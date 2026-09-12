创建可视化标记
==============================

.. currentmodule:: isaaclab

可视化标记对于调试环境状态非常有用。它们可用于在仿真中可视化坐标系、命令以及其他信息。

虽然 Isaac Sim 提供了自己的 :mod:`isaacsim.util.debug_draw` 扩展，但它仅限于渲染点、线和样条线。
如果需要渲染更复杂的形状，可以使用 :class:`markers.VisualizationMarkers` 类。

本指南附带一个示例脚本 ``markers.py`` ，位于 ``IsaacLab/scripts/demos`` 目录中。

.. dropdown:: markers.py 的代码
   :icon: code

   .. literalinclude:: ../../../scripts/demos/markers.py
      :language: python
      :emphasize-lines: 45-90, 106-107, 136-142
      :linenos:



配置标记
-----------------------

:class:`~markers.VisualizationMarkersCfg` 类提供了一个简单的接口来配置不同类型的标记。
它接受以下参数：

- :attr:`~markers.VisualizationMarkersCfg.prim_path`：标记类对应的 Prim 路径。
- :attr:`~markers.VisualizationMarkersCfg.markers`：一个字典，指定该类处理的不同标记原型
  （marker prototype）。键是标记原型的名称，值是其生成（spawn）配置。

.. note::

   如果标记原型指定的配置带有物理属性，这些属性会被移除。
   这是因为标记并不用于仿真。

这里展示了所有可以配置的不同类型的标记。它们包括圆锥、球体等简单形状，以及坐标系、箭头等更复杂的
几何体。标记原型也可以从 USD 文件配置。

.. literalinclude:: ../../../scripts/demos/markers.py
   :language: python
   :lines: 45-90
   :dedent:


绘制标记
-------------------

要绘制标记，我们调用 :class:`~markers.VisualizationMarkers.visualize` 方法。该方法接受标记的位姿
以及要绘制的相应标记原型作为参数。

.. literalinclude:: ../../../scripts/demos/markers.py
   :language: python
   :lines: 136-142
   :dedent:


运行脚本
--------------------

要运行随附的脚本，请执行以下命令：

.. code-block:: bash

  ./isaaclab.sh -p scripts/demos/markers.py

仿真应当会启动，您可以观察到以网格形式排列的不同类型的标记。
标记会绕各自的轴旋转。此外，每隔几次旋转，它们会在网格上向前滚动一次。

要停止仿真，请关闭窗口，或在终端中使用 ``Ctrl+C`` 。
