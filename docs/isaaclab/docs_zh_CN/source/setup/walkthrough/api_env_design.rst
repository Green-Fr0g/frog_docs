.. _walkthrough_api_env_design:

类与配置
====================================

首先，进入任务目录：``source/isaac_lab_tutorial/isaac_lab_tutorial/tasks/direct/isaac_lab_tutorial``，
查看 ``isaac_lab_tutorial_env_cfg.py`` 的内容。你应该会看到类似下面的内容

.. code-block:: python

  from isaaclab_assets.robots.cartpole import CARTPOLE_CFG

  from isaaclab.assets import ArticulationCfg
  from isaaclab.envs import DirectRLEnvCfg
  from isaaclab.scene import InteractiveSceneCfg
  from isaaclab.sim import SimulationCfg
  from isaaclab.utils import configclass


  @configclass
  class IsaacLabTutorialEnvCfg(DirectRLEnvCfg):

      # Some useful fields
      .
      .
      .

      # simulation
      sim: SimulationCfg = SimulationCfg(dt=1 / 120, render_interval=2)

      # robot(s)
      robot_cfg: ArticulationCfg = CARTPOLE_CFG.replace(prim_path="/World/envs/env_.*/Robot")

      # scene
      scene: InteractiveSceneCfg = InteractiveSceneCfg(num_envs=4096, env_spacing=4.0, replicate_physics=True)

      # Some more useful fields
      .
      .
      .

这是模板自带的一个简单 cartpole 环境的默认配置，它定义了你在对应环境中做任何操作时的 ``self`` 作用域。

.. currentmodule:: isaaclab.envs

首先要注意的是 ``@configclass`` 装饰器。它将一个类定义为配置类，而配置类在 Isaac Lab 中占有特殊地位。
在克隆环境以扩大训练规模时，Isaac Lab 需要判断要 "关心" 哪些内容，配置类正是其中的一部分。
Isaac Lab 会根据你的目标提供不同的基础配置类，在本例中我们使用 :class:`DirectRLEnvCfg` 类，
因为我们感兴趣的是以直接式工作流进行强化学习。

.. currentmodule:: isaaclab.sim

第二件要注意的是配置类的内容。作为作者，你可以指定任何你想要的字段，但一般来说，
你在这里总是会定义三样东西：**sim** （仿真）、**scene** （场景）和 **robot** （机器人）。
注意这些字段本身也是配置类！配置类通过这种组合方式，成为克隆任意复杂环境的解决方案。

**sim** 是 :class:`SimulationCfg` 的一个实例，它是控制我们所构建的仿真现实之性质的配置。
该字段是基类 ``DirecRLEnvCfg`` 的成员，并且有默认的仿真配置，因此 *严格来说* 是可选的。``SimulationCfg``
规定了时间步进的精细程度（dt）、重力的方向，甚至物理应如何仿真。在本例中我们只指定了时间步长和渲染间隔，
前者表示每个时间步长应仿真 1/120 秒（:math:`1/120` 秒），后者表示渲染一帧之前应执行多少个步长（值为 2 表示
每隔一帧渲染一次）。

.. currentmodule:: isaaclab.scene

**scene** 是 :class:`InteractiveSceneCfg` 的一个实例。场景描述了什么会被放到 "Stage 上"，
并管理那些需要跨环境克隆的仿真实体。场景同样是基类 ``DirectRLEnvCfg`` 的成员，
但与 sim 不同的是它没有默认值，必须在每个 ``DirectRLEnvCfg`` 中定义。``InteractiveSceneCfg``
描述了出于训练目的我们想创建多少个场景副本，以及它们在 Stage 上应该间隔多远。

.. currentmodule:: isaaclab.assets

最后是 **robot** （机器人）定义，它是 :class:`ArticulationCfg` 的一个实例。一个环境可以包含多个关节体（articulation），
因此要定义一个 ``DirectRLEnv`` 并不严格要求存在 ``ArticulationCfg``。通常的工作流是定义一个指向机器人的
正则表达式路径，并替换基础配置中的 ``prim_path`` 属性。在本例中，``CARTPOLE_CFG`` 是在
``isaaclab_assets.robots.cartpole`` 中定义的配置，通过把 prim 路径替换为 ``/World/envs/env_.*/Robot``，
我们隐式地声明了场景的每个副本都将有一个名为 ``Robot`` 的机器人。


