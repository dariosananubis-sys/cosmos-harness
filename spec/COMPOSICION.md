# Composición — contener no es excluir

Encargo de Darío (2026-09-01): *«el de código tiene que ser el mejor de código del universo y además
que no haga código mierda, que es una cosa que suele pasar, y además deben poder usarse ambas skills
a la vez»*.

Es la pregunta correcta y hay que responderla en la spec, no dejarla al sentido común: **una
jerarquía de contención se puede leer como una jerarquía de exclusión**, y si alguien la lee así,
COSMOS deja de servir. Aquí queda cerrado.

## La regla

> **La contención dice dónde vive algo y cuándo se carga. No dice con quién se puede combinar.**

Cargar el sistema solar `codigo` **no** impide cargar `web`, ni `guardia`, ni los tres a la vez.
Un pueblo de una provincia y un pueblo de otra galaxia se invocan juntos sin ningún conflicto.

Lo que la contención decide es una sola cosa: **qué no se paga mientras no se usa**. Nada más.

## Por qué esto no es obvio, y por qué había que escribirlo

Un árbol de directorios sugiere exclusividad: un fichero está en una carpeta *o* en otra. Y el agua
refuerza la impresión, porque un lago sí tiene un terreno delimitado.

Pero el agua delimita **dónde aplica una regla**, no dónde puede trabajar el agente. Son dos ejes
distintos:

| Eje | Qué decide | Se cruza |
|---|---|---|
| **Contención** (sólido) | Dónde vive · cuándo se carga | Sí, libremente |
| **Alcance** (agua) | Dónde aplica una regla | Sí, se solapan |

Un trabajo real casi siempre cruza sistemas: montar una tienda es `web` + `codigo` + `datos` +
`guardia`. Si la taxonomía obligara a elegir uno, sería inútil el primer día.

## El caso que lo motivó: capacidad y criterio

El encargo pide dos cosas del oficio de código, y son **dos cosas distintas** que se estorban si se
meten en el mismo saco:

| | `codigo` | `criterio` |
|---|---|---|
| Qué es | **Capacidad**: saber hacerlo | **Juicio**: saber qué no hacer |
| Contiene | Lenguajes, algoritmos, refactorización a escala, perfilado, depuración | Simplicidad, reutilización, límites del cambio, deuda, revisión adversarial |
| Sin el otro | Escribe mucho código, y mucho sobra | Sabe criticar, no sabe construir |

Que «suele salir código mierda» **no** se arregla siendo mejor programador: se arregla con un
criterio que diga que no. Un modelo con más capacidad y sin criterio produce **más** código de más,
no menos — porque escribir le resulta barato.

Por eso son dos sistemas solares y no uno con una sección dentro:

1. Se **cargan juntos** en todo trabajo de código serio. No compiten.
2. `criterio` sirve igual a `web`, a `datos` y a `mercados`. Metido dentro de `codigo` no llegaría a
   ellos, o habría que copiarlo — y una copia es la forma en que empieza la divergencia.
3. Tiran en direcciones opuestas **a propósito**: uno propone, el otro poda. Fundirlos deja que el
   que propone se autoevalúe, que es exactamente el fallo que el reparto Claude ↔ Codex evita en
   este mismo repo.

## `usa:` — composición declarada

Un nodo puede declarar con qué se usa habitualmente:

```yaml
---
cosmos: pueblo
nombre: refactor-masivo
padre: artesania/codigo/transformacion
resumen: Aplica una transformación a cientos de ficheros con AST, no con expresiones regulares.
usa:
  - artesania/criterio/limites-del-cambio
  - guardia/pruebas/mutacion
---
```

`usa:` es **una sugerencia, no una dependencia**. Es información para quien decide qué cargar, y
sirve para tres cosas concretas:

- Al invocar un pueblo, se ofrece lo que suele acompañarlo.
- El validador avisa si apunta a algo que no existe (**E20**).
- Hace visible el acoplamiento real: si dos nodos se declaran mutuamente y siempre van juntos, a lo
  mejor son uno.

Lo que **no** hace: cargar nada solo. Una dependencia automática convertiría `usa:` en una cadena de
arrastre —cargas uno y vienen cinco— que es el mecanismo exacto por el que un gestor de paquetes
acaba trayendo medio internet. Aquí la carga siempre la decide quien trabaja.

## Los límites de esto

Combinar sin límite tampoco es gratis: cargar seis sistemas solares a la vez cuesta seis estrellas.
La regla práctica es **cargar lo que el trabajo cruza de verdad**, que suelen ser dos o tres, y el
océano `descender` ya lo dice: no se abre lo de al lado por si acaso.

`cosmos medir --combinacion a,b,c` da el coste de una combinación concreta, para que la decisión sea
un número y no una intuición.
