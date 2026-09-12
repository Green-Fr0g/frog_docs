创建 Isaac Sim 符号链接
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在已安装的 Isaac Sim 根目录与 Isaac Lab 目录下的 ``_isaac_sim`` 之间建立符号链接。
这样可以方便地索引 Python 模块，并查找随 Isaac Sim 附带的扩展。

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code:: bash

         # enter the cloned repository
         cd IsaacLab
         # create a symbolic link
         ln -s ${ISAACSIM_PATH} _isaac_sim

         # For example:
         # Option 1: If pre-built binaries were installed:
         # ln -s ${HOME}/isaacsim _isaac_sim
         #
         # Option 2: If Isaac Sim was built from source:
         # ln -s ${HOME}/IsaacSim/_build/linux-x86_64/release _isaac_sim

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code:: batch

         :: enter the cloned repository
         cd IsaacLab
         :: create a symbolic link - requires launching Command Prompt with Administrator access
         mklink /D _isaac_sim %ISAACSIM_PATH%

         :: For example:
         :: Option 1: If pre-built binaries were installed:
         :: mklink /D _isaac_sim C:\isaacsim
         ::
         :: Option 2: If Isaac Sim was built from source:
         :: mklink /D _isaac_sim C:\IsaacSim\_build\windows-x86_64\release
