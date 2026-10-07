# Contrato dos eventos (turtleweb v1)

Três pontas: o **programa** (processo filho, Python de verdade), o **servidor** (`turtleweb.Session`) e a **página**
(`turtleweb.js`). Tudo é JSON, um objeto por mensagem. Todo objeto tem o campo `t` (tipo).

## 1. Programa ⇄ servidor: socket TCP em 127.0.0.1

- O servidor abre um socket em `127.0.0.1:0` e passa ao filho, por variável de ambiente, `TURTLEWEB_PORT` e `TURTLEWEB_TOKEN`.
- Por que socket, e não stdin/stdout: o `input()` e o `print()` dos programas são do app; um socket funciona igual em Linux,
  macOS e Windows (sem FIFO) e aceita muitas mensagens por segundo.
- Uma linha por mensagem (`\n` no fim), UTF-8. A primeira linha do filho é `hello`; o servidor só aceita quem manda o token certo.

### Filho → servidor
| `t` | Campos | Quando |
|---|---|---|
| `hello` | `v` (1), `token` | ao conectar (dentro de `turtleweb.install()`) |
| `ops` | `ops`: lista de operações de desenho (seção 3) | a cada `update()` / pausa de animação / fim de lote |
| `state` | `s`: `"waiting"` | o programa chegou em `done()` / `mainloop()` |
| `ask` | `id`, `kind` (`"string"`/`"float"`), `title`, `prompt`, `initial`, `min`, `max`, `error` | `textinput` / `numinput` |
| `end` | `code`, `stats`, `unknown` | ao sair do interpretador (o código real vem do processo, se o servidor o conhece) |

### Servidor → filho (vindas da página, só estes tipos passam)
| `t` | Campos | Efeito |
|---|---|---|
| `close` | | "fechar a janela": `done()` termina (ou o turtle recebe `WM_DELETE_WINDOW`) |
| `answer` | `id`, `v` (texto ou `null` para cancelar) | resposta do `ask` com o mesmo `id` |
| `mousedown` / `mouseup` / `mousemove` | `x`, `y` (pixels da janela, origem no canto superior esquerdo), `b` (botão 1-3) | `onscreenclick`, `onclick`, `ondrag`, `onrelease` |
| `keydown` / `keyup` | `k` (nome de tecla do Tk: `Up`, `space`, `a`...), `c` (caractere) | `onkey`, `onkeypress`, `onkeyrelease` (só depois de `listen()`, como no Tk) |
| `speed` | `v` (1 a 1000) | divide o atraso da animação por `v`; não muda o desenho |

## 2. Servidor → página: SSE; página → servidor: POST

- `GET  {base}/events/<sid>`: `text/event-stream`. Cada evento tem `id:` (posição na lista) e `data:` com um objeto. Aceita
  `Last-Event-ID` para continuar de onde parou. O servidor encerra o fluxo depois do estado final.
- `POST {base}/input/<sid>`: corpo JSON com uma mensagem da tabela "Servidor → filho". Responde `{"ok": true|false}`.
- `POST {base}/stop/<sid>` (■ Parar) e `GET {base}/status/<sid>`.

Objetos que a página recebe: `ops` e `ask` (iguais aos do filho), mais:

| `t` | Campos |
|---|---|
| `state` | `s`: `starting` → `running` → `waiting` (opcional) → `ended` (código 0) / `error` (código ≠ 0) / `stopped` (■ Parar); `code` |
| `out` | `s` (`stdout`/`stderr`), `text`: só quando o servidor de demonstração captura a saída do filho |

`ended`, `error` e `stopped` são finais: o desenho continua na página até a próxima execução (outro `sid`).

## 3. Operações de desenho (`ops`)

Cada operação é uma lista; o primeiro item é o nome. Itens do canvas têm um número (`id`) e ficam numa lista de camadas (a
última desenha por cima). Coordenadas em pixels, origem no **centro** da janela, y para baixo (como o canvas do Tk).

| Operação | Significado |
|---|---|
| `["create", id, kind, coords, opts]` | `kind`: `line`, `polygon`, `text`, `image`; `coords`: `[x0,y0,x1,y1,...]` |
| `["coords", id, coords]` | troca as coordenadas |
| `["config", id, opts]` | mescla opções |
| `["raise", id]` / `["lower", id]` | camada |
| `["delete", id]` / `["delete", "all"]` | |
| `["bg", "#rrggbb"]` | cor de fundo |
| `["geometry", w, h]` | tamanho da janela (`setup`) |
| `["title", texto]` | título |
| `["closed"]` | o turtle destruiu a janela |

`opts`: `fill`, `outline` (**sempre `#rrggbb` ou `""`**, nunca nome: os nomes passam pela tabela de cores do Tk, onde `green` é
a cor que o Tk usa), `width`, `capstyle`, `joinstyle`, `anchor`, `text`, `font` (`[família, tamanho, estilo]`; tamanho
negativo = pixels, positivo = pontos).
Dentro de um lote, só o último `coords` de cada item é enviado.

## 4. Lista de comandos (`PP_TURTLE_LOG`)

Independe do canal. Se a variável de ambiente `PP_TURTLE_LOG` aponta um arquivo, o filho grava nele uma linha JSON por
comando de nível mais alto (SPEC, seção 5). Só os argumentos posicionais entram (`font=` não).

## 5. Versão

`hello.v` = 1. Campos novos podem aparecer; quem lê ignora os que não conhece.
