# D — Robustez del código: el paquete `cosmos/` como software

Auditoría 360 de COSMOS · revisor D · 2026-09-03
Ángulo exclusivo: **el código como ingeniería**, no como idea. Premisa de partida: *esto se rompe
con la primera entrada rara*. Lo que sigue es lo que aguantó y lo que no, ejecutado.

---

## Cabecera: pin, entorno y método

**Estado del árbol auditado** (fijado al empezar y comprobado al terminar; idéntico):

```
$ git -C ~/cosmos rev-parse HEAD
b0c1ebdeb2d9bac7e068d10714213ff2f9eda926

$ git -C ~/cosmos status --porcelain | wc -l
0          # al empezar
1          # al terminar, y es `?? progress/auditoria-360-2026-09-03/` (informes de otros revisores)

$ git -C ~/cosmos status --porcelain -- cosmos/ tests/ spec/ | wc -l
0          # no he tocado una sola línea del objeto auditado
```

SHA-256 (12 primeros) de los módulos sobre los que se afirma algo, para que este informe se pueda
reconciliar si el árbol muta:

```
8625eb7add08  cosmos/abrir.py      beb238e82f62  cosmos/acertar.py    51f1a03ada18  cosmos/buscar.py
cc34168c94fe  cosmos/cli.py        c494e0501842  cosmos/compilar.py   ded783aa96dc  cosmos/estado.py
3ccce754302d  cosmos/generar.py    635bc4a1d895  cosmos/guardarrailes.py  af3655938f6f  cosmos/juez.py
72addb219a26  cosmos/medir.py      7bc369295be4  cosmos/modelo.py     6d70989f9293  cosmos/validar.py
```

Referencio **por símbolo**, nunca por `fichero:línea`.

**Entorno exacto:**

```
$ command -v python3   ->  /usr/local/bin/python3
$ python3 -VV          ->  Python 3.14.3 (v3.14.3:323c59a5e34, Feb 3 2026) [Clang 16.0.0] arm64
$ ls -d ~/cosmos/.venv ~/cosmos/venv   ->  no existe ninguno: el repo NO trae venv
$ python3 -c "import tiktoken"         ->  ModuleNotFoundError (ver D-08)
$ ls /tmp/calib/bin/python             ->  No such file or directory (ver D-08)
```

**No hay venv en el repo**, así que el intérprete correcto *es* `python3` del sistema — lo digo
explícitamente porque la regla de la casa exige nombrarlo y aquí la respuesta honesta es «no hay
otro». Máquina: M3 Pro. **Aviso de honestidad sobre los relojes:** durante la auditoría había otros
revisores de esta misma tanda ejecutando en `~/cosmos` en paralelo. Por eso las afirmaciones de
complejidad de D-01 y D-06 se sostienen sobre **conteo de llamadas**, que es inmune a la contención,
y los segundos se publican como dato secundario y con la contención declarada.

**Método:** solo lectura sobre el repo. Todo experimento corre sobre árboles sintéticos construidos
en mi scratchpad (`.../scratchpad/casos/` y `.../scratchpad/escala/`) con dos generadores propios
(`construir.py`, `generar.py`). Los códigos de salida se capturan **sin tuberías** (`subprocess.run`
devuelve el código del propio proceso; una tubería devolvería el del último comando y mentiría).
`timeout`/`gtimeout` no existen en este Mac, así que los límites de tiempo los pone Python.

---

## Resumen

| | |
|---|---|
| **Hallazgos** | 11 (**3 críticos**, 5 medios, 3 bajos) |
| **Mejoras propuestas** | 6 |
| Casos límite ejecutados | 22 árboles × 7 verbos = 154 ejecuciones |
| Suite | `Ran 259 tests — OK (skipped=2)` en 79 s aislada; **falla 2 de 7 veces bajo carga** (D-02) |
| Cuelgues, tracebacks o pánicos | **0** |

El veredicto corto: **el manejo de errores es genuinamente sólido** —22 entradas raras y ni un solo
traceback, ni un cuelgue, ni un código de salida incoherente— y **la escalabilidad no lo es**. El
producto se vende sobre «el universo puede crecer sin límite mientras el coste de entrada no se
mueve». El *coste de entrada* cumple. El **coste de la herramienta que lo comprueba** crece a
`O(n³)` y a 8× la galaxia actual `cosmos validar` tarda diez minutos.

