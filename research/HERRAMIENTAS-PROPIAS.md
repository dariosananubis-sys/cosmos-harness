# Herramientas propias — extracción para COSMOS

Inventario de la cosecha en `cosecha/`: herramientas genéricas y limpias extraídas de los repos
propios de el responsable (`<la-agencia>-deploy`, `ClawArmy`, `seo-guardian`, `Chronos`, y el `tools/` local de
este workspace), para arrancar COSMOS sin partir de cero. Regla dura aplicada en todo el barrido:
**cero datos de cliente** — nombres reales, dominios, NIF, direcciones, credenciales, rutas de
vault, IPs de servidor o IDs de expediente. Lo que no se pudo limpiar sin destripar su lógica
central se descartó (ver `## Descartadas`).

Repos revisados, en el orden pedido: `<la-agencia>-deploy` (yo), `ClawArmy` (yo, descartado entero),
`seo-guardian` (yo), `Chronos` (yo), y `tools/` local dividido en 3: un tercio yo y dos clústeres en
paralelo (`cluster-A-webops-legal.md`, `cluster-B-automatizacion-infra.md`, en `research/scratch/`).

## Copiadas

### `tools/` local — mío (19)

| fichero | qué hace | de qué repo | nicho COSMOS | qué se limpió |
|---|---|---|---|---|
| `repomix-pack.sh` | Empaqueta un repo con `repomix` a un único fichero de contexto para pegar en un LLM | `tools/` | `conocimiento` | Ninguno (ya genérico) |
| `clean-gone-branches.sh` | Borra ramas locales cuyo remoto ya no existe (`git branch -vv \| grep gone`) | `tools/` | `sistemas` | Ninguno |
| `reap-claude-orphans.sh` | Mata procesos `claude` huérfanos (PPID=1) que sobreviven a una ventana cerrada | `tools/` | `sistemas` | Ninguno |
| `foto-cuadrar.py` | Recorta/encuadra capturas de pantalla a una región exacta antes de meterlas en contexto | `tools/` | `visibilidad` | Ninguno |
| `quota-peak.py` | Detecta el pico de consumo de cuota Claude en una ventana de tiempo desde los logs locales | `tools/` | `agentes` | Ninguno |
| `dedupe-daily-autocapture.py` | Deduplica capturas automáticas diarias por hash perceptual | `tools/` | `datos` | Ninguno |
| `gdoc-read.py` | Lee un Google Doc por API a texto plano, con auth por Service Account | `tools/` | `datos` | Ruta de la key parametrizada (`GOOGLE_SA_KEY_PATH`) |
| `gsheet_sa.py` | Cliente de Google Sheets vía Service Account (lectura/escritura de rangos) | `tools/` | `datos` | Ruta de la key parametrizada |
| `gsheets.py` | Cliente de Google Sheets vía OAuth de usuario (token cacheado) | `tools/` | `datos` | Ninguno (ya genérico) |
| `captura-ventana.py` | Captura una ventana concreta (no la pantalla entera) por nombre/PID, con fallback a región | `tools/` | `visibilidad` | Nombre de cliente en docstring de ejemplo eliminado |
| `modelos-fijar.py` | Fija qué modelo usa cada rol (Opus/Sonnet/Haiku) por variable de entorno, con validación | `tools/` | `agentes` | Ninguno |
| `claude-cuenta.sh` | Lanza Claude Code con una cuenta aislada (`CLAUDE_CONFIG_DIR` por cuenta), sin tocar el Keychain compartido de las demás | `tools/` | `agentes` | Reescrito para ser autocontenido (ver nota de dependencia abajo); bypass de permisos puesto en **off por defecto** (el original lo activaba por orden puntual de el responsable, no es un default genérico sano) |
| `bws-token-set.sh` | Guarda/rota el token de Bitwarden Secrets Manager en un `.env`, verificando que funciona antes de escribirlo | `tools/` | `custodia` | Ninguno |
| `gh-token-set.sh` | Guarda un token de GitHub en el credential helper de git + en un `.env` | `tools/` | `custodia` | Repo y `BWS_SECRET_ID` reales quitados, parametrizados |
| `mcp-call.py` | Cliente MCP genérico (stdio/HTTP) para invocar una tool suelta desde línea de comandos, sin un host completo | `tools/` | `agentes` | Ninguno |
| `barrido-transcripts.py` | Busca patrones en transcripts `.jsonl` de Claude Code (útil para auditar fugas o comportamiento) | `tools/` | `agentes` | Ninguno |
| `extract_frames.py` | Extrae N fotogramas equiespaciados de un vídeo con ffmpeg | `tools/` | `medios` | Ruta de salida parametrizada |
| `codex-delegate.sh` | Delega generación de código a Codex CLI, revisando el prompt antes de confirmar | `tools/` | `agentes` | Ninguno |
| `auditar-gasto.py` | Detecta fugas de cuota conocidas en la config del harness (rules sin `paths:`, MCP conectado sin uso...) | `tools/` | `agentes` | Ninguno |

