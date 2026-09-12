# C++ 部署程序流程

本文档介绍各个主可执行程序的运行方式、命令行参数，以及日志与配置选项。

## 程序流水线

高层流程（与当前代码一致）：
- 输入接口：`keyboard | gamepad | gamepad_manager | zmq | zmq_manager | ros2 | manager`
- 可选的运动学规划器（启用时）生成目标动画
- 动作读取器在非规划器模式下提供参考动作
- 策略推理（TensorRT；可选编码器 → 解码器）
- 通过 `--output-type <zmq|ros2|all>` 发布控制输出

## 可用命令

```sh
just build           # 编译主工程
just clean           # 清理编译产物
just --list          # 显示所有可用命令
```

## 运行

### 频率测试

加载一个 ONNX 模型并打印输入/输出信息。这是针对模型加载的快速验证；报告的频率并非 TensorRT 推理速度。

```sh
# 使用默认设置（1000 次迭代、随机数据）
just run freq_test policy/example/model_step_000000.onnx

# 自定义迭代次数与数据模式
just run freq_test policy/example/model_step_000000.onnx 5000 random
```

**用法：** `just run freq_test <model_file> [iterations] [data_mode]`
- `model_file`：ONNX 模型文件路径（必需）
- `iterations`：推理迭代次数（默认：1000）
- `data_mode`：输入数据类型 — `zeros|random|ones`（默认：random）

### 策略部署

在 G1 机器人上部署 ONNX 策略，并使用参考动作进行控制：

```sh
# 示例命令（真机）
just run g1_deploy_onnx_ref enP8p1s0 policy/release/model_decoder.onnx reference/example/ \
  --obs-config policy/release/observation_config.yaml \
  --encoder-file policy/release/model_encoder.onnx \
  --planner-file planner/target_vel/V2/planner_sonic.onnx \
  --input-type manager \
  --enable-motion-recording \
  --enable-csv-logs

# MuJoCo 仿真（需禁用 CRC 校验）
python ../gear_sonic/scripts/run_sim_loop.py
just run g1_deploy_onnx_ref lo policy/release/model_decoder.onnx reference/example/ \
  --obs-config policy/release/observation_config.yaml \
  --encoder-file policy/release/model_encoder.onnx \
  --planner-file planner/target_vel/V2/planner_sonic.onnx \
  --input-type manager \
  --enable-motion-recording \
  --enable-csv-logs \
  --disable-crc-check
```

**用法：** `just run g1_deploy_onnx_ref <network_interface> <model_file> <motion_data_path> [options...]`

**必需参数：**
- `network_interface`：用于 DDS 通信的网络接口（如 `eth0`、`enp5s0`、`enP8p1s0`、`lo`）
- `model_file`：ONNX 策略模型文件路径
- `motion_data_path`：包含参考动作的动作数据目录路径

**可选参数：**

**模型配置：**
- `--obs-config <path>`：观测配置 YAML 文件路径
- `--encoder-file <path>`：ONNX 编码器模型文件路径（可选，用于基于 token 的策略）
- `--planner-file <path>`：ONNX 运动学规划器模型文件路径（ROS2、`gamepad_manager` 与 `zmq_manager` 的规划器模式必需）
- `--planner-precision <16|32>`：规划器的浮点精度（默认：32）
- `--policy-precision <16|32>`：策略的浮点精度（默认：32）

**输出模式：**
- `--output-type <type>`：用于发布控制结果的输出接口
  - `zmq` — 通过 ZMQ 发布（默认）
  - `ros2` — 通过 ROS2 发布（仅当编译时启用了 ROS2 支持）
  - `all` — 同时创建所有可用的输出接口

**输入模式：**
- `--input-type <type>`：输入接口类型（默认：`keyboard`）
  - `keyboard` — 直接键盘输入
  - `gamepad` — 无线手柄
  - `gamepad_manager` — 手柄 + 快速切换到 ZMQ/ROS2
  - `zmq` — 网络动作流式传输
  - `zmq_manager` — 在规划器与网络动作流式传输之间动态切换
  - `manager` — 在键盘、手柄、ZMQ 与 ROS2 之间动态切换
  - `ros2` — ROS2 topic 控制（需要规划器，仅当编译时启用了 ROS2 支持）

