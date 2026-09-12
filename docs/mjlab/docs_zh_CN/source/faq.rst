.. _faq:

常见问题与故障排查
====================

本页面汇总了关于 **平台支持**、**性能**、**训练稳定性** 和 **可视化** 方面的常见问题，
并提供了实用的调试技巧以及更多资源的链接。

平台支持
--------

在 macOS 上能运行吗？
~~~~~~~~~~~~~~~~~~~~~~

可以，但性能有限。mjlab 在 macOS 上通过 MuJoCo Warp 以 **仅 CPU** 的方式运行。

- **不建议在 macOS 上训练**，因为它缺乏 GPU 加速。
- **评估可以运行**，但比在带 CUDA 的 Linux 上慢得多。

对于正式的训练任务，我们强烈推荐 **搭载 NVIDIA GPU 的 Linux 系统**。

在 Windows 上能运行吗？
~~~~~~~~~~~~~~~~~~~~~~~~

我们已在 **Windows** 和 **WSL** 上进行了初步测试，但无法保证所有工作流程都稳定。

- Windows 支持可能 **落后于** Linux。
- Windows 的 **测试频率会较低**，因为 Linux 是主要的开发和部署平台。
- 非常欢迎社区贡献来改进 Windows 支持。

CUDA 兼容性
~~~~~~~~~~~

MuJoCo Warp 并不支持所有 CUDA 版本。

- 详见 `mujoco_warp#101 <https://github.com/google-deepmind/mujoco_warp/issues/101>`_，
  了解 CUDA 兼容性详情。
- **推荐**：CUDA **12.4+**，以支持 CUDA 图中的条件执行。

如何在不触碰 GPU 的情况下在 CPU 上运行？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

传入 ``device="cpu"`` 会把 mjlab 的全部计算放到 CPU 上，但这 **不会** 阻止 Warp 初始化
GPU。Warp 运行时首次启动时，会急切地枚举 **所有** 可见设备并在其上创建 CUDA 上下文，
而不管你请求的是哪个设备。因此，在有一块可见 GPU 的机器上，即使以 ``device="cpu"``
运行，仍然会占用显存。

这一行为发生在 Warp 内部，一旦该包被导入，就无法从 Python 层面阻止。要让进程完全不
接触 GPU，请在启动前对 CUDA 隐藏这些设备：

.. code-block:: bash

   CUDA_VISIBLE_DEVICES="" uv run train.py ...

在没有可见 CUDA 设备的情况下，Warp 会以仅 CPU 模式初始化，永远不会在 GPU 上分配内存。
背景信息参见 `issue #949
<https://github.com/mujocolab/mjlab/issues/949>`_。

性能
----

它比 Isaac Lab 快吗？
~~~~~~~~~~~~~~~~~~~~~

根据我们近几个月的经验，mjlab 的速度 **与 Isaac Lab 相当甚至更快**。

你们推荐什么 GPU？
~~~~~~~~~~~~~~~~~~

- **RTX 40 系列 GPU** 或更新的型号
- **L40s、H100**

mjlab 支持多 GPU 训练吗？
~~~~~~~~~~~~~~~~~~~~~~~~~

支持。mjlab 通过 `torchrunx <https://github.com/apoorvkh/torchrunx>`_ 支持
**多 GPU 分布式训练**。

- 运行 ``train`` 命令时使用 ``--gpu-ids "[0, 1]"`` 或 ``--gpu-ids all``。
- 配置细节和示例参见 :doc:`training/distributed_training`。

训练与调试
----------

我的训练因 NaN 错误而崩溃
~~~~~~~~~~~~~~~~~~~~~~~~~

使用 ``rsl_rl`` 时，一个典型的报错如下：

.. code-block:: bash

   RuntimeError: normal expects all elements of std >= 0.0

这是由于 **物理状态** 中的 NaN/Inf 值传播到了策略网络，导致其输出的标准差变为负数或
NaN。

可能的原因有很多，也包括 **MuJoCo Warp** 中的潜在 bug（该项目目前仍处于 beta 阶段）。
mjlab 提供了两个互补的机制来帮助你处理这种情况：

