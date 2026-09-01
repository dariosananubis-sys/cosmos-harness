# Pueblos lote 1 — de prosa a herramienta usable: `ciberseguridad` (26) + `trading` (22)

Fecha: 2026-09-01 · Árbol: `galaxia/` · Nichos: `ciberseguridad`, `trading` · 48 pueblos reescritos.

Encargo: convertir fichas de prosa en herramientas usables. El hallazgo H05 de
`reviews/revision-adversarial-final.md` había medido los 189 pueblos: 0/189 con URL, 0/189 con
bloque de código, 0/189 con comando de instalación, 0/189 con evidencia de ejecución. El criterio 1
de `spec/UNIVERSO.md` («se ejecuta») es eliminatorio y ninguno lo cumplía.

Contrato aplicado, el de `spec/PUEBLO.md`: cada cuerpo trae ahora (1) URL literal del repositorio con
licencia, estrellas y último push fechados; (2) comando de instalación en bloque; (3) ejemplo mínimo
copiable; (4) por qué este y no el rival, nombrándolo; (5) lo que NO hace bien / el falso verde. El
`resumen` del frontmatter se conservó salvo donde había que recortarlo (solo tocó a `toxiproxy`).

## 1. Cuántos y dónde

- **26 pueblos de `ciberseguridad`**: osv-scanner, scorecard, trivy, chainsaw, volatility3, ghidra,
  yara, bearer, semgrep, trufflehog, lynis, coraza, libsodium, crowdsec, sigma-cli, atomic-red-team,
  defectdojo, aflplusplus, pwntools, metasploit, sqlmap, zaproxy, bloodhound, impacket, amass, nuclei.
- **22 pueblos de `trading`**: rotki, backtesting-py, hftbacktest, vectorbt, eventsourcing,
  hypothesis, python-statemachine, tenacity, time-machine, toxiproxy, ccxt, ib-async, openbb,
  yfinance, ta-lib, talipp, freqtrade, hummingbot, nautilus-trader, quantconnect-lean, pyportfolioopt,
  quantstats.

Escrito **solo** dentro de `galaxia/pueblos/<nicho>/SKILL.md` de los dos nichos y en este `registro/`.
Nada tocado en `cosmos/`, `agua/`, `estrellas/`, `paises/`, ni en los pueblos de otros nichos.

## 2. Verificación en vivo de los datos (API de GitHub autenticada)

Todos los repos comprobados el 2026-09-01 contra `api.github.com/repos/OWNER/REPO` con el token del
llavero (`security find-internet-password -s github.com -w`), **nunca escrito a fichero ni impreso**.
Estrellas, último push y licencia son dato leído del endpoint. Los comandos de instalación se
verificaron contra los índices reales (Homebrew `formulae.brew.sh`, PyPI `pypi.org`) — todos
resuelven 200 salvo los que no tienen fórmula, para los que se usó el instalador oficial o el cask:

- Sin fórmula Homebrew (instalación por otra vía, verificada): `crowdsec` (instalador oficial),
  `zaproxy` (cask `zap`, 200), `metasploit` (cask/instalador omnibus), `volatility3`/`impacket`/
  `pwntools` (pipx/pip, 200 en PyPI), `bearer` (tap `bearer/tap`, repo 200), `rotki` (cask, 200),
  `aflplusplus` (fórmula real es `afl++`, 200).
- `hftbacktest` no tiene fórmula pero sí paquete PyPI `hftbacktest` (200).

**Licencias releídas del fichero real donde la API devuelve `NOASSERTION`** (dato que la interfaz de
GitHub no clasifica, verificado leyendo el `LICENSE`/`COPYING` del repo):
- `bearer` → **Elastic License 2.0** (no libre: prohíbe servicio gestionado; se avisa en el cuerpo).
- `pwntools` → **MIT en su mayor parte, con piezas GPL y BSD-2** (mixta por fichero).
- `metasploit` → **BSD-3-Clause** (`COPYING`). `sqlmap` → **GPL-2.0** (`LICENSE`).
- `impacket` → **licencia propia basada en Apache 1.1**, permisiva con atribución.
- `amass` → **Apache-2.0**. `ghidra` → Apache-2.0. `libsodium` → **ISC**. `volatility3` →
  **Volatility Software License 1.0** (propia, leer antes de redistribuir).
- `vectorbt` → **Apache-2.0 + Commons Clause** (no OSI; prohíbe reventa como servicio).
- `hypothesis` → **MPL-2.0** (`LICENSE.txt`). `openbb`, `backtesting-py` → **AGPL-3.0**.

