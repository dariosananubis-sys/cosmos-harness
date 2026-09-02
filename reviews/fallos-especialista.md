# COSMOS — fallos encontrados por el especialista

**Premisa**: todo esto está mal y mi trabajo era demostrarlo. Lo que aparece bajo «Lo que intenté y
aguantó» solo está ahí después de haber intentado tumbarlo y no haber podido, y digo qué intenté.

Esta revisión **empieza donde acabó** `reviews/revision-adversarial-final.md` (26 hallazgos, todos
declarados cerrados). No repito su trabajo: verifico sus cierres y ataco lo que se escribió
**después** — `puente/sesion.py`, los guardarraíles G01–G05, la calibración del medidor, el peor
caso de agua por extensión (dos horas antes de esta auditoría) y `cosmos/abrir.py` (durante ella).

---

## Estado auditado (fijado en cabecera: el árbol muta)

```
$ cd <repo> && git rev-parse HEAD && git status --porcelain | wc -l
d54668ef9948ee39704b54f1cd96508663675d86
       0
$ python3 --version          # 3.14.3 · tiktoken NO instalado en el sistema
$ shasum -a 256 <ficheros clave> | cut -c1-12
efb7ab2cb28a  cosmos/medir.py        a755ff1d9cc3  puente/sesion.py
f5cd39bcc8bb  cosmos/validar.py      d89b69638e96  cosmos/compilar.py
6a131d670f01  cosmos/abrir.py        390530a41762  GOAL.md
088a9f4cf8f0  spec/NUCLEO.md
```

> **El árbol mutó durante la auditoría.** Empecé en `1ca3e25`; al cerrar, otra ventana había
> commiteado `dc61ea5` (`cosmos/abrir.py`, comando nuevo) y `d54668e` (GOAL §2 reescrito). **Todas
> las mediciones se re-verificaron en `d54668e`** y ninguna cambió: entrada base 1.664, peor nicho
> 2.483, agua 1.398, peor con agua 3.881, universo 158.037, descarga 98,4 %, validador verde. La
> suite pasó de 89 a 95 pruebas (`tests/test_abrir.py`). `reviews/mejoras-especialista.md` es del
> otro especialista y no lo he tocado.

Todo lo destructivo, en `/tmp/cosmos-esp/` (copias del repo, árboles sintéticos, sabotajes, un
`venv` con `tiktoken`). **El repositorio no se modificó salvo este fichero.**

**Cero credenciales encontradas.** Sí queda un dato personal, ver F24; no lo transcribo.

---

## Resumen

**24 fallos: 5 críticos, 6 graves, 13 medios o menores.** Cada uno lleva reproducción copiable y
arreglo concreto. Doce afirmaciones del estado publicado se pusieron a prueba; **cuatro caen**.

| Afirmación del estado publicado | Veredicto |
|---|---|
| Validador de 20 invariantes en verde | **DESMENTIDA** — con tokenizador real, E16 en **rojo, +544 tokens** (F01) |
| Peor caso con agua 3.881 de 4.000 | **DESMENTIDA** — el real es **4.544**; el margen publicado (119) es negativo (F01) |
| 169 tests en verde (89+80) | **DESMENTIDA** — la misma suite da `FAILED (failures=1)` en cuanto hay tokenizador (F03) |
| Calibración ±5 % | **DESMENTIDA** — el bloque que domina el presupuesto (catálogo) se infravalora **21,2 %** (F01) |
| 18/18 mutaciones vistas fallar | **AGUANTA** — reproducidas 18/18 en rojo sobre copia |
| Escáner de secretos limpio | **AGUANTA** — `exit 0`, y el gate completo en verde |
| Entrada base 1.664, descarga 98,4 % | **AGUANTA** con `metodo="aprox"`; ver F01 y F23 sobre qué mide |
| 21 oficios, 247 herramientas | **AGUANTA** en el árbol; `GOAL.md` sigue diciendo 20 (F13) |
| El contenido de las fichas es real | **AGUANTA, y bien** — 7 repos verificados contra la API de GitHub: licencias exactas, estrellas ±5, fechas de push exactas; 8 paquetes existen |
| `compilar` no se corrompe en paralelo | **AGUANTA** — dos simultáneos: uno gana, el otro falla limpio, árbol verde |
| Casos degradados sin excepción no controlada | **AGUANTA** — 10 árboles rotos, ningún *traceback* |
| G03 impide escribir a mano el veredicto | **DESMENTIDA** — 7 formas de shell lo esquivan (F02) |

---

# CRÍTICOS — rompen el sistema

## F01 · CONFIRMADO · Con un tokenizador real el árbol está en ROJO: 4.544 / 4.000. El verde es un artefacto del contador aproximado

Es el fallo mayor: **el número que decide todo el proyecto está 15,8 % bajo**, y el error no se
reparte — se concentra justo en el bloque más caro.

`docs/CALIBRACION.md` calibró contra `tiktoken/cl100k_base` sobre 78 ficheros de **prosa** (specs,
fichas, código, agua) y publicó `MARGEN_ERROR = 0.052`. El corpus **no contiene una sola muestra de
los dos bloques que forman la entrada**: el índice generado y el catálogo generado. Y son
precisamente los que peor tokeniza contar palabras: el catálogo es una lista de `ruta: resumen`
—barras, guiones, acentos, sin prosa que amortigüe—.

```bash
# Reproducción completa (venv temporal, no toca el repo, no cuesta dinero)
python3 -m venv /tmp/calib && /tmp/calib/bin/pip install -q tiktoken
cd <repo> && /tmp/calib/bin/python - <<'PY'
import sys; sys.path.insert(0,'.')
import tiktoken
from cosmos.medir import contar_aprox, _bloques_contexto_inicial, agua_condicional
from cosmos.modelo import cargar_arbol, cargar_configuracion, cuerpo
enc=tiktoken.get_encoding("cl100k_base"); E=lambda t: len(enc.encode(t))
cfg=cargar_configuracion('cosmos.toml')
a=cargar_arbol(cfg.arbol,excluir=cfg.indice,excluir_directorios=(cfg.destino_compilacion,),tambien=(cfg.registro,))
ta=te=0
for n,t in _bloques_contexto_inicial(a,None,["ciberseguridad"]):
    x,y=contar_aprox(t),E(t); ta+=x; te+=y
    print(f"  {n:24} aprox={x:5} exacto={y:5}  error={(x-y)/y*100:+6.1f}%")
for n in agua_condicional(a):
    x,y=contar_aprox(cuerpo(n)),E(cuerpo(n))
    print(f"  {'agua/'+n.nombre:24} aprox={x:5} exacto={y:5}  error={(x-y)/y*100:+6.1f}%")
print(f"  {'TOTAL':24} aprox={ta:5} exacto={te:5}  error={(ta-te)/te*100:+6.1f}%")
PY
```

Salida literal:

```
  índice de galaxia        aprox=  643 exacto=  724  error= -11.2%
  oceano/descender         aprox=  144 exacto=  155  error=  -7.1%
  oceano/irreversible      aprox=   93 exacto=   93  error=  +0.0%
  oceano/precedencia       aprox=   69 exacto=   74  error=  -6.8%
  oceano/secretos          aprox=   81 exacto=   79  error=  +2.5%
  oceano/verificar         aprox=   83 exacto=   87  error=  -4.6%
  catálogo visible         aprox= 1370 exacto= 1738  error= -21.2%     <-- 55 % de la entrada
  agua/accesibilidad       aprox=  101 exacto=  117  error= -13.7%
  agua/criterio            aprox=  421 exacto=  481  error= -12.5%
  agua/custodia            aprox=  107 exacto=  119  error= -10.1%
  agua/pruebas             aprox=  473 exacto=  544  error= -13.1%
  agua/resistencia         aprox=  161 exacto=  183  error= -12.0%
  agua/revision            aprox=  236 exacto=  267  error= -11.6%
  TOTAL                    aprox= 2483 exacto= 2950  error= -15.8%
```

Y el veredicto, cambiando **solo** `metodo` en `cosmos.toml` (sobre una copia en `/tmp`):

