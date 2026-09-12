# 翻译指南与术语表（docs_zh_CN）

本文件是 `docs_zh_CN` 中文翻译的统一基准，由通读全部源文件整理而成。翻译任何页面之前请先读完本文件，保证全站术语、语气与格式一致。

---

## 1. 项目背景与语境

- **项目**：NVIDIA **GR00T-WholeBodyControl**，人形机器人全身控制（Whole-Body Control, WBC）的统一开发与部署平台，主要面向 **Unitree G1** 人形机器人。
- **两条技术主线**：
  1. **Decoupled WBC**（解耦全身控制）— 用于 NVIDIA Isaac-GR00T N1.5 / N1.6 的全身控制模型，附遥操作栈与数据导出器，基于 Isaac Lab + Docker。
  2. **GEAR-SONIC 系列** — GEAR 团队的 SOTA 全身控制器。SONIC 是"通用 token（universal-token）控制器"：多编码器（SMPL / G1 / 遥操作）+ FSQ 量化器 + 解码器，输出 64 维潜在运动 token，以 50 Hz 运行；部署侧为 C++ + TensorRT + ONNX，训练侧为 Isaac Lab + PPO（TRL）。
- **文档内容板块**：getting_started（安装/下载/快速上手/VR 配置）、tutorials（键盘/手柄/ZMQ/VR 遥操作/相机遥操作/数据采集/VLA 工作流与推理/接口管理器）、user_guide（配置/训练/训练数据/新机器人本体/遥操作/故障排除）、references（训练与部署代码结构、观测配置、动作参考数据、运动学规划器 ONNX、JetPack 刷机、坐标系约定、Decoupled WBC）、model_card、resources。
- **受众**：机器人学研究者与工程师，熟悉 RL、仿真与部署工具链。可放心使用"策略、观测、检查点、微调、遥操作、无头模式"等学界通用译法，术语首现可括注英文。
- **语气**：
  - getting_started / tutorials：操作手册，祈使句为主（"运行……"）。
  - 遥操作相关文档**安全语气极强**：所有 `{danger}` 警告、"Safety Warning"、"use this software at your own risk" 等必须完整、严肃翻译，**不得弱化**（如"风险自负""作者与贡献者不对任何损失负责"）。
  - user_guide / references：技术参考，简练、精确；troubleshooting 采用统一的 **症状 / 原因 / 解决方法** 三段式。

---

## 2. 不可翻译内容（红线）

1. **代码块全部原样保留**：bash/sh/python/目录树，包括所有 CLI 旗标（`--low-latency`、`--zmq-conflate`、`--motor-kp-scale 4,10=1.5` 等）、IP 与端口（`192.168.123.164`、`tcp://localhost:5556`）。目录树和代码中 `#` 注释可译，路径/文件名不可译。
2. **Hydra/OmegaConf 命令行键**（`+exp=`、`++num_envs=1`、`~manager_env/recorders=empty`）的 `+`/`++`/`~` 语法绝不可动。
3. **配置参数名 / YAML 键 / 观测名 / 张量名 / CSV 列名 / 模式与协议字段名**：如 `num_envs`、`smpl_y_up`、`token_state`、`motion_joint_positions_10frame_step5`、`body_quat`、`frame_index`、`slowWalk`、`UNITREE_G1_SONIC`、`CALIB_FULL`、`VR_3PT`、`OFF/POSE/PLANNER/PLANNER_FROZEN_UPPER` —— 一律保留英文。
4. **终端输出、日志与报错字符串**：即使出现在译文中也保留英文原文（可另加中文说明），如 `ModuleNotFoundError: No module named 'isaaclab'`、`Planner enabled`、`NVIDIA Corp. APX`。
5. **专有名词**（见第 4 节清单）。
6. **按键名**（`]`、`9`、`T`、`Ctrl+C`、A+B+X+Y、Left Grip 等）保留原文格式（加粗反引号），可括注中文。
7. **设备 UI 字符串**：用户要在英文界面里找的按钮/标签保留英文，括注中文，如 "Safeguard"（安全防护）、"Full body"、"Pair"、"Calibrate"、"Video Codec"。
8. **相对链接与锚点**：链接目标路径与 `#anchor` 不改，只译链接文本。注意跨文件锚点（`vr_wholebody_teleop.md#calibration-pose`、`#pico-controls`）与 MyST 显式锚点 `(context_mujoco_qpos)=`、`(obs-config-format)=`、`{ref}` 语法、HTML `<div id="advanced-inputs">` 必须原样保留。
9. **ASCII 图**：目录树、状态机图、流水线图、架构图的制表符与对齐敏感；框内**标签保留英文**（否则对齐会乱），框外说明可译。
10. **数字与单位**：~30 GB、131K、142K、8.7%、50 Hz、20 ms、0.2–0.8 m/s、±0.1 rad 等一律原样。
11. **HTML 标签**：`<video>`、`<figure>`、`<figcaption>`、`<div style="display: grid; ...">` 整体保留（figcaption 文本可译）。
12. **emoji**：✅ ❌ ⚠️ ❗️ 等保留。

