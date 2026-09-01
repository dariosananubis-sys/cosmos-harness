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

> **catalogo(árbol, nichos)** = una línea por nodo, en orden de rango y luego alfabético por ruta,
> **excluyendo todo lo que ya aparece en el índice** (la galaxia, los sistemas solares y los
> océanos):
>
> | Nivel | Línea |
> |---|---|
> | planeta, continente, pais, provincia | `<ruta>` (siempre: forman el mapa de descenso) |
> | ciudad, pueblo | `<ruta>: <resumen>`, solo si su sistema solar está en `nichos` |
> | rio | `<ruta>: <resumen>` |
> | casa, mar, lago, lluvia, estrella, luna | *(no aparece)* |

Ordenar por rango y no alfabéticamente por nivel es deliberado: el catálogo se inyecta en contexto y
tiene que leerse como una jerarquía, no como una lista revuelta. Resuelve también H5.

`nichos=None` significa **ningún nicho activo**: no aparece ninguna ciudad ni ningún pueblo. Una
selección como `nichos=["web", "saas"]` incluye la unión de las ciudades y pueblos contenidos por
esos dos sistemas, y ninguna skill invocable de los demás. El nicho de un sólido es el primer tramo
de su ruta completa, que por definición es el `nombre` de su sistema solar.

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

## 5. Qué se aplana: `ciudad` y `pueblo`, del nicho activo

`COMPILACION.md` hablaba de skills y ponía pueblos de ejemplo, sin enumerar. Sin enumeración, E18 no
tiene dominio.

**Resolución:** se aplanan exactamente los niveles **`ciudad`** y **`pueblo`** — las skills
invocables. No se aplanan `casa` (vive dentro de su skill), ni `rio` (los comandos tienen su propio
directorio plano), ni ningún otro nivel.

`cosmos compilar --nicho web` aplana únicamente las ciudades y pueblos cuyo primer tramo de ruta es
`web`. Cada entrada aplanada exporta **el directorio completo de la skill**, con su `SKILL.md` y sus
casas. En `--modo copia` se excluyen `.git`, `__pycache__` y los ficheros que empiezan por punto.

La API conserva `nichos=None` como compilación completa por compatibilidad. La CLI sin `--nicho`
también conserva esa vista completa; el runtime acotado se materializa siempre con el flag explícito.
Cambiar de nicho convierte las entradas registradas de los demás nichos en obsoletas y les aplica,
sin excepción, la regla por hash de §7.

E18 se comprueba sobre el conjunto `{nombre(n) : cosmos(n) ∈ {ciudad, pueblo}}`.

## 6. Orden de validación: lo generado no bloquea al que lo genera

**El problema (interbloqueo, encontrado por Codex):** `compilar` debe fallar si el árbol no valida;
pero E19 (vista plana desincronizada) pone el árbol en rojo, y esa vista es justo lo que `compilar`
viene a reparar. El comando quedaba bloqueado por su propio guardarraíl. Lo mismo con `generar` y
E15.

**Resolución — regla general**, y vale para cualquier invariante futura de este tipo:

> **Una invariante que compara el disco contra lo que se generaría no puede bloquear al comando que
> lo genera.**

| Comando | Exige antes de escribir | Comprueba después |
|---|---|---|
| `generar` | E00–E14, E16–E19 (todo menos **E15**) | E15 |
| `compilar [--nicho n]` | E00–E18 (todo menos **E19**) | E19 para la misma selección |
| `validar` | todas | — |

Así `generar` y `compilar` reparan lo suyo sin poder colarse con un árbol roto por cualquier otro
motivo, que es lo que la regla 1 de `COMPILACION.md` protegía de verdad.

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
solapamiento = 0.25                  # umbral de E17 (Jaccard sobre n-gramas de 4)
```
