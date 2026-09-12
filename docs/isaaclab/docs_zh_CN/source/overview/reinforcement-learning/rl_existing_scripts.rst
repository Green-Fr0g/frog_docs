强化学习脚本
==============================

我们为不同的强化学习库提供了封装（wrapper）。这些封装会将环境中的数据转换为
相应库的函数参数类型和返回类型。


RL-Games
--------

.. attention::

  在将 RL-Games 与 Ray 工作流结合用于分布式训练或超参数调优时，请注意，由于 Ray
  存在的安全风险，该工作流不适合在严格受控的网络环境之外使用。

-  使用
   `RL-Games <https://github.com/Denys88/rl_games>`__ 在 ``Isaac-Ant-v0`` 上训练智能体：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            # install python module (for rl-games)
            ./isaaclab.sh -i rl_games
            # run script for training
            ./isaaclab.sh -p scripts/reinforcement_learning/rl_games/train.py --task Isaac-Ant-v0 --headless
            # run script for playing with 32 environments
            ./isaaclab.sh -p scripts/reinforcement_learning/rl_games/play.py --task Isaac-Ant-v0 --num_envs 32 --checkpoint /PATH/TO/model.pth
            # run script for playing a pre-trained checkpoint with 32 environments
            ./isaaclab.sh -p scripts/reinforcement_learning/rl_games/play.py --task Isaac-Ant-v0 --num_envs 32 --use_pretrained_checkpoint
            # run script for recording video of a trained agent (requires installing `ffmpeg`)
            ./isaaclab.sh -p scripts/reinforcement_learning/rl_games/play.py --task Isaac-Ant-v0 --headless --video --video_length 200

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            :: install python module (for rl-games)
            isaaclab.bat -i rl_games
            :: run script for training
            isaaclab.bat -p scripts\reinforcement_learning\rl_games\train.py --task Isaac-Ant-v0 --headless
            :: run script for playing with 32 environments
            isaaclab.bat -p scripts\reinforcement_learning\rl_games\play.py --task Isaac-Ant-v0 --num_envs 32 --checkpoint /PATH/TO/model.pth
            :: run script for playing a pre-trained checkpoint with 32 environments
            isaaclab.bat -p scripts\reinforcement_learning\rl_games\play.py --task Isaac-Ant-v0 --num_envs 32 --use_pretrained_checkpoint
            :: run script for recording video of a trained agent (requires installing `ffmpeg`)
            isaaclab.bat -p scripts\reinforcement_learning\rl_games\play.py --task Isaac-Ant-v0 --headless --video --video_length 200

RSL-RL
------

-  使用
   `RSL-RL <https://github.com/leggedrobotics/rsl_rl>`__ 在 ``Isaac-Reach-Franka-v0`` 上训练智能体：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            # install python module (for rsl-rl)
            ./isaaclab.sh -i rsl_rl
            # run script for training
            ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Reach-Franka-v0 --headless
            # run script for playing with 32 environments
            ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task Isaac-Reach-Franka-v0 --num_envs 32 --load_run run_folder_name --checkpoint /PATH/TO/model.pt
            # run script for playing a pre-trained checkpoint with 32 environments
            ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task Isaac-Reach-Franka-v0 --num_envs 32 --use_pretrained_checkpoint
            # run script for recording video of a trained agent (requires installing `ffmpeg`)
            ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task Isaac-Reach-Franka-v0 --headless --video --video_length 200

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            :: install python module (for rsl-rl)
            isaaclab.bat -i rsl_rl
            :: run script for training
            isaaclab.bat -p scripts\reinforcement_learning\rsl_rl\train.py --task Isaac-Reach-Franka-v0 --headless
            :: run script for playing with 32 environments
            isaaclab.bat -p scripts\reinforcement_learning\rsl_rl\play.py --task Isaac-Reach-Franka-v0 --num_envs 32 --load_run run_folder_name --checkpoint /PATH/TO/model.pt
            :: run script for playing a pre-trained checkpoint with 32 environments
            isaaclab.bat -p scripts\reinforcement_learning\rsl_rl\play.py --task Isaac-Reach-Franka-v0 --num_envs 32 --use_pretrained_checkpoint
            :: run script for recording video of a trained agent (requires installing `ffmpeg`)
            isaaclab.bat -p scripts\reinforcement_learning\rsl_rl\play.py --task Isaac-Reach-Franka-v0 --headless --video --video_length 200

