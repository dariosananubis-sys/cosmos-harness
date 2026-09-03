"""Sabotea el codigo a proposito y comprueba si la suite se pone roja.

Uso: python3 sabotear.py <id>   -> imprime "<id> CAZADO|SUPERVIVIENTE ..."
Cada mutacion trabaja sobre una copia limpia de /tmp/rp/base (HEAD congelado).
"""
import json, os, shutil, subprocess, sys, pathlib

BASE = pathlib.Path("/tmp/rp/base")
TRABAJO = pathlib.Path("/tmp/rp/trabajo")

# id: (fichero, viejo, nuevo, que_afirma)
MUT = {
 "M00": ("cosmos/medir.py", "", "", "linea base sin sabotaje"),
 "M01": ("cosmos/medir.py", "cabe=peor.entrada_con_agua <= presupuesto,",
         "cabe=peor.entrada <= presupuesto,",
         "el juez del presupuesto deja de sumar el agua"),
 "M02": ("cosmos/medir.py", "cabe=peor.entrada_con_agua <= presupuesto,",
         "cabe=casos.evaluada.entrada_con_agua <= presupuesto,",
         "el juez cobra sobre la seleccion, no sobre el peor nicho"),
 "M03": ("cosmos/medir.py", "        peor_nicho, peor = max(por_nicho, key=lambda caso: caso[1].entrada)",
         "        peor_nicho, peor = min(por_nicho, key=lambda caso: caso[1].entrada)",
         "el 'peor' nicho pasa a ser el mas barato"),
 "M04": ("cosmos/modelo.py", "        os.replace(temporal_path, ruta)",
         "        shutil.copyfile(temporal_path, ruta)",
         "escribir_atomico deja de ser atomico (copia byte a byte)"),
 "M05": ("cosmos/modelo.py", "            os.fsync(fichero.fileno())", "            pass",
         "escribir_atomico deja de hacer fsync"),
 "M06": ("cosmos/modelo.py", "            if pid is not None and pid != os.getpid() and _proceso_vivo(pid):",
         "            if False:",
         "el cerrojo deja de respetar a un proceso vivo: siempre roba"),
 "M07": ("cosmos/modelo.py", "            ruta.unlink(missing_ok=True)\n    try:",
         "            raise ErrorCerrojo(f'otra {que_hace} esta en curso: {ruta}') from exc\n    try:",
         "el cerrojo rancio deja de recuperarse (repo inservible tras kill -9)"),
 "M08": ("cosmos/abrir.py", "    relativa = ruta_fichero[2:] if ruta_fichero.startswith(\"./\") else ruta_fichero",
         "    relativa = ruta_fichero[2:] if ruta_fichero.startswith(\"./\") else ruta_fichero\n    return []",
         "agua_que_moja devuelve siempre vacio"),
 "M09": ("cosmos/abrir.py", "            raise NodoNoEncontrado(",
         "            return []\n            raise NodoNoEncontrado(",
         "una ruta fuera del proyecto vuelve a devolver agua vacia en silencio"),
 "M10": ("cosmos/acertar.py", "    if not c.validacion or not c.validacion.total:",
         "    if not c.validacion:",
         "formatear_contraste vuelve a dividir por cero con validacion vacia"),
 "M11": ("cosmos/guardarrailes.py", "    return codigos_comprobados()",
         "    return tuple(f'E{n:02d}' for n in range(20))",
         "la valvula vuelve a la cadena a mano E00..E19 (E20 sin valvula)"),
 "M12": ("puente/sesion.py", "        orden = datos.get(\"command\")",
         "        orden = None",
         "_rutas_del_evento deja de mirar el comando de Bash"),
 "M13": ("puente/sesion.py", "    if entrada.get(\"hook_event_name\") == \"PreToolUse\" and not entrada.get(\"tool_name\"):",
         "    if False:",
         "PreToolUse malformado vuelve a pasar en silencio"),
 "M14": ("cosmos/acertar.py", "        if nodo.cosmos == \"sistema-solar\"",
         "        if nodo.cosmos == \"sistema-solar\" and False",
         "acertar vuelve a puntuar sin los 21 oficios (el recorte del arbol)"),
 "M15": ("cosmos/acertar.py", "    return elegida == esperada or elegida.startswith(esperada + \"/\")",
         "    return True",
         "_acierta dice que si a todo: 100% de acierto"),
 "M16": ("cosmos/acertar.py", "        if palabra.endswith(sufijo) and len(palabra) - len(sufijo) >= RAIZ_MINIMA:",
         "        if False:",
         "el recorte de sufijos se apaga (peor emparejamiento)"),
 "M17": ("cosmos/medir.py", "        if metodo_real == \"aprox\" and (\"índice\" in nombre or \"catálogo\" in nombre):",
         "        if False:",
         "indice y catalogo dejan de usar su factor propio (F01)"),
 "M18": ("cosmos/validar.py", "    _comprobar_e19, _comprobar_e20,", "    _comprobar_e19,",
         "E20 sale de COMPROBACIONES: 'usa' deja de validarse"),
 "M19": ("cosmos/abrir.py", "            if n.cosmos == \"estrella\" and n.datos.get(\"ilumina\") == nodo.referencia",
         "            if n.cosmos == \"estrella\" and nodo.referencia.endswith(str(n.datos.get(\"ilumina\")))",
         "la estrella vuelve a engancharse por nombre suelto (colision de NUCLEO 1)"),
 "M20": ("cosmos/medir.py", "    nodos_resto = [\n        nodo for nodo in arbol.nodos if nodo.cosmos not in {\"oceano\", \"lluvia\"}\n    ]",
         "    nodos_resto = [nodo for nodo in arbol.nodos if nodo.cosmos not in {\"oceano\"}]",
         "la lluvia vuelve a inflar la descarga sola"),
 "M21": ("cosmos/modelo.py", "        descriptor = os.open(ruta, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)",
         "        descriptor = os.open(ruta, os.O_CREAT | os.O_WRONLY, 0o644)",
         "el cerrojo deja de ser exclusivo (O_EXCL fuera)"),
 "M22": ("puente/sesion.py", "                if _dentro(objetivo, protegida):", "                if False:",
         "G03 deja de proteger las rutas de veredicto"),
 "M23": ("cosmos/validar.py", "def rango_comprobado() -> str:",
         "def rango_comprobado() -> str:\n    return 'E00–E19'\ndef _rango_muerto() -> str:",
         "rango_comprobado vuelve a mentir con una cadena a mano"),
 "M24": ("cosmos/acertar.py", "        if c.validacion is not None and not c.validacion.total:",
         "        if False:",
         "el conjunto de validacion VACIO deja de avisarse"),
}

