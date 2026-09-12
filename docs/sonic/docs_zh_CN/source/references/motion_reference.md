# 参考动作数据

本页介绍 C++ 部署栈所使用的参考动作数据格式、如何创建你自己的参考动作，以及如何校验和部署它们。

部署栈会回放预加载的**参考动作**（reference motions）——即策略所跟踪的关节位置、速度与全身运动学序列。这些动作以 CSV 文件的形式存储在结构化的目录层级中。只要输出符合下文描述的格式，你可以从任何来源（动作捕捉、仿真、重定向流水线等）生成它们。

---

## 目录结构

每个动作数据集是一个目录，其中每个动作片段对应一个子文件夹。C++ 读取器（`MotionDataReader`）会在启动时自动发现所有子文件夹。

```
reference/my_motions/
├── motion_name_1/
│   ├── joint_pos.csv          # 关节位置
│   ├── joint_vel.csv          # 关节速度
│   ├── body_quat.csv          # 刚体四元数
│   ├── body_pos.csv           # 刚体位置
│   ├── metadata.txt           # Body part indexes（身体部件索引）
│   ├── body_lin_vel.csv       # 刚体线速度
│   ├── body_ang_vel.csv       # 刚体角速度
│   ├── smpl_joint.csv         # SMPL 关节位置
│   ├── smpl_pose.csv          # SMPL 身体姿态
│   └── info.txt               # 详细的动作信息
└── motion_name_2/
    └── ...
```

C++ 读取器会扫描基础目录以寻找子文件夹，将每个子文件夹读取为一个动作，并校验该文件夹内所有文件的帧数一致性。
---

## 文件格式

C++ 读取器会加载所有存在的文件，并优雅地跳过缺失的文件。但在**实际使用中**，大多数策略需要：
- `joint_pos.csv`、`joint_vel.csv` —— 用于基于关节的动作跟踪
- `body_quat.csv` —— 用于锚点朝向观测（采集观测时若缺失此文件，控制循环将停止）
- `body_pos.csv` —— 用于朝向计算与 VR 三点观测
- `metadata.txt` —— 当存在刚体数据时，用于身体部件索引对齐

一个动作必须**至少拥有一个有效数据源**（关节、刚体或 SMPL）才能在启动时加载。

### `joint_pos.csv`

以 **IsaacLab 顺序**（29 个关节）表示的关节位置。每一行为一个 50 Hz 的时间步。第一行为表头。

| 列 | 说明 |
|--------|-------------|
| `joint_0` … `joint_28` | 关节角度，单位为弧度（IsaacLab 顺序） |

形状：`(timesteps, 29)`

### `joint_vel.csv`

以 **IsaacLab 顺序**（29 个关节）表示的关节速度。每一行为一个 50 Hz 的时间步。帧数必须与 `joint_pos.csv` 一致。

| 列 | 说明 |
|--------|-------------|
| `joint_vel_0` … `joint_vel_28` | 关节角速度，单位为 rad/s（IsaacLab 顺序） |

形状：`(timesteps, 29)`

### `body_pos.csv`

**世界坐标系**下的刚体位置。每个刚体贡献 3 列（x、y、z）。刚体数量因动作而异。朝向计算与 VR 三点观测需要此文件。

| 列 | 说明 |
|--------|-------------|
| `body_0_x`, `body_0_y`, `body_0_z` | 刚体 0（根节点/骨盆）的位置，单位为米 |
| `body_1_x`, `body_1_y`, `body_1_z` | 刚体 1 的位置，单位为米 |
| … | … |

形状：`(timesteps, num_bodies * 3)`

**我们假定根节点/骨盆始终位于列组 0**（前 3 列）。

### `body_quat.csv`

**世界坐标系**下以四元数表示的刚体朝向。每个刚体贡献 4 列。四元数顺序为 **(w, x, y, z)**（标量在前）。**大多数策略都需要此文件** —— 若缺失此文件，`motion_anchor_orientation` 观测（大多数策略都会使用）将失败并使控制系统停止。

| 列 | 说明 |
|--------|-------------|
| `body_0_w`, `body_0_x`, `body_0_y`, `body_0_z` | 刚体 0（根节点/骨盆）的四元数 |
| `body_1_w`, `body_1_x`, `body_1_y`, `body_1_z` | 刚体 1 的四元数 |
| … | … |

