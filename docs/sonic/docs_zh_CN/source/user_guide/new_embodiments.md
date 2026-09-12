# 新机器人本体（Embodiment）训练

SONIC 的训练流水线围绕 Unitree G1（29 自由度）设计，但可以扩展到其他人形机器人。本指南以 Unitree H2（31 自由度）为例，逐一讲解需要改动的每个文件。

## 所需准备

要让 SONIC 在新机器人上训练，你需要：

1. **机器人模型文件** — URDF 或 USD（用于 Isaac Lab）以及 MJCF/XML（用于动作库）
2. **重定向后的动作数据** — 重定向到你的机器人骨架的人体动作（PKL 格式）
3. **机器人配置** — 关节/刚体定义、执行器参数、动作缩放
4. **实验配置** — 将所有内容连接在一起的 Hydra YAML

## 需要添加或修改的文件

以下是需要关注的全部文件，按处理顺序排列：

| 文件 | 操作 | 用途 |
|------|--------|---------|
| `gear_sonic/data/assets/robot_description/urdf/<robot>/` | **添加** | 用于 Isaac Lab 仿真的 URDF + 网格文件 |
| `gear_sonic/data/assets/robot_description/mjcf/<robot>.xml` | **添加** | 用于动作库正运动学的 MuJoCo XML |
| `gear_sonic/envs/manager_env/robots/<robot>.py` | **添加** | 机器人配置：关节、执行器、映射、动作缩放 |
| `gear_sonic/envs/manager_env/robots/__init__.py` | **修改** | 导入你的新机器人模块 |
| `gear_sonic/envs/manager_env/modular_tracking_env_cfg.py` | **修改** | 将机器人加入 `robot_mapping` 字典（约第 998 行） |
| `gear_sonic/trl/utils/order_converter.py` | **修改** | 添加用于关节/刚体重排序的转换器类 |
| `gear_sonic/config/exp/manager/universal_token/all_modes/sonic_<robot>.yaml` | **添加** | 实验配置 |
| 各配置 YAML（终止、奖励、指令） | **检查** | 刚体名称必须存在于你的机器人上 |

## 第 1 步：机器人模型文件

将 URDF 和网格文件放在 `gear_sonic/data/assets/robot_description/` 目录下：

```
gear_sonic/data/assets/robot_description/
├── urdf/h2/
│   ├── h2.urdf
│   └── meshes/          # STL/OBJ 网格文件
└── mjcf/
    └── h2.xml           # MuJoCo XML
```

**URDF** 由 Isaac Lab 加载用于物理仿真。**MJCF** 由动作库用于对参考动作数据计算正运动学。两者必须表示同一台机器人，且关节名称和运动学树结构保持一致。

确保 URDF 的网格路径正确（最好使用 `meshes/pelvis.stl` 这样的相对路径）。如果你的 URDF 使用 `package://` 路径，请将其更新为与目录布局一致。

## 第 2 步：机器人配置

创建 `gear_sonic/envs/manager_env/robots/<robot>.py`。这是最重要的文件——它定义你的机器人如何接入训练流水线。

### 关节与刚体顺序

Isaac Lab 和 MuJoCo 遍历运动学树的顺序不同。你必须定义双向索引映射。获取方法：在 Isaac Lab 中加载你的 URDF、在 MuJoCo 中加载你的 MJCF，打印关节/刚体列表，然后计算重排序索引。

```python
# IsaacLab 遍历顺序下的全部刚体（包括根节点 "pelvis"）
H2_ISAACLAB_JOINTS = [
    "pelvis",
    "left_hip_pitch_link",
    "right_hip_pitch_link",
    # ... H2 的全部 32 个刚体
]

# 索引数组：输出的第 i 个位置 = 输入的第 mapping[i] 个位置
H2_ISAACLAB_TO_MUJOCO_DOF = [...]   # 长度 = num_dof（H2 为 31）
H2_MUJOCO_TO_ISAACLAB_DOF = [...]
H2_ISAACLAB_TO_MUJOCO_BODY = [...]  # 长度 = num_bodies（H2 为 32）
H2_MUJOCO_TO_ISAACLAB_BODY = [...]

H2_ISAACLAB_TO_MUJOCO_MAPPING = {
    "isaaclab_joints": H2_ISAACLAB_JOINTS,
    "isaaclab_to_mujoco_dof": H2_ISAACLAB_TO_MUJOCO_DOF,
    "mujoco_to_isaaclab_dof": H2_MUJOCO_TO_ISAACLAB_DOF,
    "isaaclab_to_mujoco_body": H2_ISAACLAB_TO_MUJOCO_BODY,
    "mujoco_to_isaaclab_body": H2_MUJOCO_TO_ISAACLAB_BODY,
}
```

