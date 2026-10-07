"""Throwaway M0 prototype: a fake `tkinter` that lets the stdlib `turtle` run
without Tk and streams every canvas operation as JSON lines on stdout.

Not the library. It exists only to answer the SPEC section 3 "canvas falso"
question. Protocol (one line per batch): PREFIX + JSON list of ops.
Input (stdin, one JSON object per line): click, key, answer, close.
"""
import heapq
import json
import os
import queue
import re
import sys
import threading
import time
import types

PREFIX = "@@TW@@ "
NO_DELAY = os.environ.get("TW_NO_DELAY") == "1"

_out = sys.stdout
_batch = []
_unknown = set()
_stats = {"ops": 0, "batches": 0, "bytes": 0}


def _emit(op):
    _batch.append(op)


def flush():
    global _batch
    if not _batch:
        return
    line = PREFIX + json.dumps(_batch, separators=(",", ":")) + "\n"
    _stats["ops"] += len(_batch)
    _stats["batches"] += 1
    _stats["bytes"] += len(line)
    _batch = []
    _out.write(line)
    _out.flush()


# --- colors: Tk accepts X11 names ("light blue", "grey50"); the page only
# understands CSS, so every color is normalized to #rrggbb here.
_COLORS = {}


def _load_colors():
    for path in ("/usr/share/X11/rgb.txt", "/etc/X11/rgb.txt"):
        if os.path.exists(path):
            with open(path) as fh:
                for line in fh:
                    m = re.match(r"\s*(\d+)\s+(\d+)\s+(\d+)\s+(.+?)\s*$", line)
                    if m:
                        _COLORS[m.group(4).lower().replace(" ", "")] = tuple(
                            int(m.group(i)) for i in (1, 2, 3))
            return
    _COLORS.update(black=(0, 0, 0), white=(255, 255, 255), red=(255, 0, 0),
                   green=(0, 255, 0), blue=(0, 0, 255), yellow=(255, 255, 0))


def _rgb8(color):
    if not _COLORS:
        _load_colors()
    if not isinstance(color, str):
        raise TclError("bad color %r" % (color,))
    c = color.strip().lower()
    if re.fullmatch(r"#[0-9a-f]{6}", c):
        return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
    if re.fullmatch(r"#[0-9a-f]{3}", c):
        return tuple(int(ch * 2, 16) for ch in c[1:])
    if re.fullmatch(r"#[0-9a-f]{12}", c):
        return tuple(int(c[i:i + 2], 16) for i in (1, 5, 9))
    rgb = _COLORS.get(c.replace(" ", ""))
    if rgb is None:
        raise TclError('unknown color name "%s"' % color)
    return rgb


def _css(color):
    if color in ("", None):
        return ""
    try:
        return "#%02x%02x%02x" % _rgb8(color)
    except TclError:
        return color


class TclError(Exception):
    pass


# --- event loop shared by Tk.mainloop, after() and the dialogs
_timers = []
_seq = [0]
_inbox = queue.Queue()
_reader_started = [False]


def _start_reader():
    if _reader_started[0]:
        return
    _reader_started[0] = True

    def run():
        for line in sys.stdin:
            line = line.strip()
            if line:
                try:
                    _inbox.put(json.loads(line))
                except ValueError:
                    pass
        _inbox.put({"t": "eof"})

    threading.Thread(target=run, daemon=True).start()


def _schedule(ms, func, args):
    _seq[0] += 1
    heapq.heappush(_timers, (time.monotonic() + ms / 1000.0, _seq[0], func, args))
    return "after#%d" % _seq[0]


def _run_due_timers():
    while _timers and _timers[0][0] <= time.monotonic():
        _, _, func, args = heapq.heappop(_timers)
        func(*args)
        flush()


class Event:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class Misc:
    """No-op widget base. Unknown public methods are recorded, not fatal."""

    def __init__(self, master=None, **kw):
        self.master = master
        self.tk = master.tk if master is not None else self
        self._opts = dict(kw)

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        _unknown.add("%s.%s" % (type(self).__name__, name))
        return lambda *a, **k: None

    def winfo_toplevel(self):
        return self.tk

    def pack(self, *a, **k):
        pass

    def grid(self, *a, **k):
        pass

    def grid_forget(self):
        pass

    def rowconfigure(self, *a, **k):
        pass

    def columnconfigure(self, *a, **k):
        pass

    def call(self, *a):
        pass

    def configure(self, **kw):
        self._opts.update(kw)

    config = configure

    def bind(self, *a, **k):
        pass

    def winfo_width(self):
        return self.tk._width

    def winfo_height(self):
        return self.tk._height


