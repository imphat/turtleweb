import turtle
t = turtle.Turtle()
t.speed(3)
depth = [0]
def arrasta(x, y):
    if depth[0]:
        print("aninhado")
    depth[0] += 1
    t.goto(x, y)
    depth[0] -= 1
t.ondrag(arrasta)
t.getscreen().onscreenclick(lambda x, y: None)
turtle.Screen().onrelease(lambda x, y: print("fim-arraste")) if hasattr(turtle.Screen(), "onrelease") else None
t.onrelease(lambda x, y: print("fim-arraste"))
turtle.done()
