"""SPEC secção 7, item 4: os programas interativos rodam, sem erro, com eventos simulados."""
import json
import os
import time

import pytest

from helpers import CHILD_PYTHON, CORPUS

CLICK = lambda x, y, b=1: [  # noqa: E731  (turtle coordinates -> window pixels: origin at the center of 640x600)
    {"t": "mousedown", "x": 320 + x, "y": 300 - y, "b": b}, {"t": "mouseup", "x": 320 + x, "y": 300 - y, "b": b}]
KEY = lambda k: [{"t": "keydown", "k": k, "c": ""}, {"t": "keyup", "k": k, "c": ""}]  # noqa: E731

# programa -> (stdin, eventos, texto esperado no stdout)
CASES = {
    "ideia-arco_iris.py": ("", [], ""),
    "ideia-bolinha.py": ("", [], ""),
    "ideia-trilha_pontos.py": ("", [], ""),
    "ideia-chuva_confete.py": ("", [], ""),
    "ideia-controle_remoto.py": ("", KEY("Up") * 3, ""),
    "ideia-desenha_teclado.py": ("", KEY("Up") * 3, ""),
    "ideia-corrida_tartarugas.py": ("", KEY("space") * 3, ""),
    "ideia-desenha_comandos.py": ("frente\nfrente\nsair\n", [], ""),
    "ideia-desenho_arquivo.py": ("", [], ""),
    "ideia-exame_cobra.py": ("", [], ""),
    "ideia-exame_desenhista.py": ("", CLICK(10, 10), ""),
    "ideia-exame_pong.py": ("", [], ""),
    "ideia-exame_simon.py": ("", CLICK(20, 30), ""),   # sem done(): termina antes do clique (como no Tk)
    "ideia-nome_estrelas.py": ("Ana\n", [], ""),
    "ideia-paleta_cores.py": ("azul\n", [], ""),
    "ideia-pincel_mouse.py": ("", [{"t": "mousedown", "x": 320, "y": 300, "b": 1},
                                  {"t": "mousemove", "x": 380, "y": 280, "b": 1},
                                  {"t": "mouseup", "x": 380, "y": 280, "b": 1}], ""),
    "ideia-pintar_cliques.py": ("", CLICK(-40, 40) + CLICK(40, -40), ""),
    "ideia-poligono_medida.py": ("", [{"t": "ANSWER", "v": "6"}], ""),
    "ideia-relogio_animado.py": ("", [], ""),
    "referencia-controle-setas.py": ("", KEY("Up") + KEY("Down"), ""),
    "referencia-pegue-a-bolinha.py": ("", CLICK(0, 0), ""),
}


def _wait(s, states, timeout=30):
    end = time.monotonic() + timeout
    while s.state not in states:
        assert time.monotonic() < end, "estado %s: %s" % (s.state, s.stderr)
        time.sleep(0.02)


def test_todos_os_interativos_tem_caso():
    index = json.loads((CORPUS / "index.json").read_text(encoding="utf-8"))
    names = {e["programa"] for e in index if e["tipo"] != "deterministico"}
    assert names == set(CASES)


@pytest.mark.parametrize("programa", sorted(CASES))
def test_roda_com_eventos_simulados(programa, tmp_path):
    from turtleweb.session import Session
    stdin, events, expect = CASES[programa]
    (tmp_path / "desenho.txt").write_text("frente 50\nfrente 30\n")
    s = Session()
    s.start(CORPUS / programa, cwd=tmp_path, python=CHILD_PYTHON, env=dict(os.environ, TURTLEWEB_NO_DELAY="1"),
            stdin_text=stdin)
    _wait(s, ("running", "waiting", "ended", "error"))
    time.sleep(0.4)                                   # let the program register its handlers
    for ev in events:
        if ev["t"] == "ANSWER":
            _wait_ask(s)
            ev = {"t": "answer", "id": _last_ask(s)["id"], "v": ev["v"]}
        s.send(ev)
        time.sleep(0.05)
    if s.state not in ("ended", "error"):
        time.sleep(0.6)
        if s.state == "waiting":
            s.send({"t": "close"})
        elif s.state == "running":
            s.stop()                                   # endless programs (timers, loops): ■ Parar
    s.wait_done(30)
    assert s.state in ("ended", "stopped"), (s.state, s.stderr)
    assert s.stderr == "", s.stderr
    out = "".join(json.loads(e)["text"] for e in s.events if '"t":"out"' in e and json.loads(e)["s"] == "stdout")
    assert expect in out
    assert s.child_end is None or s.child_end["unknown"] == []


def _last_ask(s):
    asks = [json.loads(e) for e in s.events if '"t":"ask"' in e]
    return asks[-1]


def _wait_ask(s, timeout=10):
    end = time.monotonic() + timeout
    while not any('"t":"ask"' in e for e in s.events):
        assert time.monotonic() < end
        time.sleep(0.02)
