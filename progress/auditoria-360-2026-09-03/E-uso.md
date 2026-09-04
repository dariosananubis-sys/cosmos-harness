# Auditoría 360 COSMOS — Revisor E: la experiencia real de uso

**Ángulo exclusivo:** ¿funciona cuando alguien lo clona de verdad? No miro specs, ni métrica, ni
código por dentro. Me pongo en la piel de dos personas: un agente de código que llega sin saber
nada, y Darío queriendo montarlo sobre un proyecto suyo.

## Pin de estado

```
git -C ~/cosmos rev-parse HEAD        -> b0c1ebdeb2d9bac7e068d10714213ff2f9eda926
git -C ~/cosmos status --porcelain|wc -> 0        (antes y después de esta auditoría)
```

Rama `main`, remoto `https://github.com/<propietario>/cosmos-harness.git`.
15 MB clonados, 767 ficheros versionados.

## Método

- **`~/cosmos` y `~/vh-ref` en solo lectura.** Todo el trabajo vive en
  `/private/tmp/claude-503/…/scratchpad/E-uso/`. Ni un commit, ni un push, ni un byte editado en
  ninguno de los dos.
- **Intérpretes exactos**, publicados en cada comando:
  - `/usr/local/bin/python3` → `Python 3.14.3 (v3.14.3:323c59a5e34, Feb 3 2026)`
  - venv de calibración: `…/scratchpad/E-uso/venv-calib/bin/python` con `tiktoken 0.14.0`
    (software libre, `pip install` gratuito — cero gasto).
- Cada comando se pega con su salida real y su código de salida. **Los códigos de salida se toman
  sin tubería**: `cmd > fichero; echo $?`. Dos veces me dio `EXIT=0` falso por haber colado un
  `| head` en medio (`validar` sobre el repo ajeno, `proyectar --help`); ambos re-medidos sin
  tubería dan `EXIT=1`. Los números publicados abajo son los limpios.
- Conteo de tokens: `len(texto)/4`, la misma familia de heurística que usa `cosmos medir`. Donde
  hay número exacto, es `tiktoken/cl100k_base` y se dice.

---

# 1. La bitácora del clon en frío

Ésta es la evidencia principal. Sigo **únicamente el README**, sin usar nada de lo que sé del repo.

### Paso 0 — clonar

```bash
git clone ~/cosmos cold-clone
```
```
Cloning into 'cold-clone'...
done.
EXIT=0
SEGUNDOS_CLON=1
15M cold-clone   ·   9.2M cold-clone/.git   ·   767 ficheros
```
✅ **Pasa.** Un segundo, sin dependencias, sin `pip install`. El README no declara versión mínima de
Python y no hizo falta: `python3` de sistema (3.14.3) sirve tal cual.

### Paso 1 — `python3 -m cosmos arrancar` (lo primero que manda el README)

```bash
cd cold-clone && python3 -m cosmos arrancar
```
```
COSMOS  compilar  verde

Creadas 247; actualizadas 0; iguales 0; …
CREAR /private/tmp/.../cold-clone/.cosmos/vista-galaxia/a11y-auditoria-wcag
CREAR /private/tmp/.../cold-clone/.cosmos/vista-galaxia/acceso-remoto
   … (247 líneas CREAR, una por pueblo, con la ruta absoluta completa) …
CREAR /private/tmp/.../cold-clone/.cosmos/vista-galaxia/zephyr
COSMOS  verde  0 errores

COSMOS  arrancar  verde

Vista compilada en /private/tmp/.../cold-clone/.cosmos/vista-galaxia
EXIT=0
SEGUNDOS=4.28
```
⚠️ **Funciona, pero cuesta 262 líneas / 39.926 bytes ≈ 9.980 tokens.** Ver **E-03**.

### Paso 1-bis — la segunda vez, sin haber cambiado nada

```bash
python3 -m cosmos arrancar > arr-2a.out 2>&1; echo "EXIT=$?"
```
```
EXIT=0
     255   39590 arr-2a.out

Creadas 0; actualizadas 0; iguales 247; …
--- prefijos de línea ---
 247 IGUAL
   3 COSMOS
   1 Vista
```
⚠️ **247 líneas `IGUAL <ruta absoluta>` para decir «no ha cambiado nada».** 39,6 KB ≈ 9.900 tokens
de ruido puro. Ver **E-03**.

### Paso 2 — `--help`: descubrir qué se puede hacer

```bash
python3 -m cosmos --help
```
```
usage: cosmos [-h]
              {abrir,buscar,acertar,estado,validar,medir,generar,compilar,arrancar,mapa,enganchar,desenganchar,saltar} ...
EXIT=0
```
✅ **Pasa, y bien.** 13 verbos, cada uno con una línea que dice qué hace. `abrir --help` y
`buscar --help` explican sus flags. Es la mejor pieza de documentación del repo.
❌ Pero **el README documenta 8 verbos y ninguno de los 5 de uso.** Ver **E-05**.

### Paso 3 — `cosmos validar`

```bash
python3 -m cosmos validar > validar.out 2>&1; echo "EXIT=$?"
```
```
EXIT=0
       1      25 validar.out
COSMOS  verde  0 errores
```
✅ **Pasa perfecto.** Una línea, 25 bytes. Es exactamente lo que un verbo debe costar.

### Paso 4 — `cosmos medir`

```bash
python3 -m cosmos medir > medir.out 2>&1; echo "EXIT=$?"
```
```
EXIT=0
      16     741 medir.out
COSMOS  medir

  Entrada base .... 1.343 tokens   (índice + océanos + estructura, sin pueblos; estimado, ±5%, heurística v3)
  Peor nicho ...... 2.383 tokens   (ciberseguridad, 27 pueblos)
  Agua condicional  1.163 tokens   (6 aguas por paths:, fuera de la entrada)
  Peor con agua ... 3.546 tokens   (el peor caso + agua condicional)
  Universo ........ 140.862 tokens   (estimado, ±5%, heurística v3)
  Descarga ........ 98,3 %
  Presupuesto ..... 4.000     OK, quedan 454 tokens en el peor caso con agua (ciberseguridad)

  Fuera de COSMOS . no_medido      (system prompt, tools, MCP)
```
✅ **Pasa.** 741 bytes, declara el método, declara lo que **no** mide (`no_medido`). Honesto.

### Paso 5 — `cosmos buscar`

```bash
python3 -m cosmos buscar montar un bot de trading
```
```
COSMOS  buscar

  1.  trading/bots/codigo-de-bot
      Escribir el bot: aqui un fallo no lanza una excepcion, deja una posicion abierta y una perdida.
  2.  blockchain/cadena/ponder …
  3.  saas/identidad/panel-auth-cookie …
  4.  trading/bots/codigo-de-bot/toxiproxy …
  5.  trading/mercado …

  'cosmos abrir <ruta>' carga el nodo; esto solo encuentra.
EXIT=0
```
✅ **Pasa, y es la joya del sistema.** 190 tokens, acierto en el primero, y la última línea te dice
qué hacer después. Nada que adivinar.

