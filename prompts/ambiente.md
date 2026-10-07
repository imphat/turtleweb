Só verifique o ambiente. Não escreva código do projeto e não faça mais nada além disto:

1. Mostre a versão do Python (`python3 --version`) e do pip.
2. Teste `import tkinter` e, sob `xvfb-run`, crie uma janela `turtle` mínima (`turtle.Turtle().forward(10)`) e diga se funcionou.
3. Abra um Chromium sem janela com o Playwright, carregue `data:text/html,<canvas id=c></canvas>`, desenhe um retângulo vermelho no
   canvas e leia a cor de um pixel pelo JavaScript.
4. Teste a rede: `pip download` de um pacote pequeno funciona? `apt-get` funciona? O download do navegador do Playwright
   funcionou (ou qual domínio foi bloqueado)?
5. Diga se é possível abrir um servidor em `127.0.0.1` numa porta e acessá-lo pelo navegador do item 3.
6. Escreva o resultado de cada item (funcionou, falhou, e a mensagem de erro) em `AMBIENTE.md` e abra um pull request só com esse arquivo.
Pare depois disso.
