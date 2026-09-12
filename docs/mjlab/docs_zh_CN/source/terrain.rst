.. _terrain:

地形
====

地形是场景中所有环境共享的地面。mjlab 支持两种模式：适用于无需变化地形任务的
平面地面，以及程序化地形生成器——它将一组难度可配置的子地形 (sub-terrain)
地块拼装成网格。程序化地形对训练运动 (locomotion) 策略尤其有用：难度逐步递增的
地面课程能够训练出鲁棒的行走与攀爬行为。

地形通过 ``TerrainEntityCfg`` 进行配置，并经 ``SceneCfg`` 的 ``terrain`` 字段
传入场景。关于地形如何与场景其余部分集成，请参见 :ref:`scene` 。


平面地形
--------

默认模式。用一个 MuJoCo plane geom 建模的单一地面，不含程序化几何。环境按规则
网格排列，间距由 ``SceneCfg`` 上的 ``env_spacing`` 控制。

.. code-block:: python

    from mjlab.terrains import TerrainEntityCfg

    terrain = TerrainEntityCfg(terrain_type="plane")


程序化地形
----------

对于能从地形多样性中获益的任务 (运动控制、导航)，``TerrainGeneratorCfg`` 会
拼装出一个矩形网格的子地形地块。每个地块由一个 ``SubTerrainCfg`` 生成，后者
定义几何形状及其随难度的缩放方式。

.. code-block:: python

    from mjlab.terrains import TerrainEntityCfg
    from mjlab.terrains.terrain_generator import TerrainGeneratorCfg
    import mjlab.terrains as terrain_gen

    terrain = TerrainEntityCfg(
        terrain_type="generator",
        terrain_generator=TerrainGeneratorCfg(
            size=(8.0, 8.0),
            num_rows=10,
            border_width=20.0,
            curriculum=True,
            sub_terrains={
                "flat": terrain_gen.BoxFlatTerrainCfg(proportion=0.2),
                "stairs": terrain_gen.BoxPyramidStairsTerrainCfg(
                    proportion=0.4,
                    step_height_range=(0.0, 0.15),
                    step_width=0.3,
                    platform_width=2.0,
                ),
                "rough": terrain_gen.HfRandomUniformTerrainCfg(
                    proportion=0.4,
                    noise_range=(0.02, 0.10),
                    noise_step=0.02,
                ),
            },
        ),
        max_init_terrain_level=5,
    )

生成器创建的地块网格为 ``num_rows`` 行、``num_cols`` 列 (随机模式) 或
``len(sub_terrains)`` 列 (课程模式，此时忽略 ``num_cols``)。
``sub_terrains`` 字典将名称映射到 ``SubTerrainCfg`` 实例；每个子地形的
``proportion`` 在课程模式下控制机器人在各列之间的生成分布，在随机模式下则控制
每个地块被采样的概率。


网格布局
^^^^^^^^

有两种生成模式控制地形类型在网格中的分布方式：

**课程模式** (``curriculum=True``)。每种地形类型恰好占一列；无论 ``num_cols``
取值如何，生成器都使用 ``len(sub_terrains)`` 列。同一列中的所有地块共享相同的
地形类型，难度从第 0 行 (最简单) 到第 ``num_rows - 1`` 行 (最难) 逐行递增。
``proportion`` 字段控制的是生成时机器人在各列之间的分布，而非列数。正是这种
结构化布局，使课程系统能够随着性能提升把环境推进到更难的行。

**随机模式** (``curriculum=False``)。每个地块独立地按 ``proportion`` 加权采样
地形类型，并从 ``difficulty_range`` 中采样难度。``num_cols`` 会被遵守。这种
方式提供最大的多样性，但没有结构化的难度递进。


难度参数
^^^^^^^^

每个子地形的生成函数都会收到一个 ``difficulty`` 值，用于在其可配置范围内做线性
插值。例如，``step_height_range=(0.0, 0.2)`` 的 ``BoxPyramidStairsTerrainCfg``
在难度 0 时生成平地，在难度 1 时生成 20 cm 的台阶。

在课程模式下，难度由行决定：
``difficulty = lower + (upper - lower) * row / max(num_rows - 1, 1)`` ，其中
``(lower, upper) = difficulty_range`` 。第 0 行恰好为 ``lower`` ，第
``num_rows - 1`` 行恰好为 ``upper`` ，中间各行在两者之间均匀分布。同一行的所有
列共享相同的难度标量；列与列之间可见的差异来自各子地形类型在同一难度下生成的
不同几何形状。

