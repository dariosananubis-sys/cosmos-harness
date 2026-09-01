# Montaje del universo — tanda 2

Fecha: 2026-09-01 · Árbol: `galaxia/` · Config: `galaxia.toml` · Continuación de
[`montaje-tanda-1.md`](montaje-tanda-1.md), no rediseño: mismos criterios, mismo estilo de resumen.

Lo que arregla: los 8 nichos que la tanda 1 dejó vacíos porque sus barridos aún no habían cerrado,
los 3 escasos, y el nicho `ciberseguridad`, que tenía 6 pueblos y **los 6 eran de seguridad de
código** — cero pentest, cero forense, cero malware, cero criptografía.

## 1. Qué quedó montado

| | Tanda 1 | Tanda 2 | Δ |
|---|---:|---:|---:|
| galaxia | 1 | 1 | — |
| sistema-solar | 20 | 20 | — |
| continente | 0 | 4 | +4 |
| país | 21 | 29 | +8 |
| pueblo | 66 | 127 | **+61** |
| estrella | 9 | 9 | — |
| océano | 5 | 5 | — |
| mar | 5 | 5 | — |
| **total** | **127** | **200** | **+73** |

**Los 20 nichos están poblados.** Pueblos por nicho:

`ciberseguridad` 26 · `agentes` 10 · `web` 8 · `medios` 8 · `datos` 8 · `infraestructura` 7 ·
`extraccion` 6 · `conocimiento` 5 · `mercados` 5 · `visibilidad` 5 · `cientifico` 4 · `sistemas` 4 ·
`blockchain` 4 · `moviles` 4 · `juegos` 4 · `legal` 4 · `automatizacion` 4 · `embebidos` 4 ·
`negocio` 4 · `saas` 3.

### 1.1 `ciberseguridad`: de 6 pueblos de análisis de código a un nicho completo

Los 6 que había **no se borraron**: se recolocaron bajo `analisis`, que es donde siempre debieron
estar. Los 4 continentes son los que ya esbozaba `spec/UNIVERSO.md`.

```
ciberseguridad
├── ofensiva          (auditoría autorizada, alcance por escrito)
│   ├── reconocimiento     amass · nuclei
│   ├── explotacion        metasploit · sqlmap · zaproxy
│   ├── post-explotacion   impacket · bloodhound
│   └── codigo-ofensivo    aflplusplus · pwntools
├── defensiva
│   ├── deteccion          sigma-cli · crowdsec
│   ├── codigo-defensivo   libsodium · coraza
│   └── lynis                                    ← pueblo directo: no agrupa con nadie
├── analisis
│   ├── vulnerabilidades       semgrep · bearer · trufflehog      ← los 3 que ya estaban
│   ├── cadena-de-suministro   osv-scanner · trivy · scorecard    ← los 3 que ya estaban
│   ├── forense                volatility3 · chainsaw
│   └── malware                ghidra · yara
└── gobierno          defectdojo · atomic-red-team                ← pueblos directos
```

`trufflehog` colgaba directo del sistema solar; ahora vive en `analisis/vulnerabilidades` con sus
hermanos. El país `analisis-de-codigo` se renombró a `vulnerabilidades` bajo el continente `analisis`
(nombre de `spec/UNIVERSO.md`); `cadena-de-suministro` conserva su nombre y baja un nivel.

La estrella del nicho —la que lleva **el límite que no se cruza**— no se tocó: ya estaba escrita en
la tanda 1 y se carga con cualquier trabajo del sistema.

### 1.2 Los 11 nichos restantes

Todos con los pueblos colgando **directos del sistema solar**, sin país. Es lo mismo que hizo la
tanda 1 con `visibilidad`, `saas`, `legal` y `conocimiento`, y por el mismo motivo: con 4 pueblos, un
país sería un nivel de relleno que cobra un `resumen` y no agrupa nada (`TAXONOMIA.md`). Cuando un
nicho llegue a 6-8 pueblos, ahí toca abrir países.

