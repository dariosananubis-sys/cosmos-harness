"""Revisión C (2026-09-04): el alta de máquina, con cada bug visto fallar antes de arreglarlo.

Todo corre sobre un HOME temporal con `CLAUDE_CONFIG_DIR`: nada lee ni escribe los ajustes
reales de quien commitea. `progress/revision-2026-09-04/C-alta-de-maquina.md` es el informe.
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import time
import unittest
from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from cosmos import configurar as cfg
from cosmos import guardarrailes as gr
from cosmos.estado import inventariar_maquina
from cosmos.modelo import cargar_arbol
from puente import modelos as mod
from tests.test_guardarrailes import _repo_cosmos
from tests.test_modelos import _Casa, _anotador

RAIZ = Path(__file__).resolve().parent.parent
ARBOL = cargar_arbol(RAIZ / "galaxia")


def _cosmos(entorno: dict[str, str], *args: str, entrada: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "cosmos", *args], capture_output=True, text=True, cwd=RAIZ,
                          env={**os.environ, **entorno}, input=entrada)


class Casa(unittest.TestCase):
    def setUp(self) -> None:
        self.temporal = TemporaryDirectory(prefix="revision-c-")
        self.casa = Path(self.temporal.name)
        self.config = self.casa / "claude-config"
        self.config.mkdir()
        self.ajustes = self.config / "settings.json"
        self.directorio = self.casa / ".cosmos"
        self.respaldo = self.directorio / "autonomia.json"
        self.entorno = {"HOME": str(self.casa), "CLAUDE_CONFIG_DIR": str(self.config)}

    def tearDown(self) -> None:
        self.temporal.cleanup()


class ManualDevuelveLoQueHabia(Casa):
    def test_c01_el_valor_previo_del_usuario_se_repone_en_vez_de_borrarse(self) -> None:
        self.ajustes.write_text('{"permissions": {"defaultMode": "acceptEdits"}, "model": "opus"}\n', encoding="utf-8")
        informe = cfg.fijar_autonomia("auto", self.ajustes, self.respaldo)
        self.assertIn('cambiado desde "acceptEdits"', informe[0][2])
        estado, ajenas = cfg.retirar_autonomia(self.ajustes, self.respaldo)
        self.assertEqual((estado, ajenas), ("restaurado", []))
        self.assertEqual(self.ajustes.read_text(encoding="utf-8"),
                         '{"permissions": {"defaultMode": "acceptEdits"}, "model": "opus"}\n')

    def test_c18_un_permissions_vacio_vuelve_byte_a_byte(self) -> None:
        self.ajustes.write_text('{"permissions": {}}\n', encoding="utf-8")
        cfg.fijar_autonomia("auto", self.ajustes, self.respaldo)
        estado, _ = cfg.retirar_autonomia(self.ajustes, self.respaldo)
        self.assertEqual(estado, "restaurado")
        self.assertEqual(self.ajustes.read_text(encoding="utf-8"), '{"permissions": {}}\n')

    def test_c05_manual_en_seco_no_escribe(self) -> None:
        cfg.fijar_autonomia("auto", self.ajustes, self.respaldo)
        antes = self.ajustes.read_bytes()
        estado, _ = cfg.retirar_autonomia(self.ajustes, self.respaldo, seco=True)
        self.assertEqual(estado, "eliminado")
        self.assertEqual(self.ajustes.read_bytes(), antes)
        self.assertTrue(self.respaldo.is_file(), "en seco el respaldo tiene que seguir ahí")
        r = _cosmos(self.entorno, "configurar", "--autonomia", "manual", "--seco", "--directorio", str(self.directorio))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("(seco)", r.stdout)
        self.assertEqual(self.ajustes.read_bytes(), antes, "--autonomia manual --seco escribió")


class SecoEsSeco(Casa):
    def test_c07_lanzador_en_seco_no_escribe(self) -> None:
        r = _cosmos(self.entorno, "configurar", "--lanzador", "--seco")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("(seco)", r.stdout)
        self.assertFalse((self.casa / ".local" / "bin" / "cosmos").exists(), "--lanzador --seco escribió el shim")

    def test_c08_el_alta_y_comprobar_en_seco_no_escriben(self) -> None:
        r = _cosmos(self.entorno, "configurar", "--oficios", "agentes-ia", "--herramientas", "revision-cruzada",
                    "--seco", "--no-abrir", "--directorio", str(self.directorio))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("(seco)", r.stdout)
        self.assertFalse(self.directorio.exists(), "--seco escribió perfil o credenciales")
        r = _cosmos(self.entorno, "configurar", "--oficios", "agentes-ia", "--herramientas", "revision-cruzada",
                    "--no-abrir", "--directorio", str(self.directorio))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        perfil = self.directorio / "perfil.toml"
        antes = (perfil.stat().st_mtime_ns, perfil.read_bytes())
        r = _cosmos(self.entorno, "configurar", "--comprobar", "--seco", "--directorio", str(self.directorio))
        self.assertIn("(seco)", r.stdout)
        self.assertEqual((perfil.stat().st_mtime_ns, perfil.read_bytes()), antes, "--comprobar --seco reescribió el perfil")

    def test_c04_modelos_quitar_en_seco_no_descarga_nada(self) -> None:
        with _Casa():
            ordenes, ejecutor = _anotador()
            mod.instalar(perfil={}, ejecutor=ejecutor, plataforma="darwin")
            del ordenes[:]
            lineas = mod.quitar(ejecutor=ejecutor, plataforma="darwin", seco=True)
            self.assertEqual(ordenes, [], "quitar --seco llamó a launchctl")
            self.assertTrue(mod.ruta_plist().is_file() and mod.ruta_reponedor().is_file())
            self.assertTrue(all("(seco)" in l for l in lineas), lineas)

    def test_c22_quitar_no_deja_el_bin_vacio_y_dice_que_el_log_se_conserva(self) -> None:
        with _Casa():
            _, ejecutor = _anotador()
            mod.instalar(perfil={}, ejecutor=ejecutor, plataforma="linux")
            mod.ruta_log().parent.mkdir(parents=True, exist_ok=True)
            mod.ruta_log().write_text("x\n", encoding="utf-8")
            lineas = mod.quitar(ejecutor=ejecutor, plataforma="linux")
            self.assertFalse(mod.directorio_bin().exists(), "quedó ~/.cosmos/bin vacío")
            self.assertTrue(mod.ruta_log().is_file())
            self.assertIn("se conserva", "\n".join(lineas))


class ElLanzadorYElEnlace(Casa):
    def test_c09_forzar_sobre_un_symlink_no_escribe_a_traves_del_enlace(self) -> None:
        real = self.casa / "herramienta-real"
        real.write_text("#!/bin/sh\necho mia\n", encoding="utf-8")
        enlace = self.casa / ".local" / "bin" / "cosmos"
        enlace.parent.mkdir(parents=True)
        enlace.symlink_to(real)
        ruta, estado = cfg.instalar_lanzador(RAIZ, enlace, forzar=True)
        self.assertEqual(estado, "actualizado")
        self.assertEqual(real.read_text(encoding="utf-8"), "#!/bin/sh\necho mia\n", "se pisó el destino del enlace")
        self.assertFalse(enlace.is_symlink())
        self.assertTrue(cfg.es_lanzador_nuestro(enlace))


class ElInventarioNoDiceOkSinMirar(Casa):
    def test_c10_un_interprete_que_no_existe_no_es_ok(self) -> None:
        with _Casa():
            _, ejecutor = _anotador()
            roto = str(self.casa / "venv-borrado" / "bin" / "python3")
            mod.instalar(perfil={}, ejecutor=ejecutor, plataforma="darwin", interprete=roto)
            por_nombre = {f.nombre: f for f in mod.estado(perfil={}, ejecutor=ejecutor, plataforma="darwin")}
            self.assertEqual(por_nombre["agente launchd"].estado, "falta", por_nombre["agente launchd"])
            self.assertIn("no existe", por_nombre["agente launchd"].detalle)
            self.assertEqual(por_nombre["hook SessionStart"].estado, "falta", por_nombre["hook SessionStart"])
            mod.instalar(perfil={}, ejecutor=ejecutor, plataforma="darwin")
            por_nombre = {f.nombre: f for f in mod.estado(perfil={}, ejecutor=ejecutor, plataforma="darwin")}
            self.assertEqual(por_nombre["agente launchd"].estado, "ok")
            self.assertEqual(por_nombre["hook SessionStart"].estado, "ok")

    def test_c11_credenciales_con_permisos_flojos_no_son_ok(self) -> None:
        r = _cosmos(self.entorno, "configurar", "--oficios", "agentes-ia", "--herramientas", "revision-cruzada",
                    "--no-abrir", "--directorio", str(self.directorio))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        credenciales = self.directorio / "credenciales.txt"
        credenciales.write_text("OPENROUTER_API_KEY=sk-or-v1-" + "x" * 32 + "\n", encoding="utf-8")
        credenciales.chmod(0o644)
        with mock.patch.dict(os.environ, self.entorno):
            filas = {f.nombre: f for f in inventariar_maquina(ARBOL, directorio=self.directorio, raiz_clon=RAIZ)}
        self.assertEqual(filas["credenciales"].estado, "inseguro", filas["credenciales"])
        self.assertIn("chmod 600", filas["credenciales"].detalle)
        credenciales.chmod(0o600)
        with mock.patch.dict(os.environ, self.entorno):
            filas = {f.nombre: f for f in inventariar_maquina(ARBOL, directorio=self.directorio, raiz_clon=RAIZ)}
        self.assertEqual(filas["credenciales"].estado, "ok", filas["credenciales"])

    def test_c19_estado_maquina_admite_directorio(self) -> None:
        otro = self.casa / "otro"
        r = _cosmos(self.entorno, "configurar", "--oficios", "agentes-ia", "--herramientas", "revision-cruzada",
                    "--no-abrir", "--directorio", str(otro))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = _cosmos(self.entorno, "estado", "--maquina", "--directorio", str(otro))
        self.assertEqual(r.returncode, 0, r.stderr)
        linea = next(l for l in r.stdout.splitlines() if l.strip().startswith("perfil"))
        self.assertIn(" ok ", linea, linea)


class ElHookYElPlistConRutasRaras(unittest.TestCase):
    def test_c12_la_orden_del_hook_soporta_espacios_y_se_ejecuta(self) -> None:
        with TemporaryDirectory(prefix="hook con espacio ") as tmp:
            base = Path(tmp)
            interprete = base / "dir con espacio" / "python3"
            interprete.parent.mkdir()
            marca = base / "marca-hook"
            interprete.write_text(f"#!/bin/sh\ntouch {json.dumps(str(marca))}\n", encoding="utf-8")
            interprete.chmod(0o755)
            reponedor = base / "dir con espacio" / "reponer.py"
            reponedor.write_text("", encoding="utf-8")
            orden = mod.orden_hook(str(interprete), reponedor)
            self.assertEqual(mod.partes_de_la_orden(orden), (str(interprete), str(reponedor)))
            subprocess.run(["bash", "-c", orden], check=True, timeout=10)
            limite = time.monotonic() + 8
            while not marca.exists() and time.monotonic() < limite:
                time.sleep(0.2)
            self.assertTrue(marca.exists(), "el hook no llegó a ejecutar el intérprete con espacio en la ruta")

    def test_c21_el_plist_escapa_el_xml(self) -> None:
        import xml.etree.ElementTree as ET

        texto = mod.contenido_plist("/Users/a&b/python3", Path("/Users/a&b/rep.py"), [Path("/Users/a&b/.claude.json")], Path("/l<og"))
        raiz = ET.fromstring(texto)
        cadenas = [e.text for e in raiz.iter("string")]
        self.assertIn("/Users/a&b/python3", cadenas)
        self.assertEqual(mod._programa_del_plist(texto), ("/Users/a&b/python3", "/Users/a&b/rep.py"))


class ElCableadoDeSesion(unittest.TestCase):
    def setUp(self) -> None:
        self.temporal = TemporaryDirectory(prefix="revision-c-sesion-")
        self.repo = _repo_cosmos(Path(self.temporal.name) / "repo")
        self.ajustes = self.repo / gr.RUTA_AJUSTES

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def test_c02_enganchar_dos_veces_conserva_el_primer_respaldo(self) -> None:
        self.ajustes.parent.mkdir(parents=True, exist_ok=True)
        self.ajustes.write_text('{"model": "x"}\n', encoding="utf-8")
        gr.enganchar_sesion(self.repo)
        gr.enganchar_sesion(self.repo)
        ruta, estado = gr.desenganchar_sesion(self.repo)
        self.assertEqual(estado, "restaurado")
        self.assertEqual(ruta.read_text(encoding="utf-8"), '{"model": "x"}\n')
        self.assertNotIn(gr.MARCA_SESION, ruta.read_text(encoding="utf-8"))

    def test_c13_sin_respaldo_y_sin_nada_nuestro_no_se_reescribe_lo_ajeno(self) -> None:
        self.ajustes.parent.mkdir(parents=True, exist_ok=True)
        original = '{"model":"x","hooks":{"Stop":[]},"env":{"A":"1"}}'
        self.ajustes.write_text(original, encoding="utf-8")
        ruta, estado = gr.desenganchar_sesion(self.repo)
        self.assertEqual(estado, "ausente")
        self.assertEqual(ruta.read_text(encoding="utf-8"), original)

    def test_c13_podar_conserva_una_lista_vacia_del_usuario(self) -> None:
        datos = {"hooks": {"Stop": [], "SessionStart": [{"hooks": [{"type": "command", "command": "python3 -m puente.sesion"}]}]}}
        self.assertEqual(gr.podar_sesion(datos), {"hooks": {"Stop": []}})

    def test_c17_un_pre_push_ajeno_se_dice(self) -> None:
        push = self.repo / ".git" / "hooks" / "pre-push"
        push.write_text("#!/bin/sh\necho mio\n", encoding="utf-8")
        gr.enganchar(self.repo, con_pruebas=False)
        aviso = gr.aviso_pre_push(self.repo)
        self.assertIsNotNone(aviso)
        self.assertIn("NO se instaló", aviso)
        self.assertEqual(push.read_text(encoding="utf-8"), "#!/bin/sh\necho mio\n")
        push.unlink()
        gr.enganchar(self.repo, con_pruebas=False)
        self.assertIsNone(gr.aviso_pre_push(self.repo))


class ElAltaInteractivaRespetaLasBanderas(Casa):
    def test_c06_con_autonomia_por_bandera_no_se_pregunta(self) -> None:
        from cosmos.cli import _configurar
        from cosmos.modelo import cargar_configuracion

        config = cargar_configuracion(RAIZ / "cosmos.toml")
        preguntas: list[str] = []
        elecciones = iter([["agentes-ia"], ["revision-cruzada"]])

        def entrada(texto: str = "") -> str:
            preguntas.append(texto)
            return "n"

        args = Namespace(directorio=self.directorio, no_abrir=True, comprobar=False, llavero=False, seco=False,
                         oficios="", herramientas="", autonomia=None, modelos=None, lanzador=None, forzar=False,
                         alta_autonomia="libre", alta_modelos=False, alta_forzar=False)
        with mock.patch.dict(os.environ, self.entorno), mock.patch("builtins.input", side_effect=entrada), \
                mock.patch.object(cfg, "elegir", side_effect=lambda *a, **k: next(elecciones)), mock.patch("sys.stdout"):
            codigo = _configurar(args, config, ARBOL)
        self.assertEqual(codigo, 0)
        self.assertFalse(any("sin pedir permiso" in p or "auto (recomendado)" in p for p in preguntas),
                         "se preguntó por la autonomía aunque venía por bandera")
        self.assertEqual(json.loads(self.ajustes.read_text(encoding="utf-8"))["permissions"]["defaultMode"], "bypassPermissions")


class LaAyudaNoMiente(unittest.TestCase):
    def test_c16_la_ayuda_de_modelos_nombra_todo_lo_que_escribe(self) -> None:
        r = subprocess.run([sys.executable, "-m", "cosmos", "configurar", "--help"], capture_output=True, text=True, cwd=RAIZ)
        self.assertIn("SessionStart", r.stdout)
        self.assertIn(".claude.json", r.stdout)
        self.assertIn("todas", r.stdout.replace("\n", " ").replace("  ", " "))


if __name__ == "__main__":
    unittest.main()
