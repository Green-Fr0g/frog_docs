# 面向 VLA 的数据采集

将遥操作示教录制为 [LeRobot](https://github.com/huggingface/lerobot) 数据集，用于 [Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T) 的后训练。数据导出器与 SONIC 部署及 VR 遥操作栈并行运行，以可配置的频率捕获机器人状态、SMPL 遥操作姿态和相机图像。

```{admonition} 部署模型
:class: important
除**相机服务器**运行在**机器人机载计算机**（如 Jetson Orin，物理相机连接于此）上之外，其余全部**在工作站上离机（offboard）运行**。相机服务器通过 ZMQ 向工作站发布 JPEG 帧。
```

```{admonition} 支持的相机
:class: note
经过测试并受支持的相机方案采用 **Luxonis OAK 相机**（OAK-D、OAK-1 等），包括一个头部/第一视角 OAK 相机，以及可选的 OAK 腕部相机。代码库中还包含其他相机驱动（RealSense、USB 网络摄像头），但近期未经测试。

头部/第一视角 **OAK-D W** 相机的 3D 打印支架可在 [`hardware/camera_mount/`](https://github.com/NVlabs/GR00T-WholeBodyControl/blob/main/hardware/camera_mount/README.md) 获取——打印参数、物料清单以及在 G1 上的安装方式见其 README。
```

```{admonition} 前置条件
:class: note
1. **已完成[快速上手](../getting_started/quickstart.md)**——能够运行 sim2sim 循环（包含[安装部署](../getting_started/installation_deploy.md)和[下载模型检查点](../getting_started/download_models.md)）。
2. **已完成 [VR 遥操作配置](../getting_started/vr_teleop_setup.md)**——PICO 硬件已完成校准，`.venv_teleop` 已就绪。
3. **相机服务器已在机器人上运行**——见下方[相机服务器配置](#camera-server-setup-on-robot)。仿真时，MuJoCo 仿真循环会自动发布相机图像——无需相机服务器。
```

---

## 一次性配置（工作站）

在**工作站**（运行 C++ 部署、遥操作与数据导出器的机器）上，从仓库根目录运行安装脚本，创建一个包含全部数据采集依赖（LeRobot、PyAV、OpenCV 等）的专用虚拟环境：

```sh
bash install_scripts/install_data_collection.sh
```

该脚本通过 `uv` 使用 Python 3.10 创建 `.venv_data_collection`，安装 `gear_sonic[data_collection]`（包含 `lerobot`、`av`、`opencv-python` 及其他所需包），并安装 `espeak`（系统包），用于录制时的语音反馈。

```{tip}
该环境与 `.venv_teleop` 和 `.venv_sim` 相互独立——数据导出器带有较重的 ML 依赖，遥操作与仿真并不需要。
```

---

## 相机服务器配置（机载）

相机服务器是**唯一运行在机器人计算机上的组件**（如 Jetson Orin）。其余全部——C++ 部署、PICO 遥操作推流端、数据导出器和相机查看器——均运行在工作站上。

相机服务器从物理连接到机器人的 OAK 相机捕获帧，并通过 ZMQ 发布到工作站。

### 第 1 步：在机器人上克隆仓库

SSH 登录机器人计算机并克隆本仓库：

```sh
git clone https://github.com/NVlabs/GR00T-WholeBodyControl.git
cd GR00T-WholeBodyControl
```

### 第 2 步：运行安装脚本

安装脚本会完成所有事情：创建虚拟环境，安装全部依赖（包括 OAK 相机所需的 DepthAI SDK），检测已连接的相机，
并可选择安装 systemd 服务，使相机服务器开机自启。

```sh
bash install_scripts/install_camera_server.sh
```

该脚本会：

1. 使用 `gear_sonic[camera]` 创建 `.venv_camera`（DepthAI、ZMQ、msgpack、OpenCV、tyro）。
2. 检测已连接的 OAK 相机并列出其 MxID。
3. 提示你为每个相机指定位置（第一视角，以及可选的左/右腕部）及其设备 ID。
4. 询问是否将相机服务器安装为 **systemd 服务**（推荐）。若回答 **y**，脚本会自动生成 unit 文件并安装、启用、启动该服务。

脚本运行结束后，验证服务是否正在运行：

```sh
sudo systemctl status composed_camera_server.service
journalctl -u composed_camera_server.service -f
```

```{note}
代码库中还包含其他相机驱动（RealSense、USB 网络摄像头），但近期未经数据采集测试。如需 RealSense，请在配置完成后向虚拟环境中安装 `pyrealsense2`。详情见 `gear_sonic/camera/drivers/` 中的驱动文件。
```

### 手动配置（替代方案）

如果你不想使用安装脚本，或需要重新配置：

**查找相机设备 ID：**

每台 OAK 相机都有唯一的 MxID。列出所有已连接的 OAK 设备：

```sh
source .venv_camera/bin/activate
python -c "import depthai as dai; print(dai.Device.getAllAvailableDevices())"
```

输出示例：

```text
[XLinkDeviceState.X_LINK_BOOTED, MxId: 18443010E1ABC12300, ...]
```

**手动启动相机服务器：**

```sh
source .venv_camera/bin/activate

# 单相机（仅第一视角）
python -m gear_sonic.camera.composed_camera \
    --ego-view-camera oak \
    --ego-view-device-id <YOUR_MXID> \
    --port 5555

# 多相机（第一视角 + 腕部相机）
python -m gear_sonic.camera.composed_camera \
    --ego-view-camera oak --ego-view-device-id <EGO_MXID> \
    --left-wrist-camera oak --left-wrist-device-id <LEFT_WRIST_MXID> \
    --right-wrist-camera oak --right-wrist-device-id <RIGHT_WRIST_MXID> \
    --port 5555
```

运行 `python -m gear_sonic.camera.composed_camera --help` 查看全部选项，包括 `--fps`、`--use-mjpeg` 和 `--mjpeg-quality`。

**手动配置 systemd：**

```sh
# 1. 编辑服务文件以匹配你的相机配置
nano systemd/composed_camera_server.service

# 2. 复制到 systemd，启用并启动
sudo cp systemd/composed_camera_server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable composed_camera_server.service
sudo systemctl start composed_camera_server.service
```

systemd 服务运行后，机器人每次开机相机服务器都会自动启动——无需人工干预。

### 从工作站连接

在工作站上，数据导出器和相机查看器通过网络连接到机器人的相机服务器。传入机器人的 IP 地址（G1 机器人默认 IP 为 `192.168.123.164`）：

```sh
# 数据导出器
python gear_sonic/scripts/run_data_exporter.py \
    --task-prompt "pick up the cup" \
    --camera-host 192.168.123.164 --camera-port 5555

# 相机查看器（用于确认画面）
python gear_sonic/scripts/run_camera_viewer.py \
    --camera-host 192.168.123.164 --camera-port 5555
```

tmux 启动器同样接受 `--camera-host`：

```sh
python gear_sonic/scripts/launch_data_collection.py \
    --camera-host 192.168.123.164 \
    --task-prompt "pick up the cup"
```

### ZMQ 消息格式

相机服务器在每个帧周期发布一条 msgpack 编码的载荷，包含所有相机图像：

```python
{
    "timestamps": {"ego_view": 1712345678.123, "left_wrist": 1712345678.125},
    "images": {"ego_view": "<base64-jpeg>", "left_wrist": "<base64-jpeg>"}
}
```

图像以 JPEG 压缩（质量 80），为 base64 编码字符串或原始 JPEG 字节（启用设备端 MJPEG 编码时）。数据导出器的 `ComposedCameraClientSensor` 会自动处理这两种格式。

---

## 架构

数据导出器从三个 ZMQ 数据源接收数据。C++ 部署、PICO 遥操作和数据导出器均在**工作站上离机（offboard）运行**。相机服务器**在机器人机载运行**，通过网络向工作站推流。

```text
    Workstation (offboard)                           Robot (onboard)
┌──────────────────────┐  ┌──────────────────────┐  ┌───────────────┐
│  C++ deploy          │  │  pico_manager         │  │  Camera       │
│  (zmq_output_handler)│  │  _thread_server.py    │  │  server       │
│                      │  │                       │  │  (OAK cameras)│
│  port 5557           │  │  port 5556            │  │  port 5555    │
│  topics: g1_debug,   │  │  topic: pose          │  │  (JPEG/ZMQ)   │
│          robot_config│  │  (SMPL body params)   │  │               │
└──────────┬───────────┘  └──────────┬────────────┘  └──────┬────────┘
           │                         │                       │
           └────────────┬────────────┘───────────────────────┘
                        │              (network)
               ┌────────▼────────┐
               │  run_data_      │
               │  exporter.py    │
               │  (workstation)  │
               │                 │
               │  LeRobot dataset│
               │  (parquet + mp4)│
               └─────────────────┘
```

| 数据源 | 运行位置 | ZMQ Topic | 默认端口 | 提供内容 |
|---|---|---|---|---|
| C++ 部署 | 工作站 | `g1_debug` | 5557 | 关节位置、关节速度、IMU 四元数 |
| C++ 部署 | 工作站 | `robot_config` | 5557 | 启动时的一次性机器人配置 |
| PICO 遥操作推流端 | 工作站 | `pose` | 5556 | SMPL 身体参数（遥操作目标姿态） |
| 相机服务器 | 机器人 | *（原始 TCP）* | 5555 | JPEG 压缩的相机图像（第一视角 + 可选腕部视角） |

---

## 运行数据采集

运行数据采集栈有两种方式：**一体化 tmux 启动器**（推荐）或**手动多终端启动**。

### 方式 A：一体化 tmux 启动（推荐）

启动器在单个 tmux 会话中启动全部组件，共四个窗格：

```text
┌───────────────────────┬───────────────────────┐
│ Pane 0: C++ Deploy    │ Pane 2: Data Exporter │
│ (gear_sonic_deploy)   │ (.venv_data_collection)│
├───────────────────────┼───────────────────────┤
│ Pane 1: PICO Teleop   │ Pane 3: Camera Viewer │
│ (.venv_teleop)        │ (.venv_data_collection)│
└───────────────────────┴───────────────────────┘
```

```{note}
需要已安装 `tmux`（`sudo apt install tmux`）。
```

**仿真模式**（启动器会在单独的 tmux 窗口中自动启动 `run_sim_loop.py`）：

```bash
python gear_sonic/scripts/launch_data_collection.py --sim
```

**真机模式**（相机服务器运行在 `192.168.123.164` 的机器人上）：

```bash
python gear_sonic/scripts/launch_data_collection.py \
    --camera-host 192.168.123.164 \
    --task-prompt "pick up the cup"
```

**使用腕部相机**（录制第一视角 + 左/右腕部相机流）：

```bash
python gear_sonic/scripts/launch_data_collection.py \
    --camera-host 192.168.123.164 \
    --task-prompt "pick up the cup" \
    --record-wrist-cameras
```

```{tip}
无需预先激活虚拟环境——若当前 Python 中缺少所需依赖，启动器会自动检测并使用 `.venv_data_collection`。
```

启动器会自动连接到 tmux 会话。使用 `Ctrl+b` 加方向键在窗格之间切换。

常用选项：

| 旗标 | 默认值 | 说明 |
|---|---|---|
| `--task-prompt` | `"demo"` | 语言任务描述（如 `"pick up the cup"`） |
| `--dataset-name` | *（自动：时间戳）* | 数据集名称；省略则自动生成 |
| `--sim / --no-sim` | `False` | 以仿真模式运行 deploy.sh（同时启动仿真循环） |
| `--camera-host` | `localhost` | 相机服务器主机（真机为 `192.168.123.164`） |
| `--camera-port` | `5555` | 相机服务器端口 |
| `--no-camera-viewer` | *（查看器开启）* | 禁用相机查看器窗格 |
| `--data-exporter-frequency` | `50` | 录制频率（Hz） |
| `--deploy-checkpoint` | *（默认）* | deploy.sh 的自定义检查点路径 |
| `--deploy-obs-config` | *（默认）* | deploy.sh 的自定义观测配置 |
| `--deploy-planner` | *（默认）* | deploy.sh 的自定义规划器模型路径 |
| `--deploy-motion-data` | *（默认）* | deploy.sh 的自定义动作数据路径 |
| `--deploy-motor-kp-scale` | *（禁用）* | 转发给 deploy.sh 的硬件电机 Kp 缩放规格 |
| `--deploy-motor-kd-scale` | *（禁用）* | 转发给 deploy.sh 的硬件电机 Kd 缩放规格 |
| `--record-wrist-cameras` | `False` | 将左/右腕部相机流录制进数据集 |
| `--no-text-to-speech` | *（开启）* | 禁用 espeak 语音反馈 |

运行 `python gear_sonic/scripts/launch_data_collection.py --help` 查看全部选项。

```{tip}
启动器会在 tmux 会话中自动启用**鼠标支持**——点击选择窗格、滚轮滚动、拖拽调整窗格边框大小。
```

**会话管理：**

| 操作 | 命令 |
|---|---|
| 切换窗格 | `Ctrl+b`，然后按方向键 |
| 分离（保持运行） | `Ctrl+b`，然后按 `d` |
| 重新连接 | `tmux attach -t sonic_data_collection` |
| 终止会话 | 在任意窗格按 `Ctrl+\`，或 `tmux kill-session -t sonic_data_collection` |

### 方式 B：手动多终端启动

如果你希望对每个进程单独控制，可在不同终端中分别运行：

**终端 1 — MuJoCo 仿真器** *（真机跳过）*：

```bash
source .venv_sim/bin/activate
python gear_sonic/scripts/run_sim_loop.py \
    --enable-image-publish --enable-offscreen --camera-port 5555
```

必须加上 `--enable-image-publish` 和 `--enable-offscreen` 旗标，
仿真器才能渲染相机图像并通过 ZMQ 在指定端口推流。
数据导出器订阅该端口的方式与订阅物理相机服务器完全相同。

真机部署时跳过此终端，改为参见 [VR 全身遥操作](vr_wholebody_teleop.md)。

**终端 2 — C++ 部署**（在 `gear_sonic_deploy/` 下）：

```bash
cd gear_sonic_deploy
source scripts/setup_env.sh
./deploy.sh --input-type zmq_manager sim
# 等待出现 "Init done"
```

**终端 3 — PICO 遥操作推流端：**

```bash
source .venv_teleop/bin/activate
python gear_sonic/scripts/pico_manager_thread_server.py --manager
```

**终端 4 — 数据导出器：**

```bash
source .venv_data_collection/bin/activate
python gear_sonic/scripts/run_data_exporter.py --task-prompt "pick up the cup"
```

**终端 5（可选）— 相机查看器：**

```bash
source .venv_data_collection/bin/activate
python gear_sonic/scripts/run_camera_viewer.py
```

所有选项均通过 CLI 旗标提供——没有交互式提示。关键旗标：

| 旗标 | 默认值 | 说明 |
|---|---|---|
| `--task-prompt` | `"demo"` | 本次会话的语言任务描述 |
| `--dataset-name` | *（自动：时间戳）* | 数据集名称。省略则新建，传入已有名称则追加回合 |
| `--data-collection-frequency` | `50` | 录制频率（Hz） |
| `--root-output-dir` | `outputs` | 已保存数据集的父目录 |

```{tip}
数据集保存在 `<root-output-dir>/<dataset-name>/` 下。若未指定
`--dataset-name`，则自动生成带时间戳的名称。
```

### 录制控制

控制录制有两种方式：**PICO VR 手柄**（遥操作时推荐）或**经 ZMQ 的键盘**。

**PICO VR 手柄（经 `manager_state` topic）：**

| 输入 | 动作 |
|---|---|
| **Left Grip + A** | **切换**录制——开始新回合，或停止并保存当前回合 |
| **Left Grip + B** | **丢弃**当前回合（已保存到磁盘，但在后处理中被标记为待删除） |

这些按键在任何 manager 模式（POSE、PLANNER 等）下均有效，且独立于模式切换控制。

**经 ZMQ 的键盘：**

| 按键 | 动作 |
|---|---|
| `c` | **切换**录制（同 Left Grip + A） |
| `x` | **丢弃**回合（同 Left Grip + B——标记为待删除） |

```{note}
键盘指令经独立的 ZMQ 发布端发送（默认端口 `5580`）。数据导出器会自动订阅该通道。你可以从该端口上的任意 ZMQ 发布端发送按键，或与 C++ 部署的键盘处理器集成。
```

---

## 相机查看器

独立的相机查看器可用于监控相机画面，并在不依赖数据导出器的情况下录制原始视频。

```bash
source .venv_data_collection/bin/activate
python gear_sonic/scripts/run_camera_viewer.py --camera-host localhost --camera-port 5555
```

查看器连接到数据导出器所用的同一 ZMQ 相机服务器，并在平铺的 OpenCV 窗口中显示所有检测到的相机流。

**控制**（OpenCV 窗口需获得焦点）：

| 按键 | 动作 |
|---|---|
| `R` | 开始/停止视频录制 |
| `Q` | 退出 |

录制内容保存到 `camera_recordings/rec_<timestamp>/`，每个相机流一个 MP4。用途包括：
- 开始数据采集前检查相机安装位置与图像质量
- 与 LeRobot 数据集一同录制参考视频
- 排查相机服务器连接问题

运行 `python gear_sonic/scripts/run_camera_viewer.py --help` 查看全部选项。

---

## CLI 选项

所有选项可通过 `--help` 查看：

```bash
python gear_sonic/scripts/run_data_exporter.py --help
```

关键选项：

| 旗标 | 默认值 | 说明 |
|---|---|---|
| `--task-prompt` | `"demo"` | 用于标注的语言任务描述 |
| `--dataset-name` | *（自动：时间戳）* | 数据集名称；省略则自动生成，传入已有名称则追加 |
| `--data-collection-frequency` | `50` | 录制频率（Hz） |
| `--camera-host` | `localhost` | 相机服务器主机名 |
| `--camera-port` | `5555` | 相机服务器端口 |
| `--sonic-zmq-host` | `localhost` | SMPL 姿态发布端主机 |
| `--sonic-zmq-port` | `5556` | SMPL 姿态发布端端口 |
| `--state-zmq-host` | `localhost` | 机器人状态发布端主机 |
| `--state-zmq-port` | `5557` | 机器人状态发布端端口 |
| `--root-output-dir` | `outputs` | 已保存数据集的根目录 |
| `--text-to-speech / --no-text-to-speech` | `True` | 经 espeak 的语音反馈 |

---

## 输出格式

数据集以 [LeRobot v2.1](https://github.com/huggingface/lerobot) 格式保存在 `<root-output-dir>/<dataset-name>/` 下：

```text
outputs/2026-04-03-14-30-00-G1-robot01/
├── data/
│   ├── train-00000.parquet      # Tabular data (joint states, actions, annotations)
│   └── ...
├── videos/
│   ├── observation.images.ego_view/
│   │   ├── episode_000000.mp4   # H264-encoded ego camera video
│   │   └── ...
│   ├── observation.images.left_wrist/   # (only with --record-wrist-cameras)
│   └── observation.images.right_wrist/  # (only with --record-wrist-cameras)
└── meta/
    ├── info.json                # Dataset metadata (fps, features, sizes)
    ├── modality.json            # GR00T modality configuration
    ├── episodes.jsonl           # Per-episode metadata
    └── tasks.jsonl              # Task prompt definitions
```

### 录制的数据通道

每帧包含：

| 特征 | 形状 | 说明 |
|---|---|---|
| `observation.state.joint_position` | `(N,)` | 驱动关节位置（rad） |
| `observation.state.joint_velocity` | `(N,)` | 驱动关节速度（rad/s） |
| `observation.state.body_rotation_6d` | `(6,)` | 基座朝向（6D 旋转） |
| `observation.state.projected_gravity` | `(3,)` | 机体坐标系下的重力向量 |
| `observation.images.ego_view` | `(480, 640, 3)` | 第一视角相机图像（保存为 MP4 视频） |
| `observation.images.left_wrist` | `(480, 640, 3)` | 左腕相机（仅 `--record-wrist-cameras` 时） |
| `observation.images.right_wrist` | `(480, 640, 3)` | 右腕相机（仅 `--record-wrist-cameras` 时） |
| `action.joint_position` | `(N,)` | 遥操作目标关节位置 |
| `action.body_rotation_6d` | `(6,)` | 遥操作目标身体旋转 |
| `annotation.human.action.task_description` | string | 该帧的任务提示 |

---

## 数据集后处理

录制完成后，可以使用处理脚本对数据集进行清理与合并。
以下所有命令均在**数据采集虚拟环境**中运行：

```bash
source .venv_data_collection/bin/activate
```

### 移除被丢弃的回合

采集期间被丢弃的回合（`x` 键或 Left Grip + B）会保存到磁盘，
但在 `meta/info.json` 中被标记。默认情况下，处理脚本会移除这些
被标记的回合，使其不参与微调：

```bash
# 清理单个数据集（移除被丢弃的回合 + 过期 SMPL 帧）
python gear_sonic/scripts/process_dataset.py \
    --dataset-path outputs/my_dataset \
    --output-path outputs/my_dataset_cleaned
```

如需保留被丢弃的回合（例如用于检查），传入 `--no-remove-discarded`。

### 移除过期 SMPL 帧

遥操作暂停或 ZMQ 丢帧会产生 `teleop.smpl_pose` 全零的帧。
处理脚本会检测这些帧，并同时移除其之前连续的
冻结（完全相同）引导帧：

```bash
# 原地清理单个数据集
python gear_sonic/scripts/process_dataset.py \
    --dataset-path outputs/my_dataset

# 清理并写入新目录（非破坏性）
python gear_sonic/scripts/process_dataset.py \
    --dataset-path outputs/my_dataset \
    --output-path outputs/my_dataset_cleaned
```

```{warning}
如果你使用 **VR 三点跟踪模式**（VR_3PT）采集数据，
`teleop.smpl_pose` 列将全为零，因为 VR_3PT 使用原始 VR
位置/朝向而非 SMPL 身体参数。此时你**必须**禁用 SMPL 清理，
以避免丢弃全部帧：

    python gear_sonic/scripts/process_dataset.py \
        --dataset-path outputs/my_dataset \
        --output-path outputs/my_dataset_cleaned \
        --no-remove-stale-smpl
```

### 合并多个数据集

将多个录制会话合并为单个数据集。脚本在合并前
会校验所有会话是否共享相同的 `script_config`（机器人
配置）：

```bash
# 在命令行中列出数据集进行合并
python gear_sonic/scripts/process_dataset.py \
    --dataset-path outputs/session1 outputs/session2 outputs/session3 \
    --output-path outputs/merged_dataset

# 或使用文本文件（每行一个数据集路径，# 为注释）
python gear_sonic/scripts/process_dataset.py \
    --dataset-list datasets.txt \
    --output-path outputs/merged_dataset
```

合并时默认应用 SMPL 清理。启用时，脚本
会移除 SMPL 遥操作姿态停滞在零值的整帧——这发生在操作员
暂停或 ZMQ 丢包期间，此时 SMPL 流停止更新。
进入零值块之前的连续冻结（完全相同）帧也会被移除，
因为它们代表丢帧发生前一刻的过期数据。
如需跳过清理仅做合并，添加 `--no-remove-stale-smpl`。

---

## 后续步骤：微调与部署

输出的数据集可直接用于 [Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T) 后训练流水线。要在你采集的数据上微调 VLA 模型并将其部署用于自主推理，参见 [VLA 工作流教程](vla_workflow.md)。
