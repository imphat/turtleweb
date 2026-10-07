"""M3: ciclo de vida (SPEC seção 6) e textinput/numinput."""
import time

from browser.conftest import near

RED, BLUE, WHITE = (255, 0, 0), (0, 0, 255), (255, 255, 255)


def out_text(r):
    return r.page.inner_text("#out")


def test_termina_sozinho_o_desenho_fica(run):
    r = run("fim_sozinho")
    r.wait_state("ended")
    assert r.page.inner_text(".tw-state") == "terminou"
    assert near(r.pixel(50, 0), RED)
    assert r.page.is_disabled(".tw-close")


def test_done_espera_e_fechar_termina_com_zero(run):
    r = run("outro")
    r.wait_state("waiting")
    assert r.page.inner_text(".tw-state") == "esperando você fechar a janela"
    time.sleep(0.5)
    assert r.state() == "waiting"                    # ainda esperando
    r.page.click(".tw-close")
    r.wait_state("ended")
    assert near(r.pixel(0, 50), BLUE)               # o desenho continua
    status = r.page.evaluate("fetch('/turtleweb/status/' + tw.sid).then(r => r.json())")
    assert status["code"] == 0


def test_parar_mantem_o_desenho(run):
    r = run("longo")
    r.wait_state("running")
    time.sleep(0.5)
    r.page.click("#stop")
    r.wait_state("stopped")
    assert r.page.inner_text(".tw-state") == "parado"
    assert near(r.pixel(50, 0), RED)


def test_fechar_no_meio_do_desenho_termina_sem_erro(run):
    r = run("longo")
    r.wait_state("running")
    time.sleep(0.5)
    r.page.click(".tw-close")
    r.wait_state("ended", "error")
    assert r.state() == "ended"
    assert "Terminator" not in out_text(r)


def test_erro_traceback_no_stderr_e_desenho_fica(run):
    r = run("erro_depois")
    r.wait_state("error")
    assert "ZeroDivisionError" in out_text(r)
    assert near(r.pixel(50, 0), RED)
    assert "código 1" in r.page.inner_text(".tw-state")


def test_nova_execucao_limpa_a_pagina(run):
    r = run("fim_sozinho")
    r.wait_state("ended")
    assert near(r.pixel(50, 0), RED)
    r.page.select_option("#prog", "outro")
    r.page.click("#run")
    r.wait_state("waiting")
    assert near(r.pixel(0, 50), BLUE)
    assert near(r.pixel(50, 0), WHITE)              # o desenho da execução anterior sumiu


def _answer(r, text):
    r.page.wait_for_selector(".tw-ask:not([hidden])")
    r.page.fill(".tw-ask input", text)
    r.page.click(".tw-ask button[type=submit]")


def test_textinput_e_numinput(run):
    r = run("pergunta")
    r.page.wait_for_selector(".tw-ask:not([hidden])")
    assert "Como você se chama?" in r.page.inner_text(".tw-ask")
    _answer(r, "Ana")
    # numinput: texto inválido e fora da faixa pedem de novo, com a mensagem
    _answer(r, "abc")
    r.page.wait_for_selector(".tw-err")
    assert "número" in r.page.inner_text(".tw-err")
    _answer(r, "500")
    r.page.wait_for_selector(".tw-err")
    assert "no máximo 120" in r.page.inner_text(".tw-err")
    _answer(r, "12,5")
    r.wait_state("waiting")
    assert "'Ana' 12.5" in out_text(r)


def test_cancelar_devolve_none(run):
    r = run("pergunta")
    r.page.wait_for_selector(".tw-ask:not([hidden])")
    r.page.click(".tw-ask button[type=button]")
    r.page.wait_for_selector(".tw-ask:not([hidden])")
    assert "Quantos anos?" in r.page.inner_text(".tw-ask")
    r.page.click(".tw-ask button[type=button]")
    r.wait_state("waiting")
    assert "None None" in out_text(r)
