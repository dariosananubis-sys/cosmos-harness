# FIX — Auditoría 360 de COSMOS, ciclo 2 · 2026-09-03

Contrato de este ciclo: `CICLO-1/REVISION.md` (revisor único, veredicto NO al merge: 3 bloqueantes,
4 palancas del juez, 3 desmentidas, 34 parciales, 3 «no aplica» caídos, 50 hallazgos nuevos R-01…R-50
y §4.1–4.4). Más dos encargos de Darío del día: **A** (COSMOS es suyo, cero datos de la agencia) y
**B** (el verbo `cosmos configurar`).

## Cabecera

- **Rama:** `arreglos-2026-09-03`. Sin commits, sin push, sin reescritura de historia (la purga
  F-02/F-05 la ejecuta el orquestador con el permiso ya dado; el plan corregido está en
  `PENDIENTE-DARIO.md` §1). `mv … ~/.Trash/…`, nunca `rm`. Cero dinero, cero correo.
- **Pin:** `b0c1ebdeb2d9bac7e068d10714213ff2f9eda926` al empezar y al terminar (nada commiteado). El
  índice está **entero estadificado** (`git add -A`) para que `puente.secretos --todo` y
  `puente.gate` midan lo que se va a mergear (R-11).
- **Entorno:** `/usr/local/bin/python3` = 3.14.3; tokenizador `~/.cosmos/calib/bin/python`
  (`tiktoken 0.14.0`). Subagentes: GA (galaxia, fichas), GB (pueblos propios); Codex generó
  `cosmos/holdout.py` (ciclo 1) y `cosmos/configurar.py` (ciclo 2); todo lo demás, a mano y declarado.

## Los tres bloqueantes del merge (§5 de la revisión)

| Bloqueante | Estado | Qué se hizo | Verificación |
|---|---|---|---|
| **R-11** el árbol no pasa sus controles; 43 rutas de máquina + IP en ficheros sin trackear | **CERRADO** | 43 rutas → `~`; IP redactada; correo de tercero fuera (`piper`); placeholder reconocible en `keycloak`; `git add -A` y los dos controles corridos sobre el índice; las dos válvulas legítimas registradas (`P01`: el resumen de la galaxia pierde su cardinal; `P02`: retiradas del encargo A) | `puente.secretos --todo` EXIT 0 · `puente.gate --sin-pruebas` EXIT 0 (bloque final) · `grep -r /Users/$(whoami)` fuera de `.git` = 0 |
| **R-01** el juez se amaña al 100 % publicable escribiendo el examen | **CERRADO en lo estructural, declarado en lo que no se puede** | `acertar` **nunca dice «la cifra que vale»** y **`--minimo` no existe** (argparse lo rechaza, exit 2). Publica dos cosas separadas: **integridad** (sello vigente, no quemado, no versionado, historia limpia, no calcado, brecha sana) y **atribución = False siempre**, con el porqué («el examen lo escribe quien puede leer el árbol; la procedencia es una declaración, no una prueba»). Lo verificable se publica: **compromiso** (primer commit que versiona el `.SELLO` con este sha256, commits después, resúmenes cambiados desde entonces) y **calcado** (solape Jaccard petición↔línea esperada, en validación y en ajuste; umbral 20 %, calibrado: humano 6 %, tres palabras 23 %, línea entera 100 %) | Ataque del revisor reproducido (`tests/test_juez_honesto.py::NingunaCifraEsAtribuible…`): examen calcado → `CALCADO`, no íntegro; tres palabras → `CALCADO`; y en ningún caso «la cifra que vale» ni listón. M67 (atribuible→True) y M77 (sin calcado) rojas |
| **R-05** los 91 tokens de holgura son los 109 cortados del océano, sin decirlo | **CERRADO** | El párrafo del `moja` reubicado en `spec/TAXONOMIA.md`; `oceano/descender` sin la orden `cosmos buscar/abrir` (R-20); **`cosmos medir --delta`** mide HEAD y publica qué cambió: `oceano/descender 158 → 35 (−123 tokens en TODA sesión)`, `pueblos 247 → 299`, `peor con agua` antes/después; y el veredicto dice cuántas herramientas caben («≈ N herramienta(s) más en ese nicho») | `medir --delta` en el bloque final; GOAL §1 reescrito (§4.1) |

## Las cuatro palancas del juez

