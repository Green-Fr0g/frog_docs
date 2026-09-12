import os
import sys

import sphinx_book_theme

sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, os.path.abspath("../src/mjlab"))


project = "mjlab"
copyright = "2025, The mjlab Developers"
author = "The mjlab Developers"

extensions = [
  "sphinx.ext.autodoc",
  "sphinx.ext.autosummary",
  "autodocsumm",
  "myst_parser",
  "sphinx.ext.napoleon",
  "sphinxemoji.sphinxemoji",
  "sphinx.ext.intersphinx",
  "sphinx.ext.mathjax",
  "sphinx.ext.todo",
  "sphinx.ext.viewcode",
  "sphinxcontrib.bibtex",
  "sphinx_copybutton",
  "sphinx_design",
  "sphinx_tabs.tabs",
  "sphinx.ext.extlinks",
]

extlinks = {
  "issue": (
    "https://github.com/mujocolab/mjlab/issues/%s",
    "#%s",
  ),
}

mathjax3_config = {
  "tex": {
    "inlineMath": [["\\(", "\\)"]],
    "displayMath": [["\\[", "\\]"]],
  },
}

panels_add_bootstrap_css = False
panels_add_fontawesome_css = True

source_suffix = {
  ".rst": "restructuredtext",
  ".md": "markdown",
}

nitpick_ignore = [
  ("py:obj", "slice(None)"),
]

nitpick_ignore_regex = [
  (r"py:.*", r"pxr.*"),
  (r"py:.*", r"trimesh.*"),
]

# emoji style
sphinxemoji_style = "twemoji"
autodoc_typehints = "signature"
autoclass_content = "class"
autodoc_class_signature = "separated"
autodoc_member_order = "bysource"
autodoc_inherit_docstrings = True
bibtex_bibfiles = ["source/_static/refs.bib"]
autosummary_generate = True
autosummary_generate_overwrite = False
autodoc_default_options = {
  "member-order": "bysource",
}
intersphinx_mapping = {
  "python": ("https://docs.python.org/3", None),
}

exclude_patterns = [
  "_build",
  "_redirect",
  "_templates",
  "Thumbs.db",
  ".DS_Store",
  "README.md",
  "licenses/*",
  # Collection mode: skip autodoc API pages; link to upstream instead.
  "source/api",
  "source/api/*",
]

# Kept for any residual autodoc directives outside source/api.
autodoc_mock_imports = [
  "mjlab",
  "torch",
  "numpy",
  "matplotlib",
  "scipy",
  "carb",
  "warp",
  "pxr",
  "h5py",
  "hid",
  "prettytable",
  "tqdm",
  "tensordict",
  "trimesh",
  "toml",
  "mjviser",
  "mujoco",
  "mujoco_warp",
  "gymnasium",
  "rsl_rl",
  "viser",
  "wandb",
  "torchvision",
]

suppress_warnings = [
  "ref.python",
  "docutils",
]

language = "zh_CN"

html_title = "mjlab 文档"
html_theme_path = [sphinx_book_theme.get_html_theme_path()]
html_theme = "sphinx_book_theme"
html_favicon = "source/_static/favicon.ico"
html_show_copyright = True
html_show_sphinx = False
html_last_updated_fmt = ""

html_static_path = ["source/_static"]
html_css_files = ["css/custom.css"]
html_js_files = ["js/color_mode_cycle.js"]

html_theme_options = {
  "path_to_docs": "docs_zh_CN/",
  "collapse_navigation": True,
  "repository_url": "https://github.com/mujocolab/mjlab",
  "use_repository_button": True,
  "use_issues_button": True,
  "use_edit_page_button": False,
  "show_toc_level": 2,
  "use_sidenotes": True,
  "logo": {
    "text": "mjlab 中文文档",
  },
  "icon_links": [
    {
      "name": "Benchmarks",
      "url": "https://mujocolab.github.io/mjlab/nightly/",
      "icon": "fa-solid fa-chart-line",
      "type": "fontawesome",
    },
  ],
  "icon_links_label": "快速链接",
}

templates_path = [
  "_templates",
]

html_sidebars = {
  "**": [
    "navbar-logo.html",
    "search-field.html",
    "sbt-sidebar-nav.html",
  ]
}


def skip_member(app, what, name, obj, skip, options):
  exclusions = ["from_dict", "to_dict", "replace", "copy", "validate", "__post_init__"]
  if name in exclusions:
    return True
  return None


def process_signature(app, what, name, obj, options, signature, return_annotation):
  """Suppress the ugly __init__ signature for dataclass Cfg classes."""
  if what == "class" and "exclude-members" in options:
    if "__init__" in options["exclude-members"]:
      return ("", None)
  return None


def process_docstring(app, what, name, obj, options, lines):
  """Strip auto-generated dataclass docstrings (e.g. 'ClassName(*, ...)')."""
  import dataclasses

  if what == "class" and dataclasses.is_dataclass(obj):
    if lines and lines[0].startswith(f"{obj.__name__}("):
      lines.clear()


def setup(app):
  app.connect("autodoc-skip-member", skip_member)
  app.connect("autodoc-process-signature", process_signature)
  app.connect("autodoc-process-docstring", process_docstring)
