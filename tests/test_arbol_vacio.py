"""Un árbol vacío es COSMOS recién clonado sobre un proyecto nuevo, y los verbos discrepaban.

Auditoría D-03 / E-09: `cosmos medir` decía «SIN MEDIR» y salía 1 (correcto), mientras
`cosmos validar` afirmaba «0 tokens > 4000; excede en -4000 tokens» — un `None` que ya
estaba modelado (`Veredicto.cabe` es trivalente) y se aplastaba al cruzar de módulo. Es
exactamente el patrón que el repositorio existe para perseguir: «no medido» convertido
en un número. Ninguna prueba cruzaba los dos verbos sobre el mismo árbol vacío.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

RAIZ = Path(__file__).resolve().parent.parent


def _config_vacia(directorio: Path) -> Path:
    (directorio / "arbol").mkdir()
    config = directorio / "cosmos.toml"
    config.write_text(
        (RAIZ / "cosmos.toml").read_text(encoding="utf-8")
        .replace('arbol = "galaxia"', 'arbol = "arbol"')
        .replace('indice = "galaxia/COSMOS.md"', 'indice = "arbol/COSMOS.md"')
        .replace('registro = "registro"', ""),
        encoding="utf-8",
    )
    return config


def _cosmos(*args: str, config: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "cosmos", *args, "--config", str(config)],
                          capture_output=True, text=True, cwd=RAIZ)


class LosDosVerbosDicenLoMismoSobreNada(unittest.TestCase):
    def test_validar_no_inventa_un_exceso_negativo(self) -> None:
        with TemporaryDirectory() as tmp:
            r = _cosmos("validar", config=_config_vacia(Path(tmp)))
        self.assertEqual(r.returncode, 1, "un árbol sin galaxia no puede estar en verde")
        self.assertIn("E05", r.stdout, "la ausencia de galaxia es el error que tiene sentido")
        self.assertNotIn("E16", r.stdout, "E16 volvió a hablar sobre un árbol que no midió")
        self.assertNotIn("excede en -", r.stdout)
        self.assertNotIn("0 tokens > ", r.stdout)

    def test_medir_dice_sin_medir_y_sale_1(self) -> None:
        with TemporaryDirectory() as tmp:
            r = _cosmos("medir", config=_config_vacia(Path(tmp)))
        self.assertEqual(r.returncode, 1)
        self.assertIn("SIN MEDIR", r.stdout)




class R06_ElMensajeDeE16ComparaLoMismoQueElVeredicto(unittest.TestCase):
    """Con el presupuesto por debajo de la estimación+margen, el mensaje decía «3715 > 3800; excede
    en -85» mientras `medir` decía «excede en 109» sobre el mismo hecho."""

    def test_sin_exceso_negativo_y_con_el_margen_a_la_vista(self) -> None:
        import re

        with TemporaryDirectory() as tmp:
            config = Path(tmp) / "cosmos.toml"
            texto = (RAIZ / "cosmos.toml").read_text(encoding="utf-8")
            texto = texto.replace('arbol = "galaxia"', f'arbol = "{RAIZ}/galaxia"').replace('indice = "galaxia/COSMOS.md"', f'indice = "{RAIZ}/galaxia/COSMOS.md"').replace('registro = "registro"', f'registro = "{RAIZ}/registro"')
            texto = re.sub(r"^entrada = \d+", "entrada = 3800", texto, count=1, flags=re.M)
            config.write_text(texto, encoding="utf-8")
            r = _cosmos("validar", config=config)
            m = _cosmos("medir", config=config)
        self.assertEqual(r.returncode, 1)
        self.assertIn("E16", r.stdout)
        self.assertNotIn("excede en -", r.stdout, "volvió el exceso negativo")
        self.assertIn("margen calibrado", r.stdout)
        exceso_validar = re.search(r"excede en (\d+) tokens", r.stdout)
        exceso_medir = re.search(r"excede en (\d+) tokens", m.stdout)
        self.assertIsNotNone(exceso_validar); self.assertIsNotNone(exceso_medir)
        self.assertEqual(exceso_validar.group(1), exceso_medir.group(1), "validar y medir publican excesos distintos para el mismo hecho")


if __name__ == "__main__":
    unittest.main()
