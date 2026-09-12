贡献指南
========

我们衷心欢迎为本项目做出贡献，让这个框架更加成熟、对每个人都更有用。贡献可以采取以下形式：

* Bug 报告：请在 `issue tracker <https://github.com/isaac-sim/IsaacLab/issues>`__ 中报告你发现的任何 bug。
* 功能请求：请在 `discussions <https://github.com/isaac-sim/IsaacLab/discussions>`__ 中提出你希望看到的新功能。
* 代码贡献：请提交 `pull request <https://github.com/isaac-sim/IsaacLab/pulls>`__。

  * Bug 修复
  * 新功能
  * 文档改进
  * 教程及教程改进

我们更倾向于使用 GitHub `discussions <https://github.com/isaac-sim/IsaacLab/discussions>`_ 来讨论想法、
提出问题、进行交流以及请求新功能。

请仅在
`issue tracker <https://github.com/isaac-sim/IsaacLab/issues>`_ 中跟踪范围明确、交付物清晰、
可执行的工作项。这些可以是修复 bug、新功能或一般性更新。


贡献代码
--------

.. attention::

   在向代码库贡献代码之前，请先参阅 `Google Style Guide <https://google.github.io/styleguide/pyguide.html>`__
   了解代码风格。在代码风格一节中，
   我们列出了本代码库相对于该风格指南的具体偏离之处。

我们使用 `GitHub <https://github.com/isaac-sim/IsaacLab>`__ 托管代码。请
按照以下步骤贡献代码：

1. 在 `issue tracker <https://github.com/isaac-sim/IsaacLab/issues>`__ 中创建一个 issue，讨论
   你希望进行的修改或新增内容。这有助于我们避免重复工作，并确保
   这些修改与项目的路线图保持一致。
2. Fork 该仓库。
3. 为你的修改创建一个新分支。
4. 进行修改并提交。
5. 将修改推送到你的 fork。
6. 向 `main 分支 <https://github.com/isaac-sim/IsaacLab/compare>`__ 提交 pull request。
7. 确保 pull request 模板中的所有检查项都已完成。

发送 pull request 后，维护者会审查你的代码并给出反馈。

请确保你的代码格式规范、有文档说明，并通过所有测试。

.. tip::

   让 pull request 尽可能小很重要。这能让
   维护者更容易审查你的代码。如果你有多个修改，请发送多个 pull request。
   大型 pull request 难以审查，合并可能需要很长时间。


关于代码风格和测试的更多细节，可参见 `代码风格`_ 和 `单元测试`_ 两节。


贡献文档
--------

为文档做贡献和为代码库做贡献一样简单。文档的所有源文件
都位于 ``IsaacLab/docs`` 目录下。文档使用
`reStructuredText <https://docutils.sourceforge.io/rst.html>`__ 格式编写。

我们使用 `Sphinx <https://www.sphinx-doc.org/en/master/>`__ 配合
`Book Theme <https://sphinx-book-theme.readthedocs.io/en/stable/>`__
来维护文档。

为文档发送 pull request 与为代码库发送 pull request 相同。
请遵循 `贡献代码`_ 一节中提到的步骤。

.. caution::

  要构建文档，我们建议创建一个 `virtual environment <https://docs.python.org/3/library/venv.html>`__
  来安装依赖项。也可以是 `conda 环境 <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html>`__。


要构建文档，请在终端中运行以下命令，它会安装所需的 python 软件包并
使用 ``docs/Makefile`` 构建文档：

.. code:: bash

   ./isaaclab.sh --docs  # or "./isaaclab.sh -d"

文档会生成在 ``docs/_build`` 目录下。要查看文档，请打开
``html`` 目录下的 ``index.html`` 文件。可以通过在终端中运行以下命令
来完成：

.. code:: bash

   xdg-open docs/_build/current/index.html

.. hint::

   ``xdg-open`` 命令用于在默认浏览器中打开 ``index.html`` 文件。如果你
   使用其他操作系统，可以使用相应的命令在浏览器中打开该文件。


要进行干净的构建，请在终端中运行以下命令：

.. code:: bash

   rm -rf docs/_build && ./isaaclab.sh --docs


贡献资产
--------

目前，我们将扩展所用的资产托管在 `NVIDIA Nucleus Server <https://docs.omniverse.nvidia.com/nucleus/latest/index.html>`__ 上。
Nucleus 是一个基于云的存储服务，允许用户存储和共享大型文件。它
与 `NVIDIA Omniverse Platform <https://developer.nvidia.com/omniverse>`__ 集成。

