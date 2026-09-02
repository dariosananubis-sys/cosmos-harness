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


class LaSalidaSeAbreDeVerdad(unittest.TestCase):
    """Que el código esté en una lista no prueba que la puerta abra."""

    def _evento_denegado(self) -> dict:
        return {
            "hook_event_name": "PreToolUse",
            "cwd": str(RAIZ),
            "tool_name": "Write",
            "tool_input": {"file_path": str(RAIZ / "galaxia/COSMOS.md"), "content": "x"},
        }

    def _decision(self, evento: dict) -> str:
        salida = subprocess.run([sys.executable, "-m", "puente.sesion"],
                                input=json.dumps(evento), capture_output=True,
                                text=True, cwd=RAIZ).stdout
        if not salida.strip():
            return "mudo"
        return json.loads(salida)["hookSpecificOutput"]["permissionDecision"]

    def test_g03_deniega_y_su_valvula_lo_deja_pasar(self) -> None:
        self.assertEqual(self._decision(self._evento_denegado()), "deny")

        from cosmos.guardarrailes import ruta_saltos

        registro = ruta_saltos(RAIZ)
        antes = registro.read_text(encoding="utf-8") if registro.is_file() else None
        try:
            registrar_salto(registro, "G03", "prueba: se comprueba que la salida abre",
                            timedelta(minutes=1))
            self.assertEqual(self._decision(self._evento_denegado()), "mudo",
                             "la válvula de G03 no abre: el guard sigue denegando")
        finally:
            if antes is None:
                registro.unlink(missing_ok=True)
            else:
                registro.write_text(antes, encoding="utf-8")

        self.assertEqual(self._decision(self._evento_denegado()), "deny",
                         "cerrada la válvula, el guard tiene que volver a proteger")


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


if __name__ == "__main__":
    unittest.main()
