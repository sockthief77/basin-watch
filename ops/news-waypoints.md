# News-release waypoints on the Basin Explorer map (2026-09-08, updated 2026-09-09, 2026-09-11, 2026-09-13)

**Supersedes the "Grade-release waypoints" section of `claude/map-pipeline.md`.** That
section described a green-star-only layer for grade-bearing releases. The layer now carries
every release type Ezra tracks, and the curation rules below replace the three-step recipe in
that section. Everything else in `map-pipeline.md` still stands.

Ezra's ask: "integrate the other news release entries into the Basin Explorer map, similar to
the Grade Releases. Georeference any maps in the news release, place a star on an inferred
location." Scope agreed the same day: all four non-grade release types, the same **7-day
window** as grade releases (replaced wholesale each edition, not accumulated), and figure
georeferencing built as a **flagged fallback** only.

## The record shape

```
{"n":"Wales Lake West Mobile MT", "co":"F4 Uranium",
 "x":-109.4820, "y":57.4426,
 "ty":"geo",              // release type  -> tooltip "Type" row AND star colour, see below
 "anc":"deposit",         // how the position was derived -> uncertainty ring
 "unc":6,                 // radius of that uncertainty, km
 "g":"~700 line-km Mobile MT; 2 NNW-SSE resistivity lows",
 "when":"2026-09-02", "url":"...", "note":"trilaterated from ..."
 "num":3}                 // rank in the brief's numbered news list -> badge on the star
```

`ty`, `anc`, `unc` and `num` are all optional. An entry with none of them renders as a grade
star anchored the old way, so nothing written before this change had to be migrated. `g` is the
headline figure as it appears in the tooltip - keep it to one line; for a non-grade item the
tooltip labels it "Detail" rather than "Grade". `note` is where the anchoring caveat goes.

`ty` values, current as of 2026-09-13 (2nd pass): `grade` (a chemical assay/calibrated result),
`cps` (this release's own headline number is a fresh handheld/downhole counts-per-second
reading, not a grade - **split out of `drill` on 2026-09-13** after Green Canada's and
CanAlaska's plain mobilization notices were found rendering purple alongside IsoEnergy's actual
cps reading, which was the only one of the three with real data), `drill` (program
starts/completions, permits, mobilizations - i.e. drilling-related news with **no reading
reported yet**; renders as the Other News catch-all colour, see below), `geo` (geophysics,
surveys, target definition - **its own colour as of 2026-09-13, see below**), `deal` (options,
acquisitions, JVs, community and benefits agreements), `mre` (resource estimates, PEA/PFS,
technical reports), `fin` (added 2026-09-13 - a financing/private placement; distinct from
`deal`, which specifically means a property transaction, not a capital raise).

The tooltip for every waypoint shows Type, UTM position and anchor method rows in addition to
the standard name/company/date/detail/link rows.

## Visual encoding - stars, FOUR colours as of 2026-09-13 (2nd pass), shared outline, size

**Every waypoint is a star.** A per-type glyph set (diamond / triangle / square / hexagon) was
built first and dropped the same day on Ezra's instruction: "Make these all stars as well,
maybe a very light jasper blue color?" **Do not reintroduce shape encoding without asking.**

**Colour now carries FOUR meanings - refined twice on 2026-09-13.** First pass added a purple
"fresh cps" tier so a real-data drilling release (IsoEnergy) would no longer read identically
to a bare mobilization notice, matching the "why" paragraph prose (`.g-assay` gold vs `.g-cps`
purple). Ezra caught two problems with that first pass live: the purple was too low-contrast,
and it had been applied to the whole pre-existing `drill` bucket rather than specifically to
releases with an actual reading, so two plain mobilization notices (Green Canada, CanAlaska)
were showing purple with nothing to back it up. Second pass fixed both, and Ezra asked for a
fourth tier on top - geophysics surveys get their own colour rather than disappearing into the
Other News catch-all, since a completed multi-thousand-line-km survey with named anomalies
(Terra North) is a materially different kind of release than a financing notice, even though
neither is a grade or a cps reading. Current scheme:

- **Grade releases (`ty==='grade'`): bright green fill `#00e64d`** (unchanged throughout).
- **Fresh cps releases (`ty==='cps'`): bright purple fill, constant `NEWSDCOL`, currently
  `#B266FF`** (brightened twice: `#B295DC` -> `#C9A2FF` -> `#B266FF`, each pass because the
  previous one still read as too washed-out against the dark map). Same colour as the `.g-cps`
  prose class (also updated each time, kept in lockstep - see the drift-check tool note below
  for why "kept in lockstep" now means something more than "remember to do it"). **Only for a
  release whose own headline content IS a reading** (IsoEnergy's "every number is a
  counts-per-second reading" release) - a mobilization/permit notice with no data yet is
  `ty:'drill'`, not `ty:'cps'`, and renders as the yellow catch-all below, however
  drilling-related its subject matter.
- **Geophysics/survey releases (`ty==='geo'`): bright orange fill, constant `NEWSGEOCOL`,
  `#FF7A1A`** (added 2026-09-13, 2nd pass). **Deliberately still counted under the "Other
  News" toggle/legend row (`ON.newsx`), not a separate 5th layer-bar entry** - Ezra's explicit
  ask was to add the colour distinction "to keep it less busy," i.e. more information in the
  star colour without more clutter in the toggle list. Implementation: `NEWSX` (the array the
  `newsx` toggle draws) still contains every `ty` that isn't `grade` or `cps` - geo included -
  and each item already carries its own resolved `w.col` (orange for geo, yellow for
  everything else) from ingestion, so one draw pass naturally renders two colours without a
  second toggle or a second `ON` flag.
- **Everything else (`ty` is `drill`, `deal`, `mre`, `fin`, or absent): bright yellow fill
  `#ffe600`**, `NEWSXCOL`. Colour history before the cps/geo split: light jasper blue `#9fcdea`
  (2026-09-08 to 2026-09-09) -> deeper blue `#2f7dc7` -> bright turquoise `#20e8c8` -> bright
  yellow `#ffe600` (all 2026-09-09, see prior revisions of this doc for the blow-by-blow).
- Applied to both Basin Watch and Basin Explorer, and - as of 2026-09-13 - to `site/shell.html`
  and `site/explorer-shell.html` in the repo too (`basinwatch.ca` is now the canonical build
  target, see `map-pipeline.md`'s "basinwatch.ca is the end product" section - a colour/engine
  change like this belongs there first from now on, not on a claude.ai copy).
- **`scripts/check_site_drift.py` (added 2026-09-13) checks that `NEWSXCOL`, `NEWSDCOL`,
  `NEWSGEOCOL`, the `col:` assignment ternary, and the `NEWSG`/`NEWSD`/`NEWSX` filter
  definitions are byte-identical between `site/shell.html` and `site/explorer-shell.html`.**
  Run it (`python3 scripts/check_site_drift.py` from the repo root) before publishing any
  change to either file - see `map-pipeline.md`'s "basinwatch.ca is the end product" section
  for the incident history this was built to stop repeating.
- **Outline: still shared `surf` stroke** (the `--surface` panel colour) across all four
  colours - unchanged, not reopened by either 2026-09-13 revision.
- **Star size: unchanged** (`r=7.14,r2=r*.42`) - unaffected by any colour change.
- If asked to change the fill colours again, keep each a single flat colour across all
  waypoints of that kind - see the per-company-fill note below for why that matters more than
  the exact shade. **Watch for readability clashes against other fixed-colour layers** - check
  a new colour against every layer colour listed in `map-pipeline.md`'s Layers table (Boulder
  Heat's gold `#e6b40a` and SMDI's orange `#f97316` both sit near this palette already, which
  is exactly why `NEWSGEOCOL` was picked as a more saturated red-leaning `#FF7A1A` rather than
  a plain amber that would blend into either of those two).

The first pass filled non-grade stars from `HCOL` so each waypoint matched its company's ground
underneath; Ezra asked for a single colour instead. Keep it that way - the waypoint layer reads
as one thing sitting on top of the map, and the company is named on hover. The `coColor()`
display-name-to-holder-key matcher that supported the old scheme was removed, not left dead.

## Why-paragraph U₃O₈ colour: fresh vs. historical (added 2026-09-13)

