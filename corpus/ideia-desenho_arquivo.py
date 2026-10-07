import turtle
t = turtle.Turtle()
for linha in open('desenho.txt'):
    partes = linha.split()
    if partes[0] == 'frente':
        t.forward(int(partes[1]))
