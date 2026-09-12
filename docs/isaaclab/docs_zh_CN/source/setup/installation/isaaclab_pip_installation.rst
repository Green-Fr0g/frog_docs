使用 Isaac Lab Pip 包安装
=========================================

从 Isaac Lab 2.0 开始，我们提供了 pip 包，可以通过 pip 同时安装 Isaac Sim 和 Isaac Lab 的扩展。
请注意，此安装流程只推荐给正在开发基于 Isaac Lab 构建的其他扩展项目的高级用户使用。
Isaac Lab 的 pip 包 **不** 包含任何用于训练、推理或运行演示和示例等独立（standalone）工作流的
Python 脚本。因此，通过 pip 安装 Isaac Lab 时，用户需要自行定义运行脚本。

要了解如何在 Isaac Lab 之上搭建你自己的项目，请参阅 :ref:`template-generator`。

.. note::

   目前，我们只为 Isaac Lab 的每个大版本提供 pip 包。
   例如，我们为 2.1.0 和 2.2.0 版本提供 pip 包，但不为 2.1.1 提供。
   未来，我们将为 Isaac Lab 的每个小版本提供 pip 包。

.. include:: include/pip_python_virtual_env.rst

安装依赖
~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   如果你使用 UV 创建了虚拟环境，请在下列命令中将 ``pip`` 替换为 ``uv pip``。

-  安装 Isaac Lab 包以及 Isaac Sim：

   .. code-block:: none

      pip install isaaclab[isaacsim,all]==2.3.2 --extra-index-url https://pypi.nvidia.com

-  安装与你的系统架构匹配、面向 CUDA 12.8 且支持 CUDA 的 PyTorch 2.7.0 构建：

   .. tab-set::
      :sync-group: pip-platform

      .. tab-item:: :icon:`fa-brands fa-linux` Linux (x86_64)
         :sync: linux-x86_64

         .. code-block:: bash

            pip install -U torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128

      .. tab-item:: :icon:`fa-brands fa-windows` Windows (x86_64)
         :sync: windows-x86_64

         .. code-block:: bash

            pip install -U torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128

      .. tab-item:: :icon:`fa-brands fa-linux` Linux (aarch64)
         :sync: linux-aarch64

         .. code-block:: bash

            pip install -U torch==2.9.0 torchvision==0.24.0 --index-url https://download.pytorch.org/whl/cu130

         .. note::

            在 aarch64 上安装 Isaac Lab 后，你可能会遇到如下警告：

            .. code-block:: none

               ERROR: ld.so: object '...torch.libs/libgomp-XXXX.so.1.0.0' cannot be preloaded: ignored.

            当系统和 PyTorch 的 ``libgomp`` （GNU OpenMP）库同时被预加载时，就会出现此警告。
            Isaac Sim 期望使用 **系统** 的 OpenMP 运行时，而 PyTorch 有时会捆绑自己的版本。

            要解决此问题，请先取消已有的 ``LD_PRELOAD``，然后将其设置为仅使用系统库：

            .. code-block:: bash

               unset LD_PRELOAD
               export LD_PRELOAD="$LD_PRELOAD:/lib/aarch64-linux-gnu/libgomp.so.1"

            这样可以确保为 Isaac Sim 和 Isaac Lab 预加载正确的 ``libgomp`` 库，
            从而消除运行时的预加载警告。

-  如果你想使用 ``rl_games`` 进行训练和推理，请安装
   其支持 Python 3.11 的 fork：

   .. code-block:: none

      pip install git+https://github.com/isaac-sim/rl_games.git@python3.11

.. include:: include/pip_verify_isaacsim.rst

运行 Isaac Lab 脚本
~~~~~~~~~~~~~~~~~~~~~~~~~

按照上述步骤操作后，你的 Python 环境现在应该可以访问所有的 Isaac Lab 扩展了。
要运行用户为 Isaac Lab 编写的脚本，只需执行

.. code:: bash

    python my_awesome_script.py

生成 VS Code 设置
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

由于这种安装方式产生的目录结构，VS Code 的 IntelliSense（代码补全、参数信息
和成员列表等）默认无法工作。要完成设置（定义导入解析的搜索路径、
默认 Python 解释器的路径以及其他设置），请在给定的工作区文件夹中运行以下命令：

.. code-block:: bash

   python -m isaaclab --generate-vscode-settings


.. warning::

   该命令会在工作区文件夹中生成 ``.vscode/settings.json`` 文件。
   如果该文件已存在，它将被覆盖（会先显示确认提示）。
