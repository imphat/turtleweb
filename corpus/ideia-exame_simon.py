import turtle, random
cores = ['red', 'blue', 'green']
sequencia = []
def clica(x, y):
    print(x, y)
turtle.onscreenclick(clica)
for i in range(3):
    sequencia.append(random.choice(cores))
    if sequencia[-1] == 'red':
        print('vermelho')
