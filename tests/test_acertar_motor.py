"""La contra-métrica podía publicar cualquier número entre 0 y 100 sin que nada chillara.

Es la única cifra de calidad que tiene el proyecto — existe para que abaratar el árbol no
salga gratis— y no tenía ni una prueba de su motor. Un revisor lo demostró: sustituyendo
`_acierta` por `return True` el comando publica **100 %** y la suite entera sigue verde;
recortando `_lineas_del_catalogo` publica **0 %** y también.

Y ese segundo sabotaje no es hipotético: es **el fallo exacto que ya ocurrió**. La métrica
puntuaba sobre un recorte del árbol que se dejaba fuera los 21 oficios, y estuvo así hasta
que alguien lo miró a mano. Una regresión que ya pasó una vez y no tiene canario está
esperando a pasar otra.

Árbol de juguete, respuestas fijadas a mano, y una aserción por cada forma de romperlo.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from cosmos.acertar import Encargo, _normalizar, _ordenar, _raiz, puntuar
from cosmos.modelo import cargar_arbol


def _escribir(base: Path, ruta: str, campos: dict[str, str], cuerpo: str = "") -> None:
    destino = base / ruta
    destino.parent.mkdir(parents=True, exist_ok=True)
    cabecera = ["---"] + [f"{k}: {v}" for k, v in campos.items()] + ["---", ""]
    destino.write_text("\n".join(cabecera) + cuerpo + "\n", encoding="utf-8")


def _arbol_de_juguete(base: Path) -> None:
    _escribir(base, "galaxia.md", {"cosmos": "galaxia", "nombre": "t",
                                   "resumen": "Arbol de juguete."})
    _escribir(base, "sistemas/visibilidad.md",
              {"cosmos": "sistema-solar", "nombre": "visibilidad", "padre": '""',
               "resumen": "Que te encuentren en los buscadores."})
    _escribir(base, "sistemas/embebidos.md",
              {"cosmos": "sistema-solar", "nombre": "embebidos", "padre": '""',
               "resumen": "Placas, firmware y sensores de dispositivo."})
    _escribir(base, "paises/embebidos--firmware.md",
              {"cosmos": "pais", "nombre": "firmware", "padre": "embebidos",
               "resumen": "Lo que corre dentro de la placa."})
    _escribir(base, "pueblos/zephyr/SKILL.md",
              {"cosmos": "pueblo", "nombre": "zephyr", "padre": "embebidos/firmware",
               "resumen": "Tiempo real con cientos de placas soportadas."},
              "Cuerpo de la ficha.")


class ElMotorDeLaContraMetrica(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.base = Path(self.tmp.name)
        _arbol_de_juguete(self.base)
        self.arbol = cargar_arbol(self.base)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_un_encargo_que_solo_casa_con_el_oficio_lo_alcanza(self) -> None:
        """Canario del fallo real: los oficios viven en el índice, no en el catálogo.

        «buscadores» solo aparece en el resumen de `visibilidad`, que es un sistema solar.
        Si los candidatos vuelven a construirse sin ellos, esto se pone rojo.
        """

        p = puntuar(self.arbol, [Encargo(peticion="salir en los buscadores", espera="visibilidad")])
        self.assertTrue(p.resultados[0].acierta,
                        "la métrica volvió a puntuar sobre un recorte del árbol")

    def test_no_acierta_cuando_la_respuesta_correcta_no_es_la_primera(self) -> None:
        """Canario de `_acierta` -> True: si todo acierta, la cifra no significa nada."""

        p = puntuar(self.arbol, [Encargo(peticion="placas y firmware de dispositivo",
                                         espera="visibilidad")])
        self.assertFalse(p.resultados[0].acierta,
                         "la métrica da por bueno cualquier resultado")
        self.assertEqual(p.aciertos, 0)

    def test_bajar_de_mas_cuenta_como_acierto(self) -> None:
        """Llegar a la herramienta correcta por debajo del nodo esperado no es fallar."""

        p = puntuar(self.arbol, [Encargo(peticion="tiempo real en muchas placas",
                                         espera="embebidos")])
        self.assertTrue(p.resultados[0].acierta)
        self.assertTrue(p.resultados[0].elegida.startswith("embebidos"))

    def test_una_puntuacion_perfecta_y_una_nula_se_distinguen(self) -> None:
        encargos = [
            Encargo(peticion="salir en los buscadores", espera="visibilidad"),
            Encargo(peticion="tiempo real en muchas placas", espera="embebidos"),
        ]
        p = puntuar(self.arbol, encargos)
        self.assertEqual((p.aciertos, p.total), (2, 2))

        # Una consulta sin una sola palabra del catálogo. Medida: la primera versión de
        # esta prueba usaba «palabra que no existe en ningun resumen» y acertaba 1 de 1,
        # porque «resumen» sí está. Un caso negativo que no se comprueba no es negativo.
        imposibles = [Encargo(peticion="xkcdzz qqwerty", espera="visibilidad")]
        q = puntuar(self.arbol, imposibles)
        self.assertEqual(q.aciertos, 0)
        self.assertIsNone(q.resultados[0].posicion)


class ElRecorteDeSufijos(unittest.TestCase):
    """Canario del stemming: sin él, «encuentre» y «encuentren» son palabras distintas."""

    def test_las_formas_de_un_verbo_comparten_raiz(self) -> None:
        self.assertEqual(_raiz("encuentren"), _raiz("encuentre"))
        self.assertEqual(_normalizar("que google encuentre"), _normalizar("que google encuentren"))

    def test_no_funde_palabras_distintas_que_solo_se_parecen(self) -> None:
        """Conservador a propósito: la raíz nunca baja de cuatro letras.

        Escrito DESPUÉS de medir, no antes: `sitio` sí pierde su `-o` y queda en `siti`,
        que es correcto —cuatro letras— aunque la primera versión de esta prueba afirmaba
        lo contrario. Lo que importa no es que las palabras queden intactas, sino que dos
        que no son la misma no acaben siéndolo.
        """

        self.assertNotEqual(_raiz("casa"), _raiz("caso"))
        self.assertNotEqual(_raiz("placa"), _raiz("plaza"))
        for palabra in ("casa", "caso", "sitio", "placas"):
            with self.subTest(palabra):
                self.assertGreaterEqual(len(_raiz(palabra)), 4)

    def test_el_orden_de_los_resultados_no_es_arbitrario(self) -> None:
        candidatos = [("a", "placas firmware sensores"), ("b", "buscadores y contenido")]
        self.assertEqual(_ordenar("placas y firmware", candidatos)[0], "a")
        self.assertEqual(_ordenar("buscadores", candidatos)[0], "b")


class UnSoloNormalizador(unittest.TestCase):
    """A02: cuatro normalizadores, tres casi iguales, y una promesa a medias.

    `_ordenar` promete «la misma normalización que usa la búsqueda de memoria»
    (`puente/lluvia.normalizar`) y era una copia con destino a divergir. Ahora es la
    misma función por construcción; esto fija la propiedad para que una copia nueva
    que se desvíe —acentos, dígitos, palabras cortas— se ponga roja aquí.
    """

    def test_acertar_tokeniza_como_la_busqueda_de_memoria(self) -> None:
        from puente.lluvia import normalizar

        sondas = (
            "¡Que google me ENCUENTREN ya!",
            "e-mail número 42 ñu a b",
            "BÚSCA-me: acentos, guiones y MAYÚSCULAS",
        )
        for sonda in sondas:
            with self.subTest(sonda):
                self.assertEqual(_normalizar(sonda), [_raiz(p) for p in normalizar(sonda)])


class LosEncargosSeValidanEnElBorde(unittest.TestCase):
    """B09: `cosmos acertar` reventaba con traceback crudo en el caso de estreno.

    `rio/acertar` se anuncia en cualquier proyecto sobre el que se clone COSMOS, y en
    todos menos éste `pruebas/encargos.json` no existe: `FileNotFoundError` a la cara.
    El mismo cuidado que ya recibía `--validacion` (mensaje entero, salida 2), aplicado
    al fichero que sí se lee siempre. Medido antes de escribir cada aserción.
    """

    def test_el_estreno_no_es_un_traceback(self) -> None:
        from cosmos.acertar import ErrorEncargos, cargar_encargos

        with TemporaryDirectory() as tmp:
            with self.assertRaises(ErrorEncargos) as caso:
                cargar_encargos(Path(tmp, "encargos.json"))
        self.assertIn("no existe", str(caso.exception))
        self.assertIn("recién clonado", str(caso.exception),
                      "el mensaje tiene que decir que el estreno es lo esperable, no un fallo")

    def test_json_invalido_y_esquema_roto_explican_en_vez_de_reventar(self) -> None:
        from cosmos.acertar import ErrorEncargos, cargar_encargos

        casos = (
            ("no json", "no es JSON válido"),
            ("{}", "debe ser una lista"),
            ('[{"peticion": "x"}]', "necesita 'peticion' y 'espera'"),
            ('[{"peticion": "x", "espera": 3}]', "necesita 'peticion' y 'espera'"),
        )
        with TemporaryDirectory() as tmp:
            for contenido, fragmento in casos:
                with self.subTest(contenido):
                    ruta = Path(tmp, "encargos.json")
                    ruta.write_text(contenido, encoding="utf-8")
                    with self.assertRaises(ErrorEncargos) as caso:
                        cargar_encargos(ruta)
                    self.assertIn(fragmento, str(caso.exception))

    def test_por_cli_sale_2_con_mensaje_y_sin_traceback(self) -> None:
        import subprocess
        import sys

        raiz = Path(__file__).resolve().parent.parent
        with TemporaryDirectory() as tmp:
            r = subprocess.run(
                [sys.executable, "-m", "cosmos", "acertar", "--encargos", str(Path(tmp, "no-existe.json"))],
                capture_output=True, text=True, cwd=raiz,
            )
        self.assertEqual(r.returncode, 2, "el estreno no es un rojo de la métrica: es un error de uso")
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn("no existe", r.stderr)


if __name__ == "__main__":
    unittest.main()
