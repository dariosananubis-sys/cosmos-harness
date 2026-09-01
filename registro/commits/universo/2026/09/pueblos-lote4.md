# Pueblos lote 4 — de prosa a herramienta usable: 8 nichos, 48 pueblos

Fecha: 2026-09-01 · Árbol: `galaxia/` · Nichos: `embebidos` (8), `blockchain` (8), `juegos` (7),
`cientifico` (7), `moviles` (6), `ingenieria-datos` (4), `audiovisual` (4), `analitica` (4).
Continuación de [`pueblos-lote1.md`](pueblos-lote1.md): mismo contrato, mismo estilo.

Contrato aplicado, el de `spec/PUEBLO.md`: cada cuerpo trae ahora (1) URL literal del repositorio
con licencia, estrellas y último push **con fecha de comprobación**; (2) comando de instalación en
bloque de código; (3) ejemplo mínimo copiable y pegable; (4) por qué este y no el rival,
**nombrándolo**; (5) lo que NO hace bien — el aviso que evita el falso verde.

## 1. Cuántos y dónde

**48 pueblos reescritos**, todos con cuerpo nuevo y frontmatter intacto:

- **`embebidos` (8)**: esp-idf, esphome, freertos, micropython, mosquitto, platformio, probe-rs, zephyr.
- **`blockchain` (8)**: foundry, slither, echidna, mythril, openzeppelin-contracts, viem, anchor, ponder.
- **`juegos` (7)**: godot, bevy, raylib, phaser, tiled, libresprite, miniaudio.
- **`cientifico` (7)**: pixi, dvc, hydra, reprozip, snakemake, dask, scipy.
- **`moviles` (6)**: flutter, react-native, expo, fastlane, tauri, rxdb.
- **`ingenieria-datos` (4)**: duckdb, polars, dbt-core, pandera.
- **`audiovisual` (4)**: ffmpeg, whisper-cpp, kokoro, reel-a-texto.
- **`analitica` (4)**: streamlit, evidence, gspread, statsforecast.

Escrito **solo** dentro de `galaxia/pueblos/<nombre>/SKILL.md` de esos 48 y en este `registro/`.
Ningún fichero fuera del boundary: el guion de escritura aborta si el `padre` del pueblo no empieza
por uno de los ocho nichos.

Medición del contrato sobre los 48:

```
  47/48  url http(s)        (el 48º es reel-a-texto: herramienta propia, la "URL" es cosecha/…)
  48/48  bloque de código
  48/48  comando de instalación
  48/48  ejemplo mínimo copiable
  47/48  datos de vida fechados 2026-09-01
  48/48  rival nombrado + apartado de "lo que no hace bien"
```

Ningún `resumen` se tocó: los 48 ya cabían en 120 caracteres y distinguían de su vecino.

## 2. Verificación de los datos

Cupo de WebSearch agotado (dado en el encargo). Todo se comprobó en vivo el **2026-09-01** contra
`api.github.com` con token autenticado leído del llavero (`security find-internet-password -s
github.com -w`, nunca impreso ni escrito a fichero), por `GET /repos/{owner}/{repo}` —
5.000 peticiones/hora, sin la limitación de ráfaga de `/search`. De cada repo: `stargazers_count`,
`pushed_at`, `license.spdx_id` y `archived`.

**Los 47 repos públicos citados se resolvieron con éxito.** Además se comprobó con `curl` que
resuelven las 10 URL publicadas que no son un repositorio (instaladores, pesos de modelo, CDN):
todas 200/206.

Hallazgos de la verificación que cambiaron lo que dice una ficha:

| Hallazgo | Dónde | Qué se hizo |
|---|---|---|
| `facebook/react-native` responde **301**, no 404 como decía el research | `react-native` | La ficha dice «redirección permanente» y apunta a `react/react-native` (126.472★) |
| `rhasspy/piper` está **archivado** (push 2025-08-26) | `kokoro` | Se nombra como rival y se dice que está archivado, no solo «parado» |
| `hexgrad/kokoro` **tampoco está vivo** (push 2025-08-06, casi 13 meses) | `kokoro` | Ver §4: la ficha lo declara y separa modelo de ejecutor |
| 7 repos con licencia `NOASSERTION` en la API | esphome, micropython, mosquitto, miniaudio, tiled, ffmpeg, viem | Se resolvió el fichero real por `GET /repos/…/license` y se cita la licencia con la nota de por qué la API no la detecta |

## 3. Avisos propios de cada nicho, aplicados

