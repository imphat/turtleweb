# RELATÓRIO M0 (pesquisa), 2026-10-07

## 1. O que foi entregue
- `PESQUISA.md`: 13 candidatos avaliados nos 9 critérios da seção 3, com links, datas, o que foi verificado e o que não foi;
  teste de fogo; recomendação; riscos; estimativa por marco; decisões do João.
- `experimentos/m0_canvas_falso/`: protótipo **descartável** do canvas falso (não é a biblioteca) e o teste de fogo com Playwright.
- `AMBIENTE.md`: o que a rede bloqueou e como segui. `.gitignore` para `__pycache__`.
- **Ficou de fora** (de propósito): qualquer código da biblioteca; a lista de comandos da seção 5 (é do M1).

## 2. Aceite (seção 3)
| Item | Resultado |
|---|---|
| Procurar soluções existentes, com links e datas | **passou**: 13 candidatos; código lido de 11 pacotes (PyPI/npm) |
| Anotar sim/não/parcial por critério | **passou**: tabela no `PESQUISA.md` |
| Teste de fogo: quadrado e círculo no navegador com o `turtle` da biblioteca padrão e um canvas falso | **passou**: 13/13 verificações de cor no Chromium, com o filho em 3.10, 3.13 e 3.14, todos sem Tkinter |
| Recomendação pela regra de decisão | **passou**: nenhum projeto elegível chega a 80% → canvas falso |
| Riscos, estimativa por marco, decisões do João | **passou** |
| Não verificado | data do último commit do Skulpt (GitHub 429); Basthon (framagit bloqueado); turtles para PyScript e WebTigerPython (Python no navegador, fora do escopo); cadeia VNC completa (não montada) |

## 3. O que travou ou surpreendeu
- O `turtle` da biblioteca padrão rodou **sem nenhuma alteração** só com um `tkinter` falso, e funcionou de primeira em 3.10 a 3.14.
  O corpus inteiro não chamou nenhum método do Tk que o falso não tivesse.
- Outros dois pacotes já usam a mesma ideia (svg-turtle e ipyturtle3), e um gist de 2016 fez exatamente isto para a web.
- 3 programas do corpus usam `input()`: o canal da biblioteca **não pode** ser o stdin do filho.
- `green` no Tk ≠ `green` no CSS: as cores precisam ir como `#rrggbb`.
- A espiral leva ~13 s tanto no Tk real quanto no navegador, o que conflita com o "poucos segundos" da seção 7.
- A rede bloqueia `github.com` pelo `curl` e o `framagit.org`; o PyPI, o npm e a leitura de páginas pela ferramenta da web resolveram quase tudo.
- O `uv` instalou Python 3.10 e 3.14 sem problema, então dá para testar a versão mínima (3.10) de verdade.
- O programa `ideia-galeria_salva.py` grava `galeria.txt` na pasta em que roda. Na primeira rodada ele foi criado em `corpus/` e
  eu o apaguei; o `rodar_corpus.py` agora roda cada programa numa pasta temporária.

## 4. Esforço
Cerca de 70 passos (chamadas de ferramenta). Execuções de teste: teste de fogo no navegador 4 vezes (3.13, 3.10, 3.14 e a primeira
em 3.13), corpus pelo canvas falso 4 vezes, tempo da espiral e dos carimbos (Tk real × falso) 1 vez, rodadas diretas do `run.py` 7 vezes.

## 5. Recomendação
**Continuar**, pelo caminho do canvas falso. O risco principal (fidelidade) caiu muito: a lógica é a do turtle de verdade.

## 6. O que o João precisa decidir
Detalhes na última seção do `PESQUISA.md`:
1. Aprovar o canvas falso.
2. Velocidade × fidelidade (espiral de ~13 s).
3. `input()` nos programas: o stdin fica com o app?
4. Como o turtleweb entra no programa (`tkinter` falso no `PYTHONPATH` ou `turtle.py` próprio; recomendo o segundo).
5. Manter `experimentos/` até o M1 ou apagar já.
