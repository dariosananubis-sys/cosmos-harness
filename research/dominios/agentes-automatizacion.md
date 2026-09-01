# Agentes y Automatización — el meta-nivel

Barrido GitHub para COSMOS. Dominio: orquestación multi-agente, ingeniería de contexto, memoria de
agentes, servidores MCP, automatización de navegador, flujos de trabajo automatizados, agentes que
corren solos (cron/colas/daemons), evaluación/observabilidad de agentes, y modelos locales. Es el
dominio meta: no produce un entregable de cliente, hace que el resto de dominios rinda más.

**Método**: cupo de WebSearch de la sesión agotado (compartido entre agentes activos en paralelo).
Todo este barrido es API de GitHub autenticada (`search/repositories` + `repos/{owner}/{repo}`) más
`raw.githubusercontent.com` para README en vivo. El endpoint `search` tiene un límite de 30/min que
aquí se compartía con otros barridos hermanos corriendo a la vez (los ficheros `ia-ml-aplicada.md`,
`infraestructura-devops.md`, `producto-saas.md`, `seo-contenido.md`, `web-ecommerce.md` ya
presentes en este directorio son evidencia de eso): varias tandas de consultas devolvieron 403 "API
rate limit exceeded" pese a que `/rate_limit` marcaba cupo libre, y se resolvió espaciando las
consultas ~10-13s. El límite `core` (5000/h) no se vio afectado — se usó para verificar
estrellas/licencia/`archived`/`pushed_at` de los finalistas y para contar herramientas reales de
cada MCP vía su README. Fecha del barrido: 2026-09-01. Todo lo que lleva cifra fue confirmado en
vivo en esa fecha; lo que no, va marcado `NO VERIFICADO`.

---

## De primera

Máximo 10. Ganan por: resuelven infraestructura real (no son una capa fina sobre una llamada a
modelo), coste de contexto conocido y razonable, cero coste de dinero, y actividad viva confirmada
(`pushed_at` reciente, no archivado).

1. **[openclaw/openclaw](https://github.com/openclaw/openclaw)** — 388k★, MIT-ish (`LICENSE` sin
   SPDX detectado por GitHub, licencia visible en el repo), `pushed_at` de hoy mismo, sin archivar.
   **Por qué gana**: no es un hallazgo teórico — es el upstream real del canal `ClaudeClaw` que este
   mismo arnés ya opera (`.claude/claudeclaw/`, skills `claudeclaw:jobs`, `claudeclaw:telegram`,
   `claudeclaw:discord`, heartbeat/daemon). El README lo confirma línea por línea: "Gateway
   confiable, ejecución no confiable, política determinista" — un gateway único que conecta modelos,
   herramientas y canales de mensajería (Telegram/Discord/CLI), corriendo como daemon personal o
   como despliegue de equipo con la misma configuración. Instalador propio (`curl | bash`, sin
   Docker obligatorio), Node ≥22.22.3. Mecanismo: proceso `gateway` de larga duración + política de
   permisos separada de la ejecución de herramientas. Veredicto: **ya en producción aquí bajo otro
   nombre** — el ROI de mirar el upstream es ver qué features nuevas (`openclaw onboard
   --install-daemon`, teams) todavía no se han adoptado en `ClaudeClaw`.

