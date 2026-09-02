# El núcleo: F03, F06, F07, F11, F12, F13 y F14

Fecha: 2026-09-02 · Spec dueña: [`../../../../../spec/NUCLEO.md`](../../../../../spec/NUCLEO.md) y
[`../../../../../spec/MEDIDOR.md`](../../../../../spec/MEDIDOR.md) ·
Origen: [`../../../../../reviews/fallos-especialista.md`](../../../../../reviews/fallos-especialista.md),
hallazgos F03, F06, F07, F11, F12, F13 y F14.

**Estado fijado** (el árbol muta mientras se escribe): base `a4f880e`, con otros dos agentes
trabajando a la vez en `puente/`, `galaxia/pueblos/**` y `cosmos/abrir.py`. Este parte cubre
`cosmos/medir.py`, `cosmos/cli.py`, `cosmos/generar.py`, `cosmos/validar.py`,
`cosmos/guardarrailes.py`, cuatro ficheros de `tests/`, `puente/tests/mutaciones.py`,
`docs/CALIBRACION.md`, `spec/NUCLEO.md`, `spec/MEDIDOR.md`, `GOAL.md`, `README.md` y el parte de
`rescate-skills.md`. SHA-256 (12) de los cinco módulos, en ese orden: `cb95780d3bcc`,
`bbe898fd719a`, `e15fe94bfebe`, `2af85b25913b`, `0c5d1a3573e2`. Se referencia por símbolo, nunca
por `fichero:línea`.

Los siete se reprodujeron **antes** de tocar nada. Dos de las reproducciones del informe salieron
distintas a lo que yo esperaba y cambiaron el arreglo: el interbloqueo de F11 tenía **dos** mitades,
no una, y el segundo número que F06 pedía publicar resultó ser peor que no publicarlo. Va explicado
donde toca.

> **Aviso de método, y me costó media hora.** Mi primer barrido de sabotaje dio «CAZADO» en los diez
> casos, es decir, lo contrario del informe. La copia del repo excluía `.cosmos/`, así que la suite
> ya estaba roja **antes** de mutar nada: `Ran 90 — FAILED` por E19, no 95 OK. Un barrido de
> mutación sin medir primero el verde de la copia no mide nada. Regla: la línea base de la copia se
> ejecuta y se enseña antes del primer sabotaje.

---

## F06 · El «peor caso de agua por extensión»: mi veredicto

**La premisa era falsa, y el fallo es peor que el que describe el informe: el código se apartó de la
spec sin tocar la spec.**

`spec/NUCLEO.md` §3 define, literalmente:

```
agua = Σ tokens(cuerpo(n)) para n en agua_condicional(árbol)
```

y `spec/MEDIDOR.md` llama a `entrada + agua` «el techo real de una **sesión** de trabajo». El commit
`cf7e10a` cambió eso por un máximo agrupado por extensión y **no tocó ninguno de los dos
documentos**. Un medidor que se afloja para que quepa el contenido es el fallo F01 por la otra
puerta, y esta vez además contra la norma escrita.

La premisa del docstring —«nadie toca un `.py`, un `.css` y un `.html` en el mismo instante»— es
falsa porque la pregunta no es el instante: el agua entra por `paths:` y **se queda en el contexto
el resto de la sesión**. Un proyecto React + Python toca las dos cosas en la misma sesión y paga las
dos. La premisa correcta es la que ya estaba escrita: **la sesión, no el fichero**.

Y el cálculo, además, estaba roto por dentro. Reproducción ejecutada, tal cual:

```
$ python3 -c "
from cosmos.medir import _extensiones_de as X
for m in [['**/*.spec.*'],['**/*.ts'],['**/tests/**'],['**/Makefile']]:
    print(f'  {str(m):18} -> {sorted(X(m))}')"
  ['**/*.spec.*']    -> ['.*']
  ['**/*.ts']        -> ['.ts']
  ['**/tests/**']    -> ['*']        <- un directorio se vuelve universal
  ['**/Makefile']    -> ['*']        <- un nombre sin punto, tambien
```

y sobre un árbol de dos mares que mojan **el mismo** fichero (`src/app.spec.ts`):

```
medidor publica  : 120 tokens  [('mar/tipado', 120)]
carga de verdad  : 240 tokens
```

**La mitad.** En la galaxia real el efecto era doble y en direcciones opuestas: cobraba `custodia`
(por `**/migrations/**` → «universal») a un `.py` que no la moja, y **no cobraba nunca**
`accesibilidad` (101 tok), que no solapa con el grupo ganador. El rótulo remataba: decía
`(5 aguas por paths:)` habiendo **seis** — el «5» era el tamaño del grupo ganador, no cuántas aguas
hay.

