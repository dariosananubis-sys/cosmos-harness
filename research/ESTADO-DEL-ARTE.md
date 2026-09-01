# Estado del arte — organización jerárquica de contexto para agentes de código

> Investigación para COSMOS. Objetivo del rastreo: qué existe ya en carga perezosa / jerarquía de
> contexto para agentes tipo Claude Code, con el mecanismo concreto (no la promesa de marketing).
> Método: WebSearch + WebFetch sobre documentación oficial, repos de GitHub, papers y blogs de
> ingeniería. Sin acceso a terminal de los repos (no se clonó ningún repo, todo es lectura remota),
> así que las cifras de estrellas/forks son las que reportan las fuentes secundarias — se marcan como
> «no verificado» cuando la fuente es dudosa. Fecha de la investigación: 2026-09-01.
>
> Convención de esta tabla: 🔧 = mecanismo real y verificable · 📝 = solo prosa/consejo, sin mecanismo
> forzado por código · ⚠️ = mecanismo real pero con hueco importante declarado por el propio proyecto.

---

## 1. Anthropic oficial — Agent Skills y progressive disclosure

### 1.1 Agent Skills (plataforma oficial) 🔧

- **URL**: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- **Última actividad**: documentación viva, revisada en la fecha de esta investigación (2026-09).
- **Problema que resuelve**: que instalar N skills no cueste N × (instrucciones completas) en cada
  turno.
- **Mecanismo concreto** (documentado con tabla oficial, no es aproximación):

  | Nivel | Cuándo carga | Coste | Contenido |
  |---|---|---|---|
  | 1. Metadata | Siempre, al arrancar | ~100 tokens/skill | `name` + `description` del frontmatter YAML |
  | 2. Instrucciones | Cuando la skill se dispara | <5k tokens | Cuerpo de `SKILL.md` |
  | 3. Recursos/código | Solo si se referencian | 0 tokens hasta acceder | Ficheros adicionales (`FORMS.md`, `scripts/*.py`) |

  El disparo del nivel 2 es literal: Claude ejecuta `bash: cat skill/SKILL.md` y **eso** es lo que
  mete tokens en contexto — no hay un paso de "resumen" ni un índice vectorial de por medio. Los
  scripts (nivel 3) se ejecutan por bash y **solo su salida** entra en contexto; el código del script
  nunca se carga. Nivel 3 no tiene límite práctico de contenido bundleado porque nada de eso cuenta
  hasta que se lee.
- **Reglas duras de `name`**: máx 64 caracteres, solo minúsculas/números/guiones, sin XML, sin
  "anthropic"/"claude". `description` máx 1024 caracteres, sin XML, tiene que decir **qué hace Y
  cuándo usarla** (es literalmente el texto contra el que Claude hace matching).
- **Qué le falta / dónde se queda corto**:
  - Es una jerarquía de **2 niveles reales con un tercero opcional plano** (metadata → cuerpo →
    ficheros sueltos). No hay noción de "familia de skills" ni de contención skill-dentro-de-skill
    a nivel de producto — ver punto 6 (Claude Code no descubre `SKILL.md` anidados, issue abierto).
  - No hay validador oficial de huérfanos, colisiones de `description` entre skills, ni presupuesto
    global de cuántas skills-metadata caben antes de que el propio índice pese demasiado.
  - Progressive disclosure asume que el *agente* decide bien cuándo activar cada nivel; si el
    `description` está mal escrito, el mecanismo estructural no salva una mala descripción (sigue
    dependiendo de que el LLM interprete bien el texto de nivel 1).
- **Robable para COSMOS**: la tabla de 3 niveles con coste explícito por nivel es el patrón de
  referencia para la sección "Reglas de carga" del `GOAL.md` de COSMOS — confirma que "Ciudad/Pueblo"
  (skills) debe seguir exactamente esta forma: nombre+descripción siempre, cuerpo bajo demanda,
  "Casa" (ficheros de referencia) con coste cero hasta que se abren. Los límites de `name`/
  `description` (longitud, sin XML) son directamente aplicables al validador de COSMOS.

### 1.2 Blog de ingeniería: "Equipping agents for the real world with Agent Skills" 🔧/📝

- **URL**: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- **Aporta sobre lo anterior**: la justificación de diseño explícita — "progressive disclosure is the
  core design principle" y la comparación implícita contra RAG: en vez de recuperar por embeddings,
  la jerarquía de ficheros ya ordena la información por especificidad (metadata → manual → apéndice).
  Analogía citada: "un manual bien organizado que empieza con índice, luego capítulos, luego un
  apéndice detallado" — es literalmente la misma lógica que la taxonomía cosmográfica de COSMOS
  (galaxia → sistema → ... → casa).
- **Limitaciones que Anthropic reconoce por escrito**: quieren que los agentes puedan crear/editar/
  evaluar skills por sí mismos (no existe hoy); la relación Skills↔MCP está "en exploración", no
  resuelta; la seguridad depende de auditoría manual, no hay sandboxing automático del contenido de
  una skill maliciosa.
- **Robable**: nada nuevo de mecanismo, pero es la cita de autoridad para justificar el principio
  rector de COSMOS ("no se pide gastar menos, se elimina la razón para gastar") — Anthropic lo dice
  con otras palabras y sin ir más allá de la skill individual; COSMOS extiende esa misma idea al
  harness entero.

### 1.3 Tool Search Tool — deferred loading de herramientas MCP 🔧

- **URL**: https://www.anthropic.com/engineering/advanced-tool-use ·
  https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool
- **Problema que resuelve**: MCP con muchos servidores conectados mete decenas de miles de tokens de
  definiciones de tool antes de que el agente haga nada (este mismo caso: la lista de tools
  diferidas que aparece al inicio de esta sesión es un ejemplo en vivo).
- **Mecanismo concreto**: cada tool se marca `defer_loading: true/false`. **Se sigue enviando la
  definición completa de TODAS las tools en cada request** (esto es clave y contraintuitivo: el
  ahorro no es de payload de request, es de lo que entra al *contexto visible del modelo*) — las
  marcadas como diferidas no aparecen en el contexto inicial, solo la Tool Search Tool (~500 tokens)
  y las no diferidas. Cuando el modelo llama a `tool_search`, los resultados que matchean se
  "expanden a definición completa" y se inyectan al final del contexto en ese momento.
