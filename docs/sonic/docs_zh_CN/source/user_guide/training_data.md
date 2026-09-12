# 训练数据

## BONES-SEED

[BONES-SEED](https://huggingface.co/datasets/bones-studio/seed)（Skeletal Everyday Embodiment Dataset）是由 [Bones Studio](https://bones.studio/datasets) 创建的面向人形机器人领域的开放数据集，包含 **142,220 段带标注的人体运动动画**。它以 SOMA 和 Unitree G1 格式提供动作捕捉数据，并附带自然语言描述、时序分段标签和详细的骨架元数据。

| | |
|---|---|
| **动作总数** | 142,220（71,132 原始 + 71,088 镜像） |
| **总时长** | ~288 小时（@ 120 fps） |
| **表演者** | 522 名演员（253 女 / 269 男） |
| **年龄范围** | 17–71 岁 |
| **身高范围** | 145–199 cm |
| **体重范围** | 38–145 kg |
| **输出格式** | SOMA Uniform · SOMA Proportional · Unitree G1 MuJoCo 兼容格式 |
| **标注** | 每个动作最多 6 条自然语言描述 + 时序分段 + 骨架元数据 |

### 与 SONIC 的关联

BONES-SEED 构成了 SONIC 训练数据的一个很大子集：

- **Unitree G1 关节轨迹** — 已为 MuJoCo 重定向，可直接用于动作跟踪训练
- **广泛的动作覆盖** — 涵盖移动、操作、舞蹈、体育、交流与日常活动，共 8 个大类、20 个子类
- **丰富的语言标注** — 每个动作最多 6 条自然语言描述，支持语言条件策略学习
- **时序分段** — 每个动作带时间戳的阶段标签，便于结构化技能分解
- **表演者多样性** — 522 名演员，涵盖广泛的体型、年龄与运动风格

### 动作类别

| 包       | 动作数 | 说明                                                             |
|---------------|---------|-------------------------------------------------------------------------|
| Locomotion    | 74,488  | 走、慢跑、跳跃、攀爬、爬行、转身及过渡动作 |
| Communication | 21,493  | 手势、指点、注视及交流性肢体语言            |
| Interactions  | 14,643  | 物体操作、抓取与放置、搬运及工具使用             |
| Dances        | 11,006  | 多种风格的全身舞蹈表演                     |
| Gaming        | 8,700   | 游戏风格动作与动态运动                             |
| Everyday      | 5,816   | 家务、饮食、坐、阅读及日常活动      |
| Sport         | 3,993   | 竞技性运动与专项体育动作                          |
| Other         | 2,081   | 特技、武术及边缘情况动作                             |

### 数据格式

每个动作都有三种格式：

- **SOMA Proportional（BVH）** — 保留演员原始身体比例的骨架
- **SOMA Uniform（BVH）** — 所有动作共享的标准化骨架，便于批处理
- **Unitree G1（CSV）** — 重定向到 Unitree G1 人形机器人的关节角轨迹

### 下载

```bash
# 使用 Hugging Face CLI
pip install huggingface_hub
huggingface-cli download bones-studio/seed --repo-type dataset --local-dir ./bones-seed
```

```python
# 使用 Python
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="bones-studio/seed",
    repo_type="dataset",
    local_dir="./bones-seed"
)
```

下载完成后，解压动作压缩包：