| Palanca | Cierre | Prueba de que no puedo amañarlo yo |
|---|---|---|
| R-01 (escribir el examen) | arriba | `NingunaCifraEsAtribuible…` (2 exámenes fabricados) + M67/M77 |
| R-02 (borrar herramientas sube nota y margen) | **P02** en el gate: toda baja neta de pueblos exige `cosmos saltar P02`; `acertar` publica «sobre N líneas de catálogo» | `test_gate.ElGateVigilaLasBajas…` (bloqueo, válvula, gate entero); M74 roja. Y la propia retirada de hoy pasó por la válvula, con motivo |
| R-09 (k1, b, IDF sin fijar) | `K1`, `B` como constantes, `_puntuar` expone las puntuaciones y **la tabla las fija por VALOR** (4,1568 / 1,2649 / 3,589 / 1,1605); docstring corregido («IDF suavizada por raíz cuadrada, no la logarítmica clásica») | `ElModeloDePuntuacionEstaFijado`; M78 (IDF logarítmica) roja — la versión por orden la dejaba pasar, la de valores no |
| R-14 (copiar el examen a los resúmenes AÑADIENDO) | P01 vigila también la **ganancia**: si un resumen modificado gana términos de las peticiones del examen que esperan a ese nodo (o a un ancestro), rojo. Lee el holdout local; en CI no está y lo dice, no lo finge | `test_ganar_terminos_del_examen_que_espera_al_nodo_se_denuncia`; M75 roja |

**Nota honesta sobre R-01:** ningún mecanismo offline y sin cuenta puede probar que quien escribió el
examen no había leído el árbol. Por eso la respuesta no es una guarda más sino **retirar la
afirmación**: la cifra de validación describe el instrumento sobre ese examen, nunca la calidad del
árbol, y el comando lo dice en cada salida. `spec/NUCLEO.md` §11 lo fija y dice cuándo se reabre el
listón (compromiso previo verificable de un tercero).

## La nota, con el juez del ciclo 2

```
python3 -m cosmos acertar     (bloque final, sobre el árbol definitivo)
```

- **Cifra honesta del árbol: DESCONOCIDA** (v1 quemado: sus 20 consultas están en la historia git).
- Cifra íntegra de v1 si se mide igual: **la del bloque final**, NO ATRIBUIBLE.
- **Matriz R-10** (código × árbol, medida con las tres copias): `main+main 8/20 (40 %)` ·
  `rama+main 7/20 (35 %)` · `rama+rama 6/20 (30 %)`. El juez pone 5 puntos, el árbol 5. La brecha
  ajuste−validación pasó de 26 a 44 puntos y se declara como magnitud de seguimiento.
- Mejora legítima del motor (E-12), declarada y medida: sufijo `-oria` y compuestos `ciber-` en el
  normalizador; ajuste 37 → 38 de 50; «auditar la seguridad de una web» pasa de no llegar a
  `ciberseguridad` a tener `ciberseguridad/ofensiva` en el 2.º puesto. Ningún resumen tocado
  (`git diff main --stat -- galaxia` lo enseña); fijado por `ElNormalizadorMejoradoEstaFijado`.

## Las tres desmentidas y los tres «no aplica» caídos

| ID | Ciclo 1 | Ahora | Verificación |
|---|---|---|---|
| D-06 | «cacheado» que hacía 33 parseos MÁS (`setdefault` no es perezoso) | `if k not in cache` + **prueba de conteo de llamadas**: 1.089 → **33** (una por co-cargable) | `test_escala.LosArreglosDeRendimiento…test_d06`; M79 roja |
| A-12 | `PROGRESS.md` jura ser generado y tiene 10 cifras caducadas; canario = `grep ciudad` | El bloque lo regenera un guion al cierre y **`test_progress_generado` reejecuta `cosmos estado` y compara**; la cabecera nombra el canario | bloque == salida del comando (bloque final) |
| F-10 | dos `curl \| bash` arreglados y dos nuevos sin aviso | GA cubrió la **clase** (`grep -lE 'curl … \| (ba)?sh'` → todas con aviso) | `CICLO-2/galaxia-GA.md` §4 |
| E-12 «no aplica» | la cifra que lo sostenía (40 %) era la retirada | Mejora legítima aplicada y declarada (arriba); el techo del método (BM25, no agente) sigue declarado | `ElNormalizadorMejoradoEstaFijado` |
| C-17 «no aplica» | `quota-oficial` leía la credencial de una suscripción de pago | **Retirado** por el encargo A (proceso interno); `revision-cruzada` sigue, genérico | `PENDIENTE-DARIO.md` §5-bis |
| F-09 «no aplica» | el CI que compensaba se pone rojo; `[skip ci]` lo derriba | R-11 cerrado y **`pre-push`** instalado por `enganchar` (repite `puente.secretos --todo`; no pisa uno ajeno; `desenganchar` lo quita) | `F09_ElPrePushRepiteElEscaneo` |

