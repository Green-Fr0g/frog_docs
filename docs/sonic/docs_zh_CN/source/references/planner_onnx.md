# 运动学规划器 ONNX 模型参考

本页给出**运动学规划器（Kinematic Planner）**ONNX 模型输入与输出的详细规格。运动学规划器是 GEAR-SONIC 系统的核心动作生成组件：给定机器人当前状态与高层导航指令，它生成一段未来的全身姿态序列（MuJoCo `qpos` 帧），再由底层全身控制器进行跟踪。

该 ONNX 模型属于 **C++ 推理栈**，由部署运行时在运行过程中调用。C++ 栈负责输入构造、时序与状态管理——某些输入组合是无效的，由 C++ 层处理以保证运行安全。本页面向希望深入理解模型接口、或在标准部署流水线之外构建自定义集成的开发者。

```{admonition} 训练代码与技术报告
:class: note
运动学规划器的训练代码与技术报告即将发布。本页记录的是用于部署集成的 ONNX 模型接口。
```

---

## 概览

规划器接收 **11 个输入张量**，产生 **2 个输出张量**。6 个主要输入如下所列；其余 5 个是 <a href="#advanced-inputs">高级输入</a>，由 C++ 栈管理，大多数情况下无需修改。

**主要输入：**

| 张量名 | 形状 | Dtype | 默认值 |
|-------------|-------|-------|---------|
| `context_mujoco_qpos` | `[1, 4, 36]` | `float32` | 必填 |
| `target_vel` | `[1]` | `float32` | `-1.0`（使用模式默认速度） |
| `mode` | `[1]` | `int64` | 必填 |
| `movement_direction` | `[1, 3]` | `float32` | 必填 |
| `facing_direction` | `[1, 3]` | `float32` | 必填 |
| `height` | `[1]` | `float32` | `-1.0`（禁用高度控制） |

**输出：**

| 张量名 | 形状 | Dtype |
|-------------|-------|-------|
| `mujoco_qpos` | `[1, N, 36]` | `float32` |
| `num_pred_frames` | 标量 | `int64` |

其中：
- **K** = `max_tokens - min_tokens + 1`（取决于具体模型；即允许的预测时域范围）
- **N** = 输出帧数上限（已填充/补齐）；仅前 `num_pred_frames` 帧有效

---

## 坐标系

模型运行在 **MuJoCo 的 Z-up（Z 轴朝上）坐标约定**下：

- **X** — 朝前
- **Y** — 朝左
- **Z** — 朝上

输入与输出中的所有位置向量和方向向量均遵循该约定。

---

## 输入张量

(context_mujoco_qpos)=
### `context_mujoco_qpos`

| 属性 | 值 |
|----------|-------|
| **形状** | `[1, 4, 36]` |
| **Dtype** | `float32` |
| **描述** | 规划器的上下文输入，由 4 个连续的 MuJoCo `qpos` 帧组成，表示机器人近期的状态 |

这是主要的上下文输入。它提供机器人近期 4 帧的关节配置，按仿真帧率采样。每帧的 36 个维度是 Unitree G1（29 自由度）模型的标准 MuJoCo `qpos` 向量：

| 索引 | 字段 | 描述 |
|-------|-------|-------------|
| 0–2 | 根节点位置 | `(x, y, z)`，单位为米，Z-up 世界坐标系 |
| 3–6 | 根节点四元数 | `(w, x, y, z)` 姿态——MuJoCo 约定 |
| 7–35 | DOF 位置 | 29 个关节角度，单位为弧度，遵循 MuJoCo 刚体树顺序 |

```{admonition} 坐标系
:class: note
所有输入——包括 `context_mujoco_qpos`、`movement_direction`、`facing_direction`、`specific_target_positions` 和 `specific_target_headings`——都应以**世界坐标系**给出。根节点四元数在索引 3 至 6 处使用 MuJoCo 的 `(w, x, y, z)` 顺序。模型在内部完成规范化（canonicalization）处理。
```

### `target_vel`

| 属性 | 值 |
|----------|-------|
| **形状** | `[1]` |
| **Dtype** | `float32` |
| **描述** | 覆盖默认的期望移动速度 |

控制目标移动速度。当设为**零或负值**（如 `-1.0`）时，模型使用所选模式的默认速度。当设为**正值**时，覆盖该模式的默认速度（单位为米/秒）。注意，由于临界阻尼弹簧模型和运动动力学的影响，实际达到的速度可能与目标速度不同。

| 取值 | 行为 |
|-------|----------|
| `<= 0.0` | 使用所选 `mode` 的默认速度 |
| `> 0.0` | 以该目标速度覆盖（m/s） |


