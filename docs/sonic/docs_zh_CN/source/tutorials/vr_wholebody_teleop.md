# PICO VR 全身遥操作

使用 PICO VR 头显与手柄进行完整的全身遥操作。进行遥操作时，部署期间使用 `--input-type zmq_manager` 选项。`zmq_manager` 输入类型在**规划器模式**（通过 ZMQ 发送移动指令）与**流式动作模式**（来自 PICO 的全身 SMPL 姿态）之间切换。

## SONIC 低延迟

下面的序列展示了 SONIC 低延迟在全身遥操作模式下的运行情况，包括一次成功的地面拾取。

```{image} ../_static/sonic_low_latency_demo.gif
:alt: SONIC 低延迟全身遥操作与地面拾取
:width: 640px
:align: center
```

```{admonition} Isaac Teleop / CloudXR 适用范围
:class: note
同样的 `zmq_manager` 工作流也可以通过 Isaac Teleop / CloudXR 驱动头显，方法是启动 `gear_sonic/scripts/pico_manager_thread_server.py --input-source isaac-teleop`。推流端通过 `isaacteleop[cloudxr]` 在进程内承载 CloudXR 运行时——无需单独的发布端容器。该路径目前仅支持**配备 Thor 背包的 G1**；普通 G1 配置尚不支持。
```

```{admonition} 安全警告
:class: danger
全身遥操作涉及快速、灵敏的动作。请**务必**保持安全区畅通无阻，并让一名安全员守在键盘旁，随时准备触发急停（在 C++ 终端按 **`O`**，或在 PICO 手柄上按 **A+B+X+Y**）。

你**必须穿紧身裤或打底裤**，以保证脚部跟踪器的视线不被遮挡——宽松的衣物可能使跟踪不可预测地失效，并可能导致危险动作。
```

```{video} ../_static/teleop/teleop_session_overview.mp4
:width: 100%
```
*视频：端到端遥操作完整流程——PICO 校准、策略接管，以及机器人独立保持平衡。详细最佳实践参见[遥操作指南](../user_guide/teleoperation.md)。*

## 先决条件

1. **已完成[快速上手](../getting_started/quickstart.md)** ——你能跑通 sim2sim 循环（包括[安装部署环境](../getting_started/installation_deploy.md)与[下载模型检查点](../getting_started/download_models.md)）。
2. **已完成[VR 遥操作环境搭建](../getting_started/vr_teleop_setup.md)** ——`.venv_teleop` 已就绪。默认路径下，PICO 硬件已安装、校准并连接。Isaac Teleop / CloudXR 路径下，还需安装 `isaacteleop[cloudxr]` 包（由 `install_pico.sh` 处理），头显连接到进程内 CloudXR 运行时——参见[Isaac Teleop 环境搭建](isaac_teleop_publisher_setup.md)。

---

## 分步操作：在仿真中遥操作

运行**三个终端**来遥操作仿真机器人。

### 终端 1 —— 在 MuJoCo 仿真器中启动虚拟机器人

在**仓库根目录**：

```bash
# bash install_scripts/install_pico.sh

source .venv_teleop/bin/activate
python gear_sonic/scripts/run_sim_loop.py
```

### 终端 2 —— C++ 部署

在 `gear_sonic_deploy/` 目录：

```bash
cd gear_sonic_deploy
source scripts/setup_env.sh
./deploy.sh --input-type zmq_manager sim
# 等待看到 "Init done"
```

**Isaac Teleop / CloudXR 替代方案**（**仅限 G1 + Thor 背包**）——改从项目的 ROS2 docker 容器中运行 C++ 部署，而非裸机：

```bash
cd gear_sonic_deploy
export TensorRT_ROOT=$HOME/TensorRT   # 仅当尚未写入 ~/.bashrc 时需要
./docker/run-ros2-dev.sh

# 容器内（setup_env.sh 会被自动 source）：
just build                                  # 仅首次运行需要
./deploy.sh --input-type zmq_manager sim
# 等待看到 "Init done"
```

关于 `run-ros2-dev.sh` 与 `TensorRT_ROOT` 的详情，参见[安装（部署）→ Docker（ROS2 开发环境）](../getting_started/installation_deploy.md)。

```{note}
`--zmq-host` 旗标默认为 `localhost`，当 C++ 部署脚本与遥操作脚本（终端 3）在同一台机器上运行时，这就是正确的值。如果遥操作脚本在另一台机器上运行，请传入 `--zmq-host <IP-of-teleop-machine>`。
```

### 终端 3 —— PICO 遥操作推流端

在**仓库根目录**：

