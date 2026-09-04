# Especificación del validador — para implementar

Escribe esta pieza **Codex**. Revisa **Claude**, con premisa invertida. Quien la escribe no la
aprueba (`GOAL.md` §6).

## Qué es

`cosmos validar` recorre un árbol COSMOS, comprueba las invariantes de la taxonomía y sale con
código 0 (verde) o 1 (rojo). Es el guardarraíl del sistema: la diferencia entre una taxonomía que
se mantiene sola y un diagrama bonito que se pudre en tres semanas.

Es **offline y sin dependencias externas**. Python 3.11+, solo biblioteca estándar. Nada de red,
nada de `pip install`, nada que pida tarjeta. El parseo de YAML del frontmatter se hace con un
lector propio y **restringido** al subconjunto que este esquema necesita: escalares, listas de
escalares y comentarios. Si aparece cualquier otra cosa, es un error de validación con su línea,
no un intento de interpretación creativa.

Esa restricción es deliberada: un parseador permisivo acepta frontmatter que luego cada
herramienta lee distinto, y eso reintroduce por la puerta de atrás la ambigüedad que el esquema
existe para quitar.

## Invariantes (cada una es un error con su código)

| Código | Invariante | Mensaje |
|---|---|---|
| `E00` | El frontmatter parsea y cumple el esquema: campos obligatorios presentes y de texto, `nombre` con `^[a-z0-9-]+$`, `momento` válido, ningún campo fuera de los permitidos para el nivel, listas bien tipadas, sin YAML fuera del subconjunto (`FRONTMATTER.md`) | error de esquema, con su línea |
| `E01` | Todo nodo sólido salvo la galaxia declara `padre` | nodo huérfano |
| `E02` | El `padre` declarado existe | padre inexistente |
| `E03` | `rango(padre) < rango(hijo)`, estrictamente | contención invertida o plana |
| ~~`E04`~~ | **Retirada.** La identidad por ruta completa hace los ciclos imposibles (`NUCLEO.md` §1). El hueco no se reutiliza | — |
| `E05` | Existe exactamente una galaxia | cero o varias galaxias |
| `E06` | `nombre` es único dentro de su padre | nombre duplicado entre hermanos |
| `E07` | `resumen` presente, ≤ 120 caracteres y en ASCII (se paga en cada sesión; cada acento cuesta una pieza más al tokenizador) | resumen ausente, pasado de largo o con acentos |
| `E08` | El `resumen` aporta al menos una palabra con contenido que no está en el `nombre` | resumen que no informa |
| `E09` | `cosmos` es uno de los 14 niveles válidos | nivel desconocido |
| `E10` | Todo nodo de agua declara `moja` (lista, vacía solo en `rio` y `lluvia`, y **obligatoriamente vacía** en `lluvia`) | agua sin alcance |
| `E11` | Solo `oceano` puede cubrirlo todo: ningún otro agua tiene cobertura total ni patrones que no nombren nada (`NUCLEO.md` §9) | océano encubierto |
| `E12` | El número de océanos no supera el umbral configurado. Con `[compilacion] vista = "anfitrion"` se cuentan solo los océanos del anfitrión: son los que `compilar` lleva al runtime; los de COSMOS viven en el árbol y no entran en ese arnés (`COMPILACION.md` §«Se paga lo que se compila») | exceso de contexto global |
| `E13` | `ilumina` / `orbita` apuntan a un nodo existente y del tipo correcto | adjunto colgado del aire |
| `E14` | Como mucho una estrella por sólido | contexto duplicado |
| `E15` | El índice generado coincide con el que está en disco | índice desincronizado |
| `E16` | El presupuesto de contexto de entrada no se supera | fuga de contexto |
| `E17` | Dos nodos que se pagan a la vez no repiten una afirmación con otras palabras (`NUCLEO.md` §10). Un título, un enlace `[[nota]]`, una ruta o un slug no son afirmaciones: son etiquetas y referencias (medido 2026-09-04: 40 de 63 pares en un arnés real eran cabeceras «Orden literal de … (fecha)» o la misma nota citada). En vista anfitrión, co-cargables son solo los nodos del anfitrión | solapamiento entre co-cargables |
| `E18` | El nombre de un pueblo es único en toda la galaxia: la vista plana no puede colisionar (`COMPILACION.md`) | nombre de pueblo repetido |
| `E19` | El manifiesto de la vista plana coincide con el destino en disco (`COMPILACION.md`) | vista plana desincronizada |
| `E20` | Todo destino de `usa:` existe y no es el propio nodo (`COMPOSICION.md`, `FRONTMATTER.md`) | vecino inexistente |
| `E21` | Un `pueblo` nombra qué ejecutar: URL `http(s)://` en el cuerpo —o `origen: propio` si el guion vive en su directorio— y al menos un bloque de código; `origen: guia` es un playbook propio que se lee, no se ejecuta, y solo se le exige cuerpo (`PUEBLO.md`, contrato 1-3) | pueblo que no nombra nada |
| `E22` | Los ficheros de runtime generados desde nodos con `anfitrion` (reglas, agentes, comandos; `COMPILACION.md` §«Los otros ficheros de runtime») coinciden con sus nodos y con su manifiesto | runtime generado desincronizado |

