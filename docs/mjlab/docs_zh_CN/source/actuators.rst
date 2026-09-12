.. _actuators:

执行器
======

执行器 (actuator) 将高层指令 (位置、速度、力) 转换为驱动关节的底层力。执行器通过
:ref:`EntityCfg <entity>` 的 ``articulation`` 字段进行配置。mjlab 提供
**内置执行器** 与 **显式执行器** 两类：前者利用物理引擎的隐式积分获得最佳稳定性，
后者用于自定义控制律和执行器动力学。


快速上手
--------

使用 ``BuiltinPositionActuator`` 进行基础的 PD 控制，这是最常见的起点。

.. code-block:: python

    from mjlab.actuator import BuiltinPositionActuatorCfg
    from mjlab.entity import EntityCfg, EntityArticulationInfoCfg

    robot_cfg = EntityCfg(
        spec_fn=lambda: load_robot_spec(),
        articulation=EntityArticulationInfoCfg(
            actuators=(
                BuiltinPositionActuatorCfg(
                    target_names_expr=(".*_hip_.*", ".*_knee_.*"),
                    stiffness=80.0,
                    damping=10.0,
                    effort_limit=100.0,
                ),
            ),
        ),
    )

在任何执行器配置上直接添加延迟字段，即可对通信延迟进行建模。

.. code-block:: python

    from mjlab.actuator import BuiltinPositionActuatorCfg

    BuiltinPositionActuatorCfg(
        target_names_expr=(".*",),
        stiffness=80.0,
        damping=10.0,
        delay_min_lag=2,  # Minimum 2 physics steps
        delay_max_lag=5,  # Maximum 5 physics steps
    )


内置执行器与显式执行器
----------------------

配置执行器时的关键设计决策是使用 **内置** 类型还是 **显式** 类型。二者的区别
归结为 MuJoCo 的积分器如何处理速度相关的力。

**内置执行器** (``BuiltinPositionActuator``, ``BuiltinVelocityActuator``,
``BuiltinMotorActuator``, ``BuiltinPdActuator``, ``BuiltinDcMotorActuator``,
``BuiltinMuscleActuator``) 会在 MjSpec 中创建原生的 MuJoCo 执行器元素。物理引擎
计算控制律，并对速度相关的阻尼力进行隐式积分。这带来最佳的数值稳定性，在高增益
或较大时间步长时尤为明显。

**显式执行器** (``IdealPdActuator``, ``DcMotorActuator``, ``LearnedMlpActuator``)
在用户代码中计算力矩，并通过作为直通层的 ``<motor>`` 执行器转发。由于积分器无法
考虑这些外部计算力的速度导数，显式类型的数值稳定性不如内置类型。当需要内置类型
无法表达的自定义控制律或执行器动力学 (例如速度相关的力矩限制、学习得到的执行器
网络) 时，应使用显式执行器。

在小时间步长下的线性、无约束情形中，两种方法的结果非常接近。而在更大的时间步长
或更高增益下，内置执行器更为宽容。

**积分器选择。** mjlab 将阻尼放在执行器内而非关节上。``euler`` 积分器对关节阻尼
采用隐式处理，但对执行器阻尼采用显式处理，从而限制了稳定性。``implicitfast``
积分器对所有已知的速度相关力均采用隐式处理，能够在不增加额外开销的情况下同时
处理执行器的比例项和阻尼项。

.. note::

     mjlab 默认使用 ``implicitfast`` ，因为它是 MuJoCo 推荐的积分器，对执行器
     一侧的阻尼具有更优的稳定性。


执行器类型
----------

所有执行器配置都共享几个继承自 ``ActuatorCfg`` 的通用字段：

- ``target_names_expr``: 由正则表达式组成的元组，用于匹配关节名称 (使用其他
  ``transmission_type`` 时则匹配肌腱/site 名称)。
- ``armature``: 添加到目标关节的折算转子惯量。
- ``frictionloss``: 以约束形式建模在目标关节上的静摩擦 (stiction)。参见 MuJoCo
  的 `frictionloss <https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint-frictionloss>`_ 文档。

内置执行器
^^^^^^^^^^

内置执行器通过 MjSpec API 使用 MuJoCo 的原生执行器类型。

**BuiltinPositionActuator**: 创建用于 PD 控制的 ``<position>`` 执行器。

**BuiltinVelocityActuator**: 创建用于速度控制的 ``<velocity>`` 执行器。

**BuiltinMotorActuator**: 创建用于直接力矩控制的 ``<motor>`` 执行器。