1. **用于训练稳定性** - NaN 终止

添加一个 ``nan_detection`` 终止项来重置命中 NaN 的环境：

.. code-block:: python

   from mjlab.envs.mdp import terminations as mdp_term
   from mjlab.managers.termination_manager import TerminationTermCfg

   # In your ManagerBasedRlEnvCfg subclass:
   terminations = {
      # Your other terminations...
      "nan_term": TerminationTermCfg(func=mdp_term.nan_detection),
   }

这会把出现 NaN 的环境标记为已终止，使其得以重置，而训练继续进行。这些终止事件会以
``Episode_Termination/nan_term`` 的名义记录在指标中。

.. warning::

   这是一种 **权宜之计**。如果 NaN 与任务目标相关（例如，恰好在做动作尝试抓取物体时
   出现 NaN），那么策略将永远学不会完成任务的这一部分。除了这个终止项之外，务必使用
   ``nan_guard`` 排查 **根本原因**。

2. **用于调试** - NaN 守护

启用 ``nan_guard`` 以在 NaN 出现时捕获仿真状态：

.. code-block:: bash

   uv run train.py --enable-nan-guard True

详情参见 :doc:`NaN Guard 文档 <debugging/nan_guard>`。

``nan_guard`` 工具可以帮助你：

- 检查 NaN 出现那一刻的仿真状态。
- 构建最小可复现示例（MRE）。
- 向 `MuJoCo Warp 团队 <https://github.com/google-deepmind/mujoco_warp/issues>`_
  报告框架的潜在 bug。

提交隔离良好的 issue 有助于让框架不断改进，惠及所有用户。

如何查看生成的场景 XML？
~~~~~~~~~~~~~~~~~~~~~~~~~

使用 ``export-scene`` 脚本把完整场景（XML 和网格资源）导出到一个目录：

.. code-block:: bash

    uv run export-scene g1 --output-dir /tmp/g1

导出的 ``scene.xml`` 可以直接加载到 MuJoCo 中进行可视化检查或对比。这对于验证任务
配置和物理设置是否正确很有用，也可用于创建最小可复现示例，以便分享给 mjlab 或
MuJoCo Warp 的开发者。该脚本接受任务 ID、实体别名（``g1``、``go1``、``yam``）或任意
导入路径。完整细节参见 :doc:`debugging/export_scene`。

使用 decimation 时接触传感器漏检碰撞
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

当 ``decimation > 1`` 时，每个策略步会执行多个物理子步。一次短暂的接触（例如自碰撞
或非法触地）可能在子步循环内出现又消失，因此等到读取传感器时，``found`` 已经为零，
该事件对奖励和终止项来说不可见。

将 ``ContactSensorCfg`` 的 ``history_length`` 设置为与 decimation 值相等。这样传感器
会保存最近 *N* 个子步的力、力矩和距离数据。你的奖励或终止函数可以检查这段历史，检测
否则会被漏掉的接触：

.. code-block:: python

    ContactSensorCfg(
        name="self_collision",
        ...,
        fields=("found", "force"),
        history_length=4,  # matches decimation=4
    )

    # In the reward/termination function:
    force_mag = torch.norm(sensor.data.force_history, dim=-1)  # [B, N, H]
    had_contact = (force_mag > 10.0).any(dim=1).any(dim=-1)    # [B]

完整细节参见 :ref:`contact-sensor-history`。

.. note::

   带有 ``track_air_time=True`` 的足端地面传感器本身就会跨子步累积接触状态，因此
   无需启用历史记录。

.. _faq-sim-forward:

什么时候需要调用 ``sim.forward()``？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

简短回答：几乎可以肯定你不需要。

``sim.forward()`` 封装了 MuJoCo 的 ``mj_forward``，后者会运行完整的前向动力学流水线
（运动学、接触、力、约束求解、传感器），但跳过积分，保持 ``qpos``/``qvel`` 不变。它
把 ``mjData`` 中的所有派生量（``xpos``、``xquat``、``site_xpos``、``cvel``、
``sensordata`` 等）与当前的 ``qpos``/``qvel`` 同步到一致状态。
环境的 ``step()`` 方法在每步调用它一次，时机在观测计算之前，因此观测、指令和间隔
事件总能读到最新的派生量。终止和奖励管理器在该调用 *之前* 运行，因此读到的派生量滞后
一个物理子步——这是有意为之的权衡，避免了第二次 ``forward()`` 调用，同时保持 MDP
定义良好（这种滞后在所有环境和所有步上都是一致的）。

