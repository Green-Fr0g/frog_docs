配置系统
======================

.. note::

   ProtoMotions3 使用 **基于 Python 的 dataclass 配置**，
   取代了之前版本中的 Hydra 或 YAML 继承机制。
   这一设计提供了 IDE 自动补全、类型检查、更便捷的调试，并将所有配置逻辑
   集中在一处（实验文件）。

设计
-----------------

为什么用 Python dataclass 而不是 Hydra/YAML？

* **IDE 支持**：完整的自动补全和类型提示
* **没有继承的复杂性**：无需手动追踪哪个 YAML 覆盖了什么
* **可读性好**：配置逻辑是显式的 Python 代码

实验文件结构
-------------------------

每个实验文件（例如 ``examples/experiments/mimic/mlp.py``）通过一组函数
定义完整的训练配置：

.. code-block:: python

   # Required functions
   def terrain_config(args) -> TerrainConfig:
       """Build terrain configuration."""
       return TerrainConfig()

   def scene_lib_config(args) -> SceneLibConfig:
       """Build scene library configuration."""
       return SceneLibConfig(scene_file=args.scenes_file)

   def motion_lib_config(args) -> MotionLibConfig:
       """Build motion library configuration."""
       return MotionLibConfig(motion_file=args.motion_file)

   def env_config(robot_cfg, args) -> MimicEnvConfig:
       """Build environment configuration with rewards."""
       return MimicEnvConfig(
           max_episode_length=1000,
           reward_config={...},
           ...
       )

   # Optional functions
   def configure_robot_and_simulator(robot_cfg, simulator_cfg, args):
       """Customize robot and simulator settings."""
       robot_cfg.update_fields(contact_bodies=[...])

   def agent_config(robot_cfg, env_cfg, args) -> PPOAgentConfig:
       """Build agent/network configuration."""
       return PPOAgentConfig(
           model=PPOModelConfig(...),
           batch_size=args.batch_size,
           ...
       )

   def apply_inference_overrides(robot_cfg, simulator_cfg, env_cfg, agent_cfg, args):
       """Apply evaluation-time overrides (e.g., disable early termination)."""
       env_cfg.mimic_early_termination = None

配置构建流程
~~~~~~~~~~~~~~~~~~~~

当你运行 ``train_agent.py`` 时，配置按以下顺序构建：

1. 从工厂加载机器人配置（``--robot-name``）
2. 加载仿真器配置（``--simulator``）
3. 调用 ``configure_robot_and_simulator()`` 进行定制
4. 构建 ``terrain_config()``、``scene_lib_config()``、``motion_lib_config()``
5. 构建 ``env_config()``
6. 构建 ``agent_config()``
7. 应用 CLI 覆盖（``--overrides``）
8. 将全部配置保存到 ``resolved_configs.pt``

机器人配置
--------------------

``protomotions/robot_configs/`` 中的机器人配置定义了机器人：

.. code-block:: python

   @dataclass
   class G1RobotConfig(RobotConfig):
       semantic_forward_axis_xy: Tuple[float, float] = (1.0, 0.0)

       # Map common names to robot-specific body names
       common_naming_to_robot_body_names: Dict[str, List[str]] = field(
           default_factory=lambda: {
               "all_left_foot_bodies": ["left_ankle_roll_link"],
               "all_right_foot_bodies": ["right_ankle_roll_link"],
               "head_body_name": ["head"],
               "torso_body_name": ["torso_link"],
           }
       )
       
       # Asset configuration (IsaacLab derives USD from MJCF at scene build)
       asset: RobotAssetConfig = field(default_factory=lambda: RobotAssetConfig(
           asset_file_name="mjcf/g1_bm_no_mesh_box_feet.xml",
       ))
       
       # PD control parameters per joint (regex patterns)
       control: ControlConfig = field(default_factory=lambda: ControlConfig(
           override_control_info={
               ".*_hip_(pitch|yaw)_joint": ControlInfo(
                   stiffness=40.0, damping=8.0, effort_limit=88,
               ),
               ".*_knee_joint": ControlInfo(
                   stiffness=99.0, damping=19.8, effort_limit=139,
               ),
           }
       ))
       
       # Per-simulator physics settings
       simulation_params: SimulatorParams = field(default_factory=lambda: SimulatorParams(
           isaacgym=IsaacGymSimParams(fps=100, decimation=2),
           newton=NewtonSimParams(fps=200, decimation=4),
       ))

使用配置
--------------------

基本用法
~~~~~~~~~~~

.. code-block:: bash

   python protomotions/train_agent.py \
       --robot-name g1 \
       --simulator isaacgym \
       --experiment-path examples/experiments/mimic/mlp.py \
       --experiment-name my_experiment \
       --motion-file path/to/motions.pt \
       --num-envs 4096 \
       --batch-size 16384

CLI 覆盖
~~~~~~~~~~~~~

使用 ``--overrides`` 覆盖嵌套的配置值：

.. code-block:: bash

   --overrides "agent.num_mini_epochs=4" "env.max_episode_length=500"

   # Override reward weights
   --overrides "env.reward_config.contact_match_rew.weight=0.0"

   # Disable domain randomization (NOTE: "True" not "true")
   --overrides "robot.asset.self_collisions=True"

