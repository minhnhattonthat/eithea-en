"""Scan a PS-X EXE's MIPS code for instructions matching a regex over 'mnemonic op_str'.
  python -X utf8 tools/mipsscan.py EXE REGEX [context_before] [context_after]
e.g. mipsscan.py work/d1/tree/EITHEA.EXE "addiu .*, 0x6df0" 0 8
"""
import re
import struct
import sys

import capstone

exe = open(sys.argv[1], "rb").read()
pat = re.compile(sys.argv[2])
before = int(sys.argv[3]) if len(sys.argv) > 3 else 0
after = int(sys.argv[4]) if len(sys.argv) > 4 else 0
load, size = struct.unpack_from("<I", exe, 0x18)[0], struct.unpack_from("<I", exe, 0x1C)[0]
code = exe[0x800:0x800 + size]
md = capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS32 + capstone.CS_MODE_LITTLE_ENDIAN)
md.skipdata = True  # the EXE starts with a data block; keep decoding past undecodable words
ins = list(md.disasm(code, load))
for i, x in enumerate(ins):
    if pat.search(f"{x.mnemonic} {x.op_str}"):
        print("----")
        for y in ins[max(0, i - before):i + after + 1]:
            print(f"{y.address:08x}  {y.mnemonic:8s} {y.op_str}")
