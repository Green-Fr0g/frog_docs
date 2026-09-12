# docs_zh_CN 翻译基准（术语表与规范）

本文件是 `docs_zh_CN/` 中文翻译的统一基准：术语对照、保留英文的内容、格式规范。
所有翻译批次开始前先阅读本文件；遇到本表未覆盖的词，按同类规则处理并回填到本表。

## 范围与现状

- `docs_zh_CN/source/` 是英文 `docs/source/` 的完整副本，尚未翻译（与英文版逐字相同）。
- 需翻译的正文约 6700 行 rst，分布在：
  - `getting_started/`（8 个文件，安装、快速上手、预训练模型、各数据集准备）
  - `concepts/`（6 个文件，架构与核心抽象）
  - `tutorials/`（8 个文件，含 workflows）
  - `user_guide/`（6 个文件，含 gpc.rst）
  - `index.rst`、`changelog.rst`、`contributing.rst`
- `api_reference/`（约 100 个文件）基本是 autodoc 指令，仅按需翻译标题/说明，不动指令本身。

## 语境概述

ProtoMotions 是 NVIDIA 的 GPU 加速物理仿真与学习框架，用于训练物理仿真数字人
（SMPL / SMPL-X / SOMA）和人形机器人（Unitree G1 / H1）。核心任务族：
**Mimic（动作模仿跟踪）**、**Steering（方向控制）**、**PathFollowing（路径跟随）**、
**MaskedMimic（掩码动作补全）**、**GPC/PEFT（离散潜变量先验 + 参数高效微调）**。
支持多仿真后端：Newton、IsaacGym、IsaacLab、Genesis、MuJoCo。
文档读者是做 RL 训练与机器人部署的研究者/工程师，语气为技术文档，简洁准确优先。

## 核心术语对照表

### 任务与算法

| 英文 | 中文 | 备注 |
|---|---|---|
| motion imitation / Mimic | 动作模仿 / Mimic | 作为任务族名或组件名时保留 Mimic |
| motion tracker / tracker | 动作跟踪器 / 跟踪器 | 指跟踪参考动作的策略，不是调试工具 |
| reference motion / motion clip | 参考动作 / 动作片段 | |
| MotionLib / motion library | MotionLib / 动作库 | 组件名保留英文，行文用"动作库" |
| retargeting | 动作重定向 | 基于 PyRoki 的轨迹优化，非逐帧 IK |
| keypoint | 关键点 | 重定向输入的简化骨架点 |
| steering | Steering / 方向控制 | 作为任务族名保留 Steering |
| path following | 路径跟随 | |
| MaskedMimic / masked motion inpainting | MaskedMimic / 掩码动作补全 | 方法名保留 |
| masked observation | 掩码观测 | |
| prior（GPC 语境） | 先验 | 生成式动作先验模型，绝不是"之前的" |
| unconditional prior | 无条件先验 | 不带任务条件采样 |
| frozen prior | 冻结先验 | |
| autoregressive | 自回归 | |
| FSQ (Finite Scalar Quantization) | FSQ（有限标量量化） | 首次出现给全称 |
| discrete latent code | 离散潜变量编码 | |
| PEFT (parameter-efficient fine-tuning) | PEFT（参数高效微调） | |
| SFT (supervised fine-tuning) | SFT（监督微调） | |
| RLFT (RL fine-tuning) | RLFT（强化学习微调） | 不译，与 SFT 对应 |
| adapter | 适配器 | PEFT 适配器模块，不是硬件 |
| expert（MaskedMimic 语境） | 专家模型 | 预训练 Mimic 模型，与 prior 区分 |
| PPO / AMP / ASE / ADD | 保留英文 | 首次出现可附全称（近端策略优化、对抗运动先验、对抗技能嵌入） |
| warm start | 热启动 | 旧权重 + 新配置的续训方式 |
| bootstrap（价值函数） | 自举 | `bootstrap_on_episode_end`，勿译"启动" |
| resume | 恢复训练 | 强调"复用保存的配置、忽略 CLI 覆盖" |
| checkpoint | 检查点 | RL 模型存档（`.ckpt`），不是 QA 检查点 |
| prioritized sampling | 优先级采样 | 评估器向失败动作加权采样 |
| full evaluation / full-eval | 完整评估 | 每个动作恰好评估一次，无偏指标 |
| unbiased | 无偏 | 所有动作等权 |
| success rate | 成功率 | 动作完成且不摔倒的比例 |
| RSI (reference state init) | 参考状态初始化（RSI） | |
| domain randomization (DR) | 域随机化 | |
| L2C2 / BeyondMimic (BM) | 保留英文 | 特定跟踪器训练方法名 |

### 环境与仿真