| Nicho | Pueblos nuevos |
|---|---|
| `moviles` | `flutter` · `react-native` · `tauri` · `fastlane` |
| `juegos` | `godot` · `bevy` · `phaser` · `libresprite` |
| `embebidos` | `platformio` · `esp-idf` · `zephyr` · `esphome` |
| `blockchain` | `foundry` · `openzeppelin-contracts` · `slither` · `echidna` |
| `cientifico` | `scipy` · `pixi` · `dvc` · `snakemake` |
| `sistemas` | `tree-sitter` · `rr` · `samply` · `tokio` |
| `automatizacion` | `n8n` · `windmill` · `celery` · `hammerspoon` |
| `negocio` | `docuseal` · `gobl` · `twenty` · `openproject` |
| `legal` (1→4) | `ort` · `fossology` · `arx` |
| `conocimiento` (1→5) | `mkdocs-material` · `mermaid` · `d2` · `openapi-generator` |
| `saas` (2→3) | `casdoor` |
| `visibilidad` (4→5) | `matomo` |

`matomo` cierra la mitad del hueco que la tanda 1 declaró por custodia: medir el tráfico real sin
entregar el acceso delegado de la propiedad del cliente a un servidor de terceros.

### 1.3 `maestria-codigo`: no es un nicho, y no lo es en ningún sitio

Sus 81 recursos **no produjeron ni un pueblo propio**. Se repartieron:

- **Al mar `criterio`**, ampliado: navegación semántica por protocolo de servidor de lenguaje
  (`serena`) para «reutilizar antes que crear»; transformación estructural sobre el árbol sintáctico
  (`ast-grep`, `openrewrite`) y revisión del codemod comparando árboles y no líneas (`difftastic`)
  para «tocar lo justo».
- **Al mar `pruebas`**, ampliado: el caso que rompe se busca mutando la entrada, el fallo
  intermitente se graba en vez de razonarse, y el sistema distribuido se prueba inyectando el fallo
  real y comprobando linealizabilidad.
- **A los países de código de cada nicho**: `aflplusplus` y `pwntools` a
  `ciberseguridad/ofensiva/codigo-ofensivo`; `tree-sitter` y `rr` a `sistemas`; `semgrep` ya estaba.

Los mares **cuestan 0 tokens de entrada** (el agua que no es océano no entra en `contexto_inicial`),
así que ampliarlos es gratis para el presupuesto. El precio está en §5.12.

## 2. Regla de admisión: qué entró y qué no

**122 entradas de primera fila** en los 12 barridos. Entraron **61 pueblos**: 52 de primera fila y 9
de segunda. **Rechazado el 57 % de la primera fila** y prácticamente toda la segunda y el `## Humo`.

`ciberseguridad` es la excepción del reparto: entraron **sus 12 de primera fila enteras** y 8 de
segunda, porque los 12 no cubrían continentes completos (post-explotación, endurecimiento, gobierno).
De `maestria-codigo` no entró **ninguna** como pueblo, por diseño (§1.3).

### A. Presupuesto de catálogo — el motivo dominante de esta tanda (≈45 nombres)

Es un motivo nuevo: la tanda 1 tenía 1.428 tokens de margen y esta tanda los ha gastado. Estos son
buenos, pasan el filtro y **no caben**. Todos quedan nombrados en el cuerpo del pueblo vecino.

- **Móviles**: `expo`, `capacitor`, `ionic`, `detox`, `mobsf`, `rxdb`, `nativescript`, `tuist`, `zealot`.
- **Juegos**: `raylib`, `tiled`, `entt`, `tic-80`, `miniaudio`, `noise-rs`, `pixelorama`, `ldtk`, `love`.
- **Embebidos**: `micropython`, `mosquitto`, `home-assistant`, `freertos`, `probe-rs`, `radiolib`, `mcuboot`.
- **Blockchain**: `viem`+`wagmi`, `anchor`, `ponder`, `aderyn`, `mythril`, `halmos`.
- **Científico**: `numpy`, `julia`, `dask`, `hydra`, `reprozip`.
- **Sistemas**: `llvm`, `bpftrace`, `hyperfine`, `mimalloc`, `flamegraph`, `sanitizers`.
- **Automatización**: `node-red`, `huginn`, `kestra`, `bullmq`, `rpaframework`.
- **Negocio / conocimiento**: `cal.diy`, `docusaurus`, `mdbook`, `structurizr`, `wiki-js`, `trilium`, `mingrammer/diagrams`.
- **Ciberseguridad (2.ª fila)**: `peass-ng`, `ffuf`, `gobuster`, `ropgadget`, `openscap`, `kube-bench`,
  `falco`, `autopsy`, `drakvuf-sandbox`, `malwoverview`, `yargen`, `attack-navigator`, `faraday`,
  `juice-shop`, `dvwa`, `ctf-tools`, `radare2`/`Cutter`, `honggfuzz`, `modsecurity`.

