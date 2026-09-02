---
cosmos: lluvia
nombre: fichas-y-abrir
moja: []
resumen: Parte del arreglo de F10, F15, F20, F21, F22, F24 y un hallazgo nuevo, F25.
---

# El mapa daba direcciones que no llevaban a ningún sitio

Seis fallos del especialista y uno que salió al arreglarlos. Todos comparten forma: algo
**decía** una cosa y **hacía** otra, y nada lo vigilaba.

## F10 — el agua mojaba a todo el mundo por igual

`abrir --con-agua` devolvía los seis mares enteros para cualquier nodo. El filtro comparaba
el nicho contra el glob de `moja` (`nicho in str(moja)`), y como **todos** los `moja`
empiezan por `**/`, la comprobación acertaba siempre. `trading` y `cumplimiento`, que no
comparten nada, recibían idéntica lista: 1.499 tokens de cuerpo en cada apertura. Era el
«cargarlo todo por si acaso» del `GOAL.md` §2, dentro del comando cuyo docstring cita ese
mismo párrafo.

El error estaba en la premisa, no en el `or`: **`moja` es un glob de ficheros, no una
etiqueta de oficio**. Ahora `abrir --tocando <fichero>` casa la ruta real con
`_glob_a_regex`, el mismo motor que usa E11, y sin fichero no devuelve agua — adivinar qué
se toca es indistinguible de devolverlo todo. Y lista **nombre y resumen**, nunca el cuerpo.

    trading + estrategia.py -> criterio, resistencia, revision
    trading + tests/x.py    -> criterio, pruebas, resistencia, revision
    web     + index.html    -> accesibilidad

## F22 — la estrella se enganchaba por el nombre suelto

`ilumina` se comparaba contra `{referencia, nombre}`. `NUCLEO.md` §1 exige la ruta completa
justamente para que dos nodos homónimos bajo padres distintos no se confundan; aceptar el
nombre reabría esa puerta. Hoy no mordía porque no hay colisiones — que es exactamente lo
que §1 dice vigilar con un canario, no lo que autoriza a relajarlo.

## F20 — 38 fichas nombraban guiones que no existían

Citaban `cosecha/<script>`, una ruta relativa a la raíz de COSMOS que `compilar` no copia y
`proyectar` no lleva a ninguna parte: en un proyecto proyectado, esas 38 skills nombraban
ficheros ausentes. Se han colocado los 69 guiones dentro del directorio de su pueblo
(`scripts/`, como los nueve que ya lo hacían) y reescrito las citas. Los 69 pasaron antes el
escáner de secretos; los tres hallazgos eran falsos positivos (`ta**sk-**notification`,
`ejemplo@dominio.com`).

## F24 — dos convenciones de ficha conviviendo

207 fichas con `· MIT · 3.968★ ·` y 45 con ` - MIT - 3.968 estrellas - `. Normalizadas a la
primera, que además lleva la fecha de comprobación. La fecha no se ha inventado: sale del
commit que introdujo cada ficha. Comprobado que no se perdió prosa — las únicas palabras
que desaparecieron del corpus son `cosecha` (165), `estrellas` (48) y `ultimo` (46).

Queda abierto el otro medio F24: **un commit de 38 lleva una identidad de máquina**.
Limpiarlo reescribe la historia y obliga a `--force-with-lease` sobre `main`, que necesita
el sí explícito de Darío. Preparado, no ejecutado.

## F15 y F21 — la spec decía lo que hubo, no lo que hay

`mar/revision` llevaba semanas en el árbol y `spec/UNIVERSO.md` seguía anunciando cinco
mares. Y la motivación de E17 usaba como ejemplo a cazar justo el caso que E17 **deja
pasar**. Ahora la spec separa las dos formas de duplicar —reedición y reformulación— y
publica la tabla medida, con el límite en su sitio.

## F25 — hallazgo nuevo: E17 no hacía lo que su spec decía

Al medir para F21 salió que el «mecanismo» documentado —*trocear en n-gramas de 4 palabras
(shingles)*— **no es el implementado**. E17 compara conjuntos de palabras con contenido,
frase contra frase, con un mínimo de 3 compartidas. La spec describía un algoritmo que el
código no tiene. Reescrita para decir el real.

## Lo que impide que vuelva a pasar

Tres canarios nuevos, los tres vistos fallar:

- `tests/test_abrir.py` — 5 sabotajes del filtro de agua y del emparejado de estrella.
- `tests/test_spec_al_dia.py` — los mares de la spec contra los del disco, y el recuento
  escrito en prosa contra la tabla.
