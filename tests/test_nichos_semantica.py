"""`nichos=None` significa dos cosas opuestas, y las dos se fijan aquí a la vez.

Auditoría A-04: NUCLEO §2 dice que «sin selección» el catálogo no lleva ningún pueblo;
NUCLEO §5 dice que `compilar` sin selección aplana la vista completa; y `cosmos.toml`
documentaba «lista vacía = todos» para las dos. Cada subsistema tenía sus pruebas por
separado y por eso la divergencia nunca salió en rojo. Esta prueba las cruza: cambiar
una semántica sin cambiar la otra —y sin tocar NUCLEO— se ve.
"""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from cosmos.compilar import _skills
from cosmos.medir import nodos_de_catalogo
from cosmos.modelo import cargar_arbol, cargar_configuracion, nombres_nichos

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = cargar_configuracion(RAIZ / "cosmos.toml")
ARBOL = cargar_arbol(CONFIG.arbol, tambien=(CONFIG.registro,) if CONFIG.registro else ())


def _config_compilacion(directorio: Path, modo: str = "symlink") -> Path:
    """Config sobre la galaxia real, con destino y manifiesto de la vista en el temporal."""

    config = directorio / "cosmos.toml"
    config.write_text(
        (RAIZ / "cosmos.toml").read_text(encoding="utf-8")
        .replace('arbol = "galaxia"', f'arbol = "{RAIZ}/galaxia"')
        .replace('indice = "galaxia/COSMOS.md"', f'indice = "{RAIZ}/galaxia/COSMOS.md"')
        .replace('registro = "registro"', f'registro = "{RAIZ}/registro"')
        .replace('manifiesto = ".cosmos/compilado-galaxia.json"', f'manifiesto = "{directorio}/compilado.json"'),
        encoding="utf-8",
    )
    # el espaciado de `destino` en cosmos.toml no es estable: se sustituye por expresión
    texto = re.sub(r'^destino\s*=\s*".*?"', f'destino = "{directorio}/vista"', config.read_text(encoding="utf-8"), count=1, flags=re.M)
    texto = re.sub(r'^modo\s*=\s*".*?"', f'modo = "{modo}"', texto, count=1, flags=re.M)
    config.write_text(texto, encoding="utf-8")
    return config


from tests._integrado import solo_en_el_origen

solo_en_el_origen()  # cifras y listas del catálogo del origen, no del motor


class LasDosSemanticasSeFijanJuntas(unittest.TestCase):
    def test_catalogo_sin_seleccion_no_lleva_pueblos_y_lista_vacia_es_lo_mismo(self) -> None:
        for seleccion in (None, [], ()):
            with self.subTest(seleccion=seleccion):
                pueblos = [n for n in nodos_de_catalogo(ARBOL, seleccion) if n.cosmos == "pueblo"]
                self.assertEqual(pueblos, [], "NUCLEO §2: sin nicho activo no aparece ningún pueblo")

    def test_en_la_api_none_es_ninguno_tambien_al_compilar(self) -> None:
        """A-04 cerrado de verdad (ciclo 2): el centinela se partió. `None` = ninguno en los dos
        subsistemas; la vista completa se pide explícita con `todos=True`."""

        todos = sum(1 for n in ARBOL.nodos if n.cosmos == "pueblo")
        self.assertGreater(todos, 0)
        self.assertEqual(len(_skills(ARBOL, None)), 0, "nichos=None volvió a significar «todos» al compilar")
        self.assertEqual(len(_skills(ARBOL, [])), 0)
        self.assertEqual(len(_skills(ARBOL, None, todos=True)), todos, "la vista completa explícita aplana todo")

    def test_con_seleccion_los_dos_subsistemas_coinciden(self) -> None:
        nicho = nombres_nichos(ARBOL)[0]
        del_catalogo = {n.nombre for n in nodos_de_catalogo(ARBOL, [nicho]) if n.cosmos == "pueblo"}
        self.assertEqual(del_catalogo, set(_skills(ARBOL, [nicho])))

    def test_el_toml_documenta_las_dos(self) -> None:
        texto = (RAIZ / "cosmos.toml").read_text(encoding="utf-8")
        self.assertIn("NING", texto.upper(), "cosmos.toml tiene que decir que lista vacía = ningún nicho en el catálogo")
        self.assertIn("COMPLETA", texto, "cosmos.toml tiene que decir que compilar sin nicho es la vista completa")
        self.assertNotIn("Lista vacía = todos los sistemas solares", texto, "volvió la frase falsa")

    def test_la_cli_lo_dice_al_compilar_la_vista_completa(self) -> None:
        r = subprocess.run([sys.executable, "-m", "cosmos", "compilar", "--seco"],
                           capture_output=True, text=True, cwd=RAIZ)
        self.assertEqual(r.returncode, 0, r.stderr)
        # En seco se lista todo (es su función); sin seco y sin nicho, el aviso de vista completa.
        with TemporaryDirectory() as tmp:
            r = subprocess.run([sys.executable, "-m", "cosmos", "compilar", "--modo", "copia",
                                "--config", str(_config_compilacion(Path(tmp)))],
                               capture_output=True, text=True, cwd=RAIZ)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("vista COMPLETA", r.stdout)


if __name__ == "__main__":
    unittest.main()
