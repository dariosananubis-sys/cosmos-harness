"""Canarios de la revisión de coherencia B (2026-09-04): lo que se arregló no puede volver a mentir.

Cada prueba ata un texto a la cosa que describe. Son baratas y se ponen rojas con el nombre del
fichero que se desincronizó, que es lo único que un canario tiene que hacer.
"""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

from cosmos.modelo import NIVELES_SOLIDOS, cargar_arbol

RAIZ = Path(__file__).resolve().parent.parent


class ElBloqueDeMedidorSeReproduce(unittest.TestCase):
    """B-04: la spec jura que su ejemplo se reproduce con `cosmos medir --config ejemplo.toml`, y no."""

    def test_el_bloque_de_la_spec_es_la_salida_del_comando(self) -> None:
        texto = (RAIZ / "spec/MEDIDOR.md").read_text(encoding="utf-8")
        bloque = re.search(r"```\n(COSMOS  medir\n.*?)```", texto, re.S)
        self.assertIsNotNone(bloque, "MEDIDOR.md ya no lleva el bloque de ejemplo")
        real = subprocess.run([sys.executable, "-m", "cosmos", "medir", "--config", "ejemplo.toml"],
                              capture_output=True, text=True, cwd=RAIZ).stdout
        # La línea «Vista compilada» lleva la ruta local del clon y depende de haber compilado
        # el ejemplo: es la única que no viaja en la spec, y se dice ahí.
        def sin_vista(t: str) -> list[str]:
            lineas = [l.rstrip() for l in t.rstrip().splitlines() if not l.startswith("  Vista compilada")]
            while lineas and not lineas[-1]:
                lineas.pop()
            return lineas

        self.assertEqual(sin_vista(bloque.group(1)), sin_vista(real),
                         "spec/MEDIDOR.md no es la salida de `cosmos medir --config ejemplo.toml`: regenérala")


class LaTablaDeNivelesDeGoalEsLaDelCodigo(unittest.TestCase):
    """B-12: GOAL declaraba un nivel `Universo` que el código nunca reconoció."""

    NOMBRES = {"Galaxia": "galaxia", "Sistema solar": "sistema-solar", "Planeta": "planeta", "Continente": "continente",
               "País": "pais", "Provincia": "provincia", "Pueblo": "pueblo"}

    def test_toda_fila_solida_es_un_nivel_valido(self) -> None:
        texto = (RAIZ / "GOAL.md").read_text(encoding="utf-8")
        tabla = texto[texto.index("### Sólido"):texto.index("### Agua")]
        filas = re.findall(r"^\| \*\*([^*]+)\*\* \|", tabla, re.M)
        solidos = [f for f in filas if f not in ("Estrella", "Luna")]
        for fila in solidos:
            with self.subTest(fila):
                self.assertIn(fila, self.NOMBRES, f"GOAL §3 declara un nivel que el código no tiene: {fila}")
                self.assertIn(self.NOMBRES[fila], NIVELES_SOLIDOS)
        self.assertEqual(len(solidos), len(NIVELES_SOLIDOS), "GOAL §3 y el código no tienen los mismos sólidos")


class LosEnganchesSonLosQueSeInstalan(unittest.TestCase):
    """B-16: `cosmos enganchar` instalaba un pre-push que ninguna spec ni el README nombraban."""

    def test_spec_readme_y_codigo_nombran_los_mismos(self) -> None:
        spec = (RAIZ / "spec/GUARDARRAILES.md").read_text(encoding="utf-8")
        bloque = spec[spec.index("## Los cuatro enganches"):][:1500]
        de_la_spec = set(re.findall(r"^\| \*\*([\w-]+)\*\* \|", bloque, re.M))
        self.assertEqual(de_la_spec, {"pre-commit", "pre-push", "sesión", "CI"})
        readme = (RAIZ / "README.md").read_text(encoding="utf-8")
        for enganche in ("pre-commit", "pre-push", "sesión"):
            self.assertIn(f"| {enganche}", readme.replace("| **sesión**", "| sesión"), f"el README no lista {enganche}")
        from cosmos.guardarrailes import contenido_hook, contenido_hook_push

        self.assertIn("puente.gate", contenido_hook())
        self.assertIn("puente.secretos", contenido_hook_push())


