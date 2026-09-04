# Compilación a la vista plana — decisión de arquitectura y spec

Escribe la implementación **Codex**. Revisa **Claude**.

## El problema que descubrió la investigación

`research/ESTADO-DEL-ARTE.md` §6, y es el hallazgo más importante de todos:

> **Claude Code solo escanea el nivel superior de `~/.claude/skills/`.** Una skill en
> `skills/suite/hija/SKILL.md` **no se descubre**: invocarla da «Unknown skill».
> Issue `anthropics/claude-code#18192`, abierto en enero de 2026, sin resolver.

O sea: el runtime al que apuntamos **no soporta de forma nativa** que un pueblo cuelgue de una
provincia, de un país o de un continente. La contención que COSMOS define para las skills no existe
en la plataforma: para ella, o están en el nivel superior o no están.

El apaño de la comunidad son symlinks a mano en el nivel superior. Funciona, y es exactamente lo que
COSMOS prohíbe: depende de que alguien se acuerde de crear el symlink al añadir una skill. Una
taxonomía sostenida por memoria humana es una taxonomía que ya está rota, solo que todavía no se
nota.

## Las dos salidas, y por qué se elige la primera

| | Opción A — compilar a plano | Opción B — router MCP propio |
|---|---|---|
| Cómo | Un paso de build genera la vista plana que la plataforma sí descubre | Un servidor MCP indexa el árbol y expone `cosmos_buscar` / `cosmos_cargar` |
| Depende de | Que la plataforma resuelva symlinks o acepte copias | Nada de la plataforma |
| Coste en runtime | **Un `resumen` por pueblo aplanado**, si el runtime escanea el destino: un directorio de skills se descubre inyectando nombre y descripción de cada entrada en el prompt. Por eso se aplana **por nicho** (17 resúmenes), no la galaxia entera (247), y `cosmos medir` publica «Vista compilada» (auditoría A-02) | Un servidor vivo **y sus tools en el contexto de cada sesión**, todas, siempre |
| Riesgo | Comportamiento de symlinks no estandarizado entre runtimes | Infraestructura permanente que mantener |

**Se elige A.** La razón no es la simplicidad, es el principio rector.

La opción B parece más robusta —no depende de que Anthropic arregle nada— pero un servidor MCP
**inyecta sus definiciones de herramientas en el contexto de todas las sesiones, siempre**. Es
decir: para resolver un problema de carga perezosa, añadiría carga permanente. Sería construir la
fuga dentro de la herramienta que existe para eliminarla, y encima con la conciencia tranquila de
haber elegido «lo robusto».

La opción A traslada todo el coste a un paso de build que ocurre una vez, fuera de cualquier
sesión. Coste en contexto: cero. Ese es el criterio que decide.

El riesgo de A —symlinks inconsistentes entre runtimes, ya visto en `openai/codex#22275`— se cubre
con `--modo copia`, que copia en vez de enlazar. Más disco, cero magia. Es opción, no defecto: el
symlink es mejor cuando funciona, porque no duplica.

## Qué es la verdad y qué es un artefacto

Regla de oro, y de ella sale todo lo demás:

> **El árbol cosmográfico es la verdad. La vista plana es un artefacto generado, como el índice.**

Nadie edita nunca la vista plana. Si alguien la edita, el validador lo detecta y el arreglo es
recompilar, jamás conservar el cambio manual. Igual que `COSMOS.md` (E15), y por la misma razón: lo
que se genera no puede mentir, y por eso se puede confiar en ello sin comprobarlo.

## La restricción nueva que impone aplanar

Y esta es la parte que no se ve venir hasta que se implementa.

`FRONTMATTER.md` exige que `nombre` sea único **entre hermanos** (E06). Es lo correcto para un
árbol: dos provincias distintas pueden tener cada una un pueblo `revisar` sin ningún conflicto,
porque sus rutas completas difieren.

**Al aplanar, esas dos rutas colapsan en el mismo nombre.** La vista plana no tiene jerarquía donde
desambiguar: `revisar` y `revisar` compiten por la misma entrada, y una gana en silencio. El árbol
está perfectamente sano y la compilación produce un sistema donde una skill es inalcanzable, sin
que nada falle.

Es un fallo especialmente feo porque el síntoma aparece lejísimos de la causa: alguien invoca
`revisar`, le responde la de otra provincia, y no hay ningún error en ninguna parte.

Por tanto, dos invariantes nuevas:

| Código | Invariante | Mensaje |
|---|---|---|
| `E18` | Los nombres de todo lo que se aplana son únicos **globalmente**, no solo entre hermanos | colisión al aplanar |
| `E19` | La vista plana en disco coincide con la que se generaría ahora | vista plana desincronizada |

`E18` se comprueba **sobre el árbol**, sin necesidad de compilar: es una propiedad del árbol
respecto de su futura compilación. Se detecta antes de que exista el daño, que es donde hay que
detectar las cosas.

El mensaje de `E18` nombra **las dos rutas en conflicto**, no solo el nombre repetido. Saber que
«revisar está duplicado» no ayuda a nadie; saber qué dos rutas chocan se arregla en diez segundos.

## Comportamiento

```
cosmos compilar [--nicho <n>] [--modo symlink|copia] [--destino <ruta>] [--seco]
```

| Flag | Qué hace |
|---|---|
| `--nicho` | Aplana solo los pueblos contenidos por ese sistema solar |
| `--modo` | `symlink` (por defecto) o `copia` |
| `--destino` | Dónde se escribe la vista plana. Por defecto, lo que diga `cosmos.toml` |
| `--seco` | Dice qué haría y no toca nada |

