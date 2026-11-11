# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9 (release). Last build: `work/build/` (2026-11-12, after polish pass; `work/build_e/` is older, stale).
- **Done:** engine, all 7,873 script rows + 1,050 EXE strings translated, graphics incl. English title logo, FMV
  captions, release tool. 2026-11-12: template layout; **story pass done** - 12 chapter files
  (`tools/review.py --chapters`, split per D9) all reviewed, Critical/Important fixed, re-checked;
  **polish pass done** - all `docs/polish.md` lines ticked (150 rows changed, item-get articles per D10), diff
  re-checked (`work/qa/story/polish_fixes.txt`, verdicts/polish.tsv); `qa_gate.py check work/qa/story/manifest.tsv
  work/qa/story/verdicts` exits 0. Synopsis in `docs/synopsis.md`.
- **Next:**
  1. Visual QA gate (phase 8) not done: needs a warp-by-scene debug tool (only `tools/qa.py debugstart` dev menu exists;
     dev chapter-select in STARTBAK/START1.XT reaches every chapter, see `tools/review.py` CHAPTERS), tour sheets,
     visual-qa verdicts, `textcover.py`.
  2. Playtest reports via GitHub issues.
- **Known limits:** odd-length names give a double space before suffix pieces; brush-name FMV art kept.
- **Open bugs:** none.
- **Waiting on the user:** -
