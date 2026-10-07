import pytest

from helpers import NO_TK


@pytest.fixture(scope="session")
def no_tk_python():
    if not NO_TK:
        pytest.skip("nenhum Python sem Tkinter disponível")
    return NO_TK[0]
