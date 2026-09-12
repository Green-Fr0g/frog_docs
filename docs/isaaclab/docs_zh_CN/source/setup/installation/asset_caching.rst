资产缓存
=============

Isaac Lab 使用的资产托管在云端的 AWS S3 存储桶中。
资产的加载时间可能取决于你的网络连接和地理位置。
在某些情况下，从 AWS 服务器拉取资产时，加载时间可能会很长。

如果你遇到每次运行时资产都需要几分钟才能加载的情况，
我们建议按照以下步骤启用资产缓存。

首先，启动 Isaac Sim 应用：

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code:: bash

         ./isaaclab.sh -s

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code:: batch

         isaaclab.bat -s

在 Isaac Lab 或 Isaac Sim 应用的右上角，找到标记为 ``CACHE:`` 的图标。
你可能会看到诸如 ``HUB NOT DETECTED`` 或 ``NEW VERSION DETECTED`` 的消息。

点击该消息以启用 `Hub <https://docs.omniverse.nvidia.com/utilities/latest/cache/hub-workstation.html>`_。
Hub 会自动管理 Isaac Lab 资产的本地缓存，因此后续运行将使用缓存的文件，
而无需每次都从 AWS 下载。

.. figure:: /source/_static/setup/asset_caching.jpg
    :align: center
    :figwidth: 100%
    :alt: Simulator with cache messaging.

Hub 提供了对缓存资产更好的控制和管理，使工作流更快、更可靠，
尤其是在网络受限或连接不稳定的环境中。

.. note::
   第一次运行 Isaac Lab 时，资产仍需要从云端拉取，这可能导致加载时间较长。
   一旦缓存完成，后续运行的加载时间将显著缩短。

Nucleus
-------


在 Isaac Sim 4.5 之前，资产是通过 Omniverse Nucleus 服务器访问的，包括配置了本地 Nucleus 实例的情况。

.. warning::
   从 Isaac Sim 4.5 开始，Omniverse Nucleus 服务器和 Omniverse Launcher 已被弃用。
   现有的 Nucleus 配置仍可继续工作，因此如果你已经配置了本地 Nucleus 服务器，
   可以继续使用它。
