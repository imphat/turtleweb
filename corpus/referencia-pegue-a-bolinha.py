import turtle, random
bola = turtle.Turtle()
bola.penup()
bola.shape('circle')
pontos = 0
def muda():
    bola.goto(random.randint(-150, 150), random.randint(-150, 150))
    turtle.ontimer(muda, 1000)
def clica(x, y):
    global pontos
    if bola.distance(x, y) < 20:
        pontos += 1
        print(pontos)
turtle.onscreenclick(clica)
muda()
turtle.done()
