# 观测配置

本页是部署系统中观测配置的完整参考，涵盖 YAML 配置格式、编码器系统、所有可用的观测类型，以及如何创建你自己的自定义观测。

(obs-config-format)=
## 配置格式

观测通过随 `--obs-config <path>` 传入的 YAML 文件进行配置。每个观测都有一个 `name`（必须与某个已注册的观测匹配）和一个 `enabled` 标志。

### 基本结构

```yaml
observations:
  - name: "motion_joint_positions"
    enabled: true
  - name: "motion_joint_velocities"
    enabled: true
  - name: "motion_anchor_orientation"
    enabled: true
  - name: "base_angular_velocity"
    enabled: true
  - name: "body_joint_positions"
    enabled: true
  - name: "body_joint_velocities"
    enabled: true
  - name: "last_actions"
    enabled: true
```

**关键规则：**

- 所有观测按**列出的顺序**拼接，构成策略的输入向量。
- 偏移量会自动计算 —— 无需手动管理偏移。
- 所有启用观测的**总维度**必须与 ONNX 模型的输入大小匹配。
- 被禁用的观测（`enabled: false`）会被完全跳过。
- 调整条目顺序会改变输入张量的布局（偏移量随之移动）。

(obs-config-encoder)=
### 带编码器的配置（基于 token 的策略）

对于使用编码器将观测压缩为紧凑 token 的策略，需要添加一个 `encoder:` 段：

```yaml
observations:
  - name: "token_state"           # Encoder outputs (dimension set below)
    enabled: true
  - name: "base_angular_velocity" # Direct observations
    enabled: true
  - name: "body_joint_positions"
    enabled: true
  - name: "body_joint_velocities"
    enabled: true
  - name: "last_actions"
    enabled: true

encoder:
  dimension: 64       # Token output dimension
  use_fp16: false     # TensorRT precision for encoder (optional)
  encoder_observations:
    - name: "motion_joint_positions_10frame_step5"
      enabled: true
    - name: "motion_joint_velocities_10frame_step5"
      enabled: true
    - name: "motion_anchor_orientation_10frame_step5"
      enabled: true
    - name: "motion_root_z_position_10frame_step5"
      enabled: true
  encoder_modes:            # Optional: per-mode observation requirements
    - name: "g1"
      mode_id: 0
      required_observations:
        - motion_joint_positions_10frame_step5
        - motion_joint_velocities_10frame_step5
        - motion_anchor_orientation_10frame_step5
        - motion_root_z_position_10frame_step5
```

**编码器字段：**

| 字段 | 说明 |
|---|---|
| `dimension` | token 输出维度（必须与编码器 ONNX 模型的输出一致）。设为 0 或省略即可禁用编码器。 |
| `use_fp16` | 编码器 TensorRT 引擎是否使用 FP16 精度（默认：false）。 |
| `encoder_observations` | 输入给编码器的观测（所有模式的超集）。格式与策略观测的 name/enabled 相同。 |
| `encoder_modes` | *（可选）* 每种模式的观测需求。不在某模式 `required_observations` 中的观测会填零，从而节省计算量。 |

运行时传入 `--encoder-file <path>` 以加载编码器模型。若省略，`token_state` 可以通过 ROS2/ZMQ 从外部设置。

完整带注释的示例参见 `policy/observation_config_example.yaml`。

### 命名规则

多帧观测遵循以下命名模式：`{base_name}_{N}frame_step{S}`

- **N** = 采集的帧数（时域窗口大小）
- **S** = 帧之间的步长（以 50 Hz 的控制节拍计，因此 step5 = 相隔 0.1 s）
- 不带后缀 = 仅当前单帧

例如，`motion_joint_positions_10frame_step5` 采集 10 帧关节位置，每 5 个节拍（0.1 s）采样一次，形成 0.9 s 的前瞻窗口。如果未来帧超出动作长度，则重复最后一帧。

---

## 编码器与 token 观测

这些观测与编码器（tokenizer）系统相关。YAML 格式参见上文[带编码器的配置](obs-config-encoder)。

| 名称 | 维度 | 说明 |
|---|---|---|
| `token_state` | config | 编码器输出的 token（维度由 YAML 中的 `encoder.dimension` 设定）。由本地编码器推理填充，或通过 ZMQ/ROS2 从外部填充。 |
| `encoder_mode` | 3 | 当前编码器模式 ID + 2 个零填充值。 |
| `encoder_mode_4` | 4 | 当前编码器模式 ID + 3 个零填充值。 |

