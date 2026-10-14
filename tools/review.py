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


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