唯一需要留意的情况是：你在同一个事件或指令函数中既写状态又读派生量。例如，如果事件
A 先通过 ``entity.write_root_velocity_to_sim()`` 修改 ``qvel``，然后立即读取由
``cvel`` 计算的 ``entity.data.root_link_vel_w``，那么这次读取看到的将是写入之前的
旧值。

.. warning::

   写方法（``write_root_state_to_sim``、``write_joint_state_to_sim`` 等）直接修改
   ``qpos``/``qvel``。读属性（``root_link_pose_w``、``body_link_vel_w`` 等）返回的
   派生量只在最近一次 ``sim.forward()`` 调用时是最新的。如果你需要在同一个函数中先写
   再读，请在两者之间调用 ``env.sim.forward()``。

更深入的说明参见 `Discussion #289
<https://github.com/mujocolab/mjlab/discussions/289>`_。

为什么固定随机种子后训练仍然不可复现？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MuJoCo Warp 尚不能保证确定性，因此即使输入完全相同，同样的仿真也可能产生略有差异的
输出。这是上游已知的限制，正在
`mujoco_warp#562 <https://github.com/google-deepmind/mujoco_warp/issues/562>`_ 中
跟踪。

在上游实现确定性之前，即使设置了随机种子，mjlab 的训练也无法做到完全可复现。

我的 XML ``<option>`` 标志没有生效
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

如果你在实体 XML 中设置了诸如 ``<flag contact="disable"/>`` 之类的仿真选项，它们会被
静默忽略。这是因为 mjlab 通过 ``MjSpec.attach()`` 把实体 spec 挂载到父场景 spec 来
组合场景，而该操作不会把 ``<option>`` 设置从子 spec 传播到父 spec。这是 MuJoCo 的
设计决定：跨多个被挂载的模型合并引擎选项（timestep、重力、求解器设置等）并没有合理的
方式。

要配置仿真选项，请在任务的 Python 配置中使用 :class:`~mjlab.sim.sim.MujocoCfg`：

.. code-block:: python

   from mjlab.sim.sim import MujocoCfg, SimulationCfg

   sim=SimulationCfg(
       mujoco=MujocoCfg(
           disableflags=("contact",),
           # timestep=0.01, gravity=(0, 0, -9.81), etc.
       ),
   )

``MujocoCfg`` 会把选项直接应用到编译后的模型上，因此总是生效。如果 mjlab 检测到被
挂载的实体 spec 上存在非默认的 ``<option>`` 字段，会发出警告。

渲染与可视化
------------

有哪些可视化选项？
~~~~~~~~~~~~~~~~~~

mjlab 目前支持两种可视化器，用于策略评估和调试：

- **MuJoCo 原生可视化器** - MuJoCo 自带的可视化器。
- **Viser** - `Viser <https://github.com/nerfstudio-project/viser>`_，一个基于网页的
  3D 可视化工具。

我们正在探索 **训练时可视化**，例如实时 rollout 查看器，但目前尚未提供。

作为替代，mjlab 支持 **向 Weights & Biases（W&B）记录视频**，你可以在实验面板中直接
查看 rollout 视频。

一次最多能可视化多少个环境？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

出于性能考虑，查看器只渲染少量环境。

- **离屏渲染器** - 用于录制视频：渲染被跟踪的环境及其最近的邻居。数量由
  ``ViewerConfig.max_extra_envs`` 控制（默认 2）。
- **原生/Viser 查看器** - 受 MuJoCo 几何缓冲区限制（默认 10000 个 geom）。查看器会
  显示几何预算内能容纳的那些环境。

为什么我的固定基座机器人都堆在原点而不是排成网格？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

固定基座机器人需要 **显式的重置事件** 才能被放置到各自的 ``env_origins`` 上。如果你的
机器人都堆在 (0, 0, 0)：

