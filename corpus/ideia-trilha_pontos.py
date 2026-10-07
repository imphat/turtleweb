import turtle, random
t = turtle.Turtle()
visitados = set()
for i in range(100):
    t.forward(10)
    t.left(random.choice([0, 90, 180]))
    visitados.add((round(t.xcor()), round(t.ycor())))
print(len(visitados))