- **`embebidos`** — los 8 marcan si **necesitan hardware físico**, con el coste concreto cuando es
  una barrera de euros (sonda SWD ~5 €, placa ESP32 ~3 €). Es una barrera distinta del dinero y
  evita perder una tarde. `zephyr` es el único con salida honesta sin placa (`qemu_x86`,
  `native_sim`) y se dice.
- **`blockchain`** — las cuatro herramientas de auditoría dicen **qué clase de fallo detectan y cuál
  no**: `slither` patrones sobre fuente, `echidna` la secuencia que rompe una invariante que tú
  escribiste, `mythril` caminos sobre bytecode con el corte por tiempo que produce el falso verde,
  `foundry` fuzzing de una función y no una auditoría. Los 4 que exigen gastar comisión de red
  (`foundry --broadcast`, `viem` al firmar, `anchor deploy` con su depósito de renta, `ponder` con
  la cuota de RPC) lo dicen con esas palabras. Y las 3 fichas centrales repiten la premisa: un fallo
  desplegado no se parchea, se abandona el contrato.
- **`juegos`** — `godot`, `bevy` y `phaser` nombran a **Unity y Unreal** y dicen el modelo de cobro
  (licencia por ingresos y 5 % de regalías), porque eso se decide al elegir motor, no al publicar.
  `libresprite` dice los ~20 $ de Aseprite; `miniaudio` dice que FMOD y Wwise son de pago.
- **`cientifico`** — prioridad a lo que fija entorno, semilla y procedencia. Se dice dónde *no*
  llega cada uno: `pixi` bloquea el paquete pero no la semilla ni la BLAS; `hydra` **registra** la
  semilla y no la siembra; `dvc` decide por `deps` declaradas y da verde con un `deps` incompleto;
  `snakemake` decide por fecha y no por hash; `scipy` da distintos últimos decimales según la BLAS.
- **`moviles`** — los 5 que publican dicen que **publicar cuesta dinero**: cuota anual de
  desarrollador de Apple y alta única de Google. `expo` separa lo que cuesta Expo (plan de EAS) de lo
  que cuestan las tiendas, y da la salida a coste cero (`expo run:*` local).
- **`ingenieria-datos`** — prioridad a lo que **detecta** que el dato está mal: `pandera` y los
  `tests:` de `dbt-core` llevan el peso, y la ficha de `dbt-core` marca su falso verde más caro
  (`dbt run` verde no dice nada de la calidad del dato; el que la mide es `dbt test`, comando aparte).
- **Mac de 8 GB** — marcado en 20 fichas: reserva de memoria de Ray frente a Dask, `memory_limit` de
  DuckDB, enlazado de Bevy, `n_workers` de Dask, `large-v3` de whisper, Metabase/Superset descartados,
  Electron frente a Tauri, simulador iOS + emulador Android a la vez.

## 4. Los que ya no merecían estar (no se han borrado)

Se dicen, como pidió el encargo. Ninguno se ha tocado más allá de escribir el aviso en su cuerpo.

1. **`kokoro` — el más serio.** El repositorio del modelo, `hexgrad/kokoro`, tiene su último push el
   **2025-08-06**: casi trece meses parado. Su propia ficha lo justificaba diciendo que ganaba a su
   rival «porque aquel lleva más de un año sin publicar cambios, y el cuarto criterio de admisión
   pide que esté vivo» — **el criterio que invocaba lo incumple él mismo**. Se ha reescrito
   separando modelo de ejecutor: lo que se instala y se ejecuta es `thewh1teagle/kokoro-onnx`
   (MIT, 2.694★, push 2026-08-19), que sí está vivo; el modelo se cita como lo que es. Entra porque
   hoy no hay alternativa local, gratis y de esa calidad que cumpla el criterio (`piper` archivado,
   `coqui-ai/TTS` muerto con la empresa cerrada, `espeak-ng` robótico). **Decisión de admisión
   pendiente de Darío**, no auto-revertida: o se acepta la excepción escrita, o el pueblo sale.
2. **`reprozip` — 362★ y push 2026-02-04** (siete meses). Y, peor que el ritmo: **su trazador exige
   Linux** (`ptrace`), así que en el Mac de 8 GB no puede empaquetar nada nativamente. Se ha
   reescrito para que entre como sello puntual de una ejecución, no como pieza del flujo diario, con
   sus cuatro límites escritos (no captura red, ni GPU, no sustituye a `pixi`). Es el candidato más
   claro a salir si el nicho necesita el hueco.