class Tk(Misc):
    def __init__(self, *a, **kw):
        Misc.__init__(self)
        self.tk = self
        self._width, self._height = 640, 600
        self._on_close = None
        self._alive = True
        _start_reader()

    def title(self, text=None):
        _emit(["title", text])

    def wm_protocol(self, name, func=None):
        if name == "WM_DELETE_WINDOW":
            self._on_close = func

    protocol = wm_protocol

    def geometry(self, spec=None):
        m = re.match(r"(\d+)x(\d+)", spec or "")
        if m:
            self._width, self._height = int(m.group(1)), int(m.group(2))
            _emit(["geometry", self._width, self._height])

    def winfo_screenwidth(self):
        return 1280

    def winfo_screenheight(self):
        return 800

    def destroy(self):
        self._alive = False

    def update(self):
        flush()

    def mainloop(self, n=0):
        flush()
        _emit(["waiting"])
        flush()
        while self._alive:
            _run_due_timers()
            timeout = None
            if _timers:
                timeout = max(0.0, _timers[0][0] - time.monotonic())
            try:
                msg = _inbox.get(timeout=timeout)
            except queue.Empty:
                continue
            if msg.get("t") in ("close", "eof"):
                if self._on_close:
                    self._on_close()
                self._alive = False
            else:
                _dispatch(msg)
            flush()


def mainloop(n=0):
    if _root[0] is not None:
        _root[0].mainloop()


_root = [None]
_canvases = []


def _dispatch(msg):
    if not _canvases:
        return
    cv = _canvases[-1]
    kind = msg.get("t")
    if kind == "click":
        func = cv._bindings.get("<Button-%d>" % msg.get("b", 1))
        if func:
            func(Event(x=msg["x"], y=msg["y"]))
    elif kind == "key":
        for seq in ("<KeyPress-%s>" % msg["k"], "<KeyPress>"):
            func = cv._bindings.get(seq)
            if func:
                func(Event(keysym=msg["k"], char=msg.get("c", "")))
                break


class Frame(Misc):
    pass


class Scrollbar(Misc):
    def set(self, *a):
        pass


class PhotoImage:
    def __init__(self, *a, **kw):
        self._opts = kw

    def blank(self):
        pass


