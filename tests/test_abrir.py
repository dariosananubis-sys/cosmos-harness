"""El verbo que faltaba, y las tres formas de que no sirva.

`GOAL.md` §7: no está terminado hasta que se le ha visto fallar. Cada prueba de
aquí construye el caso que rompería `abrir` y exige el fallo — no basta con que
funcione sobre un árbol bueno.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from cosmos.abrir import NodoNoEncontrado, abrir, formatear, resolver
from cosmos.modelo import cargar_arbol


def _escribir(base: Path, ruta: str, frontmatter: dict[str, str], cuerpo: str = "") -> None:
    destino = base / ruta
    destino.parent.mkdir(parents=True, exist_ok=True)
    lineas = ["---"] + [f"{k}: {v}" for k, v in frontmatter.items()] + ["---", ""]
    destino.write_text("\n".join(lineas) + cuerpo + "\n", encoding="utf-8")


def _arbol_minimo(base: Path) -> None:
    _escribir(base, "galaxia.md", {"cosmos": "galaxia", "nombre": "t", "resumen": "Árbol de prueba."})
    _escribir(base, "sistemas/web.md",
              {"cosmos": "sistema-solar", "nombre": "web", "padre": '""',
               "resumen": "Sitios que cargan y convierten."},
              "Cuerpo del oficio.")
    _escribir(base, "estrellas/web.md",
              {"cosmos": "estrella", "nombre": "web", "ilumina": "web",
               "resumen": "Lo cierto en todo trabajo de web."},
              "Se prueba en un móvil de gama media.")
    _escribir(base, "paises/web--pagos.md",
              {"cosmos": "pais", "nombre": "pagos", "padre": "web",
               "resumen": "Cobrar sin perder al cliente en el intento."})
    _escribir(base, "pueblos/stripe/SKILL.md",
              {"cosmos": "pueblo", "nombre": "stripe", "padre": "web/pagos",
               "resumen": "Pasarela con reintentos y webhooks idempotentes."},
              "https://example.com · uso real.")


class AbrirResuelve(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.base = Path(self.tmp.name)
        _arbol_minimo(self.base)
        self.arbol = cargar_arbol(self.base)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_la_ruta_del_catalogo_se_abre(self) -> None:
        """El fallo que motivó la pieza: el catálogo daba rutas que no se podían abrir.

        El catálogo entrega `web/pagos`; en disco el fichero es `paises/web--pagos.md`.
        Si esto falla, el mapa vuelve a dar direcciones que no llevan a ningún sitio.
        """

        nodo = resolver(self.arbol, "web/pagos")
        self.assertEqual(nodo.nombre, "pagos")
        self.assertEqual(nodo.cosmos, "pais")

    def test_trae_la_estrella_del_oficio(self) -> None:
        ap = abrir(self.arbol, "web")
        self.assertIsNotNone(ap.estrella)
        self.assertIn("móvil de gama media", formatear(ap))

    def test_nombra_a_los_hijos_pero_no_los_carga(self) -> None:
        """Un nivel nombra a sus hijos; describirlos es cargarlos (GOAL §2)."""

        ap = abrir(self.arbol, "web")
        salida = formatear(ap)
        self.assertIn("web/pagos", salida)
        self.assertNotIn("Cobrar sin perder", salida.split("por dónde seguir bajando")[0])


class AbrirFalla(unittest.TestCase):
    """Las tres formas de que `abrir` no sirva. Las tres tienen que dar error."""

    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.base = Path(self.tmp.name)
        _arbol_minimo(self.base)
        self.arbol = cargar_arbol(self.base)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_ruta_inexistente_falla_y_sugiere(self) -> None:
        with self.assertRaises(NodoNoEncontrado) as caso:
            resolver(self.arbol, "web/inventado")
        self.assertIn("no existe", str(caso.exception))

    def test_nombre_ambiguo_falla_en_vez_de_elegir(self) -> None:
        """Elegir por ti cuando hay duda hace perder más tiempo del que ahorra."""

        _escribir(self.base, "paises/otro--pagos.md",
                  {"cosmos": "pais", "nombre": "pagos", "padre": "web",
                   "resumen": "Otro país que se llama igual."})
        arbol = cargar_arbol(self.base)
        with self.assertRaises(NodoNoEncontrado) as caso:
            resolver(arbol, "pagos")
        self.assertIn("ambiguo", str(caso.exception))

    def test_arbol_vacio_no_revienta(self) -> None:
        with TemporaryDirectory() as vacio:
            arbol = cargar_arbol(Path(vacio))
            with self.assertRaises(NodoNoEncontrado):
                resolver(arbol, "lo-que-sea")


if __name__ == "__main__":
    unittest.main()
