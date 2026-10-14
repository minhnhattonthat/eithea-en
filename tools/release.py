"""Release: check -> build both discs -> leftover-Japanese gate -> xdelta3 patches -> re-apply check -> README + zip.
  python -X utf8 tools/release.py VERSION        (e.g. 1.0) -> release/Eithea_EN_vVERSION.zip
Patches are against the Redump Rev 1 .bin files in rom/. Release dirs stay local (gitignored); publishing is the
user's call.
"""
import hashlib
import pathlib
import re
import shutil
import subprocess
import sys
import zipfile
import zlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bind
import build
import text

root = pathlib.Path(__file__).resolve().parent.parent
ROMS = {1: root / "rom" / "Eithea (Japan) (Disc 1) (Rev 1).bin", 2: root / "rom" / "Eithea (Japan) (Disc 2) (Rev 1).bin"}
KANA = re.compile(rb"(?:\x82[\x9f-\xf1]|\x83[\x40-\x96])")   # hiragana / katakana codes


def hashes(p):
    h = {"md5": hashlib.md5(), "sha1": hashlib.sha1()}
    crc = 0
    with open(p, "rb") as f:
        while True:
            b = f.read(1 << 22)
            if not b:
                break
            crc = zlib.crc32(b, crc)
            for x in h.values():
                x.update(b)
    return dict(size=p.stat().st_size, crc32=f"{crc:08x}", **{k: v.hexdigest() for k, v in h.items()})


def leftover(n, out):
    """kana inside displayed 「」 blocks of the built disc's scripts (debug scripts excluded)."""
    tree = out / f"tree{n}"
    items = bind.split((tree / "CD_DATA/BIND.TBL").read_bytes(), (tree / "CD_DATA/BIND.DAT").read_bytes())
    bad = []
    for name, typ, data in items:
        if typ.strip() != "XT" or name.strip() in text.SKIP:
            continue
        for typ2, s, e in text.scan(data):              # raw spans: pair codes aren't all valid cp932
            if typ2 != "blk":
                continue
            i, kana = s, 0
            while i < e:                                 # walk code by code (a trail byte can look like a lead)
                c = data[i]
                if 0x81 <= c <= 0x9F or 0xE0 <= c <= 0xFC:
                    kana += bool(KANA.fullmatch(data[i:i + 2]))
                    i += 2
                else:
                    i += 1
            if kana:
                bad.append(f"{name.strip()}: {data[s:s + 40].decode('cp932', 'replace')!r}")
    return bad


def main(version):
    if subprocess.run([sys.executable, "-X", "utf8", str(root / "tools/check.py")]).returncode:
        raise SystemExit("check failed")
    rel = root / "release" / f"v{version}"
    if rel.exists():
        shutil.rmtree(rel)
    rel.mkdir(parents=True)
    work = root / "work" / "release"
    info = []
    for n in (1, 2):
        out = work / f"d{n}"
        out.mkdir(parents=True, exist_ok=True)
        build.build(n, out, english=True, keep_tree=True)
        bad = leftover(n, out)
        if bad:
            print("\n".join(bad[:30]))
            raise SystemExit(f"disc {n}: {len(bad)} script blocks still Japanese")
        shutil.rmtree(out / f"tree{n}")
        built = out / f"Eithea_disc{n}.bin"
        patch = rel / f"Eithea_EN_v{version}_Disc{n}.xdelta"
        subprocess.run(["xdelta3", "-e", "-9", "-f", "-s", str(ROMS[n]), str(built), str(patch)], check=True)
        test = out / "reapplied.bin"
        subprocess.run(["xdelta3", "-d", "-f", "-s", str(ROMS[n]), str(patch), str(test)], check=True)
        hb, ht = hashes(built), hashes(test)
        if hb["sha1"] != ht["sha1"]:
            raise SystemExit(f"disc {n}: re-applied patch differs from the build")
        test.unlink()
        info.append((n, hashes(ROMS[n]), hb, patch.name))
        built.unlink()
    readme = (root / "docs" / "README.template.txt").read_text(encoding="utf-8")
    rows = []
    for n, o, b, pname in info:
        rows.append(f"Disc {n}: {ROMS[n].name}\n  size {o['size']}  CRC32 {o['crc32']}\n  MD5 {o['md5']}\n  SHA-1 {o['sha1']}\n"
                    f"  patch {pname} -> patched size {b['size']}  CRC32 {b['crc32']}  SHA-1 {b['sha1']}\n")
    (rel / "README.txt").write_text(readme.replace("{VERSION}", version).replace("{HASHES}", "\n".join(rows)),
                                    encoding="utf-8", newline="\r\n")
    z = root / "release" / f"Eithea_EN_v{version}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_STORED) as zf:
        for f in sorted(rel.iterdir()):
            zf.write(f, f.name)
    print(z)


if __name__ == "__main__":
    main(sys.argv[1])
