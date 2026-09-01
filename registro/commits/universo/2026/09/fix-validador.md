# Cinco fallos del validador, arreglados: H04, H08, H12, H14, H16

Fecha: 2026-09-01 · Origen: `reviews/revision-adversarial-final.md` · Alcance: `cosmos/`, `tests/`,
`spec/`.

**Estado fijado, porque el árbol muta mientras se escribe.** Al empezar: `243ec87`, 24 rutas
sucias. Al cerrar: base `0b82244`, 226 rutas sucias, cambios sin commitear. **Había al menos otro
trabajo en curso sobre el mismo repo**, y no es un detalle de color: a mitad de esta tarea esa otra
ventana **cerró H01/H02/H09**, y con ello `cosmos.toml` pasó a apuntar a la galaxia, nació
`ejemplo.toml` y **`galaxia.toml` desapareció**. Los comandos de verificación del encargo usaban
`--config galaxia.toml`; aquí se ejecutan contra `--config cosmos.toml`, que desde ese cambio **es**
la configuración de la galaxia. Lo mismo vale para `cosmos/cli.py`, `cosmos/guardarrailes.py`,
`puente/` y los `*.toml`: son suyos, no míos.

Ficheros que sí son míos, con su huella al cerrar:

```
192b019838814d4f45c5da24322e5de649bb0c48b4497fb1ef4fafe79e1ca743  cosmos/validar.py
962378003719d562ba1055b3516927b82d6a0e3cec33a45eb8480befd65fd1b8  cosmos/medir.py
```

**Resultado: 5 arreglados, 83 tests en verde** (52 → 83). De los 31 nuevos, **10 son netos míos**
—11 añadidos y 1 retirado, el que falseaba E04—; los otros 21 son de la otra ventana.
La galaxia queda **en rojo con 2 × E17**: son duplicados reales que E17 no veía y que este encargo
prohíbe expresamente arreglar. Están en §7.

---

## 0. Antes y después, literal

### Antes (`243ec87`)

```
$ python3 -m unittest discover -s tests -v 2>&1 | tail -5
----------------------------------------------------------------------
Ran 52 tests in 0.232s

OK (skipped=1)

$ python3 -m cosmos validar galaxia --config galaxia.toml
COSMOS  verde  0 errores
EXIT=0

$ python3 -m cosmos medir galaxia --config galaxia.toml
COSMOS  medir

  Entrada base .... 1.128 tokens   (índice + océanos + estructura, sin pueblos; estimado, ±desconocido, heurística v1)
  Peor nicho ...... 1.771 tokens   (ciberseguridad, 26 pueblos)
  Universo ........ 22.103 tokens   (estimado, ±desconocido, heurística v1)
  Descarga ........ 92,0 %
  Presupuesto ..... 4.000     OK, quedan 2.229 tokens en el peor caso

  Fuera de COSMOS . no_medido      (system prompt, tools, MCP)

  Lo más caro de la entrada evaluada:
    1.  907 tok  catálogo visible
    2.  525 tok  índice de galaxia
    3.  77 tok  oceano/irreversible
```

### Después

```
$ python3 -m unittest discover -s tests 2>&1 | grep -E "^Ran |^OK|^FAILED"
Ran 83 tests in 2.565s
OK (skipped=1)

$ python3 -m cosmos validar --config cosmos.toml
COSMOS  rojo  2 errores

E17  agua/oceano-verificar.md
     solapamiento 33.3% entre mar/pruebas y oceano/verificar; «Una comprobacion que nunca ha dado rojo no se» ≈ «ha dado rojo no distingue una comprobación que funciona de una rota, así que toda comprobación se»
     Deja la política en un solo nodo co-cargable y que el otro la referencie.

E17  estrellas/web.md
     solapamiento 100.0% entre mar/accesibilidad y estrella/web; «se exige tamano y visibilidad reales» ≈ «se exige tamano y visibilidad reales»
     Deja la política en un solo nodo co-cargable y que el otro la referencie.
EXIT=1

$ python3 -m cosmos medir --config cosmos.toml
COSMOS  medir

  Entrada base .... 1.128 tokens   (índice + océanos + estructura, sin pueblos; estimado, ±desconocido, heurística v1)
  Peor nicho ...... 1.771 tokens   (ciberseguridad, 26 pueblos)
  Agua condicional  817 tokens   (5 aguas por paths:, fuera de la entrada)
  Peor con agua ... 2.588 tokens   (el peor caso + agua condicional)
  Universo ........ 85.308 tokens   (estimado, ±desconocido, heurística v1)
  Descarga ........ 97,9 %
  Presupuesto ..... 4.000     OK, quedan 1.412 tokens en el peor caso con agua

  Fuera de COSMOS . no_medido      (system prompt, tools, MCP)

  Lo más caro de la entrada evaluada:
    1.  907 tok  catálogo visible
    2.  525 tok  índice de galaxia
    3.  77 tok  oceano/irreversible
```

