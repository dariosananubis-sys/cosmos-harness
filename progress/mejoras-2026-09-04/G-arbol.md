# G — Árbol: tres oficios nuevos y los hallazgos de coherencia de `galaxia/`

**Ventana G (editor del catálogo).** Boundary: `galaxia/**` y `spec/UNIVERSO.md`, nada más. Sin commit.
Árbol de partida: `892f669` (2026-09-04 09:29), con la otra ventana escribiendo a la vez en `cosmos/`,
`puente/`, `tests/`, `.github/`, `spec/*.md` (salvo UNIVERSO), `galaxia/agua/oceano-*.md` y
`galaxia/agua/rio-*.md`. Lo de esas rutas que aparece en `git status` **no es mío**.

Cierre en verde: `generar`, `arrancar`, `validar`, `medir` y `estado` salen 0. Detalle en §9.

---

## 1. Tres oficios nuevos (`localizacion`, `entregabilidad`, `aprendizaje-automatico`)

### 1.1 Verificación en vivo, hoy 2026-09-04

Dos comprobaciones por herramienta, como pide `spec/PUEBLO.md` regla 2: la API pública de GitHub
(estrellas, licencia, `pushed_at`, `archived`) y `commits/HEAD.atom` (la fecha del último commit **de
HEAD**, que es la que no miente cuando el `pushed_at` viene de otra rama). Sin `gh`.

```bash
curl -s https://api.github.com/repos/<org>/<repo>
curl -s https://github.com/<org>/<repo>/commits/HEAD.atom | grep -m1 '<updated>'
```

| Oficio | Herramienta | ★ | Licencia (SPDX) | `pushed_at` | HEAD real (atom) | `archived` |
|---|---|---|---|---|---|---|
| `localizacion` | `WeblateOrg/weblate` | 6.051 | GPL-3.0 | 2026-09-04T07:01Z | 2026-09-04T06:57Z | no |
| `localizacion` | `i18next/i18next` | 8.625 | MIT | 2026-09-03T20:24Z | 2026-09-03T20:23Z | no |
| `localizacion` | `formatjs/formatjs` | 14.747 | *(sin SPDX en la raíz)* → **MIT por paquete** | 2026-09-04T05:58Z | 2026-09-04T05:58Z | no |
| `entregabilidad` | `axllent/mailpit` | 10.273 | MIT | 2026-09-03T05:08Z | 2026-09-03T05:08Z | no |
| `entregabilidad` | `domainaware/checkdmarc` | 321 | Apache-2.0 | 2026-08-31T04:49Z | 2026-08-31T04:44Z | no |
| `entregabilidad` | `domainaware/parsedmarc` | 1.291 | Apache-2.0 | 2026-09-03T19:52Z | 2026-09-03T19:51Z | no |
| `aprendizaje-automatico` | `scikit-learn/scikit-learn` | 67.158 | BSD-3-Clause | 2026-09-04T06:13Z | 2026-09-04T06:13Z | no |
| `aprendizaje-automatico` | `optuna/optuna` | 14.744 | MIT | 2026-09-04T06:25Z | 2026-09-04T06:25Z | no |
| `aprendizaje-automatico` | `bentoml/BentoML` | 8.820 | Apache-2.0 | 2026-08-28T09:19Z | 2026-08-28T09:19Z | no |

Los nueve pasan: vivos, no archivados, licencia libre, cero coste y cero tarjeta. **Ninguno hubo que
sustituir**; los tres candidatos de B §7.2 por oficio aguantaron la reverificación.

Dos matices que sí cambian la ficha respecto a lo que decía B §7.2:

- **`formatjs` no es «sin licencia»**. El monorepo no publica `LICENSE` en la raíz —por eso la API
  devuelve `license: null`—, pero cada paquete la declara: `@formatjs/intl` y `@formatjs/cli` son
  **MIT** en su `package.json` (comprobado en `raw.githubusercontent.com`). La ficha lo dice así, no
  copia el `null`.
- **`scikit-learn` no gana en exactitud** a `xgboost`/`lightgbm` sobre datos tabulares, y la ficha lo
  escribe al revés de como suena: gana en ser la interfaz que habla todo el ecosistema (incluido
  `optuna`) y en que `Pipeline` impide la fuga de información más común del oficio.