### B. Solapamiento: mismo hueco, entra uno (≈30 nombres)

Cuando el motivo es solapamiento, **la descartada está nombrada en el cuerpo del pueblo que ganó**.

- `subfinder` (vs `amass`: solo hace el paso pasivo) · `mimikatz` (su volcado ya está en `impacket`,
  y es la que más fácil se sale del uso legítimo) · `libFuzzer` y `honggfuzz` (vs `aflplusplus`) ·
  `volatility` v2 (vs v3) · `Yara-Rules/rules` como corpus (el motor entra, el corpus lleva desde
  2024 parado) · `modsecurity` (vs `coraza`, que se empotra en el proceso).
- `hardhat` (vs `foundry`, mismo hueco y mucho más lento aquí) · `mythril`+`aderyn` (vs
  `slither`+`echidna`) · `graph-node` (vs `ponder`, los dos fuera).
- `docusaurus`, `mdbook` (vs `mkdocs-material`) · `ray` (vs `dask`, los dos fuera).
- `soloud` (vs `miniaudio`) · `flecs` (vs `entt`) · `ldtk` (vs `tiled`) · `watermelondb`, `realm`,
  `powersync` (vs `rxdb`) · `webdriverio` (vs `detox`) · `cordova` (vs `capacitor`) · `emqx` (vs
  `mosquitto`) · `arduino-lmic` (vs `radiolib`) · `openocd`, `stlink` (vs `probe-rs`) ·
  `async-profiler`, `py-spy` (vs `samply`) · `jemalloc` (vs `mimalloc`) · `antlr4` (vs `tree-sitter`)
  · `rayon` (problema distinto de `tokio`, no sustituible) · `aim` (vs el registrador ya existente).

### C. Cuesta dinero o licencia no libre (10 nombres)

`Unity` y `Unreal` (cobran por umbral de ingresos o regalías; además no caben en 8 GB) · `Aseprite`
(código público, binarios de pago — por eso ganó `libresprite`) · `PICO-8` (cerrado, de pago — por
eso `tic-80`) · `IDA Pro` (licencia de miles de euros — por eso `ghidra`) · `Metasploit Pro` (la
edición con interfaz e informes; el framework libre sí entró) · `Certora Prover` (nube de pago) ·
`Bitrise Cloud` (el CLI local sería gratis) · `Sentry` autoalojado completo (exige tres bases de
datos para una sola app) · `Mender` (cliente libre, gestión de flota de pago).

**Capas gratuitas sin verificar en vivo, que es lo mismo que de pago hasta que se compruebe**:
`wazuh` (Wazuh Cloud), `velociraptor` (licencia tras el cambio de patrocinador), `opencti`
(términos comerciales), `thehive` (la v5 se declara comercial en su propio README). Los cuatro
habrían sido el país `respuesta-a-incidentes`; ese país **no existe** por esto.

### D. Muerto o parado (7 nombres)

`Yara-Rules/rules` (sin movimiento desde 2024-04-17) · `PowerSploit` (2020, y sus técnicas ya están
firmadas por cualquier detección moderna) · `volatility` v2 (2025-05) · `soloud` (2024-08) ·
`watermelondb` (2025-08) · `halmos` (2025-08, 13 meses) · `multi-tenant-saas-toolkit` (2025-06, y 16
estrellas) · `CodePush` (archivado).

### E. Prosa, no mecanismo — criterio 1 (5 nombres)

