"""PP_TURTLE_LOG: one JSON line per top-level turtle command (SPEC section 5)."""
import contextlib
import json

_depth = [0]

CANONICAL = {
    "forward": "forward", "fd": "forward",
    "backward": "backward", "back": "backward", "bk": "backward",
    "left": "left", "lt": "left",
    "right": "right", "rt": "right",
    "goto": "goto", "setpos": "goto", "setposition": "goto",
    "setheading": "setheading", "seth": "setheading",
    "setx": "setx", "sety": "sety", "home": "home", "circle": "circle",
    "dot": "dot", "stamp": "stamp", "write": "write",
    "color": "color", "pencolor": "pencolor", "fillcolor": "fillcolor",
    "pensize": "pensize", "width": "pensize",
    "penup": "penup", "pu": "penup", "up": "penup",
    "pendown": "pendown", "pd": "pendown", "down": "pendown",
    "begin_fill": "begin_fill", "end_fill": "end_fill",
}


def simplify(value, top=True):
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float)):
        return round(float(value), 3)
    if isinstance(value, str):
        return value[:30]
    if isinstance(value, (tuple, list)):
        return [simplify(v, False) for v in value[:4]]
    return None


def install(turtle_module, path):
    """Wrap the RawTurtle methods; only the outermost call is written."""
    fh = open(path, "w", encoding="utf-8")
    depth = _depth
    cls = turtle_module.RawTurtle

    def make(orig, name):
        def wrapper(self, *args, **kwargs):
            depth[0] += 1
            try:
                result = orig(self, *args, **kwargs)
            finally:
                depth[0] -= 1
            if depth[0] == 0:
                line = [name] + [simplify(a) for a in args[:4]]
                fh.write(json.dumps(line, ensure_ascii=False) + "\n")
                fh.flush()
            return result
        wrapper.__name__ = orig.__name__
        wrapper.__doc__ = orig.__doc__
        return wrapper

    for alias, name in CANONICAL.items():
        orig = getattr(cls, alias, None)
        if orig is not None:
            setattr(cls, alias, make(orig, name))


@contextlib.contextmanager
def callback_scope():
    """Event callbacks run inside update() of an outer command; they count as top level."""
    saved = _depth[0]
    _depth[0] = 0
    try:
        yield
    finally:
        _depth[0] = saved
