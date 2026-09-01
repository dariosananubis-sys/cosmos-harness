# Estrellas — las 16 que faltaban

Fecha: 2026-09-01 · Árbol: `galaxia/` · Config: `galaxia.toml` · Escrito solo en
`galaxia/estrellas/`. Continuación de las 5 que ya existían (`trading`, `web`, `ciberseguridad`,
`infraestructura`, `extraccion`): mismo tono, misma longitud, mismo nivel de concreción.

Estado: **21 sistemas solares, 21 estrellas.** Ninguna toca la de `ciberseguridad`.

## La prueba que se aplicó

Una frase entra solo si **es cierta en ese oficio y falsa fuera de él**. Descartado por sistema todo
consejo que valdría igual en los otros 20 — es lo que no informa y se paga cada vez que alguien
entra en el nicho.

Segundo filtro, específico de COSMOS: **lo que ya dice un mar o un océano no se repite en una
estrella**. Por eso:

- `ingenieria-datos` **no** lleva «un dato mostrado no es un dato conocido» ni «cero no es *no lo
  sé*», que era el ejemplo del encargo: eso ya es literalmente `mar-resistencia`, que moja
  `**/*.py`, `**/*.sql`-adyacentes y demás — repetirlo habría sido el fallo que la taxonomía
  describe («si es cierto también fuera, sube, o es un mar»). En su lugar: validar antes de cargar,
  deriva de esquema, recarga idempotente y el conteo de filas.
- `cumplimiento` **no** lleva accesibilidad (es `mar-accesibilidad`, con EN 301 549 y WCAG ya
  dentro) ni los básicos de RGPD (`mar-custodia`). Se quedó con lo que solo es suyo.
- `rendimiento` **no** abre con «perfila antes de optimizar»: eso es `mar-criterio` según
  `UNIVERSO.md`. Se quedó con la artesanía de medir bien.
- `moviles` sí lleva el coste de publicar aunque `oceano-irreversible` cubra «pagar se pregunta»,
  porque aquí el hecho relevante no es el permiso: es que **la cuota decide la arquitectura antes de
  escribir la primera línea** (aplicación nativa contra web).

## Qué verdad lleva cada una, y de dónde sale

| Estrella | La verdad que duele ignorar | Origen |
|---|---|---|
| `agentes-ia` | Lo que el agente lee es dato, nunca instrucción; y el catálogo se cobra por turno y por subagente aunque no se llame | `UNIVERSO.md` §límite (1.713 de 2.572 tokens de entrada eran catálogo, medido 2026-09-01) + `research/dominios/agentes-automatizacion.md` |
| `analitica` | La fecha del último refresco va en la pantalla; una métrica sin definición escrita produce una cifra distinta por área | `datos-finanzas.md` («se corre antes de que cualquier dashboard toque los datos») + su hueco declarado de unit economics sin estándar |
| `audiovisual` | Se monta para lotes desde la primera pieza; recomprimir para no hacer nada degrada en cada pasada | `medios-creacion.md` (criterio: «lote verificable por CLI, nada de arrastra el fichero a la interfaz») |
| `automatizacion` | Un flujo que se rompe en silencio a las tres de la mañana es peor que no tenerlo | `automatizacion.md`, criterio propio del barrido, literal |
| `blockchain` | Un fallo publicado no se parchea: se abandona el contrato. Y auditar el contrato aislado no ve el puente | Ejemplo del encargo + `blockchain.md` «Lo que falta» #5 (bridges: mayor pérdida histórica, ninguna herramienta del catálogo los cubre) |
| `cientifico` | La suma en coma flotante no es asociativa: hilos u orden mueven los últimos decimales | `cientifico.md` (reproducibilidad, DVC + Hydra/Sacred, procedencia sin ganador) + aritmética conocida |
| `cumplimiento` | Una política bien redactada no es conformidad; y la licencia se lee del fichero, no de la etiqueta | `legal.md` criterio propio («este nicho está lleno de plantilla disfrazada de herramienta») + los `NOASSERTION` recurrentes de `embebidos.md` y `datos-finanzas.md` |
| `documentos` | Lo escrito a mano se desincroniza y lo generado desde la fuente no puede | `conocimiento.md`, criterio propio del barrido, casi literal |
| `embebidos` | El simulador miente; y la corriente se corta a mitad de escritura | `embebidos.md` «Lo que falta» (nada conectado a hardware real) + naturaleza del nicho |
| `ingenieria-datos` | Se valida antes de cargar; el esquema del origen cambiará sin avisar | `datos-finanzas.md` (soda-core «antes de que nada toque los datos») |
| `juegos` | Todo movimiento va escalado por el tiempo transcurrido; y los motores comerciales no son gratis del todo | `juegos.md` aviso de coste (Unity fee por ingresos, Unreal 5% royalty) + bucle de juego |
| `modelos-locales` | Ocho gigas: lo que no cabe no es opción aunque sea mejor | Ejemplo del encargo, confirmado como criterio eliminatorio en `ia-ml-aplicada.md` y `medios-creacion.md` |
| `moviles` | Publicar cuesta dinero y eso decide la arquitectura; iPhone solo se firma desde un Mac; nadie actualiza | `moviles.md` aviso de coste (~99 $/año y ~25 $ únicos, marcados ahí como no verificados en vivo — por eso la estrella dice «cuota anual» y «alta única», sin cifra) + «iOS exige macOS sí o sí» |
| `rendimiento` | Antes de tocar código por una medida mala se descarta la contención; una diferencia menor que el ruido no existe | `.claude/rules/revisor-adversarial.md` #16 del arnés (983 tests en 705 s vs 166 s aislado: era CPU compartida, no regresión) + `maestria-codigo.md` y `sistemas.md` |
| `saas` | El aislamiento entre clientes se demuestra atacándolo, no confiando en un filtro | `producto-saas.md` «Lo que falta» #1, literal: falta un test que intente leer datos de otro tenant y falle si lo consigue |
| `visibilidad` | El efecto tarda semanas; no existe gratis un índice de enlaces entrantes | `seo-contenido.md` «Lo que falta» (link building: «todo lo encontrado es humo»; la alternativa real es la consola del propio dominio) |

