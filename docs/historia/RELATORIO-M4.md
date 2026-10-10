# RELATÓRIO M4 (interação)

## 1. O que foi entregue
- Página: mouse e toque pelo mesmo caminho (Pointer Events: `mousedown/mousemove/mouseup`, botões 1 a 3, coordenadas
  convertidas para a janela lógica mesmo com o canvas reduzido), teclado (nomes de tecla do Tk: `Up`, `space`, `Return`, `plus`...,
  repetição automática como no Tk, soltar tudo ao perder o foco), botões de seta + espaço na tela (só em tela de toque e só
  depois de `listen()`; `opts.pad` força ligado/desligado), mensagens enviadas em lote e em ordem.
- Python: `Canvas.bind/tag_bind` com acerto de clique na tartaruga (`onclick`, `ondrag`, `onrelease`), teclas só depois de `listen()`
  (como no Tk), arrasto reduzido à última posição, eventos processados em `update()` (laços de jogo com `tracer(0)`/`update()`) e a cada passo da animação.
- Testes: `tests/browser/test_m4.py` (15 casos) e `tests/test_interativos.py` (os 21 interativos com eventos simulados).
- **Ficou de fora:** `onkey` com modificadores (Ctrl/Alt/Meta não são enviados, para não roubar atalhos do navegador); `Motion` sem botão.

## 2. Aceite
| Item | Resultado |
|---|---|
| Os 21 interativos do corpus rodam com eventos simulados, sem erro | **passou** (stderr vazio, nenhum método do Tk sem implementar) |
| `referencia-pegue-a-bolinha` funciona no Chromium | **passou** (acha a bolinha no canvas, clica, pontua; versão determinística também) |
| Teclado, clique, arrastar, timer, toque e botões de seta | **passou** (toque simulado no Chromium; **Safari/iPad não testado**: é do João, `TESTE-IPAD.md`) |

## 3. O que travou ou surpreendeu
- `ondrag` só vale se o clique **começa na tartaruga** (igual ao Tk): meu primeiro teste arrastava do vazio.
- O desenho (socket) e o `print` (stdout) chegam por caminhos diferentes: os testes esperam o pixel em vez de dormir.
- `ideia-exame_desenhista` registra `onkey` sem `listen()`, então a tecla `q` não faz nada, como no Tk.

## 4. Esforço
~30 passos; ~12 execuções de teste.

## 5. Recomendação
Continuar para o M5.

## 6. Decisões do João
Nenhuma nova.
