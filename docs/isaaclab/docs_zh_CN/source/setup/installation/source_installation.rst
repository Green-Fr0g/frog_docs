.. _isaaclab-source-installation:

使用 Isaac Sim 源码安装
========================================

以下步骤首先从源码安装 Isaac Sim，然后从源码安装 Isaac Lab。

.. note::

   这是一种更高级的安装方法，不推荐大多数用户使用。只有当你希望同时修改
   Isaac Sim 的源码时，才需要采用此方法。

安装 Isaac Sim
--------------------

从源码构建
~~~~~~~~~~~~~~~~~~~~

从 Isaac Sim 5.0 版本开始，可以从源码构建 Isaac Sim。
这种方式面向希望同时修改 Isaac Sim 源码的用户，
或者想用 Isaac Sim 的 nightly 版本测试 Isaac Lab 的用户。

为了方便用户，以下说明改编自
`Isaac Sim documentation <https://github.com/isaac-sim/IsaacSim?tab=readme-ov-file#quick-start>`_。

.. attention::

   从源码构建 Isaac Sim 要求 Ubuntu 22.04 LTS 或更高版本。

.. attention::

   有关驱动要求的详细信息，请参阅 `Technical Requirements <https://docs.omniverse.nvidia.com/materials-and-rendering/latest/common/technical-requirements.html>`_ 指南。

   在 Windows 上，可能需要
   `enable long path support <https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=registry#enable-long-paths-in-windows-10-version-1607-and-later>`_，
   以避免因操作系统限制导致的安装错误。


- 将 Isaac Sim 仓库克隆到你的工作区：

  .. code:: bash

     git clone https://github.com/isaac-sim/IsaacSim.git

- 从源码构建 Isaac Sim：

  .. tab-set::
     :sync-group: os

     .. tab-item:: :icon:`fa-brands fa-linux` Linux
        :sync: linux

        .. code:: bash

           cd IsaacSim
           ./build.sh

     .. tab-item:: :icon:`fa-brands fa-windows` Windows
        :sync: windows

        .. code:: bash

           cd IsaacSim
           build.bat


验证 Isaac Sim 安装
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

为避免每次都要查找和定位 Isaac Sim 安装目录的开销，我们建议在余下的安装步骤中，
将以下环境变量导出到你的终端：

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code:: bash

         # Isaac Sim root directory
         export ISAACSIM_PATH="${pwd}/_build/linux-x86_64/release"
         # Isaac Sim python executable
         export ISAACSIM_PYTHON_EXE="${ISAACSIM_PATH}/python.sh"

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code:: batch

         :: Isaac Sim root directory
         set ISAACSIM_PATH="%cd%\_build\windows-x86_64\release"
         :: Isaac Sim python executable
         set ISAACSIM_PYTHON_EXE="%ISAACSIM_PATH:"=%\python.bat"

.. include:: include/bin_verify_isaacsim.rst


安装 Isaac Lab
--------------------

.. include:: include/src_clone_isaaclab.rst

.. include:: include/src_symlink_isaacsim.rst

.. include:: include/src_python_virtual_env.rst

.. include:: include/src_build_isaaclab.rst

.. include:: include/src_verify_isaaclab.rst
