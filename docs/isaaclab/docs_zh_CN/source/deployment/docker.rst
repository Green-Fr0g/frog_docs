.. _deployment-docker:


Docker 指南
============

.. caution::

    由于依赖 Isaac Sim docker 镜像，运行此容器即表示你已默示同意
    `NVIDIA Software License Agreement`_ 。如果你不同意该 EULA，请勿运行此容器。

设置说明
------------------

.. note::

    以下步骤取自 Isaac Sim 文档中关于 `container installation`_ 的内容。
    为完整起见，我们在此将其收录。


Docker 与 Docker Compose
~~~~~~~~~~~~~~~~~~~~~~~~~

我们已使用 Docker Engine 26.0.0 版本和 Docker Compose 2.25.0 版本对该容器进行了测试。
我们建议使用这些版本或更高版本。

* 要安装 Docker，请按照 `Docker website`_ 上适用于你的操作系统的说明进行操作。
* 要安装 Docker Compose，请按照 `docker compose`_ 页面上适用于你的操作系统的说明进行操作。
* 按照 `post-installation steps`_ 页面中的 Docker 安装后步骤进行操作。这些步骤使你能够在
  不使用 ``sudo`` 的情况下运行 Docker。
* 要构建和运行 GPU 加速的容器，你还需要安装 `NVIDIA Container Toolkit`_ 。
  请按照 `Container Toolkit website`_ 上的说明执行安装步骤。

.. note::

    由于 `snap <https://snapcraft.io/docs/home-outside-home>`_ 的限制，使用 docker 时请确保
    将 Isaac Lab 目录放置在 ``/home`` 目录树之下。


目录结构
----------------------

Isaac Lab 仓库的根目录包含 ``docker`` 目录，其中包含在 Docker 容器中运行 Isaac Lab 所需的
各种文件和脚本。下面总结了其中的一部分：

* **Dockerfile.base** ：通过将 Isaac Lab 的依赖叠加到 Isaac Sim Docker 镜像之上来定义基础的
  Isaac Lab 镜像。以其他内容结尾的 Dockerfile（即 ``Dockerfile.ros2`` ）则会构建
  `image extension <#isaac-lab-image-extensions>`_ 。
* **docker-compose.yaml** ：创建挂载，使得可以从运行容器的宿主机直接编辑 Isaac Lab 代码。
  它还会创建多个命名卷（例如 ``isaac-cache-kit`` ）来存储由 Isaac Sim 编译的经常复用的资源
  （如着色器），并保留日志、数据和文档。
* **.env.base** ：存储 ``base`` 构建过程和容器本身所需的环境变量。以其他内容结尾的 ``.env``
  文件（即 ``.env.ros2`` ）则为 `image extension <#isaac-lab-image-extensions>`_ 定义这些变量。
* **docker-compose.cloudxr-runtime.patch.yaml** ：一个补丁文件，应用后可启用 CloudXR Runtime
  支持，以便串流到兼容的 XR 设备。它为 CloudXR Runtime 和 base 定义了服务和卷。
* **.env.cloudxr-runtime** ：用于 CloudXR Runtime 支持的环境变量。
* **container.py** ：一个实用脚本，它与 ``utils`` 中的工具交互，用于配置和构建镜像，
  以及运行容器并与之交互。

运行容器
---------------------

.. note::

    docker 容器会在构建时将仓库中的所有文件复制到容器内的 ``/workspace/isaaclab`` 位置。
    这意味着在镜像构建完成（即 ``./container.py start`` 运行之后）后，在容器内对文件所做的
    更改通常不会反映到仓库中。

    为了加快开发周期，我们将 Isaac Lab 仓库中的以下目录挂载到容器中，以便你可以从宿主机
    编辑其中的文件：

    * **IsaacLab/source** ：该目录包含 Isaac Lab 的源代码。
    * **IsaacLab/docs** ：该目录包含 Isaac Lab 文档的源代码。除存储构建产物的 ``_build``
      子目录外，该目录均会以叠加方式挂载。


脚本 ``container.py`` 与基本的 ``docker compose`` 命令相对应。每个命令都可以接受一个
`image extension argument <#isaac-lab-image-extensions>`_ 参数，否则将默认使用 ``base``
镜像扩展。这些命令包括：

* **build** ：为给定的 profile 构建镜像。它不会启动容器。
* **start** ：构建镜像并以分离模式（即在后台）启动容器。
* **enter** ：在已有的 Isaac Lab 容器中启动一个新的 bash 进程，退出时不会关闭容器。
* **config** ：输出根据提供给 ``container.py start`` 的输入所生成的 compose.yaml。该命令
  对于调试 compose 配置非常有用。
