# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8 (visual QA), then 9 (release). Last build: `work/build/` (2026-11-12, after polish pass; `work/build_e/` is older, stale).
- **Done:** engine, all 7,873 script rows + 1,050 EXE strings translated, graphics incl. English title logo, FMV
  captions, release tool. 2026-11-12: template layout; **story pass done** - 12 chapter files
  (`tools/review.py --chapters`, split per D9) all reviewed, Critical/Important fixed, re-checked;
  **polish pass done** - all `docs/polish.md` lines ticked (150 rows changed, item-get articles per D10), diff
  re-checked (`work/qa/story/polish_fixes.txt`, verdicts/polish.tsv); `qa_gate.py check work/qa/story/manifest.tsv
  work/qa/story/verdicts` exits 0. Synopsis in `docs/synopsis.md`.
- **Phase 8 tooling (2026-11-12, D11/D12):** `tools/debug/warp.py` (list | build N | state N | run SCENE | tour N):
  69 dev-menu scenes (d1: ch1-5, d2: ch6-10, finales, endings, epilogues), QA build `work/build_qa/` (dev menu on
  New Game, no voice, `--qa-cover`), states `work/states/devmenu_d<N>.sstate`, tours -> `work/qa/tour_d<N>/`,
  gate manifests `work/qa/d<N>/manifest.tsv` + `verdicts/`. Text coverage: `build.py --qa-cover` sets flag[990]=row+1
  before each block, `tools/lua/rowlog.lua` logs it, `tools/debug/cover.py work/qa/tour_d1` maps + runs textcover.
  Brief `docs/visual-qa-brief.md`. Small-window area labels widened + centred (asm/font.asm 4, `text.insert`).
- **Next:**
  1. Done 2026-11-12: world-map labels English (`gfx.world_map`: 8bpp page + rect table in ZENTAI.P/ZENTAI1.P,
     Moonlight Village/Fire Dragon Kingdom widened; checked in d1_5100/d1_6100 shots). All chapter cards now use
     `gfx.fill` (erase left halo ghosts on every card). ZENTAI1.P (IVENT02, `NON` overlay) not seen in-game yet.
     VRAM+RAM dumps: `--script tools/lua/vramdump.lua --var DUMP_AT=N`.
  2. 2026-11-12 round 2: both discs toured + reviewed (d1 48 ok, d2 85 ok); fixes committed (e81bc32: MONO
     orphan word, Fire Dragon Kingdom margin, save-slot "Shou's Level" gap [unverified in-game], exe wording).
     Rebuilt + re-toured after them; gates re-initialised: chunks `work/qa/d1/chunks/chunk_000.txt`,
     `work/qa/d2/chunks/chunk_000..004.txt` need visual-qa verdicts (`work/qa/d<N>/verdicts/r3_chunk_NNN.tsv`),
     then `qa_gate.py check work/qa/d<N>/manifest.tsv work/qa/d<N>/verdicts`. Tours aren't frame-deterministic, so
     every re-tour invalidates most verdicts: do fixes in batches. Reviewers flagged tour stalls (one line held
     ~4000 frames: d2_10130, d2_12040/12050/12060/12070/12090 IVENT90, d1_4120) = coverage gap, see item 3.
     (Old item 2 text:) Rebuild QA both discs (`warp.py build N` + `state N`), re-tour both (`tour N --frames 5400 --every 90`),
     `qa_gate.py init work/qa/d<N>/manifest.tsv work/qa/tour_d<N> --build work/build_qa/Eithea_disc<N>.bin`,
     dispatch visual-qa per chunk (d1 first round: 47 ok, issues = map labels, area labels [fixed], card patches).
     Disc 2 not toured yet. Voice-test scenes (d1_8888, d2_1858/3688/681) hang to timeout: drop or waive them.
  3. Text coverage: a 5400-frame mash tour reaches only a few rows per scene (events are slow); full coverage of
     8,002 rows needs either much longer tours per scene or waivers. Ask the user which (scope decision).
  4. Inkbox: choice boxes are left-aligned grids; title menu items sit on art (inkbox can't measure) - eyeballed ok.
  5. Playtest reports via GitHub issues.
- **Known limits:** odd-length names give a double space before suffix pieces; brush-name FMV art kept.
- **Open bugs:** none.
- **Waiting on the user:** -
