# B — Coherencia de todo el harness (revisión adversarial)

**Pin del árbol auditado**

| Dato | Valor |
|---|---|
| `git rev-parse HEAD` | `892f669e70ed1b47f45a311ef5578a00e1593f01` |
| `git status --porcelain \| wc -l` | `0` (limpio al empezar; el único fichero escrito es este entregable) |
| Rama | `main` |
| Fecha de la revisión | 2026-09-04 |
| Intérprete | `python3` = `/usr/local/bin/python3`, **Python 3.14.3** (ver §9) |

Premisa: **el repositorio está incoherente y mi trabajo es demostrarlo**. Todo hallazgo lleva
fichero, cita literal y arreglo. Severidades: **CRÍTICO** (roto o miente) · **ALTO** (incoherencia
visible) · **MEDIO** · **BAJO**.

## 0. Resultado en una tabla

**38 hallazgos: 2 CRÍTICO · 13 ALTO · 17 MEDIO · 6 BAJO.**

| Lo que no aguanta | id |
|---|---|
| La suite del núcleo está **roja en `main`** y el CI con ella | B-01 |
| `mutaciones` da **76/79** donde el cierre publica 79/79, y el CI no la ejecuta | B-02, B-03 |
| El bloque de ejemplo de `spec/MEDIDOR.md` **no se reproduce** aunque la spec jura que sí | B-04 |
| `GOAL.md` declara un nivel `Universo` que el código no reconoce | B-12 |
| `cosmos enganchar` instala un **pre-push** que no aparece en ninguna spec ni en el README | B-16 |
| El ejemplo de `cosmos abrir --help` **falla** al copiarlo | B-28 |
| `E20` está viva y **ninguna prueba la ve en rojo**, contra lo que exige `VALIDADOR.md` | B-07 |
| El `resumen` de `butler` nombra una provincia retirada ayer | B-18 |
| Once nodos del producto dicen «esta casa», «este arnés» o «este Mac» | B-24 |
| `CIERRE.md` escribe «verde» a secas habiendo dos saltos activos — la mentira que el sistema existe para impedir | B-27 |
| `configurar` es el único verbo sin río: no se puede encontrar | B-05 |
| `PLAN-MAESTRO.md` (raíz, versionado) describe nueve oficios que ya no existen, sin decir que es histórico | B-22 |

**Lo que intenté tumbar y aguantó**: la taxonomía (0 nodos con hijo único, 0 resúmenes largos, 0
huérfanos, E21 al 100 % en 297 pueblos), las cifras de `PROGRESS.md` frente a `cosmos estado`, los
datos de vida de 10 fichas contra la API de GitHub, la limpieza de datos de agencia/cliente/máquina
en el producto, y la honestidad del medidor y del juez cuando les falta una pieza. Detalle en §5, §6
y §9.

---

---

## 1. Texto vs código

### B-01 · CRÍTICO · La suite del núcleo está EN ROJO en `main`

`CIERRE.md` de la auditoría de ayer publica esta fila:

> `| python3 -m unittest discover -s tests | Ran 359 · OK (2 saltos: comparativas que exigen el tokenizador exacto local) |`
> — `progress/auditoria-360-2026-09-03/CIERRE.md:14`

Medido hoy sobre `892f669`:

```
Ran 359 tests in 75.119s
FAILED (failures=1, skipped=2)      # EXIT=1
```

```
FAIL: test_el_sello_v1_esta_comprometido_desde_2026_09_02
  (tests.test_juez_honesto.ElCompromisoSeLeeDeLaHistoriaNoDelSello)
  File "tests/test_juez_honesto.py", line 462
    self.assertEqual(c.resumenes_cambiados_despues, 0)
AssertionError: 37 != 0
```

Causa: la medición del CIERRE se hizo en la rama `arreglos-2026-09-03`; al mergear a `main`
(`c6d13e9` + `892f669`, ambos con fecha **2026-09-04 08:19/08:21**) entraron commits que cambian
37 resúmenes **posteriores** al commit del sello v1. El test lee la historia git real, así que la
propia integración lo puso rojo y nadie volvió a correrlo.

Consecuencia en cadena: **el workflow de CI también está rojo** — `.github/workflows/cosmos.yml`
hace `fetch-depth: 0` precisamente para que estos tests vean la historia, y luego ejecuta
`python3 -m unittest discover -s tests -t .`.

*Arreglo*: el test afirma «el sello v1 no se ha tocado desde que se selló», pero mide «nadie ha
cambiado ningún resumen desde entonces», que es otra cosa y caduca con el primer commit. Reescribir
la aserción a lo que de verdad quiere vigilar (que el examen v1 está QUEMADO y por eso su nota no
se publica) o convertir `resumenes_cambiados_despues` en un dato informativo del veredicto en vez
de una aserción de igualdad a 0. Mientras no se arregle, `main` no compila el gate ni el CI.

### B-02 · CRÍTICO · `mutaciones.py` publica 76/79, el CIERRE dice 79/79

> `| python3 puente/tests/mutaciones.py | 79/79 invariantes vistas fallar |`
> — `progress/auditoria-360-2026-09-03/CIERRE.md:18`

> `Suite: … mutaciones python3 -m puente.tests.mutaciones (todas vistas fallar).`
> — `PROGRESS.md:20-21`

Medido hoy (EXIT=1):

```
M63 cosmos/cli.py:     VERDE (la prueba no vigila nada) — B-02: sin mirar la historia git, un examen que ya estuvo en el repositorio se da por ciego
M64 cosmos/cli.py:     VERDE (la prueba no vigila nada) — B-02: un holdout versionado en el propio repositorio se aceptaba como examen
M76 cosmos/holdout.py: VERDE (la prueba no vigila nada) — R-17: en un clon superficial la comprobacion de examen quemado decia «limpia» sin haber visto la historia
76/79 invariantes vistas fallar
```

Las tres supervivientes son exactamente las del **holdout**: sin `pruebas/encargos-validacion.json`
en disco (gitignored, vive en `~/.cosmos/holdout/`) las pruebas que deberían cazar la mutación no
llegan a ejecutarse, así que la mutación pasa. Es el antipatrón que el propio repo denuncia: *«un
validador que nunca ha dicho rojo no se distingue de uno roto»* (`README.md:151`).

*Arreglo*: (a) corregir la cifra en `CIERRE.md` y `PROGRESS.md`; (b) que M63/M64/M76 construyan su
propio holdout de juguete en un `TemporaryDirectory` en vez de depender de un fichero que el repo
prohíbe versionar, para que la mutación se vea fallar siempre.

### B-03 · ALTO · El CI no ejecuta las mutaciones

`.github/workflows/cosmos.yml` corre `arrancar`, `validar`, `medir`, `secretos --todo`, las dos
suites, `puente.gate --sin-pruebas` y el manejador de sesión. **No hay ningún paso que ejecute
`python3 -m puente.tests.mutaciones`**, que es la pieza que el README vende como la garantía del
sistema:

> «un validador que nunca ha dicho rojo no se distingue de uno roto; por eso hay un test por
> invariante que lo ve fallar a propósito» — `README.md:151-152`

Por eso B-02 pudo degradarse de 79/79 a 76/79 sin que nada se pusiera rojo.

*Arreglo*: añadir un paso al job `verificar`:

```yaml
      - name: Cada invariante se ve fallar a propósito
        run: python3 -m puente.tests.mutaciones
```

(ya devuelve exit≠0 al no llegar a 79/79, así que basta con invocarlo).

### B-04 · ALTO · El bloque de ejemplo de `spec/MEDIDOR.md` NO se reproduce, y la spec promete que sí

`spec/MEDIDOR.md:100-103` es explícito, y hasta cita el hallazgo que quiere evitar:

> «El ejemplo es el árbol de juguete versionado (`cosmos medir --config ejemplo.toml`), no la
> galaxia: un bloque copiado a mano de un árbol que crece envejece en silencio a los cinco minutos
> —es H11, y el parte de F12 lo repitió—. **Este se reproduce entero con ese comando**»

Ejecutado hoy `python3 -m cosmos medir --config ejemplo.toml`, siete cifras y dos filas enteras no
coinciden:

| Campo | `spec/MEDIDOR.md` | Salida real |
|---|---|---|
| Entrada base | `114 tokens` | `134 tokens` |
| Peor nicho | `183 tokens` | `203 tokens` |
| Peor con agua | `214 tokens` | `234 tokens` |
| Universo | `354 tokens` | `440 tokens` |
| Descarga | `48,3 %` | `53,9 %` |
| Presupuesto | `quedan 3774 tokens …` | `quedan 3753 tokens …; ≈ 129 herramienta(s) más en ese nicho` |
| índice de galaxia | `55 tok` | `75 tok` |
| `Nicho activo ....` | *ausente* | presente |
| `Vista compilada .` | *ausente* | presente |

