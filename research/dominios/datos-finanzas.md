# Datos y dinero — barrido GitHub

Barrido vía API de GitHub autenticada (búsqueda + `repos/OWNER/REPO` en vivo, 2026-09-01). Cupo de
`WebSearch` de la sesión agotado — cero contenido de este informe viene de memoria ni de búsqueda
web; todo enlace, cifra y licencia sale de una llamada a `api.github.com` con respuesta comprobada en
el momento. Lo que no se verificó en vivo se marca **NO VERIFICADO**. Alcance: ingeniería de datos y
ETL, análisis y visualización, hojas de cálculo, cuadros de mando, previsión y métricas de negocio.
Del lado financiero, solo análisis cuantitativo — bots de trading, exchanges y backtesting los cubre
otro barrido en paralelo, sin duplicar aquí.

## De primera

Máximo 10. Ganan por combinar: **mecanismo verificado** (motor que se ejecuta, no consejo), **coste
cero** sin tarjeta de por medio, **detecta datos malos** antes que los pinta bonitos, **cabe en 8 GB**
(columnar/streaming/out-of-core en vez de cargarlo todo en RAM) y **está vivo** (commits en las
últimas semanas, no un README parado).

### 1. DuckDB 🔧 — el motor analítico que no necesita servidor
- **URL**: https://github.com/duckdb/duckdb · **Estrellas**: 40.889 · **Licencia**: MIT ·
  **Última actividad**: 2026-09-01 (commits diarios).
- **Qué hace**: base de datos analítica columnar **embebida** (un solo binario/librería, sin proceso
  servidor) con SQL completo — subconsultas correladas, window functions, tipos anidados. Lee CSV y
  Parquet directo con `SELECT * FROM 'archivo.csv'`, sin ETL previo.
- **Por qué cabe en 8 GB**: motor vectorizado que **derrama a disco** cuando una consulta no cabe en
  memoria (spilling), en vez de fallar o cargar todo el dataset — la diferencia real frente a cargar
  un CSV entero en pandas.
- **Es la base del resto de la lista**: Evidence y varios MCP de esta lista se apoyan en él.

### 2. Polars 🔧 — pandas sin el problema de memoria
- **URL**: https://github.com/pola-rs/polars · **Estrellas**: 39.577 · **Licencia**: MIT ·
  **Última actividad**: 2026-09-01.
- **Qué hace**: motor de dataframes en Rust con API tipo pandas. Modo **lazy** (`pl.scan_csv`)
  construye un plan de consulta y solo materializa lo que hace falta; el motor **streaming** procesa
  por lotes sin cargar el fichero entero.
- **Mecanismo de fallo ruidoso**: los tipos se infieren y se fijan en el schema — una columna con un
  tipo inesperado revienta el `.collect()` con el error de tipo exacto, no un `NaN` silencioso.
- **Caveat real**: el motor streaming no cubre el 100% de las operaciones todavía (algunos `join`/
  `groupby` complejos caen a modo in-memory) — verificar el caso concreto antes de asumir que un
  dataset de 20 GB "simplemente funciona".

### 3. Great Expectations (GX Core) 🔧 — el estándar de validación de datos
- **URL**: https://github.com/fivetran/great_expectations (el repo histórico
  `great-expectations/great_expectations` redirige aquí — **dato verificado en vivo**: mismo `id` de
  repo, mismo `created_at` de 2017, la organización propietaria en GitHub cambió a `fivetran`) ·
  **Estrellas**: 11.761 · **Licencia**: Apache-2.0 · **Última actividad**: 2026-08-31.
- **Qué hace**: define "expectativas" (`expect_column_values_to_not_be_null`,
  `expect_column_values_to_be_between`, etc.) contra un dataset y produce un `ValidationResult` con
  cada expectativa que falló, cuántas filas la violaron y ejemplos concretos — no un booleano mudo.
- **Detecta antes de pintar**: es exactamente el filtro "calidad de datos por encima de la
  visualización" — se corre antes de que cualquier dashboard toque los datos.
- **Caveat**: es la opción pesada de esta categoría (instala Pydantic, Jinja2, genera "Data Docs"
  HTML); para un caso simple, Pandera (siguiente) pesa mucho menos.

