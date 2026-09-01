# `trading` a fondo — de 5 pueblos a 22, con su propio código dentro

Fecha: 2026-09-01 · Árbol: `galaxia/` · Config: `galaxia.toml` · Continuación de
[`montaje-tanda-2.md`](montaje-tanda-2.md): mismos criterios, mismo estilo de resumen, mismo tipo de
sección de dudas.

Encargo de Darío, literal: *«enfócate en el de código y en el apartado de trading… no hagas un
apartado de bot de trading, sino que sean apartados que se puedan complementar, pero quiero que sea
tan específico como esto los 20 nichos»*. Está montando un bot ahora mismo.

Materia prima: `research/dominios/bots-trading.md` (45 recursos, 10 de primera),
`datos-finanzas.md` y `maestria-codigo.md`. Todo lo que **no** salía de esos barridos —el país
`codigo-de-bot` entero— se verificó en vivo contra la API de GitHub el mismo día; los números están
en §3.7.

---

## 1. Qué quedó montado

| | Antes | Ahora | Δ |
|---|---:|---:|---:|
| país | 2 | 7 | +5 |
| pueblo | 5 | 22 | **+17** |
| continente | 0 | 0 | — |

```
trading
├── conectividad       ccxt · ib-async
├── datos-de-mercado   yfinance · openbb
├── investigacion      ta-lib · talipp
├── backtesting        hftbacktest · quantconnect-lean(*) · vectorbt · backtesting-py
│                      (*) el motor vive en 'motores'; se le mide aquí en §3
├── motores            nautilus-trader · quantconnect-lean · freqtrade · hummingbot
├── riesgo             pyportfolioopt · quantstats
├── codigo-de-bot      tenacity · python-statemachine · hypothesis ·
│                      toxiproxy · eventsourcing · time-machine
└── rotki                                        ← pueblo directo, sin país
```

**Medición:** `trading` = **1.701 tokens** con 22 pueblos, contra **1.771 del peor nicho**
(`ciberseguridad`, 26 pueblos) y un presupuesto de 4.000. `trading` queda **segundo, a 70 tokens del
peor**, y no mueve el veredicto de E16. Salida literal en §6.

## 2. La estructura final, y por qué no es la propuesta

La propuesta traía 9 países. Al mirar el material, tres no aguantaban y uno cambió de nombre. Las
cuatro correcciones, con su motivo:

### 2.1 `ejecucion` no existe — no tiene ni una herramienta propia

La propuesta separaba `ejecucion` (órdenes, gestión de posición, idempotencia) de los motores. Al
buscar qué pueblo colgaría de ahí, la respuesta es **ninguno**: mandar una orden, gestionar la
posición y no duplicarla no son herramientas que se instalen, son **mecanismos que o vienen dentro
de un marco o los escribes tú**. Un país de ejecución habría sido un nivel de relleno —el antipatrón
que `TAXONOMIA.md` manda borrar— con un `resumen` que se paga en cada sesión y no agrupa nada.

Su contenido se repartió en los dos sitios donde sí hay algo que invocar: **`motores`** (el marco ya
lo trae hecho) y **`codigo-de-bot`** (lo escribes tú). Esa frontera está escrita en el cuerpo de los
dos países, en las dos direcciones.

Por eso `motores` conserva su nombre en vez de renombrarse a `ejecucion`, y su resumen se reescribió
para que la frontera se lea desde arriba: *«Marcos que ya traen el bucle entero: se configuran y se
extienden, no se escriben desde cero.»*

### 2.2 `operacion` no existe, y es a propósito — es justo lo que pidió Darío

Correr 24/7 es real, pero **su herramienta no es de trading**: reinicio automático, alertas, métricas
y copias ya viven en `infraestructura` (`uptime-kuma`, `ntfy`, `victoriametrics`, `restic`) y
perfilar el bucle vive en `rendimiento` (`samply`, `tokio`). Crear aquí un país `operacion` habría
sido **absorber al vecino**, que es exactamente lo que el encargo prohíbe.