**Nota de dependencia (`claude-cuenta.sh`):** el original llamaba a un `claude-cuenta.py` gestor de
cuentas de 1482 líneas. Ese fichero lo revisó el clúster B y lo descartó por estar entrelazado con
comentarios de incidentes reales (ver `## Descartadas`). Para no dejar `claude-cuenta.sh` roto
(llamando a un script que ya no existe en `cosecha/`), se reescribió para ser autocontenido: en vez
de subcomandos `lista`/`lanzar`/`relogin` de un gestor externo, hace los mismos checks in-line
(listar subcarpetas de sesión, comprobar que existen, pedir login manual si falta). La lógica
central que sí valía la pena (aislar `CLAUDE_CONFIG_DIR` por cuenta, no heredar variables de
sesión-hija, bypass de permisos opt-in) se conserva intacta.

### `<la-agencia>-deploy` — mío (7)

| fichero | qué hace | de qué repo | nicho COSMOS | qué se limpió |
|---|---|---|---|---|
| `log.py` | Helpers de logging con formato consistente (`step`/`ok`/`fail`/`info`/`api_call`/`api_response`) que usan el resto de wrappers de API de este lote | `<la-agencia>-deploy/lib` | `conocimiento` | Ninguno (ya genérico); se copia porque varios ficheros de abajo lo importan |
| `domain-suggester.py` | Sugiere dominios libres a partir de un nombre de negocio, consultando disponibilidad vía WHOIS/RDAP | `<la-agencia>-deploy/tools` | `negocio` | Ninguno |
| `gsc-search-console.py` | Wrapper CLI de Google Search Console + Site Verification (alta, token de verificación, submit sitemap, inspect URL) vía Service Account | `<la-agencia>-deploy/apis` | `visibilidad` | Ninguno (ya parametrizado por env) |
| `bing-webmaster.py` | Wrapper CLI de Bing Webmaster Tools API, con el gotcha documentado de que `SubmitFeed`/`SubmitUrl` devuelven `d:null` en éxito (no solo en fallo) | `<la-agencia>-deploy/apis` | `visibilidad` | Ninguno |
| `pagespeed-accessibility.py` | Wrapper CLI de PageSpeed Insights, filtra los audits de accesibilidad que fallan | `<la-agencia>-deploy/apis` | `visibilidad` | Ninguno |
| `google-chat-dm.py` | Manda DMs 1:1 por Google Chat desde un bot de Service Account, con caché de resolución de space | `<la-agencia>-deploy/apis` | `agentes` | Ninguno (ya parametrizado por env) |
| `backup-rsync-configs.sh` | Respalda por rsync (solo-añadir) un directorio de configs gitignored a un host remoto, con sanity-check de fichero mínimo y permisos 600/700 aplicados DESPUÉS del rsync | `<la-agencia>-deploy` | `custodia` | Ninguno (ya parametrizado por env: `SRC`/`REMOTE_HOST`/`REMOTE_DIR`) |

### `seo-guardian` — mío (6)

| fichero | qué hace | de qué repo | nicho COSMOS | qué se limpió |
|---|---|---|---|---|
| `gsc-service-account-token.js` | Acuña un access token OAuth de Service Account (JWT RS256 firmado a mano, sin `google-auth-library`) para cualquier API de Google | `seo-guardian/lib/gscToken.js` | `visibilidad` | Nombre genericizado (servía a GSC+GA4 con el mismo código; ahora explícito por parámetro `scope`) |
| `wp-rest-base.js` | Resuelve la URL base de la REST de un WordPress que no vive en la raíz del dominio (WP en subcarpeta) | `seo-guardian/lib/rest-base.js` | `web` | Dominio de cliente real del docstring sustituido por ejemplo genérico |
| `bws-secret-get.js` | Busca un secreto por `key` en uno o varios proyectos de Bitwarden Secrets Manager | `seo-guardian/lib/bws.js` | `custodia` | Dos UUID de proyecto reales → `BWS_PROJECT_IDS` (env, coma-separado); nombres de proyecto reales en comentarios genericizados |
| `wpcli-remote.sh` | Ejecuta wp-cli remoto probando binario+versión de PHP de Plesk en orden hasta encontrar uno ejecutable | `seo-guardian/tools/wpcli-remote.sh` | `web` | UUID de secreto BWS real → `SERVERS_MAP_SECRET_ID` (env); nombres de servidor/cliente reales del incidente documentado genericizados (se conserva la lección: un `wp` que es wrapper de shell puede pasarse a PHP y "funcionar" imprimiendo texto sin ejecutar nada) |
| `bootstrap-app-pass.py` | Automatiza la creación de una Application Password de WordPress: login headless con `agent-browser`, crea la password en `profile.php`, la guarda en BWS, la verifica por REST | `seo-guardian/tools/bootstrap-app-pass.py` | `web` | UUID de proyecto real → `BWS_PROJECT_ID` (env); ruta `src/<la agencia>/.env` (fallback específico del workspace) eliminada; dominio de ejemplo real del comentario del gotcha `/users/me` vs `/settings` genericizado; ruta de `sites.yaml` parametrizada |
| `save-app-pass.py` | Hermano de `bootstrap-app-pass.py` sin login: registra en BWS una Application Password creada a mano, verifica y borra el fichero temporal | `seo-guardian/tools/save-app-pass.py` | `web` | Atribución a una persona real + fecha del comentario eliminada; misma limpieza de rutas que su hermano |

### `Chronos` — mío, 9 ficheros extraídos y genericizados de un control-plane de orquestación de contenedores efímeros (sobre pg-boss + dockerode)

