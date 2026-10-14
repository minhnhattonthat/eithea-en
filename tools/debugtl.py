"""English for the developer debug menus (DEBUG, START1, STARTBAK, BAT_TEST, BAST_CHK).
  python -X utf8 tools/debugtl.py        -> build/batches/dbg.out.tsv  (then: batches.py check dbg / merge dbg)
Each row is a list of lines; a line is 'text' or ('column 1', 'column 2') (column 2 starts at character 26).
"""
import pathlib

root = pathlib.Path(__file__).resolve().parent.parent
X = ""   # an empty (blank) menu line

ROWS = {
    # --- BAST_CHK: portrait / expression viewer
    "BAST_CHK:0000": [("Shou", "Akiho"), ("Yuka", "Lou"), ("Hikaru", "Next")],
    "BAST_CHK:0001": [("Imul", "Namuria"), ("Hermie", "Azel"), ("Albaijan", "Next")],
    "BAST_CHK:0002": [("Manabu", "Fanna"), ("Hitoshi", "Eurike"), ("Rando", "Next")],
    "BAST_CHK:0003": [("Shai", "Opas"), ("Materia", "The Queen"), ("Karen", "Next")],
    "BAST_CHK:0004": [("Myu", "Yun"), ("Popo", "Fino"), ("Pien", "Next")],
    "BAST_CHK:0005": [("Moon: shop girl", "Moon: priest"), ("Moon: female guard", "Carlyle: buyer"), ("Fire: male guard", "Next")],
    "BAST_CHK:0006": [("Club staff", "Carlyle: game shop"), ("Fire: market man", "Carlyle: apothecary"), ("Fire: shop boy", "Next")],
    "BAST_CHK:0007": [("Antique shop", "Fire: tavern"), ("Carlyle: ring shop", "Prada"), ("Fire: weapon shop", "White Lady")],
    "BAST_CHK:0008": [("1 Brave", "4 Confused"), ("2 Worried", "5 Solemn"), ("3 Angry", "Next")],
    "BAST_CHK:0009": [("6 Surprised", "9 Embarrassed"), ("7 Resolute", "10 Cheerful"), ("8 Evasive", "Next")],
    "BAST_CHK:0010": ["11 Normal", "Back"],
    "BAST_CHK:0011": [("12 Brave", "15 Worried"), ("13 Suggesting", "16 Defiant"), ("14 Sulking", "Next")],
    "BAST_CHK:0012": [("17 Complaining", "B-20 Special"), ("18 Flustered", "B-21 Confused"), ("19 Dejected", "Next")],
    "BAST_CHK:0013": [("22 Tired", "25 Cheerful"), ("23 Solemn", "26 Normal"), ("24 Kindness", "Next")],
    "BAST_CHK:0014": ["27 Sulking", "28 Exasperated", "Back"],
    "BAST_CHK:0015": [("29 Anxious", "32 Special 2"), ("30 Dejected", "33 Caring"), ("31 Special 1", "Next")],
    "BAST_CHK:0016": [("34 Confused", "37 Resolute"), ("35 Tired", "38 Sulking"), ("36 Solemn", "Next")],
    "BAST_CHK:0017": [("39 Flustered, shy", "42 Normal"), ("40 Worried", "43 Normal, 2nd half"), ("41 Cheerful", "Next")],
    "BAST_CHK:0018": [("44 Shy, 2nd half", "47 Down, 2nd half"), ("45 Resolute, 2nd half", "48 Rattled, 2nd half"), ("46 Tired, 2nd half", "Next")],
    "BAST_CHK:0019": [("49 Worried, 2nd half", "Back"), "50 Cheerful, 2nd half", "51 Confession, 2nd half"],
    "BAST_CHK:0020": [("52 Calm", "55 Worried"), ("53 Convinced", "56 Smirking"), ("54 Special 1", "Next")],
    "BAST_CHK:0021": [("57 Consoling", "B-60 Flustered"), ("58 Confused", "B-61 Solemn"), ("59 Special 2", "Next")],
    "BAST_CHK:0022": [("62 Encouraging", "65 Cheerful"), ("63 Sulking", "66 Normal"), ("64 Dejected", "Back")],
    "BAST_CHK:0023": [("67 Normal", "70 Confrontational"), ("68 Irritated", "71 Dejected"), ("69 Confused", "Next")],
    "BAST_CHK:0024": [("72 Lonely", "75 Sulking"), ("73 Crying", "76 Flustered, shy"), ("74 Lost in thought", "Next")],
    "BAST_CHK:0025": [("77 Worried", "Back"), "78 Cheerful", "79 Anxious"],
    "BAST_CHK:0026": [("80 Special 1", "83 Serious"), ("81 Special 2", "84 Angry"), ("82 Special 3", "Next")],
    "BAST_CHK:0027": [("85 Resolute", "88 Sulking"), ("86 Dejected", "89 Worried"), ("87 Exhausted", "Next")],
    "BAST_CHK:0028": [("90 Cheerful", "93 Baby 2"), ("91 Normal", "94 Prince mode"), ("92 Baby 1", "Back")],
    "BAST_CHK:0029": [("95 Warning", "98 Earnest"), ("96 Special", "99 Shy"), ("97 Normal", "Next")],
    "BAST_CHK:0030": [("100 Crying", "103 Cheerful"), ("101 Sulking", "104 Anxious"), ("102 Worried", "Next")],
    "BAST_CHK:0031": ["105 Confused", "Back"],
    "BAST_CHK:0032": [("106 Holding the book", "109 Haughty"), ("107 Beckoning", "110 Explaining"), ("108 Glad puzzle solved", "Next")],
    "BAST_CHK:0033": [("111 Grave face", "114 Hesitant"), ("112 Beside Vamur", "115 Earnest"), ("113 Startled at Azel", "Next")],
    "BAST_CHK:0034": ["116 Are you sure?", "117 Normal", "Back"],
    "BAST_CHK:0035": [("118 Looking down", "Back"), "119 Listless", "120 Exhausted"],
    "BAST_CHK:0036": [("121 Approaching to talk", "124 Surprised"), ("122 Intrigued", "125 Defiant grin"), ("123 Introducing Yun", "Next")],
    "BAST_CHK:0037": ["126 Looking down on them", "Back"],
    "BAST_CHK:0038": [("127 Reuniting: Hikaru", "130 Earnest"), ("128 Talking to Hikaru", "131 Solemn"), ("129 Exaggerating", "Next")],
    "BAST_CHK:0039": ["132 Carefree", "133 Recalling the tunnel", "Back"],
    "BAST_CHK:0040": [("134 Reuniting: Hikaru", "137 Earnest"), ("135 Talking to Hikaru", "138 Solemn"), ("136 Exaggerating", "Next")],
    "BAST_CHK:0041": ["139 Talking, smiling", "140 Recalling the tunnel", "Back"],
    "BAST_CHK:0042": ["141 Sitting in the room", "142 Troubled", "Back"],
    "BAST_CHK:0043": [("143 Normal", "146 Surprised"), ("144 Earnest", "Back"), "145 Confused"],
    "BAST_CHK:0044": [("147 Annoyed", "150 Anxious"), ("148 Angry", "Back"), "149 Pleased, irritated"],
    "BAST_CHK:0045": [("151 Tending the bow", "Back"), "152 Tending the bow, down", "153 Normal"],
    "BAST_CHK:0046": [("155 Composed", "158 Activating"), ("156 Gauging mood", "159 Vanishing"), ("157 Angry", "Back")],
    "BAST_CHK:0047": ["160 Triumphant", "161 Near death", "Back"],
    "BAST_CHK:0048": ["162 Disciplined", "163 Angry", "Back"],
    "BAST_CHK:0049": [("164 When appearing", "Back"), "165 In front of Lady", "197 Disbelief"],
    "BAST_CHK:0050": [("166 Normal", "169 Weeping"), ("167 Smug", "Back"), "168 Exhausted"],
    "BAST_CHK:0051": [("171 Normal", "174 Betrayed"), ("172 Delighted", "175 Happy"), ("173 Baffled", "Next")],
    "BAST_CHK:0052": ["176 Solemn", "Back"],
    "BAST_CHK:0053": [("177 Normal", "Back"), "178 Worried", "179 Angry, scolding"],
    "BAST_CHK:0054": [("194 Bold", "Back"), "195 Glaring", "196 Hurt, glaring"],
    # --- BAT_TEST
    "BAT_TEST:0000": [("First battle", "Moonlight Tower boss"), ("Battle after finding gun", "Iopiros boss"), ("Gym battle", "Next")],
    "BAT_TEST:0001": [("Basic pattern 1", "Basic pattern 4"), ("Basic pattern 2", "Basic pattern 5"), ("Basic pattern 3", "Next")],
    "BAT_TEST:0002": [("Basic pattern 6", "Basic pattern 9"), ("Basic pattern 7", "Basic pattern 10"), ("Basic pattern 8", "Back")],
    # --- DEBUG, disc 1
    "DEBUG:0000": [("From the start", "Voice test"), ("Jump in midway", "Magic Bullet test"), "Load and start"],
    "DEBUG:0001": ["Once more", "Back"],
    "DEBUG:0002": ["Data 1", "Data 2", "Back"],
    "DEBUG:0003": [("Ch.1", "Ch.4"), ("Ch.2", "Ch.5"), "Ch.3"],
    "DEBUG:0004": [("Start from the beginning", "Gym"), ("Start from the hallway", "Leave the hill"), "Passage to the gym"],
    "DEBUG:0005": ["Ch.2 from the start", "Start Moonlight Tower", "Moonlight Tower, before F6 boss"],
    "DEBUG:0006": [("After Albaijan arrives", "Yuka gets caught"), "Start Iopiros Tower", "Iopiros Tower boss"],
    "DEBUG:0007": [("Ch.4 start", "Start ruins search"), ("Start Hikaru search", "Locked container"), ("Start underground test", "Next")],
    "DEBUG:0008": ["Hikaru receives it", "Analyze the pendant", "Found the Talisma"],
    "DEBUG:0009": ["Ch.5 start", "Cave, before the lab", "Yuka confesses in the cell"],
    # --- DEBUG, disc 2
    "DEBUG@d2:0000": [("Main story", "Voice check"), ("Added voice check", "More added voices"), "Load and start"],
    "DEBUG@d2:0002": [("Ch.6", "Ch.9"), ("Ch.7", "Ch.10"), ("Ch.8", "Next")],
    "DEBUG@d2:0003": ["Ending", "Epilogue"],
    "DEBUG@d2:0004": [("Party", "Akiho"), ("Yuka", "Lou"), ("Hikaru", "Hermie")],
    "DEBUG@d2:0005": [("Yuka", "Lou"), ("Hikaru", "Hermie 1"), ("Akiho", "Hermie 2")],
    "DEBUG@d2:0006": [("Ch.6 start", "Before Black Chamber"), "Start exploring the inn", "Meet Azel"],
    "DEBUG@d2:0007": [("Yuka in the dungeon", "At Azel's house..."), "Hikaru in the dungeon", "To Basement 3"],
    "DEBUG@d2:0008": [("Castle town entrance", "Castle dungeon, 3F"), ("Castle town", "Back"), "Fire Dragon Castle dungeon, 1F"],
    "DEBUG@d2:0009": [("Ch.7 start", "Vamur, Black Chamber"), ("Camp in the castle", "Yun dies"), "Rea in the throne room"],
    "DEBUG@d2:0010": [("Castle town entrance", "the Queen's chamber"), ("Castle town", "Back"), "Fire Dragon Castle, floor 1"],
    "DEBUG@d2:0011": ["Ch.8 start", "Start free roaming", "Found the Talisma"],
    "DEBUG@d2:0012": [("Popo crying", "In the Lost Forest"), ("Leave at night", "Yuka's sentiment"), ("Akiho's feelings", "Next")],
    "DEBUG@d2:0013": ["Found the Talisma", "Back"],
    "DEBUG@d2:0014": [("Yamyam Town", "Yamyam Forest E"), ("Yamyam Forest", "Back"), "Yamyam Forest D"],
    "DEBUG@d2:0015": ["Ch.9 start", "Karen at the control device"],
    "DEBUG@d2:0016": ["Sacred Tree entrance", X, X],
    "DEBUG@d2:0017": [("Ch.10 start", "Lou's house"), ("Reach Moonlight Village", "Reach Carlyle"), ("To the Oracle Shrine", "Next")],
    "DEBUG@d2:0018": [("Carlyle basement 3", "Finale: Akiho"), ("Finale: Yuka", "Finale: Lou"), ("Finale: Hikaru", "Finale: Hermie")],
    "DEBUG@d2:0019": [("Into the village", "Albaijan's house"), ("Carlyle secret passage", "Start ruins"), "Reach Carlyle"],
    "DEBUG@d2:0020": [("From the start", "Finale: Yuka"), ("Carlyle basement 3", "Finale: Hikaru"), ("Carlyle basement 4", "Next")],
    "DEBUG@d2:0021": ["Finale: Akiho", "Finale: Lou", "Finale: Hermie"],
    "DEBUG@d2:0022": [("Yuka", "Lou"), ("Hikaru", "Hermie"), ("Akiho", "Back")],
    # --- START1
    "START1:0000": [("Ch.6", "Ch.9"), ("Ch.7", "Ch.10, first half"), ("Ch.8", "Next")],
    "START1:0001": [("Ch.10, second half", "Ending: Hikaru"), ("Ending: Party", "Ending: Akiho"), ("Ending: Yuka", "Next")],
    "START1:0002": [("Ending: Lou", "Epilogue: Hikaru"), ("Ending: Hermie", "Epilogue: Akiho"), ("Epilogue: Yuka", "Next")],
    "START1:0003": [("Epilogue: Lou", "Underground Chapel"), ("Epilogue: Hermie", "Underground Ruins 2"), "Back"],
    "START1:0004": [("Ch.6 start", "Before Black Chamber"), ("Start exploring the inn", "At Azel's house..."), "Meet Azel"],
    "START1:0005": [("Yuka in the dungeon", "At Azel's house..."), "Hikaru in the dungeon", "To Basement 3"],
    "START1:0007": [("Map", "Rea, throne room"), ("Ch.8 start", "Vamur, Black Chamber"), ("Camp in the castle", "Yun dies")],
    "START1:0009": [("Map", "Start free roaming"), ("Ch.9 start", "Heartbroken Lou"), ("Meet Pien", "Next")],
    "START1:0013": [("Map", "Tent event: Akiho"), ("From the start", "Karen at controls"), ("Start the dungeon", "Teleport from Pien")],
    "START1:0015": [("From the start", "Into the town"), ("Reach Moonlight Village", "Hermie's dungeon"), ("Talk to Rando", "Next")],
    "START1:0016": [("Shai and Lou on the hill", "Cathedral dungeon"), ("Hermie event", "Lou's house"), ("Fight with Myu", "Next"), X],
    "START1:0017": [("Into the village", "Albaijan's house"), ("Carlyle secret passage", "Start ruins"), ("Reach Carlyle", "Next"), X],
    "START1:0018": [("From the start", "Finale: Yuka"), ("Carlyle basement 3", "Finale: Hikaru"), ("Carlyle basement 4", "Next")],
    "START1:0019": ["Finale: Akiho", "Finale: Lou", "Finale: Hermie"],
    # --- STARTBAK (older copy of the start menu)
    "STARTBAK:0000": [("From the start", "Voice test"), "Jump into the middle", "Load and start"],
    "STARTBAK:0003": [("Start from the beginning", "Gym"), ("Start from the classroom", "Leave the hill"), "Passage to the gym"],
    "STARTBAK:0004": [("Gym", "Leave the hill"), ("Reach Iopiros Hill", "Moonlight Clan gate"), ("Hill morning event", "Back")],
    "STARTBAK:0006": [("Tower F6 boss", "Back"), "<1>After tower, no Talisma", "<1>After tower, with Talisma"],
    "STARTBAK:0007": [("Moonlight Village", "Moonlight Tower F6"), ("Moonlight Tower entrance", "Back"), "Moonlight Tower F3"],
    "STARTBAK:0009": [("To Iopiros Tower", "Iopiros Tower F6"), ("Iopiros Tower entrance", "Back"), "Iopiros Tower F3"],
    "STARTBAK:0010": [("Start Iopiros Tower", "Boss beaten, return"), ("Iopiros Tower F1 clear", "*Analyze Albaijan"), ("Iopiros Tower boss", "Back")],
    "STARTBAK:0011": [("Ch.4 start", "Start ruins search"), ("Start Hikaru search", "Locked container"), ("Start underground test", "Hikaru receives it")],
    "STARTBAK:0012": [("Go to underground test", "Camp: Yuka"), ("Start ruins search", "Locked container"), ("Camp: Hikaru", "Next")],
    "STARTBAK:0013": ["Hikaru gets it from Imul", "Analyze the pendant", ("Get Talisma underground", "Back")],
    "STARTBAK:0014": [("Carlyle town", "Carlyle basement 3F"), ("Carlyle basement 1F", "Back"), "Carlyle basement 2F"],
    "STARTBAK:0015": ["Ch.5 start", "Cave, before the lab", "Yuka confesses in the cell"],
    "STARTBAK:0016": [("Castle basement 1F", "Castle town gate"), ("Castle basement 3F", "Back"), "Castle basement 5F"],
}


def line(x):
    return x[0].ljust(26) + x[1] if isinstance(x, tuple) else x


if __name__ == "__main__":
    ids = [l.split("\t")[0] for l in (root / "build/batches/dbg.tsv").read_text(encoding="utf-8").splitlines() if l]
    missing = [i for i in ids if i not in ROWS]
    extra = [i for i in ROWS if i not in ids]
    assert not missing and not extra, (missing, extra)
    with open(root / "build/batches/dbg.out.tsv", "w", encoding="utf-8", newline="\n") as f:
        for i in ids:
            f.write(i + "\t" + "\\n".join(line(x) for x in ROWS[i]) + "\n")
    print(len(ids), "rows")