`awesome-godot`, `awesome-flutter`, `awesome-react-native`, `open-source-ios-apps`, `zardus/ctf-tools`
(bootstrap de instalación, no herramienta). Los barridos ya los usaron solo para descubrir y no los
propusieron: el filtro funcionó una capa antes.

### F. Fuera del límite ético del nicho (8 nombres)

`Sn1per` (automatismo agresivo contra objetivos no acotados) · `byob` (construcción de botnets sin
contexto de red team) · `EDRSilencer`, `EDRChoker` (evasión de detección explícita) · `HFish` ·
`hashcat`, `thc-hydra` (doble uso legítimo en auditoría de contraseñas autorizada, pero sin hueco
propio aquí — queda como hueco declarado, no como rechazo por calidad) · `sliver` (C2 maduro; fuera
por presupuesto **y** por ser el que peor envejece si el alcance no está clarísimo).

### G. Es agua, no pueblo (4 nombres)

`ast-grep`, `openrewrite`, `difftastic`, `serena` → mar `criterio`. `jepsen` y la idea del fuzzing
por cobertura → mar `pruebas`. Atraviesan los 20 nichos; ponerlos como pueblo de uno los deja
invisibles en los otros 19. Es la misma decisión que la tanda 1 tomó con `ruff` y `mutmut`.

## 3. Duplicados evitados — qué iba a añadir y con qué chocaba

Esta es la sección que responde a *«¿y no quiero repetidos?»*. Cada línea es un pueblo que **estuve a
punto de crear** y no creé.

| Iba a añadir | Chocaba con | Qué hice |
|---|---|---|
| `mlflow` (barrido `cientifico`) | `agentes/mlflow` **ya existente** | No se añade. **E18 lo habría rechazado por nombre**: el aplanado exige nombres únicos globalmente. Citado en el cuerpo de `dvc` |
| `syft` (SBOM, barrido `legal`) | `ciberseguridad/analisis/cadena-de-suministro/trivy`, que ya genera el inventario | No se añade. El cuerpo de `ort` lo dice y apunta a `trivy` |
| `dep-scan` (barrido `legal`) | `osv-scanner` + `trivy` | No se añade |
| `axe-core`, `pa11y` (barrido `legal`) | `web/calidad-de-sitio/axe-core` **ya existente** + mar `accesibilidad` | No se añade |
| `openredaction` (barrido `legal`) | `legal/presidio` | No se añade |
| `changedetection.io` (barrido `automatizacion`) | **la tanda 1 ya lo rechazó** en `extraccion` frente a `scrapy`+`playwright`+`trafilatura` | No se reintroduce por otra puerta |
| `celery`/`bullmq` como infraestructura | la tanda 1 los aparcó explícitamente «pertenecen a `automatizacion`» | Entra `celery` **aquí**, que es donde tocaba; `bullmq` fuera por presupuesto |
| `tree-sitter`, `rr`, `aflplusplus`, `semgrep` | aparecen en **dos barridos** cada uno (`maestria-codigo` + su nicho) | Colocados **una sola vez**, en su nicho |
| `n8n`, `windmill` | aparecen en `automatizacion` **y** en `negocio-operaciones` | Colocados una sola vez, en `automatizacion`; el cuerpo de `twenty` y `openproject` los nombra |
| `node-red` | aparece en `automatizacion` **y** en `embebidos` | No entra en ninguno (presupuesto), y se dice en el cuerpo de `n8n` |
| `falco` (detección en contenedor) | `trivy` (configuración) + `infraestructura/vigilancia/*` | No se añade |
| `kube-bench`, `openscap` | `lynis` + `trivy` | No se añade |
| `home-assistant`, `mosquitto` | `esphome`, que ya resuelve el cliente de mensajería y la reconexión | No se añaden; citados en su cuerpo |
| `flamegraph`, `py-spy` | `sistemas/samply` | No se añaden; citados |
| `numpy` | `scipy`, que lo lleva debajo | No se añade: no es una elección, es el sustrato |
| `dask` | `datos/motor-analitico/polars` + `duckdb` | No se añade |
| `capacitor`, `ionic` | `moviles/react-native` (mismo hueco «web a app») | No se añaden; citados en su cuerpo |
| `detox`, `webdriverio` | `extraccion/fuentes-web/playwright` + mar `pruebas` | No se añaden |
| `mobsf` (seguridad de APK) | el nicho `ciberseguridad` entero | No se añade en `moviles`; si hiciera falta, va a `analisis` |
| `mermaid` **y** `d2` | entre sí | **Entran los dos**, con la frontera escrita en el cuerpo de cada uno (§5.10) |
| `ort` **y** `fossology` | entre sí | **Entran los dos**, empate declarado por el barrido (§5.11) |
| `zephyr` **y** `freertos` | entre sí | **Entra uno** por presupuesto, con el criterio de elección escrito (§5.8) |

