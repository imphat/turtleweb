"""Canal por socket: Session + processo filho real, sem navegador."""
import json
import time

import pytest

from helpers import ALL_PY, CHILD_PYTHON, CORPUS


def _wait_state(session, state, timeout=20):
    end = time.monotonic() + timeout
    while session.state != state:
        assert time.monotonic() < end, "estado %s (esperava %s): %s" % (session.state, state, session.stderr)
        time.sleep(0.02)


@pytest.mark.parametrize("python", ALL_PY or [CHILD_PYTHON])
def test_quadrado_pelo_canal_e_lista_de_comandos(tmp_path, python):
    from turtleweb.session import Session
    s = Session()
    log = tmp_path / "log.jsonl"
    s.start(CORPUS / "referencia-quadrado.py", cwd=tmp_path, python=python, log=log)
    _wait_state(s, "waiting")                      # turtle.done()
    ops = [json.loads(t) for t in s.events if '"t":"ops"' in t]
    flat = [op for m in ops for op in m["ops"]]
    assert any(op[0] == "create" and op[2] == "line" for op in flat)
    assert any(op[0] == "config" and op[2].get("fill") == "#000000" for op in flat)  # pen drawn in black
    assert sum(op[0] == "coords" for op in flat) >= 4                                  # the sides moved
    assert s.send({"t": "close"})
    assert s.wait_done() == 0
    assert s.state == "ended"
    esperado = json.loads((CORPUS / "referencia-quadrado.esperado.json").read_text())
    assert [json.loads(x) for x in log.read_text().splitlines()] == esperado


def test_input_do_programa_continua_livre(tmp_path):
    """O canal não usa stdin/stdout: input() e print() funcionam como sempre."""
    import subprocess
    from turtleweb.session import Session, child_env
    prog = tmp_path / "p.py"
    prog.write_text("import turtle\nnome = input()\nprint('oi', nome)\nturtle.Turtle().forward(10)\n")
    s = Session()
    proc = subprocess.Popen([CHILD_PYTHON, "-u", str(prog)], env=child_env(s), cwd=tmp_path,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    s.attach(proc)
    out, _ = proc.communicate("Ana\n", timeout=20)
    assert out.strip() == "oi Ana"
    assert s.wait_done() == 0


def test_mensagem_desconhecida_da_pagina_e_descartada(tmp_path):
    from turtleweb.session import Session
    s = Session()
    assert s.send({"t": "rm -rf"}) is False
    assert s.send("x") is False


def test_filho_roda_sem_tkinter(no_tk_python):
    import subprocess
    out = subprocess.run([no_tk_python, "-c", "import tkinter"], capture_output=True)
    assert out.returncode != 0      # confirma que este Python realmente não tem Tk


def _run_to_end(program, tmp_path, python=None):
    from turtleweb.session import Session
    import os
    s = Session()
    s.start(program, cwd=tmp_path, python=python or CHILD_PYTHON, env=dict(os.environ, TURTLEWEB_NO_DELAY="1"))
    end = time.monotonic() + 60
    while s.state not in ("waiting", "ended", "error", "stopped"):
        assert time.monotonic() < end
        time.sleep(0.02)
    if s.state == "waiting":
        s.send({"t": "close"})
    s.wait_done()
    return s


from helpers import ROOT, deterministic  # noqa: E402

_PROGS = [str(CORPUS / p) for p in deterministic()] + sorted(str(p) for p in (ROOT / "tests/programs").glob("geo_*.py"))


@pytest.mark.parametrize("programa", _PROGS)
def test_nenhum_metodo_do_tk_ficou_sem_implementar(programa, tmp_path):
    s = _run_to_end(programa, tmp_path)
    assert s.state == "ended", s.stderr
    assert s.child_end is not None and s.child_end["unknown"] == []
