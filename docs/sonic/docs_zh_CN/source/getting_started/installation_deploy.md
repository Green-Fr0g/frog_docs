# 安装（部署）

## 前提条件

**所有环境均需要：**
- **Ubuntu 20.04/22.04/24.04** 或其他基于 Debian 的 Linux 发行版
- **CUDA Toolkit**（用于 GPU 加速）
- **TensorRT**（用于推理优化）— **请先安装它！**
- **Jetpack 6**（用于机载部署）
- Python 3.8+
- 支持 LFS 的 Git

从 [NVIDIA Developer](https://developer.nvidia.com/tensorrt/download/10x) **下载 TensorRT**：

| 平台 | TensorRT 版本 |
|---|---|
| x86_64（桌面） | **10.13**（必需） |
| Jetson / G1 机载 Orin | **10.7**（必需；需要 JetPack 6 — [刷机指南](../references/jetpack6.md)） |

```{tip}
请下载 **TAR** 包（而非 DEB 包），这样可以把 TensorRT 解压到任意位置。压缩包约 10 GB，建议使用 `pv` 监控下载进度：
```

```{danger}
**必须**使用上表列出的精确 TensorRT 版本。已知使用其他版本会产生错误的推理结果——规划器会输出错误的动作，可能导致危险机器人行为。
```

```sh
sudo apt-get install -y pv
pv TensorRT-*.tar.gz | tar -xz -f -
```

将解压后的 TensorRT 移动到 `~/TensorRT`（或类似位置），并添加到 `~/.bashrc`：

```sh
export TensorRT_ROOT=$HOME/TensorRT
```

## 克隆仓库

```bash
git clone https://github.com/NVlabs/GR00T-WholeBodyControl.git
cd GR00T-WholeBodyControl
git lfs pull          # make sure all large files are fetched
```

## 安装配置

### 原生开发（推荐）

**优点：** 直接安装在系统上，编译更快，可直接用于生产环境。

```{warning}
对于 G1 机载部署，我们要求将 G1 机载 Orin 计算机升级到 Jetpack 6 以支持 TensorRT。请按照[刷机指南](../references/jetpack6.md)进行升级！
```

**前提条件：**
- 基础开发工具（cmake、git 等）
- （可选）如果打算使用基于 ROS2 的输入/输出，则需要 ROS2

**安装步骤：**

1. **安装系统依赖：**

```sh
cd gear_sonic_deploy
chmod +x scripts/install_deps.sh
./scripts/install_deps.sh
```

2. **配置环境：**

```sh
source scripts/setup_env.sh
```

安装脚本会自动：
- 配置 TensorRT 环境
- 设置所有必要的路径

为方便起见，可以把环境配置添加到你的 shell 配置文件中：

```sh
echo "source $(pwd)/scripts/setup_env.sh" >> ~/.bashrc
```

3. **编译项目：**

```sh
just build
```

### Docker（ROS2 开发环境）

我们提供了一个统一的 Docker 环境，内置 ROS2 Humble，支持 x86_64 和 Jetson 平台。

**前提条件：**
- 已安装 Docker，且当前用户已加入 docker 用户组
- 宿主机上已设置 `TensorRT_ROOT` 环境变量
- Jetson 平台：JetPack 6.1+（CUDA 12.6）

**快速配置：**

```sh
# 1. Add user to docker group (one-time setup)
sudo usermod -aG docker $USER
newgrp docker

# 2. Set TensorRT path (add to ~/.bashrc for persistence)
export TensorRT_ROOT=/path/to/TensorRT

# 3. Launch container
cd gear_sonic_deploy
./docker/run-ros2-dev.sh
```

**选项：**

```sh
./docker/run-ros2-dev.sh               # Standard build (fast)
./docker/run-ros2-dev.sh --rebuild     # Force rebuild
./docker/run-ros2-dev.sh --with-opengl # Include OpenGL for visualization (RViz, Gazebo)
```

**架构支持：**
- **x86_64**：CUDA 12.4.1（需要 NVIDIA 驱动 550+）
- **Jetson**：宿主机为 CUDA 12.6 时运行 CUDA 12.4.1 容器（向前兼容）

**容器内操作：**

```sh
source scripts/setup_env.sh # set up dependency
just build                  # Build
just --list                 # Show all commands
```

**故障排除：**
- 如果遇到 "permission denied"，请确认你已加入 docker 用户组
- 必须在**宿主机**上设置好 TensorRT 后再启动容器
- Jetson 平台：先在宿主机上运行 `source scripts/setup_env.sh`（会设置 jetson_clocks）