* **copy** ：将 ``logs`` 、 ``data_storage`` 和 ``docs/_build`` 产物分别从 ``isaac-lab-logs`` 、
  ``isaac-lab-data`` 和 ``isaac-lab-docs`` 卷复制到 ``docker/artifacts`` 目录。这些产物在
  docker 容器实例之间持久保存，并在各镜像扩展之间共享。
* **stop** ：停止并移除容器。

下面演示如何以分离状态启动容器并进入其中：

.. code:: bash

    # Launch the container in detached mode
    # We don't pass an image extension arg, so it defaults to 'base'
    ./docker/container.py start

    # If we want to add .env or .yaml files to customize our compose config,
    # we can simply specify them in the same manner as the compose cli
    # ./docker/container.py start --file my-compose.yaml --env-file .env.my-vars

    # Enter the container
    # We pass 'base' explicitly, but if we hadn't it would default to 'base'
    ./docker/container.py enter base

要将文件从 base 容器复制到宿主机，可以使用以下命令：

.. code:: bash

    # Copy the file /workspace/isaaclab/logs to the current directory
    docker cp isaac-lab-base:/workspace/isaaclab/logs .

脚本 ``container.py`` 为该命令提供了一个封装，用于将 ``logs`` 、 ``data_storage`` 和
``docs/_build`` 目录复制到 ``docker/artifacts`` 目录。这对于复制日志、数据和文档非常有用：

.. code:: bash

    # stop the container
    ./docker/container.py stop


CloudXR Runtime 支持
~~~~~~~~~~~~~~~~~~~~~~~

要启用 CloudXR Runtime 以串流到兼容的 XR 设备，你需要应用补丁文件
``docker-compose.cloudxr-runtime.patch.yaml`` 来运行 CloudXR Runtime 容器。该补丁文件为
CloudXR Runtime 和 base 定义了服务和卷。CloudXR Runtime 所需的环境变量在
``.env.cloudxr-runtime`` 文件中指定。要随 base 一起启动或停止 CloudXR Runtime 容器，
请使用以下命令：

.. code:: bash

    # Start CloudXR Runtime container with base.
    ./docker/container.py start --files docker-compose.cloudxr-runtime.patch.yaml --env-file .env.cloudxr-runtime

    # Stop CloudXR Runtime container and base.
    ./docker/container.py stop --files docker-compose.cloudxr-runtime.patch.yaml --env-file .env.cloudxr-runtime


X11 转发
~~~~~~~~~~~~~~

容器支持 X11 转发，允许用户从容器中运行 GUI 应用程序并将其显示在宿主机上。

第一次使用 ``./docker/container.py start`` 启动容器时，脚本会询问用户是否激活 X11 转发。
这将在 ``docker/.container.cfg`` 处创建一个文件，用于存储用户的选择以供以后运行时使用。

如果想更改该选择，可以在 ``docker/.container.cfg`` 文件中将参数 ``X11_FORWARDING_ENABLED``
设置为 '0' 或 '1'，分别对应禁用或启用 X11 转发。此后，你需要通过运行
``./docker/container.py start`` 重新构建容器。重新构建过程可确保更改被应用到容器中，
否则这些更改不会生效。

容器启动后，你可以进入容器并在启用 X11 转发的情况下从中运行 GUI 应用程序。
显示内容将被转发到宿主机。


Python 解释器
~~~~~~~~~~~~~~~~~~

容器使用 Isaac Sim 提供的 Python 解释器。该解释器位于 ``/isaac-sim/python.sh`` 。
我们在容器内部设置了别名，以便更轻松地运行 Python 解释器。你可以使用以下命令运行
Python 解释器：

.. code:: bash

    # Run the Python interpreter -> points to /isaac-sim/python.sh
    python


理解挂载的卷
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``docker-compose.yaml`` 文件创建了多个挂载到容器中的命名卷。这些卷总结如下：