### `mode`

| 属性 | 值 |
|----------|-------|
| **形状** | `[1]` |
| **Dtype** | `int64` |
| **描述** | 选择动作风格/行为的索引 |

从预加载的动作片段库中选择动作风格。运行时模式索引会被钳位到可用片段数量以内。默认规划器内置以下模式：

**移动（locomotion）模式集：**

| 索引 | 模式 | 描述 |
|-------|------|-------------|
| 0 | `idle` | 原地站立 |
| 1 | `slowWalk` | 缓慢前进移动 |
| 2 | `walk` | 正常行走速度 |
| 3 | `run` | 奔跑 |

**下蹲 / 贴地模式集：**

| 索引 | 模式 | 描述 |
|-------|------|-------------|
| 4 | `squat` | 下蹲——需要 `height` 输入（范围 ~0.4–0.8m） |
| 5 | `kneelTwoLeg` | 双膝跪地——需要 `height` 输入（0.2m-0.4m） |
| 6 | `kneelOneLeg` | 单膝跪地——需要 `height` 输入（0.2m-0.4m） |
| 7 | `lyingFacedown` | 俯卧——需要 `height` 输入 |
| 8 | `handCrawling` | 手膝爬行 |
| 14 | `elbowCrawling` | 肘部爬行（更容易过热） |

**拳击模式集：**

| 索引 | 模式 | 描述 |
|-------|------|-------------|
| 9 | `idleBoxing` | 拳击预备姿态（待机） |
| 10 | `walkBoxing` | 保持拳击防御姿态行走 |
| 11 | `leftJab` | 左直拳 |
| 12 | `rightJab` | 右直拳 |
| 13 | `randomPunches` | 随机出拳序列 |
| 15 | `leftHook` | 左勾拳 |
| 16 | `rightHook` | 右勾拳 |

**风格化行走：**

| 索引 | 模式 | 描述 |
|-------|------|-------------|
| 17 | `happy` | 开心行走 |
| 18 | `stealth` | 潜行 |
| 19 | `injured` | 受伤跛行 |
| 20 | `careful` | 谨慎行走 |
| 21 | `objectCarrying` | 搬运物体行走（双手前伸） |
| 22 | `crouch` | 蹲伏行走 |
| 23 | `happyDance` | 开心舞蹈式行走（仅能向前走） |
| 24 | `zombie` | 僵尸行走 |
| 25 | `point` | 指向行走（行走时用手指向） |
| 26 | `scared` | 受惊行走 |

### `movement_direction`

| 属性 | 值 |
|----------|-------|
| **形状** | `[1, 3]` |
| **Dtype** | `float32` |
| **描述** | 在 MuJoCo 世界坐标系下期望的移动方向 |

一个 Z-up 世界坐标系下的三维方向向量 `(x, y, z)`，指示机器人应当朝哪个方向移动。作为良好实践，建议传入归一化向量，不过模型内部也会做归一化。速度由 `target_vel` 和 `mode` 控制，而不是由该向量的模长控制。

- 规划器使用该向量的 `(x, y)` 分量（水平面），通过临界阻尼弹簧模型计算目标根节点轨迹。
- 当模长接近零（`< 1e-5`）时，模型退回使用 `facing_direction` 并乘以一个较小的缩放因子，实现原地转向。


### `facing_direction`

| 属性 | 值 |
|----------|-------|
| **形状** | `[1, 3]` |
| **Dtype** | `float32` |
| **描述** | 在 MuJoCo 世界坐标系下期望的面朝（朝向）方向 |

一个三维方向向量 `(x, y, z)`，指示机器人躯干应面朝的方向。目标朝向角由该向量计算为 `atan2(y, x)`。与 `movement_direction` 一样，无需归一化。

它与 `movement_direction` 相互独立——机器人可以朝一个方向行走，同时面朝另一个方向（例如横移）。


### `height`

| 属性 | 值 |
|----------|-------|
| **形状** | `[1]` |
| **Dtype** | `float32` |
| **描述** | 高度感知行为所期望的根节点高度 |

对支持可变高度的模式（如 `squat`、`kneelTwoLeg`、`kneelOneLeg`、`lyingFacedown`），该输入控制目标骨盆高度。当给定正值时，模型会在参考片段的关键帧中搜索，并选择根高度最接近请求值的关键帧，将其作为动作生成的目标姿态。

| 取值 | 行为 |
|-------|----------|
| `< 0.0` | 禁用高度控制；使用参考片段中随机选取的关键帧 |
| `>= 0.0` | 在参考片段中查找高度最接近的关键帧，并将其作为目标姿态（米） |


