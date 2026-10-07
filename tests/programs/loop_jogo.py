import turtle
t = turtle.Turtle()
t.penup()
s = turtle.Screen()
s.tracer(0)
def sobe():
    t.sety(t.ycor() + 30)
s.onkeypress(sobe, "Up")
s.listen()
while True:       # game loop with update(), like the corpus games
    s.update()
    if t.ycor() > 100:
        print("fim")
        break
