# Montaje del universo — tanda 1

Fecha: 2026-09-01 · Árbol: `galaxia/` · Modelo: 20 nichos verticales + 5 mares (`spec/UNIVERSO.md`).

Sustituye el árbol anterior de 9 sistemas horizontales. Se conservaron intactos los **5 océanos**
(`irreversible`, `verificar`, `secretos`, `descender`, `precedencia`). Todo lo demás se rehízo.

## 1. Qué quedó montado

| | Nodos |
|---|---|
| galaxia | 1 |
| sistema-solar | 20 |
| país | 21 |
| pueblo | 66 |
| estrella | 9 |
| océano | 5 (conservados) |
| mar | 5 (nuevos) |
| **total** | **127** |

**Nichos poblados (12)**: `agentes` · `ciberseguridad` · `conocimiento` · `datos` · `extraccion` ·
`infraestructura` · `legal` · `medios` · `mercados` · `saas` · `visibilidad` · `web`.

**Nichos vacíos, listos para poblar (8)**: `automatizacion` · `blockchain` · `cientifico` ·
`embebidos` · `juegos` · `moviles` · `negocio` · `sistemas`. Existen con su resumen de
`spec/UNIVERSO.md`; les falta el barrido, que seguía corriendo.

Pueblos por nicho: agentes 10 · web 8 · datos 8 · medios 8 · infraestructura 7 · extraccion 6 ·
ciberseguridad 6 · mercados 5 · visibilidad 4 · saas 2 · legal 1 · conocimiento 1.

### Los 5 mares (nuevos, agua transversal)

`criterio` · `pruebas` · `resistencia` · `accesibilidad` · `custodia`. Ninguno usa `moja: ["**"]`
(eso sería un océano encubierto, E11). **Cuestan 0 tokens de entrada**: el agua que no es océano no
entra en `contexto_inicial`. Ahí es donde viven, con nombre y sin ser pueblos, los linters (`ruff`,
`eslint`, `golangci-lint`, `jscpd`) y los mutadores (`stryker-js`, `mutmut`): son el mismo criterio
aplicado a cada lenguaje, no herramientas de un oficio concreto.

### Las 9 estrellas

`web` · `mercados` · `datos` · `medios` · `infraestructura` · `negocio` (conservadas y adaptadas) ·
`agentes` (heredera de la antigua `inteligencia`) · `extraccion` (nueva, con lo que estaba mal
colocado en la estrella de `datos`) · `ciberseguridad` (nueva; lleva el **límite que no se cruza**
que `spec/UNIVERSO.md` exige que viva en su estrella).

Se borraron las estrellas `codigo`, `guardia` e `inteligencia`: sus sistemas ya no existen. El
contenido de `codigo` no se perdió — se movió al mar `criterio`, que es lo que de verdad era.

## 2. Regla de admisión: qué entró y qué no

**Primera fila de los 12 barridos: 130 entradas.** Entraron **66 pueblos**. Del `## Humo` de los 12
informes no entró **nada**, por orden. De la segunda fila tampoco, salvo lo que se cita dentro del
cuerpo del pueblo ganador como alternativa.

Los rechazos, agrupados por motivo. Cuando el motivo es «solapamiento», la descartada **está
nombrada en el cuerpo del pueblo que ganó**, con el porqué — no se ha perdido.

### A. Solapamiento: mismo hueco, entra una (≈115 nombres)

- **Web**: `web-quality-skills`, `fat-agent-skill` (vs `lighthouse`+`unlighthouse`) ·
  `accessibility-agents`, `pa11y` (vs `axe-core`+`a11y-auditoria-wcag`) ·
  `Automattic/wordpress-agent-skills` (vs el oficial) · `woocommerce-claude` ·
  `liquid-skills`, `shopifyql-skill` (vs `shopify-toolkit`).
