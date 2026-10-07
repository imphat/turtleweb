import turtle
bola = turtle.Turtle()
raquete = turtle.Turtle()
def sobe():
    raquete.sety(raquete.ycor() + 20)
turtle.onkeypress(sobe, 'Up')
turtle.listen()
while True:
    bola.forward(5)
    if bola.xcor() > 200:
        break