Lo que sí falta —y se dice, no se disimula— es el **ángulo de mercado** de esa observabilidad: avisar
de que el resultado real se ha separado del que prometía el backtest, o de que una posición lleva
abierta más de lo previsto. No hay herramienta libre para eso (§5). Queda escrito en el cuerpo del
país `codigo-de-bot`, que es quien lo necesita.

### 2.3 `riesgo` y `contabilidad` no dan para dos países

La propuesta los separaba. El material da:

- para **riesgo**: una sola librería seria (`pyportfolioopt`) — y el sizing por operación (Kelly,
  fracción fija) **no tiene librería madura en ningún sitio**, lo dice el propio barrido;
- para **contabilidad**: una sola herramienta (`rotki`).

Dos países de un hijo cada uno = dos niveles de relleno. Lo que hice: **`riesgo`** con
`pyportfolioopt` + `quantstats` —los dos leen la misma entrada, la serie de resultados, y hacen la
misma clase de matemática sobre ella— y **`rotki` colgando directo del sistema solar**, sin país,
igual que `ciberseguridad/defensiva/lynis` o `automatizacion/celery`.

Y se dice en el cuerpo de `riesgo` lo que ese país **no** es: el riesgo del instante —límite de
exposición, parada por pérdidas repetidas, corte tras racha mala— no está ahí, viene de serie en los
motores o se escribe en el bot.

### 2.4 Cero continentes

`ciberseguridad` tiene 4 continentes porque tiene 10 países. Con 7, un continente solo alargaría
todas las rutas del catálogo —que se pagan en cada sesión— sin agrupar nada que no se lea ya. Se
revisa cuando `trading` pase de 10 países.

### 2.5 `datos-de-mercado` y no `datos`

Nombre más largo a propósito, y cuesta ~4 tokens: `datos` a secas se confunde con el nicho vecino
`ingenieria-datos` en un catálogo que se lee de un vistazo. Claridad sobre 4 tokens.

## 3. Qué entró en cada país, y a quién le gana

### 3.1 `conectividad` — sin cambios de pueblos, con cuerpo nuevo

`ccxt` (cripto, más de cien mercados, REST y flujo continuo ya incluidos y gratis) e `ib-async`
(sucesor mantenido del cliente archivado en 2024; única vía razonable a acciones, futuros y opciones
desde Python, con reconexión y resincronización de estado).

**Descartado `alpaca-py`** pese a estar activo y ser Apache-2.0: es un bróker estadounidense y el
barrido reconoce que no lo profundizó. Recomendar un bróker cuya disponibilidad desde España no se
ha comprobado es prometer algo que no se ha verificado. Queda **nombrado en el cuerpo de `ib-async`**
con la advertencia exacta, que es lo que sirve sin costar una línea de catálogo.

El país estrena cuerpo con lo que faltaba: la clave de mercado va cifrada (`infraestructura/sops`) y
**nunca con permiso de retirada** — solo lectura y operar.

### 3.2 `datos-de-mercado` — lo que no es cripto

`yfinance` gana porque no hay nada gratis mejor para renta variable, divisas e índices, y entra **con
su defecto escrito**: no es una interfaz oficial, raspa un frontal, se rompe cuando ese frontal cambia
y queda en zona gris de sus condiciones. `openbb` gana el hueco de agregador (decenas de proveedores
detrás de una interfaz), con dos avisos: **algunos proveedores exigen clave de pago** y la interfaz
única esconde cuál está detrás; y copyleft de red.

**No entra `arcticdb`**: licencia BSL (no OSI) y su caso —volumen de tick que no aguanta un almacén
normal— ya lo cubre el vecino. Se apunta a `ingenieria-datos/motor/duckdb` sobre Parquet.

### 3.3 `investigacion` — los dos entran, y la frontera está escrita

