IO Descriptors 入门
===================

.. currentmodule:: isaaclab

在本教程中，我们将学习 IO Descriptors 是什么、如何导出它们，以及如何将它们添加到你的环境中。我们将以 Anymal-D 机器人为例，演示如何从环境中导出 IO Descriptors，并以我们自己的 term 为例，演示如何将 IO Descriptors 附加到自定义的动作项和观测项上。


什么是 IO Descriptors？
------------------------

在深入介绍 IO Descriptors 之前，先来了解它们是什么以及有什么用处。

IO Descriptors 是一种描述使用 Isaac Lab 中 ManagerBasedRLEnv 训练的策略的输入和输出的方式。换句话说，它们描述了策略的动作项和观测项。这一描述用于生成一个 YAML 文件，该文件可以在外部工具中加载以运行策略，而无需手动输入动作项和观测项的配置。

除此之外，IO Descriptors 还提供以下信息：
- 关节体（articulation）中所有关节的参数。
- 一些仿真参数，包括仿真时间步长和策略时间步长。
- 对于某些动作项和观测项，它会按照动作项/观测项中出现的顺序提供关节名称或刚体名称。
- 对于观测项和动作项，它会按照各项在管理器中出现的精确顺序提供。这使得从 YAML 文件中重建它们变得十分容易。

下面是由 IO Descriptors 生成的 YAML 中 Anymal-D 机器人动作部分的一个示例：

.. literalinclude:: ../../_static/policy_deployment/01_io_descriptors/isaac_velocity_flat_anymal_d_v0_IO_descriptors.yaml
   :language: yaml
   :lines: 1-39

下面是由 IO Descriptors 生成的 YAML 中 Anymal-D 机器人观测部分的一个片段示例：

.. literalinclude:: ../../_static/policy_deployment/01_io_descriptors/isaac_velocity_flat_anymal_d_v0_IO_descriptors.yaml
   :language: yaml
   :lines: 158-199

.. literalinclude:: ../../_static/policy_deployment/01_io_descriptors/isaac_velocity_flat_anymal_d_v0_IO_descriptors.yaml
   :language: yaml
   :lines: 236-279

需要注意的是，动作项和观测项都是以字典列表的形式返回，而不是字典的字典。这样做是为了确保各项的顺序得以保留。因此，要获取某个动作项或观测项，用户需要在字典中查找 ``name`` 键。

例如，在下面的片段中，我们查看的是 ``projected_gravity`` 观测项。``name`` 键用于标识该项。``full_path`` 键用于提供 Isaac Lab 源代码中用于计算该项的函数的显式路径。同时还提供了一些标志，例如 ``mdp_type`` 和 ``observation_type``，它们没有任何功能性影响，只是用来告知用户该项所属的类别。

.. literalinclude:: ../../_static/policy_deployment/01_io_descriptors/isaac_velocity_flat_anymal_d_v0_IO_descriptors.yaml
   :language: yaml
   :lines: 200-219
   :emphasize-lines: 9, 11


从环境中导出 IO Descriptors
--------------------------------------------

本节将介绍如何从环境中导出 IO Descriptors。请记住，此功能仅适用于管理器式的 RL 环境。

如果已经使用给定配置训练好了策略，则可以使用以下命令导出 IO Descriptors：

.. code-block:: bash

   ./isaaclab.sh -p scripts/environments/export_io_descriptors.py --task <task_name> --output_dir <output_dir>

例如，如果想导出 Anymal-D 机器人的 IO Descriptors，可以运行：

.. code-block:: bash

   ./isaaclab.sh -p scripts/environments/export_io_descriptors.py --task Isaac-Velocity-Flat-Anymal-D-v0 --output_dir ./io_descriptors

在训练策略时，也可以请求在训练开始时导出 IO Descriptors。这可以通过在命令行中设置 ``export_io_descriptors`` 标志来实现。

.. code-block:: bash

   ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py --task Isaac-Velocity-Flat-Anymal-D-v0 --export_io_descriptors
   ./isaaclab.sh -p scripts/reinforcement_learning/sb3/train.py --task Isaac-Velocity-Flat-Anymal-D-v0 --export_io_descriptors
   ./isaaclab.sh -p scripts/reinforcement_learning/rl_games/train.py --task Isaac-Velocity-Flat-Anymal-D-v0 --export_io_descriptors
   ./isaaclab.sh -p scripts/reinforcement_learning/skrl/train.py --task Isaac-Velocity-Flat-Anymal-D-v0 --export_io_descriptors


