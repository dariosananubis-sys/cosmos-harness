# COSMOS — qué falta y qué se puede hacer mejor

> Revisión de especialista externo, **solo lectura**, 2026-09-02. Encargo explícito: *no* buscar
> fallos —hay otro revisor en eso— sino **lo que falta, lo que sobra y el mecanismo del estado del
> arte que aquí no está**. Calibrado contra `research/ESTADO-DEL-ARTE.md` (29 proyectos).
>
> **Estado del árbol en el que se midió:** `HEAD` del 2026-09-02, `cosmos validar` verde (0 errores,
> 1,16 s), `medir` = entrada 1.664 · peor nicho 2.483 · agua 1.398 · peor con agua 3.881/4.000 ·
> descarga 98,4 % · 247 pueblos · 21 oficios · 32 nodos co-cargables (496 pares).
> Todo número de este informe se obtuvo ejecutando, no leyendo.

---

## Resumen en una frase

COSMOS tiene la **mejor mitad de arriba** que he visto en este espacio —taxonomía sólido/agua,
20 invariantes vistas fallar, válvula con caducidad, medidor con método declarado— y le falta
**la mitad de abajo**: el verbo que carga un nodo, el cierre del ciclo con el runtime que de verdad
paga, y una contra-métrica que diga si todo esto sirve para algo además de ser barato.

---

## Alto impacto

### 1. Falta el verbo. `descender` es un océano, no una operación

**Qué.** Un comando `cosmos abrir <ruta>` (río), que imprima `cuerpo(n)` del nodo, el cuerpo de su
**estrella** si la tiene, y los nombres de sus hijos. Opcionalmente `--con-agua` para el agua cuyo
`moja` case con el trabajo en curso, y `--hasta <ruta>` para bajar por el camino entero de una vez.

**Por qué.** Es el hueco más grande del proyecto y no se ve porque todo lo demás está muy bien
hecho. Hoy, la cadena completa de valor es:

| Pieza | Estado |
|---|---|
| Decidir dónde vive algo | `spec/TAXONOMIA.md`, excelente |
| Garantizar que el árbol está bien formado | E00–E20, vistas fallar |
| Saber lo que cuesta | `cosmos medir`, con método declarado |
| **Cargar un nodo cuando toca** | **no existe** |

Tres consecuencias medidas, no supuestas:

1. **El catálogo es un mapa sin direcciones.** El catálogo entrega rutas cosmográficas
   (`rendimiento/velocidad/depuracion`, `ciberseguridad/explotacion`); el disco tiene ficheros planos
   con otro nombre (`galaxia/paises/rendimiento--depuracion.md`,
   `galaxia/paises/ciberseguridad-explotacion.md`). La ruta **no es derivable** del nombre de fichero
   —ni siquiera con una regla, porque conviven `--` y `-` como separador— y el continente
   (`velocidad`, `ofensiva`) desaparece del nombre. Un agente que lee `ciberseguridad/explotacion` en
   su contexto no tiene forma de abrirlo salvo barrer con `grep`, que es exactamente el gasto que
   COSMOS existe para eliminar.
2. **Nada carga jamás una estrella.** `contexto_inicial` = índice + océanos + catálogo
   (`NUCLEO.md` §2), y la tabla de ese mismo párrafo excluye `estrella` del catálogo. `GOAL.md` §4
   promete «Estrella → con su sistema», pero *con su sistema* no lo ejecuta nadie: no aparece en
   `puente/proyectar.py:bloque()`, ni en ningún comando de la CLI (`grep estrella cosmos/*.py`
   devuelve solo el índice y el inventario). Y lo que hay dentro de las estrellas no es decorado:
   `galaxia/estrellas/ciberseguridad.md` es **el límite legal del nicho** —«sin alcance firmado no se
   toca nada»— y `spec/UNIVERSO.md` dice literalmente que va ahí *«para que se cargue siempre que
   alguien entre a trabajar»*. No se carga nunca. El único guardarraíl de doble uso del repositorio
   está escrito en un nodo sin lector.
3. **Los cuerpos intermedios son la mejor prosa del árbol y son inertes.** `pais/explotacion`:
   *«Un fallo sin prueba de explotación es una sospecha. Una explotación fuera de alcance es un
   delito.»* Dos líneas que valen por una página, y ningún camino las pone delante de nadie.

Lo que un experto habría hecho distinto **el primer día**: escribir `abrir` antes que `validar`.
Construir el validador de un árbol que nadie puede recorrer es verificar la forma de un mecanismo
que todavía no tiene motor — y explica por qué cuatro niveles sólidos siguen vacíos: nadie ha
recorrido el árbol lo suficiente como para necesitarlos.

