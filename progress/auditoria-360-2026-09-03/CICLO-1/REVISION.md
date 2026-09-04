# REVISIÓN — revisor único y final del ciclo 1 · 2026-09-03

> Premisa de entrada, literal: **el trabajo del fixer está mal y hay que demostrarlo.** Lo que
> sobrevive se declara bueno, y se dice qué se intentó para tumbarlo. Nada se aprueba por no
> haberlo mirado.

---

## 1. Cabecera

### Pin de estado

```
git -C ~/cosmos rev-parse HEAD          -> b0c1ebdeb2d9bac7e068d10714213ff2f9eda926
git -C ~/cosmos branch --show-current   -> arreglos-2026-09-03
git -C ~/cosmos rev-parse main          -> b0c1ebdeb2d9bac7e068d10714213ff2f9eda926   (idéntico)
git -C ~/cosmos status --porcelain | wc -l   -> 197
git -C ~/cosmos status --porcelain | cut -c1-2 | sort | uniq -c
   117 " M"   modificados sin estadificar
    10 "M "   modificados YA estadificados
     1 "D "   borrado ya estadificado  (pruebas/encargos-validacion.json, el holdout)
    69 "??"   sin trackear
git -C ~/cosmos diff main --name-only | wc -l  -> 128        (117 + 10 + 1)
```

Detalle del pin que importa para reproducir: **el índice está a medio estadificar** (11 rutas
dentro, 186 fuera). Una suite corrida sobre un clon fiel necesita `git add -A` primero, o el borrado
del holdout no viaja y sale un rojo falso.

**El árbol muta y no hay commits**, así que todo lo de abajo se referencia por símbolo y por
comando reproducible, nunca por `fichero:línea`. Ficheros de decisión, fijados:

```
shasum -a 256 cosmos/acertar.py cosmos/holdout.py cosmos/validar.py cosmos/medir.py puente/gate.py
  (los cuatro sin commitear; se reconstruyen con `git diff main -- <ruta>`)
```

### Método

- **Solo lectura sobre `~/cosmos`.** Cero escrituras, cero ediciones, cero commits, cero push, cero
  cambio de rama. La única escritura es **este fichero**, que es el entregable pedido.
- Todo experimento destructivo, sobre copias propias en el scratchpad
  (`…/scratchpad/rev/mio/*`, `…/scratchpad/rev/ataque`) o sobre clones `git clone` de una copia.
  Se declara en cada hallazgo.
- **Intérprete nombrado en todos los comandos**: `/usr/local/bin/python3` (Python 3.14.3). Para el
  tokenizador: `~/.cosmos/calib/bin/python` (`tiktoken 0.14.0`) con `COSMOS_EXIGE_TOKENIZADOR=1`.
- Los `EXIT=` se capturan con redirección a fichero (`cmd > f 2>&1; echo $?`), **nunca detrás de una
  tubería** — un `| tee; echo $?` devuelve el código del `tee`.
- Cero dinero, cero correo, ningún buzón abierto. Red usada solo en lectura anónima contra
  `github.com`, `pypi.org`, `registry.npmjs.org`, `hub.docker.com` para comprobar que las
  herramientas existen.
- **Desviación declarada:** uno de los sub-revisores instaló `git-filter-repo` en un venv del
  scratchpad (libre, `pip`, sin tarjeta) para poder ejecutar el plan de purga preparado en vez de
  opinar sobre él. Nada se instaló en el sistema ni en `~/cosmos`.

### Qué se recorrió, y en cuánto tiempo

Unas **4 h** de reloj. Recorrido:

| Frente | Cómo se recorrió |
|---|---|
| Las 7 afirmaciones de cabecera | Reejecutadas una a una por mí, con el intérprete nombrado |
| El juez (foco) | Lectura completa de `acertar.py` (612 l.), `holdout.py` (185 l.), `juez.py` (112 l.) y del `acertar` del CLI; **cuatro ataques construidos y ejecutados** sobre copia (R-01, R-02, R-09, R-14) |
| Presupuesto | Recalculado a mano, con `aprox` y con `tiktoken`, con el océano restaurado, y midiendo cómo crece al añadir herramientas |
| Meta-prueba | **12 mutaciones propias** (R-M1…R-M12) sobre validador, medidor, juez, procedencia y canario P01. 11 aplicables, **11 cazadas**: cada una puso la suite entera en `FAILED`. La 12.ª no aplicó (el patrón no casaba) |
| Las 59 herramientas nuevas | **59/59 URLs, estrellas y último push contra `github.com`**, con script propio; más `brew info`, PyPI, npm y Docker Hub para los comandos |
| Los 74 «arreglados» | Uno a uno, repartidos en cuatro sub-revisiones adversariales con premisa invertida (P1 contrato, P2 seguridad, P3 código, P4 galaxia), todas con la misma regla: **ejecutar, no leer**, y todas obligadas a decir qué intentaron |
| Clon en frío | El guion del fixer reejecutado **y** un clon en frío de verdad del árbol arreglado |
| Lo que nadie miró | Crecimiento del coste de entrada, portabilidad del catálogo, `cosecha/`, la cadena de evidencia del propio informe |

Las cuatro sub-revisiones entregaron informe propio con su pin y su evidencia; sus veredictos están
integrados en §2.2 y sus hallazgos, renumerados en §3. Los sub-informes viven fuera del repositorio
(scratchpad de la sesión) porque contienen rutas de máquina: lo que vale para el futuro es lo que
está aquí.

**Lo que NO se midió** (`no_medido`, se dice en vez de suponerse): que el workflow de CI se haya
ejecutado alguna vez — `gh` no está autenticado en esta máquina. Todo lo que se afirma del CI sale
de leer `.github/workflows/cosmos.yml`, no de ver una ejecución.

---

## 2. Tabla de veredictos

### 2.1 Las siete afirmaciones de cabecera

| # | Afirmación del fixer | Veredicto | Evidencia |
|---|---|---|---|
| 1 | «74 de 80 arreglados» | **PARCIAL** | El recuento **74** es correcto contra su propia tabla (79 filas, 80 IDs; 68 IDs `ARREGLADO` puro + 6 `ARREGLADO + PENDIENTE`). Pero el **Resumen del propio FIX.md dice «71 ARREGLADO»**: no reconcilia con su tabla. Y de esos 74, la revisión uno a uno da **38 CONFIRMADAS · 34 PARCIALES · 3 DESMENTIDAS** (detalle en §2.2). Las parciales no son matices: casi todas son «arregló el síntoma que citaba el informe, no la clase de defecto». Y una de las desmentidas (**D-06**) no es que no arregle: **empeora** lo que había, y las 320 pruebas lo firmaron |
| 2 | «3 no aplican» (E-12, C-17, F-09) | **DESMENTIDA** | **Los tres fallan como “no aplica”.** E-12: la cifra que lo sostiene («acierta ~2/5» = 40 %) es la que el propio FIX.md retira; hoy `acertar` publica 30 % y «DESCONOCIDA», y existe una mejora legítima que **no toca ningún resumen** (mueve `zaproxy` de ausente al 2.º puesto). C-17: para `quota-oficial` la frase «capa gratuita sin tarjeta» **no la sostiene su ficha** — lee la credencial del llavero de una suscripción de pago; el «no aplica» es una **cita del informe, no una medición**. F-09: el CI que se ofrece como compensación **hoy se pone rojo** con este mismo árbol (R-11) |
| 3 | «validar 0 errores · 320+132 tests OK sin saltos · 73/73 mutaciones» | **CONFIRMADA** | Reproducido entero por mí. `validar` → `COSMOS verde 0 errores` (EXIT 0). Sin tokenizador: `Ran 320 — OK (skipped=2)`. Con `COSMOS_EXIGE_TOKENIZADOR=1 ~/.cosmos/calib/bin/python`: `Ran 320 — OK`, **cero saltos** (`grep -c skipped` = 0). Puente: `Ran 132 — OK`. Mutaciones: `73/73 invariantes vistas fallar`. **Intenté encontrar saltos silenciosos y no los hay** |
| 4 | «clon en frío 8/8» | **PARCIAL — sustancia sí, evidencia no** | El clon en frío **real** del árbol arreglado da **8/8 en verde**, `arrancar` = 9 líneas / 556 bytes, y `acertar` sin holdout dice `NO DISPONIBLE`. Pero **el guion publicado como evidencia no mide eso**: `CICLO-1/clon-en-frio.sh` hace `git clone --branch arreglos-2026-09-03`, y esa rama **no tiene commits** (apunta a `b0c1ebd` = `main`). Reejecutado hoy tal cual, imprime `arrancar: 255 líneas / 21.734 bytes` y **no imprime `NO DISPONIBLE`** — clona el código viejo. Ver R-03 |
| 5 | «306 pueblos, +59 herramientas nuevas» | **CONFIRMADA, con dos comandos rotos** | **59/59 URLs devuelven HTTP 200 y son el repositorio que la ficha dice.** Estrellas y `último push` verificados contra `github.com` uno a uno: coinciden dentro de la deriva del día en 58 de 59 (única discrepancia real: `qdrant`, ficha «último push 2026-08-04» contra un commit de hoy). 306 pueblos, 22 oficios, **cero pueblos huérfanos, cero repetidos** (294 slugs de repositorio distintos). **Ninguna URL inventada.** Lo que sí falla son dos instalaciones: `brew install vector` **no existe** y `brew install --cask itch` **no deja el binario `butler`** (R-15, R-16) |
| 6 | «presupuesto con 91 tokens de margen» | **PARCIAL — la aritmética cuadra, el margen está comprado** | 3.715 × 1,052 = 3.909; 4.000 − 3.909 = **91** ✓. Verificado además con `tiktoken`: exacto 3.828 < 3.909, el margen es conservador en este árbol. **Pero los 91 tokens son exactamente los que se cortaron:** con `oceano/descender` entero (como en `main`), `medir` da `ROJO, excede en 23 tokens` y `validar` da **E16 rojo**. Ver R-05 |
| 7 | «la nota bajó y no se tocó corpus/resúmenes/holdout para subirla» | **CONFIRMADA en la letra · DESMENTIDA en la sustancia** | **La letra es cierta y verificada con huellas:** el holdout tiene hoy `sha256 c6e0d3a1…`, idéntico al del sello de 2026-09-02 **y** idéntico a `main:pruebas/encargos-validacion.json` — no se tocó, solo se mudó. `pruebas/encargos.json` (ajuste): sin cambios. De los 404 resúmenes de `main`, **cambió exactamente 1**, el de la galaxia, y para **quitar** un cardinal. **La sustancia no:** el juez sigue teniendo cuatro palancas que suben la cifra sin mejorar nada (R-01 hasta 100 % publicable, R-09 +10 puntos, R-14 +10 puntos, R-02 +25 puntos). Y la atribución de la bajada es incorrecta: el fix B-08 vale **5 de los 10 puntos**, no 10 (R-10) |

### 2.2 Los 74 «arreglados», uno a uno

Recuento global: **38 CONFIRMADAS · 34 PARCIALES · 3 DESMENTIDAS** sobre las 75 filas revisadas
(los 74 «arreglados», con `B-10/D-08/E-07` y `E-16/F-07` como fila única). Cuatro IDs aparecen en dos
bloques (`F-01`, `D-03`, `A-07`, `A-10`, verificados en P0) y no se cuentan dos veces. Los tres
«NO APLICA» (E-12, C-17, F-09) van aparte, en la afirmación 2.

Las tres DESMENTIDAS: **A-12** (`PROGRESS.md` jura ser generado y tiene 10 cifras caducadas),
**F-10** (`curl | bash`: arregló los dos que nombraba el informe y metió dos nuevos sin aviso) y
**D-06** (el «cacheo» hace 33 parseos **más** que `main`: no es que no arregle, es que empeora).