`ta-lib` (núcleo en C, la referencia contra la que se comparan las demás; su roce es la instalación
de la librería C) y `talipp` (incremental: recalcula solo el último valor al llegar un precio, en vez
de rehacer la serie en cada tick). No se solapan: **lote para estudiar, incremental para operar**, y
el cuerpo de `talipp` deja la comprobación obligatoria — pasar la misma serie por los dos y exigir que
coincidan, porque si no coinciden el bot en vivo opera con números que el backtest nunca vio.

Caso raro del barrido, recogido en el cuerpo de `ta-lib`: **la librería de indicadores sobre
dataframes más citada durante años ya no existe en su dirección original**; si alguien pide
`pandas-ta`, el que vive es `pandas-ta-classic`. Eso ahorra el rato de buscar un 404.

### 3.4 `motores` — cuatro marcos, cuatro modelos mentales

| Entra | Gana su hueco por | Contra quién |
|---|---|---|
| `nautilus-trader` | simulación y vivo comparten semántica de ejecución y reloj determinista; estado fuera del proceso, que es lo que permite reiniciar con posición abierta | ya estaba |
| `quantconnect-lean` | el realismo desmontado en modelos por mercado (comisión, deslizamiento, relleno, restricciones del venue) que se auditan uno a uno | `nautilus`: mismo hueco, ejes distintos, y ambos entran con la distinción escrita en los dos cuerpos |
| `freqtrade` | protecciones de serie que cortan solas, y **comprobadores dedicados de sesgo de anticipación y de recursión** que no tiene ningún otro | `jesse` y `octobot` fuera: mismo hueco, menos actividad, y el segundo empuja a su nube de pago |
| `hummingbot` | cuenta de papel contra el **libro real sin claves de ningún mercado**, y almacén local cifrado en vez de fichero en claro | nadie: es el único de creación de mercado |

**`vnpy` fuera** (45k estrellas, MIT, activo): su valor declarado por el propio barrido es de
*referencia de arquitectura* —cómo separar pasarela, motor, backtest y cuenta simulada— y su
documentación es mayoritariamente en chino. Ese valor no se pierde: el patrón está escrito en los
cuerpos de `motores` y `codigo-de-bot`, que es donde se usa. Una línea de catálogo se paga siempre;
un patrón bien dicho, no.

### 3.5 `riesgo`

`pyportfolioopt` es lo más cercano a gestión de riesgo seria que hay libre (frontera eficiente, CVaR,
paridad de riesgo jerárquica), y su cuerpo dice lo que **no** hace: cuánto arriesgar en una entrada
concreta. `quantstats` gana el hueco de informe porque se enchufa a la salida de cualquier motor —así
la comparación entre dos backtests hechos con motores distintos se hace con la misma vara— y sustituye
a la librería equivalente que murió con Quantopian (sin publicar desde 2023).

### 3.6 `rotki` — el único que cierra las cuentas

Cierra el hueco que ningún motor cubre: que el saldo que cree el bot y el saldo real coincidan, y que
de ahí salga un número presentable a Hacienda, con método de coste y ejercicio fiscal. Verificado en
vivo: **3.998 estrellas, AGPL-3.0, publicado 2026-08-31**; su propio README ofrece licencia comercial
solo para quien quiera evitar las obligaciones de la AGPL, y hay capa de pago opcional que no hace
falta para esto. Todo local: claves e histórico no salen de la máquina.

Entra con su naturaleza declarada: **es una aplicación de escritorio que corre al lado del bot, no
una librería que el bot invoque**. No sustituye al registro del bot, lo audita — y si los dos números
no cuadran, el que miente casi siempre es el del bot.

### 3.7 `codigo-de-bot` — el país que casi nadie tiene

Ningún barrido lo cubría: `bots-trading.md` es infraestructura de mercado y `maestria-codigo.md` no
produjo ni un pueblo en la tanda 2, por diseño. Así que estos seis **se verificaron en vivo contra la
API de GitHub el 2026-09-01**, y aquí van los números tal cual los devolvió:

| Pueblo | ★ | Licencia | Último push | Qué fallo de dinero previene |
|---|---:|---|---|---|
| `tenacity` | 8.770 | Apache-2.0 | 2026-08-06 | el bot muere de madrugada porque la reconexión era un `while` con `sleep` |
| `python-statemachine` | 1.299 | MIT | 2026-08-17 | una transición imposible de la orden se cuela y se descubre con dinero puesto |
| `hypothesis` | 8.930 | MPL-2.0 (*) | 2026-08-31 | el invariante que nadie probó: efectivo negativo, ejecuciones que suman de más |
| `toxiproxy` | 12.294 | MIT | 2026-09-01 | la conexión cae justo después de mandar la orden y nadie lo probó nunca |
| `eventsourcing` | 1.684 | BSD-3-Clause | 2026-08-23 | un corte a media escritura deja la posición persistida mintiendo |
| `time-machine` | 994 | MIT | 2026-08-28 | el cierre de vela, el enfriamiento y el cambio de hora, probados durmiendo |

(*) GitHub no clasifica su licencia (`NOASSERTION`); leído el `LICENSE.txt` del repo: **MPL-2.0**.

**Las peleas que hubo, con su medición:**

- `python-statemachine` (1.299★, push **2026-08-17**) gana a `pytransitions/transitions` (6.582★,
  push **2025-09-11**) pese a tener **cinco veces menos estrellas**: la otra lleva un año sin publicar
  y esto es código que decide si una orden puede pasar de cancelada a llena.
- `time-machine` (994★, push 2026-08-28) gana a `freezegun` (4.525★, push **2025-08-19**) por lo
  mismo, más un motivo técnico: sustituye el reloj a bajo nivel en vez de parchear función a función,
  así que no ralentiza la suite.
- `tenacity` no tuvo rival: `litl/backoff`, el envoltorio de reintento más citado del ecosistema,
  está **archivado** (2.695★, último push 2024-05-02).
- `py-moneyed` (aritmética de dinero) **fuera**: 474★ y sin publicar desde 2024-04-23. El problema
  real —redondeo a tick y lote— ya lo resuelve `ccxt` con sus funciones de precisión.
- `pybreaker` (692★, BSD-3, activo) **fuera por solapamiento**: el cortacircuitos de negocio ya viene
  en `freqtrade` y el de conexión lo cubren las condiciones de parada de `tenacity`.
- `pydantic` **fuera**: validar en frontera es transversal, no de trading; ya lo cubre el mar
  `resistencia` y, para dataframes, `ingenieria-datos/validacion/pandera`.

El cuerpo del país lleva las cuatro preguntas que definen este código, y son las que Darío tiene que
poder contestar de su bot: qué pasa si se cae la red justo después de mandar la orden; qué pasa si el
mismo aviso de ejecución llega dos veces; qué pasa si el proceso arranca con una posición ya abierta;
y cómo se demuestra cualquiera de las tres **sin poner dinero**.

## 4. Qué modela y qué no cada motor — la sección que evita perder dinero

Un motor no es honesto o deshonesto: **modela unas cosas y no otras, y el fallo es no saber cuáles.**
Seis ejes: comisiones · deslizamiento · latencia · liquidez y cola del libro · sesgo de supervivencia
· sesgo de anticipación.

