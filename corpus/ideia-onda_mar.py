import turtle, math
t = turtle.Turtle()
t.penup()
for x in range(-200, 200, 5):
    t.goto(x, 50 * math.sin(x / 30))
    t.pendown()
turtle.done()
