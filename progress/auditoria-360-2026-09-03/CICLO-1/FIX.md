# FIX — Auditoría 360 de COSMOS, ciclo 1 · 2026-09-03

## Cabecera

- **Rama:** `arreglos-2026-09-03` (desde `main`). Sin commits, sin push, sin reescritura de historia.
- **Pin inicial:** `b0c1ebdeb2d9bac7e068d10714213ff2f9eda926` (main). `git status` limpio salvo los
  informes de la auditoría.
- **Pin final:** el mismo `b0c1ebd` (nada commiteado — el merge lo hace el orquestador cuando el
  revisor apruebe). Árbol de trabajo: 197 rutas cambiadas (128 tracked + 69 pueblos nuevos),
  `pruebas/encargos-validacion.json` borrado del árbol (el examen ya no viaja en el repo).
- **Entorno:** `/usr/local/bin/python3` = Python 3.14.3. Sin venv en el repo (paquete de biblioteca
  estándar por diseño). Tokenizador de calibración: `~/.cosmos/calib/bin/python` con `tiktoken 0.14.0`
  (software libre, `pip install`, cero coste). El `/tmp/calib` que citaba el registro ya no existe.

## La nota, medida con el juez ya arreglado

**Arreglar el juez NO era subir la nota, y la nota BAJÓ. Eso es el resultado correcto** (PLAN §1.2):
una báscula honesta que marca menos vale más que una amañada que marca más.

```
python3 -m cosmos acertar
  Ajuste ......... 37/50 (74 %; IC95 60–84 %)
  Validación ..... 6/20 (30 %; IC95 14–52 %; n=20)
  Historia git ... QUEMADO: 20 de 20 peticiones ya están en el repositorio: examen visto
  La cifra de validación NO es publicable: · QUEMADO ...
  Mientras no haya un conjunto ciego, sellado y con procedencia, la cifra honesta es DESCONOCIDA.
```

- **Cifra honesta publicable hoy: DESCONOCIDA.** El único holdout (v1) lo escribió quien ajustaba el
  árbol y sus 20 consultas están en la historia git: el juez arreglado lo declara QUEMADO y se niega
  a publicar cifra. Antes ese mismo conjunto daba «la cifra que vale es 40 %» sin pestañear.
- **Si se mide igualmente** (para dejar el número, no para publicarlo): **30 % (IC95 14–52 %, n=20)**,
  frente al 40 % que el PLAN daba por bueno. Bajó 10 puntos por el fix B-08: el juez ahora puntúa la
  línea **literal** que el agente lee (nombre + resumen), no la ruta completa que inflaba el número.
- El **75 %** del enunciado sigue retirado (conjunto quemado); el 40 % del PLAN también deja de ser
  publicable. Recuperar una cifra honesta necesita el holdout v2 ciego (PENDIENTE-DARIO §6).
- Está **demostrado** que ya no se puede inflar por el camino de B-01: el gate P01 bloquea vaciar
  resúmenes, la brecha ≤ −15 es alarma no publicable, el sello roto no da cifra, `--minimo` sale 1 en
  todos esos estados, y las mutaciones M60–M73 exigen el rojo de cada puerta.

## Verificación global (pegada)

```
python3 -m cosmos validar                       -> COSMOS  verde  0 errores
python3 -m cosmos medir                         -> peor con agua con margen OK, quedan 91 tokens (ciberseguridad)
python3 -m unittest discover -s tests -t .      -> Ran 320 — OK   (con ~/.cosmos/calib/bin/python y COSMOS_EXIGE_TOKENIZADOR=1: OK, sin saltos)
python3 -m unittest discover -s puente/tests    -> Ran 132 — OK
python3 -m puente.tests.mutaciones              -> 73/73 invariantes vistas fallar
```

Salidas completas en `CICLO-1/verif/`. La suite núcleo, con el tokenizador exigido, corre **320
pruebas OK sin un solo salto**: el margen ±5,2 % queda verificado en la ejecución, no prometido.

**Regresión — clon en frío:** 8/8 pasos en verde sobre el árbol de trabajo (`CICLO-1/clon-en-frio.sh`).
Ningún paso roto. `arrancar` pasó de **262 líneas / ≈9.980 tokens** a **10 líneas / 554 bytes** (E-03).
El paso nuevo `acertar` sobre un clon sin holdout dice `NO DISPONIBLE`, no un número (correcto).

**Galaxia:** 247 → **306 pueblos** (G1 +17, G2 +21, G3 +21), 22 oficios intactos, cero repetidos,
cero `usa:` roto. Peor nicho ciberseguridad 2.484 tok; con agua y margen quedan 91 tokens de 4.000.

