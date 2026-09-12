.. _motion-imitation:

动作模仿
========

mjlab 可以训练人形机器人策略来模仿参考动作。本页介绍动作数据的预处理与
训练。

WandB 注册表设置
----------------

mjlab 使用 `Weights & Biases <https://wandb.ai/>`_ 存储和加载参考动作。
在预处理任何动作之前，请先按照
`BeyondMimic instructions <https://github.com/HybridRobotics/whole_body_tracking/blob/main/README.md#motion-preprocessing--registry-setup>`_
创建一个 WandB 注册表 (只需其中的注册表创建步骤；跳过那里给出的
``csv_to_npz.py`` 命令)。

动作预处理
----------

参考动作是经过重定向 (retargeting) 的 CSV 文件，遵循 Unitree 的广义坐标
约定 (基座位置、以 xyzw 表示的基座四元数，之后是关节角度)。

将 CSV 转换为 mjlab 期望的 NPZ 格式：

.. code-block:: bash

   MUJOCO_GL=egl uv run -m mjlab.scripts.csv_to_npz \
       --input-file <PATH_TO_CSV> \
       --output-name <MOTION_NAME> \
       --input-fps 30 \
       --output-fps 50 \
       --render True

该脚本会在 MuJoCo Warp 中播放动作、为每个刚体计算正运动学，并把生成的
NPZ 上传到你的 WandB 注册表。

.. warning::

   你 **必须** 使用 mjlab 的转换器 (``mjlab.scripts.csv_to_npz``)。其他
   框架 (如 IsaacLab) 的转换器生成的 NPZ 文件刚体顺序互不兼容。NPZ 中
   存储的是按刚体编号索引的预计算刚体位置和四元数，而不同物理引擎分配
   刚体索引的方式不同 (MuJoCo 采用深度优先遍历，PhysX 采用广度优先)。
   顺序不匹配的 NPZ 会把跟踪目标映射到错误的刚体上，训练将无法收敛。

训练
----

.. code-block:: bash

   uv run train Mjlab-Tracking-Flat-Unitree-G1 \
       --registry-name your-org/motions/motion-name \
       --env.scene.num-envs 4096

评估
----

.. code-block:: bash

   uv run play Mjlab-Tracking-Flat-Unitree-G1 \
       --wandb-run-path your-org/mjlab/run-id
