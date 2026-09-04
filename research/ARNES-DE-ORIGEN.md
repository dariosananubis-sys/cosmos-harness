# Auditoría técnica — el arnés de origen (`<harness-de-referencia>`) para fusión con COSMOS

Fecha: 2026-09-01. Clon auditado: `<organización>/<arnés-de-origen>`, commit en el HEAD del
clon en el momento de esta auditoría (repo limpio, `git status --porcelain` vacío antes de tocar
nada). Todo lo ejecutado fue de solo lectura salvo `python3 scripts/bootstrap.py`, corrido una vez
dentro del propio clon (autorizado explícitamente por el encargo) para medir cuánto de la auditoría
inicial era "falta arrancar" y no "roto".

---

## Resumen ejecutivo

- **11 scripts** en `scripts/` (el encargo decía 12; no existe un duodécimo — ver tabla). Los 11
  funcionan hoy: 100% de los comandos de solo lectura ejecutados (`--check`, `list`, `search`,
  `--list`) devolvieron 0.
- Los **114 tests** fallaban 3 (2 failures + 1 error) **antes** de `bootstrap.py` y pasan **114/114
  en verde** después. Los **87 problemas del auditor** bajan a **0** después del mismo bootstrap.
  **No hay ningún bug real medido en este repo**: todo lo "roto" era el primer arranque sin hacer,
  no una regresión.
- El mecanismo más valioso para COSMOS es `scripts/project.py`: proyecta packs a un repo externo
  con backup atómico por skill, detección de colisión con skills ajenas, y fusión no destructiva de
  `AGENTS.md`/`CLAUDE.md`/`.claude/settings.json`. Es la pieza que le falta a COSMOS hoy —
  `cosmos/compilar.py` solo compila el árbol sobre sí mismo, nunca sobre un repo ajeno.
- Recomendación (detalle en `## Qué hacemos`): **(b) COSMOS se construye encima**, adoptando el
  mecanismo de proyección externa de `project.py` como capa nueva y dejando su propia taxonomía de
  11 niveles como el sistema de organización — no absorber `packs/` como reemplazo de la taxonomía.

---

## Qué hay

Inventario de los 11 scripts de `scripts/` (no 12 — recuento exacto de `ls scripts/*.py`: 11
ficheros). Cada fila ejecutada con su comando de solo lectura real, salida pegada.

