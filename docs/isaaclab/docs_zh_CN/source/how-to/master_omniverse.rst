掌握面向机器人的 Omniverse
================================

NVIDIA Omniverse 提供了一整套用于 3D 内容工作流的工具。
Omniverse 中有三个主要组件（与机器人相关的）：

-  **USD Composer**：它基于一种新颖的文件格式（通用场景描述，Universal Scene
   Description），该格式来自动画社区（最初由 Pixar 提出），并在 Omniverse 中使用
-  **PhysX SDK**：这是 Omniverse 背后的主要物理引擎，
   利用基于 GPU 的并行化来处理大规模场景
-  **支持 RTX 的渲染器**：它使用 NVIDIA RTX
   GPU 中的光线追踪内核进行实时的基于物理的渲染

在这三者中，前两者需要更深入的理解，才能开始使用 Omniverse 及其组成应用
（Isaac Sim 和 Isaac Lab）。

需要学习的主要内容：

-  如何高效地使用 Composer GUI？
-  什么是 USD prim 和 schema？
-  如何组合一个 USD 场景？
-  USD 中引用（reference）与载荷（payload）有什么区别？
-  场景图实例化（scene-graph instancing）是什么意思？
-  如何在 prim 上应用 PhysX schema？可以使用哪些 schema？
-  如何用 USD 编写基本操作来创建 prim 和修改
   其属性？


第 1 部分：使用 USD Composer
------------------------------

虽然关于 NVIDIA Omniverse 已有不少`视频
教程 <https://www.youtube.com/@NVIDIA-Studio>`__ 和
`文档 <https://docs.omniverse.nvidia.com/>`__ ，
但把它们全部看完需要花费大量的时间和精力。因此，我们精选了这些资源，
引导您专门针对机器人领域使用 Omniverse。

Omniverse 与 USD 入门

-  `What is NVIDIA Omniverse? <https://youtu.be/dvdB-ndYJBM>`__
-  `What is the USD File Type? \| Getting Started in NVIDIA Omniverse <https://youtu.be/GOdyx-oSs2M>`__
-  `What Makes USD Unique in NVIDIA Omniverse <https://youtu.be/o2x-30-PTkw>`__

使用 Omniverse USD Composer

-  `Introduction to Omniverse USD Composer <https://youtu.be/_30Pf3nccuE>`__
-  `Navigation Basics in Omniverse USD Composer <https://youtu.be/kb4ZA3TyMak>`__
-  `Lighting Basics in NVIDIA Omniverse USD Composer <https://youtu.be/c7qyI8pZvF4>`__
-  `Rendering Overview in NVIDIA Omniverse USD Composer <https://youtu.be/dCvq2ZyYmu4>`__

材质与 MDL

-  `Five Things to Know About Materials in NVIDIA Omniverse <https://youtu.be/C0HmcQXaENc>`__
-  `How to apply materials? <https://docs.omniverse.nvidia.com/materials-and-rendering/latest/materials.html#applying-materials>`__

Omniverse Physics 与 PhysX SDK

-  `Basics - Setting Up Physics and Toolbar Overview <https://youtu.be/nsJ0S9MycJI>`__
-  `Basics - Demos Overview <https://youtu.be/-y0-EVTj10s>`__
-  `Rigid Bodies - Mass Editing <https://youtu.be/GHl2RwWeRuM>`__
-  `Materials - Friction Restitution and Defaults <https://youtu.be/oTW81DltNiE>`__
-  `Overview of Simulation Ready Assets Physics in Omniverse <https://youtu.be/lFtEMg86lJc>`__

导入资产

-  `Omniverse Create - Importing FBX Files \| NVIDIA Omniverse Tutorials <https://youtu.be/dQI0OpzfVHw>`__
-  `Omniverse Asset Importer <https://docs.omniverse.nvidia.com/extensions/latest/ext_asset-importer.html>`__
-  `Isaac Sim URDF impoter <https://docs.isaacsim.omniverse.nvidia.com/latest/importer_exporter/ext_isaacsim_asset_importer_urdf.html>`__


第 2 部分：Omniverse 脚本编写
------------------------------

上面的链接主要介绍了如何通过 UI 操作来使用 USD Composer 及其
功能。然而，开发者经常
需要编写脚本来执行操作。当您想要自动化某些任务，或者创建以 Omniverse 作为后端的自定义应用时，
尤其如此。本节将带您了解
Omniverse 中的脚本编写。

USD 是 Omniverse 使用的主要文件格式。因此，用于修改 USD 的
API（来自 OpenUSD）自然处于 Omniverse 的核心位置。
大多数 API 都是 C++ 的，并为它们提供了 Python 绑定。
因此，要在 Omniverse 中编写脚本，您需要理解 USD API。

.. note::

   虽然 Isaac Sim 和 Isaac Lab 试图让用户「免于」理解
   USD 的核心概念和 API，但当您开始深入代码库并针对自己的应用进行修改时，
   理解这些基础知识仍然会有很大帮助。

在深入 USD 脚本编写之前，最好先熟悉 USD 中使用的
术语。我们推荐 Houdini（一款 3D 动画软件）提供的以下
`USD 基础介绍 <https://www.sidefx.com/docs/houdini/solaris/usd.html>`__ 。
请务必阅读以下章节：

-  `Quick example <https://www.sidefx.com/docs/houdini/solaris/usd.html#quick-example>`__
-  `Attributes and primvars <https://www.sidefx.com/docs/houdini/solaris/usd.html#attrs>`__
-  `Composition <https://www.sidefx.com/docs/houdini/solaris/usd.html#compose>`__
-  `Schemas <https://www.sidefx.com/docs/houdini/solaris/usd.html#schemas>`__
-  `Instances <https://www.sidefx.com/docs/houdini/solaris/usd.html#instancing>`__
   和 `Scene-graph Instancing <https://openusd.org/dev/api/_usd__page__scenegraph_instancing.html>`__

作为对理解程度的检验，请确保您能够回答以下问题：

-  什么是 prim？Stage 中的 prim 路径是什么意思？
-  属性（attribute）与 prim 的关系是什么？
-  schema 与 prim 的关系是什么？
-  属性与 schema 有什么区别？
-  什么是资产实例化（asset instancing）？

第 3 部分：更多资源
----------------------

- `Omniverse Glossary of Terms <https://docs.isaacsim.omniverse.nvidia.com/latest/reference_material/reference_glossary.html>`__
- `Omniverse Code Samples <https://docs.omniverse.nvidia.com/dev-guide/latest/programmer_ref.html>`__
- `PhysX Limitations <https://docs.isaacsim.omniverse.nvidia.com/latest/physics/physics_resources.html>`__
- `PhysX Documentation <https://nvidia-omniverse.github.io/PhysX/physx/>`__.
