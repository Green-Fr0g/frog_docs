# Isaac Lab 文档中文翻译规范

本文件是 `docs_zh_CN` 翻译工作的统一规范，所有批次翻译必须遵守。

## 一、必须保持原样的内容

1. RST 指令本身：`.. note::`、`.. code-block::`、`.. figure::`、`.. toctree::` 等。
2. 交叉引用：`:ref:` 的标签名、`:doc:` 的路径目标、`aria-label` 等。**只翻译引用显示时其后的自定义文字（如有），不碰标签本身**。
3. 代码块、shell 命令、文件路径、URL、Python 标识符（类名、函数名、参数名、配置项名）。
4. 行内代码 `` ``xxx`` `` 的内容保持英文原文。
5. 图片、`_static` 资源、`refs.bib`。
6. HTML/XML 片段中的标签与属性名。

## 二、标题翻译

- 章节标题翻译为中文，但标题下划线（`=====`、`-----` 等）长度必须不小于标题可见长度，**建议直接保留原标题的下划线长度或加长**。
- 标题中出现代码/类名（如 `` ``ActuatorBase`` ``）时保留英文。

## 三、术语表

| 英文 | 中文译法 | 说明 |
|---|---|---|
| environment | 环境 | |
| simulation | 仿真 | |
| actuator | 执行器 | 类名 Actuator 保留英文 |
| articulation | 关节体 | 首次出现标注英文，类名 Articulation 保留 |
| sensor | 传感器 | |
| scene | 场景 | InteractiveScene → 交互式场景 |
| prim | Prim | 不翻译 |
| stage | Stage | USD Stage 不翻译 |
| asset | 资产 | |
| spawn / spawning | 生成 | |
| terrain | 地形 | |
| observation | 观测 | |
| action | 动作 | |
| reward | 奖励 | |
| episode | 回合 | |
| policy | 策略 | |
| curriculum | 课程 | curriculum learning → 课程学习 |
| domain randomization | 域随机化 | |
| teleoperation / teleop | 遥操作 | |
| Manager-Based workflow | 管理器式工作流 | |
| Direct workflow | 直接式工作流 | |
| configclass | configclass | 保留 |
| extension | 扩展 | |
| workspace | 工作区 | |
| checkpoint | 检查点 | |
| rollout | rollout | 保留 |
| benchmark | 基准测试 | |
| motion generator | 运动生成器 | |
| contact sensor | 接触传感器 | |
| frame transformer | 坐标变换传感器 | FrameTransformer 首次出现标注英文 |
| ray caster | 光线投射传感器 | RayCaster 保留英文 |
| IMU | IMU（惯性测量单元） | 首次出现标注 |
| visuo-tactile sensor | 视触觉传感器 | |
| rigid body | 刚体 | |
| joint | 关节 | |
| link | 连杆 | |
| mesh | 网格 | |
| physics engine | 物理引擎 | |
| reinforcement learning (RL) | 强化学习（RL） | |
| imitation learning (IL) | 模仿学习（IL） | |
| demonstration | 演示数据 | 视语境可为"演示" |
| dataset | 数据集 | |
| ground truth | 真值 | |
| pipeline | 流水线 | |
| framework | 框架 | |
| seamless | 无缝 | |
| out of the box | 开箱即用 | |
| walkthrough | 分步演示 | |
| hands-on | 实操 | |

## 四、风格约定

1. 译文使用简体中文，标点使用全角中文标点；代码、数字与英文单词前后各留一个空格。
2. 语气与官方技术文档一致：清晰、直接、面向开发者，不使用感叹号。
3. 不增删内容：不添加译者注，不合并或拆分段落语义；列表项数量保持一致。
4. 专有名词（Isaac Lab、Isaac Sim、Omniverse、PhysX、USD、ROS、CUDA、PyTorch 等）不翻译。
5. 拿不准的术语：首次出现时用「中文（English）」格式，之后统一用中文。
