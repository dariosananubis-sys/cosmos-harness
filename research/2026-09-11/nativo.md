# Inventario nativo de Claude Code: gasto de tokens y calidad

**Fecha de verificación: 2026-09-11 · versión más reciente publicada: v2.1.268 (2026-09-10)**

Todo lo de abajo está verificado contra la documentación oficial en code.claude.com/docs (consultada en vivo el 2026-09-11) y contra el CHANGELOG.md crudo de github.com/anthropics/claude-code. Cuando la doc HTML del changelog y el fichero crudo discrepan, mando el fichero crudo: el resumen HTML asigna mal varias versiones.

Nota de formato: este documento evita deliberadamente el carácter "mayor que" porque el guardián G03 del repo lo interpreta como redirección de shell.

---

## 1. HOOKS

**Fuente:** https://code.claude.com/docs/en/hooks.md (referencia completa) · guía: https://code.claude.com/docs/en/hooks-guide.md

### 1.1 Lista completa de eventos disponibles hoy (33)

| # | Evento | Cuándo dispara |
|---|--------|----------------|
| 1 | `SessionStart` | Arranque, `resume`, `clear`, `compact`, `fork` (campo `start_reason`) |
| 2 | `Setup` | `claude --init-only`, o `--init` / `--maintenance` en `-p` |
| 3 | `InstructionsLoaded` | Se carga un `CLAUDE.md` o un `.claude/rules/*.md` |
| 4 | `UserPromptSubmit` | Envías un prompt, antes de procesarlo |
| 5 | `UserPromptExpansion` | Un comando tecleado se expande a prompt |
| 6 | `MessageDisplay` | Mientras se muestra texto del asistente |
| 7 | `PreToolUse` | Antes de ejecutar una herramienta |
| 8 | `PermissionRequest` | Una llamada necesita decisión de permiso |
| 9 | `PostToolUse` | Después de que una herramienta acaba **bien** |
| 10 | `PostToolUseFailure` | Después de que una herramienta **falla** |
| 11 | `PostToolBatch` | Tras resolverse un lote completo de llamadas paralelas |
| 12 | `PermissionDenied` | El modo auto deniega una llamada |
| 13 | `Notification` | Claude Code emite una notificación |
| 14 | `SubagentStart` | Se lanza un subagente |
| 15 | `SubagentStop` | Un subagente termina |
| 16 | `TaskCreated` | Se crea una tarea vía `TaskCreate` |
| 17 | `TaskCompleted` | Se marca una tarea como completada |
| 18 | `Stop` | Claude termina de responder |
| 19 | `StopFailure` | El turno acaba por error de API (campo `error_type`) |
| 20 | `TeammateIdle` | Un compañero de agent team va a quedar ocioso |
| 21 | `ConfigChange` | Cambia un fichero de configuración en sesión |
| 22 | `CwdChanged` | Cambia el directorio de trabajo |
| 23 | `DirectoryAdded` | Se añade un directorio a media sesión (añadido en 2.1.219) |
| 24 | `FileChanged` | Cambia en disco un fichero vigilado |
| 25 | `WorktreeCreate` | Se crea un worktree |
| 26 | `WorktreeRemove` | Se elimina un worktree |
| 27 | `PreCompact` | Antes de compactar |
| 28 | `PostCompact` | Después de compactar |
| 29 | `PreModelSwitch` | Antes de aplicar un cambio de modelo (añadido en 2.1.251) |
| 30 | `PostModelSwitch` | Después de cambiar el modelo de la sesión (2.1.251) |
| 31 | `SessionEnd` | La sesión termina |
| 32 | `Elicitation` | Un servidor MCP pide input al usuario |
| 33 | `ElicitationResult` | El usuario responde a esa petición |

Existen todos los que preguntabas: `PostToolUseFailure`, `SubagentStart`, `PostCompact`, `TeammateIdle`, `TaskCompleted`. Y además `PostToolBatch`, `PermissionRequest`, `PermissionDenied`, `StopFailure`, `InstructionsLoaded`, `ConfigChange`, `CwdChanged`, `MessageDisplay` y `Setup`.

### 1.2 Campos comunes del JSON de entrada

**Sí trae `permission_mode`.** Tabla oficial de "Common input fields":

| Campo | Contenido |
|---|---|
| `session_id` | Identificador de la sesión |
| `prompt_id` | UUID del prompt de usuario en curso |
| `transcript_path` | Ruta al JSON de la conversación |
| `cwd` | Directorio de trabajo al invocar el hook |
| `scratchpad_dir` | Directorio scratchpad de la sesión |
| `permission_mode` | `"default"`, `"plan"`, `"acceptEdits"`, `"auto"`, `"dontAsk"` o `"bypassPermissions"` |
| `effort` | Objeto con `level` (nivel de esfuerzo vigente) |
| `hook_event_name` | Nombre del evento |
| `agent_id`, `agent_type` | Solo dentro de subagente o con `--agent` |

Ejemplo literal de la doc (`PreToolUse`):

```json
{
  "session_id": "abc123",
  "prompt_id": "550e8400-e29b-41d4-a716-446655440000",
  "transcript_path": "/home/user/.claude/projects/.../transcript.jsonl",
  "cwd": "/home/user/my-project",
  "scratchpad_dir": "/tmp/claude-1000/-home-user-my-project/abc123/scratchpad",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": { "command": "npm test", "description": "Run test suite", "timeout": 120000, "run_in_background": false },
  "tool_use_id": "toolu_01ABC123..."
}
```

### 1.3 `tool_response`: ¿stdout/stderr separados o un solo `output`? Depende del evento

- **`PostToolUse`** recibe `tool_response` igual al **objeto Output estructurado de la herramienta**. Para `Write` es `{"filePath": "...", "type": "create"}`. Para **`Bash` es un objeto con `stdout`, `stderr`, `interrupted` e `isImage`** (lo dice la nota sobre `updatedToolOutput`: "Bash returns an object with stdout, stderr, interrupted, and isImage fields"). Trae además `duration_ms` opcional, que excluye el tiempo de los prompts de permiso y de los hooks PreToolUse.
- **`PostToolUseFailure` NO trae `tool_response`.** Trae campos de nivel superior: `error` (string; en Bash/PowerShell empieza por la línea `Exit code N` y luego **stdout y stderr entremezclados en un solo bloque**), `is_interrupt` (booleano opcional) y `duration_ms`.
- **`PostToolBatch`** trae `tool_response` como el **contenido serializado del `tool_result`** que ve el modelo (string o array de bloques). La doc avisa de forma explícita: "The tool_response shape differs from PostToolUse's".

Ejemplo literal de `PostToolUseFailure`:

```json
{
  "session_id": "abc123",
  "hook_event_name": "PostToolUseFailure",
  "tool_name": "Bash",
  "tool_input": { "command": "npm test", "description": "Run test suite" },
  "tool_use_id": "toolu_01ABC123...",
  "error": "Exit code 1\nError: Cannot find module 'express'",
  "is_interrupt": false,
  "duration_ms": 4187
}
```

### 1.4 Qué puede devolver cada hook (JSON por stdout con exit 0)

**Campos universales** (los aceptan todos los eventos; algunos los descartan):

| Campo | Default | Efecto |
|---|---|---|
| `continue` | `true` | Con `false`, Claude para del todo tras el hook. Tiene prioridad sobre cualquier decisión específica del evento |
| `stopReason` | — | Mensaje mostrado cuando `continue` es `false`; permanece en la conversación |
| `suppressOutput` | `false` | **No hace nada**: se acepta pero se ignora. El stdout de un hook con éxito nunca sale en el transcript |
| `systemMessage` | — | Aviso al usuario. En el Agent SDK y en `--output-format stream-json` puede llegar como `SDKInformationalMessage` |
| `terminalSequence` | — | Secuencia de escape de terminal, restringida a OSC 0/1/2/9/99/777 y BEL |

**Campos por evento**, dentro de `hookSpecificOutput` (que exige `hookEventName`):

| Evento | Campos |
|---|---|
| `PreToolUse` | `permissionDecision`: `allow`, `deny` o `ask`; `permissionDecisionReason`; `updatedInput` (reescribe `tool_input`) |
| `PermissionRequest` | `decision`: `allow`, `deny` o `ask`; `reason` |
| `PermissionDenied` | `permissionDecision`; `retry: true` |
| `PostToolUse` y `PostToolUseFailure` | `decision: "block"` con `reason` (se añade junto al resultado, **no lo sustituye**); `additionalContext`; `classifierContext` (nota para el clasificador de auto mode, v2.1.236+); **`updatedToolOutput`** (sustituye la salida antes de llegar a Claude; el valor debe respetar el esquema de la herramienta); `updatedMCPToolOutput` (solo MCP, se prefiere `updatedToolOutput`) |
| `UserPromptSubmit` y `UserPromptExpansion` | `decision: "block"` con `reason`; `additionalContext` |
| `Stop` y `SubagentStop` | `decision: "block"` con `reason` (mantiene al agente trabajando y le entrega `reason` como siguiente instrucción); `additionalContext` |