---

## 参考动作观测

从当前激活的动作序列（参考动作、规划器输出或 ZMQ 流）中采集。所有关节数据均采用 **IsaacLab 关节顺序**（29 个关节）。

### 关节位置（来自动作）

| 名称 | 维度 | 帧数 | 步长 | 说明 |
|---|---|---|---|---|
| `motion_joint_positions` | 29 | 1 | — | 当前帧关节位置（rad） |
| `motion_joint_positions_3frame_step1` | 87 | 3 | 1 | 3 帧窗口，连续 |
| `motion_joint_positions_5frame_step5` | 145 | 5 | 5 | 5 帧窗口，相隔 0.1 s |
| `motion_joint_positions_10frame_step1` | 290 | 10 | 1 | 10 帧窗口，连续 |
| `motion_joint_positions_10frame_step5` | 290 | 10 | 5 | 10 帧窗口，相隔 0.1 s |
| `motion_joint_positions_lowerbody_10frame_step1` | 120 | 10 | 1 | 仅下肢关节（12 个关节），连续 |
| `motion_joint_positions_lowerbody_10frame_step5` | 120 | 10 | 5 | 仅下肢关节，相隔 0.1 s |
| `motion_joint_positions_wrists_10frame_step1` | 60 | 10 | 1 | 仅腕部关节（6 个关节），连续 |
| `motion_joint_positions_wrists_2frame_step1` | 12 | 2 | 1 | 仅腕部关节，连续 2 帧 |

```{note}
当上半身控制处于激活状态（例如通过 ZMQ/ROS2 遥操作）时，这些观测中的上半身关节位置会被外部提供的目标值替换。
```

### 关节速度（来自动作）

| 名称 | 维度 | 帧数 | 步长 | 说明 |
|---|---|---|---|---|
| `motion_joint_velocities` | 29 | 1 | — | 当前帧关节速度（rad/s）。未播放时为零。 |
| `motion_joint_velocities_3frame_step1` | 87 | 3 | 1 | 3 帧窗口，连续 |
| `motion_joint_velocities_5frame_step5` | 145 | 5 | 5 | 5 帧窗口，相隔 0.1 s |
| `motion_joint_velocities_10frame_step1` | 290 | 10 | 1 | 10 帧窗口，连续 |
| `motion_joint_velocities_10frame_step5` | 290 | 10 | 5 | 10 帧窗口，相隔 0.1 s |
| `motion_joint_velocities_lowerbody_10frame_step1` | 120 | 10 | 1 | 仅下肢关节，连续 |
| `motion_joint_velocities_lowerbody_10frame_step5` | 120 | 10 | 5 | 仅下肢关节，相隔 0.1 s |
| `motion_joint_velocities_wrists_10frame_step1` | 60 | 10 | 1 | 仅腕部关节，连续 |

### 锚点朝向（来自动作）

从机器人当前基座朝向到参考动作朝向、经朝向修正的相对旋转。输出为 3×3 旋转矩阵的前两列（每帧 6 个值）。

| 名称 | 维度 | 帧数 | 步长 | 说明 |
|---|---|---|---|---|
| `motion_anchor_orientation` | 6 | 1 | — | 当前帧锚点朝向（完整基座四元数） |
| `motion_anchor_orientation_10frame_step1` | 60 | 10 | 1 | 10 帧窗口，连续 |
| `motion_anchor_orientation_10frame_step5` | 60 | 10 | 5 | 10 帧窗口，相隔 0.1 s |
| `motion_anchor_orientation_heading` | 6 | 1 | — | 当前帧，仅朝向的四元数（从机器人基座中提取偏航） |
| `motion_anchor_orientation_heading_10frame_step1` | 60 | 10 | 1 | 仅朝向，10 帧窗口，连续 |
| `motion_anchor_orientation_heading_10frame_step5` | 60 | 10 | 5 | 仅朝向，10 帧窗口，相隔 0.1 s |
| `motion_anchor_orientation_refheading` | 6 | 1 | — | 当前帧，参考朝向四元数（取自第一个未来参考帧的偏航） |
| `motion_anchor_orientation_refheading_10frame_step1` | 60 | 10 | 1 | 参考朝向，10 帧窗口，连续 |
| `motion_anchor_orientation_refheading_10frame_step5` | 60 | 10 | 5 | 参考朝向，10 帧窗口，相隔 0.1 s |

### 根高度 Z 位置（来自动作）

