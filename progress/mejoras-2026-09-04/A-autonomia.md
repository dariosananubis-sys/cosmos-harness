# A — Autonomía en otra máquina + integración de `claude-modelos`

**Ángulo:** que COSMOS, clonado en un Mac nuevo, deje al agente trabajando **libre** (sin pedir
permiso, iniciando sesión donde haga falta, decidiendo y anotando) y que el mantenedor de modelos
`claude-modelos` viva dentro de COSMOS sin arrastrar nada de la máquina de origen.

**Estado del árbol auditado (pin, `.claude/rules/informes-casos-raros.md` §6):**

```
git -C ~/cosmos rev-parse HEAD          -> 892f669
git -C ~/cosmos status --porcelain | wc -> 0
python3 -m cosmos validar               -> verde (2 saltos activos: P01, P02)  0 errores
python3 -m cosmos medir                 -> peor con agua 3.701 / 4.000; quedan 106 tok
```

Trabajo **solo de lectura** sobre `~/cosmos`. El único fichero escrito es este.

**Convención de este documento:** todas las rutas son portables (`~`, `$HOME`,
`$CLAUDE_CONFIG_DIR`). Cero referencias a organizaciones, clientes o a la máquina donde se redactó.

---

## 0. Cómo pide permiso Claude Code 2.1.x (hechos verificados, con fuente)

Versión instalada al medir: **2.1.260** (`claude --version`). Todo lo de esta sección está
comprobado en la máquina o citado de la documentación oficial; lo que no pude comprobar se dice.

### 0.1 Los seis modos, y cuál arranca por defecto

`claude --help` (2.1.260) declara los valores aceptados por `--permission-mode`:

```
--permission-mode <mode>   (choices: "acceptEdits", "auto", "bypassPermissions",
                            "manual", "dontAsk", "plan")
```

