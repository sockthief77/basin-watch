# Basin Watch - history and debugging notes

Not read on a normal daily run. This is where the "how we got here" narrative lives, moved
out of `map-pipeline.md`, `open-items.md` and the skill so those stay current-state-only.
Read this only when troubleshooting a regression or wondering why something is built the way
it is. Condensed from the original session-by-session logs, not verbatim.

## Map colour system evolution

- The persistent tenure fill started capped at 3 simultaneous colours (a validated 8-hue
  palette only clears 3 slots on an all-pairs CVD test at this data size), went through a
  hatch-pattern version, then a 16-hue version, before Ezra explicitly asked for every
  corporate holder to get its own colour regardless of similarity - landed on a golden-angle
  hue sequence, which is what's current.
- New Claims and Lapsing Within 7 Days both originally used a separate weekly `NEWHCOL`
  palette, independent of the persistent `HCOL` map. This caused two real bugs (New Claims
  and Lapsing both read differently from Sask Tenure for the same company) found on different
  days by Ezra comparing layers side by side. Both were fixed by switching to `HCOL` first,
  `NEWHCOL` only as a fallback for a holder with no `HCOL` entry. Do not revert either.
- A real key-matching bug (not a logic bug) once caused a specific company's claims to render
  grey despite correct ranking/colour code: the tenure feed's holder string had a doubled
  internal space that the claims-feed string didn't, so `shortHolder()` produced two different
  keys for the same company. Lesson: when a specific holder "isn't colouring" but the logic
  reads correctly on paper, check whether the *key* matches across data sources before
  assuming the logic is wrong.
- New Claims also went through a "coloured stroke only" version that Ezra correctly called
  not fixed - a thin dashed outline on small polygons at basin zoom is easy to miss. Fixed by
  painting a solid fill first, underneath the halo/outline. Lesson: check whether a colour
  fix landed on a FILL or just a thin STROKE before concluding the data/ranking is wrong.
- Grade-release waypoints (news stars) went through a typed-glyph system (diamond/triangle/
  square/hexagon per release type, company-coloured fills) that was built and then dropped
  the same day on Ezra's instruction - "make these all stars, light jasper blue." The colour
  itself has moved twice more since (light blue -> deeper blue -> bright turquoise) purely on
  aesthetic preference, no functional reason.
- Other News vs. Grade Releases z-order flipped once (Other News on top, so it wouldn't be
  obscured -> Grade Releases on top, so grade always wins a visual tie). Current state is
  documented in `map-pipeline.md` and `news-waypoints.md` - don't flip it again without being
  asked.

## Lakes query - three attempts before it worked

Layer 80 (Hydrography, coarsest lakes) is a real leaf feature layer, not a group layer, but
three separate problems stacked on top of each other before it returned real data: (1) a bare
`where=1=1` gets a generic 400 on this specific service - fixed with `OBJECTID>=0`; (2)
requesting full polygon geometry with no bounding window pulls every lake in the province at
full resolution and times out, which looks identical to "returned nothing"; (3) the actual fix
was keeping the bounding window, dropping the page size, and adding a server-side
`maxAllowableOffset` to pre-generalise the geometry. Worth remembering if any other polygon
layer on this service starts silently returning empty: it may be a timeout wearing the
appearance of a zero-result query, not a query-syntax problem.

## Other one-off endpoint gotchas

- Tenure 404s if `/Economy/` is dropped from the FeatureServer path.
- Transportation layer 56 and Hydrography layer 78 are both parent *group* layers - querying
  them directly 400s; query the numbered leaf layers instead (133/134 for roads, 80 for
  lakes).
- UrbanAreas' name field is `UMNM`, not `NAME` or any other guessable candidate - every town
  rendered nameless until this was found.
- `GOODSTANDI` was being fetched in the tenure query but the compact bundle builder wasn't
  copying it into the record - fixed by adding it to the output field list.

## Restricted Lands - source investigation

