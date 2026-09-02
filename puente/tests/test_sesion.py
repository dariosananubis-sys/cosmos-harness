"""Los guardarraíles de sesión se prueban viéndolos denegar, bloquear y tapar.

Un guard que nunca se ha visto actuar no se distingue de uno roto, y encima
tranquiliza. Cada prueba de aquí construye el caso que el guard tiene que parar
y exige el efecto exacto: `deny` en la herramienta, `block` en el cierre, el
valor sustituido en la salida. Y su pareja, siempre: el caso vecino que NO debe
dispararlo, porque un guard que bloquea todo tampoco prueba nada.
"""

from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from cosmos.guardarrailes import (
    EVENTOS_SESION,
    ErrorEnganche,
    desenganchar_sesion,
    enganchar_sesion,
    registrar_salto,
    ruta_saltos,
)
from cosmos.cli import ejecutar
from puente import sesion
from puente.secretos import redactar_texto
from puente.tests.comun import arbol_minimo, repo_git

CONFIG = """[presupuesto]
entrada = {entrada}
resumen = 120
oceanos = 7
galaxia_lineas = 40

[raiz]
arbol = "arbol"
indice = "arbol/COSMOS.md"

[medicion]
metodo = "aprox"

[compilacion]
destino = ".cosmos/vista"
manifiesto = ".cosmos/compilado.json"
"""


def _repositorio(base: Path, *, entrada: int = 4000, lecturas: tuple[str, ...] = ()) -> Path:
    """Un repositorio con árbol mínimo, para no depender de la galaxia real."""

    raiz = repo_git(base / "repo")
    (raiz / "arbol").mkdir(parents=True, exist_ok=True)
    arbol_minimo(raiz / "arbol")
    texto = CONFIG.format(entrada=entrada)
    if lecturas:
        listado = ", ".join(json.dumps(ruta) for ruta in lecturas)
        texto += f"\n[sesion]\nlecturas_exigidas = [{listado}]\n"
    (raiz / "cosmos.toml").write_text(texto, encoding="utf-8")
    return raiz


def _en_verde(raiz: Path) -> Path:
    """Deja el árbol de prueba realmente en verde: índice generado y vista compilada.

    Un árbol recién escrito está en rojo por E15 y E19, así que sin este paso las
    pruebas del caso «no bloquea» probarían el rojo por la puerta de atrás.
    """

    config = raiz / "cosmos.toml"
    with contextlib.redirect_stdout(io.StringIO()):
        for orden in (["arrancar"], ["generar"], ["arrancar"]):
            codigo = ejecutar([*orden, "--config", str(config)])
    if codigo:
        raise AssertionError("el árbol de prueba no llega a verde")
    return raiz


def _evento(raiz: Path, **campos: object) -> dict:
    base = {"session_id": "sesion-de-prueba", "cwd": str(raiz)}
    base.update(campos)
    return base


def _decidir(raiz: Path, evento: dict):
    return sesion.decidir(evento, config_path=raiz / "cosmos.toml")[0]


class Segmentacion(unittest.TestCase):
    """Cada orden de un bloque se juzga sola; el entrecomillado no se rompe."""

    def test_un_punto_y_coma_dentro_de_comillas_no_parte_la_orden(self) -> None:
        self.assertEqual(sesion.ordenes('echo "hola; adios" > salida.txt'), ['echo "hola; adios" > salida.txt'])

    def test_un_bloque_se_parte_en_sus_ordenes(self) -> None:
        self.assertEqual(
            sesion.ordenes("ls -la && echo x >> COSMOS.md ; date"),
            ["ls -la", "echo x >> COSMOS.md", "date"],
        )

    def test_el_verbo_de_una_orden_no_contamina_el_objetivo_de_otra(self) -> None:
        # Sin segmentar, el `>` de la primera y el `COSMOS.md` de la segunda se
        # emparejan y el guard bloquea con un motivo que nadie escribió.
        bloque = "echo hola > /tmp/inocente.txt\ncat COSMOS.md"
        objetivos = [o for orden in sesion.ordenes(bloque) for o in sesion.objetivos_de_escritura(orden)]
        self.assertEqual(objetivos, ["/tmp/inocente.txt"])

    def test_reconoce_los_escritores_declarados(self) -> None:
        self.assertEqual(sesion.objetivos_de_escritura("tee -a registro.log < /dev/null"), ["registro.log"])
        self.assertEqual(sesion.objetivos_de_escritura("cp origen.json destino.json"), ["destino.json"])
        self.assertEqual(sesion.objetivos_de_escritura("sed -i '' 's/a/b/' fichero.md"), ["fichero.md"])
        self.assertEqual(sesion.objetivos_de_escritura("cat fichero.md"), [])


