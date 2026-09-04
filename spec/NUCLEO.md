# Núcleo normativo — las definiciones de las que todo depende

Este fichero existe porque la revisión adversarial de Codex (`reviews/codex-revisa-specs.md`)
demostró que las specs anteriores permitían **dos implementaciones conformes que discrepan sobre el
mismo árbol**. Eso no es una ambigüedad menor: es que la especificación no especificaba.

Aquí se fijan las seis definiciones que faltaban. Todo lo demás las usa; ninguna se redefine en otro
sitio. Cuando otra spec y este fichero discrepen, **gana este**.

---

## 1. Identidad: la referencia es la ruta completa

**El problema, tal como lo encontró Codex (B1):** con `padre: provincia/revision`, si existen dos
provincias llamadas `revision` bajo planetas distintos —perfectamente legal, porque E06 solo exige
unicidad **entre hermanos**— la referencia apunta a dos sitios. El árbol puede estar en verde y ser
ambiguo, y dos validadores correctos reconstruyen árboles distintos.

**Resolución:** `padre`, `ilumina` y `orbita` contienen la **ruta completa**, no `<nivel>/<nombre>`.

> **ruta(n)** = los `nombre` de los ancestros de `n`, desde la galaxia (excluida) hasta `n`
> (incluido), unidos por `/`.

```yaml
padre: web/tienda-online/calidad     # sistema-solar 'web' > planeta 'tienda-online' > provincia 'calidad'
```

- La galaxia tiene `ruta = ""` y se referencia como `""`, cadena vacía.
- Sus hijos directos tienen `ruta = <nombre>`.
- El nivel no aparece en la ruta: cada nodo ya declara el suyo en `cosmos:`. Meterlo otra vez es
  información duplicada que puede contradecirse, y lo que puede contradecirse acaba haciéndolo.

**Por qué esto sí es unívoco, y conviene verlo:** E06 garantiza que dos hermanos no comparten
nombre. Por inducción sobre la profundidad, dos nodos distintos no pueden compartir ruta completa —
si la compartieran, en algún nivel habría dos hermanos con el mismo nombre, que es justo lo que E06
prohíbe. La unicidad global sale gratis de la unicidad local; no hace falta un identificador nuevo
ni exigir nombres únicos en todo el árbol.

**La aciclicidad sale gratis, y por eso E04 se retira.** Para todo sólido `n` distinto de la
galaxia, `ruta(n) = ruta(padre(n)) + "/" + nombre(n)` y `nombre` cumple `^[a-z0-9-]+$`, luego tiene
longitud ≥ 1. Por tanto `len(ruta(n)) > len(ruta(padre(n)))` **estrictamente**. Un ciclo
`n₁→n₂→…→n_k→n₁` haría crecer la longitud a lo largo del ciclo y volvería a su punto de partida:
contradicción. Y si el `padre` no resuelve, salta E02. La galaxia no declara `padre` (E00), así que
tampoco cierra ciclos, y el agua no tiene `padre` en absoluto.

> **E04 («ciclo») queda retirada.** Su hueco en la numeración **no se reutiliza**: los códigos
> siguen siendo E00–E03 y E05–E21. La aciclicidad no se vigila porque el diseño la ganó; fingir
> que se vigila con una comprobación que ningún árbol legal puede disparar es peor que no tenerla
> (`GOAL.md` §7: un verde que nunca ha dado rojo no se distingue de uno roto).

Lo que sí se vigila es la **premisa** del teorema: que la identidad siga siendo la ruta completa.
Si alguien redefine `ruta`, los ciclos vuelven a ser posibles y la retirada de E04 deja de estar
justificada. Por eso existe un canario que mide `len(ruta(n)) > len(ruta(padre(n)))` sobre el árbol
y una meta-prueba que sustituye la identidad y **exige que el canario se ponga rojo**.

**El agua no tiene ruta**, porque no está contenida en nada. Se identifica por `<nivel>/<nombre>`, y
su `nombre` es único **dentro de su nivel** (dos lagos no pueden llamarse igual; un lago y un mar,
sí).

