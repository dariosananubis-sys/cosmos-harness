# Dominio: adquisición de tráfico — SEO técnico, local, schema, GEO/AEO, contenido, keyword research, link building, competencia, medición

> Investigación para COSMOS. Barrido de GitHub para encontrar skills/agentes/plugins/repos que
> conviertan a un agente de código en especialista real de este dominio, para trabajo de pago.
> Método: WebSearch + WebFetch sobre GitHub y blogs, contrastado con la API pública de GitHub
> (`api.github.com/repos/<owner>/<repo>`) cuando el rate limit lo permitió. **Convención de cifras**:
> `[API]` = estrellas/fecha de push verificadas contra la API real; `[WF]` = leídas por WebFetch sobre
> la página del repo (razonablemente fiables — 6 repos se verificaron por ambas vías y coincidieron a
> ±10 estrellas — pero no son la fuente autoritativa). Fecha de la investigación: 2026-09-01.
>
> Leyenda: 🔧 mecanismo real y ejecutable (crawler, validador, script) · 📝 solo prosa/instrucciones
> (lo que ya sabe cualquier modelo) · 💰 tiene una vía de pago (marcada exactamente dónde) · ⚠️ dato
> o riesgo a vigilar.

---

## De primera

Máximo 10, ordenados por peso real (adopción + mecanismo + vigencia), no por orden de aparición.

### 1. `AgriciDaniel/claude-seo` 🔧
- **URL**: https://github.com/AgriciDaniel/claude-seo
- **Estrellas**: 15.992 `[API]` · **Forks**: 2.341 · **Último push**: 2026-08-26 `[API]` (6 días antes de esta investigación) · **Licencia**: MIT
- **Qué es**: skill universal para Claude Code con **25 sub-skills + 18 sub-agentes** cubriendo SEO
  técnico, E-E-A-T, schema, GEO/AEO, backlinks, SEO local + maps intelligence, clustering semántico,
  e-commerce, internacional, APIs de Google y reporting PDF/Excel.
- **Mecanismo**: Python 3.10+ con Playwright Chromium opcional para SPAs. `install.sh`/`install.ps1`
  ejecutables. Sub-skills en `skills/seo-*/` y agentes en `agents/seo-*.md`, autodescubiertos; hasta
  15 agentes en paralelo; orquestador central detecta la industria y sintetiza resultados.
  Validadores reales integrados (schema, Core Web Vitals, E-E-A-T, estructura técnica).
- **Coste**: funciona entero con **cero API keys**. Extensiones opcionales de pago: DataForSEO,
  Firecrawl, Ahrefs, SE Ranking, Bing Webmaster, Unlighthouse — todas marcadas como opcionales, no
  requeridas para el core.
- **Por qué gana**: con diferencia el repo con más adopción real de todo el barrido (16k stars, ~2.300
  forks), sigue empujando commits esta misma semana, y es el único que cubre **las nueve subáreas del
  dominio asignado** en un solo paquete con mecanismo verificable, no prosa.
- **Nota de calidad**: 16k stars en un nicho tan específico invita a comprobar en vivo antes de fiarse
  a ciegas (⚠️ no se instaló ni ejecutó en esta investigación, solo se leyó el repo) — pero la
  estructura de ficheros, los scripts y el número de forks son consistentes con adopción real, no con
  un README inflado.

### 2. `Hainrixz/claude-seo-ai` 🔧 — YA INSTALADO en este workspace
- **URL**: https://github.com/Hainrixz/claude-seo-ai
- **Estrellas**: 47 `[API]` · **Forks**: 5 · **Último push**: 2026-06-01 `[API]` · **Licencia**: MIT
- **Qué es**: toolkit SEO + AI-search (GEO/AEO) — audita en dos ejes independientes (búsqueda
  clásica y visibilidad IA) con puntuación 0-100 y banda A-F. Es el plugin `claude-seo-ai` que este
  mismo workspace tiene cargado ahora mismo (los nombres de skills `audit/geo/score/fix`, los ~20
  módulos `seo-*` y los 5 subagentes — 4 auditores + `seo-fixer-writer` — coinciden exactamente).
