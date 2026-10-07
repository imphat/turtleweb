import turtle
turtle.tracer(0)
t = turtle.Turtle()
t.penup()
t.color("red")
for i in range(3000):
    t.forward(3)
    t.left(7)
    t.stamp()
turtle.update()
turtle.done()
