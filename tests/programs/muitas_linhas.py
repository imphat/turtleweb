import turtle
turtle.tracer(0)
t = turtle.Turtle()
t.hideturtle()
for i in range(4000):
    t.penup(); t.goto(i % 200 - 100, (i * 7) % 200 - 100); t.pendown()
    t.color("red" if i % 2 else "blue")
    t.forward(5)
turtle.update()
turtle.done()