- **Cifras dadas por Anthropic**: sin tool search, 147 definiciones de tool ≈ 90.000 tokens; con tool
  search, ~25 tools nativas + la propia tool de búsqueda ≈ 15.000 tokens — 85% de reducción. Otro
  ejemplo citado: de ~77K tokens a ~8.7K (equivalente, ~85-89%).
- **Compatibilidad con prompt caching**: las tools diferidas quedan fuera del prompt inicial, así que
  no rompen el cache del system prompt — detalle de implementación importante si COSMOS diseña algo
  parecido para "cargar" sistemas solares o continentes sin invalidar cache de turno en turno.
- **Qué le falta**: es *tool-level*, no *context-level* — no cubre CLAUDE.md, memoria ni skills; es
  un mecanismo hermano, no un sistema jerárquico de organización de todo el harness.
- **Robable**: el patrón "el índice se manda siempre completo pero solo lo relevante se *expande* al
  contexto visible" es exactamente el modelo que un validador de COSMOS necesita para las
  "Provincias" (grupos de skills): un índice plano y barato que apunta a contenido caro, con
  expansión bajo demanda y sin romper cache.

### 1.4 "Effective context engineering for AI agents" (Anthropic, blog general) 🔧

- **URL**: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- **Mecanismos descritos** (cuatro, todos con implementación real citada en Claude Code):
  1. **Compaction**: al acercarse al límite, resumir la conversación entera y reiniciar con el
     resumen, preservando "decisiones arquitectónicas, bugs sin resolver, detalles de implementación"
     y descartando outputs redundantes.
  2. **Nota estructurada persistida** (NOTES.md / memory tool): el agente escribe fuera del contexto
     y lo recupera después — Anthropic lo tiene como *memory tool* en beta en la plataforma.
  3. **Subagentes con contexto limpio**: cada uno devuelve **1.000-2.000 tokens** de resumen
     destilado al agente líder — es el único umbral numérico explícito de todo el post.
  4. **Recuperación "just-in-time"**: el agente guarda identificadores ligeros (rutas, queries,
     enlaces) y carga bajo demanda en vez de precargar — "imita mejor la cognición humana que la
     recuperación exhaustiva anticipada".
- **Qué le falta**: sigue siendo consejo de *comportamiento del agente* en tiempo de ejecución
  (compactar, tomar notas), no una *estructura previa* que impida que el problema aparezca. Es
  exactamente la distinción que hace COSMOS en su principio rector: esto es "pedir que se gaste
  menos" (aunque con herramientas, no solo exhortación en prosa); COSMOS quiere "que no haya nada que
  gastar" antes de que el agente decida nada.
- **Robable**: el rango de 1.000-2.000 tokens para resumen de subagente es un dato duro reutilizable
  como presupuesto de referencia para la "Luna" (subagente) de COSMOS. El énfasis en "lightweight
  identifiers" en vez de contenido es el mismo principio que "un nivel no describe a sus hijos, los
  nombra" del `GOAL.md`.

---

## 2. Sistemas de memoria jerárquica (proyectos de terceros)

### 2.1 `hierarchical-agent-memory` (HAM) — instalado localmente en este workspace 🔧⚠️

- **URL fuente**: https://github.com/kromahlusenii-ops/ham (vía skill instalada en
  `.claude/skills/hierarchical-agent-memory/SKILL.md` de este mismo repo, añadida 2026-02-27).
- **Es el proyecto más cercano en intención a COSMOS que existe ya en este disco.** Merece lectura
  directa porque es la comparación más justa.
- **Problema que resuelve**: que el agente re-lea todo el proyecto en cada prompt.
- **Mecanismo concreto**: `CLAUDE.md` raíz (~200 tokens) + un `CLAUDE.md` por subdirectorio (~250
  tokens) + capa `.memory/` (decisions.md, patterns.md, inbox.md, audit-log.md). El raíz incluye una
  sección "Context Routing" que es literalmente una lista `→ api: src/api/CLAUDE.md` — el agente lee
  el raíz y de ahí decide qué subcontexto cargar.
- **Jerarquía real**: **solo 2 niveles** (raíz + un nivel de subdirectorio). No hay nivel 3 (no hay
  "subdirectorio de subdirectorio" con su propio `CLAUDE.md` encadenado ni contención recursiva).
- **Validación**: `ham audit` es un "health check" pero el propio README admite que **no hay
  tokenizer real** (aproximación 4 chars = 1 token), las cifras de ahorro son estimaciones "basadas
  en comportamiento típico del agente" (no medidas por sesión real), y **no actualiza el contenido
  automáticamente** — el mantenimiento de los `CLAUDE.md` de subdirectorio es manual. La detección de
  "routing compliance" depende de leer el orden de lectura en el JSONL de sesión — es decir, mide si
  el agente *obedeció* la ruta, no si la ruta era correcta.
- **Qué le falta frente a COSMOS**: cero noción de ciclos u orfandad como error estructural (aquí es
  "stale" en el mejor caso, detectable solo por auditoría manual periódica); cero jerarquía
  multinivel real; cero distinción entre "sólido" (contención) y "agua" (transversal) — todo vive en
  el mismo tipo de fichero `CLAUDE.md`; el medidor de tokens es una aproximación, no una medición.
- **Robable**: el patrón "sección de Routing en el nivel padre, como lista de nombre+línea" es
  exactamente la forma de la regla 4 del `GOAL.md` de COSMOS ("un nivel no describe a sus hijos, los
  nombra"). Vale la pena robar el *formato* de esa sección, no el mecanismo de auditoría (que es
  manual y sin garantías).

### 2.2 `hierarchical-memory-middleware` (danielpodrazka) 🔧

- **URL**: https://github.com/danielpodrazka/hierarchical-memory-middleware
- **Problema que resuelve**: compresión de historial de conversación largo para agentes con
  integración Slack, sobre DuckDB.
- **Mecanismo concreto**: 4 niveles de compresión por **umbral de acumulación de nodos**, no por
  tiempo ni por relevancia: FULL (~10 nodos recientes, contenido completo) → SUMMARY (>10 nodos:
  primera frase/50 palabras + keywords TF-IDF, hasta ~50 nodos) → META (>50: agrupa 20-40 nodos
  SUMMARY con tema+rango temporal, hasta ~200) → ARCHIVE (>200: solo decisiones y resultados
  mayores). Recuperación vía MCP tools: `search_memory`, `expand_node` (recupera el original
  completo desde cualquier nivel comprimido), `get_recent_nodes`.