```
$ sed -i '' 's/^metodo = "aprox"/metodo = "exacto"/' cosmos.toml
$ /tmp/calib/bin/python -m cosmos medir | grep -E "Peor con agua|Presupuesto"
  Peor con agua ... 4.544 tokens   (el peor caso + agua condicional)
  Presupuesto ..... 4.000     ROJO, excede en 544 tokens en el peor caso con agua

$ /tmp/calib/bin/python -m cosmos validar; echo "EXIT=$?"
COSMOS  rojo  1 errores

E16  presupuesto
     peor nicho ciberseguridad: entrada 2950 + agua condicional 1594 = 4544 tokens > 4000;
     excede en 544 tokens; más caros: catálogo visible (1738), índice de galaxia (724), mar/pruebas (544)
EXIT=1
```

`NUCLEO.md` §4 existe para que «el veredicto sea una propiedad del árbol» y no del entorno. Lo
consigue en el sentido literal —fijando el método— y lo pierde en el que importa: **el método fijado
es el que da verde**, y el que mide de verdad da rojo por 544 tokens. El margen publicado
(«quedan 119») no existe: es −544.

Además el ±5 % es honesto solo como media por fichero de prosa. Medido hoy sobre el corpus vivo
(258 ficheros): error medio 3,9 %, p95 9,1 %, peor 14,8 %. Es decir: **el margen se publicó para una
población y se aplica a otra.** Y aunque fuera 5 %, ±5 % sobre 3.881 son ±194 tokens: 1,6 veces el
colchón que se publica. El colchón siempre estuvo dentro del ruido.

**Arreglo (tres piezas, en este orden):**

1. **Calibrar contra lo que se mide.** Añadir al corpus de `docs/CALIBRACION.md` la salida de
   `generar_indice(arbol)` y de `catalogo_visible(arbol, [nicho])` de la galaxia real, que son el
   80 % de la entrada. Con el corpus corregido el factor sube de 1,204 a ≈1,19·(1/0,842)≈1,43 para
   esos bloques; lo honesto es **un factor por clase de texto**, no uno global:
   `contar_aprox(texto, clase)` con `{"prosa": 1.204, "indice": 1.126, "catalogo": 1.269}`, medidos
   con el bloque de arriba.
2. **Mientras tanto, presupuesto con margen explícito.** `E16` debe comparar
   `entrada_con_agua * (1 + MARGEN_ERROR)` contra `config.entrada` cuando `estimado=True`. Un punto
   estimado contra un techo duro no es una comprobación, es una apuesta.
3. **Publicar el intervalo, no el punto**: `Peor con agua ... 3.881 tokens (3.687–4.075, ±5 %)`. Hoy
   el formateador imprime el punto y el margen por separado, y nadie los multiplica.

**Cómo se comprueba que quedó arreglado:** con el venv de arriba, `metodo="exacto"` y
`metodo="aprox"` tienen que dar **el mismo veredicto** (verde o rojo) sobre el mismo árbol. Hoy dan
distinto. Ese es el test que falta y que ninguna de las 175 pruebas hace.

---

## F02 · CONFIRMADO · G03 se salta con siete formas de shell, y `es_productor_autorizado` es una puerta abierta

G03 —«escritura a mano sobre una ruta de veredicto»— es el guard que impide poner en verde un árbol
que no lo está. `puente/sesion.py` lo escribió hoy y **no resiste el primer intento**.

