"""Throwaway M0 demo server: runs one child program and relays its canvas ops
to the page over SSE; page input goes back to the child's stdin."""
import json
import os
import subprocess
import sys
import threading

from flask import Flask, Response, request, send_file

HERE = os.path.dirname(os.path.abspath(__file__))
PREFIX = "@@TW@@ "
CHILD_PYTHON = os.environ.get("TW_CHILD_PYTHON", "python3.13")

app = Flask(__name__)
state = {"proc": None, "events": [], "cond": threading.Condition()}


def _push(item):
    with state["cond"]:
        state["events"].append(item)
        state["cond"].notify_all()


def _pump(proc):
    for line in proc.stdout:
        if line.startswith(PREFIX):
            _push(json.loads(line[len(PREFIX):]))
        else:
            _push([["print", line.rstrip("\n")]])
    code = proc.wait()
    _push([["exit", code]])


@app.route("/")
def page():
    return send_file(os.path.join(HERE, "page.html"))


@app.route("/run", methods=["POST"])
def run():
    name = os.path.basename(request.args["prog"])
    with state["cond"]:
        state["events"] = []
    env = dict(os.environ, PYTHONUTF8="1")
    proc = subprocess.Popen(
        [CHILD_PYTHON, "-u", os.path.join(HERE, "run.py"),
         os.path.join(HERE, "programas", name + ".py")],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
        cwd=os.path.join(HERE, "programas"), env=env)
    state["proc"] = proc
    threading.Thread(target=_pump, args=(proc,), daemon=True).start()
    return "ok"


@app.route("/input", methods=["POST"])
def send_input():
    proc = state["proc"]
    if proc and proc.poll() is None:
        proc.stdin.write(json.dumps(request.get_json()) + "\n")
        proc.stdin.flush()
    return "ok"


@app.route("/events")
def events():
    def gen():
        i = 0
        while True:
            with state["cond"]:
                while i >= len(state["events"]):
                    state["cond"].wait(15)
                    if i >= len(state["events"]):
                        yield ": ping\n\n"
                chunk = state["events"][i:]
                i = len(state["events"])
            for batch in chunk:
                yield "data: %s\n\n" % json.dumps(batch)

    return Response(gen(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache"})


if __name__ == "__main__":
    app.run("127.0.0.1", int(sys.argv[1]) if len(sys.argv) > 1 else 5055,
            threaded=True)
