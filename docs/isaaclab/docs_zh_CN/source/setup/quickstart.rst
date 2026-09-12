.. _isaac-lab-quickstart:

快速上手指南
=======================


本指南专为那些迫不及待想要动手实践的人编写，将介绍你在使用 Isaac Lab 构建自己的项目时会遇到的最常见概念！
内容包括安装、运行强化学习、查找环境、创建新项目等等！

Isaac Lab 的强大之处源于几个关键特性，我们将在本指南中非常简要地介绍它们。

1) **向量化**：强化学习需要反复尝试同一个任务。Isaac Lab 通过对环境进行向量化来加速这一过程——即让训练
   在同一环境的多个副本上并行运行，从而减少模型权重更新前采集数据所花费的时间。代码库的大部分内容都用于
   定义环境中需要被这套向量化系统处理的部分。

2) **模块化设计**：Isaac Lab 的设计是模块化的，这意味着你可以将项目设计成由多个组件构成的形式，
   并根据不同的需求替换这些组件。例如，假设你想训练一个支持特定机器人子集的策略。你可以通过以某个
   Manager 类的形式编写一层控制器接口（在本例中即 ``ActionManager``），把环境和任务设计成与具体机器人无关的形式。
   代码库的其余大部分内容则用于定义项目中需要被这套管理器系统处理的部分。

开始使用时，我们首先安装 Isaac Lab 并启动一个训练脚本。

快速安装指南
-------------------------

:ref:`安装 <isaaclab-installation-root>` Isaac Lab 有很多种方式，但为了配合本快速上手指南，
我们将采用使用虚拟环境的 pip 安装路线。

首先，我们定义虚拟环境。

.. tab-set::

   .. tab-item:: conda

      .. code-block:: bash

         # create a virtual environment named env_isaaclab with python3.11 and pip
         conda create -n env_isaaclab python=3.11
         # activate the virtual environment
         conda activate env_isaaclab

   .. tab-item:: uv (experimental)

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

               # create a virtual environment named env_isaaclab with python3.11
               uv venv --python 3.11 env_isaaclab
               # activate the virtual environment
               env_isaaclab\Scripts\activate


接下来，安装支持 CUDA 的 PyTorch 2.7.0 构建。

   .. code-block:: bash

      pip install -U torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128


在安装 Isaac Sim 之前，我们需要确保 pip 已更新。要更新 pip，请运行

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

现在我们就可以安装 Isaac Sim 包了。

.. code-block:: none

    pip install "isaacsim[all,extscache]==5.1.0" --extra-index-url https://pypi.nvidia.com

最后，我们可以安装 Isaac Lab。首先，使用以下命令克隆仓库

.. tab-set::

   .. tab-item:: SSH

      .. code:: bash

         git clone git@github.com:isaac-sim/IsaacLab.git

   .. tab-item:: HTTPS

      .. code:: bash

         git clone https://github.com/isaac-sim/IsaacLab.git

安装现在变得非常简单：进入仓库目录，然后用 ``--install`` 标志调用根目录脚本即可！

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code:: bash

         ./isaaclab.sh --install # or "./isaaclab.sh -i"

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code:: bash

         isaaclab.bat --install :: or "isaaclab.bat -i"


使用 Isaac Launchable 快速上手
----------------------------------

对于刚开始学习 Isaac Lab、且本地计算资源不足的用户，`Isaac Launchable <https://github.com/isaac-sim/isaac-launchable>`_ 项目
提供了一种无需手动安装即可快速上手的方式。

通过该项目，用户可以完全通过网页浏览器与 Isaac Sim 和 Isaac Lab 交互：一个标签页运行 Visual Studio Code 用于开发和执行命令，
另一个标签页提供 Isaac Sim 的串流用户界面。

该方法使用 `NVIDIA Brev <https://brev.nvidia.com/>`_，这是一个提供易于配置、按小时计费云端算力的平台。
Brev Launchables 是预先配置好、经过优化的计算与软件环境。

想立即尝试的话，请点击下方的按钮。要了解如何使用该项目，或如何创建你自己的 Launchable，
请参阅项目仓库 `这里 <https://github.com/isaac-sim/isaac-launchable>`_。