<div id="advanced-inputs"></div>

## 高级输入

这些输入由 C++ 部署栈在内部管理，正常运行时**不应修改**。此处仅为完整性而记录，供需要构建自定义集成的高级用户参考。

### `random_seed`

| 属性 | 值 |
|----------|-------|
| **形状** | `[1]` |
| **Dtype** | `int64` |
| **描述** | 控制网络随机性的种子 |


### `has_specific_target`

| 属性 | 值 |
|----------|-------|
| **形状** | `[1, 1]` |
| **Dtype** | `int64` |
| **描述** | 标志位，指示是否提供了具体的路径点目标 |

| 取值 | 行为 |
|-------|----------|
| `0` | 忽略 `specific_target_positions` 和 `specific_target_headings`；使用 `movement_direction` / `facing_direction` |
| `1` | 将给定的具体目标位置和朝向用作路径点约束 |

启用后，弹簧模型的目标根节点位置和朝向会被 `specific_target_positions` 和 `specific_target_headings` 中的值覆盖。


### `specific_target_positions`

| 属性 | 值 |
|----------|-------|
| **形状** | `[1, 4, 3]` |
| **Dtype** | `float32` |
| **描述** | MuJoCo 世界坐标下的 4 个路径点位置 |

每个路径点都是 Z-up 世界坐标系下的三维位置 `(x, y, z)`。4 个路径点对应 4 帧（即一个 token 的量）的目标根节点位置。仅在 `has_specific_target = 1` 时使用。


### `specific_target_headings`

| 属性 | 值 |
|----------|-------|
| **形状** | `[1, 4]` |
| **Dtype** | `float32` |
| **描述** | 4 个路径点的朝向角，单位为弧度 |

4 个路径点帧各自的目标朝向（偏航）角。它们是 Z-up 世界坐标系下的绝对角度，按绕 Z 轴的旋转度量。仅在 `has_specific_target = 1` 时使用。最后一个路径点的朝向（`[:, -1]`) 被用作弹簧模型的主目标朝向。


### `allowed_pred_num_tokens`

| 属性 | 值 |
|----------|-------|
| **形状** | `[1, K]`，其中 `K = max_tokens - min_tokens + 1` |
| **Dtype** | `int64` |
| **描述** | 控制允许的预测时域的二值掩码 |

一个二值掩码，每个元素对应一种可能的预测 token 数。索引 `i` 映射到 `min_tokens + i` 个 token。取值 `1` 表示允许该预测长度；`0` 表示不允许。

由于每个 token 代表 4 帧，以帧数计的预测时域为 `num_tokens * 4`。在默认规划器中，`min_tokens = 6`、`max_tokens = 16`：

| 索引 | Token 数 | 帧数 |
|-------|--------|--------|
| 0 | 6 | 24 |
| 1 | 7 | 28 |
| 2 | 8 | 32 |
| 3 | 9 | 36 |
| 4 | 10 | 40 |
| 5 | 11 | 44 |
| 6 | 12 | 48 |
| 7 | 13 | 52 |
| 8 | 14 | 56 |
| 9 | 15 | 60 |
| 10 | 16 | 64 |

---

## 输出张量

### `mujoco_qpos`

| 属性 | 值 |
|----------|-------|
| **形状** | `[1, N, 36]` |
| **Dtype** | `float32` |
| **描述** | 以 MuJoCo `qpos` 帧表示的预测动作序列 |

主要输出：与输入相同格式的 36 维 MuJoCo `qpos` 全身姿态帧序列（维度布局见 {ref}`context_mujoco_qpos <context_mujoco_qpos>`）。

```{admonition} 重要：使用 num_pred_frames 进行截断
:class: warning
输出张量 `mujoco_qpos` **不会截断**——它包含完整的填充缓冲区。只有前 `num_pred_frames` 帧是有效预测。使用该输出时，务必切片：
```

```python
valid_qpos = mujoco_qpos[:, :num_pred_frames, :]
```

姿态位于**全局 MuJoCo 世界坐标系**中（未做规范化）。模型在内部依次完成规范化、推理和坐标转换，再把输出变换回原始世界坐标系。前 4 个预测帧会与输入上下文进行融合，以获得平滑过渡。

输出中的根节点四元数采用 `(w, x, y, z)` 顺序（MuJoCo 约定）。


### `num_pred_frames`

| 属性 | 值 |
|----------|-------|
| **形状** | 标量 |
| **Dtype** | `int64` |
| **描述** | `mujoco_qpos` 输出中有效预测帧的数量 |

