"""Find compiler-inlined constant-string copies (lwl/lwr/lb/sb runs) that read a translated EXE string: their copy
length is fixed to the Japanese byte length, so a longer English string gets cut off.
  python -X utf8 tools/inlinecopy.py      -> prints addr, copy bytes, needed bytes for each risky site
"""
import json
import re
import struct

import capstone

import exetext

exe = exetext.EXE.read_bytes()
load, size = struct.unpack_from("<I", exe, 0x18)[0], struct.unpack_from("<I", exe, 0x1C)[0]
md = capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS32 + capstone.CS_MODE_LITTLE_ENDIAN)
md.skipdata = True
ins = list(md.disasm(exe[0x800:0x800 + size], load))
rows = {int(r["addr"], 16): r for r in json.loads(exetext.OUT.read_text(encoding="utf-8")) if r["en"]}
starts = sorted(rows)


def owner(a):
    import bisect
    k = bisect.bisect_right(starts, a) - 1
    return rows[starts[k]] if k >= 0 and a < starts[k] + rows[starts[k]]["size"] else None


for i, x in enumerate(ins):
    if x.mnemonic != "lui":
        continue
    reg, hi = x.op_str.split(", ")
    hi = int(hi, 0)
    for y in ins[i + 1:i + 6]:
        m = re.match(r"addiu (\$\w+), " + re.escape(reg) + r", (-?0x[0-9a-f]+|-?\d+)$", f"{y.mnemonic} {y.op_str}")
        if not m:
            continue
        a = ((hi << 16) + int(m.group(2), 0)) & 0xFFFFFFFF
        r = owner(a)
        if not r:
            break
        base = m.group(1)
        offs = []
        for z in ins[ins.index(y) + 1:ins.index(y) + 24]:
            mm = re.match(r"(lb|lbu|lwl|lwr|lh|lhu|lw) \$\w+, (-?0x[0-9a-f]+|-?\d+)\(" + re.escape(base) + r"\)$",
                          f"{z.mnemonic} {z.op_str}")
            if mm:
                o = int(mm.group(2), 0)
                offs.append(o + (3 if mm.group(1) in ("lwl", "lw") else 1 if mm.group(1) in ("lh", "lhu") else 0))
            if z.mnemonic in ("jal", "jr", "j"):
                break
        if offs:
            copy = max(offs) + 1
            need = len(exetext.encode(r["en"], r["size"]).rstrip(b"\x81\x40")) + 1
            flag = "CUT" if need > copy else "ok"
            print(f"{flag} site {y.address:08x} str {r['addr']} jp {r['jp']!r} en {r['en']!r} copy {copy} need {need}")
        break
