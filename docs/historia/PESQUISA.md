# PESQUISA (M0): já existe um turtle para o navegador com o Python no servidor?

Data da pesquisa: **2026-10-07**. Datas de versão vêm do PyPI (`https://pypi.org/pypi/<nome>/json`) ou do npm (`npm view`),
lidas nesse dia. "Verificado" quer dizer que eu li o código do pacote baixado (`pip download` / `npm pack`) ou rodei algo;
"não verificado" diz por quê.

## Resumo

- **Nenhum projeto existente elegível cobre 80% dos critérios.** O melhor (ColabTurtlePlus) chega a 67%, e todos os de notebook
  ou de navegador falham em eventos e `textinput`, além de não rodarem o programa como processo separado.
- A única solução que passa de 80% é **transmitir uma janela do Tk de verdade por VNC** (Xvfb + noVNC, como o Replit faz), mas ela
  **viola restrições obrigatórias da seção 4** (exige Tkinter e X no servidor, não roda em Windows/macOS, traz JS pesado).
  Por isso a considero **não elegível** (ver a última decisão do João).
- **O teste de fogo do canvas falso passou**: o `turtle` da biblioteca padrão, sem nenhuma alteração e com um `tkinter` falso,
  desenhou o quadrado e o círculo no Chromium com as cores certas, nos Pythons 3.10, 3.11, 3.13 e 3.14 (sem Tkinter instalado).
  Como bônus, `textinput`, `ontimer`, `onscreenclick`, `write` e "fechar a janela" também funcionaram, e **51 dos 56 programas do
  corpus** rodam pelo canvas falso (os 5 restantes param por `input()`/arquivo ausente, não por causa do turtle).
- **Recomendação (pela regra de decisão): seguir pelo canvas falso.**

## Critérios (seção 3)

C1 mesma interface do `turtle` · C2 Python roda no servidor (processo separado) · C3 eventos (`onkey`, `onscreenclick`, `ontimer`)
· C4 `textinput`/`numinput` · C5 animação e `speed` · C6 `begin_fill` e `write` · C7 licença livre · C8 mantido nos últimos 2 anos
(versão ou commit depois de 2024-10-07) · C9 funciona sem Tkinter no servidor.

Pontuação: sim = 1, parcial = 0,5, não ou não verificado = 0 (conservador). 9 critérios; 80% = 7,2 pontos.

| Candidato | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | Total |
|---|---|---|---|---|---|---|---|---|---|---|
| Transmissão por VNC (Xvfb + noVNC) | sim | sim | sim | sim | sim | sim | sim | sim | **não** | 8 (89%), **não elegível** |
| ColabTurtlePlus 2.2.0 | parcial | parcial | não | não | sim | sim | sim | sim | sim | 6 (67%) |
| Skulpt (turtle embutido) 1.2.0 | parcial | não | sim | não | sim | sim | sim | ? | sim | 5,5 (61%) |
| svg-turtle 1.2.0 | sim | parcial | não | não | não | sim | sim | sim | sim | 5,5 (61%) |
| Gist "Python Turtle with Remote Web Rendering" (ebertmi) | sim | sim | parcial | sim | parcial | sim | parcial | não | ? | 5,5 (61%) |
| Brython (turtle embutido) 3.14.3 | parcial | não | não | não | parcial | sim | sim | sim | sim | 5 (56%) |
| ColabTurtle 2.1.0 | parcial | parcial | não | não | sim | parcial | sim | não | sim | 4,5 (50%) |
| mobilechelonian 0.5 | parcial | parcial | não | não | sim | não | sim | não | sim | 4 (44%) |
| jupyturtle 2024.4.1 | parcial | parcial | não | não | parcial | não | sim | não | sim | 3,5 (39%) |
| ipyturtle3 0.1.4 | sim | parcial | não | não | parcial | parcial | sim | não | não | 3,5 (39%) |
| pyo-js-turtle 0.1.1 (Pyodide) | parcial | não | não | não | parcial | parcial | sim | não | sim | 3,5 (39%) |
| Pyodide 314.0.7 / PyScript | não | não | não | não | não | não | sim | sim | sim | 3 (33%) |
| tortoise 0.1.1 (atlastk) | não | parcial | não | não | não | não | sim | não | sim | 2,5 (28%) |
| *Canvas falso (protótipo deste M0, para comparar)* | sim | sim | parcial¹ | sim² | sim | sim | sim | — | sim | — |

