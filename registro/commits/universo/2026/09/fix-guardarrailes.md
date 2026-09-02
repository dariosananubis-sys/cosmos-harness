# Los guardarraíles de sesión se saltaban: F02, F04 y F08

Fecha: 2026-09-02 · Spec dueña: [`../../../../../spec/GUARDARRAILES.md`](../../../../../spec/GUARDARRAILES.md) ·
Origen: [`../../../../../reviews/fallos-especialista.md`](../../../../../reviews/fallos-especialista.md), hallazgos F02, F04 y F08.

**Estado fijado** (el árbol muta mientras se escribe): base `eea0116`, con otro agente trabajando a
la vez en `cosmos/`, `tests/` y `docs/`. Este parte cubre 4 ficheros —`puente/sesion.py`,
`puente/tests/test_sesion.py`, `puente/tests/mutaciones.py` y `spec/GUARDARRAILES.md`—, ninguno
suyo. SHA-256 (12): `bf389fd0649d`, `576b64f06d74`, `3a73bd13b549`, `a92810837bf2`. Se referencia
por símbolo, nunca por `fichero:línea`.

Los tres se reprodujeron **antes** de tocar código, con el guion del informe, y los tres salieron
exactamente como el informe decía. Sin ese paso se arregla lo que uno cree que dice el informe.

---

## F02 · G03 se saltaba con siete formas de shell

### La reproducción, ejecutada

El guion del informe, contra el repositorio real (`PreToolUse` es solo lectura, no escribe nada):

```bash
python3 - <<'PY'
import json, subprocess, sys
REPO="/Users/dariosatino/cosmos"; D=REPO+"/galaxia/COSMOS.md"
def probar(cmd):
    ev={"hook_event_name":"PreToolUse","session_id":"s1","cwd":REPO,
        "tool_name":"Bash","tool_input":{"command":cmd}}
    p=subprocess.run([sys.executable,"-m","puente.sesion","--formato","json","--config",REPO+"/cosmos.toml"],
                     input=json.dumps(ev),capture_output=True,text=True,cwd=REPO)
    s=p.stdout.strip()
    return "PASA" if not s else json.loads(s).get("hookSpecificOutput",{}).get("permissionDecision","?")
for n,c in [("control >",f"echo x > {D}"), ("control >>",f"echo x >> {D}"),
            ("control tee",f"echo x | tee {D}"), ("control cp",f"cp /etc/hosts {D}"),
            ("A &>",f"echo x &> {D}"), ("B redireccion delante",f"> {D} echo x"),
            ("C >|",f"echo x >| {D}"), ("D continuacion de linea",f"echo x \\\n  > {D}"),
            ("E 'cosmos' de argumento",f"python3 -c cosmos > {D}"),
            ("F sustitucion de orden",f"echo x > $(echo {D})"),
            ("G dd of=",f"dd if=/etc/hosts of={D}")]:
    print(f"{probar(c):6}  {n}")
PY
```

Antes: `deny` en los cuatro controles y **`PASA` en las siete evasiones**. Después: `deny` en las
once líneas.

Y las tres causas, comprobadas por separado:

```
$ python3 -c "from puente.sesion import es_productor_autorizado as P
print(P('python3 -c cosmos'), P('python3 x.py cosmos'), P('py cosmos'), P('cosmos lo-que-sea'))"
True True True True
$ python3 -c "from puente.sesion import _ASIGNACION; print(bool(_ASIGNACION.match('of=x')))"
True
```

### Qué cambié

1. **`_REDIRECCION` reconoce los operadores compuestos**: `^(?P<descriptor>[0-9]*&?)>>?(?P<modo>[|&]?)(?P<destino>.*)$`.
   Antes `&>` y `>|` no casaban y la orden no declaraba destino. Añadida `_DUPLICA_DESCRIPTOR`
   (`^[0-9]*>&[0-9]+$`) para que `2>&1` no cuente como escribir un fichero llamado `1`.
