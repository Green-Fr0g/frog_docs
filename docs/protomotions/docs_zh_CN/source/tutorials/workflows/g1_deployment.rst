G1 全身跟踪器：从数据到真机
================================================

ProtoMotions 为 Unitree G1 人形机器人提供了一条从动作数据到真机部署的
完整、可完全复现的管线。每一步——数据准备、重定向、RL 训练、ONNX 导出、
MuJoCo 验证、真机部署——都使用完全开源的代码和数据，依赖极少。

设计理念：

* **模块化且通用** —— 每个阶段都是独立自包含的脚本，输入输出清晰。
* **精简且可读** —— 部署代码避免使用重量级框架。参考 MuJoCo 测试脚本
  （``deployment/test_tracker_mujoco.py``）仅依赖 ``mujoco``、
  ``onnxruntime``、``numpy``、``pyyaml`` 和 ``torch``。
* **可复现** —— 预训练的通用动作跟踪器在完整的
  `BONES-SEED <https://huggingface.co/datasets/bones-studio/seed>`_ 数据集
  （约 14.2 万条重定向后的 G1 动作，参见 :doc:`../../getting_started/seed_g1_csv_preparation`）
  上使用 24 张 A100 GPU 训练而成。不过，用显著更少的 GPU 和更小的动作子集训练，
  也能得到一个对许多常见动作（行走、转身、手势等）表现合理的通用全身跟踪器。

.. note::

   预训练检查点、ONNX 模型和示例动作已随附于
   ``data/pretrained_models/motion_tracker/g1-bones-deploy/``，
   你可以跳过训练，直接进入部署环节。

管线概览
-----------------

.. code-block:: text

   BONES-SEED CSVs (open-source, ~142K retargeted G1 motions)
        |
        v  data/scripts/convert_g1_csv_to_proto.py
   ProtoMotions .motion files (30 fps)
        |
        v  protomotions/train_agent.py (IsaacGym/IsaacLab, multi-GPU)
   Trained checkpoint (last.ckpt + resolved_configs_inference.pt)
        |
        v  deployment/export_bm_tracker_onnx.py (CPU, no simulator)
   Unified ONNX model + YAML metadata
        |
        +---> deployment/test_tracker_mujoco.py  (reference MuJoCo test)
        |
        +---> robojudo/ integration              (MuJoCo sim + real G1)

设计要点
----------------

**统一的 ONNX 模型**。导出的 ONNX 将观测计算、actor 网络和动作处理
（tanh + PD 偏移/缩放）打包为单一模型。部署框架只需提供原始传感器信号——
关节位置/速度、躯干 IMU 姿态、骨盆角速度以及未来动作参考帧——
无需重写观测函数。这最大限度地减少了训练与部署之间出现不一致的可能性。

**MuJoCo 优先验证**。在接触真实硬件之前，我们先用一个对 ProtoMotions
几乎零依赖的独立 MuJoCo 脚本（``deployment/test_tracker_mujoco.py``）
验证 ONNX 模型。该脚本就是**部署契约**：任何能复现其行为的框架，
都能正确驱动这个策略。

**缓存的 50 fps 动作**。参考动作会从其原始帧率（通常为 30）重采样到控制频率
（50 Hz），使用与训练完全相同的 SLERP/lerp 插值，然后缓存到 ``.pt`` 文件。
后续运行只做纯 NumPy 数组索引，没有任何 PyTorch 计算。

**朝向对齐**。策略计算"机器人实际躯干朝向"与"动作第 0 帧朝向"之间
仅偏航角的偏移量。该机制始终开启，同时应对仿真（偏移接近恒等）
和真机（上电时机器人可能朝向任意方向）两种情况。

**RoboJuDo 集成**。我们选用 `RoboJuDo <https://github.com/HansZ8/RoboJuDo>`_
作为 G1 的部署框架，因为它简洁、可读、轻量——具有模块化的
Policy / Environment / Controller 架构，且没有繁重的依赖。
ProtoMotions 跟踪器以单个 Policy 类（约 230 行）的形式接入，
无需改动 RoboJuDo 核心。


步骤 1：准备动作数据
----------------------------

按照 :doc:`../../getting_started/seed_g1_csv_preparation` 将 BONES-SEED
G1 CSV 转换为 ProtoMotions ``.motion`` 文件，并打包成 MotionLib ``.pt`` 文件。

也可以直接使用预训练模型附带的示例动作。


步骤 2：训练（或使用预训练模型）
-----------------------------------

**使用预训练检查点** （推荐入门方式）：

预训练模型位于 ``data/pretrained_models/motion_tracker/g1-bones-deploy/``。
其中包含检查点、resolved 配置和预导出的 ONNX 模型。
可直接跳到步骤 3。

**从零开始训练**：