### 4. Pandera 🔧 — validación de esquema ligera, in-process
- **URL**: https://github.com/unionai-oss/pandera · **Estrellas**: 4.446 · **Licencia**: MIT ·
  **Última actividad**: 2026-09-01.
- **Qué hace**: define un `DataFrameSchema` (o un modelo con decoradores tipo Pydantic) con tipo,
  rango, nulabilidad y checks custom por columna; funciona sobre pandas, Polars, Dask y PySpark con
  la misma API.
- **Por qué complementa a GX en vez de duplicarlo**: sin servidor de Data Docs, sin dependencias
  pesadas — se importa y se llama como una función más dentro de un pipeline. Para "valida esta
  función pura antes de seguir" (regla del revisor adversarial de este workspace: ejecutar, no
  opinar) es la herramienta correcta.

### 5. dbt-core 🔧 — transformación SQL con tests incorporados
- **URL**: https://github.com/dbt-labs/dbt-core · **Estrellas**: 13.754 · **Licencia**:
  Apache-2.0 (verificado en vivo — dbt Core en sí es open source; dbt Cloud es el producto de pago
  aparte) · **Última actividad**: 2026-09-01.
- **Qué hace**: transforma datos con SQL versionado en Git, y trae tests declarativos
  (`unique`, `not_null`, `accepted_values`, `relationships`) que fallan el build si el dato no
  cumple — la validación vive en el mismo sitio que la transformación, no en un script aparte.
- **Estándar de facto**: es el lenguaje común entre motores (funciona sobre DuckDB, Postgres,
  Snowflake, BigQuery…) — mover de local a la nube no reescribe la lógica.

### 6. Streamlit 🔧 — dashboards en Python puro
- **URL**: https://github.com/streamlit/streamlit · **Estrellas**: 45.655 · **Licencia**: Apache-2.0
  · **Última actividad**: 2026-09-01.
- **Qué hace**: convierte un script Python en una app web interactiva con widgets — sin HTML/CSS/JS.
  Recarga el script entero en cada interacción y cachea con `@st.cache_data`.
- **Caveat de memoria (8 GB)**: Streamlit no tiene motor de datos propio — si el script carga un
  `pandas.read_csv()` de 5 GB en cada rerun, el problema no es Streamlit, es no delegarle la carga a
  DuckDB/Polars por debajo. Combinado con #1/#2 es la pila correcta; solo no cubre el filtro de
  escala real.

### 7. Evidence 🔧 — BI como código, sin servidor que mantener
- **URL**: https://github.com/evidence-dev/evidence · **Estrellas**: 6.898 · **Licencia**: MIT ·
  **Última actividad**: 2026-08-31.