## 4. Verificación

### `python3 -m cosmos validar galaxia --config galaxia.toml` — literal

```
COSMOS  verde  0 errores
```

### `python3 -m cosmos medir galaxia --config galaxia.toml` — literal

```
COSMOS  medir

  Entrada ......... 3.918 tokens   (estimado, ±desconocido, heurística v1)
  Universo ........ 11.725 tokens   (estimado, ±desconocido, heurística v1)
  Descarga ........ 66,6 %
  Presupuesto ..... 4.000     OK, quedan 82 tokens

  Fuera de COSMOS . no_medido      (system prompt, tools, MCP)

  Lo más caro de la entrada:
    1.  3.059 tok  catálogo visible
    2.  520 tok  índice de galaxia
    3.  77 tok  oceano/irreversible
```

**Entrada 3.918 < 4.000. Verde, con 82 tokens de margen.** El catálogo pasó de 1.713 a 3.059 tokens
(78 % de la entrada, era el 67 %); el índice no se movió porque los sistemas solares y los océanos son
los mismos. La **descarga** sube de 64,5 % a 66,6 %: sigue lejos del 0,95 de `PLAN-MAESTRO.md` §5 por
el mismo motivo que dijo la tanda 1 —los cuerpos son fichas, no skills escritas— aunque el universo
creció de 7.250 a 11.725 tokens, que es la dirección correcta.

### El E19 de la tanda 1 ya no existe

La tanda 1 cerró con **68 errores E19** porque `cosmos.toml` fijaba un solo manifiesto para los dos
árboles. Ese arreglo ya está hecho: existe `galaxia.toml` con su propio `destino` y `manifiesto`.
Compilé la vista plana de la galaxia con él:

```
$ python3 -m cosmos compilar galaxia --config galaxia.toml
CREAR .cosmos/vista-galaxia/aflplusplus … CREAR .cosmos/vista-galaxia/zephyr
$ python3 -m cosmos validar galaxia --config galaxia.toml
COSMOS  verde  0 errores
$ python3 -m cosmos validar ejemplo
COSMOS  verde  0 errores
$ python3 -m unittest discover -s tests -q
Ran 47 tests in 0.400s
OK (skipped=1)
```

**Los dos árboles en verde a la vez y los 47 tests pasando.** Es lo que la tanda 1 demostró con un
config del scratchpad; ahora está en el repositorio y no hace falta el truco.

### E15 (índice) no pidió regenerar

`generar` no se ejecutó porque no hacía falta: el índice lista galaxia, sistemas solares y océanos, y
ninguno de los tres cambió en esta tanda. E15 sale verde tal cual.

## 5. Decisiones dudosas — lo que hay que revisar

Ordenadas por lo cerca que estuve de equivocarme.

1. **`usa:` está en la spec y no en el código.** `spec/COMPOSICION.md` lo define con su validación
   (E20) y puse `usa:` en 12 pueblos. `cosmos/validar.py` lo rechazó con **24 errores E00**: `'usa'
   debe ser texto` y `campo no permitido para pueblo: 'usa'`. Quité el campo y moví la composición al
   cuerpo en prosa. **Es un desajuste spec↔código, no un error mío ni del árbol**, y hoy significa que
   la composición declarada no se puede escribir. Para Codex: `_ESQUEMA` no admite `usa` en ningún
   nivel y E20 no está implementada. Es el hallazgo más accionable de esta tanda.