**Coste.** ~80-120 líneas en `cosmos/` (resolución ruta→nodo ya existe: `Arbol.referencia`), un río
nuevo, un test por caso (nodo hoja, nodo con estrella, ruta inexistente, ruta ambigua). Media
jornada. Cero coste de contexto: es un comando, se paga al invocarse.

**Riesgo.** Bajo, y acotado: es aditivo, no toca ninguna invariante. El riesgo real es de *diseño*
—que `abrir` acabe imprimiendo demasiado y se convierta en la fuga— y se ataja con la misma regla
que ya rige el catálogo: imprime el cuerpo del nodo pedido y **los nombres** de sus hijos, nunca sus
cuerpos. Segundo riesgo: que se use `abrir` como excusa para no arreglar la convención de nombres de
fichero; el comando la tapa, no la cura.

**Cómo se sabría que funcionó.** Un test end-to-end que, partiendo **solo** del texto de
`contexto_inicial`, llegue al cuerpo de `ciberseguridad/explotacion` y a la estrella de su nicho sin
un solo `grep`, `find` ni `ls`. Hoy ese test es imposible de escribir; ese es el punto.

---

### 2. El perímetro medido acaba justo donde empieza quien de verdad paga

**Qué.** Cerrar el ciclo con el runtime en dos movimientos: (a) que `compilar` emita el frontmatter
**nativo** que la plataforma exige, y (b) que `medir` incorpore el índice que la plataforma inyecta
por su cuenta, dentro de `entrada` y bajo el mismo presupuesto.

**Por qué.** `spec/COMPILACION.md` elige la opción A —aplanar a `.claude/skills/`— y la razón es
correcta (un router MCP cobraría en todas las sesiones). Pero el artefacto que se produce hoy no
encaja con el destino, y en las dos direcciones posibles el número publicado deja de ser verdad:

- **Si no encaja:** el `SKILL.md` de cada pueblo lleva `cosmos: / nombre: / padre: / resumen:`. La
  plataforma exige `name:` y `description:` (comprobado contra skills nativas instaladas en esta
  máquina: todas las válidas llevan `name` + `description`; el mecanismo de nivel 1 documentado por
  Anthropic es literalmente *«`name` + `description` del frontmatter»*,
  `research/ESTADO-DEL-ARTE.md` §1.1). Un pueblo compilado no es una skill invocable: es un fichero
  de texto en una carpeta. Y entonces la mitad de abajo del sistema —247 herramientas— no tiene
  ningún camino de invocación, porque tampoco existe `abrir` (punto 1).
- **Si encaja** (se arregla el frontmatter): la plataforma inyecta ~100 tok por skill descubierta,
  **siempre**, sin pedir permiso. Con `--nicho ciberseguridad`: 27 pueblos ≈ 2.700 tok que se suman
  a los 3.881 medidos → **~6.600 contra un presupuesto de 4.000**. Sin `--nicho` —que es el defecto
  que la API y la CLI conservan por compatibilidad, `NUCLEO.md` §5— son 247 pueblos ≈ 24.700 tok: el
  número exacto del problema que el `README.md` describe en su primer párrafo.

Y hay un tercer efecto, más fino: cuando encaje, **el catálogo y el índice nativo dirán lo mismo dos
veces**. El catálogo publica `<ruta>: <resumen>` de cada pueblo del nicho; la plataforma publica
`name` + `description` de cada uno de esos mismos pueblos. Es el doble conteo de `NUCLEO.md` §2
—índice contra catálogo, que ya se cazó una vez— repetido en la frontera del proceso, donde el
medidor no mira.

La línea `Fuera de COSMOS . no_medido (system prompt, tools, MCP)` es honesta y ahora mismo es
también el sitio donde se esconde el coste que COSMOS **sí** causa. El system prompt no es de COSMOS;
el índice de skills que COSMOS acaba de escribir en el disco del destino, sí.

**Coste.** (a) Traducción de frontmatter en `compilar`/`proyectar`: pequeña, pero obliga a decidir
qué es `description` —ver «Vale la pena §3»: no es `resumen` tal cual, porque `description` tiene que
decir *cuándo* usar la skill, no solo qué hace. (b) En `medir`, un sumando
`indice_nativo = n_pueblos_compilados × coste_medido_por_ficha`, con el coste **medido** una vez
contra una instalación real y publicado con su método, no estimado a ojo. (c) E16 pasa a comparar
`entrada_con_agua + indice_nativo`. Un día largo, y muy probablemente **rojo el primer día** — que
es el objetivo.

**Riesgo.** Alto y hay que decirlo: es el cambio que puede poner el proyecto en rojo con el
presupuesto actual. Ese rojo, sin embargo, es información, no avería — es el mismo argumento del
factor de calibración de `docs/CALIBRACION.md`: *«un presupuesto que se equivoca a su favor es peor
que no tenerlo»*. Riesgo secundario: acoplarse al formato de frontmatter de un runtime concreto; se
aísla como ya se aisló `bloque_sesion` en `puente/sesion.py`, que es el precedente correcto y ya
está en casa.

