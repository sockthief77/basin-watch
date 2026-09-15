#!/usr/bin/env python3
"""
Applies every shared block tracked by check_site_drift.py's CHECKS list from a
source-of-truth file onto one or more target files, in place.

Why this exists (2026-09-15): this repo's map engine exists as up to four separate
copies - site/shell.html, site/explorer-shell.html, and two live claude.ai artifacts
(Basin Watch, Basin Explorer) that this repo can't read or write directly. Every fix to
a value both pages/artifacts share (a colour, a threshold, a whole behavior block like
the archive-list collapse) used to mean hand-writing a one-off Python script that finds
the old string in each target and replaces it with the new one - easy to typo, easy to
introduce a spurious difference (this is how a literal '\\u25B4' escape ended up in an
artifact where site/shell.html had the same character written literally - functionally
identical, but a byte-for-byte drift check-site_drift.py --against correctly flags).
This script collapses that into one command: point it at the source of truth and
whichever targets need the same blocks, and it applies check_site_drift.py's own
CHECKS list (the same ~20 named blocks that script already verifies) mechanically,
using the SOURCE's exact matched text - never a hand-retyped copy of it - as the
replacement.

This is deliberately narrow: it only touches the specific named blocks CHECKS already
tracks, not a general HTML/JS diff/merge. A target missing a block entirely (never had
it) is reported and left alone, not grafted in blind - the same "sync values, don't
invent features" boundary check_site_drift.py itself observes. After running this,
re-run check_site_drift.py --against on the same targets to confirm zero drift, and
run the project's usual headless-browser verification before publishing an artifact -
this script only edits text, it never checks the result still runs.

Usage:
    python3 scripts/sync_shared_blocks.py TARGET [TARGET ...]
    python3 scripts/sync_shared_blocks.py --source site/explorer-shell.html TARGET [...]
    python3 scripts/sync_shared_blocks.py --dry-run TARGET [...]

    Source defaults to site/shell.html. Each TARGET is rewritten in place (unless
    --dry-run) only if at least one block actually changed. Exits non-zero if any
    target still has a real difference after applying (i.e. something CHECKS tracks
    that isn't a clean find/replace - shouldn't normally happen, but don't trust a
    silent partial apply).
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_site_drift import CHECKS, ROOT, SHELL  # noqa: E402


def load(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"missing file: {path}")
    return path.read_text(encoding="utf-8")


def label(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def apply_blocks(source_html: str, target_html: str):
    """Returns (new_target_html, list of (name, status) tuples).
    status is one of: 'updated', 'already in sync', 'not found in target', 'not found in source'."""
    new_html = target_html
    report = []
    for name, pattern in CHECKS:
        m_src = re.search(pattern, source_html)
        if m_src is None:
            report.append((name, "not found in source"))
            continue
        m_tgt = re.search(pattern, new_html)
        if m_tgt is None:
            report.append((name, "not found in target"))
            continue
        if m_tgt.group(0) == m_src.group(0):
            report.append((name, "already in sync"))
            continue
        src_text = m_src.group(0)
        start, end = m_tgt.span(0)
        new_html = new_html[:start] + src_text + new_html[end:]
        report.append((name, "updated"))
    return new_html, report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", type=Path, default=SHELL, help="Source-of-truth file (default: site/shell.html)")
    ap.add_argument("--dry-run", action="store_true", help="Report what would change, write nothing")
    ap.add_argument("targets", nargs="+", type=Path)
    args = ap.parse_args()

    source_html = load(args.source)
    source_label = label(args.source)

    any_unresolved = False
    for target_path in args.targets:
        target_html = load(target_path)
        new_html, report = apply_blocks(source_html, target_html)
        target_label = label(target_path)

        updated = [n for n, s in report if s == "updated"]
        missing = [n for n, s in report if s == "not found in target"]

        print(f"-- {target_label} (source: {source_label}) --")
        if updated:
            print(f"  updated: {len(updated)}")
            for n in updated:
                print(f"    - {n}")
        if missing:
            print(f"  not found in target (left alone, not inserted): {len(missing)}")
            for n in missing:
                print(f"    - {n}")
        if not updated and not missing:
            print("  already in sync, nothing to do")

        if updated and not args.dry_run:
            target_path.write_text(new_html, encoding="utf-8")
            print(f"  wrote {target_label}")
        elif updated and args.dry_run:
            print(f"  (dry run - {target_label} NOT written)")

        # Re-check for anything CHECKS considers a real drift that this pass didn't
        # resolve (e.g. a pattern that matched in source but the target's own copy of
        # the surrounding text differs enough that find/replace succeeded yet a
        # different, unrelated check now disagrees) - belt and suspenders, since this
        # script's whole job is to make check_site_drift.py --against clean afterward.
        final_html = new_html if not args.dry_run else new_html
        _, final_report = apply_blocks(source_html, final_html)
        unresolved = [n for n, s in final_report if s not in ("already in sync", "not found in source")]
        if unresolved:
            any_unresolved = True
            print(f"  ! still unresolved after apply: {unresolved}")
        print()

    if any_unresolved:
        print("Some blocks are still unresolved after applying - inspect manually.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
