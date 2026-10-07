import turtle
bola = turtle.Turtle()
bola.penup()
bola.shape('circle')
bola.goto(60, 60)
pontos = 0
posicoes = [(60, 60), (-60, -60)]
def muda():
    posicoes.reverse()
    bola.goto(*posicoes[0])
    turtle.ontimer(muda, 1500)
def clica(x, y):
    global pontos
    if bola.distance(x, y) < 20:
        pontos += 1
        print("pontos", pontos)
turtle.onscreenclick(clica)
turtle.ontimer(muda, 1500)
turtle.done()
