# 使用键盘控制的动作跟踪与运动学规划器

<figure style="margin: 1em 0;">
<video width="100%" autoplay loop muted playsinline style="border-radius: 8px;">
  <source src="../_static/kinematic_planner/Navigation.mp4" type="video/mp4">
</video>
<figcaption style="text-align: center; font-style: italic; margin-top: 0.5em;">使用运动学规划器与键盘控制的实景导航演示。</figcaption>
</figure>

```{video} ../_static/Keyboard_Guidance.mp4
:width: 100%
```
*视频：键盘控制流程演示——启动控制系统、播放参考动作，以及使用规划器模式进行实时移动。*

使用键盘指令控制机器人，进行参考动作回放与基于规划器的移动（使用 `--input-type keyboard`）。

```{admonition} 前置条件
:class: note
完成[快速上手](../getting_started/quickstart.md)，使 sim2sim 循环可以运行。
```

```{admonition} 紧急停止
:class: danger
随时可按 **`O`** 立即停止控制并退出。请始终将一只手放在键盘附近，随时准备按下 **`O`**。
```

## 启动

**Sim2Sim（MuJoCo）：**

```bash
# Terminal 1 — MuJoCo simulator (from repo root)
source .venv_sim/bin/activate
python gear_sonic/scripts/run_sim_loop.py

# Terminal 2 — C++ deployment (from gear_sonic_deploy/)
bash deploy.sh --input-type keyboard sim
```

**真机：**

```bash
# From gear_sonic_deploy/
bash deploy.sh --input-type keyboard real
```

## 分步操作：普通模式（参考动作跟踪）

普通模式回放预加载的参考动作。这是程序启动时的默认模式。

1. 在终端 2 中按 **`]`** 启动控制系统。
2. 在 MuJoCo 窗口中按 **`9`** 让机器人落到地面。
3. 回到终端 2，按 **`T`** 播放当前参考动作——机器人会将其执行至结束。
4. 按 **`N`** 切换到下一个动作序列，按 **`P`** 切换到上一个。
5. 再次按 **`T`** 播放新的动作。
6. 要重播同一动作，在其结束后再次按 **`T`**。要在动作中途停止并回到第一帧，按 **`R`**——机器人会停在第 0 帧但不会终止策略。
7. 使用 **`Q`** / **`E`** 向左/向右微调朝向（每次按压 ±π/12 rad）。
8. 按 **`I`** 重新初始化基座四元数并将朝向重置为零，即机器人会将当前面朝的方向视为参考动作第一帧时的朝向。
9. 操作完成后，按 **`O`** 停止控制并退出。

## 分步操作：规划器模式（实时动作生成）

规划器模式让你实时控制机器人——选择移动风格，用 WASD 转向，并随时调整速度与高度。

