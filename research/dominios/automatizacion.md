# Automatización — que lo repetitivo se haga solo

Barrido GitHub para COSMOS, nicho 17 (`automatizacion`). Cubre: motores de flujos self-hosted,
tareas programadas y colas, integración entre servicios, automatización de escritorio y RPA,
vigilancia de cambios, y disparadores por evento (webhooks).

**Método**: API de GitHub autenticada (`search/repositories` + `repos/{owner}/{repo}`), cupo de
WebSearch agotado. Consultas espaciadas ~3s para evitar el 403 de rate-limit del endpoint `search`
(30/min). Fecha del barrido: 2026-09-01. Toda cifra de este informe fue confirmada en vivo esa fecha
(estrellas, licencia, `archived`, `pushed_at`); lo que no, va marcado `NO VERIFICADO`.

**Criterio propio del encargo**: gana lo que se recupera de un fallo — reintentos, idempotencia,
cola muerta. Una automatización que falla en silencio a las 3 de la mañana es peor que no tenerla.

---

## De primera

1. **[n8n-io/n8n](https://github.com/n8n-io/n8n)** — 203k★, licencia fair-code (no OSI puro,
   `NOASSERTION`), `pushed_at` de hoy, activísimo. **Por qué gana**: es el motor de flujos
   self-hosted más grande del ecosistema — 400+ integraciones, visual + código propio en cada nodo,
   self-host sin coste. Tiene workflows de error dedicados (`Error Trigger`) y reintento configurable
   por nodo: exactamente el criterio de "recuperarse de un fallo" que pide el encargo. Es también el
   más documentado y con más comunidad para resolver el edge-case raro a las 3 de la mañana.

