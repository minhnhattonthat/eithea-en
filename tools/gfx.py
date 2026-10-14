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
    bb = d.multiline_textbbox((0, 0), s, font=f, spacing=spacing, stroke_width=stroke,
                              align={"c": "center", "l": "left", "r": "right"}[align])
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


def fit_text(im, box, s, font, fill, halo, max_size=12, min_size=7, align="l", stroke=1):
    """largest size (<= max_size) whose text fits the box."""
    for size in range(max_size, min_size - 1, -1):
        f = ImageFont.truetype(WIN + font, size)
        bb = f.getbbox(s, stroke_width=stroke)
        if bb[2] - bb[0] <= box[2] - box[0] and bb[3] - bb[1] <= box[3] - box[1] + 2:
            break
    return text(im, box, s, font=font, size=size, fill=fill, halo=halo, align=align, stroke=stroke)


def option():
    """OPTION.IM option-menu labels (sprite rects = the original label bounding boxes)."""
    im = img("OPTION.IM")
    ink, glow = (32, 32, 32), (236, 236, 236)
    labels = [((0, 27, 49, 40), "Sound"), ((0, 43, 49, 56), "Vibration"), ((0, 59, 85, 72), "Window Opacity"),
              ((0, 106, 26, 120), "Voice"), ((0, 123, 85, 136), "Memory Album"),
              ((1, 138, 50, 151), "Stereo"), ((59, 138, 108, 151), "Mono")]
    im = clear(im, (3, 2, 93, 21))
    im = fit_text(im, (3, 2, 93, 21), "Options", "arialbd.ttf", (120, 232, 96), (24, 72, 24), max_size=18, align="c", stroke=2)
    for box, s in labels:
        im = clear(im, box)
        im = fit_text(im, box, s, "ARIALNB.TTF", ink, glow, max_size=13)
    return {"OPTION.IM": save("OPTION.IM", im)}


def buttons():
    """FONT.IM top row: button-legend words (ケッテイ キャンセル セツメイ センタク, TIP◆センタク)."""
    im = img("FONT.IM")
    bold = [((0, 0, 40, 10), "OK"), ((40, 0, 87, 10), "Cancel"), ((88, 0, 128, 10), "Info")]
    for box, s in bold:
        im = clear(im, box)
        im = fit_text(im, box, s, "tahomabd.ttf", (240, 240, 240), (40, 40, 40), max_size=10, align="c")
    for box in ((129, 0, 165, 10), (193, 0, 230, 10)):
        im = clear(im, box)
        im = fit_text(im, box, "Select", "tahoma.ttf", (230, 230, 230), None, max_size=10, align="c", stroke=0)
    return {"FONT.IM": save("FONT.IM", im)}


def album():
    """OMOI1.IM memory-album menu: heroine names + その他 (others)."""
    im = img("OMOI1.IM")
    for (a, b), s in zip(((4, 21), (26, 45), (51, 70), (75, 93), (99, 117), (122, 141)),
                         ("Yuka", "Hikaru", "Akiho", "Lou", "Hermie", "Others")):
        im = clear(im, (0, a, 60, b))
        im = fit_text(im, (0, a, 54, b), s, "tahomabd.ttf", (255, 236, 244), (176, 0, 24), max_size=12, align="c", stroke=2)
    return {"OMOI1.IM": save("OMOI1.IM", im)}


def note():
    """EVCHI.IM: handwritten 地下室 ("basement") on white paper."""
    im = img("EVCHI.IM")
    im = erase(im, (8, 8, 312, 232), lambda r, g, b: max(r, g, b) < 170, grow=2, iters=60)
    im = text(im, (20, 60, 300, 180), "Basement", font="Inkfree.ttf", size=58, fill=(40, 40, 40), halo=None, stroke=0)
    return {"EVCHI.IM": save("EVCHI.IM", im)}


def mono_pages(p, base=0x14CF0):
    """256x256 4bpp texture pages inside a MONO*.P map file: [(offset, 256x256 index array)]."""
    import numpy as np
    out, o = [], base % 0x8200
    while o + 0x8000 <= len(p):
        if o >= 0x200:
            a = np.frombuffer(p[o:o + 0x8000], np.uint8).reshape(256, 128)
            px = np.zeros((256, 256), np.uint8); px[:, 0::2] = a & 15; px[:, 1::2] = a >> 4
            out.append((o, px))
        o += 0x8200
    return out


