# VLA 推理

本指南介绍如何使用 Sonic 全身控制栈，在 Unitree G1 机器人上运行训练好的 Isaac-GR00T VLA 策略。

## 概览

推理流水线由以下部分组成：

1. **Isaac-GR00T PolicyServer** —— 加载 VLA 模型，并通过 ZMQ 提供动作服务
2. **VLA 推理客户端**（`run_vla_inference.py`）—— 读取相机与机器人状态，向 PolicyServer 查询，并把动作发布给 C++ 控制循环
3. **C++ 部署**（`gear_sonic_deploy`）—— 在机器人上执行全身控制
4. **相机服务器** —— 通过 ZMQ 提供相机图像（以 systemd 服务运行）
5. **数据导出器**（可选）—— 在推理期间记录回合

```
┌──────────────────────┐
│  Isaac-GR00T         │
│  PolicyServer        │
│  (GPU machine)       │
└──────┬───────────────┘
       │ ZMQ REQ/REP
       ▼
┌─────────────────────┐    ZMQ TCP    ┌──────────────────────┐
│  VLA Inference      │ ◄─────────── │  Camera Server       │
│  (run_vla_inference)│              │  (on robot)          │
└────┬───────────┬────┘              └──────────────────────┘
     │           │
     │ ZMQ PUB   │ ZMQ SUB
     │ (actions) │ (state)
     ▼           ▼
┌─────────────────────┐
│  C++ Deploy         │
│  (gear_sonic_deploy)│
└─────────────────────┘
```

## 先决条件

### 1. Isaac-GR00T PolicyServer

PolicyServer 运行在有 GPU 的机器上。它加载你微调后的 VLA 模型，并通过 ZMQ 提供推理服务。

安装 [Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T) 并启动服务器：

```bash
# 在 GPU 机器上（位于 Isaac-GR00T 仓库）
uv run python gr00t/eval/run_gr00t_server.py \
    --model-path /path/to/your/finetuned_model \
    --embodiment-tag UNITREE_G1_SONIC \
    --device cuda:0 \
    --port 5550
```

### 2. 推理环境

在推理机器上（可以与 PolicyServer 同机，也可以是单独的 PC）：

```bash
bash install_scripts/install_inference.sh
```

该脚本会创建 `.venv_inference`，其中包含 Isaac-GR00T PolicyClient 以及全部推理依赖。

### 3. 相机服务器

相机服务器应以 systemd 服务的形式在机器人上运行。相机服务器的搭建参见[数据采集](data_collection.md)。

### 4. C++ 部署

必须先编译构建 `gear_sonic_deploy` 二进制程序。参见主 README。

### SONIC v1.1 检查点

当 VLA 策略是以机器人朝向归一化的 SONIC 控制器为基准训练时，请使用 `sonic_v1_1/` 检查点。它使用 10 帧 SMPL/腕部参考时域，并在训练中采用了腕部姿态增强。它不是低延迟检查点。

```bash
python download_from_hf.py --sonic-v1-1
```

启动配套的 C++ 控制器：

```bash
cd gear_sonic_deploy
./deploy.sh \
    --cp policy/sonic_v1_1/model \
    --obs-config policy/sonic_v1_1/observation_config.yaml \
    --input-type zmq_manager \
    --motor-kp-scale 4,10=1.5 \
    --motor-kd-scale 4,10=1.5 \
    real
```

这项 v1.1 调优会缩放左右踝关节俯仰电机（硬件索引 `4` 与 `10`）。由此带来的全身稳定性提升改善了观测到的腕部跟踪效果；它并不直接缩放腕部电机。

或者，把同一对模型参数传给 Python 启动器：

```bash
python gear_sonic/scripts/launch_inference.py \
    --deploy-checkpoint policy/sonic_v1_1/model \
    --deploy-obs-config policy/sonic_v1_1/observation_config.yaml \
    --deploy-motor-kp-scale 4,10=1.5 \
    --deploy-motor-kd-scale 4,10=1.5 \
    --camera-host 192.168.123.164 \
    --prompt "pick up the cup"
```

### 低延迟遥操作检查点

`low_latency/` 检查点面向响应迅速的全身遥操作。其 SMPL 编码器使用 50 Hz 下的 4 帧未来参考帧（约 80 ms 的参考前瞻），而默认发布版本使用 10 帧（约 200 ms）。这是参考前瞻，不是端到端系统总延迟。

从 Hugging Face 下载部署文件：

```bash
python download_from_hf.py --low-latency
```

然后用低延迟模型前缀和配套的观测配置启动 `gear_sonic_deploy`：

**C++ 部署：**

