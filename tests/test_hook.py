"""Run asm/font.asm's strcat hook and party-name routine in a MIPS emulator (unicorn)."""
import pathlib
import re
import sys
import tempfile

import pytest

root = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "tools"))
import font

unicorn = pytest.importorskip("unicorn")
from unicorn import UC_HOOK_CODE, Uc,UC_ARCH_MIPS, UC_MODE_MIPS32, UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_RA, UC_MIPS_REG_V0, UC_MIPS_REG_PC, UC_MIPS_REG_T9, UC_MIPS_REG_SP

pytestmark = pytest.mark.skipif(not (root / "work/d1/tree/EITHEA.EXE").exists() or not (root / "tools/armips/armips.exe").exists(),
                                reason="needs the unpacked disc and armips")

K = 0x80000000
CODE, DEST, SRC, STOP = K + 0x10000, K + 0x20000, K + 0x21000, K + 0x30000
FALLBACK = 0x8006B2F4


@pytest.fixture(scope="module")
def hook():
    d = pathlib.Path(tempfile.mkdtemp())
    font.build(d)
    sym = {p[1]: int(p[0], 16) for p in (l.split() for l in (d / "fontext.sym").read_text().splitlines()) if len(p) == 2}
    ext = (d / "KANJI.IN").read_bytes()[font.CODEOFF:font.CODEOFF + 2000]
    return ext, sym


def run(hook, dest, src):
    ext, sym = hook
    uc = Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 + UC_MODE_LITTLE_ENDIAN)
    uc.mem_map(0, 0x100000)
    for a in (CODE, DEST, SRC, STOP):
        pass
    uc.mem_write(CODE & 0x1FFFFFFF, ext)
    uc.mem_write(DEST & 0x1FFFFFFF, dest + b"\0" * 64)
    uc.mem_write(SRC & 0x1FFFFFFF, src + b"\0")
    uc.reg_write(UC_MIPS_REG_A0, DEST)
    uc.reg_write(UC_MIPS_REG_A1, SRC)
    uc.reg_write(UC_MIPS_REG_RA, STOP)
    uc.reg_write(UC_MIPS_REG_SP, 0x80080000)                # the original strcat prologue pushes s1
    uc.mem_write(STOP & 0x1FFFFFFF, b"\0" * 8)
    start = CODE + sym["strcat_hook"]
    hit = []                                                # fetching exactly the original strcat body = fallback
    uc.hook_add(UC_HOOK_CODE, lambda u, a, s, d: (hit.append(a), u.emu_stop()), begin=FALLBACK, end=FALLBACK)
    uc.emu_start(start, STOP, count=20000)
    if hit:
        return None
    out = bytes(uc.mem_read(DEST & 0x1FFFFFFF, 80)).split(b"\0")[0]
    return out, uc.reg_read(UC_MIPS_REG_V0)


def run_tramp(tmp_build, ptr, block, start, size=0x60):
    """strcat trampoline (EXE) with 0x800e6e54 = ptr; returns the executed addresses."""
    exe = (tmp_build / "EITHEA.EXE").read_bytes()
    uc = Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 + UC_MODE_LITTLE_ENDIAN)
    uc.mem_map(0, 0x200000)
    off = start - 0x80010000 + 0x800
    uc.mem_write(start & 0x1FFFFFFF, exe[off:off + size])
    uc.mem_write(0x6B2F4 - 0x10, b"\0" * 0x20)
    uc.mem_write(0xE6E54, ptr.to_bytes(4, "little"))
    if block is not None:
        uc.mem_write(0x118000, block)
    uc.reg_write(UC_MIPS_REG_A0, K + 0x20000)
    uc.reg_write(UC_MIPS_REG_A1, K + 0x21000)
    uc.reg_write(UC_MIPS_REG_RA, STOP)
    left = []
    from unicorn import UC_HOOK_CODE
    uc.hook_add(UC_HOOK_CODE, lambda u, a, s, ud: left.append(a))
    try:
        uc.emu_start(start, 0, count=40)
    except Exception:
        pass
    return left


def test_trampoline_guard_rejects_stale_pointers(hook, tmp_path):
    ext, sym = hook
    font.build(tmp_path)
    kin = (tmp_path / "KANJI.IN").read_bytes()
    start, fallback_pc = sym["strcat_tramp"], sym["strcat_orig"]
    hook_pc = K + 0x118000 + font.CODEOFF + sym["strcat_hook"]
    good = run_tramp(tmp_path, 0x80118000, kin[:4096], start)
    assert hook_pc in good and fallback_pc not in good      # marker present: enters the ext code
    for ptr, blk in ((0, None), (0x12345678, None), (0x80118002, kin[:4096]), (0x80118000, bytes(4096)),
                     (0x80300000, None), (0x800f0000, None)):
        seen = run_tramp(tmp_path, ptr, blk, start)
        assert fallback_pc in seen, hex(ptr)
        assert not any(a >= K + 0x100000 for a in seen), hex(ptr)   # never jumped into the font block


def dec(b):
    return "".join(font.unpair(b[i], b[i + 1]) for i in range(0, len(b), 2)).replace(font.PAD, "~PAD~")


def test_odd_name_merges_into_one_space(hook):
    out, v0 = run(hook, font.encode("Doggy", font.PAD), font.encode(" defeated!", font.PAD))
    assert dec(out).rstrip("~PAD~").rstrip() == "Doggy defeated!" and v0 == DEST


def test_punctuation_piece_loses_the_pad(hook):
    out, _ = run(hook, font.encode("Akiho", font.PAD), font.encode(", choose a command!", font.PAD))
    assert dec(out).replace("~PAD~", "").rstrip() == "Akiho, choose a command!"


def test_even_name_falls_back_to_plain_strcat(hook):
    assert run(hook, font.encode("Hikaru", font.PAD), font.encode(" defeated!", font.PAD)) is None


def test_ascii_dest_untouched(hook):
    assert run(hook, b"BG01_E", b".MP") is None


def test_odd_piece_then_odd_piece(hook):
    out, _ = run(hook, font.encode("Lou", font.PAD), font.encode(" used ", font.PAD))
    assert dec(out).replace("~PAD~", "").rstrip() == "Lou used"