## 2. `contexto_inicial(árbol, nichos=None)`: una definición, byte a byte

**El problema (B2):** `MEDIDOR.md` contaba «índice + océanos + catálogo» sin decir si el catálogo
repite lo que el índice ya trae. Repetía: el índice lista los sistemas solares con su resumen y el
catálogo los listaba otra vez. **Doble conteo**, y con él la métrica principal del proyecto medía
mal.

**Resolución.** `contexto_inicial` es esta secuencia, en este orden exacto:

```
1. indice(árbol)                                   ← lo que genera 'cosmos generar'
2. cuerpo(o) para cada océano o, ordenados por nombre
3. catalogo(árbol, nichos)
```

unidas por un `\n` entre bloques. Y:

> **cuerpo(n)** = el contenido del fichero de `n` **sin su frontmatter** y sin la línea `---` que lo
> cierra, con los espacios del principio y del final recortados.

El frontmatter es metadata de COSMOS: `cosmos:`, `nombre:`, `padre:`. **Nunca llega al contexto del
modelo**, así que contarlo infla justo lo que se paga siempre. Esto resuelve además H3 de
`reviews/claude-revisa-codigo-ronda1.md`.

> **catalogo(árbol, nichos)** = una línea por nodo, **en árbol indentado y en profundidad**
> (alfabético por ruta, que agrupa cada familia), **excluyendo todo lo que ya aparece en el
> índice** (la galaxia, los sistemas solares y los océanos):
>
> | Nivel | Línea |
> |---|---|
> | hijo directo del sistema (intermedio o pueblo) | `<nicho>/<nombre>: <resumen>` — el ancla del árbol |
> | intermedio o pueblo más profundo | `<nombre>: <resumen>`, indentado dos espacios por nivel |
> | rio (`momento: trabajo`, por defecto) | `rio/<nombre>: <resumen>`, tras el mapa |
> | rio (`momento: mantenimiento`) | solo el nombre, en una línea agrupada |
> | mar, lago, lluvia, estrella, luna | *(no aparece)* |
>
> Solo aparecen los sólidos cuyo sistema está en `nichos`. El nombre corto basta para invocar:
> E18 exige nombre de pueblo único en toda la galaxia y `cosmos abrir <nombre>` resuelve.

El árbol indentado sustituyó a la lista de rutas completas el 2026-09-02: en el peor nicho, el
40 % del coste eran prefijos repetidos (medido con tiktoken: 1.452 → 1.093 en ciberseguridad).
La indentación dice lo mismo que decía el prefijo, y leerse como jerarquía —que era el porqué del
orden anterior (H5)— lo hace ahora la forma, no el orden de rango. La contra-métrica puntúa la
misma selección por construcción (`medir.nodos_de_catalogo` es compartida) y conserva las palabras
de la ruta en el texto puntuable, porque esa información el agente la sigue viendo — en la sangría.

`nichos=None` significa **ningún nicho activo**: no aparece ningún pueblo. Una selección como
`nichos=["web", "saas"]` incluye la unión de los pueblos contenidos por esos dos sistemas, y
ninguna skill invocable de los demás. El nicho de un sólido es el primer tramo
de su ruta completa, que por definición es el `nombre` de su sistema solar.

Los ríos aparecen siempre y sin depender del nicho: son los comandos, y un comando que no se sabe
que existe no se invoca. Es el único bloque del catálogo que no se acota, y por eso su resumen se
escribe corto — se paga en cada sesión, como el índice.

Pero no todos los comandos sirven para lo mismo, y el campo opcional `momento` lo declara:

- **`trabajo`** (por defecto) — resuelve el encargo del que trabaja en un oficio.
- **`mantenimiento`** — cuida el repositorio: no lo pide ningún encargo.

Cuáles son de cada clase no se escribe aquí: la lista cambió el mismo día en que se creó el
campo y esta enumeración se quedó con la mitad. La dice el árbol —`cosmos estado`— y la fija
`tests/test_rio_momento.py`, que la lleva escrita a mano **a propósito**: deducirla del árbol
dejaría que quitarle el campo a un río subiera el coste en silencio.