保存的配置
--------------------

所有配置都会被保存以保证可复现性：

.. code-block:: text

   results/<experiment_name>/
   ├── config.yaml              # CLI arguments + wandb_id
   ├── resolved_configs.pt      # Full config objects (pickled) - primary
   ├── resolved_configs.yaml    # Human-readable (best-effort)
   ├── experiment_config.py     # Copy of experiment file
   └── resolved_configs_inference.pt  # Configs with eval overrides

**resolved_configs.pt** 是主要的唯一事实来源。它使用 pickle 来处理
YAML 无法表示的复杂类型（Union、嵌套 dataclass、torch.Tensor）。

.. warning::

   **不要修改 resolved_configs.yaml 文件。** 它们只是为了便于人类阅读
   而生成的——真正的唯一事实来源是 ``.pt`` 文件。

   修改配置的方式：

   * **小改动**：在命令行使用 ``--overrides``
   * **大改动**：使用 ``--create-config-only`` 生成新配置，
     然后将新生成的 ``.pt`` 文件复制到你的检查点目录

恢复训练行为
~~~~~~~~~~~~~~~

.. warning::

   **恢复训练使用完全相同的已保存配置。** 恢复训练期间 CLI 覆盖会被忽略。

   如果需要修改配置，请用 ``--experiment-name`` 开启一个新实验。

训练模式：

1. **全新开始**：新的实验名称 → 从实验文件构建配置
2. **恢复训练**：相同实验名称且已有检查点 → 从 ``resolved_configs.pt`` 加载
3. **热启动**：``--checkpoint <path>`` 配合新的实验名称 → 新配置 + 旧权重

在新配置或代码变更下使用旧检查点
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在不训练的情况下生成配置（用于迁移旧检查点）：

.. code-block:: bash

   python protomotions/train_agent.py \
       --robot-name g1 --simulator isaacgym \
       --experiment-path examples/experiments/mimic/mlp.py \
       --experiment-name migrated_experiment \
       --motion-file /path/to/motion.pt \
       --num-envs 4096 --batch-size 16384 \
       --create-config-only

当代码或配置类发生变更时，请为公开产物重新生成 resolved 配置，
而不是添加隐藏的推理时迁移钩子。

组件配置（观测、奖励、终止）
--------------------------------------------------------------

所有组件都使用 ``MdpComponent`` 将纯张量核函数绑定到上下文路径：

.. code-block:: python

   from protomotions.envs.context_views import EnvContext
   from protomotions.envs.mdp_component import MdpComponent
   from protomotions.envs.rewards import compute_gt_rew, compute_action_smoothness

   reward_components = {
       "gt_rew": MdpComponent(
           compute_func=compute_gt_rew,                      # Pure tensor function
           dynamic_vars={                                  # Map params to context paths
               "current_rigid_body_pos": EnvContext.current.rigid_body_pos,
               "ref_rigid_body_pos": EnvContext.mimic.ref_state.rigid_body_pos,
           },
           static_params={"weight": 0.5, "coefficient": -100.0},  # Static parameters
       ),
       "action_smoothness": MdpComponent(
           compute_func=compute_action_smoothness,
           dynamic_vars={
               "current_processed_action": EnvContext.current_processed_action,
               "previous_processed_action": EnvContext.previous_processed_action,
           },
           static_params={"weight": -0.02},
       ),
   }

**关键特性：**

* **类型安全的绑定**：上下文路径有 IDE 自动补全（``EnvContext.current.rigid_body_pos``）
* **依赖显式**：绑定清楚表明每个核函数需要哪些数据
* **纯核函数**：函数接收张量、返回张量——易于测试
* **ONNX 就绪**：绑定直接映射到 ONNX 输入

**上下文路径** 提供双重访问方式：

* **类访问** （用于配置）：``EnvContext.current.rigid_body_pos`` → FieldPath 对象
* **实例访问** （运行时）：``ctx.current.rigid_body_pos`` → 张量值

这一设计提供了类型安全与 IDE 自动补全，并使依赖关系显式化。


智能体/模型配置
-------------------------

网络架构通过配置组合而成：

.. code-block:: python

   from protomotions.agents.ppo.config import PPOActorConfig, PPOModelConfig
   from protomotions.agents.common.config import MLPWithConcatConfig, MLPLayerConfig

   actor_config = PPOActorConfig(
       num_out=robot_config.kinematic_info.num_dofs,
       actor_logstd=-2.9,
       in_keys=["max_coords_obs", "mimic_target_poses"],
       mu_model=MLPWithConcatConfig(
           in_keys=["max_coords_obs", "mimic_target_poses"],
           normalize_obs=True,
           layers=[MLPLayerConfig(units=1024, activation="relu") for _ in range(6)],
           output_activation="tanh",
       ),
   )

``in_keys``/``out_keys`` 系统将观测连接到网络输入，
并将不同的网络层/模块相互连接。
数据流由 TensorDict 处理，这也使得 ONNX 导出更加容易。

调试技巧
--------------

* **询问 AI 助手**：想了解配置字段的含义，
  可以直接向你常用的 AI 编程助手提问。

后续步骤
----------

* :doc:`developer_tips` - 实用技巧
* 更多示例请查看 ``examples/experiments/``
