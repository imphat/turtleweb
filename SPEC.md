# turtleweb: especificação

> Leia este arquivo inteiro, depois o `CLAUDE.md`, antes de qualquer ação. Quem decide o que vale é o João; este arquivo diz o que
> queremos, como saber que ficou pronto, e quando parar.

## 1. Por que existe

Existe um app local (Flask) em que crianças de 8 a 12 anos aprendem Python com um tutor. Elas escrevem programas com `import turtle`,
e hoje o desenho aparece numa **janela do Tk no computador onde o app roda**. Queremos que o mesmo programa, **sem mudar uma linha**,
desenhe **dentro do navegador**, para o app poder rodar num servidor (por exemplo um Raspberry) e ser usado de qualquer aparelho,
inclusive um iPad (Safari).

**turtleweb** é a biblioteca que faz isso. Ela nasce como projeto independente e depois é plugada no app.

## 2. Meta e critério de "pronto"

O programa da criança continua assim:

```python
import turtle
t = turtle.Turtle()
t.forward(100)
turtle.done()
```

e roda **no servidor**, com o Python de verdade, como processo separado. Ao importar `turtle`, o programa recebe o módulo do
turtleweb em vez do Tk, e o desenho aparece numa página (um canvas) que o servidor entrega ao navegador.

Está pronto quando:

1. Todos os programas de `corpus/` rodam e desenham **como o turtle de verdade** (critérios de aceite na seção 7).
2. A **lista de comandos** que a tartaruga executou sai **no formato da seção 5**, igual à de hoje.
3. Funciona no **Chrome/Edge no computador e no Safari do iPad** (teclado, mouse e toque).
4. Fechar a janela, `turtle.done()` e o botão **■ Parar** do app se comportam como na seção 6.
5. Um `INTEGRACAO.md` explica como plugar no app em uma tarde.

**Fora de escopo:** rodar o Python dentro do navegador (Skulpt, Pyodide, Brython) como caminho principal; som; 3D; gráficos que
não sejam do `turtle`; contas, login ou segurança do servidor (outro projeto).

## 3. Etapa 0: pesquisa antes de escrever (obrigatória)

Antes de escrever código da biblioteca, descubra se já existe o que precisamos. Escreva `PESQUISA.md` e **pare** (o João decide).

**O que procurar** (nada disso foi verificado; confirme, com links e datas): turtle do Skulpt; turtles para Pyodide/PyScript;
ColabTurtle e similares (turtle em SVG para notebooks); projetos de turtle por WebSocket; backends de canvas alternativos para o
`turtle` da biblioteca padrão; qualquer pacote "turtle para a web".

**Critérios** (anote sim, não ou parcial para cada candidato): mesma interface do `turtle` da biblioteca padrão; **Python roda no
servidor** (o programa é um processo separado); eventos de teclado e clique (`onkey`, `onscreenclick`, `ontimer`...);
`textinput`/`numinput`; animação e `speed`; preenchimento (`begin_fill`) e `write`; licença livre; mantido nos últimos 2 anos;
funciona sem Tkinter no servidor.

**Uma hipótese a testar logo no começo** ("canvas falso"): o módulo `turtle` da biblioteca padrão separa a lógica (andar,
virar, formas, preenchimento, animação) do desenho no Tk (`TurtleScreenBase`). Se um **canvas falso** com a mesma interface do
`tkinter.Canvas` (e uma "raiz" falsa com `after`, `mainloop`, `bind`) mandar cada operação de desenho para o navegador, o turtle
real continua fazendo a lógica, e a fidelidade é quase total sem reimplementar cada comando. Faça um **teste de fogo** (um
quadrado e um círculo no navegador) antes de recomendar ou descartar.

**Regra de decisão** (escreva a recomendação seguindo isto):
- se um projeto existente cobrir ao menos 80% dos critérios, a recomendação é embrulhá-lo;
- senão, se o canvas falso passar no teste de fogo, a recomendação é seguir por ele;
- senão, a recomendação é um módulo `turtle` próprio, com a mesma interface, que manda comandos de alto nível.

`PESQUISA.md` termina com: a recomendação, os riscos, uma estimativa de esforço por marco e o que o João precisa decidir.

## 4. Arquitetura-alvo (a confirmar na Etapa 0 e no M1)

