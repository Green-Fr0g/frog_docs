project = "__TITLE__"
copyright = "The frog_docs contributors"
author = "frog_docs"

extensions = [
  "myst_parser",
  "sphinx_copybutton",
  "sphinx_design",
]

source_suffix = {
  ".rst": "restructuredtext",
  ".md": "markdown",
}

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
language = "zh_CN"
html_title = "__TITLE__ 文档"
html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_theme_options = {
  "collapse_navigation": True,
  "show_toc_level": 2,
  "logo": {"text": "__TITLE__ 中文文档"},
}
templates_path = ["_templates"]
