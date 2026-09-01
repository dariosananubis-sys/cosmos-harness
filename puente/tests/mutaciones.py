#!/usr/bin/env python3
"""Rompe cada invariante a propósito y comprueba que su prueba se pone roja.

GOAL §7: una pieza no está terminada hasta que se la ha visto fallar. Un verde que
nunca ha dado rojo no distingue una comprobación que funciona de una rota. Cada
mutación cambia una línea del puente, ejecuta la prueba dueña de esa línea y exige
que falle; luego lo deja todo como estaba.

    python3 -m puente.tests.mutaciones
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent


@dataclass(frozen=True)
class Mutacion:
    codigo: str
    fichero: str
    viejo: str
    nuevo: str
    prueba: str
    descripcion: str


MUTACIONES = (
    Mutacion(
        "M1",
        "puente/etiquetas.py",
        "        if not any(tramo in resumen for tramo in prohibidos):\n",
        "        if True:\n",
        "puente.tests.test_etiquetas.EtiquetaOpaca.test_la_etiqueta_no_contiene_ningun_tramo_de_la_ruta",
        "sin el bucle anticolisión, la etiqueta deja ver un tramo de la ruta",
    ),
    Mutacion(
        "M2",
        "puente/secretos.py",
        "    return any(\n        patron.fullmatch(texto) for patron in (_CAMELLO_O_RUTA, _SERPIENTE, _GRITO)\n    )\n",
        "    return False\n",
        "puente.tests.test_secretos.SinRuido",
        "sin el filtro de expresiones, el escáner grita por cada 'obtener_clave_del_entorno'",
    ),
    Mutacion(
        "M3",
        "puente/secretos.py",
        'rb"vault:|\\$\\{)(?P<valor>[A-Za-z0-9_./+\\-=]{20,})"',
        'rb"vault:|\\$\\{)(?P<valor>[A-Za-z0-9_./+\\-=]{200,})"',
        "puente.tests.test_secretos.SecretosPlantados",
        "subiendo el umbral del patrón, un secreto plantado deja de detectarse",
    ),
    Mutacion(
        "M4",
        "puente/proyectar.py",
        '                raise ErrorProyeccion(f"no se sobrescribe lo ajeno: {destino}/skills/{nombre}")',
        "                pass",
        "puente.tests.test_proyectar.Proyeccion.test_no_sobrescribe_una_skill_ajena",
        "sin la guarda, la proyección pisa una skill que no es suya",
    ),
    Mutacion(
        "M5",
        "puente/proyectar.py",
        "    inicios = [c.start() for c in re.finditer(re.escape(INICIO), existente)]\n",
        "    inicios, finales = [], []\n    _ = [c.start() for c in re.finditer(re.escape(INICIO), existente)]\n",
        "puente.tests.test_proyectar.Proyeccion.test_la_segunda_proyeccion_no_cambia_nada",
        "si el bloque se concatena en vez de sustituirse, la segunda proyección crece",
    ),
    Mutacion(
        "M6",
        "puente/lluvia.py",
        'CAMPOS_PUBLICOS = ("ruta", "nombre", "resumen", "carpeta", "nicho")',
        'CAMPOS_PUBLICOS = ("ruta", "nombre", "resumen", "carpeta", "nicho", "cuerpo")',
        "puente.tests.test_lluvia.NuncaElCuerpo",
        "un campo de más en la proyección y la consulta devuelve el cuerpo entero",
    ),
    Mutacion(
        "M7",
        "puente/lluvia.py",
        "        if usado + tamano > maximo:\n            break\n",
        "        if False:\n            break\n",
        "puente.tests.test_lluvia.Presupuesto",
        "sin el corte por bytes, la salida se pasa del presupuesto",
    ),

    Mutacion(
        "M8",
        "puente/gate.py",
        "                orden, cwd=instantanea, env=entorno, capture_output=silencioso, check=False\n",
        "                orden, cwd=base, env=entorno, capture_output=silencioso, check=False\n",
        "puente.tests.test_gate.Instantanea.test_no_verifica_el_arbol_de_trabajo_sucio",
        "verificando en el árbol de trabajo, el gate aprueba lo que no se va a commitear",
    ),
)


def _ejecutar(prueba: str) -> int:
    return subprocess.run(
        [sys.executable, "-m", "unittest", prueba],
        cwd=RAIZ,
        capture_output=True,
        check=False,
    ).returncode


def main() -> int:
    fallos = 0
    for mutacion in MUTACIONES:
        ruta = RAIZ / mutacion.fichero
        original = ruta.read_text(encoding="utf-8")
        if mutacion.viejo not in original:
            print(f"{mutacion.codigo}: NO APLICABLE (el código cambió)")
            fallos += 1
            continue
        ruta.write_text(original.replace(mutacion.viejo, mutacion.nuevo, 1), encoding="utf-8")
        try:
            codigo = _ejecutar(mutacion.prueba)
        finally:
            ruta.write_text(original, encoding="utf-8")
        estado = "ROJO (correcto)" if codigo else "VERDE (la prueba no vigila nada)"
        if not codigo:
            fallos += 1
        print(f"{mutacion.codigo} {mutacion.fichero}: {estado} — {mutacion.descripcion}")
    print(f"\n{len(MUTACIONES) - fallos}/{len(MUTACIONES)} invariantes vistas fallar")
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
