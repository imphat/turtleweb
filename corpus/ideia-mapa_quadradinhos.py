import turtle
mapa = [[1, 0], [0, 2]]
cores = {0: 'green', 1: 'blue', 2: 'brown'}
t = turtle.Turtle()
for linha in mapa:
    for tipo in linha:
        t.color(cores[tipo])
        t.stamp()