| Script | Líneas | Qué hace exactamente | Funciona hoy |
|---|---|---|---|
| `redaction.py` | 13 | Una función, `path_label(path)`: SHA-256 de la ruta, primeros 12 hex, prefijo `ruta#`. La usan `audit_harness`, `doctor` y `secret_scan` para no filtrar nombres de fichero/cliente en sus diagnósticos. | Sí (importado y usado por los otros; sin CLI propia que probar). |
| `bootstrap.py` | 130 | Arranque de una clonación: `validate_skills.py` → `compile_context.py` (escribe) → instala pre-commit local si no hay uno ajeno ya gestionado → `compile_context.py --check`. | Sí. Ejecutado: `skill_validation: 56 skills correctas` / `contexto generado: 91 archivos, packs=wordpress,web-quality` / `bootstrap: correcto · pre-commit=instalado`. |
| `doctor.py` | 142 | Diagnóstico informativo (Python, plataforma, CPU, RAM total, disco libre, si el contexto generado coincide con las fuentes, estado Git, remoto **redactado** por `redact_git_remote`). `--check` falla solo si falta el repo Git, el contexto no está generado, o el modo de recursos no es `native` — **nunca por RAM/disco/concurrencia**, por diseño. | Sí. `python3 scripts/doctor.py --check` → exit 0, `context_generated: True`, `resource_limits_enforced: False`. |
| `audit_harness.py` | 578 | El auditor de estructura: recorre ficheros "activos" (todo menos `.agents/skills`, `.claude/skills`, `.runtime`, `artifacts`, `harness/generated`, `workspaces`), busca patrones de interacción/bucle residente prohibidos, nombres de componentes retirados sin revelarlos (usa `REMOVED_PATTERNS` + `path_label`), topes de máquina hardcodeados (`MACHINE_LIMIT_PATTERNS`), valida `.claude/settings.json`/`.mcp.json` contra un esquema soportado, y llama a `secret_scan.scan()`. | Sí. `python3 scripts/audit_harness.py` tras bootstrap → `auditoría: limpia`. |
| `compile_context.py` | 616 | El compilador central — ver mecanismo detallado abajo. `--list`, `--check`, `--check-staged` son de solo lectura. | Sí. `--list` → `packs: wordpress, web-quality` + 15 skills activas. |
| `pack.py` | 217 | Activa/desactiva packs en `harness.local.toml` (edición de TOML preservando el resto del fichero línea a línea, sin librería de escritura TOML) y busca packs por intención (`search`, BM25 simplificado con alias en `PACK_ALIASES`). `list`/`search` son de solo lectura. | Sí. `list` → 2 activos (`web-quality`, `wordpress`) de 10 disponibles. `search "seguridad secretos"` → rankea `security` y `wordpress-operations` con las skills que matchean. |
| `precommit.py` | 131 | El hook real: aísla el entorno Git (`GIT_*` fuera salvo `GIT_INDEX_FILE` cuando aplica), corre `secret_scan.py --staged` y `--all`, `compile_context.py --check-staged`, y `verify_staged_snapshot()` — exporta el índice Git a un directorio temporal con `git checkout-index`, reinicializa un repo Git aislado ahí dentro y corre `validate_skills.py` + `compile_context.py` + `audit_harness.py` + los tests **sobre esa instantánea**, nunca sobre el worktree sucio. | No ejecutado como hook (mutaría estado); código leído completo. Su lógica de aislamiento de entorno Git se ejercita indirectamente por `tests/test_security_boundaries.py::PrecommitBoundaryTests` (3 tests, en verde). |
| `project.py` | 511 | Proyecta packs a un repo Git externo — el mecanismo más importante para COSMOS. Ver detalle abajo. `check` es de solo lectura. | No probado en vivo contra un repo externo (habría escrito fuera de `vh-ref`, prohibido por el encargo); su contrato está cubierto por `tests/test_project_bridge.py` (7 tests, en verde) y se leyó el código fuente completo. |
| `redaction.py` | (ya listado) | — | — |
| `retrieve_memory.py` | 216 | BM25 ligero sobre `memory/index.json`: pesos por campo (`title`/`aliases` 6, `tags` 4, `summary`/`kind`/`source`/`path`/`body` 1-2), expansión de un salto por relaciones (`related`/`supersedes`), y **nunca devuelve el cuerpo completo de una entrada** — solo título+resumen+ruta, acotado a un presupuesto de bytes (`--max-bytes`, por defecto 4000). | Sí — no tiene modo `--check`, pero su contrato entero está cubierto por `tests/test_memory_retrieval.py` (7 tests, en verde) y `memory/entries/` tiene 3 entradas genéricas reales que se pueden indexar. |
| `secret_scan.py` | 361 | Escáner de secretos y PII sobre blobs del índice Git (nunca el worktree sin commitear, salvo `--staged`) — ver patrones abajo. `--all`/`--staged` son de solo lectura (leen, no escriben). | Sí. `python3 scripts/secret_scan.py --all` → `secret_scan: limpio`. |
| `validate_skills.py` | 368 | Valida el subconjunto portable de Agent Skills (frontmatter YAML-lite de una sola línea por campo, sin librería YAML) sobre **todas** las skills fuente — núcleo y **todos los packs, incluidos los desactivados** — más duplicados de nombre, symlinks prohibidos y TODOs sin cerrar. | Sí. `python3 scripts/validate_skills.py` → `skill_validation: 56 skills correctas`. |

Total scripts: **3.283 líneas** en `scripts/`. Tests: **3.339 líneas** en `tests/` (7 ficheros; el
mayor, `test_deployment_capabilities.py`, 1.252 líneas). Cero dependencias externas: `pyproject.toml`
solo fija `requires-python = ">=3.11"` (usa `tomllib` de la stdlib), sin ninguna librería de
terceros.

---

## Qué está roto

### Antes de `bootstrap.py`

**3 tests (1 error + 2 failures), los tres con la misma causa raíz:**

