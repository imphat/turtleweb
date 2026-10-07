"""M6: `pip install .` num ambiente limpo e uso pelo app, sem o repositório no caminho."""
import json
import subprocess
import sys

import pytest

from helpers import CHILD_PYTHON, CORPUS, ROOT

E2E = """
import json, subprocess, sys, time
import turtleweb
from turtleweb import Session
from turtleweb.session import child_env
assert "site-packages" in turtleweb.__file__, turtleweb.__file__
s = Session()
proc = subprocess.Popen([sys.argv[1], "-u", sys.argv[2]], cwd=sys.argv[3],
                        env=child_env(s, None, log=sys.argv[4]))
s.attach(proc)
end = time.monotonic() + 30
while s.state != "waiting":
    assert time.monotonic() < end, s.state
    time.sleep(0.05)
s.send({"t": "close"})
assert s.wait_done() == 0 and s.state == "ended"
"""


def test_pip_install_e_integracao(tmp_path):
    venv = tmp_path / "v"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True, capture_output=True)
    py = venv / "bin" / "python"
    done = subprocess.run([str(py), "-m", "pip", "-q", "install", str(ROOT)], capture_output=True, text=True)
    if done.returncode != 0:
        pytest.skip("pip install indisponível (sem rede?): " + done.stderr[-200:])
    log = tmp_path / "log.jsonl"
    # the child uses another interpreter than the app (the app's copy is found through TURTLEWEB_PATH)
    run = subprocess.run([str(py), "-I", "-c", E2E, CHILD_PYTHON, str(CORPUS / "referencia-quadrado.py"),
                          str(tmp_path), str(log)], capture_output=True, text=True, timeout=90, cwd=tmp_path)
    assert run.returncode == 0, run.stderr
    esperado = json.loads((CORPUS / "referencia-quadrado.esperado.json").read_text())
    assert [json.loads(x) for x in log.read_text().splitlines()] == esperado
