import turtle
t = turtle.Turtle()
def sobe():
    t.setheading(90)
    t.forward(20)
def desce():
    t.setheading(270)
    t.forward(20)
turtle.listen()
turtle.onkey(sobe, 'Up')
turtle.onkey(desce, 'Down')
turtle.done()
