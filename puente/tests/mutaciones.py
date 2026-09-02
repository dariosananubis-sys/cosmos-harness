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
        '        if caracter in ";&|\\n":\n',
        "        if False:\n",
        "puente.tests.test_sesion.RutasDeVeredicto.test_una_escritura_escondida_detras_de_una_orden_inocente_no_pasa",
        "sin segmentar, el bloque entero se juzga por su primer programa y el 'cp' de detras no se mira",
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
    Mutacion(
        "M19",
        "puente/sesion.py",
        'r"^(?P<descriptor>[0-9]*&?)>>?(?P<modo>[|&]?)(?P<destino>.*)$"',
        'r"^(?P<descriptor>[0-9]*)>>?(?P<destino>.*)$"',
        "puente.tests.test_sesion.EvasionesDeShell.test_a_redireccion_con_ampersand",
        "sin los operadores compuestos en la regex, 'echo x &> indice' no declara ningun destino",
    ),
    Mutacion(
        "M20",
        "puente/sesion.py",
        '        if caracter in "<>":\n            actual.append(caracter)\n            while indice < total and texto[indice] in ">&|":\n                actual.append(texto[indice])\n                indice += 1\n            continue\n',
        '        if caracter in "<>":\n            actual.append(caracter)\n            continue\n',
        "puente.tests.test_sesion.EvasionesDeShell.test_c_redireccion_que_ignora_noclobber",
        "partiendo por el '|' de '>|', la redireccion se queda sin destino y la escritura pasa",
    ),
    Mutacion(
        "M21",
        "puente/sesion.py",
        '    texto = comando.replace("\\\\\\n", " ")\n',
        "    texto = comando\n",
        "puente.tests.test_sesion.Segmentacion.test_una_continuacion_de_linea_no_termina_la_orden",
        "sin resolver la continuacion de linea, un salto suelto se cuela como si fuera una ruta",
    ),
    Mutacion(
        "M22",
        "puente/sesion.py",
        '        if pieza.startswith("<"):\n            # Entrada, no salida.',
        '        if indice == 0 or _ASIGNACION.match(pieza):\n            continue\n        if pieza.startswith("<"):\n            # Entrada, no salida.',
        "puente.tests.test_sesion.EvasionesDeShell.test_b_redireccion_delante_del_programa",
        "saltando el indice 0 sin mirar si es una redireccion, '> indice orden' no declara destino",
    ),
    Mutacion(
        "M23",
        "puente/sesion.py",
        "            if _DUPLICA_DESCRIPTOR.match(pieza):\n                continue\n",
        "            if False:\n                continue\n",
        "puente.tests.test_sesion.EvasionesDeShell.test_duplicar_un_descriptor_no_es_escribir_un_fichero",
        "sin distinguir '2>&1', copiar un descriptor cuenta como escribir un fichero llamado '1'",
    ),
    Mutacion(
        "M24",
        "puente/sesion.py",
        '        if pieza.startswith("of="):\n            objetivos.append(pieza[3:])\n            continue\n        if indice == 0 or _ASIGNACION.match(pieza):\n            continue\n',
        '        if indice == 0 or _ASIGNACION.match(pieza):\n            continue\n        if pieza.startswith("of="):\n            objetivos.append(pieza[3:])\n            continue\n',
        "puente.tests.test_sesion.EvasionesDeShell.test_g_dd_escribe_en_of",
        "detras de _ASIGNACION la rama de 'of=' no se alcanza nunca y 'dd' escribe donde quiere",
    ),
    Mutacion(
        "M25",
        "puente/sesion.py",
        "            for objetivo in objetivos_de_escritura(orden):\n",
        '            if "cosmos" in orden.split():\n                continue\n            for objetivo in objetivos_de_escritura(orden):\n',
        "puente.tests.test_sesion.EvasionesDeShell.test_e_la_palabra_cosmos_de_argumento_no_autoriza",
        "volviendo a fiarse del nombre del programa, 'python3 -c cosmos > indice' escribe el veredicto",
    ),
    Mutacion(
        "M26",
        "puente/sesion.py",
        "                if _NO_RESOLUBLE.search(objetivo):\n",
        "                if False:\n",
        "puente.tests.test_sesion.EvasionesDeShell.test_f_un_destino_calculado_se_deniega",
        "sin denegar el destino calculado, '> $(echo indice)' pasa porque nadie sabe adonde escribe",
    ),
    Mutacion(
        "M27",
        "puente/sesion.py",
        '    if herramienta == "Read":\n        _marcar_si_procede(entrada, config, base)\n    if CODIGO_REDACCION in saltados or herramienta not in HERRAMIENTAS_VIGILADAS:\n        return PASAR\n',
        '    if CODIGO_REDACCION in saltados:\n        return PASAR\n    if herramienta == "Read":\n        _marcar_si_procede(entrada, config, base)\n    if herramienta not in HERRAMIENTAS_VIGILADAS:\n        return PASAR\n',
        "puente.tests.test_sesion.MarcaDeLectura.test_saltar_la_redaccion_no_desarma_la_marca_de_lectura",
        "con G04 detras del cortacircuitos de G05, abrir una valvula deja la otra denegando todo",
    ),
    Mutacion(
        "M28",
        "puente/sesion.py",
        '_CANALES = ("output", "stdout", "stderr", "content")\n',
        '_CANALES = ("output", "stdout", "content")\n',
        "puente.tests.test_sesion.Redaccion.test_tapa_el_valor_que_sale_por_stderr",
        "sin leer stderr, el token de un 'git push' entra en el contexto sin pasar por la redaccion",
    ),
    Mutacion(
        "M29",
        "puente/sesion.py",
        'HERRAMIENTAS_VIGILADAS = ("Bash", "Read", "Grep", "Glob", "Task")\n',
        'HERRAMIENTAS_VIGILADAS = ("Bash",)\n',
        "puente.tests.test_sesion.Redaccion.test_tapa_lo_que_devuelve_una_lectura",
        "mirando solo el shell, un .env leido o el informe de un subagente pasan en claro",
    ),
    Mutacion(
        "M30",
        "puente/sesion.py",
        "        for posicion, canal in enumerate(decision.canales):\n            actualizado[canal] = salida if posicion == 0 else \"\"\n",
        "        pass\n",
        "puente.tests.test_sesion.Redaccion.test_el_texto_redactado_vuelve_por_los_dos_canales",
        "sustituyendo solo 'output', el valor crudo sigue entrando por el canal que lo trajo",
    ),
    # --- Núcleo: hasta el 2026-09-02 `mutaciones.py` no tocaba ni `cosmos/medir.py`
    # ni `cosmos/validar.py`, y cinco sabotajes del medidor y del validador no
    # ponían roja ni una de las 175 pruebas (F07).
    Mutacion(
        "M31",
        "cosmos/medir.py",
        "    return [\n        ParteMedida(f\"{nodo.cosmos}/{nodo.nombre}\", contador(cuerpo(nodo)))\n        for nodo in agua_condicional(arbol)\n    ]\n",
        "    partes = [\n        ParteMedida(f\"{nodo.cosmos}/{nodo.nombre}\", contador(cuerpo(nodo)))\n        for nodo in agua_condicional(arbol)\n    ]\n    return [max(partes, key=lambda parte: parte.tokens)] if partes else []\n",
        "tests.test_medidor.PruebasMedidor.test_dos_aguas_que_mojan_el_mismo_fichero_se_cobran_las_dos",
        "publicando solo el agua mas cara, dos mares que mojan el mismo fichero cuestan la mitad",
    ),
    Mutacion(
        "M32",
        "cosmos/medir.py",
        "FACTOR_CALIBRACION = 1.204",
        "FACTOR_CALIBRACION = 1.0",
        "tests.test_medidor.PruebasMedidor.test_los_factores_publicados_son_los_que_documenta_la_calibracion",
        "sin el factor se revierte la calibracion entera: un 20% de todas las cifras publicadas",
    ),
    Mutacion(
        "M33",
        "cosmos/medir.py",
        "MARGEN_ERROR: float | None = 0.052",
        "MARGEN_ERROR: float | None = None",
        "tests.test_medidor.PruebasMedidor.test_los_factores_publicados_son_los_que_documenta_la_calibracion",
        "con el margen a None vuelve el '+-desconocido' que la documentacion da por cerrado",
    ),
    Mutacion(
        "M34",
        "cosmos/medir.py",
        '        and isinstance(nodo.datos.get("moja"), list)\n        and nodo.datos["moja"]\n',
        '        and isinstance(nodo.datos.get("moja"), list)\n',
        "tests.test_medidor.PruebasMedidor.test_el_agua_condicional_no_entra_en_la_entrada_pero_si_en_el_presupuesto",
        "sin exigir alcance, el rio y la lluvia se cobran en el presupuesto sin llegar a cargarse nunca",
    ),
    Mutacion(
        "M35",
        "cosmos/validar.py",
        "    expresiones = [_glob_a_regex(patron) for patron in patrones]\n",
        "    return False\n    expresiones = [_glob_a_regex(patron) for patron in patrones]\n",
        "tests.test_validador.PruebasInvariantes.test_e11_cobertura_total_con_todos_los_globs_anclados",
        "con la cobertura a False, E11 se queda ciega ante los globs anclados que juntos lo mojan todo",
    ),
    Mutacion(
        "M36",
        "cosmos/cli.py",
        '            propias = frozenset({"E15", "E19"}) | saltados\n',
        '            propias = frozenset({"E15"}) | saltados\n',
        "tests.test_compilar.PruebasCompilacion.test_generar_repara_e15_y_no_lo_bloquea_una_e19_que_no_puede_reparar",
        "si generar vuelve a exigir E19, un arbol nuevo se queda sin camino a verde (interbloqueo F11)",
    ),
    Mutacion(
        "M37",
        "cosmos/cli.py",
        "    if not config.indice.exists():\n",
        "    if True:\n",
        "tests.test_compilar.PruebasCompilacion.test_arrancar_no_repara_un_indice_que_existe_y_miente",
        "si arrancar reescribe siempre el indice, tapa el E15 que existe para cazar un indice que miente",
    ),
    Mutacion(
        "M38",
        "cosmos/guardarrailes.py",
        'HERRAMIENTAS_POSTERIORES = ("Bash", "Read", "Grep", "Glob", "Task")',
        'HERRAMIENTAS_POSTERIORES = ("Bash", "Read")',
        "tests.test_guardarrailes.EnrutadoDeSesion.test_el_enrutado_cubre_exactamente_lo_que_el_guard_vigila",
        "sin enrutar Grep, Glob y Task, G05 no ve la salida de tres herramientas que ya sabe tapar",
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