```
programa da criança (processo filho, Python de verdade)
   import turtle   ->  turtleweb (módulo no lugar do Tk)
        |  eventos de desenho (JSON, uma linha por evento)       ^  eventos do navegador (clique, tecla, timer, resposta de textinput)
        v                                                        |
   servidor (qualquer Flask/WSGI; a biblioteca traz um blueprint de exemplo e um servidor de demonstração)
        |  SSE ou WebSocket                                       ^  POST ou WebSocket
        v                                                        |
   página com canvas (turtleweb.js)
```

Restrições:
- O programa roda com `sys.executable -u`, `cwd` na pasta do projeto, `PYTHONUTF8=1`, e **sem Tkinter instalado**.
- O canal entre o processo filho e o servidor tem de funcionar em **Linux, macOS e Windows** (sem FIFO; prefira um socket em
  `127.0.0.1` cuja porta chega por variável de ambiente, ou a saída padrão com um prefixo reservado; justifique a escolha).
- Python **3.10 ou mais novo** (o Raspberry Pi OS traz o 3.11).
- Sem dependência de JS pesado: um arquivo `turtleweb.js` sem framework e sem CDN.
- Muitos eventos por segundo (animação de uma espiral): agrupar e limitar a taxa; o `speed()` e o `tracer()` do turtle valem.

## 5. Formato da lista de comandos (compatibilidade com o app)

Hoje o app, quando a variável de ambiente `PP_TURTLE_LOG` aponta um arquivo, grava **uma linha JSON por comando** que a tartaruga
executou, e usa isso para conferir lições e ideias de desenho e para o tutor saber o que foi desenhado.
**O turtleweb tem de gravar o mesmo arquivo, no mesmo formato**, para nada do app mudar:

- Cada linha: `["nome", arg1, arg2, ...]` (no máximo 4 argumentos) em JSON, com `\n` no fim.
- Só os comandos desta tabela são gravados; **apelidos viram o nome canônico**:

  | Canônico | Apelidos |
  |---|---|
  | `forward` | `fd` |
  | `backward` | `back`, `bk` |
  | `left` | `lt` |
  | `right` | `rt` |
  | `goto` | `setpos`, `setposition` |
  | `setheading` | `seth` |
  | `setx`, `sety`, `home`, `circle`, `dot`, `stamp`, `write` | (nenhum) |
  | `color`, `pencolor`, `fillcolor` | (nenhum) |
  | `pensize` | `width` |
  | `penup` | `pu`, `up` |
  | `pendown` | `pd`, `down` |
  | `begin_fill`, `end_fill` | (nenhum) |

- Valores: número vira `float` arredondado a 3 casas (inclusive inteiros: `100` vira `100.0`); `bool` e `None` ficam como são;
  texto é cortado em 30 caracteres; tupla ou lista vira lista (até 4 itens), com os mesmos valores simplificados; qualquer outro
  tipo vira `null`.
- **Só o comando de nível mais alto conta**: `circle` chama outros comandos por dentro e grava só `circle`.
- Os comandos que não estão na tabela (`hideturtle`, `speed`, `bgcolor`, `onkey`, `listen`...) **não** são gravados.
- Ordem: a ordem em que o programa os executou.

Os arquivos `corpus/*.esperado.json` mostram o resultado esperado de cada programa determinístico, neste formato.

## 6. Ciclo de vida (como o app espera que aconteça)

- **O programa termina sozinho** (chega ao fim sem `done()`): o turtle de verdade fecha a janela junto. No turtleweb, o desenho
  **fica visível** na página, marcado como "terminou", até a próxima execução.
- **`turtle.done()` / `mainloop()`**: o programa fica esperando até **a janela fechar**. No turtleweb, "fechar a janela" é um
  botão da página (ou o servidor avisar) e o processo termina com código 0.
- **■ Parar** do app: o servidor encerra o processo (isso já existe); a página mostra "parado" e mantém o desenho.
- **Erro no programa**: o traceback vai para o stderr como hoje (o app o mostra à criança); o desenho feito até ali fica.
- **`textinput` e `numinput`**: abrem uma caixa na página e devolvem o valor ao programa; cancelar devolve `None`.
- **Uma execução nova** limpa a página.

## 7. Aceite: como medir

`corpus/` tem os programas (`index.json` diz o tipo de cada um).
1. **Determinísticos** (`*.esperado.json`): a lista de comandos gravada **é idêntica** à esperada. Sem navegador.
2. **Geometria** (opcional, com `xvfb` e `python3-tk`): comparar com o turtle de verdade (segmentos desenhados, cores, polígonos
   preenchidos) dentro de uma tolerância pequena e documentada. Se o ambiente não suportar, registre no relatório e siga.