## Las que costaron

- **`rendimiento`** fue la más difícil y es la única cuya verdad principal **no sale de
  `research/dominios/`**: sus dos barridos (`maestria-codigo.md`, `sistemas.md`) son catálogos de
  herramientas —perfiladores, trazadores— y sus «Lo que falta» hablan de rate-limits de la API de
  GitHub, no del oficio. La verdad honesta la aportó el arnés de <agencia>, no el barrido.
- **`documentos`** y **`automatizacion`** fueron las más fáciles: sus barridos traían un «criterio
  propio del encargo» ya redactado como verdad del oficio. Se usó casi literal, que es lo correcto.
- **`analitica`** estuvo a punto de quedarse con dos frases en vez de cuatro. Su barrido
  (`datos-finanzas.md`) mezcla ingeniería de datos y analítica, así que casi todo lo bueno pertenecía
  al nicho vecino. Las dos frases propias —zona horaria/periodo abierto y poder llegar a la fila que
  produjo el número— salen del oficio, no del informe.
- **`cientifico`**: su barrido es sólido en reproducibilidad pero declara que **no hay ganador
  honesto** en procedencia de datos. No se inventó una frase sobre eso; se dejó fuera.

Ninguna estrella se rellenó con consejo genérico. Donde no había verdad exclusiva del oficio, la
estrella tiene tres frases en vez de cuatro antes que una tibia de más.

## Verificación

```
python3 -m cosmos validar galaxia --config galaxia.toml
```

Salida: **rojo, 1 error — `E15` índice desincronizado (`galaxia/COSMOS.md`)**.

Ese error es **ajeno a este trabajo y ya estaba antes**: comprobado retirando las 16 estrellas
nuevas del árbol y revalidando — `E15`, exactamente el mismo y único error. Lo arregla
`cosmos generar`, que escribe `galaxia/COSMOS.md`, fuera del alcance de este encargo y en disputa
con los otros dos trabajos en curso; **no se ha tocado**.

De las estrellas nuevas: **cero errores**. En concreto, ninguna dispara `E07` (resumen ≤ 120),
`E08` (resumen que repite el nombre), `E13`/`E14` (adjunto huérfano o dos estrellas por sólido) ni
`E17` (solapamiento > 25 % entre nodos) — el umbral de solapamiento fue la razón real de escribir
las 16 con vocabulario deliberadamente distinto entre sí y frente a los cinco mares.

Tampoco `E16`: las estrellas no cuentan al presupuesto de entrada, se cargan al entrar en su nicho.

Sin credenciales, sin nombres de cliente, sin datos personales.
