准备 Python 环境
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**强烈建议** 创建专用的 Python 环境。它有助于：

- **避免与系统 Python** 或机器上安装的其他项目发生冲突。
- **保持依赖隔离**，这样其他项目中的包升级或实验就不会破坏 Isaac Sim。
- **轻松管理多个环境**，以适应不同依赖版本的配置。
- **简化可复现性** —— 环境中只包含当前项目所需的包，
  更便于与同事共享配置或在不同的机器上运行。

你可以选择不同的包管理器来创建虚拟环境。

- **UV**：一个现代、快速、安全的 Python 包管理器。
- **Conda**：一个跨平台、语言无关的 Python 包管理器。
- **venv**：Python 中用于创建虚拟环境的标准库。

.. caution::

   虚拟环境的 Python 版本必须与 Isaac Sim 的 Python 版本一致。

   - 对于 Isaac Sim 5.X，所需的 Python 版本为 3.11。
   - 对于 Isaac Sim 4.X，所需的 Python 版本为 3.10。

   使用不同的 Python 版本会在运行 Isaac Lab 时导致错误。

以下说明针对需要 Python 3.11 的 Isaac Sim 5.X。
如果你想安装 Isaac Sim 4.5，请相应地修改说明，改用 Python 3.10。

-  使用以下任意一种包管理器创建虚拟环境：

   .. tab-set::

      .. tab-item::  Conda Environment

         要安装 conda，请按照 `这里 <https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html>`__ 的说明操作。
         你可以使用以下命令创建 Isaac Lab 环境。

         我们推荐使用 `Miniconda <https://www.anaconda.com/docs/getting-started/miniconda/main/>`_，
         因为它是轻量且高效的资源占用型环境管理系统。

         .. code-block:: bash

            conda create -n env_isaaclab python=3.11
            conda activate env_isaaclab

      .. tab-item::  venv Environment

         要使用标准库创建虚拟环境，可以使用
         以下命令：

         .. tab-set::
            :sync-group: os

            .. tab-item:: :icon:`fa-brands fa-linux` Linux
               :sync: linux

               .. code-block:: bash

                  # create a virtual environment named env_isaaclab with python3.11
                  python3.11 -m venv env_isaaclab
                  # activate the virtual environment
                  source env_isaaclab/bin/activate

            .. tab-item:: :icon:`fa-brands fa-windows` Windows
               :sync: windows

               .. code-block:: batch

                  :: create a virtual environment named env_isaaclab with python3.11
                  python3.11 -m venv env_isaaclab
                  :: activate the virtual environment
                  env_isaaclab\Scripts\activate

      .. tab-item::  UV Environment (experimental)

         要安装 ``uv``，请按照 `这里 <https://docs.astral.sh/uv/getting-started/installation/>`__ 的说明操作。

         .. note::

            由 ``uv venv`` 创建的虚拟环境 **不** 包含 ``pip``。
            由于安装 Isaac Lab 需要 ``pip``，请在激活环境后手动安装它。

         你可以使用以下命令创建 Isaac Lab 环境：

         .. tab-set::
            :sync-group: os

            .. tab-item:: :icon:`fa-brands fa-linux` Linux
               :sync: linux

               .. code-block:: bash

                  # create a virtual environment named env_isaaclab with python3.11 and pip
                  uv venv --python 3.11 --seed env_isaaclab
                  # activate the virtual environment
                  source env_isaaclab/bin/activate

            .. tab-item:: :icon:`fa-brands fa-windows` Windows
               :sync: windows

               .. code-block:: batch

                  :: create a virtual environment named env_isaaclab with python3.11 and pip
                  uv venv --python 3.11 --seed env_isaaclab
                  :: activate the virtual environment
                  env_isaaclab\Scripts\activate



-  确保安装了最新版本的 pip。要更新 pip，请在虚拟环境内运行以下命令：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code-block:: bash

            pip install --upgrade pip

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code-block:: batch

            python -m pip install --upgrade pip
