"""Identity build: dumpsxiso each disc, mkpsxiso it back, require sha1 == original .bin.
Usage: python -X utf8 tools/identity.py [1|2 ...]   (work in work/d<N>/)"""
import hashlib
import pathlib
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parent.parent
mk = root / "tools" / "mkpsxiso-2.30-win64"


def sha1(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        while b := f.read(1 << 24):
            h.update(b)
    return h.hexdigest()


def run(n):
    orig = root / "rom" / f"Eithea (Japan) (Disc {n}) (Rev 1)"
    w = root / "work" / f"d{n}"
    w.mkdir(parents=True, exist_ok=True)
    subprocess.run([mk / "dumpsxiso.exe", "-x", w / "tree", "-s", w / "layout.xml", f"{orig}.cue"], check=True, capture_output=True)
    subprocess.run([mk / "mkpsxiso.exe", "-y", "-o", "rebuilt.bin", "-c", "rebuilt.cue", "layout.xml"], check=True, capture_output=True, cwd=w)
    return sha1(w / "rebuilt.bin") == sha1(f"{orig}.bin")


if __name__ == "__main__":
    discs = [int(a) for a in sys.argv[1:]] or [1, 2]
    ok = True
    for n in discs:
        good = run(n)
        print(f"disc {n}: {'identical' if good else 'DIFFERENT'}")
        ok &= good
    sys.exit(0 if ok else 1)
