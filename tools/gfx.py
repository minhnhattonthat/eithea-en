"""English graphics. Each function returns {NAME.TYPE: new bytes} for build.py, plus EXE patches where needed.
  python -X utf8 tools/gfx.py preview OUTDIR   -> PNGs of every generated image
Sections: names (FONT3A name-box sprites + the speaker chain immediates in EITHEA.EXE).
"""
import pathlib
import struct
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import namebox
import tim

root = pathlib.Path(__file__).resolve().parent.parent
B1 = root / "work" / "d1" / "bind"
WIN = "C:/Windows/Fonts/"


def orig(name):
    """original archive file bytes (disc 1, else disc 2)."""
    for d in ("d1", "d2"):
        hits = sorted((root / "work" / d / "bind").glob(f"*_{name}"))
        if hits:
            return hits[0].read_bytes()
    raise FileNotFoundError(name)


# speaker id -> English name-box label (order of the EXE name list / strcmp chain)
SPEAKERS = ["Shou", "Yuka", "Hikaru", "Akiho", "Hitoshi", "Manabu", "Albaijan", "Lou", "Rando", "Fanna", "Eurike",
            "Shai", "Imul", "Materia", "Guard", "Clerk", "Villager", "Priest", "Pien", "Landlady", "Hermie", "Rea",
            "Namuria", "Myu", "Yun", "Cat", "Popo", "Prada", "Lady", "Opas", "Shopkeeper", "Karen", "Townsperson",
            "Young Man", "Young Woman", "Old Man", "Sentry", "Goddess", "Old Woman", "Shai", "Choice", "???",
            "Akiho & Yuka", "Everyone", "Cake Girl", "Emcee", "Child", "Goddess Statue", "Fino", "Moonlight Woman",
            "Fire Dragon Youth", "Soldier", "Myu", "Middle-Aged Man", "Azel", "Dragon", "Vamur", "Moonlight Girl",
            "Youth", "Shop Owner", "Shop Boy", "Vendor", "Saint of the Ele Tree", "Shou & Albaijan", "School PA",
            "Shou & Yuka"]
assert len(SPEAKERS) == 0x42


