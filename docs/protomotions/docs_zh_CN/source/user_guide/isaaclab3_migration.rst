IsaacLab 3 迁移固定版本
========================

ProtoMotions 的 IsaacLab 后端面向公开 IsaacLab ``develop`` 分支，
该分支包含了 issue `#5085`_ 中关于嵌套刚体接触传感器的修复
（由 PR `#6259`_ 合入，合并提交 ``17136c6``）。

固定的版本
---------------

* 公开 IsaacLab 提交：``4ecd0b036da19ff6ad2bb4d621f886b63e9f6db8``
* 确认时间：2026-07-16
* 保证：新于 ``17136c6`` / PR `#6259`

人形资产
---------------

人形机器人配置仅通过 ``RobotAssetConfig.asset_file_name`` 声明 MJCF。
在 IsaacLab 场景构建时，``convert_robot_mjcf_to_usd()`` 会调用 IsaacLab 3
的 ``MjcfConverterCfg`` / ``MjcfConverter``，并通过 ``UsdFileCfg`` 生成实例。
接触传感器的 prim 路径会从转换后的 USD 层级（扁平或嵌套）中解析。
非 IsaacLab 仿真器继续加载相同的 MJCF 文件。

MJCF 导入器的临时兼容处理
--------------------------------------

IsaacLab 3 的转换器目前会把相同刚体之间的多个单轴 MJCF 关节
折叠成一个 PhysX D6 关节。ProtoMotions 在首次转换时安装了一个
范围有限的兼容性修复，它保留共享的源坐标系、恢复 MuJoCo 弹簧增益，
并锁定未使用的 D6 轴。转换仍然由 IsaacLab 负责；一旦上游导入器
包含了对应修复，该修复就会被移除。转换器缓存中包含修复版本号，
因此更新前生成的 USD 不会被静默复用。

对于 SOMA 和 SMPL，IsaacLab 会以 ``:0``、``:1``、``:2`` 后缀
暴露这些折叠后的轴。ProtoMotions 在配置执行器和仿真器状态之前，
会将这些后端名称映射回语义化的 MJCF 自由度名称。

免 Kit 空跑
----------------

单元测试会注入一个转换器工厂，或设置
``PROTOMOTIONS_ISAACLAB_MJCF_DRY_RUN=1``，从而在不启动 Kit 的情况下
演练路径/配置/缓存逻辑。

无界面冒烟测试（需要 IsaacLab 3 + Kit）
------------------------------------------

在检出上述固定版本的 IsaacLab 3 环境中运行::

   python protomotions/inference_agent.py \\
     --checkpoint data/pretrained_models/motion_tracker/g1-bones-deploy/last.ckpt \\
     --motion-file data/motion_for_trackers/g1_bones_seed_mini.pt \\
     --simulator isaaclab --num-envs 1 --headless

该流程会转换机器人 MJCF、构建关节体/接触传感器，并步进物理。
在本地验证中，Kit 在冷启动的 Torch 预热期间达到十分钟上限前
已完成场景搭建与策略实体化。使用相同固定运行时的直接仿真器教程
（``examples/tutorial/0_create_simulator.py``）则完成了初始化、重置、
步进与状态读取，共超过 3,800 次动作/物理循环后才触发其 180 秒的
保护上限。在冷启动的机器上，首次策略编译请预留更多时间。

.. _#5085: https://github.com/isaac-sim/IsaacLab/issues/5085
.. _#6259: https://github.com/isaac-sim/IsaacLab/pull/6259