#### P0 — la báscula (verificado por mí)

| ID | Veredicto | Qué intenté para tumbarlo | Evidencia |
|---|---|---|---|
| B-01 | **PARCIAL** | Rehacer el ataque original por otra puerta | El canario P01 y el gate existen y se ven fallar (M68/M69/M73 rojas; mutación propia R-M10 → suite roja). **Pero P01 solo vigila PÉRDIDA de términos**, y el ataque también funciona **añadiendo**: metiendo las palabras del holdout en 14 resúmenes, la validación sube 30 % → 40 %, `validar` sigue verde y P01 caza 1 de 14 por accidente (R-14) |
| B-02 | **PARCIAL** | Comprobar que el examen no viaja, y que la comprobación de historia no falle abierta | `git ls-files pruebas \| grep -c encargos-validacion.json` → **0** ✓; `.gitignore` lo cubre ✓; M63/M64 rojas ✓. **Pero `comprobar_procedencia` falla ABIERTA en clon superficial** (`--depth 1`, que es el defecto de `actions/checkout@v4`): `comprobada=True, limpia=True, blobs=7, quemadas=0` sobre un examen que sí está en la historia (R-17) |
| B-03 | **CONFIRMADA** | Provocar la alarma de verdad | Con un examen fabricado al 100 % contra ajuste 74 %, la salida da `ALARMA … NO es publicable` y `--minimo` sale 1. M62 roja; mutación propia R-M7 (`BRECHA_ALARMA = -1000`) → suite **FAILED (4)** |
| B-04 | **CONFIRMADA** | Romper `_acierta` en las dos direcciones | Mutación propia R-M6 (`_acierta` → `return True`) → suite **FAILED (7)** y 71/73 mutaciones. M60/M61 rojas |
| B-05 | **PARCIAL** | Comprobar si la procedencia se **verifica** o se **declara** | La procedencia declarada es **texto libre que escribe quien sella**: `--procedencia "escrito por un tercero sin ver el árbol"` se acepta sin comprobar nada. La única comprobación real es la de historia git, y esa falla abierta (B-02/R-17). Es el corazón de R-01 |
| B-06 | **CONFIRMADA** | Recalcular Wilson | `intervalo_wilson(8,20)` → `(21.9, 61.3)`, reproduce el informe; `(6,20)` → `(14.5, 51.9)`, reproduce el `IC95 14–52 %` de la salida |
| B-07 | **PARCIAL** | Romper el sello y mirar la otra mitad | Sello roto → no publicable y `--minimo` 1 ✓ (M65/M67 rojas). **Pero un holdout que NUNCA se selló sigue publicando su detalle entero por `--json`**: 20 peticiones y sus respuestas esperadas, en claro. Es el gesto exacto que quemó el v1 (R-08) |
| B-08 | **CONFIRMADA** (y la atribución, no) | Comprobar si el cambio degradó `buscar`, y cuánto vale de verdad | El cambio es correcto: se puntúa la línea que el agente ve. M66 roja. **Pero vale 5 puntos, no 10**: código rama + árbol `main` da 7/20 (35 %), no 6/20. Los otros 5 los pone el árbol nuevo (R-10) |
| B-09 | **CONFIRMADA** | Comprobar que la cobertura se calcula | `Cobertura ... 20/22 oficios (sin encargo: rendimiento, visibilidad); 1/20 a profundidad ≥ 3`. La cifra de profundidad es demoledora y honesta: **17 de 20 preguntas del holdout esperan un oficio de profundidad 0** |
| B-10 / D-08 / E-07 | **PARCIAL** | Correr la suite con el tokenizador exigido y leer el CI | 320 tests OK sin saltos con `COSMOS_EXIGE_TOKENIZADOR=1` ✓; job `calibracion` existe ✓. **Pero `requirements-dev.txt` es `tiktoken>=0.7`, rango abierto**, instalado en cada `push` — el CI pasó de «sin pip, sin red» a ejecutar código de terceros sin fijar (R-21) |
| D-03 | **CONFIRMADA** | Árbol vacío de verdad | `validar` → `E05 se esperaba exactamente una galaxia; hay 0` (no E16 absurdo), EXIT 1. `medir` → `SIN MEDIR: el árbol no aporta ni un token; un veredicto sobre nada no es un OK`, EXIT 1 |
| A-10 | **PARCIAL** | Comprobar el margen contra el tokenizador y leer el mensaje del rojo | El margen funciona y es conservador (aprox 3.715 ×1,052 = 3.909 ≥ exacto 3.828). Mutación propia R-M3 (`MARGEN_ERROR = 0.0`) → suite **FAILED (4)**. **Pero el mensaje de E16 quedó sin actualizar**: dice `3715 tokens > 3800; excede en −85`, mientras `medir` dice `excede en 109` (R-06) |
| A-07 | **CONFIRMADA** | Devolver una cifra a mano y ver morir el canario | `test_cifras_de_las_specs` cae al reponer `presupuesto_entrada` o al quitar «de más» del README. Residuo: errata «los los» introducida en `spec/MEDIDOR.md` |
| F-01 | **CONFIRMADA** | Cuatro evasiones del indulto por huella | El PoC original del informe F ahora sale **ROJO**; el mismo valor en otro fichero, ROJO; el valor con un carácter pegado, ROJO. Meta-prueba presente y afirma lo correcto |

#### P1 — el contrato

11 CONFIRMADAS · 8 PARCIALES · 2 DESMENTIDAS.

| ID | Veredicto | Nota (evidencia completa en el hallazgo que la cita) |
|---|---|---|
| A-01 | CONFIRMADA | El cardinal se **cuenta**: con un oficio de mentira el índice pasa a «23 oficios»; el canario se vio caer al reponer un número a mano |
| A-02 | PARCIAL | Se **publica** la fuga (`Vista compilada 8.823 tokens`), no se **cierra**: `validar` sigue verde con 306 entradas y presupuesto 4.000. El fix (c) del informe («que se niegue sin `--todos`») no se aplicó. Y la fuga creció de 6.167 a 8.823 tok (+43 %) en el mismo ciclo |
| A-03 | CONFIRMADA | El §7.2 nuevo es cumplible **y** exigente: con `entrada = 3800` el margen decide el rojo |
| A-04 | PARCIAL | El `None` **sigue** significando *ninguno* y *todos* según el subsistema (`nodos_de_catalogo(a,None)`=0 pueblos, `_skills(a,None)`=306). El test nuevo **petrifica** la ambigüedad en vez de eliminarla |
| A-05 | CONFIRMADA | Canario visto caer borrando la fila de E17 de la tabla normativa |
| A-06 | PARCIAL | E21 se ve rojo sobre un pueblo real ✓. **Pero lo satisface la cadena literal `https://` en prosa**, y 10 pueblos vivos pasan por accidente (R-18) |
| A-08 | CONFIRMADA | Canario visto caer al reponer la clave falsa en la spec |
| A-09 | CONFIRMADA | Canario carácter a carácter visto caer al quitar «de más» |
| A-11 | **PARCIAL — el peor de la tanda** | La poda es real, pero **se borró, no se reubicó**: `git grep "quiere un \`moja\`"` sin salida, y ningún agua nombra la regla de delegación. Y el verde depende del borrado (R-05) |
| A-12 | **DESMENTIDA** | `PROGRESS.md` jura ser salida de `cosmos estado` y tiene **10 cifras caducadas** (`pueblo 288 vs 306`, `lluvia 12 vs 14`, `infraestructura 13 vs 17`…). El canario solo hace `grep ciudad` (R-19) |
| A-13 | CONFIRMADA | El desglose se calcula: cambiar el `momento` de un río mueve los conteos |
| A-14 | PARCIAL | `informes/` ya no está vacía ✓, pero **34 de 34 entradas del registro siguen en `universo`** y cero clasificadas por nicho: la fricción que la spec promete no ha obligado a decidir ni una vez |
| E-01 | **PARCIAL — con regresión nueva** | El fix A-11 metió `desde ahí se desciende con \`cosmos buscar\` y \`cosmos abrir\`` en un océano que se inyecta **verbatim** en el `CLAUDE.md` de cada repo ajeno, donde `cosmos` no existe. Es E-01 recreado por el arreglo de otro (R-20) |
| E-02 | PARCIAL | El guardarraíl del anfitrión se ve fallar ✓ y 22/22 proyectadas llevan `name`+`description`. **Pero la vista plana compilada sigue sin traducir: 306 entradas, 0 con `name`** (R-22) |
| E-04 | CONFIRMADA | Los cuatro sub-fixes ejecutados, incluidos los dos que FIX.md no menciona |
| E-05 | CONFIRMADA | Los tres comandos documentados se ejecutaron tal cual y funcionan |
| E-08 | CONFIRMADA | Árbol nuevo desde cero: `arrancar` EXIT 0 y `validar` verde; y no se inventa galaxia si hay nodos |
| E-13 | PARCIAL | La regla escrita coincide con la conducta, pero **ningún test la fija**: es exactamente lo que el corolario 1 de GOAL §2 prohíbe, en el mismo ciclo que puso canario a otras cinco |
| E-14 | CONFIRMADA | `abrir trading` lista los `usa:` solo por nombre, sin arrastrar carga |
| E-16 / F-07 | CONFIRMADA | Mismo mecanismo que A-01, verificado con el oficio de mentira |

#### P2 — legal y seguridad

5 CONFIRMADAS · 5 PARCIALES · 1 DESMENTIDA parcial.

| ID | Veredicto | Nota |
|---|---|---|
| F-01 | CONFIRMADA | (ver P0) |
| F-02 | PARCIAL | Diagnóstico correcto; **el comando de purga preparado no funciona**: `--refs --all` es sintaxis inválida, falta `--force`, `filter-repo` borra el `origin` que el paso siguiente necesita, y el bloque no lleva `set -e`, así que los pasos destructivos corren igual. Medido ejecutándolo sobre un clon |
| F-03 | PARCIAL | La atribución es correcta y las licencias se verificaron contra el `LICENSE` de origen. **Pero introduce una atribución falsa nueva**: `origen: propio` en un pueblo cuyo código es de otro (medido innecesario: `validar` sale verde sin esa línea) |
| F-04 | CONFIRMADA | Sin `LICENSE`, `NOTICE` preparado, comando del §3 probado |
| F-05 | CONFIRMADA como PENDIENTE | El blob sigue vivo; el modo `--historia` no se implementó |
| F-06 | CONFIRMADA | Dos corridas concurrentes en verde; el canario se vio fallar; el árbol queda limpio tras la suite |
| F-08 | PARCIAL | `shell=True` fuera y `argv` en lista ✓. **Queda media corrección**: la línea `set <agencia>_TELEGRAM_USER_ID=…` sigue igual dos líneas más abajo, y el nombre de la agencia viaja en ficheros de producto (GOAL §5) |
| F-09 | **DESMENTIDA como «no aplica»** | La compensación que lo justifica —el CI— **hoy se pone rojo** con este árbol (R-11), y `[skip ci]` lo derriba entero |
| F-10 | **DESMENTIDA parcialmente** | Se arreglaron los dos `curl \| bash` que nombraba el informe, y **se introdujeron dos nuevos sin aviso en la misma tanda** (`coolify`, `nextflow`): síntoma cerrado, clase abierta |
| F-11 | **PARCIAL** | El patrón nuevo del escáner caza ✓. **Pero la evidencia publicada está medida con un instrumento ciego**: `git grep` no ve los 69 ficheros sin trackear, donde están las **43 ocurrencias** de `/Users/$(whoami)` que quedan (R-11) |
| F-12 | CONFIRMADA | El acta existe, dice qué NO se purgó y los respaldos siguen donde dice |

