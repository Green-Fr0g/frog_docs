# Isaac Teleop 配置（CloudXR / DeviceIO，进程内）

本页介绍面向 **G1 + Thor 背包** 的 Isaac Teleop / CloudXR 部署流程，可直接从头显驱动 `GR00T-WholeBodyControl`。使用 `pico_manager_thread_server.py --input-source isaac-teleop` 时，CloudXR 运行时通过 `isaacteleop[cloudxr]` Python 包以**进程内**方式承载。

```{admonition} 适用范围
:class: important
真机部署仅在 **G1 + Thor 背包** 上受支持。Sim2Sim（MuJoCo）可在 Thor 与 x86_64 工作站上运行。
```

## 前置条件

1. **已完成[快速上手](../getting_started/quickstart.md)**——能够运行 Sim2Sim 循环（包含[安装部署](../getting_started/installation_deploy.md)和[下载模型检查点](../getting_started/download_models.md)）。
2. **已完成 [VR 遥操作配置](../getting_started/vr_teleop_setup.md)**——`.venv_teleop` 已就绪，且已运行 `install_pico.sh`（真机部署在 Thor 上运行；Sim2Sim 在工作站上运行）。

本页是上游 [Isaac Teleop](https://nvidia.github.io/IsaacTeleop/) 文档的精简、本仓库特化版本：

- [快速上手](https://nvidia.github.io/IsaacTeleop/main/getting_started/quick_start.html)
- [`isaacteleop[cloudxr]` Python API](https://nvidia.github.io/IsaacTeleop/main/)

## 第 1 步：准备 Thor 主机

在 Thor 上安装前置依赖（部署流程其他部分已完成的可跳过）：

```bash
sudo apt install -y build-essential curl git-lfs
git lfs install
```

```{note}
本步骤的剩余内容（最大功耗模式、过热检查）使用 Thor/Jetson 专属工具。如果你是在 x86_64 工作站上运行 Sim2Sim（MuJoCo）而非真机 G1 硬件，请直接跳到第 2 步。
```

为保证 Thor 性能，遥操作前启用最大功耗模式：

```bash
sudo nvpmodel -m 0
sudo jetson_clocks
```

可选的过热 / 过流检查：

```bash
cat /sys/class/hwmon/hwmon*/oc*_event_cnt
```

## 第 2 步：确认已安装 `isaacteleop[cloudxr]`

```{note}
本步骤是检查点，而非新操作。在 [VR 遥操作配置](../getting_started/vr_teleop_setup.md)第 3 步中运行的 `install_pico.sh` 已经安装了 `isaacteleop[cloudxr]`。如果该步骤已完成，直接跳到下方的第 3 步；否则请先完成它再继续。
```

供参考，`install_pico.sh` 从 NVIDIA 公共索引安装该包：

```bash
# Already wired into install_pico.sh; shown here for reference
uv pip install 'isaacteleop[cloudxr]~=1.3.0' --prerelease=allow \
    --extra-index-url https://pypi.nvidia.com
```

它还会在 `~/cloudxr.env` 中写入 `NV_DEVICE_PROFILE=Quest3`（可通过编辑该文件覆盖）。`CloudXRLauncher` 启动时读取此配置。

## 第 3 步：启动 C++ 部署

在 `gear_sonic_deploy/` 下：

```bash
export TensorRT_ROOT=$HOME/TensorRT   # only if not already in ~/.bashrc
./docker/run-ros2-dev.sh

# inside the container (setup_env.sh is sourced automatically):
just build                            # first run only

# run one of these:
./deploy.sh --input-type zmq_manager real   # real robot
./deploy.sh --input-type zmq_manager sim    # Sim2Sim (MuJoCo)
# Wait until you see "Init done"
```

```{note}
Sim2Sim 模式下，请先按[快速上手](../getting_started/quickstart.md)的 Sim2Sim 章节在宿主机上启动 MuJoCo 仿真器，否则部署程序将没有任何可控制的对象。
```

## 第 4 步：启动遥操作推流端

在**仓库根目录**：

```bash
source .venv_teleop/bin/activate
python gear_sonic/scripts/pico_manager_thread_server.py --manager \
    --input-source isaac-teleop

# If running offboard with a display, add visualization:
#   --vis_vr3pt --vis_smpl
```

启动时，推流端会拉起进程内的 CloudXR 运行时并记录日志 `Isaac Teleop session initialized.`，随后持续输出 `waiting for Isaac Teleop body data (connect the headset to CloudXR)...`，直到你在第 5 步连接客户端。

## 第 5 步：连接 XR 客户端

连接客户端后，推流端等待的身体数据流才会开始传输。

- 在头显浏览器中打开 [Isaac Teleop Web 客户端](https://nvidia.github.io/IsaacTeleop/client/)
- 输入运行推流端的主机 IP 地址
- 接受 `https://<host-ip>:48322` 的自签名证书
- 在 Thor 上，将 **Video Codec**（视频编解码器）从默认的 **AV1** 改为 **H.264** 或 **H.265 (HEVC)**。
- 返回客户端页面并点击 **Connect**（连接）

连接成功后，摆出[校准姿态](vr_wholebody_teleop.md#calibration-pose)并在 PICO 手柄上按 **A+B+X+Y** 启动策略；首次按压还会执行启动校准并进入 PLANNER（移动）模式。然后按 **A+X** 切换到 POSE 模式进行全身遥操作，你的动作将直接映射到机器人。其他模式与急停操作见[完整 PICO 按键说明](vr_wholebody_teleop.md#pico-controls)。

如需快速验证，同一客户端 URL 也可在桌面浏览器中打开。

如果你希望从源码运行 WebXR 客户端而非使用托管客户端，请按照 [Isaac Teleop 快速上手](https://nvidia.github.io/IsaacTeleop/main/getting_started/quick_start.html)中链接的 CloudXR/WebXR 构建说明操作。

## 第 6 步：启动相机可视化

通过上游 IsaacTeleop 的 `camera_viz.sh` 将相机画面推流到头显。如果还没有 IsaacTeleop 仓库，先克隆：

```bash
git clone --recurse-submodules https://github.com/NVIDIA/IsaacTeleop.git
```

然后为相机可视化推流端创建环境：

```bash
cd IsaacTeleop
examples/camera_viz/camera_viz.sh setup
source examples/camera_viz/.venv/bin/activate
cd examples/camera_viz
```
### 可选：在窗口中预览相机画面
如果你有可用的视频预览（例如在 Thor 或桌面仿真上），最好先用 "window"（窗口）模式测试相机：
```bash
./camera_viz.sh run configs/YOUR_CAMERA.yaml --mode window
```

为你的设备选择正确的 yaml 相机配置至关重要。v4l2.yaml 是默认配置，但也提供其他配置：
```bash
# run just one of these that best matches your camera
./camera_viz.sh run configs/v4l2.yaml --mode window
./camera_viz.sh run configs/oakd.yaml --mode window
./camera_viz.sh run configs/zed.yaml --mode window
./camera_viz.sh run configs/realsense.yaml --mode window
```
如果相机输出不正确，可能需要修改与你设备最接近的 yaml 文件，或在 configs 文件夹中创建自己的配置。请考虑以下几点：
- 连接多个相机会改变视频应使用的通道。
- 先尝试运行命令 "lsusb"，确认相机已连接。
- 接着用 "ls -1 /dev/video*" 列出所有视频设备模式。
- 如果你使用 v4l2 方案（Video4Linux2），以下命令有助于排查可用能力：
  - 查看通道与相机的对应关系："v4l2-ctl --list-devices"
  - 查看每个节点捕获的内容及像素格式："v4l2-ctl --device=/dev/video0 --list-formats"
  - 查看格式与可用分辨率的完整细节："v4l2-ctl --device=/dev/video0 --list-formats-ext"
获得这些信息后，请确保 yaml 配置中的设置与之匹配。

### XR 相机推流命令

确认 yaml 配置有效后，关闭所有预览窗口，改用 "--mode xr" 运行，即可将帧推流到 Isaac Teleop：

```bash
./camera_viz.sh run configs/[YOUR_CAMERA].yaml --mode xr
```
此流程也应与 [IsaacTeleop 中的说明](https://nvidia.github.io/IsaacTeleop/main/references/camera_streaming.html)保持一致。

## 故障排除

### `RuntimeError: Failed to get OpenXR system: -35`

在此配置下，该报错通常意味着 XR 客户端尚未连接。请再次检查：

- 头显 / Web 客户端已完全连接到 `https://<host-ip>:48322`
- CloudXR 运行时子进程仍在运行（寻找 `Isaac Teleop session initialized.` 日志）
- `~/cloudxr.env` 存在，且 `NV_DEVICE_PROFILE` 与你的头显匹配

### 客户端已连接但视频编码器初始化失败

在 Thor 上，这通常意味着客户端的 **Video Codec** 仍为默认的 **AV1**。将客户端切换为 **H.264** 或 **H.265 (HEVC)** 后重新连接（见第 5 步）。

### `gear_sonic_deploy` 编译报错

如果 `just build` 失败，在容器内从头重新构建（第 3 步）：

```bash
rm -rf build
just build
```

### `isaacteleop` 导入报错

重新运行 `install_pico.sh`，将 `isaacteleop[cloudxr]~=1.3.0` 重新安装到 `.venv_teleop`。若 `pypi.nvidia.com` 无法访问，请检查网络与 `--extra-index-url` 旗标。

### 收不到身体数据

如果头显停止提供身体数据，推流端会记录 `[IsaacTeleopReader] No DeviceIO data for 5.0s, flagging disconnect`。请确认：

1. 头显仍连接在 CloudXR 上（第 5 步）。
2. Pico 身体追踪器已配对并完成校准（见 [VR 遥操作配置 → Motion Tracker 配置](../getting_started/vr_teleop_setup.md)）。
3. schema 首次运行时，留意 `[IsaacTeleopReader] Unrecognised body_data schema: type=...`——若出现此日志，说明上游 `FullBodyTrackerPico.get_body_pose().data` 的形状发生了变化，需要在 `gear_sonic/utils/teleop/input_readers.py` 的 `_body_data_to_24x7()` 中为新布局增加一个分支。
