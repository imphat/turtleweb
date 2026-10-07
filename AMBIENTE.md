# Verificação do ambiente

Data: 2026-10-07. Container Linux (Ubuntu noble), sessão na nuvem.

| # | Item | Resultado |
|---|------|-----------|
| 1 | Versões | `python3` = **3.13.16**; pip **24.0** (`/usr/lib/python3/dist-packages/pip`). Também existem `python3.11`, `python3.12`, `python3.13`. |
| 2a | `import tkinter` | **Falhou** com o `python3` padrão (3.13): `ModuleNotFoundError: No module named 'tkinter'`. **Funcionou** com `/usr/bin/python3.12` (pacote `python3-tk 3.12.3` instalado). |
| 2b | `turtle` sob `xvfb-run` | **Falhou** com `python3` (3.13): `ModuleNotFoundError: No module named 'tkinter'` (em `turtle.py`, linha 38). **Funcionou** com `xvfb-run -a /usr/bin/python3.12`: `Turtle().forward(10)` → posição `(10.00,0.00)`. `xvfb-run` e `Xvfb` existem. |
| 3 | Chromium sem janela + canvas | **Funcionou.** Playwright (Node 1.56.1, `/opt/node-tools`) e Playwright Python (instalado em venv, usando `executable_path='/opt/pw-browsers/chromium'`) carregaram `data:text/html,<canvas id=c></canvas>`, desenharam retângulo vermelho e leram o pixel: `[255,0,0,255]`. |
| 4a | `pip download` | **Funcionou** (`six-1.17.0`). `pip install playwright` em venv também funcionou. |
| 4b | `apt-get` | **Funcionou**: `apt-get update` ok, `apt-get download cowsay` ok (só um aviso de permissão do `_apt` no diretório de destino). |
| 4c | Download do navegador do Playwright | **Falhou**: `playwright install chromium-headless-shell` → `403 request blocked: no rule or allowlist entry allows host "cdn.playwright.dev"`. `playwright.download.prss.microsoft.com` também não responde (curl 000). Contorno: usar o Chromium já instalado em `/opt/pw-browsers` (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`, `chromium-1194`). |
| 5 | Servidor em `127.0.0.1` + navegador | **Funcionou.** Servidor HTTP Node em `127.0.0.1:8765` acessado pelo Chromium: título `ok127`. |

## Observações
- O `python3` padrão (3.13) não tem Tk; para testes com Tk de verdade é preciso usar `python3.12`. A biblioteca pode ser testada em 3.13 sem Tk se o módulo substituto não depender dele.
- O Playwright Python do pip espera a revisão 1243 do navegador (indisponível); com `executable_path` apontando para o Chromium existente funciona.
