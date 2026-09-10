#!/usr/bin/env python3
"""
Merge gis/exports/map_bundle.json (fresh output of basin_layers.py) into
data/bundle.json (the bundle the site actually builds from).

Run after gis/basin_layers.py, before committing. Replaces every key
basin_layers.py produces - tenure, deposits, mines, places, highways,
footprints, lakes, boulder_grid, boulder_total, geochem_grid, geochem_total,
conductors, lapsed, ab_tenure, restricted, smdi - with the freshly pulled
version.

Deliberately leaves three keys untouched, per the merge guard in the Basin
Watch project's claude/map-pipeline.md:
  - "basin"     - never produced by this script (Ezra-supplied shapefile,
                   basin_layers.py explicitly does not set this key)
  - "news"      - hand-curated by the daily brief skill, not a GIS layer
  - "generated" - the edition-publish date, owned by the daily brief skill
                   (see claim-monitor-state.md); a GIS refresh is not itself
                   a new edition
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "data" / "bundle.json"
MAP_BUNDLE = ROOT / "gis" / "exports" / "map_bundle.json"

SKIP_KEYS = {"basin", "news", "generated"}


def main() -> None:
    if not MAP_BUNDLE.exists():
        raise SystemExit(f"{MAP_BUNDLE} not found - did basin_layers.py run first?")

    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    fresh = json.loads(MAP_BUNDLE.read_text(encoding="utf-8"))

    changed = []
    for k, v in fresh.items():
        if k in SKIP_KEYS:
            continue
        bundle[k] = v
        changed.append(k)

    BUNDLE.write_text(json.dumps(bundle, separators=(",", ":")), encoding="utf-8")
    print(f"merged {len(changed)} keys into {BUNDLE}: {', '.join(sorted(changed))}")


if __name__ == "__main__":
    main()
