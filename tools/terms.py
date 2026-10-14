"""Rewrite build/batches/bNNN.terms.txt from the current glossary (after glossary updates between waves).
  python -X utf8 tools/terms.py [bNNN ...]   (default: every batch without an .out.tsv)"""
import re
import sys

import batches

names = sys.argv[1:] or sorted(p.stem for p in batches.B.glob("b*.tsv")
                               if not p.stem.endswith(".out") and not (batches.B / f"{p.stem}.out.tsv").exists())
g = batches.glossary()
tables = [t for t in g if t.startswith(("Terms", "Characters", "Other names", "Elements", "Items", "UI words"))]
terms = [(jp, en) for t in tables for jp, en in g[t]]
for n in names:
    jp_all = "".join(l.split("\t")[4] + l.split("\t")[1] for l in (batches.B / f"{n}.tsv").read_text(encoding="utf-8").splitlines() if l)
    hit = [f"{jp} = {en}" for jp, en in terms if any(p in jp_all for p in re.split(r"[ =/()○]+", jp) if len(p) >= 2)]
    (batches.B / f"{n}.terms.txt").write_text("\n".join(hit) + "\n", encoding="utf-8", newline="\n")
print(len(names), "term files")
