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




class ElPunteroEsReversible(unittest.TestCase):
    """`configurar --puntero`: el bloque entra en la memoria de usuario y sale sin dejar rastro.

    Medido el 2026-09-11: con el lanzador en el PATH y 309 fichas en el catálogo, ninguna sesión
    de la máquina sabía que existía `cosmos buscar`, porque nada lo nombraba fuera del clon.
    """

    OCEANOS = ["verificar", "secretos", "autonomia"]

    def setUp(self) -> None:
        self.temporal = TemporaryDirectory(prefix="puntero-")
        self.casa = Path(self.temporal.name)
        self.ruta = self.casa / ".claude" / "CLAUDE.md"
        self.respaldo = self.casa / ".cosmos" / "puntero-respaldo.json"

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def _instalar(self):
        return cfg.instalar_puntero(self.OCEANOS, RAIZ, self.ruta, respaldo=self.respaldo)

    def _quitar(self):
        return cfg.quitar_puntero(self.ruta, respaldo=self.respaldo)

    def test_crea_el_fichero_con_el_bloque_y_lo_quita_entero(self) -> None:
        ruta, estado = self._instalar()
        self.assertEqual(estado, "creado")
        texto = ruta.read_text(encoding="utf-8")
        self.assertTrue(texto.startswith(cfg.MARCA_PUNTERO_INICIO))
        self.assertIn("cosmos buscar", texto)
        self.assertIn("cosmos abrir", texto)
        self.assertIn("autonomia, secretos, verificar", texto, "los océanos se nombran, ordenados")
        # Sin la línea del clon: la ruta de un temporal lleva dígitos y no es una cifra del catálogo.
        sin_ruta = "\n".join(l for l in texto.splitlines() if not l.startswith("Clon:"))
        self.assertNotRegex(sin_ruta, r"\d{3}", "el puntero no lleva cifras: envejecen en silencio")
        self.assertEqual(self._instalar()[1], "al día")
        self.assertEqual(self._quitar()[1], "eliminado")
        self.assertFalse(ruta.exists())
        self.assertFalse(self.respaldo.exists())

    def test_respeta_lo_ajeno_y_lo_devuelve_byte_a_byte(self) -> None:
        original = "# Mis notas\n\nNo tocar.\n\n"
        self.ruta.parent.mkdir(parents=True)
        self.ruta.write_text(original, encoding="utf-8")
        ruta, estado = self._instalar()
        self.assertEqual(estado, "actualizado")
        texto = ruta.read_text(encoding="utf-8")
        self.assertTrue(texto.startswith(original), "lo de fuera de las marcas no se toca")
        self.assertEqual(texto.count(cfg.MARCA_PUNTERO_INICIO), 1)
        # Reinstalar con otros océanos sustituye el bloque donde está, sin duplicarlo.
        cfg.instalar_puntero(["custodia"], RAIZ, self.ruta, respaldo=self.respaldo)
        texto = ruta.read_text(encoding="utf-8")
        self.assertEqual(texto.count(cfg.MARCA_PUNTERO_INICIO), 1)
        self.assertIn("(custodia)", texto)
        self.assertEqual(self._quitar()[1], "restaurado")
        self.assertEqual(ruta.read_bytes(), original.encode("utf-8"))

    def test_si_alguien_cambio_el_resto_se_poda_y_se_conserva(self) -> None:
        self.ruta.parent.mkdir(parents=True)
        self.ruta.write_text("# Mío\n", encoding="utf-8")
        self._instalar()
        with self.ruta.open("a", encoding="utf-8") as fichero:
            fichero.write("\nAñadido después.\n")
        ruta, estado = self._quitar()
        self.assertEqual(estado, "podado")
        texto = ruta.read_text(encoding="utf-8")
        self.assertNotIn(cfg.MARCA_PUNTERO_INICIO, texto)
        self.assertIn("# Mío", texto)
        self.assertIn("Añadido después.", texto)

    def test_quitar_sin_puntero_no_es_error(self) -> None:
        self.assertEqual(self._quitar()[1], "ausente")
        self.ruta.parent.mkdir(parents=True)
        self.ruta.write_text("sin bloque\n", encoding="utf-8")
        self.assertEqual(self._quitar()[1], "ausente")
        self.assertEqual(self.ruta.read_text(encoding="utf-8"), "sin bloque\n")


class ElPunteroPorLaCLI(unittest.TestCase):
    def setUp(self) -> None:
        self.temporal = TemporaryDirectory(prefix="puntero-cli-")
        self.casa = Path(self.temporal.name)
        self.entorno = {"HOME": str(self.casa), "CLAUDE_CONFIG_DIR": str(self.casa / "claude-config")}
        self.ruta = self.casa / ".claude" / "CLAUDE.md"

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def test_en_seco_no_escribe_y_de_verdad_escribe_dice_el_coste_y_se_quita(self) -> None:
        r = _cosmos(self.entorno, "--puntero", "--seco")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(self.ruta.exists(), "--puntero --seco escribió")
        r = _cosmos(self.entorno, "--puntero")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("puntero  creado", r.stdout)
        self.assertRegex(r.stdout, r"Cuesta \d+ tokens \(estimado\)")
        self.assertNotIn(str(self.casa), r.stdout, "la salida enseña la ruta de la máquina en vez de ~")
        self.assertTrue(self.ruta.is_file())
        estado = subprocess.run([sys.executable, "-m", "cosmos", "estado", "--maquina"],
                                capture_output=True, text=True, cwd=RAIZ, env={**os.environ, **self.entorno})
        self.assertRegex(estado.stdout, r"puntero \.+ ok")
        r = _cosmos(self.entorno, "--puntero", "quitar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(self.ruta.exists())
        estado = subprocess.run([sys.executable, "-m", "cosmos", "estado", "--maquina"],
                                capture_output=True, text=True, cwd=RAIZ, env={**os.environ, **self.entorno})
        self.assertRegex(estado.stdout, r"puntero \.+ falta")


class ElLanzadorSirveDesdeCualquierDirectorio(unittest.TestCase):
    def test_desde_un_directorio_sin_cosmos_toml_se_usa_el_del_clon(self) -> None:
        """Medido el 2026-09-11: desde /tmp, `cosmos buscar` decía «sin resultados» sobre un árbol vacío."""

        with TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "bin" / "cosmos"
            cfg.instalar_lanzador(RAIZ, ruta)
            r = subprocess.run([str(ruta), "estado"], capture_output=True, text=True, cwd=tmp)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertRegex(r.stdout, r"pueblo\s+\d+", "desde fuera del clon, el shim tiene que ver la galaxia")
            self.assertNotIn("sistema-solar      0", r.stdout)

if __name__ == "__main__":
    unittest.main()