Es literalmente el fallo H11 que el párrafo dice haber curado. *Arreglo*: pegar la salida de hoy y
añadir a `tests/test_cifras_de_las_specs.py` un canario que ejecute el comando y compare el bloque
—exactamente como `tests/test_progress_generado.py` hace con `cosmos estado`.

### B-05 · ALTO · `configurar` es un verbo sin río

`cosmos configurar` es un subcomando de primera clase (README §«El alta: `cosmos configurar`», con
tres invocaciones documentadas) y sale en `cosmos --help`. **No existe `galaxia/agua/rio-configurar.md`**:

```
$ ls galaxia/agua/ | grep rio | wc -l
17
$ ls galaxia/agua/rio-configurar.md
ls: galaxia/agua/rio-configurar.md: No such file or directory
```

Los 15 subcomandos del CLI tienen río salvo `configurar`; los otros tres ríos (`gate`, `secretos`,
`memoria`) son entradas de `puente/`. Consecuencia real: `cosmos buscar "dar de alta las
credenciales"` no puede llevar a `configurar`, porque el catálogo no lo contiene — y `NUCLEO.md`
§2 justifica que los ríos aparezcan siempre precisamente con *«un comando que no se sabe que existe
no se invoca»*.

*Arreglo*: crear `galaxia/agua/rio-configurar.md` (`momento: mantenimiento`, para que solo se nombre
y no se describa) y regenerar el índice. Añadir a `tests/test_rio_momento.py` la aserción de que
todo subcomando del CLI tiene río.

### B-06 · ALTO · La válvula usa `P01`/`P02` y ni la ayuda ni el README los nombran

Códigos reales (`cosmos/guardarrailes.py:49`): `CODIGOS_GATE = ("P01", "P02")`. Y son los que están
abiertos hoy en este repositorio:

```
$ python3 -m cosmos saltar --listar
ACTIVO    P01  caduca el 2026-09-10 (7 d)
ACTIVO    P02  caduca el 2026-09-10 (7 d)
```

Pero la ayuda no los enseña:

> `codigo   código concreto a saltar (E00–E21, G01..G05)` — `cosmos saltar --help`

y el README solo cita `P01`:

> `| Acotada | Un código concreto (`E00`..`E21`), de sesión (`G01`..`G05`) o del gate (`P01`); nunca «todo» |`
> — `README.md:168`

Es reincidencia exacta de F14 («E00-E19 en la ayuda con E20 existiendo»). El canario que se escribió
entonces —`tests/test_cifras_de_las_specs.py::test_la_ayuda_del_cli_muestra_el_rango_de_verdad`—
solo comprueba el rango `E`, así que no vio esta.

*Arreglo*: en `cosmos/cli.py`, componer el texto del positional desde `CODIGOS_INVARIANTES +
CODIGOS_SESION + CODIGOS_GATE` en vez de escribirlo a mano; corregir `README.md:168` a
«del gate (`P01`,`P02`)»; y ampliar el canario para exigir los tres grupos.

### B-07 · ALTO · `E20` está viva y ninguna prueba la ve en rojo

`spec/VALIDADOR.md:150-151` es una exigencia, no una recomendación:

> «para **cada invariante viva** hay un test que construye un árbol que la viola y exige el rojo con
> ese código exacto»

Medido:

```
$ grep -rhoE "def test_e[0-9]{2}" tests/*.py | sort -u
def test_e00 … def test_e19  def test_e21          # no hay test_e20
$ grep -rn '"E20"' tests/ puente/tests/
(sin resultados)
```

`tests/test_validador.py::PruebasInvariantes` cubre E00–E19; E21 tiene su prueba en otro fichero;
**E20 no tiene ninguna que la dispare**. Lo que existe (`test_cifras_de_las_specs.py:262`) comprueba
lo contrario: que el ejemplo de la spec *no* dé E20.

*Arreglo*: añadir `test_e20_vecino_inexistente` a `PruebasInvariantes` (árbol con `usa:
["no/existe"]` y otro con `usa:` a sí mismo) y una entrada en `puente/tests/mutaciones.py`.

### B-08 · MEDIO · `cosmos --version` no existe

```
$ python3 -m cosmos --version
usage: cosmos [-h] {abrir,buscar,…}
cosmos: error: the following arguments are required: comando   # exit 2
```

Un harness que se instala sobre repos ajenos (`cosmos proyectar`) y escribe un bloque marcado en su
`CLAUDE.md` no puede decir qué versión lo escribió. Ver también §8 (B-33).

### B-09 · MEDIO · La ayuda de `proyectar` se presenta con el nombre equivocado y deja dos subcomandos sin describir

```
$ python3 -m cosmos proyectar --help
usage: python3 -m cosmos [-h] [--config CONFIG] {sincronizar,comprobar,iniciar} ...
positional arguments:
  {sincronizar,comprobar,iniciar}
    iniciar   escribe planeta.toml en el repo destino; luego edítalo y ejecuta sincronizar
```

`usage:` dice `python3 -m cosmos` en vez de `cosmos proyectar`, y de los tres subcomandos solo
`iniciar` tiene `help=`. El README sí los documenta los tres (`README.md:105-108`), así que la ayuda
del programa es más pobre que el README para el verbo de portada del `GOAL.md`.

*Arreglo*: `prog="cosmos proyectar"` en el sub-parser y un `help=` por subcomando.

### B-10 · MEDIO · `tests/test_escala.py` extrapola desde una densidad del árbol que ya no es la real

> `# Densidad del árbol real (medida con `cosmos estado`): 21 oficios, 42 países, 6`
> `# continentes. … PAISES_POR_OFICIO = 2` — `tests/test_escala.py:70-73`

Medido hoy: **22 oficios, 76 países, 8 continentes** → 3,45 países por oficio, no 2. El test declara
que sus árboles sintéticos usan la densidad real «para que la extrapolación no sea una suposición
cómoda», y hoy la suposición es cómoda: subestima el mapa en un 70 %.

*Arreglo*: derivar `PAISES_POR_OFICIO` de `cosmos estado` con un canario que se ponga rojo si la
densidad real se aleja, o actualizar el comentario y la constante y decir de qué fecha son.

### B-11 · MEDIO · La cifra del holdout que publica `PROGRESS.md` no es la que imprime el comando

> «La última medición válida antes de retirarlo: **8/20 = 40 %** (IC95 22–61 %).» — `PROGRESS.md:17`

```
$ python3 -m cosmos acertar
  Validación ..... 6/20 (30 %; IC95 14–52 %; n=20)   escritos aparte; no guían ninguna decisión
```

El conjunto es el mismo (sha256 del fichero de `~/.cosmos/holdout/` = el del `.SELLO`), así que la
diferencia 8→6 es del árbol: los arreglos del ciclo 2 empeoraron dos aciertos y nadie lo miró. Es
además la única cifra de calidad del catálogo que hay, y el `PROGRESS.md` la deja congelada.

*Arreglo*: `PROGRESS.md` no debe llevar la cifra a mano — remitir a `cosmos acertar` como ya hace con
`cosmos estado`, o regenerarla en el mismo bloque generado.

*(Nota de honestidad: `cosmos acertar` degrada bien cuando el holdout no está —`Validación ..... NO
DISPONIBLE`—, comprobado con `COSMOS_HOLDOUT=/tmp/no-existe`.)*

---

## 2. Spec vs spec, y specs vs `GOAL.md`

### B-12 · ALTO · `GOAL.md` §3 y §4 declaran un nivel `Universo` que el código no reconoce

`GOAL.md:95-99` (§3, «la taxonomía aprobada»):

> `| **Universo** | Todo. Hay uno. | Galaxias |`

y `GOAL.md:129` (§4, reglas de carga): `| Universo / Galaxia | Siempre | Todo … |`.

Pero `cosmos/modelo.py:23-39` tiene **siete** sólidos y `universo` no está entre ellos; `E09` valida
contra los «14 niveles» y un fichero con `cosmos: universo` sale en rojo. `README.md:31` y
`spec/FRONTMATTER.md:44-52` dan la cadena sin `Universo`.

Lo que lo convierte en un hallazgo y no en una licencia poética es que el propio `GOAL.md` condena
esto catorce líneas más abajo, hablando de `ciudad`/`casa`:

> «Un nivel sin un solo nodo no es una reserva: es una promesa que el lector se cree.» — `GOAL.md:146`

Agravante: `universo` **sí** existe en el sistema, pero como **magnitud del medidor**
(`NUCLEO.md` §3, `cosmos medir` → `Universo ........ 168.794 tokens`). El mismo nombre significa dos
cosas distintas en dos specs.

*Arreglo*: quitar la fila `Universo` de §3, dejar §4 como `| Galaxia | Siempre | …`, y —si se quiere
conservar la idea— decir en una línea que «universo» en COSMOS es la magnitud del medidor, no un
nivel. Añadir al canario de specs la comprobación de que toda fila de la tabla §3 es un nivel de
`NIVELES_VALIDOS`.

