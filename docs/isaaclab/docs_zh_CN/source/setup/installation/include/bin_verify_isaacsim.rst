检查仿真器是否按预期运行：

.. tab-set::
    :sync-group: os

    .. tab-item:: :icon:`fa-brands fa-linux` Linux
        :sync: linux

        .. code:: bash

            # note: you can pass the argument "--help" to see all arguments possible.
            ${ISAACSIM_PATH}/isaac-sim.sh


    .. tab-item:: :icon:`fa-brands fa-windows` Windows
        :sync: windows

        .. code:: batch

            :: note: you can pass the argument "--help" to see all arguments possible.
            %ISAACSIM_PATH%\isaac-sim.bat


检查是否可以从独立的 Python 脚本运行仿真器：

.. tab-set::
    :sync-group: os

    .. tab-item:: :icon:`fa-brands fa-linux` Linux
        :sync: linux

        .. code:: bash

            # checks that python path is set correctly
            ${ISAACSIM_PYTHON_EXE} -c "print('Isaac Sim configuration is now complete.')"
            # checks that Isaac Sim can be launched from python
            ${ISAACSIM_PYTHON_EXE} ${ISAACSIM_PATH}/standalone_examples/api/isaacsim.core.api/add_cubes.py

    .. tab-item:: :icon:`fa-brands fa-windows` Windows
        :sync: windows

        .. code:: batch

            :: checks that python path is set correctly
            %ISAACSIM_PYTHON_EXE% -c "print('Isaac Sim configuration is now complete.')"
            :: checks that Isaac Sim can be launched from python
            %ISAACSIM_PYTHON_EXE% %ISAACSIM_PATH%\standalone_examples\api\isaacsim.core.api\add_cubes.py

.. caution::

   如果你之前一直在使用较早版本的 Isaac Sim，则需要在安装后 *首次* 运行时执行以下命令，
   以清除所有旧的用户数据和缓存的变量：

   .. tab-set::

      .. tab-item:: :icon:`fa-brands fa-linux` Linux

      	.. code:: bash

      		${ISAACSIM_PATH}/isaac-sim.sh --reset-user

      .. tab-item:: :icon:`fa-brands fa-windows` Windows

         .. code:: batch

            %ISAACSIM_PATH%\isaac-sim.bat --reset-user


如果按照上述步骤操作后仿真器无法运行或发生崩溃，说明某些配置不正确。
要进行调试和故障排除，请查阅 Isaac Sim
`documentation <https://docs.omniverse.nvidia.com/dev-guide/latest/linux-troubleshooting.html>`__
以及
`Isaac Sim Forums <https://docs.isaacsim.omniverse.nvidia.com/latest/common/feedback.html>`_。
