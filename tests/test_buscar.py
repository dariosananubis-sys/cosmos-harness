"""El verbo `buscar` lleva a donde el catálogo sabe llevar, y lo dice cuando no sabe.

Las consultas de estas pruebas se ejecutaron ANTES de escribir las aserciones y se
fijó lo observado (2026-09-02, catálogo en árbol indentado): «código duplicado» llega
a `refactorizacion/reglas` en primera posición y «que google encuentre mi tienda» a
`visibilidad`. No son deseos: son el comportamiento medido que, si se degrada, hay
que enterarse — el mismo criterio que la contra-métrica, con la que este verbo
comparte motor por construcción.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from cosmos.buscar import buscar_nodos, formatear_busqueda
from cosmos.modelo import cargar_arbol

RAIZ = Path(__file__).resolve().parent.parent
ARBOL = cargar_arbol(RAIZ / "galaxia")


from tests._integrado import solo_en_el_origen

solo_en_el_origen()  # cifras y listas del catálogo del origen, no del motor


class ElVerboEncuentra(unittest.TestCase):
    def test_codigo_duplicado_lleva_a_las_reglas_de_refactorizacion(self) -> None:
        hallazgos = buscar_nodos(ARBOL, "hay codigo duplicado por todo el proyecto")
        self.assertTrue(hallazgos)
        self.assertEqual(hallazgos[0].ruta, "refactorizacion/reglas")

    def test_que_te_encuentren_lleva_a_visibilidad(self) -> None:
        hallazgos = buscar_nodos(ARBOL, "que google encuentre mi tienda")
        self.assertEqual(hallazgos[0].ruta, "visibilidad")

    def test_el_limite_se_respeta(self) -> None:
        self.assertLessEqual(len(buscar_nodos(ARBOL, "codigo", limite=3)), 3)
        self.assertEqual(buscar_nodos(ARBOL, "codigo", limite=0), [])

    def test_sin_resultados_lo_dice_en_vez_de_inventar(self) -> None:
        hallazgos = buscar_nodos(ARBOL, "xkcdzz qqwerty")
        self.assertEqual(hallazgos, [])
        self.assertIn("sin resultados", formatear_busqueda(hallazgos, "xkcdzz qqwerty"))


class ElMotorEsElDeLaContraMetrica(unittest.TestCase):
    """Por construcción comparten selección y ranking; esto lo fija contra regresiones.

    Si `buscar` dejara de usar el motor de `acertar` (o lo invirtiera), la cifra de
    acierto publicada dejaría de describir lo que el verbo devuelve — la métrica
    volvería a medir un camino que ningún agente puede recorrer.
    """

    def test_buscar_devuelve_lo_que_acertar_puntua(self) -> None:
        from cosmos.acertar import _lineas_del_catalogo, _ordenar

        consulta = "quiero saber por que va lenta mi api"
        orden = _ordenar(consulta, _lineas_del_catalogo(ARBOL))
        hallazgos = buscar_nodos(ARBOL, consulta)
        self.assertEqual([h.ruta for h in hallazgos], orden[: len(hallazgos)])


class ElCliDeBuscar(unittest.TestCase):
    def _correr(self, *args: str, cwd: Path = RAIZ) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-m", "cosmos", "buscar", *args],
                              capture_output=True, text=True, cwd=cwd)

    def test_consulta_multipalabra_sin_comillas(self) -> None:
        """El posicional `raiz` de base() se tragaba la primera palabra de la consulta."""

        r = self._correr("hay", "codigo", "duplicado", "por", "todo", "el", "proyecto")
        self.assertEqual(r.returncode, 0)
        self.assertIn("refactorizacion/reglas", r.stdout)

    def test_sin_hallazgos_sale_1(self) -> None:
        r = self._correr("xkcdzz", "qqwerty")
        self.assertEqual(r.returncode, 1)
        self.assertIn("sin resultados", r.stdout)

    def test_sobre_un_arbol_que_no_existe_lo_dice(self) -> None:
        with TemporaryDirectory() as tmp:
            toml = Path(tmp, "cosmos.toml")
            toml.write_text((RAIZ / "cosmos.toml").read_text(encoding="utf-8"), encoding="utf-8")
            r = subprocess.run(
                [sys.executable, "-m", "cosmos", "buscar", "algo", "--config", str(toml)],
                capture_output=True, text=True, cwd=RAIZ,
            )
        self.assertEqual(r.returncode, 1)
        self.assertIn("no existe", r.stderr)


if __name__ == "__main__":
    unittest.main()