- **Qué le falta (admitido por el propio proyecto)**: **rompe KV-cache** porque el contexto cambia de
  forma en cada turno a medida que los niveles de compresión se desplazan; el TF-IDF pierde matices
  que solo estaban en el texto completo; la recuperación explícita por tool añade latencia frente a
  "contexto infinito pasivo".
- **Robable**: el patrón de "umbral de acumulación dispara compresión al siguiente nivel" es útil
  como *modelo mental* de por qué el agua (memoria) de COSMOS tiene que evaporarse y precipitar en
  vez de acumularse sin límite — pero el mecanismo en sí (compresión con pérdida vía TF-IDF) es lo
  contrario del enfoque de COSMOS, que prefiere "no cargado" a "cargado y resumido con pérdida". No
  robar el compresor; sí robar la idea de umbral duro por nivel.

### 2.3 Memoir — memoria con control de versiones tipo Git 🔧

- **URL**: https://github.com/zhangfengcdt/memoir · https://www.memoir-ai.dev/
- **Problema que resuelve**: sustituir bases vectoriales opacas por memoria versionada y transparente.
- **Mecanismo concreto**: rutas semánticas jerárquicas en vez de UUIDs (`preferences.coding.style`,
  `api.v2.auth`) con lookup O(log n); operaciones Git-like (branch, commit, merge, rollback) con
  integridad criptográfica; memoria "branch-aware" (cada rama de código tiene su propia memoria).
  Se distribuye como plugin de Claude Code con hooks que siguen el flujo git existente del repo.
- **Qué le falta**: la jerarquía es de *rutas de memoria* (hechos), no de *contexto operativo del
  harness* (skills, reglas, subagentes) — no cubre el problema que COSMOS ataca (organización del
  propio harness, no solo de los hechos aprendidos).
- **Robable**: el concepto de "ruta semántica en vez de UUID/vector" es un argumento fuerte a favor
  de la taxonomía cosmográfica de COSMOS frente a alternativas basadas en RAG/embeddings — confirma
  que rutas jerárquicas con nombre son más auditables que vectores. La idea de memoria "branch-aware"
  es interesante pero no prioritaria para el alcance actual de COSMOS.

### 2.4 Git Context Controller (GCC) — paper + implementaciones 🔧

- **URL**: https://arxiv.org/abs/2508.00031 · implementaciones community en
  https://github.com/swadhinbiswas/contexa y https://github.com/faugustdev/git-context-controller
- **Problema que resuelve**: contexto como flujo de tokens transitorio → memoria persistente y
  navegable, para tareas largas (SWE-bench, investigación abierta).
- **Mecanismo concreto**: cuatro operaciones explícitas — COMMIT (checkpoint de hito), BRANCH
  (exploración aislada de un camino de razonamiento alternativo), MERGE, CONTEXT (recuperación
  jerárquica del historial) — sobre un sistema de ficheros versionado (`.GCC/`, Markdown+YAML).
  Implementaciones independientes en Python/TS/Rust/Go/Zig/Lua/Elixir dicen ser interoperables sobre
  el mismo formato en disco.
- **Resultados citados**: +13% relativo sobre baselines de contexto largo en SWE-Bench Verified,
  >80% de resolución, por encima de 26 sistemas abiertos/comerciales (cifra del paper, no verificada
  de forma independiente aquí).
  **NOTA DE ESCEPTICISMO**: es un paper académico con benchmark propio — tratar la cifra como
  reclamo del autor, no como hecho establecido, hasta ver replicación independiente.
- **Qué le falta**: está pensado para el *historial de una tarea/sesión larga*, no para la
  *organización estática del harness antes de empezar* — es un complemento a COSMOS (memoria de
  ejecución), no un sustituto de la taxonomía de carga.
- **Robable**: el vocabulario de operaciones explícitas (commit/branch/merge) como *verbos* de
  gestión de contexto es útil para diseñar el ciclo de vida de la "Lluvia" (memoria) de COSMOS: qué
  operación mueve un hecho de sesión a memoria consolidada.

### 2.5 Otros proyectos de memoria (revisión rápida, menor profundidad)

- **`agentmemory` (jayzeng)** — almacenamiento markdown local + búsqueda semántica qmd para varios
  agentes (Claude Code, Codex, Cursor). 📝 Descripción de features sin detalle de mecanismo de
  jerarquía verificado en esta pasada; parece más "notas + búsqueda" que taxonomía de niveles.
- **`agent-memory` (legendPerceptor)** — memoria en capas con Qdrant (vectores) + grafo de
  conocimiento. 🔧 pero es *vector-first*: exactamente la alternativa (RAG) contra la que Anthropic
  argumenta explícitamente a favor del filesystem en 1.2. Útil como contraejemplo, no como fuente a
  robar.
- **`claude-memory-compiler` (coleam00)** — hooks que capturan sesiones y un compilador LLM que las
  organiza en "artículos de conocimiento" cruzados, inspirado en la arquitectura de "knowledge base"
  de Karpathy. 🔧 Interesante para la capa de memoria semántica (equivalente a `memory/MEMORY.md` en
  este mismo workspace), no para la jerarquía de carga.

---

## 3. Routers de skills / carga perezosa a nivel de índice

### 3.1 `skill-router` (sorcerai) 🔧

- **URL**: https://github.com/sorcerai/skill-router
- **Problema que resuelve** (citado explícitamente en el propio repo): "el sistema actual de skills
  inyecta TODAS las instaladas (nombre + categoría + descripción) en el system prompt cada turno. Con
  200+ skills instaladas eso son ~10-15K tokens en cada llamada a la API, siempre, se usen o no."
  — este es el mismo problema estructural que ataca COSMOS pero acotado a skills, no a todo el
  harness.
- **Mecanismo concreto**: servidor MCP con 3 tools —`skill_search {query, limit}` (scoring por
  solapamiento de tokens + boost de substring), `skill_load {id}` (carga `SKILL.md` completo + sus
  ficheros hermanos), `skill_reindex` (rescanea). Escanea 3 raíces con precedencia active > plugin >
  vault: `~/.claude/skills/`, `~/.claude/plugins/`, y una carpeta `~/.claude/skill-vault/` para
  skills poco usadas que **el harness deja de listar cada turno pero siguen siendo descubribles**.
  Indexar ~185 skills toma ~25 ms.
- **Qué le falta (explícito, verificado por WebFetch)**: **sin validación de contenido ni metadata**,
  **sin presupuesto/budget enforcement**, **lista plana** — no hay jerarquía más allá de la categoría
  de origen (active/plugin/vault). Riesgo de seguridad señalado: sigue symlinks, así que puede indexar
  ubicaciones no confiables sin avisar.
