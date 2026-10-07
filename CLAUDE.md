# turtleweb: regras de trabalho

Projeto: uma biblioteca que faz o `import turtle` de um programa Python desenhar **dentro do navegador**, com o Python rodando no
servidor. Leia `SPEC.md` inteiro antes de qualquer ação. Ele manda; este arquivo só diz como trabalhar.

## Ambiente (verificado em 2026-10-06; o resumo está em `AMBIENTE.md` se o João o mesclou)
- **Python:** o `python3` padrão é o 3.13 e **não tem Tkinter**. Use **`~/.venvs/turtleweb/bin/python`** (Python 3.12, com Tkinter,
  pytest, flask e playwright instalados pelo script de configuração). Se esse ambiente não existir, crie com
  `python3.12 -m venv ~/.venvs/turtleweb && ~/.venvs/turtleweb/bin/pip install pytest flask playwright`.
- **Tela virtual:** rode o que abre janela do Tk com `xvfb-run -a <comando>`.
- **Chromium sem janela:** já existe em `/opt/pw-browsers`; o caminho está em `~/.chromium-path` (ou `find /opt/pw-browsers -name chrome`).
  O Playwright Python **não consegue baixar navegador** (o `cdn.playwright.dev` dá 403): use
  `p.chromium.launch(executable_path=<caminho>)`. Não rode `playwright install`.
- **Rede:** `pip` e `apt` funcionam; servidor em `127.0.0.1` funciona; o resto da internet pode estar bloqueado.
- A biblioteca precisa funcionar no Python **3.10 ou mais novo** (o Raspberry traz o 3.11), então não use sintaxe do 3.12 ou 3.13.

## Como trabalhar aqui
- **Um marco por sessão** (o prompt diz qual). Ao terminar: escreva `RELATORIO-Mx.md`, abra o pull request e **pare**.
- Código e identificadores em inglês; comentários curtos e só onde a razão não é óbvia; textos para pessoas (relatórios,
  documentação, mensagens de erro que a criança poderia ver) em **português do Brasil**.
- **Testes primeiro no que dá para testar sem navegador**: lista de comandos contra `corpus/*.esperado.json`. Navegador sem
  janela (Playwright + Chromium) só para fumaça e para a interação.
- **Nunca abra uma janela do Tk de verdade nos testes** sem `xvfb`; se não houver tela virtual, pule esse teste e registre.
- Não leia nem grave segredos (`.env`, chaves). A biblioteca não faz chamadas de rede para fora.
- Não mexa no que o João não pediu. Ideias fora do escopo vão para `IDEIAS.md`.
- Seja econômico: leia só o necessário, rode só os testes do que mudou, e a suíte inteira uma vez no fim do marco.
- Se travar (3 tentativas diferentes sem passar), pare, escreva o que tentou e abra o pull request como incompleto.

## Estrutura sugerida (ajuste na Etapa 0/M1 e registre o motivo)
```
turtleweb/           pacote Python (o módulo que substitui o Tk; o canal; o blueprint de exemplo)
turtleweb/static/    turtleweb.js (sem framework, sem CDN)
demo/                servidor de demonstração (Flask) e a página
tests/               pytest (lista de comandos, ciclo de vida, interação) e tests/browser (Playwright)
corpus/              programas e listas esperadas (já vêm no pacote; não editar os .esperado.json sem avisar o João)
docs/                contrato.md, INTEGRACAO.md, TESTE-IPAD.md
```

## Relatório de marco (`RELATORIO-Mx.md`), curto
1. O que foi entregue (e o que ficou de fora). 2. Resultado do aceite, item a item (passou, falhou, pulado e por quê).
3. O que travou ou surpreendeu. 4. Estimativa de esforço do marco (passos e execuções de teste). 5. Recomendação: continuar,
cortar escopo ou parar. 6. O que o João precisa decidir.