-  使用
   `RSL-RL <https://github.com/leggedrobotics/rsl_rl>`__ 在 ``Isaac-Velocity-Flat-Anymal-D-v0`` 上训练并蒸馏智能体：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            # install python module (for rsl-rl)
            ./isaaclab.sh -i rsl_rl
            # run script for rl training of the teacher agent
            ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Velocity-Flat-Anymal-D-v0 --headless
            # run script for distilling the teacher agent into a student agent
            ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Velocity-Flat-Anymal-D-v0 --headless --agent rsl_rl_distillation_cfg_entry_point --load_run teacher_run_folder_name
            # run script for playing the student with 64 environments
            ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py --task Isaac-Velocity-Flat-Anymal-D-v0 --num_envs 64 --agent rsl_rl_distillation_cfg_entry_point

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            :: install python module (for rsl-rl)
            isaaclab.bat -i rsl_rl
            :: run script for rl training of the teacher agent
            isaaclab.bat -p scripts\reinforcement_learning\rsl_rl\train.py --task Isaac-Velocity-Flat-Anymal-D-v0 --headless
            :: run script for distilling the teacher agent into a student agent
            isaaclab.bat -p scripts\reinforcement_learning\rsl_rl\train.py --task Isaac-Velocity-Flat-Anymal-D-v0 --headless --agent rsl_rl_distillation_cfg_entry_point --load_run teacher_run_folder_name
            :: run script for playing the student with 64 environments
            isaaclab.bat -p scripts\reinforcement_learning\rsl_rl\play.py --task Isaac-Velocity-Flat-Anymal-D-v0 --num_envs 64 --agent rsl_rl_distillation_cfg_entry_point

SKRL
----

-  使用
   `SKRL <https://skrl.readthedocs.io>`__ 在 ``Isaac-Reach-Franka-v0`` 上训练智能体：

   .. tab-set::

      .. tab-item:: PyTorch

            .. tab-set::
               :sync-group: os

               .. tab-item:: :icon:`fa-brands fa-linux` Linux
                  :sync: linux

                  .. code:: bash

                     # install python module (for skrl)
                     ./isaaclab.sh -i skrl
                     # run script for training
                     ./isaaclab.sh -p scripts/reinforcement_learning/skrl/train.py --task Isaac-Reach-Franka-v0 --headless
                     # run script for playing with 32 environments
                     ./isaaclab.sh -p scripts/reinforcement_learning/skrl/play.py --task Isaac-Reach-Franka-v0 --num_envs 32 --checkpoint /PATH/TO/model.pt
                     # run script for playing a pre-trained checkpoint with 32 environments
                     ./isaaclab.sh -p scripts/reinforcement_learning/skrl/play.py --task Isaac-Reach-Franka-v0 --num_envs 32 --use_pretrained_checkpoint
                     # run script for recording video of a trained agent (requires installing `ffmpeg`)
                     ./isaaclab.sh -p scripts/reinforcement_learning/skrl/play.py --task Isaac-Reach-Franka-v0 --headless --video --video_length 200

               .. tab-item:: :icon:`fa-brands fa-windows` Windows
                  :sync: windows

                  .. code:: batch

                     :: install python module (for skrl)
                     isaaclab.bat -i skrl
                     :: run script for training
                     isaaclab.bat -p scripts\reinforcement_learning\skrl\train.py --task Isaac-Reach-Franka-v0 --headless
                     :: run script for playing with 32 environments
                     isaaclab.bat -p scripts\reinforcement_learning\skrl\play.py --task Isaac-Reach-Franka-v0 --num_envs 32 --checkpoint /PATH/TO/model.pt
                     :: run script for playing a pre-trained checkpoint with 32 environments
                     isaaclab.bat -p scripts\reinforcement_learning\skrl\play.py --task Isaac-Reach-Franka-v0 --num_envs 32 --use_pretrained_checkpoint
                     :: run script for recording video of a trained agent (requires installing `ffmpeg`)
                     isaaclab.bat -p scripts\reinforcement_learning\skrl\play.py --task Isaac-Reach-Franka-v0 --headless --video --video_length 200

      .. tab-item:: JAX

         .. warning::

            建议在继续安装 skrl 及其依赖之前，先手动 `安装 JAX <https://jax.readthedocs.io/en/latest/installation.html>`_，因为 JAX 默认会安装其 CPU 版本。
            更多细节请访问 **skrl** 的 `安装 <https://skrl.readthedocs.io/en/latest/intro/installation.html>`_ 页面。
            注意，JAX 的 GPU 支持仅在 Linux 上可用。

            JAX 0.6.0 及更高版本（基于 CuDNN v9.8 构建）与 Isaac Lab 的 PyTorch 2.7（基于 CuDNN v9.7 构建）不兼容，因此不受支持。
            例如，要为 CUDA 12 安装兼容版本的 JAX，可以使用 ``pip install "jax[cuda12]<0.6.0" "flax<0.10.7"``。

         .. code:: bash

            # install python module (for skrl)
            ./isaaclab.sh -i skrl
            # install jax<0.6.0 for torch 2.7
            ./isaaclab.sh -p -m pip install "jax[cuda12]<0.6.0" "flax<0.10.7"
            # install skrl dependencies for JAX
            ./isaaclab.sh -p -m pip install skrl["jax"]
            # run script for training
            ./isaaclab.sh -p scripts/reinforcement_learning/skrl/train.py --task Isaac-Reach-Franka-v0 --headless --ml_framework jax
            # run script for playing with 32 environments
            ./isaaclab.sh -p scripts/reinforcement_learning/skrl/play.py --task Isaac-Reach-Franka-v0 --num_envs 32  --ml_framework jax --checkpoint /PATH/TO/model.pt
            # run script for recording video of a trained agent (requires installing `ffmpeg`)
            ./isaaclab.sh -p scripts/reinforcement_learning/skrl/play.py --task Isaac-Reach-Franka-v0 --headless --ml_framework jax --video --video_length 200

   - 使用 skrl 训练多智能体环境 ``Isaac-Shadow-Hand-Over-Direct-v0``：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            # install python module (for skrl)
            ./isaaclab.sh -i skrl
            # run script for training with the MAPPO algorithm (IPPO is also supported)
            ./isaaclab.sh -p scripts/reinforcement_learning/skrl/train.py --task Isaac-Shadow-Hand-Over-Direct-v0 --headless --algorithm MAPPO
            # run script for playing with 32 environments with the MAPPO algorithm (IPPO is also supported)
            ./isaaclab.sh -p scripts/reinforcement_learning/skrl/play.py --task Isaac-Shadow-Hand-Over-Direct-v0 --num_envs 32 --algorithm MAPPO --checkpoint /PATH/TO/model.pt

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            :: install python module (for skrl)
            isaaclab.bat -i skrl
            :: run script for training with the MAPPO algorithm (IPPO is also supported)
            isaaclab.bat -p scripts\reinforcement_learning\skrl\train.py --task Isaac-Shadow-Hand-Over-Direct-v0 --headless --algorithm MAPPO
            :: run script for playing with 32 environments with the MAPPO algorithm (IPPO is also supported)
            isaaclab.bat -p scripts\reinforcement_learning\skrl\play.py --task Isaac-Shadow-Hand-Over-Direct-v0 --num_envs 32 --algorithm MAPPO --checkpoint /PATH/TO/model.pt

