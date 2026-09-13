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

This is NOT a general HTML/JS diff - the two files are legitimately different in plenty of
ways (explorer has no news list, its own back-link, its own single-page layout CSS). It only
checks the specific named constants and code shapes that both engines are supposed to share
verbatim, by exact substring presence/equality - the same spot-checks a session would
otherwise have to remember to do by hand.

Usage:
    python3 scripts/check_site_drift.py
Exits non-zero and prints every mismatch if anything differs; silent and exits 0 if clean.

Add a new (name, pattern) pair to CHECKS below whenever a new constant/behavior is added
that both pages must share - the same discipline as the drift this script exists to catch.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHELL = ROOT / "site" / "shell.html"
EXPLORER = ROOT / "site" / "explorer-shell.html"

# Each entry: (name, regex). The regex's first capture group is the value compared between
# the two files. Use non-capturing groups (?:...) for everything else. A pattern that isn't
# found in a file is reported as a mismatch (missing), not silently skipped - a constant
# that's supposed to exist in both and vanished from one is exactly the failure mode this
# script exists to catch.
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
                         r"(ctx\.fillStyle='#000000';ctx\.fill\(\);[^\n]*\n\s*\}\);)"),
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
]


def load(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"missing file: {path}")
    return path.read_text(encoding="utf-8")


def extract(html: str, pattern: str):
    m = re.search(pattern, html)
    return m.group(1) if m else None


def main() -> int:
    shell_html = load(SHELL)
    explorer_html = load(EXPLORER)

    problems = []
    for name, pattern in CHECKS:
        a = extract(shell_html, pattern)
        b = extract(explorer_html, pattern)
        if a is None and b is None:
            # Not present in either - fine, e.g. a shell.html-only feature that hasn't
            # been ported to explorer yet on purpose. Not this script's job to demand
            # every feature exist everywhere, only that shared ones agree.
            continue
        if a is None:
            problems.append(f"[{name}] present in explorer-shell.html but MISSING from shell.html")
        elif b is None:
            problems.append(f"[{name}] present in shell.html but MISSING from explorer-shell.html")
        elif a != b:
            problems.append(f"[{name}] DIFFERS:\n    shell.html:          {a}\n    explorer-shell.html: {b}")

    if problems:
        print(f"DRIFT CHECK FAILED - {len(problems)} mismatch(es) between site/shell.html and "
              f"site/explorer-shell.html:\n")
        for p in problems:
            print(" -", p)
        print("\nEach of these is supposed to be identical in both files - see this script's "
              "module docstring for why. Fix the file that's behind before publishing.")
        return 1

    print(f"OK - {len(CHECKS)} shared constants/behaviors checked, no drift between "
          f"shell.html and explorer-shell.html.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
