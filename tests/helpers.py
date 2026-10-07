import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"
sys.path.insert(0, str(ROOT))

import turtleweb  # noqa: E402


def _no_tk_pythons():
    """Interpreters without Tkinter (the child must not need it)."""
    found = []
    for name in ("python3.13", "python3.11", "python3.10", "python3.14"):
        path = shutil.which(name)
        if path and subprocess.run([path, "-c", "import tkinter"], capture_output=True).returncode != 0:
            found.append(path)
    return found


def _min_python():
    """Python 3.10 (the oldest supported), if `uv python install 3.10` was run. May have Tkinter: the fake replaces it."""
    uv = Path.home() / ".local/share/uv/python"
    return [str(p) for p in uv.glob("cpython-3.10*/bin/python3.10")] if uv.exists() else []


NO_TK = _no_tk_pythons()
ALL_PY = NO_TK + _min_python()
CHILD_PYTHON = NO_TK[0] if NO_TK else sys.executable


def headless_env(extra=None):
    env = dict(os.environ, PYTHONUTF8="1", TURTLEWEB="1", TURTLEWEB_NO_DELAY="1",
               PYTHONPATH=os.pathsep.join([turtleweb.boot_dir(), str(ROOT)]))
    env.pop("TURTLEWEB_PORT", None)
    env.update(extra or {})
    return env


def run_headless(program, python=None, timeout=60, extra_env=None, stdin=subprocess.DEVNULL):
    """Run a corpus program without a browser; returns (command list, CompletedProcess)."""
    with tempfile.TemporaryDirectory() as tmp:
        log = Path(tmp) / "log.jsonl"
        env = headless_env({"PP_TURTLE_LOG": str(log), **(extra_env or {})})
        src = Path(program) if Path(program).is_absolute() else CORPUS / program
        proc = subprocess.run([python or CHILD_PYTHON, "-u", str(src)], cwd=tmp, env=env,
                              capture_output=True, text=True, timeout=timeout, stdin=stdin)
        lines = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
    return lines, proc


def deterministic():
    index = json.loads((CORPUS / "index.json").read_text(encoding="utf-8"))
    return [e["programa"] for e in index if e["tipo"] == "deterministico"]
