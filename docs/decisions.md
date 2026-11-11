# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-10-14 | Honorifics and name order | keep (-san), drop; JP or Western order | Honorifics kept (-san, -kun, -chan, -sama, -sensei; 先生 alone = "Sensei"); Given Family order (Shou Niimi) |
| D2 | 2026-10-14 | Romanization source for names | official art, earlier patch, Hepburn | Translator's choice, Hepburn-style, long vowels as "ou" (Shou, Itou, Saitou); ルー = Lou |
| D3 | 2026-10-14 | Credits | stay Japanese, translate | English, graphic credits too |
| D4 | 2026-10-14 | Abbreviations | engine work first (default), abbreviate | Full names/terms, no abbreviations; no suffix glued to variables; jokes keep punch |
| D5 | 2026-10-14 | Graphics text left in Japanese | none (default), list | None by default (titles, menus, banners in scope); brush-written FMV names kept as drawn |
| D6 | 2026-10-14 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through checkpoints, report at end |
| D7 | 2026-10-14 | Saves provided | yes, none | None; late scenes need route/emulator input |
| D8 | 2026-11-12 | Albaijan's spelling (agent ruling, story pass) | dropped g's/"ya" (some files), standard (most files) | Standard spelling; gruff via word choice ("ain't", "gotta" ok). Dropped g's/"ya" stay Hitoshi's marker (glossary voices) so the two don't blur |
| D9 | 2026-11-12 | Story-pass chapter split (agent ruling) | by file prefix, by script graph, by dev chapter-select | Dev chapter-select (STARTBAK/START1.XT) entry scripts -> `tools/review.py` CHAPTERS; IVENT in number order, then field scripts |
| D10 | 2026-11-12 | Item-get article (agent ruling, polish pass) | mixed "Got <item>" / "Got a <item>" | "Got a/an" for countable items, "Got some" for liquids/bread, no article for Artia, CAN, unique named items; "the" only for story items (Book, pendants, Eletia); always "Got", not "Obtained" ("Received" kept for 手渡された) |
