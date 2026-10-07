import turtle

t = turtle.Turtle()
t.pensize(3)
t.color("red")
for _ in range(4):
    t.forward(100)
    t.left(90)
t.penup()
t.goto(-120, -100)
t.pendown()
t.color("blue", "light blue")
t.begin_fill()
t.circle(50)
t.end_fill()
t.hideturtle()
turtle.done()
