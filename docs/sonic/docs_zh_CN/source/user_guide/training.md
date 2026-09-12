# 训练指南

本指南介绍 SONIC 全身控制器的数据处理、训练、评估与 ONNX 导出。

## 概览

SONIC 采用通用 token 架构，通过模仿人体动作捕捉数据来控制人形机器人（Unitree G1，29 自由度）。多个并行编码器接受不同的动作输入格式：

- **G1**：机器人关节轨迹
- **Teleop**：VR 三点跟踪目标（头部 + 双腕）
- **SMPL**：参数化人体模型的关节位置
- **SOMA**：由 BVH 得到的骨架关节位置（可选的第 4 个编码器）

所有编码器通过 FSQ（有限标量量化）投影到共享的潜在 token 空间，而单个解码器无论输入何种模态都输出关节动作。训练在 Isaac Lab 仿真中使用 PPO 加辅助损失。

| 配置 | 编码器 | 用途 |
|--------|----------|----------|
| `sonic_release` | G1, teleop, SMPL | **默认** — 与发布的检查点对应 |
| `sonic_v1_1` | G1, teleop, SMPL | SONIC v1.1，采用朝向归一化目标和腕部姿态增强 |
| `sonic_bones_seed` | G1, teleop, SMPL, SOMA | 使用 SOMA 骨架编码器的扩展训练 |