class RutasDeVeredicto(unittest.TestCase):
    """G03: el índice, la vista, el manifiesto y el registro de la válvula."""

    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="sesion-veredicto-")
        self.raiz = _repositorio(Path(self.temporal.name))

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def _pre(self, herramienta: str, entrada_tool: dict):
        return _decidir(
            self.raiz,
            _evento(self.raiz, hook_event_name="PreToolUse", tool_name=herramienta, tool_input=entrada_tool),
        )

    def test_deniega_escribir_el_indice_a_mano_por_bash(self) -> None:
        decision = self._pre("Bash", {"command": "echo falso >> arbol/COSMOS.md"})
        self.assertEqual(decision.accion, "denegar")
        self.assertIn("COSMOS.md", decision.motivo)

    def test_deniega_escribir_el_registro_de_la_valvula(self) -> None:
        # Un salto escrito a mano no es una excepción registrada: es una firma
        # propia. Un guardarraíl que no protege su válvula no es un guardarraíl.
        decision = self._pre("Write", {"file_path": str(ruta_saltos(self.raiz))})
        self.assertEqual(decision.accion, "denegar")

    def test_el_productor_autorizado_pasa(self) -> None:
        self.assertEqual(self._pre("Bash", {"command": "python3 -m cosmos generar"}).accion, "pasar")

    def test_el_permiso_de_una_orden_no_cubre_a_la_siguiente(self) -> None:
        # Aquí es donde la segmentación se gana el sueldo: sin ella, el bloque
        # entero cuenta como «lo ejecuta cosmos» y la escritura a mano de la
        # segunda orden entra de gorra detrás del permiso de la primera.
        decision = self._pre("Bash", {"command": "python3 -m cosmos generar && echo falso >> arbol/COSMOS.md"})
        self.assertEqual(decision.accion, "denegar")

    def test_una_escritura_cualquiera_pasa(self) -> None:
        self.assertEqual(self._pre("Write", {"file_path": str(self.raiz / "notas.md")}).accion, "pasar")

    def test_la_valvula_desarma_el_guard(self) -> None:
        registrar_salto(ruta_saltos(self.raiz), "G03", "reescribiendo el índice a mano", timedelta(days=1))
        decision = self._pre("Bash", {"command": "echo falso >> arbol/COSMOS.md"})
        self.assertEqual(decision.accion, "pasar")

    def test_la_denegacion_se_renderiza_como_deny_y_como_exit_2(self) -> None:
        decision = self._pre("Bash", {"command": "echo falso >> arbol/COSMOS.md"})
        cuerpo = json.loads(sesion.como_json(decision, "PreToolUse"))
        self.assertEqual(cuerpo["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(sesion.como_exit2(decision)[1], 2)


class MarcaDeLectura(unittest.TestCase):
    """G04: «lo he leído» deja de ser una afirmación y pasa a ser comprobable."""

    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="sesion-lectura-")
        self.raiz = _repositorio(Path(self.temporal.name), lecturas=("CONTRATO.md",))
        self.contrato = self.raiz / "CONTRATO.md"
        self.contrato.write_text("Contrato del repositorio.\n" * 4, encoding="utf-8")

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def _escribir(self):
        return _decidir(
            self.raiz,
            _evento(
                self.raiz,
                hook_event_name="PreToolUse",
                tool_name="Write",
                tool_input={"file_path": str(self.raiz / "obra.md")},
            ),
        )

    def _leer(self, **extra: object):
        return _decidir(
            self.raiz,
            _evento(
                self.raiz,
                hook_event_name="PostToolUse",
                tool_name="Read",
                tool_input={"file_path": str(self.contrato), **extra},
                tool_response={"output": "leído", "exit_code": 0},
            ),
        )

    def test_sin_haber_leido_no_se_escribe(self) -> None:
        self.assertEqual(self._escribir().accion, "denegar")

    def test_leerlo_entero_abre_la_puerta(self) -> None:
        self._leer()
        self.assertEqual(self._escribir().accion, "pasar")

    def test_una_lectura_parcial_no_cuenta(self) -> None:
        self._leer(limit=2)
        self.assertEqual(self._escribir().accion, "denegar")

    def test_editar_el_fichero_invalida_la_marca(self) -> None:
        self._leer()
        self.contrato.write_text("Otro contrato distinto.\n", encoding="utf-8")
        self.assertEqual(self._escribir().accion, "denegar")

    def test_una_marca_copiada_a_mano_no_vale(self) -> None:
        # La marca lleva dentro la sesión a la que pertenece, no solo el sitio
        # donde está guardada: copiarla a la carpeta de otra sesión no la
        # convierte en una lectura de esa otra sesión.
        self._leer()
        origen = sesion.ruta_marca(self.raiz, "sesion-de-prueba", self.contrato)
        destino = sesion.ruta_marca(self.raiz, "otra-ventana", self.contrato)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(origen.read_text(encoding="utf-8"), encoding="utf-8")
        self.assertFalse(sesion.lectura_valida(self.raiz, "otra-ventana", self.contrato))

    def test_las_marcas_no_se_pueden_escribir_a_mano(self) -> None:
        decision = _decidir(
            self.raiz,
            _evento(
                self.raiz,
                hook_event_name="PreToolUse",
                tool_name="Write",
                tool_input={"file_path": str(sesion.ruta_marca(self.raiz, "sesion-de-prueba", self.contrato))},
            ),
        )
        self.assertEqual(decision.accion, "denegar")

    def test_la_marca_no_se_hereda_de_otra_sesion(self) -> None:
        self._leer()
        ajeno = _evento(self.raiz, hook_event_name="PreToolUse", tool_name="Write", tool_input={"file_path": "x.md"})
        ajeno["session_id"] = "otra-ventana"
        self.assertEqual(_decidir(self.raiz, ajeno).accion, "denegar")

    def test_precompact_borra_la_marca_sin_condiciones(self) -> None:
        # Tras compactar, lo leído puede haber salido del contexto: la marca
        # seguiría siendo cierta como historia y falsa como afirmación.
        self._leer()
        decision = _decidir(self.raiz, _evento(self.raiz, hook_event_name="PreCompact"))
        self.assertEqual(decision.accion, "informar")
        self.assertEqual(self._escribir().accion, "denegar")

    def test_sin_lecturas_exigidas_el_mecanismo_calla(self) -> None:
        otro = _repositorio(Path(self.temporal.name) / "limpio")
        decision = _decidir(
            otro,
            _evento(otro, hook_event_name="PreToolUse", tool_name="Write", tool_input={"file_path": "x.md"}),
        )
        self.assertEqual(decision.accion, "pasar")


class Redaccion(unittest.TestCase):
    """G05: reescribe lo que el modelo VE de una ejecución que ya ocurrió."""

    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="sesion-redaccion-")
        self.raiz = _repositorio(Path(self.temporal.name))

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def _post(self, salida: str):
        return _decidir(
            self.raiz,
            _evento(
                self.raiz,
                hook_event_name="PostToolUse",
                tool_name="Bash",
                tool_input={"command": "env"},
                tool_response={"output": salida, "exit_code": 0},
            ),
        )

    def test_tapa_el_valor_no_el_nombre_del_campo(self) -> None:
        # Una blocklist por nombre nunca acaba: el mismo secreto viaja como
        # `sshPass`, `SSH_PASSWORD` o `clave_ssh`. Lo que dispara es la forma.
        crudo = "GITHUB_TOKEN=ghp_" + "a" * 36 + "\nresto de la salida\n"
        decision = self._post(crudo)
        self.assertEqual(decision.accion, "reescribir")
        self.assertNotIn("ghp_" + "a" * 36, decision.salida)
        self.assertIn("GITHUB_TOKEN", decision.salida)
        self.assertIn("resto de la salida", decision.salida)

    def test_el_nombre_del_campo_da_igual(self) -> None:
        # El valor se compone en tiempo de ejecución a propósito: escrito entero
        # sería un hallazgo real para `puente.secretos` y bloquearía el commit de
        # su propia prueba. Lo que se ejercita es la forma, y la forma es la misma.
        falso = "AKIA" + "0123456789ABCDEF"
        for nombre in ("sshPass", "SSH_PASSWORD", "clave_de_acceso"):
            redactado, tapados = redactar_texto(f"{nombre}={falso}\n")
            self.assertEqual(tapados, 1, nombre)
            self.assertNotIn(falso, redactado)

    def test_una_salida_limpia_pasa_intacta(self) -> None:
        self.assertEqual(self._post("total 8\ndrwxr-xr-x  ficheros\n").accion, "pasar")

    def test_una_salida_enorme_se_aparta_a_fichero(self) -> None:
        decision = self._post("linea\n" * (sesion.MAX_LINEAS + 10))
        self.assertEqual(decision.accion, "reescribir")
        self.assertIn("apartada", decision.salida)
        self.assertLess(len(decision.salida), 4000)

    def test_la_valvula_deja_ver_la_salida_cruda(self) -> None:
        registrar_salto(ruta_saltos(self.raiz), "G05", "depurando un pipeline", timedelta(days=1))
        self.assertEqual(self._post("TOKEN=ghp_" + "a" * 36).accion, "pasar")

    def test_exit2_no_puede_reescribir_y_por_eso_no_bloquea(self) -> None:
        # Un runtime sin JSON no puede sustituir un texto: o pasa, o corta. Cortar
        # aquí sería impedir un comando que YA corrió, que no arregla nada.
        decision = self._post("TOKEN=ghp_" + "a" * 36)
        self.assertEqual(sesion.como_exit2(decision), ("", 0))