### B-13 · MEDIO · `spec/FRONTMATTER.md` se contradice a sí misma sobre `moja`

Ocho líneas de distancia, mismo fichero:

> `| `moja` | sí | Lista de patrones glob, **no vacía**. Determina cuándo se carga |` — línea 103
>
> `| `rio` | Se invoca a mano: `moja: []` permitido …|` — línea 110
> `| `lluvia` | Se consulta a mano: `moja` **tiene que ser** `[]` …|` — línea 111

El código implementa lo segundo (E10: «lista, vacía solo en `rio` y `lluvia`, y obligatoriamente
vacía en `lluvia`»). La fila de arriba está mal.

*Arreglo*: `| `moja` | sí | Lista de patrones glob. No vacía salvo en `rio` y `lluvia` (ver tabla) |`.

### B-14 · MEDIO · `spec/MEDIDOR.md` llama «Árbol» a lo que todo lo demás llama «Universo»

> `| **Árbol** | La suma de todo el contenido del árbol, si se cargara entero | …|`
> `| **Descarga** | `1 − entrada / árbol` | …|` — `spec/MEDIDOR.md:21-22`

`NUCLEO.md` §3 —que gana cuando hay discrepancia (`NUCLEO.md:8`)— define `universo = entrada + resto`
y `descarga = 1 − entrada/universo`, y el comando imprime `Universo`. La propia MEDIDOR.md imprime
`Universo` en su bloque de ejemplo (línea 112), o sea que se contradice dentro del mismo fichero.

*Arreglo*: renombrar las dos filas de la tabla a **Universo** y remitir la fórmula a `NUCLEO.md` §3
en vez de repetirla (repetir una fórmula normativa es como envejeció esta).

### B-15 · BAJO · `spec/VALIDADOR.md` enseña un `cosmos.toml` que no es el que se usa

`spec/VALIDADOR.md:104-114` documenta cuatro claves (`entrada`, `resumen`, `oceanos`,
`galaxia_lineas`) y `[raiz] arbol/indice`. El `cosmos.toml` real tiene además `solapamiento`,
`[raiz] registro`, `[medicion] metodo`, `[compilacion] destino/modo/manifiesto` y `[nichos] activos`
— todas obligatorias para que el árbol real valide.

*Arreglo*: pegar el `cosmos.toml` real (o el mínimo viable) y marcar cuáles tienen valor por defecto.

### B-16 · ALTO · `spec/GUARDARRAILES.md` habla de «los tres enganches» y el código instala cuatro

`cosmos enganchar` escribe **dos** hooks de git:

```
$ ls .git/hooks | grep -v sample
pre-commit      → exec python3 -m puente.gate --silencioso
pre-push        → exec python3 -m puente.secretos --todo
```

y el código lo confirma (`cosmos/guardarrailes.py:304-307`): *«El pre-push repite el escaneo de
secretos sobre todo lo versionado … es la última puerta local antes de que salga del disco»*.

Pero:

```
$ grep -n "pre-push" spec/GUARDARRAILES.md
(sin resultados)
```

`spec/GUARDARRAILES.md:23` se titula «## Los tres enganches» y su tabla tiene pre-commit, sesión y
CI. `README.md:137-141` copia esa tabla. `cosmos enganchar --help` dice «instala el gate de
**pre-commit** en este repositorio». Un guardarraíl que puede **parar un `git push`** no está
documentado en ningún sitio del producto.

Y hay una huella de que la spec se quedó a medias: cuatro líneas después de la tabla de tres filas
dice *«Los tres primeros son de repositorio … El de sesión es el único que actúa mientras se
decide»* (`spec/GUARDARRAILES.md:40-42`). Con tres enganches, «los tres primeros» excluyendo el de
sesión no cuadra: la frase se escribió cuando eran **cuatro**.

*Arreglo*: añadir la fila `pre-push` a la tabla de la spec y del README, retitular «Los cuatro
enganches», corregir el `help=` de `enganchar`, y ampliar
`test_los_enganches_del_readme_son_los_de_la_spec` para que además compare la lista de la spec con
lo que `cosmos/guardarrailes.py` instala de verdad.

### B-17 · MEDIO · `spec/GUARDARRAILES.md` describe un pre-commit que no es el que corre

> `| **pre-commit** | Antes de cada commit del repo que usa COSMOS | `cosmos validar`. Si rojo, el commit no ocurre |`
> — `spec/GUARDARRAILES.md:27`
>
> `| **CI** | En cada push, si hay CI | `cosmos validar` completo |` — línea 29

El hook real ejecuta `python3 -m puente.gate --silencioso`, que hace validar **sobre una instantánea
del índice** más las dos suites, el escáner de secretos y los canarios P01/P02. El CI real
(`.github/workflows/cosmos.yml`) corre diez pasos. El README lo cuenta bien
(`README.md:139`, «sobre la instantánea del índice»); la spec normativa, no.

---

## 3. Referencias muertas

### B-18 · ALTO · El resumen de `butler` nombra una provincia que se retiró ayer

```yaml
# galaxia/pueblos/butler/SKILL.md
padre: juegos/motores
resumen: Sube una build a itch.io con parches binarios; unico pueblo de la provincia de distribucion.
```

`galaxia/paises/juegos--distribucion.md` se retiró el 2026-09-03 y `butler` se recolgó de
`juegos/motores` (`PENDIENTE-DARIO.md` §5-bis). El `resumen` sigue citando el nodo muerto — y un
`resumen` **es lo que se paga en el catálogo del nicho `juegos` en cada sesión que entre ahí**:
la referencia muerta no está en un comentario, está en la línea más cara del sistema.

Además incumple el antipatrón de `spec/TAXONOMIA.md:105` («Resumen que describe hijos» / describe el
contenedor en vez del nodo) y gasta 43 de sus 120 caracteres en decirlo.

*Arreglo* (diff mínimo):

```diff
-resumen: Sube una build a itch.io con parches binarios; unico pueblo de la provincia de distribucion.
+resumen: Sube una build a itch.io con parches binarios: solo sube lo que cambio, no el juego entero.
```
y `python3 -m cosmos generar`.

### B-19 · ALTO · `galaxia/pueblos/captura-recortada` afirma un guardarraíl que COSMOS no tiene

> «Para todo lo demás, el `-R` nativo es más barato aún y no pide dependencias — y **en este arnés la
> pantalla entera está bloqueada por enganche**.» — `galaxia/pueblos/captura-recortada/SKILL.md:25`

No hay tal enganche en COSMOS: los cinco guardarraíles de sesión son G01–G05
(`spec/GUARDARRAILES.md:58-62`) y ninguno mira `screencapture`. La frase describe el harness de
origen del autor, no este producto: para el que clone COSMOS es **falsa**.

*Arreglo*: borrar la coletilla (`… y no pide dependencias.`) o reescribirla como consejo genérico.

### B-20 · MEDIO · `PENDIENTE-DARIO.md` propone archivar en `cosecha/retiradas/`, y `cosecha/` está retirada

> «se propone con motivo, **se archiva, nunca se borra** (`mv galaxia/pueblos/<x> ~/.Trash/` o a
> `cosecha/retiradas/`)» — `PENDIENTE-DARIO.md:107-108`

`cosecha/` se retiró en el mismo ciclo (`spec/TAXONOMIA.md:159-166`, «`cosecha/` se retiró: una
herramienta vive en un solo sitio»). El documento que Darío tiene que leer para decidir le da una
ruta que ya no existe.

### B-21 · MEDIO · `PENDIENTE-DARIO.md` §8 dice que el hook no está instalado; `CIERRE.md` dice que sí, y sí lo está

> «`cosmos enganchar --sesion` **no está instalado** en `~/cosmos` (solo `.sample` en `.git/hooks`).»
> — `PENDIENTE-DARIO.md:166`
>
> «**Hook de pre-commit** instalado (`cosmos enganchar --sesion`)» — `CIERRE.md:33`

Medido: `.git/hooks/pre-commit` y `.git/hooks/pre-push` existen (fecha 2026-09-03 16:14) y
`.cosmos/enganche-sesion.json` está escrito. El `PENDIENTE` es el documento que pide decisiones y
tiene un punto ya resuelto sin marcar.

*Arreglo*: tachar §8 con «HECHO 2026-09-03», como se hizo con §3 (F-04).

### B-22 · MEDIO · `PLAN-MAESTRO.md` en la raíz describe un COSMOS que no existe, sin decir que es histórico

Es un fichero **versionado y en la raíz**, junto a `GOAL.md`, `README.md` y `PROGRESS.md`. Su §2 dice:

> «**Nueve sistemas solares.**» — y la tabla nombra `codigo`, `mercados`, `inteligencia`, `datos`,
> `medios`, `negocio`, `guardia` — `PLAN-MAESTRO.md:34-45`