**常见原因：**

1. **缺少重置事件** - 最常见的问题。
2. **env_spacing 为 0 或过小** - 检查你的 ``SceneCfg(env_spacing=...)``。即使有正确
   的重置事件，如果 ``env_spacing=0.0``，所有机器人也会位于同一位置。如果
   ``env_spacing`` 很小（例如 0.01），它们会挤在一小块区域内，远看像一条线。

**解决方案**：添加一个调用 ``reset_root_state_uniform`` 的重置事件：

.. code-block:: python

   # In your ManagerBasedRlEnvCfg
   events = {
     # For positioning the base of the robot at env_origins.
     "reset_base": EventTermCfg(
       func=mdp.reset_root_state_uniform,
       mode="reset",
       params={
         "pose_range": {},  # Empty = use default pose + env_origins
         "velocity_range": {},
       },
     ),
     # ... other events
   }

示例操作任务中就使用了这种模式（参见 ``lift_cube_env_cfg.py:85-94``）。

**为什么需要这样做**：固定基座机器人会被 ``auto_wrap_fixed_base_mocap()`` 自动包装成
mocap body，但 mocap 定位只有在你显式调用重置事件时才会发生。``env_origins`` 偏移量
是在 ``envs/mdp/events.py`` 第 131 行的 ``reset_root_state_uniform()`` 内部应用的。

示例参见 `issue #560 <https://github.com/mujocolab/mjlab/issues/560>`_。

env_origins 如何决定机器人的布局？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

机器人间距取决于你的地形配置：

**平面地形** (``terrain_type="plane"``)：
  - 自动创建一个近似正方形的网格
  - 网格尺寸：``ceil(sqrt(num_envs))`` 行 x 列
  - 间距由 ``env_spacing`` 参数控制（默认：2.0m）
  - 以 ``env_spacing=2.0`` 为例：
    - 32 个环境 → 7x5 网格，覆盖 12m x 8m
    - 4096 个环境 → 64x64 网格，覆盖 126m x 126m
  - **注意**：如果 ``env_spacing=0``，所有机器人都会位于 (0, 0, 0)
  - 实现：``terrain_importer.py:_compute_env_origins_grid()``

**程序化地形** (``terrain_type="generator"``)：
  - 原点从预先生成的地形子块中加载
  - 网格尺寸：``TerrainGeneratorCfg.num_rows x num_cols``
  - 行索引 = 难度等级（课程模式）
  - 列索引 = 地形类型变体
  - **重要的分配行为**：列（地形类型）会在环境间均匀分配，但行（难度等级）是随机采样
    的。这意味着即使 ``num_envs > num_patches``，多个环境也可能生成在同一个
    (row, col) 子块上，而其他子块空置。
  - 示例：5x5 网格（25 个子块）、100 个环境 → 每列恰好分到 20 个环境，但这 20 个
    环境在 5 行中随机分布，因此部分子块仍然为空。
  - 支持 ``randomize_env_origins()`` 在训练过程中打乱位置

如何让每种地形类型独占一列？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在 ``TerrainGeneratorCfg`` 中设置 ``curriculum=True``。这会使列的分配变得确定，每列
按归一化后的比例获得一种地形类型。

以 2 种地形类型为例：

.. code-block:: python

   TerrainGeneratorCfg(
     num_rows=3,
     num_cols=2,
     curriculum=True,  # Required for deterministic column allocation!
     sub_terrains={
       "flat": BoxFlatTerrainCfg(proportion=0.5),  # Gets column 0
       "pillars": HfDiscreteObstaclesTerrainCfg(
         proportion=0.5,  # Gets column 1
       ),
     },
   )

如果没有 ``curriculum=True``，每个子块都会被随机采样，你会在所有子块上看到两种地形
类型的随机混杂。

**注意**：当 ``num_cols`` 等于地形类型数量时，无论比例值如何（它们会被归一化），每种
地形都恰好占据一列。当 ``num_cols > num_terrain_types`` 时，比例决定每种地形类型占据
多少列。

什么是平坦子块采样，它如何影响机器人生成？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