class CierreEnRojo(unittest.TestCase):
    """G02: no se cierra con el árbol en rojo, con contador propio y tope duro."""

    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="sesion-cierre-")
        self.raiz = _repositorio(Path(self.temporal.name), entrada=50)  # presupuesto imposible

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def _cerrar(self):
        return _decidir(self.raiz, _evento(self.raiz, hook_event_name="Stop"))

    def test_bloquea_el_cierre_y_lo_dice_con_numeros(self) -> None:
        decision = self._cerrar()
        self.assertEqual(decision.accion, "bloquear")
        self.assertIn("EXCEDIDO", decision.motivo)
        self.assertEqual(json.loads(sesion.como_json(decision, "Stop"))["decision"], "block")

    def test_insiste_hasta_el_tope_y_luego_deja_cerrar_anotandolo(self) -> None:
        for intento in range(sesion.TOPE_AVISOS):
            self.assertEqual(self._cerrar().accion, "bloquear", f"aviso {intento + 1}")
        ultima = self._cerrar()
        self.assertEqual(ultima.accion, "informar")
        registro = sesion.ruta_cierres(self.raiz)
        self.assertTrue(registro.is_file())
        self.assertEqual(len(registro.read_text(encoding="utf-8").strip().splitlines()), 1)

    def test_un_arbol_en_verde_no_bloquea_nada(self) -> None:
        sano = _en_verde(_repositorio(Path(self.temporal.name) / "sano"))
        self.assertEqual(_decidir(sano, _evento(sano, hook_event_name="Stop")).accion, "informar")

    def test_la_valvula_deja_cerrar(self) -> None:
        registrar_salto(ruta_saltos(self.raiz), "G02", "urgencia de viernes", timedelta(days=1))
        self.assertEqual(self._cerrar().accion, "informar")

    def test_con_un_salto_vivo_ninguna_salida_dice_verde_a_secas(self) -> None:
        sano = _en_verde(_repositorio(Path(self.temporal.name) / "sano2"))
        registrar_salto(ruta_saltos(sano), "G02", "urgencia de viernes", timedelta(days=1))
        decision = _decidir(sano, _evento(sano, hook_event_name="Stop"))
        for linea in decision.motivo.splitlines():
            if "verde" in linea:
                self.assertIn("salto activo", linea)


