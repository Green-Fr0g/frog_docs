.. _how-to-env-wrappers:


包装环境
=====================

.. currentmodule:: isaaclab

环境包装器（wrapper）是一种在不修改环境本身的情况下修改环境行为的方法。
它可以用来应用函数以修改观测或奖励、录制视频、强制时间限制等。
API 的详细说明参见 :class:`gymnasium.Wrapper` 类。

目前，所有继承自 :class:`~envs.ManagerBasedRLEnv` 或 :class:`~envs.DirectRLEnv` 类的
RL 环境都与 :class:`gymnasium.Wrapper` 兼容，因为基类实现了 :class:`gymnasium.Env` 接口。
要包装一个环境，您需要先初始化基础环境。之后，您可以通过反复调用
``env = wrapper(env, *args, **kwargs)`` 来为它套上任意数量的包装器。

例如，下面是如何包装一个环境，以强制要求在 step 或 render 之前必须先调用 reset：

.. code-block:: python

    """Launch Isaac Sim Simulator first."""


    from isaaclab.app import AppLauncher

    # launch omniverse app in headless mode
    app_launcher = AppLauncher(headless=True)
    simulation_app = app_launcher.app

    """Rest everything follows."""

    import gymnasium as gym

    import isaaclab_tasks  # noqa: F401
    from isaaclab_tasks.utils import load_cfg_from_registry

    # create base environment
    cfg = load_cfg_from_registry("Isaac-Reach-Franka-v0", "env_cfg_entry_point")
    env = gym.make("Isaac-Reach-Franka-v0", cfg=cfg)
    # wrap environment to enforce that reset is called before step
    env = gym.wrappers.OrderEnforcing(env)


用于录制视频的包装器
----------------------------

:class:`gymnasium.wrappers.RecordVideo` 包装器可用于录制环境的视频。
该包装器接受一个 ``video_dir`` 参数，用于指定视频的保存位置。视频以
`mp4 <https://en.wikipedia.org/wiki/MP4_file_format>`__ 格式按指定的间隔保存，
持续指定数量的环境步数或回合。

要使用该包装器，需要先安装 ``ffmpeg`` 。在 Ubuntu 上，可以通过运行以下命令安装：

.. code-block:: bash

    sudo apt-get install ffmpeg

.. attention::

  默认情况下，在无头（headless）模式下运行环境时，Omniverse viewport 是禁用的。这样做是为了
  避免不必要的渲染，从而提升性能。

  我们在使用 RTX 3090 GPU、以 ``Isaac-Reach-Franka-v0`` 环境测试时，观察到不同渲染模式下的
  以下性能表现：

  * 无 GUI 且未启用离屏渲染：约 65,000 FPS
  * 无 GUI 且启用离屏渲染：约 57,000 FPS
  * 带完整渲染的 GUI 执行：约 13,000 FPS


用于渲染的 viewport 相机是场景中名为 ``"/OmniverseKit_Persp"`` 的默认相机。
该相机的位姿和图像分辨率可以通过
:class:`~envs.ViewerCfg` 类进行配置。


.. dropdown:: ViewerCfg 类的默认参数：
    :icon: code

    .. literalinclude:: ../../../source/isaaclab/isaaclab/envs/common.py
        :language: python
        :pyobject: ViewerCfg


调整参数后，您可以通过使用 :class:`gymnasium.wrappers.RecordVideo` 包装器包装环境
并启用离屏渲染标志来录制视频。此外，您需要将环境的渲染模式指定为 ``"rgb_array"`` 。

例如，以下代码录制 ``Isaac-Reach-Franka-v0`` 环境 200 步的视频，
并以 1500 步为间隔将其保存到 ``videos`` 文件夹中。

.. code:: python

    """Launch Isaac Sim Simulator first."""


    from isaaclab.app import AppLauncher

    # launch omniverse app in headless mode with off-screen rendering
    app_launcher = AppLauncher(headless=True, enable_cameras=True)
    simulation_app = app_launcher.app

    """Rest everything follows."""

    import gymnasium as gym

    # adjust camera resolution and pose
    env_cfg.viewer.resolution = (640, 480)
    env_cfg.viewer.eye = (1.0, 1.0, 1.0)
    env_cfg.viewer.lookat = (0.0, 0.0, 0.0)
    # create isaac-env instance
    # set render mode to rgb_array to obtain images on render calls
    env = gym.make(task_name, cfg=env_cfg, render_mode="rgb_array")
    # wrap for video recording
    video_kwargs = {
        "video_folder": "videos/train",
        "step_trigger": lambda step: step % 1500 == 0,
        "video_length": 200,
    }
    env = gym.wrappers.RecordVideo(env, **video_kwargs)


用于学习框架的包装器
-------------------------------

每个学习框架都有自己的与环境交互的 API。例如，
`Stable-Baselines3`_ 库使用 `gym.Env <https://gymnasium.farama.org/api/env/>`_
接口与环境交互。然而，像 `RL-Games`_ 、 `RSL-RL`_ 或 `SKRL`_
这样的库则使用自己的 API 来对接学习环境。由于没有放之四海而皆准的方案，
我们不将 :class:`~envs.ManagerBasedRLEnv` 和 :class:`~envs.DirectRLEnv` 类建立在任何特定学习框架的
环境定义之上。相反，我们实现包装器，使其与学习框架的环境定义兼容。

以下是如何在 Stable-Baselines3 中使用 RL 任务环境的示例：

.. code:: python

    from isaaclab_rl.sb3 import Sb3VecEnvWrapper

    # create isaac-env instance
    env = gym.make(task_name, cfg=env_cfg)
    # wrap around environment for stable baselines
    env = Sb3VecEnvWrapper(env)


.. caution::

  使用相应学习框架的包装器包装环境应当放在最后进行，
  即在应用所有其他包装器之后。这是因为学习框架的包装器
  会修改环境 API 的解释方式，可能不再与 :class:`gymnasium.Env` 兼容。


添加新包装器
-------------------

所有新的包装器都应添加到 :mod:`isaaclab_rl` 模块中。
在应用包装器之前，它们应检查底层环境是否是 :class:`isaaclab.envs.ManagerBasedRLEnv`
或 :class:`~envs.DirectRLEnv` 的实例。
这可以通过使用 :func:`unwrapped` 属性来实现。

我们在该模块中提供了一组包装器，可作为实现您自己包装器的参考。
如果您实现了新的包装器，请考虑通过提交 pull request 将其贡献给框架。

.. _Stable-Baselines3: https://stable-baselines3.readthedocs.io/en/master/
.. _SKRL: https://skrl.readthedocs.io
.. _RL-Games: https://github.com/Denys88/rl_games
.. _RSL-RL: https://github.com/leggedrobotics/rsl_rl
