# Eithéa (アイシア) English translation

Unofficial English fan translation of **Eithéa (アイシア)**, Atlus / TamTam, PlayStation, 2001 (SLPS-03141 / SLPS-03142). Both discs.

**No game data is included.** Download the xdelta patches from the [latest release](../../releases/latest) and apply them to your own Redump (Rev 1) dumps. The release README lists the required hashes and patching steps.

## What is translated
All script text, menus, battle text, graphics text, the title logo, opening-movie cast captions, staff credits and the developer debug menu (hold L1+R1 on New Game). Voices stay Japanese. See the release README for known limits.

## Building from source
You need your own dumps unpacked under `rom/` and `work/` (gitignored). See `CLAUDE.md` for the commands and `notes/` for the engine, font hook and file-format research.

- `text/`: script rows (`text/xt/*.json`) and EXE strings (`text/exe.json`)
- `tools/`: extraction, insertion, graphics, font and release tools
- `asm/font.asm`: half-width font engine, name and strcat hooks
- `glossary.md`: naming rulings

Translation, tools and patch were produced with AI assistance (Claude, Anthropic) under the direction of the project owner. Original game © ATLUS / TamTam 2001.