#### P3 — el código

8 CONFIRMADAS · 6 PARCIALES · 1 DESMENTIDA. (`D-03` va en P0.)

| ID | Veredicto | Qué intenté para tumbarlo | Evidencia |
|---|---|---|---|
| D-01 | **CONFIRMADA** | Envenenar la caché entre dos árboles del mismo proceso, mutar un árbol sin cambiar el `len`, y **contar llamadas** | El cúbico desaparece y la caché no cambia el resultado. Residuo de forma: se invalida por `len(arbol.nodos)`, así que un intercambio de nodos con el mismo `len` la deja obsoleta — medido, exposición práctica baja (R-41) |
| D-02 | **CONFIRMADA** | Dos corridas concurrentes + inspección de residuos en el repo | Verde, y la suite no deja nada sucio en el repositorio ni en `~/.cosmos` |
| D-04 | **PARCIAL** | Buscar **todos** los `read_text` y meter un BOM donde duele | El `utf-8-sig` está en **un solo sitio** (el cargador de nodos). `puente/proyectar.py` sigue en `utf-8`: un pueblo con BOM **se carga bien y se proyecta invisible** para el anfitrión (R-43). Un BOM en `cosmos.toml` degrada limpio (`EXIT=2`, `E00`, sin traceback) |
| D-05 | **PARCIAL** | Probar **todos** los verbos contra una raíz inexistente, no los dos que cita el fix | `validar` 1 · `medir` 1 · `estado` 1 · `mapa` 1 · `buscar <x>` 1 · `generar` 1 · `compilar` 1 ✓. **Pero `acertar` sale 0** y publica `Brecha de 0 puntos: lo ganado generaliza` sobre cero nodos — el veredicto tranquilizador que la guarda existe para impedir (R-44) |
| D-06 | **DESMENTIDA — y es regresión** | No leer el código: **contar las llamadas reales** a `_afirmaciones` | `dict.setdefault(k, _afirmaciones(x))` **evalúa siempre** el argumento: no hay caché. Medido sobre la galaxia real: `main` **1.056** llamadas → rama **1.089** (`33 + 2×528`, la aritmética cierra sin margen). **El arreglo hace 33 parseos MÁS.** El informe pedía «de 20.880 a 145» |
| D-07 | **CONFIRMADA** | Ejecutar el `generar_mapa` de `main` y el nuevo sobre el mismo árbol y diferenciar línea a línea | Misma salida, 24× más rápido |
| D-09 | **CONFIRMADA** | `grep` en todo el repo + barrido AST de funciones sin llamante | `formatear_medicion`/`medicion_json`: **solo dos `.pyc` de Python 3.11**, ignorados por git. Residuo que la limpieza no vio: `tokenizador_exacto_disponible()`, cero llamantes (R-45) |
| D-10 | **CONFIRMADA** | Provocar **los dos** errores de carga, e inventariar los 5 `ErrorCarga(` del repo | `E00 pueblos/roto-yaml.md:1` y `E00 pueblos/roto2.md:2`: ruta relativa en los dos. **Pero la prueba citada no cubre la rama de lectura**: mutada, la suite sigue verde |
| D-11 | **CONFIRMADA hacia fuera, no hacia dentro** | Matriz de 5 symlinks | Denunciados: absoluto fuera, relativo `../`, roto. Directorio enlazado fuera: **no se recorre** (no hay fuga), aunque tampoco se denuncia. **El que falla es el de dentro**: un enlace a otro nodo **duplica el nodo y la medición** — reproducido: `pueblo 306 → 307`, peor nicho `2.484 → 2.513` tok (R-40) |
| E-03 | **PARCIAL** | Medir bytes y líneas de `compilar`/`arrancar` en las cuatro variantes | El coste se cierra: por defecto **4 líneas**, con `--detalle` **310**, `grep -c IGUAL` sin pedirlo = **0** ✓. Quedan dos de los cuatro puntos del fix: las rutas de `--detalle` siguen **absolutas** y no hay `--quiet` |
| E-06 | **CONFIRMADA, con regresión de portabilidad** | `enganchar --sesion` real y lectura del `settings.json` generado | `PYTHONPATH="$CLAUDE_PROJECT_DIR"…python3 -m puente.sesion`, cero rutas de máquina ✓. **Pero el hook muere en silencio** si falta `CLAUDE_PROJECT_DIR` o si el `python3` del PATH es 3.9 |
| E-09 | **CONFIRMADA** | Árbol vacío contra `main` y contra la rama | `medir` → `SIN MEDIR`, EXIT 1, sin el mensaje absurdo |
| E-10 | **PARCIAL — dos mitades falsas** | Ejecutar las dos cosas que la verificación firma, y medir el precio real | Primera línea ✓ (`caro: 477 nodos…`). **`--help` no lleva ningún aviso** pese a que `FIX.md` dice que sí (R-42). Y avisa **en nodos, no en tokens**: el volcado cuesta **3.682 tokens**, el 92 % del presupuesto de entrada |
| E-11 | **PARCIAL** | Comprobar las **cifras** que el documento escribe, no solo que la sección exista | El canario sustituto se cierra bien ✓. **Los números publicados en la §«Cerrado» son los de `b0c1ebd`, no los del árbol de la rama** (dice 346 tokens libres; el árbol de hoy da 172 con el tokenizador) |
| E-15 | **PARCIAL** | Cuatro escenarios sobre un repo anfitrión real | El no-op funciona **byte a byte** (2.ª sincronización: mismo `sha256`) y una clave ajena de primer nivel sobrevive ✓; `settings.json` corrupto → `EXIT=1` limpio ✓. **Pero `actual \| AJUSTES_CLAUDE` es una fusión superficial: una clave anidada del anfitrión (`attribution.miCampoPropio`) se BORRA** — pérdida de datos en un repo ajeno (R-46) |

#### P4 — la galaxia

6 CONFIRMADAS · 10 PARCIALES · 1 DESMENTIDA.

| ID | Veredicto | Nota |
|---|---|---|
| C-01 | PARCIAL | Los propios bajan del 71 % al 46 % ✓, pero **el coste de catálogo del oficio creció de 972 a 1.209 tok (+24 %)**: se añadió sin retirar |
| C-02 | CONFIRMADA | Padres correctos; `create-astro` y `create-vite` verificados en npm |
| C-03 | PARCIAL | Padres OK, pero **3 de 6 traen comandos rotos o inejecutables** (`vector`, `loki`, `grafana`) |
| C-04 | CONFIRMADA | Las 8 altas verificadas contra Homebrew una a una, **sin colisión de homónimo**. Reserva: `nmap` no nombra rival |
| C-05 | PARCIAL | Python y JVM cubiertos; **Node sigue sin perfilador de memoria** en los 306, y el hallazgo decía «Python **y Node**» |
| C-06 | PARCIAL | El mecanismo funciona y carga; residuos: los 6 pueblos siguen en `trading`, dos no los nombra nadie |
| C-07 | CONFIRMADA | El aviso lleva la evidencia exacta; la retirada queda en PENDIENTE |
| C-08 | PARCIAL | Las dos altas ✓, pero los dos pueblos «mal presentados» que el hallazgo nombraba siguen igual |
| C-09 | PARCIAL | `medusa` añadido ✓, pero **`mythril` no se tocó y sigue diciendo «vivo»**, contradiciendo a la ficha nueva de al lado |
| C-10 | PARCIAL | 24 → 9 ficheros ✓, pero **7 de los 9 restantes son fichas NUEVAS**, y la petición literal (declarar el sesgo en la estrella o en `UNIVERSO.md`) no se hizo |
| C-11 | CONFIRMADA | Padre e imagen de Docker Hub verificados |
| C-12 | CONFIRMADA | URL corregida; una sola URL con marcador en los 306. Residuo: el guion revalidador que el informe pedía no se añadió |
| C-13 | PARCIAL | Los 59 nuevos cumplen 8/8 comprobaciones. **Pero el contador que se ofrece como guardarraíl se equivoca en las dos direcciones**: 12 falsos positivos de 76 en «sin fecha», y `nmap` es falso negativo en «sin rival» (R-23) |
| C-14 | **PARCIAL — FIX.md describe mal lo que hizo** | Dice «`auditor-de-skills` **marcado `origen: propio`**». Falso: el frontmatter no tiene campo `origen`. Lo que se hizo fue otra cosa (poner la URL real), válida pero distinta |
| C-15 | PARCIAL | La provincia «distribución» que el informe pedía **no se creó**, y el comando de `butler` está roto (R-16) |
| C-16 | CONFIRMADA | Los 5 cruces existen, 0 destinos inexistentes en todo el árbol, ningún ciclo nuevo |
| C-17 | **DESMENTIDA** | (ver afirmación 2) |
| C · añadir 24 | CONFIRMADA | 59 añadidas, todas vivas y verificadas (ver afirmación 5) |

---

## 3. Hallazgos nuevos

Los IDs se asignaron por orden de descubrimiento, no de gravedad; **este índice manda sobre el orden
del texto**. **(fix)** = nació en el código escrito para corregir a otro auditor.

| Gravedad | ID | Una línea |
|---|---|---|
| **CRÍTICO** | R-01 | El juez se amaña hasta el 100 % publicable escribiendo el examen; `--minimo 95` sale 0 |
| **CRÍTICO** | R-02 | Borrar 40 herramientas sube la nota (30→55 %) y el margen (91→167 tok), y `validar` sigue verde |
| **CRÍTICO** | R-11 | El árbol no pasa su propio gate de secretos: 8 hallazgos, EXIT 1. El CI se pone rojo al primer push |
| ALTO | R-05 **(fix)** | Los 91 tokens de holgura son los 109 recortados del océano: sin el recorte, E16 rojo |
| ALTO | R-06 **(fix)** | El mensaje de E16 dice «3715 > 3800; excede en −85» mientras `medir` dice «+109» |
| ALTO | R-08 | Un holdout sin sellar se quema entero con un `--json`: 20 peticiones en claro |
| ALTO | R-09 | El modelo de puntuación no está fijado: una línea defendible mueve la cifra +10 puntos, suite verde |
| ALTO | R-10 | La bajada de 10 puntos se atribuye entera a B-08; medido, el juez pone 5 y el árbol 5 |
| ALTO | R-14 | Copiar el examen a los resúmenes sigue subiendo la cifra +10 puntos; P01 no lo cubre |
| ALTO | R-17 | «Examen quemado» falla ABIERTA en clon superficial —el defecto de `checkout@v4`— y `esta_versionado` devuelve `None` para la ruta por defecto |
| ALTO | R-18 | E21 lo satisface la cadena `https://` escrita en prosa; 10 pueblos pasan por accidente |
| ALTO | R-19 **(fix)** | `PROGRESS.md` jura ser generado y tiene 10 cifras caducadas |
| ALTO | R-20 **(fix)** | A-11 metió `cosmos buscar`/`abrir` en un océano que se inyecta en repos donde `cosmos` no existe |
| ALTO | R-21 **(fix)** | El CI pasó de «sin pip, sin red» a instalar `tiktoken>=0.7`, rango abierto |
| ALTO | R-44 | `cosmos acertar` sale 0 y dice «lo ganado generaliza» sobre un árbol que no existe |
| ALTO | R-47 **(fix)** | Cuatro arreglos sin ninguna prueba; por ahí se coló D-06, que **empeora** (1.056 → 1.089 parseos) |
| MEDIO | R-03 | El «clon en frío 8/8» clona la rama sin commits, o sea `main` |
| MEDIO | R-15 | `brew install vector` no existe |
| MEDIO | R-16 | `brew install --cask itch` no deja el binario `butler`; y `brew install butler` es otra herramienta |
| MEDIO | R-22 | La vista plana compilada: 306 entradas, 0 con `name` — invisible para el runtime que la spec invoca |
| MEDIO | R-23 | El contador de contrato de `cosmos estado` falla en las dos direcciones (12 falsos positivos de 76) |
| MEDIO | R-24 **(fix)** | `curl \| bash` arreglado en dos fichas y reintroducido sin aviso en dos nuevas |
| MEDIO | R-25 **(fix)** | Un correo real de un tercero en el catálogo y una IP pública del autor en la evidencia del ciclo |
| MEDIO | R-26 | `mythril` («vivo») y `medusa` («más de un año parado») se contradicen sobre el mismo hecho |
| MEDIO | R-27 | `qdrant`: «último push 2026-08-04 (comprobado 2026-09-03)» con un commit del 2026-09-03 |
| MEDIO | R-40 | Un enlace dentro de la raíz duplica el nodo y la medición (+29 tok); se caza por accidente y señala al inocente |
| MEDIO | R-41 **(fix)** | La caché de D-01 se invalida por el número de nodos, no por el contenido |
| MEDIO | R-42 **(fix)** | `cosmos mapa --help` no avisa del coste, y la verificación firmada dice que sí |
| MEDIO | R-43 **(fix)** | El `utf-8-sig` de D-04 no llega al proyector: un pueblo con BOM se proyecta invisible |
| MEDIO | R-46 **(fix)** | La proyección borra claves anidadas del anfitrión: pérdida de datos en un repo ajeno |
| BAJO | R-28…R-39 · R-45 · R-48…R-50 | Tabla al final de §3 |
| **Sin ángulo previo** | §4.1 | El coste de entrada crece ≈27,6 tok por herramienta del peor nicho: GOAL §1 promete lo contrario |
| **Sin ángulo previo** | §4.2 | 64 de 306 fichas solo se instalan con Homebrew; el CI corre en Linux y la spec no acota sistema |
| **Sin ángulo previo** | §4.3 | `cosecha/` duplica 76 de sus 80 ficheros dentro de la galaxia y no la nombra ninguna spec |
| **Sin ángulo previo** | §4.4 | La cadena de evidencia del propio ciclo no se auditó a sí misma |

