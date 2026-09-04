"""El alta (`cosmos configurar`), de una sentada y sin dejar una clave dentro del repositorio."""

from __future__ import annotations

import os
import stat
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from cosmos import configurar as cfg
from cosmos.modelo import cargar_arbol

RAIZ = Path(__file__).resolve().parent.parent
ARBOL = cargar_arbol(RAIZ / "galaxia")


def _cosmos(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "cosmos", "configurar", *args], capture_output=True, text=True, cwd=RAIZ)


class ElAltaDeUnaSentada(unittest.TestCase):
    def test_primera_vuelta_comprobar_y_llavero_en_seco(self) -> None:
        with TemporaryDirectory() as tmp:
            d = Path(tmp) / "casa"
            r = _cosmos("--oficios", "agentes-ia", "--herramientas", "revision-cruzada", "--directorio", str(d), "--no-abrir")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("Oficios activos ....... agentes-ia (1 de", r.stdout)
            perfil, cred = d / "perfil.toml", d / "credenciales.txt"
            self.assertTrue(perfil.is_file() and cred.is_file())
            self.assertEqual(stat.S_IMODE(d.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(cred.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(perfil.stat().st_mode), 0o600)
            texto = cred.read_text(encoding="utf-8")
            self.assertIn("OPENROUTER_API_KEY=", texto, "la variable que pide la ficha tiene que estar, vacía")
            self.assertIn("# revision-cruzada:", texto, "y con la pista de dónde se saca")
            self.assertEqual(cfg.leer_perfil(perfil)["credenciales_comprobadas"], False)
            # segunda vuelta con el fichero aún vacío: dice qué falta y sale 1
            r = _cosmos("--comprobar", "--directorio", str(d))
            self.assertEqual(r.returncode, 1)
            self.assertIn("FALTA      OPENROUTER_API_KEY", r.stdout)
            # rellenado (valor de juguete, nunca real)
            cred.write_text(texto.replace("OPENROUTER_API_KEY=", "OPENROUTER_API_KEY=" + "sk-or-v1-" + "x" * 32), encoding="utf-8")
            r = _cosmos("--comprobar", "--directorio", str(d))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("no se vuelve a preguntar", r.stdout)
            self.assertEqual(cfg.leer_perfil(perfil)["credenciales_comprobadas"], True)
            # llavero en seco: la orden se enseña sin el valor, y el txt no se vacía
            r = _cosmos("--llavero", "--seco", "--directorio", str(d))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("security add-generic-password", r.stdout)
            self.assertIn("cosmos/OPENROUTER_API_KEY", r.stdout)
            self.assertNotIn("x" * 32, r.stdout, "el valor se imprimió")
            self.assertIn("x" * 32, cred.read_text(encoding="utf-8"))
            # y vaciar deja las líneas puestas y vacías
            self.assertEqual(cfg.vaciar_valores(cred), 1)
            self.assertIn("OPENROUTER_API_KEY=\n", cred.read_text(encoding="utf-8"))

    def test_un_marcador_es_sospechoso_y_no_se_da_por_bueno(self) -> None:
        faltan, sospechosas = cfg.comprobar_credenciales(
            [cfg.Credencial("X_TOKEN", "p", "x"), cfg.Credencial("Y_KEY", "p", "y"), cfg.Credencial("Z_PASS", "p", "z")],
            {"X_TOKEN": "<pon-aqui-tu-token>", "Y_KEY": "abcdefgh12345678", "Z_PASS": ""})
        self.assertEqual(faltan, ["Z_PASS"])
        self.assertEqual(sospechosas, ["X_TOKEN"])

    def test_una_herramienta_de_un_oficio_dormido_se_rechaza(self) -> None:
        with TemporaryDirectory() as tmp:
            r = _cosmos("--oficios", "juegos", "--herramientas", "revision-cruzada", "--directorio", str(Path(tmp) / "c"), "--no-abrir")
        self.assertEqual(r.returncode, 2)
        self.assertIn("no activaste", r.stderr)

    def test_no_pisa_un_fichero_con_valores(self) -> None:
        with TemporaryDirectory() as tmp:
            d = Path(tmp) / "c"
            cfg.escribir_privado(d / "credenciales.txt", "OPENROUTER_API_KEY=" + "y" * 20 + "\n")
            r = _cosmos("--oficios", "agentes-ia", "--herramientas", "revision-cruzada", "--directorio", str(d), "--no-abrir")
            self.assertEqual(r.returncode, 0)
            self.assertIn("no se sobrescribe", r.stdout)
            self.assertIn("y" * 20, (d / "credenciales.txt").read_text(encoding="utf-8"))

    def test_las_credenciales_no_pueden_entrar_en_el_repositorio(self) -> None:
        from puente.secretos import _hallazgos_de_ruta

        self.assertTrue(any("sensible" in h for h in _hallazgos_de_ruta(b"cualquier/credenciales.txt")))
        self.assertTrue(any("sensible" in h for h in _hallazgos_de_ruta(b"credenciales.copia.txt")))
        self.assertEqual([h for h in _hallazgos_de_ruta(b"docs/credenciales.plantilla.txt") if "sensible" in h], [])
        self.assertIn("credenciales.txt", (RAIZ / ".gitignore").read_text(encoding="utf-8"))
        self.assertNotIn("=", "".join(l for l in (RAIZ / "docs/credenciales.plantilla.txt").read_text(encoding="utf-8").splitlines() if not l.startswith("#")).strip(), "la plantilla del repo lleva una línea VARIABLE=")

    def test_detecta_las_variables_de_las_fichas(self) -> None:
        creds = cfg.credenciales_de(ARBOL, ["revision-cruzada", "toxiproxy"])
        self.assertEqual([c.variable for c in creds], ["OPENROUTER_API_KEY"])
        self.assertEqual(creds[0].pueblo, "revision-cruzada")


if __name__ == "__main__":
    unittest.main()