2. **`ordenes()` no parte dentro de un operador compuesto** ni en una continuación de línea. El
   bucle pasa a máquina de estados con índice: al ver `>` o `<` absorbe los `>&|` que le siguen; un
   `&` seguido de `>` no separa; `|&` separa consumiendo los dos; un `\` escapa al carácter
   siguiente, y `\`+salto se normaliza a un espacio como hace el shell.
3. **`objetivos_de_escritura()` deja de saltar el índice 0 a ciegas.** La rama de redirección va
   ahora **antes** del salto: el primer elemento se salta por ser el programa, no por ser el
   primero, y `> fichero orden` —POSIX válido— vuelve a declarar destino. La rama `of=` sube por
   delante de `_ASIGNACION`, que casaba antes con `of=` y la dejaba inalcanzable (código muerto que
   el informe marcó y que era justo la evasión G).
4. **`es_productor_autorizado` se retira; no se parchea.** Ver la sección siguiente.
5. **Un destino que se calcula al ejecutar se deniega.** `_NO_RESOLUBLE` casa `$` y la comilla
   invertida; si un objetivo declarado las contiene —sustitución de órdenes o variable—, G03 deniega
   con su propio motivo («el destino de la escritura se calcula al ejecutar») en vez de resolverlo
   contra el `cwd` y dar por bueno lo que no ha comprobado.

### `es_productor_autorizado`: no había criterio robusto, así que se cambió el enfoque

Decidía por el **nombre del programa que arranca la orden** más la palabra `cosmos` suelta entre sus
piezas. Eso lo falsifica cualquiera —`python3 x.py cosmos`, un ejecutable llamado `cosmos` en el
`PATH`, una función de shell con ese nombre—, y no hay nada mejor que poner en su lugar: lo único
que el guard ve es una cadena de shell, y todo lo que se escribe en una cadena de shell se puede
escribir a propósito.

La conclusión no es «un criterio más fino», es que **la excepción no hacía falta**.
`objetivos_de_escritura` solo declara las escrituras del propio shell; lo que COSMOS escribe lo
escribe desde dentro de Python y nunca aparece como destino de la orden. Comprobado: sin la
excepción, `python3 -m cosmos generar` sigue pasando —por no declarar ningún destino, no por un
permiso— y lo único que deja de pasar es `python3 -m cosmos medir > galaxia/COSMOS.md`, que es
exactamente la autocertificación que G03 existe para impedir. La función y su regex `_PRODUCTOR`
están borradas, con el porqué escrito en su hueco para que nadie las reinvente.

### Los tests que lo fijan

Clase nueva `EvasionesDeShell`, **una prueba por evasión**, no una genérica —una genérica se pone
verde con la primera arreglada y deja las otras seis abiertas—:

| Evasión | Prueba |
|---|---|
| `&>` | `test_a_redireccion_con_ampersand` |
| `&>>` | `test_a_bis_redireccion_con_ampersand_y_anexado` |
| `> fichero orden` | `test_b_redireccion_delante_del_programa` |
| `>|` | `test_c_redireccion_que_ignora_noclobber` |
| `\` + salto de línea | `test_d_continuacion_de_linea` |
| `cosmos` de argumento | `test_e_la_palabra_cosmos_de_argumento_no_autoriza` |
| `$(...)` y `$VAR` | `test_f_un_destino_calculado_se_deniega`, `test_f_bis_una_variable_como_destino_tambien` |
| `dd of=` | `test_g_dd_escribe_en_of` |

Con sus vecinos, que **no** deben dispararlo: `test_una_redireccion_compuesta_a_una_ruta_inocente_pasa`,
`test_duplicar_un_descriptor_no_es_escribir_un_fichero` y, en `RutasDeVeredicto`,
`test_una_orden_de_cosmos_sin_redireccion_pasa`. Más, en `Segmentacion`,
`test_un_operador_compuesto_no_parte_la_orden` y `test_una_continuacion_de_linea_no_termina_la_orden`.

---

## F04 · Abrir la válvula de G05 dejaba a G04 denegando toda escritura

### La reproducción, ejecutada

Sobre copia, con `[sesion] lecturas_exigidas = ["GOAL.md"]` en `cosmos.toml`:

```
sin salto:                        con G05 saltado (antes):        después:
  escribir sin leer  -> deny        escribir sin leer  -> deny      -> deny
  leer GOAL.md       -> PASA        leer GOAL.md       -> PASA      -> PASA
  escribir tras leer -> PASA        escribir tras leer -> DENY      -> PASA
  marcas en disco    -> [lectura-…] marcas en disco    -> []        -> [lectura-…]
