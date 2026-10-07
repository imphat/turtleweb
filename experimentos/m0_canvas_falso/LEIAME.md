# Protótipo descartável do M0: canvas falso

Não é a biblioteca. Serve só para o teste de fogo da seção 3 do `SPEC.md` (resultado no `PESQUISA.md`).

| Arquivo | Para quê |
|---|---|
| `fake_tk.py` | `tkinter` falso: o `Canvas` emite cada operação como JSON no stdout (prefixo `@@TW@@ `) |
| `run.py` | ponto de entrada do processo filho: instala o falso e roda o programa |
| `server.py` | servidor Flask de teste: roda o filho, passa os lotes à página por SSE, devolve cliques e respostas pelo stdin |
| `page.html` | página com `<canvas>` (JS sem framework) |
| `programas/` | `quadrado_circulo.py` (teste de fogo) e `interacao.py` (`textinput`, `ontimer`, `onscreenclick`) |
| `test_fogo.py` | Playwright + Chromium sem janela: confere a cor dos pontos principais |
| `rodar_corpus.py` | roda o corpus inteiro pelo canvas falso, sem navegador |

```
cd experimentos/m0_canvas_falso
~/.venvs/turtleweb/bin/python test_fogo.py                     # filho em python3.13 (sem Tkinter)
TW_CHILD_PYTHON=/caminho/python3.10 ~/.venvs/turtleweb/bin/python test_fogo.py
~/.venvs/turtleweb/bin/python rodar_corpus.py python3.13
```

Limitação conhecida: usa o stdin do filho como canal de entrada, o que conflita com `input()`. A biblioteca deve usar um socket.
