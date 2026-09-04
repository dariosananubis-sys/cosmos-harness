# COSMOS

Organización jerárquica de contexto para agentes de código.

## El problema

Un harness de agente empieza con un `CLAUDE.md` de veinte líneas y a los seis meses inyecta 27.000
tokens antes de que nadie haya escrito una instrucción. Nadie decidió eso. Pasó.

Pasa porque cada pieza, por separado, tenía razón: esa regla **sí** era importante, esa skill **sí**
había que documentarla, ese aviso **sí** evitó un problema real una vez. El coste de cada decisión
es invisible y el de la suma es enorme, así que la suma no la para nadie.

## El principio

> **No se le pide al agente que gaste menos. Se elimina la razón para gastar de más.**

La respuesta habitual a un harness gordo es escribir reglas pidiendo mesura: «sé breve», «no leas
ficheros enteros», «usa pocas herramientas». Son **exhortaciones**: dependen de que el modelo se
acuerde en el turno 40, y no se acuerda. Peor: ocupan sitio, así que la cura engorda la enfermedad.

COSMOS es estructural. En cada nivel, lo que no toca todavía **no está cargado** — no hay nada de
más que leer, ni que resumir, ni que ignorar. La frugalidad no se pide: es una propiedad de la
forma. Y lo que es propiedad de la forma no se olvida en el turno 40.

## La taxonomía

**Lo sólido contiene.** Todo está dentro de otra cosa, sin excepción:

```
galaxia > sistema solar > planeta > continente > pais > provincia > pueblo
```

Con dos adjuntos: la **estrella** que ilumina un sólido (su contexto permanente) y la **luna** que
orbita un planeta (su subagente).

**El agua atraviesa.** No contiene a nadie, moja a varios:

```
oceano (todo) > mar (un sistema) > lago (acotado)
rio (un comando)   lluvia (memoria)
```

El agua nunca define jerarquía. Un lago no es menos importante que un océano: **moja menos
superficie**. Confundir alcance con importancia es como un harness llega a 27.000 tokens de prólogo,
un párrafo global bienintencionado cada vez.

## Instalar en un Mac nuevo

Diez líneas, sin `curl | bash`: lo que se ejecuta está en disco y ha pasado por el índice, el
escáner de secretos y el gate. Hace falta `python3` 3.11 o posterior y `git`; nada más.

```
git clone <repo> ~/cosmos && cd ~/cosmos
python3 -m cosmos instalar --autonomia auto --modelos --lanzador
#   1/4 arrancar: compila la vista plana y valida el clon
#   2/4 configurar: pregunta oficios y herramientas, abre ~/.cosmos/credenciales.txt para rellenarlo
#   3/4 la máquina: el runtime deja de pedir permiso (ajustes de usuario), todos los modelos en /model,
#       y `cosmos` en el PATH
#   4/4 estado --maquina: qué hay y qué falta, trivalente (ok / falta / no_comprobado)
python3 -m cosmos configurar --comprobar     # cuando el fichero de credenciales esté relleno
python3 -m cosmos enganchar --sesion         # el gate en cada commit y los guardarraíles de sesión
```

Cada pieza se deshace con el mismo verbo (`--autonomia manual`, `--modelos quitar`, `--lanzador
quitar`, `desenganchar`) devolviendo cada fichero byte a byte cuando nadie más lo tocó. `--seco` lo
cuenta sin escribir. Lo que el agente lee al abrir el harness es el océano `autonomia`: se ejecuta
sin pedir permiso, inicia sesión donde haga falta con las credenciales del alta, y solo lo que no
tiene vuelta atrás espera un sí.

## Cómo se usa

Tres verbos, y el tercero es tu terminal. Nada que adivinar: cada salida dice qué hacer después.

```
python3 -m cosmos buscar montar un bot de trading      # encuentra el nodo por intención; cuesta lo que ocupa su salida, no el árbol
python3 -m cosmos abrir trading/bots/codigo-de-bot     # carga ESE nodo: cuerpo, estrella y por dónde seguir
python3 -m cosmos abrir toxiproxy                      # una herramienta: URL, licencia, instalación, uso, límites
```