---

# Hallazgos

## D-01 · CRÍTICO · `medir_casos` es cúbico: 0,07 s una medición, 589 s todas

**Qué es.** `medir_casos` mide el caso base y **una vez por cada nicho**. Cada `medir_arbol` con
nichos llama a `nicho_de_nodo` por nodo, y `nicho_de_nodo` reconstruye el conjunto entero de nichos
en cada llamada (`candidato in set(nombres_nichos(arbol))`), que a su vez recorre y ordena todos los
nodos. Nichos ∝ nodos ⇒ **O(n³ log n)**.

Y no es un rincón: `_comprobar_e16` llama a `medir_casos`, así que **cada `cosmos validar` lo paga**.

**Prueba por conteo de llamadas** (inmune a la contención). Árboles sintéticos con la forma exacta
de `galaxia/` (proporciones reales: 22 sistema-solar, 8 continente, 76 país, 247 pueblo, 22
estrella, 5 océano, 6 mar, 17 río), escalados ×1/×2/×5:

```
$ python3 <scratchpad>/escala/generar.py 1 2 5 10
$ python3 <scratchpad>/escala/contar.py x1 x2 x5

arbol   nodos verbo        seg     nombres_nichos    nicho_de_nodo   solape_de_afirmaciones  _afirmaciones
x1        404 validar     1.41             12,761           12,716                      528          1,056
x2        802 validar     7.19             50,953           50,864                    1,830          3,660
x5       1996 validar    99.03            318,121          317,900                   10,440         20,880
```

Los cocientes cierran la aritmética sin margen de duda:

| | nodos ×  | `nombres_nichos` × | cuadrado esperado |
|---|---:|---:|---:|
| x1→x2 | 1,985 | **3,993** | 3,94 |
| x1→x5 | 4,941 | **24,93** | 24,41 |

Cuadrático en **llamadas**, y cada llamada es `O(n)` por dentro ⇒ trabajo cúbico. El reloj lo
acompaña: 1,41 s → 7,19 s → **99,03 s** para validar un árbol de 1.996 nodos (4× la galaxia real).

**El aislamiento del culpable**, en x10 (3.986 nodos ≈ 8× la galaxia real):

```
$ cd ~/cosmos && python3 -u -c '...'      # script completo en el scratchpad
cargar_arbol   3986 nodos      0.91 s
buscar                         2.15 s
medir_arbol (1 vez)            0.07 s     <-- una medición: instantánea
medir_casos (todos nichos)   589.16 s     <-- las 221 mediciones: DIEZ MINUTOS
```

`medir_arbol(nichos=None)` tarda 0,07 s porque el `and seleccion is not None` **cortocircuita antes
de llamar a `nicho_de_nodo`**. En cuanto hay una selección, se llama por nodo y explota. El coste no
está en medir: está en reconstruir 318.000 veces un conjunto que no cambia.

**Fix concreto, y medido.** Memoizar `nombres_nichos` por árbol (o, mejor, calcular el conjunto una
vez en `medir_casos`/`nodos_de_catalogo` y pasarlo). Lo he aplicado por parcheo en memoria —sin
tocar el repo— sobre el mismo x10:

```
ANTES   medir_casos    579.13 s
DESPUES medir_casos     19.29 s   -> 30x mas rapido

¿mismo resultado? peor_nicho: True | entrada peor: True | universo: True
  peor_nicho=oficio-00000  entrada=10698  universo=418665
```

**30× con resultado idéntico**, bit a bit, en las tres cifras que deciden. Los 19 s que quedan son
la cuadrática restante (re-medir el árbol entero una vez por nicho); si además se cachea el
`detalle_arbol` —que no depende del nicho— baja otro orden de magnitud.

**Riesgo.** `GOAL §1` vende clonar COSMOS sobre cualquier proyecto, y `test_escala.py` sitúa el
techo de diseño en ~150 oficios. A 220 oficios la herramienta que vigila el presupuesto tarda diez
minutos, y está enganchada al **pre-commit** (`puente/gate.py`) y a los guardarraíles de sesión. Un
gate de diez minutos se desinstala el primer viernes, y con él se va la invariante entera. Es el
modo de fallo que el propio repositorio documenta como «una puerta sin salida se rodea».