Los de mantenimiento aparecen **nombrados, no descritos**, en una sola línea agrupada. La razón es
la tesis del proyecto aplicada a sus propias herramientas: `enganchar` se ejecuta una vez en la vida
de un repositorio y su resumen viajaba en todos los turnos de todas las sesiones — coste que crece
con lo que existe y no con lo que se usa.

Lo que **no** se hace es esconderlos. Siguen en el catálogo por su nombre, y `cosmos abrir
rio/<nombre>` entrega el cuerpo entero. Ahorrar tokens escondiendo una herramienta no es ahorrar:
es perderla, y el sistema volvería a tener el problema que el índice resuelve. La invariante que
guarda las dos mitades —que dejen de costar y que sigan encontrándose— es
`tests/test_rio_momento.py`, con la lista de cuáles son escrita a mano a propósito: deducirla del
árbol dejaría que quitarle el campo a un río subiera el coste en silencio.

El índice sigue nombrando todos los sistemas solares con una línea, y los niveles intermedios siguen
mostrando por dónde descender. Por eso una skill oculta no vuelve invisible la existencia de su
nicho: se elimina la lista cara de herramientas, no el mapa para encontrarlas.

Esta función es la única definición normativa. El medidor tokeniza exactamente la cadena que
devuelve, y E17 obtiene de ella los cuerpos que coinciden en contexto; ninguno reconstruye por su
cuenta otra noción de «entrada».

## 3. `universo(árbol)` y la descarga, que ya no puede ser negativa

**El problema (H1):** `descarga = 1 − entrada/árbol` daba **−55,1 %** en un árbol de dos nodos,
porque la entrada incluía el índice y el catálogo, que no son nodos, y el denominador solo sumaba
nodos. Numerador y denominador eran universos distintos.

**Resolución:**

```
entrada  = tokens(contexto_inicial(árbol, nichos))
resto    = Σ tokens(cuerpo(n)) para todo nodo n cuyo cuerpo NO está en contexto_inicial
universo = entrada + resto
descarga = 1 − entrada / universo        si universo > 0
descarga = "no_definida"                 si universo == 0
```

Por construcción `entrada ≤ universo`, así que `descarga ∈ [0, 1]` **siempre**. Los océanos entran
en `entrada` y por tanto no vuelven a contarse en `resto`: lo que ya se paga, se paga una vez.

Invariante verificable, y es la que fija el fallo para que no vuelva: **ningún árbol ni selección de
nichos produce una descarga fuera de `[0, 1]`**.

### El agua condicional entra en el presupuesto

`contexto_inicial` no contiene los mares ni los lagos: se cargan solos cuando el `paths:` de su
`moja` casa con un fichero que se toca, sin que nadie los invoque. Publicar solo la entrada base y
el peor nicho ocultaba ese coste — medido el 2026-09-01 en la galaxia real: **817 tokens** que se
activan en la primera línea de Python que se abra, un 32 % por encima del número publicado.

```
agua_condicional(árbol) = { n : n es agua, n no es océano, moja(n) ≠ [] }
agua              = Σ tokens(cuerpo(n)) para n en agua_condicional(árbol)
entrada_con_agua  = entrada + agua
```

Se excluye el agua con `moja: []` (río y lluvia): no se carga sola, se invoca, y su resumen ya se
paga en el catálogo. En `lluvia` el `moja` vacío es obligatorio (E10) justo por esto: con alcance
entraría en `agua_condicional` y se pagaría sin llegar a cargarse nunca. Se excluyen los océanos porque ya están dentro de `entrada`.

`agua` **no** entra en `universo` ni en `descarga`: los cuerpos del agua no-océano ya están dentro
de `resto`, y sumarlos otra vez sería el doble conteo de §2 por la otra puerta. Como
`agua_condicional ⊆ resto`, se cumple `entrada_con_agua ≤ universo` y la invariante de la descarga
sigue en pie.

**E16 compara `entrada_con_agua` con el presupuesto**, no `entrada`. El número que decide rojo o
verde tiene que ver todo lo que se paga sin pedirlo; si no, el presupuesto vigila una parte del
coste y el resto entra por debajo.