| fichero | qué hace | de qué repo | nicho COSMOS | qué se limpió |
|---|---|---|---|---|
| `docker-wait-with-timeout.js` | `container.wait()` de dockerode con límite duro: al vencer, mata el contenedor en vez de dejarlo colgado para siempre | `Chronos/src/wait-timeout.js` | `infraestructura` | Nombres de cola específicos del negocio (screenshots/justificaciones/directorios) quitados de los defaults; el caller pasa su propio `timeoutMs` |
| `docker-orphan-container-cleanup.js` | Decide qué contenedores "de job" parar/eliminar al arrancar (huérfanos de un proceso anterior que murió a mitad) | `Chronos/src/orphans.js` | `infraestructura` | Ninguno (ya dep-free y genérico) |
| `docker-job-log-markers.js` | Demux de frames de log de Docker + protocolo de marcadores `::PREFIX::{json}` para que un contenedor reporte metadatos/progreso por stdout sin API aparte | `Chronos/src/log-parse.js` | `infraestructura` | Prefijos `CHRONOS_META`/`CHRONOS_STEP` → `JOB_META`/`JOB_STEP` (configurables por parámetro) |
| `docker-ephemeral-runner.js` | Ciclo de vida completo de un contenedor efímero (create→start→wait-con-timeout→logs→demux→remove) + seguimiento de progreso en vivo, evitando la race condition de `AutoRemove` | `Chronos/src/container.js` (extracto) | `infraestructura` | Se extrajo SOLO el núcleo genérico (`runEphemeralContainer` + `followStepMarkers` + limpieza de huérfanos); se descartaron las 6 funciones de lanzamiento específicas del negocio (imágenes, redes, mounts y env vars reales) — ver Descartadas |
| `docker-secret-cookie-auth.js` | Login propio (página + cookie de sesión) para una UI web interna: password desde Docker secret-file, comparación en tiempo constante, sesiones aleatorias revocables (no un hash de la password como token), rate-limit de login por IP | `Chronos/src/auth.js` | `infraestructura` (también útil en `saas`) | Quitada la dependencia de `logo.js` (logo/marca real embebida); branding "Chronos"/"<la agencia>" → `APP_NAME`/`APP_SUBTITLE`/`APP_LOGO_URI` configurables por env, con defaults genéricos |
| `google-chat-oauth-notify.js` | DM a un equipo por Google Chat al terminar un job, usando OAuth de un usuario real (no Service Account) — refresca el token en cada llamada | `Chronos/src/notify.js` | `agentes` | Referencias a la cuenta/proyecto real del comentario ("claudio.<la-agencia>", "<la-agencia>-mail-drafter") genericizadas |
| `nif-cif-validator.js` | Normaliza un NIF/CIF español y resuelve el slug de una lista de negocios por NIF | `Chronos/src/nif.js` | `legal` | Referencia a "Omnia"/`config/businesses` del comentario genericizada |
| `input-validators.js` | Validadores puros de boundary: UUID, slug, URL https-only (anti-XSS en href), rango de lote, subcarpeta segura dentro de un mount (anti path-traversal, más robusto que `startsWith`) | `Chronos/src/validate.js` (subconjunto) | `infraestructura` | Se copiaron solo los validadores genéricos; se descartaron `MESES`/`FLUJOS`/`FLUJO_DISPLAY`/`validateJustificacion` — taxonomía específica del programa de subvención Kit Digital, no genérica |
| `pg-secret-file-connection.js` | Construye el connection string de Postgres desde un Docker secret-file (nunca una env var en claro, visible en `docker inspect`), con `DATABASE_URL` como override explícito para tests | `Chronos/src/db.js` (extracto) | `infraestructura` | Se extrajo solo `buildConnectionString`; se descartó el resto (CRUD de una tabla `jobs` con columnas específicas del negocio) |

### `tools/` local — clúster A, webops/legal (14) — informe completo: `research/scratch/cluster-A-webops-legal.md`

