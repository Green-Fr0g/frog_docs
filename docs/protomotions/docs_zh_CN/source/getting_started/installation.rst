安装
====

ProtoMotions 支持五种仿真后端：IsaacGym、IsaacLab、Genesis、Newton 和 MuJoCo。
你可以只安装自己需要的仿真器，仿真后端通过配置文件选择。

**已测试版本：**

.. raw:: html

   <p>
     <a href="https://pypi.org/project/newton/1.0.0/"><img src="https://img.shields.io/badge/Newton-1.0.0-brightgreen.svg" alt="Newton"></a>
     <a href="https://github.com/isaac-sim/IsaacLab/commit/4ecd0b036da19ff6ad2bb4d621f886b63e9f6db8"><img src="https://img.shields.io/badge/IsaacLab-3.0-blue.svg" alt="IsaacLab"></a>
     <a href="https://developer.nvidia.com/isaac-gym"><img src="https://img.shields.io/badge/IsaacGym-Preview_4-blue.svg" alt="IsaacGym"></a>
     <a href="https://github.com/Genesis-Embodied-AI/Genesis"><img src="https://img.shields.io/badge/Genesis-untested-lightgrey.svg" alt="Genesis"></a>
     <a href="https://github.com/google-deepmind/mujoco"><img src="https://img.shields.io/badge/MuJoCo-3.0+-orange.svg" alt="MuJoCo"></a>
   </p>

.. note::

   建议为每个仿真器创建**独立的虚拟环境**，以避免依赖冲突。
   对于 IsaacGym、Genesis 和 MuJoCo，推荐使用 **conda** 或 **venv**；对于 IsaacLab 和 Newton，推荐使用 **uv**。

选择哪种安装方式？
------------------

.. list-table::
   :header-rows: 1
   :widths: 22 30 48

   * - 仿真器
     - 支持的安装方式
     - 说明
   * - MuJoCo、Newton、Genesis
     - 源码检出 **或** uv 依赖
     - Genesis 为实验性支持。
   * - IsaacLab
     - **固定版本的源码检出**
     - IsaacLab 12.0.0 与 Isaac Sim 6.0 需要 Python 3.12 和 Linux x86_64。
   * - IsaacGym
     - **仅支持源码检出**
     - IsaacGym 未发布到 PyPI：需要从 NVIDIA 下载并手动安装，且要求 **Python 3.8**。

如果你需要预训练检查点、动作文件或 ``examples/`` 实验文件，请使用源码检出——
它们存放在 Git LFS 中，不包含在安装包里。

前置条件
--------

克隆仓库后，拉取并检出存储在 Git LFS 中的文件：

.. code-block:: bash

   git lfs install
   git lfs pull

由于预训练检查点、动作文件、网格和 USD 资产体积较大，这一步可能需要一些时间。
如果你手动拉取了一部分资产，请确保这些文件已真正检出，而不是仍处于 Git LFS 指针文件状态。
指针文件以 ``version https://git-lfs.github.com/spec/v1`` 开头，会导致诸如
``is not a valid usda layer`` 之类的错误（在 IsaacLab 加载机器人资产时出现）。

将 ProtoMotions 作为依赖使用（uv）
-----------------------------------

可以直接从 Git 安装 ProtoMotions。机器人网格和 USD 资产是 Git LFS 对象，因此必须在启用 LFS 的情况下拉取源码——
``lfs = true`` 需要 uv 0.11.32 及以上版本：

.. code-block:: bash

   uv init --python 3.11 my-project
   cd my-project
   uv add --lfs "protomotions[newton] @ git+https://github.com/NVlabs/ProtoMotions.git"

也可以在下游项目的 ``pyproject.toml`` 中配置该依赖：

.. code-block:: toml

   [project]
   dependencies = ["protomotions[newton]"] # or [mujoco] / [isaaclab] / [genesis]

   [tool.uv]
   required-version = ">=0.11.32"

   [tool.uv.sources]
   protomotions = { git = "https://github.com/NVlabs/ProtoMotions.git", lfs = true }

然后通过安装的入口点运行训练：

.. code-block:: bash

   uv run protomotions train-agent \
       --robot-name g1 --simulator newton \
       --experiment-path experiments/my_experiment.py \
       --experiment-name my_run \
       --motion-file data/my_motion.pt \
       --num-envs 4096 --batch-size 16384