---

## D-02 · CRÍTICO · Los tests escriben en el repositorio real y filtran estado; reproducible al 100 %

**Qué es.** `tests/test_toda_puerta_tiene_salida.py` (clase `LasDosPuertasDelPresupuestoAbrenIgual`)
usa dos rutas fijas **dentro del repo real**, no en un `tmpdir`:

- `RAIZ / ".estrecho-de-prueba.toml"` (con `RAIZ = Path(__file__).resolve().parent.parent`)
- `ruta_saltos(RAIZ)` → `~/cosmos/.cosmos/saltos.log`, el **registro real de la válvula de escape**

`test_con_el_salto_abierto_no_para_y_lo_dice` registra un salto **E16** vivo un minuto y lo restaura
en un `finally` leyendo/reescribiendo el fichero entero. Dos procesos a la vez ⇒ el restore de uno
pisa el del otro.

**Reproducción determinista** (falla siempre, en las dos corridas):

```
$ cd ~/cosmos
$ python3 -m unittest tests.test_toda_puerta_tiene_salida -v > A.txt 2>&1 &
$ python3 -m unittest tests.test_toda_puerta_tiene_salida -v > B.txt 2>&1 &
$ wait

corrida A EXIT=1 :: Ran 11 tests in 4.706s FAILED (failures=1)
corrida B EXIT=1 :: Ran 11 tests in 4.682s FAILED (failures=1)

FAIL: test_sin_salto_el_presupuesto_para (...LasDosPuertasDelPresupuestoAbrenIgual...)
FAIL: test_sin_salto_el_presupuesto_para (...LasDosPuertasDelPresupuestoAbrenIgual...)
```

**Y filtra de verdad.** Tras la reproducción, el registro real del repo quedó con **dos saltos E16
huérfanos** que ningún `finally` limpió:

```
$ cat ~/cosmos/.cosmos/saltos.log
{"caduca": "2026-09-03T07:56:17...", "codigo": "E16", "motivo": "prueba: la puerta del presupuesto tiene que abrir"}
{"caduca": "2026-09-03T07:58:18...", "codigo": "E16", "motivo": "prueba: la puerta del presupuesto tiene que abrir"}
```

Mientras uno de esos saltos vive, `cosmos validar` y `cosmos medir` sobre el repo real **dejan de
parar por presupuesto** y salen 0: la invariante insignia del proyecto queda suspendida por un
residuo de test. (El fichero está en `.gitignore`, así que `git status` no lo canta: se filtra en
silencio.)

**Esto también explica la intermitencia de la suite completa.** Siete corridas:

```
run 1  Ran 259 in  80.2s  OK          run 5  Ran 259 in 104.6s  OK
run 2  Ran 259 in  76.9s  OK          run 6  Ran 259 in 111.7s  FAILED (failures=1)
run 3  Ran 259 in  74.0s  OK          (+ una corrida previa de 104.9s: FAILED)
run 4  Ran 259 in  87.6s  OK
FALLOS AGREGADOS:
   1 FAIL: test_sin_salto_el_presupuesto_para
```

**Falla 2 de 7, y solo en las corridas lentas** (104,6 s y 111,7 s; nunca por debajo de 90 s): la
ventana de solape crece con la carga. Ojo con el diagnóstico fácil —el propio repo tiene una regla
sobre falsos rojos por contención de CPU—: **aquí no es un falso rojo**. El rojo es real y su causa
es el estado compartido; la carga solo cambia la probabilidad de verlo.

**Fix concreto.** (a) `_con_presupuesto_imposible` escribe su `.toml` en un `TemporaryDirectory` con
rutas absolutas al árbol real (ya las construye: solo hay que mover el destino). (b) El test del
salto apunta `ruta_saltos` a un directorio temporal —inyectando la base, que `ruta_saltos(base)` ya
parametriza— en vez de al repo. **Riesgo si no se arregla:** la suite no es fiable en CI con
paralelismo ni en una máquina cargada, y cada corrida puede dejar la válvula E16 abierta en el repo
de trabajo.

---

## D-03 · CRÍTICO · E16 convierte «no medido» en un número, y publica una frase falsa

