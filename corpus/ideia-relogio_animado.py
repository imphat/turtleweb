import turtle
t = turtle.Turtle()
segundos = 0
def passa():
    global segundos
    segundos += 1
    t.clear()
    t.write(f'{segundos}s')
    turtle.ontimer(passa, 1000)
passa()
turtle.done()