---

## 3. MyST / Sphinx 格式规则

- 指令名与选项不可改：```` ```{note} ````、```` ```{tip} ````、```` ```{warning} ````、```` ```{danger} ````、```` ```{important} ````、```` ```{image} ````、```` ```{video} ```` 及 `:class:`、`:width:`、`:align:`、`:alt:` 等。
- ```` ```{admonition} 标题 ```` 的**标题文本可译**，指令名与 `:class: note/danger/...` 不可改。
- `{video}` / `{image}` 指令下方或内部的斜体、图注文字**可译**。
- Markdown 引用块 `> **Note**:`（installation_training.md、vla_inference.md）不是 admonition，保留 `>` 与加粗。
- 译文标题会改变自动生成的锚点 slug；凡有跨文件 `#anchor` 引用的标题，需核对锚点仍能解析（必要时保留显式锚点目标）。

---

## 4. 专有名词清单（一律保留英文）

产品/项目：SONIC、GEAR-SONIC、GR00T、Isaac-GR00T N1.5/N1.6/N1.7、GR00T-N1.7-3B、Decoupled WBC、GEM-X、LeRobot、Isaac Lab、Isaac Sim、Isaac Teleop、CloudXR、DeviceIO、XRoboToolkit（XR-Robotics）、PICO / PICO 4 / PICO 4 Pro / PICO Motion Tracker、Unitree G1 / H2、Unitree SDK2、Dex3、Bones-SEED、SOMA、SMPL、BVH、AMASS（未出现则忽略）、SteamVR/WebXR/OpenXR、Hugging Face / HF、HuggingFace TRL / Accelerate、W&B (Weights & Biases)、Hydra、TensorRT、CUDA、cuDNN、ONNX、PyTorch、MuJoCo、Pinocchio、IsaacLab 关节顺序、ZMQ / ZeroMQ、ROS2 / DDS / CycloneDDS / RViz / Gazebo、Docker、Git LFS、tmux、systemd、Jetson / Orin / Orin NX / JetPack 6 / Thor、Ubuntu、Debian、Wi-Fi、APK、DEB、TAR、uv、joblib、DepthAI、v4l2、OAK-D、RealSense、ZED、YOLOX、ViTPose、PPO、FSQ、GAE、KL、MPJPE、FP16/FP32、CRC、IMU、NVMe SSD、Fanttik。

代码标识符：`gear_sonic`、`gear_sonic_deploy`、`decoupled_wbc`、`download_from_hf.py`、`deploy.sh`、`run_sim_loop.py`、`eval_agent_trl.py`、`train_agent_trl.py`、`launch_inference.py`、`run_gr00t_server.py`、`pico_manager_thread_server.py`、`soma_to_smpl.py`、`PolicyServer` / `PolicyClient`、`zmq_manager`、`g1_debug`、`sonic_release` / `sonic_v1_1` / `sonic_bones_seed` / `sonic_h2`、`low_latency`、`last.pt`、`observation_config.yaml` 等。