La regla de la casa es explícita: *«no medido» jamás se convierte en cero*. `medir.Veredicto.cabe`
es **trivalente** a propósito (`True` / `False` / `None` = «no había nada que medir») y
`formatear_casos` lo respeta. `_comprobar_e16` **no**: hace `if veredicto_de_presupuesto(...).cabe:`
y `None` es *falsy*, así que un árbol vacío cae por la rama «excede».

Sobre un árbol vacío (directorio sin un solo `.md`), los dos verbos discrepan:

```
$ python3 -m cosmos medir --config <scratchpad>/casos/vacio/cosmos.toml
  Presupuesto ..... 4.000     SIN MEDIR: el árbol no aporta ni un token; un veredicto sobre nada no es un OK
EXIT=1                                        <-- correcto

$ python3 -m cosmos validar --config <scratchpad>/casos/vacio/cosmos.toml
E16  presupuesto
     peor nicho sin nichos: entrada 0 + agua condicional 0 = 0 tokens > 4000; excede en -4000 tokens; más caros:
```

La línea afirma **«0 tokens > 4000»** (falso) y **«excede en −4000 tokens»** (un exceso negativo).
No es cosmético: es exactamente el patrón que el proyecto existe para perseguir, con el agravante de
que aquí el `None` ya estaba modelado y se pierde al cruzar de módulo.

Y no es un caso de laboratorio: un árbol vacío es **COSMOS recién clonado sobre un proyecto nuevo**,
que es el escenario que `GOAL §1` vende.

**Fix.** En `_comprobar_e16`, ramificar sobre los tres valores: `cabe is True` → sin error;
`cabe is False` → el E16 actual; `cabe is None` → un error propio que diga «no hay nada que medir»
(o ningún error, si se decide que un árbol vacío no es un rojo de presupuesto), nunca la aritmética
del caso `False`. **Riesgo:** un diagnóstico auto-contradictorio enseña a desconfiar de todos los
demás.

---

## D-04 · MEDIO · Un BOM hace desaparecer un nodo en silencio, y culpa a un fichero inocente

`_cargar_desde` descarta lo que no empiece por `---`:

```python
contenido = ruta.read_text(encoding="utf-8")
...
if not contenido.startswith("---"):
    continue          # <-- sin error, sin aviso, sin registro
```

Un `.md` guardado con BOM (Windows, VS Code con `files.encoding` heredado, Excel/editores que lo
añaden) empieza por `﻿---`. **El nodo desaparece del árbol y no se emite ni un E00.**

```
$ python3 -c "print((SP/'bom-mixto/arbol/galaxia.md').read_bytes()[:6])"
b'\xef\xbb\xbf---'
read_text(utf-8)      -> startswith("---") = False   <-- el nodo se descarta EN SILENCIO
read_text(utf-8-sig)  -> startswith("---") = True    <-- el fix
```

Lo grave es el diagnóstico que produce, que apunta al sitio equivocado:

```
$ python3 -m cosmos validar --config <scratchpad>/casos/bom/cosmos.toml
E05  árbol
     se esperaba exactamente una galaxia; hay 0 (ninguna)      <-- la galaxia está ahí, en disco, válida

$ python3 -m cosmos validar --config <scratchpad>/casos/bom-mixto/cosmos.toml
E02  s.md:4
     padre inexistente: 'prueba'                               <-- culpa a s.md, que es correcto
```

Y `cosmos estado` sobre ese árbol responde `EXIT=0` con un inventario vacío.

**Fix, verificado:** `read_text(encoding="utf-8-sig")` en `_cargar_desde` — decodifica igual sin BOM
y lo consume si está. Comprobado que tras el cambio el frontmatter parsea entero:
`{'cosmos': 'galaxia', 'nombre': 'prueba', 'resumen': '...'}`. Complementario: si un `.md` bajo la
raíz no empieza por `---`, hoy se ignora por diseño (hay `.md` que no son nodos); mantenerlo, pero
**el BOM no debe ser lo que decide eso**.

---

## D-05 · MEDIO · `estado` y `mapa` dan verde sobre una raíz que no existe

`cli.ejecutar` guarda explícitamente el caso «la raíz del árbol no existe» —con un comentario que
explica por qué («medir cero nodos y publicar “OK, quedan 4.000” era el veredicto tranquilizador
sobre un árbol que no está»)— pero **solo en `medir` y en `buscar`**. Con un `cosmos.toml` cuyo
`arbol` apunta a un directorio inexistente:

```
validar  -> EXIT=1   COSMOS  rojo  4 errores        (E00 dice «la raíz del árbol no existe»)  OK
medir    -> EXIT=1   COSMOS  medir  rojo                                                      OK
estado   -> EXIT=0   COSMOS  estado                                                           <-- verde
mapa     -> EXIT=0   COSMOS mapa                                                              <-- verde
```

Y `estado` no se limita a callar: **afirma que no pasa nada** sobre un árbol que no existe.

```
  Niveles sin un solo nodo
    continente, estrella, galaxia, lago, lluvia, luna, mar, oceano, pais, planeta, ...
    (no es un fallo: son niveles que este árbol no necesita)
```

Es el arreglo a medias que el propio `acertar.formatear_contraste` documenta en su comentario
(«arreglar el que se ve y dejar al hermano una línea más abajo»): la guarda se escribió para dos
verbos de cuatro. **Fix:** subir el `if not config.arbol.is_dir()` al punto donde ya se carga el
árbol, para los cuatro. **Riesgo:** un `--config` mal escrito o un `raiz.arbol` relativo mal
resuelto produce un informe tranquilizador en vez de un rojo.

---

## D-06 · MEDIO · E17 recalcula las afirmaciones de cada nodo una vez por pareja

`_comprobar_e17` compara los co-cargables por parejas y llama a `solape_de_afirmaciones(a, b)`, que
**recalcula `_afirmaciones(a)` y `_afirmaciones(b)` en cada pareja**. Los co-cargables incluyen las
**estrellas**, que crecen 1:1 con los sólidos, así que la cuadrática es estructural.

Medido (mismos conteos que D-01):

| árbol | co-cargables | `solape_de_afirmaciones` | `_afirmaciones` | debería ser |
|---|---:|---:|---:|---:|
| x1 | 33 | 528 = C(33,2) | 1.056 | 33 |
| x2 | 61 | 1.830 = C(61,2) | 3.660 | 61 |
| x5 | 145 | 10.440 = C(145,2) | **20.880** | **145** |

A x5, las afirmaciones de cada nodo se re-parsean **144 veces** (regex + normalización Unicode +
`casefold` sobre el cuerpo entero). **Fix:** calcular `_afirmaciones` una vez por nodo antes del
doble bucle y pasar las listas — de 20.880 parseos a 145, sin tocar la semántica. Las C(n,2)
comparaciones se quedan (son el diseño de la invariante), pero pasan a ser comparaciones de
conjuntos ya construidos. **Riesgo:** hoy E17 domina el coste de `validar` en árboles con muchas
estrellas, y se paga en cada commit.

---

## D-07 · MEDIO · `generar_mapa` recorre todos los nodos por cada nodo

En `generar.generar_mapa`, `visitar()` busca los adjuntos de cada nodo escaneando la lista completa:

```python
adjuntos = sorted((n for n in arbol.nodos
                   if (n.cosmos == "estrella" and n.datos.get("ilumina") == nodo.referencia)
                   or (n.cosmos == "luna" and n.datos.get("orbita") == nodo.referencia)), key=_orden)
```

Es `O(n²)` con `n` = nodos del árbol. Ya hay un `por_padre` precalculado con `defaultdict` tres
líneas más arriba: **el patrón correcto está en la misma función**, solo falta aplicarlo a los
adjuntos. **Fix:** un `por_iluminado`/`por_orbitado` construido en una pasada. **Riesgo:** bajo hoy
(el verbo `mapa` es de inspección manual), pero es la misma clase de defecto que D-01 y sale gratis
cerrarlo.

---

## D-08 · MEDIO · El margen ±5,2 % —el número sobre el que descansa el presupuesto— no se verifica en ninguna instalación por defecto

El medidor publica `±5,2 %` y todo el presupuesto de entrada descansa en ese factor de calibración.
La prueba que lo verifica **se salta sola** cuando no hay `tiktoken`:

```
$ python3 -m unittest discover -s tests
Ran 259 tests in 79.427s
OK (skipped=2)

skipped 'SIN TOKENIZADOR: el margen publicado (±5,2 %) NO se ha verificado en esta ejecución...'
skipped 'sin tokenizador no se puede medir el veredicto exacto'
```

