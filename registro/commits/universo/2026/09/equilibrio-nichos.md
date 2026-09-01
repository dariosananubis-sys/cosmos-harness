# Equilibrio de nichos — los siete oficios flacos, de 4-6 a 9-10

Fecha: 2026-09-01 · Árbol: `galaxia/` · Encargo: subir a 8-12 herramientas los siete oficios más
flacos, sin duplicar nada y sin meter relleno para llegar a un número.

Oficios tocados y punto de partida: `analitica` (4) · `audiovisual` (4) · `ingenieria-datos` (4) ·
`modelos-locales` (5) · `saas` (6) · `moviles` (6) · `cumplimiento` (6).

Contrato aplicado, el de `spec/PUEBLO.md`, en los 29 pueblos nuevos: URL literal · licencia,
estrellas y último push **con fecha de comprobación** · comando de instalación · ejemplo copiable ·
por qué gana al rival **nombrándolo** · y qué no hace bien.

Toda cifra de estrellas, licencia, `pushed_at` y `archived` sale de una llamada en vivo a
`api.github.com/repos/OWNER/REPO` el **2026-09-01**, autenticada con el token del llavero. El token
no se escribió en ningún fichero ni se imprimió. Lo que no se pudo clasificar por API (licencias
`NOASSERTION`) se resolvió leyendo el `LICENSE` real por el endpoint `contents/`, y así se dice en la
ficha.

---

## 1. El antes y el después

```
$ python3 -m cosmos estado          # ANTES
  ciberseguridad 26 · trading 22 · agentes-ia 20 · rendimiento 18 · web 15
  automatizacion 11 · infraestructura 9 · documentos 9 · blockchain 8 · embebidos 8
  visibilidad 7 · juegos 7 · cientifico 7 · extraccion 7
  cumplimiento 6 · saas 6 · moviles 6 · modelos-locales 5
  ingenieria-datos 4 · analitica 4 · audiovisual 4          (mayor 26, menor 4)

$ python3 -m cosmos estado          # DESPUÉS
  ciberseguridad 26 · trading 22 · agentes-ia 20 · rendimiento 18 · web 15
  automatizacion 11 · audiovisual 10 · infraestructura 9 · cumplimiento 9 · saas 9
  modelos-locales 9 · moviles 9 · documentos 9 · ingenieria-datos 9 · analitica 9
  blockchain 8 · embebidos 8 · visibilidad 7 · juegos 7 · cientifico 7 · extraccion 7
                                                            (mayor 26, menor 7)
```

El rango pasa de **26-4** a **26-7**, y ninguno de los siete se acerca al mayor: el techo lo sigue
marcando `ciberseguridad` con 26, que no se ha tocado. La cola de 4 desaparece; el 7 que queda abajo
es de cuatro oficios que **no** estaban en este lote (`visibilidad`, `juegos`, `cientifico`,
`extraccion`).

Pueblos: **209 → 238**.

## 2. Qué entró, oficio por oficio, y por qué gana

### `audiovisual` 4 → 10 · el lote de procesado por lotes

Prioridad del encargo: el lote, no la pieza suelta. Los seis entran con ejemplo que recorre una
carpeta o que se mete en un `for`.

| Pueblo | Hueco que ocupa | A quién gana, nombrado |
|---|---|---|
| `whisperx` | Marca de tiempo por palabra y separación de hablantes | A encadenar a mano `faster-whisper` + `pyannote-audio`: ahí hay que casar dos ejes de tiempo. Lo pedía el propio `whisper-cpp`, que declara que no hace ninguna de las dos cosas |
| `pyscenedetect` | Cortes de plano y troceado por escenas | Al filtro `select='gt(scene,0.4)'` de `ffmpeg`, que da una puntuación por fotograma y obliga a elegir el umbral a ojo |
| `auto-editor` | Quitar silencios y partes muertas | A `silencedetect` de `ffmpeg`, que imprime tiempos en el log y deja el `filter_complex` de decenas de tramos por escribir |
| `ffsubsync` | Cuadrar un subtítulo descolocado | A `ffmpeg -itsoffset`, que aplica desplazamiento constante cuando el desajuste real viene de una diferencia de fotogramas por segundo |
| `ffmpeg-normalize` | Igualar volumen percibido de un lote | A `ffmpeg -af loudnorm` a pelo: aquel estima y corrige en la misma pasada y se desvía; esto hace la doble pasada que la propia documentación del filtro recomienda |
| `demucs` | Separar la voz de la música y del ambiente | A `afftdn` de `ffmpeg`, que resta un perfil de ruido **estacionario** y no puede con música con letra |

