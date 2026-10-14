"""PS1 TIM -> PNG (4/8/16/24 bpp, first CLUT).  python -X utf8 tools/tim.py in.tim out.png [clut_index]"""
import struct
import sys

from PIL import Image


def read(d):
    assert struct.unpack_from("<I", d, 0)[0] == 0x10, "not a TIM"
    flag = struct.unpack_from("<I", d, 4)[0]
    bpp = flag & 3
    p = 8
    clut = None
    if flag & 8:
        sz, cx, cy, cw, ch = struct.unpack_from("<IHHHH", d, p)
        clut = [struct.unpack_from("<H", d, p + 12 + 2 * i)[0] for i in range(cw * ch)]
        clut = (clut, cw, ch)
        p += sz
    sz, x, y, w, h = struct.unpack_from("<IHHHH", d, p)
    return bpp, clut, (x, y, w, h), d[p + 12:p + sz]


def rgb(c):
    return ((c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3, 0 if c == 0 else 255)


def to_image(d, ci=0):
    bpp, clut, (x, y, w, h), px = read(d)
    if bpp == 2:
        im = Image.new("RGBA", (w, h))
        for i in range(w * h):
            im.putpixel((i % w, i // w), rgb(struct.unpack_from("<H", px, 2 * i)[0]))
        return im
    pal = clut[0]
    n = 16 if bpp == 0 else 256
    pal = pal[ci * n:(ci + 1) * n]
    W = w * (4 if bpp == 0 else 2)
    im = Image.new("RGBA", (W, h))
    for yy in range(h):
        for xx in range(W):
            if bpp == 0:
                b = px[yy * w * 2 + xx // 2]
                v = b >> 4 if xx & 1 else b & 15
            else:
                v = px[yy * w * 2 + xx]
            im.putpixel((xx, yy), rgb(pal[v]))
    return im


def indices(d):
    """pixel palette indices as a list of rows (4/8 bpp)."""
    bpp, clut, (x, y, w, h), px = read(d)
    W = w * (4 if bpp == 0 else 2)
    if bpp == 0:
        return [[(px[yy * w * 2 + xx // 2] >> (4 * (xx & 1))) & 15 for xx in range(W)] for yy in range(h)]
    return [list(px[yy * w * 2:(yy + 1) * w * 2]) for yy in range(h)]


def write_indices(d, rows):
    """same TIM (header, CLUT, size) with new pixel indices."""
    bpp, clut, (x, y, w, h), px = read(d)
    if bpp == 0:
        out = bytes(r[i] | r[i + 1] << 4 for r in rows for i in range(0, len(r), 2))
    else:
        out = bytes(v for r in rows for v in r)
    assert len(out) == len(px), (len(out), len(px))
    p = d.rfind(px)
    return d[:p] + out + d[p + len(px):]


if __name__ == "__main__":
    to_image(open(sys.argv[1], "rb").read(), int(sys.argv[3]) if len(sys.argv) > 3 else 0).save(sys.argv[2])