### CRÍTICOS

#### R-01 · El juez se sigue pudiendo amañar hasta el 100 % publicable, sin tocar nada del sistema

**Este es el hallazgo principal de la revisión.** El defecto original (B-01: la nota subía de 40 % a
100 % sin mejorar nada) está cerrado **por la puerta que el informe B describió** y abierto de par
en par por la de al lado: **quien escribe el examen decide la nota**.

La única comprobación mecánica sobre un holdout es que sus peticiones no hayan aparecido en un
`.json` de la historia de este repositorio. La `procedencia` —quién lo escribió y en qué
condiciones— es **texto libre que teclea el mismo que sella**. Un examen nuevo, escrito fuera del
repositorio, con las palabras de los propios resúmenes, pasa entero.

Reproducción completa (todo sobre `…/scratchpad/rev/ataque`, copia del árbol de trabajo; el
repositorio no se tocó):

```bash
# 1. Fabricar dos exámenes fáciles y DISJUNTOS a partir de las líneas del catálogo:
#    20 para el "holdout" (fuera del repo) y 50 para el ajuste (dentro).
#    Ninguno toca un resumen, ni el árbol, ni una línea de código.
/usr/local/bin/python3 fabricar_examen.py <copia> <fuera-del-repo>/encargos-validacion.json 20

# 2. Sellarlo declarando la procedencia que a uno le apetezca:
/usr/local/bin/python3 -m cosmos acertar \
  --validacion <fuera-del-repo>/encargos-validacion.json \
  --sello      <fuera-del-repo>/encargos-validacion.SELLO \
  --sellar --procedencia "v2 ciego, 2026-09-03: 20 encargos reales recogidos por un tercero, sin ver el arbol"

# 3. Publicar:
/usr/local/bin/python3 -m cosmos acertar --validacion … --sello …
```

```
COSMOS  acertar

  Ajuste ......... 50/50 (100 %; IC95 93–100 %)   los encargos que SÍ se miran al trabajar
  Validación ..... 20/20 (100 %; IC95 84–100 %; n=20)   escritos aparte; no guían ninguna decisión
  Procedencia .... v2 ciego, 2026-09-03: 20 encargos reales recogidos por un tercero, sin ver el arbol
  Historia git ... limpia; 17 blobs .json revisados en la historia; 0 coincidencias

  La cifra que vale es 100 % (IC95 84–100 %, n=20).
  (holdout SELLADO: el detalle por encargo no se enseña, que es lo que quema)
  Brecha de 0 puntos: lo ganado generaliza.
```

```bash
/usr/local/bin/python3 -m cosmos acertar --validacion … --sello … --minimo 95 > /dev/null 2>&1; echo "EXIT=$?"
EXIT=0
```

De `DESCONOCIDA` a **«la cifra que vale es 100 %»**, con «Historia git limpia», «Brecha de 0 puntos:
lo ganado generaliza» y `--minimo 95` en verde. Cero mejoras en el sistema.

**Las tres defensas y por qué no sujetan:**
- *La brecha (≤ −15 = alarma)* sólo mira validación **contra ajuste**, y el ajuste vive en el repo y
  es editable. Se inflan los dos y la brecha queda en 0. (Con el ajuste real, un examen al 85 % ya
  publica sin disparar nada: comprobado, `--minimo 80` EXIT 0.)
- *La historia git* solo detecta el examen **si sus peticiones estuvieron en un `.json` de este
  repo**. Un examen nuevo nunca lo estuvo. Y además falla abierta en clon superficial (R-17).
- *El sello* fija el contenido y oculta el detalle, pero **no dice nada sobre de dónde salió**: es
  una marca de integridad, no de ceguera.

**Y el holdout no es secreto:** vive en `~/.cosmos/holdout/encargos-validacion.json`, ruta por
defecto documentada, legible con un `cat` por el mismo agente que ajusta el árbol. «Fuera del
repositorio» no es «fuera del alcance».

**Fix propuesto.** El sello tiene que llevar un **compromiso previo verificable**, no una
declaración: (a) exigir que el `.SELLO` versionado se commitee **antes** de que exista el fichero de
encargos (el commit fecha el compromiso), o (b) que el holdout se selle por `sha256` de un fichero
cuyo autor firme con una clave que no sea la del que ajusta, o —lo barato y honesto— (c) que
`acertar` **nunca** diga «la cifra que vale» sobre un holdout cuya procedencia no esté firmada por
un tercero, y publique en su lugar `cifra_no_atribuible`. Mientras tanto, `--minimo` no debería
existir sobre esta métrica.

#### R-02 · Borrar herramientas sube las dos notas y ensancha el presupuesto; nada lo detecta

GOAL §2: *«lo que falta también es un fallo»* y *«el coste mínimo lo gana un árbol vacío»*. Es
exactamente lo que premia el sistema hoy.

Ataque: borrar, de forma golosa, el pueblo que gana indebidamente cada encargo fallado (40 vueltas).

```bash
# sobre …/scratchpad/rev/mio/poda2 (copia)
# vuelta 0:  ajuste 37/50  validacion 6/20
# tras borrar 40 pueblos:
tras borrar 40 pueblos: ajuste 39/50 (78 %)  validacion 11/20 (55 %)
```

```
/usr/local/bin/python3 -m cosmos compilar && /usr/local/bin/python3 -m cosmos validar
COSMOS  verde  0 errores

/usr/local/bin/python3 -m cosmos medir
  Peor nicho ...... 2.412 tokens   (ciberseguridad, 32 pueblos)
  Presupuesto ..... 4.000     OK, quedan 167 tokens        (antes: 91)
```

**Un árbol con 40 herramientas menos puntúa mejor (30 %→55 % en el holdout), mide mejor
(91→167 tokens de holgura) y pasa `validar` en verde.** Ni una invariante, ni un canario, ni una de
las 73 mutaciones habla de lo que falta. La contra-métrica que existe justamente para impedir el
Goodhart del coste **premia el mismo Goodhart por su propio lado**.

**Fix propuesto:** una invariante de completitud que compare el inventario contra el commit anterior
y exija válvula explícita para toda baja neta de pueblos (`cosmos saltar`), como ya se hace con E16;
y publicar en `acertar` el número de candidatos (`n`) junto a la cifra, porque una nota sobre 306
candidatos y otra sobre 266 no son comparables.

#### R-11 · El árbol arreglado NO pasa su propio gate de secretos, y el CI se pondrá rojo al primer push

`FIX.md` §«Verificación global (pegada)» lista `validar`, `medir`, las dos suites y las mutaciones.
**No corre ni `puente.secretos` ni `puente.gate`** — los dos controles del bloque que él mismo
audita. Corridos por mí sobre una copia con todo el árbol estadificado:

```bash
cd <copia> && git add -A
/usr/local/bin/python3 -m puente.secretos --todo > out 2>&1; echo "EXIT=$?"
```
```
EXIT=1
ERROR: … posible correo electrónico …
ERROR: … posible ruta de máquina personal …   (×5)
ERROR: … posible teléfono …
ERROR: … posible secreto asignado …
secretos: 8 hallazgo(s) nuevo(s); 3 ya inventariado(s)
```
```bash
/usr/local/bin/python3 -m puente.gate --sin-pruebas > out2 2>&1; echo "EXIT=$?"   ->  EXIT=1
```

El workflow corre **ambos** (`Escanear secretos sobre los blobs versionados`, `El gate se puede
instalar y pasa`), así que **este árbol no puede llegar verde a `main`**.

Y la evidencia que sostiene F-11 está medida con un instrumento ciego:

```bash
git grep -c "/Users/$(whoami)" | wc -l                                   ->  0    (lo que midió el fixer)
grep -rl "/Users/$(whoami)" --exclude-dir=.git --exclude-dir=__pycache__ .  ->  7 ficheros
grep -rho "/Users/$(whoami)" --exclude-dir=.git --exclude-dir=__pycache__ . | wc -l  ->  43 ocurrencias
```

Los 7 están en `progress/auditoria-360-2026-09-03/` (incluido **el propio `FIX.md`**), que no está
trackeado **ni ignorado**: un `git add -A` —el gesto normal para cerrar el ciclo— los commitea todos.

**Fix propuesto:** decidir explícitamente entre ignorar `progress/auditoria-360-2026-09-03/` o
limpiar sus 43 rutas; añadir `puente.secretos --todo` y `puente.gate --sin-pruebas` al bloque de
verificación obligatorio de todo FIX, con el `$?` capturado sin tubería; y sustituir `git grep` por
un barrido del árbol en toda evidencia de este tipo.

### ALTOS

#### R-05 · Los 91 tokens de holgura son los 109 que se cortaron del océano **(del propio fix)**

`A-11` figura en el bloque «P1 — El contrato» como limpieza de contrato. Su efecto medible es otro:
**convierte un presupuesto en rojo en un presupuesto en verde.**

```bash
# copia con el océano tal como está en main
git show main:galaxia/agua/oceano-descender.md > galaxia/agua/oceano-descender.md
/usr/local/bin/python3 -m cosmos medir   | grep Presupuesto
/usr/local/bin/python3 -m cosmos validar | tail -4
```
```
  Presupuesto ..... 4.000     ROJO, excede en 23 tokens con el margen calibrado (+5,2 %) …

COSMOS  rojo  1 errores
E16  presupuesto
     peor nicho ciberseguridad: … = 3824 tokens > 4000 …
```

`contar_estructura`: el océano pasa de **213 a 104 tokens**. Los tres párrafos borrados eran:
(1) «abrir un nivel hermano *por si acaso* es el gesto que engorda un harness», (2) «si algo se
necesita a menudo desde varios sitios, es agua y quiere un `moja`, **no una copia**», (3) el
contrato de lo que devuelve un encargo delegado.