def paragraphs(px, bg, gap=3):
    """text blocks in a page: [(x0, y0, x1, y1)] split where more than `gap` rows step separates text rows
    (lines inside a paragraph are 2-3 rows apart, paragraphs 4+)."""
    import numpy as np
    m = px != bg
    rows = np.nonzero(m.any(axis=1))[0]
    blocks, start, prev = [], None, None
    for y in rows:
        if start is None:
            start = y
        elif y - prev > gap:
            blocks.append((start, prev)); start = y
        prev = y
    if start is not None:
        blocks.append((start, prev))
    out = []
    for a, b in blocks:
        cols = np.nonzero(m[a:b + 1].any(axis=0))[0]
        out.append((int(cols.min()), int(a), int(cols.max()) + 1, int(b) + 1))
    return out


def glow_text(w, h, s, font="tahomabd.ttf", max_size=13):
    """levels 0..15: white core (15) with a soft glow (1..6), centred lines; largest size that fits."""
    import numpy as np
    from PIL import ImageFilter
    words = s.replace("\n", " ").split()
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    for size in range(max_size, 6, -1):
        f = ImageFont.truetype(WIN + font, size)
        lines, cur = [], ""
        for wd in words:                                    # greedy wrap to the block width
            t = f"{cur} {wd}".strip()
            if cur and f.getlength(t) > w - 6:
                lines.append(cur); cur = wd
            else:
                cur = t
        lines.append(cur)
        s = "\n".join(lines)
        bb = d.multiline_textbbox((0, 0), s, font=f, spacing=2, align="center")
        if bb[2] - bb[0] <= w - 4 and bb[3] - bb[1] <= h - 2:
            break
    core = Image.new("L", (w, h))
    d = ImageDraw.Draw(core)
    d.multiline_text(((w - (bb[2] - bb[0])) // 2 - bb[0], (h - (bb[3] - bb[1])) // 2 - bb[1]), s, font=f,
                     fill=255, spacing=2, align="center")
    glow = core.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1))
    c, g = np.array(core) / 255.0, np.array(glow) / 255.0
    lev = np.maximum(np.round(c * 9 + (c > 0.1) * 6), np.round(np.minimum(g * 2, 1) * 6) * (g > 0.05))
    return np.clip(lev, 0, 15).astype(np.uint8)


# MONO*.P: (page base offset, texts for the auto-detected blocks in page order, top to bottom). A text is a script
# row id, literal English, or [(lines, text), ...] to split one detected block whose JP paragraphs touch.
MONO = {
    ("d1", "MONO1.P"): (0x14CF0, ["IVENT01:0000", "But I don't know if that's my real name.", "IVENT01:0001",
                                  "IVENT01:0002", "IVENT01:0003", "IVENT01:0004", "IVENT01:0005",
                                  "IVENT02B:0110", "IVENT02B:0111"]),
    ("d2", "MONO2.P"): (0x5410, [
        "And so, our adventure in the other world of Eithéa ended, and we came back to our own world.",
        "A world without dragons, and without any oddball princes, either.",
        "Sometimes I even wonder if everything that happened in that world was just a dream.",
        "Just like the future of our own world...",
        "But we all remember what happened there, and Hitoshi and Manabu seem to like it so much they still haven't come back.",
        "After we got back, I found out we'd only been missing for a few hours.",
        "It seems we'd been listed as missing in all the commotion.",
        "Whoever summoned us... I'd guess the \"Saint of the Ele Tree\"... must have sent just the school back ahead of us.",
        [(3, "Honestly, I still don't really know if what we did in Eithéa was right or not."),
         (5, "Right after the earthquake, the whole school was suddenly reduced to ruins, and there was total panic, apparently.")],
        "But I only ever did what I believed was right, and in the end, that's about all I can do.",
        "Sometimes I get nostalgic about Eithéa, but I don't think I'll ever go back there again.",
        "The future of Eithéa is for the people who live there to carve out together.",
        "Isn't that right, Lou...?"]),
    ("d2", "MONO4.P"): (0x5440, [
        "And so, our adventure in Eithéa, another world, came to an end.",
        "As for me, I chose to stay and live in this world with Hermie.",
        "But I only ever did what I believed was right, and in the end, that's about all I can do.",
        "Well, if you think about it, this place is kind of like my hometown anyway.",
        "When I told everyone I was staying, I think Yuka even cried...",
        "Sensei called me a \"lolicon,\" and Itou-san gave me the cold shoulder. It was rough.",
        "Still, what happened here is a precious memory for all of us, and Hitoshi and Manabu seem so comfortable they show no sign of going back.",
        "Oh, and the other day, Albaijan and Namuria had their wedding.",
        "Knowing Namuria, Albaijan is sure to end up under her thumb...",
        "Imul's still busy chasing girls as ever. As for Lou, who knows what got into her, but I hear she's been training to be a bride every day.",
        [(1, "Well, that's how peaceful it is."),
         (4, "Honestly, I still don't really know if what we did in Eithéa was right or not.")],
        [(4, "Sometimes I miss my old world, but I'll probably never go back there again."),
         (4, "Eithéa's future is something we'll have to carve out with our own strength.")]]),
}
MONO["d2", "MONO3.P"] = MONO["d2", "MONO2.P"]   # identical file


