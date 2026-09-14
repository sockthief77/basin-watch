
# Archive index

Maps each Basin Watch edition to its permanent archived page, so the "Archive" list on the
live page can link each past row to the content as it actually looked that day.

**Why this exists, added 2026-09-09 on Ezra's request:** the live page is rewritten every
morning - once an edition is overwritten its exact content is gone unless a copy was taken
first. This doc tracks that copy mechanism and its history.

## Current mechanism (switched 2026-09-11): native basinwatch.ca pages, not claude.ai snapshots

**Decided 2026-09-11, Ezra's explicit instruction: archive rows should "open up as a link
properly, not a claude artifact."** Going forward, an archived edition's row links to its own
`https://basinwatch.ca/archive/edition<NNN>/` page (built by `scripts/build_archive.py`, see
below), not to a claude.ai snapshot artifact. The claude.ai-snapshot mechanism described later
in this doc under "Superseded" is retired - kept here only as history and as the source used
to backfill Edition 001 (see below).

**How to add an archived row for a newly-outgoing edition:**
1. `scripts/build_archive.py` builds `archive/edition<NNN>/index.html` from whatever is
   currently in `data/edition.json` - so archiving edition N happens naturally the moment
   edition N's `edition.json` gets committed, no separate snapshot step needed like the old
   mechanism required.
2. In the *next* edition's Archive section, link the outgoing edition's row to
   `/archive/edition<NNN>/` (relative path - works because basinwatch.ca serves it directly).
3. The current edition's own row stays a plain, non-clickable `<div class="arow">`, same rule
   as always - the reader is already looking at that content.

**Two separate bugs had to be fixed before this actually worked end to end (both fixed
2026-09-11):**

1. **`.github/workflows/archive-edition.yml` silently no-op'd on every run.** Its commit step
   checked `git diff --quiet -- archive/` for changes *before* running `git add archive/`.
   `git diff` never reports brand-new, untracked files - only changes to files git already
   tracks. Since `archive/` had never existed in the repo, every page `build_archive.py` wrote
   there was untracked, so the check always read "no changes" and exited before
   `git add`/`commit`/`push` ever ran - green checkmark, no commit, every time. Fixed by
   staging first (`git add archive/` before `git diff --cached --quiet`).