.. code-block:: bash

   python protomotions/train_agent.py \
       --robot-name g1 \
       --simulator isaaclab \
       --experiment-path data/pretrained_models/motion_tracker/g1-bones-deploy/experiment_config.py \
       --experiment-name g1_bm_tracker \
       --motion-file /path/to/bones_seed_g1_motions.pt \
       --num-envs 4096 \
       --batch-size 16384

实验配置
（``data/pretrained_models/motion_tracker/g1-bones-deploy/experiment_config.py``）
采用 BeyondMimic 风格的设置，并做了我们的一些小改动：

* **观测**：简化坐标本体感知（带噪）+ 多时间尺度的简化坐标目标姿态
  （步长 [1, 2, 4, 8]）+ 上一步处理后的动作。同时为 L2C2 平滑正则化
  添加了对应的干净（无噪）版本。
* **奖励**：BeyondMimic 朝向不变的相对身体跟踪
  （位置 + 姿态 + 线速度/角速度，按区域加权），
  加上全局锚点姿态、动作变化率惩罚和软关节限位惩罚。
* **动作处理**：BeyondMimic PD 动作配置（``make_bm_pd_action_config``）。
* **域随机化**：观测噪声、摩擦力随机化、质心随机化、推撞扰动。


步骤 3：导出 ONNX
--------------------

将策略导出为统一的 ONNX 模型。这只需要 PyTorch 和 ProtoMotions 包——
不需要仿真器或 GPU。

.. code-block:: bash

   python deployment/export_bm_tracker_onnx.py \
       --checkpoint data/pretrained_models/motion_tracker/g1-bones-deploy/last.ckpt

产出：

* ``compiled_models/unified_pipeline.onnx`` —— ONNX 模型
* ``compiled_models/unified_pipeline.yaml`` —— 详尽的元数据，记录每个
  输入/输出、时序、约定和坐标系要求

YAML 元数据就是一份机器可读的部署契约。它对每个输入的期望形状、来源表达式
以及——最关键的——角速度输入的参考系约定（参见下文的
:ref:`g1-deploy-frame-convention`）都做了文档化。

.. note::

   已预导出的 ONNX 模型位于
   ``data/pretrained_models/motion_tracker/g1-bones-deploy/compiled_models/unified_pipeline.onnx``。


步骤 4：在 MuJoCo 中测试
------------------------

参考 MuJoCo 测试脚本以极少的依赖验证 ONNX 模型。它就是**部署契约**——
任何与其行为一致的框架都能正确驱动这个策略。

.. code-block:: bash

   # First run: resample motion to 50fps and cache
   python deployment/test_tracker_mujoco.py \
       --onnx data/pretrained_models/motion_tracker/g1-bones-deploy/compiled_models/unified_pipeline.onnx \
       --motion /path/to/walk.motion \
       --cache-motion --render

   # Subsequent runs use the cached motion (no protomotions import needed)
   python deployment/test_tracker_mujoco.py \
       --onnx data/pretrained_models/motion_tracker/g1-bones-deploy/compiled_models/unified_pipeline.onnx \
       --motion /path/to/walk.50fps.pt \
       --render

其他测试模式：

.. code-block:: bash

   # Headless benchmark
   python deployment/test_tracker_mujoco.py \
       --onnx ... --motion ... --no-realtime

该脚本负责：MJCF 加载/修补、PD 配置、朝向对齐、加速度限幅、
EMA 动作滤波以及实时节拍控制。


步骤 5：通过 RoboJuDo 部署（仿真）
-----------------------------------------

`RoboJuDo <https://github.com/HansZ8/RoboJuDo>`_ 为人形机器人提供了
即插即用的部署框架，支持 MuJoCo 仿真和 Unitree 真机。
ProtoMotions BM 跟踪器支持已合入上游——无需打补丁。

**安装**：

.. code-block:: bash

   git clone https://github.com/HansZ8/RoboJuDo.git
   cd RoboJuDo
   git checkout release   # contains the ProtoMotions tracker integration
   pip install -e .
   git lfs pull           # download mesh assets

**在 MuJoCo 仿真中运行 BM 跟踪器**：

.. code-block:: bash

   python scripts/run_pipeline.py -c g1_protomotions_bm_tracker \
       --onnx-path /path/to/unified_pipeline.onnx \
       --motion-path /path/to/motion.motion

上游 RoboJuDo 集成提供了：

* ``ProtoMotionsBMTrackerPolicy`` —— 加载 ONNX 与缓存的 50fps 动作，
  结合动作历史反馈输出 PD 目标，支持朝向对齐以及动作渐入/渐出。
* 虚拟吊架 —— 用于真机部署过渡阶段的弹簧阻尼安全保护。
* 融合接入/融合退出 —— 在待机姿态与策略控制之间平滑过渡。
* CLI 增强：``--onnx-path``、``--motion-path``、``--motion-index``、
  ``--simulate-deploy``、``--hold-seconds``。

