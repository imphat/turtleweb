"""Roda um programa e despeja os itens do canvas (tipo, coordenadas, cores) em JSON.

    python geometria_dump.py real|fake programa.py saida.json   (real: precisa de Tkinter e xvfb)
Usado por test_geometria.py para comparar o turtle de verdade com o canvas falso.
"""
import atexit
import json
import os
import runpy
import sys

mode, program, out = sys.argv[1:4]
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if mode == "fake":
    import turtleweb
    turtleweb.install()
import tkinter  # noqa: E402
import turtle  # noqa: E402

turtle.TurtleScreenBase._delay = lambda self, delay: None
if mode == "real":
    turtle.TurtleScreen.mainloop = lambda self: None  # real Tk would block in done()


def rgb(cv, c):
    if not c:
        return ""
    return "#%02x%02x%02x" % tuple(v >> 8 for v in cv.winfo_rgb(c))


def dump():
    screen = turtle.Turtle._screen
    if screen is None:
        json.dump([], open(out, "w"))
        return
    cv = screen.cv._canvas if hasattr(screen.cv, "_canvas") else screen.cv
    items = []
    for i in cv.find_all():
        kind = cv.type(i)
        coords = [round(float(c), 1) for c in cv.coords(i)]
        info = {"kind": kind, "coords": coords}
        if kind == "image":
            items.append(info)
            continue
        for opt in ("fill", "outline"):
            try:
                v = cv.itemcget(i, opt)
            except tkinter.TclError:
                continue
            if v is not None:
                info[opt] = rgb(cv, str(v)) if v else ""
        if kind != "text":
            info["width"] = float(cv.itemcget(i, "width") or 1)
        else:
            info["text"] = str(cv.itemcget(i, "text"))
            info["anchor"] = str(cv.itemcget(i, "anchor"))
        items.append(info)
    bg = cv.cget("bg")
    json.dump({"bg": rgb(cv, bg), "items": items}, open(out, "w"))


atexit.register(dump)
sys.argv = [program]
sys.path.insert(0, os.path.dirname(os.path.abspath(program)))
runpy.run_path(program, run_name="__main__")
