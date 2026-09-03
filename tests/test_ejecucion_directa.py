"""Un fichero de test que se ejecuta directo tiene que correr TODAS sus pruebas.

T05: dos ficheros tenían el `if __name__ == "__main__": unittest.main()` a media
altura, con clases definidas después. `python3 tests/test_un_solo_veredicto.py`
ejecutaba 5 pruebas de 7 y `python3 tests/test_cifras_de_las_specs.py` 4 de 13 —
**11 pruebas desaparecían sin decir nada** y las dos invocaciones terminaban en OK.
El descubrimiento (`-m unittest discover`) no lo sufría, así que el CI no mentía;
pero `python3 tests/test_X.py` es la forma natural de iterar sobre un test, y daba
un verde que no había ejercitado dos tercios del fichero.

Se comprueba con el AST, no con un grep: lo que se afirma es la posición de una
forma sintáctica (el guard de `__main__` respecto de la última clase), que es
exactamente lo que un AST representa y un grep no.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETAS = ("tests", "puente/tests")


def _linea_del_guard_main(arbol: ast.Module) -> int | None:
    for nodo in arbol.body:
        if (
            isinstance(nodo, ast.If)
            and isinstance(nodo.test, ast.Compare)
            and isinstance(nodo.test.left, ast.Name)
            and nodo.test.left.id == "__name__"
        ):
            return nodo.lineno
    return None


def _ultima_clase(arbol: ast.Module) -> int | None:
    lineas = [nodo.lineno for nodo in arbol.body if isinstance(nodo, ast.ClassDef)]
    return max(lineas) if lineas else None


class ElGuardDeMainVaDespuesDeLaUltimaClase(unittest.TestCase):
    def test_ningun_fichero_de_test_pierde_clases_al_ejecutarse_directo(self) -> None:
        ficheros = [
            fichero
            for carpeta in CARPETAS
            for fichero in sorted((RAIZ / carpeta).glob("test_*.py"))
        ]
        self.assertGreater(len(ficheros), 10, "el barrido no encontró la suite: no vigila nada")
        for fichero in ficheros:
            with self.subTest(str(fichero.relative_to(RAIZ))):
                arbol = ast.parse(fichero.read_text(encoding="utf-8"))
                guard = _linea_del_guard_main(arbol)
                ultima = _ultima_clase(arbol)
                if guard is None or ultima is None:
                    continue
                self.assertGreater(
                    guard, ultima,
                    "unittest.main() está antes de la última clase: ejecutar este fichero "
                    "directo daría un OK sin haber corrido las pruebas de debajo",
                )


if __name__ == "__main__":
    unittest.main()