**正确设置这些映射至关重要。** 如果映射有误，策略会收到错乱的观测并输出错乱的动作。验证方法：在两个仿真器中加载同一已知姿态，检查重排序后的关节值是否一致。

### 执行器参数（KP/KD 调优）

执行器刚度（KP）与阻尼（KD）对仿真到真实迁移和训练稳定性至关重要。SONIC 在 Isaac Lab 中使用隐式 PD 执行器。

```python
# 由电机规格推导 — 需针对你的机器人调优
NATURAL_FREQ = 10 * 2.0 * 3.1415926535  # 10Hz 固有频率
DAMPING_RATIO = 2.0                      # 过阻尼以保证稳定性

# 单电机刚度：KP = armature * omega^2
STIFFNESS_5020 = ARMATURE_5020 * NATURAL_FREQ**2
# 单电机阻尼：KD = 2 * zeta * armature * omega
DAMPING_5020 = 2.0 * DAMPING_RATIO * ARMATURE_5020 * NATURAL_FREQ
```

**调优指南：**

- 从数据手册中真实电机的**转子惯量（armature）**出发。
- **固有频率**决定响应速度。对人形机器人而言 10 Hz 是不错的起点。想要更硬/更快的跟踪就调高，想要更柔顺就调低。
- **阻尼比**应 >= 1.0（临界阻尼或过阻尼）以避免振荡。SONIC 使用 2.0 效果良好。
- **不同关节组需要不同的增益。** 髋/膝关节电机远强于腕部电机。请按电机类型对关节分组（参见 G1/H2 配置示例）。
- 如果训练不稳定（机器人爆掉或立即摔倒），很可能是你的 KP/KD 值不对。可尝试降低 KP 或增大 KD。
- 每个关节的**力矩上限**（最大力矩）应与真实电机规格一致。

### Articulation 配置

```python
H2_CFG = ArticulationCfg(
    spawn=sim_utils.UrdfFileCfg(
        asset_path="gear_sonic/data/assets/robot_description/urdf/h2/h2.urdf",
        fix_base=False,
        replace_cylinders_with_capsules=True,
        activate_contact_sensors=True,
        ...
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 1.04),       # 站立高度 — 必须与你的机器人匹配
        joint_pos={
            ".*_knee_joint": -0.363,  # 轻微屈膝以保持稳定
            # ... 所有关节的默认站立姿态
        },
    ),
    actuators={
        "legs": ImplicitActuatorCfg(
            joint_names_expr=[".*_hip_.*", ".*_knee_.*"],
            effort_limit={...},       # 每个关节的最大力矩（Nm）
            stiffness={...},          # KP 值
            damping={...},            # KD 值
            armature={...},           # 转子惯量
        ),
        # ... 每种电机类型一组（手臂、腰部、脚部等）
    },
)
```

**init_state 重要说明：**

- `pos` 的 z 值是出生高度。应设置成机器人站立起步时双脚略微高于地面。过低 = 第一帧双脚穿入地面。
- `joint_pos` 应是稳定的站立姿态。可取自你机器人的真实默认校准姿态或 MuJoCo 关键帧。

### 动作缩放

动作缩放将归一化的策略输出映射为关节位置目标。由力矩上限和刚度计算得到：

```python
H2_ACTION_SCALE = {}
for joint_name in joint_names:
    H2_ACTION_SCALE[joint_name] = effort_limit[joint_name] / stiffness[joint_name]
```

动作缩放越大 = 每单位策略输出引起的关节运动越大。如果机器人动作过于激进，请减小动作缩放。

### 注册到 __init__.py

将你的模块加入 `gear_sonic/envs/manager_env/robots/__init__.py`，使其可被导入。

### 注册到 modular_tracking_env_cfg.py

将你的机器人加入 `robot_mapping` 字典（第 998 行附近）：

```python
from gear_sonic.envs.manager_env.robots import g1, h2  # 加入你的 import

robot_mapping = {
    "g1_model_12_dex": {...},
    "h2": {
        "robot_cfg": h2.H2_CFG,
        "action_scale": h2.H2_ACTION_SCALE,
        "isaaclab_to_mujoco_mapping": h2.H2_ISAACLAB_TO_MUJOCO_MAPPING,
    },
}
```