形状：`(timesteps, num_bodies * 4)`

**我们假定根节点/骨盆始终位于列组 0**（前 4 列）。

```{note}
`body_quat.csv` 中的刚体数量可以与 `body_pos.csv` 不同。C++ 读取器会分别独立跟踪它们（`num_bodies` 与 `num_body_quaternions`）。但根刚体（第一个列组）必须存在，朝向计算才能正常工作。如果不需要根节点位置，可以填零。
```

### `metadata.txt`

包含 **body part indexes**（身体部件索引）数组，它将 `body_pos.csv` / `body_quat.csv` 中的每个列组映射到对应的 IsaacLab 身体索引。当存在刚体数据时需要此文件。

```
Metadata for: motion_name
==============================

Body part indexes:
[ 0  4 10 18  5 11 19  9 16 22 28 17 23 29]

Total timesteps: 497
```

C++ 读取器会解析 `Body part indexes:` 之后方括号内一行以空格分隔的整数。例如，`[0, 4, 10, 18, ...]` 表示列组 0 → IsaacLab 刚体 0（骨盆/根节点），列组 1 → 刚体 4，以此类推。

对于**仅含根节点**的动作（只有 1 个刚体），使用：

```
Body part indexes:
[0]
```

### `body_lin_vel.csv` / `body_ang_vel.csv`

世界坐标系下的刚体线速度与角速度。布局与 `body_pos.csv` 相同（每个刚体 3 列）。刚体数量必须与 `body_pos.csv` 一致。

### `smpl_joint.csv`

SMPL 关节位置（通常为 24 个关节 × 3 个坐标）。每一行为一个时间步。

形状：`(timesteps, num_smpl_joints * 3)`

### `smpl_pose.csv`

以轴角（axis-angle）表示的 SMPL 身体姿态（通常为 21 个姿态 × 3 个坐标）。每一行为一个时间步。

形状：`(timesteps, num_smpl_poses * 3)`

```{note}
**当前的参考动作跟踪流水线仅使用基于关节的跟踪**（编码器模式 0）。若要启用基于 SMPL 的参考动作跟踪（编码器模式 2），需要修改代码以检测 SMPL 数据的存在，并据此切换编码器模式。
```

### `info.txt`

包含形状、数据类型与取值范围的可读摘要。C++ 部署栈不会读取它 —— 纯粹用于文档说明。

---

## 创建你自己的参考动作

你可以从任何来源生成参考动作 —— 唯一的要求是产出符合上述格式的 CSV 文件。常见方法：

1. **动作捕捉重定向** —— 将人类动作捕捉数据重定向到 G1 模型，导出关节位置/速度与刚体运动学。
2. **仿真录制** —— 以 50 Hz 从 IsaacLab 或 MuJoCo 仿真中记录关节状态。
3. **程序化生成** —— 以编程方式创建关节轨迹。

### 所需的最小文件集

为 SONIC 策略创建一个可运行动作所需的**最小**文件集：

1. **`joint_pos.csv`** —— 29 个关节位置（IsaacLab 顺序），表头 + 每个时间步一行
2. **`joint_vel.csv`** —— 29 个关节速度（IsaacLab 顺序），表头 + 每个时间步一行
3. **`body_quat.csv`** —— 根节点四元数（w, x, y, z），表头 + 每个时间步一行
4. **`body_pos.csv`** —— 根节点位置（x, y, z），表头 + 每个时间步一行。如果不需要位置跟踪，可以全部填零。
5. **`metadata.txt`** —— 身体部件索引（仅含根节点时就是 `[0]`）

**示例文件：**

`joint_pos.csv`：
```
joint_0,joint_1,joint_2,...,joint_28
0.128441,0.102713,0.020116,...,0.045231
0.130124,0.104532,0.021045,...,0.046112
...
```

`joint_vel.csv`：
```
joint_vel_0,joint_vel_1,...,joint_vel_28
0.143671,0.143864,...,0.012345
...
```

