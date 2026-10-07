import turtle
grade = [[0] * 5 for _ in range(5)]
grade[2][2] = 1
t = turtle.Turtle()
def quadrado(x, y):
    t.goto(x, y)
    t.stamp()
for l in range(5):
    for c in range(5):
        if grade[l][c]:
            quadrado(c * 20, l * 20)