**BuiltinPdActuator**: 原生 PD，同时对位置目标和速度目标闭环，实现为一对
``<position>`` + ``<velocity>`` 执行器，二者输出相加，合力为
``kp * (p_target - q) + kd * (v_target - qdot)`` 。``BuiltinPositionActuator``
将 kd 放在 ``<position>`` 元素上，隐式假设速度参考值为零；当策略输出非零速度
目标时，应使用本类型。原生传递使 ``implicit`` / ``implicitfast`` 能够在其速度
更新中看到 kd 项，而 ``IdealPdActuator`` 只是通过一个不透明的 ``<motor>`` 转发
Python 计算的力矩，不具备这一优势。

**BuiltinDcMotorActuator**: 封装 MuJoCo 原生的
`<dcmotor> <https://mujoco.readthedocs.io/en/stable/XMLreference.html#actuator-dcmotor>`_
元素。其力矩为 ``tau = K * (V - K * omega) / R`` ，反电动势经由原生 bias 通路
传递，因此 ``implicit`` / ``implicitfast`` 会把它的速度导数识别为等效阻尼。三种
输入模式决定 ``ctrl`` 携带的内容：VOLTAGE 直接驱动电机；POSITION / VELOCITY
针对单一设定点闭合内部 PID (带抗积分饱和与斜率限制)，其输出经 Vmax 限幅后转化
为力矩。POSITION 模式将 v_target 固定为 0 (kd 项作用于原始速度)。可选物理效应：
电感、带 I^2R 发热的温度模型、齿槽转矩纹波、LuGre 摩擦。``DcMotorActuator``
(显式版本) 是在 ``<motor>`` 之上叠加速度相关力矩限幅的软件 PD；本类型才是真正
的电气模型。

**BuiltinMuscleActuator**: 创建 ``<muscle>`` 执行器，用于模拟具有力-长度-速度
特性的仿生肌肉动力学。

.. code-block:: python

    from mjlab.actuator import BuiltinPositionActuatorCfg, BuiltinVelocityActuatorCfg

    # Mobile manipulator: PD for arm joints, velocity control for wheels.
    actuators = (
        BuiltinPositionActuatorCfg(
            target_names_expr=(".*_shoulder_.*", ".*_elbow_.*", ".*_wrist_.*"),
            stiffness=100.0,
            damping=10.0,
            effort_limit=150.0,
        ),
        BuiltinVelocityActuatorCfg(
            target_names_expr=(".*_wheel_.*",),
            damping=20.0,
            effort_limit=50.0,
        ),
    )


显式执行器
^^^^^^^^^^

显式执行器自行计算力 (effort)，并将其转发给作为直通层的底层 ``<motor>`` 执行器。
稳定性方面的影响请参见上文 `内置执行器与显式执行器`_ 一节。

**IdealPdActuator**: 实现理想的 PD 控制器，力矩按
``tau = Kp * pos_error + Kd * vel_error`` 计算。

**DcMotorActuator**: 在 ``IdealPdActuator`` 的基础上增加速度相关的力矩饱和，
以建模直流电机的转矩-转速曲线 (反电动势效应)。实现线性的转矩-转速曲线：零速时
力矩最大，最大速度时力矩为零。

**LearnedMlpActuator**: 基于神经网络的执行器，使用训练好的 MLP 根据关节状态
历史预测力矩输出。当解析模型无法刻画延迟、非线性、摩擦效应等复杂执行器动力学时
非常有用。继承直流电机基于速度的力矩限制。

.. code-block:: python

    from mjlab.actuator import IdealPdActuatorCfg, DcMotorActuatorCfg

    # Ideal PD for hips, DC motor model with torque-speed curve for knees.
    actuators = (
        IdealPdActuatorCfg(
            target_names_expr=(".*_hip_.*",),
            stiffness=80.0,
            damping=10.0,
            effort_limit=100.0,
        ),
        DcMotorActuatorCfg(
            target_names_expr=(".*_knee_.*",),
            stiffness=80.0,
            damping=10.0,
            effort_limit=25.0,       # Continuous torque limit
            saturation_effort=50.0,  # Peak torque at stall
            velocity_limit=30.0,     # No-load speed (rad/s)
        ),
    )


XML 执行器
^^^^^^^^^^

XML 执行器封装机器人 XML 文件中已定义的执行器。配置通过将已有执行器的
``target`` 关节名称与 ``target_names_expr`` 模式进行匹配来找到它们。每个关节
必须恰好对应一个匹配的执行器。

**XmlActuator**: 封装 XML 中已定义的任意执行器。执行器类型 (position、velocity、
motor、muscle) 会从 XML 元素自动检测，也可以通过 ``command_field`` 显式指定。

