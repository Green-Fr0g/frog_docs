录制仿真动画
===================================

.. currentmodule:: isaaclab

Isaac Lab 支持两种录制物理仿真动画的方式：**Stage Recorder（Stage 录制器）** 和
**OVD Recorder（OVD 录制器）**。
两者都会生成可在 Omniverse 中回放的 USD 输出，但它们的工作方式以及适用场景有所不同。

`Stage Recorder`_ 扩展在仿真过程中监听 Stage 中的所有运动和 USD 属性变化，
并将其记录为**时间采样数据**。其结果是一个 USD 文件，它只捕获动态变化的内容——**而非**
完整场景——并与录制时原始 Stage 的层级结构相匹配。
这使得它可以方便地作为子层（sublayer）添加用于回放或渲染。

该方法通过 :class:`~isaaclab.envs.ui.BaseEnvWindow` 内置在 Isaac Lab 的 UI 中。
不过，要录制仿真的动画，您需要禁用 `Fabric`_ ，以便将所有变化（例如运动和 USD 属性）
读写到 USD Stage。

**OVD Recorder** 则是为更具可扩展性或自动化的工作流设计的。它使用 OmniPVD 从播放中的 Stage
捕获仿真物理，然后将其直接**烘焙（bake）**到动画 USD 文件中。它可以在启用 Fabric 的情况下工作，
并通过 CLI 参数运行。
生成的动画 USD 可以通过拖动时间线窗口快速回放和查看，而无需执行开销高昂的物理仿真操作。

.. note::

  对于一个 USD prim，Omniverse 只支持 **要么** 进行物理仿真，**要么** 进行动画回放——绝不能同时进行。
  请在想要制作动画的 prim 上禁用物理。


Stage Recorder
--------------

在 Isaac Lab 中，Stage Recorder 集成在 :class:`~isaaclab.envs.ui.BaseEnvWindow` 类中。
它是以可视化方式捕获物理仿真的最简单方法，可直接通过 UI 使用。

要进行录制，必须禁用 Fabric——这使录制器能够追踪 USD 的变化并将其写出。

Stage Recorder 设置
~~~~~~~~~~~~~~~~~~~~~~~

Isaac Lab 在 ``base_env_window.py`` 中使用合理的默认值来设置 Stage Recorder。如有需要，
您可以直接在 Omniverse Create 中使用 Stage Recorder 扩展来覆盖或查看这些设置。

.. dropdown:: base_env_window.py 中使用的设置
  :icon: code

  .. literalinclude:: ../../../source/isaaclab/isaaclab/envs/ui/base_env_window.py
    :language: python
    :linenos:
    :pyobject: BaseEnvWindow._toggle_recording_animation_fn

用法示例
~~~~~~~~~~~~~

在独立的 Isaac Lab 环境中，传入 ``--disable_fabric`` 标志：

.. code-block:: bash

  ./isaaclab.sh -p scripts/environments/state_machine/lift_cube_sm.py --num_envs 8 --device cpu --disable_fabric

启动后，Isaac Lab UI 窗口会显示一个 "Record Animation" 按钮。
点击开始录制。再次点击停止录制。

以下文件会被保存到 ``recordings/`` 文件夹：

- ``Stage.usd`` — 禁用物理后的原始 Stage
- ``TimeSample_tk001.usd`` — 动画（时间采样）层

要回放：

.. code-block:: bash

  ./isaaclab.sh -s  # Opens Isaac Sim

在 Layers 面板中，将 ``Stage.usd`` 和 ``TimeSample_tk001.usd`` 都作为子层插入。
然后点击播放按钮即可回放动画。

有关使用图层的更多信息，请参见 `tutorial on layering in Omniverse`_ 。


OVD Recorder
------------

OVD Recorder 使用 OmniPVD 记录仿真数据，并将其直接烘焙到一个新的 USD Stage 中。
这种方法更具可扩展性，更适合大规模训练场景（例如多环境 RL）。

它不受 UI 控制——整个过程通过 CLI 标志启用并自动运行。


工作流概览
~~~~~~~~~~~~~~~~

1. 用户通过 CLI 启用动画录制来运行 Isaac Lab
2. Isaac Lab 启动仿真
3. 仿真运行时记录 OVD 数据
4. 到达指定的停止时间后，仿真被烘焙到输出的 USD 文件中，IsaacLab 随即关闭
5. 最终结果是一个完全烘焙、自成一体的 USD 动画

用法示例
~~~~~~~~~~~~~

要录制动画：

.. code-block:: bash

  ./isaaclab.sh -p scripts/tutorials/03_envs/run_cartpole_rl_env.py \
    --anim_recording_enabled \
    --anim_recording_start_time 1 \
    --anim_recording_stop_time 3

.. note::

   提供的 ``--anim_recording_stop_time`` 应大于仿真时间。

.. warning::

   目前，最后的录制步骤可能会输出许多来自 [omni.usd] 的警告日志。这是一个已知问题，
   这些警告消息可以忽略。

到达停止时间后，文件将被保存到：

.. code-block:: none

  anim_recordings/<timestamp>/baked_animation_recording.usda


.. _Stage Recorder: https://docs.omniverse.nvidia.com/extensions/latest/ext_animation_stage-recorder.html
.. _Fabric: https://docs.omniverse.nvidia.com/kit/docs/usdrt/latest/docs/usd_fabric_usdrt.html
.. _Omniverse Launcher: https://docs.omniverse.nvidia.com/launcher/latest/index.html
.. _tutorial on layering in Omniverse: https://www.youtube.com/watch?v=LTwmNkSDh-c&ab_channel=NVIDIAOmniverse
