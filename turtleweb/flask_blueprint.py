"""Flask blueprint: serves turtleweb.js and relays a Session to the page (SSE + POST)."""
import json
import os

from flask import Blueprint, Response, abort, jsonify, request, send_from_directory

from .session import Hub

STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


def create_blueprint(hub=None, name="turtleweb"):
    """Routes (relative to wherever the blueprint is registered):

    GET  /turtleweb.js       the page script
    GET  /events/<sid>       server-sent events of the run (supports Last-Event-ID and ?last=<id>)
    POST /input/<sid>        a JSON message from the page to the program
    POST /stop/<sid>         ■ Parar
    GET  /status/<sid>       {"state": ..., "code": ...}
    """
    hub = hub or Hub()
    bp = Blueprint(name, __name__)
    bp.hub = hub

    def session_or_404(sid):
        s = hub.get(sid)
        if s is None:
            abort(404)
        return s

    @bp.route("/turtleweb.js")
    def script():
        resp = send_from_directory(STATIC, "turtleweb.js", mimetype="text/javascript")
        resp.headers["Cache-Control"] = "no-cache"
        return resp

    @bp.route("/events/<sid>")
    def events(sid):
        s = session_or_404(sid)
        # Last-Event-ID is sent by the browser's own reconnect; ?last= by turtleweb.js when it reopens the stream itself
        last = request.headers.get("Last-Event-ID", "") or request.args.get("last", "")
        start = int(last) + 1 if last.isdigit() else 0

        def gen():
            for item in s.iter_events(start):
                if item is None:
                    yield ": ping\n\n"
                else:
                    yield "id: %d\ndata: %s\n\n" % item

        return Response(gen(), mimetype="text/event-stream",
                        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    @bp.route("/input/<sid>", methods=["POST"])
    def page_input(sid):
        s = session_or_404(sid)
        msg = request.get_json(silent=True)
        return jsonify(ok=s.send(msg))

    @bp.route("/stop/<sid>", methods=["POST"])
    def stop(sid):
        session_or_404(sid).stop()
        return jsonify(ok=True)

    @bp.route("/status/<sid>")
    def status(sid):
        return jsonify(session_or_404(sid).snapshot())

    return bp