De esos nueve, hoy existen dos (`web`, `infraestructura`); `spec/UNIVERSO.md:16-18` dice
explícitamente que `datos`, `agentes`, `medios`, `sistemas` y `conocimiento` **se expulsaron por ser
categorías temáticas**. Además: «continentes, países, provincias, **ciudades** y pueblos» (nivel
retirado), «El índice son **nueve líneas** de sistema», «13 barridos», y la capa «Sistema inmune ·
Especificado, **por implementar**» que lleva implementada desde hace días.

El propio repositorio ya lo había detectado y decidió no tocarlo:

> «**`PLAN-MAESTRO.md` habla de ciudades y de nichos ya retirados** (`medios`, `negocio`, `guardia`).
> Es un plan histórico, superado por `spec/UNIVERSO.md`»
> — `registro/commits/universo/2026/09/fix-h20-niveles.md:227-229`

La decisión de no reescribirlo es defendible; **dejarlo en la raíz sin una sola línea que diga que es
histórico, no**. Un clon nuevo lee `PLAN-MAESTRO.md` y se lleva el mapa equivocado.

*Arreglo* (dos líneas, sin reescribir nada):

```diff
 # Plan maestro — la herramienta definitiva
+
+> **Histórico (2026-09-01), conservado tal cual.** El mapa vigente es `spec/UNIVERSO.md` (22 oficios)
+> y el contrato es `GOAL.md`. Los nueve sistemas de §2 y el nivel `ciudad` ya no existen.
```
o moverlo a `registro/decisiones/`.

### B-23 · BAJO · `research/` conserva referencias a las tres herramientas retiradas ayer

`research/dominios/seo-contenido.md:42` («`Hainrixz/claude-seo-ai` 🔧 — **YA INSTALADO en este
workspace**»), `research/dominios/bots-trading.md:141` (`talipp`), `research/dominios/blockchain.md:31`
(`mythril`). Son documentos de barrido, no producto; el hallazgo es que `research/` no dice en
ninguna parte que sea un archivo congelado.

*Arreglo*: un `research/README.md` de tres líneas («barridos de GitHub de 2026-09-01/02; congelado;
el catálogo vivo es `galaxia/`»).

---

## 4. Restos de la agencia, de clientes y de esta máquina

Contexto: `GOAL.md:150` — *«Este repo es **público-limpio y genérico**. Fuera de cualquier
organización, cliente o negocio.»* Y el encargo de Darío citado en `PENDIENTE-DARIO.md:88`:
*«tiene que estar este harnés fuera de <la agencia>, no pongas datos de <la agencia>, es para Darío»*.

**Lo que NO encontré, habiéndolo buscado** (esto pasó): cero ocurrencias del nombre de la agencia,
de su canal propio, de sus productos internos, de correos, de dominios de cliente ni de rutas
`<casa>/...` en `galaxia/`, `spec/`,
`cosmos/`, `puente/`, `tests/`, `docs/`, `.github/` y los ficheros de raíz. El barrido
(`grep -rniE "<agencia>|<canal>|<producto>|<usuario>|<casa>/|@gmail|…"`, con los nombres reales)
solo da resultados en `research/`, `reviews/` y `puente/tests/test_secretos.py` (donde `<casa>/` es
el patrón del propio detector). La limpieza del ciclo 2 es real.

Lo que sí queda es de otra clase: **el repositorio se sigue hablando a sí mismo como si fuera el
harness de su autor**.

### B-24 · ALTO · Once nodos del producto dicen «esta casa», «este arnés» o «este Mac»

| Fichero | Cita |
|---|---|
| `galaxia/pueblos/sanitizers/SKILL.md:40` | «Y el falso verde de **esta casa**, **medido en este Mac** (arm64, Apple clang 21, 2026-09-01)» |
| `galaxia/pueblos/samply/SKILL.md:21` | «a `perf` en **esta casa** por lo pragmático: corre en **este Mac** y con **este procesador**» |
| `galaxia/pueblos/mlx-lm/SKILL.md:31` | «exige CUDA y no corre en **este Mac**» |
| `galaxia/pueblos/context7/SKILL.md:28` | «Ya está disponible en **esta casa**.» |
| `galaxia/pueblos/lm-evaluation-harness/SKILL.md:27` | «que importa para **esta casa**» |
| `galaxia/pueblos/openclaw/SKILL.md:17` | «Es el origen del canal autónomo que ya se usa en **esta casa**.» |
| `galaxia/pueblos/geo-optimizer/SKILL.md:28` | «es una regla dura de **esta casa**» |
| `galaxia/pueblos/elementor-mcp/SKILL.md:12` | «Del lado de **esta casa**, dos guiones propios» |
| `galaxia/pueblos/tree-sitter/SKILL.md:26` | «herramientas de **este arnés**, no una más» |
| `galaxia/pueblos/captura-recortada/SKILL.md:25` | «en **este arnés** la pantalla entera está bloqueada» (ver B-19) |
| `galaxia/pueblos/acceso-remoto/scripts/acceso-remoto-watchdog.sh:2` | «Vigila que el acceso remoto a **este Mac** siga vivo» |

«Esta casa» y «este arnés» son el vocabulario del harness de origen, no de un producto que se clona.
Para el que clona, el deíctico no resuelve: no sabe qué casa ni qué Mac. Y en tres casos
(`sanitizers`, `samply`, `mlx-lm`) la afirmación técnica está **anclada a un hardware concreto**, que
es exactamente lo que `spec/UNIVERSO.md:158-161` declaró corregido:

> «Hasta el 2026-09-02 las fichas se escribieron desde un portátil de 8 GB sin GPU, y 24 de ellas
> elegían por esas restricciones (auditoría C-10). La máquina de referencia es un M3 Pro de 18 GB, y
> … todo requisito de máquina —RAM, GPU dedicada, Apple Silicon— es un dato del apartado «Ojo».»

*Arreglo*: sustituir el deíctico por el hecho («en macOS arm64 con Apple clang 21», «en Apple
Silicon», «cuando el harness anfitrión ya lo trae»), y añadir a la suite un canario léxico —el repo
ya tiene la mecánica en `tests/test_cifras_de_las_specs.py`— que ponga rojo `esta casa|este arnés|este Mac`
en `galaxia/**`.

### B-25 · ALTO · El nicho `agentes-ia` sigue siendo, en gran parte, el harness del autor

C-01 de la auditoría dijo *«`agentes-ia` no es el oficio que declara: es "operar Claude Code"»*, con
15 de 21 pueblos propios (71 %). Hoy: **25 pueblos, 10 con `origen: propio` (40 %)**. Mejoró, pero de
esos diez, ocho no son «agentes IA» sino instrumentación del harness del autor:
`alcance-y-excepcion`, `captura-recortada`, `codigo-al-modelo`, `delegar-generacion`,
`diario-sin-duplicados`, `medir-contexto`, `plan-auditado`, `playbook-obligatorio`,
`revision-cruzada`.

Ejemplos medibles:
- `galaxia/pueblos/medir-contexto/SKILL.md:9` lee `~/.claude/projects/*.jsonl` — mide el gasto **del
  harness que ejecuta COSMOS**, no un agente que se construya.
- `galaxia/pueblos/diario-sin-duplicados/SKILL.md:12` usa como ejemplo `notes/daily/2026-09-01.md`,
  que es la convención de bóveda Obsidian del autor, no un camino genérico.

No es un fallo del validador (todos cumplen E21), es un desajuste entre el nicho declarado en
`spec/UNIVERSO.md` («Agentes que hacen trabajo real, con herramientas, memoria y evaluación») y su
contenido.

*Arreglo*: o se declara un continente `agentes-ia/instrumentacion-del-harness` que lo diga, o esos
ocho bajan a un país propio y el resumen del sistema se corrige. Decisión de producto, no de código.

### B-26 · MEDIO · `revision-cruzada` depende de un servicio con cuenta, y `GOAL.md` §5 lo prohíbe

> `export OPENROUTER_API_KEY="<clave-de-capa-gratuita>"` — `galaxia/pueblos/revision-cruzada/SKILL.md:13`

`GOAL.md:155`: «Cero dependencias de pago y cero servicios que pidan tarjeta.» La capa gratuita de
OpenRouter no pide tarjeta, así que no es una violación estricta, pero es el único pueblo cuyo
ejemplo mínimo **no corre sin darse de alta en un tercero**. Ya estaba señalado
(`PENDIENTE-DARIO.md:126`, «a vigilar») y sigue igual.

---

## 5. Taxonomía y comandos: lo que dicen los números

**Lo que intenté tumbar y aguanta** (medido con un recorrido propio de los 454 nodos con frontmatter
de `galaxia/`, no leyendo el validador):