将 IO Descriptors 附加到自定义观测项
----------------------------------------------------

本节将介绍如何将 IO Descriptors 附加到自定义观测项上。

让我们看看如何将 IO Descriptor 附加到一个简单的观测项上：

.. code-block:: python

   @generic_io_descriptor(
      units="m/s", axes=["X", "Y", "Z"], observation_type="RootState", on_inspect=[record_shape, record_dtype]
   )
   def base_lin_vel(env: ManagerBasedEnv, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> torch.Tensor:
       """Root linear velocity in the asset's root frame."""
       # extract the used quantities (to enable type-hinting)
       asset: RigidObject = env.scene[asset_cfg.name]
       return asset.data.root_lin_vel_b

这里我们定义了一个名为 ``base_lin_vel`` 的自定义观测项，用于计算机器人根部的线速度。我们还为该项附加了一个 IO Descriptor。该 IO Descriptor 通过 ``@generic_io_descriptor`` 装饰器定义。

``@generic_io_descriptor`` 装饰器是一个特殊的装饰器，用于将 IO Descriptor 附加到自定义观测项上。它接受任意参数来描述该观测项，这里我们提供了一些可能对最终用户有用的额外信息：

- ``units`` ：观测项的单位。
- ``axes`` ：观测项的轴。
- ``observation_type`` ：观测项的类型。

你还会注意到提供了一个 ``on_inspect`` 参数。这是一个用于检查观测项的函数列表。这里我们使用 ``record_shape`` 和 ``record_dtype`` 函数来记录观测项输出的形状和 dtype。

这些函数的定义如下：

.. code-block:: python

   def record_shape(output: torch.Tensor, descriptor: GenericObservationIODescriptor, **kwargs) -> None:
       """Record the shape of the output tensor.

       Args:
          output: The output tensor.
          descriptor: The descriptor to record the shape to.
          **kwargs: Additional keyword arguments.
       """
       descriptor.shape = (output.shape[-1],)


   def record_dtype(output: torch.Tensor, descriptor: GenericObservationIODescriptor, **kwargs) -> None:
       """Record the dtype of the output tensor.

       Args:
          output: The output tensor.
          descriptor: The descriptor to record the dtype to.
          **kwargs: Additional keyword arguments.
       """
       descriptor.dtype = str(output.dtype)

这些函数总是以观测项的输出张量作为第一个参数，以描述符作为第二个参数。观测项的所有输入都会在 ``kwargs`` 中提供。除了 ``on_inspect`` 函数之外，装饰器还会在后台调用一些函数来收集观测项的 ``name``、``description`` 和 ``full_path``。请注意，添加此装饰器不会改变观测项的签名，因此可以安全地与观测管理器一起使用。

现在让我们来看一个更复杂的示例：获取机器人的相对关节位置。

.. code-block:: python

   @generic_io_descriptor(
       observation_type="JointState",
       on_inspect=[record_joint_names, record_dtype, record_shape, record_joint_pos_offsets],
       units="rad",
   )
   def joint_pos_rel(env: ManagerBasedEnv, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> torch.Tensor:
       """The joint positions of the asset w.r.t. the default joint positions.

       Note: Only the joints configured in :attr:`asset_cfg.joint_ids` will have their positions returned.
       """
       # extract the used quantities (to enable type-hinting)
       asset: Articulation = env.scene[asset_cfg.name]
       return asset.data.joint_pos[:, asset_cfg.joint_ids] - asset.data.default_joint_pos[:, asset_cfg.joint_ids]

与前面的示例类似，我们通过一组探测观测项的函数，为自定义观测项添加 IO Descriptor。

要获取关节的名称，可以编写如下函数：

.. code-block:: python

   def record_joint_names(output: torch.Tensor, descriptor: GenericObservationIODescriptor, **kwargs) -> None:
       """Record the joint names of the output tensor.

       Expects the `asset_cfg` keyword argument to be set.

       Args:
           output: The output tensor.
           descriptor: The descriptor to record the joint names to.
           **kwargs: Additional keyword arguments.
       """
       asset: Articulation = kwargs["env"].scene[kwargs["asset_cfg"].name]
       joint_ids = kwargs["asset_cfg"].joint_ids
       if joint_ids == slice(None, None, None):
           joint_ids = list(range(len(asset.joint_names)))
       descriptor.joint_names = [asset.joint_names[i] for i in joint_ids]

请注意，我们可以在 ``kwargs`` 字典中访问观测项的所有输入。因此可以访问 ``asset_cfg``，它包含计算该观测项所用的关节体的配置。

要获取偏移量，可以编写如下函数：

.. code-block:: python

   def record_joint_pos_offsets(output: torch.Tensor, descriptor: GenericObservationIODescriptor, **kwargs):
    """Record the joint position offsets of the output tensor.

    Expects the `asset_cfg` keyword argument to be set.

    Args:
        output: The output tensor.
        descriptor: The descriptor to record the joint position offsets to.
        **kwargs: Additional keyword arguments.
    """
       asset: Articulation = kwargs["env"].scene[kwargs["asset_cfg"].name]
       ids = kwargs["asset_cfg"].joint_ids
       # Get the offsets of the joints for the first robot in the scene.
       # This assumes that all robots have the same joint offsets.
       descriptor.joint_pos_offsets = asset.data.default_joint_pos[:, ids][0]

有了这些知识，你现在应该能够为自己的自定义观测项附加 IO Descriptor 了。不过，在本教程结束之前，让我们再看看如何将 IO Descriptor 附加到自定义动作项上。


将 IO Descriptors 附加到自定义动作项
-----------------------------------------------

本节将介绍如何将 IO Descriptors 附加到自定义动作项上。动作项是继承自 :class:`managers.ActionTerm` 类的类。要为动作项添加 IO Descriptor，我们需要扩展它的 :meth:`~managers.ActionTerm.IO_descriptor` 属性。

默认情况下，:meth:`~managers.ActionTerm.IO_descriptor` 属性会返回基础描述符并填充以下字段：
- ``name`` ：动作项的名称。
- ``full_path`` ：动作项的完整路径。
- ``description`` ：动作项的描述。
- ``export`` ：是否导出该动作项。

.. code-block:: python

   @property
   def IO_descriptor(self) -> GenericActionIODescriptor:
       """The IO descriptor for the action term."""
       self._IO_descriptor.name = re.sub(r"([a-z])([A-Z])", r"\1_\2", self.__class__.__name__).lower()
       self._IO_descriptor.full_path = f"{self.__class__.__module__}.{self.__class__.__name__}"
       self._IO_descriptor.description = " ".join(self.__class__.__doc__.split())
       self._IO_descriptor.export = self.export_IO_descriptor
       return self._IO_descriptor

要向描述符添加更多信息，我们需要重写 :meth:`~managers.ActionTerm.IO_descriptor` 属性。让我们看一个示例，了解如何向描述符添加关节名称、缩放（scale）、偏移（offset）和裁剪（clip）。

.. code-block:: python

   @property
   def IO_descriptor(self) -> GenericActionIODescriptor:
       """The IO descriptor of the action term.

       This descriptor is used to describe the action term of the joint action.
       It adds the following information to the base descriptor:
       - joint_names: The names of the joints.
       - scale: The scale of the action term.
       - offset: The offset of the action term.
       - clip: The clip of the action term.

       Returns:
           The IO descriptor of the action term.
       """
       super().IO_descriptor
       self._IO_descriptor.shape = (self.action_dim,)
       self._IO_descriptor.dtype = str(self.raw_actions.dtype)
       self._IO_descriptor.action_type = "JointAction"
       self._IO_descriptor.joint_names = self._joint_names
       self._IO_descriptor.scale = self._scale
       # This seems to be always [4xNum_joints] IDK why. Need to check.
       if isinstance(self._offset, torch.Tensor):
           self._IO_descriptor.offset = self._offset[0].detach().cpu().numpy().tolist()
       else:
           self._IO_descriptor.offset = self._offset
       # FIXME: This is not correct. Add list support.
       if self.cfg.clip is not None:
           if isinstance(self._clip, torch.Tensor):
               self._IO_descriptor.clip = self._clip[0].detach().cpu().numpy().tolist()
           else:
               self._IO_descriptor.clip = self._clip
       else:
           self._IO_descriptor.clip = None
       return self._IO_descriptor

以上就是全部内容。你现在应该能够为自己的自定义动作项附加 IO Descriptor 了，本教程到此结束。