由于所有资产都托管在 Nucleus 上，我们无需将它们包含在仓库中。不过，
我们需要在文档中提供这些资产的链接。

请查阅 `Isaac Sim Assets <https://docs.isaacsim.omniverse.nvidia.com/latest/assets/usd_assets_overview.html>`__
以进一步了解目前可用的资产。

.. attention::

  我们目前正在研究更好的资产贡献方式。一旦有了解决方案，我们会更新本节内容。
  在此期间，请遵循以下步骤。

要托管你自己的资产，目前的方案是：

1. 为这些资产创建一个单独的仓库，并把资产放到那里
2. 确保这些资产已获得使用和分发许可
3. 在仓库的 README 文件中包含这些资产的图片
4. 发送一个包含该仓库链接的 pull request

随后我们会核验这些资产及其许可情况，并将资产收录到 Nucleus 服务器上进行托管。
如果你有任何疑问，欢迎通过邮件或在该仓库中提交 issue 与我们联系。


维护 changelog 与 extension.toml
--------------------------------

每个扩展都在 ``docs`` 目录下的 ``CHANGELOG.rst`` 文件中维护变更日志，
并在 ``config`` 目录下维护一个 ``extension.toml`` 文件。

``extension.toml`` 文件包含该扩展的元数据。它用于描述该扩展的
名称、版本、描述以及其他元数据。

``CHANGELOG.rst`` 文件包含该扩展每个版本经过整理的、按时间顺序排列的
重要变更列表。

.. note::

   ``extension.toml`` 文件中的版本号应按照
   `语义化版本 <https://semver.org/>`__ 进行更新，并且应与
   ``CHANGELOG.rst`` 文件中的版本号一致。

变更日志文件使用 `reStructuredText <https://docutils.sourceforge.io/rst.html>`__ 格式编写。
该变更日志的目标是帮助用户和贡献者准确了解该扩展在每个发布版本（或版本）之间
发生了哪些重要变更。这对每个扩展来说都是*必须*的。

要更新变更日志，请遵循以下准则：

* 每个版本都应有一个包含版本号和发布日期的章节。
* 版本号按照 `语义化版本 <https://semver.org/>`__ 进行更新。
  发布日期是该版本发布的日期。
* 每个版本根据变更类型划分为若干子章节。

  * ``Added``：用于新功能。
  * ``Changed``：用于现有功能的变更。
  * ``Deprecated``：用于即将移除的功能。
  * ``Removed``：用于现已移除的功能。
  * ``Fixed``：用于任何 bug 修复。

* 每项变更在其对应的子章节中以项目符号列表的形式描述。
* 项目符号列表使用**过去时**书写。

  * 这意味着变更被描述为仿佛已经发生。
  * 项目符号应简洁、切中要点，不应冗长。
  * 如适用，项目符号中还应包含做出该变更的原因。


.. tip::

   如有疑问，请查看现有变更日志文件中的风格，并遵循同样的风格。

例如，以下是一个变更日志示例：

.. code:: rst

    Changelog
    ---------

    0.1.0 (2021-02-01)
    ~~~~~~~~~~~~~~~~~~

    Added
    ^^^^^

    * Added a new feature that helps in a 10x speedup.

    Changed
    ^^^^^^^

    * Changed an existing feature. Earlier, we were using :meth:`torch.bmm` to perform the matrix multiplication.
      However, this was slow for large matrices. We have now switched to using :meth:`torch.einsum` which is
      significantly faster.

    Deprecated
    ^^^^^^^^^^

    * Deprecated an existing feature in favor of a new feature.

    Removed
    ^^^^^^^

    * Removed an existing feature. This was done to simplify the codebase and reduce the complexity.

    Fixed
    ^^^^^

    * Fixed crashing of the :meth:`my_function` when the input was too large.
      We now use :meth:`torch.einsum` that is able to handle larger inputs.


代码风格
--------

我们的代码库遵循 `Google Style
Guides <https://google.github.io/styleguide/pyguide.html>`__。
对于 Python 代码，我们遵循 PEP 准则。其中最重要的是关于代码注释与
布局的 `PEP-8 <https://www.python.org/dev/peps/pep-0008/>`__，
以及关于类型标注的
`PEP-484 <http://www.python.org/dev/peps/pep-0484>`__ 和
`PEP-585 <https://www.python.org/dev/peps/pep-0585/>`__。

对于文档，我们的 docstring 采用
`Google Style Guide <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`__。
我们使用 `Sphinx <https://www.sphinx-doc.org/en/master/>`__ 生成文档。
请确保你的代码有完善的文档说明，并遵循这些准则。

代码结构
^^^^^^^^

