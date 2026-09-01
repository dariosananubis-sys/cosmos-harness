# Esquema de frontmatter — normativo

Todo nodo de COSMOS es un fichero Markdown con frontmatter YAML. No hay base de datos, no hay
manifiesto central escrito a mano: **el árbol se deduce leyendo los frontmatter**, y el índice se
genera. Un manifiesto central a mano se desincroniza el segundo día; un índice generado, no puede.

## Por qué frontmatter y no un fichero de configuración

Porque el nodo y su declaración viajan juntos. Si mueves un pueblo de provincia, su `padre` va
dentro del propio fichero: no hay un segundo sitio que actualizar y, por tanto, no hay un segundo
sitio que olvidar. Toda la clase de errores «lo moví pero no actualicé el índice» deja de existir
por construcción — que es exactamente lo que pide el principio rector del `GOAL.md`.

## Campos comunes

| Campo | Obligatorio | Tipo | Regla |
|---|---|---|---|
| `cosmos` | sí | enum | El nivel. Uno de los 16 de la taxonomía |
| `nombre` | sí | slug | `[a-z0-9-]+`, único dentro de su padre |
| `resumen` | sí | string | **Máximo 120 caracteres.** Es lo único que se ve desde arriba |

`resumen` es el campo más importante del sistema y el más fácil de estropear. Es lo que aparece en
el índice de un nivel superior, así que **es coste fijo permanente**: cada carácter de más se paga
en todas las sesiones para siempre. El límite de 120 no es estético, es presupuestario, y el
validador lo trata como error, no como aviso.

## Nodos sólidos (contienen)

```yaml
---
cosmos: pueblo
nombre: agent-browser
padre: provincia/navegacion-web
resumen: Automatiza un navegador real por CDP; captura, rellena y verifica.
---
```

| Campo | Obligatorio | Regla |
|---|---|---|
| `padre` | sí, salvo galaxia | `<nivel>/<nombre>` de un nodo existente de rango estrictamente menor |

**Rango de los sólidos** (de mayor a menor superficie):

```
1 galaxia
2 sistema-solar
3 planeta
4 continente
5 pais
6 provincia
7 ciudad
8 pueblo
9 casa
```

Regla de contención: `rango(padre) < rango(hijo)`. **Estrictamente menor, no exactamente uno
menos.** Un pueblo puede colgar directamente de una provincia, de un país o de un continente sin
inventar niveles intermedios vacíos.

Esto es deliberado y hay que respetarlo: obligar a la cadena completa produce niveles de relleno
—una provincia con un solo hijo, una ciudad que no es más que un envoltorio— y esos niveles de
relleno son fuga pura, porque cada uno aporta un `resumen` que se paga y no informa de nada. Se
crea un nivel cuando **agrupa de verdad**; si no agrupa, no existe.

Hay exactamente **una** galaxia por instalación, y es el único nodo sin `padre`.

## Adjuntos (no contienen, se adhieren a un sólido)

```yaml
---
cosmos: estrella
nombre: web
ilumina: sistema-solar/web
resumen: Contexto permanente de todo trabajo de web.
---
```

| Nivel | Campo propio | Apunta a |
|---|---|---|
| `estrella` | `ilumina` | Un sólido. Es su `CLAUDE.md`: se carga con él |
| `luna` | `orbita` | Un `planeta`. Es un subagente propio de ese proyecto |

Una estrella por sólido como máximo. Dos estrellas iluminando el mismo sistema es un error: son dos
contextos que se cargan juntos y compiten, y nadie sabrá cuál manda.

## Nodos de agua (atraviesan)

```yaml
---
cosmos: lago
nombre: convenciones-de-commit
moja:
  - ".git/**"
  - "**/CHANGELOG.md"
resumen: Formato de mensajes de commit y reglas de rama.
---
```

| Campo | Obligatorio | Regla |
|---|---|---|
| `moja` | sí | Lista de patrones glob, no vacía. Determina cuándo se carga |

| Nivel | `moja` permitido |
|---|---|
| `oceano` | Exactamente `["**"]`. Es global y hay que declararlo así, a la vista |
| `mar` | Globs amplios, pero **no** `**` |
| `lago` | Globs acotados, **no** `**`, y no la raíz de un sistema entero |
| `rio` | Se invoca a mano: `moja: []` permitido; lleva `invoca` con su nombre de comando |
| `lluvia` | Se consulta a mano: `moja: []` permitido |

El validador **cuenta los océanos**. Un océano es contexto permanente para todo el mundo y para
siempre, así que su número es la métrica de salud más honesta del sistema: si crece, el harness se
está degradando por el mismo camino por el que se degradan todos. El umbral por defecto es 7, y
subirlo es una decisión consciente que se escribe en `cosmos.toml`, no un ajuste silencioso.

Un mar o un lago con `moja: ["**"]` es un océano **encubierto**, y es el modo de fallo más común y
más caro: alguien quiere que su regla «se vea siempre» y la disfraza de local. El validador lo
rechaza por igualdad literal del patrón, no por intención declarada.

## Lo que ningún nodo puede llevar

- Credenciales, tokens, claves, rutas de vault.
- Nombres de cliente, dominios de cliente, correos, IP, datos personales.
- Un `resumen` que sea el nombre otra vez («agent-browser: la skill de agent-browser»). No informa
  y se paga siempre.
- Un `resumen` que describa a sus hijos. Describir a los hijos **es** cargarlos, y ese es
  precisamente el hábito que COSMOS existe para eliminar.
