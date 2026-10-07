# Ideias fora do escopo

- Redesenho incremental do canvas (camada em cache para itens que não mudam) se algum programa passar de ~20 mil itens.
- Guardar o `sid` em `sessionStorage` para a página recarregada voltar a seguir a execução.
- Medir texto no navegador e devolver ao Python (hoje `bbox` de texto é estimado; afeta `write(move=True)` e `align`).
- `register_shape` / `bgpic` com imagens (P2).
- WebSocket como alternativa ao SSE se algum proxy do app bufferizar eventos.