.. code-block:: python

    from mjlab.actuator import XmlActuatorCfg

    # Robot XML already has:
    # <actuator>
    #   <position name="hip_joint" joint="hip_joint" kp="100"/>
    # </actuator>

    # Wrap existing XML actuators.
    actuators = (
        XmlActuatorCfg(target_names_expr=("hip_joint",)),
    )

执行器延迟
^^^^^^^^^^

任何执行器配置都支持内联的延迟字段，用于对指令延迟建模。在真实机器人上，板载
PD 环路以 KHz 频率运行并可直接读取编码器，但来自策略的位置目标会因推理耗时和
通信总线周期而延迟到达。执行器延迟对此建模：指令目标被延迟，而控制律看到的仍是
新鲜的关节状态。

这与观测延迟不同，后者对传感器管线的延迟建模 (进入策略的状态是过期的)。二者共同
覆盖了往返链路的两个方向：从传感器到策略，再从策略到电机。

.. code-block:: python

    from mjlab.actuator import IdealPdActuatorCfg

    # Add 2-5 step delay to position commands.
    actuators = (
        IdealPdActuatorCfg(
            target_names_expr=(".*",),
            stiffness=80.0,
            damping=10.0,
            delay_min_lag=2,
            delay_max_lag=5,
            delay_hold_prob=0.3,         # 30% chance to keep current lag
            delay_update_period=10,      # Resample lag every 10 steps
        ),
    )

每个物理步都会从 ``[delay_min_lag, delay_max_lag]`` 中均匀采样一个滞后值。延迟
以物理时间步为粒度进行量化。例如，在 500Hz 的物理步频 (每步 2ms) 下，
``delay_min_lag=2`` 表示最小 4ms 的延迟。


编写执行器配置
--------------

由于每个配置内的执行器参数是统一的，对于需要不同参数的关节，应使用单独的执行器
配置：

.. code-block:: python

    from mjlab.actuator import BuiltinPositionActuatorCfg

    # G1 humanoid with different gains per joint group.
    G1_ACTUATORS = (
        BuiltinPositionActuatorCfg(
            target_names_expr=(".*_hip_.*", "waist_yaw_joint"),
            stiffness=180.0,
            damping=18.0,
            effort_limit=88.0,
            armature=0.0015,
        ),
        BuiltinPositionActuatorCfg(
            target_names_expr=("left_hip_pitch_joint", "right_hip_pitch_joint"),
            stiffness=200.0,
            damping=20.0,
            effort_limit=88.0,
            armature=0.0015,
        ),
        BuiltinPositionActuatorCfg(
            target_names_expr=(".*_knee_joint",),
            stiffness=150.0,
            damping=15.0,
            effort_limit=139.0,
            armature=0.0025,
        ),
        BuiltinPositionActuatorCfg(
            target_names_expr=(".*_ankle_.*",),
            stiffness=40.0,
            damping=5.0,
            effort_limit=25.0,
            armature=0.0008,
        ),
    )

这一设计选择体现了 mjlab 的一次有意简化：每个 ``ActuatorCfg`` 代表一种单一的
执行器类型 (例如某个具体的电机/减速箱型号)，并均匀地应用于它驱动的所有关节。
``armature`` (折算转子惯量) 和 ``gear`` 等硬件参数描述的是执行器硬件的属性，
尽管它们在 MuJoCo 中是作为关节或执行器字段实现的。在其他框架 (如 Isaac Lab)
中，这些字段可能接受 ``float | dict[str, float]`` 以支持逐关节的差异。mjlab 则
鼓励每种执行器类型或每组关节使用一个配置，使硬件模型在物理上保持一致且明确。
主要的代价是在特殊情况下 (例如并联连杆机构) 会显得繁琐——逐关节覆盖本可以带来
便利——但换来的是更清晰的语义和更简单的维护。

关于动作项如何把策略输出路由到执行器 (包括用于任务空间控制的 DifferentialIK)，
参见 :ref:`actions` ；关于增益和 effort 上限的随机化，参见
:ref:`domain_randomization` 。


计算硬件参数
------------

本节适用于根据真实电机数据手册配置执行器的情形。如果你使用的是手动整定的增益，
可以跳过本节。

mjlab 在 ``mjlab.utils.actuator`` 中提供了一些工具，可根据电机的物理规格计算
执行器参数。这对于计算折算惯量 (``armature``) 以及从硬件数据手册推导合适的控制
增益尤其有用。

**示例：Unitree G1 电机配置**