---

## Tabla de los 80 hallazgos

Estados: **ARREGLADO** · **PENDIENTE-DARIO** (preparado, necesita su sí — detalle en
`PENDIENTE-DARIO.md`) · **NO APLICA** (falso positivo o limitación declarada, con la medición que lo
sostiene). Ninguno queda `NO VERIFICADO`.

### P0 — La báscula

| ID | Estado | Qué se hizo | Verificación |
|---|---|---|---|
| B-01 | ARREGLADO | Holdout fuera del repo + procedencia + brecha-alarma + **canario P01** en el gate contra resúmenes vaciados | `cosmos acertar` no publica cifra sobre v1 quemado; mutaciones M62/M68/M69/M73 rojas |
| B-02 | ARREGLADO | Holdout a `~/.cosmos/holdout/` (o `$COSMOS_HOLDOUT`), `.gitignore` + comprobación contra la historia git de toda consulta | `git ls-files pruebas | grep validacion.json` = 0; M63/M64 rojas; `test_juez_honesto` |
| B-03 | ARREGLADO | Brecha ≤ −15 = alarma no publicable (era un elogio); `--minimo` sale 1 | árbol inflado (ajuste 64 / val 100) → NO publicable; M62 roja |
| B-04 | ARREGLADO | `_acierta` fijado con tabla de casos límite + mutaciones en las dos direcciones | M60/M61 rojas; `LaReglaDeCorreccionEstaFijada` |
| B-05 | ARREGLADO + PENDIENTE-DARIO | Procedencia declarada en el sello + comprobación git; el holdout v2 ciego lo dicta Darío | procedencia en la salida; §6 de PENDIENTE-DARIO |
| B-06 | ARREGLADO | Cifra siempre con `n` e IC95 de Wilson | `intervalo_wilson(8,20)=(21.9,61.3)` reproduce el informe |
| B-07 | ARREGLADO | Sello roto → NO publicable y `--minimo` 1 (antes decía «no publicable» y a la vez «la cifra que vale») | M65/M67 rojas; `ElSelloRotoNoDejaCifra` |
| B-08 | ARREGLADO | El juez puntúa la línea literal del catálogo (`lineas_de_catalogo`), no la ruta completa | la nota bajó 40→30 %, medido; M66 roja |
| B-09 | ARREGLADO + PENDIENTE-DARIO | Cobertura de oficios y profundidad publicada; v2 con n≥100 y los 22 oficios lo dicta Darío | `Cobertura ... 20/22 oficios` en la salida; §6 |
| B-10 / D-08 / E-07 | ARREGLADO | Venv de calibración fuera de `/tmp` (`~/.cosmos/calib`) + job `calibracion` en CI con `COSMOS_EXIGE_TOKENIZADOR=1` + `requirements-dev.txt` | 320 tests OK **sin saltos** con el tokenizador |
| D-03 | ARREGLADO | `_comprobar_e16` trivalente: `cabe is None` no cae por la rama «excede» | árbol vacío: `validar` E05 (no E16 absurdo), `medir` SIN MEDIR; `test_arbol_vacio` |
| A-10 | ARREGLADO | `medir` publica ±5,2 % medio **y** peor caso 33,6 %; E16 evalúa con el margen calibrado encima | salida `medir`; `test_validador` exige rojo con presupuesto en la estimación desnuda |
| A-07 | ARREGLADO | 4 cifras petrificadas al registro de `test_cifras_de_las_specs` + corregidas | `test_cifras_de_las_specs` OK |
| F-01 | ARREGLADO | La excepción del escáner se compara por **huella del valor** (sha256[:12]), no por fichero×clase; un secreto por valor | `test_secretos.LaExcepcionIndultaUnValorNoUnFichero` |

### P1 — El contrato