`buscar` es BM25 léxico sobre las mismas líneas que el agente tiene delante (no es un agente:
`cosmos acertar` mide cuántas veces lleva a la herramienta correcta, y publica la cifra con su `n`
y su intervalo o dice por qué no la publica). `abrir` nombra a los hijos y no los describe, salvo
los de la última planta; `usa:` se lista solo por nombre. `cosmos estado` es el inventario y
`cosmos mapa` el volcado entero — caro: cuesta más que el recorrido guiado, y lo dice.

## Arranque

La vista plana es un **artefacto generado** y no se versiona, así que un clon recién bajado la tiene
ausente y E19 lo canta. Un comando lo resuelve:

```
git clone <repo> && cd cosmos
python3 -m cosmos arrancar        # compila la vista y valida; deja el clon en verde
python3 -m cosmos enganchar       # instala el gate de pre-commit y el pre-push (opcional, muy recomendable)
```

(`cosmos instalar` lo encadena con el alta; esto es el paso suelto.)

Sobre un directorio vacío con su `cosmos.toml`, `arrancar` escribe además la galaxia mínima y el
índice, que son los dos artefactos que un árbol nuevo no tiene, y se queda en verde. Un sistema
solar cuelga de la galaxia con `padre: ""` y su nombre no aparece en las rutas de sus hijos
(`spec/FRONTMATTER.md`, `spec/NUCLEO.md` §1).

## El alta: `cosmos configurar`

Lo primero al instalar COSMOS en una máquina. Pregunta qué **oficios** usas de verdad (los demás
duermen), qué **herramientas** de cada uno, y deja listo el fichero de credenciales con las
variables que esas herramientas piden, vacías y con la pista de dónde se saca cada una:

```
python3 -m cosmos configurar                 # pregunta; o --oficios trading,web --herramientas ccxt,toxiproxy
#   se abre ~/.cosmos/credenciales.txt: rellénalo de una sentada
python3 -m cosmos configurar --comprobar     # dice qué falta o parece un marcador, y se lo queda
python3 -m cosmos configurar --llavero       # al llavero de macOS y el txt se vacía
```

Perfil y credenciales viven **fuera del repositorio** (`~/.cosmos/`, directorio 700, ficheros 600).
En el repo solo hay la plantilla vacía (`docs/credenciales.plantilla.txt`); `.gitignore` y el
escáner de secretos impiden que `credenciales*.txt` o `perfil.toml` se versionen. Con el perfil
puesto, `cosmos medir` y la vista compilada solo llevan tus oficios y tus herramientas; el juez
del presupuesto (E16) sigue mirando el peor nicho entero, porque el techo vale para cualquiera.

El alta tiene tres caras más, **de máquina** y no de proyecto: el runtime solo acepta el modo de
permisos desde sus ajustes de usuario (desde el `.claude/settings.json` de un repositorio lo ignora
en silencio), así que un `enganchar --libre` sería un verde que miente.

```
python3 -m cosmos configurar --autonomia            # en qué grado arranca esta máquina; no toca nada
python3 -m cosmos configurar --autonomia auto       # sin preguntas, con el clasificador del runtime detrás (recomendado)
python3 -m cosmos configurar --autonomia libre      # bypassPermissions + aceptación del diálogo; ojo: apaga también el clasificador
python3 -m cosmos configurar --autonomia manual     # deshace: el fichero vuelve byte a byte
python3 -m cosmos configurar --modelos instalar     # todos los modelos de la cuenta en /model, para siempre (macOS: agente launchd + hook)
python3 -m cosmos configurar --modelos estado       # qué hay; el acceso de la cuenta a cada id se declara no_comprobado (hace falta red)
python3 -m cosmos configurar --lanzador             # ~/.local/bin/cosmos apuntando a este clon
python3 -m cosmos estado --maquina                  # el inventario de la máquina, trivalente
```

`--autonomia` es lo que hace verdadera la promesa del océano `autonomia`: G01 avisa en cada arranque
si la carta promete libertad y los ajustes de usuario arrancan en manual (y dice `desconocido`
cuando no puede leerlos: el evento de arranque no trae el modo). La lista de modelos vive en un solo
sitio, `puente/modelos.py`, y un test la compara con este README y con el río `configurar`:
Fable 5.1 (`claude-fable-5-1`), Opus 5 (`claude-opus-5`), Sonnet 5 (`claude-sonnet-5`), Haiku 4.5
(`claude-haiku-4-5-20251001`) y las variantes de ventana de un millón `claude-fable-5-1[1m]`,
`claude-opus-5[1m]` y `claude-sonnet-5[1m]`. Los atajos `maxcode` (Opus 5 + `--effort max`) y
`ultracode` (Opus 5 + `--effort ultracode`) se instalan con el vigilante; no se suman, son puntos
distintos de la misma escala.

