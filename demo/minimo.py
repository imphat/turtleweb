"""O menor app possível com o turtleweb: uma página com um botão que roda desenho.py.

    pip install flask
    python demo/minimo.py        e abra http://127.0.0.1:5000
"""
import os
import sys

from flask import Flask, jsonify

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))  # dispensável se o turtleweb estiver instalado

from turtleweb import Hub, Session  # noqa: E402
from turtleweb.flask_blueprint import create_blueprint  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
hub = Hub()
app.register_blueprint(create_blueprint(hub), url_prefix="/turtleweb")

PAGINA = """<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<button id="rodar">Desenhar</button>
<div id="area"></div>
<script src="/turtleweb/turtleweb.js"></script>
<script>
  const tw = TurtleWeb.mount(document.getElementById("area"), {base: "/turtleweb"});
  document.getElementById("rodar").onclick = async () => {
    const resp = await fetch("/rodar", {method: "POST"});
    tw.attach((await resp.json()).sid);
  };
</script>
"""


@app.get("/")
def pagina():
    return PAGINA


@app.post("/rodar")
def rodar():
    session = hub.add(Session())
    session.start(os.path.join(AQUI, "desenho.py"), cwd=AQUI)
    return jsonify(sid=session.sid)


if __name__ == "__main__":
    app.run(threaded=True)