**Cómo se sabría que funcionó.** Clonar sobre un repo de prueba, compilar con `--nicho` y comparar
el desglose de contexto que reporta el propio runtime contra lo que dice `cosmos medir`. Que cuadren
dentro del margen publicado. Hoy esa comparación no se puede hacer, y esa imposibilidad es el
hallazgo.

---

### 3. El catálogo es perecedero y nada vigila su fecha de caducidad

**Qué.** Un campo `verificado: YYYY-MM-DD` obligatorio en el frontmatter de `pueblo` (invariante
nueva, E21), un `cosmos caducar` que liste lo que pasó de N días, y CI que lo cante. Todo offline:
lo que se comprueba es la **fecha declarada**, no la red.

**Por qué.** Es la propuesta aburrida, y por eso va aquí arriba. Medido sobre el árbol de hoy:

| | Fichas |
|---|---:|
| Con estrellas / fecha de push en el cuerpo | 162 |
| Dicen `comprobado <fecha>` | 133 (**todas la misma: 2026-09-01**) |
| Dicen `comprobado` **sin fecha** | 67 |
| No dicen nada | 40 |

O sea: 162 fichas afirman un hecho del mundo exterior que envejece solo, 67 lo afirman sin decir
cuándo, y todo el corpus fechado es de un único barrido de un día. Dentro de seis meses una parte
sustancial de esas cifras será falsa y **ningún mecanismo lo dirá**, en un repositorio cuya promesa
literal es *«lo mejor que exista **hoy**»* (`spec/UNIVERSO.md`).

Peor: `spec/UNIVERSO.md` ya tiene la regla —*«lo que no se invoca en tres meses se archiva»*— y es
**una exhortación**. Es decir, el antipatrón que `GOAL.md` §2 prohíbe en la primera página, escrito
en la propia spec que define el contenido. La corrección no es acordarse: es que la fecha sea un
campo y el olvido, un rojo. `ctxlint` ya tiene este check (`staleness`,
`research/ESTADO-DEL-ARTE.md` §4.2) y es el que COSMOS no robó.

Segundo efecto, más valioso que el primero: con `verificado` en el frontmatter, «archivar lo que no
se usa» deja de ser una intención y pasa a ser una consulta. Y el criterio 5 de `UNIVERSO.md` («se
ha usado una vez») se vuelve auditable.

**Coste.** Bajo. Un campo, una invariante con su mutación, un comando de listado, un barrido de
247 ficheros para poner la fecha (mecánico: 133 ya la tienen en el cuerpo). Umbral en `cosmos.toml`
(`[presupuesto] caducidad_dias`), no en el código.

**Riesgo.** El conocido de todo aviso periódico: que caduquen 200 fichas a la vez y el rojo se
vuelva ruido que se salta con la válvula cada viernes. Se ataja con dos decisiones de diseño, no
con disciplina: **escalonar** (que `verificado` no sea la fecha del barrido sino la del último toque
real de cada ficha, lo que reparte los vencimientos solo) y **graduar** (amarillo en `estado`, rojo
solo pasado el doble del umbral). Si aun así satura, es señal de que el catálogo es más grande de lo
que nadie puede mantener — que también es información.

**Cómo se sabría que funcionó.** Adelantar el reloj en un test: con `verificado` vencido,
`cosmos validar` rojo con el nombre de la ficha; con la fecha renovada, verde. Y una mutación que
rompa la comprobación y exija que la prueba se ponga roja, como las otras 18.

---

### 4. La entrada crece con el tamaño del universo, no con el uso

**Qué.** Hacer perezoso también el **mapa intermedio**: que el catálogo despliegue los
continentes / países / provincias **solo de los nichos activos**. De los demás basta el nombre del
sistema solar, que ya está en el índice.

> ⚠️ **Contradice una decisión tomada.** `NUCLEO.md` §2 fija explícitamente que planeta, continente,
> país y provincia aparecen **siempre** («forman el mapa de descenso»), y §2 argumenta que así «una
> skill oculta no vuelve invisible la existencia de su nicho». Sostengo que la decisión era correcta
> con 21 oficios y deja de serlo antes de los 50, por lo que sigue. No lo cuelo como nuevo.

**Por qué.** El catálogo base son 127 líneas y **1.370 de los 1.664 tokens de entrada** — el 82 % de
lo que se paga siempre. De esas líneas, 48 son continentes y países: puro mapa, sin una sola
herramienta. Hoy sale barato porque hay 42 países. La cuenta al crecer:

| | Hoy | 50 oficios, 1.000 herramientas |
|---|---:|---:|
| Sistemas solares (índice) | 21 | ~50 |
| Nodos intermedios (catálogo) | 48 | ~250-350 |
| Entrada base estimada | 1.664 | **~4.000-5.000** |

Es decir: el presupuesto se agota **dibujando el mapa**, antes de que entre una sola herramienta. Y
el fallo tiene la forma exacta que `GOAL.md` §2 describe —coste que crece con lo que existe, no con
lo que se usa— solo que aplicado al índice en vez de al contenido. Es el bug conceptual más caro que
le queda al diseño, y hoy es invisible porque el árbol es pequeño.

El argumento a favor de la decisión actual («que se vea por dónde descender») se conserva entero si
`abrir <sistema>` lista los hijos de ese sistema (propuesta 1). El mapa no desaparece: **deja de
estar precargado**, que es literalmente la tesis del proyecto aplicada a sí mismo.

**Coste.** Pequeño en código —`catalogo_visible` ya filtra pueblos por nicho, es la misma condición
extendida a los intermedios— y grande en consecuencias: E16 mide otra cosa, y todas las cifras
publicadas cambian. Depende de la propuesta 1: sin `abrir`, esto deja al agente sin mapa. **No se
hace antes.**

**Riesgo.** El que declara `NUCLEO.md` §2 y hay que respetar: que un nicho no activo se vuelva
invisible. Se acota con una regla explícita —el índice sigue nombrando **todos** los sistemas
solares con su línea, siempre— así que lo que se pierde es la estructura interna de un oficio en el
que no se está trabajando, y eso es exactamente lo que el sistema promete no cobrar.

**Cómo se sabría que funcionó.** Un test de escala: generar sintéticamente 50 oficios × 20
herramientas y exigir que `entrada` con un nicho activo se mantenga dentro de presupuesto. Ese test
es valioso **aunque no se adopte la propuesta**, porque hoy nadie sabe en qué número se rompe.

---

### 5. Se optimiza el coste sin medir el beneficio: falta la contra-métrica

**Qué.** Un conjunto dorado de ~50 encargos en lenguaje natural, cada uno con la ruta que **debería**
alcanzarse (`"quiero saber por qué esta API va lenta"` → `rendimiento/velocidad/perfilado`), y un
`cosmos acertar` que puntúe, **solo con las líneas del catálogo**, cuántos se resuelven bien. Léxico
y determinista: el BM25 de `puente/lluvia.py` ya está escrito y es la pieza exacta. Cero red, cero
modelo, cero dinero.

**Por qué.** Todo lo que COSMOS mide hoy es **coste**: tokens, presupuesto, descarga, solapamiento.
No hay una sola cifra de si el sistema **acierta**. Eso deja la puerta abierta a Goodhart en su forma
más pura, y el camino está pavimentado: *la manera más barata de pasar E16 es escribir resúmenes
peores*. Recortar un resumen baja `entrada`, pone verde el presupuesto y no dispara nada — y degrada
justo aquello por lo que se paga el resumen. Con 21 oficios se nota poco; con 50 es el modo de fallo
dominante.

Es, además, el hueco que el propio `ESTADO-DEL-ARTE.md` deja registrado: HAM mide *routing
compliance* leyendo el JSONL de sesión (§2.1) y ni siquiera eso hay aquí; los papers de §9 son todos
sobre *qué cargar* y ninguno sobre *si la jerarquía está bien formada* — COSMOS resolvió
brillantemente el segundo problema y no tocó el primero.

Y hay un beneficio lateral que vale por sí solo: escribir los 50 encargos obliga a formular en voz
alta qué se espera del árbol. Media docena de resúmenes se reescribirán solos al ver que ningún
encargo razonable los alcanza.

**Coste.** Medio, y casi todo humano: el conjunto dorado es el trabajo (medio día para 50 entradas
honestas). El puntuador reutiliza `lluvia.py`. Debe vivir como fixture versionada, no como test
frágil: un umbral («no bajar de X aciertos») en CI, no una comparación exacta.

**Riesgo.** Dos, y los dos hay que declararlos en la salida como se declara el límite de E17:
(a) un puntuador léxico **no es un agente** — mide si el resumen contiene las palabras del encargo,
no si un modelo elegiría bien; (b) un conjunto dorado escrito por quien escribió los resúmenes se
puntúa a sí mismo. La mitigación para (b) es la que este repo ya practica mejor que nadie: **lo
escribe uno y lo revisa el otro**, y quien redacta los encargos no es quien redactó las fichas.

**Cómo se sabría que funcionó.** Que un recorte de resúmenes que hoy pone verde a E16 baje la
puntuación y se vea. Es decir: que exista por fin una **tensión** entre dos métricas, en vez de una
sola métrica que solo se puede mejorar en una dirección.

---

## Vale la pena

