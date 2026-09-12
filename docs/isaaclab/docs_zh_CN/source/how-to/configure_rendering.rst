配置渲染设置
==============================

Isaac Lab 提供 3 种预设渲染模式：performance（性能）、balanced（均衡）和 quality（质量）。
您可以通过命令行参数或在脚本中选择一种模式，并根据需要自定义设置。
调整并微调渲染，以为您的工作流达到理想的平衡。

选择渲染模式
--------------------------

可以通过 2 种方式选择渲染模式。

1. 使用 :class:`~sim.RenderCfg` 中的 ``rendering_mode`` 输入类参数

   .. code-block:: python

     # for an example of how this can be used, checkout the tutorial script
     # scripts/tutorials/00_sim/set_rendering_mode.py
     render_cfg = sim_utils.RenderCfg(rendering_mode="performance")

2. 使用 ``--rendering_mode`` CLI 参数，它的优先级高于 :class:`~sim.RenderCfg` 中的 ``rendering_mode`` 参数。

   .. code-block:: bash

     ./isaaclab.sh -p scripts/tutorials/00_sim/set_rendering_mode.py --rendering_mode {performance/balanced/quality}


注意，``rendering_mode`` 默认为 ``balanced``。
但是，如果未设置启动器参数 ``--enable_cameras``，则不会应用默认的 ``rendering_mode``，
而是使用默认的 kit 渲染设置。


``set_rendering_mode.py`` 脚本的渲染示例。
为了便于评估渲染效果，示例场景包含一些反射、半透明、直接光照与环境光照，以及多种材质类型。

-  Quality 模式

   .. image:: ../_static/how-to/howto_rendering_example_quality.jpg
      :width: 100%
      :alt: Quality Rendering Mode Example

-  Balanced 模式

   .. image:: ../_static/how-to/howto_rendering_example_balanced.jpg
      :width: 100%
      :alt: Balanced Rendering Mode Example

-  Performance 模式

   .. image:: ../_static/how-to/howto_rendering_example_performance.jpg
      :width: 100%
      :alt: Performance Rendering Mode Example

覆盖特定渲染设置
---------------------------------------

可以通过 :class:`~sim.RenderCfg` 类覆盖预设的渲染设置。

有 2 种方式提供覆盖预设的设置。

1. :class:`~sim.RenderCfg` 支持通过易于使用的设置名称来覆盖特定设置，这些名称映射到底层的 RTX 设置。
   例如：

   .. code-block:: python

      render_cfg = sim_utils.RenderCfg(
         rendering_mode="performance",
         # user friendly setting overwrites
         enable_translucency=True, # defaults to False in performance mode
         enable_reflections=True, # defaults to False in performance mode
         dlss_mode="3", # defaults to 1 in performance mode
      )

   易于使用的设置列表。

   .. table::
      :widths: 25 75

      +----------------------------+--------------------------------------------------------------------------+
      |enable_translucency         |布尔值。启用镜面透射表面（例如玻璃）的半透明效果，但会损失一些性能。      |
      +----------------------------+--------------------------------------------------------------------------+
      |enable_reflections          |布尔值。启用反射，但会损失一些性能。                                      |
      +----------------------------+--------------------------------------------------------------------------+
      |enable_global_illumination  |布尔值。启用漫射全局光照，但会损失一些性能。                              |
      +----------------------------+--------------------------------------------------------------------------+
      |antialiasing_mode           |Literal["Off", "FXAA", "DLSS", "TAA", "DLAA"].                            |
      |                            |                                                                          |
      |                            |DLSS：通过 AI 从较低分辨率的输入输出更高分辨率的帧来提升性能。DLSS        |
      |                            |采样多张较低分辨率的图像，并利用运动数据和先前帧的反馈来重建原生质量的图像|
      |                            |。DLAA：使用基于 AI 的抗锯齿技术提供更高的图像质量。DLAA 使用为 DLSS      |
      |                            |开发的相同超分辨率（Super                                                 |
      |                            |Resolution）技术，重建原生分辨率的图像以最大化图像质量。                  |
      +----------------------------+--------------------------------------------------------------------------+
      |enable_dlssg                |布尔值。启用 DLSS-G。DLSS Frame Generation 通过 AI 生成更多帧来提升性能。 |
      |                            |此功能需要 Ada Lovelace 架构的 GPU，并且由于额外的线程相关活动可能会损害  |
      |                            |性能。                                                                    |
      +----------------------------+--------------------------------------------------------------------------+
      |enable_dl_denoiser          |布尔值。启用 DL 降噪器，以性能为代价提升渲染质量。                        |
      +----------------------------+--------------------------------------------------------------------------+
      |dlss_mode                   |Literal[0, 1, 2, 3]。用于 DLSS 抗锯齿，选择性能/质量权衡模式。有效值为    |
      |                            |0（Performance）、1（Balanced）、2（Quality）或 3（Auto）。               |
      +----------------------------+--------------------------------------------------------------------------+
      |enable_direct_lighting      |布尔值。启用光源的直接光照贡献。                                          |
      +----------------------------+--------------------------------------------------------------------------+
      |samples_per_pixel           |整数。定义直接光照的每像素采样数。更高的值会以性能为代价提升直接光照质量。|
      +----------------------------+--------------------------------------------------------------------------+
      |enable_shadows              |布尔值。以性能为代价启用阴影。禁用时，光源不会投射阴影。                  |
      +----------------------------+--------------------------------------------------------------------------+
      |enable_ambient_occlusion    |布尔值。启用环境光遮蔽，但会损失一些性能。                                |
      +----------------------------+--------------------------------------------------------------------------+


2. 如果需要更多控制，:class:`~sim.RenderCfg` 允许您使用 ``carb_settings`` 参数覆盖任意 RTX 设置。

   RTX 设置的示例可以在仓库内 ``apps/rendering_modes`` 中的渲染模式预设文件中找到。

   此外，RTX 文档见此处 - https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer.html。

   ``carb_settings`` 的使用示例。

   .. code-block:: python

      render_cfg = sim_utils.RenderCfg(
         rendering_mode="quality",
         # carb setting overwrites
         carb_settings={
            "rtx.translucency.enabled": False,
            "rtx.reflections.enabled": False,
            "rtx.domeLight.upperLowerStrategy": 3,
         }
      )


当前限制
-------------------

出于性能原因，我们默认使用 DLSS 进行降噪，这通常能提供更好的性能。
这可能导致渲染质量较低，在低分辨率下尤其明显。
因此，我们建议每瓦片（per-tile）或每相机的分辨率至少为 100 x 100。
对于更低分辨率的渲染，我们建议将 :class:`~sim.RenderCfg` 中的 ``antialiasing_mode`` 属性设置为
``DLAA`` ，并可能同时启用 ``enable_dl_denoiser`` 。这两项设置都有助于提升渲染质量，但也会带来
性能开销。还可以在 :class:`~sim.RenderCfg` 中指定其他渲染参数。