## Las 34 parciales, atacando la clase

| ID | Clase de defecto | Cierre | Verificación |
|---|---|---|---|
| B-01 | el canario solo veía pérdida | ganancia de términos del examen (R-14) | M75 |
| B-02 | procedencia falla abierta en clon superficial | `comprobada=None` con `--is-shallow-repository` o 0 blobs; CI con `fetch-depth: 0` | `LaProcedenciaEsTrivalenteDeVerdad` (clon `--depth 1` real); M76 |
| B-05 | procedencia = texto libre | se publica como «declarada, NO verificada» + compromiso verificable | salida de `acertar` |
| B-07 | holdout sin sellar se quema por `--json` | el detalle de validación se redacta SIEMPRE | `ElDetalleDeValidacionSeRedactaSiempre`; M58 |
| B-10/D-08/E-07 | `tiktoken>=0.7` abierto | versiones fijadas a `pip freeze` (tiktoken, regex, requests, charset-normalizer, idna, urllib3, certifi); `actions/checkout` por SHA; sin `--require-hashes` (declarado: ruedas por plataforma) | `requirements-dev.txt`, workflow |
| A-10 | mensaje de E16 con exceso negativo | `excede = con_margen − presupuesto`, y el mensaje enseña estimación + margen | `R06_ElMensajeDeE16…` (validar y medir publican el mismo exceso) |
| A-02 | la fuga se publicaba, no se cerraba | `compilar` **se niega** a aplanar la vista completa en un directorio que el runtime escanea (`.claude/skills`, `.agents/skills`) sin `--todos`; y en symlink hacia esos directorios también (invisible) | `R22_LaVistaCompiladaLaVeElRuntime` (dos negativas) |
| A-04 | el test petrificaba la ambigüedad | **centinela partido**: `nichos=None` = ninguno también al compilar; la vista completa es `todos=True`; el manifiesto conserva `nichos: null` por compatibilidad | `test_nichos_semantica` reescrito; `test_nichos_none_ya_no_es_todos_en_la_api` |
| A-04 bis | dos lectores del mismo TOML (`cli.nichos_de_configuracion` y `modelo.cargar_configuracion`, sin `[nichos]`) — lo señalaba D §5 | un solo lector: `cargar_configuracion` lee y valida `[nichos] activos`; `nichos_de_configuracion` delega. Salió al cerrar: el test del árbol de ejemplo veía E19 por esta divergencia | `test_ejemplo_completo_es_verde` |
| A-06 | E21 lo satisfacía `https://` en prosa | URL de repositorio en la **primera línea** (`https://host/org/proyecto`), sin marcadores; **`origen: propio` exige un guion en el directorio** (R-37) | `A06_E21…` (prosa, marcador, segunda línea, sin guion); M72 |
| A-11 | se borró, no se reubicó | párrafo del `moja` en `TAXONOMIA.md`; descender sin verbos (R-20) | `ElBloqueRealNoMandaEjecutarCosmos` (océanos reales) |
| A-14 | 34/34 entradas en `universo` | sin cambio: todo lo hecho es trabajo sobre COSMOS mismo y `universo` es su nicho correcto; se declara, no se fuerza | — |
| E-01 | orden `cosmos` en el océano proyectado | quitada; test sobre el bloque real | `ElBloqueRealNoMandaEjecutarCosmos` |
| E-02 | vista compilada 306/306 sin `name` | `compilar --modo copia` traduce el `SKILL.md` (mismo `para_el_anfitrion`) y el hash esperado lo incluye (E19 no lo confunde con edición); `ejemplo.toml` pasa a copia y acota su oficio | `R22…test_en_copia…` |
| E-13 | regla sin test | `E13_AbrirDescribeLasHojasYNombraLosIntermedios` | verde |
| F-02 | plan de purga inválido | plan corregido (sintaxis, `--force`, `origin` guardado, `set -euo pipefail`, el valor en fichero 600 y borrado) — sin ejecutar | `PENDIENTE-DARIO.md` §1 (R-38) |
| F-03 | atribución falsa nueva (`origen: propio` en código ajeno) | `auditor-de-skills` sin `origen`: primera línea con la URL real, MIT leída, 25.450★; NOTICE | E21 verde |
| F-08 | media corrección | `OPENCLAW_TELEGRAM_USER_ID`, `export`, sin nombre de la agencia (R-39); `cosecha/` retirada (§4.3): ya no hay gemelo que olvidar | `grep <agencia>` = 0 |
| F-11 | evidencia con instrumento ciego | barrido del árbol entero (no `git grep`) y cero ocurrencias; patrón del escáner activo | bloque final |
| D-04 | `utf-8-sig` en un solo sitio | también en `proyectar.para_el_anfitrion` (R-43) | — |
| D-05 | guarda de raíz para 2 verbos | **una** guarda para todos los verbos que cargan el árbol; fuera las copias de `medir` y `buscar` (R-44) | `D05_…`; M50 |
| D-10 | rama de lectura sin test | `test_d10_el_error_de_lectura_lleva_ruta_relativa` (chmod 000) | verde |
| D-11 | frontera abierta hacia dentro | un enlace dentro de la raíz se denuncia como ENLACE (no se carga, no duplica, no culpa al original) (R-40) | `R40_…` |
| D-01 | caché por `len` | clave `(len, id(lista))` + `Arbol.invalidar()` para mutaciones en sitio (R-41); `normalizar_nichos` también usa la caché | `R41_…`; `test_d01…` (conteo) |
| E-03 | rutas absolutas y sin `--quiet` | acciones relativas al cwd; `--quiet` en `compilar`/`arrancar` (R-50) | `E03_…` |
| E-06 | hook muere en silencio | `${CLAUDE_PROJECT_DIR:-.}` + mensaje de sistema si `python3` < 3.11 (R-48) | `E06_…` |
| E-10 | `--help` sin aviso; en nodos | aviso en `--help` y en la primera línea, **en tokens medidos** sobre el propio volcado (R-42) | `cosmos mapa \| head -1` |
| E-11 | cifras de otro árbol | §Cerrado regenerado por guion con el pin del árbol de hoy (R-49) | `docs/CALIBRACION.md` |
| E-15 | fusión superficial borra claves anidadas | fusión recursiva (R-46) | `test_settings_no_se_reordena…` + anidada |
| C-01 | añadido sin retirar | el coste del oficio se publica; retirar es decisión de Darío (§5) | — |
| C-03 | 3 de 6 comandos rotos | GA: `vector` (tap), `grafana`/`vector`/`loki` con uso real ejecutable | `galaxia-GA.md` |
| C-05 | Node sin perfilador de memoria | GA añadió `memlab` (verificado vivo) | `galaxia-GA.md` §10 |
| C-06 | los 6 genéricos siguen en `trading` | se quedan: no hay país neutro que los contenga (el agua no contiene); los mares los nombran | declarado |
| C-08 | pueblos propios mal presentados | `bing-webmaster`, `search-console`: `origen: propio`, y sus imports rotos arreglados (GB) | E21 verde |
| C-09 | `mythril` decía «vivo» | GA corrigió con el `.atom` de hoy, coherente con `medusa` (R-26) | `galaxia-GA.md` |
| C-10 | sesgo no declarado | declarado en `spec/UNIVERSO.md` («el hardware no decide qué entra») | — |
| C-13 | contador en las dos direcciones | fecha con `\s+`; rival exige verbo comparativo + identificador (R-23) | `cosmos estado` |
| C-14 | FIX describía mal lo hecho | corregido aquí: en el ciclo 1 se puso la URL real y una línea de origen; `origen: propio` lo añadí después por error y hoy se quita (es código ajeno, MIT) | E21 verde sin `origen` |
| C-15 | provincia «distribución» no creada; `butler` roto | GA creó la provincia y arregló `butler` (descarga oficial de itch.io; aviso de los dos falsos amigos); **la provincia con un solo hijo incumple la taxonomía** (`test_oficios_estructurados`) y se retiró: `butler` vuelve a `juegos/motores` hasta que haya una segunda herramienta viva | `PENDIENTE-DARIO` §5-bis |