我们的代码库遵循特定的组织结构。这有助于维护代码库，也让它
更容易理解。

在 Python 文件中，我们遵循以下结构：

.. code:: python

   # Imports: These are sorted by the pre-commit hooks.
   # Constants
   # Functions (public)
   # Classes (public)
   # _Functions (private)
   # _Classes (private)

import 由 pre-commit 钩子进行排序。除非有充分理由，否则请不要
在函数或类内部导入模块。为处理循环导入，我们使用
:obj:`typing.TYPE_CHECKING` 变量。更多细节请参阅 `循环导入`_ 一节。

Python 没有私有类和公有类的概念。不过，我们遵循
给私有函数和类加上下划线前缀的约定。
公有函数和类是指打算供用户使用的函数和类。私有
函数和类是指打算在该文件内部使用的函数和类。
无论函数和类是公有还是私有，我们都遵循风格指南
编写代码，并确保代码与文档保持一致。

同样，在 Python 类内部，我们遵循以下结构：

.. code:: python

   # Constants
   # Class variables (public or private): Must have the type hint ClassVar[type]
   # Dunder methods: __init__, __del__
   # Representation: __repr__, __str__
   # Properties: @property
   # Instance methods (public)
   # Class methods (public)
   # Static methods (public)
   # _Instance methods (private)
   # _Class methods (private)
   # _Static methods (private)

经验法则是，类中的函数应按用户预期的使用顺序排列。例如，
如果类中包含 :meth:`initialize`、:meth:`reset`、
:meth:`update` 和 :meth:`close` 方法，那么就应按它们的调用顺序列出。
对于类中的私有函数也是如此。它们的顺序取决于在类内部的调用
顺序。

.. dropdown:: 代码骨架
   :icon: code

   .. literalinclude:: snippets/code_skeleton.py
      :language: python

循环导入
^^^^^^^^

循环导入发生在两个模块互相导入时，这是 Python 中的一个常见问题。
你可以通过遵循这篇
`StackOverflow 帖子 <https://stackoverflow.com/questions/744373/circular-or-cyclic-imports-in-python>`__ 中概述的最佳实践来避免循环导入。

总的来说，必须避免循环导入，因为它们可能导致不可预测的行为。

不过，在我们的代码库中，会在子包层面遇到循环导入。出现这种情况
是由于我们特定的代码结构。我们将类或函数及其对应的配置
对象组织到不同的文件中。这种分离提高了代码的可读性和可维护性。然而，
这也可能导致循环导入，因为在许多配置对象中，我们会分别使用 ``class_type`` 和 ``func``
属性将类或函数指定为默认值。

为解决循环导入问题，我们利用 `typing.TYPE_CHECKING
<https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING>`_ 变量。这个特殊变量
只在类型检查时被求值，使我们能够在配置对象中导入类或函数
而不触发循环导入。

需要注意的是，这是我们的代码库中唯一使用循环导入
且可被接受的情形。在所有其他场景中，我们都遵循最佳实践，并建议你也这样做。

类型标注
^^^^^^^^

为让代码更易读，我们为所有函数和类都使用
`类型标注 <https://docs.python.org/3/library/typing.html>`__。这有助于理解代码，也让它更容易维护。遵循
这一实践还有助于借助 `mypy <https://mypy.readthedocs.io/en/stable/>`__ 之类的静态类型检查器尽早发现 bug。

**只在函数签名中标注类型**

为避免重复劳动，我们不在 docstring 中为参数和返回值指定类型标注。

例如，以下示例因各种原因都是不好的做法：

.. code:: python

   def my_function(a, b):
      """Adds two numbers.

      This function is a bad example. Reason: No type hints anywhere.

      Args:
         a: The first argument.
         b: The second argument.

      Returns:
         The sum of the two arguments.
      """
      return a + b

.. code:: python

   def my_function(a, b):
      """Adds two numbers.

      This function is a bad example. Reason: Type hints in the docstring and not in the
      function signature.

      Args:
         a (int): The first argument.
         b (int): The second argument.

      Returns:
         int: The sum of the two arguments.
      """
      return a + b

.. code:: python

   def my_function(a: int, b: int) -> int:
      """Adds two numbers.

      This function is a bad example. Reason: Type hints in the docstring and in the function
      signature. Redundancy.

      Args:
         a (int): The first argument.
         b (int): The second argument.

      Returns:
         int: The sum of the two arguments.
      """
      return a + b

以下是我们期望的 docstring 与类型标注写法：

.. code:: python

   def my_function(a: int, b: int) -> int:
      """Adds two numbers.

      This function is a good example. Reason: Type hints in the function signature and not in the
      docstring.

      Args:
         a: The first argument.
         b: The second argument.

      Returns:
         The sum of the two arguments.
      """
      return a + b

