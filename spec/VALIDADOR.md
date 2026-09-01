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
| `E01` | Todo nodo sólido salvo la galaxia declara `padre` | nodo huérfano |
| `E02` | El `padre` declarado existe | padre inexistente |
| `E03` | `rango(padre) < rango(hijo)`, estrictamente | contención invertida o plana |
| `E04` | No hay ciclos en la relación de padres | ciclo |
| `E05` | Existe exactamente una galaxia | cero o varias galaxias |
| `E06` | `nombre` es único dentro de su padre | nombre duplicado entre hermanos |
| `E07` | `resumen` presente y ≤ 120 caracteres | resumen ausente o pasado de largo |
| `E08` | `resumen` no repite el `nombre` ni es vacío de contenido | resumen que no informa |
| `E09` | `cosmos` es uno de los 16 niveles válidos | nivel desconocido |
| `E10` | Todo nodo de agua declara `moja` (lista, vacía solo en `rio` y `lluvia`) | agua sin alcance |
| `E11` | Solo `oceano` puede tener `moja: ["**"]` | océano encubierto |
| `E12` | El número de océanos no supera el umbral configurado | exceso de contexto global |
| `E13` | `ilumina` / `orbita` apuntan a un nodo existente y del tipo correcto | adjunto colgado del aire |
| `E14` | Como mucho una estrella por sólido | contexto duplicado |
| `E15` | El índice generado coincide con el que está en disco | índice desincronizado |
| `E16` | El presupuesto de contexto de entrada no se supera | fuga de contexto |

### Sobre `E08`, que es el que se va a discutir

Un resumen «no informa» si, tras quitar guiones y minúsculas, es igual al nombre, o si sus palabras
son un subconjunto de las del nombre más palabras vacías (`la`, `de`, `skill`, `para`, `sistema`).
Es una heurística y va a fallar en algún caso raro. La respuesta correcta a un falso positivo es
escribir un resumen mejor, no relajar la comprobación: el coste de un resumen inútil es permanente
y el de reescribirlo, de un minuto.

### Sobre `E15`, que es el que sostiene todo lo demás

El índice (`COSMOS.md`, el mapa de la galaxia) **se genera**. `cosmos validar` lo regenera en
memoria y lo compara con el de disco. Si difieren, es rojo, y el arreglo es `cosmos generar`, nunca
editar el índice a mano.

Sin esta invariante el sistema entero se cae: un índice editado a mano es un manifiesto central, y
un manifiesto central se desincroniza. Con ella, el índice **no puede** mentir, y esa es la razón
de que el índice pueda estar permanentemente en contexto sin que nadie tenga que confiar en él.

### Sobre `E16`, que es el punto entero del proyecto

`cosmos medir` (ver `MEDIDOR.md`) calcula la entrada base y cada nicho por separado. El validador
falla si el **peor nicho individual** supera `presupuesto_entrada` de `cosmos.toml`, aunque el caso
base quepa. El error nombra el nicho culpable y los tokens exactos que excede. **No es un aviso, es
un rojo.**

Un aviso se ignora. La razón por la que los harness se degradan hasta 27.000 tokens de prólogo no
es que nadie lo supiera: es que el que lo sabía tenía otra cosa que hacer y el aviso no le paraba.
Aquí para.

## Configuración: `cosmos.toml`

```toml
[presupuesto]
entrada = 4000        # tokens máximos de contexto de entrada
resumen = 120         # caracteres por resumen
oceanos = 7           # número máximo de reglas globales
galaxia_lineas = 40   # líneas máximas del índice generado

[raiz]
arbol = "."           # dónde vive el árbol
indice = "COSMOS.md"  # dónde se escribe el índice generado
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
     Cuelga foo de una provincia o de una ciudad.

E11  arbol/mar/estilo.md:6
     'moja: ["**"]' — solo un océano puede mojarlo todo.
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

Por tanto, para **cada una de las 16 invariantes** hay un test que construye un árbol que la viola
y exige el rojo con ese código exacto. Dieciséis rojos comprobados, más un verde sobre el árbol de
ejemplo. Sin eso, la pieza no está terminada.

Además, un test de la meta-invariante: si se rompe el propio validador (por ejemplo, haciendo que
todas las comprobaciones devuelvan «bien»), la batería tiene que ponerse roja. Un validador que
pasa sus propios tests después de haber sido vaciado es decorativo.