| 名称 | 维度 | 帧数 | 步长 | 说明 |
|---|---|---|---|---|
| `motion_root_z_position` | 1 | 1 | — | 当前帧根高度（m） |
| `motion_root_z_position_3frame_step1` | 3 | 3 | 1 | 3 帧窗口，连续 |
| `motion_root_z_position_10frame_step1` | 10 | 10 | 1 | 10 帧窗口，连续 |
| `motion_root_z_position_10frame_step5` | 10 | 10 | 5 | 10 帧窗口，相隔 0.1 s |

---

## SMPL 观测

从动作序列中的 SMPL 数据采集（可选 —— 需要动作带有 `smpl_joint.csv` / `smpl_pose.csv`）。

### SMPL 关节位置

每个 SMPL 关节的三维位置（24 个关节 × 3 = 每帧 72 维）。

| 名称 | 维度 | 帧数 | 步长 | 说明 |
|---|---|---|---|---|
| `smpl_joints` | 72 | 1 | — | 当前帧，全部 24 个 SMPL 关节 |
| `smpl_joints_2frame_step1` | 144 | 2 | 1 | 连续 2 帧 |
| `smpl_joints_5frame_step5` | 360 | 5 | 5 | 5 帧窗口，相隔 0.1 s |
| `smpl_joints_10frame_step1` | 720 | 10 | 1 | 10 帧窗口，连续 |
| `smpl_joints_10frame_step5` | 720 | 10 | 5 | 10 帧窗口，相隔 0.1 s |
| `smpl_joints_lower_10frame_step1` | 270 | 10 | 1 | 仅下肢 SMPL 关节（9 个关节），连续 |

### SMPL 姿态（轴角）

每个 SMPL 身体部件的三维轴角（21 个姿态 × 3 = 每帧 63 维）。

| 名称 | 维度 | 帧数 | 步长 | 说明 |
|---|---|---|---|---|
| `smpl_pose` | 63 | 1 | — | 当前帧，全部 21 个 SMPL 姿态 |
| `smpl_pose_5frame_step5` | 315 | 5 | 5 | 5 帧窗口，相隔 0.1 s |
| `smpl_pose_10frame_step1` | 630 | 10 | 1 | 10 帧窗口，连续 |
| `smpl_pose_10frame_step5` | 630 | 10 | 5 | 10 帧窗口，相隔 0.1 s |
| `smpl_elbow_wrist_poses_10frame_step1` | 120 | 10 | 1 | 仅肘部 + 腕部姿态（4 个部件），连续 |

### SMPL 别名

这些观测使用与动作观测相同的采集器，但面向基于 SMPL 的策略：

| 名称 | 维度 | 帧数 | 步长 | 说明 |
|---|---|---|---|---|
| `smpl_root_z_10frame_step1` | 10 | 10 | 1 | 根高度，连续 10 帧 |
| `smpl_anchor_orientation_10frame_step1` | 60 | 10 | 1 | 锚点朝向，连续 10 帧 |
| `smpl_anchor_orientation_2frame_step1` | 12 | 2 | 1 | 锚点朝向，连续 2 帧 |

---

## VR 跟踪观测

VR 三点与五点跟踪数据。当外部来源（ZMQ/ROS2）提供 VR 数据时，直接使用缓冲的值。否则，位置与朝向会根据动作序列的刚体数据计算，并归一化到根刚体坐标系。

### VR 三点

| 名称 | 维度 | 说明 |
|---|---|---|
| `vr_3point_local_target` | 9 | 根坐标系下的三点位置：`[left_wrist xyz, right_wrist xyz, head xyz]` |
| `vr_3point_local_target_compliant` | 9 | 同上（遥操作期间两者相同） |
| `vr_3point_local_orn_target` | 12 | 根坐标系下的三点朝向：`[left quat wxyz, right quat wxyz, head quat wxyz]` |
| `vr_3point_compliance` | 3 | 柔顺度值：`[left_arm, right_arm, head]`。由键盘控制（g/h/b/v 键），范围 [0.0, 0.5]。 |

### VR 五点

| 名称 | 维度 | 说明 |
|---|---|---|
| `vr_5point_local_target` | 15 | 根坐标系下的五点位置：`[left_wrist, right_wrist, head, left_ankle, right_ankle]` × xyz |
| `vr_5point_local_orn_target` | 20 | 根坐标系下的五点朝向：5 个四元数 × wxyz |

---

## 机器人状态历史观测