### 1.2 Estructura creada

Cada oficio: un `sistema-solar` con `padre: ""`, su `estrella` (`ilumina: <n>`), y un mapa por el que
bajar. Se respetan las dos reglas duras a la vez —ningún oficio en plano (`tests/test_oficios_estructurados.py`)
y ningún nivel con un solo hijo (`spec/TAXONOMIA.md`)—, así que donde no había dos hermanos para un
país, la herramienta cuelga directamente del oficio:

```
localizacion                      (sistema)
├── weblate                       (pueblo suelto: plataforma, no agrupa con nadie)
└── mensajes                      (país)
    ├── i18next
    └── formatjs

entregabilidad                    (sistema)
├── mailpit                       (pueblo suelto: lo que TÚ envías, no lo que el mundo dice de ti)
└── autenticacion                 (país)
    ├── checkdmarc
    └── parsedmarc

aprendizaje-automatico            (sistema)
├── bentoml                       (pueblo suelto: servir es el paso de después del país)
└── entrenamiento                 (país)
    ├── scikit-learn
    └── optuna
```

Ficheros nuevos (18):

```
galaxia/sistemas/localizacion.md                    galaxia/estrellas/localizacion.md
galaxia/sistemas/entregabilidad.md                  galaxia/estrellas/entregabilidad.md
galaxia/sistemas/aprendizaje-automatico.md          galaxia/estrellas/aprendizaje-automatico.md
galaxia/paises/localizacion--mensajes.md
galaxia/paises/entregabilidad--autenticacion.md
galaxia/paises/aprendizaje-automatico--entrenamiento.md
galaxia/pueblos/{weblate,i18next,formatjs}/SKILL.md
galaxia/pueblos/{mailpit,checkdmarc,parsedmarc}/SKILL.md
galaxia/pueblos/{scikit-learn,optuna,bentoml}/SKILL.md
```

`spec/UNIVERSO.md`: título `22 → 25 oficios`, cabecera `## Los 22 → ## Los 25`, tres filas nuevas
(23-25), la fila 7 (`agentes-ia`) reescrita para que no prometa solo «agentes que hacen trabajo
real», «los 22» → «los 25» en el bloque de mares y en el del límite, y un párrafo que registra la
decisión del 2026-09-03 y por qué los tres pasan la prueba «¿alguien contrataría esto?».

### 1.3 Vecinos (`usa:`)

`tests/test_universo_navegable.py` exige que ningún oficio quede sin que nadie lo cite (solo `juegos`
está declarado terminal). Aristas añadidas, todas verdaderas sobre cómo se cruza el trabajo real:

| Desde | Hacia | Por qué |
|---|---|---|
| `web`, `moviles`, `saas` | `localizacion` | un sitio, una app o un producto de suscripción en varios idiomas |
| `saas`, `automatizacion`, `infraestructura` | `entregabilidad` | correo transaccional, avisos de flujo, correo del servidor |
| `cientifico`, `analitica`, `agentes-ia` | `aprendizaje-automatico` | modelo que predice, previsión de demanda, el agente que llama a un modelo entrenado |

Y los tres oficios nuevos declaran sus propios `usa:` (`localizacion` → web/moviles/documentos;
`entregabilidad` → infraestructura/saas/automatizacion; `aprendizaje-automatico` →
cientifico/ingenieria-datos/agentes-ia/infraestructura).

### 1.4 E16 por nicho — medido, no estimado

```bash
python3 -m cosmos medir --nicho <oficio> --json
```

| Nicho | Pueblos | Entrada | Entrada + agua |
|---|---|---|---|
| `ciberseguridad` (**el peor**) | 35 | 2.564 | 3.797 |
| `agentes-ia` | 25 | 2.242 | 3.475 |
| `cumplimiento` | 12 | 1.742 | 2.975 |
| **`entregabilidad`** | 3 | **1.452** | 2.685 |
| **`aprendizaje-automatico`** | 3 | **1.444** | 2.677 |
| **`localizacion`** | 3 | **1.443** | 2.676 |