### `ingenieria-datos` 4 → 9 · detectar antes que pintar

Prioridad del encargo respetada: los cinco **detectan** que el dato o el SQL están mal; ninguno es
una biblioteca de gráficos.

- `dagster` — orquesta por tabla producida, no por tarea; `asset_check(blocking=True)` **para** la
  cadena en vez de solo registrar el fallo. Gana a `airflow` (46.677★) y a `prefect` (23.752★), que
  orquestan tareas y no saben qué tabla quedó vieja.
- `dlt` — carga con `schema_contract`: una columna nueva en el origen para la carga con un error que
  la nombra. Gana a escribir `requests` + `INSERT` a mano y a `airbyte` por peso.
- `elementary` — pruebas de anomalía sobre el proyecto de `dbt-core` que ya existe: detecta que el
  número **sigue siendo válido y ha cambiado de escala**, que es lo que `dbt test` no ve.
- `sqlfluff` — analiza el SQL por su dialecto real y tras renderizar las plantillas, con código de
  salida. Gana al formateador del editor, que alinea texto sin entender el dialecto.
- `qsv` — valida el CSV **antes** de que exista ningún dataframe. Gana a `csvkit` en tiempo y a
  abrirlo en una hoja de cálculo, que corrige en silencio.

### `analitica` 4 → 9 · métricas en las que se puede confiar

- `marimo` — cuaderno reactivo sin estado oculto, guardado como `.py`. Gana a `jupyter` en lo único
  que decide aquí: un cuaderno clásico puede enseñar la salida de un código que ya no existe.
- `datasette` — un fichero de datos convertido en sitio navegable **y en API JSON** con un comando;
  la misma URL que abre una persona la consulta un agente.
- `rill` — cuadro de mando explorable en un solo binario con DuckDB dentro y **capa de métricas**:
  una definición por métrica, que es el fallo de gobierno que hace que nadie se fíe del panel.
- `papermill` — ejecuta un cuaderno con parámetros y **guarda cada ejecución como prueba**. Gana a
  `jupyter nbconvert --execute`, que ejecuta pero no acepta parámetros.
- `xlsxwriter` — la hoja que el cliente abre de verdad, con fórmulas vivas y gráficos nativos. Gana a
  `openpyxl` cuando solo hay que escribir, y se dice que para **leer** un `.xlsx` gana aquel.

### `modelos-locales` 5 → 9 · con el veredicto de 8 GB en cada ficha

Los cuatro dicen si caben y con qué cuantización, como pedía el encargo:

- `outlines` — restricción durante la generación: la salida no puede romper el esquema. **Es lo que
  hace viables los modelos que sí caben**: un 3B en 4 bits restringido acierta la estructura siempre.
  Gana a `guidance` en integración, y se dice honestamente que `ollama` acepta hoy esquema JSON y
  `llama.cpp` tiene gramáticas — lo que ninguno cubre es expresión regular + gramática libre de
  contexto + tipos de Python en el mismo guion.
- `llm` — el modelo como filtro de shell, con **todo guardado en SQLite**. Coste en memoria: cero, la
  ocupa el modelo de detrás (4 bits, hasta 7B con margen justo).
- `chonkie` — troceado para recuperación sin arrastrar un marco de orquestación entero. Núcleo sin
  modelo (trivial en RAM); el modo semántico carga uno de vectores y ahí valen las reglas de
  `sentence-transformers` (`all-MiniLM-L6-v2`, ~90 MB).
- `mlx-vlm` — cierra el único hueco que faltaba: **visión**. Un modelo de ~3B en 4 bits ocupa 2-2,5 GB
  y va con soltura; 7B en 4 bits ronda 5 GB y deja el sistema al límite; por encima no entra. Y el
  aviso propio de visión: **la imagen también ocupa** —una captura retina son miles de tokens
  visuales—, así que se reescala antes de pasarla.