.. list-table::
   :header-rows: 1
   :widths: 23 45 32

   * - Volume Name
     - Description
     - Container Path
   * - isaac-cache-kit
     - 存储缓存的 Kit 资源
     - /isaac-sim/kit/cache
   * - isaac-cache-ov
     - 存储缓存的 OV 资源
     - /root/.cache/ov
   * - isaac-cache-pip
     - 存储缓存的 pip 资源
     - /root/.cache/pip
   * - isaac-cache-gl
     - 存储缓存的 GLCache 资源
     - /root/.cache/nvidia/GLCache
   * - isaac-cache-compute
     - 存储缓存的计算资源
     - /root/.nv/ComputeCache
   * - isaac-logs
     - 存储由 Omniverse 生成的日志
     - /root/.nvidia-omniverse/logs
   * - isaac-carb-logs
     - 存储由 carb 生成的日志
     - /isaac-sim/kit/logs/Kit/Isaac-Sim
   * - isaac-data
     - 存储由 Omniverse 生成的数据
     - /root/.local/share/ov/data
   * - isaac-docs
     - 存储由 Omniverse 生成的文档
     - /root/Documents
   * - isaac-lab-docs
     - 存储在容器内构建的 Isaac Lab 文档
     - /workspace/isaaclab/docs/_build
   * - isaac-lab-logs
     - 存储在容器内运行 Isaac Lab 工作流时生成的日志
     - /workspace/isaaclab/logs
   * - isaac-lab-data
     - 存储用户希望在多次容器运行之间保留的任何数据
     - /workspace/isaaclab/data_storage

要查看这些卷的内容，可以使用以下命令：

.. code:: bash

    # list all volumes
    docker volume ls
    # inspect a specific volume, e.g. isaac-cache-kit
    docker volume inspect isaac-cache-kit



Isaac Lab 镜像扩展
--------------------------

生成的镜像取决于传递给 ``container.py start`` 和 ``container.py stop`` 的参数。这些命令
可以接受一个镜像扩展参数作为附加参数。如果未传递任何参数，则该参数默认为 ``base`` 。
目前，唯一有效的取值是（ ``base`` 、 ``ros2`` ）。
一次只能传递一个镜像扩展。生成的镜像和容器将被命名为
``isaac-lab-${profile}`` ，其中 ``${profile}`` 为镜像扩展名称。

``suffix`` 是 ``container.py`` 的一个可选字符串参数，用于指定 docker 镜像和容器名称的
后缀，这在开发时可能很有用。默认情况下 ``${suffix}`` 为空字符串。
如果 ``${suffix}`` 是非空字符串，则生成的 docker 镜像和容器将被命名为
``isaac-lab-${profile}-${suffix}`` ，即名称中会在 ``${profile}`` 和 ``${suffix}`` 之间
插入一个连字符。 ``suffix`` 不应与集群部署一起使用。

.. code:: bash

    # start base by default, named isaac-lab-base
    ./docker/container.py start
    # stop base explicitly, named isaac-lab-base
    ./docker/container.py stop base
    # start ros2 container named isaac-lab-ros2
    ./docker/container.py start ros2
    # stop ros2 container named isaac-lab-ros2
    ./docker/container.py stop ros2

    # start base container named isaac-lab-base-custom
    ./docker/container.py start base --suffix custom
    # stop base container named isaac-lab-base-custom
    ./docker/container.py stop base --suffix custom
    # start ros2 container named isaac-lab-ros2-custom
    ./docker/container.py start ros2 --suffix custom
    # stop ros2 container named isaac-lab-ros2-custom
    ./docker/container.py stop ros2 --suffix custom

所传递的镜像扩展参数将构建 ``Dockerfile.${image_extension}`` 中定义的镜像，并结合
``docker-compose.yaml`` 中对应的 `profile`_ 以及 ``.env.${image_extension}`` 中的环境变量
（如有），外加 ``.env.base`` 中的内容。

ROS2 镜像扩展
~~~~~~~~~~~~~~~~~~~~

在 ``Dockerfile.ros2`` 中，容器通过一个 `apt package`_ 安装 ROS2 Humble，并在 ``.bashrc``
中进行 source。确切版本由 ``.env.ros2`` 文件中的变量 ``ROS_APT_PACKAGE`` 指定，
默认为 ``ros-base`` 。其他相关的 ROS2 变量也在 ``.env.ros2`` 文件中指定，
包括定义 `various middleware`_ 选项的变量。

容器默认使用 ``FastRTPS`` ，但也支持 ``CylconeDDS`` 。这些中间件都可以使用 ``docker/.ros``
下相应的 ``.xml`` 文件进行 `tuned`_ 。


.. dropdown:: ROS2 镜像扩展的参数
   :icon: code

   .. literalinclude:: ../../../docker/.env.ros2
      :language: bash


运行预构建的 Isaac Lab 容器
-------------------------------------

在 Isaac Lab 2.0 版本中，我们引入了一个精简的预构建容器，它只包含非常精简的一组
Isaac Sim 和 Omniverse 依赖，并将 Isaac Lab 2.0 预构建到容器中。
该容器允许用户直接从 NGC 拉取容器，而无需在本地构建 docker 镜像。
Isaac Lab 源代码将位于该容器中的 ``/workspace/IsaacLab`` 下。

