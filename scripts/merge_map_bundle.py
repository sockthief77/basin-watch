#!/usr/bin/env python3
"""
Merge gis/exports/map_bundle.json (fresh output of basin_layers.py) into
data/bundle.json (the bundle the site actually builds from).

Run after gis/basin_layers.py, before committing. Replaces every key
basin_layers.py produces - tenure, deposits, mines, places, highways,
footprints, lakes, boulder_grid, boulder_total, geochem_grid, geochem_total,
conductors, lapsed, ab_tenure, restricted, smdi - with the freshly pulled
version, subject to the guards below.

Deliberately leaves three keys untouched, per the merge guard in the Basin
Watch project's claude/map-pipeline.md:
  - "basin"     - never produced by this script (Ezra-supplied shapefile,
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

# Below this length, a layer is small enough that ordinary variation could
# plausibly swing past SHRINK_FLOOR on a legitimate run - don't second-guess
# it either way, just take the fresh value like before.
MIN_SIZE_TO_GUARD = 20


def list_should_be_rejected(fresh_list, existing_list):
    """True if fresh_list looks like a failed/partial query, not real data."""
    old_len = len(existing_list or [])
    new_len = len(fresh_list)
    if old_len < MIN_SIZE_TO_GUARD:
        return False
    if new_len == 0:
        return True
    if new_len < old_len * SHRINK_FLOOR:
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
        if k in SKIP_KEYS or k in TOTAL_OF.values():
            continue  # totals are handled below, tied to their list's decision
        if isinstance(v, list):
            existing = bundle.get(k)
            if list_should_be_rejected(v, existing):
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

    BUNDLE.write_text(json.dumps(bundle, separators=(",", ":")), encoding="utf-8")
    print(f"merged {len(changed)} keys into {BUNDLE}: {', '.join(sorted(changed))}")
    if skipped:
        print("SKIPPED (fresh data looked like a failed/partial query, kept what was already live):")
        for k, old_v, new_v in sorted(skipped):
            print(f"  {k}: had {old_v}, fresh run had {new_v}")


if __name__ == "__main__":
    main()