`Entrada base` y `Peor nicho` **no se mueven** (1.128 / 1.771), que es lo que había que comprobar:
el arreglo del agua **añade** una magnitud, no reescribe las que ya estaban. `Universo` sí salta
(22.103 → 85.308) y **eso no es mío**: es la otra ventana metiendo pueblos y reescribiendo un
centenar de `SKILL.md` mientras esto corría. Se midió tres veces en una hora: 22.103, 39.829,
85.308.

---

## 1. H04 — E04 era inalcanzable y su test la falseaba

**Qué pasaba.** `_comprobar_e04` no la podía disparar ningún árbol legal, y
`tests/test_validador.py:85-97` fingía el rojo declarando `class NodoCiclico(Nodo)` con un
`ruta_cosmos` sacado de un campo `ruta-prueba` que ningún parser produce, montando el `Arbol` a mano
sin pasar por `cargar_arbol`.

**Decisión: se retira E04.** El árbol no necesita esa vigilancia porque el diseño ya se la ganó, y
el teorema es corto: para todo sólido distinto de la galaxia
`ruta(n) = ruta(padre(n)) + "/" + nombre(n)` con `nombre` de longitud ≥ 1, luego
`len(ruta(n)) > len(ruta(padre(n)))` estrictamente; un ciclo devolvería la longitud a su punto de
partida habiendo crecido. Si el padre no resuelve, salta E02 antes; la galaxia no declara `padre` y
el agua no lo tiene.

Es una **buena noticia mal contada**, no un agujero: NUCLEO §1 hizo los ciclos imposibles por
construcción. Lo deshonesto era fingir que se vigilaban.

**El hueco no se reutiliza.** Los códigos siguen siendo E00–E03 y E05–E19. Renumerar invalidaría
todos los partes y mensajes de error escritos hasta hoy para ahorrar un número. Queda documentado en
`spec/NUCLEO.md` §1, en la tabla de `spec/VALIDADOR.md` (fila tachada, con motivo) y en un bloque de
comentario en el sitio exacto de `cosmos/validar.py` donde vivía la función.

**Lo que se pone en su lugar, y es la parte que importa.** Retirar una comprobación sin más deja el
sistema sin nada que avise si la premisa cae. Así que se vigila **la premisa**:

- `test_canario_la_identidad_es_la_ruta_completa` — sobre un árbol de cuatro niveles cargado del
  disco, mide que `len(ruta_cosmos) > len(padre)` en cada sólido. Si alguien redefine la identidad,
  los ciclos vuelven a ser posibles y esto se pone rojo.
- `test_meta_el_canario_de_aciclicidad_salta_si_la_identidad_cambia` — **la meta-prueba que lo ve
  fallar**: sustituye `Nodo.ruta_cosmos` por la identidad plana que usaba el test falso y exige
  exactamente 3 fallos (los tres sólidos anidados). Una guarda que nunca se ha visto fallar es
  decorativa; esta se ha visto fallar.
- `test_e04_retirada_ningun_arbol_legal_construye_un_ciclo` — construye el cebo **por el camino de
  verdad** (ficheros en disco + `cargar_arbol`), comprueba que sale E02 y no un ciclo, y afirma que
  ninguna comprobación viva se llama `e04`.

## 2. H08 — E11 se evadía con cinco globs

**Qué pasaba.** `moja == ["**"]`, comparación de cadena. Cualquier otra escritura pasaba.

**Arreglo: se comprueba cobertura, no texto.** `spec/NUCLEO.md` §9 fija por primera vez la semántica
del glob (`**/` = cero o más directorios, `**` cruza separadores, `*` no, `?` un carácter, `./`
inicial se descarta) y define **doce sondas normativas** que cubren todas las familias de fichero:
con extensión y sin ella, en raíz y anidadas, ocultas y visibles, nombre compuesto y nombre de una
letra. Un agua que no es océano es un océano encubierto si:

