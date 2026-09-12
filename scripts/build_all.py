#!/usr/bin/env python3
"""Build the portal and every project docs tree into site/."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = ROOT / "docs"
PORTAL_ROOT = ROOT / "portal"
SITE_ROOT = ROOT / "site"

# Reuse per-project builder
sys.path.insert(0, str(ROOT / "scripts"))
from build_project import build_language, load_meta  # noqa: E402


def discover_projects() -> list[str]:
  if not DOCS_ROOT.is_dir():
    return []
  projects = []
  for path in sorted(DOCS_ROOT.iterdir()):
    if path.is_dir() and (path / "meta.yaml").is_file():
      projects.append(path.name)
  return projects


def write_projects_json(projects: list[dict], dest: Path) -> None:
  dest.write_text(json.dumps(projects, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def copy_portal(projects: list[dict]) -> None:
  if not PORTAL_ROOT.is_dir():
    raise FileNotFoundError(f"Missing portal directory: {PORTAL_ROOT}")

  SITE_ROOT.mkdir(parents=True, exist_ok=True)
  for item in PORTAL_ROOT.iterdir():
    target = SITE_ROOT / item.name
    if item.is_dir():
      if target.exists():
        shutil.rmtree(target)
      shutil.copytree(item, target)
    else:
      shutil.copy2(item, target)

  write_projects_json(projects, SITE_ROOT / "projects.json")


def project_card(meta: dict) -> dict:
  langs = []
  for code, info in meta.get("languages", {}).items():
    langs.append(
      {
        "code": code,
        "label": info.get("label", code),
        "href": f"./{meta['id']}/{code}/",
      }
    )
  return {
    "id": meta["id"],
    "title": meta.get("title", meta["id"]),
    "summary": meta.get("summary", ""),
    "summary_zh": meta.get("summary_zh", meta.get("summary", "")),
    "upstream": meta.get("upstream"),
    "api_mode": meta.get("api_mode", "collection"),
    "languages": langs,
  }


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--clean", action="store_true", help="Wipe site/ before building")
  parser.add_argument(
    "--projects",
    nargs="*",
    help="Subset of project ids (default: all with meta.yaml)",
  )
  args = parser.parse_args()

  if args.clean and SITE_ROOT.exists():
    shutil.rmtree(SITE_ROOT)

  project_ids = args.projects or discover_projects()
  if not project_ids:
    raise SystemExit("No projects found under docs/*/meta.yaml")

  cards: list[dict] = []
  for project_id in project_ids:
    meta = load_meta(project_id)
    for lang, lang_meta in meta["languages"].items():
      build_language(project_id, lang, lang_meta, clean=True)
    cards.append(project_card(meta))

  copy_portal(cards)
  print(f"[ok] site ready at {SITE_ROOT} ({len(cards)} project(s))")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
