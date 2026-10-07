"""SPEC secção 7, item 1: a lista de comandos dos determinísticos é idêntica à esperada."""
import json

import pytest

from helpers import CORPUS, ALL_PY, deterministic, run_headless


@pytest.mark.parametrize("programa", deterministic())
def test_lista_identica(programa):
    esperado = json.loads((CORPUS / programa.replace(".py", ".esperado.json")).read_text(encoding="utf-8"))
    comandos, proc = run_headless(programa)
    assert proc.returncode == 0, proc.stderr
    assert comandos == esperado


@pytest.mark.parametrize("python", ALL_PY)
def test_quadrado_em_cada_python_sem_tkinter(python):
    esperado = json.loads((CORPUS / "referencia-quadrado.esperado.json").read_text())
    comandos, proc = run_headless("referencia-quadrado.py", python=python)
    assert proc.returncode == 0, proc.stderr
    assert comandos == esperado
