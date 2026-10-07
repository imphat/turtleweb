import turtle
t = turtle.Turtle()
t.color('orange')
t.pensize(3)
t.begin_fill()
for i in range(5):
    t.forward(150)
    t.right(144)
t.end_fill()
turtle.done()
