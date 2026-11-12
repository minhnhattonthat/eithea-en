"""World-map labels: rect table and page edits stay inside the page and match the original layout elsewhere."""
import pathlib
import struct
import sys

import pytest

root = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "tools"))
pytestmark = pytest.mark.skipif(not list((root / "work/d1/bind").glob("*_ZENTAI.P")), reason="needs unpacked discs")


def test_world_map():
    import gfx
    out = gfx.world_map("d1")
    assert set(out) == {"ZENTAI.P", "ZENTAI1.P"}
    for name, b in out.items():
        o = gfx.orig(name)
        page = gfx.MAP_PAGE[name]
        assert len(b) == len(o)
        end = gfx.MAP_RECT0 + 10 * gfx.MAP_NRECTS[name]
        assert b[:gfx.MAP_RECT0] == o[:gfx.MAP_RECT0] and b[end:page] == o[end:page] and b[page + 0x10000:] == o[page + 0x10000:]
        for k in range(1, gfx.MAP_NRECTS[name]):
            u0, v0, u1, v1 = struct.unpack_from("<4h", b, gfx.MAP_RECT0 + 10 * k)
            assert 0 <= u0 <= u1 <= 255 and 0 <= v0 <= v1 <= 255, k
    assert out["ZENTAI.P"][gfx.MAP_PAGE["ZENTAI.P"]:][:0x10000] == out["ZENTAI1.P"][gfx.MAP_PAGE["ZENTAI1.P"]:][:0x10000]
