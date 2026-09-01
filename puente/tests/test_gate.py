"""El gate verifica la instantánea del índice, no lo que casualmente hay en disco."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from puente import gate


def _repo(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "--quiet"], cwd=base, check=True)
    subprocess.run(["git", "config", "user.email", "puente@example.invalid"], cwd=base, check=True)
    subprocess.run(["git", "config", "user.name", "puente"], cwd=base, check=True)
    return base.resolve()


def _comprobacion(esperado: str) -> list[list[str]]:
    programa = (
        "import sys, pathlib;"
        f"sys.exit(0 if pathlib.Path('fichero.txt').read_text().strip() == {esperado!r} else 1)"
    )
    return [[sys.executable, "-c", programa]]


class Instantanea(unittest.TestCase):
    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="puente-gate-")
        self.repo = _repo(Path(self.temporal.name) / "repo")
        (self.repo / "fichero.txt").write_text("INDICE\n", encoding="utf-8")
        subprocess.run(["git", "add", "fichero.txt"], cwd=self.repo, check=True)
        (self.repo / "fichero.txt").write_text("SUCIO\n", encoding="utf-8")
        self.ordenes = gate._ordenes

    def tearDown(self) -> None:
        gate._ordenes = self.ordenes
        self.temporal.cleanup()

    def test_verifica_lo_que_esta_en_el_indice(self) -> None:
        gate._ordenes = lambda *_: _comprobacion("INDICE")
        self.assertEqual(gate.verificar_instantanea(silencioso=True, raiz=self.repo), 0)

    def test_no_verifica_el_arbol_de_trabajo_sucio(self) -> None:
        gate._ordenes = lambda *_: _comprobacion("SUCIO")
        self.assertEqual(gate.verificar_instantanea(silencioso=True, raiz=self.repo), 1)

    def test_un_fichero_borrado_del_disco_sigue_en_la_instantanea(self) -> None:
        (self.repo / "fichero.txt").unlink()
        gate._ordenes = lambda *_: _comprobacion("INDICE")
        self.assertEqual(gate.verificar_instantanea(silencioso=True, raiz=self.repo), 0)


class Entorno(unittest.TestCase):
    def test_el_entorno_aislado_no_lleva_variables_de_git(self) -> None:
        anterior = dict(os.environ)
        os.environ["GIT_DIR"] = "/tmp/otro/.git"
        os.environ["GIT_INDEX_FILE"] = "/tmp/otro/.git/index"
        os.environ["COSMOS_NICHOS"] = "web"
        try:
            aislado = gate.entorno_aislado()
            origen = gate.entorno_de_origen()
        finally:
            os.environ.clear()
            os.environ.update(anterior)
        self.assertFalse([clave for clave in aislado if clave.startswith("GIT_")])
        self.assertNotIn("COSMOS_NICHOS", aislado)
        self.assertEqual(list(clave for clave in origen if clave.startswith("GIT_")), ["GIT_INDEX_FILE"])
        self.assertEqual(origen["PYTHONDONTWRITEBYTECODE"], "1")


if __name__ == "__main__":
    unittest.main()