.. image:: https://brev-assets.s3.us-west-1.amazonaws.com/nv-lb-dark.svg
   :target: https://brev.nvidia.com/launchable/deploy/now?launchableID=env-35JP2ywERLgqtD0b0MIeK1HnF46
   :alt: Click here to deploy


启动训练
-------------------

Isaac Lab 的各个后端通过位于 ``isaaclab/scripts/reinforcement_learning`` 目录中对应的
``train.py`` 和 ``play.py`` 脚本来访问。
调用这些脚本时需要提供一个 **任务名称** 以及与 gymnasium API 对应的 **入口点**。例如

.. code-block:: bash

    python scripts/reinforcement_learning/skrl/train.py --task=Isaac-Ant-v0

这会训练 MuJoCo 蚂蚁 "奔跑"。你可以使用 ``--help`` 标志查看各种可用的启动选项。
请特别留意 ``--num_envs`` 选项和 ``--headless`` 标志，
在开发和调试新环境时它们都非常有用。在这一层级指定的选项会自动覆盖代码中定义的任何等价配置
（只要那些定义属于 ``@configclass``，见下文）。

列出可用环境
-----------------------------

上文中，``Isaac-Ant-v0`` 是任务名称，``skrl`` 是所使用的 RL 框架。``Isaac-Ant-v0`` 环境
已在 `Gymnasium API <https://gymnasium.farama.org/>`_ 中注册，你可以通过调用
``list_envs.py`` 脚本查看入口点是如何定义的，该脚本位于 ``isaaclab/scripts/environments/list_envs.py``。
你应该会看到类似下面的条目

.. code-block:: bash

    $> python scripts/environments/list_envs.py

    +--------------------------------------------------------------------------------------------------------------------------------------------+
    |  Available Environments in Isaac Lab
    +--------+----------------------+--------------------------------------------+---------------------------------------------------------------+
    | S. No. | Task Name            | Entry Point                                | Config
    .
    .
    .
    +--------+----------------------+--------------------------------------------+---------------------------------------------------------------+
    |   2    | Isaac-Ant-Direct-v0  |  isaaclab_tasks.direct.ant.ant_env:AntEnv  |  isaaclab_tasks.direct.ant.ant_env:AntEnvCfg
    +--------+----------------------+--------------------------------------------+---------------------------------------------------------------+
    .
    .
    .
    +--------+----------------------+--------------------------------------------+---------------------------------------------------------------+
    |   48   | Isaac-Ant-v0         | isaaclab.envs:ManagerBasedRLEnv            |   isaaclab_tasks.manager_based.classic.ant.ant_env_cfg:AntEnvCfg
    +--------+----------------------+--------------------------------------------+---------------------------------------------------------------+

注意这里有两个不同的 ``Ant`` 任务，一个用于 ``Direct`` 环境，另一个用于 ``ManagerBased`` 环境。
它们是你可以开箱即用地配合 Isaac Lab 使用的 :ref:`两种主要工作流<feature-workflows>`。
直接式工作流能让你以最短路径得到一个可用于强化学习的自定义环境，而管理器式工作流则为你的项目提供更通用开发
所需的模块化结构。在本快速上手指南中，我们只关注直接式工作流。


生成你自己的项目
--------------------------

用 Isaac Lab 启动一个新项目起初可能看起来令人生畏，但正因如此我们提供了 :ref:`模板生成器
<template-generator>`，可以通过命令行快速搭建新项目的样板代码。

.. code-block:: bash

    ./isaaclab.sh --new

这会根据你选择的设置为创建一个新项目

* **External vs Internal（外部 vs 内部）**：决定该项目是作为 Isaac Lab 仓库的一部分构建，还是
  作为外部扩展加载。
* **Direct vs Manager（直接式 vs 管理器式）**：直接式任务将全部实现细节都包含在环境定义中，
  而管理器式项目则使用我们为环境各个 "部分" 提供的模块化定义。
* **Framework（框架）**：此处可以选择多个选项。这决定了你打算在项目中原生使用哪些 RL 框架
  （即你想用哪些具体的算法实现来进行训练）。

