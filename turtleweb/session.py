"""Server side of the channel: one Session per program run.

The app (or the demo) starts the child process; the Session listens on
127.0.0.1, collects what the child draws, and lets any web framework serve it
to the page (see flask_blueprint.py and docs/contrato.md).
"""
import json
import os
import secrets
import socket
import subprocess
import sys
import threading
import time

import turtleweb

TERMINAL = ("ended", "error", "stopped")
# What the page may send to the program (everything else is dropped).
PAGE_MESSAGES = ("mousedown", "mouseup", "mousemove", "keydown", "keyup", "answer", "close", "speed")
MAX_OUTPUT = 200_000
COMPACT_AT = 3000  # events kept before the history is replaced by a snapshot of the drawing


class _Model:
    """What the page would be showing: lets a long run forget its history (and a late page start from a snapshot)."""

    def __init__(self):
        self.items = {}
        self.order = []
        self.bg = None
        self.geometry = None
        self.title = None
        self.listening = False

    def apply(self, op):
        name = op[0]
        if name == "create":
            self.items[op[1]] = [op[2], op[3], dict(op[4])]
            self.order.append(op[1])
        elif name == "coords" and op[1] in self.items:
            self.items[op[1]][1] = op[2]
        elif name == "config" and op[1] in self.items:
            self.items[op[1]][2].update(op[2])
        elif name in ("raise", "lower") and op[1] in self.items:
            self.order.remove(op[1])
            self.order.append(op[1]) if name == "raise" else self.order.insert(0, op[1])
        elif name == "delete":
            if op[1] == "all":
                self.items.clear()
                self.order.clear()
            elif op[1] in self.items:
                del self.items[op[1]]
                self.order.remove(op[1])
        elif name == "bg":
            self.bg = op[1]
        elif name == "geometry":
            self.geometry = op[1:3]
        elif name == "title":
            self.title = op[1]
        elif name == "listen":
            self.listening = True

    def snapshot(self):
        ops = []
        if self.geometry:
            ops.append(["geometry"] + list(self.geometry))
        if self.bg:
            ops.append(["bg", self.bg])
        if self.title:
            ops.append(["title", self.title])
        for i in self.order:
            kind, coords, opts = self.items[i]
            ops.append(["create", i, kind, coords, opts])
        if self.listening:
            ops.append(["listen"])
        return {"t": "ops", "reset": True, "ops": ops}


def child_env(session=None, env=None, log=None):
    """Environment for the child process: sitecustomize on PYTHONPATH, channel port and token."""
    env = dict(os.environ if env is None else env)
    pkg_parent = os.path.dirname(os.path.dirname(os.path.abspath(turtleweb.__file__)))
    parts = [turtleweb.boot_dir()]
    if env.get("PYTHONPATH"):
        parts.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(parts)
    env["PYTHONUTF8"] = "1"
    env["TURTLEWEB"] = "1"
    env["TURTLEWEB_PATH"] = pkg_parent  # last-resort import path (a checkout that is not pip-installed)
    if session is not None:
        env["TURTLEWEB_PORT"] = str(session.port)
        env["TURTLEWEB_TOKEN"] = session.token
    if log:
        env["PP_TURTLE_LOG"] = str(log)
    return env