### Paso 6 — `cosmos abrir`

```bash
python3 -m cosmos abrir trading/bots/codigo-de-bot/toxiproxy
```
```
COSMOS  abrir  trading/bots/codigo-de-bot/toxiproxy  (pueblo)

https://github.com/Shopify/toxiproxy · MIT · 12.294★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
brew install toxiproxy
brew services start toxiproxy      # el servidor; el bot apunta al proxy, no al mercado
```
…
EXIT=0   ·   31 líneas / 1.750 bytes
```
✅ **Pasa, y cumple la promesa del GOAL**: herramienta que se ejecuta, con licencia, estrellas,
fecha comprobada y la frontera declarada («prueba el canal de red, no la lógica de mercado»). Esto
es mejor que lo que devuelve una búsqueda en GitHub.

### Paso 7 — `cosmos enganchar --sesion`

```bash
python3 -m cosmos enganchar --sesion
```
```
COSMOS  enganchar  verde
Hook de pre-commit creado en …/cold-clone/.git/hooks/pre-commit
Guardarraíles de sesión creado en …/cold-clone/.claude/settings.json
Se quita todo con 'cosmos desenganchar'.
EXIT=0
```
✅ Escribe lo que dice y dice dónde. ⚠️ Pero lo que escribe lleva rutas absolutas de esta máquina y
no está en `.gitignore`. Ver **E-06**.

### Paso 8 — los tests, que el README no menciona

```bash
python3 -m pytest tests -q   ->  EXIT=1 · /usr/local/bin/python3: No module named pytest
python3 -m unittest discover -s tests -q  ->  EXIT=0 · Ran 259 tests in 88.909s · OK (skipped=2)
```
⚠️ El comando correcto (`unittest`) no está escrito en ningún sitio; el intuitivo (`pytest`) falla.
Y los 2 saltos silencian la única prueba de la métrica principal. Ver **E-07**.

### Veredicto del clon en frío

**El clon en frío FUNCIONA. No falla en ningún paso.** Los 8 pasos dan verde y el sistema es usable
en menos de 5 segundos desde `git clone` sin instalar nada. Mi premisa de partida —«sólo funciona en
el Mac de Darío»— **queda desmentida para el repo COSMOS en sí**.

Donde sí se rompe es fuera del propio repo: en el momento en que intentas cumplir la frase del
`GOAL.md` («clonar **sobre cualquier proyecto**»). Ahí sí, y de forma crítica (E-01, E-02).

---

# 2. Montarlo sobre otro proyecto

Proyecto ajeno: **`~/vh-ref`** (412 ficheros, Python, con `CLAUDE.md`, `AGENTS.md`,
`.claude/skills/` y `.agents/skills/` propios). Copiado a mi scratchpad; el original no se tocó
(`ls -ld ~/vh-ref` idéntico antes y después).

### 2.1 El camino ingenuo: clonar COSMOS dentro del proyecto

```bash
cd proyecto-ajeno && git clone ~/cosmos .cosmos-harness
cd .cosmos-harness && python3 -m cosmos arrancar
  -> compila la galaxia DE COSMOS, no la del proyecto. El proyecto ajeno sigue sin harness.

python3 -m cosmos arrancar "$PWD/../"   > arr-ajeno.out 2>&1; echo "EXIT=$?"
```
```
EXIT=1
COSMOS  rojo  616 errores
E00  .agents/skills/accessibility/SKILL.md
     falta el campo obligatorio 'cosmos'
     Añade 'cosmos' al frontmatter.
…  (2.467 líneas)
```
❌ 616 errores, 2.467 líneas, y ninguna pista de por dónde salir. **Este camino no existe.**

### 2.2 Crear un árbol nuevo a mano

`spec/NUCLEO.md` §6 promete: *«`arrancar` es el único que deja un árbol nuevo en verde de una
vez»*. Lo probé con un directorio vacío + un `cosmos.toml` copiado del ejemplo:

```
EXIT=1
COSMOS  rojo  2 errores

E05  árbol
     se esperaba exactamente una galaxia; hay 0 (ninguna)
E16  presupuesto
     peor nicho sin nichos: entrada 0 + agua condicional 0 = 0 tokens > 4000; excede en -4000 tokens; más caros:
```
❌ La promesa es falsa (**E-08**) y el mensaje E16 es absurdo: *«0 tokens > 4000; excede en −4000»*
(**E-09**).

Llegué a verde en **5 intentos**, y sólo porque leí `spec/FRONTMATTER.md` (una spec normativa, no
documentación de usuario) y porque abrí un nodo real del árbol para copiar convenciones:

| # | Qué hice | Resultado |
|---|---|---|
| 1 | dir vacío + `cosmos.toml` | rojo: E05 + E16 absurdo |
| 2 | escribí `galaxia.md` con el frontmatter de la spec | **verde**, índice creado |
| 3 | añadí un sistema-solar con `padre: <nombre-galaxia>` | rojo: `padre inexistente` |
| 4 | `padre: ""` — deducido abriendo `galaxia/sistemas/trading.md` | rojo: la ruta del hijo no lleva el nombre de la galaxia |
| 5 | `cosmos generar` (que `arrancar` NO hace si el índice ya existe) | **verde, 0 errores** |

**Tres cosas que tuve que adivinar y que no están escritas en ningún sitio de usuario:**
1. Un árbol nuevo necesita un `galaxia.md` escrito a mano, con su frontmatter exacto.
2. Un sistema-solar lleva `padre: ""` (cadena vacía). `spec/FRONTMATTER.md` dice *«`padre`:
   obligatorio salvo galaxia — la ruta completa de un nodo existente»*, lo que induce a escribir el
   nombre de la galaxia. Es exactamente lo que hice, y falla.
3. El nombre de la galaxia **no** aparece en las rutas de sus descendientes.

### 2.3 El mecanismo real, escondido: `puente.proyectar`

Listando `galaxia/agua/` encontré `rio-proyectar.md`, que declara:
`invoca: python3 -m puente.proyectar <repo>` — *«Lleva los oficios elegidos a un repositorio ajeno
sin pisar lo suyo»*. Existe de verdad:

```bash
python3 -m puente.proyectar --help
```
```
usage: python3 -m puente.proyectar [-h] [--config CONFIG] {sincronizar,comprobar,iniciar} ...
Proyecta COSMOS sobre un repo Git ajeno sin pisar nada que no sea suyo.
EXIT=0
```

**Es la pieza que cumple el `GOAL.md`, y aparece 0 veces en `README.md` y 0 veces en `GOAL.md`:**
```bash
grep -c "proyectar" README.md GOAL.md   ->   README.md:0   GOAL.md:0
python3 -m cosmos proyectar --help      ->   invalid choice: 'proyectar'
```
Sólo se descubre hurgando dentro del contenido. **E-04.**

Usándolo:

```bash
python3 -m puente.proyectar iniciar /…/destino/vh-ref
->  proyección sincronizada · 0 skills · nichos=ninguno        EXIT=0
```
⚠️ Verde, y no proyectó nada: `planeta.toml` nace con `nichos = []`. El flujo real es
`iniciar` → editar `planeta.toml` a mano → `sincronizar`. No está documentado. `iniciar --nicho
trading` a la segunda falla con `ERROR: planeta.toml ya existe; usa sincronizar`.

```bash
# edito planeta.toml -> nichos = ["trading"]
python3 -m puente.proyectar sincronizar /…/destino/vh-ref
->  proyección sincronizada · 22 skills · nichos=trading        EXIT=0
```

Lo que escribe en el repo ajeno:
```
 M .claude/settings.json
 M AGENTS.md
 M CLAUDE.md
