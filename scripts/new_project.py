#!/usr/bin/env python3
"""Scaffold a new docs/<project> tree from templates/project."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "project"
DOCS_ROOT = ROOT / "docs"

VALID_ID = re.compile(r"^[a-z][a-z0-9_-]*$")


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("project_id", help="Directory name under docs/, e.g. mylib")
  parser.add_argument("--title", help="Display title (default: project_id)")
  parser.add_argument(
    "--upstream",
    default="",
    help="Upstream repository URL",
  )
  args = parser.parse_args()

  project_id = args.project_id
  if not VALID_ID.match(project_id):
    raise SystemExit("project_id must match ^[a-z][a-z0-9_-]*$")

  if not TEMPLATE.is_dir():
    raise SystemExit(f"Missing template directory: {TEMPLATE}")

  dest = DOCS_ROOT / project_id
  if dest.exists():
    raise SystemExit(f"Already exists: {dest}")

  title = args.title or project_id
  shutil.copytree(TEMPLATE, dest)

  meta_path = dest / "meta.yaml"
  meta = meta_path.read_text(encoding="utf-8")
  meta = meta.replace("__PROJECT_ID__", project_id)
  meta = meta.replace("__TITLE__", title)
  meta = meta.replace("__UPSTREAM__", args.upstream)
  meta_path.write_text(meta, encoding="utf-8")

  for conf in dest.glob("*/conf.py"):
    text = conf.read_text(encoding="utf-8")
    conf.write_text(
      text.replace("__PROJECT_ID__", project_id).replace("__TITLE__", title),
      encoding="utf-8",
    )

  for index in dest.glob("*/index.rst"):
    text = index.read_text(encoding="utf-8")
    index.write_text(text.replace("__TITLE__", title), encoding="utf-8")

  print(f"[ok] created {dest}")
  print("Next: edit meta.yaml and Sphinx sources, then run scripts/build_all.py")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