该值等于 `num_pred_tokens * 4`，其中 `num_pred_tokens` 是模型决定生成的运动 token 数量（受 `allowed_pred_num_tokens` 约束）。请使用该值对 `mujoco_qpos` 输出进行切片。

---

## 内部流水线

1. **规范化（canonicalization）** —— 输入 qpos 通过去除第一帧的朝向旋转和水平位置，被变换到以刚体为参考的坐标系。这有助于模型在不同起始姿态和位置之间泛化。

2. **弹簧模型** —— 临界阻尼弹簧模型根据高层指令生成平滑的目标根节点轨迹和朝向角，使用训练片段中与模式相关的平均速度。

3. **目标姿态选择** —— 根据 `mode` 和 `random_seed`，从预加载的动作片段库中取出一个目标姿态，并对齐（旋转/平移）到弹簧模型预测的目标位置和朝向。

4. **动作推理** —— 核心动作模型在上下文（当前状态）与目标（期望的未来状态）之间填补动作，生成自然的过渡。

5. **后处理** —— 输出被转换回原始世界坐标系下的 MuJoCo qpos，前 4 帧与输入上下文融合，以获得平滑过渡。

---

## 部署集成

本节描述 C++ 部署栈在运行时如何使用规划器。理解这些内容有助于构建自定义集成或修改重规划行为。

### 线程模型

规划器运行在一个**以 10 Hz 运行的专用线程**上（`planner_dt = 0.1s`），与控制循环（50 Hz）和输入线程（100 Hz）相互独立。规划器线程：

1. 从线程安全缓冲区（由输入接口写入）读取最新的 `MovementState`。
2. 判断是否需要重规划。
3. 如需要，调用 `UpdatePlanning()` 执行 TensorRT 推理。
4. 将结果存入共享缓冲区，由控制线程在下一个控制节拍（tick）读取。

### 初始化

当规划器首次被启用时（例如在键盘接口上按下 **ENTER**），规划器线程会：

1. 从最新的 `LowState` 中读取机器人当前的基座四元数和关节位置。
2. 调用 `Initialize()`，其执行以下操作：
   - 以默认站立高度、零偏航姿态设置 4 帧上下文。
   - 以 `IDLE` 模式、无移动运行一次初始推理。
   - 将 30 Hz 输出重采样到 50 Hz。
3. 控制线程检测到新的规划器动作后，将 `current_motion_` 切换为规划器输出。

### 上下文构造

规划器需要 4 帧上下文（形状为 `[1, 4, 36]` 的 `context_mujoco_qpos`）。运行过程中，该上下文从**当前规划器动作**（而非机器人状态）中采样：

- 上下文从 `gen_frame = current_frame + motion_look_ahead_steps` 处开始（默认前瞻 = 50 Hz 下的 2 帧）。
- 从该起始点开始，以 30 Hz 间隔采样 4 帧。
- 关节位置、刚体位置和四元数在 50 Hz 动作帧之间线性插值（四元数使用 slerp），得到 30 Hz 的上下文采样。

### 重规划逻辑

并非每个规划器控制节拍都会触发重规划。判断遵循以下优先级：

**1. 以下情况总是重规划**（无论静态/非静态模式）：
- 移动模式改变
- 面朝方向改变
- 高度改变

**2. 仅对非静态模式**，满足以下任一条件时也重规划：
- 移动速度改变
- 移动方向改变
- 周期性重规划计时器到期**且**移动速度非零

静态模式（待机、下蹲、跪地、俯卧、拳击待机）**绝不会**因第二类条件触发重规划——它们只在第一类的模式/面朝方向/高度变化时重规划。

**重规划间隔**（周期计时器）按移动类型区分，以平衡响应速度与计算开销：

| 移动类型 | 重规划间隔 |
|----------------|-----------------|
| 奔跑 | 0.1 s（每个规划器节拍） |
| 爬行 | 0.2 s |
| 拳击（出拳、勾拳） | 1.0 s |
| 其他所有（行走、下蹲、风格化等） | 1.0 s |

周期计时器仅在当前移动速度非零时才触发重规划——非静态模式下静止的机器人（例如速度为 0 的 Walk 模式）不会因计时器而重规划。

### 输出重采样（30 Hz → 50 Hz）

规划器模型以 **30 Hz** 输出帧。部署栈使用线性插值将其重采样到 **50 Hz**（控制循环频率）：

- 对每个 50 Hz 帧，计算对应的 30 Hz 分数帧索引。
- 在最近的两个 30 Hz 帧之间线性插值关节位置和刚体位置。
- 对刚体四元数做 slerp 插值。
- 通过对重采样后的位置做有限差分计算关节速度（`(pos[t+1] - pos[t]) * 50`）。