| Motor | Sí modela | **No** modela | Cuándo miente |
|---|---|---|---|
| **hftbacktest** | posición en la **cola** del libro, retardo de datos y de orden por separado, libro reconstruido tick a tick (nivel 2 y 3) | nada relevante de microestructura; a cambio **exige** datos L2/L3, que ni son gratis ni cómodos | casi nunca en su hueco; miente si le das velas en vez de libro |
| **quantconnect-lean** | comisión por bróker, deslizamiento, relleno y restricciones **del venue**, con modelos intercambiables y auditables por mercado; multiactivo | la cola del libro | si tu orden es grande respecto al libro: cree que se llena entera |
| **nautilus-trader** | reloj de nanosegundos, ticks de cotización y operación, barras y libro real; comisión y deslizamiento por adaptador; **misma semántica en simulación y vivo** | la cola del libro por sí solo | igual que el anterior, en estrategias que ponen precio |
| **freqtrade** | comisión; **rellena al precio pedido, SIN deslizamiento**, siempre que ese precio caiga dentro del máximo y el mínimo de la vela | libro, latencia y liquidez: trabaja sobre velas | en cuanto la estrategia dependa de entrar a un precio concreto dentro de la vela |
| **backtesting-py** | comisión por operación y relleno dentro del rango de la vela; órdenes de mercado, límite y stop | cartera multiinstrumento, libro, latencia, liquidez | si tu tamaño mueve el precio: no lo sabe |
| **vectorbt** | comisiones y deslizamiento por operación; validación hacia delante por ventanas | **no itera en el tiempo**: trabaja sobre matrices de señales precalculadas | siempre que un `shift` esté mal puesto — mete sesgo de anticipación **y no salta ningún error** |
| **hummingbot** | libro real en cuenta de papel, sin claves | no es un backtest histórico: es simulación en vivo | si se confunde papel con backtest |

Y lo que ninguno modela solo: **sesgo de supervivencia**. Si el histórico son los pares que hoy
existen, los que se deslistaron no están, y toda estrategia de cripto sale mejor de lo que fue.

Tres reglas que salen de esa tabla y están escritas en los cuerpos:

1. **El único número que vale es el que empeora al añadir costes.** Una curva que solo sube cuando se
   quitan las comisiones no es una estrategia, es una hoja de cálculo. (cuerpo de `backtesting`)
2. **Lo que sobreviva al barrido vectorizado se vuelve a correr evento a evento** antes de creérselo.
   (cuerpo de `vectorbt`)
3. **Si la estrategia vive dentro del diferencial, solo vale `hftbacktest`**; si cruza el diferencial
   y aguanta horas, cualquiera de los otros. (cuerpo de `hftbacktest`)

Sobre `freqtrade`, y esto es el filtro 4 del encargo aplicado a un proyecto muy popular: es el bot
cripto más usado (53.9k estrellas) **y su backtest no modela deslizamiento**. No es un defecto
oculto: lo documenta él mismo. Lo que sí es mérito suyo, y no tiene ningún otro, es traer
comprobadores de sesgo de anticipación y de recursión como subcomandos de primera clase.

## 5. Vecinos: qué se apuntó en vez de duplicar

Cada línea es un pueblo que **no** creé porque ya vive en otro nicho. Todos quedan nombrados en el
cuerpo del nodo de `trading` que los necesita, diciendo para qué sirven **aquí**.

| Lo que hacía falta | Ya vive en | Dónde se apunta |
|---|---|---|
| validar velas, huecos, máximo < mínimo, volumen cero | `ingenieria-datos/validacion/pandera` | cuerpo del país `datos-de-mercado` |
| almacenar años de series sin montar servidor | `ingenieria-datos/motor/duckdb` (sobre Parquet) | cuerpo del país `datos-de-mercado` |
| perfilar el bucle, latencia, concurrencia | `rendimiento/perfilado/samply`, `rendimiento/concurrencia/tokio` | cuerpo del país `codigo-de-bot` |
| correr 24/7, reinicio, alertas, métricas, copias | `infraestructura` (`uptime-kuma`, `ntfy`, `victoriametrics`, `restic`) | cuerpo del país `codigo-de-bot` |
| cuadro de mando de resultados para que lo mire otro | `analitica/cuadros-de-mando/evidence` | cuerpo de `quantstats` |
| custodia de las claves de mercado | `infraestructura/sops` + océano de secretos | cuerpo del país `conectividad` |
| optimización numérica bajo `pyportfolioopt` | `cientifico/scipy` | cuerpo de `pyportfolioopt` |
| mutación para saber si un test afirma algo | mar `pruebas` | cuerpo de `hypothesis`, marcando que **complementa**, no repite |
| validar en frontera, fallo ruidoso | mar `resistencia` | motivo del descarte de `pydantic` (§3.7) |

