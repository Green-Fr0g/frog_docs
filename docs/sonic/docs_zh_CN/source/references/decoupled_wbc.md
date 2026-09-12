# Decoupled WBC

面向多个人形机器人平台的移动操作（loco-manipulation）实验软件栈，主要支持 Unitree G1。本仓库提供全身控制策略、遥操作栈和数据导出器。

---

## 系统安装

### 前提条件
- Ubuntu 22.04
- 配有较新驱动的 NVIDIA GPU
- Docker 与 NVIDIA Container Toolkit（容器内访问 GPU 必需）

### 仓库设置

安装 Git 和 Git LFS：

```bash
sudo apt update
sudo apt install git git-lfs
git lfs install
```

克隆仓库：

```bash
mkdir -p ~/Projects
cd ~/Projects
git clone https://github.com/NVlabs/GR00T-WholeBodyControl.git
cd decoupled_wbc
```

### Docker 环境

我们提供了预装全部依赖的 Docker 镜像。

安装全新镜像并启动容器：

```bash
./docker/run_docker.sh --install --root
```

该命令会从 `docker.io/nvgear` 拉取最新的 `decoupled_wbc` 镜像。

启动或重新进入容器：

```bash
./docker/run_docker.sh --root
```

使用 `--root` 以 `root` 用户运行。若要以普通用户运行，请在本地构建镜像：

```bash
./docker/run_docker.sh --build
```

---

## 运行控制栈

进入容器后，即可直接启动控制策略。

- 仿真：

```bash
python decoupled_wbc/control/main/teleop/run_g1_control_loop.py
```

- 真机：确保主机网络已按照 [G1 SDK 开发指南](https://support.unitree.com/home/en/G1_developer) 配置，并将静态 IP 设为 `192.168.123.222`、子网掩码 `255.255.255.0`：

```bash
python decoupled_wbc/control/main/teleop/run_g1_control_loop.py --interface real
```

键盘快捷键（终端窗口内）：
- `]`：激活策略
- `o`：停用策略
- `9`：释放 / 保持（Hold）机器人
- `w` / `s`：前进 / 后退
- `a` / `d`：左移 / 右移
- `q` / `e`：左转 / 右转
- `z`：导航指令清零
- `1` / `2`：升高 / 降低基座高度
- `backspace`（查看器）：在可视化器中重置机器人

---

## 运行遥操作栈

遥操作策略主要使用 Pico 手柄实现手部与身体的协调控制。也支持其他遥操作设备，包括 LeapMotion 以及搭配 Nintendo Switch Joy-Con 手柄的 HTC Vive。

保持 `run_g1_control_loop.py` 运行，并在另一个终端中执行：

```bash
python decoupled_wbc/control/main/teleop/run_teleop_policy_loop.py --hand_control_device=pico --body_control_device=pico
```

### Pico 配置与操控

按照 [XR Robotics 指南](https://github.com/XR-Robotics) 在 Pico 头显上配置遥操作应用。

所需的 PC 端软件已预装在 Docker 容器中，只需 [XRoboToolkit-PC-Service](https://github.com/XR-Robotics/XRoboToolkit-PC-Service) 组件。

前提条件：将 Pico 连接到与主机相同的网络。

手柄按键绑定：
- `menu + 左扳机键`：切换下半身策略
- `menu + 右扳机键`：切换上半身策略
- `左摇杆`：X/Y 平移
- `右摇杆`：偏航旋转
- `左/右扳机键`：控制手部夹持器

Pico 单元测试：

```bash
python decoupled_wbc/control/teleop/streamers/pico_streamer.py
```

---

## 运行数据采集栈

通过部署助手运行完整栈（控制循环、遥操作策略与相机转发器）：

```bash
python decoupled_wbc/scripts/deploy_g1.py \
    --interface sim \
    --camera_host localhost \
    --sim_in_single_process \
    --simulator robocasa \
    --image-publish \
    --enable-offscreen \
    --env_name PnPBottle \
    --hand_control_device=pico \
    --body_control_device=pico
```

该命令会创建 `tmux` 会话 `g1_deployment`，其中包含以下窗格：
- `control_data_teleop`：主控制循环、数据采集与遥操作策略
- `camera`：相机转发器
- `camera_viewer`：可选的实时相机画面

`controller` 窗口（`control_data_teleop` 窗格，左侧）中的操作：
- `]`：激活策略
- `o`：停用策略
- `k`：重置仿真与策略
- `` ` ``：终止 tmux 会话
- `ctrl + d`：退出窗格中的 shell

`data exporter` 窗口（`control_data_teleop` 窗格，右上）中的操作：
- 输入任务指令（task prompt）

Pico 手柄上的操作：
- `A`：开始/停止录制
- `B`：丢弃轨迹
