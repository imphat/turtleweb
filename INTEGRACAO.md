# Guia de integração

Este guia é para quem já tem um app que roda programas Python de alunos e quer que o `turtle` desenhe no navegador em vez
de abrir uma janela no servidor. Dá para fazer numa tarde. Se você está começando do zero, olhe primeiro o
`demo/minimo.py`: ele já faz tudo isto num arquivo só.

## A ideia em uma frase

Você continua rodando o programa do aluno do mesmo jeito que roda hoje, só que com algumas variáveis de ambiente a mais.
Elas fazem o Python do aluno carregar o turtleweb antes de qualquer coisa, e o turtleweb manda o desenho para o seu
servidor, que manda para a página.

O que **não** muda:

- o programa do aluno: continua `import turtle`, nem uma linha diferente;
- o `input()` e o `print()`: o turtleweb não usa a entrada nem a saída do programa (ele conversa por um socket local), então
  o seu app continua lendo e escrevendo nelas como sempre;
- o botão de parar: matar o processo continua funcionando, e a página passa a mostrar "parado";
- a lista de comandos (`PP_TURTLE_LOG`), se você usa: mesmo arquivo, mesmo formato.

O que muda: o servidor não precisa mais de Tkinter nem de tela. Pode desinstalar o `python3-tk` e o `xvfb`, se estavam lá
só por causa do turtle.

## 1. Instalar

No mesmo ambiente Python do seu app:

```
pip install git+https://github.com/imphat/turtleweb
pip install flask        # só se for usar o blueprint pronto
```

Precisa do Python 3.10 ou mais novo. O turtleweb não tem dependências.

## 2. Rodar o programa do aluno com o ambiente do turtleweb

Em algum lugar o seu app faz algo parecido com isto:

```python
proc = subprocess.Popen([sys.executable, "-u", programa], cwd=pasta, env=meu_env,
                        stdin=..., stdout=..., stderr=...)
```

Com o turtleweb fica assim:

```python
from turtleweb import Session
from turtleweb.session import child_env

session = Session()                                   # abre um socket em 127.0.0.1, numa porta livre
env = child_env(session, meu_env, log=caminho_do_log) # log= é opcional (é o PP_TURTLE_LOG)
proc = subprocess.Popen([sys.executable, "-u", programa], cwd=pasta, env=env,
                        stdin=..., stdout=..., stderr=...)   # igualzinho a antes
session.attach(proc)                                  # a sessão fica sabendo quando o programa termina
```

A `Session` representa uma execução: ela recebe o desenho do programa, guarda o que a página precisa e repassa para o
programa os cliques e as teclas que vêm da página.

O `child_env` só **acrescenta** variáveis ao ambiente que você passou:

| Variável | Para quê |
|---|---|
| `PYTHONPATH` | ganha, no começo, a pasta do `sitecustomize` do turtleweb |
| `TURTLEWEB`, `TURTLEWEB_PORT`, `TURTLEWEB_TOKEN` | ligam o turtleweb e dizem onde está o servidor (o token impede que outro processo se conecte) |
| `TURTLEWEB_PATH` | onde achar o turtleweb se ele não estiver instalado no Python do aluno |
| `PYTHONUTF8` | texto em UTF-8 em qualquer sistema |
| `PP_TURTLE_LOG` | só se você passar `log=` |

### O que acontece dentro do processo do aluno

Quando o Python começa, ele executa automaticamente um arquivo chamado `sitecustomize`, se achar um no caminho. O
turtleweb usa isso: o dele chama `turtleweb.install()`, que coloca um `tkinter` falso no lugar do verdadeiro e se conecta
ao servidor. Quando o programa faz `import turtle`, o turtle da biblioteca padrão é carregado normalmente e passa a
desenhar no Tk falso, sem saber de nada.

Algumas situações que você pode encontrar:

- **Já existe um `sitecustomize` no sistema** (algumas distribuições Linux têm): o do turtleweb executa o outro logo depois.
- **O aluno usa outro Python** que não o do app: instale o turtleweb nele também, ou deixe como está, porque o
  `TURTLEWEB_PATH` aponta para a cópia do servidor.
- **O programa não usa `turtle`**: nada muda para ele.
- **Prefere não usar `sitecustomize`**: rode o programa com `python -m turtleweb programa.py`, ou ponha
  `import turtleweb; turtleweb.install()` antes do `import turtle`.

## 3. Mostrar o desenho na página

### Com Flask

O blueprint já traz as rotas:

```python
from turtleweb import Hub
from turtleweb.flask_blueprint import create_blueprint

hub = Hub()                    # guarda as execuções, cada uma com um id
app.register_blueprint(create_blueprint(hub), url_prefix="/turtleweb")
```

Depois de criar a `Session` (passo 2), registre-a e devolva o id para a página:

```python
hub.add(session)
return {"sid": session.sid}
```

As rotas, relativas ao prefixo:

