# Daily publish instructions - basinwatch.ca (added 2026-09-10, updated 2026-09-10 evening, 2026-09-11)

For Ezra, every morning after the scheduled `uranium-brief` task runs. This is the one manual
step left in the pipeline - see `claude/claim-monitor-state.md`'s RESOLVED and CLOSED sections
(2026-09-10) for the full diagnosis of why it's manual and why a fully automated alternative
was tried and closed out.

**Standing note, added 2026-09-14: this manual routine is superseded for repo-bound sessions.**
See `basinwatch-pipeline-fix.md`'s "Standing note: real git write access confirmed 2026-09-14"
section. A Claude Code session/environment with `sockthief77/basin-watch` selected as its
repository has real git push access and should publish `data/edition.json` directly via
`git add` / commit / `git push` to `main`, verified first with `scripts/build.py` - not via
this manual paste-and-commit flow. This file stays accurate and in force for any session
WITHOUT that repo binding (a generic Cowork/chat session) - check which kind of session you're
running in before assuming direct push is available.

**Update, 2026-09-10 evening: deliver the content inline in the chat reply, not just as a file
attachment.** Ezra found selecting/copying text out of the `SendUserFile` file card hard to
do. Going forward, every run that hands off an `edition.json` pastes the full JSON content
directly into the chat reply as a fenced code block (in addition to still sending the file via
`SendUserFile`, which stays useful as a backup/record) - the code block is what Ezra actually
copies from.

**Standing rule, added 2026-09-11 (later): take the simple route - be the automation, don't
make Ezra do it.** Ezra's own words, after a rough stretch this session trying to get him to
do a manual 5-edit find-and-replace in a downloaded copy of `site/shell.html`: "Always take
the simple route. If I can't automate the whole website, you are my automation." When there's
a choice between walking Ezra through a manual multi-step process (especially anything
involving precise text editing, find-and-replace, or copy-paste across programs) and just
asking him to upload the one file that's needed so the session can edit it directly and hand
back a complete ready-to-paste result, **default to asking for the file and doing the edit
yourself.** The GitHub-editor-paste-and-commit pattern (whole-file paste, no local editing)
is the standard to aim for every time - see the `site/shell.html` Lapsing-8-14-Days patch
2026-09-11 for the worked example: asking Ezra to do 5 manual find-replace edits in
Notepad++ hit real friction (Windows clipboard silently changing line endings, a read-only
file property, markdown fence characters getting swept into a copy) before switching to "just
upload the file" and the whole thing was done in one clean pass.

**Standing rule, added 2026-09-11: always resend the actual current file fresh, never point
back at an earlier message in the conversation.** During an interactive session (not just the
scheduled daily run), Ezra's explicit instruction: "ALWAYS give me the files here fresh." If a
file was already sent earlier in the same conversation and is still the one he needs - whether
that's `edition.json` after a fix, or a one-time handoff file like `build_archive.py` - resend
it via `SendUserFile` again in the same message rather than saying "use the one from earlier"
or "scroll up for it." This applies to every file this skill hands off, not just
`edition.json`. Rationale is the same one behind the 2026-09-10 mix-up below: asking Ezra to
find the right past version in scrollback is exactly how the wrong file gets used, and it
costs nothing to just attach the current copy again.

**Standing rule, added 2026-09-11: anonymity and professional voice in anything published.**
See `claude/watchlist-and-sources.md`'s "Anonymity and voice - published content only" section
for the full rule and the 2026-09-11 incident it documents (the operator's first name had
accumulated in ~40 code comments across `site/shell.html`, both claude.ai pages and two frozen
archive snapshots, plus an edition note reading "per [name]'s request" - all scrubbed and
republished the same day). Before any edition or code change goes live: no name or other
identifying detail anywhere in published text or committed code (comments included), and no
AI-style process narration ("a count derived from...", "confirmed by a direct diff of...") in
anything a reader sees - state the fact, not the method.

**Standing rule, FINAL 2026-09-11: no ceo.ca tagline anywhere, at all.** A tongue-in-cheek
tagline mocking ceo.ca ("ceo.ca, if pump-and-dump weren't the business model", and an earlier
"like ceo.ca, ..." wording) was tried in two different placements (under "Week in review", then
centered under the spot-price ticker) and iterated on for most of a session. **Ezra killed it
for good, in his own words: "get rid of the ceo.ca line. Its messing up everything and probably
a legal issue."** Removed from `edition_top_html`, from `site/shell.html`'s CSS (no
`.tagline` rule of any kind should exist in that file), and from both claude.ai artifact pages.
**Do not re-add a ceo.ca tagline, reference, or comparison anywhere in `edition_top_html`,
`site/shell.html`, or either artifact page, in any wording or placement, unless Ezra
explicitly asks again.** If in doubt, leave ceo.ca out of anything published entirely -
factual sourcing mentions (e.g. citing it as a news source in an internal note) are fine, but
no jokes, taglines, or comparisons about it in anything a reader sees.

The masthead's other 2026-09-11 change stays (this part is unrelated to the tagline and is
still wanted): the `.sub` paragraph, verbatim:
```html
<p class="sub">Daily Athabasca Basin uranium briefing, covering both juniors and majors, ranked by news-release materiality.<span style="display:block;white-space:nowrap">NR and tenure movement tracked on the companion Basin Explorer map.</span><span style="display:block">A new edition publishes every day at 9:00 a.m. CST.</span></p>
```
The `.tickerwrap` block stays at its original, pre-tagline structure - just the ticker, nothing
added below it:
```html
<div class="tickerwrap"><div class="ticker">
    <span class="tksym mono">U₃O₈</span>
    <span class="tkpx mono">$123.74</span>
    <span class="tklbl">CA$/lb</span>
    <span class="tksrc">Aug month-end avg · US$89.68 at 1.3798</span>
  </div></div>
```
(the U₃O₈ price/label/source values inside `.ticker` update daily as normal)
Matching CSS in `site/shell.html`, reverted to original (no `.tagline` rule at all):
```css
.tickerwrap{display:flex;pointer-events:none;justify-self:center;align-self:center}
```

