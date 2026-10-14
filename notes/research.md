# Eithéa (アイシア) — research notes

## Game
- JP title **アイシア** (reading "Aishia"; official romanized logo **Eithéa**). Not エィシア/エイシア — search with アイシア.
- PS1, Atlus (publisher), TamTam (developer), 2001-02-22. 2 discs. RPG with heavy dating-sim/ADV elements, full voice.
- Releases: standard SLPS-03141/03142 (**our dump**, Rev 1), Limited/Deluxe Pack SLPS-03058/03059, Atlus Best Collection SLPM-87091/87092 (2002-06-13). Interactive DVD-PG version also exists.
- No English fan translation found (RHDN, cdromance, web search, 2026-10).
- Character design 七瀬葵 (Aoi Nanase). Scenario 岩田浩平, 小野洋一; scenario supervisor 庄司卓 (also wrote the novel). Atlus director 中村陽子. OP theme 「FLAME」 by 米倉千尋.
- Official guide: 『アイシア公式攻略ガイド』 (電撃攻略王, MediaWorks 2001, ISBN 4840218064, 127pp) — maps, monster data, ending system. Not online.
- Fan guide: ハッパ「アイシア完全攻略ツール」 (not found online); supplementary memo https://hepodeka.ashigaru.jp/eithea.html
- Cheat codes: https://w.atwiki.jp/ps_par/pages/27.html (403 to fetcher; open in browser — RAM addresses useful for flags/LAV).

## Story
High-school student 新見翔 (Shou), his classmates and their teacher are pulled into the other world アイシア after an earthquake at school. Three clans/peoples compete around the sacred エレの樹. Shou is the goddess-born guardian; party looks for a way home; romance with heroines, one confesses at the end. 10 chapters, ~1 dungeon + boss each; ch.1 mostly talk. ~14h. One ending per heroine.

## Systems (JP term → working EN)
| JP | Notes | Working EN |
|---|---|---|
| LAV (Latent Ability Voltage) | hidden morale/affection value per girl; changed by dialogue choices, castle talk; drives barrier strength, events, ending | LAV |
| RPS (リアルパートーシステム?) | party members talk to you while moving | RPS |
| ソウルリング | rings worn instead of armor; defense depends on LAV | Soul Ring |
| 陣形 / バリア / フォーム | formation sets facing/defense per direction; barrier lost when anyone falls | Formation / Barrier |
| TIP (銀の玉, also gold) | dropped by enemies; ammo for guns/bows, combined into 魔弾 | TIP |
| 魔弾 | magic bullets: element attacks, support, ailments, summon 陽神 | Magic Bullet |
| アーティア | magic artifacts (psxdatacenter: "Artia"); appears at last battle | Artia |
| エレの樹 | three sacred trees giving energy | Tree of Ele (TBD) |

## Places
- ユーロリア — 火竜族 capital, high tech, monarchy, unrest.
- イオピロス — 月光族 village, hunters.
- カーライル — neutral trade city, ruins underground.
- ヤムヤムの森 — northern sacred forest (third tree).

## Peoples
月光族 (Moonlight clan), 火竜族 (Fire Dragon clan), 夜夢族 (Night Dream clan) — EN TBD.

## Characters (name / age / role / VA)
Party: 新見翔 にいみしょう 17 hero, gun+karate (上田祐司) · 松岡ユカ 17 childhood friend, karate, claws/sword (今井由香) · 伊藤ひかる 16 Yuka's best friend, bow (菊池志穂) · 吉永秋穂 25 homeroom teacher, archery club advisor, bow (玉川紗己子) · ルー 17 月光族 gunner/huntress (三石琴乃) · ハーミー 12 夜夢族 mind reader, ends lines with 「なのぉ」 (大谷育江) · イムル=ルズ=ギ 18 火竜族 prince, sword (保志総一朗) · アルバイジャン ? merchant/researcher, makes 魔弾 (立木文彦).
Classmates (non-combat): 斉藤ヒトシ 17 (高橋広樹) · 高木学 17 photo club (高橋直純).
月光族: シャイ (Ruu's friend, archer) · ファンナ (chief's daughter) · エウリケ (high priestess) · ランドー (chief).
火竜族: ナムリア=ルズ=ギ (Imuru's sister) · レア=ルズ=ギ (queen) · ヴァムール (uncle, 銀河万丈) · オパス=ノウジ (guard captain, Namuria's fiancé) · アゼル (rebel leader = witch プラダ) · ユン=ゼフ.
夜夢族: カレン, ピエン, ポーポー. Other: マテリア (credited cast).
Goddess/witches: 女神 (of the エレの樹), ミュウ, プラダ, レディ (final boss → ファイナルレディ).
Romanization of ルー/ハーミー/イムル etc. is open: ask user (Ruu/Lou? Hermie/Harmie?).

## Disc layout (from ISO dir scan)
Both discs: `SLPS_031.4x` (boot, 546816 B), `EITHEA.EXE` (552960), `EITHEA1.EXE` (546816), `CD_DATA/BIND.DAT` (archive, 292MB/336MB) + `BIND.TBL` (index, ~63KB) + `FILE.LST`, `FILESIZE.DAT`, `DISKNO.DAT`, `MOVIE/OPEN1.STR` (opening FMV), `SECRET.BIN` (32MB, unknown/padding?). Disc 2 adds `XEND.XA` (126MB, ending voice/audio).
Text is likely inside BIND.DAT; voiced lines mean dialogue is text + XA, so text edits don't touch audio.

## Sources
- https://ja.wikipedia.org/wiki/アイシア_(ゲーム) (characters, terms; flagged as poorly sourced)
- https://megatenstaff.miraheze.org/wiki/アイシア (staff + cast)
- https://psxdatacenter.com/games/J/E/SLPS-03141.html
- https://www.ge-iroreview.com/ps/0a/aisia.htm (player reviews: systems, chapters, endings)
- https://hepodeka.ashigaru.jp/eithea.html