**Comprobado antes de crear cada pueblo:** ninguno de los 17 nombres nuevos existía ya en el árbol
(189 pueblos en el momento de cerrar). E18 en verde.

La frontera que más me costó, y la digo: **`toxiproxy` roza el mar `pruebas`**, que ya nombra la idea
de inyectar el fallo real (partición de red, reloj desincronizado, proceso muerto) para sistemas
distribuidos. Entra igual como pueblo por dos motivos: el mar nombra la *idea* y no la herramienta,
y aquí el modo de fallo es de dinero, no de consistencia. Está en §7 como decisión revisable.

## 6. Verificación — salida literal

```
$ python3 -m cosmos generar galaxia --config galaxia.toml
COSMOS  generar  verde

Índice escrito en /Users/<usuario>/cosmos/galaxia/COSMOS.md
```

```
$ python3 -m cosmos validar galaxia --config galaxia.toml
COSMOS  verde  0 errores
```

```
$ python3 -m cosmos medir galaxia --config galaxia.toml
COSMOS  medir

  Entrada base .... 1.128 tokens   (índice + océanos + estructura, sin pueblos; estimado, ±desconocido, heurística v1)
  Peor nicho ...... 1.771 tokens   (ciberseguridad, 26 pueblos)
  Universo ........ 19.978 tokens   (estimado, ±desconocido, heurística v1)
  Descarga ........ 91,1 %
  Presupuesto ..... 4.000     OK, quedan 2.229 tokens en el peor caso

  Fuera de COSMOS . no_medido      (system prompt, tools, MCP)

  Lo más caro de la entrada evaluada:
    1.  907 tok  catálogo visible
    2.  525 tok  índice de galaxia
    3.  77 tok  oceano/irreversible
```

```
$ python3 -m cosmos medir galaxia --config galaxia.toml --nicho trading
  Entrada base .... 1.128 tokens
  Peor nicho ...... 1.771 tokens   (ciberseguridad, 26 pueblos)
  Nicho activo .... 1.701 tokens   (trading; 22 pueblos)
  Presupuesto ..... 4.000     OK, quedan 2.299 tokens en el nicho activo
```

**`trading` no es el peor nicho.** 1.701 contra 1.771, a 70 tokens. Con 26 pueblos habría empatado;
por eso me quedé en 22 y no en 25.

Comprobaciones colaterales, para descartar que rompiera algo ajeno:

```
$ python3 -m unittest discover -s tests -q
Ran 52 tests in 0.197s
OK (skipped=1)

$ python3 -m cosmos validar ejemplo
COSMOS  verde  0 errores
```

**Ningún rojo, ni mío ni ajeno.** El árbol está siendo modificado por otros tres trabajos a la vez
(127 → 189 pueblos mientras trabajaba); todo lo que quedó rojo en algún momento intermedio fue E19 y
lo reparó `compilar` (§7.6).

**Aviso de concurrencia:** al cerrar, otro trabajo commiteó el árbol entero
(`273350b feat(galaxia): 21 estrellas, 189 herramientas, verde`) y arrastró dentro mis 22 nodos de
`trading` y los 7 países. **No se perdió nada** —el commit incluye los ficheros tal cual quedaron— pero
ese commit no es mío ni lleva mi mensaje, así que el historial no separa las dos tandas. Solo este
parte quedó fuera, sin commitear.

## 7. Decisiones dudosas — lo que hay que revisar

Ordenadas por lo cerca que estuve de equivocarme.