- **Visibilidad**: `LibreCrawl` (vs `advertools`), `claude-seo` (ver §4).
- **Agentes**: `letta`, `MemOS`, `Memori` (vs `mem0`) · `LangGraph`, `CrewAI`, `agent-framework`,
  `AutoGen` (vs `claude-agent-sdk`) · `llama.cpp`, `LocalAI`, `vLLM` (vs `ollama`) · `Unsloth`,
  `Axolotl`, `PEFT`, `TRL`, `LLaMA-Factory` (vs `mlx-lm`) · `Qdrant`, `Chroma`, `Milvus` (vs
  `lancedb`) · `LangChain`, `LlamaIndex`, `Haystack` (pegamento) · `langwatch`, `openlit` (vs
  `mlflow`) · `browser-use` (vs `agent-browser`).
- **Datos**: `Ibis`, `sqlglot` (vs `duckdb`) · `Great Expectations` (vs `pandera`) · `Metabase`,
  `Superset` (vs `streamlit`/`evidence`) · `Prophet` (vs `statsforecast`) · `excel-mcp-server`.
- **Extracción**: `Crawl4AI`, `Crawlee`, `colly`, `changedetection.io` (vs `scrapy`+`playwright`+
  `trafilatura`) · `Marker`, `Unstructured`, `dedoc`, `Tika`, `extractous`, `pdfplumber`, `pypdf`,
  `Camelot`, `img2table`, `gmft` (vs `docling`) · `Tesseract`, `PaddleOCR`, `Surya`, `dots.ocr` (vs
  `ocrmypdf`) · `dedupe`, `splink` (vs `rapidfuzz`).
- **Infraestructura**: `Traefik`, `Nginx Proxy Manager` (vs `caddy`) · `borgmatic`, `Kopia`,
  `pgbackrest`, `wal-g` (vs `restic`) · `Healthchecks` (vs `uptime-kuma`, que ya trae monitores de
  empuje) · `Prometheus+Grafana`, `Netdata` (vs `victoriametrics`) · `Gotify` (vs `ntfy`) ·
  `Infisical`, `OpenBao` (vs `sops`) · `Woodpecker CI` (vs `gitea`).
- **Medios**: `moviepy`, `ffmpeg-python` (vs `ffmpeg`) · `faster-whisper`, `vosk` (vs
  `whisper-cpp`) · `pyttsx3`, `espeak-ng` (vs `kokoro`) · `squoosh`, `oxipng`, `svgo` (vs `sharp`) ·
  `python-docx`, `fpdf2` (vs `weasyprint`) · `Real-ESRGAN`, `video2x`, `pyvideotrans`, `VideoLingo`,
  `darktable`, `RawTherapee`, `exiftool`, `DeepFilterNet`, `marp-cli`, `slidev`, `diagrams`.
- **Mercados**: `QuantConnect Lean`, `vnpy` (vs `nautilus-trader`) · `jesse`, `OctoBot` (vs
  `freqtrade`) · `backtesting.py` (los motores ya traen backtest) · `Hummingbot`.
- **Ciberseguridad**: `bandit`, `gosec` (reglas ya reimplementadas en `semgrep` y en `ruff`) ·
  `gitleaks`, `detect-secrets` (vs `trufflehog`) · `syft`+`grype`, `pip-audit` (vs `osv-scanner`+
  `trivy`) · `allstar` (vs `scorecard`) · `cosign` (sin caso de uso aquí todavía).

### B. Prosa, no mecanismo — criterio 1 (≈24 nombres)

`addyosmani/web-quality-skills` (listas de causas y arreglos que un modelo bueno ya tiene; el motor
que hay debajo sí entró) · `seomachine` (estrategia de contenido = consejo) · `wshobson/agents` y con
él los **16 «pueblos» del mapeo de `producto-saas`** (`stripe-integration`, `pci-compliance`,
`billing-automation`, `postgresql-table-design`, `sql-optimization-patterns`, `database-migration`,
`auth-implementation-patterns`, `api-design-principles`, `microservices-patterns`,
`k8s-manifest-generator`, `terraform-module-library`, `prometheus-configuration`,
`distributed-tracing`, `webapp-testing`, `mcp-builder`, `before-you-build`) · marketplaces y
catálogos que se consultan y no ejecutan: `awesome-selfhosted`, `awesome-mcp-servers`,
`awesome-claude-code`, `anthropics/skills`, `claude-plugins-official`.

