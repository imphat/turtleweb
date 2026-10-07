import turtle

t = turtle.Turtle()
s = turtle.Screen()
s.bgcolor("lightyellow")
nome = s.textinput("Nome", "Qual é o seu nome?")
t.penup()
t.goto(-150, -150)
t.write("Olá, " + str(nome), font=("Arial", 16, "bold"))
t.goto(0, 0)
t.pendown()


def pinta_timer():
    t.penup()
    t.goto(-100, 100)
    t.dot(30, "green")
    t.goto(0, 0)
    t.pendown()


def vai(x, y):
    t.pensize(4)
    t.goto(x, y)


s.ontimer(pinta_timer, 200)
s.onscreenclick(vai)
turtle.done()
