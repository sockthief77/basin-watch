#!/usr/bin/env python3
"""
Basin Watch static build.

Substitutes data/bundle.json (map layers) and data/edition.json (the day's
brief text - masthead date, ranked news, notes, archive row) into
site/shell.html, and data/bundle.json into site/explorer-shell.html, writing
dist/index.html and dist/explorer/index.html. Deterministic, no model
involved - this is the fix for the drift/breakage history documented in the
Basin Watch project's open-items.md (dead references, stripped <script> tags,
swatch-colour drift, etc.), all of which came from editing the ~7MB rendered
page as text instead of rebuilding it from a template + data split.

data/edition.json was introduced 2026-09-10 to close the gap where the daily
brief's news section was static HTML seeded once and never updated
automatically - see claude/map-pipeline.md and claim-monitor-state.md in the
Basin Watch project for the history. It's populated by
scripts/merge_edition.py, run by .github/workflows/publish-brief.yml shortly
after the daily brief skill publishes its Artifact pages each morning.

Usage:
    python3 scripts/build.py

Verifies, for the main page, before writing:
  - exactly two <script> tags survive
  - the substituted bundle re-parses as JSON (via raw_decode, not a greedy regex -
    see the project's map-pipeline.md for why a naive regex over-matches on a
    file this size)
  - both edition placeholders were found exactly once and got substituted
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DATA = ROOT / "data"
DIST = ROOT / "dist"

BUNDLE_PLACEHOLDER = "/*__BUNDLE__*/"
BUNDLE_PREFIX = "<script>window.BASIN_BUNDLE="
EDITION_TOP_PLACEHOLDER = "<!--__EDITION_TOP__-->"
EDITION_BOTTOM_PLACEHOLDER = "<!--__EDITION_BOTTOM__-->"


def load_json(name: str) -> dict:
    with open(DATA / name, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def substitute_once(shell: str, placeholder: str, value: str, label: str) -> str:
    if placeholder not in shell:
        raise SystemExit(f"{label}: placeholder {placeholder!r} not found")
    if shell.count(placeholder) != 1:
        raise SystemExit(f"{label}: expected exactly one {placeholder!r}, found {shell.count(placeholder)}")
    return shell.replace(placeholder, value, 1)


def render(shell_path: Path, bundle_json: str, edition: dict | None) -> str:
    shell = shell_path.read_text(encoding="utf-8")
    label = str(shell_path)

    if edition is not None:
        shell = substitute_once(shell, EDITION_TOP_PLACEHOLDER, edition["edition_top_html"], label)
        shell = substitute_once(shell, EDITION_BOTTOM_PLACEHOLDER, edition["edition_bottom_html"], label)

    out = substitute_once(shell, BUNDLE_PLACEHOLDER, bundle_json, label)

    # verify exactly two <script> tags survive
    n_scripts = out.count("<script>")
    if n_scripts != 2:
        raise SystemExit(f"{label}: expected 2 <script> tags after build, found {n_scripts}")

    # verify the bundle re-parses as JSON, using raw_decode rather than a greedy
    # regex (a naive regex over-matches past the real end of the object on a
    # file this size - see map-pipeline.md)
    idx = out.index(BUNDLE_PREFIX)
    json_start = idx + len(BUNDLE_PREFIX)
    decoder = json.JSONDecoder()
    try:
        _, end = decoder.raw_decode(out, json_start)
    except json.JSONDecodeError as e:
        raise SystemExit(f"{label}: bundle failed to re-parse as JSON: {e}")
    tail = out[end:end + 10]
    if not tail.lstrip().startswith(";</script>"):
        raise SystemExit(f"{label}: unexpected content after bundle: {tail!r}")

    return out


def main() -> None:
    bundle = load_json("bundle.json")
    bundle_json = json.dumps(bundle, separators=(",", ":"))
    edition = load_json("edition.json")

    required = {"generated", "edition", "edition_top_html", "edition_bottom_html"}
    missing = required - edition.keys()
    if missing:
        raise SystemExit(f"data/edition.json missing keys: {missing}")
    if not edition["edition_top_html"].strip() or not edition["edition_bottom_html"].strip():
        raise SystemExit("data/edition.json has an empty edition_top_html or edition_bottom_html - refusing to build")

    DIST.mkdir(exist_ok=True)
    (DIST / "explorer").mkdir(exist_ok=True)

    main_html = render(SITE / "shell.html", bundle_json, edition)
    (DIST / "index.html").write_text(main_html, encoding="utf-8")
    print(f"wrote dist/index.html ({len(main_html):,} bytes)")

    explorer_html = render(SITE / "explorer-shell.html", bundle_json, None)
    (DIST / "explorer" / "index.html").write_text(explorer_html, encoding="utf-8")
    print(f"wrote dist/explorer/index.html ({len(explorer_html):,} bytes)")

    # Cloudflare's static asset server doesn't reliably declare charset=utf-8
    # on its own, and without it browsers fall back to guessing the encoding -
    # which garbles every non-ASCII character on the page (U3O8 subscripts,
    # en dashes, etc). Force it explicitly for every response.
    headers_path = DIST / "_headers"
    headers_path.write_text("/*\n  Content-Type: text/html; charset=utf-8\n", encoding="utf-8")
    print("wrote dist/_headers")

    print(f"bundle: {bundle.get('generated')}, {len(bundle.get('tenure', [])):,} tenure records, "
          f"{len(bundle.get('news', [])):,} news waypoints")
    print(f"edition: {edition.get('generated')}, No. {edition.get('edition')}")


if __name__ == "__main__":
    main()
