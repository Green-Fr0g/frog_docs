验证 Isaac Lab 安装
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

要验证安装是否成功，请在仓库顶层运行以下命令：

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code:: bash

         # Option 1: Using the isaaclab.sh executable
         # note: this works for both the bundled python and the virtual environment
         ./isaaclab.sh -p scripts/tutorials/00_sim/create_empty.py

         # Option 2: Using python in your virtual environment
         python scripts/tutorials/00_sim/create_empty.py

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code:: batch

         :: Option 1: Using the isaaclab.bat executable
         :: note: this works for both the bundled python and the virtual environment
         isaaclab.bat -p scripts\tutorials\00_sim\create_empty.py

         :: Option 2: Using python in your virtual environment
         python scripts\tutorials\00_sim\create_empty.py


上述命令应会启动仿真器，并显示一个带有黑色视口（viewport）的窗口。
你可以通过在终端中按 ``Ctrl+C`` 退出脚本。
在 Windows 机器上，请从命令提示符中使用 ``Ctrl+Break`` 或 ``Ctrl+fn+B`` 终止进程。

.. figure:: /source/_static/setup/verify_install.jpg
    :align: center
    :figwidth: 100%
    :alt: Simulator with a black window.


如果看到了这个画面，说明安装成功了！ |:tada:|

.. note::

   如果你看到 ``ModuleNotFoundError: No module named 'isaacsim'`` 错误，请确保虚拟环境已激活，
   并且已经执行过 ``source _isaac_sim/setup_conda_env.sh`` （使用 uv 时也是如此）。


训练一个机器人！
~~~~~~~~~~~~~~~~

现在你可以使用 Isaac Lab 通过强化学习来训练机器人了！使用 Isaac Lab 最快捷的方式，
是通过我们 **开箱即用** 的机器人任务之一提供的预定义工作流。执行以下命令即可快速训练一只蚂蚁（ant）走路！
我们建议添加 ``--headless`` 参数以加快训练速度。

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code:: bash

         ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task=Isaac-Ant-v0 --headless

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code:: batch

         isaaclab.bat -p scripts/reinforcement_learning/rsl_rl/train.py --task=Isaac-Ant-v0 --headless

……或者训练一只机器狗！

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code:: bash

         ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task=Isaac-Velocity-Rough-Anymal-C-v0 --headless

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code:: batch

         isaaclab.bat -p scripts/reinforcement_learning/rsl_rl/train.py --task=Isaac-Velocity-Rough-Anymal-C-v0 --headless

Isaac Lab 提供了你创建自己的 **任务** 和 **工作流** 所需的工具，以满足项目的任何需求。
详情请参阅我们的 :ref:`how-to` 指南，例如 :ref:`Adding your own learning Library <how-to-add-library>`
和 :ref:`Wrapping Environments <how-to-env-wrappers>`。

.. figure:: /source/_static/setup/isaac_ants_example.jpg
    :align: center
    :figwidth: 100%
    :alt: Idle hands...
