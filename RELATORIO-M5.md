# RELATÓRIO M5 (endurecimento)

## 1. O que foi entregue
- **Taxa de envio:** no máximo ~60 lotes por segundo (`MIN_INTERVAL`), com um temporizador que envia o resto; pontos que bloqueiam
  (esperar evento, `textinput`, pausas ≥ 16 ms da animação, fim) enviam na hora. Só o último `coords` de cada item vai no lote.
- **Memória do servidor:** o histórico de uma execução vira um retrato do desenho a cada 3000 eventos (`reset` no `ops`); ids do SSE
  continuam absolutos, então `Last-Event-ID` e páginas atrasadas funcionam. Mensagens da página enviadas antes de o programa conectar ficam na fila.
- **Página:** retina (canvas com `devicePixelRatio`), **reduzir movimento** (`prefers-reduced-motion` começa no modo instantâneo; o
  desenho não muda), botão "Mais rápido" (÷8), "reconectando…" / "sem conexão com o servidor", operações desconhecidas ignoradas.
- Sinal (código negativo, ex.: o app matou o processo) conta como "parado", não "erro".
- Testes: `tests/browser/test_m5.py` (30, inclui os 21 interativos no navegador) e `tests/test_compactacao.py`.
- **Ficou de fora:** redesenho incremental do canvas (cada quadro redesenha tudo; 3000 carimbos = ~8 ms, 4000 linhas = ~2,4 ms; ver `IDEIAS.md`).

## 2. Aceite (seção 7, itens 3 a 5, corpus inteiro)
| Item | Resultado |
|---|---|
| 3. Fumaça no navegador, corpus inteiro | **passou** (35 determinísticos + 21 interativos; 4 que precisam de stdin/arquivo terminam com erro de leitura, como sem entrada) |
| 4. Interativos com eventos simulados | **passou** (M4) |
| 5. Desempenho: espiral e carimbos tão rápidos quanto o Tk, com opção de acelerar | **passou**: espiral 13,0 s (Tk real: 13,6 s no M0); com "Mais rápido" < 6 s; carimbos 1,4 s; com reduzir movimento < 5 s; desenho idêntico nos três modos |

## 3. O que surpreendeu
- Mesmo com `speed(0)`, o turtle de verdade espera 10 ms por comando (`delay`); um programa com 9000 comandos leva ~1 min no Tk e no turtleweb. O turtleweb preserva isso (decisão 2); "Mais rápido" resolve.
- Um teste inicial de carimbos precisou de `tracer(0)` por esse motivo.

## 4. Esforço
~25 passos; ~8 execuções de teste.

## 5. Recomendação
Continuar para o M6.

## 6. Decisões do João
Nenhuma nova.
