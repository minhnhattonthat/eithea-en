"""Opening FMV (MOVIE/OPEN1.STR): cover the Japanese cast captions with English ones.
  python -X utf8 tools/fmv.py build OUT.STR   -> patched copy of disc 1's OPEN1.STR (jPSXdec -replaceframes)
Frames are decoded once to work/fmv/fr/fNNNNNN.png. Each caption: frame range, box (320x240 coords), name, voice
actor, alignment. The box is blurred and darkened so the Japanese is unreadable, then the English is drawn.
The artistic brush-written names that animate in some shots are artwork and stay.
"""
import pathlib
import re
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

root = pathlib.Path(__file__).resolve().parent.parent
JAR = root / "tools/jpsxdec/jpsxdec_v2.0/jpsxdec.jar"
W = root / "work" / "fmv"
FONT = "C:/Windows/Fonts/"

CAPTIONS = [  # (first, last, (x0, y0, x1, y1), line1, line2, align)
    # ranges end at the next hard cut (found by frame differencing) so a caption never leaks into the next shot
    (316, 411, (132, 194, 304, 218), "song by Chihiro Yonekura", None, "r"),
    (458, 496, (28, 164, 172, 218), "Shou Niimi", "cv: Yuji Ueda", "l"),
    (563, 603, (30, 12, 172, 66), "Yuka Matsuoka", "cv: Yuka Imai", "l"),
    (665, 702, (30, 166, 172, 218), "Lou", "cv: Kotono Mitsuishi", "l"),
    (766, 813, (156, 146, 306, 218), "Hikaru Itou", "cv: Shiho Kikuchi", "r"),
    (865, 903, (124, 146, 306, 218), "Akiho Yoshinaga", "cv: Sakiko Tamagawa", "r"),
    (953, 994, (28, 164, 172, 218), "Hermie", "cv: Ikue Otani", "l"),
    (1059, 1094, (128, 164, 306, 218), "Imul", "cv: Soichiro Hoshi", "r"),
    (1128, 1162, (28, 164, 176, 218), "Albaijan", "cv: Fumihiko Tachiki", "l"),
]


def frames(src):
    if (W / "fr").exists() and len(list((W / "fr").glob("f*.png"))) >= 1357:
        return
    W.mkdir(parents=True, exist_ok=True)
    idx = W / "open1.idx"
    subprocess.run(["java", "-jar", str(JAR), "-f", str(src), "-x", str(idx)], check=True, capture_output=True)
    subprocess.run(["java", "-jar", str(JAR), "-x", str(idx), "-i", "0", "-vf", "png", "-dir", str(W / "frames"),
                    "-quality", "high"], check=True, capture_output=True)
    (W / "fr").mkdir(exist_ok=True)
    for f in (W / "frames").glob("*.png"):
        n = int(re.search(r"\[(\d+)\]\.png$", f.name).group(1))
        shutil.copy(f, W / "fr" / f"f{n:06d}.png")


def caption(im, box, l1, l2, align):
    x0, y0, x1, y1 = box
    reg = im.crop(box).filter(ImageFilter.GaussianBlur(5)).filter(ImageFilter.GaussianBlur(5))
    reg = Image.eval(reg, lambda v: int(v * 0.72))
    mask = Image.new("L", reg.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, reg.width - 1, reg.height - 1), radius=8, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(3))
    im.paste(reg, (x0, y0), mask)
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(FONT + "tahomabd.ttf", 14 if l2 else 12)
    f2 = ImageFont.truetype(FONT + "tahoma.ttf", 11)
    lines = [(l1, f1)] + ([(l2, f2)] if l2 else [])
    h = sum(f.getbbox(t)[3] + 3 for t, f in lines)
    y = y0 + (y1 - y0 - h) // 2
    for k, (t, f) in enumerate(lines):
        w = f.getlength(t)
        x = x0 + 6 + (10 if k else 0) if align == "l" else x1 - 6 - w
        d.text((x, y), t, font=f, fill=(250, 250, 250), stroke_width=1, stroke_fill=(30, 30, 40))
        y += f.getbbox(t)[3] + 3
    return im


def build(out):
    src = root / "work/d1/tree/MOVIE/OPEN1.STR"
    frames(src)
    rep = W / "rep"
    rep.mkdir(exist_ok=True)
    xml = ['<?xml version="1.0"?>', '<str-replace version="0.3">']
    for first, last, box, l1, l2, align in CAPTIONS:
        for n in range(first, last + 1):
            im = Image.open(W / "fr" / f"f{n:06d}.png").convert("RGB")
            caption(im, box, l1, l2, align).save(rep / f"f{n:06d}.png")
            x0, y0, x1, y1 = box
            xml.append(f'  <partial-replace frame="{n}" tolerance="8" rect="{x0},{y0},{x1 - x0},{y1 - y0}">'
                       f'{(rep / f"f{n:06d}.png").as_posix()}</partial-replace>')
    xml.append("</str-replace>")
    (W / "replace.xml").write_text("\n".join(xml) + "\n", encoding="utf-8")
    out = pathlib.Path(out)
    shutil.copy(src, out)
    idx = W / "patch.idx"
    subprocess.run(["java", "-jar", str(JAR), "-f", str(out), "-x", str(idx)], check=True, capture_output=True)
    r = subprocess.run(["java", "-jar", str(JAR), "-x", str(idx), "-i", "0", "-replaceframes", str(W / "replace.xml")],
                       capture_output=True, text=True)
    log = r.stdout + r.stderr
    (W / "replace.log").write_text(log, encoding="utf-8")
    if r.returncode or "does not fit" in log or "too detailed" in log:
        raise SystemExit("frame replacement failed, see work/fmv/replace.log")
    return out


if __name__ == "__main__":
    if sys.argv[1] == "build":
        print(build(sys.argv[2]))
