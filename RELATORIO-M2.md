# RELATÓRIO M2 (comandos P0)

## 1. O que foi entregue
Os comandos P0 já funcionam porque a lógica é a do `turtle` real; o trabalho do M2 foi **provar a fidelidade**:
- `tests/geometria_dump.py` + `tests/test_geometria.py`: roda o programa no Tk de verdade (xvfb) e no canvas falso e compara
  item a item (tipo, coordenadas ±0,5 px, cores, largura, texto) — 35 determinísticos + `tests/programs/geo_p0.py`, que usa
  todos os P0 (`Screen` com `setup/title/colormode/bgcolor/tracer/update`, `color` com tupla e hex, `circle` com extent, `dot`, `write` com `font=` e `align`, `setx/sety/home`, `hideturtle/showturtle`, `clear`, `reset`, `speed`).
- `tests/browser/test_corpus.py`: fumaça no Chromium para os 35 determinísticos + cores de `referencia-bolinhas`.
- Teste de que nenhum método do Tk ficou sem implementar (`unknown` vazio) nos 36 programas.
- Ficou de fora: nada do P0.

## 2. Aceite
| Item | Resultado |
|---|---|
| Seção 7.1: lista de comandos idêntica nos 35 | **passou** |
| Seção 7.3: fumaça no navegador (abre, recebe eventos, canvas não vazio, cor dos pontos) | **passou** (35 + bolinhas) |
| Seção 7.2: geometria × Tk real | **passou**: 36/36 idênticos (tolerância 0,5 px) |

## 3. O que surpreendeu
Nada travou. O `bbox` de texto é estimado (afeta só `write(move=True)`/alinhamento); fora do corpus determinístico.
A comparação de geometria vale para o desenho enviado; como o navegador rasteriza (anti-aliasing, fontes), pixels não são idênticos.

## 4. Esforço
~25 passos; ~10 execuções de teste.

## 5. Recomendação
Continuar para o M3.

## 6. Decisões do João
Nenhuma nova.
