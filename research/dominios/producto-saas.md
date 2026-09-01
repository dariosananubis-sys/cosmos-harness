# Dominio: Ingeniería de Producto SaaS

Barrido de GitHub para poblar COSMOS. Dominio asignado: construir y vender productos SaaS —
backend, frontend, autenticación, pagos y suscripciones, multi-tenancy, APIs, bases de datos,
despliegue e infraestructura, observabilidad, migraciones, rendimiento.

Fecha del barrido: 2026-09-01. Estrellas y fechas de actividad verificadas vía GitHub API/WebFetch
en esa fecha — GitHub las mueve a diario, tratar como aproximación fresca, no como constante.

---

## De primera

Lo que instalaría hoy. Seis recursos, no diez — el resto de lo mirado o era redundante con estos
o no pasaba el filtro de mecanismo.

### 1. [wshobson/agents](https://github.com/wshobson/agents) — plugin marketplace multi-harness

~39.300 ★ · actividad: commits el 2026-08-31 (ayer respecto al barrido) · MIT (autor único: Seth
Hobson / major7apps, ver nota de riesgo abajo).

Qué es: un marketplace de plugins para Claude Code (y adaptado nativamente a Codex CLI, Cursor,
OpenCode, Antigravity y Copilot desde una única fuente Markdown). **93 plugins, 202 agentes, 181
skills, 105 comandos.** Cubre el dominio casi entero: `backend-development` (API design REST/GraphQL,
Clean/Hexagonal/DDD, microservicios, CQRS/event sourcing/sagas), `database-design` +
`database-migrations` (schema, migraciones zero-downtime), `payment-processing` (Stripe, PayPal,
PCI DSS, billing automation), `backend-api-security`, `cloud-infrastructure` (Terraform multi-cloud,
service mesh), `kubernetes-operations`, `observability-monitoring` (Prometheus, Grafana, tracing,
SLO), `application-performance`, `database-cloud-optimization`, `cicd-automation`,
`developer-essentials` (SQL tuning, auth JWT/OAuth2/RBAC, code review), `before-you-build` (riesgo
de producto/monetización antes de construir), `startup-metrics-framework`.

