"""Un guard que no está no se distingue de uno que aprobó.

Dos fallos de la misma familia, los dos silenciosos:

- **F19**: `cosmos.toml` se buscaba solo en `cwd`. Desde cualquier subdirectorio los
  cinco guards estaban apagados y nada lo indicaba. Y cualquier excepción se tragaba
  devolviendo 0, así que un guard reventado y un guard que aprueba se veían igual.
- **F18**: una lectura sin `limit` contaba como lectura completa. El runtime lee 2.000
  líneas por defecto sin ponerlo en `tool_input`, así que un fichero de 5.000 quedaba
  marcado como leído entero habiendo entrado el 40 %.

Cada prueba construye el caso que apagaba el guard y exige que hoy no lo apague.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

RAIZ = Path(__file__).resolve().parent.parent.parent


def _lanzar(evento: dict) -> tuple[int, str]:
    """Se lanza SIEMPRE desde la raíz, como hace el runtime.

    El directorio de trabajo que importa viaja dentro del evento (`cwd`), que es
    justo el dato que apagaba los guards. Cambiar además el del proceso solo
    rompía el import y falseaba la prueba.
    """

    proceso = subprocess.run(
        [sys.executable, "-m", "puente.sesion"],
        input=json.dumps(evento),
        capture_output=True,
        text=True,
        cwd=str(RAIZ),
    )
    return proceso.returncode, proceso.stdout


def _decision(salida: str) -> str:
    if not salida.strip():
        return "mudo"
    return json.loads(salida)["hookSpecificOutput"]["permissionDecision"]


def _escritura_sobre_el_indice(cwd: str) -> dict:
    return {
        "hook_event_name": "PreToolUse",
        "cwd": cwd,
        "tool_name": "Write",
        "tool_input": {"file_path": str(RAIZ / "galaxia/COSMOS.md"), "content": "x"},
    }


class ElGuardNoSeApagaPorElDirectorio(unittest.TestCase):
    """F19: el mismo evento, cuatro directorios de trabajo, una sola respuesta."""

    def test_deniega_desde_cualquier_subdirectorio(self) -> None:
        for sitio in (RAIZ, RAIZ / "galaxia", RAIZ / "cosecha", RAIZ / "puente/tests"):
            with self.subTest(cwd=str(sitio)):
                _, salida = _lanzar(_escritura_sobre_el_indice(str(sitio)))
                self.assertEqual(_decision(salida), "deny")

    def test_deniega_aunque_el_cwd_este_fuera_del_repositorio(self) -> None:
        """Lo que decide es dónde cae el daño, no desde dónde se lanza."""

        with TemporaryDirectory() as fuera:
            _, salida = _lanzar(_escritura_sobre_el_indice(fuera))
            self.assertEqual(_decision(salida), "deny")

    def test_un_repositorio_sin_cosmos_sigue_en_silencio(self) -> None:
        """El silencio tiene que seguir existiendo donde toca: esto no va con nosotros."""

        with TemporaryDirectory() as fuera:
            evento = {
                "hook_event_name": "PreToolUse",
                "cwd": fuera,
                "tool_name": "Write",
                "tool_input": {"file_path": str(Path(fuera) / "x.md"), "content": "x"},
            }
            codigo, salida = _lanzar(evento)
            self.assertEqual((codigo, _decision(salida)), (0, "mudo"))


class LaRutaDeBashTambienCuenta(unittest.TestCase):
    """El agujero que el revisor adversarial encontró en el arreglo de F19.

    `Bash` no trae la ruta en un campo del `tool_input`: la lleva dentro del texto del
    comando. El primer arreglo miraba `file_path`, `notebook_path` y `path`, así que
    `echo x > <repo>/galaxia/COSMOS.md` lanzado desde fuera del repositorio pasaba en
    silencio — mientras el mismo comando desde la raíz denegaba. Arreglar el caso que se
    prueba y dejar el hermano abierto es la forma más común de un fix incompleto.
    """

    def test_un_redirect_a_la_ruta_de_veredicto_deniega_desde_fuera(self) -> None:
        evento = {
            "hook_event_name": "PreToolUse",
            "cwd": str(RAIZ.parent),
            "tool_name": "Bash",
            "tool_input": {"command": f"echo x > {RAIZ}/galaxia/COSMOS.md"},
        }
        _, salida = _lanzar(evento)
        self.assertEqual(_decision(salida), "deny")

    def test_un_comando_fuera_de_todo_repositorio_sigue_mudo(self) -> None:
        with TemporaryDirectory() as fuera:
            evento = {
                "hook_event_name": "PreToolUse",
                "cwd": fuera,
                "tool_name": "Bash",
                "tool_input": {"command": f"echo x > {fuera}/x.md"},
            }
            codigo, salida = _lanzar(evento)
            self.assertEqual((codigo, _decision(salida)), (0, "mudo"))


class UnGuardQueRevientaNoAprueba(unittest.TestCase):
    """F19b: fallar abierto y callar es lo peor de los dos mundos."""

    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.base = Path(self.tmp.name)
        (self.base / "cosmos.toml").write_text("esto no es toml valido [[[", encoding="utf-8")
        (self.base / "g").mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _evento_roto(self) -> dict:
        return {
            "hook_event_name": "PreToolUse",
            "cwd": str(self.base),
            "tool_name": "Write",
            "tool_input": {"file_path": str(self.base / "g/x.md"), "content": "x"},
        }

    def test_pretooluse_deniega_cuando_no_puede_evaluar(self) -> None:
        _, salida = _lanzar(self._evento_roto())
        self.assertEqual(_decision(salida), "deny")
        self.assertIn("no pudo evaluar", salida)

    def test_deja_el_rastro_en_cierres_log(self) -> None:
        _lanzar(self._evento_roto())
        registro = self.base / ".cosmos/cierres.log"
        self.assertTrue(registro.is_file(), "un fallo sin rastro es un fallo invisible")
        self.assertIn("PreToolUse", registro.read_text(encoding="utf-8"))

    def test_los_eventos_que_no_deniegan_siguen_fallando_abiertos(self) -> None:
        """Romper la herramienta que vigilas es peor que no avisar — pero se anota."""

        evento = dict(self._evento_roto(), hook_event_name="SessionStart")
        codigo, salida = _lanzar(evento)
        self.assertEqual(codigo, 0)
        self.assertEqual(_decision(salida), "mudo")
        self.assertTrue((self.base / ".cosmos/cierres.log").is_file())


class UnaLecturaTruncadaNoEsUnaLectura(unittest.TestCase):
    """F18: el límite implícito del runtime también trunca."""

    def test_sin_limit_un_fichero_largo_no_cuenta_como_leido(self) -> None:
        from puente.sesion import LINEAS_POR_LECTURA, _lectura_completa

        with TemporaryDirectory() as tmp:
            largo = Path(tmp, "largo.md")
            largo.write_text("linea\n" * (LINEAS_POR_LECTURA + 1), encoding="utf-8")
            self.assertFalse(_lectura_completa({}, largo))

    def test_sin_limit_un_fichero_corto_si_cuenta(self) -> None:
        from puente.sesion import _lectura_completa

        with TemporaryDirectory() as tmp:
            corto = Path(tmp, "corto.md")
            corto.write_text("linea\n" * 100, encoding="utf-8")
            self.assertTrue(_lectura_completa({}, corto))

    def test_un_limit_explicito_que_alcanza_cuenta(self) -> None:
        from puente.sesion import _lectura_completa

        with TemporaryDirectory() as tmp:
            largo = Path(tmp, "largo.md")
            largo.write_text("linea\n" * 3000, encoding="utf-8")
            self.assertFalse(_lectura_completa({}, largo))
            self.assertTrue(_lectura_completa({"limit": 3000}, largo))


if __name__ == "__main__":
    unittest.main()
