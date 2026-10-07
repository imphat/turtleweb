import turtle
t = turtle.Turtle()
try:
    lados = int(turtle.textinput('Lados', 'Quantos lados?'))
except (TypeError, ValueError):
    lados = 5
for i in range(lados):
    t.forward(60)
    t.left(360 / lados)
turtle.done()