| Comprobación | Resultado |
|---|---|
| Nodos sólidos con **un solo hijo** (antipatrón `TAXONOMIA.md:104`) | **0** |
| `resumen` de más de 120 caracteres (E07) | **0** |
| Nombres duplicados dentro del mismo padre (E06) | **0** (hay 3 países homónimos —`motores`, `auditoria`, `publicacion`— bajo padres distintos: legal por diseño) |
| Pueblos sin URL `http(s)` en la primera línea del cuerpo **ni** `origen: propio` (E21) | **0 de 297** |
| Destinos de `usa:` inexistentes (E20) | **0** |
| Suma de nodos por nivel = 468 | ✅ coincide con `spec/VALIDADOR.md:68` («los 468 nodos de la galaxia real») |
| 22 oficios / 6 mares / 5 océanos en `galaxia/COSMOS.md:3` | ✅ coincide con `cosmos estado` |
| Bloque de cifras de `PROGRESS.md` vs `python3 -m cosmos estado` | ✅ idéntico (lo guarda `tests/test_progress_generado.py`) |
| Fichas contra la API de GitHub (10 muestreadas: `toxiproxy`, `butler`, `osv-scanner`, `ta`, `chonkie`, `katana`, `slither`, `medusa`, `claude-skills`, `superpowers-lab`) | ✅ estrellas, licencia y `pushed_at` correctos dentro de la deriva de un día |
| Hallazgos C-02, C-03, C-04, C-05, C-11, C-12, C-14 de la auditoría | ✅ **cerrados** en el árbol (`astro`/`payload`/`vite`/`tailwindcss`; `ansible`/`opentofu`; `nmap`; `memray`/`memlab`; `metabase`/`rill`/`evidence`; `feyninc/chonkie`; URL de `auditor-de-skills`) |

### B-27 · ALTO · `cosmos validar` no dice «verde» a secas — pero el `CIERRE.md` sí

Salida real de hoy:

```
$ python3 -m cosmos validar
COSMOS  verde (2 saltos activos: P01, caduca en 7 d; P02, caduca en 7 d)  0 errores
```

El comando cumple la regla del README al pie de la letra:

> «La palabra «verde» no aparece nunca sola habiendo saltos activos. Un verde que oculta un salto es
> una mentira, y basta una para que nadie vuelva a creerse ninguna.» — `README.md:175-176`

Pero el documento que declara el cierre **sí la escribe sola**:

> `| python3 -m cosmos validar | verde, 0 errores |` — `CIERRE.md:11`

Es la mentira exacta que el mecanismo existe para impedir, cometida por el humano al transcribir la
salida del mecanismo. Y los dos saltos no son menores: `P02` es el que permite **dar de baja pueblos
sin que el gate lo pare** («toda baja de pueblo pasa por la válvula `cosmos saltar P02`»,
`puente/gate.py:212`), es decir, la válvula estaba abierta justo mientras se retiraban seis nodos.
Caducan el **2026-09-10**; a partir de ese día el gate vuelve a rojo si algo depende de ellos.

*Arreglo*: en `CIERRE.md`, pegar la línea literal con los saltos. Y —mejor— que `puente/gate.py`
escriba en el propio informe de cierre la lista de saltos vivos, para que no dependa de que alguien
copie bien.

### B-28 · ALTO · El ejemplo de `cosmos abrir --help` no funciona

```
$ python3 -m cosmos abrir --help
  ruta   ruta cosmográfica o nombre, p.ej. 'trading/backtesting'

$ python3 -m cosmos abrir trading/backtesting
COSMOS  abrir  rojo

no existe 'trading/backtesting'.            # exit 1
```

La ruta real es `trading/estrategia/backtesting` (`galaxia/paises/trading-backtesting.md`,
`padre: trading/estrategia`). El nombre corto sí resuelve (`cosmos abrir backtesting` → verde), o sea
que el ejemplo de la ayuda es el **único** de las dos formas que falla.

Agravante: el mensaje de error no dice qué hacer, y el README promete lo contrario en la línea 50
(«Nada que adivinar: **cada salida dice qué hacer después**») y `spec/VALIDADOR.md:141` lo eleva a
doctrina («Un error que solo dice qué está mal invita a desactivar la comprobación»).

*Arreglo* (dos líneas): cambiar el ejemplo a `'trading/estrategia/backtesting'` o al nombre corto, y
en el error de `abrir`, si el último tramo resuelve como nombre único, decir
`¿querías 'trading/estrategia/backtesting'? o prueba 'cosmos buscar <intención>'`.

### B-29 · MEDIO · Un resumen de océano rompe la convención de escritura sin acentos

Medido sobre los 454 resúmenes del árbol: **453 están escritos sin acentos** (0/22 sistemas, 0/76
países, 0/8 continentes, 0/297 pueblos, 0/22 estrellas). Hay exactamente uno que no:

> `resumen: Cuando dos reglas chocan, gana la más específica; y una orden reciente gana a una regla.`
> — `galaxia/agua/oceano-precedencia.md:5`

Y está en el sitio más caro que existe: un **océano**, que se paga en toda sesión y todo subagente.
La convención no está escrita en ninguna spec ni la comprueba ninguna invariante, así que solo se
sostiene por costumbre — que es lo que este repositorio llama «exhortación» (`GOAL.md:70`).

*Arreglo*: decidir. O se escribe la regla en `spec/FRONTMATTER.md` («los `resumen` van en ASCII: el
tokenizador BPE parte cada acento en una pieza aparte», que es justo lo que documenta
`docs/CALIBRACION.md:60`) y se añade una comprobación a E00; o se quita la convención y se acentúan
los 453. Lo que no puede quedarse es una norma de 453 casos que nadie declara y que un caso rompe.

---

## 6. Limitaciones heredadas de una máquina pequeña

El barrido (`grep -rniE "8 ?GB|sin GPU|portátil de|RAM|tres sesiones"`) sobre `galaxia/`, `spec/`,
`cosmos/`, `puente/`, `tests/` y la raíz **no encuentra ninguna decisión de catálogo justificada por
un Mac de 8 GB**. La corrección de C-10 está hecha y declarada:

> «Hasta el 2026-09-02 las fichas se escribieron desde un portátil de 8 GB sin GPU, y 24 de ellas
> elegían por esas restricciones (auditoría C-10). **La máquina de referencia es un M3 Pro de 18 GB**»
> — `spec/UNIVERSO.md:158-159`

Las menciones de RAM que quedan son propiedades reales de la herramienta y están en su apartado
«Ojo», como manda la spec: `dask` (Ray reserva un tercio de la RAM del host), `bevy` (varios GB al
compilar), `micropython` (100 KB), `tauri`, `xlsxwriter`, `compose-multiplatform`. Correcto.

Queda una sola cosa, y es menor:

### B-30 · BAJO · `TOPE_SESIONES = 3` es la regla del Mac de 8 GB, con su cifra puesta

> `TOPE_SESIONES = 3          # ajusta al límite de RAM de tu máquina, no es un valor mágico`
> — `galaxia/pueblos/agent-browser/scripts/navegador_seguro.py:19`

El comentario ya avisa de que es ajustable (bien), pero el valor por defecto viene de la regla de
tres sesiones de una máquina de 8 GB, y en un M3 Pro de 18 GB queda corto sin motivo. La ficha del
pueblo lo dice ya en genérico —«En una máquina justa de memoria, pocas sesiones simultáneas»
(`galaxia/pueblos/agent-browser/SKILL.md:34`)—, así que la incoherencia es solo la constante.

*Arreglo*: `TOPE_SESIONES = int(os.environ.get("AGENT_BROWSER_TOPE_SESIONES", "3"))`, o derivarlo de
la memoria física con `os.sysconf`.

---

## 7. Mejoras decididas y no aplicadas

### 7.1 · Lo de `C-galaxia.md` que el CIERRE dejó fuera — casi todo se aplicó

Comprobé una por una las 12 de prioridad 1, las 12 de prioridad 2 y las ~35 de prioridad 3 contra
`galaxia/pueblos/`. **Solo dos no están**, y una de ellas por diseño:

| Propuesta | Estado | Verificación de hoy (API de GitHub) |
|---|---|---|
| `aboutcode-org/scancode-toolkit` → `cumplimiento/licencias` | **sin aplicar** | 2.617★ · push 2026-09-04 · no archivado |
| `go-task/task` → `automatizacion` | sin aplicar, pero la propuesta decía «`go-task/task` **o** `casey/just`» y `just` sí está | 16.087★ · push 2026-09-04 · MIT |

*Qué*: añadir `scancode-toolkit` como pueblo de `cumplimiento/licencias`. *Dónde*:
`galaxia/pueblos/scancode-toolkit/SKILL.md` + `cosmos generar`. *Coste*: ~26 tokens en el catálogo de
`cumplimiento` (12 pueblos, muy por debajo del peor nicho: no mueve E16). *Riesgo*: ninguno; su rival
—`ort`, que ya está— lo usa por dentro, y eso es justamente el «rival nombrado» que exige
`spec/PUEBLO.md` regla 4.