```
ERROR: test_manifest_hashes_every_generated_artifact
  FileNotFoundError: harness/generated/context-manifest.json (no existe)

FAIL: test_full_audit_is_clean
  AssertionError: [] != ['falta .agents/skills/.generated-by-arnes-de-origen', ...87 elementos]

FAIL: test_generated_tree_matches_sources
  AssertionError: [] != ['falta .agents/skills/.generated-by-arnes-de-origen', ...87 elementos]
```

**87 problemas del auditor** (`python3 scripts/audit_harness.py`), todos `ERROR: falta <ruta>`, y se
agrupan en exactamente 3 causas — no 87 causas distintas:

| Causa | Cuántos | Se arregla con |
|---|---|---|
| Falta `.claude/skills/*` (43 rutas: marcador + 15 skills × sus ficheros) | 43 | `bootstrap.py` / `compile_context.py` |
| Falta `.agents/skills/*` (mismas 43 rutas, para Codex) | 43 | idem |
| Falta `harness/generated/context-manifest.json` | 1 | idem |
| **Total** | **87** | |

Verificado en vivo: antes de `bootstrap.py`, `ls .claude/` solo contenía `settings.json` (ni
`skills/` ni nada más) y `harness/generated/` no existía. Es decir: **el clon nunca había ejecutado
su propio arranque**. No es una regresión ni un bug del repo — es literalmente el primer paso que
`README.md` pide como paso 1 (`python3 scripts/bootstrap.py`) y que nadie había corrido en esta
copia.

### Después de `bootstrap.py`

```
$ python3 scripts/bootstrap.py
skill_validation: 56 skills correctas
contexto generado: 91 archivos, packs=wordpress,web-quality
contexto generado: correcto
bootstrap: correcto · pre-commit=instalado

$ python3 scripts/audit_harness.py
contexto fijo: Codex ~1352 tok · Claude ~1419 tok · 15 skills · hooks config 0 B · plugins 0 · MCP 0 · auto-memory 0 · git-context 0 · notificaciones 0
auditoría: limpia

$ python3 -m unittest discover -s tests -v
Ran 114 tests in 47.303s
OK
```

**Conclusión sin ambigüedad: 0 problemas roto-de-verdad, 90 (87 auditor + 3 tests, mismo origen)
eran "falta un paso de arranque".** El pre-commit se instaló porque no había ninguno gestionado
antes (comportamiento correcto y documentado: si hubiera un hook ajeno, `install_precommit()` lo
respeta y devuelve `"omitido (hook ajeno)"` — leído en el código, `scripts/bootstrap.py:41-107`).

---

## Solape