3. **Fumaça no navegador** (Playwright + Chromium sem janela): a página abre, recebe eventos, o canvas fica diferente de vazio e
   a cor dos pontos principais confere (por exemplo, o centro de uma bolinha vermelha é vermelho).
4. **Interativos** (`interativo_ou_aleatorio`): rodam sem erro com eventos simulados (clique, tecla, timer, `textinput`); escreva
   você os eventos e o que esperar.
5. **Desempenho**: a espiral e os carimbos (`referencia-espiral`, `referencia-carimbos`) terminam de aparecer em poucos segundos
   num computador comum, sem travar a página.
6. **Safari/iPad**: quem testa é o João; deixe um `TESTE-IPAD.md` com o passo a passo e o que observar.

## 8. Prioridade dos comandos

A contagem de uso está em `COMANDOS.md`. Ordem:
- **P0 (M2):** `Turtle`, `forward`, `backward`, `left`, `right`, `goto`, `setheading`, `setx`, `sety`, `home`, `circle`, `dot`,
  `write` (com `font=`), `penup`, `pendown`, `pensize`, `color`, `pencolor`, `fillcolor`, `begin_fill`, `end_fill`,
  `done`/`mainloop`, `Screen()` básico (`bgcolor`, `title`, `setup`, `colormode`, `tracer`, `update`), `hideturtle`/`showturtle`,
  `speed`, `clear`, `reset`.
- **P1 (M3 e M4):** `textinput`, `numinput`, `onkey`, `onkeypress`, `onkeyrelease`, `listen`, `onscreenclick`, `onclick`,
  `ondrag`, `ontimer`, `xcor`, `ycor`, `pos`, `heading`, `distance`, `towards`, `stamp`, `clearstamp`, `shape`, `shapesize`,
  `undo`, `exitonclick`, `bye`.
- **P2 (se sobrar orçamento):** o resto da documentação oficial do módulo `turtle`.

## 9. Marcos

Uma sessão por marco, **um pull request por marco**, e um `RELATORIO-Mx.md` curto no fim (o que passou, o que não passou, o
que ficou de fora, quanto tempo e quanto do orçamento foi usado, e se recomenda continuar). **Não comece o marco seguinte.**

| Marco | Entrega | Aceite |
|---|---|---|
| M0 | `PESQUISA.md` e recomendação | seção 3 |
| M1 | contrato dos eventos (`docs/contrato.md`), canal, servidor de demonstração, página com canvas, testes com navegador sem janela | um quadrado e um círculo desenhados no navegador por um programa Python real; `referencia-quadrado` com a lista de comandos idêntica |
| M2 | P0 | todos os determinísticos do corpus passam (seção 7, itens 1 e 3); geometria se o ambiente permitir |
| M3 | ciclo de vida e `textinput`/`numinput` (seção 6) | os casos da seção 6 com testes |
| M4 | interação (P1: teclado, clique, arrastar, timer; toque; botões de seta na tela) | os interativos do corpus rodam com eventos simulados; um jogo pequeno (`referencia-pegue-a-bolinha`) funciona no Chromium |
| M5 | endurecimento (desempenho, `tracer/update`, retina, reduzir movimento, muitos carimbos, erros) | seção 7, itens 3 a 5, com o corpus inteiro |
| M6 | pacote instalável (`pip install .`), `INTEGRACAO.md`, `TESTE-IPAD.md`, documentação | consigo plugar no app trocando o módulo; todos os testes passam |

## 10. Limites e paradas (o João não está acompanhando em tempo real)

- **Um marco por sessão.** Terminou o marco, escreva o relatório, abra o pull request e **pare**.
- **Se o aceite do marco não passar depois de 3 tentativas diferentes** para o mesmo problema, **pare**, escreva o que tentou e o
  que bloqueia, e abra o pull request mesmo assim, marcado como incompleto.
- **Não amplie o escopo** (sem recursos que não estão aqui, sem refatorar por gosto). O que for útil, mas fora do pedido, vai
  em `IDEIAS.md`.
- **Se o ambiente impedir algo** (rede, instalar o navegador, `apt`), escreva em `AMBIENTE.md` o que falhou e siga com o que dá
  para fazer sem aquilo.
- **Gasto:** seja econômico: leia só o que precisa, não rode a suíte inteira a cada edição pequena, não gere arquivos grandes.
  Registre no relatório uma estimativa do esforço do marco (número de passos e de execuções de teste).