.. note::

   当 ``num_rows=1`` 且 ``curriculum=True`` 时，所有地块都会以
   ``difficulty = lower`` (已配置的最简单难度) 生成。如果想要一个难度随机采样
   的网格，请改用 ``curriculum=False`` 。

在随机模式下，每个地块的难度都独立地从 ``difficulty_range`` 中均匀采样。


子地形类型
----------

mjlab 提供两大类子地形类型：由 box geom 构建的 **图元地形** (primitive)，以及
由连续高程网格构建的 **高度场地形** (heightfield)。所有类型均继承自
``SubTerrainCfg``，并接受 ``proportion`` 权重和可选的 ``flat_patch_sampling``
配置。


图元地形
^^^^^^^^

完全由 box geom 构建的程序化地块。离散的几何形状使其非常适合楼梯、汀步石和
其他结构化障碍。大多数图元类型共享一些公共参数：``platform_width`` (中央平坦
区域)、``border_width`` (平坦边距)，以及一个或多个随难度缩放的范围。

.. grid:: 3

   .. grid-item-card:: 平地 (Flat)

      .. image:: _static/terrains/box_flat.png

      平坦的 box 地块。可用作课程网格中的简单基线。

   .. grid-item-card:: 金字塔楼梯 (Pyramid Stairs)

      .. image:: _static/terrains/box_pyramid_stairs.png

      金字塔形楼梯，台阶向内下降，汇聚到中央平台。

   .. grid-item-card:: 倒金字塔楼梯 (Inverted Pyramid Stairs)

      .. image:: _static/terrains/box_inverted_pyramid_stairs.png

      倒金字塔形，台阶从外向内上升。

   .. grid-item-card:: 随机楼梯 (Random Stairs)

      .. image:: _static/terrains/box_random_stairs.png

      每级台阶高度随机的金字塔楼梯。

   .. grid-item-card:: 开放楼梯 (Open Stairs)

      .. image:: _static/terrains/box_open_stairs.png

      同心台阶环。根据 ``inverted`` 标志可呈碗形或金字塔形。

   .. grid-item-card:: 随机网格 (Random Grid)

      .. image:: _static/terrains/box_random_grid.png

      高度随机采样的方块网格。

   .. grid-item-card:: 随机散布 (Random Spread)

      .. image:: _static/terrains/box_random_spread.png

      大小不一、随机放置并旋转的方块散布在地块上。

   .. grid-item-card:: 汀步石 (Stepping Stones)

      .. image:: _static/terrains/box_stepping_stones.png

      从深坑中升起的汀步石柱。

   .. grid-item-card:: 狭窄横梁 (Narrow Beams)

      .. image:: _static/terrains/box_narrow_beams.png

      从坑上方中央平台向外延伸的放射状横梁。

   .. grid-item-card:: 倾斜网格 (Tilted Grid)

      .. image:: _static/terrains/box_tilted_grid.png

      由独立倾斜的网格瓦片构成的网格。

   .. grid-item-card:: 嵌套圆环 (Nested Rings)

      .. image:: _static/terrains/box_nested_rings.png

      随机高度的同心圆环结构。


高度场地形
^^^^^^^^^^

由 MuJoCo heightfield geom 构建的连续地形剖面。表面是密集的高程采样网格，能够
生成 box geom 无法表现的平滑坡面和起伏地面。

.. grid:: 3

   .. grid-item-card:: 金字塔斜坡 (Pyramid Slope)

      .. image:: _static/terrains/hf_pyramid_slope.png

      光滑的金字塔斜坡，峰顶有平坦平台。``inverted=True`` 会把平台放在底部。

   .. grid-item-card:: 均匀随机噪声 (Random Uniform)

      .. image:: _static/terrains/hf_random_uniform.png

      随机均匀噪声，可选择降采样并插值以控制特征尺寸。

   .. grid-item-card:: 波浪 (Wave)

      .. image:: _static/terrains/hf_wave.png

      正弦波形剖面。

   .. grid-item-card:: 离散障碍 (Discrete Obstacles)

      .. image:: _static/terrains/hf_discrete_obstacles.png

      散布在平坦基底上的矩形凸起与凹坑。

   .. grid-item-card:: Perlin 噪声 (Perlin Noise)

      .. image:: _static/terrains/hf_perlin_noise.png

      分形 Perlin 噪声，生成自然的地形起伏。


