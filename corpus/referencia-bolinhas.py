import turtle
t = turtle.Turtle()
for i, cor in enumerate(['red', 'green', 'blue']):
    t.penup()
    t.goto(-80 + i * 80, 0)
    t.pendown()
    t.color(cor)
    t.dot(40)
t.penup()
t.goto(-60, -60)
t.write('Oi!', font=('Arial', 20, 'bold'))
turtle.done()