| fichero | qué hace | nicho COSMOS | qué se limpió |
|---|---|---|---|
| `wp-ssh.sh` | wp-cli remoto por SSH con ControlMaster (evita baneos fail2ban) y PHP seguro vía `eval-file` (nunca `wp eval` inline); consolida 6 scripts casi idénticos | `web` | Reescrito desde 0 a partir del patrón; dominio, rutas Plesk, nombres de variable y de cliente fuera; todo parametrizado |
| `wp_sql.py` | SQL remoto sobre WordPress con fallback a PHP+`$wpdb` si no hay cliente `mariadb` | `web` | Lógica de doble-script quitada; usa solo `wp-ssh.sh --sitio`; nombres de cliente fuera |
| `navegador_seguro.py` | Wrapper de seguridad sobre `agent-browser`: nunca reutiliza sesión ajena, verifica URL/viewport antes de fiarse de una medición | `web` / `pruebas` | Nombres de cliente del docstring → ejemplos genéricos |
| `wp-mcp-sync.py` | Registra un servidor MCP de Elementor por sitio de un índice JSON, con checks de seguridad (solo HTTPS, detecta credenciales de plantilla sin rellenar) | `agentes` | Ya limpio; `cliente_id` → `sitio_id` |
| `wp-mcp-stdio-bridge.sh` | Sirve por STDIO el MCP de Elementor usando el PHP del CLI del servidor cuando el del vhost es muy viejo | `agentes` | Dominio, credenciales y nombres de cliente fuera; 100% por env vars |
| `cookies_catalogo.py` | Catálogo de >60 patrones de cookies (WP, WooCommerce, Elementor, GA/Ads, Meta, TikTok...) → clasificación legal en castellano | `legal` | 3 comentarios con nombre de cliente → descripción genérica |
| `legales-bloque-cookies.py` | Mide servicios de terceros reales en el HTML, cruza con Complianz, escribe el bloque LSSI de forma idempotente | `legal` | Nombre de cliente genericizado; rutas aplanadas |
| `legales-bloque-rest.py` | Mismo bloque LSSI pero por REST (`wp-json`/`app_password`), para sitios sin SSH | `legal` | 3 dominios de cliente reales → genérico |
| `legales-crear-paginas.py` | Genera aviso legal (art. 10 LSSI) y política de cookies mínimos, idempotente | `legal` | Nombre de cliente eliminado |
| `legales-texto.py` | Sustitución literal de texto en página legal (clásico o Elementor), transporte comprimido | `legal` | NIF de ejemplo → placeholder ficticio `12345678Z` |
| `legales-cookies-complianz.py` | Rellena ficha de cada cookie en Complianz (finalidad/caducidad/titularidad) | `legal` | Nombre de cliente fuera; constante muerta eliminada |
| `legales-lssi.py` | Audita páginas legales publicadas contra LSSI (aviso legal + cookies) | `legal` | 4 dominios reales → placeholders |
| `legales-purga-servicios-complianz.py` | Deja en Complianz solo servicios realmente cargados (evita sobre-declarar heredado de plantilla) | `legal` | Nombre de cliente fuera |
| `woocommerce-verificar-catalogo.py` | Verifica catálogo WooCommerce completo (precio, comprable, imagen, categoría, variaciones) | `web` | Reescrito: orquestación por cliente (`<panel-interno>.sh`) fuera, solo la lógica de negocio genérica |

### `tools/` local — clúster B, automatización/infra (24) — informe completo: `research/scratch/cluster-B-automatizacion-infra.md`

| fichero | qué hace | nicho COSMOS | qué se limpió |
|---|---|---|---|
| `codex-handler.sh` | Delegado a Codex CLI con detección/reintento de error de cuota y validación post-generación del output | `agentes` | Ninguno |
| `ig-dl.sh` | Descarga de Instagram: cookie de sesión de Chrome/Firefox → yt-dlp → gallery-dl → scrape sin login, en cascada | `medios`/`extraccion` | Ninguno |
| `analyze-reel.sh` | Pipeline de reel: yt-dlp + ffmpeg + `mlx_whisper` local + 5 keyframes | `medios` | Ninguno |
| `semble-doctor.sh` | Instala `uv`/`semble`, purga entradas MCP `semble` duplicadas, reporta versión | `agentes` | Ruta de ejemplo genericizada |
| `install-open-interpreter-macos` | Instalador de Open Interpreter CLI con modelo gratis OpenRouter, guarda key en Keychain | `infraestructura`/`agentes` | Ninguno |
| `audit-harness.sh` | Valida el esquema de `feature_list.json` (SDD: campos, `acceptance` con `R<n>:`, `depends_on`, LEDGER) | `agentes` | Ninguno |
| `patch-claude-mem-hooks.sh` | Parchea 3 bugs documentados del plugin público `claude-mem` | `agentes` | Ninguno |
| `cc-history.sh` | Wrapper sobre `npx cchistory` para auditar el historial bash de Claude Code | `agentes` | Ninguno |
| `cdp-client.py` | Cliente Chrome DevTools Protocol por WebSocket hecho a mano (handshake+framing manual, sin deps); dump/load de cookies | `web`/`agentes` | Ninguno |
| `excepcion-codigo.py` | Pase de excepción de 24h para saltar un guard de "no tocar código nativo", con motivo y expiración | `agentes` | Slug de cliente → `<slug>`; atribución personal genericizada |
| `alcance.py` | Declara qué slugs de proyecto están autorizados en la tarea actual, bloquea escritura fuera de alcance | `agentes` | Slugs de cliente reales → genéricos |
| `telegram-bridge.py` | Bot de Telegram que reenvía mensajes a `claude -p` y devuelve la salida, con Markdown→Telegram-HTML | `agentes`/`automatizacion` | Branding y ruta de ejemplo genericizados; variable de token renombrada |
| `quota-oficial.py` | Consulta el endpoint oficial no documentado de cuota real Claude 5h/semanal, resuelve `CLAUDE_CONFIG_DIR` vía daemon activo, token OAuth de Keychain, backoff exponencial | `agentes` | Atribución personal y ruta de vault genericizadas |
| `multi-review.py` | Revisión de código multi-modelo en paralelo (Gemini + 2 modelos gratis OpenRouter), consenso con exit codes | `agentes` | Branding y ruta de ejemplo genericizados |
| `mandar-a-terminales.py` | Difunde texto a terminales VS Code hermanas por AppleScript, con hallazgos negativos documentados (`TIOCSTI`→`EPERM` en macOS) | `agentes` | Atribución personal genericizada |
| `mantener-sesiones-claude.sh` | Mantiene vivas N cuentas aisladas de Claude Code con una llamada Haiku mínima, checks de permisos 700/600 | `agentes`/`infraestructura` | Alias reales → variable configurable; ruta de vault genericizada |
| `medir-contexto-claude.py` | Báscula de coste de contexto: parsea transcripts dedupe por `requestId`, coste equivalente de caché | `agentes` | Ruta hardcodeada → derivada dinámicamente; branding genericizado |
| `acceso-remoto-watchdog.sh` | Vigila cada 5 min SSH/Screen Sharing/Tailscale y los reactiva; documenta el gotcha de Tailscale SSH interceptando el puerto 22 | `infraestructura` | Hostname, comentario de incidente y ruta genericizados |
| `auto_resume.ps1` | PowerShell: reenfoca VS Code y envía teclas a hora programada para reanudar sesión colgada | `agentes`/`infraestructura` | Branding genericizado |
| `actualizacion-nocturna-mac.sh` | `pmset`+`softwareupdate` para actualizaciones nocturnas desatendidas, con guardarraíl de Time Machine | `infraestructura` | Referencias personales y disco de ejemplo genericizados |
| `setup-mac.sh` | Setup idempotente Apple Silicon: `stats`+`topgrade`, limpia Homebrew, LaunchAgent quincenal | `infraestructura` | Label de LaunchAgent genericizado |
| `install-modifier-swap.sh` | Intercambia Command↔Option en teclado externo vía `hidutil`, autodetecta Vendor/ProductID | `infraestructura` | Label de LaunchAgent genericizado |
| `enviar-correo-smtp.py` | Envío SMTP (SSL/STARTTLS) + copia por IMAP a Enviados (necesario en proveedores que no la generan solos) | `automatizacion` | Nombre/dominio reales y ruta de credenciales genericizados |
| `claude-code/` (8 ficheros: `run-smart.sh`, `run-balanced.sh`, `run-low.sh`, `run-pro.sh`, `run-strict.sh`, `mcp-servers.full.json`, `mcp-servers.min.json`, `README.md`) | Familia de lanzadores de `claude` con presets de coste/esfuerzo y clasificador heurístico tarea→modelo; toggle de config MCP mínima/completa | `agentes` | Ninguno (ya genérico); se omitió `tmux/` por falta de tiempo para revisarlo |

