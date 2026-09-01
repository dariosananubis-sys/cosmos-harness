# Dominio: Web, e-commerce y conversión

Barrido de GitHub para poblar COSMOS. Cubre: construcción de sitios (WordPress, Elementor),
tiendas online (WooCommerce, Shopify), pagos, diseño de interfaz (Figma-to-code, Tailwind),
accesibilidad (a11y/WCAG), rendimiento web (Core Web Vitals) y CRO (landings, formularios,
checkout, A/B testing).

Metodología: WebSearch (variantes en castellano e inglés, por subtema) + verificación de
estrellas/última actividad vía `api.github.com` (algunos con caché de WebFetch cuando el API
rate-limit unauthenticated se agotó) + lectura de README/estructura de cada repo candidato.
Fecha del barrido: 2026-09-01.

---

## De primera

Diez recursos, ordenados por peso real (oficialidad + mecanismo + actividad), no por estrellas.

1. **[WordPress/agent-skills](https://github.com/WordPress/agent-skills)** — ⭐ 2090 · activo
   (push 2026-08-24) · **oficial del proyecto WordPress**. 14+ skills portables (bloques, temas,
   arquitectura de plugins, seguridad, REST/Interactivity API, permisos por capacidades, WP-CLI,
   rendimiento, WordPress Playground, Design System, guías de Plugin Directory). Mecanismo real:
   cada skill trae, además del `SKILL.md`, documentación de referencia y **scripts JavaScript
   deterministas** de detección/validación — no es solo prosa. Instalable global o por proyecto,
   compatible con Claude/Cursor/Copilot. Gana por ser la fuente canónica y por tener el ecosistema
   más grande alrededor (91 commits, 27 PRs, 24 issues abiertas — vivo de verdad).

2. **[addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills)** — ⭐ 2730 ·
   activo (push 2026-08-24). Autor: Addy Osmani, líder de Chrome DevTools en Google — autoridad
   real en la materia, no un curioso. 6 skills: auditoría orquestada, performance, Core Web Vitals
   (LCP/INP/CLS con checklist de causas y fixes por framework), accesibilidad WCAG 2.2, SEO,
   buenas prácticas de seguridad/estándares modernos. Mecanismo: se integra con **Chrome DevTools
   MCP** para medición en vivo y cae a **Lighthouse CLI + PageSpeed Insights** si no hay MCP —
   mide de verdad, no opina. Sin coste (Lighthouse es local/gratis).

3. **[stripe/ai](https://github.com/stripe/ai)** — ⭐ ~1.8k · **oficial de Stripe**. No es un
   `SKILL.md` suelto: es un monorepo con SDKs reales (`@stripe/ai-sdk` para Vercel AI SDK,
   `@stripe/token-meter`), skills instalables vía `npx skills add https://docs.stripe.com` y un
   servidor MCP remoto con OAuth. Cubre checkout, suscripciones, webhooks, SCA. Nota de coste: el
   SDK/skill es gratis, pero **Stripe como pasarela cobra comisión por transacción** — no es gasto
   de infraestructura pero sí un coste de negocio a decidir con el cliente, no a instalar sin más.

4. **[Community-Access/accessibility-agents](https://github.com/Community-Access/accessibility-agents)**
   — ⭐ 403 · activo (push 2026-08-11). 79 agentes en 8 equipos; 11 son especialistas web (ARIA,
   foco en modales, contraste, teclado, live regions, validación de formularios, alt text, tablas,
   calidad de link text, auditoría interactiva). Mecanismo: instrucciones Markdown que **invocan
   axe-core y Playwright** para el escaneo real, con salida en **SARIF 2.1.0** y CSV con
   remediación — no es "revisa esto a ojo", produce artefactos verificables. Corre en Claude Code,
   GitHub Copilot, Gemini CLI, Codex y MCP Server.

5. **[masuP9/a11y-specialist-skills](https://github.com/masuP9/a11y-specialist-skills)** — ⭐ 56 ·
   activo (push 2026-06-13). Menos estrellas pero el más ejecutable de los de accesibilidad: trae
   un **paquete npm (`@a11y-skills/audit`)** con scripts Playwright dedicados para foco, reflow,
   espaciado de texto y tamaño de objetivo táctil, más metodología **WAIC** para planificar una
   auditoría formal. 4 skills: revisión ad hoc, auditoría WCAG 2.2 AA en 4 fases (automatizada +
   interactiva + manual + calidad de contenido), planificación de auditoría, plan de madurez
   organizacional (L1-L4). Gana a los de más estrellas en profundidad de mecanismo.

6. **[spruikco/fat-agent-skill](https://github.com/spruikco/fat-agent-skill)** ("FAT Agent — Fix,
   Audit, Test") — ⭐ 38 · el mecanismo más pesado encontrado en todo el barrido: **scripts Python**
   (parseo HTML, scoring, crawler concurrente a SQLite, integración Lighthouse, regresión visual),
   validadores modulares por categoría, dashboard HTML generado por plantilla y **915 tests en 55
   ficheros**. Auto-detecta módulos de e-commerce/negocio local/i18n analizando el HTML del sitio.
   Audita SEO, seguridad, accesibilidad, rendimiento, SEO local, e-commerce, deliverability de
   email, DNS. Re-testea tras el redeploy para confirmar el fix. Pocas estrellas porque es
   reciente, pero es justo lo que pide el criterio "mecanismo, no prosa".

7. **[woocommerce/agent-skills](https://github.com/woocommerce/agent-skills)** — ⭐ 9 · activo
   (push 2026-08-25) · **oficial de WooCommerce/Automattic**, muy nuevo. Dos skills documentadas
   (Abilities API, auditoría de PRs stale) pero con **tooling de build real**
   (`shared/scripts/skillpack-build.mjs`, `skillpack-install.mjs`) que empaqueta para
   Claude/Copilot/Cursor/Codex a la vez. Cubre patrones post-HPOS y Blocks API — la fuente correcta
   para no escribir extensiones WooCommerce con patrones obsoletos.

8. **[woocommerce/woocommerce-claude](https://github.com/woocommerce/woocommerce-claude)** — ⭐ 28
   · activo (push 2026-08-24) · **oficial**. Capa de analítica IA para tiendas WooCommerce vivas
   ("pregúntale a tu tienda cualquier cosa"): conocimiento estructurado de la tienda + scoring de
   "AI readiness" + skills de insight. Útil para diagnóstico de una tienda de cliente ya en
   producción, complementario a `tienda-woocommerce` (la skill ya instalada localmente, que cubre
   carga de catálogo).

9. **[Shopify/Shopify-AI-Toolkit](https://github.com/Shopify/Shopify-AI-Toolkit)** — ⭐ 527 ·
   activo (push 2026-08-28) · **oficial de Shopify**. Instalable con
   `claude plugin install shopify-ai-toolkit@claude-plugins-official`. Conocimiento experto en
   GraphQL/REST Admin API, Liquid, Polaris (componentes UI), OAuth, webhooks, Billing API,
   extensiones de checkout UI y admin UI, extensiones POS, bulk operations. Referencia obligada si
   algún cliente pide Shopify en vez de WooCommerce.

10. **[Automattic/wordpress-agent-skills](https://github.com/Automattic/wordpress-agent-skills)** —
    ⭐ 112 · **oficial de Automattic/WordPress.com**. Incluye un **servidor MCP de Studio** que
    ejecuta WP-CLI de verdad, escribe ficheros y genera enlaces de preview compartibles sobre un
    WordPress local — no solo instrucciones. Entra en la lista con matiz: el propio README lo
    marca como "prototipo temprano" y advierte que **los temas generados no son production-ready**;
    útil para prototipar rápido, no para la entrega final a cliente.

## Segunda fila

- **[respira-press/agent-skills-wordpress](https://github.com/respira-press/agent-skills-wordpress)**
  — ⭐ 42, muy activo (push 2026-08-27). Mecanismo real (214-319 tools MCP para auditoría,
  migración entre page builders incluido Elementor→Gutenberg/Bricks/Breakdance), pero **depende
  del servidor MCP comercial `respira-wordpress-mcp`, de pago** (planes desde 9-19 €/mes, hasta
  199 €/mes agencia) — viola la regla de coste cero salvo autorización explícita de Darío.
- **[secondsky/claude-skills](https://github.com/secondsky/claude-skills)** — ⭐ 212, muy activo
  (push 2026-08-30). 142 skills "production-tested", incluye `woocommerce-code-review` y
  `web-performance-optimization`. Genérico (Cloudflare/React/Tailwind también), no especializado.
- **[jezweb/claude-skills](https://github.com/jezweb/claude-skills)** — ⭐ 986, activo (push
  2026-07-02). Plugin de Shopify (`shopify-products`, `shopify-content`, `shopify-setup`) dentro
  de una colección más amplia de stack fullstack.
- **[jorgerosal/wordpress-skills](https://github.com/jorgerosal/wordpress-skills)** — ⭐ 82, activo
  (push 2026-06-07). Skills para Claude y Codex de desarrollo WordPress genérico.
- **[elvismdev/claude-wordpress-skills](https://github.com/elvismdev/claude-wordpress-skills)** —
  ⭐ 230 pero **parado desde 2025-11-29** (~9 meses); el ecosistema de Skills cambió mucho desde
  entonces (formato oficial de Anthropic se estabilizó después). Cubre performance, seguridad,
  Gutenberg — revisar si sigue vigente antes de instalar.
- **[Mekko-Digital/elementor-skills](https://github.com/Mekko-Digital/elementor-skills)** — ⭐ 1,
  activo (push 2026-06-11). Markdown puro sin scripts, pero muy bien acotado: 7 skills atómicas
  (widgets custom, form actions Pro, dynamic tags, theme builder locations, **render-debug** para
  páginas Elementor rotas/en blanco, matriz free-vs-Pro de features, deploy-verify vía WP-CLI/MCP
  solo en staging). El `render-debug` en particular es justo el tipo de conocimiento verificable
  que un modelo genérico no trae de fábrica.
- **[guramzhgamadze/WordPress-Elementor-Skill](https://github.com/guramzhgamadze/WordPress-Elementor-Skill)**
  — ⭐ 25, activo (push 2026-08-23). Un único `SKILL.md` extenso, guía procedimental para código
  WordPress+Elementor Pro de producción. Prosa densa, sin scripts propios.
- **[lmoncany/elementor-claude-skill](https://github.com/lmoncany/elementor-claude-skill)** — ⭐ 3,
  activo (push 2026-03-13). Crea/scrapea/inyecta/genera en bulk páginas Elementor Flexbox
  Container vía WP-CLI — mecanismo real pero muy nicho y poco probado (3 estrellas).
- **[Shopify/liquid-skills](https://github.com/Shopify/liquid-skills)** — ⭐ 32, **oficial** pero
  sin push desde 2026-03-18 (~5-6 meses parado; dentro del año pero ritmo bajo para ser oficial).
- **[devkindhq/shopifyql-skill](https://github.com/devkindhq/shopifyql-skill)** — ⭐ 7, activo
  (push 2026-05-28). Nicho: solo ayuda a escribir/depurar consultas ShopifyQL de analítica.
- **[Properly-DEV/figma-to-code-skills](https://github.com/Properly-DEV/figma-to-code-skills)** —
  ⭐ 6, push 2026-04-17. Diez skills que convierten un design system de Figma en React+Tailwind.
- **[nafiurrahmanniloy/figma-skill](https://github.com/nafiurrahmanniloy/figma-skill)** — ⭐ 2,
  push 2026-03-12. Conecta con la API de Figma, extrae tokens, genera código para 7 frameworks.
  Requiere token de API de Figma (cuenta gratuita de Figma sirve, sin tarjeta).
- **[wshobson/agents](https://github.com/wshobson/agents)** — ⭐ 39317, muy activo (push
  2026-08-31). Marketplace multi-dominio enorme (93 plugins, 202 agentes, 181 skills, 105
  comandos) para 5 harnesses distintos. Incluye un skill `tailwind-design-system` pero **no está
  especializado en web/e-commerce** — es horizontal (arquitectura, infra, seguridad, datos, ML).
  Vale la pena tenerlo indexado como fuente genérica, no como recurso de este dominio.

## Humo

- **[andreilupu/wp-cursor-rules](https://github.com/andreilupu/wp-cursor-rules)** — ⭐ 4, sin push
  desde 2025-03-26 (>1 año muerto), formato `.cursorrules` pre-estándar de Skills. Prosa genérica.
- **[PatrickJS/awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules)** (entrada
  WordPress) — el repo tiene 40690 estrellas pero la entrada concreta de WordPress es un
  `.cursorrules` de una sola pieza, sin mecanismo, formato obsoleto frente al estándar Agent
  Skills actual.
- **[scoobynko/claude-code-design-skills](https://github.com/scoobynko/claude-code-design-skills)**
  — ⭐ 39, sin push desde 2025-11-07 (~10 meses). Figma-to-code sin actividad reciente.
- **[firedev/tailwind-skill](https://github.com/firedev/tailwind-skill)** — ⭐ 1. Un solo skill,
  atado a apps Rails, sin tracción.
- **[pwinslow/Conversion-Rate-Optimization](https://github.com/pwinslow/Conversion-Rate-Optimization)**
  — notebook Jupyter de un reto de datos universitario, no una herramienta de agente. Representa
  bien el patrón: casi todo lo que aparece bajo "CRO" en GitHub es ciencia de datos académica o
  checklists en blogs, no mecanismo para un agente.

## Mapeo a COSMOS

Este dominio entero encaja como **continente** dentro de cada planeta (proyecto de cliente) que
tenga web: `Continente: Web y comercio electrónico`. Los países son familias de capacidades; las
provincias, grupos de skills hermanas dentro de un país; los pueblos, skills atómicas.

- **País: WordPress** — provincias: *Bloques y temas* (block.json, render, deprecación — de
  `WordPress/agent-skills`), *WP-CLI y operaciones* (search-replace, multisite, backups — de
  `WordPress/agent-skills` + `Automattic/wordpress-agent-skills`), *Seguridad y arquitectura de
  plugins*. Pueblos: `wordpress-plugin-development` (ya instalada localmente), `block-development`,
  `wp-cli-operations`.
- **País: WooCommerce** — provincias: *Extensiones y Blocks API* (post-HPOS, service container —
  de `woocommerce/agent-skills`), *Catálogo y stock* (ya cubierta por la skill local
  `tienda-woocommerce`), *Analítica de tienda viva* (`woocommerce/woocommerce-claude`). Pueblo:
  `wordpress-woocommerce-development` (ya instalada localmente).
- **País: Elementor** — provincias: *Widgets y controles Pro* (`Mekko-Digital/elementor-skills`),
  *Theme Builder* (header/footer/condiciones de visualización), *Debug de render* (páginas en
  blanco, corrupción de datos, CSS regen). Pueblos: `header-footer` y `web-fidelidad-elementor`
  (ya instaladas localmente cubren buena parte de esta provincia con mecanismo propio: medición
  numérica contra mockup).
- **País: Shopify** — provincias: *Admin API y Liquid* (`Shopify/Shopify-AI-Toolkit`,
  `Shopify/liquid-skills`), *Analítica ShopifyQL* (`devkindhq/shopifyql-skill`).
- **País: Pagos y checkout** — provincia: *Stripe* (`stripe/ai`, con SDKs y MCP oficiales). Pueblo
  huérfano detectado: no hay país para pasarelas europeas/españolas (Redsys/TPV Virtual, PayPal) —
  ver "Lo que falta".
- **País: Accesibilidad (a11y/WCAG)** — provincias: *Auditoría automatizada* (axe-core + Playwright,
  de `Community-Access/accessibility-agents` y `masuP9/a11y-specialist-skills`), *Planificación y
  madurez organizacional* (metodología WAIC). Pueblo: la skill local `accessibility` puede
  absorber mecanismo de estos dos repos en vez de quedarse en prosa genérica.
- **País: Rendimiento web (Core Web Vitals)** — provincias: *Medición* (Lighthouse CLI/PSI/Chrome
  DevTools MCP, de `addyosmani/web-quality-skills`), *Auditoría integral post-lanzamiento*
  (`spruikco/fat-agent-skill`, con crawler y regresión visual).
- **País: Diseño de interfaz (Figma-to-code, Tailwind)** — provincias: *Extracción de tokens*
  (`Properly-DEV/figma-to-code-skills`, `nafiurrahmanniloy/figma-skill`), *Sistemas Tailwind*.
- **País: CRO / conversión** — sin provincias sólidas todavía; ver "Lo que falta".

## Lo que falta

- **CRO con mecanismo real: no existe nada bueno.** Todo lo encontrado bajo "conversion rate
  optimization" en GitHub es prosa de blog, checklists o notebooks académicos de ciencia de datos
  — nada que analice un funnel real, corra un test A/B, o mida fricción de un formulario de forma
  verificable. Es el hueco más grande de todo el dominio. Si se necesita CRO de verdad, hay que
  construirlo (p. ej. un script que cruce datos de GA4/heatmap con un checklist de fricción
  verificable, no un skill que "opine" sobre persuasión).
- **Pasarelas de pago europeas/españolas: nada.** Cobertura fuerte de Stripe (oficial) pero cero
  para Redsys/TPV Virtual, PayPal (más allá de menciones sueltas) o Bizum — relevante para el
  trabajo real de la agencia con clientes españoles.
- **Validador de checkout end-to-end (WooCommerce/Shopify) con medición real**: nada equivalente
  a `fat-agent-skill` pero centrado en el flujo de compra completo (carrito → pago → confirmación)
  con aserciones automáticas. Se podría montar combinando Playwright + `fat-agent-skill` como base.
- **Landing pages / tests A/B**: no hay un skill que gestione la mecánica de un test A/B real
  (variantes servidas, tracking de conversión, significancia estadística) — solo guías genéricas.
- **Design tokens ↔ Elementor**: hay Figma-to-code para React/Tailwind, pero nada que traduzca
  tokens de diseño directamente a la estructura JSON de Elementor (`_elementor_data`) — el puente
  falta y hoy lo cubren `header-footer`/`web-fidelidad-elementor` a mano, midiendo píxeles.