Ezra's ask: the map's colour distinctions above should extend into the ranked news items' own
"why" prose, not just the star/rank badge - specifically, a release's own **fresh** headline
assay figure should read in the same green as a Grade Release star, while a
**historical/prior-drilling** figure quoted for context in the same paragraph should keep the
existing gold. Two CSS classes now do this (both in `site/shell.html`'s `<style>` block; not
needed in `explorer-shell.html`, which never renders news prose):

- **`.g-assay-fresh` (new, green `#00e64d`)** - this release's OWN new number. Example: the
  2026-09-13 edition's Purepoint item, "Best result is NV26-05, 0.3 m at
  `<span class="g-assay-fresh">1.65% U₃O₈</span>`".
- **`.g-assay` (unchanged, gold `#F2C14E`)** - a figure from PRIOR drilling/a different program,
  quoted for comparison. Example, same Purepoint item, a plain (unwrapped, this edition) later
  mention: "previous Nova drilling of up to 8.1% U₃O₈ over 0.4 m" - historical, not this
  release's result, so it does NOT get `.g-assay-fresh` even though it's also a U₃O₈ figure in
  the same paragraph.
- `.g-cps` (purple, same `NEWSDCOL` value as the map/badge - kept in lockstep each time that
  constant is brightened) already only ever wraps a release's own fresh cps reading in
  practice - no historical/fresh split needed for that class, it was already consistent.

