简单智能体
=============

工作流
---------

借助 Isaac Lab，我们还在 ``isaaclab_tasks`` 扩展中提供了一整套基准测试环境。我们使用 OpenAI Gym
注册机制来注册这些环境。对于每个环境，我们都提供了一个默认配置文件，用于定义场景、观测、奖励和动作空间。

通过运行以下命令，可以查看已注册到 OpenAI Gym 的所有环境列表：

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code:: bash

         ./isaaclab.sh -p scripts/environments/list_envs.py

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code:: batch

         isaaclab.bat -p scripts\environments\list_envs.py

虚拟智能体（Dummy agents）
~~~~~~~~~~~~~~~~~~~~~~~~~~

这里包含输出全零动作或随机动作的虚拟智能体。它们可用于确保环境的配置正确无误。

-  Cart-pole 示例上的零动作智能体：

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code:: bash

         ./isaaclab.sh -p scripts/environments/zero_agent.py --task Isaac-Cartpole-v0 --num_envs 32

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code:: batch

         isaaclab.bat -p scripts\environments\zero_agent.py --task Isaac-Cartpole-v0 --num_envs 32

-  Cart-pole 示例上的随机动作智能体：

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code:: bash

         ./isaaclab.sh -p scripts/environments/random_agent.py --task Isaac-Cartpole-v0 --num_envs 32

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code:: batch

         isaaclab.bat -p scripts\environments\random_agent.py --task Isaac-Cartpole-v0 --num_envs 32


状态机
~~~~~~~~~~~~~

我们提供了针对这些环境手工编写状态机的示例。它们有助于理解环境以及如何使用所提供的接口。
这些状态机使用 `warp <https://github.com/NVIDIA/warp>`__ 编写，可以借助 CUDA 内核
在大量环境中高效执行。

-  使用机械臂抓起一个立方体并将其放置到目标位姿：

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code:: bash

         ./isaaclab.sh -p scripts/environments/state_machine/lift_cube_sm.py --num_envs 32

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code:: batch

         isaaclab.bat -p scripts\environments\state_machine\lift_cube_sm.py --num_envs 32

-  使用机械臂抓起一只可变形的泰迪熊并将其放置到目标位姿：

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code:: bash

         ./isaaclab.sh -p scripts/environments/state_machine/lift_teddy_bear.py

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code:: batch

         isaaclab.bat -p scripts\environments\state_machine\lift_teddy_bear.py