1. **`allowed-tools` por pueblo.** La plataforma ofrece contención de herramientas por skill, gratis,
   declarativa, y COSMOS —cuya tesis entera es la contención— no la usa en ninguno de los 247
   pueblos. Un pueblo de `ciberseguridad/explotacion` que declara sus herramientas es contención
   real, no metáfora. *Coste:* un campo por ficha, opcional. *Riesgo:* atarse a un runtime; se aísla
   en la traducción de frontmatter de la propuesta 2. Encaja además con `hidden: true`, que la
   plataforma ya soporta y sirve para lo mismo que `--nicho` sin recompilar.

2. **Discriminabilidad del resumen dentro de un nicho (E22).** E17 compara **cuerpos** de nodos
   co-cargables; E18 compara **nombres** al aplanar. Nadie compara los **resúmenes de dos pueblos del
   mismo nicho**, que es la única comparación que decide si el agente elige bien. Es
   `skill-trigger-collision` de `ctxlint` (§4.2 del estado del arte), no robado. La maquinaria de
   E17 sirve tal cual, cambiando el alcance. *Coste:* bajo, reusa código medido. *Riesgo:* falsos
   positivos entre herramientas legítimamente parecidas —dos escáneres— que ya tienen su respuesta
   escrita en `UNIVERSO.md` criterio 2: *«si de verdad empatan, entran los dos y el resumen de cada
   uno dice en qué se distingue del otro»*. La invariante haría cumplible esa frase.

3. **Que `resumen` responda «cuándo», no solo «qué».** Anthropic es explícita: `description` tiene
   que decir *qué hace **y cuándo** usarla*, porque es el texto contra el que se hace el matching.
   Los resúmenes de aquí (93 caracteres de media) casi siempre dicen qué es. E08 solo exige «alguna
   palabra con contenido fuera del nombre», que es un suelo muy bajo. Con 27 herramientas por nicho,
   el «cuándo» es lo único que separa. *Coste:* una pasada de reescritura + endurecer E08. *Riesgo:*
   los resúmenes crecen y con ellos la entrada; el tope de 120 caracteres (`[presupuesto] resumen`)
   ya lo contiene.

4. **Calibrar contra el tokenizador que se paga, no contra un primo suyo.** `docs/CALIBRACION.md` es
   trabajo excelente —78 ficheros, sesgo del 20,4 % detectado y corregido— pero la referencia es
   `cl100k_base`, que es el tokenizador de otra familia de modelos. El `±5 %` publicado es «±5 %
   contra cl100k_base», no «±5 % contra lo que factura». Dos salidas, ninguna cuesta dinero:
   (a) recalibrar contra el desglose de contexto que el propio runtime reporta —es gratis y es la
   verdad—; (b) si no, cambiar la etiqueta a `±5 % vs cl100k_base` y decir que la desviación contra
   el tokenizador real es `no_medida`. La segunda cuesta veinte minutos y es coherente con la regla
   de oro del medidor: nunca publicar un número sin decir de dónde sale.

5. **`cosmos anadir <nivel> --padre <ruta>`.** Hoy, meter una herramienta exige saber: la convención
   de ficheros planos por nivel, el separador del nombre de fichero —que es **inconsistente**:
   conviven `agentes-ia--construccion.md` y `ciberseguridad-explotacion.md`—, el esquema de
   frontmatter de ese nivel, y acordarse de `generar` y `compilar` después. Es el mayor bloqueo de
   adopción, y la inconsistencia demuestra que ni los autores tenían la regla. Un comando que crea
   el fichero, escribe el frontmatter, aplica la convención y valida convierte las cuatro preguntas
   de `TAXONOMIA.md` en un flujo. *Coste:* medio día. *Riesgo:* ninguno relevante; es aditivo.

6. **Salida SARIF en `validar`.** Es el contrato que `cclint` usa para anotar la línea exacta en la
   PR (§4.1). `validar` ya tiene ruta, línea, campo y acción por error: es un renderizador más, junto
   a los que ya existen. *Coste:* muy bajo. *Riesgo:* cero, es una salida opcional.

7. **Detección de contradicciones entre aguas co-cargables.** E17 caza la duplicación; nadie caza la
   **contradicción**, que con 5 océanos + 6 mares + 21 estrellas escritos en momentos distintos es el
   modo de fallo natural. Existe `oceano/precedencia` para resolver el choque **en ejecución**, que
   es la respuesta correcta a un conflicto legítimo y la respuesta equivocada a un defecto de
   diseño. Una heurística barata (afirmaciones con alto solape léxico y polaridad opuesta) caza el
   caso obvio; el resto necesitaría semántica, y eso cuesta dinero. Publicar el límite, como se hizo
   con E17. *Coste:* medio. *Riesgo:* falsos positivos; empezar como aviso en `estado`, no como rojo.

