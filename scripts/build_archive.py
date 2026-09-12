#!/usr/bin/env python3
"""
Builds a static, text-only archive page for the edition currently in data/edition.json,
at archive/edition<NNN>/index.html (zero-padded to 3 digits, e.g. archive/edition002/).

No map, no BASIN_BUNDLE, no JS - just the masthead/signals/news/notes/table content already
in edition_top_html + edition_bottom_html, wrapped in a minimal static page with a
"<- Previous edition" link computed from (edition number - 1). Stateless: everything it needs
comes from data/edition.json itself, so there is no separate index/listing file to keep in
sync.

Run from the repo root: python scripts/build_archive.py
Writes (and only writes) archive/edition<NNN>/index.html for the CURRENT edition in
data/edition.json - it does not touch any other archive page. If that file already exists
with identical content, no write occurs (so a re-run / duplicate trigger is a no-op, not an
error).
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if os.path.basename(os.path.dirname(os.path.abspath(__file__))) == "scripts" else os.getcwd()
EDITION_JSON = os.path.join(REPO_ROOT, "data", "edition.json")
ARCHIVE_DIR = os.path.join(REPO_ROOT, "archive")

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Basin Watch — Edition {edition_padded} ({generated})</title>
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans+Condensed:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
:root{{
  color-scheme:dark;
  --ground:#272727; --surface:#323131; --surface-2:#383837; --sunk:#232323;
  --ink:#F9F9F7; --muted:#C3C2B7; --faint:#97958D; --line:#444341; --line-soft:#343432;
  --accent:#D97757; --accent-ink:#F0A382; --accent-soft:#3D2A21;
  --hot:#E9764F; --hot-soft:#331F17;
  --home:#5FADEA; --home-soft:#12283A;
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);
  font-family:"IBM Plex Sans","Segoe UI",system-ui,sans-serif;font-size:15px;line-height:1.55;
  -webkit-font-smoothing:antialiased}}
.wrap{{width:96%;max-width:1400px;margin:0 auto;padding:18px 0 44px}}
h1,h2,h3,.cond{{font-family:"IBM Plex Sans Condensed","IBM Plex Sans",system-ui,sans-serif}}
.mono{{font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;font-variant-numeric:tabular-nums}}

.archbanner{{background:var(--surface-2);border:1px solid var(--line);border-left:3px solid var(--accent);
  padding:10px 15px;font-size:13px;color:var(--muted);margin-bottom:16px}}
.archbanner a{{color:var(--accent-ink)}}

.mast{{position:relative;display:flex;justify-content:center;align-items:center;gap:24px;
  padding:4px 0 13px;border-bottom:2px solid var(--ink);flex-wrap:wrap}}
.mast .lead{{display:flex;align-items:center;gap:20px;flex:0 1 auto;min-width:0}}
.mast .titlecol{{display:flex;flex-direction:column;align-items:center;gap:3px;flex:0 0 auto}}
.mast .titlecol h1{{margin:0}}
.mast .wir{{font-size:13px;line-height:16px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);text-align:center}}
.mast h1{{margin:0;font-size:clamp(26px,5vw,40px);font-weight:700;letter-spacing:-.018em;line-height:.98}}
.mast .sub{{color:var(--muted);font-size:13px;line-height:1.45;max-width:640px;margin:0 0 0 20px}}
.tickerwrap{{display:flex}}
.ticker{{border:1.5px solid var(--hot);padding:5px 11px;display:grid;
  grid-template-columns:auto auto auto;justify-content:center;align-items:center;gap:1px 7px}}
.ticker .tksrc{{grid-column:1/-1;font-size:8.5px;letter-spacing:.06em;text-transform:uppercase;
  color:var(--faint);text-align:center;white-space:nowrap}}
.ticker .tksym{{font-size:13.2px;letter-spacing:.06em;color:var(--hot);font-weight:700;line-height:1}}
.ticker .tkpx{{font-size:19px;font-weight:700;letter-spacing:-.01em;color:var(--ink);line-height:1}}
.ticker .tklbl{{font-size:11.4px;letter-spacing:.02em;color:var(--muted);font-weight:600;line-height:1}}
.mastright{{display:flex;align-items:center;gap:18px}}
.edition{{text-align:center}}
.edition .d{{font-size:13px;line-height:16px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}}
.edition .n{{font-size:22px;line-height:26px;font-weight:600;letter-spacing:-.01em}}

.signals{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1px;
  background:var(--line);border:1px solid var(--line);margin:16px 0 24px}}
.sig{{background:var(--surface);padding:11px 15px 12px;display:flex;flex-direction:column;gap:2px}}
.sig .k{{font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--faint);font-weight:600}}
.sig .v{{font-size:25px;font-weight:600;letter-spacing:-.02em;line-height:1.15}}
.sig .n{{font-size:12px;color:var(--muted);line-height:1.4}}
.sig.hot .v{{color:var(--hot)}}

h2.sec{{font-size:13px;letter-spacing:.15em;text-transform:uppercase;color:var(--muted);
  font-weight:600;margin:26px 0 4px;display:flex;align-items:center;gap:10px}}
h2.sec::after{{content:"";flex:1;height:1px;background:var(--line)}}

.news{{display:flex;flex-direction:column;gap:1px;background:var(--line);
  border:1px solid var(--line);margin-bottom:22px}}
.item{{background:var(--surface);padding:13px 16px;display:grid;
  grid-template-columns:32px minmax(0,1fr) 190px;gap:10px 16px}}
.item>*{{grid-column:2}}
.item>.rank{{grid-column:1}}
.item>.stk{{grid-column:3;grid-row:1}}
.rank{{font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--faint);padding-top:3px;font-weight:500}}
.item.lead .rank{{color:var(--hot);font-weight:600}}
.hd{{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 10px}}
.co{{font-family:"IBM Plex Sans Condensed",sans-serif;font-weight:700;font-size:17px;letter-spacing:-.005em}}
.tk{{font-family:"IBM Plex Mono",monospace;font-size:11.5px;color:var(--muted);border:1px solid var(--line);padding:1px 5px}}
.when{{font-size:12px;color:var(--faint);margin-left:auto}}
.ttl{{grid-column:2;font-size:14.5px;margin:3px 0 0;color:var(--ink)}}
.ttl a{{color:inherit;text-decoration:none;border-bottom:1px solid var(--line)}}
.why{{grid-column:2;font-size:13.5px;color:var(--muted);margin:6px 0 0}}
.why b{{color:var(--ink);font-weight:600}}
.chips{{grid-column:2;display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}}
.chip{{font-family:"IBM Plex Mono",monospace;font-size:11px;padding:2.5px 7px;
  border:1px solid var(--line);color:var(--muted);white-space:nowrap}}
.chip.g{{background:var(--hot-soft);border-color:transparent;color:var(--hot);font-weight:600}}
.chip.s{{background:var(--accent-soft);border-color:transparent;color:var(--accent-ink);font-weight:500}}
.chip.warn{{border-style:dashed;border-color:var(--hot);color:var(--hot)}}
.g-assay{{font-family:"IBM Plex Mono",monospace;font-weight:700;color:#F2C14E}}
.g-cps{{font-family:"IBM Plex Mono",monospace;font-style:italic;font-weight:500;color:#B295DC}}

.stk{{border:1px solid var(--line);background:var(--surface-2);padding:9px 11px;
  font-family:"IBM Plex Mono",monospace;display:flex;flex-direction:column;gap:2px}}
.stk .sx{{font-size:9.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--faint)}}
.stk .sp{{font-size:19px;font-weight:600;color:var(--ink);letter-spacing:-.01em}}
.stk .sc{{font-size:12px;font-weight:600}}
.stk .sc.up{{color:#4bbd7d}} .stk .sc.dn{{color:var(--hot)}} .stk .sc.fl{{color:var(--faint)}}
.stk .sr{{font-size:9.8px;color:var(--muted);line-height:1.5;margin-top:4px;padding-top:5px;border-top:1px solid var(--line-soft)}}
.stk .sr b{{color:var(--faint);font-weight:400}}

.note{{background:var(--surface-2);border-left:3px solid var(--accent);padding:11px 15px;
  font-size:13.5px;margin:0 0 20px;color:var(--ink)}}
.note b{{font-weight:600}}
.note .h{{font-family:"IBM Plex Sans Condensed",sans-serif;font-weight:700;font-size:14.5px;
  display:block;margin-bottom:3px}}

.tbl{{width:100%;border-collapse:collapse;font-size:13.5px;background:var(--surface)}}
.tbl caption{{text-align:left;font-size:12px;color:var(--muted);padding:0 0 8px}}
.tbl th{{text-align:left;font-size:10.5px;letter-spacing:.11em;text-transform:uppercase;
  color:var(--faint);font-weight:600;padding:9px 12px;border-bottom:1px solid var(--line);white-space:nowrap}}
.tbl td{{padding:8px 12px;border-bottom:1px solid var(--line-soft);vertical-align:top}}
.tbl tr:last-child td{{border-bottom:none}}
.tbl td.num{{font-family:"IBM Plex Mono",monospace;white-space:nowrap}}
.tblwrap{{overflow-x:auto;border:1px solid var(--line);margin:20px 0 16px}}

.arch{{background:var(--surface);border:1px solid var(--line);padding:2px 0;margin-bottom:16px}}
.arow{{display:flex;gap:14px;align-items:baseline;padding:10px 16px;border-bottom:1px solid var(--line-soft);font-size:13.5px}}
.arow:last-child{{border-bottom:none}}
.arow .ad{{font-family:"IBM Plex Mono",monospace;font-size:12.5px;color:var(--muted);flex:0 0 auto}}
.arow .as{{color:var(--muted)}}
.arow .cur{{color:var(--accent-ink);font-weight:600}}
.arch a.arow{{color:inherit;text-decoration:none}}
.arch a.arow:hover{{background:var(--surface-2)}}

.prevnav{{margin:26px 0 10px;padding-top:16px;border-top:1px solid var(--line)}}
.prevnav a{{color:var(--accent-ink);text-decoration:none;font-size:13.5px}}
.prevnav a:hover{{text-decoration:underline}}

footer{{margin-top:22px;padding-top:14px;border-top:1px solid var(--line);
  font-size:12.5px;color:var(--faint);line-height:1.6}}
footer a{{color:var(--muted)}}

@media(max-width:820px){{
  .wrap{{width:100%;max-width:none;padding:18px 16px 56px}}
  .mast{{display:block;position:static;padding-bottom:13px}}
  .mast .lead{{display:block}}
  .mast .sub{{margin:6px 0 0}}
  .mast h1{{font-size:28px}}
  .mastright{{display:block;margin-left:0}}
  .tickerwrap{{margin:12px 0 0}}
  .edition{{text-align:left;margin:12px 0 0}}
  .signals{{grid-template-columns:1fr}}
  .item{{grid-template-columns:26px minmax(0,1fr);padding:14px}}
  .item>.stk{{grid-column:1/span 2;grid-row:auto;margin-top:11px}}
  .when{{margin-left:0;flex-basis:100%}}
}}
</style>
</head>
<body>
<div class="wrap">

<div class="archbanner">This is an archived Basin Watch edition, frozen as published on {generated}. <a href="https://basinwatch.ca/">See the current edition →</a></div>

{edition_top_html}

{edition_bottom_html}

{prev_nav}

<footer>
Basin Watch — Athabasca Basin uranium competitor brief. Archived edition, no longer updated.
</footer>

</div>
</body>
</html>
"""

