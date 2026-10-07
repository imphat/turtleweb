import turtle
n = 6
pontos = [(60 * i, 30 * (i % 2)) for i in range(n)]
t = turtle.Turtle()
def liga():
    for x, y in pontos:
        t.goto(x, y)
liga()