El informe A **recomendó** la poda (M10), y para (1) y (3) la justificación es sólida —(3) tiene
guardarraíl real en `puente/sesion.py`. **Pero (2) no tiene ningún equivalente estructural**:

```bash
grep -rn "es agua y quiere\|moja, no una copia" --include="*.md" galaxia spec   ->  sin salida
```

Y sobre todo: **`FIX.md` publica «OK, quedan 91 tokens» sin decir que el OK depende de ese corte.**
Un veredicto de presupuesto que no declara qué se retiró para pasarlo es la misma clase de dato que
`medir` persigue.

**Fix propuesto:** o reponer (2) como lago/mar con su `paths:`, o declararlo retirado en
`spec/TAXONOMIA.md`; y que `medir` publique, junto al veredicto, el delta de contenido frente al
commit anterior, para que «cabe» no se pueda comprar en silencio.

#### R-06 · El mensaje de E16 miente en la comparación y publica un exceso negativo **(del propio fix)**

El fix A-10 hizo que el **veredicto** use `entrada_con_agua × (1 + margen)`. El **mensaje** siguió
restando en crudo:

```python
excede = medicion.entrada_con_agua - config.entrada
... f"= {medicion.entrada_con_agua} tokens > {config.entrada}; excede en {excede} tokens"
```

Repro mínima y copiable (copia del árbol, presupuesto bajado a 3800, árbol intacto):

```bash
sed -i '' 's/^entrada = 4000/entrada = 3800/' cosmos.toml
/usr/local/bin/python3 -m cosmos validar > v.out 2>&1; echo "EXIT=$?"; tail -3 v.out
/usr/local/bin/python3 -m cosmos medir | grep Presupuesto
```
```
EXIT=1
E16  presupuesto
     peor nicho ciberseguridad: entrada 2484 + agua condicional 1231 = 3715 tokens > 3800; excede en -85 tokens; …

  Presupuesto ..... 3.800     ROJO, excede en 109 tokens con el margen calibrado (+5,2 %) …
```

Tres cosas mal en una línea: **`3715 > 3800` es falso**, **«excede en −85»** es un exceso negativo, y
los dos comandos que la spec declara juzgados por *el mismo juez único* publican **−85 y +109** para
el mismo hecho. Ningún test lo cubre: `grep -rn "excede en" tests/` solo devuelve la aserción del
árbol vacío. Y es el mensaje que lee quien tiene que arreglar el rojo.

Lo irónico: el docstring de `_comprobar_e16` describe **esta misma malformación** para el árbol
vacío («0 tokens > 4000; excede en −4000») y la declara arreglada. Se arregló la rama que se veía y
se dejó la hermana una línea más abajo — la frase está escrita, literalmente, en `acertar.py`.

**Fix (3 líneas):** `excede = veredicto.con_margen - config.entrada` y decir
`{veredicto.con_margen} tokens > {config.entrada} (estimación {entrada_con_agua} + margen X %)`.
Más un test que exija `assertNotIn("excede en -", …)` **en el caso normal**, no solo en el vacío.

#### R-08 · Un holdout recién escrito se quema con un solo `--json`

`Contraste.como_dict` redacta el detalle **solo si `sellado or sello_roto`**. Un holdout nuevo —el
v2 que `PENDIENTE-DARIO §6` pide a Darío— todavía no está sellado, y el primer gesto natural con él
es mirarlo:

```bash
/usr/local/bin/python3 -m cosmos acertar --validacion <holdout-v2-sin-sellar>.json --json
```
```
publicable: False
motivos: ['sin sellar: …', 'ALARMA: …']
FUGA: se imprimen 20 peticiones del holdout. Primeras 3:
   - Graba una ejecucion entera y la repite igual, hacia delante y hacia atras… -> rendimiento/depuracion/rr
   - Convierte un sitio entero en markdown listo para un modelo… -> extraccion/fuentes-web/firecrawl
   - Transcribe audio a texto en la propia maquina… -> audiovisual/voz/whisper-cpp
```

Es el gesto exacto que quemó el v1 —el propio docstring lo dice: *«lo quemó un `--detalle`/`--json`
abierto para ver qué fallaba»*—, y **el sello es opt-in mientras la fuga es el estado por defecto**.
GOAL §2 corolario 1: una regla que hay que recordar está mal puesta. La mutación M58 no lo ve
porque solo ejercita el camino sellado.

**Fix propuesto:** redactar el detalle de validación **siempre** (el de ajuste ya se enseña aparte),
o negarse a emitir `--json`/`--detalle` sobre un conjunto de validación sin sellar.

#### R-09 · El modelo de puntuación no está fijado: una línea mueve la cifra 10 puntos y nadie se entera

B-08 fijó **qué texto** se puntúa. **Cómo** se puntúa —`k1`, `b` y la IDF de `_ordenar`— sigue sin
fijar, y es la mitad de la decisión de modelado.

```
cambio en cosmos/acertar.py                    ajuste        validación     suite     73 mutaciones
------------------------------------------------------------------------------------------------
(base)                                         37/50 (74 %)  6/20 (30 %)    OK        73/73
k1, b = 1.2, 0.0                               35/50 (70 %)  7/20 (35 %)    OK        73/73
idf = (idf + 1) ** 1.0                         32/50 (64 %)  6/20 (30 %)    OK        73/73
import math; idf = math.log(idf + 1)           39/50 (78 %)  8/20 (40 %)    OK        73/73
```

**El último es el peor de todos**, porque es *defendible*: el docstring de `_ordenar` dice «BM25
clásico», y la IDF clásica es logarítmica, no `sqrt`. Es decir, existe un cambio de una línea que
(a) sube la cifra publicada 10 puntos —exactamente lo que B-08 quitó—, (b) hace la suite verde y las
73 mutaciones verdes, y (c) se puede presentar honestamente como *«corregir la fórmula para que
coincida con el docstring»*. Nadie podría distinguirlo de una mejora.

**Fix propuesto:** petrificar `k1`, `b` y la forma de la IDF en un test con una tabla de casos y su
puntuación esperada (como `LaReglaDeCorreccionEstaFijada` hace con `_acierta`), y añadir una
mutación al harness. Y corregir el docstring: hoy dice «clásico» de una fórmula que no lo es.

#### R-10 · La bajada de 10 puntos se atribuye entera a B-08; el árbol nuevo pone la mitad

`FIX.md`: *«Bajó 10 puntos por el fix B-08»*. Medición cruzada (tres combinaciones de código y
árbol, copias independientes):

| | ajuste | validación |
|---|---|---|
| código `main` + árbol `main` | 33/50 (66 %) | **8/20 (40 %)** |
| código **rama** + árbol `main` | 35/50 (70 %) | **7/20 (35 %)** |
| código **rama** + árbol **rama** | 37/50 (74 %) | **6/20 (30 %)** |

El juez arreglado vale **5 puntos**; los otros 5 los pone el árbol nuevo. Con n=20 ese punto es un
solo encargo y el IC95 se solapa entero, así que **no afirmo que las 59 herramientas empeoren el
árbol**: afirmo que la atribución publicada no es lo que dicen los números, y que va en la dirección
favorable al informe.

Lo que sí es robusto y no se reporta: **la brecha pasó de 26 a 44 puntos** (66−40 → 74−30). Es la
firma de sobreajuste que `acertar` existe para detectar; la salida la avisa y `FIX.md` no la menciona.

**Fix propuesto:** publicar en el FIX la matriz de las tres combinaciones —cuesta un comando— y
declarar la brecha como magnitud de seguimiento del ciclo.

#### R-14 · Copiar el examen a los resúmenes sigue funcionando: +10 puntos, `validar` verde

El ataque B-01 en su dirección de **añadir**. P01 solo vigila *pérdida* de términos (`UMBRAL_VACIADO`),
así que ampliar un resumen con las palabras del encargo no lo despierta.

```
antes: validación 6/20 (30 %)
resúmenes AMPLIADOS (solo se añade, nunca se quita): 14
después:
  Ajuste ......... 35/50 (70 %)
  Validación ..... 8/20 (40 %)
COSMOS  verde  0 errores
  resúmenes vaciados detectados por P01: 1     ← y ese 1 es un efecto colateral del tope de 120 caracteres
```

P01 no cubre el ataque; caza un daño lateral. **Fix propuesto:** que el canario mire también la
*ganancia* de términos que coinciden con un conjunto de encargos conocido, y —sobre todo— que la
métrica no se publique cuando el holdout ha sido legible por quien edita (R-01).

#### R-17 · La guarda de «examen quemado» falla ABIERTA en clon superficial

`comprobar_procedencia` devuelve `Procedencia(True, …)` incondicionalmente cuando el repo es válido,
**incluso con `blobs_revisados == 0`**, y `limpia` solo exige `comprobada is True and not quemadas`.

```
clon completo   -> comprobada=True limpia=False blobs=17 quemadas=1     correcto
clon --depth 1  -> comprobada=True limpia=True  blobs=7  quemadas=0     FALLA ABIERTA
```

`actions/checkout@v4` clona con `fetch-depth: 1` **por defecto** y el workflow no lo cambia: en CI la
comprobación no ve la historia y devuelve «limpio». Es la regla 14 literal — `AUSENTE == AUSENTE` y
la bandera dice `true` sin haber observado nada.

**Fix propuesto:** `comprobada` trivalente de verdad (`None` cuando `revisados == 0` o cuando
`git rev-parse --is-shallow-repository` sea `true`), publicar `blobs_revisados` y `es_superficial` en
el sello, y `fetch-depth: 0` en los dos `checkout` del workflow.

**Y la hermana, en la misma familia:** `esta_versionado()` **sí** es honestamente trivalente, pero
`cosmos/cli.py` solo mira `is True`, así que su «no lo sé» se consume como «limpio»:

```
esta_versionado(repo, ~/.cosmos/holdout/encargos-validacion.json)  ->  None    ← la ruta POR DEFECTO
esta_versionado(repo, GOAL.md)                                      ->  True
esta_versionado(repo, no-existe.md)                                 ->  False
```

La ruta por defecto está fuera del repositorio, así que `git ls-files` sale con `returncode 128`
(«outside repository») y la función devuelve `None`, correctamente. Es decir: **en la configuración
por defecto —justo la que B-02 instaura— la comprobación “el examen no está versionado” no se
ejecuta nunca de verdad**, y su ausencia no aparece en `motivos_no_publicable()`. Regla 14 del
arnés, literal: si no estabas mirando, dilo. Hoy no lo dice.

#### R-18 · E21 —el guardarraíl que convierte `PUEBLO.md` en estructura— lo satisface la palabra `https://`

`PATRON_URL = re.compile(r"https?://\S+")` aplicado con `search` sobre **todo** el cuerpo. No
comprueba que sea una URL de repositorio, ni que esté en la primera línea, ni que no sea un
marcador, aunque su propio mensaje de error exige las tres cosas.

```
(a) cuerpo sin URL                                                    -> E21 ROJO
(b) mismo cuerpo, cambiando una frase por:
    "Esto fuerza `https://`, y no nombra ningun repositorio…"          -> E21 DESAPARECE
```

**No es teórico: 10 pueblos vivos pasan E21 por accidente** —por `http://localhost`, por
`https://<dominio-cliente`, por una URL de documentación de Microsoft o Google, o por la prosa
«`isSafeHttpsUrl` fuerza `https://`»— y ninguno declara `origen: propio`. Dos de ellos son
exactamente los que C-08 señaló como «pueblos propios mal presentados».

