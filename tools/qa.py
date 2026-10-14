"""QA helpers.
  python -X utf8 tools/qa.py debugstart OUT.XT   -> START.XT that opens the developer menu (DEBUG.TXT) on New Game
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
        pathlib.Path(sys.argv[2]).write_bytes(b.replace(b"change IVENT01.TXT", b"change DEBUG.TXT"))