Mecanismo: cada skill es un `SKILL.md` con frontmatter + contenido específico y verificable —
ejemplos de código reales (no "usa buenas prácticas" genérico), y **progressive disclosure**:
`SKILL.md` corto + `references/details.md` que solo se carga si hace falta (comprobado en
`auth-implementation-patterns` y `before-you-build`). Los plugins llevan además `agents/` (personas
con restricción de tools) y `commands/`. Trae su propio evaluador ejecutable,
[`plugin-eval`](https://github.com/wshobson/agents/tree/main/plugins/plugin-eval): análisis estático
+ juez LLM + Monte Carlo (50-100 runs) para certificar calidad de un plugin/skill —
`uv run plugin-eval score path/to/skill`. Instalación: `/plugin marketplace add wshobson/agents` +
`/plugin install <nombre>`.

Coste: cero (solo consume cuota de Claude ya pagada).

Nota de calidad: mantenido por una sola persona con proceso de contribución abierto — el riesgo de
bus-factor es real, pero la cobertura, el ritmo de commits y el evaluador ejecutable lo dejan muy
por delante de cualquier alternativa vista. Es el ganador claro del barrido: instala directamente
`backend-development`, `payment-processing`, `database-migrations` y `developer-essentials` primero.

### 2. [anthropics/skills](https://github.com/anthropics/skills) — repositorio oficial de Agent Skills

~172.900 ★ · actividad: 2026-08-21 · repo oficial de Anthropic.

Qué es: el catálogo oficial que Anthropic usa internamente. Para este dominio importan tres:
- **`webapp-testing`** — mecanismo real, no prosa: trae `scripts/with_server.py`, un script Python
  ejecutable que gestiona el ciclo de vida de uno o varios servidores (backend+frontend) mientras
  Claude escribe y corre Playwright contra ellos. Árbol de decisión explícito HTML estático vs.
  webapp dinámica.
- **`mcp-builder`** — guía de 4 fases para construir servidores MCP (la forma estándar de exponer
  una API/servicio a un agente) en Python (FastMCP) o TypeScript, con checklist de diseño de tools,
  naming, manejo de errores accionables y referencia a la spec MCP.
- **`frontend-design`** — la skill que usa el propio Anthropic para Claude.ai; evita el "esto lo hizo
  una IA" por defecto. Ya en producción en el propio workspace de Darío como
  `anthropic-frontend-design`, lo que corrobora la calidad de forma independiente.

Coste: cero. Vivo y con el mayor número de estrellas del barrido — es la referencia de facto del
formato Agent Skill (el `spec/` del repo es la especificación que todos los demás siguen).

### 3. [stripe/agent-toolkit](https://github.com/stripe/agent-toolkit) ("Stripe AI") — pagos, oficial

~1.800 ★ · MIT · mantenido activamente por Stripe.

Qué es: el kit oficial de Stripe para construir productos de IA sobre su plataforma. Incluye
`@stripe/agent-toolkit` (Python y TypeScript, function-calling para LangChain/CrewAI/OpenAI Agent
SDK/Vercel AI SDK), `@stripe/ai-sdk`, `@stripe/token-meter` (metering de consumo LLM nativo), un
**servidor MCP remoto** en `https://mcp.stripe.com` (OAuth) y **Agent Skills empaquetadas
específicamente para Claude Code, Codex, Cursor y el estándar Agent Plugins**.

Por qué gana a cualquier skill de Stripe de terceros (incluida la de `wshobson/agents`): es la
fuente autoritativa — se actualiza cuando Stripe cambia su API, no cuando un tercero se acuerda de
tocar el repo. Úsalo como fuente primaria; la skill `stripe-integration` de wshobson sirve de
resumen rápido cuando no hace falta la precisión total.

Coste: cero para instalar el toolkit. Usar Stripe en producción cuesta comisión por transacción,
pero eso es inherente al negocio de cobrar pagos, no un coste que imponga la herramienta.

### 4. [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) — marketplace oficial de flujo de desarrollo

~35.800 ★ · repo oficial de Anthropic.

Qué es: el marketplace curado por el propio equipo de Claude Code. Para este dominio:
`mcp-server-dev` (construir servidores MCP, complementa a `mcp-builder`), `agent-sdk-dev`
(construir agentes con el Claude Agent SDK — relevante si el SaaS integra IA), `feature-dev`
(flujo de feature end-to-end), `code-review`, `security-guidance`, `plugin-dev`. También trae LSPs
por lenguaje (`typescript-lsp`, `pyright-lsp`, `rust-analyzer-lsp`, etc.) que dan al agente
comprensión de tipos real vía Language Server Protocol — mecanismo genuino, no prosa.

Coste: cero. Más pequeño que wshobson/agents pero con el sello oficial y sin el riesgo de
mantenedor único.

### 5. Context7 MCP (`mcp__context7__*`, ya activo en este harness) — documentación viva de librerías

Qué es: no es una skill sino un MCP que resuelve documentación actualizada de cualquier
framework/librería/API en el momento de la consulta, en vez de que el modelo recite lo que
memorizó en el entrenamiento (que en un dominio que cambia tan rápido como APIs de pago,
frameworks JS o clientes de Postgres, se queda obsoleto en meses). Ya está en el `CLAUDE.md` de
este workspace como paso obligatorio antes de justificar una decisión con documentación
(`search-first.md`, `citar-fuentes.md`).

Mecanismo: consulta activa, no memoria estática — es exactamente el tipo de "conocimiento
verificable que un modelo no tiene de memoria" que pide el filtro.

Coste: cero en el tier gratuito (limitado sin API key; con API key gratuita de Upstash, más alto).
Cero tarjeta.

### 6. [getlago/lago](https://github.com/getlago/lago) — metering y facturación por uso, autoalojable

~10.500 ★ · AGPLv3 · self-hosted con Docker Compose.

No es una skill de Claude — es la pieza de infraestructura que faltaba en el resto del barrido.
Ningún recurso de arriba cubre bien "facturación por uso" (usage-based billing, algo cada vez más
común en SaaS con IA integrada): Lago procesa eventos de uso en métricas facturables, aplica
precios/créditos, gestiona entitlements y genera facturas — todo autoalojado y gratis en su edición
open source (AGPLv3; Lago Cloud/Premium son de pago, no hace falta tocarlos). Se instala aparte del
agente; el valor para COSMOS es que un agente "especialista en producto SaaS" debería saber que
Lago existe como alternativa gratuita a Stripe Billing/Chargebee cuando el modelo de precios es por
consumo, no solo por asiento.

---

## Segunda fila

Útil pero no urgente — o porque solapa con algo de primera, o porque el mecanismo es más débil.

- **[VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)**
  (~24.800 ★, actividad 2026-08-12) — 100+ subagentes especializados por categoría (core-dev,
  infra, calidad, DX). Mecanismo: personas en Markdown con restricción de tools, sin el
  progressive-disclosure ni el evaluador ejecutable de wshobson/agents. Instálalo solo si prefieres
  el formato "un fichero = un agente" sin el aparato de plugins; si no, wshobson/agents ya cubre
  más terreno con mejor mecanismo.
- **[hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)**
  (~53.300 ★, actividad 2026-09-01, el mismo día del barrido) — no es una skill, es el índice
  maestro del ecosistema Claude Code (skills, agentes, plugins, status lines, tooling). Sirve como
  radar para volver a barrer el dominio dentro de unos meses, no para instalar hoy.
- **[ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)**
  (~74.200 ★, actividad reciente) — mezcla lista curada con carpetas de skills reales (Stripe,
  Square, Shopify, Supabase, Postgres read-only, AWS CDK). El pero: es el escaparate del propio
  producto de Composio — buena parte de las 1000+ integraciones pasan por su **MCP Gateway
  alojado**, una cuenta de terceros de la que este barrido no verificó el tier gratuito con
  garantía. Útil como catálogo de ideas; antes de instalar nada de aquí, confirmar que la skill
  concreta no obliga a darse de alta en Composio.
- **[lanemc/multi-tenant-saas-toolkit](https://github.com/lanemc/multi-tenant-saas-toolkit)**
  (16 ★, último commit 2025-06-19 — más de un año parado a fecha del barrido) — librería npm real
  (no solo prompts): aislamiento de tenant vía AsyncLocalStorage, adaptadores Prisma/Sequelize/
  Mongoose con filtrado automático por tenant, RBAC/ABAC. Código genuino y específico, pero tracción
  y mantenimiento demasiado bajos para fiarse en producción sin auditarlo entero primero.

---

## Humo

- **mcpmarket.com, claudemarketplaces.com, claudedirectory.org, agensi.io, aiskillhome.com,
  summone.co.uk, theskills.directory, agenticskills.io, mcsaguru.com** y sitios similares —
  granjas de páginas SEO, una por cada consulta tipo "claude code skill X". `mcpmarket.com` en
  concreto está detrás de un checkpoint de bot de Vercel que impidió verificar si detrás hay algo
  descargable; el resto no enlaza a un repo de origen verificable en los resultados de búsqueda.
  Tratar cualquier "skill" solo vista en uno de estos dominios como no confirmada hasta encontrar
  su repo real.
- **PatrickJS/awesome-cursorrules** (~40.700 ★) — confirmado por WebFetch: contenido
  mayoritariamente prosa/guía de estilo en ficheros `.mdc`, sin scripts ni validadores. Además la
  convención `.cursorrules`/`.cursor/rules` está siendo sustituida por `AGENTS.md` (leído ya por
  Cursor, Claude Code y Codex) — apostar por este formato es apostar por algo en salida.
- **rohitg00/awesome-claude-code-toolkit** (~2.600 ★, último commit 2026-05-12, 4 meses parado
  frente al barrido) — mismo terreno que wshobson/agents (agentes+skills+plugins+comandos) pero con
  15x menos estrellas y sin evidencia de evaluador de calidad propio. Redundante frente al #1.
- **La mayoría de resultados "Database Migration / API Design / Idempotency Patterns... Claude Code
  Skill"** que aparecieron en las búsquedas venían todos de las granjas SEO de arriba, describiendo
  el mismo puñado de conceptos genéricos con nombres de producto distintos. Ninguno aportaba algo
  que wshobson/agents o anthropics/skills no cubrieran ya con mejor mecanismo.

---

## Mapeo a COSMOS

Propuesta de encaje en la jerarquía sistema-solar > planeta > continente > país > provincia >
ciudad > pueblo. El dominio asignado ("ingeniería de producto software") corresponde a un
**continente** dentro del planeta más amplio de ingeniería de software:

- **Planeta**: `Ingeniería de Software` (incluye este continente y otros fuera de alcance aquí:
  IA/ML, mobile nativo, data engineering pesado, gaming).
- **Continente**: `Ingeniería de Producto SaaS` (este dominio).
- **Países** (familias de capacidades, 7):
  1. `Backend y Arquitectura de APIs`
  2. `Datos y Persistencia`
  3. `Autenticación, Autorización y Multi-tenencia`
  4. `Pagos, Suscripciones y Facturación`
  5. `Frontend de Producto`
  6. `Infraestructura y Despliegue`
  7. `Observabilidad, Rendimiento y Fiabilidad`
- **Provincias** (grupos de skills hermanas), con ejemplos por país:
  - *Backend y Arquitectura de APIs*: Diseño de API (REST/GraphQL/OpenAPI) · Patrones de
    arquitectura (Clean/Hexagonal/DDD, microservicios, CQRS/event sourcing/sagas) · Fiabilidad de
    API (idempotencia, rate limiting, webhooks HMAC).
  - *Datos y Persistencia*: Diseño de esquema · Migraciones (zero-downtime, ORMs) · Optimización de
    consultas (SQL/indexado).
  - *Autenticación...*: Patrones de auth (JWT/OAuth2/sesiones/RBAC) · Aislamiento multi-tenant (RLS,
    queries tenant-aware) · SSO empresarial.
  - *Pagos, Suscripciones y Facturación*: Integración de pasarelas (Stripe/PayPal/Square) ·
    Facturación y métricas de uso (billing automation, usage metering) · Cumplimiento de pago
    (PCI DSS, SCA).
  - *Frontend de Producto*: Design systems y componentes · Frameworks (Next.js/React) ·
    Accesibilidad.
  - *Infraestructura y Despliegue*: IaC (Terraform multi-cloud) · Contenedores y orquestación
    (Docker/Kubernetes/Helm/GitOps) · Pipelines CI/CD.
  - *Observabilidad...*: Métricas y dashboards (Prometheus/Grafana) · Trazas distribuidas
    (OpenTelemetry/Jaeger) · Rendimiento (profiling, Core Web Vitals) · Respuesta a incidentes
    (postmortems, runbooks).
- **Pueblos** (skills atómicas — ya localizadas en el barrido, instalables tal cual):
  `stripe-integration`, `pci-compliance`, `billing-automation`, `postgresql-table-design`,
  `sql-optimization-patterns`, `database-migration`, `auth-implementation-patterns`,
  `api-design-principles`, `microservices-patterns`, `k8s-manifest-generator`,
  `terraform-module-library`, `prometheus-configuration`, `distributed-tracing`,
  `webapp-testing`, `mcp-builder`, `before-you-build`.

---

## Lo que falta

Capacidades del dominio para las que NO apareció nada bueno en el barrido — habría que escribirlas
a mano:

1. **Aislamiento multi-tenant con verificación ejecutable.** Todo lo encontrado es prosa (guías de
   "usa RLS" o "filtra por tenant_id") o una librería parada de 16 estrellas
   (lanemc/multi-tenant-saas-toolkit). Falta una skill que genere Row-Level-Security de Postgres y
   la **verifique de verdad** — un test que intente leer datos de otro tenant y falle si lo consigue,
   no solo un checklist.
2. **Migraciones zero-downtime con guardarraíles ejecutables.** Herramientas OSS reales existen
   (gh-ost, pg-repack, Bytebase) pero ninguna está empaquetada como skill de Claude con scripts que
   comprueben locks, tiempo estimado o reversibilidad antes de aplicar. Todo lo visto es la versión
   markdown ("evita ALTER TABLE bloqueante en tablas grandes").
3. **Integración operativa de billing por uso.** Lago (arriba) es la pieza de infraestructura, pero
   no hay una skill que guíe paso a paso "conecta tu app a Lago/Stripe Billing y expón el
   dashboard de consumo al cliente" — el hueco está entre el producto y el conocimiento de cómo
   integrarlo.
4. **Validación de contratos de API ejecutable en el propio flujo del agente.** Hay mucha prosa
   sobre "OpenAPI 3.1" pero ningún skill visto invoca de verdad un linter tipo Spectral y actúa
   sobre su salida — sería fácil de escribir (Spectral es gratis y ya existe), pero nadie lo ha
   empaquetado como skill.
5. **Paywalls y experimentos de precio para SaaS.** `before-you-build` y `startup-metrics-framework`
   (wshobson/agents) dan el marco de alto nivel, pero no hay nada operativo tipo "genera y monta un
   A/B test de tabla de precios" — sigue siendo trabajo de producto, no de ingeniería, y probablemente
   deba quedar fuera de este continente.
