# Eithéa (アイシア, PS1, Atlus/TamTam 2001) JP→EN

Skill: `H:/translation/eithea/.claude/skills/translate-retro-game/SKILL.md` (read before work). `$SKILL` = that dir.
Rulings and names: `glossary.md` (Lou, honorifics kept, English credits, full names, no abbreviations). Research: `notes/research.md`.

## Commands (run from repo root, `python -X utf8`)
- check (pre-commit): `python -X utf8 tools/check.py` (pytest; `SLOW=1` adds identity test)
- identity: `python -X utf8 tools/identity.py [1|2]` → dumpsxiso + mkpsxiso, sha1 vs original
- smoke: `python -X utf8 $SKILL/scripts/emu.py "rom/Eithea (Japan) (Disc 1) (Rev 1).cue" --out work/smoke --bios tools/pcsx-redux/bios/SCPH-5500.bin --frames 2400 --shot-every 600 --smoke --sheet`
- build / release: not written yet

## Paths
- `rom/` originals (2 discs, Redump Rev 1, SLPS-03141/03142), gitignored. `work/d<N>/tree` unpacked disc, `layout.xml`.
- `tools/` third-party (gitignored): pcsx-redux (+bios/), mkpsxiso 2.30, jpsxdec, armips, quickbms, psximager.
- Emulator: PCSX-Redux headless; BIOS SCPH-5500 (JP).

## Disc facts
- Each disc: boot `SLPS_031.4x`, `EITHEA.EXE`, `EITHEA1.EXE` (all ~546-552 KB), `CD_DATA/BIND.DAT` (archive) + `BIND.TBL` (13-byte entries: 8-char name, 2-char type, 3 bytes unknown), `FILE.LST`, `MOVIE/OPEN1.STR`, `SECRET.BIN` 32 MB. Disc 2 adds `XEND.XA`.
- BIND.DAT starts with a script-like text (`pic_feed X.TIM`, `disk_change 1`, `hitret`) — event scripts live there.

## Status
- Done: Step 0 setup, original smoke boots, identity build byte-identical on both discs.
- Next: Phase 1 recon: decode BIND.TBL entries, find text/script encoding, font, graphics text survey.
- Open: none yet.