- **Robable**: es la prueba de que un índice-y-carga-bajo-demanda para skills **ya se ha construido y
  funciona** con 3 tools simples — buen precedente de implementación mínima. El hueco (sin validación,
  sin jerarquía real, sin presupuesto) es exactamente donde COSMOS puede diferenciarse: COSMOS no es
  "otro router de skills", es la taxonomía completa **más** el validador que este proyecto no tiene.

### 3.2 `openskills` (numman-ali) 🔧

- **URL**: https://github.com/numman-ali/openskills
- **Qué es**: "cargador universal de skills para agentes de código" (`npm i -g openskills`) — permite
  usar el mismo formato SKILL.md/frontmatter en distintos runtimes (no solo Claude Code).
- No se profundizó más allá del listado inicial; se marca para revisión futura si COSMOS necesita
  portabilidad multi-runtime (Codex, Cursor, Gemini CLI). Anotado aquí para no perder el hilo, no
  investigado en detalle en esta pasada.

### 3.3 Blog: "Progressive disclosure of agent tools from the perspective of CLI tool style" (claude-code-router) 📝

- **URL**: https://github.com/musistudio/claude-code-router/blob/main/blog/en/progressive-disclosure-of-agent-tools-from-the-perspective-of-cli-tool-style.md
- Encontrado en el listado pero no fetcheado en profundidad — por título y contexto del repo (un
  router de modelos/proveedores para Claude Code) parece ser análisis en prosa sobre cómo estructurar
  tools al estilo CLI (subcomandos con `--help` bajo demanda en vez de flags planos). Marcar como
  📝 pendiente de verificación de mecanismo si se retoma.

---

## 4. Validadores / linters de ficheros de contexto — la pieza que casi nadie tiene

Esta es la sección más importante para COSMOS porque el `GOAL.md` exige un validador que detecte
huérfanos, ciclos y que **se haya visto fallar a propósito**. La mayoría de proyectos de "context
engineering" no tienen nada de esto. Estos dos sí:

### 4.1 `cclint` (felixgeelhaar) 🔧