## Los 50 hallazgos nuevos (R-01…R-50) y §4

| ID | Estado | Nota |
|---|---|---|
| R-01, R-02, R-09, R-14 | CERRADO | las cuatro palancas (arriba) |
| R-03 | CERRADO | `clon-en-frio.sh` copia el árbol de trabajo, lo convierte en repo y lo clona: mide lo que se va a mergear |
| R-05, R-06, R-08, R-10, R-11 | CERRADO | arriba |
| R-15, R-16 | CERRADO (GA) | `vector` por tap; `butler` por la descarga oficial; y la **clase**: 104 paquetes `brew` cruzados contra la base de Homebrew, 4 inexistentes corregidos |
| R-17 | CERRADO | procedencia trivalente (superficial / 0 blobs → `None`); `versionado` trivalente publicado; `fetch-depth: 0` |
| R-18 | CERRADO | E21 estricta; 12 pueblos que pasaban por accidente resueltos (9 `origen: propio` con guion, `kokoro` y `auditor-de-skills` con la URL en la primera línea, `web-fidelidad-elementor` retirado) |
| R-19 | CERRADO | canario real de `PROGRESS.md` |
| R-20, R-21, R-22, R-23, R-24 | CERRADO | arriba / GA |
| R-25 | CERRADO | correo del tercero fuera; IP redactada |
| R-26, R-27 | CERRADO (GA) | `mythril` coherente; `qdrant` con el `.atom` de hoy, y la clase (59 fichas releídas) |
| R-28 | CERRADO | este FIX reconcilia sus recuentos (abajo) |
| R-29, R-30, R-31, R-32 | CERRADO | «los los»; cifra a mano del README fuera; canario por palabra entera; canario `ciudad` sobre `galaxia/**` incluidos los pueblos |
| R-33, R-34, R-35, R-36 | CERRADO (GA) | rivales en `nmap`/`osquery`/`wireshark`; SQL en bloque `sql`; usos reales en `grafana`/`vector`/`loki`; colisiones `httpx`/`arrow` declaradas |
| R-37 | CERRADO | `origen: propio` exige guion (E21) |
| R-38 | CERRADO (texto) | plan de purga corregido, sin ejecutar |
| R-39 | CERRADO | nombre de la agencia fuera de los guiones |
| R-40, R-41, R-42, R-43, R-44, R-45, R-46, R-47, R-48, R-49, R-50 | CERRADO | arriba |
| §4.1 | CERRADO en contrato | GOAL §1 dice lo que el medidor mide (el coste crece con el oficio más poblado, no con el universo); `medir` publica cuántas herramientas caben |
| §4.2 | CERRADO en contrato | `spec/PUEBLO.md` declara la premisa de plataforma (macOS/Homebrew salvo que la ficha diga otra cosa) |
| §4.3 | CERRADO | `cosecha/` retirada; documentado en `TAXONOMIA.md` |
| §4.4 | CERRADO | el bloque de verificación de este FIX incluye `secretos --todo` y `gate --sin-pruebas` sobre el índice, y el clon en frío del árbol real |

