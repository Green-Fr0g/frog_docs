扩展开发
=======================

Omniverse 中的一切要么是一个扩展（extension），要么是扩展的集合（一个应用程序）。它们是构成 Omniverse 生态系统基本单元的模块化包。每个扩展提供一组功能，可供其他扩展或独立应用程序使用。如果一个文件夹在 ``config`` 目录中包含 ``extension.toml`` 文件，它就会被识别为一个扩展。有关扩展的更多信息，请参阅 `Omniverse 文档 <https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/extensions_basic.html>`__。

Isaac Lab 中的每个扩展都编写为一个 Python 包，并遵循以下结构：

.. code:: bash

   <extension-name>
   ├── config
   │   └── extension.toml
   ├── docs
   │   ├── CHANGELOG.md
   │   └── README.md
   ├── <extension-name>
   │   ├── __init__.py
   │   ├── ....
   │   └── scripts
   ├── setup.py
   └── tests

``config/extension.toml`` 文件包含扩展的元数据，包括名称、版本、描述、依赖项等。Omniverse API 会使用这些信息来加载扩展。``docs`` 目录包含该扩展的文档，其中有关于该扩展的更详细信息，以及记录每个版本所做更改的 CHANGELOG 文件。

``<extension-name>`` 目录包含该扩展的主要 Python 包。它还可以包含 ``scripts`` 目录，用于存放基于 Python 的应用程序；当通过 `Extension Manager <https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/extensions_basic.html>`__ 启用该扩展时，这些应用程序会被加载到 Omniverse 中。

更具体地说，当一个扩展被启用时，``config/extension.toml`` 文件中指定的 Python 模块会被加载，并且包含 :class:`omni.ext.IExt` 类子类的脚本会被执行。

.. code:: python

   import omni.ext

   class MyExt(omni.ext.IExt):
      """My extension application."""

      def on_startup(self, ext_id):
         """Called when the extension is loaded."""
         pass

      def on_shutdown(self):
         """Called when the extension is unloaded.

         It releases all references to the extension and cleans up any resources.
         """
         pass

将扩展加载到 Omniverse 中是自动完成的，但在独立应用程序中使用该 Python 包则需要额外的步骤。为了简化构建过程，并避免理解 Omniverse 所使用的 `premake <https://premake.github.io/>`__ 构建系统，我们直接使用 `setuptools <https://setuptools.readthedocs.io/en/latest/>`__ Python 包来构建扩展提供的 Python 模块。这是由扩展目录中的 ``setup.py`` 文件完成的。

.. note::

   对于仅通过 `Extension Manager <https://docs.omniverse.nvidia.com/prod_extensions/prod_extensions/ext_extension-manager.html>`__ 加载到 Omniverse 中的扩展，不需要 ``setup.py`` 文件。

最后，``tests`` 目录包含该扩展的单元测试。这些测试使用 `unittest <https://docs.python.org/3/library/unittest.html>`__ 框架编写。需要注意的是，Omniverse 也提供了一个类似的 `测试框架 <https://docs.omniverse.nvidia.com/kit/docs/kit-manual/104.0/guide/testing_exts_python.html>`__。但是，它需要经过构建过程，并且不支持在独立应用程序中测试 Python 模块。

自定义扩展的依赖管理
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

某些扩展可能存在依赖项，需要先安装额外的软件包才能使用该扩展。Python 依赖项由 `setuptools <https://setuptools.readthedocs.io/en/latest/>`__ 包处理并在 ``setup.py`` 文件中指定，而诸如 `ROS <https://www.ros.org/>`__ 包或 `apt <https://en.wikipedia.org/wiki/APT_(software)>`__ 包等非 Python 依赖项则不由 setuptools 处理。处理这类依赖项需要一个额外的流程。

在 ``extension.toml`` 文件的 ``isaac_lab_settings`` 部分下可以指定两类依赖项：

1. **apt_deps**: 需要安装的 apt 软件包列表。这些软件包通过 `apt <https://ubuntu.com/server/docs/package-management>`__ 包管理器安装。
2. **ros_ws**: 包含 ROS 软件包的 ROS 工作区（workspace）路径。这些软件包通过 `rosdep <https://docs.ros.org/en/humble/Tutorials/Intermediate/Rosdep.html>`__ 依赖管理器安装。

作为示例，下面的 ``extension.toml`` 文件指定了该扩展的依赖项：

.. code-block:: toml

   [isaac_lab_settings]
   # apt dependencies
   apt_deps = ["libboost-all-dev"]

   # ROS workspace
   # note: if this path is relative, it is relative to the extension directory's root
   ros_ws = "/home/user/catkin_ws"

这些依赖项通过 ``tools`` 目录中提供的 ``install_deps.py`` 脚本安装。要为所有扩展安装所有依赖项，请运行以下命令：

.. code-block:: bash

   # execute from the root of the repository
   # the script expects the type of dependencies to install and the path to the extensions directory
   # available types are: 'apt', 'rosdep' and 'all'
   python tools/install_deps.py all ${ISAACLAB_PATH}/source

.. note::
   目前，该脚本会在 ``Dockerfile.base`` 和 ``Dockerfile.ros2`` 的构建过程中自动执行。这确保了在分别构建扩展之前，所有 'apt' 和 'rosdep' 依赖项都已安装完毕。


独立应用程序
~~~~~~~~~~~~~~~~~~~~~~~

在典型的 Omniverse 工作流中，先启动仿真器，然后启用扩展。Python 模块和其他 Python 应用程序的加载会在底层自动完成。虽然这是推荐的工作流，但它并不总是可行的。

例如，考虑机器人强化学习的场景。必须完全控制仿真步进以及更新的时机，而不是异步等待结果。在这种情况下，我们需要直接控制仿真，因此有必要编写独立应用程序。这些应用程序在功能上是相似的：它们使用 :class:`~isaaclab.app.AppLauncher` 启动仿真器，然后通过 :class:`~isaaclab.sim.SimulationContext` 直接控制仿真。在这些情况下，扩展中的 Python 模块**必须**在应用程序启动之后再导入。如果在应用程序启动之前导入，会导致模块缺失错误。

下面的代码片段展示了如何编写一个独立应用程序：

.. code:: python

   """Launch Isaac Sim Simulator first."""

   from isaaclab.app import AppLauncher

   # launch omniverse app
   app_launcher = AppLauncher(headless=False)
   simulation_app = app_launcher.app


   """Rest everything follows."""

   from isaaclab.sim import SimulationContext

   if __name__ == "__main__":
      # get simulation context
      simulation_context = SimulationContext()
      # reset and play simulation
      simulation_context.reset()
      # step simulation
      simulation_context.step()
      # stop simulation
      simulation_context.stop()

      # close the simulation
      simulation_app.close()


必须先启动仿真器再运行任何其他代码，因为扩展是在仿真器启动时热加载的。许多 Omniverse 模块只有在仿真器启动后才可用。更多细节，我们建议浏览 Isaac Lab 的 :ref:`tutorials`。
