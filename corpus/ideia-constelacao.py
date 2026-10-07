import turtle
estrelas = {'A': [0, 0], 'B': [50, 80], 'C': [120, 40]}
t = turtle.Turtle()
def liga(nome):
    x, y = estrelas[nome]
    t.goto(x, y)
for nome in estrelas:
    liga(nome)
