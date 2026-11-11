# Eithéa (アイシア) English translation

Unofficial English fan translation of **Eithéa (アイシア)**, Atlus / TamTam, PlayStation, 2001 (SLPS-03141 / SLPS-03142). Both discs.

**No game data is included.** Download the xdelta patches from the [latest release](../../releases/latest) and apply them to your own Redump (Rev 1) dumps. The release README lists the required hashes and patching steps.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue / story, choices, monologues (both discs) | Translated |
| Menus, items, equipment, magic bullets, monsters, battle text | Translated |
| Title logo and menu, chapter cards, other graphics text | Translated (a few pieces of in-world artwork stay as drawn) |
| Opening movie | Partly translated (cast captions in English; the animated brush-written names stay as drawn) |
| Staff credits | Translated (staff name readings are best effort) |
| Developer debug menu (hold L1+R1 on New Game) | Translated |
| Voice acting | Left in Japanese (spoken audio; the text is English) |

Known issues: none known, but scenes after the first chapter's opening were checked with the text tools, not played through; [report one](../../issues/new/choose).

## What's here

| Path | What it is |
|---|---|
| `text/` | Script rows (`text/xt/*.json`) and EXE strings (`text/exe.json`): Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: unpack, extract, insert, font, graphics, release. |
| `asm/font.asm` | Half-width font engine, name and strcat hooks. |
| `tests/` | pytest suite (disc-dependent tests skip when the dumps are absent). |
| `docs/re/` | Reverse-engineering notes (engine, font hook, file formats). |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.codex/agents/`, `.opencode/agents/` | Subagent types for Codex and opencode; Claude Code gets them from the plugin. |

## Build your own patched discs

Needs Python 3.12+, Windows (mkpsxiso, armips and jPSXdec go under `tools/`) and your own Redump Rev 1 dumps:

```sh
# copy your dumps (.bin + .cue) to rom/:
#   Eithea (Japan) (Disc 1) (Rev 1).bin  408001440 bytes, SHA-1 47541f3bd8c53ad4b272861955b14ec1d73b0fa1
#   Eithea (Japan) (Disc 2) (Rev 1).bin  603981840 bytes, SHA-1 ba3368060fd044722f7f82cc512dcb9b0d28b75f
#   (the build refuses any other dump, see rom.sha1)
python -X utf8 tools/identity.py                     # unpack to work/d1, work/d2 and verify a byte-identical rebuild
python -X utf8 tools/bind.py unpack work/d1/tree/CD_DATA/BIND.TBL work/d1/tree/CD_DATA/BIND.DAT work/d1/bind  # same for d2
python -X utf8 tools/build.py 1 --english --out build # -> build/Eithea_disc1.bin/.cue
python -X utf8 tools/check.py                        # tests
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

Translation, tools and patch were produced with AI assistance (Claude, Anthropic) under the direction of the project owner. Original game © ATLUS / TamTam 2001.