class Arranque(unittest.TestCase):
    """G01: la primera línea de la sesión dice la entrada real, medida."""

    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="sesion-arranque-")

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def test_dice_el_numero_y_el_presupuesto(self) -> None:
        raiz = _en_verde(_repositorio(Path(self.temporal.name)))
        decision = _decidir(raiz, _evento(raiz, hook_event_name="SessionStart"))
        self.assertEqual(decision.accion, "informar")
        self.assertIn("tokens", decision.motivo)
        self.assertIn("verde", decision.motivo)

    def test_avisa_en_rojo_cuando_la_entrada_se_pasa(self) -> None:
        raiz = _repositorio(Path(self.temporal.name) / "apretado", entrada=50)
        decision = _decidir(raiz, _evento(raiz, hook_event_name="SessionStart"))
        self.assertIn("rojo", decision.motivo)
        self.assertIn("EXCEDIDO", decision.motivo)

    def test_arrancar_nunca_bloquea(self) -> None:
        raiz = _repositorio(Path(self.temporal.name) / "apretado2", entrada=50)
        decision = _decidir(raiz, _evento(raiz, hook_event_name="SessionStart"))
        self.assertFalse(decision.bloquea)


class NoRevienta(unittest.TestCase):
    """Un guard de sesión que peta rompe la herramienta que vigilaba. Ante la duda, calla."""

    def test_sin_arbol_no_dice_nada_y_sale_con_cero(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sesion-vacio-") as tmp:
            evento = {"hook_event_name": "SessionStart", "session_id": "x", "cwd": tmp}
            with self.assertRaises(sesion.ErrorSesion):
                sesion.decidir(evento, config_path=Path(tmp) / "cosmos.toml")

    def test_un_evento_desconocido_pasa(self) -> None:
        decision, _ = sesion.decidir({"hook_event_name": "Inventado"})
        self.assertEqual(decision.accion, "pasar")

    def test_pasar_no_escribe_nada(self) -> None:
        self.assertEqual(sesion.como_json(sesion.PASAR, "PreToolUse"), "")


class DeVerdadPorLaTuberia(unittest.TestCase):
    """Igual que el gate: el hook se prueba ejecutándolo, no leyéndolo.

    Todo lo de arriba llama a funciones. Esto arranca el módulo como lo arranca
    el runtime —proceso aparte, JSON por la entrada estándar— porque un hook que
    se instala y no corre es peor que ninguno: además tranquiliza.
    """

    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="sesion-tuberia-")
        self.raiz = _repositorio(Path(self.temporal.name))

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def _ejecutar(self, evento: dict, *extra: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-m", "puente.sesion", "--config", str(self.raiz / "cosmos.toml"), *extra],
            input=json.dumps(evento),
            capture_output=True,
            text=True,
            cwd=Path(__file__).resolve().parents[2],
            check=False,
        )

    def test_el_deny_sale_por_la_salida_estandar(self) -> None:
        evento = _evento(
            self.raiz,
            hook_event_name="PreToolUse",
            tool_name="Bash",
            tool_input={"command": "echo falso >> arbol/COSMOS.md"},
        )
        proceso = self._ejecutar(evento)
        self.assertEqual(proceso.returncode, 0)
        cuerpo = json.loads(proceso.stdout)
        self.assertEqual(cuerpo["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_el_formato_exit2_corta_con_codigo_2_y_motivo_en_stderr(self) -> None:
        evento = _evento(
            self.raiz,
            hook_event_name="PreToolUse",
            tool_name="Bash",
            tool_input={"command": "echo falso >> arbol/COSMOS.md"},
        )
        proceso = self._ejecutar(evento, "--formato", "exit2")
        self.assertEqual(proceso.returncode, 2)
        self.assertIn("veredicto", proceso.stderr)
        self.assertEqual(proceso.stdout, "")

    def test_una_entrada_que_no_es_json_no_rompe_nada(self) -> None:
        proceso = subprocess.run(
            [sys.executable, "-m", "puente.sesion"],
            input="esto no es json",
            capture_output=True,
            text=True,
            cwd=Path(__file__).resolve().parents[2],
            check=False,
        )
        self.assertEqual((proceso.returncode, proceso.stdout), (0, ""))


class CableadoDeSesion(unittest.TestCase):
    """`enganchar --sesion` es explícito, y `desenganchar` deja el repo igual."""

    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="sesion-cableado-")
        self.raiz = repo_git(Path(self.temporal.name) / "repo")
        self.ajustes = self.raiz / ".claude" / "settings.json"

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def test_sin_fichero_previo_lo_crea_y_lo_borra(self) -> None:
        enganchar_sesion(self.raiz)
        datos = json.loads(self.ajustes.read_text(encoding="utf-8"))
        self.assertEqual(sorted(datos["hooks"]), sorted(evento for evento, _ in EVENTOS_SESION))
        self.assertEqual(desenganchar_sesion(self.raiz)[1], "eliminado")
        self.assertFalse(self.ajustes.exists())

    def test_devuelve_byte_a_byte_lo_que_habia(self) -> None:
        original = '{\n    "permissions": {"allow": ["Bash"]},\n  "hooks": {"Stop": []}\n}\n'
        self.ajustes.parent.mkdir(parents=True, exist_ok=True)
        self.ajustes.write_text(original, encoding="utf-8")
        enganchar_sesion(self.raiz)
        self.assertNotEqual(self.ajustes.read_text(encoding="utf-8"), original)
        self.assertEqual(desenganchar_sesion(self.raiz)[1], "restaurado")
        self.assertEqual(self.ajustes.read_text(encoding="utf-8"), original)

    def test_no_pisa_los_hooks_de_otro(self) -> None:
        ajeno = {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "mi-script.sh"}]}]}}
        self.ajustes.parent.mkdir(parents=True, exist_ok=True)
        self.ajustes.write_text(json.dumps(ajeno), encoding="utf-8")
        enganchar_sesion(self.raiz)
        entradas = json.loads(self.ajustes.read_text(encoding="utf-8"))["hooks"]["Stop"]
        self.assertEqual(len(entradas), 2)
        desenganchar_sesion(self.raiz)
        self.assertEqual(json.loads(self.ajustes.read_text(encoding="utf-8")), ajeno)

    def test_reenganchar_no_duplica(self) -> None:
        enganchar_sesion(self.raiz)
        enganchar_sesion(self.raiz)
        entradas = json.loads(self.ajustes.read_text(encoding="utf-8"))["hooks"]["Stop"]
        self.assertEqual(len(entradas), 1)

    def test_un_json_roto_no_se_toca(self) -> None:
        self.ajustes.parent.mkdir(parents=True, exist_ok=True)
        self.ajustes.write_text("{ esto no es json", encoding="utf-8")
        with self.assertRaises(ErrorEnganche):
            enganchar_sesion(self.raiz)
        self.assertEqual(self.ajustes.read_text(encoding="utf-8"), "{ esto no es json")


if __name__ == "__main__":
    unittest.main()