2. **Even after #1 was fixed and `archive/edition002/index.html` existed in the repo,
   `basinwatch.ca/archive/edition002/` still 404'd.** Root cause: Cloudflare Pages serves only
   `dist/` (`wrangler.toml`'s `[assets] directory = "./dist"`), and `scripts/build.py` - the
   script that actually produces `dist/` - never copied `archive/` into it. The
   `archive-edition.yml` workflow was committing pages to the right place in the *repo*, but
   nothing ever put a copy where Cloudflare *serves from*. Fixed by adding an `archive/` ->
   `dist/archive/` copy step to `scripts/build.py` (`shutil.copytree`, skipped gracefully if
   `archive/` doesn't exist yet).

**A third bug, found 2026-09-11 after the pages were actually loading: a huge blank gap
between ranked news items on the archive page (screenshotted by Ezra - item #1 to item #2 on
Edition 001 had roughly 900px of empty space between them).** Root cause: `build_archive.py`
bakes its own copy of the relevant page CSS into its template string rather than reading it
from `site/shell.html` - and that baked-in copy had drifted stale. Specifically
`.item>.stk{grid-row:1/span 99}` (a since-abandoned trick to make the stock-price card span
"however many rows the item needs"), which the live pages had already simplified to
`.item>.stk{grid-row:1}` at some point. `span 99` forces ~98 empty implicit grid rows into
existence, and CSS grid's `row-gap` (10px here) applies between every adjacent row whether or
not it holds content - so ~98 x 10px of pure gap appeared between items. Confirmed by
rendering the built HTML locally in Playwright before and after the fix (screenshots matched
Ezra's report exactly, then matched the live page once fixed). Fixed by changing that one CSS
rule in `build_archive.py` to `grid-row:1`, matching the live page. **Lesson for later: if
`build_archive.py`'s baked-in CSS ever needs other rules the live page has, that same
drift risk applies to all of it, not just this one rule** - worth eventually having
`build_archive.py` extract its CSS from `site/shell.html` directly instead of keeping its own
copy, so the two can't drift apart again.

**Files handed to Ezra 2026-09-11 to complete this transition:**
- `scripts/build.py` (patched with the `dist/archive/` copy step)
- `scripts/build_archive.py` (patched to fix the `grid-row:1/span 99` layout bug)
- `archive/edition001/index.html` (new - the backfilled page, rebuilt with the layout fix)
- `archive/edition002/index.html` (replaces the existing one - links back to 001, rebuilt
  with the layout fix)
- `data/edition.json` (Edition 001's Archive row now points at `/archive/edition001/` instead
  of the claude.ai snapshot URL)

## Edition numbering - resumed 2026-09-11 (schedule set 2026-09-10, the authoritative version)

**Current, authoritative schedule (2026-09-10, Ezra's explicit instruction):**

- **2026-09-10 stayed Edition 001, no archive snapshot taken at the time.** Ordinary in-place
  republish - it got its archived page later, via the 2026-09-11 backfill above.
- **2026-09-11's run archived 2026-09-10 as Edition 001** (via a claude.ai snapshot, since
  that was the mechanism in use at the time - see "Superseded" below) and **published as
  Edition 002.**
- **Every run from 2026-09-12 onward increments by one** from the previous edition's number
  (read off the outgoing edition, never hardcoded). With the native mechanism, archiving the
  outgoing edition is automatic - see "Current mechanism" above - no separate snapshot step.

**Superseded history, left for reference only - do not act on it:**
1. The original 2026-09-08 rule: stay at Edition 001 indefinitely until Ezra explicitly says
   to start version 2.
2. The 2026-09-09 evening rule: "2026-09-09 stays Edition 001. Tomorrow's 8am run,
   2026-09-10, is Edition 002, and the number increments by one every subsequent daily
   edition from there." Reversed the next morning before it executed.
3. A same-morning (2026-09-10) correction back to rule 1 ("stay at 001 indefinitely"),
   in force for only a few hours before Ezra clarified he wants archiving to resume
   starting with the very next run - landing on the current schedule above.

**The 2026-09-09 snapshot below (`bf565a86...`) remains stale and unused** - it was
a mid-day setup snapshot, never adopted as any edition's real archived copy.

## Superseded: the claude.ai snapshot mechanism (2026-09-09 to 2026-09-11, retired)

This was the original mechanism, in use before the native `basinwatch.ca/archive/` pages
existed. No longer used for new editions - kept here for history and because it's what
Edition 001's backfilled page was built from.

1. Before rewriting the live page with the new edition, the live page's current full HTML
   (the edition about to become "yesterday's") got published as its own new claude.ai
   artifact - titled `Basin Watch — <date>`, same favicon (☢️).
2. The returned URL was recorded in the Index below, keyed by date.
3. The new edition's Archive section linked the row for the date just archived to that URL.

**CSS already on the live page** (added 2026-09-09, still in use - the link styling is
mechanism-agnostic):
```
.arch a.arow{color:inherit;text-decoration:none;cursor:pointer}
.arch a.arow:hover{background:var(--surface-2)}
.arch a.arow:hover .ad{color:var(--ink)}
```

## 2026-09-08 row removed from the live page (2026-09-09 evening, Ezra's request)

The 2026-09-08 edition never had a snapshot (predates any archive mechanism), so its Archive
row was a permanently-unlinked plain div. Ezra asked to remove it from the display entirely
rather than keep showing a dead, unclickable row. Removed from the live page's Archive
section same evening, verified (2 `<script>` tags, bundle still parses), republished. **Do
not re-add a 2026-09-08 row** - there is no snapshot to link it to (the native mechanism
can't backfill it either, since `data/edition.json` didn't exist that far back) and Ezra
explicitly wants it gone, not just unlinked.

## Index

| Date | Archived edition URL | Notes |
|---|---|---|
| 2026-09-09 | https://claude.ai/code/artifact/bf565a86-dfc5-402f-985c-bad1203893b3 | Stale mid-day snapshot, never adopted as any edition's archived copy - see "Edition numbering" above. Do not reuse. |
| 2026-09-10 | `/archive/edition001/` on basinwatch.ca | Edition 001. Originally archived 2026-09-11 as a claude.ai snapshot (`https://claude.ai/code/artifact/641bbe0c-90f4-410b-aaad-34535b64e7e8`, still valid, scrubbed and up to date) - backfilled to the native page 2026-09-11 by feeding that snapshot's content through `build_archive.py` directly. The claude.ai URL still works if needed but is no longer what the live page links to. |
| 2026-09-11 | `/archive/edition002/` on basinwatch.ca | Edition 002. Built automatically by `build_archive.py` the native way - no snapshot step needed. |
| 2026-09-12 | `/archive/edition003/` on basinwatch.ca (expected) | Edition 003. A claude.ai snapshot was also taken 2026-09-13 (`https://claude.ai/code/artifact/796c8a77-fddd-4d05-8328-53d609121360`) for the claude.ai pages' own Archive links - both mechanisms now run in parallel, see `claim-monitor-state.md`'s 2026-09-13 run note. |

Every edition from here on gets its `/archive/edition<NNN>/` page automatically the moment
its `data/edition.json` is committed (once `scripts/build.py`'s `dist/archive/` copy step is
live) - nothing to add to this table manually going forward. Keep adding a row here only if a
mechanism problem needs documenting, the way the three 2026-09-11 bugs did.