```bash
# Reproducción: script completo en el cuerpo, se pega tal cual
cd <copia-en-/tmp> && python3 - <<'PY'
import json, subprocess, sys
REPO="/tmp/cosmos-esp/repo"; D=REPO+"/galaxia/COSMOS.md"
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

Salida literal:

```
deny    control >
deny    control >>
deny    control tee
deny    control cp
PASA    A &>
PASA    B redireccion delante
PASA    C >|
PASA    D continuacion de linea
PASA    E 'cosmos' de argumento
PASA    F sustitucion de orden
PASA    G dd of=
```

Y las siete **escriben de verdad** (comprobado con `bash -c` sobre un fichero de prueba: A, B, C, D
y F dejan el contenido; E y G lo truncan a vacío). El caso más grave escribe contenido arbitrario:

```bash
$ python3 -c "print('# COSMOS - mentira total')" cosmos > galaxia/COSMOS.md
# guard: PASA (silencio)   -> índice falsificado, E15 en rojo, y el guard no dijo nada
```

**Tres causas distintas, y conviene separarlas:**

1. **`ordenes()` parte por `;&|\n` sin conocer los operadores compuestos.** `&>` se parte en
   `["echo x", "> galaxia/COSMOS.md"]`; una continuación de línea (`\` + salto) también. Lo mismo
   `>|`, porque `|` es separador.
2. **`objetivos_de_escritura()` salta el índice 0 incondicionalmente** (`if indice == 0 ... continue`).
   Con eso, `> fichero cmd` —POSIX válido— y el resto de la orden `> fichero` que dejó (1) no
   declaran ningún objetivo.
3. **`es_productor_autorizado()` exime la orden entera** si el programa casa
   `^(?:python[0-9.]*|py)$|^cosmos$` **y la palabra `cosmos` aparece suelta entre sus piezas**:

```
$ python3 -c "from puente.sesion import es_productor_autorizado as P
print(P('python3 -c cosmos'), P('python3 x.py cosmos'), P('py cosmos'), P('cosmos lo-que-sea'))"
True True True True
```

`python3 x.py cosmos` —un guion cualquiera con `cosmos` de argumento— recibe permiso de escritura
sobre **todas** las rutas de veredicto.

**Bonus, código muerto:** la rama `if pieza.startswith("of="):` (para `dd`) **nunca se alcanza**,
porque `_ASIGNACION = ^[A-Za-z_][A-Za-z0-9_]*=` casa antes con `of=` y hace `continue`:

```
$ python3 -c "from puente.sesion import _ASIGNACION; print(bool(_ASIGNACION.match('of=x')))"
True
```

**Ninguno de los siete está en `puente/tests/test_sesion.py`.** Lo único cubierto es
`>`, `>>`, `tee`, `cp`, `sed -i` (líneas 98–117).

**Arreglo:**

- En `ordenes()`, reconocer los operadores compuestos **antes** de partir: tratar `&>`, `&>>`, `>&`,
  `>|` y `|&` como parte de la orden, no como separador. La forma barata y correcta es sustituirlos
  por un marcador antes del bucle y restaurarlos después, o partir con una máquina de estados que
  mire el carácter siguiente. Y **quitar el salto de línea del conjunto de separadores cuando la
  línea anterior acaba en `\`**.
- En `objetivos_de_escritura()`, borrar la condición `indice == 0`. El índice 0 solo debe saltarse si
  **es el programa**, es decir, si `_REDIRECCION` no casa con él. Con eso B y D caen solos.
- En `es_productor_autorizado()`, dejar de mirar si `cosmos` aparece «entre las piezas» y exigir la
  forma exacta: `piezas[:2] == ["-m", "cosmos"]` tras el intérprete (o `programa == "cosmos"` con
  una ruta absoluta comprobada). Un permiso que se concede por que una palabra aparezca en algún
  argumento no es un permiso.
- Aceptar y **declarar** que la sustitución de órdenes (`$(...)`) queda fuera —es indecidible sin
  ejecutar— pero entonces **denegar por defecto** toda orden que contenga `$(` o backticks y a la
  vez un operador de escritura. Es lo que ya hace el propio módulo con «lo que escriba un intérprete
  que la orden arranca»: declarar el límite, no fingir cobertura.
- Borrar la rama `of=` o moverla **antes** de `_ASIGNACION`.

**Cómo se comprueba:** el script de arriba tiene que imprimir `deny` en las once líneas.

---

## F03 · CONFIRMADO · La prueba que vigila la calibración FALLA en cuanto hay tokenizador; verde solo porque la máquina no lo tiene

Es la misma clase de fallo que `NUCLEO.md` §4 dice haber cerrado, en el sitio donde nadie miró: **el
test que guarda el número está `skipped` justo en la máquina donde se publicó el número.**

```
$ python3 -m unittest discover -s tests -t . 2>&1 | tail -2
Ran 95 tests in 5.4s
OK (skipped=1)

$ /tmp/calib/bin/python -m unittest discover -s tests -t . 2>&1 | tail -2   # el MISMO árbol, con tiktoken
Ran 95 tests in 4.5s
FAILED (failures=1)

$ /tmp/calib/bin/python -m unittest tests.test_medidor.PruebasMedidor.test_aproximado_y_exacto_respetan_margen_publicado 2>&1 | tail -6
  File "<repo>/tests/test_medidor.py", line 82, in test_aproximado_y_exacto_respetan_margen_publicado
    self.assertLessEqual(divergencia, medir.MARGEN_ERROR)
AssertionError: 0.19047619047619047 not less than or equal to 0.052
```

19,05 % contra un 5,2 % publicado, sobre un corpus de siete líneas que el propio test escribe. No es
un caso raro: es el caso de juguete.

**Y hay una segunda mentira, en la documentación de mantenimiento.** `docs/CALIBRACION.md`, sección
«Cómo rehacer esta medición», publica un guion que calcula
`ratio = exacto / (contar_aprox(t)/FACTOR_CALIBRACION)` y dice: *«Si el ratio se aleja de 1,0, el
factor se ha quedado viejo»*. Ese cociente **es el factor**: por construcción vale ≈1,204 cuando el
factor es correcto. Ejecutando el guion tal cual sobre el corpus de hoy:

```
n=258  ratio=1.2274      # criterio del documento: "muy lejos de 1,0" -> declararía roto un factor sano
```

El procedimiento de mantenimiento publicado **da siempre alarma**, así que nadie lo va a usar dos
veces.

**Arreglo:**

- Corregir el criterio en `docs/CALIBRACION.md`: el ratio se compara con `FACTOR_CALIBRACION`, no
  con 1,0. Umbral explícito: `abs(ratio/FACTOR - 1) > 0.05` → recalibrar.
- Arreglar el test: o el corpus del test es representativo (usar el índice y el catálogo reales,
  ver F01) o `MARGEN_ERROR` sube a lo que de verdad se mide. Lo que **no** puede quedar es un test
  que solo pasa por ausencia de dependencia.
- Meter `tiktoken` en el CI (es gratuito y no pide tarjeta) o, si no se quiere dependencia, **fallar
  ruidosamente** cuando el test se salta: `self.fail("sin tokenizador no se puede verificar el
  margen publicado; instálalo o baja MARGEN_ERROR a None")`. Un `skip` silencioso sobre la única
  prueba de la métrica principal es un verde comprado.

---

## F04 · CONFIRMADO · Abrir la válvula de G05 deja G04 denegando TODA escritura para siempre

`spec/GUARDARRAILES.md` promete que la válvula es **«Acotada: se salta un código concreto, nunca
todo»**. No lo es: G04 (marca de lectura) depende de código que vive detrás del cortacircuitos de
G05 (redacción).

```python
# puente/sesion.py, despues_de_la_herramienta()
saltados, activos, caducados = _saltados(base)
if CODIGO_REDACCION in saltados:      # G05
    return PASAR                      # <-- sale antes de llegar a la línea siguiente
herramienta = str(entrada.get("tool_name") or "")
if herramienta == "Read":
    return _marcar_si_procede(entrada, config, base)   # <-- esto es G04, no G05
```

Reproducción (sobre copia; `[sesion] lecturas_exigidas = ["GOAL.md"]` en `cosmos.toml`):

```
sin salto:
  1) escribir sin leer  -> deny
  2) leer GOAL.md       -> PASA  (deja marca)
  3) escribir tras leer -> PASA

$ python3 -m cosmos saltar G05 --motivo "prueba de acoplamiento" --caduca 1d
COSMOS  saltar  G05 saltado hasta el 2026-09-03 (1 d)

con G05 saltado:
  2) leer GOAL.md       -> PASA
  3) escribir tras leer -> DENY
  marcas en disco       -> []          <-- ninguna, y ya no se puede crear ninguna
```

Efecto: abrir la válvula de la **redacción de secretos** deja al agente sin poder escribir nada,
nunca, hasta que también abra la válvula de G04. Es decir, la válvula acotada obliga a abrir dos
guards. Y el que se abre de propina es el que impide autocertificarse.

Hoy no muerde porque `cosmos.toml` no trae `[sesion] lecturas_exigidas`. Muerde el día que alguien
use la funcionalidad, que está documentada y probada.

**Arreglo:** sacar el marcado de lectura fuera del cortacircuitos de G05. Dos líneas:

```python
def despues_de_la_herramienta(entrada, config, base):
    saltados, activos, caducados = _saltados(base)
    herramienta = str(entrada.get("tool_name") or "")
    if herramienta == "Read":
        return PASAR if CODIGO_LECTURA in saltados else _marcar_si_procede(entrada, config, base)
    if CODIGO_REDACCION in saltados or herramienta != "Bash":
        return PASAR
    ...
```

**Cómo se comprueba:** un test que salte G05, lea el fichero exigido y **exija que la escritura
posterior pase**. Y su pareja: saltar G04 y exigir que la escritura pase sin haber leído.

---

## F05 · CONFIRMADO · `cosmos medir` imprime «ROJO, excede en 544 tokens» y devuelve `exit 0`

El código de salida no mira el agua; el texto sí. Un CI que haga `cosmos medir || exit 1` aprueba un
árbol rojo.

```
$ /tmp/calib/bin/python -m cosmos medir; echo "EXIT MEDIR=$?"     # cosmos.toml con metodo="exacto"
  Peor con agua ... 4.544 tokens   (el peor caso + agua condicional)
  Presupuesto ..... 4.000     ROJO, excede en 544 tokens en el peor caso con agua
EXIT MEDIR=0
```

Causa, en `cosmos/cli.py`:

```python
return 0 if resultado_medicion.evaluada.entrada <= config.entrada else 1
#                                        ^^^^^^^ el formateador usa entrada_con_agua
```

El mismo criterio equivocado está copiado en el guard de sesión, y con un comentario que lo declara
a propósito (`puente/sesion.py`, `revisar_arbol`): *«Mismo criterio que el código de salida de
'cosmos medir': si aquí fuese otro, el guard y el comando dirían cosas distintas del mismo árbol»*.
Alinean dos sitios equivocados entre sí, y los dos discrepan de E16, que sí usa `entrada_con_agua`
(`cosmos/validar.py:444`) tal como manda `NUCLEO.md` §3.

**Arreglo:** en `cli.py`, `return 0 if resultado_medicion.evaluada.entrada_con_agua <= config.entrada
else 1`. En `sesion.py`, `holgado = medicion.evaluada.entrada_con_agua <= config.entrada`, y borrar
el comentario que justifica la desviación.

**Cómo se comprueba:** un test con un árbol cuya `entrada` cabe y cuya `entrada_con_agua` no, que
exija `exit 1` de `cosmos medir` y `rojo` de G01. Hoy no existe.

---

# GRAVES

## F06 · CONFIRMADO · El «peor caso de agua por extensión» infravalora el coste real, y su premisa es falsa

Escrito hace dos horas (`cf7e10a`). `_extensiones_de()` reduce cada glob a una «extensión» con
`p.rfind(".")`, y el resultado no es una extensión:

```
$ python3 -c "
from cosmos.medir import _extensiones_de as X
for m in [['**/*.spec.*'],['**/*.ts'],['**/*.env*'],['**/*.env'],['**/tests/**'],['**/Makefile']]:
    print(f'  {str(m):22} -> {sorted(X(m))}')"
  ['**/*.spec.*']        -> ['.*']
  ['**/*.ts']            -> ['.ts']
  ['**/*.env*']          -> ['.env*']
  ['**/*.env']           -> ['.env']
  ['**/tests/**']        -> ['*']        <-- un directorio se vuelve "universal"
  ['**/Makefile']        -> ['*']        <-- un nombre sin punto, también
```

Dos aguas que casan **el mismo fichero** acaban en grupos distintos y nunca se suman.
`app.spec.ts` casa `**/*.spec.*` y `**/*.ts`; sus «extensiones» son `.*` y `.ts`: intersección
vacía. Reproducción end-to-end sobre un árbol de dos mares (`/tmp/cosmos-esp/subcuenta`):

```
Agua que de verdad carga 'src/app.spec.ts': 482 tok [('specs', 241), ('tipado', 241)]
Agua que publica el medidor              : 241 tok [('mar/specs', 241)]
```

**El medidor publica la mitad.** En un árbol así, con el presupuesto entre los dos valores, E16 sale
verde y el coste real lo dobla.

**Y la premisa del cambio es falsa para una sesión.** El docstring dice: *«Sumar todos los mares
supone que alguien toca un .py, un .css y un .html en el mismo instante… No pasa»*. El agua se carga
por `paths:` y **se queda en el contexto el resto de la sesión**: un proyecto React + Python toca las
dos cosas en la misma sesión y paga las dos. Medido sobre la galaxia real con el matcher normativo
de E11 (no con extensiones):

```
  peor fichero individual REAL : 1.291 tok  (tests/test_x.py -> criterio, pruebas, resistencia, revision)
  lo que publica el medidor    : 1.398 tok  (criterio, custodia, pruebas, resistencia, revision)
  toda el agua condicional     : 1.499 tok  (lo que acumula una sesión que toque .py y .tsx)
```

Es decir: el modelo se equivoca **en las dos direcciones a la vez** —cobra `custodia` a un `.py` que
no la moja, y no cobra `accesibilidad` a una sesión que sí la carga— y el 1.398 publicado solo es
alcanzable por un fichero rarísimo (`db/migrations/test_x.py`), no por el razonamiento que dice
seguir.

Además la línea publicada miente sobre el conteo: `Agua condicional 1.398 tokens (5 aguas por
paths:…)`. **Hay seis.** El «5» es el tamaño del grupo ganador, no cuánta agua condicional existe.

**Arreglo:**

1. Borrar `_extensiones_de` entera. La coincidencia se decide con el matcher que ya existe y ya es
   normativo: `cosmos.validar._glob_a_regex`. El peor caso por fichero es
   `max(sondas, key=lambda f: sum(coste(n) for n in aguas if any(_glob_a_regex(p).match(f) for p in n.moja)))`,
   evaluado sobre `SONDAS_E11` más las rutas que los propios `moja` del árbol hacen alcanzables.
2. Publicar **dos** números, porque son dos preguntas distintas: `agua_por_fichero` (el máximo de
   arriba) y `agua_por_sesion` (la suma de toda el agua condicional, que es lo que se acumula). E16
   compara contra **`agua_por_sesion`**: es lo que se paga sin invocar nada, y `NUCLEO.md` §3 dice
   literalmente que el presupuesto tiene que ver «todo lo que se paga sin pedirlo».
3. Corregir la etiqueta: `({len(agua_condicional(arbol))} aguas por paths:)`.

**Cómo se comprueba:** el árbol de dos mares de `/tmp/cosmos-esp/subcuenta` (dos globs que casan
`app.spec.ts`) tiene que publicar 482, no 241. Ese es el test que falta.

---

## F07 · CONFIRMADO · Cinco sabotajes del código escrito hoy no ponen roja ni una de las 175 pruebas

Método: copia del repo, una línea cambiada, las dos suites completas.

```
CAZADO       medir._peor_agua_coincidente -> []        nucleo=FAILED (failures=2)
CAZADO       medir.agua_condicional -> []              nucleo=FAILED (failures=2)
CAZADO       E16 compara 'entrada' en vez de con_agua  nucleo=FAILED (failures=1)
CAZADO       medir: catálogo ignora el nicho           nucleo=FAILED (failures=3)
CAZADO       compilar: lock desactivado                nucleo=FAILED (failures=1)
CAZADO       sesion.es_productor_autorizado -> True    puente=FAILED (failures=3, errors=2)
CAZADO       sesion.objetivos_de_escritura -> []       puente=FAILED (failures=5, errors=2)
CAZADO       sesion.ordenes -> no segmenta             puente=FAILED (failures=2)
CAZADO       sesion._lectura_completa -> True          puente=FAILED (failures=1)
CAZADO       sesion.borrar_marcas -> no borra          puente=FAILED (failures=1)
CAZADO       sesion: G05 no redacta                    puente=FAILED (failures=1)

NO CAZADO    medir._extensiones_de -> siempre {"*"}    nucleo=OK  puente=OK
NO CAZADO    medir.FACTOR_CALIBRACION = 1.0            nucleo=OK  puente=OK
NO CAZADO    medir.MARGEN_ERROR = None                 nucleo=OK  puente=OK
NO CAZADO    validar.cobertura_total -> False          nucleo=OK  puente=OK
NO CAZADO    sesion: MAX_BYTES = 10**12                nucleo=OK  puente=OK
NO CAZADO    sesion: TOPE_AVISOS = 999                 nucleo=OK  puente=OK
```

(Guion completo: `/tmp/cosmos-esp/sab.py` y `sab2.py`; se reconstruye copiando el repo, aplicando
`str.replace` de una línea y corriendo `python3 -m unittest discover` sobre `tests` y
`puente/tests`.)

Los seis silenciosos, uno a uno:

- **`_extensiones_de` → `{"*"}`**: la función escrita hace dos horas queda reducida a «suma todo el
  agua», que es exactamente el comportamiento que el commit vino a cambiar. **Su comportamiento
  distintivo no tiene ni un test.**
- **`FACTOR_CALIBRACION = 1.0`**: se revierte la calibración entera —un 20 % de todos los números
  publicados— sin un solo rojo.
- **`MARGEN_ERROR = None`**: vuelve el `±desconocido` que `docs/CALIBRACION.md` presenta como
  cerrado, en silencio.
- **`cobertura_total → False`**: **E11 se queda ciega** y nadie se entera. Es la invariante que se
  reescribió para cerrar H08 (las cinco evasiones de glob). Sus tests solo ejercitan la rama de
  anclaje (`_sin_anclaje`), porque todos los cebos usan patrones sin caracteres alfanuméricos. El
  caso que **solo** caza `cobertura_total` no está probado:

```
$ python3 -c "
from cosmos.validar import cobertura_total, _sin_anclaje
m=['**/*.py','**/*.html','**/*.md','**/*.txt','**/*.js','**/Makefile','LICENSE','**/x','**/.gitignore']
print('sin anclaje:', [p for p in m if _sin_anclaje(p)], '| cobertura_total:', cobertura_total(m))"
sin anclaje: [] | cobertura_total: True
```

- **`MAX_BYTES` enorme**: el desvío de salidas grandes —la mitad de G05— no tiene test propio; lo que
  hay prueba `MAX_LINEAS`.
- **`TOPE_AVISOS = 999`**: `M17` de `mutaciones.py` afirma cubrir «sin tope duro el Stop es un bucle
  sin salida», pero muta la comparación, no el valor. Con el valor a 999 el bucle sin salida es real
  y la suite dice OK.

**Arreglo:** un test por cada uno, y son cortos.
`_extensiones_de`: el árbol de F06 (482 ≠ 241). `FACTOR_CALIBRACION` y `MARGEN_ERROR`: aserción de
valor contra `docs/CALIBRACION.md` más el test de F03 arreglado. `cobertura_total`: el patrón de
arriba tiene que dar E11. `MAX_BYTES`: una salida de 60 KB en una sola línea. `TOPE_AVISOS`: cuatro
`Stop` seguidos, exigir `bloquear, bloquear, bloquear, informar`. Y añadir las mutaciones
correspondientes a `puente/tests/mutaciones.py`, que hoy no toca `cosmos/medir.py` ni
`cosmos/validar.py` en absoluto.

---

## F08 · CONFIRMADO · G05 solo tapa `stdout` de Bash: `stderr`, `Read`, `Grep` y los subagentes pasan en claro

`spec/GUARDARRAILES.md` llama a G05 *«la única defensa contra una fuga hacia el contexto»*. Su
alcance real:

```
  Bash / stdout    -> TAPADO
  Bash / output    -> TAPADO
  Bash / STDERR    -> NO TAPADO   (PASA sin reescritura)
  Read  de .env    -> NO TAPADO
  Grep  resultado  -> NO TAPADO
  Task  subagente  -> NO TAPADO
```

(Reproducción: `PostToolUse` con `tool_response={"stderr": "clave=AKIA…EXAMPLE"}` y equivalentes;
guion en el cuerpo de F02, cambiando el evento.)

En `puente/sesion.py`, `_respuesta()` lee `output` y luego `stdout`, y **nunca `stderr`**; y
`despues_de_la_herramienta()` hace `if herramienta != "Bash": return PASAR`. `stderr` es
justamente donde salen las fugas típicas —`curl -v`, un `git push` con el token en la URL del
remoto, una traza con el entorno volcado—. Y como tampoco se mide, una `stderr` de 200 KB entra
entera en el contexto sin pasar por el desvío de salidas grandes.

**Arreglo:** en `_respuesta()`, concatenar `stdout` y `stderr` y devolver las dos partes redactadas
por separado (`updatedToolOutput` admite el texto completo; si el runtime distingue los canales, se
redactan los dos). Y ampliar el disparador a las herramientas de lectura: como mínimo `Read`,
`Grep`, `Glob` y `Task`, que es por donde entra texto de fichero sin pasar por un shell. Si alguna
no se puede cubrir, decirlo en la spec como límite declarado, igual que se hizo con `exit2`.

**Cómo se comprueba:** la matriz de arriba, con `TAPADO` en las seis filas o con las excepciones
escritas en `spec/GUARDARRAILES.md`.

---

## F09 · CONFIRMADO · Un `compilar.lock` rancio deja el repositorio en rojo permanente

El bloqueo se crea con `O_CREAT|O_EXCL` y se borra en un `finally`. Un `SIGKILL`, un corte de
corriente o un contenedor que se para dejan el fichero, y **no hay comprobación de PID ni de edad ni
forma de forzar**:

```
$ echo 99999 > .cosmos/compilar.lock         # pid que no existe
$ python3 -m cosmos compilar | head -3
COSMOS  compilar  rojo

otra compilación está en curso: <repo>/.cosmos/compilar.lock
```

Como `compilar` es el **único** reparador de E19, el árbol se queda rojo para siempre: `validar`
falla, el gate de pre-commit falla, G02 impide cerrar la sesión, y el mensaje no dice qué hacer.

**Arreglo:** escribir en el lock `{"pid": …, "momento": …}` y, al encontrarlo, comprobar
`os.kill(pid, 0)`; si el proceso no existe, o si el fichero tiene más de N minutos, apropiarse del
lock diciéndolo por pantalla. Y en cualquier caso, terminar el mensaje con la salida:
`si no hay ninguna compilación en curso, borra <ruta>`.

**Cómo se comprueba:** el comando de arriba tiene que compilar, avisando de que el lock estaba
huérfano.

---

## F10 · CONFIRMADO · `cosmos abrir --con-agua` devuelve TODA el agua, siempre: el filtro es inerte

`cosmos/abrir.py` (escrito durante esta auditoría) filtra el agua así:

```python
any(nicho in str(m) or "**" in str(m) for m in n.datos.get("moja", []))
```

**Todos** los `moja` reales empiezan por `**/`, así que `"**" in str(m)` es cierto siempre y la
segunda mitad del `or` hace que la primera no importe:

```
$ python3 -m cosmos abrir trading --con-agua --json | python3 -c "import sys,json;print([a['nombre'] for a in json.load(sys.stdin)['agua']])"
['mar/accesibilidad', 'mar/criterio', 'mar/custodia', 'mar/pruebas', 'mar/resistencia', 'mar/revision']
$ python3 -m cosmos abrir cumplimiento --con-agua --json | python3 -c "import sys,json;print([a['nombre'] for a in json.load(sys.stdin)['agua']])"
['mar/accesibilidad', 'mar/criterio', 'mar/custodia', 'mar/pruebas', 'mar/resistencia', 'mar/revision']
```

Idéntico para dos oficios que no comparten nada, y con el **cuerpo entero** de los seis: 1.499
tokens vertidos al contexto al abrir cualquier nodo. Es el «cargar todo lo que existe» que el
`GOAL.md` §2 declara como el problema del proyecto, en el comando cuyo docstring cita ese mismo §2.

Y el criterio, aun corregido el `or`, sería erróneo: `nicho in str(m)` es una comparación de
subcadena contra un glob —`web` casaría `**/*.webp`—, no una comprobación de alcance.

**Arreglo:** el agua no se filtra por nicho, se filtra por **los ficheros de ese nodo**. Si `abrir`
va a mostrar agua, que reciba una ruta o un patrón y use `cosmos.validar._glob_a_regex` para decidir.
Y que muestre **el nombre y el resumen**, no el cuerpo: es literalmente la regla que el propio
docstring cita dos párrafos antes («describir a los hijos es cargarlos»). El cuerpo, al invocarla.

**Cómo se comprueba:** `abrir trading --con-agua` y `abrir cumplimiento --con-agua` tienen que
devolver listas **distintas**, y ninguna debe incluir `mar/accesibilidad` para `trading`.

---

## F11 · CONFIRMADO · Un árbol COSMOS nuevo no puede llegar a verde: `generar` y `compilar` se remiten el uno al otro

`NUCLEO.md` §6 se escribió para romper este interbloqueo y solo lo rompió a medias: cada comando se
exime **de su propia** invariante, no de la del otro. En un árbol recién creado faltan las dos cosas.

```
$ cosmos validar   -> EXIT 1
  E15  arbol/COSMOS.md   índice desincronizado
       Ejecuta 'cosmos generar'; no edites el índice a mano.
  E19  .cosmos/vista     falta el manifiesto
       Ejecuta 'cosmos compilar'; no edites la vista plana a mano.

$ cosmos generar   -> EXIT 1
  E19  ... Ejecuta 'cosmos compilar'

$ cosmos compilar  -> EXIT 1
  E15  ... Ejecuta 'cosmos generar'
```

(Árbol mínimo reproducible en `/tmp/cosmos-esp/nuevo`: una galaxia, un sistema solar, un pueblo.)

La salida está en `cosmos arrancar`, que compila omitiendo `{"E15","E19"}` y luego dice «regenéralo
con cosmos generar». Pero: no aparece en la tabla de `NUCLEO.md` §6, ninguno de los dos mensajes de
error lo menciona, y su propia ayuda promete lo que no cumple —«deja un clon recién bajado en
verde»— porque sobre un árbol nuevo termina en `COSMOS arrancar rojo` con `exit 1`.

El clon de **este** repositorio sí se recupera, porque `galaxia/COSMOS.md` está versionado y al día:
`git clone && cosmos compilar` lo deja verde en 0 errores (comprobado). El agujero es para el caso
que `GOAL.md` §1 vende: «un repo que se puede clonar **sobre cualquier proyecto**».

**Arreglo:** o `generar` se exime también de E19 (no lo toca, así que no puede repararlo ni
romperlo), o los dos mensajes cambian a `Ejecuta 'cosmos arrancar' y luego 'cosmos generar'`, o
`arrancar` encadena `compilar → generar → compilar → validar`, que es lo único que deja un árbol
nuevo verde de una vez. Lo primero es lo correcto y son dos caracteres:

```python
# cli.py, comando generar
omitir_codigos=frozenset({"E15", "E19"}) | saltados     # en el previo, no en el posterior
```

Y actualizar la tabla de `NUCLEO.md` §6 con la fila de `arrancar`.

**Cómo se comprueba:** sobre el árbol nuevo, `cosmos generar && cosmos compilar && cosmos validar`
tiene que acabar en `verde`.

---

# MEDIOS

## F12 · CONFIRMADO · El parte del último commit atribuye a un cambio de medida una subida que causó su propio contenido

`registro/commits/universo/2026/09/rescate-skills.md:107` dice:

> *«El resto es el commit `cf7e10a` … que cambió cómo se mide el agua condicional: **pasó de 961 a
> 1.398 tokens sin que se añadiera un solo nodo**.»*

Las tres partes son falsas. Medido sobre el árbol de `cf7e10a^` extraído con `git archive`:

```
$ cd /tmp/cosmos-esp/prev && python3 -m cosmos medir | grep Agua
  Agua condicional  961 tokens   (5 aguas por paths:, fuera de la entrada)
$ ls galaxia/agua/mar-*.md | wc -l
       5
```

y en `cf7e10a`: **6 mares**. Ese commit añadió `mar-revision` (236 tokens) y lecciones a los otros
cinco — «un solo nodo» y varios cuerpos. Su propio mensaje de commit lo dice al revés y bien:
*«Medido: 1.499 -> 1.398 tokens»*. Es decir, **la medida bajó 101 tokens**; lo que subió 437 fue el
contenido que el mismo commit metió.

Efecto: quien lea el parte creerá que el margen se estrechó por un cambio de método y no por haber
gastado presupuesto, que es lo contrario de lo que pasó.

**Arreglo:** corregir esas dos frases con los números de arriba. Y, ya que el propio `GOAL.md` §1
dice que «un número copiado a mano envejece en silencio», que los partes citen el bloque de
`cosmos medir` **con el hash del commit al que corresponde** en la misma línea.

## F13 · CONFIRMADO · `GOAL.md`, que es normativo, sigue diciendo 20 oficios contra los 21 del árbol

```
$ grep -n "20 oficios\|los 20 de" GOAL.md
18:Y encima de ese esqueleto, **un universo de 20 oficios**, cada uno lleno de lo mejor que exista hoy
96:| **Sistema solar** | Un oficio por el que te contratan (los 20 de `spec/UNIVERSO.md`) | Planetas |
$ head -1 spec/UNIVERSO.md
# El universo — 21 oficios
$ grep -rc "^cosmos: sistema-solar$" galaxia/sistemas/*.md | awk -F: '{s+=$2} END {print s}'
21
```

`GOAL.md` §0 dice: *«Si algo del repo contradice este fichero, gana este fichero»*. Aplicando su
propia regla, el oficio 21 es ilegal. La revisión anterior arregló `UNIVERSO.md` (H10) y dejó
`GOAL.md` sin tocar. **Arreglo:** las dos líneas a 21, o una frase que fije que el número lo dicta
`spec/UNIVERSO.md` y `GOAL.md` no lo repite. Lo segundo es mejor: un número menos que mantener.

## F14 · CONFIRMADO · «E00-E19» en la ayuda y en el README, con E20 existiendo — y ya estaba anotado

```
$ grep -n "E00-E19\|E00–E19" cosmos/cli.py README.md
cosmos/cli.py:56:    validar = base("validar", "comprueba las invariantes E00-E19")
README.md:72:| `cosmos validar` | E00–E19. Esquema, estructura, duplicación, presupuesto y artefactos …
$ python3 -c "from cosmos.validar import COMPROBACIONES; print(len(COMPROBACIONES))"
20
```

Lo llamativo: `registro/commits/universo/2026/09/fix-h20-niveles.md:221` **ya lo señala**
(«`cosmos/cli.py` dice “comprueba las invariantes E00-E19” y ya existe E20») y sigue ahí. Un
hallazgo escrito y no cerrado es peor que uno no encontrado. **Arreglo:** `E00–E20` en los dos
sitios, o generar la cadena desde `COMPROBACIONES` para que no se pueda desincronizar.

## F15 · CONFIRMADO · `mar/revision` existe en el árbol y no está en ninguna spec

`spec/UNIVERSO.md` (líneas 64-70) documenta cinco mares: `criterio`, `pruebas`, `resistencia`,
`accesibilidad`, `custodia`. `ls galaxia/agua/mar-*.md` devuelve **seis**: falta `revision`, que
además es el tercero más caro (236 tokens) y entra en el peor caso de agua. `grep` en `spec/`,
`GOAL.md` y `README.md` no lo menciona. **Arreglo:** su fila en la tabla de `spec/UNIVERSO.md`.

## F16 · CONFIRMADO · El índice se escribe sin atomicidad ni bloqueo; el manifiesto sí los tiene

`NUCLEO.md` §7 exige escritura atómica del manifiesto porque «un manifiesto truncado es peor que
ninguno». El argumento vale igual —o más— para el índice, que **es** el contexto de entrada:

```python
# cosmos/generar.py:50
destino.write_text(contenido, encoding="utf-8")     # ni temporal, ni os.replace, ni lock
```

frente a `cosmos/compilar.py:164` (`mkstemp` + `fsync` + `os.replace`). Y `generar` no toma el
`compilar.lock` ni ninguno propio, así que dos `generar` simultáneos se entrelazan. El daño es
detectable (E15 lo canta) pero deja el árbol rojo hasta que alguien lo regenere, y G03 impide
arreglarlo a mano. **Arreglo:** reutilizar `_escribir_atomico` de `compilar.py` (moverla a
`cosmos/modelo.py`, que ya la comparten los dos) y tomar el mismo lock.

## F17 · CONFIRMADO · Tres veredictos de presupuesto distintos sobre el mismo árbol

| Quién | Qué compara | Fuente |
|---|---|---|
| `E16` (validar, el gate) | `peor.entrada_con_agua` | `validar.py:444` |
| `cosmos medir` (salida y `exit`) | `evaluada.entrada` para el código; `evaluada.entrada_con_agua` para el texto | `cli.py:361`, `medir.py:formatear_casos` |
| `G01`/`G02` (sesión) | `evaluada.entrada` | `sesion.py:revisar_arbol` |

Y `evaluada` es **el nicho activo**, no el peor, cuando `[nichos] activos` no está vacío:

```
$ sed -i '' 's/^activos = \[\]/activos = ["web"]/' cosmos.toml && python3 -m cosmos medir | grep -E "Nicho|Presupuesto"
  Nicho activo .... 2.277 tokens   (web; 17 pueblos)
  Presupuesto ..... 4.000     OK, quedan 325 tokens en el nicho activo con agua
```

`quedan 325` frente al `quedan 119` que vigila E16. Ninguno está mal por separado; el problema es
que se publican con la misma etiqueta. **Arreglo:** un único `veredicto_de_presupuesto(resumen,
config) -> (bool, str)` en `medir.py`, que compare siempre `peor.entrada_con_agua`, y que los tres
llamantes usen. El nicho activo se sigue mostrando, etiquetado como informativo.

## F18 · PLAUSIBLE · Una lectura truncada por el límite por defecto cuenta como lectura completa (G04)

`_lectura_completa()` devuelve `True` cuando `limit` es `None` o `""`. Si el runtime aplica un
límite por defecto (Claude Code lee 2.000 líneas si no se le pide otra cosa) sin ponerlo en
`tool_input`, un fichero de 5.000 líneas se marca como leído entero habiendo entrado un 40 %. El
docstring afirma lo contrario: *«Una lectura parcial no es una lectura: el trozo que falta es justo
el que importa»*. Lo etiqueto como **plausible** porque depende de si el runtime rellena `limit`, y
no puedo observarlo desde aquí. **Arreglo, y no cuesta nada:** exigir que el fichero tenga menos
líneas que el límite por defecto del runtime, configurable en `[sesion] lineas_por_lectura = 2000`,
y tratar la ausencia de `limit` como «leyó como mucho ese número».

## F19 · CONFIRMADO · Los guards de sesión enmudecen desde cualquier subdirectorio, y fallan abiertos ante cualquier error

`decidir()` busca `cosmos.toml` en `Path(entrada["cwd"]) / "cosmos.toml"`; si no está, lanza
`ErrorSesion` y `main()` devuelve 0 sin decir nada. Es decir: **con el `cwd` del evento en un
subdirectorio, los cinco guards están apagados** y nada lo indica. Lo mismo con cualquier
`OSError`/`ValueError`/`RecursionError`: `main()` los captura todos y devuelve 0.

Fallar abierto es defendible para G05 (no romper la herramienta que vigila); no lo es para G03, cuyo
único trabajo es denegar. Y el silencio total es lo peor de los dos mundos: un guard que no está no
se distingue de uno que aprobó.

**Arreglo:** buscar `cosmos.toml` **subiendo** desde `cwd` hasta la raíz del repositorio (como hace
`git`), y separar el manejo de errores por guard: G03 y G04 fallan **cerrados** (deny con el motivo
«el guard no pudo evaluar»), G01/G02/G05 fallan abiertos pero escriben una línea en
`.cosmos/cierres.log`. Un fallo silencioso de un guardarraíl es indistinguible de su ausencia.

## F20 · CONFIRMADO · 38 fichas apuntan a `cosecha/<script>` y ninguna lleva el guion dentro

```
$ grep -rlo "cosecha/" galaxia/pueblos/*/SKILL.md | wc -l
      38
$ c=0; for f in $(grep -rlo "cosecha/" galaxia/pueblos/*/SKILL.md); do [ $(ls $(dirname $f)|wc -l) -gt 1 ] && c=$((c+1)); done; echo $c
0
$ ls .cosmos/vista-galaxia/alcance-y-excepcion/
SKILL.md
$ grep -c cosecha puente/proyectar.py
0
```

Nueve pueblos sí traen su `scripts/` (los del último rescate), y el parte
`registro/commits/universo/2026/09/rescate-skills.md` lo generaliza a «cada skill compilada». Para
los otros 38 la ruta es **relativa a la raíz de COSMOS**, `compilar` no la copia y `proyectar` no
lleva `cosecha/` a ninguna parte: en un proyecto proyectado, esas 38 skills nombran ficheros que no
existen. Es el resto sin cerrar de H05 (9 de 38 hechos).

**Arreglo:** o cada ficha lleva su guion dentro de su directorio (como los nueve), o
`puente/proyectar.py` copia `cosecha/` al destino y las fichas la nombran desde ahí, o las rutas se
declaran absolutas respecto a una variable (`$COSMOS_RAIZ/cosecha/…`) que el proyectado defina. Lo
primero es lo que ya funciona. **Cómo se comprueba:** una invariante nueva —o E18 ampliada— que
exija que toda ruta `cosecha/…` citada por un pueblo exista **dentro** de su directorio.

## F21 · CONFIRMADO · E17 no caza el caso que la spec usa para justificarla

`spec/GUARDARRAILES.md` motiva E17 así: *«nadie copia y pega dos veces la misma política. Se
reescribe con otras palabras, en otro sitio, meses después»*. Medido con su propia función:

```
  1.000  SALTA  copia literal
  0.500  SALTA  paráfrasis leve  (comunes: copia, nunca, seguridad)
  0.455  SALTA  el caso H13-3 real (casi literal)
  0.000  PASA   "Antes de tocar produccion se deja escrito el camino de vuelta."
              vs "No se modifica un entorno vivo sin haber redactado antes como deshacerlo."
  0.000  PASA   "Los secretos jamas se escriben en claro dentro del repositorio."
              vs "Las credenciales nunca van sin cifrar en el codigo versionado."
```

Los dos que pasan son **la misma política dicha con otro vocabulario**, que es literalmente la
descripción que la spec da del problema. E17 caza la mitad fácil. La limitación está declarada
(«E17 caza la paráfrasis, no la reformulación total»), así que **no es un fallo oculto**; el fallo es
que la spec presenta como resuelto el caso que su propia limitación excluye. **Arreglo:** reescribir
ese párrafo para que el ejemplo motivador sea uno que E17 sí caza, y mover el caso del vocabulario
distinto a la lista de límites declarados.

## F22 · CONFIRMADO · `abrir` empareja la estrella por nombre suelto, reabriendo la ambigüedad que NUCLEO §1 cerró

```python
# cosmos/abrir.py
n.datos.get("ilumina") in {nodo.referencia, nodo.nombre}
```

`NUCLEO.md` §1 establece que `ilumina` contiene **la ruta completa** justamente para que dos nodos
con el mismo nombre bajo padres distintos no se confundan. Aceptar `nodo.nombre` reintroduce la
colisión por la puerta de atrás: una estrella que ilumina `calidad` se engancharía a cualquier
`.../calidad` del árbol. Hoy no muerde porque no hay colisiones de nombre entre iluminados, pero es
exactamente la premisa cuya pérdida `NUCLEO.md` §1 dice vigilar con un canario. **Arreglo:** dejar
solo `nodo.referencia`. Si se quiere la comodidad de escribir el nombre, que la resuelva
`resolver()` —que ya trata la ambigüedad como error— antes de comparar.

## F23 · CONFIRMADO · La descarga del 98,4 % incluye en el denominador los partes de commit del propio COSMOS

`resto` suma el cuerpo de todo nodo no-océano, y `[raiz] registro = "registro"` mete los partes en
el árbol:

```
$ python3 -c "…censo por nivel…"
  pueblo    n=247  tokens=131221
  lluvia    n=  7  tokens= 17263      <-- 11 % del 'universo'
  estrella  n= 21  tokens=  3158
```

Esos 17.263 tokens son informes de commit del propio proyecto. No son contexto que un agente cargue
al trabajar: son la historia de COSMOS. Contarlos infla la descarga (98,42 % con ellos, 98,24 % sin
ellos). El efecto es pequeño —dos décimas— pero la métrica principal del proyecto está medida contra
un universo que incluye su propia documentación interna, y eso crece sin techo: cada parte nuevo
mejora la descarga sin que el sistema descargue nada. **Arreglo:** que `resto` excluya los niveles
que nunca se cargan solos ni por invocación de trabajo (`lluvia` del registro), o que
`ResultadoMedicion` publique `universo` y `universo_de_trabajo` por separado. Y decir en
`spec/MEDIDOR.md` cuál de los dos es el que se cita.

## F24 · CONFIRMADO · Queda un dato personal en la historia de Git, y un desajuste de formato en las fichas

- **Identidad**: 1 de los 36 commits lleva una identidad de autor con nombre de usuario y de máquina;
  los otros 35 ya usan una identidad neutra. Es el resto de H18 y `GOAL.md` §5 lo prohíbe. No lo
  transcribo: se ve con `git log --all --format='%ae' | sort -u`. **Arreglo:** `git filter-repo
  --mailmap` antes de publicar, o asumirlo por escrito en `GOAL.md` §5. Las rutas absolutas del
  usuario **sí** están limpias (`git grep -lI "/Users/[a-z]"` → 0 ficheros) y el escáner de secretos
  pasa en verde.
- **Formato de ficha**: conviven dos convenciones en el mismo corpus —`· MIT · 3.968★ · último push`
  frente a ` - MIT - 3.968 estrellas - ultimo push`— y **30 fichas no traen URL** (las de herramienta
  propia, que citan `cosecha/…`, ver F20). Ninguna invariante mira el cuerpo de un pueblo, así que el
  «contrato completo» que anuncia el commit `3799944` no es verificable. **Arreglo:** una invariante
  E21 sobre el cuerpo de `pueblo`: o una URL con licencia, estrellas y fecha de push, o una ruta
  `cosecha/…` que exista dentro del directorio de la skill (F20). Con eso el contrato deja de ser una
  costumbre.

---

# Lo que intenté y aguantó

Esto es lo que da valor al resto. Cada línea es un intento real de tumbar algo, con lo que hice.

**El contenido de las fichas — aguanta, y es lo mejor del repositorio.** Cogí seis pueblos al azar
con semilla fija (`random.seed(20260902)`: `statsforecast`, `evidence`, `xlsxwriter`, `hftbacktest`,
`streamlit`, `scipy`) más el que la revisión anterior citaba (`a11y-auditoria-wcag`), y contrasté
**cada afirmación** contra la API de GitHub y contra PyPI/npm:

```
Nixtla/statsforecast          http=200 stars=4894  lic=Apache-2.0   push=2026-09-01   (ficha: 4.892, Apache-2.0, 2026-09-01)
evidence-dev/evidence         http=200 stars=6902  lic=MIT          push=2026-09-01   (ficha: 6.898, MIT, 2026-08-31)
jmcnamara/XlsxWriter          http=200 stars=3968  lic=BSD-2-Clause  push=2026-08-04   (ficha: 3.968, BSD-2-Clause, 2026-08-04)
nkaz001/hftbacktest           http=200 stars=4579  lic=MIT          push=2025-12-23   (ficha: 4.574, MIT, 2025-12-23)
streamlit/streamlit           http=200 stars=45661 lic=Apache-2.0   push=2026-09-02   (ficha: 45.655, Apache-2.0, 2026-09-01)
scipy/scipy                   http=200 stars=14981 lic=BSD-3-Clause push=2026-09-02   (ficha: 14.976, BSD-3-Clause, 2026-09-01)
masuP9/a11y-specialist-skills http=200 stars=56    lic=MIT          push=2026-06-13   (ficha: 56, MIT, 2026-06-13)

pypi statsforecast 200 · XlsxWriter 200 · hftbacktest 200 · streamlit 200 · scipy 200 · duckdb 200
npm  @a11y-skills/audit 200 (latest 0.5.0) · degit 200 · skills 200 (latest 1.5.23)
gh   evidence-dev/template 200
```

**Siete de siete repositorios existen. Siete de siete licencias exactas. Siete de siete fechas de
push exactas. Estrellas dentro de ±6 (un día de deriva). Ocho de ocho paquetes de instalación
existen.** Busqué específicamente el fallo que la revisión anterior cazó —un comando de instalación
inventado— y no hay ninguno. Esta parte del trabajo es sólida y hay que decirlo.

**`compilar` en paralelo — aguanta.** Lancé dos compilaciones simultáneas sobre un clon con la vista
borrada: `A=0` (verde, 247 creadas), `B=1` (`otra compilación está en curso`), y `cosmos validar`
después en `verde 0 errores`. Repetí buscando corrupción del manifiesto y no la hay: el
`O_CREAT|O_EXCL` funciona para el caso honesto. Lo que no resiste es el lock huérfano (F09), que es
otra cosa.

**Casos degradados — aguantan, sin una sola excepción no controlada.** Diez árboles construidos para
romperlo, cuatro comandos cada uno (`validar`, `medir`, `estado`, `mapa`): árbol vacío, solo galaxia,
oficio sin herramientas, nombre con acentos (`telefonía`), resumen de un carácter, pueblo huérfano,
*frontmatter* roto, cuerpo de 1,6 MB, nombre en mayúsculas, y un ciclo declarado por ruta
(`a` → `a/b` → `a`). **Cero *tracebacks*.** El ciclo lo cazan E02/E06 antes de que importe, que es
justo lo que `NUCLEO.md` §1 predice al retirar E04. Y con `chmod 000` sobre un nodo, el cargador
dice `E00 … no se puede leer: [Errno 13]` en vez de reventar.

**El nicho activo en configuración (H09) — cerrado de verdad.** Puse `[nichos] activos = ["web"]`,
compilé y validé **sin repetir ningún flag**: `compilar verde`, `validar verde 0 errores`,
`Nicho activo 2.277 tokens (web; 17 pueblos)`. E16, además, **no** se deja engañar por ese ajuste:
`_comprobar_e16` llama a `medir_casos(...)` sin nichos y usa `casos.peor`, así que seleccionar un
oficio barato no relaja el presupuesto. Lo intenté a propósito y no cede.

**Las 18 mutaciones — 18/18 en rojo**, ejecutadas sobre una copia en `/tmp` (nunca sobre el árbol
vivo, por H23, que sigue sin arreglarse: `mutaciones.py` escribe en `RAIZ` y restaura en un
`finally`). Incluidas las nueve nuevas de `sesion.py` (M9–M17) y la de `desenganchar` byte a byte
(M18). Ese trozo está bien hecho.

**El escáner de secretos y el gate — verdes.** `python3 -m puente.secretos --todo` → `exit 0`,
`secretos: limpio`. `python3 -m puente.gate --sin-pruebas` → `exit 0`, `COSMOS verde 0 errores`,
`COSMOS arrancar verde`. H01, H03 y H06 de la revisión anterior están cerrados: `.cosmos/` y
`.claude/skills/` están en `.gitignore`, no hay artefactos generados versionados, y un clon limpio
llega a verde con `cosmos compilar` (`git status --porcelain` = 0 después).

**E08 y E11, reescritas tras la revisión anterior — aguantan en su cara visible.** La lista de
vacías de E08 pasó de 5 a 152 palabras y los cuatro cebos de H16 caen ahora los cuatro. E11 caza las
cinco escrituras de H08 y también el caso duro con anclaje que construí a mano (nueve globs que
cubren las doce sondas). Lo que sí encontré es que su rama de cobertura **no tiene test** (F07).

**Doble conteo en `contexto_inicial` — no está.** Volví a buscar el fallo B2/H3 sobre el árbol de
hoy, bloque a bloque: el catálogo excluye galaxia, sistemas solares y océanos, y ningún cuerpo de
nodo no-océano aparece dentro de la cadena de entrada. `entrada + resto = universo` cuadra al token
(2.483 + 155.554 = 158.037) y `descarga ∈ [0,1]` en los diez árboles degradados.

**Herramientas repetidas — no hay.** 247 nombres, 0 duplicados. Y la puerta trasera de H15 (meter
herramientas dentro de un mar para que no paguen catálogo) sigue abierta como diseño, pero no la
usaron para colar nada nuevo.

---

# Qué arreglaría, y en qué orden

1. **F01 + F03** — la calibración. Es un solo problema: el número que decide todo se midió con un
   corpus que no contiene lo que se mide, y la prueba que lo vigilaba está dormida. Hasta que esto
   se cierre, **todos** los números publicados del proyecto están un 16 % bajos y el árbol está en
   rojo sin saberlo.
2. **F02 + F08** — los dos guards que sí tienen enemigo. G03 se salta con siete formas triviales de
   shell y G05 no mira `stderr`. Un guardarraíl que se esquiva con `&>` tranquiliza sin proteger,
   que es peor que no tenerlo.
3. **F04 + F05 + F17** — las tres son la misma enfermedad: **dos verdades distintas del mismo
   árbol**. Una válvula que abre dos guards, un `exit 0` que contradice su propio texto, y tres
   comparaciones de presupuesto. Se arregla con una función única de veredicto y sacando G04 de
   detrás de G05.
4. **F06 + F07** — el peor caso de agua. El código de hace dos horas está mal *y* su comportamiento
   distintivo no tiene ni una prueba. Los seis sabotajes silenciosos de F07 son la lista literal de
   tests que faltan.
5. **F09 + F11** — los dos atascos operativos: el lock huérfano y el interbloqueo
   `generar`↔`compilar`. Los dos dejan el sistema en rojo sin salida escrita, y los dos se arreglan
   con menos de diez líneas.
6. **F10 + F20 + F24** — el contenido: el filtro inerte de `abrir`, las 38 rutas que no viajan, y la
   ausencia de invariante sobre el cuerpo de un pueblo. Lo que no se valida, se desalinea; ya pasó
   con `UNIVERSO.md` y con `QUEDA.md`.
7. **F12 a F16, F21 a F23** — coherencia y prosa. Baratos, y son los que hacen que el siguiente que
   lea el repositorio se crea lo que pone.

---

*Revisión hecha con premisa invertida: 11 formas de shell probadas contra G03 y verificadas después
en `bash`, 17 sabotajes de una línea sobre copias con las dos suites completas, 18 mutaciones
ejecutadas, 10 árboles degradados construidos a propósito, 2 árboles sintéticos para aislar el
medidor, un `venv` temporal con `tiktoken` para recalcular todos los números publicados contra un
tokenizador real, dos compilaciones en paralelo, un clon limpio, un árbol nuevo desde cero, y 7
repositorios y 8 paquetes contrastados contra sus registros. Todo lo destructivo, en
`/tmp/cosmos-esp/`; el repositorio no se modificó salvo este fichero.*