class Canvas(Misc):
    def __init__(self, master=None, **kw):
        Misc.__init__(self, master, **kw)
        self._items = {}
        self._order = []
        self._next = 1
        self._bindings = {}
        self._tag_bindings = {}
        _canvases.append(self)
        if kw.get("bg"):
            _emit(["bg", _css(kw["bg"])])

    @staticmethod
    def _flat(args):
        out = []
        for a in args:
            if isinstance(a, (list, tuple)):
                out.extend(Canvas._flat(a))
            else:
                out.append(round(float(a), 2))
        return out

    @staticmethod
    def _clean(kw):
        clean = {}
        for k, v in kw.items():
            if k == "image":
                continue
            if k in ("fill", "outline"):
                v = _css(v)
            elif k == "font" and isinstance(v, tuple):
                v = list(v)
            clean[k] = v
        return clean

    def _create(self, kind, coords, kw):
        item = self._next
        self._next += 1
        coords = self._flat(coords)
        self._items[item] = {"kind": kind, "coords": coords, "opts": dict(kw)}
        self._order.append(item)
        _emit(["create", item, kind, coords, self._clean(kw)])
        return item

    def create_line(self, *coords, **kw):
        return self._create("line", coords, kw)

    def create_polygon(self, *coords, **kw):
        return self._create("polygon", coords, kw)

    def create_text(self, *coords, **kw):
        return self._create("text", coords, kw)

    def create_image(self, *coords, **kw):
        return self._create("image", coords, kw)

    def coords(self, item, *args):
        if not args:
            return list(self._items[item]["coords"])
        coords = self._flat(args)
        self._items[item]["coords"] = coords
        _emit(["coords", item, coords])

    def itemconfigure(self, item, **kw):
        self._items[item]["opts"].update(kw)
        clean = self._clean(kw)
        if clean:
            _emit(["config", item, clean])

    itemconfig = itemconfigure

    def tag_raise(self, item, *a):
        if item in self._items:
            self._order.remove(item)
            self._order.append(item)
            _emit(["raise", item])

    def tag_lower(self, item, *a):
        if item in self._items:
            self._order.remove(item)
            self._order.insert(0, item)
            _emit(["lower", item])

    def delete(self, item):
        if item == "all":
            self._items.clear()
            self._order.clear()
            _emit(["delete", "all"])
        elif item in self._items:
            del self._items[item]
            self._order.remove(item)
            _emit(["delete", item])

    def type(self, item):
        return self._items[item]["kind"]

    def find_all(self):
        return tuple(self._order)

    def bbox(self, item):
        # Rough text metrics; the real size is only known in the browser.
        it = self._items[item]
        x, y = it["coords"][:2]
        font = it["opts"].get("font") or ("Arial", 8, "normal")
        size = abs(int(font[1])) if len(font) > 1 else 8
        w = int(len(str(it["opts"].get("text", ""))) * size * 0.6)
        return (int(x), int(y - size * 1.4), int(x + w), int(y))

    def update(self):
        flush()

    def update_idletasks(self):
        pass

    def after(self, ms, func=None, *args):
        if func is None:
            flush()
            if not NO_DELAY:
                time.sleep(ms / 1000.0)
            return None
        return _schedule(ms, func, args)

    def after_idle(self, func, *args):
        return _schedule(0, func, args)

    def winfo_rgb(self, color):
        return tuple(v * 257 for v in _rgb8(color))

    def configure(self, **kw):
        self._opts.update(kw)
        if kw.get("bg"):
            _emit(["bg", _css(kw["bg"])])

    config = configure

    def cget(self, key):
        return self._opts.get(key)

    __getitem__ = cget

    def bind(self, seq, func=None, add=None):
        self._bindings[seq] = func

    def unbind(self, seq, funcid=None):
        self._bindings.pop(seq, None)

    def tag_bind(self, item, seq, func=None, add=None):
        self._tag_bindings[(item, seq)] = func

    def tag_unbind(self, item, seq, funcid=None):
        self._tag_bindings.pop((item, seq), None)

    def canvasx(self, x):
        return x - self.tk._width / 2.0

    def canvasy(self, y):
        return y - self.tk._height / 2.0

    def focus_force(self):
        pass

    def xview(self, *a):
        pass

    def yview(self, *a):
        pass

    def xview_moveto(self, f):
        pass

    def yview_moveto(self, f):
        pass


def _ask(kind, title, prompt, **kw):
    flush()
    _emit(["ask", kind, title, prompt])
    flush()
    while True:
        msg = _inbox.get()
        if msg.get("t") == "answer":
            value = msg.get("v")
            if value is None:
                return None
            return float(value) if kind == "float" else str(value)
        if msg.get("t") == "eof":
            return None


def install():
    """Put the fake `tkinter` in sys.modules (before `import turtle`)."""
    tk = types.ModuleType("tkinter")
    for name in ("Tk", "Frame", "Canvas", "Scrollbar", "PhotoImage",
                 "TclError", "mainloop", "Event"):
        setattr(tk, name, globals()[name])
    tk.ROUND, tk.SUNKEN, tk.HORIZONTAL = "round", "sunken", "horizontal"

    orig_init = Tk.__init__

    def tk_init(self, *a, **kw):
        orig_init(self, *a, **kw)
        _root[0] = self

    Tk.__init__ = tk_init

    dialog = types.ModuleType("tkinter.simpledialog")
    dialog.askstring = lambda title, prompt, **kw: _ask("string", title, prompt, **kw)
    dialog.askfloat = lambda title, prompt, **kw: _ask("float", title, prompt, **kw)
    tk.simpledialog = dialog
    sys.modules["tkinter"] = tk
    sys.modules["tkinter.simpledialog"] = dialog


def finish(code):
    flush()
    _emit(["end", code, _stats, sorted(_unknown)])
    flush()