2. **`casdoor` entra desde SEGUNDA fila**, rompiendo la regla que la tanda 1 aplicó («de la segunda
   fila no entró nada»). Motivo: el hueco de identidad de `saas` **no tiene ningún candidato de
   primera fila** en todo el barrido, y el único de multi-cliente tenía 16 estrellas y un año parado.
   Preferí un pueblo declarado como frágil a un hueco silencioso. Si al probarlo no convence, sale y
   el hueco se declara.
3. **En `ciberseguridad` entraron 8 pueblos de segunda fila.** Justificación: las 12 de primera no
   cubrían continentes enteros. Sin `bloodhound` no hay post-explotación; sin `lynis` no hay
   endurecimiento; sin `defectdojo` y `atomic-red-team` el continente `gobierno` no existiría. Es una
   desviación consciente del reparto de la tanda 1 y la digo, no la disimulo.
4. **Bibliotecas como pueblo.** El criterio 1 dice «herramienta, script o validador», y `libsodium`,
   `openzeppelin-contracts`, `tokio` y `scipy` no se invocan como comando: se importan. Entran por
   precedente de la tanda 1 (`ccxt`, `polars`, `sharp`, `sentence-transformers`) y porque su valor
   está en lo que **evitan escribir**. Leído en estricto, salen los cuatro.
5. **Herramientas de doble uso.** `metasploit`, `sqlmap`, `impacket`, `bloodhound` y `pwntools` entran
   con el contexto legítimo declarado en su propio cuerpo, y la estrella del nicho —que lleva el
   límite— se carga siempre con ellas. `mimikatz`, `sliver`, `hashcat` y `thc-hydra` quedan fuera: su
   hueco ya está cubierto y son las que peor envejecen si el alcance no está clarísimo.
6. **`ghidra` acabó en `analisis/malware`, no en `ofensiva/codigo-ofensivo`**, que es donde lo ponía
   su barrido. Motivo: aquí el uso mayoritario es entender una muestra ajena, que es defensivo, y así
   `codigo-ofensivo` queda coherente con dos pueblos (encontrar la entrada que rompe, armar el
   exploit). Es defendible al revés.
7. **`gobierno` queda con 2 pueblos directos y sin país.** Es legal (`rango(padre) < rango(hijo)`,
   estrictamente menor) y evita un nivel de un solo hijo, pero es el continente más pobre de los
   cuatro: falta el navegador de la matriz pública de técnicas, fuera por presupuesto.
8. **`zephyr` gana a `freertos` en un empate que el propio barrido declara empate.** Entró uno solo
   por presupuesto de catálogo. El criterio está escrito en su cuerpo: proyecto nuevo que quiere pilas
   incluidas, este; base de código existente o núcleo lo más pequeño posible, el otro. Si el trabajo
   real es lo segundo, la decisión correcta es la contraria.
9. **`bevy` entra pese al aviso de máquina.** Su primera compilación tarda minutos y aprieta el
   enlazado en 8 GB; la alternativa mínima en C arranca en segundos. Entra porque el hueco que ocupa
   es la arquitectura (entidad-componente-sistema), no el rendimiento de compilación. Si la máquina
   manda, sobra y entra la otra.
10. **`mermaid` y `d2` entran los dos**, igual que la tanda 1 hizo con `claude-seo-ai` y
    `geo-optimizer`. La frontera —dentro del texto vs fichero propio que se mantiene años— está en el
    cuerpo de cada uno. Si al usarlos no aguanta, sobra `d2`.
11. **`ort` y `fossology` entran los dos.** Es el caso más frágil de esta tanda: el segundo solo
    aporta la interfaz de revisión humana sobre el mismo trabajo. Entra por el criterio 2 («si empatan
    de verdad, entran los dos y se dice cuándo usar cada uno»), pero es la primera línea que quitaría
    si hace falta margen.
