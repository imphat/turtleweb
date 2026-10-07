import turtle, random
corpo = [turtle.Turtle()]
def cima():
    corpo[0].setheading(90)
turtle.listen()
turtle.onkey(cima, 'Up')
comida = random.randint(-100, 100)
while True:
    corpo[0].forward(10)
    if corpo[0].xcor() > 200:
        break
