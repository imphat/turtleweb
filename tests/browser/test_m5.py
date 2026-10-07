"""M5: desempenho, velocidade, retina, reduzir movimento, muitos carimbos, erros."""
import time

import pytest

from browser.conftest import near

RED, WHITE = (255, 0, 0), (255, 255, 255)


def test_espiral_tao_rapida_quanto_o_tk(run, server_real_speed):
    t0 = time.time()
    r = run("referencia-espiral", base=server_real_speed)
    r.wait_state("waiting", timeout=60000)
    assert 8 < time.time() - t0 < 20            # Tk de verdade: ~13,6 s; o turtleweb: ~13 s
    assert r.has_ink()


def test_botao_mais_rapido_acelera_sem_mudar_o_desenho(run, server_real_speed):
    r = run("referencia-espiral", base=server_real_speed)
    r.page.wait_for_selector(".tw-fast")
    r.page.click(".tw-fast")
    t0 = time.time()
    r.wait_state("waiting", timeout=60000)
    assert time.time() - t0 < 6
    assert r.page.inner_text(".tw-fast") == "Velocidade normal"
    fast = r.page.evaluate("JSON.stringify([...tw.items.values()])")
    # same program at normal speed draws exactly the same items
    r2 = run("referencia-espiral", base=server_real_speed)
    r2.wait_state("waiting", timeout=60000)
    assert r2.page.evaluate("JSON.stringify([...tw.items.values()])") == fast


def test_reduzir_movimento_comeca_rapido(browser, server_real_speed):
    from browser.conftest import Run
    r = Run(browser, server_real_speed, "referencia-espiral", reduced_motion="reduce")
    try:
        t0 = time.time()
        r.wait_state("waiting", timeout=60000)
        assert time.time() - t0 < 5
        assert r.has_ink()
    finally:
        r.close()


def test_retina_canvas_com_o_dobro_de_pixels(browser, server):
    from browser.conftest import Run
    r = Run(browser, server, "quadrado_circulo", device_scale_factor=2)
    try:
        r.wait_state("waiting")
        dims = r.page.evaluate("(() => { const c = document.querySelector('.tw canvas'); return [c.width, c.height, c.style.width]; })()")
        assert dims == [1280, 1200, "640px"]
        assert near(r.pixel(50, 0), RED)
        assert near(r.pixel(-120, -50), (173, 216, 230))
    finally:
        r.close()


def test_muitos_carimbos_nao_trava_a_pagina(run):
    t0 = time.time()
    r = run("muitos_carimbos")
    r.wait_state("waiting", timeout=30000)
    assert time.time() - t0 < 10
    assert r.page.evaluate("tw.items.size") >= 3000
    ms = r.page.evaluate("(() => { const t = performance.now(); for (let i = 0; i < 5; i++) tw.draw(); return (performance.now() - t) / 5; })()")
    assert ms < 50                                  # um quadro com 3000 carimbos
    assert r.has_ink()


def test_muitas_linhas(run):
    t0 = time.time()
    r = run("muitas_linhas")
    r.wait_state("waiting", timeout=30000)
    assert time.time() - t0 < 10
    assert r.page.evaluate("tw.items.size") >= 4000


def test_erro_de_sintaxe_vai_para_o_stderr(run):
    r = run("sintaxe")
    r.wait_state("error")
    assert "SyntaxError" in r.out()


def test_sessao_inexistente_mostra_sem_conexao(run):
    r = run("fim_sozinho")
    r.wait_state("ended")
    r.page.evaluate("tw.attach('nao-existe')")
    r.page.wait_for_function("document.querySelector('.tw-state').textContent.includes('sem conexão')", timeout=10000)


def test_operacao_desconhecida_e_ignorada(run):
    r = run("fim_sozinho")
    r.wait_state("ended")
    r.page.evaluate("tw.onMessage({t: 'ops', ops: [['nada-disso', 1, 2], ['coords', 999, [1, 2]]]})")
    assert not r.errors


# O corpus inteiro no navegador (os que esperam stdin ou arquivo terminam com erro de leitura, como no app sem entrada).
PRECISAM_DE_ENTRADA = {"ideia-desenha_comandos", "ideia-desenho_arquivo", "ideia-nome_estrelas", "ideia-paleta_cores"}


def _interativos():
    import json
    from helpers import CORPUS
    idx = json.loads((CORPUS / "index.json").read_text(encoding="utf-8"))
    return [e["programa"][:-3] for e in idx if e["tipo"] != "deterministico"]


@pytest.mark.parametrize("programa", _interativos())
def test_corpus_interativo_no_navegador(run, programa):
    r = run(programa)
    r.wait_state("running", "waiting", "ended", "error", timeout=30000)
    time.sleep(0.6)
    assert not r.errors
    state = r.state()
    if programa in PRECISAM_DE_ENTRADA:
        assert state == "error"
    else:
        assert state in ("running", "waiting", "ended"), r.out()
    if state in ("running", "waiting"):
        r.page.click("#stop")
        r.wait_state("stopped")