1. **cobertura total** — sus patrones casan con las doce sondas; o
2. **ningún patrón acota por nombre** — algún patrón suyo no tiene un solo carácter alfanumérico.

La segunda cláusula no es un parche: nombra la propiedad real, **una regla regional tiene que
nombrar su región**. Es la que caza `**/*.*`, que escapa de la primera porque no cubre `Makefile`
pero no acota por nada salvo «tener un punto».

Los ocho globs del test van rojos: los cinco del informe (`**/*`, `**/**`, `*`, `**/*.*`, `./**`),
más `*/**`, `**/?` y `*/*`. Y hay un caso que ninguna de las dos cláusulas por separado veía y que
la primera sí caza: `["**/*.*", "**/[A-Za-z]", "**/M*", "**/L*"]` — cuatro patrones anclados que
**sumados** no dejan fuera ninguna sonda.

Contra-prueba en verde (`test_verde_e11_un_mar_que_nombra_su_region`): `**/*.py`, `**/test/**`,
`src/**` siguen pasando. Los cinco mares reales de la galaxia, también.

## 3. H12 — E17 no medía nada

**Por qué no medía.** El conjunto **no estaba vacío**: `_siempre_cargados` devolvía correctamente
los 5 océanos, o sea 10 pares. Lo vacío era **la señal**. Medido:

```
  k=4 (lo que había)  los 10 pares de océanos -> 0,0000
  k=3                 los 10 pares            -> 0,0000
  k=2                 los 10 pares            -> 0,0000
```

Bajar a 3-gramas —la recomendación del informe— **no arregla nada**. Un n-grama exige n palabras
consecutivas idénticas, y la duplicación que engorda un prólogo es una paráfrasis. Ampliando además
el alcance a océanos + mares + estrellas (31 nodos, 465 pares), el máximo con 3-gramas seguía en
**0,0299**, ocho veces por debajo del umbral de 0,25.

**Arreglo: dos cambios, y hacían falta los dos.**

- **Alcance** — los nodos que se pagan **a la vez sin que nadie los invoque**: océanos (siempre),
  agua no-océano con `moja` (por `paths:`) y estrellas (al descender al sólido). Ciudades y pueblos
  siguen fuera: se invocan, y su duplicación la vigila E18.
- **Medida** — de documento contra documento a **afirmación contra afirmación**: se parte el cuerpo
  en frases con ≥ 4 palabras con contenido y se toma el máximo Jaccard entre pares de frases,
  contando solo los pares que comparten **≥ 3 palabras con contenido**.

**Calibración, contra una verdad independiente.** El suelo no se eligió a ojo: el informe H13 ya
había listado a mano, leyendo el agua y las 21 estrellas, los duplicados reales. Con el suelo en 3 y
el umbral en 0,25 salen **exactamente los dos pares de H13 que están en alcance, y ninguno de los
otros 463**. El primer no-duplicado queda en 0,286 con 2 palabras compartidas: por debajo del suelo
**y** por debajo del umbral, con margen por los dos lados.

Un detalle que cambió el resultado: la lista de vacías **no tenía `no`, `ni` ni `ha`**. Con esas
partículas contando como contenido, «una comprobación que nunca **ha** dado rojo» y «una copia que
nunca se **ha** restaurado» —una analogía, no una duplicación— compartían 4 «palabras» y puntuaban
0,44. Añadirlas es lo correcto y además limpia el ruido. Hay contra-prueba en verde para ese caso
exacto (`test_verde_e17_una_analogia_no_es_una_duplicacion`).

El mensaje de error ahora **enseña las dos frases**. Un rojo que no las enseña obliga a leer los dos
ficheros enteros.

## 4. H14 — el agua no entraba en el presupuesto

**Arreglo: un tercer número, y que ese sea el que decide.** `spec/NUCLEO.md` §3 define

```
agua_condicional(árbol) = { n : n es agua, n no es océano, moja(n) ≠ [] }
agua             = Σ tokens(cuerpo(n))
entrada_con_agua = entrada + agua
```