def correr(dirtrab):
    r = {}
    for etiqueta, args in (("tests", ["-s","tests","-t","."]), ("puente", ["-s","puente/tests","-t","."])):
        p = subprocess.run([sys.executable,"-m","unittest","discover",*args],
                           cwd=dirtrab, capture_output=True, text=True)
        r[etiqueta] = (p.returncode, [l for l in p.stderr.splitlines() if l.startswith(("Ran ","OK","FAILED"))])
    p = subprocess.run([sys.executable,"-m","cosmos","validar"], cwd=dirtrab, capture_output=True, text=True)
    r["validar"] = (p.returncode, p.stdout.splitlines()[:1])
    p = subprocess.run([sys.executable,"puente/tests/mutaciones.py"], cwd=dirtrab, capture_output=True, text=True)
    r["mutaciones"] = (p.returncode, p.stdout.strip().splitlines()[-1:])
    return r

def main():
    mid = sys.argv[1]
    fichero, viejo, nuevo, afirma = MUT[mid]
    dirtrab = TRABAJO / mid
    if dirtrab.exists(): shutil.rmtree(dirtrab)
    dirtrab.mkdir(parents=True)
    subprocess.run(["tar","-xf","/tmp/rp/pristino.tar","-C",str(dirtrab)],check=True)
    if mid == "M00":
        r = correr(dirtrab)
        print(json.dumps({"id":mid,"estado":"BASE","detalle":r}, ensure_ascii=False)); return
    ruta = dirtrab / fichero
    texto = ruta.read_text(encoding="utf-8")
    if texto.count(viejo) != 1:
        print(json.dumps({"id":mid,"estado":"NO_APLICA","ocurrencias":texto.count(viejo),"afirma":afirma}))
        return
    if fichero == "cosmos/modelo.py" and "shutil" in nuevo:
        texto = texto.replace("import tempfile", "import tempfile\nimport shutil", 1)
    ruta.write_text(texto.replace(viejo, nuevo, 1), encoding="utf-8")
    r = correr(dirtrab)
    BASE_OK = {"tests": "OK", "puente": "OK", "validar": "COSMOS  rojo  1 errores",
               "mutaciones": "38/38 invariantes vistas fallar"}
    difs = []
    for k, esperado in BASE_OK.items():
        obtenido = " ".join(r[k][1])
        if esperado not in obtenido:
            difs.append(f"{k}: {obtenido[:90]}")
    rojo = bool(difs)
    print(json.dumps({"id":mid,"estado":"CAZADO" if rojo else "SUPERVIVIENTE",
                      "afirma":afirma,"difs":difs,"detalle":r}, ensure_ascii=False))

main()
