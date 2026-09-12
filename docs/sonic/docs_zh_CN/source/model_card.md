# 模型卡

SONIC 为 Unitree G1 提供三个已发布的全身控制器检查点。请根据参考表示形式和目标部署场景选择模型。

## 可用模型

| 模型 | Hugging Face 位置 | SMPL 参考输入 | 用途与说明 |
|---|---|---|---|
| **Default SONIC（原始发布版）** | 顶层 `model_encoder.onnx`、`model_decoder.onnx`、`observation_config.yaml`；训练检查点位于 `sonic_release/last.pt` | 以 20 ms 间隔取 10 个未来帧，约 200 ms 参考前瞻 | 默认通用 SONIC 控制器，用于动作跟踪、规划、遥操作，以及与现有部署的兼容。G1 与遥操作的未来参考观测使用 `step5`。 |
| **低延迟遥操作（Low-latency teleoperation）** | [`low_latency/`](https://huggingface.co/nvidia/GEAR-SONIC/tree/main/low_latency) | 以 20 ms 间隔取 4 个未来帧，约 80 ms 参考前瞻 | 适用于响应更快的全身遥操作与 VLA 执行。G1 与遥操作的未来参考观测使用 `step1`。其编码器、解码器与观测配置需配套使用。 |
| **SONIC v1.1** | [`sonic_v1_1/`](https://huggingface.co/nvidia/GEAR-SONIC/tree/main/sonic_v1_1) | 以 20 ms 间隔取 10 个未来帧，约 200 ms 参考前瞻 | 使用机器人朝向归一化的目标朝向，并以腕部姿态增强进行训练。适用于朝向稳定的全身遥操作，以及以该控制器为基础训练的基于 SONIC 的 VLA 策略。G1 与遥操作的未来参考观测使用 `step5`；这不是低延迟模型。 |

```{image} _static/sonic_v1_1_demo.gif
:alt: SONIC v1.1 全身遥操作演示
:width: 100%
:align: center
```

*SONIC v1.1：全身遥操作模式，具备富有表现力的腕部动作与动态运动。*

三个模型均采用 SONIC 通用 token 控制器架构，输出 64 维潜在运动 token，以 50 Hz 运行控制器，并支持 SMPL 姿态、G1 动作参考与遥操作输入。部署使用 C++ 与 TensorRT；PyTorch 检查点支持 Isaac Lab 评估与继续训练。

```{note}
前瞻数值描述的是呈现给控制器的参考时域，并非端到端遥操作总延迟的实测值——后者还包括感知、网络传输、预处理与推理耗时。
```

## 发布文件

| 模型 | 部署文件 | PyTorch 与配置文件 |
|---|---|---|
| Default SONIC | `model_encoder.onnx`、`model_decoder.onnx`、`observation_config.yaml` | `sonic_release/last.pt`、`sonic_release/config.yaml` |
| 低延迟遥操作 | `low_latency/model_encoder.onnx`、`low_latency/model_decoder.onnx`、`low_latency/observation_config.yaml` | `low_latency/last.pt`、`low_latency/config.yaml`、`low_latency/model_config.yaml` |
| SONIC v1.1 | `sonic_v1_1/model_encoder.onnx`、`sonic_v1_1/model_decoder.onnx`、`sonic_v1_1/observation_config.yaml` | `sonic_v1_1/last.pt`、`sonic_v1_1/config.yaml`、`sonic_v1_1/model_config.yaml` |

根目录的 [`config.json`](https://huggingface.co/nvidia/GEAR-SONIC/blob/main/config.json)
是各变体与共享工件的标准发布清单。官方下载器会在下载模型文件之前先获取并校验该清单。

所有文件托管于
[`nvidia/GEAR-SONIC`](https://huggingface.co/nvidia/GEAR-SONIC)。模型权重受
[NVIDIA Open Model License](resources/license.md) 约束。

## 如何选择模型

当你需要原始发布版本、与现有部署方案的最大兼容性，或标准的动作跟踪与规划控制器时，请使用 **Default SONIC**。

当对 SMPL、VR 或 VLA 指令流的响应速度是首要考虑时，请使用 **低延迟遥操作** 版本。其更短的参考时域减少了指令动作的前瞻量，但并不能消除系统中其他环节的延迟。

当需要机器人朝向归一化的全身遥操作，或要训练以该控制器为基础的基于 SONIC 的 VLA 策略时，请使用 **SONIC v1.1**。它保留了 10 帧 SMPL 参考时域，并以腕部姿态增强进行训练。

## 用法

在仓库根目录安装 Hugging Face 依赖：

```bash
pip install huggingface_hub
```

### Default SONIC

```bash
python download_from_hf.py

cd gear_sonic_deploy
./deploy.sh --input-type zmq_manager real
```

### 低延迟遥操作

```bash
python download_from_hf.py --low-latency

cd gear_sonic_deploy
./deploy.sh \
    --cp policy/low_latency/model \
    --obs-config policy/low_latency/observation_config.yaml \
    --input-type zmq_manager \
    real
```

### SONIC v1.1

```bash
python download_from_hf.py --sonic-v1-1

cd gear_sonic_deploy
./deploy.sh \
    --cp policy/sonic_v1_1/model \
    --obs-config policy/sonic_v1_1/observation_config.yaml \
    --input-type zmq_manager \
    --motor-kp-scale 4,10=1.5 \
    --motor-kd-scale 4,10=1.5 \
    real
```

上述增益旗标是经过实测的 v1.1 硬件调参。电机索引 `4` 和 `10` 分别对应左右踝关节俯仰电机；额外的刚度可提升全身稳定性以及观察到的腕部跟踪效果。增益缩放为可选项。

### Python VLA 启动器

默认模型：

```bash
python gear_sonic/scripts/launch_inference.py \
    --camera-host 192.168.123.164 \
    --prompt "pick up the cup"
```

低延迟模型：

```bash
python gear_sonic/scripts/launch_inference.py \
    --deploy-checkpoint policy/low_latency/model \
    --deploy-obs-config policy/low_latency/observation_config.yaml \
    --camera-host 192.168.123.164 \
    --prompt "pick up the cup"
```

SONIC v1.1：将上面两个 `policy/low_latency/` 路径替换为
`policy/sonic_v1_1/`，并追加：

```text
--deploy-motor-kp-scale 4,10=1.5
--deploy-motor-kd-scale 4,10=1.5
```

PyTorch 检查点评估与更多下载选项参见 [下载模型检查点](getting_started/download_models.md)。

## 局限性与安全

- "低延迟" 一词指控制器参考前瞻的缩短，并非系统总延迟的基准测试结果。
- SONIC v1.1 不是低延迟检查点；它使用 10 帧 SMPL 参考时域。
- 每个 ONNX 编码器与解码器必须与其配套的观测配置一起使用。
- 这些检查点面向 Unitree G1 机器人本体。
- 部署前请先在仿真中测试，并保持一名安全员随时可以停止实体机器人。