The first version sourced four general-purpose gis.saskatchewan.ca layers (Parks, Aboriginal
Lands, Planning, Urban Areas) that turned out not to match what MARS itself actually draws its
restriction colouring from. Loading the live MARS page and reading its own JS layer object
found the real source (`iscmaps.isc.ca/.../RestrictionsProhibitions/MapServer`, six
sublayers). That host is blocked from both the cloud container and the device sandbox, so
field names for it are still unconfirmed - `basin_layers.py` was rewritten to try a list of
candidate name fields per sublayer rather than assume one. Not yet re-run as of this note; see
`open-items.md` if it's still outstanding.

## Grid/layout bugs worth remembering the shape of

- A short "aside" element (the stock-price card) sitting beside long-form text in a CSS grid
  item caused a visible gap, misdiagnosed once (removing a `grid-row` span didn't fix it - the
  gap just moved). The actual fix was wrapping the long-form text in its own single grid cell
  so it block-stacks internally, rather than letting each of its child elements auto-place
  into its own grid row. General lesson: when a layout bug is reported as still present after
  a fix, render the actual page and look - don't re-derive the fix from CSS review alone a
  second time.
- Firefox specifically didn't fire click-to-open on map waypoints, because the click handler
  depended on a native `click` event that Firefox doesn't reliably fire after
  `pointerdown`/`pointerup` with pointer capture in play. Fixed by deciding click-vs-drag
  entirely inside the `pointerup` handler (a movement threshold) instead of waiting on a
  `click` event at all - browser-independent by construction. If the map canvas's pointer
  handling is ever touched again, keep the decision inside `pointerup`.

## The CRITICAL script-tag stripping bug (2026-09-08)

A scripted string-replace against a downloaded artifact HTML, run as part of inserting a news
item, over-matched and stripped the `<script>`/`</script>` tags around the entire
`BASIN_BUNDLE` line on both live pages - the raw ~6.3 MB JSON sat as visible page text and the
map engine fell back to an empty bundle (blank map, blank layer bar, blank Top 10 list) on
both pages simultaneously. Root cause was never pinned to an exact command, but the pattern
(both pages, identical stripped span) pointed at a post-build, pre-publish text edit rather
than a `build.py` bug. This is why every scripted/partial edit against a full artifact HTML
now has a mandatory post-publish check: exactly two `<script>` tags present, and the bundle
string between them still parses as JSON via `json.JSONDecoder().raw_decode` (a greedy regex
extraction can over-match past the real end of a 6MB object and throw a false error even when
the bundle is fine).

## Shell/bundle split - why it exists

Before the split, the ~6.3 MB single-line published page broke the Read tool's offset/limit
ranges outright and made Grep print `[Omitted long matching line]` instead of the actual
match, so every edit needed a Python offset-hunting workaround. Splitting into a ~95KB shell
(markup/CSS/engine) plus a separate untouched bundle.json cut the cost of an ordinary page
edit by roughly 70x. See `map-pipeline.md` for the current workflow.

## Watermark / count-endpoint reliability

The `returnCountOnly` count on the Mineral Dispositions layer was found to lag the true max
OBJECTID by one on at least one occasion, and a separate call mis-stated a 368-row result as
533 in its own prose summary while returning the correct rows underneath. Both are why the
current rule (`claim-monitor-state.md`) is to always run the actual attribute query and count
the literal returned rows, never trust an endpoint's own stated count or a change in the count
alone as proof nothing moved.

## Deficiency-deposit "$ to hold" feature build

