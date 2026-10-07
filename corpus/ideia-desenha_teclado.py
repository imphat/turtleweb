import turtle
t = turtle.Turtle()
def anda():
    t.forward(10)
screen = turtle.Screen()
screen.onkey(anda, 'Up')
screen.listen()
turtle.done()