?? planeta.toml
+ 22 directorios nuevos en .claude/skills/ y en .agents/skills/
```
✅ **La fusión en `CLAUDE.md`/`AGENTS.md` es correcta y no destructiva**: inyecta entre marcas
`<!-- cosmos:inicio -->` / `<!-- cosmos:fin -->`, deja intacto lo anterior, y es idempotente
(segunda `sincronizar` → sigue en 4 ficheros tocados). El bloque lleva el índice de los 22 oficios
más el listado de ríos. Esto **sí** lo carga Claude Code.

❌ Pero el resto está roto: **E-01** y **E-02**.

---

# 3. La carga perezosa, medida

**Funciona, y es lo mejor del proyecto.** Aquí van los números, no la opinión.

### 3.1 Coste de entrada

| Método | Entrada | Peor nicho | +agua | Universo | Descarga |
|---|---|---|---|---|---|
| `aprox` (por defecto) | 1.343 | 2.383 | **3.546** | 140.862 | 98,3 % |
| `exacto` (tiktoken/cl100k_base) | 1.313 | 2.406 | **3.654** | 142.688 | 98,3 % |

Desviación aprox↔exacto en la cifra que decide: **3,0 %**, dentro del ±5 % publicado. La métrica no
miente.

### 3.2 El descenso real hasta una herramienta ejecutable

No es una estimación: es la suma de las salidas reales de los comandos.

```
paso                                             bytes   ~tok
ENTRADA galaxia/COSMOS.md                         1960    490
abrir trading                                     1294    324
abrir trading/bots                                 148     37
abrir trading/bots/codigo-de-bot                  1914    478
abrir trading/bots/codigo-de-bot/toxiproxy        1723    431
-------------------------------------------------------------
TOTAL descenso hasta la herramienta                      1760
```

**1.760 tokens de 142.688 = 1,2 % del universo.** La promesa central se cumple, medida de punta a
punta. Un `abrir` de un continente cuesta 37 tokens: nombra a sus hijos y nada más.

### 3.3 Intentos de romperla

| Vía | ¿Arrastra carga? | Evidencia |
|---|---|---|
| `usa:` (trading declara `usa: [ingenieria-datos, infraestructura]`) | **No** | `abrir trading` no menciona ninguno de los dos. Pero eso significa que la relación declarada es **invisible** para el agente que navega — la pierde. |
| Un índice que describe en vez de nombrar | **Parcial** | `abrir trading` y `abrir trading/bots` listan hijos **sin** resumen. `abrir trading/bots/codigo-de-bot` los lista **con** resumen (6 líneas). Inconsistente por nivel: es más caro cuanto más abajo, justo al revés de lo deseable. |
| Un fichero que arrastra a otro | **No** | Cada `abrir` lee su nodo y los frontmatter de sus hijos. |
| **`cosmos mapa`** | **SÍ, y mucho** | 418 líneas / 10.479 bytes ≈ **2.620 tokens**. Es **1,5× el descenso guiado entero**. Está en `--help` como *«muestra el árbol completo para inspección»*, sin ningún aviso de coste: un agente que empieza por «a ver qué hay aquí» se gasta más que haciendo el recorrido completo. **E-10.** |
| **`cosmos arrancar` / `compilar`** | **SÍ, lo más caro del sistema** | ≈9.900 tokens por ejecución, incluso cuando no cambia nada. **E-03.** |

---

# 4. El recorrido del agente sin contexto

Tres tareas reales, recorridas con los verbos, contando pasos y tokens.

```
========================================================================
T1  "necesito montar un bot de trading"
  paso 1  ENTRADA galaxia/COSMOS.md ....................    490 tok
  paso 2  cosmos buscar montar un bot de trading .......    190 tok
  paso 3  cosmos abrir trading .........................    324 tok
  paso 4  cosmos abrir trading/bots ....................     37 tok
  paso 5  cosmos abrir trading/bots/codigo-de-bot ......    478 tok
  paso 6  cosmos abrir …/codigo-de-bot/toxiproxy .......    431 tok
  --> 6 pasos, 1950 tokens          ACIERTO: buscar clavó el nº1
========================================================================
T2  "tengo que auditar la seguridad de una web"
  paso 1  ENTRADA ......................................    490 tok
  paso 2  cosmos buscar auditar la seguridad de una web     203 tok
  paso 3  cosmos abrir ciberseguridad ..................    314 tok
  paso 4  cosmos abrir ciberseguridad/ofensiva .........    120 tok
  paso 5  cosmos abrir web/calidad-de-sitio/lighthouse .    382 tok
  --> 5 pasos, 1509 tokens          FALLO: ver abajo
========================================================================
T3  "quiero un pipeline de datos que no se rompa"
  paso 1  ENTRADA ......................................    490 tok
  paso 2  cosmos buscar pipeline de datos que no se rompa   172 tok
  paso 3  cosmos abrir ingenieria-datos ................    203 tok
  paso 4  cosmos abrir ingenieria-datos/calidad ........    133 tok
  paso 5  cosmos abrir ingenieria-datos/calidad/pandera     489 tok
  --> 5 pasos, 1487 tokens          ACIERTO: nº1 exacto
```

**5-6 pasos y ~1.500-1.950 tokens por tarea.** El recorrido es corto, barato y termina en una
herramienta que se ejecuta. Eso funciona.

**T2 es el fallo, y es representativo.** Para «auditar la seguridad de una web», `buscar` devolvió:

```
  1.  cumplimiento/web-legal/paginas-legales   <- páginas legales, no seguridad
  2.  web/calidad-de-sitio/lighthouse          <- rendimiento, no seguridad
  3.  blockchain
  4.  ciberseguridad/analisis/…/auditor-de-skills   <- audita skills, no webs
  5.  agentes-ia/construccion/plan-auditado
