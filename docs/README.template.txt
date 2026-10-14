Eithea (Aishia) - English Translation Patch v{VERSION}
=====================================================

Unofficial fan translation of "Eithea" (Aishia), Atlus / TamTam, PlayStation, 2001.
This archive contains patches only. No game data is included; you need your own copy of the game.
Do not ask for or distribute pre-patched images.

WHAT IS TRANSLATED
- All story dialogue, choices and monologues on both discs (about 7,900 script boxes).
- Menus, items, equipment, magic bullets, monsters, battle messages, save/load and memory card messages.
- Name boxes, title menu, chapter cards, battle results, option and album menus, button hints.
- The boot prologue, the opening/ending monologue screens, and the cast captions in the opening movie.
- Staff credits (names romanized in the usual given-name family-name order).
Character names keep their Japanese honorifics (-san, -kun, -sensei...).

KNOWN LIMITATIONS
- Spoken voice acting stays Japanese (text is English).
- The title logo, the stylized brush-written names that animate in the opening movie, and a few
  pieces of in-world artwork stay as drawn.
- Text uses a fixed-width 6 px font.
- Staff name readings are best effort; corrections welcome.

REQUIRED FILES (Redump, Rev 1)
{HASHES}
HOW TO PATCH
1. Use xdelta3 (or Delta Patcher / xdelta UI on Windows).
2. Apply Eithea_EN_v{VERSION}_Disc1.xdelta to "Eithea (Japan) (Disc 1) (Rev 1).bin"
   and Eithea_EN_v{VERSION}_Disc2.xdelta to "Eithea (Japan) (Disc 2) (Rev 1).bin".
   Command line: xdelta3 -d -s "original.bin" "patch.xdelta" "patched.bin"
3. Keep your original .cue file for each disc; edit the FILE line to point at the patched .bin
   (or rename the patched .bin to the original name).
4. Check the patched CRC32 / SHA-1 against the values above.

DEBUG MENU (developer tool, translated)
Hold L1 + R1 while you choose New Game on the title screen (keep them held until the loading screen
appears). The developer menu opens instead of the prologue: start a chapter or scene directly, test
battles, check voices and character expressions. It was never meant for players: jumping into the
middle of the story skips events and can leave flags unset, so don't save over a real game with it.
Disc 2 has its own list (chapters 6-10, endings and epilogues).

TESTING
Checked in PCSX-Redux (SCPH-5500 BIOS): boot, prologue, opening movie, the first chapter's opening
scenes, field menus and a battle. Later scenes were checked with the text tools (line widths, codes),
not played through. Start from a cold boot (not a savestate made with the Japanese game).
Bug reports with a screenshot or savestate are welcome.

CREDITS
Translation, tools and patch: produced with AI assistance (Claude, Anthropic) under the direction of
the project owner. Original game (c) ATLUS / TamTam 2001.
