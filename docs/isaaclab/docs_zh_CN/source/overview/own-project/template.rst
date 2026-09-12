.. _template-generator:


创建新项目或任务
==========================

传统上，构建利用 Isaac Lab 功能的新项目需要在 Isaac Lab 仓库中创建自己的扩展。然而，这种方式会降低项目的可见性，并使从一个版本的 Isaac Lab 升级到另一个版本变得更加复杂。为了避免这些问题，我们现在提供一个命令行工具（**模板生成器**）用于创建基于 Isaac Lab 的项目和任务。

使用模板生成器可以创建：

* **外部项目（External project）** （推荐）：一种不属于 Isaac Lab 仓库的独立项目。这种方式在核心 Isaac Lab 仓库之外工作，确保你的开发工作保持独立。此外，它还允许你的代码作为扩展在 Omniverse 中运行。

  .. hint::

    对于外部项目，模板生成器会在指定目录中初始化一个新的 Git 仓库。你可以将生成的内容推送到自己的远程仓库（例如 GitHub）并与其他人共享。

* **内部任务（Internal task）**：属于 Isaac Lab 仓库的任务。这种方式只应用于在 Isaac Lab 仓库内创建新任务，以便为其做出贡献。

  .. warning::

    通过 pip 安装的 Isaac Lab 不支持 *内部（Internal）* 模板。
    如果 ``isaaclab`` 是从 ``site-packages`` 或 ``dist-packages`` 加载的，则 *内部* 选项将被禁用，
    并改为使用 *外部（External）* 模板。

运行模板生成器
------------------------------

按照 `安装指南 <../../setup/installation/index.html>`_ 安装 Isaac Lab。
我们推荐使用 conda 或 uv 安装方式，因为它简化了从终端调用 Python 脚本的过程。

然后，运行以下命令来生成新的外部项目或内部任务：

.. tab-set::
  :sync-group: os

  .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code-block:: bash

        ./isaaclab.sh --new  # or "./isaaclab.sh -n"

  .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code-block:: batch

        isaaclab.bat --new  :: or "isaaclab.bat -n"

生成器会通过询问以下问题来引导你根据需要设置项目/任务：

* 项目/任务的类型（外部或内部），以及根据所选类型输入的项目/任务路径或名称。
* Isaac Lab 工作流（参见 :ref:`feature-workflows`）。
* 强化学习库（参见 :ref:`rl-frameworks`），以及算法（如果所选库支持多种算法）。

外部项目的使用（生成后）
------------------------------

外部项目生成后，会在指定目录中创建一个 ``README.md`` 文件。
该文件包含如何安装项目以及如何运行任务的说明。

以下是一些入门常用命令：

.. note::

  如果 Isaac Lab 没有安装在 conda 环境或（虚拟）Python 环境中，请使用 ``FULL_PATH_TO_ISAACLAB/isaaclab.sh -p``
  （在 Windows 上为 ``FULL_PATH_TO_ISAACLAB\isaaclab.bat -p``）代替 ``python`` 来运行以下命令。

* 安装项目（以可编辑模式）。

  .. tab-set::
    :sync-group: os

    .. tab-item:: :icon:`fa-brands fa-linux` Linux
        :sync: linux

        .. code-block:: bash

          python -m pip install -e source/<given-project-name>

    .. tab-item:: :icon:`fa-brands fa-windows` Windows
        :sync: windows

        .. code-block:: batch

          python -m pip install -e source\<given-project-name>

* 列出项目中可用的任务。

  .. warning::

    如果任务名称发生更改，可能需要更新搜索模式 ``"Template-"``
    （位于 ``scripts/list_envs.py`` 文件中），以便能够列出这些任务。

  .. tab-set::
    :sync-group: os

    .. tab-item:: :icon:`fa-brands fa-linux` Linux
        :sync: linux

        .. code-block:: bash

          python scripts/list_envs.py

    .. tab-item:: :icon:`fa-brands fa-windows` Windows
        :sync: windows

        .. code-block:: batch

          python scripts\list_envs.py

* 运行一个任务。

  .. tab-set::
    :sync-group: os

    .. tab-item:: :icon:`fa-brands fa-linux` Linux
        :sync: linux

        .. code-block:: bash

          python scripts/<specific-rl-library>/train.py --task=<Task-Name>

    .. tab-item:: :icon:`fa-brands fa-windows` Windows
        :sync: windows

        .. code-block:: batch

          python scripts\<specific-rl-library>\train.py --task=<Task-Name>

更多细节，请遵循生成的项目 ``README.md`` 文件中的说明。

内部任务的使用（生成后）
------------------------------

内部任务生成后，它将与其他 Isaac Lab 任务一起提供使用。

以下是一些入门常用命令：

.. note::

  如果 Isaac Lab 没有安装在 conda 环境或（虚拟）Python 环境中，请使用 ``./isaaclab.sh -p``
  （在 Windows 上为 ``isaaclab.bat -p``）代替 ``python`` 来运行以下命令。

* 列出 Isaac Lab 中可用的任务。

  .. tab-set::
    :sync-group: os

    .. tab-item:: :icon:`fa-brands fa-linux` Linux
        :sync: linux

        .. code-block:: bash

          python scripts/environments/list_envs.py

    .. tab-item:: :icon:`fa-brands fa-windows` Windows
        :sync: windows

        .. code-block:: batch

          python scripts\environments\list_envs.py

* 运行一个任务。

  .. tab-set::
    :sync-group: os

    .. tab-item:: :icon:`fa-brands fa-linux` Linux
        :sync: linux

        .. code-block:: bash

          python scripts/reinforcement_learning/<specific-rl-library>/train.py --task=<Task-Name>

    .. tab-item:: :icon:`fa-brands fa-windows` Windows
        :sync: windows

        .. code-block:: batch

          python scripts\reinforcement_learning\<specific-rl-library>\train.py --task=<Task-Name>

* 使用虚拟智能体（dummy agent）运行任务。

  这些智能体会输出零动作或随机动作。它们可用于确保环境配置正确。

  * 零动作智能体

    .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
          :sync: linux

          .. code-block:: bash

            python scripts/zero_agent.py --task=<Task-Name>

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
          :sync: windows

          .. code-block:: batch

            python scripts\zero_agent.py --task=<Task-Name>

  * 随机动作智能体

    .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
          :sync: linux

          .. code-block:: bash

            python scripts/random_agent.py --task=<Task-Name>

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
          :sync: windows

          .. code-block:: batch

            python scripts\random_agent.py --task=<Task-Name>
