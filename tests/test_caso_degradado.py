"""Ante una entrada degradada, el sistema elegía el valor cómodo en vez de la alarma.

Cuatro hallazgos del revisor adversarial que por separado parecían distintos y juntos son
el mismo defecto — el que la rule llama «un valor mostrado no es un valor conocido»: no
distinguir *cero* de *no lo sé*, y quedarse con la lectura tranquilizadora.

| Entrada degradada | Qué hacía |
|---|---|
| evento JSON truncado | exit 0 y silencio, cuando un `cosmos.toml` roto sí denegaba |
| `--validacion` con ruta inexistente | cobrar el listón sobre el conjunto de AJUSTE, sin decirlo |
| conjunto de validación vacío | `ZeroDivisionError` crudo |
| `--tocando` con ruta absoluta | agua vacía, en silencio |

El segundo es el peor de los cuatro y no por su efecto: el comentario de tres líneas
escrito justo encima **prohíbe exactamente eso**. El código hacía lo contrario de lo que
su propio comentario declaraba, que es la clase de defecto que sobrevive a las revisiones
porque quien lee el comentario cree haber leído el código.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from cosmos.abrir import NodoNoEncontrado, agua_que_moja
from cosmos.modelo import cargar_arbol

RAIZ = Path(__file__).resolve().parent.parent
ARBOL = cargar_arbol(RAIZ / "galaxia")


def _acertar(*extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "cosmos", "acertar", *extra],
                          capture_output=True, text=True, cwd=RAIZ)


class UnExamenQueNoApareceNoSeApruebaPorIncomparecencia(unittest.TestCase):
    def test_no_existe_liston_sobre_esta_metrica(self) -> None:
        """R-01: `--minimo` se retiró. Un listón sobre una cifra que describe a quien escribió el
        examen —y no al árbol— se aprueba escribiendo el examen. argparse lo rechaza (exit 2)."""

        r = _acertar("--minimo", "70")
        self.assertEqual(r.returncode, 2)
        self.assertIn("--minimo", r.stderr)

    def test_sin_conjunto_de_validacion_se_dice_y_no_se_usa_el_de_ajuste(self) -> None:
        with TemporaryDirectory() as tmp:
            r = _acertar("--validacion", str(Path(tmp, "no-existe.json")))
        self.assertEqual(r.returncode, 0)
        self.assertIn("NO DISPONIBLE", r.stdout)
        self.assertNotIn("Cifra íntegra", r.stdout)

    def test_un_conjunto_vacio_no_revienta_con_un_traceback(self) -> None:
        with TemporaryDirectory() as tmp:
            vacio = Path(tmp, "vacio.json")
            vacio.write_text("[]", encoding="utf-8")
            r = _acertar("--validacion", str(vacio))
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn("VACÍO", r.stdout)


class UnEventoIlegibleNoEsUnEventoAprobado(unittest.TestCase):
    def _lanzar(self, crudo: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-m", "puente.sesion"],
                              input=crudo, capture_output=True, text=True, cwd=RAIZ)

    def test_pretooluse_sin_tool_name_deniega(self) -> None:
        evento = json.dumps({
            "hook_event_name": "PreToolUse",
            "cwd": str(RAIZ),
            "tool_input": {"file_path": str(RAIZ / "galaxia/COSMOS.md")},
        })
        salida = self._lanzar(evento).stdout
        self.assertIn('"permissionDecision": "deny"', salida)
        self.assertIn("no pudo evaluar", salida)

    def test_un_json_ilegible_deja_rastro_aunque_pase(self) -> None:
        """No se puede denegar lo que no se sabe qué es — pero se anota."""

        registro = RAIZ / ".cosmos/cierres.log"
        antes = registro.stat().st_size if registro.is_file() else 0
        resultado = self._lanzar('{"hook_event_name":"PreToolUse","tool_')
        self.assertEqual(resultado.returncode, 0)
        self.assertTrue(registro.is_file(), "un evento ilegible no dejó rastro")
        self.assertGreater(registro.stat().st_size, antes)


class UnaRutaQueNoSeEntiendeNoEsUnaRutaSinAgua(unittest.TestCase):
    def test_absoluta_dentro_del_proyecto_da_lo_mismo_que_relativa(self) -> None:
        absoluta = agua_que_moja(ARBOL, str(RAIZ / "cosmos/abrir.py"))
        relativa = agua_que_moja(ARBOL, "cosmos/abrir.py")
        self.assertEqual([n.nombre for n in absoluta], [n.nombre for n in relativa])
        self.assertTrue(absoluta, "un .py del proyecto tiene que mojarse con algo")

    def test_absoluta_de_fuera_lo_dice_en_vez_de_devolver_vacio(self) -> None:
        with self.assertRaises(NodoNoEncontrado) as caso:
            agua_que_moja(ARBOL, "/etc/hosts")
        self.assertIn("fuera del proyecto", str(caso.exception))


if __name__ == "__main__":
    unittest.main()
