# Extracción de datos — barrido GitHub

Barrido vía API de GitHub autenticada (búsqueda + `repos/OWNER/REPO` en vivo, 2026-09-01). Cupo de
`WebSearch` de la sesión agotado — cero contenido de este informe viene de memoria ni de búsqueda
web; todo enlace y cifra sale de una llamada a `api.github.com` con respuesta guardada. Lo que no se
verificó en vivo se marca **NO VERIFICADO**.

## De primera

Máximo 10. Ganan por combinar: **legal y respetuoso por diseño** (no existe para saltar
protecciones anti-bot ni resolver captchas — eso manda directo a Humo), **coste cero** y
autoalojable, **fallo ruidoso** (dice cuándo se ha roto en vez de devolver cero filas en silencio), y
ser el estándar de facto vivo de su sub-tarea, no un experimento de tres semanas.

### 1. Scrapy 🔧 — el framework de scraping
- **URL**: https://github.com/scrapy/scrapy · **Estrellas**: 64.150 · **Licencia**: BSD-3-Clause ·
  **Última actividad**: 2026-08-28.
- **Qué hace**: framework Python completo — spiders, middlewares, pipelines, exportadores CSV/JSON,
  control de concurrencia y `AutoThrottle`.
- **Mecanismo de fallo ruidoso**: `spider_error` y las señales `item_dropped`/`request_dropped` se
  disparan explícitamente; los códigos HTTP no-200 pasan por `handle_httpstatus_list` en vez de
  perderse. **Caveat real**: si el HTML cambia y un selector CSS/XPath deja de matchear, Scrapy no
  lo sabe — no valida contra un esquema. Mitiga con `ITEM_PIPELINES` que rechacen items con campos
  vacíos obligatorios.
- **Respetuoso por defecto**: `ROBOTSTXT_OBEY = True` es plantilla estándar del `scrapy startproject`
  y `AutoThrottle` ajusta la tasa según la latencia del servidor.
- **Ecosistema**: `scrapy-playwright` (1.441★) para páginas con JS, `parsel` (1.353★, motor de
  selectores) y `scrapyd` (3.101★, demonio de despliegue) — todo bajo el mismo paraguas BSD.

### 2. Crawl4AI 🔧 — crawler pensado para alimentar LLMs
- **URL**: https://github.com/unclecode/crawl4ai · **Estrellas**: 80.632 · **Licencia**: Apache-2.0 ·
  **Última actividad**: 2026-09-01 (commits diarios).
- **Qué hace**: crawler sobre Playwright que entrega Markdown limpio, extracción estructurada por
  esquema CSS/XPath o por LLM, y gestión de sesión/caché — alternativa self-hosted directa a
  Firecrawl.
- **Mecanismo de fallo ruidoso**: cada `CrawlResult` trae `success: bool` y `error_message`
  explícitos por URL — no hay que adivinar si una página falló, el objeto lo dice.
- **Coste cero real**: el modo por esquema/CSS no toca ningún LLM; el modo de extracción por LLM es
  opcional y usa el proveedor que se le indique (o uno local vía Ollama).

### 3. Playwright 🔧 — el motor de automatización de navegador
- **URL**: https://github.com/microsoft/playwright (núcleo) y
  https://github.com/microsoft/playwright-python (bindings Python, 14.967★) · **Estrellas núcleo**:
  95.462 · **Licencia**: Apache-2.0 · **Última actividad**: 2026-08-31.
- **Qué hace**: automatización headless de Chromium/Firefox/WebKit con una sola API — base de facto
  de todo lo demás en esta lista que necesita renderizar JS.
- **Mecanismo de fallo ruidoso** — el más limpio del barrido: cada acción (`click`, `fill`,
  `wait_for_selector`) lanza `TimeoutError` explícito si el elemento no aparece. No hay modo
  silencioso: o la acción ocurrió, o Playwright lo dice.
- **Nota**: es el motor; no incluye evasión de detección de bots por diseño — eso es justo lo que
  los forks "stealth" añaden encima (ver Humo).

### 4. Docling 🔧 — parseo de documentos a Markdown/JSON estructurado
- **URL**: https://github.com/docling-project/docling · **Estrellas**: 65.838 · **Licencia**: MIT ·
  **Última actividad**: 2026-09-01.
- **Qué hace**: convierte PDF, DOCX, PPTX, XLSX, HTML e imágenes a Markdown o JSON con estructura
  (títulos, tablas, layout), pensado explícitamente para pipelines de IA generativa. Proyecto de
  IBM Research donado a la Linux Foundation AI & Data.
