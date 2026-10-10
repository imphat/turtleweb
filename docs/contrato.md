# As mensagens do turtleweb

Este é o formato das mensagens trocadas entre as três partes do turtleweb. Você só precisa dele se for escrever o seu
próprio servidor (sem o blueprint de Flask), a sua própria página (sem o `turtleweb.js`) ou mexer no protocolo. Para usar
a biblioteca do jeito normal, o [guia de integração](../INTEGRACAO.md) basta.

As três partes:

- o **programa**: o processo Python do aluno, com o Tk falso dentro;
- o **servidor**: a `turtleweb.Session`, dentro do seu app;
- a **página**: o `turtleweb.js`, no navegador.

Toda mensagem é um objeto JSON com um campo `t`, que diz o tipo. Quem recebe um campo que não conhece deve ignorá-lo:
assim dá para acrescentar coisas sem quebrar quem já usa.

## 1. Programa e servidor conversam por um socket local

O servidor abre um socket TCP em `127.0.0.1`, numa porta livre, e passa ao programa a porta e uma senha pelas variáveis de
ambiente `TURTLEWEB_PORT` e `TURTLEWEB_TOKEN`. Cada mensagem é uma linha (JSON + `\n`, em UTF-8). A primeira linha que o
programa manda é `hello`, com a senha; o servidor fecha qualquer conexão que não comece assim.

Por que um socket e não a entrada e a saída padrão do programa? Porque elas são do aluno: o `input()` e o `print()`
precisam continuar funcionando como sempre. E um socket local funciona igual em Linux, macOS e Windows.

### Do programa para o servidor

| `t` | Campos | Quando |
|---|---|---|
| `hello` | `v` (versão, hoje 1), `token` | ao conectar |
| `ops` | `ops`: lista de operações de desenho (seção 3) | a cada quadro da animação, no máximo uns 60 por segundo |
| `state` | `s`: `"waiting"` | o programa chegou no `turtle.done()` ou `mainloop()` e está esperando |
| `ask` | `id`, `kind` (`"string"` ou `"float"`), `title`, `prompt`, `initial`, `min`, `max`, `error` | `textinput` ou `numinput`; `error` vem preenchido quando a resposta anterior não valia |
| `end` | `code`, `stats`, `unknown` | o programa terminou; `unknown` lista métodos do Tk que o turtle chamou e o Tk falso não tem |

### Do servidor para o programa

São as mensagens que vêm da página. O servidor só deixa passar estes tipos:

| `t` | Campos | O que acontece no programa |
|---|---|---|
| `close` | | "fechar a janela": o `done()` termina; se o programa ainda estava desenhando, ele acaba sem mensagem de erro |
| `answer` | `id`, `v` (o texto digitado, ou `null` se cancelou) | resposta ao `ask` de mesmo `id` |
| `mousedown`, `mouseup`, `mousemove` | `x`, `y` (pixels da janela, a partir do canto de cima à esquerda), `b` (botão: 1, 2 ou 3) | `onscreenclick`, `onclick`, `ondrag`, `onrelease` |
| `keydown`, `keyup` | `k` (nome da tecla no Tk: `Up`, `space`, `Return`, `a`...), `c` (o caractere) | `onkey`, `onkeypress`, `onkeyrelease` |
| `speed` | `v` (de 1 a 1000) | divide as pausas da animação por `v`; o desenho final é o mesmo |

Dois detalhes que pegam muita gente, e que são iguais no Tk de verdade:

- as teclas só chegam ao programa depois que ele chama `listen()`;
- o `onkey` reage quando a tecla é **solta**. Por isso, quando um botão de seta fica apertado na página, ela manda
  "soltou, apertou" repetidamente, como o teclado faz no Linux.

E um comportamento do turtleweb: se chega um clique, tecla ou movimento enquanto uma função de evento do programa ainda
está rodando (por exemplo, a tartaruga ainda está andando por causa do último arraste), a mensagem espera a função
terminar. Funções de evento nunca rodam uma dentro da outra. De vários `mousemove` seguidos, só o último é entregue;
cliques, soltar e teclas nunca são descartados.

## 2. Servidor e página: server-sent events e POST