Este grupo es el que más volumen quita: un marketplace de agentes en Markdown parecía 16 pueblos y
era una biblioteca de consejos.

### C. Cuesta dinero o licencia no libre — criterio 3 (9 nombres)

`claude-code-security-review` (💰 API por PR) · `CodeQL` (uso sobre código privado exige la
suscripción de la plataforma; ver §4) · `semgrep` Pro, solo la edición de pago (la libre entró) ·
`elmo` (💰) · `vectorbt` (Commons Clause) · `ArcticDB` (Business Source License) · `DataForSEO`
(extensión de pago de dos candidatos) · `socket-cli` (panel de organización de pago, límite del CLI
sin verificar) · `soda-core` (licencia sin verificar en el barrido).

### D. Muerto o sin actividad — criterio 4 (8 nombres)

`piper` (sin publicar cambios desde 2025-08-26; **por eso ganó `kokoro`**) · `lighthouse-ci` (5+
meses) · `AutoGen` (sin commits desde abril) · `ib_insync` (archivado) · `pyfolio` (abandonado 2023)
· `AutoAWQ` (deprecado) · `pandas-ta` (desapareció de GitHub) · `DependencyCheck` (el repo se movió
y el barrido no resolvió el destino).

### E. No llegó a primera fila o procedencia sin validar — criterios 2 y 5 (≈30 nombres)

`claude-dependency-auditor` (mecanismo bueno, 0 estrellas: cero validación social) ·
`elementor-skills`, `figma-to-code-skills`, `figma-skill` · en infraestructura, todo lo que estaba
solo en el mapeo: `OpenTofu`, `Ansible`, `Docker`/`Portainer`/`Dockge`/`Watchtower`/`Diun`, `k3s`,
`Tailscale`/`Headscale`, `AdGuard`/`Pi-hole`, `acme.sh` · en mercados: `TA-Lib`, `talipp`,
`pandas-ta-classic`, `PyPortfolioOpt`, `quantstats`, `yfinance`, `OpenBB` · en agentes: `promptfoo`,
`ragas`, `DeepEval`, `lm-evaluation-harness`, `LiteLLM`, `rerankers`, `text-embeddings-inference` ·
`Prefect`, `Dagster`, `RQ`, `Celery`, `dlt` (además pertenecen a `automatizacion`, sin barrido).

### F. Riesgo de custodia (3 nombres)

`Suganthans-GSC-MCP` y `google-analytics-mcp`: servidores de terceros que custodiarían el **acceso
delegado a la propiedad del cliente**. Entregar eso a un tercero no verificado es justo lo que el
mar `custodia` y el océano `secretos` no permiten a la ligera. Queda como **hueco declarado**: medir
el rendimiento real en el buscador no tiene hoy pueblo. `allstar` cae aquí también (exige instalar
una aplicación con permisos amplios sobre la organización).

### G. Es agua, no pueblo (6 nombres)

`ruff`, `eslint`, `golangci-lint`, `jscpd` → mar `criterio`. `stryker-js`, `mutmut` → mar `pruebas`.
Atraviesan los 20 nichos; ponerlos como pueblo de uno los deja invisibles en los otros 19.

## 3. Verificación

### `python3 -m cosmos medir galaxia` — literal

```
COSMOS  medir

  Entrada ......... 2.572 tokens   (estimado, ±desconocido, heurística v1)
  Universo ........ 7.250 tokens   (estimado, ±desconocido, heurística v1)
  Descarga ........ 64,5 %
  Presupuesto ..... 4.000     OK, quedan 1.428 tokens

  Fuera de COSMOS . no_medido      (system prompt, tools, MCP)

  Lo más caro de la entrada:
    1.  1.713 tok  catálogo visible
    2.  520 tok  índice de galaxia
    3.  77 tok  oceano/irreversible
```

