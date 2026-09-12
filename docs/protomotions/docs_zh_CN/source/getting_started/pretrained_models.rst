预训练模型
==========

每个随附的检查点旁边都有一张模型卡，其中包含训练配方、输入输出契约、各文件产物的角色、预期用途和局限性。

除非其模型卡另有说明，策略应当在其训练所用的仿真器上运行。推荐的检查点均在 IsaacLab 中训练或微调。
G1 部署跟踪器是目前唯一使用完整的面向迁移的域随机化方案训练的策略，因此预期可以迁移到兼容的仿真器和硬件上；
但这并不保证对所有后端或版本都成立。

.. list-table::
   :header-rows: 1
   :widths: 24 31 25 20

   * - 模型
     - 用途
     - 运行环境预期
     - 模型卡
   * - SOMA BONES-SEED GPC 先验
     - SOMA 动作的离散 GPC 先验
     - 仅 IsaacLab
     - `阅读模型卡 <https://github.com/NVlabs/ProtoMotions/blob/main/data/pretrained_models/gpc_prior/soma_bones/MODEL_CARD.md>`__
   * - SMPL MaskedMimic
     - 稀疏与掩码的未来动作控制
     - 仅 IsaacLab
     - `阅读模型卡 <https://github.com/NVlabs/ProtoMotions/blob/main/data/pretrained_models/masked_mimic/smpl/MODEL_CARD.md>`__
   * - G1 BONES-SEED 部署跟踪器
     - 域随机化的动作跟踪与部署
     - 在 IsaacLab 训练；预期可迁移
     - `阅读模型卡 <https://github.com/NVlabs/ProtoMotions/blob/main/data/pretrained_models/motion_tracker/g1-bones-deploy/MODEL_CARD.md>`__
   * - SMPL AMASS 平坦地形跟踪器
     - 平坦地面上的通用 SMPL 动作跟踪
     - 仅 IsaacLab
     - `阅读模型卡 <https://github.com/NVlabs/ProtoMotions/blob/main/data/pretrained_models/motion_tracker/smpl/MODEL_CARD.md>`__
   * - SMPL AMASS 地形跟踪器
     - 程序化生成地形上的通用 SMPL 动作跟踪
     - 仅 IsaacLab
     - `阅读模型卡 <https://github.com/NVlabs/ProtoMotions/blob/main/data/pretrained_models/motion_tracker/smpl-terrains/MODEL_CARD.md>`__
   * - SOMA BONES-SEED 跟踪器
     - 连续动作的 SOMA 动作跟踪
     - 仅 IsaacLab 微调版（``last_lab.ckpt``）
     - `阅读模型卡 <https://github.com/NVlabs/ProtoMotions/blob/main/data/pretrained_models/motion_tracker/soma-bones/MODEL_CARD.md>`__
   * - SOMA BONES-SEED FSQ 跟踪器
     - GPC 使用的离散 FSQ 跟踪器
     - 仅 IsaacLab
     - `阅读模型卡 <https://github.com/NVlabs/ProtoMotions/blob/main/data/pretrained_models/motion_tracker/soma_bones_fsq/MODEL_CARD.md>`__
   * - SOMA BONES-SEED FSQ AMP 跟踪器
     - 带 AMP 正则化的 FSQ 动作跟踪器
     - 仅 IsaacLab
     - `阅读模型卡 <https://github.com/NVlabs/ProtoMotions/blob/main/data/pretrained_models/motion_tracker/soma_bones_fsq_amp_muon/MODEL_CARD.md>`__
