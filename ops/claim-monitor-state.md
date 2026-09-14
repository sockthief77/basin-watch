
# Claim Monitor State

Machine-read by the daily uranium brief. Update the watermark every run.

**Never create a new dated file for run notes (e.g. `run-notes-YYYY-MM-DD.md`).** Write
findings directly into the relevant section of this doc (or `open-items.md` for standing
items), under a dated subheading if needed. A prior session tried the dated-file pattern on
2026-09-09 specifically to avoid a whole-file overwrite race with a concurrent session -
that reasoning was sound for that one moment, but the file was never folded back in
automatically and just sat there as a duplicate, growing project size and busting the
project-wide cache on every unrelated edit. If a concurrent-edit race is a real risk, use a
small, asserted string replacement against this file instead of a full overwrite - not a
separate file.

## Standing note, added 2026-09-14: real git write access confirmed for repo-bound sessions

See `basinwatch-pipeline-fix.md`'s "Standing note: real git write access confirmed 2026-09-14"
section. A Claude Code session/environment with `sockthief77/basin-watch` selected as its
repository has real git push access, confirmed by an actual test push. This closes the access
gap described throughout the CLOSED/RESOLVED sections below (fine-grained PAT tried and
abandoned; Cowork scheduled tasks confirmed to have no secret storage) **for that session type
specifically**. A generic Cowork/chat session without that repo binding still has the old
read-only-clone-only constraint documented below - check which kind of session you're running
in (`git push --dry-run` against this repo: succeeds -> push directly; denied with "not in
this session's authorized repository set" -> still use the manual paste-and-commit flow).

## Supplemental update, 2026-09-13 (same day as Edition 004) - Nexus Uranium trading-halt flag added mid-day

Not a new edition and not a scheduled run - a targeted addition to the already-live Edition
004, done at the user's request after a wide-net sweep test (see `watchlist-and-sources.md`'s
Sources section for the newly-mandatory newswire.ca/ACCESS Newswire sources this stemmed from).

**Finding:** a sweep against the newly-added mandatory sources (newswire.ca/Cision, ACCESS
Newswire) plus a recheck of the standard sweep sources against the live 7-day window (7-13 Sep)
turned up **Nexus Uranium Corp. (CSE:NEXU) - a CIRO trading halt, all issues, 10 September
09:18 ET** - found on newswire.ca, not caught by any source in the standard sweep, not in
Edition 004 as originally published. Everything else checked (JMN's full Athabasca Basin
topic-page history, ACCESS Newswire, TMX Newsfile, WISE Uranium, Saskatchewan EA projects,
CNSC mines-and-mills) confirmed clean - no other misses, nothing else in-window.

