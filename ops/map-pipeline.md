# Basin Watch map pipeline

How the interactive map on the living page is built and kept up to date. This doc states
**current** behavior only. Session-by-session history (what was tried, what broke, what got
reverted) lives in `history.md` - read it only when troubleshooting a regression, not
on a normal run.

## Standing rule, added 2026-09-13: basinwatch.ca is the end product - read this before touching the map engine

**Ezra's explicit direction, 2026-09-13: "I want to ALWAYS update basinwatch.ca. The purpose
of this project is to have that be the end product, auto-updated. I want this to be a clean
and efficient process each run."** This supersedes the informal practice that grew up over
the previous few days, where every map/UI engine fix (lake and highway name labels, the
box-clip fix so lakes/rivers stop vanishing at the working-box edge, the click-to-interact
redesign, the scale-bar-based zoom gate, rank-badge-to-map linking) was applied directly to
the two claude.ai pages' own copy of the shell and never ported back into the repo's
`site/shell.html` / `site/explorer-shell.html`. That practice is why a same-day discovery on
2026-09-13 found `site/shell.html` and `site/explorer-shell.html` on `main` were still running
a materially older map engine than either claude.ai page - none of the five items above were
present, so basinwatch.ca still had the original vanishing-lake/highway bug and none of the
zoom-triggered labels, even though both claude.ai pages had looked fixed for a day already.

**Going forward: any map-engine change is authored directly against `site/shell.html` and
`site/explorer-shell.html` in the repo, never against a claude.ai artifact copy first.**
Verify with `python3 scripts/build.py` (checks placeholder substitution, script-tag count,
JSON re-parse) then a headless-Chromium/Playwright load-and-screenshot check of
`dist/index.html` and `dist/explorer/index.html`, the same standard already used for the
claude.ai pages. **As of 2026-09-13 (2nd pass), also run `python3 scripts/check_site_drift.py`
before publishing either file** - see "Drift-check script" below; it exists specifically
because "verify by eye" wasn't catching every place a shared constant needed updating in both
files. As of 2026-09-14, a repo-bound Claude Code session can commit these changes directly
(`git add`/`commit`/`push`) - see "Standing note: real git write access" in
`basinwatch-pipeline-fix.md`. This is what "clean and efficient" means in practice: one
canonical engine, one place it's edited, and basinwatch.ca picks it up on the very next push
via Cloudflare's existing auto-deploy - no separate "now also go fix the site copy" step, ever
again. The claude.ai pages remain useful as a live preview/talking surface but are no longer
where engine fixes originate.

**Ported 2026-09-13**, closing the gap described above: all five items (box-clip, lake labels,
highway labels, click-to-interact top-left/whole-card activation, scale-bar 25 km gate) plus
the rank-badge-to-map click-through were added to `site/shell.html`
(`site/explorer-shell.html` got everything except the rank-badge linking, which needs a
`.news .item` list that only Basin Watch renders). Ported as a minimal, additive diff against
each file's OWN current text - not a wholesale replacement - specifically to avoid disturbing
things that were never part of this fix and are still live-in-use on basinwatch.ca only (the
Newsletter Sign-Up modal wiring `nlOpenBtn`/`nlOverlay`, the masthead's own grid layout,
`measOut`/Measure-tool markup) but were never carried over to the claude.ai copies either, in
the other direction. Verified via `scripts/build.py` (both script-tag counts and the JSON
re-parse passed) and Playwright (page-error check on both built pages; a zoomed screenshot of
`dist/explorer/index.html` confirmed a highway label - "Hwy 905" - actually renders, proving
the ported engine runs, not just that it compiles).