| Rota | O que faz |
|---|---|
| `GET /turtleweb.js` | o script da página |
| `GET /events/<sid>` | o desenho e os avisos, em tempo real (server-sent events) |
| `POST /input/<sid>` | cliques, teclas e respostas da página para o programa |
| `POST /stop/<sid>` | para o programa |
| `GET /status/<sid>` | o estado atual (`running`, `waiting`, `ended`...) |

### Na página

```html
<div id="area"></div>
<script src="/turtleweb/turtleweb.js"></script>
<script>
  const tw = TurtleWeb.mount(document.getElementById("area"), {
    base: "/turtleweb",
    onstate: (estado, codigo) => { /* opcional: atualizar a sua interface */ },
  });

  // quando o servidor iniciar uma execução:
  tw.attach(sid);
</script>
```

O `mount` cria a área de desenho, a linha de estado e os botões "Fechar a janela" e "Mais rápido". Cada `attach` começa
uma execução nova e limpa a tela.

Opções do `mount`:

| Opção | Padrão | Para quê |
|---|---|---|
| `base` | `""` | onde o blueprint foi registrado |
| `onstate(estado, codigo)` | | avisa quando o programa começa, espera, termina, dá erro, é parado ou a conexão cai (`"offline"`) |
| `onoutput(fluxo, texto)` | | recebe a saída do programa, se o servidor repassar (o `Session.start` repassa; o `attach` com `Popen` próprio não) |
| `pad` | só em tela de toque | botões de seta na tela, quando o programa chama `listen()` |
| `keyboardButton` | só em tela de toque | botão "⌨️ Teclado", que abre o teclado do aparelho |
| `reduceMotion` | segue o aparelho | começa sem animação para quem ativou "reduzir movimento" |
| `title` | `true` | `false` para o programa não mudar o título da aba |

### Sem Flask

Use a `Session` direto. `session.iter_events(inicio)` gera os eventos para você mandar como server-sent events,
`session.send(mensagem)` entrega uma mensagem da página ao programa e `session.stop()` para tudo. O formato das mensagens
está em [docs/contrato.md](docs/contrato.md). A rota de eventos deve aceitar o cabeçalho `Last-Event-ID` e o parâmetro
`?last=`, que a página usa para retomar depois de uma queda de conexão (no iPad isso acontece toda vez que a tela
bloqueia).

## 4. Parar o programa

Se o seu app já mata o processo, continue assim: a página mostra "parado". Se preferir, chame `session.stop()`, que faz o
mesmo.

## 5. A lista de comandos (`PP_TURTLE_LOG`)

Se o seu app usa esse arquivo para conferir exercícios, nada muda. Cada linha é um comando que o programa chamou,
em JSON, com os apelidos trocados pelo nome principal (`fd` vira `forward`, `pu` vira `penup`), números com três casas e
texto cortado em 30 caracteres. Só entram os comandos chamados pelo próprio programa: o `circle` aparece, os passinhos que
ele faz por dentro não. Comandos dentro de uma função de tecla, clique ou timer entram normalmente.

## 6. Colocando no ar

- **Threads**: cada página aberta mantém uma conexão de eventos aberta. Use um servidor com threads: o do Flask com
  `threaded=True`, o `waitress`, ou `gunicorn -k gthread --threads 16`.
- **Um processo só**: as execuções ficam na memória do processo que as criou. Com vários processos, a página pode cair num
  que não conhece a execução.
- **Atrás do nginx**: desligue o buffer nas rotas de eventos (`proxy_buffering off;`), senão o desenho chega aos pedaços.
- **Segurança**: o blueprint não tem login. Os ids são aleatórios, mas isso não é autenticação; se o servidor é acessível
  por outras pessoas, proteja as rotas com o login do seu app. O canal entre servidor e programa só aceita conexões locais
  e exige o token.
- **Memória**: o `Hub` guarda as últimas 20 execuções (`Hub(keep=N)` para mudar), e uma execução longa não acumula
  histórico sem fim: de tempos em tempos ele vira um retrato do desenho atual.

## 7. Velocidade

Por padrão a tartaruga anda na mesma velocidade do Tk, porque é isso que o aluno espera ver e é isso que o professor
explicou. Quem tem pressa aperta **Mais rápido** (oito vezes mais rápido, mesmo desenho). Quem ativou "reduzir movimento"
no aparelho já começa sem animação.

## 8. Roteiro da tarde

1. Instale e rode os testes (`cd tests && python -m pytest -q`).
2. Troque o `Popen` como no passo 2 e registre o blueprint como no passo 3.
3. Rode `corpus/referencia-quadrado.py`: o quadrado aparece na página, e o `PP_TURTLE_LOG` sai igual ao
   `referencia-quadrado.esperado.json`.
4. Teste um programa com teclado (`referencia-controle-setas`), um com pergunta (`ideia-poligono_medida`) e o botão de parar.
5. Siga o [roteiro do iPad](TESTE-IPAD.md) num aparelho de verdade.