```

Las herramientas correctas **existen** —`zaproxy` y `sqlmap` en `ciberseguridad/ofensiva/explotacion`,
`nuclei` y `amass` en `…/reconocimiento`— y **ninguna aparece**. Peor: repitiendo la consulta con el
nombre de la herramienta dentro,

```bash
python3 -m cosmos buscar escanear vulnerabilidades web zap
  1.  extraccion                                    <- "Sacar datos del mundo: webs, PDF…"
  2.  ciberseguridad/ofensiva/reconocimiento/nuclei
```
`zaproxy` sigue sin salir, y el nº1 es un oficio entero equivocado. Y bajando a mano tampoco se
llega: los hijos de `ciberseguridad/ofensiva` se llaman `explotacion`, `reconocimiento`,
`post-explotacion`, `codigo-ofensivo` — ninguno dice «auditar una web».

Esto no es una anécdota: es la cifra que el propio sistema publica.

```bash
python3 -m cosmos acertar
```
```
  Ajuste ......... 33/50 (66 %)   los encargos que SÍ se miran al trabajar
  Validación ..... 8/20 (40 %)   escritos aparte; no guían ninguna decisión

  La cifra que vale es 40 %.
  Y la brecha es de 26 puntos: parte de lo ganado es puntería sobre
  las preguntas conocidas, no un árbol que lleve mejor.
```
✅ **Mérito grande:** el repo mide su propia contra-métrica, sella el holdout y publica 40 % sin
maquillarlo, diciendo además que el 66 % está contaminado. Eso es honestidad de la buena.
❌ **Realidad de uso:** **3 de cada 5 veces el catálogo no lleva a la herramienta correcta.**
Es el techo real del producto hoy, y pesa más que cualquier otro hallazgo de esta lista salvo E-01.

---

# 5. La integración con Claude Code

Aquí es donde se cae, y lo comprobé con el mecanismo real, no con las specs.

### 5.1 En el propio repo COSMOS: no hay integración

```bash
ls ~/cosmos/CLAUDE.md          ->  No such file or directory
find ~/cosmos/.claude -type f  ->  (vacío: sólo el dir .claude/skills con 2 symlinks)
git -C ~/cosmos ls-files | grep -c '^CLAUDE.md'  ->  0
```
Un agente que abre Claude Code dentro de `~/cosmos` **no recibe nada**. Ni el índice, ni los verbos.

`enganchar --sesion` instala hooks, pero lo que inyectan es una línea de estado:

```bash
echo '{"session_id":"test-e","cwd":"…","hook_event_name":"SessionStart","source":"startup"}' \
 | PYTHONPATH=… /usr/local/bin/python3 -m puente.sesion
```
```json
{"systemMessage": "COSMOS  sesion  verde  entrada 3546 / 4000 tokens",
 "hookSpecificOutput": {"hookEventName": "SessionStart",
                        "additionalContext": "COSMOS  sesion  verde  entrada 3546 / 4000 tokens"}}
```
**47 caracteres.** El «presupuesto de entrada 3.546/4.000 tokens» que el sistema vigila con tanto
cuidado **nadie lo gasta**: no hay nada que inyecte esos 3.546 tokens en una sesión de Claude Code.
Se está midiendo, presupuestando y protegiendo con hooks un coste hipotético.

`G04` (*«exige haber leído entero lo que la configuración declare»*) sería el mecanismo para forzar
la lectura del índice — pero es inerte: `lecturas_exigidas()` lee `[sesion].lecturas_exigidas` y
`cosmos.toml` no tiene esa clave. El propio docstring lo dice: *«El mecanismo se trae; la política,
no»*.

El repo ya lo sabe, en `research/<agencia>-HARNESS.md:22`:
> *«Es la pieza que le falta a COSMOS hoy — `cosmos/compilar.py` sólo compila el árbol sobre sí
> mismo, nunca sobre un repo ajeno.»*

### 5.2 En un repo proyectado: el bloque manda ejecutar algo que no existe

El bloque que `proyectar` inyecta en el `CLAUDE.md` ajeno termina así:

```
rio/abrir: Carga un nodo cuando toca: su cuerpo, su estrella y por donde seguir bajando.
rio/buscar: Encuentra el nodo por intencion sin conocer el arbol; …
rio (mantenimiento, 'cosmos abrir rio/x'): acertar, arrancar, compilar, …
```

Soy el agente en ese repo. Hago lo que me dice:

```bash
cd destino/vh-ref
cosmos abrir rio/abrir              ->  command not found: cosmos
python3 -m cosmos abrir rio/abrir   ->  /usr/local/bin/python3: No module named cosmos
ls cosmos.toml                      ->  No such file or directory
```
❌ **La proyección no instala el paquete `cosmos`, ni un `cosmos.toml`, ni un wrapper.** El agente
recibe un índice estático de 22 oficios y **cero forma de descender**. La carga perezosa —el
producto entero— muere en el repo destino. **E-01, crítico.**

### 5.3 Los 22 pueblos proyectados son invisibles para Claude Code

`sincronizar` copió 22 pueblos a `.claude/skills/`. Su frontmatter:

```yaml
# destino/vh-ref/.claude/skills/toxiproxy/SKILL.md
---
cosmos: pueblo
nombre: toxiproxy
padre: trading/bots/codigo-de-bot
resumen: Corta la red a proposito entre el bot y el mercado: latencia, timeout y conexion caida.
---
```

El que exige Claude Code (skill real instalada en la máquina, `~/<arnes>/.claude/skills/agent-browser/SKILL.md`):

```yaml
---
name: agent-browser
description: Browser automation CLI for AI agents. Use when …
allowed-tools: Bash(agent-browser:*)
---
```

Conteo sobre los 37 `SKILL.md` del repo destino:
```
SKILL.md totales .......................... 37
con name+description (Claude Code las ve) . 15   <- las propias de vh-ref, preexistentes
SIN name/description (invisibles) ......... 22   <- las 22 que proyectó COSMOS, todas

