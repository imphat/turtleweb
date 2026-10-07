"""turtleweb: makes `import turtle` draw in the browser while Python runs on the server.

Child process side:  turtleweb.install()   (called by the sitecustomize in turtleweb/_boot)
Server side:         turtleweb.Session / Hub, and turtleweb.flask_blueprint.create_blueprint
"""
import atexit
import importlib.abc
import importlib.machinery
import os
import sys

__version__ = "0.1.0"

_installed = False
_exit_code = [0]


def boot_dir():
    """Directory with the sitecustomize that calls install() (put it on PYTHONPATH)."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "_boot")


def install():
    """Replace `tkinter` with the fake one and connect to the server. Call before `import turtle`.

    Idempotent. Environment: TURTLEWEB_PORT / TURTLEWEB_TOKEN (server channel),
    PP_TURTLE_LOG (command list file), TURTLEWEB_NO_DELAY=1 (skip animation delays).
    """
    global _installed
    if _installed:
        return
    _installed = True
    from . import _channel, _fake_tk

    tk, dialog = _fake_tk.build_module()
    sys.modules["tkinter"] = tk
    sys.modules["tkinter.simpledialog"] = dialog
    _channel.connect()

    def excepthook(kind, value, tb, _orig=sys.excepthook):
        _exit_code[0] = 1
        _orig(kind, value, tb)

    sys.excepthook = excepthook
    atexit.register(lambda: _fake_tk.finish(_exit_code[0]))

    if "turtle" in sys.modules:
        _after_turtle(sys.modules["turtle"])
    else:
        sys.meta_path.insert(0, _TurtleFinder())


def _after_turtle(module):
    path = os.environ.get("PP_TURTLE_LOG")
    if path:
        from . import _cmdlog
        _cmdlog.install(module, path)


class _TurtleFinder(importlib.abc.MetaPathFinder):
    """Runs a hook right after the standard `turtle` module is executed."""

    def find_spec(self, name, path, target=None):
        if name != "turtle":
            return None
        spec = importlib.machinery.PathFinder.find_spec(name, path)
        if spec is None or spec.loader is None:
            return None
        real = spec.loader

        class Loader(importlib.abc.Loader):
            def create_module(self, spec):
                return real.create_module(spec)

            def exec_module(self, module):
                real.exec_module(module)
                _after_turtle(module)

            def __getattr__(self, attr):
                return getattr(real, attr)

        spec.loader = Loader()
        return spec


def __getattr__(name):  # lazy server-side imports, so the child stays light
    if name in ("Session", "Hub", "child_env"):
        from . import session
        return getattr(session, name)
    raise AttributeError(name)
