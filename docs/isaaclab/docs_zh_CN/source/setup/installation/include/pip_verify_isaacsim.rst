
验证 Isaac Sim 安装
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  确保你的虚拟环境已激活（如适用）

-  检查仿真器是否按预期运行：

   .. code:: bash

      # note: you can pass the argument "--help" to see all arguments possible.
      isaacsim

-  也可以使用特定的 experience 文件运行：

   .. code:: bash

      # experience files can be absolute path, or relative path searched in isaacsim/apps or omni/apps
      isaacsim isaacsim.exp.full.kit


.. note::

   首次运行 Isaac Sim 时，所有依赖的扩展都会从注册表（registry）拉取。
   这一过程可能需要 10 分钟以上，并且每个 experience 文件首次运行时都需要执行。
   扩展拉取完成后，使用同一 experience 文件的后续运行将使用缓存的扩展。

.. attention::

   首次运行时，系统会提示用户接受 Nvidia Omniverse 许可协议。
   要接受 EULA，当出现以下消息时请回复 ``Yes``：

   .. code:: bash

      By installing or using Isaac Sim, I agree to the terms of NVIDIA OMNIVERSE LICENSE AGREEMENT (EULA)
      in https://docs.isaacsim.omniverse.nvidia.com/latest/common/NVIDIA_Omniverse_License_Agreement.html

      Do you accept the EULA? (Yes/No): Yes


如果按照上述步骤操作后仿真器无法运行或发生崩溃，说明某些配置不正确。
要进行调试和故障排除，请查阅 Isaac Sim
`documentation <https://docs.omniverse.nvidia.com/dev-guide/latest/linux-troubleshooting.html>`__
以及
`Isaac Sim Forums <https://docs.isaacsim.omniverse.nvidia.com/latest/common/feedback.html>`_。