| ID | Estado | Qué se hizo | Verificación |
|---|---|---|---|
| A-01 | ARREGLADO | `cosmos generar` compone el cardinal contando el árbol; el `resumen` de la galaxia sin números + canario | índice dice «22 oficios…»; `LaCabeceraDelIndiceSeCuentaNoSeEscribe` |
| A-02 | ARREGLADO | Magnitud `Vista compilada` en `medir` (mide el manifiesto) + aviso «vista COMPLETA» al compilar + fila de la spec corregida | `medir` publica «Vista compilada … N entradas» |
| A-03 | ARREGLADO | `GOAL.md` §7.2 reescrito: número con el método declarado y margen, nunca «no_medido» como cero | GOAL §7.2 |
| A-04 | ARREGLADO | `nichos=None` documentado con sus dos sentidos (catálogo=ninguno, compilar=todos) en `cosmos.toml` y NUCLEO §5 + test conjunto | `test_nichos_semantica` |
| A-05 | ARREGLADO | Repuestas E00,E17–E20 en `VALIDADOR.md` + canario de completitud de la tabla | `LaTablaDeInvariantesEstaCompleta` |
| A-06 | ARREGLADO | Invariante **E21** (URL o `origen: propio` + bloque de código) + `cosmos estado` cuenta el resto del contrato | `A06_E21_UnPuebloNombraQueEjecutar`; M72 roja |
| A-08 | ARREGLADO | §E16 de `VALIDADOR.md` reescrita (`entrada_con_agua`, clave real `[presupuesto] entrada`) + canario | `test_e16_describe_lo_que_el_codigo_compara` |
| A-09 | ARREGLADO | README enuncia el principio rector con «de más» + canario carácter a carácter contra GOAL | `ElReadmeEnunciaElPrincipioRectorComoGoal` |
| A-11 | ARREGLADO | `oceano/descender` podado a su frase de identidad (los otros dos párrafos ya son estructura/guardarraíl) | `medir` entrada base baja; validar verde |
| A-12 | ARREGLADO | `PROGRESS.md` regenerado con pin de commit y cifras de `cosmos estado`; `ciudad` fuera + canario | `A12_UnNivelRetiradoNoSeNombraComoVivo` |
| A-13 | ARREGLADO | `cosmos estado` desglosa `rio` por `momento` con nombres | `cosmos estado` → «Ríos por momento» |
| A-14 | ARREGLADO | Primera entrada en `registro/informes/` (`bascula-rota.md`, diagnóstico reutilizable del juez) | validar verde (lluvia) |
| E-01 | ARREGLADO | El bloque proyectado no anuncia verbos que el repo ajeno no tiene (`con_rios=False`) y explica cómo bajar | `test_proyectar.LoProyectadoLoVeElAnfitrion` |
| E-02 | ARREGLADO | `proyectar` traduce el frontmatter a `name:`/`description:`; `comprobar` verifica el contrato del **anfitrión** | M70/M71 rojas |
| E-04 | ARREGLADO | `cosmos proyectar` como verbo de primera clase + sección «Montarlo sobre tu proyecto» en el README | `cosmos proyectar --help` |
| E-05 | ARREGLADO | Sección «Cómo se usa» en el README (`buscar` → `abrir` → ejecutar) | README |
| E-08 | ARREGLADO | `arrancar` escribe la galaxia mínima que falta (como el índice) y deja el árbol nuevo en verde | `E08_ArrancarDejaUnArbolNuevoEnVerde` |
| E-13 | ARREGLADO | Regla escrita en `COMPOSICION.md`: hijos hoja se describen, intermedios se nombran | `COMPOSICION.md` §«Qué se ve al abrir» |
| E-14 | ARREGLADO | `abrir` lista `usa:` al pie, solo nombres, sin cargar nada | `E14_AbrirNombraLosOficiosQueUsa` |
| E-16 / F-07 | ARREGLADO | Junto con A-01 (cardinal generado) | índice dice 22 |

### P2 — Legal y seguridad

| ID | Estado | Qué se hizo | Verificación |
|---|---|---|---|
| F-03 | ARREGLADO (atribución) + PENDIENTE-DARIO (retirar/licenciar) | `NOTICE` + fichas de `auditor-de-skills` y `consola-interactiva-tmux` con origen, autor y licencia leída | `NOTICE`; §4 de PENDIENTE-DARIO |
| F-04 | PENDIENTE-DARIO | La licencia propia del repo la decide Darío; `NOTICE` ya preparado | §3 |
| F-08 | ARREGLADO | `telegram-bridge.py` (×2): argv en lista sin `shell=True`, `--dangerously-skip-permissions` solo con `OPENCLAW_SIN_PERMISOS=1`, aviso en la ficha | `py_compile` OK; grep sin `shell=True` |
| F-06 | ARREGLADO | Junto con D-02: los tests del salto usan un `cosmos.toml` en un temporal; canario contra saltos de prueba en el repo | `NingunaPruebaDejaEstadoEnElRepositorio` |
| F-10 | ARREGLADO | Aviso `curl | bash` en `foundry` y `rill` (como `openclaw`); `brew` preferible en `rill` | fichas |
| F-09 | NO APLICA (+ PENDIENTE-DARIO) | `--no-verify` es limitación estructural compensada por CI (el propio informe lo dice); el hook no instalado en `~/cosmos` queda como decisión de Darío | §8 |
| F-11 | ARREGLADO | 64 rutas absolutas reescritas a `~`/`<usuario>` + patrón «ruta de máquina personal» en el escáner | `LasRutasDeUnaMaquinaPersonalSaltan`; `git grep ~` = 0 |
| F-12 | ARREGLADO (acta) + PENDIENTE-DARIO (respaldos) | Acta en `registro/decisiones/universo/` de la reescritura del 02-09; borrar los respaldos vivos = §1 | acta escrita |
| F-02 | PENDIENTE-DARIO | CIF auténtico en la historia de 5 ramas; purga con `filter-repo` + `push --force` preparada | §1 |
| F-05 | PENDIENTE-DARIO | Volcado con datos de terceros vivo en `origin/main`; misma purga | §2 |

