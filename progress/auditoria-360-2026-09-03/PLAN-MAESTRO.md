# PLAN MAESTRO — Auditoría 360 de COSMOS · 2026-09-03

**Encargo de Darío:** *"el arnés siempre lo hemos estado puntuando desde el mismo ángulo … que sea
un 10 … QUIERO 0 FALLOS Y TODAS LAS MEJORAS QUE SE PUEDAN"*. Seis revisores Opus barrieron el repo
entero, cada uno desde un ángulo distinto y sin hablarse.

**Resultado: 80 hallazgos, 13 críticos.**

Y el hallazgo que cambia todo lo demás: **el instrumento con el que COSMOS se ponía nota no sirve.**
El juez sube de 40 % a 100 % sin que el sistema mejore nada, con todas las puertas en verde (B-01);
el examen está en claro dentro del repo (B-02); y la única guarda anti-Goodhart vigila el lado
equivocado y felicita al tramposo (B-03). El 75 % que dábamos por bueno es **una cifra retirada:
conjunto quemado**. Nota defendible hoy: **acierto 40 %** (IC95 22-61, n=20), sistema de evaluación
**6/10**.

Por eso el orden de este plan no es por gravedad: **primero se arregla la báscula, luego se pesa.**

## Estado auditado

```
git -C ~/cosmos rev-parse HEAD   -> b0c1ebd (main)
git -C ~/cosmos status --porcelain -> limpio salvo los informes de esta auditoría
```

| Informe | Ángulo | Hallazgos |
|---|---|---|
| `A-contrato.md` | ¿el código hace lo que las specs dicen? | 14 (4 críticos) |
| `B-juez.md` | ¿la nota es honesta? | 10 (3 críticos) |
| `C-galaxia.md` | ¿las herramientas son las mejores, y qué falta? | 17 · 17 a retirar, **24 a añadir** |
| `D-codigo.md` | el paquete `cosmos/` como software | 11 (3 críticos) |
| `E-uso.md` | clon en frío y proyección sobre otro proyecto | 16 (2 críticos) |
| `F-seguridad.md` | secretos, licencias, honestidad del registro | 12 (1 crítico) · 5 afirmaciones desmentidas |

Los informes son **evidencia: se leen, NO se editan**.

---

## 1. Reglas de aplicación

### 1.1 Dónde se trabaja

Rama nueva desde `main`: `git -C ~/cosmos switch -c arreglos-2026-09-03`. **Nada de commits en
`main`, nada de `push`, nada de reescribir historia** (`filter-repo`, `rebase -i`, `--force`). El
merge a `main` y el push los hace el orquestador al final, cuando el revisor dé el visto bueno.

`trash`, nunca `rm` (orden de Darío). Cero dinero, cero correo, cero buzones. La evaluación por API
está aparcada por decisión suya: no se contrata nada.

### 1.2 La trampa de este lote: arreglar el juez NO es subir la nota

Es la regla más importante del plan. B-01 demuestra que se puede llevar el acierto de 40 % a 100 %
sin mejorar nada. **Está terminantemente prohibido tocar el corpus, los resúmenes, el holdout o el
formato del catálogo con el efecto de subir la cifra.**

El trabajo es el contrario: hacer el instrumento **incorruptible** — sellar el examen de verdad,
poner la guarda anti-Goodhart donde toca, separar quien escribe el holdout de quien ajusta el árbol,
publicar el intervalo de confianza y el `n`. Si al terminar la nota **baja**, el trabajo está bien
hecho. Una báscula honesta que marca 40 vale infinitamente más que una amañada que marca 100.