**Fix propuesto:** exigir la URL en la primera línea no vacía, con esquema `https://`, host con
punto y path de al menos dos segmentos, y rechazo de marcadores (`usuario/repo`, `<…>`, `example.*`,
`ejemplo.*`, `localhost`, `127.0.0.1`). Con la meta-prueba (a)/(b) de arriba como test.

#### R-19 · `PROGRESS.md` jura ser generado y está pegado a mano **(del propio fix)**

Cabecera nueva de `PROGRESS.md`: *«Las cifras de abajo no se escriben a mano: son la salida de
`python3 -m cosmos estado`»*. Contra `cosmos estado` de hoy, en el mismo árbol: **10 cifras
divergen** (`pueblo 288 vs 306`, `lluvia 12 vs 14`, `infraestructura 13 vs 17`, `automatizacion 12
vs 14`, `rendimiento 8 vs 11`, `ingenieria-datos 9 vs 11`, `extraccion 8 vs 10`, `saas 9 vs 10`,
`cientifico 7 vs 9`, `visibilidad 7 vs 9`). El propio `FIX.md` dice «247 → **306** pueblos» y
contradice a `PROGRESS.md` sin que medie un commit.

El canario que se le puso (`A12_UnNivelRetiradoNoSeNombraComoVivo`) solo hace `grep ciudad`: **no
vigila ni una cifra**. Es A-01 —el hallazgo que este ciclo cierra con un canario— reencarnado dentro
del arreglo de A-12, y con una frase que hará que el siguiente lector no lo verifique.

**Fix propuesto:** `cosmos estado --markdown` y un canario que reejecute el comando y compare el
bloque, como `LaCabeceraDelIndiceSeCuentaNoSeEscribe` hace con el índice.

#### R-20 · El fix A-11 metió una orden imposible en todos los repos proyectados **(del propio fix)**

`main` decía «desde ahí se desciende.». El fix escribe «desde ahí se desciende **con `cosmos buscar`
y `cosmos abrir`**», y ese océano se inyecta verbatim en el `CLAUDE.md`/`AGENTS.md` de cada repo
ajeno, en la línea 33 de 100, donde `which cosmos` → *not found*. La aclaración que lo desmiente
está 66 líneas más abajo.

Es el enunciado literal de E-01 —el hallazgo que este mismo ciclo declara ARREGLADO— recreado por el
arreglo de otro. El test que lo debería ver (`test_el_bloque_no_manda_ejecutar_un_verbo_que_el_repo_no_tiene`)
solo hace `assertNotIn("rio/")` y corre sobre `arbol_minimo`, un doble sin los océanos reales: el
doble está puesto demasiado adentro.

#### R-21 · El CI pasó de «sin pip, sin red» a instalar un rango abierto **(del propio fix)**

`requirements-dev.txt` entero: `tiktoken>=0.7`. El job `calibracion` lo instala en cada `push` y cada
`pull_request`. La afirmación del informe F («CI correcto… sin `pip`, sin red») era cierta del
workflow anterior y dejó de serlo con este cambio, sin reauditarse. Con `permissions: contents: read`
el daño está acotado, pero es ejecución de código de terceros en el runner, con las transitivas
(`regex`, `requests`) también sin fijar.

**Fix propuesto:** `tiktoken==0.14.0` (la versión que el propio FIX declara haber usado), con
`--require-hashes` y lock generado, y `actions/checkout` pinchado por SHA.

#### R-47 · Cuatro arreglos de P3 no tienen ninguna prueba, y por ahí se coló uno sin hacer

D-01, D-06, D-07 y D-10 se pueden mutar a propósito y **la suite de 320 sigue en `OK`**. No es un
reproche estético: **D-06 se entregó sin arreglar y las 320 pruebas lo firmaron.**

`cosmos/validar.py`:

```python
afirmaciones_segundo = afirmaciones.setdefault(id(segundo), _afirmaciones(segundo))
for palabras_a, texto_a in afirmaciones.setdefault(id(primero), _afirmaciones(primero)):
```

`dict.setdefault(clave, valor)` **no es perezoso**: `_afirmaciones(...)` se ejecuta en cada pareja
aunque la clave ya esté, y el pre-relleno añade N llamadas más sin evitar ninguna. Contadas sobre la
galaxia real:

```
rama:  co-cargables N = 33 · parejas C(N,2) = 528 · llamadas reales a _afirmaciones = 1089   (= 33 + 2×528)
main:                                              llamadas reales a _afirmaciones = 1056
```

**1.056 → 1.089: el «arreglo» hace 33 parseos MÁS que `main`**, contra un informe que pedía bajar de
20.880 a 145. Es la forma más pura del defecto que esta revisión busca: un fix que no arregla nada,
que la verificación declara hecho, y que ninguna prueba mira.

**Fix propuesto:** sustituir los dos `setdefault` por `if clave not in …`, y —lo importante— añadir
las tres pruebas de **conteo de llamadas** que faltan (inmunes a la contención de CPU, dos líneas
cada una en `tests/test_escala.py`). Un arreglo de rendimiento sin conteo de llamadas es una
promesa, no un cambio.

#### R-44 · `cosmos acertar` sale 0 y dice «lo ganado generaliza» sobre un árbol que no existe

Mismo patrón que D-05, un verbo más abajo — y es **el verbo que publica la contra-métrica**:

```
python3 -m cosmos acertar --config <toml con arbol = "no-existe">
  Ajuste ......... 0/50 (0 %; IC95 0–7 %)
  Validación ..... 0/20 (0 %; IC95 0–16 %; n=20)
  Cobertura ...... 0/0 oficios (sin encargo: ninguno)
  Brecha de 0 puntos: lo ganado generaliza.
EXIT=0
```

Hoy queda tapado por otra razón (el holdout está QUEMADO), no por esta guarda. **Fix (1 línea):**
añadir `acertar` —y `abrir`, y `generar`— al conjunto de la guarda de `cosmos/cli.py`, o mejor
subirla justo detrás de `cargar_arbol` para todos los verbos que lo cargan y borrar las dos copias
que quedan en `medir` y `buscar`.

### MEDIOS

#### R-03 · El «clon en frío 8/8» clona `main`, no el árbol arreglado

`CICLO-1/clon-en-frio.sh` hace `git clone --branch arreglos-2026-09-03 $HOME/cosmos`. Esa rama
**no tiene commits**: `git rev-parse arreglos-2026-09-03` = `b0c1ebd` = `main`. Reejecutado hoy tal
cual:

```
paso 1  EXIT=0  /usr/local/bin/python3 -m cosmos arrancar
arrancar: 255 lineas / 21734 bytes
acertar sin holdout … : (nada — el grep de NO DISPONIBLE no encuentra)
8/8 pasos en verde
```

frente a lo que publica `FIX.md`: *«`arrancar` pasó de 262 líneas / ≈9.980 tokens a 10 líneas / 554
bytes»* y *«el paso nuevo `acertar` … dice `NO DISPONIBLE`»*. El 8/8 es real, pero es 8/8 **del
código sin arreglar**.

Hecho el clon en frío **de verdad** (copia → `git add -A` + commit → `git clone`), el árbol arreglado
sí da 8/8, `arrancar` = 9 líneas / 556 bytes y `NO DISPONIBLE` aparece. Es decir: **la conclusión es
correcta y la evidencia publicada no la sostiene** — el comando publicado no reproduce en la máquina
del que lee.

**Fix propuesto:** que el guion clone el árbol de trabajo (`rsync` + `git add -A` en un temporal), o
que el ciclo commitee antes de publicar evidencia de clon.

#### R-15 · `brew install vector` no existe: la instalación de un pueblo nuevo no instala nada

```
$ brew info --json=v2 vector
Error: No available formula with the name "vector". Did you mean pgvector or veccore?
```
`vector` vive en un tap propio del proyecto y la ficha no lo dice.
**Fix:** `brew tap vectordotdev/brew && brew install vector`.

#### R-16 · `butler`: el comando instala otra aplicación

```
$ brew info --json=v2 --cask itch
CASK itch | artifacts: [ {"app":["itch.app"], "target":"/Applications/itch.app"} ]      ← sin stanza `binary`
$ brew info --json=v2 butler
CASK butler | Arrange your tasks in a customisable configuration | manytricks.com/butler/   ← otra herramienta
```
El cask deja `itch.app` y **ningún `butler` en el PATH**; las tres líneas siguientes de la ficha
fallan tal cual se copian. **Fix:** `go install github.com/itchio/butler@latest` + aviso de que
`brew install butler` es otra cosa.

#### R-22 · La vista plana compilada sigue invisible para cualquier runtime: 306 de 306 sin `name`

```bash
tot=0; ok=0; for f in .cosmos/vista-galaxia/*/SKILL.md; do tot=$((tot+1)); head -8 "$f" | grep -q "^name:" && ok=$((ok+1)); done; echo "entradas=$tot con name=$ok"
entradas=306 con name=0
```
`spec/COMPILACION.md` apoya toda su decisión arquitectónica en que ese directorio es «lo que la
plataforma sí descubre». `puente/proyectar.para_el_anfitrion` ya resuelve la traducción; falta
llamarla desde `cosmos/compilar.py`, o denunciarlo con una invariante.

#### R-23 · El contador de contrato de `cosmos estado` se equivoca en las dos direcciones

Es el guardarraíl que sustituye a la parte de `PUEBLO.md` que E21 no bloquea. `PATRON_FECHA` usa un
espacio literal, así que **12 de las 76 fichas «sin fecha de comprobación» sí la tienen** —partida
por un salto de línea— y el trabajo que manda hacer ya está hecho en el 16 % de los casos. Al revés:
`opentofu` sale como «sin rival» diciendo «se elige `opentofu` y **no** `terraform` por la licencia»,
y `nmap` **no** sale pese a no nombrar ninguno (pasa por un «en vez de» que no compara herramientas).

**Fix:** `r"comprobado\s+(?:el\s+)?20\d\d-\d\d-\d\d"`, y exigir que el verbo comparativo vaya seguido
de un identificador entre backticks o en mayúscula.

#### R-24 · `curl | bash` reintroducido en la misma tanda que lo arregló

```bash
grep -rlE 'curl [^\n]*\| *(ba)?sh' galaxia/pueblos/*/SKILL.md
coolify  foundry  nextflow  openclaw  rill
# avisos de tubería a shell:  foundry 1 · openclaw 1 · rill 1 · coolify 0 · nextflow 0
```
F-10 puso el aviso en `foundry` y `rill`. Las dos fichas **nuevas** que introducen el patrón no lo
llevan. Síntoma cerrado, clase abierta, en el mismo árbol.

#### R-25 · Un correo real de un tercero y una IP pública del autor

- `galaxia/pueblos/piper/SKILL.md`: ``voice@` + el dominio de la fundación` — el único correo de dominio real
  de los 306 (los otros 9 son `@ejemplo.test`), y no está en `secretos-conocidos.txt`, así que el
  gate lo marca (R-11).
- `CICLO-1/g3-verif/verif1.txt`, tres veces: la IP pública desde la que se consultó la API de GitHub,
  dentro de un mensaje de rate-limit. Es la única IPv4 no privada ni de documentación del árbol.
  Mismo tipo de dato que hace de F-05 un hallazgo, **introducido hoy**, en la evidencia de este ciclo.

#### R-26 · `mythril` y `medusa` se contradicen sobre el mismo hecho

`mythril` (sin tocar): «último push 2026-04-27 … Cuatro meses sin movimiento: **vivo**».
`medusa` (nueva, al lado): «`mythril` … lleva parado desde 2025-01-31 … **más de un año sin
commits**». El FIX escribió el dato bueno en la ficha nueva y dejó el engañoso en la que se abre
primero.

#### R-27 · `qdrant`: dato de vida con fecha de hoy y contenido de hace un mes