1. **Reviré dos decisiones que estaban escritas en cuerpos de nodo.** El cuerpo de `hftbacktest`
   descartaba explícitamente el motor vectorizado *«por su licencia con cláusula de uso comercial
   restringido»* (`vectorbt`) y el simple *«con copyleft fuerte»* (`backtesting-py`); el de
   `nautilus-trader` descartaba *«la plataforma equivalente en otro lenguaje… su camino natural es la
   nube de su empresa»* (`quantconnect-lean`). **Los tres entran ahora.** Motivo: aquellas decisiones
   se tomaron cuando `trading` tenía 5 huecos en total; con un país `backtesting` dedicado, el criterio
   deja de ser «cuál es el único» y pasa a ser «qué modela cada uno». Y las tres licencias se
   releyeron: ninguna cuesta dinero para montar bots propios o de cliente. **Reescribí esos dos
   cuerpos** para que no se contradigan con el árbol. Si Darío prefiere el criterio anterior, quitar
   `vectorbt` es el revert más limpio.
2. **`vectorbt` es la entrada más discutible del país.** Su licencia no es OSI (Apache con cláusula de
   no reventa) y su paradigma facilita el sesgo de anticipación —el propio barrido lo avisa—. Entra
   porque el hueco *«descartar mil combinaciones rápido»* es real y no lo cubre nadie más gratis, y
   con la advertencia en su propio cuerpo. Es la primera línea que quitaría si hiciera falta margen.
3. **`toxiproxy` frente al mar `pruebas`** — la frontera de §5. Si se decide que la inyección de fallo
   es transversal y no de trading, sale de aquí y sube al mar, y se pierde la línea de catálogo pero
   también su descubribilidad.
4. **`rotki` cuelga directo del sistema solar** en vez de tener país `contabilidad`. Es legal
   (`rango(padre) < rango(hijo)`) y evita un nivel de un solo hijo, pero deja la contabilidad como
   pueblo suelto en un nicho que sí tiene países. Cuando entre una segunda herramienta de conciliación
   o fiscalidad, ahí nace el país.
5. **`hypothesis` y `tenacity` son transversales y las metí en un nicho.** Se prueban invariantes y se
   reintenta con espera creciente en cualquier proyecto, no solo en un bot. Entran aquí —y no en un
   mar— porque el encargo pedía expresamente que `codigo-de-bot` tuviera **su propio código dentro**, y
   porque en los otros 19 nichos un fallo de estos da una excepción y aquí da una pérdida. Leído en
   estricto, `tenacity` es agua.
6. **Compilé la vista plana, que escribe fuera de `galaxia/` y `registro/`.** Añadir 17 pueblos deja
   E19 en rojo por definición, y `NUCLEO.md` §6 dice que es `compilar` quien lo repara. Escribí en
   `.cosmos/vista-galaxia/` (ignorado por git) y `.cosmos/compilado-galaxia.json` (versionado). Mismo
   precedente y misma declaración que la tanda 2 en su §5.14. **Efecto secundario a vigilar**: como el
   árbol está mutando por otros tres trabajos, ese manifiesto recogió también sus pueblos, no solo los
   míos.
7. **Ejecuté `generar`, que reescribe `galaxia/COSMOS.md`.** Lo pedía el encargo. Mis cambios no
   añaden ningún sistema solar ni ningún océano, y el índice solo lista galaxia, sistemas solares y
   océanos: `indice(árbol)` no cambia por mi trabajo, y `validar` (que incluye E15) estaba verde antes
   y después. El `git diff` de ese fichero contra HEAD es de otro trabajo —el renombrado de nichos
   `mercados`→`trading`, `datos`→`ingenieria-datos`, `agentes`→`agentes-ia`—, **no mío**.
8. **Renombré dos ficheros de país**: `mercados-conectividad.md` → `trading-conectividad.md` y
   `mercados-motores.md` → `trading-motores.md`, con `git mv`. El nombre de fichero no afecta al árbol
   (todo se deduce del frontmatter), pero `mercados` era deuda del renombrado del nicho. Cambio
   cosmético, declarado.