- **Mecanismo de fallo ruidoso**: el resultado de conversión trae un `ConversionStatus` de tres
  valores (`SUCCESS` / `PARTIAL_SUCCESS` / `FAILURE`), no un booleano — distingue "salió perfecto"
  de "salió algo, con avisos" de "no salió nada". Es exactamente el patrón trivalente que exige
  `revisor-adversarial.md` (nunca colapsar "no lo sé" en el valor tranquilizador).

### 5. Marker (datalab-to/marker) 🔧 — PDF a Markdown de alta fidelidad
- **URL**: https://github.com/datalab-to/marker (renombrado desde `VikParuchuri/marker`, redirect
  de GitHub verificado en vivo) · **Estrellas**: 39.448 · **Licencia**: Apache-2.0 · **Última
  actividad**: 2026-08-31.
- **Qué hace**: convierte PDF a Markdown/JSON conservando tablas, fórmulas matemáticas y orden de
  lectura; usa modelos de layout propios (no un LLM externo de pago).
- **Complementa a Docling**: Docling gana en variedad de formatos de entrada; Marker gana en
  fidelidad sobre PDF académico/técnico con fórmulas.

### 6. Tesseract 🔧 — el motor OCR canónico
- **URL**: https://github.com/tesseract-ocr/tesseract · **Estrellas**: 76.287 · **Licencia**:
  Apache-2.0 · **Última actividad**: 2026-08-25.
- **Qué hace**: reconocimiento óptico de caracteres, +100 idiomas, motor sobre el que se apoyan la
  mayoría de wrappers Python de OCR del ecosistema (incluido OCRmyPDF, nº 7 de esta lista).
- **Mecanismo de fallo ruidoso**: devuelve confianza por palabra (`conf`) vía `image_to_data` — un
  pipeline serio debe leer ese número y no solo el texto, porque una imagen ilegible puede devolver
  cadena vacía sin lanzar excepción. Es el punto ciego a vigilar, no un secreto: está documentado.

### 7. OCRmyPDF 🔧 — capa de OCR sobre PDF escaneado, con validación estricta
- **URL**: https://github.com/ocrmypdf/OCRmyPDF · **Estrellas**: 34.641 · **Licencia**: MPL-2.0 ·
  **Última actividad**: 2026-08-31.
- **Qué hace**: añade una capa de texto buscable a un PDF escaneado sin destruir el original, sobre
  Tesseract.
- **Mecanismo de fallo ruidoso — el más ejemplar del barrido**: tiene una tabla de **códigos de
  salida distintos** para cada modo de fallo (ya tiene texto y no se fuerza, PDF cifrado, prioridades
  en conflicto, Ghostscript ausente…) en vez de un genérico "error". Es justo el antipatrón que
  `revisor-adversarial.md` señala como típico (`"un fallo genérico... suele ser un contrato de campos,
  no los datos"`) resuelto de fábrica.

### 8. Unstructured (Unstructured-IO) 🔧 — ETL de documentos para RAG/LLM
- **URL**: https://github.com/Unstructured-IO/unstructured · **Estrellas**: 15.375 · **Licencia**:
  Apache-2.0 · **Última actividad**: 2026-08-28.
- **Qué hace**: parte PDF, Word, PPTX, HTML, correo (.eml/.msg) e imágenes en "elementos" tipados
  (título, párrafo, tabla, pie de página…) listos para indexar — cubre a la vez documento + email de
  la lista de partida.
- **Caveat a verificar antes de confiar a ciegas**: hay reportes de la comunidad de partición
  silenciosa de elementos mal formados en ciertos parsers internos — no tomar "devolvió N elementos"
  como sinónimo de "los extrajo todos" sin una muestra de control (NO VERIFICADO en este barrido,
  queda para cuando se pruebe con documentos reales del cliente).

### 9. Trafilatura 🔧 — extracción de texto y metadatos web, grado académico
- **URL**: https://github.com/adbar/trafilatura · **Estrellas**: 6.746 · **Licencia**: Apache-2.0 ·
  **Última actividad**: 2026-08-28.
- **Qué hace**: extrae el contenido principal (sin menú/publicidad/boilerplate) y metadatos
  (autor, fecha, título) de una página, con salida CSV/JSON/XML/Markdown/TXT.
