# 流式动作跟踪

通过 ZMQ 向机器人流式传输动作数据，用于参考动作跟踪。该接口支持从任意外部源（`--input-type zmq`）流式传输**基于 SMPL 的姿态**（例如来自 PICO）或 **G1 全身关节位置**（qpos）。

```{admonition} 先决条件
:class: note
先完成[快速上手](../getting_started/quickstart.md)，使 sim2sim 循环处于运行状态。
```

```{admonition} 紧急停止（急停）
:class: danger
任何时候按下 **`O`** 即可立即停止控制并退出。请始终让一只手放在键盘附近，随时准备按下 **`O`**。
```

## 启动

**Sim2Sim（MuJoCo）：**

```bash
# 终端 1 —— MuJoCo 仿真器（在仓库根目录）
source .venv_sim/bin/activate
python gear_sonic/scripts/run_sim_loop.py

# 终端 2 —— C++ 部署（在 gear_sonic_deploy/ 目录）
bash deploy.sh --input-type zmq \
  --zmq-host <publisher-ip> \
  --zmq-port 5556 \
  --zmq-topic pose \
  sim
```

**真机：**

```bash
# 在 gear_sonic_deploy/ 目录
bash deploy.sh --input-type zmq \
  --zmq-host <publisher-ip> \
  --zmq-port 5556 \
  --zmq-topic pose \
  real
```

## 操作步骤

1. 按下 **`]`** 启动控制系统。
2. 默认处于**参考动作模式**——用 **`T`** 播放动作，**`N`** / **`P`** 切换，**`R`** 重新开始（与[键盘接口](keyboard.md)相同）。
3. 按下 **`ENTER`** 切换到 **ZMQ 流式传输模式**。终端会打印 `ZMQ STREAMING MODE: ENABLED`。
4. 此时策略会实时跟踪从 ZMQ 发布端到达的动作帧。回放自动开始。
5. 再次按下 **`ENTER`** 切换回参考动作。终端会打印 `ZMQ STREAMING MODE: DISABLED`，编码模式重置为 `0`（基于关节）。
6. 在两种模式下，均可用 **`Q`** / **`E`** 调整朝向（每次 ±0.1 rad）。
7. 按下 **`I`** 重新初始化基座四元数，并把朝向重置为零。
8. 结束后，按下 **`O`** 停止控制并退出。

```{note}
**不支持规划器** —— 该接口仅使用预加载的和 ZMQ 流式传输的参考动作。如需规划器 + ZMQ 控制（例如 PICO VR 遥操作），请改用 `--input-type zmq_manager`。参见[VR 全身遥操作教程](vr_wholebody_teleop.md)。
```

```{tip}
**构建你自己的推流源。** 下文描述的 ZMQ 流协议是自包含的——任何按该格式发送消息的发布端都可以驱动机器人。你可以编写自己的动作捕捉重定向流水线、仿真器桥接器，或任何其他能产生所需字段的数据源。无需 PICO 硬件。
```

## 与 PICO VR 遥操作配合使用

你可以将 `--input-type zmq` 与 PICO 遥操作推流端配合使用，搭建一个简单的、仅流式传输的全身遥操作系统。在该模式下，PICO 通过 ZMQ 推流全身 SMPL 姿态，部署侧直接跟踪这些姿态——没有移动规划器，也不通过 PICO 按键切换模式。所有控制都通过键盘完成。

### 先决条件

1. **已完成[快速上手](../getting_started/quickstart.md)** ——你能跑通 sim2sim 循环。
2. **PICO VR 硬件已就绪** ——头显与手柄已连接，身体跟踪正常工作，且 `.venv_teleop` 已安装。安装与校准参见[VR 遥操作环境搭建](../getting_started/vr_teleop_setup.md)。

### 启动（Sim2Sim）

运行三个终端：

**终端 1 —— MuJoCo 仿真器**（在仓库根目录）：

```bash
source .venv_sim/bin/activate
python gear_sonic/scripts/run_sim_loop.py
```