Solo **después**, y como trabajo aparte y declarado, se mejora la búsqueda para que el número suba
por la vía legítima (E-12: `buscar` acierta 2 de cada 5 y falla entero en "auditar la seguridad de
una web").

### 1.3 «Lo que falta también es un fallo»

Lo dice el GOAL y es la mitad del valor de esta auditoría. El listón es **el harness más completo que
exista**, no el más barato: no se busca coste mínimo sino **cero coste innecesario**. Las 24
herramientas que C propone añadir (empezando por que `ciberseguridad` es el nicho más grande y **no
tiene `nmap`**) son tan obligatorias como cerrar un bug.

Al añadir: cada herramienta se verifica viva (repo existe, commit reciente, no archivado), se le
escribe ficha con **invocación ejecutable** (`spec/PUEBLO.md`), y se respeta la regla dura de cero
repetidos y el presupuesto medido con `cosmos medir` — no con un número copiado a mano.

### 1.4 La máquina objetivo es un M3 Pro de 18 GB

Ya lo pidió Darío el 2026-09-02 (*"lo de los recursos quítalo del arnés si puedes"*) y lo repite hoy.
**C-10: 24 fichas eligen herramienta por las restricciones de una máquina pequeña** — esa deuda se
retira. Pero cuidado con la distinción: se relaja lo que limitaba la RAM, **no** lo que limita el
coste en tokens del contexto, que es el proyecto entero.

### 1.5 Verificación — sin ella el fix no cuenta

Después de cada bloque: `python3 -m cosmos validar` en verde, la suite de tests entera, y la medición
antes/después pegada. Comando copiable + salida real, **nombrando el intérprete** (`python` a secas
puede resolver a otro y falsear el resultado). Un "arreglado" sin prueba se reporta `NO VERIFICADO`.

Ojo con **D-02**: hoy los tests escriben en el repositorio real y filtran estado. Arregla eso pronto,
o tus propias verificaciones ensuciarán el árbol que estás midiendo.

---

## 2. Los 80 hallazgos, por orden de ataque

### P0 — La báscula (sin esto, ninguna otra medición vale)

| ID | Gravedad | Hallazgo |
|---|---|---|
| B-01 | CRÍTICO | La nota sube de 40 % a 100 % sin mejorar nada, con todas las puertas en verde |
| B-02 | CRÍTICO | El sello no sella: el examen está en claro dentro del repo |
| B-03 | CRÍTICO | La única guarda anti-Goodhart vigila el lado equivocado y felicita al tramposo |
| B-04 | GRAVE | La regla de corrección no está guardada: aflojarla sube la nota con la suite verde |
| B-05 | GRAVE | El holdout lo escribió quien ajusta el árbol, con el árbol delante |
| B-06 | GRAVE | n=20: publicar «40 %» ya es precisión falsa. Publicar IC y `n` |
| B-07 | GRAVE | El aviso de sello roto y el veredicto se contradicen en la misma salida |
| B-08 | MEDIO | La cifra se mueve 10 puntos según una decisión de modelado que nadie ha fijado |
| B-09 | MEDIO | El holdout no cubre el árbol entero |
| B-10 / D-08 / E-07 | MEDIO | Las pruebas que verifican el medidor no se ejecutan en esta máquina; el margen ±5,2 % no se verifica en ninguna instalación por defecto |
| D-03 | CRÍTICO | **E16 convierte «no medido» en un número y publica una frase falsa** — la regla de oro del repo, rota por su validador |
| A-10 | MEDIO | El medidor publica ±5 % sobre una heurística cuyo peor caso calibrado es 33,6 %, que no publica |
| A-07 | ALTO | Cifras petrificadas fuera del canario, incluidas dos que el canario presume de haber arreglado |
| F-01 | CRÍTICO | La lista de excepciones del escáner blanquea *(fichero × clase)* para siempre — se calló al escáner en el commit que presumía de enseñarle |

### P1 — El contrato: el producto no hace lo que promete

| ID | Gravedad | Hallazgo |
|---|---|---|
| A-01 | CRÍTICO | El índice generado —el artefacto que «no puede mentir»— miente en la primera línea que se paga |
| A-02 | CRÍTICO | «Coste en runtime: Cero» es falso, y el comando de arranque documentado materializa el peor caso |
| A-03 | CRÍTICO | Con el `GOAL.md` de hoy, ninguna pieza del repo puede estar terminada |
| A-04 | CRÍTICO | `nichos=None` significa dos cosas opuestas en la misma spec, y `cosmos.toml` documenta la equivocada |
| E-02 | CRÍTICO | Los 22 pueblos proyectados son invisibles para Claude Code, y `comprobar` da verde |
| E-01 | CRÍTICO | El repo proyectado recibe instrucciones para un comando que no tiene |
| E-04 | ALTO | El mecanismo que cumple el GOAL no está documentado ni es un verbo |
| A-05 / A-08 | ALTO | `spec/VALIDADOR.md`: documenta 16 invariantes y hay 20; describe una E16 que el código no implementa y una clave que no existe |
| A-06 | ALTO | `spec/PUEBLO.md` es normativo y no lo comprueba nadie: 28 de 247 pueblos no nombran qué ejecutar |
| A-09 | ALTO | El README enuncia el principio rector **en la versión que Darío corrigió** |
| A-11 | MEDIO | `oceano/descender`: 144 tok/sesión de exhortación contra algo que la estructura ya impide |
| A-12 / A-13 | MEDIO | `PROGRESS.md` (designado «el estado real») caducado y cita un nivel retirado · `NUCLEO.md` delega en `cosmos estado` algo que no responde |
| E-05 | MEDIO | El README documenta el mantenimiento, no el uso |
| E-08 | MEDIO | `arrancar` no deja un árbol nuevo en verde, contra lo que promete la spec |
| E-13 / E-14 | MEDIO | `abrir` describe a los hijos en unos niveles y no en otros · `usa:` es invisible para quien navega |
| E-16 / F-07 | BAJO | El índice inyectado en cada sesión dice «Veintiún oficios» y hay 22 |
| A-14 | BAJO | El registro tiene la forma que promete y ninguna de sus dos ventajas |

### P2 — Legal y seguridad (parte necesita el OK de Darío)

| ID | Gravedad | Hallazgo |
|---|---|---|
| F-03 | ALTO | **1.400+ líneas de código ajeno redistribuidas sin licencia, sin autor y sin URL** |
| F-04 | MEDIO | El repo no declara licencia propia |
| F-08 | MEDIO | Se cataloga un guion que lanza un agente con `--dangerously-skip-permissions` sin advertirlo |
| F-06 | MEDIO | Un test escribe un salto REAL de E16 en el repositorio real y con concurrencia no lo limpia |
| F-10 | BAJO | Dos fichas publican `curl \| bash` sin el aviso que sí lleva una tercera |
| F-09 | BAJO | `--no-verify` salta el gate entero (compensado por CI) |
| F-11 | BAJO | 64 rutas absolutas del Mac de Darío; el escáner no tiene patrón para ellas |
| F-12 | BAJO | La reescritura de historia no está registrada y sus respaldos siguen vivos |

### P3 — El código

| ID | Gravedad | Hallazgo |
|---|---|---|
| D-01 | CRÍTICO | `medir_casos` es cúbico: 0,07 s una medición, **589 s todas** |
| D-02 | CRÍTICO | Los tests escriben en el repositorio real y filtran estado |
| D-04 | MEDIO | Un BOM hace desaparecer un nodo en silencio, y culpa a un fichero inocente |
| D-05 | MEDIO | `estado` y `mapa` dan verde sobre una raíz que no existe |
| D-06 / D-07 | MEDIO | E17 recalcula por pareja · `generar_mapa` recorre todos los nodos por cada nodo |
| E-03 / E-10 | MEDIO | `arrancar`/`compilar` son lo más caro y también cuando no cambian nada · `cosmos mapa` cuesta más que el recorrido entero y no avisa |
| D-09 | BAJO | `formatear_medicion` y `medicion_json`: código muerto que solo mantienen sus tests |
| D-10 / D-11 | BAJO | Rutas de error mezclan absoluta y relativa · symlinks de fuera del árbol se cargan como nodos |
| E-09 / E-11 | BAJO | Mensaje de E16 sin sentido en árbol vacío · `docs/CALIBRACION.md` dice rojo donde ya hay verde |
| E-06 | MEDIO | `enganchar --sesion` escribe rutas absolutas en un fichero versionable |
| E-15 | BAJO | La proyección reordena `.claude/settings.json` del repo ajeno sin añadir nada |

### P4 — La galaxia: lo que falta (la mitad del valor)

| ID | Gravedad | Hallazgo |
|---|---|---|
| C-04 | ALTO | `ciberseguridad` es el nicho más grande de la galaxia y **no tiene `nmap`** |
| C-01 | ALTO | `agentes-ia` no es el oficio que declara: es «operar Claude Code» |
| C-02 | ALTO | `web/construccion-de-sitios`: 7 de 7 WordPress, cero frameworks |
| C-03 | ALTO | `infraestructura` sin infraestructura como código |
| C-05 | ALTO | `rendimiento` promete «memoria» y no trae un perfilador de memoria |
| C-06 | MEDIO-ALTO | Herramientas de propósito general encerradas en un nicho, inalcanzables desde donde hacen falta |
| C-10 | MEDIO | **24 fichas eligen por las restricciones de una sola máquina** (deuda del Mac viejo: retirar) |
| C-07 / C-09 / C-12 / C-14 | MEDIO | Repos parados, abandonados, con organización cambiada o con marcador 404 |
| C-08 | MEDIO | `visibilidad`: 3 de 7 no son herramientas que se ejecuten |
| C-11 | MEDIO | `analitica/cuadros-de-mando`: 5 herramientas y ninguna es una plataforma de BI |
| C-13 / C-15 / C-16 / C-17 | BAJO | Contrato de `spec/PUEBLO.md` incumplido en parte · `juegos` promete lo que no trae · `usa:` incompleto · dos pueblos dependen de un servicio con cuenta |
| **C · LO QUE FALTA** | — | **24 herramientas a añadir y 17 a retirar o degradar**: la lista literal está en `C-galaxia.md` |

### Requiere decisión de Darío — se deja preparado, no se aplica

| ID | Por qué |
|---|---|
| F-02 | Un **CIF español auténtico** vivo en la historia publicada, incluida `historia-limpia`. Quitarlo de la historia es reescribirla: prohibido sin su orden. Alternativa sin reescribir: valorar si el dato es sensible y de quién |
| F-05 | Volcado con datos de terceros borrado del árbol y **vivo en `origin/main`**: mismo caso |
| F-04 | Qué licencia lleva COSMOS es decisión suya (y condiciona F-03) |
| F-03 | La atribución se puede escribir hoy; **retirar** código ajeno o cambiar su licencia es decisión suya |
| C · retiradas | Retirar 17 herramientas cambia el contenido del producto: se propone con motivo, y se archiva, nunca se borra |

---

## 3. Entregable del fixer

`~/cosmos/progress/auditoria-360-2026-09-03/CICLO-1/FIX.md`:

1. Cabecera: rama, pin inicial y final, entorno (intérprete exacto).
2. **Tabla de los 80**, ninguno omitido: `ID | estado | qué se hizo | verificación`. Estados:
   `ARREGLADO` · `NO APLICA (y por qué)` · `PENDIENTE-DARIO` · `NO VERIFICADO`.
3. Por cada arreglado: comando copiable y salida real, antes y después.
4. **La nota, medida con el juez ya arreglado**, con su `n` y su intervalo. Si baja respecto al 40 %,
   se dice. Bajar con la báscula honesta es un resultado, no un fracaso.
5. `PENDIENTE-DARIO.md` aparte, con los diffs listos y el riesgo de cada uno en una línea.
6. **Regresiones**: `cosmos validar` verde, suite entera, y que el clon en frío siga funcionando
   (hoy: 8/8 pasos en 4,28 s — si tras tus cambios tarda más o falla un paso, lo has roto).

Una sola línea en el chat al terminar.