Los tres quedan a más de 1.100 tokens del peor nicho: **ninguno mueve E16 por su catálogo**, como
predecía B §7.2. Lo que sí lo mueve es otra cosa, y B §7.2 no la vio — ver §10.1.

### 1.5 `mlflow`: NO se ha movido, y por qué

B §7.2 avisaba de que `mlflow` (hoy `padre: agentes-ia/evaluacion`) es el candidato natural del
oficio nuevo y que E18 + `GOAL.md` §1 prohíben duplicarlo. Se ha decidido **dejarlo donde está** y
citarlo como vecino, que es la otra opción que el encargo dejaba abierta. Tres razones medibles:

1. **Su ficha argumenta un hueco de `agentes-ia`, no de ML clásico**: gana a `langwatch/langwatch` y
   `openlit/openlit` como observatorio de agentes, y su resumen es «registra ejecuciones, trazas y
   evaluaciones de **un agente**». Moverlo obliga a reescribir la ficha entera —rivales incluidos—,
   que es trabajo fuera de este encargo y sin verificación en vivo hecha.
2. **Deja un hueco real donde estaba.** `agentes-ia/evaluacion` se queda ya sin `revision-cruzada`
   (se va a `instrumentacion`, §2). Si además pierde `mlflow`, el país pierde su registro de
   ejecuciones y nadie lo cubre.
3. **El oficio nuevo no lo necesita para tener mapa**: `entrenamiento` tiene dos hijos sin él, y
   `bentoml` cuelga del sistema. Meterlo obligaría a inventar un país `puesta-en-produccion` de dos
   hijos que hoy no agrupa nada más.

Queda citado desde los dos sitios donde hace falta y sin copiar un byte:

- `galaxia/estrellas/aprendizaje-automatico.md`: *«El registro de ejecuciones y artefactos no se
  duplica aquí: vive en `agentes-ia/evaluacion`, y desde este oficio se usa, no se copia.»*
- `galaxia/pueblos/optuna/SKILL.md` y `galaxia/pueblos/bentoml/SKILL.md` declaran su frontera con él.
- `galaxia/sistemas/aprendizaje-automatico.md` tiene `usa: agentes-ia`.

**Cero pueblos duplicados**: `cosmos validar` (E18) en verde y `cosmos estado` sin huérfanos.

---

## 2. B-25 — `agentes-ia/instrumentacion`

Fichero nuevo `galaxia/paises/agentes-ia--instrumentacion.md`:

```yaml
resumen: Con que se opera y se mide al propio agente de codigo, no lo que le da capacidades nuevas.
```

Los nueve pueblos que B-25 identificó pasan ahí. De dónde venía cada uno:

| Pueblo | `padre` antes | `padre` ahora |
|---|---|---|
| `alcance-y-excepcion` | `agentes-ia` (suelto) | `agentes-ia/instrumentacion` |
| `playbook-obligatorio` | `agentes-ia` (suelto) | `agentes-ia/instrumentacion` |
| `captura-recortada` | `agentes-ia/coste` | `agentes-ia/instrumentacion` |
| `codigo-al-modelo` | `agentes-ia/coste` | `agentes-ia/instrumentacion` |
| `medir-contexto` | `agentes-ia/coste` | `agentes-ia/instrumentacion` |
| `delegar-generacion` | `agentes-ia/construccion` | `agentes-ia/instrumentacion` |
| `plan-auditado` | `agentes-ia/construccion` | `agentes-ia/instrumentacion` |
| `diario-sin-duplicados` | `agentes-ia/memoria` | `agentes-ia/instrumentacion` |
| `revision-cruzada` | `agentes-ia/evaluacion` | `agentes-ia/instrumentacion` |

**Efecto colateral que había que resolver: `agentes-ia/coste` se quedó sin hijos.** Sus tres pueblos
eran exactamente los tres que se mueven (medido: `grep -rl "padre: agentes-ia/coste"` → 0 después).
Un país vacío no agrupa nada y su `resumen` se seguiría pagando en el catálogo de `agentes-ia`, así
que se retira **a la papelera, no se borra** (convención del repo, `spec/TAXONOMIA.md` §`cosecha/`):