```bash
cd gear_sonic_deploy
./deploy.sh \
    --cp policy/low_latency/model \
    --obs-config policy/low_latency/observation_config.yaml \
    --input-type zmq_manager \
    real
```

仿真时把 `real` 换成 `sim`。`--cp` 的值是模型前缀：`deploy.sh` 会在内部追加 `_encoder.onnx` 与 `_decoder.onnx`。

**Python 启动器：**

```bash
python gear_sonic/scripts/launch_inference.py \
    --deploy-checkpoint policy/low_latency/model \
    --deploy-obs-config policy/low_latency/observation_config.yaml \
    --camera-host 192.168.123.164 \
    --prompt "pick up the cup"
```

Python 启动器会在一个 tmux 窗格中启动相同的 C++ 部署命令，然后运行 Python VLA 推理客户端、键盘发布端和可选的数据导出器。

## 动作空间

Sonic 具身（`unitree_g1_sonic`）使用 78 维动作空间：64 维运动 token + 7 维左手关节 + 7 维右手关节。

## 快速开始——tmux 启动器

运行推理最简单的方式是一体化 tmux 启动器：

```bash
# 真机
python gear_sonic/scripts/launch_inference.py \
    --prompt "pick up the apple" \
    --camera-host 192.168.123.164

# 仿真
python gear_sonic/scripts/launch_inference.py --sim \
    --prompt "pick up the apple"

# 不录制数据
python gear_sonic/scripts/launch_inference.py \
    --no-data-exporter \
    --prompt "pick up the apple"
```

启动器会创建一个包含四个窗格的 tmux 会话：

| 窗格 | 组件 | 描述 |
|------|-----------|-------------|
| 0（左上） | C++ 部署 | 全身控制器 |
| 1（左下） | 键盘发布端 | 在此输入键盘指令 |
| 2（右上） | VLA 推理 | 策略客户端 + 动作循环 |
| 3（右下） | 数据导出器 | 记录回合（可选） |

### 键盘控制

在**键盘发布端**窗格（窗格 1）中输入这些按键：

| 按键 | 操作 |
|-----|--------|
| `k` | 启动 / 停止 C++ 控制循环 |
| `i` | 平滑过渡到初始姿态，并切换到 POSE 模式 |
| `p` | 暂停 / 恢复策略推理 |
| `[` | 切换左手张开/闭合（初始姿态） |
| `]` | 切换右手张开/闭合（初始姿态） |
| `t <text>` | 更改推理提示词（例如 `t pick up the cup`） |
| `c` | 开始录制回合（数据导出器） |
| `s` | 停止录制——成功（数据导出器） |
| `f` | 停止录制——失败 / 丢弃（数据导出器） |

### 典型工作流

