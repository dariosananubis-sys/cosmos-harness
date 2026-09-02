"""El verbo que faltaba, y las tres formas de que no sirva.

`GOAL.md` §7: no está terminado hasta que se le ha visto fallar. Cada prueba de
aquí construye el caso que rompería `abrir` y exige el fallo — no basta con que
funcione sobre un árbol bueno.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from cosmos.abrir import NodoNoEncontrado, abrir, agua_que_moja, formatear, resolver
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


class AguaSeMojaPorFichero(unittest.TestCase):
    """F10: el filtro por nicho devolvia TODA el agua para cualquier nodo.

    `moja` es un glob de ficheros. Filtrar por nicho con `nicho in str(moja)` acertaba
    siempre —todos los `moja` empiezan por `**/`— y volcaba los seis mares enteros en
    cada `abrir`. Estas pruebas exigen listas distintas y que ninguna traiga el cuerpo.
    """

    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.base = Path(self.tmp.name)
        _arbol_minimo(self.base)
        _escribir(self.base, "agua/mar-pruebas.md",
                  {"cosmos": "mar", "nombre": "pruebas",
                   "moja": '["**/tests/**", "**/*_test.*"]',
                   "resumen": "Un test afirma lo medido, no lo deseado."},
                  "Cuerpo largo del mar de pruebas que no debe volcarse al abrir.")
        _escribir(self.base, "agua/mar-accesibilidad.md",
                  {"cosmos": "mar", "nombre": "accesibilidad",
                   "moja": '["**/*.html", "**/*.css"]',
                   "resumen": "Lo que no se puede usar con teclado no esta terminado."},
                  "Cuerpo del mar de accesibilidad.")
        _escribir(self.base, "agua/oceano-verificar.md",
                  {"cosmos": "oceano", "nombre": "verificar", "moja": '["**"]',
                   "resumen": "Nada esta hecho hasta que se ha visto funcionar."},
                  "Cuerpo del oceano.")
        self.arbol = cargar_arbol(self.base)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_dos_ficheros_distintos_traen_agua_distinta(self) -> None:
        html = [n.nombre for n in agua_que_moja(self.arbol, "publico/index.html")]
        prueba = [n.nombre for n in agua_que_moja(self.arbol, "tests/test_pago.py")]
        self.assertEqual(html, ["accesibilidad"])
        self.assertEqual(prueba, ["pruebas"])
        self.assertNotEqual(html, prueba)

    def test_sin_fichero_no_hay_agua(self) -> None:
        """Adivinar que se toca es indistinguible de devolverlo todo."""

        self.assertEqual(agua_que_moja(self.arbol, None), [])
        self.assertEqual(abrir(self.arbol, "web").agua, [])

    def test_el_oceano_no_se_lista_aunque_moje_todo(self) -> None:
        nombres = [n.nombre for n in agua_que_moja(self.arbol, "cualquier/cosa.html")]
        self.assertNotIn("verificar", nombres)

    def test_el_agua_se_nombra_pero_no_se_carga(self) -> None:
        """GOAL §2: describir a un nodo es una cosa; verter su cuerpo es otra."""

        salida = formatear(abrir(self.arbol, "web", tocando="publico/index.html"))
        self.assertIn("mar/accesibilidad", salida)
        self.assertIn("no se puede usar con teclado", salida)
        self.assertNotIn("Cuerpo del mar de accesibilidad", salida)


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

    def test_la_estrella_no_se_engancha_por_nombre_suelto(self) -> None:
        """F22: `ilumina` lleva la ruta completa, y solo la ruta completa la empareja.

        Dos paises llamados `pagos` bajo padres distintos y una estrella que dice
        iluminar `pagos`, a secas. Eso no nombra a ninguno de los dos: aceptarlo
        engancharia la misma estrella a los dos nodos, que es la colision que NUCLEO §1
        cerro exigiendo la ruta completa. La estrella escrita bien —`ilumina: web/pagos`—
        sigue llegando a su nodo y solo a el.
        """

        _escribir(self.base, "sistemas/otro.md",
                  {"cosmos": "sistema-solar", "nombre": "otro", "padre": '""',
                   "resumen": "Otro oficio cualquiera."})
        _escribir(self.base, "paises/otro--pagos.md",
                  {"cosmos": "pais", "nombre": "pagos", "padre": "otro",
                   "resumen": "Un pais homonimo bajo otro padre."})
        _escribir(self.base, "estrellas/suelta.md",
                  {"cosmos": "estrella", "nombre": "suelta", "ilumina": "pagos",
                   "resumen": "Estrella mal escrita: no dice de que pagos habla."},
                  "No se guarda el numero de tarjeta.")
        arbol = cargar_arbol(self.base)

        self.assertIsNone(abrir(arbol, "web/pagos").estrella)
        self.assertIsNone(abrir(arbol, "otro/pagos").estrella)

    def test_la_estrella_con_ruta_completa_llega_a_su_nodo_y_solo_a_el(self) -> None:
        _escribir(self.base, "sistemas/otro.md",
                  {"cosmos": "sistema-solar", "nombre": "otro", "padre": '""',
                   "resumen": "Otro oficio cualquiera."})
        _escribir(self.base, "paises/otro--pagos.md",
                  {"cosmos": "pais", "nombre": "pagos", "padre": "otro",
                   "resumen": "Un pais homonimo bajo otro padre."})
        _escribir(self.base, "estrellas/pagos.md",
                  {"cosmos": "estrella", "nombre": "pagos", "ilumina": "web/pagos",
                   "resumen": "Lo cierto al cobrar."},
                  "Nunca se guarda el numero de tarjeta.")
        arbol = cargar_arbol(self.base)

        self.assertIsNotNone(abrir(arbol, "web/pagos").estrella)
        self.assertIsNone(abrir(arbol, "otro/pagos").estrella)

    def test_arbol_vacio_no_revienta(self) -> None:
        with TemporaryDirectory() as vacio:
            arbol = cargar_arbol(Path(vacio))
            with self.assertRaises(NodoNoEncontrado):
                resolver(arbol, "lo-que-sea")


if __name__ == "__main__":
    unittest.main()
