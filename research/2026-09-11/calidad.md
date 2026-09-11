# Informe: mecanismos que mejoran la calidad del resultado final de una sesión de agente

> Investigación para COSMOS. Fecha de la investigación: **2026-09-11**.
> Método: `gh api repos/<owner>/<repo>` (token autenticado) para estrellas / licencia / último push,
> y WebFetch sobre la página real para la documentación. Todas las cifras de esta tabla están
> verificadas hoy; si una no se pudo verificar, se marca **«no verificado»** en vez de estimarse.
>
> Convención: 🔧 **MECANISMO** = falla solo, ejecuta código, deniega o bloquea sin que el modelo
> tenga que acordarse · 📝 **PROSA** = instrucción que el modelo debe recordar en el turno 40 ·
> ⚠️ = mecanismo real con hueco declarado por el propio proyecto.
>
> Criterio de veredicto (doctrina COSMOS): «implementar como guardarraíl» solo si es 🔧 **y** cubre
> un hueco que COSMOS hoy no tiene. Un 📝 excelente se cataloga como ficha, no se instala.

---

## Resumen ejecutivo en una tabla

| # | Mecanismo | Tipo | Coste/sesión | Veredicto |
|---|---|---|---|---|
| M01 | `verify-gate.sh` + `track-read.sh` (contrato default-FAIL, Anthropic) | 🔧⚠️ | ~0 (solo al bloquear, ~45 tok) | **Implementar como guardarraíl** |
| M02 | `/goal` nativo (evaluador Haiku tras cada turno) | 🔧 | ~0 en el hilo principal; tokens Haiku aparte | **Implementar** (documentar + usar) |
| M03 | Hooks `type: "agent"` y `type: "prompt"` en `Stop` | 🔧 | ~0 salvo al bloquear | **Implementar como guardarraíl** |
| M04 | `agents/evaluator.md` — evaluador de contexto fresco | 🔧 (si lo lanza un guion) | 0 en el hilo principal | **Implementar como guardarraíl** |
| M05 | hookify `require-tests-stop.local.md` (oficial) | 🔧 | ~60 tok al bloquear | **Implementar** (la forma, no la regla) |
| M06 | `ralph-loop` plugin oficial (Stop hook que realimenta el prompt) | 🔧 | prompt completo × iteración | **Catalogar como ficha** |
| M07 | `obra/superpowers` — `verification-before-completion` | 📝 | ~780 tok/sesión fijos | **Catalogar como ficha** |
| M08 | `/code-review` oficial — 5 revisores + filtro de confianza ≥80 | 🔧 (guion de comando) | alto (multiagente) | **Implementar la forma del filtro** |
| M09 | `anthropics/claude-code-action` — revisión adversarial en PR | 🔧 (CI) | 0 en la sesión local | **Catalogar como ficha** |
| M10 | `github/spec-kit` — SDD con `constitution.md` | 📝 | variable, alto | **Catalogar como ficha** |
| M11 | `EveryInc/compound-engineering-plugin` — plan→work→review→compound | 📝 | muy alto (skills de 30-100 KB) | **Catalogar como ficha** |
| M12 | `skill-creator` — evals con `evals/evals.json` | 🔧 | 0 (corre fuera de la sesión) | **Implementar como guardarraíl** |
| M13 | `claude plugin eval` — umbral + código de salida + brazo baseline | 🔧 | 0 (corre fuera de la sesión) | **Implementar como guardarraíl** |
| M14 | `protect-tests` — deniega borrar/saltar tests | 🔧 | ~30 tok al bloquear, 0 si pasa | **Implementar como guardarraíl** |
| M15 | Typecheck por lotes en `Stop` + `format-code` de coste cero | 🔧 | 100-300 tok al bloquear, 0 si pasa | **Implementar como guardarraíl** |

Tratados **sin número** porque no compiten por las 15 plazas: `gotalab/cc-sdd` (**descartar**:
«puertas» que no deniegan nada, 4 meses parado), `/skill-doctor` (**ficha**: mide coste y uso de
skills, pero no es una puerta), la **memoria automática nativa** (línea base con tope duro propio, ver
área 5), `thedotmack/claude-mem` y `Digital-Process-Tools/claude-remember` (**descartar**, ver área 5),
y `disler/claude-code-hooks-mastery` (**ficha** por el patrón de hooks por subagente; **descartar** el
código, sin licencia).

---

## 0. El hallazgo que cambia el marco: Anthropic publicó su propio arnés

Antes de entrar por áreas hay que decir esto, porque reordena todo lo demás. **Anthropic publicó en
mayo de 2026 los ficheros exactos de un arnés de sesión larga**, con los mismos cinco enganches que
COSMOS derivó por su cuenta auditando un harness de terceros.

- **URL**: https://github.com/anthropics/cwc-long-running-agents
- **Licencia**: Apache-2.0 · **Estrellas**: 676 · **Creado**: 2026-05-06 · **Último push**: 2026-05-13
  (verificado hoy con `gh api repos/anthropics/cwc-long-running-agents`)
- **Estado declarado por el propio repo**: «Built as the take-home for the Long-Running Agents
  station at Code with Claude 2026. **These are example ingredients, not a turnkey harness.** Event
  demo; not maintained and not accepting contributions.»

Ficheros (todos verificados leyendo el blob):

| Fichero | Evento | Qué hace |
|---|---|---|
| `claude-code-config/.claude/hooks/verify-gate.sh` (1330 B) | `PreToolUse` matcher `Write\|Edit` | Deniega escribir en `test-results.json` si no se ha **leído** antes un fichero de evidencia |
| `claude-code-config/.claude/hooks/track-read.sh` (564 B) | `PreToolUse` matcher `Read` | Apunta qué evidencias se abrieron (`.claude/.evidence-reads`) |
| `claude-code-config/.claude/hooks/commit-on-stop.sh` (750 B) | `Stop` | `git commit -am "session checkpoint: <fecha>"` |
| `claude-code-config/.claude/hooks/kill-switch.sh` (391 B) | `PreToolUse` matcher `*` | Bloquea **toda** llamada mientras exista `./AGENT_STOP` |
| `claude-code-config/.claude/hooks/steer.sh` (754 B) | `PreToolUse` matcher `*` | Vuelca `STEER.md` al agente una vez y lo vacía |
| `claude-code-config/.claude/agents/evaluator.md` (1740 B) | subagente | Revisor escéptico sin `Write`/`Edit`; devuelve `PASS` / `NEEDS_WORK` |

Los tres primitivos que el README nombra:

> - **Default-FAIL contract.** Every criterion starts `false`; the agent can't mark it passing without opening evidence first.
> - **Fresh-context evaluator.** A separate agent with no Write/Edit tools grades the work from a context window that never saw the build.
> - **Agent-maintained handoff.** The agent writes its own progress notes and commits to git so the next session picks up cleanly.

**Lo que esto vale para COSMOS**: confirma G03 y G04 desde la fuente oficial (`track-read.sh` es
literalmente G04 en 20 líneas, y más flojo: no ata sesión ni SHA-256) y señala **el hueco que COSMOS
no cubre: el contrato default-FAIL sobre el veredicto funcional**, no sobre el árbol de ficheros.

---

## Área 1 — Bucles de verificación antes de terminar

### M01 · Contrato default-FAIL: `verify-gate.sh` + `track-read.sh` 🔧⚠️

- **URL**: https://github.com/anthropics/cwc-long-running-agents/blob/main/claude-code-config/.claude/hooks/verify-gate.sh
- **Licencia**: Apache-2.0 · **Estrellas (repo)**: 676 · **Último push**: 2026-05-13 (verificado hoy)
- **Dónde vive**: `PreToolUse` con matcher `Write|Edit`, declarado en
  `claude-code-config/.claude/settings.json`. El registro de evidencias es
  `./.claude/.evidence-reads`, poblado por `track-read.sh` en `PreToolUse` matcher `Read`.
- **Mecanismo o prosa**: 🔧 mecanismo. Devuelve por stdout
  `{"decision":"block","reason":"Cannot modify the results file: no screenshot or console-log evidence has been Read this session..."}`
  y **consume la evidencia** (`: > "$log"`), así que el siguiente cambio exige prueba fresca.
- **Hueco declarado por el propio fichero** (está en los comentarios, verbatim):
  > «This is a teaching example, not a security boundary. Known gaps a real enforcement layer would
  > close: this only hooks Write/Edit (Bash sed/jq can rewrite the file unchecked); the path match is
  > basename-only and case-sensitive; and any evidence read unlocks any result row, not the
  > corresponding one.»
- **Evidencia de que mejora el resultado**: anecdótica pero de primera mano de Anthropic. El README
  del repo: *«Agents will mark a feature "passing" after a unit test or a curl when the UI is visibly
  broken. Asking nicely in the prompt doesn't reliably stop this.»* Y el post de ingeniería de nov-2025
  (https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents):
  *«One final major failure mode that we observed was Claude's tendency to mark a feature as complete
  without proper testing.»* **No hay cifras**: el propio post no publica porcentajes ni benchmark A/B.
- **Coste en tokens**: ~0 en el caso normal (el hook sale con `exit 0` sin imprimir nada). Al bloquear
  inyecta el `reason`: el texto literal del fichero son 27 palabras, ≈35-45 tokens con el envoltorio JSON.
- **Veredicto**: **implementar en COSMOS como guardarraíl**, cerrando los tres huecos que el propio
  fichero declara (COSMOS ya sabe cerrar dos: G04 ata sesión+SHA-256, y G03 ya lee redirecciones de
  shell, así que la fuga «Bash sed/jq» está resuelta en su lector de órdenes).

### M02 · `/goal` nativo — evaluador separado tras cada turno 🔧

- **URL**: https://code.claude.com/docs/en/goal (verificado hoy)
- **Licencia / estrellas / commit**: no aplica, es funcionalidad de producto de Claude Code.
  No verificable por `gh api`.
