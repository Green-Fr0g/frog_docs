.. _how-to:

操作指南
=============

本节包含帮助您使用 Isaac Lab 的指南。这些指南面向已经完成教程学习、希望进一步了解如何使用
Isaac Lab 的用户。如果您刚接触 Isaac Lab，我们建议您先从教程开始。

.. note::

    本节仍在完善中。如果您有问题在此处没有得到解答，请在我们的
    `GitHub 页面 <https://github.com/isaac-sim/IsaacLab>`_ 上提交 issue。

导入新资产
---------------------

将资产导入 Isaac Lab 是一项常见任务。它包含两个步骤：将资产导入为 USD 格式，然后为该资产设置配置对象。
以下指南介绍了如何将新资产导入 Isaac Lab。

.. toctree::
    :maxdepth: 1

    import_new_asset
    write_articulation_cfg

创建固定资产
----------------------

您可能经常需要在场景中创建固定资产。例如，把一个浮动基座机器人改成固定基座机器人。
本指南介绍了创建固定资产的各种注意事项和步骤。

.. toctree::
    :maxdepth: 1

    make_fixed_prim

生成多个资产
------------------------

本指南介绍如何在每个环境中导入并配置不同的资产。当您想创建包含不同对象的多样化环境时，
这会非常有用。

.. toctree::
    :maxdepth: 1

    multi_asset_spawning

保存相机输出
--------------------

本指南介绍如何在 Isaac Lab 中保存相机输出。

.. toctree::
    :maxdepth: 1

    save_camera_output

估算您的机器上可以运行多少个相机
-------------------------------------------------

本指南演示了如何在给定参数下估算您的机器上可以运行的相机数量。

.. toctree::
    :maxdepth: 1

    estimate_how_many_cameras_can_run

配置渲染
-------------------

本指南演示了如何选择渲染模式预设以及覆盖预设的渲染设置。

.. toctree::
    :maxdepth: 1

    configure_rendering

绘制标记
---------------

本指南介绍如何使用 :class:`~isaaclab.markers.VisualizationMarkers` 类在
Isaac Lab 中绘制标记。

.. toctree::
    :maxdepth: 1

    draw_markers


与环境交互
-----------------------------

这些指南介绍如何与 Isaac Lab 中的强化学习环境进行交互。

.. toctree::
    :maxdepth: 1

    wrap_rl_env
    add_own_library


录制动画与视频
--------------------------------

本指南介绍如何在 Isaac Lab 中录制动画和视频。

.. toctree::
    :maxdepth: 1

    record_animation
    record_video


使用 CurriculumTerm 动态修改环境参数
----------------------------------------------------------------

本指南介绍如何在 Isaac Lab 中于训练期间动态修改环境参数。
内容涵盖使用课程（curriculum）工具在运行时更改环境参数。

.. toctree::
    :maxdepth: 1

    curriculums


精通 Omniverse
-------------------

Omniverse 是一个功能强大的平台，提供了广泛的特性。本指南链接了一些额外的资源，
帮助您在 Isaac Lab 中使用 Omniverse 的各项功能。

.. toctree::
    :maxdepth: 1

    master_omniverse


设置 CloudXR 遥操作
--------------------------------

本指南介绍如何在 Isaac Lab 中使用 CloudXR 和 Apple Vision Pro 进行沉浸式串流与遥操作。

.. toctree::
    :maxdepth: 1

    cloudxr_teleoperation


设置 Haply 遥操作
------------------------------

本指南介绍如何在 Isaac Lab 中使用 Haply Inverse3 和 VerseGrip 设备进行具有方向性力反馈的
机器人遥操作。

.. toctree::
    :maxdepth: 1

    haply_teleoperation


理解仿真性能
------------------------------------

本指南提供了针对不同仿真用例优化仿真性能的技巧。同时还链接了其他资源，
为 Isaac Sim 和 Omniverse Physics 提供相关的性能指南。

.. toctree::
    :maxdepth: 1

    simulation_performance


优化 Stage 创建
-----------------------

本指南介绍两种可以加速 Stage 初始化的特性：**fabric 克隆** 和 **内存中 Stage（stage in memory）** 这两种。

.. toctree::
    :maxdepth: 1

    optimize_stage_creation
