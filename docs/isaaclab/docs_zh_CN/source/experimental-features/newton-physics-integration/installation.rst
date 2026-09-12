安装
====

安装 Newton 物理集成分支需要满足三个条件：

1) Isaac Lab 的 ``feature/newton`` 分支
2) Ubuntu 22.04 或 24.04（Windows 即将支持）
3) [可选] Isaac Sim 5.1（如果不使用 Omniverse 可视化器，则不需要 Isaac Sim）

首先，通过查看启动仿真应用时所创建窗口的标题来确认 Isaac Sim 的版本。你也可以在应用内的 ``Help -> About`` 菜单中找到更明确的版本信息。如果你的版本低于 5.1，必须先`更新或重新安装 Isaac Sim <https://docs.isaacsim.omniverse.nvidia.com/latest/installation/quick-install.html>`_ 才能继续。

接下来，进入你本地 Isaac Lab 仓库副本的根目录并打开一个终端。

运行以下命令，确保我们处于 ``feature/newton`` 分支：

.. code-block:: bash

    git checkout feature/newton

下面我们提供通过 pip 安装 Isaac Sim 的说明。


Pip 安装
--------

我们推荐使用 conda 管理 Python 环境。conda 可从 `这里 <https://docs.conda.io/en/latest/miniconda.html>`_ 下载安装。

如果你之前已经为 Isaac Lab 创建过虚拟环境，请务必从一个全新的环境开始，以避免任何依赖冲突。如果你曾通过 pip 安装过较早版本的 mujoco、mujoco-warp 或 newton 包，我们建议先用 ``pip cache purge`` 清理 pip 缓存，以清除可能与最新版本冲突的旧版本缓存。

创建一个新的 conda 环境：

.. code-block:: bash

    conda create -n env_isaaclab python=3.11

激活该环境：

.. code-block:: bash

    conda activate env_isaaclab

安装正确版本的 torch 和 torchvision：

.. code-block:: bash

    pip install -U torch==2.7.0 torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128

[可选] 安装 Isaac Sim 5.1：

.. code-block:: bash

    pip install "isaacsim[all,extscache]==5.1.0" --extra-index-url https://pypi.nvidia.com

安装 Isaac Lab 扩展及依赖：

.. code-block:: bash

    ./isaaclab.sh -i


测试安装
--------

要验证安装是否成功，在 Isaac Lab 仓库根目录下运行以下命令：

.. code-block:: bash

    ./isaaclab.sh -p scripts/environments/zero_agent.py --task Isaac-Cartpole-Direct-v0 --num_envs 128


请注意，由于 Newton 所需的 Warp 版本比 Isaac Sim 5.1 更新，可能存在一些不兼容问题，导致诸如 ``ModuleNotFoundError: No module named 'warp.sim'`` 之类的错误。这些错误可以忽略，不会影响使用。
