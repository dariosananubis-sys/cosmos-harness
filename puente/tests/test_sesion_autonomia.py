"""G01 y el océano `autonomia`: la carta no puede ser una mentira.

La pareja obligatoria de `spec/GUARDARRAILES.md` («Verificación exigida» §1): el aviso sale
cuando los ajustes de usuario arrancan en manual, NO sale con `auto` o `bypassPermissions`, y
dice `desconocido` —nunca «manual»— cuando no hay fichero legible. Todo con `CLAUDE_CONFIG_DIR`
en un temporal: nada lee los ajustes de quien ejecuta la suite.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from cosmos.cli import ejecutar
from puente import sesion
from puente.tests.comun import arbol_minimo, repo_git

CONFIG = """[presupuesto]
entrada = 4000
resumen = 120
oceanos = 7
galaxia_lineas = 40
solapamiento = 0.25

[raiz]
arbol = "arbol"
indice = "arbol/COSMOS.md"

[medicion]
metodo = "aprox"

[compilacion]
destino = ".cosmos/vista"
modo = "symlink"
manifiesto = ".cosmos/compilado.json"
"""

OCEANO_AUTONOMIA = """---
cosmos: oceano
nombre: autonomia
moja: ["**"]
resumen: Se ejecuta sin pedir permiso; solo lo que no tiene vuelta atras espera el visto bueno.
---

Se ejecuta sin pedir permiso. Espera un si lo que no tiene vuelta atras.
"""


def _repositorio(base: Path, *, con_oceano: bool) -> Path:
    raiz = repo_git(base / "repo")
    (raiz / "arbol").mkdir(parents=True, exist_ok=True)
    arbol_minimo(raiz / "arbol")
    if con_oceano:
        (raiz / "arbol" / "oceano-autonomia.md").write_text(OCEANO_AUTONOMIA, encoding="utf-8")
    (raiz / "cosmos.toml").write_text(CONFIG, encoding="utf-8")
    with contextlib.redirect_stdout(io.StringIO()):
        for orden in (["arrancar"], ["generar"], ["arrancar"]):
            if ejecutar([*orden, "--config", str(raiz / "cosmos.toml")]):
                raise AssertionError("el árbol de prueba no llega a verde")
    return raiz


class LaCartaYLaMaquinaDicenLoMismo(unittest.TestCase):
    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="sesion-autonomia-")
        self.base = Path(self.temporal.name)
        self.config_dir = self.base / "claude"
        self.config_dir.mkdir()
        self.parche = mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": str(self.config_dir)})
        self.parche.start()

    def tearDown(self) -> None:
        self.parche.stop()
        self.temporal.cleanup()

    def _arranque(self, raiz: Path, **campos: object) -> str:
        evento = {"hook_event_name": "SessionStart", "session_id": "x", "cwd": str(raiz), **campos}
        decision, _ = sesion.decidir(evento, config_path=raiz / "cosmos.toml")
        self.assertEqual(decision.accion, "informar")
        self.assertFalse(decision.bloquea, "G01 nunca bloquea")
        return decision.motivo

    def _ajustes(self, modo: str | None) -> None:
        contenido = {} if modo is None else {"permissions": {"defaultMode": modo}}
        (self.config_dir / "settings.json").write_text(json.dumps(contenido), encoding="utf-8")

    def test_avisa_en_rojo_cuando_la_maquina_arranca_en_manual(self) -> None:
        raiz = _repositorio(self.base / "a", con_oceano=True)
        self._ajustes("default")
        motivo = self._arranque(raiz)
        self.assertIn("autonomia  rojo", motivo)
        self.assertIn("configurar --autonomia auto", motivo)

    def test_calla_cuando_la_maquina_acompana(self) -> None:
        raiz = _repositorio(self.base / "b", con_oceano=True)
        for modo in ("auto", "bypassPermissions"):
            with self.subTest(modo):
                self._ajustes(modo)
                self.assertNotIn("autonomia", self._arranque(raiz))

    def test_dice_desconocido_sin_fichero_y_sin_clave_nunca_manual(self) -> None:
        raiz = _repositorio(self.base / "c", con_oceano=True)
        motivo = self._arranque(raiz)
        self.assertIn("autonomia  desconocido", motivo)
        self.assertNotIn("rojo", motivo.split("autonomia", 1)[1])
        self._ajustes(None)
        motivo = self._arranque(raiz)
        self.assertIn("autonomia  desconocido", motivo)
        (self.config_dir / "settings.json").write_text("{ roto", encoding="utf-8")
        self.assertIn("autonomia  desconocido", self._arranque(raiz))

    def test_el_modo_del_evento_manda_si_llega(self) -> None:
        """El evento no lo trae hoy; si un día lo trae, es la medida real y gana a los ajustes."""

        raiz = _repositorio(self.base / "d", con_oceano=True)
        self._ajustes("default")
        self.assertNotIn("autonomia", self._arranque(raiz, permission_mode="bypassPermissions"))
        self._ajustes("auto")
        self.assertIn("autonomia  rojo", self._arranque(raiz, permission_mode="plan"))

    def test_sin_el_oceano_no_hay_nada_que_comprobar(self) -> None:
        raiz = _repositorio(self.base / "e", con_oceano=False)
        self._ajustes("default")
        self.assertNotIn("autonomia", self._arranque(raiz))


if __name__ == "__main__":
    unittest.main()
