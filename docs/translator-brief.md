# Translator brief - Eithéa (アイシア, PS1, Atlus/TamTam 2001)

You translate part of the Japanese script of Eithéa into English for a fan patch. Fantasy RPG with dating-sim
elements: high-school student Shou Niimi, his classmates and their teacher are pulled into the world of Eithéa after
an earthquake. Light-hearted banter, romance, some drama. Work only on the batch named in your dispatch.
Do all translation yourself; do not dispatch subagents. Do not edit any file except your output file.

## Read first
1. `docs/style-reference.md` - character voices and approved example pairs. Match this voice.
2. `build/batches/<batch>.terms.txt` - binding glossary rows for this batch. Full table: `glossary.md`
   (see "Speaker tags" and "Voices" sections there too).

## Input: `build/batches/<batch>.tsv`
`id<TAB>speaker<TAB>kind<TAB>limit<TAB>Japanese`. `\n` in the Japanese = line break inside one box.
kind: `msg` (message box, speaker shown in a name box), `choice` (player choice menu; one option per line),
`mono` (Shou's narrated monologue drawn as full-screen text). Rows are in script order: use neighbours for context.
Several consecutive msg boxes can be one sentence split across boxes: make the pieces read in sequence.

## Output: `build/batches/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Use `\n` for a line break inside a box.
- Font: fixed-width, plain ASCII only (straight quotes ' ", `...` for ellipses, `--` for dashes). Allowed extras:
  é (only in "Eithéa"), ~ (playful/drawn-out tone), ♪ and ♥ (only where the Japanese has them).
  Never use { } | ` or any Japanese/fullwidth/curly character.
- Limits (hard, the check enforces them): `msg` box = at most 3 lines of 46, 46, 44 characters. If the meaning
  needs more room, start a NEW BOX with `<p>` (e.g. `line1\nline2\nline3<p>line4`), which shows another box with the
  same speaker; the check tells you when `<p>` is not allowed. Never cut meaning to fit.
  `choice` = exactly as many lines as the Japanese, each <= 44 chars. `mono` = <= 48 chars per line, same or a few
  more lines than the Japanese.
- Inline codes: `<1>`..`<9>` are colour codes (`<3>name<8>` highlights a name, `<1>term<8>` a key term; `<8>` ends
  the colour). Keep every one of them, wrapped around the matching English word(s). `<10>` is a short pause: keep it
  where it fits the rhythm or drop it.
- Dry run: `python -X utf8 tools/batches.py fit "line one\nline two"` prints the characters per line.

## Validate
Run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every reported id until it prints OK.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese
  doesn't state; don't summarise or skip. Adapt jokes and wordplay so they still land (no translator notes).
- Natural, modern, conversational English; contractions; each character keeps their voice (style reference).
- Names and terms exactly as in the glossary. Never abbreviate a name or term to fit.
- Honorifics kept: -san, -kun, -chan, -sama, -sensei ("Yoshinaga-sensei", "Niimi-kun"); 先生 alone = "Sensei".
  Names Given Family ("Shou Niimi"). Long vowels in Japanese names as "ou" (Shou, Itou, Saitou).
- Punctuation: 『』 inside dialogue -> "..." quotes; ！！ -> `!!` is fine; ？！ -> `?!`; ……/… -> `...`;
  ～ at a word end -> `~` (or drop it); stuttering "a, ano" -> "U-Um".
- Sound effects/interjections: きゃあ -> "Kyaaah!", えっ -> "Huh?", ふう -> "Phew".
- Hitoshi speaks Kansai-ben: render as loose casual slang (dropped g's, "ya", "gonna"), not a regional US accent.
- Hermie's なのぉ verbal tic: soft trailing `~` on her sentences, childlike wording.
- Don't translate the speaker column; it is context.

## Notes from earlier batches (binding)
- Read the "Other names", "Elements and Artia", "Items" and "UI words" tables in `glossary.md` and use those forms.
- Choice menus are a grid: 3 rows per column. When a Japanese choice line holds TWO options (a second option after a
  run of full-width spaces), write column 1 (<= 24 chars), pad with spaces so column 2 starts at character 26
  (counting from the first letter of column 1), and keep column 2 <= 20 chars. Don't add leading spaces to options.
  The check enforces this.
- A stray `<8>` with no opening code exists in the source (e.g. "翔<8>"): keep it right after the same word.
- `???` speakers whose identity is clear from context: write them in that character's voice.
- Floor/area banners: plain text like "Moonlight Tower - Floor 3".

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`.
