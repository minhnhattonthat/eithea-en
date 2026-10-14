"""One-command check used by the pre-commit hook: runs pytest when tests exist."""
import pathlib
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parent.parent
if not any((root / "tests").glob("test_*.py")):
    print("check: no tests yet")
    sys.exit(0)
sys.exit(subprocess.call([sys.executable, "-X", "utf8", "-m", "pytest", "-q", "-p", "no:faulthandler", str(root / "tests")]))
