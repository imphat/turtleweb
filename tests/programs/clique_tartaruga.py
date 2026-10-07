import turtle
t = turtle.Turtle()
t.shape("square")
t.shapesize(3)
def clicou(x, y):
    t.color("red")
    print("tartaruga", round(x), round(y))
t.onclick(clicou)
t.penup()
turtle.Screen().onclick(lambda x, y: print("tela", round(x), round(y)), add=True)
turtle.done()