## Encargo A — COSMOS es de Darío: cero datos de la agencia

- Barrido del árbol entero (sin `.git`): rutas `/Users/<usuario>` = **0**; `<agencia>`, `<agencia>`,
  `<arnes>`, `<producto>`, `Omnia`, `<cliente>`, `<usuario>` = **0** fuera de los informes
  originales de la auditoría (que son evidencia y no se editan). `research/<agencia>-HARNESS.md` →
  `research/ARNES-DE-ORIGEN.md`; la decisión del registro renombrada; los marcadores del arnés de
  origen (`.generated-by-…`, `managed-by-…`) genéricos.
- **37 pueblos propios revisados uno a uno (GB):** 30 se quedan **reescritos en genérico** (rutas
  `tools/` → `scripts/`, hosts de proveedor → variables, sistemas de diseño de un producto fuera,
  slugs de clientes fuera de `legales-lssi.py`, imports rotos arreglados) y **7 salen** por describir
  el proceso interno de la agencia. Más `web-fidelidad-elementor` (prosa de «esta casa» sin guion) y
  `cosecha/`. Todo en `~/.Trash/cosmos-retirados-2026-09-03/`, reversible.
- `LICENSE` Apache-2.0 a nombre de Darío Satiño (decidida por él) y `NOTICE` actualizado.

## Encargo B — `cosmos configurar`

