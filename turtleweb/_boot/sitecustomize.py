"""Started by Python before the program. Turns turtleweb on when the app asks for it."""
import os
import sys

if os.environ.get("TURTLEWEB_PORT") or os.environ.get("TURTLEWEB") == "1":
    try:
        import turtleweb
        turtleweb.install()
    except Exception:  # never stop the child program because of the integration
        import traceback
        traceback.print_exc()

# Another sitecustomize (e.g. a distribution's) may have been shadowed by this one: run it too.
try:
    import importlib.machinery
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    others = [p for p in sys.path if os.path.abspath(p or ".") != here]
    spec = importlib.machinery.PathFinder.find_spec("sitecustomize", others)
    if spec is not None and spec.origin and os.path.abspath(spec.origin) != os.path.abspath(__file__):
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
except Exception:
    pass