class Session:
    def __init__(self, sid=None):
        self.sid = sid or secrets.token_urlsafe(8)
        self.token = secrets.token_hex(16)
        self.state = "starting"
        self.code = None
        self.events = []  # everything the page needs, in order (SSE id = position + _dropped)
        self._dropped = 0
        self._model = _Model()
        self.stderr = ""
        self.proc = None
        self._cond = threading.Condition()
        self._conn = None
        self._send_lock = threading.Lock()
        self._pending = []  # page messages that arrived before the program connected
        self._stopped = False
        self._finalized = False
        self._child_end = None
        self.child_end = None  # the child's own `end` message (stats, unknown fake-Tk methods)
        self._reader = None
        self._listener = socket.socket()
        self._listener.bind(("127.0.0.1", 0))
        self._listener.listen(1)
        self.port = self._listener.getsockname()[1]
        threading.Thread(target=self._accept, daemon=True).start()

    # -- starting the program ---------------------------------------------------

    def start(self, program, cwd=None, python=None, log=None, env=None, args=(), stdin_text=None):
        """Convenience for the demo and tests: spawn `python -u program` with the channel set up.

        `stdin_text`, if given, is fed to the program's stdin (the app normally owns it)."""
        proc = subprocess.Popen(
            [python or sys.executable, "-u", str(program), *args],
            cwd=cwd, env=child_env(self, env, log),
            stdin=subprocess.DEVNULL if stdin_text is None else subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if stdin_text is not None:
            proc.stdin.write(stdin_text.encode("utf-8"))
            proc.stdin.close()
        self.attach(proc)
        for name in ("stdout", "stderr"):
            threading.Thread(target=self._pipe, args=(getattr(proc, name), name), daemon=True).start()
        return proc

    def attach(self, proc):
        """Tell the session which process it belongs to (exit code, ■ Parar)."""
        self.proc = proc
        threading.Thread(target=self._watch, args=(proc,), daemon=True).start()

    def _pipe(self, stream, name):
        for raw in iter(stream.readline, b""):
            text = raw.decode("utf-8", "replace")
            if name == "stderr" and len(self.stderr) < MAX_OUTPUT:
                self.stderr += text
            self._push({"t": "out", "s": name, "text": text})

    def _watch(self, proc):
        code = proc.wait()
        if self._reader is not None:
            self._reader.join(2)
        self._finalize(code)

    # -- socket from the child ---------------------------------------------------

    def _accept(self):
        self._listener.settimeout(60)
        while True:
            try:
                conn, _ = self._listener.accept()
            except OSError:
                self._listener.close()
                return
            conn.settimeout(10)
            first = self._read_line(conn, b"")
            try:
                hello = json.loads(first[0]) if first else {}
            except ValueError:
                hello = {}
            if hello.get("t") == "hello" and secrets.compare_digest(str(hello.get("token", "")), self.token):
                conn.settimeout(None)
                self._conn = conn
                self._listener.close()
                self._set_state("running")
                pending, self._pending = self._pending, []
                for msg in pending:
                    self.send(msg)
                self._reader = threading.Thread(target=self._read, args=(conn, first[1]), daemon=True)
                self._reader.start()
                return
            conn.close()

    @staticmethod
    def _read_line(conn, buf):
        try:
            while b"\n" not in buf:
                chunk = conn.recv(65536)
                if not chunk:
                    return None
                buf += chunk
        except OSError:
            return None
        line, rest = buf.split(b"\n", 1)
        return line, rest

    def _read(self, conn, buf):
        while True:
            got = self._read_line(conn, buf)
            if got is None:
                break
            line, buf = got
            try:
                msg = json.loads(line)
            except ValueError:
                continue
            kind = msg.get("t")
            if kind == "end":
                self._child_end = self.child_end = msg
            elif kind == "state":
                self._set_state(msg.get("s"))
            elif kind == "ops":
                for op in msg["ops"]:
                    self._model.apply(op)
                self._push(msg, raw=line)
                if len(self.events) > COMPACT_AT:
                    self._compact()
            elif kind == "ask":
                self._push(msg, raw=line)
        if self.proc is None:  # nobody else will tell us how it ended
            self._finalize((self._child_end or {}).get("code"))

    # -- state and events ----------------------------------------------------------

    def _push(self, msg, raw=None):
        with self._cond:
            self.events.append(raw.decode("utf-8") if raw is not None else json.dumps(msg, separators=(",", ":")))
            self._cond.notify_all()

    def _compact(self):
        with self._cond:
            state = {"t": "state", "s": self.state, "code": self.code}
            self._dropped += len(self.events) - 2
            self.events = [json.dumps(self._model.snapshot(), separators=(",", ":")),
                           json.dumps(state, separators=(",", ":"))]
            self._cond.notify_all()

    def _set_state(self, state, code=None):
        self.state = state
        self._push({"t": "state", "s": state, "code": code})

    def _finalize(self, code):
        with self._cond:
            if self._finalized:
                return
            self._finalized = True
        if self._child_end is not None and code is None:
            code = self._child_end.get("code")
        self.code = code
        # a negative code means a signal: the app (or the user) ended it, not the program's own error
        state = "stopped" if self._stopped or (code or 0) < 0 else ("ended" if code in (0, None) else "error")
        self._set_state(state, code)
        if self._conn is not None:
            try:
                self._conn.close()
            except OSError:
                pass
        try:
            self._listener.close()
        except OSError:
            pass

    def iter_events(self, start=0, timeout=15.0):
        """Yield (id, json_text) forever; yields None every `timeout` seconds as a keepalive.

        `start` is an absolute id. If history was compacted past it, the snapshot comes first.
        Returns after the terminal state has been yielded.
        """
        i = start
        while True:
            with self._cond:
                if i >= self._dropped + len(self.events):
                    self._cond.wait(timeout)
                first = max(i - self._dropped, 0)
                chunk = [(self._dropped + k, text) for k, text in enumerate(self.events[first:], first)]
            if not chunk:
                yield None
                continue
            for item in chunk:
                yield item
            i = chunk[-1][0] + 1
            if self.state in TERMINAL and i >= self._dropped + len(self.events):
                return

    def wait_done(self, timeout=60.0):
        end = time.monotonic() + timeout
        while self.state not in TERMINAL:
            if time.monotonic() > end:
                raise TimeoutError("o programa não terminou em %ss (estado: %s)" % (timeout, self.state))
            time.sleep(0.02)
        return self.code

    # -- page -> program -------------------------------------------------------------

    def send(self, msg):
        """Forward a message from the page to the program. Returns False if it was dropped."""
        if isinstance(msg, list):  # the page batches messages to keep their order
            return all([self.send(m) for m in msg]) if msg else False
        if not isinstance(msg, dict) or msg.get("t") not in PAGE_MESSAGES:
            return False
        if self._conn is None:
            if self.state == "starting" and len(self._pending) < 100:
                self._pending.append(msg)   # delivered as soon as the program connects
                return True
            return False
        data = (json.dumps(msg, separators=(",", ":")) + "\n").encode("utf-8")
        with self._send_lock:
            try:
                self._conn.sendall(data)
            except OSError:
                return False
        return True

    def stop(self):
        """■ Parar: end the process, keep the drawing, mark the run as stopped."""
        self._stopped = True
        proc = self.proc
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(3)
            except subprocess.TimeoutExpired:
                proc.kill()
        elif proc is None:
            self._finalize(None)

    def snapshot(self):
        return {"sid": self.sid, "state": self.state, "code": self.code, "events": self._dropped + len(self.events)}


class Hub:
    """Keeps the runs by id so the page can attach to them (the app may keep its own instead)."""

    def __init__(self, keep=20):
        self._runs = {}
        self._keep = keep
        self._lock = threading.Lock()

    def add(self, session):
        with self._lock:
            self._runs[session.sid] = session
            while len(self._runs) > self._keep:
                old = next((s for s in self._runs.values() if s.state in TERMINAL), None)
                if old is None:
                    break
                del self._runs[old.sid]
        return session

    def new(self, **kw):
        return self.add(Session(**kw))

    def get(self, sid):
        return self._runs.get(sid)