项目创建完成后，进入已安装的项目并运行

.. code-block:: bash

    python -m pip install -e source/<given-project-name>

以完成安装流程并注册环境。在模板生成器创建的目录中，你会找到至少一个 ``__init__.py`` 文件，
其中包含类似下面的内容

.. code-block:: python

    import gymnasium as gym

    gym.register(
        id="Template-isaaclabtutorial_env-v0",
        entry_point=f"{__name__}.isaaclabtutorial_env:IsaaclabtutorialEnv",
        disable_env_checker=True,
        kwargs={
            "env_cfg_entry_point": f"{__name__}.isaaclabtutorial_env_cfg:IsaaclabtutorialEnvCfg",
            "skrl_cfg_entry_point": f"{agents.__name__}.skrl_ppo_cfg:PPORunnerCfg",
        },
    )

这才是真正为环境注册以供日后使用的函数。注意 ``entry_point`` 实际上就是指向环境定义的
Python 模块路径。这就是我们需要把项目作为包安装的原因：模块路径 **就是** gymnasium API 的入口点。

配置
---------------

无论你要用 Isaac Lab 做什么，都需要与 **配置（Configuration）** 打交道。所有配置都可以通过
类定义上方的 ``@configclass`` 装饰器以及缺少 ``__init__`` 函数来识别。例如，考虑
:ref:`cartpole 环境 <tutorial-create-direct-rl-env>` 的下面这个配置类。

.. code-block:: python

    @configclass
    class CartpoleEnvCfg(DirectRLEnvCfg):
        # env
        decimation = 2
        episode_length_s = 5.0
        action_scale = 100.0  # [N]
        action_space = 1
        observation_space = 4
        state_space = 0

        # simulation
        sim: SimulationCfg = SimulationCfg(dt=1 / 120, render_interval=decimation)

        # robot
        robot_cfg: ArticulationCfg = CARTPOLE_CFG.replace(prim_path="/World/envs/env_.*/Robot")
        cart_dof_name = "slider_to_cart"
        pole_dof_name = "cart_to_pole"

        # scene
        scene: InteractiveSceneCfg = InteractiveSceneCfg(num_envs=4096, env_spacing=4.0, replicate_physics=True)

        # reset
        max_cart_pos = 3.0  # the cart is reset if it exceeds that position [m]
        initial_pole_angle_range = [-0.25, 0.25]  # the range in which the pole angle is sampled from on reset [rad]

        # reward scales
        rew_scale_alive = 1.0
        rew_scale_terminated = -2.0
        rew_scale_pole_pos = -1.0
        rew_scale_cart_vel = -0.01
        rew_scale_pole_vel = -0.005

注意，整个类定义只是一系列值字段和其他配置的列表。任何需要在训练过程中被 Lab 向量化处理的东西，
都需要配置类。如果你想把一个环境复制数千份，并异步管理来自每个副本的数据，就需要以某种方式 "标注"
场景中哪些部分与这个复制过程（向量化）相关。这正是配置类所完成的工作！

在这个例子中，该类定义了整个训练环境的配置！还要注意 ``InteractiveSceneCfg`` 中的 ``num_envs`` 变量。它实际上会在
``train.py`` 脚本内部被命令行参数覆盖。配置提供了直达配置层级中任何变量的路径，使得在启动时修改
环境所 "配置" 的任何内容都变得容易。

机器人
-------

在 Isaac Lab 中，机器人完全以配置实例的形式定义。如果你查看 ``source/isaaclab_assets/isaaclab_assets/robots``，
会看到许多文件，每个文件都包含相应机器人的配置。这些单独文件的目的在于更好地界定所有不同机器人的作用范围，
但没有任何东西阻止你 :ref:`添加自己的机器人 <tutorial-add-new-robot>` 到你的项目中，甚至添加到 ``isaaclab``
仓库中！例如，考虑下面 Dofbot 的配置