**终端 2 —— C++ 部署**（在 `gear_sonic_deploy/` 目录）：

```bash
bash deploy.sh --input-type zmq \
  --zmq-host localhost \
  --zmq-port 5556 \
  --zmq-topic pose \
  sim
```

**终端 3 —— PICO 遥操作推流端**（在仓库根目录）：

```bash
source .venv_teleop/bin/activate

# 开启可视化（首次运行推荐）：
python gear_sonic/scripts/pico_manager_thread_server.py \
    --manager --vis_smpl --vis_vr3pt

# 不开可视化（无头模式）：
# python gear_sonic/scripts/pico_manager_thread_server.py --manager
```

### 启动（真机）

运行两个终端（无 MuJoCo）：

**终端 1 —— C++ 部署**（在 `gear_sonic_deploy/` 目录）：

```bash
bash deploy.sh --input-type zmq \
  --zmq-host <teleop-machine-ip> \
  --zmq-port 5556 \
  --zmq-topic pose \
  real
```

如果 PICO 推流端运行在同一台机器上，请将 `<teleop-machine-ip>` 替换为 `localhost`；否则替换为运行终端 2 的机器的 IP。

**终端 2 —— PICO 遥操作推流端**（在仓库根目录）：

```bash
source .venv_teleop/bin/activate
python gear_sonic/scripts/pico_manager_thread_server.py --manager
```

### 操作步骤

1. **校准姿态**：身体站直，双脚并拢，上臂自然下垂于身体两侧，前臂向前弯曲 90°（肘部呈 L 形），掌心朝内。
2. 在 PICO 手柄上同时按下 **A + B + X + Y**，初始化并校准身体跟踪。
3. 在 PICO 手柄上按下 **A + X**，开始推流姿态。
4. 在终端 2（C++ 部署）中，按下 **`]`** 启动控制系统。
5. 在 MuJoCo 窗口（仅仿真）中，按下 **`9`** 让机器人落到地面。
6. 回到终端 2，按下 **`ENTER`** 启用 ZMQ 流式传输。终端打印 `ZMQ STREAMING MODE: ENABLED`。机器人开始实时跟踪你的 PICO 姿态。
7. 活动身体——机器人会镜像你的动作。用每个 PICO 手柄上的 **Trigger**（扳机）按键闭合对应的机器人手。
8. 要**暂停**推流（例如为了调整站位），再次按下 **`ENTER`**。终端打印 `ZMQ STREAMING MODE: DISABLED`。机器人保持其最后的姿态并停止跟踪。你可以自由移动而不影响机器人。
9. 要**恢复**，再按一次 **`ENTER`**。机器人会瞬间对齐到你的当前姿态——恢复前请**先回到接近机器人当前姿态的位置**，以避免突然跳动。
10. 结束后，按下 **`O`** 停止控制并退出。

```{admonition} 危险——从暂停中恢复
:class: danger
当你在暂停后按下 **`ENTER`** 恢复推流时，机器人会立即尝试到达你当前的身体姿态。如果你的身体与机器人姿态相差很大，机器人可能做出突然而剧烈的动作。**按下 `ENTER` 恢复之前，务必先回到接近机器人当前姿态的位置。**
```

### ZMQ 模式下的 PICO 按键

在 `--input-type zmq` 模式下，C++ 部署侧**不会**直接处理 PICO 手柄的按键组合。但这些按键仍会影响 **Python 推流端**，而后者决定 `pose` ZMQ topic 上发布哪些数据。由于部署侧会跟踪该 topic 上到达（或停止到达）的任何数据，若干按键仍会对机器人产生间接影响。

