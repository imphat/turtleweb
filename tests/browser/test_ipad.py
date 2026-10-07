"""Problemas vistos no iPad (iPad 7, iOS 18, Safari): botões de seta, teclado, dot, arraste, reconexão."""
import time

from browser.conftest import Run, near

BLACK, WHITE = (0, 0, 0), (255, 255, 255)
TOUCH = dict(has_touch=True, is_mobile=True, viewport={"width": 1024, "height": 768})


def touch_run(browser, server, prog, **extra):
    return Run(browser, server, prog, **{**TOUCH, **extra})


def hold(r, key, seconds):
    """Finger down on a pad button, wait, finger up (synthetic pointer events, as a touch screen sends)."""
    sel = '.tw-pad button[data-key="%s"]' % key
    r.page.dispatch_event(sel, "pointerdown", {"pointerType": "touch", "isPrimary": True, "button": 0})
    time.sleep(seconds)
    r.page.dispatch_event(sel, "pointerup", {"pointerType": "touch", "isPrimary": True, "button": 0})


def test_seta_para_baixo_do_pad_funciona(browser, server):
    r = touch_run(browser, server, "referencia-controle-setas")
    try:
        r.wait_state("waiting")
        r.page.wait_for_selector(".tw-pad:not([hidden])")
        r.page.tap('.tw-pad button[data-key="Down"]')
        r.wait_ink(0, -10)
    finally:
        r.close()


def test_segurar_o_botao_repete_a_acao_do_onkey(browser, server):
    """onkey() responde ao SOLTAR a tecla: segurar tem de gerar soltar+apertar a cada repetição (como o X11)."""
    r = touch_run(browser, server, "conta_teclas")
    try:
        r.wait_state("waiting")
        r.page.wait_for_selector(".tw-pad:not([hidden])")
        hold(r, "Up", 0.8)
        time.sleep(0.3)
        n = r.out().count("up")
        assert n >= 4, r.out()
        before = n
        time.sleep(0.5)
        assert r.out().count("up") == before          # soltou: parou de repetir
    finally:
        r.close()


def test_toque_curto_e_uma_acao_so(browser, server):
    r = touch_run(browser, server, "conta_teclas")
    try:
        r.wait_state("waiting")
        r.page.wait_for_selector(".tw-pad:not([hidden])")
        r.page.tap('.tw-pad button[data-key="Up"]')
        time.sleep(0.5)
        assert r.out().count("up") == 1
    finally:
        r.close()


def test_dot_colorido_no_clique_mesmo_sem_linha_de_comprimento_zero(run):
    """O dot() é forward(0): uma linha de comprimento zero com ponta redonda. O Safari não a desenha: o JS desenha o círculo."""
    r = run("ideia-pintar_cliques")
    r.wait_state("waiting")
    r.click_at(60, 40)
    r.page.wait_for_function("document.querySelectorAll('.tw').length")
    time.sleep(0.6)
    # the dot (diameter 10) is partly under the turtle arrow: look at its right edge, outside the arrow
    px = r.pixel(63, 40)
    assert px[0] > 200 and px[2] < 80 or px[2] > 200 and px[0] < 80, px   # red or blue


def test_linha_de_comprimento_zero_vira_circulo(run):
    r = run("fim_sozinho")
    r.wait_state("ended")
    # behave like WebKit: a stroke of a zero-length path draws nothing
    r.page.evaluate("""() => { const stroke = CanvasRenderingContext2D.prototype.stroke;
        CanvasRenderingContext2D.prototype.stroke = function () { if (this.__len === 0) return; return stroke.call(this); };
        const lineTo = CanvasRenderingContext2D.prototype.lineTo, moveTo = CanvasRenderingContext2D.prototype.moveTo;
        CanvasRenderingContext2D.prototype.moveTo = function (x, y) { this.__len = 0; this.__x = x; this.__y = y; return moveTo.call(this, x, y); };
        CanvasRenderingContext2D.prototype.lineTo = function (x, y) { this.__len += Math.hypot(x - this.__x, y - this.__y); this.__x = x; this.__y = y; return lineTo.call(this, x, y); };
    }""")
    r.page.evaluate("""() => { tw.reset(); tw.apply(['create', 1, 'line', [10, 10, 10, 10], {fill: '#ff0000', width: 20, capstyle: 'round'}]);
                              tw.apply(['create', 2, 'line', [-50, 0, -50, 0], {fill: '#0000ff', width: 20, capstyle: 'butt'}]); tw.draw(); }""")
    assert near(r.pixel(10, -10), (255, 0, 0))        # y is flipped: canvas (10,10) is turtle (10,-10)
    assert near(r.pixel(10 + 8, -10), (255, 0, 0))    # reaches the radius
    assert near(r.pixel(-50, 0), WHITE)               # butt cap: nothing, as in Tk


def test_botao_teclado_abre_o_teclado_do_ipad(browser, server):
    r = touch_run(browser, server, "teclas")
    try:
        r.wait_state("waiting")
        r.page.wait_for_selector(".tw-kbd:not([hidden])")
        r.page.tap(".tw-kbd")
        assert r.page.evaluate("document.activeElement.className") == "tw-keyfield"
        r.page.keyboard.type("a")
        r.wait_out("tecla a\n")
        r.page.keyboard.press("Enter")
        r.wait_out("tecla Return")
        r.page.tap(".tw-kbd")                              # toggles: closes the keyboard
        assert r.page.evaluate("document.activeElement.className") != "tw-keyfield"
    finally:
        r.close()


def test_botao_teclado_so_com_listen_e_toque(browser, server, run):  # noqa
    r = touch_run(browser, server, "eco_clique")       # no listen()
    try:
        r.wait_state("waiting")
        time.sleep(0.3)
        assert r.page.is_hidden(".tw-kbd")
    finally:
        r.close()
    d = run("teclas")                                   # desktop: physical keyboard
    d.wait_state("waiting")
    time.sleep(0.3)
    assert d.page.is_hidden(".tw-kbd")


def test_arraste_com_animacao_lenta_nao_aninha_manipuladores(run, server_real_speed):
    """Drags faster than the turtle can follow: the handler must never run inside itself."""
    r = run("arraste_lento", base=server_real_speed)
    r.wait_state("waiting")
    r.drag([(0, 0)] + [(i * 4, (i * 3) % 90) for i in range(1, 60)])
    r.wait_out("fim-arraste", timeout=30000)
    out = r.out()
    assert "aninhado" not in out
    r.page.click(".tw-close")
    r.wait_state("ended")


def test_pagina_volta_a_acompanhar_depois_de_dormir(browser, server):
    """Tela bloqueada no iOS: o fluxo de eventos some. Ao voltar, a página continua do último evento, sem repetir nem perder."""
    ctrl = Run(browser, server, "tic")      # the demo keeps one run at a time: finish the control run first
    ctrl.wait_state("ended")
    sleeper = Run(browser, server, "tic")
    try:
        sleeper.page.wait_for_function("tw.items.size > 1")
        sleeper.page.evaluate("tw.es.close()")                  # the stream dies silently
        time.sleep(1.5)                                          # the program goes on without the page
        assert sleeper.state() in ("running", "starting")
        sleeper.page.evaluate("""() => { Object.defineProperty(document, 'hidden', {value: false, configurable: true});
                                        document.dispatchEvent(new Event('visibilitychange')); }""")
        sleeper.wait_state("ended")
        mine = sleeper.page.evaluate("JSON.stringify([...tw.items.values()])")
        assert mine == ctrl.page.evaluate("JSON.stringify([...tw.items.values()])")
    finally:
        ctrl.close()
        sleeper.close()
