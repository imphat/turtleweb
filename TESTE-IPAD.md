# Testando no iPad (ou em qualquer tablet e celular)

Os testes automáticos rodam no Chromium, mas o turtleweb foi feito pensando em quem programa num iPad. Toque, teclado
virtual, tela bloqueada e o próprio Safari só dá para conferir num aparelho de verdade. Este roteiro leva uns 20 minutos
e serve para qualquer tablet ou celular.

## Preparando

1. No computador que vai ser o servidor (pode ser um Mac, um PC ou um Raspberry Pi), dentro da pasta do projeto:

   ```
   pip install -e . flask
   python demo/app.py --host 0.0.0.0 --port 5000
   ```

   O `--host 0.0.0.0` deixa outros aparelhos da rede abrirem a página. Sem ele, só o próprio computador acessa.

2. Descubra o IP do computador na rede: `hostname -I` no Linux, ou Ajustes do Sistema > Rede no Mac. O iPad e o
   computador precisam estar na mesma rede Wi-Fi. Redes de convidados costumam bloquear a conversa entre aparelhos.

3. No iPad, abra o Safari em `http://IP-DO-COMPUTADOR:5000/`, escolha um programa e toque em **▶ Executar**. Um atalho:
   `http://IP-DO-COMPUTADOR:5000/?prog=referencia-quadrado` já abre e executa.

## O roteiro

Para cada item, anote se funcionou e o que você viu.

1. **`referencia-quadrado`**: aparece um quadrado preto e a página diz "esperando você fechar a janela". Toque em
   **Fechar a janela**: a página passa a dizer "terminou" e o desenho continua lá.

2. **`referencia-bolinhas`**: três bolinhas (vermelha, verde e azul) e o texto "Oi!". O verde é o verde do Tk, um verde
   escuro (`#008000`).

3. **`referencia-estrela`** e **`referencia-flor`**: desenhos preenchidos, com linhas nítidas na tela retina.

4. **`referencia-espiral`**: cronometre. Deve levar uns 13 segundos, o mesmo tempo que no Tk. Rode de novo tocando
   **Mais rápido** logo no começo: termina bem antes, com o mesmo desenho.

5. **`referencia-controle-setas`**: aparecem botões de seta (▲ ◀ ▼ ▶ e "espaço") embaixo do desenho. Este programa só usa
   ▲ e ▼, então ◀ e ▶ não fazem nada. Toque ▲: a tartaruga sobe. Segure: ela continua subindo.

6. **`ideia-controle_remoto`** e **`ideia-desenha_teclado`**: estes só usam ▲. Toque em **⌨️ Teclado**: o teclado do iPad
   abre (toque de novo para fechar). Usando as setas ou o espaço, a página não deve rolar.

7. **`ideia-pintar_cliques`**: toque em vários pontos. Em cada um aparece um ponto colorido. A tartaruga também deixa uma
   linha entre um toque e outro: é o programa que não levanta a caneta, e o Tk faz o mesmo.

8. **`ideia-pincel_mouse`**: ponha o dedo **em cima da tartaruga** e arraste. A linha segue o dedo. Arrastando muito
   rápido, as curvas ficam mais anguladas: a tartaruga vai para o ponto mais recente em vez de passar por todos, para não
   ficar para trás.

9. **`referencia-pegue-a-bolinha`**: toque na bolinha preta. O placar aparece no texto embaixo do desenho.

10. **`ideia-poligono_medida`**: abre uma caixa perguntando "Quantos lados?" e o teclado do iPad aparece. Digite 6 e
    confirme: sai um hexágono. Rode de novo e toque em **Cancelar**: sai um pentágono, porque é isso que o programa faz
    quando não recebe resposta.

11. **`referencia-pegue-a-bolinha`** de novo, agora tocando **■ Parar**: a página diz "parado" e o desenho fica.

12. **Tela bloqueada**: com algum programa rodando (o `ideia-relogio_animado` é bom para isso), bloqueie o iPad por uns
    10 segundos e desbloqueie. O programa continuou rodando no servidor; a página deve voltar a acompanhar sozinha, talvez
    mostrando "reconectando…" por um instante.

13. **Reduzir movimento**: ligue em Ajustes > Acessibilidade > Movimento, recarregue a página e rode
    `referencia-espiral`. O desenho aparece quase de uma vez.

14. **Girar o iPad** com qualquer programa: a área de desenho cabe inteira na tela, sem rolagem para os lados.

## Se algo der errado

Anote o número do item, o modelo do aparelho, a versão do sistema e do navegador, o que você viu (uma foto da tela ajuda
muito) e o que a página mostra ao lado dos botões. O terminal onde o servidor está rodando mostra os pedidos que chegaram,
o que ajuda a saber se o problema é na página ou no servidor. Com isso, abra uma issue no GitHub.

## Coisas que parecem defeito, mas não são

Todas funcionam do mesmo jeito no turtle de verdade:

- sem `listen()` no programa, as teclas e os botões de seta não fazem nada;
- `ondrag` só funciona se o toque começa em cima da tartaruga;
- `goto` com a caneta abaixada desenha uma linha até o ponto.

## Resultado do último teste

Em outubro de 2026, num iPad 7ª geração com iOS 18.7.4 e Safari, com o servidor num Mac: todos os itens funcionaram depois
das correções do [relatório do teste no iPad](docs/historia/RELATORIO-IPAD.md).