| 英文 | 中文 | 备注 |
|---|---|---|
| environment | 环境 | 指并行仿真实例（`--num-envs`），不是"设置" |
| parallel environments | 并行环境 | |
| simulator backend | 仿真后端 | |
| physics-based animation | 基于物理的动画 | |
| digital human | 数字人 | SMPL/SMPL-X/SOMA |
| humanoid | 人形（机器人）/ 人形角色 | 视上下文 |
| morphology | 形体结构 | 机器人身体结构，区别于 skeleton（骨骼） |
| terrain | 地形 | procedural terrain = 程序化生成地形 |
| heightfield | 高度场 | |
| complex terrain / flat terrain | 复杂地形 / 平坦地形 | 固定搭配 |
| SceneLib / scene object | SceneLib / 场景物体 | |
| asset | 资产 | 机器人/场景文件（MJCF、USD） |
| MJCF / USD / URDF / ONNX | 保留英文 | |
| episode | 回合 | 一次环境尝试（max_episode_length） |
| rollout | 采样轮 | 一次 num_steps 的数据收集 |
| iteration | 迭代 | 一轮 rollout + PPO 优化 |
| mini-epochs | 迷你轮次 | PPO 对已收集数据的优化遍数 |
| early termination | 提前终止 | 跟踪误差超阈值切断回合 |
| kinematic playback | 运动学回放 | 无物理直接回放，调试用 |
| ground truth (GT) | 真值 / 参考真值 | gt_rew、Eval/gt_err 语境 |
| noisy / clean (state, obs) | 带噪 / 干净 | actor 用带噪观测，critic 用干净观测，成对统一 |
| anchor | 锚点（躯干参考系） | anchor_rot/anchor_ang_vel 同属此参考系 |
| root | 根节点 / 根刚体 | root_pos 等 |
| DOF (degree of freedom) | 自由度 | `num_dofs`、dof_pos |
| rigid body | 刚体 | |
| quaternion (xyzw / wxyz) | 四元数 | 标注顺序时保留 xyzw/wxyz |
| axis-angle / Euler angles | 轴角 / 欧拉角 | |
| FK / IK | 正向运动学 / 逆运动学 | |
| reduced / maximal coordinates | 简化坐标 / 最大化坐标 | qpos 广义坐标 vs 世界系刚体位姿 |
| PD control / PD gains | PD 控制 / PD 增益 | stiffness 刚度，damping 阻尼 |
| actuator / articulation | 执行器 / 关节体 | IsaacLab 术语 |
| contact label | 接触标签 | 足底接触的启发式二值标签 |
| sim2sim / sim2real | 保留英文 | sim2real = 仿真到现实迁移 |
| reality gap | 现实差距 | |
| deployment contract | 部署契约 | MuJoCo 测试脚本 + ONNX 元数据组成的规范 |
| blend-in / blend-out | 融合接入 / 融合退出 | 真机部署阶段 |
| fade-in / fade-out | 渐入 / 渐出 | 与 blend 区分，不合并 |
| ramp-up | 爬坡过渡 | |
| virtual gantry | 虚拟吊架 | 弹簧阻尼安全保护 |
| waypoint | 路径点 | |
| heading / heading alignment | 朝向 / 朝向对齐 | 仅偏航角的偏移 |
| heightfield query / ground height | 地形高度查询 | |

### 系统与训练

| 英文 | 中文 | 备注 |
|---|---|---|
| experiment（文件/运行） | 实验 | 实验文件 = Python 配置文件 |
| experiment file | 实验文件 | 定义完整训练配置的 Python 文件 |
| dataclass config | dataclass 配置 | |
| component | 组件 | control/observation/reward/termination 组件 |
| control component | 控制组件 | 有状态任务管理器 |
| observation component | 观测组件 | 无状态纯函数 |
| reward component | 奖励组件 | |
| termination component | 终止组件 | |
| kernel（MdpComponent） | 计算核 / 核函数 | 纯张量函数 |
| context（EnvContext） | 上下文 | |
| context path | 上下文路径 | |
| reward shaping | 奖励塑形 | |
| reward term | 奖励项 | |
| grace period | 宽限期 | 奖励激活前的缓冲时间 |
| actor / critic | actor / critic | 保留英文（策略网络 / 价值网络可作首现注释） |
| Agent（组件/行文） | 智能体 | 行文译"智能体"，类名（BaseAgent 等）保留英文 |
| ground truth（MJCF 基准语义） | 基准真值 | "MJCF is the ground truth" 语境；动作真值语境用"真值/参考真值" |
| pin / pinned revision | 固定 / 固定的版本 | isaaclab3_migration 语境，锁定特定 commit |
| spawn（USD/UsdFileCfg） | 生成实例 | |
| policy materialization | 策略实体化 | 策略权重物化到 GPU |
| projectile | 投射物 | domain_randomization 场景物体 |
| resolved configs（散文） | resolved 配置 | 文件名 resolved_configs.pt 保留英文 |
| policy | 策略 | |
| asymmetric actor-critic | 非对称 actor-critic | |
| clip_frac | 保留英文 | 指标名，PPO 裁剪比例 |
| sharded MotionLib | 分片动作库 | shard = 分片，chunk 文件名保留 |
| slurmrank | 保留英文 | |
| headless | 无界面（模式） | `--headless` 参数本身保留 |
| weight（三种含义） | 采样权重 / 奖励权重 / （网络）权重 | 按语境区分 |
| model card | 模型卡 | pretrained_models 页 |
| entry point | 入口点 | `protomotions train-agent` |