这个字符串键（例如 `"h2"`）就是你在实验配置中 `robot.type` 要填的值。

## 第 3 步：顺序转换器

在 `gear_sonic/trl/utils/order_converter.py` 中添加一个转换器类。评估与导出流水线会用到它：

```python
class H2Converter(IsaacLabMuJoCoConverter):
    def __init__(self):
        from gear_sonic.envs.manager_env.robots.h2 import (
            H2_ISAACLAB_JOINTS, H2_ISAACLAB_TO_MUJOCO_BODY,
            H2_ISAACLAB_TO_MUJOCO_DOF, H2_MUJOCO_TO_ISAACLAB_BODY,
            H2_MUJOCO_TO_ISAACLAB_DOF,
        )
        self.JOINT_NAMES = H2_ISAACLAB_JOINTS
        self.DOF_MAPPINGS = {
            ("isaaclab", "mujoco"): H2_ISAACLAB_TO_MUJOCO_DOF,
            ("mujoco", "isaaclab"): H2_MUJOCO_TO_ISAACLAB_DOF,
        }
        self.BODY_MAPPINGS = {
            ("isaaclab", "mujoco"): H2_ISAACLAB_TO_MUJOCO_BODY,
            ("mujoco", "isaaclab"): H2_MUJOCO_TO_ISAACLAB_BODY,
        }

    # 用于 VR 跟踪和脚部接触的刚体 — 根据你的机器人更新
    VR_3POINTS_BODY_NAMES = ["torso_link", "left_wrist_pitch_link", "right_wrist_pitch_link"]
    FOOT_BODY_NAMES = ["left_ankle_roll_link", "right_ankle_roll_link"]
```

请使用延迟导入（放在 `__init__` 内部）以避免循环依赖。

## 第 4 步：刚体名称兼容性

这是常见的错误来源。训练配置引用了特定的刚体名称，它们必须存在于你的机器人上。请逐一检查以下**所有**内容：

### 指令配置（`config/manager_env/commands/terms/motion.yaml`）

```yaml
anchor_body: "pelvis"                           # 根刚体
vr_3point_body: ["left_wrist_yaw_link", "right_wrist_yaw_link", "torso_link"]
reward_point_body: ["pelvis", "left_wrist_yaw_link", "right_wrist_yaw_link",
                    "left_ankle_roll_link", "right_ankle_roll_link"]
body_names: [                                   # 14 个被跟踪的刚体
    "pelvis", "left_hip_roll_link", "left_knee_link", "left_ankle_roll_link",
    "right_hip_roll_link", "right_knee_link", "right_ankle_roll_link",
    "torso_link", "left_shoulder_roll_link", "left_elbow_link",
    "left_wrist_yaw_link", "right_shoulder_roll_link", "right_elbow_link",
    "right_wrist_yaw_link",
]
```

### 终止条件配置（`config/manager_env/terminations/terms/`）

- `ee_body_pos_adaptive.yaml`：引用了 `left_ankle_roll_link`、`right_ankle_roll_link`、
  `left_wrist_yaw_link`、`right_wrist_yaw_link`
- `foot_pos_xyz.yaml`：引用了 `left_ankle_roll_link`、`right_ankle_roll_link`

### 奖励配置（`config/manager_env/rewards/terms/`）

- `undesired_contacts.yaml`：用正则模式将特定刚体排除在接触惩罚之外 — 引用了踝部和腕部 link 名称
- `anti_shake_ang_vel.yaml`：引用了 `left_wrist_yaw_link`、`right_wrist_yaw_link`、
  `head_link`

### 名称不一致时怎么办

如果你的机器人对等刚体使用了不同的名称（例如 H2 用 `head_pitch_link` 而不是 G1 的 `head_link`），有两种选择：

1. **在实验配置中覆盖**（推荐）：在 `sonic_<robot>.yaml` 中为有差异的特定字段添加覆盖项。

2. **创建机器人专属配置变体**：复制受影响的 term YAML 文件，创建机器人专属版本（例如 `anti_shake_ang_vel_h2.yaml`）。

对 H2 而言，大多数 G1 刚体名称恰好都存在（两者都是 Unitree 人形机器人），但 `head_link` 不存在 — H2 用的是 `head_yaw_link`。在实验配置中覆盖：

```yaml
manager_env:
  rewards:
    anti_shake_ang_vel:
      params:
        body_names: ["left_wrist_yaw_link", "right_wrist_yaw_link", "head_yaw_link"]
```

