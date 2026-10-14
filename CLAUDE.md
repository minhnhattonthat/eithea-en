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

## More tools
- `tools/bind.py` (BIND pack/unpack), `tools/build.py N [--qa-novoice] [--override NAME.TYPE=FILE]` (rebuild disc; QA builds strip voice cmds because PCSX-Redux hangs on the first voice), `tools/tim.py`, `tools/mipsscan.py`, `tools/lua/*.lua` probes. Details: `notes/recon.md`.
- Rebuilt discs need a COLD boot in emu.py (savestates break); route to new game in notes/recon.md.

## Status
- Done: Step 0 setup, original smoke boots, identity build byte-identical on both discs.
- Done (Phase 1 mostly): BIND format + roundtrip, scripts are plain cp932 text, font format, print routine found (notes/recon.md).
- Next: (a) extract XT scripts + EXE strings to a translatable format with roundtrip test; (b) engine patch: VWF ASCII in print routine 0x80036958 (armips, host code in verified-free memory); (c) graphics-text survey (OPEN1.STR subtitles, title, credits, UI TIMs); (d) width gate, marker build.
- Rulings: specs pre-approved (report at end). No user saves. Given Family names.
- Open: none yet.
