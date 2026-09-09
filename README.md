# Basin Watch

Daily Athabasca Basin uranium competitor brief + claim-monitoring map, for `basinwatch.ca`.

## Structure

```
site/
  shell.html            # Basin Watch page template - everything except data,
                         # with /*__BUNDLE__*/ standing in for it
  explorer-shell.html   # Basin Explorer page template, same placeholder pattern
data/
  bundle.json           # BASIN_BUNDLE - the one data object both pages render from
scripts/
  build.py              # Substitutes bundle.json into both shells, writes dist/
dist/                   # Build output (gitignored) - index.html + explorer/index.html
```

This is a template/data split, not the multi-MB hand-edited HTML the project ran on
originally (see `claude/map-pipeline.md` and `claude/open-items.md` in the Basin Watch
project docs for the drift and breakage history that pattern produced - dead function
references blanking the map, stripped `<script>` tags, swatch-colour drift, repeated
same-day publish collisions). Editing the page now means editing `data/bundle.json` and/or
`site/*.html`, never a rendered output file.

## Building

```
pip install --break-system-packages -r requirements.txt   # none yet - build.py is stdlib-only
python3 scripts/build.py
```

Writes `dist/index.html` and `dist/explorer/index.html`. The build script verifies, for
each output, that exactly two `<script>` tags survive and that the substituted bundle
re-parses as JSON before writing anything - a bad edit fails the build instead of shipping
a broken page.

## Hosting

Cloudflare Pages, connected directly to this repo:
- Build command: `python3 scripts/build.py`
- Build output directory: `dist`
- Custom domain: `basinwatch.ca` (Basin Explorer lives at `basinwatch.ca/explorer`, not a
  separate domain or a separate deploy - see the project's launch-readiness doc)

Every push to `main` that changes `data/bundle.json` or `site/*.html` triggers a rebuild
and redeploy automatically.

## Data pipeline (in progress)

The daily edition (news ranking, claim-staking diff) and the geoscience layer refresh
(`basin_layers.py` - tenure, conductors, SMDI, boulder/geochem heat, etc.) currently still
run the way they did before this repo existed - see the Basin Watch Claude project's
`claude/claim-monitor-state.md` and `claude/map-pipeline.md` for the full mechanism.
Migrating both onto a schedule that writes straight into `data/bundle.json` and commits
here (so a push is what publishes an edition, not a manual artifact republish) is tracked
work, not yet done. `gis.saskatchewan.ca` and the Alberta GIS host are blocked by egress
allowlists from most cloud environments; GitHub Actions runners are not behind that
allowlist, which is the planned fix for the current dependency on a scheduled task on
Ezra's own machine (documented as fragile in `claude/open-items.md`).

## Provenance

Seeded 2026-09-09 from the live pages then at
`claude.ai/code/artifact/27c1b96e-0b57-47f1-bc6f-0e698e4ca186` (Basin Watch) and
`claude.ai/code/artifact/47766502-5368-43a1-9a1e-6e007f270bbc` (Basin Explorer), split into
template + data and verified to render pixel-identical to both live pages with zero
JS errors before being committed here.