| Capacidad | el arnés de origen | COSMOS | Quién gana y por qué |
|---|---|---|---|
| **Agrupación cargable bajo demanda** | `packs/` — 10 paquetes **planos** (wordpress, web-quality, seo, security…), cada uno con su carpeta `skills/` propia. Activar un pack es una línea en `harness.local.toml`. | Taxonomía de 11 niveles (universo→galaxia→...→casa) con reglas de carga distintas por nivel (siempre / al declarar dominio / al tocar path / al invocar). | **COSMOS**, y no por poco: un pack es una lista plana de skills sin relación entre sí; la taxonomía expresa *cuándo* entra cada nivel con una regla propia (galaxia siempre, país al descender, casa nunca sola). Pero **el arnés de origen gana en simplicidad operativa**: activar/desactivar un pack es una operación, sin que el agente tenga que entender 11 niveles para usarla. |
| **Presupuesto de contexto** | `harness.toml` fija bytes máximos (`max_root_bytes`, `max_active_skill_description_bytes`, `max_memory_index_bytes`) y el compilador **aborta la escritura** si se excede (`CompileError`, `compile_context.py:336-345`). | `cosmos.toml [presupuesto]` con `entrada`, `resumen`, `oceanos`, `galaxia_lineas`, más `[guardarrailes] umbral_solapamiento`. Invariantes E00-E19 lo verifican, incluida E17 (solapamiento por Jaccard de n-gramas). | Empate técnico, con matiz: el arnés de origen mide en **bytes** (reproducible sin tokenizador); COSMOS mide en **tokens aproximados** declarados (`metodo="aprox"` por defecto, `"exacto"` falla en voz alta si no hay tokenizador — NUCLEO.md §4). El diseño de COSMOS es más honesto sobre la métrica que le importa de verdad (tokens, no bytes) pero paga con un método "aprox" no verificado contra un tokenizador real en este repo. |
| **Validación** | `validate_skills.py` (368 líneas): frontmatter, duplicados, symlinks, TODOs sin cerrar — sobre **skills**, no sobre una taxonomía de 11 niveles. `audit_harness.py` (578 líneas): estructura, patrones prohibidos, secretos. | `cosmos/validar.py` (452 líneas): 19 invariantes E00-E18 (E19 en `compilar.py` aparte, según NUCLEO.md §6). | **COSMOS**, porque su validador cubre relaciones estructurales que el arnés de origen no modela (padre-hijo, unicidad entre hermanos, ciclos). el arnés de origen valida **contenido de skill** mejor (frontmatter estricto, TODOs, symlinks) porque es lo único que tiene que validar. |
| **Medición de tokens** | `audit_harness.py` imprime una aproximación de "contexto fijo" en tokens (`~1352 tok`) pero no hay un medidor dedicado ni fórmula documentada de cálculo — es un efecto secundario del auditor. | `cosmos/medir.py` (201 líneas) dedicado, con la fórmula `contexto_inicial`/`universo`/`descarga` fijada byte a byte en NUCLEO.md §2-3 (índice + cuerpos de océanos + catálogo, sin doble conteo, `descarga ∈ [0,1]` siempre). | **COSMOS**, con ventaja clara: tiene una fórmula normativa y su propio invariante que prohíbe que el resultado salga de rango — algo que este repo no tiene para su número de "contexto fijo". |
| **Compilación a vista plana** | `compile_context.py::write_outputs` — proyecta a `.claude/skills/` y `.agents/skills/` con manifiesto SHA-256 por artefacto (`harness/generated/context-manifest.json`), y protege con un marcador de prefijo (`_prepare_projection`, solo borra si el destino está vacío o tiene el marcador). | `cosmos/compilar.py` (356 líneas) — mismo patrón: escritura atómica, hash por entrada, símlinks relativos, respeta "ajenas" (nombres no reconocidos del manifiesto anterior). | Empate de diseño, con una diferencia real: la protección de el arnés de origen en `compile_context.py` es **de todo el prefijo `.claude/skills/` de una vez** (un solo marcador en la raíz del prefijo, `MARKER = ".generated-by-arnes-de-origen"` en `compile_context.py:26`); si el marcador existe, hace `shutil.rmtree` de **todo** el directorio y lo reescribe entero. La de COSMOS, por lo leído en `compilar.py` (variable `ajenas_nombres`), parece más fina (por entrada). Pero **el propio `project.py` de el arnés de origen sí es más fino que su propio `compile_context.py`** — ver "Mecanismos aprovechables". |
| **Integración real con Claude Code y Codex** | Proyecta a `.claude/skills/` (Claude) **y** `.agents/skills/` (Codex) desde las mismas fuentes, en el mismo paso (`MANAGED_PREFIXES` en `compile_context.py`). Además desactiva memoria automática de Claude Code y sus instrucciones Git nativas vía `.claude/settings.json` (visto en `CLAUDE_SETTINGS` de `project.py` y en la config repo). | `cosmos.toml [compilacion] destino = ".claude/skills"` — solo Claude Code, sin equivalente para Codex/`.agents/`. | **el arnés de origen**, con evidencia directa: dual-target ya funciona hoy (91 archivos generados en ambos prefijos, verificado). COSMOS no tiene destino para Codex en su configuración actual. |
| **Escaneo de secretos** | `secret_scan.py` (361 líneas): 12 patrones de contenido (claves privadas, tokens GitHub/OpenAI/Anthropic/AWS/Slack/GitLab/npm/Stripe, secretos asignados, URIs con credencial, DNI/NIE/NIF, IBAN, email, teléfono), más detección de tablas CSV/TSV con columnas PII (`_looks_like_pii_table`), más rutas prohibidas por nombre y prefijo. Nunca imprime el valor encontrado, solo `ruta:línea: posible <tipo>`. | No hay equivalente citado en `GOAL.md`/`NUCLEO.md`/`UNIVERSO.md` — el `spec/UNIVERSO.md` reserva esto al sistema solar `seguridad` (galaxia `guardia`) pero como catálogo de herramientas de terceros, no como escáner propio. | **el arnés de origen, sin discusión**: tiene un escáner propio, medido, funcionando (`secret_scan: limpio` en este repo). COSMOS no tiene nada que auditar aquí todavía — es hueco de diseño, no una capacidad peor. |
| **Memoria** | `retrieve_memory.py` (216 líneas): BM25 + expansión de un salto + presupuesto de bytes de salida, sobre `memory/index.json` generado desde `memory/entries/*.md` por `compile_context.py::memory_artifacts` (con detección de ciclos de supersesión, backlinks, fechas de vigencia). | Nivel `lluvia` en la taxonomía ("memoria: se evapora del contexto y precipita donde hace falta") — **descrito**, sin implementación citada en `cosmos/*.py` (los 8 módulos listados son `cli`, `compilar`, `generar`, `medir`, `modelo`, `validar`, `__init__`, `__main__` — ninguno de recuperación de memoria). | **el arnés de origen**, y con margen: tiene un recuperador BM25 real, con tests (`test_memory_retrieval.py`, 7 tests en verde) y datos reales indexados. COSMOS tiene el concepto (`lluvia`) pero, por lo que hay en el repo hoy, no el mecanismo. |
| **Proyección a repos externos** | `project.py` (511 líneas) — ver mecanismo detallado abajo. Es la única pieza de todo el repo con `init`/`sync`/`check` contra un `target` **fuera** del propio repo del arnés. | Ninguna. `cosmos/compilar.py` compila el árbol de COSMOS **sobre sí mismo** (`destino = ".claude/skills"` es relativo a la raíz de COSMOS, no a un repo de proyecto ajeno). No hay concepto de "proyectar sobre un repo externo sin pisar lo suyo" en la spec leída. | **el arnés de origen, y es la capacidad más importante de las diez de esta tabla** para el objetivo declarado de COSMOS (un repo clonable sobre cualquier proyecto). Detalle abajo. |