### `saas` 6 → 9 · los tres huecos que el propio árbol tenía escritos

- `openfga` — `casdoor` decía literalmente «sigue sin pueblo el aislamiento por inquilino». Esto lo
  cierra, y con **pruebas ejecutables**: `fga model test` afirma que el usuario del otro inquilino NO
  ve el documento, y la tubería se pone roja si algún día lo ve. Gana a `casbin` porque modela
  relaciones y no roles sueltos.
- `squawk` — guardarraíl ejecutable de migraciones: detecta el índice sin `CONCURRENTLY`, la columna
  obligatoria y el cambio de tipo que reescribe la tabla. Gana a `ariga/atlas` (8.694★) por encaje, no
  por potencia, y se dice que si hay que gestionar el esquema entero gana Atlas.
- `spectral` — el contrato de API contra reglas propias versionadas, con código de salida. Frontera
  escrita con `openapi-generator`, que ya vive en `documentos`: aquel genera a partir del contrato,
  esto decide si el contrato merece que se genere algo.

**Facturación española**: no se creó ningún pueblo nuevo, a propósito — ver duplicados evitados.

### `moviles` 6 → 9

- `maestro` — no había **ninguna** forma de probar la app en el aparato. Gana a `wix/Detox` (12.022★)
  en alcance: aquel es específico de React Native, este habla con la pantalla y el mismo flujo vale
  para Flutter, RN, Expo y nativo. Aviso de dinero: Maestro Cloud es de pago; `maestro test` local, no.
- `mobsf` — analiza el **paquete compilado**, que es donde está lo que metieron las dependencias.
  Toca el mar `custodia`: una clave incrustada en un APK es pública el día que se publica.
- `compose-multiplatform` — la tercera respuesta al mismo problema que `flutter` y `react-native`, con
  su caso propio escrito: **el proyecto ya es Android nativo** y se empieza compartiendo solo la
  lógica. No contradice a los otros dos, que declaran que entre ellos no hay ganador absoluto.

### `cumplimiento` 6 → 9 · con norma, versión y territorio en cada ficha

Como pedía el encargo, los tres traen los apartados **Norma que cubre** y **Lo que NO comprueba**:

| Pueblo | Norma, versión y territorio | Qué NO comprueba |
|---|---|---|
| `greenmask` | RGPD (UE 2016/679) art. 5.1.c minimización y art. 32.1.a seudonimización; en España, LOPDGDD 3/2018. **Unión Europea** | No busca dónde están los datos personales: la columna que se olvide sale en claro. No mide riesgo de reidentificación — eso es `arx` |
| `reuse` | Especificación **REUSE v3.3** de la FSFE sobre identificadores **SPDX**; evidencia para el Reglamento europeo de ciberresiliencia. **Sin territorio** | No mira dependencias (eso es `ort`/`fossology`) y **no verifica que la licencia declarada sea la verdadera**: solo que se declara |
| `blacklight` | Art. **22.2 LSSI-CE (Ley 34/2002)** + **Guía de cookies de la AEPD** en su edición adaptada al CEPD vigente desde enero de 2023, + arts. 6 y 7 del RGPD. **España** | No valida el banner ni que rechazar sea tan fácil como aceptar, no lee el registro de consentimientos y no emite dictamen |

`blacklight` cierra un hueco que `cookies-declaradas` tenía escrito: «no mira si se cargan terceros
antes del consentimiento (eso es medición en vivo, con el navegador)».

---

## 3. Los duplicados que evité — y son más que los pueblos que escribí

Este es el resultado más caro del encargo. Antes de crear nada, se recorrieron los cuerpos de los
209 pueblos existentes buscando decisiones de exclusión ya escritas. **Catorce candidatos que estaban
en mi lista de partida ya estaban descartados a propósito por un pueblo vivo**, y meterlos habría
dejado el árbol contradiciéndose:

| Candidato descartado | Quién lo excluye, y con qué palabras |
|---|---|
| `moviepy`, `ffmpeg-python` | `ffmpeg`: «Descartados los envoltorios en Python… el error útil lo imprime FFmpeg de todas formas» |
| `ibis`, `sqlglot` | `duckdb`: «Descartada la capa de portabilidad entre motores y el traductor de dialectos» |
| `llama.cpp` | `ollama`: «define el formato GGUF y es el estándar de facto; no entra como pueblo propio porque aquí nunca se usa suelto» |
| `LocalAI`, `vLLM` | `ollama`: el primero se solapa con backends que aquí no se usan; el segundo pide GPU dedicada |
| `qdrant`, `chroma` | `lancedb`: mejores a escala real, pero piden proceso servidor con su RAM en una máquina de 8 GB |
| `promptfoo` | `lm-evaluation-harness`, que gana por correr entero en local sin modelo juez |
| `metabase`, `superset` | `streamlit`: «ninguna de las dos cabe cómoda en un Mac de 8 GB» |
| `syft` | `ort`: «no entra: el inventario ya lo produce el escáner de imágenes del nicho de seguridad» |
| `pa11y` | `axe-core`: «Gana a `pa11y/pa11y` en licencia y en integración» |
| `capacitor` | `react-native`: «no entra como pueblo propio porque es el mismo hueco resuelto por debajo» |
| `PaddleOCR` | `ocrmypdf`: «se anota como alternativa y no como pueblo porque aquí casi todo llega en PDF» |
| `great_expectations` | `pandera`, que lo nombra como el rival al que gana en este entorno |
| `prophet` | `statsforecast`: «Descartado `facebook/prophet` —el modelo de previsión más famoso del sector, y el rival real—» |
| `scancode` | `fossology`, que lo nombra y dice por qué gana |
| `facturae-php`, `tbai-php-lib` y compañía | `gobl`: «quedan citadas y fuera: cubren una jurisdicción cada una y obligan a reimplementar la lógica de negocio por cada país» |

**Sobre la facturación española**, que el encargo pedía citar con fecha: `gobl` ya la cubre entera
—Facturae 3.2.x, Verifactu del RD 1007/2023 y la Orden HAC/1177/2024, y TicketBAI por complemento— y
además ya avisa de lo importante: **las fechas de obligatoriedad se han movido varias veces y hay que
confirmarlas en el BOE o en la sede de la AEAT antes de prometerle una a un cliente**. Añadir una
biblioteca suelta por norma habría contradicho ese pueblo. Comprobado el 2026-09-01: los tres
conversores de `gobl` siguen vivos (`gobl.facturae`, `gobl.verifactu`, `gobl.es.ticketbai`, push
2026-08-17). No se creó pueblo nuevo aquí.

También quedó fuera `soda-core` (2.420★) tras leer su `LICENSE` real por API: es **Elastic License
2.0**, no libre. Su hueco lo ocupa `elementary`, que es Apache-2.0 y vive dentro del proyecto de
`dbt-core` que ya existe. Queda dicho en la ficha de `elementary`.

## 4. Descartados por estar muertos o archivados

Comprobado en vivo el 2026-09-01. **Regla aplicada: archivado o más de un año sin push, no entra.**

| Candidato | Estado medido | Consecuencia |
|---|---|---|
| `facebookresearch/demucs` | **`archived: true`**, push 2024-04-24, 10.358★ | Es el que sale primero al buscar. El pueblo `demucs` apunta al vivo, `adefossez/demucs` (3.148★, push 2026-08-31), y avisa del cambio en la primera línea |
| `rhasspy/piper` | Archivado, push 2025-08-26 | Ya estaba documentado por `kokoro`; no se rescató |
| `Nozbe/WatermelonDB` | push 2025-08-11 → **13 meses** | Ya estaba documentado por `rxdb`; no entra |
| `Rikorose/DeepFilterNet` | Sin push desde octubre de 2024 | Nombrado como rival vencido en la ficha de `demucs` |
| `SYSTRAN/faster-whisper` | Sin commits desde noviembre de 2025 | Nombrado como rival vencido en `whisper-cpp` y usado como término de comparación en `whisperx` |
| `haris-musa/excel-mcp-server` | push 2026-04-12, casi cinco meses | No entra en `analitica`: además `gspread` ya lo tenía descartado |
| `AnswerDotAI/rerankers` | push 2025-12-20, 1.631★ | No entra: `sentence-transformers` ya trae `CrossEncoder`, así que era hueco cubierto **y** proyecto enfriándose |
| `microsoft/react-native-code-push` | archivado (dato del barrido previo) | No se rescató |