该容器仅设计用于 **headless** 模式运行，不支持 X11 转发或以 GUI 方式运行。
请仅将该容器用于无头训练。对于其他用例，我们建议按照上述步骤构建你自己的
Isaac Lab docker 镜像。

.. note::

  目前，我们仅在 Isaac Lab 的每个主版本发布时提供 docker 镜像。
  例如，我们提供 2.0.0 和 2.1.0 版本的 docker 镜像，但不提供 2.0.2 版本。
  未来，我们将为 Isaac Lab 的每个次要版本提供 docker 镜像。

要拉取精简版 Isaac Lab 容器，请运行：

.. code:: bash

  docker pull nvcr.io/nvidia/isaac-lab:2.3.2

要以交互式 bash 会话运行 Isaac Lab 容器，请运行：

.. code:: bash

  docker run --name isaac-lab --entrypoint bash -it --gpus all -e "ACCEPT_EULA=Y" --rm --network=host \
     -e "PRIVACY_CONSENT=Y" \
     -v ~/docker/isaac-sim/cache/kit:/isaac-sim/kit/cache:rw \
     -v ~/docker/isaac-sim/cache/ov:/root/.cache/ov:rw \
     -v ~/docker/isaac-sim/cache/pip:/root/.cache/pip:rw \
     -v ~/docker/isaac-sim/cache/glcache:/root/.cache/nvidia/GLCache:rw \
     -v ~/docker/isaac-sim/cache/computecache:/root/.nv/ComputeCache:rw \
     -v ~/docker/isaac-sim/logs:/root/.nvidia-omniverse/logs:rw \
     -v ~/docker/isaac-sim/data:/root/.local/share/ov/data:rw \
     -v ~/docker/isaac-sim/documents:/root/Documents:rw \
     nvcr.io/nvidia/isaac-lab:2.3.2

要通过 X11 转发启用渲染，请运行：

.. code:: bash

  xhost +
  docker run --name isaac-lab --entrypoint bash -it --gpus all -e "ACCEPT_EULA=Y" --rm --network=host \
     -e "PRIVACY_CONSENT=Y" \
     -e DISPLAY \
     -v $HOME/.Xauthority:/root/.Xauthority \
     -v ~/docker/isaac-sim/cache/kit:/isaac-sim/kit/cache:rw \
     -v ~/docker/isaac-sim/cache/ov:/root/.cache/ov:rw \
     -v ~/docker/isaac-sim/cache/pip:/root/.cache/pip:rw \
     -v ~/docker/isaac-sim/cache/glcache:/root/.cache/nvidia/GLCache:rw \
     -v ~/docker/isaac-sim/cache/computecache:/root/.nv/ComputeCache:rw \
     -v ~/docker/isaac-sim/logs:/root/.nvidia-omniverse/logs:rw \
     -v ~/docker/isaac-sim/data:/root/.local/share/ov/data:rw \
     -v ~/docker/isaac-sim/documents:/root/Documents:rw \
     nvcr.io/nvidia/isaac-lab:2.3.2

要在容器内运行示例，请运行：

.. code:: bash

  ./isaaclab.sh -p scripts/tutorials/00_sim/log_time.py --headless


.. _`NVIDIA Software License Agreement`: https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-software-license-agreement
.. _`container installation`: https://docs.isaacsim.omniverse.nvidia.com/latest/installation/install_container.html
.. _`Docker website`: https://docs.docker.com/desktop/install/linux-install/
.. _`docker compose`: https://docs.docker.com/compose/install/linux/#install-using-the-repository
.. _`NVIDIA Container Toolkit`: https://github.com/NVIDIA/nvidia-container-toolkit
.. _`Container Toolkit website`: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
.. _`post-installation steps`: https://docs.docker.com/engine/install/linux-postinstall/
.. _`Isaac Sim container`: https://catalog.ngc.nvidia.com/orgs/nvidia/containers/isaac-sim
.. _`NGC API key`: https://docs.nvidia.com/ngc/gpu-cloud/ngc-user-guide/index.html#generating-api-key
.. _`several streaming clients`: https://docs.isaacsim.omniverse.nvidia.com/latest/installation/manual_livestream_clients.html
.. _`known issue`: https://forums.developer.nvidia.com/t/unable-to-use-webrtc-when-i-run-runheadless-webrtc-sh-in-remote-headless-container/222916
.. _`profile`: https://docs.docker.com/compose/compose-file/15-profiles/
.. _`apt package`: https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html#install-ros-2-packages
.. _`various middleware`: https://docs.ros.org/en/humble/How-To-Guides/Working-with-multiple-RMW-implementations.html
.. _`tuned`: https://docs.ros.org/en/foxy/How-To-Guides/DDS-tuning.html
