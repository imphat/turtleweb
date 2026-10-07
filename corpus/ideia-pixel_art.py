import turtle
cores = [['red', 'blue'], ['blue', 'red']]
def quadrado(t, cor):
    t.color(cor)
    t.forward(20)
t = turtle.Turtle()
for linha in cores:
    for cor in linha:
        quadrado(t, cor)