`cosmos/configurar.py` (Codex, 210 líneas, validado) + el verbo en `cosmos/cli.py`:

1. Pregunta los **oficios** (o `--oficios a,b`) → `~/.cosmos/perfil.toml`; sin nichos en
   `cosmos.toml`, mandan los del perfil (el resto duerme).
2. Por oficio, las **herramientas** (o `--herramientas x,y`) → solo esas entran en el catálogo y en
   la vista del usuario. **El juez E16 no cambia**: mide el peor nicho entero (NUCLEO §2 bis).
3. `~/.cosmos/credenciales.txt` con las variables que piden esas fichas (`VAR=` vacías, pista de
   dónde se saca), y `open -t` (o `--no-abrir`).
4. `--comprobar`: lee, dice `FALTA` / `SOSPECHOSA` (marcadores, valores cortos), y **se lo queda**
   (`credenciales_comprobadas = true`).
5. Directorio 700, ficheros 600, fuera del repo. En el repo solo `docs/credenciales.plantilla.txt`;
   `.gitignore` y el escáner (`credenciales*.txt`, `perfil.toml` prohibidos; la plantilla permitida).
6. `--llavero` (`security add-generic-password -s cosmos/<VAR> -U`) y vacía el txt; `--seco` enseña
   las órdenes **sin el valor**.

Verificación: `tests/test_configurar.py` (alta, comprobar, llavero en seco, marcador sospechoso,
oficio dormido rechazado, no pisa valores, el repo no puede contener credenciales); flujo interactivo
probado con `printf 'juegos\ntodos\n' | cosmos configurar …`; `COSMOS_PERFIL=… cosmos medir` enseña
«Nicho activo … juegos; 10 pueblos». Documentado en README («El alta») y NUCLEO.

## Recuento reconciliado (R-28)

Del ciclo 1: 74 ARREGLADO, 3 PENDIENTE-DARIO, 3 NO APLICA (esta tabla no dice 71 en ningún sitio).
De este ciclo: **3/3 bloqueantes cerrados · 4/4 palancas · 3/3 desmentidas · 3/3 «no aplica» caídos
resueltos · 34/34 parciales atacadas por clase (2 declaradas sin cambio y por qué: A-14, C-06) ·
50/50 R cerrados (R-38 como texto, sin ejecutar) · §4.1–4.4 cerrados**. Pendiente de Darío: la purga
de historia (§1-2), las 17 retiradas (§5), el holdout v2 (§6), conservar o retirar el código ajeno
MIT (§4), el hook local (§8).

## Verificación global (pegada al cierre)

Batería final ejecutada al cierre del ciclo 2. Salidas íntegras en `CICLO-2/verif/`.
Este bloque lo pega el orquestador tras comprobar cada salida a mano (el fixer cerró turno
esperándola); nada de lo de abajo es una afirmación suya sin verificar.

```
python3 -m unittest discover -s tests        Ran 359 tests in 77.377s  ·  OK  (0 skipped)
python3 -m unittest discover -s puente/tests Ran 139 tests             ·  OK
python3 -m cosmos validar                    verde · 0 errores (2 saltos activos P01/P02, caducan en 7 d)  EXIT=0
python3 -m puente.gate --sin-pruebas         arrancar verde · vista compilada                              EXIT=0
python3 -m puente.secretos --todo            limpio de nuevos; 3 inventariados en secretos-conocidos.txt   EXIT=0
mutaciones                                   79/79 invariantes vistas fallar                               EXIT=0
clon en frío                                 9/9 pasos en verde, 5,86 s · 0 ocurrencias de /Users/ en settings.json
python3 -m cosmos medir                      peor con agua 3.701 · 299 pueblos · oceano/descender −123 tok/sesión
```

**Contraste con el ciclo 1:** mutaciones 73/79 → **79/79** (ninguna guarda queda decorativa);
`gate` y `secretos` EXIT 1 → **EXIT 0** (el primer push ya no sale rojo); clon en frío 8/8 → **9/9**,
ahora con el paso que comprueba que los hooks no llevan rutas de esta máquina.

**Lo que este bloque NO dice:** nada sobre la nota. El holdout sigue quemado y `acertar` ya no
publica «la cifra que vale» (R-01). La nota honesta seguirá siendo DESCONOCIDA hasta que exista el
holdout v2 ciego (PENDIENTE-DARIO §6).