``uv run protomotions info`` 会打印解析后的资产根目录，以及哪些仿真器模块可导入。

安装包包含 Python 模块和完整的机器人资产树，但**不包含** SMPL/SMPL-H 资产
（后者附带独立的许可条款）。预训练检查点、动作文件和 ``examples/`` 实验文件也不包含在内；
如果需要这些内容，请保留一份 Git LFS 检出，并设置 ``PROTOMOTIONS_ASSET_ROOT``。

将 IsaacLab 作为依赖
~~~~~~~~~~~~~~~~~~~~

受支持的 IsaacLab 技术栈是一个固定版本的源码工作区，而不是由 ProtoMotions 独立解析的依赖。
请按照下文的 IsaacLab 安装流程创建其 Python 3.12 的 ``.venv``，然后将 ProtoMotions 安装到该环境中。
在单独的项目里直接执行 ``uv add protomotions[isaaclab]`` 并不会安装所需的 IsaacLab 源码版本。

选择你的仿真器
--------------

IsaacGym
~~~~~~~~

IsaacGym 要求 **Python 3.8**。

1. 创建 conda 环境：

   .. code-block:: bash

      conda create -n isaacgym python=3.8
      conda activate isaacgym

2. 下载 IsaacGym Preview 4：

   .. code-block:: bash

      wget https://developer.nvidia.com/isaac-gym-preview-4
      tar -xvzf isaac-gym-preview-4

3. 安装 IsaacGym Python API：

   .. code-block:: bash

      pip install -e isaacgym/python

4. 安装 ProtoMotions 及依赖：

   .. code-block:: bash

      pip install -e /path/to/protomotions
      pip install -r /path/to/protomotions/requirements_isaacgym.txt

IsaacLab
~~~~~~~~

ProtoMotions 面向来自 IsaacLab 公开提交 ``4ecd0b036da19ff6ad2bb4d621f886b63e9f6db8`` 的
IsaacLab 12.0.0 与 Isaac Sim 6.0。该技术栈要求 **Python 3.12**。
请在安装 ProtoMotions 之前先安装固定版本的 IsaacLab 源码检出，以确保其工作区包和仿真器依赖就位。

1. 克隆并切换到受支持的 IsaacLab 版本：

   .. code-block:: bash

      git clone https://github.com/isaac-sim/IsaacLab.git
      cd IsaacLab
      git checkout 4ecd0b036da19ff6ad2bb4d621f886b63e9f6db8

2. 创建固定版本的 IsaacLab 环境并安装其 Isaac Sim 扩展：

   .. code-block:: bash

      uv sync --extra isaacsim
      source .venv/bin/activate

3. 安装 ProtoMotions 及依赖：

   .. code-block:: bash

      uv pip install -e "/path/to/protomotions[isaaclab]" \
        --extra-index-url https://pypi.nvidia.com
      uv pip install -r /path/to/protomotions/requirements_isaaclab.txt

.. note::

   IsaacLab/IsaacSim 在首次使用时可能会提示接受 NVIDIA EULA。请在运行无人值守的
   无界面任务之前，以交互方式完成接受。

Genesis（实验性）
~~~~~~~~~~~~~~~~~

Genesis 要求 **Python 3.10**。

1. 创建 conda 环境：

   .. code-block:: bash

      conda create -n genesis python=3.10
      conda activate genesis

2. 安装 `Genesis <https://genesis-world.readthedocs.io/en/latest/index.html>`_

3. 安装 ProtoMotions 及依赖：

   .. code-block:: bash

      pip install -e /path/to/protomotions
      pip install -r /path/to/protomotions/requirements_genesis.txt

Newton
~~~~~~~~~~~~~

Newton 是基于 NVIDIA Warp 构建的 GPU 加速物理仿真器，现已上架 PyPI。
完整的安装细节请参阅 `Newton 安装指南 <https://newton-physics.github.io/newton/1.0.0/guide/installation.html>`__。

**系统要求**：Python 3.10+（推荐 3.11+）、NVIDIA GPU（计算能力 >= 5.0）、驱动 545+

1. 创建虚拟环境：

   .. code-block:: bash

      python -m venv .venv_newton
      source .venv_newton/bin/activate

