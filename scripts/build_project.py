#!/usr/bin/env python3
"""Build a single project's Sphinx docs for one or all languages."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = ROOT / "docs"
SITE_ROOT = ROOT / "site"


def load_meta(project_id: str) -> dict:
  meta_path = DOCS_ROOT / project_id / "meta.yaml"
  if not meta_path.is_file():
    raise FileNotFoundError(f"Missing meta.yaml: {meta_path}")
  with meta_path.open(encoding="utf-8") as f:
    meta = yaml.safe_load(f) or {}
  meta.setdefault("id", project_id)
  if "languages" not in meta:
    raise ValueError(f"{meta_path} must define languages")
  return meta


def build_language(project_id: str, lang: str, lang_meta: dict, *, clean: bool) -> Path:
  src_root = DOCS_ROOT / project_id / lang_meta["root"]
  conf = src_root / "conf.py"
  if not conf.is_file():
    raise FileNotFoundError(f"Sphinx conf.py not found: {conf}")

  out_dir = SITE_ROOT / project_id / lang
  if clean and out_dir.exists():
    shutil.rmtree(out_dir)
  out_dir.mkdir(parents=True, exist_ok=True)

  doctree_dir = ROOT / ".cache" / "doctrees" / project_id / lang
  doctree_dir.mkdir(parents=True, exist_ok=True)

  # Collection mode uses autodoc mocks; do not treat warnings as errors.
  cmd = [
    sys.executable,
    "-m",
    "sphinx",
    "-b",
    "html",
    "-d",
    str(doctree_dir),
    str(src_root),
    str(out_dir),
  ]
  print(f"[build] {project_id}/{lang}: {' '.join(cmd)}", flush=True)
  result = subprocess.run(cmd, cwd=ROOT)
  if result.returncode != 0:
    raise RuntimeError(f"Sphinx build failed for {project_id}/{lang} (exit {result.returncode})")
  return out_dir


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("project", help="Project id under docs/")
  parser.add_argument(
    "--lang",
    action="append",
    dest="langs",
    help="Language code to build (repeatable). Default: all languages in meta.yaml",
  )
  parser.add_argument("--clean", action="store_true", help="Remove output dir before build")
  args = parser.parse_args()

  meta = load_meta(args.project)
  languages = meta["languages"]
  selected = args.langs or list(languages.keys())

  for lang in selected:
    if lang not in languages:
      raise SystemExit(f"Unknown language '{lang}' for {args.project}. Known: {', '.join(languages)}")
    build_language(args.project, lang, languages[lang], clean=args.clean)

  print(f"[ok] built {args.project}: {', '.join(selected)}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
