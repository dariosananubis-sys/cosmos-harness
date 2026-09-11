# Informe: qué reduce de verdad el gasto de tokens en Claude Code

**Verificado el 2026-09-11.** Estrellas, licencias y fechas de último commit comprobadas hoy contra
`api.github.com`. Las funciones nativas están contrastadas contra `code.claude.com/docs`,
`platform.claude.com/docs` y el `CHANGELOG.md` oficial de `anthropics/claude-code`. Cada cifra dice
si está **medida** (metodología reproducible publicada) o si es **marketing** (afirmación sin método).

---

## 0. Seis correcciones al encargo, antes de nada

El encargo daba por buenas varias cosas que hoy son falsas. Van primero porque cambian las
conclusiones.

| Lo que se asumía | Lo que dice la fuente hoy |
|---|---|
| `ryoppippi/ccusage` | **Ya no existe con ese nombre.** `api.github.com/repos/ryoppippi/ccusage` devuelve `301 Moved Permanently`. El repo vivo es **`ccusage/ccusage`** (organización propia). Cualquier ficha vieja apunta a una redirección. |
| «`model` con sufijo `[1m]` y **su precio**» | **No hay sobreprecio de contexto largo.** Página de precios, sección *Long context pricing*, literal: *«Claude 4.6 and later models and Claude Mythos Preview include the full 1M token context window at standard pricing. (A 900k-token request is billed at the same per-token rate as a 9k-token request.)»* Opus 5 = **$5/MTok entrada, $25/MTok salida** a cualquier longitud. La ventana de 1M no se paga más cara **por token**; se paga más cara **por cuántos tokens acumulas**, que es otra cosa. |
| «carga diferida de herramientas (tool search)» como algo por activar | **Ya está activa por defecto.** No hay clave en `settings.json`: el único control es la variable de entorno `ENABLE_TOOL_SEARCH`, y *sin definir* significa **diferir todas las definiciones MCP**. La acción no es activarla, es **no romperla**. |
| `modelSettings.effortLevel` | La ruta real es **`modelSettings.<modelId>.effortLevel`** (objeto por modelo, v2.1.251+), más un `effortLevel` suelto de primer nivel como respaldo. Desde v2.1.267 existe además **`maxEffortLevel`**, que es un tope. |
| Los hooks `PostToolUse` recortan la salida | **No pueden.** Docs de hooks: la salida de `PostToolUse` sólo admite `hookSpecificOutput` con `additionalContext`, `systemMessage` y `terminalSequence`. **No hay `updatedOutput`.** El hook se dispara *después* de que la herramienta devolvió: puede **añadir** contexto, nunca quitarlo. Quien recorta de verdad es **`PreToolUse` con `updatedInput`**. Ver §5.1: es el hallazgo que más afecta a COSMOS. |
| `/cost` como orden propia | **Es un alias de `/usage`** (igual que `/stats`). Misma salida. |

---

## 1. Dónde se gasta de verdad — las cifras medidas que existen

Antes de tocar nada conviene saber el reparto. Estas son las **únicas** mediciones públicas con
método que he encontrado; el resto del género «recorta el 90 % de tus tokens» cita a estas o no cita
a nadie.

