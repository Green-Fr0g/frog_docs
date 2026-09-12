.. _how-to-add-library:

接入您自己的学习库
================================

Isaac Lab 预先集成了许多库（例如 RSL-RL、RL-Games、SKRL、Stable Baselines 等）。
不过，您可能想将自己的库与 Isaac Lab 集成，或者使用与 Isaac Lab 所安装版本不同的库版本。
只要该库可以作为 Python 包使用，并且支持底层仿真器所使用的 Python 版本，这就是可行的。
例如，如果您使用的是 Isaac Sim 4.0.0 及更高版本，则需要确保该库支持 Python 3.11。

使用不同版本的库
--------------------------------------

如果您想使用与 Isaac Lab 所安装版本不同的库版本，可以通过从源码构建来安装该库，
或者使用 PyPI 上提供的其他版本的库。

例如，如果您想使用自己修改过的 `rsl-rl`_ 库版本，可以按照以下步骤操作：

1. 按照 Isaac Lab 的安装说明进行安装。这会安装默认版本的 ``rsl-rl`` 库。
2. 从 GitHub 仓库克隆 ``rsl-rl`` 库：

   .. code-block:: bash

     git clone git@github.com:leggedrobotics/rsl_rl.git


3. 在您的 Python 环境中安装该库：

   .. code-block:: bash

     # Assuming you are in the root directory of the Isaac Lab repository
     cd IsaacLab

     # Note: If you are using a virtual environment, make sure to activate it before running the following command
     ./isaaclab.sh -p -m pip install -e /path/to/rsl_rl

在这种情况下，``rsl-rl`` 库会被安装到 Isaac Lab 所使用的 Python 环境中。现在您就可以在实验中
使用 ``rsl-rl`` 库了。要查看库版本和其他详细信息，可以使用以下命令：

.. code-block:: bash

  ./isaaclab.sh -p -m pip show rsl-rl-lib

此时应该会显示 ``rsl-rl`` 库的位置为您克隆该库的目录。
例如，如果您把该库克隆到了 ``/home/user/git/rsl_rl``，上述命令的输出应该为：

.. code-block:: bash

  Name: rsl_rl
  Version: 3.0.1
  Summary: Fast and simple RL algorithms implemented in pytorch
  Home-page: https://github.com/leggedrobotics/rsl_rl
  Author: ETH Zurich, NVIDIA CORPORATION
  Author-email:
  License: BSD-3
  Location: /home/user/git/rsl_rl
  Requires: torch, torchvision, numpy, GitPython, onnx
  Required-by:


集成新库
-------------------------

向 Isaac Lab 添加新库与使用不同版本的库类似。您可以在自己的 Python 环境中安装该库并在实验中使用它。
但是，如果想将该库与 Isaac Lab 集成，您首先需要为该库编写一个包装器（wrapper），具体说明见
:ref:`how-to-env-wrappers`。

将新库与 Isaac Lab 集成可以遵循以下步骤：

1. 在扩展 ``isaaclab_rl`` 的 ``setup.py`` 中将您的库添加为额外依赖（extra-dependency）。
   这样可以确保在安装 Isaac Lab 时会安装该库，否则在该库未安装或不可用时将会报错。
2. 在 Isaac Lab 所使用的 Python 环境中安装您的库。您可以按照上一节中提到的步骤进行操作。
3. 为该库创建一个包装器。您可以查看 :mod:`isaaclab_rl` 模块，
   其中提供了针对不同库的包装器示例。您可以为您的库创建一个新包装器并将其添加到该模块中。
   如果愿意，您也可以为包装器创建一个新模块。
4. 为您的库创建用于训练和评估智能体的工作流脚本。您可以查看
   ``scripts/reinforcement_learning`` 目录中已有的工作流脚本作为示例。您可以为您的库创建新的
   工作流脚本并将其添加到该目录中。

您还可以选择为包装器添加一些测试和文档。这有助于确保包装器按预期工作，并可以指导用户如何使用该包装器。

* 添加一些测试，以确保包装器按预期工作并与该库保持兼容。
  这些测试可以添加到 ``source/isaaclab_rl/test`` 目录中。
* 为包装器添加一些文档。您可以将 API 文档添加到 ``isaaclab_rl`` 模块的
  :ref:`API 文档<api-isaaclab-rl>` 中。


配置 RL 智能体
-----------------------

将新库与 Isaac Lab 集成后，您就可以配置示例环境来使用该新库。
您可以查看 :ref:`tutorial-configure-rl-training`，了解如何配置训练过程以使用不同库的示例。


.. _rsl-rl: https://github.com/leggedrobotics/rsl_rl