**提示：** 先用 `num_envs=1` 运行训练。如果某个刚体名称不存在，Isaac Lab 会抛出明确的错误，告诉你哪个名称失败了。修复后重试。

## 第 5 步：动作数据

SONIC 要求重定向后的动作数据为 PKL 文件（joblib 格式）。每个文件包含一个以动作名为键的字典：

```python
{
    "motion_name": {
        "root_trans_offset": np.ndarray,  # (T, 3) — 根节点平移
        "pose_aa": np.ndarray,            # (T, num_bodies, 3) — 每个刚体的轴角
        "dof": np.ndarray,                # (T, num_dof) — MuJoCo 顺序的关节位置
        "root_rot": np.ndarray,           # (T, 4) — 根节点四元数（wxyz）
        "smpl_joints": np.ndarray,        # (T, 24, 3) — SMPL 关节位置（可选）
        "fps": int,                       # 帧率（通常为 30）
    }
}
```

**重要的数据格式说明：**

- `num_bodies` 和 `num_dof` 必须与你的机器人匹配（例如 H2 为 32 个刚体 / 31 自由度）。
- `dof` 值必须按 **MuJoCo 关节顺序**，而不是 IsaacLab 顺序。
- `pose_aa` 必须按 **MuJoCo 刚体顺序**。
- 镜像变体（文件名以 `_M.pkl` 结尾）可将有效数据集规模翻倍并改善对称性。
- `smpl_joints` 字段供 SMPL 编码器使用。如果没有 SMPL 数据，将其置零即可。

动作库会从目录**递归**加载 PKL 文件：

```
data/h2_motions/
├── session_01/
│   ├── walk_forward_001.pkl
│   └── walk_forward_001_M.pkl
└── session_02/
    └── ...
```

### 源动作数据

