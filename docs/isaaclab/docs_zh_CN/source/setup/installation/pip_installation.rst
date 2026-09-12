.. _isaaclab-pip-installation:

使用 Isaac Sim Pip 包安装
========================================

以下步骤首先通过 pip 安装 Isaac Sim，然后从源码安装 Isaac Lab。

.. attention::

   通过 pip 安装 Isaac Sim 要求 GLIBC 版本为 2.35 及以上。
   要查看你系统上的 GLIBC 版本，请使用命令 ``ldd --version``。

   这可能会与某些 Linux 发行版产生兼容性问题。例如，Ubuntu 20.04 LTS
   默认的 GLIBC 版本为 2.31。如果你遇到兼容性问题，我们建议采用
   :ref:`Isaac Sim Binaries Installation <isaaclab-binaries-installation>` 的方法。

.. note::

   如果你稍后计划 :ref:`Set up Visual Studio Code <setup-vs-code>`，我们建议采用
   :ref:`Isaac Sim Binaries Installation <isaaclab-binaries-installation>` 的方法。

安装 Isaac Sim
--------------------

从 Isaac Sim 4.0 开始，可以使用 pip 安装 Isaac Sim。
这种方式无需下载 Isaac Sim 二进制包，使安装更加简便。
如果遇到任何问题，请到
`Isaac Sim Forums <https://docs.isaacsim.omniverse.nvidia.com/latest/common/feedback.html>`_ 报告。

.. attention::

   在 Windows 上，可能需要
   `enable long path support <https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=registry#enable-long-paths-in-windows-10-version-1607-and-later>`_，
   以避免因操作系统限制导致的安装错误。

.. include:: include/pip_python_virtual_env.rst

安装依赖
~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   如果你使用 UV 创建了虚拟环境，请在下列命令中将 ``pip`` 替换为 ``uv pip``。

-  安装 Isaac Sim pip 包：

   .. code-block:: none

      pip install "isaacsim[all,extscache]==5.1.0" --extra-index-url https://pypi.nvidia.com

-  安装与你的系统架构匹配、且支持 CUDA 的 PyTorch 构建：

   .. tab-set::
      :sync-group: pip-platform

      .. tab-item:: :icon:`fa-brands fa-linux` Linux (x86_64)
         :sync: linux-x86_64

         .. code-block:: bash

            pip install -U torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128

      .. tab-item:: :icon:`fa-brands fa-windows` Windows (x86_64)
         :sync: windows-x86_64

         .. code-block:: bash

            pip install -U torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128

      .. tab-item:: :icon:`fa-brands fa-linux` Linux (aarch64)
         :sync: linux-aarch64

         .. code-block:: bash

            pip install -U torch==2.9.0 torchvision==0.24.0 --index-url https://download.pytorch.org/whl/cu130

         .. note::

            在 aarch64 上安装 Isaac Lab 后，你可能会遇到如下警告：

            .. code-block:: none

               ERROR: ld.so: object '...torch.libs/libgomp-XXXX.so.1.0.0' cannot be preloaded: ignored.

            当系统和 PyTorch 的 ``libgomp`` （GNU OpenMP）库同时被预加载时，就会出现此警告。
            Isaac Sim 期望使用 **系统** 的 OpenMP 运行时，而 PyTorch 有时会捆绑自己的版本。

            要解决此问题，请先取消已有的 ``LD_PRELOAD``，然后将其设置为仅使用系统库：

            .. code-block:: bash

               unset LD_PRELOAD
               export LD_PRELOAD="$LD_PRELOAD:/lib/aarch64-linux-gnu/libgomp.so.1"

            这样可以确保为 Isaac Sim 和 Isaac Lab 预加载正确的 ``libgomp`` 库，
            从而消除运行时的预加载警告。

.. include:: include/pip_verify_isaacsim.rst

安装 Isaac Lab
--------------------

.. include:: include/src_clone_isaaclab.rst

.. include:: include/src_build_isaaclab.rst

.. include:: include/src_verify_isaaclab.rst
