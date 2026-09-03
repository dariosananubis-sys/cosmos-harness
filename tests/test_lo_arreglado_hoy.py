"""Lo que se arregla tras una revisión no está revisado, y hoy volvió a pasar.

El tercer revisor entró sobre el árbol ya corregido por los dos anteriores y **el hallazgo
crítico estaba en el código escrito para corregir al primero**: el fix que hacía que `Bash`
llevara su ruta al guard abrió un bypass — la primera ruta absoluta del comando decidía
contra qué repositorio se evaluaba el evento, así que nombrar una ruta ajena antes que la
propia apagaba G03 en silencio.

Estas pruebas fijan esa tanda entera. Cada una nombra el fix que la motivó, porque el
patrón es siempre el mismo: **el arreglo del arreglo es donde vive el fallo que nadie mira**.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from cosmos.abrir import agua_que_moja
from cosmos.medir import medir_casos, veredicto_de_presupuesto
from cosmos.modelo import cargar_arbol, cargar_configuracion, escribir_atomico

RAIZ = Path(__file__).resolve().parent.parent
ARBOL = cargar_arbol(RAIZ / "galaxia")


class UnaRutaAjenaNoDecidePorElRepositorioTocado(unittest.TestCase):
    """B01: el bypass que abrió el fix de `Bash`."""

    def _lanzar(self, comando: str) -> str:
        evento = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "cwd": str(RAIZ),
            "tool_input": {"command": comando},
        }
        salida = subprocess.run([sys.executable, "-m", "puente.sesion"],
                                input=json.dumps(evento), capture_output=True,
                                text=True, cwd=RAIZ).stdout
        if not salida.strip():
            return "mudo"
        return json.loads(salida)["hookSpecificOutput"]["permissionDecision"]

    def test_deniega_aunque_el_comando_nombre_otro_arbol_cosmos_primero(self) -> None:
        with TemporaryDirectory() as ajeno:
            otro = Path(ajeno)
            (otro / "arbol").mkdir()
            (otro / "arbol/galaxia.md").write_text(
                "---\ncosmos: galaxia\nnombre: x\nresumen: Arbol ajeno.\n---\n", encoding="utf-8")
            (otro / "cosmos.toml").write_text(
                (RAIZ / "cosmos.toml").read_text(encoding="utf-8")
                .replace('arbol = "galaxia"', 'arbol = "arbol"'),
                encoding="utf-8")
            comando = f"cp {otro}/arbol/galaxia.md {RAIZ}/galaxia/COSMOS.md"
            self.assertEqual(self._lanzar(comando), "deny",
                             "una ruta ajena delante apagó el guard del árbol que se tocaba")

    def test_el_caso_simple_sigue_denegando(self) -> None:
        self.assertEqual(self._lanzar(f"echo x > {RAIZ}/galaxia/COSMOS.md"), "deny")


class ElVeredictoQueSeLeeEsElQueDecide(unittest.TestCase):
    """B02: quedaba una cuarta comparación, y era la que ve la persona."""

    def test_la_salida_y_el_codigo_de_salida_no_se_contradicen(self) -> None:
        with TemporaryDirectory() as tmp:
            config = Path(tmp, "c.toml")
            config.write_text(
                (RAIZ / "cosmos.toml").read_text(encoding="utf-8")
                .replace("entrada = 4000", "entrada = 3000")
                .replace("activos = []", 'activos = ["juegos"]')
                .replace('arbol = "galaxia"', f'arbol = "{RAIZ}/galaxia"')
                .replace('indice = "galaxia/COSMOS.md"', f'indice = "{RAIZ}/galaxia/COSMOS.md"')
                .replace('registro = "registro"', f'registro = "{RAIZ}/registro"'),
                encoding="utf-8")
            r = subprocess.run([sys.executable, "-m", "cosmos", "medir", "--config", str(config)],
                               capture_output=True, text=True, cwd=RAIZ)
        dice_ok = "OK, quedan" in r.stdout
        self.assertEqual(dice_ok, r.returncode == 0,
                         f"la salida dice {'OK' if dice_ok else 'ROJO'} y el exit es {r.returncode}")


class LaEscrituraAtomicaNoCambiaQuienPuedeLeer(unittest.TestCase):
    """B04: `mkstemp` crea en 0600 y el temporal sustituye al destino."""

    def test_conserva_los_permisos_del_fichero_que_reemplaza(self) -> None:
        with TemporaryDirectory() as tmp:
            destino = Path(tmp, "indice.md")
            destino.write_text("viejo\n", encoding="utf-8")
            os.chmod(destino, 0o644)
            escribir_atomico(destino, "nuevo\n")
            self.assertEqual(destino.stat().st_mode & 0o777, 0o644)

    def test_un_fichero_restringido_sigue_restringido(self) -> None:
        with TemporaryDirectory() as tmp:
            destino = Path(tmp, "secreto.md")
            destino.write_text("viejo\n", encoding="utf-8")
            os.chmod(destino, 0o600)
            escribir_atomico(destino, "nuevo\n")
            self.assertEqual(destino.stat().st_mode & 0o777, 0o600,
                             "la escritura atómica abrió un fichero que estaba cerrado")


class LosDosDivisoresEstanGuardados(unittest.TestCase):
    """B05: se arregló el que salió en el traceback y no su hermano de la línea siguiente."""

    def test_un_conjunto_de_ajuste_vacio_no_revienta(self) -> None:
        with TemporaryDirectory() as tmp:
            vacio = Path(tmp, "vacio.json")
            vacio.write_text("[]", encoding="utf-8")
            r = subprocess.run([sys.executable, "-m", "cosmos", "acertar", "--encargos", str(vacio)],
                               capture_output=True, text=True, cwd=RAIZ)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn("sin encargos", r.stdout)


class ElMensajeDeLaValvulaNombraLasQueExisten(unittest.TestCase):
    """B06: anunciaba un rango, y la numeración tiene huecos a propósito."""

    def test_no_anuncia_un_rango_con_huecos(self) -> None:
        from cosmos.guardarrailes import ErrorSalto, normalizar_codigo
        from cosmos.validar import codigos_comprobados

        with self.assertRaises(ErrorSalto) as caso:
            normalizar_codigo("E04")
        mensaje = str(caso.exception)
        self.assertNotIn("E00..E19", mensaje)
        self.assertNotIn("E04", mensaje.split(";")[1] if ";" in mensaje else "")
        for codigo in codigos_comprobados():
            self.assertIn(codigo, mensaje)


class UnaRutaNoCanonicaNoDaOtraRespuesta(unittest.TestCase):
    """B07: `tests//test_x.py` perdía tres de sus cuatro mares, plausiblemente."""

    def test_las_formas_de_escribir_la_misma_ruta_dan_lo_mismo(self) -> None:
        formas = ["tests/test_x.py", "tests//test_x.py", "./tests/test_x.py",
                  str(RAIZ / "tests/test_x.py")]
        respuestas = {f: [n.nombre for n in agua_que_moja(ARBOL, f)] for f in formas}
        primera = respuestas[formas[0]]
        self.assertTrue(primera, "un test .py tiene que mojarse con algo")
        for forma, agua in respuestas.items():
            with self.subTest(forma):
                self.assertEqual(agua, primera)

    def test_un_fichero_del_home_no_recibe_el_agua_del_proyecto(self) -> None:
        from cosmos.abrir import NodoNoEncontrado

        with self.assertRaises(NodoNoEncontrado):
            agua_que_moja(ARBOL, "~/x.py")


if __name__ == "__main__":
    unittest.main()