PREV_NAV_TEMPLATE = '<div class="prevnav"><a href="/archive/edition{prev_padded}/">&larr; Previous edition (No. {prev_padded})</a></div>'


def main():
    if not os.path.exists(EDITION_JSON):
        print(f"ERROR: {EDITION_JSON} not found", file=sys.stderr)
        sys.exit(1)

    with open(EDITION_JSON, "r", encoding="utf-8") as f:
        edition_data = json.load(f)

    for key in ("generated", "edition", "edition_top_html", "edition_bottom_html"):
        if key not in edition_data:
            print(f"ERROR: data/edition.json missing required key '{key}'", file=sys.stderr)
            sys.exit(1)

    edition_num = int(edition_data["edition"])
    edition_padded = f"{edition_num:03d}"
    generated = edition_data["generated"]

    # Link back only if that edition was ACTUALLY archived by this mechanism - not just
    # "edition_num - 1 >= 1". Edition 001 (and any other edition published before this
    # workflow existed) has no archive page here and never will, so a purely arithmetic
    # link would 404. Check the file's actual presence instead.
    prev_nav = ""
    if edition_num > 1:
        prev_padded = f"{edition_num - 1:03d}"
        prev_page_path = os.path.join(ARCHIVE_DIR, f"edition{prev_padded}", "index.html")
        if os.path.exists(prev_page_path):
            prev_nav = PREV_NAV_TEMPLATE.format(prev_padded=prev_padded)

    html = TEMPLATE.format(
        edition_padded=edition_padded,
        generated=generated,
        edition_top_html=edition_data["edition_top_html"],
        edition_bottom_html=edition_data["edition_bottom_html"],
        prev_nav=prev_nav,
    )

    out_dir = os.path.join(ARCHIVE_DIR, f"edition{edition_padded}")
    out_path = os.path.join(out_dir, "index.html")

    if os.path.exists(out_path):
        with open(out_path, "r", encoding="utf-8") as f:
            existing = f.read()
        if existing == html:
            print(f"No change: {out_path} already up to date.")
            return
        print(f"NOTE: {out_path} already exists with DIFFERENT content - overwriting. "
              f"This means edition {edition_padded} was archived once already (a re-run or a "
              f"same-edition-number republish) - check this is expected before trusting it.")

    os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Wrote {out_path} ({len(html)} bytes)")


if __name__ == "__main__":
    main()