Y no hay ninguna vía automática de tenerlo:

- **no hay `requirements.txt`, ni `pyproject.toml`, ni `setup.py`** en el repo;
- `docs/CALIBRACION.md` indica montar un venv temporal, y el que quedó registrado
  (`/tmp/calib/bin/python`, citado en `registro/commits/universo/2026/09/*`) **no existe**
  (`ls /tmp/calib/bin/python` → *No such file or directory*), y `/tmp` se vacía al reiniciar;
- `COSMOS_EXIGE_TOKENIZADOR` —la palanca que convierte el salto en fallo— **no aparece ni en
  `.github/workflows/cosmos.yml` ni en `puente/gate.py`**: solo en el test que la lee y en la
  documentación. Grep completo sobre código y CI: cero apariciones fuera de `tests/test_medidor.py`
  y `docs/CALIBRACION.md`.

Es decir: en CI, en el pre-commit y en cualquier clon nuevo, esas dos pruebas se saltan **siempre**,
para siempre, y el verde es un verde con la calibración sin comprobar.

**Lo que está bien hecho** y hay que decirlo: el test **no miente**. Imprime un `AVISO` en la salida,
el mensaje del skip nombra el número exacto que queda sin verificar, y existe la palanca para
exigirlo. Es honestidad de manual — lo que falta es que **alguien la ejerza automáticamente**.

**Fix.** Añadir un job en CI que instale `tiktoken` en un venv desechable y corra la suite con
`COSMOS_EXIGE_TOKENIZADOR=1`, en paralelo al job sin dependencias (que debe seguir existiendo: el
«cero dependencias» es una virtud real del proyecto, ver «Lo sólido»). Así el verde por defecto
sigue sin red y, aparte, alguien comprueba el número de verdad. **Riesgo:** el factor se calibró
contra un corpus de 78 ficheros del propio repo; el árbol ha cambiado desde entonces y nadie lo
sabría.

---

## D-09 · BAJO · `formatear_medicion` y `medicion_json`: código muerto que solo mantienen sus propios tests

```
$ grep -rn "formatear_medicion\|medicion_json" --include='*.py' .
tests/test_medidor.py:193 · tests/test_medidor.py:235 · tests/test_medidor.py:310
```

**Ningún llamante de producción**: el CLI usa `formatear_casos`/`casos_json`. Y duplican:
`formatear_medicion` (39 líneas) comparte **16 líneas idénticas** con `formatear_casos`
(41 % de la primera) — cabecera de método, cálculo de descarga, bloque de detalle. Dos formateadores
para la misma cosa, uno de ellos vivo solo porque tiene tests. **Fix:** borrar los dos y sus tres
pruebas (~50 líneas). Si se quiere conservar la vista de un solo `ResultadoMedicion`, que
`formatear_casos` delegue en ella en vez de reimplementarla.

## D-10 · BAJO · Las rutas de los errores de carga mezclan absoluta y relativa

En `_cargar_desde`, el fallo de **lectura** registra `str(ruta)` (absoluta) mientras el fallo de
**parseo** registra `relativa`. En la misma salida de `cosmos validar` conviven:

```
E00  /private/tmp/.../casos/ilegible/arbol/prohibido.md      <-- lectura: absoluta
E00  anidado.md:5                                            <-- parseo: relativa
```

**Fix:** usar `relativa` en ambos (ya está calculada dos líneas más abajo; basta subirla antes del
`try`). Cosmético, pero rompe el `grep`/`awk` de quien procese la salida.

## D-11 · BAJO · Los enlaces simbólicos a ficheros de fuera del árbol se cargan como nodos

Un symlink dentro de la raíz que apunta a un `.md` **fuera** de ella se sigue y su destino entra al
árbol como nodo de pleno derecho:

```
symlink-fuera  buscar  EXIT=0  ->  1. desdefuera      # el fichero vive en ../fuera/secreto.md
```

No es explotable por sí solo y la resolución de `ruta_relativa` no se rompe, pero significa que la
frontera del árbol es porosa: lo que `cosmos.toml` declara como `raiz.arbol` no acota de verdad lo
que se mide ni lo que se aplana. **Fix:** decidirlo a propósito —y documentarlo—; si se quiere
cerrar, comprobar `ruta.resolve().is_relative_to(raiz_path)` al cargar. Los otros dos casos de
symlink **están bien resueltos** y se dicen en «Lo sólido».