Dos que **sí** entraron pese a tener una señal floja, dicho en su propia ficha para que nadie se lo
encuentre después:

- `papermill` — último push 2026-07-06 (dos meses). Estable y muy usado; la ficha dice que no esperar
  novedades.
- `blacklight` — **240★ y un solo laboratorio detrás**. Es el único del barrido que mide rastreadores
  antes del consentimiento, y la ficha lo llama «el pueblo más frágil de su nicho — revisar cada
  trimestre».

## 5. Licencias que la API no clasifica, resueltas leyendo el fichero

`NOASSERTION` en la API no significa código cerrado, significa que GitHub no pudo clasificar el
fichero. Se leyeron cinco por el endpoint `contents/`:

| Repositorio | Lo que dice el fichero real |
|---|---|
| `slhck/ffmpeg-normalize` | **MIT** (cabecera propia en `LICENSE.md`) → entra |
| `dathere/qsv` | **MIT** (`COPYING`; antes doble con Unlicense) → entra |
| `tuist/tuist` | MIT salvo `server/` y `kura/` → no se usó al final |
| `sodadata/soda-core` | **Elastic License 2.0** → **descartado**, no es libre |
| `fsfe/reuse-tool` | Sin `LICENSE` en la raíz; su carpeta `LICENSES/` trae `GPL-3.0-or-later`, `Apache-2.0`, `CC-BY-SA-4.0` y `CC0-1.0` → entra, con la licencia escrita en la ficha |

Y una URL que cambió de sitio: `chonkie` vive hoy bajo otra organización (`chonkie-inc` redirige a
`feyninc`). Queda avisado en su ficha, igual que `react-native` avisa del suyo.

## 6. Ninguno se queda por debajo de 8

El encargo permitía quedarse en 7 si un oficio no daba más. **No hizo falta**: los siete llegan a 9,
y `audiovisual` a 10. Lo que sí se aplicó fue el freno contrario, el de no rellenar. De la lista de
partida entraron **29** y quedaron fuera **30 candidatos nombrados**: 21 por duplicar un hueco que un
pueblo vivo ya tenía declarado (tabla del apartado 3), 1 por licencia no libre (`soda-core`) y 8 por
estar archivados o enfriándose (tabla del apartado 4). Ninguno salió por falta de sitio.

Huecos que **siguen vacíos** y que no se taparon con relleno, porque no hay candidato bueno:

- **Doblaje extremo a extremo sin coste**: `VideoLingo` (18.315★) necesita una API de LLM para
  traducir y `pyvideotrans` (18.856★) es GPL con la documentación en chino y orientado a interfaz
  gráfica. Las piezas ya están en el árbol (`ffmpeg` + `whisper-cpp` + `kokoro`); el orquestador
  gratuito y maduro, no existe.
- **Accesibilidad dentro de `cumplimiento`**: el motor (`axe-core`), el barrido del sitio entero
  (`unlighthouse`) y los guiones de foco y reflow (`a11y-auditoria-wcag`) viven en `web`, y el `usa:`
  de `cumplimiento` ya apunta ahí. `pa11y` no entra porque `axe-core` lo declara vencido. No se
  duplicó nada.
- **Retención de datos y solicitudes de derechos (DSAR)**: sin candidato, como ya decía el barrido de
  `legal.md`.
- **Cohortes y unidad económica** (`analitica`): sigue sin estándar vivo; hoy se construye sobre SQL.

## 7. Verificación

```
$ python3 -m cosmos generar && python3 -m cosmos compilar && python3 -m cosmos validar
COSMOS  verde  0 errores

$ python3 -m cosmos medir
  Entrada base .... 1.609 tokens
  Peor nicho ...... 2.383 tokens   (ciberseguridad, 26 pueblos)
  Agua condicional  961 tokens
  Peor con agua ... 3.344 tokens
  Presupuesto ..... 4.000     OK, quedan 656 tokens en el peor caso con agua
```

