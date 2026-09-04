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




class ElCanarioDeVaciadoDeResumen(unittest.TestCase):
    """B-01: reescribir los resúmenes con las palabras del examen dejó todo en verde y la
    contra-métrica en 100 %. Ninguna invariante mira la diferencia con HEAD; el gate sí."""

    NODO = "---\ncosmos: pueblo\nnombre: nuclei\npadre: web\nresumen: {resumen}\n---\n\nCuerpo.\n"
    ORIGINAL = "Escanea vulnerabilidades web con plantillas mantenidas por la comunidad, rapido y sin agente."

    def _repo_con_nodo(self, base: Path) -> Path:
        repo = _repo(base)
        (repo / "nuclei.md").write_text(self.NODO.format(resumen=self.ORIGINAL), encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "base"], cwd=repo, check=True)
        return repo

    def _reescribir(self, repo: Path, resumen: str) -> None:
        (repo / "nuclei.md").write_text(self.NODO.format(resumen=resumen), encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)

    def test_un_resumen_vaciado_se_denuncia(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_con_nodo(Path(tmp))
            self._reescribir(repo, "auditar seguridad web.")
            hallazgos = gate.resumenes_vaciados(repo)
            self.assertEqual(len(hallazgos), 1, hallazgos)
            self.assertIn("nuclei.md", hallazgos[0])
            self.assertEqual(gate.comprobar_vaciado(repo), 1)

    def test_una_mejora_que_conserva_los_terminos_pasa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_con_nodo(Path(tmp))
            self._reescribir(repo, self.ORIGINAL.replace("rapido", "rapido y en paralelo"))
            self.assertEqual(gate.resumenes_vaciados(repo), [])
            self.assertEqual(gate.comprobar_vaciado(repo), 0)

    def test_la_valvula_p01_abre_y_lo_dice(self) -> None:
        from datetime import timedelta

        from cosmos.guardarrailes import registrar_salto, ruta_saltos

        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_con_nodo(Path(tmp))
            self._reescribir(repo, "auditar seguridad web.")
            registrar_salto(ruta_saltos(repo), gate.CODIGO_VACIADO, "prueba: reescritura a propósito",
                            timedelta(days=1))
            self.assertEqual(gate.comprobar_vaciado(repo), 0)

    def test_un_fichero_sin_resumen_o_nuevo_no_cuenta(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_con_nodo(Path(tmp))
            (repo / "notas.md").write_text("sin frontmatter\n", encoding="utf-8")
            (repo / "nuevo.md").write_text(self.NODO.format(resumen="x"), encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
            self.assertEqual(gate.resumenes_vaciados(repo), [])

    def test_el_gate_entero_lo_bloquea(self) -> None:
        """No basta con que la función exista: `main` tiene que llamarla antes de la instantánea."""

        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_con_nodo(Path(tmp))
            self._reescribir(repo, "auditar seguridad web.")
            r = subprocess.run([sys.executable, "-m", "puente.gate", "--sin-pruebas"],
                               cwd=repo, capture_output=True, text=True,
                               env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parent.parent.parent)})
        self.assertEqual(r.returncode, 1)
        self.assertIn("resúmenes que se vacían", r.stderr)




class ElGateVigilaLasBajasYLaCopiaDelExamen(unittest.TestCase):
    """R-02: borrar 40 pueblos subía la nota y el margen con validar verde. R-14: añadir al resumen
    las palabras del examen que lo espera subía la validación sin vaciar nada."""

    PUEBLO = "---\ncosmos: pueblo\nnombre: {n}\npadre: web\nresumen: {r}\norigen: propio\n---\n\nCuerpo.\n\n```bash\nx\n```\n"

    def _repo(self, base: Path) -> Path:
        repo = _repo(base)
        (repo / "a.md").write_text(self.PUEBLO.format(n="alfa", r="Mide anchos reales sin opinar."), encoding="utf-8")
        (repo / "b.md").write_text(self.PUEBLO.format(n="beta", r="Recorta imagenes en lote."), encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "base"], cwd=repo, check=True)
        return repo

    def test_retirar_un_pueblo_se_bloquea_sin_valvula(self) -> None:
        from datetime import timedelta

        from cosmos.guardarrailes import registrar_salto, ruta_saltos

        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            subprocess.run(["git", "rm", "-q", "b.md"], cwd=repo, check=True)
            self.assertEqual(gate.pueblos_retirados(repo), ["b.md"])
            self.assertEqual(gate.comprobar_bajas(repo), 1)
            registrar_salto(ruta_saltos(repo), gate.CODIGO_BAJA, "prueba: retirada a propósito", timedelta(days=1))
            self.assertEqual(gate.comprobar_bajas(repo), 0)

    def test_borrar_un_md_que_no_es_pueblo_no_cuenta(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            (repo / "notas.md").write_text("sin frontmatter\n", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "--quiet", "-m", "notas"], cwd=repo, check=True)
            subprocess.run(["git", "rm", "-q", "notas.md"], cwd=repo, check=True)
            self.assertEqual(gate.pueblos_retirados(repo), [])

    def test_ganar_terminos_del_examen_que_espera_al_nodo_se_denuncia(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            holdout = Path(tmp) / "holdout.json"
            holdout.write_text('[{"peticion": "quiero saber el ancho exacto de cada elemento", "espera": "web/alfa"}]', encoding="utf-8")
            (repo / "a.md").write_text(self.PUEBLO.format(n="alfa", r="Mide anchos reales sin opinar: el ancho exacto de cada elemento."), encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
            hallazgos = gate.resumenes_calcados(repo, holdout)
            self.assertEqual(len(hallazgos), 1, hallazgos)
            self.assertIn("web/alfa", hallazgos[0])
            # y una mejora que no viene del examen pasa
            (repo / "a.md").write_text(self.PUEBLO.format(n="alfa", r="Mide anchos reales sin opinar, en varios navegadores."), encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
            self.assertEqual(gate.resumenes_calcados(repo, holdout), [])

    def test_el_gate_entero_bloquea_una_baja(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            subprocess.run(["git", "rm", "-q", "b.md"], cwd=repo, check=True)
            r = subprocess.run([sys.executable, "-m", "puente.gate", "--sin-pruebas"], cwd=repo, capture_output=True, text=True,
                               env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parent.parent.parent)})
        self.assertEqual(r.returncode, 1)
        self.assertIn("se retiran pueblos", r.stderr)

    def test_sin_holdout_la_guarda_de_ganancia_no_finge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            self.assertEqual(gate.resumenes_calcados(repo, Path(tmp) / "no-existe.json"), [])


if __name__ == "__main__":
    unittest.main()
