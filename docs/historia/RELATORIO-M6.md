# RELATÓRIO M6 (pacote, integração, documentação)

## 1. O que foi entregue
- Pacote instalável (`pip install .`, `pyproject.toml`, Python ≥ 3.10, sem dependências; Flask é opcional), `python -m turtleweb programa.py`.
- `INTEGRACAO.md` (como o app troca o ambiente do processo filho e como o `PP_TURTLE_LOG` continua igual), `TESTE-IPAD.md`, `README.md`.
- `child_env` agora só coloca a pasta do `sitecustomize` no `PYTHONPATH`; a cópia do servidor entra em `TURTLEWEB_PATH`, usada só se o
  interpretador do filho não tiver o pacote (não polui o `site-packages` do filho).
- Correção achada ao rodar a suíte: fechar a janela cancela os timers pendentes (como o Tk) e não imprime `Terminator` (`tests/test_fechar.py`).
- `experimentos/` removida (decisão 6; segue no histórico do git); demo com `--host`.
- **Ficou de fora:** publicar no PyPI; testes em Safari/iPad (do João).

## 2. Aceite
| Item | Resultado |
|---|---|
| `pip install .` num ambiente limpo e uso sem o repositório no caminho | **passou** (`tests/test_instalacao.py`: filho em outro Python, lista idêntica) |
| Plugar no app trocando o módulo (`INTEGRACAO.md`) | **passou** em teste com um "app" mínimo; o app real do João não foi tocado |
| Todos os testes passam | **passou** (ver `RELATORIO-FINAL.md`) |

## 3. O que surpreendeu
Um teste ocasional (`ideia-relogio_animado`) mostrou que um timer podia disparar logo depois do `close`; corrigido.

## 4. Esforço
~25 passos; ~8 execuções de teste.

## 5. Recomendação
Pronto para o João integrar e testar no iPad.

## 6. Decisões do João
Ver `RELATORIO-FINAL.md`.
