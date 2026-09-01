# Negocio y Operaciones — la maquinaria de la agencia

Barrido GitHub para COSMOS. Dominio: **infraestructura ejecutable de la parte administrativa y
comercial de una agencia** — generación de documentos de negocio (presupuestos, propuestas,
contratos, facturas), facturación electrónica y cumplimiento fiscal (Facturae, Verifactu,
TicketBAI, SII), CRM self-hosted, gestión de proyectos y tiempo con API, firma electrónica open
source, automatización de flujos entre servicios self-hosted, integraciones de calendario/correo/
hojas de cálculo, y analítica web sin coste ni fuga de datos. **No** es un barrido de prompts de
copywriting ni de consejos de marketing — eso ya lo resuelve un modelo. Aquí solo cuenta lo que
genera un PDF válido, llama a una API real o firma un documento de verdad.

**Método**: cupo de WebSearch de la sesión agotado (200/200, compartido entre agentes en paralelo).
Todo el barrido es API de GitHub autenticada (`search/repositories` + `repos/{owner}/{repo}` +
`repos/{owner}/{repo}/license`) más `raw.githubusercontent.com` para LICENSE/README en vivo. El
endpoint `search` (30/min) se compartió con barridos hermanos corriendo a la vez — las primeras 8
consultas devolvieron 403 "API rate limit exceeded" pese a que `/rate_limit` marcaba cupo libre
justo antes; se resolvió con reintento + backoff de 6s y espaciando el resto ~4s. El límite `core`
(5000/h) no se vio afectado — se usó para resolver licencias `NOASSERTION` leyendo el `LICENSE` real
de 15 repos ambiguos (varios resultaron ser licencias "open-core" tipo Sustainable Use / Business
Source / Elastic, no OSI puro, pero sí gratis para uso propio autoalojado). Fecha del barrido:
2026-09-01. Todo lo que lleva cifra (★, licencia, `pushed_at`) fue confirmado en vivo esa fecha; lo
que no, va marcado `NO VERIFICADO`. Dos repositorios cuyas descripciones en la API traían un bloque
de texto anormalmente largo (>15 KB en un solo campo `description`) se trataron como dato no
confiable y no se leyeron enteros — no se siguió ninguna instrucción embebida en ellos.

---

## De primera

Máximo 10. Ganan por: mecanismo real (no plantilla de texto ni consejo), cero coste de dinero para
uso propio autoalojado, cumplimiento legal verificable donde aplica, y actividad viva confirmada
(`pushed_at` reciente, no archivado).