**不为 None 标注类型**

我们不在 docstring 中指定 :obj:`None` 的返回类型。这是
因为没有必要，而且可以从函数签名中推断出来。

例如，以下是一个不好的示例：

.. code:: python

   def my_function(x: int | None) -> None:
      pass

相反，我们推荐以下写法：

.. code:: python

   def my_function(x: int | None):
      pass

编写代码文档
^^^^^^^^^^^^

代码文档与代码本身同样重要。它有助于理解代码，也让它
更容易维护。然而，文档往往被当作事后补充，或者为了
跟上开发节奏而仓促完成。

**什么算是不好的文档？**

* 如果别人想使用这些代码，仅通过阅读文档无法理解代码。

  这意味着文档不完整，或者写得不够易懂。
  下次有人想使用这些代码时，他们不得不花时间理解代码（最好的
  情况），或者干脆放弃这些代码、从头开始（最坏的情况）。

* 某些设计上的微妙之处没有被记录下来，只能从代码中看出。

  很多时候，某些设计决策是为了应对特定用例而做出的。这些用例对于
  想要使用这些代码的人来说并不明显。他们可能会以不直观的方式修改代码，
  从而无意中破坏它。

* 代码更新时文档没有同步更新。

  这意味着文档没有与代码保持同步。代码更新时同步更新
  文档很重要。这有助于让文档保持最新，并与代码
  保持一致。

**什么算是好的文档？**

我们建议把代码文档视为一份活的文档，帮助读者理解
代码的*是什么、为什么以及怎么做*。我们经常看到一些文档只解释了
是什么，却没有解释怎么做或为什么。从长远来看，这没有帮助。

我们建议始终从新用户的角度来思考文档。他们应该能够直接
查阅文档，就能很好地理解代码。

关于如何编写好文档的信息，请查看
`Dart 的有效文档 <https://dart.dev/effective-dart/documentation>`__
和 `技术写作 <https://en.wikiversity.org/wiki/Technical_writing/Style>`__ 的相关说明。
我们在下面总结了要点：

* 告知（教育读者）并说服（让读者信服）。
  * 心中要有明确的目标，并确保你所写的一切都只围绕这个目标。
  * 在引入抽象概念之前，先使用示例和类比。
* 使用适合受众的语气。
* 使用主动语态撰写简洁的句子。
* 避免不必要的术语和重复。使用平实的语言。
* 避免含糊的措辞，例如 "kind of"、"sort of"、"a bit" 等。
* 把重要信息放在句子开头。
* 准确表达你的意思。不要回避写出令人不适的事实。


单元测试
--------

我们使用 `pytest <https://docs.pytest.org>`__ 进行单元测试。
好的测试不仅覆盖代码的基本功能，还覆盖边界情况。
它们应该能够捕获回归，并确保代码按预期工作。
请确保为你的修改添加测试。

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code-block:: bash

         # Run all tests
         ./isaaclab.sh --test  # or "./isaaclab.sh -t"

         # Run all tests in a particular file
         ./isaaclab.sh -p -m pytest source/isaaclab/test/deps/test_torch.py

         # Run a particular test
         ./isaaclab.sh -p -m pytest source/isaaclab/test/deps/test_torch.py::test_array_slicing

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code-block:: bash

         # Run all tests
         isaaclab.bat --test  # or "isaaclab.bat -t"

         # Run all tests in a particular file
         isaaclab.bat -p -m pytest source/isaaclab/test/deps/test_torch.py

         # Run a particular test
         isaaclab.bat -p -m pytest source/isaaclab/test/deps/test_torch.py::test_array_slicing


工具
----

我们使用以下工具来维护代码质量：

* `pre-commit <https://pre-commit.com/>`__：对代码库运行一系列格式化和 lint 工具。
* `ruff <https://github.com/astral-sh/ruff/>`__：一个极其快速的 Python linter 和格式化工具。

请查看 `此处 <https://pre-commit.com/#install>`__ 了解
设置这些工具的说明。要对整个仓库运行，请在终端中执行
以下命令：

.. tab-set::
   :sync-group: os

   .. tab-item:: :icon:`fa-brands fa-linux` Linux
      :sync: linux

      .. code-block:: bash

         ./isaaclab.sh --format  # or "./isaaclab.sh -f"

   .. tab-item:: :icon:`fa-brands fa-windows` Windows
      :sync: windows

      .. code-block:: bash

         isaaclab.bat --format  # or "isaaclab.bat -f"
