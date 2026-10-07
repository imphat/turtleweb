import turtle
t = turtle.Turtle()
t.color("red")
t.pensize(5)
t.forward(100)
for i in range(100000):   # keeps drawing until the app stops it
    t.left(5)
    t.forward(1)
