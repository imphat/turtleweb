import turtle
pontos = [(50, 20), (-30, 60), (10, -40)]
ordem = sorted(pontos, key=lambda p: p[0])
t = turtle.Turtle()
for x, y in ordem:
    t.goto(x, y)
