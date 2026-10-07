"""Fechar a janela cancela os timers pendentes (como o Tk) e não imprime Terminator."""
import time

from helpers import CHILD_PYTHON


def test_timer_nao_roda_depois_de_fechar(tmp_path):
    import os
    from turtleweb.session import Session
    prog = tmp_path / "p.py"
    prog.write_text("import turtle\nt = turtle.Turtle()\n"
                    "def tic():\n    t.forward(1)\n    turtle.ontimer(tic, 5)\n"
                    "tic()\nturtle.done()\n")
    s = Session()
    s.start(prog, cwd=tmp_path, python=CHILD_PYTHON, env=dict(os.environ, TURTLEWEB_NO_DELAY="1"))
    end = time.monotonic() + 20
    while s.state != "waiting":
        assert time.monotonic() < end, s.stderr
        time.sleep(0.01)
    time.sleep(0.2)
    s.send({"t": "close"})
    assert s.wait_done() == 0
    assert s.stderr == ""
