# VLA 工作流：采集、微调、部署

本教程介绍在配备 SONIC 全身控制的 Unitree G1 上训练并部署视觉-语言-动作（VLA）策略的端到端工作流：

1. 使用 SONIC 技术栈**采集**遥操作示教数据
2. 在采集的数据上对 Isaac-GR00T N1.7 模型进行**微调**
3. **部署**微调后的策略，进行自主推理

```text
+-----------------+     +-----------------+     +-----------------+
| 1. Collect      |     | 2. Fine-tune    |     | 3. Deploy       |
| VR teleop +     | --> | Isaac-GR00T     | --> | PolicyServer +  |
| data export     |     | N1.7            |     | SONIC           |
+-----------------+     +-----------------+     +-----------------+
```

想了解用该工作流完成的全身操作任务示例，参见 [GEAR-SONIC 项目页面上的 VLA 结果视频](https://nvlabs.github.io/GEAR-SONIC/#connection-to-vla-foundation-model)。

## 工作原理：SONIC 潜在动作

VLA 不直接预测原始关节角度，而是预测 **SONIC 潜在运动 token**——一种由 SONIC 全身控制器学到的紧凑的 64 维表示。SONIC 随后将这些潜向量解码为 50 Hz 的全身关节指令。

```text
+-------------+   latent tokens   +-------------+   joint commands   +-------+
| VLA Model   | ----------------> | SONIC       | -----------------> | Robot |
| 2.5 Hz      |   64-dim x 40     | Decoder     |   50 Hz            |       |
|             |                   | C++         |                    |       |
+-------------+                   +-------------+                    +-------+
```

这意味着 VLA 只需推理*做什么*——*怎么做*由 SONIC 负责：平衡、移动与流畅的全身协调都由预训练控制器直接提供。最终得到的系统可以同时行走、伸手、抓握和操作。

每个推理步的完整动作空间为 78 维：64 维运动 token + 7 维左手关节 + 7 维右手关节。

## 步骤 1：数据采集

使用 VR 全身遥操作采集遥操作示教数据。数据导出器会把机器人状态、相机图像和遥操作动作记录为 LeRobot 数据集。

完整的搭建说明（相机服务器、VR 遥操作、录制控制）参见[数据采集教程](data_collection.md)。

**快速开始：**

```bash
python gear_sonic/scripts/launch_data_collection.py \
    --camera-host 192.168.123.164 \
    --task-prompt "pick up the soda can and place it in the bin"
```

**输出：** 一个 LeRobot v2.1 数据集目录，例如：

```text
outputs/2026-04-03-14-30-00-G1-robot01/
+-- data/
|   +-- train-00000.parquet
+-- videos/
|   +-- observation.images.ego_view/
|       +-- episode_000000.mp4
+-- meta/
    +-- info.json
    +-- modality.json
    +-- episodes.jsonl
    +-- tasks.jsonl
```

```{tip}
为获得可靠的微调效果，目标任务至少要采集 50–100 条示教数据。用 `--dataset-name` 可把多次会话追加到同一数据集中，或之后用 `process_dataset.py` 合并各次会话。
```

### 微调前的后处理

采集完成后，运行处理脚本删除已丢弃的回合（录制时用 `x` 键标记为待删除）并清理过期的 SMPL 帧：

```bash
source .venv_data_collection/bin/activate
python gear_sonic/scripts/process_dataset.py \
    --dataset-path outputs/2026-04-03-14-30-00-G1-robot01 \
    --output-path outputs/my_task_cleaned
```

这样可确保只有成功的示教数据用于微调。

## 步骤 2：使用 Isaac-GR00T 微调

使用 [Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T) 训练流水线，在你采集的数据集上微调 GR00T N1.7 基座模型。

### 先决条件

- 克隆并安装 [Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T)：
  ```bash
  git clone https://github.com/NVIDIA/Isaac-GR00T.git
  cd Isaac-GR00T
  uv sync --all-extras
  ```
- 多 GPU 机器（建议 4 张以上 GPU）
- 训练机器可访问你采集的数据集

### 启动微调

```bash
export NUM_GPUS=4
uv run python \
    gr00t/experiment/launch_finetune.py \
    --base-model-path nvidia/GR00T-N1.7-3B \
    --dataset-path /path/to/your/collected_dataset \
    --embodiment-tag UNITREE_G1_SONIC \
    --modality-config-path gr00t/configs/data/embodiment_configs.py \
    --num-gpus $NUM_GPUS \
    --output-dir /path/to/output \
    --save-total-limit 5 \
    --save-steps 5000 \
    --max-steps 20000 \
    --use-wandb \
    --global-batch-size 32 \
    --color-jitter-params brightness 0.3 contrast 0.4 saturation 0.5 hue 0.08 \
    --dataloader-num-workers 4
```

### 关键参数

| 旗标 | 描述 |
|------|-------------|
| `--base-model-path` | HuggingFace 模型 ID 或预训练权重的本地路径 |
| `--dataset-path` | 步骤 1 中 LeRobot 数据集的路径 |
| `--embodiment-tag` | 必须与数据集的具身类型匹配（`UNITREE_G1_SONIC`） |
| `--modality-config-path` | 定义模态配置的 Python 文件 |
| `--num-gpus` | 用于分布式训练的 GPU 数量 |
| `--max-steps` | 总训练步数（2 万步是不错的起点） |
| `--global-batch-size` | 所有 GPU 的总批大小 |
| `--save-steps` | 检查点保存间隔 |
| `--use-wandb` | 启用 Weights & Biases 日志记录 |

### 监控

使用 `--use-wandb` 时，训练指标（损失、学习率等）会记录到你的 W&B 项目中。请关注训练损失曲线——它应平稳下降，并在 `--max-steps` 之前趋于平稳。

### 输出

检查点保存在 `--output-dir`：

```text
/path/to/output/
+-- checkpoint-5000/
+-- checkpoint-10000/
+-- checkpoint-15000/
+-- checkpoint-20000/
+-- config.json
+-- processor_config.json
```

使用最终的检查点（或根据你的评估表现最好的那个）进行步骤 3 的部署。

## 步骤 3：部署推理

使用 Isaac-GR00T PolicyServer 与 SONIC 推理栈部署微调后的模型。推理流水线、键盘控制与配置的完整细节参见[VLA 推理教程](vla_inference.md)。

### 启动 PolicyServer

在 GPU 机器上，进入 Isaac-GR00T 仓库：

```bash
uv run python gr00t/eval/run_gr00t_server.py \
    --model-path /path/to/output/checkpoint-20000 \
    --embodiment-tag UNITREE_G1_SONIC \
    --device cuda:0 \
    --port 5550
```

### 运行推理

在推理机器上（位于 GR00T-WholeBodyControl 仓库）：

```bash
python gear_sonic/scripts/launch_inference.py \
    --policy-host <gpu_machine_ip> \
    --policy-port 5550 \
    --camera-host 192.168.123.164 \
    --prompt "pick up the soda can and place it in the bin"
```

## 总结

| 步骤 | 位置 | 关键命令 |
|------|-------|-------------|
| 采集 | GR00T-WholeBodyControl | `launch_data_collection.py` |
| 微调 | Isaac-GR00T | `launch_finetune.py` |
| 部署 | 两个仓库 | `run_gr00t_server.py` + `launch_inference.py` |

要在任务上迭代，重复步骤 1–3：采集更多数据、再次微调（或从现有检查点继续训练），然后重新部署。