Reglas de la compilación:

1. **Falla antes de tocar nada si el árbol no valida.** Compilar un árbol roto propaga el destrozo
   a un sitio donde cuesta más verlo.
2. **Nunca borra lo que no ha creado.** Lleva su propio manifiesto, `.cosmos/compilado.json`, con lo
   que puso. Lo que no está en él, se deja y se avisa. Un compilador que limpia el directorio de
   destino borra el día menos pensado algo que alguien puso a mano y que importaba.
3. **Es idempotente.** Compilar dos veces seguidas deja el mismo estado y la segunda no reporta
   cambios.
4. **Dice exactamente qué hizo**: cuántas entradas creó, actualizó, dejó igual y cuántas ajenas
   respetó.

La selección forma parte del artefacto: el manifiesto guarda el nicho activo y E19 compara contra
esa misma selección. Al pasar de `web` a `saas`, las entradas que el manifiesto atribuía a `web`
son obsoletas: se borran solo si conservan el hash registrado; si alguien las modificó se preservan,
se avisa y salen del manifiesto. Una entrada nunca registrada sigue siendo ajena y no se toca.

Sin `--nicho` se conserva la compilación completa anterior por compatibilidad. Esa forma sirve para
migración e inspección; la vista que consume un runtime con carga acotada se genera con `--nicho`.

## Verificación exigida

1. Un test de que un árbol con dos pueblos homónimos en provincias distintas da `E18`, **y que el
   mensaje nombra las dos rutas**.
2. Un test de que compilar sobre un árbol inválido no escribe ni un byte en el destino.
3. Un test de idempotencia: compilar, compilar otra vez, y comprobar que la segunda no cambia nada.
4. Un test de que un fichero ajeno en el destino **sobrevive** a la compilación y se reporta.
5. Un test de que editar la vista plana a mano produce `E19`.
6. Un test de `--seco`: no escribe nada, y lo que dice que haría coincide con lo que hace luego sin
   el flag.
7. Un test en `--modo copia` de que no queda ningún symlink en el destino.
8. Un test de que `--nicho web` solo aplana `web`, elimina por hash las entradas intactas de otros
   nichos y preserva las modificadas.

## Los otros ficheros de runtime: reglas, agentes y comandos

Un anfitrión como Claude Code lee cuatro cosas: skills (la vista plana de arriba), **reglas** que se
cargan por rutas (`.claude/rules/*.md` con `paths:`), **agentes** (`.claude/agents/*.md`) y
**comandos** (`.claude/commands/*.md`). Cuando COSMOS organiza un arnés que ya existía, esos tres
también son nodos —un mar o un lago es una regla, una luna es un agente, un río con `invoca: /x` es un
comando— y también se generan. La regla es una sola y es la que hace reversible la migración:

> **El nodo es el fichero original del anfitrión más las claves de COSMOS, y compilar es quitarlas.**

Un nodo con `anfitrion: claude-code` (`FRONTMATTER.md`) conserva el frontmatter del anfitrión tal
cual —orden, comillas, mapas anidados incluidos— y añade delante `cosmos:`, `nombre:`, `resumen:` y
lo que su nivel exija (`moja`, `orbita`, `invoca`…). `cosmos compilar` escribe en cada destino
declarado en `cosmos.toml` (`[compilacion] rules`, `agentes`, `comandos`) el nodo **sin** esas claves
(`modelo.sin_claves_cosmos`, textual: no se re-serializa nada); si el frontmatter queda vacío, se
quita entero. El resultado tiene que ser, byte a byte, el fichero que el anfitrión tenía antes, y la
prueba es `git diff` sobre el destino tras compilar: vacío. La vista de skills hace lo mismo para los
pueblos con `anfitrion` (copia sin traducir nada: el original ya lleva `name`/`description`), y esos
pueblos entran **siempre** en la vista, sea cual sea el nicho activo, porque son las skills que el
anfitrión ya usaba.

Cada destino lleva su manifiesto (`.cosmos/compilado-<tipo>.json`) y la misma política que la vista
plana: lo que COSMOS escribió se actualiza o se retira cuando su nodo desaparece; lo que **no**
escribió (ajeno) no se toca nunca, salvo para adoptarlo si es idéntico a lo que se crearía; lo que
alguien editó después de escribirlo se preserva y se dice. **E22** comprueba que cada nodo con
`anfitrion` tiene su fichero generado, igual a él y en el manifiesto, y que el manifiesto no nombra
ficheros que ya no tienen nodo; el arreglo es `cosmos compilar`, nunca editar el fichero generado.

Lo que no se genera: la memoria del anfitrión (`REGISTRO.md`, se indexa donde está), `CLAUDE.md`
y los ajustes del runtime (`.claude/settings.json`, hooks): eso sigue siendo del arnés y de
`cosmos enganchar`.

### Se paga lo que se compila

Con `[compilacion] vista = "anfitrion"` el árbol tiene dos poblaciones: los nodos del anfitrión, que
`compilar` lleva al runtime, y el catálogo genérico de COSMOS, que se **busca** (`buscar`, `acertar`)
pero no se carga. El validador y el medidor lo saben: E12 cuenta solo los océanos del anfitrión, E17
compara solo entre nodos del anfitrión, y `medir` suma solo su agua. Sin esto, organizar un arnés real
el 2026-09-04 dio 12 océanos (5 de COSMOS que nadie leía), 63 solapamientos (40 contra agua que no
entraba) y una entrada inflada con reglas que el runtime no conocía. Lo que **sí** se mide igual es el
índice y el catálogo: son la aproximación de COSMOS a lo que el anfitrión inyecta por su cuenta.
