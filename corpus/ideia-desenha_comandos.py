import turtle
t = turtle.Turtle()
while True:
    c = input('Comando? ')
    if c == 'sair':
        break
    if c == 'frente':
        t.forward(50)
