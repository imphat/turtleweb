"""SPEC secção 7, item 3: fumaça no navegador com os determinísticos do corpus."""
import pytest

from helpers import deterministic

# Pontos principais (coordenadas do turtle) e a cor esperada, programas conhecidos.
BOLINHAS = [(-80, 0, (255, 0, 0)), (0, 0, None), (80, 0, (0, 0, 255))]


@pytest.mark.parametrize("programa", deterministic())
def test_abre_recebe_eventos_e_desenha(run, programa):
    r = run(programa[:-3])
    r.wait_state("waiting", "ended", timeout=60000)
    assert not r.errors
    assert r.has_ink(), "o canvas ficou vazio"
    session_info = r.page.evaluate("fetch('/turtleweb/status/' + tw.sid).then(r => r.json())")
    assert session_info["state"] in ("waiting", "running", "ended")


def test_bolinhas_coloridas(run):
    r = run("referencia-bolinhas")
    r.wait_state("waiting", "ended")
    for x, y, want in BOLINHAS:
        if want:
            assert max(abs(a - b) for a, b in zip(r.pixel(x, y), want)) < 40, (x, y, r.pixel(x, y))