```bash
source .venv_teleop/bin/activate

# 开启完整可视化（首次运行推荐）：
python gear_sonic/scripts/pico_manager_thread_server.py --manager \
    --vis_vr3pt --vis_smpl

# 不开可视化（无头 / 机载演练用）：
# python gear_sonic/scripts/pico_manager_thread_server.py --manager
```

**Isaac Teleop / CloudXR 替代方案**（**仅限 G1 + Thor 背包**）——通过 CloudXR 连接头显（无需 XRoboToolKit PC 服务）；推流端通过 `isaacteleop[cloudxr]` 在进程内启动 CloudXR 运行时：

```bash
source .venv_teleop/bin/activate

python gear_sonic/scripts/pico_manager_thread_server.py --manager \
    --input-source isaac-teleop

# 如在机外带显示器运行，可添加可视化：
#   --vis_vr3pt --vis_smpl
```

开启可视化后，等待窗口弹出，其中显示所有关节处于默认角度的 Unitree G1 网格模型。如果默认 PICO 路径下没有窗口出现，请在[VR 遥操作环境搭建](../getting_started/vr_teleop_setup.md)中复查 PICO 的 XRoboToolKit IP 配置。如果你使用的是 Isaac Teleop，请确认头显已连接到进程内 CloudXR 运行时——连接步骤参见[Isaac Teleop 环境搭建](isaac_teleop_publisher_setup.md)。

### 你的第一次遥操作会话