```

### Qué cambié

`despues_de_la_herramienta()` comprobaba `CODIGO_REDACCION in saltados` y devolvía `PASAR` **antes**
de llegar al marcado de lectura, que es G04 y no G05. El marcado sube por delante del
cortacircuitos. Y se marca **incluso con G04 saltado**: registrar el hecho no cuesta nada, el salto
caduca antes que la sesión, y quien decide si la marca hacía falta es `PreToolUse` — así el mismo
acoplamiento no vuelve por la otra puerta cuando el salto venza a media sesión.

### Los tests que lo fijan

`MarcaDeLectura.test_saltar_la_redaccion_no_desarma_la_marca_de_lectura` (salta G05, lee, exige que
la escritura pase) y su pareja `test_saltar_la_lectura_deja_escribir_sin_haber_leido` (salta G04,
exige que la escritura pase sin haber leído).

---

## F08 · G05 solo tapaba `stdout` de Bash

### La reproducción, ejecutada

`PostToolUse` con un valor con forma de secreto por cada canal. Antes / después:

| Canal | Antes | Después |
|---|---|---|
| `Bash` · `output` | TAPADO | TAPADO |
| `Bash` · `stdout` | TAPADO | TAPADO |
| `Bash` · `stderr` | **NO TAPADO** | TAPADO |
| `Read` (`file.content`) | **NO TAPADO** | TAPADO |
| `Grep` (`output`) | **NO TAPADO** | TAPADO |
| `Task` (bloques de `content`) | **NO TAPADO** | TAPADO |

### Qué cambié

- **`_respuesta()` devuelve todo el texto y por qué claves se puede reescribir.** Leía `output` y, a
  falta de él, `stdout`. Ahora recorre `output`, `stdout`, `stderr` y `content` —los canales que
  llegan como cadena suelta y por tanto se pueden sustituir— y, si ninguno trae texto, cae a
  `_texto_anidado()` para las formas propias de `Read` (`file.content`) y `Task` (bloques). `stderr`
  entra además en el conteo del desvío de salidas grandes, que antes tampoco lo miraba.
- **`HERRAMIENTAS_VIGILADAS = ("Bash", "Read", "Grep", "Glob", "Task")`** sustituye al
  `if herramienta != "Bash": return PASAR`.
- **El texto redactado vuelve por los canales que lo trajeron.** `Decision` lleva `canales` y
  `como_json` los emite dentro de `updatedToolOutput`: el primero con el texto, los demás vaciados.
  Sustituir solo `output` dejaba el valor crudo entrando por `stderr` si el runtime separa los
  canales — la corrección habría sido decorativa.

### Los tests que lo fijan

`Redaccion`: `test_tapa_el_valor_que_sale_por_stderr`,
`test_el_texto_redactado_vuelve_por_los_dos_canales`, `test_tapa_lo_que_devuelve_una_lectura`,
`test_tapa_lo_que_devuelve_un_grep`, `test_tapa_lo_que_devuelve_un_subagente`, y el vecino
`test_una_herramienta_fuera_de_la_lista_pasa`.

---

## Lo que NO cubro, y por qué

Está escrito también en `spec/GUARDARRAILES.md`, en la tabla de canales de G05 y en la sección de
G03. Una cobertura declarada de más tranquiliza sin proteger; una honesta de menos, no.

1. **`Grep`, `Glob` y `Task` no llegan al guard hoy.** El guard los tapa —los tests lo demuestran
   llamando al manejador—, pero el cableado enruta `PostToolUse` por el filtro
   `Bash|Read` de `EVENTOS_SESION`, que vive en `cosmos/guardarrailes.py`, **fuera de mi
   boundary** (hay otro agente en el núcleo). Mientras ese filtro no se amplíe, esas tres filas son
   límite declarado, no cobertura. Es un cambio de una línea y lo elevo abajo.
2. **La sustitución en respuestas anidadas depende del runtime.** Para `Read` con `file.content` o
   `Task` con bloques, COSMOS lee el texto y decide, pero que `updatedToolOutput` se aplique fuera de
   `Bash` no se puede comprobar desde aquí, y sin poder medirlo no se declara cubierto. Lo que sí
   ocurre siempre es el aviso por `additionalContext`.
3. **Lo que escriba un intérprete que la orden arranque sigue fuera de G03** (`python -c "open(...)"`).
   Ya estaba declarado y no cambia: es indecidible sin ejecutar, y perseguirlo con más regex es el
   antipatrón que este proyecto documentó.
4. **`exit2` no puede reescribir**, así que G05 ahí no bloquea. Sin cambios; ya estaba declarado.

## Frentes que abre este arreglo

- **G03 deniega ahora un destino calculado** (`echo x > $HOME/log`, `> $(...)`, `> $VAR`), aunque la
  ruta final fuese inocente. Es deliberado: no se puede resolver antes de ejecutar, y pasar sería
  fingir cobertura. El coste es un `deny` en órdenes legítimas que usen variables en el destino; el
  mensaje dice la salida (escribir la ruta literal) y la válvula `cosmos saltar G03` sigue ahí. Si
  molesta en el uso real, la decisión a revisar es esta línea, no el resto del arreglo.
- **Ya no existe productor autorizado.** Si alguien añade un comando de COSMOS que escriba un
  artefacto de veredicto **por redirección del shell** en vez de desde Python, G03 lo denegará y
  hará bien: tendrá que escribirlo desde dentro, como los demás.
- **El marcado de lectura ocurre aunque G04 esté saltado.** Es un cambio de comportamiento respecto
  a la propuesta del informe (que proponía no marcar); se hizo así a propósito para no repetir el
  acoplamiento de F04 en el momento en que el salto caduque.

## Para el agente del núcleo (fuera de mi boundary)

1. `EVENTOS_SESION` en `cosmos/guardarrailes.py`: `("PostToolUse", "Bash|Read")` →
   `("PostToolUse", "Bash|Read|Grep|Glob|Task")` cierra la fila 3 de la tabla de canales de G05. El
   guard ya está listo; solo falta que el evento llegue.
2. `spec/GUARDARRAILES.md` promete ahora esa cobertura como **límite declarado**: si se amplía el
   filtro, hay que actualizar la tabla.

## Verificación

```
$ python3 -m unittest discover -s puente/tests   ->  Ran 102 tests  OK      (eran 80)
$ python3 puente/tests/mutaciones.py             ->  30/30 invariantes vistas fallar   (eran 18/18)
$ python3 -m cosmos validar                      ->  COSMOS  verde  0 errores
$ python3 -m cosmos medir                        ->  Presupuesto 4.000  OK
```

`python3 -m unittest discover -s tests` da **95 OK (skipped=1)** sobre `eea0116` con solo mis
cambios de `puente/` aplicados (comprobado en copia limpia: `git checkout -- .` y copiar encima los
tres ficheros de `puente/`). En el árbol vivo da `FAILED (failures=1)`, y el fallo es ajeno:
`test_medidor.test_los_factores_publicados_son_los_que_documenta_la_calibracion` contra
`docs/CALIBRACION.md`, del trabajo en curso del núcleo sobre F01. Ni `tests/` ni `docs/` están en mi
boundary.

**Efecto colateral declarado:** ejecutar la suite del núcleo regeneró `ejemplo/COSMOS.md` bajo el
`cosmos/generar.py` que ese agente tiene sin commitear. No lo revierto porque revertirlo vuelve a
poner `tests/test_cli` en rojo; queda anotado para que su dueño decida.