2. **[windmill-labs/windmill](https://github.com/windmill-labs/windmill)** — 17.7k★, `NOASSERTION`
   pero código abierto, `pushed_at` de hoy. **Por qué gana su hueco**: alternativa developer-first a
   n8n — convierte scripts (Python/TS/Go/Bash) en webhooks, flujos y UIs, con motor propio que se
   anuncia 13x más rápido que Airflow en sus benchmarks. Gana cuando el automatismo es más código que
   clic-y-arrastra: versionado real de scripts, tipado, tests.

3. **[node-red/node-red](https://github.com/node-red/node-red)** — 23.6k★, Apache-2.0, `pushed_at`
   de hoy. **Por qué gana**: es el motor de referencia para integración con hardware/IoT (miles de
   nodos de comunidad para dispositivos, protocolos serie, MQTT) — un hueco que n8n/windmill no
   cubren igual de bien. Proyecto de la OpenJS Foundation, maduro desde 2013 y aún con commits diarios.

4. **[huginn/huginn](https://github.com/huginn/huginn)** — 49.9k★, MIT, `pushed_at` 2026-08-29.
   **Por qué gana**: "crea agentes que vigilan y actúan en tu nombre" — es el proyecto que mejor
   combina vigilancia de cambios + disparo de acción en un solo agente encadenable (RSS, scraping,
   webhooks de salida). Rails, arquitectura más vieja que las alternativas modernas, pero sigue vivo
   y sin sustituto directo con la misma flexibilidad de "agente que observa y reacciona".

5. **[kestra-io/kestra](https://github.com/kestra-io/kestra)** — 28.0k★, Apache-2.0, `pushed_at` de
   hoy. **Por qué gana**: orquestación declarativa (YAML) orientada a evento, para "aplicaciones
   críticas" — retries, triggers por evento/cron/webhook y backfill nativos. Gana frente a Airflow
   cuando se quiere el mismo rigor de orquestación sin la complejidad operativa de Airflow (menos
   piezas de infra, arranque en un solo contenedor).

6. **[celery/celery](https://github.com/celery/celery)** — 28.8k★, `NOASSERTION` (BSD histórico),
   `pushed_at` de hoy. **Por qué gana**: el estándar de facto de colas de tareas distribuidas en
   Python — reintentos con backoff, ack tardío, colas muertas vía `task_reject_on_worker_lost` +
   brokers con DLQ. Es la pieza que se elige cuando "colas" significa infraestructura de producción,
   no un flujo visual.

7. **[dgtlmoon/changedetection.io](https://github.com/dgtlmoon/changedetection.io)** — 33.4k★,
   Apache-2.0, `pushed_at` 2026-08-31. **Por qué gana**: es LA herramienta de vigilancia de cambios
   web — detecta cambios de contenido/precio/stock en cualquier página, con filtros CSS/XPath,
   captura visual y notificación (webhook, email, Telegram…) al disparo. Sin rival con esa
   combinación de simplicidad + potencia de filtrado en el hueco "vigilancia de cambios".

8. **[Hammerspoon/hammerspoon](https://github.com/Hammerspoon/hammerspoon)** — 16.0k★, MIT,
   `pushed_at` 2026-07-08. **Por qué gana**: automatización de escritorio nativa de macOS vía Lua —
   controla ventanas, atajos globales, eventos del sistema, WiFi, batería. Es la vía directa para
   automatizar la propia máquina (Darío usa macOS) sin capas de terceros ni coste.

9. **[robocorp/rpaframework](https://github.com/robocorp/rpaframework)** — 1.6k★, Apache-2.0,
   `pushed_at` 2026-08-29. **Por qué gana su hueco**: RPA en Python real (no low-code de pago) sobre
   Robot Framework — librerías para Excel, PDF, correo, navegador, Windows/desktop. Frente a
   `open-rpa/openrpa` (GUI completa, más pesado de desplegar) gana cuando el RPA se quiere como
   código versionable e integrado en CI, no como aplicación aparte.

10. **[taskforcesh/bullmq](https://github.com/taskforcesh/bullmq)** — 9.4k★, MIT, `pushed_at` de
    hoy. **Por qué gana**: cola de trabajos sobre Redis o Postgres con reintentos, backoff
    exponencial, *flows* (DAGs de jobs) y trabajos retrasados, con soporte multi-lenguaje (Node,
    Python, .NET, Elixir, Rust, PHP) desde el mismo broker. Con `bull-board` (compañero del mismo
    autor) da panel visual de la cola muerta — el criterio de "verse el fallo" en la práctica.

---

## Segunda fila

- **[activepieces/activepieces](https://github.com/activepieces/activepieces)** — 24.2k★,
  `NOASSERTION`, activo hoy. Alternativa a n8n muy volcada en MCP/agentes de IA (~400 servidores MCP
  listos). Se queda en segunda fila porque n8n cubre el mismo hueco con más madurez e integraciones.
- **[apache/airflow](https://github.com/apache/airflow)** — 46.7k★, Apache-2.0, activo hoy. El
  orquestador DAG de referencia de la industria — reintentos, SLA, alertas, backfill. Pesado de
  operar (scheduler + workers + metastore); Kestra cubre el mismo problema con menos infraestructura.
- **[dagucloud/dagu](https://github.com/dagucloud/dagu)** — 3.8k★, GPL-3.0, activo hoy. Orquestador
  YAML autohospedable ligero, sin base de datos externa — buen punto medio entre un cron y Airflow
  para equipos pequeños.
- **[hatchet-dev/hatchet](https://github.com/hatchet-dev/hatchet)** — 7.8k★, MIT, activo hoy. Motor
  de orquestación para tareas en segundo plano y agentes de IA con ejecución duradera — más joven que
  Celery/BullMQ, a vigilar.
- **[sidequestjs/sidequest](https://github.com/sidequestjs/sidequest)** — 1.0k★, LGPL-3.0, activo
  2026-08-27. Alternativa a BullMQ **sin Redis** — persiste en Postgres/MySQL/SQLite/MongoDB que ya
  se tenga desplegado; dashboard incluido.
- **[coleifer/huey](https://github.com/coleifer/huey)** y **[rq/rq](https://github.com/rq/rq)** —
  6.0k★ MIT / 10.7k★ `NOASSERTION`, ambos activos hoy. Colas de tareas Python más ligeras que Celery
  (menos piezas móviles) cuando no hace falta toda su potencia.
- **[mher/flower](https://github.com/mher/flower)** — 7.2k★, monitor web en tiempo real para Celery
  — el panel que le falta a Celery de fábrica.
- **[open-rpa/openrpa](https://github.com/open-rpa/openrpa)** — 3.1k★, MPL-2.0, activo 2026-04-15.
  RPA de escritorio con GUI completa (grado empresarial); más pesado que `rpaframework` pero cubre
  el caso "usuario no-programador construye el flujo".
- **[octalmage/robotjs](https://github.com/octalmage/robotjs)** — 12.8k★, MIT, activo 2026-08-07.
  Control de ratón/teclado/pantalla nativo desde Node.js — la pieza de bajo nivel cuando el RPA hay
  que escribirlo a medida.

## Humo

- **[z8run/z8run](https://github.com/z8run/z8run)** — motor visual de flujos en Rust+React,
  autohospedado, alternativa joven a n8n/Node-RED (32★).
- **[flowbaker/flowbaker](https://github.com/flowbaker/flowbaker)** — motor de ejecución de un
  constructor de flujos no-code (204★).
- **[PremoWeb/chadburn](https://github.com/PremoWeb/chadburn)** — alternativa a cron para Docker,
  en Go (78★).
- **[ManiMozaffar/aioclock](https://github.com/ManiMozaffar/aioclock)** — programador Python
  moderno con inyección de dependencias, alternativa a APScheduler/Rocketry (242★).
- **[janbjorge/pgqueuer](https://github.com/janbjorge/pgqueuer)** — cola de tareas Python sobre
  Postgres, sin Redis (1.5k★).
- **[nanobrowser/nanobrowser](https://github.com/nanobrowser/nanobrowser)** — extensión Chrome de
  automatización web multi-agente con tu propia API key de LLM (13.7k★).
- **getmaxun/maxun** (17.3k★) apareció en "rpa open source" pero es scraping/extracción
  estructurada, no RPA — pertenece al nicho `extraccion`, no a este.

---

## Mapeo a COSMOS

```
sistema-solar  automatizacion
├── continente  orquestacion
│   ├── pais  flujos-visuales        n8n · windmill · node-red · activepieces
│   └── pais  flujos-declarativos    kestra · airflow · dagu
├── continente  colas-y-programacion
│   ├── pais  colas-de-tareas        celery · bullmq · rq · huey · sidequest
│   └── pais  programadores          alternativas a cron, aioclock, chadburn
├── continente  vigilancia-y-eventos
│   ├── pais  vigilancia-de-cambios  changedetection.io · huginn
│   └── pais  disparadores-webhook   webhooks nativos de n8n/kestra/changedetection
├── continente  escritorio-y-rpa
│   ├── pais  automatizacion-mac     hammerspoon
│   └── pais  rpa                    rpaframework · openrpa · robotjs
└── continente  codigo-automatizacion   ← el código propio del nicho
       provincias: nodos/conectores a medida (n8n custom nodes, scripts windmill),
       recetas YAML de dagu/kestra, receptores de webhook propios, workers de cola con
       reintento e idempotencia escritos a mano
```

## Lo que falta

- No hay un ganador claro y vivo de "RPA de escritorio moderno para Windows" fuera de OpenRPA
  (grado empresarial pero con menos tracción reciente que los de flujos visuales); si el cliente
  necesita RPA de escritorio Windows específicamente, revisar en 3 meses.
- El hueco "cron moderno con UI y alertas" está fragmentado en proyectos pequeños (chadburn,
  aioclock, skedule) sin un ganador consolidado — Kestra/Dagu lo resuelven mejor si se acepta un
  motor de flujos completo en vez de "solo un cron mejor".
- Huginn es la mejor pieza de "vigilancia + acción combinadas" pero su base Rails está más
  estancada que el resto del hueco; si aparece un sucesor moderno con la misma flexibilidad de
  agentes encadenables, revisar.
