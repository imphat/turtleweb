# PROGRESSO (leia primeiro se a sessão for reaberta)

Ramo: `turtleweb-m1-m6`. Um commit por marco ("M1: ..."). Regras de parada: ver o prompt (`prompts/M1-M6.md`) e `DECISOES.md`.

| Marco | Estado |
|---|---|
| M1 | pronto (ver RELATORIO-M1.md) |
| M2 | pronto (RELATORIO-M2.md) |
| M3 a M6 | não começados |

## Comandos
```
# Python com Tk (testes, geração da tabela de cores): ~/.venvs/turtleweb/bin/python
cd tests && ~/.venvs/turtleweb/bin/python -m pytest -q                 # tudo
cd tests && ~/.venvs/turtleweb/bin/python -m pytest -q test_comandos.py test_session.py   # sem navegador
cd tests && ~/.venvs/turtleweb/bin/python -m pytest -q browser          # Chromium sem janela
~/.venvs/turtleweb/bin/python demo/app.py --port 5000                  # servidor de demonstração
```
Pythons sem Tkinter para o filho: `python3.11`, `python3.13`; Python 3.10: `uv python install 3.10`.
