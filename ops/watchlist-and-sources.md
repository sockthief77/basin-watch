# Uranium Brief - Watchlist and Sources

Reference for the daily uranium competitor brief.

## Editorial stance

**The brief is unbiased.** Rank on what a release reports, never on who reported it. No
operator is weighted for or against, Standard Uranium included, and no project or district
gets preferential placement or a proximity bonus. Geography is neutral fact, never a measure
of importance.

Coverage model: the roster below, **plus any new name** that stakes ground or issues
Saskatchewan or Alberta news. Add new names to the roster as they appear.

## Anonymity and voice - published content only (core rule, added 2026-09-11)

**The operator's name must never appear in anything published or in any code committed to a
public or live surface.** That means: the edition text (`edition_top_html`/`edition_bottom_html`
and their equivalent on the two claude.ai pages), any note box, any tooltip or hint string, and
**every code comment** in `site/shell.html`, the two claude.ai artifacts' `<style>`/`<script>`
blocks, and anything pushed to the `sockthief77/basin-watch` GitHub repo - comments included,
since `view-source` on a public page exposes them to anyone. This is a hard rule, not a style
preference: **"NEVER make anything published or in the code accessible by someone traceable
back to me."** Discovered and fixed 2026-09-11 after the live map's engine code (both claude.ai
pages, `site/shell.html`, and two frozen archive snapshots) had accumulated ~40 comments
attributing individual feature decisions to the operator by name ("Ezra's explicit request",
"Ezra asked for...", etc.), and a same-day edition note read "per Ezra's request." All of it
was scrubbed and republished the same day - see `daily-publish-instructions.md` for the
verification habit going forward. **This project's own docs (this file, `claim-monitor-state.md`,
`map-pipeline.md`, etc.) are exempt** - they're private working notes, never published, and
attributing a decision to "Ezra" in a project doc is fine and useful. The rule is specifically
about anything that ends up on a live page or in a committed file.

**Published prose reads as professional industry reporting, not as an AI narrating its own
process.** No methodology self-narration in anything a reader sees: not "a count derived from
two independently verified totals," not "confirmed by a direct diff of the full DISPOSIT_1
list," not "this figure required splitting the query into two single-bound queries - see the
run note for why." State the fact plainly (the number, the holder, the date) and stop -
pipeline mechanics, verification steps and query-splitting workarounds belong in the run notes
in `claim-monitor-state.md`, never on the page itself. Also discovered and fixed 2026-09-11,
same pass as the anonymity fix above, same root cause: editorial notes drafted the way an
internal engineering note would be drafted, not the way a subscriber-facing brief should read.

**Practical check before any edition or code change goes live:** if a sentence names who asked
for a feature, describes how a number was verified or computed, or reads like a commit message
rather than a news item, it doesn't belong in the published output - cut it or move it to a
project doc.

**Canadian spelling throughout (added 2026-09-11, Ezra's explicit correction).** The product
is Saskatchewan-specific and should read that way. Concretely, that means Canadian `-ize`
endings, not British `-ise`: **mobilized**, not mobilised; **localized**, not localised;
organized, recognized, finalized, and so on follow the same pattern. Keep the British/Canadian
forms Canadian English does use elsewhere (colour, favour, centre, cheque) - this rule is
specifically about the `-ize`/`-ise` choice, not a wholesale switch to American spelling.
Caught and fixed 2026-09-11 in that day's edition text ("mobilised" -> "mobilized",
"localised" -> "localized") on both claude.ai pages and basinwatch.ca. Check for this the same
way as the anonymity/voice check above before anything goes live.

## Ranking rules - live in the skill, not here (changed 2026-09-08)

The weighted 100-point scheme used to be written out in full in this doc **and** in
`uranium-brief`'s SKILL.md. Two copies of the same rules is exactly what caused the
scheduled task's prompt to drift out of agreement with these docs, so the copy here is gone
deliberately.

**The scheme lives in the skill, Step 3, and that is the only copy.** Summary for orientation
only, not for scoring from: nine ranked tiers competing for position (resource estimates and
economic studies 25, assayed grade 17, permitting and regulatory 13, gamma-derived grade 11,
corporate and financing 11, geophysical target definition 9, Indigenous agreements 6,
programs 5, filings 4), plus three modifiers that attach to a tiered item rather than
competing on their own (cash runway, insider activity, drill hit-rate).

