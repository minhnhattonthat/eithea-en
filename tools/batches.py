"""Translation batches.
  python -X utf8 tools/batches.py split [--size 3500]   -> build/batches/bNNN.tsv + bNNN.terms.txt (untranslated rows)
  python -X utf8 tools/batches.py check bNNN            -> validates build/batches/bNNN.out.tsv; prints OK or errors
  python -X utf8 tools/batches.py merge bNNN            -> check, then write English into text/xt/*.json
  python -X utf8 tools/batches.py fit "text"  [--kind msg|choice]   -> chars per line
Input TSV: id, speaker, kind, limit, jp (line breaks as \\n). Output TSV: id<TAB>English (\\n = line break, <p> = new box).
Identical long blocks (>= 12 chars) appear once; merge copies the English to every copy.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import text

root = pathlib.Path(__file__).resolve().parent.parent
B = root / "build" / "batches"
TM_MIN = 12


def glossary():
    """{table title: [(jp, en)]} from glossary.md."""
    out, cur = {}, None
    for l in (root / "glossary.md").read_text(encoding="utf-8").splitlines():
        if l.startswith("## "):
            cur = l[3:].strip()
        m = re.match(r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", l)
        if m and cur and m.group(1) not in ("JP", "---"):
            out.setdefault(cur, []).append((m.group(1), m.group(2)))
    return out


def speakers():
    g = glossary()
    d = dict(g.get("Speaker tags (name box; JP tag in scripts -> EN)", []))
    for jp, en in g.get("Characters", []):
        d.setdefault(jp.split()[-1].split("=")[0], en.split()[0])
    return d


def all_rows():
    for p in sorted(text.OUT.glob("*.json")):
        yield p, json.loads(p.read_text(encoding="utf-8"))


def esc(s):
    return s.replace("\n", "\\n")


def unesc(s):
    return s.replace("\\n", "\n").strip(" \t\r")   # keep blank trailing menu lines


def limit(kind):
    return {"msg": "3x46", "choice": "44", "mono": "48/line"}[kind]


def split(size=3500):
    B.mkdir(parents=True, exist_ok=True)
    spk = speakers()
    seen, cur, n, out = set(), [], 0, []
    for p, rows in all_rows():
        for r in rows:
            if r["en"]:
                continue
            if len(r["jp"]) >= TM_MIN:
                if r["jp"] in seen:
                    continue
                seen.add(r["jp"])
            cur.append(r)
            n += len(r["jp"])
            if n >= size:
                out.append(cur); cur, n = [], 0
    if cur:
        out.append(cur)
    terms = [(jp, en) for t in ("Terms", "Characters") for jp, en in glossary().get(t, [])]
    for k, rows in enumerate(out, 1):
        name = f"b{k:03d}"
        with open(B / f"{name}.tsv", "w", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write("\t".join((r["id"], spk.get(r["speaker"], r["speaker"]), r["kind"], limit(r["kind"]), esc(r["jp"]))) + "\n")
        alljp = "".join(r["jp"] + r["speaker"] for r in rows)
        hit = [f"{jp} = {en}" for jp, en in terms if any(part in alljp for part in re.split(r"[ =/]", jp) if len(part) >= 2)]
        (B / f"{name}.terms.txt").write_text("\n".join(hit) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(out)} batches, {sum(len(r) for r in out)} rows")


def read_out(name):
    p = B / f"{name}.out.tsv"
    res = {}
    for l in p.read_text(encoding="utf-8-sig").splitlines():
        if not l.strip():
            continue
        if "\t" not in l:
            raise SystemExit(f"no tab: {l[:60]!r}")
        i, en = l.split("\t", 1)
        if i.strip() in res:
            raise SystemExit(f"duplicate id {i}")
        res[i.strip()] = unesc(en)
    return res


def check(name, quiet=False):
    want = [l.split("\t")[0] for l in (B / f"{name}.tsv").read_text(encoding="utf-8").splitlines() if l.strip()]
    got = read_out(name)
    errs = []
    if set(want) != set(got):
        errs.append(f"ids: missing {sorted(set(want) - set(got))[:5]} extra {sorted(set(got) - set(want))[:5]}")
    rows = {r["id"]: r for _, rs in all_rows() for r in rs}
    terms = glossary().get("Terms", [])
    for i in want:
        if i not in got or i not in rows:
            continue
        r = dict(rows[i], en=got[i])
        if not r["en"]:
            errs.append(f"{i}: empty"); continue
        key, idx = i.rsplit(":", 1)
        e = parse_cache(key)[int(idx)]
        for m in text.lint(r, e["nexthcls"]):
            errs.append(f"{i}: {m}")
        for jp, en in terms:
            for a, b in zip(jp.split(" / "), en.split(" / ")):
                if len(a) >= 2 and a in r["jp"] and b.lower() not in r["en"].lower():
                    errs.append(f"{i}: term {a} -> {b} missing")
    if not quiet:
        print("\n".join(errs[:60]) + (f"\n... {len(errs)} errors" if len(errs) > 60 else ""))
        print("OK" if not errs else f"{len(errs)} errors")
    return not errs


_pc = {}


def parse_cache(key):
    if key not in _pc:
        _pc[key] = text.parse(text.sources()[key][2])
    return _pc[key]


def merge(name):
    if not check(name):
        raise SystemExit("not merged")
    got = read_out(name)
    tm, jp_of = {}, {}
    for p, rows in all_rows():
        for r in rows:
            if r["id"] in got:
                jp_of[r["id"]] = r["jp"]
    for i, en in got.items():
        if len(jp_of[i]) >= TM_MIN:
            tm[jp_of[i]] = en
    n = 0
    for p, rows in all_rows():
        ch = False
        for r in rows:
            if r["id"] in got:
                r["en"] = got[r["id"]]; ch = True; n += 1
            elif not r["en"] and r["jp"] in tm:
                r["en"] = tm[r["jp"]]; ch = True; n += 1
        if ch:
            p.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"merged {n} rows")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "split":
        split(int(sys.argv[sys.argv.index("--size") + 1]) if "--size" in sys.argv else 3500)
    elif cmd == "check":
        sys.exit(0 if check(sys.argv[2]) else 1)
    elif cmd == "merge":
        merge(sys.argv[2])
    elif cmd == "fit":
        kind = sys.argv[sys.argv.index("--kind") + 1] if "--kind" in sys.argv else "msg"
        for l in unesc(sys.argv[2]).replace("<p>", "\n").split("\n"):
            print(f"{text.line_chars(l):3d} {l}")
        en = unesc(sys.argv[2])
        print("\n".join(text.lint(dict(en=en, jp=en, kind=kind))) or "fits")