8. **Materia de nivel 3 en los nodos intermedios.** Los pueblos son directorios y pueden llevar
   ficheros de referencia a coste cero hasta que se abren —el patrón L2 de Anthropic y OpenViking,
   ya adoptado. Los países y continentes son ficheros sueltos y no pueden. En cuanto un país necesite
   una plantilla o una tabla larga, se meterá en el cuerpo, que es lo que se paga al descender.
   Convertirlos en directorios ahora es barato; después, una migración. *Coste:* bajo hoy, creciente.
   *Riesgo:* toca la carga del árbol y la convención de ficheros; hacerlo junto con la propuesta 5.

---

## Lo que quitaría

1. **`provincia` y `lago` de la taxonomía.**
   > ⚠️ **Contradice una decisión tomada** (hallazgo H20, `spec/TAXONOMIA.md` + `tests/test_niveles_vivos.py`).

   `cosmos estado` sobre la galaxia real: `lago, luna, planeta, provincia` = **cero nodos**. La
   respuesta de H20 fue correcta a medias: distinguir «nivel muerto» de «nivel que este árbol no
   necesita» estaba muy bien visto, y por eso `planeta` y `luna` se quedan sin discusión —viven en
   los repos destino, y `puente/proyectar.py` los usa de verdad (`planeta.toml`, `raiz_del_planeta`).
   Pero `provincia` y `lago` tienen **un nodo cada uno, en un árbol de juguete escrito para
   mantenerlos vivos**. Esa es, literalmente, la definición que este mismo repo dio al retirar
   `ciudad` y `casa`: *«un nivel sin un solo nodo no es una reserva: es una promesa que el lector se
   cree»*. Un test que fabrica el nodo que justifica el nivel no es evidencia de uso: es la promesa
   con coartada. Sostengo que la regla de `TAXONOMIA.md` —«un nivel existe cuando agrupa de verdad»—
   se aplicó a `ciudad`/`casa` y se dejó de aplicar aquí porque `ejemplo/` daba la excusa.
   *Coste de quitarlos:* el mismo procedimiento de 3 pasos que ya está escrito para volver a meter
   `ciudad`. *Riesgo:* que hagan falta en el primer árbol grande — mitigado porque el camino de
   vuelta está documentado y probado. *Alternativa si no se quitan:* que `test_niveles_vivos` exija
   el nodo en un **árbol real**, no en el ejemplo; entonces el test dice la verdad y decide solo.

2. **Once de los catorce ríos, del catálogo de un repo proyectado.** Los ríos son el único bloque del
   catálogo que **no se acota por nicho** (`NUCLEO.md` §2), y hoy los 14 son comandos de
   mantenimiento del propio COSMOS: `arrancar`, `desenganchar`, `enganchar`, `generar`, `mapa`,
   `proyectar`, `saltar`, `secretos`, `gate`, `compilar`, `estado`. Un agente trabajando en un repo
   ajeno paga ~170 tok en cada sesión por saber que existe `desenganchar`. Dejaría en el catálogo los
   que se invocan mientras se trabaja —`medir`, `validar`, `memoria` y el `abrir` de la propuesta 1—
   y el resto tras una línea: *«mantenimiento del árbol: `cosmos --help`»*. *Coste:* trivial (un
   campo `en_catalogo: false` o un `moja` que lo excluya). *Riesgo:* que un comando deje de
   descubrirse; es exactamente el mismo trato que ya reciben 247 pueblos, y el argumento que lo
   justifica para ellos vale igual aquí.

3. **`cosecha/` fuera del repositorio.** 73 ficheros heredados del harness de origen, con nombres que
   apuntan a herramientas y cuentas de un negocio concreto (`bing-webmaster.py`, `claude-cuenta.sh`,
   `bws-token-set.sh`, `cookies_catalogo.py`). No cuesta un token de contexto, pero `GOAL.md` §5 dice
   *«público-limpio y genérico… cero nombres de cliente»* y esto es material sin destilar en la
   frontera de esa promesa. Lo que valga, se reescribe genérico y entra como pueblo; lo demás, a otro
   sitio. *Coste:* una tarde de triaje. *Riesgo:* perder material aún no destilado — se resuelve
   moviendo, no borrando.

4. **`metodo = "exacto"`.** Es un modo que exige `tiktoken`, que no es dependencia, que CI no puede
   ejercitar (su test sale `skipped`) y que mide contra el tokenizador de otra familia de modelos.
   Es decir: no es más exacto, es exacto **respecto a otra cosa**. Con la propuesta 4 de «vale la
   pena» resuelta, el modo `aprox` calibrado y declarado es mejor por todos lados. *Riesgo de
   quitarlo:* bajo; si se prefiere conservarlo, al menos que su salida diga contra qué tokenizador
   es exacto, porque hoy la palabra promete más de lo que da.

