局限性
=======

在 Newton 以及这个 Isaac Lab 集成项目的早期开发阶段，
你很可能会遇到破坏性变更以及不完善的文档。

在框架达到正式发布之前，我们预计无法提供支持或调试协助。

以下按扩展分组列出了 Newton 实验特性分支目前支持的能力（并非全部）：

* isaaclab：
    * Articulation API（同时支持关节体和作为刚体的单刚体关节）
    * 接触传感器
    * 直接式与管理器式单智能体工作流
    * Omniverse Kit 可视化器
    * Newton 可视化器
* isaaclab_assets：
    * 四足机器人
        * Anymal-B、Anymal-C、Anymal-D
        * Unitree A1、Go1、Go2
        * Spot
    * 人形机器人
        * Unitree H1 与 G1
        * Cassie
    * 机械臂与灵巧手
        * Franka
        * UR10
        * Allegro Hand
    * 玩具示例
        * Cartpole
        * Ant
        * Humanoid
* isaaclab_tasks：
    * 直接式：
        * Cartpole（状态、RGB、深度）
        * Ant
        * Humanoid
        * Allegro Hand Repose Cube
    * 管理器式：
        * Cartpole（状态）
        * Ant
        * Humanoid
        * 运动（平地速度）
            * Anymal-B
            * Anymal-C
            * Anymal-D
            * Cassie
            * A1
            * Go1
            * Go2
            * Unitree G1
            * Unitree H1
        * 操作到达
            * Franka
            * UR10
