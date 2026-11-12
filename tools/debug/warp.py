"""Warp to any dev-menu scene from a cold boot (debug tool, phase 8 QA).

The developer menu DEBUG.XT (one per disc; disc 1: ch1-5, disc 2: ch6-10 + endings/epilogues) lists every chapter
start, dungeon and ending. A QA build opens it on New Game; each scene = the cursor presses through its menus.

  python -X utf8 tools/debug/warp.py list [N]             scene names (d<N>_<label>), menu path, target script
  python -X utf8 tools/debug/warp.py build N              QA build -> work/build_qa (dev menu on New Game, no voice)
  python -X utf8 tools/debug/warp.py state N              cold boot to the dev menu -> work/states/devmenu_d<N>.sstate
  python -X utf8 tools/debug/warp.py run SCENE.. [--frames F] [--every E] [--out DIR]   -> DIR/<scene>/sheet*.png
  python -X utf8 tools/debug/warp.py tour N [--frames F] [--jobs J]  every scene of disc N -> work/qa/tour_d<N>/
Runs mash circle after the warp to click through dialogue. Rebuild + `state` after any build change.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

root = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "tools"))
from skill import SKILL

BUILD = root / "work" / "build_qa"
STATES = root / "work" / "states"
BIOS = root / "tools" / "pcsx-redux" / "bios" / "SCPH-5500.bin"
BOOT = "13200 -;4 circle;700 -"   # title -> New Game -> dev menu (menu up by ~13900)


def blocks(n):
    """[(label, [lines])] in file order; tab comments and ; lines dropped."""
    f = next((root / "work" / f"d{n}" / "bind").glob("*_DEBUG.XT"))
    out = []
    for l in f.read_text(encoding="cp932").splitlines():
        l = l.split("\t")[0].strip()
        if not l or l.startswith((";", "//")):
            continue
        m = re.fullmatch(r"\*{5}(\d+)", l)
        if m:
            out.append((int(m[1]), []))
        elif out:
            out[-1][1].append(l)
    return out


def en_cells(n):
    """JP choice block text -> English cells in cursor order (column-major, 3 rows per column)."""
    p = root / "text" / "xt" / ("DEBUG@d2.json" if n == 2 else "DEBUG.json")
    out = {}
    for r in json.loads(p.read_text(encoding="utf-8")):
        rows = [re.split(r"\s{2,}", l.strip()) for l in r["en"].split("\n")]
        out[re.sub(r"\s", "", r["jp"])] =[c[k] for k in (0, 1) for c in rows if len(c) > k]
    return out


def scenes(n):
    """{name: (presses, desc, target)}; presses = cursor index per menu level."""
    bl = blocks(n)
    idx = {lab: i for i, (lab, _) in enumerate(bl)}
    cells = en_cells(n)

    def resolve(i):
        """Follow goto / fall-through from block i: ('menu', i, opts) or ('leaf', target) or None."""
        seen = set()
        while i < len(bl) and i not in seen:
            seen.add(i)
            lines = bl[i][1]
            sj = [l for l in lines if l.startswith("select_jump")]
            if sj:
                if any(l.startswith("battle ") for l in lines):   # battle test: fights, then asks again/back
                    return "leaf", next(l for l in lines if l.startswith("battle "))
                txt = re.sub(r"\s", "", "".join(lines).split("「", 1)[1].split("」")[0])
                return "menu", i, [int(x) for x in sj[0].split(None, 1)[1].split(",")], cells.get(txt, [])
            ch = [l.split()[1].strip('"') for l in lines if l.startswith("change ")]
            if ch:
                return ("leaf", ch[0]) if ch[0] != "START.TXT" else None
            gt = [l for l in lines if l.startswith("goto")]
            i = idx[int(gt[0].split()[1])] if gt else i + 1
        return None

    out, seen, queue = {}, set(), [(resolve(0), [], [])]
    while queue:
        node, path, desc = queue.pop(0)
        if node[1] in seen:
            continue
        seen.add(node[1])
        _, _, opts, names = node
        for k, lab in enumerate(opts):
            if lab not in idx:
                continue
            r = resolve(idx[lab])
            d = desc + [names[k] if k < len(names) else str(lab)]
            if r is None:
                continue
            if r[0] == "menu":
                queue.append((r, path + [k], d))
            elif f"d{n}_{lab}" not in out:
                out[f"d{n}_{lab}"] = (path + [k], " / ".join(d), r[1])
    return out


def route(presses):
    """Cursor starts on item 0 of each menu: right per column, down per row, circle."""
    steps = ["30 -"]
    for k in presses:
        steps += ["4 right;20 -"] * (k // 3) + ["4 down;20 -"] * (k % 3) + ["4 circle;90 -"]
    return ";".join(steps)


def emu(n, out, *args):
    cmd = [sys.executable, "-X", "utf8", str(pathlib.Path(SKILL) / "scripts" / "emu.py"),
           str(BUILD / f"Eithea_disc{n}.cue"), "--out", str(out), "--bios", str(BIOS), "--timeout", "1200", *args]
    return subprocess.run(cmd, capture_output=True, text=True)


def run(name, frames, every, outdir):
    n = int(name[1])
    presses, desc, target = scenes(n)[name]
    out = outdir / name
    r = emu(n, out, "--state-in", str(STATES / f"devmenu_d{n}.sstate"), "--route-str", route(presses),
            "--frames", str(frames), "--shot-every", str(every), "--mash", "60", "--mash-key", "circle", "--sheet")
    (out / "scene.txt").write_text(f"{name}\t{desc}\t{target}\n", encoding="utf-8")
    print(name, "exit", r.returncode, desc, "->", target, flush=True)
    return r.returncode


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "build", "state", "run", "tour"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--frames", type=int, default=3600)
    ap.add_argument("--every", type=int, default=60)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out", help="default work/qa/tour_d<N> (qa_gate manifest: work/qa/d<N>/)")
    a = ap.parse_args()
    a.out = a.out or str(root / "work" / "qa" / f"tour_d{(a.args or ['d1'])[0].lstrip('d')[0]}")
    if a.cmd == "list":
        for n in map(int, a.args or ["1", "2"]):
            for k, (p, d, t) in scenes(n).items():
                print(f"{k}\t{','.join(map(str, p))}\t{d}\t{t}")
    elif a.cmd == "build":
        n = a.args[0]
        xt = root / "work" / f"qa_START_d{n}.XT"
        subprocess.run([sys.executable, "-X", "utf8", str(root / "tools/qa.py"), "debugstart", str(xt), n], check=True)
        sys.exit(subprocess.run([sys.executable, "-X", "utf8", str(root / "tools/build.py"), n, "--english", "--qa-novoice",
                                 "--override", f"START.XT={xt}", "--out", str(BUILD)]).returncode)
    elif a.cmd == "state":
        n = int(a.args[0])
        r = emu(n, root / "work" / "qa" / f"devboot{n}", "--route-str", BOOT, "--state-out", str(STATES / f"devmenu_d{n}.sstate"))
        print(r.stdout[-300:], r.stderr[-300:])
        sys.exit(r.returncode)
    elif a.cmd == "run":
        sys.exit(max(run(s, a.frames, a.every, pathlib.Path(a.out)) for s in a.args))
    else:
        names = list(scenes(int(a.args[0])))
        with ThreadPoolExecutor(a.jobs) as ex:
            codes = list(ex.map(lambda s: run(s, a.frames, a.every, pathlib.Path(a.out)), names))
        sys.exit(max(codes))
