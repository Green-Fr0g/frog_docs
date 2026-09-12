# 下载模型检查点

预训练的 GEAR-SONIC 检查点（ONNX 格式）托管在 Hugging Face 上：

**[nvidia/GEAR-SONIC](https://huggingface.co/nvidia/GEAR-SONIC)**

## 快速下载

### 安装依赖

```bash
pip install huggingface_hub
```

### 运行下载脚本

在仓库根目录下执行：

```bash
# Deployment (ONNX models + planner → gear_sonic_deploy/)
python download_from_hf.py

# Low-latency teleoperation checkpoint (ONNX models + planner → gear_sonic_deploy/)
python download_from_hf.py --low-latency

# SONIC v1.1 checkpoint (ONNX models + planner → gear_sonic_deploy/)
python download_from_hf.py --sonic-v1-1

# Training (checkpoint + SMPL data → sonic_release/ + data/smpl_filtered/)
python download_from_hf.py --training

# Low-latency PyTorch checkpoint + config only
python download_from_hf.py --training --low-latency

# SONIC v1.1 PyTorch checkpoint + configs only
python download_from_hf.py --training --sonic-v1-1 --no-smpl

# Sample data only (1 walking sequence for quick testing)
python download_from_hf.py --sample

# Training checkpoint only (skip 30GB SMPL download)
python download_from_hf.py --training --no-smpl
```

该命令会将**最新**的策略编码器 + 解码器 + 运动学规划器下载到
`gear_sonic_deploy/`，并保持部署二进制程序所期望的目录结构。
每条命令都会先获取仓库级的 `config.json` 发布清单，并在下载模型文件之前
校验所选模型的目录结构。

---

## 选项

| 旗标 | 说明 |
|------|-------------|
| `--training` | 下载训练检查点 + SMPL 动作数据（~30 GB） |
| `--low-latency` | 下载低延迟遥操作检查点。用于部署时，ONNX 文件放到 `gear_sonic_deploy/policy/low_latency/`；配合 `--training` 时，PyTorch 检查点和配置放到 `low_latency/`。 |
| `--sonic-v1-1` | 下载 SONIC v1.1，它使用机器人朝向归一化的目标，并采用腕部姿态增强进行训练。部署文件放到 `gear_sonic_deploy/policy/sonic_v1_1/`；训练文件放到 `sonic_v1_1/`。 |
| `--sample` | 仅下载示例动作数据（~4 MB） |
| `--no-planner` | 跳过运动学规划器的下载 |
| `--no-smpl` | 配合 `--training` 使用时，跳过 SMPL 数据（仅下载检查点） |
| `--output-dir PATH` | 覆盖目标下载目录 |
| `--token TOKEN` | HF token（`hf auth login` 的替代方式） |

### 示例

```bash
# Policy + planner (default)
python download_from_hf.py

# Policy only
python download_from_hf.py --no-planner

# Low-latency teleoperation policy only
python download_from_hf.py --low-latency --no-planner

# SONIC v1.1 policy only
python download_from_hf.py --sonic-v1-1 --no-planner

# Download into a custom directory
python download_from_hf.py --output-dir /data/gear-sonic
```

---

## 低延迟遥操作检查点

发布在 [`nvidia/GEAR-SONIC`](https://huggingface.co/nvidia/GEAR-SONIC) 仓库
`low_latency/` 目录下的检查点，专为响应迅速的全身遥操作而配置。其 SMPL
编码器使用 **4 帧未来参考动作帧**，而默认发布版本使用 **10 帧**。在
50 Hz（每帧 20 ms）下，这将把 SMPL 参考前瞻从约 **200 ms 缩短到 80 ms**。

这是控制器自身的参考前瞻，并非端到端系统总延迟的实测值。该检查点不会
取代默认的顶层部署策略。

下载部署用 ONNX 文件：

```bash
python download_from_hf.py --low-latency
```

这将生成：

```
gear_sonic_deploy/
└── policy/low_latency/
    ├── model_encoder.onnx
    ├── model_decoder.onnx
    └── observation_config.yaml
```

### C++ 部署推理

在仿真中运行低延迟 ONNX 控制器：

```bash
cd gear_sonic_deploy
./deploy.sh \
    --cp policy/low_latency/model \
    --obs-config policy/low_latency/observation_config.yaml \
    sim
```

在真机上运行 VLA 或遥操作：

```bash
cd gear_sonic_deploy
./deploy.sh \
    --cp policy/low_latency/model \
    --obs-config policy/low_latency/observation_config.yaml \
    --input-type zmq_manager \
    real
```

`deploy.sh` 要求 `--cp` 为共享的模型文件名前缀，它会在内部自动拼接
`_encoder.onnx` 和 `_decoder.onnx`。低延迟 PyTorch 检查点为
`low_latency/last.pt`：

```bash
python download_from_hf.py --training --low-latency
```

### Python 推理与评估

若要在 Isaac Lab 中进行 Python 侧的检查点评估，请下载 PyTorch
检查点和示例动作：

```bash
python download_from_hf.py --training --low-latency
python download_from_hf.py --sample
```

然后用 `eval_agent_trl.py` 运行低延迟检查点：

```bash
python gear_sonic/eval_agent_trl.py \
    +checkpoint=low_latency/last.pt \
    +headless=False \
    ++num_envs=1 \
    ++manager_env.observations.policy.enable_corruption=False \
    ++manager_env.observations.tokenizer.enable_corruption=False \
    "++manager_env.commands.motion.motion_lib_cfg.motion_file=sample_data/robot_filtered" \
    "++manager_env.commands.motion.motion_lib_cfg.smpl_motion_file=sample_data/smpl_filtered"
```

对于 Python VLA tmux 启动器，可通过启动器旗标传入相同的低延迟 C++ 部署文件：

```bash
python gear_sonic/scripts/launch_inference.py \
    --deploy-checkpoint policy/low_latency/model \
    --deploy-obs-config policy/low_latency/observation_config.yaml \
    --camera-host 192.168.123.164 \
    --prompt "pick up the cup"
```

该启动器仍然通过 C++ 部署面板运行 ONNX 控制器；Python 进程负责协调
VLA 客户端、相机客户端、键盘控制以及可选的数据导出器。

---

## SONIC v1.1 检查点

`sonic_v1_1/` 目录下的检查点使用机器人朝向归一化的目标朝向，并在训练时
采用了腕部姿态增强。它面向朝向稳定的全身遥操作，以及针对该控制器训练的
SONIC 后端 VLA 策略。

其 SMPL 和腕部编码器使用 **20 ms 间隔的 10 个未来帧**
（约 **200 ms** 的参考前瞻）。G1 与遥操作参考使用 `step5` 间隔的 10 帧。
这不是低延迟检查点。

下载配套的 ONNX 编码器、解码器、观测配置和规划器：

```bash
python download_from_hf.py --sonic-v1-1
```

这将生成：

```
gear_sonic_deploy/
└── policy/sonic_v1_1/
    ├── model_encoder.onnx
    ├── model_decoder.onnx
    └── observation_config.yaml
```

在仿真中运行该控制器：

```bash
cd gear_sonic_deploy
./deploy.sh \
    --cp policy/sonic_v1_1/model \
    --obs-config policy/sonic_v1_1/observation_config.yaml \
    --motor-kp-scale 4,10=1.5 \
    --motor-kd-scale 4,10=1.5 \
    sim
```

上述增益设置是经过实测验证的 v1.1 硬件调参。索引 `4` 和 `10` 对应左、右
踝关节俯仰电机；这一调整可改善全身稳定性以及实测的腕部跟踪效果。它们
保持显式写出，是为了让其他模型变体保留各自的原始增益。

对于 VLA 启动器：

```bash
python gear_sonic/scripts/launch_inference.py \
    --deploy-checkpoint policy/sonic_v1_1/model \
    --deploy-obs-config policy/sonic_v1_1/observation_config.yaml \
    --deploy-motor-kp-scale 4,10=1.5 \
    --deploy-motor-kd-scale 4,10=1.5 \
    --camera-host 192.168.123.164 \
    --prompt "pick up the cup"
```

下载 PyTorch 检查点和配置、但跳过 30 GB 的共享 SMPL 数据集：

```bash
python download_from_hf.py --training --sonic-v1-1 --no-smpl
```

使用配套的发布版本配方进行评估：

```bash
python gear_sonic/eval_agent_trl.py \
    +exp=manager/universal_token/all_modes/sonic_v1_1 \
    +checkpoint=sonic_v1_1/last.pt \
    +headless=False \
    ++num_envs=1 \
    ++manager_env.observations.policy.enable_corruption=False \
    ++manager_env.observations.tokenizer.enable_corruption=False
```

继续训练时，请将相同的 `+exp` 和 `+checkpoint` 取值用于 `train_agent_trl.py`。

---

## 通过 CLI 手动下载

如果你偏好使用 Hugging Face CLI：

```bash
pip install huggingface_hub[cli]

# Policy only
hf download nvidia/GEAR-SONIC \
    config.json \
    model_encoder.onnx \
    model_decoder.onnx \
    observation_config.yaml \
    --local-dir gear_sonic_deploy

# Everything (policy + planner)
hf download nvidia/GEAR-SONIC --local-dir gear_sonic_deploy
```

---

## 通过 Python 手动下载

```python
from huggingface_hub import hf_hub_download

REPO_ID = "nvidia/GEAR-SONIC"

manifest = hf_hub_download(repo_id=REPO_ID, filename="config.json")
encoder = hf_hub_download(repo_id=REPO_ID, filename="model_encoder.onnx")
decoder = hf_hub_download(repo_id=REPO_ID, filename="model_decoder.onnx")
obs_config = hf_hub_download(repo_id=REPO_ID, filename="observation_config.yaml")
planner = hf_hub_download(repo_id=REPO_ID, filename="planner_sonic.onnx")

print("Release manifest:", manifest)
print("Policy encoder :", encoder)
print("Policy decoder :", decoder)
print("Obs config     :", obs_config)
print("Planner        :", planner)
```

---

## SONIC 训练检查点

SONIC 发布的训练检查点和配置同样可在 Hugging Face 上获取，用于评估或微调：

### 通过 CLI 下载

```bash
hf download nvidia/GEAR-SONIC \
    config.json \
    sonic_release/last.pt \
    sonic_release/config.yaml \
    --local-dir models
```

### 通过 Python 下载

```python
from huggingface_hub import hf_hub_download

REPO_ID = "nvidia/GEAR-SONIC"

manifest = hf_hub_download(repo_id=REPO_ID, filename="config.json")
checkpoint = hf_hub_download(repo_id=REPO_ID, filename="sonic_release/last.pt")
training_config = hf_hub_download(repo_id=REPO_ID, filename="sonic_release/config.yaml")

print("Manifest   :", manifest)
print("Checkpoint :", checkpoint)
print("Config     :", training_config)
```

### 评估检查点

```bash
python gear_sonic/eval_agent_trl.py \
    +checkpoint=models/sonic_release/last.pt \
    +num_envs=1 headless=False
```

---

## 示例动作数据（快速上手）

我们提供了一个小型示例数据集（1 条行走序列），无需下载完整的 Bones-SEED
数据集即可快速测试。它包含训练所需的全部三种数据类型：机器人重定向数据、
SOMA 骨骼数据和 SMPL 数据。

### 通过 CLI 下载

```bash
# Sample data only
hf download nvidia/GEAR-SONIC \
    --include "config.json" \
    --include "sample_data/*" \
    --local-dir .

# Sample data + training checkpoint
hf download nvidia/GEAR-SONIC \
    --include "config.json" \
    --include "sample_data/*" \
    --include "sonic_release/*" \
    --local-dir .
```

这将生成：

```
sample_data/
├── robot_filtered/210531/    # G1 retargeted motion (for motion tracking)
│   ├── walk_forward_amateur_001__A001.pkl
│   └── walk_forward_amateur_001__A001_M.pkl
├── soma_filtered/210531/     # SOMA skeleton motion
│   ├── walk_forward_amateur_001__A001.pkl
│   └── walk_forward_amateur_001__A001_M.pkl
└── smpl_filtered/            # SMPL human motion
    ├── walk_forward_amateur_001__A001.pkl
    └── walk_forward_amateur_001__A001_M.pkl
```

### 用示例数据测试训练

```bash
python gear_sonic/train_agent_trl.py \
    +exp=manager/universal_token/all_modes/sonic_release \
    num_envs=16 headless=True \
    manager_env.commands.motion.motion_lib_cfg.motion_file=sample_data/robot_filtered \
    manager_env.commands.motion.motion_lib_cfg.smpl_motion_file=sample_data/smpl_filtered
```

如需完整规模训练，请下载完整的 [Bones-SEED](https://huggingface.co/datasets/bones-studio/seed)
数据集，并按照[训练指南](../user_guide/training.md)操作。

---

## SMPL 动作数据（Bones-SEED 过滤版）

训练所用的 SMPL 重定向动作数据（131K 条序列，从 Bones-SEED 数据集过滤而来）
以分卷 tar 压缩包形式提供（总计约 30GB）。

### 下载与解压

```bash
# Download all parts
hf download nvidia/GEAR-SONIC \
    --include "config.json" \
    --include "bones_seed_smpl/*" \
    --local-dir .

# Reassemble and extract
cat bones_seed_smpl/bones_seed_smpl.tar.part_* | tar xf - -C data/
```

解压后得到 `data/smpl_filtered/`，其中包含 131K 个 `.pkl` 文件。

然后让训练指向该目录：

```bash
python gear_sonic/train_agent_trl.py \
    +exp=manager/universal_token/all_modes/sonic_release \
    +checkpoint=sonic_release/last.pt \
    num_envs=4096 headless=True \
    ++manager_env.commands.motion.motion_lib_cfg.smpl_motion_file=data/smpl_filtered
```

---

## 可用文件

```
nvidia/GEAR-SONIC/
├── config.json                       # Release manifest and model layout
├── model_encoder.onnx                # Policy encoder (ONNX, for deployment)
├── model_decoder.onnx                # Policy decoder (ONNX, for deployment)
├── observation_config.yaml           # Observation configuration (deployment)
├── planner_sonic.onnx                # Kinematic planner (ONNX)
├── low_latency/
│   ├── model_encoder.onnx            # Low-latency policy encoder (ONNX)
│   ├── model_decoder.onnx            # Low-latency policy decoder (ONNX)
│   ├── observation_config.yaml       # Low-latency observation configuration
│   ├── last.pt                       # Low-latency training checkpoint
│   ├── config.yaml                   # Low-latency training config
│   └── model_config.yaml             # Low-latency model config
├── sonic_v1_1/
│   ├── model_encoder.onnx            # SONIC v1.1 policy encoder (ONNX)
│   ├── model_decoder.onnx            # SONIC v1.1 policy decoder (ONNX)
│   ├── observation_config.yaml       # Matching deployment observations
│   ├── last.pt                       # SONIC v1.1 training checkpoint
│   ├── config.yaml                   # Resolved training config
│   └── model_config.yaml             # Model architecture config
├── bones_seed_smpl/                  # SMPL motion data (131K sequences, ~30GB split tar)
│   ├── bones_seed_smpl.tar.part_aa
│   ├── ...
│   └── bones_seed_smpl.tar.part_ag
├── sonic_release/
│   ├── last.pt                       # Training checkpoint (for eval/fine-tuning)
│   └── config.yaml                   # Training config
└── sample_data/                      # Sample motion data (1 walking sequence)
    ├── robot_filtered/               # G1 retargeted motion
    ├── soma_filtered/                # SOMA skeleton motion
    └── smpl_filtered/                # SMPL human motion
```

下载脚本会将部署文件放置到部署二进制程序所期望的目录结构中：

```
gear_sonic_deploy/
├── policy/release/
│   ├── model_encoder.onnx
│   ├── model_decoder.onnx
│   └── observation_config.yaml
├── policy/low_latency/
│   ├── model_encoder.onnx
│   ├── model_decoder.onnx
│   └── observation_config.yaml
├── policy/sonic_v1_1/
│   ├── model_encoder.onnx
│   ├── model_decoder.onnx
│   └── observation_config.yaml
└── planner/target_vel/V2/
    └── planner_sonic.onnx
```

---

## 身份验证

该仓库是**公开的**——下载无需 token。

如果遇到速率限制，或需要访问私有 fork：

```bash
# Option 1: CLI login (recommended — token is saved once)
hf login

# Option 2: environment variable
export HF_TOKEN="hf_..."
python download_from_hf.py

# Option 3: pass token directly
python download_from_hf.py --token hf_...
```

可在 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 免费获取 token。

---

## 后续步骤

下载完成后，请按照[快速上手](quickstart.md)指南在 MuJoCo 仿真或真实硬件上
运行部署栈。
