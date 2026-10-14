# Eithéa (アイシア, PS1, Atlus/TamTam 2001) JP→EN

Skill: `H:/translation/eithea/.claude/skills/translate-retro-game/SKILL.md` (read before work). `$SKILL` = that dir.
Rulings and names: `glossary.md`. Research: `notes/research.md`. Engine/recon: `notes/recon.md`. Engine design: `notes/engine.md`.

## Commands (run from repo root, `python -X utf8`)
- check (pre-commit): `tools/check.py` (pytest: pair codec, inline codes, script roundtrip; `SLOW=1` identity)
- build: `tools/build.py N --english [--qa-novoice] [--marker] [--override NAME.TYPE=FILE] [--out DIR]` → DIR/Eithea_discN.bin/cue
- release: `tools/release.py 1.0` → release/Eithea_EN_v1.0.zip (check, both discs, leftover-JP gate, xdelta3, re-apply verify)
- smoke/QA: `$SKILL/scripts/emu.py work/build_e/Eithea_disc1.cue --out work/qa --bios tools/pcsx-redux/bios/SCPH-5500.bin --route work/exp1b/route.txt --frames 16000 --shot-every 60 --mash 200`
- QA debug menu: `tools/qa.py debugstart work/qa_START.XT` + `--override START.XT=work/qa_START.XT` (New Game → dev menu; battle test = right, down, circle; title menu needs ~13100 frames)

## Text pipeline
- Scripts: `tools/text.py` (XT 「」 blocks ↔ `text/xt/*.json`; kinds msg/choice/mono; `<1>..<10>` codes, `<p>` extra box). Limits: msg 46/46/44 ×3 lines, choice 44 (2-column grid: col 2 at char 26), mono 48.
- Batches: `tools/batches.py split|check|merge`, `tools/terms.py`, briefs in `docs/` (translator, reviewer, exe). Polish rules: `tools/polish.py`. Single row: `tools/setrow.py ID "text"`.
- EXE strings: `tools/exetext.py` (`text/exe.json`, in place, padded with 0x8140; `raw:` = plain SJIS for BIOS-drawn text).
- Font: `tools/font.py` + `asm/font.asm` (2 chars per SJIS-safe code, hook in glyph blitter; battle name-copy fix).
- Graphics: `tools/gfx.py` (name box FONT3A + EXE u/v/w, title menu, chapter/info cards, result, option, album, buttons, note, prologue incl. PROLOG.NM copies, MONO*.P monologue pages). FMV: `tools/fmv.py` (jPSXdec partial replace).

## Paths / disc facts
- `rom/` originals (Redump Rev 1), `work/d<N>/tree` + `bind/` unpacked (gitignored). Disc space on H: is tight: delete old work/build_* dirs.
- EITHEA.EXE = game; SLPS/EITHEA1 = boot (logos, prologue, FMV; endings exec it). BIND.DAT/TBL archive; scripts .XT plain cp932.
- PCSX-Redux hangs on the first voice: QA builds use `--qa-novoice`. Cold boot after every rebuild (savestates hold old RAM).

## Status (2026-10-14)
- Done: engine, all 7,873 script rows + 1,050 EXE strings translated (44 agent batches + 4 EXE batches, sampled review, fixes), graphics, FMV captions, release tool.
- Known limits: odd-length names give a double space before suffix pieces; title logo and brush-name FMV art kept; debug menus Japanese.
