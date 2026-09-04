"""El vigilante de modelos (`puente/modelos.py`), sin tocar el disco real ni lanzar launchctl.

`HOME` y `CLAUDE_CONFIG_DIR` apuntan a un temporal en todas las pruebas: el gate corre esta
suite sobre una instantánea del índice y nada puede leer `~/.claude.json` de quien commitea.
`instalar()` recibe un ejecutor que solo anota las órdenes de `launchctl`.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from puente import modelos as mod

RAIZ = Path(__file__).resolve().parent.parent


class _Casa:
    """Un $HOME temporal con CLAUDE_CONFIG_DIR y un .claude.json global."""

    def __init__(self) -> None:
        self.temporal = TemporaryDirectory(prefix="modelos-")
        self.casa = Path(self.temporal.name)
        self.config_dir = self.casa / "config-aislado"
        self.config_dir.mkdir()
        self.global_ = self.casa / ".claude.json"
        self.global_.write_text(json.dumps({"additionalModelOptionsCache": [
            {"value": "del-servidor", "label": "Servidor", "description": "vino del servidor"}]}), encoding="utf-8")
        self.parches = [
            mock.patch.dict(os.environ, {"HOME": str(self.casa), "CLAUDE_CONFIG_DIR": str(self.config_dir)}),
            mock.patch("pathlib.Path.home", return_value=self.casa),
            mock.patch.object(mod, "DIRECTORIO", self.casa / ".cosmos"),
        ]

    def __enter__(self) -> "_Casa":
        for parche in self.parches:
            parche.start()
        return self

    def __exit__(self, *exc: object) -> None:
        for parche in reversed(self.parches):
            parche.stop()
        self.temporal.cleanup()


def _anotador() -> tuple[list[list[str]], mod.Ejecutor]:
    ordenes: list[list[str]] = []

    def ejecutor(orden: list[str]) -> subprocess.CompletedProcess:
        ordenes.append(orden)
        return subprocess.CompletedProcess(orden, 0, stdout="state = running\n", stderr="")

    return ordenes, ejecutor


class LaListaDeModelos(unittest.TestCase):
    def test_bien_formada_y_sin_duplicados(self) -> None:
        valores = [m.valor for m in mod.MODELOS]
        etiquetas = [m.etiqueta for m in mod.MODELOS]
        self.assertEqual(len(set(valores)), len(valores))
        self.assertEqual(len(set(etiquetas)), len(etiquetas))
        for valor in valores:
            self.assertRegex(valor, r"^claude-[a-z0-9.-]+(\[1m\])?$")

    def test_coincide_con_el_readme_y_con_el_rio(self) -> None:
        """Una tabla escrita a mano se desincroniza: la fuente es MODELOS y los textos la citan entera."""

        for fichero in ("README.md", "galaxia/agua/rio-configurar.md"):
            texto = (RAIZ / fichero).read_text(encoding="utf-8")
            with self.subTest(fichero):
                if fichero == "README.md":
                    for modelo in mod.MODELOS:
                        self.assertIn(f"`{modelo.valor}`", texto, f"{fichero} no cita {modelo.valor}")
                else:
                    self.assertIn("puente/modelos.py", texto, "el río tiene que decir dónde vive la lista")


class Reponer(unittest.TestCase):
    def test_es_idempotente_y_respeta_lo_del_servidor(self) -> None:
        with _Casa() as casa:
            anadidos, motivo = mod.repone(casa.global_)
            self.assertIsNone(motivo)
            self.assertEqual(anadidos, [m.valor for m in mod.MODELOS])
            despues = casa.global_.read_bytes()
            datos = json.loads(despues)
            self.assertEqual(datos["additionalModelOptionsCache"][0]["value"], "del-servidor", "lo del servidor va primero y no se toca")
            self.assertEqual(mod.repone(casa.global_), ([], None))
            self.assertEqual(casa.global_.read_bytes(), despues, "la segunda pasada reescribió el fichero")
            self.assertEqual(oct(casa.global_.stat().st_mode & 0o777), "0o600")

    def test_un_config_ilegible_no_rompe_el_resto_y_se_nombra(self) -> None:
        with _Casa() as casa:
            roto = casa.config_dir / ".claude.json"
            roto.write_text("{ roto", encoding="utf-8")
            resultados = {str(c): mod.repone(c) for c in mod.configs_vigilados({})}
            self.assertIn("ilegible", resultados[str(roto)][1])
            self.assertEqual(resultados[str(casa.global_)][1], None)
            self.assertTrue(resultados[str(casa.global_)][0])

    def test_escritura_atomica_no_deja_a_medias(self) -> None:
        with _Casa() as casa:
            antes = casa.global_.read_bytes()
            with mock.patch("os.replace", side_effect=OSError("disco lleno")):
                with self.assertRaises(OSError):
                    mod.repone(casa.global_)
            self.assertEqual(casa.global_.read_bytes(), antes)
            self.assertEqual([p.name for p in casa.casa.iterdir() if p.name.startswith(".claude.json.")], [],
                             "quedó un temporal suelto")


class RutasSinMaquina(unittest.TestCase):
    def test_configs_vigilados_solo_bajo_home_o_config_dir(self) -> None:
        """El canario anti-regresión de GOAL §5: ninguna ruta de una máquina u organización."""

        with _Casa() as casa:
            (casa.casa / "cuentas" / "a").mkdir(parents=True)
            (casa.casa / "cuentas" / "a" / ".claude.json").write_text("{}", encoding="utf-8")
            configs = mod.configs_vigilados({"configs": ["~/cuentas", "~/otro.json"]})
            self.assertEqual(configs[0], casa.global_)
            self.assertIn(casa.config_dir / ".claude.json", configs)
            self.assertIn(casa.casa / "cuentas" / "a" / ".claude.json", configs)
            for ruta in configs:
                self.assertTrue(str(ruta).startswith(str(casa.casa)), ruta)
        fuente = (RAIZ / "puente/modelos.py").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"/Users/|/home/|\.secrets|Desktop", fuente), "una ruta de máquina en el código")

    def test_el_plist_y_el_reponedor_no_llevan_rutas_ajenas(self) -> None:
        with _Casa() as casa:
            configs = mod.configs_vigilados({})
            plist = mod.contenido_plist(sys.executable, mod.ruta_reponedor(), configs, mod.ruta_log())
            self.assertIn(mod.ETIQUETA, plist)
            self.assertNotIn("anubis", plist.lower())
            for linea in plist.splitlines():
                if "<string>/" in linea and "python" not in linea:
                    self.assertIn(str(casa.casa), linea, linea)
            reponedor = mod.contenido_reponedor(configs)
            compile(reponedor, "modelos-reponer.py", "exec")  # es Python válido
            self.assertIn(mod.MARCA, reponedor)
            for modelo in mod.MODELOS:
                self.assertIn(modelo.valor, reponedor)

    def test_importar_no_hace_nada(self) -> None:
        with TemporaryDirectory() as tmp:
            r = subprocess.run([sys.executable, "-c", "import puente.modelos"], capture_output=True, text=True, cwd=RAIZ,
                               env={**os.environ, "HOME": tmp, "CLAUDE_CONFIG_DIR": str(Path(tmp) / "cfg")})
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(sorted(p.name for p in Path(tmp).iterdir()), [], "importar creó ficheros")


class InstalarYQuitar(unittest.TestCase):
    def test_instalar_escribe_todo_y_quitar_lo_devuelve(self) -> None:
        with _Casa() as casa:
            ajustes = casa.config_dir / "settings.json"
            original = '{\n   "model": "x",\n "hooks": {"Stop": []}\n}\n'
            ajustes.write_text(original, encoding="utf-8")
            ordenes, ejecutor = _anotador()
            lineas = mod.instalar(perfil={}, ejecutor=ejecutor, plataforma="darwin")
            texto = "\n".join(lineas)
            self.assertTrue(mod.ruta_reponedor().is_file())
            self.assertTrue(mod.ruta_plist().is_file())
            self.assertEqual(oct(mod.ruta_reponedor().stat().st_mode & 0o777), "0o700")
            self.assertEqual([o[:2] for o in ordenes], [["launchctl", "bootout"], ["launchctl", "enable"], ["launchctl", "bootstrap"]])
            self.assertEqual(ordenes[-1][-1], str(mod.ruta_plist()))
            self.assertTrue(mod.tiene_hook(ajustes))
            datos = json.loads(ajustes.read_text(encoding="utf-8"))
            self.assertEqual(datos["hooks"]["Stop"], [], "lo ajeno se conserva")
            for nombre, _ in mod.ATAJOS:
                self.assertTrue((mod.directorio_atajos() / nombre).is_file())
            self.assertIn("Repuesto ahora", texto)
            self.assertEqual(json.loads(casa.global_.read_text(encoding="utf-8"))["additionalModelOptionsCache"][1]["value"], mod.MODELOS[0].valor)
            # reinstalar es idempotente: un solo hook, no dos
            mod.instalar(perfil={}, ejecutor=ejecutor, plataforma="darwin")
            self.assertEqual(sum(1 for e in json.loads(ajustes.read_text(encoding="utf-8"))["hooks"]["SessionStart"] if mod.MARCA in json.dumps(e)), 1)
            filas = mod.estado(perfil={}, ejecutor=ejecutor, plataforma="darwin")
            por_nombre = {f.nombre: f.estado for f in filas}
            self.assertEqual(por_nombre["reponedor"], "ok")
            self.assertEqual(por_nombre["agente launchd"], "ok")
            self.assertEqual(por_nombre["hook SessionStart"], "ok")
            self.assertEqual(por_nombre["acceso de la cuenta"], "no_comprobado")
            # quitar: ajustes byte a byte, el menú conserva sus entradas
            lineas = mod.quitar(ejecutor=ejecutor, plataforma="darwin")
            self.assertEqual(ajustes.read_text(encoding="utf-8"), original)
            self.assertFalse(mod.ruta_plist().exists())
            self.assertFalse(mod.ruta_reponedor().exists())
            self.assertIn(mod.MODELOS[0].valor, casa.global_.read_text(encoding="utf-8"), "quitar borró entradas del menú")
            self.assertIn("no se borran", "\n".join(lineas))

    def test_no_pisa_un_maxcode_ajeno(self) -> None:
        with _Casa() as casa:
            ajeno = mod.directorio_atajos() / "maxcode"
            ajeno.parent.mkdir(parents=True)
            ajeno.write_text("#!/bin/sh\necho mio\n", encoding="utf-8")
            _, ejecutor = _anotador()
            lineas = mod.instalar(perfil={}, ejecutor=ejecutor, plataforma="linux")
            self.assertIn("NO es nuestro", "\n".join(lineas))
            self.assertEqual(ajeno.read_text(encoding="utf-8"), "#!/bin/sh\necho mio\n")
            self.assertIn("solo existe en macOS", "\n".join(lineas))
            self.assertFalse(mod.ruta_plist().exists())
            mod.instalar(perfil={}, ejecutor=ejecutor, plataforma="linux", forzar=True)
            self.assertIn(mod.MARCA, ajeno.read_text(encoding="utf-8"))
            self.assertEqual(mod.estado(perfil={}, ejecutor=ejecutor, plataforma="linux")[1].estado, "no_comprobado")

    def test_el_reponedor_instalado_corre_solo_y_estado_lo_ve_desactualizado(self) -> None:
        with _Casa() as casa:
            _, ejecutor = _anotador()
            mod.instalar(perfil={}, ejecutor=ejecutor, plataforma="linux")
            casa.global_.write_text("{}", encoding="utf-8")
            r = subprocess.run([sys.executable, str(mod.ruta_reponedor())], capture_output=True, text=True,
                               env={**os.environ, "HOME": str(casa.casa), "CLAUDE_CONFIG_DIR": str(casa.config_dir)})
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("añadidos", r.stdout)
            self.assertEqual(len(json.loads(casa.global_.read_text(encoding="utf-8"))["additionalModelOptionsCache"]), len(mod.MODELOS))
            mod.ruta_reponedor().write_text(mod.contenido_reponedor([]) , encoding="utf-8")
            filas = mod.estado(perfil={}, ejecutor=ejecutor, plataforma="linux")
            self.assertEqual(filas[0].estado, "desactualizado")

    def test_seco_no_escribe(self) -> None:
        with _Casa() as casa:
            _, ejecutor = _anotador()
            lineas = mod.instalar(perfil={}, ejecutor=ejecutor, plataforma="darwin", seco=True)
            self.assertTrue(all("(seco)" in l for l in lineas if not l.startswith("      ")), lineas)
            self.assertFalse((casa.casa / ".cosmos").exists())
            self.assertFalse(mod.ruta_plist().exists())

    def test_el_modelo_duro_sale_del_perfil(self) -> None:
        self.assertEqual(mod.modelo_duro({}), mod.MODELO_DURO_POR_DEFECTO)
        self.assertEqual(mod.modelo_duro({"duro": "claude-fable-5-1"}), "claude-fable-5-1")
        atajo = mod.contenido_atajo("maxcode", "max", "claude-fable-5-1", Path("/tmp/x.log"))
        self.assertIn('MODELO="claude-fable-5-1"', atajo)
        self.assertIn("COSMOS_VERIFICA", atajo)
        self.assertNotIn("COSMOS_VERIFICA", mod.contenido_atajo("ultracode", "ultracode", "claude-opus-5", Path("/tmp/x.log")))


if __name__ == "__main__":
    unittest.main()
