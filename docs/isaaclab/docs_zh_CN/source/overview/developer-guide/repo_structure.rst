仓库组织结构
-----------------------

.. code-block:: bash

   IsaacLab
   ├── .vscode
   ├── CONTRIBUTING.md
   ├── CONTRIBUTORS.md
   ├── LICENSE
   ├── isaaclab.bat
   ├── isaaclab.sh
   ├── pyproject.toml
   ├── README.md
   ├── docs
   ├── docker
   ├── source
   │   ├── isaaclab
   │   ├── isaaclab_assets
   │   ├── isaaclab_mimic
   │   ├── isaaclab_rl
   │   └── isaaclab_tasks
   ├── scripts
   │   ├── benchmarks
   │   ├── demos
   │   ├── environments
   │   ├── imitation_learning
   │   ├── reinforcement_learning
   │   ├── tools
   │   ├── tutorials
   ├── tools
   └── VERSION

Isaac Lab 构建在与 Isaac Sim 相同的后端之上。因此，它以一系列**扩展（extension）**的形式存在，这些扩展可以组装成**应用程序（application）**。``source`` 目录包含仓库中的大部分代码以及组成 Isaac Lab 的各个扩展，而 ``scripts`` 目录包含用于启动自定义独立应用程序的 Python 脚本（例如我们的各种工作流）。这是与仿真交互的两种主要方式，Isaac Lab 对两者都提供了支持！如需了解更多细节，请查阅这份 `Isaac Sim 工作流简介 <https://docs.isaacsim.omniverse.nvidia.com/latest/introduction/workflows.html>`__。

扩展
~~~~~~~~~~

组成 Isaac Lab 的各个扩展保存在 ``source`` 目录中。为了简化构建过程，Isaac Lab 直接使用 `setuptools <https://setuptools.readthedocs.io/en/latest/>`__。如果你使用 Isaac Lab 创建自己的扩展，我们强烈建议遵循这一流程。

这些扩展的组织方式如下：

* **isaaclab**: 包含 Isaac Lab 的核心接口扩展。它提供了执行器（actuator）、物体、机器人和传感器（sensor）的主要模块。
* **isaaclab_assets**: 包含为 Isaac Lab 预配置资产的扩展。
* **isaaclab_tasks**: 包含为 Isaac Lab 预配置环境的扩展。
* **isaaclab_mimic**: 包含用于模仿学习数据生成的 API 和预配置环境。
* **isaaclab_rl**: 包含将上述环境与不同强化学习智能体配合使用的封装器。


独立应用程序
~~~~~~~~~~~~

``scripts`` 目录包含各种用 Python 编写的独立应用程序。
它们的结构如下：

* **benchmarks**: 包含用于对框架不同组件进行基准测试的脚本。
* **demos**: 包含展示核心框架 :mod:`isaaclab` 的各种演示应用程序。
* **environments**: 包含使用不同智能体运行 :mod:`isaaclab_tasks` 中所定义环境的应用程序。这些智能体包括随机策略、零动作策略、遥操作或脚本化状态机。
* **tools**: 包含使用框架所提供工具的应用程序。这些工具包括资产转换、数据集生成等。
* **tutorials**: 包含使用框架所提供 API 的分步教程。
* **workflows**: 包含将环境与各种基于学习的框架配合使用的应用程序。这些框架包括不同的强化学习或模仿学习库。