- `tests/test_e17_limite.py` — las cifras publicadas salen de la función. Falsear una en la
  spec pone la prueba roja.

Es la lección de siempre en este repositorio: **lo que se escribe a mano se desincroniza**.
Donde no se puede generar, se compara.

---

# Segunda tanda: la métrica se estaba mintiendo, y luego yo a ella

## El resumen raíz decía 20 oficios y 5 aguas

Son 21 y 6. Es la **primera línea que lee cualquier agente**, y llevaba semanas
equivocada — anotada en un parte anterior y no arreglada. Ahora la escribe un recuento,
no la memoria de nadie.

## La contra-métrica puntuaba sobre menos árbol del que existe

`_lineas_del_catalogo` armaba los candidatos con `catalogo_visible`, que **no incluye los
sistemas solares**: 309 líneas de profundidad 1, 2 y 3, y ni una de profundidad 0. Los 21
oficios viven en el índice, que el agente tiene delante igual. Los quince encargos cuya
respuesta es un oficio solo podían acertar de rebote, por un nieto, compitiendo contra el
catálogo entero: «que google encuentre mi web» salía en el puesto **83**.

No medía el árbol. Medía un recorte que ningún agente ve. Arreglado, y sin tocar una sola
ficha: **44 % → 62 %**.

## Y dos encargos pedían rutas que no deben existir

`saas/facturacion` y `automatizacion/firma` no están en el árbol: `gobl` y `docuseal`
cuelgan directamente de su oficio. Crear el país intermedio para que la prueba pasara
habría sido un nivel de un solo hijo — el que `cosmos estado` marca como relleno porque no
agrupa y cobra su resumen. Se corrigió el encargo, que era lo que estaba mal.

## Lo que no funcionó, y por qué se dice

Dos intentos de mejorar el ordenador de resultados:

- **Recorte de sufijos** (`encuentre`/`encuentren` son la misma palabra menos una `n`):
  +4 puntos. Se queda.
- **Factor de cobertura de la consulta**, para que casar un término genérico en una línea
  corta no ganara —«una app para iphone y android» llevaba a un motor de trading—: la
  hipótesis era buena y **el resultado fue peor** (validación 50 % → 45 %). Revertido. Se
  anota aquí para no volver a intentarlo sin datos nuevos.

## Lo importante: la métrica ahora se vigila a sí misma

Al mejorar tres resúmenes el acierto subió a 68 %. Sonaba bien hasta que lo medí contra
**veinte encargos escritos aparte, que no guiaron ninguna decisión**: 50 %.

| | Antes | Después |
|---|---:|---:|
| Encargos de ajuste (los que se miran) | 48 % | **66 %** |
| Encargos de validación (los que no) | 45 % | **50 %** |

Dieciocho puntos donde miraba, cinco donde no. Eso no es un árbol que lleve mejor: es
puntería sobre las preguntas conocidas — el mismo Goodhart contra el que se escribió
`acertar`, un piso más arriba.

Así que el contraste va **dentro del comando**: `cosmos acertar` publica las dos cifras,
dice que la que vale es la de validación, y denuncia la brecha cuando pasa de diez puntos.
`--minimo` se cobra sobre la validación: dejar que el listón lo mida el conjunto que se
mira al trabajar es dejar que el examinando escriba su propio examen.

**La cifra honesta de COSMOS hoy es 50 %**, no 66 %. Y el techo del método léxico está
cerca: los diez fallos de validación están todos en la lista, la mayoría en los diez
primeros. Subirlo de verdad pide mejores resúmenes en general —no los de esta lista— o un
ordenador que entienda sinónimos, que necesita un modelo y cuesta dinero (`GOAL.md` §5).

Cinco sabotajes más vistos fallar, incluido el del `--minimo` cobrado sobre el conjunto
equivocado.

---

# Tercera tanda: los guards estaban apagados y nadie lo sabía

## F19 — con el `cwd` en un subdirectorio, los cinco guards callaban

Reproducido antes de tocar nada, con el mismo evento y solo el directorio cambiando:

    cwd=<repo>            -> deny
    cwd=<repo>/galaxia    -> (mudo)
    cwd=<repo>/cosecha    -> (mudo)
    cwd=/tmp              -> (mudo)

`cosmos.toml` se buscaba **solo** en `cwd`. Ahora se busca subiendo hasta la raíz, como
hace `git` — y no solo desde el `cwd`: también desde **la ruta del fichero que se va a
tocar**, que es el caso que de verdad importa. Un evento que escribe en
`<repo>/galaxia/COSMOS.md` con el directorio de trabajo en `/tmp` no lo protegía nadie.
Los cuatro casos deniegan hoy, y un repositorio que no usa COSMOS sigue en silencio.

