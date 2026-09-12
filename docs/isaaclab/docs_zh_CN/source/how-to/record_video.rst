在训练期间录制视频片段
=====================================

Isaac Lab 支持在训练期间使用
`gymnasium.wrappers.RecordVideo <https://gymnasium.farama.org/main/_modules/gymnasium/wrappers/record_video/>`_
类录制视频片段。

通过安装 ``ffmpeg`` 并在训练脚本中使用以下命令行参数即可启用此功能：

* ``--video``：在训练期间启用视频录制
* ``--video_length``：每个录制视频的长度（以步为单位）
* ``--video_interval``：每次视频录制之间的间隔（以步为单位）

在无头（headless）模式下运行时，请确保同时添加 ``--enable_cameras`` 参数。
注意，启用录制相当于在训练期间启用渲染，这会降低启动和运行时的性能。

用法示例：

.. code-block:: shell

    python scripts/reinforcement_learning/rl_games/train.py --task=Isaac-Cartpole-v0 --headless --video --video_length 100 --video_interval 500


录制的视频将保存在与训练检查点相同的目录中，位于
``IsaacLab/logs/<rl_workflow>/<task>/<run>/videos/train`` 。
