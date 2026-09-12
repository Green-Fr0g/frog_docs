设置 Python 环境（可选）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. attention::
   此步骤是可选的。如果你使用的是 Isaac Sim 自带的 Python，可以跳过此步骤。

**强烈建议** 为 Isaac Lab 创建专用的 Python 环境，尽管这一步是可选的。
使用虚拟环境有助于：

- **避免与系统 Python** 或机器上安装的其他项目发生冲突。
- **保持依赖隔离**，这样其他项目中的包升级或实验就不会破坏 Isaac Sim。
- **轻松管理多个环境**，以适应不同依赖版本的配置。
- **简化可复现性** —— 环境中只包含当前项目所需的包，
  更便于与同事共享配置或在不同的机器上运行。


你可以选择不同的包管理器来创建虚拟环境。

- **UV**：一个现代、快速、安全的 Python 包管理器。
- **Conda**：一个跨平台、语言无关的 Python 包管理器。

创建完成后，你可以使用虚拟环境中的默认 Python（*python* 或 *python3*）
来代替 *./isaaclab.sh -p* 或 *isaaclab.bat -p*。

.. caution::

   虚拟环境的 Python 版本必须与 Isaac Sim 的 Python 版本一致。

   - 对于 Isaac Sim 5.X，所需的 Python 版本为 3.11。
   - 对于 Isaac Sim 4.X，所需的 Python 版本为 3.10。

   使用不同的 Python 版本会在运行 Isaac Lab 时导致错误。


.. tab-set::

   .. tab-item::  Conda Environment

      要安装 conda，请按照 `这里 <https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html>`__ 的说明操作。
      你可以使用以下命令创建 Isaac Lab 环境。

      我们推荐使用 `Miniconda <https://www.anaconda.com/docs/getting-started/miniconda/main/>`_，
      因为它是轻量且高效的资源占用型环境管理系统。

      .. tab-set::
         :sync-group: os

         .. tab-item:: :icon:`fa-brands fa-linux` Linux
            :sync: linux

            .. code:: bash

               # Option 1: Default environment name 'env_isaaclab'
               ./isaaclab.sh --conda  # or "./isaaclab.sh -c"
               # Option 2: Custom name
               ./isaaclab.sh --conda my_env  # or "./isaaclab.sh -c my_env"

            .. code:: bash

               # Activate environment
               conda activate env_isaaclab  # or "conda activate my_env"

         .. tab-item:: :icon:`fa-brands fa-windows` Windows
            :sync: windows

            .. code:: batch

               :: Option 1: Default environment name 'env_isaaclab'
               isaaclab.bat --conda  :: or "isaaclab.bat -c"
               :: Option 2: Custom name
               isaaclab.bat --conda my_env  :: or "isaaclab.bat -c my_env"

            .. code:: batch

               :: Activate environment
               conda activate env_isaaclab  # or "conda activate my_env"

   .. tab-item::  UV Environment (experimental)

      要安装 ``uv``，请按照 `这里 <https://docs.astral.sh/uv/getting-started/installation/>`__ 的说明操作。
      你可以使用以下命令创建 Isaac Lab 环境：

      .. tab-set::
         :sync-group: os

         .. tab-item:: :icon:`fa-brands fa-linux` Linux
            :sync: linux

            .. code:: bash

               # Option 1: Default environment name 'env_isaaclab'
               ./isaaclab.sh --uv  # or "./isaaclab.sh -u"
               # Option 2: Custom name
               ./isaaclab.sh --uv my_env  # or "./isaaclab.sh -u my_env"

            .. code:: bash

               # Activate environment
               source ./env_isaaclab/bin/activate  # or "source ./my_env/bin/activate"

         .. tab-item:: :icon:`fa-brands fa-windows` Windows
            :sync: windows

            .. warning::
               目前尚不支持在 Windows 上使用 UV。请关注
               `issue #3483 <https://github.com/isaac-sim/IsaacLab/issues/3438>`_ 以了解进展。

一旦进入虚拟环境，你就无需使用 ``./isaaclab.sh -p`` 或
``isaaclab.bat -p`` 来运行 Python 脚本。运行 ``python`` 或 ``python3``
即可使用你环境中的默认 Python 可执行文件。不过，在本文档的其余部分，
我们将假定你使用 ``./isaaclab.sh -p`` 或 ``isaaclab.bat -p`` 来运行 Python 脚本。