---

## Mecanismos aprovechables

### 1. Cómo decide `compile_context.py` qué entra en el contexto raíz

`active_skill_dirs(config)` (`compile_context.py:143-172`) hace un glob de **un solo nivel** dos
veces:

```python
skill_dirs = sorted(path.parent for path in (ROOT / "skills").glob("*/SKILL.md"))
for pack in enabled:
    skill_dirs.extend(sorted(path.parent for path in (ROOT / "packs" / pack / "skills").glob("*/SKILL.md")))
```

Es decir: siempre entran las 4 skills núcleo (`skills/*/SKILL.md`), y solo se añaden las de los
packs listados en `harness.toml [skills] enabled_packs` (hoy `["wordpress", "web-quality"]`).
Cambiar qué está activo es **una lista en un TOML**, sin tocar Git (lo gestiona `pack.py`, ver
punto 2). El contexto raíz (`AGENTS.md`/`CLAUDE.md`) se genera con `render_template()`
(`compile_context.py:174-183`), que solo interpola `{{CORE_POLICY}}` y `{{PACKS}}` en una plantilla
fija — **nunca** vuelca la lista de skills activas ni sus descripciones al contexto raíz (eso
vive en `skills-catalogo.json` y en las proyecciones nativas). Presupuesto: si el `AGENTS.md`/
`CLAUDE.md` renderizado supera `max_root_bytes` (12.000 hoy) o la suma de bytes de `description` de
las skills activas supera `max_active_skill_description_bytes` (9.000 hoy), `build_artifacts()`
lanza `CompileError` y no escribe nada (`compile_context.py:336-345`) — falla cerrado, no trunca en
silencio.

### 2. Cómo habilita/deshabilita `pack.py` sin tocar Git