**Every future edition's own authoring pass needs to pick the right class per figure** - this
is a content-authoring judgment call (which number is "this release's own headline result" vs.
"a number quoted for context"), the same kind of call already being made correctly in the
prose text itself (compare how carefully existing editions already say "historical Orchid Lake
boulder grabs" or "Crackingstone's own historical record" in plain words) - it just wasn't
being reflected in the span class before 2026-09-13. When in doubt, the item's own lead
sentence usually says explicitly whether a number is new or historical; match the class to
that, don't guess from the number's position in the paragraph alone.

## Rank badges: the brief's item number on the star (added 2026-09-09)

Ezra's ask: "For each of the numbered news release entries, add a number to the star which
represents it on the Basin Explorer map." Applied to **both** pages, not Explorer only - the
numbered list itself lives on Basin Watch and the two map engines otherwise stay identical.

- A waypoint carries `num` = its rank in that edition's "Ranked by technical materiality"
  list. Waypoints **not** in the numbered list get no `num` and no badge: context notes
  (CanAlaska's Key Extension mobilisation, carried in the majors note), out-of-window items,
  anything mentioned only in prose. Absent `num` is the default, so nothing older needed
  migrating.
- **Every edition must set `num` when it replaces the `news` key**, in the same pass that
  writes the waypoints, and must renumber - ranks change edition to edition and a stale `num`
  is worse than none. **As of 2026-09-11, the goal is zero gaps** - see "Active anchor search"
  below; a gap is now a sign the search wasn't tried hard enough, not an expected steady state.
  (Historically, ranked items whose anchor didn't hold stayed off the map entirely, so the
  numbers on the map were a subset of the list with gaps - e.g. edition 001 rendered 1, 4, 6
  and 7, with 2, 3 and 5 unanchored. That's no longer the default expectation for numbered
  items - see below.)
- **Every edition must also DROP any waypoint whose release has aged out of the current 7-day
  window** - found live 2026-09-13: a Skyharbour "Moore & Russell Lake NI 43-101" waypoint
  dated 2026-09-03 was still sitting in `BASIN_BUNDLE.news` and rendering on the map days after
  it should have rolled off, and it wasn't mentioned anywhere in the current edition's own
  text. Ezra caught it by clicking a star and getting content that didn't match anything in
  that day's article. **The `news` array is supposed to be replaced wholesale each edition, not
  accumulated** (stated as the scope back at the top of this doc) - this is that rule being
  violated in practice, not a new rule. Check the whole array against the current edition's
  actual content before publishing, not just against what's being added.
- **Gap found live, 2026-09-13: Edition 003 shipped with items 3 (Terra Clean Energy,
  financing) and 6 (Belmont Resources, gravity-survey mobilization) both missing `num` AND a
  waypoint entirely** - only 1, 2, 4, 5 were in `BASIN_BUNDLE.news` at first, and Ezra noticed
  and asked about it directly ("How come the Terra and Belmont news releases aren't numbered on
  the map or colored yellow?" - conflating Terra Clean Energy, #3, with the differently-named
  Terra North Resources, #4, which DID already have a waypoint). Both were anchored and added
  after the fact (Terra Clean Energy to the Fraser Lakes B showing / SMDI #5289, already
  resolved in an earlier edition per rung 3's worked example below; Belmont to a centroid of
  the three Crackingstone Peninsula SMDI occurrences closest to the release's own "~8 km
  southwest of Uranium City"). **Going forward: every numbered item gets an anchor attempt per
  the existing "Active anchor search" rule below, financings included** - don't assume a
  release "obviously" has nowhere to point without trying rung 2/3 first.
- **Rendered as a small pill pinned to the star's upper right** (centre `x+7.6, y-7.6`, half-
  height 5.5px, widening for two digits via `measureText`), filled in that star's own colour
  with the shared `surf` outline, digit in `surf` at `700 8.4px "IBM Plex Mono"`. Uses
  `ctx.roundRect` with a plain `arc` fallback.
- **The number is deliberately NOT drawn inside the star.** That was built and rendered first,
  at several font sizes, with and without a same-colour halo: at the star's 7.14px outer radius
  (3.0px inner) the digit is illegible at real map scale in every variant. Don't move it back
  inside without re-testing at 1x - it only looks fine zoomed in.
- The badge inherits the star's favourite-dimming alpha, so a non-favourite's number dims with
  its star rather than floating over the map at full strength.

## Z-order: Grade Releases now sit on top of Other News (reversed 2026-09-09)

**This is the opposite of the original rule and supersedes it.** From 2026-09-08 to
2026-09-09 the rule was "Other News is always drawn on top of Grade Releases" (Ezra: "never
have these icons be obscured by the actual grade releases"). On 2026-09-09 Ezra asked for the
reverse: **"Make the Grade Releases green stars obscure the Other News stars if they occupy
the same area."** Grade releases (green) are now painted last, so a green star sitting on top
of a turquoise one hides it; the reverse is fine and expected.

Implementation, both pages, `shell.html`/`explorer-shell.html`'s map engine:

- Draw pass order is `[[NEWSX,ON.newsx],[NEWSD,ON.newsd],[NEWSG,ON.news]]` (Drill Results
  pass added 2026-09-13, between Other News and Grade, so grade still wins any collision and
  the cps tier still wins over plain other-news/geo) - Other News first (bottom), cps tier,
  Grade last (top). Geo items live inside the `NEWSX` pass (see "Visual encoding" above) so
  they paint at the same layer as the rest of Other News, just in their own colour.
- `pick()`'s hover hit-test walks the same order (`NEWSX`, then `NEWSD`, then `NEWSG`) using
  `<=` rather than `<` on the distance test, so on a tie the later-checked (grade) marker wins,
  matching what's visible.
- This is a real collision, not a hypothetical: Paladin's Atlas grade result and its Birch
  Narrows agreement sit ~3 km apart, about one marker-width at basin zoom.

**Do not revert to the old "Other News on top" order without Ezra explicitly asking again** -
this has now flipped once already and needs to stay whichever way he last said.

## The anchor hierarchy - work down it, stop at the first that holds

`anc` records which rung was used, and drives the dashed uncertainty ring drawn around the
star. The ring is sized in **real kilometres**, so it grows as the viewer zooms in: a claim-
block centroid stops looking like a drill collar the moment the scale makes the difference
matter. Default radii when `unc` is absent: `collar` 0, `deposit` 1.5, `claims` 6, `figure` 2.

1. **`collar` - a coordinate table in the release.** Most Athabasca juniors publish a drill
   hole table with UTM 13N easting/northing per collar, in the body or an appendix. Exact,
   free, and the old recipe never looked for it. **Check this first, every time, including for
   grade releases.**
2. **`claims` - the holder's own claim block.** The bundle already carries every active
   disposition with its holder string. Group that holder's claims into contiguous blocks and
   take the centroid of the right one. Self-maintaining, and works for releases carrying no
   coordinate at all.
   **Caveat proven on the first edition: picking the LARGEST block is wrong often enough that
   it cannot be used blind.** Paladin's largest cluster (18 claims, -104.51/57.11) is nowhere
   near PLS; its second (17 claims, -109.35/57.61) is. Stallion's four clusters give no way to
   tell which is Moonlite. Use this rung only when the release names something that identifies
   *which* block - then it is good: Skyharbour's second cluster (-105.26/57.44) landed 4 km
   from the independently trilaterated Moore position, two methods agreeing.
   **If a direct claims-block search under the company's own display name comes up empty**
   (zero features), don't stop there - the registry records the legal/registered holder name,
   which is frequently not the company's brand name: a predecessor company (renamed or
   RTO'd), an option/JV partner named in the release, or a subsidiary. Try those names too
   before concluding this rung doesn't hold. Example (2026-09-11): Green Canada Uranium's
   Marshall claim is registered to "BASIN ENERGY NORTH MILLENNIUM CORP." (the prior owner's
   entity, named in Green Canada's own disclosed option structure), not to Green Canada at
   all - an `OWNERS LIKE '%GREEN CANADA%'` search alone would have (and initially did) come up
   empty.
   **Geometry safety**: when pulling a claim polygon's centroid via WebFetch, use the
   **bounding-box midpoint** (min/max x, min/max y - four numbers), not an average of every
   ring vertex. A single claim can carry 300+ vertices, and WebFetch's summarization of a long
   coordinate list is exactly the failure mode the skill already warns about for the tenure
   registry's row lists - it applies just as much to silently mis-averaging a vertex list into
   a wrong centroid. The bbox midpoint needs only 4 numbers transcribed correctly.
3. **`deposit` - offset from a mapped deposit.** Cross-reference the project name against
   `BASIN_BUNDLE.deposits`/`smdi` or the footprints layer. Where the release states distances
   to **two** mapped deposits, trilaterate rather than guessing a bearing - both first-edition
   trilaterations resolved cleanly, and the ambiguous second intersection was discarded using
   the direction words in the release ("northeast of", "east of").
   **If the project name itself isn't in the bundle**, don't stop there either - search for
   what specific named historical showing or deposit actually sits on that property (a
   technical report, an old PR, or even an unrelated recent article about the property often
   names one) and look *that* name up in `deposits`/`smdi` instead. Example (2026-09-11):
   Terra Clean Energy's South Falcon East property isn't itself a named deposit, but hosts the
   "Fraser Lakes B" showing (found via a web search, not the bundle) which IS in `smdi` as
   "Fraser Lake Zone B" (#5289) - a solid anchor the passive cross-reference alone would have
   missed. Cross-validate against any distance/bearing description in the release or on the
   company's own site when one exists (South Falcon East's "50 km east of Key Lake Mill"
   landed within ~20 km of the Fraser Lakes B anchor - good enough agreement to trust both).
   **This exact anchor (Fraser Lakes B / SMDI #5289) is why the 2026-09-13 gap noted above was
   avoidable** - a South Falcon East financing item has a resolved anchor sitting right there
   from a prior edition; it wasn't reused for Edition 003's item 3 until after the fact.
4. **`figure` - read a coordinate or grid reference off a figure in the release itself.**
   Flagged fallback only, per Ezra's original scope ("figure georeferencing built as a flagged
   fallback") - use it when nothing above holds, and say so in `note`. **Release figures are
   not always UTM Zone 13**: Stallion's Stone Island figure is NAD83 Zone 12, so reading it
   through the shared `UTM13()` transform would land badly wrong. Check the figure's own grid
   labelling before transforming, every time - don't assume Zone 13 because the property is in
   the basin.

If none of the four rungs holds, leave the item off the map rather than guess, per the
original grade-waypoint rule this recipe inherited (see `map-pipeline.md`).

## Active anchor search for numbered items (added 2026-09-11)

**Scope: this applies to items that make the numbered "Ranked by technical materiality" list
only** - not majors-note context items, not out-of-basin watchlist mentions, not anything
carried only in prose. Numbered items are the ones the map's rank badges point at, so they're
the ones worth the extra effort; everything else keeps the old passive-check-only behavior.

**For a numbered item, "no anchor found" now means an active search was tried and came up
empty, not that the bundle didn't already contain an obvious match.** Concretely, before
leaving a numbered item off the map: one web search for a named deposit/showing on the
property (rung 3) or for the release's actual registered/predecessor/partner company name
(rung 2), then the corresponding bundle lookup or ArcGIS query. That is the bound - roughly
one extra search-plus-lookup pass per unanchored item, not an open-ended investigation. If
that doesn't turn up a rung 1-3 anchor, leave the item off per the standing rule; don't reach
for rung 4 (figure-reading) just to fill a gap, and don't guess a bearing/distance without a
release-stated or company-stated figure to anchor it to. **This still wasn't applied to two
items in one live edition (2026-09-13 finding, above) - re-check every numbered item against
this rung list before finalizing an edition, don't rely on remembering to run it.**

This is a real, if modest, per-edition cost - each search-plus-lookup pass is a handful of
extra tool calls - so it's worth doing once a genuine attempt is warranted (i.e., for the
numbered list, which is short), not for every mention anywhere on the page.

## Two findings worth not rediscovering

Both proven the hard way on the first edition and worth keeping in mind before repeating
either mistake: picking a holder's **largest** claim block as an anchor is wrong often enough
to be unusable (Paladin's largest block, 18 claims, is nowhere near PLS - see rung 2 above);
and release figures are **not always UTM Zone 13** - Stallion's Stone Island figure is NAD83
Zone 12 (see rung 4 above).

**Note reconstructed 2026-09-09:** an earlier edit this session overwrote this file without
first reading it in full, truncating everything from rung 4 onward. The anchor-hierarchy tail,
the hover-row line and the findings section above were reconstructed from references to this
file in `open-items.md` and should be treated as a faithful paraphrase, not a guaranteed
verbatim restoration of whatever else may have been below rung 4 originally.

**Second reconstruction note, 2026-09-13: this happened again the same way, same session that
was doing the colour-scheme work** - a `project_write` replaced this file's full content
without first re-reading everything below "Rank badges," briefly dropping this Z-order
section, the anchor hierarchy, "Active anchor search," and this section itself. Caught and
restored within the same turn by re-reading the file immediately after writing and noticing
the gap, before anyone downstream relied on the truncated version. **The actual lesson, twice
now: when editing a long project doc via full-file rewrite, diff the new content against the
last known-good version's section list before writing, not just before-and-after on the
specific section being changed** - editing a few sections in the middle of a long doc from
memory, rather than the full text in hand, is exactly how a tail goes missing without anyone
noticing until they search for something that used to be there.

## Proposed ranking-tier rule (raised 2026-09-13, adopted the same day - see `open-items.md`)

Ezra flagged a real inconsistency in Edition 003's own order: #3 (Terra Clean Energy's
financing, no named program, no technical milestone) ranked above #4 (Terra North's completed
2,441 line-km airborne survey, seven named anomalies) - a materially thinner release outranking
a materially thicker one, under a page that explicitly claims to rank "by technical
materiality." Nothing currently documented says what breaks a tie or orders across release
*types*, only within them.

**Fix, confirmed adopted 2026-09-13 (Ezra said "Yes" to retroactive application - see
`open-items.md`'s "Still open" note for the exact status of the retroactive relabel):** use the
same four-way category split the colour scheme now encodes as a first-order ranking tier, high
to low: `grade` > `cps` > `geo` > everything else (`drill`, `deal`, `mre`, `fin`). Within a
tier, rank by whatever the brief already uses (materiality of the specific figures, apparently
recency/scale today - not changed by this rule). This puts a completed survey (`geo`) above a
plain financing (`fin`) automatically, without needing a special-cased rule for that specific
pair. Applied retroactively to `data/bundle.json`'s `news[].num` fields and
`data/edition.json`'s article order the same day (Purepoint=1, IsoEnergy=2, TerraNorth=3,
Belmont=4, TerraCleanEnergy=5, GreenCanada=6).