### Qué cambié

Se borran `_extensiones_de` y `_peor_agua_coincidente`; `_detalle_agua` devuelve toda el agua
condicional, que es la definición normativa. `agua` pasa de 1.245 a 1.346 tokens en la galaxia.

**Lo que NO hice, y por qué.** El informe pedía publicar además un segundo número, `agua_por_fichero`.
No lo he puesto, y creo que es lo correcto:

1. Calcular de verdad el peor fichero es **intersecar globs** (¿existe una ruta que case
   `**/*.spec.*` **y** `**/*.ts`? sí: `x.spec.ts`). Toda aproximación barata —instanciar cada glob
   por separado, agrupar por extensión— se equivoca **hacia abajo**, que es exactamente el error que
   este arreglo viene a cerrar. Un segundo número que solo puede subestimar, al lado de un
   presupuesto, es el antipatrón otra vez.
2. La comprobación de aceptación que pedía el informe («el árbol de dos mares tiene que publicar
   482, no 241») **la cumple ya la suma**: publica los 480 enteros. El segundo número no hacía falta
   para eso.
3. F17 del mismo informe se queja de «tres veredictos de presupuesto distintos sobre el mismo
   árbol». Añadir un cuarto número que no decide nada empuja en esa dirección.

Quien quiera el desglose lo tiene sin inventar métricas: `cosmos medir --detalle` lista el agua nodo
a nodo con su coste.

### Qué lo fija

`tests/test_medidor.py`, tres pruebas nuevas, **las tres vistas en rojo** contra el `cosmos/medir.py`
de `HEAD` antes del arreglo:

| Prueba | Qué caza |
|---|---|
| `test_dos_aguas_que_mojan_el_mismo_fichero_se_cobran_las_dos` | el 120 donde había 240 |
| `test_un_agua_que_no_solapa_con_la_mas_cara_tambien_se_cobra` | `accesibilidad` desapareciendo del número |
| `test_el_recuento_publicado_es_el_numero_real_de_aguas` | el rótulo «5 aguas» habiendo seis |

Y `spec/MEDIDOR.md` gana los puntos 6 y 7 de «Verificación exigida», para que el próximo que quiera
cambiar cómo se mide el agua tenga que cambiar la spec primero.

---

## F03 · La prueba de calibración estaba en verde por no tener la dependencia

### La reproducción, ejecutada

```
$ python3 -m unittest tests.test_medidor            # esta máquina, sin tiktoken
OK (skipped=1)
$ python3 -m venv /tmp/calib && /tmp/calib/bin/pip install -q tiktoken
$ /tmp/calib/bin/python -m unittest tests.test_medidor.PruebasMedidor.test_aproximado_y_exacto_respetan_margen_publicado
AssertionError: 0.19047619047619047 not less than or equal to 0.052
```

19,05 % contra un 5,2 % publicado. El corpus eran **siete líneas** que el propio test escribía.
Medido: sobre el árbol de juguete la divergencia media es del **27,9 %**; sobre el árbol real, del
**4,99 %**. La representatividad del corpus no era un detalle, era el fallo entero.

### Qué cambié

- El corpus pasa a ser **lo que el medidor cuenta de verdad**: los cuerpos de los nodos de la
  galaxia (n=315, divergencia media 4,99 % ≤ 5,2 %) y, aparte, el número que decide el presupuesto
  (`entrada`, 2,3 %). Con tokenizador la prueba **pasa de verdad**, por primera vez.
- El salto ya no es silencioso: imprime un `AVISO` nombrando lo que se ha quedado sin verificar, y
  `COSMOS_EXIGE_TOKENIZADOR=1` lo convierte en fallo. Comprobados los tres modos.
- Nace `test_los_factores_publicados_son_los_que_documenta_la_calibracion`, que **corre siempre**,
  con tokenizador o sin él, y ata `FACTOR_CALIBRACION`, `FACTOR_GENERADO` y `MARGEN_ERROR` a los
  números de `docs/CALIBRACION.md`. Es la que cierra dos de los agujeros de F07.
- `docs/CALIBRACION.md`: el procedimiento de mantenimiento comparaba el ratio con **1,0** cuando por
  construcción vale ≈`FACTOR_CALIBRACION` (`n=258 ratio=1.2274` sobre un factor sano). Un
  procedimiento que siempre grita no se usa dos veces. Criterio nuevo y explícito:
  `abs(ratio/FACTOR - 1) > 0.05 → recalibrar`.
