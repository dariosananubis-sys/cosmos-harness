# Auditoría GB — pueblos `origen: propio` (ciclo 2)

Encargo de Darío: "tiene que estar este harnés fuera de <la agencia>, no pongas datos de <la agencia>, es
para Darío, no <la agencia>." COSMOS debe quedar público-limpio y genérico (GOAL.md §5).

Descubrimiento por `grep -l '^origen: propio' galaxia/pueblos/*/SKILL.md`: **37 pueblos**, no 28
como decía el encargo original (probable trabajo concurrente de agentes hermanos del mismo ciclo
de auditoría). Se auditaron los 37 leyendo SKILL.md + `scripts/` + `references/` completos.

Criterio aplicado sin excepciones:
- **GENÉRICO reescrito**: describe una capacidad que cualquiera contrataría. Se reescribió lo que
  tenía dato de agencia; los que ya estaban limpios se dejan como "ya estaba limpio".
- **INTERNO**: describe el proceso interno de la agencia, no una capacidad contratable. No se toca
  el contenido — "el fixer decide y lo retira" — solo se anota el motivo.
- **sin guion**: propio con solo prosa y cero scripts. Ninguno de los 37 cae aquí (los 37 tienen
  al menos un fichero en `scripts/`).

## Tabla

| pueblo | veredicto | qué dato de la agencia tenía | qué se cambió |
|---|---|---|---|
| acceso-remoto | GENÉRICO reescrito | "el iMac" (máquina identificable), hostname Tailscale hardcodeado `imac-remoto`, comentario apuntaba a `tools/` | "el iMac" → "este Mac"; hostname a `TS_HOSTNAME="${TS_HOSTNAME:-mac-remoto}"` configurable; comentario de fuente a `scripts/` |
| alcance-y-excepcion | GENÉRICO reescrito | rutas de ejemplo `tools/alcance.py` / `tools/excepcion-codigo.py`; variable `CLAUDECLAW_VENTANA` (nombre de producto propio); docstring mencionaba `guard-web-sin-codigo.py` y ficheros internos por nombre | rutas a `scripts/`; `CLAUDECLAW_VENTANA` → `AGENTE_SESION`; referencias a ficheros internos genericizadas ("un enganche", "tu propio registro de excepciones") |
| aviso-por-chat | GENÉRICO reescrito | `google-chat-dm.py` hacía `from log import ...` de un módulo que no existía en su carpeta (import roto en tiempo de ejecución, no detectable por `py_compile`) | se copió `log.py` (mismo módulo compartido de `search-console`) a su carpeta; verificado el conjunto de símbolos exportado coincide exacto |
| bing-webmaster | GENÉRICO reescrito | mismo bug de import roto que aviso-por-chat: `from log import ...` sin el fichero físico en la carpeta | se copió `log.py` a su carpeta; `py_compile` OK |
| captura-recortada | GENÉRICO | ya estaba limpio | sin cambios |
| catalogo-woocommerce | GENÉRICO | ya estaba limpio (placeholders `<slug>`, `~/.wp-sites/sites.json`) | sin cambios |
| codigo-al-modelo | GENÉRICO reescrito | SKILL.md decía "medido en esta casa"; `semble-doctor.sh` apuntaba a `tools/semble-doctor.sh` en el uso | "esta casa" → "un caso real"; rutas de uso a `scripts/semble-doctor.sh` |
| consola-interactiva-tmux | GENÉRICO | ya estaba limpio; rescatado con atribución correcta (Jesse Vincent / `obra`, MIT, verificada 2026-09-03) | sin cambios |
| contenedor-efimero | GENÉRICO (con bug estructural, no de datos de agencia) | ninguno — el contenido en sí es genérico | **no se tocó**: SKILL.md declara 5 scripts (`docker-ephemeral-runner.js`, `docker-wait-with-timeout.js`, `docker-job-log-markers.js`, `docker-orphan-container-cleanup.js`, `pg-secret-file-connection.js`) pero solo existe 1 en disco, y ese único fichero importa `./docker-wait-with-timeout.js` y `./docker-job-log-markers.js`, que no existen. Sintaxis JS válida (`node --check` OK) pero el módulo no es importable tal cual. Fuera del mandato de "quitar datos de agencia": queda anotado para que el fixer decida reconstruir o recortar el SKILL.md |
| cookies-declaradas | GENÉRICO | ya estaba limpio — los "medido en un caso real"/"un sitio"/"otro sitio" ya usan fraseo genérico, sin nombres de cliente | sin cambios |
| correo-smtp | GENÉRICO reescrito | docstring con referencia a "él"/Darío y a IONOS como proveedor por nombre; ruta de ejemplo `tools/enviar-correo-smtp.py`; host SMTP/IMAP hardcodeados a `smtp.ionos.es`/`imap.ionos.es` como default | docstring generalizado; ruta a `scripts/`; defaults de host quitados — ahora exige `MAIL_SMTP_HOST`/`MAIL_IMAP_HOST` por variable de entorno |
| delegar-generacion | GENÉRICO reescrito | `codex-handler.sh` apuntaba a `./tools/codex-handler.sh`; `forbidden=(...)` traía hardcodeado el sistema de diseño de un producto concreto (clases Tailwind, `BentoCard`/`BentoPill`/`BentoStat`); check de "sistema de diseño" con marcadores `useTheme\|isDark\|c.text\|c.muted` hardcodeados | ruta a `scripts/`; `forbidden` vacío por defecto, configurable por `CODEX_FORBIDDEN_PATTERNS`; check de diseño envuelto en `CODEX_DESIGN_SYSTEM_MARKERS` (vacío = se omite) |
| despliegue-reanudable | GENÉRICO | ya estaba limpio (núcleo sin red ni rutas de agencia; "Rescatado de la skill `resumable-deployment` de un arnes propio" — convención de procedencia aceptada) | sin cambios |
| diario-sin-duplicados | GENÉRICO | ya estaba limpio | sin cambios |
| dominios-libres | GENÉRICO | ya estaba limpio (solo fuentes públicas: NS, RDAP, whois) | sin cambios |
| extractor-de-curso | GENÉRICO reescrito | `chrome_cdp.sh` tenía una referencia colgante a `memory/reference-cdp-perfil-chrome-google.md` (fichero interno del arnés original, inexistente aquí) | se sustituyó por la explicación inline del motivo técnico (Chrome 136+ ignora `--remote-debugging-port` sobre el user-data-dir por defecto) |
| gate-de-salida-web | GENÉRICO | ya estaba limpio | sin cambios |
| mcp-call | GENÉRICO | ya estaba limpio (puente JSON-RPC genérico vía `MCP_BRIDGE_CMD`) | sin cambios |
| medir-contexto | GENÉRICO reescrito | docstring mencionaba `ORQUESTADOR.md` (fichero interno de la agencia); 4 rutas de uso a `tools/medir-contexto-claude.py` y `tools/cc-history.sh`; ruta hardcodeada `.claude/claudeclaw` para leer `sessions.json`/`session.json` | mención a "cualquier prompt adicional que tu propio canal de automatización inyecte"; rutas a `scripts/`; `.claude/claudeclaw` reemplazado por `SESSION_NAMES_DIR` configurable por entorno (con degradación a `{}` si no está definida) |
| paginas-legales | GENÉRICO reescrito | **hallazgo más grave del audit**: `legales-lssi.py` tenía 5 apariciones de slugs reales de clientes de <la agencia> (`<cliente>`, `<cliente>`, `<cliente>`, `exclusivocuero` ×2, `mcespacios`) en comentarios de "caso real medido" | los 5 nombres sustituidos por fraseo genérico ("varias webs más del catálogo", "una tienda real", "una web real", "caso real medido"); verificado por grep que no aparecen en ningún otro fichero del repo |
| panel-auth-cookie | GENÉRICO | ya estaba limpio (Docker + cookie de secreto, todo por variables de entorno) | sin cambios |
| plan-auditado | GENÉRICO reescrito | `audit-harness.sh` apuntaba a `./tools/audit-harness.sh` en el uso | ruta a `scripts/audit-harness.sh` |
| playbook-obligatorio | GENÉRICO | ya estaba limpio | sin cambios |
| punto-de-restauracion-web | GENÉRICO | ya estaba limpio | sin cambios |
| reel-a-texto | GENÉRICO reescrito | `analyze-reel.sh` e `ig-dl.sh` apuntaban a `tools/analyze-reel.sh` / `tools/ig-dl.sh` en cabecera y uso | rutas a `scripts/` |
| revision-cruzada | GENÉRICO reescrito | `multi-review.py`: 4 rutas de uso a `tools/multi-review.py`; el `AUDIT_SYSTEM_PROMPT` traía hardcodeado el sistema de diseño real de un producto (IBM Plex Sans/Mono, `--color-accent:#56b8d4`, `ThemeContext`/`useTheme`) y un anti-patrón específico de ese producto (`text-gray-*`/`text-zinc-*`); SKILL.md decía "esta casa" | rutas a `scripts/`; plantilla de sistema de diseño convertida en placeholders editables (`<tu tipografía de cuerpo>`, etc.); anti-patrón específico quitado, se conservan los genéricos; "esta casa" → "cualquier regla seria de revisor adversarial" |
| search-console | GENÉRICO | ya estaba limpio; `log.py` es el módulo compartido copiado a bing-webmaster y aviso-por-chat | sin cambios (fuente del fix de los otros dos) |
| validadores-frontera | GENÉRICO | ya estaba limpio (funciones puras JS) | sin cambios |
| wp-app-password | GENÉRICO | ya estaba limpio (BWS + `sites.yaml` como placeholder) | sin cambios |
| wp-remoto | GENÉRICO reescrito | SKILL.md traía un ejemplo de comando roto: `sys.path.insert(0,'cosecha')` (mezcla del término narrativo "cosecha propia" con un path real que no existe — el directorio real es `scripts/`) e importaba una función `sql` que no existe en `wp_sql.py` (las reales son `consulta`/`ejecuta`/`php`/`prefijo`/`wp`) | corregido a `sys.path.insert(0,'scripts')` y `from wp_sql import consulta` |
| auditar-gasto | **INTERNO** | "cómo se audita el gasto del arnés de Darío" (ejemplo explícito de Darío) | no se toca — el contenido leído ya es genérico/anonimizado (`GLOBALES_OK = set()` vacío por defecto), pero la clasificación INTERNO se mantiene por instrucción literal; se señala para que el fixer reconsidere si de verdad no es contratable |
| contrato-de-publicacion | **INTERNO** | "el contrato de publicación de ocho puertas de la agencia" (ejemplo explícito de Darío) | no se toca — contenido ya genérico/anonimizado; misma nota de transparencia que auditar-gasto |
| cuentas-del-asistente | **INTERNO** | "cómo se reparten las cuentas del asistente" (ejemplo explícito de Darío); referencias directas a rutas de tipo `tools/` propias | no se toca |
| lanzadores-de-modelo | **INTERNO** | "los lanzadores de modelo del CLI de una persona" (ejemplo explícito de Darío) | no se toca — contenido ya genérico/anonimizado; misma nota de transparencia |
| manifiesto-de-evidencias | **INTERNO** | "el manifiesto de evidencias de un programa de subvenciones concreto" (ejemplo explícito de Darío) | no se toca — contenido ya genérico/anonimizado (placeholders `sitio-demo`, `example.invalid`); misma nota de transparencia |
| ordenes-entre-ventanas | **INTERNO** | "las órdenes entre ventanas de su editor" (ejemplo explícito de Darío); `mandar-a-terminales.py` nombra el producto propio directamente | no se toca |
| quota-oficial | **INTERNO** | "la cuota de su suscripción" (ejemplo explícito de Darío) — **la fuga más pesada de todo el audit**: `quota-oficial.py` satura de rutas/nombres del producto propio (`.claude/claudeclaw`, `rate-limits.json`, `daemon.pid`, `claude-cuenta.py`, `tools/claudeclaw-ui/src/quota.ts`, `.claude/statusline.cjs`), un incidente fechado que nombra literalmente la cuenta `webmaster` (la misma bajo la que corre esta sesión), y una ruta hardcodeada `~/.secrets/claude-accounts` de esta máquina exacta; `quota-peak.py` en el mismo pueblo es comparativamente limpio (solo lee `~/.claude/projects`) | no se toca ningún fichero — "el fixer decide y lo retira" |