E16 no usa el caso base. Mide por separado cada sistema solar, con un único nicho activo, y compara
el presupuesto contra el de mayor `entrada`. Un rojo de E16 nombra ese nicho y el exceso exacto. Las
combinaciones de varios nichos se miden de forma explícita; no redefinen cuál es el peor nicho
individual que vigila E16.

## 4. El método de medición se fija en configuración, nunca se adivina

**El problema (H2):** con `metodo="auto"`, el mismo árbol daba números distintos según la máquina
tuviera `tiktoken` instalado o no. Como E16 pone en rojo al pasarse de presupuesto, **el veredicto
dependía del entorno**: verde en un portátil, rojo en CI, sin que nadie cambiara nada.

**Resolución:** se elimina `auto`. `cosmos.toml` fija el método:

```toml
[medicion]
metodo = "aprox"      # "aprox" | "exacto"
```

- `aprox` es el defecto: reproducible en cualquier máquina, sin dependencias.
- `exacto` **falla en voz alta** si no hay tokenizador. Nunca cae a `aprox` en silencio.
- E16 se evalúa siempre con el método configurado, así que el veredicto es una propiedad del árbol.

`--metodo` en línea de comandos existe para inspeccionar a mano, y **no** puede cambiar el veredicto
de `cosmos validar`.

## 5. Qué se aplana: `pueblo`, del nicho activo

`COMPILACION.md` hablaba de skills y ponía pueblos de ejemplo, sin enumerar. Sin enumeración, E18 no
tiene dominio.

**Resolución:** se aplana exactamente el nivel **`pueblo`** — la skill invocable. No se aplana `rio`
(los comandos tienen su propio directorio plano) ni ningún otro nivel. Hasta el 2026-09-01 el
conjunto era `{ciudad, pueblo}`; `ciudad` se retiró de la taxonomía sin haber tenido nunca un nodo
(`spec/TAXONOMIA.md`), así que el conjunto se quedó en uno.

`cosmos compilar --nicho web` aplana únicamente los pueblos cuyo primer tramo de ruta es `web`. Cada
entrada aplanada exporta **el directorio completo de la skill**, con su `SKILL.md` y los ficheros de
referencia que tenga al lado. En `--modo copia` se excluyen `.git`, `__pycache__` y los ficheros que
empiezan por punto.

**`nichos=None` significa aquí lo contrario que en §2, y se dice en vez de disimularse**
(auditoría A-04): en el catálogo de entrada, «sin selección» es **ningún** pueblo (la entrada base,
lo que se paga sin haber elegido oficio); en `compilar`, «sin selección» es la vista **completa**,
porque el bootstrap de un clon (`arrancar`) tiene que dejar E19 en verde sin que nadie haya elegido
nicho todavía, y el manifiesto registra esa ausencia como `nichos = null` para que E19 compare lo
mismo que se compiló. La CLI sin `--nicho` materializa esa vista completa **y lo imprime** («vista
COMPLETA: N pueblos de todos los nichos»); el runtime acotado se materializa con el flag o con
`[nichos] activos`, que es donde se decide de verdad. `tests/test_nichos_semantica.py` fija las dos
semánticas a la vez: cambiar una sin la otra sale en rojo. Cambiar de nicho convierte las entradas
registradas de los demás nichos en obsoletas y les aplica, sin excepción, la regla por hash de §7.

E18 se comprueba sobre el conjunto `{nombre(n) : cosmos(n) = pueblo}`.

## 6. Orden de validación: lo generado no bloquea al que lo genera

**El problema (interbloqueo, encontrado por Codex):** `compilar` debe fallar si el árbol no valida;
pero E19 (vista plana desincronizada) pone el árbol en rojo, y esa vista es justo lo que `compilar`
viene a reparar. El comando quedaba bloqueado por su propio guardarraíl. Lo mismo con `generar` y
E15.

**El problema, segunda mitad (F11):** la resolución de arriba eximía a cada comando **de su propia**
invariante, no de la del otro. En un árbol recién creado faltan las dos cosas, así que `generar`
mandaba a `compilar` por E19, `compilar` mandaba a `generar` por E15, y **un árbol nuevo no tenía
ningún camino a verde** — que es lo primero que hace quien clona COSMOS sobre otro proyecto (§0 de
`GOAL.md`).

