"""Glossary consistency fixes applied to every English script row (idempotent).
  python -X utf8 tools/polish.py [--dry]
Each rule: (regex, replacement, optional JP substring the row must contain). Choice rows are re-padded so column 2
still starts at char 26. Prints changed ids; lint errors abort without writing.
"""
import json
import re
import sys

import text

RULES = [
    (r"\bTower of Iopiros\b", "Iopiros Tower", None),
    (r"\bthe Iopiros Tower\b", "Iopiros Tower", None),
    (r"\bMagic Bullet Research\b", "Magic Bullet Study", "魔弾研究"),
    (r"\bStudy Magic Bullets\b", "Magic Bullet Study", "魔弾研究"),
    (r"\bRed Dragon Inn\b", "Red Dragon Tavern", None),
    (r"\bTsurigyoro\b", "Googly-Glare", None),
    (r"\bOracle Hall\b", "Oracle Shrine", None),
    (r"\b[Ss]acred tree\b", "Sacred Tree", "神木"),
    (r"\b(an |the )?Elixir of Protection\b", lambda m: ("a " if m.group(1) == "an " else m.group(1) or "") + "Guard Elixir", None),
    (r"\bPassion Loincloth\b", "Passion Fundoshi", None),      # item names must fit the EXE's 16-char fields
    (r"\bDragon Crusher Blade\b", "Dragon Crusher", None),
    (r"\b(the|our) chief\b", r"\1 Chief", "族長"),
    (r"\bold writings\b", "old texts", "文献"),
]


def repad(line):
    m = re.match(r"(.*?\S) {2,}(\S.*)$", line.lstrip(" "))
    if not m:
        return line
    return m.group(1).ljust(26) + m.group(2)


def main(dry):
    changed, errs = [], []
    files = {}
    for p in sorted(text.OUT.glob("*.json")):
        rows = json.loads(p.read_text(encoding="utf-8"))
        dirty = False
        for r in rows:
            en = r["en"]
            for pat, rep, need in RULES:
                if need and need not in r["jp"]:
                    continue
                en = re.sub(pat, rep, en)
            if r["kind"] == "choice" and en != r["en"]:
                en = "\n".join(repad(l) for l in en.split("\n"))
            if en != r["en"]:
                r["en"] = en; dirty = True; changed.append(r["id"])
                errs += [f"{r['id']}: {e}" for e in text.lint(r)]
        if dirty:
            files[p] = rows
    print(len(changed), "rows changed:", " ".join(changed[:40]), "..." if len(changed) > 40 else "")
    if errs:
        print("\n".join(errs)); raise SystemExit("lint errors, nothing written")
    if not dry:
        for p, rows in files.items():
            p.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main("--dry" in sys.argv)
