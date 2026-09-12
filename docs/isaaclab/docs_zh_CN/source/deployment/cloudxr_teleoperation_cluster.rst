.. _cloudxr-teleoperation-cluster:

在 Kubernetes 上部署 CloudXR 遥操作
===================================

.. currentmodule:: isaaclab

本节介绍如何在 Kubernetes（K8s）集群上为 Isaac Lab 部署 CloudXR 遥操作。

.. _k8s-system-requirements:

系统要求
--------

* **最低要求**：Kubernetes 集群中有一个节点配备至少 1 块 NVIDIA RTX PRO 6000 / L40 GPU 或同等 GPU
* **推荐要求**：Kubernetes 集群中有一个节点配备至少 2 块 RTX PRO 6000 / L40 GPU 或同等 GPU

.. note::
   如果你使用的是 DGX Spark，请查看 `DGX Spark Limitations <https://isaac-sim.github.io/IsaacLab/v2.3.2/source/setup/installation/index.html#dgx-spark-details-and-limitations>`_ 了解兼容性信息。

软件依赖
--------

* 宿主机上安装 ``kubectl``

  * 如果你使用 MicroK8s，则已经有 ``microk8s kubectl``
  * 否则请遵循 `kubectl 官方安装指南 <https://kubernetes.io/docs/tasks/tools/#kubectl>`_

* 宿主机上安装 ``helm``

  * 如果你使用 MicroK8s，则已经有 ``microk8s helm``
  * 否则请遵循 `Helm 官方安装指南 <https://helm.sh/docs/intro/install/>`_

* 你的 Kubernetes 集群能够访问 NGC 公共仓库，特别是以下容器镜像：

  * ``https://catalog.ngc.nvidia.com/orgs/nvidia/containers/isaac-lab``
  * ``https://catalog.ngc.nvidia.com/orgs/nvidia/containers/cloudxr-runtime``

* 你的 Kubernetes 集群中已安装 NVIDIA GPU Operator 或同等组件以暴露 NVIDIA GPU
* 你的 Kubernetes 集群各节点上已安装 NVIDIA Container Toolkit

准备工作
--------

在宿主机上，你应当已经配置好 ``kubectl`` 以访问你的 Kubernetes 集群。要进行验证，请运行以下命令并确认其正确返回你的节点：

.. code:: bash

   kubectl get node

如果你不是使用 :ref:`k8s-appendix` 中描述的设置，而是安装到自己的 Kubernetes 集群，那么你在 K8s 集群中的角色应至少拥有以下 RBAC 权限：

.. code:: yaml

   rules:
   - apiGroups: [""]
     resources: ["configmaps"]
     verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
   - apiGroups: ["apps"]
     resources: ["deployments", "replicasets"]
     verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
   - apiGroups: [""]
     resources: ["pods"]
     verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
   - apiGroups: [""]
     resources: ["services"]
     verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]

.. _k8s-installation:

安装
----

.. note::

   以下步骤已在安装了 GPU Operator 的 MicroK8s 集群上验证（配置见 :ref:`k8s-appendix`）。如果遇到问题，可以据此配置你自己的 K8s 集群。

#. 从 NGC 下载 Helm chart（根据 `公开指南 <https://docs.nvidia.com/ngc/ngc-overview/index.html#generating-api-key>`_ 获取你的 NGC API 密钥）：

   .. code:: bash

      helm fetch https://helm.ngc.nvidia.com/nvidia/charts/isaac-lab-teleop-2.3.0.tgz \
        --username='$oauthtoken' \
        --password=<your-ngc-api-key>

#. 在默认命名空间中安装并运行 Isaac Lab 的 CloudXR 遥操作 pod，占用宿主机全部 GPU：

   .. code:: bash

      helm upgrade --install hello-isaac-teleop isaac-lab-teleop-2.3.0.tgz \
        --set fullnameOverride=hello-isaac-teleop \
        --set hostNetwork="true"

   .. note::

      你可以通过创建外部 LoadBalancer VIP（例如使用 MetalLB）并在部署 Helm chart 时设置环境变量 ``NV_CXR_ENDPOINT_IP`` 来避免使用主机网络：

      .. code:: yaml

         # local_values.yml file example:
         fullnameOverride: hello-isaac-teleop
         streamer:
           extraEnvs:
             - name: NV_CXR_ENDPOINT_IP
               value: "<your external LoadBalancer VIP>"
             - name: ACCEPT_EULA
               value: "Y"

      .. code:: bash

         # command
         helm upgrade --install --values local_values.yml \
           hello-isaac-teleop isaac-lab-teleop-2.3.0.tgz