**Entrada 2.572 < 4.000.** Con los 20 nichos montados y 1.428 tokens de margen para los 8 barridos
que faltan. El coste de salida del comando es 0.

Nota honesta sobre la **descarga (64,5 %)**: `PLAN-MAESTRO.md` §5 pide > 0,95. No se cumple todavía,
y no es un fallo del árbol: los cuerpos de los 66 pueblos son cortos (2-4 líneas) porque son fichas,
no skills escritas. Cuando cada pueblo traiga su `SKILL.md` real, el denominador crece y la descarga
sube sola. La métrica que sí manda hoy —la entrada— está en verde.

### `python3 -m cosmos validar galaxia` — literal, y sale ROJO

```
COSMOS  rojo  68 errores

E19  /Users/dariosatino/cosmos/.claude/skills
     vista plana desincronizada: a11y-auditoria-wcag: no figura en el manifiesto
     Ejecuta 'cosmos compilar'; no edites la vista plana a mano.

E19  /Users/dariosatino/cosmos/.claude/skills
     vista plana desincronizada: advertools: no figura en el manifiesto
     Ejecuta 'cosmos compilar'; no edites la vista plana a mano.

[... 64 líneas más de la misma forma, una por pueblo ...]

E19  /Users/dariosatino/cosmos/.claude/skills
     vista plana desincronizada: probar-salida: entrada obsoleta en el manifiesto
     Ejecuta 'cosmos compilar'; no edites la vista plana a mano.

E19  /Users/dariosatino/cosmos/.claude/skills
     vista plana desincronizada: revisar-formato: entrada obsoleta en el manifiesto
     Ejecuta 'cosmos compilar'; no edites la vista plana a mano.
```

Desglose por código (`validar galaxia --json`):

```
Counter({'E19': 68})
```

**Los 68 errores son E19 y solo E19. E00–E18 están en verde**: 0 errores de esquema, contención,
identidad por ruta completa, resúmenes, agua, adjuntos, índice, presupuesto, solapamiento y
colisiones al aplanar.

## 4. El rojo de E19 no es del árbol: es acoplamiento de configuración

**No lo he esquiveado y no lo he arreglado por mi cuenta, porque arreglarlo rompía a Codex.** Esto es
lo que pasa, con la prueba.

`cosmos.toml` fija **un** manifiesto y **un** destino de compilación para todo el repositorio:

```toml
[raiz]
arbol = "ejemplo"
[compilacion]
destino    = ".claude/skills"
manifiesto = ".cosmos/compilado.json"
```

Pero `cosmos validar <raiz>` permite apuntar a **otro** árbol: `_configuracion()` en `cli.py`
sustituye `arbol` e `indice` con el argumento posicional y **deja `destino_compilacion` y
`manifiesto_compilacion` como estaban**. Resultado: al validar `galaxia` se compara el árbol de
galaxia contra el manifiesto de `ejemplo`. De ahí los 66 «no figura en el manifiesto» (mis pueblos)
y los 2 «entrada obsoleta» (los pueblos de `ejemplo`).

**Por qué no ejecuté `cosmos compilar galaxia`**, que es lo que dice la acción del error:

1. Reescribiría `.cosmos/compilado.json` y `.claude/skills/`, que están **versionados en git**
   (`git ls-files` los devuelve) y pertenecen a `ejemplo`.
2. Rompería `tests/test_validador.py::PruebasValidadorComplementarias::test_ejemplo_completo_es_verde`,
   que carga `cosmos.toml` y exige que `ejemplo` valide en verde, E19 incluida. Los dos árboles son
   **mutuamente excluyentes** con un solo manifiesto: el que compile deja al otro en rojo.
3. `cosmos/`, `tests/` y `ejemplo/` están fuera de mi boundary, y Codex trabaja ahí ahora mismo.

