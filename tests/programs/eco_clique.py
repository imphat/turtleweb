import turtle
turtle.onscreenclick(lambda x, y: print("clique", round(x), round(y)))
turtle.onscreenclick(lambda x, y: print("direito", round(x), round(y)), 3)
turtle.done()