invisibles: backtesting-py, ccxt, eventsourcing, freqtrade, hftbacktest, hummingbot, hypothesis,
ib-async, nautilus-trader, openbb, pyportfolioopt, python-statemachine, quantconnect-lean,
quantstats, rotki, ta-lib, talipp, tenacity, time-machine, toxiproxy, vectorbt, yfinance
```
**22 de 22 proyectadas, 0 de 22 visibles.** Y el verificador del propio COSMOS da verde:

```bash
python3 -m puente.proyectar comprobar destino/vh-ref
->  proyección correcta · nichos=trading        EXIT=0
```
❌ **Un verde falso.** `comprobar` verifica el contrato de COSMOS consigo mismo, no que el anfitrión
vea nada. Es exactamente el antipatrón que el propio repo predica en `mar/revision` y en
`mar/resistencia` («un valor mostrado no es un valor conocido»). **E-02, crítico.**

Nota: los 2 symlinks de `~/cosmos/.claude/skills/` (`probar-salida`, `revisar-formato`) tienen el
mismo frontmatter, así que **también son invisibles en el propio repo de Darío**.

---

# 6. La documentación

| Fuente | Tamaño | Veredicto |
|---|---|---|
| `README.md` | 6.348 B | Excelente para **entender el porqué**. Inútil para **usarlo**. |
| `docs/` | 1 fichero, 147 líneas (`CALIBRACION.md`) | Sólo métrica. Y con una sección caducada (E-11). |
| `--help` de los verbos | — | **Lo mejor que hay.** Cubre lo que el README no cubre. |
| `spec/` | 11 ficheros | Normativo entre Claude y Codex. No es doc de usuario, pero es donde tuve que ir a buscar el frontmatter. |

Cobertura de verbos en la documentación de usuario:
```
verbo        README   docs/
abrir           0       0
buscar          0       0
acertar         0       0
estado          0       0
mapa            0       0
proyectar       0       0
```
**El README documenta los 8 verbos de mantenimiento (`arrancar`, `validar`, `medir`, `generar`,
`compilar`, `enganchar`, `desenganchar`, `saltar`) y ninguno de los 6 con los que se usa el
sistema.** Un desconocido competente instala COSMOS y no descubre que existe `cosmos buscar` salvo
que teclee `--help` por su cuenta.

### Lo que tuve que adivinar (= lo que le faltará al siguiente)

1. Que existe `cosmos buscar` / `cosmos abrir` → sólo por `--help`.
2. Que existe `puente.proyectar` → sólo listando `galaxia/agua/`.
3. Que el flujo de proyección es `iniciar` → editar `planeta.toml` a mano → `sincronizar`.
4. Que un árbol nuevo necesita un `galaxia.md` escrito a mano.
5. Que un sistema-solar lleva `padre: ""`.
6. Que el nombre de la galaxia no va en las rutas de sus hijos.
7. Que si el índice ya existe, `arrancar` no lo repara: hace falta `cosmos generar`.
8. Que los tests se corren con `unittest`, no con `pytest`.
9. Que para verificar el margen de la métrica hace falta un venv con `tiktoken`.

---

# 7. Topes heredados de la máquina vieja

Búsqueda dirigida sobre `galaxia/ spec/ cosmos/ puente/ README.md GOAL.md docs/`:
```bash
grep -rniE "8 ?gb|18 ?gb|ram|tres sesiones|3 sesiones|maquina vieja"  -> 0 topes
grep -rniE "max_?(workers|jobs|paralel|concurren)|nproc|cpu_count"    -> 0 resultados
grep -rn  "~|<usuario>"                            -> 0 ficheros
grep -rln "<agencia>|<agencia>|<arnes>|<dominio>"  galaxia/         -> 0 ficheros
```
✅ **Limpio, y es un mérito real.** El commit `4eb9604 feat(galaxia): los limites de la maquina
vieja salen del contenido` hizo el trabajo. Además el contenido está despersonalizado: cero rutas de
la máquina de Darío y cero marcas de <agencia> en el árbol publicable. **Nada que retirar por este
frente.**

Único residuo, y no es del contenido sino del generador: `enganchar --sesion` escribe rutas
absolutas de la máquina donde se ejecuta (**E-06**).

---

# 8. Hallazgos

## Críticos

### E-01 · El repo proyectado recibe instrucciones para un comando que no tiene
**Gravedad: crítica.** Es la muerte del producto en su caso de uso declarado.
**Evidencia**
```bash
cd destino/vh-ref            # repo tras 'puente.proyectar sincronizar'
grep -n "cosmos abrir" CLAUDE.md
  69: rio (mantenimiento, 'cosmos abrir rio/x'): acertar, arrancar, compilar, …