**Total copiadas: 79** (19 + 7 + 6 + 9 + 14 + 24).

## Descartadas

### Repos enteros

- **`ClawArmy`** (repo completo): fork de un proyecto OSS público con licencia MIT + una capa de negocio propietaria fina encima (`bin/empresa-*`). La parte genérica ya está pública en el proyecto original; la parte propietaria no es separable ni reutilizable fuera de ese negocio concreto. Se descarta el repo entero en vez de minarlo parcialmente.

### `<la-agencia>-deploy`

- `progress/` (184 MB) y `docs/` (22 MB): saturados de nombres de cliente en la propia estructura de directorios/ficheros (nunca se abrió su contenido — el listado ya lo delataba).
- `wpcli/gen_llms_txt.py`: depende de `lib/creds.py` (`SERVERS_MAP` respaldado por BWS); docstring con dominios de cliente reales de referencia.
- `tools/set_site_icon.py`: depende de `lib.client`/`lib.provision.dest_conn` (BWS/SSH) y `wpcli.deployer._wp`; no autocontenido.
- `lib/client.py`: esquema Pydantic de ficha de cliente, demasiado acoplado a la infraestructura bespoke (Plesk/IONOS/Hostalia) para ser un "esquema genérico" reutilizable sin reescritura.
- `apis/chat.py` — comando `ping()` original: eliminado de la copia (no todo el fichero) por contener bromas personales sobre compañeros reales nombrados; el resto del fichero (`google-chat-dm.py`) sí se copió limpio.

### `seo-guardian`

- `lib/` motor de contenido (`writer.js`, `publisher.js`, `run.js`, `checks/`, `calendar.js`, `config.js`, `sites.js`, `topic.js`, `verify.js`, `schedule.js`, `notify.js`, `report/`, `apply/`, `collect/`, `issue/`, `history/`, `correo.js`+prompt, `lectura.js`+prompt, `firmas-cambio.js`, `image.js`, `schema/`): motor de negocio completo de blogs mensuales por cliente, acoplado a YAML de sitios/calendarios reales y prompts con tono de cliente. No es una herramienta genérica sino el producto entero; no separable sin vaciar su lógica.
- `config/calendars/`, `config/seo-sites.yaml`, `config/sites.yaml`, `data/backups/`, `data/cambios/`, `data/corpus-humano.ref`, `data/correos-ref/`, `data/history/`, `data/lecturas/`: datos de cliente por convención de directorio (nunca abiertos).
- `tools/catchup-2026-07.csv`, `tools/catchup-styledogs-2026-07.csv`: el segundo lleva nombre de cliente en el propio nombre de fichero; ninguno es código.
- `tools/run-catchup.sh`: solo dispara `bin/run-site.mjs`, parte del motor de negocio descartado arriba — sin él no es ejecutable.

### `Chronos`

