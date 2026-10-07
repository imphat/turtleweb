# INTEGRACAO: plugar o turtleweb no app em uma tarde

O programa da criança **não muda uma linha**: continua `import turtle`. O app só (1) instala a biblioteca, (2) muda o
**ambiente** do processo filho e (3) serve a página.

## 0. O que muda para o app
| Hoje | Com o turtleweb |
|---|---|
| o filho abre uma janela do Tk no computador do app | o filho desenha numa página no navegador |
| precisa de `python3-tk` (e de tela) | **não** precisa de Tkinter nem de tela no servidor |
| `PP_TURTLE_LOG` grava a lista de comandos | **igual**: mesmo arquivo, mesmo formato (SPEC seção 5) |
| `input()`/`print()` pelo stdin/stdout do filho | **igual**: o turtleweb não toca neles (o canal é um socket em 127.0.0.1) |
| ■ Parar mata o processo | **igual**; a página passa a mostrar "parado" |

## 1. Instalar (no mesmo ambiente do app)
```
pip install /caminho/para/turtleweb        # ou: pip install turtleweb-0.1.0-py3-none-any.whl
pip install flask                          # se o app usa Flask (o blueprint de exemplo precisa)
```
Python 3.10 ou mais novo. Sem outras dependências.

## 2. Trocar o ambiente do processo filho
Onde o app hoje faz `subprocess.Popen([sys.executable, "-u", programa], cwd=pasta, env=..., ...)`:

```python
from turtleweb import Session
from turtleweb.session import child_env

session = Session()                                   # abre o socket em 127.0.0.1:<porta livre>
env = child_env(session, base_env, log=caminho_do_PP_TURTLE_LOG)   # base_env = o env que o app já usa
proc = subprocess.Popen([sys.executable, "-u", programa], cwd=pasta, env=env,
                        stdin=..., stdout=..., stderr=...)           # exatamente como hoje
session.attach(proc)                                  # para o código de saída e o ■ Parar
```
`child_env` só acrescenta variáveis: `PYTHONPATH` (com a pasta do `sitecustomize` do turtleweb, **antes** dos outros itens), `PYTHONUTF8=1`,
`TURTLEWEB=1`, `TURTLEWEB_PORT`, `TURTLEWEB_TOKEN`, `TURTLEWEB_PATH` e, se você passar `log=`, `PP_TURTLE_LOG`.

O que acontece no filho: o Python roda o `sitecustomize`, que chama `turtleweb.install()` **antes** de qualquer `import turtle`;
essa função põe um `tkinter` falso em `sys.modules`, conecta ao socket e prepara a lista de comandos. O `turtle` da biblioteca
padrão roda **sem alteração**. Não existe um `turtle.py` próprio.

- Quer chamar à mão (sem sitecustomize)? `import turtleweb; turtleweb.install()` na primeira linha, ou `python -m turtleweb programa.py`.
- Já existe um `sitecustomize` no sistema? O do turtleweb o executa em seguida.
- Interpretador diferente do do app? Instale o turtleweb nele, ou deixe `TURTLEWEB_PATH` (já posto por `child_env`) apontar para a cópia do servidor.
- Programa que não usa `turtle`: nada muda (só conecta e avisa que terminou).

## 3. Servir a página
Com Flask (blueprint de exemplo):
```python
from turtleweb.flask_blueprint import create_blueprint
from turtleweb import Hub

hub = Hub()                                  # guarda as execuções por id
app.register_blueprint(create_blueprint(hub), url_prefix="/turtleweb")
...
hub.add(session)                             # depois de criar a Session no passo 2
return {"sid": session.sid}                  # a página usa este id
```
Rotas (relativas ao prefixo): `GET /turtleweb.js`, `GET /events/<sid>` (SSE), `POST /input/<sid>`, `POST /stop/<sid>`, `GET /status/<sid>`.
Outro framework (FastAPI, Django...)? Use só `Session`: `session.iter_events(start)` gera os eventos SSE,
`session.send(msg)` entrega a mensagem da página ao programa, `session.stop()` é o ■ Parar. O contrato está em `docs/contrato.md`.

Na página do app:
```html
<div id="area"></div>
<script src="/turtleweb/turtleweb.js"></script>
<script>
  const tw = TurtleWeb.mount(document.getElementById("area"), {
    base: "/turtleweb",
    onstate: (estado, codigo) => {},        // "running", "waiting", "ended", "error", "stopped", "offline"
    onoutput: (fluxo, texto) => {},         // só se o servidor repassar stdout/stderr (Session.start faz isso)
  });
  // depois de o servidor iniciar uma execução:
  tw.attach(sid);                           // chamar de novo a cada execução nova: a página é limpa
</script>
```
Opções de `mount`: `pad: true|false` (botões de seta; padrão: só em tela de toque e só depois de `listen()`),
`reduceMotion` (padrão: segue o aparelho), `title: false` (não mudar o título da aba).

## 4. O ■ Parar
Pode continuar matando o processo como hoje: código de saída negativo vira "parado" na página. Se preferir, chame
`session.stop()` (termina o processo e marca "parado").

## 5. A lista de comandos (`PP_TURTLE_LOG`) continua igual
Mesmo arquivo, uma linha JSON por comando de nível mais alto, apelidos viram o nome canônico, números com 3 casas, texto até 30
caracteres. Os 35 programas determinísticos do `corpus/` dão listas **idênticas** às esperadas (`tests/test_comandos.py`), nos
Pythons 3.10, 3.11 e 3.13 e **sem Tkinter**. Só comandos chamados pelo programa entram; os chamados por dentro (ex.: o `forward` dentro de
`circle`) não, e os chamados dentro de um callback de tecla/clique/timer entram como comandos próprios.

## 6. Implantação (Raspberry Pi etc.)
- **SSE precisa de uma thread por página aberta**: use o servidor de desenvolvimento com `threaded=True`, `waitress` ou `gunicorn -k gthread --threads 16`.
- **Um processo só** (ou afinidade de sessão): as execuções ficam na memória do processo que as criou.
- Atrás de nginx: `proxy_buffering off;` nas rotas `/turtleweb/events/` (o blueprint já manda `X-Accel-Buffering: no`).
- O servidor e o filho conversam só por 127.0.0.1; o socket exige o token de `TURTLEWEB_TOKEN`.
- **O blueprint não tem login.** Proteja `/events`, `/input` e `/stop` com a autenticação do app (os ids são aleatórios, mas isso não é autenticação).
- Execuções antigas: o `Hub` guarda as últimas 20 (`Hub(keep=N)`); o histórico de cada uma é limitado (vira um retrato a cada 3000 eventos).

## 7. Velocidade
Por padrão a animação dura o mesmo que no Tk (a espiral de referência leva ~13 s). A página tem o botão **Mais rápido** (÷8, mesmo
desenho). Aparelhos com "Reduzir movimento" ligado começam em modo instantâneo.

## 8. Checklist de uma tarde
1. `pip install` e rodar `tests` (`cd tests && python -m pytest -q`; os testes de geometria e de navegador pulam sozinhos sem `xvfb`/Chromium).
2. Passo 2 no lugar onde o app inicia o processo; passo 3 para a rota e a página.
3. Abrir `referencia-quadrado`: quadrado na página, `PP_TURTLE_LOG` igual ao esperado.
4. `referencia-controle-setas` (teclas e botões de seta), `ideia-poligono_medida` (`textinput`), ■ Parar.
5. `TESTE-IPAD.md` no aparelho de verdade.