class LosResumenesVanEnAscii(unittest.TestCase):
    """B-29: 453 de 454 resúmenes sin acentos y uno con, en un océano. Ahora es E07 y esto lo mide."""

    def test_ningun_resumen_del_arbol_real_lleva_acentos(self) -> None:
        for raiz in (RAIZ / "galaxia", RAIZ / "ejemplo"):
            arbol = cargar_arbol(raiz, tambien=(RAIZ / "registro",) if raiz.name == "galaxia" else ())
            for nodo in arbol.nodos:
                with self.subTest(nodo.ruta_relativa):
                    self.assertTrue((nodo.resumen or "").isascii(), nodo.resumen)


class LaAyudaNoEnsenaCifrasAMano(unittest.TestCase):
    """B-38: `mapa` decía «~3.700 tokens, el 90 %» escrito a mano."""

    def test_mapa_no_lleva_numero(self) -> None:
        ayuda = subprocess.run([sys.executable, "-m", "cosmos", "--help"], capture_output=True, text=True, cwd=RAIZ).stdout
        linea = ayuda[ayuda.index("mapa"):ayuda.index("proyectar")]
        self.assertIsNone(re.search(r"\d\.\d{3}|\d+ ?%", linea), "la ayuda de mapa vuelve a llevar una cifra a mano")

    def test_version(self) -> None:
        from cosmos import __version__

        r = subprocess.run([sys.executable, "-m", "cosmos", "--version"], capture_output=True, text=True, cwd=RAIZ)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), f"cosmos {__version__}")
        pyproject = (RAIZ / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn(f'version = "{__version__}"', pyproject, "pyproject.toml y cosmos/__init__.py no dicen la misma versión")


class ElAbrirSugiereLaRutaCompleta(unittest.TestCase):
    """B-28: el ejemplo de la ayuda fallaba y el error no decía qué hacer."""

    def test_una_ruta_corta_sugiere_la_larga_y_el_verbo_de_busqueda(self) -> None:
        r = subprocess.run([sys.executable, "-m", "cosmos", "abrir", "trading/backtesting"], capture_output=True, text=True, cwd=RAIZ)
        self.assertEqual(r.returncode, 1)
        self.assertIn("trading/estrategia/backtesting", r.stderr)
        self.assertIn("cosmos buscar", r.stderr)

    def test_el_ejemplo_de_la_ayuda_funciona(self) -> None:
        ayuda = subprocess.run([sys.executable, "-m", "cosmos", "abrir", "--help"], capture_output=True, text=True, cwd=RAIZ).stdout
        ejemplo = re.search(r"p\.ej\.\s+'([^']+)'", ayuda)
        self.assertIsNotNone(ejemplo)
        r = subprocess.run([sys.executable, "-m", "cosmos", "abrir", ejemplo.group(1)], capture_output=True, text=True, cwd=RAIZ)
        self.assertEqual(r.returncode, 0, r.stderr)


class ElCiCorreLasMutaciones(unittest.TestCase):
    """B-03: el README vendía las mutaciones como la garantía y el CI no las ejecutaba."""

    def test_el_workflow_ejecuta_mutaciones_y_una_matriz(self) -> None:
        ci = (RAIZ / ".github/workflows/cosmos.yml").read_text(encoding="utf-8")
        self.assertIn("python3 -m puente.tests.mutaciones", ci)
        self.assertIn('"3.11"', ci, "el CI no cubre la versión mínima que el repo exige")
        self.assertIn("macos-latest", ci)


class LosDocumentosHistoricosLoDicen(unittest.TestCase):
    """B-22 / B-23: un plan superado en la raíz y un archivo de barridos sin cartel."""

    def test_plan_maestro_y_research_se_declaran_historicos(self) -> None:
        self.assertIn("Histórico", (RAIZ / "PLAN-MAESTRO.md").read_text(encoding="utf-8")[:600])
        self.assertIn("congelado", (RAIZ / "research/README.md").read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()
