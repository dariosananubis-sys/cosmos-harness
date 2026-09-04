## Copiadas

| fichero | qué hace | nicho COSMOS | qué se limpió |
|---|---|---|---|
| codex-handler.sh | Delegado a Codex CLI con detección/reintento de error de cuota y validación post-generación del output (CSS prohibido, `export default`, estructura de módulo) | agentes | Ninguno (ya genérico) |
| ig-dl.sh | Descargador de Instagram: detecta cookie de sesión viva en Chrome/Firefox (sqlite3 modo solo-lectura), yt-dlp → gallery-dl → scrape de embed sin login como fallback en cascada | medios / extraccion | Ninguno (100% genérico) |
| analyze-reel.sh | Pipeline de reel: yt-dlp + ffmpeg (audio) + mlx_whisper (transcripción local, base/large-v3) + 5 keyframes equiespaciados | medios | Ninguno (100% genérico) |
| semble-doctor.sh | Instala `uv`/`semble`, purga cualquier entrada MCP `"semble"` de `~/.claude.json` (fuerza uso por CLI), reporta versión + fugas MCP | agentes | Ruta de ejemplo `./src/<la agencia>/<la-agencia>-assets` → `./src/mi-proyecto` |
| install-open-interpreter-macos | Instalador autoinstalable de Open Interpreter CLI con modelo gratuito de OpenRouter (DeepSeek); guarda la API key en Keychain, se autocopia a `~/.local/bin` | infraestructura / agentes | Ninguno (usa `$USER` genérico) |
| audit-harness.sh | Valida el esquema de `feature_list.json` (patrón SDD: campos obligatorios, `acceptance` con prefijo `R<n>:`, `depends_on` resuelto, LEDGER si `status=done`) en cualquier repo con `src/*/` o `projects/*/` | agentes | Ninguno (100% genérico, POSIX sh puro) |
| patch-claude-mem-hooks.sh | Parchea 3 bugs reales y documentados del plugin público `claude-mem` (hooks SessionStart ruidosos, flag `--setting-sources` vacío del Agent SDK bundled, puerto de health-check desalineado) | agentes | Ninguno (100% genérico, sin dato de cliente) |
| cc-history.sh | Wrapper de una línea sobre `npx cchistory` para auditar el historial de comandos bash que Claude Code ejecutó | agentes | Ninguno (100% genérico) |
| cdp-client.py (ex `claw/cdp.py`) | Cliente Chrome DevTools Protocol por WebSocket hecho a mano con solo stdlib (handshake + framing manual); `dump`/`load` de `Storage.getCookies`/`setCookies` | web / agentes | Ninguno (100% genérico) |
| excepcion-codigo.py | Pase de excepción de 24h para saltar un guard de "no tocar código nativo", con motivo obligatorio y expiración a fichero JSON | agentes | Slug de cliente `canicas` → `<slug>`; "autoriza el responsable" → "autoriza el humano responsable" |
| alcance.py | Declara qué slugs de proyecto están autorizados a tocarse en la tarea actual, bloquea escrituras fuera de ese alcance, expira a fin del día local | agentes | Slugs reales `identity/canicas/osos/davidnoguer` → `proyecto-a/b/c/d`; comentario "el responsable" → "el usuario" |
| telegram-bridge.py | Bot de Telegram que relee mensajes a `claude -p --dangerously-skip-permissions` y devuelve la salida, con conversor Markdown→Telegram-HTML | agentes / automatizacion | Branding "el arnés de origen" y ruta `D:/el arnés de origen` genericizados; `ARNES-DE-ORIGEN_BOT_TOKEN` → `TELEGRAM_BOT_TOKEN` |
| quota-oficial.py | Consulta el endpoint oficial no documentado `GET /api/oauth/usage` para la cuota real 5h/semanal, resuelve `CLAUDE_CONFIG_DIR` vía el daemon activo, lee el token OAuth de Keychain, con backoff exponencial | agentes | Comentarios "el responsable" → genéricos; ruta vault `.secrets/<la-agencia>/claude-accounts` → `.secrets/claude-accounts` |
| multi-review.py | Revisión de código multi-modelo en paralelo (Gemini CLI local + 2 modelos gratis de OpenRouter vía `asyncio.gather`), parseo de veredicto XML, consenso con exit codes, modo alterno de auditoría de frontend | agentes | Branding "el arnés de origen" en headers/paths/prints; ruta ejemplo `src/<la agencia>/<la-agencia>-panel/src` → `src/mi-proyecto/frontend/src` |
| mandar-a-terminales.py | Difunde texto a las terminales VS Code hermanas vía AppleScript (ciclo `Cmd+Shift+P` → "Focus Next Terminal"), con modo de calibración por capturas y detector de "ocupada" por tamaño de transcript; incluye hallazgos negativos documentados (`/dev/ttysNNN`, `TIOCSTI` → `EPERM` en macOS) | agentes | Atribución "el responsable, 2026-07-29" → genérica |
| mantener-sesiones-claude.sh (ex `mantener-sesiones.sh`) | Mantiene vivas N cuentas aisladas de Claude Code (refresh token ~9 días) con una llamada Haiku mínima por cuenta, con checks estrictos de permisos 700/600 antes de tocar el vault | agentes / infraestructura | Alias reales `<la-agencia>`/`webmaster` → lista configurable por `MANTENER_SESIONES_ALIASES`; ruta vault genericizada |
| medir-contexto-claude.py (ex `claudeclaw-medir-contexto.py`) | Báscula de coste de contexto: parsea transcripts `.jsonl` de Claude Code deduplicando por `requestId`, calcula coste equivalente de caché (`cache_creation*1.25 + cache_read*0.10`), diff antes/después | agentes | `PROJECT` hardcodeado a una ruta absoluta → derivado dinámicamente de la ruta del repo o `CLAUDE_PROJECT_SLUG`; branding "ClaudeClaw" → genérico |
| acceso-remoto-watchdog.sh | Vigila cada 5 min que SSH/Screen Sharing/Tailscale sigan vivos y los reactiva; documenta el gotcha de Tailscale SSH interceptando el puerto 22 e ignorando `authorized_keys` | infraestructura | Hostname `imac-dario` → `imac-remoto`; comentario de incidente con nombre real → genérico; ruta plist con "Arnes-el responsable" → genérica |
| auto_resume.ps1 | PowerShell: reenfoca VS Code y envía `SendKeys` a una hora programada para reanudar una sesión de Claude Code colgada | agentes / infraestructura | Branding "el arnés de origen" → genérico |
| actualizacion-nocturna-mac.sh (ex `mac-mantenimiento/actualizacion-nocturna.sh`) | Activa `pmset repeat wakeorpoweron` + `softwareupdate --schedule on` para actualizaciones nocturnas 100% desatendidas sin guardar contraseña en disco (limitación real de Apple Silicon), con guardarraíl de backup Time Machine y flag `--revertir` | infraestructura | "Mac de el responsable"/"contraseña de el responsable" → genérico; disco de ejemplo "My Passport" → genérico |
| setup-mac.sh (ex `mac-optimizacion/setup-mac.sh`) | Setup idempotente de Apple Silicon: instala `stats`+`topgrade`, limpia Homebrew, para `ollama`, instala LaunchAgent quincenal, detecta el bug conocido de `PerfPowerServices` | infraestructura | Label `com.alex.topgrade-auto` → `com.example.topgrade-auto` |
| install-modifier-swap.sh (ex `keyboard-swap/install-modifier-swap.sh`) | Intercambia Command↔Option en un teclado externo vía `hidutil`, autodetecta VendorID/ProductID, instala LaunchAgent que reaplica el mapeo al reconectar | infraestructura | Label `com.alex.gmk67-modifier-swap` → `com.example.keyboard-modifier-swap` |
| enviar-correo-smtp.py (ex `enviar-correo-corporativo.py`) | Envío SMTP (SSL/STARTTLS) + copia por IMAP a la carpeta Enviados (necesario en IONOS, que no la genera solo) | automatizacion | Docstring/ejemplos con nombre y dominio reales → genéricos; ruta de credenciales genericizada |
| claude-code/ (run-smart.sh, run-balanced.sh, run-low.sh, run-pro.sh, run-strict.sh, mcp-servers.full.json, mcp-servers.min.json, README.md) | Familia de lanzadores del CLI `claude` con presets de coste/esfuerzo y clasificador heurístico de tarea → modelo (`run-smart.sh`); toggle de config MCP mínima/completa | agentes | Ninguno (100% genérico desde origen; se omitió `tmux/` por falta de tiempo para revisarlo) |