def label(text, font=WIN + "tahomabd.ttf", size=11):
    """name-box label: 16 px tall indices (0 clear, 1 outline, 15..11 fill gradient)."""
    f = ImageFont.truetype(font, size)
    w = int(f.getlength(text) + len(text)) + 4
    m = Image.new("1", (w, 16))
    d = ImageDraw.Draw(m)
    d.fontmode = "1"
    x = 2
    for c in text:                     # 1 px tracking so the outlines don't merge
        d.text((x, 1), c, font=f, fill=1)
        x += f.getlength(c) + 1
    px = m.load()
    rows = [[0] * w for _ in range(16)]
    for y in range(16):
        for x in range(w):
            if px[x, y]:
                rows[y][x] = max(11, 15 - max(0, y - 5) // 2)
    for y in range(16):
        for x in range(w):
            if not px[x, y] and any(0 <= x + dx < w and 0 <= y + dy < 16 and px[x + dx, y + dy]
                                    for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                rows[y][x] = 1
    # trim empty columns at the right
    while w > 1 and all(r[w - 1] == 0 for r in rows):
        w -= 1
    return [r[:w] for r in rows], w


def names():
    """new FONT3A.IM and {exe address: new instruction word}."""
    src = orig("FONT3A.IM")
    rows = tim.indices(src)
    W, H = len(rows[0]), len(rows)
    canvas = [[0] * W for _ in range(H)]
    place, x, y, done = {}, 0, 0, {}
    for i, t in enumerate(SPEAKERS):
        if t in done:
            place[i] = done[t]; continue
        lab, w = label(t)
        if x + w > W:
            x, y = 0, y + 16
        assert y + 16 <= H, "name sheet full"
        for yy in range(16):
            canvas[y + yy][x:x + w] = lab[yy]
        place[i] = done[t] = (x, y, w)
        x += w
    exe = namebox.EXE.read_bytes()
    patch = {}
    reg = {"s6": 22, "s5": 21, "s4": 20}
    for i, ((u, v, w), setter) in namebox.table(exe).items():
        nu, nv, nw = place[i]
        for r, val in (("s6", nu), ("s5", nv), ("s4", nw)):
            a = setter[r]
            new = 0x24000000 | reg[r] << 16 | val           # addiu rX, zero, val
            if a in patch and patch[a] != new:
                raise SystemExit(f"shared setter {hex(a)} for speaker {i}")
            patch[a] = new
    return {"FONT3A.IM": tim.write_indices(src, canvas)}, patch


def img(name):
    return tim.to_image(orig(name)).convert("RGBA")


def erase(im, box, pred, grow=2, iters=80):
    """remove pixels where pred(r,g,b) holds inside box (plus `grow` px) by diffusing the surroundings in."""
    import numpy as np
    a = np.array(im).astype(float)
    x0, y0, x1, y1 = box
    reg = a[y0:y1, x0:x1]
    mask = np.vectorize(lambda r, g, b: pred(r, g, b))(reg[..., 0], reg[..., 1], reg[..., 2]).astype(bool)
    for _ in range(grow):
        m = mask.copy(); m[1:] |= mask[:-1]; m[:-1] |= mask[1:]; m[:, 1:] |= mask[:, :-1]; m[:, :-1] |= mask[:, 1:]; mask = m
    known, cur = ~mask, reg.copy()
    for _ in range(iters):
        wsum = np.zeros(mask.shape); acc = np.zeros(reg.shape)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            k = np.roll(known, (dy, dx), (0, 1)); v = np.roll(cur, (dy, dx), (0, 1))
            wsum += k; acc += v * k[..., None]
        fill = mask & ~known & (wsum > 0)
        cur[fill] = acc[fill] / wsum[fill][:, None]; known |= fill
    a[y0:y1, x0:x1] = cur
    return Image.fromarray(a.clip(0, 255).astype("uint8"), "RGBA")


def text(im, box, s, font="tahoma.ttf", size=11, fill=(48, 48, 48), halo=(248, 248, 248), align="c", aa=True,
         spacing=2, shadow=None, stroke=1):
    """draw s (may hold \\n) centred in box with a 1 px halo."""
    f = ImageFont.truetype(WIN + font if "/" not in font else font, size)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if not aa:
        d.fontmode = "1"
    x0, y0, x1, y1 = box
    bb = d.multiline_textbbox((0, 0), s, font=f, spacing=spacing, stroke_width=stroke, align=align[0] if align != "c" else "center")
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    x = x0 + ((x1 - x0 - w) // 2 if align == "c" else 0 if align == "l" else x1 - x0 - w) - bb[0]
    y = y0 + (y1 - y0 - h) // 2 - bb[1]
    kw = dict(font=f, spacing=spacing, align="center" if align == "c" else "left" if align == "l" else "right")
    if shadow:
        d.multiline_text((x + shadow[0], y + shadow[1]), s, fill=shadow[2], stroke_width=stroke, stroke_fill=shadow[2], **kw)
    d.multiline_text((x, y), s, fill=fill, stroke_width=stroke if halo else 0, stroke_fill=halo, **kw)
    return Image.alpha_composite(im, lay)


def save(name, im, keep_unchanged=True):
    """requantize to the TIM's own CLUT; unchanged pixels keep their index."""
    src = orig(name)
    bpp, clut, rect, px = tim.read(src)
    pal = clut[0][:16 if bpp == 0 else 256]
    rgb = [tim.rgb(c) for c in pal]
    opaque = [i for i, c in enumerate(pal) if c != 0]
    old = tim.indices(src)
    ref = tim.to_image(src).convert("RGBA").load()
    p = im.load()
    W, H = im.size
    cache = {}
    rows = []
    for y in range(H):
        row = []
        for x in range(W):
            c = p[x, y]
            if keep_unchanged and c == ref[x, y]:
                row.append(old[y][x]); continue
            if c[3] < 128:
                row.append(old[y][x] if rgb[old[y][x]][3] == 0 else next((i for i, q in enumerate(pal) if q == 0), 0)); continue
            k = c[:3]
            if k not in cache:
                cache[k] = min(opaque, key=lambda i: (rgb[i][0] - k[0]) ** 2 + (rgb[i][1] - k[1]) ** 2 + (rgb[i][2] - k[2]) ** 2)
            row.append(cache[k])
        rows.append(row)
    return tim.write_indices(src, rows)


def menu():
    """ROGO0: title menu sprites, two colour sets of three 16 px rows at x 16..128."""
    im = img("ROGO0.IM")
    items = ["New Game", "Continue", "Options"]
    dark = lambda r, g, b: max(r, g, b) < 165
    blue = lambda r, g, b: b - r > 70 and b > 170 and r < 170
    for k, s in enumerate(items):
        for y0, pred, col in ((16, dark, (40, 40, 48)), (64, blue, (72, 96, 232))):
            box = (16, y0 + 16 * k, 128, y0 + 16 * k + 16)
            im = erase(im, box, pred)
            im = text(im, box, s, font="tahomabd.ttf", size=11, fill=col)
    return {"ROGO0.IM": save("ROGO0.IM", im)}


def rich(im, cx, cy, parts, halo=(250, 250, 250), shadow=(40, 70, 80, 120)):
    """one line of differently coloured/sized parts centred at (cx, cy): parts = [(text, (r,g,b), font, size)]."""
    fs = [ImageFont.truetype(WIN + f, s) for _, _, f, s in parts]
    ws = [f.getlength(t) for (t, *_), f in zip(parts, fs)]
    x = cx - sum(ws) / 2
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k, ((t, col, _, _), f, w) in enumerate(zip(parts, fs, ws)):
        asc, desc = f.getmetrics()
        y = cy - (asc + desc) / 2
        if shadow:
            d.text((x + 2, y + 3), t, font=f, fill=shadow, stroke_width=2, stroke_fill=shadow)
        x += w
    x = cx - sum(ws) / 2
    for (t, col, _, _), f, w in zip(parts, fs, ws):
        asc, desc = f.getmetrics()
        d.text((x, cy - (asc + desc) / 2), t, font=f, fill=col, stroke_width=2, stroke_fill=halo)
        x += w
    return Image.alpha_composite(im, lay)


def not_teal(r, g, b):
    return max(r, g, b) < 140 or min(r, g, b) > 226 or not (b >= r - 5 and g >= r - 5 and abs(g - b) < 60)


CHAPTERS = [  # (title card, number, [(text, accent?)])  accent part drawn bigger in the card's accent colour
    ("TITLE01.IM", 1, [("It Came ", 0), ("Suddenly", 1)], (24, 64, 200)),
    ("TITLE02.IM", 2, [("The ", 0), ("Moonlight", 1), (" Tower", 0)], (130, 130, 20)),
    ("TITLE03.IM", 3, [("The ", 0), ("Mysterious", 1), (" Artia", 0)], (30, 110, 30)),
    ("TITLE04.IM", 4, [("Carlyle, the Neutral ", 0), ("City", 1)], (190, 50, 30)),
    ("TITLE05.IM", 5, [("The ", 0), ("Past", 1), (" Revealed", 0)], (150, 30, 40)),
    ("TITLE06.IM", 6, [("The Wyvern's ", 0), ("Fang", 1)], (150, 140, 20)),
    ("TITLE07.IM", 7, [("The ", 0), ("Flames", 1), (" of Eurolia", 0)], (150, 30, 30)),
    ("TITLE08.IM", 8, [("Yamyam, the ", 0), ("Holy", 1), (" Land", 0)], (20, 40, 200)),
    ("TITLE09.IM", 9, [("The ", 0), ("Price", 1), (" of Mistakes", 0)], (130, 30, 110)),
    ("TITLE10.IM", 10, [("The ", 0), ("Three", 1), (" Witches", 0)], (110, 40, 200)),
]


def chapters():
    out = {}
    gray = (64, 64, 72)
    for name, n, parts, acc in CHAPTERS:
        im = img(name)
        im = erase(im, (16, 74, 304, 162), not_teal, grow=3, iters=150)
        im = rich(im, 160, 92, [(f"~ Chapter {n} ~", gray, "tahomabd.ttf", 13)])
        im = rich(im, 160, 122, [(t, acc if a else gray, "tahomabd.ttf", 21 if a else 17) for t, a in parts])
        out[name] = save(name, im)
    return out


def info():
    """INFO000-003: plain chapter / time-skip cards."""
    out = {}
    white_bg = lambda r, g, b: max(r, g, b) < 200          # dark text on white
    dark_bg = lambda r, g, b: min(r, g, b) > 60            # light text on black
    for name, pred, lines, col, halo in (
            ("INFO000.IM", white_bg, "~ Chapter 1 ~\nIt Came Suddenly", (40, 40, 40), None),
            ("INFO003.IM", white_bg, "~ Chapter 4 ~\nThe Town of Carlyle", (40, 40, 40), None),
            ("INFO001.IM", dark_bg, "A few minutes later...", (224, 224, 224), None),
            ("INFO002.IM", dark_bg, "30 minutes later...", (224, 224, 224), None)):
        im = img(name)
        box = (8, 60, 312, 180)
        im = erase(im, box, pred, grow=2, iters=200)
        im = text(im, box, lines, font="tahoma.ttf", size=20 if "\n" in lines else 16, fill=col, halo=halo, stroke=0, spacing=8)
        out[name] = save(name, im)
    return out


def clear(im, box):
    d = ImageDraw.Draw(im)
    d.rectangle((box[0], box[1], box[2] - 1, box[3] - 1), fill=(0, 0, 0, 0))
    return im


def result():
    """RESULT.IM battle-result sprites: white text, thick black outline."""
    im = img("RESULT.IM")
    for box, s, size in (((4, 28, 164, 64), "Victory!!", 26), ((0, 64, 54, 88), "EXP", 14), ((3, 136, 100, 160), "Obtained!", 14)):
        im = clear(im, box)
        im = text(im, box, s, font="arialbd.ttf", size=size, fill=(240, 240, 240), halo=(24, 24, 24), stroke=2)
    return {"RESULT.IM": save("RESULT.IM", im)}


def exe_patch(exe, patch):
    exe = bytearray(exe)
    for a, word in patch.items():
        struct.pack_into("<I", exe, a - namebox.BASE, word)
    return bytes(exe)


def all_files():
    files, patch = {}, {}
    f, p = names()
    files.update(f); patch.update(p)
    for sec in SECTIONS:
        files.update(sec())
    return files, patch


SECTIONS = [menu, chapters, info, result]


if __name__ == "__main__":
    if sys.argv[1] == "preview":
        out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
        files, patch = all_files()
        for n, b in files.items():
            tim.to_image(b).save(out / f"{n}.png")
        print(len(files), "images,", len(patch), "exe words")