### P3 — El código

| ID | Estado | Qué se hizo | Verificación |
|---|---|---|---|
| D-01 | ARREGLADO | `nichos_disponibles` cachea el conjunto por árbol; `nicho_de_nodo` deja de reconstruirlo por llamada | suite verde; el cúbico desaparece (conteo de llamadas) |
| D-02 | ARREGLADO | Los tests del salto/presupuesto usan `cosmos.toml` en `TemporaryDirectory`; canario anti-fuga | dos corridas concurrentes de `test_toda_puerta_tiene_salida` en verde, sin saltos huérfanos |
| D-04 | ARREGLADO | `read_text(encoding="utf-8-sig")` en el cargador | `D04_UnBomNoHaceDesaparecerUnNodo` |
| D-05 | ARREGLADO | Guarda «raíz no existe» para `estado` y `mapa`, no solo `medir`/`buscar` | `D05_EstadoYMapaNoDanVerdeSobreUnaRaizQueNoExiste` |
| D-06 | ARREGLADO | E17 calcula `_afirmaciones` una vez por nodo (caché) en vez de por pareja | suite verde |
| D-07 | ARREGLADO | `generar_mapa` indexa adjuntos en una pasada (`adjuntos_de`) | suite verde |
| D-09 | ARREGLADO | `formatear_medicion` + `medicion_json` + sus 3 tests fuera (código muerto) | grep sin llamantes; suite verde |
| D-10 | ARREGLADO | Los dos errores de carga usan la ruta relativa | `D11_...` comprueba `errores[0].ruta == "web.md"` |
| D-11 | ARREGLADO | Un symlink que apunta fuera de la raíz se denuncia, no entra como nodo | `D11_UnEnlaceFueraDelArbolNoEntraComoNodo` |
| E-03 | ARREGLADO | `compilar`/`arrancar` solo resumen por defecto; detalle tras `--detalle`; nunca `IGUAL` sin pedirlo | `E03_CompilarNoListaLoQueNoCambia`; clon en frío 554 bytes |
| E-06 | ARREGLADO | La orden del hook usa `$CLAUDE_PROJECT_DIR` y `python3` cuando COSMOS es el repo | `E06_LaOrdenDelHookEsPortableCuandoPuede` |
| E-09 | ARREGLADO | Junto con D-03 (guarda de árbol vacío antes del cálculo de presupuesto) | `test_arbol_vacio` |
| E-10 | ARREGLADO | `cosmos mapa` avisa del coste en la primera línea y en `--help` | `generar_mapa` primera línea |
| E-11 | ARREGLADO | `docs/CALIBRACION.md`: sección «Cerrado» con la medición de hoy; canario F01 sustituido por «aprox↔exacto coinciden» | `test_el_veredicto_exacto_y_el_aproximado_coinciden` |
| E-15 | ARREGLADO | La proyección reescribe `.claude/settings.json` solo si cambia el contenido efectivo, sin reordenar | `test_settings_no_se_reordena_si_no_cambia_nada` |
| E-12 | NO APLICA | `buscar` acierta ~2/5: es el techo declarado del método (BM25 léxico, «no es un agente»), no un bug. Subirlo tocando los resúmenes es exactamente lo que la regla de oro prohíbe; la mejora legítima de la búsqueda es trabajo aparte, fuera del ciclo del juez | el propio `acertar` lo publica y explica el método |

### P4 — La galaxia

