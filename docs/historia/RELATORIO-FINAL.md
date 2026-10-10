# RELATÓRIO FINAL (M1 a M6)

## 1. O que ficou pronto
Tudo o que a seção 9 do `SPEC.md` pede, M1 a M6, no ramo `turtleweb-m1-m6` (um commit por marco). O `turtle` da biblioteca padrão roda
**sem alteração** sobre um `tkinter` falso; cada operação vai por um socket em 127.0.0.1 ao servidor e daí à página (SSE + POST).
Nada de Tkinter no servidor; Python 3.10, 3.11 e 3.13 testados como filho.

**O que não ficou pronto / não foi verificado**
- **Safari/iPad:** não testado (é seu; `TESTE-IPAD.md`). O toque foi simulado no Chromium.
- O app real não foi alterado; a integração foi provada com um "app" mínimo e com o servidor de demonstração.
- `bbox` de texto é estimado (afeta `write(move=True)` e alinhamentos finos); imagens (`register_shape`, `bgpic`) fora (P2).
- Modificadores (Ctrl/Alt/Meta) não são enviados ao programa.

## 2. Aceite, item a item
| Seção 7 / 9 | Resultado |
|---|---|
| M1: quadrado e círculo no navegador por programa real; `referencia-quadrado` idêntico | **passou** |
| 7.1 Determinísticos: lista idêntica (35/35) | **passou** (Pythons 3.10, 3.11, 3.13; filho sem Tkinter) |
| 7.2 Geometria × Tk real (36 programas) | **passou**: itens, coordenadas (±0,5 px) e cores idênticos |
| 7.3 Fumaça no navegador (corpus inteiro: 35 + 21) | **passou** |
| 7.4 Interativos com eventos simulados (21/21) | **passou** |
| 7.5 Desempenho: espiral/carimbos tão rápidos quanto o Tk, com "Mais rápido" | **passou** (espiral 13,0 s × 13,6 s no Tk; < 6 s acelerada) |
| 7.6 Safari/iPad | **pendente: do João** |
| M3: seção 6 (termina sozinho, `done`, ■ Parar, erro, `textinput`/`numinput`, nova execução) | **passou** |
| M4: P1 + `referencia-pegue-a-bolinha` no Chromium | **passou** |
| M5: retina, reduzir movimento, muitos carimbos, erros | **passou** |
| M6: `pip install .`, `INTEGRACAO.md`, `TESTE-IPAD.md` | **passou** |
| Suíte inteira | **234 passed** (`cd tests && python -m pytest -q`, ~2 min) |

Nenhuma regra de parada foi acionada.

## 3. Esforço por marco (passos de ferramenta; execuções de teste)
| Marco | Previsto no PESQUISA | Real |
|---|---|---|
| M1 | 50–80; 15–25 | ~55; ~12 |
| M2 | 40–70; 15–25 | ~25; ~10 |
| M3 | 30–60; 10–20 | ~12; 3 |
| M4 | 60–100; 20–35 | ~30; ~12 |
| M5 | 40–80; 15–30 | ~25; ~8 |
| M6 | 25–45; 5–10 | ~25; ~8 |
Menos que o previsto porque o `turtle` real já faz a lógica e o protótipo do M0 serviu de base.

## 4. Decisões que dependem do João
1. **Cor `green`:** o Tk 8.6.14 real responde `#008000` (não `#00ff00`; `gray`, `maroon`, `purple` também são os do CSS; `lime` é `#00ff00`).
   A tabela embutida segue o Tk real (`DECISOES.md`, item 5). Para o valor antigo do X11, troque 4 linhas de `turtleweb/_colors.py`.
2. **Fechar a janela no meio do desenho** termina em silêncio (código 0), em vez do traceback `turtle.Terminator` do turtle de verdade.
3. **`numinput`** aceita vírgula decimal (`12,5`) e mostra mensagens em português; o Tk aceitaria só ponto.
4. **Autenticação:** o blueprint não tem login; o app precisa proteger as rotas (`INTEGRACAO.md`, seção 6).
5. Merge: o ramo tem todos os marcos; o pull request está pronto para revisão.

## 5. Documentos
`INTEGRACAO.md`, `TESTE-IPAD.md`, `docs/contrato.md`, `DECISOES.md`, `IDEIAS.md`, `RELATORIO-M1.md` a `RELATORIO-M6.md`, `PROGRESSO.md`.
