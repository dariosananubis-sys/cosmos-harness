"""El corredor de mutaciones no se fía del bytecode: cada mutación se compila desde el fuente."""

from __future__ import annotations

import importlib.util
import os
import py_compile
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from puente.tests import mutaciones


class ElCorredorNoReutilizaBytecodeRancio(unittest.TestCase):
    def test_una_mutacion_del_mismo_tamano_y_el_mismo_segundo_se_ejecuta_de_verdad(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mut-pyc-") as tmp:
            raiz = Path(tmp)
            modulo = raiz / "vigilado.py"
            modulo.write_text("VALOR = 1\n", encoding="utf-8")
            (raiz / "test_vigilado.py").write_text(
                "import unittest\nimport vigilado\n\n\nclass T(unittest.TestCase):\n"
                "    def test_mutado(self):\n        self.assertEqual(vigilado.VALOR, 2)\n",
                encoding="utf-8",
            )
            # El .pyc del VALOR = 1, escrito a propósito: el gate corre las suites sin escribir
            # bytecode, así que un `import` no lo dejaría y la carrera no se reproduciría.
            py_compile.compile(str(modulo), cfile=importlib.util.cache_from_source(str(modulo)), doraise=True)
            self.assertTrue(list(raiz.rglob("__pycache__")), "no se pudo escribir el bytecode rancio")
            antes = modulo.stat()
            # La «mutación»: mismo tamaño, misma fecha en segundos.
            modulo.write_text("VALOR = 2\n", encoding="utf-8")
            os.utime(modulo, ns=(antes.st_atime_ns, antes.st_mtime_ns))
            # Sin la purga, Python cree que el .pyc sigue siendo válido y la prueba ve VALOR = 1.
            rancio = subprocess.run([sys.executable, "-m", "unittest", "test_vigilado"], cwd=raiz, capture_output=True)
            self.assertNotEqual(rancio.returncode, 0, "el bytecode rancio no se reutilizó: la prueba no reproduce la carrera")
            self.assertEqual(mutaciones._ejecutar("test_vigilado", raiz), 0,
                             "el corredor sigue leyendo bytecode compilado antes de la mutación")
            self.assertFalse(list(raiz.rglob("__pycache__")), "el corredor volvió a escribir bytecode")


if __name__ == "__main__":
    unittest.main()
