克隆 Isaac Lab
~~~~~~~~~~~~~~~~~

.. note::

   我们建议先创建 Isaac Lab 仓库的 `fork <https://github.com/isaac-sim/IsaacLab/fork>`_ 来为项目做贡献，
   但这对使用该框架来说不是必需的。如果你创建了 fork，
   请在后续说明中将 ``isaac-sim`` 替换为你的用户名。

将 Isaac Lab 仓库克隆到你项目的工作区中：

.. tab-set::

   .. tab-item:: SSH

      .. code:: bash

         git clone git@github.com:isaac-sim/IsaacLab.git

   .. tab-item:: HTTPS

      .. code:: bash

         git clone https://github.com/isaac-sim/IsaacLab.git


我们分别为 Linux 和 Windows 提供了辅助可执行文件 `isaaclab.sh <https://github.com/isaac-sim/IsaacLab/blob/main/isaaclab.sh>`_
和 `isaaclab.bat <https://github.com/isaac-sim/IsaacLab/blob/main/isaaclab.bat>`_，
它们提供了管理扩展的实用功能。

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code:: text

         ./isaaclab.sh --help

         usage: isaaclab.sh [-h] [-i] [-f] [-p] [-s] [-t] [-o] [-v] [-d] [-n] [-c] -- Utility to manage Isaac Lab.

         optional arguments:
            -h, --help           Display the help content.
            -i, --install [LIB]  Install the extensions inside Isaac Lab and learning frameworks (rl_games, rsl_rl, sb3, skrl) as extra dependencies. Default is 'all'.
            -f, --format         Run pre-commit to format the code and check lints.
            -p, --python         Run the python executable provided by Isaac Sim or virtual environment (if active).
            -s, --sim            Run the simulator executable (isaac-sim.sh) provided by Isaac Sim.
            -t, --test           Run all python pytest tests.
            -o, --docker         Run the docker container helper script (docker/container.sh).
            -v, --vscode         Generate the VSCode settings file from template.
            -d, --docs           Build the documentation from source using sphinx.
            -n, --new            Create a new external project or internal task from template.
            -c, --conda [NAME]   Create the conda environment for Isaac Lab. Default name is 'env_isaaclab'.
            -u, --uv [NAME]      Create the uv environment for Isaac Lab. Default name is 'env_isaaclab'.

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code:: text

         isaaclab.bat --help

         usage: isaaclab.bat [-h] [-i] [-f] [-p] [-s] [-v] [-d] [-n] [-c] -- Utility to manage Isaac Lab.

         optional arguments:
            -h, --help           Display the help content.
            -i, --install [LIB]  Install the extensions inside Isaac Lab and learning frameworks (rl_games, rsl_rl, sb3, skrl) as extra dependencies. Default is 'all'.
            -f, --format         Run pre-commit to format the code and check lints.
            -p, --python         Run the python executable provided by Isaac Sim or virtual environment (if active).
            -s, --sim            Run the simulator executable (isaac-sim.bat) provided by Isaac Sim.
            -t, --test           Run all python pytest tests.
            -v, --vscode         Generate the VSCode settings file from template.
            -d, --docs           Build the documentation from source using sphinx.
            -n, --new            Create a new external project or internal task from template.
            -c, --conda [NAME]   Create the conda environment for Isaac Lab. Default name is 'env_isaaclab'.
            -u, --uv [NAME]      Create the uv environment for Isaac Lab. Default name is 'env_isaaclab'.