**使用你自己的部署框架**：核心契约是：

1. 按 YAML 附属文件中的文档提供 ONNX 输入（关节位置/速度、躯干姿态、
   骨盆局部角速度、上一步处理后的动作、未来动作参考）。
2. 将 ONNX 输出（PD 位置目标）施加到你的机器人的执行器上。
3. 按 YAML ``control`` 部分的文档应用动作后处理（加速度限幅 + EMA）。
4. 验证你的框架与 ``deployment/test_tracker_mujoco.py`` 在 MuJoCo
   中的行为一致。


步骤 6：部署到真机 G1
--------------------------------

.. warning::

   在真机上部署之前，请阅读
   `RoboJuDo README <https://github.com/HansZ8/RoboJuDo#alert--disclaimer-%EF%B8%8F%EF%B8%8F%EF%B8%8F>`_
   中的安全免责声明。务必验证急停功能有效。
   策略在失去平衡时可能产生剧烈动作。

通用的真机设置（以太网连接、防火墙配置、Unitree SDK 安装）请参考
`RoboJuDo real robot guide <https://github.com/HansZ8/RoboJuDo#run-robojudo-on-real-robot->`_。

机器人连接好后，运行：

.. code-block:: bash

   cd robojudo
   python scripts/run_pipeline.py -c g1_protomotions_bm_tracker_real \
       --onnx-path /path/to/unified_pipeline.onnx \
       --motion-path /path/to/motion.motion

``g1_protomotions_bm_tracker_real`` 配置在仿真配置的基础上启用了
Unitree 真机环境（``UnitreeCppEnv``）和安全检查。

安全
^^^^^^

随时按下 Unitree 遥控器上的 **A 键**即可对机器人**紧急停止**。
部署全程请手持遥控器，并在每次部署开始前验证急停功能有效。

部署阶段
^^^^^^^^^^^^^^^^^

真机部署使用四个阶段在待机与策略控制之间安全过渡。每个阶段都必不可少——
跳过或仓促进行，都可能导致关节突然运动，损坏机器人或周围环境。

**阶段 1：爬坡过渡。**
关节从机器人当前姿态缓慢插值到动作片段的第一帧。此阶段应将机器人
悬挂在吊架上。等待过渡完成后再进行下一步。

**阶段 2：融合接入。**
策略被激活，但只接收第一帧作为目标，即让它自主保持该姿态。
控制权在数秒内从静态姿态线性过渡给策略。此阶段操作员应缓慢下放吊架，
直到机器人在自身平衡下站立于地面。到阶段 2 结束时，机器人已完全自主，
可以松开吊架。

**阶段 3：跟踪。**
策略接收完整动作并开始复现它。机器人将从头到尾执行整个动作片段。

**阶段 4：融合退出。**
当动作结束或操作员通过 Unitree 遥控器触发渐出时，流程反向进行：
PD 目标从策略输出融合回初始姿态。机器人平稳回到稳定的站姿。
操作员应在此阶段将吊架升回支撑位置，以便融合退出完成时机器人
完全被吊架支撑。融合退出后，管线可以回到融合接入阶段执行下一个动作，
也可以结束本次部署会话。

传感器要求
^^^^^^^^^^^^^^^^^^^

ProtoMotions 跟踪器策略与真机 G1 兼容。所有 ONNX 输入都对应物理 G1
上可用的传感器：

* ``dof_pos`` / ``dof_vel`` —— 来自关节编码器
* ``anchor_rot`` （躯干）—— 由骨盆 IMU + 关节编码器经正向运动学计算得到
* ``root_local_ang_vel`` （骨盆）—— 直接来自骨盆 IMU 陀螺仪
  （已在机体局部坐标系中）
* 未来动作参考 —— 来自缓存的动作文件

训练时的域随机化（观测噪声、摩擦力随机化、推撞扰动）提供了对真实世界
传感器噪声和动力学差异的鲁棒性。


.. _g1-deploy-frame-convention:

重要：角速度参考系约定
---------------------------------------------

ONNX 模型期望 ``root_local_ang_vel`` 位于**骨盆刚体的局部坐标系**。
不同来源提供的角速度位于不同的参考系：

.. list-table::
   :header-rows: 1

   * - 来源
     - 参考系
     - 处理方式
   * - MuJoCo ``data.cvel[body+1, 0:3]``
     - 世界系
     - 应用 ``quat_rotate_inverse(pelvis_rot, ang_vel)``
   * - MuJoCo ``data.qvel[3:6]`` (free joint)
     - 局部系
     - 直接使用——无需旋转
   * - 真机 IMU 陀螺仪
     - 局部系
     - 直接使用——无需旋转
