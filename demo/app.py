"""Demo server: pick a program, run it, watch it draw.

    ~/.venvs/turtleweb/bin/python demo/app.py [--host 0.0.0.0] [--port 5000] [--programs corpus] [--python /usr/bin/python3.13]
"""
import argparse
import os
import sys
import tempfile

from flask import Flask, jsonify, request, send_file

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from turtleweb.flask_blueprint import create_blueprint  # noqa: E402


def create_app(programs_dir=None, python=None, env=None):
    programs_dir = os.path.abspath(programs_dir or os.path.join(HERE, "..", "corpus"))
    app = Flask(__name__)
    bp = create_blueprint()
    app.register_blueprint(bp, url_prefix="/turtleweb")
    hub = bp.hub
    current = {"sid": None}

    @app.route("/")
    def index():
        return send_file(os.path.join(HERE, "index.html"))

    @app.route("/programs")
    def programs():
        names = sorted(f[:-3] for f in os.listdir(programs_dir) if f.endswith(".py"))
        return jsonify(names)

    @app.route("/run", methods=["POST"])
    def run():
        name = os.path.basename(request.args["prog"])
        old = hub.get(current["sid"]) if current["sid"] else None
        if old is not None:
            old.stop()
        session = hub.new()
        current["sid"] = session.sid
        workdir = tempfile.mkdtemp(prefix="turtleweb-")  # programs may write files
        session.start(os.path.join(programs_dir, name + ".py"), cwd=workdir, python=python, env=env,
                      log=os.path.join(workdir, "comandos.jsonl"))
        return jsonify(sid=session.sid)

    @app.route("/stop", methods=["POST"])
    def stop():
        s = hub.get(current["sid"]) if current["sid"] else None
        if s is not None:
            s.stop()
        return jsonify(ok=True)

    return app


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1", help="use 0.0.0.0 para abrir de outro aparelho (iPad)")
    ap.add_argument("--port", type=int, default=5000)
    ap.add_argument("--programs")
    ap.add_argument("--python")
    a = ap.parse_args()
    create_app(a.programs, a.python).run(a.host, a.port, threaded=True)
