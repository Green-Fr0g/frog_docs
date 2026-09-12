.. _isaaclab-binaries-installation:

使用 Isaac Sim 预构建二进制包安装
===============================================

以下步骤首先从预构建的二进制包安装 Isaac Sim，然后从源码安装 Isaac Lab。

安装 Isaac Sim
--------------------

下载预构建二进制包
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Isaac Sim 的二进制包可以直接以 zip 文件的形式从
`这里 <https://docs.isaacsim.omniverse.nvidia.com/latest/installation/download.html>`__ 下载。
如果你想使用较旧的 Isaac Sim 4.5 版本，请查看较早的下载页面
`这里 <https://docs.isaacsim.omniverse.nvidia.com/4.5.0/installation/download.html>`__。

下载 zip 文件后，你可以将其解压到所需的目录。
有关解压 Isaac Sim 二进制包的示例操作说明，
请参阅 `Isaac Sim documentation <https://docs.isaacsim.omniverse.nvidia.com/latest/installation/install_workstation.html#example-installation>`__。

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      在 Linux 系统上，我们假设 Isaac Sim 目录名为 ``${HOME}/isaacsim``。

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      在 Windows 系统上，我们假设 Isaac Sim 目录名为 ``C:\isaacsim``。

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
         export ISAACSIM_PATH="${HOME}/isaacsim"
         # Isaac Sim python executable
         export ISAACSIM_PYTHON_EXE="${ISAACSIM_PATH}/python.sh"

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code:: batch

         :: Isaac Sim root directory
         set ISAACSIM_PATH="C:\isaacsim"
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
