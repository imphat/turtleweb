import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(2)
cores = ["red", "orange", "gold", "green", "blue", "purple"]
for i in range(72):
    t.color(cores[i % 6])
    t.circle(80)
    t.left(5)
turtle.done()