重采样后的动作存储在 `planner_motion_50hz_` 中，共有 `num_pred_frames * 50/30` 帧（向下取整）。

### 动作融合

当新的规划器输出到来而上一个仍在播放时，控制线程会在 8 帧的交叉淡化区间内**融合**新旧两段动画：

1. 旧动画先做重定基（rebase），使 `current_frame` 映射到第 0 帧。
2. 新动画对齐到重定基时间线上的 `gen_frame - current_frame` 处开始。
3. 从融合点开始的 8 帧内，施加一个线性递增的权重 `w_new`（0 → 1）：
   - 关节位置/速度：`w_old * old + w_new * new`
   - 刚体位置：`w_old * old + w_new * new`
   - 刚体四元数：`slerp(old, new, w_new)`
4. 融合区间之后，新动画完全接管。
5. 融合结果的 `current_frame` 重置为 0。

这保证了连续规划器输出之间平滑过渡，不会出现可见的不连续。

### TensorRT 加速

规划器通过 **TensorRT** 运行，并使用 CUDA 图捕获以实现低延迟推理：

1. 启动时，ONNX 模型被转换为 TensorRT 引擎（缓存到磁盘）。
2. 初始化时捕获一个 **CUDA 图**——它将整个推理过程（输入拷贝 → 内核启动 → 输出拷贝）记录为单个可重放的图。
3. 每次重规划时，输入通过锁页内存（`TPinnedVector`）拷贝到 GPU，启动 CUDA 图，再把输出拷贝回来。
4. 支持 FP16 精度，通过 `--planner-precision 16` 启用（默认为 FP32）。

### 规划器模型版本

部署栈支持多个规划器模型版本，从模型文件名自动检测：

| 版本 | 输入数 | 模式数 | 描述 |
|---------|--------|-------|-------------|
| V0 | 6 | 4（待机、慢走、行走、奔跑） | 仅基础移动 |
| V1 | 11 | 20 | 增加下蹲/跪地/拳击/风格化行走 + 高度控制 + 路径点目标 |
| V2 | 11 | 27 | 全部 V1 模式 + 更多风格化行走模式 |

版本由规划器模型文件名中是否含有 `V0`、`V1` 或 `V2` 决定。版本决定了：
- 输入张量的数量（6 还是 11）
- `mode` 值的有效范围
- 是否使用 `height`、`has_specific_target`、`specific_target_positions`、`specific_target_headings` 与 `allowed_pred_num_tokens` 输入

---

## 模型属性

导出的 ONNX 模型具有以下属性：

- **ONNX opset 版本**：17
- **批大小**：1（固定）

模型以单个 `.onnx` 文件发布，附带一个包含参考输入/输出张量的 `.pt` 文件，可用于校验。

```{admonition} 即将推出
:class: note
训练代码、导出工具与完整技术报告即将发布，敬请关注更新。
```

---

## 使用示例

```python
import onnxruntime as ort
import numpy as np

# Load the ONNX model
session = ort.InferenceSession("kinematic_planner.onnx")

# Primary inputs
inputs = {
    "context_mujoco_qpos": current_qpos_buffer.astype(np.float32),           # [1, 4, 36]
    "target_vel": np.array([-1.0], dtype=np.float32),                         # -1.0 = use mode default
    "mode": np.array([2], dtype=np.int64),                                    # 2 = walk
    "movement_direction": np.array([[1.0, 0.0, 0.0]], dtype=np.float32),      # forward
    "facing_direction": np.array([[1.0, 0.0, 0.0]], dtype=np.float32),        # face forward
    "height": np.array([-1.0], dtype=np.float32),                             # -1.0 = disabled

    # Advanced inputs (typically managed by the C++ stack)
    "random_seed": np.array([1234], dtype=np.int64),
    "has_specific_target": np.array([[0]], dtype=np.int64),
    "specific_target_positions": np.zeros([1, 4, 3], dtype=np.float32),
    "specific_target_headings": np.zeros([1, 4], dtype=np.float32),
    "allowed_pred_num_tokens": np.ones([1, 11], dtype=np.int64),              # K = 11 for default model
}

# Run inference
mujoco_qpos, num_pred_frames = session.run(None, inputs)

# Extract valid frames only
num_frames = int(num_pred_frames)
predicted_motion = mujoco_qpos[0, :num_frames, :]  # [num_frames, 36]

# Each row: [x, y, z, qw, qx, qy, qz, 29 joint angles in radians]
for frame in predicted_motion:
    root_pos = frame[:3]
    root_quat = frame[3:7]       # (w, x, y, z)
    joint_angles = frame[7:36]   # 29 DOF positions
```