**Majors clarification (2026-09-11, the operator's explicit correction - the skill's Step 3 text
is wrong/incomplete and needs fixing the next time someone can edit it):** the skill currently
reads that major-producer news is "never forced through the numbered ranking." That is not
the rule. **The correct rule, stated directly: "I DO want majors on the numbered
list" / "a majors item may still take a numbered slot when it's clearly the week's most
material release."** So majors are NOT automatically excluded from the numbered list - a
major's release competes for a slot by ordinary editorial judgment of materiality (the same
judgment call used to order items within a tier), same as it did in Edition 001 when
IsoEnergy's 26-hole/10,159 m Larocque East program landed at #2, ahead of items with a higher
raw tier score. What majors don't get is automatic exclusion, and they also don't automatically
compete on the 9-tier point scale the way junior-roster items do (their news is often cps-only,
not assayed, which would score artificially low on that scale) - so a major's placement is a
judgment call about real-world materiality, not a tier-point calculation. **2026-09-11's
Edition 002 briefly moved IsoEnergy and CanAlaska out of the numbered list into the majors
note, following the skill's literal (wrong) text - caught within the hour and corrected the
same day, IsoEnergy restored to its ranked slot.** Don't repeat that mistake:
until the skill's own Step 3 text is fixed, treat this doc's wording above as the actual rule,
not the skill's.

First applied to a live edition 2026-09-08. The permitting and Indigenous-agreement tiers
immediately produced content the brief had been missing. **If the weights need changing,
change them in the skill and leave this section as a pointer.**

## The roster - one table, 2026-09-08

**Consolidated from three separate tables the same day.** The roster previously sat in a main
juniors list, an "added by the roster audit" list, and an ASX list, which meant a run building
its sweep from the main table alone missed a third of the coverage universe with no visible
symptom. One table now. Keep it that way; add new names here rather than in a new section.

### Majors and producers

Their own coverage lane for the "quiet week" / majors-context writeup, **but not excluded from
the numbered ranking** - see the "Majors clarification" note above. A major's release still
gets a numbered slot when it's the week's most material item by ordinary editorial judgment.

| Company | Ticker | Saskatchewan assets |
|---|---|---|
| Cameco | TSX:CCO | McArthur River, Cigar Lake, Key Lake, Rabbit Lake |
| Orano Canada | private (Orano SA) | McClean Lake mill, Cigar Lake JV, McClean Lake JV. Also Alberta - see below |
| Denison Mines | TSX:DML | Wheeler River (Phoenix, Gryphon), Waterbury |
| NexGen Energy | TSX:NXE | Rook I / Arrow |
| Paladin Energy | TSX:PDN / ASX:PDN | Patterson Lake South (Triple R, Atlas, Saloon). ASX-listed, PDF caveat applies |
| IsoEnergy | TSX:ISO | Larocque East (Hurricane, Hurricane South) |
| Uranium Energy Corp | NYSE:UEC | Roughrider |
| CanAlaska Uranium | TSXV:CVV | West McArthur JV (with Cameco), Cree East, Key Extension - grouped with the majors per operator instruction 2026-09-07 |

**CanAlaska's grouping changes where it is listed, not how it is scored.** Its news still
ranks alongside every other operator's on release substance. What it changes is the majors
check and the "quiet week" note: CanAlaska activity belongs in that context rather than
implied to be a small junior's move.

### Juniors and explorers

Alphabetical. `?` in the last column means the entry rests on a possibly dated release and the
detail is unverified - confirm against a current release before reporting from it.

