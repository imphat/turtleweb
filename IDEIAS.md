# Ideias para quem quiser contribuir

Coisas que ficaram de fora até agora, mais ou menos em ordem de quanto ajudariam. Se você quiser pegar alguma, abra uma
issue para a gente conversar antes.

- **Imagens na tartaruga e no fundo.** `register_shape("gato.gif")` e `bgpic("praia.gif")` ainda não funcionam. O Tk falso
  precisaria servir a imagem para a página, e o `turtleweb.js` desenhá-la no canvas.
- **Medir texto no navegador.** Hoje o tamanho de um texto escrito com `write` é estimado no servidor, então
  `write(..., move=True)` pode deixar a tartaruga alguns pixels fora do lugar. A página poderia medir e devolver.
- **Servidores de exemplo para FastAPI e Django.** O blueprint de Flask tem cinco rotas finas sobre a `Session`; um
  equivalente para outros frameworks deixaria a integração mais fácil para mais gente.
- **Desenho incremental.** A página redesenha todos os itens a cada quadro. Com 3 mil carimbos isso leva uns 8 ms, o que
  ainda é tranquilo; acima de 20 mil itens valeria guardar numa camada o que não muda.
- **Voltar a acompanhar depois de recarregar a página.** Se a pessoa recarrega a página no meio de uma execução, ela perde
  o fio. Dava para guardar o id da execução no `sessionStorage`.
- **WebSocket como alternativa** aos server-sent events, para servidores ou proxies que seguram as respostas em buffer.
- **Testar no Windows.** Nada no código depende do sistema, mas ninguém rodou por lá ainda.