Added to the map's lapsing-claim hover on Ezra's request. First pass considered a page-level
paragraph explaining the figures; Ezra wanted it computed silently and shown only on hover
over the "Lapsing Within 7 Days" polygons, no page prose. Built as a client-side JS
computation (claim polygon area via the shoelace formula on existing ring geometry, times the
Mineral Tenure Registry Regulations' per-hectare rate table) cross-validated against an
independent Python pass before shipping (claim counts and per-holder counts matched the page's
own published figures, with one small unchased discrepancy - see `claim-monitor-state.md` if
it resurfaces). Deliberately excludes contractor day-rate costs - Ezra asked to hold off until
he supplies his actual rates.

## UI features added 2026-09-12

Five features shipped to both live pages (Basin Watch and Basin Explorer) in one session:
lake name labels at zoom, highway name labels at zoom (code shipped, but no real labels will
show until the next `gis-export.yml` run, since the `basin_layers.py` field fix landed after
that day's run already happened), numbered news-list items linking to their map waypoint
(colour-matched rank badges; click pans/zooms the map and reopens the tooltip), company names
in the news list linking out to the company's official website (new `COMPANY_URL` lookup
table, ~60 entries), and a click-to-interact map so page scroll passes through until the user
clicks the map once. A sixth requested item - matching "Lapsing 8-14 Days" polygon opacity to
the 7-day tier - was dropped on Ezra's instruction once it turned out the two tiers' code was
already identical. Both pages were published from a fresh `Artifact.read` of the live pages
(not a stale session-local copy): Basin Watch went to Version 166, Basin Explorer to Version
101. Full technical detail is in `map-pipeline.md`'s "UI features added 2026-09-12" section.

## Privacy exposure found and fixed, and both pages republished with corrected map data (2026-09-13)

Ezra caught a real, previously-undisclosed privacy exposure: despite this project's standing
hard rule (see `watchlist-and-sources.md`) that the operator's real first name must never
appear in anything published or in any code committed to a public/live surface, "Ezra" was
present in comments across 5 files in the `sockthief77/basin-watch` GitHub repo -
`site/explorer-shell.html` (the template the live `basinwatch.ca/explorer` page builds from,
~33 mentions), `gis/basin_layers.py` (3 mentions, in a session-authored handoff that was never
checked), `README.md`, `scripts/merge_map_bundle.py`, and `.github/workflows/gis-export.yml`.
`site/shell.html` (the Basin Watch template) had already been scrubbed in an earlier session
and was clean. All 5 files were scrubbed to the project's established neutral-phrasing
convention ("Ezra's explicit request" -> "explicit requirement", "Ezra asked for X" ->
"Requested: X", etc.) and committed by Ezra directly via GitHub's web editor. Confirmed via
direct `curl` (not WebFetch, which gave an unreliable "0 occurrences" before the fix landed -
likely doesn't parse `<script>`-embedded JSON/comments) that `basinwatch.ca/explorer` went
from 37 occurrences of "Ezra" to 0 after the commits deployed. **Lesson for any future full-
file repo handoff: grep it for the operator's real name before sending, regardless of how
confident the authoring session is that it didn't introduce one.**

Separately, the same day's earlier `gis/basin_layers.py` fixes (see `map-pipeline.md`'s
"Follow-up fixes, 2026-09-13" section - gazetteer fallback for blank `LAKNAMEEN`, a severity-
thresholded self-intersection filter, and a claims/tenure existence check) were confirmed live
in `data/bundle.json` after Ezra manually triggered `gis-export.yml`: 48/55 lakes named (was
14/55), 118/119 highways named (was 0/119), 0 claims with no matching tenure record (was some
number of orphans, exact count not logged). Both claude.ai pages were then republished from
that corrected data - Basin Watch to **Version 169**, Basin Explorer to **Version 104** -
merging every `basin_layers.py`-produced key from a fresh `git pull` of `data/bundle.json`
into each page's own currently-live `news`/`generated`/`basin` values (same merge boundary
`scripts/merge_map_bundle.py` uses), rebuilt from a fresh `Artifact.read` of each live page
(confirmed byte-identical to the session's earlier extraction, so no intervening changes were
lost), and verified before publish: script-tag counts unchanged (3 watch / 2 explorer), bundle
JSON re-parses, 0 "ezra" mentions in either built file, Playwright load with no page errors,
and a zoomed screenshot showing a lake label rendering at zoom. This was the same-day follow-
up Ezra was asking about with "I still dont see any of the changes we just made" - the
client-side geometry/hint fixes from earlier had already published (v167/102), but the
gazetteer-named-lakes/highways/claims-orphan data fix required this separate bundle-merge
republish once `gis-export.yml` had actually run against the fixed `basin_layers.py`.

## Standing note: real git write access confirmed 2026-09-14

See `basinwatch-pipeline-fix.md`'s "Standing note: real git write access confirmed 2026-09-14"
section for the full detail - a Claude Code session/environment with `sockthief77/basin-watch`
selected as its repository has real git push access, confirmed by an actual test push. This
closes the access gap documented throughout this file and in `roadmap.md`'s former TOP
PRIORITY section, for that session type specifically. Sessions without that repo binding still
have the old read-only-clone constraint described throughout this file.