- **Mecanismo**: scripts Node.js **cero-dependencias** (Node ≥18) en `/scripts/`: `parse-html.mjs`,
  `validate-jsonld.mjs`, `parse-robots-sitemap.mjs`, `score.mjs`, más una suite de 30 aserciones en
  `/tests/run.mjs`. Hook `PreToolUse` que bloquea escritura sin verificación previa; rechaza árbol
  Git sucio.
- **Coste**: Tier 0 (por defecto) funciona 100% offline sin API alguna. Tier 1 opcional:
  `PSI_API_KEY` (PageSpeed Insights, gratis) + MCP de renderizado. Tier 2 opcional: OAuth para
  Search Console / Merchant Center (gratis, solo requiere credenciales propias).
- **Por qué está aquí**: es el que ya está en producción en este mismo arnés — la comparación
  honesta es que `AgriciDaniel/claude-seo` (#1) tiene 340× más estrellas y más del doble de
  sub-skills. **Recomendación concreta**: evaluar mantener ambos (roles distintos: éste es más
  ligero y 100% offline; el #1 es el especialista de fondo) o migrar el core a #1 y quedarse con
  éste solo para el modo sin-red.

### 3. `TheCraigHewitt/seomachine` 🔧
- **URL**: https://github.com/TheCraigHewitt/seomachine
- **Estrellas**: ~7.400 `[WF]` · **Licencia**: MIT
- **Qué es**: workspace de Claude Code dedicado a **contenido largo SEO** — investigar, escribir,
  analizar y optimizar contenido pensado para rankear. Es el recurso más fuerte encontrado
  específico de "estrategia de contenido" (subárea explícitamente pedida).
- **Mecanismo**: slash commands (`/research`, `/write`, `/rewrite`, `/optimize`), agentes
  especializados (SEO Optimizer, Meta Creator, Internal Linker) y **scripts Python** de integración
  con Google Analytics, Search Console y DataForSEO.
- **Coste**: base gratis; la integración con DataForSEO (si se activa) es de pago.
- **Por qué gana**: sin él, "estrategia de contenido" solo estaría cubierta como sub-skill dentro de
  paquetes generalistas (#1); éste es mecanismo dedicado y con adopción real.

### 4. `Auriti-Labs/geo-optimizer-skill` 🔧
- **URL**: https://github.com/Auriti-Labs/geo-optimizer-skill
- **Estrellas**: 748 `[WF]` · **Último push**: 2026-09-01 `[WF]` (el mismo día de esta investigación)
  · **Licencia**: MIT
- **Qué es**: toolkit GEO/AEO dedicado — audita si ChatGPT, Perplexity, Gemini, Claude y Google AI
  Overviews pueden descubrir y citar un sitio. Puntúa 0-100 sobre **47 métodos en 8 categorías**
  (robots.txt, llms.txt, JSON-LD, meta tags, estructura, coherencia de marca, señales, endpoints de
  descubrimiento de IA) y comprueba crawlability contra **27 bots de IA**.
- **Mecanismo**: CLI, API Python (`audit()`/`audit_async()`), **servidor MCP** (usable desde Claude,
  Cursor, Windsurf) e integración Astro para generar `llms.txt` en build-time.
- **Coste**: auditoría local gratis sin API keys. `geo citations` (verificar menciones reales en
  motores) 💰 requiere API key propia (Perplexity, OpenAI, Anthropic, Groq, DeepSeek, Gemini —
  cualquiera vale, no exclusivo de un proveedor de pago). Plataforma hospedada opcional (GeoReady)
  desde $19/mes — evitable, el CLI local ya da la puntuación.
- **Por qué gana**: es el especialista GEO/AEO más completo y **más vivo** de todo el barrido
  (commit el mismo día), y cubre exactamente la subárea "GEO/AEO" del encargo con mecanismo real
  (no solo un README con consejos).

### 5. `GoogleChrome/lighthouse` 🔧
- **URL**: https://github.com/GoogleChrome/lighthouse
- **Estrellas**: 30.700 `[WF]` · **Licencia**: Apache-2.0
- **Qué es**: el motor canónico de auditoría de Core Web Vitals / performance / a11y / SEO on-page,
  mantenido por Google Chrome. Integrado en DevTools, PageSpeed Insights y CLI/CI.
- **Mecanismo**: CLI Node, corre localmente, genera reportes HTML/JSON, sin enviar datos a
  terceros. Base de facto de decenas de herramientas "Lighthouse-as-a-Service".
- **Coste**: cero, siempre.
- **Por qué gana**: es la referencia oficial y gratuita de medición de Core Web Vitals — cualquier
  especialista técnico necesita esto o algo construido encima (ver #6).

### 6. `harlan-zw/unlighthouse` 🔧
- **URL**: https://github.com/harlan-zw/unlighthouse
- **Estrellas**: 4.800 `[WF]` · **Licencia**: MIT
- **Qué es**: audita Lighthouse en **el sitio entero**, no página a página — un solo comando
  (`npx unlighthouse --site <url>`), muestreo inteligente para sitios grandes, dashboard moderno.
- **Mecanismo**: CLI que orquesta Lighthouse (#5) a escala; paquete dedicado `unlighthouse-ci` para
  pipelines.
- **Coste**: cero, self-hosted, sin API.
- **Por qué gana**: Lighthouse solo (#5) audita una URL; esto lo convierte en auditoría de sitio
  completo, que es lo que de verdad se necesita para un cliente con decenas de páginas.

### 7. `eliasdabbas/advertools` 🔧
- **URL**: https://github.com/eliasdabbas/advertools
- **Estrellas**: 1.449 `[API]` · **Forks**: 249 · **Último push**: 2026-06-30 `[API]` · **Licencia**: MIT
- **Qué es**: librería Python madura (siete años de desarrollo) de productividad para marketing
  online. SEO: crawler propio sobre Scrapy (extrae títulos, headings, códigos de estado),
  descarga/parseo de sitemaps XML, importación de resultados de búsqueda. SEM: generación de
  keywords, creación de anuncios. Análisis de texto: frecuencia de palabras, URLs, emojis, hashtags.
- **Mecanismo**: todo son funciones Python independientes que devuelven DataFrames — se compone
  como se quiera, sin estructuras de datos propietarias.
- **Coste**: cero para el core (crawler, sitemaps, texto). Módulos opcionales de Twitter/YouTube/
  Google Search API requieren credenciales propias (no necesariamente de pago, según cuota).
- **Por qué gana**: es la librería Python de SEO más establecida y con mecanismo real (crawler
  Scrapy de verdad, no un wrapper), y sigue con actividad reciente.

### 8. `PhialsBasement/LibreCrawl` 🔧
- **URL**: https://github.com/PhialsBasement/LibreCrawl
- **Estrellas**: 895 `[API]` · **Forks**: 193 · **Último push**: 2026-08-18 `[API]` · **Licencia**: MIT
- **Qué es**: alternativa gratuita a Screaming Frog — crawler web-based multi-tenant para auditoría
  SEO técnica.
- **Mecanismo**: Flask + interfaz web moderna, self-hosted (script de instalación detecta
  Docker o Python), soporte multiusuario concurrente, exportación CSV/JSON/XML, integración con
  PageSpeed Insights, sistema de plugins, renderizado JS vía Playwright/Chromium.
- **Coste**: cero, sin cuenta ni API key. ⚠️ Existen varios forks con nombres casi idénticos
  (`ScreamingLizard`, `swang62/seo-crawler`, `jamie-dit/librecrawl`) con la misma descripción
  copiada palabra por palabra — este (`PhialsBasement`) es el que tiene más estrellas y actividad
  más reciente, tratable como el original de facto.
- **Por qué gana**: sustituto real y gratuito de una herramienta de pago (Screaming Frog cuesta
  licencia), con mecanismo de crawling de verdad, no una maqueta.

### 9. `towfiqi/serpbear` 🔧
- **URL**: https://github.com/towfiqi/serpbear
- **Estrellas**: 2.100 `[WF]` · **Licencia**: MIT
- **Qué es**: rank tracker self-hosted — seguimiento ilimitado de keywords en Google, alertas de
  cambio de posición, API SERP propia, integración con Search Console y Google Ads.
- **Mecanismo**: Next.js + SQLite, self-hosted (Docker/npx/Fly.io gratis).
- **Coste**: la app es gratis. 💰 Para obtener datos SERP reales necesita un scraper de terceros
  (ScrapingAnt, ScrapingRobot, SearchApi, SerpApi, HasData — todos de pago) **o** proxies propios
  del usuario — sin eso no trackea rankings de verdad. Marcar claramente antes de usar: esta pieza
  concreta cuesta dinero salvo que se aporten proxies propios.
- **Por qué gana**: sustituye rank trackers de pago ($99/mes+) y es el único de este barrido
  dedicado a keyword tracking con mecanismo self-hosted real.

### 10. `Suganthan-Mohanadasan/Suganthans-GSC-MCP` 🔧
- **URL**: https://github.com/Suganthan-Mohanadasan/Suganthans-GSC-MCP
- **Estrellas**: 120 `[WF]` · **Licencia**: Apache-2.0
- **Qué es**: servidor MCP para Google Search Console con **29 herramientas** (no 20 como decía el
  README indexado por el buscador) repartidas en análisis (quick wins, cannibalización, decadencia
  de contenido, clusters temáticos...), SEO de imágenes, indexación y verificación de hechos.
- **Mecanismo**: corre localmente, OAuth o service account propios, sin servidor intermediario —
  los datos van directo entre la máquina del usuario y Google. Setup de un comando
  (`npx suganthan-gsc-mcp setup`).
- **Coste**: cero — usa la cuota gratuita de la API de Search Console con credenciales propias.
- **Por qué gana**: cubre la subárea de "medición" con la integración más profunda de Search
  Console encontrada (29 tools vs. las ~9-13 de alternativas), local-first y sin intermediario que
  vea los datos del cliente.

---

## Segunda fila

Mecanismo real o parcialmente real, pero con menos adopción, más nicho, o con un pero que vigilar.

- **`stjudewashere/seonaut`** 🔧 — 777★ `[WF]`, MIT, Go+MySQL, self-hosted, crawler y auditoría
  técnica reales (broken links, redirects, meta duplicados, heading mal ordenados). Hay versión
  hospedada gratis en seonaut.org si no se quiere self-host. Solapa con LibreCrawl/advertools —
  útil como segunda opción si el stack ya es Go, no imprescindible junto a los de primera.
- **`elmohq/elmo`** 🔧💰 — 284★ `[API]`, push 2026-09-01 `[API]`, MIT, self-hosted vía Docker
  Compose. Trackea cómo ChatGPT/Claude/Perplexity/Gemini/Copilot/Grok/AI Overviews mencionan una
  marca. Cada métrica es auditable en código (Postgres propio). **Pero**: el tracking real necesita
  keys de pago por uso (OpenAI/Anthropic/Mistral/OpenRouter) o el plan hospedado desde $29/mes —
  choca directo con la regla de "nunca pagar sin orden". Vale para diseño/arquitectura de un
  tracker de citas propio; no desplegar sin autorización explícita de gasto.
- **`surendranb/google-analytics-mcp`** 🔧 — 239★ `[API]`, push 2026-08-18 `[API]`, MIT. MCP de
  GA4 con descubrimiento de esquema y agregación server-side. Alternativa a la #10 pero para GA4 en
  vez de Search Console; conviene juntar los dos MCP (GSC + GA4) para medición completa.
- **`google/schemarama`** 🔧⚠️ — 150★ `[API]`, **ARCHIVADO 2024-08-19** `[API]` (más de dos años sin
  tocar). Validación de datos estructurados vía ShEx/SHACL, oficial de Google, pero el propio repo
  advierte "no recomendado para producción" y ahora está congelado. Útil solo como referencia de
  diseño, no como dependencia viva.
- **`iaincollins/structured-data-testing-tool`** 🔧⚠️ — 82★ `[API]`, último push **2023-07-31**
  `[API]` (>3 años). Detecta JSON-LD/RDFa/Microdata automáticamente. Mecanismo real pero
  claramente abandonado — sospechar antes de depender de él para schema en 2026.
- **`amplifying-ai/awesome-generative-engine-optimization`** 📝 — 494★ `[WF]`. Lista curada (no
  herramienta) de guías, papers y plataformas GEO por motor (AI Overviews, ChatGPT, Perplexity).
  Sirve como índice de descubrimiento, no como mecanismo — usar para encontrar más recursos, no
  como especialista en sí.
- **`puneetindersingh/open-seo-crawler`** 🔧 — 31★ `[WF]`, MIT, Flask, self-hosted, consciente de
  CMS (Shopify/WordPress/Yoast-RankMath/Webflow). Mecanismo real pero adopción mínima — vigilar
  antes de apostar por él sobre LibreCrawl.
- **`FassihFayyaz/SEO-Clustering-Tool`** 🔧💰 — 7★ `[WF]`, MIT, Streamlit. Clustering semántico
  **gratis** con embeddings locales; el clustering por SERP-overlap 💰 requiere DataForSEO de pago.
  Adopción casi nula (7 estrellas) — usar el modo semántico local, evitar activar DataForSEO sin
  orden.
- **MCP de schema/SEO menores, sin verificar en profundidad** — `Theycallmeholla/schema-org-mcp`,
  `RichardDillman/seo-audit-mcp`, `mgsrevolver/seo-inspector-mcp`, `Docker-Hunterpedia/seo-mcp-server`,
  `mikusnuz/gsc-mcp`: aparecen en los resultados con mecanismo declarado (validación JSON-LD,
  integración Lighthouse, cobertura completa de la API de GSC/Indexing) pero no se les hizo
  WebFetch individual por presupuesto de búsqueda agotado en esta sesión — revisar antes de
  adoptar, no descartar.
- **`Shinobis-dev/llmstxt-generator`** y **`bridgetoagent/llms-txt-validator`** 🔧 — generador y
  validador de `llms.txt` (el "robots.txt para IA"), gratis, siguen el estándar llmstxt.org. No se
  verificaron estrellas/actividad; útil para la subárea GEO junto a #4.
- **`r0yfire/python-sitemap-generator`** 🔧 — generador de sitemaps XML con soporte de índice para
  sitios de +50.000 URLs. Utilidad pequeña pero mecanismo correcto; no imprescindible si ya se usa
  advertools (#7) para sitemaps.

---

## Humo

Una línea cada uno. Prosa genérica, wrappers finos, o directamente arriesgado.

- `maivyly52-gif/backlink-generator` y la org `backlink-generator-tool` — generación automatizada
  de backlinks en directorios: es la práctica exacta que Google penaliza; no usar ni para un
  cliente, riesgo de penalización manual.
- `reggy18/competitor-backlink-tool` — descripción de vendedor ("descubre oportunidades", "reportes
  visuales") sin mecanismo visible en el repo; huele a plantilla genérica.
- `digitaldonusum/LLMs.txt-Generator` — se lee más como landing de marketing de contenidos que como
  repositorio de código real.
- `respectlytics/respectaso` — es investigación de keywords para **App Store (ASO)**, no SEO web:
  fuera de dominio pese a aparecer en la búsqueda.
- `ai-search-guru/getcito-worlds-first-open-source-aio-aeo-or-geo-tool` — el propio nombre
  ("world's first & only") es la señal de alarma clásica; no verificado, tratar con sospecha.
- `kenancn/seo-analysis-tool`, `ercanatay/cybokron-backlink-checker` — wrappers pequeños sin señal
  de adopción ni mecanismo diferenciado de lo que ya cubren `advertools` o `LibreCrawl`.
- `aaron-he-zhu/seo-geo-claude-skills` — repo "signpost": las 16 skills activas se movieron a un
  bundle de marketing más grande (120 skills); la versión standalone (v9.9.12) ya no recibe
  actualizaciones. No instalar la versión vieja.
- Docenas de "SEO checker" / "AI visibility tool" con menos de 10 estrellas encontrados en los
  resultados de búsqueda genéricos: mismo patrón — README con lista de features, cero commits de
  sustancia. No se listan uno a uno porque ninguno pasó el primer filtro de "mecanismo, no prosa".

---

## Mapeo a COSMOS

Propuesta encajable en la taxonomía (`sistema-solar > planeta > continente > país > provincia >
ciudad > pueblo`), saltando niveles donde no agrupan de verdad (regla de COSMOS: un nivel con un
solo hijo se borra).

```
sistema-solar: Trabajo de agencia con webs de cliente     (modo permanente, no se acaba)
  continente:  Marketing y visibilidad                     (disciplina dentro del proyecto-cliente)
    país:      Adquisición de tráfico                      (mi dominio asignado — familia de
                                                             capacidades que comparten el modelo
                                                             mental "que te encuentren y te citen")
      provincia: SEO técnico y crawling
        pueblo:  Auditoría técnica de sitio (AgriciDaniel/claude-seo, LibreCrawl, advertools, seonaut)
        pueblo:  Core Web Vitals a escala de sitio (unlighthouse sobre lighthouse)
        pueblo:  Sitemaps y robots.txt (advertools, r0yfire/python-sitemap-generator)

      provincia: Datos estructurados y GEO/AEO
        pueblo:  Validación y generación de JSON-LD/schema.org
        pueblo:  Auditoría GEO/AEO y crawlers de IA (Auriti-Labs/geo-optimizer-skill)
        pueblo:  llms.txt (generación y validación)

      provincia: Contenido y keyword research
        pueblo:  Workspace de contenido SEO (TheCraigHewitt/seomachine)
        pueblo:  Investigación y clustering de keywords
        pueblo:  E-E-A-T y calidad de contenido

      provincia: SEO local
        pueblo:  (ya cubierto en este workspace por la skill local `gbp-optimizar` — Google
                 Business Profile vía OAuth; no encontrado equivalente GitHub con más mecanismo)

      provincia: Autoridad y competencia
        pueblo:  Análisis de backlinks y competencia (sin representante de primera fila real —
                 ver "Lo que falta")

      provincia: Medición
        pueblo:  Search Console (Suganthans-GSC-MCP)
        pueblo:  GA4 (surendranb/google-analytics-mcp)
        pueblo:  Rank tracking (serpbear)
        pueblo:  Visibilidad en motores de IA (elmo — con el 💰 declarado)
```

Nota: `claude-seo` (#1) y `claude-seo-ai` (#2, ya instalado) actúan como **orquestadores** que
internamente ya cubren varias provincias a la vez (son "país completo" empaquetado). El resto de
entradas de primera fila son piezas de una sola provincia, útiles para reforzar o sustituir un
módulo concreto del orquestador sin traerse el paquete entero.

---

## Lo que falta

- **Link building / análisis de backlinks con mecanismo real**: es el hueco más claro del barrido.
  Todo lo encontrado en esta subárea es humo (generación automática de spam) o wrappers sin
  adopción. No hay un equivalente gratuito y vivo a Ahrefs/Majestic con un índice de backlinks
  propio — construir un índice de backlinks desde cero es carísimo (requiere crawling masivo
  constante), así que es razonable que no exista gratis. **Alternativa real**: usar Search Console
  (enlaces externos, gratis pero limitado al propio dominio) + el módulo de backlinks incluido en
  `AgriciDaniel/claude-seo` (#1) en vez de buscar un especialista dedicado.
- **Análisis de competencia con mecanismo (no solo SERP scraping genérico)**: tampoco apareció un
  repo dedicado y vivo; lo más cercano es el scraping de SERP dentro de `advertools` (#7) o
  `SEO-Clustering-Tool` (segunda fila, requiere DataForSEO de pago para esa parte).
- **SEO local fuera de Google Business Profile**: no se encontró un repo GitHub que gestione NAP
  (Name-Address-Phone) consistency across directorios (Apple Maps, Bing Places, Waze) con
  mecanismo real y gratis — todo lo que apareció era SaaS de pago (LocalClarity y similares).
- **Verificación en vivo pendiente**: ninguno de los repos de "De primera" se instaló ni se ejecutó
  en esta investigación — es lectura de repos, no prueba de campo. Antes de comprometerse con
  `AgriciDaniel/claude-seo` (#1) como reemplazo/complemento del `claude-seo-ai` ya instalado,
  instalarlo en un entorno de prueba y correr `/scan-skills` (gate de seguridad obligatorio del
  workspace para toda skill de terceros) antes de usarlo con datos de cliente real.
- **Presupuesto de búsqueda agotado a mitad de sesión**: WebSearch llegó a su límite de 200
  llamadas (compartido con otras tareas activas en el mismo periodo) antes de poder profundizar en
  `firecrawl` (scraping para agentes, mencionado varias veces como dependencia opcional de otros
  repos) ni en los MCP de schema/SEO menores listados sin verificar en "Segunda fila". Si se
  necesita cerrar ese hueco, repetir la búsqueda en una sesión nueva.
