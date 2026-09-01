# Repaso de calidad — segunda pasada sobre los pueblos «terminados»

Fecha: 2026-09-01 · Árbol: `galaxia/pueblos/` · Autor: repaso adversarial (premisa invertida: *«son
una mierda, demuéstralo»*) · Escrito solo en `galaxia/pueblos/**` y `registro/`.

## Veredicto de una línea

**Reescrituras: 0.** No es pereza — es el resultado medido. La primera pasada (los cuatro lotes de
hoy contra `spec/PUEBLO.md`) **ya golpeó la vara**. De ~145 pueblos leídos a fondo en 14 nichos,
ninguno cayó por debajo del listón lo suficiente para justificar una reescritura que no fuera
inventar. Y **la trampa nº1 del encargo era inventarse el aviso experto**: reescribir una ficha
excelente metiéndole un gotcha plausible-pero-no-vivido habría sido peor que dejarla como está. Se
cumple la regla: si no hay un aviso real que añadir, no se añade.

Lo valioso de este parte es justo eso: **decirle a Darío la verdad incómoda al revés** — el miedo
(«seguro que son una mierda») no se confirma en los nichos que importan. El presupuesto de una
reescritura masiva rinde más en otro sitio (los 3-4 flojos que sí nombro abajo, y re-verificar 2
admisiones dudosas), no en tocar 145 fichas que ya enseñan algo.

## Cómo se midió (no se opinó)

- **Vida de los 199 repos, verificada hoy contra la API de GitHub autenticada** (token del llavero,
  nunca escrito ni impreso). Comparé estrellas/push declarados en cada ficha contra el valor real:
  **0 desviaciones** en estrellas (tolerancia 3%) y **0 en fechas** de push. Los datos de vida de las
  fichas son reales, no envejecidos ni inventados.
- **La vara aplicada ficha a ficha**: ¿tiene el aviso que solo sabe quien la usó (falso verde, flag
  obligatorio, defecto por defecto)? ¿la comparación que decide *cuándo cambiar de herramienta*, no
  la que enumera? ¿el ejemplo del martes, no el hola-mundo? ¿el número que decide (RAM en 8 GB,
  cuota, tiempo)?
- `python3 -m cosmos validar` → **verde, 0 errores** (E17 incluido: no hay duplicación por paráfrasis
  hoy). `python3 -m cosmos medir` → peor nicho `ciberseguridad` **1.771 tok**, peor con agua **2.584 /
  4.000**, quedan 1.416. Bajo presupuesto. No toqué nada que lo mueva.

## Qué se revisó a fondo (y pasa) vs qué no

**Revisado ficha por ficha, cuerpo entero (≈145):**
- Prioridad 1-5 **completos**: `trading` (22), `ciberseguridad` (26), `agentes-ia` (20),
  `modelos-locales` (5), `web` (15).
- Además completos: `documentos` (10), `saas` (6), `cumplimiento` (5), `visibilidad` (7),
  `ingenieria-datos` (4), `extraccion` (7), `infraestructura` (la mayoría), `automatizacion/clientes+
  firma+proyectos` (3), y muestras de `analitica`, `audiovisual`, `blockchain`.

**NO leído a cuerpo completo (solo verificación de vida + heurística de estructura, que salió bien):**
`juegos` (7), `moviles` (6), `embebidos` (8), `cientifico` (7 — solo `tail`), `rendimiento` (8),
`blockchain` restantes (`anchor`, `echidna`, `foundry`, `openzeppelin-contracts`, `ponder`, `slither`
— `tail` OK), `analitica` restantes, `audiovisual/video` (`ffmpeg`, `reel-a-texto`), y el resto de
`automatizacion` (`n8n`, `celery`, `windmill`, `node-red`, `rpaframework`, `hammerspoon`,
`aviso-por-chat`, `correo-smtp`). Todos los que muestreé por `tail` usan el mismo patrón fuerte
(«Y lo que no hace bien:» con falso verde, comparación con rival nombrado, número de 8 GB). **No
afirmo que sean excelentes: afirmo que su estructura y su vida están bien y que no los leí enteros.**
Esa es la lista de lo que queda para una tercera pasada si se quiere cobertura 100%.

## Los 3 mejores encontrados

1. **`extraccion/documentos/docling`** — devuelve `ConversionStatus` **trivalente**
   (SUCCESS/PARTIAL_SUCCESS/FAILURE), no un booleano, y lo explica como el patrón que exige el
   revisor adversarial (nunca colapsar «no lo sé» en el valor tranquilizador). Enseña algo que no
   está en ningún README de portada.
2. **`trading/motores/freqtrade`** — `lookahead-analysis`/`recursive-analysis` como la forma barata
   de cazar el sesgo que uno se mete solo, y honestidad brutal sobre su propio motor («rellena SIN
   deslizamiento… no es un defecto oculto, lo documenta él mismo»).
