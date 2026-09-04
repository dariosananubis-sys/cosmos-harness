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
    # --- Cierre de la cola de la revisión profunda (2026-09-02): B03, B08-B11,
    # T03/T04, A01/A02. Cada arreglo entra con su sabotaje visto fallar.
    Mutacion(
        "M39",
        "cosmos/modelo.py",
        "            if pid is not None and _proceso_vivo(pid):\n",
        "            if pid is not None and pid != os.getpid() and _proceso_vivo(pid):\n",
        "tests.test_escritura_segura.UnCerrojoDelQueSePuedeSalir.test_la_reentrada_se_rechaza_y_el_exterior_conserva_la_exclusion",
        "con el pid propio excluido, la reentrada roba el cerrojo y la exclusion se evapora en silencio (B08)",
    ),
    Mutacion(
        "M40",
        "cosmos/modelo.py",
        '            os.write(descriptor, f"{os.getpid()}\\n".encode("utf-8"))\n            os.close(descriptor)\n',
        "            os.close(descriptor)\n",
        "tests.test_escritura_segura.UnCerrojoDelQueSePuedeSalir.test_el_pid_esta_dentro_antes_de_ceder_el_control",
        "sin el PID escrito antes de ceder, el cerrojo esta vacio y otro proceso lo clasifica como rancio y lo roba",
    ),
    Mutacion(
        "M41",
        "cosmos/compilar.py",
        "            if _hash_actual(entrada, modo) == hash_esperado:\n",
        "            if False:\n",
        "tests.test_compilar.PruebasCompilacion.test_la_vista_huerfana_identica_se_adopta_y_e19_sana",
        "sin adopcion, borrar .cosmos/ deja la vista huerfana para siempre y la receta de E19 no cura (B03)",
    ),
    Mutacion(
        "M42",
        "cosmos/modelo.py",
        "        os.chmod(temporal_path, permisos)\n",
        "        pass  # os.chmod(temporal_path, permisos)\n",
        "tests.test_compilar.PruebasCompilacion.test_el_manifiesto_conserva_sus_permisos_al_reescribirse",
        "sin conservar el modo, cada reescritura estrecha los permisos a 0600 — y al haber UN escritor, el canario del manifiesto lo ve (A01/B04)",
    ),
    Mutacion(
        "M43",
        "cosmos/acertar.py",
        "    except FileNotFoundError:\n",
        "    except ():\n",
        "tests.test_acertar_motor.LosEncargosSeValidanEnElBorde.test_el_estreno_no_es_un_traceback",
        "sin validar el borde, el caso de estreno (repo sin encargos) revienta con FileNotFoundError crudo (B09)",
    ),
    Mutacion(
        "M44",
        "cosmos/medir.py",
        "        cabe=None if peor.universo == 0 else con_margen <= presupuesto,\n",
        "        cabe=con_margen <= presupuesto,\n",
        "tests.test_un_solo_veredicto.ElVeredictoEsTrivalente.test_sobre_un_arbol_vacio_cabe_es_none_y_la_linea_no_dice_ok",
        "sin el veredicto trivalente, un arbol sin un token vuelve a dar «OK, quedan 4.000» (B10)",
    ),
    Mutacion(
        "M45",
        "cosmos/medir.py",
        "    peor = casos.peor\n    margen_error = float(peor.margen_error or 0.0) if peor.estimado else 0.0\n",
        "    peor = casos.evaluada\n    margen_error = float(peor.margen_error or 0.0) if peor.estimado else 0.0\n",
        "tests.test_un_solo_veredicto.ElJuezCobraSobreElPeorAunqueHayaSeleccion.test_cabe_es_falso_con_la_seleccion_barata_activa",
        "el juez cobra sobre la seleccion: elegir un nicho barato pone verde un arbol cuyo peor caso no cabe (T03, el sabotaje M02 del tercer revisor)",
    ),
    Mutacion(
        "M46",
        "cosmos/medir.py",
        "    veredicto = veredicto_de_presupuesto(resultado, evaluada.presupuesto)\n    evaluado = veredicto.evaluado\n    estado = veredicto.como_linea()\n",
        '    evaluado = evaluada.entrada_con_agua\n    estado = (f"OK, quedan {evaluada.presupuesto - evaluado} tokens" if evaluado <= evaluada.presupuesto\n              else f"ROJO, excede en {evaluado - evaluada.presupuesto} tokens")\n',
        "tests.test_un_solo_veredicto.ElJuezCobraSobreElPeorAunqueHayaSeleccion.test_la_linea_que_lee_una_persona_dice_lo_mismo_que_el_codigo_de_salida",
        "un cuarto juez en el formateador: la linea que lee una persona dice OK mientras el proceso sale 1 (B02)",
    ),
    Mutacion(
        "M47",
        "puente/sesion.py",
        '        actualizado: dict[str, object] = {}\n        if decision.codigo_salida is not None:\n            actualizado["exit_code"] = decision.codigo_salida\n',
        '        actualizado: dict[str, object] = {"output": salida, "exit_code": decision.codigo_salida or 0}\n',
        "puente.tests.test_sesion.Redaccion.test_la_reescritura_no_inventa_exit_code_ni_output",
        "la reescritura vuelve a fabricar output y exit_code 0: el modelo lee como salida estandar y exito lo que fue error (B11)",
    ),
    Mutacion(
        "M48",
        "puente/sesion.py",
        "    codigo: int | None = None\n",
        "    codigo: int | None = 0\n",
        "puente.tests.test_sesion.Redaccion.test_la_reescritura_no_inventa_exit_code_ni_output",
        "el 0 por defecto vuelve: un exit_code que nadie dijo entra al contexto como hecho (B11)",
    ),
    Mutacion(
        "M49",
        "cosmos/acertar.py",
        "    for palabra in normalizar(texto):\n        raices.append(_raiz(palabra))\n",
        '    import re as _re\n    for palabra in _re.findall(r"[a-z0-9]{2,}", texto.lower()):\n        raices.append(_raiz(palabra))\n',
        "tests.test_acertar_motor.UnSoloNormalizador.test_acertar_tokeniza_como_la_busqueda_de_memoria",
        "una copia local que diverge (sin quitar acentos) rompe la promesa de «la misma normalizacion que la memoria» (A02)",
    ),
    Mutacion(
        "M50",
        "cosmos/cli.py",
        "        if not config.arbol.is_dir():\n",
        "        if False:\n",
        "tests.test_un_solo_veredicto.ElVeredictoEsTrivalente.test_medir_sale_1_cuando_la_raiz_del_arbol_no_existe",
        "sin comprobar la raiz, medir calla el motivo: sale rojo por el veredicto trivalente pero sin decir que el arbol no esta (B10)",
    ),
    # --- Taxonomia C01/C03 (2026-09-02): las decisiones de contenido tambien tienen canario.
    Mutacion(
        "M51",
        "galaxia/sistemas/ciberseguridad.md",
        "  - blockchain\n",
        "",
        "tests.test_universo_navegable.ElGrafoUsaLlegaATodosSalvoLosTerminales.test_ningun_oficio_sin_citar_salvo_los_declarados",
        "quitando una arista, un oficio vuelve a quedarse sin que nadie lo cite y el mapa deja de llegar a el (C01)",
    ),
    Mutacion(
        "M52",
        "spec/UNIVERSO.md",
        "# El universo — 25 oficios",
        "# El universo — 24 oficios",
        "tests.test_universo_navegable.ElCardinalDelTituloEsElDelDisco.test_universo_anuncia_los_oficios_que_hay",
        "el cardinal del titulo vuelve a escribirse a mano y a envejecer sin que nada lo diga",
    ),
    Mutacion(
        "M53",
        "galaxia/pueblos/mutmut/SKILL.md",
        "padre: refactorizacion/mutacion",
        "padre: rendimiento",
        "tests.test_universo_navegable.LaParticionDeRendimientoNoSeRefunde.test_los_dos_oficios_existen_y_cada_mitad_esta_en_el_suyo",
        "recolgar una herramienta de calidad en rendimiento deshace en silencio la particion decidida (C03)",
    ),
    # --- Agua condensada (2026-09-02): la condensacion fue reescritura, no recorte,
    # y borrar una norma en una futura "limpieza" tiene que doler en rojo.
    Mutacion(
        "M54",
        "galaxia/agua/mar-criterio.md",
        "Mover o partir codigo no es reescribirlo de memoria: se traslada con la herramienta que conserva\nel historial y se cuadra el conteo.\n",
        "",
        "tests.test_agua_normativa.NingunaNormaSePierdeAlCondensar.test_cada_afirmacion_sigue_presente",
        "borrar la norma de mover-sin-reescribir pasa desapercibido sin la lista a mano de afirmaciones",
    ),
    Mutacion(
        "M55",
        "galaxia/agua/mar-pruebas.md",
        "Se mide primero y se escribe la asercion despues: el test afirma lo medido, no lo deseado.\n",
        "",
        "tests.test_agua_normativa.NingunaNormaSePierdeAlCondensar.test_cada_afirmacion_sigue_presente",
        "la primera norma del mar de pruebas —la doctrina entera del repo— se puede borrar sin que E07-E20 digan nada",
    ),
    # --- El verbo buscar y el catalogo en arbol (2026-09-02).
    Mutacion(
        "M56",
        "cosmos/buscar.py",
        "    for ruta in _ordenar(consulta, candidatos)[: max(limite, 0)]:\n",
        "    for ruta in _ordenar(consulta, candidatos)[::-1][: max(limite, 0)]:\n",
        "tests.test_buscar.ElVerboEncuentra.test_codigo_duplicado_lleva_a_las_reglas_de_refactorizacion",
        "con el ranking invertido, buscar devuelve lo peor puntuado como primer resultado",
    ),
    Mutacion(
        "M57",
        "cosmos/medir.py",
        '        if profundidad <= 1:\n',
        '        if True:\n',
        "tests.test_medidor.PruebasMedidor.test_catalogo_web_contiene_solo_pueblos_de_web",
        "si el catalogo vuelve a pagar la ruta completa por linea, el 40% del peor nicho vuelve en silencio",
    ),
    Mutacion(
        "M58",
        "cosmos/acertar.py",
        "        if validacion is not None:\n            # El detalle por encargo es EXACTAMENTE lo que quema un holdout: verlo una vez\n",
        "        if False:\n            # El detalle por encargo es EXACTAMENTE lo que quema un holdout: verlo una vez\n",
        "tests.test_sello_holdout.ElDetallePorEncargoNoSeEnsenaSellado.test_como_dict_redacta_solo_la_validacion",
        "sin la redaccion, --json vuelve a ensenar el detalle por encargo: el gesto exacto que quemo el holdout anterior",
    ),
    Mutacion(
        "M59",
        "cosmos/juez.py",
        "    return max(presentes, key=len) if presentes else None\n",
        "    return presentes[0] if presentes else None\n",
        "tests.test_juez_local.LaRutaSeExtraeDelRuido.test_si_nombra_varias_gana_la_mas_larga",
        "con el primer candidato en vez del mas largo, contestar la hoja se puntua como la raiz que la contiene",
    ),
    # --- El juez honesto (auditoria 360, informe B, 2026-09-03). Cada puerta se ve cerrada.
    Mutacion(
        "M60",
        "cosmos/acertar.py",
        '    return elegida == esperada or elegida.startswith(esperada + "/")\n',
        '    return elegida == esperada or elegida.startswith(esperada + "/") or esperada.startswith(elegida + "/")\n',
        "tests.test_juez_honesto.LaReglaDeCorreccionEstaFijada",
        "B-04: aceptar el ancestro como acierto subia la validacion 5 puntos con 259 tests en verde",
    ),
    Mutacion(
        "M61",
        "cosmos/acertar.py",
        '    return elegida == esperada or elegida.startswith(esperada + "/")\n',
        '    return elegida == esperada or elegida.startswith(esperada)\n',
        "tests.test_juez_honesto.LaReglaDeCorreccionEstaFijada",
        "B-04, la otra direccion: un prefijo de texto («webs» por «web») pasaba por acierto",
    ),
    Mutacion(
        "M62",
        "cosmos/acertar.py",
        "        if brecha is not None and brecha <= BRECHA_ALARMA:\n",
        "        if False:\n",
        "tests.test_juez_honesto.LaGuardaAntiGoodhartMiraAlLadoCorrecto",
        "B-03: sin la alarma, el arbol inflado (ajuste 64, validacion 100) vuelve a publicar «la cifra que vale es 100 %»",
    ),
    Mutacion(
        "M63",
        "cosmos/cli.py",
        "        procedencia=comprobar_procedencia(raiz, [e.peticion for e in encargos]),\n",
        "        procedencia=None,\n",
        "tests.test_juez_honesto.ElExamenNoViajaConElRepositorio.test_por_cli_un_holdout_con_una_consulta_de_la_historia_no_publica_cifra",
        "B-02: sin mirar la historia git, un examen que ya estuvo en el repositorio se da por ciego",
    ),
    Mutacion(
        "M64",
        "cosmos/cli.py",
        "    versionado: bool | None = esta_versionado(raiz, validacion) if esta_dentro(raiz, validacion) else False\n",
        "    versionado: bool | None = False\n",
        "tests.test_juez_honesto.ElExamenNoViajaConElRepositorio.test_por_cli_un_holdout_versionado_se_declara_quemado",
        "B-02: un holdout versionado en el propio repositorio se aceptaba como examen",
    ),
    Mutacion(
        "M65",
        "cosmos/cli.py",
        "        sello_roto=datos_sello is not None and not vigente,\n",
        "        sello_roto=False,\n",
        "tests.test_sello_holdout.ElCliRespetaElSello.test_un_sello_desfasado_avisa_y_quita_la_cifra",
        "B-07: con el sello roto sin detectar, la salida ya no dice que el conjunto cambio despues de sellarse",
    ),
    Mutacion(
        "M66",
        "cosmos/acertar.py",
        "    lineas.extend(lineas_de_catalogo(arbol, todos))\n",
        '    lineas.extend((r, f"{r} {t}") for r, t in lineas_de_catalogo(arbol, todos))\n',
        "tests.test_juez_honesto.ElJuezPuntuaLoQueElAgenteVe",
        "B-08: volver a puntuar la ruta completa —que el agente no ve en esa linea— vale 10 puntos a favor de la cifra",
    ),
    Mutacion(
        "M67",
        "cosmos/acertar.py",
        '            "atribuible": False,\n',
        '            "atribuible": True,\n',
        "tests.test_acertar_contraste.ElContrasteEnJson.test_publica_la_brecha_y_la_cifra_no_atribuible",
        "R-01: declarar atribuible una cifra cuyo examen escribe quien lee el arbol es el amaño que el revisor construyo",
    ),
    Mutacion(
        "M68",
        "puente/gate.py",
        "        if terminos_antes and len(perdidos) / len(terminos_antes) > umbral:\n",
        "        if False:\n",
        "puente.tests.test_gate.ElCanarioDeVaciadoDeResumen.test_un_resumen_vaciado_se_denuncia",
        "B-01: sin el canario, vaciar los resumenes para copiar el examen pasa el gate en verde",
    ),
    Mutacion(
        "M69",
        "puente/gate.py",
        "    if comprobar_vaciado(base):\n        return 1\n",
        "    if False:\n        return 1\n",
        "puente.tests.test_gate.ElCanarioDeVaciadoDeResumen.test_el_gate_entero_lo_bloquea",
        "B-01: el canario existe pero el gate no lo llama",
    ),
    Mutacion(
        "M70",
        "puente/proyectar.py",
        "        if ruta.parent == origen and ruta.name == \"SKILL.md\":\n            contenido = para_el_anfitrion(contenido)\n",
        "        if False:\n            contenido = para_el_anfitrion(contenido)\n",
        "puente.tests.test_proyectar.LoProyectadoLoVeElAnfitrion.test_el_skill_proyectado_lleva_name_y_description",
        "E-02: sin traducir el frontmatter, los pueblos proyectados son invisibles para Claude Code",
    ),
    Mutacion(
        "M71",
        "puente/proyectar.py",
        "        for nombre in invisibles_para_el_anfitrion(base, sorted(fuentes)):\n",
        "        for nombre in ():\n",
        "puente.tests.test_proyectar.LoProyectadoLoVeElAnfitrion.test_comprobar_verifica_el_contrato_del_anfitrion_no_el_de_cosmos",
        "E-02: comprobar vuelve a verificar el contrato de COSMOS consigo mismo y da verde sobre skills que el anfitrion no ve",
    ),
    Mutacion(
        "M72",
        "cosmos/validar.py",
        '        if origen != "propio" and url_de_repositorio(texto) is None:\n',
        "        if False:\n",
        "tests.test_arreglos_p3.A06_E21_UnPuebloNombraQueEjecutar.test_sin_url_ni_origen_es_rojo",
        "A-06: sin E21, un pueblo que no nombra ningun repositorio vuelve a pasar por herramienta",
    ),
    Mutacion(
        "M73",
        "puente/gate.py",
        "        if not antes or despues is None:\n            continue\n",
        "        if True:\n            continue\n",
        "puente.tests.test_gate.ElCanarioDeVaciadoDeResumen.test_un_resumen_vaciado_se_denuncia",
        "B-01: el canario que salta todos los ficheros no vigila nada",
    ),
    Mutacion(
        "M74",
        "puente/gate.py",
        "    if comprobar_bajas(base):\n        return 1\n",
        "    if False:\n        return 1\n",
        "puente.tests.test_gate.ElGateVigilaLasBajasYLaCopiaDelExamen.test_el_gate_entero_bloquea_una_baja",
        "R-02: sin P02 en el gate, borrar herramientas sube la nota y ensancha el presupuesto en verde",
    ),
    Mutacion(
        "M75",
        "puente/gate.py",
        "        if del_examen:\n",
        "        if False:\n",
        "puente.tests.test_gate.ElGateVigilaLasBajasYLaCopiaDelExamen.test_ganar_terminos_del_examen_que_espera_al_nodo_se_denuncia",
        "R-14: sin la guarda de ganancia, copiar el examen al resumen del nodo esperado pasa el gate",
    ),
    Mutacion(
        "M76",
        "cosmos/holdout.py",
        "    if es_superficial(raiz_repo):\n",
        "    if False:\n",
        "tests.test_juez_honesto.LaProcedenciaEsTrivalenteDeVerdad.test_clon_superficial_dice_no_lo_se",
        "R-17: en un clon superficial la comprobacion de examen quemado decia «limpia» sin haber visto la historia",
    ),
    Mutacion(
        "M77",
        "cosmos/acertar.py",
        "        if self.calcado is not None and self.calcado >= SOLAPE_CALCADO:\n",
        "        if False:\n",
        "tests.test_juez_honesto.NingunaCifraEsAtribuibleMientrasElExamenLoEscribaElExaminando.test_el_examen_calcado_de_las_lineas_no_es_integro",
        "R-01: sin la señal de calcado, un examen copiado del catalogo pasa por integro",
    ),
    Mutacion(
        "M78",
        "cosmos/acertar.py",
        "    idf = (idf + 1) ** 0.5\n",
        "    idf = __import__(\"math\").log(idf + 1)\n",
        "tests.test_juez_honesto.ElModeloDePuntuacionEstaFijado",
        "R-09: la IDF logaritmica «para que coincida con el docstring» subia 10 puntos con la suite en verde",
    ),
    Mutacion(
        "M79",
        "cosmos/validar.py",
        "    if id(segundo) not in afirmaciones:\n        afirmaciones[id(segundo)] = _afirmaciones(segundo)\n",
        "    afirmaciones[id(segundo)] = _afirmaciones(segundo)\n",
        "tests.test_escala.LosArreglosDeRendimientoSeCuentanNoSeCreen.test_d06_e17_parsea_cada_co_cargable_una_sola_vez",
        "R-47 / D-06: una cache que no cachea, firmada por 320 pruebas; ahora se cuentan las llamadas",
    ),
    Mutacion(
        "M80",
        "cosmos/configurar.py",
        "        if actual == valor:\n            _quitar(copia, clave)\n",
        "        if True:\n            _quitar(copia, clave)\n",
        "tests.test_autonomia.LosAjustesDeUsuarioSeEscribenSinPisar.test_no_pisa_un_valor_cambiado_a_mano",
        "A §2.5: sin comparar el valor, --autonomia manual borra una clave que alguien cambió a mano",
    ),
    Mutacion(
        "M81",
        "puente/modelos.py",
        "    faltan = [e for e in entradas_deseadas() if e[\"value\"] not in presentes]\n    if not faltan:\n        return [], None\n",
        "    faltan = list(entradas_deseadas())\n",
        "tests.test_modelos.Reponer.test_es_idempotente_y_respeta_lo_del_servidor",
        "A §3.7: sin mirar lo presente, cada pasada del reponedor duplica las entradas del menú",
    ),
    Mutacion(
        "M82",
        "puente/modelos.py",
        "        os.chmod(tmp, 0o600)\n        os.replace(tmp, ruta)\n",
        "        os.chmod(tmp, 0o600)\n        ruta.write_text(texto, encoding=\"utf-8\"); Path(tmp).unlink()\n",
        "tests.test_modelos.Reponer.test_escritura_atomica_no_deja_a_medias",
        "A §3.7 / NUCLEO §7: escribir en el sitio deja el fichero del CLI a medias si algo falla",
    ),
    Mutacion(
        "M83",
        "cosmos/validar.py",
        "        elif not nodo.resumen.isascii():\n",
        "        elif False:\n",
        "tests.test_validador.PruebasInvariantes.test_e07_resumen_con_acentos",
        "B-29: sin la comprobación ASCII, un resumen con acentos se paga de más en cada sesión sin que nadie lo vea",
    ),
    Mutacion(
        "M84",
        "cosmos/validar.py",
        "                errores.append(_error(\"E20\", nodo, f\"vecino inexistente en 'usa': {destino}\",\n",
        "                _ = (_error(\"E20\", nodo, f\"vecino inexistente en 'usa': {destino}\",\n",
        "tests.test_validador.PruebasInvariantes.test_e20_vecino_inexistente",
        "B-07: E20 estaba viva sin prueba que la viera en rojo; ahora un vecino inexistente tiene la suya",
    ),
    Mutacion(
        "M85",
        "puente/sesion.py",
        "    if grado in (\"auto\", \"libre\"):\n        return None\n    if grado == \"desconocido\":\n",
        "    if grado in (\"auto\", \"libre\", \"manual\"):\n        return None\n    if grado == \"desconocido\":\n",
        "puente.tests.test_sesion_autonomia.LaCartaYLaMaquinaDicenLoMismo.test_avisa_en_rojo_cuando_la_maquina_arranca_en_manual",
        "A §2.6: si G01 calla con la máquina en manual, el océano `autonomia` es una exhortación que el agente se cree",
    ),
    Mutacion(
        "M86",
        "cosmos/compilar.py",
        "        if actual != esperado:\n            errores.append(f\"{entrada} no coincide con su nodo {nodo.ruta_relativa}\")\n",
        "        if False:\n            errores.append(f\"{entrada} no coincide con su nodo {nodo.ruta_relativa}\")\n",
        "tests.test_anfitrion.Arbol.test_compilar_devuelve_el_runtime_byte_a_byte_y_e22_lo_vigila",
        "E22: sin comparar el hash, un fichero de runtime editado a mano pasa por sincronizado",
    ),
    Mutacion(
        "M87",
        "cosmos/modelo.py",
        "        quitando = clave in CLAVES_COSMOS\n",
        "        quitando = False\n",
        "tests.test_anfitrion.ElParserTolera.test_sin_claves_cosmos_devuelve_el_original_byte_a_byte",
        "COMPILACION: si compilar no quita las claves de COSMOS, el runtime deja de ser el fichero original",
    ),
    Mutacion(
        "M88",
        "cosmos/validar.py",
        "            if anfitrion is None:\n                for campo in sorted(set(nodo.datos) - permitidos):\n",
        "            if True:\n                for campo in sorted(set(nodo.datos) - permitidos):\n",
        "tests.test_anfitrion.Arbol.test_e00_acepta_las_claves_del_anfitrion_solo_con_la_declaracion",
        "FRONTMATTER: si E00 no abre la puerta con `anfitrion`, ningún fichero del runtime puede ser nodo",
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
        # `.git` viaja con la copia: tres pruebas del juez (M63, M64, M76) leen la historia y se
        # saltan sin ella con `skipIf`, y un test saltado devuelve 0 — la mutación salía VERDE
        # sin que nadie la vigilara (revisión B-02: 76/79 donde el cierre decía 79/79).
        shutil.copytree(
            RAIZ, copia,
            ignore=shutil.ignore_patterns("__pycache__", ".cosmos", "research"),
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
