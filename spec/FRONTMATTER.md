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
| `cosmos` | sí | enum | El nivel. Uno de los 14 de la taxonomía |
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
padre: web/construccion-de-sitios
resumen: Automatiza un navegador real por CDP; captura, rellena y verifica.
---
```

| Campo | Obligatorio | Regla |
|---|---|---|
| `padre` | sí, salvo galaxia | La **ruta completa** de un nodo existente de rango estrictamente menor (`NUCLEO.md` §1). El nivel NO aparece en la ruta: `web/pagos`, nunca `pais/pagos` |

**Rango de los sólidos** (de mayor a menor superficie):

```
1 galaxia
2 sistema-solar
3 planeta
4 continente
5 pais
6 provincia
7 pueblo
```

Regla de contención: `rango(padre) < rango(hijo)`. **Estrictamente menor, no exactamente uno
menos.** Un pueblo puede colgar directamente de una provincia, de un país o de un continente sin
inventar niveles intermedios vacíos.

Esto es deliberado y hay que respetarlo: obligar a la cadena completa produce niveles de relleno
—una provincia con un solo hijo, un país que solo envuelve a otro— y esos niveles de
relleno son fuga pura, porque cada uno aporta un `resumen` que se paga y no informa de nada. Se
crea un nivel cuando **agrupa de verdad**; si no agrupa, no existe.

Los rangos 7 y 9 de la versión anterior (`ciudad` y `casa`) se retiraron el 2026-09-01: cero nodos
en los dos árboles del repositorio y cero tests que los crearan. El motivo y el camino de vuelta,
en `spec/TAXONOMIA.md`.

Hay exactamente **una** galaxia por instalación, y es el único nodo sin `padre`.

## Adjuntos (no contienen, se adhieren a un sólido)

```yaml
---
cosmos: estrella
nombre: web
ilumina: web
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
| `moja` | sí | Lista de patrones glob. No vacía salvo en `rio` y `lluvia` (tabla siguiente). Determina cuándo se carga |

| Nivel | `moja` permitido |
|---|---|
| `oceano` | Exactamente `["**"]`. Es global y hay que declararlo así, a la vista |
| `mar` | Globs amplios, pero **no** `**` |
| `lago` | Globs acotados, **no** `**`, y no la raíz de un sistema entero |
| `rio` | Se invoca a mano: `moja: []` permitido; lleva `invoca` con su nombre de comando |
| `lluvia` | Se consulta a mano: `moja` **tiene que ser** `[]`; con alcance se cobraría sin cargarse |

El validador **cuenta los océanos**. Un océano es contexto permanente para todo el mundo y para
siempre, así que su número es la métrica de salud más honesta del sistema: si crece, el harness se
está degradando por el mismo camino por el que se degradan todos. El umbral por defecto es 7, y
subirlo es una decisión consciente que se escribe en `cosmos.toml`, no un ajuste silencioso.

Un mar o un lago con `moja: ["**"]` es un océano **encubierto**, y es el modo de fallo más común y
más caro: alguien quiere que su regla «se vea siempre» y la disfraza de local. El validador no lo caza
comparando el patrón con `"**"`: eso lo esquivaría cualquiera escribiendo `**/*` o una lista de
globs que entre todos lo cubren igual. Lo que mide es la **cobertura real** — si el conjunto de
patrones casa con todas las sondas del corpus normativo, es un océano se llame como se llame
(`NUCLEO.md` §9). La intención declarada no cuenta; el alcance efectivo, sí.

## Campos opcionales

Ninguno es obligatorio, y todos los valida el código.

| Campo | Dónde | Regla |
|---|---|---|
| `usa` | cualquier sólido | Lista de rutas completas de nodos que existen, y nunca la propia (E20). Declara **con qué se trabaja junto** sin arrastrar carga: se valida el destino y no se carga nada, porque una dependencia automática sería la cadena de arrastre que trae medio internet. Ver `spec/COMPOSICION.md` |
| `origen` | solo `pueblo` | `propio`: la herramienta es un guion que vive en el directorio del pueblo, no un repositorio ajeno, y por eso no lleva URL. `guia`: un playbook propio que se **lee** y no se ejecuta (sin URL ni guion; E21 solo exige que tenga cuerpo). Son las dos excepciones que admite E21 (`PUEBLO.md`); sin este campo, un pueblo sin `http(s)://` en el cuerpo es un rojo |
| `anfitrion` | cualquier nodo | Solo el valor `claude-code`. Declara que el nodo **es el fichero de runtime del anfitrión más las claves de COSMOS**: las demás claves de su frontmatter (`name`, `description`, `paths`, `tools`, `model`, `mcpServers`, `metadata`…) son del runtime, pueden llevar mapas anidados, COSMOS no las juzga y viajan intactas al fichero que `compilar` genera quitando solo las claves de COSMOS (`COMPILACION.md`). Sin esta declaración, una clave desconocida o un mapa anidado siguen siendo E00: la puerta se abre a la vista, nunca por defecto |
| `momento` | solo `rio` | `trabajo` (por defecto) o `mantenimiento` (E00). Un río de mantenimiento cuida el repositorio y no resuelve el encargo de nadie, así que el catálogo lo **nombra sin describirlo**: su resumen dejaría de pagarse en cada sesión para usarse una vez. Ver `spec/NUCLEO.md` §2 |

## Lo que ningún nodo puede llevar

- Credenciales, tokens, claves, rutas de vault.
- Nombres de cliente, dominios de cliente, correos, IP, datos personales.
- Un `resumen` que sea el nombre otra vez («agent-browser: la skill de agent-browser»). No informa
  y se paga siempre.
- Un `resumen` que describa a sus hijos. Describir a los hijos **es** cargarlos, y ese es
  precisamente el hábito que COSMOS existe para eliminar.