- **URL**: https://github.com/felixgeelhaar/cclint
- **Qué valida** (lista verificada, no de marketing):
  - Imports `@path` sin resolver y **dependencias circulares con profundidad máxima de 5 saltos**.
  - Frontmatter ausente o mal formado en skills/subagentes.
  - Identificadores de modelo inválidos/deprecados (ej. `claude-3-5-sonnet`).
  - Contenido duplicado entre `CLAUDE.md` padre e hijos en monorepos.
  - Comandos bash peligrosos en bloques de código (`rm -rf /`, `curl | bash`, fork bombs), falta de
    `set -e`/`|| exit 1`.
  - Secretos probables (API keys, bloques PEM, asignaciones de alta entropía).
  - **Tamaño de fichero** (~5KB recomendado), jerarquía de headings, lenguaje vago ("sigue buenas
    prácticas" sin más).
  - JSON válido en `.mcp.json`, `plugin.json`, `settings.json`.
- **Lo que NO hace** (verificado, no supuesto): **no valida presupuesto de tokens** ni **huérfanos
  más allá de resolución de imports** — es decir, detecta un import roto, pero no detecta un
  `CLAUDE.md` de subdirectorio que nadie referencia desde ningún sitio.
- **Invocación**: CLI (`cclint lint`, con salida JSON/SARIF/texto), GitHub Action con SARIF para Code
  Scanning, hooks pre-commit/pre-push, LSP server para diagnóstico en editor, exit code 0/1.
- **Robable — alto valor**: la detección de ciclos con profundidad máxima acotada es exactamente el
  tipo de guardarraíl que el validador de COSMOS necesita para el grafo Galaxia→...→Casa. El patrón
  de salida SARIF + exit code es el contrato correcto para integrarlo en CI sin red (cumple la
  prohibición de "cero red en el camino crítico" del `GOAL.md`, ya que el linteo es local).

### 4.2 `ctxlint` (YawLabs) 🔧 — el más completo encontrado en toda la investigación

- **URL**: https://github.com/YawLabs/ctxlint
- **45 checks documentados**, agrupados en 4 categorías. Los directamente relevantes para COSMOS:
  - **`skill-orphaned`**: exactamente el concepto de "pueblo huérfano" que el `GOAL.md` de COSMOS
    llama error de sistema. Es la prueba de que ya existe un checker equivalente en producción para
    robar el diseño (aunque sea a nivel de skill, no de taxonomía completa).
  - **`skill-trigger-collision`**: detecta descripciones de skills que se solapan tanto que el
    agente no puede decidir cuál disparar — relevante para la regla de COSMOS de que cada nivel se
    *nombra*, no se describe de más (una descripción ambigua rompe el enrutado).
  - **`skill-broken-ref`**, **`skill-dead-tool-restriction`**: referencias rotas dentro de una skill
    y restricciones de tool que ya no aplican.
  - **`tokens` / `tier-tokens`**: mide cuánto contexto consume cada fichero **por sesión real**
    (aggregate token usage across files) — el candidato más cercano a "medidor real, no estimado" de
    los que exige el `GOAL.md`, aunque no queda claro por el fetch si usa un tokenizer real o
    aproximación (pendiente de verificar leyendo el código fuente, no solo el README).
  - **`redundancy` / `contradictions`**: contenido duplicado y directivas contradictorias entre
    ficheros de contexto (ej. "usa Jest" en un fichero vs "usa Vitest" en otro) — esto es justo el
    tipo de error que aparece cuando "agua" (regla transversal) se confunde con "tierra" (regla
    local) en la taxonomía de COSMOS.
  - **`staleness`**: compara fecha de modificación del contexto contra fecha de los commits del
    código que describe, para detectar contexto obsoleto.
  - Categoría **`Sessions`**: `session-memory-index-overflow`, `session-loop-detection` — validación
    sobre el propio historial de sesión, no solo sobre ficheros estáticos.
- **Invocación**: CLI (`npx @yawlabs/ctxlint`), modo `--fix` (autocorrección de rutas), `--strict`
  para CI, `--watch`, servidor MCP (`serve`) para integración con IDE/agente, GitHub Action.
- **Qué le falta**: no tiene noción de *taxonomía cosmográfica con niveles nombrados* — sus checks
  son planos (por tipo de fichero: contexto/MCP/sesión/skill), no organizados por una jerarquía de
  contención estricta con reglas de "qué se ve antes de entrar" como pide COSMOS.
- **Robable — el más importante de todo el informe**: el catálogo de 45 checks es el mejor punto de
  partida conocido para especificar el validador de COSMOS. En concreto, robar el *vocabulario* de
  checks (`orphaned`, `trigger-collision`, `broken-ref`, `redundancy`, `contradictions`, `staleness`)
  y remapearlos sobre la taxonomía cosmográfica de 11 niveles sólidos + 5 de agua, en vez de sobre la
  categoría plana (context/mcp/session/skill) que usa ctxlint.

---

## 5. Medición real del contexto inicial de una sesión

El `GOAL.md` de COSMOS exige "un número real de tokens de contexto inicial, medido, no estimado".
Esto es lo que existe:

### 5.1 `/context` (comando nativo de Claude Code) 🔧

- Desglosa el uso por categoría: system prompt, system tools, tools MCP, ficheros de memoria
  (incluyendo `CLAUDE.md`), agentes personalizados, mensajes, espacio libre y buffer de auto-compact.
  `/context all` expande el detalle por cada tool MCP, cada skill y cada fichero de memoria
  individual con su coste propio.
- **Cifra citada como ejemplo real** (de una fuente secundaria, no oficial): system prompt ~10.700
  tokens + system tools ~28.500 tokens = ~28.789 tokens de coste estructural **antes de escribir
  nada** en un caso concreto reportado. Tratar como ejemplo anecdótico de un usuario, no como cifra
  universal — varía por cuántas tools/MCP tenga cada instalación.
- **Esto es lo más parecido a un medidor "real" que existe hoy**, porque lee el estado real de la
  conversación tal como lo procesa el modelo, no una aproximación de caracteres/4. Es la pieza que
  COSMOS debería usar como *fuente de verdad* para su propio medidor, en vez de reinventar un
  tokenizer — aunque siendo un comando interactivo, hace falta envolverlo o replicar su lógica para
  poder correrlo en CI sin intervención humana (pendiente de investigar si hay una API/flag
  no-interactiva).
- **Contraste importante**: HAM (sección 2.1) usa 4 chars ≈ 1 token como aproximación explícitamente
  admitida como no-real. `/context` es la alternativa correcta y ya la trae el propio Claude Code.

### 5.2 API `count_tokens` de Anthropic 🔧

- Mencionada de pasada en los resultados de búsqueda ("herramientas que miden el context-window
  overhead de servidores MCP usando la count_tokens API de Anthropic o estimación sin clave") — es la
  vía oficial y exacta para contar tokens de un payload dado sin gastar una llamada de generación
  completa. Es la pieza de infraestructura correcta para un medidor CI de COSMOS que sea determinista
  y no dependa de heurísticas de caracteres.
  **Nota de alcance**: usar esta API implica salir a red (llamada HTTP a Anthropic), lo cual choca
  con la prohibición de COSMOS de "cero red en el camino crítico: el validador corre offline". Habría
  que decidir si el medidor es una pieza aparte del validador (con red, opcional) o si se acepta un
  tokenizer local offline (tiktoken/equivalente) con la advertencia de que no es 100% idéntico al
  tokenizer real de Claude.

### 5.3 Herramientas de terceros (revisión superficial, sin mecanismo verificado en profundidad)

- **agentsroom.dev** — "medidor de tokens en vivo" para sesiones de Claude Code con desglose input/
  output/cache. 📝 No se verificó el mecanismo exacto (¿lee `/context`? ¿parsea JSONL de sesión?).
- **Skill "Token Usage Tracker"** (mcpmarket) — describe monitorización de consumo con reportes de
  coste por fichero. 📝 Mismo nivel de verificación, sin profundizar.

---

## 6. El hueco más importante encontrado: la plataforma no soporta nesting real de skills

Este es el hallazgo más accionable de toda la investigación, y confirma directamente la premisa de
COSMOS de que nadie ha resuelto esto:

- **Issue abierto en `anthropics/claude-code`**: #18192 ("Recursive skill discovery — scan
  subdirectories in `~/.claude/skills/`"), abierto el 14 de enero de 2026, **sin respuesta de
  mantenedor ni resolución** en el momento de este fetch. Hay un segundo issue relacionado, #28266,
  sobre el mismo síntoma.
- **El problema exacto, verificado**: Claude Code **solo escanea el nivel superior** de
  `~/.claude/skills/`. Si organizas skills como:
  ```
  ~/.claude/skills/spec-system/spec-creator/SKILL.md   ← NO se descubre
  ~/.claude/skills/spec-system/spec-executor/SKILL.md  ← NO se descubre
  ```
  Llamar a `Skill("spec-creator")` falla con "Unknown skill". Es decir: **el runtime que COSMOS
  targetea no soporta de forma nativa el nivel "Ciudad contiene Pueblo" de la taxonomía cosmográfica**
  para el caso de skills.
- **Workaround actual de la comunidad**: symlinks manuales en el nivel superior apuntando a cada
  skill anidada (`ln -s spec-system/spec-creator spec-creator`), que exige mantenimiento manual y
  "acordarse" de crear el symlink al añadir una skill nueva — es decir, reintroduce exactamente el
  antipatrón que COSMOS prohíbe ("una regla que depende de que alguien se acuerde").
- **Opciones propuestas en el propio issue** (sin implementar): (A) escaneo recursivo con profundidad
  razonable (p.ej. 3 niveles), (B) `skills.scanDepth` configurable, (C) marcador explícito
  `SKILL_SUITE.md` para controlar la recursión.
- **Implicación directa para COSMOS**: la taxonomía cosmográfica de "Ciudad/Pueblo/Casa" **no puede
  apoyarse en que Claude Code descubra la jerarquía sola**. Hacen falta necesariamente una de estas
  dos piezas, y son responsabilidad del propio COSMOS, no de la plataforma:
  1. Un **paso de "compilación"** que genere symlinks (o copias) planas en `~/.claude/skills/` a
     partir del árbol cosmográfico anidado — análogo al workaround de la comunidad, pero automatizado
     y verificado por el validador (para que nunca dependa de que alguien se acuerde).
  2. Un **router propio** (al estilo `skill-router`, sección 3.1) que indexe el árbol completo y
     exponga `cosmos_search`/`cosmos_load` como MCP tools, sin depender del descubrimiento nativo de
     Claude Code en absoluto.
- La opción 2 es más robusta (no depende de que Anthropic resuelva el issue) pero añade una pieza de
  infraestructura corriendo (servidor MCP); la opción 1 es más simple pero frágil si Claude Code
  cambia cómo resuelve symlinks (hay un issue relacionado en `openai/codex` #22275 sobre
  descubrimiento de `SKILL.md` a través de symlinks con comportamiento inconsistente, señal de que
  esto no está estandarizado entre runtimes).

---

## 7. Taxonomías multinivel reales (más allá de "raíz + subdirectorio")

Petición específica del encargo: ¿alguien ya hizo una taxonomía de varios niveles de verdad? Hay
**un** candidato serio:

### 7.1 OpenViking (ByteDance/Volcengine) — el único con 3 niveles reales y filesystem jerárquico 🔧

- **URL**: https://github.com/volcengine/OpenViking
- **Cifras**: reportado con más de 30.000 estrellas y 2.300+ forks (cifra de fuentes secundarias, no
  verificada contra la página del repo directamente en esta pasada — tratar con cautela dado lo
  reciente del proyecto, principios de 2026). Respaldo académico: paper aceptado en VLDB 2026.
- **Problema que resuelve**: unificar memoria de agente, RAG de conocimiento y skills bajo un único
  paradigma, en vez de tener 3 sistemas separados (vector DB para RAG, otro almacén para memoria, un
  tercero para skills).
- **Mecanismo concreto — el más parecido a la taxonomía de COSMOS de todo lo encontrado**:
  - Protocolo virtual `viking://` con directorios reales: `resources/`, `user/{user_id}/`
    (memorias+recursos+skills+conexiones), `memories/preferences/`.
  - El agente navega con `ls`, `tree`, `find` — **contención real de sistema de ficheros**, no una
    base de datos con campos jerárquicos simulados.
  - **Cada entrada** (no solo cada tipo, cada fichero individual) se procesa en 3 niveles al
    escribirse: **L0 (abstract, ~100 tokens, "chequeo rápido de relevancia")**, **L1 (overview, ~2k
    tokens, estructura y puntos clave)**, **L2 (detalle completo, se carga solo si hace falta)**.
  - Recuperación: "localiza primero el directorio con mayor score, luego baja capa a capa" — es
    búsqueda jerárquica descendente, no un ranking plano de todos los ficheros por similitud.
  - "Self-evolving": al terminar una sesión, extrae de forma asíncrona preferencias del usuario y
    experiencia del agente hacia memoria de largo plazo — un mecanismo real de realimentación, no
    solo la promesa de la palabra "self-evolving".
  - Reducción de tokens reclamada: hasta 91% (cifra del proyecto, no verificada de forma
    independiente).
- **Qué le falta (verificado por fetch directo, no supuesto)**: **no se documentó ningún mecanismo de
  validación** de huérfanos, ciclos o consistencia del árbol — el propio proyecto admite estar "en
  etapa temprana, con mucho por construir" sin enumerar límites arquitectónicos concretos. Tampoco
  hay mención de un *validador* en el sentido que pide COSMOS (algo que falle en rojo a propósito).
- **Robable — el más directamente aplicable de toda la investigación**: la idea de **L0/L1/L2 por
  entrada individual** (no solo por tipo de contenido) generaliza mejor que la tabla de 3 niveles de
  Anthropic Skills (que es por *skill completa*, no por *cada fichero dentro de la skill*). Para
  COSMOS: cada nodo de la taxonomía (Sistema Solar, Continente, Ciudad...) podría tener su propio
  L0 (una línea, para el índice del padre), L1 (resumen, para cuando se entra al nivel) y L2
  (contenido completo del nivel, para cuando se baja a un hijo concreto) — eso encaja con la regla 4
  del `GOAL.md` ("cuando entra en contexto" vs "qué se ve de él antes de entrar") de forma casi
  literal.
- **Qué NO robar**: es un sistema *runtime* con protocolo virtual propio y backend propio — mucho más
  pesado que lo que pide el `GOAL.md` de COSMOS (repo clonable, offline, sin dependencias de pago).
  Robar el *modelo mental* (L0/L1/L2 por nodo + navegación descendente por score), no la
  implementación (no traer el protocolo `viking://` ni su backend).

### 7.2 GenericAgent — modelo de 4 capas (índice/hecho/SOP/+1) 📝

- **URL**: https://arxiv.org/pdf/2604.17091 ("GenericAgent: A Token-Efficient Self-Evolving LLM Agent
  via Contextual Information Density Maximization")
- Capas citadas: L1 índice (punteros compactos, mapeo de keywords, restricciones duras, para
  navegación/enrutado rápido), L2 hechos (información factual verificada y estable, validada por
  ejecución), L3 SOP (conocimiento procedimental reusable, workflows). Es un **paper**, no un repo
  usable — se marca 📝 por falta de implementación verificada, aunque el modelo de capas en sí es
  coherente con lo que ya aparece en OpenViking y HAM. No profundizado más allá del abstract/resumen
  de búsqueda.

### 7.3 Conclusión de esta sección

Fuera de OpenViking, **nadie encontrado en esta pasada implementa de verdad más de 2 niveles de
jerarquía de contexto con contención estricta y nombres semánticos por nivel**. La inmensa mayoría de
"context engineering" en GitHub es: (a) un `CLAUDE.md` raíz + reglas con `paths:` (patrón que este
mismo workspace ya usa, ver `CLAUDE.md` del repo), o (b) memoria vectorial con metadata jerárquica
simulada (no contención real). La taxonomía cosmográfica de 11 niveles sólidos + 5 de agua de COSMOS,
con nombres propios y regla dura de "ningún elemento existe fuera de un padre", **no tiene precedente
directo** en lo encontrado — el candidato más cercano (OpenViking) llega a 3 niveles de granularidad
de carga pero con una jerarquía de *directorios de usuario/recurso*, no una taxonomía semántica de
*tipos de nivel* (sistema solar, continente, país...) con reglas de carga distintas por tipo.

---

## 8. Arquitecturas multi-agente relacionadas (contexto, no jerarquía de ficheros)

### 8.1 "Choosing the Right Multi-Agent Architecture" (LangChain) 📝/🔧

- **URL**: https://www.langchain.com/blog/choosing-the-right-multi-agent-architecture
- Cuatro patrones con datos de rendimiento comparados: **Subagentes** (supervisor + subagentes como
  tools, aislamiento de contexto fuerte, subagentes sin estado), **Skills** (un agente carga prompts/
  conocimiento bajo demanda manteniendo el control), **Handoffs** (un tool escribe una variable de
  estado, middleware la lee antes de cada llamada al modelo y cambia system prompt + lista de tools
  — "usó la menor cantidad de texto de prompt con diferencia" porque cada paso carga un prompt
  pequeño y una tool, no todo el dominio), **Router** (enrutado en un paso separado antes de que
  corra cualquier agente, paraleliza).
- **Guía de selección citada**: empezar con Skills o Handoffs para validar un MVP, subir a
  Subagentes/Router solo al chocar con cuellos de botella.
- **Robable**: el hallazgo de que **Handoffs minimiza el texto de prompt "por un margen amplio"**
  porque cada paso carga *un* prompt pequeño y *una* tool en vez de todo el dominio es evidencia a
  favor del principio de COSMOS de que el coste se paga al bajar de nivel, no al entrar — es la misma
  lógica aplicada a nivel de arquitectura de agentes en vez de a nivel de ficheros de contexto.

---

## 9. Papers académicos sobre routing de skills — señal de investigación activa, no herramientas usables

Aparecieron varios papers de 2026 sobre el problema exacto de "elegir qué skill/tool cargar" con
benchmarks propios. Se listan por completitud del rastreo, marcados 📝 porque son investigación, no
proyectos instalables, y no se profundizó en ellos (fuera del alcance práctico de COSMOS ahora mismo,
pero indican que el problema está reconocido como no resuelto en la literatura):

- **SkillCAT** (arxiv 2606.13317) — autoevolución de skills por topología con evaluación contrastiva.
- **Skill-to-LoRA** (arxiv 2606.16769) — en vez de repetir instrucciones de skill en cada turno,
  aprender el comportamiento como adaptador LoRA — enfoque radicalmente distinto (skill como pesos,
  no como texto cargado). Interesante como "qué NO es COSMOS": COSMOS asume que el contexto sigue
  siendo texto/tokens, no pesos entrenados.
- **"Skill Is Not Document"** (arxiv 2606.03565) — benchmark + retriever de dos etapas para el
  problema de que una skill no es un documento cualquiera para recuperación — título que valida
  directamente que el enfoque RAG-plano para skills es reconocido como insuficiente en la literatura,
  reforzando la apuesta de Anthropic (y de COSMOS) por estructura de ficheros en vez de embeddings.
- **SkillPager** (arxiv 2606.00822) — navegación intra-skill por recuperación de nodos semánticos
  adaptativa a la query — el equivalente académico de "Casa" dentro de "Pueblo" con carga bajo
  demanda por relevancia, en vez de por referencia explícita desde SKILL.md.
- **SkillReducer** (arxiv 2603.29919) — optimización de skills para eficiencia de tokens.
- **HMARS** (arxiv 2606.28349) — sistema de memoria jerárquica multi-agente para razonamiento de
  contexto largo.

**Ninguno de estos papers tiene, hasta donde se verificó en esta pasada, una implementación con
validador de estructura (huérfanos/ciclos) ni una taxonomía nombrada de niveles como la de COSMOS.**
Son todos sobre *qué cargar* (retrieval/routing), no sobre *cómo se garantiza que la jerarquía en sí
está bien formada* — que es precisamente el hueco que el `GOAL.md` de COSMOS pone en el centro
("definición de terminado" exige validador con prueba de rojo, no solo buen retrieval).

---

## 10. Proyectos marcados como puro humo o sin mecanismo verificable

Por honestidad del rastreo, estos aparecieron en las búsquedas con lenguaje de "context engineering"
pero **no se pudo verificar mecanismo real** (o el propio fetch confirmó que es solo prosa/WIP):

- **`context-engine` (contextenginehq)** — README describe propiedades deseables (determinista,
  token-aware, versionado) pero **no documenta el algoritmo de scoring, ni si hay jerarquía, ni cómo
  se aplican los presupuestos**; remite a sub-repos (`context-core`, `context-specs`) que no se
  pudieron inspeccionar en esta pasada. Tratar como 📝 hasta ver código.
- **`agent-harness` (Michaelliv)** — "token budget" aparece solo como una entrada en una lista de
  "stop conditions" conceptuales; el propio proyecto se declara "early development / work in
  progress" con "open questions" sin resolver. 📝, no 🔧.
- **`context-engineering-intro` / `hubbardmichael/context-engineering`** — por el resumen de
  búsqueda, son guías de prompting y estructura de repo ("PRPs", plantillas) más que mecanismo de
  carga perezosa forzado por código. No se fetchearon en profundidad porque el patrón (guía en prosa)
  ya se repite en varios resultados similares — descartados de la lista de "robable" salvo que una
  revisión futura encuentre código de validación no visible desde el README.
- **La mayoría de listas "awesome-claude-code-skills"** son catálogos curados, no mecanismo — útiles
  como directorio, cero valor de arquitectura. Se usaron aquí solo para descubrir proyectos concretos
  (p. ej. `skill-router` salió indirectamente de esta vía), no se documentan como fuente propia.
- **Cifra de "29.5K+ estrellas" para `headroomlabs-ai/headroom`**, citada por una de las fuentes
  secundarias: se marca explícitamente como **sospechosa/no verificada** — es una cifra alta para un
  proyecto de compresión de contexto de nicho y reciente; podría ser un error de la fuente
  (confusión con otro repo) o una cifra real pero no confirmada de forma independiente en esta
  pasada. Mecanismo en sí (compresores especializados por tipo de contenido: logs, grep, JSON, código;
  "live-zone compression" para no romper el cache del proveedor) sí suena a mecanismo real y sería
  robable — pero pesar la cifra de adopción con cautela.

---

## Qué robamos

Priorizado por impacto directo sobre las piezas que el `GOAL.md` de COSMOS pide construir (validador,
medidor, taxonomía, reglas de carga):

1. **La tabla de 3 niveles de Anthropic Skills (metadata siempre / cuerpo bajo demanda / recursos a
   coste cero hasta acceder), con sus costes explícitos, es el patrón canónico para "Ciudad/Pueblo/
   Casa".** No hay que inventar nada aquí: replicar la forma exacta, con los mismos límites de
   `name`/`description` (longitud, sin XML) en el esquema de validación de COSMOS.
2. **El catálogo de checks de `ctxlint`** (`skill-orphaned`, `skill-trigger-collision`,
   `skill-broken-ref`, `redundancy`, `contradictions`, `staleness`) como vocabulario base del
   validador — remapeado sobre los 11 niveles sólidos y los 5 de agua de COSMOS en vez de sobre la
   categoría plana que usa ctxlint. Es la pieza más cercana a "un elemento huérfano ni una regla que
   dependa de que alguien se acuerde" del punto 4 del `GOAL.md`.
3. **La detección de ciclos con profundidad máxima acotada de `cclint`** (5 saltos) como guardarraíl
   concreto para el grafo de contención de COSMOS, más su contrato de salida SARIF/exit-code para
   integrarse en CI sin red.
4. **El modelo L0/L1/L2 por nodo individual de OpenViking** (una línea para el índice del padre, un
   resumen para cuando se entra, el contenido completo solo al bajar a un hijo) generaliza mejor que
   una tabla de 3 niveles por *tipo* de contenido — aplicarlo nodo a nodo en toda la taxonomía
   cosmográfica, no solo a las skills.
5. **El patrón "índice completo pero expansión bajo demanda sin romper cache" de la Tool Search Tool
   de Anthropic** (mandar todo pero mostrar solo lo relevante, inyectado al final del contexto) como
   referencia de implementación para cómo un "Sistema Solar" o "Continente" de COSMOS se expande sin
   invalidar el prompt cache de turno en turno.
6. **El rango de 1.000-2.000 tokens para resumen de subagente** (Anthropic, sección 1.4) como
   presupuesto de referencia para la "Luna" de COSMOS.
7. **La sección "Context Routing" de HAM** (lista `→ nombre: ruta`, solo nombre+línea, nunca
   descripción completa) como formato literal para la regla "un nivel no describe a sus hijos, los
   nombra" del `GOAL.md` — ya validado en un proyecto real, aunque ese proyecto no tenga validador.
8. **El workaround de symlinks + la alternativa de router MCP propio** (sección 6) como las dos
   opciones reales para resolver que Claude Code no descubre `SKILL.md` anidados — decisión de diseño
   pendiente que COSMOS tiene que tomar explícitamente, no ignorar.
9. **El vocabulario de operaciones explícitas de Git Context Controller** (commit/branch/merge) como
   verbos para el ciclo de vida de la "Lluvia" (memoria transversal) de COSMOS.
10. La API `count_tokens` de Anthropic y el comando `/context` como las dos fuentes de verdad para
    "medido, no estimado" — con la tensión sin resolver de que `count_tokens` implica red (choca con
    "el validador corre offline" del `GOAL.md`) y `/context` es interactivo (no está claro que tenga
    modo no-interactivo para CI). **Esto queda como pregunta abierta de diseño, no como robo
    resuelto** — ver siguiente sección.

## Qué NO existe — el hueco real que COSMOS llena

1. **Nadie tiene una taxonomía nombrada de más de 2-3 niveles con contención estricta y reglas de
   carga distintas por nivel.** El máximo real encontrado es OpenViking con 3 niveles de
   *granularidad de carga* (L0/L1/L2) sobre una jerarquía de *directorios de usuario/recurso*, no
   sobre una taxonomía semántica de *tipos* de nivel (galaxia/sistema/estrella/planeta/luna/
   continente/país/provincia/ciudad/pueblo/casa) con la distinción explícita sólido-vs-agua que tiene
   COSMOS. Todo lo demás son 2 niveles (raíz + subdirectorio, como HAM) o listas planas (skill-router,
   la mayoría de "awesome-*").
2. **Nadie tiene un validador que cubra a la vez: huérfanos, ciclos y presupuesto superado, sobre una
   jerarquía completa de harness (no solo skills).** `cclint` hace ciclos e imports; `ctxlint` hace
   huérfanos y colisiones de skills y presupuesto por fichero; ninguno de los dos cubre los tres a la
   vez sobre una taxonomía con más de 2 niveles con tipos nombrados. Y ninguno de los dos exige, como
   sí exige el `GOAL.md` de COSMOS, que el validador **se haya visto fallar a propósito** antes de
   aceptarse como terminado — esa disciplina de "prueba de rojo" no aparece en ningún proyecto de
   contexto encontrado (sí es común en testing de software normal, pero no se aplica hoy a linters de
   ficheros de contexto de agentes).
3. **Nadie separa explícitamente "contención" de "alcance transversal"** como hace COSMOS con
   sólido/agua. Todos los sistemas revisados (HAM, ctxlint, cclint, OpenViking) tratan toda regla o
   memoria como del mismo tipo — no hay la distinción de COSMOS entre "esto contiene a otra cosa" y
   "esto moja a varias cosas sin contenerlas", que es justo lo que evita el antipatrón medido en este
   mismo workspace de que una regla local termine en el prólogo global de 30k tokens (ver
   `CLAUDE.md` de este repo, sección "Gasto").
4. **Nadie mide el contexto inicial de forma real, reproducible y offline, con desglose por nivel de
   una taxonomía nombrada.** `/context` es real pero interactivo y específico de Claude Code;
   `count_tokens` es real pero requiere red; todos los "medidores" de terceros revisados (HAM,
   agentsroom, el skill de mcpmarket) usan aproximación de caracteres o no documentan el método. El
   `GOAL.md` de COSMOS exige exactamente esto y hoy no existe una pieza que lo resuelva de fábrica —
   es trabajo de implementación real para COSMOS (probablemente: tokenizer local tipo tiktoken como
   aproximación offline verificada contra `/context` como ground truth ocasional, documentando el
   margen de error entre ambos en vez de fingir exactitud).
5. **Nadie resuelve el hueco de la plataforma** (sección 6: Claude Code no descubre `SKILL.md`
   anidados) **con una capa que además se valide a sí misma.** El workaround de symlinks que usa la
   comunidad es manual y no auditado; COSMOS puede ser el primer proyecto que compile automáticamente
   la taxonomía cosmográfica anidada a la vista plana que la plataforma necesita, **y** verifique con
   su propio validador que esa compilación no dejó nada huérfano ni rompió el mapeo — cerrando
   exactamente el ciclo que hoy depende de "acordarse".

**Resumen de una línea**: existe de sobra "cárgalo bajo demanda" (Anthropic Skills, Tool Search,
OpenViking) y existe por separado "líntalo" (cclint, ctxlint) — lo que no existe es la combinación de
una **taxonomía multinivel con nombre propio por tipo de nivel**, un **validador que cubra huérfanos +
ciclos + presupuesto sobre esa taxonomía completa y se demuestre a sí mismo fallando**, y un
**medidor real y offline** atados a la misma especificación. Ese es exactamente el hueco que ocupa
COSMOS.