**Resolución — regla general**, y vale para cualquier invariante futura de este tipo:

> **Una invariante que compara el disco contra lo que se generaría no puede bloquear a un comando
> que no la puede reparar** — ni a quien la genera, ni a nadie más.

| Comando | Exige antes de escribir | Comprueba después |
|---|---|---|
| `generar` | todo menos **E15** (la repara) y **E19** (no la toca) | E15 |
| `compilar [--nicho n]` | todo menos **E19** (la repara) y **E15** (no la toca) | E19 para la misma selección |
| `arrancar` | nada: es el bootstrap | todas |
| `validar` | todas | — |

Así `generar` y `compilar` reparan lo suyo sin poder colarse con un árbol roto por cualquier otro
motivo, que es lo que la regla 1 de `COMPILACION.md` protegía de verdad.

`arrancar` es el único que escribe los **dos** artefactos generados, y por eso es el único que deja
un árbol nuevo en verde de una vez. Escribe el índice **solo si no existe**: un índice ausente no
puede engañar a nadie, uno presente y falso sí, y ahí E15 tiene que seguir siendo un rojo real. Si
el índice existe y miente, `arrancar` sale en rojo y no lo toca.

## 7. Manifiesto: escritura atómica, y qué hacer con lo obsoleto

**Escritura atómica.** El manifiesto se escribe en un temporal del mismo directorio y se mueve con
`os.replace`, que es atómico en POSIX. Nunca se escribe en el sitio: una interrupción a media
escritura dejaría un manifiesto truncado, y un manifiesto truncado es peor que ninguno, porque el
compilador se cree lo que dice.

**Concurrencia.** Un fichero de bloqueo `.cosmos/compilar.lock`, creado con `O_CREAT|O_EXCL`. Si ya
existe, el segundo proceso falla diciendo que hay otra compilación en curso. Sin esto, dos
compilaciones simultáneas se pisan el manifiesto y ninguna se entera.

**Entradas obsoletas** (están en el manifiesto pero su nodo ya no existe en el árbol):

1. Si el contenido actual **coincide** con el hash que guardó el compilador, se borra. Es suya y
   nadie la ha tocado.
2. Si **no coincide**, alguien la modificó a mano: **no se borra**, se avisa y se saca del
   manifiesto.

Seleccionar otro nicho equivale, para este algoritmo, a que las entradas registradas fuera de la
nueva selección ya no existan: se vuelven obsoletas. El manifiesto guarda `nichos` (`null` para la
vista completa o una lista para la vista acotada), de modo que E19 no puede validar una selección
contra el artefacto de otra por accidente.

Sin la regla 1, E19 se quedaría en rojo permanente tras eliminar cualquier skill. Sin la regla 2, el
compilador borraría trabajo ajeno, que es exactamente lo que la regla «nunca borra lo que no ha
creado» quería impedir.

**Symlinks:** relativos al directorio de destino, nunca absolutos, para que el árbol se pueda mover
sin romper la vista. Editar a través del enlace es editar la verdad —es el mismo fichero— y está
permitido.

## 8. Claves de `cosmos.toml` que faltaban

```toml
[compilacion]
destino    = ".claude/skills"        # dónde se escribe la vista plana
modo       = "symlink"               # "symlink" | "copia"
manifiesto = ".cosmos/compilado.json"

[medicion]
metodo = "aprox"                     # "aprox" | "exacto"

[presupuesto]
solapamiento = 0.25                  # umbral de E17 (Jaccard entre conjuntos de palabras, frase a frase)
```

### El perfil local acota el catálogo del usuario, no el juez

`cosmos configurar` (2026-09-03) escribe `~/.cosmos/perfil.toml` con los oficios y las herramientas
que esa persona usa. Cuando `cosmos.toml` no fija `[nichos] activos`, mandan los oficios del perfil;
y las herramientas del perfil dejan fuera del catálogo y de la vista los pueblos no elegidos. **E16
no lo mira**: el juez del presupuesto mide siempre el peor nicho con todos sus pueblos, porque el
techo tiene que valer para cualquier perfil, no para el más frugal.

