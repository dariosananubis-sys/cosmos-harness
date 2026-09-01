# Sistemas — bajo nivel

Barrido GitHub para COSMOS. Nicho: compiladores e intérpretes, runtime y recolección de basura,
concurrencia y paralelismo, gestión de memoria, perfilado y rendimiento extremo, llamadas al
sistema, sistemas de ficheros, y depuración de lo que no se ve (trazas, volcados, condiciones de
carrera).

Método: cupo de WebSearch agotado (dado). API de GitHub autenticada — `/search/repositories` para
descubrir candidatos por consulta, `/repos/{owner}/{repo}` para verificar uno a uno (estrellas,
licencia, fecha del último push) los candidatos fuertes o los que ya conocía de antes. El endpoint
`/search` tiene un límite propio de 30 peticiones/minuto que se agotó varias veces con 403 "API rate
limit exceeded" incluso espaciando las llamadas 3-6s — el mismo síntoma que documentó
`infraestructura-devops.md` el mismo día. El endpoint `/repos/{owner}/{repo}` (rate limit "core",
5000/h) no tuvo ese problema y fue la vía principal para cerrar el barrido sin gastar más tiempo en
reintentos. Fecha: 2026-09-01. Estrellas y fechas de push tal cual las devolvió la API en ese
momento — no hay instalación ni ejecución real de ninguna herramienta en esta sesión.

---

## De primera

Máximo 10. Elegidos por: se ejecuta de verdad (nada de "awesome-lists"), es el mejor de su hueco
(perfilado, parsing, memoria, concurrencia, depuración de lo invisible), coste cero, y corre en un
Mac Apple Silicon de 8 GB sin pedir una cadena de compilación cruzada rara.

