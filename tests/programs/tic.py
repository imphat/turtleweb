import turtle
t = turtle.Turtle()
t.pensize(3)
turtle.tracer(0)
for i in range(12):
    t.forward(10)
    turtle.update()
    turtle.Screen().cv.after(200) if False else __import__("time").sleep(0.2)
