import os
import subprocess
import sys

import pytest

pytestmark = pytest.mark.skipif(not os.environ.get("SLOW"), reason="set SLOW=1 (rebuilds ~1 GB of disc images)")


def test_identity_build():
    r = subprocess.run([sys.executable, "-X", "utf8", "tools/identity.py"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