**Arranque en frío de una sesión real** (XDA, 2026-08-28, método: ejecutar `/context` y leer la
rejilla — https://www.xda-developers.com/claude-code-using-fifty-thousand-tokens-before-typed-prompt-fixed-it/):

| Partida | Tokens | Tras podar |
|---|---:|---:|
| Prompt de sistema | 10.700 | 6.700 |
| **Herramientas integradas** | **28.500** | 28.500 |
| Skills | ~6.300 | 3.200 |
| Agentes propios | 943 | 74 |
| Mensajes | ~5.000 | — |
| **Total antes de escribir nada** | **51.400** | **~41.400** |

**La partida más grande no es la que todo el mundo persigue.** Las **herramientas integradas
(~28.500 tokens)** pesan más que el prompt de sistema y más que la mayoría de configuraciones MCP,
y el ecosistema entero de 2026 está mirando hacia otro lado. Existe un interruptor nativo poco
conocido que sí las toca: `CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT=1` (§2, A.3).

**Coste de las definiciones MCP** (zhang-liz/mcp-token-benchmark, 2026-07-08, método publicado:
`initialize` + `tools/list` por stdio, serializar cada definición y contar con `o200k_base` —
https://github.com/zhang-liz/mcp-token-benchmark — MIT, 0★, pero el método es correcto):
Notion 24 herramientas = **17.161 tokens**; Firecrawl 26 = **16.565**; GitHub 26 = **3.546**;
Slack 8 = **679**. Es decir, **de 85 a 715 tokens por herramienta según lo mal escrita que esté**,
un abanico de 25×. Mi cifra de trabajo en la Parte B (~300 tok/herramienta) sale de la medición
independiente de Toolport y cae dentro de ese rango.

**Aviso crítico sobre `/context`** (Cameron Cooke, 2026-01-22, tres métodos de conteo cruzados —
https://www.async-let.com/posts/claude-code-mcp-token-reporting/): para XcodeBuildMCP, el
tokenizador directo da **14.081 tokens** y el endpoint `count_tokens` **15.282**, pero **`/context`
reporta 45.018**. La diferencia (~30.937) es un **artefacto de doble conteo**: repite las
instrucciones de sistema compartidas por cada una de las 60 herramientas. **`/context` infla el
coste MCP unas 3×.** Todo el género de posts «tu MCP se come media ventana» de 2026 está construido
sobre esa cifra inflada.

**La ventana larga degrada la calidad, no sólo el bolsillo.** Es el argumento que convierte esto en
algo más que ahorro: *Classifier Context Rot* (Sam Martin y Fabien Roger, **Anthropic**, mayo 2026,
arXiv **2605.12366** — https://arxiv.org/abs/2605.12366): Opus 4.6, GPT-5.4 y Gemini 3.1 **pasan por
alto acciones peligrosas de 2× a 30× más a menudo** cuando ocurren tras 800K tokens de actividad
benigna; en MonitorBench, Opus 4.6 con razonamiento cae de **98,6 % a 88 % de recall**. Dos trabajos
más en ventana: arXiv **2606.29718** (29-06-2026, nombra el mecanismo: *terminación prematura*, y la
tasa correlaciona con la longitud del contexto) y arXiv **2607.17937** (20-07-2026, Codex: 8/10
aciertos con 10.991 caracteres frente a 3/10 con 299.140 — **pero n=10 y Fisher p=0,0698, o sea no
significativo**, y el autor lo dice).

**Lo que Anthropic publicó en la ventana junio-septiembre 2026:** un solo post,
https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models
(24-07-2026, Thariq Shihipar), que afirma haber *«removed over 80% of Claude Code's system prompt
for models like Claude Opus 5 and Claude Fable 5 with no measurable loss on our coding evaluations»*.
**Sin nombres de evals, sin puntuaciones, sin conteos antes/después: marketing hasta que publiquen
el método.** Las cifras duras de Anthropic sobre herramientas (tool search −85 %, *programmatic tool
calling* 43.588→27.297 = −37 %) son de **noviembre de 2025**, no de este verano:
https://www.anthropic.com/engineering/advanced-tool-use

---

## 2. Parte A — Funciones nativas de Claude Code (nada que instalar)

Todo lo de esta sección está confirmado hoy en la documentación oficial. Orden: primero lo que más
ahorra.

### A.1 — Topes de salida de herramientas ← **la palanca nativa más grande y la menos usada**

| Control | Grafía exacta | Defecto | Rango |
|---|---|---|---|
| Salida de Bash | `bashOutputMaxChars` (ajuste, **v2.1.261+**) | **30.000 caracteres** | 4.000–128.000 |
| Salida de Bash | `BASH_MAX_OUTPUT_LENGTH` (entorno) | 30.000 | máx. 150.000 |
| Respuestas MCP | `MAX_MCP_OUTPUT_TOKENS` (entorno) | **25.000 tokens** | aviso por encima de 10.000 |
| Tareas en segundo plano | `taskOutputMaxChars` (ajuste, v2.1.261+) | **32.000 caracteres** | 4.000–128.000 |
| Tareas en segundo plano | `TASK_MAX_OUTPUT_LENGTH` (entorno) | 32.000 | máx. 160.000 |
| Lecturas de fichero | `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS` (entorno) | **no documentado** | — |
| Caché de WebFetch | `CLAUDE_CODE_WEBFETCH_CACHE_TTL_MS` | 900.000 (15 min) | sólo dígitos |
| Búsquedas web | `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` | 200 | subible, **no desactivable** |

**Qué ahorra:** cuando la salida pasa del tope, Claude Code **la guarda en un fichero y al modelo
sólo le llega una vista previa más la ruta**. No se pierde nada; simplemente no se carga salvo que
haga falta. Con los defectos de fábrica, **una sola** orden ruidosa puede meter 30.000 caracteres
(~7.500 tokens) y **una sola** respuesta MCP puede meter 25.000 tokens.

**Qué cuesta:** si el modelo necesitaba de verdad la cola de esa salida, gasta un turno extra en
leer el fichero. En la práctica es el canje más barato del informe.

**Cómo se activa** (`~/.claude/settings.json`):
```json
{
  "bashOutputMaxChars": 12000,
  "taskOutputMaxChars": 12000,
  "env": { "MAX_MCP_OUTPUT_TOKENS": "12000" }
}
```
Ojo: `bashOutputMaxChars` **anula y hace ignorar** `BASH_MAX_OUTPUT_LENGTH`. No pongas los dos.

Fuentes: https://code.claude.com/docs/en/settings-reference#bashoutputmaxchars ·
https://code.claude.com/docs/en/env-vars

### A.2 — Carga diferida de herramientas MCP (*tool search*) — **ya encendida**

No hay clave en `settings.json`. El único control es la variable **`ENABLE_TOOL_SEARCH`**:

| Valor | Comportamiento |
|---|---|
| *sin definir* (**defecto**) | **Difiere todas las definiciones MCP.** Sólo entran nombres e instrucciones del servidor |
| `auto` | Carga por adelantado **si las definiciones caben en el 10 % de la ventana** |
| `auto:N` | Mismo umbral, en N % |
| `true` | Difiere siempre y manda la cabecera beta |
| `false` | Carga todo por adelantado |

**Qué ahorra:** la documentación cita *«50 tools can use 10–20K tokens»* y que *«tool selection
accuracy degrades above 30–50 tools loaded at once»*. Se cargan hasta **5 herramientas por
búsqueda**, con un catálogo tope de **10.000**.
**Beneficio extra para la caché:** con herramientas diferidas, que un servidor se conecte, se
desconecte o cambie su lista **sólo añade**, así que no invalida el prefijo cacheado. Con carga por
adelantado, cualquier cambio invalida la caché entera.

**Qué cuesta — y es un coste real, no teórico:** el modelo puede **no encontrar nunca** tus
herramientas. Está documentado empíricamente en el README de `Mibayy/token-savior` (ver B.9): en
**143 sesiones de benchmark, exactamente una** llamó a una herramienta del servidor, porque las 18
estaban tras un `ToolSearch` y el modelo tiró de `Grep` y `Read`. Por eso el fichero de contexto de
Serena para Claude Code grita *«use the tool search tool to load all of them right now»*.

**Cómo se activa:** no hagas nada. Lo que hay que hacer es **verificar que sigue puesta**
(`ENABLE_TOOL_SEARCH` sin definir) y saber que `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1`
**la apaga a la fuerza** sin que `ENABLE_TOOL_SEARCH` pueda revertirlo. Para eximir un servidor
concreto: `"alwaysLoad": true` en su configuración.
Requiere un modelo con bloques `tool_reference`: Sonnet 4.5, Haiku 4.5, Opus 4.5 **y posteriores**.

Fuente: https://code.claude.com/docs/en/mcp#scale-with-mcp-tool-search

### A.3 — `CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT=1` — **el interruptor que nadie menciona**

**Qué ahorra:** *«shorter system prompt + abbreviated tool descriptions»* en cualquier modelo,
conservando el conjunto completo de herramientas, los hooks, MCP y el descubrimiento de CLAUDE.md.
Es lo único nativo que toca la partida de **28.500 tokens de herramientas integradas** que la medición
de XDA identifica como la mayor del arranque en frío.

**Qué cuesta:** descripciones de herramienta abreviadas → el modelo tiene menos guía sobre cuándo y
cómo usar cada una. No hay medición pública del impacto en calidad. **Mídelo con `/context` antes y
después y con una tarea de referencia.**

**Cómo se activa:** `export CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT=1` (o en `env` de `settings.json`).
Se desactiva con `0`/`false`/`no`/`off`.

**No confundir con `CLAUDE_CODE_SIMPLE=1` / `--bare`**, que es mucho más agresivo: prompt mínimo y
**sólo Bash + leer fichero + editar fichero**, sin hooks, skills, órdenes, subagentes, plugins, MCP,
memoria automática ni CLAUDE.md, y exige `ANTHROPIC_API_KEY` (no vale el llavero ni OAuth). Para
COSMOS eso mata el arnés entero.

Fuente: https://code.claude.com/docs/en/env-vars

### A.4 — Esfuerzo de razonamiento (`effortLevel` / `maxEffortLevel` / `/effort`)

Esto es lo que el encargo llamaba «razonamiento extendido en turnos triviales».

```json
{
  "effortLevel": "medium",
  "maxEffortLevel": "high",
  "modelSettings": {
    "claude-opus-5": { "effortLevel": "medium", "maxEffortLevel": "high" }
  }
}
```

- Valores en ajustes: `low` | `medium` | `high` | `xhigh`. **`max` y `ultracode` son sólo de sesión**
  y no se aceptan en `effortLevel` ni en `CLAUDE_CODE_EFFORT_LEVEL`.
- `modelSettings` requiere **v2.1.251+**; `maxEffortLevel` requiere **v2.1.267+** y funciona como
  **tope** (gana el más bajo entre ámbitos); el usuario aún puede elegir por debajo.
- Las claves usan el **nombre canónico** (`claude-opus-5`); alias, IDs con fecha, `[1m]` e IDs de
  proveedor caen todos en la misma entrada.
- Por defecto **`high`** en todos los modelos con esfuerzo, **salvo Opus 4.7 que arranca en `xhigh`**.
- La documentación describe `medium` literalmente como *«reduces token usage for cost-sensitive
  work»*.
- **En sesión:** `/effort medium`, y `/effort` acepta `s` para aplicar sólo a la sesión.

**Qué cuesta:** menos profundidad de razonamiento. Y hay una trampa de caché: **en casi todos los
modelos cada nivel de esfuerzo tiene su propia caché de prompt, así que cambiar de nivel a mitad de
sesión recomputa la petición entera.** Decide al arrancar, no a mitad.

⚠️ **`ultracode` es un amplificador de coste**, no un ahorro: manda `xhigh` *y además* orquesta
flujos dinámicos.

Fuentes: https://code.claude.com/docs/en/settings-reference#effortlevel ·
https://code.claude.com/docs/en/model-config#adjust-effort-level

### A.5 — `MAX_THINKING_TOKENS` y compañía

| Variable | Comportamiento exacto |
|---|---|
| `MAX_THINKING_TOKENS` | Presupuesto fijo de razonamiento extendido. Tope: **un token por debajo del máximo de salida de la petición**, nunca por debajo de **1.024**. `0` desactiva el razonamiento en la API de Anthropic. **Se ignora (valores distintos de 0) en modelos de razonamiento adaptativo** salvo que pongas `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Máximo de tokens de salida. **Subirlo reduce el contexto efectivo disponible antes de que salte la autocompactación.** Defecto 32.000 para IDs de modelo no reconocidos |
| `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` | `1` desactiva el razonamiento adaptativo **sólo en Opus 4.6 y Sonnet 4.6** |
| `CLAUDE_CODE_DISABLE_THINKING` | `1` omite el parámetro `thinking`. **En modelos que razonan por defecto, el modelo puede seguir razonando.** No es un ahorro fiable |
| `alwaysThinkingEnabled` (ajuste) | `false` apaga el razonamiento extendido; `MAX_THINKING_TOKENS` lo sobreescribe por sesión en ambos sentidos |

Fuente: https://code.claude.com/docs/en/env-vars

### A.6 — Autocompactación

```json
{
  "autoCompactEnabled": true,
  "autoCompactWindow": 400000
}
```
- **`autoCompactWindow` es un número absoluto de TOKENS**, no un porcentaje. Rango **100.000–1.000.000**,
  **sin definir por defecto** (Claude Code elige una ventana por modelo). Se limita a la ventana del
  modelo.
- Precedencia: `CLAUDE_CODE_AUTO_COMPACT_WINDOW` (entorno) → `--autocompact` (CLI) → el ajuste.
  ⚠️ La variable de entorno **sólo acepta enteros planos**: `500k` se lee como `500` y se ajusta a
  100.000. La orden `/autocompact` sí acepta `500k`.
- `DISABLE_AUTO_COMPACT=1` la apaga por sesión (**sin prefijo `CLAUDE_CODE_`**).
- **Sonnet 5 compacta hacia los ~967K** por defecto (ventana de 1M completa, subida este verano).
- **`/compact` con instrucciones** funciona: `/compact Focus on code samples and API usage`. Y se
  puede fijar en CLAUDE.md:
  ```markdown
  # Compact instructions
  When you are using compact, please focus on test output and code changes
  ```
- **Qué cuesta:** la compactación es **con pérdida**. Además, tras compactar **no se reinyecta el
  listado de skills** (sólo las que invocaste) y se releen hasta los 5 ficheros modificados más
  recientemente.
- ⚠️ Si pones `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, el `used_percentage` de la barra de estado **deja de
  indicar cuándo saltará la compactación** (siempre mide contra la ventana completa del modelo).

Fuentes: https://code.claude.com/docs/en/settings-reference#autocompactwindow ·
https://code.claude.com/docs/en/costs#reduce-token-usage

### A.7 — `outputStyle: "Concise"` — tokens de salida, que cuestan 5×

```json
{ "outputStyle": "Concise" }
```
`Concise` (v2.1.237+) *«leads with the result, skips preamble and narration, keeps responses short by
default, while doing the engineering work as thoroughly as in the Default style»*. Los informes de
error, los avisos de seguridad y las confirmaciones de acciones destructivas **nunca** se recortan.

**Por qué importa más de lo que parece:** en Opus 5 la salida cuesta **$25/MTok frente a $5/MTok de
entrada** — 5×. Un token de salida ahorrado vale cinco de entrada.
⚠️ `Explanatory` y `Learning` **aumentan** los tokens de salida.
⚠️ **`/output-style` fue eliminada en v2.1.91.** Se cambia por `/config` → *Output style*.
⚠️ Cambiarlo a mitad de sesión **cuesta una reconstrucción de la caché de prompt**.

Fuente: https://code.claude.com/docs/en/output-styles

### A.8 — Memoria, CLAUDE.md y skills

| Control | Efecto | Defecto |
|---|---|---|
| `claudeMdExcludes` (`string[]` de globs) | Salta ficheros CLAUDE.md concretos | sin definir |
| `autoMemoryEnabled` | `false` = ni lee ni escribe memoria automática | `true` |
| `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` | **No carga ningún CLAUDE.md**: usuario, proyecto y memoria automática | sin definir |
| `includeGitInstructions` | `false` quita las instrucciones de git del prompt de sistema | `true` |
| `skillListingBudgetFraction` | Presupuesto del listado de skills. **Defecto `0.01` = 1 % de la ventana** | `0.01` |
| `skillListingMaxDescChars` | Caracteres por skill en el listado | `1536` |
| `disable-model-invocation: true` (frontmatter de la skill) | **Mantiene la skill completamente fuera del contexto** hasta que escribas `/nombre` | — |
| `disableBundledSkills` | Quita las skills incluidas del listado | `false` |

**Límites duros no configurables:** `MEMORY.md` carga **sólo las primeras 200 líneas o 25 KB, lo que
llegue antes** — lo que pase de ahí se descarta en silencio. Los `@path` de CLAUDE.md **no ahorran
contexto**: los ficheros importados se cargan al arrancar. **Lo que sí ahorra son las reglas con
ámbito de ruta** en `.claude/rules/` con un patrón `paths:`, que se cargan sólo cuando Claude toca
ficheros que casan.

Cuando el listado pasa del presupuesto, Claude Code **conserva todos los nombres pero descarta las
descripciones de las skills menos usadas** — la skill sigue invocable, pero el modelo la elegirá
menos por su cuenta. En la sesión medida por XDA, skills + plugins + memoria automática eran
**~11.000 de 51.400 tokens**, y la memoria automática sola ~4.000.

Fuentes: https://code.claude.com/docs/en/memory ·
https://code.claude.com/docs/en/settings-reference#skilllistingbudgetfraction

### A.9 — Caché de prompt (automática) y sus TTL

Claude Code la gestiona sola, en capas de menor a mayor rotación: prompt de sistema (instrucciones +
definiciones de herramienta) → contexto de proyecto (CLAUDE.md, memoria automática) → conversación.

```json
{ "promptCacheTtl": "1h", "subagentPromptCacheTtl": "5m" }
```
(v2.1.242+; sólo `5m` y `1h`. Equivalentes de entorno: `CLAUDE_CODE_PROMPT_CACHE_TTL`,
`CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL`. Desde v2.1.248 hay `experimental.cacheTtl` en el frontmatter
de un subagente.)

**Precio:** escritura 5m = 1,25× la entrada base; escritura 1h = **2×**; **lectura de caché = 0,1×**
(0,025× en Fable 5.1). O sea: 1h se amortiza tras **dos** lecturas, 5m tras una. **En ráfagas cortas
que nunca pasan de 5 minutos ociosos, `1h` es una pérdida.**

**Por defecto**, con suscripción Claude dentro de plan, la conversación principal ya está en **1 hora**;
al pasar a créditos de uso Claude Code **la baja a 5m** para abaratar. Fijar `promptCacheTtl: "1h"`
mantiene la hora ahí.

**Lo que invalida la caché** (y por tanto lo que hay que evitar a mitad de sesión): cambiar de modelo
(`/model`), cambiar el nivel de esfuerzo, y cualquier cambio en el conjunto de definiciones de
herramienta cargadas.
**`DISABLE_PROMPT_CACHING=1` casi siempre encarece.** No es un ahorro.

Fuentes: https://code.claude.com/docs/en/prompt-caching ·
https://platform.claude.com/docs/en/about-claude/pricing#prompt-caching

### A.10 — Subagentes: el mayor ahorro estructural

Cada subagente corre **en su propia ventana de contexto**: sus lecturas y llamadas a herramienta
**nunca entran en la tuya**, sólo vuelve el resumen final. Es exactamente lo que estoy haciendo en
esta investigación.

| Control | Efecto |
|---|---|
| `model: haiku` en el frontmatter | La documentación **lo recomienda explícitamente** para subtareas mecánicas. Haiku 4.5 = $1/$5 frente a Opus 5 $5/$25 |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Modelo por defecto de subagentes y compañeros |
| `tools:` en el frontmatter | Restringe el conjunto de herramientas → prompt de sistema más pequeño para ese agente |
| `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` | Defecto **20**. Ajustable, **no desactivable** |
| `CLAUDE_CODE_MAX_TURNS` / `--max-turns` | Tope duro de turnos agénticos |

⚠️ **No existe ningún ajuste que limite el tamaño de lo que devuelve un subagente.** Lo busqué en la
documentación y no está. La única palanca es la instrucción en el prompt del agente. Esto contradice
la esperanza del encargo («subagentes que devuelven parrafadas»): **se controla escribiendo mejor la
definición del agente, no configurando nada.**
⚠️ Un **fork** (`/fork`) hereda la conversación entera del padre: pierde el aislamiento de entrada y
sólo conserva el de salida.
⚠️ La ventana de un subagente la fija **su propio modelo**, no el del padre.

Fuente: https://code.claude.com/docs/en/sub-agents

### A.11 — Instrumentos de medida nativos

| Orden | Qué da |
|---|---|
| `/context` (y `/context all`) | Rejilla por categorías con sugerencias de optimización. **Recuerda: infla el coste MCP ~3×** (§1) |
| `/usage` (alias `/cost`, `/stats`) | Coste de sesión, límites de plan y **línea de caché de prompt por sesión**: ratio de acierto, fallos, tokens recacheados, frío/caliente. Y desde este verano, **diagnóstico de la causa probable de un fallo de caché** («tool definitions changed», «idle past the TTL») |
| `/doctor` | Cuánto contexto consume el listado de skills y qué skills dominan |
| **`/skill-doctor`** (v2.1.261, **2026-09-04**) | **Qué skills cargadas no se usan nunca y qué cuesta cada una por turno.** Es el instrumento más útil que ha salido este verano |
| `/btw <pregunta>` | **Pregunta lateral que no entra en el historial.** La forma más barata de preguntar algo puntual sin engordar el contexto para siempre |
| `/mcp` | Ver y desactivar servidores MCP que no usas |

### A.12 — Amplificadores de coste que conviene comprobar que están apagados

- **`fastMode: true` / `/fast`** — en Opus 5 y Opus 4.8 se factura a **$10 entrada / $50 salida por
  MTok**: el doble, en toda la ventana. Guárdalo con `CLAUDE_CODE_DISABLE_FAST_MODE=1`.
- **`ultracode`** — `xhigh` más orquestación de flujos.
- **Residencia de datos / `inference_geo: "us"`** — **1,1× sobre todo** (entrada, salida, escrituras
  y lecturas de caché) en Claude 4.6+.
- **Puntos de acceso regionales en Bedrock y Google Cloud** — **10 % de recargo**.
- **Búsqueda web** — **$10 por 1.000 búsquedas** además de los tokens, y los resultados cuentan como
  entrada **en ese turno y en todos los siguientes**.
- ⚠️ **Tokenizador nuevo:** *«Claude 4.7 and later models and Claude Mythos Preview use a newer
  tokenizer... approximately 30% more tokens for the same text.»* Opus 4.7/4.8/5 cuestan ~30 % más
  **por unidad de texto** de lo que sugiere el precio por token frente a los modelos de la era 4.6.

### A.13 — Novedades del verano 2026 (v2.1.158 → v2.1.268)

- **`maxEffortLevel`**, suelto y por modelo (v2.1.267)
- **`promptCacheTtl` / `subagentPromptCacheTtl`** como ajustes (v2.1.242); `experimental.cacheTtl` en
  frontmatter de agente (v2.1.248)
- **`bashOutputMaxChars` / `taskOutputMaxChars`** como ajustes (v2.1.261)
- **`/skill-doctor`** (v2.1.261, 2026-09-04)
- **Línea de caché de prompt en `/usage`** con diagnóstico de causa del fallo
- **Desglose de Loops en `/usage`** — llamadas, tokens totales y tokens por ejecución de cada bucle,
  para cazar un `/loop` desbocado
- La descripción de la herramienta de workflows bajó de **5,7K a ~1K tokens** (la referencia se movió
  a una skill)
- `/context` pasó a **estimación local** cuando la API de conteo no responde, en vez de gastar
  peticiones extra a un modelo pequeño
- Los fan-out de workflows **escalonan** agentes hermanos con el mismo prefijo para que los últimos
  lean la caché en vez de re-pagarla
- Muchos arreglos de fallos de caché de prompt (cambio de modelo reenviando todas las definiciones,
  refresco horario de token OAuth, sesiones con capturas de pantalla…) — **actualizar Claude Code es,
  por sí solo, un ahorro**

---

## 3. Parte B — Herramientas de GitHub, verificadas hoy

Convención de cada ficha: **URL literal · licencia · estrellas · último commit** (todo comprobado el
2026-09-11 contra `api.github.com`), mecanismo, ahorro reclamado y si está medido, coste de tenerla,
veredicto.

**Cómo estimo «lo que inyecta al arrancar».** La única medición pública y reproducible del coste de
una definición de herramienta MCP es la de Toolport (ver ficha): 415 herramientas = 164.880 tokens
por petición, 63 herramientas = 19.002, 183 = 51.533. Eso da **~280–400 tokens por herramienta MCP**.
Uso **300 tokens/herramienta** como cifra de trabajo y lo digo cada vez que la aplico. Para prompts y
frontmatter de skills cuento caracteres reales del fichero y divido entre 4.

---

### B.1 — Toolport · lazy MCP (la palanca externa mejor medida)

- **URL:** https://github.com/btsouth/toolport
- **Licencia:** MIT · **Estrellas:** 211 · **Último commit:** 2026-09-11 (`c761b898`) · Rust · creado 2026-06-19
- **Mecanismo:** pasarela MCP local. Se registra como **un solo servidor MCP** en el cliente y habla
  con los servidores reales por detrás. En modo `TOOLPORT_DISCOVERY=lazy` expone **4 meta-herramientas**
  (`toolport_status`, `toolport_search_tools`, `toolport_call_tool`, `toolport_fetch_result`) y el
  agente busca la herramienta cuando la necesita.
- **Ahorro reclamado y su fuente:** `BENCHMARK.md` del propio repo
  (https://github.com/btsouth/toolport/blob/main/BENCHMARK.md). **Medido, y de los mejores que he
  visto en este campo:**

  | Servidores | Herramientas | Plano | Lazy | Reducción | Aciertos (plano/lazy) |
  |---|---|---|---|---|---|
  | 3 | 63 | 179.181 tok | 47.095 tok | **74 %** | 15/15 · 15/15 |
  | 6 | 183 | 471.775 tok | 40.354 tok | **91 %** | 15/15 · 15/15 |

  Sobrecarga de definiciones **por petición**: plano 19.002 → 51.533 tokens; lazy **451 constantes**.
  Sobre un catálogo real de 14 servidores y **415 herramientas**: 164.880 tokens por petición sin
  Toolport frente a **886 con él (−99,5 %)**.
- **Por qué me lo creo:** dos modos, mismas tareas, mismo modelo (GPT-5.5), 5 repeticiones, y —esto es
  lo decisivo— **calificado por respuesta correcta, no por «completado»**: 30/30 correctas en ambos
  modos. No cambió exactitud por tokens. El script de medición (`benchmark/token-cost.mjs`) se puede
  apuntar al catálogo propio sin necesidad de modelo.
- **Coste de tenerla:** **886 tokens por petición** (medido por ellos, las 4 meta-herramientas). Es
  una app de escritorio Tauri + pasarela; añade un proceso local y un punto de fallo entre el cliente
  y todos los MCP. Las credenciales pasan al llavero del sistema (mejora, no coste).
- **Veredicto:** **catalogar como ficha** — el mecanismo es el correcto y la medición es seria, pero
  Claude Code ya trae carga diferida nativa (ver Parte A), así que para COSMOS el valor real es el
  `benchmark/token-cost.mjs` como instrumento de medida, no la pasarela.

---

### B.2 — ripwire · recuperación de contexto desde la CLI

- **URL:** https://github.com/redhat-et/ripwire
- **Licencia:** Apache-2.0 · **Estrellas:** 1.894 · **Último commit:** 2026-09-11 (`40a1895b`) · C++23 · creado 2026-07-29 · release v0.5.0 (2026-09-08)
- **Mecanismo:** **un binario, sin servidor**. Se usa como orden de shell (`ripwire . --for="…"`,
  `--callers=SYM`, `--impact=SYM`, `--from-trace`, `--situ`, `--pr-context`). El instalador además
  activa 17 *skills* de Claude Code que enseñan al agente *cuándo* llamarlo. El servidor MCP es la
  **segunda interfaz, opcional**, y el propio README desaconseja empezar por ahí.
- **Ahorro reclamado y su fuente:** tabla de 10 escenarios re-medida el **2026-08-08** sobre su propio
  repo, con la orden exacta que reproduce cada fila y los bytes en bruto en `docs/EVALS.md` §5.
  Extractos: «¿quién llama a esta función?» ~580 tok frente a ~40–52K de `grep` + abrir ficheros
  (**69×–89×**); «tengo un stack trace» ~1,4K frente a ~124–298K (**87×–209×**); «oriéntame en el
  repo» ~5,6K frente a ~20–25K (**3,6×–4,5×**).
- **Está medido, y con las derrotas publicadas.** Es lo que lo separa del resto: contra un servidor
  MCP de grafo de código, **ganó 27 · perdió 7 · empató 14** en 48 preguntas, gastando ~77K tokens
  frente a ~486K. Y publican el número que les va en contra: el titular «5,0 % de lo que gasta el
  pase ingenuo» viene con la frase *«on a 12-question set where it strictly satisfied 5 to the naive
  arm's 11»* — es decir, contexto más barato que **responde menos**, y lo dicen ellos. En LocBench
  encuentra todos los ficheros de oro en el top-10 en el 58,3 % de los casos (mejor alternativa:
  40,0 %).
- **Coste de tenerla — medido, no estimado:** el frontmatter (`name` + `description`) de las 17 skills
  suma **6.886 caracteres ≈ 1.721 tokens** que entran en cada sesión. Se puede instalar un subconjunto.
  Si además registras el servidor MCP, sumas sus esquemas; el README lo advierte él mismo: *«its verb
  schemas sit in your agent's context every session, whether or not it calls them»*.
- **Veredicto:** **instalar en la máquina** — es la única del lote cuyo camino principal (CLI) cuesta
  cero definiciones de herramienta, mide sus pérdidas y encaja con el criterio 1 de `spec/UNIVERSO.md`
  («se ejecuta»). Instalar sólo 4–6 skills, no las 17.

---

### B.3 — Headroom · compresión de salidas en un proxy local

- **URL:** https://github.com/headroomlabs-ai/headroom
- **Licencia:** Apache-2.0 · **Estrellas:** 71.549 · **Último commit:** 2026-09-10 (`04cdf79a`) · Python · creado 2026-01-07 · release v0.37.0 (2026-08-27)
- **Mecanismo:** **proxy HTTP local** que se interpone en `/v1/messages` (Anthropic) y
  `/v1/chat/completions` + `/v1/responses` (OpenAI). Se engancha con `headroom wrap claude`
  (arranca el proxy y lanza el agente apuntando a él) o `headroom proxy --port 8787`. También hay
  biblioteca (`from headroom import compress`) y servidor MCP. **Corre en local**: el README dice
  explícitamente *«runs locally — your data stays here»*, y los originales se cachean en disco para
  que el modelo pueda recuperarlos con `headroom_retrieve` (mecanismo CCR).
- **Ahorro reclamado y su fuente:** `benchmarks/index_proof_table.py --seed 20260902`, semilla fija y
  sin red, cuatro escenarios construidos con formatos reales de salida MCP:

  | Escenario | Antes | Después | Ahorro |
  |---|---:|---:|---:|
  | Búsqueda de código (100 resultados) | 17.199 | 13.597 | 21 % |
  | Depuración de incidente SRE | 55.957 | 24.340 | 57 % |
  | Exploración de base de código | 58.801 | 33.895 | 42 % |
  | Triaje de issues de GitHub | 46.067 | 32.429 | 30 % |

  **Medido**, con tokenizador del proveedor y semilla publicada. Y acompañado de una tabla de
  **exactitud** (`python -m headroom.evals suite --tier 1`): GSM8K 0,870 → 0,870 (±0,000);
  SQuAD v2 97 % con 19 % de compresión; BFCL (herramientas) 97 % con 32 % de compresión. Ellos mismos
  matizan que a N=100 un delta de ±0,03 cae dentro del intervalo de confianza.
- **La parte honesta:** el ahorro de tokens **de salida** (31,7 %) lo etiquetan como `[estimated]`
  con intervalo de confianza, porque es contrafactual, y ofrecen `HEADROOM_OUTPUT_HOLDOUT=0.1` para
  convertirlo en `measured`. Eso es exactamente el rigor que pide `spec/PUEBLO.md`.
- **Dos mecanismos que interesan a COSMOS directamente** (`HEADROOM_OUTPUT_SHAPER=1`, apagado por
  defecto): *verbosity steering* (añade una nota de concisión **al final** del prompt de sistema para
  no romper la caché) y **effort routing** (baja el esfuerzo de razonamiento cuando el turno es sólo
  el modelo reanudando tras un resultado de herramienta; preguntas nuevas y errores conservan esfuerzo
  completo). Usa `thinking.budget_tokens` / `output_config.effort` en Anthropic, sólo hacia abajo.
- **Coste de tenerla:** el proxy en sí **no inyecta contexto** (0 tokens). Pero `headroom wrap claude`
  **instala Serena a nivel de usuario en `~/.claude.json`** y la deja registrada en todos tus
  proyectos hasta que ejecutes `headroom unwrap` — es decir, te mete el coste de Serena sin pedirlo
  (~6.600 tokens/sesión, ver B.4). Se evita con `--code-memory none`. Añade además un proceso local
  en el camino crítico de cada petición.
- **Veredicto:** **catalogar como ficha** — la idea de *effort routing* es la mejor de todo el informe
  y COSMOS puede copiarla con un hook propio sin montar un proxy; meter un intermediario en el camino
  de autenticación del agente es un coste que sólo compensa si de verdad vas a usar la compresión.

---

### B.4 — Serena · recuperación semántica por símbolos (LSP)

- **URL:** https://github.com/oraios/serena
- **Licencia:** MIT · **Estrellas:** 29.186 · **Último commit:** 2026-09-08 (`701e7c84`) · Python · release v1.7.0 (2026-08-09)
- **Mecanismo:** servidor **MCP** que envuelve *language servers* (LSP) de más de 40 lenguajes y
  ofrece navegación a nivel de símbolo: `get_symbols_overview`, `find_symbol`,
  `find_referencing_symbols`, `replace_symbol_body`, `insert_after_symbol`… Trae un *contexto*
  específico para Claude Code
  (`src/serena/resources/config/contexts/claude-code.yml`) que excluye 6 herramientas redundantes
  (`read_file`, `execute_shell_command`, `find_file`, `list_dir`, `search_for_pattern`,
  `create_text_file`) y activa `single_project: true` para recortar el conjunto al mínimo.
- **Ahorro reclamado y su fuente:** **aquí está el problema.** El README de Serena **no da ni una
  sola cifra medida de ahorro de tokens**; lo que da son testimonios de modelos («Opus 4.6 (high) in
  Claude Code…») valorando la herramienta. El «60–80 %» que circula sale de blogs de terceros
  (p. ej. https://hanafifirman.dev/blog/serena-mcp-token-efficiency/), no del proyecto. **Marketing,
  no medición**, en lo que a ahorro de tokens respecta. Sí hay un benchmark independiente serio sobre
  *calidad* (ManoMano, 2026-02-02, proyecto Java de 36.407 líneas:
  https://medium.com/manomano-tech/project-aegis-benchmarking-ai-agents-and-why-serena-is-our-new-must-have-311673db35dd).
- **Coste de tenerla — estimado:** 49 herramientas documentadas
  (https://oraios.github.io/serena/01-about/035_tools.html), de las que el contexto `claude-code`
  deja ~20 activas → **~6.000 tokens** a 300 tok/herramienta, **más 611 tokens medidos** del prompt
  de contexto (2.445 caracteres del `claude-code.yml`). Total **≈ 6.600 tokens por sesión**, un 165 %
  del presupuesto de entrada entero de COSMOS.
- **Coste de calidad, y es real:** ese prompt de 611 tokens es coercitivo — `Read -> FORBIDDEN for
  discovery`, `Edit -> FORBIDDEN`, `**CRITICAL**`, y una lista de «razonamientos no permitidos» que
  prohíbe al modelo justificar el uso de sus propias herramientas. Está peleado con las herramientas
  nativas de Claude Code por diseño.
- **Veredicto:** **catalogar como ficha** — el mecanismo (símbolos en vez de ficheros enteros) es
  correcto y el proyecto es sólido, pero cobra ~6.600 tokens de entrada por sesión para ahorrar en
  lecturas, y **no publica la medición que justificaría ese canje**. ripwire hace lo mismo por ~1.700
  tokens y sí publica.

---

### B.5 — code-review-graph (CRG) · grafo persistente del repo

- **URL:** https://github.com/tirth8205/code-review-graph
- **Licencia:** MIT · **Estrellas:** 31.334 · **Último commit:** 2026-08-26 (`b5866875`) · Python · release v2.3.8 (2026-08-21)
- **Mecanismo:** indexa el repo en un grafo (tree-sitter + comunidades Leiden + *embeddings* locales
  `all-MiniLM-L6-v2`), y lo expone como **CLI** y como **servidor MCP** (`code-review-graph serve`).
  Actualización incremental por hooks: en un repo de ~3.000 ficheros, editar dos ficheros re-indexa en
  ~2,5 s.
- **Ahorro reclamado y su fuente:** `README` §Benchmarks, recaptura del **2026-08-02**, 6 repos reales
  con SHA fijado, semilla fija, *embeddings* deterministas en CPU; receta completa en
  `docs/REPRODUCING.md`. Mediana **~65×** de reducción por pregunta (rango 36× fastapi → 376×).
- **Pero el titular está inflado y ellos lo dicen:** el denominador es *whole-corpus baseline*, y el
  propio README admite que es *«an upper bound no real agent pays: a competent agent greps for
  identifiers and reads only the best-matching files»*. El número honesto (`agent_baseline`, grep +
  top-3 ficheros) existe en los CSV pero **no se publica como titular**. Además el benchmark formal
  `token_efficiency.py` **da ratios por debajo de 1** en commits pequeños. Y la precisión de impacto
  («recall 1.0») la marcan ellos como **circular**: la verdad de referencia sale de las mismas aristas
  que recorre el predictor.
- **Coste de tenerla:** **30 herramientas MCP por defecto** → **~9.000 tokens/sesión** a 300 tok/u.
  Recortable con `--tools` o `CRG_TOOLS=…`. Más un índice en disco y un proceso de indexación.
- **Veredicto:** **catalogar como ficha** — medición reproducible y admisiones honestas, pero 30
  herramientas MCP son 2,25 veces el presupuesto de entrada de COSMOS para un ahorro cuyo titular el
  propio proyecto desautoriza. Si se usa, con `CRG_TOOLS` recortado a 3.

---

### B.6 — ccusage · medición del gasto desde los JSONL

- **URL:** https://github.com/ccusage/ccusage — **ojo: `ryoppippi/ccusage` ya no existe como tal**,
  devuelve `301 Moved Permanently` hacia la organización `ccusage`. Actualiza cualquier ficha vieja.
- **Licencia:** NOASSERTION (fichero propio, no SPDX estándar) · **Estrellas:** 18.496 ·
  **Último commit:** 2026-09-11 (`401a9a7d`) · Rust
- **Mecanismo:** **CLI pura**, `npx ccusage@latest`. Lee los JSONL locales que ya escribe el agente y
  saca informes diarios/semanales/mensuales/por sesión. Tiene `--offline` con precios cacheados y un
  modo `ccusage statusline` (beta) para la barra de estado.
- **Ahorro reclamado:** **ninguno, y está bien así.** No ahorra tokens: los mide. Es el instrumento,
  no la palanca.
- **Coste de tenerla:** **0 tokens de contexto.** Se ejecuta en la terminal; su salida sólo entra al
  contexto si tú se la pegas. En modo statusline tampoco entra: la barra de estado se pinta en el
  terminal, no en el prompt del modelo.
- **Veredicto:** **instalar en la máquina** — coste cero y es la única forma de saber si algo de lo
  demás funciona. Sin ella el resto del informe es opinión.

---

### B.7 — ccstatusline · medidor de contexto en la barra de estado

- **URL:** https://github.com/sirmalloc/ccstatusline
- **Licencia:** MIT · **Estrellas:** 12.839 · **Último commit:** 2026-09-03 (`016be1fc`) · TypeScript
- **Mecanismo:** se registra como `statusLine` en `settings.json`. Lee el transcript JSONL en
  streaming (no carga el fichero entero) y pinta widgets: longitud de contexto, porcentaje, tokens,
  velocidad, coste, **effort**, y compactación. Tiene corrección explícita post-compactación: los
  widgets se reinician desde `compact_boundary.postTokens` tras un `/compact`.
- **Ahorro reclamado:** ninguno directo. Su valor es que **ves** el gasto mientras ocurre.
- **Coste de tenerla:** **0 tokens de contexto** (misma razón que ccusage). Sí cuesta un proceso por
  render de la barra.
- **Veredicto:** **instalar en la máquina** — coste cero, y el widget de contexto + effort es
  justamente lo que COSMOS necesita para saber cuándo un turno merece razonamiento extendido.
  Alternativas verificadas hoy con el mismo papel: `aiedwardyi/claude-usage-monitor` (54★),
  `hyperi-io/claudemeter` (18★), `lakpriya1s/ccbar` (9★). ccstatusline es la más mantenida con
  diferencia.

---

### B.8 — claude-mem · memoria persistente comprimida

- **URL:** https://github.com/thedotmack/claude-mem
- **Licencia:** Apache-2.0 · **Estrellas:** 93.679 · **Último commit:** 2026-09-11 (`7bfc4016`) ·
  TypeScript · release v13.24.21 (2026-09-11)
- **Mecanismo:** **5 hooks de ciclo de vida** (`SessionStart`, `UserPromptSubmit`, `PostToolUse`,
  `Stop`, `SessionEnd`) + servicio worker local (Bun) + SQLite + Chroma, y **4 herramientas MCP**
  con flujo en 3 capas: `search` (índice compacto, ~50–100 tok/resultado) → `timeline` →
  `get_observations` (detalle completo, ~500–1.000 tok/resultado).
- **Ahorro reclamado y su fuente:** «**~10x token savings** by filtering before fetching details»,
  README, sin benchmark, sin metodología, sin corpus. **Marketing.** Además el ahorro que describe es
  *interno a su propia búsqueda* (filtrar antes de traer detalle), no frente a no tenerlo instalado.
- **Coste de tenerla — y va en la dirección contraria:** el hook `SessionStart` **inyecta** memoria en
  cada sesión nueva. Eso **suma** tokens de entrada; el canje es no volver a derivar el contexto. Las
  4 herramientas MCP son **~1.200 tokens**, y la inyección de memoria es variable y no está acotada
  en el README.
- **Dos banderas rojas que COSMOS debe pesar:**
  1. El **valor por defecto es «CMEM Pro, la memoria alojada»**; el observador local es *opt-in*
     (`--provider host`). Es decir, por defecto la traza de tus sesiones sale de tu máquina.
  2. El proyecto tiene un **token de criptomoneda asociado** (CMEM, en BASE, CA publicado en el
     propio README, «oficialmente abrazado por el creador»). Un proyecto cuyo crecimiento está atado
     a un memecoin no es una dependencia que yo pondría en el camino de arranque de cada sesión.
- **Veredicto:** **descartar** — inyecta en vez de recortar, su «10×» no está medido, envía datos
  fuera por defecto y lleva un memecoin pegado.

---

### B.9 — token-savior · el hallazgo más útil del informe no es la herramienta

- **URL:** https://github.com/Mibayy/token-savior
- **Licencia:** MIT · **Estrellas:** 1.148 · **Último commit:** 2026-08-10 (`73e9c7f5`) · Python
- **Mecanismo:** servidor MCP (18 herramientas) de navegación estructural + memoria, más compactadores
  `PostToolUse` (34) y un reescritor `PreToolUse` (10 reglas), ambos *opt-in*
  (`TS_BASH_COMPACT=1`, `TS_BASH_REWRITE=1`).
- **Ahorro reclamado:** 97,9 % (188/192) en «tsbench» con **−80 % de tokens activos** y −83 % de
  tiempo, frente a 78,3 % en Claude Code pelado. El propio README avisa: *«its repository is not
  public at the moment, so take the figures as reported rather than as independently verifiable»*.
  **No verificable.**
- **Y aquí está lo valioso — una retractación publicada el 2026-08-10** que vale más que la
  herramienta. Citando el README: una re-medición publicada el 2026-08-09 fue **retirada** porque
  *«those numbers did not measure this server at all: across 143 benchmark sessions, **exactly one**
  called a Token Savior tool. The client running the harness had MCP deferred-tool loading enabled,
  so all 18 tools sat behind a `ToolSearch` lookup instead of appearing in the model's manifest. The
  model never saw them and fell back to `Grep` and `Read` — 66 greps, 30 reads, one MCP call.»*

  **Dos lecciones directas para COSMOS:**
  - Con la carga diferida nativa activa, **un servidor MCP instalado puede no usarse nunca**. Pagas
    el descubrimiento y no obtienes el beneficio. (Es exactamente por esto que el `claude-code.yml`
    de Serena grita *«use the tool search tool to load all of them right now»*.)
  - *«A benchmark of an MCP server must assert that its tools were actually called.»* Debería ser
    criterio de aceptación de cualquier ficha de pueblo que reclame ahorro vía MCP.
- **Veredicto:** **descartar la herramienta, catalogar la lección.** 18 herramientas MCP (~5.400
  tokens) por cifras que su propio autor marca como no verificables.

---

### B.10 — Aider (repomap) · el origen de la idea, no una herramienta para Claude Code

- **URL:** https://github.com/Aider-AI/aider
- **Licencia:** Apache-2.0 · **Estrellas:** 48.901 · **Último commit:** **2026-05-22** (`5dc9490b`) ·
  Python · 1.860 issues abiertas
- **Mecanismo:** el *repo map* de aider (tree-sitter + PageRank sobre el grafo de referencias,
  recortado a un presupuesto de tokens) vive **dentro de aider**, su propio agente de terminal. **No
  hay integración con Claude Code.**
- **Estado:** sin commits desde el 2026-05-22 — casi **cuatro meses parado**, con 1.860 issues
  abiertas. El proyecto está, como mínimo, en pausa.
- **Veredicto:** **descartar como herramienta** (no se engancha a Claude Code y está parado);
  **el algoritmo sigue vigente** y hay portes vivos si alguna vez hace falta:
  `dereira/goldfish` (Go, PageRank + tree-sitter, presupuesto de tokens, 2★) y
  `dotcommander/repomap` (Go, 1★). Ambos demasiado verdes para instalar.

---

### B.11 — Descartes rápidos (verificados hoy, no merecen ficha)

Los hooks de recorte de salida que pedías buscar existen, pero **todos son diminutos y están
parados**, y COSMOS ya tiene su propio guardarraíl que hace lo mismo:

| Repo | ★ | Último commit | Por qué se descarta |
|---|---|---|---|
| https://github.com/signal1project/rtk | 0 | 2026-05-21 | «PostToolUse hook que comprime salida» — 0 estrellas, un solo día de vida |
| https://github.com/ThomasTartrau/mcp-rtk | 4 | 2026-04-23 | proxy MCP, «60-90 %» sin medición, parado 5 meses |
| https://github.com/dockplusai-ops/token-guard | 6 | 2026-05-10 | hooks de bloqueo de ficheros pesados, sin licencia |
| https://github.com/mr7495/token_saver_nova | 2 | 2026-08-23 | dos días de vida |
| https://github.com/msiShariful/claude-token-inspector | 4 | 2026-05-14 | lo cubre `/context` nativo |
| https://github.com/chris-schra/mcp-funnel | 156 | **2025-11-24** | buena idea (filtrar MCP), parado 10 meses |
| https://github.com/voicetreelab/lazy-mcp | 112 | 2026-01-09 | parado 8 meses; lo hace Toolport mejor y medido |
| https://github.com/mcpslim/serena-slim | 4 | 2026-01-20 | un único commit, en enero |

**Mención aparte, por afinidad filosófica con COSMOS:** https://github.com/AraneaDev/ariadne
(MIT, **1★**, 2026-09-08) mide *«what your installed MCP servers cost you after install: the tokens
their tool definitions spend on every turn, the ones you never call»*. Es exactamente el medidor que
pide `spec/MEDIDOR.md` aplicado a MCP — pero con 1 estrella y en pre-release, **no instalar**;
anotar la idea.

**Otros motores de contexto verificados hoy** que hacen lo mismo que B.2/B.5 sin aportar nada nuevo:
https://github.com/elara-labs/code-context-engine (413★, MIT, 2026-08-23, «94 %» con baseline de
corpus entero — mismo sesgo que CRG), https://github.com/probelabs/probe (702★, Apache-2.0,
2026-09-08, ripgrep + tree-sitter, sin cifras de ahorro publicadas),
https://github.com/kunal12203/GrapeRoot (1.035★, Apache-2.0, 2026-09-03).
---

### B.12 — ponytail · reducir lo que el agente **escribe**, no lo que lee

- **URL:** https://github.com/DietrichGebert/ponytail
- **Licencia:** MIT · **Estrellas:** 135.612 (7.269 forks) · **Último commit:** 2026-09-07 (`356918eb`) ·
  JavaScript · creado **2026-06-12**
- **Es el fenómeno del verano** y no es un compresor: es un plugin de skills que obliga al agente a
  elegir la solución más perezosa que funcione (YAGNI, biblioteca estándar antes que código propio,
  una línea antes que cincuenta). Ahorra tokens **de salida** porque el agente escribe menos código,
  y ahorra tokens **futuros** porque hay menos código que releer después.
- **Mecanismo:** skills de Claude Code. `/plugin marketplace add DietrichGebert/ponytail`.
- **Ahorro reclamado y su fuente — medido, y con una señal de honestidad poco común:** benchmark
  agéntico sobre un repo FastAPI+React, 12 tareas, n=4, Haiku 4.5: **−54 % de líneas de código,
  −22 % de tokens, −20 % de coste, −27 % de tiempo, seguridad igualada al 100 %**. Y los autores
  **descartan explícitamente su propia cifra más vistosa** («80-94 % menos código» en tiro único)
  calificándola de artefacto del baseline. Eso vale más que el número.
- **Coste de tenerla — medido:** `skills/ponytail/SKILL.md` son **6.637 caracteres**; la descripción
  del frontmatter (~800 car. ≈ **200 tokens**) entra en el listado de skills de cada sesión, y el
  cuerpo (~5.800 car. ≈ **1.450 tokens**) entra cuando se invoca. Hay 6 skills más en el paquete.
- **Coste de calidad:** empuja sistemáticamente hacia menos abstracción. En un arnés como COSMOS,
  donde las especificaciones son normativas, «lo más perezoso que funcione» puede chocar con
  «lo que dice `spec/`».
- **Veredicto:** **catalogar como ficha** — el ángulo (menos salida, que cuesta 5× la entrada) es el
  correcto y está medido, pero es un sesgo de diseño global, y esa decisión no se toma en un informe
  de tokens.

---

### B.13 — caveman · compresión de estilo de salida

- **URL:** https://github.com/JuliusBrussee/caveman
- **Licencia:** **NOASSERTION** (no es SPDX estándar — revisar antes de usar) · **Estrellas:** 104.963 ·
  **Último commit:** 2026-09-07 (`15581d14`) · Go · creado 2026-04-04 (**fuera de la ventana
  junio-septiembre**, pero sigue activo)
- **Mecanismo:** skill de Claude Code que hace responder al modelo en telegrama («why use many token
  when few token do trick»). Niveles `lite|full|ultra` más variantes *wenyan*. Persiste toda la sesión.
- **Ahorro reclamado y su fuente — medido:** salida **−65 %** sobre 10 llamadas reales (rango 22-87 %);
  entrada del proxy **−33,2 %** sobre un benchmark fijado de 54 ejecuciones (3 por caso); modo
  navegación 121 frente a 15.704 tokens (129,8×).
- **Y el mantenedor publica el contra-argumento**, que es lo que lo hace citable: *«Whole-session
  savings land lower than the table»*, y la skill **añade ~1-1,5K tokens de entrada por turno** con
  sus propias reglas — **en sesiones ya concisas puede salir perdiendo**.
- **Coste de tenerla — medido por mí:** `skills/caveman/SKILL.md` = **7.022 caracteres**; una vez
  activada, el cuerpo (~6.750 car. ≈ **1.690 tokens**) se queda en contexto toda la sesión, lo que
  cuadra con la advertencia del propio autor.
- **Coste de calidad:** el agente te habla como un cavernícola. Es un coste de legibilidad real, no
  una broma, y en un arnés cuyas salidas se leen y se archivan, importa.
- **Veredicto:** **descartar para COSMOS** — el mecanismo útil (respuestas breves) ya lo da
  `outputStyle: "Concise"` de forma nativa, sin instalar nada, sin 1.690 tokens por sesión y sin
  hablar como un cavernícola. Licencia no estándar, además.

---

### B.14 — Paritok · pasarela de compresión no destructiva

- **URL:** https://github.com/Paritok-official/paritok-4b-v1
- **Licencia:** Apache-2.0 · **Estrellas:** 1.451 (138 forks) · **Último commit:** 2026-09-10
  (`f95ac0f0`) · Python · creado 2026-07-15
- **Mecanismo:** pasarela de compresión con un modelo de 4B que comprime las lecturas, más filtrado
  de esquemas de herramienta (**~29K → 8K por turno**).
- **Ahorro reclamado y su fuente — el mejor método de evaluación de todo el lote externo:**
  sobre **SWE-bench Lite**, retiene el **86,5 % de la calidad de resolución con contexto completo a
  un 25,7 % de compresión** (89,3 % con fuente numerada por líneas), y una auditoría de
  **extractividad del 96,2 %** sobre datos reservados. Ahorro extremo a extremo: ~25 % en el turno 1,
  ~39 % en el turno 5, «pasado el 85 %» en sesiones saturadas. Reproducible con una orden; autoinformado,
  sin evaluación de terceros.
- **Por qué me interesa el método y no sólo la cifra:** medir contra SWE-bench Lite y publicar
  «retenemos el 86,5 % de la calidad» es exactamente lo contrario del género de «−90 % sin pérdida de
  calidad». Admite la pérdida y la cuantifica.
- **Coste de tenerla:** una pasarela más un modelo de 4B corriendo en local. No inyecta contexto,
  pero añade proceso, memoria y latencia.
- **Veredicto:** **catalogar como ficha** — la medición es la más seria del lote de compresores; el
  coste operativo (modelo local en el camino crítico) es demasiado para lo que COSMOS necesita hoy.

---

### B.15 — mcptoon y mcp-token-benchmark · instrumentos, no palancas

- **https://github.com/activeing123/mcptoon** — Apache-2.0 · **195★** · último commit **2026-09-11** ·
  creado 2026-07-27. Reclama **71.929 → 581 tokens (−99,2 %)** en descubrimiento de herramientas con
  255 herramientas, con `tiktoken`/`cl100k_base`, **el JSON del benchmark commiteado**
  (`assets/benchmark_tiktoken.json`) y una calculadora para reproducirlo. Declara explícitamente que
  ambas filas son configuraciones medidas, «not one number scaled up and down». **Medido y creíble**,
  pero es el mismo mecanismo que la carga diferida nativa (A.2), que COSMOS ya tiene gratis.
- **https://github.com/zhang-liz/mcp-token-benchmark** — MIT · **0★** · commit único 2026-07-08.
  Cero tracción, pero es **el único medidor publicado con método explícito** del coste de las
  definiciones MCP (§1). **Catalogar la metodología, no el repo.**

**Veredicto para ambos:** **catalogar como ficha** en la rama de medición. Lo que COSMOS necesita de
aquí es la técnica de conteo, no un binario más.

---

### B.16 — token-diet · buen método, proyecto frío

- **URL:** https://github.com/Kulaxyz/token-diet
- **Licencia:** **ninguna** (sin fichero de licencia — jurídicamente inutilizable) · **Estrellas:** 470 ·
  **Último commit:** **2026-07-04** (un día después de crearse; **más de dos meses parado**) ·
  0 watchers
- **Ahorro reclamado — medido:** **≈31 % menos de factura de media** sobre ejecuciones reales con
  Sonnet 5, rango −17 % a −54 % según el tipo de sesión; salida −30 % a −81 %. Reproducible con
  `ANTHROPIC_API_KEY=… node bench/bench.mjs`, resultados en `bench/RESULTS.md`.
- **Veredicto:** **descartar** — sin licencia y sin mantenimiento desde el día siguiente a su
  creación, por muy buena que sea la medición. 470 estrellas y 0 watchers es el perfil de algo que se
  compartió mucho y no lo usa nadie.
---

## 4. Las 5 palancas de más impacto

### Supuestos de la «sesión típica»

Para que las cifras signifiquen algo, esta es la sesión que estoy modelando. Cambia los supuestos y
cambian los números; están puestos para que se puedan discutir.

- Modelo **Opus 5 [1m]**: **$5/MTok entrada, $25/MTok salida, $0,50/MTok lectura de caché,
  $6,25/MTok escritura de caché a 5 min** (precios verificados hoy, sin recargo por contexto largo).
- **40 turnos**, **~25 llamadas a herramienta**, arranque en frío **~35.000 tokens** (por debajo de
  los 51.400 medidos por XDA, asumiendo que COSMOS va más ligero), contexto final ~180.000.
- **El principio que ordena la lista:** un token que entra en el turno *k* se vuelve a enviar en
  todos los turnos de *k* a 40. Por eso doy **dos** cifras en cada palanca: **tokens de ventana**
  (espacio liberado, que es lo que afecta a la calidad y a cada cuánto compactas) y **tokens
  facturados** (ventana × turnos que persiste × multiplicador de caché). Un token en el prompt de
  sistema se paga 40 veces; uno que entra a mitad, unas 20.
- Los tokens de **salida** cuestan **5×** los de entrada, así que los convierto a
  «tokens-de-entrada-equivalentes» para poder compararlos en la misma columna.

### Ranking

| # | Palanca | Tipo | Tokens de ventana | Tokens facturados (equiv.) | Coste estimado evitado |
|---|---|---|---:|---:|---:|
| 1 | Tope de esfuerzo + `outputStyle: "Concise"` | **(a) nativo** | — (salida) | **~325.000** | **~$1,63** |
| 2 | No romper la carga diferida de MCP + podar lo que quede | **(a) nativo** | ~25.000 | ~1.000.000 | ~$0,66 |
| 3 | Bajar los topes de salida de herramientas | **(a) nativo** | ~36.000 | ~765.000 | ~$0,64 |
| 4 | ripwire en lugar de leer ficheros enteros | **(b) externo** | ~34.000 netos | ~680.000 | ~$0,55 |
| 5 | `CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT=1` | **(a) nativo** | ~12.000 | ~480.000 | ~$0,32 |

Cuatro de las cinco son **ajustes nativos que no requieren instalar nada**. Esa es la conclusión
principal del informe.

---

#### 1 — (a) Tope de esfuerzo + `outputStyle: "Concise"` · ~325.000 tokens-equivalentes

**Supuesto:** 40 turnos. Con esfuerzo `xhigh` estimo ~2.000 tokens de razonamiento por turno frente a
~600 en `medium`: 1.400 × 40 = **56.000 tokens de salida**. `Concise` recorta además ~30 % de los
~900 tokens de prosa por turno: **~11.000** más. Total **~67.000 tokens de salida**, que a $25/MTok
equivalen a **~325.000 tokens de entrada**.

**Por qué es la primera:** es la única palanca que ataca el lado caro de la factura. Y el encargo la
nombraba bien: *«razonamiento extendido en turnos triviales»*. Un turno en el que el modelo sólo
reanuda tras un resultado de herramienta no necesita `xhigh`.

**Cómo:**
```json
{
  "outputStyle": "Concise",
  "maxEffortLevel": "high",
  "modelSettings": { "claude-opus-5": { "effortLevel": "medium", "maxEffortLevel": "high" } }
}
```
**Lo que cuesta:** menos profundidad de razonamiento en los turnos que sí la necesitaban. Mitigación:
`maxEffortLevel` es un **tope**, no un valor fijo — puedes subir a mano con `/effort` cuando toque.
⚠️ Pero **cambiar de nivel a mitad de sesión invalida la caché de prompt** y recomputa la petición
entera, así que decide al arrancar.

**Lo más fino sería copiar el *effort routing* de Headroom** (B.3): bajar el esfuerzo automáticamente
sólo cuando el turno es «el modelo reanudando tras un resultado de herramienta», y dejarlo completo en
preguntas nuevas y errores. Eso COSMOS lo puede hacer con un hook propio sin montar el proxy.

---

#### 2 — (a) No romper la carga diferida de MCP, y podar lo que quede · ~25.000 tokens de ventana

**Supuesto:** 5-6 servidores MCP con ~20 herramientas cada uno. A las tarifas medidas por
zhang-liz (85-715 tokens por herramienta según el servidor) y con el descuento de 3× por el
sobre-conteo de `/context`, estimo **~25.000 tokens reales** que la carga diferida ya te está
ahorrando. Viven en el turno 0, así que se pagan **las 40 veces**: ~1.000.000 de tokens facturados.

**Es la palanca más grande que ya tienes.** El trabajo no es activarla, es:
1. **Verificar** que `ENABLE_TOOL_SEARCH` sigue sin definir y que nadie ha puesto
   `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` (que la apaga a la fuerza y no se puede revertir desde
   `ENABLE_TOOL_SEARCH`).
2. **Desinstalar los servidores MCP que no se usan** (`/mcp`). Diferido no es gratis: sigues pagando
   nombres e instrucciones de servidor.
3. **No poner `"alwaysLoad": true`** salvo que sepas exactamente por qué.

**Lo que cuesta — y es real:** el modelo puede **no encontrar nunca** una herramienta que sí
necesitaba (B.9: 143 sesiones, 1 llamada MCP). Si instalas un MCP y quieres que se use, tienes que
decirlo en el prompt.

---

#### 3 — (a) Bajar los topes de salida de herramientas · ~36.000 tokens de ventana

**Supuesto:** de 25 llamadas a herramienta, 5 desbordan un tope de 12.000 — tres salidas de Bash de
~25.000 caracteres (ahorro 3.250 tokens cada una) y dos respuestas MCP de 25.000 tokens (ahorro
13.000 cada una). Total **~35.750 tokens de ventana**. Entran a media sesión, así que persisten ~20
turnos: **~765.000 tokens facturados**.

**Por qué funciona tan limpiamente:** cuando la salida pasa del tope, Claude Code **la escribe en un
fichero y al modelo le llega una vista previa más la ruta**. No se pierde información; deja de
cargarse por defecto.

```json
{
  "bashOutputMaxChars": 12000,
  "taskOutputMaxChars": 12000,
  "env": { "MAX_MCP_OUTPUT_TOKENS": "12000" }
}
```
**Lo que cuesta:** un turno extra de lectura cuando el modelo sí necesitaba la cola. Barato.
⚠️ `bashOutputMaxChars` **anula** `BASH_MAX_OUTPUT_LENGTH`; no pongas los dos.

---

#### 4 — (b) ripwire en lugar de leer ficheros enteros · ~34.000 tokens netos

**Supuesto:** 8 lecturas exploratorias de ~6.000 tokens cada una (48.000) sustituidas por consultas
de ripwire de ~1.500 (12.000). Ahorro bruto 36.000, **menos los 1.721 tokens medidos** del frontmatter
de sus 17 skills → **~34.000 netos**. Persisten ~20 turnos: ~680.000 facturados.

Es la única herramienta externa que entra en el ranking, y entra por tres razones:
- **La documentación oficial dice que este es el problema:** *«File reads dominate context usage»*
  (https://code.claude.com/docs/en/costs#reduce-token-usage).
- **Su camino principal es la CLI**, no MCP: cero definiciones de herramienta. El propio README
  advierte de que registrar el servidor MCP mete los esquemas en contexto «whether or not it calls
  them».
- **Publica sus derrotas**: el titular «5,0 % de lo que gasta el pase ingenuo» viene acompañado de
  «satisfizo 5 preguntas frente a 11 del pase ingenuo». Contexto más barato que responde menos no es
  un ahorro — y lo dicen ellos.

**Lo que cuesta:** 1.721 tokens por sesión si instalas las 17 skills (instala 4-6). Y el riesgo real
de todo esto: que el agente use la herramienta para preguntas que `grep` ya respondía.

```bash
RIPWIRE_REPO=redhat-et/ripwire bash -c "$(curl -fsSL https://raw.githubusercontent.com/redhat-et/ripwire/main/scripts/install.sh)"
ripwire . --for="lo que vas a cambiar, en palabras"
```

---

#### 5 — (a) `CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT=1` · ~12.000 tokens de ventana · **la menos segura**

**Supuesto:** las herramientas integradas miden **~28.500 tokens** y el prompt de sistema **~10.700**
(XDA, 2026-08-28). El interruptor promete *«shorter system prompt + abbreviated tool descriptions»*.
Estimo una reducción del 25-40 % sobre esos ~39.200 → **~12.000 tokens**. Como viven en el turno 0,
se pagan 40 veces: ~480.000 facturados.

**La pongo la quinta a propósito: es la única de las cinco cuyo ahorro NO está medido por nadie.**
La documentación no da cifras y no he encontrado ninguna medición pública. Pero es también la única
palanca que toca la partida más grande del arranque en frío, que el ecosistema entero ignora.

**Lo que cuesta:** descripciones de herramienta abreviadas → menos guía sobre cuándo usar cada una.
Sin medición de impacto en calidad.

**Cómo:** `export CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT=1`, y **medir con `/context` antes y después**
más una tarea de referencia. Si el ahorro real es menor de ~8.000 tokens o la calidad baja, revertir.
No confundir con `CLAUDE_CODE_SIMPLE=1` / `--bare`, que desactiva hooks, skills, MCP y CLAUDE.md —
eso mata COSMOS entero.

---

### Menciones honoríficas que no entraron

- **(a) `/btw`** — preguntas laterales que **no entran en el historial**. Ahorro pequeño por uso pero
  con amplificación total: un `/btw` de 2.000 tokens en el turno 5 evita 35 relecturas.
- **(a) `/skill-doctor`** (v2.1.261, 2026-09-04) — no ahorra, pero es el único instrumento nativo que
  atribuye coste por turno a una skill concreta. Es el punto de partida.
- **(a) `disable-model-invocation: true`** en el frontmatter de una skill — la mantiene
  **completamente fuera del contexto** hasta que la invoques con `/nombre`. Para skills que sólo usas
  a mano, es ahorro puro sin ningún coste.
- **(a) Subagentes con `model: haiku`** — la documentación lo recomienda explícitamente para
  subtareas mecánicas. Haiku 4.5 son $1/$5 frente a $5/$25 de Opus 5: **cinco veces más barato**, y
  el contexto del subagente no entra en el tuyo.
- **(a) Reglas con ámbito de ruta** en `.claude/rules/` con patrón `paths:` — se cargan sólo cuando
  Claude toca ficheros que casan. Los `@path` de CLAUDE.md **no** ahorran nada: se cargan al arrancar.
- **(a) Actualizar Claude Code** — el changelog de junio-septiembre arregla media docena de fallos de
  caché de prompt (cambio de modelo reenviando todas las definiciones, refresco OAuth horario,
  sesiones con capturas). Es ahorro sin configurar nada.

---

## 5. Cinco cosas que este informe encontró y que afectan a COSMOS directamente

### 4.1 — El guardarraíl PostToolUse de COSMOS probablemente no ahorra lo que cree

**Documentación oficial de hooks** (https://code.claude.com/docs/en/hooks): la salida de un hook
`PostToolUse` sólo admite `hookSpecificOutput` con `additionalContext`, `systemMessage` y
`terminalSequence`. **No existe `updatedOutput`.** El hook se dispara *después* de que la herramienta
devolvió: **puede añadir contexto, nunca quitarlo.**

Lo confirma de forma independiente el README de `Mibayy/token-savior`, que tiene 34 compactadores
`PostToolUse` y avisa: *«These run in PostToolUse, so they do not shrink the current turn. The hook
fires after the tool has returned; it can add context, not remove it. The compact rendering is
appended below the raw output, which stays.»*

**Qué significa para COSMOS:** el guardarraíl que «aparta a fichero las salidas de más de 50 KB»
sólo puede estar consiguiendo **persistencia** (la salida completa sobrevive a una compactación), no
**reducción del turno**. La reducción hay que hacerla en `PreToolUse` con `updatedInput`, que sí
puede reescribir la orden antes de ejecutarla — y es exactamente el patrón que recomienda la
documentación oficial de costes, con su propio ejemplo de reescribir una orden de tests a
`| grep -A 5 -E '(FAIL|ERROR|error:)' | head -100`, cuantificado como *«reducing context from tens of
thousands of tokens to hundreds»*.

*(El aviso de G05 sobre secretos dice «los valores reales no llegaron aquí», lo que sugiere que esa
parte usa otro mecanismo. Merece una comprobación, no una conclusión desde fuera.)*

### 4.2 — El umbral de 50 KB de COSMOS está por debajo del corte nativo, y por tanto nunca se dispara en Bash

**`bashOutputMaxChars` vale 30.000 caracteres por defecto** — unos **30 KB**. El guardarraíl de
COSMOS corta a **50 KB**. Para salidas de Bash, **el corte nativo ocurre primero, siempre**: ninguna
salida de Bash llega jamás a 50 KB. El umbral de COSMOS sólo puede activarse en respuestas MCP
(`MAX_MCP_OUTPUT_TOKENS` = 25.000 tokens ≈ 100 KB) y en lecturas de fichero.

La acción no es programar nada: es **bajar `bashOutputMaxChars` y `MAX_MCP_OUTPUT_TOKENS`**, que hacen
nativamente y bien lo que el guardarraíl intenta hacer, y guardar el guardarraíl para lo que sólo él
sabe hacer (tapar secretos).

### 4.3 — El presupuesto de 4.000 tokens mide el 8 % del problema

COSMOS mide su propia entrada con rigor: 3.772 tokens en el peor caso contra un presupuesto de 4.000.
Pero el arranque en frío **medido** de una sesión real es de **35.000 a 51.400 tokens**. COSMOS está
afinando al detalle una partida que es **menos de una décima parte** del gasto de arranque; el 90 %
restante son prompt de sistema, herramientas integradas, skills y memoria.

No es una crítica al presupuesto — es que hace falta un segundo medidor al lado, sobre `/context`
y `/skill-doctor`, para las partidas que COSMOS hoy no ve.

### 4.4 — Dos candidatas populares cuestan más que el presupuesto entero de COSMOS

Aplicando la regla de `spec/PUEBLO.md` de medir contra el presupuesto **antes** de instalar:

| Herramienta | Coste estimado por sesión | Frente al presupuesto de 4.000 |
|---|---:|---:|
| **Serena** (~20 herramientas + prompt de 611 tokens medidos) | **~6.600 tokens** | **165 %** |
| **code-review-graph** (30 herramientas MCP por defecto) | **~9.000 tokens** | **225 %** |
| ripwire (17 skills, frontmatter medido) | 1.721 tokens | 43 % |
| ripwire (6 skills) | ~600 tokens | 15 % |
| Toolport en modo lazy (medido por ellos) | 886 tokens | 22 % |

Serena además **no publica ninguna medición propia de ahorro de tokens** — el «60-80 %» que circula
es de blogs de terceros. Cobra 6.600 tokens de entrada por sesión a cambio de una promesa sin medir.

### 4.5 — No construyas el medidor de COSMOS sobre la línea MCP de `/context`

Medición con tres métodos cruzados (https://www.async-let.com/posts/claude-code-mcp-token-reporting/):
para el mismo servidor, el tokenizador directo da **14.081 tokens**, el endpoint `count_tokens`
**15.282**, y **`/context` reporta 45.018**. El exceso es **doble conteo**: `/context` repite las
instrucciones de sistema compartidas por cada herramienta. **Infla el coste MCP unas 3×.**

Si COSMOS va a medir el coste de un servidor MCP, el método correcto está publicado y es sencillo:
`initialize` + `tools/list` por stdio, serializar cada definición y contar con el tokenizador real
(https://github.com/zhang-liz/mcp-token-benchmark, MIT). También existe
https://github.com/AraneaDev/ariadne (MIT, 1★, pre-release), que hace justo eso como plugin: mide lo
que cuestan **por turno** los servidores instalados y cuáles no se llaman nunca. Demasiado verde para
instalarlo; la idea es la correcta.

---

## 6. Resumen de veredictos

| Herramienta | Veredicto | En una frase |
|---|---|---|
| **ccusage** (`ccusage/ccusage`) | **instalar** | Cero tokens de contexto, y sin medir el resto es opinión. |
| **ccstatusline** | **instalar** | Cero tokens de contexto; el widget de contexto y esfuerzo es lo que hace accionable todo lo demás. |
| **ripwire** | **instalar** | Camino principal por CLI (cero definiciones de herramienta), publica sus derrotas, y ataca la partida que la documentación oficial señala como la mayor. |
| **Toolport** | ficha | Mecanismo correcto y el mejor benchmark del informe, pero Claude Code ya trae carga diferida nativa; lo valioso es su medidor. |
| **Headroom** | ficha | Su *effort routing* es la mejor idea del informe y COSMOS la puede copiar con un hook, sin meter un proxy en la autenticación. |
| **Serena** | ficha | Mecanismo correcto, pero 6.600 tokens por sesión (165 % del presupuesto) a cambio de un ahorro que no mide. |
| **code-review-graph** | ficha | Benchmark reproducible y admisiones honestas, pero 30 herramientas MCP y un titular que el propio README desautoriza. |
| **Paritok** | ficha | La medición más seria de los compresores (SWE-bench Lite, pérdida cuantificada); coste operativo excesivo. |
| **ponytail** | ficha | Ataca el lado caro (salida, 5×) y está medido, pero «lo más perezoso que funcione» es una decisión de diseño, no de tokens. |
| **mcptoon** / **mcp-token-benchmark** | ficha (metodología) | Instrumentos de medida; lo que COSMOS necesita de aquí es la técnica de conteo. |
| **caveman** | **descartar** | `outputStyle: "Concise"` hace lo mismo nativamente, sin 1.690 tokens por sesión y sin hablar como un cavernícola. |
| **claude-mem** | **descartar** | Inyecta en vez de recortar, su «10×» no está medido, manda datos fuera por defecto y lleva un memecoin pegado. |
| **token-savior** | **descartar** (la lección, catalogarla) | Cifras que su propio autor marca como no verificables; su retractación vale más que la herramienta. |
| **token-diet** | **descartar** | Sin licencia y parado desde el día siguiente a crearse. |
| **Aider (repomap)** | **descartar** | No se engancha a Claude Code y lleva parado desde el 2026-05-22. |
| **serena-slim, mcp-funnel, lazy-mcp, rtk, mcp-rtk, token-guard, token_saver_nova, claude-token-inspector** | **descartar** | Todos parados, diminutos, o cubiertos por una función nativa. |

---

## 7. Fuentes

**Documentación oficial** (verificada 2026-09-11): https://code.claude.com/docs/en/hooks ·
https://code.claude.com/docs/en/settings-reference · https://code.claude.com/docs/en/env-vars ·
https://code.claude.com/docs/en/costs · https://code.claude.com/docs/en/context-window ·
https://code.claude.com/docs/en/mcp · https://code.claude.com/docs/en/model-config ·
https://code.claude.com/docs/en/prompt-caching · https://code.claude.com/docs/en/memory ·
https://code.claude.com/docs/en/sub-agents · https://code.claude.com/docs/en/output-styles ·
https://code.claude.com/docs/en/statusline · https://code.claude.com/docs/en/commands ·
https://code.claude.com/docs/en/changelog · https://platform.claude.com/docs/en/about-claude/pricing ·
https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md

**Mediciones independientes:** https://www.async-let.com/posts/claude-code-mcp-token-reporting/ ·
https://github.com/zhang-liz/mcp-token-benchmark ·
https://www.xda-developers.com/claude-code-using-fifty-thousand-tokens-before-typed-prompt-fixed-it/ ·
https://github.com/btsouth/toolport/blob/main/BENCHMARK.md

**Calidad y contexto largo:** https://arxiv.org/abs/2605.12366 (Anthropic) ·
https://arxiv.org/abs/2606.29718 · https://arxiv.org/abs/2607.17937

**Anthropic:** https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models
(24-07-2026, sin método publicado) · https://www.anthropic.com/engineering/advanced-tool-use
(24-11-2025, las cifras duras de tool search y *programmatic tool calling*)