## Descartadas

- check-backups-webroot.py: identificadores del parque de servidores propio (`PLESK=[...]`, `HESTIA=[...]`) inseparables, e importa un módulo de resolución de credenciales por servidor.
- selector-modelo.py / elegir-modelo.py: no funcionales sin los ficheros "motor" no cosechados (`ask-popup.py`, `llm-providers/registry.py`, logos).
- web-diff-visual.py: algoritmo valioso (diff visual con tolerancia a desplazamiento) pero con `BASE` de dominio propio y comentarios de proyectos de cliente entrelazados; no separable sin reescritura mayor.
- preguntar.py: no funcional sin el motor `ask-popup.py` no cosechado.
- espera-tareas.py: depende de la cadena `preguntar.py`/`ask-popup.py` no cosechada, y del lenguaje de flujo propio de un usuario concreto.
- generar-agents-md.py: la plantilla de salida embebe ~200 líneas de política específica (nombre, IP de producción, nombre de buzón, reglas propias); limpiar sería reescribir la plantilla, no un harvest mecánico. El patrón de introspección (leer skills/agents/rules/tools para generar `AGENTS.md`) queda anotado como valioso para el futuro.
- wp_acceso.py: nombres de dominio de cliente reales inseparables en comentarios (son la explicación de por qué existe cada excepción).
- dashboard/serve.sh + dashboard-chorus/ (44 ficheros): lanzador de un fork de un proyecto OSS de terceros ("Chorus") ya vendorizado completo (LICENSE, CONTRIBUTING.md, ROADMAP.md…), no es IP propia.
- skill-seekers/ (55 ficheros): repo OSS de terceros vendorizado completo (LICENSE, CHANGELOG.md, CONTRIBUTING.md…).
- claude-cuenta.py (1482 líneas): patrón valioso (multicuenta Claude Code aislada por `CLAUDE_CONFIG_DIR`) pero comentarios de incidentes reales entrelazados en toda la lógica y acoplado al daemon propio; el núcleo del patrón ya queda cubierto, más ligero, por `mantener-sesiones-claude.sh` y `quota-oficial.py`.
- repartir-trabajo.py (1084 líneas): orquestador de "cuadrilla" atado al daemon propio (`http://127.0.0.1:4632`) y con reglas de cuota personales incrustadas como constantes con comentarios "Regla de el responsable"; limpieza no mecánica.
- supervisor-tick.py + supervisor-tick-instalar.sh: depende de la API del daemon propio para leer ventanas/títulos; sin ese daemon no es funcional standalone. Patrón (reloj externo en vez de que el LLM se autoprogramme el despertar, evitando cientos de miles de tokens de caché por sondeo) anotado como valioso para referencia futura.
- analizador_masivo.py / analizador_masivo_local.py: solapa con `analyze-reel.sh` (ya copiada) en la parte yt-dlp+whisper; arrastra ruta Windows hardcodeada y docstring con la razón de facturación de un socio.
- trello.py, trello_from_mail.py, trello-watcher/ (todo el directorio): capa fina sobre la API REST de Trello con convenciones de negocio de un socio entrelazadas (tablero, listas "Hecho/Instalado"); además sus ficheros grandes (`mailcheck.py`, `watch.py`) ya estaban marcados como contaminados con buzones reales.
- generar-presupuesto-lib.js, generar-presupuesto.js, presupuesto-google-sheets.gs: lógica de precios/presupuestos propia de la agencia, no es herramienta genérica.
- relogin-cuenta.sh, anadir-cuenta.sh: companions del almacén de cuentas de `claude-cuenta.py` (descartado); mismo acoplamiento.
- claudeclaw-compactar.py, claudeclaw-daemon.py, claudeclaw-limpiar-sesiones.py, claudeclaw-reiniciar-libre.sh, claw-broadcast.py, claw-watch.py, claw/claw.py, claw/tarea.py: subsistema completo atado al daemon propio ClaudeClaw (`localhost:4632`, gestión de ventanas/sesiones de este arnés concreto); no son herramientas standalone.
- mac2-claude.sh, mac2-cuenta.sh, mac2-reglas-fijas.md, mac2-setup.sh, mac2.sh, publisher-mac2.sh: configuración específica del setup de dos Macs propio (hostnames, IPs, cuentas); sin patrón genérico separable en el tiempo disponible.
- abrir-claudeclaw.sh, abrir-panel-publisher.sh: lanzadores de infraestructura propia (daemon ClaudeClaw / panel de negocio).
- creds-vnc.sh: manejo de credenciales de VNC propias.
- avisar-dario.sh: notificador personal nombrado y dirigido a una persona concreta.
- claudeclaw-ui/ (12 ficheros, incl. shots.py, try-css.py): companion de una app ya marcada como contaminada (`fetch-fonts.py`).
- intel-routine/: automatización de rutina de inteligencia propia del negocio (prompts y setup específicos), sin patrón genérico separado a tiempo.
- launchagents/ (4 plist): atados a rutas y labels `com.<la-agencia>.*` concretos; el patrón LaunchAgent en sí es documentación estándar de Apple, no aporta como extracto.
- mailwatch.sh: toggle de un workflow de GitHub Actions concreto (`REPO="<la agencia>/mail-watch"`), valor añadido bajo tras genericizar; se prioriza el resto del lote más rico del cluster.
- mail-mac-configurar.py: técnica de fondo valiosa (perfil `.mobileconfig` `com.apple.mail.managed` para provisionar cuentas de Mail.app que AppleScript no puede crear) pero la lógica de dos cuentas está entrelazada con nombre/organización reales y rutas de vault reales; limpiarlo de verdad exige reescribir a un bucle N-cuentas guiado por JSON, más que un harvest mecánico.
- claude-code/tmux/: no revisado a fondo por límite de tiempo del cluster; se deja fuera para no copiar sin verificar.

## Barrido de contaminación (esta tanda)

Primera pasada (grep completo sobre `cosecha/`, incluyendo ficheros de otros forks): aciertos reales
encontrados solo en ficheros de este cluster — corregidos:
- `alcance.py`: "el dia de trabajo de el responsable" → genérico.
- `acceso-remoto-watchdog.sh`: ruta con "Arnes-el responsable" y "login a mano de el responsable" → genéricos.
- `multi-review.py`: ruta de ejemplo `src/<la agencia>/<la-agencia>-panel/src` → genérica.
- `semble-doctor.sh`: ruta de ejemplo `./src/<la agencia>/<la-agencia>-assets` → genérica.
- `telegram-bridge.py`: `ARNES-DE-ORIGEN_BOT_TOKEN` → `TELEGRAM_BOT_TOKEN`.
- `excepcion-codigo.py`: "autoriza el responsable" (x2) → "autoriza el humano responsable".

Segunda pasada, solo sobre los ficheros copiados por este cluster (tras las correcciones):

```
--- fin barrido cluster B ---
```

Sin aciertos. (El único "sk-or-v1-*" detectado en `install-open-interpreter-macos` es un patrón de
validación de formato de clave, no una credencial embebida — ruido esperado por la propia regla del
barrido.)
