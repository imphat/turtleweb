"""Child side of the channel: a TCP socket to the server, JSON lines both ways.

The port arrives in TURTLEWEB_PORT (and a shared secret in TURTLEWEB_TOKEN). The
program's stdin/stdout/stderr are never touched, so `input()` and `print()`
stay with the app.
"""
import json
import os
import queue
import socket
import threading

inbox = queue.Queue()
_sock = None
_lock = threading.Lock()


def connect():
    """Connect if the environment asks for it. Returns True when connected."""
    global _sock
    if _sock is not None:
        return True
    port = os.environ.get("TURTLEWEB_PORT")
    if not port:
        return False
    sock = socket.create_connection(("127.0.0.1", int(port)), timeout=10)
    sock.settimeout(None)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    _sock = sock
    send({"t": "hello", "v": 1, "token": os.environ.get("TURTLEWEB_TOKEN", "")})
    threading.Thread(target=_reader, args=(sock,), daemon=True).start()
    return True


def connected():
    return _sock is not None


def send(obj):
    """Send one message; silently drops it when the server is gone."""
    if _sock is None:
        return
    data = (json.dumps(obj, separators=(",", ":")) + "\n").encode("utf-8")
    with _lock:
        try:
            _sock.sendall(data)
        except OSError:
            pass


def _reader(sock):
    buf = b""
    try:
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                if line.strip():
                    try:
                        inbox.put(json.loads(line.decode("utf-8")))
                    except ValueError:
                        pass
    except OSError:
        pass
    inbox.put({"t": "eof"})


def close():
    global _sock
    if _sock is not None:
        try:
            _sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        _sock.close()
        _sock = None
