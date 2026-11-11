# Reverse-engineering notes

One file per subsystem. Mark every finding with how far it is proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely. Promote it to verified before code depends on it.

Addresses are for the dumps in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| `research.md` | earlier patches, docs, game facts | sources |
| `recon.md` | disc layout, BIND.DAT/TBL, XT scripts, EXE, graphics assets and provenance | verified (identity build, roundtrip tests) |
| `engine.md` | English text engine: SJIS 2-char codes, glyph blitter hook, strcat/name fixes | verified (in-game, `tests/test_hook.py`) |
| `../tl_reports.md` | translator/reviewer batch reports | log |