1. 在普通模式下按 **`ENTER`** 切换到规划器模式。终端将打印 `Planner enabled`。
2. 机器人以**移动（Locomotion）**动作集启动。按 **`1`** 慢走、**`2`** 行走，或 **`3`** 奔跑。
3. 按 **`W`** 前进。机器人采用动量系统——按住方向键会将动量设为满值；松开后机器人逐渐减速并回到待机。
4. 用 **`A`** / **`D`** 转向（同时调整朝向与移动方向），或用 **`Q`** / **`E`** 原地转向（每次按压 ±π/6 rad，仅改变面朝方向）。
5. 按 **`,`** / **`.`** 向左 / 向右横移。
6. 按 **`S`** 后退。
7. 用 **`9`**（减小）/ **`0`**（增大）调整速度。速度范围取决于当前模式（见下表）。
8. 按 **`N`** 循环切换到下一个动作集（移动 → 下蹲 → 拳击 → 风格化行走 → …）。用 **`P`** 返回。
9. 在一个动作集内，按 **`1`**–**`8`** 选择具体模式（见下方"动作集"一节）。
10. 下蹲类模式可用 **`-`**（降低）/ **`=`**（升高）调整身体高度，限制在 0.2–0.8 m 范围内。
11. 如需立即停止，按 **`R`**、**`` ` ``** 或 **`~`**——这会将移动动量瞬间重置为零。
12. 再按 **`ENTER`** 返回普通模式，或按 **`O`** 停止并退出。

## 控制参考

### 系统控制（两种模式通用）

| 按键 | 动作 |
|-----|--------|
| **]** | 启动控制系统 |
| **O** | 停止控制并退出（急停） |
| **ENTER** | 在普通 / 规划器模式之间切换 |
| **I** | 重新初始化基座四元数并重置朝向 |
| **Z** | 切换 encoder 模式（在模式 0 与模式 1 之间，若已加载 encoder） |
| **F** | 播报电机温度（TTS 语音提示） |

### 普通模式按键

| 按键 | 动作 |
|-----|--------|
| **T** | 将当前动作播放至结束 |
| **R** | 从头重新开始当前动作（停在第 0 帧） |
| **P** / **N** | 上一个 / 下一个动作序列 |
| **Q** / **E** | 向左 / 向右调整朝向增量（策略层面，±π/12 rad） |

### 规划器模式按键

**移动：**

| 按键 | 动作 |
|-----|--------|
| **W** / **S** | 前进 / 后退 |
| **A** / **D** | 略微调整朝向并前进（左 / 右） |
| **,** / **.** | 向左 / 向右横移 |

**朝向：**

| 按键 | 动作 |
|-----|--------|
| **Q** / **E** | 向左 / 向右调整面朝方向（规划器层面，±π/6 rad） |
| **J** / **L** | 向左 / 向右调整朝向增量（策略层面，±π/12 rad） |

**模式与速度：**

| 按键 | 动作 |
|-----|--------|
| **N** / **P** | 下一个 / 上一个动作集 |
| **1**–**8** | 在当前动作集内选择模式 |
| **9** / **0** | 减小 / 增大移动速度 |
| **-** / **=** | 降低 / 升高高度（非站立类动作集，0.2–0.8 m） |
| **T** | 播放动作 |

**紧急：**

| 按键 | 动作 |
|-----|--------|
| **R** / **`** / **~** | 急停（瞬间动量重置） |

## 动作集

**动作集**是一组相关移动风格的集合（如移动、手势或下蹲）。选中集合内的某个模式后，机器人会以该风格行动。每个动作集最多包含 8 个可选模式。

用 **`N`**（下一个）/ **`P`**（上一个）在动作集之间循环。在每个动作集内，按 **`1`**–**`8`** 选择模式。底层规划器模型、模式索引与输入/输出规格的更多细节，见[运动学规划器 ONNX 模型参考](../references/planner_onnx.md)。

### 动作集 0 — 移动（站立）

| 按键 | 模式 | 速度范围 |
|-----|------|-------------|
| **1** | 慢走（Slow Walk） | 0.2–0.8 m/s |
| **2** | 行走（Walk） | — |
| **3** | 奔跑（Run） | 1.5–3.0 m/s |
| **4** | 开心（Happy） | — |
| **5** | 潜行（Stealth） | — |
| **6** | 受伤（Injured） | — |