```
mv galaxia/paises/agentes-ia--coste.md ~/.Trash/cosmos-retirado-2026-09-04/
```

Los otros tres países quedan sanos: `construccion` 4 hijos, `evaluacion` 4, `memoria` 2,
`herramientas` 6, `instrumentacion` 9. Cero pueblos sueltos colgando del oficio (el tope tolerado son
2). `cosmos estado` no publica ningún «nivel con un solo hijo».

`usa:` afectados: **ninguno**. Se comprobó que en toda la galaxia `usa:` solo se declara a nivel de
sistema y solo con nombres de oficio, así que mover pueblos no rompe ninguna arista (E20 en verde).
Las dos menciones a `mlflow` en prosa (`hydra`, `lm-evaluation-harness`) siguen siendo válidas porque
el pueblo no ha cambiado de nombre ni de sitio.

Resumen del sistema, que ya no promete solo agentes:

```diff
-resumen: Agentes y chatbots con herramientas, memoria y evaluacion; MCP.
+resumen: Agentes con herramientas, memoria, evaluacion e instrumental para operarlos.
```

(y la fila 7 de `spec/UNIVERSO.md` dice lo mismo con más sitio).

---

## 3. B-24 + B-19 — el deíctico sustituido por el hecho

Once ficheros. El criterio: el que clona COSMOS no sabe qué casa ni qué Mac, así que donde había un
deíctico va el hecho comprobable, y donde había un guardarraíl que este repo no tiene, no va nada.

| Fichero | Antes | Ahora |
|---|---|---|
| `sanitizers/SKILL.md` | «el falso verde de **esta casa**, medido en **este Mac** (arm64, Apple clang 21…)» | «el falso verde que hay que conocer, **medido en macOS arm64 con Apple clang 21**» |
| `samply/SKILL.md` | «a `perf` en **esta casa**… corre en **este Mac** y con **este procesador**» | «a `perf` por lo pragmático: corre en **macOS sobre Apple Silicon**» |
| `mlx-lm/SKILL.md` | «exige CUDA y no corre en **este Mac**» | «exige CUDA y no corre en **Apple Silicon**» |
| `context7/SKILL.md` | «Ya está disponible en **esta casa**.» | «Cuando **el harness anfitrión** ya lo trae conectado, no hay nada que instalar.» |
| `lm-evaluation-harness/SKILL.md` | «lo que importa para **esta casa**» | «lo que importa **cuando no se paga por uso**» |
| `openclaw/SKILL.md` | «el canal autónomo que ya se usa en **esta casa**» | «el canal autónomo —mensajería que despierta a un agente— que después replican **otros arneses**» |
| `geo-optimizer/SKILL.md` | «es una regla dura de **esta casa**» | «es **la línea que no se cruza sin permiso explícito**» |
| `elementor-mcp/SKILL.md` | «Del lado de **esta casa**, dos guiones propios» | «**En el directorio de este pueblo**, dos guiones propios» |
| `tree-sitter/SKILL.md` | «herramientas de **este arnés**» | «herramientas **del catálogo**» |
| `captura-recortada/SKILL.md` | «…y en **este arnés la pantalla entera está bloqueada por enganche**» | frase **borrada** (B-19: COSMOS no tiene ese guardarraíl; los suyos son G01–G05 y ninguno mira `screencapture`) |
| `acceso-remoto/scripts/acceso-remoto-watchdog.sh` | «el acceso remoto a **este Mac**» | «el acceso remoto **al equipo**» |

Comprobación exigida:

```
$ grep -rniE "esta casa|este arn[eé]s|este mac\b|este procesador" galaxia/ | wc -l
0
```

Cinco párrafos hubo que reflujarlos después de la sustitución (`samply`, `context7`, `openclaw`,
`geo-optimizer`, `lm-evaluation-harness`) porque el reemplazo partía un `código` entre líneas.

---

## 4. B-18 — `butler`

```diff
-resumen: Sube una build a itch.io con parches binarios; unico pueblo de la provincia de distribucion.
+resumen: Sube una build a itch.io con parches binarios: solo sube lo que cambio, no el juego entero.
```