| PICO 按键 | 效果 |
|-------------|--------|
| **A + B + X + Y** | 在推流端校准身体跟踪。按一次初始化；再按一次停止推流（推流端侧的急停）。 |
| **A + X** | 切换推流端的 Pose 模式——开始或停止发布姿态数据。停止后机器人保持最后的姿态。**相当于暂停/恢复。** |
| **Menu（按住）** | 按住期间暂停推流端的姿态推流。在你松开之前，机器人一直保持最后的姿态。**相当于暂停。** 松开前请先回到接近机器人当前姿态的位置。 |
| **Trigger** | 手部抓握——由推流端处理，并以 `left_hand_joints` / `right_hand_joints` 的形式随流发送。 |
| **B + Y** | 切换推流端的 Pose 模式（与 A+X 效果相同）——开始或停止发布姿态数据。**相当于暂停/恢复。** |

部署侧的所有模式控制都通过键盘完成：

| 按键 | 操作 |
|-----|--------|
| **`]`** | 启动控制系统 |
| **`ENTER`** | 切换流式传输开/关（暂停/恢复） |
| **`O`** | 急停——停止控制并退出 |
| **`I`** | 重新初始化基座四元数并重置朝向 |
| **`Q`** / **`E`** | 调整朝向（±0.1 rad） |
| **`F`** | 报告电机温度（TTS 语音播报） |

```{note}
如需带规划器支持、移动模式和基于 PICO 手柄模式切换的完整 PICO VR 体验，请改用 `--input-type zmq_manager`。参见[VR 全身遥操作教程](vr_wholebody_teleop.md)。
```

## 控制按键

| 按键 | 操作 |
|-----|--------|
| **]** | 启动控制系统 |
| **O** | 停止控制并退出（急停） |
| **ENTER** | 在参考动作与 ZMQ 流式传输之间切换 |
| **I** | 重新初始化基座四元数并重置朝向 |
| **Q** / **E** | 向左 / 向右调整朝向增量（±0.1 rad） |
| **F** | 报告电机温度（TTS 语音播报） |

*仅参考动作模式（未推流）时：*

| 按键 | 操作 |
|-----|--------|
| **T** | 播放当前动作至结束 |
| **R** | 从头重新播放当前动作（停在第 0 帧） |
| **P** / **N** | 上一个 / 下一个动作序列 |

## 流协议版本

编码模式由 ZMQ 流协议版本自动确定。**SONIC 使用协议 v1、v3 和 v4。** 协议 v2 面向自定义应用开放。

### 编码模式逻辑

编码模式仅在策略模型配置并加载了**编码器**时才生效。启动时，每个动作的编码模式根据编码器是否可用进行初始化：

| `encode_mode` | 含义 |
|----------------|---------|
| `-2` | 模型中未配置编码器 / token 状态——编码模式无效果 |
| `-1` | 存在编码器配置（token 状态维度 > 0）但未提供编码器模型文件 |
| `0` | 编码器已加载，基于关节模式（默认） |
| `1` | 编码器已加载，遥操作 / 3 点上半身模式 |
| `2` | 编码器已加载，基于 SMPL 模式 |

当 ZMQ 流式传输激活时，协议版本会为所推流的动作设定编码模式：v1 → `0`，v2/v3 → `2`。协议 v4 完全绕过编码器——它将预先计算好的 token 直接送入策略。只有当模型确实配有编码器（`encode_mode >= 0`）时，这才会影响推理。如果未配置编码器（`-2`），该值会被设置但对推理流水线无影响。

切换回参考动作时（按下 **ENTER** 禁用推流），编码模式重置为 `0`（前提是该动作配有编码器，即 `encode_mode >= 0`）。

### 通用字段（所有版本）

所有版本都要求两个通用字段：

| 字段 | 形状 | 数据类型 | 描述 |
|-------|-------|-------|-------------|
| `body_quat` | `[N, 4]` 或 `[N, num_bodies, 4]` | `f32` / `f64` | 每帧的刚体四元数（w, x, y, z） |
| `frame_index` | `[N]` | `i32` / `i64` | 用于对齐的单调递增帧索引 |

```{warning}
不允许在会话中途更改协议版本。如果发布端在推流过程中切换协议版本，接口出于安全考虑会自动禁用 ZMQ 模式并返回参考动作。

报错信息：`Protocol version changed from X to Y during active ZMQ session!`
```

### 协议 v1 —— 基于关节（编码模式 0）

