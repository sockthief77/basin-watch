# Basin Watch roadmap - potential future changes

**This file replaces `feature-requests.md` and `launch-readiness-review.md` (2026-09-09).**
Merged 2026-09-11 per Ezra's request for one place to track changes he might make, rather than
three sources of overlapping ideas. Both source docs are retired; nothing in them is lost -
everything below is carried forward, deduplicated where two items described the same fix twice.
Original dates are kept on each item so the history is still visible.

**Status: this is a backlog, not a build queue.** Nothing below has been built. Read it before
starting build work so nothing gets lost or duplicated, and check an item off (or delete it)
here when it ships.

## TOP PRIORITY item RESOLVED 2026-09-14: real write access to `sockthief77/basin-watch`

**This section previously read "TOP PRIORITY, raised repeatedly (2026-09-13)" and is now
resolved.** See `basinwatch-pipeline-fix.md`'s "Standing note: real git write access confirmed
2026-09-14" section for the full detail: a Claude Code session/environment with
`sockthief77/basin-watch` selected as its repository has real git push access, confirmed by an
actual test push. The manual download-and-upload workflow described below (and throughout
`daily-publish-instructions.md`, `history.md`, `open-items.md`, `claim-monitor-state.md`) is
now superseded for that session type - kept here as the historical record of why it was such a
persistent, repeatedly-raised ask.

**Ezra, verbatim, after being asked to confirm this should be logged: "Yes, you know I do. I
want this automated. I've said it like 10 times already."**

**The actual cost this solved:** every fix this project made to the repo (`basin_layers.py`,
`site/shell.html`, `site/explorer-shell.html`, `data/edition.json`, etc.) had to be handed to
Ezra as a full-file download, and he had to manually upload each one via GitHub's web editor
(Add file -> Upload files) and commit it himself, then separately trigger `gis-export.yml` by
hand when a data-pipeline file changed. This worked, but it was a manual step on every single
change, and Ezra flagged the friction of it many times, not just once.

**Why it was like this, historically:** the old Cowork scheduled-task session type only ever
got read-only repo access (a plain `git clone`, no credential) - confirmed multiple times.
`git push --dry-run` returned "access denied by the git proxy... not in this session's
authorized repository set," with no self-service UI for adding it found in that product
surface. **That finding was from a Cowork scheduled task specifically** - it was never a
limitation of Claude Code environments generally, which is the surface that resolved this
2026-09-14 via the repo-picker on the task composer (real GitHub App OAuth-based write access,
confirmed by an actual test push to a throwaway branch).

## What's strong - keep doing it (2026-09-09)

The editorial layer is genuinely differentiated and is the thing a paying geologist or
analyst would value most: the cps-vs-assay distinction enforced on every number, the `warn`
chips naming what a release doesn't say, the closeology guard on Lancaster's borrowed
Centennial-deposit grades, the price-freshness rule that prints a dash rather than a stale
quote. No free aggregator applies this kind of judgment. The map's geoscience layer depth
(boulder/geochem heat, SMDI, EM conductors, deposit footprints) is beyond any free public
tool. This is the foundation to build on, not rework. **Also: Ezra likes the "hard numbers"
close on each news item (added 2026-09-11) - keep this, don't cut it in any redesign.**

## New layer idea: hunting and fishing lodges (added 2026-09-11, parked - come back to this)

Ezra uploaded a KML (`Hunting_and_Fishing_Lodges_SK.kml`, with an empty QGIS `.qmd` sidecar -
no useful metadata in it beyond a CRS block) and asked to explore adding it as a new toggleable
point layer in Basin Explorer's left-side layer bar. Not built - just scoping it here so the
next session can pick it up without re-deriving the dataset shape.

**What's in the file:** 178 point placemarks across Saskatchewan (province-wide, not
basin-only), each with a name, a numeric `ID`, and an `Outfitters` category split roughly
evenly three ways - 60 "Both Fishing and Hunting", 59 "Only Fishing", 59 "Only Hunting".
Coordinates are plain lon/lat (KML's mandatory WGS84 decimal-degree format, e.g. Misaw Lake
Lodge at `-102.606, 59.921`) - no reprojection needed despite the `.qmd`'s UTM13N CRS block,
which describes the QGIS project's display setting, not the KML's own coordinate system. No
address, website, or contact fields - name, ID and category only.