- **`FACTOR_GENERADO` no estaba documentado en ninguna parte.** Lo introdujo el arreglo de F01 hace
  unas horas y `docs/CALIBRACION.md` seguía publicando un solo factor. Ahora tiene su sección.

---

## F11 · Un árbol nuevo no tenía camino a verde

### La reproducción, ejecutada

Árbol mínimo creado desde cero (una galaxia, un sistema, un planeta, un pueblo), sin índice y sin
vista plana:

```
$ python3 -m cosmos validar   -> EXIT 1   E15 «Ejecuta 'cosmos generar'» + E19 «Ejecuta 'cosmos compilar'»
$ python3 -m cosmos generar   -> EXIT 1   E19 «Ejecuta 'cosmos compilar'»
$ python3 -m cosmos compilar  -> EXIT 1   E15 «Ejecuta 'cosmos generar'»
$ python3 -m cosmos arrancar  -> EXIT 1   COSMOS arrancar rojo
```

Cada comando manda al otro. Cuatro salidas, ninguna puerta.

### El arreglo del informe estaba a medias, y lo vi al ejecutarlo

El informe proponía eximir a `generar` de E19 («son dos caracteres»). Lo hice, y `arrancar` **siguió
en rojo**. La razón: el interbloqueo tiene dos mitades y la segunda está en el paso **posterior** de
`compilar`, que exigía E15 —una invariante que `compilar` tampoco puede reparar, porque no escribe
el índice—. Con solo la mitad del arreglo, `cosmos generar && cosmos compilar && cosmos validar`
funciona pero `cosmos arrancar` no.

La regla de `NUCLEO.md` §6 estaba enunciada demasiado estrecha. Generalizada:

> **Una invariante que compara el disco contra lo que se generaría no puede bloquear a un comando
> que no la puede reparar** — ni a quien la genera, ni a nadie más.

### Qué cambié

1. `generar` omite E19 **antes y después**: no toca la vista plana, así que ni la repara ni la rompe.
2. `compilar` omite E15 **antes y después**, por simetría. `validar` las sigue exigiendo las dos:
   el rojo se ve igual, solo deja de secuestrar al comando equivocado.
3. `arrancar` escribe el índice **si no existe**. Un índice ausente no puede engañar a nadie; uno
   presente y falso sí, y ahí E15 sigue siendo un rojo real y `arrancar` no lo toca. Es lo que hace
   que un árbol nuevo llegue a verde con **un solo comando**, que es lo que su ayuda promete.
4. `spec/NUCLEO.md` §6: regla generalizada, tabla con la fila de `arrancar` y la condición del
   índice ausente.

Comprobado a mano sobre el árbol nuevo:

```
$ python3 -m cosmos arrancar                                   -> EXIT 0  «COSMOS arrancar verde»
$ python3 -m cosmos generar && compilar && validar             -> EXIT 0
# y con un indice que EXISTE y miente:
$ python3 -m cosmos arrancar   -> EXIT 1 (E15) y el fichero falso intacto
```

### Qué lo fija

`tests/test_compilar.py`: `test_generar_repara_e15_y_no_lo_bloquea_una_e19_que_no_puede_reparar`
(reescrita: la anterior **exigía** el interbloqueo), `test_un_arbol_nuevo_llega_a_verde_con_un_solo_arrancar`
y `test_arrancar_no_repara_un_indice_que_existe_y_miente`, que es el contrapeso: sin ella, el
bootstrap se convertiría en una forma de tapar el fallo que E15 existe para cazar. Las tres vistas
en rojo (las dos primeras contra el `cli.py` de `HEAD`, la tercera mutando `if not
config.indice.exists()` a `if True`).

---

## F07 · Las funciones sin vigilar: encontré ocho, no cinco

Barrido propio, un `str.replace` de una línea sobre una copia del repo y las dos suites enteras.
Sobre la línea base verificada (`Ran 95 OK (skipped=1)` y `Ran 80 OK`):