Ficha: `último push 2026-08-04 (comprobado 2026-09-03)`. Real: commit en `master` el **2026-09-03**
a las 11:19Z. Es el único de los 59 con desviación real; los otros 58 coinciden dentro de la deriva
del día. La regla 2 de `PUEBLO.md` («los datos de vida se citan con su fecha») se cumple en la forma
y falla en el fondo: un dato **con** fecha que nace falso engaña más que uno sin ella.

#### R-40 · D-11 cierra la frontera hacia fuera y la deja abierta hacia dentro: un enlace duplica el nodo y la medición

D-11 denuncia el enlace que sale del árbol. El que **no sale** —un enlace dentro de la raíz que
apunta a otro nodo— entra dos veces. Reproducido sobre copia:

```bash
mkdir -p galaxia/pueblos/clon-de-nmap
ln -s ../nmap/SKILL.md galaxia/pueblos/clon-de-nmap/SKILL.md
```
```
antes:   pueblo 306   Peor nicho 2.484 tokens (ciberseguridad, 35 pueblos)
después: pueblo 307   Peor nicho 2.513 tokens (ciberseguridad, 36 pueblos)     ← +29 tok de presupuesto
```

Se pone en rojo, sí, pero **por accidente y señalando al inocente**: sale `E06 pueblos/nmap/SKILL.md:3`
(nombre duplicado entre hermanos) y `E18`, apuntando al fichero **original**. Quien lea el error irá
a `nmap`, que está perfecto. Y el mecanismo que lo caza es la colisión de nombre, no la detección del
enlace: cualquier variante que evite la colisión duplicaría la medición en verde.

*Caso vecino, menor:* un enlace a un **directorio** fuera de la raíz no se recorre (no hay fuga, bien)
pero tampoco se denuncia — `validar` verde, y ni siquiera un pueblo con `padre` inventado dentro de él
dice nada. Es una asimetría de trato, no un agujero.

**Fix propuesto:** comprobar `resolve()` también para los enlaces internos y denunciar el **enlace**,
no la víctima, con un código propio.

#### R-46 · La proyección borra claves anidadas del anfitrión: pérdida de datos en un repo ajeno

`puente/proyectar.py`, `return actual | AJUSTES_CLAUDE`: el `|` de diccionarios es **superficial**.
Cualquier clave del anfitrión dentro de un objeto que COSMOS también declare (`attribution.*`, por
ejemplo) desaparece del `settings.json` de **su** repositorio. Comprobado sobre un anfitrión real:
una clave de primer nivel sobrevive; `attribution.miCampoPropio` **no**.

Es el peor sitio posible para un fallo de este tipo: E-15 se abrió justamente para que la proyección
no pisara lo ajeno, y el arreglo cerró el ruido (no reescribir si no cambia nada) dejando abierta la
pérdida.

**Fix propuesto:** fusión recursiva —
`for k, v in AJUSTES.items(): actual[k] = {**actual.get(k, {}), **v} if isinstance(v, dict) else v`—
y un test con una clave anidada ajena.

#### R-43 · El `utf-8-sig` de D-04 no llega al proyector: un pueblo con BOM se proyecta invisible

El `utf-8-sig` está en **un solo** `read_text`, el del cargador de nodos. `puente/proyectar.py` sigue
leyendo en `utf-8`, así que un pueblo con BOM carga y valida bien dentro de COSMOS **y llega al repo
anfitrión sin `name`/`description` reconocibles**: invisible para Claude Code. Es E-02 otra vez, por
una puerta que D-04 no cerró.

#### R-41 · La caché de D-01 se invalida por el número de nodos, no por el contenido **(del propio fix)**

```python
marca = len(arbol.nodos)
cache = getattr(arbol, "_nichos_cache", None)
if cache is None or cache[0] != marca: ...
```

Cualquier mutación en sitio que conserve el `len` deja la caché obsoleta. Demostrado cambiando un
`sistema-solar` por otro sobre el árbol real (477 nodos antes y después):

```
verdad tiene 'juegos'?  False  | 'oficio-nuevo'? True
CACHE  tiene 'juegos'?  True   | 'oficio-nuevo'? False
=> cache OBSOLETA: True
```

La exposición práctica hoy es **baja** —el árbol se carga una vez, la caché vive en la instancia de
`Arbol` y `Nodo.nombre` es de solo lectura—, y lo digo para no inflar el hallazgo. Lo que sí es
grave es la forma: el propio docstring justifica la clave diciendo que se invalida «si cambia el
número de nodos, que es **lo único que hacen las pruebas** que construyen un árbol a mano». La clave
de una caché se elige por el invariante, no por lo que hacen los tests; y esta alimenta
`catalogo_visible`, `medir_casos` (el presupuesto) y la selección de `compilar`.

**Fix propuesto:** invalidar por una huella del contenido (`hash` de las referencias ordenadas) o,
mejor, calcularlo una vez al terminar la carga y dejar `Arbol.nodos` inmutable.

#### R-42 · `cosmos mapa --help` no avisa del coste, y `FIX.md` dice que sí

```bash
/usr/local/bin/python3 -m cosmos mapa | head -1
COSMOS mapa   (caro: 477 nodos; para navegar usa 'cosmos buscar' y 'cosmos abrir')   ← correcto

/usr/local/bin/python3 -m cosmos mapa --help
usage: cosmos mapa [-h] [--config CONFIG] [raiz]
  raiz             raíz del árbol; por defecto usa cosmos.toml
  -h, --help       show this help message and exit
  --config CONFIG  ruta de cosmos.toml                                              ← ningún aviso
```

`FIX.md` E-10: *«`cosmos mapa` avisa del coste en la primera línea **y en `--help`**»*. La mitad de
la verificación firmada es falsa, y se comprueba en un comando. Es el sitio donde más falta hace:
`--help` es lo que se lee **antes** de pagar el coste; la primera línea, después.

### BAJOS