### Sobre `E08`, que es el que se va a discutir

Un resumen «no informa» si, tras normalizar, **no queda ni una sola palabra con contenido**: se le
quitan las palabras del propio nombre y las palabras vacías, y si el resto es el conjunto vacío, el
resumen no dice nada que el nombre no dijera ya.

«Palabra vacía» aquí son tres familias, y las tres están en el código como una sola lista:

1. **Gramaticales** — artículos, preposiciones, conjunciones, auxiliares (`el`, `de`, `que`, `es`…).
2. **Del propio vocabulario de COSMOS** — `skill`, `sistema`, `pais`, `pueblo`, `oceano`, `mar`,
   `estrella`… Nombrar el nivel al que ya pertenece el nodo no informa de nada.
3. **Comodines de relleno** — `cosa`, `cosas`, `varios`, `varias`, `otro`, `general`, `generico`,
   `todo`, `mismo`… Las palabras que caben en cualquier ficha porque no distinguen ninguna.

La lista corta anterior (`la`, `de`, `skill`, `para`, `sistema`) se saltaba con dos palabras. Medido
en `reviews/revision-adversarial-final.md` (H16): con el nombre `calidad`, tanto
`«El pais de calidad»` como `«Cosas y mas cosas varias.»` pasaban en verde. Con la lista completa
los dos dan cero palabras con contenido y saltan.

El umbral es **una** palabra, no dos. Medido sobre los 493 nodos de la galaxia real: el resumen más
flojo que hay hoy aporta dos palabras con contenido, así que exigir una endurece sin generar un
solo falso positivo, y exigir dos dejaría el margen a cero. Sigue siendo una heurística y va a
fallar en algún caso raro. La respuesta correcta a un falso positivo es escribir un resumen mejor,
no relajar la comprobación: el coste de un resumen inútil es permanente y el de reescribirlo, de un
minuto. Lo que no vale es una comprobación tan floja que nadie la note, porque el resumen es
exactamente lo que se paga en el catálogo, en cada sesión.

### Sobre `E15`, que es el que sostiene todo lo demás

El índice (`COSMOS.md`, el mapa de la galaxia) **se genera**. `cosmos validar` lo regenera en
memoria y lo compara con el de disco. Si difieren, es rojo, y el arreglo es `cosmos generar`, nunca
editar el índice a mano.

Sin esta invariante el sistema entero se cae: un índice editado a mano es un manifiesto central, y
un manifiesto central se desincroniza. Con ella, el índice **no puede** mentir, y esa es la razón
de que el índice pueda estar permanentemente en contexto sin que nadie tenga que confiar en él.

### Sobre `E16`, que es el punto entero del proyecto

`cosmos medir` (ver `MEDIDOR.md`) calcula la entrada base y cada nicho por separado. El validador
falla si el **peor nicho** —su `entrada` más el **agua condicional** que se carga por `paths:` sin
que nadie la invoque, es decir `entrada_con_agua`, definida en `NUCLEO.md` §3 y no repetida aquí—
supera `[presupuesto] entrada` de `cosmos.toml`, aunque el caso base quepa. Cuando la cifra es
estimada se compara **con el margen calibrado encima** (`MEDIDOR.md`, «Calibración»): un guardarraíl
que compara una estimación sesgada a la baja contra el techo se equivoca a su favor justo en el
borde. El error nombra el nicho culpable, los tokens exactos que excede y las tres partes más
caras. **No es un aviso, es un rojo.** El juez es único —`medir.veredicto_de_presupuesto`— para E16,
para el código de salida de `cosmos medir` y para los guardarraíles de sesión.

