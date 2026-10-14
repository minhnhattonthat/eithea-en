"""Script text (XT files) <-> JSON.
  python -X utf8 tools/text.py dump [--force]   -> text/xt/NAME.json (NAME@d2.json when disc 2 differs)
  python -X utf8 tools/text.py roundtrip        -> re-encode every jp block, compare with the original files
  python -X utf8 tools/text.py stats

Displayed text = 「...」 blocks read by the interpreter at top level (outside ; comments). 〈speaker〉 tags are NOT
text: the interpreter matches them against EXE names to pick the name-box sprite, so they stay Japanese.
Block forms: msg (message window), choice (followed by command_select; each line starts with a full-width space).
In jp/en: newline = line break, <1>..<10> = inline codes ①..⑩ (⑧ ends a colour, ⑩ is a short pause).
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import font

root = pathlib.Path(__file__).resolve().parent.parent
OUT = root / "text" / "xt"
SKIP = {"DEBUG", "START1", "STARTBAK", "BAT_TEST", "BAST_CHK"}  # debug-only scripts, left Japanese
LQ, RQ, NM, NME = "「」〈〉"
CIRC = "①②③④⑤⑥⑦⑧⑨⑩"
WIDTH = {"msg": 48, "choice": 46}   # chars per line (6 px each); provisional until the width gate


# original script bugs fixed before parsing (a missing 」 swallowed the following commands into the message)
SRC_FIX = {"IVENT10": [("なんです……\r\nhcls V1036", "なんです……」\r\nhcls V1036")]}


def sources():
    """{key: (disc, NAME, bytes)}; key is NAME, or NAME@d2 when disc 2 has different content."""
    out = {}
    for d in ("d1", "d2"):
        for f in sorted((root / "work" / d / "bind").glob("*.XT")):
            name = f.name[5:-3]
            b = f.read_bytes()
            for old, new in SRC_FIX.get(name, ()):
                assert b.count(old.encode("cp932")) == 1, name
                b = b.replace(old.encode("cp932"), new.encode("cp932"))
            if name in out and out[name][2] != b:
                out[f"{name}@d2"] = (d, name, b)
            elif name not in out:
                out[name] = (d, name, b)
    return out


def scan(b):
    """Yield (start, end, kind_hint) byte spans of block CONTENT (between 「 and 」) the interpreter reads, plus
    ('name', start, end) for 〈..〉. Mirrors the reader at 0x8002b2f4: ';' comments to end of line, 2-byte SJIS."""
    i, n = 0, len(b)
    lq, rq, nm, nme = (c.encode("cp932") for c in (LQ, RQ, NM, NME))
    while i < n:
        c = b[i]
        if c == 0x1A:
            break
        if c == 0x3B:                                    # ; comment
            j = b.find(b"\r\n", i)
            i = n if j < 0 else j + 2
            continue
        if 0x81 <= c <= 0x9F or 0xE0 <= c <= 0xFC:
            two = b[i:i + 2]
            if two == lq:
                j = i + 2
                while j < n and b[j:j + 2] != rq:        # block: scan 2-byte aware to 」
                    cj = b[j]
                    if cj == 0x3B:                       # comment inside a block: skip to end of line
                        k = b.find(b"\r\n", j)
                        j = n if k < 0 else k
                        continue
                    j += 2 if (0x81 <= cj <= 0x9F or 0xE0 <= cj <= 0xFC) else 1
                yield ("blk", i + 2, j)
                i = j + 2
                continue
            if two == nm:
                j = b.find(nme, i)
                yield ("name", i + 2, j)
                i = j + 2
                continue
            i += 2
            continue
        i += 1


def to_text(raw):
    t = raw.decode("cp932").replace("\r\n", "\n")
    for k, ch in enumerate(CIRC):
        t = t.replace(ch, f"<{k + 1}>")
    return t


def from_jp(t):
    for k, ch in enumerate(CIRC):
        t = t.replace(f"<{k + 1}>", ch)
    return t.replace("\n", "\r\n").encode("cp932")


TAG = re.compile(r"<(10|[1-9])>")


def enc_line(s):
    """English line -> pair codes. Inline codes must sit on a pair boundary: a lone char before a code is
    resolved by moving a colour start before a space, deferring <8>/<10> by one char, or padding with a space."""
    toks = [t for t in re.split(r"(<(?:10|[1-9])>)", s) if t]
    out, pend, i = [], "", 0
    seq = []                                             # flatten to chars and codes
    for t in toks:
        if TAG.fullmatch(t):
            seq.append(int(TAG.fullmatch(t).group(1)))
        else:
            seq.extend(t)
    held = []                                            # codes deferred until the pending char pairs up
    for k, x in enumerate(seq):
        if isinstance(x, int):
            if not pend:
                out.append(bytes((0x87, 0x3F + x)))
            elif x in (8, 10) and k + 1 < len(seq) and isinstance(seq[k + 1], str):
                held.append(x)
            elif pend == " ":
                out.append(bytes((0x87, 0x3F + x)))
            else:
                out.append(font.pair(pend, " ")); pend = ""
                out.append(bytes((0x87, 0x3F + x)))
            continue
        if pend:
            out.append(font.pair(pend, x)); pend = ""
            out.extend(bytes((0x87, 0x3F + h)) for h in held); held = []
        else:
            pend = x
    if pend:
        out.append(font.pair(pend, " "))
    out.extend(bytes((0x87, 0x3F + h)) for h in held)
    return b"".join(out)


def visible_len(s):
    """chars on screen after pair padding (6 px each)."""
    n = 0
    for part in TAG.split(s)[::2]:
        n += len(part)
    return n + sum(1 for _ in TAG.finditer(s))  # worst case: each code costs one padding space


def enc_en(en, kind):
    lines = en.split("\n")
    pre = "　".encode("cp932") if kind == "choice" else b""
    return b"\r\n".join(pre + enc_line(l) for l in lines)


def parse(b):
    """entries in file order: dict(kind, start, end, jp, speaker)."""
    ents, speaker = [], ""
    spans = list(scan(b))
    for k, (typ, s, e) in enumerate(spans):
        if typ == "name":
            speaker = b[s:e].decode("cp932")
            continue
        after = b[e + 2:e + 200]
        m = re.match(rb"\s*(?:cls\s*)?(command_select)", after)
        kind = "choice" if m else "msg"
        mc = b.rfind(b"map_change", 0, s)
        if kind == "msg" and mc >= 0 and b"MONO" in b[mc:b.find(b"\r\n", mc)] and b"open_meswindow" not in b[mc:s]:
            kind = "mono"   # monologue drawn as pre-rendered map graphics (MONO*.P), not the message window
        ents.append(dict(kind=kind, start=s, end=e, jp=to_text(b[s:e]), speaker=speaker if kind == "msg" else ""))
    return ents


def dump(force=False):
    OUT.mkdir(parents=True, exist_ok=True)
    for key, (d, name, b) in sources().items():
        if name in SKIP:
            continue
        ents = parse(b)
        if not ents:
            continue
        p = OUT / f"{key}.json"
        if p.exists() and not force:
            continue
        rows = [dict(id=f"{key}:{k:04d}", kind=e["kind"], speaker=e["speaker"], jp=e["jp"], en="") for k, e in enumerate(ents)]
        p.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def load(key):
    p = OUT / f"{key}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def insert(b, rows, mode="en"):
    """new file bytes. mode 'en': English where present; 'jp': re-encode jp (roundtrip); 'marker': id markers."""
    ents = parse(b)
    assert len(ents) == len(rows), "entry count changed"
    out, pos = [], 0
    for e, r in zip(ents, rows):
        assert e["jp"] == r["jp"], f"{r['id']}: jp mismatch"
        out.append(b[pos:e["start"]])
        if mode == "jp":
            out.append(from_jp(r["jp"]))
        elif mode == "marker":
            out.append(enc_en(marker(r), r["kind"]))
        elif r["en"]:
            out.append(enc_en(r["en"], r["kind"]))
        else:
            out.append(b[e["start"]:e["end"]])
        pos = e["end"]
    out.append(b[pos:])
    return b"".join(out)


def marker(r):
    lines = r["jp"].split("\n")
    tag = r["id"].split(":")[0][:10] + ":" + r["id"].split(":")[1]
    if r["kind"] == "choice":
        return "\n".join(f"{tag}.{k} choice text here" for k in range(len(lines)))
    filler = "The quick brown fox jumps over the lazy dog, then"
    return "\n".join((f"[{tag}] " + filler)[:48] if k == 0 else (f"line {k + 1} " + filler * 2)[:48] for k in range(len(lines)))


def files(mode="en"):
    """{(disc, NAME): new bytes} for every XT that has entries."""
    res = {}
    for key, (d, name, b) in sources().items():
        rows = load(key)
        if not rows:
            continue
        nb = insert(b, rows, mode)
        if key.endswith("@d2"):
            res[("d2", name)] = nb
        else:
            res[("d1", name)] = nb
            res[("d2", name)] = nb   # same content on both discs (or only on one; build ignores missing)
    return res


def roundtrip():
    bad = 0
    for key, (d, name, b) in sources().items():
        rows = load(key)
        if rows and insert(b, rows, "jp") != b:
            print("MISMATCH", key); bad += 1
    print("roundtrip", "OK" if not bad else f"{bad} bad")
    return bad == 0


def stats():
    import collections
    c = collections.Counter(); lines = collections.Counter(); chars = 0
    for p in sorted(OUT.glob("*.json")):
        for r in json.loads(p.read_text(encoding="utf-8")):
            c[r["kind"]] += 1
            lines[r["jp"].count("\n") + 1] += 1
            chars += len(r["jp"])
    print(dict(c), "lines/block", sorted(lines.items()), "jp chars", chars)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "dump":
        dump("--force" in sys.argv)
    elif cmd == "roundtrip":
        sys.exit(0 if roundtrip() else 1)
    elif cmd == "stats":
        stats()
