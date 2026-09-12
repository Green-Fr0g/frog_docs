# 基于 GEM-X 的单相机实时遥操作

用**一个 RGB 相机**遥操作 Unitree G1——无需动捕服、无需 VR 头显、无需身体追踪器。[GEM-X](https://github.com/NVlabs/GEM-X) 从网络摄像头画面中恢复你的全身 3D 运动，本示例将该运动转换为 SMPL 并经 SONIC 的 ZMQ 姿态协议推流（`--input-type zmq`），SONIC 策略在保持机器人平衡的同时对其进行跟踪。

<figure style="margin: 1em 0;">
<video width="100%" controls autoplay loop muted playsinline style="border-radius: 8px;">
  <source src="../_static/live_camera_teleop/teleop_real_robot.mp4" type="video/mp4">
</video>
<figcaption style="text-align: center; font-style: italic; margin-top: 0.5em;">真机 G1 上的网络摄像头实时遥操作——操作员（左侧）仅由一台相机跟踪，无动捕服、无手套、无头显。按照首次硬件会话的推荐，机器人安置在安全龙门架上。</figcaption>
</figure>

```{admonition} 前置条件
:class: note
完成[快速上手](../getting_started/quickstart.md)，使 sim2sim 循环可以运行。本教程驱动的是[流式动作跟踪](zmq.md)中所述的同一接口——如果此前未用过 `--input-type zmq`，请先阅读该页，因为键盘控制与推流协议是共用的。
```

```{admonition} GEM-X 是外部依赖
:class: important
GEM-X **不**随本仓库捆绑发布，也不由任何 SONIC 安装脚本安装。你需要单独安装它，并用 `--gemx-root`（或 `$GEMX_ROOT`）将本示例指向它。GEM-X 采用 Apache-2.0 许可证。
```

---

## 工作原理

```text
  Webcam ──RGB──►  GEM-X rolling window  ──SOMA──►  soma_to_smpl.py
  (1 camera)       YOLOX → ViTPose (2D)   77 joints  SOMA → SMPL, 24 joints
                   → diffusion denoiser              root-local, Z-up
                   → SOMA decoder                            │
                                                             │  ZMQ Protocol v3
                                                             │  topic "pose"
                                                             │  tcp://<gemx-host>:5556
                                                             ▼
                                              SONIC C++ deployment
                                              smpl encoder → WBC policy
                                                             │
                                                             ▼
                                              Unitree G1 (sim or real)
```

| 阶段 | 发生了什么 | 输出 |
|---|---|---|
| 捕获 | OpenCV 从相机读取一帧 | RGB 图像 |
| 检测 + 2D 姿态 | 先 YOLOX 检测，再 ViTPose 关键点（ONNX） | 77 个 2D 关键点 |
| 提升至 3D | GEM-X 扩散去噪器在缓存帧的滚动窗口上运行 | SOMA 潜向量 |
| 解码 | GEM-X 解码器产生身体参数，并融合重力对齐的根朝向 | SOMA 身体参数（77 关节） |
| 转换 | `soma_to_smpl.py` 将 SOMA 映射为 SMPL，从 Y-up 旋转到 Z-up，并去除根旋转 | `smpl_joints`（24×3）、`body_quat` |
| 推流 | ZMQ `PUB` 套接字每帧发送一条 Protocol v3 消息 | topic `pose` 上的线上消息 |
| 跟踪 | SONIC 的 `smpl` 编码器（mode 2）将 SMPL 转为策略所跟踪的潜在指令 | 机器人关节目标 |

### 为什么推流 SMPL 而不是关节角度

SONIC 自带一个在人体 SMPL 运动上训练的 `smpl` 编码器，因此人体到机器人的映射本来就存在于**策略内部**。推流 SMPL 即是把该映射交给编码器，使在线回路中无需任何逐帧重定向或逆运动学求解。

另一种做法——离线将 SOMA 转成 G1 关节角度并推流 Protocol v1——需要在回路中加入重定向器，而这正是计算开销最大的部分。`soma_to_smpl.py` 中的转换与 `gear_sonic/scripts/pico_manager_thread_server.py:process_smpl_joints` 完全一致，因此推流的数据对 PICO 路径所用的同一编码器而言是同分布的。

### 文件

所有内容位于 `gear_sonic/examples/live_camera_teleop/`：

| 文件 | 作用 |
|---|---|
| `webcam_stream.py` | 实时主循环：捕获 → GEM-X → 转换 → 发布。也是相机测试工具。 |
| `soma_to_smpl.py` | SOMA → SMPL 转换与 Protocol v3 ZMQ 发布端。作为模块导入，不直接运行。 |
| `soma_pt_to_sonic_v3.py` | 回放已保存的 GEM-X 结果（`hpe_results.pt`）——无需相机的验证方式。 |
| `README.md` | 本教程的简版参考。 |

---

## 前置条件

1. **SONIC 部署已编译且可运行**——见[安装（部署）](../getting_started/installation_deploy.md)与[快速上手](../getting_started/quickstart.md)，后者也涵盖[下载已发布的检查点](../getting_started/download_models.md)，本路径使用的正是其 `smpl` 编码器。
2. **已安装 GEM-X**——完成克隆、构建其虚拟环境并准备好其检查点。它是一个独立仓库，没有任何 SONIC 安装脚本会替你配置；下方的第 1 步会覆盖这部分。
3. **一个相机**——任何 UVC USB 网络摄像头或笔记本摄像头均可。视频文件可以替代一切，只是缺少实时感。

---

## 第 1 步 — 安装并配置 GEM-X

按照 [GEM-X 安装指南](https://github.com/NVlabs/GEM-X/blob/main/docs/INSTALL.md)操作。简要版本：

```bash
git clone --recursive https://github.com/NVlabs/GEM-X.git
cd GEM-X

pip install uv && uv venv .venv --python 3.12 && source .venv/bin/activate
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
uv pip install -e third_party/soma && (cd third_party/soma && git lfs pull)
bash scripts/install_env.sh
```

此外，本示例在标准 GEM-X 安装之上还需要两件事：

```bash
# 1. SOMA body-model assets must be reachable at inputs/soma_assets
mkdir -p inputs
ln -sfn "$PWD/third_party/soma/assets" inputs/soma_assets

# 2. Extra Python deps for the ZMQ bridge
uv pip install pyzmq scipy
```

```{admonition} soma_assets 链接不可省略
:class: warning
`webcam_stream.py` 会构造 `SomaLayer(data_root="<gemx-root>/inputs/soma_assets")`。缺少该路径时，程序会在转换器启动时失败，而此时相机与去噪器**已经**初始化完毕——表现为一次来得晚且令人费解的崩溃。请在首次实时运行前创建该链接。

请按示例使用**绝对路径**作为链接目标。相对目标会相对于 `inputs/` 而非仓库根目录解析，从而悄悄产生一个悬空链接。
```

GEM-X 首次使用时会从 Hugging Face 下载其检查点，因此首次运行比后续运行慢。

最后，将本示例指向两个仓库。脚本位于 SONIC 仓库中但要导入 GEM-X 的 `gem`，因此它们在 **GEM-X 的虚拟环境**中运行，并通过路径定位 SONIC：

```bash
cd /path/to/GEM-X
source .venv/bin/activate

export GEMX_ROOT=$PWD
export SONIC_ROOT=/path/to/GR00T-WholeBodyControl
```

```{admonition} 为什么必须设置 SONIC_ROOT
:class: note
`soma_to_smpl.py` 中的转换复用了 SONIC 自带的旋转辅助函数（`gear_sonic.isaac_utils.rotations`），以使 SMPL 约定与部署端逐位一致。Python 会将**脚本所在**目录放入 `sys.path`，而非仓库根目录，因此除非设置 `$SONIC_ROOT`（或传入 `--sonic-root`），否则在 GEM-X 环境中无法导入 `gear_sonic`。这些辅助函数只需要 `torch` 和 `numpy`——你**不需要**在 GEM-X 环境中安装 `gear_sonic`。
```

---

## 第 2 步 — 验证输入相机

请在涉及机器人之前完成。`webcam_stream.py` 兼作相机测试工具：`--kp-only` 只运行检测与 2D 关键点而跳过 3D 去噪器，因此启动快且不需要检查点。

### 找到设备

```bash
ls /dev/video*
v4l2-ctl --list-devices                       # sudo apt install v4l-utils
v4l2-ctl -d /dev/video0 --list-formats-ext    # modes the camera actually supports
```

`/dev/videoN` 中的索引就是传给 `--source` 的值（`/dev/video0` → `--source 0`）。许多 USB 相机为同一物理设备暴露多个节点；编号最小的通常才是采集节点。

### 预览跟踪效果

```bash
# Live overlay window, press q to quit
python "$SONIC_ROOT/gear_sonic/examples/live_camera_teleop/webcam_stream.py" \
    --source 0 --kp-only --show
```

你应当看到绿色关键点跟踪你的身体，且状态行上的帧率稳定。请在此阶段解决关键点缺失或跳动的问题——控制器只能跟踪估计器看到的东西。

### 请求采集模式

相机的默认模式往往是低分辨率或低帧率的，这会限制遥操作频率。请从 `--list-formats-ext` 报告的模式中选择一个请求：

```bash
... --source 0 --resolution 1280x720 --cap-fps 30
```

相机会默默忽略不支持的设置，因此脚本会记录它实际协商到的模式。请核对该行输出，而不要想当然认为请求已生效。

(framing)=
### 如何摆放相机与操作员

单目估计只能看到它看得到的东西，而下半身正是控制器赖以平衡的依据：

- 保持**全身入镜，包括双脚。**腿部被裁切会使下半身估计不可靠。
- 大约站在**2–3 m 之外**，相机接近躯干高度，镜头大致水平。
- 光线**均匀且正面照射**。避免强烈逆光。
- **画面中只有一个人**——跟踪的是最大的检测结果。
- **与机器人面朝同一方向。**朝向是以机器人自身坐标系推流的，因此操作员与机器人应当对齐。

---

## 第 3 步 — 无相机干跑

`soma_pt_to_sonic_v3.py` 回放已保存的 GEM-X 结果，将转换与线上格式同一切与相机相关的因素隔离开。先对一段视频运行任意 GEM-X 示例生成 `hpe_results.pt`，然后：

```bash
# Convert frame 0 and print the result — no ZMQ, no robot
python "$SONIC_ROOT/gear_sonic/examples/live_camera_teleop/soma_pt_to_sonic_v3.py" \
    --pt /path/to/hpe_results.pt --dry-run
```

打印出合理的 24 关节骨架后，将其作为流回放给仿真器（先启动下一节的终端 1 和终端 2）：

```bash
python "$SONIC_ROOT/gear_sonic/examples/live_camera_teleop/soma_pt_to_sonic_v3.py" \
    --pt /path/to/hpe_results.pt --fps 30 --loop
```

这是确认 SONIC 一侧接线正确的最快方式，而且可复现——相同输入每次产生相同动作。

---

## 第 4 步 — 仿真中遥操作

运行**三个终端**。

### 终端 1 — MuJoCo 仿真器

在**仓库根目录**：

```bash
source .venv_sim/bin/activate
python gear_sonic/scripts/run_sim_loop.py
```

### 终端 2 — C++ 部署

在 `gear_sonic_deploy/` 下：

```bash
cd gear_sonic_deploy
source scripts/setup_env.sh
./deploy.sh --input-type zmq --zmq-host localhost sim
# Wait until you see "Init done"
```

```{admonition} 此处不要加 --zmq-port 或 --zmq-topic
:class: warning
`deploy.sh` 只转发 `--input-type` 和 `--zmq-host`。端口与 topic 保持部署默认值 `5556` 和 `pose`——恰好就是本示例发布所用的值，因此无需额外旗标。

无法识别的旗标不会被拒绝；`deploy.sh` 会把任何未知参数当作位置参数中的接口参数处理，因此传入 `--zmq-port 5556` 可能会根据参数顺序悄悄覆盖你的 `sim` / `real` 选择。
```

(remote-streamer)=
```{admonition} 在另一台机器上运行 GEM-X
:class: note
本示例**绑定**其 ZMQ `PUB` 套接字（`tcp://*:5556`），部署端则**连接**到它。因此 `--zmq-host` 是运行 `webcam_stream.py` 的机器的 IP，而不是机器人的。两者运行在同一工作站上时保持 `localhost`；部署在机器人机载运行时传入工作站的 IP。
```

### 终端 3 — GEM-X 网络摄像头桥接

在 **GEM-X 仓库**下，激活其环境并导出两个根路径变量（第 1 步）：

```bash
python "$SONIC_ROOT/gear_sonic/examples/live_camera_teleop/webcam_stream.py" \
    --source 0 --stream-sonic --window 30 --smooth 0.8
```

预期输出大致如下：

```text
[webcam] backends: vitpose=..., denoiser=...
[bridge] Using SONIC's pack_pose_message (exact wire format).
[webcam] streaming SMPL v3 to SONIC on tcp://*:5556
[webcam] frame 42 |  12.3 fps | soma=yes
```

有两行值得仔细阅读：

- **`Using SONIC's pack_pose_message`** 确认 `$SONIC_ROOT` 已正确解析。如果你看到的是 `gear_sonic not importable ... using built-in fallback packer`，线上格式仍逐字节一致，但转换需要同样的辅助函数——因此请修复 `$SONIC_ROOT`，而不要依赖回退实现。
- **`soma=yes`** 表示 3D 输出正在流入。前几帧会报告 `warmup/kp-only`，这是滚动窗口在填充。

### 你的第一次会话

三个终端都运行起来后，在终端 2 中操控部署程序：

1. 按 **`]`** 启动控制系统。
2. 在 MuJoCo 窗口中按 **`9`** 让机器人落到地面。
3. 以**放松、直立**的姿态站在相机前，全身入镜。确认终端 3 显示 `soma=yes`。
4. 回到终端 2，按 **`ENTER`** 启用 ZMQ 推流。终端打印 `ZMQ STREAMING MODE: ENABLED`，机器人开始跟踪你。
5. 从**只做缓慢的手臂动作**开始。在移动腿部或躯干之前，先确认机器人以预期方向镜像你的动作。
6. 再按 **`ENTER`** 返回参考动作模式，按 **`O`** 停止并退出。

```{admonition} 启用推流前先对齐姿态
:class: danger
按下 **`ENTER`** 的瞬间，机器人会立刻吸附到正在推流的姿态。机器人当前姿态与你的姿态之间的大幅偏差会产生突然、猛烈的动作——这与 [PICO VR 教程](vr_wholebody_teleop.md)中 POSE 模式所述的风险相同。请保持放松直立，并确认跟踪稳定后，再启用推流。
```

---

## 第 5 步 — 真机上遥操作

```{admonition} 安全警告
:class: danger
只有在仿真中能流畅完成一次会话、并且熟悉急停操作后才能继续。**先终止 `run_sim_loop.py`**——仿真器与真机同时运行会相互冲突。

首次真机会话请将机器人安置在龙门架上，并安排一名安全员值守 **`O`** 键与硬件急停。开始前请先阅读[全身遥操作指南](../user_guide/teleoperation.md)。
```

```{admonition} 预期机器人会向前走
:class: warning
将手臂前伸或做出大幅、快速的手臂动作，会使推流的参考发生足够大的偏移，以至于策略为了保持平衡而向前迈步。在硬件上这意味着机器人会离开其起始位置，而没有任何移动指令被下达——因此请保持机器人前方空间畅通，不要站在其行进路径上，并从贴近身体的小幅手臂动作开始。相关工作正在进行中。
```

真机流程使用**两个终端**（无 MuJoCo）。

### 终端 1 — C++ 部署

在 `gear_sonic_deploy/` 下：

```bash
cd gear_sonic_deploy
source scripts/setup_env.sh

# 'real' auto-detects the robot network interface (192.168.123.x).
# If GEM-X runs on this workstation, localhost is correct:
./deploy.sh --input-type zmq --zmq-host localhost real

# If the deployment runs onboard and GEM-X is on a workstation,
# point it at the workstation:
#   ./deploy.sh --input-type zmq --zmq-host <workstation-IP> real

# Wait until you see "Init done"
```

### 终端 2 — GEM-X 网络摄像头桥接

与仿真情形完全相同：

```bash
cd /path/to/GEM-X && source .venv/bin/activate
export GEMX_ROOT=$PWD SONIC_ROOT=/path/to/GR00T-WholeBodyControl

python "$SONIC_ROOT/gear_sonic/examples/live_camera_teleop/webcam_stream.py" \
    --source 0 --stream-sonic --window 30 --smooth 0.8
```

然后遵循同样的流程：**`]`** 启动，跟踪稳定后按 **`ENTER`** 启用推流，按 **`O`** 停止。

---

## 控制参考

所有按键均在 **C++ 部署终端**中按下，并与[流式动作跟踪](zmq.md)共用。

| 按键 | 动作 |
|---|---|
| **`]`** | 启动控制系统 |
| **`ENTER`** | 开 / 关 ZMQ 推流模式（相机跟踪） |
| **`Q`** / **`E`** | 向左 / 向右调整朝向（每次按压 ±0.1 rad） |
| **`I`** | 重新初始化基座四元数并将朝向重置为零 |
| **`T`** / **`N`** / **`P`** / **`R`** | 参考动作回放（推流模式关闭时） |
| **`O`** | **急停**——停止控制并退出 |

---

## 命令行参考

### `webcam_stream.py`

| 选项 | 默认值 | 说明 |
|---|---|---|
| `--source` | `0` | 相机索引（`ls /dev/video*`）或视频文件路径 |
| `--stream-sonic` | 关 | 发布 Protocol v3 SMPL 推流。不加则不会向 SONIC 发送任何内容。 |
| `--window` | `120` | 滚动窗口长度（帧）。决定帧率的主导因素——见[调参](#tuning)。 |
| `--smooth` | `0.75` | 推流参考的时域平滑权重（`0` = 关闭） |
| `--port` | `5556` | 要绑定的 ZMQ `PUB` 端口。与部署默认值匹配；要么都改，要么都不改。 |
| `--resolution` | 相机默认 | 请求的采集分辨率，如 `1280x720` |
| `--cap-fps` | 相机默认 | 请求的采集帧率 |
| `--kp-only` | 关 | 仅 2D 关键点——跳过去噪器。用于相机检查。 |
| `--show` / `--save` | 关 | 实时预览窗口 / 写出叠加效果的 mp4 |
| `--max-frames` | `0` | 处理 N 帧后停止（`0` = 运行到被中断为止） |
| `--gemx-root` | `$GEMX_ROOT` | GEM-X 仓库根目录 |
| `--sonic-root` | `$SONIC_ROOT` | SONIC 仓库根目录（见第 1 步） |

### `soma_pt_to_sonic_v3.py`

| 选项 | 默认值 | 说明 |
|---|---|---|
| `--pt` | *必填* | 已保存的 GEM-X `hpe_results.pt` 路径 |
| `--fps` | `30` | 回放速率 |
| `--loop` | 关 | 连续回放 |
| `--dry-run` | 关 | 转换第 0 帧，打印后退出——不使用 ZMQ |
| `--smooth` | `0.0` | 时域平滑（默认关闭，与实时路径不同） |
| `--port` / `--max-frames` / `--gemx-root` / `--sonic-root` | — | 同上 |

---

(tuning)=
## 调参：帧率与稳定性的权衡

去噪器每帧都要在整个缓存窗口上运行，因此计算开销随 `--window` 增长，直至缓存填满。这使 `--window` 成为吞吐量的主要旋钮。

| 症状 | 尝试 |
|---|---|
| 帧率过低 | 调低 `--window`（如 `30` → `20`）；用 `--resolution` / `--cap-fps` 请求更轻量的采集模式 |
| 机器人抖动或迈出细碎步伐 | 将 `--smooth` 提高到接近 `0.85`；改善光照与[取景](#framing) |
| 机器人感觉迟滞、"跟不上"你 | 调低 `--smooth`，调低 `--window`，并放慢动作节奏 |
| 腿部或脚部看起来不对 | 几乎总是取景问题——让双脚完整入镜并站得更远 |
| 机器人在朝向上漂移 | 按 **`I`** 重新初始化基座四元数，再用 **`Q`** / **`E`** 微调 |

从 `--window 30 --smooth 0.8` 开始，每次只调一个旋钮。

---

## 故障排除

| 症状 | 原因 / 解决方法 |
|---|---|
| `Could not open video source: 0` | 索引错误（`ls /dev/video*`），或用户不在 `video` 组（`sudo usermod -aG video $USER`，然后重新登录） |
| 能打开，但取帧失败或卡住 | 另一进程占用了设备（浏览器标签页、之前的运行）。用 `sudo fuser /dev/video0` 检查 |
| `ModuleNotFoundError: No module named 'gear_sonic'` | `$SONIC_ROOT` 未设置或不正确——见第 1 步 |
| `ModuleNotFoundError: No module named 'gem'` | 在错误的环境中运行。请激活 GEM-X 的 `.venv`，而非 SONIC 的。 |
| 转换器启动时崩溃，报错涉及 SOMA 资源 | `inputs/soma_assets` 链接缺失或悬空——见第 1 步 |
| 关于 `identity_coeffs` / `scale_params` 的 `KeyError` | SOMA 解码不完整；这些参数没有安全的零默认值，因此桥接端宁可拒绝推流一个坍缩的骨架，也不向控制器发送垃圾数据 |
| 按 **`ENTER`** 后机器人始终不动 | 没有消息到达。检查终端 3 是否打印 `soma=yes`、`--zmq-host` 是否指向运行 GEM-X 的机器，以及端口 `5556` 是否可达 |
| 帧率极低 | 相机协商到了慢速模式，或 `--window` 过大——见[调参](#tuning) |
| 无头机器上 `--show` 失败 | 没有显示器；改用 `--save` |
| 检测不到关键点 | 身体未完整入镜、太暗或距离太远 |

---

## 局限性

- **不支持指令式的根平移。**推流内容是根坐标系下姿态加朝向，不含显式的根平移，因此"自己走带动机器人走"不受支持。可结合[运动学规划器](keyboard.md)实现移动，将相机用于上半身动作。
- **手腕与手指不被跟踪。**`smpl_pose` 与 6 个腕部关节以零值推流。GEM-X 本身会估计手部，将它们接入是自然的扩展方向。
- **机器人会为保持平衡而向前走。**某些手臂动作——前伸手臂或大幅、快速的挥臂——会使推流的参考偏移得足够远，以至于策略为了保持直立而迈步。即使没有下达任何移动指令，机器人也会偏离起始位置。相关工作正在进行中。
- **单目下半身是最弱的信号。**仅凭一台相机，脚部与深度天然不如追踪器可靠，而这恰恰是控制器赖以平衡的部分。取景在这里比任何参数都重要。
- **单主体、固定相机。**跟踪的是最大的检测结果，且整个回路假设相机固定不动。

---

## 后续步骤

- [流式动作跟踪](zmq.md)——底层 ZMQ 接口与完整协议参考
- [PICO VR 全身遥操作](vr_wholebody_teleop.md)——基于追踪器的遥操作，可作对比
- [全身遥操作指南](../user_guide/teleoperation.md)——运动模式与操作规范
- [面向 VLA 的数据采集](data_collection.md)——将遥操作会话录制为训练数据
