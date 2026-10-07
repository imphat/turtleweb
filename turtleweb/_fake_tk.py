"""A fake `tkinter` just big enough for the standard-library `turtle`.

The real `turtle` module keeps doing all the work (moving, turning, shapes,
fills, animation, undo); only the pixels differ: every Canvas operation is
turned into a small JSON op and sent to the browser (see docs/contrato.md).

Not a general tkinter replacement: methods turtle never calls are no-ops, and
the unknown ones are recorded and reported when the program ends.
"""
import heapq
import math
import os
import re
import sys
import time
import traceback
import types

from . import _channel, _cmdlog
from ._colors import TK_COLORS

NO_DELAY = os.environ.get("TURTLEWEB_NO_DELAY") == "1"
MAX_BATCH = 2000  # ops buffered before a forced flush

_batch = []
_unknown = set()
_stats = {"ops": 0, "batches": 0}
_speed = [1.0]  # "Mais rápido": the animation delays are divided by this


class TclError(Exception):
    pass


# --- colors -----------------------------------------------------------------

def _rgb8(color):
    if not isinstance(color, str):
        raise TclError('unknown color name "%s"' % (color,))
    c = color.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]+)", c)
    if m and len(m.group(1)) in (3, 6, 9, 12):
        h = m.group(1)
        n = len(h) // 3
        # Tk scales short forms to 16 bits; the top byte is what is displayed
        return tuple(int(h[i * n:(i + 1) * n].ljust(2, "0")[:2], 16) for i in range(3))
    hexcolor = TK_COLORS.get(c.replace(" ", ""))
    if hexcolor is None:
        raise TclError('unknown color name "%s"' % color)
    return tuple(int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))


def _css(color):
    if color in ("", None):
        return ""
    try:
        return "#%02x%02x%02x" % _rgb8(color)
    except TclError:
        return ""


# --- output -----------------------------------------------------------------

def _emit(*op):
    _batch.append(list(op))
    if len(_batch) >= MAX_BATCH:
        flush()


def _compact(ops):
    """Keep only the last `coords` of each item inside one batch."""
    last = {}
    for i, op in enumerate(ops):
        if op[0] == "coords":
            last[op[1]] = i
    if len(last) == sum(1 for op in ops if op[0] == "coords"):
        return ops
    return [op for i, op in enumerate(ops) if op[0] != "coords" or last[op[1]] == i]


def flush():
    global _batch
    if not _batch:
        return
    ops, _batch = _compact(_batch), []
    _stats["ops"] += len(ops)
    _stats["batches"] += 1
    _channel.send({"t": "ops", "ops": ops})


# --- event loop (timers, incoming messages, dialogs) --------------------------

_timers = []
_seq = [0]
_cancelled = set()
_root = [None]
_canvases = []
_closed = [False]


def _schedule(ms, func, args):
    _seq[0] += 1
    heapq.heappush(_timers, (time.monotonic() + max(ms, 0) / 1000.0, _seq[0], func, args))
    return "after#%d" % _seq[0]


def _call(func, *args):
    """Run a Tk callback: errors are printed and the loop goes on, like Tk does."""
    with _cmdlog.callback_scope():
        try:
            func(*args)
        except SystemExit:
            raise
        except BaseException:
            traceback.print_exc()


def _run_due_timers():
    ran = False
    while _timers and _timers[0][0] <= time.monotonic():
        _, seq, func, args = heapq.heappop(_timers)
        if ("after#%d" % seq) in _cancelled:
            _cancelled.discard("after#%d" % seq)
            continue
        _call(func, *args)
        ran = True
    return ran


def _drain():
    """Handle every message already received."""
    n = 0
    while True:
        try:
            msg = _channel.inbox.get_nowait()
        except Exception:
            return n
        _handle(msg)
        n += 1


def _handle(msg):
    kind = msg.get("t")
    if kind in ("close", "eof"):
        _closed[0] = True
        root = _root[0]
        if root is not None and root._alive:
            if root._on_close:
                _call(root._on_close)
            else:
                root.destroy()
    elif kind == "speed":
        try:
            _speed[0] = min(max(float(msg.get("v", 1)), 1.0), 1000.0)
        except (TypeError, ValueError):
            pass
    elif _canvases:
        _canvases[-1]._dispatch(msg)


def _next_timeout():
    if _timers:
        return max(0.0, _timers[0][0] - time.monotonic())
    return None