2. **[anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python)**
   (+ [-typescript](https://github.com/anthropics/claude-agent-sdk-typescript) 1.7k★, +
   [-demos](https://github.com/anthropics/claude-agent-sdk-demos) 2.7k★) — 8.0k★, oficial de
   Anthropic, activo. **Por qué gana**: es el SDK con el que se construye un harness de agentes
   propio sin reimplementar el bucle tool-use/streaming/sesiones/permisos a mano — exactamente el
   problema que resuelve COSMOS. Al ser oficial, sigue el mismo modelo mental que Claude Code (tools,
   hooks, subagentes) en vez de uno propio que hay que traducir.

3. **[anthropics/skills](https://github.com/anthropics/skills)** — 173k★, oficial, activo semanal.
   **Por qué gana**: es el repo fuente del formato `SKILL.md` + frontmatter que ya usa el catálogo de
   skills de este arnés (incluida la lista inyectada en cada sesión). Referencia directa para diseñar
   skills propias con el contrato correcto en vez de improvisar el formato.

4. **[vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser)** — 41.7k★,
   Apache-2.0, `pushed_at` de hoy. **Por qué gana**: prueba viva y no teórica de que un CLI ligero
   gana a un MCP de navegador para este caso de uso — es literalmente la skill `agent-browser` que
   este arnés ya usa a diario (`.claude/skills/agent-browser/SKILL.md`, CDP nativo). Coste de
   contexto: **cero tools permanentes** — se invoca por Bash, no vive cargado como definición de MCP
   en cada sesión. Confirma la regla ya escrita en `CLAUDE.md`/reglas del usuario de preferir
   `agent-browser` sobre `claude-in-chrome` y sobre MCP de Playwright.

5. **[thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)** — 92.8k★, Apache-2.0,
   activo diario. **Por qué gana**: "Persistent memory compression system built for Claude Code" —
   resuelve exactamente el problema que este arnés ya resuelve a mano con `memory/` +
   `notes/daily/` + hooks de `PreCompact`, pero empaquetado como herramienta reutilizable basada en
   hooks (no un MCP, no tools permanentes; captura vía hooks del propio Claude Code y comprime a
   SQLite/embeddings). Útil como referencia de diseño aunque el propio arnés ya tenga su variante
   (memoria semántica en `memory/MEMORY.md`).

6. **[mem0ai/mem0](https://github.com/mem0ai/mem0)** — 64.5k★, Apache-2.0, activo diario. **Por qué
   gana**: capa de memoria genérica para agentes, no atada a Claude Code — relevante si COSMOS
   necesita memoria compartida entre runtimes/modelos distintos (no solo sesiones de Claude). Se
   autoaloja (SQLite/Postgres/vector store local), sin API de pago obligatoria.

7. **[mlflow/mlflow](https://github.com/mlflow/mlflow)** — 27.8k★, Apache-2.0, activo hoy. **Por qué
   gana**: es el evaluador/observability de facto para agentes y LLM ya con tracing nativo de
   agentes (`agentops`, `llm-evaluation` en sus topics oficiales), autoalojado, sin coste de API. Para
   el punto del encargo "evaluación y observabilidad de agentes" es la pieza más madura y menos
   propietaria (frente a alternativas SaaS de pago del mismo espacio).

8. **[punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)** — 93.6k★,
   MIT, activo hoy, **3.482 entradas enlazadas** (contadas en vivo en su README). **Por qué gana**:
   no es una herramienta que se instala, es el índice — coste de contexto **cero** porque nunca se
   carga como servidor MCP, solo se consulta como página cuando hace falta un MCP concreto. Evita
   descubrir servidores MCP a ciegas por WebSearch.

9. **[letta-ai/letta](https://github.com/letta-ai/letta)** — 24.5k★, Apache-2.0, activo esta semana.
   **Por qué gana**: la plataforma de referencia para "agentes con estado" (memoria editable como
   parte del propio contexto del agente, no un adjunto externo) — arquitectura a estudiar para
   decidir cómo COSMOS trata memoria a largo plazo, aunque no se adopte el proyecto entero.

10. **[microsoft/agent-framework](https://github.com/microsoft/agent-framework)** — 13.3k★, activo
    hoy. **Por qué gana**: framework oficial de Microsoft (sucesor declarado de AutoGen + Semantic
    Kernel) para construir y orquestar agentes y flujos multi-agente con soporte de checkpointing y
    human-in-the-loop — referencia de arquitectura de un actor grande, útil para contrastar
    decisiones de diseño de COSMOS aunque el stack real de este workspace sea Claude-only.

---

## Segunda fila

- **[github/github-mcp-server](https://github.com/github/github-mcp-server)** — 32.6k★, oficial,
  activo hoy. Expone **91 tools** distintas contadas en vivo en su README (`actions_get`,
  `actions_list`, gestión de Issues/PRs/Actions/repos…). Con ese tamaño, cargarlo entero es la fuga
  de contexto por excelencia que advierte el filtro del encargo. Soporta `--toolsets` para reducir
  el subconjunto cargado, pero para uso ocasional el `gh` CLI (que este mismo arnés ya usa para todo
  lo de GitHub) da el mismo resultado con coste de contexto cero.
- **[microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp)** — 36.7k★, oficial,
  activo hoy. Expone **71 tools** contadas en vivo (`browser_click`, `browser_console_messages`…).
  Ya está cargado en este mismo entorno (`mcp__plugin_playwright_playwright__*`) pero las reglas
  propias del usuario ya lo tratan como *fallback* de `agent-browser`, no como opción por defecto —
  el hallazgo en vivo (71 tools permanentes) es la justificación numérica de por qué esa regla existe.
- **[langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)** — 40.8k★, activo hoy.
  Framework de grafos de estado para agentes "resilientes". Referencia de industria, pero asume
  integraciones LangChain y normalmente API de pago por token — no encaja directo en un stack
  Claude-only sin capa de traducción.
- **[crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)** — 57.9k★, activo hoy. Orquestación de
  agentes con roles ("crew"). Mismo comentario que LangGraph: capa fina de abstracción sobre
  llamadas a modelo, útil como vocabulario pero no como pieza a instalar aquí.
- **[microsoft/autogen](https://github.com/microsoft/autogen)** — 60.7k★, pero `pushed_at`
  2026-04-15 (**5 meses sin commits** frente a los otros candidatos, todos con actividad de hoy) —
  el propio Microsoft parece haber movido el foco a `agent-framework` (#10 de arriba), que sí está
  vivo a diario. Tratarlo como legado.
- **[n8n-io/n8n](https://github.com/n8n-io/n8n)** — 203k★, activo hoy, self-hosted, con MCP
  cliente/servidor nativo (topics `mcp-client`, `mcp-server`). El workflow-automation self-hosted
  más grande y con más plantillas (`enescingoz/awesome-n8n-templates`, 25k★, 280+ plantillas). Exige
  su propio servidor/proceso — no encaja en un harness local puro, pero es la pieza a considerar si
  COSMOS necesita automatizaciones no-agénticas (webhooks, ETL simple) fuera del canal de agentes.
- **[buildermethods/agent-os](https://github.com/buildermethods/agent-os)** — 5.4k★, activo esta
  semana. Sistema de especificación dirigida por agente (inyecta estándares del propio código en los
  specs). Comparable en propósito al propio `harness-sdd.md`/`feature_list.json` de este arnés —
  vale como contraste de diseño, no como reemplazo.
- **[humanlayer/12-factor-agents](https://github.com/humanlayer/12-factor-agents)** — 25.6k★, pero
  `pushed_at` 2025-09-21 (**~1 año sin commits**). No pasa el filtro "vivo" como proyecto, pero como
  documento de principios de arquitectura (el equivalente a "the twelve-factor app" para agentes LLM)
  sigue siendo la referencia más citada del espacio — se incluye con esa salvedad explícita.
- **[Mintplex-Labs/anything-llm](https://github.com/Mintplex-Labs/anything-llm)** — 65.5k★, activo
  hoy. Workspace local-first con agentes, RAG y multi-modelo (incluye Ollama). Candidato fuerte para
  la parte "modelos locales" del encargo si se quiere UI, no solo CLI.
- **[Fosowl/agenticSeek](https://github.com/Fosowl/agenticSeek)** — 27.1k★, activo hace 3 semanas.
  "Fully Local Manus AI. No APIs, No $200 monthly bills" — agente autónomo 100% local (browsing,
  código, planificación) sin ninguna API de pago. Encaja directo con la regla dura de este workspace
  de cero gasto por API.
- **[browser-use/browser-use](https://github.com/browser-use/browser-use)** — 112k★, activo hoy.
  El framework de automatización de navegador más popular del ecosistema (por delante incluso de
  `agent-browser` en estrellas). No sustituye a `agent-browser`/BrowserClaw ya en uso aquí, pero es
  la referencia obligada si algún día hace falta comparar mecanismos.

---

## Humo

Match de la consulta, sin verificación de mecanismo más allá del README/topics — nombrados por si
hacen falta más adelante, no evaluados a fondo:

- **hesreallyhim/awesome-claude-code** (53k★) — índice de recursos Claude Code, alternativa a
  `awesome-mcp-servers` pero para el ecosistema Claude entero.
- **VoltAgent/awesome-openclaw-skills** (52k★) — "5.400+ skills filtradas" del marketplace oficial
  de OpenClaw — catálogo, no herramienta.
- **davepoon/buildwithclaude** (3.4k★) — hub de skills/agentes/comandos/plugins de Claude.
- **wshobson/agents** (39.3k★) — marketplace multi-harness (Claude Code, Codex, Cursor…) de agentes
  y plugins.
- **googleapis/mcp-toolbox** (16.3k★) — MCP oficial de Google para bases de datos; relevante solo si
  COSMOS acaba tocando una BD que no sea SQLite local.
- **GLips/Figma-Context-MCP** (15.7k★) — MCP de Figma→código; nicho de diseño, no aplica hoy.
- **casdoor/casdoor** (14.3k★) — gateway de identidad/IAM con capa MCP; interesante solo si COSMOS
  necesita auth multiusuario.
- **deepset-ai/haystack** (26.4k★) — framework de orquestación LLM más orientado a RAG que a agentes.
- **letta-ai** ecosistema — `memvid/memvid` (16.5k★), `MemTensor/MemOS` (11.1k★),
  `MemoriLabs/Memori` (16.3k★) — más capas de memoria de agentes, redundantes entre sí; elegir una
  sola si hace falta, no las tres.
- **khoj-ai/khoj** (36.9k★) — "segundo cerebro" autoalojable con agentes propios; solapa con
  `notes/` (Obsidian) de este workspace.
- **langwatch/langwatch** (3.5k★), **lmnr-ai/lmnr** (3.2k★), **openlit/openlit** (2.7k★) —
  observabilidad de agentes más pequeña/joven que MLflow; vigilar si MLflow se queda corto en algo.
- **gptme/gptme** (4.4k★) — agente de terminal minimalista, todo local — buen ejemplo de "cuánto
  hace falta de verdad" antes de sumar dependencias.
- **VRSEN/agency-swarm** (4.5k★), **kyegomez/swarms** (7.1k★) — más frameworks de orquestación
  multi-agente de terceros, mismo comentario que LangGraph/CrewAI.
- **SolaceLabs/solace-agent-mesh** (5.0k★) — orquestación multi-agente basada en eventos; nicho
  enterprise.

---

## Mapeo a COSMOS

```
sistema-solar   Software / Ingeniería
└─ planeta      Ingeniería y Producto
   └─ continente   Operaciones y Plataforma
      └─ país          AGENTES Y AUTOMATIZACIÓN   ← este dominio
         ├─ provincia   Runtime y orquestación de agentes
         │   ├─ ciudad   Gateway/daemon personal   → pueblo: openclaw (= upstream de ClaudeClaw)
         │   ├─ ciudad   SDK oficial                → pueblos: claude-agent-sdk-python/-typescript
         │   └─ ciudad   Frameworks de terceros      → pueblos: LangGraph, CrewAI, agent-framework
         │                                             (AutoGen: legado, sin commits desde abril)
         ├─ provincia   Memoria y contexto de agentes
         │   ├─ ciudad   Memoria de sesión (Claude Code) → pueblo: claude-mem
         │   └─ ciudad   Memoria genérica multi-runtime   → pueblos: mem0, letta, MemOS, Memori
         ├─ provincia   Servidores MCP
         │   ├─ ciudad   Índice/catálogo           → pueblo: awesome-mcp-servers (se consulta, no se instala)
         │   └─ ciudad   Servidores concretos       → pueblos: github-mcp-server (91 tools),
         │                                             playwright-mcp (71 tools), mcp-toolbox, Figma-Context-MCP
         ├─ provincia   Automatización de navegador
         │   └─ ciudad   CLI ligero vs MCP pesado    → pueblos: agent-browser (en uso), browser-use,
         │                                             BrowserClaw (propio de este arnés)
         ├─ provincia   Flujos de trabajo automatizados (self-hosted)
         │   └─ ciudad   No-code/low-code con IA     → pueblos: n8n, dify, activepieces
         ├─ provincia   Evaluación y observabilidad de agentes
         │   └─ ciudad   Tracing/eval autoalojado    → pueblos: mlflow, langwatch, openlit
         ├─ provincia   Skills y catálogos
         │   └─ ciudad   Formato y marketplace       → pueblos: anthropics/skills, awesome-claude-code
         └─ provincia   Modelos locales para agentes
             └─ ciudad   Agente 100% local, cero API  → pueblos: agenticSeek, anything-llm

mar (regla transversal, no país):
  "coste de contexto por MCP" — todo servidor MCP que se cargue permanentemente cobra sus tools en
  cada sesión, use las o no (91 en github-mcp-server, 71 en playwright-mcp, medido en vivo). Esta
  regla atraviesa toda la provincia de Servidores MCP y también a Automatización de navegador — no
  contiene nada por sí sola, así que no es un pueblo, es agua.
```

**Frontera con países vecinos**: `infraestructura-devops.md` ya señala esta ausencia — "lo que hace
correr y sobrevivir servicios propios" (contenedores, backups, TLS, DNS) vive allí; este país cubre
el runtime/orquestación de los agentes en sí. Comparten mecanismo de sandboxing (contenedores) con
E2B/microsandbox, que siguen viviendo en el país vecino. Con `ia-ml-aplicada.md` la frontera es:
construir/servir/afinar el modelo va allí (llama.cpp, RAG, fine-tuning); orquestar lo que el modelo
hace una vez servido va aquí.

## Lo que falta

- **Cero instalación real.** Todo el barrido es lectura de API pública + README; nada de esto se
  instaló, desplegó ni se probó en ejecución. Las cifras de "N tools" de `github-mcp-server` y
  `playwright-mcp` se contaron por grep de patrón sobre el README (`- **nombre** - descripción`), no
  conectando el servidor real — coherente con el resto de cifras del documento pero conviene
  reverificar si algún día se decide instalar uno de los dos.
- **AGENTS.md (estándar de convenciones para agentes de código)**: la consulta específica no se pudo
  ejecutar por el rate-limit compartido de `search` (30/min repartido entre barridos hermanos en
  paralelo) y no se reintentó por no ser crítica para el resto del informe. Pendiente si hace falta
  comparar el propio `AGENTS.md`/`CLAUDE.md` de COSMOS contra el estándar de facto.
- **Computer-use (control de escritorio, no solo navegador)**: la única consulta que se pudo lanzar
  devolvió candidatos pequeños (<700★, la mayoría experimentales o sin commits recientes) — no se
  encontró un "de primera" real en este subsegmento; puede que en 2026 siga sin haber un ganador
  claro fuera de las herramientas nativas de Anthropic/OpenAI, o puede que falte una segunda ronda de
  búsqueda dedicada.
- **Colas/cron como mecanismo aislado** (fuera del gateway de OpenClaw): no se buscó explícitamente
  "task queue for LLM agents" como categoría propia — quedó cubierto solo indirectamente por
  `n8n`/`openclaw`. Si COSMOS necesita colas de trabajos LLM sin gateway completo, falta esa ronda.
- **Todas las cifras de estrellas de este documento** son del barrido GitHub del 2026-09-01 y pueden
  estar infladas por dinámicas de la plataforma en este año (varios repos superan las 100-300k
  estrellas, mucho más alto que lo que sería normal en ciclos de hype anteriores) — se toman tal cual
  las devuelve la API porque es la única fuente en vivo disponible, no se puede descartar star-fraud
  sin herramienta dedicada de auditoría de estrellas.
