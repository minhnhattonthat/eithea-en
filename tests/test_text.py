import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "tools"))
import font
import text

HAVE_SRC = (pathlib.Path(__file__).resolve().parent.parent / "work" / "d1" / "bind").exists()
C = lambda n: bytes((0x87, 0x3F + n))
P = font.pair


def test_pair_roundtrip_and_sjis_safe():
    for a in range(0x20, 0x7E):
        for b in range(0x20, 0x7E):
            if chr(a) in "{}`|^" or chr(b) in "{}`|^":
                continue
            p = P(chr(a), chr(b))
            assert font.unpair(*p) == chr(a) + chr(b)
            assert 0x88 <= p[0] <= 0x9F or 0xE0 <= p[0] <= 0xFC
            assert 0x40 <= p[1] <= 0xFC and p[1] != 0x7F


def test_inline_codes_land_on_pair_boundaries():
    # colour start after a lone space goes before the space
    assert text.enc_line("Meet <3>Lou<8>!") == P("M", "e") + P("e", "t") + C(3) + P(" ", "L") + P("o", "u") + C(8) + P("!", " ")
    # colour end after a lone char waits for the next char
    assert text.enc_line("<3>Yoshinaga<8> said") == C(3) + P("Y", "o") + P("s", "h") + P("i", "n") + P("a", "g") + P("a", " ") + C(8) + P("s", "a") + P("i", "d")
    # otherwise pad with a space
    assert text.enc_line("ab<3>c") == P("a", "b") + C(3) + P("c", " ")
    assert text.enc_line("a<3>bc") == P("a", " ") + C(3) + P("b", "c")


@pytest.mark.skipif(not HAVE_SRC, reason="needs unpacked discs in work/")
def test_script_roundtrip():
    assert text.roundtrip()