推流原始 G1 关节位置与速度。当你的数据源直接提供 qpos/qvel 数据（例如来自另一个仿真器或动作捕捉重定向流水线）时，使用本协议。

**必填字段：**

| 字段 | 形状 | 数据类型 | 描述 |
|-------|-------|-------|-------------|
| `joint_pos` | `[N, 29]` | `f32` / `f64` | IsaacLab 顺序的关节位置（全部 29 个关节） |
| `joint_vel` | `[N, 29]` | `f32` / `f64` | IsaacLab 顺序的关节速度（全部 29 个关节） |

- `N` = 每条消息的帧数（批大小）。
- 必须提供全部 29 个关节值，且均有意义。
- `joint_pos` 与 `joint_vel` 的帧数必须一致。

**常见报错：**
- `Version 1 missing required fields (joint_pos, joint_vel)` ——一个或两个字段缺失。
- `Frame count mismatch between joint_pos and joint_vel` ——`N` 维度不一致。

### 协议 v2 —— 基于 SMPL（编码模式 2）

推流 SMPL 身体模型数据。SONIC 的内置流水线**不使用**本协议——它面向你自己的、能产生 SMPL 表示的自定义应用开放，例如一个只观测 SMPL 的策略。

**必填字段：**

| 字段 | 形状 | 数据类型 | 描述 |
|-------|-------|-------|-------------|
| `smpl_joints` | `[N, 24, 3]` | `f32` / `f64` | SMPL 关节位置（24 个关节 × xyz） |
| `smpl_pose` | `[N, 21, 3]` | `f32` / `f64` | 轴角表示的 SMPL 关节旋转（21 个身体姿态 × xyz） |

- 在 v2 中，`joint_pos` 与 `joint_vel` 是**可选的**。

**常见报错：**
- `Version 2 missing required field 'smpl_joints'` 或 `'smpl_pose'` ——必填的 SMPL 字段缺失。

### 协议 v3 —— 关节 + SMPL 组合（编码模式 2）

同时包含关节级与 SMPL 数据。SONIC 的全身遥操作（例如 PICO VR）使用的就是本协议。

**必填字段：**

| 字段 | 形状 | 数据类型 | 描述 |
|-------|-------|-------|-------------|
| `joint_pos` | `[N, 29]` | `f32` / `f64` | IsaacLab 顺序的关节位置 |
| `joint_vel` | `[N, 29]` | `f32` / `f64` | IsaacLab 顺序的关节速度 |
| `smpl_joints` | `[N, 24, 3]` | `f32` / `f64` | SMPL 关节位置（24 个关节 × xyz） |
| `smpl_pose` | `[N, 21, 3]` | `f32` / `f64` | 轴角表示的 SMPL 关节旋转（21 个身体姿态 × xyz） |

```{important}
在协议 v3 中，`joint_pos` 里**只有 6 个腕部关节需要有意义的值**——其余 23 个关节可以为零。腕部关节索引（IsaacLab 顺序）为：**[23, 24, 25, 26, 27, 28]**（每只手腕 3 个关节 × 2 只手）。非腕部关节的 `joint_vel` 值同样可以为零。

在 v3 中，SMPL 字段（`smpl_joints`、`smpl_pose`）承载主要动作数据；`joint_pos` 中的腕部关节提供 SMPL 单独无法表达的精细腕部控制。
```

- 四个字段的帧数必须相互一致。

**常见报错：**
- `Version 3 missing required field 'joint_pos'` 或 `'joint_vel'` ——关节字段缺失（与 v2 不同，它们在 v3 中是必填的）。
- `Version 3 frame count mismatch between smpl_joints (X) and joint_pos (Y)` ——各字段间 `N` 维度不一致。

### 协议 v4 —— 仅 token 推流（直接潜在动作）

将预先计算好的运动 token 直接推流给策略，完全绕过编码器。当你的数据源能产生已编码的潜在动作时，使用本协议（例如运行在另一台机器上的独立编码器，或直接输出 token 的生成模型）。

