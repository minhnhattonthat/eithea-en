"""Build a disc image from work/d<N>/ (dumpsxiso tree + layout) with optional edits.
  python -X utf8 tools/build.py N [--qa-novoice] [--out DIR]
Reads the original BIND files, applies edits to the in-memory file list, writes BIND.TBL/DAT into a copy of the
tree, runs mkpsxiso. Output: DIR/Eithea_discN.bin/.cue (default work/build/).
--qa-novoice: QA only. PCSX-Redux hangs on voice_wait (no voice ever ends), so replace it with `wait 1`.
"""
import argparse
import pathlib
import re
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bind

root = pathlib.Path(__file__).resolve().parent.parent
mk = root / "tools" / "mkpsxiso-2.30-win64" / "mkpsxiso.exe"


# whole lines `voice X`, `voice_start X`, `voice_wait`, `voice_stop` vanish; `hcls VL012` loses its voice argument
QA_VOICE = re.compile(rb"^[ \t]*(?:voice(?:_start|_wait|_stop)?\b[^\r\n]*(?:\r\n)?|(hcls)[ \t]+V[LT]\d+[^\r\n]*)", re.M)


def edit(items, qa_novoice, overrides=(), scripts=None):
    out = []
    ov = dict(o.split("=", 1) for o in overrides)  # NAME.TYPE (e.g. IVENT01.XT) -> replacement file
    for name, typ, data in items:
        key = f"{name.rstrip()}.{typ.rstrip()}"
        if scripts and typ == "XT" and name.rstrip() in scripts:
            data = scripts[name.rstrip()]
        if key in ov:
            data = pathlib.Path(ov[key]).read_bytes()
        if qa_novoice and typ == "XT":
            data = QA_VOICE.sub(lambda m: b"" if m.group(1) is None else m.group(1), data)
        out.append((name, typ, data))
    return out


def build(n, out, qa_novoice=False, overrides=(), english=False, marker=False):
    w = root / "work" / f"d{n}"
    tree = out / f"tree{n}"
    if tree.exists():
        shutil.rmtree(tree)
    shutil.copytree(w / "tree", tree)
    if english:  # pair-font hook in EITHEA.EXE + half-width font prepended to KANJI.IN/BL
        import font
        fb = out / "font"
        font.build(fb)
        import exetext
        import gfx
        files, patch = gfx.all_files()                      # English images + EXE words they need
        exe = gfx.exe_patch(exetext.apply((fb / "EITHEA.EXE").read_bytes()), patch)
        (tree / "EITHEA.EXE").write_bytes(exe)
        gd = out / "gfx"
        gd.mkdir(exist_ok=True)
        for k, b in files.items():
            (gd / k).write_bytes(b)
        overrides = [f"KANJI.IN={fb / 'KANJI.IN'}", f"KANJI.BL={fb / 'KANJI.BL'}",
                     *(f"{k}={gd / k}" for k in files), *overrides]
    cd = w / "tree" / "CD_DATA"
    scripts = None
    if english:  # translated XT scripts (text/xt/*.json); mode "marker" shows ids instead
        import text
        scripts = {nm: b for (d, nm), b in text.files(marker and "marker" or "en").items() if d == f"d{n}"}
    items = edit(bind.split((cd / "BIND.TBL").read_bytes(), (cd / "BIND.DAT").read_bytes()), qa_novoice, overrides, scripts)
    tbl, dat = bind.join(items)
    (tree / "CD_DATA" / "BIND.TBL").write_bytes(tbl)
    (tree / "CD_DATA" / "BIND.DAT").write_bytes(dat)
    lay = (w / "layout.xml").read_text(encoding="utf-8").replace('source="tree"', f'source="tree{n}"').replace("tree/license_data.dat", f"tree{n}/license_data.dat")
    (out / f"layout{n}.xml").write_text(lay, encoding="utf-8")
    subprocess.run([mk, "-y", "-o", f"Eithea_disc{n}.bin", "-c", f"Eithea_disc{n}.cue", f"layout{n}.xml"], cwd=out, check=True, capture_output=True)
    shutil.rmtree(tree)
    print(out / f"Eithea_disc{n}.cue")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("disc", type=int)
    ap.add_argument("--qa-novoice", action="store_true")
    ap.add_argument("--out", default=str(root / "work" / "build"))
    ap.add_argument("--override", action="append", default=[], help="NAME.TYPE=FILE replaces that archive file")
    ap.add_argument("--english", action="store_true", help="English font engine patch + translated scripts")
    ap.add_argument("--marker", action="store_true", help="with --english: every script block shows its id")
    a = ap.parse_args()
    o = pathlib.Path(a.out)
    o.mkdir(parents=True, exist_ok=True)
    build(a.disc, o, a.qa_novoice, a.override, a.english, a.marker)