- **Qué hace**: informes en Markdown con bloques SQL embebidos que se compilan a un sitio estático
  con gráficos interactivos — el informe entero vive versionado en Git, y por defecto usa **DuckDB**
  como motor de consulta (encaja directo con #1).
- **Por qué gana a un BI con servidor**: nada que desplegar ni mantener vivo — el output es HTML
  estático servible desde cualquier sitio, coste de hosting cero.

### 8. statsforecast (Nixtla) 🔧 — previsión estadística, sin deep learning
- **URL**: https://github.com/Nixtla/statsforecast · **Estrellas**: 4.892 · **Licencia**: Apache-2.0
  · **Última actividad**: 2026-09-01.
- **Qué hace**: `AutoARIMA`, `ETS`, `CES`, `Theta` y una batería de modelos econométricos clásicos,
  vectorizados con Numba — README confirma que es CPU-only, sin dependencia de PyTorch/TensorFlow
  (verificado leyendo el README en vivo).
- **Por qué gana sobre Prophet/redes neuronales en un Mac de 8 GB**: los modelos estadísticos
  clásicos no necesitan GPU ni un runtime de deep learning cargado en memoria; Prophet además arrastra
  la dependencia de compilación de Stan, un punto de fallo típico en instalación. Para pronóstico de
  demanda o series de negocio (no trading de alta frecuencia, fuera de este alcance) es la opción más
  ligera que sigue siendo seria.

### 9. excel-mcp-server 🔧 — Excel nativo para un agente, no para un humano
- **URL**: https://github.com/haris-musa/excel-mcp-server · **Estrellas**: 4.147 · **Licencia**: MIT
  · **Última actividad**: 2026-04-12 (**sin push en ~5 meses** — señal de enfriamiento, no de
  abandono: 456 forks y 68 issues abiertas indican uso real, pero conviene revisar el fork más activo
  antes de adoptarlo en producción).
- **Qué hace**: servidor MCP que expone lectura/escritura de `.xlsx` (celdas, fórmulas, formato,
  gráficos) como *tools* que un agente invoca directamente — sin abrir Excel, sin macros.
- **Por qué encaja en COSMOS específicamente**: es la única entrada de esta lista pensada desde el
  origen para que la use un **agente**, no un humano con un notebook — coherente con que COSMOS es un
  harness de agentes, no una suite de BI para analistas.

### 10. gspread 🔧 — Google Sheets como base de datos, vía API oficial
- **URL**: https://github.com/burnash/gspread · **Estrellas**: 7.506 · **Licencia**: MIT ·
  **Última actividad**: 2026-07-30.
- **Qué hace**: envoltorio directo de la Google Sheets API v4 — leer/escribir celdas y rangos,
  formato condicional, fórmulas, todo con una cuenta de servicio gratuita de Google Cloud (capa
  gratuita, sin tarjeta si se queda dentro de las cuotas del API).
- **Caso de uso real para este workspace**: automatizar informes que un cliente ya consume en Google
  Sheets sin migrarlo a un dashboard nuevo — la hoja de cálculo sigue siendo la interfaz.

## Segunda fila

- **Ibis** (ibis-project/ibis, 6.649★, Apache-2.0) — API tipo pandas que compila a SQL sobre 20+
  motores (incluido DuckDB); útil si el mismo código debe correr local y luego contra un warehouse
  en la nube sin reescribirse.
- **sqlglot** (tobymao/sqlglot, 9.581★, MIT) — parser y transpilador de SQL entre dialectos; utilidad
  de bajo nivel para cualquier herramienta que genere o valide SQL programáticamente.
- **soda-core** (sodadata/soda-core, 2.420★, licencia `NOASSERTION` en GitHub — **verificar el
  fichero LICENSE exacto antes de adoptar**) — "contratos de datos" declarativos en YAML, alternativa
  más ligera a Great Expectations para checks simples.
- **Prefect** (PrefectHQ/prefect, 23.747★, Apache-2.0) y **Dagster** (dagster-io/dagster, 16.079★,
  Apache-2.0) — orquestación de pipelines en Python con reintentos y observabilidad; más peso que
  falta hacer si el pipeline es un solo script con cron, pero es el escalón natural cuando hay varios
  pasos dependientes. **Apache Airflow** (46.677★, Apache-2.0) es el más pesado y el más instalado en
  empresa — considerar solo si ya existe infraestructura para sostenerlo.
- **WeasyPrint** (Kozea/WeasyPrint, 9.546★, BSD-3) — convierte HTML/CSS a PDF con motor propio;
  la forma más simple de generar un informe con buena tipografía a partir de una plantilla Jinja2.
- **fpdf2** (py-pdf/fpdf2, 1.537★, LGPL-3.0) y **XlsxWriter** (jmcnamara/XlsxWriter, 3.968★,
  BSD-2-Clause) — generación directa de PDF y XLSX sin motor de renderizado HTML, para reportes más
  simples o con muchas fórmulas/gráficos nativos de Excel.
- **papermill** (nteract/papermill, 6.477★, BSD-3) — parametriza y ejecuta notebooks Jupyter desde
  código o cron; forma barata de convertir un análisis exploratorio en un informe programado.
- **quarto-cli** (quarto-dev/quarto-cli, 5.972★, licencia `NOASSERTION` en GitHub — es de Posit/
  RStudio, verificar el LICENSE real) — publica el mismo documento a HTML/PDF/Word desde Markdown +
  código ejecutable; más pesado que WeasyPrint pero con mejor soporte de gráficos embebidos.
- **mcp-server-chart** (antvis/mcp-server-chart, 4.346★, MIT) — servidor MCP con 25+ tipos de gráfico
  vía AntV; complementa a excel-mcp-server para que un agente genere visualizaciones sin tocar un
  notebook.
- **Metabase** (metabase/metabase, 49.035★, **dual-licencia verificada en vivo**: AGPL fuera del
  directorio `enterprise/`, licencia comercial de Metabase dentro — no es MIT/Apache simple) y
  **Apache Superset** (apache/superset, 74.572★, Apache-2.0) — plataformas BI completas con más
  usuarios simultáneos que un solo agente; en un Mac de 8 GB, Metabase (JVM) y Superset (necesita
  Postgres/Redis/Celery en producción) pesan más que todo el resto de esta lista junto — valorar solo
  para un servidor dedicado, no para uso local del agente.
- **Vaex** (vaexio/vaex, 8.509★, MIT, **último push 2026-04-01** — 5 meses sin commits, señal de
  ritmo bajando) y **Modin** (modin-project/modin, 10.393★, Apache-2.0, **último push 2026-02-10** —
  7 meses) — dataframes out-of-core / escalado de pandas; siguen vivos pero con menos tracción que
  Polars, que ha absorbido buena parte de ese caso de uso.
- **jdatamunch-mcp** (jgravelle/jdatamunch-mcp, 81★, licencia sin detectar) — MCP que indexa CSV/
  Excel y responde consultas agregadas sin volcar el fichero entero al contexto del agente; pocas
  estrellas pero el mecanismo (ahorro de tokens en consulta tabular) encaja de forma muy directa con
  cómo trabaja un harness de agentes — **NO VERIFICADO** en profundidad, revisar antes de adoptar.
- **lightdash** (lightdash/lightdash, 6.111★, licencia `NOASSERTION`) — capa de métricas encima de
  dbt con BI conversacional; útil si ya se adoptó dbt-core (#5) y hace falta una capa de consulta en
  lenguaje natural encima.

## Humo

- **Amundsen** (amundsen-io/amundsen, 4.783★, Apache-2.0) — catálogo de datos/lineage, pero necesita
  Neo4j o Elasticsearch detrás: infraestructura de más para uso individual.
- **xlwings** (xlwings/xlwings, 3.399★, licencia `NOASSERTION`) — puente Python↔Excel, pero requiere
  Microsoft Excel instalado de verdad (no headless) — coste de licencia de Office implícito.
- **cc-equity-research** (prof-little-bear/cc-equity-research, 88★) y **finance-super-skill**
  (get-zeked/finance-super-skill, 19★) — bundles de skills de Claude Code para análisis cuantitativo/
  research de renta variable; muy pocas estrellas, sin verificar en profundidad.
- **dbt-semantic-layer** (keithbinkly/dbt-semantic-layer, 7★) — skill de Claude para MetricFlow;
  demasiado pequeño para confiar sin auditar el código.
- **theseus_growth** (ESeufert/theseus_growth, 216★, sin push desde 2023) y **cohort_me**
  (n8/cohort_me, 319★, sin push desde 2021) — librerías de análisis de cohortes, ambas dormidas.
- **growthcues-core** (ArvoanDev/growthcues-core, 11★) — capa semántica de métricas B2B SaaS sobre
  dbt; proyecto muy joven.
- **precis-finance-mcp** (precis-finance/precis-finance-mcp, 5★) — MCP de FP&A/reporting gestionado;
  demasiado pequeño para evaluar viveza real.
- **saasboard** / **SaaS-dashboard-frontend** (~30-47★) — plantillas de frontend para dashboards de
  KPI SaaS, sin motor de datos detrás — solo maquetación.
- Múltiples MCP de Google Sheets compitiendo sin diferenciación clara (xing5/mcp-google-sheets,
  freema/mcp-gsheets, mkummer225/google-sheets-mcp, isaacphi/mcp-gdrive) — todos MIT, pocas
  estrellas, sin evidencia de cuál es el que la comunidad convergió a usar.
- Varios validadores CSV pequeños (datahappy1/csv_file_validator, GeoCodable/schema_validata,
  ipriyaaanshu/smart-schema) — cubren lo mismo que Pandera con mucho menos uso real detrás.

## Mapeo a COSMOS

Según `spec/TAXONOMIA.md`, un **país** es "una familia de capacidades que comparten tecnología o
modelo mental". Este dominio no es un país único: agrupa **varios modelos mentales distintos**
(cómputo columnar embebido ≠ afirmar expectativas sobre datos ≠ presentar lo ya validado ≠ ajustar un
modelo estadístico ≠ leer/escribir una hoja de cálculo), así que propongo **varios países** bajo el
continente "Datos" (disciplina, según la definición de continente de la taxonomía — la existencia y
nombre exacto de ese continente los decide quien compile el árbol completo, no este barrido).

| País (modelo mental compartido) | Provincia (skills hermanas) | Pueblos (herramienta atómica de este barrido) |
|---|---|---|
| **Motor analítico local** | Cómputo columnar embebido | DuckDB, Polars, Ibis |
| | Utilidad SQL de bajo nivel | sqlglot |
| **Calidad y contratos de datos** | Validación de esquema pesada | Great Expectations |
| | Validación de esquema ligera in-process | Pandera |
| | Contratos declarativos YAML | soda-core (verificar licencia) |
| **Transformación declarativa** | SQL versionado con tests | dbt-core |
| **Cuadros de mando y BI** | Dashboards en Python puro | Streamlit |
| | BI como código (estático, sin servidor) | Evidence |
| | Generación de gráficos para agentes | mcp-server-chart |
| | BI con servidor (uso multiusuario) | Metabase (dual-licencia), Apache Superset |
| **Previsión cuantitativa** | Modelos estadísticos clásicos | statsforecast |
| **Automatización de oficina** | Hojas de cálculo desde un agente | excel-mcp-server, gspread, XlsxWriter |
| | Documentos y PDF | WeasyPrint, fpdf2, papermill, quarto-cli |
| **Orquestación de pipelines** *(si nace fuera de un solo script)* | Workflows con reintentos | Prefect, Dagster |

Ninguna de estas herramientas tiene hoy partes que se carguen aparte según el caso de uso (la prueba
de "ciudad" de la taxonomía), así que todas entran como **pueblo**, no como ciudad — la señal de
ascenso sería, por ejemplo, que una skill de "Motor analítico local" empaquetase por separado el
soporte de Parquet remoto frente al de CSV local.

**Hueco real de país**: "métricas de negocio" (unit economics, LTV, churn, cohortes) tal como lo pide
el encargo **no tiene un país sano** en este barrido — ver "Lo que falta".

## Lo que falta

- **Unit economics / LTV / cohortes: no hay estándar de facto vivo.** Busqué explícitamente
  (`cohort+analysis`, `unit+economics+SaaS+metrics`) y lo único que apareció son proyectos de
  ejemplo o de aula dormidos desde 2018-2023 (theseus_growth, cohort_me, retention-graph-cohort-
  analysis) y plantillas de frontend sin motor detrás (saasboard). Si COSMOS necesita esta capacidad
  de verdad, hoy se construye a mano sobre SQL (dbt-core + un par de modelos de cohorte) en vez de
  adoptar una librería — no hay atajo verificado.
- **Business Intelligence conversacional/agentic (Canner/WrenAI, holoviz/lumen, mprove)**: aparecieron
  con tracción real (WrenAI 17.437★) pero no los metí en primera fila porque son productos completos
  con su propia capa de LLM — mezclan "motor de datos" con "agente", que es justo la capa que COSMOS
  ya provee por su cuenta. Quedan para una decisión de arquitectura, no de librería suelta.
- **Licencias `NOASSERTION` sin resolver**: quarto-cli, soda-core, lightdash y xlwings muestran
  `NOASSERTION` en la API de GitHub — no significa código cerrado, significa que GitHub no pudo
  clasificar el fichero LICENSE automáticamente. Antes de adoptar cualquiera, leer el LICENSE real.
- **No verifiqué footprint de RAM en frío** de ninguna herramienta corriendo de verdad en un Mac de
  8 GB — todo lo anterior sobre "cabe/no cabe" sale de arquitectura documentada (streaming, spilling,
  JVM vs proceso nativo), no de una medición con `/usr/bin/time` o Activity Monitor. Si se adopta algo
  de la lista "Metabase/Superset/Vaex/Modin", medirlo en vivo antes de comprometerse.
- **Sin cobertura de MDX/OLAP clásico** (Mondrian, Cube.dev) — quedó fuera del rastreo por presupuesto
  de tiempo, no por descarte deliberado.