cosmos abrir rio/abrir             -> command not found: cosmos
python3 -m cosmos abrir rio/abrir  -> No module named cosmos
ls cosmos.toml                     -> No such file or directory
```
**Impacto** El `GOAL.md` promete *«un repo que se puede clonar sobre cualquier proyecto y que deja
el harness organizado por niveles, **con carga perezosa real y verificable**»*. En el repo destino
la carga perezosa no existe: hay un índice plano de 22 líneas y ninguna forma de bajar. Lo que
COSMOS proyecta hoy es una tabla de contenidos, no un sistema de navegación.
**Fix** `puente.proyectar` debe dejar el destino autosuficiente. Tres opciones, de menos a más:
(a) escribir un wrapper `./cosmos` en el destino que exporte `PYTHONPATH` al repo COSMOS de origen y
delegue — barato, pero ata el destino a una ruta local; (b) copiar el paquete `cosmos/` + un
`cosmos.toml` con `arbol` apuntando a los nichos proyectados — autosuficiente de verdad; (c)
publicar COSMOS como paquete instalable (`pipx install cosmos-harness`) y que la proyección escriba
la instrucción de instalación. **Recomiendo (b) para el corto plazo y (c) como destino.** Y en
cualquier caso: el bloque inyectado tiene que abrir con la línea exacta que ejecuta el primer
`buscar` en ese repo.
**Riesgo del fix** Bajo en (a)/(b). (b) mete ~200 KB de código en el repo ajeno, que hay que
declarar en el bloque de marcas para que `desproyectar` lo sepa quitar.

### E-02 · Los 22 pueblos proyectados son invisibles para Claude Code, y `comprobar` da verde
**Gravedad: crítica.**
**Evidencia** (conteo completo sobre el repo destino, arriba en §5.3)
```
SKILL.md totales 37 · con name+description 15 · SIN name/description 22
las 22 sin: backtesting-py … yfinance   (todas las que proyectó COSMOS)
python3 -m puente.proyectar comprobar destino/vh-ref -> "proyección correcta"  EXIT=0
```
Claude Code descubre skills por `name:` + `description:` en el frontmatter (comprobado contra una
skill real: `~/<arnes>/.claude/skills/agent-browser/SKILL.md`). COSMOS escribe `cosmos:`,
`nombre:`, `padre:`, `resumen:`.
**Impacto** El coste de proyectar es real (22 directorios en el repo ajeno) y el beneficio es cero.
Y como `comprobar` sale verde, nadie se entera. Afecta también a `~/cosmos/.claude/skills/`.
**Fix** Al proyectar, **traducir** el frontmatter en vez de copiarlo: emitir `name: <nombre>` y
`description: <resumen>` (y conservar los campos COSMOS, que no estorban, o moverlos a un bloque
propio). Y **`comprobar` tiene que verificar el contrato del anfitrión, no el de COSMOS**: contar
cuántas de las proyectadas tienen `name`+`description` y salir en rojo si no son todas. Sin eso,
E-02 vuelve callado.
**Riesgo del fix** Bajo. `resumen` está capado a 120 caracteres, que es una `description` corta pero
válida; conviene revisar que ese texto sirva de disparador (hoy describe la herramienta, no dice
*cuándo* usarla, que es lo que Claude Code necesita).

## Altas

### E-03 · `arrancar`/`compilar` son lo más caro del sistema, y también cuando no cambian nada
**Evidencia**
```
1ª ejecución: 262 líneas / 39.926 B ≈ 9.980 tok   (247 × "CREAR <ruta absoluta>")
2ª ejecución: 255 líneas / 39.590 B ≈  9.900 tok   (247 × "IGUAL <ruta absoluta>")
Descenso guiado completo hasta una herramienta:    1.760 tok
```
No hay `--quiet` en ninguno de los dos (`--help` de ambos, pegado arriba).
**Impacto** El primer comando que el README manda ejecutar cuesta **5,7× el recorrido entero** del
agente, en un proyecto cuya tesis es la frugalidad de contexto. Y el modo «no ha cambiado nada»
cuesta lo mismo que el modo «he creado 247 cosas».
**Fix** Por defecto, una línea de resumen (`Creadas 247; iguales 0; …` — ya se emite). Las rutas,
detrás de `--detalle`, y relativas a la raíz, no absolutas. `IGUAL` no debería imprimirse nunca sin
`--detalle`. Añadir `--quiet`/`-q`.
**Riesgo** Ninguno. `compilar --seco` ya existe y es el sitio natural para el listado largo.

### E-04 · El mecanismo que cumple el GOAL no está documentado ni es un verbo
**Evidencia** `grep -c "proyectar" README.md GOAL.md` → `0` y `0`.
`python3 -m cosmos proyectar` → `invalid choice`. Sólo aparece en `galaxia/agua/rio-proyectar.md`.
Además, ningún flag de `iniciar` (`--nombre`, `--tipo`, `--nicho`) tiene texto de ayuda, y
`iniciar` sin `--nicho` sale verde habiendo proyectado 0 skills.
**Impacto** La frase que abre el `GOAL.md` no tiene camino descubrible. Un recién llegado no llega.
**Fix** (1) `cosmos proyectar` como subcomando de primera clase; (2) sección «Montarlo sobre tu
proyecto» en el README con el flujo `iniciar → planeta.toml → sincronizar → comprobar`; (3) `help=`
en los tres flags; (4) que `iniciar` sin nichos avise en amarillo: *«contrato creado, 0 oficios
proyectados: declara `nichos` en planeta.toml y ejecuta sincronizar»*.
**Riesgo** Ninguno.

### E-05 · El README documenta el mantenimiento y no el uso
**Evidencia** tabla de §6: los 6 verbos de uso salen 0 veces en `README.md` y 0 en `docs/`.
**Impacto** Todo el valor del sistema (buscar por intención, descender barato) queda oculto tras un
`--help` que nadie garantiza que se teclee. Es el hallazgo que más fricción quita por menos trabajo.
**Fix** Sección «Cómo se usa» antes de «Cómo se sostiene», con los tres comandos y su salida real:
`cosmos buscar <lo que quieres hacer>` → `cosmos abrir <ruta>` → ejecutar. Media página.
**Riesgo** Ninguno.

### E-06 · `enganchar --sesion` escribe rutas absolutas en un fichero versionable
**Evidencia**
```json
"command": "PYTHONPATH='/private/tmp/…/cold-clone'\"${PYTHONPATH:+:$PYTHONPATH}\" '/usr/local/bin/python3' -m puente.sesion"
```
`.gitignore` sólo ignora `.claude/skills/`, no `.claude/settings.json`; `git status` tras enganchar
muestra `?? .claude/`.
**Impacto** Quien haga `git add -A` commitea la ruta de su disco y el intérprete de su máquina. En
otro clon los 5 hooks fallan en silencio (un hook que no arranca no protege nada, y G02 —«no cerrar
en rojo»— deja de existir sin avisar).
**Fix** Ruta relativa a la raíz del repo (`$CLAUDE_PROJECT_DIR`) y `python3` sin ruta absoluta; o
generar `.claude/settings.local.json` y añadirlo al `.gitignore`, que es la convención de Claude
Code para lo que es de una máquina.
**Riesgo** Bajo.

## Medias

### E-07 · La única prueba de la métrica principal se salta por defecto
**Evidencia**
```
python3 -m unittest discover -s tests -q   ->  Ran 259 tests · OK (skipped=2)
```
Con `tiktoken` instalado en un venv:
```
COSMOS_EXIGE_TOKENIZADOR=1 venv/bin/python -m unittest tests.test_medidor -v
FAIL: test_canario_f01_el_veredicto_exacto_sigue_en_rojo
AssertionError: 3654 not greater than 4000 : el veredicto exacto ya es verde: F01 está cerrado, borra este canario
```
**Impacto** Doble: el margen ±5 % nunca se verifica en una ejecución normal (fallo F03, ya conocido),
y —esta vez en positivo— **el canario lleva días queriendo avisar de que F01 se cerró y nadie lo
oye**, porque sólo habla si hay tokenizador. Un test que sólo corre si alguien monta un venv a mano
no corre.
**Fix** `tiktoken` en un `requirements-dev.txt`, `COSMOS_EXIGE_TOKENIZADOR=1` en el workflow de CI, y
el README diciendo cómo se corren los tests (`unittest`, no `pytest`).
**Riesgo** Ninguno.

### E-08 · `arrancar` no deja un árbol nuevo en verde, contra lo que promete la spec
**Evidencia** dir vacío + `cosmos.toml` → `EXIT=1`, `E05: se esperaba exactamente una galaxia; hay 0`.
`spec/NUCLEO.md` §6: *«`arrancar` es el único que deja un árbol nuevo en verde de una vez»*.
Y con el índice ya creado, `arrancar` tampoco lo repara: hace falta `cosmos generar` (intento 5).
**Impacto** El bootstrap sólo funciona sobre un árbol que ya tiene una galaxia escrita a mano, cosa
que ninguna doc de usuario explica. El README dice «deja el clon en verde» y es cierto **sólo la
primera vez y sólo para un clon de COSMOS**.
**Fix** Que `arrancar` sobre un árbol sin galaxia escriba el `galaxia.md` mínimo (preguntando el
nombre o tomándolo del directorio) en vez de salir en rojo — es el mismo criterio que ya aplica al
índice («lo escribe sólo si no existe»). Y matizar la frase del README.
**Riesgo** Bajo. Un `galaxia.md` ausente no puede engañar a nadie, igual que el índice ausente.

### E-09 · Mensaje de E16 sin sentido en un árbol vacío
**Evidencia** `peor nicho sin nichos: entrada 0 + agua condicional 0 = 0 tokens > 4000; excede en -4000 tokens; más caros: `
**Impacto** `0 > 4000` es falso y «excede en −4000» es un exceso negativo. Es el segundo mensaje que
ve quien monta un árbol nuevo, y no significa nada. La lista «más caros:» sale vacía.
**Fix** Guarda de árbol vacío antes del cálculo de presupuesto: si no hay nodos, E05 es el único
error que tiene sentido emitir.
**Riesgo** Ninguno.

### E-10 · `cosmos mapa` cuesta más que el recorrido entero, y no lo avisa
**Evidencia** 418 líneas / 10.479 B ≈ **2.620 tokens**, contra 1.760 del descenso completo.
`--help`: *«muestra el árbol completo para inspección»*.
**Impacto** Es la trampa más plausible para un agente sin contexto: el instinto de «déjame ver qué
hay» sale más caro que hacer bien la tarea. Un verbo así, en un sistema de carga perezosa, tiene que
declarar su precio.
**Fix** Que `--help` diga *«(caro: ~2.600 tokens; para navegar usa `buscar`)»* y que la primera línea
de la salida lo repita. Opcional: exigir `--todo` para el volcado completo y que sin flag muestre
sólo hasta continente.
**Riesgo** Ninguno.

### E-11 · `docs/CALIBRACION.md` dice que el veredicto exacto está en rojo, y ya no lo está
**Evidencia** doc, líneas 137-147: *«exacto entrada=2.778 agua=1.545 con_agua=4.323 ROJO, excede en
323 · El árbol **no cabe** en 4.000 con el tokenizador de referencia»*.
Medido hoy con `tiktoken 0.14.0` sobre `b0c1ebd`:
```
venv-calib/bin/python -m cosmos medir --metodo exacto
  Peor con agua ... 3.654 tokens
  Presupuesto ..... 4.000     OK, quedan 346 tokens en el peor caso con agua