## 专有名词保留清单（不翻译）

- **仿真器/平台**：Newton、IsaacGym（注意是一个词）、IsaacLab（一个词，不是 "Isaac Lab"）、Isaac Sim、Genesis、MuJoCo、PhysX、PyTorch、TensorDict、ONNX、USD、MJCF、SLURM、wandb / Weights & Biases（行文可用 W&B）、Hydra、Git LFS、Docker、Singularity、Enroot、Kit
- **机器人/角色**：Unitree G1、H1 / H1_2（标识符用 H1_2，行文可用 H1-2，各自保留）、SMPL、SMPL-X、SMPL-H、SOMA（soma23）、Booster T1、BONES-SEED（数据集；页面标题 "SEED"）
- **数据集/工具**：AMASS、PHUMA、OMOMO、KIMODO（文中拼写为 "Kimodo"）、PyRoki、DeepMimic、RoboJuDo（仓库小写 robojudo）
- **方法/论文名**：PPO、AMP、ASE、ADD、MaskedMimic、MaskedManipulator、GPC、PEFT、FSQ、L2C2、BeyondMimic（缩写 BM）、DeepMimic（Peng et al. 2018）；论文标题保持英文
- **代码标识符**：所有 Python 类名/函数名/文件名/CLI 参数/wandb 指标名（`gt_rew`、`Eval/gt_err`、`--num-envs`、`last.ckpt`、`inference_last.ckpt`、`resolved_configs.pt` 等）一律原样保留
- **拼写陷阱**：`protomotions train-agent`（连字符，uv 入口）与 `train_agent.py`（下划线）是两种写法，不可混用

## 格式与翻译规范

1. **只译散文，不动代码**：`.. code-block::` 内的 Python/bash/text（含 ASCII 架构图、管线图）一律原样保留；raw HTML 块不译（其中可见的英文短句如视频占位文字可译，谨慎处理）。
2. **RST 指令与结构原样**：`:doc:`、`:ref:` 链接目标、锚点（如 `seed-bvh-scaling-up`、`g1-deploy-frame-convention`）、`.. list-table::`、`.. note::`/`.. tip::`/`.. warning::`、标题下划线符号（`=====`、`-----`、`~~~~~`）全部保留；中文标题通常比英文短，下划线长度只需 ≥ 标题宽度即可。
3. **首次出现给全称**：FSQ、PEFT、SFT、RLFT、RSI、DR 等缩写首次出现时以"中文全称（英文缩写）"形式给出。
4. **术语一致性**：同一概念全库用同一个译名（以本表为准）；quickstart 与 amass_smpl 中"指标可能因优先级采样而波动"等重复句式，译法保持一致。
5. **changelog 保持简练**：条目式短句，保留 commit hash、版本号、组件名。
6. **contributing 语气自然**：友好口吻（"Don't worry about being perfect" → 别担心不够完美），不要生硬直译；git 命令、工具名（pre-commit、Ruff、Typos）不动。
7. **`isaaclab3_migration.rst` 特殊**：`::` 字面块的续行反斜杠 `\\`、DOF 后缀 `:0`/`:1`/`:2`、issue/PR 链接目标（#5086、#6259）必须逐字保留。
8. **数字与单位**：数值、单位、GPU 型号、超参数保持原样。

## 建议翻译批次（由短到长、由核心到外围）

1. index.rst、contributing.rst、changelog.rst（入门 + 定调）
2. concepts/ 全部 6 个文件（术语密度最高，先译可校准术语表）
3. getting_started/（installation、quickstart、pretrained_models → 各数据集准备）
4. user_guide/（configuration、experiments、gpc、developer_tips、slurm_training、isaaclab3_migration）
5. tutorials/（index、code_tutorials、challenges → workflows 5 篇）
6. api_reference/ 标题（可选）
