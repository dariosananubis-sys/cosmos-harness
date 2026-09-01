# COSMOS

Organización jerárquica de contexto para agentes de código.

## El problema

Un harness de agente empieza con un `CLAUDE.md` de veinte líneas y a los seis meses inyecta 27.000
tokens antes de que nadie haya escrito una instrucción. Nadie decidió eso. Pasó.

Pasa porque cada pieza, por separado, tenía razón: esa regla **sí** era importante, esa skill **sí**
había que documentarla, ese aviso **sí** evitó un problema real una vez. El coste de cada decisión
es invisible y el de la suma es enorme, así que la suma no la para nadie.

## El principio

> **No se le pide al agente que gaste menos. Se elimina la razón para gastar.**

La respuesta habitual a un harness gordo es escribir reglas pidiendo mesura: «sé breve», «no leas
ficheros enteros», «usa pocas herramientas». Son **exhortaciones**: dependen de que el modelo se
acuerde en el turno 40, y no se acuerda. Peor: ocupan sitio, así que la cura engorda la enfermedad.

COSMOS es estructural. En cada nivel, lo que no toca todavía **no está cargado** — no hay nada de
más que leer, ni que resumir, ni que ignorar. La frugalidad no se pide: es una propiedad de la
forma. Y lo que es propiedad de la forma no se olvida en el turno 40.

## La taxonomía

**Lo sólido contiene.** Todo está dentro de otra cosa, sin excepción:

```
galaxia > sistema solar > planeta > continente > pais
        > provincia > ciudad > pueblo > casa
```

Con dos adjuntos: la **estrella** que ilumina un sólido (su contexto permanente) y la **luna** que
orbita un planeta (su subagente).

**El agua atraviesa.** No contiene a nadie, moja a varios:

```
oceano (todo) > mar (un sistema) > lago (acotado)
rio (un comando)   lluvia (memoria)
```

El agua nunca define jerarquía. Un lago no es menos importante que un océano: **moja menos
superficie**. Confundir alcance con importancia es como un harness llega a 27.000 tokens de prólogo,
un párrafo global bienintencionado cada vez.

## Cómo se sostiene

Tres piezas, y ninguna depende de que nadie se acuerde de nada:

| Pieza | Qué hace |
|---|---|
| `cosmos validar` | E00–E18. Esquema, estructura, duplicación, colisiones y presupuesto. Rojo, no aviso |
| `cosmos medir` | Cuánto contexto se paga por existir, antes del primer turno. Con el método declarado: si es estimado, dice **estimado** |
| `cosmos generar` | El índice de la galaxia se **genera**. Nunca se edita a mano, así que no puede desincronizarse ni mentir |

Un aviso se ignora; por eso pasarse de presupuesto es rojo. Un índice a mano se desincroniza; por
eso se genera. Un validador que nunca ha dicho rojo no se distingue de uno roto; por eso hay un
test por invariante que lo ve fallar a propósito.

## Estado

En construcción. `GOAL.md` es el contrato, `PROGRESS.md` el estado real, `reviews/` las revisiones
cruzadas.

Lo escriben dos agentes en pareja —Claude las especificaciones, Codex la implementación— y **ninguno
aprueba su propio trabajo**: cada pieza la revisa el otro con premisa invertida, entrando a
demostrar que está mal y contando qué intentó.