与 v1–v3 不同，协议 v4 **不**携带动作帧——机器人侧的参考动作保持不变。token 被直接注入解码器策略的 `token_state` 观测槽位。

**必填字段：**

| 字段 | 形状 | 数据类型 | 描述 |
|-------|-------|-------|-------------|
| `token_state` | `[D]` | `f32` / `f64` | 运动 token 数组（维度必须与观测配置中编码器的 `dimension` 一致） |

**可选字段：**

| 字段 | 形状 | 数据类型 | 描述 |
|-------|-------|-------|-------------|
| `frame_index` | `[1]` | `i32` / `i64` | 帧索引（仅用于日志记录，不影响回放） |
| `left_hand_joints` | `[7]` 或 `[1, 7]` | `f32` / `f64` | 左手 7 自由度 Dex3 关节位置 |
| `right_hand_joints` | `[7]` 或 `[1, 7]` | `f32` / `f64` | 右手 7 自由度 Dex3 关节位置 |
| `body_quat_w` | `[4]` 或 `[1, 4]` | `f32` / `f64` | 用于朝向更新的身体四元数（w, x, y, z） |

- `token_state` 的维度会对照编码器配置进行校验。不一致时记录为警告。
- 如提供手部关节，会直接作用于机器人（与 v1–v3 的可选手部字段相同）。
- 在 token 推流期间，`body_quat_w` 可用于更新朝向参考。

**常见报错：**
- `Version 4 missing required field 'token_state'` ——消息中缺少 `token_state` 字段。
- `Protocol version 4 with motion data is impossible!` ——v4 消息产生了动作序列（正常情况不应发生；表明解码器存在 bug）。
- `Protocol version 4 with empty token data!` ——`token_state` 字段存在但不含数据。

```{warning}
协议 v4 要求策略的编码器配置在其观测中包含 `token_state`。如果模型没有编码器（`encode_mode == -2`），token 会被接收但不产生任何效果。
```

### 协议总结

| 协议 | 编码模式 | SONIC 是否使用 | 必填字段 |
|----------|-------------|---------------|-----------------|
| v1 | `0`（基于关节） | ✅ 是 | `joint_pos`, `joint_vel` |
| v2 | `2`（基于 SMPL） | ❌ 仅自定义 | `smpl_joints`, `smpl_pose` |
| v3 | `2`（基于 SMPL） | ✅ 是 | `joint_pos`, `joint_vel`, `smpl_joints`, `smpl_pose` |
| v4 | N/A（绕过编码器） | ✅ 是 | `token_state` |

## 可选流字段

以下可选字段可用于任何协议版本：

| 字段 | 形状 | 数据类型 | 描述 |
|-------|-------|-------|-------------|
| `left_hand_joints` | `[7]` 或 `[1, 7]` | `f32` / `f64` | 左手 7 自由度 Dex3 关节位置 |
| `right_hand_joints` | `[7]` 或 `[1, 7]` | `f32` / `f64` | 右手 7 自由度 Dex3 关节位置 |
| `vr_position` | `[9]` 或 `[3, 3]` | `f32` / `f64` | VR 三点跟踪位置：左腕、右腕、头（xyz × 3） |
| `vr_orientation` | `[12]` 或 `[3, 4]` | `f32` / `f64` | VR 三点朝向：左、右、头的四元数（wxyz × 3） |
| `catch_up` | 标量 | `bool` / `u8` / `i32` | 若为 `true`（默认），检测到大帧间隔时重置回放 |
| `heading_increment` | 标量 | `f32` / `f64` | 每条消息施加的增量朝向调整 |

## 配置

| 旗标 | 默认值 | 描述 |
|------|---------|-------------|
| `--zmq-host` | `localhost` | ZMQ 发布端主机 |
| `--zmq-port` | `5556` | ZMQ 发布端端口 |
| `--zmq-topic` | `pose` | ZMQ topic 前缀 |
| `--zmq-conflate` | off | 仅保留最新消息（丢弃过期帧） |