#. 验证部署已完成：

   .. code:: bash

      kubectl wait --for=condition=available --timeout=300s \
        deployment/hello-isaac-teleop

   pod 运行后，完成资产加载并开始流式传输大约还需要 5-8 分钟。

卸载
----

只需运行以下命令即可卸载：

.. code:: bash

   helm uninstall hello-isaac-teleop

.. _k8s-appendix:

附录：使用 MicroK8s 搭建本地 K8s 集群
--------------------------------------

你的本地工作站应当已安装 NVIDIA Container Toolkit 及其依赖，否则以下设置将无法工作。

清理现有安装（可选）
~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   # Clean up the system to ensure we start fresh
   sudo snap remove microk8s
   sudo snap remove helm
   sudo apt-get remove docker-ce docker-ce-cli containerd.io
   # If you have snap docker installed, remove it as well
   sudo snap remove docker

安装 MicroK8s
~~~~~~~~~~~~~

.. code:: bash

   sudo snap install microk8s --classic

安装 NVIDIA GPU Operator
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   microk8s helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
   microk8s helm repo update
   microk8s helm install gpu-operator \
     -n gpu-operator \
     --create-namespace nvidia/gpu-operator \
     --set toolkit.env[0].name=CONTAINERD_CONFIG \
     --set toolkit.env[0].value=/var/snap/microk8s/current/args/containerd-template.toml \
     --set toolkit.env[1].name=CONTAINERD_SOCKET \
     --set toolkit.env[1].value=/var/snap/microk8s/common/run/containerd.sock \
     --set toolkit.env[2].name=CONTAINERD_RUNTIME_CLASS \
     --set toolkit.env[2].value=nvidia \
     --set toolkit.env[3].name=CONTAINERD_SET_AS_DEFAULT \
     --set-string toolkit.env[3].value=true

.. note::

   如果你已将 GPU operator 配置为在设备插件上使用卷挂载方式的 ``DEVICE_LIST_STRATEGY``，并在 toolkit 上禁用了 ``ACCEPT_NVIDIA_VISIBLE_DEVICES_ENVVAR_WHEN_UNPRIVILEGED``，则该配置目前不受支持，因为无法确保所分配的 GPU 资源在同一 pod 的各容器之间一致共享。

验证安装
~~~~~~~~

运行以下命令验证所有 pod 都在正常运行：

.. code:: bash

   microk8s kubectl get pods -n gpu-operator

你应看到类似如下的输出：

.. code:: text

   NAMESPACE          NAME                                                        READY   STATUS      RESTARTS   AGE
   gpu-operator       gpu-operator-node-feature-discovery-gc-76dc6664b8-npkdg       1/1     Running     0          77m
   gpu-operator       gpu-operator-node-feature-discovery-master-7d6b448f6d-76fqj   1/1     Running     0          77m
   gpu-operator       gpu-operator-node-feature-discovery-worker-8wr4n              1/1     Running     0          77m
   gpu-operator       gpu-operator-86656466d6-wjqf4                                 1/1     Running     0          77m
   gpu-operator       nvidia-container-toolkit-daemonset-qffh6                      1/1     Running     0          77m
   gpu-operator       nvidia-dcgm-exporter-vcxsf                                    1/1     Running     0          77m
   gpu-operator       nvidia-cuda-validator-x9qn4                                   0/1     Completed   0          76m
   gpu-operator       nvidia-device-plugin-daemonset-t4j4k                          1/1     Running     0          77m
   gpu-operator       gpu-feature-discovery-8dms9                                   1/1     Running     0          77m
   gpu-operator       nvidia-operator-validator-gjs9m                               1/1     Running     0          77m

所有 pod 运行起来后，你就可以继续 :ref:`k8s-installation` 一节。
