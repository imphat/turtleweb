# RELATÓRIO M1 (base: canal, instalação, servidor de demonstração, página)

## 1. O que foi entregue
- `turtleweb/`: `install()` (injeta o `tkinter` falso antes do `turtle`, conecta ao canal, liga a lista de comandos), `_fake_tk.py`
  (canvas falso; já com eventos de mouse/teclado, timers e diálogos, que serão testados em M3/M4), `_channel.py` (socket
  em 127.0.0.1, porta e token por variável de ambiente), `_cmdlog.py` (`PP_TURTLE_LOG`, só o comando de nível mais alto),
  `_colors.py` (tabela de cores do Tk, gerada do Tk real), `session.py` (`Session`, `Hub`), `flask_blueprint.py`, `_boot/sitecustomize.py`,
  `static/turtleweb.js`.
- `demo/` (Flask + página), `docs/contrato.md`, `pyproject.toml`, `tests/`.
- **Ficou de fora** (de propósito): ciclo de vida completo (M3), interação na página (M4), desempenho (M5), pacote/INTEGRACAO (M6).

## 2. Aceite
| Item | Resultado |
|---|---|
| Quadrado e círculo desenhados no navegador por um programa Python real | **passou** (`tests/browser/test_m1.py`: cores de 8 pontos no Chromium; `done()` espera e o botão fecha com código 0) |
| `referencia-quadrado` com a lista de comandos idêntica, pelo canal | **passou** (`test_session.py`, Pythons 3.10, 3.11 e 3.13) |
| Todos os 35 determinísticos com lista idêntica | **passou** (já no M1; `test_comandos.py`) |
| Roda num Python sem Tkinter | **passou** (3.11 e 3.13 do sistema; o 3.10 do `uv` tem Tk, e o falso o substitui) |
| `input()` do programa continua livre | **passou** (`test_input_do_programa_continua_livre`) |

## 3. O que travou ou surpreendeu
- **Cor `green`:** o Tk 8.6.14 real responde `#008000`, não `#00ff00` (ver `DECISOES.md`, item 5). Usei a tabela do Tk real.
- `text=Fechar a janela` do Playwright casava com o texto de estado: usei classes (`.tw-close`).
- Nenhum bloqueio.

## 4. Esforço
~55 passos; execuções de teste: ~12 (corpus 2, sessão 3, navegador 5, depuração 2).

## 5. Recomendação
Continuar para o M2.

## 6. O que o João precisa decidir
Confirmar o item da cor `green` (`DECISOES.md`).