## 9. Semántica de `moja`, y qué significa «lo moja todo» (E11)

**El problema (H08 de `reviews/revision-adversarial-final.md`):** E11 comparaba con el literal
`["**"]`. Cinco escrituras distintas mojaban exactamente lo mismo y pasaban en verde:

```
moja: ["**/*"]    moja: ["**/**"]    moja: ["*"]    moja: ["**/*.*"]    moja: ["./**"]
```

Una invariante que existe para impedir «un párrafo global disfrazado de regla regional» no puede
comprobar una cadena: tiene que comprobar la **cobertura**.

**Semántica normativa del glob.** Sobre rutas POSIX relativas a la raíz del proyecto:

| Elemento | Qué casa |
|---|---|
| `**/` | cero o más directorios completos |
| `**` | cualquier cosa, incluidos separadores |
| `*` | cualquier cosa **dentro de un segmento**, nunca un `/` |
| `?` | exactamente un carácter que no sea `/` |
| cualquier otro carácter | él mismo |

Un `./` inicial se descarta antes de traducir; no significa nada distinto de la raíz.

**Un agua que no es océano es un océano encubierto si se cumple cualquiera de las dos:**

1. **Cobertura total** — el conjunto de sus patrones casa con **todas** las sondas del corpus
   normativo. Es la propiedad semántica: da igual cómo se escriba, si no deja nada fuera es
   global.
2. **Ningún patrón acota por nombre** — algún patrón suyo no contiene un solo carácter
   alfanumérico. `**/*.*` no cubre `Makefile`, así que escapa de (1), pero no nombra nada: acota
   por «tener un punto», que no es una región. Una regla regional **nombra su región**.

El corpus normativo de sondas son doce rutas de un repositorio real, elegidas para que ninguna
familia de ficheros quede sin representar: con extensión y sin ella, en la raíz y anidadas,
ocultas y visibles, con nombre compuesto y con nombre de una letra.

```
main.py · src/app/main.py · tests/test_x.py · web/index.html · docs/guia.md
Makefile · src/Makefile · LICENSE · x · .gitignore · a/b/c/d/e.txt
deep/nested/very/long/path/file.min.js
```

Añadir una sonda solo endurece la comprobación: cubrir un corpus mayor es más difícil, nunca más
fácil. Quitar una la debilita, y por eso el corpus es normativo y vive aquí.

## 10. Qué compara E17: los nodos que se pagan a la vez

**El problema (H12):** E17 medía Jaccard de 4-gramas entre los nodos siempre cargados. Sobre la
galaxia real daba **0,0000 en los diez pares de océanos**, y seguía dando 0,0000 bajando a
2-gramas. Un 4-grama exige cuatro palabras consecutivas idénticas: cualquier paráfrasis lo esquiva,
y la paráfrasis es justo lo que engorda un prólogo. La invariante estaba implementada y no medía
nada.

**Alcance.** E17 compara los nodos que pueden estar en contexto **al mismo tiempo sin que nadie los
invoque**: los océanos (siempre), el agua no-océano con `moja` (por `paths:`) y las estrellas (al
descender a su sólido). No compara pueblos ni ríos: esos se invocan, se pagan una vez y su
duplicación la vigila E18.

**Medida.** La duplicación que importa es **una afirmación repetida con otras palabras**, no un
documento parecido. Por eso se mide afirmación a afirmación:

```
afirmaciones(n) = las frases de cuerpo(n) (cortadas por . ; : y salto de línea)
                  con al menos 4 palabras con contenido
palabras(f)     = las palabras de f, normalizadas, sin las vacías
solape(a, b)    = max sobre pares de afirmaciones (fa, fb) de
                    |palabras(fa) ∩ palabras(fb)| / |palabras(fa) ∪ palabras(fb)|
                  contando solo los pares con |∩| ≥ 3
```