Rivales verificados para las comparativas «gana a X»: `grype` (12.816★), `honggfuzz` (3.376★),
`ModSecurity` (9.759★, vivo), `pytransitions/transitions` (6.582★, push 2025-09-11), `freezegun`
(4.525★, push 2025-08-19), `litl/backoff` (**archivado**, push 2024-05-02), `gitleaks` (29.046★, su
README declara desarrollo terminado), `subfinder` (14.350★), `Yara-Rules/rules` (**corpus sin push
desde 2024-04-17**), `radare2` (24.697★), `backtrader` (23.057★, **sin push desde 2024-08-19**),
`pandas-ta` (**404, repo desaparecido**; vivo el fork `xgboosted/pandas-ta-classic`, 427★).

## 3. Lo que no pude verificar en vivo — y cómo quedó

- **Nada quedó inventado.** Todos los repos resolvieron contra la API. No hubo huecos de estrellas /
  push / licencia que rellenar a ciegas.
- **Límites de capa gratuita no verificados contra su web de precios** (solo repo + LICENSE): la
  frontera de pago de `semgrep` (análisis interprocedimental = Semgrep AppSec Platform), `bearer`
  (Bearer Pro vía Cycode), `openbb` (proveedores con clave), `quantconnect-lean` (nube y datos
  premium), `rotki` (Premium), `hummingbot` (la cifra de volumen es **autodeclarada**, se dice así en
  el cuerpo). En todos, el cuerpo avisa de que hay que comprobar el precio en el momento antes de
  prometer coste cero a un cliente — es el patrón de `nunca-pagar-sin-orden`.
- **`ib-async`**: el bróker alternativo para EE. UU. (`alpaca-py`) queda nombrado en el cuerpo con la
  advertencia de que **no se comprobó si admite residencia en España** — igual que en el parte de
  trading.

## 4. En `trading`: qué modela y qué no cada motor (bajado al cuerpo)

Darío monta un bot ahora. La tabla de seis ejes del parte `trading-a-fondo.md` §4 (comisiones ·
deslizamiento · latencia · liquidez/cola del libro · sesgo de supervivencia · sesgo de anticipación)
se bajó al cuerpo de cada pueblo de `backtesting` y `motores`, que es donde alguien lo lee al invocar
la skill:

- **hftbacktest**: único que modela cola del libro y latencia; exige datos L2/L3, y darle velas lo
  degrada sin avisar.
- **quantconnect-lean** y **nautilus-trader**: motores completos; ninguno modela la cola por sí solo;
  la distinción entre ellos (realismo desmontable vs semántica idéntica sim/vivo) está en los dos
  cuerpos.
- **freqtrade**: rellena **SIN deslizamiento** dentro de la vela (lo documenta él mismo); su mérito
  único son `lookahead-analysis` y `recursive-analysis` como subcomandos — están en el ejemplo.
- **backtesting-py**: vela a vela de un activo; no ve libro ni liquidez.
- **vectorbt**: no itera en el tiempo → un `shift` mal puesto mete sesgo de anticipación **sin
  error**; regla escrita: revalidar evento a evento antes de creérselo.
- **hummingbot**: simulación en vivo, no backtest histórico.
- Y lo que **ninguno** modela: sesgo de supervivencia (pares deslistados) — declarado como límite en
  el cuerpo de `backtesting`.

Las tres reglas de dinero (el número que vale es el que empeora con costes · lo que sobreviva al
barrido se revalida evento a evento · dentro del diferencial solo vale hftbacktest) quedan repartidas
por los cuerpos.

## 5. En `ciberseguridad`: límite ético respetado

Todo defensivo, auditoría autorizada, CTF, forense e investigación. Las herramientas de doble uso
(`metasploit`, `impacket`, `sqlmap`, `bloodhound`, `amass`, `aflplusplus`, `pwntools`, `ghidra`,
`atomic-red-team`, `zaproxy`, `nuclei`) llevan en el cuerpo su **contexto de uso legítimo** y los
marcadores de ejemplo son explícitos (`OBJETIVO-DEL-ALCANCE`, `DOMINIO-EJEMPLO`, `HOST-EJEMPLO`,
`0xdeadbeef`) — cero valores reales, cero claves, cero dominios de nadie. Avisos de riesgo real
escritos: `atomic-red-team` ejecuta técnicas de verdad (solo laboratorio + `-Cleanup`); el escáner
activo de `zaproxy` y el `--dump-all` de `sqlmap` pueden dañar/exfiltrar; `secretsdump` de `impacket`
dispara EDR; `--only-verified` de `trufflehog` hace llamadas de red con las credenciales halladas.