```
  NO CAZADO  medir._extensiones_de -> siempre {"*"}
  NO CAZADO  medir.FACTOR_CALIBRACION = 1.0
  NO CAZADO  medir.FACTOR_GENERADO = 1.204              <- no estaba en el informe
  NO CAZADO  medir.MARGEN_ERROR = None
  NO CAZADO  validar.cobertura_total -> False
  NO CAZADO  medir.agua_condicional cuenta el agua con 'moja: []'   <- no estaba en el informe
  NO CAZADO  validar.SONDAS_E11 amputado                <- no estaba en el informe
  NO CAZADO  cli: generar no revalida despues de escribir           <- no estaba en el informe
  CAZADO     medir.contar_generado usa el factor de prosa
  CAZADO     medir: el catalogo no distingue nicho
```

Los cuatro que el informe no traía, uno a uno:

- **`FACTOR_GENERADO = 1.204`**: revertir el factor que el arreglo de F01 introdujo hace tres horas
  —el que separa índice y catálogo de la prosa— devolvía el árbol al verde falso sin un solo rojo.
  La corrección de un fallo llegó sin la prueba que la vigila.
- **`agua_condicional` sin exigir alcance**: el río y la lluvia (`moja: []`) se cobrarían en el
  presupuesto sin llegar a cargarse nunca. `NUCLEO.md` §3 los excluye explícitamente. Lo tapaba el
  propio agrupamiento por extensión: un `moja: []` no aportaba extensión y se caía del grupo, así
  que el test que sí lo miraba no podía verlo. **Al arreglar F06 este agujero se cerró solo** — y
  ahora tiene su mutación.
- **`SONDAS_E11` amputado**: el corpus normativo de E11 puede perder familias enteras de ficheros en
  silencio; con solo `main.py`, `['**/*.py']` ya «lo cubriría todo».
- **`generar` sin revalidar**: se puede declarar verde un índice recién escrito que sigue sin cuadrar.

### Qué lo fija

| Sabotaje | Prueba que lo caza |
|---|---|
| `_extensiones_de` (borrada) → el agua más cara | `test_dos_aguas_que_mojan_el_mismo_fichero_se_cobran_las_dos` |
| `FACTOR_CALIBRACION`, `FACTOR_GENERADO`, `MARGEN_ERROR` | `test_los_factores_publicados_son_los_que_documenta_la_calibracion` |
| `cobertura_total → False` | `test_e11_cobertura_total_con_todos_los_globs_anclados` |
| `agua_condicional` con `moja: []` | `test_el_agua_condicional_no_entra_en_la_entrada_pero_si_en_el_presupuesto` |
| `SONDAS_E11` amputado | `test_el_corpus_de_sondas_no_deja_fuera_ninguna_familia` |
| `generar` sin revalidar | `test_generar_no_declara_verde_sin_revalidar_lo_que_acaba_de_escribir` |

Detalle de `cobertura_total`: los cebos que ya existían llevan `**/*.*` o `**/?`, sin una sola letra
— los caza `_sin_anclaje` y `cobertura_total` no llega nunca a decidir. El cebo nuevo son nueve
globs **todos anclados** que juntos cubren las doce sondas.

`puente/tests/mutaciones.py` pasa de 30 a 38 mutaciones: **M31–M38**, las primeras que tocan
`cosmos/medir.py`, `cosmos/validar.py`, `cosmos/cli.py` y `cosmos/guardarrailes.py`. Antes de esto,
`mutaciones.py` no vigilaba ni una línea del medidor ni del validador.

```
$ python3 puente/tests/mutaciones.py | tail -1
38/38 invariantes vistas fallar
```

---

## F12 · El parte que atribuía a la medida lo que causó su contenido

`rescate-skills.md` decía: *«el commit `cf7e10a` … cambió cómo se mide el agua condicional: pasó de
961 a 1.398 tokens **sin que se añadiera un solo nodo**»*. Las tres afirmaciones son falsas, y en la
dirección que más engaña: hacen pensar que el margen se estrechó por un cambio de método y no por
haber gastado presupuesto.

Medido con `git archive`, cada árbol con su propio código:

```
cf7e10a^ : 5 mares, agua publicada 961
cf7e10a  : 6 mares, agua publicada 1.398
cf7e10a  : 6 mares, con el metodo VIEJO (suma de toda el agua) = 1.499
```

`cf7e10a` **añadió** `mar-revision` (236 tok) y engordó otros tres (`criterio` 295→421, `pruebas`
358→473, `resistencia` 100→161). Con el mismo método, el contenido subió **+538**; el cambio de
método bajó el número **−101**. Su propio mensaje de commit lo decía bien («Medido: 1.499 -> 1.398»)
y el parte lo copió al revés.

Corregido en el fichero, con la reproducción dentro y la lección que pedía el informe: **un parte
cita el bloque de `cosmos medir` con el hash del commit al que corresponde en la misma línea**, no
un número suelto de memoria.

