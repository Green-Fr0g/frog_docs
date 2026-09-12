# 快速上手

几分钟内即可开始使用 SONIC！

```{admonition} 前提条件
:class: note
1. **已完成[安装指南](installation_deploy)** — 已安装 TensorRT、已克隆仓库，且 C++ 部署已编译完成。
2. **已下载模型检查点** — 在仓库根目录运行 `python download_from_hf.py`。详见[下载模型检查点](download_models)。
```

```{admonition} 安全警告
:class: danger
机器人可能造成危险。请确保留出清晰的安全区，安排一名安全员在键盘前随时准备触发紧急停止（急停），并自行承担使用本软件的风险。作者与贡献者不对因使用或滥用本项目而造成的任何损害、伤害或损失负责。
```

## Isaac Lab 评估

使用 Isaac Lab 在仿真中快速验证（sanity-check）已发布的 PyTorch 检查点。请在 Isaac Lab Python 环境中、从仓库根目录运行以下命令。

如果你只下载了部署用 ONNX 文件，请先获取评估检查点和小型示例动作集：

```sh
python download_from_hf.py --training --no-smpl
python download_from_hf.py --sample
```

要打开 Isaac Sim 查看器并观察策略：

```sh
python gear_sonic/eval_agent_trl.py \
    +checkpoint=sonic_release/last.pt \
    +headless=False \
    ++num_envs=1 \
    ++manager_env.observations.policy.enable_corruption=False \
    ++manager_env.observations.tokenizer.enable_corruption=False \
    "++manager_env.commands.motion.motion_lib_cfg.motion_file=sample_data/robot_filtered" \
    "++manager_env.commands.motion.motion_lib_cfg.smpl_motion_file=sample_data/smpl_filtered"
```

让该进程保持运行，以便你在查看器中观察，然后按 `Ctrl+C` 停止。

如需快速输出指标：

```sh
python gear_sonic/eval_agent_trl.py \
    +checkpoint=sonic_release/last.pt \
    +headless=True \
    ++eval_callbacks=im_eval \
    ++run_eval_loop=False \
    ++num_envs=128 \
    ++manager_env.observations.policy.enable_corruption=False \
    ++manager_env.observations.tokenizer.enable_corruption=False \
    "+manager_env/terminations=tracking/eval" \
    "++manager_env.commands.motion.motion_lib_cfg.max_unique_motions=512" \
    "++manager_env.commands.motion.motion_lib_cfg.motion_file=sample_data/robot_filtered" \
    "++manager_env.commands.motion.motion_lib_cfg.smpl_motion_file=sample_data/smpl_filtered"
```

若要渲染视频：

```sh
python gear_sonic/eval_agent_trl.py \
    +checkpoint=sonic_release/last.pt \
    +headless=True \
    ++eval_callbacks=im_eval \
    ++run_eval_loop=False \
    ++num_envs=8 \
    ++manager_env.config.render_results=True \
    "++manager_env.config.save_rendering_dir=/tmp/sonic_renders" \
    ++manager_env.config.env_spacing=10.0 \
    "~manager_env/recorders=empty" "+manager_env/recorders=render" \
    ++manager_env.observations.policy.enable_corruption=False \
    ++manager_env.observations.tokenizer.enable_corruption=False \
    "++manager_env.commands.motion.motion_lib_cfg.motion_file=sample_data/robot_filtered" \
    "++manager_env.commands.motion.motion_lib_cfg.smpl_motion_file=sample_data/smpl_filtered"
```

视频会写入 `/tmp/sonic_renders`。完整数据集评估及预期指标请参阅[训练指南](../user_guide/training.md#evaluation)。


## MuJoCo 中的 Sim2Sim

<video width="100%" autoplay loop muted playsinline style="border-radius: 8px; margin: 1em 0;">
  <source src="../_static/sim2sim.mp4" type="video/mp4">
</video>

若要在 MuJoCo 仿真器中测试，请在两个独立的终端中分别运行仿真循环和部署脚本。

```{note}
MuJoCo 仿真器（终端 1）在**宿主机**上的 Python 虚拟环境中运行——它**不在** Docker 容器内。部署二进制程序（终端 2）既可以在宿主机上原生运行，也可以在 Docker 容器内运行。如果你使用 Docker，请在宿主机上运行终端 1，在容器内运行终端 2。
```

### 一次性配置：安装 MuJoCo 仿真环境

在**宿主机**上（Docker 之外），从**仓库根目录**（`GR00T-WholeBodyControl/`）运行：

```sh
bash install_scripts/install_mujoco_sim.sh
```

这会创建一个轻量级的 `.venv_sim` 虚拟环境，其中仅包含仿真器所需的包（MuJoCo、Pinocchio、Unitree SDK2 等）。

### 运行 sim2sim 循环

我们强烈建议在部署到真实硬件之前，先在仿真中完整走一遍该流程，并熟悉各项控制。

**终端 1 — MuJoCo 仿真器**（宿主机，仓库根目录下）：

```sh
source .venv_sim/bin/activate
python gear_sonic/scripts/run_sim_loop.py
```

**终端 2 — 部署**（宿主机或 Docker，`gear_sonic_deploy/` 目录下）：

```sh
bash deploy.sh sim
```

**启动控制：**

1. 在终端 2（deploy.sh）中，按 **`]`** 启动策略。
2. 点击 MuJoCo 查看器窗口，按 **`9`** 将机器人下放到地面。
3. 回到终端 2。按 **`T`** 播放当前参考动作——机器人会将其执行完毕。
4. 按 **`N`** 或 **`P`** 切换到下一条或上一条动作序列。
5. 再按 **`T`** 播放新的动作。
6. 一条动作播放完毕后，可以再按 **`T`** 重新播放同一条动作。如果想停下并回到当前动作的第一帧，按 **`R`** 从头重新开始。这可以用来在不终止策略的情况下停止动作。
7. 操作完成或需要**急停**时，按 **`O`** 停止控制并退出。

更多控制方式请参阅 [Keyboard（键盘）](../tutorials/keyboard.md)、[Gamepad（手柄）](../tutorials/gamepad.md)、[ZMQ Streaming（ZMQ 推流）](../tutorials/zmq.md)和 [Interface Manager（接口管理器）](../tutorials/manager.md)教程。

## 真实机器人

要在真实的 G1 机器人上部署，运行：

```sh
./deploy.sh real
```

## 在线可视化

启动可视化工具并连接到正在运行的 `g1_deploy` 可执行程序：

```sh
python visualize_motion.py --realtime_debug_url tcp://localhost:5557
```

说明：
- 默认端口：5557（可通过 `--zmq-out-port <port>` 修改）
- 默认 topic（主题）：`g1_debug`（可在可执行程序上用 `--zmq-out-topic <topic>`、在可视化工具上用 `--realtime_debug_topic <topic>` 修改）
- 对于真实机器人，请将 `localhost` 替换为机器人的 IP 地址

离线动作 CSV 的可视化与日志详情，请参阅[部署代码与程序流程](../references/deployment_code.md)。

更多进阶用法请参阅 [Keyboard（键盘）](../tutorials/keyboard.md)、[Gamepad（手柄）](../tutorials/gamepad.md)、[ZMQ Streaming（ZMQ 推流）](../tutorials/zmq.md)、[VR Whole-Body Teleop（VR 全身遥操作）](../tutorials/vr_wholebody_teleop.md)和 [Interface Manager（接口管理器）](../tutorials/manager.md)教程。