预设配置
--------

mjlab 在 ``mjlab.terrains.config`` 中提供了三个现成的 ``TerrainGeneratorCfg``
预设：

``ROUGH_TERRAINS_CFG``
    一个 10x20 的随机模式网格，包含七种地形类型 (平地、楼梯、倒置楼梯、斜坡、
    倒置斜坡、随机粗糙地形、波浪)。为运动控制训练设计，难度范围适中。可通过
    ``dataclasses.replace`` 设置 ``curriculum=True`` ，将其用作课程网格 (每种
    地形类型占一列)。

``STAIRS_TERRAINS_CFG``
    一个 10 行的课程网格，专注于楼梯通行：平地加上三种难度递增的金字塔楼梯
    变体。

``ALL_TERRAINS_CFG``
    一个 10 行的随机模式网格，以相同比例覆盖所有可用地形类型。适合在最大地形
    多样性下训练。

以上预设均可直接使用，或通过 ``dataclasses.replace()`` 进行定制：

.. code-block:: python

    from dataclasses import replace
    from mjlab.terrains.config import ROUGH_TERRAINS_CFG

    my_terrains = replace(ROUGH_TERRAINS_CFG, num_rows=5)


地形课程
--------

在课程模式下，地形网格为渐进式训练提供了一个天然的坐标轴：行代表难度等级，
课程系统根据性能表现让环境在网格中上下移动。配置课程项的完整细节请参见
:ref:`curriculum` 。

关键概念如下：

- 每个环境都跟踪 ``terrain_level`` (行索引) 和 ``terrain_type`` (列索引)。
- ``TerrainEntityCfg.max_init_terrain_level`` 控制环境首次重置时可以从多高的
  行开始。设为 5 意味着环境从第 0 行到第 5 行起步。
- 内置的 ``terrain_levels_vel`` 课程项会晋升对指令速度跟踪良好的环境，并降级
  摔倒或未能取得进展的环境。
- 当环境被晋升超过最难的行时，会被随机重新分配到 ``[0, num_rows)`` 中的任意
  一行，以防止策略坍缩到单一难度等级。


平坦地块检测
------------

高度场地形可以在生成时预先计算其表面上的平坦区域。这些平坦地块可用作安全的
生成点，适合那些要求机器人在平地上起步的任务——即使整体地形崎岖不平。

平坦地块检测通过 ``SubTerrainCfg`` 上的 ``flat_patch_sampling`` 字段按子地形
进行配置：

.. code-block:: python

    from mjlab.terrains.terrain_generator import FlatPatchSamplingCfg

    rough = terrain_gen.HfRandomUniformTerrainCfg(
        proportion=0.5,
        noise_range=(0.02, 0.10),
        flat_patch_sampling={
            "spawn": FlatPatchSamplingCfg(
                num_patches=10,
                patch_radius=0.5,
                max_height_diff=0.05,
            ),
        },
    )

检测算法使用形态学滤波来寻找高度变化保持在 ``max_height_diff`` 之内的圆形
区域。检测到的地块可在运行时通过 ``scene.terrain.flat_patches["spawn"]``
访问。

若要让机器人生成在检测到的地块上而不是子地形中心，请使用
``reset_root_state_from_flat_patches`` 作为重置事件项。详情参见 :ref:`events` 。

.. note::

   只有高度场 (``Hf*``) 地形支持平坦地块检测。图元 (``Box*``) 地形没有可供
   分析的高度场数据。如果网格中的任何子地形配置了 ``flat_patch_sampling`` ，
   则会为所有单元分配平坦地块数组；没有地块的子地形，其槽位会填入该子地形的
   生成原点，从而保证重置事件总是收到有效的位置。


调试可视化
----------

地形实体向三个 geom 组添加了调试 site，可在 MuJoCo 原生查看器或 Viser 查看器
中切换显示：

- **Group 3**: 平坦地块 site (标记安全生成区域的黄色方块)
- **Group 4**: 环境原点 site (位于每个环境位置处的绿色球体)
- **Group 5**: 地形原点 site (位于每个子地形地块中心的蓝色球体)

.. figure:: _static/terrains/flat_patch_group.png
   :width: 100%
   :align: center
   :alt: 平坦地块可视化

   Viser 查看器中叠加在程序化地形网格上的平坦地块 (组 3)。