def _wait(timeout):
    """Block until a message arrives or `timeout` passes, then process it."""
    try:
        msg = _channel.inbox.get(timeout=timeout)
    except Exception:
        return
    _handle(msg)


def _pump():
    flush()
    _drain()
    _run_due_timers()
    flush()


# --- widgets ------------------------------------------------------------------

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
        _root[0] = self

    def title(self, text=None):
        _emit("title", text)

    def wm_protocol(self, name, func=None):
        if name == "WM_DELETE_WINDOW":
            self._on_close = func

    protocol = wm_protocol

    def geometry(self, spec=None):
        m = re.match(r"(\d+)x(\d+)", spec or "")
        if m:
            self._width, self._height = int(m.group(1)), int(m.group(2))
            _emit("geometry", self._width, self._height)

    def winfo_screenwidth(self):
        return 1280

    def winfo_screenheight(self):
        return 800

    def destroy(self):
        self._alive = False
        _emit("closed")
        flush()

    def update(self):
        _pump()

    def mainloop(self, n=0):
        flush()
        if not _channel.connected():
            return  # headless run (tests, command log only): nothing to wait for
        _channel.send({"t": "state", "s": "waiting"})
        while self._alive:
            _drain()
            _run_due_timers()
            flush()
            if not self._alive:
                break
            _wait(_next_timeout())


def mainloop(n=0):
    if _root[0] is not None:
        _root[0].mainloop()


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


# --- Canvas -------------------------------------------------------------------

_BIND_RE = [
    (re.compile(r"^<(?:ButtonPress|Button)-(\d)>$"), r"<Button-\1>"),
    (re.compile(r"^<ButtonRelease-(\d)>$"), r"<ButtonRelease-\1>"),
    (re.compile(r"^<(?:B|Button)(\d)-Motion>$"), r"<B\1-Motion>"),
    (re.compile(r"^<(?:KeyPress|Key)-(.+)>$"), r"<KeyPress-\1>"),
    (re.compile(r"^<(?:KeyPress|Key)>$"), "<KeyPress>"),
    (re.compile(r"^<KeyRelease-(.+)>$"), r"<KeyRelease-\1>"),
]


def _norm(seq):
    for rx, rep in _BIND_RE:
        if rx.match(seq):
            return rx.sub(rep, seq)
    return seq