Aplicada esa misma lección a `spec/MEDIDOR.md`, que publicaba un bloque de salida de la heurística
v1 (`1.012 / 817 / 2.472 / 61.400`, ±8 %) sin fecha: ahora el ejemplo es el **árbol de juguete
versionado** (`cosmos medir --config ejemplo.toml`), que se reproduce entero y no envejece con el
crecimiento de la galaxia.

---

## F13 y F14 · Dos números escritos a mano que ya contradecían al árbol

- **F13**: `GOAL.md` decía «20 oficios» (dos sitios, más un «los veinte sitios») contra los 21 del
  árbol. `GOAL.md` §0 dice que si algo del repo lo contradice, gana `GOAL.md`: aplicando su propia
  regla, el oficio 21 era ilegal. **Quitado el número**, que era la opción que recomendaba el
  informe: lo dicta `spec/UNIVERSO.md` y `GOAL.md` no lo repite. Una cosa menos que mantener.
- **F14**: `cosmos/cli.py` y `README.md` decían «E00–E19» con E20 existiendo, y el desfase **ya
  estaba anotado** en `fix-h20-niveles.md` desde hacía días. Un hallazgo escrito y no cerrado es
  peor que uno no encontrado. Ahora la ayuda **se genera** desde `COMPROBACIONES`
  (`validar.rango_comprobado()`), así que no se puede desincronizar; el README no se puede generar,
  así que se ata con una prueba.

Las tres pruebas (`tests/test_cli.py::DocumentacionAlDia`) vistas en rojo contra el `README.md`, el
`GOAL.md` y el `cli.py` anteriores. Nota para quien añada E21: la cadena se ajusta sola.

---

## Encargo del coordinador: `EVENTOS_SESION` no enrutaba `Grep`, `Glob` ni `Task`

Verificado con llamadas reales, no leyendo el módulo:

```
$ python3 -c "...bloque_sesion('ORDEN')..."
  PostToolUse -> matcher "Bash|Read"                      <- solo tres de las cinco

$ echo '{"hook_event_name":"PostToolUse","tool_name":"Grep","tool_response":"... AKIA..."}' | python3 -m puente.sesion
  {"updatedToolOutput": {"output": "... [REDACTADO: clave AWS] ..."}}   <- el guard SI sabe taparlo
```

Una puerta construida y sin cablear: un secreto encontrado con `Grep` entraba en claro. Enrutadas
las cinco (`HERRAMIENTAS_POSTERIORES`), y atado con tres pruebas en
`tests/test_guardarrailes.py::EnrutadoDeSesion`: el `settings.json` que `enganchar_sesion` escribe
de verdad, la comparación contra `puente.sesion.HERRAMIENTAS_VIGILADAS` (anti-deriva) y una llamada
real al guard por subproceso. Mutación **M38**.

`PreToolUse` se deja como estaba: `Grep`, `Glob` y `Task` son de solo lectura y lo que se decide
allí es escritura y ejecución.

---

## El presupuesto: lo que costó decir la verdad, y dónde queda

Restaurar la definición normativa del agua subió el número honesto **+101** y dejó el árbol en
**4.071 / 4.000, rojo por 71**. No se sube el límite. Busqué coste innecesario **dentro de mi
boundary** y encontré 81 tokens, los dos en el índice generado y los dos sin perder información:

| Qué | Tokens | Por qué sobra |
|---|---:|---|
| `<!-- Generado por cosmos generar. No editar a mano. -->` | 23 | va dirigido a una persona que abra el fichero, pero quien lo lee en cada turno es el agente; y quien impide el retoque a mano es E15, que ya dice esa frase exacta |
| Acentos graves y raya de `` - `nombre` — resumen `` | 58 | el catálogo, en el mismo bloque, ya usa `clave: resumen`; dos formatos para la misma cosa |

Es el mismo criterio con el que este proyecto ya había quitado los océanos del índice («presentar
algo que viene dos líneas después es coste sin función»). `cosmos acertar` no se movió: la
contra-métrica lee el catálogo, no el índice.

**Estado al cerrar: `3.999 / 4.000`. Queda 1 token.** No es margen mío que me haya comido: mientras
trabajaba, otro agente creció el universo de 158.045 a 160.316 tokens. El presupuesto muerde, que es
lo que tiene que hacer, pero el siguiente commit de contenido pone en rojo a todo el mundo. Lo digo
aquí en vez de arreglarlo por mi cuenta porque las dos salidas que quedan son decisiones de
contenido y no mías:

- **Los 14 ríos cuestan 329 tokens del catálogo, en todos los nichos** (8 % del presupuesto). Son
  los verbos del propio COSMOS. `NUCLEO.md` §3 dice que su resumen «ya se paga en el catálogo», así
  que sacarlos es cambiar la spec — pero conviene saber que uno de los fallos de `acertar` es
  «predecir las ventas del próximo trimestre → `rio/validar`»: además de costar, desvían.
- Recortar contenido de `galaxia/`, que está fuera de mi boundary y con otro agente dentro.

### Elevado: F01 **no** está cerrado, y su commit lo declaró verde con el contador aproximado

Reproducción copiable:

```
$ python3 -m venv /tmp/calib && /tmp/calib/bin/pip install -q tiktoken
$ /tmp/calib/bin/python -c "
import sys; sys.path.insert(0,'.')
import pathlib; from cosmos.modelo import cargar_arbol; from cosmos import medir
a = cargar_arbol(pathlib.Path('galaxia'))
for m in ('aprox','exacto'):
    r = medir.medir_casos(a, metodo=m, presupuesto=4000).peor
    print(f'{m:7} entrada={r.entrada} agua={r.agua} con_agua={r.entrada_con_agua}')"
aprox   entrada=2653 agua=1346 con_agua=3999
exacto  entrada=2778 agua=1545 con_agua=4323
```

**Con el tokenizador de referencia el árbol está en 4.323 / 4.000.** No lo he causado yo: sobre
`HEAD` antes de tocar nada ya daba `exacto 4.268` mientras el medidor publicaba 3.970. El commit
`eea0116` cierra F01 diciendo «Verde de verdad: 3.970/4.000» — ese 3.970 es del contador
**aproximado**, que es justo lo que F01 denunciaba. Los dos factores redujeron el error del 15 % al
7,7 %; no lo cerraron. Medido hoy: la prosa real tokeniza a **1,243** (factor 1,204) y los bloques
generados a **≈1,455** (factor 1,381).

Recalibrar **no** lo arregla: solo hace que el rojo se vea. Lo que decide es qué contenido sale o
qué presupuesto es el bueno, y eso no lo decide un agente por su cuenta. Queda anotado en
`docs/CALIBRACION.md` y vigilado por
`tests/test_medidor.py::test_canario_f01_el_veredicto_exacto_sigue_en_rojo`, que **afirma el defecto
a propósito**: el día que el veredicto exacto sea verde, esa prueba se pone roja y se borra junto
con el arreglo.

---

## Cadena de verificación

```
$ python3 -m unittest discover -s tests            ->  Ran 129   OK (skipped=2)
$ python3 -m unittest discover -s puente/tests     ->  Ran 102   OK
$ python3 puente/tests/mutaciones.py               ->  38/38 invariantes vistas fallar
$ python3 -m cosmos validar                        ->  COSMOS verde, 0 errores
$ python3 -m cosmos medir                          ->  3.999 / 4.000, OK (quedan 1)
$ python3 -m cosmos acertar                        ->  33/50 ajuste, 10/20 validacion
$ /tmp/calib/bin/python -m unittest discover -s tests   ->  OK, sin skips: la calibracion pasa de verdad
$ COSMOS_EXIGE_TOKENIZADOR=1 python3 -m unittest discover -s tests  ->  FAILED (el salto ya no es gratis)
```

Los dos skips de la suite normal son las dos pruebas que necesitan tokenizador, y ahora lo dicen en
voz alta por `stdout`.

---

## Sin commitear, a propósito

Tres agentes trabajan el mismo árbol a la vez y `cosmos/cli.py` ya se fue en el commit de otro. Dos
ficheros que toco tienen trabajo ajeno **en vuelo**: `puente/tests/mutaciones.py` (M19–M30 son del
agente de guardarraíles; M31–M38 son mías) y el propio `cosmos/` alrededor de `abrir.py`. Commitear
selectivamente partiría mi entrega o se llevaría la suya con mi mensaje, así que se deja todo en el
árbol de trabajo y lo secuencia quien orquesta. Los 18 ficheros están verdes ahora mismo y la cadena
de verificación de arriba se reproduce tal cual.

`cosmos/validar.py` solo gana dos funciones al final (`codigos_comprobados` y `rango_comprobado`);
una E21 nueva entra en `COMPROBACIONES` sin tocarlas y la cadena `E00–E21` se ajusta sola.
