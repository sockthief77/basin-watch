#!/usr/bin/env python3
"""
Fetch the day's brief content from the "Basin Watch - Daily Handoff" Claude
Artifact page and write it to data/edition.json, which scripts/build.py then
substitutes into site/shell.html at the __EDITION_TOP__/__EDITION_BOTTOM__
placeholders.

This is the daily-brief-content half of the automation; scripts/basin_layers.py
+ merge_map_bundle.py (run by .github/workflows/gis-export.yml) is the map/GIS
half. Run by .github/workflows/publish-brief.yml, shortly after the daily
brief skill has published the handoff page (skill runs ~09:00 America/Regina;
this workflow runs ~09:25 to give it time to finish).

The handoff page must be set to "Shared" from its own share menu in Claude -
this script fetches it anonymously (no login), the same way basin_layers.py
reads public Saskatchewan GIS endpoints and the skill itself reads
data/bundle.json over the public raw.githubusercontent.com URL. If the page
isn't shared, or Claude hasn't published today's edition yet, or the fetch
fails for any reason, this script exits 0 without touching data/edition.json -
same "never wipe good data with a failed fetch" guard used in
merge_map_bundle.py for the restricted-lands incident. A missing edition
update just means the site keeps showing yesterday's edition until the next
successful run, which is always better than the site going blank or half-built.

Usage:
    python3 scripts/merge_edition.py
"""
import base64
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EDITION_PATH = ROOT / "data" / "edition.json"

HANDOFF_URL = "https://claude.ai/code/artifact/306616aa-3eb1-4744-8497-d9a9745cdedf"
REQUIRED_KEYS = {"generated", "edition", "edition_top_html", "edition_bottom_html"}
PRE_RE = re.compile(
    r'<pre id="handoff-data"[^>]*>([A-Za-z0-9+/=\s]+)</pre>', re.DOTALL
)


def fail_soft(msg: str) -> None:
    # Never a non-zero exit: a bad/missing handoff page should not break the
    # workflow or block the map-data half of the site from staying current.
    print(f"merge_edition.py: {msg} - leaving data/edition.json untouched")
    sys.exit(0)


def main() -> None:
    try:
        req = urllib.request.Request(
            HANDOFF_URL, headers={"User-Agent": "basin-watch-publish-brief/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        fail_soft(f"fetch failed: {e}")
        return

    m = PRE_RE.search(html)
    if not m:
        fail_soft("no <pre id=\"handoff-data\"> block found in fetched page "
                   "(page may not be Shared yet, or today's edition hasn't published)")
        return

    b64 = "".join(m.group(1).split())
    try:
        payload = base64.b64decode(b64, validate=True).decode("utf-8")
        edition = json.loads(payload)
    except Exception as e:
        fail_soft(f"payload did not decode/parse as JSON: {e}")
        return

    missing = REQUIRED_KEYS - edition.keys()
    if missing:
        fail_soft(f"decoded JSON missing keys: {missing}")
        return
    if not str(edition["edition_top_html"]).strip() or not str(edition["edition_bottom_html"]).strip():
        fail_soft("edition_top_html or edition_bottom_html is empty")
        return

    if EDITION_PATH.exists():
        try:
            current = json.loads(EDITION_PATH.read_text(encoding="utf-8-sig"))
            if current.get("generated") == edition.get("generated") and \
               current.get("edition") == edition.get("edition"):
                print(f"merge_edition.py: handoff still shows {edition.get('generated')} "
                      f"No. {edition.get('edition')} - same as current data/edition.json, nothing to do")
                return
        except Exception:
            pass  # if the existing file is unreadable, fall through and overwrite it

    EDITION_PATH.write_text(
        json.dumps(edition, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"merge_edition.py: wrote data/edition.json - {edition.get('generated')} No. {edition.get('edition')}")


if __name__ == "__main__":
    main()