12. **Los mares crecieron y eso tiene un precio que no es de tokens.** `ast-grep`, `difftastic`,
    `openrewrite`, `serena` y la inyección de fallos viven ahora nombrados en `criterio` y `pruebas`.
    Cuestan **0 tokens de entrada**, pero **no aparecen en el catálogo**: no se pueden descubrir
    mirando el árbol, solo se cargan cuando el `moja` toca un fichero de su tipo. Es exactamente el
    compromiso que la tanda 1 anotó con `stryker-js` y `mutmut` (su punto 12), ahora con cinco
    herramientas más. Si se quiere que sean encontrables, hay que subirlas a pueblo y pagar su línea.
13. **El margen es de 82 tokens y eso es poco.** La palanca más barata si hace falta espacio:
    renombrar el país `cadena-de-suministro` a `suministro` ahorra **16 tokens** (su ruta cuesta 9 por
    pueblo). No lo hice por no romper la nomenclatura que fijó la tanda 1, pero está medido y listo.
14. **Compilé la vista plana, que escribe fuera de `galaxia/` y `registro/`.**
    `.cosmos/vista-galaxia/` (ignorado por git) y `.cosmos/compilado-galaxia.json` (versionado). Es el
    artefacto propio de la galaxia, es la acción literal que pide E19, y `galaxia.toml` existe justo
    para que no pise al ejemplo — comprobado: `ejemplo` verde y 47 tests en verde. Aun así, es una
    escritura fuera del boundary literal del encargo y por eso está aquí. Revertir ese fichero
    devuelve `validar` a rojo con 127 errores E19.
15. **Ningún pueblo de esta tanda se ha ejecutado.** El criterio 5 («se ha usado una vez») **no se
    cumple para los 61**. Los barridos son metadata verificada en vivo contra la API (estrellas,
    licencia, última publicación), no prueba de campo, y sus propios autores lo dicen. Vale igual para
    la tanda 1. Es la deuda pendiente del universo entero, no de esta tanda.

## 6. Huecos declarados (nuevos, para la fase 5)

- **Aislamiento por inquilino / multi-cliente** en `saas`: sin candidato con tracción y mantenimiento.
- **Respuesta a incidentes** (SIEM/XDR, orquestación de casos) en `ciberseguridad`: los cuatro
  candidatos tienen la capa gratuita sin verificar contra su documentación de precios de hoy. **No se
  promete ninguno a un cliente sin comprobarlo en el momento.**
- **Marco de técnicas** (navegar y anotar la matriz pública) en `ciberseguridad/gobierno`.
- **Auditoría de contraseñas autorizada**: subinvestigada, no descartada por calidad.
- **Validación en frontera por lenguaje** en `codigo-defensivo`: puede que ya no exista como categoría
  de herramienta —cada framework trae la suya— y convenga documentarlo como patrón.
- **Testing automatizado específico de videojuegos**: el barrido no encontró ganador.
- **Sonda de depuración y analizador lógico** en `embebidos`: existen y son buenos, pero **exigen
  hardware físico** (sonda SWD/JTAG desde ~5 €, analizador lógico aparte). No es un rechazo, es una
  compra pendiente de decidir.
- **Colas del ecosistema de la web** (grafos de trabajos, panel de la cola muerta) en `automatizacion`.
- Siguen abiertos de la tanda 1: rendimiento dentro del buscador, pasarelas de pago europeas, CRO,
  datos de mercado de renta variable, dimensionamiento por operación, métricas de negocio,
  descubrimiento de APIs públicas.

## 7. Ficheros

Escrito dentro de `galaxia/` y de `registro/`. `cosmos/`, `tests/`, `ejemplo/` y `cosecha/` intactos
(única excepción declarada en §5.14: el artefacto de compilación de la propia galaxia).

```
galaxia/continentes/ciberseguridad-*.md     4   (nuevo directorio)
galaxia/paises/ciberseguridad-*.md         10   (2 recolocados, 8 nuevos)
galaxia/pueblos/<n>/SKILL.md               61   nuevos  +  6 recolocados
galaxia/agua/mar-criterio.md                    ampliado
galaxia/agua/mar-pruebas.md                     ampliado
```

Borrado: `galaxia/paises/ciberseguridad-analisis-de-codigo.md`, renombrado a
`ciberseguridad-vulnerabilidades.md` bajo el continente `analisis`.

Cero credenciales, cero nombres de cliente, cero dominios, cero datos personales en ningún nodo.
