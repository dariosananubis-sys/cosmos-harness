"""Ningún guardarraíl de COSMOS puede dejar a nadie atrapado. Y se comprueba abriendo.

`spec/GUARDARRAILES.md` lo dice desde el principio —la válvula es «obligatoria, no
opcional», porque «todo guardarraíl duro sin válvula de escape acaba desactivado a la
fuerza»— pero era una **costumbre**, y las costumbres se rompen sin avisar: E20 estuvo
viva y sin válvula porque la lista de códigos era un `range(20)` escrito a mano, y solo lo
encontró una persona leyendo.

El caso que lo terminó de demostrar no fue de este repositorio. Un hook del arnés de al
lado bloquea `git push --force` sin excepción posible, y su mensaje remite a «pedir
confirmación explícita». Se pidió, se dio, y el hook siguió bloqueando: compara texto y no
sabe leer una conversación. Un guardarraíl al que su dueño no puede decirle «sí, esta vez»
deja de ser un guardarraíl y pasa a ser un muro — y lo que se hace con los muros es
rodearlos, que es exactamente lo que la válvula existe para evitar.

De ahí esta prueba. No se conforma con que el código esté en una lista: **abre la válvula
de cada guard y comprueba que el guard deja de bloquear**. Una salida que nadie ha visto
abrirse es tan decorativa como una invariante que nadie ha visto fallar.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from cosmos.guardarrailes import (
    CODIGOS,
    CODIGOS_SESION,
    ErrorSalto,
    normalizar_codigo,
    registrar_salto,
)
from cosmos.validar import codigos_comprobados

RAIZ = Path(__file__).resolve().parent.parent


from tests._integrado import solo_en_el_origen

solo_en_el_origen()  # cifras y listas del catálogo del origen, no del motor


class TodoLoQueBloqueaAceptaSuSalida(unittest.TestCase):
    def test_cada_invariante_comprobada_tiene_valvula(self) -> None:
        faltan = [c for c in codigos_comprobados() if c not in CODIGOS]
        self.assertEqual(faltan, [], "invariantes vivas sin vía de escape")

    def test_cada_guardarrail_de_sesion_tiene_valvula(self) -> None:
        for codigo in CODIGOS_SESION:
            with self.subTest(codigo):
                self.assertEqual(normalizar_codigo(codigo), codigo)

    def test_los_guards_que_existen_son_los_que_tienen_valvula(self) -> None:
        """Ni uno de menos (quedaría atrapado) ni uno de más (mentiría sobre lo que hay)."""

        from puente.sesion import MANEJADORES

        self.assertTrue(MANEJADORES, "no hay manejadores de sesión que vigilar")
        self.assertEqual(len(CODIGOS_SESION), 5)

    def test_no_se_puede_saltar_todo_de_golpe(self) -> None:
        """La salida es acotada o no es una salida: es apagar el sistema."""

        for intento in ("TODO", "todos", "*", "ALL"):
            with self.subTest(intento):
                with self.assertRaises(ErrorSalto) as caso:
                    normalizar_codigo(intento)
                self.assertIn("no es un salto", str(caso.exception))


def _config_sobre_el_arbol_real(directorio: Path, **cambios: str) -> Path:
    """Un `cosmos.toml` en un directorio de usar y tirar que apunta al árbol real.

    La base de la válvula es el directorio del `cosmos.toml` (`cli._base_repositorio`,
    `sesion.base_de`), así que con el config aquí el registro de saltos cae en
    `<tmp>/.cosmos/saltos.log` y no en el del repositorio. Antes estas pruebas escribían
    un salto REAL de E16 en `~/cosmos/.cosmos/saltos.log` y lo restauraban en un
    `finally` sin cerrojo: dos corridas a la vez se pisaban el restore y dejaban la
    invariante de presupuesto suspendida en el repo de trabajo (auditoría D-02 / F-06).
    """

    texto = (
        (RAIZ / "cosmos.toml").read_text(encoding="utf-8")
        .replace('arbol = "galaxia"', f'arbol = "{RAIZ}/galaxia"')
        .replace('indice = "galaxia/COSMOS.md"', f'indice = "{RAIZ}/galaxia/COSMOS.md"')
        .replace('registro = "registro"', f'registro = "{RAIZ}/registro"')
    )
    for viejo, nuevo in cambios.items():
        texto = texto.replace(viejo, nuevo)
    config = directorio / "cosmos.toml"
    config.write_text(texto, encoding="utf-8")
    return config


class LaSalidaSeAbreDeVerdad(unittest.TestCase):
    """Que el código esté en una lista no prueba que la puerta abra."""

    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.config = _config_sobre_el_arbol_real(self.base)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _evento_denegado(self) -> dict:
        return {
            "hook_event_name": "PreToolUse",
            "cwd": str(self.base),
            "tool_name": "Write",
            "tool_input": {"file_path": str(RAIZ / "galaxia/COSMOS.md"), "content": "x"},
        }

    def _decision(self, evento: dict) -> str:
        salida = subprocess.run([sys.executable, "-m", "puente.sesion", "--config", str(self.config)],
                                input=json.dumps(evento), capture_output=True,
                                text=True, cwd=RAIZ).stdout
        if not salida.strip():
            return "mudo"
        return json.loads(salida)["hookSpecificOutput"]["permissionDecision"]

    def test_g03_deniega_y_su_valvula_lo_deja_pasar(self) -> None:
        from cosmos.guardarrailes import ruta_saltos

        self.assertEqual(self._decision(self._evento_denegado()), "deny")
        registro = ruta_saltos(self.base)
        registrar_salto(registro, "G03", "prueba: se comprueba que la salida abre",
                        timedelta(minutes=1))
        self.assertEqual(self._decision(self._evento_denegado()), "mudo",
                         "la válvula de G03 no abre: el guard sigue denegando")
        registro.unlink()
        self.assertEqual(self._decision(self._evento_denegado()), "deny",
                         "cerrada la válvula, el guard tiene que volver a proteger")
        self.assertFalse(ruta_saltos(RAIZ).is_file() and "prueba:" in ruta_saltos(RAIZ).read_text(encoding="utf-8"),
                         "la prueba escribió su salto en el repositorio real")


class LaSalidaTienePrecio(unittest.TestCase):
    """Una válvula sin coste es un interruptor de apagado, y se usa como tal."""

    def test_exige_motivo(self) -> None:
        with TemporaryDirectory() as tmp:
            with self.assertRaises(ErrorSalto):
                registrar_salto(Path(tmp, "s.jsonl"), "G03", "   ", timedelta(days=1))

    def test_caduca(self) -> None:
        with TemporaryDirectory() as tmp:
            salto = registrar_salto(Path(tmp, "s.jsonl"), "G03", "motivo real",
                                    timedelta(days=1))
            self.assertGreater(salto.caduca, salto.creado)

    def test_queda_escrito(self) -> None:
        with TemporaryDirectory() as tmp:
            log = Path(tmp, "s.jsonl")
            registrar_salto(log, "E16", "el presupuesto se revisa el lunes", timedelta(days=2))
            linea = json.loads(log.read_text(encoding="utf-8").strip())
            self.assertEqual(linea["codigo"], "E16")
            self.assertIn("lunes", linea["motivo"])



class LasDosPuertasDelPresupuestoAbrenIgual(unittest.TestCase):
    """La misma válvula, abierta en un comando y cerrada en el otro.

    Lo midió el agente que cerró la cola de las revisiones: con un salto E16 vivo,
    `cosmos validar` salía 0 diciendo «verde (1 salto activo)» y `cosmos medir` salía 1
    sobre el mismo árbol y el mismo presupuesto. `medir` cobra código de salida —lo usa
    el CI— así que es una puerta, y una puerta sin salida acotada se rodea.

    Es el mismo defecto que E20 y que el hook del `--force`, en su tercera forma: la
    salida existe, pero no en todos los sitios donde la puerta cierra.
    """

    def setUp(self) -> None:
        # Cada prueba estrena su directorio: el config con presupuesto imposible y el
        # registro de saltos viven ahí, nunca en el repositorio. Dos suites a la vez ya
        # no comparten estado, y un SIGKILL a mitad no deja la válvula de E16 abierta.
        self._tmp = TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.config = _config_sobre_el_arbol_real(self.base, **{"entrada = 4000": "entrada = 10"})

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _medir(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-m", "cosmos", "medir", "--config", str(self.config)],
                              capture_output=True, text=True, cwd=RAIZ)

    def test_sin_salto_el_presupuesto_para(self) -> None:
        r = self._medir()
        self.assertEqual(r.returncode, 1)
        self.assertIn("ROJO", r.stdout)

    def test_con_el_salto_abierto_no_para_y_lo_dice(self) -> None:
        from cosmos.guardarrailes import ruta_saltos
        from cosmos.validar import INVARIANTE_PRESUPUESTO

        registrar_salto(ruta_saltos(self.base), INVARIANTE_PRESUPUESTO,
                        "prueba: la puerta del presupuesto tiene que abrir",
                        timedelta(minutes=1))
        r = self._medir()
        self.assertEqual(r.returncode, 0, "la válvula de E16 no abre en `medir`")
        self.assertIn("Salto activo", r.stdout,
                      "abrió en silencio: un salto vivo se dice siempre")

    def test_cerrada_la_valvula_vuelve_a_parar(self) -> None:
        r = self._medir()
        self.assertEqual(r.returncode, 1, "el presupuesto dejó de proteger tras cerrar el salto")


class NingunaPruebaDejaEstadoEnElRepositorio(unittest.TestCase):
    """Canario del fallo D-02/F-06: la suite no puede dejar un salto vivo en el repo real.

    Un salto E16 huérfano en `.cosmos/saltos.log` suspende la invariante de presupuesto
    sobre el árbol de trabajo, y `git status` no lo canta porque está en `.gitignore`.
    """

    def test_el_registro_real_no_tiene_saltos_de_prueba(self) -> None:
        from cosmos.guardarrailes import ruta_saltos

        registro = ruta_saltos(RAIZ)
        if not registro.is_file():
            return
        de_prueba = [linea for linea in registro.read_text(encoding="utf-8").splitlines()
                     if '"motivo": "prueba:' in linea]
        self.assertEqual(de_prueba, [], f"la suite dejó saltos de prueba en {registro}")

    def test_ninguna_prueba_escribe_un_config_en_la_raiz(self) -> None:
        self.assertFalse((RAIZ / ".estrecho-de-prueba.toml").exists(),
                         "volvió el config de prueba escrito en la raíz del repositorio")

if __name__ == "__main__":
    unittest.main()