---

## Lo que NO tocaría, y por qué

Esta sección importa tanto como las otras: casi todo lo que hay aquí está resuelto **mejor que en el
estado del arte**, y varias piezas son del tipo que se rompe en silencio si alguien las «mejora».

1. **La distinción sólido / agua.** Es la única idea genuinamente nueva del proyecto frente a los 29
   revisados, y es la que hace que la contención sea compatible con las reglas transversales. Todos
   los demás sistemas tienen un solo tipo de fichero y por eso acaban con reglas locales en el
   fichero raíz. No tocar el eje.

2. **`cuerpo(n)` sin frontmatter, `universo` bien definido y `descarga ∈ [0,1]`** (`NUCLEO.md` §2-3).
   Es aritmética ganada a pulso tras un −55,1 % que delató un doble conteo. Cualquier
   «simplificación» de esas definiciones reintroduce el error, y esta vez sin nadie mirando.

3. **La retirada de E04 con su canario y su meta-prueba.** Demostrar que la aciclicidad se gana por
   construcción y luego **vigilar la premisa** en vez de fingir una comprobación que ningún árbol
   legal puede disparar, es el mejor razonamiento del repositorio. No reponer E04 «por si acaso».

4. **E11 semántica con corpus normativo de sondas.** Comprobar cobertura en vez de comparar con el
   literal `["**"]`, más la segunda condición («ningún patrón acota por nombre») que caza `**/*.*`,
   está por encima de todo lo que hace nadie. El corpus de doce sondas es normativo y está bien que
   viva en la spec: no lo movería ni le quitaría una sonda.

5. **E17 medida afirmación a afirmación, con suelo de 3 palabras con contenido.** Calibrada sobre
   496 pares reales, dos verdaderos positivos, cero falsos, y el primer no-duplicado a 0,286 con
   margen por los dos lados. Y encima el registro honesto de que los 4-gramas daban 0,0000 y la
   invariante «estaba implementada y no medía nada». Eso es ingeniería, no documentación.

6. **La válvula (`saltar`) y su regla de que «verde» nunca aparece sola.** Acotada, con motivo,
   caducable a 30 días, log que solo crece, ruidosa al vencer, local para que la urgencia de uno no
   apague el CI de todos. No he visto nada igual en ningún proyecto del sector. Que la propuesta 3
   de este informe genere avisos periódicos **no** es motivo para relajarla.

7. **`NUCLEO.md` §6: lo generado no bloquea al que lo genera.** La regla general —no solo el parche
   para E15/E19— es de las que cualquiera vuelve a romper en seis meses al añadir la siguiente
   invariante de artefacto. Está bien escrita como regla y no como excepción.

8. **La elección de aplanar en vez de montar un router MCP** (`COMPILACION.md`). El razonamiento
   —«añadir carga permanente para resolver un problema de carga perezosa»— es correcto y no lo
   reabro: mi propuesta 2 no vuelve a la opción B, usa el índice **nativo** que el runtime ya
   inyecta, sin servidor ni tools nuevas.

9. **G05: redacción por patrón de VALOR, no por nombre de campo**, con un solo catálogo compartido
   con el escáner. Es la decisión correcta por la razón correcta («una blocklist de nombres no acaba
   nunca») y el detalle de que dos catálogos separados garantizan que uno se queda atrás.

10. **La disciplina entera de verificación**: 18/18 mutaciones vistas fallar, la meta-prueba que
    rechaza un validador siempre-verde, el test que ejecuta el manejador como proceso aparte con JSON
    por entrada estándar, y el reparto Claude/Codex con premisa invertida donde nadie aprueba lo
    suyo. Es lo que hace creíble todo lo demás, y es lo primero que se erosiona cuando entra prisa.

11. **`registro/` clasificado por nicho antes que por fecha, y `lluvia` que devuelve punteros y nunca
    el cuerpo.** Las dos decisiones son contraintuitivas y las dos son correctas; la segunda es
    especialmente rara de encontrar (todo el mundo devuelve el contenido «por comodidad» y ahí se va
    el contexto).

12. **El `resumen` de un nivel describe el grupo, no la lista de hijos.** Está bien formulado como
    antipatrón en `TAXONOMIA.md` y bien cumplido en el árbol; es la regla que más silenciosamente se
    incumple en todos los harness que he visto.

---

## Lo que se rompe al crecer

Escenario del encargo: **50 oficios, 1.000 herramientas**. En orden de qué cede primero.

1. **La entrada base, con diferencia** — propuesta 4. El catálogo intermedio es O(nodos del árbol),
   no O(uso): de 48 líneas a ~300. Estimación: 1.664 → 4.000-5.000 tok **sin una sola herramienta
   cargada**. Se rompe antes de llegar a los 50 oficios; probablemente sobre los 35.

