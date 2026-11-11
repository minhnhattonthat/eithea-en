# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| `tools/font.py` (glyph table in code) | drawn for this project | MIT, same as repo | yes | 5x10 half-width dialogue/menu font (KANJI.IN) | - |
| `C:/Windows/Fonts/tahoma.ttf`, `tahomabd.ttf`, `arialbd.ttf`, `Inkfree.ttf` | Windows system fonts | Microsoft font EULA | as rendered bitmaps only (no font file ships) | `tools/gfx.py` graphics text: title menu, chapter cards, option, album, buttons, note | rendered at fixed sizes, haloed |
