import turtle, random
t = turtle.Turtle()
turtle.colormode(1.0)
for i in range(60):
    t.pencolor(random.random(), random.random(), random.random())
    t.forward(i * 3)
    t.left(91)
