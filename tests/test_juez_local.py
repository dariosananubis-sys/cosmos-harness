"""El juez con modelo, ejercitado sin modelo: se dobla el transporte, no el juicio.

En esta máquina no se levanta ningún modelo (y el módulo, por diseño, jamás arranca
uno: se conecta o falla limpio). Lo que sí se ejercita entero es todo lo demás —
prompt, extracción de ruta del ruido, puntuación con el mismo `_acierta` de la
contra-métrica— doblando el borde más externo: la función de transporte. Doblar más
adentro obligaría a mantener a mano el contrato del servidor, que es el antipatrón
que `mar/pruebas` prohíbe.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from cosmos.acertar import Encargo
from cosmos.juez import ErrorJuez, extraer_ruta, juzgar
from cosmos.modelo import cargar_arbol

RAIZ = Path(__file__).resolve().parent.parent
ARBOL = cargar_arbol(RAIZ / "galaxia")


class LaRutaSeExtraeDelRuido(unittest.TestCase):
    RUTAS = ["web", "web/tienda", "trading", "rendimiento/perfilado"]

    def test_encuentra_la_ruta_aunque_venga_envuelta(self) -> None:
        self.assertEqual(extraer_ruta("La ruta es `web/tienda`.", self.RUTAS), "web/tienda")

    def test_si_nombra_varias_gana_la_mas_larga(self) -> None:
        # «web/tienda» contiene «web»: contestar la hoja no puede puntuarse como la raíz.
        self.assertEqual(extraer_ruta("web/tienda (dentro de web)", self.RUTAS), "web/tienda")

    def test_sin_candidato_es_none_y_nunca_un_acierto_por_defecto(self) -> None:
        self.assertIsNone(extraer_ruta("no tengo ni idea", self.RUTAS))


class ElJuicioUsaElMismoAcierta(unittest.TestCase):
    def test_juzga_con_transporte_doblado(self) -> None:
        encargos = [
            Encargo(peticion="que google encuentre mi tienda", espera="visibilidad"),
            Encargo(peticion="un bot que opere solo", espera="trading"),
        ]
        respuestas = iter(["Iría a `visibilidad`, sin duda.", "ninguna me convence"])
        p = juzgar(ARBOL, encargos, modelo="doblado", preguntar=lambda _: next(respuestas))
        self.assertEqual((p.aciertos, p.total), (1, 2))
        self.assertTrue(p.resultados[0].acierta)
        self.assertFalse(p.resultados[1].acierta, "una respuesta sin ruta contó como acierto")

    def test_bajar_de_mas_tambien_vale_para_el_juez(self) -> None:
        p = juzgar(ARBOL, [Encargo(peticion="x", espera="rendimiento")],
                   modelo="doblado", preguntar=lambda _: "rendimiento/perfilado")
        self.assertTrue(p.resultados[0].acierta)

    def test_sin_servidor_falla_limpio(self) -> None:
        with self.assertRaises(ErrorJuez) as caso:
            juzgar(ARBOL, [Encargo(peticion="x", espera="web")],
                   modelo="nadie", servidor="http://127.0.0.1:9")  # puerto discard: nunca abierto
        self.assertIn("no arranca", str(caso.exception))


class ElCliDelJuez(unittest.TestCase):
    def test_sin_servidor_sale_2_con_mensaje_y_sin_traceback(self) -> None:
        r = subprocess.run(
            [sys.executable, "-m", "cosmos", "acertar", "--juez", "nadie",
             "--servidor", "http://127.0.0.1:9"],
            capture_output=True, text=True, cwd=RAIZ,
        )
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn("sin juez", r.stderr)


if __name__ == "__main__":
    unittest.main()
