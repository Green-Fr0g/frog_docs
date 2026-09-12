# frog_docs

多项目文档收集库：汇总各项目的原版与中文文档，构建为可本地预览、可部署的静态站点。

当前已收录：**mjlab**、**sonic**（GR00T-WholeBodyControl）、**protomotions**、**isaaclab**（Isaac Lab）（均为英文原版 + 中文译文）。

## 快速开始

```bash
uv sync
uv run python scripts/build_all.py
uv run python -m http.server -d site 8000
```

浏览器打开 <http://127.0.0.1:8000> 。

| 路径 | 内容 |
|------|------|
| `/` | 门户首页 |
| `/mjlab/en/` | mjlab 英文文档 |
| `/mjlab/zh-CN/` | mjlab 中文文档 |
| `/sonic/en/` | sonic（GR00T-WholeBodyControl）英文文档 |
| `/sonic/zh-CN/` | sonic 中文文档 |
| `/protomotions/en/` | protomotions 英文文档 |
| `/protomotions/zh-CN/` | protomotions 中文文档 |
| `/isaaclab/en/` | Isaac Lab 英文文档 |
| `/isaaclab/zh-CN/` | Isaac Lab 中文文档 |

## 仓库结构

```text
portal/                 # 站点首页
docs/<project>/         # 各项目文档源
  meta.yaml             # 项目元数据（含各语言的 Sphinx 源根目录）
  docs/ 或 en/          # 英文 Sphinx 源
  docs_zh_CN/ 或 zh-CN/ # 中文 Sphinx 源
scripts/                # 构建与脚手架
site/                   # 构建产物（不入库）
```

各项目 `meta.yaml` 的 `languages.<code>.root` 指定 **Sphinx `conf.py` 所在目录**
（即 `sphinx-build` 的 srcdir），需要指向实际存放 `conf.py` / `index.rst` 的那一层：

| 项目 | 英文 root | 中文 root |
|------|-----------|-----------|
| mjlab | `docs` | `docs_zh_CN` |
| isaaclab | `docs` | `docs_zh_CN` |
| sonic | `docs/source` | `docs_zh_CN/source` |
| protomotions | `docs/source` | `docs_zh_CN/source` |

## API 文档策略

本仓库是**文档收集库**，不捆绑上游 Python 源码。各项目按上游 `conf.py` 的既有配置分别处理：

| 项目 | 本地 API 页 | 说明 |
|------|-------------|------|
| mjlab | 跳过 | `conf.py` 的 `exclude_patterns` 排除 `source/api`，API 参考链接到[上游文档](https://mujocolab.github.io/mjlab/source/api/index.html) |
| sonic | 跳过 | `conf.py` 的 `exclude_patterns` 排除 `api` |
| isaaclab | 跳过 | 上游 `autosummary_generate = True` 会在 `builder-inited` 阶段 `import isaaclab`，无源码时直接中止构建；故 `exclude_patterns` 排除 `source/api`，API 参考见[上游文档](https://isaaclab.sh/docs/) |
| protomotions | 跳过 | `conf.py` 的 `exclude_patterns` 排除 `api_reference`（上游本可借 `autodoc_mock_imports` 构建，收集库统一不发布本地 API） |

需要切换策略时，改对应 `conf.py` 的 `exclude_patterns` 即可，源文件无需删除。

## 上游文档适配记录

部分项目在收集库场景下需要少量调整（均已在源码中注明）：

| 项目 | 文件 | 调整 | 原因 |
|------|------|------|------|
| isaaclab | `VERSION`（新增） | 从上游取当前版本号 `2.3.2` | `docs/conf.py` 会读取 `../VERSION`，但文档目录内不含该文件，缺失即构建失败 |
| isaaclab | `docs/conf.py`、`docs_zh_CN/conf.py` | 移除 `sphinx_multiversion` 扩展与 `smv_*` 配置，侧栏去掉版本切换器 | 该扩展要求多版本 git 标签，收集库只有一个 `main` 分支 |
| isaaclab | `docs/conf.py`、`docs_zh_CN/conf.py` | `exclude_patterns` 排除 `source/api` | 见上方 API 策略；`autosummary` 无法导入不存在的 `isaaclab` 包 |
| isaaclab | `docs_zh_CN/conf.py` | `language = "en"` → `"zh_CN"` | 否则中文站导出英文搜索索引 |
| protomotions | `docs_zh_CN/source/conf.py` | `language = "en"` → `"zh_CN"` | 同上 |
| sonic、protomotions | `conf.py` 的 `exclude_patterns` 与 `suppress_warnings` | 排除 `api` / `api_reference`，并抑制 `ref.doc` 警告 | 统一为「不发布本地 API」策略，与 mjlab、isaaclab 一致 |
| sonic、isaaclab、protomotions | 各自 `conf.py` 的 `html_js_files`；新增 `_static/js/color_mode_cycle.js`；三者均在 `custom.css` 隐藏下拉菜单 | 主题按钮由「下拉选择」改为「点击循环」：light → dark → auto | 统一全站交互，与 mjlab 保持一致（mjlab 上游自带该定制，此处把同一脚本复制到其余三个项目） |

## 添加新项目

1. 在 `docs/<project_id>/` 放入 Sphinx 文档（建议双语目录）。
2. 编写 `docs/<project_id>/meta.yaml`，其中 `languages.<code>.root` 指向含 `conf.py` 的目录。
3. 运行 `uv run python scripts/build_all.py` 验证。

也可使用脚手架：

```bash
uv run python scripts/new_project.py <project_id> --title "Display Name"
```

## 部署

推送到 `main` 后，GitHub Actions 会构建并发布到 GitHub Pages（需在仓库 Settings → Pages 中启用 GitHub Actions 作为源）。
