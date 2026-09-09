#!/usr/bin/env python3
"""
Basin Watch static build.

Substitutes data/bundle.json into site/shell.html and site/explorer-shell.html,
writing dist/index.html and dist/explorer/index.html. Deterministic, no model
involved - this is the fix for the drift/breakage history documented in the
Basin Watch project's open-items.md (dead references, stripped <script> tags,
swatch-colour drift, etc.), all of which came from editing the ~7MB rendered
page as text instead of rebuilding it from a template + data split.

Usage:
    python3 scripts/build.py

Verifies, for each output page, before writing:
  - exactly two <script> tags survive
  - the substituted bundle re-parses as JSON (via raw_decode, not a greedy regex -
    see the project's map-pipeline.md for why a naive regex over-matches on a
    file this size)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DATA = ROOT / "data"
DIST = ROOT / "dist"

PLACEHOLDER = "/*__BUNDLE__*/"
BUNDLE_PREFIX = "<script>window.BASIN_BUNDLE="


def load_bundle() -> dict:
    with open(DATA / "bundle.json", "r", encoding="utf-8") as f:
        return json.load(f)


def render(shell_path: Path, bundle_json: str) -> str:
    shell = shell_path.read_text(encoding="utf-8")
    if PLACEHOLDER not in shell:
        raise SystemExit(f"{shell_path}: placeholder {PLACEHOLDER!r} not found")
    if shell.count(PLACEHOLDER) != 1:
        raise SystemExit(f"{shell_path}: expected exactly one placeholder")
    out = shell.replace(PLACEHOLDER, bundle_json, 1)

    # verify exactly two <script> tags survive
    n_scripts = out.count("<script>")
    if n_scripts != 2:
        raise SystemExit(f"{shell_path}: expected 2 <script> tags after build, found {n_scripts}")

    # verify the bundle re-parses as JSON, using raw_decode rather than a greedy
    # regex (a naive regex over-matches past the real end of the object on a
    # file this size - see map-pipeline.md)
    idx = out.index(BUNDLE_PREFIX)
    json_start = idx + len(BUNDLE_PREFIX)
    decoder = json.JSONDecoder()
    try:
        _, end = decoder.raw_decode(out, json_start)
    except json.JSONDecodeError as e:
        raise SystemExit(f"{shell_path}: bundle failed to re-parse as JSON: {e}")
    tail = out[end:end + 10]
    if not tail.lstrip().startswith(";</script>"):
        raise SystemExit(f"{shell_path}: unexpected content after bundle: {tail!r}")

    return out


def main() -> None:
    bundle = load_bundle()
    bundle_json = json.dumps(bundle, separators=(",", ":"))

    DIST.mkdir(exist_ok=True)
    (DIST / "explorer").mkdir(exist_ok=True)

    main_html = render(SITE / "shell.html", bundle_json)
    (DIST / "index.html").write_text(main_html, encoding="utf-8")
    print(f"wrote dist/index.html ({len(main_html):,} bytes)")

    explorer_html = render(SITE / "explorer-shell.html", bundle_json)
    (DIST / "explorer" / "index.html").write_text(explorer_html, encoding="utf-8")
    print(f"wrote dist/explorer/index.html ({len(explorer_html):,} bytes)")

    print(f"bundle: {bundle.get('generated')}, {len(bundle.get('tenure', [])):,} tenure records, "
          f"{len(bundle.get('news', [])):,} news waypoints")


if __name__ == "__main__":
    main()