El suelo de **tres palabras con contenido compartidas** es lo que separa una política duplicada de
una coincidencia de vocabulario, y solo funciona con una lista de vacías que incluya de verdad las
partículas gramaticales: mientras `no`, `ni` y `ha` contaban como contenido, «una comprobación que
nunca ha dado rojo» y «una copia que nunca se ha restaurado» —una analogía, no una duplicación—
compartían cuatro «palabras» y puntuaban 0,44.

Sobre la galaxia real de hoy (630 pares de nodos co-cargables, cifra vigilada por
`tests/test_cifras_de_las_specs.py`) ningún par comparte ya tres palabras con contenido: los dos
duplicados que existían se deduplicaron. En la medición que calibró el suelo (2026-09-02, árbol de
entonces) quedaban con el suelo en 3 **exactamente los dos pares** que la revisión adversarial
había señalado a mano leyendo el agua y las estrellas (H13), y **ningún** falso positivo; el
primer par no duplicado quedaba en 0,286 con solo dos palabras compartidas — por debajo del suelo
y por debajo del umbral, con margen por los dos lados.

E17 salta cuando `solape(a, b) > presupuesto.solapamiento`. El error nombra los dos nodos, el
porcentaje y **las dos frases concretas**, porque un rojo que no enseña la frase obliga a leer los
dos ficheros enteros.

## 11. El juez: dónde vive el examen y cuándo vale su cifra

**El problema (auditoría 360, informe B, 2026-09-03):** la cifra de acierto subía de 40 % a 100 %
copiando las veinte consultas del holdout a los resúmenes, con `validar` verde, `medir` más barato
y `--minimo 95` en 0. El examen estaba en claro dentro del repositorio; la única guarda anti-Goodhart
(`brecha = ajuste − validación`) alarmaba cuando el ajuste iba por delante y **felicitaba** cuando
la validación iba por delante, que es la firma exacta del examen filtrado; y el criterio de
corrección se aflojaba con la suite entera en verde. Todo lo de abajo es estructural: ninguna de
estas reglas depende de que alguien se acuerde.

**Dónde vive cada cosa.**

| Pieza | Dónde | Se versiona |
|---|---|---|
| Conjunto de **ajuste** (`pruebas/encargos.json`) | en el repositorio | sí: se mira al trabajar |
| Conjunto de **validación** (holdout) | `~/.cosmos/holdout/encargos-validacion.json`, o `$COSMOS_HOLDOUT`, o `--validacion` | **nunca** (`.gitignore` + prueba que lo exige) |
| **Sello** del holdout (`pruebas/encargos-validacion.SELLO`) | en el repositorio | sí: sha256 del contenido, fecha, `n` y **procedencia** |

Quien tiene el repositorio no puede tener el examen: un holdout que viaja con el sistema que evalúa
es un ejercicio resuelto. El sello ata el contenido exacto y declara **quién escribió el examen y en
qué condiciones** (`--sellar --procedencia "..."`, obligatorio): el primero lo escribió quien ajusta
el árbol, con el árbol delante, y solo se supo leyendo el registro. Un examen ciego lo dicta otra
persona, o sale de encargos reales, sin ver el árbol.

**Cuándo la cifra de validación es publicable.** `cosmos acertar` publica «la cifra que vale» solo si
se cumplen TODAS, y si falta alguna dice cuál y **no da número**:

1. El holdout existe y se lee. Sin él: `Validación ..... NO DISPONIBLE` — nunca se sustituye por la
   cifra de ajuste.
2. **No está versionado** en este repositorio, y **ninguna de sus consultas aparece en la historia
   git** de ningún `.json` (`git rev-list --all --objects` + `cat-file --batch`): un fichero borrado
   sigue legible con `git show`. Si git no está, la procedencia es «no comprobada», que tampoco
   publica. Trivalente, como el veredicto del presupuesto.
3. El sello está **vigente**: existe y su sha256 coincide. Roto (editado después de sellar) o
   ausente, no hay cifra. Antes, con el sello roto, la salida decía «no publicable» y cuatro líneas
   después «la cifra que vale es 40 %», y `--minimo` salía 0.