- **Mecanismo de fallo ruidoso**: función principal devuelve `None` explícito cuando no logra
  aislar contenido con confianza suficiente, en vez de devolver un fragmento parcial disfrazado de
  completo. Además publica benchmarks de precisión/recall contra otros extractores (dragnet,
  readability, newspaper3k) — es transparente sobre sus propios límites, algo raro en esta categoría.

### 10. RQ (Redis Queue) 🔧 — colas y reintentos, sin infraestructura pesada
- **URL**: https://github.com/rq/rq · **Estrellas**: 10.678 · **Licencia**: sin SPDX asignado
  (repo público, revisar el fichero `LICENSE` antes de redistribuir) · **Última actividad**:
  2026-09-01.
- **Qué hace**: colas de trabajo simples sobre Redis — encaja como pieza de reintentos/backoff para
  un pipeline de scraping sin montar Celery entero.
- **Mecanismo de fallo ruidoso**: los jobs fallidos van a un `FailedJobRegistry` explícito, con
  traceback guardado — no desaparecen ni se reintentan en silencio infinito; el reintento es una
  política que se declara, no un comportamiento oculto.
- **Alternativa de mayor escala**: **Celery** (`celery/celery`, 28.848★, en el mismo repo sin SPDX
  claro) si el pipeline crece a multi-cola con enrutado complejo.

## Segunda fila

- **apify/crawlee-python** (9.483★, Apache-2.0) — framework de crawling con pool de sesiones,
  reintentos y abstracción de almacenamiento incorporados; la versión Node (`apify/crawlee`,
  25.586★) es la más madura si el proyecto acaba en TypeScript.
- **microsoft/markitdown** (177.474★, MIT) — conversor ligero de Office/HTML/PDF a Markdown pensado
  para pipelines LLM; más simple que Docling, menos estructura de tablas.
- **browser-use/browser-use** (111.912★, MIT) — capa de automatización orientada a agentes IA sobre
  Playwright; útil si la extracción necesita "navegar y decidir", no solo listar selectores fijos.
- **gocolly/colly** (25.493★, Apache-2.0) — framework de crawling en Go, concurrencia nativa, para
  cuando el volumen pide algo que no sea Python.
- **jsvine/pdfplumber** (10.707★, MIT) — acceso fino a caracteres/rectángulos/líneas de un PDF;
  mejor que Docling/Marker cuando hace falta control quirúrgico de coordenadas.
- **py-pdf/pypdf** (10.184★, sin SPDX) — manipulación PDF pura Python (split/merge/crop) sin
  dependencias binarias — la pieza de bajo nivel, no un extractor de alto nivel.
- **camelot-dev/camelot** (3.814★, MIT) — extracción de tablas de PDF por método lattice/stream;
  clásico, pero sin commits desde 2023-01 — **verificar viveza antes de apostar por él** frente a
  `img2table` o `gmft`, más recientes.
- **xavctn/img2table** (893★, MIT) y **conjuncts/gmft** (540★, MIT) — extracción de tablas de PDF e
  imágenes vía OpenCV/deep learning, ambos con actividad en 2026.
- **ispras/dedoc** (732★, Apache-2.0) — parseo universal con estructura lógica y tablas, alternativa
  europea a Unstructured con menos tracción pero misma idea.
- **PaddlePaddle/PaddleOCR** (88.582★, Apache-2.0) y **datalab-to/surya** (21.341★, Apache-2.0,
  redirect verificado desde `VikParuchuri/surya`) — OCR + layout + orden de lectura + tablas en
  90-100+ idiomas; alternativas más pesadas a Tesseract cuando el documento tiene layout complejo.
- **studio-dots-ai/dots.ocr** (9.097★, MIT) — parseo de layout multilingüe con un único modelo
  visión-lenguaje; interesante pero más joven, exige GPU para rendir.
- **apache/tika** (4.024★, Apache-2.0) — detección y extracción de metadatos/texto de +1000 formatos
  de fichero; veterano Java, útil como red de seguridad para formatos raros que nada más reconoce.
- **yobix-ai/extractous** (1.772★, Apache-2.0) — extracción de datos no estructurados en Rust con
  bindings multilenguaje; rápido, pero última actividad 2024-12 (**revisar viveza**).
- **jina-ai/reader** (11.937★, Apache-2.0) — convierte cualquier URL a texto limpio para LLM vía
  prefijo `r.jina.ai`; el servicio público es gratuito con límites, y el código es autoalojable.
