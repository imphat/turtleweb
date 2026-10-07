import turtle
t = turtle.Turtle()
def anda():
    t.forward(10)
turtle.onkey(anda, 'Up')
turtle.listen()
turtle.done()
