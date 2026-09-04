"""Los guardarraíles se prueban viéndolos bloquear de verdad.

Un hook instalado que no bloquea es peor que ninguno, porque además tranquiliza
(spec/GUARDARRAILES.md). Así que aquí se instala el hook en un repositorio Git
real, se rompe el árbol y se comprueba que `git commit` no ocurre.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from cosmos.cli import ejecutar, nichos_de_configuracion
from cosmos.guardarrailes import (
    EVENTOS_SESION,
    RUTA_AJUSTES,
    ErrorEnganche,
    ErrorSalto,
    ahora_utc,
    analizar_duracion,
    desenganchar,
    enganchar,
    enganchar_sesion,
    estado_saltos,
    registrar_salto,
    ruta_saltos,
)

REPO_COSMOS = Path(__file__).resolve().parents[1]

GALAXIA = """---
cosmos: galaxia
nombre: prueba
resumen: Galaxia minima para probar los guardarrailes.
---

Cuerpo de la galaxia.
"""

SISTEMA = """---
cosmos: sistema-solar
nombre: web
padre: ""
resumen: Un sitio que carga y no se cae.
---

Cuerpo del sistema.
"""

OCEANO = """---
cosmos: oceano
nombre: verificar
moja: ["**"]
resumen: Nada se declara hecho sin haberlo visto funcionar.
---

Dos capas: la máquina y los ojos.
"""

PUEBLO = """---
cosmos: pueblo
nombre: medir-anchos
padre: web
resumen: Mide anchos reales en el navegador, sin opinar.
---

https://github.com/pruebas-sinteticas/medir-anchos · MIT · 0★ · último push 2026-01-01 (comprobado 2026-01-01)

Cuerpo del pueblo (E21 exige URL de repositorio u `origen: propio` con guion).