def _point_in_polygon(x, y, p):
    inside = False
    n = len(p) // 2
    j = n - 1
    for i in range(n):
        xi, yi, xj, yj = p[2 * i], p[2 * i + 1], p[2 * j], p[2 * j + 1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def _dist_segment(x, y, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if dx == dy == 0:
        return math.hypot(x - x1, y - y1)
    t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - x1 - t * dx, y - y1 - t * dy)


class Canvas(Misc):
    def __init__(self, master=None, **kw):
        Misc.__init__(self, master, **kw)
        self._items = {}
        self._order = []
        self._next = 1
        self._bindings = {}
        self._tag_bindings = {}
        self._focused = False
        self._drag_item = None
        _canvases.append(self)
        if kw.get("bg"):
            _emit("bg", _css(kw["bg"]))

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
            elif k == "font" and isinstance(v, (tuple, list)):
                v = list(v)
            elif k == "width":
                v = float(v)
            clean[k] = v
        return clean

    def _create(self, kind, coords, kw):
        item = self._next
        self._next += 1
        coords = self._flat(coords)
        self._items[item] = {"kind": kind, "coords": coords, "opts": dict(kw)}
        self._order.append(item)
        _emit("create", item, kind, coords, self._clean(kw))
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
        _emit("coords", item, coords)

    def itemconfigure(self, item, **kw):
        self._items[item]["opts"].update(kw)
        clean = self._clean(kw)
        if clean:
            _emit("config", item, clean)

    itemconfig = itemconfigure

    def itemcget(self, item, key):
        return self._items[item]["opts"].get(key)

    def tag_raise(self, item, *a):
        if item in self._items:
            self._order.remove(item)
            self._order.append(item)
            _emit("raise", item)

    def tag_lower(self, item, *a):
        if item in self._items:
            self._order.remove(item)
            self._order.insert(0, item)
            _emit("lower", item)

    def delete(self, item):
        if item == "all":
            self._items.clear()
            self._order.clear()
            _emit("delete", "all")
        elif item in self._items:
            del self._items[item]
            self._order.remove(item)
            _emit("delete", item)

    def type(self, item):
        return self._items[item]["kind"]

    def find_all(self):
        return tuple(self._order)

    def bbox(self, item):
        # Rough text metrics: the real size is only known in the browser.
        it = self._items[item]
        x, y = it["coords"][:2]
        font = it["opts"].get("font") or ("Arial", 8, "normal")
        size = abs(int(font[1])) if len(font) > 1 else 8
        w = int(len(str(it["opts"].get("text", ""))) * size * 0.6)
        return (int(x), int(y - size * 1.4), int(x + w), int(y))

    def update(self):
        _pump()

    def update_idletasks(self):
        pass

    def after(self, ms, func=None, *args):
        if func is None:
            # a plain delay: this is the turtle animation speed
            flush()
            if not NO_DELAY and ms > 0 and _channel.connected():
                time.sleep(ms / 1000.0 / _speed[0])
            return None
        return _schedule(ms, func, args)

    def after_idle(self, func, *args):
        return _schedule(0, func, args)

    def after_cancel(self, ident):
        _cancelled.add(ident)

    def winfo_rgb(self, color):
        return tuple(v * 257 for v in _rgb8(color))

    def configure(self, **kw):
        self._opts.update(kw)
        if kw.get("bg"):
            _emit("bg", _css(kw["bg"]))

    config = configure

    def cget(self, key):
        return self._opts.get(key)

    __getitem__ = cget

    def canvasx(self, x):
        return x - self.tk._width / 2.0

    def canvasy(self, y):
        return y - self.tk._height / 2.0

    def focus_force(self):
        self._focused = True

    def xview(self, *a):
        pass

    def yview(self, *a):
        pass

    def xview_moveto(self, f):
        pass

    def yview_moveto(self, f):
        pass

    # -- events ---------------------------------------------------------------

    def bind(self, seq, func=None, add=None):
        seq = _norm(seq)
        if func is None:
            return self._bindings.get(seq)
        if add in ("+", True) and seq in self._bindings:
            self._bindings[seq].append(func)
        else:
            self._bindings[seq] = [func]

    def unbind(self, seq, funcid=None):
        self._bindings.pop(_norm(seq), None)

    def tag_bind(self, item, seq, func=None, add=None):
        key = (item, _norm(seq))
        if func is None:
            return self._tag_bindings.get(key)
        if add in ("+", True) and key in self._tag_bindings:
            self._tag_bindings[key].append(func)
        else:
            self._tag_bindings[key] = [func]

    def tag_unbind(self, item, seq, funcid=None):
        self._tag_bindings.pop((item, _norm(seq)), None)

    def _hit(self, cx, cy):
        """Topmost item under the point (canvas coordinates), like Tk's 'current' item."""
        for item in reversed(self._order):
            it = self._items[item]
            p, o = it["coords"], it["opts"]
            if it["kind"] == "polygon" and len(p) >= 6:
                if o.get("fill") and _point_in_polygon(cx, cy, p):
                    return item
                if o.get("outline"):
                    w = float(o.get("width", 1)) / 2 + 1
                    n = len(p) // 2
                    if any(_dist_segment(cx, cy, p[2 * i], p[2 * i + 1],
                                         p[2 * (i + 1) % len(p)], p[(2 * (i + 1) + 1) % len(p)]) <= w
                           for i in range(n)):
                        return item
            elif it["kind"] == "line" and len(p) >= 4 and o.get("fill"):
                w = float(o.get("width", 1)) / 2 + 1
                if any(_dist_segment(cx, cy, *p[i:i + 4]) <= w for i in range(0, len(p) - 2, 2)):
                    return item
            elif it["kind"] == "text":
                x0, y0, x1, y1 = self.bbox(item)
                if x0 <= cx <= x1 and y0 <= cy <= y1:
                    return item
        return None

    def _fire(self, handlers, event):
        for func in list(handlers):
            _call(func, event)

    def _dispatch(self, msg):
        kind = msg.get("t")
        if kind in ("mousedown", "mouseup", "mousemove"):
            self._dispatch_mouse(kind, msg)
        elif kind in ("keydown", "keyup"):
            if not self._focused:
                return  # like Tk: keys only reach the canvas after listen()
            sym = str(msg.get("k", ""))
            ev = Event(keysym=sym, char=msg.get("c", ""), widget=self)
            if kind == "keydown":
                seqs = ("<KeyPress-%s>" % sym, "<KeyPress>")
            else:
                seqs = ("<KeyRelease-%s>" % sym, "<KeyRelease>")
            for seq in seqs:
                if seq in self._bindings:
                    self._fire(self._bindings[seq], ev)
                    break

    def _dispatch_mouse(self, kind, msg):
        x, y, b = msg.get("x", 0), msg.get("y", 0), int(msg.get("b", 1))
        ev = Event(x=x, y=y, num=b, widget=self)
        cx, cy = self.canvasx(x), self.canvasy(y)
        if kind == "mousedown":
            item = self._hit(cx, cy)
            self._drag_item = item
            seq = "<Button-%d>" % b
            if item is not None and (item, seq) in self._tag_bindings:
                self._fire(self._tag_bindings[(item, seq)], ev)
            if seq in self._bindings:
                self._fire(self._bindings[seq], ev)
        elif kind == "mouseup":
            seq = "<ButtonRelease-%d>" % b
            item, self._drag_item = self._drag_item, None
            if item is not None and (item, seq) in self._tag_bindings:
                self._fire(self._tag_bindings[(item, seq)], ev)
            if seq in self._bindings:
                self._fire(self._bindings[seq], ev)
        else:
            seq = "<B%d-Motion>" % b
            item = self._drag_item  # Tk keeps delivering the drag to the item that was grabbed
            if item is not None and (item, seq) in self._tag_bindings:
                self._fire(self._tag_bindings[(item, seq)], ev)
            if seq in self._bindings:
                self._fire(self._bindings[seq], ev)
            elif "<Motion>" in self._bindings:
                self._fire(self._bindings["<Motion>"], ev)


# --- dialogs (turtle.textinput / numinput) ---------------------------------------

_ask_id = [0]


def _ask(kind, title, prompt, initial=None, minvalue=None, maxvalue=None):
    """Ask the page and block for the answer. Returns None on cancel or window close."""
    error = None
    while True:
        flush()
        _ask_id[0] += 1
        msg = {"t": "ask", "id": _ask_id[0], "kind": kind, "title": title, "prompt": prompt,
               "initial": initial, "min": minvalue, "max": maxvalue, "error": error}
        if not _channel.connected():
            return None
        _channel.send(msg)
        value = _wait_answer(_ask_id[0])
        if value is None or kind == "string":
            return value if value is None else str(value)
        try:
            number = float(str(value).replace(",", "."))
        except ValueError:
            error = "Isso não é um número. Tente de novo."
            continue
        if minvalue is not None and number < minvalue:
            error = "O número precisa ser pelo menos %g." % minvalue
        elif maxvalue is not None and number > maxvalue:
            error = "O número precisa ser no máximo %g." % maxvalue
        else:
            return number


def _wait_answer(ask_id):
    while True:
        msg = _channel.inbox.get()
        kind = msg.get("t")
        if kind == "answer" and msg.get("id") == ask_id:
            return msg.get("v")
        if kind in ("close", "eof"):
            _handle(msg)
            return None
        _handle(msg)


# --- install ------------------------------------------------------------------------

def build_module():
    tk = types.ModuleType("tkinter")
    tk.__doc__ = "turtleweb fake tkinter"
    for name in ("Tk", "Frame", "Canvas", "Scrollbar", "PhotoImage", "TclError",
                 "mainloop", "Event", "Misc"):
        setattr(tk, name, globals()[name])
    tk.ROUND, tk.SUNKEN, tk.HORIZONTAL, tk.VERTICAL = "round", "sunken", "horizontal", "vertical"
    tk.TkVersion = 8.6

    dialog = types.ModuleType("tkinter.simpledialog")
    dialog.askstring = lambda title, prompt, **kw: _ask("string", title, prompt, kw.get("initialvalue"))
    dialog.askfloat = lambda title, prompt, **kw: _ask(
        "float", title, prompt, kw.get("initialvalue"), kw.get("minvalue"), kw.get("maxvalue"))
    dialog.askinteger = lambda title, prompt, **kw: _ask_integer(title, prompt, **kw)
    tk.simpledialog = dialog
    return tk, dialog


def _ask_integer(title, prompt, **kw):
    value = _ask("float", title, prompt, kw.get("initialvalue"), kw.get("minvalue"), kw.get("maxvalue"))
    return None if value is None else int(value)


def finish(code):
    flush()
    _channel.send({"t": "end", "code": code, "stats": _stats, "unknown": sorted(_unknown)})
    _channel.close()