## Steps (for sessions WITHOUT repo write access - see standing note above)

1. **Find the content.** The scheduled task's run posts the full `edition.json` content
   directly in its chat reply, inside a fenced code block, once it finishes
   (~8:30-8:50am Regina). It also sends the same content as a file, but the code block in the
   chat is the one to copy from.

2. **Copy it.** Click/tap inside the code block and select all of its content (from the
   opening `{` to the closing `}`), copy it. It should look like this at the start:
   ```
   {
     "generated": "<today's date>",
     "edition": 1,
     "edition_top_html": "...",
     "edition_bottom_html": "..."
   }
   ```

3. **Open this exact link:**
   `https://github.com/sockthief77/basin-watch/edit/main/data/edition.json`
   This is GitHub's built-in editor, already on the right file and the `main` branch.

4. **Clear the old content.** Click inside the editor, Ctrl+A / Cmd+A to select all existing
   text, Delete to remove it.

5. **Paste the new content.** Ctrl+V / Cmd+V.

6. **Check the `"generated"` date at the top of the pasted text matches today.** If it shows
   yesterday's date (or anything else unexpected), stop - don't commit - and flag it instead.

7. **Click the green "Commit changes..." button**, top right of the page.

8. **In the dialog that opens, confirm "Commit directly to the `main` branch" is selected**
   (it's the default), then click the confirm button (also "Commit changes").

9. **Done.** Cloudflare Pages is connected directly to the repo and redeploys automatically
   on that push - no workflow to run, no re-share, nothing else needed. Give it 1-2 minutes.

10. **Optional verification:** open `https://basinwatch.ca` after a minute or two and confirm
    the masthead date and lead story match today's edition.

## If something looks wrong

Stop and flag it rather than guessing or forcing it through - don't force-push, don't delete
and retry blindly. `main` has branch protection (restrict deletions, block force pushes) as
of 2026-09-10, so a bad commit is always recoverable with `git revert <sha> && git push` -
see `claude/claim-monitor-state.md`'s "`main` branch protection" section.

## Note on a 2026-09-10 mix-up

On 2026-09-10 an earlier, no-op `edition.json` (sent before a wrap-bug fix was found and
applied later the same day) got pasted and committed instead of the corrected one sent
afterward - both files looked alike and the fixed one was buried in chat scrollback. Pasting
straight from the chat's own code block each morning (rather than hunting for the right past
file attachment) is meant to prevent a repeat of that specific mix-up. **The 2026-09-11
"always resend fresh" rule above is the same fix applied more generally**, after the same
underlying problem showed up again in an interactive (non-scheduled) session the same day -
Ezra had to ask for a file to be resent because it was easier than finding it in scrollback.

## One-time repo setup files, handed off 2026-09-11 (not part of the daily routine)

Two features were built this session that need a **one-time** paste into the repo, separate
from the daily `edition.json` routine above. Once pasted and committed, neither needs to be
touched again - they run themselves.

- **`scripts/build_archive.py` + `.github/workflows/archive-edition.yml`** - sets up
  basinwatch.ca's own `/archive/edition<NNN>/` pages (text-only, no map, chained back to the
  previous edition). Triggers automatically on every future `data/edition.json` push - no
  change to the daily steps above. See `claude/archive-index.md`/`claude/map-pipeline.md` for
  the design.
- **`site/shell.html` patch for "Lapsing 8-14 Days"** - 5 find/replace edits (handed off as a
  markdown file, not a full-file replacement, since the session didn't have the exact current
  text of `site/shell.html` in hand) so basinwatch.ca's own map gets the same second-tier
  lapsing layer already live on the two claude.ai pages. Verify with `scripts/build.py` before
  committing. See `claude/map-pipeline.md`'s "Lapsing: two tiers" section.

**Status checked 2026-09-11 afternoon:** both `scripts/build_archive.py` and
`.github/workflows/archive-edition.yml` are confirmed present on `main`
(`raw.githubusercontent.com` fetch of both paths succeeds). **But no `archive/edition*/`
page exists yet** - `basinwatch.ca/archive/edition001/` and `/edition002/` both 404, and the
repo's Actions history shows no "Archive edition" workflow run at all, despite `data/edition.json`
having been pushed twice since (14:59 and 16:37 UTC, 2026-09-11). Two explanations fit: the
workflow file may have landed on `main` after both of those pushes, so it simply hasn't had a
qualifying push yet - the very next `edition.json` commit should trigger it and produce
`archive/edition002/`; or something is silently wrong (workflow permissions, a paths-filter
mismatch) and it won't fire even then. **Check after the next `edition.json` push** (the next
scheduled run, or the next manual paste-and-commit) whether `archive/edition002/index.html`
appears in the repo and the page loads on basinwatch.ca. If it still doesn't, the workflow
needs debugging from a session with repo write/Actions-log access, which this one didn't have.

**`site/shell.html` patch status:** confirmed committed 2026-09-11 ("commit changes"), and
confirmed live and correct on `basinwatch.ca` (checked via `view-source` the same afternoon).
The one thing wrong with it - the operator's name baked into ~30 code comments - was found and
scrubbed the same afternoon; see the anonymity rule above and `watchlist-and-sources.md`.
