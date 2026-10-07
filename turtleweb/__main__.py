"""python -m turtleweb programa.py  : roda o programa com o tkinter falso (sem sitecustomize).

Útil para depurar. Sem TURTLEWEB_PORT, roda "sem janela": nada é desenhado, mas PP_TURTLE_LOG funciona.
"""
import os
import runpy
import sys

import turtleweb


def main(argv):
    if len(argv) < 2:
        print("uso: python -m turtleweb programa.py [argumentos]", file=sys.stderr)
        return 2
    turtleweb.install()
    program = os.path.abspath(argv[1])
    sys.argv = argv[1:]
    sys.path.insert(0, os.path.dirname(program))
    runpy.run_path(program, run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
