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
        c = Contraste(ajuste=_puntuacion(33, 50), validacion=_puntuacion(10, 20))
        salida = formatear_contraste(c)
        self.assertIn("La cifra que vale es 50 %", salida)

    def test_una_brecha_grande_se_denuncia_en_la_salida(self) -> None:
        c = Contraste(ajuste=_puntuacion(33, 50), validacion=_puntuacion(10, 20))
        self.assertAlmostEqual(c.brecha, 16.0)
        self.assertIn("puntería sobre", formatear_contraste(c))

    def test_sin_brecha_se_dice_que_generaliza(self) -> None:
        c = Contraste(ajuste=_puntuacion(30, 50), validacion=_puntuacion(12, 20))
        self.assertIn("generaliza", formatear_contraste(c))
        self.assertNotIn("puntería sobre", formatear_contraste(c))

    def test_sin_conjunto_de_validacion_no_se_inventa_una_brecha(self) -> None:
        c = Contraste(ajuste=_puntuacion(33, 50), validacion=None)
        self.assertIsNone(c.brecha)
        self.assertIsNone(c.como_dict()["cifra_honesta"])


class ElContrasteEnJson(unittest.TestCase):
    def test_publica_la_brecha_y_la_cifra_honesta(self) -> None:
        d = Contraste(ajuste=_puntuacion(33, 50), validacion=_puntuacion(10, 20)).como_dict()
        self.assertAlmostEqual(d["brecha_puntos"], 16.0)
        self.assertEqual(d["cifra_honesta"], 50.0)


if __name__ == "__main__":
    unittest.main()
