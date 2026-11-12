"""Text coverage for warp/tour runs: which script rows the interpreter actually reached.

  python -X utf8 tools/debug/cover.py LOGDIR [--waive docs/text_unshown.tsv] [--list]

Reads every LOGDIR/**/log.txt written with tools/lua/scriptpos.lua ("POS <script> <off> <lineoff>"; the run dir name
starts d1_/d2_ = disc). A row counts as shown when the read offset entered its 「...」 block in the QA build's bytes
(text.files() + build.QA_VOICE, i.e. exactly what `warp.py build` put on the disc).
Writes LOGDIR/cover/log.txt ("TEXT <n>") + strings.tsv, then runs the skill's textcover.py gate (exit 1 = unshown).
"""
import argparse
import pathlib
import re
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "tools"))
import build
import text
from skill import SKILL


def spans():
    """{(disc, NAME): [(start, end, id)]} for the QA build's script bytes."""
    out = {}
    for (d, name), b in text.files().items():
        key = name if (d == "d1" or (name + "@d2") not in text.sources()) else name + "@d2"
        rows = text.load(key)
        b = build.QA_VOICE.sub(lambda m: b"" if m.group(1) is None else m.group(1), b)
        ents = [(s, e) for t, s, e in text.scan(b) if t == "blk"]   # parse() decodes jp; English bytes are pairs
        ids = [r["id"] for r in rows for _ in range(1 + r["en"].count("<p>"))]   # <p> = one more block (enc_en)
        assert len(ents) == len(ids), (d, name)
        out[(d, name)] = [(s, e, rid) for (s, e), rid in zip(ents, ids)]
    return out


def shown(logdir, sp):
    seen = set()
    for log in pathlib.Path(logdir).rglob("log.txt"):
        m = re.search(r"d([12])_", str(log.relative_to(logdir)))
        if not m:
            continue
        d = "d" + m[1]
        for name, off in re.findall(r"^POS (\S+)\.TXT ([0-9a-f]+) ", log.read_text(encoding="utf-8", errors="replace"), re.M):
            off = int(off, 16)
            for s, e, rid in sp.get((d, name), ()):
                if s - 2 <= off <= e + 2:
                    seen.add(rid)
    return seen


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("logdir")
    ap.add_argument("--waive", default=str(root / "docs" / "text_unshown.tsv"))
    ap.add_argument("--list", action="store_true", help="print shown/total per script")
    a = ap.parse_args()
    sp = spans()
    ids = sorted({rid for v in sp.values() for _, _, rid in v})
    seen = shown(a.logdir, sp)
    if a.list:
        per = {}
        for rid in ids:
            k = rid.split(":")[0]
            t = per.setdefault(k, [0, 0])
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
    cmd = [sys.executable, "-X", "utf8", str(pathlib.Path(SKILL) / "scripts" / "textcover.py"), str(cov), str(cov / "strings.tsv")]
    if pathlib.Path(a.waive).exists():
        cmd += ["--waive", a.waive]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print("\n".join(r.stdout.splitlines()[-3:]))
    sys.exit(r.returncode)
