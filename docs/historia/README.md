# Como o turtleweb foi feito

Esta pasta guarda o registro do projeto, do pedido inicial até o teste no iPad. Não é preciso ler nada daqui para usar a
biblioteca, mas ajuda a entender por que ela é do jeito que é.

O turtleweb foi construído em etapas (marcos), com um agente de programação (Claude Code) trabalhando a partir de uma
especificação e de decisões tomadas por uma pessoa entre uma etapa e outra.

| Arquivo | O que tem |
|---|---|
| [SPEC.md](SPEC.md) | a especificação: o problema, o que conta como pronto, o formato da lista de comandos, como medir |
| [PESQUISA.md](PESQUISA.md) | o que já existia (Skulpt, Brython, Pyodide, ColabTurtle e outros) e o teste que mostrou que trocar só o Tk funcionava |
| [DECISOES.md](DECISOES.md) | as decisões tomadas depois da pesquisa |
| `RELATORIO-M0.md` a `RELATORIO-M6.md` | o relatório de cada etapa: o que foi feito, o que passou, o que surpreendeu |
| [RELATORIO-FINAL.md](RELATORIO-FINAL.md) | o resumo de todas as etapas |
| [RELATORIO-IPAD.md](RELATORIO-IPAD.md) | os problemas achados no iPad e como foram corrigidos |
| [PROGRESSO.md](PROGRESSO.md), [AMBIENTE.md](AMBIENTE.md), [COMANDOS.md](COMANDOS.md) | anotações de trabalho: andamento, ambiente de desenvolvimento, quais comandos do turtle mais aparecem |
| `prompts/`, `setup/` | as instruções de cada etapa e o script que preparou o ambiente na nuvem |

Os textos são do momento em que foram escritos: alguns caminhos citados (como a pasta `experimentos/`) não existem mais.