**Decided 2026-09-11: filter to the basin-proximate subset**, not all 178 - same treatment as
every other point layer on the map. Using the project's actual basin cutoff (`NORTH_CUT_M` =
6,250,000 m UTM13N Northing, the same constant every other layer's `northOK()` filter already
uses - not the looser 55.5N Alberta-tenure floor, which is a different, more southerly line
used only for that one layer) and reprojecting the KML's WGS84 points to EPSG:2957 to check:
**42 of the 178 lodges fall inside the basin cutoff.** Category split within that subset skews
fishing-heavy - 22 Both, 19 Only Fishing, 1 Only Hunting - which tracks: hunting outfitters
concentrate further south in the province, fishing lodges follow the lake country that overlaps
the basin. Build should filter with this same `NORTH_CUT_M` constant at ingest, matching how
every other point layer already gets cropped, rather than inventing a separate cutoff for this
one layer.

**Practical build notes for whoever picks this up:** needs its own glyph/colour, distinct from
the existing waypoint stars, deposit squares, SMDI dots, and town markers, to avoid reading as
another exploration signal - something like a small tent/cabin icon reads as clearly
non-uranium at a glance. Default off, like the other reference layers (Mines & Mills,
Restricted Lands). Category (Only Fishing / Only Hunting / Both) is a natural tooltip field
and could support the same colour-by-category treatment used for grade vs. non-grade
waypoints, if that reads as useful rather than just decorative. **Source file saved:** the KML
is stored in the project at `claude/hunting-fishing-lodges-sk.kml` (the `.qmd` sidecar carried
no useful data, so it wasn't copied over) - a future session can read it directly, no need to
ask Ezra to re-upload.

## JV / majority-operator tenure attribution for Top 10 Holders (added 2026-09-11, decided 2026-09-11, **BUILT and published 2026-09-11**)

**Built and live on all three surfaces:** Basin Watch (claude.ai artifact, Version 158),
Basin Explorer (claude.ai artifact, Version 93), and `site/shell.html` on basinwatch.ca
(patched file handed to Ezra for paste-and-commit; pending his confirmation it's live).

**What actually shipped, superseding the original plan below it:**

- **Top 10 ranking is now by hectares, not parcel count** (was parcel count all along -
  discovered mid-build, Ezra's call: "Switch to hectares while we're in here"). Every JV
  parcel's hectares are split by exact financial-ownership percentage across all named owners
  and added to each owner's running total - not just majority/minority, any N-way split.
- **JV percentages are read live from MARS's own `OWNERS` field**, which already encodes
  exact splits verbatim (e.g. `"ISOENERGY LTD.: 50.000%;  PUREPOINT URANIUM GROUP INC.:
  50.000%"`) - no hardcoded table needed for any Saskatchewan JV. The originally-planned
  override table was dropped once this was discovered; it turned out to be unnecessary
  engineering for the common case.
- **One exception still needs a manual override, deliberately deferred (not built):** Alberta's
  tenure registry (`gis.energy.gov.ab.ca`) only names a single "designated representative" per
  agreement and hides the real split - confirmed for Rea, registered under Orano despite
  GoldMining holding 75%. This is the only remaining gap; everything else in the roster is
  registry-sourced automatically.
- **Map treatment is a single flat colour (the primary/largest owner's) plus a diagonal hatch
  overlay** flagging "shared ground," instead of the originally-planned two-colour diagonal
  split-fill. The split-fill broke down once real 3-way (Hook Lake) and 4-way (Northwest
  Athabasca) JVs turned up in research - Ezra: "This is becoming convoluted... Back to square
  one." The hatch scales to any party count without getting busier; the full percentage
  breakdown moved to the tooltip only (plain text, not pixels, handles any N).
- **Tooltip's Holder row is now JV-aware**, listing every owner and their percentage when the
  parcel is jointly held.
- **Known, accepted limitation:** isolating a *minority* JV partner on the map (e.g. Cameco's
  39.5% of Hook Lake) will not highlight that ground, since colour/isolate-matching is keyed to
  the plurality owner only. This does not affect the Top 10 hectare math, which correctly
  splits every owner's true percentage regardless of rank. Flagging here rather than fixing
  now - narrow edge case, real fix would need a from-scratch isolate mechanism.

Original plan (superseded by the above, kept for the decision trail):

Ezra's original call was Top 10 hectares split by ownership percentage, a two-colour diagonal
split-fill on the map, a one-line tooltip fact, and a small hardcoded JV override table
maintained opportunistically alongside the roster doc. All of this shipped except the visual
treatment (hatch instead of split-fill, once real multi-party JVs showed the split-fill
wouldn't scale) and the override table (superseded by MARS's own live `OWNERS` field for every
Saskatchewan JV; Rea/Alberta is the one JV still needing a manual entry, not yet added).

## Ranked list and map churn (added 2026-09-11, from a review this chat did earlier the same day)

Four related ideas about how the numbered ranking and its map badges behave day to day as
items enter and age out of the 7-day window. None built yet.

1. **Clarifying subtitle on the 7-day ranking window.** The ranked list is implicitly a
   rolling 7-day window, but nothing on the page states that - a reader landing cold could
   assume "ranked" means all-time or month-to-date. Add a small subtitle under "Ranked by
   technical materiality" naming the window explicitly.
2. **Stable/decoupled map rank badges.** The numbered badge on a map waypoint currently
   mirrors that day's position in the ranked list, which reshuffles daily as items enter and
   age out - so the same company's marker can jump from #2 to #5 to unnumbered with no change
   to the underlying release. Decouple the badge from the daily rank (e.g. show it only while
   the item is genuinely new, or drop the number and rely on the star/legend) so the map
   doesn't visually reset every morning.
3. **"New today" flag on ranked items.** No visual distinction currently between an item
   appearing in the ranked list for the first time today and one that's been sitting there a
   few days. A small flag would let a daily reader jump straight to what's actually new.
4. **Day-6/7 "last day in window" warning, instead of implicit rank decay.** An item's
   position can read as decaying as it nears the edge of the 7-day window, which looks like
   the story is getting less material when nothing about the release itself changed - it's
   just about to fall off. Replace that with an explicit flag on day 6-7 ("last day in the
   ranked list") so the drop-off is a stated fact, not a confusing implicit rank shift.

The fifth idea from that same review - a persistent table for programs that are still running
when they age out of the 7-day window - is the same fix already covered under Data gaps below
("Programs age out of the 7-day news window while still running"); see that item rather than
duplicating it here.

## Data gaps (2026-09-09, unless noted)

- **Nothing accumulates - the single biggest miss.** Every edition is a snapshot, archived
  as frozen HTML with no queryable history. Corporate/institutional readers want basin-wide
  series (metres drilled per quarter by company, financings per month, staking rate, hectares
  gained/lost by holder over 12 months) that nobody currently sells - the brief computes every
  one of these daily and discards them. Fix: write each run's numbers to a flat
  `history.jsonl` (or similar) starting now, before anything reads it. In 6 months this is a
  proprietary dataset. Same fix resurrects the price-sparkline idea that was dropped for
  staleness (stockanalysis.com runs 2-3 weeks stale) - the brief already pulls a
  freshness-validated quote per ranked company every run; storing them builds an own-sourced
  price series with zero new fetches. **This is also the fix for two items flagged 2026-09-11:
  archive browsing as a real series rather than one-off frozen pages, and a U3O8 price-history
  view** - both need the same `history.jsonl` store, not separate mechanisms.
- **Cash runway is the most predictive junior-explorer variable and is absent.** Documented
  as blocked on SEDAR+ (bot-blocked), but cash-on-hand doesn't need SEDAR+ - quarterly MD&A
  PDFs are on company websites and fetchable, and it's quarterly data so a stale-by-weeks
  figure is still correct. Refresh monthly, not daily, separate cadence from the daily sweep.
- **No valuation comparables.** EV/lb resource is the standard uranium comp metric and isn't
  computed anywhere, despite the brief already having market cap and shares outstanding for
  every ranked name. Adding net cash and resource figure for the ~8 names with a defined
  resource gives a peer table that answers "has the market already paid for this" - currently
  unanswered anywhere on the page.
- **Programs age out of the 7-day news window while still running** (flagged twice already in
  `open-items.md`/`claim-monitor-state.md`: Lorado, F4 Wales Lake). News and state are
  different objects. Add a persistent "Active programs" table (operator, project, holes
  planned/completed, metres, start date, results outstanding) that updates rather than ages
  out - answers "who is drilling right now and when do we hear" directly. Same underlying
  need as idea #4 in the "Ranked list and map churn" item above.
- **Geologist-specific gap: no depth-to-unconformity / sandstone-thickness layer** - the
  first-order screening variable in the basin, and the map is plan-view only. Historical
  drillhole collars from SMAD (once out of the confidentiality window) would be a real
  differentiator nobody else publishes for free.
- **`generated` field is overloaded and will read as wrong once paying customers rely on it.**
  It's bumped to the publication date each edition so the 7-day lapsing window tracks "today,"
  but the underlying tenure snapshot can be (and per the docs, currently often is) days older,
  since it only refreshes when `basin_layers.py` is run. One field carries two meanings and a
  subscriber will read it as data freshness. Split into `data_asof` (true vintage of the
  tenure pull) and `window_anchor` (today) - print `data_asof` visibly on the map.
- **SMDI grade provenance is hover-only.** The visible on-page disclaimer was intentionally
  removed at Ezra's request (documented in `open-items.md`) and that's a reasonable call for
  a private page. Worth reconsidering once the page is public and paid: nine of 1,170 parsed
  SMDI grades were chemically impossible (>100% U3O8) before client-side sanitizing, and a
  "grade" number with provenance only on hover is the kind of figure that gets screenshotted
  out of context. A short source line in the layer bar itself (not a page-wide caption) would
  cost little visually.

## News-feed UI (2026-09-09, unless noted)

- **No filtering on the news list, and no saved watchlist.** Favourites exists on the map
  only. Unify: starring a company should filter both the map and the news feed. Add a
  release-type filter (drill/financing/geophysics/permitting/corporate) - the `ty` field
  already exists on waypoints, so the data's there, just not exposed as a control on the news
  side. **This is the same fix as the "watchlist" request flagged 2026-09-11** - a saved list
  of companies to track, surfaced in the news feed as well as the map, is what a unified
  favourites-as-filter mechanism gives you; build it once, not as two separate features.
- **No archive search.** "Every Denison item this year" is table stakes for a paid product
  and is currently impossible - the archive is one-line summaries pointing at frozen
  snapshot artifacts, not a queryable store. Depends on the same history-accumulation fix
  above.
- **The why-paragraphs are written for geologists and lose retail readers.** The bold lead
  sentence is already a good summary; make the rest collapsible - default open on desktop,
  default collapsed on mobile. Serves both audiences from the same content.
- **Signal tiles have no comparison point.** "10,159 metres" means little without last
  week's figure. Add a delta once the history store exists.
- **Confirmed mobile bug:** the page scrolls horizontally at 390px viewport width. The
  masthead ticker (`.ticker`, `display:inline-flex`, no-wrap content) overruns the right
  edge; on the map, the axis tick labels collide with the scale bar.
- **Dark-only is a deliberate, documented choice** (`map-pipeline.md`: "Dark mode is the
  only mode for this page, always" - explicit operator instruction). Flagging only because a
  public launch adds daylight-field and print-for-a-meeting use cases that didn't exist for a
  private page - not a recommendation to change it, just worth revisiting once, not undoing
  unilaterally.

## Map UI (2026-09-09, unless noted)

- **Persist Basin Explorer favourites across sessions (added 2026-09-11).** Currently reset
  on close/reopen. Needs `localStorage` (or similar per-viewer storage) so a starred company
  stays starred.
- **Tenure layer is an undifferentiated grey-white mass at reset zoom** - the map's core
  promise (who holds what) is illegible until zoomed in. Consider colouring only the top-N
  holders at low zoom and neutralizing the rest, or rendering tenure as density below a zoom
  threshold.
- **No URL state.** Highest-value cheap addition for professional users: a geologist can't
  send a colleague "the map at Davidson River with tenure and conductors on." Serializing
  view + layer toggles to the location hash gives shareable deep links, which also functions
  as free word-of-mouth marketing.
- **No search box.** Basin Watch currently has no Filters panel at all (see the `mkSel`
  breakage documented in `open-items.md`). Rather than restoring the old four dropdowns, one
  search field (company / claim number / deposit / place name) replaces all of them and is a
  better control anyway.
- **No export.** Geologists will want this week's new claims as GeoJSON for ArcGIS Pro - the
  pipeline already generates exactly that file (`claim_export.py`). Near-free paid-tier
  feature.
- **Thirteen toggles with no grouping.** Three group headers (Activity / Tenure / Geoscience)
  would cost a handful of markup lines and meaningfully help a first-time visitor.
- **No legend for fixed symbols and no zoom buttons.** Red square vs. red circle means
  producer vs. occurrence and nothing on the page currently says so.
- **No time slider on tenure.** Once history accumulates, this is the standout feature:
  scrub twelve months of staking activity across the basin.

## Automation and token cost, once live (2026-09-09)

This is where effort should go first - most open items in `open-items.md` trace back to one
root cause. **See the TOP PRIORITY section above - the specific, repeatedly-requested piece of
this (real repo write access so a fix doesn't need a manual upload every time) is now RESOLVED
as of 2026-09-14.** The rest of this section is still open backlog.

1. **The model should stop touching HTML directly.** Every recorded incident (dead `mkSel`
   references blanking the map, stripped `<script>` wrapper tags, swatch-colour drift, the
   SMDI label drifting three times in one night, repeated same-day publish collisions) comes
   from editing a 6-7 MB hand-authored page as text. Fix: separate template from data. The
   model emits structured JSON (rank, company, ticker, title, url, why, chips); a
   deterministic build script renders HTML from it. Removes this entire failure class and
   should cut per-run token cost by roughly an order of magnitude, since the model stops
   reading/rewriting a multi-MB document every edit.
2. **Move deterministic work out of the model's reasoning loop.** Quote fetching, claim
   diffing, date-window arithmetic, edition numbering, archive snapshotting, bundle merging
   are all deterministic and currently run inside an expensive model turn. The model should
   receive a small digest (candidate releases, registry delta) and return only rankings and
   prose.
3. **Keep the roster out of the prompt.** `watchlist-and-sources.md` is large and, if read
   every run, is likely the single biggest recurring token cost. Convert the roster to a CSV
   the sweep script filters against mechanically; only the ranking rules (already isolated to
   the skill, per the 2026-09-08 cleanup) need to reach the model.
4. **One page, not two.** Basin Watch and Basin Explorer are full duplicate 6+ MB bundles
   that must be patched identically and have documented drifting apart four times in one
   session. A public site only needs one map.
5. **Don't ship a 7+ MB page to the public.** Split the bundle: static layers (28k
   conductors, 4,800+ tenure polygons, lakes) as separately cached files fetched on demand,
   plus a small daily delta. First paint drops from ~7 MB to low hundreds of KB - matters a
   lot on phones and on camp bandwidth.
6. **Get the geoscience export off Ezra's personal laptop.** DONE 2026-09-11 - see below.
7. **One publisher, with a lock.** Documented collisions (nine-plus in one evening per
   `open-items.md`) happened because multiple sessions could publish concurrently. Once live,
   restrict to one publishing path.

**Item 6 detail, done 2026-09-11:** the data spine used to depend on a Windows scheduled task
on Ezra's own machine being awake at 07:30 local, and per `open-items.md` this was unconfirmed
working after two fix attempts, with folder binding silently failing on at least two recorded
runs. The only real blocker was the egress allowlist on `gis.saskatchewan.ca`/
`gis.energy.gov.ab.ca`. GitHub Actions has unrestricted egress, is free at this scale, and now
runs `basin_layers.py` on a cron and commits `exports/` to a repo (`gis-export.yml`) - this
removed the single point of failure and the folder-binding problem in one move.

## To review

- **Exploration Insights' "Intelligently AI" piece on evaluating drill results** (added
  2026-09-11) -
  https://explorationinsights.com/free-content/intelligently-ai-hi-evaluating-drill-results/,
  flagged by Ezra as a toolkit/framework investors use for reading drill results. Not yet
  reviewed against Basin Watch's own drill-result write-ups - check whether it suggests a
  metric or framing Basin Watch is missing (e.g. how it normalizes/contextualizes intercepts).

## One item outside the technical scope (2026-09-09)

Ezra is a P.Geo employed by Standard Uranium and is proposing to sell competitor analysis,
including price commentary, on companies that compete with his employer - including,
per the roster's own editorial-stance rule, Standard Uranium itself as a covered name. The
unbiased-coverage rule in `watchlist-and-sources.md` is the right instinct for the content,
but the separate question - being paid for research on direct competitors while holding a
professional designation with its own conduct obligations, and while employed by one of the
covered names - is worth raising with Standard Uranium and a securities lawyer before launch.
Not legal advice; flagging because it's the kind of decision that's expensive to unwind after
the fact. **This gets more pressing, not less, once real money changes hands** - see
Monetization below.

## Strategy notes (2026-09-09, still relevant, nothing acted on beyond what's noted)

### Naming

**Confirmed live at a registrar 2026-09-09 (instantdomainsearch.com, real-time availability,
not just a DNS/WHOIS check):**

| Candidate | .com | .ca | .io | Other checked |
|---|---|---|---|---|
| **basinwatch** | Taken | Available (now purchased) | Taken | - |
| **pitchblende** | Taken | Available | Taken | .net, .ai, .xyz, .studio, .media also taken |

**Recommendation (acted on): keep Basin Watch, register `basinwatch.ca`.** Already reads
correctly to all three audiences, has accumulated brand equity in this project, is honest
about what the product does, and `.ca` fits a Saskatchewan-specific product.

`pitchblende.ca` was still available as of the check and was not purchased - noted here in
case Ezra wants it later as a secondary/redirect domain. Availability can change at any time;
this is a point-in-time snapshot, not a hold.

**Sub-property naming decided:** Basin Explorer does not need (and should not get) its own
domain. It lives as a path or subdomain of `basinwatch.ca` - e.g. `basinwatch.ca/explorer`
or `explorer.basinwatch.ca` - configured via DNS/routing once hosting is set up, not via a
separate registration. No `basinexplorer.ca` purchase needed or recommended.

### Domain status

**`basinwatch.ca` purchased by Ezra, 2026-09-09.** Registrar and account details are his own
(purchase was guided, not performed by any session - domain purchases require payment
details no session enters). **Update 2026-09-10/11: since connected** - basinwatch.ca is
live on Cloudflare Pages, built from the `sockthief77/basin-watch` repo. See
`daily-publish-instructions.md` for the daily publish routine.

### Monetization strategy (2026-09-09)

Ezra ruled out ads. Proposed free trial + subscription; refined below.

**Trial:** 7 days, no card required to start, card required to continue. Matches the
product's own cadence (one edition cycle = enough to judge value) and removes the biggest
top-of-funnel killer for an unknown product.

**Tiering - price the data layer, not the newsletter layer.** The three named audiences have
very different willingness to pay; one flat price leaves money on the table with the
highest-value segment (institutional/corporate) while overpricing the largest-headcount,
lowest-budget one (retail):

| Tier | Audience | Includes | Rough price |
|---|---|---|---|
| Individual | Retail investors, individual geologists | Daily brief + Basin Explorer map, no export | $19-29/mo or ~$200-290/yr |
| Pro | Serious retail, institutional analysts, corporate BD | + GeoJSON/shapefile export, claim-change alerts, archive search | $99-149/mo |
| Enterprise | Companies, funds, consultancies | + multi-seat, API/data feed, priority support | Custom, likely $300-1,000+/mo/seat |

Comparable checked live: **CEO.ca Pro** (the platform this brief already sources from) runs
$50-116/mo for Level 2 market data and trading tools sold to the same retail micro-cap
audience - useful as a ceiling reference, though CEO.ca is a trading terminal, not a research
product, so not a direct comp on features.

The claim-staking-change alert and GeoJSON export are the actual moat (nothing else
automates this) and should justify most of the Individual-to-Pro price gap, not "more news."

Annual discount (~2 months free) standard, reduces churn.

**Real constraint: a Claude Artifact has no login, paywall, or billing hooks - it's a public
URL.** Monetizing requires moving the live site to real hosting with auth and a billing
provider (Stripe or Paddle) handling trial/recurring billing/cancellation. This is a
separate, larger project phase from anything built so far, not a bolt-on to the current
architecture - ties directly into the "automation and token cost" section above (one page,
off Ezra's laptop, deterministic build) since that rework has to happen before a paywall can
sit in front of it. **Update 2026-09-10/11: the "off Ezra's laptop" piece is now done (see
above); "one page" is still not done** - basinwatch.ca today is a static mirror of the
claude.ai page's content, not a rebuilt deterministic pipeline; see the Automation section
above.

### Competitive positioning vs. CEO.ca (2026-09-09)

Ezra asked how to make Basin Watch "a preferable competitor to ceo.ca." Pushed back on the
frame before answering: **they are not the same product**, and matching CEO.ca feature-for-
feature would be the wrong goal, not just a hard one.

**What CEO.ca actually sells:** real-time Level 2 market depth, a live trading chat
community across every TSXV/CSE ticker in every sector, and - confirmed live on their own
site 2026-09-09 - dedicated `#promotion`/`#promotions` sections plus paid private "Confidential
Investor Discussion" channels. It's trading infrastructure monetized partly through
sponsored/promotional content. Matching it means licensing real-time market data and
building a chat product, then taking the sponsored-content revenue Ezra already ruled out.

**The relevant asymmetry is already documented in this project**: `watchlist-and-sources.md`
records that ceo.ca is JavaScript-rendered and **cannot be automated** - Basin Watch's own
sweep gets a loading shell with no threads, tickers or activity counts. Basin Watch is not
positioned to out-build CEO.ca's infrastructure; it's positioned to make that infrastructure
less necessary for one narrow, high-value question.

**Where Basin Watch structurally wins, for its actual audience:**

- **Land tenure / claim-staking monitoring** - nothing on CEO.ca does this. Not adjacent to
  a trading terminal; it's exploration-stage due diligence, and a chat forum cannot replicate
  it. The single strongest differentiator in the whole product - worth leaning on harder than
  the news digest itself in any positioning/marketing.
- **Editorial judgment over chronological noise.** CEO.ca is a live feed the reader has to
  filter themselves. Basin Watch already ranks by technical materiality and names what a
  release doesn't say (cps-vs-assay, closeology, stale quotes) - the value is what it leaves
  out, not everything it includes.
- **No pump culture, by design** - a direct contrast with CEO.ca's promotional sections and
  private paid channels, which are structurally opposed to unbiased coverage since that's
  part of how CEO.ca monetizes. Only a real differentiator once the P.Geo/Standard Uranium
  conflict question above is actually resolved, not merely documented as a rule.
- **Built for someone with a day job**, not someone glued to a screen - corporate BD staff,
  institutional analysts, geologists. CEO.ca rewards live attention; that's its buyer, not
  Basin Watch's.

**Practical recommendation:** don't market as a "CEO.ca alternative" - that invites a
feature-by-feature comparison Basin Watch loses (no Level 2 data, no live chat, no broad
sector coverage). Position it as what a basin-focused reader checks *instead of* scrolling
CEO.ca's uranium threads each morning: one ranked digest plus the claim-monitoring layer
CEO.ca doesn't have at all. If the goal is specifically to pull CEO.ca's uranium-interested
users, the wedge is "we read the noise so you don't have to sit in it, and we watch ground
CEO.ca can't see" - not a broader trading-community pitch.

## Not yet done

As of 2026-09-14: the data/UI/automation review, the monetization plan, and the competitive
positioning above are still strategy only - no changes have been made to either live page,
the skill, or basinwatch.ca as a result of them, beyond the items marked "done" inline above
(geoscience export off the laptop; domain connected; masthead subtitle text corrected; **real
repo write access, resolved 2026-09-14**). **JV attribution shipped 2026-09-11** (see that
section above). None of "Ranked list and map churn," "Data gaps," "News-feed UI," or "Map UI"
have been built. Revisit this file before starting build work, and update or delete an item
here once it ships.