## Montarlo sobre tu proyecto

Es la frase de portada del `GOAL.md` y tiene un verbo: `proyectar`. Lleva los oficios elegidos a un
repositorio Git ajeno sin pisar nada suyo.

```
python3 -m cosmos proyectar iniciar /ruta/al/repo --nicho trading    # escribe planeta.toml
#   edita planeta.toml: nichos, objetivo, rutas de escritura, comandos de verificación
python3 -m cosmos proyectar sincronizar /ruta/al/repo                # inyecta el bloque y las skills
python3 -m cosmos proyectar comprobar /ruta/al/repo                  # rojo si algo se desincronizó
```

Lo que escribe en el repo ajeno: un bloque entre `<!-- cosmos:inicio -->` y `<!-- cosmos:fin -->`
en su `CLAUDE.md` y `AGENTS.md` (índice, océanos, catálogo del nicho, contrato; lo de fuera de las
marcas no se toca), y los pueblos de esos nichos como **skills nativas** en `.claude/skills/` y
`.agents/skills/`, con `name:` y `description:` para que el agente anfitrión las descubra. La carga
perezosa allí es la del anfitrión: nombre y descripción en el prompt, cuerpo al invocar. Los verbos
de COSMOS no viajan; el bloque lo dice y explica cómo bajar por otro oficio. `comprobar` verifica el
contrato del anfitrión (que las vea), no solo el de COSMOS consigo mismo.

### Organizar un arnés que ya existe

Si el repositorio ya tiene sus skills, sus reglas, sus agentes y sus comandos, COSMOS no los reescribe:
**cada fichero del runtime pasa a ser un nodo** (el fichero original más las claves de COSMOS,
declarado con `anfitrion: claude-code`) y `cosmos compilar` vuelve a generar `.claude/skills`,
`.claude/rules`, `.claude/agents` y `.claude/commands` quitando solo esas claves. El resultado es el
fichero original byte a byte —`git diff` sobre `.claude/` tras compilar da vacío—, y desde entonces la
fuente es el árbol: `validar` lo comprueba (E22), `medir` cuenta lo que cuesta de verdad y `buscar`
lo encuentra. La memoria del anfitrión (`memory/`) no se mueve: `cosmos memoria` la indexa donde está.

```
[compilacion]
destino = ".claude/skills"    # copia, y solo los pueblos del anfitrión (vista = "anfitrion")
modo = "copia"
vista = "anfitrion"
rules = ".claude/rules"
agentes = ".claude/agents"
comandos = ".claude/commands"

[raiz]
memoria = "memory"
```

`arrancar` construye la vista y vuelve a validar el árbol entero. **No** regenera el índice: si el
índice miente, sale en rojo y te manda a `cosmos generar`. Un bootstrap que repara en silencio lo
que el validador debería denunciar no es un bootstrap, es un encubrimiento.

`cosmos.toml` apunta al árbol real (`galaxia/`). El árbol de juguete tiene su propia configuración
en `ejemplo.toml`: `python3 -m cosmos arrancar --config ejemplo.toml`.

## Cómo se sostiene

Cuatro piezas que comprueban, y cuatro enganches que las ejecutan sin que nadie se acuerde:

| Pieza | Qué hace |
|---|---|
| `cosmos validar` | E00–E22. Esquema, estructura, duplicación, presupuesto, artefactos sincronizados, el contrato de cada pueblo y el runtime generado |
| `cosmos medir` | Cuánto contexto se paga por existir, antes del primer turno. Con el método declarado: si es estimado, dice **estimado** |
| `cosmos generar` | El índice de la galaxia se **genera**. Nunca se edita a mano, así que no puede desincronizarse ni mentir |
| `cosmos compilar` | Aplana los pueblos en symlinks relativos o copias, con lock y manifiesto atómico |

