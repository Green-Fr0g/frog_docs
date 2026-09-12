参与贡献
========

欢迎随时提交 Bug 修复和文档改进。

.. important::

   对于新功能，请先 `提交 issue <https://github.com/mujocolab/mjlab/issues>`_ 与我们讨论，确认它是否符合项目范围。


开发环境搭建
------------

克隆仓库并同步依赖：

.. code-block:: bash

   git clone https://github.com/mujocolab/mjlab.git && cd mjlab
   uv sync

安装 pre-commit 钩子，以便在每次提交前发现格式和 lint 问题：

.. code-block:: bash

   uvx pre-commit install


常用命令
--------

``Makefile`` 为最常见的开发任务提供了快捷方式：

.. code-block:: bash

   make format      # Format code and fix lint errors (ruff)
   make type        # Type check (ty + pyright)
   make check       # Format + type check
   make test-fast   # Run tests, excluding slow ones
   make test        # Run the full test suite
   make test-all    # Format + type check + full test suite

也可以单独运行某个测试以加快迭代：

.. code-block:: bash

   uv run pytest tests/test_rewards.py

类型检查 (``make type``) 是必需的。未通过的 PR 会被阻止合并。


构建文档
--------

在本地构建文档：

.. code-block:: bash

   make docs

HTML 输出会写入 ``docs/_build/``。编辑时如需实时刷新：

.. code-block:: bash

   make docs-watch


提交拉取请求
------------

1. 复刻 (fork) 仓库并创建功能分支。
2. 进行修改。
3. 运行 ``make test-all``，验证格式、类型检查和测试全部通过。
4. 按照 `Keep a Changelog <https://keepachangelog.com/>`_ 的约定，在
   ``docs/source/changelog.rst`` 的 “Upcoming version” 小节中，按相应
   类别（Added / Changed / Fixed）添加条目。
5. 提交拉取请求。


使用 Claude Code 进行开发
-------------------------

仓库根目录包含一个 ``CLAUDE.md`` 文件。该文件为
`Claude Code <https://claude.com/claude-code>`_ 定义了开发约定、风格
指南和常用命令。由于它记录了 CI 中强制执行的同一套规则，对人类贡献者
同样是有用的参考。

项目还在 ``.claude/commands/`` 中提供了一些共享命令。任何安装了
Claude Code 的贡献者都可以把它们作为斜杠命令调用。

``/update-mjwarp <commit-hash>``
   把 ``mujoco-warp`` 依赖更新到指定的 commit。它会一步完成编辑
   ``pyproject.toml``、运行 ``uv lock`` 并打开 PR。

   .. code-block:: text

      /update-mjwarp e28c6038cdf8a353b4146974e4cf37e74dda809a

``/commit-push-pr``
   暂存当前修改，提交、推送并打开 PR。
