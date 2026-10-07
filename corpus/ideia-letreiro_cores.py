import turtle
cores = ['red', 'blue']
t = turtle.Turtle()
for i, letra in enumerate('python'.upper()):
    t.color(cores[i % 2])
    t.write(letra)
    t.forward(20)