---

# Mejoras, por prioridad

1. **Cerrar D-01 con la memoización medida** (30×, salida idéntica). Es un cambio de pocas líneas
   con el mayor retorno del informe. Segundo paso, si se quiere: `detalle_arbol` no depende del
   nicho — calcularlo una vez en `medir_casos` en lugar de una vez por nicho quita la cuadrática que
   queda.
2. **Aislar los tests del repo real (D-02)**, que es lo que hace la suite creíble. Mientras no se
   haga, no se puede paralelizar CI ni fiarse de un rojo en una máquina cargada.
3. **Trivalente de punta a punta (D-03).** `Veredicto.cabe` ya modela «no lo sé»; el arreglo es que
   `_comprobar_e16` deje de aplastarlo. Conviene un test que ejercite el árbol vacío en los **dos**
   verbos a la vez: hoy uno acierta y el otro no, y ninguna prueba lo cruza.
4. **Un job de CI con tokenizador (D-08)**, para que el ±5,2 % deje de ser un número sin auditor.
5. **Simplificación — donde de verdad sobra código:**
   - `formatear_medicion` + `medicion_json` + sus 3 tests: **~50 líneas fuera** (D-09).
   - `formatear_medicion` y `formatear_casos` comparten 16 líneas: extraer el cálculo de
     `metodo`/`descarga`/bloque-de-detalle a un helper deja el formateador que quede en ~35 líneas.
   - `cli.ejecutar` es una cadena de 15 `if args.comando == ...` con cuerpos de hasta 25 líneas
     dentro de un `try` gigante (≈180 líneas en una función). Un `dict[str, Callable]` de despacho
     —el patrón que `validar.COMPROBACIONES` ya usa en este mismo repo— la deja en una decena de
     líneas y hace que cada verbo se pueda probar suelto. Es la mayor deuda de legibilidad del
     paquete, y no requiere cambiar ni un comportamiento.
   - `nichos_de_configuracion` (en `cli.py`) reimplementa la lectura de un TOML que
     `cargar_configuracion` (en `modelo.py`) ya hace: dos parsers para el mismo fichero, con
     validación distinta. Unificar en `modelo`.
6. **Cerrar las dos cuadráticas baratas (D-06, D-07).** Ninguna cambia semántica y las dos son el
   mismo patrón: precalcular un índice antes del bucle en vez de rescanear dentro.

**Sobre dependencias, nada que reprochar:** el paquete importa **solo biblioteca estándar**
(`argparse, ast, collections, contextlib, csv, dataclasses, datetime, hashlib, io, json, math, os,
pathlib, re, shlex, shutil, stat, subprocess, sys, tempfile, tomllib, typing, unicodedata, urllib`),
`tiktoken` es opcional y está detrás de un `try/ImportError`, y el juez local habla por `urllib` sin
cliente HTTP de terceros. No hay nada que pinnear porque no hay nada que instalar. Eso es un acierto
de diseño, no una carencia — la única consecuencia a gestionar es D-08.

---

# Lo que está sólido

No es cortesía: son cosas que intenté romper y no se rompieron.

- **Ni un traceback, ni un cuelgue, ni un código de salida incoherente** en 154 ejecuciones sobre 22
  árboles hostiles. Todo fallo sale como mensaje formateado y un código de salida estable:
  **0** correcto · **1** rojo de la métrica/validación · **2** error de uso o configuración.
- **Casos límite que aguantan con diagnóstico explícito:** CRLF (limpio, sin un solo error espurio);
  nombres de fichero con espacios, acentos y emoji (`emoji-🚀.md` carga sin problema: la identidad
  del nodo vive en el frontmatter, no en el nombre del fichero); **acentos y emoji en el campo
  `nombre`** rechazados por E00 con la línea exacta; fichero de **10 MB** (`validar` en 0,68 s);
  **120 niveles de anidamiento** de directorios; fichero **ilegible** (`chmod 000`) → E00 «no se
  puede leer»; **bytes no-UTF8** → E00; TOML corrupto → salida 2 en los siete verbos; cinco formas
  distintas de YAML mal formado → 8 × E00 con número de línea.
