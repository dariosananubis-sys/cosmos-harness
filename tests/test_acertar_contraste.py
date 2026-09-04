"""La métrica se vigila a sí misma: quien la mira mientras trabaja la deforma.

`acertar` nació para que abaratar el árbol no saliera gratis. Pero una métrica que se
consulta mientras se retocan los resúmenes deja de medir el árbol y empieza a medir la
puntería sobre sus propias preguntas — el mismo Goodhart que vino a evitar, un piso más
arriba. Medido en el árbol real: los cambios de una tarde subieron 18 puntos el conjunto
que se miraba y 5 el que no.

De ahí el contraste. Estas pruebas exigen que la cifra publicada sea la del conjunto que
no guía decisiones, y que el aviso salte cuando las dos se separan.
"""

from __future__ import annotations

import unittest

from cosmos.acertar import Contraste, Encargo, Puntuacion, Resultado, formatear_contraste
from cosmos.holdout import Procedencia

# Un contraste «sano»: sellado y con procedencia limpia. Desde la auditoría B (2026-09-03)
# una cifra sin sello o sin procedencia comprobada no se publica, así que las pruebas que
# afirman «la cifra que vale» parten de aquí.
SANO = dict(sellado=True, procedencia=Procedencia(True, (), 1, "1 blob; 0 coincidencias"))


def _puntuacion(aciertos: int, total: int) -> Puntuacion:
    resultados = [
        Resultado(
            encargo=Encargo(peticion=f"p{i}", espera="x"),
            elegida="x" if i < aciertos else "otro",
            posicion=1 if i < aciertos else 4,
            acierta=i < aciertos,
        )
        for i in range(total)
    ]
    return Puntuacion(resultados=resultados)


class LaCifraQueSePublica(unittest.TestCase):
    def test_la_que_vale_es_la_de_validacion(self) -> None:
        c = Contraste(ajuste=_puntuacion(33, 50), validacion=_puntuacion(10, 20), **SANO)
        salida = formatear_contraste(c)
        self.assertIn("Cifra íntegra: 50 %", salida)
        self.assertIn("NO ATRIBUIBLE", salida)
        self.assertNotIn("La cifra que vale", salida)

    def test_una_brecha_grande_se_denuncia_en_la_salida(self) -> None:
        c = Contraste(ajuste=_puntuacion(33, 50), validacion=_puntuacion(10, 20), **SANO)
        self.assertAlmostEqual(c.brecha, 16.0)
        self.assertIn("puntería sobre", formatear_contraste(c))

    def test_sin_brecha_se_dice_que_generaliza(self) -> None:
        c = Contraste(ajuste=_puntuacion(30, 50), validacion=_puntuacion(12, 20), **SANO)
        self.assertIn("generaliza", formatear_contraste(c))
        self.assertNotIn("puntería sobre", formatear_contraste(c))

    def test_sin_conjunto_de_validacion_no_se_inventa_una_brecha(self) -> None:
        c = Contraste(ajuste=_puntuacion(33, 50), validacion=None)
        self.assertIsNone(c.brecha)
        self.assertIsNone(c.como_dict()["cifra_no_atribuible"])


class UnHoldoutEsDeUnSoloUso(unittest.TestCase):
    """Lo encontró el revisor adversarial, y tenía razón: el conjunto se quemó el mismo día.

    Basta abrir su `--detalle` una vez y escribir hacia lo que falla. Medido después: de
    las 37 palabras nuevas que entraron en los resúmenes, seis existen SOLO en el holdout
    (`iphone`, `android`, `solidity`, `chatgpt`, `cookies`, `placas`). Son mejoras buenas
    por sí mismas y aun así invalidan la cifra: mide un examen visto.
    """

    def test_un_conjunto_quemado_no_da_cifra(self) -> None:
        c = Contraste(
            ajuste=_puntuacion(33, 50),
            validacion=_puntuacion(15, 20),
            quemado="2026-09-02 · se miró su detalle antes de reescribir los resúmenes",
        )
        self.assertIsNone(c.como_dict()["cifra_no_atribuible"])
        salida = formatear_contraste(c)
        self.assertIn("DESCONOCIDA", salida)
        self.assertNotIn("La cifra que vale es", salida)

    def test_sin_quemar_sigue_publicandola(self) -> None:
        c = Contraste(ajuste=_puntuacion(33, 50), validacion=_puntuacion(15, 20), **SANO)
        self.assertEqual(c.como_dict()["cifra_no_atribuible"], 75.0)
        self.assertIn("Cifra íntegra: 75 %", formatear_contraste(c))


class ElContrasteEnJson(unittest.TestCase):
    def test_publica_la_brecha_y_la_cifra_no_atribuible(self) -> None:
        d = Contraste(ajuste=_puntuacion(33, 50), validacion=_puntuacion(10, 20), **SANO).como_dict()
        self.assertAlmostEqual(d["brecha_puntos"], 16.0)
        self.assertEqual(d["cifra_no_atribuible"], 50.0)
        self.assertTrue(d["integra"])
        self.assertEqual(d["motivos_no_integra"], [])
        self.assertIs(d["atribuible"], False, "ninguna cifra es atribuible mientras el examen lo escriba quien lee el árbol")

    def test_sin_sello_ni_procedencia_no_hay_cifra(self) -> None:
        d = Contraste(ajuste=_puntuacion(33, 50), validacion=_puntuacion(10, 20)).como_dict()
        self.assertIsNone(d["cifra_no_atribuible"])
        self.assertFalse(d["integra"])


if __name__ == "__main__":
    unittest.main()