Y **la misma referencia muerta estaba también en el cuerpo**, que B-18 no citaba: la «Nota de padre»
decía *«vive en `juegos/distribucion`, la provincia abierta para él»* mientras su `padre` es
`juegos/motores`. Reescrita para decir dónde cuelga de verdad y por qué se retiró aquel país (un solo
hijo = nivel de relleno). Un `resumen` corregido con el cuerpo mintiendo no cierra el hallazgo.

---

## 5. B-31 — `eventsourcing` y `python-statemachine` alcanzables desde el agua

`galaxia/agua/mar-resistencia.md`, última línea. Se **reescribe** en vez de añadir una línea nueva,
porque el presupuesto no daba para una línea nueva (§10.1) y la lista de punteros ya existía:

```diff
-Reintento con espera: `tenacity`; fallos de red a propósito: `toxiproxy`; congelar el reloj: `time-machine`.
+Reintento `tenacity`; fallos de red `toxiproxy`; reloj `time-machine`; estado `eventsourcing`, `python-statemachine`.
```

Coste medido: **+2,6 tokens** en el peor caso con agua (la versión con la redacción larga costaba
+11,8 y ponía E16 en rojo). El precio es que se pierden «con espera» y «a propósito»; el mar explica
los dos conceptos tres párrafos más arriba, así que la pérdida es de adorno, no de información.

---

## 6. B-32 — `reprozip` se queda, con el rival escrito

Reverificado hoy antes de decidir: **362★ · BSD-3-Clause · `pushed_at` 2026-02-04 · HEAD (atom)
2026-01-18 · no archivado**. Casi ocho meses sin commits en HEAD: lento, pero por debajo del año que
lo mataría. La cabecera de la ficha ahora publica las dos fechas, no una.

La condición de `PENDIENTE-DARIO.md` («se queda solo si su ficha justifica el solapamiento») se
cumple con un párrafo que nombra a los dos vecinos que ya están en el árbol:

> Gana a `pixi` y a `dvc`, sus dos vecinos de este país, en la única pregunta que ninguno de los dos
> contesta: **qué usó de verdad la ejecución**. […] Los dos parten de una declaración humana, y lo
> que no está declarado no viaja: la biblioteca del sistema que se instaló a mano, el fichero de
> `/etc` que el guion lee, el binario auxiliar que se llama por `subprocess`. `reprozip` no pregunta,
> observa.

Y se le pone papel acotado y condición de permanencia explícita: sellado puntual, no flujo diario;
«si ese sello no hace falta, este pueblo sobra».

De propina, salía también en «sin apartado de avisos» de `cosmos estado` —su sección de límites
empezaba por «Y lo que no hace bien», en minúscula, que el detector no reconoce—. Reencabezada como
«Ojo, y es mucho…». Medido después: `reprozip` sale de las tres listas del contrato de pueblo.

**No se ha archivado**, así que no hay nada en `~/.Trash` por este hallazgo.

---

## 7. B-30 — `TOPE_SESIONES` deja de ser la cifra de un Mac de 8 GB

`galaxia/pueblos/agent-browser/scripts/navegador_seguro.py`:

```diff
 import json
+import os
 import subprocess
 import time

-TOPE_SESIONES = 3          # ajusta al límite de RAM de tu máquina, no es un valor mágico
+# El tope depende de la RAM de la máquina, no de una regla universal: se ajusta sin tocar el guion.
+TOPE_SESIONES = int(os.environ.get("AGENT_BROWSER_TOPE_SESIONES", "3"))
```

`python3 -c "import ast; ast.parse(...)"` → sintaxis OK.

---

## 8. §7.1 — `scancode-toolkit` NO se ha creado: ya está en el árbol

**B §7.1 se equivoca.** Dice que `aboutcode-org/scancode-toolkit` está «sin aplicar» en
`cumplimiento/licencias`. Está aplicado desde antes, con el nodo llamado `scancode`:

```
$ head -8 galaxia/pueblos/scancode/SKILL.md
nombre: scancode
padre: cumplimiento/licencias
https://github.com/aboutcode-org/scancode-toolkit · Apache-2.0 AND CC-BY-4.0 · 2.617★ …
```

