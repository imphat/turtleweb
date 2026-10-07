import turtle, random
cores = ['red', 'blue']
t = turtle.Turtle()
def quadrado():
    t.color(random.choice(cores))
    for i in range(4):
        t.forward(50)
        t.right(90)
turtle.Screen().onkey(quadrado, 'q')
turtle.Screen().onscreenclick(lambda x, y: t.clear())
turtle.done()