- **Bucle de enlaces simbólicos: no cuelga y no duplica.** Un symlink que apunta a su propio
  ancestro se recorre en 0,08 s y el nodo aparece una sola vez. Un symlink roto se reporta como E00
  en vez de reventar.
- **macOS insensible a mayúsculas: cerrado por diseño.** `PATRON_NOMBRE = ^[a-z0-9-]+$` impide que
  dos nodos colisionen al aplanar por diferir solo en la caja; el intento (`dedup` vs `DEDUP`) muere
  en E00 antes de llegar a E18. Es la respuesta correcta y estaba prevista.
- **`medir --metodo exacto` falla explícito, no inventa.** Sin `tiktoken`: `MetodoNoDisponible`,
  salida 1, mensaje entero. Es exactamente lo que pedía el encargo y está bien resuelto.
- **El veredicto trivalente existe y `medir` lo respeta** («SIN MEDIR: un veredicto sobre nada no es
  un OK», salida 1). El defecto de D-03 es que un consumidor lo aplasta, no que falte el concepto.
- **Escritura atómica de verdad:** `escribir_atomico` usa `mkstemp` + `fsync` + `os.replace` y
  **conserva los permisos previos** (el comentario documenta el bug real de 644→600 que eso arregla).
- **El cerrojo distingue «ocupado» de «alguien murió aquí»**, guarda el PID, pregunta con `signal 0`,
  y es **explícitamente no reentrante** con un error propio (`ErrorCerrojo`) en vez de evaporar la
  exclusión en silencio. Es el manejo de cerrojos más cuidadoso que he visto en un repo de este
  tamaño.
- **`tests/test_escala.py` afirma lo medido, no lo deseado** —su propio docstring lo dice— y fija el
  punto de rotura como un **rango** (`range(100, 221)`) en vez de un número frágil. Es el patrón
  correcto. Su único punto ciego es que mide la curva de **tokens** y no la de **tiempo**, que es
  justo donde está D-01: usa `medir_arbol` (una llamada) y nunca toca `medir_casos`.
- **E04 retirada con argumento, no por comodidad.** El comentario en `validar.py` demuestra que
  ningún árbol legal puede ciclar, retira la comprobación, y **en su lugar vigila la premisa** con
  un canario más una meta-prueba que lo hace saltar. Eso es exactamente lo contrario de un test
  tautológico, y merece decirse en un informe que va a buscarlos.
- **Cero dependencias de terceros en tiempo de ejecución** y CI que comprueba el suelo de versión
  (3.11+ por `tomllib`).
- **Portabilidad: limpia.** Cero rutas absolutas de la máquina de Darío en `cosmos/` y en `puente/`
  (las únicas apariciones de `/Users/...` están en `research/` y `registro/`, ya anonimizadas como
  `/Users/<usuario>/`). Nada específico de macOS en el paquete. `/tmp/calib` **no aparece en el
  código**: solo en partes de commit y en `docs/CALIBRACION.md`, y su ausencia degrada a un skip
  honesto (D-08), no a un fallo. El producto es clonable sobre cualquier proyecto; lo que no escala
  es el tiempo de sus verbos (D-01), no su portabilidad.

---

## Nota de método sobre una afirmación que retiré

A mitad de auditoría creí haber encontrado que un salto **caducado** seguía contando como activo
(`cosmos saltar --listar` decía «ACTIVO E16, caduca en 1 d» sobre una entrada cuyo `caduca` ya había
pasado). Al ir a publicarlo con la invocación completa —como exige la regla de la casa— resultó que
yo había leído **solo la primera línea** del registro mientras `estado_saltos` usa **la última por
código**, y entre mis dos lecturas los tests concurrentes habían escrito un salto nuevo con ventana
fresca. Comprobado correctamente:

```
ahora_utc() = 2026-09-03 07:58:24
  E16  caduca=07:56:17  activo=False  dias=0
  E16  caduca=07:58:18  activo=False  dias=0
estado_saltos -> activos: [] caducados: ['E16']
```

**La lógica de caducidad es correcta y no hay hallazgo.** Lo dejo escrito porque el episodio es la
evidencia de D-02 vista desde otro ángulo: el estado compartido no solo rompe los tests, también
hace que un auditor mida mal.
