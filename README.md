# turtleweb

Faz o `import turtle` de um programa Python desenhar **dentro do navegador**, com o Python rodando no servidor e **sem Tkinter**:
o `turtle` da biblioteca padrão roda sem alteração sobre um `tkinter` falso, e cada operação de desenho vai por um socket local
até a página.

| Para quê | Arquivo |
|---|---|
| Plugar no app em uma tarde | `INTEGRACAO.md` |
| Testar no Safari do iPad | `TESTE-IPAD.md` |
| Formato das mensagens | `docs/contrato.md` |
| Especificação e decisões | `SPEC.md`, `DECISOES.md`, `PESQUISA.md` |
| Relatórios | `RELATORIO-FINAL.md` (e `RELATORIO-M0.md` a `RELATORIO-M5.md`) |
| Ideias fora do escopo | `IDEIAS.md` |

```
turtleweb/        o pacote (install(), Session/Hub, blueprint Flask, turtleweb.js)
demo/             servidor de demonstração:  python demo/app.py
tests/            pytest (lista de comandos, geometria × Tk real, canal, navegador sem janela)
corpus/           programas de teste e listas esperadas
tools/            gerador da tabela de cores do Tk
```

Testes: `cd tests && python -m pytest -q` (geometria precisa de `xvfb-run` e Tkinter; navegador, de Playwright + Chromium; pulam sozinhos).
