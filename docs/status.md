# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9 (release). Last build: `work/build_e/` (2026-11-12, after story-pass fixes).
- **Done:** engine, all 7,873 script rows + 1,050 EXE strings translated, graphics incl. English title logo, FMV
  captions, release tool. 2026-11-12: template layout; **story pass done** - 12 chapter files
  (`tools/review.py --chapters`, split per D9) all reviewed, Critical/Important fixed, re-checked;
  `qa_gate.py check work/qa/story/manifest.tsv work/qa/story/verdicts` exits 0. Synopsis in `docs/synopsis.md`.
- **Next:**
  1. Polish pass: `docs/polish.md` (~90 unticked Minors from the story pass; release refuses while any is unticked).
     Tick each `[x]` fixed or `waived: reason`. Fix by `tools/setrow.py`; re-run `review.py --chapters` + `qa_gate.py init`
     afterwards (changed chapters then need a new verdict file: a quick diff re-check like this session's
     `work/qa/story/fixes.txt` reviewer).
  2. Visual QA gate (phase 8) not done: needs a warp-by-scene debug tool (only `tools/qa.py debugstart` dev menu exists;
     dev chapter-select in STARTBAK/START1.XT reaches every chapter, see `tools/review.py` CHAPTERS), tour sheets,
     visual-qa verdicts, `textcover.py`.
  3. Playtest reports via GitHub issues.
- **Known limits:** odd-length names give a double space before suffix pieces; brush-name FMV art kept.
- **Open bugs:** none.
- **Waiting on the user:** -
