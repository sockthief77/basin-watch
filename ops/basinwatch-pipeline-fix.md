# basinwatch.ca pipeline: corrected diagnosis (2026-09-10, superseding the earlier version of this doc)

**The earlier version of this doc was wrong.** It was built from `WebFetch` calls against
`raw.githubusercontent.com` that returned false 404s on files that actually exist - confirmed
by cloning the repo directly (`git clone https://github.com/sockthief77/basin-watch.git`,
which works read-only with no credential since the repo is public). A plain `curl` to the
same raw URLs also returned 200. **`WebFetch`'s 404s against this host were not reliable this
session - don't trust them again without cross-checking via a real clone.**

## What's actually there (verified by clone, not WebFetch)

The pipeline is complete and well-built:

| Path | State |
|---|---|
| `.github/workflows/gis-export.yml` | Exists, correctly configured (07:30 America/Regina cron, `contents: write`, checkout → `basin_layers.py` → `merge_map_bundle.py` → conditional commit/push). |
| `.github/workflows/publish-brief.yml` | Exists, correctly configured (09:20 America/Regina cron → `merge_edition.py` → `build.py` → conditional commit/push). **Confirmed dead code - recommended for deletion, see map-pipeline.md.** |
| `scripts/merge_map_bundle.py` | Exists. Has a real anti-data-loss guard: if a freshly-pulled layer comes back empty while the existing bundle has real data for that key, it skips the overwrite rather than erasing good data with a failed fetch's empty result. |
| `scripts/merge_edition.py` | Exists. **Confirmed dead code** - the base64-Artifact-handoff mechanism this was for is retired; it always fails soft and never actually updates anything. |
| `scripts/build.py` | Exists. Substitutes `data/bundle.json` and `data/edition.json` into `site/shell.html` / `site/explorer-shell.html`, writes `dist/index.html` and `dist/explorer/index.html`. Verifies exactly two `<script>` tags survive (three on Basin Watch as of the footer modal - check against what the page had before your edit, not a fixed number) and the bundle re-parses as real JSON before writing anything - a real regression guard against the exact class of bug (`<script>` tags silently stripped, bundle corrupted) documented at length in `claim-monitor-state.md` and `map-pipeline.md`. Handles the UTF-8 BOM in the data files correctly (`encoding="utf-8-sig"`). |
| `data/bundle.json` | Exists, several MB, real data (~7,400+ tenure records). |
| `data/edition.json` | Exists, updated daily. |
| `wrangler.toml` | Exists, points Cloudflare Pages at `./dist` as the static asset directory. |

## Standing note: real git write access confirmed 2026-09-14

**As of 2026-09-14, a Claude Code scheduled task/environment with `sockthief77/basin-watch`
selected as its repository has real git push access** - confirmed by an actual test push to a
throwaway branch, and this is now how the daily `uranium-brief` run should publish
`data/edition.json`: `git add`, commit, `git push` directly to `main`, verified first with
`scripts/build.py`. **The old "settled, manual-by-design, don't re-investigate" architecture
this file (and `daily-publish-instructions.md`, `claim-monitor-state.md`) describe below is
now superseded for any session running as this bound Claude Code environment.** It is NOT
superseded for a generic Cowork/chat session with no repo binding - that kind of session still
has no git credential and should still hand off `edition.json` via `SendUserFile` for manual
paste-and-commit, exactly as documented below. Check which kind of session you're running in
before assuming direct push is available: if `git push --dry-run` against this repo succeeds,
push directly; if it's denied with "not in this session's authorized repository set," you're
in the old kind of session and the manual handoff below still applies.

## Historical context (accurate description of the OLD, pre-2026-09-14 constraint, kept for sessions without repo binding)

1. Every session type before this one only ever got read-only repo access (a plain `git clone`,
   no credential) - write access was denied by the git proxy with "not in this session's
   authorized repository set."
2. The working path for those sessions: diagnose from a read-only clone, hand the user complete
   fixed files, they paste-and-commit via GitHub's own web editor - see
   `daily-publish-instructions.md` for the exact steps, still valid for non-repo-bound sessions.
3. This was investigated repeatedly (fine-grained PAT tried and abandoned, Cowork scheduled
   tasks confirmed to have no secret-storage mechanism) and closed as a platform limitation
   for THAT task surface specifically - not a limitation of Claude Code environments generally,
   which is the gap that was finally closed 2026-09-14.