#### B-31 · MEDIO · C-06 se resolvió a medias: los mares apuntan, los nodos no se movieron

C-06 proponía dos arreglos alternativos y se aplicó el barato:

```
$ grep -o '`[a-z0-9/._-]*`' galaxia/agua/mar-pruebas.md galaxia/agua/mar-resistencia.md
mar-pruebas.md:`refactorizacion/mutacion` `hypothesis` `trading`
mar-resistencia.md:`tenacity` `toxiproxy` `time-machine`
```

Bien: cuatro de los seis genéricos ya son alcanzables desde el agua. Pero los seis siguen colgando
de `trading/bots/codigo-de-bot`, y **`eventsourcing` y `python-statemachine` no los nombra ningún
mar**: para quien trabaja en `saas`, `web` o `infraestructura` siguen sin existir.

*Arreglo*: nombrarlos también en `mar-resistencia` (una línea), o mover los seis a un país neutro. Lo
primero cuesta ~10 tokens y cierra el hallazgo.

#### B-32 · MEDIO · Dos de las «retiradas dudosas» incumplen la condición que se les puso

`PENDIENTE-DARIO.md:118-122`: *«**Dudosas (6): se quedan solo si su ficha justifica el solapamiento**»*.
Las ocho fichas siguen en el árbol. Medido con `cosmos estado --json` (apartado «sin rival nombrado»,
que es la métrica del propio repositorio para eso):

| Ficha | Rival nombrado en la ficha | Veredicto contra su propia condición |
|---|---|---|
| `a11y-auditoria-wcag` | sí | se queda |
| `unlighthouse` | sí | se queda |
| `tokio`, `mimalloc` | sí | se quedan |
| `openproject`, `twenty` | sí | se quedan |
| `arx` | sí (justifica frente a `presidio`) | se queda |
| **`reprozip`** | **no** — está en la lista de los 69 «sin rival nombrado» | **incumple: o se escribe el rival, o se retira** |

*Qué*: escribir en `galaxia/pueblos/reprozip/SKILL.md` la comparación con `pixi` + `dvc` (que ya están
en el árbol) o archivarlo. *Coste*: dos frases. *Riesgo*: cero, archivar es reversible.

### 7.2 · Los tres oficios nuevos — verificados hoy, dos herramientas vivas cada uno

`PENDIENTE-DARIO.md` §7 los deja «decididos, no montados». `C-galaxia.md` §«lo que falta» demuestra
que **un oficio nuevo cuesta cero en el peor caso** (E16 mira el peor nicho individual, y ninguno de
estos se acercaría a `ciberseguridad`), así que el único freno es el sí de Darío sobre
`spec/UNIVERSO.md`.

Verificado el 2026-09-04 por API pública de GitHub **y** por `commits/HEAD.atom` (sin `gh auth`):

| Oficio | Herramienta | ★ | `pushed_at` | HEAD real (atom) | Licencia |
|---|---|---|---|---|---|
| `localizacion` | `WeblateOrg/weblate` | 6.051 | 2026-09-04 | 2026-09-04T06:23Z | GPL-3.0 |
| `localizacion` | `i18next/i18next` | 8.625 | 2026-09-03 | 2026-09-03T20:23Z | MIT |
| `localizacion` | *(3.ª)* `formatjs/formatjs` | 14.747 | 2026-09-04 | — | sin SPDX declarado |
| `entregabilidad` | `domainaware/parsedmarc` | 1.291 | 2026-09-03 | 2026-09-03T19:51Z | Apache-2.0 |
| `entregabilidad` | `axllent/mailpit` | 10.273 | 2026-09-03 | 2026-09-03T05:08Z | MIT |
| `entregabilidad` | *(3.ª)* `domainaware/checkdmarc` | 321 | 2026-08-31 | — | Apache-2.0 |
| `aprendizaje-automatico` | `optuna/optuna` | 14.744 | 2026-09-04 | 2026-09-04T06:25Z | MIT |
| `aprendizaje-automatico` | `bentoml/BentoML` | 8.820 | 2026-08-28 | — | Apache-2.0 |
| `aprendizaje-automatico` | *(3.ª)* `scikit-learn/scikit-learn` | 67.158 | 2026-09-04 | — | BSD-3-Clause |

**Aviso que hay que resolver antes de montarlo, y no está en `PENDIENTE-DARIO.md`:** el candidato
natural de `aprendizaje-automatico`, `mlflow`, **ya existe** en el árbol con
`padre: agentes-ia/evaluacion`, y `dvc` con `padre: cientifico/reproducible`. E18 prohíbe dos pueblos
con el mismo nombre y `GOAL.md:44` dice «una herramienta vive en un solo sitio»: montar el oficio
obliga a **mover** `mlflow`, no a duplicarlo — y mover un pueblo cambia el catálogo de dos nichos.

*Coste*: 3 sistemas + 3 estrellas + 3 filas en `UNIVERSO.md` + ~6-9 pueblos ≈ 250 tokens en el
**Universo**, **0 en el peor caso** de E16 (queda comprobado midiendo con `--nicho <nuevo>` antes de
commitear). *Riesgo*: cambia el mapa aprobado el 2026-09-01 → requiere el sí explícito.

### 7.3 · Holdout v2 — sigue siendo la única cifra desconocida del proyecto

Confirmado hoy: el v1 existe en `~/.cosmos/holdout/encargos-validacion.json`, su sha256 coincide con
`pruebas/encargos-validacion.SELLO`, y el juez lo declara quemado sin que haya que fiarse de nadie:

```
$ python3 -m cosmos acertar
  Historia git ... QUEMADO: 20 de 20 peticiones ya están en el repositorio: examen visto
  Mientras no haya un conjunto ciego, sellado y con procedencia, la cifra honesta es DESCONOCIDA.
```

Sin el holdout el comando degrada bien (`Validación ..... NO DISPONIBLE`, comprobado con
`COSMOS_HOLDOUT=/tmp/no-existe`). La receta está en `PENDIENTE-DARIO.md` §6 y **no la puede escribir
ningún agente que haya visto la galaxia** — yo la he visto entera, así que tampoco yo.

Añado dos cosas que la receta no dice y que hacen falta:

1. `PENDIENTE-DARIO.md` §6 pide `n ≥ 100` cubriendo los 22 oficios. Hoy la cobertura del conjunto de
   ajuste es `20/22 oficios (sin encargo: rendimiento, visibilidad)` — los dos que faltan son
   precisamente los dos que se crearon o reorganizaron después, así que el v2 tiene que nacer con
   ellos dentro o repetirá el sesgo.
2. Mientras no exista, **`puente/tests/mutaciones.py` no puede llegar a 79/79** (B-02): tres de sus
   mutaciones dependen de un holdout en disco. Son el mismo problema, y el orden importa.

### 7.4 · `secretos --historia` — la purga sigue pendiente y el escáner sigue sin mirar atrás

```
$ python3 -m puente.secretos --help
  [--indice | --todo]        # no hay --historia
```

Y los dos objetos que `PENDIENTE-DARIO.md` §1-2 quiere purgar **siguen alcanzables**:

```
$ git log --all --oneline -- research/scratch/q14_analytics.txt | wc -l   → 2
$ git rev-list --objects --all | grep -c q14_analytics.txt               → 1
$ git log --all --oneline -- cosecha/nif-cif-validator.js | wc -l        → 5
```

*Qué*: `--historia` que recorra `git rev-list --objects --all` con el mismo detector y el mismo
inventario de huellas. *Dónde*: `puente/secretos.py`, junto a `--todo`. *Coste*: la auditoría F lo
midió en ~90 s sobre este repo — demasiado para el pre-commit, correcto para el CI semanal o para un
`workflow_dispatch`. *Riesgo*: falsos positivos históricos; se absorben con el mismo
`secretos-conocidos.txt`, que desde el ciclo 2 indulta por huella de valor y no por fichero.

---

## 8. Otras mejoras para que esto sea un 10 en un M3 Pro

### B-33 · MEDIO · No hay `pyproject.toml`: `cosmos` no puede estar en el PATH

No existen `pyproject.toml`, `setup.py` ni `setup.cfg`. Todo el producto se invoca como
`python3 -m cosmos …`, incluidos los hooks generados, que por eso tienen que inyectar
`PYTHONPATH="$COSMOS_INSTALACION"` a mano:

```sh
# .git/hooks/pre-commit, generado por 'cosmos enganchar'
COSMOS_INSTALACION='<ruta de la instalación>'
PYTHONPATH="$COSMOS_INSTALACION"; export PYTHONPATH
exec '<python>' -m puente.gate --silencioso
```

