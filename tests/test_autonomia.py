"""El grado de autonomía de la máquina (`cosmos configurar --autonomia`), sin tocar el disco real.

Todo corre con `HOME` y `CLAUDE_CONFIG_DIR` apuntando a un temporal: el gate ejecuta esta suite
sobre una instantánea del índice y ninguna prueba puede leer ni escribir los ajustes de usuario
de quien commitea.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from cosmos import configurar as cfg

RAIZ = Path(__file__).resolve().parent.parent


def _cosmos(entorno: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "cosmos", "configurar", *args],
                          capture_output=True, text=True, cwd=RAIZ, env={**os.environ, **entorno})


class LosAjustesDeUsuarioSeEscribenSinPisar(unittest.TestCase):
    def setUp(self) -> None:
        self.temporal = TemporaryDirectory(prefix="autonomia-")
        self.casa = Path(self.temporal.name)
        self.config = self.casa / "claude-config"
        self.config.mkdir()
        self.ajustes = self.config / "settings.json"
        self.respaldo = self.casa / ".cosmos" / "autonomia.json"
        self.entorno = {"HOME": str(self.casa), "CLAUDE_CONFIG_DIR": str(self.config)}

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def test_destino_respeta_claude_config_dir_y_sin_ella_home(self) -> None:
        with mock.patch.dict(os.environ, self.entorno):
            self.assertEqual(cfg.ajustes_usuario(), self.ajustes)
        with mock.patch.dict(os.environ, {"HOME": str(self.casa)}, clear=False):
            os.environ.pop("CLAUDE_CONFIG_DIR", None)
            with mock.patch("pathlib.Path.home", return_value=self.casa):
                self.assertEqual(cfg.ajustes_usuario(), self.casa / ".claude" / "settings.json")

    def test_escribe_solo_las_claves_del_grado_y_conserva_lo_ajeno(self) -> None:
        original = '{\n  "model": "x",\n   "hooks": {"Stop": []},\n "permissions": {"deny": ["Bash(rm -rf *)"]},\n "theme": "dark", "voice": false\n}\n'
        self.ajustes.write_text(original, encoding="utf-8")
        informe = cfg.fijar_autonomia("libre", self.ajustes, self.respaldo)
        self.assertEqual([(c, e) for c, _, e in informe],
                         [("permissions.defaultMode", "nuevo"), ("skipDangerousModePermissionPrompt", "nuevo")])
        datos = json.loads(self.ajustes.read_text(encoding="utf-8"))
        self.assertEqual(datos["permissions"], {"deny": ["Bash(rm -rf *)"], "defaultMode": "bypassPermissions"})
        self.assertIs(datos["skipDangerousModePermissionPrompt"], True)
        for clave in ("model", "hooks", "theme", "voice"):
            self.assertEqual(datos[clave], json.loads(original)[clave])
        self.assertEqual(cfg.grado_vigente(self.ajustes)[0], "libre")

    def test_vuelta_byte_a_byte(self) -> None:
        original = '{\n    "model": "x",\n  "permissions": {"allow": ["Bash"]}\n}\n'  # indentación rara a propósito
        self.ajustes.write_text(original, encoding="utf-8")
        cfg.fijar_autonomia("auto", self.ajustes, self.respaldo)
        self.assertNotEqual(self.ajustes.read_text(encoding="utf-8"), original)
        estado, ajenas = cfg.retirar_autonomia(self.ajustes, self.respaldo)
        self.assertEqual((estado, ajenas), ("restaurado", []))
        self.assertEqual(self.ajustes.read_bytes(), original.encode("utf-8"))
        self.assertFalse(self.respaldo.exists())

    def test_cambiar_de_grado_no_deja_claves_del_grado_anterior(self) -> None:
        self.ajustes.write_text("{}\n", encoding="utf-8")
        cfg.fijar_autonomia("libre", self.ajustes, self.respaldo)
        cfg.fijar_autonomia("auto", self.ajustes, self.respaldo)
        datos = json.loads(self.ajustes.read_text(encoding="utf-8"))
        self.assertEqual(datos, {"permissions": {"defaultMode": "auto"}})
        estado, _ = cfg.retirar_autonomia(self.ajustes, self.respaldo)
        self.assertEqual(estado, "restaurado")
        self.assertEqual(self.ajustes.read_text(encoding="utf-8"), "{}\n")

    def test_no_pisa_un_valor_cambiado_a_mano(self) -> None:
        self.ajustes.write_text("{}\n", encoding="utf-8")
        cfg.fijar_autonomia("auto", self.ajustes, self.respaldo)
        datos = json.loads(self.ajustes.read_text(encoding="utf-8"))
        datos["permissions"]["defaultMode"] = "plan"  # alguien lo cambió después
        self.ajustes.write_text(json.dumps(datos), encoding="utf-8")
        estado, ajenas = cfg.retirar_autonomia(self.ajustes, self.respaldo)
        self.assertEqual(estado, "podado")
        self.assertEqual(ajenas, ["permissions.defaultMode"])
        self.assertEqual(json.loads(self.ajustes.read_text(encoding="utf-8"))["permissions"]["defaultMode"], "plan")

    def test_si_no_existia_se_borra_y_el_directorio_tambien_si_lo_creamos(self) -> None:
        ruta = self.casa / "nuevo-config" / "settings.json"
        cfg.fijar_autonomia("auto", ruta, self.respaldo)
        self.assertTrue(ruta.is_file())
        estado, _ = cfg.retirar_autonomia(ruta, self.respaldo)
        self.assertEqual(estado, "eliminado")
        self.assertFalse(ruta.exists())
        self.assertFalse(ruta.parent.exists(), "el directorio lo creamos nosotros y quedó vacío")

    def test_sin_respaldo_no_se_toca_nada(self) -> None:
        self.ajustes.write_text('{"permissions": {"defaultMode": "auto"}}\n', encoding="utf-8")
        estado, _ = cfg.retirar_autonomia(self.ajustes, self.respaldo)
        self.assertEqual(estado, "ausente", "sin respaldo no se sabe qué es nuestro: no se quita nada")
        self.assertIn('"auto"', self.ajustes.read_text(encoding="utf-8"))

    def test_un_fichero_que_no_es_json_no_se_toca(self) -> None:
        self.ajustes.write_text("{ esto no es json", encoding="utf-8")
        with self.assertRaises(ValueError):
            cfg.fijar_autonomia("auto", self.ajustes, self.respaldo)
        self.assertEqual(self.ajustes.read_text(encoding="utf-8"), "{ esto no es json")

    def test_el_grado_es_trivalente(self) -> None:
        self.assertEqual(cfg.grado_vigente(self.ajustes)[0], "desconocido", "sin fichero no se afirma manual")
        self.ajustes.write_text("{}", encoding="utf-8")
        self.assertEqual(cfg.grado_vigente(self.ajustes)[0], "desconocido", "sin la clave, el defecto lo decide el runtime")
        self.ajustes.write_text('{"permissions": {"defaultMode": "default"}}', encoding="utf-8")
        self.assertEqual(cfg.grado_vigente(self.ajustes)[0], "manual")
        self.ajustes.write_text('{"permissions": {"defaultMode": "auto"}}', encoding="utf-8")
        self.assertEqual(cfg.grado_vigente(self.ajustes)[0], "auto")
        self.ajustes.write_text("no json", encoding="utf-8")
        self.assertEqual(cfg.grado_vigente(self.ajustes)[0], "desconocido")

    def test_por_cli_seco_no_escribe_nada_y_manual_deshace(self) -> None:
        self.ajustes.write_text('{"model": "x"}\n', encoding="utf-8")
        antes = (self.ajustes.stat().st_mtime_ns, self.ajustes.read_bytes())
        r = _cosmos(self.entorno, "--autonomia", "libre", "--seco", "--directorio", str(self.casa / ".cosmos"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('"bypassPermissions"', r.stdout)
        self.assertIn("skipDangerousModePermissionPrompt", r.stdout)
        self.assertEqual((self.ajustes.stat().st_mtime_ns, self.ajustes.read_bytes()), antes, "--seco escribió")
        r = _cosmos(self.entorno, "--autonomia", "auto", "--directorio", str(self.casa / ".cosmos"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("permissions.defaultMode", r.stdout)
        self.assertIn("(nuevo)", r.stdout)
        self.assertIn("--autonomia manual", r.stdout)
        self.assertNotIn(str(self.casa), r.stdout, "la salida enseña la ruta de la máquina en vez de ~")
        self.assertEqual(json.loads(self.ajustes.read_text(encoding="utf-8"))["permissions"]["defaultMode"], "auto")
        r = _cosmos(self.entorno, "--autonomia", "--directorio", str(self.casa / ".cosmos"))
        self.assertIn("autonomia  auto", r.stdout)
        r = _cosmos(self.entorno, "--autonomia", "manual", "--directorio", str(self.casa / ".cosmos"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("byte a byte", r.stdout)
        self.assertEqual(self.ajustes.read_bytes(), antes[1])

    def test_el_alta_con_banderas_no_toca_los_ajustes_de_usuario(self) -> None:
        """Un script que encadena el alta no puede acabar cambiando los permisos de nadie."""

        r = _cosmos(self.entorno, "--oficios", "agentes-ia", "--herramientas", "revision-cruzada",
                    "--directorio", str(self.casa / ".cosmos"), "--no-abrir")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(self.ajustes.exists(), "el alta por banderas escribió ajustes de usuario sin pedirlo")


class ElLanzadorNoPisaLoAjeno(unittest.TestCase):
    def test_instalar_quitar_y_no_pisar(self) -> None:
        with TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "bin" / "cosmos"
            destino, estado = cfg.instalar_lanzador(RAIZ, ruta)
            self.assertEqual(estado, "creado")
            self.assertTrue(cfg.es_lanzador_nuestro(destino))
            self.assertEqual(cfg.raiz_del_lanzador(destino), RAIZ)
            self.assertTrue(os.access(destino, os.X_OK))
            # El shim ejecuta de verdad el paquete desde cualquier directorio.
            r = subprocess.run([str(destino), "--version"], capture_output=True, text=True, cwd=tmp)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("cosmos ", r.stdout)
            self.assertEqual(cfg.instalar_lanzador(RAIZ, ruta)[1], "actualizado")
            self.assertEqual(cfg.quitar_lanzador(ruta)[1], "eliminado")
            ruta.write_text("#!/bin/sh\necho ajeno\n", encoding="utf-8")
            self.assertEqual(cfg.instalar_lanzador(RAIZ, ruta)[1], "ajeno")
            self.assertEqual(ruta.read_text(encoding="utf-8"), "#!/bin/sh\necho ajeno\n")
            self.assertEqual(cfg.quitar_lanzador(ruta)[1], "ajeno")
            self.assertEqual(cfg.instalar_lanzador(RAIZ, ruta, forzar=True)[1], "actualizado")


class ElPerfilConservaLaTablaDeModelos(unittest.TestCase):
    def test_reescribir_el_perfil_no_borra_modelos(self) -> None:
        with TemporaryDirectory() as tmp:
            perfil = Path(tmp) / "perfil.toml"
            cfg.escribir_privado(perfil, cfg.perfil_toml(["web"], ["astro"], modelos={"configs": ["~/cuentas"], "duro": "claude-opus-5"}))
            self.assertEqual(cfg.leer_modelos(perfil), {"configs": ["~/cuentas"], "duro": "claude-opus-5"})
            cfg.escribir_privado(perfil, cfg.perfil_toml(["web"], ["astro"], comprobadas=True, modelos=cfg.leer_modelos(perfil)))
            self.assertEqual(cfg.leer_perfil(perfil)["credenciales_comprobadas"], True)
            self.assertEqual(cfg.leer_modelos(perfil)["duro"], "claude-opus-5")
            self.assertEqual(cfg.leer_modelos(Path(tmp) / "no-existe.toml"), {})


if __name__ == "__main__":
    unittest.main()
