from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from cosmos.cli import ejecutar


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


if __name__ == "__main__":
    unittest.main()