- **Dónde vive**: no es un fichero del repo. La doc lo dice literalmente:
  *«`/goal` is a wrapper around a session-scoped prompt-based Stop hook.»*
- **Mecanismo o prosa**: 🔧 mecanismo puro, y además **el patrón exacto que COSMOS persigue**: tras
  cada turno, Claude Code manda la condición y la conversación al *small fast model* (Haiku por
  defecto en la API de Claude) y recibe uno de tres veredictos: `Not yet met` / `Met` / `Impossible`.
- **Detalles verificados en la página**:
  - La condición admite hasta **4.000 caracteres**.
  - Una sola meta activa por sesión; se restaura al reanudar (`--continue`, `--resume`, selector).
  - Freno anti-bucle: *«If Claude keeps answering the evaluator without making progress (no tool use
    for several turns in a row), Claude Code stops the loop, prints a warning, and returns control to
    you with the goal still set.»*
  - **Límite importante**: *«It doesn't run commands or read files independently, so write the
    condition as something Claude's own output can demonstrate.»* → el evaluador **solo juzga lo que
    ya está en el transcript**. Un árbol rojo que nunca se imprimió, no lo ve.
  - Se desactiva si `disableAllHooks` es `true` o si hay `allowManagedHooksOnly` en ajustes
    gestionados.
- **Coste en tokens**: la doc: *«Evaluation tokens are billed on the small fast model configured for
  your provider and are typically negligible compared to main-turn spend.»* **Cero tokens en el
  contexto principal** — el evaluador vive fuera. `/goal` con argumento vacío informa del gasto real
  acumulado en tokens de esa meta.
- **Veredicto**: **implementar en COSMOS**: no como código a copiar sino como **la salida barata de
  G02**. Hoy G02 bloquea el cierre con el árbol en rojo y cuenta hasta 3; `/goal` da el mismo bucle
  sin escribir nada. Documentar en `spec/GUARDARRAILES.md` que `cosmos` recomienda
  `/goal cosmos validar sale 0 y las dos suites están en verde` y que **el freno de `/goal` y el
  contador de G02 son independientes** — conviven sin pisarse.

### M03 · Hooks `type: "agent"` y `type: "prompt"` en `Stop` 🔧

- **URL**: https://code.claude.com/docs/en/hooks-guide#agent-based-hooks (verificado hoy)
- **Mecanismo o prosa**: 🔧. Son tipos de hook nuevos, al lado de `type: "command"`.
  - `type: "prompt"`: una sola llamada al modelo (Haiku por defecto, `model` configurable), timeout
    30 s. Devuelve `{"ok": false, "reason": "..."}`; en `Stop`/`SubagentStop` el `reason` **se
    realimenta a Claude para que siga trabajando**, salvo que además ponga `"impossible": true`.
  - `type: "agent"`: **marcado como experimental por la propia doc** («Agent hooks are experimental…
    For production workflows, prefer command hooks»). Lanza un subagente con herramientas: puede
    **leer ficheros y ejecutar comandos** para verificar. Timeout 60 s por defecto, hasta **50 turnos
    de uso de herramienta**. Placeholder `$ARGUMENTS` con el JSON del evento.
- **El ejemplo de la doc es literalmente el guardarraíl que COSMOS no tiene** (copiado verbatim):
  ```json
  { "hooks": { "Stop": [ { "hooks": [ {
    "type": "agent",
    "prompt": "Verify that all unit tests pass. Run the test suite and check the results. $ARGUMENTS",
    "timeout": 120 } ] } ] } }
  ```
- **Tope de bloqueos, verificado**: *«Claude Code overrides a Stop hook after it blocks **eight**
  times in a row without progress»*, y se sube con la variable de entorno
  `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`. **COSMOS usa tope 3**, más conservador que el del runtime; eso
  es una decisión propia legítima, pero conviene anotar en la spec que el runtime ya trae uno a 8 y
  que el de COSMOS es el que muerde primero.
- **Coste en tokens**: ~0 en el contexto principal cuando pasa. El hook `agent` corre en su propia
  ventana; solo el `reason` vuelve al hilo.
- **Veredicto**: **implementar en COSMOS como guardarraíl**. Es la vía oficial para un G02 que
  *ejecuta* la verificación en vez de fiarse del estado en disco.

### M04 · Evaluador de contexto fresco (`agents/evaluator.md`) 🔧

- **URL**: https://github.com/anthropics/cwc-long-running-agents/blob/main/claude-code-config/.claude/agents/evaluator.md
- **Licencia**: Apache-2.0 · **Estrellas (repo)**: 676 · **Último push**: 2026-05-13
- **Dónde vive**: `claude-code-config/.claude/agents/evaluator.md`, `tools: Read, Glob, Grep, Bash`
  (sin `Write`/`Edit`). Se invoca con `claude --agent evaluator -p "<prompt de revisión>"`.
- **Mecanismo o prosa**: mixto, y el repo es honesto sobre ello. El fichero es un prompt (📝), pero
  **el aislamiento sí es mecánico**: el subagente no tiene herramientas de escritura, así que no
  puede arreglar lo que critica ni certificarse a sí mismo. El README lo clasifica como
  «Enforcement: you invoke it», es decir, **solo es mecanismo si un guion lo lanza**.
- **Lo que lo hace no decorativo** (del propio fichero, verbatim): *«Plausibility is not correctness.
  A diff that looks reasonable paired with a screenshot that shows a broken layout is NEEDS_WORK.
  Missing evidence for any acceptance criterion is NEEDS_WORK.»* Y el contrato de salida es
  parseable: *«Begin your reply with the bare word `PASS` or `NEEDS_WORK` on its own line, with
  nothing before it, so a wrapper script can read the verdict.»*
- **El bucle completo que publica el repo** (`README.md`, verbatim):
  ```bash
  while grep -q '"passes": false' test-results.json; do
    claude -p "Read PROGRESS.md and build the next unfinished feature per CLAUDE.md."
    VERDICT=$(claude --agent evaluator -p "Review the most recent commit against its spec.")
    [ "$(echo "$VERDICT" | head -1)" = "PASS" ] || echo "$VERDICT" > NEXT_FINDINGS.md
  done
  ```
- **Evidencia**: del post de marzo-2026 (https://www.anthropic.com/engineering/harness-design-long-running-apps,
  **publicado 2026-03-24**): arquitectura inspirada en GAN con generador y evaluador; el evaluador
  usó Playwright MCP para *«click through the running application the way a user would»*.
  **Cifras reales publicadas en ese post** (las únicas que hay, y son de coste/duración, no de
  calidad medida): Retro Game Maker con arnés solo `20 min` / `$9` frente al arnés completo `6 hr` /
  `$200` (*«over 20x more expensive»*); un DAW en `3 hr 50 min` / `$124.70`. Diseño frontend: *«5 to
  15 iterations per generation»*. **No hay porcentaje de mejora de calidad publicado.**
- **Coste en tokens**: **0 en el contexto principal** — es otro proceso `claude`. El coste real es en
  dinero y está publicado arriba.
- **Veredicto**: **implementar en COSMOS como guardarraíl**. Es exactamente la «premisa invertida»
  que COSMOS ya practica con humanos (Codex escribe, Claude revisa), pero **automatizada y con
  contrato de salida parseable**. El aislamiento por `tools:` es lo que la hace mecánica.

### M05 · `hookify` — regla `require-tests-stop` oficial 🔧

- **URL**: https://github.com/anthropics/claude-plugins-official/blob/main/plugins/hookify/examples/require-tests-stop.local.md
- **Licencia**: Apache-2.0 · **Estrellas (repo)**: 36.141 · **Último push**: 2026-09-11 (hoy; verificado)
- **Dónde vive**: el plugin cablea `plugins/hookify/hooks/hooks.json` → `Stop` →
  `python3 hooks/stop.py`, con timeout 10 s. `stop.py` lee reglas de
  `.claude/hookify.*.local.md` y las evalúa con `core/rule_engine.py` (10.711 B).
- **La regla, verbatim**:
  ```yaml
  ---
  name: require-tests-run
  enabled: false
  event: stop
  action: block
  conditions:
    - field: transcript
      operator: not_contains
      pattern: npm test|pytest|cargo test
  ---
  ```
- **Mecanismo o prosa**: 🔧 mecanismo, pero **con un defecto de diseño grave para la doctrina COSMOS**:
  comprueba `transcript not_contains <patrón>`, es decir, **comprueba que el comando aparezca escrito,
  no que haya salido en verde**. Un `pytest` que falló satisface la regla. Viene `enabled: false` por
  defecto, y el propio fichero avisa: *«Enable this rule only when you want strict test enforcement.»*
- **Evidencia**: ninguna medida. Es un ejemplo del plugin oficial, sin benchmark.
- **Coste en tokens**: ~60 tokens (el cuerpo markdown de la regla se devuelve como razón del bloqueo);
  0 cuando pasa.
- **Veredicto**: **implementar la forma, nunca la política**. La forma que vale es «reglas de bloqueo
  declaradas en markdown con frontmatter, evaluadas por un motor» — encaja con `[sesion]` de
  `cosmos.toml`. La condición «aparece la palabra pytest» es justo la autocertificación que G03
  existe para impedir: COSMOS debe exigir **código de salida**, no presencia de una cadena.

### M06 · `ralph-loop` — plugin oficial del patrón Ralph Wiggum 🔧

- **URL**: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop
- **Licencia**: Apache-2.0 · **Estrellas (repo)**: 36.141 · **Último push**: 2026-09-11 (verificado hoy)
- **Dónde vive**: `plugins/ralph-loop/hooks/hooks.json` → `Stop` →
  `bash "${CLAUDE_PLUGIN_ROOT}/hooks/stop-hook.sh"` (7.533 B). Comandos `/ralph-loop` y
  `/cancel-ralph`.
- **Mecanismo o prosa**: 🔧. El `stop-hook.sh` emite `{"decision":"block","reason": <prompt>}` con
  `jq -n`, es decir, **realimenta el mismo prompt original** en cada iteración. Tiene freno:
  `max_iterations` en el frontmatter del fichero de estado, y `completion_promise` (una frase que, si
  aparece en el último bloque de texto del asistente, cierra el bucle). Lee el transcript JSONL y
  aplana solo los bloques de texto.
