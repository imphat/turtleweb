"""SPEC secção 7, item 2: o canvas falso recebe os mesmos itens (formas, cores) que o Tk de verdade."""
import json
import os
import shutil
import subprocess
import sys

import pytest

from helpers import CHILD_PYTHON, CORPUS, ROOT, deterministic, headless_env

pytestmark = pytest.mark.tk
TOL = 0.5  # pixels (a lista do Tk é arredondada em 1 casa)
DUMP = str(ROOT / "tests" / "geometria_dump.py")


def _tk_python():
    try:
        subprocess.run([sys.executable, "-c", "import tkinter"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        return None
    return sys.executable


@pytest.fixture(scope="module", autouse=True)
def _need_tk():
    if not shutil.which("xvfb-run") or not _tk_python():
        pytest.skip("sem xvfb-run ou sem Tkinter: geometria não comparada")


def _dump(mode, programa, tmp_path):
    path = programa if os.path.isabs(programa) else str(CORPUS / programa)
    out = tmp_path / ("%s.json" % mode)
    if mode == "real":
        cmd = ["xvfb-run", "-a", sys.executable, DUMP, mode, path, str(out)]
        env = dict(os.environ)
    else:
        cmd = [CHILD_PYTHON, DUMP, mode, path, str(out)]
        env = headless_env()
    proc = subprocess.run(cmd, cwd=tmp_path, env=env, capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr
    return json.loads(out.read_text())


def _same(a, b):
    assert a["kind"] == b["kind"]
    assert len(a["coords"]) == len(b["coords"])
    assert all(abs(x - y) <= TOL for x, y in zip(a["coords"], b["coords"])), (a, b)
    for key in ("fill", "outline", "text", "anchor"):
        assert a.get(key) == b.get(key), (key, a, b)
    assert abs(a.get("width", 0) - b.get("width", 0)) < 0.01, (a, b)


EXTRAS = sorted(str(p) for p in (ROOT / "tests" / "programs").glob("geo_*.py"))


@pytest.mark.parametrize("programa", deterministic() + EXTRAS)
def test_mesmos_itens_que_o_tk(programa, tmp_path):
    real, fake = _dump("real", programa, tmp_path), _dump("fake", programa, tmp_path)
    assert real["bg"] == fake["bg"]
    assert len(real["items"]) == len(fake["items"])
    for a, b in zip(real["items"], fake["items"]):
        _same(a, b)