## Resumen de veredictos

- **GENÉRICO**: 30 (13 reescritos con cambios reales, 1 con bug estructural anotado sin tocar, 16 ya estaban limpios).
- **INTERNO**: 7 — los 4 que Darío nombró explícitamente y que además ya leían limpios de contenido (auditar-gasto, contrato-de-publicacion, manifiesto-de-evidencias, lanzadores-de-modelo) quedan señalados para que el fixer reconsidere su encaje INTERNO/GENÉRICO; los otros 3 (cuentas-del-asistente, ordenes-entre-ventanas, quota-oficial) tienen fuga de datos de agencia confirmada en el propio código.
- **sin guion**: 0 — los 37 pueblos tienen al menos un fichero en `scripts/`.

## Verificación de sintaxis

Todos los ficheros `.py` editados o revisados: `python3 -m py_compile` OK. Todos los `.sh`:
`bash -n` OK. El único `.js` de contenedor-efimero: `node --check` OK (sintaxis válida; el bug es
de dependencias que faltan en disco, no de sintaxis).

Barridos finales de cierre (sin más hallazgos): `CLAUDECLAW`/`claudeclaw`/`ClaudeClaw` (solo en los
4 INTERNO ya clasificados), `tools/<script>` self-referencias (solo en 3 INTERNO que las tenían de
origen), `dario`/`<agencia>` (0 apariciones), `esta casa` (0 apariciones dentro del alcance de 37
pueblos tras los 2 arreglos de codigo-al-modelo y revision-cruzada), direcciones de correo y
dominios reales (0 apariciones adicionales).

## `python3 -m cosmos validar`

```
COSMOS  verde (2 saltos activos: P01, caduca en 7 d; P02, caduca en 7 d)  0 errores
```

Verde, 0 errores, tras todos los cambios de este informe.