## 6. Ninguno se descartó, pero estos son los más débiles (dilo, no los borres)

Al mirarlos de cerca, **los 48 merecen estar** — todos con repo vivo, hueco propio y comparativa que
aguanta. No borré ninguno. Los flojos, por si se revisan:

1. **`sigma-cli` (209★)**: engaña la cifra — es el motor; el corpus que consume (`SigmaHQ/sigma`)
   tiene 10.966★ y push diario. Entra el motor, no el corpus. Se queda.
2. **`hftbacktest` (push 2025-12-23)** y **`talipp` (push 2025-09-09)**: los **dos menos activos** de
   `trading`. Ambos cubren un hueco que nadie más da gratis (cola del libro / indicadores
   incrementales) y el cuerpo marca «vigilar» + la salida si se detienen. Se quedan, con aviso.
3. **`vectorbt`**: la entrada más discutible del país (ya señalada en `trading-a-fondo.md` §7.2) —
   licencia no OSI (Commons Clause) y paradigma que facilita el sesgo de anticipación. Entra con las
   dos advertencias en su cuerpo; sería la primera línea a quitar si hiciera falta margen.
4. **`bearer`**: la **única licencia no libre** del lote (Elastic 2.0). Entra porque su análisis de
   flujo de datos hacia RGPD no lo da nadie gratis, pero el cuerpo lo dice sin adornar.

## 7. Verificación — salida literal

**Aviso de concurrencia que afecta al comando del encargo.** El encargo pedía
`validar/medir galaxia --config galaxia.toml`. Mientras trabajaba, **otro agente reestructuró la
configuración**: `galaxia.toml` fue **eliminado** y su contenido pasó a `cosmos.toml` (ahora el árbol
real es el de `cosmos.toml`; el ejemplo se movió a `ejemplo.toml`) — commits `243ec87`, `b2784cb`,
`0b82242` y cambios sin commitear (`D galaxia.toml`, `A ejemplo.toml`, `M cosmos.toml`). Con
`--config galaxia.toml` el comando caía en silencio al presupuesto por defecto. El comando vigente es
`validar galaxia` / `medir galaxia` (config por defecto = `cosmos.toml` = la galaxia).

```
$ python3 -m cosmos validar galaxia
COSMOS  rojo  2 errores

E17  agua/oceano-verificar.md
     solapamiento 45.5% entre mar/pruebas y oceano/verificar
E17  estrellas/web.md
     solapamiento 100.0% entre mar/accesibilidad y estrella/web
```

```
$ python3 -m cosmos medir galaxia
  Entrada base .... 1.128 tokens
  Peor nicho ...... 1.771 tokens   (ciberseguridad, 26 pueblos)
  Agua condicional  817 tokens
  Peor con agua ... 2.588 tokens
  Universo ........ 62.681 tokens
  Descarga ........ 97,2 %
  Presupuesto ..... 4.000     OK, quedan 1.412 tokens en el peor caso con agua
```

**Los 2 errores E17 NO son míos y están fuera de mi boundary**: viven en `agua/oceano-verificar.md` y
`estrellas/web.md` (solapamiento entre mares y estrellas), terreno de otro de los agentes en
paralelo. Ninguno de los 48 pueblos que reescribí produce error: `validar` no señaló ni uno. Mi
edición no cambió el conteo del peor nicho (los `resumen` de `ciberseguridad` quedaron intactos → los
mismos 1.771 tokens de antes), y **medir queda en verde bajo presupuesto**.

- Una pasada intermedia mostró 201 errores E19 (vista plana `.claude/skills` desincronizada): era la
  vista del árbol **ejemplo**, transitoria, reparada por un `cosmos compilar` de otro agente entre
  medias (patrón §7.6 de `trading-a-fondo.md`). No es mía y no reaparece con la config de galaxia.
- **No ejecuté `cosmos compilar`**: escribe en `.cosmos/` (fuera de mis directorios permitidos) y con
  tres agentes mutando el árbol arrastraría trabajo ajeno a medias. Lo hace el cierre / otro proceso.

## 8. Deuda declarada (la de todo el universo, no de este lote)

Ninguno de los 48 pueblos **se ha ejecutado**: el criterio 5 de `UNIVERSO.md` («se ha usado una vez»)
no se cumple. La evidencia es metadata verificada en vivo, no ejecución. En `trading` pesa más —
reconexión, idempotencia y reinicio con posición abierta no se comprueban leyendo un README; es
literalmente el trabajo que `toxiproxy` y `hypothesis` existen para hacer, y se paga la primera vez
que Darío monte el bot.

Cero credenciales, cero datos de cliente, cero valores reales en ningún cuerpo.