Límite duro relevante para el gasto: **las cadenas de salida de hooks (`additionalContext`, `systemMessage`, stdout plano) se capan a 10.000 caracteres**; lo que pase se guarda a fichero y se sustituye por un preview más la ruta. Un hook charlatán ya no puede reventar el contexto (arreglo de 2.1.248).

Códigos de salida: exit 0 con JSON en stdout da control fino; **exit 2 bloquea** en los eventos que lo soportan; el stderr de un exit 2 sí se le enseña a Claude en `PostToolUse` y `PostToolUseFailure`. El stderr de un hook que sale con 0 va solo al log de depuración.

### 1.5 Campo `timeout` por hook: sí existe

Campo `timeout`, **en segundos**, opcional. Texto literal de la doc, en cursiva:

*"Seconds before canceling. Claude Code doesn't enforce it on a command hook you run with async: true. Defaults: **600 for command, http, and mcp_tool; 30 for prompt; 60 for agent**. Claude Code lowers the command, http, and mcp_tool default to **30** on UserPromptSubmit, PreModelSwitch, and PostModelSwitch, and to **10** on MessageDisplay. SessionEnd hooks share a **1.5-second budget**; if your settings set a longer per-hook timeout, Claude Code raises the budget to match, up to 60 seconds."*

Variable relacionada: `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` (arreglada en 2.1.268 para que extienda de verdad los hooks `SessionEnd` que no llevan `timeout` propio).

### 1.6 Tipos de hook distintos de `command`: sí, hay cinco en total

1. **`command`** — shell; recibe el JSON por stdin y responde con código de salida y stdout. Campos extra: `args`, `async`, `asyncRewake`, `shell` (`bash` o `powershell`), `statusMessage`, `if` (condición con sintaxis de regla de permiso), `once`.
2. **`http`** — POST del JSON del evento a una URL; la respuesta usa el mismo formato JSON. Campos: `url`, `headers` (admite `$VAR`), `allowedEnvVars`. Se restringe con `allowedHttpHookUrls` y `httpHookAllowedEnvVars`.
3. **`mcp_tool`** — llama a una tool de un servidor MCP ya conectado (`server`, `tool`, `input` con `${campo}`); su texto se trata como stdout.
4. **`prompt`** — manda un prompt a un modelo para una evaluación de un solo turno; devuelve JSON. Campos: `prompt` (con `$ARGUMENTS`), `model`. Timeout por defecto 30 s.
5. **`agent`** — lanza un subagente que puede usar Read, Grep y Glob para verificar antes de decidir. **Experimental.** Timeout 60 s.

Placeholders de ruta admitidos: `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`.

Aviso de coste: **los hooks `prompt` y `agent` gastan tokens** porque son llamadas al modelo. Para filtrar salidas voluminosas sin gastar, usa `command` con `updatedToolOutput`.

---

## 2. SETTINGS Y VARIABLES QUE AFECTAN AL GASTO

**Fuentes:** https://code.claude.com/docs/en/settings-reference.md · https://code.claude.com/docs/en/env-vars.md · https://code.claude.com/docs/en/model-config.md · https://code.claude.com/docs/en/costs.md · https://code.claude.com/docs/en/mcp.md

### 2.1 Modelo, contexto de 1M y esfuerzo

| Ajuste | Dónde se pone | Valores | Qué hace |
|---|---|---|---|
| `model` | settings.json, `--model`, `/model` | alias (`default`, `best`, `fable`, `opus`, `sonnet`, `haiku`, `opusplan`) o ID completo (`claude-opus-5`, `claude-sonnet-5`, `claude-fable-5-1`, `claude-opus-4-8`…) | Modelo por defecto |
| Sufijo **`[1m]`** | `opus[1m]`, `sonnet[1m]`, `fable[1m]`, `opusplan[1m]`, `claude-opus-4-8[1m]` | — | Ventana de **1 millón de tokens**; el sufijo se elimina antes de mandar la petición a la API. **Precio: sin recargo. Tarifa estándar del modelo para todos los tokens, también los que pasan de 200K.** Lo que cambia es el acceso: Opus con 1M va incluido en Max, Team y Enterprise; en Pro requiere usage credits; **Sonnet 4.6 con 1M requiere usage credits en todos los planes, incluido Max**; en API y pay-as-you-go, acceso total. **Sonnet 5 corre 1M nativo y no tiene variante `[1m]`** |
| `modelSettings.ID.effortLevel` | settings.json | `"low"`, `"medium"`, `"high"`, `"xhigh"`, `"max"` | Esfuerzo guardado por modelo. La clave es el **ID completo** (`claude-opus-5`, no `opus`). Si el modelo no soporta el nivel, se usa el mayor soportado por debajo (`xhigh` pasa a `high` en Opus 4.6) |
| `effortLevel` | settings.json | ídem | Default para modelos sin nivel guardado. Desde 2.1.251, `/effort` escribe en `modelSettings`, no aquí |
| **`maxEffortLevel`** | settings.json, global o dentro de `modelSettings.ID` | `low`…`max` (`"max"` no pone tope) | **Nuevo en v2.1.267.** Tope duro de esfuerzo aplicado en cliente antes de cada petición, así que funciona también en Bedrock, Vertex y Foundry. En managed settings lo impone la organización; si varios scopes ponen tope, gana el más bajo. Un tope por debajo de `xhigh` deja `ultracode` inutilizable |
| `alwaysThinkingEnabled` | settings.json o `/config` | booleano | `false` apaga el extended thinking en todas las sesiones. En modelos que siempre piensan (Fable) no tiene efecto. Con thinking apagado en la API de Anthropic, Claude Code manda esfuerzo `high` a los modelos que no aceptan la combinación (como Opus 5) |
| `MAX_THINKING_TOKENS` | env | número | Presupuesto fijo de pensamiento. **Solo aplica a modelos de presupuesto fijo (Opus 4.6 y Sonnet 4.6).** Fable, Sonnet 5 y Opus 4.7+ usan razonamiento adaptativo e ignoran valores positivos. `0` desactiva el pensamiento en la API de Anthropic |
| `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` | env | — | Vuelve al presupuesto fijo en Opus 4.6 y Sonnet 4.6 |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | env | número (admite notación científica y separadores) | Tope de tokens de salida |
| `fallbackModel`, `--fallback-model` | settings o flag | lista, máximo 3 | Cadena de respaldo ante sobrecarga; no actúa ante errores de auth, rate limit ni facturación |
| `availableModels`, `enforceAvailableModels`, `modelPicker`, `modelOverrides` | settings | — | Restringir qué modelos puede elegir el usuario |
| `modelPricing` | **solo managed settings** | `multiplier` y/o `overrides` | Hace que `/usage`, la status line y OTel reporten tus tarifas contratadas en vez del precio de lista (v2.1.242+) |
| `CLAUDE_CODE_SUBAGENT_MODEL` | env | ID de modelo | Modelo **por defecto** de subagentes. Desde 2.1.259 ya no pisa el `model:` de la definición del agente |

### 2.2 Compactación automática y ventana de contexto

- `autoCompactEnabled` (booleano, default `true`): activa o desactiva la compactación automática.
- **`autoCompactWindow`** (settings.json): número de tokens entre **`100000` y `1000000`**; Claude Code lo capa a la ventana real del modelo. Sin valor, usa la ventana afinada por modelo.
- **`/autocompact [auto|tokens]`** (v2.1.221+): acepta `200000`, `500k`, `1M`, o un número desnudo de 100 a 1000 entendido como miles. Guarda en user settings y lo aplica ya.
- **`--autocompact`** (flag de lanzamiento): pisa el setting durante ese lanzamiento y, a diferencia del comando, **no lo preempta un scope superior** como managed settings.
- **`CLAUDE_CODE_AUTO_COMPACT_WINDOW`** (env): **manda sobre el comando, el flag y el setting**. Solo acepta el recuento de tokens desnudo.
- **`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`** (env): sí existe. Porcentaje de 1 a 100 de la ventana en el que se dispara la compactación. **Solo puede adelantarla, nunca retrasarla.**
- **Umbrales por defecto:** sin configurar, se compacta al llegar al límite del modelo, con estas excepciones: sesiones cloud compactan al acercarse; Sonnet 4.6 y Opus 4.6 sin contexto extendido, y Opus 4.8 y Opus 5 cuando corren con ventana de 200K (Bedrock, Vertex, Foundry), compactan en la **frontera de 200K**; los modelos con 1M nativo (Sonnet 5, Fable, Opus 4.7 y posteriores en la API) compactan **a unos 967K tokens** (cambiado en 2.1.247; antes eran unos 934K).
- `CLAUDE_CODE_DISABLE_1M_CONTEXT=1`: quita las variantes 1M del picker y trata como 200K a los modelos con 1M nativo.
- `CLAUDE_CODE_MAX_CONTEXT_TOKENS`: ventana asumida para IDs de gateway o personalizados. Reglas finas según si el ID resuelve a un modelo conocido; con IDs `claude-` reconocidos solo surte efecto junto a `DISABLE_COMPACT`.
- `CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1`: compacta solo cuando la API rechace por longitud.
- `fileCheckpointingEnabled`: snapshots de fichero para `/rewind`.