```{tip}
使用 **`,`** / **`.`** 横移（侧向迈步）时，建议将目标速度保持在 **0.4 m/s** 左右。横移速度过高时，侧向迈步所需的交叉腿部落足方式可能导致机器人双脚碰撞。
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1em; margin: 1em 0;">
<figure style="margin: 0;">
<video width="100%" autoplay loop muted playsinline style="border-radius: 8px;">
  <source src="../_static/kinematic_planner/planner_happy.mp4" type="video/mp4">
</video>
<figcaption style="text-align: center; font-style: italic; margin-top: 0.5em;">开心风格化行走。</figcaption>
</figure>
<figure style="margin: 0;">
<video width="100%" autoplay loop muted playsinline style="border-radius: 8px;">
  <source src="../_static/kinematic_planner/planner_stealth.mp4" type="video/mp4">
</video>
<figcaption style="text-align: center; font-style: italic; margin-top: 0.5em;">潜行风格化行走。</figcaption>
</figure>
<figure style="margin: 0;">
<video width="100%" autoplay loop muted playsinline style="border-radius: 8px;">
  <source src="../_static/kinematic_planner/planner_injured.mp4" type="video/mp4">
</video>
<figcaption style="text-align: center; font-style: italic; margin-top: 0.5em;">受伤风格化行走。</figcaption>
</figure>
<figure style="margin: 0;">
<video width="100%" autoplay loop muted playsinline style="border-radius: 8px;">
  <source src="../_static/kinematic_planner/planner_run.mp4" type="video/mp4">
</video>
<figcaption style="text-align: center; font-style: italic; margin-top: 0.5em;">奔跑移动模式。</figcaption>
</figure>
</div>

### 动作集 1 — 下蹲 / 贴地

可用 **`-`** / **`=`** 调整高度（0.2–0.8 m）。进入该动作集时初始高度默认为 0.8 m。

| 按键 | 模式 | 速度范围 |
|-----|------|-------------|
| **1** | 下蹲（Squat） | 静态 |
| **2** | 双膝跪地（Kneel Two Legs） | 静态 |
| **3** | 单膝跪地（Kneel One Leg） | 静态 |
| **4** | 手膝爬行（Hand Crawling） | 0.4–1.0 m/s |
| **5** | 肘部爬行（Elbow Crawling） | 0.7–1.0 m/s |

<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1em; margin: 1em 0;">
<figure style="margin: 0;">
<video width="100%" autoplay loop muted playsinline style="border-radius: 8px;">
  <source src="../_static/kinematic_planner/planner_kneeling.mp4" type="video/mp4">
</video>
<figcaption style="text-align: center; font-style: italic; margin-top: 0.5em;">跪地模式，高度可调。</figcaption>
</figure>
<figure style="margin: 0;">
<video width="100%" autoplay loop muted playsinline style="border-radius: 8px;">
  <source src="../_static/kinematic_planner/hand_crawling.mp4" type="video/mp4">
</video>
<figcaption style="text-align: center; font-style: italic; margin-top: 0.5em;">手膝爬行移动。</figcaption>
</figure>
<figure style="margin: 0;">
<video width="100%" autoplay loop muted playsinline style="border-radius: 8px;">
  <source src="../_static/kinematic_planner/planner_elbow_crawling.mp4" type="video/mp4">
</video>
<figcaption style="text-align: center; font-style: italic; margin-top: 0.5em;">肘部爬行移动。</figcaption>
</figure>
</div>

### 动作集 2 — 拳击

| 按键 | 模式 | 速度范围 |
|-----|------|-------------|
| **1** | 待机拳击（Idle Boxing） | 静态 |
| **2** | 行走拳击（Walk Boxing） | 0.7–1.5 m/s |
| **3** | 左直拳（Left Jab） | 0.7–1.5 m/s |
| **4** | 右直拳（Right Jab） | 0.7–1.5 m/s |
| **5** | 随机出拳（Random Punches） | 0.7–1.5 m/s |
| **6** | 左勾拳（Left Hook） | 0.7–1.5 m/s |
| **7** | 右勾拳（Right Hook） | 0.7–1.5 m/s |

<figure style="margin: 1em 0;">
<video width="100%" autoplay loop muted playsinline style="border-radius: 8px;">
  <source src="../_static/kinematic_planner/planner_boxing.mp4" type="video/mp4">
</video>
<figcaption style="text-align: center; font-style: italic; margin-top: 0.5em;">拳击模式演示。</figcaption>
</figure>

### 动作集 3 — 更多风格化行走

| 按键 | 模式 |
|-----|------|
| **1** | 谨慎（Careful） |
| **2** | 搬运物体（Object Carrying） |
| **3** | 蹲伏（Crouch） |
| **4** | 开心舞蹈（Happy Dance） |
| **5** | 僵尸（Zombie） |
| **6** | 指向（Point） |
| **7** | 受惊（Scared） |

## 移动动量系统

键盘模式下的规划器使用基于动量的移动系统：
- 按下方向键（**W/S/A/D/,/.**）会将动量设为 **1.0**（全速）。
- 每个未按下方向键的帧，动量按乘法衰减（×0.999）。
- 当动量降到 **0.1** 以下时，机器人切换为待机（移动动作集）或保持当前静态姿态（下蹲与拳击动作集）。
- 急停（**R/`/~**）会将动量瞬间重置为零。

这意味着你不需要一直按住按键——单次按压即可启动移动，机器人随后自然滑行减速停止。