推荐的数据源是 [Bones-SEED](https://huggingface.co/datasets/bones-studio/seed)
— 一个大规模人体动作数据集（142K+ 个动作，约 288 小时），提供：

- **原始 BVH 文件** — 全身人体动作捕捉
- **G1 重定向 CSV** — 已重定向到 Unitree G1（29 自由度）

对于新机器人，你需要把原始人体动作**重定向**到你的机器人骨架上。这是最耗人力的步骤。

### 重定向选项

1. **[SOMA Retargeter](https://github.com/NVIDIA/soma-retargeter)**（推荐）—
   NVIDIA 基于 Newton 和 NVIDIA Warp 构建的 BVH 到人形机器人动作重定向库。通过 JSON 配置支持任意人形机器人，并附带查看器，可并排查看源动作与重定向后的动作。生成 Bones-SEED G1 重定向数据所用的正是这个工具。

2. **[GMR](https://github.com/YanjieZe/GMR)**（General Motion Retargeting）—
   在 CPU 上实时将人体动作重定向到任意人形机器人。支持任意 URDF。是一种更轻量的替代方案。

3. **本仓库的数据处理**（`gear_sonic/data_process/`）— 将重定向后的 CSV/BVH 转换为 SONIC 期望的 PKL 格式。请在重定向完成后作为最后一步使用：

   ```bash
   # 将重定向后的 CSV 转换为动作库 PKL
   python gear_sonic/data_process/convert_soma_csv_to_motion_lib.py \
       --input /path/to/retargeted_csvs/ \
       --output data/my_robot_motions/robot \
       --fps 30 --fps_source 120 --individual --num_workers 16

   # 过滤掉你的机器人物理上无法完成的动作
   python gear_sonic/data_process/filter_and_copy_bones_data.py \
       --source data/my_robot_motions/robot \
       --dest data/my_robot_motions/robot_filtered
   ```

### SMPL 数据（可选但推荐）

SMPL 编码器为策略提供额外的人体骨架输入信号。你需要与机器人数据动作键完全匹配的 SMPL 重定向数据。

- Bones-SEED 动作的预计算 SMPL 数据可在
  [Hugging Face](https://huggingface.co/nvidia/GEAR-SONIC) 获取：
  `python download_from_hf.py --training`
- 如果使用自定义动作，请从 BVH 文件提取 SMPL 关节：

  ```bash
  python gear_sonic/data_process/extract_soma_joints_from_bvh.py \
      --input /path/to/bvh_files/ \
      --output data/my_robot_motions/soma \
      --fps 30 --num_workers 16
  ```

- 如果没有 SMPL 数据，在配置中设置 `smpl_motion_file: dummy`。训练流水线会根据机器人动作生成最小的占位 SMPL 数据。这样能跑通，但 SMPL 编码器性能会较弱。

## 第 6 步：实验配置

创建 `gear_sonic/config/exp/manager/universal_token/all_modes/sonic_<robot>.yaml`。先复制 `sonic_release.yaml`，然后修改：

```yaml
# @package _global_
defaults:
  - /algo: ppo_im_phc
  - /manager_env: base_env
  # ... 与 sonic_release.yaml 相同的 defaults

project_name: TRL_H2_Track                     # 修改项目名

manager_env:
  config:
    robot:
      type: h2                                  # 必须与 robot_mapping 的键匹配
  commands:
    motion:
      motion_lib_cfg:
        motion_file: null                       # 在命令行提供
        asset:
          assetFileName: "h2.xml"               # 你的 MJCF 文件名
```

**需要检查并可能覆盖的字段：**

- `robot.type` — 必须与 `robot_mapping` 中的键匹配
- `motion_lib_cfg.asset.assetFileName` — 你的 MJCF 文件
- `reward_point_body` / `reward_point_body_offset` — 奖励计算的关键刚体
- `vr_3point_body` / `vr_3point_body_offset` — 进行 VR 遥操作时需要
- `upper_body_augment_prefixes` — 如果你的动作数据命名不同，请移除
- 奖励/终止覆盖项中的刚体名称 — 见第 4 步

## 第 7 步：训练

```bash
python gear_sonic/train_agent_trl.py \
    +exp=manager/universal_token/all_modes/sonic_h2 \
    num_envs=16 headless=False \
    ++manager_env.commands.motion.motion_lib_cfg.motion_file=<path/to/h2_motions>
```

先用 `num_envs=16 headless=False` 直观验证机器人能正确加载、动作能正确回放，然后再扩展到 `num_envs=4096 headless=True` 进行完整训练。

## 示例：H2（已包含）

代码库已包含完整的 H2 支持作为参考：

| 组件 | 文件 |
|-----------|------|
| 机器人配置 | `gear_sonic/envs/manager_env/robots/h2.py` |
| URDF + 网格 | `gear_sonic/data/assets/robot_description/urdf/h2/` |
| MJCF | `gear_sonic/data/assets/robot_description/mjcf/h2.xml` |
| 实验配置 | `gear_sonic/config/exp/manager/universal_token/all_modes/sonic_h2.yaml` |
| 顺序转换器 | `gear_sonic/trl/utils/order_converter.py`（`H2Converter`） |
| 机器人映射 | `gear_sonic/envs/manager_env/modular_tracking_env_cfg.py` |

## 检查清单

新增机器人时，请逐项核对：

- [ ] URDF 和网格文件位于 `gear_sonic/data/assets/robot_description/urdf/<robot>/`
- [ ] MJCF 位于 `gear_sonic/data/assets/robot_description/mjcf/<robot>.xml`
- [ ] 机器人配置位于 `gear_sonic/envs/manager_env/robots/<robot>.py`：
  - [ ] 关节/刚体名称列表
  - [ ] IsaacLab ↔ MuJoCo 索引映射（务必验证正确！）
  - [ ] 带有按电机组调好的 KP/KD/力矩上限的 `ArticulationCfg`
  - [ ] 正确的 init_state（站立高度 + 默认关节角度）
  - [ ] 动作缩放字典
- [ ] 机器人已在 `robots/__init__.py` 中导入
- [ ] 机器人已加入 `modular_tracking_env_cfg.py` 的 `robot_mapping`
- [ ] `order_converter.py` 中的顺序转换器类
- [ ] 实验配置 YAML 中 `robot.type` 和 `assetFileName` 正确
- [ ] 配置 YAML 中的所有刚体名称都存在于你的机器人上（用 `num_envs=1` 检查）
- [ ] 人体动作源数据（例如 [Bones-SEED](https://huggingface.co/datasets/bones-studio/seed) 的 BVH/CSV 文件）
- [ ] 动作已重定向到你的机器人骨架（例如通过 [SOMA Retargeter](https://github.com/NVIDIA/soma-retargeter)）
- [ ] 重定向后的数据已转换为 PKL 格式（MuJoCo 关节/刚体顺序）
- [ ] 已按物理可行性过滤动作（`filter_and_copy_bones_data.py`）
- [ ] 用于对称性训练的镜像动作变体（`_M.pkl`）
- [ ] 与动作键匹配的 SMPL 数据（或 `smpl_motion_file: dummy`）