**Qué sobrevive a la compactación** (https://code.claude.com/docs/en/context-window.md): el system prompt y el output style siguen aplicando; el CLAUDE.md de raíz, las reglas sin `paths`, la auto memory y el plan de plan mode se **reinyectan desde disco**; las reglas con `paths:` y los CLAUDE.md anidados se recargan cuando Claude vuelve a leer un fichero que casa; se **re-leen hasta 5 ficheros** (los modificados más recientemente, y uno de más de 5.000 tokens vuelve como referencia de ruta sin contenido, marcado `Referenced file`); **los cuerpos de las skills invocadas se reinyectan con tope de 5.000 tokens por skill y 25.000 en total**, descartando primero las más antiguas y truncando por el final, así que conviene poner lo importante al principio del SKILL.md.

### 2.3 MCP: el mayor sumidero de contexto

| Ajuste | Valores y default | Efecto |
|---|---|---|
| **`ENABLE_TOOL_SEARCH`** (env) | **activo por defecto**, con esquemas diferidos; `auto` carga los esquemas por adelantado **si caben en el 10 % de la ventana de contexto**; `false` carga todo por adelantado | Con tool search, en contexto solo entran los **nombres** de las tools MCP y las instrucciones del servidor; los esquemas se cargan bajo demanda. **No existe ninguna variable llamada `CLAUDE_CODE_ENABLE_TOOL_SEARCH`: el nombre correcto es `ENABLE_TOOL_SEARCH`.** No está disponible con `ANTHROPIC_BASE_URL` propio ni en modelos anteriores a la generación 4.5 en Vertex |
| `MCP_DISCOVERY_CACHE=1` | v2.1.221+, apagado salvo rollout | Cachea la lista de tools entre sesiones ("cached 2h ago · connects on first use") |
| **`MAX_MCP_OUTPUT_TOKENS`** | **default 25.000**, aviso a partir de 10.000 | Por encima, el texto se persiste a disco y se sustituye por una referencia de fichero |
| `_meta["anthropic/maxResultSizeChars"]` | tope duro de 500.000 caracteres | Límite por tool que fija el autor del servidor MCP |
| **`MCP_TOOL_TIMEOUT`** (ms) | **default unas 28 horas**, es decir, casi sin límite | Tope de reloj por llamada. Se puede fijar `timeout` por servidor en `.mcp.json`; valores por debajo de 1000 ms se ignoran |
| `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT` | HTTP/SSE/WebSocket/conectores 5 min; stdio 30 min | Aborta llamadas sin respuesta ni notificación de progreso |
| `MCP_TIMEOUT` | 30.000 ms | Timeout de arranque y conexión del servidor |
| `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS` | 120000; `0` desactiva | Manda a segundo plano las llamadas largas |
| `/mcp enable|disable [servidor|all]` | — | Apagar servidores sin borrar la configuración; se guarda por proyecto en `~/.claude.json` |
| `disableClaudeAiConnectors`, `deniedMcpServers`, `ENABLE_CLAUDEAI_MCP_SERVERS=false` | — | Quitar conectores de claude.ai |

La doc de costes es explícita: **prefiere CLIs (`gh`, `aws`, `gcloud`, `sentry-cli`) a servidores MCP**, porque no añaden listado por herramienta.

### 2.4 Bash y salidas voluminosas

- **`BASH_MAX_OUTPUT_LENGTH`** (env): default **30.000** caracteres, máximo 150.000, solo dígitos.
- **`bashOutputMaxChars`** (settings.json, v2.1.261+): mismo efecto; Claude Code lo capa al rango **4.000 a 128.000**.
- `BASH_DEFAULT_TIMEOUT_MS` (120.000 ms) y `BASH_MAX_TIMEOUT_MS` (600.000 ms).
- Tope nuevo en 2.1.265: **1 GB** para resultados de herramienta guardados a disco.

### 2.5 Skills, memoria, hooks, plugins y limpieza

| Ajuste | Default | Efecto sobre el coste |
|---|---|---|
| **`skillListingBudgetFraction`** | **`0.01`, es decir el 1 % de la ventana** | Presupuesto del listado de skills que se manda **en cada turno**. Al desbordarse se conservan todos los nombres pero **se tiran las descripciones de las skills que menos invocas** |
| **`skillListingMaxDescChars`** | **`1536`** | Tope de caracteres de `description` más `when_to_use` por skill en el listado |
| `SLASH_COMMAND_TOOL_CHAR_BUDGET` (env) | — | Fija el presupuesto del listado en un número de caracteres |
| `skillOverrides` | — | `"on"`, `"name-only"`, `"user-invocable-only"`, `"off"`. `name-only` libera presupuesto sin perder la skill |
| `disableBundledSkills` y `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS=1` | apagado | Quita las skills y workflows incluidos |
| `autoMemoryEnabled` y `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` | `true` | Auto memory. Se cargan **las primeras 200 líneas o 25 KB de MEMORY.md** en cada sesión; los ficheros de tema se leen bajo demanda |
| `autoMemoryDirectory` | `~/.claude/projects/PROYECTO/memory/` | Ruta absoluta o que empiece por `~/` |
| `claudeMdExcludes` | `[]` | Saltar CLAUDE.md ajenos en monorepos, con globs sobre rutas absolutas; los arrays se fusionan entre capas |
| `claudeMd` | — | CLAUDE.md de organización embebido en managed settings |
| `disableAllHooks` | apagado | Apaga los hooks **y además la status line personalizada y el comando de sugerencia de ficheros** |
| `allowManagedHooksOnly`, `allowedHttpHookUrls`, `httpHookAllowedEnvVars` | — | Restricciones de hooks para organizaciones |
| **`promptCacheTtl`** y `subagentPromptCacheTtl` | sin fijar | `"5m"` o `"1h"` (v2.1.242+). Precedencia, de mayor a menor: `FORCE_PROMPT_CACHING_5M`, `CLAUDE_CODE_PROMPT_CACHE_TTL`, el setting, y por último `ENABLE_PROMPT_CACHING_1H` |
| `DISABLE_AUTOUPDATER` | apagado | Desactiva la autoactualización del CLI **y la de los plugins de marketplace**; `FORCE_AUTOUPDATE_PLUGINS=1` mantiene la de plugins |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | apagado | Corta el tráfico no esencial. Ojo: **también apaga el fetch de feature flags, así que deja sin `/skill-doctor`** y, antes de 2.1.246, sin arranque autónomo de `/code-review` |
| `includeCoAuthoredBy` | `true` | **Deprecado desde v2.0.62**: usa `attribution` (`attribution.commit`, `attribution.pr`, `attribution.sessionUrl`). Se sigue honrando `false` en ficheros antiguos, pero se ignora en cuanto fijas `attribution.commit` o `attribution.pr` |
| `cleanupPeriodDays` | **30** | Días de retención de transcripts y datos de aplicación. Los ficheros de memoria quedan excluidos de la purga |
| `crossSessionInbound` | `"notice"` | Con `hold`, un mensaje de otra sesión no arranca un turno que mandaría el contexto completo |
| `CLAUDE_CODE_GOAL_CHECKIN_MINUTES=0` | — | Apaga los check-ins de `/goal` en reposo, que mandan el contexto entero |
| `fastMode`, `fastModePerSessionOptIn`, `CLAUDE_CODE_DISABLE_FAST_MODE=1` | apagado | Fast mode: **10 USD / 50 USD por Mtok** en Opus 5 y Opus 4.8, solo con usage credits en planes de suscripción. La primera vez que lo activas en una conversación pagas el contexto entero como input sin cachear a precio de fast mode, así que conviene activarlo al principio |
| `--bare`, `--restricted` o `CLAUDE_CODE_RESTRICTED=1`, `--safe-mode` o `CLAUDE_CODE_SAFE_MODE` | — | Arrancar sin hooks, skills, plugins, MCP ni memoria. Es lo más barato y reproducible para CI |
| `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` | — | Desde 2.1.268 las tools de tareas solo se ofrecen en Claude 3.x, Opus 4.0-4.7, Sonnet 4.0-4.6 y Haiku 4.5; en el resto hay que activarlas a mano |

---

## 3. COMANDOS DE SESIÓN

**Fuente:** https://code.claude.com/docs/en/commands.md (tabla "All commands")

| Comando | Qué hace hoy |
|---|---|
| `/context [all]` | Visualiza el uso de contexto como rejilla de colores, con sugerencias de optimización para tools pesadas y memory bloat, y aviso cuando la conversación excede la ventana. En fullscreen colapsa el desglose; `all` lo expande. La fila Skills refleja el listado **ya recortado por el presupuesto**, así que coincide con lo que recibe el modelo. Desde 2.1.261 estima tokens en local cuando la API de conteo no está disponible, en vez de gastar peticiones a un modelo pequeño. **No tiene salida no interactiva**: no figura entre los comandos soportados en `-p` |
| `/cost` | **Alias de `/usage`** |
| `/usage` | Uso y coste de la sesión: coste total, duración de API y de reloj, tokens por modelo. Desde 2.1.251 añade la línea **`Prompt cache (main)`**: peticiones, porcentaje de input servido desde caché, fallos con tokens re-cacheados, reconstrucciones esperadas y estado warm/cold con el TTL; desde 2.1.260 nombra la **causa probable** del último fallo de caché. En planes de suscripción añade **atribución de uso a skills, subagentes, plugins y servidores MCP individuales**, banderas de comportamiento (cuando algo supone 10 % o más del uso) y filas de `/loop` (2.1.242+). `d` y `w` cambian entre 24 horas y 7 días. Los totales se reinician con `/clear` desde 2.1.211 |
| `/compact [instrucciones]` | Resume la conversación; acepta instrucciones de foco, por ejemplo `/compact céntrate en el bug de auth`. También puedes fijar instrucciones permanentes en el CLAUDE.md bajo una sección `# Compact instructions`. Compactar un contexto grande es en sí una petición grande |
| `/autocompact [auto|tokens]` | Fija la ventana de auto-compact (`500k`, `1M`, `200`…). Requiere v2.1.221+ |
| `/clear [nombre]` | Nueva conversación con contexto vacío; alias `/reset` y `/new`. **No cuesta tokens**, a diferencia de `/compact` |
| `/model [modelo]` | Cambia de modelo y lo guarda como default. En el picker, `Enter` guarda y `s` aplica solo a esta sesión (v2.1.257+); las flechas izquierda y derecha ajustan el slider de esfuerzo. Funciona en `-p` pasando el modelo como argumento |
| `/effort [nivel|auto|status]` | `low` a `xhigh`, `max`, `ultracode` o `auto`; `status` lo imprime. `max` y `ultracode` son de sesión. Desde 2.1.251 guarda el nivel **por modelo**; desde 2.1.257 `s` aplica solo a esta sesión. Funciona en `-p` salvo durante el "effort hold" de un modelo nuevo |
| `/loop [intervalo] [prompt]` | **Skill incluida.** Repite un prompt mientras la sesión siga abierta. Sin intervalo, Claude se marca el ritmo; sin prompt usa el prompt de mantenimiento integrado o tu `loop.md`. Alias `/proactive`. **Cada iteración manda el contexto completo**, así que vigílalo en las filas Loops de `/usage` |
| `/fast [on|off]` | Activa o desactiva fast mode (Opus 5 y Opus 4.8; 10/50 USD por Mtok; usage credits). Se puede ejecutar a mitad de turno. En `-p` solo funciona si arrancaste con `--settings '{"fastMode": true}'` |
| `/config [clave=valor ...]` | Abre Settings o fija ajustes directamente. **El formato clave=valor funciona en `-p` y en Remote Control**, por ejemplo `/config thinking=false` |
| `/doctor` | **Skill incluida.** Chequeo de instalación y de configuración: instalaciones duplicadas o restos, problemas de PATH, ficheros de settings ilegibles, **skills, servidores MCP y plugins sin usar frente a su coste de contexto**, hooks lentos, versión nueva en tu canal de release, deduplicación de CLAUDE.md locales contra los versionados, **recorte de los CLAUDE.md versionados** cortando lo que Claude puede deducir del código (v2.1.206+), migración de la guía siempre-cargada a skills y CLAUDE.md anidados, y ofertas para poner auto mode por defecto y pre-aprobar comandos de solo lectura denegados con frecuencia. Informa primero y pide confirmación antes de tocar nada. Desde el terminal, `claude doctor` imprime el diagnóstico de instalación sin abrir sesión. Alias `/checkup` |
| `/skill-doctor` | Muestra **lo que cuesta en contexto cada skill y con qué frecuencia se usa**, para poder apagarlas. En sesión interactiva abre la pestaña **Stats** de `/plugin`; en `-p` lo imprime como texto. Cubre las skills de tu sesión salvo las bundled y las de empresa; marca las que nunca se han invocado y dice dónde apagarlas; también lista plugins sin uso reciente. **Requiere v2.1.252 o posterior y fetch de feature flags**: no está disponible con la telemetría o el tráfico no esencial desactivados, ni por Remote Control (responde "Skill usage reports are not available on this connection") |
| `/code-review [low|medium|high|xhigh|max|ultra] [--fix] [--comment] [--post] [pr#|rama|ruta]` | **Skill incluida.** Revisa los commits de tu rama por delante del upstream más los cambios sin commitear, o el target que pases. Desde 2.1.218 corre como **subagente en segundo plano**, así que la revisión no llena tu conversación. Sin nivel, **reutiliza el último que tecleaste**, incluso de una sesión anterior (2.1.223+). Niveles bajos dan menos falsos positivos; altos amplían cobertura. `ultra` lanza **ultrareview en la nube** (requiere cuenta claude.ai; no disponible en Bedrock, Vertex, Foundry ni con Zero Data Retention, donde cae a revisión local). `--fix` aplica los hallazgos al working tree, `--comment` los publica en el PR de GitHub o como nota única en el merge request de GitLab. Alias `/review` |
| `/security-review [...]` | **Skill incluida.** Lo mismo, orientado a vulnerabilidades |
| `/memory` | Edita los CLAUDE.md, activa o desactiva la auto memory y abre la carpeta de memorias |
| `/rewind` | Retrocede la conversación y/o el código a un checkpoint, o resume desde/hasta un mensaje seleccionado. Alias `/checkpoint` y `/undo` |
| `/resume [nombre]` | Vuelve a una conversación anterior o a una rama creada con `/branch` |
| `/statusline` | Configura la status line, que puede mostrar contexto usado, coste y el objeto `prompt_cache` |
| `/insights` | Informe HTML de tus sesiones recientes (hasta 200 sin analizar por ejecución) en `~/.claude/usage-data/report.html` |
| `/plugin` | Gestor de plugins con pestañas Discover, Installed, Marketplaces, Errors y **Stats** |

**No interactivo (`claude -p`):** las skills y comandos de usuario funcionan poniendo `/nombre` dentro del prompt, y Claude Code los expande antes de ejecutar. Aceptan valor como argumento `/model`, `/effort`, `/fast`, `/color` y `/rename`; `/config clave=valor` fija ajustes; `/mcp` sin argumento imprime un resumen de estado; `/theme` también funciona. Todos requieren v2.1.205 o posterior. Los comandos que solo existen en el terminal, como `/login`, no están disponibles. **`/context` y `/usage` no están en esa lista**: para métricas de gasto en scripts usa `--output-format json`, cuyo payload trae `total_cost_usd` y un desglose de coste por modelo (ambos estimaciones de cliente), o exporta por OpenTelemetry.

---

## 4. SKILLS

**Fuente:** https://code.claude.com/docs/en/skills.md

### 4.1 Frontmatter completo (tabla oficial)

| Campo | Requerido | Notas |
|---|---|---|
| `name` | No | Nombre mostrado en los listados. Por defecto, el del directorio |
| `description` | Recomendado | Qué hace y cuándo usarla. Si falta, se usa la primera línea no vacía del cuerpo. **`description` más `when_to_use` se truncan a 1.536 caracteres en el listado** |
| `when_to_use` | No | Contexto adicional de activación, con frases disparadoras o ejemplos. Se añade a `description` y cuenta para el mismo tope |
| `argument-hint` | No | Pista de autocompletado, por ejemplo `[issue-number]` |
| `arguments` | No | Argumentos posicionales con nombre para sustitución `$nombre` |
| **`disable-model-invocation`** | No | `true` impide que Claude la cargue por su cuenta. También impide precargarla en subagentes y, desde 2.1.196, que la dispare una tarea programada. Default `false` |
| **`user-invocable`** | No | `false` la oculta del menú `/` y evita que se ejecute al teclear `/nombre`: solo Claude. Default `true` |
| **`allowed-tools`** | No | Tools pre-aprobadas **solo durante el turno** que invoca la skill; el permiso se borra con tu siguiente mensaje. No restringe otras ni pisa reglas deny |
| `disallowed-tools` | No | Tools retiradas del pool mientras la skill está activa |
| **`model`** | No | Modelo para ese turno, o el del subagente si hay `context: fork`; `inherit` mantiene el de la sesión. Un valor excluido por `availableModels` se ignora |
| `effort` | No | `low`, `medium`, `high`, `xhigh`, `max` para ese turno |
| **`context`** | No | `fork` para correr en un subagente aislado |
| `agent` | No | Qué tipo de subagente usar con `context: fork` (`Explore`, `Plan`, `general-purpose`…) |
| `background` | No | Solo con `fork`. **Default `true` desde v2.1.218**; `false` bloquea el turno hasta tener resultado |
| `hooks` | No | Hooks registrados al invocar la skill, que siguen activos el resto de la sesión |
| **`paths`** | No | **Sí existe.** Globs que limitan la auto-invocación a ficheros que casen. Mismo formato que las reglas con `paths` |
| `shell` | No | `bash` (default) o `powershell` para los comandos inline |
| `metadata`, `license`, `compatibility` | No | Spec de Agent Skills. Claude Code los acepta pero no actúa sobre ellos (`compatibility` admite hasta 500 caracteres) |

Los booleanos aceptan `true`, `false`, `yes`, `no`, `on`, `off`, `1` y `0` sin distinguir mayúsculas, desde v2.1.218. Fuera de Claude Code (subidas a claude.ai, Skills API, `package_skill.py`) solo valen `name`, `description`, `license`, `compatibility`, `metadata` y `allowed-tools`.

### 4.2 Qué cuesta cada skill en el prompt

- **Siempre en contexto, en cada turno:** un listado con el **nombre de todas** las skills y sus descripciones.
- El listado se capa a **`skillListingBudgetFraction`, por defecto el 1 % de la ventana del modelo**. Al desbordar, **se conservan todos los nombres y se van tirando descripciones empezando por las skills que menos invocas**, y se escribe un aviso al log de depuración, visible con `--debug`. Una skill sin descripción sigue siendo invocable, pero Claude tiene menos probabilidad de elegirla por su cuenta.
- Cada entrada se corta a **1.536 caracteres** (`skillListingMaxDescChars`), independientemente del presupuesto global.
- **Sí hay carga diferida del cuerpo:** el `SKILL.md` completo entra en contexto **solo al invocarla**, y a partir de ahí permanece toda la sesión y **no se vuelve a leer** en turnos posteriores, así que conviene escribir instrucciones "de pie" para tareas multi-turno. Reinvocarla con el mismo contenido renderizado produce solo una nota corta; con argumentos o contexto dinámico distintos, vuelve a entrar entera.
- Tras compactar: se reinyecta la última invocación de cada skill con tope de **5.000 tokens por skill y 25.000 en total**.
- Para medir y podar: `/skill-doctor`, `/doctor` y la fila Skills de `/context`.

### 4.3 Rutas de descubrimiento

Por orden de precedencia: managed settings de empresa, **`~/.claude/skills/`** (personal), **`.claude/skills/`** del proyecto y de **todos los directorios padre hasta la raíz del repo**, **`.claude/skills/` anidados por debajo del directorio de arranque**, `.claude/skills/` de directorios añadidos con `--add-dir`, **plugins** (carpeta `skills/` del plugin, con namespace `/plugin:skill`) y skills de la cuenta claude.ai (solo Cowork y cloud, descargadas a `~/.claude/skills/synced/`). Sigue funcionando `.claude/commands/fichero.md`, que se convierte internamente en skill. Se admiten symlinks en todas las ubicaciones que no son de plugin. Nombre reservado: no llames `synced` a una carpeta de skills.

### 4.4 SKILL.md anidados en subdirectorios: issue 18192

**El issue `anthropics/claude-code#18192` ("Recursive skill discovery: scan subdirectories in ~/.claude/skills/") está CERRADO desde el 2026-08-17** (se abrió el 2026-01-14). Estado real hoy, según la documentación:

- **Sí** se descubren los **`.claude/skills/` anidados** (por ejemplo `apps/web/.claude/skills/deploy/SKILL.md`): **no cargan al arrancar**, sino la primera vez que Claude lee o edita un fichero de ese subdirectorio, y luego quedan disponibles el resto de la sesión. Se pueden precargar con `/add-dir`. Si colisionan nombres, conviven los dos: `/deploy` para la de raíz y `/apps/web:deploy` para la anidada.
- **La vía soportada para agrupar skills dentro de una carpeta** (el caso exacto del issue, `~/.claude/skills/spec-system/spec-creator/`) es convertir la carpeta contenedora en un **plugin de directorio de skills**: `claude plugin init mi-suite` crea `~/.claude/skills/mi-suite/` con su `.claude-plugin/plugin.json` y una SKILL.md de partida, y en la siguiente sesión carga como **`mi-suite@skills-dir`** sin marketplace ni instalación, con sus skills anidadas dentro. Desde 2.1.221 los plugins aceptan `"."` como ruta de `skills`, y un plugin de una sola skill puede poner el SKILL.md en su raíz.
- **Lo que sigue sin documentarse** es la recursión "a pelo" dentro de `~/.claude/skills/` sin manifest: la estructura documentada de una skill es una carpeta con su `SKILL.md` más ficheros de apoyo.

---

## 5. RULES: `.claude/rules/*.md`

**Fuente:** https://code.claude.com/docs/en/memory.md, sección "Organize rules with .claude/rules/"

**Sí existe oficialmente hoy.** Datos exactos:

- Ficheros `.md` en `.claude/rules/` del proyecto, uno por tema. **Descubrimiento recursivo**, así que admite subcarpetas como `frontend/` o `backend/`.
- **Frontmatter exacto**: solo el campo `paths`, como lista YAML de globs.

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules

- All API endpoints must include input validation
- Use the standard error response format
```

  Con varios patrones y expansión de llaves: `"src/**/*.{ts,tsx}"`, `"lib/**/*.ts"`, `"tests/**/*.test.ts"`.
- **Cuándo se cargan:**
  - **Sin `paths`: al arrancar**, con la misma prioridad que `.claude/CLAUDE.md`.
  - **Con `paths`: bajo demanda, cuando Claude lee un fichero que casa** con el patrón, no en cada uso de herramienta. Desde v2.1.198 también casan cuando el fichero se alcanza por una ruta con symlink al directorio del proyecto.
- Tras compactar, las reglas con `paths` **se recargan cuando Claude vuelve a leer un fichero que casa**. Si una regla debe persistir siempre, quítale el `paths` o muévela al CLAUDE.md de raíz.
- Presupuesto de globs: la lista `paths` de una regla comparte **1.000 patrones expandidos y 4 MiB**. Un patrón que lo excediera se usa **sin expandir**, y entonces sus llaves literales no casan con nada. Antes de v2.1.217 un `paths` con muchos grupos de llaves colgaba o mataba el CLI al arrancar; el mismo arreglo aplica al `paths` de SKILL.md.
- El corchete de apertura se interpreta como expresión de corchetes; para buscarlo literal hay que escaparlo (`photos \[2024/**`). Antes de v2.1.207, un patrón inválido hacía fallar la tool Read para todos los ficheros contra los que se evaluaba la regla.
- `~/.claude/rules/` son reglas personales para todos los proyectos; se cargan **antes** que las de proyecto, de modo que las de proyecto tienen prioridad.
- Se admiten symlinks; si el destino cae fuera del working directory se tratan como import externo: no cargan hasta que apruebas imports externos del proyecto y, aun entonces, solo las que **no** tienen `paths`.
- Se saltan si excluyes `project` de `--setting-sources`. Antes de v2.1.211, las reglas de carga bajo demanda (con `paths` y las anidadas) cargaban igualmente.
- Se pueden excluir con `claudeMdExcludes`; desde v2.1.239 basta con que el patrón case la ruta bajo `.claude/rules/` o la del destino del symlink.
- Para depurar qué instrucciones se cargan, cuándo y por qué: **hook `InstructionsLoaded`**, añadido en 2.1.69.
- Consejo de la propia doc: las reglas están en contexto siempre o al tocar ficheros que casan; si algo solo hace falta de vez en cuando, **eso es una skill**, que solo carga al invocarse.

---

## 6. SUBAGENTES

**Fuente:** https://code.claude.com/docs/en/sub-agents.md

### 6.1 Frontmatter de `.claude/agents/*.md`

**Obligatorios:** `name` (minúsculas y guiones, sin dos puntos; llega a los hooks como `agent_type`) y `description`.

**Opcionales:**

| Campo | Valores | Qué hace |
|---|---|---|
| `tools` | lista de tools, admite `Agent(subagent_type)` | Allowlist. Si se omite, hereda todas las tools disponibles para subagentes |
| `disallowedTools` | lista | Se aplica antes que `tools` |
| `model` | `sonnet`, `opus`, `haiku`, `fable`, ID completo o `inherit` | Modelo del subagente |
| `permissionMode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`, `manual` | Modo de permisos. Se ignora en subagentes de plugin |
| **`maxTurns`** | entero positivo | Turnos máximos; al alcanzarlo devuelve la salida marcada como parcial |
| `skills` | lista de nombres | Precarga skills en el subagente: **inyecta el contenido completo**, no solo la descripción |
| `mcpServers` | nombres o definiciones inline | Servidores MCP disponibles solo para ese subagente |
| `hooks` | objeto | Hooks con alcance de ese subagente |
| **`memory`** | `user`, `project`, `local` | Memoria persistente propia del subagente para aprendizaje entre sesiones |
| `background` | booleano | Mantenerlo en segundo plano aunque Claude lo pida en primer plano. Default `false` |
| `effort` | `low` a `max` | Nivel de esfuerzo mientras está activo |
| **`isolation`** | `worktree` | Lo ejecuta en un git worktree temporal con copia aislada del repositorio |
| `color` | 8 colores | Color en la lista de tareas y el transcript |
| `initialPrompt` | texto | Primer turno autoenviado cuando corre como agente de sesión con `--agent` |
| **`experimental`** | `{ cacheTtl: "5m" o "1h" }` | TTL de caché de prompt por agente, usado si no hay ajuste global de subagentes (añadido en 2.1.248) |

### 6.2 Coste de contexto: sí se paga en cada sesión

Cita literal de la doc: *"Subagent descriptions consume context in every session"*. Hay un **límite de 15.000 tokens para las descripciones combinadas de todos los subagentes personalizados**; al superarlo Claude Code muestra un aviso de arranque con el total. Las descripciones de los subagentes integrados **no** cuentan para ese límite. Recomendación oficial: descripciones breves y todo el detalle en el cuerpo markdown, que es el system prompt del subagente y solo carga cuando ese subagente corre.

Rutas, por prioridad: managed settings, flag `--agents`, `.claude/agents/` del proyecto (subiendo desde el cwd hasta la raíz del repo, con la definición más cercana ganando), `~/.claude/agents/` y, por último, la carpeta `agents/` de los plugins. Escaneo recursivo; los subdirectorios no afectan a la identidad, solo cuenta el campo `name`.

Palanca de ahorro clave, según la propia doc de costes: **delegar lecturas y salidas voluminosas a subagentes**, porque el contenido se queda en su ventana y a la principal solo vuelve el resumen. La auto memory de la conversación principal **no** se carga en los subagentes, salvo en un `fork`, que hereda conversación y system prompt. Para tareas simples de subagente, `model: haiku`.

Aviso de coste opuesto: los **agent teams** usan aproximadamente **7 veces más tokens** que una sesión normal cuando los compañeros corren en plan mode, porque cada uno mantiene su propia ventana y su propia instancia. Están desactivados por defecto (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`).

---

## 7. PLUGINS, MARKETPLACES Y `claude plugin eval`

**Fuentes:** https://code.claude.com/docs/en/plugins.md · https://code.claude.com/docs/en/discover-plugins.md · https://code.claude.com/docs/en/plugin-marketplaces.md

### 7.1 Qué inyecta un plugin habilitado y cómo se mide

Componentes posibles, todos en la **raíz** del plugin salvo el manifiesto (dentro de `.claude-plugin/` solo va `plugin.json`): `skills/`, `commands/`, `agents/`, `hooks/hooks.json`, `.mcp.json`, `.lsp.json`, `monitors/monitors.json`, `bin/` (se añade al PATH de la tool Bash mientras el plugin está activo) y `settings.json` de plugin (solo se admiten las claves `agent` y `subagentStatusLine`).

Campos del manifiesto `plugin.json`: `name` (identificador y namespace de las skills), `description`, `version` (opcional; si se fija, los usuarios solo reciben actualizaciones al subirla), `author`, y además `homepage`, `repository`, `license`.

Coste en contexto: las **skills** aportan nombre y descripción al listado de **cada turno**; los **agentes** aportan su descripción en **cada sesión** y cuentan para el tope de 15.000 tokens; los **servidores MCP** aportan los nombres de sus tools (los esquemas van diferidos con tool search); los **hooks** solo gastan al dispararse, salvo los de tipo `prompt` y `agent`, que llaman al modelo.

Cómo medirlo:

- **`/plugin`, pestaña Discover, detalle del plugin**: muestra una estimación de **Context cost** ("cuántos tokens añade el plugin a tu ventana de contexto en cada turno"), la fecha de **Last updated** y una sección **Will install** con los comandos, agentes, skills, hooks y servidores MCP y LSP que aporta. No todos los plugins publican estos datos; los de marketplaces locales o personalizados pueden mostrar "Components will be discovered at installation".
- **`/plugin`, pestaña Stats**: lo que cuesta cada skill y cuánto se usa. Es la misma vista que abre `/skill-doctor`.
- **`/plugin`, pestaña Installed**: cabecera **"Not used recently"** para los plugins que instalaste tú y llevas sin usar al menos dos semanas y 10 sesiones, con una línea **Last used** en el detalle. Quedan fuera los gestionados por la organización, los de `--plugin-dir` y los que solo aportan tema, output style, monitor o workflow.
- `/context`, `/doctor` y `claude plugin details` desde la línea de comandos.
- Recargar plugins tiene coste en la siguiente petición: los componentes nuevos se anuncian en contenido añadido a la conversación. Si el plugin aporta servidores MCP no diferidos, **invalida la caché de prompt** y la siguiente petición reenvía la conversación entera.

### 7.2 `claude plugin eval`: estado real

- **Está en acceso anticipado (early access) y se habilita por organización. No hay página pública de documentación todavía**, así que no te doy URL: no existe.
- **En esta sesión NO está habilitado.** El comando existe, pero imprime "plugin eval is currently in early access" y sale con código 1. Que aparezca ese mensaje no significa que el comando no exista.
- Qué hace: ejecuta cada caso de eval (un prompt más sus graders) en una sesión `claude -p` aislada y limpia, con solo el plugin bajo prueba cargado, varias veces, y lo puntúa. Opcionalmente corre también un brazo **baseline** sin el plugin y reporta el delta. Los casos viven en `evals/CASO/prompt.md` y `evals/CASO/graders/*.md`. Tipos de grader: `regex`, `tool_used`, `tool_order`, `file_exists`, `llm` y `baseline`. Salidas: progreso por stderr, tabla resumen por stdout, y en `results/TIMESTAMP/` un `aggregate-result.json` y un `report.html`.
- Habilitación: los clientes de primera parte ya habilitados lo recogen solos tras `claude update` y una sesión nueva. Los clientes que no pueden leer feature flags del servidor (Bedrock, Vertex, Foundry, gateways o `ANTHROPIC_BASE_URL` propio, o con `DISABLE_TELEMETRY`, `DO_NOT_TRACK`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` o `DISABLE_GROWTHBOOK`) necesitan **una variable de entorno de habilitación que se entrega durante el onboarding**. No invento su nombre: hay que pedirla al contacto de Anthropic.
- Autotest rápido: ejecutar `claude plugin eval` en un directorio vacío. Si responde "early access", no está habilitado; si responde "No eval cases found", sí lo está.
- Lo que sí es público y estable: **`claude plugin validate RUTA`** (valida la estructura; desde 2.1.233 también revisa un `.claude/skills` suelto y reporta los SKILL.md cuyo frontmatter no parsea; `--strict` convierte los avisos en errores) y **`claude plugin list --json`** (con `errorDetails` y `noteDetails` desde 2.1.268).

### 7.3 Marketplace oficial `anthropics/claude-plugins-official`

Claude Code lo añade solo la primera vez que arrancas de forma interactiva. Si no está: `/plugin marketplace add anthropics/claude-plugins-official`. Catálogo navegable en https://claude.com/plugins. Instalación: `/plugin install NOMBRE@claude-plugins-official`.

Plugins de hoy relevantes para tus cuatro ejes:

- **Revisión de código:** `pr-review-toolkit` (agentes especializados para revisar pull requests) y `commit-commands` (flujos de commit, push y creación de PR).
- **Seguridad:** **`security-guidance`**, que revisa cada cambio que hace Claude buscando vulnerabilidades comunes y le indica arreglarlas en la misma sesión. Doc: https://code.claude.com/docs/en/security-guidance.md
- **Tokens y contexto:** los **plugins de code intelligence (LSP)** son los que la doc de costes recomienda de forma explícita para gastar menos, porque dan navegación por símbolos y diagnósticos automáticos tras cada edición en lugar de grep más lectura de varios ficheros candidatos. Son `typescript-lsp`, `pyright-lsp`, `rust-analyzer-lsp`, `gopls-lsp`, `clangd-lsp`, `csharp-lsp`, `jdtls-lsp`, `kotlin-lsp`, `lua-lsp`, `php-lsp` y `swift-lsp`. Hay que instalar aparte el binario del language server. No arrancan en sesiones cloud.
- **Calidad de skills:** **`skill-creator`**, que automatiza el bucle de evaluación con y sin la skill; lo recomienda la propia doc de skills.
- **Desarrollo:** `plugin-dev` y `agent-sdk-dev`. **Output styles:** `explanatory-output-style` y `learning-output-style`. **Integraciones MCP:** `github`, `gitlab`, `atlassian`, `asana`, `linear`, `notion`, `figma`, `vercel`, `firebase`, `supabase`, `slack` y `sentry`.
- **Memoria:** hoy no hay plugin oficial de memoria; eso lo cubre la auto memory nativa en `~/.claude/projects/PROYECTO/memory/`.

Marketplace comunitario: `anthropics/claude-plugins-community`, que se añade a mano y del que se instala con `@claude-community`; cada plugin queda fijado a un commit SHA concreto. Marketplace de demo: `anthropics/claude-code`.

---

## 8. CHANGELOG junio a septiembre de 2026, con versiones y fechas reales

**Fuente:** https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md (fichero crudo) más las fechas de release de la API de GitHub. Ventana: **v2.1.160 (2026-06-02) hasta v2.1.268 (2026-09-10)**.

### 8.1 Tokens, contexto, caché y compactación

| Versión (fecha) | Entrada |
|---|---|
| **2.1.267** (09-09) | Añadido `maxEffortLevel`: tope de esfuerzo global o por modelo, aplicado en todos los proveedores, Bedrock, Vertex y Foundry incluidos |
| **2.1.267** | Estabilidad de caché: subagentes y sesiones con `--system-prompt` o `--append-system-prompt` registran el system prompt y las definiciones de tools una sola vez en vez de re-renderizarlas |
| **2.1.267** | Arreglado: cambiar de modelo con `/model` reenviaba todas las definiciones de tools, fallo total de caché. La atribución de commits y PR pasa a ser una nota de conversación |
| **2.1.267** | Arreglado: tools MCP y de plugin añadidas a mitad de sesión sin ToolSearch rompían la reutilización de caché; ahora llegan como definiciones diferidas |
| **2.1.265** (09-08) | Tope de 1 GB para los resultados de herramienta guardados a disco, con aviso de truncado en el preview |
| **2.1.261** (09-04) | `/context` usa **estimación local** cuando la API de conteo de tokens no está disponible, en vez de peticiones extra a un modelo pequeño |
| **2.1.261** | Añadido `bashOutputMaxChars` (salida de Bash inline configurable) |
| **2.1.260** (09-03) | Auto-compact mejorado para modelos de 1M: Opus y Fable compactan poco antes del límite de 1M, y la compactación de recuperación en contextos enormes deja de expirar a los 10 minutos |
| **2.1.260** | `/cost` y el campo `prompt_cache` de la status line indican la **causa probable** de un fallo de caché |
| **2.1.260** | `/effort` en Fable 5.1 ya no invalida la caché al cambiar a mitad de sesión |
| **2.1.257** (09-01) | **Claude Fable 5.1** (`claude-fable-5-1`), nuevo Fable por defecto: 1M de contexto, **10/50 USD por Mtok** y lecturas de caché a **0,25 USD/Mtok** |
| **2.1.257** | `s` en `/effort` cambia el esfuerzo solo para la sesión actual |
| **2.1.251** (08-28) | **Línea de caché de prompt por sesión en `/cost`**: ratio de acierto, fallos, tokens re-cacheados, warm/cold, más un objeto `prompt_cache` para los scripts de status line |
| **2.1.251** | `/effort` guarda el nivel por defecto **por modelo** |
| **2.1.248** (08-27) | Añadido `experimental.cacheTtl` (`"5m"` o `"1h"`) en el frontmatter de agentes |
| **2.1.247** (08-26) | La ventana de auto-compact de Sonnet 5 pasa a su 1M completo: **compacta a unos 967K en vez de unos 934K** |
| **2.1.243** (08-23) | Añadidos `promptCacheTtl` y `subagentPromptCacheTtl`: caché de 1 hora en la conversación principal y 5 minutos en subagentes, para usuarios de API key y proveedores cloud |
| **2.1.243** | Añadido el desglose **Loops** en `/usage`: ejecuciones, tokens totales, tokens por ejecución y última ejecución de cada `/loop` |
| **2.1.229** (08-12) | Los fan-outs de workflow escalonan a los agentes hermanos para que lean el prefijo cacheado en vez de volver a pagarlo (`CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS=0` lo desactiva) |
| **2.1.223** (08-06) | `CLAUDE_CODE_DISABLE_1M_CONTEXT` retiene a 200K a todo modelo con 1M nativo; auto-compact mantiene los IDs desconocidos dentro de la ventana asumida (`CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1` revierte) |
| **2.1.221** (08-04) | Tool search reactivado en Vertex para modelos de generación 4.5 y posteriores; coste de caché reducido en los chequeos de permisos de auto mode; el panel Stats cuenta tokens de caché con desglose |
| **2.1.219** (07-24) | **Claude Opus 5** (`claude-opus-5`), nuevo Opus por defecto: 1M de contexto, fast mode a 10/50 USD por Mtok |
| **2.1.217** (07-21) | Un `paths` de CLAUDE.md o SKILL.md con muchos grupos de llaves ya no cuelga ni mata el CLI al arrancar |
| **2.1.216** (07-20) | `/context` avisa de forma explícita cuando la conversación excede la ventana, y un `/compact` fallido se muestra como error |
| **2.1.208** (07-14) | Arreglado: `CLAUDE_CODE_MAX_OUTPUT_TOKENS` y variables similares usaban solo la mantisa en notación científica (`1e6` se leía como 1) |
| **2.1.198** (07-01) | **Los subagentes y la compactación heredan la configuración de extended thinking de la sesión**, lo que mejora la calidad en tareas delegadas |
| **2.1.197** (06-30) | **Claude Sonnet 5**: modelo por defecto, 1M nativo, precio promocional de 2/10 USD por Mtok hasta el 31 de agosto |
| **2.1.196** (06-29) | **`/code-review`: cinco buscadores de limpieza fusionados en uno, unos 25 % menos de tokens** |
| **2.1.178** (06-15) | El aviso de truncado del listado de skills indica a cuántas descripciones afecta |
| **2.1.174** (06-12) | El hot-reload de skills deja de reenviar el listado entero cuando cambia una sola |
| **2.1.172** (06-10) | Las sesiones con 1M sin usage credits dejan de quedarse atascadas: compactan de vuelta bajo el límite estándar |
| **2.1.169** (06-08) | Añadido `/cd` para mover la sesión de directorio sin romper la caché de prompt |

### 8.2 Hooks

| Versión | Entrada |
|---|---|
| **2.1.268** (09-10) | Arreglado: los hooks `PermissionRequest` no disparaban en modo `--print`; y `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` no extendía los hooks `SessionEnd` sin `timeout` propio, que se cancelaban a los 1,5 s |
| **2.1.251** (08-28) | **Añadidos `PreModelSwitch` y `PostModelSwitch`** para bloquear, confirmar o anotar un cambio de modelo. Los hooks `SessionStart` de reanudación reciben además la antigüedad de la sesión y **el coste estimado de re-cachear** |
| **2.1.251** | Un hook que imprime en stdout un objeto que no es JSON válido se reporta como error de hook con el mensaje del parser, en vez de tratarse como texto plano |
| **2.1.248** (08-27) | Arreglado: un hook o agente en segundo plano que imprimiera megas de error podía desbordar la conversación y dejar la sesión atascada en "Prompt is too long" |
| **2.1.236** (08-19) | `classifierContext` en PostToolUse: nota sobre el resultado para el clasificador de auto mode |
| **2.1.222** (08-04) | Arreglado: hooks PreToolUse de auto-allow se saltaban restricciones de tools en tareas de agente en segundo plano (resúmenes, compactación, renombrados) |
| **2.1.219** (07-24) | **Añadido el hook `DirectoryAdded`**, que dispara tras `/add-dir` o `register_repo_root` |
| **2.1.214** (07-18) | Las condiciones `if:` de un solo segmento (`dir/**`) casan solo `cwd/dir`; para cualquier profundidad hay que escribir `**/dir/**`. Las reglas de permiso deny y ask conservan el casado a cualquier profundidad |
| **2.1.214** | `SessionStart` reporta `source: "fork"` cuando la sesión nace como fork, en vez de `"resume"` |
| **2.1.198** (07-01) | Las notificaciones de agentes en segundo plano disparan el hook `Notification` (`agent_needs_input` y `agent_completed`) |

### 8.3 Skills

| Versión | Entrada |
|---|---|
| **2.1.261** (09-04) | **Añadido `/skill-doctor`** para ver qué skills cargadas no se usan y cuánto cuestan en contexto, y poder podarlas |
| **2.1.261** | **Huella del Workflow tool reducida: su descripción pasa de unos 5,7k a unos 1k tokens**, moviendo la referencia de escritura de scripts a una skill incluida, `workflow-authoring` |
| **2.1.248** (08-27) | Añadido `--restricted` (o `CLAUDE_CODE_RESTRICTED=1`): quita las tools que ejecutan comandos o código y `WebFetch`, confina las tools de ficheros al working directory, rechaza `bypassPermissions` e ignora los settings de usuario, proyecto y locales |
| **2.1.233** (08-14) | `claude plugin validate` revisa un directorio `.claude/skills` suelto y reporta los SKILL.md con frontmatter ilegible |
| **2.1.222** (08-04) | Cuando Claude intenta invocar una skill con `disable-model-invocation`, ahora se le dice que **te pida que la ejecutes** en vez de replicar su flujo por su cuenta |
| **2.1.221** (08-04) | Los plugins aceptan `"."` como ruta de `skills`, y el error de validación de un SKILL.md en la raíz sugiere usar la raíz del plugin |
| **2.1.218** (07-22) | **Las skills con `context: fork` corren en segundo plano por defecto**; se desactiva por skill con `background: false` |
| **2.1.218** | Los booleanos de frontmatter de skills y plugins aceptan `yes`, `no`, `on`, `off`, `1` y `0` |
| **2.1.210** (07-14) | Añadida la skill incluida `/todos` |
| **2.1.199** (07-02) | Se pueden apilar hasta 6 skills en un mensaje (`/skill1 /skill2 args`) |
| **2.1.198** (07-01) | Añadida la skill `/dataviz`, con validador ejecutable de paleta de color |
| **2.1.186** (06-22) | Sección "Skills" en la pestaña Installed de `/plugin`; el frontmatter acepta kebab-case, snake_case y camelCase en `display-name`, `default-enabled`, `fallback` y `metadata.*`; un YAML malformado carga el cuerpo con metadatos vacíos en vez de fallar en silencio |
| **2.1.169** (06-08) | Añadidos `disableBundledSkills` y `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS`, y `--safe-mode` / `CLAUDE_CODE_SAFE_MODE`, que arranca sin CLAUDE.md, plugins, skills, hooks ni servidores MCP |

Nota: el changelog anuncia `/skill-doctor` en 2.1.261, mientras que la doc dice que requiere v2.1.252 o posterior.

### 8.4 Memoria, CLAUDE.md y rules

| Versión | Entrada |
|---|---|
| **2.1.268** (09-10) | El aviso de truncado de `MEMORY.md` dice **cuántas líneas se cortaron y dónde empieza el corte** |
| **2.1.260** (09-03) | Un CLAUDE.md gestionado (`claudeMd`) vía server-managed settings deja de disparar el diálogo de aprobación de seguridad; hooks, comandos de shell, sandbox y `env` inseguros lo siguen exigiendo |
| **2.1.260** | El `env` de `.claude/settings.json` de proyecto ya no puede fijar `CLAUDE_CONFIG_DIR`, `CLAUDE_CODE_TMPDIR` ni `TMPDIR`, `TMP` o `TEMP` |
| **2.1.239** (08-21) | Tras compactar, los argumentos originales de una skill ya no se re-ejecutan como petición nueva |
| **2.1.234** (08-17) | Seguridad: lecturas remotas, restauración de sesión, includes de CLAUDE.md, scripts de workflow y subidas rechazan rutas NT-namespace de Windows |
| **2.1.214** (07-18) | Marca de tiempo ISO `modified` en el frontmatter de los ficheros de memoria |
| **2.1.211** (07-15) | Las reglas `.claude/rules/*.md` anidadas dejan de cargar cuando se excluyen los settings de proyecto; el aviso de índice de memoria mide solo el contenido cargado, sin frontmatter ni comentarios HTML |
| **2.1.210** (07-14) | Una escritura que deje `MEMORY.md` por encima de su límite de lectura produce un **error explícito** en vez de truncado silencioso |
| **2.1.206** (07-10) | **Añadido el chequeo de `/doctor` que propone recortar los CLAUDE.md versionados**, cortando lo que Claude puede deducir del código |
| **2.1.198** (07-01) | Las reglas condicionales de `.claude/rules/` cargan también cuando el fichero se alcanza por una ruta con symlink |
| **2.1.186** (06-22) | Se recuerda al agente que compacte su índice `MEMORY.md` al acercarse al límite de tamaño |

### 8.5 Revisión de código

| Versión | Entrada |
|---|---|
| **2.1.268** (09-10) | Nota bajo la lista de hallazgos abiertos en revisiones de seguimiento: **resolver el hilo** de un hallazgo, no solo responderle, evita que revisiones posteriores lo sigan contando como abierto |
| **2.1.260** (09-03) | `/code-review --comment` publica los hallazgos en merge requests de GitLab vía `glab mr note` |
| **2.1.260** | `/ultrareview` y `claude ultrareview` esperan hasta **45 minutos** (antes 30) por revisiones cloud largas |
| **2.1.248** (08-27) | `/ultrareview PR#` comprueba antes de lanzar que la cuenta de GitHub conectada puede acceder al repositorio |
| **2.1.246** (08-25) | Claude puede iniciar `/code-review` por su cuenta **también** en Bedrock, Vertex y Foundry, con Claude apps gateway, y con la telemetría o el tráfico no esencial desactivados |
| **2.1.227** (08-10) | Añadido `--post` en `/code-review ultra` para publicar los hallazgos terminados en el PR de github.com |
| **2.1.223** (08-06) | `/review` pasa a ser **alias** de `/code-review`; sin nivel de esfuerzo, se reutiliza el último tecleado; `ultra` lanza la revisión profunda en la nube |
| **2.1.218** (07-22) | **`/code-review` corre como subagente en segundo plano**, así que el trabajo de revisión ya no llena la conversación, y mantiene los comandos apilados como target |
| **2.1.206** (07-10) | Mejor calidad de hallazgos de `/code-review` en `claude-opus-4-8` en todos los niveles de esfuerzo |
| **2.1.202** (07-06) | `/review PR` vuelve a ser una pasada única rápida; el multi-agente es `/code-review NIVEL PR#` |
| **2.1.196** (06-29) | `/code-review` gasta un 25 % menos de tokens al fusionar los cinco buscadores de limpieza |
| **2.1.186** (06-22) | `/review PR` usa el mismo motor que `/code-review medium` |

---

## Apéndice: URLs de referencia

| Tema | URL |
|---|---|
| Hooks (referencia completa) | https://code.claude.com/docs/en/hooks.md |
| Hooks (guía) | https://code.claude.com/docs/en/hooks-guide.md |
| Settings (referencia completa) | https://code.claude.com/docs/en/settings-reference.md |
| Variables de entorno | https://code.claude.com/docs/en/env-vars.md |
| Modelo, esfuerzo, 1M y auto-compact | https://code.claude.com/docs/en/model-config.md |
| Ventana de contexto y compactación | https://code.claude.com/docs/en/context-window.md |
| Caché de prompt | https://code.claude.com/docs/en/prompt-caching.md |
| Costes y cómo reducir tokens | https://code.claude.com/docs/en/costs.md |
| Memoria, CLAUDE.md y rules | https://code.claude.com/docs/en/memory.md |
| Skills | https://code.claude.com/docs/en/skills.md |
| Subagentes | https://code.claude.com/docs/en/sub-agents.md |
| MCP | https://code.claude.com/docs/en/mcp.md |
| Comandos | https://code.claude.com/docs/en/commands.md |
| Plugins (crear) | https://code.claude.com/docs/en/plugins.md |
| Plugins (descubrir e instalar, marketplace oficial) | https://code.claude.com/docs/en/discover-plugins.md |
| Marketplaces | https://code.claude.com/docs/en/plugin-marketplaces.md |
| Code review y ultrareview | https://code.claude.com/docs/en/code-review.md y https://code.claude.com/docs/en/ultrareview.md |
| Fast mode | https://code.claude.com/docs/en/fast-mode.md |
| Headless y `-p` | https://code.claude.com/docs/en/headless.md |
| Changelog | https://code.claude.com/docs/en/changelog.md y https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md |
| `claude plugin eval` | Sin página pública todavía (acceso anticipado) |