**Action taken:** added a new short note to the live Basin Watch page ("Flagged: trading halt,
no release yet") between the existing Majors note and the Out-of-basin note - not a numbered
ranked item, since a halt alone with no accompanying release is thin material for that. Also
appended a clause to Edition 004's own archive-row summary text noting the flag. No claims/map
data touched (bundle `claims`/`news` keys unchanged) - this was a text-only edit to
`edition_top_html`. Basin Watch -> **Version 172**. Basin Explorer not republished (no map data
changed). `edition.json` regenerated from the edited shell and re-verified via the repo's own
`scripts/build.py` (placeholders substituted once, bundle re-parsed as JSON) before delivery.

**Watch for a resumption notice or an actual release from Nexus** on tomorrow's run - if one
lands, this flag should either be upgraded to a real numbered/context item or removed if the
halt turns out to be procedural with nothing behind it.

## Run note, 2026-09-13 (later, unscheduled/interactive-style run) - real BASIN_BUNDLE syntax-error bug found and fixed on the live Basin Watch page

Run started to produce today's edition per the daily brief prompt. Before touching anything,
re-read both live claude.ai pages fresh per the standing "always diff a saved local bundle
against a fresh `Artifact.read`" rule, and confirmed via the news-sweep and claim-monitor
sub-passes that nothing material had changed since the Edition 004 run logged above earlier
the same day: same six ranked items, same lapsing figures (98/95), same Google Finance quotes
(all still dated Friday 11 Sep - markets closed, today is a Sunday), same stale `data/bundle.json`
(`generated` field still 2026-09-09). One new fact surfaced: newswire.ca and a general search
turned up the actual CIRO bulletin behind the already-flagged Nexus Uranium (CSE:NEXU) halt -
issued 10 September 9:07 AM ET, reason stated as "improper dissemination of news." No
resumption notice or corrective release has been issued yet, so the flag stays a flag, updated
with the now-known reason. Since nothing else changed, this stayed a text-only supplemental
edit to the live Edition 004 page rather than a new numbered edition, consistent with the
supplemental-update entry above and with the skill's "no new ranked item, no re-ranking needed"
guidance.

**A real, separate bug was found and fixed while re-splitting the live Basin Watch page for
that text edit.** The published page's `<script>window.BASIN_BUNDLE=` assignment had two
stray literal underscore characters immediately wrapping the JSON literal on both sides -
`window.BASIN_BUNDLE=__{...}__;` - which is not valid JavaScript (`identifier` directly
followed by an object literal is a syntax error). Loading the actual saved artifact HTML in a
headless Chromium session (via Playwright, already available in this environment) confirmed
this directly: a page error (`Unexpected token '{'`) fired on load and `window.BASIN_BUNDLE`
was left `undefined` - meaning the entire interactive map (layer bar, Recent Stakers panel,
Favourites, Top 10 holders, the canvas itself) had zero data and could not have been rendering
for anyone visiting the live page, regardless of what the masthead/news-list content above it
showed. Basin Explorer's own copy of `BASIN_BUNDLE` was checked the same way and was already
clean (no wrapping, parsed and loaded fine) - the bug was isolated to the Basin Watch page
only, not systemic to both pages.

Before assuming this was a real live-site bug rather than an artifact of this session's own
read/save tooling, it was verified directly: two disposable diagnostic artifacts (a small one
and a ~7.3MB one, matched to Basin Watch's real size) with large embedded JSON blobs were
published and re-read through the exact same tool path used for the real page. Neither showed
any stray-underscore wrapping at any size, confirming the tooling round-trips large inline
JSON cleanly and the wrapping found on the real page was genuine content already live, not
something introduced by reading it. Both diagnostic artifacts were deleted immediately after
the test.

**Fix applied and verified before publishing:** the two stray underscore characters were
removed from both sides of the JSON literal (a precise index-based edit off the JSON decoder's
own parse boundaries, not a fragile text-substring replace, since a plain string match against
"__" or similar could have been ambiguous elsewhere in a 7MB file). The corrected page was then
actually loaded in headless Chromium before publishing (not just re-parsed as JSON): zero page
errors, `window.BASIN_BUNDLE` populated with all 20 expected keys, `claims`/`news` counts
matching the values already confirmed correct (81/6), the layer bar and Recent Stakers panel
both populated with real content, and a screenshot after a simulated click confirmed the map
canvas actually draws the basin outline, claim markers, and news stars - not just "loads
without throwing." Script-tag count held at 3 (unchanged from before the edit), matching the
standing rule that Basin Watch (with its newsletter-modal script) is 3, not the older
universal-2 assumption. Published as Basin Watch -> **Version 173**. Basin Explorer was not
republished, since its `BASIN_BUNDLE` was already clean and neither `claims` nor `news` changed
this run.

**Root cause not investigated further this run** (out of scope for a normal daily run, and
this session has no way to inspect the history of who/what introduced it) - worth a future
session checking whether any documented split/rebuild script or manual edit path could produce
a `__<value>__` wrapper around `BASIN_BUNDLE` specifically, since if that pattern exists
somewhere in this project's own tooling (rather than being a one-off manual mistake), it could
reproduce on a future edit. Given how severe the symptom is (the entire map silently
non-functional with no visible error on the page itself, and not something a text-based fetch
or JSON-only verification would ever catch - only an actual browser load exposes it), it is
worth adding a real headless-browser load-and-page-error check as a standing pre-publish step
for Basin Watch specifically, not just the JSON-reparse and script-tag-count checks already in
place, since JSON re-parsing alone (as documented as the skill's own "best verification") would
not have caught this bug - the JSON substring inside the wrapper was itself always valid JSON,
just not validly embedded as a JS statement.

No claims/news bundle values changed this run (still 81/6, matching the already-pulled stale
`data/bundle.json`), so no `edition.json`/basinwatch.ca handoff was generated this run - the
Edition 004 handoff already delivered earlier the same day still stands as today's edition for
basinwatch.ca, and the fix above only affects the claude.ai Basin Watch artifact, which has no
basinwatch.ca equivalent to resync (basinwatch.ca's own static `site/shell.html` build is a
separate file entirely, per `map-pipeline.md`, and was not checked for the same bug this run -
worth a future session checking it too, ideally with the same headless-browser load check
rather than a text-only fetch).

## Run note, 2026-09-13 (same day) - manual/interactive invocation, not the 08:30 scheduled trigger

**Correction, same day:** an earlier pass at logging this run's note replaced this entire
file's content instead of appending to it, wiping the two-pipeline fix history, all query
recipes, the Layer 3 snapshot list, and every other standing section below. Caught and
restored the same turn from the version already read into this conversation. Lesson (same
one `news-waypoints.md` already logged twice for itself): a full-file `project_write` against
a long, load-bearing doc must carry the complete prior content forward, not just the section
being changed - diff against the last known-good text before writing, don't rewrite from
memory of "what this run needs to say."

Run started 13:39:37 UTC (07:39:37 America/Regina). User asked to run the daily brief now, as
a normal scheduled run would proceed, timing the whole thing.

- **Claim monitor (Step 1):** `git clone` of `sockthief77/basin-watch` succeeded (read-only,
  confirmed working, consistent with every prior session's finding that read access via clone
  is fine even when direct `curl`/WebFetch to gis.saskatchewan.ca or raw.githubusercontent.com
  is blocked). Latest commit `047a2ff`, "Daily GIS export refresh (2026-09-13)", authored
  2026-09-13 05:04 UTC - but `data/bundle.json`'s own `generated` field still reads 2026-09-09
  (4 days stale internally, despite a same-day commit) - flagged for a future session to check
  `gis-export.yml`'s own logic, not fixed this run. Diffed the pulled `bundle.json` against the
  claude.ai pages' existing embedded bundle: `claims` (81), `tenure` (7,460), `lapsed` (374),
  `ab_tenure` (74) were already byte-identical - no map-data merge needed for those keys. Only
  `lakes` differed (55 -> 60 entries, all now named, reflecting the river-naming/gazetteer fix
  described in `map-pipeline.md`) - adopted the new `lakes`. Lapsing bands recomputed directly
  from the `tenure` array (today = 2026-09-13): **98 dispositions lapse by 20 Sep** (Ryan Kalt
  17, Eagle Plains 13, Murchison Minerals 12, Orano 11, Greenridge 10, Inspiration Energy 8,
  Jasper Mowatt 5, 92 Energy Canada 4, Denison 3, Cosa Resources 3), **95 lapse 21-27 Sep**
  (Ryan Kalt 76 - a real figure, not a parsing artifact, worth a closer look at what this
  individual holder's block actually is; Greenridge 8, Argo Gold 3, then smaller holders).
  Claims (14-day window) unchanged at 81 (42 corporate / 39 individual) - the underlying
  data's last effective date is still 2026-09-11, consistent with the stale `generated` flag
  above.
- **News sweep (Step 2):** full sweep for the 2026-09-07 to 2026-09-13 window. No releases
  dated 2026-09-12 or 2026-09-13 were found for any roster company - every substantive item
  in-window is the same set already on Edition 003 (Purepoint's Nova assay, IsoEnergy's
  Larocque East completion, Terra Clean Energy's financing, Terra North/GEMC's Charlot-Neely
  radiometric anomalies, Green Canada's Marshall mobilization, Belmont's Crackingstone gravity
  survey). Per the skill's own "no new ranked item, no re-ranking needed" guidance, ranking
  carried forward unchanged. ATHA's Rib North (Nunavut, out of basin) and CanAlaska's Key
  Extension mobilization stay in their existing context notes, unchanged.
- **Price/market context (Step 4):** ISO, PTU, SASK(ATHA), TCEC quotes refreshed (all still
  dated 11 Sep - Friday's close, markets closed the intervening weekend). GEMC still dashed
  (stale Aug 27 quote, same recurring issue). GCUC and BEA could not get a fresh quote this run
  (GCUC:CNSX 404'd on Google Finance; BEA:CVE hit repeated WebFetch rate-limiting that didn't
  clear within the run) - both dashed per the hard freshness rule rather than carrying forward
  last edition's numbers. U3O8 ticker unchanged: Aug month-end US$89.68/lb x 1.3866 = CA$124.35/lb.
- **Artifacts (Step 4a):** both claude.ai pages re-split from a fresh `Artifact.read`, merged
  bundle (lakes updated, everything else unchanged except `news` which was also unchanged),
  edition text updated (date, window, edition number 003->004, lapsing figures, registry
  table, archive section with 003 now linked to its archive page). Basin Watch script-tag
  count held at 3, Basin Explorer at 2, both re-verified via `json.JSONDecoder().raw_decode`
  before publish. Archive snapshot of the outgoing Edition 003 published as its own one-time
  artifact (`https://claude.ai/code/artifact/796c8a77-fddd-4d05-8328-53d609121360`) before
  overwriting the live page. Basin Watch -> Version 171, Basin Explorer -> Version 105.
- **edition.json (Step 4b):** extracted `edition_top_html`/`edition_bottom_html` from the
  freshly-rebuilt shell against the actual `<!--__EDITION_TOP__-->`/`<!--__EDITION_BOTTOM__-->`
  placeholders in the cloned repo's `site/shell.html`. Verified with the repo's own
  `scripts/build.py`: both placeholders substituted exactly once, `dist/index.html` and
  `dist/explorer/index.html` built clean, bundle re-parsed as JSON. Delivered to the user
  inline as a fenced code block and via `SendUserFile`, per standing instruction. The
  basinwatch.ca commit itself is the one manual step - user is completing it now.
- **Note:** this was a manual/interactive invocation of the skill, not the 08:30 scheduled
  trigger firing - logged here anyway since it's a real production run of the same pipeline.

## Two-pipeline fix, 2026-09-12 (same day as Edition 003, later - an interactive session, not the scheduled run)

Ezra asked, after seeing the claude.ai pages and basinwatch.ca show visibly different map
numbers (New Claims, Lapsing tiers, Boulder Heat, Recent Stakers) on the same day: "how come
the new and lapsing claim count is off then?" then, after an explanation, asked for a plan to
fix the two-pipeline split AND make each run as automated as possible. Full investigation and
fix, both approved and executed the same session:

**Root cause, confirmed by reading the actual repo code (not just the docs, which turned out
stale on this point):** `gis-export.yml` already runs `gis/basin_layers.py` on GitHub's own
runners every morning at 07:30 America/Regina - fully automated, no laptop involved, contrary
to what `map-pipeline.md` said before this fix. But `basin_layers.py` never produced a
`claims` key at all (confirmed by grep - zero mentions), so `data/bundle.json`'s `claims`
field (what basinwatch.ca's map actually reads) was frozen forever at whatever a one-time
seed wrote (61 entries, dated around 2026-09-09) - nothing in the automated pipeline ever
touched it, and the daily brief's own by-hand `claims` computation only ever went into the two
claude.ai pages, never into the site's `data/bundle.json`. Three surfaces, two genuinely
different data sources. Separately confirmed: `tenure` in `data/bundle.json` is deliberately
province-wide (the module's own docstring says so - "province-wide tenure" is the one
exception to the basin-window clip), and scanning it locally for GOODSTANDI dates reproduced
the day's live-query lapsing figures (102/94) exactly - so the registry table's province-wide
lapsing prose and the map's own basin-clipped "Lapsing" toggle counts were always measuring
two different populations by design (`northOK()`/`ringNorthOK()` clip at render time), not a
bug on either side.

**Fix, both files written, syntax-checked, and exercised against synthetic data before
handoff (no live gis.saskatchewan.ca access from this session to test against the real
endpoint, so synthetic-data testing is the strongest verification available here):**

- **`gis/basin_layers.py`**: new section 8b, right after the existing tenure pull, computes
  `claims` from the exact same live query (`tn`) already fetched for `tenure` - no second
  ArcGIS round-trip. Trailing-14-day `EFFECTIVED` window (today inclusive), `corp` flag via
  the same URANIUM/RESOURCES/GEM OIL/CORP/LTD/INC keyword test the front-end has documented
  (but never had a real producer for) since it shipped, coordinates via bounding-box midpoint
  of each claim's own ring (already in hand from the tenure pull, no extra geometry call).
  Deliberately left province-wide, matching `tenure`'s own convention - `site/shell.html`'s
  `CLAIMS_F` filter already clips it with `northOK()` at render time, confirmed by reading
  that code directly (`var CLAIMS_F=(B.claims||[]).filter(function(c){ return
  !isSGO(c.o)&&northOK(c.x,c.y); });`), so the Python side doesn't need to duplicate that
  filter. **A real bug was caught by testing, not review**: the first version used
  `datetime.timedelta(days=14)` for the cutoff, which actually produces a 15-day-inclusive
  window (or equivalently, lands one day short of the intended start) - a trailing-14-day
  window that includes today needs the cutoff at `days=13)` back. Caught by a synthetic
  boundary-date assertion before this ever reached a real run; fixed to `days=13`, re-tested,
  passed. Also fixed the module's stale "RUN FROM WINDOWS" docstring to describe the actual
  `gis-export.yml` automation.
- **`scripts/merge_map_bundle.py`**: the existing `SHRINK_FLOOR` guard (rejects a same-day
  drop of more than 50% in any list-valued key, on the theory that real registries don't move
  that fast) would have wrongly frozen `claims` again the first time a big staking batch aged
  out of its own 14-day rolling window on a day when nothing else happened - a `claims`
  layer's day-to-day count is naturally volatile in a way `tenure`/`lapsed`/etc. aren't, since
  it's a full independent recomputation each run, not an incremental diff. Fix: a new
  `DERIVED_FROM = {"claims": "tenure"}` mechanism - `claims` skips its own shrink check
  entirely and instead inherits whatever accept/reject decision `tenure` got that run (same
  underlying query, so if `tenure`'s pull looked like a failure, `claims` is protected right
  along with it; if `tenure` succeeded, `claims` is always taken fresh, any size). Verified
  with two synthetic end-to-end runs of the actual patched script: (1) tenure pull succeeds,
  claims legitimately shrinks past the 50% floor on its own -> claims value IS updated
  (correct - not a real failure); (2) tenure pull looks like a failure (crashed from 100 to 3
  records) and claims also looks empty -> claims correctly KEPT at its old value, not
  overwritten with the bad `0` (correct - a real failure, protected).
- **Daily brief's own procedure, corrected in `map-pipeline.md`** (the skill file itself is a
  reconstruction this project can't edit directly - see the note at the top of that project;
  this doc and `map-pipeline.md` are the authoritative override, same pattern already used for
  the Step 3 majors-ranking correction): every run now pulls the day's `data/bundle.json` from
  the repo (read-only `git clone`, already proven reliable this session) and uses it wholesale
  as the base bundle for both claude.ai pages - every key except `news` - instead of computing
  `claims` by hand and carrying forward whatever was last manually merged for everything else.
  The registry table's own province-wide lapsing prose is now read locally off that same
  pulled bundle's `tenure` array instead of a separate live ArcGIS query. Net effect: the
  brief's Step 1 shrinks to just the OBJECTID/lapsed-register sanity checks and the Alberta
  count; Step 4a's map update becomes "take the pulled bundle, set `news`, publish" instead of
  a two-key surgical edit against yesterday's embedded data.
- **Recommended but not yet done**: delete `.github/workflows/publish-brief.yml` and
  `scripts/merge_edition.py` - confirmed dead code (the exact base64-Artifact-handoff
  mechanism the RESOLVED section below already documented as a dead end; `merge_edition.py`
  always fails soft and has never once actually updated `data/edition.json`). Harmless as-is,
  but exactly the kind of stale-automation-that-looks-live clutter that made this
  investigation harder than it needed to be. No urgency.

**Status as of this note: both code files are written and locally verified, but NOT yet
committed to the repo** - this session has no git push access (confirmed, same limitation as
every prior session - see the CLOSED section below). They're handed to Ezra as full-file
replacements to paste into GitHub's web editor, same pattern as every other repo change this
project has made. **Check the next `gis-export.yml` run's Actions log and the resulting
`data/bundle.json`'s `claims` key once he's pasted them - that first real run is the actual
end-to-end proof, since this session's testing was necessarily against synthetic data, not
the live ArcGIS endpoint.** Once confirmed live, update this note and stop treating the daily
brief's old by-hand `claims`/lapsing-query procedure as current anywhere it's still described.

## Standing rule, added 2026-09-12: log completion time and a cost proxy every scheduled run

Added after Ezra asked whether the pipeline reliably makes the 9:00am publish deadline, and
found the project had no actual measured data to check that against - only a written estimate
("~8:30-8:50am") in `daily-publish-instructions.md` that was never verified against real runs.
Also part of a push to cut per-run token cost - see `roadmap.md`'s "Automation and token cost"
section, not yet acted on as of this note.

**Every scheduled run must add one line to a running log in this file** (new subsection below,
`## Run timing and cost log`), before or as part of the existing dated run note - not a
separate file, same rationale as the rule above:

```
2026-09-12 | fired 08:30 | posted <HH:MM> | <total elapsed> | subagent used: yes/no | SMDI scrape: cached/full | notes
```

- **`posted`** = the wall-clock time (America/Regina) this run's chat reply with the
  `edition.json` code block actually went out - read from the run's own turn timestamp if
  available; if not directly readable, estimate from context (e.g. "before 8:50, exact time
  not visible to the run itself") rather than skip the line entirely.
- **`subagent used`** - whether the news sweep ran via a sub-agent (per the skill's Step 2) -
  this is very likely the single largest per-run cost driver (roadmap.md item 2: "move
  deterministic work out of the model's reasoning loop" and item 3: keeping the
  `watchlist-and-sources.md` roster out of the prompt), so it's worth knowing whether it ran
  every time or only on some runs.
- **`SMDI scrape`** - cached (fast, just a lookup) vs. full (~15-20 min, only the first run
  ever needed this, per `map-pipeline.md`) - flag if a full scrape ever recurs, since that
  would blow the 9am deadline outright.
- Free-text notes: anything unusual that made the run slower or more expensive than normal
  (retried queries, WebFetch rate-limiting, extra editorial back-and-forth).

**Purpose:** after 1-2 weeks of real entries, this answers two separate questions with actual
data instead of estimates - (1) is the 8:30 trigger time leaving enough buffer for the 9:00am
deadline plus Ezra's manual paste-and-commit step, and (2) which run steps are actually
expensive, to prioritize the `roadmap.md` cost-cutting backlog by real impact rather than
guesswork. Revisit both questions once entries accumulate - don't re-guess from a single day.

## Run timing and cost log

(New entries go here, most recent first.)

2026-09-13 (later) | non-scheduled run producing today's edition, after Edition 004 was already
live from an earlier run the same day | found nothing new in news/prices/claims versus the
earlier same-day edition (weekend, markets closed, no new roster releases) except the CIRO
halt-reason detail for Nexus Uranium, applied as a text-only supplemental edit rather than a
new numbered edition | also found and fixed a real JS syntax-error bug in the live Basin
Watch page's `BASIN_BUNDLE` embedding (stray `__` wrapper breaking the entire interactive map) -
verified with a headless-Chromium load before and after the fix, confirmed via two disposable
diagnostic artifacts that this was genuine live-page content, not a read/write tooling
artifact | Basin Watch -> Version 173, Basin Explorer not touched (already clean, no data
change) | no `edition.json`/basinwatch.ca handoff generated (no claims/news change to hand
off) | notes: this is the first run in this project's history to load a saved artifact HTML
file in an actual browser (Playwright/headless Chromium, available in this environment) rather
than relying solely on text-based JSON re-parse and script-tag-count checks - worth adopting as
a standing pre-publish step for Basin Watch given what it caught.

2026-09-13 (supplemental) | manual/interactive mid-day update, not a full run | Nexus Uranium
trading-halt note added to already-live Edition 004 | no subagent, no claims/price refresh -
text-only edit to `edition_top_html` plus the archive-row summary | Basin Watch -> Version 172,
Basin Explorer not touched.

2026-09-13 | manual/interactive run, not the 08:30 trigger | started 13:39:37 UTC | posted:
pending user's "site is live" confirmation, total elapsed to be reported then | subagent used:
yes, both Step 1 (claim monitor bundle pull) and Step 2 (news sweep) ran via general-purpose
subagents in parallel | SMDI scrape: not touched this run | notes: several Google Finance
quote fetches hit the documented ~60s rate limit (GCUC, CVV, BEA); GCUC and BEA never cleared
within the run and were dashed rather than retried indefinitely. `git clone` of
`sockthief77/basin-watch` succeeded cleanly. An early attempt to log this very run note
overwrote this file's full content instead of appending - caught and restored same turn, see
the correction note above.

2026-09-12 | fired 08:30 America/Regina (a Saturday - the scheduled task fires every day, no
weekday-only guard) | posted: exact wall-clock not directly visible to the run itself, well
within the run turn | total elapsed: long - two research subagents (claim monitor + news
sweep) ran in parallel, then price fetches, shell/bundle split and edit, and a read-only
`git clone` for the site/shell.html placeholder boundaries and a `build.py` dry run | subagent
used: yes, both Step 1 (claim monitor ArcGIS check) and Step 2 (news sweep) ran via
general-purpose subagents in parallel | SMDI scrape: not touched this run (map-pipeline's SMDI
section is Ezra's own-machine job, out of scope for the daily brief) | notes: several Google
Finance quote fetches hit the documented ~60s rate limit (GEMC, CanAlaska); one retry each,
no other blockers. `git clone` of `sockthief77/basin-watch` succeeded cleanly (read-only,
depth 1) and was used only to find the exact `<!--__EDITION_TOP__-->`/`<!--__EDITION_BOTTOM__-->`
boundaries in `site/shell.html` and to run `scripts/build.py` as the skill's "best
verification" step before handing off `edition.json` - both succeeded with no structural
errors (2 script tags, both placeholders found exactly once, bundle re-parsed as JSON).

## Finding, 2026-09-12: OBJECTID watermark does not reliably detect new staking - EFFECTIVED-window is the real detector

The Step-1 claim-monitor check (Task 1, "new claims since watermark") returned zero new rows
for `OBJECTID > 7468`, and a `1=1` count-only query also returned 7468, so on the surface
nothing looked new. **It wasn't true.** A separate EFFECTIVED-window query (2026-08-30 through
2026-09-12) turned up 81 dispositions newly staked in that period - all of them already
carrying `OBJECTID` values well below 7468 (spot-checked: the true current max `OBJECTID` is
only **7462**, found via `OBJECTID > 7462` returning zero rows and `OBJECTID > 7455` returning
the top 7 - i.e. `OBJECTID` on this service is not chronological and does not correlate with
recency at all, and the 7468 "total feature count" is not the same number as "max OBJECTID"
(there is a real, unexplained gap between the two - not investigated further this run).
**Conclusion: the OBJECTID-watermark check (skill Step 1, Task 1) should be treated as a
weak/supplementary signal only, never as proof that nothing was staked.** The EFFECTIVED-window
scan (which already feeds the `claims` bundle key) is the reliable new-staking detector and
should be read as primary from here on. Recorded here so a future run doesn't re-trust a clean
OBJECTID diff at face value.

## Finding, 2026-09-12: four of this window's new claims are the same Flin Flon outlier block from 2026-09-09/10, correctly excluded from the map again

Of the 81 EFFECTIVED-window dispositions, four (MC00024174, 175, 176, 177 - all GEM OIL INC.)
centre on approximately -101.9, 54.9 - confirmed by direct bounding-box-midpoint queries
(`outSR=4326`), i.e. the same ~370 km-outside-the-basin Flin Flon-area block already flagged
in the 2026-09-09/10 editions' archive text. These four are excluded from this edition's
`claims` bundle key and from the Recent Stakers panel/registry table counts, same as before -
they're geographically outside the working basin bounding box the map already clips everything
else to. A fifth claim initially missing from the live `tenure` bundle (MC00024178, an
individual holder, Gary Clayton Dunn) resolved to a real in-basin position (-105.2871, 56.6857,
via the same bbox-midpoint method) once queried directly and IS included in this edition's
claims layer.

## Finding, 2026-09-12: weekend edition - Google Finance quotes freshness rule interpreted as "most recent trading day", not literal calendar date

2026-09-12 is a Saturday. Every Google Finance quote fetched this run (ISO, PTU, BEA, CVV,
GCUC, TCEC) returned an as-of date of "September 11, 4:00 PM" - Friday's close - because
markets are closed on Saturday, not because the quotes are stale. **The skill's Step 4 hard
freshness rule ("must carry a returned as-of date equal to the run date, or print a dash") was
written with weekday runs in mind and does not explicitly address what to do when the run date
itself is a non-trading day.** Since the scheduled task's cron fires every day including
weekends, this is a real recurring case, not a one-off edge case. **Reading taken this run:**
treat "the most recent trading day's close" as satisfying the freshness rule when the run date
is a weekend/holiday, since a literal reading would print all-dashes on every single weekend
edition forever, which is a worse outcome than showing Friday's real close clearly dated "11
Sep" (the existing per-item date label already states which day the quote is from - it has
never claimed to be "today"). GEMC's quote was still genuinely stale (Aug 27) under either
reading and was dashed as usual. **Flagging this interpretation for Ezra to confirm or
override** - if he wants literal dashes on weekend editions instead, that's a one-line change
to how this case is handled, but nobody had settled it before this run needed an answer.

**Reconfirmed 2026-09-13 (later run): 2026-09-13 is also a non-trading day (Sunday)** - every
Google Finance quote fetched that run again returned Friday 11 September's close, consistent
with this reading, and no override instruction has been given since.

## Finding, 2026-09-12: registry table's "Staked" row was still framed as a 7-day window on the live page, not the 14-day window the skill and map panel already use

The 2026-09-11 edition's live page still showed "Staked 5-11 Sep, corporate: 0, individuals: 0"
in the registry table, and its detail text for "Active dispositions" claimed "no new claims
staked in the past seven days." Both were carried over from before the 2026-09-11 staking-
window widening and were never updated to match it - the map's own "Recent Stakers" panel
heading had already been renamed, but the table row text and its 7-day framing hadn't. Fixed
this edition: the two "Staked" rows now read "Staked 30 Aug - 12 Sep" (the actual trailing-14-
day range) with real counts (38 corporate, 39 individual, the Flin Flon outlier excluded), and
the "Active dispositions" detail text no longer asserts "no new claims" - it points at the two
rows below instead. Worth checking on a future run that this framing doesn't drift back.

## Correction, 2026-09-11 (same run, caught by Ezra within the hour): majors ranking + lapsing-within-7-days both fixed

Two mistakes in the 08:30 Edition 002 run below, both caught and corrected the same morning
via chat, both republished (Basin Watch -> Version 144, Basin Explorer -> Version 88,
`edition.json` re-sent as a corrected file).

- **Majors ranking.** The run below read the skill's Step 3 literally ("never forced through
  the numbered ranking") and moved IsoEnergy out of the numbered list into the majors note.
  **Ezra's explicit correction: "I DO want majors on the numbered list" / "a majors item may
  still take a numbered slot when it's clearly the week's most material release."** So majors
  are not automatically excluded - a major's release competes for a numbered slot by ordinary
  editorial judgment of materiality, same as any other item, it just doesn't get forced through
  the 9-tier point scale the way junior items do (a lot of majors' news is cps-only, which
  would score artificially low on that scale). IsoEnergy restored to rank #2 (its Edition 001
  slot), items renumbered 03-06. **The skill's own Step 3 text is still wrong** - written
  guidance is now in `watchlist-and-sources.md`'s "Majors clarification" section until the
  skill itself can be corrected (no `propose_skills`-equivalent tool was available this
  session to fix it directly).
- **Lapsing-within-7-days, root cause found and fixed.** The block reported below (`PROXY_REJECTED`,
  HTTP 403) turned out to be specifically the combination of **two quoted date literals joined
  by `AND`** in one where-clause - a single-bound query (`GOODSTANDI<=timestamp'...'` alone, no
  `AND`) goes through cleanly. Fix: two single-bound queries instead of one combined range
  query - see the new query recipe below. Real number obtained: **45 dispositions lapse by
  18 September** - Eagle Plains 13, Orano 11, an individual holder (Jasper jon arthur Mowatt)
  5, Golden Band 3, Argo Gold 2, Willgrass Resources 2, Debbie Dahrouge (individual) 2,
  1255004 B.C. Ltd. 2, then singles (Greenridge, Atha Energy, Inspiration Energy, 92 Energy
  Canada) and one 50/50-held disposition (randy andrew powder / Steve Alphonse Powder). Cross-
  referencing DISPOSIT_1-vs-OWNERS in one combined query (3 outFields) also hit a 403 a few
  times, but the same 2-field query (`DISPOSIT_1,OWNERS` alone, no `GOODSTANDI`) worked - the
  pattern isn't fully pinned down (possibly a WAF heuristic on multi-field + literal
  combinations, possibly just transient), so if a future run hits a 403 on a query that worked
  before, try dropping to fewer outFields before concluding the endpoint is down.
- **Also observed 2026-09-11: WebFetch itself rate-limits on Google Finance** (`PROXY_REJECTED`,
  HTTP 429, "wait ~60s") after a handful of back-to-back quote fetches in the same run. Not the
  same failure as the ArcGIS 403s above - space price-card fetches out or expect to retry.
  **Reconfirmed 2026-09-12**, same pattern, one retry each cleared it.
- **Map waypoints for the two "no confident anchor" items (Terra Clean Energy/South Falcon
  East, Green Canada Uranium/Marshall) found the same day, at Ezra's request to chase them
  down rather than leave them off.** Both required going past the local bundle's `smdi`/
  `deposits` arrays into either a web search for a named deposit on the property, or a direct
  ArcGIS holder search:
  - **South Falcon East -> Fraser Lake Zone B deposit.** A web search for "Skyharbour Terra
    Clean Energy South Falcon East" surfaced that the property hosts the **Fraser Lakes B
    deposit** (a rare-earth showing recognized by the Government of Canada) - that name was
    then found directly in the local bundle's `deposits`/`smdi` arrays as "Fraser Lake Zone B"
    (-104.9317, 57.0479, SMDI #5289). Cross-validated against the company's own stated "50 km
    east of Key Lake Mill" description (Key Lake's coordinates from the `mines` array,
    bearing+distance gives ~-104.82/57.20 - within ~20 km of the deposit anchor, consistent).
  - **Marshall -> disposition MC00014967.** An ArcGIS `OWNERS LIKE '%BASIN ENERGY%'` search
    (Basin Energy Ltd. sold Marshall to Green Canada) returned 12 claims, 11 of them
    "BASIN ENERGY GEIKI CORP." (a different Basin Energy project, Geikie, already separately
    on the roster) and exactly one, **MC00014967**, held "CANALASKA URANIUM LTD.: 60%;
    BASIN ENERGY NORTH MILLENNIUM CORP.: 40%" - matching Green Canada's disclosed option into
    "North Millennium's underlying interest" precisely. Geometry for a single claim was
    requested and its **bounding-box midpoint** used as the anchor rather than an average of
    all ring vertices (331 of them) - the skill's standing warning that WebFetch mangles
    long coordinate-array transcription applies just as much to summarizing many vertices into
    a centroid as to listing full lists of rows, so the 4-number bbox is the safer derivation.
  - **General technique worth reusing**: when a project name isn't in the local bundle's named
    deposits/SMDI arrays, search for what specific historical showing/deposit sits on that
    property (usually named in a technical-report or a PR about it), then look THAT name up
    locally - much higher hit rate than guessing coordinates from a prose location description
    alone. An ArcGIS `OWNERS LIKE '%<partial company/predecessor name>%'` search is the fallback
    when no named deposit exists, and single- or double-word LIKE patterns went through fine
    (no 403s), unlike the `IN (...)` multi-value list tried earlier the same day. **Reconfirmed
    2026-09-12: an `IN (...)` list with 5 quoted values still 403s; single `DISPOSIT_1='...'`
    equality queries, one at a time, do not.**

## Run note, 2026-09-12 (daily brief, Edition 003) - scheduled 08:30 America/Regina run

Unattended scheduled run. Reading taken per "Unattended runs": full sweep, full publish chain
including the edition.json handoff, no computer connection this run (none exists for this
task and none should be added). Both research subagents (claim monitor, news sweep) ran in
parallel per the skill's Step 2 guidance.

- **Claim monitor (Step 1):** `OBJECTID > 7468` returned zero rows and a `1=1` count also read
  7468 - looked clean, but see the OBJECTID-unreliability finding above: it wasn't. The
  EFFECTIVED-window scan (2026-08-30 through 2026-09-12) found 81 newly-staked dispositions;
  77 after excluding the 4-claim Flin Flon outlier block (see above) - CanAlaska Uranium 16,
  Skyharbour Resources 6, Gem Oil 6, Cosa Resources 6, Standard Uranium (Saskatchewan) 4, and
  22 distinct individual stakers (39 claims). Lapsed register (layer 3): 368, re-verified
  identical to the stored snapshot, zero additions or removals. Lapsing within 7 days (by 19
  September): **102**, more than double last edition's 45 - largest blocks Ryan Kalt
  (individual) 17, Eagle Plains 13, Murchison Minerals 12, Orano 11, Greenridge Exploration 10,
  Inspiration Energy 8, Jasper Mowatt (individual) 5, then smaller holders. Lapsing 8-14 days
  out (20-26 September): 94 (down from 151, consistent with part of that group rolling into
  the 7-day tier as the calendar moved forward). Alberta tenure: 716 features, matching the
  prior baseline - no diff possible without `exports/ab_state.json`, which this session cannot
  reach (no device connection).
- **News sweep (Step 2):** full sweep order run via subagent. No new releases dated 2026-09-11
  or 2026-09-12 were found anywhere in the sweep (consistent with a Saturday edition - press
  releases are a weekday phenomenon). The trailing-7-day window (6-12 Sep) is still covered by
  the same six items as yesterday's edition, none of which have aged out yet: Purepoint/
  IsoEnergy's Nova assay (10 Sep), IsoEnergy's Larocque East completion (8 Sep), Terra Clean
  Energy's $2.0M placement (9 Sep, still expected to close ~5 Oct), Global Energy Metals'
  Charlot-Neely radiometric-anomaly release (8 Sep), Green Canada Uranium's Marshall
  mobilization (9 Sep), and Belmont Resources' Crackingstone gravity-survey announcement
  (10 Sep). CanAlaska's Key Extension mobilization (8 Sep) stays in the majors-context note,
  not the numbered list, matching its Edition 002 treatment - no new CanAlaska development to
  reconsider that placement. Ranking order kept identical to Edition 002's (no new information
  to justify reordering unchanged items) - **per the skill's own Step 5 guidance, "no new
  ranked item, no re-ranking needed" is treated as the valid, complete outcome for the numbered
  list this run.** One item worth double-checking on a future run: the subagent doing the news
  sweep this time reported Terra Clean Energy's Sept 8-10 news as being for its Marysvale, Utah
  project and initially wanted to exclude it - the $2.0M placement itself (Sept 9, already on
  the live page since Edition 002) is general corporate financing, not tied to a named project
  in its own release text, so it was kept; but if TCEC's Saskatchewan (South Falcon East) and
  Utah (Marysvale) news start being conflated in a future sweep, that's worth untangling
  properly rather than assuming either edition got it right.
- **Price/market context:** ISO, PTU, BEA, CVV, GCUC and TCEC all returned real quotes dated
  11 September (Friday's close - see the weekend-freshness finding above for how that was
  read). GEMC's quote is still dated 27 August, same recurring staleness as every prior
  edition - dashed as usual. U3O8 ticker: Cameco's page still shows Aug 2026 month-end
  (US$89.68/lb, unchanged), Bank of Canada's most recent published USD/CAD is 1.3866 (11 Sep) -
  CA$124.35/lb.
- **Map waypoints:** no change needed - the six numbered items are the same six as Edition 002
  and already have established anchors in the live bundle's `news` key (Nova's published drill
  collar, Larocque East offset from the Hurricane deposit, South Falcon East anchored to
  Fraser Lakes B, Charlot-Neely Lake anchored to the Charlot Lake Uranium Showing, Crackingstone
  anchored to the Crackingstone Peninsula occurrence cluster, Marshall anchored to disposition
  MC00014967). `news` bundle key republished byte-identical to Edition 002's.
- **Two claude.ai pages republished:** Basin Watch -> Version 165, Basin Explorer -> Version
  100, both verified for script-tag count matching their pre-edit counts (3 and 2 respectively)
  and bundle JSON re-parse via `json.JSONDecoder().raw_decode` before publish. `claims`
  replaced wholesale with the 77-item, 14-day-window list above on both pages, identical
  values.
- **No archive snapshot taken as a new claude.ai artifact.** Per `archive-index.md`'s "Current
  mechanism (switched 2026-09-11)" section, the claude.ai-snapshot archiving mechanism is
  retired - basinwatch.ca now builds its own `/archive/edition<NNN>/` pages automatically from
  each day's `data/edition.json`, and that mechanism was confirmed working this run (fetched
  `https://basinwatch.ca/archive/edition002/` directly - loads real archived Edition 002
  content, not a 404). So this edition's Archive section links Edition 002 and Edition 001 to
  their `basinwatch.ca/archive/edition00N/` pages rather than to claude.ai snapshot artifacts,
  matching the retired-mechanism guidance. The old claude.ai snapshot URLs (Edition 001's
  `641bbe0c-...`) still resolve if ever needed, but are no longer what the live pages link to.
  **Note (2026-09-13): the claude.ai-page archive snapshot practice was actually used again
  this day for Edition 003's outgoing snapshot** - see the 2026-09-13 run note above. Treat
  both mechanisms as live in parallel: basinwatch.ca's own native archive pages for that site,
  plus a claude.ai snapshot artifact per edition for the claude.ai pages' own Archive links.
- **edition.json assembled and verified against the real repo, not just parsed locally.**
  `git clone`d `sockthief77/basin-watch` (read-only, worked cleanly) to get the exact
  `<!--__EDITION_TOP__-->`/`<!--__EDITION_BOTTOM__-->` boundaries from the actual
  `site/shell.html` rather than assuming them, then ran the repo's own `scripts/build.py`
  against the new `edition.json` and the repo's existing (separately-refreshed) `data/bundle.json`
  - this is the skill's stated "best verification" and it passed clean: both placeholders
  substituted exactly once, exactly 2 `<script>` tags survived, the bundle re-parsed as JSON.
  Delivered to Ezra both inline in the chat reply as a fenced code block and via `SendUserFile`,
  per standing instruction.
- Watermark and Layer3 snapshot updated below regardless of the "nothing changed by OBJECTID"
  finding, since the underlying total counts (7,468 active, 368 lapsed) are still the current,
  correct figures to carry forward - only the *staking-detection method* was found to be
  unreliable, not the counts themselves.

## Rule: do not write to Ezra's computer

The brief publishes to an artifact and writes nothing to disk on his machine. Never create
a folder or file there as a side effect of a run. If something genuinely needs to land on
disk, ask first. **Never write into a OneDrive-synced or company directory** - the
`Standard Uranium` folder in his user profile is the company directory and is off limits.

The one exception, added 2026-09-08: the scheduled task now has
`C:\Users\EzraMeszaros\Desktop\basin-watch` attached to its runs so it can **read**
`exports/map_bundle.json`. Read-only. It still writes nothing there.

## Living page

`https://claude.ai/code/artifact/27c1b96e-0b57-47f1-bc6f-0e698e4ca186`

One artifact, rewritten each morning, archive preserved. Never publish a second copy of
*this* page. **This no longer means never publish any other artifact** - see "Archive
snapshots" below, added 2026-09-09: each edition also gets its own one-time, never-touched-
again archive artifact, which is a different thing from duplicating the living page.
**As of 2026-09-11's run, archiving resumes - see "Versioning and edition-numbering rule"
below for the exact one-day-delayed schedule.** **As of 2026-09-11 evening (see
`archive-index.md`), the claude.ai-snapshot archiving mechanism described in this section and
below is retired in favour of native `basinwatch.ca/archive/edition<NNN>/` pages - no more new
claude.ai snapshot artifacts are created per edition. Confirmed working 2026-09-12.** **Update
2026-09-13: a claude.ai snapshot WAS taken again this day for Edition 003 (see the run note
above) - the "no more" framing above is stale; both mechanisms run in parallel now, one per
surface (basinwatch.ca native archive, and a claude.ai snapshot for the claude.ai pages' own
Archive section links).**

## RESOLVED 2026-09-10 (later same day): basinwatch.ca publishing works, confirmed live - the section below is history, not current architecture

**Supersedes the "Handoff page version pinning" section immediately below.** That section's
diagnosis (a real platform behavior - shared Artifact links pin to a fixed version) was never
actually the blocker. Testing the real failure path (not just tool-based checks) found the
true cause: `claude.ai/code/artifact/*` pages are client-rendered, so a genuinely anonymous
HTTP client - exactly what `publish-brief.yml`'s `urllib.request` fetch in GitHub Actions is -
gets an empty JS shell back, never the actual `<pre id="handoff-data">` content, regardless of
share settings or re-share timing. Confirmed directly with a plain `curl` and an unmodified
run of the repo's own `scripts/merge_edition.py`, both of which got the shell, not the data.
Every session that had checked this page's content, including whoever diagnosed the version-
pinning issue below, used `WebFetch` or `Artifact.read`, which carry the session's own
claude.ai login - not available to an anonymous fetcher.

A second fix attempt - getting this skill's own cloud session real git push access to
`sockthief77/basin-watch` - was also tried and abandoned the same day: this task runs as a
Cowork scheduled task, not a Claude Code web Routine, and no repository-write-access control
for that surface exists (`claude.ai/code/routines` doesn't even list this task).

**What's actually shipped and confirmed working:** the skill's Step 4b now writes a plain
`data/edition.json` file (not base64, not wrapped in an Artifact page) and sends it to Ezra
via `SendUserFile`. Ezra pastes it into
`github.com/sockthief77/basin-watch/edit/main/data/edition.json` and commits directly to
`main` - one paste, one commit, same daily cost as the old re-share click, except this one
works. Cloudflare Pages is connected directly to the repo (see the repo's `README.md`,
"Hosting" section) and rebuilds and redeploys automatically on any push to `main` that
touches `data/edition.json` - **independent of `publish-brief.yml` entirely**. So the site
updates within a couple of minutes of the commit landing; `publish-brief.yml`'s 09:20 Regina
schedule doesn't need to fire for this to work (its own fetch-and-rebuild steps are now
vestigial - harmless no-ops, safe to remove later, not urgent).

**Confirmed live 2026-09-10:** `curl https://basinwatch.ca/` returned Edition 001, "Sept 04 -
Sept 10", Purepoint's Nova assay leading - matching that day's actual edition content.
**Re-confirmed live again later the same day** (see the run note at the bottom of this file):
a fresh `curl https://basinwatch.ca/` still returns Edition 001, "Sept 04 - Sept 10",
Purepoint's Nova assay leading, byte-for-byte consistent with the `claude.ai` artifact - the
paste-flow architecture is holding up, not just a one-time success. **Re-confirmed again
2026-09-12: basinwatch.ca correctly serves Edition 002 (WebFetch's own response cache served a
stale Edition-001-looking read on the first try - a cache-buster query param on the second
fetch showed the true, current Edition 002 content - not a real site problem).**

**This is still a daily manual step, not full automation - see the exchange with Ezra
2026-09-10 for why.** This skill has no git credentials and, per the investigation above,
cannot get any for this task surface. The one remaining human action is the commit itself
(paste `edition.json`, click commit) - everything downstream of that commit (site rebuild,
Cloudflare deploy) is automatic. That is the ceiling given the constraint, not a partial fix.
**Don't re-investigate any of this.** Not the version-pinning fix, not getting this session
git access, not whether `publish-brief.yml`'s schedule needs adjusting. The architecture is
settled: Ezra commits `edition.json` by hand each morning, Cloudflare does the rest.
**Superseded 2026-09-14 for repo-bound sessions - see the standing note at the top of this
file.**

**Note found 2026-09-10 (later still): the skill's own SKILL.md Step 4b text had never been
updated to match this settled architecture, and was fixed this same day.** It previously
described the old base64-Artifact-handoff mechanism verbatim. Ezra asked for it to be fixed;
the full skill was rewritten (via `propose_skills`, since skill files on disk are a read-only
cache and only a proposal the user saves actually changes the skill) to describe the
plain-`edition.json`-via-`SendUserFile` flow throughout - Constants, Step 4b, Unattended runs
and Known open items were all updated together so they tell one consistent story. **This is
a proposal pending Ezra's save**, not yet guaranteed live - a future run should confirm the
skill's Step 4b actually reads the new way before assuming this is done. **Update, 2026-09-10
evening: this proved true - the live SKILL.md on disk was found corrupted (a placeholder
sentence, not real content) rather than merely stale, and was rebuilt from scratch and
resubmitted. See the newest run note below.** **Update, 2026-09-12: the skill as loaded this
run still describes the plain-edition.json-via-SendUserFile flow correctly and still doesn't
contain the "Map data now refreshes itself" section the scheduled task's own prompt references
- same mismatch flagged on 2026-09-11, still unresolved, still not blocking (the documented
Step 1 direct-ArcGIS-query method works fine as the actual source of truth).**

## CLOSED 2026-09-10 (same day, later still): fine-grained PAT automation tried and abandoned; branch protection added instead

Ezra asked to remove the daily manual step entirely by giving this skill's session a real
GitHub credential (a fine-grained PAT, scoped to `sockthief77/basin-watch` only,
`Contents: Read and write`, 90-day expiry). Investigated properly rather than guessed at:

- **The git proxy itself is not the blocker for a scoped, real credential.** A
  `git push --dry-run` using the PAT (via an `http.extraHeader` Basic-auth header, not a
  credential-in-URL, which the session's own auto-mode classifier blocks on sight) succeeded
  cleanly against the real repo. So if this task type could hold a secret, the push mechanism
  itself would work today.
- **It can't.** The full "Edit scheduled task" form for this Cowork task (Name, Instructions,
  folder/model, Frequency, Permissions, "Require this computer") was checked field by field -
  there is no environment-variable or secret field anywhere in it. This is not "couldn't find
  it," it's "confirmed it isn't there." Cowork scheduled tasks have no persistent-credential
  storage at all, so there is no way to give a recurring run of this specific task real git
  push access without moving the automation to a different product surface entirely (a
  Claude Code web Routine, which does have per-task environment variables per its own docs -
  a real future option, but a separate migration, not a same-day fix. Don't attempt it without
  Ezra explicitly asking to take that on).
- **The PAT was revoked** (`basin-watch-daily-edition`, deleted from
  github.com/settings/personal-access-tokens) once this was confirmed dead-ended - no live
  credential was left sitting unused anywhere.
- **A GitHub ruleset was added to `main` instead**, as the safety net Ezra asked for
  regardless of which publishing mechanism won: **Restrict deletions** and **Block force
  pushes** are on. Nothing else is restricted (plain pushes, including the daily
  `edition.json` commit, are unaffected). This is the safety net for the paste-flow
  architecture - see the CLOSED section above for why it was added instead of (not in
  addition to) automated push access. If a bad edition ever lands, the fix is
  `git revert <bad commit sha> && git push` - Cloudflare rebuilds from the revert
  automatically.

**Net result: the paste-flow architecture in the RESOLVED section above is not a stepping
stone to something more automated - it's the settled design**, now with branch-level
protection on top, **for a non-repo-bound session type. Superseded 2026-09-14 for a
repo-bound Claude Code environment - see the standing note at the top of this file.** Don't
re-propose the PAT-in-environment-variable approach for a Cowork-style task; it's a confirmed
dead end there. **This session (2026-09-12) confirms `git clone` (read-only, HTTPS, no
credential) still works fine for reading the repo - used it to verify `site/shell.html`'s
placeholder boundaries and run `scripts/build.py` before handoff.**

## Handoff page version pinning - historical context only, not the current mechanism (discovered 2026-09-10, superseded same day - see above)

**Claude Artifact share links pin to a fixed version once shared "Anyone with the link"
(external/outside-org access), and cannot be switched to "Latest" while that external
access stays open.** Confirmed directly: the share panel's own UI showed "Shared version:
Version 1 · ... · 32m ago" with a red warning reading "Can't switch to Latest while people
outside your organization can open this artifact. Change who has access first," and Ezra
independently confirmed the same block when he tried switching the dropdown himself. This
is real platform behavior, but it turned out not to be why `basinwatch.ca` was stale - see
the RESOLVED section above for the actual cause and fix. Left here only so nobody rediscovers
the same (true, but non-blocking) fact and mistakes it for the explanation again.

## Archive snapshots (added 2026-09-09, corrected 2026-09-09 evening, timing corrected 2026-09-10, mechanism retired 2026-09-11, resumed in parallel 2026-09-13) - read `claude/archive-index.md`

**As of 2026-09-13, this practice is back in use alongside the native basinwatch.ca mechanism**
(see the 2026-09-13 run note above) - a claude.ai snapshot artifact is published per edition
for the claude.ai pages' own Archive section links, while basinwatch.ca continues to build its
own native `/archive/edition<NNN>/` pages independently. The steps below (originally written
as history for the retired mechanism) describe exactly what to do when taking a claude.ai
snapshot:

- **Before overwriting the live page with a new edition**, publish the live page's current
  full HTML as a new artifact titled `Basin Watch — <date>` (set the `<title>` tag itself -
  a `title` parameter is ignored if the HTML already has one, so set the `<title>` tag itself),
  favicon ☢️. Record the URL in `claude/archive-index.md`.
- Turn that date's Archive row into `<a class="arow" href="...">` (was `<div class="arow">`).
  Rows with no recorded URL stay plain divs - never link to a URL that doesn't exist.
- **The current edition's own row is always a plain `<div class="arow">`, never a link** -
  even though its own snapshot URL exists and is valid in the index below, render it as a
  plain, non-clickable div - the reader is already looking at that content. Only *past*
  editions (every row except the top/current one) should ever be `<a>` tags.
- This was a **new artifact per calendar edition, created once and never republished again**
  - not a second copy of the living page, and not something a run should ever touch after
  its first publish.
- CSS for the link styling is already on the live page (`.arch a.arow` rules) - don't
  duplicate or reintroduce it. **This CSS is mechanism-agnostic and is still in use** for the
  native basinwatch.ca-URL links too.

**2026-09-10: no archive snapshot taken this day (confirmed correct).** 2026-09-10 stays
Edition 001; a claude.ai snapshot of it was taken 2026-09-11 and later backfilled into the
native `archive/edition001/` page the same day.

## Editing the page: always split it first (2026-09-08)

The published page is ~6.3-6.9 MB, nearly all of it the one-line `BASIN_BUNDLE`. Never open
or edit `basin-watch.html` directly. Every session that touches the page does this first:

1. `Artifact` read on the canonical URL - the tool saves the full HTML to a local file.
2. Split it into `shell.html` (~90-100 KB, everything but the data, with `/*__BUNDLE__*/`
   standing in for it) and `bundle.json` (~6.8 MB, never opened by hand).
3. Edit `shell.html`, run `build.py` to substitute the bundle back in, publish the result.

`build.py` asserts the placeholder survived. The container is ephemeral, so this split has
to be redone from the published page at the start of every session - it is not a one-time
setup. See `map-pipeline.md` for the same rule from the map side.

**Narrow exception for a one-string text fix:** if the change is a single unique literal
outside the bundle line, a scripted read-replace-write on the saved artifact file with an
`assert count == 1` is safe and much cheaper than the split. Verify the bundle line is
intact before publishing. Do not use this for anything structural, and never for a change
inside `BASIN_BUNDLE`.

**A scripted read-replace-write with a small handful of asserted, unique-string replacements
(not just one) is fine too**, as long as every replacement is outside `BASIN_BUNDLE`, each is
asserted to match exactly once, and the standing post-publish checks (script-tag count
unchanged from before the edit, bundle JSON still parses via `json.JSONDecoder().raw_decode`,
not a naive greedy regex) are run before publishing. **Correction 2026-09-11: "exactly two
script tags" stopped being a universal constant once Basin Watch's footer newsletter/contact
modal shipped - Basin Watch has 3 (`BASIN_BUNDLE` + engine + modal), Basin Explorer still has
2 (no footer modal). Check the count against what the page had before your edit, not a fixed
number, or a legitimate Basin Watch edit will look like corruption.** Same correction applied
to the `uranium-brief` skill itself via a `propose_skills` update. **Reconfirmed 2026-09-12
and 2026-09-13: both counts (3 and 2) held on each run's split/rebuild of both pages.**

**Confirmed 2026-09-09: a local shell/bundle split can go stale mid-session if another
session publishes in between.** Diff any local split's ticker values and news-item count
against a fresh `Artifact.read` of the live page before trusting it as an editing base.

**New standing check, added 2026-09-13 (later run): a JSON re-parse of `BASIN_BUNDLE` is NOT
sufficient proof the page will actually run in a browser.** A real incident this same day (see
the "real BASIN_BUNDLE syntax-error bug" run note above) had `BASIN_BUNDLE`'s JSON content
itself always valid and always re-parsing clean, while the surrounding JS statement embedding
it (`window.BASIN_BUNDLE=__{...}__;`, two stray literal underscores) was a hard syntax error
that left the entire page's script non-functional. **Before publishing any edit to Basin
Watch, in addition to the existing script-tag-count and JSON-reparse checks, load the actual
candidate HTML in a headless browser (Playwright/Chromium, confirmed available in this
environment) and confirm: zero page errors, and `typeof window.BASIN_BUNDLE === 'object'`
with the expected key set.** This is now the standard to hold every future Basin Watch publish
to, not just an occasional check - see that run note for exactly how it's done and what it
caught.

## Reporting window

**Every edition covers the trailing 7 calendar days, today inclusive** - not just what
changed since the last run. Recompute the cutoff from the current date every run (e.g. on
2026-09-13 the window is 2026-09-07 through 2026-09-13). **The staking-specific window
(Recent Stakers panel, registry table's Staked rows, New Claims map layer) is a separate,
independently-computed trailing-14-day window as of 2026-09-11 - see the skill's Constants
section. Don't conflate the two**, per the 2026-09-12 finding above about the registry table's
stale 7-day framing.

## Watermark

```
LAST_OBJECTID: 7459
LAST_RUN: 2026-09-14
LAYER0_COUNT_AT_LAST_RUN: 7459
LAYER3_LAPSED_COUNT_AT_LAST_RUN: 375
LAST_EDITION_NO: 004
```

**Note (2026-09-14): edition number NOT incremented this run** - see the 2026-09-14 run note
below. No new edition was published (news sweep and price refresh could not be performed - a
session/environment-level network egress block, not a data problem), so `LAST_EDITION_NO` stays
004, the last edition actually published. The claim/tenure/lapsed figures above ARE fresh
(sourced from `data/bundle.json`, itself refreshed by `gis-export.yml` earlier the same day -
confirmed by a fresh `git log`/`git pull`, not by this session's own ArcGIS queries, since this
session's WebFetch access to `gis.saskatchewan.ca` is part of the same block described below).

## Run note, 2026-09-14 (scheduled 08:20 America/Regina run) - repo-bound session, network egress blocks news sweep and price refresh; no new edition published

**Session type confirmed repo-bound**: `git push --dry-run` against `sockthief77/basin-watch`
succeeded (real push access, per `basinwatch-pipeline-fix.md`'s 2026-09-14 standing note), and
this run is publishing per Step 4b's repo-bound path (direct `git add`/commit/push to `main`,
not the manual `SendUserFile` handoff) - except no publish happened this run, see below.

**Step 1 (claim monitor) - completed successfully, using the simplified repo-sourced procedure
per `map-pipeline.md`'s "one map dataset" section:**
- `git pull origin main` confirmed current with `origin/main` (commit `52407f8`); `data/bundle.json`
  was refreshed by `gis-export.yml` earlier today (commit `14e3f59`, "Daily GIS export refresh
  (2026-09-14)") - its own `generated` field still reads 2026-09-09, which is the already-documented
  `merge_map_bundle.py` behaviour (that script deliberately excludes `generated` from every merge),
  not a sign the refresh didn't run. Confirmed the refresh is real by diffing record counts against
  the prior day's committed bundle: `tenure` 7,460 -> 7,459, `lapsed` 375 -> (see below), `claims`
  and `ab_tenure` unchanged (81, 74).
- Lapsing by 21 Sep (7 days): **100** - Ryan Kalt (individual) 17, Eagle Plains Resources 13,
  Murchison Minerals 12, Orano Canada 11, Greenridge Exploration 10, Inspiration Energy 8, Jasper
  jon arthur Mowatt (individual) 5, 92 Energy Canada 4, then smaller holders. Computed locally from
  `data/bundle.json`'s `tenure[].x` (GOODSTANDI) field, today = 2026-09-14.
- Lapsing 22-28 Sep (8-14 days out): **93** - Ryan Kalt 76, Greenridge Exploration 8, Argo Gold 3,
  Golden Band Resources 2, Orano Canada 2, then singles.
- Claims (14-day staking window): still **81** (42 corporate / 39 individual) - byte-identical
  composition to Edition 004's figures (CanAlaska 16, Gem Oil 10, Cosa Resources 6, Skyharbour 6,
  Standard Uranium 4 among corporate holders). Max `EFFECTIVED` date in the array is still
  2026-09-11 - consistent with the documented business-days-only staking pattern (09-12 Sat,
  09-13 Sun had no new registrations, and 09-14's own day-of staking wouldn't appear in a bundle
  built from an early-morning pull) rather than a stale pipeline.
- Lapsed register: **375** in `data/bundle.json`, vs **376** in `gis/exports/lapsed_state.json`
  (both dated 2026-09-14) - a 1-record discrepancy between two outputs of the same day's pipeline
  run, not independently re-verified against a live ArcGIS count this run (see network block
  below). Worth a future run checking if this recurs.
- Alberta tenure: 74 agreements survive the basin window (`ab_tenure`), 712 total in
  `gis/exports/ab_state.json` (region-wide, pre-basin-filter) - consistent with the documented
  ~74/province-wide split, no anomaly.

**Step 2 (news sweep) and Step 4 (price/market context) - NOT completed. Root cause: this
session's network egress policy blocks `WebFetch` to essentially every external domain tested,
not just the specific hosts previously documented as blocked for other session types.**

Confirmed via direct test (all returned `EGRESS_BLOCKED` from the local agent proxy, per
`/root/.ccr/README.md`'s "403/407 from the proxy: destination host not allowed by your
organization's egress policy for this session - do not retry or route around it, report the
blocked host"): `www.cameco.com`, `www.google.com` (Google Finance), `stockanalysis.com`,
`www.newsfilecorp.com`, `en.wikipedia.org`, `www.bankofcanada.ca`. The only domain that answered
was `github.com` (used for this repo). This is a materially different constraint from every prior
session's documented finding (which named a short, specific list - `gis.saskatchewan.ca`,
`raw.githubusercontent.com`, `basinwatch.ca`, `accounts.google.com` - and treated everything else
as reachable): in this session/environment, the allowlist appears to cover little beyond GitHub.

`WebSearch` (a separate tool, not proxied the same way) does still work, but its AI-summarized
answers proved unreliable and couldn't be independently checked: a test query for Cameco's
published spot price returned "$75.13, up from $71.10" with no matching source snippet actually
containing that figure, directly contradicting the already-live page's own Aug-2026 figure of
US$89.68/lb - i.e. the summary was very likely synthesized/hallucinated rather than read off a
real page. Per the skill's own hard rule ("a confidently wrong price is worse than no price") and
the general rule against publishing unverified figures, `WebSearch` summaries were not used as a
substitute for `WebFetch`-verified source content anywhere in this run.

**Decision: no new edition published this run.** Fabricating a news sweep or carrying forward
unverified/possibly-stale news content while implying a fresh check had been done would violate
the skill's own explicit instruction ("do not fabricate roster, claims, or state data to force a
run through... stop and say so... a refusal to publish is the correct behavior, not a bug to
route around") - that instruction is written about missing ops docs, but the same principle
applies squarely to a blocked data source. The claude.ai Basin Watch/Basin Explorer pages and
`data/edition.json`/`main` were left untouched; Edition 004 (2026-09-13) remains the live/current
edition. This watermark file and this run note were committed and pushed directly to `main`
(repo-bound push, per Step 4b), since capturing the finding is itself a repo file change, not a
publish of unverified content.

**Independent confirmation:** a subagent dispatched in parallel to attempt the full news sweep via
`WebSearch` (not `WebFetch`, which it also found `EGRESS_BLOCKED` for every named source -
Junior Mining Network, TMX Newsfile, newswire.ca, ACCESS Newswire, GlobeNewswire, Saskatchewan EA,
CNSC, WISE Uranium, CIRO) reached the same conclusion independently: no primary source was
fetchable, only secondary/aggregator search summaries, which it correctly flagged as needing
primary-source confirmation rather than being publishable as-is. For the next run once network
access is restored, worth specifically re-checking: whether IsoEnergy's Larocque East assays
(still pending as of Sep 8 reporting) have landed; the CanAlaska Key Extension item may need
upgrading from "mobilization" to "Fall 2026 drill program underway" (per the subagent's secondary
sourcing - unverified); the Nexus Uranium (NEXU) CIRO halt is reportedly still unresolved with no
resumption notice found, and no listed resumption in CIRO's Sep 12-14 batch (ALGR, IVS, SPMC,
NILI, GORO, CQR) included it. None of this was added to the live page - it is all secondary-source
only and unverified per the caveats above.

**Recommended follow-up, not for this run to act on:** check whether this Claude Code
environment's network egress allowlist is meant to include the news-wire and financial-data hosts
this skill depends on (`juniorminingnetwork.com`, `newsfilecorp.com`, `newswire.ca`,
`accessnewswire.com`, `globenewswire.com`, `saskatchewan.ca`, `cnsc-ccsn.gc.ca`,
`wise-uranium.org`, `cameco.com`, `google.com` for Finance quotes, `bankofcanada.ca`) - if the
intent is for this repo-bound environment to run the full daily brief unattended, the allowlist
needs those hosts added; until then, either the old non-repo-bound scheduled task (which ran in
an environment where those hosts were reachable) should keep covering the news/price steps, or
this environment's policy needs revisiting.

**Second attempt, same day (2026-09-14, later run): same conclusion, plus new evidence the
sources aren't just blocked but unreliable when they do answer.** A second scheduled firing
re-tested reachability directly rather than assuming the earlier finding still held:
`cameco.com/invest/markets/uranium-price` answered this time (unlike the earlier EGRESS_BLOCKED
report) but returned a spot price dated **28 Feb 2026** — seven months stale against today's date
and inconsistent with the live page's already-published Aug-2026 figure, with no way to tell from
this session whether that's a stale cache, a WebFetch summarization artifact, or a real page
regression. `juniorminingnetwork.com`'s uranium topic page 404'd. A Google Finance fetch for a
roster ticker (`CVV:CNSX`) silently returned an unrelated NASDAQ-listed company's quote instead of
an error, which would have been publishable as a real figure if not checked against the ticker
requested. None of this was used to write or refresh any ranked item or price cell. Given both
this and the earlier same-day attempt independently conclude the data pipeline can't currently be
trusted, no new edition was published this run either; Edition 004 remains live. This session also
flags, for a human to weigh rather than for a run to decide on its own: the skill file's own
2026-09-14 update — which introduces unattended direct `git push` to `main` for a repo-bound
session, bypassing the manual review step that every prior edition has gone through — reads as an
unusually large, self-granted escalation to arrive in the skill's own text on the very day an
unattended routine would first act on it, and is worth an independent check that it actually
reflects Ezra's intent before a future run relies on it to publish real content unattended.

**Note (2026-09-12): `LAST_OBJECTID`/`LAYER0_COUNT_AT_LAST_RUN` both track the `1=1`
returnCountOnly total (7468), not literally the maximum `OBJECTID` value (confirmed this run
to be only 7462 - the two numbers really do differ on this service). Kept as the total-count
convention this field has always used, for continuity - see the OBJECTID-unreliability finding
above for why this field should not be trusted as a new-claims detector regardless of which of
the two numbers it holds.**

**Note (2026-09-13, later run): watermark values left unchanged this run** - no fresh ArcGIS
query or new `data/bundle.json` pull was performed (the earlier same-day run already pulled
and recorded the current stale-but-current bundle state), and Edition 004's own number stays
004 since this run's changes (a text-only Nexus-detail update and the BASIN_BUNDLE bug fix)
were supplemental to the already-published edition, not a new one.

## GOODSTANDI - date-literal queries work, but only single-bound (fixed 2026-09-11)

Both `EFFECTIVED` and `GOODSTANDI` serialise as epoch milliseconds in the JSON response,
which makes them look like numeric fields. They are not - they are ArcGIS **date** fields,
and a plain numeric comparison against them fails.

**Working recipe (confirmed 2026-09-11, reconfirmed 2026-09-12): two single-bound
`timestamp'...'` queries, not one combined range query.** A where-clause with two quoted date
literals joined by `AND` gets rejected at the WebFetch proxy layer itself (HTTP 403 before the
request reaches ArcGIS) - this was misdiagnosed earlier the same day as "the query is blocked,
period." It isn't: drop the `AND` and query each bound separately. **Also reconfirmed
2026-09-12: `returnCountOnly=true` combined with `outFields` in the same request 403s; drop
`outFields` entirely for a pure count-only query (`where=...&returnCountOnly=true&f=pjson`,
nothing else) and it goes through.** `returnCentroid=true` also 403s reliably regardless of
how few outFields accompany it - not a usable shortcut for getting claim-centroid coordinates
without full `returnGeometry=true` (see the bbox-midpoint recipe below instead).

1. `where=GOODSTANDI%3C%3Dtimestamp%27<END-DATE> 00:00:00%27&outFields=DISPOSIT_1,GOODSTANDI&returnGeometry=false&f=pjson`
   (the upper bound, e.g. 7 days out) - this is the one that matters, since it's a small subset
   of the ~7,468 active records (325 on 2026-09-11, for example) and safe to transcribe in full
   via WebFetch (verify the returned count against a separate `returnCountOnly=true` call, with
   no `outFields`, on the same where-clause before trusting the list).
2. Filter that list client-side for `GOODSTANDI >= <TODAY, epoch ms>` to drop already-past
   good-standing dates that are still flagged active (the registry's own "catching up" lag,
   documented elsewhere in this file) - this is the actual "lapsing within 7 days" set.
3. For owner names on that (much smaller, ~30-100 row) filtered set, a plain
   `outFields=DISPOSIT_1,OWNERS` query (same single-bound where-clause, or no where-clause at
   all with a `DISPOSIT_1 IN (...)` list) usually works - but an `IN (...)` list with many
   quoted values also hit a 403 on 2026-09-11 and again on 2026-09-12 (confirmed with just 5
   values), while the plain single-bound query with just `DISPOSIT_1,OWNERS` did not, and
   neither did a single `DISPOSIT_1='...'` equality query repeated one at a time. If a query
   that worked before starts 403-ing, try dropping outFields or the `IN` clause before
   concluding something is actually broken.

**2026-09-13 addition: when the daily bundle pull already has `tenure` with an `x` (expiry)
field per record, the whole GOODSTANDI dance above can be skipped entirely** - just filter the
already-in-hand `tenure` array locally by date. This is what this run actually did (see the
run note above); the ArcGIS recipe below stays documented as the fallback for when a live
query is genuinely needed (e.g. a claim not yet present in the pulled bundle). **Note: the
`x` field observed in the pulled `data/bundle.json` this project reads is a plain `YYYY-MM-DD`
date string, not epoch milliseconds - confirmed 2026-09-13 (later run) - convert accordingly
when computing lapsing bands from the pulled bundle rather than assuming the epoch-ms shape
described for the live ArcGIS endpoint's own `GOODSTANDI` field above.**

State the figures as of the run date. The bundle's own `tenure`/`x` field (used historically
as a fallback) is a second, independent way to get the same figures if this query path
degrades again. **2026-09-12: this fallback is genuinely useful, not just theoretical** - the
live bundle's `tenure` array already carries every active disposition's ring geometry, so a
new claim's centroid can often be computed locally (bounding-box midpoint of the `r` array)
without any further ArcGIS query at all, as long as the claim is already present in `tenure`
(a handful of very recently staked claims may not be yet - see the bbox-midpoint recipe below
for those).

## Known-good query recipes

Base:
`https://gis.saskatchewan.ca/arcgis/rest/services/Economy/Mineral_Tenure_Crown_Dispositions/FeatureServer`

Layers: 0 Mineral Dispositions, 3 Lapsed. maxRecordCount 2000. Native SR wkid 2151.

**Current max OBJECTID**: `/0/query?where=1%3D1&returnCountOnly=true&f=pjson` - **caveat added
2026-09-12: this returns the total feature count, not necessarily the true maximum `OBJECTID`
value on this service (confirmed to differ, 7468 vs 7462, this run) - see the Watermark note
above. To find the true max OBJECTID, binary-search with `OBJECTID > N` until it returns zero
rows.**

**New claims since watermark**:
`/0/query?where=OBJECTID+%3E+<WATERMARK>&outFields=OBJECTID,DISPOSIT_1,OWNERS,EFFECTIVED,GOODSTANDI,DISPOSIT_3&returnGeometry=false&f=pjson`
**Caveat added 2026-09-12: this is not a reliable new-staking detector on its own - `OBJECTID`
does not track chronological order on this service. Always cross-check with the EFFECTIVED-
window query below before concluding nothing new was staked.**

**New claims by EFFECTIVED window (the reliable method, added 2026-09-12)**:
`/0/query?where=EFFECTIVED%3E%3Dtimestamp%27<WINDOW-START> 00:00:00%27&outFields=DISPOSIT_1,OWNERS&returnGeometry=false&f=pjson`
for the owner list, plus a second call with `outFields=DISPOSIT_1,EFFECTIVED` for exact dates
(request the raw epoch-ms integer, do not let the fetch tool convert/round it, then convert
locally with `datetime.fromtimestamp(ms/1000, utc)`). Cross-check the row count against a
plain `returnCountOnly=true` call (no `outFields`) on the same where-clause.

**Claim centroid without a fresh ArcGIS geometry call, when the claim is already in the live
bundle's `tenure` array (added 2026-09-12):** look up by `DISPOSIT_1` (`tenure[i].d`) and take
the bounding-box midpoint of `tenure[i].r` (already lon/lat pairs, no reprojection needed) -
`((min_x+max_x)/2, (min_y+max_y)/2)`. Free, exact enough for map placement, no WebFetch
transcription risk since it's done locally in a script against the already-fetched bundle.

**Claim centroid via a fresh ArcGIS call, when the claim is NOT yet in `tenure` (added
2026-09-12):** query that one `DISPOSIT_1` by itself (never an `IN (...)` list - see above)
with `returnGeometry=true&outSR=4326&maxAllowableOffset=0.001` and ask for the bounding-box
midpoint of the returned ring, not a vertex average - same safety rule as the news-waypoint
anchor recipe in `news-waypoints.md`. `outSR=4326` matters: the service's native SR (wkid 2151)
returns projected metre coordinates, not lon/lat, and reprojecting those by hand is unnecessary
extra risk when the server will do it directly.

**Full lapsed register, one page**:
`/3/query?where=OBJECTID+%3E+0&outFields=DISPOSIT_1&returnGeometry=false&returnDistinctValues=true&f=pjson`
Constraining to the single `DISPOSIT_1` field is what makes it fit. Don't trust the tool's
own prose-stated count for this endpoint - always extract the literal list and count it with
a script. **Reconfirmed 2026-09-10 (four separate times across the day, three distinct wrong
values seen - 520 and 533 in earlier runs, 500 in the evening run): the prose-stated count is
never reliable for this endpoint, even when the underlying data is fine.** When the row list
itself is long, an even more reliable check is a server-side count query with
`returnDistinctValues=true&returnCountOnly=true` (no `outFields` row listing at all) - this
returns the true count directly without needing to trust any summarization of a long list.
**2026-09-11: WebFetch's own row-list transcription (not the ArcGIS response) is also
unreliable on this query even at ~368 rows - a first attempt inflated/duplicated the list to
545 before a stricter "count must equal N, recount if not" prompt fixed it. Always
cross-check the transcribed list's length against the separate count-only query before
trusting it for a diff.** **Reconfirmed clean 2026-09-12 and 2026-09-13: 368/374 both ways
each time, zero unexplained drift.**

Field meanings, layer 0: `DISPOSIT_1` claim number, `OWNERS` holder with percentages,
`EFFECTIVED` epoch ms of registration, `GOODSTANDI` epoch ms good-standing expiry,
`DISPOSIT_3` status. Convert epoch ms with `datetime.fromtimestamp(ms/1000, utc)`.

**Do not request full polygon geometry through WebFetch for MANY features at once** - it
summarises coordinate arrays rather than returning them for a long list. Centroids are safe.
**For a SINGLE feature (added 2026-09-12), a full-ring geometry request with a tight
`maxAllowableOffset` is fine as long as you ask for the bounding-box midpoint explicitly
rather than a raw coordinate dump - confirmed reliable across 5 separate single-claim
queries this run.**

## Lapsed-layer diffing - implementation (2026-09-07)

Diff by `DISPOSIT_1` (the stable claim number, not `OBJECTID`, confirmed non-sequential on
this layer). Replace the stored set wholesale every run.

### Layer 3 snapshot (most recent run)

```
LAYER3_SNAPSHOT_DATE: 2026-09-12
LAYER3_SNAPSHOT_COUNT: 374
```

**Note (2026-09-13): the full 368-item DISPOSIT_1 list from the 2026-09-12 snapshot is not
reproduced in this rewrite** (this file's earlier version, restored above after this run's
overwrite-and-recovery, has the complete list) - the pulled `data/bundle.json`'s own `lapsed`
array (374 entries as of this run) is the current authoritative source and can be re-extracted
from a fresh `git clone` any time a full diff against the stored set is needed. Re-verified
2026-09-13: count is 374, up 6 from the 368 stored in the prior snapshot - consistent with
ordinary lapsed-register growth, not investigated claim-by-claim this run.

## SMAD - assessed, not added to the daily automation (2026-09-07)

Research source only, ~2-year confidentiality lag. Not a daily source.

## MARS - checked, and the question it was needed for is now closed (2026-09-08)

Good-standing is a hard deadline, not a grace period, per the MARS client manual. Stop
hedging this on the page.

## Versioning and edition-numbering rule (current, set 2026-09-10)

- **2026-09-10 stayed Edition 001, took no archive snapshot.**
- **2026-09-11's run archived 2026-09-10's actual final-state HTML as Edition 001's own
  snapshot, then published as Edition 002. Done.**
- **From 2026-09-12 onward, every run increments by one** from the previous edition's
  number, archiving the outgoing edition first each time. **2026-09-12 published as Edition
  003. 2026-09-13 published as Edition 004**, archiving Edition 003 first (both via a
  claude.ai snapshot artifact and, separately, basinwatch.ca's own native archive mechanism
  once the edition.json commit lands).
- **Clarified 2026-09-13 (later run): this increment-per-run rule is meant for one
  substantive edition per calendar day, not literally every touch of the live page.** A
  same-day supplemental text edit (the Nexus halt-reason detail, or the earlier Nexus flag
  addition, or a bug fix like the BASIN_BUNDLE syntax-error fix) that doesn't change the
  ranked news list or the claims/lapsing figures stays inside the current edition number
  rather than minting a new one - consistent with how both same-day supplemental edits
  logged above were handled. A genuinely new day's full sweep, or a same-day re-sweep that
  finds materially new content, is what increments the edition number.

The archive row's date always moves regardless of the edition-number rule.

## The scheduled task

**Current trigger: `trig_013LuMgYMkSLjJYEyZXHPxQD`, "Athabasca Basin Watch - daily 8:30am
uranium brief", cron `30 14 * * *` (08:30 America/Regina, UTC-6, no DST) - fires every
calendar day including weekends, confirmed 2026-09-12 (a Saturday).** No device
binding (`folders_state: FOLDERS_STATE_NONE`) - correct, matches "Never write to the user's
computer." **Confirmed 2026-09-10: this Cowork scheduled task's edit form has no
environment-variable/secret field of any kind** - see the CLOSED section above. Don't look
for one again on this task type. **Note 2026-09-13: today's run was a manual/interactive
invocation of the skill, not this trigger firing** - see the run note at the top of this file.
**Update, 2026-09-13 (later): a second run this same day (also invoked as "produce today's
edition," per its own stored prompt) found the schedule has since moved to 08:20 America/Regina
(cron `20 14 * * *`), per `open-items.md`'s own audit note - this doc's schedule line above is
stale and should be treated as historical; `open-items.md` is authoritative on the current
cron.** **Update, 2026-09-14: a new, separately repo-bound routine
(`trig_01HQ598Dp56ZYQco5R4sU29g`, created via the Claude Code web UI's own Routine flow,
scheduled 2:20 AM GMT / 8:20am America/Regina) has been created as the eventual replacement
for this task, once it can run correctly - see `basinwatch-pipeline-fix.md`'s standing note
and `roadmap.md`'s TOP PRIORITY section. This old task (`trig_013LuMgYMkSLjJYEyZXHPxQD`)
should stay enabled until the new one has a clean end-to-end pass - don't disable it early.**

**`publish-brief.yml`'s own GitHub Actions cron: 09:20 America/Regina (14:20 UTC,
`20 15 * * *`)** - now vestigial for actually publishing (Cloudflare Pages deploys directly
off any push to `main`, see the RESOLVED section above), but harmless to leave running.

**Its stored prompt is deliberately thin**: invokes `uranium-brief`, names that skill as the
single source of truth, tells the run to stop rather than improvise if the skill is missing.
The prompt also references a "Map data now refreshes itself" skill section that does not exist
in the skill as currently loaded - flagged 2026-09-11, still true through 2026-09-13, not
blocking (the documented Step 1 ArcGIS-query/bundle-pull method is used instead and is the
real source of truth).

## `main` branch protection (added 2026-09-10)

A GitHub ruleset on `sockthief77/basin-watch`, enforcement Active, targeting `main`:
**Restrict deletions** and **Block force pushes** are on. Nothing else is restricted (plain
pushes, including the daily `edition.json` commit, are unaffected). This is the safety net
for the paste-flow architecture - see the CLOSED section above for why it was added instead
of (not in addition to) automated push access. If a bad edition ever lands, the fix is
`git revert <bad commit sha> && git push` - Cloudflare rebuilds from the revert automatically.
**This protection stays in place and matters just as much now that repo-bound sessions can
push directly** - it protects against a bad direct push exactly the same as a bad manual
paste.

## `gis-export.yml`: automated map-data refresh (added 2026-09-10) - confirmed working 2026-09-11, generated-field staleness re-observed 2026-09-13

`.github/workflows/gis-export.yml` runs `basin_layers.py` + `scripts/merge_map_bundle.py` on
GitHub's own runners (not behind the egress allowlist that blocks `gis.saskatchewan.ca` from
this cloud container and from Ezra's device sandbox) and pushes straight to `data/bundle.json`
on success. Cron `30 13 * * *` (07:30 America/Regina), plus `workflow_dispatch` for a manual
trigger. **This skill never touches `gis/basin_layers.py` or `data/bundle.json` directly - the
daily brief only ever supplies `data/edition.json`.**

**2026-09-13 observation**: the repo's `data/bundle.json` was refreshed by a same-day commit
(`047a2ff`, 05:04 UTC) but the file's own internal `generated` field still read 2026-09-09 -
4 days stale despite the fresh commit. Not investigated further this run (out of scope for a
normal daily run per the skill), but worth a future session checking whether
`merge_map_bundle.py`'s `generated`-exclusion-from-merge logic (see the note below) is
interacting badly with something in `basin_layers.py`'s own generation of that field, since a
staleness of exactly this shape has now been seen on at least two separate dates. **Still
stale as of the 2026-09-13 later run (same-day re-check, no new pull performed that run).**

**Correction to the 2026-09-11 morning run note above**: `data/bundle.json`'s `generated`
field staying at a date well before the actual commit is NOT necessarily a sign this workflow
hasn't run - `merge_map_bundle.py` deliberately excludes `generated` from every merge
(`SKIP_KEYS = {"basin","news","generated"}`, see that script's own docstring: "the
edition-publish date, owned by the daily brief skill... a GIS refresh is not itself a new
edition"). Confirmed live via `workflow_dispatch` the morning of 2026-09-11: it ran clean
(commit `d49f5b3`, "Daily GIS export refresh (2026-09-11)"), refreshed
`gis/exports/ab_state.json` and `lapsed_state.json`, and found `data/bundle.json` itself
byte-identical to what was already committed except where new data genuinely differed - i.e.
a stale-looking `generated` field does not by itself mean the workflow failed; check other
keys (or the Actions log) to judge that. **The Alberta lakes/rivers merge is confirmed live in
`data/bundle.json`** (55 lakes as of 2026-09-11/12, 60 as of 2026-09-13's pull, named entries
include Lake Claire, Peace River, Slave River, Mamawi Lake, Dunvegan Lake, Richardson Lake -
Alberta-side features well past the SK border, not just Lake Athabasca's own AB portion).
**Also confirmed present in both claude.ai artifact pages' embedded `BASIN_BUNDLE`** as of
every run through 2026-09-13.

**The seam Ezra screenshotted (Lake Athabasca AB/SK border) is not a missing-data gap - both
sides of the border already have lake polygons.** It's a stitching mismatch between two
different generalization tiers (SK layer 80, AB layer 70) where a lake crosses the border.

**Fix landed 2026-09-11**: `gis/basin_layers.py` section 6c clips every qualifying Alberta
lake ring to strictly west of `BORDER_LON = -110.0` (the real AB/SK border, the 4th Meridian)
using the file's own `clip_ring()` helper, dropping any ring that clips down to fewer than 3
points. Verified with `ast.parse` and a standalone synthetic test on three fabricated rings
(straddling, fully east, fully west) - all three clipped exactly as expected.

## Finding + fix, 2026-09-13: MC00024178 (and any claim like it) drawn as a permanent marker instead of a shaped polygon

Ezra flagged a specific claim, MC00024178 (Gary Clayton Dunn, registered 2026-09-11), showing
as a bare circle marker on the map at every zoom level instead of a proper claim outline.
Confirmed in the live bundle: MC00024178 is present in `claims` (77 entries at the time) but
had **no matching entry in `tenure`** at all - the client engine's own documented fallback
("filled circle marker if a claim has no matching tenure polygon," see `map-pipeline.md`'s
Layers table) is working exactly as designed; the real problem is that this claim should never
have ended up in that fallback state in the first place, since `claims` is supposed to be
sourced from the exact same query as `tenure`.

**Root cause, found by reading `gis/basin_layers.py` directly**: the tenure loop (section 8)
drops a feature if its geometry Douglas-Peucker-simplifies down to fewer than 3 points
(`s = dp(...); if len(s) < 3: continue`) - a real, intentional guard against degenerate slivers.
The claims loop (section 8b) only checked `if not rings: continue` - a weaker test that doesn't
apply the same simplification-based rejection. A claim whose polygon is small/sliver-shaped
enough to fail the tenure loop's check was still passing the claims loop's looser one, so it
landed in `claims` with nothing in `tenure` to match against. **Fixed** in the handed-off
`gis/basin_layers.py`: the claims loop now requires `DISPOSIT_1` to already be present in the
tenure results before including a claim, so the two lists can't disagree about which
dispositions exist, by construction - not a second copy of the same rejection rule to
maintain in sync.

## Fixes bundled into one `gis/basin_layers.py` handoff, 2026-09-13

Sent to Ezra as a full-file replacement. Three independent fixes in one file:

1. **The MC00024178 claims/tenure mismatch above.**
2. **Lake self-intersection guard.** A severity threshold (crossing count > max(10, 10% of the
   ring's point count)) cleanly separates 6 genuinely badly-tangled shapes from 49 legitimate
   ones with harmless micro-crossings from Douglas-Peucker simplification. Those 6 are now
   skipped, and the "top" selection keeps scanning further down the ranked list until enough
   good ones are found.
3. **Real lake names via a proper gazetteer, not a guess.** `Hydrography/MapServer/80`'s own
   `LAKNAMEEN` field is blank for every big, well-known lake checked directly (Wollaston Lake,
   Reindeer Lake included). Found Saskatchewan's own `SaskNamesDatabaseWater` service (a point
   gazetteer, field `TOPONYM`) via the GeoHub's own service listing. The handed-off file pulls
   this gazetteer once and fills in any lake's blank name from the gazetteer point that falls
   inside its ring - never a guessed name, only ever a real `TOPONYM` from the source, and only
   when `LAKNAMEEN` itself is blank. **Confirmed live in the 2026-09-13 bundle pull: 60/60
   lakes named**, up from 48/55 previously - see `map-pipeline.md`'s "Named-lake mismatch"
   section for the gazetteer tie-break fix (largest-HECTARES match) that was needed on top of
   this, and its river-ranking fix that raised the cap from 55 to 60.

## Note, 2026-09-13: 25 km scale-bar gate replaces the old zoom-multiplier gate for lake/highway name labels

See `map-pipeline.md` for the full detail - a `currentScaleKm()` helper now gates lake/highway
name-label visibility on the same rounding logic the on-screen scale bar itself uses (<=25 km),
rather than an internal zoom-ratio multiplier with no visible on-screen correspondence.

## Note, 2026-09-13: click-to-interact hint text/position, company-website links reverted

See `map-pipeline.md` for the full detail - hint text shortened and repositioned, activation
area widened to the whole map card (legend toggles included), and the company-website-link
feature from 2026-09-12 was removed entirely per explicit instruction.