`body_quat.csv`（仅根节点四元数）：
```
body_0_w,body_0_x,body_0_y,body_0_z
0.999123,0.000456,0.001234,0.040567
...
```

`body_pos.csv`（根节点位置，可以全为零）：
```
body_0_x,body_0_y,body_0_z
0.000000,0.000000,0.000000
...
```

`metadata.txt`：
```
Metadata for: my_motion
==============================

Body part indexes:
[0]

Total timesteps: 100
```

这样就得到了一个**仅含根节点**的动作（1 个刚体 = 骨盆/根节点），大多数策略都能跟踪它。


### 提供的转换脚本

项目中附带了一个便捷脚本 `reference/convert_motions.py`，用于将 **joblib pickle**（`.pkl`）文件转换为上述格式。这只是一种可能的来源 —— 你可以使用任何能产出正确 CSV 输出的工具或流水线。

```bash
cd gear_sonic_deploy
python reference/convert_motions.py <pkl_file> [output_dir]
```

该 pickle 应为一个字典，其中每个键是动作名称，每个值包含 `joint_pos`、`joint_vel`、`body_pos_w`、`body_quat_w`、`body_lin_vel_w`、`body_ang_vel_w`、`_body_indexes` 与 `time_step_total`。

---

## 校验参考动作

### MuJoCo 可视化

使用自带的可视化工具检查动作在 G1 模型上是否表现正确：

```bash
cd gear_sonic_deploy
python visualize_motion.py --motion_dir reference/my_motions/motion_name_1/
```

**控制按键：**
- **Space（空格）**：暂停 / 恢复播放
- **R**：重置到第 0 帧
- **,** / **.**：向后 / 向前逐帧步进
- **-** / **=**：上一个 / 下一个动作（若加载了多个）

请确认：
- 机器人直立站立，不会穿入地面
- 关节角度看起来合理（无极端姿态）
- 动作播放平滑，没有突然的跳变
- 刚体位置跟踪预期的轨迹

---

## 使用参考动作

### 通过 `deploy.sh` 使用

通过 `--motion-data` 传入动作目录：

```bash
./deploy.sh --motion-data reference/my_motions/ sim
```

或者使用默认动作（在 `deploy.sh` 中配置）：

```bash
./deploy.sh sim
```

### 运行时使用

部署完成后，使用键盘或手柄浏览并播放动作：

- **T**：播放当前动作
- **N / P**：下一个 / 上一个动作
- **R**：从第 0 帧重新开始

完整的控制说明参见[键盘教程](../tutorials/keyboard.md)。

---

## 校验规则

C++ 读取器在加载时执行以下校验：

- **帧数一致性**：动作文件夹内所有 CSV 文件的行数（不含表头）必须相同。不一致会导致该动作被跳过并报错。
- **关节数一致性**：`joint_pos.csv` 与 `joint_vel.csv` 的列数必须相同。
- **刚体数一致性**：`body_lin_vel.csv` 与 `body_ang_vel.csv` 的刚体列数必须与 `body_pos.csv` 相同。
- **至少一个数据源**：动作必须至少包含某种有效数据（关节、刚体或 SMPL）才能被加载。
- **元数据解析**：`metadata.txt` 文件必须包含 `Body part indexes:` 一行及其后方括号内的整数列表，动作才能获得正确的身体部件对齐。

如果某个动作未通过校验，它会被跳过并打印一条警告。部署将继续使用其余有效的动作。

---

## 注意事项

- 所有数据均为 **50 Hz**（每个时间步 0.02 s），与控制循环频率一致。
- 关节顺序遵循 **IsaacLab 约定**（而非 MuJoCo）。C++ 部署栈在发送电机指令时会在内部处理转换。
- 刚体四元数采用 **(w, x, y, z)**（标量在前）顺序。
- 第一个刚体（列组 0）必须对应根节点/骨盆，朝向计算与锚点朝向观测才能正常工作。
- 虽然 C++ 读取器可以加载没有 `body_quat.csv` 的动作，但如果策略观测了 `motion_anchor_orientation`（大多数策略都会），控制循环会在采集观测时失败。
- CSV 文件必须以**表头行**作为第一行 —— C++ 读取器会跳过每个 CSV 的第一行。
- 数值在内部以 `double` 精度解析。