- `index.js`: entrypoint del propio Chronos, glue code atado a sus colas y workers específicos (screenshots/justificaciones/directorios); no es una herramienta reutilizable aislada.
- `server.js` (500 líneas): servidor HTTP con endpoints y HTML de UI 100% específicos del proceso de negocio Kit Digital (capturas/justificaciones/directorios); no revisado línea a línea por juicio de patrón ya confirmado en ficheros hermanos.
- `worker.js`: registra workers atados a `container.js` (imágenes/negocio específicos) y `db.js` (tabla `jobs` específica); glue, no herramienta aislada.
- `just-status.js`: taxonomía de estados de "justificación" específica del programa Kit Digital.
- `logo.js`: logo real de la agencia en base64 — asset de marca, no una herramienta.
- `omnia-adapters.js`: allowlist anti-inyección de una lista fija de directorios de negocio (citiservi, hotfrog...) — patrón demasiado fino/específico para justificar un fichero aparte (el principio general de "nunca aceptar un valor externo sin contrastarlo contra una allowlist" ya queda documentado como advertencia en `docker-ephemeral-runner.js`).
- `container.js` (resto, tras extraer `docker-ephemeral-runner.js`): las 6 funciones de lanzamiento (`runScreenshotsJob`, `runJustificacionesJob`, `runDirectoriosJob`, `listOmniaBusinesses`, `listPendingRows`, `listPendingClients`) tienen nombres de imagen, red, volumen, rutas de secret-file y hasta un ID de proyecto GCP real hardcodeados — no genéricas.
- `db.js` (resto, tras extraer `pg-secret-file-connection.js`): CRUD de la tabla `jobs` con columnas específicas del negocio (`domain`, `razon_social`, `drive_url`) y su máquina de estados particular.
- `validate.js` (resto, tras extraer `input-validators.js`): `MESES`/`FLUJOS`/`FLUJO_DISPLAY`/`validateJustificacion` — taxonomía del programa de subvención Kit Digital, no genérica.
- `progress/` (11 MB) y `assets/` (1 MB): histórico de trabajo específico y assets de marca; no código.

### Clúster A (`tools/` local, webops/legal) — detalle en `research/scratch/cluster-A-webops-legal.md`

- `hwp.sh`, `hwp-php.sh`, `hwp-cliente.sh`, `hwp-identity.sh`, `hwp-identity-php.sh`, `hwp-<cliente>.sh`: 5-6 copias casi idénticas del mismo patrón SSH+wp-cli con dominio y credenciales `PANEL_SSH_*` hardcodeadas (una lleva literalmente el nombre de un cliente). Consolidadas en el único `wp-ssh.sh` genérico ya copiado.
- `web-checkpoint.py`, `web-contrato.py`, `web-contrato-produccion.py`, `web-gate.py`, `web-sin-codigo.py`, `webs-estado.py`, `mockup-html.py`, `gate_render.py`: motor interno de QA/gate de la agencia, atado a convenciones propias y con dominios de cliente reales incrustados en el propio código (no solo comentarios); no separable sin reescribir el motor entero.
- `migra-customcss-nativo.py`: depende de volcados internos y esquema MCP propio; docstring con nombres de cliente reales.
- `generar-logos-popup.py`: generador de iconos del popup interno de la propia agencia; sin valor genérico fuera de ese contexto.
- `verificar-catalogo.py` (original): sustituido por `woocommerce-verificar-catalogo.py`, ya limpio.
- `mockup-header.py` (local, mío): nombres de proyecto de cliente en código, dominio propio hardcodeado, depende de `navegador_seguro.py` + convención interna `progress/gates/`.
- `web-foto.py` (local, mío): docstring con nombre de cliente real en una narrativa de incidente; depende de skill externa + `~/.wp-sites/sites.json` + dominio propio.

### Clúster B (`tools/` local, automatización/infra) — detalle en `research/scratch/cluster-B-automatizacion-infra.md`

- `check-backups-webroot.py`: identificadores del parque de servidores propio (`PLESK=[...]`, `HESTIA=[...]`) inseparables.
- `selector-modelo.py`/`elegir-modelo.py`: no funcionales sin el "motor" no cosechado (`ask-popup.py`, `llm-providers/registry.py`, logos).
- `web-diff-visual.py`: algoritmo valioso pero `BASE` de dominio propio y comentarios de proyectos de cliente entrelazados.
- `preguntar.py`: no funcional sin `ask-popup.py`.
- `espera-tareas.py`: depende de `preguntar.py`/`ask-popup.py` y del lenguaje de flujo de un usuario concreto.
- `generar-agents-md.py`: la plantilla de salida embebe ~200 líneas de política específica (nombre, IP de producción, buzón, reglas propias); el patrón de introspección queda anotado como valioso para el futuro.
- `wp_acceso.py`: dominios de cliente reales inseparables (son la explicación de cada excepción).
- `dashboard/` + `dashboard-chorus/` (44 ficheros): fork de un proyecto OSS de terceros ("Chorus") ya vendorizado completo — no es IP propia.
- `skill-seekers/` (55 ficheros): repo OSS de terceros vendorizado completo.
- `claude-cuenta.py` (1482 líneas): patrón valioso (multicuenta Claude Code aislada por `CLAUDE_CONFIG_DIR`) pero comentarios de incidentes reales entrelazados en toda la lógica y acoplado al daemon propio; el núcleo ya queda cubierto, más ligero, por `mantener-sesiones-claude.sh` y `quota-oficial.py` (ver nota de dependencia sobre `claude-cuenta.sh` en Copiadas).
- `repartir-trabajo.py` (1084 líneas): orquestador atado al daemon propio, reglas de cuota personales incrustadas como constantes.
- `supervisor-tick.py` + `supervisor-tick-instalar.sh`: depende de la API del daemon propio; patrón (reloj externo en vez de auto-sondeo) anotado como valioso para referencia futura.
- `analizador_masivo.py`/`analizador_masivo_local.py`: solapa con `analyze-reel.sh` ya copiada; ruta Windows hardcodeada y docstring con razón de facturación de un socio.
- `trello.py`, `trello_from_mail.py`, `trello-watcher/`: convenciones de negocio de un socio entrelazadas; ficheros grandes ya marcados con buzones reales.
- `generar-presupuesto-lib.js`, `generar-presupuesto.js`, `presupuesto-google-sheets.gs`: lógica de precios propia de la agencia.
- `relogin-cuenta.sh`, `anadir-cuenta.sh`: companions de `claude-cuenta.py` descartado.
- `claudeclaw-*` (compactar/daemon/limpiar-sesiones/reiniciar-libre), `claw-broadcast.py`, `claw-watch.py`, `claw/claw.py`, `claw/tarea.py`: subsistema atado al daemon propio ClaudeClaw.
- `mac2-*` (6 ficheros): configuración específica del setup de dos Macs propio (hostnames, IPs, cuentas).
- `abrir-claudeclaw.sh`, `abrir-panel-publisher.sh`: lanzadores de infraestructura propia.
- `creds-vnc.sh`: credenciales de VNC propias.
- `avisar-dario.sh`: notificador personal dirigido a una persona concreta.
- `claudeclaw-ui/` (12 ficheros): companion de una app ya marcada como contaminada.
- `intel-routine/`: automatización de rutina de inteligencia propia del negocio.
- `launchagents/` (4 plist): rutas y labels `com.<la-agencia>.*` concretos; el patrón LaunchAgent en sí es doc estándar de Apple, no aporta como extracto.
- `mailwatch.sh`: toggle de un workflow de GitHub Actions concreto (`REPO="<la agencia>/mail-watch"`).
- `mail-mac-configurar.py`: técnica de fondo valiosa (perfil `.mobileconfig` para provisionar Mail.app) pero lógica de dos cuentas entrelazada con nombre/organización reales.
- `claude-code/tmux/`: no revisado a fondo por límite de tiempo; se deja fuera para no copiar sin verificar.

