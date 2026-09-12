# VR 遥操作配置（PICO）

本页介绍 PICO VR 全身遥操作的一次性硬件与软件配置。完成这些步骤后，请前往 [ZMQ Manager 教程](../tutorials/vr_wholebody_teleop.md)在仿真或真实硬件上运行遥操作。

---

## 所需硬件

- [PICO 4 / PICO 4 Pro 头显](https://www.picoxr.com/global/products/pico4)
- [2 个 PICO 手柄（控制器）](https://www.picoxr.com/global/products/pico4)
- [2 个 PICO 动作追踪器（Motion Tracker）](https://www.picoxr.com/global/products/pico-motion-tracker)（绑在脚踝上）
- 高速、低延迟的 Wi-Fi 连接；遥操作性能在很大程度上取决于网络质量。

---

## 第 1 步：安装 XRoboToolkit

XRoboToolkit 由一个 PC 服务（运行在你的工作站上）和一个 PICO 应用（运行在头显上）组成，用于推流身体追踪数据。

### PC 服务

在 PICO 连接之前，必须先在工作站上安装并运行 PC 服务。

**Ubuntu 22.04（x86_64 工作站）：**

```bash
wget https://github.com/XR-Robotics/XRoboToolkit-PC-Service/releases/download/v1.0.0/XRoboToolkit_PC_Service_1.0.0_ubuntu_22.04_amd64.deb
sudo dpkg -i XRoboToolkit_PC_Service_1.0.0_ubuntu_22.04_amd64.deb
```

**Ubuntu 24.04（x86_64 工作站）：**

```bash
wget https://github.com/XR-Robotics/XRoboToolkit-PC-Service/releases/download/v1.0.0/XRoboToolkit_PC_Service_1.0.0_ubuntu_24.04_amd64.deb
sudo dpkg -i XRoboToolkit_PC_Service_1.0.0_ubuntu_24.04_amd64.deb
```

**Jetson（aarch64，机载）：**

```bash
sudo dpkg -i gear_sonic_deploy/thirdparty/roboticsservice_1.0.0.0_arm64.deb
```

其他平台或更新版本请参见 [XRoboToolkit-PC-Service releases](https://github.com/XR-Robotics/XRoboToolkit-PC-Service/releases)。

### PICO 应用

1. 佩戴 PICO 头显，开始配置与安装流程。
2. 完成 PICO 上的快速设置。
3. 确认 PICO 已连接 Wi-Fi。
4. 打开 PICO 中的浏览器应用。
5. 在搜索栏输入 **"xrobotoolkit"**，选择 GitHub 页面 [https://github.com/XR-Robotics](https://github.com/XR-Robotics)。

```{image} ../_static/pico_setup/google_search_screenshot.png
:width: 600px
:align: center
```

6. 确认 **Developer Mode**（开发者模式）已启用（Settings → Developer）。
7. **【在 PICO 内】** 在 GitHub 页面向下滚动，直到看到 APK 下载选项，用 PICO 扳机键点击下载。

```{tip}
在 PICO 上用浏览器下载 [XRoboToolkit-PICO-1.1.1.apk](https://github.com/XR-Robotics/XRoboToolkit-Unity-Client/releases/download/v1.1.1/XRoboToolkit-PICO-1.1.1.apk)。（[其他版本](https://github.com/XR-Robotics/XRoboToolkit-Unity-Client/releases)）
```

8. **【在 PICO 内】** 打开浏览器页面右上角区域的下载管理选项，点击打开 `XRoboToolkit-PICO-1.1.1.apk` 的下载。
9. **【在 PICO 内】** 选择 **Install**（安装）——该应用将出现在你的媒体库的 **Unknown**（未知来源）分区中。

---

## 第 2 步：动作追踪器配置

```{image} ../_static/pico_setup/pico_setup_screenshot.png
:width: 600px
:align: center
```

1. 将一个 PICO 动作追踪器绑在左脚踝、另一个绑在右脚踝。**收拢（Scrunch）**任何宽松的衣物，确保追踪器可见。确保带指示灯的一面朝上。
2. 进入 PICO 设置。在左侧菜单中向下滚动到最后一项：**"Developer"**（开发者）。确认 **"Safeguard"**（安全防护）已关闭。
   - 如果 Developer 选项未激活，点按 "Software"（软件）直到它出现。
3. 点击 PICO 菜单中的 **Wi-Fi 图标**。会显示头显的画面。在头显上方，会有一个动作追踪器的小圆形图标。如果没有该图标，请打开 **"Motion Tracker"**（动作追踪器）应用本身。
   - 头显和 2 个手柄会出现在列表中——选择 **Motion Tracker**（小圆形图标）。
4. 每个追踪器旁边都有一个 **"i"** 图标。点击它，并**解除所有追踪器的配对（unpair）**。
5. 清除所有追踪器后，点击右上角的 **"Pair"**（配对）按钮。
6. 长按每个动作追踪器顶部的按钮 **6 秒**。进入配对模式后，指示灯会红蓝交替闪烁。

### 动作追踪器校准

1. 将 PICO 头显戴在眼前。
2. 按下蓝色的 **"Calibrate"**（校准）按钮，并依次完成两个校准序列：
   - **序列 1：** 笔直站立，手持控制器垂放在身体两侧。
   - **序列 2：** 低头看向脚上的动作追踪器，直到头显摄像头识别到它们。
3. 校准完成后，将 PICO 头显推到额头处（确保 PICO 仍朝前，以便继续检测动作追踪器）。

---

## 第 3 步：安装 PICO 遥操作环境

在**仓库根目录**下：

```bash
bash install_scripts/install_pico.sh
```

这会创建一个 `.venv_teleop` 虚拟环境（Python 3.10），其中包含：
- `teleop` extra（ZMQ、Pinocchio、PyVista）
- `sim` extra（MuJoCo、tyro）
- XRoboToolkit SDK
- Unitree SDK2 Python 绑定

用以下命令激活：

```bash
source .venv_teleop/bin/activate   # prompt: (gear_sonic_teleop)
```

---

## 第 4 步：将 PICO 连接到你的工作站

1. 在笔记本/PC 和 PICO 上分别打开 Wi-Fi 设置，确保它们位于**同一 Wi-Fi 网络**。记下 Wi-Fi IPv4 地址。
   - 要找到 PICO 的 Wi-Fi，请选择菜单右下角的控制中心。

```{image} ../_static/pico_setup/internet.png
:width: 600px
:align: center
```

```{image} ../_static/pico_setup/pico_vr_screenshot.png
:width: 600px
:align: center
```

2. 打开 **XRoboToolKit** 应用。点击 "PC Service:" 旁边的 **"Enter"**（输入），输入笔记本的 IP 地址。如果 "Status:"（状态）旁边出现 **WORKING**，说明连接正常。
   - 如果 IP 地址已经输入过，请在 Network（网络）区域中 "Status:" 处选择 **"Reconnect"**（重新连接）。

3. 确保下图所示的复选框已被勾选：
   - "Tracking"（追踪）区域下的 **"Head"**（头部）和 **"Controller"**（控制器）。
   - Data/Control 处，确保选中 **"Send"**（发送）按钮。
   - "Pico Motion Tracker" 处，确保选择 **"Full body"**（全身）。

```{image} ../_static/pico_setup/xrrobot_setup.png
:width: 600px
:align: center
```

---

## 后续步骤

PICO 的硬件与软件现已就绪。请前往 [ZMQ Manager（`zmq_manager`）教程](../tutorials/vr_wholebody_teleop.md)，在仿真或真实机器人上运行全身遥操作。
