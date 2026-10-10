# Como o turtleweb funciona por dentro

Este texto é para quem quer entender o código, corrigir alguma coisa ou fazer um fork. Se você só quer usar a biblioteca,
o [README](../README.md) e o [guia de integração](../INTEGRACAO.md) bastam.

## A sacada: trocar o Tk, não o turtle

O módulo `turtle` do Python é dividido em duas partes. Em cima fica a lógica: posição, direção, como fazer um círculo,
preenchimento, velocidade da animação, desfazer, carimbos, eventos. Embaixo fica o desenho propriamente dito, feito num
`tkinter.Canvas`. E a conversa entre as duas partes é pequena: o turtle usa uns 40 métodos do Tk, como `create_line`,
`create_polygon`, `coords`, `itemconfigure`, `delete`, `update`, `after` e `bind`.

Então, em vez de reescrever o turtle (que é o que quase todos os projetos parecidos fazem), o turtleweb entrega ao turtle
um `tkinter` falso com esses métodos. O turtle acha que está desenhando numa janela; na verdade cada chamada vira uma
mensagem pequena que vai para o navegador. O resultado é que tudo o que o turtle sabe fazer continua igual, inclusive
detalhes que ninguém lembra de reimplementar.

## O caminho de um traço

1. O aluno escreve `t.forward(100)`.
2. O turtle da biblioteca padrão calcula a animação e chama, por exemplo, `canvas.coords(5, 0, 0, 100, 0)` várias vezes,
   uma por quadro.
3. O `Canvas` falso (`turtleweb/_fake_tk.py`) anota `["coords", 5, [0, 0, 100, 0]]` num lote.
4. A cada `update()` (que o turtle chama a cada quadro), o lote é enviado pelo socket para o servidor, no máximo uns 60
   lotes por segundo. Dentro de um lote, se o mesmo item mudou de posição várias vezes, só vai a última.
5. A `Session` (`turtleweb/session.py`) recebe o lote, guarda e entrega a todas as páginas conectadas por server-sent events.
6. O `turtleweb.js` aplica as operações numa lista de itens e redesenha o `<canvas>` no próximo quadro do navegador.

O caminho de volta é parecido: a página manda `{"t": "mousedown", "x": 320, "y": 300, "b": 1}`, o servidor repassa pelo
socket, e o Tk falso chama a função que o turtle registrou com `bind`, do mesmo jeito que o Tk de verdade faria.

## Os arquivos

### `turtleweb/__init__.py`: a instalação

`install()` coloca o Tk falso em `sys.modules["tkinter"]`, conecta ao servidor (se `TURTLEWEB_PORT` existir) e registra o
que fazer quando o programa terminar. Ele também instala um gancho de importação: quando o programa faz `import turtle`,
o gancho deixa o turtle carregar normalmente e, logo depois, liga a lista de comandos (`PP_TURTLE_LOG`), se pedida.

Quem chama o `install()` é o `turtleweb/_boot/sitecustomize.py`, que o Python executa sozinho ao iniciar quando a pasta
`_boot` está no `PYTHONPATH`.

### `turtleweb/_fake_tk.py`: o Tk de mentira

É o arquivo mais importante. Tem as classes que o turtle usa (`Tk`, `Canvas`, `Frame`, `Scrollbar`, `PhotoImage`) e um
laço de eventos simples, com três pontos que valem conhecer:

- **Cores.** O Tk aceita nomes como `"light blue"` ou `"grey50"`, que o navegador não entende, e alguns nomes têm valor
  diferente no Tk e no CSS. Toda cor sai como `#rrggbb`, convertida pela tabela de cores do próprio Tk
  (`turtleweb/_colors.py`, gerada por `tools/gen_colors.py`).
- **Eventos.** Cliques, teclas e arrastes chegam numa fila e são tratados quando o programa está esperando
  (`mainloop`/`done`) ou chama `update()`, que é exatamente quando o Tk de verdade os trataria. Teclas só chegam depois de
  `listen()`, como no Tk. Um clique na tartaruga (`onclick`) é decidido aqui mesmo, testando se o ponto cai dentro do
  desenho dela.