## F19b — y cualquier excepción se tragaba devolviendo 0

Un guard reventado y un guard que aprueba se veían igual. La política se parte por lo que
el guard hace: `PreToolUse` (G03, G04) **deniega** cuando no puede evaluar —su trabajo es
denegar, y la válvula sigue ahí para seguir a propósito— y los demás pasan pero escriben
la línea en `.cosmos/cierres.log`. Documentado en `spec/GUARDARRAILES.md`, sección nueva.

## F18 — una lectura truncada contaba como lectura completa

`_lectura_completa` daba por buena toda lectura sin `limit`. El runtime lee 2.000 líneas
por defecto y **no lo pone en `tool_input`**, así que un fichero de 5.000 quedaba marcado
como leído entero habiendo entrado el 40 %. El docstring ya decía lo correcto —*«el trozo
que falta es justo el que importa»*—; el código decía otra cosa. La ausencia de `limit` se
trata ahora como el tope implícito del runtime.

Comprobado que no rompe nada hoy: `lecturas_exigidas` está vacía en este repositorio, así
que el arreglo protege cuando se configure en vez de estorbar ahora.

Cinco sabotajes más vistos fallar. 111 pruebas en `puente`, verde.

---

# Cuarta tanda: los 21 oficios, y los verbos que se pagaban sin usarse

## Los resúmenes de oficio hablaban en el idioma del gremio

`visibilidad` decía *«Que te encuentren: SEO tecnico, buscadores con IA y contenido»* y
`cientifico`, *«Calculo numerico, simulacion, analisis cientifico y reproducibilidad»*.
Bien escritos, y sin una sola palabra de las que usa quien pregunta: nadie escribe
«reproducibilidad», escribe «que mi simulacion se pueda repetir igual».

Reescritos los 21 con un criterio uniforme —**nombrar el trabajo con las palabras de
quien lo pide**— y con el mismo presupuesto de caracteres: 1.397 antes, 1.368 después.

| | Antes | Después |
|---|---:|---:|
| Encargos de ajuste | 66 % | 66 % |
| **Encargos de validación** | **50 %** | **75 %** |

Veinticinco puntos donde no se miraba, y ni uno donde sí. Es la forma de la mejora que no
es puntería: si fuera sobreajuste, habría subido el otro.

## Y luego el presupuesto dijo que no

Ese cambio dejó el árbol en 4.017 / 4.000. No se deshizo ni se subió el límite: se buscó
coste innecesario, y estaba en los propios verbos de COSMOS.

Ocho de los quince ríos no resuelven el encargo de nadie: `enganchar` y `desenganchar` se
ejecutan una vez en la vida del repositorio, `proyectar` cuando se lleva a otro sitio,
`generar` y `compilar` cuando el guard te lo pide por su nombre. Su resumen viajaba en
**cada turno de cada sesión**. Es la tesis del proyecto incumplida por sus propias
herramientas.

Campo nuevo `momento: trabajo | mantenimiento`. Los de mantenimiento se **nombran, no se
describen**, en una línea agrupada — y siguen abriéndose enteros con `cosmos abrir
rio/<nombre>`. Ahorrar escondiendo una herramienta no es ahorrar: es perderla, y hay una
prueba para cada mitad.

Resultado: **3.929 / 4.000**, con los 21 resúmenes nuevos dentro.

## Faltaban dos ríos

`abrir` y `acertar` se añadieron como comandos y nadie les escribió su verbo. Ahora hay
una prueba que compara los comandos del CLI con los ríos del árbol, así que no puede
volver a pasar.

## Lo que queda ABIERTO y hay que decidir

**Con tokenizador real el árbol está en 4.244 / 4.000.** El verde de arriba es del contador
aproximado. Lo elevó el agente del núcleo y lo he confirmado ejecutándolo:

    python3 -m venv /tmp/calib && /tmp/calib/bin/pip install -q tiktoken
    /tmp/calib/bin/python -m cosmos medir --metodo exacto
      Peor con agua ... 4.244 tokens
      Presupuesto ..... 4.000     ROJO, excede en 244 tokens

Recalibrar no lo arregla: solo hace visible el rojo. Son 244 tokens de contenido que
recortar o un presupuesto que subir, y las dos cosas son decisión de Darío, no mía.

Tres sabotajes más vistos fallar, y dos que **sobrevivieron a la primera** y obligaron a
reescribir sus pruebas: el test miraba solo el árbol bueno, así que quitarle el campo a un
río o admitir un `momento` inventado no ponía nada rojo.