- **dedupeio/dedupe** (4.510★, MIT), **moj-analytical-services/splink** (2.372★, MIT) y
  **rapidfuzz/RapidFuzz** (4.106★, MIT) — deduplicación difusa y resolución de entidades en Python;
  `dedupe` para casos pequeños con aprendizaje activo, `splink` para escala con backend SQL
  (proyecto del Ministerio de Justicia del Reino Unido, buen pedigrí de mantenimiento), `RapidFuzz`
  como pieza base de comparación de cadenas para cualquiera de los dos.
- **dlt-hub/dlt** (5.804★, Apache-2.0) — carga y normalización de datos extraídos hacia destinos de
  almacenamiento (Parquet, DuckDB, Postgres…), cierra el extremo final del pipeline.
- **kurtmckee/feedparser** (2.417★, sin SPDX) — parseo de RSS/Atom, la pieza que falta para
  "descubrimiento de APIs públicas" cuando la fuente es un feed.
- **SpamScope/mail-parser** (455★, Apache-2.0) — parseo de correos `.eml` con extracción completa de
  cabeceras/adjuntos/cuerpo.
- **dgtlmoon/changedetection.io** (33.433★, Apache-2.0) — monitorización de cambios en páginas web
  con alertas; útil como capa de vigilancia sobre fuentes ya scrapeadas, no como extractor en sí.
- **firecrawl/firecrawl** (175.007★, AGPL-3.0) — mencionado aparte porque el repo del motor es
  autoalojable y gratis, pero el producto empuja activamente a la API de nube de pago; si se usa,
  self-host explícito para no acabar facturando por uso. AGPL-3.0 obliga a publicar el código si se
  ofrece como servicio a terceros — revisar antes de envolverlo en un producto propio.

## Humo

Descartado por el filtro legal/ético (punto 1) salvo que se indique otro motivo:

- **FlareSolverr/FlareSolverr** — proxy hecho para resolver a la fuerza el reto de Cloudflare: es
  literalmente "saltar protecciones anti-bot".
- **ultrafunkamsterdam/undetected-chromedriver** — se anuncia como "pasa TODOS los sistemas de
  mitigación de bots (Distil/Imperva/Datadome/Cloudflare)"; diseño explícito de evasión.
- **VeNoMouS/cloudscraper** — "bypass de la página anti-bot de Cloudflare" en su propia descripción.
- **2captcha/2captcha-python** — resolutor de captchas de pago (reCAPTCHA/Turnstile/FunCaptcha):
  cae a la vez en el filtro legal y en el de coste cero.
- **Xewdy444/Playwright-reCAPTCHA** — resuelve reCAPTCHA v2/v3 con Playwright.
- **CloakHQ/CloakBrowser** — Chromium "stealth" que dice pasar "30/30 tests de detección de bots",
  con parches de fingerprinting a nivel de código fuente.
- **Kaliiiiiiiiii-Vinyzu/patchright-python** y **feder-cr/invisible_playwright** — forks
  "undetected" de Playwright con el mismo objetivo de evasión de huella digital.
- **skernelx/tavily-key-generator** — automatiza el alta de cuentas y generación de claves de
  Tavily/Firecrawl: viola directamente los términos de servicio de esos proveedores.
- **feder-cr/Jobs_Applier_AI_Agent_AIHawk** — rellena y envía solicitudes de empleo en nombre del
  usuario en portales de terceros de forma automática: riesgo de suplantación y de ToS de esos
  portales, aunque el objetivo declarado (buscar empleo) sea legítimo.
- **zohaibbashir/Google-Maps-Scrapper** — scraping masivo de fichas de negocio de Google Maps
  (nombre, contacto…): viola los Términos de Servicio de Google y roza datos personales sin base
  legal clara bajo RGPD.
- **RamsesAguirre777/facebook-ads-library-mcp** — raspa la Facebook Ad Library saltándose la capa de
  acceso oficial pese a no pedir token; sigue siendo extracción no autorizada de una plataforma con
  ToS explícitos contra el scraping.
- **Evil0ctal/Douyin_TikTok_Download_API** — descarga contenido de TikTok/Douyin/Kuaishou saltándose
  sus APIs oficiales de descarga.
- **JCodesMore/ai-website-cloner-template** — clona sitios web enteros con un comando sin
  verificación de permisos: riesgo directo de infracción de derechos de autor sobre el diseño y
  contenido clonado.
