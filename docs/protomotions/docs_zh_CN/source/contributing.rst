参与贡献
============

欢迎！很高兴你有兴趣为 ProtoMotions 做贡献。

这个项目依靠社区的力量发展。无论是修复一个错别字、添加一个功能，还是分享你的研究——每一份贡献都很重要。

参与方式
------------------

可以帮助的方式有很多，而且你不需要是专家：

**分享你的成果**
   在项目或论文中使用了 ProtoMotions？欢迎告诉我们！我们很乐意展示你的工作。

**报告问题**
   发现了 bug？文档里有让人困惑的地方？请 `提交 issue <https://github.com/NVLabs/ProtoMotions/issues>`_ 并告诉我们。

**改进文档**
   发现错别字？对某个内容有更好的讲解思路？文档改进永远受欢迎。

**添加示例**
   创建了很棒的实验配置或训练方案？欢迎分享给其他人。

**修复 bug**
   浏览 `开放的问题 <https://github.com/NVLabs/ProtoMotions/issues>`_，挑一个你感兴趣的入手。

**添加功能**
   对新功能有想法？先开一个 issue 讨论，然后再提交 PR。

上手步骤
---------------

1. 在 GitHub 上 **fork 本仓库**

2. **克隆你 fork 的仓库**：

   .. code-block:: bash

      git clone https://github.com/YOUR_USERNAME/ProtoMotions.git
      cd ProtoMotions

3. 为你的改动 **创建一个分支**：

   .. code-block:: bash

      git checkout -b my-contribution

4. **完成修改** 并测试

5. **提交**，附上清晰的提交信息（并签名）：

   .. code-block:: bash

      git commit -s -m "Add feature X"

6. **推送** 到你的 fork：

   .. code-block:: bash

      git push origin my-contribution

7. 在 GitHub 上 **发起 Pull Request**

就是这样！我们会审阅你的 PR，并协助你完成合并。

为提交签名
--------------------

我们要求所有贡献者对提交进行"签名"（sign-off）。这证明该贡献是你的原创工作，或者你有权在同样的许可下提交它。

为提交签名，使用 ``--signoff``（或 ``-s``）选项：

.. code-block:: bash

   git commit -s -m "Add cool feature"

这会在提交信息末尾追加：

.. code-block:: text

   Signed-off-by: Your Name <your@email.com>

**注意：** 包含未签名提交的贡献将不会被接受。

代码风格
----------

我们使用 `pre-commit <https://pre-commit.com/>`_ 自动格式化和检查代码。设置方法：

.. code-block:: bash

   pip install pre-commit
   pre-commit install

这会在每次提交时运行以下检查：

* **Ruff**：代码检查与格式化（替代 black、isort、flake8）
* **Typos**：拼写检查
* 插入许可证头部
* 修掉行尾空白和文件末尾换行

你也可以手动运行这些检查：

.. code-block:: bash

   pre-commit run --all-files

除了自动化格式之外：

* 使用有意义的变量和函数命名
* 为新增的函数和类添加 docstring
* 保持提交聚焦——每个提交只包含一个逻辑改动

别担心不够完美。我们很乐意在评审过程中帮你打磨贡献。

Pull Request 建议
-----------------

* **保持 PR 聚焦**：一个 PR 只做一个功能或修复，更容易评审
* **描述你的改动**：帮助评审者理解你做了什么、为什么这样做
* **测试你的改动**：提交前确保一切正常工作
* **保持耐心**：我们会尽快处理你的 PR

有疑问？
----------

不知道从哪里入手？对代码库有疑问？

* 在 `GitHub Discussion <https://github.com/NVLabs/ProtoMotions/discussions>`_ 发帖
* 查看已有 issue 中是否有类似问题
* 卡住了就在你的 PR 里留言

我们随时提供帮助。别犹豫，尽管问！

致谢
----------

每一份贡献——无论大小——都在让 ProtoMotions 变得更好。感谢你成为这个项目的一员！