.. code-block:: python

    import isaaclab.sim as sim_utils
    from isaaclab.actuators import ImplicitActuatorCfg
    from isaaclab.assets.articulation import ArticulationCfg
    from isaaclab.utils.assets import ISAAC_NUCLEUS_DIR

    DOFBOT_CONFIG = ArticulationCfg(
        spawn=sim_utils.UsdFileCfg(
            usd_path=f"{ISAAC_NUCLEUS_DIR}/Robots/Dofbot/dofbot.usd",
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                disable_gravity=False,
                max_depenetration_velocity=5.0,
            ),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=True, solver_position_iteration_count=8, solver_velocity_iteration_count=0
            ),
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            joint_pos={
                "joint1": 0.0,
                "joint2": 0.0,
                "joint3": 0.0,
                "joint4": 0.0,
            },
            pos=(0.25, -0.25, 0.0),
        ),
        actuators={
            "front_joints": ImplicitActuatorCfg(
                joint_names_expr=["joint[1-2]"],
                effort_limit_sim=100.0,
                velocity_limit_sim=100.0,
                stiffness=10000.0,
                damping=100.0,
            ),
            "joint3_act": ImplicitActuatorCfg(
                joint_names_expr=["joint3"],
                effort_limit_sim=100.0,
                velocity_limit_sim=100.0,
                stiffness=10000.0,
                damping=100.0,
            ),
            "joint4_act": ImplicitActuatorCfg(
                joint_names_expr=["joint4"],
                effort_limit_sim=100.0,
                velocity_limit_sim=100.0,
                stiffness=10000.0,
                damping=100.0,
            ),
        },
    )

这就完整地定义了 dofbot！你可以把这段代码复制到一个 ``.py`` 文件中并作为模块导入，然后就可以在你自己的
Lab 仿真中使用 dofbot 了。在任何定义了带状态对象的配置中，你都会看到一个常见特征：存在一个
``InitialStateCfg``。请记住，配置是向量化过程的依据，而 ``InitialStateCfg`` 描述的是机器人在每个环境中被创建时
其关节的状态。``ImplicitActuatorCfg`` 使用由关节类型决定的默认驱动模型来定义机器人的关节。
并非所有关节都需要被驱动，但如果不驱动你会收到警告。如果你不打算使用那些未定义的关节，通常可以忽略这些警告。

应用与仿真
--------------

使用仿真意味着要启动 Isaac Sim 应用来提供仿真上下文（simulation context）。如果你运行的不是由标准工作流定义的任务，
那么你需要自行负责创建应用、管理上下文，并随时间推进仿真。这就是 "第三种工作流"：一个 **独立（Standalone）** 应用，
我们把框架、演示、基准测试等脚本都称为这类应用。

独立式工作流让你对应用和仿真上下文中的 *一切* 拥有完全控制权。开发独立应用在
`Isaac Sim documentation <https://docs.isaacsim.omniverse.nvidia.com/latest/index.html>`_ 中有详细讨论，
但有几点非常实用，值得在此提及。

.. code-block:: python

    import argparse

    from isaaclab.app import AppLauncher
    # add argparse arguments
    parser = argparse.ArgumentParser(
        description="This script demonstrates adding a custom robot to an Isaac Lab environment."
    )
    parser.add_argument("--num_envs", type=int, default=1, help="Number of environments to spawn.")
    # append AppLauncher cli args
    AppLauncher.add_app_launcher_args(parser)
    # parse the arguments
    args_cli = parser.parse_args()

    # launch omniverse app
    app_launcher = AppLauncher(args_cli)
    simulation_app = app_launcher.app

``AppLauncher`` 是所有 Isaac Sim 应用（包括 Isaac Lab）的入口点。*在应用启动之前，许多 Isaac Lab 和
Isaac Sim 模块都无法导入！*。这通过上面代码的倒数第二行完成，即 ``AppLauncher`` 被构造的时候。
``app_launcher.app`` 是我们与 Kit App 框架交互的接口；它是更底层的中间代码，将仿真与扩展管理系统、
GUI 等绑定在一起。在独立式工作流中，这个通常被称为 ``simulation_app`` 的接口主要用于检查仿真是否
正在运行，以及仿真结束后进行清理。
