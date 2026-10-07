import turtle
t = turtle.Turtle()
t.penup()
log = []
def tecla(nome):
    def f():
        print("tecla", nome)
    return f
for k in ("a", "space", "Up", "Return", "plus", "A"):
    turtle.onkey(tecla(k), k)
turtle.onkeypress(lambda: print("press-b"), "b")
turtle.listen()
turtle.done()
