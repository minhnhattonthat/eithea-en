# Recon (Phase 1) — Eithéa PS1

## Disc / archive
- Identity build OK (`tools/identity.py`). Boot EXE `SLPS_031.41/42` == `EITHEA1.EXE` (identical on disc 1); `EITHEA.EXE` differs. Load 0x80010000, size 0x85000.
- `CD_DATA/BIND.DAT` + `BIND.TBL`: TBL = 13-byte entries (name[8], type[2], size[3 big-endian]); files back to back, each padded to 2048. 4874 files (disc 1), 4995 (disc 2). `tools/bind.py` unpack/pack, strict byte roundtrip passes on both.
- Types: XT script text (130), B (3306, binary: voices V*/VL*/VT*, SE, BGM), IM TIM images (322), NM/NC/ND/P map/anim data, EQ/H sound seq, IN/BL font (KANJI.IN glyphs + KANJI.BL charset), NI/NN system data.
- Voices are `.B` files (e.g. VL001.B), referenced from scripts; voices stay Japanese.

## Scripts (`*.XT`) — the main text
- Plain Shift-JIS (cp932), CRLF, interpreted at runtime from a RAM buffer. Commands: `open_meswindow`, `close_meswindow`, `hcls [VLnnn]`, `hitret`, `voice X`, `voice_start X`, `voice_wait`, `message_speed N`, `command_select N`, `select_jump a,b,..`, `map_change ...`, `flag[n] = v;`, `if (`, `goto N`, `change FILE.TXT`, `*****NNN` labels, `;` comments, trailing Japanese comments after tabs.
- Dialogue: `〈Speaker〉` line then `「text` ... `」` over up to 3 lines ≈ 20 fullwidth chars/line; window shows 2 lines + name box above. Inline control chars: `③name⑧` / `①word⑧` (colour start/end). Hitoshi speaks Kansai-ben.
- Speaker names ALSO appear in the EXE table at 0x80010ac4.. (ひかる, ヒトシ, アルバイジャン ...), and magic-bullet descriptions in EXE (0x80010f24..): ~1195 SJIS strings, ~11.7k chars in `SLPS_031.41`; see work/exe_strings.txt (regenerate).
- Debug/chapter-select scripts exist (START1.XT etc.) — handy for reaching scenes in QA (`change X.TXT`).
- Scale: disc 1 ~143k chars of text in 124 XT files + IVENT04.AK (5k).
- Command-name table in EXE at 0x8007a3e4 (93 pointers); lookup function 0x80024a5c; interpreter at ~0x80024c90.

## Font
- Message font = KANJI.IN (glyph per char of KANJI.BL; 1720 chars = every char used in the game, in order of first appearance). A test render as 16x24 1bpp looked correct. FONT*.IM = UI TIM textures (partly English already: Attack/LAV/Sold/Menu/Status/Equip/Item...), halfwidth ASCII + katakana glyph sets for UI.
- TODO: confirm how the message engine handles ASCII; whether glyph set is closed (needs new glyphs appended to KANJI.IN/BL + code to map).

## Engine findings (EITHEA.EXE = the game; SLPS_031.41 == EITHEA1.EXE = boot/title program, same interpreter; identical on both discs)
- Slot loader `0x8003003c(slot, name)`; KANJI.TBL (=BIND `KANJI.BL`) lands at 0x80117000, KANJI.BIN (=`KANJI.IN`) at 0x80118000 (pointer table at 0x800e6df0+0x5c/+0x64).
- **KANJI.BL** = list of 2-byte big-endian SJIS codes (terminated by 0xFF). Glyph index = position. **KANJI.IN** = 48 bytes/glyph: 12 rows x 2 bytes x 2 bitplanes (planes 0x18 apart; 4 colour levels incl. outline), 12x12 px. (My first 1bpp 16x24 render was wrong.) Capacity buffer: ~0x15800 bytes before the script buffer at 0x8012d800.
- Glyph blit `0x800367d4(x,y,sjis,buf,...)`: finds the code in KANJI.BL (linear search), expands 2 planes to a 12x14 4bpp cell in `buf` (+0x54 bytes per cell). Callers 0x8002947c, 0x80029950, 0x80029b64, 0x80036b2c, 0x80036f84.
- **String print `0x80036958(x,y,str,...)`** (65 callers: message window, menus, etc.): per char: `\n` -> x=start, y+=14; space (0x20) -> x+=6; `\r\n`; codes 0x8740..0x8748 (①..⑨ etc.) set colour state (s3); 0x8140 (full-width space) = no glyph; **everything else is read as a 2-byte code**, drawn as a 12px cell and uploaded to VRAM (x/4+0x340, y+0x100, w=3 halfwords, h=14) via `0x8006c414`; x advances 12. => halfwidth ASCII does NOT render today (verified in-game, exp1); full-width Latin only renders if the glyph is in KANJI.BL/IN.
- Message window: name box above (name from `〈..〉`), text area ~292 px wide: 24 full-width chars/line, 3 lines; VWF English would give ~50 chars/line.
- Plan: patch the print routine (both EXEs) to render ASCII with a variable-width font into a pixel-accurate line buffer, upload only touched 4px-aligned columns; font+width table + code hosted in free memory (zero runs at 0x800949f1 (0x106b bytes), 0x80095d5c (0x451), 0x800921bb (0x2f5) in EITHEA.EXE - must verify with a write watchpoint that nothing writes there; or load a new BIND file into a verified-free RAM region).
- No free RAM beyond EXE end (0x80096800..0x800c0000 is BSS in use); large zero RAM areas exist at runtime (e.g. 0x80182000, 0x801aa000) but unverified across modes.