1. 等待所有窗格完成初始化
2. 点击**窗格 0**（C++ 部署），按 Enter 确认部署
3. 切换到**窗格 1**（键盘发布端）
4. 按 `k` 启动 C++ 控制循环（以 PLANNER 模式启动）
5. 按 `i` 过渡到初始姿态（切换到 POSE 模式）
   > 机器人会在 1 秒内平滑插值到初始姿态。如果你的任务的起始姿态与默认不同，请参见下文[自定义初始姿态](#customizing-the-initial-pose)。
6. 按 `p` 取消暂停推理循环
7. 机器人将开始执行 VLA 预测的动作
8. 结束时按 `p` 暂停，按 `k` 停止控制循环

## 手动搭建（不使用 tmux）

如果你更愿意在各自独立的终端中运行每个组件：

### 终端 1 —— Isaac-GR00T PolicyServer（GPU 机器）

```bash
# 位于 Isaac-GR00T 仓库
uv run python gr00t/eval/run_gr00t_server.py \
    --model-path /path/to/your/finetuned_model \
    --embodiment-tag UNITREE_G1_SONIC \
    --device cuda:0 \
    --port 5550
```

### 终端 2 —— C++ 部署

```bash
cd gear_sonic_deploy
./deploy.sh --input-type zmq_manager real
```

低延迟变体：

```bash
python gear_sonic/scripts/launch_inference.py \
    --deploy-checkpoint policy/low_latency/model \
    --deploy-obs-config policy/low_latency/observation_config.yaml \
    --camera-host 192.168.123.164 \
    --prompt "pick up the apple"
```

等价的手动 C++ 部署命令：

```bash
cd gear_sonic_deploy
./deploy.sh \
    --cp policy/low_latency/model \
    --obs-config policy/low_latency/observation_config.yaml \
    --input-type zmq_manager \
    real
```

### 终端 3 —— VLA 推理

```bash
source .venv_inference/bin/activate
python gear_sonic/scripts/run_vla_inference.py \
    --host <policy_server_ip> \
    --port 5550 \
    --embodiment-tag unitree_g1_sonic \
    --prompt "pick up the apple" \
    --camera-host 192.168.123.164
```

### 终端 4 —— 数据导出器（可选）

```bash
source .venv_data_collection/bin/activate
python gear_sonic/scripts/run_data_exporter.py \
    --task-prompt "pick up the apple" \
    --camera-host 192.168.123.164
```

## 配置参考

### VLA 推理（`run_vla_inference.py`）

| 旗标 | 默认值 | 描述 |
|------|---------|-------------|
| `--host` | `localhost` | PolicyServer 主机 |
| `--port` | `5550` | PolicyServer 端口 |
| `--embodiment-tag` | `unitree_g1_sonic` | 具身标签（embodiment tag） |
| `--prompt` | `demo` | 语言提示词 |
| `--action-publish-rate` | `50` | 动作发布频率（Hz） |
| `--action-horizon` | `40` | 每个推理动作块中的动作数 |
| `--rate` | `2.5` | 推理频率（Hz） |
| `--camera-host` | `localhost` | 相机服务器主机 |
| `--camera-port` | `5555` | 相机服务器端口 |
| `--initial-pose-blend-duration` | `1.0` | 过渡到初始姿态的时长（秒）（0 = 立即对齐） |
| `--verbose-timing` | `false` | 始终打印循环耗时 |

### tmux 启动器（`launch_inference.py`）

启动器暴露上述所有旗标，外加部署与数据导出器选项。使用 `--deploy-motor-kp-scale` 与 `--deploy-motor-kd-scale` 可将硬件增益设置传递给 C++ 控制器。完整列表请运行 `python gear_sonic/scripts/launch_inference.py --help`。

## 远程 PolicyServer

在另一台 GPU 机器上运行 PolicyServer 时：

```bash
# 在推理机器上，指向远程服务器
python gear_sonic/scripts/launch_inference.py \
    --policy-host <gpu_machine_ip> \
    --policy-port 5550 \
    --camera-host 192.168.123.164 \
    --prompt "pick up the apple"
```

请确保 5550 端口（或你选定的端口）在两台机器之间可访问。

## 延迟补偿

推理循环会自动补偿网络与计算延迟。当新的动作块到达时，系统会根据自推理开始以来经过的时间，计算动作块中已有多少动作“过期”，并跳到相应的动作索引。这由 `--action-publish-rate` 与 `--action-horizon` 控制。

## 自定义初始姿态

按下 `i` 时，推理客户端会让机器人从当前构型平滑过渡到一个预定义的**初始姿态**——它被编码为一个 64 维潜在运动 token。该姿态应与你示教数据通常的起始构型一致。

### 何时需要更改初始姿态

出现以下情况时，你应更新初始运动 token：

- 你采集的示教数据的起始姿态与默认相差很远（例如手臂高举、手持物体，或不同的站姿）
- 你切换到不同的 SONIC 检查点（每个检查点有自己的潜空间——同一个 token 在不同检查点会产生不同的姿态）
- 按下 `i` 时机器人会对齐到危险或不稳定的构型

### 在哪里修改

编辑 `gear_sonic/utils/inference/initial_poses.py`：

```python
LATENT_INITIAL_MOTION_TOKEN = np.array(
    [
        # 替换为你的 64 维 token
        ...
    ],
    dtype=np.float32,
)
```

### 如何找到合适的 token

1. **从数据采集：** 查看一条好的示教回合的首个动作帧。parquet 文件中 `frame_index=0` 处的 `action.motion_token` 列就是该姿态对应的潜在 token。

2. **从 C++ 部署：** 通过遥操作把机器人摆到期望的起始姿态，然后读取 ZMQ 动作通道上最近发布的潜在 token。

### 过渡时长

过渡时长控制机器人切换到初始姿态的快慢：

```bash
# 默认：1 秒平滑过渡
python gear_sonic/scripts/run_vla_inference.py --initial-pose-blend-duration 1.0

# 更快过渡（0.5 秒）
python gear_sonic/scripts/run_vla_inference.py --initial-pose-blend-duration 0.5

# 立即对齐（无插值，旧行为）
python gear_sonic/scripts/run_vla_inference.py --initial-pose-blend-duration 0
```

```{warning}
把 `--initial-pose-blend-duration` 设置得过低（或为 0）可能导致动作颠簸，尤其当机器人当前姿态与初始姿态相差较远时。默认的 1 秒过渡对大多数构型都是安全的。
```