```
**Impacto** La única documentación técnica del repo afirma un fallo abierto que se cerró (por el
commit que adelgazó el contenido). Miente en dirección pesimista, que es la menos dañina, pero
`informes-casos-raros.md` §1 es explícito: quien cambia el estado real actualiza el documento.
**Fix** Actualizar §«Pendiente» a cerrado con la medición de hoy, y borrar el canario
`test_canario_f01_el_veredicto_exacto_sigue_en_rojo` como el propio test pide en su mensaje.
**Riesgo** Ninguno.

## Bajas

### E-12 · `buscar` acierta 2 de cada 5, y en «auditar la seguridad de una web» falla entero
**Evidencia** `cosmos acertar` → validación sellada **8/20 (40 %)**. Caso reproducible completo en §4.
`buscar escanear vulnerabilidades web zap` no devuelve `zaproxy`, que existe en
`ciberseguridad/ofensiva/explotacion`.
**No lo subo a crítico** porque el repo lo mide, lo publica sin maquillar y explica el método
(«BM25 léxico … NO es un agente»). Es una limitación declarada, no un engaño. Pero es el techo real:
el 60 % de las veces el agente no llega.
**Fix** El mayor retorno está en los `resumen`, no en el motor: hoy describen **qué es** la
herramienta y el encargo llega en lenguaje de **qué quiero hacer**. Un `resumen` que empiece por el
encargo («Escanea una web publicada en busca de vulnerabilidades…») sube el BM25 sin tocar código.
Segundo: `--juez` con un modelo local ya está implementado — usarlo para medir la brecha entre
léxico y semántica antes de decidir si hace falta un motor mejor.
**Riesgo** Ninguno; `resumen` está capado a 120 caracteres y el validador lo vigila (E00).

### E-13 · `abrir` describe a los hijos en unos niveles y no en otros
**Evidencia** `abrir trading` y `abrir trading/bots` → hijos sin resumen (37 tok el segundo).
`abrir trading/bots/codigo-de-bot` → 6 hijos **con** resumen (478 tok).
**Impacto** El principio declarado es *«el índice nombra a los hijos; no los describe»*. Se cumple
arriba y se rompe abajo, que es donde hay más hijos. Es defendible (el último salto necesita elegir
entre herramientas parecidas) pero no está declarado en ninguna spec, así que un mantenedor futuro
no sabrá cuál de los dos comportamientos es el correcto.
**Fix** Declararlo en `spec/COMPOSICION.md` como regla («los hijos hoja se describen; los
intermedios sólo se nombran») o unificarlo. Cualquiera de las dos, pero escrita.
**Riesgo** Ninguno.

### E-14 · `usa:` es invisible para quien navega
**Evidencia** `galaxia/sistemas/trading.md` declara `usa: [ingenieria-datos, infraestructura]`.
`cosmos abrir trading` no los menciona (grep vacío salvo el «se usa» de la prosa de la estrella).
**Impacto** Lo bueno: **no arrastra carga**, que era mi hipótesis de rotura y queda desmentida. Lo
malo: una relación declarada en el modelo que el agente nunca ve es una relación que no existe.
**Fix** Una línea al pie de `abrir`: `── oficios que este usa ── ingenieria-datos, infraestructura`.
Sólo nombres, ~10 tokens, sin cargar nada.
**Riesgo** Ninguno.

### E-15 · La proyección reordena `.claude/settings.json` del repo ajeno sin añadir nada
**Evidencia**
```
git diff --stat  ->  .claude/settings.json | 10 +++----
```
El diff son 5 claves movidas a orden alfabético. Ningún valor perdido (verificado clave a clave),
ninguna añadida.
**Impacto** El río promete *«lo que hubiera antes sigue ahí»* y se cumple, pero ensucia el diff de un
repo ajeno con ruido cosmético. En un PR de un tercero eso es fricción gratuita.
**Fix** Reescribir el fichero sólo si el contenido efectivo cambia (comparar dicts, no bytes), y
preservar el orden original.
**Riesgo** Ninguno.

### E-16 · El índice dice «Veintiun oficios» y hay 22
**Evidencia**
```
grep -c '^- ' galaxia/COSMOS.md   -> 22
grep -o 'Veinti[a-z]*'            -> Veintiun
ls galaxia/sistemas | wc -l       -> 22
cosmos estado -> sistema-solar  22
```
**Impacto** Trivial en tokens, pero está en el `resumen` de la galaxia: es la primerísima frase que
lee un agente, y la única del sistema que se inyecta también en cada repo proyectado. Un número mal
en la línea de entrada erosiona la confianza en todo lo demás.
**Fix** El `resumen` de la galaxia no debería llevar un número escrito a mano — o se genera, o se
quita el número.
**Riesgo** Ninguno.

---

# 9. Lo que un recién llegado NO puede hacer hoy

1. **Usar COSMOS desde Claude Code sin que se lo cuenten.** No hay `CLAUDE.md` en el repo y el hook
   de `SessionStart` inyecta 47 caracteres de estado. El agente no sabe que el árbol existe.
2. **Descender en un repo proyectado.** `cosmos: command not found` (E-01). Recibe un índice y nada
   más.
3. **Que sus pueblos proyectados sirvan de algo.** 22 de 22 invisibles, y el verificador dice verde
   (E-02).
4. **Enterarse de que existen `buscar`, `abrir`, `acertar`, `estado`, `mapa` y `proyectar`** leyendo
   la documentación (E-05).
5. **Montar COSMOS sobre su proyecto siguiendo el README.** El verbo que lo hace no aparece en el
   README ni en el GOAL (E-04).
6. **Crear un árbol nuevo sin leer `spec/FRONTMATTER.md` y sin abrir un nodo real para copiar
   convenciones.** Me costó 5 intentos y 3 hechos adivinados (E-08).
7. **Correr los tests.** El comando intuitivo (`pytest`) falla y el que funciona no está escrito.
8. **Fiarse de `docs/CALIBRACION.md`**, que afirma un fallo ya cerrado (E-11).
9. **Encontrar cómo auditar la seguridad de una web**, teniendo el sistema `zaproxy`, `sqlmap`,
   `nuclei` y `amass` dentro (E-12).

---

# 10. Mejoras, por fricción que quitan

| # | Mejora | Hallazgos | Esfuerzo | Fricción que quita |
|---|---|---|---|---|
| 1 | **Traducir el frontmatter al proyectar** (`name`/`description`) y que `comprobar` valide el contrato del anfitrión | E-02 | S | Convierte 22 ficheros muertos en 22 skills vivas. Es la diferencia entre proyectar y no proyectar. |
| 2 | **Dejar el destino autosuficiente**: paquete + `cosmos.toml`, y el bloque inyectado abriendo con el comando exacto | E-01 | M | Resucita la carga perezosa fuera de `~/cosmos`. Sin esto, el GOAL no se cumple. |
| 3 | **Sección «Cómo se usa» en el README**: `buscar` → `abrir` → ejecutar, con salida real | E-05 | S | Media página. Hace descubrible todo el valor del sistema. |
| 4 | **Callar `arrancar`/`compilar`** por defecto; rutas relativas tras `--detalle` | E-03 | S | −9.900 tokens por ejecución en el primer comando del README. |
| 5 | **Un `CLAUDE.md` en el propio COSMOS** que cargue el índice y enseñe los verbos | §5.1 | S | Hace que el presupuesto de 4.000 tokens sea un coste real y no hipotético. Y hace que el repo se coma su propia comida. |
| 6 | **`cosmos proyectar` como verbo + doc del flujo** `iniciar → planeta.toml → sincronizar` | E-04 | S | Hace descubrible el mecanismo que cumple el GOAL. |
| 7 | **Reescribir los `resumen` en clave de encargo**, no de definición | E-12 | M | Es la palanca real sobre el 40 %, y no toca código. |
| 8 | **`tiktoken` en dev-deps + `COSMOS_EXIGE_TOKENIZADOR=1` en CI** | E-07 | S | El canario deja de estar mudo; la métrica se verifica sola. |
| 9 | **Actualizar `docs/CALIBRACION.md` y borrar el canario F01** | E-11 | S | El repo deja de afirmar un fallo que ya arregló. |
| 10 | **Rutas relativas en los hooks de `enganchar`** o `settings.local.json` | E-06 | S | Los guardarraíles siguen vivos en el segundo clon. |
| 11 | **Avisar del coste de `mapa`**; guarda de árbol vacío en E16; `usa:` al pie de `abrir`; el número del resumen de la galaxia | E-10, E-09, E-14, E-16 | S | Pulido. Barato y quita cuatro tropiezos concretos. |

---

# 11. Lo que ya funciona sin ayuda de nadie

Dicho sin rebaja, porque me puse a tumbarlo y no pude:

- **El clon en frío.** `git clone` → `arrancar` → verde en **4,28 s**, con `python3` de sistema, sin
  `pip install`, sin venv, sin variables de entorno, sin nada que preguntar. Los 8 pasos que da el
  README dan `EXIT=0`.
- **La carga perezosa es real y la medí de punta a punta.** 1.760 tokens del índice a una
  herramienta ejecutable, contra 142.688 del universo: **1,2 %**. No es una estimación del propio
  sistema, es la suma de las salidas de los comandos. Y `usa:` no arrastra carga: mi principal
  hipótesis de rotura falló.
- **`buscar` + `abrir` son un buen par.** 190 tokens para encontrar, 431 para abrir una herramienta
  con licencia, estrellas, fecha comprobada, comandos que se copian y la frontera de lo que NO
  hace. La última línea de `buscar` te dice qué hacer después: nada que adivinar.
- **`validar` cuesta 25 bytes** y `medir` 741, declarando el método y lo que no mide (`no_medido`).
  Los verbos baratos son baratos de verdad.
- **La honestidad de la métrica.** `medir --metodo exacto` con `tiktoken` da 3.654 contra 3.546 del
  estimador: **3,0 % de desviación**, dentro del ±5 % publicado. Y `acertar` publica 40 % con el
  holdout sellado, avisando de que el 66 % del ajuste está contaminado. Un proyecto que publica su
  peor número sin que nadie se lo pida es un proyecto en el que se puede confiar.
- **`--help` es buena documentación.** Los 13 verbos con una línea cada uno; `abrir --help` y
  `buscar --help` explican los flags de verdad. Es la pieza que salva la experiencia.
- **La fusión en `CLAUDE.md`/`AGENTS.md` del repo ajeno es correcta**: marcas propias, no
  destructiva, idempotente. El mecanismo está bien pensado; lo que falla es lo que mete dentro.
- **El contenido está limpio de esta máquina.** 0 rutas `~`, 0 marcas
  <agencia>/<agencia> en `galaxia/`, 0 topes de RAM o de concurrencia. El commit `4eb9604` cerró ese
  frente y no queda deuda de la máquina vieja que retirar (§7).
- **259 tests en 89 s, `OK`,** en un clon recién bajado, sin instalar nada.

**Veredicto de mi ángulo.** La premisa que me dieron —«COSMOS sólo funciona en el Mac de Darío y con
quien ya se lo sabe»— es **falsa en su primera mitad y verdadera en la segunda**. El repo se clona y
funciona en cualquier máquina con Python 3: eso lo intenté tumbar y no pude. Lo que no funciona es
*fuera* del repo: proyectado sobre otro proyecto, COSMOS deja un índice sin navegador (E-01) y 22
ficheros que el anfitrión no lee (E-02), y su propio verificador da verde. Y sí funciona sólo «con
quien ya se lo sabe»: los seis verbos con los que se usa el sistema no están en ninguna
documentación de usuario (E-05), y el mecanismo que cumple la frase de portada del `GOAL.md` no se
nombra ni una vez en el README ni en el propio `GOAL.md` (E-04).

Arreglando E-01, E-02 y E-05 —dos de ellos con cambios pequeños— el producto pasa de «funciona para
su autor» a «funciona para quien lo clone».