Se excluye el agua con `moja: []` (río, lluvia): no se carga sola, se invoca, y su resumen ya se
paga en el catálogo. Se excluyen los océanos: ya están dentro de `entrada`.

**`agua` no entra en `universo` ni en `descarga`.** Los cuerpos del agua no-océano ya viven dentro
de `resto`; sumarlos otra vez sería el doble conteo de NUCLEO §2 entrando por la otra puerta. Como
`agua_condicional ⊆ resto`, se cumple `entrada_con_agua ≤ universo` y la invariante «la descarga
nunca sale de [0,1]» sigue en pie — hay aserción explícita de las dos cosas en el test.

**E16 compara `entrada_con_agua`**, no `entrada`. Era el punto: de nada sirve publicar el número si
el que decide rojo o verde sigue mirando otro. En la galaxia real 1.771 + 817 = 2.588 contra un
presupuesto de 4.000, así que **no introduce ningún rojo nuevo**; lo que cambia es que el colchón
publicado pasa de 2.229 a 1.412, que es el de verdad.

El mensaje de E16 desglosa `entrada + agua = total` y su lista de «lo más caro» ahora mezcla partes
de entrada y aguas, ordenadas juntas: si el que sobra es un mar, lo dice.

## 5. H16 — E08 se saltaba con dos palabras

La lista de vacías tenía cinco elementos. Ahora son tres familias explícitas —gramaticales,
vocabulario de la propia taxonomía (`skill`, `sistema`, `pais`, `oceano`, `mar`…) y comodines de
relleno (`cosa`, `varios`, `general`, `mismo`, `todo`…)— y la regla es una propiedad, no una lista
de casos: **un resumen no informa si, quitadas las palabras del nombre y las vacías, no queda ni una
palabra con contenido**.

**El umbral es una palabra, no dos, y eso se midió.** Sobre los 312 nodos de la galaxia, el resumen
más flojo que existe hoy (`estrella/infraestructura`, «Lo que es cierto al tocar infraestructura.»)
aporta **dos**. Exigir una endurece sin un solo falso positivo; exigir dos dejaría el margen a cero.
Histograma de palabras con contenido en la galaxia: `2:1, 3:6, 4:13, 5:26, 6:21, 7:35, 8:58, 9+:...`.

Los cuatro cebos del informe y uno más van rojos; `«Comprueba el contraste de color en cada
pantalla.»` sigue verde. **Cero regresiones de E08 en los 312 nodos de la galaxia y los 16 del
ejemplo.**

---

## 6. Que se ha visto fallar (GOAL §7.1)

Los tests nuevos se ejecutaron contra el **código de antes** (`cosmos/validar.py` y `cosmos/medir.py`
restaurados de `HEAD` sobre una copia, con los tests de ahora):

```
FAIL  test_e04_retirada_ningun_arbol_legal_construye_un_ciclo
FAIL  test_e08_resumen_que_no_informa... (resumen='El pais de calidad')
FAIL  test_e08_resumen_que_no_informa... (resumen='Cosas y mas cosas varias.')
FAIL  test_e08_resumen_que_no_informa... (resumen='Cosas generales del mismo tipo.')
FAIL  test_e11_oceano_encubierto_con_globs_equivalentes  (los 8: **/* **/** * **/*.* ./** */** **/? */*)
FAIL  test_e11_conjunto_de_globs_que_entre_todos_lo_cubren_todo
FAIL  test_e17_parafrasis_entre_un_mar_y_una_estrella
ERROR test_e16_cuenta_el_agua_que_se_carga_por_paths
ERROR test_el_agua_condicional_no_entra_en_la_entrada_pero_si_en_el_presupuesto
Ran 9 tests — FAILED (failures=14, errors=2)
```

Dos matices honestos:

1. Los dos de H14 salen como **ERROR, no FAIL**: el código de antes no tiene el atributo, así que la
   prueba revienta en vez de fallar limpiamente. Es rojo igual, pero no es lo mismo y se dice.
2. Las dos pruebas de `PruebasAciclicidad` **pasan** con el código de antes, y tienen que pasar: el
   canario no mide un fallo, mide la propiedad que hace innecesaria a E04, y esa propiedad ya era
   cierta. Quien las ve fallar es su meta-prueba, que es lo que las salva de ser decorativas.

