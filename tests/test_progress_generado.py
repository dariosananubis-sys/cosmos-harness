"""`PROGRESS.md` jura que sus cifras son la salida de `cosmos estado`: se comprueba, no se cree.

Revisión R-19: la cabecera decía «las cifras de abajo no se escriben a mano» y diez de ellas
estaban caducadas; el canario solo hacía `grep ciudad`. Este reejecuta el comando y compara el
bloque, como `LaCabeceraDelIndiceSeCuentaNoSeEscribe` hace con el índice. Regenerar:
    python3 -m cosmos estado > /tmp/estado.txt   (y pegarlo en el bloque ```text de PROGRESS.md)
o `python3 tools/regenerar_progress.py` si existe.
"""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


class ElBloqueDeEstadoEsLaSalidaDelComando(unittest.TestCase):
    def test_el_bloque_coincide_con_cosmos_estado(self) -> None:
        texto = (RAIZ / "PROGRESS.md").read_text(encoding="utf-8")
        bloque = re.search(r"```text\n(COSMOS  estado\n.*?)```", texto, re.S)
        self.assertIsNotNone(bloque, "PROGRESS.md ya no lleva el bloque generado de `cosmos estado`")
        real = subprocess.run([sys.executable, "-m", "cosmos", "estado"], capture_output=True, text=True, cwd=RAIZ).stdout
        self.assertEqual(bloque.group(1).rstrip(), real.rstrip(),
                         "PROGRESS.md dice ser la salida de `cosmos estado` y no lo es: regenéralo")

    def test_la_cabecera_no_promete_lo_que_no_cumple(self) -> None:
        texto = (RAIZ / "PROGRESS.md").read_text(encoding="utf-8")
        self.assertIn("no se escriben a mano", texto)
        self.assertIn("test_progress_generado", texto, "la cabecera tiene que decir qué canario lo vigila")


if __name__ == "__main__":
    unittest.main()
