# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9 (release); phase 8 gates pass. Last build: `work/build/` (2026-11-12, after polish pass; `work/build_e/` is older, stale).
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
- **Phase 8 gates pass (2026-11-12, round 4):** `qa_gate.py check work/qa/d<N>/manifest.tsv work/qa/d<N>/verdicts`
  exits 0 for both discs (d1 51 sheets ok; d2 89 ok, build afb71a9d waived: gfx.mono hotfix re-checked in spot runs).
  Round 3 was void: a Ch.10 save on the shared emulator card turned New Game into Load; `warp.py` now passes a fresh
  blank card (`work/qa/blank.mcd`) to every run. Round 4 fixes: IVENT70:0003 "big brother"; MONO split cuts snap to
  the JP paragraph gap (stray dash on "few hours." page); MONO4 "But I only ever..." block wraps past u=255 (8-bit
  u) - left-edge strip erased, text fits the real box (was clipped both sides). Coverage waived (D13).
  Gotchas: `qa_gate init` gives newly added ids credit for old verdicts with the same id - move old verdicts out
  (`verdicts_old/`) after a broken tour; delete stale sheet_N.png from earlier tours before init.
- **Next:**
  1. Phase 9: `release/Eithea_EN_v1.0.zip` built 2026-11-12 (check, leftover-JP gate, xdelta re-apply all pass;
     README TESTING updated). Shipped patches applied to rom/ originals match the README SHA-1s and both boot
     (d1 prologue, d2 "swap for DISC 1"). Note: release.py deletes the built .bin - smoke the re-applied patch.
     **Waiting on the user: publish or not.**
  2. Known tour defects, not text bugs: d1_4090 lands on the same scene as d1_4050 (dev-menu path?); d2_11010 mash
     saves to the blank card and sticks on "Overwrite?"; voice-test scenes time out; ending variants share openings.
  3. Inkbox: choice boxes are left-aligned grids; title menu items sit on art (inkbox can't measure) - eyeballed ok.
  4. Playtest reports via GitHub issues.
- **History (round 1-3 notes):**
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
- **Known limits:** odd-length names give a double space before suffix pieces; brush-name FMV art kept.
- **Open bugs:** none.
- **Waiting on the user:** publish decision for v1.0 (zip is local only).
