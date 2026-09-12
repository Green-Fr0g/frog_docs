安装
~~~~~~~~~~~~

-  使用 ``apt`` 安装依赖（仅限 Linux）：

   .. code:: bash

      # these dependency are needed by robomimic which is not available on Windows
      sudo apt install cmake build-essential

-  运行安装命令，该命令会遍历 ``source`` 目录中的所有扩展，并使用 pip（带 ``--editable``
   标志）安装它们：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            ./isaaclab.sh --install # or "./isaaclab.sh -i"

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            isaaclab.bat --install :: or "isaaclab.bat -i"


   默认情况下，上述命令会安装 **所有** 学习框架。这些框架包括
   ``rl_games``、``rsl_rl``、``sb3``、``skrl``、``robomimic``。

   如果只想安装某个特定的框架，可以将框架名称作为参数传入。
   例如，只安装 ``rl_games`` 框架，可以运行：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            ./isaaclab.sh --install rl_games  # or "./isaaclab.sh -i rl_games"

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            isaaclab.bat --install rl_games :: or "isaaclab.bat -i rl_games"

   有效选项包括 ``all``、``rl_games``、``rsl_rl``、``sb3``、``skrl``、``robomimic``
   和 ``none``。如果传入 ``none``，则不会安装任何学习框架。
