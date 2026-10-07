# TESTE-IPAD: roteiro para testar no Safari do iPad

Quem testa é o João. Tempo: ~20 minutos.

## Preparar
1. No computador (ou Raspberry) do servidor, na pasta do projeto:
   ```
   pip install -e . flask
   python demo/app.py --host 0.0.0.0 --port 5000
   ```
   (Rodando de outro Python? Veja `INTEGRACAO.md`, passo 2.)
2. Descubra o IP do servidor na rede (`hostname -I` no Linux). O iPad e o servidor precisam estar **na mesma rede Wi-Fi**.
3. No iPad, abra o Safari em `http://IP-DO-SERVIDOR:5000/`. Escolha um programa na lista e toque em **▶ Executar**.
   (Atalho: `http://IP:5000/?prog=referencia-quadrado` já executa.)

## Roteiro (marque ✔ ou ✘ e anote o que viu)
| # | Programa | O que fazer | O que deve acontecer |
|---|---|---|---|
| 1 | `referencia-quadrado` | Executar | quadrado preto; estado "esperando você fechar a janela"; **Fechar a janela** → "terminou" |
| 2 | `referencia-bolinhas` | Executar | três bolinhas: vermelha, **verde** e azul, com texto "Oi!". Anote o tom do verde (decisão da cor `green`, `DECISOES.md`) |
| 3 | `referencia-estrela`, `referencia-flor` | Executar | desenhos preenchidos, linhas nítidas (tela retina), sem serrilhado forte |
| 4 | `referencia-espiral` | Executar e cronometrar | termina em ~13 s. Repita tocando **Mais rápido** logo no começo: bem mais rápido, **mesmo desenho** |
| 5 | `referencia-controle-setas` | Executar | aparecem os **botões de seta** (▲ ◀ ▼ ▶ e "espaço") sob o desenho. Toque ▲: a tartaruga sobe 20; segure: repete |
| 6 | `ideia-controle_remoto`, `ideia-desenha_teclado` | Executar e usar o teclado do iPad (se tiver teclado externo, as setas) | a tartaruga anda; a página **não rola** quando usa as setas ou espaço |
| 7 | `ideia-pintar_cliques` | Tocar em vários pontos | um ponto colorido onde tocou (confira a posição) |
| 8 | `ideia-pincel_mouse` | Pôr o dedo **em cima da tartaruga** e arrastar | desenha uma linha seguindo o dedo (só funciona se começar na tartaruga, como no Tk) |
| 9 | `referencia-pegue-a-bolinha` | Tocar na bolinha preta | o contador aparece no texto de saída abaixo do desenho |
| 10 | `ideia-poligono_medida` | Executar | abre a caixa "Quantos lados?"; o teclado do iPad aparece; digite 6 → hexágono. Teste **Cancelar** |
| 11 | `referencia-pegue-a-bolinha` | **■ Parar** | estado "parado", o desenho continua |
| 12 | qualquer | Bloquear a tela por 10 s, desbloquear | a página volta a seguir a execução ou mostra "reconectando…" e depois continua (anote o que acontece) |
| 13 | `referencia-espiral` | Ajustes > Acessibilidade > Movimento > **Reduzir movimento** ligado; recarregue e execute | o desenho aparece quase de uma vez |
| 14 | `ideia-relogio_animado` | Girar o iPad (vertical/horizontal) | a área de desenho continua inteira, sem rolagem horizontal da página |

## O que anotar se algo falhar
O número do item, o modelo do iPad e a versão do iOS, o que você viu (foto de tela ajuda) e o texto que a página mostra ao lado dos
botões. No servidor, o terminal onde o demo roda mostra os pedidos recebidos.

## Limites conhecidos (não são defeitos)
- Sem `listen()` no programa, as teclas e os botões de seta não funcionam (igual ao Tk).
- `ondrag` só vale se o toque começa na tartaruga.
- O iPad só alcança o servidor se a rede Wi-Fi permitir conexão entre aparelhos (redes de convidados costumam bloquear).
