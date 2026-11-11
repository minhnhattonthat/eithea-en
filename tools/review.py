"""Reviewer input: build/review/rNN.txt with `>> id | speaker | kind` then JP and EN lines.
  python -X utf8 tools/review.py N_CHUNKS SIZE    -> evenly spaced contiguous chunks over all script rows
"""
import json
import pathlib
import sys

import batches
import text

root = pathlib.Path(__file__).resolve().parent.parent
OUT = root / "build" / "review"


def main(n, size):
    OUT.mkdir(parents=True, exist_ok=True)
    spk = batches.speakers()
    rows = [r for p in sorted(text.OUT.glob("*.json")) for r in json.loads(p.read_text(encoding="utf-8"))]
    step = len(rows) // n
    for k in range(n):
        chunk = rows[k * step:k * step + size]
        with open(OUT / f"r{k + 1:02d}.txt", "w", encoding="utf-8", newline="\n") as f:
            for r in chunk:
                f.write(f">> {r['id']} | {spk.get(r['speaker'], r['speaker']) or '-'} | {r['kind']}\n")
                f.write("JP: " + r["jp"].replace("\n", " / ") + "\n")
                f.write("EN: " + r["en"].replace("\n", " / ") + "\n\n")
        print(OUT / f"r{k + 1:02d}.txt", chunk[0]["id"], "..", chunk[-1]["id"])


# Story chapters, from the dev chapter-select in STARTBAK.XT / START1.XT (which scripts each entry jumps to).
# Each entry: (chapter, regex on the script name). First match wins. System scripts (menus, tests) match nothing.
CHAPTERS = [
    ("ch01", r"IVENT0[1-3][A-C]?|GAKKO\d+|I_MORI0[12]|GEKKO00"),
    ("ch02", r"IVENT0[4-9][A-C]?|GEKKO0[1-6]|G(RANDO|SHOP|RUUU|MATE|SYAI|SHINKAN|EURIKE)|G_TOU\d"),
    ("ch03", r"IVENT1[0-7][A-C]?|GEKKO10|I_MORI03|I_TO[U\d][\d_]*"),
    ("ch04", r"IVENT2[0-8]|IVENTC0[01]|KARILE0[1-3]|K_CHI0.*|KA_(CLUB|ALBAI|KAITO|GAME|KUSUR|UNTIQ|RING)"),
    ("ch05", r"IVENT(29|3[01])|IVENTC02|KA_CHI\d+|KARYU04"),
    ("ch06", r"IVENT3[5-8]|IVENTC0[34]|KARYU02B?|K_(ICHIBA|BUKI|SAKABA|AZEL|DOUGU)|KA_ROU\d+"),
    ("ch07", r"IVENT4\d|IVENTC05|KARYU03|KA_SHI\d+"),
    ("ch08", r"IVENT5\d|YAMU\d+|YA_.*|Y_MORI\d+"),
    ("ch09", r"IVENT6\d|IVENTC06|SHIN\d+"),
    ("ch10a", r"IVENT(7\d|8[0-4])|IVENTC07|(?!VT).*Z|SEIDOU\d+|K_CHI2[12].*"),
    ("ch10b", r"IVENT(8[56]|90\d?|91\d)|IVENTC(08|09|10)|K_CHI2[3-6].*"),
    ("endings", r"IVENT1[01]\d"),
]
STORY = root / "work" / "qa" / "story" / "chapters"


def chapter_of(name):
    import re
    base = name.split("@")[0]
    return next((c for c, rx in CHAPTERS if re.fullmatch(rx, base)), None)


def chapters():
    """One file per chapter: event scripts (IVENT*) in number order, then field scripts by name."""
    import re
    spk = batches.speakers()
    by = {}
    for p in text.OUT.glob("*.json"):
        c = chapter_of(p.stem)
        if c:
            by.setdefault(c, []).append(p)
    key = lambda p: (not p.stem.startswith("IVENT"), [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", p.stem)])
    STORY.mkdir(parents=True, exist_ok=True)
    for c, ps in sorted(by.items()):
        n = 0
        with open(STORY / f"{c}.txt", "w", encoding="utf-8", newline="\n") as f:
            for p in sorted(ps, key=key):
                f.write(f"== {p.stem} ==\n")
                for r in json.loads(p.read_text(encoding="utf-8")):
                    n += 1
                    f.write(f">> {r['id']} | {spk.get(r['speaker'], r['speaker']) or '-'} | {r['jp'].replace(chr(10), ' / ')}\n")
                    f.write(f"   {r['en'].replace(chr(10), ' / ')}\n")
        print(c, len(ps), "scripts", n, "rows")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--chapters"]:
        chapters()
    else:
        main(int(sys.argv[1]), int(sys.argv[2]))
