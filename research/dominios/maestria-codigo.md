# Maestría de Código — ser un experto en código de verdad

Barrido GitHub para COSMOS. Dominio: dominio profundo de lenguajes (Rust, Go, TypeScript, Python, C,
SQL), algoritmos y estructuras de datos, arquitectura y patrones, sistemas distribuidos y
concurrencia, rendimiento y perfilado, depuración de problemas difíciles, refactorización a gran
escala, migraciones de código, compiladores, y lectura/comprensión de bases de código enormes y
ajenas. No es "consejos de estilo" — es mecanismo: lo que un modelo de lenguaje no puede hacer solo
(aplicar una transformación consistente a 400 ficheros, perfilar un binario, navegar dos millones de
líneas, reproducir determinísticamente un crash).

Método: API de GitHub autenticada (`api.github.com/search/repositories` + `/repos/{owner}/{repo}`),
NO WebSearch (cupo de sesión agotado, 200/200). Límite real observado: el endpoint `search` dispara
un rate-limit **secundario** (no el contador documentado de 30/min — ese se mostraba en `0 usado` a
la vez que la API devolvía 403) con ráfagas de más de ~3-4 peticiones seguidas; se resolvió
espaciando las búsquedas 3-10s. El endpoint `/repos/{owner}/{repo}` (core, 5.000/h) no tuvo ese
problema. Varios repos conocidos habían cambiado de organización (redirect 301, resuelto siguiendo
`Location` a `api.github.com/repositories/{id}`): `weggli` → `weggli-rs/weggli`, `GritQL` →
`biomejs/gritql` (absorbido por Biome), `cppcheck` → `cppcheck-opensource/cppcheck`, `scip` →
`scip-code/scip`, `gitingest` → `coderamp-labs/gitingest`.

Fecha del barrido: 2026-09-01. Estrellas y `pushed_at` verificados en vivo vía API, no de memoria.

---

## De primera

Máximo 10. Elegidos por mecanismo verificable — no "el modelo ya sabe escribir un bucle", sino "esto
hace algo que un modelo por sí solo no puede": transformar código real sin equivocarse, perfilar un
proceso vivo, reproducir un crash de forma determinista, encontrar el input exacto que rompe algo.

