import turtle, random
t = turtle.Turtle()
for i in range(50):
    t.goto(random.randint(-100, 100), random.randint(-100, 100))
    t.dot(5)
turtle.done()
