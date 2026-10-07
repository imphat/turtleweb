# Pacote de partida do turtleweb

Esta pasta é o ponto de partida do projeto **turtleweb** (o turtle no navegador), feito na nuvem do Claude e depois plugado no app.
Foi gerada por `tools/gerar_pacote_turtleweb.py` no app (rode de novo se as lições ou as ideias mudarem).

| Arquivo | Para quê |
|---|---|
| `SPEC.md` | a especificação: meta, pesquisa, arquitetura, formato dos comandos, ciclo de vida, aceite, marcos e paradas |
| `CLAUDE.md` | regras de trabalho do agente no repositório novo |
| `COMANDOS.md` | os comandos do turtle por frequência de uso nos programas do app |
| `corpus/` | os programas de teste (`index.json` diz o tipo de cada um) e a lista de comandos esperada dos determinísticos |
| `setup/setup-ambiente.sh` | script de configuração do ambiente da nuvem (Xvfb, Tkinter, Playwright, Chromium) |
| `prompts/` | o texto para colar em cada sessão: `ambiente.md` (teste do ambiente), `M0.md` a `M6.md` |

## Como usar (resumo; o passo a passo completo foi dado na conversa)
1. Copie o **conteúdo** desta pasta para a raiz do clone do repositório `turtleweb`, faça commit e push.
2. No ambiente da nuvem, cole `setup/setup-ambiente.sh` como script de configuração.
3. Rode uma sessão com `prompts/ambiente.md` e leia o `AMBIENTE.md` do pull request.
4. Rode a sessão do **M0** (modelo mais forte); leia o `PESQUISA.md`; decida.
5. Rode **um marco por sessão**, na ordem, mesclando o pull request de cada um antes de abrir o próximo.
