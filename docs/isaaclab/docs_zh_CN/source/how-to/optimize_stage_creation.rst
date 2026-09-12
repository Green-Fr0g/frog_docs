优化 Stage 创建
=======================

Isaac Lab 支持两种实验性特性来加速 Stage 创建：**fabric 克隆（fabric cloning）** 和
**内存中 Stage（stage in memory）**。
这些特性对于拥有数千个环境的大规模 RL 设置尤其有效。

这些特性的作用
-----------------------

**Fabric 克隆**

- 使用 Fabric 库克隆环境（参见 `USD Fabric USDRT Documentation <https://docs.omniverse.nvidia.com/kit/docs/usdrt/latest/docs/usd_fabric_usdrt.html>`_ ）
- 部分支持，并且在某些环境中默认启用（受支持的环境列表见 `限制`_ 一节）

**内存中 Stage**

- 在内存中构建 Stage，而不是使用 USD 文件，从而避免磁盘 I/O 开销
- Stage 创建完成后，如果需要渲染，Stage 会被挂载到 USD 上下文，恢复为默认的 Stage 配置
- 默认不启用

用法示例
--------------

可以通过设置 :attr:`isaaclab.scene.InteractiveSceneCfg.clone_in_fabric` 标志来启用或禁用 Fabric 克隆。

**在 RL 环境中使用 Fabric 克隆**

.. code-block:: python

    # create environment configuration
    env_cfg = CartpoleEnvCfg()
    env_cfg.scene.clone_in_fabric = True
    # setup RL environment
    env = ManagerBasedRLEnv(cfg=env_cfg)


可以通过设置 :attr:`isaaclab.sim.SimulationCfg.create_stage_in_memory` 标志来启用或禁用内存中 Stage。

**在 RL 环境中使用内存中 Stage**

.. code-block:: python

    # create config and set flag
    cfg = CartpoleEnvCfg()
    cfg.scene.num_envs = 1024
    cfg.sim.create_stage_in_memory = True
    # create env with stage in memory
    env = ManagerBasedRLEnv(cfg=cfg)

注意，如果在没有使用现有 RL 环境类的情况下启用内存中 Stage，还需要额外的几个步骤。
Stage 创建步骤应当包裹在 :py:keyword:`with` 语句中，以设置 Stage 上下文。
如果需要挂载 Stage，则应在 Stage 创建完成后调用 :meth:`~isaaclab.sim.utils.attach_stage_to_usd_context` 函数。

**在手动搭建场景时使用内存中 Stage**

.. code-block:: python

    # init simulation context with stage in memory
    sim = SimulationContext(cfg=SimulationCfg(create_stage_in_memory=True))

    # grab stage in memory and set stage context
    stage_in_memory = sim.get_initial_stage()
    with stage_utils.use_stage(stage_in_memory):
        # create cartpole scene
        scene_cfg = CartpoleSceneCfg(num_envs=1024)
        scene = InteractiveScene(scene_cfg)
        # attach stage to memory after stage is created
        sim_utils.attach_stage_to_usd_context()

    sim.play()


限制
-----------

**Fabric 克隆**

- 必须使用 USDRT 函数（而不是 USD 函数）来访问经 Fabric 克隆的环境。
- Fabric 克隆为部分支持，并且在以下列出的一些环境中默认启用。

.. code-block:: none

    1.  Isaac-Ant-Direct-v0
    2.  Isaac-Ant-v0
    3.  Isaac-Cartpole-Direct-v0
    4.  Isaac-Cartpole-Showcase-Box-Box-Direct-v0
    5.  Isaac-Cartpole-Showcase-Box-Discrete-Direct-v0
    6.  Isaac-Cartpole-Showcase-Box-MultiDiscrete-Direct-v0
    7.  Isaac-Cartpole-Showcase-Dict-Box-Direct-v0
    8.  Isaac-Cartpole-Showcase-Dict-Discrete-Direct-v0
    9.  Isaac-Cartpole-Showcase-Dict-MultiDiscrete-Direct-v0
    10. Isaac-Cartpole-Showcase-Discrete-Box-Direct-v0
    11. Isaac-Cartpole-Showcase-Discrete-Discrete-Direct-v0
    12. Isaac-Cartpole-Showcase-Discrete-MultiDiscrete-Direct-v0
    13. Isaac-Cartpole-Showcase-MultiDiscrete-Box-Direct-v0
    14. Isaac-Cartpole-Showcase-MultiDiscrete-Discrete-Direct-v0
    15. Isaac-Cartpole-Showcase-MultiDiscrete-MultiDiscrete-Direct-v0
    16. Isaac-Cartpole-Showcase-Tuple-Box-Direct-v0
    17. Isaac-Cartpole-Showcase-Tuple-Discrete-Direct-v0
    18. Isaac-Cartpole-Showcase-Tuple-MultiDiscrete-Direct-v0
    19. Isaac-Cartpole-v0
    20. Isaac-Factory-GearMesh-Direct-v0
    21.  Isaac-Factory-NutThread-Direct-v0
    22.  Isaac-Factory-PegInsert-Direct-v0
    23.  Isaac-Franka-Cabinet-Direct-v0
    24.  Isaac-Humanoid-Direct-v0
    25.  Isaac-Humanoid-v0
    26.  Isaac-Quadcopter-Direct-v0
    27.  Isaac-Repose-Cube-Allegro-Direct-v0
    28.  Isaac-Repose-Cube-Allegro-NoVelObs-v0
    29.  Isaac-Repose-Cube-Allegro-v0
    30.  Isaac-Repose-Cube-Shadow-Direct-v0
    31.  Isaac-Repose-Cube-Shadow-OpenAI-FF-Direct-v0
    32.  Isaac-Repose-Cube-Shadow-OpenAI-LSTM-Direct-v0

**内存中 Stage**

- 目前无法与 **Fabric 克隆** 同时启用。

- 将内存中 Stage 挂载到 USD 上下文可能较慢，会抵消部分甚至全部性能收益。

  - 注意，只有在启用渲染时才需要挂载。例如，在无头（headless）模式下无需挂载。

- 某些底层 Kit API 尚不支持内存中 Stage。

  - 在大多数情况下，当调用到这些 API 时，现有脚本会自动提前挂载 Stage 并打印一条警告消息。
  - 在一种特殊情况下，对于某些环境，当启用内存中 Stage 时，为地面平面着色的 API 调用会被跳过。


基准测试结果
-----------------

在启用渲染的情况下克隆 4000 个 ShadowHand 机器人的性能对比

+--------+-----------------+-------------------+------------------------+---------------------------+------------------------+------------------------+
| Test # | Stage in Memory | Clone in Fabric   | Attach Stage Time (s)  | Fabric Attach Time (s)    | Clone Paths Time (s)   | First Step Time (s)    |
+========+=================+===================+========================+===========================+========================+========================+
| 1      | Yes             | Yes               | 3.88                   | 0.15                      | 4.84                   | 1.39                   |
+--------+-----------------+-------------------+------------------------+---------------------------+------------------------+------------------------+
| 2      | No              | No                | —                      | 60.17                     | 4.46                   | 3.52                   |
+--------+-----------------+-------------------+------------------------+---------------------------+------------------------+------------------------+
| 3      | No              | Yes               | —                      | 0.47                      | 4.72                   | 2.56                   |
+--------+-----------------+-------------------+------------------------+---------------------------+------------------------+------------------------+
| 4      | Yes             | No                | 42.64                  | 21.75                     | 1.87                   | 2.16                   |
+--------+-----------------+-------------------+------------------------+---------------------------+------------------------+------------------------+
