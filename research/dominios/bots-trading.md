# Bots de Trading — infraestructura para montar un bot que funciona de verdad

Barrido GitHub para COSMOS. Dominio: conexión a exchanges/brokers (REST+WS), motores de ejecución,
gestión de posiciones, motores de backtesting serios, gestión de riesgo y sizing, datos de mercado,
indicadores técnicos, infraestructura 24/7 (reconexión, idempotencia, reinicio con posiciones
abiertas), paper trading, contabilidad de operaciones/P&L y observabilidad en producción.

Método: **cupo de WebSearch de la sesión agotado antes de empezar este dominio** — barrido 100% vía
API de GitHub autenticada (`api.github.com/search/repositories` + `/repos/{owner}/{repo}`, 5000
peticiones/hora verificadas) y lectura directa de READMEs/docs/LICENSE en
`raw.githubusercontent.com`. Sin comparativa de terceros (foros, "best of" en blogs) — todo dato de
estrellas, licencia y último push viene de la API en vivo, no de memoria.

Fecha del barrido: 2026-09-01. Estrellas y fechas de push tal cual las devolvió la API en ese
momento.

---

## De primera

Máximo 10. Criterio: honestidad del backtest primero, infraestructura de producción segundo,
coste cero siempre verificado. Se penaliza sin piedad lo que promete rentabilidad y se premia lo que
documenta sus propias limitaciones.

