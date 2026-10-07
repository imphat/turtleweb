import turtle
cores = ['red', 'blue']
def espiral():
    for i in range(50):
        t.forward(i)
        t.color(cores[i % 2])
t = turtle.Turtle()
espiral()