- **Tratadores não se aninham.** Se uma função de arraste ainda está animando a tartaruga quando chega o próximo
  movimento do dedo, o movimento espera a função terminar, e de vários movimentos seguidos só vale o último. Sem isso, a
  função seria chamada dentro dela mesma até estourar a pilha (foi o que travou o pincel no iPad).

Qualquer método do Tk que o turtle chamar e que o falso não tenha é anotado e informado no fim da execução. Assim, se uma
versão nova do Python passar a usar algo diferente, os testes avisam.

### `turtleweb/_channel.py`: o fio até o servidor

Um socket TCP em `127.0.0.1`, uma mensagem JSON por linha. Uma thread lê o que vem do servidor e põe numa fila.
Usamos socket, e não a entrada e saída padrão, porque elas pertencem ao programa do aluno (`input()`, `print()`).

### `turtleweb/_cmdlog.py`: a lista de comandos

Embrulha os métodos do turtle (`forward`, `circle`, `color`...) para gravar cada chamada feita pelo programa num arquivo,
uma linha JSON por comando. Um contador de profundidade garante que só a chamada de fora é gravada: o `circle` aparece,
os passos que ele dá por dentro não.

### `turtleweb/session.py`: o servidor

A `Session` abre o socket, espera o programa se conectar (conferindo o token), guarda tudo o que a página precisa numa
lista de eventos numerados e entrega essa lista para quantas páginas quiserem ver. Ela também mantém um modelo do desenho
atual: quando a lista fica grande, o histórico é trocado por um retrato do desenho, então uma página que chega atrasada
(ou um relógio que roda por horas) não acumula memória sem fim. O `Hub` é só um dicionário de sessões por id.

### `turtleweb/flask_blueprint.py`: as rotas prontas

Cinco rotas finas sobre a `Session`. Se o seu servidor não é Flask, este arquivo é o exemplo do que copiar.

### `turtleweb/static/turtleweb.js`: a página

Um arquivo só, sem framework e sem nada de fora. Ele:

- recebe os eventos, aplica as operações numa lista de itens e redesenha o `<canvas>` uma vez por quadro, já na resolução
  de tela retina;
- transforma cliques, toques e teclas em mensagens, traduzindo os nomes de tecla do navegador para os do Tk
  (`ArrowUp` vira `Up`, `" "` vira `space`);
- mostra a caixa do `textinput`/`numinput`, os botões de seta e o botão de teclado em tela de toque;
- reabre a conexão sozinho quando a página volta de uma tela bloqueada, continuando do último evento recebido.

## Fidelidade, e como ela é testada

A pasta `corpus/` tem 56 programas: 35 determinísticos (sempre desenham a mesma coisa) e 21 interativos ou aleatórios.
Para os determinísticos existe o resultado esperado da lista de comandos. A suíte em `tests/` confere:

- **a lista de comandos**, idêntica à esperada, em vários Pythons (3.10, 3.11, 3.13), inclusive sem Tkinter;
- **a geometria**: o mesmo programa roda no Tk de verdade (numa tela virtual, com `xvfb-run`) e no Tk falso, e os itens do
  canvas são comparados um a um, com tolerância de meio pixel;
- **o navegador**: com Playwright e Chromium sem janela, a página abre, desenha, e as cores de pontos escolhidos conferem;
- **a interação**: cliques, teclas, toques, arraste, timers e perguntas simulados, para os programas interativos e para
  programas de teste em `tests/programs/`.

Se você mexer no Tk falso, rode `tests/test_geometria.py`: ele é o que mais rápido acusa um desenho diferente do Tk.

## Para onde dá para levar

Algumas ideias estão em [IDEIAS.md](../IDEIAS.md). As que mais fariam diferença: suporte a imagens nas formas da
tartaruga, medir o texto no navegador, e um servidor de exemplo para FastAPI ou Django.