1. **[NautilusTrader](https://github.com/nautechsystems/nautilus_trader)** — 28.2k★, LGPL-3.0,
   push 2026-09-01 (muy activo). **Por qué gana a todo lo demás**: es el único motor de esta lista
   que resuelve de raíz el problema #1 de un bot en producción — la divergencia entre lo que se
   backtesteó y lo que corre en vivo. Su propio README lo dice explícito: *"the same execution
   semantics and deterministic time model operate in both research and live systems... with no code
   changes"*. Núcleo en Rust (thread-safe, tipado), Python como capa de orquestación/estrategia,
   persistencia de estado en Redis (clave para reiniciar con posiciones abiertas sin perderlas),
   resolución de nanosegundo en el backtest con quote/trade ticks, barras y order book reales.
   Adaptadores modulares para cualquier REST/WebSocket — cripto CEX/DEX, FX, acciones, futuros,
   opciones, casas de apuestas. Mecanismo: mismo grafo de eventos y mismo bus de mensajes en
   backtest y en vivo; lo que cambia es solo el adaptador de datos/ejecución.

2. **[QuantConnect Lean](https://github.com/QuantConnect/Lean)** — 21.4k★, Apache-2.0, push
   2026-08-31 (muy activo). **Por qué gana**: es el motor "de libro de texto" de honestidad de
   backtest — modela explícitamente `FeeModel`, `SlippageModel`, `FillModel` y `BrokerageModel` por
   cada venue/broker simulado, en vez de un único supuesto genérico para todo el mercado. Corre
   100% local y gratis con el LEAN CLI + datos gratuitos (solo la nube/datos premium de QuantConnect
   son de pago; el motor y el backtest local no lo son). Soporta Python y C#, multi-activo
   (acciones, forex, futuros, cripto, opciones). Mecanismo: arquitectura de algoritmo único que se
   despliega igual en backtest, papel y broker real, con modelos de realismo de mercado
   intercambiables y auditables.

3. **[hftbacktest](https://github.com/nkaz001/hftbacktest)** — 4.6k★, MIT, push 2025-12-23.
   **Por qué gana en honestidad pura**: es el motor de backtest más riguroso que encontré en todo el
   barrido para cripto/market making. Su propio README: *"accounting for both feed and order
   latencies, as well as the order queue position for order fill simulation"*, con **reconstrucción
   completa del order book a partir de feeds Level-2 (market-by-price) y Level-3 (market-by-order)**
   y modelos de latencia de feed/orden configurables. La inmensa mayoría de "backtesting engines" de
   esta lista asumen fill instantáneo a un precio; hftbacktest simula la cola de tu orden en el libro
   — exactamente lo que un motor vectorizado o basado en velas no puede ver. Núcleo Rust + bindings
   Python. Mecanismo: replay de datos tick-a-tick con reconstrucción de libro + modelo de latencia
   propio o custom.

4. **[freqtrade](https://github.com/freqtrade/freqtrade)** — 53.9k★, GPL-3.0, push 2026-09-01 (muy
   activo). **Por qué gana como "todo en uno"**: es el único bot cripto de la lista que (a) documenta
   sus propias asunciones de backtest sin adornarlas — *"All orders are filled at the requested
   price (no slippage) as long as the price is within the candle's high/low range"* — y (b) trae
   **herramientas propias para cazar el sesgo que ese motor introduce**: `lookahead-analysis` y
   `recursive-analysis` como subcomandos de primera clase, algo que ningún otro bot de esta lista
   ofrece de fábrica. Módulo `Protections` (StoplossGuard, MaxDrawdown, CooldownPeriod,
   LowProfitPairs) como circuit-breakers reales, activables también en backtest/hyperopt con
   `--enable-protections`. Dry-run (paper trading) usa literalmente la misma clase de estrategia que
   el live — no hay un "modo simulado" aparte que pueda divergir. Persistencia de operaciones en
   SQLite (contabilidad/P&L) + FreqUI (dashboard) + API REST. Mecanismo: motor basado en velas OHLCV
   con asunciones de fill documentadas + analizadores de sesgo dedicados.

5. **[ccxt](https://github.com/ccxt/ccxt)** — 43.8k★, MIT, push 2026-08-31 (muy activo). **Por qué
   gana**: es la capa de conectividad universal que casi todo lo demás de esta lista usa por debajo
   — API unificada REST **y WebSocket** ("CCXT Pro", ya integrado en el paquete gratuito, no es un
   producto de pago aparte) para 100+ exchanges cripto. Verificado en el propio README: cada
   exchange listado trae su badge "CCXT Pro" incluido. Sin esto, cada bot tendría que reimplementar
   el conector REST+WS de cada exchange a mano. Mecanismo: capa de abstracción sobre las APIs
   nativas de cada exchange, normaliza símbolos, tipos de orden y estructuras de respuesta.

6. **[ib_async](https://github.com/ib-api-reloaded/ib_async)** — 1.7k★, BSD-2-Clause, push
   2026-08-19 (activo). **Por qué gana**: es el sucesor oficial de la comunidad de `ib_insync`
   (archivado por su autor original el 2024-03-14 — verificado, `archived: true` en la API) para
   Interactive Brokers, el bróker tradicional (acciones/forex/futuros/opciones) más usado en bots
   open source. README propio: *"Production-Ready: Robust error handling, reconnection logic, and
   comprehensive logging"* — exactamente el punto débil de un bot 24/7 (reconexión tras caída de
   la Gateway/TWS). Cuenta paper de IBKR es gratis, así que se puede probar la conectividad real sin
   arriesgar capital. Mecanismo: wrapper async sobre la API oficial de Interactive Brokers
   (TWS/Gateway), maneja el ciclo de reconexión y resincronización de estado.

7. **[Hummingbot](https://github.com/hummingbot/hummingbot)** — 19.7k★, Apache-2.0, push
   2026-09-01 (muy activo). **Por qué gana en su nicho (market making)**: es el único proyecto de la
   lista centrado en estrategias de creación de mercado (Pure MM, Avellaneda MM, Cross-Exchange MM)
   con **paper trading contra order book real sin necesitar API keys** (`--set
   exchange=binance_paper_trade`), y con keystore local cifrado para las claves de exchange en vez de
   texto plano. Conectores separados en CEX custodiados vs DEX no-custodiados (arquitectura distinta
   y explícita para cada riesgo). Nota: el README afirma "$34B en volumen generado" — cifra
   autodeclarada del propio proyecto, no verificada de forma independiente por este barrido.
   Mecanismo: conectores que normalizan REST+WS por tipo de exchange (CLOB-CEX, CLOB-DEX, AMM-DEX) +
   motor de estrategias V2 configurable en caliente.

8. **[vectorbt](https://github.com/polakowo/vectorbt)** (versión libre, no vectorbt PRO) — 8.9k★,
   push 2026-08-02 (activo). **Aviso de licencia real**: no es Apache-2.0 puro pese a lo que dice
   GitHub — es **"Apache 2.0 + Commons Clause"** (verificado en su `LICENSE.md`): puedes usarlo y
   modificarlo gratis, pero la cláusula prohíbe explícitamente "vender" el software o revenderlo como
   servicio (hosting/consultoría cuyo valor derive sustancialmente de vectorbt). Para uso interno de
   agencia (montar bots para clientes, no vender vectorbt-as-a-service) esto no es un problema; para
   un SaaS de backtesting sí lo sería. **Por qué gana pese a la nota**: backtesting vectorizado sobre
   pandas/NumPy/Numba — corre miles de combinaciones de parámetros en el tiempo que un motor
   event-driven tarda en correr una — con optimización walk-forward integrada. **Riesgo real a
   vigilar**: el paradigma vectorizado (arrays de señales precalculados en vez de iteración
   vela-a-vela) hace más fácil introducir lookahead bias por error de desplazamiento (`shift`) si no
   se es cuidadoso — al contrario que un motor event-driven, no te obliga a razonar "qué sé en este
   instante t".

9. **[backtesting.py](https://github.com/kernc/backtesting.py)** — 8.9k★, AGPL-3.0, push
   2026-08-05 (activo). **Por qué gana como contrapeso a vectorbt**: motor event-driven simple,
   vela-a-vela, de un solo activo — el modelo mental más difícil de hacer trampa sin darse cuenta.
   Modela comisión (`commission=.002` en su propio ejemplo del README) y rango de fill dentro de la
   vela. AGPL-3.0: gratis para uso interno; si se ofreciera como servicio de red a terceros, la AGPL
   obligaría a liberar el código — no aplica a un bot propio o de cliente que no se revende como
   SaaS. Mecanismo: bucle de simulación bar-by-bar con órdenes de mercado/límite/stop y gestión de
   posición explícita.

10. **[vnpy](https://github.com/vnpy/vnpy)** — 45k★, MIT, push 2026-09-01 (muy activo). **Por qué
    gana como referencia de arquitectura full-stack**: es el framework de trading cuantitativo más
    grande del ecosistema chino, con **arquitectura modular de gateways** — cada conector a un
    bróker/exchange es un paquete pip separado (`vnpy_ctp` para futuros/opciones chinos vía CTP,
    `vnpy_ib` para Interactive Brokers, gateways de Binance/OKX, etc.), un módulo de backtest CTA con
    GUI propia (`vnpy_ctabacktester`, sin depender de Jupyter) y un módulo de **cuenta simulada local
    (`vnpy_paperaccount`)** que empareja órdenes contra datos de mercado reales en tiempo real —
    paper trading genuino, no solo "restar de un saldo ficticio". Aviso: documentación y comunidad
    mayoritariamente en chino; útil sobre todo como referencia de cómo separar gateway / motor de
    estrategia / backtest / cuenta simulada en piezas independientes, patrón que vale la pena copiar
    aunque no se use el framework entero.

---

## Segunda fila

- **[TA-Lib (python wrapper)](https://github.com/TA-Lib/ta-lib-python)** — 12.2k★, BSD-2-Clause,
  push 2026-08-29. El estándar de facto para indicadores técnicos — núcleo en C, décadas de uso.
  Complementarios: **[talipp](https://github.com/nardew/talipp)** (536★, MIT, push 2025-09-09),
  librería de indicadores **incrementales/streaming** — recalcula solo el último valor en vez de
  todo el histórico en cada tick, lo que importa de verdad en un bot 24/7 en vivo. **Caso raro
  verificado**: el repo histórico `twopirllc/pandas-ta` (la librería de indicadores sobre pandas más
  citada durante años) **ya no existe** — la API de GitHub devuelve 404 sobre `twopirllc/pandas-ta`.
  El sucesor mantenido por la comunidad es
  **[pandas-ta-classic](https://github.com/xgboosted/pandas-ta-classic)** (427★, MIT, push
  2026-07-25, 250+ indicadores) — si algún tutorial o cliente pide "pandas-ta", este es el fork vivo.

- **[jesse](https://github.com/jesse-ai/jesse)** — 8.4k★, MIT, push 2026-08-27. Bot cripto Python
  puro con la misma promesa de "sin lookahead bias" que freqtrade (verificado en su README), motor
  de estrategias con multi-timeframe/multi-símbolo nativo, dry-run y live con el mismo código.
  Alternativa a freqtrade cuando se prefiere Python de estrategia en vez de config YAML/JSON.

- **[OctoBot](https://github.com/Drakkar-Software/OctoBot)** — 6.5k★, GPL-3.0, push 2026-09-01.
  Núcleo libre y activo, con backtest + paper trading + motor de estrategias (Grid/DCA/TradingView).
  **Aviso**: el README empuja fuerte hacia `octobot.cloud` (capa SaaS de pago) para varias features
  "avanzadas" — el core self-hosted sigue siendo gratis y funcional, pero hay que revisar con cuidado
  qué queda solo en la nube de pago antes de comprometerse a usarlo como base.

- **[zipline-reloaded](https://github.com/stefan-jansen/zipline-reloaded)** — 1.9k★, Apache-2.0,
  push 2026-01-06. Continuación mantenida por la comunidad del `quantopian/zipline` original — este
  último quedó efectivamente muerto (último push 2024-02-13) cuando Quantopian cerró. Si algo pide
  "zipline", usar el reloaded, no el original.

- **[backtrader](https://github.com/mementum/backtrader)** — 23k★, GPL-3.0, **último push
  2024-08-19** (más de dos años sin actividad al momento del barrido). Sigue siendo uno de los
  motores de backtest más citados en tutoriales por su popularidad histórica, pero su autor lo dejó
  de mantener y no encontré ningún fork con tracción real que lo continúe (los forks buscados tienen
  0-1★). No lo pondría como base de nada nuevo hoy — usar NautilusTrader o backtesting.py en su
  lugar.

- **[quantstats](https://github.com/ranaroussi/quantstats)** — 7.6k★, Apache-2.0, push 2026-07-20.
  Capa de reporting de P&L/riesgo de cartera (Sharpe, drawdown, tearsheets) — se conecta a la salida
  de cualquiera de los motores de arriba. Sustituye en la práctica a
  **[pyfolio](https://github.com/quantopian/pyfolio)** (6.4k★, Apache-2.0, sin push desde
  2023-12-23 — abandonado con el resto del ecosistema Quantopian).

- **[yfinance](https://github.com/ranaroussi/yfinance)** — 25.1k★, Apache-2.0, push 2026-08-27.
  Datos históricos gratis vía scraping no oficial de Yahoo Finance — cero coste, pero sin SLA: rompe
  cuando Yahoo cambia su frontend, y su uso está en zona gris de los términos de servicio de Yahoo.
  Sirve para prototipar y para acciones/forex/índices; no vale para cripto tick-level.

- **[OpenBB](https://github.com/OpenBB-finance/OpenBB)** — 72.6k★, **AGPL-3.0** (verificado en su
  `LICENSE`, no MIT como podría parecer por lo popular que es), push 2026-07-30. Agregador de datos
  de mercado con decenas de proveedores conectables (muchos gratis, algunos exigen API key de pago) —
  la pieza más grande para centralizar fuentes de datos, pero la AGPL implica que si se ofrece como
  servicio de red hay que liberar el código: para uso interno de agencia no es problema, para
  revender como producto sí.

- **[PyPortfolioOpt](https://github.com/PyPortfolio/PyPortfolioOpt)** — 6.0k★, MIT, push
  2026-07-07. Lo más cercano a una librería de gestión de riesgo/sizing de cartera "seria" que
  encontré (frontera eficiente, CVaR, Hierarchical Risk Parity). No es sizing por-operación
  (Kelly/fixed-fractional a nivel de una sola posición) — ver hueco en "Lo que falta".

- **[Superalgos](https://github.com/Superalgos/Superalgos)** — 5.6k★, Apache-2.0, push 2026-09-01.
  Bot cripto con diseño visual/nodos en vez de código, backtest y paper trading integrados. Curva de
  entrada distinta al resto de la lista (no es "escribe una función `populate_indicators`"); útil si
  el cliente quiere iterar estrategias sin tocar código, con la salvedad de que auditar la lógica
  visual es más difícil que auditar una función Python.

- **[ArcticDB](https://github.com/man-group/ArcticDB)** — 2.5k★, **Business Source License 1.1**
  (verificado en su `LICENSE.txt`, no un license OSI estándar), push 2026-09-01. Datastore de series
  temporales/tick data de Man Group — gratis para uso normal, pero la BSL prohíbe ofrecerlo como
  base de datos competidora en la nube durante un plazo (se relicencia a Apache pasado ese periodo).
  Relevante solo si el volumen de tick data de un bot supera lo que Postgres/TimescaleDB (ver
  `infraestructura-devops.md`) puede sostener cómodo.

- **[ib_insync](https://github.com/erdewit/ib_insync)** — 3.3k★, archivado 2024-03-14 por su autor
  original. Se menciona solo para que quede claro: no partir de aquí, partir de `ib_async` (arriba),
  su continuación activa.

---

## Humo

Larga a propósito — este dominio atrae mucho ruido de "IA que te hace rico" y toy-repos con nombres
grandilocuentes y cero usuarios reales.

- **[mlfinlab](https://github.com/hudson-and-thames/mlfinlab)** — 4.9k★. **La trampa más peligrosa
  de todo el barrido**: parece un repo open source normal (código visible, README técnico serio
  sobre triple-barrier labeling y purged k-fold CV para evitar leakage) pero su `LICENSE.txt` es en
  realidad un **contrato de licencia por suscripción de pago** ("Copyright Protection Notice and
  Licensing Agreement" — nada de MIT/Apache/GPL). Estrellas y visibilidad de proyecto libre;
  términos legales de producto comercial. No usar sin leer ese contrato con calma.
- **[Gekko](https://github.com/askmike/gekko)** — 10.2k★, **archivado 2020-02-16** por su propio
  autor. README actual, verificado: *"This repo is not maintained anymore"* y, en el contenido
  histórico que dejó, *"Use Gekko at your own risk"*. Cero valor como base hoy.
- **quantopian/zipline** — 20.1k★ pero muerto desde 2024-02-13 (Quantopian cerró). Usar
  `zipline-reloaded` (segunda fila) en su lugar.
- **The-Swarm-Corporation/AutoHedge** (4.3k★) y **0xemmkty/QuantMuse** (2.9k★) — "construye tu
  hedge fund autónomo en minutos" / "IA + gestión de riesgo avanzada": promesa de rentabilidad vía
  "swarm intelligence" sin motor de ejecución ni backtest verificable descrito — humo por
  definición del propio brief.
- **iterativv/NostalgiaForInfinity** (3.4k★) — no es infraestructura, es una *estrategia* concreta
  para freqtrade; fuera de alcance de este dominio (infra, no estrategia).
- **ctubio/Krypto-trading-bot** (3.7k★, C++, sin licencia declarada, sin push desde 2024-12-15) —
  market making de alta frecuencia sin mantenimiento activo ni licencia clara para reutilizar.
- **CryptoSignal/Crypto-Signal** (5.6k★, sin push desde 2024-07-07) — bot de señales TA, no de
  ejecución; abandonado.
- **nestmotormanshow98/Universal-Trading-Bot** (1.2k★, sin licencia) — "framework universal
  multi-broker" para Pocket Option/Quotex/Polymarket/Robinhood/MT5/Forex/Delta/Cripto a la vez —
  patrón clásico de humo: cuanto más mercados promete cubrir un solo repo pequeño, menos profundidad
  real tiene en cada uno.
- **warp-id/solana-trading-bot** (2.3k★, sin push desde 2024-08-10) — bot de sniping en Solana, zona
  gris legal/ética (front-running de lanzamientos de tokens) y sin mantenimiento.
- Enjambre de **bots de Polymarket/predicción con "arquitectura de N fases" y pocas estrellas**:
  `aulekator/Polymarket-BTC-15-Minute-Trading-Bot` (574★, "arquitectura de 7 fases"),
  `emmanuelwestra/Polymarket-Trading-Bot` (19★, "7 estrategias automatizadas"),
  `brishowkanem4/Polymarket` (173★) — descripciones con mucho adjetivo ("production-grade",
  "professional") y sin mención de modelado de comisiones/slippage/backtest en ninguna.
- Micro-repos de "motor de matching/HFT" con <10★ y nombres grandilocuentes, encontrados en el
  barrido de "order execution engine": `ledgerhubteam/PrimeSwap` (5★), `Dnreikronos/DarkPool-Exchange`
  (4★, "zero-knowledge proofs" + "sub-100ns" en un repo de 4 estrellas sin tests visibles),
  `Prateekbala/Fix-Protocol-Tranding-Engine` (4★), `mahmoud20138/IFC-Trading-System` (5★, "11-layer
  institutional flow confluence"), `Husky-Quantitative-Group/hqg-engine` (6★),
  `tfrmma/latency-benchmarking-suite` (6★) — ninguno con evidencia de uso real más allá del propio
  README.
- **TreborNamor/TradingView-Machine-Learning-GUI** (984★) — promete "comportamiento Pine-like" para
  backtesting Python sin citar qué motor hay debajo ni cómo modela fills.

---

## Mapeo a COSMOS

```
sistema-solar  Software / Ingeniería (todo el conocimiento técnico de COSMOS)
└─ planeta     Ingeniería y Producto
   └─ continente  Trading Algorítmico y Mercados
      └─ país         BOTS DE TRADING   ← este dominio
         ├─ provincia  Conectividad con Exchanges y Brokers
         │   ├─ ciudad  REST/WS unificado cripto     → pueblo: ccxt (+ CCXT Pro, ya incluido gratis)
         │   └─ ciudad  Brokers tradicionales         → pueblos: ib_async (activo), ib_insync (histórico, archivado)
         ├─ provincia  Motores de Ejecución
         │   ├─ ciudad  Motor institucional multi-activo → pueblos: NautilusTrader, QuantConnect Lean
         │   └─ ciudad  Bot todo-en-uno cripto            → pueblos: freqtrade, jesse, OctoBot
         ├─ provincia  Motores de Backtesting
         │   ├─ ciudad  Backtest de alta fidelidad (HFT/MM) → pueblo: hftbacktest (queue position + latencia + L2/L3)
         │   ├─ ciudad  Backtest vectorizado a escala        → pueblo: vectorbt (ojo: licencia Commons Clause)
         │   └─ ciudad  Backtest event-driven simple         → pueblos: backtesting.py, zipline-reloaded
         ├─ provincia  Market Making y Ejecución Especializada
         │   └─ ciudad  → pueblo: Hummingbot (paper trading contra order book real)
         ├─ provincia  Datos de Mercado
         │   ├─ ciudad  Históricos gratis   → pueblos: yfinance (scraping, sin SLA), OpenBB (agregador, AGPL)
         │   └─ ciudad  Almacenamiento tick → pueblo: ArcticDB (ojo: Business Source License)
         ├─ provincia  Indicadores Técnicos
         │   └─ ciudad  → pueblos: TA-Lib (estándar C), talipp (streaming/incremental), pandas-ta-classic
         │                (sucesor del pandas-ta original, que desapareció de GitHub — caso raro verificado)
         ├─ provincia  Gestión de Riesgo y Circuit-Breakers
         │   ├─ ciudad  Circuit-breakers integrados en bot → pueblo: Protections de freqtrade (StoplossGuard, MaxDrawdown, CooldownPeriod)
         │   └─ ciudad  Sizing / optimización de cartera    → pueblo: PyPortfolioOpt (hueco: sin Kelly por-operación dedicado, ver "Lo que falta")
         ├─ provincia  Contabilidad de Operaciones y P&L
         │   └─ ciudad  → pueblos: quantstats (activo), pyfolio (legado, abandonado 2023)
         └─ provincia  Referencia de Arquitectura Full-Stack
             └─ ciudad  → pueblo: vnpy (gateways modulares + backtester GUI + cuenta paper local)
```

Frontera con el país vecino de Infraestructura/DevOps (`infraestructura-devops.md`): aquí solo entra
lo específico de mercados/trading (conectividad de exchange, motores de backtest, contabilidad de
operaciones); la observabilidad genérica de un proceso 24/7 (Prometheus/Grafana, Healthchecks,
reconexión de red a nivel de sistema) vive en el país vecino y se referencia, no se duplica.

## Lo que falta

- **Cero ejecución en vivo.** Todo el barrido es lectura de API de GitHub + READMEs/LICENSE/docs
  públicos — ningún motor de esta lista se instaló, conectó a un exchange real (ni en paper) ni corrió
  un ciclo completo backtest→dry-run→live. Antes de recomendar cualquiera de estos a un cliente real,
  probar reconexión forzada, idempotencia de órdenes y reinicio con posición abierta en un entorno
  de prueba — ninguna de estas tres cosas se puede verificar leyendo un README.
- **WebSearch agotado desde el minuto uno de este dominio** (herencia del resto de la sesión) — no
  hubo forma de contrastar con foros, Reddit (r/algotrading) o comparativas de terceros; todo el
  criterio de "de primera vs. humo" sale de leer el código/README/LICENSE de cada proyecto
  directamente, sin la capa de opinión externa que normalmente aportaría una búsqueda.
- **Sizing por operación (Kelly fraccional, fixed-fractional) sin librería madura dedicada.**
  PyPortfolioOpt resuelve asignación de cartera, no "cuánto arriesgar en esta entrada concreta" — en
  la práctica cada bot de la lista lo implementa a mano (los `Protections` de freqtrade son
  circuit-breakers, no sizing). Si COSMOS necesita esto, es una pieza a escribir, no a instalar.
- **Observabilidad específica de un bot de trading en producción** (más allá de los dashboards
  propios de freqtrade/FreqUI y Hummingbot) no se investigó a fondo — remite al país vecino
  `infraestructura-devops.md` (VictoriaMetrics/Grafana, Healthchecks, Uptime Kuma) para la capa
  genérica; falta el ángulo específico de trading (p. ej. alertar sobre desviación entre P&L
  esperado por el backtest y P&L real, o sobre una posición que lleva abierta más tiempo del
  parametrizado).
- **FIX Protocol e infraestructura de baja latencia real (FPGA, colocation, C++ a medida)** quedó
  fuera a propósito — el brief pide coste cero y self-hosted razonable, no HFT institucional de
  colocation; los repos encontrados en esa punta (`High-Frequency-Trading-FPGA-System`,
  `Fix-Protocol-Tranding-Engine`) son proyectos académicos/toy, no infraestructura reutilizable.
- **Brokers regulados fuera de cripto/IBKR** (Schwab/TD Ameritrade API, Tradier) no se exploraron —
  Alpaca sí se tocó (`alpaca-py`, activo, Apache-2.0; su SDK anterior `alpaca-trade-api-python` está
  archivado) pero sin profundizar en el resto del panorama de brokers US regulados.
- **Cifras autodeclaradas sin verificar**: el "$34B de volumen" de Hummingbot y afirmaciones
  similares de otros READMEs son del propio proyecto, no una medición independiente de este barrido.
- Sin datos de clientes, credenciales ni claves de API en este fichero.