从 StateLogger 环形缓冲区（真实机器人测得的传感器数据）中采集。这些观测通过采样过去的状态提供时域上下文。

### 单帧（当前状态）

| 名称 | 维度 | 说明 |
|---|---|---|
| `base_angular_velocity` | 3 | IMU 角速度（rad/s）：`[roll_rate, pitch_rate, yaw_rate]` |
| `body_joint_positions` | 29 | 来自编码器的当前关节位置（rad，IsaacLab 顺序） |
| `body_joint_velocities` | 29 | 来自编码器的当前关节速度（rad/s，IsaacLab 顺序） |
| `last_actions` | 29 | 上一次策略输出（归一化动作值） |
| `gravity_dir` | 3 | 机身坐标系下的重力方向（由基座 IMU 四元数计算） |

### 多帧历史（4 帧，步长 1）

| 名称 | 维度 | 说明 |
|---|---|---|
| `his_body_joint_positions_4frame_step1` | 116 | 关节位置：连续 4 个节拍（29 × 4） |
| `his_body_joint_velocities_4frame_step1` | 116 | 关节速度：连续 4 个节拍 |
| `his_last_actions_4frame_step1` | 116 | 过去动作：连续 4 个节拍 |
| `his_base_angular_velocity_4frame_step1` | 12 | 角速度：连续 4 个节拍（3 × 4） |
| `his_gravity_dir_4frame_step1` | 12 | 重力方向：连续 4 个节拍 |

### 多帧历史（10 帧，步长 1）

| 名称 | 维度 | 说明 |
|---|---|---|
| `his_body_joint_positions_10frame_step1` | 290 | 关节位置：连续 10 个节拍（29 × 10） |
| `his_body_joint_velocities_10frame_step1` | 290 | 关节速度：连续 10 个节拍 |
| `his_last_actions_10frame_step1` | 290 | 过去动作：连续 10 个节拍 |
| `his_base_angular_velocity_10frame_step1` | 30 | 角速度：连续 10 个节拍（3 × 10） |
| `his_gravity_dir_10frame_step1` | 30 | 重力方向：连续 10 个节拍 |

---

## 创建自定义观测

你可以通过修改 C++ 源码来添加自己的观测类型。观测系统围绕**注册表模式**构建 —— 你编写一个采集器函数，用一个名称和维度注册它，然后在 YAML 配置中使用该名称。

所有观测代码都位于 `gear_sonic_deploy/src/g1/g1_deploy_onnx_ref/src/g1_deploy_onnx_ref.cpp` 中的 `G1Deploy` 类内。

### 第 1 步：编写采集器函数

采集器函数从内部状态（传感器数据、动作数据等）读取信息，并将输出写入给定偏移处的目标缓冲区。函数签名为：

```cpp
bool MyObservation(std::vector<double>& target_buffer, size_t offset) {
    // Write your observation values into target_buffer starting at offset.
    // Return true on success, false on failure (will stop the control loop).
}
```

**G1Deploy 内可用的数据来源**（完整列表见 `g1_deploy_onnx_ref.cpp` 中的成员变量）：

| 来源 | 说明 |
|---|---|
| `state_logger_` | 过去机器人状态的环形缓冲区 —— IMU、关节、速度、动作、手部状态、token 状态 |
| `current_motion_` / `current_frame_` | 当前激活的动作序列与播放游标 |
| `operator_state` | 操作员控制标志（`.play`、`.start`、`.stop`） |
| `vr_*_buffer_`、`left_hand_joint_buffer_` 等 | 缓冲的输入接口数据 —— VR 跟踪、手部关节、柔顺度、上半身目标 |
| `heading_state_buffer_`、`movement_state_buffer_` | 用于朝向与规划器移动指令的线程安全缓冲区 |

**示例** —— 一个输出躯干 IMU 角速度（3 个值）的自定义观测：

```cpp
bool GatherTorsoAngularVelocity(std::vector<double>& target_buffer, size_t offset) {
    if (!state_logger_) { return false; }

    auto hist = state_logger_->GetLatest(1);
    if (hist.empty()) { return false; }

    const auto& entry = hist[0];
    target_buffer[offset + 0] = entry.body_torso_ang_vel[0];
    target_buffer[offset + 1] = entry.body_torso_ang_vel[1];
    target_buffer[offset + 2] = entry.body_torso_ang_vel[2];
    return true;
}
```

### 第 2 步：注册到观测注册表

将你的观测添加到 `g1_deploy_onnx_ref.cpp` 的 `GetObservationRegistry()` 方法中。每个条目是一个 `{name, dimension, gatherer_lambda}` 元组：