## Graphics text found so far
- Opening FMV `MOVIE/OPEN1.STR`: red Japanese story text burned into video (needs STR subtitle/replace).
- Title logo: `ROGO.IM`; menu 最初から始める / 続きから始める / オプション: separate `ROGO0.IM`. Both now replaced in English builds.
- Staff/ending credits, chapter title cards, map names: TBD survey.

### English title logo (2026-10-18)

- Source: BIND entries `work/d1/bind/1344_ROGO.IM` and `work/d2/bind/1433_ROGO.IM`, byte-identical (77,344 bytes). TIM is 320×240, 8bpp, one 256-colour CLUT; VRAM rect `(320, 0, 160, 240)` in 16-bit words. Pixel data starts at byte 544. Searching every unpacked BIND member on both discs for the complete pixel block found only these two files, no embedded copies.
- `tools/title_logo.png` is the masked 258×116 RGBA English artwork, placed at `(32, 18)` by `gfx.title_logo()`. The blue katakana and its shadow are replaced with glossy, beveled **Eithéa**, including the acute accent. The plank and its gold English inscription are redrawn where the removed stems exposed them. The surrounding forest, lower sky, and menu area outside the mask stay original.
- Artwork was made with the built-in imagegen tool, using the decoded original as an edit target. Prompt: replace only the large アイシア with exact “Eithéa”; match icy blue glossy bevels, dark navy extrusion, cyan-white highlights, bold slightly italic fantasy letters, and the original approximately `(36,20)..(285,125)` footprint; retain the wooden plank, its gold English inscription, forest canopy, sky, rays, and 4:3 framing; reconstruct exposed background, with no extra text or ornaments. The generated edit was Lanczos-downsampled to 320×240, masked to the union of the old/new title and plank, then cropped to the checked-in PNG. Builds use this fixed asset; no image-generation service is needed.
- `title_logo` is in `gfx.SECTIONS`, so both `gfx.all_files("d1")` and `gfx.all_files("d2")` return `ROGO.IM` for `tools/build.py --english`. Existing `save()` requantizes to the original CLUT without dithering. Verified both outputs retain the exact size, TIM headers, CLUT and VRAM rect, all indices remain below 256, and every index outside the alpha mask is unchanged (21,018 changed pixels).
- QA: `python -X utf8 tools/check.py`: **9 passed, 1 skipped**. Disc 1 built with `python -X utf8 tools/build.py 1 --qa-novoice --english --out work/build_logo`. Cold boot with SCPH-5500, route `10800 -;4 circle;2300 -`, 13,100 frames, screenshots every 300: exit 0, smoke passed, English title/menu visually inspected. Final screenshot: `work/title_logo_title.png`. Temporary build/run directories removed after QA. Disc 2 asset generation checked; disc 2 was not built or booted.
- Environment gotcha: the old `.claude/skills/translate-retro-game/scripts/emu.py` path is absent in this checkout. Used the installed plugin's `C:/Users/Nathan/.claude/plugins/marketplaces/retro-translation/skills/translate-retro-game/scripts/emu.py` with the same route/BIOS/frame arguments plus `--smoke --sheet`. This path migration belongs in the skill's `references/emulator-qa.md` setup guidance. The opening FMV's separate Japanese title artwork is outside this title-screen texture change.

## Emulator QA notes
- PCSX-Redux headless: first `voice_start`/`voice_wait` never completes (voice end not detected) → game hangs. `tools/build.py --qa-novoice` strips voice commands from XT scripts for QA builds only.
- Savestates are only valid on the exact disc layout; rebuilt discs need cold boot. Cold boot to title ≈ 10800 frames at 8x; ○ (circle) confirms.
- Route for new game: `10800 -;4 circle;300 -;4 circle;300 -;4 circle;300 -;4 circle;600 -` then mash circle.