| ID | Estado | Qué se hizo | Verificación |
|---|---|---|---|
| C-04 | ARREGLADO | +8 en ciberseguridad: `nmap`, `ffuf`, `hashcat`, `wireshark`, `codeql`, `httpx`, `subfinder`, `osquery` | `galaxia-G1.md`; validar verde |
| C-01 | ARREGLADO (+añadir) + PENDIENTE-DARIO (retirar) | +9 agentes reales (`langgraph`, `pydantic-ai`, `deepeval`, `promptfoo`, `inspect-ai`, `fastmcp`, `mcp-servers`, `browser-use`, `dspy`); la provincia `coste` la decide Darío | `galaxia-G2.md`; §5 |
| C-02 | ARREGLADO | +`astro`, `vite`, `tailwindcss`, `payload`, `medusajs` (web sin WordPress) | `galaxia-G2.md` |
| C-03 | ARREGLADO | +`ansible`, `opentofu`, `grafana`, `loki`, `vector`, `coolify` (IaC + visor de métricas) | `galaxia-G1.md` |
| C-05 | ARREGLADO | +`memray`, `scalene`, `async-profiler` (perfilado de memoria) | `galaxia-G1.md` |
| C-06 | ARREGLADO | Los mares nombran `hypothesis` / `tenacity` / `toxiproxy` / `time-machine` con `cosmos abrir` | validar verde (E17 pasa) |
| C-08 | ARREGLADO | +`sitespeed`, `katana` (la capa medible del oficio) | `galaxia-G3.md` |
| C-10 | ARREGLADO | El sesgo de una máquina reescrito en las fichas: el hardware es un dato en «Ojo», no el criterio; `llama-cpp` y `vllm` entran con su aviso | fichas de `mlx-lm`, `ollama`, `vllm`, etc. |
| C-11 | ARREGLADO | +`metabase` (plataforma de BI con servidor) | `galaxia-G2.md` |
| C-12 | ARREGLADO | `chonkie` → URL canónica `feyninc/chonkie` | ficha |
| C-14 | ARREGLADO | `auditor-de-skills` marcado `origen: propio` + atribución (F-03) | E21 verde |
| C-15 | ARREGLADO | +`blender`, `butler`, `love2d` (activos 3D y distribución) | `galaxia-G3.md` |
| C-16 | ARREGLADO | 5 cruces `usa:` añadidos (juegos→moviles, audiovisual→modelos-locales, analitica→web, embebidos→ciberseguridad, refactorizacion→agentes-ia) | E20 verde |
| C-13 | ARREGLADO | E21 exige el núcleo del contrato; `cosmos estado` cuenta rival/avisos/fecha que quedan como prosa | `cosmos estado` → «Contrato de pueblo» |
| C-07 | ARREGLADO (aviso) + PENDIENTE-DARIO (retirar) | `claude-seo-ai`: aviso reforzado con la evidencia exacta; retirada = decisión de Darío | ficha; §5 |
| C-09 | ARREGLADO (relevo) + PENDIENTE-DARIO (retirar) | `medusa` añadido como relevo de `mythril`; retirar `mythril` = decisión de Darío | ficha `medusa`; §5 |
| C-17 | NO APLICA | `revision-cruzada` y `quota-oficial` dependen de una capa gratuita sin tarjeta: no incumplen GOAL §5 y sus fichas ya lo avisan. Se anota para vigilancia periódica | fichas; §5 (a vigilar) |
| C · añadir 24 | ARREGLADO | 59 herramientas añadidas (supera las 24 P1/P2 del informe), todas verificadas vivas | `cosmos estado`: 306 pueblos |
| C · retirar 17 | PENDIENTE-DARIO | Retirar cambia el contenido del producto: se propone con motivo, se archiva (nunca `rm`) | §5 |

---

## Resumen

- **80 hallazgos:** 74 con componente ARREGLADO (68 puros + 6 con una mitad PENDIENTE-DARIO), 3
  PENDIENTE-DARIO puros (F-02, F-04, F-05), 3 NO APLICA (E-12, C-17, la parte estructural de F-09),
  0 NO VERIFICADO. [Corregido en el ciclo 2 (R-28): decía «71» y su propia tabla daba 74. Los tres
  NO APLICA cayeron en la revisión y se cerraron en `CICLO-2/FIX.md`.]
- **Lo que necesita el sí de Darío:** `PENDIENTE-DARIO.md` (purga de historia F-02/F-05, licencia
  F-04, retirar/licenciar código ajeno F-03, 17 herramientas a retirar, holdout v2 ciego, hook local).
- **Regla de oro cumplida:** la nota bajó (40 → 30 %, y de publicable a DESCONOCIDA). No se tocó
  corpus, resúmenes, holdout ni formato para subirla; el juez es incorruptible por las vías del
  informe B, y se le ha visto fallar puerta por puerta (M60–M73).