Con un `pyproject.toml` mínimo (`[project] name/version/requires-python = ">=3.11"`,
`[project.scripts] cosmos = "cosmos.cli:main"`), `pip install -e .` deja `cosmos` en el PATH, el hook
se reduce a `exec cosmos-gate` sin rutas absolutas, y `cosmos --version` (B-08) sale gratis de la
misma pieza. Sigue siendo cero dependencias en tiempo de ejecución, así que no toca `GOAL.md` §5.

*Coste*: 15 líneas. *Riesgo*: bajo; hay que actualizar `cosmos/guardarrailes.py` para que el hook use
el binario si está y el `-m` si no.

### B-34 · MEDIO · La suite tarda 75 s y el 74 % se lo llevan cuatro módulos

Medido por módulo (`/usr/local/bin/python3`, M3 Pro, suite sola):

| Módulo | s |
|---|---|
| `test_un_solo_veredicto` | 20,3 |
| `test_escala` | 13,3 |
| `test_juez_honesto` | 11,7 |
| `test_arreglos_p3` | 9,4 |
| `test_guardarrailes` | 4,8 |
| resto (28 módulos) | ~15 |
| **total `discover -s tests`** | **75,1** |

El gate de pre-commit corre esa suite entera sobre una instantánea del índice: ~90 s por commit
(cifra que `PENDIENTE-DARIO.md:168` ya reconoce). En una máquina con 11-12 núcleos eso es tiempo
regalado: los cuatro módulos caros levantan subprocesos (`subprocess.run([sys.executable, …])`) y
son perfectamente paralelizables.

*Arreglo por orden de rentabilidad*: (1) `python3 -m unittest` no paraleliza, pero
`concurrent.futures` dentro de los tres módulos que lanzan N subprocesos secuenciales sí; (2)
reutilizar un árbol de juguete de módulo en `test_escala` en vez de reconstruirlo por test; (3) en el
gate, permitir `--rapido` que salte los cuatro y los deje solo para el pre-push y el CI. *Riesgo*: (3)
debilita el gate — habría que dejarlo detrás de la misma válvula (`P0x`) para que se registre.

### B-35 · MEDIO · El CI no cubre la versión mínima que el propio repo exige

`.github/workflows/cosmos.yml` comprueba `sys.version_info >= (3, 11)` y corre en `ubuntu-latest` con
el Python que traiga el runner (hoy 3.12/3.13). Nadie ejecuta nunca la suite en **3.11**, que es la
versión que `spec/VALIDADOR.md:12` declara como mínima («Python 3.11+, solo biblioteca estándar»), ni
en **macOS**, que es la plataforma de todos los pueblos que usan `screencapture`, `pyobjc`, `brew` o
`launchd`.

*Arreglo*: `strategy.matrix` con `python-version: ["3.11", "3.13"]` y `os: [ubuntu-latest,
macos-latest]` en el job `verificar` (el de `calibracion` puede quedarse en uno solo). *Coste*: 4
líneas y ~4× minutos de CI, que en un repo público son gratis. *Riesgo*: puede sacar rojos reales —
que es el objetivo.

### B-36 · BAJO · El CI no ejecuta `cosmos acertar --minimo` ni `cosmos estado`

`PENDIENTE-DARIO.md:153` dice «hasta entonces `cosmos acertar --minimo` sale 1 y el CI no cobra
listón». Correcto hoy; pero cuando exista el holdout v2 nadie se acordará de añadir el paso. Dejarlo
escrito ya, comentado, con la fecha en que se descomenta.

### B-37 · BAJO · No hay `dependabot.yml`, `CODEOWNERS` ni plantillas en `.github/`

`.github/` contiene un único fichero. `requirements-dev.txt` fija versiones a mano y su propio
comentario dice que el lock con hashes «se declara como mejora pendiente». Un `dependabot.yml` para
`github-actions` y `pip` lo automatiza, y es gratis en repos públicos.

### B-38 · BAJO · `cosmos mapa` avisa de su coste con una cifra escrita a mano

> `mapa   … CARO: sobre la galaxia real son ~3.700 tokens, el 90 % del presupuesto de entrada`
> — `cosmos --help`

Medido hoy: la salida de `cosmos mapa` son 11.688 bytes ≈ 3.700 tokens con la heurística v3, y el
presupuesto es 4.000 → 92,5 %. La cifra acierta **hoy**; es exactamente la clase de número que este
repositorio prohíbe escribir a mano (`GOAL.md:46`, hallazgo H11). *Arreglo*: calcularlo con
`medir.tokens()` al construir la ayuda, o quitar la cifra y dejar «CARO: más que el recorrido guiado;
`cosmos medir` da el número».

---

## 9. Batería ejecutada

Todo lo de abajo se ejecutó desde `<casa>/cosmos` (raíz del repo) con
`python3` = **Python 3.14.3**. La suite se corrió **sola**, sin nada pesado en paralelo.

| # | Comando | Línea decisiva |
|---|---|---|
| 1 | `git rev-parse HEAD` | `892f669e70ed1b47f45a311ef5578a00e1593f01` |
| 2 | `git status --porcelain \| wc -l` | `0` (al empezar) |
| 3 | `python3 -m unittest discover -s tests -t .` | `Ran 359 tests in 75.119s` · **`FAILED (failures=1, skipped=2)`** · `EXIT=1` |
| 4 | *(el fallo)* | `FAIL: test_el_sello_v1_esta_comprometido_desde_2026_09_02` → `AssertionError: 37 != 0` (`tests/test_juez_honesto.py:462`) |
| 5 | `python3 -m unittest discover -s puente/tests -t .` | `Ran 139 tests in 6.847s` · `OK` |
| 6 | `python3 -m puente.tests.mutaciones` | **`76/79 invariantes vistas fallar`** · `EXIT=1` (verdes: M63, M64, M76) |
| 7 | `python3 -m cosmos validar` | `COSMOS  verde (2 saltos activos: P01, caduca en 7 d; P02, caduca en 7 d)  0 errores` · 0,86 s |
| 8 | `python3 -m cosmos validar --json` | `"codigo_salida": 0, "configuracion_por_defecto": false, "errores": []` + los 2 saltos |
| 9 | `python3 -m cosmos medir` | `Peor con agua ... 3.701 tokens` · `Presupuesto ..... 4.000  OK, quedan 106 tokens con el margen calibrado (+5,2 %)` · 0,70 s |
| 10 | `python3 -m cosmos medir --config ejemplo.toml` | `Entrada base .... 134` / `Universo ........ 440` / `Descarga ........ 53,9 %` → **no coincide con `spec/MEDIDOR.md`** (B-04) |
| 11 | `python3 -m cosmos estado` | bloque idéntico al de `PROGRESS.md:23-76` (468 nodos, 22 oficios, 297 pueblos) · 0,15 s |
| 12 | `python3 -m cosmos estado --json` | `EXIT=0`; `sin rival nombrado 69` · `sin apartado de avisos 38` · `sin fecha de comprobacion 54` |
| 13 | `python3 -m cosmos acertar` | `Ajuste 38/50 (76 %)` · `Validación 6/20 (30 %; IC95 14–52 %)` · `Historia git ... QUEMADO` · 1,60 s |
| 14 | `COSMOS_HOLDOUT=/tmp/no-existe python3 -m cosmos acertar` | `Validación ..... NO DISPONIBLE` (degrada honestamente ✅) |
| 15 | `python3 -m cosmos buscar montar un bot de trading` | 5 resultados, el 2.º es `trading/bots/codigo-de-bot` · 0,26 s |
| 16 | `python3 -m cosmos abrir trading/bots/codigo-de-bot` | verde (README:54 ✅) |
| 17 | `python3 -m cosmos abrir toxiproxy` | verde, con URL/licencia/★ en la 1.ª línea (README:55 ✅) |
| 18 | `python3 -m cosmos abrir trading/backtesting` | **`no existe 'trading/backtesting'`** · `EXIT=1` — es el ejemplo de `abrir --help` (B-28) |
| 19 | `python3 -m cosmos abrir backtesting` | verde → `trading/estrategia/backtesting` |
| 20 | `python3 -m cosmos --version` | `error: the following arguments are required: comando` · `EXIT=2` (B-08) |
| 21 | `python3 -m cosmos saltar --listar` | `ACTIVO P01 … / ACTIVO P02 …`, caducan el 2026-09-10 |
| 22 | `python3 -m cosmos saltar --help` | `codigo … (E00–E21, G01..G05)` — sin `P01/P02` (B-06) |
| 23 | `python3 -m cosmos proyectar --help` | `usage: python3 -m cosmos …`; solo `iniciar` tiene `help=` (B-09) |
| 24 | `python3 -m cosmos configurar --comprobar` | `rojo — no hay perfil en ~/.cosmos/perfil.toml` (correcto, mensaje accionable) |
| 25 | `python3 -m cosmos mapa \| wc -c` | `11.685` bytes (la ayuda dice «~3.700 tokens, el 90 % del presupuesto»: consistente hoy, escrito a mano — B-38) |
| 26 | `python3 -m puente.secretos --help` | `[--indice \| --todo]`, **no hay `--historia`** (§7.4) |
| 27 | recorrido propio de los 454 nodos con frontmatter | 0 con hijo único · 0 resúmenes > 120 · 0 pueblos sin URL/`origen: propio` · 3 países homónimos bajo padres distintos (legal) |
| 28 | recuento de acentos en los 454 `resumen` | 453 sin acentos, 1 con (`galaxia/agua/oceano-precedencia.md`) — B-29 |
| 29 | `curl api.github.com/repos/<10 repos del catálogo>` | estrellas, licencia y `pushed_at` correctos en los 10 (nada que desmentir) |
| 30 | `curl api.github.com` + `commits/HEAD.atom` × 9 candidatos de los 3 oficios nuevos | todos vivos, ninguno archivado (tabla §7.2) |
| 31 | `git log --all -- research/scratch/q14_analytics.txt \| wc -l` | `2` — la purga de F-05 sigue pendiente |
| 32 | `git log --all -- cosecha/nif-cif-validator.js \| wc -l` | `5` — la purga de F-02 sigue pendiente |
| 33 | tiempo por módulo de test (33 módulos) | `test_un_solo_veredicto` 20,3 s · `test_escala` 13,3 · `test_juez_honesto` 11,7 · `test_arreglos_p3` 9,4 (B-34) |
| 34 | `ls .git/hooks \| grep -v sample` | `pre-commit`, **`pre-push`** (B-16) |
| 35 | `git status --porcelain` al terminar | ver «Deriva» abajo |