环境
-----------------

接下来，让我们看看任务目录中另一个 Python 文件的内容：``isaac_lab_tutorial_env.py``

.. code-block:: python

  # imports
  .
  .
  .
  from .isaac_lab_tutorial_env_cfg import IsaacLabTutorialEnvCfg

  class IsaacLabTutorialEnv(DirectRLEnv):
      cfg: IsaacLabTutorialEnvCfg

      def __init__(self, cfg: IsaacLabTutorialEnvCfg, render_mode: str | None = None, **kwargs):
          super().__init__(cfg, render_mode, **kwargs)
          . . .

      def _setup_scene(self):
          self.robot = Articulation(self.cfg.robot_cfg)
          # add ground plane
          spawn_ground_plane(prim_path="/World/ground", cfg=GroundPlaneCfg())
          # add articulation to scene
          self.scene.articulations["robot"] = self.robot
          # clone and replicate
          self.scene.clone_environments(copy_from_source=False)
          # add lights
          light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
          light_cfg.func("/World/Light", light_cfg)

      def _pre_physics_step(self, actions: torch.Tensor) -> None:
          . . .

      def _apply_action(self) -> None:
          . . .

      def _get_observations(self) -> dict:
          . . .

      def _get_rewards(self) -> torch.Tensor:
          total_reward = compute_rewards(...)
          return total_reward

      def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
          . . .

      def _reset_idx(self, env_ids: Sequence[int] | None):
          . . .

  @torch.jit.script
  def compute_rewards(...):
      . . .
      return total_reward


.. currentmodule:: isaaclab.envs

为了便于讨论，部分代码被省略了。这里才是直接式工作流真正的 "核心" 所在，
也是我们在调整模板以满足自身需求时进行大部分修改的地方。
目前，``IsaacLabTutorialEnv`` 的所有成员函数都直接继承自 :class:`DirectRLEnv`。
这一已知接口正是 Isaac Lab 及其支持的 RL 框架与环境交互的方式。

环境初始化时，会接收到自己的配置作为参数，随后立即传递给超类以初始化
``DirectRLEnv``。这个超类调用还会调用 ``_setup_scene``，由它真正构建场景并进行恰当的克隆。
值得注意的是机器人在 ``_setup_scene`` 中被创建并注册到场景的方式。首先，机器人关节体
是使用我们在 ``IsaacLabTutorialEnvCfg`` 中定义的 ``robot_config`` 创建的：在此之前它并不存在！
当关节体被创建后，机器人便存在于 Stage 上的 ``/World/envs/env_0/Robot`` 处。随后对
``scene.clone_environments`` 的调用会恰当地复制 ``env_0``。此时机器人以许多副本的形式
存在于 Stage 上，剩下的工作就是通知 ``scene`` 对象跟踪这个关节体的存在。场景的关节体保存在一个字典中，
因此 ``scene.articulations["robot"] = self.robot`` 会在 ``articulations`` 字典中创建一个新的
``robot`` 条目，并将其值设置为 ``self.robot``。

还要注意，除 ``_reset_idx`` 之外，其余函数都不接受额外的参数。这是因为环境只负责把
动作施加到被仿真的智能体上，然后更新仿真。这正是 ``_pre_physics_step`` 和 ``_apply_action``
两个步骤的用途：我们为机器人设置驱动指令，这样当仿真向前推进时，动作就被施加，关节就被驱动到新的目标。
把这一过程拆分成这样的步骤，是为了确保对环境执行方式的系统性控制，这一点在管理器式工作流中尤为重要。
``_get_dones`` 函数与 ``_reset_idx`` 之间也存在类似的关系。前者 ``_get_dones`` 判断每个环境
是否处于终止状态，并填充布尔值张量，以指示哪些环境因进入终止状态而终止、哪些因超时而终止
（即该函数返回的两个张量）。后者 ``_reset_idx`` 接收一个环境索引值（整数）列表，然后真正重置
那些环境。重要的是，诸如更新驱动目标或重置环境之类的操作不能 **在** 物理步或渲染步 **期间** 发生，
以这种方式拆分接口有助于防止这种情况。
