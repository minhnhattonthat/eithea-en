# Eithéa (アイシア, PS1, Atlus/TamTam 2001) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: its SKILL.md; `python tools/skill.py` prints the dir = `$SKILL`). Read it before ROM, text or QA work.
Names and style rules: `glossary.md`. Rulings with reasons: `docs/decisions.md`. RE notes: `docs/re/README.md`. Fonts: `docs/fonts.md`.

## Commands (repo root, `python -X utf8`)
- Setup once: `git config core.hooksPath tools/hooks` (pre-commit runs check). Unpack + identity: `tools/identity.py` (checks `rom.sha1`, fills `work/d<N>/`).
- Check: `tools/check.py` (pytest: pair codec, inline codes, script roundtrip, font hook; `SLOW=1` identity)
- Build: `tools/build.py N --english [--qa-novoice] [--marker] [--override NAME.TYPE=FILE] [--out DIR]` -> DIR/Eithea_discN.bin/cue
- Smoke: `$SKILL/scripts/emu.py work/build_e/Eithea_disc1.cue --out work/qa/smoke --bios tools/pcsx-redux/bios/SCPH-5500.bin --route tools/routes/boot.txt --frames 16000 --shot-every 60 --mash 200 --smoke`
- Debug menu: `tools/qa.py debugstart work/qa_START.XT` + build `--override START.XT=work/qa_START.XT` (New Game -> dev menu; battle test = right, down, circle; title menu needs ~13100 frames)
- Release: `tools/release.py 1.0` -> release/Eithea_EN_v1.0.zip (check, both discs, leftover-JP gate, xdelta3, re-apply verify). Never publish without the user.
- Clean: `tools/clean.py` (lists rebuildable files; `--yes` deletes). Disc space on H: is tight.

## Text pipeline
- Scripts: `tools/text.py` (XT 「」 blocks <-> `text/xt/*.json`; kinds msg/choice/mono; `<1>..<10>` codes, `<p>` extra box). Limits: msg 46/46/44 x3 lines, choice 44 (2-column grid: col 2 at char 26), mono 48.
- Batches: `tools/batches.py split|check|merge`, `tools/terms.py`, briefs in `docs/` (translator, reviewer, exe). Polish: `tools/polish.py`. Single row: `tools/setrow.py ID "text"`.
- EXE strings: `tools/exetext.py` (`text/exe.json`, in place, padded with 0x8140; `raw:` = plain SJIS for BIOS-drawn text).
- Font: `tools/font.py` + `asm/font.asm` (2 chars per SJIS-safe code, hook in glyph blitter; battle name-copy fix).
- Graphics: `tools/gfx.py` (name box FONT3A + EXE u/v/w, title logo + menu, chapter/info cards, result, option, album, buttons, note, prologue incl. PROLOG.NM copies, MONO*.P pages). FMV: `tools/fmv.py` (jPSXdec partial replace).

## Paths / disc facts
- `rom/` originals (Redump Rev 1, SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`); `work/d<N>/tree` + `bind/` unpacked (gitignored). Emulator: `tools/pcsx-redux/` (gitignored). Savestates: `work/states/`.
- EITHEA.EXE = game; SLPS/EITHEA1 = boot (logos, prologue, FMV; endings exec it). BIND.DAT/TBL archive; scripts .XT plain cp932.

## Rulings
- Edit source files (.py .lua .asm .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: use the plugin types `translate-retro-game:<type>` (Claude Code), `.codex/agents/` or `.opencode/agents/`, never general-purpose.
- Read `docs/decisions.md` before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, update `docs/status.md`.
- PCSX-Redux hangs on the first voice: QA builds use `--qa-novoice`. Cold boot after every rebuild (savestates hold old RAM).

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