Stable-Baselines3
-----------------

-  使用
   `Stable-Baselines3 <https://stable-baselines3.readthedocs.io/en/master/index.html>`__
   在 ``Isaac-Velocity-Flat-Unitree-A1-v0`` 上训练智能体：

   .. tab-set::
      :sync-group: os

      .. tab-item:: :icon:`fa-brands fa-linux` Linux
         :sync: linux

         .. code:: bash

            # install python module (for stable-baselines3)
            ./isaaclab.sh -i sb3
            # run script for training
            ./isaaclab.sh -p scripts/reinforcement_learning/sb3/train.py --task Isaac-Velocity-Flat-Unitree-A1-v0 --headless
            # run script for playing with 32 environments
            ./isaaclab.sh -p scripts/reinforcement_learning/sb3/play.py --task Isaac-Velocity-Flat-Unitree-A1-v0 --num_envs 32 --checkpoint /PATH/TO/model.zip
            # run script for playing a pre-trained checkpoint with 32 environments
            ./isaaclab.sh -p scripts/reinforcement_learning/sb3/play.py --task Isaac-Velocity-Flat-Unitree-A1-v0 --num_envs 32 --use_pretrained_checkpoint
            # run script for recording video of a trained agent (requires installing `ffmpeg`)
            ./isaaclab.sh -p scripts/reinforcement_learning/sb3/play.py --task Isaac-Velocity-Flat-Unitree-A1-v0 --headless --video --video_length 200

      .. tab-item:: :icon:`fa-brands fa-windows` Windows
         :sync: windows

         .. code:: batch

            :: install python module (for stable-baselines3)
            isaaclab.bat -i sb3
            :: run script for training
            isaaclab.bat -p scripts\reinforcement_learning\sb3\train.py --task Isaac-Velocity-Flat-Unitree-A1-v0 --headless
            :: run script for playing with 32 environments
            isaaclab.bat -p scripts\reinforcement_learning\sb3\play.py --task Isaac-Velocity-Flat-Unitree-A1-v0 --num_envs 32 --checkpoint /PATH/TO/model.zip
            :: run script for playing a pre-trained checkpoint with 32 environments
            isaaclab.bat -p scripts\reinforcement_learning\sb3\play.py --task Isaac-Velocity-Flat-Unitree-A1-v0 --num_envs 32 --use_pretrained_checkpoint
            :: run script for recording video of a trained agent (requires installing `ffmpeg`)
            isaaclab.bat -p scripts\reinforcement_learning\sb3\play.py --task Isaac-Velocity-Flat-Unitree-A1-v0 --headless --video --video_length 200

上述所有脚本都会将训练进度记录到仓库根目录 ``logs`` 目录下的 `Tensorboard`_ 中。
日志目录遵循 ``logs/<library>/<task>/<date-time>`` 的模式，其中 ``<library>``
是学习框架的名称，``<task>`` 是任务名称，``<date-time>`` 是训练脚本
被执行时的时间戳。

要查看日志，请运行：

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code:: bash

         # execute from the root directory of the repository
         ./isaaclab.sh -p -m tensorboard.main --logdir=logs

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code:: batch

         :: execute from the root directory of the repository
         isaaclab.bat -p -m tensorboard.main --logdir=logs

.. _Tensorboard: https://www.tensorflow.org/tensorboard
