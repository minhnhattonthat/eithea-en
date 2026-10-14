"""BIND.DAT/BIND.TBL archive tool.
TBL = 13-byte entries: name[8] type[2] size[3, big-endian]. DAT = files back to back, each padded to 2048.
  python -X utf8 tools/bind.py unpack TBL DAT OUTDIR   -> OUTDIR/<idx:04d>_<name>.<type>, OUTDIR/index.txt
  python -X utf8 tools/bind.py pack OUTDIR TBL DAT      (uses index.txt order)
  python -X utf8 tools/bind.py roundtrip TBL DAT        (unpack+pack in memory, require identical bytes)
"""
import pathlib
import sys

SEC = 2048


def entries(tbl):
    for i in range(0, len(tbl) - 12, 13):
        e = tbl[i:i + 13]
        yield e[:8].decode("latin-1"), e[8:10].decode("latin-1"), int.from_bytes(e[10:13], "big")


def split(tbl, dat):
    """-> [(name8, type2, bytes)] ; raises if the table doesn't cover the DAT exactly."""
    out, pos = [], 0
    for name, typ, size in entries(tbl):
        out.append((name, typ, dat[pos:pos + size]))
        pos += (size + SEC - 1) // SEC * SEC
    if pos != len(dat) or len(tbl) % 13:
        raise ValueError(f"table covers {pos} of {len(dat)} bytes")
    return out


def join(items):
    tbl, dat = bytearray(), bytearray()
    for name, typ, data in items:
        if len(data) >= 1 << 24:
            raise ValueError(f"{name} too big for a 24-bit size")
        tbl += name.encode("latin-1") + typ.encode("latin-1") + len(data).to_bytes(3, "big")
        dat += data + b"\0" * (-len(data) % SEC)
    return bytes(tbl), bytes(dat)


def fname(i, name, typ):
    safe = lambda s: "".join(c if c.isascii() and (c.isalnum() or c in "_-") else f"%{ord(c):02x}" for c in s.rstrip())
    return f"{i:04d}_{safe(name)}.{safe(typ) or '_'}"


def main(a):
    cmd = a[0]
    if cmd == "unpack":
        out = pathlib.Path(a[3])
        out.mkdir(parents=True, exist_ok=True)
        lines = []
        for i, (name, typ, data) in enumerate(split(open(a[1], "rb").read(), open(a[2], "rb").read())):
            (out / fname(i, name, typ)).write_bytes(data)
            lines.append(f"{name}|{typ}|{fname(i, name, typ)}")
        (out / "index.txt").write_text("\n".join(lines) + "\n", encoding="latin-1")
    elif cmd == "pack":
        src = pathlib.Path(a[1])
        items = []
        for ln in (src / "index.txt").read_text(encoding="latin-1").split("\n")[:-1]:
            name, typ, f = ln.split("|")
            items.append((name, typ, (src / f).read_bytes()))
        tbl, dat = join(items)
        open(a[2], "wb").write(tbl)
        open(a[3], "wb").write(dat)
    elif cmd == "roundtrip":
        tbl, dat = open(a[1], "rb").read(), open(a[2], "rb").read()
        t2, d2 = join(split(tbl, dat))
        ok = t2 == tbl and d2 == dat
        print("roundtrip", "OK" if ok else "FAIL (padding bytes differ?)", len(tbl) // 13, "files")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main(sys.argv[1:])