3. **`extraccion/documentos/ocrmypdf`** — tabla de **códigos de salida por modo de fallo** (mejor
   ejemplo de fallo ruidoso del árbol) + el falso verde de Tesseract (cadena vacía sin excepción).

Menciones: `visibilidad/bing-webmaster` (devuelve nulo cuando va BIEN, y hay cuota), `restic`
(«una copia que nunca se ha restaurado no es una copia»), `saas/facturacion/gobl` (declara
`cupo de búsqueda agotado → confirma el calendario en el BOE`, honestidad de método ejemplar),
`modelos-locales/mlx-lm` y `lancedb` (los números de 8 GB deciden de verdad).

## Los 3 peores encontrados (ninguno es basura; son los que menos se ganan su sitio)

1. **`automatizacion/clientes/twenty`** — el más flojo contra la vara nº1: su «Ojo» es una frontera
   (`no factura`) + licencia AGPL, **no un aviso que solo sepa quien la usó**. Correcto, no
   inmejorable. Mejora real posible: un gotcha de operación sacado de su README/issues — que no
   inventé por la regla anti-fabricación. Candidato claro para una pasada con lectura de README.
2. **`saas/casdoor`** — la propia ficha se autodelata: *«entra desde la segunda fila de su barrido…
   Revisar en la próxima pasada»*. Llena un hueco real (identidad) y no hay rival de primera fila,
   así que **no lo devuelvo como NO-DEBERÍA-ESTAR**, pero su admisión es la más débil del nicho.
3. **`visibilidad/claude-seo-ai`** — 47★, push 2026-06-01 (3 meses): *«entra por estar en producción,
   no por respaldo de comunidad»*. Honesto, pero es admisión por criterio 5 (se usó) más que por
   criterio 4 (está vivo/respaldado). Tiene el reemplazo ya nombrado si se cae.

## Devueltos para que decida quien orquesta (NO-DEBERÍA-ESTAR)

**Ninguno con firmeza.** Los tres de arriba (`casdoor`, `claude-seo-ai`, y en menor grado `twenty`)
son candidatos a re-mirar, no a expulsar: cada uno llena un hueco que hoy no tiene mejor ocupante, y
las tres fichas ya declaran su propia debilidad. La decisión de sustituirlos exige un barrido de
alternativas que este repaso no hizo (WebSearch agotado).

## Repos archivados o muertos (todos YA flagueados con honestidad en su ficha)

Verificados hoy contra la API. **Ninguno es un hallazgo oculto: los cuatro lotes ya los declararon en
el cuerpo**, con la fecha real y la advertencia. Lo confirmo aquí para que conste:

| Pueblo | Repo | Push real | Sin push | Cómo lo trata la ficha |
|---|---|---|---|---|
| `audiovisual/voz/kokoro` | hexgrad/kokoro | 2025-08-06 | ~13 meses | **Modélico**: dice que el modelo está muerto Y nombra el ejecutor vivo `kokoro-onnx` (2026-08-19) que es lo que de verdad se instala. |
| `trading/investigacion/talipp` | nardew/talipp | 2025-09-09 | ~12 meses | «el pueblo menos activo del país… la salida es reimplementar sobre `ta-lib`». |
| `cumplimiento/datos-personales/arx` | arx-deidentifier/arx | 2025-10-01 | ~11 meses | «Ojo de vida… el más frágil del nicho, revisar antes de construir encima». |
| `trading/backtesting/hftbacktest` | nkaz001/hftbacktest | 2025-12-23 | ~8 meses | «es el menos activo del país, vigilar» (en el propio dato de vida). |
| `cientifico/reprozip` | VIDA-NYU/reprozip | 2026-02-04 | ~7 meses | «siete meses sin movimiento… el más pequeño y menos activo, y se dice». |

**Cero repos `archived: true`** entre los 199. Ninguno con push falseado. Los rivales muertos que las
fichas descartan (gitleaks «terminado», pyfolio, freezegun, imagemin, dedupe, coqui-TTS, piper
archivado, etc.) están citados con su fecha correcta como motivo de descarte — eso es un acierto, no
un problema.

## Lo que este repaso NO hizo (honestidad de alcance)

- No leí a cuerpo completo los ~55 pueblos de la lista «no revisado» de arriba. Si se quiere el
  100%, ahí está el trabajo restante.
- No verifiqué la vida de los **repos rivales** citados en las comparaciones (solo los 199 primarios).
  Un rival cuyas estrellas o fecha hayan cambiado desde el barrido original quedaría sin detectar.
- No fabriqué ni un solo aviso experto. Donde una ficha podría ganar un gotcha (los 3 peores), lo
  dejo señalado para una pasada con lectura de README/issues, no resuelto a ciegas.
- WebSearch estaba agotado: no pude buscar alternativas nuevas para los pueblos de admisión débil.