B lo buscó por el nombre del repositorio y el nodo se llama por el binario (`scancode`, que es como
se invoca). Crear `galaxia/pueblos/scancode-toolkit/SKILL.md` habría metido **la misma herramienta
dos veces**, que es justo lo que `GOAL.md` §1 prohíbe («una herramienta vive en un solo sitio») y lo
que E18 existe para evitar.

Lo que sí valía de §7.1 se ha hecho sobre la ficha que ya existe:

- **Verificación refrescada a hoy** con las dos fuentes: 2.617★ · Apache-2.0 AND CC-BY-4.0 (leído en
  su `NOTICE`) · `pushed_at` 2026-09-04 · **HEAD (`develop`) 2026-08-28** · no archivado. El desfase
  entre las dos fechas se declara en la propia ficha: el push más reciente es de otra rama.
- **Se nombra a `ort`**, que era el rival que §7.1 pedía y que la ficha no tenía: `ort` resuelve el
  grafo de dependencias del gestor de paquetes y aplica política sobre lo declarado; `scancode` lee
  el texto de cada fichero, incluido el código copiado que no aparece en ningún manifiesto — y `ort`
  lo invoca por dentro como escáner. Se encadenan.

---

## 9. Cierre — salidas reales

```
$ python3 -m cosmos generar   → verde (2 saltos activos: P01, P02) · EXIT=0
$ python3 -m cosmos arrancar  → verde · vista compilada, 306 pueblos · EXIT=0
$ python3 -m cosmos validar   → verde (2 saltos activos: P01, caduca en 7 d; P02, caduca en 7 d)  0 errores · EXIT=0
$ python3 -m cosmos medir     → EXIT=0
$ python3 -m cosmos estado    → EXIT=0
```

`cosmos medir` completo tras todos los cambios:

```
  Entrada base .... 1.314 tokens
  Peor nicho ...... 2.564 tokens   (ciberseguridad, 35 pueblos)
  Agua condicional  1.231 tokens
  Agua condicional  1.233 tokens
  Peor con agua ... 3.797 tokens
  Presupuesto ..... 4.000     OK, quedan 5 tokens con el margen calibrado (+5,2 %)
```

`cosmos estado`, lo que importa:

```
  sistema-solar      25   (eran 22)
  pais               79   (eran 76: +3 nuevos, +instrumentacion, −coste)
  pueblo            306   (eran 297: +9)
  estrella           25   (eran 22)
  Niveles con un solo hijo: no aparece la sección → 0
  huerfanos: []   nichos_sin_estrella: []   niveles_de_relleno: []
  Contrato de pueblo: los 9 pueblos nuevos cumplen las tres reglas contadas
                      (rival nombrado, apartado de avisos, fecha de comprobación)
```

Tests del árbol que sí son míos y pasan: `tests/test_universo_navegable.py`,
`tests/test_oficios_estructurados.py`, `tests/test_spec_al_dia.py`, `tests/test_niveles_vivos.py`.

---

## 10. Lo que dejo sin hacer, y por qué

### 10.1 · E16 queda con 5 tokens de margen — decisión de Darío, no mía

**Este es el hallazgo importante de la tanda, y B §7.2 lo estimó mal.** Decía: *«≈250 tokens en el
Universo, **0 en el peor caso** de E16»*. Es falso, y la razón es estructural: el **índice de galaxia
entra en la entrada de todos los nichos** (`cosmos/medir.py`, `_bloques_contexto_inicial`), y cada
oficio nuevo añade una línea a ese índice. Medido:

| | Peor con agua | Margen que queda |
|---|---|---|
| Antes de esta tanda | 3.743 | 62 tokens |
| Con los 3 oficios nuevos | 3.795 | 7 tokens |
| Con B-31 (mar-resistencia) | 3.797 | **5 tokens** |

Los tres oficios se han comido 52 de los 62 tokens libres, y no por sus catálogos (§1.4) sino por sus
tres líneas de índice. Para que cupieran hubo que escribir los tres `resumen` de sistema en su forma
más corta defendible («Traducir un producto y mantenerlo traducido.», «Que el correo no acabe en
spam.», «Entrenar un modelo, ajustarlo y servirlo.») y comprimir la línea de `mar-resistencia`.

