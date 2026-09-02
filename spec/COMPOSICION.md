# Composición — contener no es excluir

Encargo de Darío (2026-09-01): *«el de código tiene que ser el mejor de código del universo y además
que no haga código mierda, que es una cosa que suele pasar, y además deben poder usarse ambas skills
a la vez»*.

Es la pregunta correcta y hay que responderla en la spec, no dejarla al sentido común: **una
jerarquía de contención se puede leer como una jerarquía de exclusión**, y si alguien la lee así,
COSMOS deja de servir. Aquí queda cerrado.

> Reescrita el 2026-09-02: la primera versión razonaba sobre un universo anterior (`codigo`,
> `datos`, `guardia`, `artesania`, `mercados`) que la revisión de UNIVERSO expulsó por ser
> categorías temáticas, y llamaba a `criterio` «sistema solar» cuando GOAL §1 lo fija como **mar**.
> Ninguno de sus ejemplos existía en el árbol; el ejemplo de `usa:` de la propia spec que define
> E20 habría dado E20. Los ejemplos de abajo apuntan a nodos reales y un canario
> (`tests/test_cifras_de_las_specs.py`) comprueba que lo siguen siendo.

## La regla

> **La contención dice dónde vive algo y cuándo se carga. No dice con quién se puede combinar.**

Cargar el sistema solar `web` **no** impide cargar `saas`, ni `rendimiento`, ni los tres a la vez.
Un pueblo de una provincia y un pueblo de otro sistema solar se invocan juntos sin ningún conflicto.

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

Un trabajo real casi siempre cruza sistemas: montar una tienda que cobra es `web` + `saas` +
`visibilidad` + `cumplimiento` — que es literalmente el vecindario que `web` declara en su `usa:`.
Si la taxonomía obligara a elegir uno, sería inútil el primer día.

## El caso que lo motivó: capacidad y criterio

El encargo pide dos cosas del oficio de código, y son **dos cosas distintas** que se estorban si se
meten en el mismo saco:

| | Capacidad | Criterio |
|---|---|---|
| Qué es | Saber hacerlo | Saber qué no hacer |
| Contiene | Lenguajes, algoritmos, refactorización a escala, perfilado, depuración | Simplicidad, reutilizar antes que crear, tocar lo justo, deuda |
| Sin el otro | Escribe mucho código, y mucho sobra | Sabe criticar, no sabe construir |

Que «suele salir código mierda» **no** se arregla siendo mejor programador: se arregla con un
criterio que diga que no. Un modelo con más capacidad y sin criterio produce **más** código de más,
no menos — porque escribir le resulta barato.

La resolución que GOAL §1 fija como no negociable reparte los dos por **niveles distintos**, no por
dos sistemas hermanos:

1. **La capacidad vive dentro de cada nicho.** El código de un exploit no se parece al de un tema de
   WordPress ni al de una estrategia de backtesting: un oficio genérico de «código» sería la
   categoría temática que la prueba de UNIVERSO expulsa. Por eso no existe un sistema `codigo`.
2. **El criterio es un mar** (`mar/criterio`), y por eso moja `**/*.py`, `**/*.js` y el resto de
   ficheros de código **en todos los nichos a la vez**. Un mar entra por `paths:`, sin que nadie lo
   invoque: el que propone no puede olvidarse de cargar al que poda, que es exactamente el fallo que
   tendría cualquier reparto donde cargar el criterio fuera una decisión del que escribe.
3. Tiran en direcciones opuestas **a propósito**: uno propone, el otro poda. Fundirlos deja que el
   que propone se autoevalúe, que es el fallo que el reparto Claude ↔ Codex evita en este mismo repo.

Así «usarse ambas a la vez» no es una opción que alguien concede: es lo que pasa por construcción al
entrar en cualquier nicho y tocar un fichero de código.

## `usa:` — composición declarada

Un nodo puede declarar con qué se usa habitualmente. Los 21 sistemas solares lo hacen —GOAL §1:
*«cada nicho apunta a sus vecinos y no duplica nada»*— y un pueblo también puede:

```yaml
---
cosmos: pueblo
nombre: refactor-masivo
padre: refactorizacion/transformacion
resumen: Aplica una transformación a cientos de ficheros con AST, no con expresiones regulares.
usa:
  - refactorizacion/transformacion/ast-grep
  - refactorizacion/mutacion/mutmut
---
```

(`padre` y los destinos de `usa:` son rutas completas de nodos que existen en el árbol real; el
canario de las specs lo vigila para que este ejemplo no envejezca como envejeció el anterior.)

`usa:` es **una sugerencia, no una dependencia**. Es información para quien decide qué cargar, y
sirve para tres cosas concretas:

- Al invocar un nodo, se ofrece lo que suele acompañarlo.
- El validador comprueba que apunta a algo que existe y no a uno mismo (**E20**): un `usa:` que
  apunta a un nicho renombrado no da error en ningún sitio y deja al lector buscando algo que ya no
  se llama así.
- Hace visible el acoplamiento real: si dos nodos se declaran mutuamente y siempre van juntos, a lo
  mejor son uno.

Lo que **no** hace: cargar nada solo. Una dependencia automática convertiría `usa:` en una cadena de
arrastre —cargas uno y vienen cinco— que es el mecanismo exacto por el que un gestor de paquetes
acaba trayendo medio internet. Aquí la carga siempre la decide quien trabaja.

El grafo se revisó el 2026-09-02 (C01): se añadieron las aristas que son verdad sobre cómo se
cruza el trabajo real —cada una con su historia en el parte `taxonomia-c01-c03`— y quedó un único
oficio al que nadie manda, `juegos`, declarado **terminal**: se llega a él por el encargo, no desde
otro oficio. E20 garantiza que ningún destino miente; que ningún oficio quede sin citar salvo los
terminales declarados lo vigila `tests/test_universo_navegable.py`. La reciprocidad total no se
persigue: una arista es una afirmación sobre el trabajo, no un trámite de simetría.

## Los límites de esto

Combinar sin límite tampoco es gratis: cada sistema solar cargado cuesta su estrella. La regla
práctica es **cargar lo que el trabajo cruza de verdad**, que suelen ser dos o tres, y el océano
`descender` ya lo dice: no se abre lo de al lado por si acaso.

`cosmos medir --combinacion a,b,c` da el coste de una combinación concreta, para que la decisión sea
un número y no una intuición.
