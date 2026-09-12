# 安装（训练）

本指南介绍如何搭建面向人形机器人全身控制的 SONIC 训练环境。

## 前提条件

- **GPU**：支持 CUDA 12.x 的 NVIDIA GPU（推荐 L40）
- **操作系统**：Ubuntu 22.04+
- **Python**：3.11（Isaac Lab 要求；sim/teleop/deploy 脚本可在 3.10+ 上运行）
- **Isaac Lab**：2.3+（仿真环境必需）

## 安装 Isaac Lab

SONIC 训练使用 Isaac Lab 进行物理仿真。请按照官方
[Isaac Lab 安装指南](https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html)
安装 Isaac Lab。

安装完成后，请验证：

```bash
python -c "import isaaclab; print(isaaclab.__version__)"
```

## 安装 gear_sonic（训练）

在仓库根目录下执行：

```bash
pip install -e "gear_sonic/[training]"
```

这会在 Isaac Lab 环境的基础上安装训练依赖（Hydra、W&B、HuggingFace TRL 等）。

## 从 Hugging Face 下载模型与数据

SONIC 模型检查点和 SMPL 动作数据托管在
[Hugging Face](https://huggingface.co/nvidia/GEAR-SONIC) 上。

```bash
pip install huggingface_hub
python download_from_hf.py --training
```

下载内容包括：

- 用于微调的 **PyTorch 检查点**（`sonic_release/last.pt`）
- 供 SMPL 编码器使用的 **SMPL 动作数据**（`data/smpl_filtered/`）

## 准备机器人动作数据

SONIC 在 [Bones-SEED](https://huggingface.co/datasets/bones-studio/seed) 动作捕捉数据集上训练
（142K+ 条已重定向到 Unitree G1 的动作序列）。

### 第 1 步：下载并转换

从 [HuggingFace 上的 Bones-SEED](https://huggingface.co/datasets/bones-studio/seed) 下载 **G1 重定向后的 CSV**
（29 自由度，120 FPS），然后进行转换：

```bash
python gear_sonic/data_process/convert_soma_csv_to_motion_lib.py \
    --input /path/to/bones_seed/g1/csv/ \
    --output data/motion_lib_bones_seed/robot \
    --fps 30 --fps_source 120 --individual --num_workers 16
```

### 第 2 步：过滤动作

删除 G1 机器人无法执行的动作：

```bash
python gear_sonic/data_process/filter_and_copy_bones_data.py \
    --source data/motion_lib_bones_seed/robot \
    --dest data/motion_lib_bones_seed/robot_filtered --workers 16
```

这一步会删除约 8.7% 的动作（142K 中约保留 130K）。详见
[训练指南](../user_guide/training.md)。

你的数据目录应如下所示：

```
<repo_root>/
├── data/
│   ├── motion_lib_bones_seed/
│   │   └── robot_filtered/     # Filtered G1 motions (~130K PKLs)
│   └── smpl_filtered/           # SMPL motion data (from Hugging Face)
└── sonic_release/               # Released checkpoint (from Hugging Face)
```

> **Note**: 数据处理脚本（`gear_sonic/data_process/`）**不需要**
> Isaac Lab，只需 `pip install -e gear_sonic/` 即可在任何机器上运行。

## 验证安装

首先运行预检脚本，验证所有依赖：

```bash
python check_environment.py --training
```

然后用少量并行环境运行一次快速冒烟测试：

```bash
# Interactive (with viewer)
python gear_sonic/train_agent_trl.py \
    +exp=manager/universal_token/all_modes/sonic_release \
    num_envs=16 headless=False \
    ++algo.config.num_learning_iterations=5

# Headless (server / no display)
python gear_sonic/train_agent_trl.py \
    +exp=manager/universal_token/all_modes/sonic_release \
    num_envs=16 headless=True \
    ++algo.config.num_learning_iterations=5
```

经过约一分钟的初始化后，你应该能在控制台看到训练指标（奖励、误差）持续输出。

## 完整训练

安装验证通过后，请参阅[训练指南](../user_guide/training.md)了解完整训练命令
（推荐 64+ GPU）、评估、ONNX 导出以及 SOMA 编码器的配置。