**ZMQ 配置（使用 `--input-type zmq`、`zmq_manager`、`demo_gamepad_manager` 或 `manager` 时）：**
- `--zmq-host <host>`：ZMQ 服务器主机（默认：`localhost`）
- `--zmq-port <port>`：ZMQ 服务器端口（默认：`5556`）
- `--zmq-topic <topic>`：ZMQ topic/前缀（默认：`pose`）
- `--zmq-conflate`：启用 ZMQ CONFLATE（仅保留最新消息）模式
- `--zmq-verbose`：启用 ZMQ 订阅端的详细日志
- `--zmq-out-port`：使用 `--output-type zmq` 时控制结果的发布端口（默认：`5557`）
- `--zmq-out-topic`：使用 `--output-type zmq` 时控制结果的发布 topic（默认：`g1_debug`）

**仿真：**
- `--disable-crc-check`：禁用 CRC 校验（MuJoCo 仿真时必需）

**手部与柔顺度控制：**
- `--set-compliance <value>`：设置 VR 三点跟踪的初始柔顺度（0.01 = 刚性，0.5 = 柔顺；默认：`0.5,0.5,0.0`）。可指定 1 个值（同时作用于双手）或 3 个逗号分隔的值（`left_wrist,right_wrist,head`）。运行时键盘控制：`g/h` = 左手 ±0.1，`b/v` = 右手 ±0.1。
- `--max-close-ratio <value>`：设置手部最大闭合比例的初始值（0.2–1.0；默认：1.0，即允许完全闭合）。运行时键盘控制：`x/c` = ±0.1。

**日志（CLI 旗标）：**
- **调试 / 分析日志（写入单个 CSV 文件）**：
  - `--target-motion-logfile <path>`：记录控制器正在跟踪的目标动作（可用 `visualize_motion.py` 可视化）
  - `--planner-motion-logfile <path>`：记录规划器生成的动画序列
  - `--policy-input-logfile <path>`：记录策略输入（观测）张量
  - `--record-input-file <path>`：将操作员的控制输入记录到 CSV，供之后回放
  - `--playback-input-file <path>`：从 CSV 回放先前录制的控制输入
- **状态 CSV 日志（写入带时间戳的目录）**：
  - `--logs-dir <path>`：状态 CSV 日志的基准目录（默认：`logs/dd-mm-yy/hh-mm-ss`）
  - `--enable-csv-logs`：启用机器人状态 CSV 日志记录（默认：关闭）
  - `--enable-motion-recording`：将当前活跃的动作流录制到 `reference/recorded_motion/...`（默认：关闭）

## 日志（详细说明）

系统提供多种日志功能，用于调试、分析与回放。

### 动作日志

**目标动作（`--target-motion-logfile <path>`）：**
- 记录控制器在每个控制帧（约 50 Hz）正在跟踪的动作
- CSV 列：`pos_x, pos_y, pos_z, rot_qw, rot_qx, rot_qy, rot_qz, dof_0, dof_1, ... dof_28`
  - 全局位置（xyz）
  - 全局旋转四元数（w, x, y, z）
  - 29 个关节角度（DoF）

**规划器动作（`--planner-motion-logfile <path>`）：**
- 记录规划器生成的动画序列（规划器约以 10 Hz 更新）
- 规划器每次更新会产生一段短序列（例如约 100 帧），追加写入 CSV
- CSV 格式与目标动作相同
- 包含动作融合与重规划的结果

**动作录制（`--enable-motion-recording`）：**
- 自动将当前活跃的动作流录制到 `reference/recorded_motion/YYYYMMDD/` 下带时间戳的文件夹中
  - **流式动作**（ZMQ pose topic）：保存为 `streamed_HHMMSS/`
  - **规划器动作**（规划器生成的序列）：保存为 `planner_motion_HHMMSS/`
- 每个录制文件夹包含 `joint_pos.csv`、`joint_vel.csv`、`body_pos.csv`、`body_quat.csv` 等文件
- 可用于闭环行为的离线检查 / 回归对比

### 可视化

所有动作 CSV 文件（记录的数据与参考动作）都可以用 `visualize_motion.py` 脚本可视化：

```sh
# 可视化记录的动作数据（单个 CSV 文件）
python visualize_motion.py --csv_path target_motion.csv

# 可视化动作数据目录中的参考动作
python visualize_motion.py --motion_dir reference/example/high_jump_full_turn/
```

