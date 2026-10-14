"""EITHEA.EXE strings <-> text/exe.json (in-place: English must fit the original byte span).
  python -X utf8 tools/exetext.py dump [--force]   -> text/exe.json
  python -X utf8 tools/exetext.py check            -> fit / charset errors
A string = run of 2-byte SJIS codes whose glyphs exist in KANJI.BL (or full-width space / ①..⑩), >= 2 chars.
`size` = bytes of the run (trailing full-width spaces included). English is pair-encoded (2 chars per 2 bytes),
then padded with full-width spaces to `size`, so record fields and pointers keep their layout.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import text

root = pathlib.Path(__file__).resolve().parent.parent
EXE = root / "work" / "d1" / "tree" / "EITHEA.EXE"
OUT = root / "text" / "exe.json"
BASE = 0x80010000 - 0x800
FWS = b"\x81\x40"


def charset():
    bl = (root / "work/d1/bind/0931_KANJI.BL").read_bytes()
    s = {bl[i] << 8 | bl[i + 1] for i in range(0, len(bl) - 1, 2) if bl[i] != 0xFF}
    return s | {0x8140} | set(range(0x8740, 0x874A))


def scan(b):
    ok = charset()
    i, n, res = 0x800, len(b), []
    while i < n - 1:
        j = i
        while j < n - 1 and (b[j] << 8 | b[j + 1]) in ok:
            j += 2
        if j - i >= 4 and any((b[k] << 8 | b[k + 1]) != 0x8140 for k in range(i, j, 2)):
            raw = b[i:j]
            body = raw.rstrip(FWS) if len(raw.rstrip(FWS)) % 2 == 0 else raw  # keep alignment
            jp = raw.decode("cp932")
            hira = sum(1 for c in jp if "぀" <= c <= "ヿ" or c in "ー！？。、")
            if hira or len(jp) >= 4:
                res.append(dict(addr=f"{i + BASE:08x}", size=j - i, jp=text.to_text(raw), en=""))
            i = j
        else:
            i += 1 if j == i else 2
    return res


def dump(force=False):
    if OUT.exists() and not force:
        raise SystemExit(f"{OUT} exists (--force to overwrite)")
    rows = scan(EXE.read_bytes())
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(len(rows), "strings,", sum(len(r["jp"]) for r in rows), "chars")


def encode(en, size):
    """English -> bytes of exactly `size` (pair codes + full-width-space padding).
    `raw:` prefix = plain SJIS (for text the BIOS draws, e.g. the memory-card save title)."""
    if en.startswith("raw:"):
        b = en[4:].encode("cp932")
    else:
        b = b"\r\n".join(text.enc_line(l) for l in en.split("\n"))
    if len(b) > size:
        raise ValueError(f"{len(b)} bytes > {size}: {en!r}")
    return b + FWS * ((size - len(b)) // 2)


def apply(exe):
    exe = bytearray(exe)
    for r in json.loads(OUT.read_text(encoding="utf-8")):
        if r["en"] and r.get("status") != "skip":
            o = int(r["addr"], 16) - BASE
            assert text.from_jp(r["jp"]) == exe[o:o + r["size"]], r["addr"]
            exe[o:o + r["size"]] = encode(r["en"], r["size"])
    return bytes(exe)


def check():
    bad = 0
    for r in json.loads(OUT.read_text(encoding="utf-8")):
        if not r["en"] or r.get("status") == "skip":
            continue
        try:
            encode(r["en"], r["size"])
        except Exception as e:
            print(r["addr"], e); bad += 1
    print("OK" if not bad else f"{bad} errors")
    return not bad


AREAS = [  # (start, end, context for translators)
    (0x80010000, 0x800110c0, "disc-change / loading messages"),
    (0x800110c0, 0x80013000, "STAFF CREDITS: each entry is one 42-char line, centred with spaces; role titles and romanized names (Given Family)"),
    (0x80013000, 0x80013eb8, "magic bullet elements (short names) and bullet effect descriptions (one line)"),
    (0x80013eb8, 0x80016530, "item / weapon / ring / accessory descriptions (one help line; some have a column break via spaces)"),
    (0x80016530, 0x80019000, "menus, status screen, shop, memory card, formations, battle messages (concatenated with a name: write suffixes like ' was defeated!')"),
    (0x80019000, 0x8008d000, "party names and battle text"),
    (0x8008d000, 0x8008e700, "monster names (16-char fields)"),
    (0x8008e700, 0x80092000, "item / bullet / weapon / ring / accessory names (16-char fields); 予備 = unused spare, 研究失敗 = failed research"),
]
B = root / "build" / "batches"


def area(addr):
    a = int(addr, 16)
    return next(t for s, e, t in AREAS if s <= a < e) if any(s <= a < e for s, e, _ in AREAS) else ""


def split(per=280):
    rows = [r for r in json.loads(OUT.read_text(encoding="utf-8")) if r.get("status") != "skip" and not r["en"]]
    B.mkdir(parents=True, exist_ok=True)
    for k in range(0, len(rows), per):
        name = f"exe{k // per + 1}"
        with open(B / f"{name}.tsv", "w", encoding="utf-8", newline="\n") as f:
            for r in rows[k:k + per]:
                f.write(f"{r['addr']}\t{r['size']}\t{area(r['addr'])}\t{r['jp']}\n")
        print(name, len(rows[k:k + per]))


def read_out(name):
    res = {}
    for l in (B / f"{name}.out.tsv").read_text(encoding="utf-8-sig").splitlines():
        if l.strip():
            a, en = l.split("\t", 1)
            res[a.strip()] = en.rstrip("\n").replace("\\n", "\n")
    return res


def check_batch(name):
    want = [l.split("\t")[0] for l in (B / f"{name}.tsv").read_text(encoding="utf-8").splitlines() if l]
    got = read_out(name)
    rows = {r["addr"]: r for r in json.loads(OUT.read_text(encoding="utf-8"))}
    errs = []
    if set(want) != set(got):
        errs.append(f"ids: missing {sorted(set(want) - set(got))[:5]} extra {sorted(set(got) - set(want))[:5]}")
    for a in want:
        if a not in got:
            continue
        en, r = got[a], rows[a]
        bad = set(text.TAG.sub("", en)) - text.font.CHARS
        if bad:
            errs.append(f"{a}: bad chars {''.join(sorted(bad))!r}")
        if sorted(text.TAG.findall(en)) != sorted(text.TAG.findall(r["jp"])):
            errs.append(f"{a}: inline codes differ from jp")
        try:
            encode(en, r["size"])
        except Exception:
            errs.append(f"{a}: {text.line_chars(en)} chars > {r['size']} (limit)")
        if "\n" in en:
            errs.append(f"{a}: no line breaks in EXE strings")
    print("\n".join(errs[:60]))
    print("OK" if not errs else f"{len(errs)} errors")
    return not errs


def merge(name):
    if not check_batch(name):
        raise SystemExit("not merged")
    got = read_out(name)
    rows = json.loads(OUT.read_text(encoding="utf-8"))
    for r in rows:
        if r["addr"] in got:
            r["en"] = got[r["addr"]]
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("merged", len(got))


if __name__ == "__main__":
    if sys.argv[1] == "dump":
        dump("--force" in sys.argv)
    elif sys.argv[1] == "check":
        sys.exit(0 if (check_batch(sys.argv[2]) if len(sys.argv) > 2 else check()) else 1)
    elif sys.argv[1] == "split":
        split()
    elif sys.argv[1] == "merge":
        merge(sys.argv[2])