3. **`libresprite` — se quedó en el Aseprite de 2016** y lleva dos meses y medio sin push. Cumple el
   criterio de coste cero, y la ficha dice sin adornos que si el trabajo es producción diaria de arte
   pixel los 20 $ de Aseprite se amortizan el primer día. Es un pueblo de criterio, no de calidad.
4. **`mythril` — push 2026-04-27**, cuatro meses. Vivo, pero no de los que publican cada semana; se
   dice en la primera línea. Se mantiene porque cubre el único hueco que `slither` y `echidna` no
   pueden: auditar cuando solo hay bytecode desplegado.

Ninguno de los 48 se ha borrado. Los cuatro llevan el aviso dentro de su propio cuerpo.

## 5. Lo que no se pudo verificar

- **Nada se ha instalado ni ejecutado.** Los comandos publicados son los de la documentación oficial
  de cada proyecto, comprobados como URL cuando descargan algo; no hay evidencia de ejecución real en
  esta máquina para ninguno de los 48, y por eso ninguna ficha la reclama.
- **`reel-a-texto`** es herramienta propia: sus tres guiones (`cosecha/analyze-reel.sh`,
  `extract_frames.py`, `ig-dl.sh`) se leyeron para sacar el uso real, las salidas y los códigos de
  retorno, pero **no se ejecutaron** — habría requerido una sesión de red social iniciada. Es el
  único pueblo del lote sin URL http(s) y sin dato de vida fechado, por naturaleza.
- **Licencias dobles**: `mosquitto` (EPL-2.0/EDL-1.0), `miniaudio` (dominio público / MIT-0),
  `tiled` (GPL-2.0 el editor / BSD-2 `libtiled`), `ffmpeg` (LGPL-2.1+ o GPL-2+ **según cómo se
  compile**) y `viem` (MIT en el repo, `NOASSERTION` en la API). Se cita el fichero de licencia de
  cada uno y se dice que hay que leerlo antes de redistribuir; **no se ha auditado su texto legal**.
- La afirmación de que `rxdb` tiene complementos de pago se comprobó contra su README
  («Buy access to the premium plugins»), y los nombres de sus plugins contra
  `GET /repos/pubkey/rxdb/contents/src/plugins`. No se ha comprobado el precio ni qué complemento
  concreto es premium hoy.

## 6. Validar y medir

`galaxia.toml` **desapareció a mitad de trabajo**: otro agente en paralelo reestructuró la
configuración (`galaxia.toml` → borrado, `cosmos.toml` ahora apunta al árbol real, `ejemplo.toml`
nuevo). El comando del encargo (`--config galaxia.toml`) ya no resuelve; la salida de abajo es la de
`cosmos.toml`, que es el nuevo por defecto y apunta a la misma galaxia.

```
$ python3 -m cosmos validar
COSMOS  rojo  2 errores

E17  agua/oceano-verificar.md
     solapamiento 33.3% entre mar/pruebas y oceano/verificar
E17  estrellas/web.md
     solapamiento 100.0% entre mar/accesibilidad y estrella/web
```

```
$ python3 -m cosmos medir
  Entrada base .... 1.128 tokens
  Peor nicho ...... 1.771 tokens   (ciberseguridad, 26 pueblos)
  Agua condicional  817 tokens
  Peor con agua ... 2.588 tokens
  Universo ........ 66.539 tokens
  Descarga ........ 97,3 %
  Presupuesto ..... 4.000     OK, quedan 1.412 tokens en el peor caso con agua
```

**Bajo presupuesto**, con 1.412 tokens de margen en el peor caso. El `Universo` sube de 22.103 a
66.539 tokens por los cuerpos de este lote y los de los otros tres agentes — y **no cuenta para el
presupuesto**: sólo el `resumen` entra en el catálogo (`spec/PUEBLO.md`, «el presupuesto no cambia»).
La descarga sube del 92,0 % al 97,3 % justamente por eso.

**Los 2 errores no son de este lote.** Ambos son `E17` de solapamiento entre `agua/` y `estrellas/`,
fuera del boundary de este trabajo; ningún error toca ninguno de los 48 pueblos (comprobado filtrando
la salida por sus rutas: cero coincidencias).

Aparte, durante el trabajo aparecieron **201 errores `E19` («vista plana desincronizada»)** al
invocar con el config viejo: son efecto de la reestructuración en paralelo — el manifiesto
`.cosmos/compilado-galaxia.json` fue borrado y `.claude/skills` quedó obsoleto. Se cierran con
`cosmos compilar`, que pertenece a quien está haciendo esa reestructuración; **no se ha ejecutado
desde aquí** para no pisar su trabajo. Con `cosmos.toml` no aparecen.
