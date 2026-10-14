"""Name-box sprites: speaker id -> (u, v, w) in FONT3A.TIM, set by an if-chain in EITHEA.EXE at 0x8002a3e4.
  python -X utf8 tools/namebox.py table      -> print id, u, v, w and the instruction addresses that set them
Used by tools/gfx.py to re-layout FONT3A with English names and patch the chain's immediates.
"""
import struct
import pathlib

import capstone

root = pathlib.Path(__file__).resolve().parent.parent
EXE = root / "work" / "d1" / "tree" / "EITHEA.EXE"
BASE = 0x80010000 - 0x800
START, SPK = 0x8002A3E4, 0x8008BD90
REGS0 = {"s7": 2, "fp": 5, "s0": 8, "zero": 0}


def sim(exe, idx):
    md = capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS32 + capstone.CS_MODE_LITTLE_ENDIAN)
    r = dict(REGS0)
    setter = {}
    pc, pending = START, None
    for _ in range(4000):
        ins = next(md.disasm(exe[pc - BASE:pc - BASE + 4], pc))
        ops = [o.strip().lstrip("$") for o in ins.op_str.split(",")]
        m = ins.mnemonic
        nxt = pc + 4
        val = lambda o: r.get(o, 0) if not o.lstrip("-").startswith("0x") and not o.lstrip("-").isdigit() else int(o, 0)
        target = None
        if m == "jal":
            break
        if m in ("addiu", "addu"):
            r[ops[0]] = (val(ops[1]) + val(ops[2])) & 0xFFFFFFFF
        elif m == "move":
            r[ops[0]] = val(ops[1])
        elif m == "lui":
            r[ops[0]] = (int(ops[1], 0) << 16) & 0xFFFFFFFF
        elif m == "andi":
            r[ops[0]] = val(ops[1]) & int(ops[2], 0)
        elif m == "lbu":
            r[ops[0]] = idx  # the speaker byte
        elif m in ("bne", "beq"):
            take = (val(ops[0]) != val(ops[1])) == (m == "bne")
            target = int(ops[2], 0) if take else None
        elif m in ("bnez", "beqz"):
            take = (val(ops[0]) != 0) == (m == "bnez")
            target = int(ops[1], 0) if take else None
        elif m in ("j", "b"):
            target = int(ops[0], 0)
        elif m == "nop" or m.startswith("s") and m in ("sw", "sh", "sb"):
            pass
        if ops and ops[0] in ("s6", "s5", "s4") and m in ("addiu", "move"):
            setter[ops[0]] = pc
        if pending is not None:
            pc, pending = pending, None
            continue
        if target is not None:
            pending = target
        pc = nxt
    return (r.get("s6", 0), r.get("s5", 0), r.get("s4", 0)), setter


def table(exe=None):
    exe = exe or EXE.read_bytes()
    return {i: sim(exe, i) for i in range(0x42)}


if __name__ == "__main__":
    for i, ((u, v, w), st) in table().items():
        print(f"{i:02x} u={u:3d} v={v:3d} w={w:3d}", {k: hex(a) for k, a in st.items()})
