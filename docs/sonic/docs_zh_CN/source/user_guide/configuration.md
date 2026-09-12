# 配置指南

SONIC 使用 [Hydra](https://hydra.cc/) 进行层次化配置。本指南介绍配置结构以及最重要的可调参数。

## 配置层级

当你运行如下训练命令时：

```bash
python gear_sonic/train_agent_trl.py +exp=manager/universal_token/all_modes/sonic_release
```

Hydra 会从一串 YAML 文件组合出最终配置：

```
gear_sonic/config/
├── base.yaml                    # 全局默认值（seed、num_envs、路径）
├── base/
│   ├── hydra.yaml               # Hydra 输出目录设置
│   └── structure.yaml           # 解析后的实验目录结构
├── algo/
│   └── ppo_im_phc.yaml          # PPO 超参数
├── manager_env/
│   ├── base_env.yaml            # 环境默认值（sim_dt、decimation、回合长度）
│   ├── actions/tracking/base.yaml
│   ├── commands/tracking/base.yaml
│   │   └── terms/motion.yaml    # 动作库、刚体名称、未来帧
│   ├── rewards/tracking/
│   │   └── base_5point_local_feet_acc.yaml  # 奖励项组成
│   │       └── terms/*.yaml     # 各个奖励项及其权重
│   ├── terminations/tracking/
│   │   └── base_adaptive_strict_ori_foot_xyz.yaml  # 终止条件组成
│   │       └── terms/*.yaml     # 各个终止条件
│   ├── events/tracking/
│   │   └── level0_4.yaml        # 域随机化事件
│   └── observations/
│       ├── tokenizer/           # 编码器输入观测
│       ├── policy/              # 策略（Actor）观测
│       └── critic/              # Critic 观测
├── actor_critic/
│   └── universal_token/         # 网络结构（编码器、解码器、量化器）
├── aux_losses/
│   └── universal_token/         # 辅助损失项
├── trainer/
│   └── trl_ppo_aux.yaml         # 训练器配置（带辅助损失的 PPO）
├── callbacks/                   # 训练回调（保存、评估、W&B、重采样）
└── exp/manager/universal_token/all_modes/
    ├── sonic_release.yaml       # 原始发布实验配置
    └── sonic_v1_1.yaml          # SONIC v1.1 实验配置
```

实验配置（`sonic_release.yaml`）位于顶层，会覆盖基础配置中的特定值。你还可以在命令行用 `++key=value` 进一步覆盖任何值。

## 覆盖配置值

Hydra 使用 `++` 前缀强制覆盖值（包括嵌套值）：

```bash
# 覆盖顶层值
python gear_sonic/train_agent_trl.py +exp=... num_envs=16

# 覆盖嵌套值（用点表示嵌套层级）
python gear_sonic/train_agent_trl.py +exp=... \
    ++manager_env.commands.motion.motion_lib_cfg.motion_file=/path/to/data

# 覆盖奖励权重
python gear_sonic/train_agent_trl.py +exp=... \
    ++manager_env.rewards.tracking_anchor_pos.weight=1.0
```

## 需要调优的关键参数

### 训练规模

| 参数 | 默认值 | 位置 | 说明 |
|-----------|---------|----------|-------------|
| `num_envs` | 4096 | `base.yaml` | 并行环境数。调试时可减小（`16`），追求吞吐量时可增大。 |
| `headless` | True | `base.yaml` | 设为 `False` 可打开 Isaac Lab 查看器进行可视化调试。 |
| `seed` | 0 | `base.yaml` | 用于可复现性的随机种子。 |

### PPO 超参数

| 参数 | 默认值 | 位置 | 说明 |
|-----------|---------|----------|-------------|
| `algo.config.actor_learning_rate` | 2e-5 | `ppo_im_phc.yaml` | Actor 学习率。微调时调低，从零训练时调高。 |
| `algo.config.critic_learning_rate` | 1e-3 | `ppo_im_phc.yaml` | Critic 学习率。通常为 Actor 学习率的 10-100 倍。 |
| `algo.config.num_learning_epochs` | 5 | `ppo_im_phc.yaml` | 每批经验数据对应的 PPO 更新轮数。 |
| `algo.config.num_mini_batches` | 4 | `ppo_im_phc.yaml` | 每个 PPO 轮次的小批次数。 |
| `algo.config.num_steps_per_env` | 24 | `sonic_release.yaml` | rollout 长度（每次 PPO 更新前每个环境的步数）。 |
| `algo.config.gamma` | 0.99 | `ppo_im_phc.yaml` | 折扣因子。 |
| `algo.config.lam` | 0.95 | `ppo_im_phc.yaml` | GAE lambda（广义优势估计参数）。 |
| `algo.config.clip_param` | 0.2 | `ppo_im_phc.yaml` | PPO 裁剪参数。 |
| `algo.config.entropy_coef` | 0.01 | `ppo_im_phc.yaml` | 熵奖励系数。 |
| `algo.config.desired_kl` | 0.01 | `ppo_im_phc.yaml` | 自适应学习率调度所用的目标 KL 散度。 |
| `algo.config.num_learning_iterations` | 100000 | `ppo_im_phc.yaml` | 总训练迭代数。 |

### 仿真

| 参数 | 默认值 | 位置 | 说明 |
|-----------|---------|----------|-------------|
| `manager_env.config.sim_dt` | 0.005 | `base_env.yaml` | 物理时间步长（200 Hz）。越小越稳定但越慢。 |
| `manager_env.config.decimation` | 4 | `base_env.yaml` | 策略每 `decimation` 个仿真步运行一次（200 Hz 仿真下策略频率为 50 Hz）。 |
| `manager_env.config.episode_length_s` | 10.0 | `base_env.yaml` | 超时重置前的回合时长（秒）。 |
| `manager_env.config.terrain_type` | trimesh | `sonic_release.yaml` | `plane` 为平地，`trimesh` 为粗糙地形。 |
| `manager_env.config.robot.type` | g1_model_12_dex | `sonic_release.yaml` | 机器人类型（必须与代码中的 `robot_mapping` 匹配）。 |

### 动作数据

| 参数 | 默认值 | 位置 | 说明 |
|-----------|---------|----------|-------------|
| `manager_env.commands.motion.motion_lib_cfg.motion_file` | — | `sonic_release.yaml` | 重定向到机器人的动作 PKL 文件路径。 |
| `manager_env.commands.motion.motion_lib_cfg.smpl_motion_file` | — | `sonic_release.yaml` | SMPL 动作 PKL 路径（或 `dummy`）。 |
| `manager_env.commands.motion.motion_lib_cfg.soma_motion_file` | — | `sonic_bones_seed.yaml` | SOMA 动作 PKL 路径（仅 4 编码器配置）。 |
| `manager_env.commands.motion.motion_lib_cfg.smpl_y_up` | true | `sonic_release.yaml` | 若 SMPL 数据使用 y 轴朝上坐标，则设为 `true`。 |
| `manager_env.commands.motion.motion_lib_cfg.target_fps` | 50 | `motion.yaml` | 动作重采样的目标 FPS。 |
| `manager_env.commands.motion.motion_lib_cfg.asset.assetFileName` | g1_29dof_rev_1_0.xml | `motion.yaml` | 动作库正运动学使用的 MJCF 文件。更换机器人时需修改。 |

### 动作指令（motion command）

| 参数 | 默认值 | 位置 | 说明 |
|-----------|---------|----------|-------------|
| `manager_env.commands.motion.num_future_frames` | 10 | `sonic_release.yaml` | 提供给策略的未来参考帧数量。 |
| `manager_env.commands.motion.dt_future_ref_frames` | 0.1 | `sonic_release.yaml` | 未来帧之间的时间间隔（秒）。 |
| `manager_env.commands.motion.cat_upper_body_poses` | true | `sonic_release.yaml` | 用不同片段的上半身动作增强下半身动作。 |
| `manager_env.commands.motion.cat_upper_body_poses_prob` | 0.5 | `sonic_release.yaml` | 每个回合进行上半身动作增强的概率。 |
| `manager_env.commands.motion.freeze_frame_aug` | true | `sonic_release.yaml` | 使用冻结（静止）参考帧进行增强。 |

### 观测历史

| 参数 | 默认值 | 位置 | 说明 |
|-----------|---------|----------|-------------|
| `actor_prop_history_length` | 10 | `sonic_release.yaml` | Actor 堆叠的过去本体感觉帧数。 |
| `actor_actions_history_length` | 10 | `sonic_release.yaml` | Actor 堆叠的过去动作帧数。 |
| `critic_prop_history_length` | 10 | `sonic_release.yaml` | 同上，用于 Critic。 |
| `critic_actions_history_length` | 10 | `sonic_release.yaml` | 同上，用于 Critic。 |

### 奖励权重

所有奖励项都有一个 `weight` 参数。正权重鼓励相应行为，负权重惩罚相应行为。`base_5point_local_feet_acc` 的默认权重：

| 奖励项 | 权重 | 说明 |
|-------------|--------|-------------|
| `tracking_anchor_pos` | 0.5 | 根节点位置跟踪 |
| `tracking_anchor_ori` | 0.5 | 根节点朝向跟踪 |
| `tracking_relative_body_pos` | 1.0 | 刚体位置跟踪（相对锚点） |
| `tracking_relative_body_ori` | 1.0 | 刚体朝向跟踪（相对锚点） |
| `tracking_body_linvel` | 1.0 | 刚体线速度跟踪 |
| `tracking_body_angvel` | 1.0 | 刚体角速度跟踪 |
| `tracking_vr_5point_local` | 2.0 | 五点（双腕 + 头 + 双脚）局部跟踪 |
| `action_rate_l2` | -0.1 | 使动作平滑（惩罚动作突变） |
| `joint_limit` | -10.0 | 保持关节在限位范围内 |
| `undesired_contacts` | -0.1 | 惩罚非脚部与地面的接触 |
| `anti_shake_ang_vel` | -0.005 | 惩罚腕部/头部抖动 |
| `feet_acc` | -2.5e-6 | 惩罚脚部加速度（使迈步平滑） |

每个奖励项还有一个控制高斯核锐度的 `std` 参数。`std` 越小 = 跟踪越严格（误差增大时奖励下降更快）。

覆盖示例：
```bash
++manager_env.rewards.tracking_anchor_pos.weight=2.0
++manager_env.rewards.tracking_anchor_pos.params.std=0.1
```

### 终止阈值

当跟踪误差超过阈值时，终止条件会提前结束回合。自适应变体使用课程学习，在训练过程中逐步收紧阈值：

| 终止条件 | 阈值 | 说明 |
|-------------|-----------|-------------|
| `anchor_pos` | 0.15 m | 根节点位置偏差 |
| `anchor_ori_full` | 0.2 rad | 根节点朝向偏差 |
| `ee_body_pos` | 0.15 m | 末端执行器位置偏差 |
| `foot_pos_xyz` | 0.2 m | 脚部位置偏差 |
| `motion_time_out` | — | 动作片段播完时回合结束 |

较宽松的阈值（较大的值）在训练初期更容易。自适应终止会随策略提升自动收紧。

### 自适应动作采样

动作库支持自适应采样——策略失败的动作会被更频繁地采样：

| 参数 | 默认值 | 说明 |
|-----------|---------|-------------|
| `adaptive_sampling.enable` | true | 启用自适应采样。 |
| `adaptive_sampling.bin_size` | 50 | 失败率统计的窗口大小。 |
| `adaptive_sampling.adp_samp_failure_rate_max_over_mean` | 200 | 最大/平均失败率比值上限。防止单个过难动作占据主导。 |

### 保存与日志

| 参数 | 默认值 | 位置 | 说明 |
|-----------|---------|----------|-------------|
| `algo.config.save_interval` | 500 | `ppo_im_phc.yaml` | 每 N 个迭代保存一次检查点。 |
| `algo.config.eval_frequency` | 500 | `ppo_im_phc.yaml` | 每 N 个迭代运行一次评估。 |
| `use_wandb` | false | `base.yaml` | 启用 Weights & Biases 日志。 |
| `base_dir` | logs_rl | `base.yaml` | 训练输出的根目录。 |

## 实验配置

| 配置 | 编码器 | 用途 |
|--------|----------|----------|
| `sonic_release` | G1, teleop, SMPL | 默认配置 — 与发布的检查点对应 |
| `sonic_v1_1` | G1, teleop, SMPL | SONIC v1.1，采用朝向归一化目标和腕部姿态增强 |
| `sonic_bones_seed` | G1, teleop, SMPL, SOMA | 使用 SOMA 骨架编码器的扩展训练 |
| `sonic_h2` | G1, teleop, SMPL | H2 机器人（31 自由度） |

## 常用配方

### 可视化调试训练运行

```bash
python gear_sonic/train_agent_trl.py +exp=... \
    num_envs=4 headless=False \
    algo.config.num_learning_iterations=10
```

### 用较低学习率微调

```bash
python gear_sonic/train_agent_trl.py +exp=... \
    +checkpoint=sonic_release/last.pt \
    ++algo.config.actor_learning_rate=5e-6 \
    ++algo.config.desired_kl=0.005
```

### 仅在平地上训练

```bash
python gear_sonic/train_agent_trl.py +exp=... \
    ++manager_env.config.terrain_type=plane
```

### 为较难动作放宽终止阈值

```bash
python gear_sonic/train_agent_trl.py +exp=... \
    ++manager_env.terminations.anchor_pos.params.threshold=0.3 \
    ++manager_env.terminations.ee_body_pos.params.threshold=0.3
```

### 提高跟踪精度

```bash
python gear_sonic/train_agent_trl.py +exp=... \
    ++manager_env.rewards.tracking_relative_body_pos.params.std=0.1 \
    ++manager_env.rewards.tracking_anchor_pos.params.std=0.1
```
