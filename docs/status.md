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
  1. World map place labels still Japanese (エレの樹, 月光族の村, イオピロスの塔, カーライルの町, 火竜族の王国, 王国): in
     ZENTAI.P / ZENTAI1.P (d1) / C0LMAP.ND, shown by `map_change 999,ZENTAI.MP,...,C0LMAP.AND` (IVENT20, IVENT29).
     Survey + redraw (gfx.py, like MONO*.P pages). Also check the Ch.4 card ("Carlyle, the Neutral City", d1_5100
     tiles 2-3) for pale patches from erased lettering against the original.
  2. Rebuild QA both discs (`warp.py build N` + `state N`), re-tour both (`tour N --frames 5400 --every 90`),
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