4. La brecha `ajuste − validación` no baja de **−15 puntos**. Una validación muy por encima del
   ajuste no es un elogio: es la señal más grave que el sistema puede dar (examen filtrado a los
   resúmenes, o ajuste roto).

**Íntegra no es atribuible, y el comando lo dice en cada salida (revisión R-01, 2026-09-03).** Todo
lo de arriba comprueba la **integridad** del examen (fijado, no quemado, no calcado, brecha sana). Lo
que nadie puede comprobar en este repositorio es la **atribución**: que la cifra describa el árbol y
no a quien escribió el examen. La `procedencia` del sello es una declaración de texto libre —vale lo
que vale— y el holdout vive en una ruta que el mismo agente que ajusta el árbol puede leer. Por eso
`cosmos acertar` **nunca dice «la cifra que vale»** y **no ofrece listón** (`--minimo` se retiró):
publica «cifra íntegra, NO ATRIBUIBLE» o «DESCONOCIDA», y con ella lo único verificable:

- **Compromiso**: el primer commit que versiona el `.SELLO` con este sha256, cuántos commits van
  después y cuántos resúmenes cambiaron desde entonces. Prueba que el examen no cambió; no prueba
  ceguera.
- **Calcado**: solape medio (Jaccard) entre cada petición y la línea del catálogo que espera, en la
  validación y en el ajuste. Un examen fabricado copiando las líneas del catálogo —el ataque R-01—
  da 100 %; con tres palabras distintivas por línea, 23 %; el holdout v1, escrito por una persona,
  6 %. Por encima del 20 % la cifra no es íntegra: no es un examen, es una copia. Es una señal
  contra la fabricación burda, no una prueba de ceguera. Se mide también en
  el ajuste porque el ajuste vive en el repo y se puede fabricar igual, y entonces la brecha no
  significa nada.
- **Candidatos**: la cifra se publica «sobre N líneas de catálogo»; una nota sobre 306 pueblos y
  otra sobre 266 no son comparables (R-02), y el gate `P02` exige válvula para toda baja neta de
  pueblos.

Cuando exista un compromiso previo verificable de un tercero (examen firmado por alguien que no
ajusta el árbol, o generado desde encargos reales fuera del repo), este párrafo se revisa y el
listón se reabre. Hasta entonces, la nota del árbol es, con razón, DESCONOCIDA.

**Cómo se publica.** Siempre con su `n` y su intervalo de Wilson al 95 %: `8/20 (40 %; IC95 22–61 %;
n=20)`. Con veinte encargos cada acierto vale cinco puntos; publicar «40 %» a secas es precisión
falsa. Junto a la cifra va la **cobertura** (oficios sin encargo, encargos a profundidad ≥ 3) y la
procedencia declarada en el sello.

**Qué se puntúa.** La **línea literal** que el agente tiene delante: las del índice (`nombre:
resumen`) y las del catálogo tal cual las renderiza `medir.lineas_de_catalogo` — la misma función
que las pinta, para que no puedan divergir. Hasta el 2026-09-03 el juez añadía la ruta completa a
cada línea; la decisión valía diez puntos de la cifra publicada y a favor. Un pueblo profundo
puntúa por su nombre y su resumen, como se lee.

**Qué cuenta como acierto** (`_acierta`): el nodo exacto o cualquiera **bajo** él (bajar de más no
es fallar). Quedarse en el ancestro **no** es llegar, y un prefijo de texto («webs» por «web») no
es un prefijo de ruta. La tabla vive en `tests/test_juez_honesto.py` y las mutaciones M60–M67 de
`puente/tests/mutaciones.py` aflojan cada puerta y exigen el rojo.

**Lo que esto NO hace.** No impide que quien tiene el holdout en su máquina lo lea: por eso la
procedencia se declara y el examen lo escribe alguien que no ajusta el árbol. Y no sube la cifra:
sobre el árbol de hoy el juez arreglado declara el holdout v1 **QUEMADO** (sus veinte consultas
están en la historia git) y la cifra honesta **DESCONOCIDA** hasta que exista un v2 ciego. Bajar
con la báscula honesta es un resultado, no un fracaso.