La documentación ([code.claude.com/docs/en/permission-modes](https://code.claude.com/docs/en/permission-modes),
«Available modes») los describe así — `manual` es el alias de `default`:

| Modo | Qué corre sin preguntar |
|---|---|
| `default` (alias `manual`) | Solo lecturas |
| `acceptEdits` | Lecturas, ediciones de fichero y órdenes de ficheros comunes (`mkdir`, `mv`, `cp`…) |
| `plan` | Lecturas, más las órdenes que apruebe el clasificador si hay modo `auto` |
| `auto` | **Todo**, con comprobaciones de seguridad en segundo plano (un modelo clasificador) |
| `dontAsk` | Solo las herramientas pre-aprobadas |
| `bypassPermissions` | Todo, sin comprobación ninguna |

**Hecho que cambia el diseño de todo esto:** en un Mac nuevo con plan Pro, Max o Team, en terminal
o en la extensión de VS Code, **el modo de arranque incorporado ya es `auto`** (requiere 2.1.228 o
posterior en macOS). Es decir: *«que en otros PC no pidan permiso»* está a mitad de camino de fábrica
— y `auto` es el modo que Anthropic recomienda para trabajo autónomo, porque un clasificador revisa
las acciones en vez de bloquearlas.

Excepciones documentadas en las que el arranque cae a `default` aunque el plan sea Pro/Max: cualquier
fichero de ajustes con `disableAutoMode: "disable"`, el *feature-flag fetching* apagado, la primera
sesión tras instalar o actualizar, `claude -p` y el Agent SDK, los proveedores de nube, y los planes
Enterprise o una clave de Console.

### 0.2 Qué se puede y qué NO se puede poner en `settings.json`

Verificado en la doc de ajustes ([code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings),
sección de precedencia y «el fichero no puede fijar ese valor»), literal:

> `permissions.defaultMode` values `auto` and `bypassPermissions` **don't take effect from project or
> local settings**; set them in **user or managed settings** instead, or pass `--permission-mode` for
> one session. Before v2.1.257, `bypassPermissions` took effect from any file.

Con 2.1.260 esto ya aplica. Consecuencia dura para COSMOS:

| Fichero | ¿Puede fijar `bypassPermissions`? |
|---|---|
| `~/.claude/settings.json` (o `$CLAUDE_CONFIG_DIR/settings.json`) — **usuario** | **Sí** |
| `managed-settings.json` — organización | Sí |
| `<repo>/.claude/settings.json` — proyecto | **No** (se ignora en silencio; la sesión arranca en Manual) |
| `<repo>/.claude/settings.local.json` — local | **No** |

→ **COSMOS no puede volver libre a un repositorio escribiendo dentro del repositorio.** El modo de
autonomía es una decisión **de máquina**, no de proyecto. Eso decide el §2 entero.

Otras piezas verificadas del mismo sistema:

- `permissions.allow` **no tiene ningún efecto** en `bypassPermissions`; las reglas `deny` bloquean
  en todos los modos, `bypassPermissions` incluido. Las reglas `allow` sí valen en `auto`, `default`,
  `acceptEdits` y `dontAsk`, y son la vía correcta para «no preguntes por esto en concreto».
- `permissions.disableBypassPermissionsMode: "disable"` y `permissions.disableAutoMode: "disable"`
  funcionan **desde cualquier ámbito**: un usuario puede cerrarse a sí mismo la puerta.
- Acciones que **ningún modo auto-aprueba**, `bypassPermissions` incluido: reglas `ask` explícitas,
  `AskUserQuestion`, herramientas MCP con `requiresUserInteraction`, `rm`/`rmdir` sobre *critical
  paths*, y los dos resguardos de mensajería entre sesiones.
- En Linux y macOS Claude Code **se niega a arrancar** en `bypassPermissions` como root o bajo
  `sudo`.

### 0.3 El diálogo que sí bloquea en una máquina nueva, y la clave que lo apaga

Doc de `permission-modes`, sección «Skip all checks with bypassPermissions mode», literal:

> The first time you start an interactive session with this mode enabled, Claude Code shows a warning
> dialog asking you to accept responsibility... **Claude Code saves your acceptance to user settings**,
> so the dialog appears only once. If you decline, Claude Code exits. In non-interactive mode no
> dialog is shown, and a background session started with `--bg` is refused until you've accepted the
> dialog in an interactive session.

La clave concreta donde se guarda esa aceptación **no está documentada**, pero es comprobable por
los dos lados:

```bash
# 1) la cadena existe en el binario instalado
LC_ALL=C grep -a -c skipDangerousModePermissionPrompt \
  ~/.local/share/claude/versions/2.1.260          -> 11

# 2) y aparece como clave de PRIMER NIVEL en el settings.json de usuario
python3 -c 'import json,pathlib;d=json.loads((pathlib.Path.home()/".claude/settings.json").read_text());print(d.get("skipDangerousModePermissionPrompt"))'
                                                  -> True
```

> `skipDangerousModePermissionPrompt` es una clave **de primer nivel** de `settings.json` (no va
> dentro de `permissions`), booleana, y es la aceptación guardada del diálogo. **No documentada**:
> se marca `UNVERIFIED-DOC` y se usa sabiendo que puede cambiar de nombre. Escribirla a mano es
> equivalente a haber contestado «sí» una vez.

El **segundo** diálogo que frena una máquina nueva es el de confianza de carpeta. Su rastro no está
en `settings.json` sino en `~/.claude.json`, dentro de `projects.<ruta absoluta>`:

```
claves de una entrada de proyecto: [... 'hasTrustDialogAccepted', ...]
```

Verificado leyendo las claves (no los valores) de `~/.claude.json`. Con `-p` o con la salida
redirigida el diálogo de confianza se salta solo, pero en TUI interactiva bloquea.

### 0.4 Lo que NO se puede hacer desde ajustes, en una lista

1. Fijar `bypassPermissions` o `auto` desde `.claude/settings.json` o `.claude/settings.local.json`
   de un repositorio (§0.2). Silencioso: no hay error, la sesión arranca en Manual.
2. Entrar en `bypassPermissions` a mitad de una sesión que no arrancó con él disponible («You can't
   enter `bypassPermissions` from a session you started without it enabled»).
3. Saltarse las reglas `ask`, `AskUserQuestion`, ni el `rm -rf` sobre un *critical path* (§0.2).
4. Correr en `bypassPermissions` como root/sudo.
5. **`claude config` ya no existe como subcomando en 2.1.260** — comprobado: la lista de `Commands:`
   de `claude --help` trae `agents, attach, auth, auto-mode, doctor, gateway, import, install, logs,
   mcp, plugin, project, respawn, rm, setup-token, stop, ultrareview, update`, y ningún `config`.
   Cualquier receta que diga `claude config set …` está muerta: se escribe el JSON.

### 0.5 La combinación correcta y portable, y por qué no es la más agresiva

| Objetivo | Vía correcta en 2.1.x | Comentario |
|---|---|---|
| Que no pregunte, con red de seguridad | `permissions.defaultMode: "auto"` en ajustes **de usuario** | Ya es el defecto en Pro/Max; ponerlo explícito lo hace inmune a que el *feature flag* no llegue |
| Que no pregunte **nada**, sin clasificador | `permissions.defaultMode: "bypassPermissions"` en ajustes de usuario + `skipDangerousModePermissionPrompt: true` | Sin la segunda clave, la **primera** sesión interactiva de esa máquina pide aceptar responsabilidad, y `--bg` se niega hasta entonces |
| Lo mismo, por sesión | `claude --dangerously-skip-permissions` (equivalente a `--permission-mode bypassPermissions`) | Gana a los ajustes; es lo que hace un lanzador |
| Dejar el modo *disponible* sin activarlo | `claude --allow-dangerously-skip-permissions` | Lo añade al ciclo de Shift+Tab |
| Pre-aprobar cosas concretas conservando el clasificador | `permissions.allow: ["Bash(git *)", …]` | **Inútil en bypass**: allí las reglas `allow` no se miran |

**Recomendación para COSMOS: `auto` como grado por defecto y `bypassPermissions` como grado
explícito.** Motivo, y es del propio proyecto: `spec/GUARDARRAILES.md` ya decidió no portar
`permissionDecision: "ask"` porque *«en modo autónomo no hay nadie al otro lado»*. Coherente. Pero
`bypassPermissions` **apaga también el clasificador que revisa `rm` en rutas críticas y los mensajes
entre sesiones**, y la propia doc lo restringe a contenedores y VM. Ofrecer los dos grados, decir en
voz alta cuál se escribió y poder volver atrás es la lectura correcta de «toda puerta tiene salida».

---

## 1. Carta de autonomía (texto completo + ubicación + presupuesto medido)

### 1.1 Dónde vive: océano, y **fusionado** con `irreversible` — no uno nuevo

**P0.** Las tres ubicaciones que plantea el encargo, juzgadas con los números del árbol:

| Candidata | Veredicto |
|---|---|
| Océano nuevo `galaxia/agua/oceano-autonomia.md` | **No cabe.** Ver §1.2: quedan 106 tokens de presupuesto y un océano nuevo con contenido cuesta ~130 |
| Trozo del bloque que inyecta `proyectar` | **Redundante.** `puente/proyectar.py:349` (`bloque()`) ya emite `contexto_inicial(...)`, que por `spec/NUCLEO.md` §2 incluye **el cuerpo de todos los océanos**. Un océano viaja al repo ajeno sin escribir una línea de más; meterlo aparte sería la duplicación que E17 existe para cazar |
| `systemMessage` del hook `SessionStart` (G01) | **No es su sitio, pero sí tiene un papel.** Un `systemMessage` no está en el árbol, no lo mide `medir`, no lo vigila E17 y no viaja con `proyectar`: sería exactamente la «exhortación» que `GOAL.md` §2 prohíbe. Lo que sí le corresponde a G01 es **la coherencia**: decir en rojo si la carta promete libertad y la máquina está preguntando (§2.5) |

**Decisión: `galaxia/agua/oceano-irreversible.md` se reescribe como
`galaxia/agua/oceano-autonomia.md`** (`nombre: autonomia`), absorbiendo su contenido. Cinco razones,
ninguna de gusto:

1. **El techo de océanos aguanta pero el de tokens no.** E12 permite 7 (`cosmos.toml`
   `[presupuesto] oceanos = 7`, `cosmos/validar.py:404`) y hay 5 — cabrían dos más. Pero E16 mide
   tokens, no ficheros, y ahí solo quedan 106 (§1.2). El límite que muerde es el otro.
2. **Son la misma política, por sus dos caras.** El océano actual ya termina diciendo *«Lo reversible
   se hace entero y sin preguntar»*: la carta de autonomía **es** esa frase desarrollada. Escribir un
   océano nuevo que empiece por ahí es la «reedición» que describe `spec/GUARDARRAILES.md` §E17 —
   misma política, otras palabras— y sería un candidato serio a rojo de E17 entre dos nodos que
   siempre están cargados a la vez.
3. **`spec/UNIVERSO.md` no se toca.** La carta no es un oficio ni un mar: no altera los 22 nichos ni
   los 6 mares, así que no abre el mapa que Darío aprobó el 2026-09-01 (el punto 7 de
   `PENDIENTE-DARIO.md` deja claro qué sí requiere su sí).
4. **`spec/NUCLEO.md` §2 lo cobra en `entrada` y por tanto en E16.** Es lo que se quiere: una regla
   que se paga siempre tiene que estar dentro del presupuesto que la vigila, no fuera de él.
5. **El recuento «5 oceanos» del índice es generado** (`cardinales()`, fijado por
   `tests/test_cifras_de_las_specs.py:138`). Fusionar mantiene el 5 y no hay ninguna cifra escrita a
   mano que corregir.

Corolario que hay que decir en voz alta: **la carta no puede ser larga.** No porque haya que ser
breve —eso es una exhortación—, sino porque se paga en cada sesión de cada oficio y el presupuesto
es un techo duro. Lo que no quepa aquí baja a un río (`rio-autonomia.md`, §2.6), que se paga solo al
invocarlo.

### 1.2 Presupuesto medido, antes y después

```
$ python3 -m cosmos medir            # árbol en 892f669, sin tocar
  Peor con agua ... 3.701 tokens
  Presupuesto ..... 4.000    OK, quedan 106 tokens con el margen calibrado (+5,2 %)
                             en el peor caso con agua (ciberseguridad); ≈ 3 herramienta(s) más
  Lo más caro de la entrada evaluada:
    3.  101 tok  oceano/irreversible      5.  88 tok  oceano/secretos
    4.   91 tok  oceano/verificar         6.  75 tok  oceano/precedencia
                                          7.  35 tok  oceano/descender
```

Y el candidato, medido **con el propio medidor del repo** (no a ojo):

```bash
python3 - <<'PY'
from cosmos.medir import contar_aprox
import pathlib
actual = pathlib.Path("galaxia/agua/oceano-irreversible.md").read_text("utf-8").split("---",2)[2].strip()
print("cuerpo actual :", contar_aprox(actual), "tok")     # -> 93 tok
print("cuerpo nuevo  :", contar_aprox(NUEVO), "tok")      # -> 130 tok  (texto de §1.3)
PY
```

| | tokens del cuerpo | efecto en E16 (margen +5,2 %) |
|---|---|---|
| `oceano/irreversible` hoy | 93 | — |
| `oceano/autonomia` propuesto | **130** | **+39** |
| Holgura del presupuesto | 106 → **67** | ≈ 2 herramientas más en el peor nicho, en vez de 3 |

**Ese es el precio y no se disimula: la carta cuesta una herramienta del peor nicho.** Dos formas
de recuperarla, las dos ya sobre la mesa y ninguna necesaria para que esto entre en verde:

- Los **3 retiros firmes** que propone `PENDIENTE-DARIO.md` §5 (`claude-seo-ai`, `mythril`,
  `talipp`) **no ayudan aquí**: viven en `visibilidad`, `blockchain` y `trading`, y E16 mide el peor
  nicho, que es `ciberseguridad` (35 pueblos). Decirlo evita la tentación de venderlo como
  compensación.
- Lo que sí bajaría el peor caso es el **agua condicional** (1.231 tok: `mar/pruebas` 332,
  `mar/criterio` 289, `mar/revision` 208, `mar/resistencia` 196). No entra en este encargo y no se
  toca.

### 1.3 El texto completo propuesto

Fichero: **`galaxia/agua/oceano-autonomia.md`** (sustituye a `oceano-irreversible.md`).

```markdown
---
cosmos: oceano
nombre: autonomia
moja: ["**"]
resumen: Se ejecuta sin pedir permiso; solo espera un sí lo que no tiene vuelta atrás.
---

Se ejecuta sin pedir permiso: instalar, escribir, lanzar, entrar en un servicio con las credenciales
del alta. Ante la duda se decide y se anota. Un encargo es una orden de hacerlo, no de conversar.

Espera un sí lo que no tiene vuelta atrás: pagar, borrar datos o cuentas, publicar, escribir en
nombre de alguien, forzar la rama principal. Se llega hasta el borde, se deja lista con su importe o
su alcance exacto, y se pide el visto bueno para esa concreta. Un permiso de otro día no vale.
```

Comprobaciones hechas sobre ese texto exacto, no sobre la intención:

| Invariante | Resultado |
|---|---|
| **E07** (`resumen` ≤ 120 car.) | 77 caracteres ✅ |
| **E08** (el resumen aporta palabras fuera del nombre) | «ejecuta», «permiso», «vuelta atrás» ✅ |
| **E10 / E11** (`moja` de un océano) | `["**"]`, literal exigido ✅ |
| **E12** (≤ 7 océanos) | siguen siendo **5** ✅ |
| **E16** (presupuesto) | 3.701 → ~3.740 de 4.000 ✅ (§1.2) |
| **E17** (solape entre co-cargables) | **0,0000** contra los **32** nodos co-cargables del árbol (océanos, agua con `moja` y estrellas); umbral 0,25 ✅ |

La medición de E17 se hizo con las funciones del propio validador (`cosmos.validar._normalizar`,
`PALABRAS_VACIAS_E17`, `MINIMO_PALABRAS_AFIRMACION=4`, `MINIMO_PALABRAS_COMPARTIDAS=3`), reproducible:

```bash
cd ~/cosmos && python3 - <<'PY'
import re
from cosmos import validar as V
from cosmos.modelo import cargar_arbol, cuerpo
arbol = cargar_arbol("galaxia", tambien=("registro",))
NUEVO = open("/dev/stdin").read()      # o el literal de §1.3
def afirms(t):
    o=[]
    for f in re.split(r"[.;:\n]", t):
        p=[w for w in V._normalizar(f).split() if w not in V.PALABRAS_VACIAS_E17]
        if len(p) >= V.MINIMO_PALABRAS_AFIRMACION: o.append((frozenset(p), f.strip()))
    return o
peor=(0,None)
for n in arbol.nodos:
    if n.cosmos=="oceano" and n.nombre=="irreversible": continue
    if n.cosmos not in ("oceano","mar","lago","estrella"): continue
    if n.cosmos in ("mar","lago") and not n.datos.get("moja"): continue
    for sa,_ in afirms(NUEVO):
        for sb,_ in afirms(cuerpo(n)):
            c = sa & sb
            if len(c) >= V.MINIMO_PALABRAS_COMPARTIDAS:
                peor = max(peor, (len(c)/len(sa|sb), f"{n.cosmos}/{n.nombre}"))
print(peor)          # -> (0, None): ningún par comparte 3 palabras con contenido
PY
```

### 1.4 Lo que el texto **no** dice, a propósito

- **No nombra a Claude Code, ni un flag, ni un fichero de ajustes.** Un océano es una política de
  quien trabaja; el runtime es el §2. Si mañana el CLI renombra `--dangerously-skip-permissions`, la
  carta no envejece.
- **No dice «no pidas permiso NUNCA».** Dice qué es lo que sí espera un sí. La lista corta de frenos
  —pagar, borrar datos o cuentas, publicar, escribir en nombre de alguien, forzar la rama
  principal— es la que ya estaba, verificada contra `spec/GUARDARRAILES.md` («guardas de shell
  destructivo… es seguridad de puesto de trabajo, no de COSMOS»).
- **No repite «se anota dónde».** Eso ya es `oceano/verificar` («si un paso se saltó, se dice») y
  repetirlo dispararía E17 con razón.
- **No menciona `~/.cosmos/credenciales.txt` por su ruta.** Dice «las credenciales del alta»:
  `oceano/secretos` es quien manda sobre cómo se leen, y nombrar la ruta aquí sería la segunda
  copia de una política que ya tiene dueño.

---

## 2. Mecanismo (ficheros, JSON exacto, verbo, reversibilidad)

### 2.1 Por qué NO es `enganchar --libre` — y esto es medible, no una preferencia

`cosmos enganchar` escribe **dentro del repositorio** (`.claude/settings.json` y `.git/hooks/`,
`cosmos/guardarrailes.py:388` y `:266`). Y §0.2 demuestra que `permissions.defaultMode:
"bypassPermissions"` **se ignora en silencio** desde ahí en 2.1.257+. Un `enganchar --libre`
escribiría una clave que Claude Code no mira y saldría en verde: sería un guard que aprobó sin haber
podido mirar, el fallo que `spec/GUARDARRAILES.md` («Cuando el guard no puede decidir») nombra como
el más silencioso que puede tener un sistema de vigilancia.

**Va en `cosmos configurar`.** Es el verbo del **alta de máquina**: ya escribe fuera del repositorio
(`~/.cosmos/perfil.toml`, `~/.cosmos/credenciales.txt`, `cosmos/configurar.py:22-24`), ya tiene
sub-modos por bandera (`--comprobar`, `--llavero`, `--seco`), y el modo de permisos es exactamente
del mismo tipo: **una decisión de máquina, no de proyecto**.

### 2.2 La interfaz

```bash
python3 -m cosmos configurar --autonomia            # dice en qué grado está la máquina y no toca nada
python3 -m cosmos configurar --autonomia auto       # P0 · defecto recomendado: sin preguntas, con clasificador
python3 -m cosmos configurar --autonomia libre      # bypassPermissions + aceptación del diálogo
python3 -m cosmos configurar --autonomia manual     # revierte: deja el fichero como estaba
python3 -m cosmos configurar --autonomia libre --seco   # enseña el JSON que escribiría y sale
```

Tres grados y ni uno más. `acceptEdits`, `plan` y `dontAsk` existen en el CLI pero no responden a la
pregunta «¿es libre esta máquina?»; quien los quiera los pone a mano o los pasa por bandera. Un
`--autonomia` con seis valores sería la abstracción prematura que `.claude/rules/development.md` §2
prohíbe.

### 2.3 Dónde escribe, y cómo lo encuentra en cualquier máquina

```python
def ajustes_de_usuario() -> Path:
    """El settings.json de ámbito USUARIO, que es el único que puede fijar el modo (§0.2)."""
    base = os.environ.get("CLAUDE_CONFIG_DIR")
    return (Path(base) if base else Path.home() / ".claude") / "settings.json"
```

Nada de rutas absolutas de una máquina. `CLAUDE_CONFIG_DIR` primero porque la documentación oficial
dice que, si está puesta, «Claude Code then stores your settings, session history, and plugins
there instead» — y quien usa sesiones aisladas por cuenta la tiene puesta.

### 2.4 El JSON exacto, por grado

**Grado `auto` (P0).** Se escribe **una** clave:

```json
{
  "permissions": {
    "defaultMode": "auto"
  }
}
```

**Grado `libre` (P1).** Dos claves, y la segunda es la que hace que una máquina *nueva* no se pare:

```json
{
  "permissions": {
    "defaultMode": "bypassPermissions"
  },
  "skipDangerousModePermissionPrompt": true
}
```

Sin `skipDangerousModePermissionPrompt` la primera sesión interactiva de esa máquina abre el diálogo
de responsabilidad (§0.3) y `claude --bg` se **niega** hasta que alguien lo conteste — es decir, el
caso «PC nuevo, trabajo desatendido» falla exactamente donde importa. Con ella, el arranque es limpio.
La clave no está documentada: la salida del comando **lo dice** («clave no documentada; si Claude
Code la renombra, el diálogo vuelve una vez y `--autonomia libre` la reescribe»).

**Lo que el comando NO escribe, y lo dice:**

- `permissions.allow`: en `bypassPermissions` **no se mira** (§0.2); en `auto` sobra, porque el
  clasificador ya aprueba. Escribir una allowlist «por si acaso» es coste sin efecto.
- `permissions.deny`: sería política de puesto de trabajo. `spec/GUARDARRAILES.md` ya decidió no
  portar las guardas de shell destructivo por eso mismo, y el freno real de COSMOS es el océano.
- `hasTrustDialogAccepted` en `~/.claude.json`: **es un fichero de estado del CLI, no de ajustes**, y
  se rellena solo al confiar una carpeta. Escribirlo por debajo es falsificar el consentimiento del
  dueño de la máquina. El comando **avisa** de que la primera TUI en una carpeta nueva pedirá
  confianza y de que con `-p` no aparece.

### 2.5 Reversibilidad: el mismo patrón que `enganchar_sesion`, sin inventar nada

Se copia el mecanismo ya probado de `cosmos/guardarrailes.py:483-580`, que es el estilo de la casa:

| Pieza | En `enganchar --sesion` | En `configurar --autonomia` |
|---|---|---|
| Respaldo de los bytes originales | `.cosmos/enganche-sesion.json` | **`~/.cosmos/autonomia.json`** (fuera del repo, 600, como el perfil) |
| Marca de «esto es nuestro» | la cadena `puente.sesion` dentro del `command` | las **claves declaradas** en el respaldo + **su valor exacto** |
| Poda | `podar_sesion(datos)` | `podar_autonomia(datos, escritas)` |
| Vuelta atrás byte a byte | si lo podado == lo podado del original → reescribe el original | idéntico |

Respaldo, con todo lo que hace falta para deshacer y para no mentir:

```json
{
  "esquema": 1,
  "existia": true,
  "creo_directorio": false,
  "original": "<los bytes exactos del settings.json anterior>",
  "grado": "libre",
  "escritas": {"permissions.defaultMode": "bypassPermissions",
               "skipDangerousModePermissionPrompt": true},
  "cuando": "2026-09-04T09:00:00Z"
}
```

Regla de la poda, calcada de `spec/NUCLEO.md` §7 (entradas obsoletas del manifiesto), porque el
problema es el mismo — *«¿esto lo escribí yo o lo tocó alguien?»*:

1. La clave está y su valor **coincide** con el del respaldo → es nuestra: se quita.
2. La clave está y su valor **no coincide** → alguien la cambió a mano: **no se toca**, se avisa y se
   saca del respaldo. Nunca se pisa la decisión de otro.
3. `permissions` queda como objeto vacío → se elimina la clave entera, igual que `podar_sesion` hace
   con `hooks`.
4. Si tras podar el fichero es idéntico al original podado y el fichero **no existía** antes → se
   borra, y el directorio si lo creamos nosotros y está vacío.

Y lo que dice al terminar, siempre, porque «explícito y reversible» significa que se lee la factura:

```
COSMOS  configurar  autonomia  libre

  Escrito en ~/.claude/settings.json (ambito usuario; CLAUDE_CONFIG_DIR sin definir)
    permissions.defaultMode            = "bypassPermissions"   (nuevo)
    skipDangerousModePermissionPrompt  = true                  (nuevo; clave no documentada)
  Respaldo del fichero anterior en ~/.cosmos/autonomia.json
  Vuelta atras: python3 -m cosmos configurar --autonomia manual

  Ojo: bypassPermissions apaga tambien el clasificador que revisa `rm` en rutas criticas.
       La primera TUI en una carpeta nueva sigue pidiendo confianza (eso no se escribe por debajo).
```

### 2.6 El guardarraíl que impide que la carta sea una mentira

**P0, y es la pieza que convierte esto en COSMOS y no en un README.** `GOAL.md` §2 corolario 1: *«Si
una regla tiene que recordarse, está mal puesta. Se convierte en estructura o en guardarraíl.»* La
carta del §1 promete que no se pide permiso. Si la máquina arranca en Manual, la carta es una
exhortación — y encima una que el agente se cree.

Se amplía **G01** (`SessionStart`, `puente/sesion.py`), que ya mide la entrada y ya sabe emitir texto:

```
COSMOS  entrada 3.740 tok de 4.000
COSMOS  el oceano `autonomia` promete que no se pide permiso y esta sesion arranca en `default`
        (Manual). Arreglalo con: python3 -m cosmos configurar --autonomia auto
```

Tres reglas para que el propio aviso no mienta —regla 14 de `.claude/rules/revisor-adversarial.md`,
la bandera trivalente:

1. El modo se lee de `permission_mode` **del sobre del evento**. Es un campo común de los hooks, pero
   la documentación avisa: *«Not all events receive this field»*. Comprobado que la cadena existe en
   el binario 2.1.260 (55 apariciones), **no** comprobado que `SessionStart` la traiga.
2. Si el campo no viene, se lee `permissions.defaultMode` del `settings.json` de usuario. Eso dice el
   **defecto**, no el modo real: un `--permission-mode` en la línea de comandos lo pisa.
3. Si no hay ninguna de las dos, el aviso es **`desconocido`**, nunca «Manual» ni «libre». `AUSENTE ==
   AUSENTE` no es una medición.

G01 **nunca bloquea** (así está especificado en `spec/GUARDARRAILES.md`), y su válvula es la que ya
tiene: `cosmos saltar G01 --motivo "..." --caduca 7d`.

### 2.7 El lanzador: uno sí, otro no

**Sí — `~/.local/bin/cosmos` (P1).** Es otro problema, y es el crítico **E-01** de la auditoría de uso:
el bloque proyectado manda ejecutar `cosmos abrir …` y en el repo destino eso da `command not found`.
Un shim de cuatro líneas lo arregla sin meter 200 KB en el repo ajeno:

```bash
#!/usr/bin/env bash
# generado por 'cosmos configurar --lanzador'; se quita con '--lanzador quitar'
COSMOS_RAIZ="__RAIZ__"          # la raíz del clon, resuelta al instalar
exec env PYTHONPATH="$COSMOS_RAIZ${PYTHONPATH:+:$PYTHONPATH}" python3 -m cosmos "$@"
```

Es la opción (a) de E-01 y su límite se declara: ata el destino a la ruta local del clon, así que
`cosmos estado` tiene que decir si el shim apunta a un directorio que ya no existe.

**No — un lanzador de permisos.** La escalera anti-overengineering de `.claude/rules/development.md`
§2 para en el primer peldaño que aguante, y aquí aguanta el peldaño 4 (funcionalidad nativa de la
plataforma): `permissions.defaultMode` en ajustes de usuario ya deja **todas** las sesiones libres —
terminal, VS Code, `--bg`—, mientras que un `claudelibre` solo cubre las que se arranquen con él.
Quien quiera una sesión suelta tiene la línea oficial y `--autonomia --seco` se la imprime:

```bash
claude --dangerously-skip-permissions      # equivale a --permission-mode bypassPermissions
```

### 2.8 Tests nuevos que exige esto (unittest, cero dependencias)

En `tests/test_configurar.py` (que ya existe) o en `tests/test_autonomia.py`:

| Test | Qué afirma |
|---|---|
| `test_escribe_solo_las_dos_claves` | Tras `--autonomia libre` sobre un settings con 5 claves ajenas, el fichero tiene 7 y las 5 ajenas son idénticas |
| `test_destino_respeta_CLAUDE_CONFIG_DIR` | Con la variable puesta escribe ahí; sin ella, en `~/.claude/settings.json`. Con `HOME` y la variable apuntando a un `tmpdir` |
| `test_vuelta_byte_a_byte` | `libre` y luego `manual` devuelven el fichero **idéntico** (`read_bytes()`), incluida la indentación rara del original |
| `test_no_pisa_valor_cambiado_a_mano` | Si alguien pone `defaultMode: "plan"` después, `manual` **no** lo borra, lo dice y sale 0 |
| `test_no_existia_se_borra` | Si no había `settings.json`, `manual` lo elimina y elimina el directorio si lo creamos |
| `test_seco_no_escribe_nada` | `--seco` imprime el JSON y el disco no cambia (mtime + bytes) |
| `test_g01_avisa_cuando_el_modo_no_acompana` | Evento `SessionStart` con `permission_mode: "default"` y el océano en el árbol → el `systemMessage` contiene el aviso |
| `test_g01_calla_cuando_el_modo_acompana` | Mismo evento con `"auto"` o `"bypassPermissions"` → **no** hay aviso. (La pareja obligatoria de `spec/GUARDARRAILES.md` «Verificación exigida» §7) |
| `test_g01_dice_desconocido_sin_campo` | Evento **sin** `permission_mode` y sin settings legibles → el texto dice `desconocido`, nunca «Manual» |
| **Mutación** en `puente/tests/mutaciones.py` | Romper la comparación de valores de `podar_autonomia` (que borre siempre) tiene que poner **roja** a `test_no_pisa_valor_cambiado_a_mano` |

El gate (`puente/gate.py`) corre la suite sobre la instantánea del índice: ninguno de estos tests
puede leer el `~/.claude/settings.json` real ni depender del árbol de trabajo. Todos usan `tmpdir` +
`unittest.mock.patch.dict(os.environ, {"HOME": ..., "CLAUDE_CONFIG_DIR": ...})`.

---

## 3. `claude-modelos` súper ordenado dentro de COSMOS

### 3.0 Qué se conserva, qué se generaliza, qué se tira

Lo que hay hoy en `claude-modelos` (README, `install.sh`, `uninstall.sh`, `bin/modelos-fijar.py`,
`bin/maxcode`, `bin/ultracode`, `bin/_effort-preflight.sh`), leído entero:

| Pieza | Veredicto | Motivo |
|---|---|---|
| Reponer `additionalModelOptionsCache` de forma **idempotente y atómica** (`mkstemp` + `os.replace`, respeta lo que venga del servidor) | **Se conserva tal cual** | Es exactamente la escritura atómica que `spec/NUCLEO.md` §7 exige para el manifiesto. Ya está bien resuelto |
| LaunchAgent `RunAtLoad` + `WatchPaths` + `StartInterval 300` | **Se conserva la forma** | Las tres capas son necesarias: `WatchPaths` agrupa eventos, `RunAtLoad` cubre el reinicio, `StartInterval` es la red |
| Hook `SessionStart` con `sleep 3` en segundo plano | **Se conserva** | Su README lo justifica con una medición: sin el hook, un `/model` abierto a los ~6 s no las veía |
| Copia el vigilante a `~/.claude/bin` porque launchd no lee `~/Desktop` (TCC) | **Se conserva la idea, no la ruta** | El destino pasa a `~/.cosmos/bin/`, que es donde COSMOS ya guarda lo suyo fuera del repo |
| Etiqueta con el nombre de una organización (`com.<organizacion>.claude-modelos`) | **Se generaliza** → `com.cosmos.modelos` | `GOAL.md` §5: cero nombres de organización |
| `WatchPaths` con `~/.secrets/<organización>/…/sessions` | **Se tira y se sustituye** | Ruta de una máquina y de una organización. §3.2 |
| Preflight que lee un JSON de cuota dentro de otro repositorio, en `~/Desktop/<arnés>/…` | **Se tira** | §3.5 |
| Lista de modelos 4.x (`claude-opus-4-8` … `claude-sonnet-4-5`) | **Se sustituye** por la familia Claude 5 | §3.3 |
| `MAXCODE_VERIFY` encendido por defecto (2 pasadas, ×2 tokens) | **Se conserva, apagado por defecto** | §3.6 |

### 3.1 Dónde vive dentro de COSMOS — las cuatro preguntas del encargo, respondidas

| Pregunta | Respuesta | Por qué |
|---|---|---|
| ¿Verbo `cosmos modelos …`? | **No.** Va como `cosmos configurar --modelos instalar\|estado\|quitar` | Los quince verbos de COSMOS son verbos; `modelos` es un sustantivo. Y sobre todo: **es alta de máquina**, exactamente como `--autonomia` (§2.1). `configurar` queda con cuatro caras: oficios+credenciales, autonomía, modelos, lanzador. Si algún día son ocho, se parte en un `cosmos maquina`; hoy sería la abstracción prematura de `development.md` §2 |
| ¿`enganchar --modelos`? | **No.** `enganchar` es ámbito **repositorio** (`.git/hooks`, `.claude/settings.json` del repo). Esto escribe en `~/Library/LaunchAgents` y en los ajustes de **usuario** | Mezclar los dos ámbitos en un verbo es lo que hizo que `enganchar --sesion` escribiera rutas de una máquina en un fichero versionable (auditoría **E-06**) |
| ¿`puente/modelos.py`? | **Sí, ahí exactamente** | `cosmos/` es el núcleo (árbol, validador, medidor) y no sabe qué runtime hay. `puente/` es la frontera con Claude Code: `sesion.py`, `proyectar.py`, `gate.py`. Un vigilante de `~/.claude.json` + launchd es 100 % frontera |
| ¿Río `rio-modelos.md`? | **No: `rio-configurar.md`**, que **hoy no existe y debería** | Un río por **verbo** (`spec/NUCLEO.md` §2). Hay 17 ríos y 15 verbos, y `configurar` —verbo desde el 2026-09-03— **no tiene el suyo**: es un hueco de coherencia real, no una excusa. Con `momento: mantenimiento` cuesta solo su nombre en la línea agrupada del catálogo |
| ¿Un pueblo del catálogo? | **No, y esto es firme** | `PENDIENTE-DARIO.md` §5-bis retiró del catálogo `lanzadores-de-modelo`, `cuentas-del-asistente` y `quota-oficial` por orden literal de Darío: *«proceso interno… lanzadores del CLI de una persona»*. Volver a meterlos como pueblo sería deshacer esa decisión por la puerta de atrás. El catálogo es «lo que alguien contrataría»; esto es fontanería del propio COSMOS |

### 3.2 Fichero a fichero

#### `puente/modelos.py` — nuevo, funciones puras + tres acciones

**Regla que cumple desde la primera línea:** *nada se instala solo al importar el paquete*
(`README.md`, `spec/GUARDARRAILES.md`). El módulo define constantes y funciones; ninguna acción
corre en el import, ni siquiera leer `~/.claude.json`.

```python
"""Mantiene el selector de modelos de Claude Code con las entradas de la cuenta.

Claude Code arma el menu de /model con sus opciones nativas MAS el array
`additionalModelOptionsCache` de ~/.claude.json, que el propio CLI rellena desde el
servidor en cada arranque: lo anadido a mano se pierde. Aqui se repone, de forma
idempotente y atomica, sin tocar lo que venga del servidor.
"""
from __future__ import annotations
import json, os, tempfile
from dataclasses import dataclass
from pathlib import Path

ETIQUETA = "com.cosmos.modelos"                  # sin nombre de organizacion (GOAL §5)
MARCA    = "generado-por-cosmos-modelos"         # como MARCA_HOOK en guardarrailes.py
BASE     = Path.home() / ".cosmos"               # el mismo sitio que perfil.toml (700/600)


@dataclass(frozen=True)
class Modelo:
    valor: str          # el id que se le pasa al CLI
    etiqueta: str       # lo que se ve en el menu
    nota: str           # una linea

# UNICA fuente de verdad de la lista. El rio y el README la citan; un test compara.
MODELOS: tuple[Modelo, ...] = (
    Modelo("claude-fable-5-1",           "Fable 5.1", "Fable 5.1 · lo mas capaz"),
    Modelo("claude-opus-5",              "Opus 5",    "Opus 5 · razonamiento duro"),
    Modelo("claude-sonnet-5",            "Sonnet 5",  "Sonnet 5 · rapido y barato"),
    Modelo("claude-haiku-4-5-20251001",  "Haiku 4.5", "Haiku 4.5 · el mas rapido"),
)


def ajustes_usuario() -> Path:                    # identica a la de §2.3: una sola definicion
    base = os.environ.get("CLAUDE_CONFIG_DIR")
    return (Path(base) if base else Path.home() / ".claude") / "settings.json"


def configs_vigilados(perfil: dict | None = None) -> list[Path]:
    """Los .claude.json a reponer. NUNCA una ruta escrita a mano en el codigo."""
    vistos: dict[Path, None] = {}
    vistos[Path.home() / ".claude.json"] = None                    # 1. el global
    if (cd := os.environ.get("CLAUDE_CONFIG_DIR")):                # 2. el del dir aislado
        vistos[Path(cd) / ".claude.json"] = None
    for extra in ((perfil or {}).get("configs") or []):            # 3. los que declare el perfil
        p = Path(extra).expanduser()
        (vistos.update({q: None for q in sorted(p.glob("*/.claude.json"))})
         if p.is_dir() else vistos.setdefault(p, None))
    return list(vistos)


def entradas_deseadas() -> list[dict]:
    return [{"value": m.valor, "label": m.etiqueta, "description": m.nota} for m in MODELOS]


def repone(config: Path) -> list[str]:
    """Anade las que falten. Devuelve los ids anadidos; [] si no tocaba nada."""
    try:
        datos = json.loads(config.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []                                   # ilegible: se anota fuera, no se rompe nada
    actuales = datos.get("additionalModelOptionsCache")
    actuales = actuales if isinstance(actuales, list) else []
    presentes = {o.get("value") for o in actuales if isinstance(o, dict)}
    faltan = [e for e in entradas_deseadas() if e["value"] not in presentes]
    if not faltan:
        return []
    datos["additionalModelOptionsCache"] = actuales + faltan
    _atomico(config, json.dumps(datos, indent=2, ensure_ascii=False))
    return [e["value"] for e in faltan]


def _atomico(ruta: Path, texto: str) -> None:
    """Temporal en el MISMO directorio + os.replace. NUNCA en el sitio (NUCLEO §7)."""
    fd, tmp = tempfile.mkstemp(dir=str(ruta.parent), prefix=f".{ruta.name}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(texto)
        os.chmod(tmp, 0o600)
        os.replace(tmp, ruta)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
```

Cambios frente al original, uno a uno y con su porqué:

1. **`SESIONES_GLOB` con la ruta de una organización desaparece.** La sustituye
   `configs_vigilados()`: el global, el de `$CLAUDE_CONFIG_DIR` y los que el usuario declare en
   `~/.cosmos/perfil.toml`. Ninguna ruta de máquina en el código.
2. **El respaldo `.json.bak-modelos` se retira.** Con `os.replace` atómico no hay estado intermedio
   que perder, y un `.bak` que solo se escribe la primera vez envejece hasta ser una foto de hace
   meses — es peor que no tenerlo (mismo argumento que `spec/NUCLEO.md` §7 sobre el manifiesto
   truncado). Quien quiera respaldo, tiene `--seco`.
3. **`chmod 0o600` se conserva**: `~/.claude.json` lleva estado de sesión.
4. Un `.claude.json` ilegible **no aborta el resto**, pero **se anota** en la salida y en el log; no
   se traga en silencio (`spec/GUARDARRAILES.md`, «cuando el guard no puede decidir»).

#### `~/.cosmos/perfil.toml` — tabla opcional nueva

```toml
[perfil]
oficios = ["ciberseguridad", "trading"]
herramientas = ["nmap", "ccxt"]
credenciales_comprobadas = true

# Opcional. Solo si tienes varios directorios de configuracion de Claude Code
# (por ejemplo, uno por cuenta con CLAUDE_CONFIG_DIR). Un DIRECTORIO se expande a
# sus */.claude.json; un FICHERO se toma tal cual. Rutas con ~ permitidas.
[modelos]
configs = ["~/mis-cuentas-claude"]
duro    = "claude-opus-5"        # el modelo de `maxcode`/`ultracode`; por defecto, este
```

`cosmos/configurar.py:perfil_toml()` hoy serializa a mano tres claves. Hay que extenderla para
conservar `[modelos]` al reescribir el perfil — **si no, `cosmos configurar` borraría la tabla del
usuario en la siguiente alta**, que es la clase de sorpresa por la que se desinstala un sistema.

#### El LaunchAgent — `~/Library/LaunchAgents/com.cosmos.modelos.plist`

```xml
<key>Label</key>            <string>com.cosmos.modelos</string>
<key>ProgramArguments</key> <array>
  <string>__PYTHON__</string>          <!-- sys.executable resuelto al instalar -->
  <string>__HOME__/.cosmos/bin/modelos-reponer.py</string>
</array>
<key>RunAtLoad</key>      <true/>
<key>WatchPaths</key>     <array><!-- una linea por configs_vigilados() --></array>
<key>StartInterval</key>  <integer>300</integer>
<key>StandardOutPath</key><string>__HOME__/.cosmos/logs/modelos.log</string>
<key>StandardErrorPath</key><string>__HOME__/.cosmos/logs/modelos.log</string>
```

- **`~/.cosmos/bin/modelos-reponer.py`** es una copia de arranque de `puente/modelos.py` (nueve
  líneas: `import`, `configs_vigilados`, bucle, `print`). Se copia por el mismo motivo TCC que
  documenta el original —launchd no lee dentro de `~/Desktop` ni `~/Documents`— y además porque un
  LaunchAgent que apunta al clon se rompe el día que el clon se mueve. `--modelos estado` compara el
  SHA-256 de la copia con el del módulo y dice **`desactualizado`** si no coinciden.
- **`__PYTHON__` se resuelve al instalar** con `sys.executable`, no se escribe `/usr/bin/python3` a
  pelo: en un Mac sin Command Line Tools ese binario dispara el instalador de Xcode (el propio README
  original lo avisa), y COSMOS exige ≥ 3.11 por `tomllib`. Se comprueba la versión **antes** de
  escribir el plist y se sale en rojo diciendo cuál se encontró.
- **macOS solamente.** En Linux no hay launchd: la acción instala el hook `SessionStart` y **dice
  que no instala agente**. Declarar el límite, nunca fingir cobertura.

#### El hook `SessionStart`, fusionado sin pisar nada

Se reutiliza literalmente el mecanismo de `cosmos/guardarrailes.py` (`_es_entrada_nuestra` +
`podar_*` + respaldo de los bytes originales), apuntando a los ajustes **de usuario** y con `MARCA`
en el comando para reconocer lo propio:

```json
{ "hooks": { "SessionStart": [ { "hooks": [ { "type": "command", "timeout": 5,
  "command": "bash -c 'nohup bash -c \"sleep 3; __PYTHON__ $HOME/.cosmos/bin/modelos-reponer.py\" >/dev/null 2>&1 &' # generado-por-cosmos-modelos" } ] } ] } }
```

Diferencia con el `install.sh` original, y es un fallo real de aquél: allí el filtro es
`"modelos-fijar" not in json.dumps(e)`, que casa por **nombre de fichero**. Si el usuario renombra el
script, `uninstall.sh` deja el hook huérfano para siempre. Aquí la marca es una cadena propia y
estable, igual que `MARCA_HOOK = "cosmos-enganchar"`.

#### `~/.local/bin/maxcode` y `~/.local/bin/ultracode`

Se conservan con su nombre (Darío ya los teclea) y con **una regla nueva, la de la casa**: *no se
pisa lo ajeno*. Si el fichero existe y **no** lleva la línea `# generado-por-cosmos-modelos`, no se
toca y se dice:

```
COSMOS  configurar  modelos  aviso
  ~/.local/bin/maxcode existe y no es nuestro: no se toca.
  Quitalo o renombralo y repite, o usa --forzar.
```

Es el mismo trato que `cosmos enganchar` le da a un pre-commit ajeno.

### 3.3 La lista de modelos: en un solo sitio, y qué se puede verificar de verdad

Fuente única: `MODELOS` en `puente/modelos.py`. Familia Claude 5 vigente:

| Menú | id |
|---|---|
| Fable 5.1 | `claude-fable-5-1` |
| Opus 5 | `claude-opus-5` |
| Sonnet 5 | `claude-sonnet-5` |
| Haiku 4.5 | `claude-haiku-4-5-20251001` |

**Qué se puede verificar sin red** (`GOAL.md` §5: cero red en el camino crítico) y qué no — medido,
no supuesto:

- ✅ **Forma, unicidad y coherencia documental.** Un test comprueba que cada `valor` casa
  `^claude-[a-z0-9.-]+$`, que no hay `valor` ni `etiqueta` repetidos, y que la tabla del río y la del
  README contienen **exactamente** esos cuatro ids — el patrón de `tests/test_cifras_de_las_specs.py`,
  que ya impide que una cifra escrita a mano envejezca.
- ✅ **Presencia efectiva.** `--modelos estado` lee cada `.claude.json` y dice cuáles de los cuatro
  están y cuáles faltan. Eso es un hecho del disco.
- ❌ **Que la cuenta acepte el id: NO se puede comprobar offline, y no se finge.** Miré el candidato
  obvio, la caché del propio CLI, y está **vacía**:

  ```bash
  python3 -c 'import json,pathlib;print(json.loads((pathlib.Path.home()/".claude.json").read_text()).get("modelAccessCache"))'
  -> []
  ```

  Cruzar contra ella daría verde por ausencia (`AUSENTE == AUSENTE`, regla 14 de
  `revisor-adversarial.md`). Así que `--modelos estado` publica **`acceso: no_comprobado`** y, junto
  a él, la línea que sí lo comprueba, para que la ejecute quien quiera pagar la cuota:

  ```bash
  claude --model claude-opus-5 -p ping     # responde -> el id vale; "not found" -> no
  ```

**Un detalle que hay que decir porque induce a error:** en la máquina de referencia el array vivo
contiene `claude-fable-5[1m]`. El sufijo `[1m]` **no es otro modelo**: es la variante de ventana de
1 M de contexto del mismo. Puede añadirse como entrada extra si se quiere en el menú, pero entonces
la nota tiene que decir «ventana de 1 M», o el menú miente sobre cuántos modelos hay.

### 3.4 Las tres acciones, y qué imprime cada una

```
python3 -m cosmos configurar --modelos estado
  COSMOS  configurar  modelos  estado
    Agente launchd .. cargado (com.cosmos.modelos, ultima ejecucion hace 2 min)   [solo macOS]
    Hook SessionStart puesto en ~/.claude/settings.json
    Copia de arranque ~/.cosmos/bin/modelos-reponer.py  AL DIA (sha coincide)
    Configs vigilados (2):
      ~/.claude.json                       4/4 presentes
      ~/mis-cuentas-claude/x/.claude.json  2/4 presentes  (faltan claude-sonnet-5, claude-haiku-4-5-20251001)
    Acceso de la cuenta a cada id ......... no_comprobado (hace falta red; ver el rio)

python3 -m cosmos configurar --modelos instalar [--seco] [--forzar]
python3 -m cosmos configurar --modelos quitar
  COSMOS  configurar  modelos  quitar
    Agente launchd descargado y ~/Library/LaunchAgents/com.cosmos.modelos.plist borrado
    Hook SessionStart quitado; ~/.claude/settings.json restaurado BYTE A BYTE
    ~/.cosmos/bin/modelos-reponer.py, ~/.local/bin/maxcode, ~/.local/bin/ultracode borrados
    Las entradas ya presentes en /model siguen ahi hasta el proximo arranque del CLI: no se borran
```

Esa última línea es del `uninstall.sh` original y es correcta: **quitar el vigilante no es borrar
datos ajenos.**

### 3.5 El preflight de cuota: **se retira**

Hoy lee un JSON de cuota bajo `~/Desktop/<arnés>/…`, un fichero que escribe la
*statusline* de otro proyecto. Dentro de COSMOS eso no existe y **nadie lo escribiría nunca**: sería
un aviso que no se dispara jamás, exactamente el caso E20 de `spec/GUARDARRAILES.md` («una
invariante que nadie ha visto fallar no se distingue de una rota»), y encima con una ruta de
organización dentro.

Se retira, y **la escalera anti-overengineering** (`development.md` §2, peldaño 4) dice con qué se
sustituye: el propio CLI ya trae `/status`, que es el dato bueno y de primera mano.

Lo que **sí** se conserva del preflight es el **rastro**, que cuesta una línea y sirve para saber
cuántas veces se tiró del modo caro:

```
~/.cosmos/logs/esfuerzo.log     {"at":"…Z","modo":"maxcode","cwd":"…","args":"…"}
```

*(Variante P2, si Darío la quiere: leer un `~/.cosmos/cuota.json` opcional con un esquema
documentado. Coste: un esquema más que mantener y un productor que COSMOS no tiene. Beneficio: nulo
mientras nadie lo escriba. Recomiendo no hacerla hasta que exista el productor.)*

### 3.6 `maxcode` / `ultracode`: dos cambios de fondo

1. **El modelo duro sale del perfil, no del script.** `MODELO_DURO` pasa a leerse de
   `[modelos] duro` de `~/.cosmos/perfil.toml`, con `claude-opus-5` por defecto. Hoy el id está
   escrito en dos ficheros distintos; el día que cambie, uno de los dos se queda atrás.
2. **La auto-verificación de dos pasadas se conserva, pero APAGADA por defecto.** Hoy está encendida
   y **duplica los tokens** de todo `maxcode -p`. En un proyecto cuyo `GOAL.md` §2 se define como
   «cero coste innecesario», un ×2 silencioso es justo lo contrario. Se invierte:
   `COSMOS_VERIFICA=1 maxcode -p "…"` la enciende, y el script lo dice en `stderr` cuando la usa.
   Además `oceano/verificar` ya obliga a verificar por medios que no cuestan el doble de contexto.

Lo demás del script se conserva porque está bien: `set -euo pipefail`, respetar un `--model` o
`--effort` que pase el usuario, y la explicación medida de por qué `max` y `ultracode` **no se
suman** (son puntos de la misma escala).

### 3.7 Tests nuevos (unittest, cero dependencias, sin tocar el disco real)

| Test | Qué afirma |
|---|---|
| `test_repone_es_idempotente` | Dos pasadas seguidas: la segunda devuelve `[]` y el fichero es **idéntico byte a byte** |
| `test_repone_respeta_lo_del_servidor` | Con entradas que no son nuestras en el array, siguen ahí, en su orden, tras reponer |
| `test_escritura_atomica_no_deja_a_medias` | Se fuerza `OSError` a mitad de escritura: el original queda intacto y no hay temporales sueltos en el directorio |
| `test_config_ilegible_no_rompe_el_resto` | Con dos configs y el primero con JSON roto: el segundo se repone y la salida **nombra** al roto |
| `test_configs_vigilados_sin_rutas_de_maquina` | `configs_vigilados({})` con `HOME` y `CLAUDE_CONFIG_DIR` en `tmpdir` devuelve **solo** rutas bajo ellos. **El canario anti-regresión de `GOAL.md` §5** |
| `test_lista_de_modelos_bien_formada` | Formato, cero duplicados en `valor` y en `etiqueta` |
| `test_lista_coincide_con_rio_y_readme` | Los ids de `MODELOS` == los de la tabla de `galaxia/agua/rio-configurar.md` == los del README. Patrón de `test_cifras_de_las_specs.py` |
| `test_no_pisa_un_maxcode_ajeno` | Con un `maxcode` sin la marca, `instalar` **no** lo reescribe y sale avisando; con `--forzar`, sí |
| `test_quitar_devuelve_settings_byte_a_byte` | Instalar y quitar deja el `settings.json` de usuario idéntico |
| `test_quitar_no_borra_entradas_del_menu` | Tras `quitar`, `additionalModelOptionsCache` sigue con sus entradas |
| `test_plist_sin_rutas_ajenas` | El XML generado no contiene ninguna ruta fuera de `$HOME` ni la palabra de ninguna organización |
| `test_importar_no_hace_nada` | `import puente.modelos` con `HOME` en un `tmpdir` **vacío**: cero ficheros creados. La regla «nada se instala al importar», vista fallar |
| **Mutación** en `puente/tests/mutaciones.py` | (a) quitar el `os.replace` y escribir en el sitio → roja `test_escritura_atomica_no_deja_a_medias`; (b) devolver siempre `faltan` sin mirar `presentes` → roja `test_repone_es_idempotente`; (c) colar una ruta absoluta ajena en `configs_vigilados` → roja `test_configs_vigilados_sin_rutas_de_maquina` |

**Compatibilidad con `puente/gate.py`:** la suite corre sobre la **instantánea del índice**, así que
ningún test puede leer `~/.claude.json`, `~/Library/LaunchAgents` ni el árbol de trabajo. Todos
parchean `HOME` y `CLAUDE_CONFIG_DIR` a un `tmpdir` y llaman a las funciones puras; `launchctl` no se
ejecuta nunca en test — `instalar()` recibe un `ejecutor` inyectable que en las pruebas solo **anota**
las órdenes, y un test comprueba la orden exacta (`launchctl bootstrap gui/<uid> <plist>`) sin
lanzarla.

---

## 4. Otras mejoras (leyendo `E-uso.md` y `cosmos/configurar.py`)

**Antes de la tabla, una que NO propongo porque ya está hecha** (gate search-first,
`.claude/rules/search-first.md`): *«que el txt de credenciales se genere y se abra solo al
instalar»*. **Ya lo hace.** `cosmos/cli.py:428-439` escribe la plantilla y llama a
`cfg.abrir_en_editor(credenciales)` salvo `--no-abrir`, y si el editor no abre **lo dice** en vez de
callarse. Lo único que falta ahí es un matiz de §A-04.

| id | Qué | Dónde | Coste | Riesgo de romper coherencia |
|---|---|---|---|---|
| **A-01** · P0 | `configurar` pregunta también por el **modo de autonomía**: tras los oficios, `¿esta máquina trabaja sin pedir permiso? [auto/libre/manual]` | `cosmos/cli.py:_configurar` + §2 | ~25 líneas | **Bajo.** Es una pregunta más en un flujo que ya pregunta dos cosas. Cuidado con `--oficios`/`--herramientas`: en modo no interactivo **no debe** preguntar ni tocar permisos sin `--autonomia` explícito |
| **A-02** · P0 | `configurar` ofrece **instalar el vigilante de modelos** al final del alta, con un `[s/N]` que por defecto es **no** | `cosmos/cli.py` + §3 | ~15 líneas | **Bajo**, si el defecto es «no». Un alta que instala un LaunchAgent sin preguntar rompe *«nada se instala solo»* |
| **A-03** · P0 | **`cosmos estado --maquina`**: qué falta en ESTA máquina — `python3` ≥ 3.11 (versión exacta), `git`, `claude` (versión), `tmux`, llavero (`security` presente y desbloqueado), `~/.cosmos/perfil.toml`, credenciales rellenas, modo de autonomía vigente, vigilante de modelos | `cosmos/estado.py` (+ flag en `cli.py`) | ~70 líneas | **Bajo**, con **una condición dura**: cada línea es **trivalente** (`ok` / `falta` / `no_comprobado`) y jamás dice `ok` por no haber podido mirar (`revisor-adversarial.md` §14). Y NO cambia el veredicto de `validar`: es inventario, como el resto de `estado` |
| **A-04** · P1 | Que `configurar` diga **cuántas credenciales quedaron a medias** y que `--comprobar` salga **1** si falta alguna | `cosmos/cli.py:379-388` | ~5 líneas | **Bajo.** Hoy imprime lo que falta y devuelve 0: un script que encadene el alta no se entera |
| **A-05** · P1 | **`python3 -m cosmos instalar`** = `arrancar` + `configurar` + (opcional) `--autonomia` + `--modelos` + `--lanzador`, en un comando y **sin `curl \| bash`** | `cosmos/cli.py` (verbo nuevo, delega) + `rio-instalar.md` | ~60 líneas + un río | **Medio.** Verbo nuevo ⇒ río nuevo (`momento: mantenimiento`) + fila en `test_rio_momento.py` + README. Nada de red: es `git clone` y luego local, como pide `GOAL.md` §5 |
| **A-06** · P1 | README: **«Instalar en un Mac nuevo» en 10 líneas**, arriba del todo | `README.md` | ~15 líneas | **Bajo.** Ataca **E-05** de la auditoría de uso («el README documenta el mantenimiento y no el uso»). Ojo: nada de cifras a mano — las genera `cosmos medir`/`estado` (**H11**) |
| **A-07** · P1 | **`rio-configurar.md`**, que hoy **no existe** teniendo el verbo | `galaxia/agua/` | ~12 líneas | **Bajo** si lleva `momento: mantenimiento` (solo el nombre en el catálogo, coste ≈ 3 tok). Obliga a tocar `tests/test_rio_momento.py`, que lleva la lista **a mano a propósito** |
| **A-08** · P2 | `arrancar`/`compilar` **callados por defecto**: una línea de resumen; las 247 rutas, tras `--detalle`, y **relativas** | `cosmos/compilar.py`, `cosmos/cli.py` | ~20 líneas | **Bajo.** Es **E-03**: el primer comando del README cuesta ~9.900 tokens y el modo «no cambió nada» cuesta lo mismo que el modo «creé 247». En un proyecto sobre frugalidad de contexto, es el hallazgo más barato de arreglar |
| **A-09** · P2 | `estado --maquina` avisa si el **shim `~/.local/bin/cosmos` apunta a un clon que ya no existe** | `cosmos/estado.py` | ~8 líneas | **Bajo.** Es el límite declarado del §2.7: si no se vigila, un `cosmos abrir` en un repo proyectado falla sin explicar por qué |
| **A-10** · P2 | Que `~/.cosmos/` entero se cree con `700` y se **compruebe** en cada escritura (hoy `escribir_privado` hace `chmod 0o700` del padre, pero `~/.cosmos/logs/` y `~/.cosmos/bin/` los crearían §2 y §3) | `cosmos/configurar.py:96` | ~5 líneas | **Bajo.** `oceano/secretos` y `mar/custodia` mandan aquí; que un log de modelos quede en 755 sería incoherente con el resto |

### Detalle de las tres que más se pueden torcer

**A-01 — la pregunta, con su trampa.** El alta se ejecuta a menudo con banderas (`--oficios web
--herramientas …`) desde un script. En ese modo **no puede** preguntar por permisos ni escribirlos:
tocar el `settings.json` de usuario sin que nadie lo pida es exactamente lo que
`spec/GUARDARRAILES.md` llama «un sistema que se engancha sin que se lo pidan», y se arranca de raíz
a la primera molestia. Regla: **interactivo pregunta con defecto `auto`; no interactivo no toca nada
salvo `--autonomia <grado>` explícito.**

**A-03 — `estado --maquina`, forma exacta de la salida.** El valor está en que se pueda pegar en un
informe sin interpretarlo:

```
COSMOS  estado  maquina

  python3 ............ ok            3.14.3  (>= 3.11 exigido por tomllib)
  git ................ ok            2.51.0
  claude ............. ok            2.1.260
  tmux ............... falta         opcional; solo para el pueblo de consola interactiva
  llavero ............ no_comprobado  `security` existe; no se prueba una escritura sin permiso
  perfil ............. ok            ~/.cosmos/perfil.toml  (2 oficios, 7 herramientas)
  credenciales ....... falta         3 de 7 vacias   -> cosmos configurar --comprobar
  autonomia .......... auto          ~/.claude/settings.json  permissions.defaultMode
  modelos ............ falta         vigilante no instalado  -> cosmos configurar --modelos instalar
```

`no_comprobado` no es un fallo del comando: es la respuesta honesta. Un `ok` en el llavero por haber
encontrado el binario sería la bandera de seguridad que mide una ausencia.

**A-05 — por qué `git clone && python3 -m cosmos instalar` y no `curl | bash`.** Tres razones del
propio repo, no de estilo: (1) `GOAL.md` §5 prohíbe red en el camino crítico y un `curl | bash`
**es** el camino crítico; (2) `puente/secretos.py` y el gate existen para que nada entre sin pasar
por el índice, y una tubería a shell salta el gate entero; (3) el usuario no puede leer lo que va a
correr. Con `git clone` primero, lo que se ejecuta está en disco y auditado.

---

## 5. Lista de coherencia: cada fichero existente que habría que tocar, y por qué

Si una de estas líneas no se hace, algo del repo pasa a decir algo distinto de otra cosa del repo —
que es como empiezan los verdes que mienten.

### 5.1 Por la carta de autonomía (§1)

| Fichero | Qué hay que hacer | Si no se hace |
|---|---|---|
| `galaxia/agua/oceano-irreversible.md` | **Se renombra** a `oceano-autonomia.md` con el cuerpo de §1.3 (`git mv` + edición incremental, **nunca** borrar y reescribir de memoria — `development.md` §7) | — |
| `galaxia/COSMOS.md` | **Se regenera** con `cosmos generar`. **Nunca a mano**: E15 lo caza y G03 deniega la escritura | E15 en rojo |
| `PROGRESS.md` | Se regenera: sus cifras las produce `cosmos estado`, y las líneas `3. 77 tok oceano/irreversible` y `oceano 5` se quedan mintiendo | `tests/test_progress_generado.py` en rojo |
| `tests/test_cifras_de_las_specs.py` | Comprobar la línea `cardinales()` («… y **5** oceanos siempre presentes»). Con la fusión sigue siendo 5, así que **no debería cambiar**: si cambia, es que se añadió un océano y hay que revisar E16 | Verde falso o rojo sin explicación |
| `tests/test_agua_normativa.py` | Revisar si nombra `irreversible` | Rojo por un nombre que ya no existe |
| `spec/UNIVERSO.md` | **No se toca.** No cambian los 22 oficios ni los 6 mares | — |
| `spec/GUARDARRAILES.md` | Añadir una línea a «Lo que NO se trae»: la carta **no** convierte a COSMOS en un sistema que decide permisos por el runtime; eso es el §2 y es explícito | El lector cree que el océano apaga los diálogos |
| `registro/commits/universo/2026/09/` | Entrada nueva de commit (es el formato del repo, `spec/REGISTRO.md`) | El registro deja de contar lo que pasó |

### 5.2 Por el mecanismo (§2)

| Fichero | Qué hay que hacer |
|---|---|
| `cosmos/configurar.py` | `ajustes_usuario()`, `podar_autonomia()`, `escribir_autonomia()`, `leer_grado()`. Reutilizar `escribir_privado()` para el respaldo |
| `cosmos/cli.py` | `--autonomia {auto,libre,manual}` (y sin valor = solo informa), `--lanzador`, y su `help=`. **Los tres flags de `proyectar iniciar` siguen sin `help=`** (E-04): mismo viaje, mismo arreglo |
| `puente/sesion.py` | G01 amplía su mensaje con la comprobación de coherencia (§2.6), trivalente |
| `spec/GUARDARRAILES.md` | Documentar la ampliación de G01 en la tabla de los cinco mecanismos y en «Verificación exigida» (el caso vecino que **no** debe disparar) |
| `galaxia/agua/rio-configurar.md` | **Nuevo** (A-07), con `momento: mantenimiento`, `invoca: python3 -m cosmos configurar`, y la tabla de modelos de §3.3 |
| `tests/test_rio_momento.py` | Añadir `configurar` a la lista escrita **a mano** de ríos de mantenimiento |
| `tests/test_configurar.py` | Los 6 tests de §2.8 |
| `tests/test_guardarrailes.py` | Los 3 tests de G01 de §2.8 |
| `puente/tests/mutaciones.py` | La mutación de `podar_autonomia` |
| `README.md` | Sección «Instalar en un Mac nuevo» (A-06) y una línea en «El alta» diciendo que `configurar` también fija el modo de la máquina |
| `.gitignore` | **Nada.** `~/.cosmos/autonomia.json` vive fuera del repositorio, como `perfil.toml`. Pero conviene añadir `autonomia.json` a la lista defensiva junto a `perfil.toml`, por si alguien lo copia dentro |
| `secretos-conocidos.txt` | **Nada**, y es una comprobación que hay que hacer: el respaldo guarda los **bytes del `settings.json` de usuario**, que puede contener `apiKeyHelper` o un token. Vive fuera del repo y con 600 — pero si alguien lo pega en un informe, el escáner tiene que **saltar**, no indultarlo |
| `docs/credenciales.plantilla.txt` | **Nada.** El modo de permisos no es una credencial |

### 5.3 Por `claude-modelos` (§3)

| Fichero | Qué hay que hacer |
|---|---|
| `puente/modelos.py` | **Nuevo** (§3.2) |
| `puente/__init__.py` | **No importar** `modelos` ahí. La regla «nada se instala al importar» se rompe también importando de más |
| `cosmos/cli.py` | `--modelos {instalar,estado,quitar}`, `--forzar`, y que `--seco` valga también aquí |
| `cosmos/configurar.py` | `perfil_toml()` debe **conservar** una tabla `[modelos]` existente al reescribir el perfil (§3.2) |
| `cosmos/estado.py` | Filas de A-03: vigilante, copia de arranque, configs vigilados |
| `galaxia/agua/rio-configurar.md` | La tabla de los cuatro modelos vive ahí y un test la compara con `MODELOS` |
| `tests/test_modelos.py` | **Nuevo**: los 12 tests de §3.7 |
| `puente/tests/mutaciones.py` | Las tres mutaciones de §3.7 |
| `README.md` | Una fila en la tabla de enganches: «modelos — al arrancar el Mac y cuando el CLI pisa su config — `cosmos configurar --modelos instalar`». Y decir que es **solo macOS** |
| `spec/GUARDARRAILES.md` | El vigilante **no es** un cuarto enganche de COSMOS (no valida nada): se nombra donde toca y se dice que no participa del veredicto |
| `.gitignore` | Nada nuevo: todo lo del vigilante vive en `~/.cosmos/` y `~/Library/`. **Comprobar** que un `cosmos.toml` de otro repo no acaba copiando `~/.cosmos/bin/` dentro |
| `secretos-conocidos.txt` | Nada. Pero el test `test_plist_sin_rutas_ajenas` es el que impide que una ruta de máquina entre en el árbol, que es el problema del que venimos |
| `progress/` | El repo original `claude-modelos` **no se importa como directorio**: se reescribe genérico. `GOAL.md` §5: *«Cero skills de negocio importadas tal cual. Si un patrón vale, se reescribe genérico»* |

### 5.4 Orden de ejecución recomendado (P0 → P2)

1. **P0** · §1 la carta (fusión del océano) + `cosmos generar` + `PROGRESS.md` + tests de cifras.
   Es lo único que toca el presupuesto: se hace primero y se mide (`cosmos medir` tiene que seguir
   diciendo OK, con ~67 tokens de holgura).
2. **P0** · §2 el mecanismo (`--autonomia`) + G01 coherente + sus 9 tests + `rio-configurar.md`.
3. **P0** · A-03 `estado --maquina` (es lo que hace verificable todo lo anterior en un Mac nuevo).
4. **P1** · §3 `claude-modelos` dentro (`puente/modelos.py`, `--modelos`, 12 tests + 3 mutaciones).
5. **P1** · A-05 `cosmos instalar` + A-06 README «Instalar en un Mac nuevo» + A-04 + §2.7 el shim.
6. **P2** · A-08 (`arrancar` callado), A-09, A-10.

Y el cierre que exige el propio repo: `python3 -m unittest discover -s tests -t .`,
`… -s puente/tests -t .`, `python3 -m puente.tests.mutaciones`, `python3 -m cosmos validar` y
`python3 -m cosmos medir`, **pegando la salida**. Con el intérprete nombrado, nunca `python` a secas
(`development.md` §5).

---

## Anexo · Lo que NO he podido verificar, dicho aparte

1. **Que el evento `SessionStart` traiga `permission_mode`.** La cadena está en el binario 2.1.260
   (55 apariciones) y la doc de hooks la lista como campo común, pero avisa de que *«not all events
   receive this field»*. No he disparado un `SessionStart` real para verlo. Por eso el §2.6 es
   trivalente: si no viene, dice `desconocido`.
2. **Que `skipDangerousModePermissionPrompt` sea exactamente la aceptación del diálogo.** Verificado
   que la clave existe en el binario y que está a `true` en un `settings.json` de usuario donde el
   diálogo ya se aceptó. **No** he probado a borrarla y relanzar para ver reaparecer el diálogo: eso
   requiere una máquina que se pueda dejar sucia. Marcado `UNVERIFIED-DOC`.
3. **Que `launchd` ignore sin error un `WatchPaths` inexistente.** Lo afirma el README de
   `claude-modelos`; no lo he reproducido. En el diseño da igual: `StartInterval 300` cubre el caso,
   y `--modelos estado` enseña la última ejecución.
4. **Los ids de la familia Claude 5** (`claude-fable-5-1`, `claude-opus-5`, `claude-sonnet-5`,
   `claude-haiku-4-5-20251001`) vienen del encargo, no de una llamada. Lo único medido aquí es que
   `modelAccessCache` está **vacío** y por tanto **no** sirve para comprobarlos offline (§3.3).