9. **Ninguno de los 22 pueblos se ha ejecutado.** El criterio 5 de `UNIVERSO.md` («se ha usado una
   vez») **no se cumple**. Para los 16 de los barridos, la evidencia es metadata verificada en vivo;
   para los 6 de `codigo-de-bot`, lo mismo, verificado por mí hoy (§3.7). Es la deuda de todo el
   universo, no de este nicho — y en este nicho pesa más que en ningún otro, porque el propio barrido
   avisa de que **reconexión, idempotencia y reinicio con posición abierta no se pueden verificar
   leyendo un README**. Ese es literalmente el trabajo que `toxiproxy` y `hypothesis` existen para
   hacer: la primera vez que Darío monte el bot, ahí se paga la deuda.

## 8. Huecos declarados — lo que falta y no tiene herramienta buena

1. **Sizing por operación.** Kelly fraccional, fracción fija, riesgo por operación como porcentaje del
   capital: **no hay librería madura**. `pyportfolioopt` resuelve reparto de cartera, que es otro
   problema. Cada bot del barrido lo implementa a mano. **Es código a escribir, no herramienta a
   instalar** — y es de las primeras cosas que Darío necesita.
2. **Observabilidad específica de trading.** Alertar de que el resultado real se ha separado del que
   prometía el backtest, o de que una posición lleva abierta más de lo parametrizado. Los cuadros de
   mando propios de `freqtrade` y `hummingbot` son lo único que hay, y solo para ellos mismos. La capa
   genérica ya está en `infraestructura`; el ángulo de mercado hay que escribirlo.
3. **Etiquetado y validación cuantitativa seria** (triple barrera, validación cruzada purgada). El
   proyecto que la ofrece es **la trampa más peligrosa de todo el barrido**: parece libre —código
   visible, README técnico— y su `LICENSE.txt` es en realidad un contrato de suscripción de pago. No
   entra, y queda escrito aquí para que nadie lo reintroduzca por descuido.
4. **Datos de mercado de renta variable con garantía.** Lo gratis es raspado sin garantía (`yfinance`);
   lo fiable es de pago. Sigue abierto desde la tanda 1.
5. **Sesgo de supervivencia en cripto.** Ningún motor lo modela y ninguna fuente gratis da la lista de
   pares deslistados con sus fechas. Hoy solo se puede declarar como límite del backtest.
6. **Protocolo FIX y baja latencia real** (colocation, FPGA): fuera a propósito, no encaja con coste
   cero y autoalojado. Los repos de esa punta son proyectos de clase, no infraestructura.
7. **Bróker regulado no estadounidense fuera de la pasarela clásica**: sin explorar.

## 9. Ficheros

Escrito **solo** dentro de `galaxia/pueblos/`, `galaxia/paises/` y `registro/`. Excepción única
declarada en §7.6 (artefacto de compilación) y §7.7 (índice, que lo pedía el encargo).

```
galaxia/paises/trading-backtesting.md            nuevo
galaxia/paises/trading-codigo-de-bot.md          nuevo
galaxia/paises/trading-datos-de-mercado.md       nuevo
galaxia/paises/trading-investigacion.md          nuevo
galaxia/paises/trading-riesgo.md                 nuevo
galaxia/paises/trading-conectividad.md           renombrado desde mercados-*, cuerpo nuevo
galaxia/paises/trading-motores.md                renombrado desde mercados-*, resumen y cuerpo nuevos
galaxia/pueblos/<17 nuevos>/SKILL.md             nuevos
galaxia/pueblos/hftbacktest/SKILL.md             recolocado a trading/backtesting + cuerpo reescrito
galaxia/pueblos/nautilus-trader/SKILL.md         cuerpo reescrito (§7.1)
galaxia/pueblos/freqtrade/SKILL.md               cuerpo ampliado con sus asunciones de backtest
galaxia/pueblos/ib-async/SKILL.md                cuerpo ampliado
```

`galaxia/estrellas/trading.md` **intacto**, tal como pedía el encargo. `cosmos/`, `tests/`,
`ejemplo/`, `cosecha/`, `puente/` y `spec/` **intactos**.

Cero credenciales, cero claves de API, cero nombres de cliente, cero dominios, cero datos personales
en ningún nodo.
