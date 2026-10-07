import turtle
lados = [3, 4, 5]
with open('galeria.txt', 'w') as f:
    f.write(' '.join(str(n) for n in lados))
t = turtle.Turtle()
for n in open('galeria.txt').read().split():
    for i in range(int(n)):
        t.forward(40)
        t.left(360 / int(n))