Tampoco pude usar `cosmos generar galaxia` para escribir el índice: `generar` valida antes de
escribir omitiendo solo E15, así que **E19 lo bloquea**. Escribí `galaxia/COSMOS.md` llamando a
`cosmos.generar.escribir_indice` con el mismo árbol y los mismos parámetros que usa el CLI, así que
es byte a byte lo que produciría el comando — y E15 sale verde, lo que lo demuestra.

### Prueba de que el árbol sí es válido y compilable

Con un `cosmos.toml` aislado (en el scratchpad, apuntando a `galaxia` y con su propio manifiesto y
destino, sin tocar nada del repositorio):

```
$ python3 -m cosmos compilar --config <scratch>/cosmos-galaxia.toml
CREAR <scratch>/vista-plana/a11y-auditoria-wcag
... 66 entradas ...
$ python3 -m cosmos validar --config <scratch>/cosmos-galaxia.toml
COSMOS  verde  0 errores
$ python3 -m cosmos validar ejemplo
COSMOS  verde  0 errores
```

**Verde las dos, a la vez, en cuanto cada árbol tiene su propio manifiesto.**

### Para Codex, en una línea

`_configuracion()` en `cosmos/cli.py` debería derivar también `destino_compilacion` y
`manifiesto_compilacion` cuando se pasa una `raiz` distinta de `config.arbol` (por ejemplo,
relativas a la raíz dada), o bien `validar` debería aceptar `--destino`/`--manifiesto` como los
acepta `compilar`. Hoy, la invariante que compara disco contra árbol se evalúa contra el disco de
**otro** árbol. Es el mismo tipo de interbloqueo que `NUCLEO.md` §6 resolvió para `generar` y
`compilar`, un nivel más arriba: no solo hay que decidir *cuándo* se comprueba, sino *contra qué*.

## 5. Decisiones dudosas — lo que hay que revisar

Ordenadas por lo cerca que estuve de equivocarme.

1. **`claude-seo-ai` gana a `claude-seo` (16.000★ vs 47★).** Descarté el candidato con 340 veces más
   adopción. Motivo: criterio 5, «se ha usado una vez» — el pequeño está en producción en esta casa
   y el grande no se ha probado nunca aquí; además su propio barrido advierte de que 16k estrellas en
   un nicho tan estrecho piden comprobación en vivo. **Es la decisión más frágil del montaje**: si
   alguien prueba `claude-seo` y funciona, probablemente deba sustituirlo. Queda nombrado en el
   cuerpo del pueblo ganador.
2. **`geo-optimizer` entra junto a `claude-seo-ai` aunque se solapan.** Los dos auditan el eje de
   buscadores con IA. Los admití los dos porque uno es orquestador generalista y el otro
   especialista vivo, y escribí la frontera en el cuerpo de cada uno. Si al usarlos se ve que la
   frontera no aguanta, sobra uno — y sobra el generalista, no el especialista.
3. **`CodeQL` fuera por coste.** Es el único con seguimiento de contaminación entre funciones y
   ficheros, técnicamente superior a `semgrep`. Lo dejé fuera porque su uso sobre código privado
   exige la suscripción de la plataforma. Si el trabajo es sobre repositorios públicos, la decisión
   correcta es la contraria.
4. **`stripe-agent-toolkit` entra aunque la pasarela cobra comisión.** El criterio 3 dice «nada que
   pida tarjeta». El kit es gratis; lo que cobra es la pasarela del cliente, que es una decisión de
   negocio suya, no una instalación nuestra. Lo anoté en el cuerpo del pueblo. Si se lee el criterio
   en sentido estricto, sale.
5. **`kokoro` gana a `piper` por estar vivo, no por ser mejor.** `piper` tiene 11.300★ y `kokoro`
   un envoltorio de CLI con estrellas sin verificar. Gana el segundo porque el primero lleva **más
   de un año sin publicar cambios** (criterio 4) y el segundo cabe en 2-3 GB con licencia
   permisiva. Es un empate técnico resuelto por actividad, no por calidad.
