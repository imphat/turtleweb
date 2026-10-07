import turtle
paleta = {'vermelho': 'red', 'azul': 'blue'}
def pega(nome):
    return paleta.get(nome, 'black')
cor = input('Cor? ')
t = turtle.Turtle()
if cor in paleta:
    t.color(pega(cor))