| Enganche | Cuándo corre | Se instala con |
|---|---|---|
| pre-commit | Antes de cada commit, sobre la **instantánea del índice** (no sobre lo que haya sucio en disco): validar, las dos suites, secretos y los canarios `P01`/`P02` | `cosmos enganchar` |
| pre-push | Antes de cada push: el escáner de secretos sobre todo lo versionado, la última puerta local antes de que algo salga del disco | `cosmos enganchar` |
| **sesión** | Mientras un agente trabaja: cinco guardarraíles que avisan, protegen lo generado y tapan secretos antes de que lleguen al modelo | `cosmos enganchar --sesion` |
| CI | En cada push y cada PR, en Linux y macOS y con el Python mínimo (3.11): todo lo anterior más las mutaciones y la calibración | ya está en `.github/workflows/cosmos.yml` |

(`cosmos arrancar` no es un enganche: es lo primero que se ejecuta tras clonar, porque la vista
plana es un artefacto generado y no viaja en el repositorio.)

`cosmos enganchar` es explícito y reversible: dice qué escribió y dónde, **no pisa un pre-commit
ajeno** —si lo hay, lo dice y no toca nada— y `cosmos desenganchar` lo quita dejando el repositorio
exactamente como estaba. Nada se instala solo al importar el paquete.

Un aviso se ignora; por eso pasarse de presupuesto es rojo. Un índice a mano se desincroniza; por
eso se genera. Un validador que nunca ha dicho rojo no se distingue de uno roto; por eso hay un
test por invariante que lo ve fallar a propósito. Y un validador que nadie ejecuta no se distingue
de no tenerlo; por eso hay enganches.

## La válvula de escape

Todo guardarraíl duro sin válvula acaba desactivado a la fuerza: alguien tiene una urgencia real un
viernes, el guard le estorba, y lo arranca entero. Así que COSMOS trae la suya, y usarla es más
cómodo que saltarse el sistema:

```
python3 -m cosmos saltar E16 --motivo "importando 40 skills, se reorganiza el lunes" --caduca 7d
python3 -m cosmos saltar --listar
```

| Propiedad | Regla |
|---|---|
| Acotada | Un código concreto (`E00`..`E22`), de sesión (`G01`..`G05`) o del gate (`P01`, `P02`); nunca «todo» |
| Con motivo | Obligatorio. Sin `--motivo` no hay salto |
| Caducable | Obligatorio, máximo 30 días. Sin `--caduca` no hay salto |
| Registrada | Log que solo crece en `.cosmos/saltos.log`; renovar añade línea, no reescribe |
| Visible | Con un salto vivo la salida dice `verde (1 salto activo: E16, caduca en 5 d)`, nunca «verde» a secas |
| Ruidosa al caducar | Al vencer vuelve el rojo y el mensaje recuerda el motivo que se escribió |

La palabra «verde» no aparece nunca sola habiendo saltos activos. Un verde que oculta un salto es
una mentira, y basta una para que nadie vuelva a creerse ninguna.

El registro es local y no se versiona: una urgencia de una persona no puede apagar el CI de todos.
La deuda que sí es del repositorio se inventaría aparte, en `secretos-conocidos.txt`, y ahí lo que
no está en la lista bloquea igual.

## Las pruebas

```
python3 -m unittest discover -s tests -t .          # el núcleo (unittest, no pytest: cero dependencias)
python3 -m unittest discover -s puente/tests -t .   # el puente
python3 -m puente.tests.mutaciones                  # cada invariante, vista fallar a propósito
```

Dos pruebas verifican el margen del medidor contra un tokenizador real y se saltan avisando si no lo
hay: `python3 -m venv ~/.cosmos/calib && ~/.cosmos/calib/bin/pip install -r requirements-dev.txt`, y
`COSMOS_EXIGE_TOKENIZADOR=1 ~/.cosmos/calib/bin/python -m unittest discover -s tests -t .` las
exige. El CI lo hace en cada push (`docs/CALIBRACION.md`).

## Estado

En construcción. `GOAL.md` es el contrato, `PROGRESS.md` el estado real (con pin de commit; las
cifras las genera `cosmos estado`), `reviews/` las revisiones cruzadas.

Lo escriben dos agentes en pareja —Claude las especificaciones, Codex la implementación— y **ninguno
aprueba su propio trabajo**: cada pieza la revisa el otro con premisa invertida, entrando a
demostrar que está mal y contando qué intentó.