---

## 5. 统一术语表（已消歧，全站照此执行）

> 原则：motion 统一译"动作"（动作库/动作序列/参考动作/动作捕捉）；heading 统一译"朝向"（机器人语境）；校准统一用"校准"（对应 PICO 界面 Calibrate）；token、latent 相关词保留英文"token"，"latent"译"潜在/潜空间"。

### 5.1 通用 RL / 机器人学

| 英文 | 中文 | 备注 |
|---|---|---|
| policy | 策略 | |
| reward / reward term / reward weight | 奖励 / 奖励项 / 奖励权重 | |
| observation / action | 观测 / 动作 | LeRobot 键名不译 |
| privileged observations | 特权观测 | |
| proprioception | 本体感觉 | |
| checkpoint | 检查点 | |
| fine-tuning / post-training | 微调 / 后训练 | GR00T 官方用语 |
| training from scratch | 从零训练 | |
| evaluation / sanity-check | 评估 / 快速验证 | |
| episode / termination / timeout reset | 回合 / 终止（条件）/ 超时重置 | |
| success rate / MPJPE | 成功率 / MPJPE（每关节平均位置误差） | |
| curriculum (learning) | 课程学习 | |
| adaptive (motion) sampling | 自适应（动作）采样 | |
| domain randomization (events) | 域随机化（事件） | |
| PPO / GAE / actor / critic | PPO / 广义优势估计 / Actor / Critic | 首现可注"近端策略优化" |
| rollout / mini-batch / clip parameter / entropy bonus | rollout（轨迹采样）/ 小批次 / 裁剪参数 / 熵奖励系数 | |
| discount factor / desired_kl / learning rate | 折扣因子 / 目标 KL 散度 / 学习率 | |
| headless | 无头模式 | 首现括注 headless |
| viewer / rendering | 查看器 / 渲染 | |
| num_envs（并行环境数） | 并行环境数 | 键名不译 |
| sim-to-real / sim-to-sim | 仿真到真实 / Sim2Sim（仿真到仿真） | sim2sim 常保留英文 |
| inference / inference pipeline | 推理 / 推理流水线 | |
| deployment / deployment binary | 部署 / 部署二进制程序 | |
| build / flashing / burn image | 编译构建 / 刷机 / 烧录镜像 | |
| host / container / workstation / onboard | 宿主机 / 容器 / 工作站 / 机载 | |
| troubleshooting | 故障排除 | |
| emergency stop (E-stop) | 紧急停止（急停） | 全站统一"急停"可简用 |
| safety zone / safety operator / gantry | 安全区 / 安全员 / 龙门架 | |
| state machine / control chain | 状态机 / 控制链路 | |

### 5.2 控制器与模型结构

| 英文 | 中文 | 备注 |
|---|---|---|
| whole-body control (WBC) | 全身控制 | WBC 保留 |
| whole-body teleoperation | 全身遥操作 | |
| universal-token controller | 通用 token 控制器 | |
| encoder / decoder / tokenizer | 编码器 / 解码器 / tokenizer | |
| motion token / latent motion token | 运动 token / 潜在运动 token | token 不译 |
| latent (space/vector) | 潜空间 / 潜向量 | |
| FSQ (Finite Scalar Quantization) / quantizer | 有限标量量化 / 量化器 | FSQ 保留 |
| action transform module (ATM) | 动作变换模块（ATM） | |
| VLA (Vision-Language-Action) | 视觉-语言-动作（VLA）模型 | 缩写保留 |
| action space / action chunk / action horizon | 动作空间 / 动作块 / 动作视野 | |
| embodiment / new embodiments | 具身 / 新机器人本体（新 Embodiment） | 首现括注；标签值不译 |
| demonstration (teleop demo) | 示教（遥操作演示） | |
| data collection / annotation / post-processing | 数据采集 / 标注 / 后处理 | |
| discard / flagged for removal | 丢弃 / 标记为待删除 | |
| batch size / global batch size / distributed training | 批大小 / 全局批大小 / 分布式训练 | |
| color jitter (brightness/contrast/saturation/hue) | 颜色抖动（亮度/对比度/饱和度/色调） | 键名不译 |
| data augmentation / wrist-pose augmentation | 数据增强 / 腕部姿态增强 | |
| freeze-frame augmentation / upper-body augmentation | 冻结帧增强 / 上半身动作增强 | |
| loss curve / plateau / convergence | 损失曲线 / 趋于平稳 / 收敛 | |