1. **[ast-grep](https://github.com/ast-grep/ast-grep)** — 15.7k★, MIT, muy activo (push 2026-08-31).
   **Por qué gana**: motor de búsqueda/lint/reescritura *estructural* (no regex) sobre el AST real de
   ~30 lenguajes, en Rust. Una regla YAML describe un patrón sintáctico y una reescritura, y se
   aplica a un repo entero de forma determinista — exactamente lo que un LLM no puede garantizar
   (consistencia en 400 ficheros). Tiene MCP server propio (`ast-grep-mcp`, 455★) y extensión VS
   Code. Ecosistema de reglas comunitarias ya montado (`coderabbitai/ast-grep-essentials`, 150★).

2. **[tree-sitter](https://github.com/tree-sitter/tree-sitter)** — 26.8k★, MIT, muy activo (push
   2026-09-01). **Por qué gana**: es el sustrato de parsing incremental que sostiene a ast-grep,
   difftastic, Neovim, Helix y Zed — un parser generator que produce un AST concreto tolerante a
   errores y actualizable incrementalmente mientras se edita. Entender esta pieza es entender por qué
   media docena de herramientas de esta lista funcionan.

3. **[Serena](https://github.com/oraios/serena)** — 28.7k★, MIT, muy activo (push 2026-08-30).
   **Por qué gana**: MCP toolkit que da a un agente de código *navegación semántica real* vía
   Language Server Protocol — `find_symbol`, `find_referencing_symbols`, rename, go-to-definition —
   en vez de que el modelo adivine offsets de texto o haga grep a ciegas. Es la pieza que convierte
   "leer una base de código enorme" en un problema resoluble sin cargarla entera en contexto.

4. **[difftastic](https://github.com/Wilfred/difftastic)** — 25.8k★, MIT, activo (push 2026-08-28).
   **Por qué gana**: diff *consciente de sintaxis* (usa tree-sitter): un `git diff` normal marca como
   cambiada una línea reformateada; difftastic ve que el árbol sintáctico es el mismo y no la marca.
   Imprescindible para revisar el resultado de un codemod o una migración a gran escala sin ruido.

5. **[rr](https://github.com/rr-debugger/rr)** — 10.6k★ (nacido en Mozilla), activo (push
   2026-08-16). **Por qué gana**: depurador de **grabación y repetición determinista** — graba una
   ejecución una vez y la repite bit a bit tantas veces como haga falta con `reverse-continue`,
   `reverse-step`. Es la única forma real de depurar un bug intermitente/de concurrencia: nada que un
   modelo pueda simular razonando sobre el código.

6. **[Semgrep](https://github.com/semgrep/semgrep)** (+ **[opengrep](https://github.com/opengrep/opengrep)**
   como fork libre tras cambios de licencia/registro de reglas de Semgrep) — Semgrep 16.5k★
   LGPL-2.1, opengrep 3.0k★ LGPL-2.1, ambos activos (push 2026-09-01 y 2026-08-31). **Por qué gana**:
   análisis estático "patrones que se parecen al código fuente" — la regla se escribe casi como el
   código que busca, sin aprender un DSL de AST. Motor detrás de GitHub Advanced Security en muchos
   repos y de miles de reglas comunitarias.

7. **[OpenRewrite](https://github.com/openrewrite/rewrite)** — 3.7k★, Apache-2.0, muy activo (push
   2026-09-01). **Por qué gana**: refactorización masiva basada en un **Lossless Semantic Tree**
   (preserva formato, comentarios, espacios) con "recetas" componibles versionadas — migra un
   framework entero (ej. JUnit 4→5, Spring Boot) en cientos de repos de forma reproducible y
   revisable en PR. Es a Java/Kotlin lo que ast-grep es a lenguajes más ligeros, con más años de
   rodaje en refactors gigantes reales.

8. **[py-spy](https://github.com/benfred/py-spy)** — 15.5k★, MIT, activo (push 2026-08-14).
   **Por qué gana**: perfilador de muestreo para Python que se **engancha a un PID en producción sin
   tocar el código ni reiniciar el proceso** (lee memoria del proceso vía `/proc` o `ptrace`). Genera
   flame graphs de un servicio real corriendo — algo que ningún análisis estático ni el propio modelo
   pueden inferir sin medir.

9. **[AFL++](https://github.com/AFLplusplus/AFLplusplus)** — 6.7k★, AGPL-3.0, muy activo (push
   2026-08-31). **Por qué gana**: fuzzing guiado por cobertura — muta inputs y observa qué caminos de
   código nuevos destapa cada mutación, sin que nadie escriba el caso de prueba. Encuentra el input
   exacto que revienta un parser o un `unwrap()` que un razonamiento manual jamás cubriría.

10. **[Jepsen](https://github.com/jepsen-io/jepsen)** — 7.5k★, sin licencia declarada (código
    disponible, verificar términos antes de reutilizar), activo (push 2026-08-29). **Por qué gana**:
    framework de verificación de sistemas distribuidos con **inyección de fallos real** (particiones
    de red, relojes desincronizados, procesos muertos) + comprobador de linealizabilidad sobre la
    historia de operaciones observada. Ha encontrado bugs de consistencia reales en MongoDB, etcd,
    Redis Cluster, CockroachDB — bugs que solo aparecen bajo fallo real, no en el código en reposo.

---

## Segunda fila

**Búsqueda estructural y codemods, alternativas/complementos a ast-grep:**
- **[comby](https://github.com/comby-tools/comby)** — 2.7k★, Apache-2.0. Búsqueda/reescritura
  estructural con sintaxis de "huecos" (`:[var]`) sin necesitar gramática tree-sitter por lenguaje —
  cubre lenguajes que ast-grep no soporta aún, a costa de menos precisión sintáctica.
- **[GritQL](https://github.com/biomejs/gritql)** — 4.6k★, MIT, absorbido por el proyecto Biome
  (antes `getgrit/gritql`, redirect 301 confirmado). Lenguaje de consulta declarativo para
  buscar/lintar/modificar código, integrado ahora en el toolchain de Biome.
- **[jscodeshift](https://github.com/facebook/jscodeshift)** — 10.0k★, MIT, activo. El toolkit de
  codemods de JS/TS de Facebook, base de casi todos los codemods de migración de librerías React/Jest
  del ecosistema (`jest-codemods`, `types-react-codemod`, `aws-sdk-js-codemod`).
- **[ts-morph](https://github.com/dsherret/ts-morph)** — 6.2k★, MIT, activo. Envoltorio sobre la
  Compiler API de TypeScript para manipular AST con una API ergonómica — mejor que jscodeshift cuando
  el codemod necesita tipos, no solo sintaxis.
- **[LibCST](https://github.com/Instagram/LibCST)** — 1.9k★, activo. CST (concrete syntax tree) de
  Python que preserva formato exacto — la base recomendada para escribir codemods Python en serio en
  vez de tocar el `ast` estándar (que pierde formato).
- **[rope](https://github.com/python-rope/rope)** — 2.2k★, LGPL-3.0, activo. Librería de
  refactorización Python (rename, extract method, move) usada como motor por varios IDEs.
- **[pyupgrade](https://github.com/asottile/pyupgrade)** / **[refurb](https://github.com/dosisod/refurb)**
  — 4.1k★ y 2.5k★. Modernizan sintaxis Python automáticamente (pyupgrade sube de versión de lenguaje,
  refurb sugiere/aplica idioms más nuevos); refurb sin push desde abril-2026, menos vivo.
- **[facebookarchive/codemod](https://github.com/facebookarchive/codemod)** — 4.1k★, **archivado**
  desde 2020. Interés histórico: el codemod CLI original de Facebook, sustituido de facto por
  jscodeshift/ast-grep. No usar para nada nuevo.

**Navegación y búsqueda a escala de repo gigante:**
- **[sourcegraph/zoekt](https://github.com/sourcegraph/zoekt)** — 1.9k★, Apache-2.0, activo. Motor
  de búsqueda de código por trigramas, muy rápido sobre monorepos; es el motor de búsqueda que usaba
  Sourcegraph. **Nota**: el repo principal `sourcegraph/sourcegraph` devuelve 404 en la API — parece
  haberse cerrado/privatizado, sin confirmar motivo (marcar `UNVERIFIED`).
- **[hound](https://github.com/hound-search/hound)** — 5.9k★, MIT, activo. Búsqueda de código
  instantánea (motor trigram similar a zoekt), self-hosted, nacido en Etsy.
- **[universal-ctags](https://github.com/universal-ctags/ctags)** — 7.3k★, GPL-2.0, muy activo. El
  generador de índices de símbolos que sigue vivo (fork mantenido del ctags original) — sigue siendo
  la base de "jump to definition" en editores sin LSP.
- **[probe](https://github.com/probelabs/probe)** — 694★, Apache-2.0, activo. Motor de búsqueda de
  código "AI-friendly" que combina velocidad de ripgrep con chunking AST vía tree-sitter — más nuevo
  y con menos tracción que Serena, pero mecanismo similar sin depender de un LSP por lenguaje.
- **[Kythe](https://github.com/kythe/kythe)** — 2.2k★, Apache-2.0, con actividad más lenta (push
  jul-2026). Ecosistema de Google para indexación de código agnóstica de lenguaje (el "backend" que
  alimentaba grep.app/Google Code Search internamente).
- **[Glean](https://github.com/facebookincubator/Glean)** — 1.4k★, activo (push 2026-09-01). Sistema
  de Meta para recolectar y consultar "hechos" sobre una base de código — la contraparte de Kythe en
  Facebook, con un lenguaje de consulta (Angle) propio.
- **[SCIP](https://github.com/scip-code/scip)** — 762★, Apache-2.0, activo (repo movido desde
  `sourcegraph/scip`). Protocolo binario de intercambio de inteligencia de código (sucesor de LSIF),
  más compacto y con menos overhead que LSIF para indexar un repo entero offline.

**Perfilado por lenguaje (complementan a py-spy):**
- **[samply](https://github.com/mstange/samply)** — 4.4k★, Apache-2.0, muy activo. Perfilador de
  muestreo multiplataforma (macOS/Linux/Windows) que exporta al formato del Firefox Profiler —
  cómodo para Rust/C/C++ sin instrumentar el binario.
- **[flamegraph-rs/flamegraph](https://github.com/flamegraph-rs/flamegraph)** (cargo-flamegraph) y
  **[pprof-rs](https://github.com/tikv/pprof-rs)** — generación de flame graphs para binarios Rust
  vía `perf`/backtrace-rs, sin Perl ni pipes manuales como el script original de Brendan Gregg.
- **[google/pprof](https://github.com/google/pprof)** — 9.3k★, Apache-2.0, muy activo. Visualización
  y análisis de perfiles pprof — el formato estándar de facto para perfiles CPU/memoria en Go y cada
  vez más en otros ecosistemas.
- **[brendangregg/FlameGraph](https://github.com/brendangregg/FlameGraph)** — 19.7k★, sin push desde
  oct-2024 (estable, no significa abandonado: el formato ya está consolidado). El visualizador de
  stack traces original — casi todo lo demás de esta lista genera datos en su formato o lo emula.
- **[scalene](https://github.com/plasma-umass/scalene)** / **[memray](https://github.com/bloomberg/memray)**
  / **[austin](https://github.com/P403n1x87/austin)** — 13.5k★/15.2k★/2.2k★, todos activos. Trío
  Python: scalene separa CPU/GPU/memoria línea a línea, memray es específico de memoria (detecta
  fugas y su traza de asignación), austin es un sampler de muy bajo overhead pensado para producción.
- **[hotspot](https://github.com/KDAB/hotspot)** — 5.1k★, GUI Qt sobre `perf` de Linux — para leer
  visualmente lo que ya capturó `perf record`, sin la terminal.

**Depuración de concurrencia y memoria:**
- **[miri](https://github.com/rust-lang/miri)** — 6.5k★, Apache-2.0, muy activo. Intérprete del MIR
  de Rust que detecta *undefined behavior* (aliasing inválido, use-after-free) que el compilador no
  ve porque solo se manifiesta en tiempo de ejecución.
- **[google/sanitizers](https://github.com/google/sanitizers)** — 12.5k★, activo. AddressSanitizer /
  ThreadSanitizer / MemorySanitizer — instrumentación en tiempo de compilación (parte de LLVM/GCC)
  que atrapa data races y corrupción de memoria con overhead bajo comparado con Valgrind.
- **[loom](https://github.com/tokio-rs/loom)** — 2.8k★, MIT, activo. Testing por permutación de
  concurrencia para Rust: ejecuta *todos* los interleavings posibles de un test concurrente pequeño en
  vez de confiar en que el scheduler real algún día exponga la race.
- **[tokio-console](https://github.com/tokio-rs/console)** — 4.6k★, MIT, activo. "Depurador" para
  tareas async de Tokio — ve qué tareas están bloqueadas, cuánto tiempo llevan sin poll, algo
  invisible con un debugger tradicional en código asíncrono.
- **[CodeTracer](https://github.com/metacraft-labs/codetracer)** — 1.3k★, AGPL-3.0, muy activo (push
  2026-09-01). Depurador de time-travel multi-lenguaje más joven que rr pero con ambición más amplia
  (no solo Linux/x86); vale la pena vigilarlo, todavía menos probado en producción que rr.

**Análisis estático por lenguaje:**
- **[ruff](https://github.com/astral-sh/ruff)** — 49.4k★, MIT, muy activo. Linter+formateador Python
  en Rust, sustituye a Flake8+isort+pyupgrade+buena parte de pylint con un solo binario muy rápido.
- **[pyright](https://github.com/microsoft/pyright)** — 15.6k★, activo. Type checker estático de
  Python, motor detrás de Pylance en VS Code.
- **[staticcheck](https://github.com/dominikh/go-tools)** — 6.9k★, MIT, activo. El linter Go más
  respetado más allá de `go vet`; **[golangci-lint](https://github.com/golangci/golangci-lint)**
  (19.3k★) lo orquesta junto a decenas de linters más en un único runner rápido.
- **[eslint](https://github.com/eslint/eslint)** (27.5k★) y **[biome](https://github.com/biomejs/biome)**
  (25.7k★) — el estándar JS/TS y su alternativa en Rust todo-en-uno (lint+format), más rápida pero
  con menos plugins de terceros aún.
- **[cppcheck](https://github.com/cppcheck-opensource/cppcheck)** — 6.7k★, GPL-3.0, activo (repo
  movido desde `danmar/cppcheck`). Análisis estático C/C++ sin necesitar compilar el proyecto.
- **[coccinelle](https://github.com/coccinelle/coccinelle)** — 813★, GPL-2.0, activo. Motor de
  "semantic patches" para C — describe una transformación en un lenguaje parecido a un diff y la
  aplica en todo el árbol; es como usa el kernel de Linux para sus refactors masivos en C.
- **[joern](https://github.com/joernio/joern)** — 3.5k★, Apache-2.0, muy activo. Plataforma de
  análisis basada en Code Property Graphs (fusiona AST + control-flow + data-flow) para
  C/C++/Java/JS/Python/Kotlin/binarios — pensado para caza de vulnerabilidades a gran escala.
- **[weggli](https://github.com/weggli-rs/weggli)** — 2.5k★, Apache-2.0, **sin push desde jul-2024**
  (repo movido desde `googleprojectzero/weggli`, org original de Project Zero). Búsqueda semántica
  ligera en C/C++ pensada para hunting de vulnerabilidades; útil pero claramente poco mantenido hoy.
- **[sqlfluff](https://github.com/sqlfluff/sqlfluff)** — 9.9k★, MIT, muy activo. Linter/formateador
  SQL modular con soporte multi-dialecto y SQL templado (dbt, Jinja).

**Compiladores y frontends de lenguaje:**
- **[LLVM](https://github.com/llvm/llvm-project)** — 40.0k★, muy activo. La infraestructura de
  compiladores de referencia; incluye clang-tidy/clang-analyzer (análisis estático C/C++) y clangd
  (el LSP de C/C++) en el mismo monorepo.
- **[Roslyn](https://github.com/dotnet/roslyn)** — 20.6k★, MIT, muy activo. La plataforma de
  compilador de C#/VB con API de análisis y *code fixes* de primera clase — el modelo que inspiró
  buena parte del tooling moderno de refactor-con-API-de-compilador.
- **[rust-analyzer](https://github.com/rust-lang/rust-analyzer)** — 16.8k★, Apache-2.0, muy activo.
  El LSP de referencia de Rust. **[golang/tools](https://github.com/golang/tools)** (8.0k★) cubre el
  equivalente en Go (`gopls`, `goimports`, etc.).

**Fuzzing adicional:** **[cargo-fuzz](https://github.com/rust-fuzz/cargo-fuzz)** (1.9k★) y
**[honggfuzz](https://github.com/google/honggfuzz)** (3.4k★) — envoltorios/motores alternativos a
AFL++, cargo-fuzz específico de Rust sobre libFuzzer.

**Verificación formal:** **[TLA+](https://github.com/tlaplus/tlaplus)** — 3.0k★, MIT, muy activo. El
model checker que AWS usa públicamente para verificar protocolos distribuidos antes de escribir una
línea de implementación — complementa a Jepsen (Jepsen verifica el sistema ya construido; TLA+
verifica el diseño antes de construirlo).

**Métricas y complejidad:** **[tokei](https://github.com/XAMPPRocky/tokei)** (14.9k★),
**[scc](https://github.com/boyter/scc)** (8.7k★, además estima COCOMO), **[cloc](https://github.com/AlDanial/cloc)**
(23.5k★, el más veterano) y **[lizard](https://github.com/terryyin/lizard)** (2.5k★, complejidad
ciclomática multi-lenguaje sin necesitar compilar). **radon** (Python, `rubik/radon`, 2.0k★) sin push
desde oct-2024 — sigue siendo el estándar de facto para complejidad Python aunque esté parado.

**Contexto de repo para LLM (aplanar un repo entero a un prompt):**
**[repomix](https://github.com/yamadashy/repomix)** (28.2k★, muy activo),
**[gitingest](https://github.com/coderamp-labs/gitingest)** (15.4k★, repo movido) y
**[code2prompt](https://github.com/mufeedvh/code2prompt)** (7.6k★) — tres herramientas que resuelven
lo mismo (empaquetar un repo con árbol + contenido + conteo de tokens para pegarlo a un LLM); repomix
es el más completo (templating, XML/Markdown, respeta `.gitignore`).

---

## Humo

Cola larga: proyectos nuevos, de nicho o con tracción aún pequeña — mecanismo real pero sin rodaje
probado. El clúster más llamativo es el de "puentes MCP↔LSP para agentes de código", todos con menos
de 25★ y la mayoría con commits de las últimas semanas: prueba de que es un nicho caliente en 2026,
pero ninguno se acerca a Serena en madurez todavía — revisar en unos meses.

- **[ckb](https://github.com/SimplyLiz/ckb)** (108★) — inteligencia de código para asistentes IA: MCP + CLI + HTTP API con navegación de símbolos.
- **[pathfinder / Headless IDE](https://github.com/irahardianto/pathfinder)** (14★) — MCP server con inteligencia semántica AST-aware para agentes.
- **codescout, lsp-mcp-server, symtrace-mcp, CogniCode, Simone-MCP, karellen-lsp-mcp, lsp-intelligence, code-intel, mcp-lsp-server** — media docena más de puentes LSP→MCP casi idénticos en propósito, todos de 2026, todos <5★.
- **[jonatas/fast](https://github.com/jonatas/fast)** (273★) — "Find in AST", grep-y-refactor directamente sobre el AST de Ruby.
- **[pyastgrep](https://github.com/spookylukey/pyastgrep)** (111★) — grep del AST de Python vía XPath.
- **[serpl](https://github.com/yassinebridi/serpl)** (856★) — TUI de búsqueda-y-reemplazo estilo VS Code, sobre ripgrep+sd.
- **ast-grep-vscode, ast-grep-mcp, ast-grep-essentials, telescope-sg, ast-grep.el** — extensiones satélite del propio ecosistema ast-grep (VS Code, MCP, reglas comunitarias, Neovim/Telescope, Emacs).
- **[semble_rs](https://github.com/johunsang/semble_rs)** (215★) — búsqueda de código híbrida BM25+semántica con chunking AST vía tree-sitter, "AI-agent-native"; nótese que el `semble` CLI que Darío ya tiene instalado y usa a diario parece construido sobre esta misma idea/nombre — ya adoptado, no hace falta evaluarlo de nuevo.
- **[opengrep](https://github.com/opengrep/opengrep)** — cubierto en Segunda fila junto a Semgrep, se repite aquí como recordatorio del patrón "fork libre tras cambio de licencia" (mismo patrón que OpenTofu/Terraform en el dominio de infraestructura).
- **[oxc](https://github.com/oxc-project/oxc)** (22.6k★) y **[rolldown](https://github.com/rolldown/rolldown)** (13.9k★) — toolchain JS/TS en Rust (parser, linter, bundler) apostando por velocidad extrema; interesante como referencia de "cómo se construye un compilador/toolchain moderno", no una herramienta que se instale para trabajo de agencia.
- **[zed](https://github.com/zed-industries/zed)**, **[helix](https://github.com/helix-editor/helix)**, **[neovim](https://github.com/neovim/neovim)** — editores construidos directamente sobre tree-sitter/LSP; útiles como referencia de implementación del mecanismo, no como "herramienta a instalar" per se.
- **CodeAlive-AI/codealive-mcp, xdotech/goatlas, kraklabs/cie, user120309/kontext-engine, dan-fernan/codeburrow** y media docena más de "motores de búsqueda semántica de código" con 1-90★ — mismo problema que resuelve probe/Serena, todos demasiado nuevos para evaluar.
- **[FireDBG.for.Rust](https://github.com/SeaQL/FireDBG.for.Rust)**, **[revy](https://github.com/rerun-io/revy)**, **cargo-rr**, **pycrunch-trace** — depuradores de time-travel de nicho (Rust, motor de juegos Bevy, wrapper de rr, Python) con mucha menos tracción que rr/CodeTracer.
- **[Reactime](https://github.com/open-source-labs/Reactime)** (2.2k★) — time-travel debugging específico de React, fuera del alcance de "código de verdad" backend pero mencionable si el stack es frontend-pesado.
- **VoxCore84/code-intel** — inteligencia de código híbrida ctags+clangd vía MCP, específico para C/C++.

---

## Mapeo a COSMOS

```
sistema-solar  Software / Ingeniería (todo el conocimiento técnico de COSMOS)
└─ planeta     Ingeniería y Producto
   └─ continente  Desarrollo y Calidad de Código
      └─ país         MAESTRÍA DE CÓDIGO   ← este dominio
         ├─ provincia  Búsqueda y Transformación Estructural
         │   ├─ ciudad  Motores de patrón estructural   → pueblos: ast-grep, comby, GritQL
         │   └─ ciudad  Codemods por lenguaje            → pueblos: jscodeshift, ts-morph, LibCST,
         │                                                          rope, OpenRewrite, pyupgrade
         ├─ provincia  Sustrato de Parsing
         │   └─ ciudad  Gramáticas incrementales          → pueblo: tree-sitter (y sus ~200 gramáticas)
         ├─ provincia  Navegación de Bases de Código Enormes
         │   ├─ ciudad  Puente LSP para agentes            → pueblos: Serena, el enjambre de MCP-LSP
         │   ├─ ciudad  Motores de búsqueda de código      → pueblos: Zoekt, Hound, probe, ctags
         │   ├─ ciudad  Indexación a escala (Google/Meta)  → pueblos: Kythe, Glean, SCIP
         │   └─ ciudad  Contexto de repo para LLM          → pueblos: repomix, gitingest, code2prompt
         ├─ provincia  Diffing Estructural
         │   └─ ciudad  Diff consciente de sintaxis        → pueblo: difftastic
         ├─ provincia  Depuración de Problemas Difíciles
         │   ├─ ciudad  Depuración reversible               → pueblos: rr, CodeTracer
         │   ├─ ciudad  UB / races en tiempo de compilación → pueblos: miri, sanitizers (ASan/TSan/UBSan), loom
         │   └─ ciudad  Depuración async                    → pueblo: tokio-console
         ├─ provincia  Rendimiento y Perfilado
         │   ├─ ciudad  Python                              → pueblos: py-spy, scalene, memray, austin
         │   ├─ ciudad  Rust/C/C++                          → pueblos: samply, cargo-flamegraph, pprof-rs, hotspot
         │   └─ ciudad  Go                                  → pueblo: google/pprof
         ├─ provincia  Análisis Estático y Linters
         │   └─ ciudad  Por lenguaje                        → pueblos: Semgrep/opengrep/CodeQL/joern (multi),
         │                                                             ruff/pyright (Python), staticcheck/golangci-lint (Go),
         │                                                             eslint/biome (JS/TS), cppcheck/coccinelle/weggli (C),
         │                                                             sqlfluff (SQL)
         ├─ provincia  Fuzzing y Verificación
         │   ├─ ciudad  Fuzzing guiado por cobertura        → pueblos: AFL++, cargo-fuzz, honggfuzz
         │   └─ ciudad  Sistemas distribuidos               → pueblos: Jepsen (verifica lo construido), TLA+ (verifica el diseño)
         ├─ provincia  Compiladores y Frontends de Lenguaje
         │   └─ ciudad  Infraestructura                     → pueblos: LLVM, Roslyn, rust-analyzer, gopls
         └─ provincia  Métricas y Complejidad
             └─ ciudad  Conteo y complejidad                → pueblos: tokei, scc, cloc, lizard, radon
```

Frontera con países vecinos de COSMOS: aquí solo entra lo que ayuda a *escribir, entender, transformar
o depurar* código ya existente con mecanismo verificable. Un país vecino de "Infraestructura y DevOps"
cubre hacer correr ese código en producción (contenedores, CI/CD, monitorización); uno de "IA/Agentes"
cubriría plataformas de agentes en sí (sandboxes, orquestación multi-agente) aunque compartan
mecanismo de AST/LSP con la provincia de Navegación de este país.

## Lo que falta

- **Cero verificación en vivo.** Todo el barrido es lectura de metadatos de la API de GitHub
  (estrellas, licencia, `pushed_at`, descripción) — ninguna herramienta de esta lista se instaló ni
  se ejecutó contra código real. Antes de recomendar cualquiera de las de "De primera" a un caso real,
  probar el ciclo completo (p. ej. correr una regla de ast-grep sobre un repo de verdad, o adjuntar
  py-spy a un proceso vivo) para confirmar que el mecanismo se comporta como documenta.
- **WebSearch agotado desde el minuto cero** de esta tarea (200/200 de la sesión compartida) — todo
  el barrido se hizo con la API de GitHub, sin la comparativa de terceros ni blogs/benchmarks que
  trae una búsqueda normal. Los "por qué gana" son lectura de README/descripción propia de cada
  proyecto más criterio del agente, no una fuente externa independiente.
- **Rate-limit secundario del endpoint `search`** obligó a espaciar consultas 3-10s y a resolver
  varias por `/repos/{owner}/{repo}` directo en vez de búsqueda — cobertura de nichos muy nuevos
  (proyectos con <1 semana de vida) probablemente incompleta.
- **`sourcegraph/sourcegraph` devuelve 404** en la API — no se ha confirmado si el repo se privatizó,
  se renombró o el producto cambió de modelo; marcado `UNVERIFIED`, no asumir motivo.
- **El clúster de "MCP↔LSP para agentes"** (Humo) tiene más de 12 proyectos casi idénticos nacidos en
  2026, todos con tracción mínima: es señal de un nicho que probablemente se consolide en 1-2
  ganadores pronto — vale la pena repasar este dominio en 2-3 meses en vez de darlo por cerrado.
- **Jepsen no declara licencia** en los metadatos de GitHub (`license: None`) pese a tener el código
  público — revisar el `LICENSE` real del repo antes de reutilizar nada de su código, no solo leer
  los reportes.
- Cobertura débil a propósito de **algoritmos y estructuras de datos puros** y de **arquitectura y
  patrones de diseño**: casi todo lo que existe ahí es "prosa" (libros, cursos, listas de patrones)
  que el filtro de este barrido descarta por diseño — si hace falta ese ángulo, es un dominio de
  contenido/formación, no de mecanismo, y no encaja en este país de COSMOS tal como está definido.
