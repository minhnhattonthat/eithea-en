# English text engine (asm/font.asm, tools/font.py)

- The script reader (0x8002b2f4) drops ASCII bytes and matches command keywords anywhere, so English must be stored
  as valid 2-byte SJIS. Each code holds TWO characters: lead 0x88..0x9F/0xE0..0xFC, trail 0x40..0xFC (no 0x7F).
  first-char index = 2*lead_index + (trail_index >= 94), second = trail_index % 94; chars = ASCII 0x20..0x7D,
  with { } ` | repurposed as ♪ ♥ é ~.
- Glyph blitter 0x800367d4: the KANJI.BL search block is replaced by a call into code living inside KANJI.IN
  (prepended block: 106 half glyphs × 24 bytes, 48-byte scratch glyph, ext code; KANJI.BL gets matching dummy
  entries so Japanese glyph indices still line up). Codes < 0x8800 still use the original search (kana, symbols,
  ①..⑩ colour codes survive). The half glyphs are composed into the scratch cell: out = A | B >> 6.
- Every message/menu/name path uses this blitter: one hook covers the game. 12 px per code = 6 px per char,
  48 chars per line; message box shows 3 lines (4th dropped), page icon covers the end of line 3.
- Battle prompt names (switch at 0x800627d0) used inlined fixed-length copies; cases 0 (翔) and 3 (秋穂) now jump
  through EXE stubs to a NUL-terminated copy in the ext code (strings Shou/Akiho at the end of the ext block).
- Name box = sprite from FONT3A.TIM chosen by speaker id (if-chain at 0x8002a3e4 sets u/v/w); 〈name〉 tags in scripts
  must stay Japanese (strcmp against the EXE list).
- Choices: command_select draws the cursor on a grid (3 rows per column, column 2 at x+156 px = cell 13).
- Load delay: after `lw` the next instruction can't use the register (armips warns).