微调与评估请使用 `sonic_release`。`sonic_bones_seed` 配置增加了第四个 SOMA 编码器（参见[使用 SOMA 编码器训练](#training-with-soma-encoder)）。使用 `sonic_v1_1` 时请配合 `sonic_v1_1/last.pt`。

## 数据处理

### 第 1 步：转换动作数据

SONIC 要求动作数据为 **motion_lib PKL 格式**。转换 Bones-SEED CSV 文件：

```bash
python gear_sonic/data_process/convert_soma_csv_to_motion_lib.py \
    --input /path/to/bones_seed/g1/csv/ \
    --output data/motion_lib_bones_seed/robot \
    --fps 30 \
    --fps_source 120 \
    --individual \
    --num_workers 16
```

### 第 2 步：筛选动作

移除 G1 机器人无法完成的动作（家具交互、车辆、杂技、高处表面）：

```bash
python gear_sonic/data_process/filter_and_copy_bones_data.py \
    --source data/motion_lib_bones_seed/robot \
    --dest data/motion_lib_bones_seed/robot_filtered \
    --workers 16
```

此操作会移除约 8.7% 的动作（142K 中保留约 130K）。可用 `--dry-run` 预览，或用 `--add-keywords` 添加自定义过滤规则。

### 数据布局

将处理后的数据放在仓库根目录：

```
<repo_root>/
├── data/motion_lib_bones_seed/
│   ├── robot/              # 完整动作库（142K 个 PKL）
│   └── robot_filtered/     # 过滤后的子集（~130K 个 PKL）
└── gear_sonic/
```

## 训练

### 基本命令

```bash
python gear_sonic/train_agent_trl.py \
    +exp=manager/universal_token/all_modes/sonic_release \
    num_envs=4096 headless=True \
    ++manager_env.commands.motion.motion_lib_cfg.motion_file=<path/to/robot_filtered> \
    ++manager_env.commands.motion.motion_lib_cfg.smpl_motion_file=<path/to/smpl_filtered>
```

例如，使用来自 Hugging Face 的示例数据：

```bash
python gear_sonic/train_agent_trl.py \
    +exp=manager/universal_token/all_modes/sonic_release \
    num_envs=16 headless=True \
    ++manager_env.commands.motion.motion_lib_cfg.motion_file=sample_data/robot_filtered \
    ++manager_env.commands.motion.motion_lib_cfg.smpl_motion_file=sample_data/smpl_filtered
```

或使用完整数据集：

```bash
python gear_sonic/train_agent_trl.py \
    +exp=manager/universal_token/all_modes/sonic_release \
    num_envs=4096 headless=True \
    ++manager_env.commands.motion.motion_lib_cfg.motion_file=data/motion_lib_bones_seed/robot_filtered \
    ++manager_env.commands.motion.motion_lib_cfg.smpl_motion_file=data/smpl_filtered
```

### 从发布的检查点微调

```bash
python gear_sonic/train_agent_trl.py \
    +exp=manager/universal_token/all_modes/sonic_release \
    +checkpoint=sonic_release/last.pt \
    num_envs=4096 headless=True \
    ++manager_env.commands.motion.motion_lib_cfg.motion_file=<path/to/robot_filtered> \
    ++manager_env.commands.motion.motion_lib_cfg.smpl_motion_file=<path/to/smpl_filtered>
```

### 自适应采样的失败归因

自适应采样默认启用。在 Isaac Lab 重新采样环境之前，发生终止的环境会被记到它在物理步进期间所跟踪的动作 ID 和帧区间上。这可以避免把失败错误地归因到新抽取的动作。

迭代几百次之后，`adp_samp/failure_rate_max` 应当与 `adp_samp/failure_rate_mean` 分离开来；若两者几乎保持一致，则强烈说明失败仍被归因到重置之后的动作。

### 多 GPU 与多节点训练

建议使用 **64 块以上 GPU** 训练，以获得合理的收敛时间。单节点（8 GPU）训练可行，但会明显更慢。

```bash
# 单节点（8 GPU）
accelerate launch --num_processes=8 gear_sonic/train_agent_trl.py \
    +exp=manager/universal_token/all_modes/sonic_release \
    num_envs=4096 headless=True

# 多节点 — 使用 accelerate config 配置分布式
accelerate launch \
    --multi_gpu \
    --num_machines=8 \
    --num_processes=64 \
    --machine_rank=$MACHINE_RANK \
    --main_process_ip=$MASTER_ADDR \
    --main_process_port=$MASTER_PORT \
    gear_sonic/train_agent_trl.py \
    +exp=manager/universal_token/all_modes/sonic_release \
    num_envs=4096 headless=True
```

多节点配置请参阅 [Accelerate 分布式训练指南](https://huggingface.co/docs/accelerate/usage_guides/deepspeed)与[多节点启动器文档](https://huggingface.co/docs/accelerate/package_reference/cli#accelerate-launch)。

### W&B 日志

默认启用。关键覆盖项：

```bash
WANDB_MODE=offline python gear_sonic/train_agent_trl.py ...   # 离线模式
    wandb.wandb_project=my_project wandb.wandb_entity=my_team  # 自定义项目
    use_wandb=false                                             # 完全禁用
```

### 本地调试运行

```bash
python gear_sonic/train_agent_trl.py \
    +exp=manager/universal_token/all_modes/sonic_release \
    num_envs=16 headless=False \
    ++algo.config.num_learning_iterations=100
```

## 监控

### 关键指标

| 指标 | 良好范围 | 说明 |
|--------|-----------|-------------|
| `rewards/total` | 3.0+ | 总奖励 |
| `rewards/anchor_pos_err` | < 0.15 | 根节点位置跟踪误差（m） |
| `rewards/body_pos_err` | < 0.10 | 刚体位置跟踪误差（m） |
| `throughput/fps` | ~4000+ | 训练吞吐量 |

### 检查点

每 2000 步保存一次，路径为：

```
logs_rl/TRL_G1_Track/<experiment_name>-<timestamp>/
├── model_step_002000.pt
├── config.yaml
└── ...
```

## 评估

### 可视化参考动作

训练前先回放动作以验证数据质量：

```bash
python gear_sonic/train_agent_trl.py \
    +exp=manager/universal_token/all_modes/sonic_release \
    ++replay=True num_envs=4 headless=False
```

### 评估检查点

两种评估模式：**metrics**（指标：成功率、MPJPE）与 **render**（渲染：视频输出）。

对于发布的检查点，必须覆盖动作路径，因为其 `config.yaml` 中包含内部训练路径。对于你自己用 `sonic_release` 训练的检查点，可省略动作路径覆盖。

```bash
# --- 指标评估 ---
python gear_sonic/eval_agent_trl.py \
    +checkpoint=<path_to_checkpoint.pt> \
    +headless=True \
    ++eval_callbacks=im_eval \
    ++run_eval_loop=False \
    ++num_envs=128 \
    "+manager_env/terminations=tracking/eval" \
    "++manager_env.commands.motion.motion_lib_cfg.max_unique_motions=512"
```

```bash
# --- 渲染视频 ---
python gear_sonic/eval_agent_trl.py \
    +checkpoint=<path_to_checkpoint.pt> \
    +headless=True \
    ++eval_callbacks=im_eval \
    ++run_eval_loop=False \
    ++num_envs=8 \
    ++manager_env.config.render_results=True \
    "++manager_env.config.save_rendering_dir=/tmp/renders" \
    ++manager_env.config.env_spacing=10.0 \
    "~manager_env/recorders=empty" "+manager_env/recorders=render"
```

仅对**发布的检查点**，在任一命令后追加以下覆盖项（其内嵌配置包含内部训练路径）：

```bash
    "++manager_env.commands.motion.motion_lib_cfg.motion_file=data/motion_lib_bones_seed/robot_filtered"
```

视频以 `000000.mp4`、`000001.mp4` 等文件名保存在 `save_rendering_dir` 中。

### 预期评估指标

*训练奖励*（W&B `Episode_Reward/`）：

| 指标 | 收敛值 | 说明 |
|--------|-----------|-------------|
| `tracking_vr_5point_local` | > 0.80 | 五点跟踪质量 |
| `tracking_relative_body_pos` | > 0.44 | 上半身位置跟踪 |
| `tracking_anchor_pos` | > 0.14 | 根节点位置跟踪 |
| `time_out` | > 0.90 | 回合完成率 |

*评估指标*（来自 `eval_agent_trl.py`）：

| 指标 | 收敛值 | 说明 |
|--------|-----------|-------------|
| `success_rate` | > 0.97 | 未被提前终止而完成跟踪的动作比例 |
| `mpjpe_l` | < 30 mm | 局部每关节位置误差 |
| `mpjpe_g` | < 200 mm | 全局每关节位置误差 |

收敛良好的策略在 100K 次迭代后可达到 >0.98 的成功率和 <29 mm 的 mpjpe_l。

## ONNX 导出

将训练好的检查点导出为 ONNX 以供 C++ 部署：

```bash
python gear_sonic/eval_agent_trl.py \
    +checkpoint=<path_to_checkpoint.pt> \
    +headless=True ++num_envs=1 \
    +export_onnx_only=true
```

对于发布的检查点，请追加上面评估一节所示的动作路径覆盖项。

输出（位于检查点旁的 `exported/` 目录）：

| 文件 | 说明 |
|------|-------------|
| `*_smpl.onnx` | SMPL 编码器 + 解码器（姿态估计输入） |
| `*_g1.onnx` | G1 编码器 + 解码器（机器人关节输入） |
| `*_teleop.onnx` | Teleop 编码器 + 解码器（VR 跟踪输入） |
| `*_encoder.onnx` | 全部编码器合并 |
| `*_decoder.onnx` | 仅解码器 |

请使用与你的输入模态匹配的编码器+解码器组合。C++ 细节参见[部署代码参考](../references/deployment_code.md)。

(training-with-soma-encoder)=

## 使用 SOMA 编码器训练

`sonic_bones_seed` 配置增加了第四个 SOMA 编码器，用于由 BVH 得到的骨架关节位置。

### SOMA 数据准备

```bash
# 从 BVH 提取 SOMA 关节
python gear_sonic/data_process/extract_soma_joints_from_bvh.py \
    --input /path/to/bones_seed/bvh/ \
    --output data/motion_lib_bones_seed/soma \
    --fps 30 --num_workers 16 --skip_existing

# 过滤以与机器人数据保持一致
python gear_sonic/data_process/filter_and_copy_bones_data.py \
    --source data/motion_lib_bones_seed/soma \
    --dest data/motion_lib_bones_seed/soma_filtered \
    --workers 16
```

### 训练

请使用多节点训练（推荐 64 块以上 GPU）：

```bash
accelerate launch \
    --multi_gpu --num_machines=8 --num_processes=64 \
    --machine_rank=$MACHINE_RANK \
    --main_process_ip=$MASTER_ADDR \
    --main_process_port=$MASTER_PORT \
    gear_sonic/train_agent_trl.py \
    +exp=manager/universal_token/all_modes/sonic_bones_seed \
    num_envs=4096 headless=True \
    ++manager_env.commands.motion.motion_lib_cfg.motion_file=data/motion_lib_bones_seed/robot_filtered \
    ++manager_env.commands.motion.motion_lib_cfg.smpl_motion_file=data/smpl_filtered \
    ++manager_env.commands.motion.motion_lib_cfg.soma_motion_file=data/motion_lib_bones_seed/soma_filtered
```

4 编码器训练的数据布局：

```
data/
├── motion_lib_bones_seed/
│   ├── robot_filtered/     # ~130K 个 PKL（G1 重定向）
│   └── soma_filtered/      # ~130K 个 PKL（SOMA 骨架）
└── smpl_filtered/          # ~131K 个 PKL（SMPL 人体）
```
