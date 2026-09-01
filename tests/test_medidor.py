from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cosmos import medir
from cosmos.modelo import Arbol, Nodo


class PruebasMedidor(unittest.TestCase):
    def test_arbol_de_tokens_conocidos_a_mano(self) -> None:
        nodo = Nodo(Path("galaxia.md"), "galaxia.md", {"cosmos": "galaxia", "nombre": "raiz", "resumen": "explica"}, {}, "alpha beta")
        resultado = medir.medir_arbol(Arbol(Path("."), [nodo]), metodo="aprox", indice="uno dos")
        self.assertEqual(2, resultado.entrada)
        self.assertEqual(2, resultado.arbol)
        self.assertEqual(0.0, resultado.descarga)

    def test_aproximado_y_exacto_respetan_margen_publicado(self) -> None:
        exacto = medir._contador_exacto()
        if exacto is None:
            self.skipTest("tokenizador exacto local no disponible; comparación declaradamente omitida")
        self.assertIsNotNone(medir.MARGEN_ERROR, "hay tokenizador exacto pero no existe margen publicado")
        corpus = "# Prueba\n\nTexto en castellano and English.\n\n```python\nprint('ok')\n```\n"
        esperado = exacto[0](corpus)
        aproximado = medir.contar_aprox(corpus)
        divergencia = abs(aproximado - esperado) / esperado
        self.assertLessEqual(divergencia, medir.MARGEN_ERROR)

    def test_no_medido_nunca_se_convierte_en_cero(self) -> None:
        resultado = medir.medir_arbol(Arbol(Path(".")), metodo="aprox", indice="")
        self.assertEqual("no_medido", resultado.fuera_cosmos)
        serializado = medir.medicion_json(resultado)
        self.assertIn('"fuera_cosmos": "no_medido"', serializado)
        self.assertNotIn('"fuera_cosmos": 0', serializado)

    def test_arbol_vacio_no_publica_descarga_perfecta(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            resultado = medir.medir_arbol(Arbol(Path(temporal)), metodo="aprox", indice="")
        self.assertEqual(0, resultado.entrada)
        self.assertEqual(0, resultado.arbol)
        self.assertEqual("no_definida", resultado.descarga)


if __name__ == "__main__":
    unittest.main()