```cpp
std::vector<ObservationRegistry> GetObservationRegistry() {
    return {
        // ... existing observations ...

        // Your custom observation:
        {"torso_angular_velocity", 3,
         [this](std::vector<double>& buf, size_t offset) {
             return GatherTorsoAngularVelocity(buf, offset);
         }},
    };
}
```

**名称**就是你将在 YAML 配置中使用的字符串。**维度**必须精确 —— 系统会校验所有启用观测的总维度是否与 ONNX 模型输入大小匹配。

### 第 3 步：在 YAML 配置中使用

注册之后，你的观测就可以像任何内置观测一样使用：

```yaml
observations:
  - name: "torso_angular_velocity"
    enabled: true
  # ... other observations ...
```

### 提示

- **维度必须固定。** 观测维度在注册时设定，运行时不可更改。如果需要可变大小的数据，请填充到固定的最大值。
- **不要在高频路径（热路径）中动态分配内存。** 采集器函数在控制循环中以 50 Hz 运行。避免使用 `new`、`malloc` 或重新调整 vector 大小。在构造函数中预分配缓冲区，或使用栈上数组。
- **谨慎返回 `false`。** 采集器返回 `false` 会停止整个控制循环。只有不可恢复的错误才应返回 `false`。对于缺失的可选数据，应写入零并返回 `true`。
- **线程安全。** 采集器在控制线程上运行。从 `state_logger_` 和 `DataBuffer` 对象读取是线程安全的。访问 `current_motion_` 与 `current_frame_` 受 `current_motion_mutex_` 保护（调用 `GatherObservations()` 时该锁已被持有）。
- **多帧模式。** 如果你的观测需要时域窗口，请遵循现有的 `GatherHis*` 或 `GatherMotion*MultiFrame` 模式 —— 它们接受 `num_frames` 与 `step_size` 参数，并注册多个变体（例如 `my_obs`、`my_obs_4frame_step1`、`my_obs_10frame_step5`）。
- **编码器观测。** 自定义观测也可以用作编码器输入。在同一个注册表中注册即可 —— 它们将同时可用于 YAML 配置中的 `observations:` 与 `encoder_observations:`。
- **修改后重新构建。** 修改 C++ 源码后，在 `gear_sonic_deploy/` 目录下运行 `just build` 重新构建。

---

## 配置示例

### 最小配置（154D —— 默认策略）

```yaml
observations:
  - name: "motion_joint_positions"       # 29D
    enabled: true
  - name: "motion_joint_velocities"      # 29D
    enabled: true
  - name: "motion_anchor_orientation"    # 6D
    enabled: true
  - name: "base_angular_velocity"        # 3D
    enabled: true
  - name: "body_joint_positions"         # 29D
    enabled: true
  - name: "body_joint_velocities"        # 29D
    enabled: true
  - name: "last_actions"                 # 29D
    enabled: true
# Total: 154D
```

### 带编码器的基于 token 的策略

```yaml
observations:
  - name: "token_state"                  # 64D (from encoder)
    enabled: true
  - name: "base_angular_velocity"        # 3D
    enabled: true
  - name: "body_joint_positions"         # 29D
    enabled: true
  - name: "body_joint_velocities"        # 29D
    enabled: true
  - name: "last_actions"                 # 29D
    enabled: true

encoder:
  dimension: 64
  use_fp16: false
  encoder_observations:
    - name: "motion_joint_positions_10frame_step5"   # 290D
      enabled: true
    - name: "motion_joint_velocities_10frame_step5"  # 290D
      enabled: true
    - name: "motion_anchor_orientation_10frame_step5" # 60D
      enabled: true
    - name: "motion_root_z_position_10frame_step5"   # 10D
      enabled: true
```

### VR 遥操作策略

```yaml
observations:
  - name: "token_state"                         # 64D
    enabled: true
  - name: "vr_3point_local_target"              # 9D
    enabled: true
  - name: "vr_3point_local_orn_target"          # 12D
    enabled: true
  - name: "vr_3point_compliance"                # 3D
    enabled: true
  - name: "base_angular_velocity"               # 3D
    enabled: true
  - name: "body_joint_positions"                # 29D
    enabled: true
  - name: "body_joint_velocities"               # 29D
    enabled: true
  - name: "last_actions"                        # 29D
    enabled: true
```

YAML 语法的详细信息参见上文[配置格式](obs-config-format)。
