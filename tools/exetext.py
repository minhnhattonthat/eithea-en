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
    """English -> bytes of exactly `size` (pair codes + full-width-space padding)."""
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


if __name__ == "__main__":
    if sys.argv[1] == "dump":
        dump("--force" in sys.argv)
    elif sys.argv[1] == "check":
        sys.exit(0 if check() else 1)