可视化脚本还可以连接到正在运行的 `g1_deploy` 可执行程序，实时显示目标 / 实测的机器人动作：

```sh
python visualize_motion.py --realtime_debug_url tcp://localhost:5557
```

画面中显示 4 台 G1 机器人：目标动画（着色显示）、零平移下的目标（绿色）、实测传感器数据（红色），以及电机温度热力图（白色，带每个关节的颜色指示：按温度由绿 → 黄 → 橙 → 红 / 闪烁）。

**配置：**
- 默认端口：5557（可用 `--zmq-out-port <port>` 修改）
- 默认 topic：`g1_debug`（可在可执行程序上用 `--zmq-out-topic <topic>`、在可视化脚本上用 `--realtime_debug_topic <topic>` 修改）
- 对于真机，请将 `localhost` 替换为机器人的 IP 地址

**回放控制：**
- **Space**（空格）：暂停 / 恢复回放
- **`.`**（句号）：向前单步一帧
- **`,`**（逗号）：向后单步一帧
- **`r`**：重置到第 0 帧

### 策略输入日志

**策略输入（`--policy-input-logfile <path>`）：**
- 记录输入神经网络策略的原始观测张量
- 输出：单个 CSV 文件（每个控制步一行，包含所有观测值）
- 可用于调试观测配置与输入漂移

### 控制输入录制 / 回放

**录制（`--record-input-file <path>`）：**
- 记录控制输入（动作索引、帧、操作员状态、规划器状态、移动指令）
- 控制系统被激活时开始记录
- 提示：从龙门架上放下机器人后，先等几秒再启动控制，以便在回放时给自己留出准备时间

**回放（`--playback-input-file <path>`）：**
- 重放录制的控制输入，实现可复现实验
- 控制系统被激活时开始回放
- 适合在完全相同的输入下测试策略改动

### 机器人状态 CSV 记录器

通过 `--enable-csv-logs` 启用后，系统会在每个控制步（50 Hz）记录详细的机器人状态。

**输出目录：**
- 默认：`logs/dd-mm-yy/hh-mm-ss`（自动生成时间戳）
- 自定义：使用 `--logs-dir <path>` 指定目录

**生成的文件（按信号类型拆分）：**
- `base_quat.csv` — 基座 IMU 四元数（4 个值：w, x, y, z）
- `base_ang_vel.csv` — 基座角速度（3 个值：x, y, z）
- `torso_quat.csv` — 躯干 IMU 四元数（4 个值）
- `torso_ang_vel.csv` — 躯干角速度（3 个值）
- `q.csv` — 关节位置（29 个关节）
- `dq.csv` — 关节速度（29 个关节）
- `action.csv` — 策略动作（29 个关节）

**CSV 格式：**
- 列：`index,time_ms,...`
- `time_ms`：距首次记录的毫秒数（起始为 0.0，允许小数）
- 所有文件使用相同的 index/时间戳保持同步

**示例：**

```sh
just run g1_deploy_onnx_ref enp5s0 policy/model.onnx reference/motions/ \
  --obs-config policy/obs_config.yaml \
  --enable-csv-logs \
  --logs-dir logs/my_experiment
```

## 观测配置

系统使用 YAML 配置文件定义哪些观测会输入策略，从而在不修改代码的前提下实现灵活的策略设计。

**基本结构（`--obs-config <path>`）：**

```yaml
observations:
  - name: "body_joint_positions"
    enabled: true
  - name: "base_angular_velocity"
    enabled: true
  # ... 其他观测
```

**配合编码器（基于 token 的策略）：**

对于使用编码 token 的策略，需增加 `encoder:` 配置段：

```yaml
observations:
  - name: "token_state"           # 编码器输出（64 维 token）
    enabled: true
  - name: "base_angular_velocity" # 直接观测
    enabled: true

encoder:
  dimension: 64       # token 输出维度
  use_fp16: false     # TensorRT 精度（可选）
  encoder_observations:
    - name: "motion_joint_positions_10frame_step5"
      enabled: true
    # ... 输入编码器的观测
```

然后运行时通过 `--encoder-file <path>` 加载编码器模型。若省略该参数，token 可通过 ROS2/ZMQ 由外部设置。

**完整观测参考：**

关于所有可用观测名称、维度与示例配置的完整列表，请参见 [观测配置](observation_config.md)。

**示例：**
- 参见 `policy/observation_config_example.yaml`