## Joyas

Las 5 herramientas de más valor para arrancar un harness genérico, y por qué:

1. **`docker-secret-cookie-auth.js`** (de `Chronos/src/auth.js`) — auth de cookie-sesión para un
   panel web interno sin ningún framework: password desde Docker secret-file (nunca env, que se
   filtra en `docker inspect`), comparación en tiempo constante, sesiones ALEATORIAS revocables de
   verdad (no un hash de la password como token — el bug clásico que hace que copiar la cookie
   equivalga a robar la contraseña para siempre), y rate-limit de login por IP. Cualquier proyecto
   de COSMOS que necesite un panel de administración mínimo parte de aquí en vez de reinventarlo mal.

2. **`docker-ephemeral-runner.js` + `docker-wait-with-timeout.js` + `docker-job-log-markers.js`**
   (de `Chronos/src/container.js`+`wait-timeout.js`+`log-parse.js`) — el núcleo de "un job = un
   contenedor efímero" bien resuelto: evita la race condition de `AutoRemove` (logs leídos ANTES
   del remove), pone límite duro a `container.wait()` (sin él, un contenedor colgado congela una
   cola entera sin auto-recuperación), y define un protocolo mínimo de progreso en vivo por stdout
   (`::PREFIX::{json}`) sin necesitar una API/socket adicional. Es infraestructura de agentes real,
   ya probada en producción con sus tres bugs (F-1/F-3/F-5) documentados y corregidos.

3. **`wp-ssh.sh`** (consolidado de 6 scripts casi idénticos del clúster A) — wp-cli remoto por SSH
   con ControlMaster (evita baneos de fail2ban por reconectar en cada llamada) y ejecución de PHP
   SIEMPRE vía fichero (`eval-file`), nunca `wp eval` con una cadena interpolada — el patrón que
   evita inyección de comandos al construir el argumento. Cualquier tool de COSMOS que gestione
   WordPress remoto puede montarse encima sin repetir ese error.

4. **`bootstrap-app-pass.py` + `save-app-pass.py`** (de `seo-guardian`) — automatiza por completo el
   punto más manual de integrar con la REST de WordPress: crear una Application Password. Login
   headless, creación en `profile.php`, guardado en un gestor de secretos, y verificación contra
   `/wp/v2/settings` en vez de `/users/me` — con el gotcha real documentado de que algunas webs
   capan la enumeración de usuarios y devuelven 403 aunque la credencial sea válida. Ahorra la
   sesión entera de "por qué no me deja crear la Application Password por API" (WordPress no
   expone esa creación por REST — solo por UI — así que hay que automatizar la UI).

5. **`quota-oficial.py`** (clúster B) — la única forma documentada de consultar la cuota REAL de
   Claude Code (5h/semanal) contra el endpoint oficial no documentado `GET /api/oauth/usage`,
   resolviendo el `CLAUDE_CONFIG_DIR` activo vía el daemon y leyendo el token OAuth directamente del
   Keychain. Sin esto, cualquier tooling de gestión de cuota tiene que adivinar o hacer scraping de
   la UI; con esto, es una llamada HTTP con backoff.

## Barrido de contaminación

Comando ejecutado sobre el `cosecha/` final (79 ficheros, tras las dos rondas de limpieza de los
clústeres A y B y la mía propia):

