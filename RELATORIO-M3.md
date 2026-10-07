# RELATÓRIO M3 (ciclo de vida, textinput/numinput)

## 1. O que foi entregue
- Estados da página: `conectando → rodando → esperando você fechar a janela → terminou / terminou com erro (código N) / parado`.
- Fechar a janela no meio do desenho: o turtle real imprimiria `turtle.Terminator`; o turtleweb encerra **em silêncio com código 0**
  (`excepthook` em `turtleweb/__init__.py`). Desvio consciente do turtle de verdade, para não assustar a criança.
- `textinput`/`numinput`: caixa na página, cancelar devolve `None`; `numinput` repete a pergunta com mensagem em português para
  texto que não é número e para valor fora de `minval`/`maxval`; aceita vírgula decimal (`12,5`), o que o Tk não aceitaria.
- Testes: `tests/browser/test_m3.py` (8 casos).
- **Ficou de fora:** reconectar a página depois de recarregar (o `sid` não é guardado; o SSE reconecta sozinho com `Last-Event-ID`).

## 2. Aceite (seção 6)
| Caso | Resultado |
|---|---|
| Termina sozinho: desenho fica, marcado "terminou" | **passou** |
| `done()` espera; botão fecha; código 0 | **passou** |
| ■ Parar: processo encerrado, "parado", desenho fica | **passou** |
| Erro no programa: traceback no stderr, desenho fica, estado de erro | **passou** |
| `textinput` e `numinput` (valor, inválido, faixa, cancelar) | **passou** |
| Nova execução limpa a página | **passou** |

## 3. O que travou ou surpreendeu
Nada. Um seletor de teste (`text=Fechar a janela`) casava com o texto de estado (corrigido no M1 com classes).

## 4. Esforço
~12 passos; 3 execuções de teste.

## 5. Recomendação
Continuar para o M4 (o maior).

## 6. Decisões do João
Fechar a janela no meio do desenho termina em silêncio (código 0), em vez de mostrar o traceback `Terminator`. Quer isso?
