import turtle, random
t = turtle.Turtle()
def pinta(x, y):
    t.goto(x, y)
    t.dot(10, random.choice(['red', 'blue']))
turtle.onscreenclick(pinta)
turtle.done()