```bash
python3 -m cosmos abrir medir-anchos
```
"""

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


def _git(repo: Path, *argumentos: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *argumentos], cwd=repo, capture_output=True, text=True, check=False
    )


def _repo_cosmos(base: Path) -> Path:
    """Un repositorio Git con un árbol COSMOS mínimo, ya commiteado y en verde."""

    base.mkdir(parents=True, exist_ok=True)
    arbol = base / "arbol"
    (arbol / "pueblos" / "medir-anchos").mkdir(parents=True)
    (arbol / "galaxia.md").write_text(GALAXIA, encoding="utf-8")
    (arbol / "web.md").write_text(SISTEMA, encoding="utf-8")
    (arbol / "oceano-verificar.md").write_text(OCEANO, encoding="utf-8")
    (arbol / "pueblos" / "medir-anchos" / "SKILL.md").write_text(PUEBLO, encoding="utf-8")
    (base / "cosmos.toml").write_text(CONFIG, encoding="utf-8")
    (base / ".gitignore").write_text(".cosmos/\n", encoding="utf-8")
    # Orden de arranque de un árbol nuevo: primero la vista plana (E19), luego el
    # índice (E15). `arrancar` sale en rojo en la primera pasada justo porque no
    # fabrica el índice él solo, que es lo que se quiere.
    ejecutar(["arrancar", "--config", str(base / "cosmos.toml")])
    codigo = ejecutar(["generar", "--config", str(base / "cosmos.toml")])
    assert codigo == 0, "el árbol de prueba tiene que nacer en verde"
    for orden in (
        ["init", "--quiet"],
        ["config", "user.email", "cosmos@example.invalid"],
        ["config", "user.name", "cosmos"],
        ["add", "--all"],
        ["commit", "--quiet", "-m", "inicial"],
    ):
        resultado = _git(base, *orden)
        assert resultado.returncode == 0, resultado.stderr
    return base.resolve()


def _huella(raiz: Path) -> dict[str, str]:
    """Nombre y contenido de todo lo que cuelga de una ruta, recursivamente."""

    huella: dict[str, str] = {}
    for camino in sorted(raiz.rglob("*")):
        clave = str(camino.relative_to(raiz))
        if camino.is_dir():
            huella[clave] = "<dir>"
        else:
            huella[clave] = hashlib.sha256(camino.read_bytes()).hexdigest()
    return huella


def _commits(repo: Path) -> int:
    return int(_git(repo, "rev-list", "--count", "HEAD").stdout.strip() or 0)


class Valvula(unittest.TestCase):
    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="cosmos-valvula-")
        self.base = Path(self.temporal.name)
        self.log = ruta_saltos(self.base)

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def test_la_caducidad_es_obligatoria_y_no_pasa_de_treinta_dias(self) -> None:
        self.assertEqual(timedelta(days=7), analizar_duracion("7d"))
        for invalido in ("", "siempre", "0d", "31d", "7"):
            with self.assertRaises(ErrorSalto):
                analizar_duracion(invalido)

    def test_no_se_puede_saltar_todo_ni_un_codigo_inventado(self) -> None:
        for codigo in ("todo", "*", "E99"):
            with self.assertRaises(ErrorSalto):
                registrar_salto(self.log, codigo, "urgencia", timedelta(days=1))

    def test_el_motivo_es_obligatorio(self) -> None:
        with self.assertRaises(ErrorSalto):
            registrar_salto(self.log, "E16", "   ", timedelta(days=1))

    def test_el_registro_solo_crece(self) -> None:
        registrar_salto(self.log, "E16", "primera", timedelta(days=1))
        registrar_salto(self.log, "E16", "renovada", timedelta(days=2))
        lineas = self.log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(2, len(lineas))
        self.assertEqual("primera", json.loads(lineas[0])["motivo"])
        activos, _ = estado_saltos(self.log)
        self.assertEqual(["renovada"], [salto.motivo for salto in activos])

    def test_un_salto_caducado_vuelve_a_poner_rojo_y_recuerda_el_motivo(self) -> None:
        ahora = ahora_utc()
        registrar_salto(
            self.log, "E16", "importando 40 skills", timedelta(days=1), ahora=ahora - timedelta(days=3)
        )
        activos, caducados = estado_saltos(self.log, ahora=ahora)
        self.assertEqual([], activos)
        self.assertEqual(["E16"], [salto.codigo for salto in caducados])
        self.assertEqual("importando 40 skills", caducados[0].motivo)

    def test_dias_restantes_redondea_hacia_arriba(self) -> None:
        ahora = ahora_utc()
        registrar_salto(self.log, "E11", "obras", timedelta(days=5), ahora=ahora)
        activos, _ = estado_saltos(self.log, ahora=ahora)
        self.assertEqual(5, activos[0].dias_restantes(ahora))


class ValvulaEnLaSalida(unittest.TestCase):
    """Un verde que oculta un salto es una mentira; basta una para perderlas todas."""

    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="cosmos-salida-")
        self.base = Path(self.temporal.name) / "repo"
        self.base.mkdir(parents=True)
        arbol = self.base / "arbol"
        (arbol / "pueblos" / "medir-anchos").mkdir(parents=True)
        (arbol / "galaxia.md").write_text(GALAXIA, encoding="utf-8")
        (arbol / "web.md").write_text(SISTEMA, encoding="utf-8")
        (arbol / "oceano-verificar.md").write_text(OCEANO, encoding="utf-8")
        (arbol / "pueblos" / "medir-anchos" / "SKILL.md").write_text(PUEBLO, encoding="utf-8")
        self.config = self.base / "cosmos.toml"
        self.config.write_text(CONFIG, encoding="utf-8")
        self.ejecutar(["arrancar", "--config", str(self.config)])
        self.assertEqual(0, self.ejecutar(["generar", "--config", str(self.config)])[0])
        self.assertEqual(0, self.ejecutar(["arrancar", "--config", str(self.config)])[0])

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def ejecutar(self, argumentos: list[str]) -> tuple[int, str]:
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(salida):
            codigo = ejecutar(argumentos)
        return codigo, salida.getvalue()

    def test_sin_saltos_la_salida_dice_verde_a_secas(self) -> None:
        codigo, salida = self.ejecutar(["validar", "--config", str(self.config)])
        self.assertEqual(0, codigo, salida)
        self.assertIn("COSMOS  verde  0 errores", salida)

    def test_con_un_salto_activo_la_salida_nunca_dice_solo_verde(self) -> None:
        registrar_salto(ruta_saltos(self.base), "E16", "importando 40 skills", timedelta(days=5))
        codigo, salida = self.ejecutar(["validar", "--config", str(self.config)])
        self.assertEqual(0, codigo, salida)
        self.assertNotIn("COSMOS  verde  0 errores", salida)
        self.assertIn("verde (1 salto activo: E16, caduca en 5 d)", salida)
        for linea in salida.splitlines():
            if "verde" in linea:
                self.assertIn("salto activo", linea, linea)

    def test_ninguna_salida_dice_verde_a_secas_con_un_salto_vivo(self) -> None:
        registrar_salto(ruta_saltos(self.base), "E16", "obras", timedelta(days=3))
        for orden in (["validar"], ["compilar"], ["arrancar"], ["generar"]):
            codigo, salida = self.ejecutar([*orden, "--config", str(self.config)])
            self.assertEqual(0, codigo, salida)
            for linea in salida.splitlines():
                if "verde" in linea:
                    self.assertIn("salto activo", linea, f"{orden}: {linea}")

    def test_el_json_tambien_declara_los_saltos(self) -> None:
        registrar_salto(ruta_saltos(self.base), "E16", "obras", timedelta(days=2))
        codigo, salida = self.ejecutar(["validar", "--config", str(self.config), "--json"])
        self.assertEqual(0, codigo, salida)
        datos = json.loads(salida)
        self.assertEqual(["E16"], [salto["codigo"] for salto in datos["saltos_activos"]])
        self.assertEqual([], datos["saltos_caducados"])

    def test_un_salto_caducado_no_omite_nada_y_lo_dice(self) -> None:
        log = ruta_saltos(self.base)
        registrar_salto(log, "E16", "obras de agosto", timedelta(days=1), ahora=ahora_utc() - timedelta(days=9))
        codigo, salida = self.ejecutar(["validar", "--config", str(self.config)])
        self.assertEqual(0, codigo, salida)
        self.assertIn("SALTO CADUCADO", salida)
        self.assertIn("obras de agosto", salida)


class Enganche(unittest.TestCase):
    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="cosmos-enganche-")
        self.repo = _repo_cosmos(Path(self.temporal.name) / "repo")

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def test_no_pisa_un_pre_commit_ajeno(self) -> None:
        hook = self.repo / ".git" / "hooks" / "pre-commit"
        ajeno = "#!/bin/sh\necho 'hook de otro'\n"
        hook.write_text(ajeno, encoding="utf-8")
        hook.chmod(0o755)
        with self.assertRaises(ErrorEnganche):
            enganchar(self.repo)
        self.assertEqual(ajeno, hook.read_text(encoding="utf-8"))
        with self.assertRaises(ErrorEnganche):
            desenganchar(self.repo)
        self.assertEqual(ajeno, hook.read_text(encoding="utf-8"))

    def test_desenganchar_deja_el_repositorio_identico(self) -> None:
        antes_hooks = _huella(self.repo / ".git" / "hooks")
        antes_arbol = _huella(self.repo / "arbol")
        enganchar(self.repo, con_pruebas=False)
        self.assertNotEqual(antes_hooks, _huella(self.repo / ".git" / "hooks"))
        ruta, estado = desenganchar(self.repo)
        self.assertEqual("eliminado", estado)
        self.assertFalse(ruta.exists())
        self.assertEqual(antes_hooks, _huella(self.repo / ".git" / "hooks"))
        self.assertEqual(antes_arbol, _huella(self.repo / "arbol"))

    def test_desenganchar_sin_hook_no_es_error(self) -> None:
        _, estado = desenganchar(self.repo)
        self.assertEqual("ausente", estado)

    def test_reenganchar_es_idempotente(self) -> None:
        _, primero = enganchar(self.repo, con_pruebas=False)
        ruta, segundo = enganchar(self.repo, con_pruebas=False)
        self.assertEqual(("creado", "actualizado"), (primero, segundo))
        self.assertTrue(ruta.stat().st_mode & 0o111)


class EnrutadoDeSesion(unittest.TestCase):
    """El cableado tiene que llegar a TODAS las herramientas que el guard vigila.

    G05 sabía tapar `Grep`, `Glob` y `Task` desde el principio —están en
    `puente.sesion.HERRAMIENTAS_VIGILADAS`— pero el enrutado solo mandaba
    `Bash|Read`: una puerta construida y sin cablear, por la que un secreto
    encontrado con `Grep` entraba en claro. Se comprueba con el fichero de ajustes
    que `enganchar_sesion` escribe de verdad y con una llamada real al guard, no
    leyendo el módulo.
    """

    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="cosmos-enrutado-")
        self.base = Path(self.temporal.name).resolve()
        subprocess.run(["git", "init", "-q", str(self.base)], check=True, capture_output=True)

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def test_los_ajustes_escritos_enrutan_las_cinco_herramientas(self) -> None:
        enganchar_sesion(self.base)
        ajustes = json.loads((self.base / RUTA_AJUSTES).read_text(encoding="utf-8"))
        matcher = ajustes["hooks"]["PostToolUse"][0]["matcher"]
        self.assertEqual(["Bash", "Glob", "Grep", "Read", "Task"], sorted(matcher.split("|")))

    def test_el_enrutado_cubre_exactamente_lo_que_el_guard_vigila(self) -> None:
        """Anti-deriva: la lista de aquí y la del guard no pueden separarse."""

        from puente.sesion import HERRAMIENTAS_VIGILADAS

        enrutado = dict(EVENTOS_SESION)["PostToolUse"].split("|")
        self.assertEqual(sorted(HERRAMIENTAS_VIGILADAS), sorted(enrutado))

    def test_el_guard_tapa_de_verdad_un_secreto_hallado_con_grep(self) -> None:
        evento = {
            "hook_event_name": "PostToolUse",
            "tool_name": "Grep",
            "tool_response": "hallado AKIAIOSFODNN7EXAMPLE en el fichero",
        }
        resultado = subprocess.run(
            [sys.executable, "-m", "puente.sesion"],
            input=json.dumps(evento), capture_output=True, text=True, cwd=REPO_COSMOS,
        )
        self.assertEqual(0, resultado.returncode, resultado.stderr)
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", resultado.stdout)
        self.assertIn("REDACTADO", resultado.stdout)


class HookQueBloquea(unittest.TestCase):
    """El gate instalado tiene que impedir un commit con el árbol roto, de verdad."""

    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="cosmos-bloqueo-")
        self.repo = _repo_cosmos(Path(self.temporal.name) / "repo")
        enganchar(self.repo, interprete=sys.executable, con_pruebas=False)

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def test_un_commit_sano_pasa(self) -> None:
        (self.repo / "LEEME.txt").write_text("nada que validar\n", encoding="utf-8")
        self.assertEqual(0, _git(self.repo, "add", "LEEME.txt").returncode)
        resultado = _git(self.repo, "commit", "-m", "sano")
        self.assertEqual(0, resultado.returncode, resultado.stdout + resultado.stderr)
        self.assertEqual(2, _commits(self.repo))

    def _falsificar_indice(self) -> None:
        (self.repo / "arbol" / "COSMOS.md").write_text(
            "<!-- Generado por cosmos generar. No editar a mano. -->\n\n"
            "# COSMOS — mentira-total\n\n## Sistemas solares\n\n"
            "- `no-existe` — Un oficio inventado que no está en el árbol.\n\n"
            "## Oceanos\n\n- Ninguno\n",
            encoding="utf-8",
        )

    def test_un_indice_roto_no_llega_a_commit(self) -> None:
        self._falsificar_indice()
        self.assertEqual(0, _git(self.repo, "add", "arbol/COSMOS.md").returncode)
        resultado = _git(self.repo, "commit", "-m", "roto")
        self.assertNotEqual(0, resultado.returncode, "el hook dejó pasar un árbol roto")
        self.assertEqual(1, _commits(self.repo))
        # Un gate que bloquea sin decir por qué se desinstala el mismo día.
        explicacion = resultado.stdout + resultado.stderr
        self.assertIn("E15", explicacion, explicacion)
        self.assertIn("commit bloqueado", explicacion, explicacion)
        self.assertIn("cosmos saltar", explicacion, explicacion)

    def test_la_valvula_desbloquea_el_paso_de_validacion_del_gate(self) -> None:
        """El salto tiene que llegar al hook, o la válvula no existe donde duele.

        El registro no se versiona, así que la instantánea del índice no lo trae:
        el gate lo copia dentro a propósito. Sin eso, quien tiene la urgencia un
        viernes se encuentra la válvula puesta y el guard igual de cerrado, y
        entonces arranca el guard entero, que es justo lo que se quiere evitar.

        Alcance exacto: la válvula cubre los códigos E00–E19 del **validador**,
        también dentro del gate. NO silencia las suites de tests — un test que
        afirma que el árbol está verde tiene que seguir dando rojo, o dejaría de
        significar nada. Este repositorio de prueba no trae suites, y el hook se
        instala con `con_pruebas=False`.
        """

        self._falsificar_indice()
        self.assertEqual(0, _git(self.repo, "add", "arbol/COSMOS.md").returncode)
        self.assertNotEqual(0, _git(self.repo, "commit", "-m", "roto").returncode)
        registrar_salto(
            ruta_saltos(self.repo), "E15", "importando 40 skills, se reorganiza el lunes", timedelta(days=7)
        )
        resultado = _git(self.repo, "commit", "-m", "roto pero con salto")
        self.assertEqual(0, resultado.returncode, resultado.stdout + resultado.stderr)
        self.assertEqual(2, _commits(self.repo))

    def test_un_fichero_sensible_nuevo_no_llega_a_commit(self) -> None:
        (self.repo / ".env").write_text("TOKEN=lo_que_sea\n", encoding="utf-8")
        self.assertEqual(0, _git(self.repo, "add", "--force", ".env").returncode)
        resultado = _git(self.repo, "commit", "-m", "sensible")
        self.assertNotEqual(0, resultado.returncode, "el hook dejó pasar un fichero sensible")
        self.assertEqual(1, _commits(self.repo))


class NichosEnConfiguracion(unittest.TestCase):
    """El nicho activo no puede vivir en un flag que hay que recordar (H09)."""

    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="cosmos-nichos-")
        self.base = Path(self.temporal.name)

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def _config(self, texto: str) -> Path:
        ruta = self.base / "cosmos.toml"
        ruta.write_text(CONFIG + texto, encoding="utf-8")
        return ruta

    def test_sin_seccion_significa_todos(self) -> None:
        self.assertIsNone(nichos_de_configuracion(self._config("")))

    def test_lista_vacia_significa_todos(self) -> None:
        self.assertIsNone(nichos_de_configuracion(self._config("\n[nichos]\nactivos = []\n")))

    def test_lista_con_nombres_se_respeta(self) -> None:
        self.assertEqual(["web"], nichos_de_configuracion(self._config('\n[nichos]\nactivos = ["web"]\n')))

    def test_el_repositorio_declara_su_nicho_activo(self) -> None:
        self.assertIsNotNone(nichos_de_configuracion.__doc__)
        self.assertIsNone(nichos_de_configuracion(REPO_COSMOS / "cosmos.toml"))


if __name__ == "__main__":
    unittest.main()