def mono_text(ref):
    if ":" not in ref or " " in ref:
        return ref
    key, idx = ref.rsplit(":", 1)
    import json, text as T
    r = json.loads((T.OUT / f"{key}.json").read_text(encoding="utf-8"))[int(idx)]
    return r["en"].replace("<p>", "\n")


def mono(only=None):
    """replace the monologue text pages; returns {NAME.P: bytes} per disc via MONO_FILES."""
    import numpy as np
    out = {}
    for (disc, name), (base, refs) in MONO.items():
        if only and disc != only:
            continue
        src = (sorted((root / "work" / disc / "bind").glob(f"*_{name}"))[0]).read_bytes()
        p = bytearray(src)
        blocks = []
        for o, px in mono_pages(src, base):
            vals, cnt = np.unique(px, return_counts=True)
            bg = int(vals[cnt.argmax()])
            if (px != bg).sum() == 0:
                continue
            for box in paragraphs(px, bg):
                if box[3] - box[1] > 3:                 # skip 1-2 row decorations
                    blocks.append((o, px, bg, box))
        assert len(blocks) == len(refs), f"{name}: {len(blocks)} text blocks, {len(refs)} texts"
        jobs = []
        for (o, px, bg, (x0, y0, x1, y1)), ref in zip(blocks, refs):
            if isinstance(ref, list):                   # split a block by line counts
                pitch, a = (y1 - y0) / sum(n for n, _ in ref), 0
                for n, t in ref:
                    ya, yb = int(y0 + a * pitch), int(y0 + (a + n) * pitch)
                    cols = np.nonzero((px[ya:yb] != bg).any(axis=0))[0]
                    jobs.append((o, px, bg, (int(cols.min()), ya, int(cols.max()) + 1, yb), t))
                    a += n
            else:
                jobs.append((o, px, bg, (x0, y0, x1, y1), ref))
        pages = {}
        for o, px, bg, (x0, y0, x1, y1), ref in jobs:
            px = pages.setdefault(o, px.copy())
            X0, Y0, X1, Y1 = max(0, x0 - 4), max(0, y0 - 2), min(256, x1 + 4), min(256, y1 + 2)
            lev = glow_text(X1 - X0, Y1 - Y0, mono_text(ref))
            px[Y0:Y1, X0:X1] = bg
            idx = lev if bg == 0 else 15 - lev
            region = px[Y0:Y1, X0:X1]
            region[lev > 0] = idx[lev > 0]
        for o, px in pages.items():
            p[o:o + 0x8000] = (px[:, 0::2] | (px[:, 1::2] << 4)).astype(np.uint8).tobytes()
        out[name] = bytes(p)
    return out


def exe_patch(exe, patch):
    exe = bytearray(exe)
    for a, word in patch.items():
        struct.pack_into("<I", exe, a - namebox.BASE, word)
    return bytes(exe)


def all_files(disc="d1"):
    """{NAME.TYPE: bytes} for this disc's archive, and {EXE address: word}."""
    files, patch = {}, {}
    f, p = names()
    files.update(f); patch.update(p)
    for sec in SECTIONS:
        files.update(sec())
    files.update(mono(disc))
    return files, patch


SECTIONS = [menu, chapters, info, result, option, buttons, album, note]


if __name__ == "__main__":
    if sys.argv[1] == "preview":
        out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
        files, patch = all_files()
        for n, b in files.items():
            tim.to_image(b).save(out / f"{n}.png")
        print(len(files), "images,", len(patch), "exe words")
