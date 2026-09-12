# 故障排除

常见问题与解决方法。如果这里没有列出你的问题，请查看
[GitHub issues](https://github.com/NVlabs/GR00T-WholeBodyControl/issues) 页面。

---

## 1. `ModuleNotFoundError: No module named 'isaaclab'`

**症状：** 训练或评估脚本立即退出并报 import 错误。

**原因：** 未安装 Isaac Lab，或者你运行在错误的 Python 环境中。Isaac Lab 不是 pip 依赖 — 必须单独安装。

**解决方法：**

1. 按照
   [官方指南](https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html)安装 Isaac Lab。
2. 运行前确保激活正确的 conda/venv 环境：
   ```bash
   conda activate env_isaaclab  # 或你实际命名的环境名
   python -c "import isaaclab; print(isaaclab.__version__)"
   ```

---

## 2. 网格文件是微小的文本文件（未安装 Git LFS）

**症状：** 仿真崩溃，或渲染出不可见/破损的机器人。网格文件（`.stl`、`.STL`）只有约 130 字节，内容是 `version https://git-lfs.github.com/spec/v1` 之类的文本。

**原因：** 克隆仓库时未启用 Git LFS。大文件（网格、ONNX 模型）通过 Git LFS 存储，需要单独拉取。

**解决方法：**

```bash
sudo apt install git-lfs
git lfs install
git lfs pull
```

验证：`ls -la gear_sonic/data/assets/robot_description/urdf/g1/main.urdf` 应为 60KB 以上，而不是约 130 字节。

---

## 3. 加载检查点时报 `RuntimeError: size mismatch`

**症状：** 训练或评估崩溃，报类似如下错误：
```
size mismatch for actor_module.decoders.g1_dyn.module.0.weight:
  copying a param with shape torch.Size([2048, 994]) from checkpoint,
  the shape in current model is torch.Size([4096, 994])
```

**原因：** 实验配置定义的网络结构与检查点训练时的结构不一致。常见于配置把 `hidden_dims` 覆盖为不同大小的情况。

**解决方法：** 确保实验配置与检查点的网络结构匹配。查看随检查点一起保存的 `config.yaml`，获取正确的 `hidden_dims`、编码器/解码器设置等。发布的 `sonic_release` 检查点使用：

```yaml
decoders:
  g1_dyn:
    params:
      module_config_dict:
        layer_config:
          hidden_dims: [2048, 2048, 1024, 1024, 512, 512]
```

---

## 4. pip 安装时 `trl` / `transformers` 版本冲突

**症状：** `pip install -e "gear_sonic/[training]"` 失败，报 `transformers` 版本不兼容的依赖解析错误。

**原因：** `trl==0.28.0` 要求 `transformers>=4.56.2`。如果你固定或安装了较旧的 `transformers`，pip 将无法完成解析。

**解决方法：**

```bash
pip install -e "gear_sonic/[training]" --upgrade
```

或者在全新环境中安装。如果其他项目需要特定版本的 `transformers`，请为 SONIC 训练使用单独的 venv。

---

## 5. TensorRT 构建失败（未设置 `TensorRT_ROOT`）

**症状：** C++ 部署构建期间出现 CMake 错误：
```
Could not find a package configuration file provided by "TensorRT"
```

**原因：** 未设置 `TensorRT_ROOT` 环境变量，或未安装 TensorRT。

**解决方法：**

1. 下载正确的 TensorRT 版本（TAR 包，而非 DEB）：

   | 平台 | TensorRT 版本 |
   |---|---|
   | x86_64（桌面） | **10.13**（必需） |
   | Jetson / G1 机载 Orin | **10.7**（必需；JetPack 6） |

2. 解压并设置环境变量：
   ```bash
   export TensorRT_ROOT=$HOME/TensorRT
   echo 'export TensorRT_ROOT=$HOME/TensorRT' >> ~/.bashrc
   ```

---

## 6. 动作文件路径错误（`FileNotFoundError` 或动作库为空）

**症状：** 训练因动作路径 `FileNotFoundError` 崩溃，或者启动后日志显示 `0 motions loaded`。

**原因：** 实验配置中的占位路径（例如
`data/motion_lib_bones_seed/robot_filtered`）在你的机器上并不存在。动作数据路径必须在命令行提供。

**解决方法：** 始终显式传入动作数据路径：

```bash
python gear_sonic/train_agent_trl.py \
    +exp=manager/universal_token/all_modes/sonic_release \
    ++manager_env.commands.motion.motion_lib_cfg.motion_file=<path/to/robot_filtered> \
    ++manager_env.commands.motion.motion_lib_cfg.smpl_motion_file=<path/to/smpl_filtered>
```

如需快速测试，可从 HuggingFace 下载示例数据：

```bash
hf download nvidia/GEAR-SONIC \
    --include "config.json" \
    --include "sample_data/*" \
    --local-dir .
```

---

## 7. 刚体名称错误（`RuntimeError: body 'xxx' not found`）

**症状：** Isaac Lab 崩溃，报刚体/关节名称在机器人 articulation 中找不到的错误。

**原因：** 某个配置 YAML 引用了你的机器人上不存在的刚体名称。在用 G1 配置驱动其他机器人（例如 H2）时很常见。

**解决方法：** 检查是哪个刚体名称失败了，并找到它的引用位置：

```bash
grep -rn "the_failing_body_name" gear_sonic/config/
```

在实验配置中覆盖该刚体名称，或查阅
[新机器人本体训练](new_embodiments.md)指南，获取引用刚体名称的配置文件完整列表。

---

## 8. 机器人第一帧就爆掉或摔倒

**症状：** 仿真一开始机器人就变成布娃娃、飞出去或瘫倒。

**原因：** 通常为以下之一：

- **初始高度不对** — 机器人生成在地面之内或过高。
  检查机器人配置中的 `init_state.pos`（z 值为出生高度）。
- **KP/KD 值不对** — 刚度（KP）过低时关节没有保持力矩；过高时仿真变得不稳定。调优指南参见
  [新机器人本体训练](new_embodiments.md)。
- **动作缩放过大** — 策略输出使关节运动过于激进。
  减小 `action_scale` 值。
- **默认关节角度不对** — 机器人以不可能的姿态起步。
  检查 `init_state.joint_pos` 是否对应稳定的站立构型。

**调试：** 用 `num_envs=1 headless=False` 运行并观察前几帧。

---

## 9. 部署时机器人行为异常（TensorRT 版本不对）

**症状：** C++ 部署时机器人能站立但动作紊乱、漂移或动作不自然 — 尽管同一个检查点在 Isaac Lab 或 MuJoCo 仿真中工作正常。

**原因：** 你使用的 TensorRT 版本与要求的不一致。TensorRT 版本不匹配会产生**静默错误的推理结果** — 模型运行不报错，但输出的动作不正确。

**解决方法：** 你**必须**使用确切的 TensorRT 版本：

| 平台 | 所需版本 |
|---|---|
| x86_64（桌面） | **TensorRT 10.13** |
| Jetson / G1 机载 Orin | **TensorRT 10.7**（JetPack 6） |

验证你的版本：

```bash
echo $TensorRT_ROOT
ls $TensorRT_ROOT/lib/libnvinfer.so*
```

如果版本不对，请从
[NVIDIA Developer](https://developer.nvidia.com/tensorrt/download/10x) 下载正确版本，并重新编译 C++ 部署二进制程序。

---

## 10. MuJoCo 仿真中出现 `ChannelFactory create domain error`

**症状：** `run_sim_loop.py` 崩溃并报：
```
[ChannelFactory] create domain error. msg: Occurred upon initialisation
of a cyclonedds.domain.Domain
```

**原因：** CycloneDDS 域初始化冲突。SimulatorFactory 重新初始化了一个已经创建的 channel。

**解决方法：** 这是一个已知问题（[#77](https://github.com/NVlabs/GR00T-WholeBodyControl/issues/77)）。
临时解决方法：注释掉 simulator factory 中重复的 channel 初始化，或确保你的机器上没有其他 DDS 进程占用同一 domain。

---

## 11. SMPL 跟踪不稳定或漂移

**症状：** 机器人对 G1 动作跟踪表现良好，但使用 SMPL 编码器输入时漂移或不稳定。

**原因：** SMPL 数据可能坐标约定不匹配（y-up 与 z-up）、关节顺序不正确，或 SMPL 到机器人的重定向质量较差。

**解决方法：**

- 如果 SMPL 数据使用 y-up 坐标，请确认配置中设置了 `smpl_y_up: true`。
- 检查 SMPL PKL 文件的形状是否正确：`smpl_joints` 应为
  `(T, 24, 3)`。
- 先用 `smpl_motion_file: dummy` 训练，确认机器人编码器工作正常后，再引入 SMPL。

---

## 12. Docker 中 MuJoCo 查看器渲染异常

**症状：** 在配备 Intel 显示控制器的机器上于 Docker 内运行时，MuJoCo 窗口黑屏、花屏或出现渲染伪影。

**原因：** Docker 内 Intel iGPU 与 NVIDIA dGPU 之间的 GPU 直通或显示驱动冲突。

**解决方法：** 强制使用 NVIDIA GPU 渲染：

```bash
export __NV_PRIME_RENDER_OFFLOAD=1
export __GLX_VENDOR_LIBRARY_NAME=nvidia
```

或在 docker run 命令中加 `--gpus all -e DISPLAY=$DISPLAY`。详情见
[#25](https://github.com/NVlabs/GR00T-WholeBodyControl/issues/25)。

---

## 13. `deploy.sh` 在 Orin 上无法绑定 ZMQ 端口 5557

**症状：** `deploy.sh` 退出并报 ZMQ 端口 5557 绑定错误。

**原因：** Unitree 系统服务（`iphone_server.service`）已经在监听 5557 端口。

**解决方法：**

```bash
sudo systemctl stop iphone_server.service
```

然后重新运行部署。该服务会在下次开机时自启；若要在重启后保持停止状态，使用 `sudo systemctl disable iphone_server.service`。

---

## 仍然无法解决？

- 在[现有 issues](https://github.com/NVlabs/GR00T-WholeBodyControl/issues) 中搜索
- 提交[新 issue](https://github.com/NVlabs/GR00T-WholeBodyControl/issues/new)
  并附上你的报错信息、Python 版本和操作系统