### 5.3 动作数据与运动学

| 英文 | 中文 | 备注 |
|---|---|---|
| motion library (motion_lib) | 动作库 | |
| reference motion / motion clip / motion sequence | 参考动作 / 动作片段 / 动作序列 | |
| motion playback / replay | 动作回放 / 重播 | |
| motion set / styled walking | 动作集 / 风格化行走 | |
| retargeting / retargeted data | （动作）重定向 / 重定向后的数据 | 项目核心词 |
| motion capture (mocap) / motion capture dataset | 动作捕捉 / 动作捕捉数据集 | |
| kinematic planner | 运动学规划器 | |
| locomotion / gait / strafe | （双足）移动 / 步态 / 横移 | |
| heading / delta heading / facing direction / yaw | 朝向 / 朝向增量 / 面朝方向 / 偏航 | heading 统一"朝向" |
| pitch / roll | 俯仰 / 横滚 | |
| joint position / velocity (qpos/qvel) | 关节位置 / 关节速度 | qpos/qvel 保留 |
| joint command / joint targets | 关节指令 / 关节目标 | |
| DOF / joint limits / effort limit / torque | 自由度 / 关节限位 / 力矩上限 / 力矩 | DOF 常保留缩写 |
| PD gains / Kp / Kd (KP/KD) | PD 增益 / 刚度 KP / 阻尼 KD | 项目用大写 KP/KD |
| armature (rotor inertia) | 转子惯量（armature） | |
| natural frequency / damping ratio / critically damped / overdamped | 固有频率 / 阻尼比 / 临界阻尼 / 过阻尼 | |
| forward kinematics (FK) / inverse kinematics (IK) | 正运动学 / 逆运动学 | |
| kinematic tree / body (link) / articulation | 运动学树 / 刚体（连杆）/ articulation（保留） | |
| root / pelvis / root-local / root height | 根节点 / 骨盆 / 根坐标系下 / 根高度 | |
| quaternion (w, x, y, z) / scalar-first (wxyz) | 四元数 / 标量在前（wxyz） | 顺序标注保留 |
| axis-angle / 6D rotation / Euler angles | 轴角 / 6D 旋转 / 欧拉角 | |
| Z-up / Y-up | Z 轴朝上 / Y 轴朝上 | 可保留 Z-up/Y-up |
| anchor (root anchor) | 锚点 | tracking_anchor_* 不译 |
| end-effector / gripper / Dex3 hand | 末端执行器 / 末端夹持器 / Dex3 灵巧手 | |
| ankle-pitch motors / wrist joints | 踝关节俯仰电机 / 腕部关节 | |
| 3-point / 5-point tracking (VR_3PT) | 三点 / 五点跟踪 | 头+双腕；五点加双脚 |
| keypoints / 2D pose estimation / diffusion denoiser | 关键点 / 2D 姿态估计 / 扩散去噪器 | |
| calibration / calibration pose / recalibrate | 校准 / 校准姿态 / 重新校准 | |
| compliance | 柔顺度 | 手部柔顺度 |
| grasp / manipulation / pick-and-place | 抓握 / 操作 / 抓取与放置 | |
| look-ahead / reference lookahead / reference horizon | 前瞻 / 参考前瞻 / 参考时域 | 与"端到端系统延迟"严格区分 |
| latency / latency compensation / frame rate / dropout | 延迟 / 延迟补偿 / 帧率 / 丢帧 | |
| stale frames / frozen frames / catch-up | 过期帧 / 冻结帧 / 追帧 | |
| temporal smoothing / jitter / drift / laggy | 时域平滑 / 抖动 / 漂移 / 延迟感 | |
| publisher / subscriber / topic / wire format | 发布端 / 订阅端 / topic（主题）/ 线上格式 | |
| streaming / streamer / conflated | 流式传输（推流）/ 推流端 / 仅保留最新消息 | |
| canonicalization | 规范化 | planner 内部处理 |
| prediction horizon / waypoint / replan / resampling | 预测时域 / 路径点 / 重规划 / 重采样 | |
| linear interpolation / slerp / cross-fade / blending | 线性插值 / 球面线性插值 / 交叉淡化 / 动作融合 | |
| CUDA graph / pinned memory / kernel launch | CUDA 图 / 锁页内存 / 内核启动 | |
| hot path / ring buffer / thread-safe / mutex | 热路径（高频执行路径）/ 环形缓冲区 / 线程安全 / 互斥锁 | |
| momentum (system) / dead zone | 动量（系统）/ 死区 | |
| crouch / squat / kneel / crawl / boxing (jab/hook) | 蹲伏 / 下蹲 / 跪地 / 爬行 / 拳击（直拳/勾拳） | 模式名统一译法 |
| idle / slowWalk / walk / run（模式值） | 保留英文，描述性文字可译（待机/慢走/行走/奔跑） | 模式值 `slowWalk` 等不译 |