| Rota | O que é |
|---|---|
| `GET {base}/events/<sid>` | fluxo `text/event-stream` com tudo o que a página precisa mostrar |
| `POST {base}/input/<sid>` | uma mensagem (ou uma lista delas, em ordem) para o programa; responde `{"ok": true}` ou `false` |
| `POST {base}/stop/<sid>` | para o programa |
| `GET {base}/status/<sid>` | `{"sid", "state", "code", "events"}` |

Cada evento do fluxo tem um `id:` crescente e um `data:` com um objeto. Para continuar de onde parou, o cliente manda o
último id recebido no cabeçalho `Last-Event-ID` (o navegador faz isso sozinho ao reconectar) ou no parâmetro `?last=`
(o `turtleweb.js` usa quando reabre a conexão por conta própria, por exemplo quando o iPad volta da tela bloqueada). O
servidor encerra o fluxo depois do estado final.

A página recebe `ops` e `ask` (iguais aos do programa) e mais:

| `t` | Campos |
|---|---|
| `state` | `s`: `starting` (esperando o programa conectar), `running`, `waiting` (no `done()`), e no fim `ended` (terminou, código 0), `error` (terminou com erro) ou `stopped` (foi parado); `code`: o código de saída |
| `out` | `s` (`stdout` ou `stderr`), `text`: a saída do programa, só quando o servidor a captura (o `Session.start` captura) |

Depois de `ended`, `error` ou `stopped` o desenho fica na página até a próxima execução.

Uma execução muito longa não guarda o histórico inteiro: de tempos em tempos o servidor troca o histórico por um retrato do
desenho atual, uma mensagem `ops` com `"reset": true`. Quem recebe um `reset` apaga o que tinha e aplica as operações.

## 3. As operações de desenho

Cada operação é uma lista cujo primeiro item é o nome. O canvas tem itens numerados (`id`) numa pilha de camadas: o último
fica por cima. As coordenadas são em pixels, com a origem no **centro** da janela e o y crescendo para baixo, como no
canvas do Tk (o turtle já faz a conversão do y para cima).

| Operação | O que faz |
|---|---|
| `["create", id, tipo, coords, opções]` | cria um item; `tipo` é `line`, `polygon`, `text` ou `image`; `coords` é `[x0, y0, x1, y1, ...]` |
| `["coords", id, coords]` | muda as coordenadas do item |
| `["config", id, opções]` | muda algumas opções do item |
| `["raise", id]`, `["lower", id]` | manda o item para cima ou para baixo de todos |
| `["delete", id]`, `["delete", "all"]` | apaga um item ou tudo |
| `["bg", "#rrggbb"]` | cor de fundo |
| `["geometry", largura, altura]` | tamanho da janela (o `setup` do turtle); o padrão é 640 × 600 |
| `["title", texto]` | título |
| `["listen"]` | o programa chamou `listen()`: a página pode mostrar os botões de seta e de teclado |
| `["closed"]` | o turtle fechou a janela |

As opções possíveis são `fill`, `outline`, `width`, `capstyle`, `joinstyle`, `anchor`, `text` e `font`.

- Cores (`fill`, `outline`) chegam **sempre** como `#rrggbb` ou `""` (sem cor), nunca como nome. Os nomes são convertidos
  no programa pela tabela do Tk, porque alguns nomes têm valor diferente no Tk e no CSS.
- `font` é `[família, tamanho, estilo]`. Tamanho positivo é em pontos, negativo é em pixels, como no Tk.
- Uma linha de comprimento zero com ponta redonda é um ponto: é assim que o `dot()` do turtle desenha. Desenhe como
  círculo, porque o Safari não desenha traço de comprimento zero.
- Dentro de um mesmo lote, o servidor só manda a última mudança de coordenadas de cada item.

## 4. A lista de comandos (`PP_TURTLE_LOG`)

Não passa pelo canal. Se a variável `PP_TURTLE_LOG` aponta para um arquivo, o programa grava nele uma linha JSON para cada
comando de turtle que chamou diretamente, por exemplo `["forward", 100.0]`. Apelidos viram o nome principal, números saem
com três casas, textos são cortados em 30 caracteres e só os argumentos posicionais entram (o `font=` do `write` não). A
especificação completa está na seção 5 do [SPEC.md](../SPEC.md).

## 5. Versão

Este documento descreve a versão 1 (`hello.v`). Campos novos podem aparecer sem mudar a versão; quem lê ignora o que não
conhece.