- **Origen y derivados verificados hoy**:
  - `ghuntley/how-to-ralph-wiggum` — sin licencia (NONE) · 1.753 ★ · último push 2026-01-11
  - `snarktank/ralph` — MIT · 21.762 ★ · último push 2026-02-02
  - `frankbria/ralph-claude-code` — MIT · 9.626 ★ · último push 2026-07-18
  - `snwfdhmp/awesome-ralph` — NONE · 918 ★ · último push 2026-02-03
  - `ghuntley/ralph` **no existe** (404 en la API hoy): el repo canónico es `how-to-ralph-wiggum`.
- **Evidencia**: anecdótica. El README del plugin cita a Huntley: *«Ralph is a Bash loop»*. El propio
  post de Anthropic de marzo-2026 lo cataloga como «Unattended loop» y enlaza este plugin.
- **Coste en tokens**: **el peor de la lista**. Reinyecta el prompt completo en cada iteración y el
  contexto de la sesión no se resetea (el bucle vive *dentro* de la sesión). Con un prompt de 500
  tokens y 50 iteraciones son 25.000 tokens solo de realimentación, más el crecimiento natural.
- **Veredicto**: **catalogar como ficha**. Como mecanismo de cierre es peor que `/goal` (que juzga una
  condición en vez de repetir un prompt) y peor que un Stop hook `type: agent` (que verifica de
  verdad). Su valor para COSMOS es la **forma del freno**: `max_iterations` + frase de terminación,
  que es lo mismo que el tope de 3 de G02.

### M07 · `obra/superpowers` — `verification-before-completion` 📝

- **URL**: https://github.com/obra/superpowers
- **Licencia**: MIT · **Estrellas**: 285.217 · **Último push**: 2026-09-11 (hoy; verificado con `gh api`)
- **Skills relevantes** (verificadas listando `skills/`): `verification-before-completion` (3.646 B),
  `test-driven-development` (9.015 B + `writing-good-tests.md` 8.268 B), `systematic-debugging`
  (9.465 B + `root-cause-tracing.md` 5.316 B), `brainstorming` (15.456 B), `writing-plans` (7.053 B),
  `subagent-driven-development` (32.339 B), `requesting-code-review`, `receiving-code-review`.
- **Dónde vive el único mecanismo del repo**: `hooks/hooks.json`. Lo leí entero, y **solo tiene un
  enganche**:
  ```json
  { "hooks": { "SessionStart": [ { "matcher": "startup|clear|compact",
    "hooks": [ { "type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start", "shell": "bash", "async": false } ] } ] } }
  ```
  **No hay Stop hook. No hay PreToolUse. No hay PostToolUse.** El `session-start` inyecta el cuerpo
  de `skills/using-superpowers/SKILL.md` envuelto en `<EXTREMELY_IMPORTANT>`.
- **Mecanismo o prosa**: 📝 **prosa, y esto es el hallazgo del apartado**. `verification-before-completion`
  es un texto excelente —«NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE», una tabla de
  racionalizaciones, banderas rojas— pero **nada lo hace cumplir**. Es exactamente la definición de
  «exhortación» del `GOAL.md` de COSMOS: una regla que el modelo tiene que recordar en el turno 40.
  La única palanca real es un `SessionStart` que inyecta texto.
- **Evidencia de que mejora el resultado**: solo la reputación del proyecto (285.217 ★). **No hay
  benchmark, A/B ni medición publicada.** Las 285 mil estrellas miden adopción, no calidad de salida.
- **Coste en tokens**: **medido**. `skills/using-superpowers/SKILL.md` son **3.108 bytes** ≈ **780
  tokens fijos en cada arranque**, cada `/clear` y cada compactación, más los ~100 tok/skill de
  metadata × 14 skills ≈ 1.400 tok. Total del orden de **2.200 tok/sesión** solo por estar instalado,
  antes de disparar ninguna skill. Y una skill grande como `subagent-driven-development` son 32.339 B
  ≈ **8.000 tokens** de golpe al dispararse.
- **Veredicto**: **catalogar como ficha**. El *contenido* de `verification-before-completion` es la
  mejor redacción pública del principio y merece copiarse como texto de referencia en
  `spec/GUARDARRAILES.md`; el *proyecto* no aporta ningún mecanismo que COSMOS no tenga ya, y su
  coste fijo de ~2.200 tok/sesión es exactamente el tipo de fuga que el medidor de COSMOS existe para
  cazar (compárese con la fuga de 2.187 tok/sesión documentada en `research/PATRONES-HARNESS.md`).

---

## Área 2 — Planificación forzada antes de codificar

### M10 · `github/spec-kit` — desarrollo dirigido por especificación 📝

- **URL**: https://github.com/github/spec-kit
- **Licencia**: MIT · **Estrellas**: 135.637 · **Último push**: 2026-09-10 (verificado hoy)
- **Dónde vive**: `.specify/memory/constitution.md` es el artefacto central; los comandos son ficheros
  markdown `speckit.*` (p. ej. `presets/constitution-sync/commands/speckit.constitution.md`,
  `extensions/assess/commands/speckit.assess.{intake,research,shape,define,decide}.md`,
  `extensions/bug/commands/speckit.bug.{assess,fix,test}.md`).
- **Mecanismo o prosa**: 📝 **prosa estructurada**. Recorrí el árbol completo del repo con
  `gh api .../git/trees/main?recursive=1`: **no hay ningún `hooks.json` ni `settings.json` con
  enganches de Claude Code**. Lo que sí hay son guiones reales (`extensions/git/scripts/bash/*.sh`:
  `auto-commit.sh`, `create-new-feature-branch.sh`, `git-common.sh`, `initialize-repo.sh`) y un
  `.pre-commit-config.yaml` **para el propio repo**, no para el usuario. La disciplina
  spec → plan → tasks → implement la sostiene el modelo leyendo comandos, no un hook que deniegue.
- **Evidencia**: adopción masiva (135 mil ★) y respaldo institucional de GitHub; **sin medición
  publicada de mejora de calidad**.
- **Coste en tokens**: no medido con precisión; alto por construcción — cada comando `speckit.*` es un
  markdown que entra entero al dispararse, y `constitution.md` se relee en cada fase.
- **Veredicto**: **catalogar como ficha**. Aporta vocabulario y plantillas, no un guardarraíl.

### (sin número — descartado) · `gotalab/cc-sdd` — puertas de revisión de requisitos y diseño 📝

- **URL**: https://github.com/gotalab/cc-sdd
- **Licencia**: MIT · **Estrellas**: 3.662 · **Último push**: **2026-05-20** (verificado hoy;
  ~4 meses sin tocar)
- **Dónde vive**: `.kiro/settings/rules/requirements-review-gate.md`,
  `.kiro/settings/rules/design-review-gate.md`, `.kiro/settings/rules/gap-analysis.md`, y skills
  `kiro-verify-completion`, `kiro-validate-{design,gap,impl}` bajo
  `tools/cc-sdd/templates/agents/antigravity-skills/skills/`.
- **Mecanismo o prosa**: 📝. El nombre «gate» es engañoso: son ficheros de reglas en markdown que el
  agente debe leer y obedecer. Busqué `hook|settings.json` en el árbol completo: **no aparece ningún
  enganche de Claude Code**; lo único que hay son workflows de CI del propio repo
  (`.github/workflows/claude.yml`, `claude-dispatch.yml`).
- **Evidencia**: ninguna medida.
- **Coste en tokens**: alto y no medido (multitud de plantillas y reglas).
- **Veredicto**: **descartar**. Una «puerta» que no deniega nada es una exhortación con nombre de
  puerta, y COSMOS ya tiene el vocabulario. Cuatro meses sin commits refuerzan la decisión.

### M11 · `EveryInc/compound-engineering-plugin` — plan → work → review → compound 📝

- **URL**: https://github.com/EveryInc/compound-engineering-plugin
- **Licencia**: MIT · **Estrellas**: 25.020 · **Último push**: 2026-09-11 (hoy; verificado)
  · **Versión**: 3.24.0 (`.claude-plugin/plugin.json`)
- **Dónde vive**: 35 skills bajo `skills/ce-*`. Las del ciclo: `ce-brainstorm`, `ce-plan`, `ce-work`,
  `ce-code-review`, `ce-compound`, `ce-compound-refresh`, `ce-handoff`, `ce-proof`, `ce-noslop`.
- **Mecanismo o prosa**: 📝 con guiones de apoyo. Busqué `hook` en el árbol completo: **los únicos
  `hooks.json` están en `tests/fixtures/`** — el plugin **no instala ningún enganche**. Sí hay
  ejecutables reales dentro de las skills (`ce-brainstorm/scripts/peer-job-runner.py` de 104.164 B,
  `packs-resolve.py` 31.513 B, `elevation-dispatch.sh` 13.515 B, `ce-babysit-pr/scripts/pr-snapshot`
  de 176.012 B), pero los lanza el modelo cuando decide, no un evento.
- **Lo interesante para el área 3**: `skills/ce-code-review/references/` contiene
  `cross-model-review.md` (36.022 B), `cross-model-eval.md`, `action-class-rubric.md` y un
  `findings-schema.json` (6.576 B) — es decir, **revisión adversarial con esquema de hallazgos y
  varios modelos**. Eso sí es transferible.
- **Evidencia**: el `homepage` del plugin apunta a
  https://every.to/source-code/my-ai-had-already-fixed-the-code-before-i-saw-it — un relato, no una
  medición. **Sin cifras.**
- **Coste en tokens**: **el más alto del informe**. `AGENTS.md` son 55.920 B (~14.000 tok) y
  `CONCEPTS.md` 36.903 B (~9.200 tok); `ce-brainstorm/references/synthesis-summary.md` son 29.228 B
  y `ce-babysit-pr/references/watch-loop.md` 44.105 B (~11.000 tok cada carga). Una sola skill de
  este plugin puede costar más que todo el presupuesto de sesión de COSMOS.
