.. _walkthrough_training_jetbot_reward_exploration:

探索 RL 问题
=========================

发给 Jetbot 的指令是一个指定期望行驶方向的单位向量，我们必须以某种方式让智能体感知到它，
以便智能体能相应地调整自己的动作。实现方式有很多种，"零阶" 的做法就是直接把指令加入观测空间。
首先，**编辑 ``IsaacLabTutorialEnvCfg``，把观测空间设为 9**：世界的速度向量包含机器人的线速度和角速度，
共 6 个维度，如果再把指令附加到这个向量后面，观测空间总共就是 9 个维度。

接下来，我们只需在获取观测时执行这个附加操作。我们还需要为后续使用计算前向向量。
Jetbot 的前向向量是 x 轴，因此我们把 ``root_link_quat_w`` 应用到 ``[1,0,0]`` 上，
即可得到世界坐标系下的前向向量。将 ``_get_observations`` 方法替换为以下内容：

.. code-block:: python

    def _get_observations(self) -> dict:
        self.velocity = self.robot.data.root_com_vel_w
        self.forwards = math_utils.quat_apply(self.robot.data.root_link_quat_w, self.robot.data.FORWARD_VEC_B)
        obs = torch.hstack((self.velocity, self.commands))
        observations = {"policy": obs}
        return observations

那么现在奖励应该是什么？

当机器人按预期表现时，它会以全速朝指令方向行驶。如果我们同时奖励 "向前行驶" 和 "与指令对齐"，
那么最大化这个组合信号应该会让机器人朝指令方向行驶……对吧？

我们来试一试！将 ``_get_rewards`` 方法替换为以下内容：

.. code-block:: python

    def _get_rewards(self) -> torch.Tensor:
        forward_reward = self.robot.data.root_com_lin_vel_b[:,0].reshape(-1,1)
        alignment_reward = torch.sum(self.forwards * self.commands, dim=-1, keepdim=True)
        total_reward = forward_reward + alignment_reward
        return total_reward

``forward_reward`` 是机器人在本体坐标系下质心线速度的 x 分量。我们知道
x 方向是该资产的前进方向，因此这应当等价于前向向量与世界坐标系下线速度的内积。
对齐项是前向向量与指令向量的内积：当它们指向同一方向时该项为 1，
指向相反方向时则为 -1。我们把它们相加得到组合奖励，终于可以开始训练了！
让我们看看会发生什么！

.. code-block:: bash

    python scripts/skrl/train.py --task=Template-Isaac-Lab-Tutorial-Direct-v0


.. figure:: https://download.isaacsim.omniverse.nvidia.com/isaaclab/images/walkthrough_naive_webp.webp
    :align: center
    :figwidth: 100%
    :alt: Naive results

我们肯定能做得更好！

奖励与观测调优
-------------------------------

在为训练调优环境时，根据经验，你应当让观测空间尽可能小。这是为了
减少模型中的参数数量（奥卡姆剃刀的字面体现），从而缩短训练时间。
在本例中，我们需要以某种方式编码与指令的对齐程度和前向速度。
一种方法是利用线性代数中的点积和叉积！将 ``_get_observations`` 的内容替换为以下内容：

.. code-block:: python

    def _get_observations(self) -> dict:
        self.velocity = self.robot.data.root_com_vel_w
        self.forwards = math_utils.quat_apply(self.robot.data.root_link_quat_w, self.robot.data.FORWARD_VEC_B)

        dot = torch.sum(self.forwards * self.commands, dim=-1, keepdim=True)
        cross = torch.cross(self.forwards, self.commands, dim=-1)[:,-1].reshape(-1,1)
        forward_speed = self.robot.data.root_com_lin_vel_b[:,0].reshape(-1,1)
        obs = torch.hstack((dot, cross, forward_speed))

        observations = {"policy": obs}
        return observations

我们还需要 **编辑 ``IsaacLabTutorialEnvCfg``，把观测空间改回 3**，
其中包含点积、叉积的 z 分量以及前向速度。