.. code-block:: python

    from math import pi

    from mjlab.utils.actuator import (
        reflected_inertia_from_two_stage_planetary,
        ElectricActuator
    )

    # Motor specs from manufacturer datasheet.
    ROTOR_INERTIAS_7520_14 = (
        0.489e-4,  # Motor rotor inertia (kg*m**2)
        0.098e-4,  # Planet carrier inertia
        0.533e-4,  # Output stage inertia
    )
    GEARS_7520_14 = (
        1,            # First stage (motor to planet)
        4.5,          # Second stage (planet to carrier)
        1 + (48/22),  # Third stage (carrier to output)
    )

    # Compute reflected inertia at joint output.
    # J_reflected = J_motor*(N1*N2)**2 + J_carrier*N2**2 + J_output.
    ARMATURE_7520_14 = reflected_inertia_from_two_stage_planetary(
        ROTOR_INERTIAS_7520_14, GEARS_7520_14
    )

    # Create motor spec container.
    ACTUATOR_7520_14 = ElectricActuator(
        reflected_inertia=ARMATURE_7520_14,
        velocity_limit=32.0,   # rad/s at joint
        effort_limit=88.0,     # N*m continuous torque
    )

    # Derive PD gains from natural frequency and damping ratio.
    NATURAL_FREQ = 10 * 2*pi  # 10 Hz bandwidth.
    DAMPING_RATIO = 2.0       # Overdamped, see note below.
    STIFFNESS = ARMATURE_7520_14 * NATURAL_FREQ**2
    DAMPING = 2 * DAMPING_RATIO * ARMATURE_7520_14 * NATURAL_FREQ

    # Use in actuator config.
    from mjlab.actuator import BuiltinPositionActuatorCfg

    actuator = BuiltinPositionActuatorCfg(
        target_names_expr=(".*_hip_pitch_joint",),
        stiffness=STIFFNESS,
        damping=DAMPING,
        effort_limit=ACTUATOR_7520_14.effort_limit,
        armature=ACTUATOR_7520_14.reflected_inertia,
    )

.. note::

     示例使用 ``DAMPING_RATIO = 2.0`` (过阻尼) 而非临界阻尼值 1.0。这是因为
     折算惯量的计算只考虑了电机转子的惯量，而没有考虑被驱动连杆的表观惯量。
     实际上，关节处的总有效惯量高于单纯的电机折算惯量，因此在真实系统惯量被
     低估时，采用过阻尼的阻尼比能提供更好的稳定裕度。

**并联连杆机构近似：**

对于由并联连杆机构驱动的关节 (例如 G1 的双电机脚踝)，标称位姿下的等效 armature
可以近似为各电机 armature 之和：

.. code-block:: python

    # Two 5020 motors driving ankle through parallel linkage.
    G1_ACTUATOR_ANKLE = BuiltinPositionActuatorCfg(
        target_names_expr=(".*_ankle_pitch_joint", ".*_ankle_roll_joint"),
        stiffness=STIFFNESS_5020 * 2,
        damping=DAMPING_5020 * 2,
        effort_limit=ACTUATOR_5020.effort_limit * 2,
        armature=ACTUATOR_5020.reflected_inertia * 2,
    )


扩展：自定义执行器
------------------

所有执行器都实现统一的 ``compute()`` 接口：该接口接收一个 ``ActuatorCmd``
(包含位置、速度和 effort 目标)，并返回驱动各关节的底层 MuJoCo 执行器所需的
控制信号。

**核心接口：**

.. code-block:: python

    def compute(self, cmd: ActuatorCmd) -> torch.Tensor:
        """Convert high-level commands to control signals.

        Args:
            cmd: Command containing position_target, velocity_target,
                effort_target (each is a [num_envs, num_targets] tensor
                or None)

        Returns:
            Control signals for this actuator
            ([num_envs, num_targets] tensor)
        """

**生命周期钩子：**

- ``edit_spec``: 在编译前修改 MjSpec (添加执行器、设置增益)
- ``initialize``: 编译后的初始化 (解析索引、分配缓冲区)
- ``reset``: 逐环境的重置逻辑
- ``update``: 步进前的更新
- ``compute``: 将指令转换为控制信号

**属性：**

- ``target_ids``: 本执行器所控制的局部目标索引张量
- ``target_names``: 本执行器所控制的目标名称列表
- ``ctrl_ids``: 本执行器的全局控制输入索引张量

``IdealPdActuator`` 是编写自定义显式执行器时推荐使用的基类。
``DcMotorActuator`` 和 ``LearnedMlpActuator`` 都构建于其上，可作为扩展模式的
示例。