```
grep -rniE "<la-agencia>|<la-agencia>|dario|@gmail|@<la-agencia>|[0-9]{8}[A-Z]|ghp_|sk-|BEGIN [A-Z ]*PRIVATE KEY|password *=|token *=" /Users/<usuario>/cosmos/cosecha/ | head -40
```

Salida literal:

```
/Users/<usuario>/cosmos/cosecha/bws-token-set.sh:30:if ! BWS_ACCESS_TOKEN="$TOK" bws secret list -o json >"$TMP_OUT" 2>"$TMP_ERR"; then
/Users/<usuario>/cosmos/cosecha/bws-token-set.sh:47:    if l.startswith("BWS_ACCESS_TOKEN="):
/Users/<usuario>/cosmos/cosecha/bws-token-set.sh:49:        lineas[i] = f"BWS_ACCESS_TOKEN={tok}{fin}"
/Users/<usuario>/cosmos/cosecha/bws-token-set.sh:53:    lineas.append(f"\nBWS_ACCESS_TOKEN={tok}\n")
/Users/<usuario>/cosmos/cosecha/gh-token-set.sh:40:printf 'protocol=https\nhost=github.com\nusername=%s\npassword=%s\n\n' "$LOGIN" "$TOKEN" \
/Users/<usuario>/cosmos/cosecha/gh-token-set.sh:50:    if l.startswith("GITHUB_TOKEN="):
/Users/<usuario>/cosmos/cosecha/gh-token-set.sh:51:        l, visto["GITHUB_TOKEN"] = f"GITHUB_TOKEN={token}", True
/Users/<usuario>/cosmos/cosecha/gh-token-set.sh:55:if not visto["GITHUB_TOKEN"]: lineas.append(f"GITHUB_TOKEN={token}")
/Users/<usuario>/cosmos/cosecha/legales-crear-paginas.py:10:        --nif 12345678Z --domicilio "Calle X, 1, 28001 Madrid" \\
/Users/<usuario>/cosmos/cosecha/gsc-search-console.py:141:    token = get_meta_token(site_url)
/Users/<usuario>/cosmos/cosecha/install-open-interpreter-macos:29:[[ "$api_key" == sk-or-v1-* ]] || { print -u2 "Formato de clave no válido."; exit 1; }
/Users/<usuario>/cosmos/cosecha/wp-mcp-sync.py:63:    token = base64.b64encode(f"{usuario}:{clave}".encode()).decode()
/Users/<usuario>/cosmos/cosecha/pg-secret-file-connection.js:23:  const password = fs.readFileSync(pwFile, 'utf8').trim();
/Users/<usuario>/cosmos/cosecha/google-chat-oauth-notify.js:78:    const token = loadJson('GCHAT_TOKEN', 'GCHAT_TOKEN_FILE', '/run/secrets/gchat_token');
/Users/<usuario>/cosmos/cosecha/google-chat-oauth-notify.js:79:    const accessToken = await refreshAccessToken(creds, token);
/Users/<usuario>/cosmos/cosecha/legales-texto.py:10:        --buscar "Identificador fiscal: ES 12345678Z" \\
/Users/<usuario>/cosmos/cosecha/legales-texto.py:11:        --sustituir "NIF: 12345678Z" --aplicar
/Users/<usuario>/cosmos/cosecha/bootstrap-app-pass.py:144:    token = base64.b64encode(f'{user}:{app_pass}'.encode()).decode()
/Users/<usuario>/cosmos/cosecha/bootstrap-app-pass.py:170:        url, user, password = creds.get('url'), creds.get('user'), creds.get('pass')
/Users/<usuario>/cosmos/cosecha/barrido-transcripts.py:46:    r"This session is being continued|<task-notification|\[Image)")
/Users/<usuario>/cosmos/cosecha/docker-secret-cookie-auth.js:40:const PASSWORD = loadPassword();
/Users/<usuario>/cosmos/cosecha/docker-secret-cookie-auth.js:80:  const token = crypto.randomBytes(32).toString('hex');
/Users/<usuario>/cosmos/cosecha/docker-secret-cookie-auth.js:165:  const token = createSession();
/Users/<usuario>/cosmos/cosecha/docker-secret-cookie-auth.js:362:    const password = extractPassword(body, req.headers['content-type'] || '');
/Users/<usuario>/cosmos/cosecha/gsheets.py:40:    creds = Credentials(token=_token())
/Users/<usuario>/cosmos/cosecha/gsheets.py:74:            pageSize=200, pageToken=page).execute()
/Users/<usuario>/cosmos/cosecha/telegram-bridge.py:18:BOT_TOKEN      = os.environ.get("TELEGRAM_BOT_TOKEN", "")
/Users/<usuario>/cosmos/cosecha/telegram-bridge.py:31:        print("Ejecuta: set TELEGRAM_BOT_TOKEN=tu_token_aqui")
```

Veredicto: **sin aciertos reales**. Todo lo listado es (a) nombres de variable genéricos
(`token =`, `password =`, `*_TOKEN=`) propios de cualquier wrapper de credenciales/auth, (b) los
dos placeholders de NIF explícitamente ficticios `12345678Z` (usados a propósito como ejemplo en
docstrings, ya señalados como seguros por el clúster A), y (c) un validador de FORMATO de API key
(`sk-or-v1-*`) que comprueba un prefijo, no una clave embebida. Ningún nombre real de cliente,
dominio, email, NIF real, credencial ni ruta de vault sobrevive en `cosecha/`.
