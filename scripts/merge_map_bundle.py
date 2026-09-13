#!/usr/bin/env python3
"""
Merge gis/exports/map_bundle.json (fresh output of basin_layers.py) into
data/bundle.json (the bundle the site actually builds from).

Run after gis/basin_layers.py, before committing. Replaces every key
basin_layers.py produces - tenure, claims, deposits, mines, places, highways,
footprints, lakes, boulder_grid, boulder_total, geochem_grid, geochem_total,
conductors, lapsed, ab_tenure, restricted, smdi - with the freshly pulled
version, subject to the guards below. ("claims" added 2026-09-12 - see
incident 3 below for why it's guarded differently from everything else here.)

Deliberately leaves three keys untouched, per the merge guard in the Basin
Watch project's claude/map-pipeline.md:
  - "basin"     - never produced by this script (a supplied shapefile,
                   basin_layers.py explicitly does not set this key)
  - "news"      - hand-curated by the daily brief skill, not a GIS layer
  - "generated" - the edition-publish date, owned by the daily brief skill
                   (see claim-monitor-state.md); a GIS refresh is not itself
                   a new edition

## Guards (updated 2026-09-10 after a real incident)

basin_layers.py's own query helper swallows a failed/partial ArcGIS query
(network blip, DNS failure, timeout) and returns whatever it has so far
rather than crashing the whole export - by design, so one bad source
shouldn't take down every other layer's refresh. That means a single fresh
export can legitimately come back with an empty or partial result for one
layer while every other layer is fine, and this merge step is the only
thing standing between that and a bad commit going live.

Two incidents, same underlying gap, one old guard didn't cover either
fully:

1. (2026-09-09, the original guard) "restricted"'s source (iscmaps.isc.ca)
   failed DNS resolution on a run; the old code blindly replaced 113 good
   polygons with the resulting empty list. Fixed by: skip a list-valued key
   entirely when the fresh value is an empty list but the existing bundle
   already has real data for it.

2. (2026-09-10) That fix only covers a list dropping to fully EMPTY. Two
   things it missed, both on the same day, most likely the same transient
   network hiccup against Saskatchewan's GIS host:
   - The boulder-heat query failed outright. `boulder_grid` (a list) came
     back empty and was correctly protected by guard #1 above - it kept its
     old 462 cells. But `boulder_total` (a plain int, not a list) has no
     "empty list" for the old guard to notice, so it fell straight through
     unprotected and got overwritten with the failed run's 0 - live data
     ended up with boulder_grid and boulder_total badly out of sync
     (correct grid, zeroed total), which broke the Boulder Heat toggle on
     the site (its enable/disable check reads boulder_total).
   - The lake-sediment geochem query failed while the till/soil geochem
     query succeeded. `geochem_grid` combines both sources into one grid,
     so the fresh result was NON-empty (built from till/soil alone) - just
     smaller (1,320 cells instead of 2,252) and missing the entire
     lake-sediment component (whole southwest-basin quadrant gone). Guard
     #1 only checks for fully-empty, so this partial, silent degradation
     sailed straight through and overwrote the good, complete data.

   Fixed by the two mechanisms below: TOTAL_OF ties a scalar total to its
   paired list's guard decision so they can never drift apart again, and
   SHRINK_FLOOR extends the guard to reject a large same-day shrink, not
   just a drop to zero - a same-day drop of more than half in any of these
   layers is essentially always a failed/partial source query, never a
   real registry change (claims lapse and get staked in single digits or
   low double digits per day, not by cutting a whole layer in half).

3. (2026-09-12, anticipated rather than hit live) The new "claims" layer
   (gis/basin_layers.py section 8b - the trailing-14-day staking window,
   added to close the two-pipeline drift between the claude.ai pages and
   basinwatch.ca - see claude/map-pipeline.md) does NOT behave like the
   other layers here: it's a rolling window recomputed from scratch every
   run, not an incrementally-updated registry, so its day-to-day count can
   legitimately swing by more than half in either direction (a big multi-
   claim staking batch simply ages out of the 14-day window on its own
   schedule, unrelated to anything going wrong that day). Running it through
   SHRINK_FLOOR as-is would misread that normal volatility as a failed query
   and freeze "claims" stale again - reintroducing, via a different code
   path, exactly the staleness bug this whole file exists to prevent. Since
   "claims" is built from the exact same `tenure` pull in the same run (see
   section 8b's own comment), its correctness is already guaranteed by
   tenure's own guard: if that pull failed, tenure's guard already rejects
   it (see DERIVED_FROM below), and if it succeeded, claims's own count is
   trustworthy at any size. So "claims" skips SHRINK_FLOOR entirely and
   instead inherits tenure's accept/reject decision.

4. (2026-09-13, hit live - "the lakes still aren't showing up") A single bad
   ArcGIS run tripped two separate, previously-unnoticed gaps in the guard at
   once:
   - `list_should_be_rejected()`'s very first line, `if old_len <
     MIN_SIZE_TO_GUARD: return False`, exempted any list shorter than 20
     items from EVERY check below it, including the "did this go to zero"
     check that guard #1 above exists specifically to catch. "places" (8
     items on a good day) is exactly this small, so when its query failed
     that day and came back empty, the guard let all 8 places be silently
     replaced with 0 - the same unprotected-empty failure mode incident #1
     was supposed to have closed everywhere, reopened here for every
     small list. Fixed by checking for a fresh empty list FIRST, before the
     small-list exemption ever gets a chance to apply - a list going to
     zero is never "too small to matter," whatever floor it's judged against
     otherwise.
   - The generic SHRINK_FLOOR=0.5 is tuned for layers where "a lot changed
     overnight" is itself already suspicious. That's the wrong floor for a
     near-static geographic registry like "lakes" or "highways" - lakes
     don't newly exist or vanish, so a same-day count that drops by 42%
     (60 -> 35, the actual live figure that day) is never real, it's the
     source query returning a partial result and a bad shape or two per
     the self-intersection filter getting the rest to look like enough
     of a drop to slip under 50%. 58% of the old count still cleared the
     0.5 floor, so this was accepted and shipped. Fixed by
     PER_KEY_SHRINK_FLOOR below: an explicit, stricter floor (0.85) for
     the specific keys where day-to-day volatility this large is never
     legitimate, checked in `list_should_be_rejected()` via
     `PER_KEY_SHRINK_FLOOR.get(key, SHRINK_FLOOR)` - everything not listed
     there keeps the original 0.5 behavior unchanged.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "data" / "bundle.json"
MAP_BUNDLE = ROOT / "gis" / "exports" / "map_bundle.json"

SKIP_KEYS = {"basin", "news", "generated"}

# Scalar counts that ride alongside a list-valued key and describe it (a raw
# sample count behind a binned grid, say). These have no "empty list" of
# their own to protect them, so each one is tied to its paired list's guard
# decision instead of being merged independently - if the list gets
# rejected, the total is rejected right along with it, whatever value the
# fresh export gave it.
TOTAL_OF = {"boulder_grid": "boulder_total", "geochem_grid": "geochem_total"}

# A same-day drop below this fraction of the existing length is treated as a
# failed/partial source query, not a real change, and the whole key is
# rejected (existing data kept). Every layer here is a slow-moving registry
# or a large static dataset - real day-to-day movement is small.
SHRINK_FLOOR = 0.5

# Per-key override of SHRINK_FLOOR, for keys where even a same-day drop that
# would clear the generic 0.5 floor is still never legitimate. Added after
# incident 4: "lakes" going 60 -> 35 (58% of the old count - a passing grade
# under 0.5) was in fact a failed/partial query, not 25 lakes disappearing
# overnight. Lakes and highways don't move day to day at all, so a much
# stricter floor is safe here without risking false rejections of real data.
PER_KEY_SHRINK_FLOOR = {"lakes": 0.85, "highways": 0.85}

# Below this length, a layer is small enough that ordinary variation could
# plausibly swing past SHRINK_FLOOR on a legitimate run - don't second-guess
# it either way, just take the fresh value like before.
MIN_SIZE_TO_GUARD = 20

# Keys built FROM another key's data in the same basin_layers.py run, whose
# own size is naturally volatile (a rolling window, not a slow-moving
# registry) and so must never be judged by SHRINK_FLOOR on its own terms -
# it inherits its source key's accept/reject decision instead. See incident
# 3 above.
DERIVED_FROM = {"claims": "tenure"}


def list_should_be_rejected(fresh_list, existing_list, key=None):
    """True if fresh_list looks like a failed/partial query, not real data.

    The empty check runs BEFORE the small-list exemption (incident 4, part 1) - a
    list going to zero is never "too small to matter," whatever floor it would
    otherwise be judged against. key selects a stricter per-key floor from
    PER_KEY_SHRINK_FLOOR when one exists (incident 4, part 2); everything else
    keeps the original SHRINK_FLOOR.
    """
    old_len = len(existing_list or [])
    new_len = len(fresh_list)
    if old_len == 0:
        return False
    if new_len == 0:
        return True
    if old_len < MIN_SIZE_TO_GUARD:
        return False
    floor = PER_KEY_SHRINK_FLOOR.get(key, SHRINK_FLOOR)
    if new_len < old_len * floor:
        return True
    return False


def main() -> None:
    if not MAP_BUNDLE.exists():
        raise SystemExit(f"{MAP_BUNDLE} not found - did basin_layers.py run first?")

    bundle = json.loads(BUNDLE.read_text(encoding="utf-8-sig"))
    fresh = json.loads(MAP_BUNDLE.read_text(encoding="utf-8-sig"))

    changed = []
    skipped = []  # (key, existing_len_or_val, fresh_len_or_val)
    rejected_lists = set()

    for k, v in fresh.items():
        if k in SKIP_KEYS or k in TOTAL_OF.values() or k in DERIVED_FROM:
            continue  # totals and derived keys are handled below, tied to another key's decision
        if isinstance(v, list):
            existing = bundle.get(k)
            if list_should_be_rejected(v, existing, key=k):
                skipped.append((k, len(existing or []), len(v)))
                rejected_lists.add(k)
                continue
        bundle[k] = v
        changed.append(k)

    for list_key, total_key in TOTAL_OF.items():
        if total_key not in fresh:
            continue
        if list_key in rejected_lists:
            skipped.append((total_key, bundle.get(total_key), fresh[total_key]))
            continue
        bundle[total_key] = fresh[total_key]
        changed.append(total_key)

    for derived_key, source_key in DERIVED_FROM.items():
        if derived_key not in fresh:
            continue
        if source_key in rejected_lists:
            skipped.append((derived_key, len(bundle.get(derived_key) or []), len(fresh[derived_key])))
            continue
        bundle[derived_key] = fresh[derived_key]
        changed.append(derived_key)

    BUNDLE.write_text(json.dumps(bundle, separators=(",", ":")), encoding="utf-8")
    print(f"merged {len(changed)} keys into {BUNDLE}: {', '.join(sorted(changed))}")
    if skipped:
        print("SKIPPED (fresh data looked like a failed/partial query, kept what was already live):")
        for k, old_v, new_v in sorted(skipped):
            print(f"  {k}: had {old_v}, fresh run had {new_v}")


if __name__ == "__main__":
    main()
