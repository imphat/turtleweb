import turtle
nome = input('Seu nome? ')
t = turtle.Turtle()
for i in range(5):
    t.write(f'{nome} ⭐')
    t.forward(40)