`write_local()` (`pack.py:48-104`) **no** usa una librería de escritura TOML (no existe una en la
stdlib): edita `harness.local.toml` línea por línea, localizando la sección `[skills]` con una
regex tolerante a comillas/espacios, reconstruyendo solo la línea `enabled_packs = [...]` y
preservando byte a byte todo lo demás del fichero (otras claves locales, comentarios). `_assignment_end()`
prueba, línea a línea, si el TOML acumulado hasta ahí ya parsea con `enabled_packs` dentro, para
saber dónde termina una asignación que puede ocupar varias líneas. `harness.local.toml` **no se
publica** (está fuera de Git — confirmado por el propio README). El override de entorno
`ARNES-DE-ORIGEN_PACKS` tiene precedencia sobre el fichero mientras exista, y los comandos que mutan
packs fallan explícitamente mientras esa variable esté puesta, para que el estado mostrado nunca
contradiga lo guardado.

### 3. Cómo proyecta `project.py` a un repo externo sin pisar lo ajeno — la pieza clave para COSMOS

Este es el mecanismo que responde directamente a la necesidad de COSMOS de un `compilar` que
también sepa proyectarse sobre un repo de trabajo ajeno sin pisarlo.

**Marcador por skill, no por prefijo.** A diferencia de `compile_context.py` (un marcador en la
raíz de `.claude/skills/` que protege *todo el árbol* de una vez), `project.py` escribe un fichero
`.generated-by-arnes-de-origen` **dentro de cada carpeta de skill individual**, con un contenido exacto
fijo (`MARKER_CONTENT`). `_managed_skill_dirs(base)` (`project.py:324-337`) solo considera "gestionada"
una carpeta si ese marcador existe, es un fichero regular (no symlink) y su contenido coincide
byte a byte. Esto permite distinguir, dentro del mismo `.claude/skills/`, cuáles carpetas puso el
arnés y cuáles son del proyecto (o de otro arnés).

**Colisión con lo ajeno = error, nunca sobrescritura.** `sync_project()` (`project.py:429-460`)
recorre las skills esperadas y, si el destino existe pero **no** está en el conjunto gestionado,
lanza `ProjectError(f"no se sobrescribe la skill ajena {runtime}/skills/{name}")` — aborta sin
escribir nada. `project_problems()` (el `check`, de solo lectura) hace la misma comprobación y la
reporta como `conflicto no gestionado <runtime>/skills/<name>` sin lanzar excepción, para que un
`check` pueda correr en CI sin abortar el proceso.

**Reemplazo atómico por skill, con backup y rollback.** `_replace_skill()` (`project.py:403-427`):
escribe los ficheros nuevos en un directorio de staging (`tempfile.mkdtemp` en el mismo padre),
renombra el destino actual a `.<nombre>.arnes-de-origen-backup`, renombra el staging al nombre final, y
solo entonces borra el backup. Si algo falla a mitad, el bloque `except` restaura el backup **si el
destino quedó sin existir** — nunca deja el proyecto sin esa skill ni con dos copias a la vez. Si ya
existe un backup pendiente de una sincronización anterior (señal de que algo se cortó a media
operación), se niega a continuar (`"existe un backup pendiente de una sincronización anterior"`) en
vez de arriesgarse a pisarlo.

**Fusión no destructiva de `AGENTS.md`/`CLAUDE.md`.** `_merged()` (`project.py:258-275`) busca los
marcadores `<!-- arnes-de-origen-harness:start -->` / `<!-- arnes-de-origen-harness:end -->`. Si no existen y
el fichero está vacío, escribe el bloque entero; si no existen y el fichero tiene contenido ajeno,
**añade** el bloque al final, respetando el contenido existente; si existen (una sola vez cada uno,
en orden), sustituye solo lo que hay entre ellos y conserva todo lo de fuera, delante y detrás. Si
hay marcadores duplicados o desordenados, falla con `ProjectError` en vez de adivinar.

**Fusión de `.claude/settings.json` por unión de diccionarios.** `expected_claude_settings()`
(`project.py:294-308`) hace `current | CLAUDE_SETTINGS` — las claves del arnés (memoria automática
apagada, instrucciones Git nativas apagadas, notificaciones apagadas, MCP de todos los proyectos
apagado) **ganan** sobre las mismas claves si ya existían, pero **todas las demás claves del
proyecto se conservan intactas**, porque `|` de diccionarios en Python no toca lo que no está en el
operando derecho.