2. **El índice nativo del runtime** — propuesta 2. 1.000 pueblos compilados sin `--nicho` ≈ 100.000
   tok inyectados por la plataforma. Consecuencia concreta: `--nicho` deja de ser una opción y pasa a
   ser obligatorio, pero hoy **la API y la CLI conservan la vista completa como defecto**
   (`NUCLEO.md` §5, «por compatibilidad»). Esa compatibilidad es una bomba de relojería: el defecto
   correcto a escala es el opuesto.

3. **La discriminabilidad del resumen** — «vale la pena» §2-3. Con 27 herramientas por nicho el
   agente ya tiene que decidir entre fichas parecidas (conviven, p. ej., dos rutas distintas hacia
   accesibilidad); con 50 por nicho elige mal de forma sistemática. **No aparece en ninguna métrica
   actual**: E16 seguirá verde y E17 seguirá verde mientras el sistema deja de acertar. Es el fallo
   silencioso, y por eso la contra-métrica de la propuesta 5 es urgente **antes** de crecer, no
   después.

4. **E18 y los nombres globalmente únicos.** Aplanar exige unicidad global. Con 1.000 herramientas,
   `scan`, `audit`, `deploy`, `bench`, `fuzz` colisionan de verdad. La salida habitual —prefijar por
   nicho— destruye la invocación por nombre humano, que es justo lo que la vista plana existe para
   conservar. Conviene decidir la política **antes** de la primera colisión real, no en caliente.

5. **El tiempo del validador.** `cosmos validar` hoy: **1,16 s** con 32 nodos co-cargables (496
   pares). E17 es cuadrática en pares y, dentro de cada par, en frases. Con 50 estrellas + mares +
   lagos → ~5.000 pares: del orden de 10-15 s. Un gate de pre-commit de 15 s se desinstala, y
   `spec/GUARDARRAILES.md` tiene escrito por qué eso es fatal. Salidas: cachear por hash de cuerpo
   (los nodos cambian poco), o filtrar candidatos con un pre-paso barato antes del cuadrático.

6. **El mantenimiento del catálogo** — propuesta 3. 1.000 fichas con estrellas, fechas y versiones es
   un trabajo a tiempo completo si nadie lo automatiza. Sin `verificado` no habrá manera ni de saber
   cuánto hay pendiente. Y aquí choca una restricción dura del proyecto: refrescar esos datos es
   red, y la red está fuera del camino crítico. La salida coherente es **separar los dos mundos**:
   el validador comprueba la fecha (offline, siempre); un comando aparte y explícitamente opcional
   refresca (con red, nunca en CI, nunca en pre-commit).

7. **`usa:` no impide la duplicación, solo la nombra.** *«Una herramienta vive en un solo sitio»* es
   regla dura, pero lo único que la vigila es E18, **por nombre**. Con 1.000 herramientas y 50
   oficios, dos nichos meterán la misma herramienta con dos nombres distintos y nada dirá nada. La
   invariante que falta es por **identidad externa** (la URL del repositorio de origen, que 162
   fichas ya llevan en el cuerpo): un campo `origen:` en el frontmatter, único en todo el árbol,
   convierte la regla dura en una comprobación de una línea.

8. **El árbol de ejemplo como segundo mundo.** Dos árboles, dos configuraciones, doble CI, y un test
   (`test_niveles_vivos`) cuyo veredicto depende de cuál de los dos se mire. A esta escala es un
   coste menor; con 50 oficios, mantener el juguete sincronizado con la taxonomía real es trabajo que
   nadie hará y una fuente de veredictos contradictorios.

9. **La caché del prefijo.** Hoy el bloque COSMOS vive entre marcadores dentro de `CLAUDE.md`, es
   estático y se lleva bien con el caché del prefijo. En cuanto el «descenso» de la propuesta 1 mute
   ese bloque **durante** la sesión, se entra en el modo de fallo que
   `hierarchical-memory-middleware` documenta de sí mismo (§2.2 del estado del arte): romper la caché
   en cada turno. La regla de diseño, si se implementa el descenso: lo cargado se **añade al final**
   del contexto, nunca reescribe el prefijo. Anthropic tomó exactamente esa decisión en Tool Search
   (§1.3) y está anotada en el propio informe de investigación.

---

## Coda

Tres cosas que este proyecto tiene y casi nadie: **una taxonomía con dos ejes**, **invariantes que se
han visto fallar** y **una válvula que hace más cómodo cumplir que saltarse el sistema**. Sobre esa
base, lo que falta no es más spec — es el otro lado del ciclo: un verbo que cargue, un perímetro de
medición que llegue hasta quien paga, una fecha en cada afirmación perecedera y un número que diga
si acierta. Cuatro piezas, ninguna grande, y las cuatro sostienen el peso de las 21 que ya están.
