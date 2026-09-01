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

## Arranque

La vista plana es un **artefacto generado** y no se versiona, así que un clon recién bajado la tiene
ausente y E19 lo canta. Un comando lo resuelve:

```
git clone <repo> && cd cosmos
python3 -m cosmos arrancar        # compila la vista y valida; deja el clon en verde
python3 -m cosmos enganchar       # instala el gate de pre-commit (opcional, muy recomendable)
```

`arrancar` construye la vista y vuelve a validar el árbol entero. **No** regenera el índice: si el
índice miente, sale en rojo y te manda a `cosmos generar`. Un bootstrap que repara en silencio lo
que el validador debería denunciar no es un bootstrap, es un encubrimiento.

`cosmos.toml` apunta al árbol real (`galaxia/`). El árbol de juguete tiene su propia configuración
en `ejemplo.toml`: `python3 -m cosmos arrancar --config ejemplo.toml`.

## Cómo se sostiene

Cuatro piezas que comprueban, y tres enganches que las ejecutan sin que nadie se acuerde:

| Pieza | Qué hace |
|---|---|
| `cosmos validar` | E00–E19. Esquema, estructura, duplicación, presupuesto y artefactos sincronizados |
| `cosmos medir` | Cuánto contexto se paga por existir, antes del primer turno. Con el método declarado: si es estimado, dice **estimado** |
| `cosmos generar` | El índice de la galaxia se **genera**. Nunca se edita a mano, así que no puede desincronizarse ni mentir |
| `cosmos compilar` | Aplana ciudades y pueblos en symlinks relativos o copias, con lock y manifiesto atómico |

| Enganche | Cuándo corre | Se instala con |
|---|---|---|
| pre-commit | Antes de cada commit, sobre la **instantánea del índice** (no sobre lo que haya sucio en disco) | `cosmos enganchar` |
| CI | En cada push y cada PR | ya está en `.github/workflows/cosmos.yml` |
| arranque | Al clonar | `cosmos arrancar` |

`cosmos enganchar` es explícito y reversible: dice qué escribió y dónde, **no pisa un pre-commit
ajeno** —si lo hay, lo dice y no toca nada— y `cosmos desenganchar` lo quita dejando el repositorio
exactamente como estaba. Nada se instala solo al importar el paquete.

Un aviso se ignora; por eso pasarse de presupuesto es rojo. Un índice a mano se desincroniza; por
eso se genera. Un validador que nunca ha dicho rojo no se distingue de uno roto; por eso hay un
test por invariante que lo ve fallar a propósito. Y un validador que nadie ejecuta no se distingue
de no tenerlo; por eso hay enganches.

## La válvula de escape

Todo guardarraíl duro sin válvula acaba desactivado a la fuerza: alguien tiene una urgencia real un
viernes, el guard le estorba, y lo arranca entero. Así que COSMOS trae la suya, y usarla es más
cómodo que saltarse el sistema:

```
python3 -m cosmos saltar E16 --motivo "importando 40 skills, se reorganiza el lunes" --caduca 7d
python3 -m cosmos saltar --listar
```

| Propiedad | Regla |
|---|---|
| Acotada | Un código concreto (`E00`..`E19`), nunca «todo» |
| Con motivo | Obligatorio. Sin `--motivo` no hay salto |
| Caducable | Obligatorio, máximo 30 días. Sin `--caduca` no hay salto |
| Registrada | Log que solo crece en `.cosmos/saltos.log`; renovar añade línea, no reescribe |
| Visible | Con un salto vivo la salida dice `verde (1 salto activo: E16, caduca en 5 d)`, nunca «verde» a secas |
| Ruidosa al caducar | Al vencer vuelve el rojo y el mensaje recuerda el motivo que se escribió |

La palabra «verde» no aparece nunca sola habiendo saltos activos. Un verde que oculta un salto es
una mentira, y basta una para que nadie vuelva a creerse ninguna.

El registro es local y no se versiona: una urgencia de una persona no puede apagar el CI de todos.
La deuda que sí es del repositorio se inventaría aparte, en `secretos-conocidos.txt`, y ahí lo que
no está en la lista bloquea igual.

## Estado

En construcción. `GOAL.md` es el contrato, `PROGRESS.md` el estado real, `reviews/` las revisiones
cruzadas.

Lo escriben dos agentes en pareja —Claude las especificaciones, Codex la implementación— y **ninguno
aprueba su propio trabajo**: cada pieza la revisa el otro con premisa invertida, entrando a
demostrar que está mal y contando qué intentó.