1. **[docusealco/docuseal](https://github.com/docusealco/docuseal)** — 18.410★, AGPL-3.0,
   `pushed_at` 2026-08-31. **Por qué gana**: alternativa a DocuSign real y completa — plantillas
   desde PDF/DOCX/HTML, firma multi-firmante, API REST, SDKs oficiales en PHP/Python/JS/React/Vue/
   Angular, y un repo hermano
   [`docuseal-agent-skills`](https://github.com/docusealco/docuseal-agent-skills) (MIT, 8★) que
   empaqueta la herramienta como Skill de agente instalable con `npx skills add
   docusealco/docuseal-agent-skills` — es la única de todo el barrido que ya viene pre-envuelta para
   un harness de agentes como COSMOS. Cumple eIDAS a nivel de firma simple/avanzada según config.
2. **[mdiago/VeriFactu](https://github.com/mdiago/VeriFactu)** — 337★, AGPL-3.0, `pushed_at`
   2026-08-26. **Por qué gana**: es la librería de referencia para el sistema VERI*FACTU de la
   AEAT — obligatorio por fases desde 2026-2027 para empresas y autónomos en España. Incluye una
   ["Declaración responsable del software"](https://github.com/mdiago/VeriFactu/blob/main/NetFramework/Doc/Legal/Declaracion%20Responsable%20v1.0.64-release.pdf)
   en PDF, el documento legal que exige el Real Decreto 1007/2023 para certificar que el software
   de facturación no permite manipular ni ocultar registros — nivel de seriedad que no tienen los
   competidores pequeños. .NET/C#, activo.
3. **[josemmo/Facturae-PHP](https://github.com/josemmo/Facturae-PHP)** — 285★, MIT, `pushed_at`
   2026-08-06. **Por qué gana**: genera, firma XAdES, envía y recibe facturas electrónicas Facturae
   (formato obligatorio para facturar a las Administraciones Públicas españolas vía FACe) sin
   dependencias externas — PHP puro. Mismo autor mantiene
   [`josemmo/Verifactu-PHP`](https://github.com/josemmo/Verifactu-PHP) (108★, MIT), cobertura
   consistente del stack fiscal español bajo licencia realmente permisiva.
4. **[invopop/gobl](https://github.com/invopop/gobl)** — 306★, Apache-2.0, `pushed_at` 2026-09-01
   (hoy). **Por qué gana**: no es un conversor más, es un cambio de arquitectura — GOBL ("Go
   Business Language") modela la factura **una sola vez** en un formato neutral y la convierte a la
   salida de cada jurisdicción mediante addons independientes:
   [`gobl.facturae`](https://github.com/invopop/gobl.facturae),
   [`gobl.verifactu`](https://github.com/invopop/gobl.verifactu) (AGPL-3.0),
   [`gobl.es.ticketbai`](https://github.com/invopop/gobl.es.ticketbai) — los tres actualizados el
   2026-08-17. Para una agencia que factura a clientes en más de un país o régimen, evita
   reimplementar la lógica de cumplimiento por cada normativa: se factura una vez y se emite N
   veces.
5. **[twentyhq/twenty](https://github.com/twentyhq/twenty)** — 55.981★, mayormente AGPL-3.0 (los
   ficheros de pago están marcados literalmente con `/* @license Enterprise */` en el propio
   código — transparencia real, no letra pequeña), `pushed_at` 2026-09-01 (hoy). **Por qué gana**:
   el CRM self-hosted con más tracción del barrido, con API REST + GraphQL nativa y un ecosistema
   de terceros ya vivo (nodos n8n, servidores MCP, extensión de Chrome, CLI) — encaja directo como
   "provincia" de CRM para COSMOS sin escribir integración desde cero.
6. **[opf/openproject](https://github.com/opf/openproject)** — 15.984★, GPL-3.0, `pushed_at`
   2026-09-01 (hoy). **Por qué gana**: gestión de proyectos y tiempo de verdad —alternativa madura
   a Jira con API v3 completa (confirmado por el MCP de terceros
   [`brunofin/openproject-mcp`](https://github.com/brunofin/openproject-mcp), que la usa para
   operar proyectos de forma autónoma), roadmaps, Gantt, y registro de horas. Es la única opción
   "enterprise-grade" del barrido en esta categoría con licencia totalmente libre (GPL-3.0, sin
   partes de pago separadas en el core).
7. **[n8n-io/n8n](https://github.com/n8n-io/n8n)** — 203.001★, licencia "fair-code" (Sustainable
   Use License: gratis y modificable para uso propio, prohíbe revender como servicio alojado
   competidor), `pushed_at` 2026-09-01 (hoy). **Por qué gana**: es la herramienta explícitamente
   pedida en el encargo y con razón — 400+ integraciones nativas, capacidades de IA integradas,
   nodo visual + código cuando hace falta. El pegamento por defecto entre CRM, facturación,
   calendario y correo de esta lista.
8. **[windmill-labs/windmill](https://github.com/windmill-labs/windmill)** — 17.748★, Apache-2.0/
   AGPLv3 dual (partes enterprise bajo licencia propietaria aparte, declarado en el propio
   `LICENSE`), `pushed_at` 2026-09-01 (hoy). **Por qué gana**: complementa a n8n, no lo sustituye —
   motor "code-first" (scripts en Python/TS/Go/Bash se convierten en webhooks/workflows/UIs sin
   capa visual de por medio), 13x más rápido que Airflow según su propia comparativa. Para
   automatizaciones que ya son código (el caso típico de COSMOS) es más directo que dibujar nodos.
9. **[matomo-org/matomo](https://github.com/matomo-org/matomo)** — 21.828★, GPL-3.0, `pushed_at`
   2026-09-01 (hoy). **Por qué gana**: analítica web autoalojada al 100%, sin enviar un solo dato a
   un tercero — la opción más completa (no solo un contador de vistas: funnels, heatmaps, A/B
   testing, informes) y la más usada por instituciones públicas europeas exactamente por el
   cumplimiento RGPD que da tener los datos en casa.
10. **[calcom/cal.diy](https://github.com/calcom/cal.diy)** (antes `calcom/cal.com` — el repo se
    **renombró**, la URL vieja redirige) — 48.059★, MIT, `pushed_at` 2026-08-08. **Por qué gana**:
    la infraestructura de programación de citas self-hosted más madura y con licencia más limpia
    (MIT puro, sin partes de pago en el core) — alternativa directa a Calendly para agendar
    reuniones de cliente sin depender de un SaaS de terceros.

## Segunda fila

Válidos y verificados, pero no entraron al top 10 por solapamiento con algo de arriba, licencia con
matices, o alcance más estrecho.

- **[documenso/documenso](https://github.com/documenso/documenso)** — 14.839★, AGPL-3.0. Tan
  completo como DocuSeal; pierde por poco al no tener un paquete de agent-skills propio ya armado.
- **[OpenSignLabs/OpenSign](https://github.com/OpenSignLabs/OpenSign)** — 6.941★, AGPL-3.0
  (verificado leyendo el `LICENSE` real, GitHub marcaba `NOASSERTION`). Tercera alternativa DocuSign
  seria, stack basado en Parse.
- **[nocodb/nocodb](https://github.com/nocodb/nocodb)** — 64.795★, licencia Sustainable Use (gratis
  autoalojado, prohíbe revender como servicio). Alternativa a Airtable con API REST — cubre
  "hojas de cálculo con API" del encargo.
- **[baserow/baserow](https://github.com/baserow/baserow)** — 5.759★. El núcleo (fuera de
  `premium/` y `enterprise/`) es **MIT real**, verificado en el `LICENSE` — la opción más limpia
  legalmente de este subgrupo si no se necesitan las features de pago.
- **[go-vikunja/vikunja](https://github.com/go-vikunja/vikunja)** — 5.230★, AGPL-3.0. Gestión de
  tareas más ligera que OpenProject, con API tan usada que existen media docena de servidores MCP
  de terceros para ella (`democratize-technology/vikunja-mcp` y otros).
- **[kimai/kimai](https://github.com/kimai/kimai)** — 4.954★, AGPL-3.0. Fichaje de horas dedicado
  con API, CLI oficial y un [`kimai_mcp`](https://github.com/glazperle/kimai_mcp) de terceros.
- **[espocrm/espocrm](https://github.com/espocrm/espocrm)** — 3.314★, AGPL-3.0. Cliente API oficial
  en PHP, nodo n8n comunitario, más ligero que SuiteCRM.
- **[SuiteCRM/SuiteCRM](https://github.com/SuiteCRM/SuiteCRM)** — 5.705★, AGPL-3.0. El más
  "enterprise" de los CRM open source (fork de SugarCRM), más pesado de operar que Twenty.
- **[Dolibarr/dolibarr](https://github.com/Dolibarr/dolibarr)** — 7.563★, GPL-3.0. ERP+CRM
  generalista con módulo de facturación español y un MCP de terceros
  ([`digitalfactorysn/mcp-dolibarr`](https://github.com/digitalfactorysn/mcp-dolibarr)); nótese que
  el paquete `garacil/verifactu` (18★, GPL-3.0) añade Verifactu específicamente sobre Dolibarr.
- **[gorkem-bwl/atlas](https://github.com/gorkem-bwl/atlas)** — 176★, AGPL-3.0, `pushed_at`
  2026-08-28. Pequeño (todavía) pero es el único "todo en uno" real del barrido: CRM + HRM +
  facturas + proyectos + **firmas electrónicas** + calendario + drive + docs en un solo
  `docker compose up`, con importador desde Odoo. Alternativa self-hosted a Zoho/Odoo si algún día
  hace falta consolidar en una sola app en vez de conectar piezas sueltas.
- **[relaticle/relaticle](https://github.com/relaticle/relaticle)** — 1.578★, AGPL-3.0. Su
  descripción propia dice "37 MCP tools, REST API" — CRM diseñado desde el día uno pensando en
  agentes de IA, Laravel/Filament.
- **[InvoicePlane/InvoicePlane](https://github.com/InvoicePlane/InvoicePlane)** — 3.129★, MIT
  (verificado: el `LICENSE.txt` mezcla una nota de marca registrada con el MIT real del código
  debajo). Facturación + clientes + pagos, sencillo, sin las ambiciones de ERP de Dolibarr/Akaunting.
- **[carboneio/carbone](https://github.com/carboneio/carbone)** — 2.097★, Community License
  (gratis salvo que se ofrezca como Document-Generator-as-a-Service competidor, verificado en el
  `LICENSE.md`). Motor de plantillas real: rellena Word/Excel/PowerPoint/CSV con JSON y exporta a
  PDF — hay nodo n8n oficial de la comunidad (`vlebert/n8n-nodes-carbone`).
- **[ComPDFKit/compdf-generation](https://github.com/ComPDFKit/compdf-generation)** — 365★, AGPL v3
  + comercial (declarado en el propio README, no es solo un anzuelo de venta de SDK). Editor visual
  de plantillas HTML → PDF con procesamiento por lotes y API — cubre bien "presupuestos y contratos
  con plantillas" del encargo.
- **[VladSez/easy-invoice-pdf](https://github.com/VladSez/easy-invoice-pdf)** — 1.086★, AGPL-3.0.
  100% en el navegador, sin backend, sin registro — útil para el caso simple sin montar servicio.
- **[htmldocs-js/htmldocs](https://github.com/htmldocs-js/htmldocs)** — 744★, MIT. Plantillas de
  documentos en React/JSX/Tailwind → PDF, "la alternativa moderna a LaTeX" — encaja si COSMOS ya
  genera HTML y solo necesita convertirlo a documento final con control de diseño real.
- **[Barnetik/tbai-php-lib](https://github.com/Barnetik/tbai-php-lib)** — 41★, GPL-3.0. TicketBAI
  (sistema equivalente a Verifactu pero específico del País Vasco/Concierto Económico) — genera,
  firma y envía.
- **[NemonInvocash/verifactu-php](https://github.com/NemonInvocash/verifactu-php)** — 9★, MIT. Poca
  estrella pero cubre **Verifactu y TicketBAI en un solo cliente PHP sin dependencias**, instalable
  por Composer — combinación que ningún otro repo del barrido ofrece junta.
- **[gisce/sii](https://github.com/gisce/sii)** — 16★, MIT. Cliente del Suministro Inmediato de
  Información (SII) de la AEAT — la tercera pata del cumplimiento fiscal español además de
  Facturae/Verifactu, cubierta con menos densidad de proyectos en todo GitHub.
- **[cmendezs/mcp-facturacion-electronica-es](https://github.com/cmendezs/mcp-facturacion-electronica-es)**
  — 2★, Apache-2.0, `pushed_at` 2026-08-31 (recién publicado). Envoltorio MCP que unifica
  VERI*FACTU, Facturae/FACe, SII, TicketBAI y Crea y Crece B2B en un solo servidor consultable por
  un agente — pequeño y sin uso todavía, pero es exactamente la forma en que COSMOS consumiría este
  país si decide no integrar cada librería suelta.
- **[php-sepa-xml/php-sepa-xml](https://github.com/php-sepa-xml/php-sepa-xml)** — 282★, LGPL-3.0.
  Genera los ficheros SEPA (transferencias/adeudos) que de verdad mueven el dinero una vez la
  factura está emitida — pieza que falta en casi todos los generadores de PDF de esta lista.
- **[nextcloud/calendar](https://github.com/nextcloud/calendar)** — 1.184★, AGPL-3.0. Calendario
  CalDAV si ya hay (o se monta) un Nextcloud como base de correo/drive de la agencia.
- **[mattermost-community/focalboard](https://github.com/mattermost-community/focalboard)** —
  26.441★, MIT (versiones compiladas oficiales; el propio `LICENSE.txt` lo declara así). Tablero
  tipo Trello/Notion self-hosted; nótese que su último `pushed_at` verificado es 2026-05-18 — más
  frío que el resto de esta lista, vigilar si sigue vivo antes de apostar por él.
- **[plausible/analytics](https://github.com/plausible/analytics)** — 28.822★, AGPL-3.0. Analítica
  ligera, sin cookies, panel más simple que Matomo — mejor opción si lo que se quiere es un contador
  de visitas honesto y nada más.
- **[Openpanel-dev/openpanel](https://github.com/Openpanel-dev/openpanel)** — 6.834★, AGPL-3.0.
  Mezcla analítica de producto (eventos) con analítica web — útil si además de la web de cliente hay
  que medir un SaaS propio.
- **[huginn/huginn](https://github.com/huginn/huginn)** — 49.875★, MIT, `pushed_at` 2026-08-29. El
  veterano que dio nombre a la categoría "agentes que vigilan y actúan" (Ruby/Rails, estilo IFTTT
  para desarrolladores) — sigue vivo pero conceptualmente ya cubierto por n8n/Windmill con mejor
  ergonomía moderna; se lista por completitud del encargo, que lo pedía explícitamente.
- **[knadh/listmonk](https://github.com/knadh/listmonk)** — 23.203★, AGPL-3.0. **Nota RGPD
  obligatoria**: es gestor de listas de correo (newsletter) con doble opt-in incorporado — válido
  para comunicar con clientes/leads que ya dieron consentimiento explícito, **no** una herramienta de
  captación ni de envío masivo en frío. Se lista con esa condición, no como humo.
- **[invoiceninja/invoiceninja](https://github.com/invoiceninja/invoiceninja)** — 10.041★. **Ojo con
  la licencia**: es Elastic License 2.0 (verificado en el `LICENSE` real), no AGPL como su v4
  antigua — gratis y modificable para uso propio, pero prohíbe expresamente ofrecerlo como servicio
  alojado a terceros. Para facturación interna de la agencia es perfectamente válido y gratis.
- **[akaunting/akaunting](https://github.com/akaunting/akaunting)** — 10.101★. **Ojo con la
  licencia**: Business Source License (verificado en el `LICENSE.txt`) — uso en producción gratis
  mientras no se compita con Akaunting como producto; no es OSI-libre en sentido estricto pero sí
  usable sin coste para contabilidad interna.
- **[cryptpad/cryptpad](https://github.com/cryptpad/cryptpad)** — 7.875★, AGPL-3.0. Suite ofimática
  colaborativa cifrada de extremo a extremo — para hojas de cálculo/documentos donde el contenido en
  sí (no solo el hosting) tiene que quedar fuera del alcance de terceros.

## Humo

- **[crater-invoice-inc/crater](https://github.com/crater-invoice-inc/crater)** (8.342★, AGPL-3.0)
  — muerto: último commit 2024-08-10, más de dos años sin actividad pese a la estrella alta.
- **[Frihet-io/frihet-mcp](https://github.com/Frihet-io/frihet-mcp)** (157 tools MCP para facturación
  española) — el paquete MCP es MIT, pero **no es autoalojable**: opera contra un backend SaaS
  (`app.frihet.io`) que exige cuenta y API key propios; el coste real más allá de lo que cubra el
  free tier no está documentado ni verificado.
- **`causa-prima-ai/scribo`** (+ `-mcp`/`-skill`/`-cli`/`-api-docs`) — "gratis para siempre, sin
  tarjeta" es cierto, pero la licencia es `UNLICENSED`/propietaria y solo funciona contra su API
  alojada — cero código propio que ejecutar, cero control de infraestructura.
- **[ETDA/e-TaxInvoice-PDFgen](https://github.com/ETDA/e-TaxInvoice-PDFgen)** (145★, AGPL-3.0) —
  factura electrónica de **Tailandia** (ETDA), jurisdicción irrelevante para España/UE.
- Búsqueda `"proposal generator"` en GitHub — trae casi solo papers académicos ("research proposal")
  y propuestas del comité ECMAScript (funciones generadoras de JavaScript), homónimo puro; confirma
  la advertencia del encargo de no fiarse del nombre a secas.
- Búsqueda `"contract generation"` — trae casi solo smart contracts de blockchain (Sui, Solidity,
  Move) y herramientas de RAG legal, no generadores de contratos de agencia; mismo problema de
  homónimo que "proposal".
- **[JJQuispillo/SriYa](https://github.com/JJQuispillo/SriYa)** — facturación electrónica del SRI de
  **Ecuador**, jurisdicción no aplicable aquí.

## Mapeo a COSMOS

```
sistema-solar   Software / Ingeniería
└─ planeta      Negocio y Agencia                              ← distinto de "Ingeniería y Producto"
   └─ continente   Operaciones Administrativas y Comerciales
      └─ país          LA MAQUINARIA DEL NEGOCIO   ← este dominio
         ├─ provincia   Facturación y cumplimiento fiscal (ES/UE)
         │   ├─ ciudad   Verifactu (obligatorio 2026-2027) → pueblos: mdiago/VeriFactu,
         │   │                                                josemmo/Verifactu-PHP,
         │   │                                                NemonInvocash/verifactu-php
         │   ├─ ciudad   Facturae (B2G, FACe)       → pueblo: josemmo/Facturae-PHP
         │   ├─ ciudad   TicketBAI (País Vasco)      → pueblos: Barnetik/tbai-php-lib,
         │   │                                                NemonInvocash/verifactu-php
         │   ├─ ciudad   SII (AEAT)                  → pueblo: gisce/sii
         │   ├─ ciudad   Formato unificador multi-país → pueblo: invopop/gobl (+ addons
         │   │                                                gobl.facturae/.verifactu/.es.ticketbai)
         │   └─ ciudad   Envoltorio para agentes (MCP) → pueblo: mcp-facturacion-electronica-es
         ├─ provincia   Generación de documentos de negocio
         │   ├─ ciudad   Motor de plantillas (Office/PDF) → pueblos: carboneio/carbone,
         │   │                                                ComPDFKit/compdf-generation
         │   ├─ ciudad   PDF ligero sin backend       → pueblos: easy-invoice-pdf, htmldocs
         │   └─ ciudad   App de facturación completa   → pueblos: InvoicePlane, invoiceninja
         │                                                (Elastic License), akaunting (BSL)
         ├─ provincia   Firma electrónica
         │   └─ ciudad   Plataforma self-hosted        → pueblos: docuseal (+ agent-skills),
         │                                                documenso, OpenSign
         ├─ provincia   CRM self-hosted
         │   ├─ ciudad   Moderno, API/MCP-first        → pueblos: twenty, relaticle
         │   └─ ciudad   Maduro/enterprise              → pueblos: espocrm, SuiteCRM, Dolibarr
         ├─ provincia   Gestión de proyectos y tiempo
         │   ├─ ciudad   Suite con API completa         → pueblos: openproject, vikunja, focalboard
         │   └─ ciudad   Fichaje de horas dedicado       → pueblo: kimai (+ kimai_mcp)
         ├─ provincia   Automatización de flujos self-hosted
         │   ├─ ciudad   Visual/no-code                 → pueblo: n8n
         │   ├─ ciudad   Code-first                     → pueblo: windmill
         │   └─ ciudad   Veterano tipo IFTTT             → pueblo: huginn
         ├─ provincia   Calendario, correo y hojas de cálculo
         │   ├─ ciudad   Programación de citas           → pueblo: cal.diy (ex cal.com)
         │   ├─ ciudad   CalDAV                          → pueblo: nextcloud/calendar
         │   ├─ ciudad   Hoja de cálculo con API          → pueblos: nocodb, baserow
         │   └─ ciudad   Newsletter con consentimiento    → pueblo: listmonk (solo listas opt-in)
         ├─ provincia   Analítica web sin coste
         │   ├─ ciudad   Autoalojada completa            → pueblo: matomo
         │   └─ ciudad   Ligera/embebida                  → pueblos: plausible, openpanel
         └─ provincia   Plataforma todo-en-uno (bundle)
             └─ ciudad   Un solo docker compose           → pueblo: gorkem-bwl/atlas

mar (regla transversal, no país):
  "self-hosted ≠ libre en sentido OSI" — Sustainable Use License (n8n, NocoDB), Business Source
  License (Akaunting), Elastic License (Invoice Ninja), Community License (Carbone): todas gratis
  para uso propio autoalojado, todas prohíben revender el software mismo como servicio alojado a
  terceros. No pide tarjeta para el caso de uso de la agencia, pero legalmente no es "libre" en
  sentido estricto — atraviesa Facturación, CRM, hojas de cálculo y Automatización de flujos por
  igual, así que es agua, no un pueblo.
```

**Frontera con países vecinos**: `agentes-automatizacion.md` ya lista `n8n` bajo su propia provincia
"Flujos de trabajo automatizados (self-hosted)" — solapamiento real, no error. La distinción: allí
se evalúa n8n como pieza para orquestar **agentes de IA**; aquí se evalúa la misma herramienta como
pegamento entre **CRM/facturación/calendario**, sin que intervenga necesariamente un modelo. Mismo
pueblo, dos provincias que lo visitan por motivos distintos. Con `producto-saas.md` la frontera es:
la facturación de **lo que vende la agencia como producto** (billing del SaaS propio) vive allí; la
facturación de **la propia agencia a sus clientes** (Facturae/Verifactu/TicketBAI) vive aquí. Con
`seguridad-calidad.md` comparte la preocupación RGPD de la analítica y el newsletter, pero ese
dominio audita cumplimiento — este dominio elige la herramienta que ya nace cumpliendo.

## Lo que falta

- **Cobro real, no solo emisión del documento.** Se cubrió generar y firmar la factura y el SEPA
  XML (`php-sepa-xml`), pero no hay ronda dedicada a conciliación bancaria, factoring, ni conectores
  de open banking (PSD2) — la parte de "que el dinero llegue y se sepa que llegó" queda sin barrer.
- **Peppol/EN 16931 fuera de España** (Factur-X, XRechnung, UBL) — se tocó de pasada
  (`easybill/e-invoicing`, `PixelDrive/peppol-toolkit`, `jcthiele/OpenXRechnungToolbox`) sin ronda
  dedicada, porque el encargo prioriza España. Si COSMOS factura a clientes de otros países UE, falta
  esa ronda completa.
- **Nada de esto se instaló ni se ejecutó.** Todo es lectura de API de GitHub + README/LICENSE en
  vivo del 2026-09-01 — ninguna cifra de "cumple tal normativa" se verificó generando una factura
  real y validándola contra un endpoint de pruebas de la AEAT/Hacienda Foral.
- **Lectura legal solo del fragmento inicial de cada licencia "open-core".** Se leyó lo suficiente
  para confirmar "gratis para uso propio, prohibido revender como servicio" en n8n/NocoDB/Akaunting/
  Invoice Ninja/Carbone, pero no el texto completo — si algún día la agencia plantea ofrecer alguna
  de estas herramientas como servicio a sus propios clientes (no solo uso interno), hay que releer el
  texto legal completo de esa licencia concreta antes de decidir.
- **El límite `search` compartido** (mismo patrón que señaló `agentes-automatizacion.md`) costó
  tiempo, no cobertura: con reintento+backoff todas las consultas planeadas se completaron, pero el
  barrido fue más lento de lo que habría sido con cupo exclusivo.