点积（内积）用一个标量告诉我们两个向量的对齐程度。如果它们高度对齐且指向同一方向，内积
会是一个较大的正值；如果它们对齐但方向相反，则会是一个较大的负值。如果两个向量
互相垂直，内积为零。这意味着前向向量与指令向量的内积可以告诉我们
自己正对指令朝向多少、背对指令朝向多少，但无法告诉我们该往哪个方向转才能改善对齐。

叉积同样能告诉我们两个向量的对齐程度，但它以向量的形式表达这种关系。任意两个
向量的叉积定义了一个垂直于这两个参数向量所在平面的轴，结果向量沿该轴的方向
由坐标系的定向性（dimension ordering，即手性/handedness）决定。在我们的例子中，可以利用我们是在
2D 中操作这一点，只考察 :math:`\vec{forward} \times \vec{command}` 结果的 z 分量。当两个向量共线时该分量为零，
指令向量在前向向量左侧时为正，右侧时为负。

最后，质心线速度的 x 分量告诉我们前向速度，正值表示向前，负值表示向后。我们把这三者
"水平"（沿 dim 1）堆叠在一起，为每台 Jetbot 生成观测。仅这一点就能提升性能！


.. figure:: https://download.isaacsim.omniverse.nvidia.com/isaaclab/images/walkthrough_improved_webp.webp
    :align: center
    :figwidth: 100%
    :alt: Improved results

从定性上看训练效果更好了，Jetbot 也在一点点向前挪动……我们肯定还能做得更好！

训练的另一条经验法则是尽可能缩减和简化奖励函数。奖励中的各项的行为类似于
逻辑 "OR" 运算。在本例中，我们通过把 "向前行驶" 和 "与指令对齐" 相加来同时奖励它们，因此智能体
只要向前行驶 **或** 与指令对齐就能获得奖励。要迫使智能体学会朝指令方向行驶，我们应该只在智能体
向前行驶 **且** 与指令对齐时给予奖励。逻辑 AND 意味着乘法，因此得到如下奖励函数：

.. code-block:: python

    def _get_rewards(self) -> torch.Tensor:
        forward_reward = self.robot.data.root_com_lin_vel_b[:,0].reshape(-1,1)
        alignment_reward = torch.sum(self.forwards * self.commands, dim=-1, keepdim=True)
        total_reward = forward_reward*alignment_reward
        return total_reward

现在，只有当对齐奖励非零时，我们才会因向前行驶而获得奖励。让我们看看这样会产生什么结果！

.. figure:: https://download.isaacsim.omniverse.nvidia.com/isaaclab/images/walkthrough_tuned_webp.webp
    :align: center
    :figwidth: 100%
    :alt: Tuned results

训练速度确实变快了，但 Jetbot 学会了当指令在身后时倒着行驶。在我们的场景中这或许可以接受，
但它表明策略行为对奖励函数的依赖有多强。在本例中，我们的奖励函数存在 **退化解（degenerate solutions）**：
奖励在前向行驶且与指令对齐时达到最大，但如果 Jetbot 倒着行驶，前向项为负，
而如果它倒着朝指令行驶，对齐项 **同样为负**，这意味着乘积为正！
当你设计自己的环境时，会遇到这样的退化解，而大量的奖励工程正是致力于通过修改奖励函数
来抑制或鼓励这些行为。

假设在我们的场景中不想要这种行为。本例中对齐项的取值域是 ``[-1, 1]``，但我们更希望它只被
映射到正值。我们并不想 *消除* 对齐项的符号，而是希望较大的负值接近于零，
这样当未对齐时我们就不会获得奖励。指数函数正好可以做到这一点！

.. code-block:: python

    def _get_rewards(self) -> torch.Tensor:
        forward_reward = self.robot.data.root_com_lin_vel_b[:,0].reshape(-1,1)
        alignment_reward = torch.sum(self.forwards * self.commands, dim=-1, keepdim=True)
        total_reward = forward_reward*torch.exp(alignment_reward)
        return total_reward

现在训练时，Jetbot 会转向并始终朝指令方向正向行驶！

.. figure:: https://download.isaacsim.omniverse.nvidia.com/isaaclab/images/walkthrough_directed_webp.webp
    :align: center
    :figwidth: 100%
    :alt: Directed results