**Cómo resuelve el problema de que Claude Code solo escanea el primer nivel de `skills/`.**
Aquí está la respuesta directa a la pregunta que pedía el encargo: **sí, ya está resuelto, y de dos
formas complementarias**. `skill_sources()` (`project.py:210-233`) hace el mismo glob de un nivel
que `compile_context.py` (`(ROOT/"skills").glob("*/SKILL.md")` + `(ROOT/"packs"/pack/"skills").glob("*/SKILL.md")`)
— es decir, la fuente puede vivir anidada (`packs/wordpress/skills/header-footer/`, dos niveles
bajo `packs/`) sin que eso le importe a Claude Code, porque **nunca se le entrega esa ruta**: lo que
se copia al destino es siempre `<runtime>/skills/<nombre-de-skill>/`, un solo nivel bajo `skills/`,
sea cual sea la profundidad de origen. Comprobado en vivo en este repo: tras `bootstrap.py`,
`.claude/skills/` tiene **15 carpetas de skill directamente dentro**, ninguna anidada bajo un
subdirectorio de pack, aunque las fuentes vengan de `skills/` (núcleo) y de `packs/wordpress/skills/`
+ `packs/web-quality/skills/` (dos packs distintos) simultáneamente. Es el mecanismo más
directamente reutilizable por COSMOS: su taxonomía de 11 niveles puede vivir tan profunda como
haga falta puertas adentro, mientras el `compilar` de COSMOS aplane exactamente `ciudad` y `pueblo`
(ya es lo que dice NUCLEO.md §5) al mismo patrón de "un nivel bajo el directorio que Claude Code sí
escanea".

### 4. Cómo detecta secretos `secret_scan.py`

Lee del **índice/blobs de Git**, nunca del worktree sin commitear salvo con `--staged` explícito
(`_candidate_git_entries`, `scan()`), y por streaming en bloques de 64 KiB con solape de 4096 bytes
entre bloques (`PATTERN_OVERLAP`) para no perder una coincidencia partida entre dos lecturas. Nunca
imprime el valor capturado — solo `ruta:línea: posible <categoría>` (`_finding()`), y las rutas
mismas pasan por `path_label()` cuando el hallazgo es sobre la ruta y no el contenido. Detecta,
además de credenciales de proveedor conocidas (AWS, GitHub, OpenAI, Anthropic, Slack, GitLab, npm,
Stripe) por regex de formato: DNI/NIE/NIF y IBAN españoles asignados con `=`/`:`, URIs con
credencial embebida (`user:pass@host`), y **tablas CSV/TSV con dos o más columnas de cabecera
sensible** (`_looks_like_pii_table`, normaliza cabeceras quitando acentos y compara contra una lista
de 19 términos en español/inglés) — no busca el patrón de un valor, busca la **forma de una tabla de
personas**.

### 5. Qué hace `redaction.py`

Trece líneas: una función, `path_label()`, hash SHA-256 truncado a 12 hex de la ruta con prefijo
`ruta#`. Es el mecanismo por el que **ningún diagnóstico de este repo revela nunca una ruta ni un
nombre de fichero real** — se usa en `audit_harness.py` para nombrar hallazgos de patrones prohibidos
sin decir cuál es el fichero afectado, y en `secret_scan.py` para el mismo fin. Es trivial de portar
tal cual a COSMOS si su validador necesita reportar violaciones sin filtrar nombres de proyecto.

### 6. Cómo se instala el pre-commit sin sustituir uno existente

`install_precommit()` (`bootstrap.py:68-113`): si no hay hook, lo instala. Si hay un hook y contiene
el marcador propio (`HOOK_MARKER = "# managed-by-arnes-de-origen-harness"`) o coincide con el patrón de un
hook legado de una versión anterior del mismo arnés (`_is_legacy_managed_hook`, que reconoce un
hook de dos líneas `#!/bin/sh` + `exec <python> <ruta a precommit.py del mismo repo>`), lo
**actualiza**. Si hay un hook ajeno que no cumple ninguna de las dos condiciones, imprime un aviso
con la ruta redactada (`path_label(hook)`) y devuelve `"omitido (hook ajeno)"` **sin tocarlo**. El
propio hook, en tiempo de ejecución, resuelve su intérprete (`python3` o `python`, el primero con
versión ≥3.11) en vez de asumir uno fijo — evita el fallo silencioso de `command not found` con
`python` a secas documentado como circuit-breaker en las reglas de este workspace.

