from __future__ import annotations

import contextlib
import io
import re
import tempfile
import unittest
from pathlib import Path

from cosmos.cli import ejecutar
from cosmos.validar import rango_comprobado


REPO = Path(__file__).resolve().parents[1]
# El árbol de juguete tiene su propia configuración desde que `cosmos.toml` pasó a
# apuntar a la galaxia real: el comando por defecto tiene que mirar lo que importa.
CONFIG = REPO / "ejemplo.toml"


class PruebasCLI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # La vista plana es un artefacto generado y no se versiona: en un clon
        # limpio hay que arrancarla antes de validar. Es idempotente.
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(salida):
            codigo = ejecutar(["arrancar", "--config", str(CONFIG)])
        assert codigo == 0, salida.getvalue()

    def ejecutar(self, argumentos: list[str]) -> tuple[int, str]:
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(salida):
            codigo = ejecutar(argumentos)
        return codigo, salida.getvalue()

    def test_validar(self) -> None:
        codigo, salida = self.ejecutar(["validar", "--config", str(CONFIG)])
        self.assertEqual(0, codigo)
        self.assertIn("COSMOS  verde", salida)

    def test_medir(self) -> None:
        codigo, salida = self.ejecutar(["medir", "--config", str(CONFIG), "--metodo", "aprox"])
        self.assertEqual(0, codigo)
        self.assertIn("Fuera de COSMOS . no_medido", salida)

    def test_medir_nichos_repetidos_y_combinacion(self) -> None:
        codigo, salida = self.ejecutar(
            ["medir", "--config", str(CONFIG), "--nicho", "construccion", "--nicho", "analisis"]
        )
        self.assertEqual(0, codigo, salida)
        self.assertIn("Combinación", salida)
        self.assertIn("construccion, analisis", salida)

        codigo, salida = self.ejecutar(
            ["medir", "--config", str(CONFIG), "--combinacion", "construccion,analisis"]
        )
        self.assertEqual(0, codigo, salida)
        self.assertIn("construccion, analisis", salida)

    def test_generar(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            destino = Path(temporal) / "indice.md"
            codigo, salida = self.ejecutar(["generar", "--config", str(CONFIG), "--salida", str(destino)])
            self.assertEqual(0, codigo)
            self.assertTrue(destino.exists())
            self.assertIn("Índice escrito", salida)

    def test_mapa(self) -> None:
        codigo, salida = self.ejecutar(["mapa", "--config", str(CONFIG)])
        self.assertEqual(0, codigo)
        self.assertIn("galaxia/cosmos-ejemplo", salida)
        self.assertIn("Agua", salida)


class DocumentacionAlDia(unittest.TestCase):
    """F13 y F14: dos números escritos a mano que ya contradecían al árbol.

    La ayuda del CLI y el README decían «E00–E19» con E20 existiendo —y el desfase
    llevaba días anotado en un parte de commit sin cerrarse—, y `GOAL.md`, que es
    normativo (§0: «si algo del repo contradice este fichero, gana este fichero»),
    seguía diciendo 20 oficios contra los 21 del árbol: aplicando su propia regla,
    el oficio 21 era ilegal.

    La ayuda ya se genera desde `COMPROBACIONES`. El README no se puede generar, así
    que se ata; y de `GOAL.md` se quitó el número, que es una cosa menos que mantener.
    """

    def test_la_ayuda_del_cli_publica_el_rango_generado(self) -> None:
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), self.assertRaises(SystemExit):
            ejecutar(["--help"])
        self.assertIn(f"comprueba las invariantes {rango_comprobado()}", salida.getvalue())

    def test_el_readme_publica_el_mismo_rango_que_el_validador(self) -> None:
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        primero, ultimo = rango_comprobado().split("\u2013")
        self.assertIn(f"{primero}\u2013{ultimo}. Esquema", readme)
        self.assertIn(f"(`{primero}`..`{ultimo}`)", readme)

    def test_goal_no_repite_el_recuento_de_oficios(self) -> None:
        """Un número menos que mantener: el recuento lo dicta `spec/UNIVERSO.md`."""

        goal = (REPO / "GOAL.md").read_text(encoding="utf-8")
        sobran = re.findall(r"\b(?:\d+|[Vv]einte|[Vv]eintiun[ao]?)\s+oficios", goal)
        self.assertEqual([], sobran, f"GOAL.md vuelve a fijar el número de oficios: {sobran}")


if __name__ == "__main__":
    unittest.main()