Dos cebos de E08 (`«La skill de calidad»`, `«Calidad.»`) **ya saltaban antes** y siguen saltando:
son los que la heurística vieja sí cazaba.

## 7. Duplicados reales encontrados — NO arreglados, por encargo

E17 arreglada pone la galaxia **en rojo con 2 errores**. No los toco: `galaxia/` está fuera de mi
alcance y el encargo lo dice expresamente. Los dos coinciden con lo que H13 ya había señalado a
mano, así que no son ruido de la invariante nueva:

| Solape | Nodos | Frase |
|---:|---|---|
| **100 %** | `mar/accesibilidad` ↔ `estrella/web` | «se exige tamano y visibilidad reales» — **idéntica**, palabra por palabra |
| **33,3 %** | `mar/pruebas` ↔ `oceano/verificar` | «Una comprobacion que nunca ha dado rojo no se [distingue de una rota]» ≈ «ha dado rojo no distingue una comprobación que funciona de una rota» |

Los dos son mar↔(estrella|océano): política de un océano o un mar repetida un nivel más abajo. El
arreglo es de una línea en cada caso —borrar la frase del nodo más específico y dejar que la herede
del más general— pero es contenido de la galaxia y lo decide quien la escribe.

Los otros dos casos de H13 (`oceano/secretos` ↔ `mar/custodia`, 0,111 con 1 palabra compartida, y
`mar/resistencia` ↔ `estrella/extraccion`, 0,286 con 2) **quedan por debajo** y E17 no los ve. Es
una limitación conocida y la digo: son paráfrasis más cortas y más libres, y bajar el suelo para
cazarlas mete falsos positivos. Se documentan aquí, no se tapan.

## 8. Efectos colaterales que hay que saber

- **`tests/test_validador.py::test_ejemplo_completo_es_verde` pasó a leer `ejemplo.toml`.** Su
  nombre dice «ejemplo» y desde el arreglo de H02 `cosmos.toml` apunta a la galaxia: sin este cambio
  la prueba validaba el árbol real creyendo que validaba el de juguete. Es un cambio de una línea y
  restaura su intención original.
- **La meta-prueba `test_meta_bateria_rechaza_validador_siempre_verde` se corrigió en dos sitios.**
  (a) Solo recoge las que **exigen rojo** (`^test_e\d\d_`); las contra-pruebas en verde ahora llevan
  prefijo `test_verde_` y **deben** pasar con el mutante — exigirles un fallo sería la misma mentira
  al revés. (b) Contaba registros de fallo, y un test con `subTest` deja uno por subcaso: 26 pruebas
  producían 37 registros y la meta-prueba se ponía roja sola. Ahora cuenta pruebas distintas.
- **`_shingles` y `_siempre_cargados` se borraron** (huérfanos de mi propio cambio), y con ellos el
  import de `contexto_inicial` en `validar.py`.
- **`PALABRAS_VACIAS_E17` se conserva como alias** de `PALABRAS_GRAMATICALES` para no romper a nadie
  que la importe.
- **No he tocado** `galaxia/`, `puente/`, `cosecha/`, `ejemplo/`, `cosmos/cli.py`,
  `cosmos/guardarrailes.py`, `cosmos/modelo.py`, `cosmos/compilar.py`, `cosmos/generar.py` ni
  ningún `*.toml`.

## 9. Spec tocada (normativa primero, código después)

| Fichero | Qué |
|---|---|
| `spec/NUCLEO.md` §1 | Teorema de aciclicidad, retirada de E04, hueco no reutilizable, y el canario que vigila la premisa |
| `spec/NUCLEO.md` §3 | `agua_condicional`, `entrada_con_agua`, por qué no entra en `universo`, y que E16 lo usa |
| `spec/NUCLEO.md` §9 | **Nueva.** Semántica del glob, corpus de 12 sondas y las dos cláusulas de E11 |
| `spec/NUCLEO.md` §10 | **Nueva.** Alcance y medida de E17, con la calibración medida |
| `spec/MEDIDOR.md` | Dos magnitudes nuevas en la tabla, sección «El agua no se puede quedar fuera del número», salida de ejemplo y una verificación exigida más |
| `spec/VALIDADOR.md` | Tabla (E04 tachada, E08 y E11 reescritas), sección de E08 al completo, y la regla de qué hacer con una invariante inalcanzable |
