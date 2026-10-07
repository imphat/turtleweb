"""Child entry point: python -u run.py program.py (fake tkinter, real turtle)."""
import os
import runpy
import sys
import traceback

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import fake_tk  # noqa: E402

fake_tk.install()
program = os.path.abspath(sys.argv[1])
sys.argv = sys.argv[1:]
sys.path[0] = os.path.dirname(program)
code = 0
try:
    runpy.run_path(program, run_name="__main__")
except SystemExit as exc:
    code = exc.code if isinstance(exc.code, int) else 0
except BaseException:
    traceback.print_exc()
    code = 1
fake_tk.finish(code)
sys.exit(code)