| Company | Ticker | Projects | |
|---|---|---|---|
| Abasca Resources | TSXV:ABA | basin properties | |
| Aero Energy (was Angold Resources) | TSXV:AERO | Sun Dog earn-in | |
| Americas Uranium (was Allied Strategic) | CSE:NUCA | Ford Lake - TDEM/gravity structural work 2026 | |
| Apogee Minerals | TSXV:APMI | Shasko Bay (U), Pine Channel - Eagle Plains partner | |
| Appia Rare Earths & Uranium | CSE:API | Alces Lake | |
| ATHA Energy | TSXV:SASK | Gemini, large basin package. Also Alberta, and Angilak in Nunavut (out of basin) | |
| Atomic Minerals | TSXV:ATOM | **Mozzie Lake only** - stated by the company as immediately northeast of the basin, not within it. Bleasdell Lake, Pistol Lake and Baby Loon are no longer listed. Focus is now the Colorado Plateau and Quebec. See the currency check below | ? |
| Aventis Energy | CSE:AVE | Corvo earn-in | |
| Azincourt Energy | TSXV:AAZ | East Preston JV | |
| Basin Energy | ASX:BSN | Geikie | ASX |
| Bedford Metals | TSXV:BFM | basin properties | |
| Belmont Resources | TSXV:BEA | Crackingstone U-REE - drill permit received | |
| Blast Resources | CSE:BLST | Wales Lake (flagship), Britts Lake | |
| Canadian Uranium | CSE:CANU | King South | |
| Collective Metals | CSE:COMT | Rocas earn-in | |
| Cosa Resources | TSXV:COSA | Ursa, Cypress | |
| Eagle Plains Resources | TSXV:EPL | Lorado (Xcite partner), Dufferin (Refined partner) | |
| F3 Uranium | TSXV:FUU | Patterson Lake North, Minto, Broach | |
| F4 Uranium | TSXV:FFU | Wales Lake. Renamed Fission 3.0 - ticker history is truncated | |
| Foremost Clean Energy | CSE:FAT | multiple basin properties | |
| Forum Energy Metals | TSXV:FMC | Northwest Athabasca JV | |
| Fortune Bay | TSXV:FOR | Murmac, Strike (Manhattan operates) | |
| Future Fuels | TSXV:FTUR | Hatchet Lake (flagship), Highway, CBX/Shoe, Usam, Genie - ~97,674 ha from the May 2026 Hatchet acquisition | |
| Geiger Energy (was Baselode Energy) | TSXV:BEEP | Hook / ACKIO, Aberdeen. **Renamed with a share consolidation; TSXV:FIND is a dead ticker** | |
| Global Energy Metals | TSXV:GEMC | **Not an operator.** Holds a 0.5% NSR royalty across Terra North Resources' Saskatchewan uranium portfolio, including Charlot-Neely Lake. Added 2026-09-08 after it issued the release naming seven radiometric anomalies at Charlot-Neely Lake; Terra North itself is private and already on this roster | |
| Global Uranium | CSE:GURN | basin properties | |
| Green Canada Uranium | TSXV:GCUC | **Added 2026-09-08.** Marshall project (11,225 ha), held via a 51% option into North Millennium's underlying interest, ~30 km SW of CanAlaska's West McArthur Pike Zone. Formed by a reverse takeover of PTX Metals' shell (closed 1 Sep 2026); began trading 9 Sep 2026, the same day it mobilized a rig for a 2-hole maiden program - see the 2026-09-09 edition | |
| Greenridge Exploration | CSE:GXP | basin properties | |
| Kiplin Metals | TSXV:KIP | basin properties | |
| Lancaster Resources | CSE:LCR | **Catley Lake (3,036 ha) and Centennial East (5,081 ha), 100%**, ~24 km northeast of Cameco's Dufferin deposit. See the closeology warning in the currency check below | |
| Mamba Exploration | ASX:M24 | Canary | ASX |
| Manhattan Uranium Discovery | TSXV:MANU | Murmac, Strike - JV/earn-in with Fortune Bay, and **operator** of the June 2026 25-30 hole program | |
| Marvel Discovery | TSXV:MARV | KLR / Key Lake Road, Wollaston-Mudjatic domain contact, eastern basin. Also Walker. Last SK uranium results are **May 2023** | ? |
| Mustang Energy | CSE:MEC | basin properties | |
| Nexus Uranium | CSE:NEXU | basin properties | |
| North Shore Uranium | TSXV:NSU | Falcon, West Bear. Also Rio Puerco, New Mexico (out of basin) | |
| Patterson Metals | TSXV:PAT | Carter Lake, Pendleton Lake | |
| Purecore Metals | CSE:PURE | basin properties | |
| Purepoint Uranium | TSXV:PTU | Hook Lake JV, Dorado JV | |
| Radiant Uranium | CSE:RUC | Gorilla Lake (Carswell structure, near Cluff Lake), Key Lake Road | |
| Recharge Metals | ASX:REC | Newnham Lake | ASX |
| Refined Energy | CSE:RUU | Dufferin West, Dufferin North (with Eagle Plains) - maiden drill program Apr 2026, intersected the unconformity | |
| Searchlight Resources | TSXV:SCLT | Athabasca staking; already appears in the tenure registry as a holder | |
| Sienna Resources | TSXV:SIEN | Dragon Uranium, Atomic Uranium (50,440 ac), Uranium Town - ground bordering Cameco | |
| Skyharbour Resources | TSXV:SYH | Moore, Russell Lake (Denison JV), Preston | |
| Stallion Uranium | TSXV:STUD | Moonlite / Stone Island | |
| Standard Uranium | TSXV:STND | Davidson River, Corvo, Rocas, Sun Dog | |
| Terra Clean Energy | CSE:TCEC | South Falcon | |
| Terra North Resources | private (39.5% Terra Balcanica, CSE:TERA) | Charlot-Neely Lake, 20 km N of Uranium City. Global Energy Metals (TSXV:GEMC) holds a 0.5% NSR royalty across the portfolio - see that entry | |
| Traction Uranium | CSE:TRAC | basin properties | |
| Trinex Minerals | ASX:TX3 | Gibbons Creek | ASX |
| Uranium One Mining | CSE:UUU | **Pasfield Lake** (~4,400 ha prospecting permit, ~60 km NW of Cigar Lake, acquired 26 Jun 2026) **and the Nucleon Uranium Project**, stated as Athabasca Basin. Foghorn is BC; Quark's location is unstated | |
| UraniumX Discovery | CSE:STMN | Murphy Lake, 5 km from IsoEnergy's Hurricane | |
| Xcite Uranium | CSE:XRI | Lorado (Eagle Plains partner) | |

### Currency check on the three flagged entries (2026-09-08)

All three carried a `?` because they rested on possibly dated releases. Checked directly.

