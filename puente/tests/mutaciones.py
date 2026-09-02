#!/usr/bin/env python3
"""Rompe cada invariante a propósito y comprueba que su prueba se pone roja.

GOAL §7: una pieza no está terminada hasta que se la ha visto fallar. Un verde que
nunca ha dado rojo no distingue una comprobación que funciona de una rota. Cada
mutación cambia una línea del puente, ejecuta la prueba dueña de esa línea y exige
que falle; luego lo deja todo como estaba.

    python3 -m puente.tests.mutaciones
"""

from __future__ import annotations

import shutil
import tempfile
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
    Mutacion(
        "M9",
        "puente/sesion.py",
        '        if caracter in ";&|\\n":\n            piezas.append("".join(actual))\n            actual = []\n            continue\n',
        '        if False:\n            piezas.append("".join(actual))\n            actual = []\n            continue\n',
        "puente.tests.test_sesion.RutasDeVeredicto.test_el_permiso_de_una_orden_no_cubre_a_la_siguiente",
        "sin segmentar, el permiso de 'cosmos generar' cubre la escritura a mano que va detras",
    ),
    Mutacion(
        "M10",
        "puente/sesion.py",
        "                if _dentro(objetivo, protegida):\n",
        "                if False:\n",
        "puente.tests.test_sesion.RutasDeVeredicto.test_deniega_escribir_el_indice_a_mano_por_bash",
        "sin la comprobacion de contencion, el indice se reescribe a mano y nadie lo impide",
    ),
    Mutacion(
        "M11",
        "puente/sesion.py",
        "    return frozenset(salto.codigo for salto in activos), activos, caducados\n",
        "    return frozenset(), activos, caducados\n",
        "puente.tests.test_sesion.RutasDeVeredicto.test_la_valvula_desarma_el_guard",
        "ignorando los saltos, un guard de sesion no se puede abrir y acaba arrancado de raiz",
    ),
    Mutacion(
        "M12",
        "puente/secretos.py",
        "    if _permitida(etiqueta, coincidencia):\n        return coincidencia.group(0)\n",
        "    if True:\n        return coincidencia.group(0)\n",
        "puente.tests.test_sesion.Redaccion.test_tapa_el_valor_no_el_nombre_del_campo",
        "sin sustituir el valor, el secreto entra entero en el contexto del modelo",
    ),
    Mutacion(
        "M13",
        "puente/sesion.py",
        '            and datos.get("sha256") == sha256_de(ruta)\n',
        "            and True\n",
        "puente.tests.test_sesion.MarcaDeLectura.test_editar_el_fichero_invalida_la_marca",
        "sin el hash, la marca certifica una version del documento que ya no existe",
    ),
    Mutacion(
        "M14",
        "puente/sesion.py",
        '            datos.get("session_id") == (session_id or "")\n',
        "            True\n",
        "puente.tests.test_sesion.MarcaDeLectura.test_una_marca_copiada_a_mano_no_vale",
        "sin la sesion dentro de la marca, copiarla a otra carpeta la convierte en lectura ajena",
    ),
    Mutacion(
        "M15",
        "puente/sesion.py",
        '    for marca in directorio_sesion(base, session_id).glob("lectura-*.json"):\n',
        "    for marca in ():\n",
        "puente.tests.test_sesion.MarcaDeLectura.test_precompact_borra_la_marca_sin_condiciones",
        "sin el borrado al compactar, la prueba de lectura sobrevive al contenido que probaba",
    ),
    Mutacion(
        "M16",
        "puente/sesion.py",
        "TOPE_AVISOS = 3\n",
        "TOPE_AVISOS = 0\n",
        "puente.tests.test_sesion.CierreEnRojo.test_bloquea_el_cierre_y_lo_dice_con_numeros",
        "con el tope a cero el cierre en rojo no se bloquea nunca: avisar y callarse no verifica nada",
    ),
    Mutacion(
        "M17",
        "puente/sesion.py",
        "    if avisos <= TOPE_AVISOS:\n",
        "    if True:\n",
        "puente.tests.test_sesion.CierreEnRojo.test_insiste_hasta_el_tope_y_luego_deja_cerrar_anotandolo",
        "sin tope duro el Stop es un bucle sin salida, y un bucle sin salida se desinstala",
    ),
    Mutacion(
        "M18",
        "cosmos/guardarrailes.py",
        '        if intacto and guardado["existia"] and isinstance(original, str):\n',
        "        if False:\n",
        "puente.tests.test_sesion.CableadoDeSesion.test_devuelve_byte_a_byte_lo_que_habia",
        "sin restaurar los bytes originales, desenganchar reformatea los ajustes de otro",
    ),
)


def _ejecutar(prueba: str, raiz: Path) -> int:
    return subprocess.run(
        [sys.executable, "-m", "unittest", prueba],
        cwd=raiz,
        capture_output=True,
        check=False,
    ).returncode


def main() -> int:
    """Muta sobre una instantánea, nunca sobre el árbol de trabajo.

    Antes escribía en los ficheros versionados y los restauraba en un `finally`.
    Funciona hasta que no funciona: un SIGKILL o un corte de luz entre la escritura
    y la restauración deja un fichero del repo corrompido. La instantánea hace que
    ese fallo sea imposible en vez de improbable — el mismo criterio que usa
    `gate.py` al verificar sobre el índice y no sobre el árbol sucio.
    """

    fallos = 0
    with tempfile.TemporaryDirectory(prefix="cosmos-mut-") as tmp:
        copia = Path(tmp) / "repo"
        shutil.copytree(
            RAIZ, copia,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".cosmos", "research"),
        )
        for mutacion in MUTACIONES:
            ruta = copia / mutacion.fichero
            original = ruta.read_text(encoding="utf-8")
            if mutacion.viejo not in original:
                print(f"{mutacion.codigo}: NO APLICABLE (el código cambió)")
                fallos += 1
                continue
            ruta.write_text(original.replace(mutacion.viejo, mutacion.nuevo, 1), encoding="utf-8")
            try:
                codigo = _ejecutar(mutacion.prueba, copia)
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