**Drift-check script, added 2026-09-13 (2nd pass).** Three separate bugs the same day were all
the same shape: a constant or bit of logic updated in one of `shell.html`/`explorer-shell.html`
and never updated in the other, because nothing forced them to agree (the rank-badge lookup
array missing a newly-added bucket, `explorer-shell.html`'s `HOMEBOX` stuck on an old value
`shell.html` had already moved past, and - from an earlier session - the Boulder Heat toggle
reading the wrong field in one file only). `scripts/check_site_drift.py` spot-checks the named
constants/behaviors that are supposed to be identical between the two files (colour constants,
`HOMEBOX`, `NORTH_CUT_M`/box bounds, the `NEWSTYPE`/`ANCLAB`/`ANCUNC` lookup objects, the
Mines & Mills fill, the `col:` assignment ternary and `NEWSG`/`NEWSD`/`NEWSX` filters, and a
presence check for `clipRingToBox`/`currentScaleKm`/the click-to-interact markup) and fails
loudly, naming exactly what differs, if any of them don't match byte-for-byte. Run it from the
repo root before every publish of either file: `python3 scripts/check_site_drift.py`. Add a
new `(name, pattern)` entry to its `CHECKS` list whenever a new shared constant/behavior is
introduced - the same discipline the script exists to enforce on everything else.

## Named-lake mismatch found and fixed, 2026-09-13: gazetteer tie-break by HECTARES