Un aviso se ignora. La razón por la que los harness se degradan hasta 27.000 tokens de prólogo no
es que nadie lo supiera: es que el que lo sabía tenía otra cosa que hacer y el aviso no le paraba.
Aquí para.

## Configuración: `cosmos.toml`

El de verdad es `cosmos.toml` en la raíz del repositorio (este bloque es su forma; las claves sin
valor por defecto están marcadas):

```toml
[presupuesto]
entrada = 4000        # tokens máximos de contexto de entrada
resumen = 120         # caracteres por resumen
oceanos = 7           # número máximo de reglas globales
galaxia_lineas = 40   # líneas máximas del índice generado
solapamiento = 0.25   # umbral de E17 entre nodos que se cargan a la vez

[raiz]
arbol = "galaxia"           # dónde vive el árbol (obligatoria)
indice = "galaxia/COSMOS.md" # dónde se escribe el índice generado (obligatoria)
registro = "registro"       # la puerta del registro; sus entradas también se validan (opcional)

[medicion]
metodo = "aprox"            # aprox | exacto; el exacto exige tokenizador (docs/CALIBRACION.md)

[compilacion]
destino = ".cosmos/vista-galaxia"          # la vista plana (artefacto generado)
modo = "symlink"                           # symlink | copia
manifiesto = ".cosmos/compilado-galaxia.json"

[nichos]
activos = []                # vacío: ningún nicho activo para el catálogo; la vista completa al compilar
```

Todos los umbrales son configurables y **ninguno es opcional**: si falta el fichero, se usan estos
valores por defecto y el validador lo dice en la primera línea de su salida. Un umbral silencioso
es un umbral que alguien subió sin querer.

## Salida

Legible por humano por defecto, `--json` para máquinas. Cada error con: código, ruta del fichero,
línea si se puede, y **qué hacer** — no solo qué está mal.

```
COSMOS  rojo  3 errores  (presupuesto por defecto: no hay cosmos.toml)

E03  spec/../arbol/pueblo/foo.md:4
     'padre: pueblo/bar' — un pueblo no puede contener a un pueblo.
     Cuelga foo de una provincia o de un país.

E11  arbol/mar/estilo.md:6
     'moja: ["**/*"]' — cubre las 12 sondas del corpus: solo un océano puede mojarlo todo.
     Acota el glob, o cambia 'cosmos: mar' por 'cosmos: oceano' y asume el coste.

E16  presupuesto
     Contexto de entrada 4.812 tokens > 4.000.
     Los 3 resúmenes más caros: ... (ver 'cosmos medir --detalle')
```

Ese último campo —qué hacer— no es cortesía. Un error que solo dice qué está mal invita a
desactivar la comprobación; uno que dice cómo arreglarlo invita a arreglarlo.

## Verificación exigida (esto es parte de la entrega, no un extra)

El `GOAL.md` §7 pide que el validador **se haya visto fallar**. No basta con que pase en verde
sobre un árbol bueno: un validador que nunca ha dicho rojo no se distingue de uno que siempre dice
verde, y ese es un fallo real y frecuente.

Por tanto, para **cada invariante viva** hay un test que construye un árbol que la viola y exige el
rojo con ese código exacto, más un verde sobre el árbol de ejemplo. Sin eso, la pieza no está
terminada.

«Viva» es la palabra importante. Una invariante que **ningún árbol legal puede disparar** no se
tapa con un test que fabrica el caso saltándose el parser o subclasando el modelo: eso es un verde
que no distingue una comprobación que funciona de una rota, que es justo lo que `GOAL.md` §7
prohíbe. Se retira la invariante, se documenta por qué el diseño la hace innecesaria, y se deja en
su lugar **un canario sobre la propiedad que la hacía innecesaria** más una meta-prueba que
sustituye esa propiedad y exige que el canario se ponga rojo. Es lo que se hizo con E04
(`NUCLEO.md` §1).

Los códigos **no se renumeran** al retirar uno: E04 queda como hueco documentado. Renumerar
invalidaría todos los partes, informes y mensajes de error escritos hasta hoy para ahorrar un
número.

Además, un test de la meta-invariante: si se rompe el propio validador (por ejemplo, haciendo que
todas las comprobaciones devuelvan «bien»), la batería tiene que ponerse roja. Un validador que
pasa sus propios tests después de haber sido vaciado es decorativo.