**Consecuencia práctica: el catálogo está lleno.** Con 5 tokens, la próxima herramienta que entre en
`ciberseguridad` (≈27,6 tokens por línea) o el próximo oficio pone E16 en rojo. Las salidas, y ninguna
es mía:

1. Subir `presupuesto.entrada` en `cosmos.toml` — es una decisión consciente y se escribe ahí, que es
   lo que la propia spec pide. **Fuera de mi boundary.**
2. Podar `ciberseguridad`, que con 35 pueblos fija el peor caso él solo (el segundo, `agentes-ia`,
   está 322 tokens por debajo).
3. Adelgazar los mares: 1.231 tokens de agua condicional se suman a **todos** los nichos.

### 10.2 · Cuatro cifras a mano en `spec/*.md` que ahora mienten — son de la otra ventana

`tests/test_cifras_de_las_specs.py` falla en cuatro entradas, todas en ficheros de tu boundary. Son
sustituciones de un número, sin más:

| Fichero | Frase | Dice | Tiene que decir |
|---|---|---|---|
| `spec/REGISTRO.md` | «uno de los N sistemas solares» | 22 | **25** |
| `spec/COMPOSICION.md` | «Los N sistemas solares lo hacen» | 22 | **25** |
| `spec/NUCLEO.md` | «N pares de nodos co-cargables» | 528 | **630** |
| `spec/VALIDADOR.md` | «los N nodos de la galaxia real» | 468 | **488** |

Y una quinta, del mismo tipo y también fuera de mi boundary: `tests/test_progress_generado.py` falla
porque el bloque ```` ```text ```` de **`PROGRESS.md`** jura ser la salida de `cosmos estado` y ya no
lo es (nodos y oficios cambiados). Se arregla regenerándolo:

```bash
python3 -m cosmos estado    # y pegar la salida en el bloque de PROGRESS.md
```

Trazabilidad de los dos números raros:

- **630 pares** = 36 co-cargables × 35 / 2. Eran 33 (5 océanos + 6 mares + 22 estrellas); las **3
  estrellas nuevas** son 100 % mías.
- **488 nodos** = 468 + 20. De esos 20, **18 son míos** (3 sistemas + 3 estrellas + 3 países nuevos +
  `instrumentacion` − `coste` + 9 pueblos) y **2 son tuyos** (los ríos `configurar` e `instalar`, que
  aparecieron durante esta tanda).

No los toco porque el encargo lo prohíbe expresamente. `cosmos validar` **no** los mira, así que el
cierre sigue en verde; el rojo está solo en esa prueba.

### 10.3 · Lo demás

- **`mlflow` no se ha movido.** Razonado en §1.5, con las tres citas que lo dejan alcanzable desde el
  oficio nuevo. Si prefieres moverlo, hay que reescribirle la ficha entera (rivales incluidos: hoy
  compara contra observatorios de agentes, no contra `wandb`/`aim`) y buscarle sustituto a
  `agentes-ia/evaluacion`. Es una tanda propia.
- **`galaxia/pueblos/dvc/SKILL.md` publica una URL que no es la del proyecto**: dice
  `https://github.com/treeverse/dvc` y `dvc` es `iterative/dvc` (`treeverse` es lakeFS). Está fuera de
  los hallazgos que me tocaban y no lo he tocado para no meter ruido en esta tanda, pero es un fallo
  de la regla 1 de `spec/PUEBLO.md` (la URL es literal y verificada) que E21 no caza porque la forma
  de la URL es válida. **Recomiendo arreglarlo en la siguiente.**
- **La suite completa**: `python3 -m unittest discover -s tests -t .` → `Ran 398 in 84 s — FAILED
  (failures=5, skipped=2)`. Las cinco están inventariadas arriba (4 cifras en `spec/*.md` + el bloque
  de `PROGRESS.md`) y **las cinco viven en ficheros de tu boundary**; ninguna es un fallo de
  comportamiento, todas son un número o un bloque copiado que hay que regenerar. Los cuatro módulos
  que sí dependen de mi trabajo se corrieron aislados y están en verde (§9).
