.. _migration_guide:

迁移指南（Isaac Sim）
=====================

从 Isaac Sim 4.2 迁移到 4.5 及更高版本会带来 API、Isaac Sim 扩展与类的大量变化。
本文档概述了这些变化，以及如何将你的代码迁移到新的 API。


Isaac Sim 扩展的重命名
----------------------

此前，Isaac Sim 扩展一直遵循 ``omni.isaac.*`` 的命名约定，
例如 ``omni.isaac.core``。在 Isaac Sim 4.5 中，Isaac Sim 扩展被重命名，
改用前缀 ``isaacsim`` 来替代 ``omni.isaac``。此外，为准备一个更模块化、
可由用户通过应用模板进行定制的框架，许多扩展被重命名并拆分为多个扩展。

其中，Isaac Lab 中常用的以下 Isaac Sim 扩展重命名如下：

* ``omni.isaac.cloner`` --> ``isaacsim.core.cloner``
* ``omni.isaac.core.prims`` --> ``isaacsim.core.prims``
* ``omni.isaac.core.simulation_context`` --> ``isaacsim.core.api.simulation_context``
* ``omni.isaac.core.utils`` --> ``isaacsim.core.utils``
* ``omni.isaac.core.world`` --> ``isaacsim.core.api.world``
* ``omni.isaac.kit.SimulationApp`` --> ``isaacsim.SimulationApp``
* ``omni.isaac.ui`` --> ``isaacsim.gui.components``


URDF 与 MJCF 导入器的重命名
---------------------------

从 Isaac Sim 4.5 开始，URDF 和 MJCF 导入器被重命名，以与 Isaac Sim 中的其他扩展
保持更一致的命名。这些导入器作为开源项目发布在 isaac-sim GitHub 上。

由于扩展名称的变化，Python 模块名也随之改变：

* URDF 导入器：:mod:`isaacsim.asset.importer.urdf`（此前为 :mod:`omni.importer.urdf`）
* MJCF 导入器：:mod:`isaacsim.asset.importer.mjcf`（此前为 :mod:`omni.importer.mjcf`）

在 Isaac Sim 界面中，现在可以在文件浏览器中选择相应的 .urdf 或 .xml 文件后，
直接从 File > Import 菜单访问 URDF 和 MJCF 导入器。


URDF 导入器的变化
-----------------

Isaac Sim 4.5 为 URDF 导入器带来了一些更新，全新的界面让我们从 URDF 导入机器人时
可以进行更好的配置。因此，Isaac Lab 的 URDF 转换器也进行了相应更新以反映这些变化。
:class:`UrdfConverterCfg` 新增了一些设置，例如用于配置驱动器增益的 :class:`PDGainsCfg`
和 :class:`NaturalFrequencyGainsCfg` 类。

需要特别注意的一个破坏性变更：:attr:`UrdfConverterCfg.JointDriveCfg.gains` 属性
必须是 :class:`PDGainsCfg` 或 :class:`NaturalFrequencyGainsCfg` 类型。

:class:`PDGainsCfg` 的刚度必须显式指定，如下所示：

.. code::python

    joint_drive=sim_utils.UrdfConverterCfg.JointDriveCfg(
        gains=sim_utils.UrdfConverterCfg.JointDriveCfg.PDGainsCfg(stiffness=None, damping=None)
    )

对于 :class:`NaturalFrequencyGainsCfg`，必须指定 :attr:`natural_frequency`。


omni.isaac.core 类的重命名
--------------------------

Isaac Sim 4.5 对 Isaac Lab 中常用的核心 prim 类引入了一些命名变化。这些变化影响到
prim 类的单个对象版本和 ``View`` 版本，包括 Articulation、RigidPrim、XFormPrim 等。
单对象类的名称现在加上 ``Single`` 前缀，例如 ``SingleArticulation``；
而张量化的 View 类则去掉了 ``View`` 后缀。

各类的具体重命名如下：

* ``Articulation`` --> ``SingleArticulation``
* ``ArticulationView`` --> ``Articulation``
* ``ClothPrim`` --> ``SingleClothPrim``
* ``ClothPrimView`` --> ``ClothPrim``
* ``DeformablePrim`` --> ``SingleDeformablePrim``
* ``DeformablePrimView`` --> ``DeformablePrim``
* ``GeometryPrim`` --> ``SingleGeometryPrim``
* ``GeometryPrimView`` --> ``GeometryPrim``
* ``ParticleSystem`` --> ``SingleParticleSystem``
* ``ParticleSystemView`` --> ``ParticleSystem``
* ``RigidPrim`` --> ``SingleRigidPrim``
* ``RigidPrimView`` --> ``RigidPrim``
* ``XFormPrim`` --> ``SingleXFormPrim``
* ``XFormPrimView`` --> ``XFormPrim``


Isaac Lab 扩展与文件夹的重命名
------------------------------

为了对应 Isaac Sim 4.5 的变化，我们也对 Isaac Lab 的目录和扩展做了一些更新。
此前位于 ``source/extensions`` 下的所有扩展现在直接位于 ``source/`` 目录下。
``source/apps`` 和 ``source/standalone`` 文件夹已移到根目录，现分别称为
``apps/`` 和 ``scripts/``。

Isaac Lab 的扩展已重命名为：

* ``omni.isaac.lab`` --> ``isaaclab``
* ``omni.isaac.lab_assets`` --> ``isaaclab_assets``
* ``omni.isaac.lab_tasks`` --> ``isaaclab_tasks``

此外，我们将此前的 ``source/standalone/workflows`` 目录拆分为 ``scripts/imitation_learning``
和 ``scripts/reinforcement_learning`` 目录。RSL RL、Stable-Baselines、RL_Games、SKRL 和 Ray 目录
位于 ``scripts/reinforcement_learning`` 下，而 Robomimic 和新的 Isaac Lab Mimic 目录位于
``scripts/imitation_learning`` 下。

为帮助你在自己的项目中完成 Isaac Lab 扩展的重命名，我们提供了一个 `简单脚本`_，它会遍历
本地 Isaac Lab 项目中的 ``source`` 和 ``docs`` 目录，并替换所有已重命名的
目录和 import。**请自行承担使用该脚本的风险，因为它会直接覆盖源文件。**


Isaac Lab 扩展的重组
--------------------

随着 ``isaaclab_mimic`` 的引入（用于支持模仿学习的数据生成工作流），
我们还将此前 ``isaaclab_tasks`` 下的 ``wrappers`` 文件夹拆分出来，形成独立模块 ``isaaclab_rl``。
这个新扩展将包含针对 Isaac Lab 所支持的各种 RL 库的强化学习专用封装。

新的 ``isaaclab_mimic`` 扩展还将取代此前 ``robomimic`` 文件夹下的模仿学习脚本。
我们移除了旧的数据采集和数据集准备脚本，改用新的 mimic 工作流。对于
偏好使用此前脚本的用户，它们仍可在先前的发布分支中找到。

此外，我们还将 ``isaaclab_assets`` 扩展重组为 ``robots`` 和 ``sensors``
两个子目录。这样可以更清晰地区分该扩展中提供的预定义配置。
对于任何现有的 import，例如 ``from omni.isaac.lab_assets.anymal import ANYMAL_C_CFG``，请将其替换为
``from isaaclab.robots.anymal import ANYMAL_C_CFG``。


.. _简单脚本: https://gist.github.com/kellyguo11/3e8f73f739b1c013b1069ad372277a85