平坦子块采样（flat patch sampling）用于在高程场地形上检测机器人可以安全生成的平坦
区域。它对高程场做形态学滤波，找出高度变化在容差范围内的圆形区域。

通过 ``flat_patch_sampling`` 可以在任意子地形上配置它：

.. code-block:: python

   from mjlab.terrains.terrain_generator import FlatPatchSamplingCfg

   "obstacles": HfDiscreteObstaclesTerrainCfg(
     ...,
     flat_patch_sampling={
       "spawn": FlatPatchSamplingCfg(
         num_patches=10,      # patches to sample per sub-terrain
         patch_radius=0.5,    # flatness check radius (meters)
         max_height_diff=0.05,  # max height variation within radius
       ),
     },
   )

然后将 ``reset_root_state_from_flat_patches`` 用作重置事件，让机器人生成在检测到的
子块上，而不是子地形中心。

**关键细节：**

- 只有高程场地形（``Hf*``）支持真正的平坦子块检测。盒式地形（``Box*``）没有可供分析
  的高程场数据。
- 只要网格配置中有任何一个子地形配置了 ``flat_patch_sampling``，平坦子块数组就会为
  **所有** 单元格分配。没有产生子块的子地形，其槽位会填入该子地形的生成原点，因此
  ``reset_root_state_from_flat_patches`` 总能拿到有效位置。
- 未配置 ``flat_patch_sampling`` 时，请使用 ``reset_root_state_uniform``，它会在子
  地形原点（``env_origins``）处生成，并可选地叠加随机偏移。

开发与扩展
----------

可以在自己的仓库中开发自定义任务吗？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

可以。mjlab 提供了 **插件系统**，让你在独立的仓库中开发任务，同时仍与核心库无缝集成：

- 你的任务会作为常规条目出现在 ``train`` 和 ``play`` 命令中。
- 你可以独立地对任务仓库进行版本管理和维护。

完整的指南将在未来的版本中提供。

资源与兼容性
------------

内置了哪些机器人？
~~~~~~~~~~~~~~~~~~

mjlab 包含两个 **参考机器人**：

- **Unitree Go1**，四足机器人。
- **Unitree G1**，人形机器人。

这些机器人的作用是：

- 作为 **机器人集成** 的最小示例。
- **基准任务** 的稳定且经过充分测试的基线。

为了保持核心库精简，我们 **不** 计划激进地扩充内置机器人库。额外的机器人可能会通过
独立的仓库或社区维护的包提供。

可以使用 USD 或 URDF 模型吗？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

不可以，mjlab 需要 **MJCF（MuJoCo XML）** 格式的模型。

- 你需要把 USD 或 URDF 资源 **转换** 为 MJCF。
- 对于许多常见机器人，你可以直接使用
  `MuJoCo Menagerie <https://github.com/google-deepmind/mujoco_menagerie>`_，其中
  提供了高质量的 MJCF 模型和资源。

获取帮助
--------

GitHub Issues
~~~~~~~~~~~~~

GitHub issues 适用于：

- **Bug 报告**
- **性能回退**
- **文档缺口**

提交 bug 时，请附带：

- CUDA 驱动和运行时版本
- GPU 型号
- 最小复现脚本
- 完整的错误日志和堆栈跟踪
- 恰当的标签（例如：``bug``、``performance``、``docs``）

`提交 issue <https://github.com/mujocolab/mjlab/issues>`_

Discussions
~~~~~~~~~~~

GitHub Discussions 适用于：

- 使用问题（配置、调试、最佳实践）
- 性能调优技巧
- 资源转换与建模问题
- 设计讨论和路线图构想

`发起讨论 <https://github.com/mujocolab/mjlab/discussions>`_

已知限制
--------

我们在 https://github.com/mujocolab/mjlab/issues/100 中跟踪稳定版尚缺失的功能。请
查看我们的 `open issues <https://github.com/mujocolab/mjlab/issues>`_，了解目前正在
进行的工作。

如果有东西无法正常工作，或者我们遗漏了什么，请
`提交 bug 报告 <https://github.com/mujocolab/mjlab/issues/new>`_。
