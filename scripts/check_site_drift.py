#!/usr/bin/env python3
"""
Checks that site/shell.html and site/explorer-shell.html agree on every constant/behavior
that's supposed to be identical between the two pages' map engines.

Why this exists (2026-09-13): three separate bugs in one session were all the same shape -
a value or piece of logic got updated in one file (usually the one being actively worked
on) and the other file was never touched, because nothing forces the two copies to stay in
sync. Specifically: the rank-badge-to-map lookup array missing the new Drill Results bucket,
explorer-shell.html's Reset View box stuck on an old value shell.html had already moved on
from, and (from an earlier session) the Boulder Heat toggle reading the wrong field in one
file but not the other. All three were "I changed X, forgot Y also needed it." The same day
also turned up explorer-shell.html completely missing the Lapsing 8-14 Days layer - not a
drifted value but a whole feature present on one page and never ported to the other - which
this script also now guards against as a named-constant check (the LAYERS entry itself).

This is NOT a general HTML/JS diff - the files are legitimately different in plenty of
ways (explorer has no news list, its own back-link, its own single-page layout CSS). It only
checks the specific named constants and code shapes that are supposed to be shared
verbatim, by exact substring presence/equality - the same spot-checks a session would
otherwise have to remember to do by hand.

Usage:
    python3 scripts/check_site_drift.py
        Default, unchanged since 2026-09-13: compares site/shell.html (source of truth)
        against site/explorer-shell.html.

    python3 scripts/check_site_drift.py --against FILE [--against FILE ...]
        Compares site/shell.html against each FILE instead of (not in addition to)
        explorer-shell.html - e.g. a freshly-read copy of a live claude.ai artifact saved
        to the scratchpad, so the same 20-odd shared-block checks this script already
        knows about can be run against the two live map surfaces this repo can't read
        directly, not just the two files sitting in site/. Multiple --against files are
        each checked independently against the source, and all mismatches are reported
        together.

    python3 scripts/check_site_drift.py --source FILE --against FILE [--against FILE ...]
        Same, with an explicit source of truth instead of site/shell.html - e.g. to check
        site/explorer-shell.html's own blocks propagated correctly to the Explorer
        artifact.

Exits non-zero and prints every mismatch if anything differs; silent and exits 0 if clean.

Add a new (name, pattern) pair to CHECKS below whenever a new constant/behavior is added
that's supposed to be shared - the same discipline as the drift this script exists to catch.
See scripts/sync_shared_blocks.py to apply the source's blocks onto a target file, rather
than just report where it's behind.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHELL = ROOT / "site" / "shell.html"
EXPLORER = ROOT / "site" / "explorer-shell.html"

# Each entry: (name, regex). The regex's first capture group is the value compared between
# files. Use non-capturing groups (?:...) for everything else. A pattern that isn't found in
# a file is reported as a mismatch (missing), not silently skipped - a constant that's
# supposed to exist in both and vanished from one is exactly the failure mode this script
# exists to catch. A pattern absent from BOTH sides being compared is fine (not every check
# here applies to every surface - e.g. the archive list only exists on shell.html-shaped
# pages) - see main()'s "present in neither" handling.
CHECKS = [
    ("NORTH_CUT_M",      r"var NORTH_CUT_M=(\d+);"),
    ("BOX_E_MIN/MAX, BOX_N_MIN/MAX",
                         r"var BOX_E_MIN=(\d+), BOX_E_MAX=\d+, BOX_N_MIN=\d+, BOX_N_MAX=\d+;"),
    ("HOMEBOX",          r"var HOMEBOX=(\[[^\]]*\]);"),
    ("NEWSXCOL (Other News colour)",  r"var NEWSXCOL='(#[0-9A-Fa-f]{6})';"),
    ("NEWSDCOL (Drill Results colour)", r"var NEWSDCOL='(#[0-9A-Fa-f]{6})'"),
    ("NEWSGEOCOL (Geophysics colour)",  r"var NEWSGEOCOL='(#[0-9A-Fa-f]{6})'"),
    ("col: ternary (star/badge colour assignment)",
                         r"(col:\(ty==='grade'\?[^}]*?\)\}\); \}\);)"),
    ("NEWSG/NEWSD/NEWSX filter definitions",
                         r"(var NEWSG=P\.news\.filter[\s\S]*?var NEWSX=P\.news\.filter\(function\(w\)\{return[^;]*;\}\);)"),
    ("NEWSTYPE (tooltip type labels)", r"(var NEWSTYPE=\{[\s\S]*?\}\};)"),
    ("ANCLAB (anchor-method tooltip labels)", r"(var ANCLAB=\{[^}]*\};)"),
    ("ANCUNC (default anchor uncertainty)",   r"(var ANCUNC=\{[^}]*\};)"),
    ("Mines & Mills fill/stroke",
                         r"(ctx\.fillStyle='#[0-9A-Fa-f]{6}';ctx\.fill\(\);[^\n]*\n\s*\}\);)"),
    ("Mines & Mills legend swatch colour",
                         r"\{k:'mine',\s*label:'Mines & Mills',\s*color:'(#[0-9A-Fa-f]{6})'"),
    ("clipRingToBox/clipLineToBox present", r"(function clipRingToBox\(ring\)\{)"),
    ("currentScaleKm() present",            r"(function currentScaleKm\(\)\{)"),
    ("mapActivate hint markup",
                         r'(<div class="mapactivate" id="mapActivateHint">[^<]*</div>)'),
    ("Lapsing 8-14 Days LAYERS entry",
                         r"(\{k:'lapse2',label:'Lapsing 8-14 Days',color:'#[0-9A-Fa-f]{6}',"
                         r"get:function\(\)\{return P\.tenure\.filter\(function\(t\)\{"
                         r"return t\.lapseSoon2&&!t\.isNew;\}\)\.length;\}\})"),
    ("Lapsing 7-day/8-14-day outline lineWidth",
                         r"(ctx\.lineWidth=Math\.max\([\d.]+,Math\.min\([\d.]+,view\.s\*[\d.]+\)\);ctx\.stroke\(\);)"),
    ("Lake/river fill+stroke translucency",
                         r"(ctx\.fillStyle='rgba\(61,111,138,[\d.]+\)';ctx\.strokeStyle='rgba\(61,111,138,[\d.]+\)';ctx\.lineWidth=\.7;)"),
    ("Archive list collapse (COLLAPSE_AFTER + toggle)",
                         r"(var COLLAPSE_AFTER=\d+;[\s\S]*?archEl\.appendChild\(toggle\);\n\}\)\(\);)"),
]


def load(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"missing file: {path}")
    return path.read_text(encoding="utf-8")


def extract(html: str, pattern: str):
    m = re.search(pattern, html)
    return m.group(1) if m else None


def compare(source_html: str, source_label: str, target_html: str, target_label: str):
    """Returns a list of mismatch strings for one (source, target) file pair."""
    problems = []
    for name, pattern in CHECKS:
        a = extract(source_html, pattern)
        b = extract(target_html, pattern)
        if a is None and b is None:
            continue
        if a is None:
            problems.append(f"[{name}] present in {target_label} but MISSING from {source_label}")
        elif b is None:
            problems.append(f"[{name}] present in {source_label} but MISSING from {target_label}")
        elif a != b:
            problems.append(f"[{name}] DIFFERS:\n    {source_label}: {a}\n    {target_label}: {b}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", type=Path, default=None,
                     help="Source-of-truth file (default: site/shell.html)")
    ap.add_argument("--against", type=Path, action="append", default=None,
                     help="Target file to compare against source (repeatable). "
                          "Default: site/explorer-shell.html")
    args = ap.parse_args()

    source_path = args.source or SHELL
    target_paths = args.against or [EXPLORER]

    source_html = load(source_path)
    source_label = str(source_path.relative_to(ROOT)) if source_path.is_relative_to(ROOT) else str(source_path)

    all_problems = {}
    for target_path in target_paths:
        target_html = load(target_path)
        target_label = str(target_path.relative_to(ROOT)) if target_path.is_relative_to(ROOT) else str(target_path)
        problems = compare(source_html, source_label, target_html, target_label)
        if problems:
            all_problems[target_label] = problems

    if all_problems:
        total = sum(len(v) for v in all_problems.values())
        print(f"DRIFT CHECK FAILED - {total} mismatch(es) against source {source_label}:\n")
        for target_label, problems in all_problems.items():
            print(f"-- vs {target_label} --")
            for p in problems:
                print(" -", p)
            print()
        print("Each of these is supposed to be identical - see this script's module "
              "docstring for why. Fix whichever side is behind before publishing. "
              "scripts/sync_shared_blocks.py can apply the source's blocks onto a "
              "target automatically.")
        return 1

    target_labels = [str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p) for p in target_paths]
    print(f"OK - {len(CHECKS)} shared constants/behaviors checked, no drift between "
          f"{source_label} and {', '.join(target_labels)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
