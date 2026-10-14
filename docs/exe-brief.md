# EXE strings brief - Eithéa

You translate UI strings from the game program (menus, item/monster names, descriptions, battle messages, staff
credits). Work only on the batch named in your dispatch; do all the work yourself; edit only your output file.

## Read first
- `glossary.md` (rulings, Terms, Items, Elements, UI words, Speaker tags). Dialogue already uses many item and place
  names: before inventing an English name, search the translated scripts for the Japanese term
  (`grep -l "傷薬" text/xt/*.json`, then read the matching row's `en`) and reuse that English exactly.

## Input: `build/batches/<batch>.tsv`
`address<TAB>limit<TAB>area<TAB>Japanese`. `area` says what kind of string it is. Rows are in program order:
neighbours belong together (a menu, a list of names, a description table).

## Output: `build/batches/<batch>.out.tsv` (file-write tool, not a shell heredoc)
`address<TAB>English`, every input address once, same order. One line per string (no `\n`).

## Hard rules (the check enforces them)
- At most `limit` characters (each Japanese character is 2 English characters wide on screen, so `limit` is
  exactly the original on-screen width). Plain ASCII; extras é ~ ♪ ♥ only. No { } | `.
- Keep inline codes `<9>` etc. exactly where they are (usually the very start).
- Never abbreviate a name or term from the glossary. If a name truly can't fit, report it as `LONG:`.

## Layout rules
- Full-width spaces (　) inside a string are layout. One full-width space = 2 English spaces. When a string holds
  several items in columns (`はい　　　いいえ`, `作成しますか？　　　　はい　　　いいえ`, `必要人数：３`), every item
  must start at the same screen position: a Japanese item starting at character k starts at English character 2k.
  The game puts a cursor at fixed positions, so this matters.
- Leading full-width spaces (indent/centering): keep the same visual indent (2 spaces each), or re-centre within
  the limit for titles.
- Fixed-width name fields (monsters, items): just the name; the tool pads it.
- Message pieces the game glues to a name (they start with a particle: は、 を が の に): translate so that
  name + piece reads as English, keeping the piece order. E.g. `を倒した！` after an enemy name -> ` was defeated!`
  (leading space), `は、` + item + `を使った！` -> ` used ` + item + `!`. Look at neighbouring pieces.
- Staff credits: one 42-char line each, centred with spaces like the original. Role titles in English
  (シナリオ -> Scenario, プログラム -> Program, 原画 -> Original Art...). People's names: Given Family, plain Hepburn
  without macrons or "ou" (中村 陽子 -> Yoko Nakamura, 庄司 卓 -> Taku Shoji); for voice actors use their usual
  English spellings (上田祐司 -> Yuji Ueda). Company names in their usual English form (株式会社アトラス -> ATLUS CO., LTD.).
  Character names in the cast list come from the glossary.
- 予備 (unused spare slot) -> "Spare". デバッグ用 strings are debug-only: translate literally.

## Validate
`python -X utf8 tools/exetext.py check <batch>` from the repo root; fix until it prints OK.

## Report (reply with only this)
File and entry count; then `NEW TERM: jp -> en`, `UNSURE: address - note`, `LONG: address - note`.
