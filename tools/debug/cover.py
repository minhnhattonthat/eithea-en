"""Text coverage for warp/tour runs: which script rows the interpreter actually reached.

  python -X utf8 tools/debug/cover.py LOGDIR [--waive docs/text_unshown.tsv] [--list]

QA builds made with `build.py --qa-cover` (warp.py build does) get `flag[990] = <row+1>;` before every text block
(instrument()); tools/lua/rowlog.lua logs "ROW <script> <value>" whenever the flag or the script changes.
A run dir name starting d1_/d2_ gives the disc. Writes LOGDIR/cover/log.txt ("TEXT <n>") + strings.tsv, then runs
the skill's textcover.py gate (exit 1 = rows never shown and not waived).
"""
import argparse
import pathlib
import re
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "tools"))
import text

FLAG = 990   # unused by the game (highest used: 960)


def key(disc, name):
    return name + "@d2" if disc == 2 and text.OUT.joinpath(name + "@d2.json").exists() else name


def instrument(disc, name, b):
    """b (built script bytes) with a flag set before each row's first block (its 〈name〉 line when there is one)."""
    rows = text.load(key(disc, name))
    if not rows:
        return b
    blocks = [s - 2 for t, s, e in text.scan(b) if t == "blk"]
    firsts, k = [], 0
    for i, r in enumerate(rows):
        firsts.append((blocks[k], i))
        k += 1 + r["en"].count("<p>")
    assert k == len(blocks), (disc, name)
    out, pos = [], 0
    for at, i in firsts:
        ls = b.rfind(b"\n", 0, at) + 1
        prev = b.rfind(b"\n", 0, max(ls - 1, 0)) + 1
        if b[prev:ls].strip().startswith("〈".encode("cp932")):
            ls = prev
        out += [b[pos:ls], f"flag[{FLAG}] = {i + 1};\r\n".encode()]
        pos = ls
    return b"".join(out + [b[pos:]])


def shown(logdir):
    seen = set()
    for log in pathlib.Path(logdir).rglob("log.txt"):
        m = re.match(r"d([12])_", log.parent.name)
        if not m:
            continue
        for name, v in re.findall(r"^ROW (\S+)\.TXT (\d+)", log.read_text(encoding="utf-8", errors="replace"), re.M):
            if int(v):
                seen.add(f"{key(int(m[1]), name)}:{int(v) - 1:04d}")
    return seen


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("logdir")
    ap.add_argument("--waive", default=str(root / "docs" / "text_unshown.tsv"))
    ap.add_argument("--list", action="store_true", help="print shown/total per script")
    a = ap.parse_args()
    ids = sorted(r["id"] for p in text.OUT.glob("*.json") for r in text.load(p.stem))
    seen = shown(a.logdir) & set(ids)
    if a.list:
        per = {}
        for rid in ids:
            t = per.setdefault(rid.split(":")[0], [0, 0])
            t[1] += 1
            t[0] += rid in seen
        for k, (s, t) in sorted(per.items()):
            print(f"{k}\t{s}/{t}")
    cov = pathlib.Path(a.logdir) / "cover"
    cov.mkdir(exist_ok=True)
    num = {rid: i for i, rid in enumerate(ids)}
    (cov / "strings.tsv").write_text("".join(f"{rid}\t{num[rid]:x}\n" for rid in ids), encoding="utf-8")
    (cov / "log.txt").write_text("".join(f"TEXT {num[rid]:x}\n" for rid in sorted(seen)), encoding="utf-8")
    print(f"shown {len(seen)}/{len(ids)} rows", flush=True)
    from skill import SKILL
    cmd = [sys.executable, "-X", "utf8", str(pathlib.Path(SKILL) / "scripts" / "textcover.py"), str(cov), str(cov / "strings.tsv")]
    if pathlib.Path(a.waive).exists():
        cmd += ["--waive", a.waive]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print("\n".join(r.stdout.splitlines()[-3:]))
    sys.exit(r.returncode)
