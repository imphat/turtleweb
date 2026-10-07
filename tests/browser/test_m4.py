"""M4: interação (teclado, mouse, arrastar, timer, toque, botões de seta)."""
import time

from browser.conftest import near

RED, BLUE, BLACK, WHITE = (255, 0, 0), (0, 0, 255), (0, 0, 0), (255, 255, 255)


def test_clique_de_tela_com_coordenadas_do_turtle(run):
    r = run("eco_clique")
    r.wait_state("waiting")
    r.click_at(60, -40)
    r.wait_out("clique 60 -40")
    r.click_at(-100, 80, button="right")
    r.wait_out("direito -100 80")


def test_onclick_na_tartaruga_so_quando_acerta(run):
    r = run("clique_tartaruga")
    r.wait_state("waiting")
    r.click_at(100, 100)
    r.wait_out("tela 100 100")
    assert "tartaruga" not in r.out()
    r.click_at(0, 0)
    r.wait_out("tartaruga 0 0")
    r.wait_pixel(0, 0, RED)                       # cor da tartaruga mudou


def test_teclas_com_nomes_do_tk(run):
    r = run("teclas")
    r.wait_state("waiting")
    r.page.wait_for_selector(".tw canvas")
    for key, name in [("a", "a"), ("Space", "space"), ("ArrowUp", "Up"), ("Enter", "Return"), ("A", "A")]:
        r.page.keyboard.press(key)
        r.wait_out("tecla %s\n" % name)
    r.page.keyboard.press("Shift+Equal")          # "+"
    r.wait_out("tecla plus")
    r.page.keyboard.down("b")
    r.page.keyboard.up("b")
    r.wait_out("press-b")


def test_teclas_so_depois_de_listen(run):
    r = run("sem_listen")
    r.wait_state("waiting")
    r.page.keyboard.press("a")
    r.wait_out("timer")
    time.sleep(0.3)
    assert "nao devia" not in r.out()


def test_setas_do_corpus(run):
    r = run("referencia-controle-setas")
    r.wait_state("waiting")
    r.page.keyboard.press("ArrowUp")
    r.wait_ink(0, 10)                   # subiu 20 desenhando
    r.page.keyboard.press("ArrowDown")
    r.page.keyboard.press("ArrowDown")
    r.wait_ink(0, -10)


def test_tecla_durante_laco_com_update(run):
    r = run("loop_jogo")
    r.wait_state("running", "waiting")
    for _ in range(4):
        r.page.keyboard.press("ArrowUp")
        time.sleep(0.1)
    r.wait_out("fim")
    r.wait_state("ended")


def test_tecla_durante_animacao_do_turtle(run):
    r = run("ideia-exame_pong")
    r.wait_state("ended")                         # o laço roda sozinho e termina


def test_arrastar_desenha(run):
    r = run("ideia-pincel_mouse")
    r.wait_state("waiting")
    r.drag([(0, 0), (50, 20), (100, 50)])   # ondrag só vale se o clique começa na tartaruga
    # ondrag moves the turtle with the pen down: the path (0,0)-(50,20)-(100,50) is drawn
    r.wait_ink(90, 45)                       # (the intermediate vertex may be coalesced away)


def test_ontimer_relogio(run):
    r = run("ideia-relogio_animado")
    r.wait_state("waiting")
    assert r.has_ink()


def test_exitonclick_fecha_a_janela(run):
    r = run("sai_ao_clicar")
    r.wait_state("waiting")
    r.click_at(0, 100)
    r.wait_state("ended")


def test_pegue_a_bolinha_deterministico(run):
    r = run("pegue_det")
    r.wait_state("waiting")
    r.click_at(60, 60)
    r.wait_out("pontos 1")
    r.click_at(-60, -60)                          # ainda não chegou lá
    time.sleep(0.2)
    assert "pontos 2" not in r.out()
    r.page.wait_for_function("document.getElementById('out').textContent.includes('pontos 1')")
    deadline = time.time() + 6
    while "pontos 2" not in r.out() and time.time() < deadline:
        r.click_at(-60, -60)
        time.sleep(0.3)
    assert "pontos 2" in r.out()


def test_pegue_a_bolinha_do_corpus(run):
    """O programa real: acha a bolinha preta no canvas e clica nela."""
    r = run("referencia-pegue-a-bolinha")
    r.wait_state("waiting")
    found = r.page.evaluate("""() => { const c = document.querySelector('.tw canvas');
        const s = c.width / parseFloat(c.style.width), d = c.getContext('2d').getImageData(0,0,c.width,c.height);
        let sx = 0, sy = 0, n = 0;
        for (let y = 0; y < d.height; y++) for (let x = 0; x < d.width; x++) {
          const i = (y * d.width + x) * 4;
          if (d.data[i] < 40 && d.data[i+1] < 40 && d.data[i+2] < 40) { sx += x; sy += y; n++; } }
        return n ? [sx / n / s - c.width / s / 2, c.height / s / 2 - sy / n / s, n] : null; }""")
    assert found and found[2] > 20
    r.click_at(found[0], found[1])
    r.wait_out("1")


def test_toque_e_botoes_de_seta(browser, server):
    from browser.conftest import Run
    r = Run(browser, server, "referencia-controle-setas", has_touch=True, is_mobile=True, viewport={"width": 800, "height": 900})
    try:
        r.wait_state("waiting")
        r.page.wait_for_selector(".tw-pad:not([hidden])")      # só aparece depois de listen() e em tela de toque
        r.page.tap('.tw-pad button[data-key="Up"]')
        r.wait_ink(0, 10)
    finally:
        r.close()


def test_toque_na_tela_e_clique(browser, server):
    from browser.conftest import Run
    r = Run(browser, server, "eco_clique", has_touch=True, viewport={"width": 800, "height": 900})
    try:
        r.wait_state("waiting")
        x, y = r.at(30, 40)
        r.page.touchscreen.tap(x, y)
        r.wait_out("clique 30 40")
        assert r.page.is_hidden(".tw-pad")                      # sem listen(): sem botões de seta
    finally:
        r.close()


def test_botoes_de_seta_escondidos_no_computador(run):
    r = run("referencia-controle-setas")
    r.wait_state("waiting")
    time.sleep(0.2)
    assert r.page.is_hidden(".tw-pad")
