"""Teste de fogo do M0: o turtle da biblioteca padrão, com um tkinter falso,
desenha no Chromium sem janela. Rodar: ~/.venvs/turtleweb/bin/python test_fogo.py
"""
import os
import socket
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))


def chromium_path():
    p = os.path.expanduser("~/.chromium-path")
    if os.path.exists(p):
        return open(p).read().strip()
    return subprocess.check_output(
        "find /opt/pw-browsers -name chrome -o -name headless_shell | head -1",
        shell=True, text=True).strip()


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def pixel(page, x, y):
    """Color at turtle coordinates (x, y)."""
    return page.evaluate(
        """([x, y]) => { const c = document.getElementById('cv');
        const d = c.getContext('2d').getImageData(c.width/2 + x, c.height/2 - y, 1, 1).data;
        return [d[0], d[1], d[2]]; }""", [x, y])


def close(a, b, tol=40):
    return all(abs(p - q) <= tol for p, q in zip(a, b))


def check(results, name, got, want):
    ok = close(got, want)
    results.append((name, ok, got, want))
    print(("PASSOU " if ok else "FALHOU ") + name, got, "esperado", want)


def main():
    child = os.environ.get("TW_CHILD_PYTHON", "python3.13")
    port = free_port()
    server = subprocess.Popen([sys.executable, os.path.join(HERE, "server.py"), str(port)],
                              env=dict(os.environ, TW_CHILD_PYTHON=child),
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    results = []
    try:
        for _ in range(50):
            try:
                socket.create_connection(("127.0.0.1", port), 0.2).close()
                break
            except OSError:
                time.sleep(0.1)
        base = "http://127.0.0.1:%d/" % port
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=chromium_path())
            page = browser.new_page(viewport={"width": 800, "height": 760})

            # 1. quadrado e círculo
            t0 = time.monotonic()
            page.goto(base + "?prog=quadrado_circulo")
            page.wait_for_function(
                "document.getElementById('status').textContent.startsWith('esperando')",
                timeout=30000)
            page.wait_for_timeout(200)
            print("quadrado_circulo: desenho completo em %.1fs" % (time.monotonic() - t0))
            red, white = (255, 0, 0), (255, 255, 255)
            check(results, "lado de baixo do quadrado é vermelho", pixel(page, 50, 0), red)
            check(results, "lado direito do quadrado é vermelho", pixel(page, 100, 50), red)
            check(results, "lado de cima do quadrado é vermelho", pixel(page, 50, 100), red)
            check(results, "dentro do quadrado é branco", pixel(page, 50, 50), white)
            check(results, "centro do círculo é azul-claro", pixel(page, -120, -50), (173, 216, 230))
            check(results, "topo do círculo é azul", pixel(page, -120, 0), (0, 0, 255))
            check(results, "base do círculo é azul", pixel(page, -120, -100), (0, 0, 255))
            check(results, "fora de tudo é branco", pixel(page, 200, -200), white)
            page.locator("#cv").screenshot(path=os.path.join(HERE, "quadrado_circulo.png"))
            page.click("#close")
            page.wait_for_function(
                "document.getElementById('status').textContent.startsWith('terminou')", timeout=10000)
            st = page.text_content("#status")
            results.append(("fechar a janela termina com código 0", st == "terminou (código 0)", st, ""))
            print(results[-1][1] and "PASSOU" or "FALHOU", "fechar:", st)

            # 2. textinput, ontimer, onscreenclick (bônus)
            page.goto(base + "?prog=interacao")
            page.wait_for_selector("#ask", state="visible", timeout=15000)
            page.fill("#askvalue", "Ana")
            page.click("#askok")
            page.wait_for_function(
                "document.getElementById('status').textContent.startsWith('esperando')",
                timeout=15000)
            page.wait_for_timeout(1200)
            check(results, "fundo lightyellow", pixel(page, 250, 250), (255, 255, 224))
            check(results, "ontimer pintou bolinha verde", pixel(page, -100, 100), (0, 255, 0))
            box = page.locator("#cv").bounding_box()
            page.mouse.click(box["x"] + box["width"] / 2 + 160, box["y"] + box["height"] / 2 - 120)
            page.wait_for_timeout(2500)
            check(results, "clique fez a tartaruga andar (meio da linha preto)",
                  pixel(page, 80, 60), (0, 0, 0))
            dark = page.evaluate("""() => { const c = document.getElementById('cv');
              const d = c.getContext('2d').getImageData(c.width/2 - 150, c.height/2 + 130, 120, 25).data;
              let n = 0; for (let i = 0; i < d.length; i += 4) if (d[i] < 100) n++; return n; }""")
            results.append(("write('Olá, Ana') aparece (pixels escuros)", dark > 50, dark, ">50"))
            print(results[-1][1] and "PASSOU" or "FALHOU", "texto: pixels escuros =", dark)
            page.locator("#cv").screenshot(path=os.path.join(HERE, "interacao.png"))
            page.click("#close")
            page.wait_for_function(
                "document.getElementById('status').textContent.startsWith('terminou')", timeout=10000)
            browser.close()
    finally:
        server.terminate()
    failed = [r for r in results if not r[1]]
    print("\n%d verificações, %d falharam (filho: %s)" % (len(results), len(failed), child))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
