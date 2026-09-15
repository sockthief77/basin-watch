#!/usr/bin/env python3
"""
Identity leak gate - run before every publish of any file under site/, data/,
or archive/ (anything Cloudflare actually serves from dist/).

Blocks the same failure mode that shipped live twice (2026-09-11: ~40 code
comments and an edition note naming the operator; 2026-09-15: one comment
slipped back in after the first scrub). A written rule alone did not hold -
this script is the enforcement.

Checks two things:
  1. The operator's name (any case) does not appear anywhere in site/,
     data/, or archive/.
  2. No AI-process-narration phrases leak into published text (per
     watchlist-and-sources.md's "Published prose reads as professional
     industry reporting" rule) - a lighter heuristic check, flagged not
     blocked, since this one has legitimate false positives.

Exit code 1 (and a loud message naming every match) if the name check finds
anything. Run from the repo root: python3 scripts/check_no_identity.py
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The operator's name(s)/handles that must never appear in anything served
# by Cloudflare. Add to this list if a new identifying string is ever found -
# never remove an entry just because a scrub made it pass once.
FORBIDDEN = [
    "ezra",
    "meszaros",
]

SCAN_DIRS = ["site", "data", "archive"]

NARRATION_PATTERNS = [
    r"\bconfirmed by (a )?direct diff\b",
    r"\bderived from (two|three|several) independently\b",
    r"\brequired splitting the query\b",
    r"\bconfirmed by a live query\b",
]


def scan_identity():
    hits = []
    for d in SCAN_DIRS:
        dirpath = ROOT / d
        if not dirpath.exists():
            continue
        for path in dirpath.rglob("*"):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            lower = text.lower()
            for name in FORBIDDEN:
                if name in lower:
                    for i, line in enumerate(text.splitlines(), 1):
                        if name in line.lower():
                            hits.append((str(path.relative_to(ROOT)), i, line.strip()[:120]))
    return hits


def scan_narration():
    hits = []
    for d in SCAN_DIRS:
        dirpath = ROOT / d
        if not dirpath.exists():
            continue
        for path in dirpath.rglob("*"):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for pat in NARRATION_PATTERNS:
                for m in re.finditer(pat, text, re.IGNORECASE):
                    line_no = text.count("\n", 0, m.start()) + 1
                    hits.append((str(path.relative_to(ROOT)), line_no, m.group(0)))
    return hits


def main():
    identity_hits = scan_identity()
    narration_hits = scan_narration()

    if narration_hits:
        print("NOTICE: possible AI-process-narration language found (not blocking, review before publish):")
        for f, ln, match in narration_hits:
            print(f"  {f}:{ln}  -> {match!r}")
        print()

    if identity_hits:
        print("BLOCKED: identifying information found in files Cloudflare will serve:")
        for f, ln, line in identity_hits:
            print(f"  {f}:{ln}  -> {line}")
        print()
        print("Fix every line above before committing. This check exists because the same")
        print("leak has shipped live twice already - see claude/daily-publish-instructions.md.")
        sys.exit(1)

    print("OK: no identifying strings found in site/, data/, or archive/.")
    sys.exit(0)


if __name__ == "__main__":
    main()