¹ clique e timer testados no navegador; teclado implementado e não testado. ² `textinput` testado; `numinput` implementado e não testado.

## Candidato por candidato

### Transmissão por VNC (Xvfb + x11vnc + noVNC/websockify)
- **O que é:** o programa abre uma janela do Tk de verdade num X virtual, e a página mostra essa tela por VNC. O Replit documenta
  esse caminho ([docs.replit.com, streaming-native-graphics-vnc](https://docs.replit.com/hosting/streaming-native-graphics-vnc)).
- **Verificado:** noVNC 1.7.0 (npm, licença MPL-2.0, publicado em 2026-10-05); websockify 0.13.0 (PyPI, LGPLv3, 2025-05-26);
  Xvfb funciona neste ambiente (`xvfb-run`). A fidelidade é a do Tk, por definição.
- **Não verificado:** não montei a cadeia completa (não é o caminho que o SPEC pede).
- **Por que não é elegível:** a seção 4 exige o programa **sem Tkinter instalado** e um canal que funcione em **Linux, macOS e
  Windows** (Xvfb só existe no Linux), e proíbe JS pesado (o noVNC é um cliente VNC inteiro). Também não grava a lista de comandos
  (seção 5), precisa de um servidor X por criança, e teclado/toque no iPad por VNC é ruim.

### ColabTurtlePlus — [PyPI](https://pypi.org/project/ColabTurtlePlus/), [GitHub](https://github.com/mathriddle/ColabTurtlePlus)
- **Verificado (código 2.2.0, publicado em 2026-10-02, MIT):** reimplementação própria em SVG via `IPython.display`; tem classes
  `Turtle`/`Screen`, `circle`, `dot`, `stamp`, `begin_fill`/`end_fill`, `write`, `speed` com animação. **Nenhuma** ocorrência de
  `onkey`, `onscreenclick`, `ontimer`, `textinput` ou `numinput` no código. O README confirma: "most of the missing ones are for
  user events".
- **Por que não serve:** depende do Jupyter para mostrar o desenho; sem eventos nem `textinput`; interface parecida, mas
  reimplementada (a fidelidade não é a do turtle).

### Skulpt — [GitHub](https://github.com/skulpt/skulpt), npm `skulpt`
- **Verificado (pacote npm 1.2.0, publicado em 2022-06-26, MIT):** `src/lib/turtle.js` é uma reimplementação em JS com `onkey`,
  `onclick`, `onscreenclick`, `ondrag`, `ontimer`, `speed`, `tracer`, `begin_fill`, `write`, `stamp`, `undo`; **zero**
  ocorrências de `textinput`/`numinput`.
- **Não verificado:** a data do último commit (o GitHub deu 403 pelo `curl` e 429 pelo WebFetch). No npm, a última versão é de 2022.
- **Por que não serve:** o Python roda **no navegador**, e o SPEC põe isso fora do escopo.

### svg-turtle — [PyPI](https://pypi.org/project/svg-turtle/), [GitHub](https://github.com/donkirkby/svg-turtle)
- **Verificado (código 1.2.0, publicado em 2026-06-18, MIT):** usa o `RawTurtle`/`TurtleScreen` **reais** da biblioteca padrão
  com um `Canvas` falso (`svg_turtle/canvas.py`: `create_line`, `create_polygon`, `create_text`...) e, se o Tkinter não existir,
  põe um módulo `tkinter` vazio em `sys.modules`. **É a mesma ideia do canvas falso**, usada em produção para gerar arquivos SVG.
- **Por que não serve:** gera um arquivo no fim, sem página ao vivo, sem animação, eventos ou diálogos.

### Gist "Python Turtle with Remote Web Rendering" — [gist.github.com/ebertmi](https://gist.github.com/ebertmi/2bc0b67867c3da4434389d31b43a5e41)
- **Verificado (só pelo resumo da página feito pelo WebFetch, não li o código inteiro):** é um `turtle.py` modificado (cabeçalho
  "turtle 1.1b - for Python 3.1", de 2009) em que um `WebCanvas` substitui o canvas do Tk e manda lotes JSON por descritores de
  arquivo 4 e 5; tem `onclick`, `onscreenclick`, `onkey` (com TODOs), `ontimer`, `textinput`/`numinput`. Criado em 2016-07-23,
  última revisão em 2016-08-22. Não declara licença para as mudanças. Era usado pelo site trycoding.io.
- **Não verificado:** se funciona sem Tkinter; se roda nos Pythons 3.10+.
- **Por que não serve:** é uma cópia antiga e modificada do turtle (diverge do da 3.10+), parada desde 2016, e descritores de
  arquivo herdados não funcionam bem no Windows. **Mas confirma que a abordagem já foi usada de verdade.**

### Brython — [PyPI](https://pypi.org/project/brython/), [brython.info](https://www.brython.info/gallery/turtle.html)
- **Verificado (`brython_stdlib.js` da versão 3.14.3, npm 2026-06-19, BSD):** o módulo `turtle` é uma adaptação em SVG;
  `onkey`, `onkeypress`, `onkeyrelease`, `onscreenclick`, `ontimer`, `textinput` e `numinput` existem só para escrever
  "Warning: Screen.xxx() is not implemented." no stderr.
- **Por que não serve:** Python no navegador (fora do escopo) e sem eventos.

### ColabTurtle — [PyPI](https://pypi.org/project/ColabTurtle/), [GitHub](https://github.com/tolgaatam/ColabTurtle)
- **Verificado (código 2.1.0, 2021-03-19, MIT):** funções de módulo em SVG via `IPython.display`, com `speed`, `write`,
  `color`; sem preenchimento, sem eventos, sem diálogos. Parado desde 2021.

### mobilechelonian — [PyPI](https://pypi.org/project/mobilechelonian/), [GitHub](https://github.com/takluyver/mobilechelonian)
- **Verificado (código 0.5, 2018-03-01, BSD):** widget do ipywidgets com `forward`, `left`, `circle`, `speed`, `pencolor`;
  sem preenchimento, `write`, eventos ou diálogos. Parado desde 2018.

### jupyturtle — [PyPI](https://pypi.org/project/jupyturtle/), [GitHub](https://github.com/ramalho/jupyturtle)
- **Verificado (código 2024.4.1, 2024-04-01, BSD):** API própria para notebooks (`move_to`, `jump_to`, `pen_up`...), SVG;
  sem `begin_fill`, `write`, eventos ou diálogos. Última versão antes da janela de 2 anos.

### ipyturtle3 (e ipyturtle, ipyturtlenext) — [PyPI](https://pypi.org/project/ipyturtle3/)
- **Verificado (código ipyturtle3 0.1.4, 2022-06-04, Apache 2.0):** também usa o turtle da biblioteca padrão com uma classe
  `Canvas` própria desenhando no ipycanvas (outra confirmação da abordagem). Mas faz `import turtle` direto (precisa do Tkinter),
  o canvas não tem `bind` nem `create_text`, e depende do Jupyter. ipyturtle 0.2.4 (2019) e ipyturtlenext 0.1.1 (2022) são
  widgets do Jupyter com API própria (só metadados verificados).

### pyo-js-turtle (Pyodide) — [PyPI](https://pypi.org/project/pyo-js-turtle/)
- **Verificado (código 0.1.1, 2022-01-22, MIT):** `import js`, só roda dentro do Pyodide; API parecida, com `begin_fill` e
  `speed`, sem `write` e sem eventos.

### Pyodide e PyScript
- **Verificado:** o `python_stdlib.zip` do pacote npm `pyodide` 314.0.7 (2026-09-16, MPL-2.0) **não tem** `turtle.py` nem `tkinter`.
  `@pyscript/core` 0.7.31 (2026-07-13) existe; não inspecionei se traz turtle.
- **Não verificado:** os turtles da comunidade para PyScript ([CoderDojoTrento/turtle-pyscript](https://github.com/CoderDojoTrento/turtle-pyscript))
  e o WebTigerPython (ETH Zürich, [arXiv 2410.07001](https://arxiv.org/html/2410.07001v1)), que reimplementa o turtle com PixiJS.
  Não segui porque todos rodam o Python no navegador (fora do escopo).
- O Basthon (framagit.org/basthon) também roda no navegador; o framagit está bloqueado pela rede, então não verifiquei como faz o turtle.

### tortoise — [PyPI](https://pypi.org/project/tortoise/), [GitHub](https://github.com/epeios-q37/tortoise-python)
- **Verificado (código 0.1.1, 2019-08-03, MIT):** API própria (`setPosition`, `setColorRGB`, `up`/`down`) sobre o atlastk.
  O atlastk 0.13.5 (2025-05-27) conecta por padrão a um servidor externo (`pAddr = "faas.q37.info"` em `XDHqFaaS.py`), o que
  viola "a biblioteca não faz chamadas de rede para fora".

### Outros achados que não são candidatos
- [kilppari](https://github.com/ahathoor/kilppari), [js-turtle](https://github.com/bjpop/js-turtle), [turtlewax](https://github.com/davebalmer/turtlewax):
  turtles escritos em JavaScript (o programa não é Python).
- pywebio (1.8.4, 2025-04-04) e mplh5canvas: interfaces web para Python, sem turtle.
- Nomes procurados no PyPI sem resultado: `webturtle`, `turtle-web`, `turtle-canvas`, `turtlesvg`, `ipycanvas-turtle`, `basthon`.

## Teste de fogo do canvas falso

Código descartável em [`experimentos/m0_canvas_falso/`](experimentos/m0_canvas_falso/) (não é a biblioteca).

**Como funciona:** antes de `import turtle`, um `tkinter` falso (`fake_tk.py`) entra em `sys.modules`. O `turtle` da biblioteca
padrão roda **sem nenhuma alteração** (nem o `_Root` nem o `ScrolledCanvas` foram trocados). O `Canvas` falso guarda os itens e
emite cada operação (`create`, `coords`, `config`, `raise`, `delete`, `bg`...) como JSON. As operações saem em lote a cada
`update()`/`after()`, que o turtle já chama a cada quadro da animação. Um servidor Flask passa os lotes à página por SSE, e a
página (cerca de 100 linhas de JS, sem framework) redesenha os itens num `<canvas>`.

**A fronteira é pequena e estável:** o turtle usa do Tk só ~40 métodos (`create_line/polygon/text/image`, `coords`,
`itemconfigure`, `tag_raise`, `delete`, `update`, `after`, `bind`, `tag_bind`, `winfo_rgb`, `bbox`, `cget/config`...). O
`fake_tk.py` registra qualquer método não implementado, e nenhum foi chamado no corpus inteiro. Entre 3.11 e 3.13, a única mudança
nessa fronteira foi no `_update` (passou a chamar `update_idletasks`).

**Resultados** (`test_fogo.py`, Chromium sem janela, filho sem Tkinter):

| Verificação | 3.10 | 3.13 | 3.14 |
|---|---|---|---|
| Quadrado: três lados vermelhos `(255,0,0)`, por dentro branco | passou | passou | passou |
| Círculo com `begin_fill`: borda azul `(0,0,255)`, centro `lightblue` `(173,216,230)` | passou | passou | passou |
| Fora do desenho: branco | passou | passou | passou |
| `done()` espera; botão "Fechar a janela" termina com código 0 | passou | passou | passou |
| `bgcolor("lightyellow")` | passou | passou | passou |
| `textinput` respondido na página; `write("Olá, Ana", font=...)` aparece | passou | passou | passou |
| `ontimer` desenha uma bolinha verde `(0,255,0)` | passou | passou | passou |
| `onscreenclick`: o clique faz a tartaruga andar até o ponto | passou | passou | passou |

13 de 13 verificações em cada versão. O 3.11 rodou o quadrado e o círculo sem navegador, com saída idêntica à do 3.13. As imagens
estão em `experimentos/m0_canvas_falso/quadrado_circulo.png` e `interacao.png`.

**Corpus inteiro pelo canvas falso** (`rodar_corpus.py`, sem navegador e sem atrasos): **51/56 sem erro** em 3.10, 3.13 e 3.14,
incluindo **todos os 35 determinísticos**. Os 5 restantes não falham por causa do turtle: 3 usam `input()` (o stdin estava
fechado), 1 lê `desenho.txt` (não existe no corpus) e 1 repete `textinput` até receber um número (o teste não respondia).

**Desempenho:** a `referencia-espiral` leva **12,7 s** pelo canvas falso e **13,6 s** no Tk de verdade (com Xvfb). O tempo é o
mesmo porque a animação é a do próprio turtle (`speed`, `delay`). Ela gera 11.052 operações (616 KB de JSON), e os carimbos, 429.

**Achados que mudam o projeto:**
1. **O canal não pode ser o stdin/stdout do filho:** 3 programas do corpus usam `input()`. O protótipo usou o stdin para
   simplificar; a biblioteca deve usar um **socket em `127.0.0.1` com a porta numa variável de ambiente** (funciona em Linux,
   macOS e Windows).
2. **As cores precisam sair como `#rrggbb`:** o Tk usa os nomes do X11, e alguns têm valor diferente no CSS (`green` é
   `#00ff00` no Tk e `#008000` no CSS; `light blue` com espaço não existe no CSS). O protótipo converte em Python; a biblioteca
   deve embutir a tabela de cores do Tk, porque `rgb.txt` não existe no Windows nem no macOS.
3. **Medida de texto:** o turtle pergunta ao canvas o tamanho do texto (`bbox`) para `write(move=True)`. Em Python só dá para
   estimar; a diferença é de alguns pixels.

## Recomendação

Pela regra de decisão da seção 3: nenhum projeto elegível cobre 80% dos critérios, e o canvas falso passou no teste de fogo.
**Recomendo seguir pelo canvas falso:** o turtleweb fornece um `tkinter` falso (ou um `turtle` que o instala e carrega o turtle da
biblioteca padrão), um canal por socket local, um blueprint Flask e um `turtleweb.js`. Toda a lógica (andar, virar, `circle`,
preenchimento, `speed`, `tracer`, `undo`, carimbos, eventos) continua sendo a do turtle de verdade.

A lista de comandos da seção 5 é independente do desenho: um invólucro nos métodos do `RawTurtle` com contador de profundidade
(para gravar só o comando de nível mais alto) deve bastar no M1.

## Riscos

| Risco | Chance | Efeito | O que fazer |
|---|---|---|---|
| Depender de partes internas do `turtle` (`TurtleScreenBase`, `ScrolledCanvas`, `_Root`) que mudem num Python futuro | média | um Python novo quebra | fronteira pequena (~40 métodos) e já testada em 3.10, 3.11, 3.13 e 3.14; testes em várias versões; o `fake_tk` avisa quando aparece um método desconhecido |
| Eventos chegarem só no `mainloop` e não durante animações e laços com `update()` | alta se nada for feito | jogos com `while True: ... update()` não respondem às teclas | processar a fila de entrada também em `update()` e `after()` (M4) |
| Volume de mensagens (espiral: 11 mil operações, 616 KB) | média | página lenta no iPad | juntar `coords` repetidos do mesmo item no lote, limitar a taxa, compactar (M5) |
| Animação fiel ao Tk demora (espiral ~13 s) e pode bater de frente com a seção 7, item 5 ("poucos segundos") | alta | decisão de produto | o João decide (abaixo) |
| Medida de texto estimada no Python | baixa | `write(move=True)` e `align` com alguns pixels de diferença | tabela de larguras médias por fonte; tolerância documentada no teste de geometria |
| `onclick` numa tartaruga precisa saber que item está sob o ponteiro | média | `onclick`/`ondrag` de tartaruga não funcionam de primeira | teste de acerto (`find_overlapping`) no Python ou no JS (M4) |
| Formas de imagem (`register_shape("x.gif")`, `bgpic`) | baixa (não aparecem no corpus) | P2 | servir a imagem pela página |
| Um programa que importe `tkinter` direto recebe o falso | baixa | erro estranho | decidir no M1 como o turtleweb entra (abaixo) |
| Safari/iPad: SSE, teclado virtual, toque | média | interação ruim no iPad | botões de seta na tela (M4); teste do João (`TESTE-IPAD.md`) |

## Estimativa de esforço por marco (seguindo o canvas falso)

"Passos" são chamadas de ferramenta de uma sessão do agente; é uma estimativa grosseira, baseada no tamanho deste M0 (~70 passos).

| Marco | O que muda com o canvas falso | Tamanho | Passos | Execuções de teste |
|---|---|---|---|---|
| M1 | o protótipo vira base: contrato, canal por socket, blueprint, página, lista de comandos | médio | 50–80 | 15–25 |
| M2 | quase tudo vem do turtle real; o trabalho é a fidelidade do desenho (texto, `dot`, carimbos, cores) e a lista de comandos de todos os determinísticos | pequeno a médio | 40–70 | 15–25 |
| M3 | ciclo de vida (terminou, parado, erro, nova execução) e diálogos com cancelar | médio | 30–60 | 10–20 |
| M4 | teclas (nomes do Tk × do navegador), clique em tartaruga, arrastar, eventos durante animação, toque e botões de seta | o maior | 60–100 | 20–35 |
| M5 | juntar e limitar mensagens, `tracer`, retina, reduzir movimento, muitos carimbos | médio | 40–80 | 15–30 |
| M6 | pacote, `INTEGRACAO.md`, `TESTE-IPAD.md` | pequeno | 25–45 | 5–10 |

## O que o João precisa decidir

1. **Aprovar o caminho do canvas falso** (ou pedir outro: o módulo próprio da regra de decisão, ou reconsiderar o VNC, que é
   fiel mas exige Tkinter e X no servidor e só roda no Linux).
2. **Velocidade × fidelidade:** a espiral leva ~13 s no Tk de verdade e o mesmo no navegador. A seção 7, item 5, pede "poucos
   segundos". Vale o tempo do Tk (fiel; minha recomendação), ou o turtleweb deve acelerar (por exemplo, limitar a animação a
   alguns segundos)?
3. **`input()` nos programas:** 3 programas do corpus usam `input()`. O turtleweb vai deixar o stdin e o stdout livres para o app
   (o canal será um socket). O app já cuida do `input()` hoje? Se não, isso fica fora do turtleweb?
4. **Como o turtleweb entra no programa** (posso decidir no M1, se preferir): (a) uma pasta no `PYTHONPATH` com um `tkinter`
   falso, que o `turtle` da biblioteca padrão usa sem saber; ou (b) uma pasta com um `turtle.py` que instala o falso e carrega o
   turtle da biblioteca padrão. Recomendo (b), porque não engana um programa que importe `tkinter` direto.
5. **O que fazer com `experimentos/m0_canvas_falso/`:** manter como referência até o M1 e apagar depois (minha sugestão), ou
   apagar já.

> Nota (M6): a pasta `experimentos/m0_canvas_falso/` citada acima foi removida no pacote final (decisão 6 do `DECISOES.md`); continua no histórico do git (commit `dd770d3`).