---

## 6. 跨文件一致性要求

1. **模式标识符**（`OFF/POSE/PLANNER/PLANNER_FROZEN_UPPER/VR_3PT`、`CALIB/CALIB_FULL`）出现在 4 个文件中，译法/括注必须完全一致。
2. **步态模式名**（Idle…Boxing…）在 gamepad.md、keyboard.md、vr_wholebody_teleop.md、planner_onnx.md 中集合不同，每种动作一个固定中文译名（如 开心/潜行/受伤/下蹲/双膝跪地/单膝跪地/手膝爬行/肘部爬行/匍匐）。
3. **急停 / 安全警告 admonition** 出现在 6+ 个文件，中文措辞完全一致。
4. **校准 vs 标定**：全站统一"校准"。
5. **动作库 vs 运动库**：全站统一"动作库"。

---

## 7. 原文质量问题（翻译时按原意处理，勿照搬错误）

- 拼写错误：`plicy`（zmq.md）、`cammands`（isaac_teleop_publisher_setup.md）、`emergecy stop` / `Reclibrate`（teleoperation.md）、`upper body controller by planner`（vr_wholebody_teleop.md，应为 controlled）、`the robot .`（多余空格）。
- gamepad.md 操作步骤编号跳过 3（1,2,4,5,…），按项目惯例决定是否规范化。
- **training_data.md 在第 70 行句子中间截断**（"After downloading, extract the motion archives:" 后无内容），源文件疑似缺失段落。
- installation_deploy.md 个别句子语义含糊（"production-ready" 用法、"we require the onboard Orin…"缺限定词），按"G1 机载 Orin 计算机"理解。

---

## 8. 建议工作流

1. 逐文件翻译，**格式标记全部原样保留**（见第 2、3 节）。
2. 每译完一个文件，用本表自查术语一致性。
3. 译文使用简体中文，全角标点；代码、路径、键名周围保留半角空格分隔。
4. `index.rst` / `conf.py` 等站点级文件最后处理；`conf.py` 中如需设置 `language = 'zh_CN'` 与中文字体，单独确认。
