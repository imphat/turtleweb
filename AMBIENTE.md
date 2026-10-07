# AMBIENTE (registrado no M0, 2026-10-07)

## O que funcionou
- `~/.venvs/turtleweb/bin/python` (3.12, com Tkinter, pytest, flask, playwright).
- Pythons **sem Tkinter** para testar o canvas falso: `/usr/bin/python3.11`, `/usr/bin/python3.13`.
- **Python 3.10 e 3.14 instalados com `uv python install 3.10` e `uv python install 3.14`** (o `uv` já existe em
  `~/.local/bin/uv`). Caminhos: `~/.local/share/uv/python/cpython-3.10-linux-x86_64-gnu/bin/python3.10` e
  `.../cpython-3.14-linux-x86_64-gnu/bin/python3.14`. O 3.14 do uv traz Tkinter.
- `xvfb-run -a` para o Tk de verdade.
- Chromium sem janela via Playwright com `executable_path` lido de `~/.chromium-path`.
- PyPI (`pip download`, JSON em `pypi.org/pypi/<nome>/json`) e npm (`npm view`, `npm pack`).
- Busca na web (ferramenta de busca) e leitura de páginas do GitHub pela ferramenta de leitura da web (com limites, abaixo).

## O que falhou (e como segui)
- `curl` para `github.com` e `api.github.com`: **403** do proxy. Segui com a ferramenta de leitura da web e com os pacotes do PyPI/npm.
- `docs.python.org` pelo `curl`: sem resposta (código 000). Li o `turtle.py` instalado localmente (3.10 a 3.14).
- `framagit.org` (Basthon): **bloqueado** pelo proxy. Basthon ficou "não verificado" no `PESQUISA.md`.
- Página de commits do GitHub (`github.com/skulpt/skulpt/commits/master`): **429** (limite de requisições). A data do último
  commit do Skulpt ficou "não verificada".
- `/usr/bin/time` não existe; medi tempo com `date +%s.%N`.