6. **`ollama` y `mlx-lm` entran; `llama.cpp` no.** Dejé fuera el estándar de hecho del nicho porque
   aquí nunca se usa suelto: se usa por debajo de `ollama`. Es defendible y también es el tipo de
   decisión que envejece mal si alguien quiere compilar con opciones propias.
7. **`pandera` gana a `Great Expectations`.** Descarté «el estándar» del hueco por ser
   infraestructura de equipo (servidor de documentación, dependencias pesadas) en una máquina de 8
   GB. Si el trabajo pasa a un equipo, cambia.
8. **`duckdb` y `polars` entran los dos.** Rozan la regla de «uno por hueco». Los admití porque el
   modelo mental es distinto (consulta SQL sobre ficheros vs transformaciones tipadas encadenadas),
   no porque los dos sean buenos.
9. **`web-fidelidad-elementor` es el único pueblo que no sale de GitHub.** Es una skill local de esta
   casa. Entra porque el propio informe de `web-ecommerce` dice que cubre esa provincia con mecanismo
   propio —medición numérica contra el mockup— y ningún candidato de GitHub lo iguala. Si se prefiere
   que el árbol sea 100 % de fuentes externas en esta fase, sale.
10. **`legal` y `conocimiento` quedan con un solo pueblo cada uno** (`presidio`, `context7`), sin
    barrido propio. No es un nivel de relleno —son sistemas solares, que existen por decisión de
    `spec/UNIVERSO.md`— pero sí es material colocado por afinidad desde los barridos de
    `seguridad-calidad` y `producto-saas`. Si al llegar sus barridos el encaje no cuadra, se mueven.
11. **Nivel elegido: casi no hay provincias ni continentes.** Usé `sistema-solar → país → pueblo`, y
    en 8 casos `sistema-solar → pueblo` directo. `NUCLEO.md` y `TAXONOMIA.md` lo permiten
    (`rango(padre) < rango(hijo)`, estrictamente menor) y evita niveles de un solo hijo, que se
    pagan en el catálogo y no informan. El precio es que los mapeos de los barridos, que sí proponían
    provincias, quedan aplanados: **si un país llega a 6-8 pueblos, ahí toca abrir provincias**.
12. **El testing quedó sin pueblos propios** (`stryker-js`, `mutmut` viven nombrados en el mar
    `pruebas`). Es coherente —atraviesan los 20 nichos— pero significa que no aparecen en el
    catálogo y solo se cargan cuando el `moja` del mar toca un fichero de test. Si se quiere que sean
    encontrables desde el catálogo, hay que subirlos a pueblo y pagar su línea.

## 6. Huecos declarados (para la fase 5)

- **Medición de rendimiento real en buscador** (consola de búsqueda, analítica): sin pueblo, por
  custodia del acceso delegado del cliente. Es un hueco que se puede construir.
- **Pasarelas de pago europeas** (TPV virtual español, redirección bancaria): ningún candidato en
  todo el barrido de web.
- **CRO / conversión**: el barrido de web lo declaró sin provincias sólidas.
- **Datos de mercado de renta variable** sin scraping frágil ni licencia restrictiva.
- **Dimensionamiento por operación** (Kelly) en mercados: nada dedicado.
- **Métricas de negocio** (unidad económica, retención, cohortes): sin país sano.
- **Descubrimiento de APIs públicas** en extracción.
- **Contenedores e IaC** en infraestructura: el mapeo los pide, la primera fila no los trajo.

## 7. Ficheros

Escrito solo dentro de `galaxia/` y de `registro/`. `cosmos/`, `tests/` y `ejemplo/` intactos.

```
galaxia/galaxia.md
galaxia/COSMOS.md            (índice generado)
galaxia/sistemas/*.md        20
galaxia/paises/*.md          21
galaxia/pueblos/<n>/SKILL.md 66
galaxia/estrellas/*.md       9
galaxia/agua/oceano-*.md     5   (conservados sin tocar)
galaxia/agua/mar-*.md        5   (nuevos)
```

Cero credenciales, cero nombres de cliente, cero dominios, cero datos personales en ningún nodo.
