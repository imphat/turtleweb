import turtle
cores = ['red', 'pink', 'orange']
t = turtle.Turtle()
def flor(x, y, cor):
    t.penup()
    t.goto(x, y)
    t.pendown()
    t.color(cor)
    for i in range(6):
        t.circle(20, 60)
for i in range(3):
    flor(i * 80 - 80, 0, cores[i])
turtle.done()