1. **[LLVM / Clang](https://github.com/llvm/llvm-project)** — 40k★, licencia Apache-2.0 con
   excepciones LLVM, push 2026-09-01. **Por qué gana**: es la infraestructura de compiladores de
   facto — frontend (Clang), IR intermedia, decenas de backends, y de propina trae LLDB y las bases
   de AddressSanitizer/ThreadSanitizer. Este es el "país de código de compiladores" del nicho: quien
   necesite escribir un lenguaje, un backend o una pasada de optimización entra aquí, no en un
   tutorial.

2. **[tree-sitter](https://github.com/tree-sitter/tree-sitter)** — 26.8k★, MIT, push 2026-09-01.
   **Por qué gana** frente a ANTLR4 (19k★, clásico generador LALR): tree-sitter hace parsing
   *incremental* con recuperación de errores, pensado para herramientas que reparsean mientras el
   usuario teclea (editores, linters, `semble`-like). ANTLR4 sigue siendo mejor para implementar un
   lenguaje completo desde su gramática formal — entra en segunda fila para ese caso concreto, no es
   un empate real.

3. **[rr](https://github.com/rr-debugger/rr)** — 10.6k★, licencia mixta (BSD+MIT, NOASSERTION en
   GitHub), push 2026-08-16. **Por qué gana**: graba una ejecución nativa entera y la reproduce
   determinísticamente, con `reverse-continue`/`reverse-step` sobre GDB. Es la herramienta que
   convierte "el bug de carrera que no se repite" en algo que sí se repite — literal "depuración de
   lo que no se ve".

4. **[bpftrace](https://github.com/bpftrace/bpftrace)** — 10.3k★, Apache-2.0, push 2026-08-29.
   **Por qué gana**: lenguaje de trazado de alto nivel (estilo DTrace) sobre eBPF, para hacer una
   pregunta puntual al kernel en vivo (`bpftrace -e 'kprobe:do_sys_open { printf("%s\n", comm); }'`)
   sin escribir un programa BPF en C. Nota de entorno: eBPF es kernel Linux — en este Mac se usa
   contra una VM/servidor Linux, no contra macOS.

5. **[samply](https://github.com/mstange/samply)** — 4.4k★, Apache-2.0, push 2026-08-31. **Por qué
   gana** frente a async-profiler (9.1k★, segunda fila): async-profiler es oro para JVM, pero exige
   una JVM corriendo; samply es un profiler de muestreo nativo multiplataforma (macOS/Linux/Windows,
   Apple Silicon incluido) que abre el resultado en Firefox Profiler — el pick correcto para el
   entorno de este Mac sin instalar nada más.

6. **[flamegraph-rs/flamegraph](https://github.com/flamegraph-rs/flamegraph)** — 6k★, Apache-2.0,
   push 2026-09-01. **Por qué gana** frente al [FlameGraph original de Brendan
   Gregg](https://github.com/brendangregg/FlameGraph) (19.7k★, sin licencia declarada en GitHub —
   NOLIC, aunque el proyecto usa CDDL/MIT según sus ficheros): este es un subcomando de `cargo` que
   envuelve `perf`+`dtrace`(macOS)+inferno en un solo comando, con licencia limpia y push de hoy. El
   original de Gregg sigue siendo la referencia histórica del formato — se cita, no se recomienda
   como dependencia directa por la ambigüedad de licencia.

7. **[mimalloc](https://github.com/microsoft/mimalloc)** — 13.3k★, MIT, push 2026-08-31. **Por qué
   gana**: allocator de propósito general con rendimiento de referencia, drop-in (`LD_PRELOAD` o
   enlazado directo), documentación clara y soporte nativo ARM64/macOS. Frente a jemalloc (11.1k★,
   segunda fila, el estándar de Redis/FreeBSD) gana en facilidad de adopción para un proyecto nuevo.

8. **[hyperfine](https://github.com/sharkdp/hyperfine)** — 28.8k★, Apache-2.0, push 2026-04-30.
   **Por qué gana**: benchmarking de línea de comandos con rigor estadístico (warmup, outliers,
   comparación A/B) para *cualquier* binario, no solo código propio — sirve igual para medir un
   script Python que un binario Rust. Para micro-benchmarks dentro de código Rust, criterion.rs
   (5.5k★) es el complemento natural, no un competidor — va en segunda fila.

9. **[google/sanitizers](https://github.com/google/sanitizers)** (AddressSanitizer,
   ThreadSanitizer, MemorySanitizer) — 12.5k★, NOASSERTION (licencia BSD/Apache según componente),
   push 2026-05-19. **Por qué gana**: no hay competidor real — es la implementación de referencia,
   integrada en Clang y GCC, y detecta en tiempo de ejecución exactamente lo que un test no ve:
   overflows, use-after-free, data races.

10. **[Tokio](https://github.com/tokio-rs/tokio)** — 33k★, MIT, push 2026-08-31. **Por qué gana**:
    es el runtime async de facto en Rust — scheduler multi-hilo, temporizadores, I/O no bloqueante.
    Representa el "país de código de concurrencia" del nicho: una librería con la que se *escribe*
    software concurrente, no solo una herramienta que lo mide. Rayon (13.3k★, segunda fila) resuelve
    un problema distinto — paralelismo de datos CPU-bound, no I/O async — y no es sustituible por
    Tokio ni viceversa.

---

## Segunda fila

- **[ANTLR4](https://github.com/antlr/antlr4)** — 19k★, BSD-3-Clause. Generador de parsers LALR
  clásico; gana a tree-sitter cuando el objetivo es implementar un lenguaje completo desde su
  gramática, no analizar código ya escrito de forma incremental.
- **[lalrpop](https://github.com/lalrpop/lalrpop)** / **[rust-peg](https://github.com/kevinmehall/rust-peg)**
  — generadores de parser LR(1)/PEG específicos de Rust, para cuando el objetivo final es un binario
  Rust y no hace falta portabilidad de gramática entre lenguajes.
- **[wasmtime](https://github.com/bytecodealliance/wasmtime)** — 18.6k★, Apache-2.0, push
  2026-09-01. Runtime WebAssembly rápido y sandboxed (Bytecode Alliance); representa la pieza
  "runtime alternativo" del continente compiladores — útil para quien necesita ejecutar código no
  confiable con límites duros de memoria/CPU.
- **[RustPython](https://github.com/RustPython/RustPython)** — 22.3k★, MIT. Intérprete de Python
  escrito en Rust; interesante como referencia de "cómo se escribe un intérprete", no como reemplazo
  de CPython en producción.
- **[bdwgc](https://github.com/bdwgc/bdwgc)** — 3.5k★, licencia mixta permisiva (NOASSERTION en
  GitHub). El recolector de basura conservador C/C++ más usado en la práctica (Guile, Mono en algún
  momento, muchos lenguajes embebidos). Nota: el repo original `ivmai/bdwgc` se movió aquí — la URL
  vieja da 301.
- **[mmtk-core](https://github.com/mmtk/mmtk-core)** — 512★, Apache-2.0, push 2026-09-01. Toolkit de
  gestión de memoria de investigación (Rust) diseñado para conectarse a runtimes de lenguaje
  distintos (usado experimentalmente por Julia, JikesRVM); la opción moderna si se quiere estudiar
  o construir un GC nuevo, no solo usar uno ya hecho.
- **[jemalloc](https://github.com/jemalloc/jemalloc)** / **[tcmalloc](https://github.com/google/tcmalloc)**
  — allocators alternativos a mimalloc; jemalloc es el histórico de Redis/FreeBSD, tcmalloc el de
  Google (parte de gperftools). Cambiar de uno a otro es casi siempre benchmarking, no una decisión
  a priori.
- **[go-delve/delve](https://github.com/go-delve/delve)** — 24.9k★, MIT. El debugger de Go — no hay
  alternativa real dentro del ecosistema Go, se menciona porque LLDB/GDB no entienden bien sus
  goroutines.
- **[BCC](https://github.com/iovisor/bcc)** — 22.6k★, Apache-2.0. Toolkit de herramientas eBPF listas
  para usar (`opensnoop`, `execsnoop`, `biolatency`...) en C/Python; más verboso que bpftrace pero
  con ejemplos ya escritos para casi cualquier pregunta común sobre el kernel.
- **[async-profiler](https://github.com/async-profiler/async-profiler)** — 9.1k★, Apache-2.0. El
  profiler de referencia para JVM (Java/Kotlin/Scala) — gana a samply *solo* si el target corre en
  una JVM.
- **[Scalene](https://github.com/plasma-umass/scalene)** — 13.5k★, Apache-2.0. Profiler Python de
  CPU/GPU/memoria con sugerencias de optimización asistidas por IA; el más completo del ecosistema
  Python cuando la duda es "¿dónde se va la memoria Y el tiempo a la vez?".
- **[VizTracer](https://github.com/gaogaotiantian/viztracer)** — 7.7k★, Apache-2.0. Traza y
  visualiza la ejecución completa de un programa Python (no solo muestreo) — mejor para entender
  *flujo* que para medir hot-path puro.
- **[osquery](https://github.com/osquery/osquery)** — 23.5k★, NOASSERTION (Apache-2.0/GPL-2.0 dual
  según componente). Convierte el sistema operativo en una base SQL consultable
  (`SELECT * FROM processes WHERE...`) — el ángulo "sistemas de ficheros y llamadas al sistema" del
  nicho resuelto como instrumentación, no como trazado puntual.
- **[Watchman](https://github.com/facebook/watchman)** — 13.7k★, MIT. Vigilancia de cambios en el
  sistema de ficheros a escala (miles de ficheros) con consultas — la pieza que usan build systems
  grandes para no hacer polling.
- **[speedscope](https://github.com/jlfwong/speedscope)** — 6.7k★, MIT — visor web interactivo de
  perfiles (acepta el formato de `perf`, Chrome DevTools, y más); complementa a samply/flamegraph
  cuando se quiere navegar el perfil en vez de mirar un SVG estático.
- **[inferno](https://github.com/jonhoo/inferno)** — 2.2k★, NOASSERTION (MIT/Apache-2.0 dual).
  Puerto en Rust del FlameGraph original, más rápido; usado internamente por flamegraph-rs.
- **[criterion.rs](https://github.com/bheisler/criterion.rs)** — 5.5k★, Apache-2.0. Micro-benchmarks
  estadísticamente honestos dentro de un crate Rust — el complemento de hyperfine a nivel de función
  en vez de proceso completo.
- **[trio](https://github.com/python-trio/trio)** / **[ZIO](https://github.com/zio/zio)** —
  librerías de concurrencia estructurada para Python y Scala respectivamente; alternativas a Tokio
  cuando el lenguaje del proyecto no es Rust.

## Humo

- **[Parca](https://github.com/parca-dev/parca)** (5k★) / **[Perforator](https://github.com/yandex/perforator)** (3.4k★) — perfilado continuo a escala de clúster; sobreingeniería para una agencia con pocos servidores.
- **[Coroot](https://github.com/coroot/coroot)** (7.9k★) — observabilidad con perfilado continuo vía eBPF y RCA asistido por IA; más una plataforma de infraestructura que una herramienta de bolsillo.
- **[snoop](https://github.com/pandaadir05/snoop)** (223★) — `strace` moderno sobre eBPF con TUI; prometedor pero joven, poca base de usuarios todavía — vigilar, no confiar aún.
- **[rbspy](https://github.com/rbspy/rbspy)** (2.6k★) / **[vernier](https://github.com/jhawthorn/vernier)** (1.1k★) — profilers de muestreo para Ruby.
- **[fgprof](https://github.com/felixge/fgprof)** (3.1k★) — profiler Go que junta tiempo on-CPU y off-CPU (I/O) en un solo perfil.
- **[php-spx](https://github.com/NoiseByNorthwest/php-spx)** (2.6k★) — profiler PHP con UI web integrada, cero configuración de infraestructura aparte.
- **[0x](https://github.com/davidmarkclements/0x)** (3.5k★) — flamegraph de Node.js con un solo comando.
- **[yappi](https://github.com/sumerc/yappi)** (1.7k★) — profiler Python consciente de hilos/asyncio/gevent.

## Mapeo a COSMOS

```
sistema-solar  sistemas
├── continente  compiladores-e-interpretes
│   ├── pais  infraestructura-de-compilacion
│   │          provincias: frontend · IR · backends · optimizacion
│   │          pueblos: LLVM/Clang, RustPython (intérprete alternativo, referencia educativa)
│   ├── pais  analisis-de-codigo-y-generacion-de-parsers
│   │          provincias: gramaticas-formales · parsing-incremental · recuperacion-de-errores
│   │          pueblos: tree-sitter, ANTLR4, lalrpop, rust-peg
│   └── pais  runtimes-alternativos
│              provincias: sandboxing · bytecode-portable
│              pueblos: wasmtime
├── continente  runtime-y-recoleccion-de-basura
│   ├── pais  recolectores-de-basura
│   │          provincias: conservador-embebible · investigacion-multi-lenguaje
│   │          pueblos: bdwgc, mmtk-core, whippet (WIP, vigilar)
│   └── pais  asignadores-de-memoria
│              provincias: proposito-general · hardened · especificos-de-GPU
│              pueblos: mimalloc, jemalloc, tcmalloc
├── continente  concurrencia-y-paralelismo
│   └── pais  codigo-de-concurrencia              ← el código propio de este nicho
│              provincias: runtimes-async · paralelismo-de-datos · alternativas-por-lenguaje
│              pueblos: Tokio, Rayon, trio (Python), ZIO (Scala)
├── continente  perfilado-y-rendimiento-extremo
│   ├── pais  profilers-de-muestreo
│   │          provincias: nativo-multiplataforma · por-runtime-de-lenguaje
│   │          pueblos: samply, async-profiler (JVM), Scalene/yappi/VizTracer (Python), rbspy (Ruby), fgprof (Go)
│   └── pais  visualizacion-de-perfiles
│              provincias: generadores-de-flamegraph · visores-interactivos
│              pueblos: flamegraph-rs, FlameGraph (origen, licencia sin clasificar), inferno, speedscope
├── continente  llamadas-al-sistema-y-sistemas-de-ficheros
│   └── pais  instrumentacion-del-sistema-operativo
│              provincias: consultas-tipo-SQL-sobre-el-SO · vigilancia-de-ficheros-a-escala
│              pueblos: osquery, Watchman
└── continente  depuracion-de-lo-que-no-se-ve
    ├── pais  depuracion-nativa-y-replay
    │          provincias: replay-determinista · por-lenguaje-especifico
    │          pueblos: rr, delve (Go), codelldb (front-end de LLDB)
    ├── pais  trazas-y-eBPF
    │          provincias: lenguaje-de-alto-nivel · toolkit-listo-para-usar
    │          pueblos: bpftrace, BCC, snoop (joven)
    └── pais  sanitizers-y-benchmarking-honesto
               provincias: deteccion-de-bugs-en-tiempo-de-ejecucion · medicion-estadistica
               pueblos: google/sanitizers (ASan/TSan/MSan), hyperfine, criterion.rs
```

Frontera declarada: el trazado *distribuido* de microservicios (Jaeger, SigNoz, Zipkin — que sí
aparecieron en las búsquedas de "tracing") **no entra aquí**: eso es observabilidad de *servicios* y
ya vive en `infraestructura-devops.md`. Este nicho cubre trazado de *proceso y kernel* (eBPF, replay
determinista, profilers), que es un oficio distinto aunque comparta la palabra "tracing".

## Lo que falta

- **GDB y Valgrind no están verificados en vivo.** Viven en sourceware.org sin un mirror único y
  canónico en GitHub fácil de confirmar en el tiempo disponible — se omiten del catálogo por eso, no
  porque no sirvan; cualquier lector los conoce igual y siguen siendo estándar de facto.
- **Zig se confirmó en vivo que ya no vive principalmente en GitHub**: `ziglang/zig` devuelve
  descripción "Moved to Codeberg" y último push 2025-11-27 (hace ~9 meses) — quedó fuera del barrido
  por esa razón, no por falta de calidad.
- **La provincia de recolección de basura es la más floja**: solo 2 candidatos verificados con
  tracción real (bdwgc, mmtk-core) y uno joven sin rodaje (whippet, 241★, WIP). Los recolectores más
  usados en producción (V8, .NET, Go) van integrados en su runtime y no existen como paquete
  standalone — se documenta como ausencia intencional, no como hueco por cubrir.
- **El endpoint `/search` de GitHub golpeó el rate-limit de 30/min varias veces** incluso con 3-6s
  entre llamadas — mismo síntoma que documentó ya `infraestructura-devops.md` el mismo día 2026-09-01;
  parece compartido a nivel de token/IP, no exclusivo de esta sesión. Se resolvió cambiando a
  `/repos/{owner}/{repo}` directo para verificar candidatos concretos, que no tuvo ese problema.
- **Cero instalación o ejecución real** — todo el barrido son metadatos de GitHub (estrellas,
  licencia, fecha de push), no una prueba de uso. Antes de recomendar cualquiera de estos a un
  cliente, ejecutarlo una vez sobre un caso real, tal como exige el filtro "perfecto" de COSMOS.
- Sin datos de clientes, IPs ni credenciales en este fichero.