**Verde, bajo presupuesto, y el peor nicho sigue siendo `ciberseguridad`**, que no se tocó. `E17` no
saltó: solo compara nodos co-cargables (océano, mar, lago, estrella) y un pueblo no lo es — aun así
ninguna ficha nueva reutiliza las frases de sus vecinas, que se leyeron enteras antes de escribir.

### Lo que estos 29 pueblos cuestan de verdad: cero a quien no entre en su oficio

Medido, no supuesto. El catálogo se materializa por nicho, así que se midió nicho a nicho:

```python
from cosmos.medir import catalogo_visible, contar_aprox
# catalogo_visible(arbol, None)   -> la parte que se paga siempre (sin pueblos)
# catalogo_visible(arbol, [n])    -> esa parte + los pueblos del nicho n
```

```
base sin ningún nicho activo ......  551 tok
solo ciberseguridad .............. 1.326 tok   -> 775 tok de sus 26 pueblos
solo audiovisual ...................  846      -> 295 de sus 10
solo modelos-locales ...............  834      -> 283 de sus  9
solo ingenieria-datos ..............  832      -> 281 de sus  9
solo analitica .....................  821      -> 270
solo cumplimiento ..................  821      -> 270
solo saas ..........................  803      -> 252
solo moviles .......................  787      -> 236
```

Ninguno de los siete llega a la mitad de lo que cuesta `ciberseguridad`. Quien trabaje en `web` no
paga un solo token por los diez pueblos de `audiovisual`.

### Un dato que NO es mío, y conviene que no se me atribuya

El presupuesto libre bajó de **943 a 656 tokens** entre la medición inicial y la final. **No es por
estos 29 pueblos.** El aumento está entero en la parte base del catálogo, y se midió:

```
$ tokens del catálogo base ...................... 551
$ de ellos, líneas que empiezan por "rio/" ...... 287   (14 ríos)
$ catálogo base sin los ríos .................... 265   (= lo que había antes)
```

Los 14 `rio` y 6 `lluvia` los añadió el agente que trabaja en la taxonomía en paralelo, y sí se pagan
en la entrada de todo el mundo. Se deja anotado, no corregido: `cosmos.toml`, `cosmos/` y `spec/`
están fuera de mi alcance en este encargo.

## 8. Alcance tocado

Escrito **solo** en `galaxia/pueblos/<nombre>/SKILL.md` de los 29 nuevos y en este `registro/`. No se
tocó `cosmos/`, `tests/`, `spec/`, `galaxia/sistemas/`, `galaxia/agua/` ni `cosecha/`. Tampoco hizo
falta crear ningún `pais` nuevo: `spec/FRONTMATTER.md` permite que un pueblo cuelgue directamente de
su sistema solar (`rango(padre) < rango(hijo)`, estrictamente), y crear niveles intermedios con un
solo hijo es fuga pura.

Los 29, con su padre:

```
audiovisual/voz    whisperx · ffmpeg-normalize · demucs
audiovisual/video  pyscenedetect · auto-editor · ffsubsync
ingenieria-datos   dagster · dlt · elementary · sqlfluff
ingenieria-datos/motor                                        qsv
analitica          papermill · xlsxwriter
analitica/cuadros-de-mando                                    marimo · datasette · rill
modelos-locales/servir       outlines · llm · mlx-vlm
modelos-locales/recuperacion chonkie
saas               openfga · squawk · spectral
moviles            maestro · mobsf · compose-multiplatform
cumplimiento       blacklight
cumplimiento/datos-personales  greenmask
cumplimiento/licencias         reuse
```

`git status` confirma 29 directorios nuevos bajo `galaxia/pueblos/` y una entrada nueva en
`registro/`. El resto de lo modificado en el árbol (`cosmos.toml`, `cosmos/*.py`, `spec/*.md`,
`galaxia/agua/rio-*.md`, `tests/`) es del agente de taxonomía, no de este encargo.
