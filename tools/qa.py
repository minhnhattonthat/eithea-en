"""QA helpers.
  python -X utf8 tools/qa.py debugstart OUT.XT [2]   -> START.XT that opens the developer menu (DEBUG.TXT) on New Game
                                                     (2: for disc 2, asks for disc 2 instead of disc 1)
Use with: tools/build.py 1 --qa-novoice --english --override START.XT=OUT.XT
Debug menu grid (3 rows per column): 0 start, 1 chapter select, 2 load / 3 voice test, 4 battle test.
"""
import pathlib
import sys

root = pathlib.Path(__file__).resolve().parent.parent

if __name__ == "__main__":
    if sys.argv[1] == "debugstart":
        b = sorted((root / "work/d1/bind").glob("*_START.XT"))[0].read_bytes()
        assert b.count(b"change IVENT01.TXT") == 1
        b = b.replace(b"change IVENT01.TXT", b"change DEBUG.TXT")
        if sys.argv[3:] == ["2"]:   # disc 2: New Game would ask for disc 1 (disk_change 1)
            assert b.count(b"disk_change 1") == 1
            b = b.replace(b"disk_change 1", b"disk_change 2")
        pathlib.Path(sys.argv[2]).write_bytes(b)
