import turtle
nome = turtle.textinput("Nome", "Como você se chama?")
idade = turtle.numinput("Idade", "Quantos anos?", default=10, minval=1, maxval=120)
print(repr(nome), repr(idade))
t = turtle.Turtle()
t.write(str(nome))
turtle.done()
