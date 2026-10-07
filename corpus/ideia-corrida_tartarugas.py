import turtle, random
a = turtle.Turtle()
def largada():
    a.forward(random.randint(1, 10))
turtle.Screen().onkey(largada, 'space')
turtle.done()