Ezra flagged Tazin Lake's shape as wrong, linking a Google Maps location
(59.827,-109.133). Investigation found the *shape* was fine (343 points, 1 harmless
self-intersection, nowhere near the severity-filter's reject threshold) - the problem was the
**name**: the polygon was labelled "Godfrey Lake" instead of "Tazin Lake". Root cause:
`gazetteer_name()` (the `SaskNamesDatabaseWater` fallback added 2026-09-13 morning for blank
`LAKNAMEEN` fields - see `history.md`) took the *first* gazetteer point that tested as
inside a lake ring, with no tie-break. Confirmed directly against the live service: this one
polygon contains gazetteer points for both **Tazin Lake** (36,510.59 ha, the real, large lake -
several TOPONYM points scattered across its extent, all sharing that HECTARES value) and tiny
**Godfrey Lake** (65.65 ha, sitting at the polygon's northern tip, dissolved into the same
coarse Hydrography outline). Godfrey's point happened to test as the first match, so the
550x-bigger lake got the small lake's name.

**Fix**: `gazetteer_name()` now pulls `HECTARES` alongside `TOPONYM` and, when more than one
gazetteer point falls inside a ring, keeps the one with the largest `HECTARES` rather than
whichever tested first. Verified against the real live data for this exact case (extracted via
a live query, replayed through both the old and new logic): old logic -> "Godfrey Lake", new
logic -> "Tazin Lake". A small satellite lake's own point still wins when it's genuinely the
*only* match for its own (uncontaminated) polygon - this only changes the outcome on a
multi-match.

**Also fixed the same day: named rivers were losing out to lakes in the 55-feature cap.** The
lake/river selection in `basin_layers.py` ranks candidates by ring AREA and takes the top 55 -
a long, narrow river can be enormously significant and still have a tiny polygon footprint
next to a round lake, so Clearwater River (a real, named feature with its own provincial park
along it) was ranked well outside the cut and never shipped at all. Fixed by pulling any
candidate whose own government-supplied name contains "river" to the front of the ranking,
ahead of area-only sorting, and raising the cap 55 -> 60 to give them room without displacing
existing lakes. **Root cause of it still not rendering, found and fixed 2026-09-13 (later
pass) - see `open-items.md`:** `_is_named_river()` only checked the raw `LAKNAMEEN` field
(blank for most features at this tier) and needed to also check the gazetteer fallback BEFORE
the area-based cut decides who survives, not after.

## News waypoint colour scheme, ranking-badge bug, and stale-waypoint fixes, 2026-09-13 (2nd pass)

Full detail lives in `news-waypoints.md` (colour scheme, `ty` taxonomy, anchor rules) - this is
the short version for anyone scanning this file only.

**Real bug found and fixed: the rank-badge-to-map click link (`ALLNEWS=NEWSG.concat(NEWSX)`)
was never updated when a third news bucket (`NEWSD`, then renamed around `cps`/`drill`) was
added**, so any waypoint in that third bucket silently fell out of the lookup - its rank number
in the list rendered with whatever default CSS colour was underneath (an orange-red "lead"
default, or plain grey) instead of being coloured and made clickable. Fixed by including every
bucket in the lookup array: `ALLNEWS=NEWSG.concat(NEWSD).concat(NEWSX)`.

**Also found live: a Skyharbour waypoint from a previous edition (dated 2026-09-03, outside
the current 7-day window, not mentioned anywhere in the current edition's text) was still
sitting in `BASIN_BUNDLE.news` and rendering on the map.** The `news` array is supposed to be
replaced wholesale each edition (see `news-waypoints.md`'s scope statement) - this was that
rule not being followed in practice. Removed. Check the whole array against the current
edition's actual content before publishing, not just what's being added that day.

**Colour scheme, current state:** four tiers now - green (`grade`), purple (`cps` - a fresh
handheld/downhole reading, split out from `drill` after two plain mobilization notices were
found wrongly rendering purple), orange (`geo` - geophysics/surveys, added so a real completed
survey doesn't look identical to a bare financing notice), yellow (everything else: `drill`,
`deal`, `mre`, `fin`). Geo is deliberately still counted under the "Other News" toggle, not a
5th legend row, per Ezra's explicit ask to keep the layer bar from growing. See
`news-waypoints.md`'s "Visual encoding" section for the full colour history and exact hex
values, and its "Proposed ranking-tier rule" section for an open, not-yet-decided proposal to
use this same four-way split as a ranking tier (grade > cps > geo > everything else) after
Ezra flagged a financing outranking a completed survey in Edition 003's own order.

## Standing rule, added 2026-09-12: one map dataset, not two - read this before Step 1/4a

**The two-pipeline problem, found and fixed 2026-09-12:** the two claude.ai pages and
basinwatch.ca used to get their map data from two independent sources that never agreed.
`data/bundle.json` (what basinwatch.ca builds from) is refreshed automatically every morning
by `.github/workflows/gis-export.yml` running `gis/basin_layers.py` - but that script never
produced a `claims` key at all, so basinwatch.ca's own "New Claims"/"Recent Stakers" numbers
were frozen at whatever a one-time seed put there, forever, while the daily brief kept
computing a fresh `claims` list by hand every morning and pushing it only into the two
claude.ai pages. Three surfaces, two different answers, and the site's answer was silently
wrong the whole time.

**The fix has two parts, both landed 2026-09-12:**

1. `gis/basin_layers.py` now computes `claims` itself (section 8b, right after the
   tenure pull it reuses) - the trailing-14-day `EFFECTIVED` window, built from the exact same
   live tenure query as the `tenure` layer, with the `corp` flag set via the documented
   keyword test (URANIUM/RESOURCES/GEM OIL/CORP/LTD/INC). Deliberately province-wide, same as
   `tenure` - the client engine's own `CLAIMS_F` filter (`northOK()` in `site/shell.html`)
   already clips it to the basin for display. `scripts/merge_map_bundle.py` was updated
   alongside it: `claims` is naturally volatile (a rolling window recomputed from scratch every
   run), so it's exempted from the normal shrink-floor guard and instead inherits `tenure`'s
   own accept/reject decision for that run (`DERIVED_FROM = {"claims": "tenure"}`).
2. **The daily brief no longer computes `claims` (or the map-facing lapsing counts) by
   hand.** Every run now starts by pulling the CURRENT `data/bundle.json` from
   `sockthief77/basin-watch` (a read-only `git clone`, or a direct `git pull` if running as the
   repo-bound Claude Code environment) and uses it as the base bundle for BOTH claude.ai pages,
   replacing every key except `news`: `tenure`, `claims`, `lapsed`, `boulder_grid`/
   `boulder_total`, `geochem_grid`/`geochem_total`, `ab_tenure`, `restricted`, `smdi`,
   `deposits`, `mines`, `footprints`, `conductors`, `lakes`, `places`, `highways`, `basin`.
   `news` stays hand-curated by the brief, exactly as before.
3. **The registry table's province-wide lapsing figures (the ones in the page's own prose -
   "102 dispositions lapse by 19 Sep" - which are intentionally NOT basin-clipped) are now also
   computed locally from that same pulled bundle's `tenure` array** (`tenure[i].x` carries each
   claim's own good-standing date), rather than a separate live ArcGIS query.

**What this means for Step 1 and Step 4a of the skill's own numbered steps: treat this doc as
authoritative over the skill's older described procedure, the same way `watchlist-and-sources.md`'s
"Majors clarification" already overrides the skill's wrong Step 3 text.** Concretely:

- **Step 1** no longer needs its own `EFFECTIVED`-window ArcGIS query, per-claim coordinate
  lookups, or Flin-Flon-style outlier exclusion - all of that now happens once, upstream, in
  `gis/basin_layers.py`. Step 1 still needs: the OBJECTID-watermark sanity check (weak signal
  only), the lapsed-register diff (still worth an independent live check against
  `claim-monitor-state.md`'s stored snapshot, since `data/bundle.json`'s own `lapsed` count can
  lag by up to an hour), and the Alberta tenure count.
- **Step 4a**'s old text about which `BASIN_BUNDLE` keys the daily run touches is superseded -
  the daily run now replaces every key EXCEPT `news` with the freshly-pulled `data/bundle.json`,
  then sets `news` from the day's own curation.

**Also recommended, not yet done:** delete `.github/workflows/publish-brief.yml` and
`scripts/merge_edition.py`. Both are confirmed dead code. No urgency.

## Standing note, added 2026-09-12 evening: always diff a saved local bundle against a fresh pull before republishing

Confirmed 2026-09-12: a bundle snapshot saved earlier the same afternoon can go stale by
publish time if `gis-export.yml`'s own automated refresh lands in between. Re-split the shell
straight out of a fresh source (either `Artifact.read` of each live claude.ai page, or a fresh
`git pull` if running repo-bound) rather than reusing a session-local bundle file.

## UI features - see `history.md` for the full session-by-session record

Item summaries: lake name labels at zoom (halo-background text, bounding-box centroid label
point), highway route name labels at zoom (grouped by name once per frame, `RTNUMBER1`/
`RTENAME1EN` fields on layer 134 Secondary, not 133 Primary), numbered news items linking to
map waypoints (colour-matched rank badge, click pans/zooms and reopens tooltip), click-to-
interact map (a `mapActive` boolean gates the wheel handler; activation area is the whole
`.mapcard` including legend toggles, hint text "Click to interact" top-left).

**Lake Athabasca no longer stays visible regardless of zoom** - removed the `a >= 0.15` size
exception; every named lake waits for the same `currentScaleKm()<=25` gate.

**Root cause found for lakes/rivers "cut off in odd places or missing completely": a real bug,
fixed.** `ringInBoxOK()` required every single vertex of a ring to fall inside the fixed
UTM13N working box - one stray point anywhere, and the *entire* feature was silently dropped.
Fixed by clipping instead of excluding: new `clipRingToBox()`/`clipLineToBox()` functions do a
proper Sutherland-Hodgman box clip. Applied to `lakes` and `highways` ingestion only (the two
that used `ringInBoxOK` for whole-ring/line features).

**Scale-bar-based zoom gate.** Both the lake and highway label gates use a `currentScaleKm()`
helper that replicates the on-screen scale bar's own rounding rule (largest of
`[10,25,50,100,200,500]` whose bar would render under 150px) and gates labels on `<=25`.

**Lake naming completeness - a real data gap in the government source, addressed via
gazetteer fallback.** `Hydrography/MapServer/80`'s own `LAKNAMEEN` field is blank for most
big, well-known lakes (Wollaston, Reindeer included). Fixed via a `SaskNamesDatabaseWater`
gazetteer fallback (point service, field `TOPONYM`) - took named count from 14/55 to 60/60
after the tie-break-by-HECTARES fix above.

## Named lake/river completeness, current state

As of the 2026-09-13 fixes: 60/60 lakes/rivers named in the live bundle, up from 14/55
originally. The remaining risk is dissolved-multi-lake blobs at this generalization tier with
no single correct name - not further investigated.