---

## Qué hacemos

**Recomendación: (b) COSMOS se construye encima, adoptando `project.py` como capa nueva de
proyección externa; no absorbe `packs/` como sustituto de su taxonomía.**

Argumentos, con lo medido arriba:

1. **La taxonomía de 11 niveles no tiene equivalente en el arnés de origen y es la razón de ser del
   proyecto.** `packs/` es una lista plana de 10 paquetes sin relaciones de contención ni reglas de
   carga por nivel — resuelve "qué se agrupa", no "cuándo entra cada cosa en el contexto según
   dónde vive". Absorberlo significaría renunciar a `spec/NUCLEO.md` y `spec/UNIVERSO.md`, que son
   trabajo ya validado (revisión adversarial de Codex documentada, invariantes E00-E18 en verde con
   meta-prueba mutante) y que resuelven problemas que `packs/` ni se plantea (unicidad de ruta,
   ciclos de contención, descarga acotada a `[0,1]`).
2. **`project.py` no tiene equivalente en COSMOS y es la pieza que el `GOAL.md` de COSMOS pide
   explícitamente** ("un repo que se puede clonar sobre cualquier proyecto"). `cosmos/compilar.py`
   hoy solo compila sobre sí mismo. Construir esto desde cero repetiría un trabajo ya hecho y medido
   en 511 líneas + 7 tests en verde (`test_project_bridge.py`): marcador por skill, colisión con lo
   ajeno como error duro, reemplazo atómico con backup y rollback, fusión de instrucciones por
   bloque marcado, fusión de settings por unión de diccionarios. Reescribirlo en Python contra la
   spec de COSMOS es el trabajo concreto que sigue; **portar el mecanismo, no el código pack-céntrico**.
3. **Riesgos de esta vía:**
   - `project.py` proyecta *skills planas* (packs) a un destino plano (`<runtime>/skills/<nombre>`).
     COSMOS tiene que adaptar el mismo patrón de marcador-por-unidad + backup atómico a sus dos
     únicos niveles aplanables (`ciudad`, `pueblo` — NUCLEO.md §5), lo cual es un cambio de qué
     cuenta como "unidad", no del mecanismo de escritura seguro en sí.
   - El presupuesto de el arnés de origen es en **bytes**; el de COSMOS es en **tokens aproximados**. Si se
     porta la lógica de `expected_root_files()` (que valida contra `max_root_bytes` antes de
     escribir), hay que decidir si el gate de COSMOS sigue siendo por tokens (más caro de calcular,
     más honesto) o se añade un segundo gate en bytes (más barato, redundante). Fijarlo en
     `cosmos.toml` explícitamente, no dejarlo implícito.
   - Ninguno de los scripts de el arnés de origen fue probado aquí contra un repo externo real (la regla de
     "solo lectura sobre vh-ref" lo impedía); el contrato de `project.py` se verificó por lectura de
     código + los 7 tests de `test_project_bridge.py`, no por una ejecución en vivo de esta sesión.
     Antes de portarlo, ejercitarlo una vez contra un repo de prueba desechable.
   - `secret_scan.py` y `redaction.py` no están en el `GOAL.md`/`UNIVERSO.md` de COSMOS como
     capacidad propia (el sistema `seguridad` los trata como catálogo de herramientas de terceros).
     Son pequeños (374 líneas juntos), están probados y no compiten con la taxonomía — son candidatos
     directos a portar tal cual, no a rediseñar.

**No se recomienda (a)** — COSMOS no gana nada absorbiendo `packs/`, porque ya tiene un sistema de
agrupación más expresivo y validado; absorber el código de el arnés de origen entero traería su modelo plano
como si fuera un reemplazo, cuando es un caso más simple que la taxonomía ya cubre.

**No se recomienda (c)** — mantenerlos separados repite exactamente el problema que motivó esta
auditoría: dos compiladores con manifiesto+hash+escritura atómica (`compile_context.py` /
`cosmos/compilar.py`), dos medidores de contexto, y ningún proyector externo en ninguno de los dos
si no se actúa. El coste de no fusionar es mantener en paralelo trabajo que ya se solapa a día de
hoy.
