"""M1: um quadrado e um círculo desenhados no navegador por um programa Python real."""
from browser.conftest import near

RED, BLUE, LIGHTBLUE, WHITE = (255, 0, 0), (0, 0, 255), (173, 216, 230), (255, 255, 255)


def test_quadrado_e_circulo(run):
    r = run("quadrado_circulo")
    r.wait_state("waiting")          # turtle.done(): the program waits for the window to close
    assert not r.errors
    # square: from the center to (100,0) up to (100,100); sides are red, pensize 3
    assert near(r.pixel(50, 0), RED)
    assert near(r.pixel(100, 50), RED)
    assert near(r.pixel(50, 100), RED)
    assert near(r.pixel(50, 50), WHITE)          # inside the square nothing is filled
    # circle: tangent below the start at (-120,-100), radius 50, center (-120,-50), lightblue fill, blue border
    assert near(r.pixel(-120, -50), LIGHTBLUE)
    assert near(r.pixel(-120, -100), BLUE)
    assert near(r.pixel(-120, -150), WHITE)
    r.page.click(".tw-close")
    r.wait_state("ended")
