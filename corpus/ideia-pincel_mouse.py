import turtle
t = turtle.Turtle()
def arrasta(x, y):
    t.goto(x, y)
t.ondrag(arrasta)
turtle.done()