- **Veredicto**: **catalogar como ficha**, con la nota de coste. Lo único que COSMOS debería copiar es
  el `findings-schema.json`: un esquema de hallazgos hace que la revisión sea contrastable en vez de
  opinable.

---

## Área 3 — Revisión adversarial automatizada

### M08 · `/code-review` oficial — 5 revisores en paralelo + filtro de confianza ≥ 80 🔧

- **URL**: https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-review/commands/code-review.md
- **Licencia**: Apache-2.0 · **Estrellas (repo)**: 36.141 · **Último push**: 2026-09-11 (verificado hoy)
- **Dónde vive**: `plugins/code-review/commands/code-review.md` (7.422 B), con
  `allowed-tools` restringido a subcomandos `gh` concretos
  (`Bash(gh pr diff:*)`, `Bash(gh pr comment:*)`, …).
- **Mecanismo o prosa**: mixto pero **el filtro sí es mecánico y es lo valioso**. El guion:
  1. Un agente Haiku decide elegibilidad (cerrado / borrador / trivial / ya revisado).
  2. Otro Haiku lista las rutas de los `CLAUDE.md` relevantes (**las rutas, no el contenido** — ahorro
     de contexto deliberado).
  3. **5 agentes Sonnet en paralelo**, cada uno con un ángulo distinto: adherencia a `CLAUDE.md`;
     escaneo somero de bugs obvios *sin leer contexto extra*; `git blame` e historia; comentarios de
     PRs anteriores que tocaron esos ficheros; comentarios en el código.
  4. **Por cada hallazgo, un Haiku puntúa 0-100 la confianza** con una rúbrica dada verbatim
     (0 falso positivo · 25 dudoso · 50 verificado pero nimio · 75 muy probable · 100 certeza).
  5. *«Filter out any issues with a score less than 80.»* Si no queda ninguno, **no comenta**.
- **La lista de falsos positivos que declara explícitamente** (verbatim, abreviada): problemas
  preexistentes; nimiedades que un ingeniero sénior no señalaría; *«Issues that a linter, typechecker,
  or compiler would catch»*; falta de cobertura o seguridad genérica salvo que `CLAUDE.md` lo exija;
  cosas silenciadas con un `lint ignore`; **líneas que el usuario no modificó**.
- **Evidencia**: es el revisor que Anthropic usa sobre sus propios repos. Sin cifras publicadas.
- **Coste en tokens**: alto pero **fuera del hilo principal**: 1 Haiku + 1 Haiku + 1 Haiku + 5 Sonnet
  + N Haiku de puntuación. Al hilo solo vuelve el comentario final, que el guion obliga a que sea
  breve.
- **Veredicto**: **implementar la forma del filtro en COSMOS**. El patrón «cada hallazgo lleva una
  puntuación de confianza calculada por un juez separado, y por debajo de un umbral no se emite» es
  directamente aplicable a `cosmos/juez.py` y a la «premisa invertida». Es lo que convierte una
  revisión adversarial en algo que no ahoga en ruido.

### M09 · `anthropics/claude-code-action` — revisión adversarial en el PR 🔧

- **URL**: https://github.com/anthropics/claude-code-action
- **Licencia**: MIT · **Estrellas**: 8.845 · **Último push**: 2026-09-10 (verificado hoy)
- **Dónde vive**: `.github/workflows/claude-review.yml`, disparado por
  `on: pull_request: types: [opened]`. Además el repo trae 5 subagentes revisores especializados en
  `.claude/agents/`: `code-quality-reviewer.md`, `security-code-reviewer.md`,
  `performance-reviewer.md`, `test-coverage-reviewer.md`, `documentation-accuracy-reviewer.md`.
- **Mecanismo o prosa**: 🔧 mecanismo de CI. El workflow verificado hoy:
  ```yaml
  prompt: "/review-pr REPO: ${{ github.repository }} PR_NUMBER: ${{ github.event.pull_request.number }}"
  claude_args: |
    --allowedTools "mcp__github_inline_comment__create_inline_comment"
    --model "claude-opus-4-7"
  ```
  Autentica por **OIDC / Workload Identity Federation** (`anthropic_federation_rule_id`), no con API
  key estática, y se salta los PR de forks porque no pueden acuñar el token.
- **Evidencia**: sin cifras; es infraestructura oficial en producción sobre sus propios repos.
- **Coste en tokens**: **0 en la sesión local**, corre en GitHub Actions. Cuesta dinero de API.
- **Veredicto**: **catalogar como ficha**. COSMOS ya tiene gate de pre-commit y CI; esto es la capa de
  PR, útil pero fuera del ámbito «sesión de agente». Lo transferible es el catálogo de **cinco ángulos
  de revisión con un subagente por ángulo**.

---

## Área 4 — Evaluación de skills y plugins

### M12 · `skill-creator` — evals, benchmark y A/B ciego sobre skills 🔧

- **URL**: https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator
- **Licencia**: Apache-2.0 · **Estrellas (repo)**: 36.141 · **Último push**: 2026-09-11 (verificado hoy)
- **Dónde vive** (ficheros verificados listando el árbol):
  - `skills/skill-creator/scripts/run_eval.py` (11.464 B) — *«Tests whether a skill's description
    causes Claude to trigger (read the skill) for a set of queries. Outputs results as JSON.»*
    Lanza `claude -p` de verdad creando un fichero de comando en `.claude/commands/`.
  - `scripts/aggregate_benchmark.py` (14.386 B), `scripts/run_loop.py` (13.605 B),
    `scripts/improve_description.py` (11.116 B), `scripts/quick_validate.py` (3.972 B),
    `scripts/generate_report.py` (12.847 B)
  - `agents/grader.md` (9.049 B), `agents/comparator.md` (7.287 B), `agents/analyzer.md` (10.376 B)
  - `eval-viewer/generate_review.py` + `viewer.html` (44.998 B)
- **El contrato de datos, verbatim de `references/schemas.md`**: los evals viven en
  **`evals/evals.json`** dentro del directorio de la skill:
  ```json
  { "skill_name": "example-skill",
    "evals": [ { "id": 1, "prompt": "...", "expected_output": "...",
                 "files": ["evals/files/sample1.pdf"],
                 "expectations": ["The output includes X", "The skill used script Y"] } ] }
  ```
  Y `history.json` guarda la progresión con `expectation_pass_rate` (0.65 → 0.75 en el ejemplo) y
  `grading_result` (`baseline` / `won`).
- **Mecanismo o prosa**: 🔧 mecanismo puro — son guiones de Python que ejecutan, no instrucciones.
- **Evidencia**: Anthropic publicó el porqué en
  https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills. El concepto
  clave verificado: **detección de regresión por modelo** — cuando sale un modelo nuevo se rehacen los
  benchmarks y, si el *baseline* sin skill iguala o supera a la skill, la skill está fijando patrones
  obsoletos y toca retirarla.
- **Coste en tokens**: **0 en la sesión** — se corre fuera, como un test.
- **Veredicto**: **implementar en COSMOS como guardarraíl**. Es el equivalente exacto del *holdout
  ciego* que COSMOS ya tiene para el buscador, extendido a las skills/pueblos: una tasa de acierto
  medida, sellada y repetible. Encaja como `cosmos acertar --skills`.

> Nota: `claude plugin eval` (M13) y `/skill-doctor` se verifican en la sección **Área 4 (ampliación)**
> más abajo, con la doc oficial.

---

## Área 4 (ampliación) — `claude plugin eval`, `/skill-doctor`, `/code-review`, `/loop`

Verificado contra las páginas reales y contra el binario local (`claude 2.1.268`).

### M13 · `claude plugin eval` — suite de evals con umbral y código de salida 🔧

- **Estado**: **existe, pero en early access por organización y SIN página pública de documentación.**
  Comprobado: `https://code.claude.com/docs/en/plugin-eval.md` devuelve **404**, y la palabra «eval»
  no aparece en `https://code.claude.com/docs/llms.txt`, ni en `plugins.md`, `plugins-reference.md`
  ni `cli-reference.md`. Invocarlo responde `` `plugin eval` is currently in early access ``.
  **Todo lo que sigue está verificado contra el `--help` del binario, no contra una página**; cítese
  como «referencia de early access, sin doc pública».
- **Ficheros exactos de una suite**: `<eval dir>/**/case.yaml` **o** `prompt.md` + `graders/*.md`.
  El directorio es `evals/` salvo `--eval-dir <dir>` o el campo `experimental.evals` del `plugin.json`.
  **No existe `evals/*.yaml` suelto ni `eval.json`.**
  - `prompt.md`: frontmatter (`name`, `tags`, `plugins`, `runs`, `max_turns`, `timeout_seconds`,
    `allowed_tools`, `model`, `append_system_prompt`, `env` con claves `EVAL_*`) + cuerpo = prompt.
    Defaults: `runs: 3`, `max_turns: 10`, `timeout_seconds: 300`.
  - `graders/<nombre>.md`: frontmatter `type:` + cuerpo = rúbrica. Tipos: `regex`, `tool_used`,
    `tool_order`, `file_exists`, `llm` (juez, haiku por defecto, voto 2 de 3), `baseline`.
  - `case.yaml` solo si hace falta `context.scaffold_script`, `context.history_file` o
    `context.add_dirs` (exige `schema_version: "1.1"` y `name`).
  - Mocks MCP opcionales: `<eval dir>/mocks/<server>/<tool>.md`.
- **Qué comprueba**: cada caso corre N veces en una sesión `claude -p` aislada (workspace desechable,
  `CLAUDE_CONFIG_DIR`/`HOME` frescos, solo el plugin bajo prueba, modo `dontAsk`). **Aviso
  declarado: no es sandbox de sistema operativo y la red NO está bloqueada.** Por defecto corre
  además un **brazo baseline sin el plugin** (`--ablation with-without`) y reporta el delta — que es
  exactamente la pregunta «¿esta skill aporta algo o el modelo ya lo hacía solo?».