1. **摆出校准姿态** ——身体站直，双脚并拢，上臂自然下垂于身体两侧，前臂向前弯曲 90°（肘部呈 L 形），掌心朝内。详见[校准姿态](#calibration-pose)。
2. 同时按下 **A + B + X + Y**，接管控制策略并执行首次完整校准（`CALIB_FULL`）。
3. 将手臂对齐到机器人当前姿态，然后按下 **A + X** 进入全身 SMPL 遥操作（**POSE** 模式）。活动手臂和腿——机器人会跟随。
4. 再次按下 **A + X** 回退到 **PLANNER**（待机）模式。
5. 再次按下 **A + B + X + Y** 停止机器人。

<figure style="margin: 1em 0;">
<video width="100%" autoplay loop muted playsinline style="border-radius: 8px;">
  <source src="../_static/teleop_calib/basic_flow_web.mp4" type="video/mp4">
</video>
<figcaption style="text-align: center; font-style: italic; margin-top: 0.5em;">基础全身遥操作流程：校准姿态 → 接管 → POSE 模式 → PLANNER 待机 → 停止。</figcaption>
</figure>

---

(pico-controls)=

## PICO 完整按键说明

### 模式与校准

系统有 **4 种运行模式**和 **2 种校准类型**。

**模式：**

| 模式 | 编码器 | 描述 |
|---|---|---|
| **OFF** | -- | 策略未运行。摆好[校准姿态](#calibration-pose)，然后按 **A+B+X+Y** 启动策略。 |
| **POSE** | SMPL | 全身遥操作——将 PICO 的 SMPL 姿态流式传输到 C++ 部署侧。你的动作会直接映射到机器人身上。 |
| **PLANNER** | G1 | 移动规划器激活；上半身由规划器控制。在行走与奔跑模式下，摇杆控制方向与朝向。 |
| **PLANNER_FROZEN_UPPER** | G1 | 规划器移动；上半身冻结在最后一次 POSE 快照。 |
| **VR_3PT** | TELEOP | 规划器移动；上半身跟随 VR 三点跟踪（头 + 双手）。依赖于基于非 IK 的 VR 三点校准。 |

**校准类型**（非 IK 工作流，延迟最小）：

| 类型 | 校准内容 | 触发时机 |
|---|---|---|
| **CALIB_FULL** | 头部 + 双腕，以**全零**参考姿态为基准。 | 首次按下 **A+B+X+Y**（启动）时执行一次。 |
| **CALIB** | 仅双腕，以**机器人当前姿态**为基准。 | 每次通过**左摇杆按下（Left Stick Click）**切入 VR_3PT 时。 |

### 状态机

系统有 4 种模式和 2 条控制链路。每条链路构成一个三角形：**A+X**（或 **B+Y**）可从*规划器节点*及其 VR_3PT 子模式二者返回 POSE。

```text
  ┌──────────────────────────────────────┐
  │  A+B+X+Y (any mode) ──► OFF          │
  └──────────────────────────────────────┘

  Startup:
    OFF ──(A+B+X+Y)──► PLANNER ──(A+X)──► POSE
          CALIB_FULL

  Chain 1 — G1 encoder listens to planner-generated full-body motion: PLANNER

    PLANNER ─── L-Stick (+CALIB) ──► VR_3PT
     ▲    │ ◄─────── L-Stick ─────────  │
     │    │                             │
     │A+X │A+X                    A+X   │
     │    ▼                             ▼
     └─ POSE ◄──────────────────────────┘

  Chain 2 — G1 encoder listens to planner-generated lower-body motion: PLANNER_FROZEN_UPPER

    PLANNER_FROZEN_UPPER ── L-Stick (+CALIB) ──► VR_3PT
         ▲     │ ◄──────── L-Stick ──────────     │
         │     │                                  │
         │B+Y  │B+Y                          B+Y  │
         │     ▼                                  ▼
         └── POSE ◄───────────────────────────────┘
```

```{admonition} 危险——模式切换安全
:class: danger
**在切换到 POSE 或 VR_3PT 之前**，务必先将身体对齐到机器人当前姿态！！

- **POSE：** 机器人会瞬间对齐到你的身体姿态。差异过大会导致突然而剧烈的动作。
- **VR_3PT：** 校准未对齐时，你一移动手臂机器人就会出现紊乱的危险动作。更多信息参见[单次切换校准](#per-switch-calib)一节。
```

(calibration-pose)=

### VR_3PT 校准提示

`VR_3PT` 模式依赖准确的校准。校准事件有两种：

#### 一次性 `CALIB_FULL`（头部 + 双腕）

首次按下 **A + B + X + Y** 之前，你**必须**以机器人的**全零参考姿态**站立。系统会把你的 PICO 身体跟踪帧捕获为零参考，作为后续所有动作映射的基准。

**参考姿态：**
1. **身体站直**，双脚并拢，目视正前方。
2. **上臂**自然下垂，贴近躯干。
3. **前臂**向前弯曲 90°（肘部呈 L 形），掌心朝内。

```{tip}
用 `--vis_vr3pt` 启动遥操作脚本，可在可视化窗口中看到机器人的参考姿态。按下启动组合键之前，先让自己的身体与之对齐。
```

(per-switch-calib)=
#### 每次切换时的 `CALIB`（仅双腕）

每次通过**左摇杆按下（Left Stick Click）**进入 `VR_3PT` 时，系统都会以机器人**当前**姿态为基准重新校准双腕。按下之前，务必先将手臂与机器人对齐。

下面是一个**错误校准做法**的示例——未将手臂对齐机器人当前姿态就切入 VR_3PT。机器人可能不会立即跳动，但你一动就会出现紊乱的危险动作。

<figure style="margin: 1em 0;">
<video width="100%" autoplay loop muted playsinline style="border-radius: 8px;">
  <source src="../_static/teleop_calib/BAD_Calib_VR3PT_web.mp4" type="video/mp4">
</video>
<figcaption style="text-align: center; font-style: italic; margin-top: 0.5em;">错误做法：未对齐手臂就进入 VR_3PT，会导致紊乱、不安全的动作。</figcaption>
</figure>




```{admonition} 危险——模式切换安全
:class: danger
**在切换到 POSE 或 VR_3PT 之前**，务必先将身体对齐到机器人当前姿态。

**从错误的 VR_3PT 校准中恢复：**
1. 冻结上半身——通过**左摇杆按下（Left Stick Click）**切回。
2. 将手臂重新对齐到机器人当前（可能已扭曲）的姿态。
3. 切换到 **POSE** 模式（**A+X**）以重置。
```

下面是**恢复流程**——如果你意外进入了校准不良的 VR_3PT 状态，先冻结上半身（左摇杆按下切回），再切换到 POSE 模式（A+X）安全重置。

<figure style="margin: 1em 0;">
<video width="100%" autoplay loop muted playsinline style="border-radius: 8px;">
  <source src="../_static/teleop_calib/BAD_Calib_VR3PT_recover_web.mp4" type="video/mp4">
</video>
<figcaption style="text-align: center; font-style: italic; margin-top: 0.5em;">从错误的 VR_3PT 校准中恢复：冻结上半身 → 重新对齐 → 切换到 POSE 模式。</figcaption>
</figure>

### 快速上手速查表

| 操作 | 按键 | 说明 |
|---|---|---|
| **启动 / 停止策略** | **A+B+X+Y** | 首次按下：接管 + CALIB_FULL。再次按下：急停 → OFF。 |
| **切换 POSE** | **A+X** | 在 PLANNER ↔ POSE 之间切换；或从（经 PLANNER 进入的）VR_3PT → POSE。 |
| **切换 PLANNER_FROZEN_UPPER** | **B+Y** | 在 POSE ↔ PLANNER_FROZEN_UPPER 之间切换；或从（经 PLANNER_FROZEN_UPPER 进入的）VR_3PT → POSE。 |
| **切换 VR_3PT** | **Left Stick Click** | 从任意规划器模式 → VR_3PT（触发 CALIB）。再次按下返回。 |
| **手部抓握** | **Trigger**（每只手） | 控制对应手部的抓握。 |

### 摇杆控制（规划器模式）

在 **PLANNER**、**PLANNER_FROZEN_UPPER** 和 **VR_3PT** 中生效：

| 输入 | 功能 |
|---|---|
| **Left Stick** | 移动方向（前进 / 后退 / 横移） |
| **Right Stick (horizontal)** | 偏航 / 朝向（连续累积） |
| **A + B** | 下一个移动模式 |
| **X + Y** | 上一个移动模式 |

**移动模式**（通过 A+B / X+Y 循环切换）：

| ID | 模式 |
|---|---|
| 0 | 待机 [DEFAULT] |
| 1 | 慢走 |
| 2 | 行走 |
| 3 | 奔跑 |
| 4 | 下蹲 |
| 5 | 双膝跪地 |
| 6 | 单膝跪地 |
| 7 | 俯卧 |
| 8 | 手膝爬行 |
| 9–16 | 拳击变体（待机、行走、直拳、勾拳） |
| 17 | 前跳 |
| 18 | 潜行 |
| 19 | 负伤行走 |

---

## 紧急停止（急停）

| 方式 | 操作 |
|---|---|
| **PICO 手柄** | 同时按下 **A+B+X+Y** → OFF |
| **键盘**（C++ 终端） | 按下 **`O`** 立即停止 |

---

## 分步操作：在真机上遥操作

```{admonition} 安全警告
:class: danger
只有在仿真中能够流畅控制机器人、并且能熟练执行急停之后才可继续。**先终止所有正在运行的 `run_sim_loop.py` 进程**——仿真与真机实例同时运行会相互冲突。
```

真机工作流使用**两个终端**（无 MuJoCo 仿真器）。

### 终端 1 —— C++ 部署（真机）

在 `gear_sonic_deploy/` 目录：

```bash
cd gear_sonic_deploy
source scripts/setup_env.sh

# 'real' 会自动探测机器人的网络接口（192.168.123.x）。
# 如果自动探测失败，直接传入 G1 的 IP：
#   ./deploy.sh --input-type zmq_manager <G1-IP>
./deploy.sh --input-type zmq_manager real

# 等待看到 "Init done"
```

**Isaac Teleop / CloudXR 替代方案**（**仅限 G1 + Thor 背包**）——改从项目的 ROS2 docker 容器中运行 C++ 部署，而非裸机：

```bash
cd gear_sonic_deploy
export TensorRT_ROOT=$HOME/TensorRT   # 仅当尚未写入 ~/.bashrc 时需要
./docker/run-ros2-dev.sh

# 容器内（setup_env.sh 会被自动 source）：
just build                                   # 仅首次运行需要
./deploy.sh --input-type zmq_manager real
# 等待看到 "Init done"
```

```{note}
如果遥操作脚本（终端 2）在另一台机器上运行，请添加 `--zmq-host <IP-of-teleop-machine>`，让 C++ 侧知道 ZMQ 发布端在哪里。
```

### 终端 2 —— PICO 遥操作推流端

在**仓库根目录**：

```bash
# bash install_scripts/install_pico.sh

source .venv_teleop/bin/activate
python gear_sonic/scripts/pico_manager_thread_server.py --manager

# 如在机外带显示器运行，可添加可视化：
#   --vis_vr3pt --vis_smpl
```

**Isaac Teleop / CloudXR 替代方案**（**仅限 G1 + Thor 背包**）——通过 `isaacteleop[cloudxr]` 使用进程内 CloudXR 运行时，无需 XRoboToolKit PC 服务：

```bash
source .venv_teleop/bin/activate
python gear_sonic/scripts/pico_manager_thread_server.py --manager --input-source isaac-teleop
```

```{note}
启动默认 PICO 路径之前，请先在 PICO 的 XRoboToolKit 应用中将 IP 更新为本机地址。对于 Isaac Teleop，请确保头显已连接到进程内 CloudXR 运行时——参见[Isaac Teleop 环境搭建](isaac_teleop_publisher_setup.md)。
```

按照相同的启动顺序：校准姿态 → **A+B+X+Y** → 按 **A+X** 进入 POSE 模式。所有可用指令参见[PICO 完整按键说明](#pico-controls)。