2. 安装 PyTorch 和 Newton：

   .. code-block:: bash

      pip install torch --index-url https://download.pytorch.org/whl/cu124
      pip install "newton[examples]==1.0.0"

   如果只需要无界面模式（不使用查看器），请用 ``newton[sim]==1.0.0`` 替代 ``newton[examples]==1.0.0``。

3. 安装 ProtoMotions 及依赖：

   .. code-block:: bash

      pip install -e /path/to/protomotions
      pip install -r /path/to/protomotions/requirements_newton.txt

.. note::

   在 Python 3.10 上，``imgui-bundle``（``newton[examples]`` 的依赖）没有预编译的 wheel，
   需要从源码编译，可能耗时 10-20 分钟。Python 3.11+ 提供预编译 wheel，可即时安装。

MuJoCo（仅 CPU）
~~~~~~~~~~~~~~~~

MuJoCo 是一个仅使用 CPU 的后端，适合在没有 GPU 的情况下进行快速测试和调试。它仅支持单个环境（``num_envs=1``）。

**系统要求**：Python 3.10+，无需 GPU

1. 创建 conda 环境：

   .. code-block:: bash

      conda create -n protomotions_mujoco python=3.10
      conda activate protomotions_mujoco

2. 安装 CPU 版 PyTorch（更轻量，无需 CUDA）：

   .. code-block:: bash

      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

3. 安装 ProtoMotions 及依赖：

   .. code-block:: bash

      pip install -e /path/to/protomotions
      pip install -r /path/to/protomotions/requirements_mujoco.txt

4. 使用 MuJoCo 运行推理：

   .. code-block:: bash

      python protomotions/inference_agent.py \
        --checkpoint data/pretrained_models/motion_tracker/g1-bones-deploy/last.ckpt \
        --motion-file data/motion_for_trackers/g1_bones_seed_mini.pt \
        --simulator mujoco \
        --num-envs 1

   本示例使用随附的 G1 动作跟踪器及配套的动作数据。检查点目录中包含所需的
   ``resolved_configs_inference.pt`` 文件。

.. note::

   MuJoCo 后端适用于快速验证策略和调试。如需训练或大规模评估，请使用 GPU 加速的后端（IsaacGym、IsaacLab、Newton、Genesis）。

故障排查
--------

IsaacLab 问题
~~~~~~~~~~~~~

**Torch Inductor 警告**

在较小的 GPU 上，IsaacLab 评估可能打印类似以下的警告：

.. code-block:: text

   Not enough SMs to use max_autotune_gemm mode

这是一条非致命的 PyTorch 性能警告。除非其后跟随了真正的 traceback，否则评估可以继续进行。

IsaacGym 问题
~~~~~~~~~~~~~

**libpython 错误**

如果遇到与 ``libpython`` 相关的错误，需要将 ``LD_LIBRARY_PATH`` 指向你的 conda 环境：

.. code-block:: bash

   # First, check your conda environment path
   conda info -e
   
   # Then set LD_LIBRARY_PATH (replace with your actual conda env path)
   export LD_LIBRARY_PATH=/path/to/conda/envs/your_env/lib:$LD_LIBRARY_PATH
   
   # For example:
   export LD_LIBRARY_PATH=${CONDA_PREFIX}/lib:$LD_LIBRARY_PATH

要让该设置仅对这个 conda 环境永久生效，可以添加激活钩子：

.. code-block:: bash

   mkdir -p "${CONDA_PREFIX}/etc/conda/activate.d" "${CONDA_PREFIX}/etc/conda/deactivate.d"
   cat > "${CONDA_PREFIX}/etc/conda/activate.d/isaacgym-libpython.sh" <<'EOF'
   export _OLD_LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}"
   export LD_LIBRARY_PATH="${CONDA_PREFIX}/lib:${LD_LIBRARY_PATH:-}"
   EOF
   cat > "${CONDA_PREFIX}/etc/conda/deactivate.d/isaacgym-libpython.sh" <<'EOF'
   export LD_LIBRARY_PATH="${_OLD_LD_LIBRARY_PATH:-}"
   unset _OLD_LD_LIBRARY_PATH
   EOF

**内存问题**

如果在训练期间遇到内存问题：

.. code-block:: bash

   # Reduce number of environments in your training command
   --num-envs 1024

后续步骤
--------

完成安装后，请继续阅读 :doc:`quickstart` 指南，训练你的第一个智能体或运行预训练模型。