- **CI**: `--json [path]`, `--threshold <0..1>` (default **1.0**), `--output-dir`, `--max-cost-usd`.
  Códigos de salida: `0` todos ≥ umbral · `1` por debajo, error de carga, sin casos o gate cerrado ·
  `2` parcial (techo de coste o credencial rechazada) · `130` interrumpido · `143` terminado.
- **Informe**: `<eval dir>/results/<timestamp>/aggregate-result.json` (v1: `schemaVersion`, `suite`,
  `cases[].arms.{with,without}[].graders[]`, `aggregates`) + `report.html`.
- **Mecanismo o prosa**: 🔧 mecanismo puro: puntúa y devuelve código de salida. El grader `llm` mete
  juicio no determinista **dentro** del mecanismo — hay que saberlo.
- **Coste en tokens**: 0 en la sesión; corre fuera, como un test. Cuesta dinero de API (por eso
  `--max-cost-usd`).
- **Veredicto**: **implementar en COSMOS como guardarraíl**, con la cautela de que hoy es early
  access: el diseño (umbral + exit code + brazo baseline) es *exactamente* el holdout ciego de COSMOS
  aplicado a pueblos y skills. Aunque el comando no esté disponible, **la forma se puede replicar hoy
  con `cosmos acertar`**, y el brazo baseline es la idea que COSMOS todavía no tiene.

### (sin número — medidor, no puerta) · `/skill-doctor` — medidor de coste y uso de skills 🔧 (medidor, no puerta)

- **URL**: https://code.claude.com/docs/en/skills.md#find-unused-skills (sección «Find unused
  skills»), con la fila del comando en https://code.claude.com/docs/en/commands.md
- **Qué hace**, literal de la doc: *«see what each of your skills costs and how often it gets used,
  so you can decide which ones to turn off»*. Cubre las skills de la sesión **salvo las bundled y las
  de empresa**; marca las **nunca invocadas** y dice dónde apagarlas; lista también plugins sin uso
  reciente. La doc recomienda empezar por las de mayor coste de contexto.
- **Informe**: interactivo → pestaña **Stats** del gestor `/plugin`; en `-p` → texto plano.
- **Requisitos**: Claude Code **v2.1.252+**. Por Remote Control responde
  `Skill usage reports are not available on this connection.`
- **No es un linter**: para estructura está `claude plugin validate <path>`; para comportamiento,
  `claude plugin eval`. Y es distinto de `/doctor` (chequeo de instalación).
- **Mecanismo o prosa**: 🔧 **mecanismo de medición, pero no es una puerta**: informa, no falla ni
  devuelve código de salida.
- **Coste en tokens**: el propio informe, una vez. No inyecta nada de forma continua.
- **Veredicto**: **catalogar como ficha**, y usarlo. Es el gemelo oficial del **medidor de tokens**
  de COSMOS, con un dato que COSMOS no tiene: **frecuencia real de invocación**. Una skill que cuesta
  800 tok/sesión y nunca se dispara es una fuga, y hoy COSMOS mide el coste pero no el uso.

### `/code-review` nativo y `ultra` — detalle verificado

- **URLs**: https://code.claude.com/docs/en/code-review.md · https://code.claude.com/docs/en/ultrareview.md
- **Firma literal**: `/code-review [low|medium|high|xhigh|max|ultra] [--fix] [--comment] [pr#|branch|path]`,
  alias `/review`. **Seis niveles de esfuerzo.** Si no se teclea nivel, **reutiliza el último
  `low`–`max` tecleado, incluso de una sesión anterior**; `ultra` ni usa ni actualiza ese recuerdo.
- Corre **local**, en segundo plano como subagente **con su propia ventana de contexto** (de ahí que
  el coste no caiga en el hilo principal). Lee `CLAUDE.md`; **no lee `REVIEW.md`**. Sus ediciones en
  segundo plano **no las deshace `/rewind`** — límite relevante si COSMOS lo recomienda.
- `--comment` publica hallazgos inline en un PR de GitHub, o una nota única en una MR de GitLab
  (v2.1.257+ y `glab`).
- **`ultra` (= `/ultrareview`), research preview**: corre **en la nube**, con una flota de revisores en
  sandbox y **verificación independiente de cada hallazgo**, 5–10 min. Límites 500 ficheros / 8.000
  líneas. Publica **un comentario plano** desde la cuenta de GitHub del usuario, nunca una review ni
  un approval; **`--no-post` es el valor por defecto**. En CI: `claude ultrareview [PR|base]` con
  `--json` y `--timeout` (default 45 min); exit `0` completada / `1` fallo o timeout / `130` Ctrl-C.
  **Ojo para COSMOS: exit 0 significa «la revisión terminó», no «no hay hallazgos»** — no sirve como
  gate tal cual.
- **Code Review gestionado (GitHub App)**, research preview solo Team/Enterprise: check run
  **Claude Code Review** con conclusión **siempre neutral, nunca bloquea**; se afina con `CLAUDE.md`
  y con **`REVIEW.md`** en la raíz (solo para review; **no expande imports `@`**). El gate hay que
  montárselo leyendo `bughunter-severity` del check run con `gh api`.
- **Veredicto**: **implementar la forma del filtro (M08) y catalogar el resto como ficha.** Lo
  reutilizable para COSMOS: el escalón de esfuerzo con coste creciente, y que **ningún revisor
  automático oficial bloquea por sí solo** — el gate lo pone quien lo consume.

### `/loop` nativo — detalle verificado

- **URL**: https://code.claude.com/docs/en/scheduled-tasks.md (sección «Run a prompt repeatedly with
  /loop»). Alias **`/proactive`**. Firma: `/loop [interval] [prompt]`.
- **Dos modalidades, ambas reales**: con intervalo (`/loop 5m ...` → se convierte a **cron**; `s/m/h/d`,
  redondeo al paso cron limpio) y **auto-marcada** (sin intervalo → Claude elige un retardo de entre
  **1 minuto y 1 hora** tras cada iteración e imprime el motivo).
- **Fichero**: `.claude/loop.md` (proyecto, con precedencia) o `~/.claude/loop.md`. Define **un único
  prompt por defecto**, no una lista; se **trunca por encima de 25.000 bytes**; se ignora si se pasa
  prompt en la línea. Sin `loop.md`, corre un prompt de mantenimiento integrado.
- **Parada**: `Esc` cancela el despertar pendiente; Claude puede terminarlo llamando a la herramienta
  **`ScheduleWakeup` con `stop: true`**; los de intervalo fijo expiran a los **7 días**.
- **Mecanismo o prosa**: 🔧 el planificador (cron + `ScheduleWakeup`); 📝 el `loop.md`.
- **Veredicto**: **descartar para calidad de sesión.** `/loop` repite en el tiempo; no verifica nada.
  Para «no cerrar sin verificar» el instrumento correcto es `/goal` o un Stop hook, no `/loop`.

---

## La referencia de hooks, verificada hoy (lo que cambia para COSMOS)

`https://code.claude.com/docs/en/hooks.md` — **33 eventos**, no los 5 que COSMOS usa:

`SessionStart`, `Setup`, `InstructionsLoaded`, `UserPromptSubmit`, `UserPromptExpansion`,
`MessageDisplay`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PostToolUseFailure`,
`PostToolBatch`, `PermissionDenied`, `Notification`, `SubagentStart`, `SubagentStop`, `TaskCreated`,
`TaskCompleted`, `Stop`, `StopFailure`, `TeammateIdle`, `ConfigChange`, `CwdChanged`,
`DirectoryAdded`, `FileChanged`, `WorktreeCreate`, `WorktreeRemove`, `PreCompact`, `PostCompact`,
`PreModelSwitch`, `PostModelSwitch`, `SessionEnd`, `Elicitation`, `ElicitationResult`.

**Cinco hechos que afectan directamente a los guardarraíles actuales de COSMOS:**

1. **`FileChanged` existe.** Matcher = nombres de fichero literales separados por `|` (no regex).
   Cierra el hueco que `verify-gate.sh` declara y que COSMOS documenta en G03/G05: un fichero
   reescrito **por Bash** no dispara `PostToolUse` matcher `Write|Edit`, pero sí `FileChanged`.
   La propia doc lo dice: *«To run a hook when a specific file changes on disk, whatever wrote it,
   use a FileChanged hook.»*
2. **La receta oficial para cobertura total de escrituras** (verbatim de la guía): *«If your hook must
   see every file change, such as for compliance scanning or audit logging, add a `Stop` hook that
   scans the working tree once per turn. For per-call coverage instead, also match `Bash|PowerShell`
   and have your script list modified and untracked files with `git status --porcelain`.»*
3. **`PreToolUse` admite cuatro decisiones**: `allow` / `deny` / `ask` / **`defer`**. COSMOS solo usa
   `deny` en G03; `ask` permite degradar una denegación a pregunta, que es el comportamiento correcto
   para la válvula caducable.
4. **`suppressOutput` se acepta pero no hace nada** (declarado en la tabla de salida JSON). Y los
   strings de salida **se capan a 10.000 caracteres** — relevante para el desvío de salidas grandes
   de G05. `updatedToolOutput` en `PostToolUse` queda confirmado como el campo correcto.
5. **`exit 2` NO bloquea en `PostToolUse`** (solo muestra el stderr a Claude) ni en
   `PermissionRequest` (ahí hay que usar `decision.behavior: "deny"`). Sí bloquea en `PreToolUse`,
   `UserPromptSubmit`, `UserPromptExpansion`, `Stop`, `SubagentStop`, `PreCompact`, `PostToolBatch`,
   `TaskCreated`, `TaskCompleted`, `ConfigChange`, `PreModelSwitch`. Y **`exit 2` gana siempre**:
   *«even a JSON `permissionDecision` of "allow" can't override it»*.
6. **Eventos nuevos con potencial de guardarraíl que COSMOS no usa**: `SubagentStop` (verificar lo que
   devuelve un subagente antes de aceptarlo — el punto exacto donde `verification-before-completion`
   dice «Trusting agent success reports»), `TaskCompleted`, `PostToolBatch` (bloquea tras una tanda
   de llamadas paralelas, antes de la siguiente llamada al modelo) y `PostCompact`.

---

## Área 5 — Memoria que mejora entre sesiones sin engordar el contexto

### La línea base es nativa, y ya tiene el mecanismo de tope

- **URL**: https://code.claude.com/docs/en/memory (sección «Auto memory»; verificada hoy)
- **Ubicación exacta**: `~/.claude/projects/<proyecto>/memory/`, con `MEMORY.md` de índice y **un
  fichero por tema**. El `<proyecto>` se deriva del repositorio git, así que **todos los worktrees
  comparten un único directorio de memoria**.
- **Tope, verbatim de la doc**: *«The first 200 lines of `MEMORY.md`, or the first 25KB, whichever
  comes first, are loaded at the start of every conversation.»* → **máximo ≈6.000 tokens/sesión**.
- **Y el tope es un mecanismo, no un consejo**: *«After Claude writes to `MEMORY.md`, Claude Code
  measures the file against the 200-line and 25KB read limits… If the file is over a limit, the write
  still succeeds, but Claude Code returns an error telling Claude to rewrite the index, because
  everything past the limit is dropped on the next load.»* **Falla solo.**
- **Los ficheros de tema NO se cargan al arrancar**: *«Claude Code doesn't load topic files such as
  `user_role.md` … at startup. Claude reads them on demand.»* Es decir, **progressive disclosure
  nativa aplicada a la memoria**, que es justo lo que COSMOS persigue con su jerarquía.
- **Aviso importante, verbatim**: *«The main conversation's auto memory isn't loaded into subagents»*
  — excepto en un `fork`. Un guardarraíl que dependa de la memoria automática **no protege a los
  subagentes**.
- **Veredicto**: **catalogar como la base, y no instalar nada que la duplique.** Cualquier gestor de
  memoria de terceros compite con esto; la pregunta correcta no es «¿qué instalo?» sino «¿qué aporta
  sobre 6.000 tokens topados y con error automático?».

### Tope duro de contexto en `SessionStart` — `affaan-m/ECC` 🔧

- **URL**: https://github.com/affaan-m/ECC · **MIT** · **256.347 ★** · **último push 2026-09-10**
  (verificado hoy con `gh api`)
- **Dónde vive**: `hooks/hooks.json` (42 KB, grafo de producción) más un contrato legible en
  `hooks/memory-persistence/hooks.json`; implementación en `scripts/hooks/session-start.js`. Eventos:
  `SessionStart`, `PreCompact`, `SessionEnd`, y `Pre`/`PostToolUse` en observación no bloqueante.
- **Mecanismo o prosa**: 🔧. Lo valioso es una constante:
  `DEFAULT_SESSION_START_CONTEXT_MAX_CHARS = 8000` (≈2.000 tokens), con **truncado con marcador
  explícito**, ajustable por `ECC_SESSION_START_MAX_CHARS` y desactivable con
  `ECC_SESSION_START_CONTEXT=off`.
- **Coste en tokens**: **2.000 tokens/sesión como tope duro**, medido en el código.
- **Veredicto**: **implementar el patrón, no el plugin.** ECC trae 20+ hooks que COSMOS no quiere.
  Lo que hay que copiar es `limitSessionStartContext()`: tope duro + marcador de truncado + salida por
  variable de entorno. COSMOS mide el contexto; esto **lo acota en el punto de inyección**.

### `coleam00/claude-memory-compiler` 🔧 pero inutilizable

- **URL**: https://github.com/coleam00/claude-memory-compiler · **SIN LICENCIA** (`license` = null,
  verificado) · **1.289 ★** · **último push 2026-04-06** (5 meses parado)
- **Dónde vive**: `.claude/settings.json` → `SessionStart` (15 s), `PreCompact` (10 s), `SessionEnd`
  (10 s), todos `uv run python hooks/*.py`. `hooks/session-start.py` devuelve
  `hookSpecificOutput.additionalContext` = fecha + `knowledge/index.md` completo + últimas 30 líneas
  del log diario.
- **Coste en tokens**: `MAX_CONTEXT_CHARS = 20_000` ≈ **5.000 tokens**, truncado con `...(truncated)`.
- **Veredicto**: **catalogar como ficha.** El diseño (índice compilado + log diario + tres hooks de
  ~5 KB, sin servidor) es el más legible que hay, pero **sin licencia no se puede reutilizar código**
  y lleva cinco meses sin tocar.

### `thedotmack/claude-mem` — el más popular, y el que hay que descartar

- **URL**: https://github.com/thedotmack/claude-mem · **Apache-2.0** · **93.679 ★** ·
  **último push 2026-09-11** (hoy; verificado)
- **Dónde vive**: `plugin/hooks/hooks.json` (12 KB), seis eventos: `Setup`, `SessionStart` (matcher
  `startup|resume|clear|compact`), `UserPromptSubmit`, `PostToolUse` (`async`), `PreToolUse` (matcher
  `Read`, `async`) y `Stop` (`async`). Cada comando llama a
  `node scripts/bun-runner.js scripts/worker-service.cjs hook claude-code <…>`, que **levanta un
  worker HTTP persistente más ChromaDB**; el contexto sale de `GET /api/context/inject`.
- **Coste en tokens**: **no hay tope de caracteres en el hook.** Los defaults
  (`CLAUDE_MEM_CONTEXT_OBSERVATIONS='50'`, `CLAUDE_MEM_CONTEXT_SESSION_COUNT='10'`) dan del orden de
  **3.000–6.000 tokens/sesión estimados** — no medidos con exactitud porque el texto lo genera el
  worker en tiempo de ejecución.
- **Veredicto**: **descartar.** Un proceso residente más una base vectorial más telemetría de plan y
  prueba, para acabar en el mismo orden de tokens que la memoria nativa **que sí trae tope duro**.
  Añádase que el README promociona un token de criptomoneda («CMEM»): eso no es un criterio técnico,
  pero sí un aviso sobre los incentivos del proyecto.

### `EveryInc` — los «compound docs» son prosa

- Ya tratado en M11. El dato concreto que faltaba: **el plugin no instala ningún hook** (los únicos
  `hooks.json` del árbol están en `tests/fixtures/`). El mecanismo real es
  `skills/ce-compound/SKILL.md`, **una skill invocada a mano** (`/ce-compound`) que escribe un
  documento bajo `<root>/solutions/` (`docs/` por defecto, configurable con `docs_root` en
  `.compound-engineering/config.yaml`) más `CONCEPTS.md`. **No inyecta nada en contexto por sí sola.**
- Lo que sí merece copiarse como idea para las fichas de COSMOS: la **barra de durabilidad
  contrafactual** — antes de escribir una lección, preguntarse «¿se habría repetido este error sin
  esta nota?». Pero la evalúa el propio modelo, así que es 📝.
- **Veredicto**: **catalogar como ficha.**

### Recordatorio post-compactación — `Dicklesworthstone/post_compact_reminder` 🔧

- **URL**: https://github.com/Dicklesworthstone/post_compact_reminder · **NOASSERTION** (el README
  dice «MIT with OpenAI/Anthropic Rider»: **no es MIT puro**, hay que leerla antes de copiar) ·
  **54 ★** · **último push 2026-08-31** (verificado hoy)
- **Dónde vive**: `install-post-compact-reminder.sh` escribe en `settings.json` un hook `SessionStart`
  con **`"matcher": "compact"`**, y además el guion vuelve a comprobar `.source == "compact"`.
- **Qué inyecta**: cuatro líneas fijas («Context was just compacted. STOP. You MUST: 1. Read AGENTS.md
  NOW; 2. Confirm…»): **≈40 tokens, y solo tras una compactación.**
- **Veredicto**: **implementar el patrón** (15 líneas de bash, coste ≈0). Ataca el fallo que la
  doctrina de COSMOS nombra explícitamente —el modelo olvida las reglas en el turno 40— justo en el
  momento en que ocurre. Y **encaja con G04**: COSMOS ya borra las marcas de lectura en `PreCompact`;
  esto es la otra mitad, recordar en `SessionStart(compact)` qué hay que releer.

---

## Área 6 — Guardarraíles de calidad de código por hook

### M14 · `protect-tests` — contra el «verde falso» 🔧

- **URL**: https://github.com/karanb192/claude-code-hooks · **MIT** · **509 ★** ·
  **último push 2026-09-08** (verificado hoy). 21 plugins, marketplace instalable, 1.570 tests propios.
- **Dónde vive**: `plugins/protect-tests/hooks/hooks.json` (leído literalmente):
  ```json
  { "hooks": { "PreToolUse": [ { "matcher": "Bash|Edit|MultiEdit|Write",
      "hooks": [ { "type": "command", "command": "node \"${CLAUDE_PLUGIN_ROOT}/protect-tests.js\"" } ] } ] } }
  ```
  **Nótese que el matcher incluye `Bash`**: cubre el `rm` por shell, no solo el `Edit`.
- **Qué comprueba**: las tres formas de poner la suite en verde sin arreglar nada — borrar el test
  (`rm`, `git rm`), renombrarlo a `.disabled`/`.bak`/`.skip`, o meterle un marcador de salto
  (`@pytest.mark.skip`, `@Disabled`, `it.skip`, `t.Skip`, `#[ignore]`, `xit`…). **No** bloquea escribir
  tests nuevos ni refactorizarlos.
- **Cómo bloquea**: `hookSpecificOutput.permissionDecision: 'deny'` + `permissionDecisionReason` de
  una línea.
- **Coste en tokens**: **≈30 tokens, y solo cuando bloquea.** Cero en el camino feliz.
- **Evidencia**: el README publica un banco propio (`bench/run.mjs`, proceso Node fresco por
  invocación): mediana **34–38 ms** por hook de guarda en Apple M3 Pro / Node v26; `format-code`
  114 ms. **Es evidencia de coste, no de efecto**: no hay medición de «mejora la calidad de la
  salida». Reproducible con `node bench/run.mjs`.
- **Veredicto**: **implementar en COSMOS como guardarraíl.** Es el único mecanismo público que he
  encontrado contra el fallo «el agente hace pasar la suite desactivando tests», que es exactamente
  la autocertificación que G03 persigue, un nivel más abajo.

### M15 · Typecheck por lotes al cerrar — `ECC stop:format-typecheck` 🔧

- **URL**: https://github.com/affaan-m/ECC · MIT · 256.347 ★ · último push 2026-09-10 (verificado hoy)
- **Dónde vive**: `hooks/hooks.json`, evento **`Stop`, matcher `.*`** (el 2.º de seis hooks `Stop`),
  lanzando `scripts/hooks/run-with-flags.js stop:format-typecheck scripts/hooks/stop-format-typecheck.js standard,strict`.
- **Cómo funciona, y por qué es el diseño correcto**: un acumulador registra los ficheros editados
  durante la respuesta; al parar, **los agrupa por `tsconfig.json` y corre un solo
  `npx tsc --noEmit --pretty false` por tsconfig**, no uno por fichero. El acumulador se vacía al
  leerlo. Reparte un presupuesto de tiempo entre lotes para no reventar el límite del hook `Stop`.
- **Cómo bloquea**: stderr + código de salida ≠ 0, que en `Stop` obliga a Claude a seguir trabajando.
  El formateador, en cambio, es **explícitamente no bloqueante** si la herramienta no está instalada.
- **Coste en tokens**: **recorte duro a 10 líneas de error por fichero editado** (`.slice(0, 10)`),
  filtradas para dejar solo las que mencionan ese fichero: **≈100–300 tokens en el peor caso, 0 cuando
  pasa**.
- **Veredicto**: **implementar en COSMOS como guardarraíl.** Resuelve el problema real del
  «lint en cada edición»: hacerlo por edición cuesta latencia en cada turno y llena el contexto de
  ruido; hacerlo **una vez al cerrar, por lotes y con el error recortado**, cuesta casi nada.

### `format-code` — la forma correcta de formatear (coste cero) 🔧

- **URL**: https://github.com/karanb192/claude-code-hooks (mismo repo, MIT, 509 ★, 2026-09-08)
- **Dónde vive**: `plugins/format-code/hooks/hooks.json`, `PostToolUse` matcher `Write|Edit` →
  `node "${CLAUDE_PLUGIN_ROOT}/format-code.js"` (verificado literalmente). Ruff `--fix --exit-zero`
  para Python, prettier para MD/YAML/JSON.
- **Coste en tokens**: **0.** Siempre imprime `{}` y registra en `~/.claude/hooks-logs/`; **nunca
  devuelve el diff al modelo**. Ese es el detalle que lo hace bueno: un formateador que cuenta lo que
  hizo es una fuga de contexto en cada edición.
- **Veredicto**: **implementar como guardarraíl**, es trivial y su coste es exactamente cero.
  Compárese con el ejemplo de la doc oficial
  (`jq -r '.tool_input.file_path' | xargs npx prettier --write`), que es el mismo patrón en una línea.

### `disler/claude-code-hooks-mastery` — la trampa, y el hallazgo

- **URL**: https://github.com/disler/claude-code-hooks-mastery · **SIN LICENCIA** · **3.916 ★** ·
  **último push 2026-03-04** (verificado hoy)
- **La trampa**: su `.claude/settings.json` declara los 14 eventos, pero
  `.claude/hooks/post_tool_use.py` **solo escribe un JSON de log: no hace lint, ni typecheck, ni
  nada**. Es el antipatrón A1 de `research/PATRONES-HARNESS.md` otra vez: un enganche que anuncia
  vigilancia y no vigila.
- **El hallazgo, que sí vale**: los validadores reales
  (`.claude/hooks/validators/ruff_validator.py`, `ty_validator.py`) **no están en `settings.json`**;
  están cableados en el **frontmatter YAML del subagente** `.claude/agents/team/builder.md`:
  ```yaml
  hooks:
    PostToolUse:
      - matcher: "Write|Edit"
        hooks: [ruff_validator.py, ty_validator.py]
  ```
  **Se pueden colgar hooks de un subagente concreto** en lugar de globalmente. Para COSMOS eso es
  directamente aplicable: exigir el typecheck solo al subagente que escribe código, sin gravar a los
  que solo leen.
- **Cómo bloquea**: `{"decision": "block", "reason": "Lint check failed:\n" + salida[:500]}` — recorte
  a 500 caracteres ≈125 tokens. El `pre_tool_use.py` usa la otra vía: `sys.exit(2)` con stderr.
- **Veredicto**: **catalogar como ficha** el patrón de hooks por subagente; **descartar el código**
  (sin licencia, y el hook global que anuncia no hace nada).

### Descartados, verificados

- **`Digital-Process-Tools/claude-remember`** — 168 ★, push 2026-09-11, licencia **NOASSERTION**
  («Community License» que prohíbe redistribución comercial y «uso competidor»: COSMOS podría caer
  ahí). Además `memory_inject_max_bytes: 200000` ≈ **50.000 tokens**, que no es un presupuesto sino un
  cortafuegos anti-cuelgue. **Descartar.**
- **`ryanlewis/claude-format-hook`** — 4 ★, último push **2025-08-14**. Muerto y superado. **Descartar.**
- **`gotalab/cc-sdd`** — ya tratado en el área 2, sin número. **Descartar.**

### ⚠️ Aviso que condiciona TODO el área 6 (verificado hoy en `anthropics/claude-code`)

| Issue | Título | Estado | Cerrado |
|---|---|---|---|
| **#18312** | `[Bug] PreToolUse hook permissionDecision ignored when tool in allow list` | closed, `duplicate` | 2026-01-19 |
| **#37210** | `PreToolUse hook permissionDecision: "deny" ignored for Edit tool — tool executes despite deny` | closed, `not_planned` | 2026-03-21 |
| **#40117** | `Agent bypasses git pre-commit hooks using --no-verify, stash, and quiet flags despite explicit deny rules` | closed, `not_planned` | 2026-05-07 |

**Consecuencia práctica para COSMOS, y es seria**: un guardarraíl de commit **no puede apoyarse solo
en `permissions.deny` ni en el pre-commit de git**. G03 ya deniega por `PreToolUse`, pero si
`Bash(git commit:*)` acaba en la *allowlist* de `settings.json`, **el `deny` puede no aplicarse**
(#18312). Y el agente tiene tres salidas documentadas del pre-commit: `--no-verify`, `git stash` y
flags silenciosos (#40117). El gate de pre-commit de COSMOS necesita un `PreToolUse` que **parsee la
orden completa y detecte `--no-verify` en cualquier posición** — COSMOS ya tiene el lector de órdenes
de shell de G03, así que es una extensión de algo que existe, no una pieza nueva.

---

## Área 7 — Lo que Anthropic recomienda oficialmente hoy

Dos artículos y un repo, todos verificados:

1. **«Effective harnesses for long-running agents»** (nov-2025) —
   https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
   - Agente **inicializador** que prepara el entorno en la primera pasada: escribe un `init.sh`, un
     `claude-progress.txt` y **un JSON estructurado con la lista de funcionalidades de extremo a
     extremo**, cada una con un campo `"passes": false`.
   - Verbatim: *«We prompt coding agents to edit this file only by changing the status of a `passes`
     field, and we use strongly-worded instructions like "It is unacceptable to remove or edit tests
     because this could lead to missing or buggy functionality."»*
   - El modo de fallo que nombran: *«Claude's tendency to mark a feature as complete without proper
     testing.»*
   - **Sin cifras**: el artículo no publica porcentajes ni comparaciones antes/después.
2. **«Harness design for long-running application development»** (**publicado 2026-03-24**) —
   https://www.anthropic.com/engineering/harness-design-long-running-apps
   - Arquitectura **inspirada en GAN**: planificador, generador y evaluador. El evaluador con
     Playwright MCP *«clicked through the running application the way a user would, testing UI
     features, API endpoints, and database states»*, con umbrales duros.
   - **Reinicios de contexto con traspaso estructurado**: *«a structured handoff that carries the
     previous agent's state and the next steps»*.
   - **Y la conclusión que más importa para COSMOS**: con Opus 4.6 *«removed the sprint construct
     entirely»* y el arnés corrió *«coherently for over two hours without the sprint decomposition»*.
     Es decir, **parte del arnés dejó de hacer falta al mejorar el modelo**. De ahí el patrón
     «Re-simplify on model upgrades»: tras cada versión, comentar piezas del arnés una a una y ver
     cuál sigue sosteniendo algo.
   - **Cifras publicadas** (las únicas, y son de coste y duración, no de calidad medida):
     Retro Game Maker con arnés mínimo **20 min / $9** frente a arnés completo **6 h / $200**
     (*«over 20x more expensive»*); un DAW en **3 h 50 min / $124,70** (fase de construcción sola:
     2 h 7 min / $71,08); diseño frontend, **«5 to 15 iterations per generation»** y ejecuciones de
     hasta cuatro horas.
3. **`anthropics/cwc-long-running-agents`** — los ficheros, ya desmenuzados en la sección 0.

**Lo que Anthropic NO publica y conviene decir en voz alta**: ninguna de las dos entradas de ingeniería
trae un benchmark A/B de calidad con y sin arnés. **Toda la evidencia pública de esta área es
anecdótica o de coste.** Quien diga que un Stop hook «mejora la calidad un X%» no lo ha sacado de
Anthropic.

---

## Los 5 guardarraíles de calidad que COSMOS no tiene y debería tener

> Los cinco son mecanismos: fallan solos. Ninguno depende de que el modelo recuerde nada.
> Ninguno inyecta tokens en el camino feliz.

### 1 · G06 — Contrato de veredicto por defecto en rojo, desbloqueado solo con evidencia

- **Evento**: `PreToolUse` matcher `Write|Edit|MultiEdit` **+ `FileChanged`** sobre el fichero de
  veredicto (`FileChanged` cierra el hueco de la reescritura por Bash, que el propio Anthropic declara
  sin tapar).
- **Qué comprueba**: que no se marque ningún criterio como `passes: true` sin que en **esta sesión**
  se haya leído una salida de ejecución fresca. Reutiliza la marca de G04 (sesión + SHA-256), que es
  estrictamente más fuerte que el `.evidence-reads` de Anthropic; y **consume la evidencia** tras cada
  cambio, así que el siguiente criterio exige una prueba nueva.
- **Cómo falla solo**: `permissionDecision: "deny"` con el motivo; la herramienta no llega a
  ejecutarse. En `FileChanged` no hay control de decisión, así que ahí el mecanismo es **invalidar el
  veredicto** (reescribirlo a rojo) y anotarlo, no denegar.
- **Cuánto cuesta**: ~45 tokens al bloquear, **0 cuando pasa**.
- **Qué repo lo demuestra**: `anthropics/cwc-long-running-agents`,
  `claude-code-config/.claude/hooks/verify-gate.sh` + `track-read.sh` (Apache-2.0, 676 ★, 2026-05-13).
  Es el «default-FAIL contract», el primero de los tres primitivos que Anthropic nombra.
- **Por qué COSMOS lo necesita**: G02 bloquea el cierre con **el árbol de ficheros** en rojo. Nada
  impide hoy que el agente declare **funcionalmente** hecho lo que no ha comprobado. Ese es
  literalmente el modo de fallo que Anthropic dice haber observado.

### 2 · G07 — Stop hook que EJECUTA la verificación, no que la consulta

- **Evento**: `Stop`, con un hook `type: "agent"` (o un `type: "command"` que lance
  `claude --agent evaluator -p`).
- **Qué comprueba**: corre de verdad `cosmos validar` y las dos suites **en el momento del cierre**,
  y compara la salida con lo que la sesión afirma. El ejemplo literal de la doc oficial es
  `"prompt": "Verify that all unit tests pass. Run the test suite and check the results. $ARGUMENTS"`.
- **Cómo falla solo**: `{"ok": false, "reason": …}` realimenta el motivo y Claude sigue trabajando;
  `"impossible": true` es la salida honesta cuando la condición no se puede satisfacer. Tope de
  bloqueos del runtime: **8** (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`); el de COSMOS es 3 y muerde antes.
- **Cuánto cuesta**: **0 en el contexto principal** cuando pasa; el subagente corre en su propia
  ventana (60 s por defecto, hasta 50 turnos de herramienta). Solo vuelve el `reason`.
- **Qué repo lo demuestra**: la propia doc (https://code.claude.com/docs/en/hooks-guide#agent-based-hooks),
  `anthropics/claude-plugins-official` → `plugins/hookify/hooks/hooks.json` (Apache-2.0, 36.141 ★,
  push de hoy) y `plugins/ralph-loop/hooks/stop-hook.sh`.
- **Advertencia honesta**: los hooks `agent` están **marcados como experimentales** por la propia
  doc, que recomienda `command` para producción. La versión de COSMOS debería ser un `command` que
  ejecute y parsee, y dejar el `agent` como opción.

### 3 · G08 — Revisor adversarial de contexto fresco, sin herramientas de escritura

- **Evento**: `SubagentStop`, o un guion que lo lance entre iteraciones.
- **Qué comprueba**: un subagente que **no vio construir nada** lee el diff y la evidencia y devuelve
  `PASS` o `NEEDS_WORK` en la primera línea, para que un guion pueda leer el veredicto. Es la
  «premisa invertida» de COSMOS, automatizada.
- **Cómo falla solo**: **por aislamiento de herramientas**, que es lo que lo hace mecánico y no
  retórico: `tools: Read, Glob, Grep` **sin `Write` ni `Edit`**, así que no puede arreglar lo que
  critica ni certificarse a sí mismo. En `SubagentStop` se bloquea con `decision: "block"`.
  Añádase el filtro de confianza del `/code-review` oficial: **cada hallazgo puntuado 0-100 por un
  juez separado, y por debajo de 80 no se emite** — eso es lo que evita ahogar la sesión en ruido.
- **Cuánto cuesta**: **0 en el hilo principal**; es otro proceso. Cuesta dinero de API.
- **Qué repo lo demuestra**: `anthropics/cwc-long-running-agents` →
  `claude-code-config/.claude/agents/evaluator.md` (el «fresh-context evaluator»), y
  `anthropics/claude-plugins-official` → `plugins/code-review/commands/code-review.md` para la rúbrica
  de confianza y su lista explícita de falsos positivos.
- **Por qué COSMOS lo necesita**: hoy la premisa invertida la ejecutan personas (Codex escribe, Claude
  revisa). Eso no escala a una sesión de siete horas, y `verification-before-completion` nombra
  «Trusting agent success reports» como una de sus banderas rojas.

### 4 · G09 — Protección de los tests contra el «verde falso»

- **Evento**: `PreToolUse` matcher **`Bash|Edit|MultiEdit|Write`** (el `Bash` es imprescindible: el
  borrado llega por shell).
- **Qué comprueba**: que no se borre un test (`rm`, `git rm`), no se renombre a
  `.disabled`/`.bak`/`.skip`, y no se le meta un marcador de salto (`@pytest.mark.skip`, `it.skip`,
  `#[ignore]`, `xit`…). Escribir tests nuevos y refactorizarlos sigue permitido.
- **Cómo falla solo**: `hookSpecificOutput.permissionDecision: "deny"` con un motivo de una línea.
  **Ojo al aviso del área 6**: si `Bash(git commit:*)` o los editores están en la *allowlist*, el
  `deny` puede ignorarse (issue #18312, cerrada como duplicada el 2026-01-19), así que el guardarraíl
  tiene que ir acompañado de una revisión de `permissions.allow`.
- **Cuánto cuesta**: **≈30 tokens al bloquear, 0 en el camino feliz.** Latencia medida por el repo:
  **34–38 ms** de mediana por invocación.
- **Qué repo lo demuestra**: `karanb192/claude-code-hooks` →
  `plugins/protect-tests/hooks/hooks.json` + `protect-tests.js` (MIT, 509 ★, push 2026-09-08), con
  1.570 tests propios y un banco reproducible en `bench/run.mjs`.
- **Por qué COSMOS lo necesita**: G03 impide reescribir a mano el **veredicto**; nada impide hoy
  llegar al verde **borrando la prueba**. Es la misma autocertificación un piso más abajo, y es el
  camino que un agente cansado encuentra solo.

### 5 · G10 — Typecheck y formato por lotes al cerrar, con el error recortado

- **Evento**: `Stop` (el typecheck, bloqueante) y `PostToolUse` matcher `Write|Edit` (el formato, en
  silencio).
- **Qué comprueba**: acumula los ficheros editados durante la respuesta; al cerrar, **los agrupa y
  lanza una sola pasada de typecheck por proyecto**, no una por fichero. El formateador corre en cada
  edición pero **devuelve `{}` siempre**: nunca cuenta al modelo lo que hizo.
- **Cómo falla solo**: código de salida ≠ 0 + stderr en `Stop` obliga a seguir trabajando. El
  formateador es explícitamente **no bloqueante** si la herramienta no está instalada — un hook que
  rompe la sesión porque falta `prettier` se desinstala el mismo día.
- **Cuánto cuesta**: **≈100–300 tokens en el peor caso** gracias al recorte duro a 10 líneas de error
  por fichero; **0 cuando pasa** y **0 siempre** en el formateador.
- **Qué repo lo demuestra**: `affaan-m/ECC` → `hooks/hooks.json`, evento `Stop`,
  `scripts/hooks/stop-format-typecheck.js` (MIT, 256.347 ★, push 2026-09-10) para el typecheck por
  lotes; `karanb192/claude-code-hooks` → `plugins/format-code/` (MIT) para el formateo de coste cero.
  El ejemplo de una línea está también en la doc oficial
  (`jq -r '.tool_input.file_path' | xargs npx prettier --write`).
- **Por qué COSMOS lo necesita**: es el único de los cinco que mejora el **código**, no el veredicto
  sobre el código. Y el diseño importa tanto como la idea: hacerlo por edición llena el contexto de
  ruido en cada turno; hacerlo por lotes al cerrar no cuesta casi nada.

---

## Cierre: tres avisos para quien implemente esto

1. **Ninguna de las fuentes publica una mejora de calidad medida.** Ni Anthropic, ni superpowers
   (285.217 ★), ni compound-engineering, ni spec-kit. Las únicas cifras públicas son de **coste y
   latencia** (`$9` vs `$200`; 34–38 ms por hook). Si COSMOS quiere saber si estos guardarraíles
   mejoran algo, **tiene que medirlo él**, con el holdout ciego que ya sabe construir. Esa es, de
   hecho, la aportación diferencial: nadie más lo está midiendo.
2. **El arnés caduca con el modelo.** Anthropic lo dice de su propio arnés: con Opus 4.6 quitaron el
   constructo de sprints entero y el sistema corrió mejor. El patrón «Re-simplify on model upgrades»
   debería entrar en `spec/GUARDARRAILES.md` como obligación: tras cada versión, comentar cada
   guardarraíl uno a uno y comprobar cuál sigue sosteniendo algo.
3. **Cuidado con lo que se instala por popularidad.** `obra/superpowers` tiene 285.217 estrellas y
   **un solo hook**, de `SessionStart`, que inyecta ~780 tokens fijos; `thedotmack/claude-mem` tiene
   93.679 y levanta un worker con base vectorial para igualar lo que la memoria nativa ya da con tope
   duro. Las estrellas miden adopción, no mecanismo — y COSMOS ya aprendió esa lección cara en
   `research/PATRONES-HARNESS.md`.
