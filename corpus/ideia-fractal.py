import turtle
def arvore(t, n):
    if n > 0:
        t.forward(n)
        arvore(t, n - 10)
t = turtle.Turtle()
arvore(t, 50)