### Lo que NO se ejecutó, y por qué

- `python3 -m cosmos generar`, `arrancar`, `compilar` y `enganchar`: **escriben**. El encargo es de
  solo lectura, así que no se tocaron. Que el índice está sincronizado lo demuestra E15 en verde
  (comando 7); que la vista plana lo está, E19.
- `python3 -m puente.gate`: corre la suite sobre una instantánea, y la suite está roja (B-01);
  además `git init` en un temporal es escritura. Se deduce de 3 + 34: **con la suite en rojo, el gate
  local no pasa.**
- La purga de historia de `PENDIENTE-DARIO.md` §1-2: irreversible y requiere el sí de Darío.

### Deriva del árbol durante la revisión (importante)

`git status --porcelain` estaba a **0** al empezar y al terminar muestra:

```
 M cosmos/configurar.py
RM galaxia/agua/oceano-irreversible.md -> galaxia/agua/oceano-autonomia.md
?? progress/mejoras-2026-09-04/
```

`HEAD` no ha cambiado (`892f669`). **Otra ventana está trabajando sobre este árbol ahora mismo**
(renombrando un océano y tocando `cosmos/configurar.py`); no he tocado nada de eso. Todas las
mediciones de este informe son del árbol limpio en `892f669` — la salida de `cosmos medir` del
comando 9 todavía dice `oceano/irreversible`, o sea que se tomó antes del renombrado.

Nota de coherencia derivada: el renombrado `irreversible → autonomia` **no rompe nada del producto**
(comprobado: `grep -rn "irreversible"` fuera de `progress/`, `research/`, `registro/` y `reviews/`
solo da prosa genérica y los dos bloques históricos de `PROGRESS.md:146,168`), pero sí deja
desactualizado el desglose «Lo más caro de la entrada» de esos dos bloques.

---

## 10. Orden de aplicación recomendado

El gate corre la suite sobre una **instantánea del índice**, y `cosmos generar` + `cosmos arrancar`
regeneran índice y vista. Eso fija el orden: **primero lo que devuelve el verde, luego lo que toca
`galaxia/`, y `generar` inmediatamente después de cada tanda que toque un frontmatter.**

### Tanda 0 — devolver el rojo a verde (sin esto no se puede commitear nada)

1. **B-01** — arreglar `tests/test_juez_honesto.py:462`. Es el único bloqueante: con él rojo, el
   pre-commit no pasa y el CI tampoco. No toca `galaxia/`, así que no necesita `generar`.
2. **B-02** — que M63/M64/M76 se construyan su propio holdout de juguete. Después, `mutaciones` vuelve
   a 79/79 y **entonces** se corrigen las cifras de `CIERRE.md:18` y `PROGRESS.md:20-21`.
3. **B-03** — añadir el paso de mutaciones al CI. Va después de 2, no antes, o el CI nace rojo.

*Verificación de la tanda*: `python3 -m unittest discover -s tests -t .` → `OK`, y
`python3 -m puente.tests.mutaciones` → `79/79`, `EXIT=0`.

### Tanda 1 — texto que miente, sin tocar el árbol (cero riesgo para el gate)

4. **B-27** (línea literal con saltos en `CIERRE.md`), **B-21** (§8 de `PENDIENTE` a HECHO),
   **B-20** (`cosecha/retiradas/`), **B-22** (banner en `PLAN-MAESTRO.md`), **B-23**
   (`research/README.md`).
5. **B-12** (quitar `Universo` de `GOAL.md` §3/§4), **B-13** (`moja` en `FRONTMATTER.md`),
   **B-14** (`Árbol`→`Universo` en `MEDIDOR.md`), **B-15** (`cosmos.toml` real en `VALIDADOR.md`),
   **B-16** y **B-17** (pre-push y descripción real del pre-commit en `GUARDARRAILES.md` + README).
6. **B-04** — pegar la salida de hoy en `spec/MEDIDOR.md` **y** añadir el canario que la reejecuta.
   El canario primero visto fallar, como manda `GOAL.md` §7.

*Verificación*: `python3 -m unittest tests.test_cifras_de_las_specs` → `OK` con los canarios nuevos.

### Tanda 2 — CLI y mensajes (código, no árbol)

7. **B-06** (códigos de la válvula compuestos, no escritos a mano) → amplía el canario existente.
8. **B-28** (ejemplo de `abrir --help` + sugerencia en el error), **B-09** (`prog` y `help=` de
   `proyectar`), **B-08/B-33** (`pyproject.toml` + `--version`), **B-38** (cifra de `mapa` calculada).
9. **B-07** — `test_e20_vecino_inexistente` + su mutación. Cierra la exigencia de
   `spec/VALIDADOR.md:150`.

*Verificación*: las dos suites + mutaciones, y `cosmos saltar --help` mostrando `P01`,`P02`.

### Tanda 3 — el árbol (aquí sí hace falta `generar`)

10. **B-18** (`resumen` de `butler`), **B-19** (coletilla de `captura-recortada`), **B-24** (los once
    «esta casa / este arnés / este Mac»), **B-29** (decidir la convención de acentos y aplicarla),
    **B-31** (`eventsourcing` y `python-statemachine` nombrados en `mar-resistencia`),
    **B-32** (`reprozip`: rival o archivo), **B-30** (`TOPE_SESIONES`).
11. **`python3 -m cosmos generar` + `python3 -m cosmos arrancar` + `python3 -m cosmos validar`**, en
    ese orden, en cuanto se toque cualquier `resumen` o `padre`. Y `python3 -m cosmos medir` para
    confirmar que el peor caso sigue por debajo de 4.000 — hoy quedan **106 tokens**, así que
    cualquier resumen que se alargue puede poner E16 en rojo.
12. **B-05** (`rio-configurar.md`) va aquí, no antes: crea un nodo y cambia el catálogo, que se paga
    en toda sesión. Medir antes y después.

*Verificación*: `cosmos validar` verde, `cosmos medir` con margen positivo, y `git diff --stat` del
índice mostrando solo lo esperado.

### Tanda 4 — lo que necesita el sí de Darío (no lo toca un agente)

13. §7.2 los **tres oficios nuevos** (y la decisión sobre mover `mlflow`), §7.1 `scancode-toolkit`,
    **B-25** (qué hacer con los ocho pueblos de instrumentación en `agentes-ia`), **B-26**
    (`revision-cruzada` y su clave).
14. §7.3 **holdout v2** — desbloquea la cifra honesta y las tres mutaciones del punto 2 quedan
    respaldadas por un fichero real.
15. §7.4 **`secretos --historia`** + la purga de `PENDIENTE-DARIO.md` §1-2 (irreversible: bundle
    previo, `filter-repo`, `push --force`).
16. **B-35** (matriz de CI con 3.11 y macOS) — se puede hacer sin permiso, pero conviene después de la
    tanda 0 para que el rojo que saque sea informativo y no ruido.

### Regla transversal

Con **106 tokens** de margen en el peor caso (`ciberseguridad` + agua), **toda tanda que toque un
`resumen`, un océano o un mar termina con `cosmos medir`**. Y como hay dos saltos vivos que caducan
el **2026-09-10**, conviene cerrar las tandas 0-3 antes de esa fecha: al vencer, el gate vuelve a
rojo y el trabajo pendiente se mezcla con el rojo nuevo.