| ID | Hallazgo |
|---|---|
| R-28 | `FIX.md` §Resumen dice «71 ARREGLADO» y su propia tabla da **74** IDs con componente ARREGLADO. No reconcilia |
| R-29 | Errata introducida por A-07: `spec/MEDIDOR.md` «**los los** mares sumaban 817 tokens» |
| R-30 | Cifra a mano nueva y sin vigilar en el `README.md` («~190 tokens»; medido: 205), en el mismo ciclo que condena A-01 |
| R-31 | El canario de A-01 compara cardinales por **subcadena**: un resumen legítimo como «…hasta entrar en **uno** de sus oficios» lo pondría en rojo sin haber cifra a mano |
| R-32 | El canario de `ciudad` no cubre `galaxia/*.md` (ni el índice generado, que es la línea que se paga siempre) ni los 306 pueblos |
| R-33 | Regla 4 de `PUEBLO.md` incumplida en tres fichas nuevas: `nmap`, `osquery`, `wireshark` no nombran rival. Duele en `nmap`, que es la pieza que justifica C-04 entero |
| R-34 | `osquery` mete SQL en un bloque ` ```bash `: pegado en una terminal falla |
| R-35 | Dos bloques de uso 100 % comentados (`grafana` 7/7 líneas; `vector` 13/15), y `loki` llama a `logcli`, que su propia instalación no instala |
| R-36 | Colisión de nombre sin declarar: `pip install httpx` es `encode/httpx` y `pip install arrow` es `arrow-py`, no los proyectos de las fichas. `medusajs` sí lo declara y sirve de plantilla |
| R-37 | `origen: propio` es un indulto **autodeclarado**: un pueblo sin ningún guion en su directorio pasa `validar` en verde. `spec/PUEBLO.md` define la excepción como «un guion que vive en el directorio del pueblo» |
| R-38 | El plan de purga de `PENDIENTE-DARIO §1` deja el CIF en claro en `$HOME` y nunca lo borra; y `--refs --all` es sintaxis inválida (medido ejecutándolo) |
| R-39 | El nombre de la agencia (`<agencia>_TELEGRAM_USER_ID`) viaja en dos ficheros de producto que este mismo fix tocó, contra GOAL §5 («fuera de cualquier organización») |
| R-45 | Residuo de código muerto que la limpieza de D-09 no vio: `cosmos/medir.py::tokenizador_exacto_disponible()`, cero llamantes en todo el repo. Mismo criterio que D-09: fuera, o que lo use `_seleccionar_contador` |
| R-48 | El hook portable de E-06 **muere en silencio** si falta `CLAUDE_PROJECT_DIR` o si el `python3` del PATH es 3.9 (COSMOS exige 3.11 por `tomllib`). Un guardarraíl que no arranca no avisa de que no arrancó |
| R-49 | Las cifras que `docs/CALIBRACION.md` §«Cerrado» publica como «la medición de hoy» son las de `b0c1ebd`, no las del árbol de la rama: dice 346 tokens libres donde el árbol de hoy da 172 con el tokenizador. Es A-01 otra vez —cifra a mano que envejece— en el documento que sostiene el margen |
| R-50 | `cosmos compilar --detalle` sigue imprimiendo **rutas absolutas** y no existe `--quiet`: dos de los cuatro puntos del fix E-03 no se hicieron, y las rutas absolutas son material para el escáner de secretos (R-11) |

---

## 4. Lo que ningún ángulo anterior cubrió

Los seis fueron: contrato/specs, el juez, la galaxia, el código, el uso real, seguridad. Esto se
quedó fuera de los seis.

### 4.1 · El coste de entrada crece linealmente con el peor nicho: la tesis de GOAL §1 no se cumple

GOAL §1, la frase que sostiene el proyecto entero: *«con contención estricta, el universo puede
crecer sin límite mientras el coste de entrada se queda quieto»*.

Medido, añadiendo pueblos mínimos al peor nicho sobre una copia:

```
nuevos   peor nicho     peor con agua    veredicto
0        2.484 tokens   3.715 tokens     OK, quedan 91 tokens
5        2.622 tokens   3.853 tokens     ROJO, excede en 54 tokens
10       2.760 tokens   3.991 tokens     ROJO, excede en 199 tokens
20       3.036 tokens   4.267 tokens     ROJO, excede en 489 tokens
40       3.588 tokens   4.819 tokens     ROJO, excede en 1.070 tokens
```

**≈27,6 tokens por herramienta, lineal.** La entrada contiene el catálogo **entero** del peor nicho,
así que el coste de entrada es `O(herramientas del oficio más poblado)`. No se queda quieto: crece
con cada alta, y **cinco fichas más en ciberseguridad ponen E16 en rojo**.

Esto no lo introdujo el fixer, pero su tanda lo volvió agudo: consumió el margen hasta 91 tokens
(2,3 % de 4.000, ~3 herramientas), y `FIX.md` presenta «306 pueblos, +59 herramientas» como logro sin
decir que el sistema queda a tres altas del rojo. Con R-05 encima —el margen comprado con el
recorte del océano—, la lectura honesta es: **el presupuesto ya está gastado**, y las 17 retiradas de
`PENDIENTE-DARIO §5` han dejado de ser una decisión de calidad para ser el único camino de vuelta.

**Es un hallazgo de contrato, no de código.** O el catálogo del nicho activo deja de estar en la
entrada (paginado, o solo la provincia que se toca), o GOAL §1 tiene que decir que lo que se queda
quieto es el coste **por oficio**, no el de entrada. Hoy la spec promete una propiedad que el
medidor desmiente.

### 4.2 · El catálogo es de un solo sistema operativo, y no lo declara

```
brew install       93 fichas          apt install     4 fichas
pip install        92 fichas          dnf / pacman    0 fichas
docker run         21 fichas          winget / choco / scoop   0 fichas
go install          8 fichas
```

**64 de 306 fichas (21 %) no ofrecen ningún camino de instalación que no sea Homebrew.** GOAL §1
vende «un repo que se puede clonar sobre cualquier proyecto», el CI corre en `ubuntu-latest`, y
`spec/PUEBLO.md` regla 3 dice «el comando de uso se puede copiar y pegar» **sin acotar sistema**. Un
usuario de Linux que abra `nmap`, `wireshark`, `ffuf`, `httpx` o `hashcat` recibe un comando que no
existe en su máquina. No es un fallo de una ficha: es una **premisa de plataforma no declarada** que
recorre un quinto del producto.

**Fix propuesto:** o declararlo en `spec/PUEBLO.md` («los comandos son de macOS/Homebrew salvo que se
diga otra cosa») —barato y honesto—, o exigir un segundo camino en las fichas donde el proyecto
publique binario o paquete.

### 4.3 · `cosecha/` duplica 76 de sus 80 ficheros dentro de la galaxia, y no la nombra ninguna spec

```
duplicados byte a byte entre cosecha/ y galaxia/ ....... 76 de 80
grep -rn "cosecha" README.md GOAL.md spec/*.md ......... sin salida
git ls-files cosecha | wc -l ........................... 80   (viaja en el repo)
```

GOAL: *«Una herramienta vive en **un solo sitio**: cero repetidos es regla dura.»* El informe C
comprobó pueblos repetidos —y no hay ninguno—, pero nadie comprobó **ficheros** repetidos. Cada
herramienta propia viaja dos veces, y `cosecha/` no está documentada en ninguna parte del contrato.

No es cosmético: `FIX.md` dice, literalmente, «`telegram-bridge.py` (**×2**)». La corrección de
seguridad F-08 hubo que aplicarla dos veces **por esta duplicación**, y el sub-revisor de seguridad
encontró que la segunda mitad (`set <agencia>_TELEGRAM_USER_ID=…`) quedó sin corregir. La próxima
vez alguien arreglará solo una copia.

**Fix propuesto:** decidir qué es `cosecha/` —cantera temporal o parte del producto— y, si es lo
primero, sacarla del repo o al `.gitignore`; si es lo segundo, documentarla en una spec y hacer que
los pueblos la referencien en vez de copiarla.

### 4.4 · La cadena de evidencia del propio informe no se auditó a sí misma

Tres de los hallazgos de arriba (R-03, R-11, R-19) tienen la misma forma: **el número publicado es
correcto y el instrumento que lo produjo no mide lo que se dice.** El guion de clon en frío clona la
rama sin commits; `git grep` no ve los ficheros sin trackear; `PROGRESS.md` afirma ser generado y
está pegado. Ninguno de los seis ángulos tenía como encargo auditar la evidencia del ciclo, porque
el ciclo aún no existía.

**Recomendación de proceso:** que todo FIX incluya, como parte obligatoria del bloque de
verificación, los dos controles que hoy faltan (`puente.secretos --todo`, `puente.gate
--sin-pruebas`), y que cualquier evidencia de «clon» o de «cero ocurrencias» se produzca sobre el
árbol que de verdad se va a mergear.

### 4.5 · Lo que intenté tumbar y aguantó

Se dice, porque cuenta tanto como lo que cayó:

- **Meta-prueba propia: 11 mutaciones de 11 aplicables, cazadas.** Rompí a propósito el validador
  (`valido` → `True`; E21 fuera de la lista; E07 sin comprobar), el medidor (`MARGEN_ERROR = 0`;
  veredicto siempre «cabe»; contador a la mitad; peor caso sin publicar), el juez (`_acierta` →
  `True`; `BRECHA_ALARMA = −1000`; `publicable` → `True`), la procedencia (nunca encuentra el examen
  quemado) y el canario P01 (eliminado). **Las once pusieron la suite en `FAILED`.** Estas guardas
  no son decorativas: se las ha visto fallar.
- **Determinismo e idempotencia:** `cosmos generar` da el mismo `sha256` con `LC_ALL=C` y con
  `PYTHONHASHSEED=1`; `cosmos arrancar` dos veces seguidas deja el mismo manifiesto.
- **Los arreglos de rendimiento que sí lo son, medidos y no creídos:** D-01 hace desaparecer el
  cúbico y la caché **no cambia el resultado** (comprobado envenenándola entre dos árboles del mismo
  proceso); D-07 da la misma salida línea a línea **24× más rápido**. Y D-11 cierra la frontera hacia
  fuera en los tres casos que probé además del citado (absoluto, relativo `../`, roto).
- **El no-op de E-15 es byte a byte**: una segunda sincronización sin cambios deja el mismo `sha256`
  del `settings.json` del anfitrión, y un fichero corrupto no se pisa (`EXIT=1` con mensaje).
- **La guarda de raíz inexistente cubre siete verbos**, no los dos que el fix menciona.
- **El margen de calibración es conservador**: aprox 3.715 × 1,052 = 3.909 ≥ exacto 3.828
  (`tiktoken/cl100k_base`). Intenté que el margen se quedara corto y no pude.
- **Contención y duplicados de la galaxia:** 306 pueblos, `padre:` existente en los 306, **cero
  huérfanos**, **cero repetidos** por nombre y por slug de repositorio (294 slugs distintos), **cero
  destinos `usa:` inexistentes**, ningún ciclo nuevo.
- **Las 59 herramientas existen**: 59/59 HTTP 200, estrellas y `último push` verificados contra
  `github.com` uno a uno. **Ninguna URL inventada, ningún repositorio fantasma.** Los homónimos que
  yo daba por sospechosos (`httpx`, `medusa`, `just`, `arrow`, `piper`) están **bien resueltos** en
  el comando; los dos rotos (`vector`, `butler`) no estaban en mi lista.
- **El holdout no se tocó**, y está probado con huellas, no con la palabra del fixer: `sha256
  c6e0d3a1…` idéntico al del sello de 2026-09-02 y a `main:pruebas/encargos-validacion.json`.
  De 404 resúmenes de `main` cambió **uno**, y para quitar contenido.
- Una hipótesis mía era falsa y lo digo: creí que B-08 (puntuar la línea literal) había degradado
  `buscar`. Medido sobre los 50 encargos de ajuste: línea literal **37/50** frente a línea+ruta
  **35/50**. La hipótesis no se sostiene.

---

## 5. Veredicto final

### ¿Se puede mergear a `main` tal como está? **No.**

Tres bloqueantes, en orden:

1. **R-11 — el árbol no pasa sus propios controles.** `puente.gate --sin-pruebas` y
   `puente.secretos --todo` salen **EXIT 1** sobre este árbol estadificado, y el workflow corre los
   dos. El primer push es rojo. Además, 43 rutas de la máquina personal y una IP pública están en
   ficheros que no están trackeados **ni ignorados**: quien teclee `git add -A` las commitea.
   *Coste de arreglo: minutos.* Es la condición mínima para que un merge sea siquiera posible.
2. **R-01 — la métrica de calidad del producto es amañable hasta el 100 %.** Mergear tal cual
   consolida un `acertar` que publica «la cifra que vale es 100 %» sobre un examen que escribe el
   examinando. Mientras no haya compromiso previo verificable, el comando **no debería decir «la
   cifra que vale»** ni ofrecer `--minimo`. *Coste de la mitigación honesta: una condición y un
   cambio de texto.*
3. **R-05 + §4.1 — el presupuesto está en verde por 91 tokens comprados con un recorte, y el modelo
   de coste crece linealmente.** No es un bug que bloquee un merge por sí solo, pero **`FIX.md` no
   puede publicar «OK, quedan 91 tokens» sin decir que el OK depende de haber borrado 109 tokens de
   océano**, ni «+59 herramientas» sin decir que queda sitio para tres.

**Lo que recomiendo cerrar también antes del merge, aunque no bloquee por sí solo:**

- **R-47 / D-06** — un arreglo declarado hecho que **empeora** lo que había (1.056 → 1.089 parseos),
  firmado por las 320 pruebas. Corregir el `setdefault` es una línea; lo importante es añadir las
  tres pruebas de conteo de llamadas que faltan, porque el problema real es que **cuatro arreglos de
  P3 no tienen ninguna prueba**.
- **R-15 y R-16** — dos comandos de instalación que no instalan la herramienta (`vector` no existe en
  Homebrew; `--cask itch` no deja `butler`). Es el tipo de fallo que destruye la credibilidad de un
  catálogo entero, y son dos líneas.
- **R-06** — tres líneas, y es el mensaje que lee quien tiene que arreglar el rojo del presupuesto.
- **R-46** — pérdida de una clave anidada en el `settings.json` de un repo **ajeno**. Es el único
  hallazgo que daña datos de un tercero.

Lo demás (R-08, R-09, R-17…R-50) es deuda arreglable que no impide mergear una vez cerrado lo de
arriba, pero R-08 y R-09 deberían entrar en el mismo ciclo que R-01: son las otras dos puertas del
mismo cuarto.

### La nota que yo defendería

**El trabajo del fixer: 7,0 / 10.** Método, para que se pueda discutir:

| Eje | Peso | Nota | Por qué |
|---|---|---|---|
| Lo que dijo que hizo, ¿lo hizo? | 30 % | **7** | 38 CONFIRMADAS, 34 PARCIALES, 3 DESMENTIDAS sobre 75 filas. Poco más de la mitad se sostiene entera; las parciales casi siempre son «arregló el síntoma citado, no la clase» |
| Honestidad de la báscula | 25 % | **9** | Aquí está lo mejor del ciclo, y con diferencia. Dejó que la nota bajara, retiró el 75 %, retiró el 40 %, publicó «DESCONOCIDA», y el holdout está intacto **con huella verificable**, no de palabra. Es lo difícil y lo hizo |
| Robustez de lo arreglado | 20 % | **5** | Las guardas existen y se las ve fallar (11/11 en mi meta-prueba), pero **cuatro palancas de amaño siguen abiertas**, cuatro arreglos no tienen prueba —y por ahí se coló **D-06**, entregado sin hacer y firmado por las 320— y cinco fixes crearon defecto nuevo (R-06, R-19, R-20, R-43, R-46) |
| Calidad del catálogo | 15 % | **8** | 59/59 herramientas reales, cero repetidos, cero huérfanos, contrato mecánico 8/8 en las nuevas. Dos comandos rotos y una fecha falsa lo bajan |
| Evidencia y trazabilidad | 10 % | **4** | El clon en frío mide el código viejo, `git grep` mide donde no está el problema, `PROGRESS.md` jura ser generado y no lo es, las cifras de `CALIBRACION.md` son de otro árbol, y el bloque de verificación omite los dos controles que se ponen rojos |

**El sistema COSMOS en sí, hoy: 6 / 10.** Que es distinto de la nota del fixer, y hay que separarlo.
La arquitectura de carga perezosa funciona y está medida; el validador tiene 21 invariantes que se
han visto fallar; el catálogo tiene 306 herramientas reales, sin huérfanos ni repetidos, con un
contrato que ya se comprueba. Lo que le falta para más nota no es pulido: es que **su métrica de
acierto no resiste a quien quiera subirla** (R-01, R-02, R-09, R-14), que **su tesis central sobre el
coste de entrada no la cumple su propio medidor** (§4.1), y que **la cifra honesta de si el árbol
lleva a la herramienta correcta sigue siendo, con razón, `DESCONOCIDA`**.

Esa última frase es, a la vez, el mayor mérito del ciclo y el motivo de la nota: el sistema ya sabe
decir que no sabe. Lo que todavía no sabe es impedir que alguien le haga decir que sí.

---

*Revisión adversarial única y final · 2026-09-03 · sobre el árbol de trabajo de `b0c1ebd`
(rama `arreglos-2026-09-03`, 197 rutas sucias, sin commits) · solo lectura sobre `~/cosmos` salvo
este fichero · experimentos en `…/scratchpad/rev/`.*