- **psf/requests-html** — no es un problema legal, es de viveza: sin commits desde 2024-04, depende
  de `pyppeteer` (ya obsoleto frente a Playwright). Riesgo de **fallo silencioso** por dependencias
  rotas — justo lo que el filtro 3 penaliza. Descartado de "de primera"/"segunda fila" por esto, no
  por ética.
- **camelot-dev/camelot** — no descartado (sigue en segunda fila), pero se nombra aquí también como
  aviso: sin commits desde 2023-01, mismo riesgo de abandono que requests-html a vigilar antes de
  construir algo crítico encima.

## Mapeo a COSMOS

Este dominio entero encaja como **país** (TAXONOMIA.md: "familia de capacidades que comparten
tecnología o modelo mental" — aquí, sacar datos de una fuente externa y dejarlos en un formato
usable). Las **provincias** agrupan las skills hermanas por sub-tarea; los **pueblos** son las
herramientas atómicas concretas de este rastreo. Ninguna tiene hoy partes que se carguen aparte, así
que ninguna sube a ciudad todavía — la señal de ascenso sería que una integrase, por ejemplo, una
guía propia de "OCR de facturas" cargable por separado del resto.

| País | Provincia | Pueblos (de este rastreo) |
|---|---|---|
| **Extracción de datos** | Scraping y crawling a escala | Scrapy, Crawl4AI, Crawlee (Python/Node), colly, changedetection.io |
| | Automatización de navegador headless | Playwright (núcleo + Python), browser-use |
| | Parseo de documentos (PDF/Word/Excel/HTML) | Docling, Marker, Unstructured, pdfplumber, pypdf, dedoc, Apache Tika, extractous, MarkItDown |
| | Extracción de tablas | Camelot (verificar viveza), img2table, gmft |
| | OCR de escaneados | Tesseract, OCRmyPDF, PaddleOCR, Surya, dots.ocr |
| | Extracción de texto y metadatos web | Trafilatura, Jina Reader |
| | Parseo de correo y feeds | mail-parser, feedparser |
| | Normalización y deduplicación | dedupe, splink, RapidFuzz |
| | Colas, reintentos y carga a almacenamiento | RQ, Celery, dlt |

Nota de alcance: "descubrimiento de APIs públicas" (parte del encargo del dominio) no tiene un
pueblo dedicado en este barrido — ver "Lo que falta".

## Lo que falta

- **Descubrimiento de APIs públicas**: no se encontró ni se buscó todavía una herramienta específica
  (tipo catálogo/registro de APIs abiertas o detector automático de endpoints JSON tras una web).
  Pendiente de una pasada de búsqueda dedicada cuando el cupo de `WebSearch` se recupere — la API de
  búsqueda de GitHub no es el instrumento adecuado para esto (no es "una librería", es "un
  directorio").
- **`table-extraction-pdf` como query directa devolvió 0 resultados** en el barrido (posible fallo
  de sintaxis de la consulta, no de falta de proyectos — hay varios sólidos vía otras consultas:
  Camelot, img2table, gmft, ExtractPDF4J). No repetido por presión de rate-limit de búsqueda
  (30/hora); si hace falta ampliar esta sub-provincia, repetir con sintaxis distinta.
- **Licencias sin SPDX** (pypdf, RQ, Celery, feedparser) — GitHub no les asigna un identificador
  SPDX automático aunque tengan fichero `LICENSE`; antes de redistribuir código que los envuelva,
  leer el fichero real en cada repo en vez de fiarse del campo `license.spdx_id` de la API.
- **Unstructured-IO**: el caveat de partición silenciosa de elementos mal formados es de la
  comunidad (foros/issues), no verificado con una prueba propia en este barrido — pendiente de un
  test con un documento real antes de confiar en él para datos de cliente.
- **Coste real de Firecrawl/Jina Reader autoalojados**: no se midió consumo de CPU/RAM de correr
  Firecrawl (AGPL-3.0, stack con Playwright + colas + Redis) en local — antes de recomendarlo sobre
  Crawl4AI habría que comparar footprint de recursos, no solo licencia.
- **Extractous y Camelot**: viveza a re-verificar en unos meses (última actividad 2024-12 y 2023-01
  respectivamente) — si siguen parados, bajarlos de segunda fila a humo por abandono.
- Ninguna búsqueda de este barrido usó `WebSearch` (agotado) ni navegador — todo por
  `api.github.com` autenticado. Si aparece una herramienta relevante que no está indexada como repo
  de GitHub (p. ej. un servicio SaaS sin código abierto), este barrido no la habría visto.