**Atomic Minerals (TSXV:ATOM) - the entry was wrong, not just stale.** The roster said
Bleasdell Lake, Pistol Lake and Baby Loon. The company's own site now lists its Canadian
portfolio as **Mozzie Lake (Saskatchewan) and Mont-Laurier (Quebec)** only, with the US
portfolio (10 Mile, Harts Point, South Lisbon Valley East, Delores Anticline) on the Colorado
Plateau. The three named properties do not appear.

The trail: a **23 December 2024** release confirms Atomic then held four claims totalling
2,180 ha across Bleasdell Lake, Pistol Lake and Baby Loon, having **returned Carswell, Parks
Lake and Archie Lake to the vendors**, with an exploration permit application filed 9 October
2024 for Bleasdell Lake (historic resource 620,700 lb U3O8, 1957) and consultation underway
with Peter Ballantyne Cree Nation. So the change happened after December 2024.

Two things to carry: **Mozzie Lake is stated by the company as "immediately northeast of the
prolific Athabasca Basin" - adjacent, not within**, which is the same footing as Fortune Bay's
Murmac and Terra North's Charlot-Neely, both of which are on this roster; and **"no longer
shown on the website" is not the same as "divested"**, so the `?` stays until a release
confirms what happened to Bleasdell, Pistol and Baby Loon.
([Newsfile, 23 Dec 2024](https://www.newsfilecorp.com/release/234915/Atomic-Minerals-Provides-Update-on-Properties-in-the-Athabasca-Basin-and-Northern-Saskatchewan),
[atomicminerals.ca](https://www.atomicminerals.ca/))

**Lancaster Resources (CSE:LCR) - upgraded from "thin detail" to specific, `?` removed.**
It holds **100% of Catley Lake (3,036 ha) and Centennial East (5,081 ha)**, confirmed in a
22 July 2025 release. Cameco's Dufferin deposit is ~24 km southwest of the claims.

**Closeology warning, carry this into any ranked Lancaster item.** The company's own property
page presents *"assays up to 8.78% U3O8 over 33.9m"* and concentrations *"up to 25.6%"* in the
same breath as Centennial East. **Those are historical results from the Centennial deposit
area, not Lancaster's drilling on its own ground.** Never attribute them to Lancaster, and
never chip them.

Also worth knowing about this issuer: the 22 July 2025 release was a **clarification issued at
the request of the CSE and CIRO**, correcting how a separate Quebec property (Lac Iris) had
been described - acquired by online staking with titles still pending provincial review, not a
completed acquisition. Not a uranium matter, but it establishes that this issuer's disclosure
has been formally corrected once.
([GlobeNewswire, 22 Jul 2025](https://www.globenewswire.com/news-release/2025/07/22/3119904/0/en/Lancaster-Resources-Clarifies-News-Release.html),
[lancaster-resources.com](https://lancaster-resources.com/properties/catley-lake-centennial-east/))

**Marvel Discovery (TSXV:MARV) - confirmed stale, `?` stays, but now precisely dated.** The
KLR result the entry rested on is **17 May 2023**, and it is real: SRC core assays of
**841 ppm U3O8 over 1.07 m** and **512 ppm over 2.93 m** (KLR23-06, DD Zone), **201 ppm over
2.32 m** (KLR23-05), **553 ppm over 1.89 m** (KLR23-02, Highway Zone), with downhole gamma
(QL40-GRA probe) peaking at 11,500 cps. For scale, 841 ppm is 0.084% U3O8 - two orders of
magnitude below basin discovery grades, so this is a mineralized-system indication, not an
economic intersection.

No Saskatchewan uranium news from Marvel was found for 2025 or 2026; the property acquisition
and airborne-survey items all date to 2021-2022, and the company's news page returns a 404.
**Do not report the 2023 numbers as current.**
([INN, 17 May 2023](https://investingnews.com/marvel-intersects-significant-radioactive-zones-at-klr-uranium-project-saskatchewan/))

### Alberta basin

Listed separately **only because the claims data source differs**, not because these are
weighted or ranked differently. Alberta holds tenure as metallic and industrial minerals
agreements on its own ArcGIS registry
(`gis.energy.gov.ab.ca/arcgis/rest/services/wms/SREM_Metallic/MapServer`), not on
MARS/GeoAtlas.

| Company | Ticker | Alberta project |
|---|---|---|
| GoldMining Inc. | TSX:GOLD / NYSE American:GLDG | Rea - 125,328 ha, 75% (Orano Canada 25%), surrounds Orano's Dragon Lake. Three corridors totalling >70 km; approval for up to 15 holes and 7,500 m |
| Orano Canada | private (Orano SA) | Rea (25%) - **registered as designated representative for the whole agreement**, so Rea shows under Orano's name on the Alberta registry, not GoldMining's. Only 3 agreements, which is the whole of Rea |
| ATHA Energy | TSXV:SASK | 41 agreements, the largest Alberta holding on the roster |

**Now on the map** (2026-09-08). `basin_layers.py` section 11 pulls the layer and both pages
carry an `Alberta Tenure` layer. 74 agreements survive the basin window; see `open-items.md`
for the 58N cut and why a 55.5N floor pulled in 142 Hammerstone limestone leases around Fort
McMurray.

**No registration date on this layer** (only TermDate/expiry), so new Alberta staking cannot
be watermark-detected. Change detection is a set diff on `AgreementNumber` between runs, into
`exports/ab_state.json`.

**Two holders worth watching:** a numbered company (1818403 Alberta Ltd., 16 agreements) and a
staking consultancy (Dahrouge Geological Consulting, 6) hold 22 between them adjacent to
ATHA's 41. That is the Alberta equivalent of the individual-staker pattern.

### Checked and deliberately excluded

- **ValOre Metals (TSXV:VO)** - sold Hatchet to Future Fuels and Angilak to Labrador Uranium;
  now Brazil PGM focused. No SK ground.
- **Generation Uranium (CSE:GEN)** - flagship Yath is Nunavut.
- **Uranium Royalty (NASDAQ:UROY)** - royalty holder, not an explorer.
- **Frontier Nuclear and Minerals (Nasdaq:FNUC)** - formerly Snow Lake Resources, renamed
  March 2026. Pine Ridge (Wyoming), Engo Valley (Namibia), Shatford Lake and Snow Lake Lithium
  (Manitoba), Tallahassee (Colorado). No Saskatchewan ground. **Settled, do not re-check.**
- **Uranium One Inc.** - the famous one, and it does not belong. Founded 1997 as Southern Cross
  Resources, became SXR Uranium One (ticker UUU), taken over in stages by Rosatom's ARMZ and
  **delisted from both exchanges in October 2013**. Now a wholly owned Rosatom subsidiary
  holding principally Kazakh ISR joint ventures. No Saskatchewan or Athabasca assets, ever;
  not listed, no release feed. **Unrelated to Uranium One Mining Corp. (CSE:UUU) in the roster
  above, despite the near-identical name and the reused ticker.** Searching "Uranium One"
  returns overwhelmingly Rosatom and US-politics material, which is why the CSE company never
  surfaced in roster-building. Carry this caveat forward.
- A tail of names on JMN's Athabasca stock screen (Maverick, Gold'n Futures, Canadian
  GoldCamps, Aurwest, Bayridge, New Earth, Dark Star, Spartacus, Inspiration) where active SK
  uranium ground was **not** confirmed. That screen is loose and includes gold names with
  basin-region claims. GoldMining is no longer on this list - Alberta scope moved it into the
  roster.

## Advanced projects tracked for feasibility-study milestones

Check each edition for a technical-report, PEA, PFS or FS filing or update, not just drill
results. Any other roster project that announces one belongs in this table going forward.

| Project | Operator | Stage |
|---|---|---|
| Arrow | NexGen Energy | Feasibility Study complete; watch updates and permitting milestones |
| Rook I | NexGen Energy | Same project area as Arrow; licensing / construction-readiness news |
| Wheeler River (Phoenix, Gryphon) | Denison Mines | Feasibility Study complete; watch updates |
| Triple R (Patterson Lake South) | Paladin Energy | Post-acquisition studies; watch for PFS/FS updates |
| Roughrider | Uranium Energy Corp | **PFS in progress, not yet released** - see below |

### Roughrider PFS status

It is not missing from the news, it has not been published. November 2024: UEC completed an
**Initial Economic Assessment** (IEA/PEA) - post-tax NPV8 $946M, 40% IRR, 61.2M lb U3O8 over
9 years - and said it would pursue an updated resource estimate to support a PFS. UEC's Q3
FY2026 release (2026-06-09), the most recent found, says core drilling was "over 80% complete
to support a planned pre-feasibility study" with Tetra Tech engaged, and **gives no completion
or release date**. Nothing found between June and September 2026.

**Do not report a PFS as complete until an actual PFS, not the 2024 IEA/PEA, is announced.**
UEC's fiscal year ends 31 July, so full-year results around October are the next scheduled
opening. ([Resource World](https://resourceworld.com/uranium-energy-completes-initial-economic-assessment-for-roughrider-uranium-project-saskatchewan/),
[PR Newswire](https://www.prnewswire.com/news-releases/uranium-energy-corp-reports-results-for-the-third-quarter-of-fiscal-2026-302794776.html))

## Sources

The skill's Step 2 is the operative sweep order. This section carries the detail behind each
source and the findings that settled which ones are usable.

### Press-release aggregators - the primary sweep

- **Junior Mining Network, all three topic pages, every edition, not optional**: Athabasca
  Basin, Saskatchewan, uranium. `https://www.juniorminingnetwork.com/mining-topics/topic/athabasca-basin.html`
  The basin tag has twice missed a roster operator's release that the uranium tag carried
  (North Shore's Rio Puerco, edition 002; ATHA's Rib North, 8 Sep). The headline list can be
  date-filtered directly, but article URLs need a second WebFetch asking for hrefs.
- **TMX Newsfile, Mining & Metals** - `https://www.newsfilecorp.com/news/mining-metals`.
  **Highest-value source added 2026-09-08.** The wire most small basin juniors actually
  distribute on - Geiger, Manhattan, Atomic, Blast, Radiant, Searchlight. JMN reposts
  selectively and with lag; this is the origin. Static, same-day dated.
- **Cision/newswire.ca, Mining & Metals list - mandatory, every run, added 2026-09-13.**
  `https://www.newswire.ca/news-releases/heavy-industry-manufacturing-latest-news/mining-metals-list/`.
  **Evidence-based addition, not speculative**: a same-day test run against the live 2026-09-13
  edition caught Nexus Uranium Corp. (CSE:NEXU) trading-halt news (10 Sep 2026) that steps
  1-4 of the sweep had missed entirely - a real roster-relevant item, not a hypothetical gap.
  Static HTML, dated entries, one cheap fetch. Add as sweep step 3, ahead of the GlobeNewswire
  RSS pull below (renumber accordingly).
- **ACCESS Newswire, Metals & Mining category - mandatory, every run, added 2026-09-13.**
  `https://www.accessnewswire.com/newsroom/industry/metals-and-mining`. Structurally usable
  (static, dated pages, no JS-rendering block). The 2026-09-13 test found nothing new that day,
  but it's zero marginal cost, covers a distributor Eagle Plains and others use, and the point
  is coverage breadth, not a hit every run. Run alongside newswire.ca.
- **GlobeNewswire mining RSS** -
  `https://www.globenewswire.com/RssFeed/subjectcode/17-Mining/feedTitle/GlobeNewswire-Mining`.
  Future Fuels, Refined Energy, Apogee, Terra Balcanica, Lancaster. The subject filter leaks
  non-mining items; keyword-filter on uranium/Athabasca/Saskatchewan.
- **Investing News Network** uranium vertical - running company-by-company list.
- **CSE per-listing pages** - `https://thecse.com/listings/<company>/`. The roster is
  CSE-heavy. There is no global CSE news index; `thecse.com/news/` is a 404.
- **TSXV daily bulletins** - published in full to PR Newswire / newswire.ca as "TSX Venture
  Exchange Daily Bulletins". Static HTML, complete text, includes name changes and
  consolidations. URLs carry opaque numeric ids, so find them by search each run.
- **JMN Athabasca Basin stock screen** -
  `https://www.juniorminingnetwork.com/mining-stocks/athabasca-basin-mining-stocks.html`,
  69 companies. **Roster maintenance, monthly, not news.** This is what surfaced Geiger,
  Manhattan, Future Fuels, Radiant and UraniumX.

### Permitting, regulatory and community - mandatory every run, not occasional (reaffirmed 2026-09-13)

These three were already listed below as part of the sweep but had not been explicitly flagged
as non-optional; a 2026-09-13 coverage review found no evidence they'd been skipped, but
flagging them removes the ambiguity going forward. **Run all three every edition, same as the
aggregator steps above** - they're the only sources on this list carrying permitting,
licensing and Indigenous-agreement news, none of which any aggregator reports promptly.

- **Saskatchewan Environmental Assessment projects** -
  `https://www.saskatchewan.ca/business/environmental-protection-and-sustainability/environmental-assessment/environmental-assessment-projects`.
  Static dated activity log; carries ministerial approvals and licence decisions. **This
  closes the old "no confirmed permit/EA registry" open item - confirmed fetchable and used
  2026-09-08.** Nothing published there since 29 July as of that check.
- **CNSC uranium mines and mills** - `https://www.cnsc-ccsn.gc.ca/eng/uranium/mines-and-mills/`.
  Federal licensing milestones, hearing dates, licence amendments, which no aggregator
  reports promptly.
- **WISE Uranium, new Saskatchewan projects** - `https://www.wise-uranium.org/upcdnsk.html`.
  Curated chronological log of CNSC licences, EIS approvals, **Mutual Benefit Agreements** and
  PEA results. The only source on this list carrying Indigenous-agreement news; on 2026-09-08
  it carried three items nothing else on the sweep reported. Non-promotional.

### Editorial

- **Mining.com** for development-stage stories. **World Nuclear News** and **NucNet** for
  fuel-cycle and utility contracting, which drives exploration budgets.
- **The Northern Miner is paywalled** - a fetch returns the lede and a limit notice.
  Headlines only; never quote it as reporting.

### Primary sources

- Company release feeds directly, when an aggregator carries only a stub. **A company's own
  site is also how a roster entry goes quietly wrong**: Atomic's property list changed with no
  release the sweep would have caught. Worth a periodic pass over the sites of names that have
  gone quiet - see "Quiet-company rotation" below for how this is now scheduled rather than ad
  hoc.
- **Saskatchewan Mineral Assessment Database (SMAD)** - real ArcGIS REST endpoint, queryable,
  but reports sit under ~2 years of confidentiality, so it is a research source rather than a
  daily one. See `claim-monitor-state.md`.
- **MARS and the GIS disposition layers** for claim staking - more current than any news site.
  See `claim-monitor-state.md` for the query recipes.

### Quiet-company rotation (added 2026-09-13)

**The problem this solves:** full company-by-company scraping of all ~68 roster companies'
own "News Release" pages was considered and rejected 2026-09-13 - too costly (60-70 extra
fetches/day on top of a sweep that already hits Google Finance rate limits on far fewer calls),
mostly redundant with wire-service distribution (every company on the roster distributes
through JMN, TMX Newsfile, GlobeNewswire, newswire.ca or ACCESS Newswire - that's the whole
point of a wire distributor), and partly blocked outright by JS-rendered company sites, the
same failure mode that killed ceo.ca. The real failure mode isn't "the wire missed a release" -
it's a roster entry going quietly stale with **no release at all** (the Atomic Minerals property
list is the standing example: the change was never announced, only visible by checking the
site directly).

**The fix: a rotating spot-check, not a full daily scrape.** Roughly 10 roster companies per
run, cycling through the ~68-company roster (majors and producers excluded - they're
covered separately and don't go quiet the same way) so the full roster gets checked once every
6-7 runs (roughly weekly). Rotation order follows the roster table's existing alphabetical
order, 10 names per day, wrapping around. Check each company's **wire-distributor issuer
profile page** (its per-company page on newswire.ca, TMX Newsfile or GlobeNewswire, whichever
it distributes through) rather than its own corporate site - this sidesteps the JS-rendering
problem that makes company sites and ceo.ca unreliable for unattended fetching, while still
surfacing anything genuinely new. Log which 10 were checked and what (if anything) was found in
the run note in `claim-monitor-state.md`; nothing found is a normal, expected result most days.

**Not yet built**: the actual rotation tracker (which day starts at which roster position).
Until one exists, pick the next 10 alphabetically after wherever the previous run's log says it
stopped; if no prior rotation note exists, start from the top of the roster table.

### Blocked or unusable - settled, do not retry in an unattended run

- **ceo.ca** - JavaScript-rendered; WebFetch returns a loading shell with no threads, tickers
  or activity counts. No forum-activity signal is buildable unattended. A one-off check of a
  specific ticker's thread is possible through the interactive browser while the operator is
  present.
- **SEDAR+** - search page redirects to a PerimeterX/ShieldSquare challenge; no public API.
  Financings and private placements come from the aggregator sweep instead.
- **SEDI** - same block. **The insider-activity modifier cannot be automated.** Manual-only.
- **GeoAtlas** - a viewer over the same ArcGIS services already queried directly. Nothing to
  scrape.
- **PR Newswire's mining-metals list page** - tested 2026-09-13, content served 3-4 weeks
  stale on two fetches (one with a cache-busting query parameter), so this is server-side/CDN
  caching on PR Newswire's end. Do not add; see the Press-release aggregators section above for
  the two wire-distributor sources that were tested and did work.
- **TheNewswire.com** - identified but still not feed-tested; no finding either way yet.

### Paid-promotion caveat

**Proactive Investors, Streetwise Reports and Canadian Mining Report publish sponsored
coverage of the companies they write about.** Usable only to confirm a release exists. Never
for assessment. If one is the only source for a figure, mark the figure unverified in the item
text - **do not add a standing caveat to the page**, which has no method footer any more.

### Disclosure caveats to carry into every edition

- `eU3O8` from calibrated downhole gamma is not a chemical assay. Always say which it is.
- Handheld spectrometer counts-per-second on core are neither an assay nor calibrated gamma,
  and do not convert to a percentage. Say so.
- "Composite" mineralization is not a continuous interval.
- **Neighbouring-property grades are not the issuer's own.** Lancaster's property page is the
  worked example (see the currency check above). Check whose drilling produced a number before
  chipping it.
- ASX-listed names publish PDF announcements the fetch tools cannot parse; figures taken from
  secondary reporting must be marked unverified.

## Price and market context

**U3O8 ticker.** The masthead carries a red-outlined spot-price ticker: industry-average spot
(TradeTech/UxC via Cameco's published price table,
`https://www.cameco.com/invest/markets/uranium-price`), converted to CA$/lb via the Bank of
Canada FX API. Refreshed by the daily run as plain text, not a `BASIN_BUNDLE` key.

**It is a month-end figure** - print the month it belongs to. If the run cannot reach Cameco's
table, leave the previous value with its own date rather than restating a stale month as
current.

The Sprott Physical Uranium Trust (U.UN-CA / SRUUF) unit price is a **fund** price, not the
$/lb benchmark, and is **not** what this ticker shows. Sprott's Uranium Watch commentary is
useful reading. The Sprott quote remains a valid fallback mechanism only if Cameco's page
becomes unreachable and a $/lb figure is found nowhere else - and it would need labelling as a
different thing.

### Share-price cells on the news items

Each ranked item carries last price with currency and exchange, day change, and the **52-week**
range. **Added 2026-09-09: also volume (today's vs. trailing average) and market cap with
shares outstanding**, per the operator's request to fill the empty space that opened up in the
price card next to a long why-it-matters paragraph. Same card, two more lines.

**Why 52-week and not all-time.** All-time figures for these names are mostly artifacts.
Verified: Canadian Uranium's reported all-time high is CA$120.00 against a ~CA$1.18 price;
Skyharbour's is CA$70.00 from a March 2000 dot-com predecessor shell, about 143x today;
Stallion's CA$8.25 is roughly 59x. These are predecessor-entity and consolidation residue, not
prices the company ever traded at. F4's series is self-contradictory - a reported all-time high
*below* its own 52-week high, because FFU is the renamed Fission 3.0 and the ticker history is
truncated. Comparability is also unconfirmed for IsoEnergy, CanAlaska and Denison. Only Cameco,
NexGen, UEC and Xcite have all-time figures worth printing. Publishing a "record high" that is
a shell artifact on a page headed for public release would be a plain factual error.

**Data source and the trap in it.** Google Finance with `?hl=en&gl=us` appended. Without that
cache-buster it serves snapshots weeks stale that look completely plausible - a first pass
returned Stallion at CA$0.36, an April snapshot, against a true CA$0.14.

**Google Finance ticker-suffix format, confirmed 2026-09-09 (previously undocumented, found by
trial):** `TICKER:TSE` for TSX-listed names - **not** `:TSX`, which 404s. TSX Venture is
`:CVE` - **not** `:TSXV`. CSE is `:CNSX` - **not** `:CSE`. Example URLs that work:
`google.com/finance/quote/ISO:TSE?hl=en&gl=us`, `google.com/finance/quote/STUD:CVE?hl=en&gl=us`,
`google.com/finance/quote/TCEC:CNSX?hl=en&gl=us`. NYSE/ASX/Nasdaq-listed roster names haven't
been tested against this endpoint yet - confirm the suffix before trusting a quote for one of
those.

**Hard rule, in the skill's Step 4: every refreshed quote must carry a returned as-of date, and
that date must equal the run date. If it does not, or none comes back, print a dash rather than
a number.** A confidently wrong price is worse than no price. **Applied for the first time
2026-09-08 (evening run): Global Energy Metals' Google Finance quote carried an Aug 27 as-of
date against a Sep 8 run - dropped, printed as a dash rather than the stale CA$0.02.** **Still
happening 2026-09-11 - GEMC's quote again came back dated Aug 27, three weeks stale - GEMC's
Google Finance quote has now gone stale on at least two separate occasions, not a one-off.**

**Same freshness rule applies to Volume specifically** - it's a day-specific figure, same as
price. Avg. Volume, Market Cap and Shares Outstanding are trailing/structural figures (a
rolling average, and a share count that rarely moves day to day) so they don't need the same
same-day-as-of-date test; source them from the same fresh Google Finance fetch used for price
when convenient, but a slightly older shares-outstanding figure isn't the same defect as a
stale price or volume number. When a ticker has no usable price (freshness check failed, or no
listing found - GEMC, GCUC on 2026-09-09), print a dash for all four new-line fields too rather
than a mix of numbers and dashes.

**Format used 2026-09-09:** `VOL  154.8K / 210.4K avg` and `MKT CAP  $1.07B · 65.3M sh` (omit
the share count when Google Finance doesn't return Shares Outstanding for that ticker, e.g.
TCEC and CANU that day - print the market cap alone rather than guessing a share count).

TMX Money, Barchart and stockanalysis.com are blocked by the egress proxy for direct code
execution, but **reachable through WebFetch** (WebFetch goes through a separate proxy - see the
skill's Network constraint section). Confirmed 2026-09-09: stockanalysis.com's quote and
`/history/` pages return real data but are **consistently 2-3 weeks stale** on every ticker
checked (a free-tier delay, not a fetch fluke) - fine for a static fact like shares outstanding,
useless for anything that needs to be current, including a price-trend sparkline (considered
and dropped for that reason 2026-09-09 - see `claude/history.md`). Yahoo and stooq's historical
endpoints are blocked outright by WebFetch's own robots.txt check, not the egress proxy - don't
retry those. Yahoo's live quote page served stale before. TradingView is the only source found
for all-time figures. Quotes are intraday, not closes.

**WebFetch rate limiting observed 2026-09-11**: several back-to-back Google Finance quote
fetches in the same run hit `PROXY_REJECTED` (HTTP 429, "waiting ~60s before retrying"). Space
out price-card fetches or expect to retry after a short wait - don't treat a 429 as the ticker
being unreachable.
