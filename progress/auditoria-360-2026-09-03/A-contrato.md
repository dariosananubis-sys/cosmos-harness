# Auditoría 360 de COSMOS — Revisor A: verdad del contrato

**Ángulo exclusivo:** ¿el código hace lo que las specs dicen que hace?
**Premisa de entrada:** las specs mienten sobre el código, y mi trabajo es demostrarlo.

## Pin de estado

```
git -C ~/cosmos rev-parse HEAD        -> b0c1ebdeb2d9bac7e068d10714213ff2f9eda926
git -C ~/cosmos status --porcelain|wc -> 0        (árbol limpio; rama main)
```

Todo lo de abajo se midió sobre ese commit exacto. Las referencias son **por símbolo o
sección**, nunca por `fichero:línea`, porque el árbol muta.

## Método

- Solo lectura sobre `~/cosmos`. No se editó ningún fichero del repo, no hay commits ni push.
  Lo único escrito es este informe.
- Intérprete: `/usr/local/bin/python3`, **Python 3.14.3**. No hay venv en el repo y el proyecto
  es de biblioteca estándar por diseño (`spec/VALIDADOR.md`, «offline y sin dependencias»), así
  que `python3` es el intérprete correcto aquí. Todo comando publicado se copia y pega desde
  `~/cosmos`.
- **Aviso de shell**: el shell del arnés es `zsh` y no hace word-splitting. Los bucles sobre
  listas en variable de este informe van dentro de `bash <<'EOF' … EOF`. Ejecutar
  `for c in "cosmos estado" …; do python3 -m $c; done` en zsh devuelve `exit=1` en las 13
  entradas y parece que ningún río funciona; en bash devuelve `exit=0` en las 13. Me pasó
  durante esta auditoría y estuvo a punto de convertirse en un hallazgo falso.
- Nada de red, nada de dinero, ningún buzón de correo abierto.

## Alcance cubierto, con conteos

| Qué | Cobertura |
|---|---|
| `spec/` | **11 de 11** ficheros leídos enteros (COMPILACION, COMPOSICION, FRONTMATTER, GUARDARRAILES, MEDIDOR, NUCLEO, PUEBLO, REGISTRO, TAXONOMIA, UNIVERSO, VALIDADOR) |
| Contrato de cabecera | `GOAL.md` y `README.md` enteros |
| Árbol real | **416 nodos** (404 en `galaxia/` + 12 `lluvia` en `registro/`), **500 ficheros** en `galaxia/` |
| Pueblos | **247 de 247** medidos contra el contrato de `spec/PUEBLO.md`, por conteo, no por muestreo |
| Ríos | **17 de 17** ejecutados |
| Invariantes | **20 vivas** (E00–E03, E05–E20) contrastadas contra lo que documenta `spec/VALIDADOR.md` |
| Suite | `Ran 259 tests in 104.498s — OK (skipped=2)`, exit 0 |
| Comandos ejecutados | `validar`, `medir`, `medir --metodo exacto`, `estado`, `compilar --seco`, `compilar --nicho web --seco`, `arrancar`, `saltar` (6 variantes), `mapa`, `abrir`, `buscar`, `acertar`, `generar`, `enganchar`, `desenganchar`, `puente.{gate,lluvia,proyectar,secretos}` |

Baseline sano antes de empezar, para que no se confunda un hallazgo con un rojo preexistente:

```bash
cd ~/cosmos && python3 -m cosmos validar
# COSMOS  verde  0 errores        (exit 0)
```

---

# Hallazgos

## A-01 · CRÍTICO · El índice generado —el artefacto que «no puede mentir»— miente en la primera línea que se paga

`README.md` («Cómo se sostiene») y `spec/VALIDADOR.md` (sección *Sobre `E15`*) apoyan el sistema
entero en esta promesa:

> «El índice de la galaxia se **genera**. Nunca se edita a mano, así que no puede desincronizarse
> ni mentir» · «Con ella, el índice **no puede** mentir, y esa es la razón de que el índice pueda
> estar permanentemente en contexto sin que nadie tenga que confiar en él.»

El índice está sincronizado (E15 verde) y **aun así es falso**, porque lo que se genera es la
copia literal del cuerpo y el resumen del nodo galaxia, y ese resumen lleva un número a mano.

```bash
cd ~/cosmos && sed -n '3p' galaxia/COSMOS.md
# Veintiun oficios, seis mares que los cruzan y cinco oceanos siempre presentes; nada se carga hasta entrar en ello.

cd ~/cosmos && python3 -m cosmos estado | sed -n '/sistema-solar/p'
#     sistema-solar      22
```

Origen: el campo `resumen:` del nodo `galaxia` (fichero `galaxia/galaxia.md`). «seis mares» y
«cinco oceanos» sí cuadran (6 y 5, medidos); **«Veintiun oficios» no**: son 22.

**Por qué es el peor sitio posible donde envejecer.** Esa cadena es simultáneamente:

1. El `resumen` de la galaxia, es decir **la primera línea del contexto de entrada de toda sesión
   y de todo subagente**, para siempre. `spec/FRONTMATTER.md` lo dice de sí mismo: «`resumen` es
   el campo más importante del sistema… es coste fijo permanente».
2. Contenido del **único artefacto que el repo declara incapaz de mentir**. E15 solo compara disco
   contra regeneración: si la fuente lleva el número a mano, E15 lo certifica en verde para siempre.
3. Exactamente lo que `GOAL.md` §1 prohíbe: «Un número copiado a mano en una spec envejece en
   silencio y acaba mintiendo — ya pasó una vez (hallazgo H11)».

**Y hay canario para todo lo de al lado, menos para esto.** El repo sabe perfectamente que este
número envejece:

- `puente/tests/mutaciones.py` tiene la mutación **M52**, que cambia `# El universo — 22 oficios`
  por `21 oficios` en `spec/UNIVERSO.md` y exige que
  `tests.test_universo_navegable.ElCardinalDelTituloEsElDelDisco` la mate.
- `tests/test_spec_al_dia.py` incluso trae un diccionario `cardinales` (`"Tres": 3 … "Diez": 10`)
  para vigilar la frase «Seis aguas que mojan» — prueba de que saben que **los cardinales escritos
  con letra también envejecen**.

El cardinal en letra del índice quedó fuera de los dos. `tests/test_cifras_de_las_specs.py` vigila
4 cifras, todas con el patrón `(\d+)`: un `Veintiun` no lo cruza ninguna.

**Fix.** Generar ese tramo en vez de escribirlo: que `cosmos generar` componga la cabecera del
índice contando el árbol (`len([n for n in arbol.nodos if n.cosmos == "sistema-solar"])`), y dejar
en `galaxia/galaxia.md` un resumen sin cifras. Si se prefiere conservar la redacción a mano, añadir
al registro de `tests/test_cifras_de_las_specs.py` una `Cifra` sobre `galaxia/galaxia.md` con
mapeo de cardinal en letra, reutilizando el diccionario que ya existe en `test_spec_al_dia.py`.

**Riesgo si no se toca.** Es el fallo más caro del catálogo: cada sesión y cada subagente leen un
dato falso sobre el tamaño del sistema, y el mecanismo que existe para impedirlo (E15) lo firma en
verde. Es H11 reencarnado dentro de la defensa contra H11.

---

## A-02 · CRÍTICO · «Coste en runtime: Cero» es falso, y el comando de arranque documentado materializa el peor caso

`spec/COMPILACION.md`, en la tabla que **decide la arquitectura** (opción A frente a router MCP),
publica esta fila:

| | Opción A — compilar a plano | Opción B — router MCP |
|---|---|---|
| Coste en runtime | **Cero.** Es un artefacto en disco | Un servidor vivo **y sus tools en el contexto de cada sesión** |

Y el argumento decisivo, literal: la opción B «**inyecta sus definiciones de herramientas en el
contexto de todas las sesiones, siempre**… Sería construir la fuga dentro de la herramienta que
existe para eliminarla».

**La vista plana funciona por el mismo mecanismo.** Su propósito declarado, en la misma spec, es
que «Claude Code solo escanea el nivel superior de `~/.claude/skills/`» y por eso hay que aplanar
ahí. Un runtime que descubre skills escaneando un directorio inyecta **nombre + descripción de cada
skill de nivel superior** en el prompt de cada sesión. Eso no es «un artefacto en disco»: es
exactamente la inyección permanente por la que se descartó la opción B, solo que con otro nombre.

Medido:

```bash
cd ~/cosmos && python3 -m cosmos compilar --seco | grep -cE "^(CREAR|IGUAL|ACTUALIZAR)"
# 247
cd ~/cosmos && python3 -m cosmos compilar --nicho web --seco | grep -cE "^(CREAR|IGUAL|ACTUALIZAR)"
# 17
cd ~/cosmos && ls .cosmos/vista-galaxia | wc -l
# 247        <- lo que hay materializado hoy en disco
```

```bash
cd ~/cosmos && python3 - <<'PY'
from pathlib import Path
from cosmos.modelo import cargar_arbol, cargar_configuracion
from cosmos.medir import contar_aprox
cfg = cargar_configuracion(Path("cosmos.toml"))
arbol = cargar_arbol(cfg.arbol, tambien=(cfg.registro,) if cfg.registro else ())
pu = [n for n in arbol.nodos if n.cosmos == "pueblo"]
print("pueblos:", len(pu))
print("nombre+resumen de los 247:",
      contar_aprox("\n".join(f"{n.nombre}: {n.datos.get('resumen','')}" for n in pu)), "tokens")
PY
# pueblos: 247
# nombre+resumen de los 247: 6167 tokens
```

**6.167 tokens.** Comparados con lo que el propio sistema publica:

| Magnitud | Tokens |
|---|---:|
| Presupuesto (`[presupuesto] entrada`) | 4.000 |
| Entrada base publicada por `cosmos medir` | 1.343 |
| Peor nicho + agua (el número que E16 vigila) | 3.546 |
| **Vista plana completa que construye `arrancar`** | **6.167** |

Es **1,5 × el presupuesto entero** y **2,6 × el peor nicho** que E16 pone en rojo. Ninguna magnitud
del medidor lo ve: `spec/MEDIDOR.md` lo manda entero al saco `Fuera de COSMOS … no_medido`.

**Y no es una vista de laboratorio: la construye el primer comando que el README manda ejecutar.**
`README.md` §Arranque dice `python3 -m cosmos arrancar`. En `cosmos/cli.py`, `_arrancar` llama a
`_compilar` con `args.nicho` sin fijar, que resuelve a `config.nichos`, que con el `cosmos.toml`
versionado es `None` → compilación completa, 247 entradas. El `--nicho` que acota la vista
**nunca aparece en el camino documentado**.

**Segunda mitad, y es igual de grave por el lado contrario.** El `destino` de la galaxia en
`cosmos.toml` es `.cosmos/vista-galaxia`, un directorio privado que **ningún runtime escanea**:

```bash
cd ~/cosmos && grep -A3 '\[compilacion\]' cosmos.toml
# destino    = ".cosmos/vista-galaxia"
cd ~/cosmos && ls .claude/skills
# probar-salida
# revisar-formato          <- son del árbol de juguete (ejemplo.toml), no de la galaxia
cd ~/cosmos && grep -rn "\.claude/skills" README.md spec/ GOAL.md cosmos.toml | wc -l
# 3      (y ninguna es una instrucción de entrega para la galaxia)
```

Así que hoy las dos lecturas son un fallo, y hay que elegir cuál se arregla:

- Si `.cosmos/vista-galaxia` **es** lo que consume el runtime → se pagan 6.167 tokens no medidos y
  la fila «Coste en runtime: Cero» es falsa.
- Si **no lo es** → la premisa entera de `COMPILACION.md` («un paso de build genera la vista plana
  que la plataforma sí descubre») está **sin realizar para el árbol real**: la galaxia compila a un
  cajón que nadie lee, y el único `destino` que apunta a `.claude/skills` es el del juguete
  (`ejemplo.toml`).

**Fix.** (a) Corregir la fila de la tabla de decisión: el coste de la opción A no es cero, es «un
`resumen` por pueblo aplanado, y por eso se aplana por nicho». La decisión A sigue ganando —17
resúmenes contra 247— pero por la razón verdadera. (b) Añadir al medidor una magnitud
`vista_compilada` que tokenice nombre+resumen de lo que hay en `destino`, y que no se pueda declarar
verde una vista de 247 entradas con un presupuesto de 4.000. (c) Que `arrancar` compile con el nicho
activo, o que se niegue a compilar la vista completa sin `--todos` explícito. (d) Documentar el
camino real desde la galaxia hasta el directorio que el runtime escanea.

**Riesgo.** Es la fuga que COSMOS existe para eliminar, construida dentro de COSMOS, y con el
argumento contrario escrito en la spec que la autoriza.

---

## A-03 · CRÍTICO · Con el `GOAL.md` de hoy, ninguna pieza del repo puede estar terminada

`GOAL.md` §7 («Definición de terminado») es taxativo, y `GOAL.md` manda sobre todo el repo («Si
algo del repo contradice este fichero, gana este fichero»):

> 2. El medidor da un número real de tokens de contexto inicial, **medido, no estimado**.

El repo está configurado para lo contrario, y no puede hacer otra cosa:

```bash
cd ~/cosmos && grep -A2 '\[medicion\]' cosmos.toml
# metodo = "aprox"

cd ~/cosmos && python3 -m cosmos medir | sed -n '3p'
#   Entrada base .... 1.343 tokens   (índice + océanos + estructura, sin pueblos; estimado, ±5%, heurística v3)

cd ~/cosmos && python3 -m cosmos medir --metodo exacto > /tmp/m.out 2>&1; echo "EXIT=$?"; head -3 /tmp/m.out
# EXIT=1
# COSMOS  medir  rojo
#
# se pidió método exacto, pero no hay tokenizador local
```

`spec/NUCLEO.md` §4 y `spec/MEDIDOR.md` fijan `aprox` como defecto **a propósito y con buen
motivo** (reproducibilidad: con `auto`, el veredicto de E16 dependía de si la máquina tenía
`tiktoken`). Ese razonamiento es correcto. Lo que no puede quedarse como está es que la definición
de terminado del contrato de cabecera exija un número «medido, no estimado» que el sistema, por
diseño y sin dependencias de pago (`GOAL.md` §5), no puede producir.

Hoy, leído al pie de la letra, **ninguna de las piezas declaradas hechas en `PROGRESS.md` cumple
`GOAL.md` §7.2**.

**Fix.** Se corrige en `GOAL.md`, que es donde manda la regla y donde el propio fichero dice que
hay que corregirla primero: sustituir §7.2 por «El medidor da un número de tokens de contexto
inicial obtenido con el método declarado en `cosmos.toml`, con su margen calibrado publicado, y
nunca un `no_medido` sumado como cero». Eso conserva la intención (nada de números inventados) sin
exigir un tokenizador que el §5 prohíbe pagar.

**Riesgo.** Una definición de terminado que nada puede cumplir se ignora entera, y con ella se van
los otros tres puntos —el validador visto fallar, la revisión cruzada, cero huérfanos— que sí se
cumplen y sí valen.

---

## A-04 · CRÍTICO · `nichos=None` significa dos cosas opuestas, en la misma spec, y el `cosmos.toml` documenta la equivocada

`spec/NUCLEO.md` es el fichero que existe para cerrar ambigüedades: «Aquí se fijan las seis
definiciones que faltaban… Cuando otra spec y este fichero discrepen, gana este». Discrepa consigo
mismo:

- §2, sobre el catálogo: «`nichos=None` significa **ningún nicho activo**: no aparece ningún pueblo».
- §5, sobre compilar: «La API conserva `nichos=None` como **compilación completa** por compatibilidad».

El mismo centinela: en un sitio **nada**, en el otro **todo**. Medido:

```bash
cd ~/cosmos && python3 - <<'PY'
from pathlib import Path
from cosmos.modelo import cargar_arbol, cargar_configuracion
from cosmos.medir import nodos_de_catalogo
cfg = cargar_configuracion(Path("cosmos.toml"))
arbol = cargar_arbol(cfg.arbol, tambien=(cfg.registro,) if cfg.registro else ())
print("cosmos.toml -> cfg.nichos =", cfg.nichos)
for etq, n in [("None", None), ("[] vacia", []), ("['web']", ["web"])]:
    nodos = nodos_de_catalogo(arbol, n)
    print(f"  nichos={etq:10s} -> catalogo={len(nodos):3d} nodos, pueblos={sum(1 for x in nodos if x.cosmos=='pueblo'):3d}")
PY
# cosmos.toml -> cfg.nichos = None
#   nichos=None       -> catalogo= 17 nodos, pueblos=  0
#   nichos=[] vacia   -> catalogo= 17 nodos, pueblos=  0
#   nichos=['web']    -> catalogo= 38 nodos, pueblos= 17
```

Contra lo que dice el `cosmos.toml` versionado, en su propio comentario:

```
# Nicho activo del runtime acotado. Lista vacía = todos los sistemas solares.
[nichos]
activos = []
```

**«Lista vacía = todos los sistemas solares» es falso para el catálogo**: da **cero** pueblos, no
todos. Es verdad solo para `compilar` (247 entradas, A-02). Un mismo valor de configuración,
documentado una vez, gobernando dos subsistemas con semánticas contrarias.

Lo que se cae con esto es la lectura del presupuesto: quien lea el comentario del `cosmos.toml`
creerá que `cosmos medir` con la configuración por defecto está midiendo los 22 nichos activos —
el peor caso absoluto—, cuando está midiendo el caso con **cero** pueblos.

**Fix.** Partir el centinela: `nichos=None` = «todos» y `nichos=()` = «ninguno», en las dos rutas,
o al revés; lo que no puede es depender del subsistema. Mientras tanto, corregir el comentario del
`cosmos.toml` para que diga las dos cosas que hace de verdad. Y añadir un test que fije la
semántica de `[]` y de `None` en `catalogo_visible` y en `compilar_arbol` a la vez — hoy cada uno
tiene sus tests por separado y por eso la divergencia no sale en rojo.

**Riesgo.** Es la clase de ambigüedad que `NUCLEO.md` §1 documenta como el hallazgo B1 de Codex
(«dos implementaciones conformes que discrepan sobre el mismo árbol»), reaparecida en el mismo
fichero que la resolvió.

---

## A-05 · ALTO · `spec/VALIDADOR.md` documenta 16 invariantes; el validador comprueba 20

El fichero se titula «Especificación del validador — para implementar» y su sección *Invariantes
(cada una es un error con su código)* es la tabla normativa. Llega hasta E16 y para.

```bash
cd ~/cosmos && python3 -c "
from cosmos.validar import codigos_comprobados, rango_comprobado
print(sorted(codigos_comprobados())); print(rango_comprobado())"
# ['E00','E01','E02','E03','E05','E06','E07','E08','E09','E10','E11','E12','E13','E14','E15','E16','E17','E18','E19','E20']
# E00–E20

cd ~/cosmos && grep -oE "E[0-9]{2}" spec/VALIDADOR.md | sort -u | tr '\n' ' '
# E01 E02 E03 E04 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E16
```

Cinco invariantes vivas fuera de la spec del validador: **E00, E17, E18, E19, E20**. Cuatro tienen
definición en otra parte (E17 en `NUCLEO.md` §10, E18 y E19 en `COMPILACION.md`, E20 en
`COMPOSICION.md` y `FRONTMATTER.md`), lo cual ya es un problema de localización.

**E00 no tiene definición normativa en ninguna spec.** Solo aparece de pasada en `FRONTMATTER.md`
(dentro de la fila de `momento`) y en `NUCLEO.md` §1 (dentro del argumento de la aciclicidad). Y es
el más ancho del validador: en `cosmos/validar.py` emite **ocho** errores distintos —campo
obligatorio ausente, campo que no es texto, `momento` inválido, `nombre` inválido, campo no
permitido para el nivel, lista mal tipada, error de sintaxis del frontmatter—.

Es agravante que el mismo repo tenga un canario para la frase vecina: `tests/test_cifras_de_las_specs.py`
vigila que `NUCLEO.md` diga «E00–E03 y E05–E20» y lo pone rojo si el rango envejece. Nadie vigila
que la tabla de invariantes esté completa.

**Fix.** Reponer en `spec/VALIDADOR.md` las cinco filas (E00, E17, E18, E19, E20), con E00 definida
por primera vez y las otras cuatro remitiendo a su spec dueña. Añadir a
`tests/test_cifras_de_las_specs.py` una prueba que compare `codigos_comprobados()` con los códigos
que aparecen en la tabla de `VALIDADOR.md`: es el mismo patrón que `test_spec_al_dia.py` ya aplica
a los mares, y aquí falta.

**Riesgo.** Quien implemente un COSMOS contra la spec produce un validador con 16 comprobaciones y
dirá que es conforme. Es literalmente el fallo que `NUCLEO.md` abre denunciando: «la especificación
no especificaba».

---

## A-06 · ALTO · `spec/PUEBLO.md` es normativo y no lo comprueba nadie: 28 de 247 pueblos no nombran lo que hay que ejecutar

`spec/PUEBLO.md` se titula «Qué tiene que traer un pueblo — **normativo**», dice «Un pueblo
responde a cuatro preguntas… **Si falta una, no está terminado**» y titula una sección «Reglas que
no se negocian», cuya regla 1 es: «**La URL es literal y verificada.** … Sin ella, el pueblo no
nombra nada y el agente que lo lea sigue sin saber qué ejecutar».

No hay ningún guardarraíl. Cero referencias en todo el código y en toda la suite:

```bash
cd ~/cosmos && grep -rln "PUEBLO.md\|spec/PUEBLO" cosmos/ tests/ .github/ ; echo "coincidencias=$?"
# (sin salida)   coincidencias=1
```

Medido sobre los **247 de 247**, no por muestreo:

```bash
cd ~/cosmos && python3 - <<'PY'
import pathlib, re
pu = []
for p in sorted(pathlib.Path("galaxia").rglob("*.md")):
    t = p.read_text(encoding="utf-8")
    if not t.startswith("---"): continue
    fm, cuerpo = t.split("---", 2)[1], t.split("---", 2)[2]
    if re.search(r"^cosmos:\s*pueblo\s*$", fm, re.M): pu.append((p, cuerpo))
n = len(pu)
chk = [("regla 1  URL http(s)",            r"https?://"),
       ("         bloque de codigo",       r"```"),
       ("         comando de instalacion", r"(brew|pip|pipx|npm|go|cargo|apt|uv tool|gem) install|docker (run|pull)"),
       ("regla 4  comparacion nombra rival", r"(Gana a|gana a|frente a|mejor que|a diferencia de)"),
       ("regla 5  apartado de avisos",     r"(Ojo|Aviso|No hace|no cubre|falso verde|Limitaci)"),
       ("regla 2  fecha de comprobacion",  r"20\d\d-\d\d-\d\d")]
print("pueblos:", n)
for etq, pat in chk:
    v = sum(1 for _, c in pu if re.search(pat, c))
    print(f"  {v:4d}/{n}  {etq}   (faltan {n-v})")
PY
# pueblos: 247
#    219/247  regla 1  URL http(s)               (faltan 28)
#    247/247           bloque de codigo          (faltan 0)
#    192/247           comando de instalacion    (faltan 55)
#    180/247  regla 4  comparacion nombra rival  (faltan 67)
#    207/247  regla 5  apartado de avisos        (faltan 40)
#    217/247  regla 2  fecha de comprobacion     (faltan 30)
```

Los 28 sin URL son, en su mayoría, herramientas propias del arnés (`captura-recortada`,
`auditar-gasto`, `codigo-al-modelo`, `correo-smtp`…). Es una categoría **legítima** que la spec
sencillamente no contempla: `PUEBLO.md` no carva ninguna excepción para «herramienta propia, no de
GitHub» —que es exactamente la frase que usa el cuerpo de `captura-recortada`—. Así que el hallazgo
es real por los dos lados: o la spec necesita esa excepción, o 28 pueblos están fuera de contrato.
Los 67 sin rival nombrado y los 55 sin comando de instalación no tienen esa defensa.

Y esto es **infracción directa del corolario 1 de `GOAL.md`**: «Si una regla tiene que recordarse,
está mal puesta: se convierte en estructura o en guardarraíl, nunca en un párrafo pidiendo buen
comportamiento». `PUEBLO.md` es hoy, íntegro, un párrafo pidiendo buen comportamiento.

**Fix.** Una invariante nueva (siguiente código libre, **E21**, porque `VALIDADOR.md` prohíbe
renumerar y reutilizar huecos) sobre `cosmos: pueblo`: exige URL **o** un campo explícito
`origen: propio`; exige bloque de código; exige rival nombrado. Con su test que la ve fallar y su
entrada en `CODIGOS_INVARIANTES` para que tenga válvula —`tests/test_cifras_de_las_specs.py`
(`TodaInvarianteVivaTieneValvula`) lo exigirá solo—. Y una `--seco`/informe que liste los 67 para
saldarlos por tandas.

**Riesgo.** `spec/UNIVERSO.md` declara el criterio 1 («**Se ejecuta**») **eliminatorio**. Hoy 28
pueblos entregan prosa donde prometen una herramienta, que es el hallazgo H05 que dio origen a este
mismo fichero, sin cerrar y ahora sin medida.

---

## A-07 · ALTO · Cifras petrificadas fuera del canario, incluidas dos que el propio canario presume de haber arreglado

`tests/test_cifras_de_las_specs.py` vigila **4** cifras. Estas cinco están escritas a mano, ninguna
vigilada, y todas falsas hoy:

| Dónde | Dice | El árbol cuenta | Comando que lo decide |
|---|---|---|---|
| `spec/COMPOSICION.md`, §`usa:` | «Los **21** sistemas solares lo hacen» | **22** | `python3 -m cosmos estado` |
| `spec/PUEBLO.md`, cabecera y bloque `0/189` | «los **189** pueblos existentes» | **247** | `python3 -m cosmos estado` |
| `spec/TAXONOMIA.md`, §retirada de `ciudad`/`casa` | «las **209** skills montadas» | **247** | `python3 -m cosmos estado` |
| `spec/MEDIDOR.md`, §«El agua no se puede quedar fuera» | «los **cinco** mares suman **817** tokens» | **6** mares, **1.163** | `python3 -m cosmos medir` |
| `spec/UNIVERSO.md`, cabecera del documento | (correcta: 22) | 22 | vigilada por la mutación M52 |

```bash
cd ~/cosmos && grep -n "21 sistemas" spec/COMPOSICION.md
# 77:Un nodo puede declarar con qué se usa habitualmente. Los 21 sistemas solares lo hacen —GOAL §1:

cd ~/cosmos && python3 -m cosmos medir | sed -n '5p'
#   Agua condicional  1.163 tokens   (6 aguas por paths:, fuera de la entrada)
```

La de `COMPOSICION.md` es la más incómoda: el docstring de
`tests/test_cifras_de_las_specs.py` presume de haber cazado *«uno de los 20 sistemas solares cuando
son 21»* — y arregló la de `REGISTRO.md`, que hoy dice 22 y está vigilada por el patrón
`uno de los (\d+) sistemas solares`. La de `COMPOSICION.md` está redactada distinto
(`Los (\d+) sistemas solares`) y se escapó del mismo barrido, en el mismo día.

Las de `MEDIDOR.md` y `PUEBLO.md` van fechadas o atribuidas a un hallazgo histórico, lo que las
hace defendibles como cita. Pero `MEDIDOR.md` cierra su propia lista de verificaciones con
*«Un test de que el rótulo cuenta lo mismo que el número: "N aguas por paths:"… Decía 5 habiendo
6»* — o sea, corrigieron el rótulo del programa y dejaron el «cinco mares» de la prosa dos
párrafos más arriba.

**Fix.** Añadir las cuatro al `REGISTRO` de `tests/test_cifras_de_las_specs.py` (la estructura
`Cifra(fichero, patron, calcular, por_que)` las admite tal cual), o sustituirlas por la remisión al
comando, que es lo que la clase `LasCifrasQueSeRetiraronSiguenRetiradas` ya hace con dos casos.

---

## A-08 · ALTO · `spec/VALIDADOR.md` describe una E16 que el código no implementa, y nombra una clave de configuración que no existe

`spec/VALIDADOR.md`, sección *Sobre `E16`*: «El validador falla si el **peor nicho individual**
supera `presupuesto_entrada` de `cosmos.toml`».

Dos cosas falsas en una frase:

1. `presupuesto_entrada` **no es una clave de `cosmos.toml`**. La clave es `entrada`, dentro de
   `[presupuesto]`.
2. E16 **no** compara el peor nicho: compara `entrada_con_agua`, como impone `NUCLEO.md` §3
   («E16 compara `entrada_con_agua` con el presupuesto, no `entrada`. El número que decide rojo o
   verde tiene que ver todo lo que se paga sin pedirlo»). El agua no aparece en la descripción de
   `VALIDADOR.md`.

Forzado a rojo bajando el presupuesto a 2.000 sobre una copia del repo:

```
E16  presupuesto
     peor nicho ciberseguridad: entrada 2383 + agua condicional 1163 = 3546 tokens > 2000;
     excede en 1546 tokens; más caros: catálogo visible (1315), índice de galaxia (555), mar/pruebas (301)
     Ejecuta 'cosmos medir --detalle' y reduce las partes más caras del nicho culpable o el cuerpo de los mares.
```

El código está bien y el mensaje es excelente (nombra nicho, exceso exacto y los tres más caros,
tal como pide la spec). **Lo que está mal es la spec**, que describe una comparación que dejaría el
32 % del gasto fuera del presupuesto — el porcentaje es el que `NUCLEO.md` §3 mide para justificar
que hubo que cambiarla.

**Fix.** Reescribir esa sección de `VALIDADOR.md` para que cite `entrada_con_agua` y la clave real
`[presupuesto] entrada`, remitiendo a `NUCLEO.md` §3 en vez de repetir la definición (que es la
regla que el propio `NUCLEO.md` fija: «ninguna se redefine en otro sitio»).

---

## A-09 · ALTO · El `README.md` enuncia el principio rector en la versión que Darío corrigió

Es la frase que ambos documentos ponen en un `>` como tesis del proyecto:

```bash
cd ~/cosmos && grep -n "Se elimina la razón para gastar" GOAL.md README.md
# GOAL.md:50:> **No se le pide al agente que gaste menos. Se elimina la razón para gastar de más.**
# README.md:16:> **No se le pide al agente que gaste menos. Se elimina la razón para gastar.**
```

El README se come **«de más»**. No es un matiz de estilo: es exactamente la distinción que
`GOAL.md` §2 dedica tres párrafos a defender, citando la corrección literal de Darío del
2026-09-02 —*«yo no te dije que se centre en mínimo coste, sino que no hubiese costes innecesarios,
que es distinto»*— y explicando que «si la métrica es el mínimo, el óptimo perfecto es un harness
vacío».

«Eliminar la razón para gastar» **es** la formulación de coste mínimo. El documento público del
repo enuncia la versión pre-corrección de su propia tesis, y es el único que la mayoría de la gente
leerá. `GOAL.md` §0 zanja quién gana: «Si algo del repo contradice este fichero, gana este fichero».

Colateral menor del mismo par: `GOAL.md` habla de «30k tokens de prólogo» (dos veces) y el README y
otras dos specs, de «27.000 tokens» (cuatro veces). Es retórica, no medición, pero conviene una
sola cifra.

**Fix.** Dos palabras en el README. Y una prueba de una línea en `tests/test_cifras_de_las_specs.py`
que exija que la frase del `>` del README sea carácter a carácter la del `>` de `GOAL.md`: es el
enunciado más copiado del repo y el más fácil de parafrasear al reescribir.

---

## A-10 · MEDIO · El medidor publica ±5 % sobre una heurística cuyo peor caso calibrado es 33,6 %, que no publica en ninguna parte

`spec/MEDIDOR.md` es tajante: «El error medido se publica en `docs/CALIBRACION.md` con la fecha y
el corpus, y el medidor lo cita en su salida… **Un margen de error inventado es peor que ninguno:
da una precisión falsa sobre la que alguien tomará una decisión.**»

`docs/CALIBRACION.md` mide y publica dos números:

```
error medio 5,2 %   ·   peor caso 33,6 %
```

El medidor cita el primero, redondeado a la baja, y **el segundo no aparece en ningún sitio**:

```bash
cd ~/cosmos && python3 -m cosmos medir | grep -o "±[0-9,.]*%" | sort -u
# ±5%
cd ~/cosmos && grep -rn "33,6\|33\.6" cosmos/ spec/ README.md | wc -l
# 0
cd ~/cosmos && grep -n "MARGEN_ERROR" cosmos/medir.py
# 28:MARGEN_ERROR: float | None = 0.052
```

(`0.052` formateado con `:.0%` sale `±5%`: se pierde el 0,2 por redondeo.)

Por qué importa hoy, no en abstracto:

```bash
cd ~/cosmos && python3 -m cosmos medir | sed -n '8p'
#   Presupuesto ..... 4.000     OK, quedan 454 tokens en el peor caso con agua (ciberseguridad)
```

El margen vivo es **454 sobre 3.546 = 12,8 %**. Por debajo del peor caso calibrado de la
heurística. Con un sesgo de peor caso, 3.546 × 1,336 = **4.737 > 4.000**: el árbol estaría en rojo
mostrando verde, y E16 —«no es un aviso, es un rojo», el punto entero del proyecto— no lo vería.

**Fix.** Publicar los dos números en la salida (`estimado, ±5,2 % medio / 33,6 % peor caso`), y
que E16 evalúe el presupuesto contra el peor caso, no contra el medio: un guardarraíl se calibra
por su peor caso o no es un guardarraíl. Alternativa más barata: bajar el presupuesto efectivo de
E16 por el factor de peor caso y decirlo en el mensaje.

---

## A-11 · MEDIO · `oceano/descender` es una exhortación de 144 tokens por sesión contra un comportamiento que la estructura ya impide

Es el nodo de agua más caro del sistema y se paga en **toda** sesión y **todo** subagente:

```bash
cd ~/cosmos && python3 - <<'PY'
from pathlib import Path
from cosmos.modelo import cargar_arbol, cargar_configuracion, cuerpo
from cosmos.medir import contar_aprox
cfg = cargar_configuracion(Path("cosmos.toml"))
arbol = cargar_arbol(cfg.arbol, tambien=(cfg.registro,) if cfg.registro else ())
for n in sorted((x for x in arbol.nodos if x.cosmos == "oceano"), key=lambda x: -contar_aprox(cuerpo(x))):
    print(f"  {contar_aprox(cuerpo(n)):4d} tok  oceano/{n.nombre}")
PY
#    144 tok  oceano/descender
#     93 tok  oceano/irreversible
#     83 tok  oceano/verificar
#     81 tok  oceano/secretos
#     69 tok  oceano/precedencia
#   (470 tokens de océano en toda sesión y todo subagente)
```

Su cuerpo tiene tres párrafos:

1. «El índice nombra a los hijos; no los describe. Para trabajar en algo se entra en su sistema
   solar y desde ahí se desciende. **Abrir un nivel hermano "por si acaso" es el gesto que engorda
   un harness**» — es una petición de buen comportamiento sobre algo que la estructura **ya hace
   imposible**. Medido: con un nicho activo, en la entrada no aparece ni un solo resumen de pueblo
   de otro nicho (ver «lo que sí cumple», prueba L-01: `resúmenes de pueblos de OTRO nicho = 0`).
   No hay nada de al lado que abrir por si acaso; hay que invocar `cosmos abrir` a propósito.
2. «Si algo se necesita a menudo desde varios sitios, es agua y quiere un `moja`» — es taxonomía,
   y su sitio es `spec/TAXONOMIA.md`, no el contexto de cada sesión.
3. «Lo que devuelve un encargo delegado es el camino de un fichero y dos líneas… un contexto lleno
   de material de paso razona entre un 20 % y un 40 % peor» — **no habla de descender**: habla de
   delegación a subagentes. Y su versión estructural ya existe: el guardarraíl **G05**
   (`spec/GUARDARRAILES.md`) desvía a fichero toda salida de más de 50 KB o 2.000 líneas.

Es el antipatrón que la propia `spec/TAXONOMIA.md` cataloga como **«Estrella que ha engordado»**
(«un `CLAUDE.md` con secciones que solo aplican a un hijo → bajar cada sección a su sitio»),
aplicado a un océano, que es el sitio donde más cuesta.

Contraste, para que quede claro que no es una queja genérica: `oceano/irreversible` y
`oceano/precedencia` **son legítimos** y encajan exactos en la lista de `TAXONOMIA.md` («los tres
océanos que casi siempre son legítimos»: daño irreversible, identidad, cómo se decide un
conflicto). `oceano/secretos` y `oceano/verificar` son exhortaciones **con guardarraíl detrás**
(G05 y `puente/secretos.py`; G02 bloquea el cierre con el árbol en rojo), que es la forma correcta
según el corolario 1. `descender` es el único sin ninguna de las dos defensas.

**Fix.** Recortarlo a la frase de identidad («el índice nombra, no describe; se entra por el
sistema solar»), llevar el párrafo 2 a `TAXONOMIA.md` y el 3 a un mar que moje lo que toca la
delegación. Ahorro estimado ~90 tokens en cada sesión y cada subagente, y —más importante— quita
del contexto permanente una regla que pide lo que la forma ya garantiza.

---

## A-12 · MEDIO · `PROGRESS.md`, que `GOAL.md` designa como el estado real, está caducado y cita un nivel retirado

`GOAL.md` §8: «El progreso vive en `PROGRESS.md`… Ninguna de las dos partes declara nada terminado
en el chat: se declara en el fichero».

```bash
cd ~/cosmos && sed -n '3p;10p;21,24p' PROGRESS.md
# Actualizado: 2026-09-01, catálogo por nicho implementado y medido.
#   ninguna ciudad ni pueblo. Con una selección incluye solo las skills invocables de esos sistemas.
# `galaxia/` de 20 a 21 oficios y dejaron su índice E15 rojo a propósito. Se conservaron completos:
# 21 nichos reproduce el antiguo catálogo global: 4.070 tokens, de los que 3.206 son catálogo. Durante
```

Fechado el 2026-09-01 (hoy es 2026-09-03, con dos días de commits encima), habla de **21 oficios**
(son 22) y describe `contexto_inicial` diciendo que «no carga ninguna **ciudad** ni pueblo» —
`ciudad` es un nivel **retirado el 2026-09-01** por `spec/TAXONOMIA.md` y `GOAL.md` §4. Es deuda
directa de la reorganización: el fichero sobrevivió al cambio de taxonomía sin actualizarse.

`GOAL.md` §4 lo juzga solo: «Un nivel sin un solo nodo no es una reserva: es una promesa que el
lector se cree». Aquí un nivel inexistente sigue nombrado en el documento de estado.

**Fix.** Regenerar la cabecera de `PROGRESS.md` con los conteos de `cosmos estado` y quitar
`ciudad`. Y un canario mínimo: que ningún fichero fuera de `research/`, `reviews/`, `registro/` y
`progress/` mencione `ciudad` o `casa` salvo `GOAL.md` y `TAXONOMIA.md`, que las citan a propósito
para documentar la retirada.

---

## A-13 · MEDIO · `NUCLEO.md` delega en `cosmos estado` una pregunta que `cosmos estado` no responde

`spec/NUCLEO.md` §2 retira a propósito la enumeración de ríos por `momento` —bien hecho, es una
lista que envejece— y remite al comando:

> «Cuáles son de cada clase no se escribe aquí… **La dice el árbol —`cosmos estado`—** y la fija
> `tests/test_rio_momento.py`».

`cosmos estado` no la dice:

```bash
cd ~/cosmos && python3 -m cosmos estado | grep -i "rio"
#     rio                17
```

Cuenta 17 ríos y no distingue `trabajo` de `mantenimiento`. La información existe (el catálogo la
usa: agrupa 8 de mantenimiento en una línea sin describirlos) pero el comando al que la spec manda
al lector no la expone. La remisión es correcta en intención y falsa en el hecho.

**Fix.** Que `cosmos estado` desglose `rio` en `trabajo` / `mantenimiento` y liste los nombres —es
el mismo dato que ya calcula `nodos_de_catalogo`—. Es de las mejoras más baratas del informe.

---

## A-14 · BAJO · El registro tiene la forma que promete y ninguna de sus dos ventajas

`spec/REGISTRO.md` justifica toda su estructura con: «**el primer corte es el nicho, porque es como
se busca**… al escribir una entrada hay que elegir su nicho, y esa pequeña fricción obliga a
decidir de qué era».

```bash
cd ~/cosmos && find registro -type f -name "*.md" | sed 's|registro/\([a-z]*\)/\([a-z-]*\)/.*|\1 -> \2|' | sort | uniq -c
#   12 commits -> universo
#    1 decisiones -> universo
#    4 lluvia -> universo
cd ~/cosmos && ls registro/informes/
# (vacío salvo .gitkeep)
```

Las **36** entradas están **todas** en `universo`, el cajón de sastre para «lo que afecta a todo», y
`informes/` —la carpeta de «qué se investigó», la que más ahorra— está vacía. Cero entradas
clasificadas por uno de los 22 nichos. La fricción que la spec dice que obliga a decidir no ha
obligado a decidir ni una vez.

Es defendible por juventud del repo (todo lo hecho hasta hoy es trabajo sobre COSMOS mismo, que es
`universo` legítimamente). Lo señalo porque el mecanismo está sin estrenar y no hay forma de saber
si funciona: es un «verde que nunca ha dado rojo», en la terminología del propio repo.

**Fix.** Ninguno urgente. Cuando entre la primera entrada de un nicho real, comprobar que el
`memoria`/`puente.lluvia` la encuentra por nicho. Y llenar `informes/` con el primer diagnóstico
reutilizable, que es lo que la carpeta promete.

---

# Lo que falta (en COSMOS un hueco es un fallo)

Ordenado por lo que más duele:

1. **Ninguna invariante protege el contrato de `spec/PUEBLO.md`.** Es la spec que define la
   calidad del producto —247 pueblos son el 59 % de los nodos— y es la única normativa sin código
   detrás. Hueco medido en A-06: 67 pueblos sin rival nombrado, 55 sin comando de instalación.
2. **El medidor no tiene magnitud para la vista plana compilada.** Es el artefacto que el runtime
   consume y el único gasto grande que ninguna cifra publicada ve (6.167 tokens, A-02). Falta
   `vista_compilada` en `ResumenMedicion` y en el `--json`.
3. **No hay camino documentado de la galaxia al directorio que el runtime escanea.** El único
   `destino` que apunta a `.claude/skills` es el del árbol de juguete. Falta la sección del README
   que diga cómo se entrega la galaxia a un proyecto real, que es literalmente el producto según
   `GOAL.md` §1 («un repo que se puede clonar sobre cualquier proyecto»).
4. **E00 no tiene definición normativa.** Es el código más ancho del validador (8 ramas) y no
   existe en ninguna spec (A-05).
5. **Falta el canario de completitud sobre la tabla de invariantes.** Existen canarios para el
   rango (`E00–E03 y E05–E20`), para los mares, para los ejemplos de frontmatter y para 4 cifras;
   no existe el que compara `codigos_comprobados()` con lo que documenta `VALIDADOR.md`. Por eso
   A-05 lleva vivo desde que se añadió E17.
6. **Falta el canario sobre el `resumen` de la galaxia.** Es la cadena más cara del sistema y la
   única de su clase sin vigilancia (A-01).
7. **El peor caso de la calibración (33,6 %) no se publica.** Está medido en
   `docs/CALIBRACION.md` y no sale por ninguna interfaz (A-10).
8. **Cuatro niveles de la taxonomía no tienen ningún nodo en la galaxia**: `planeta`, `provincia`,
   `lago`, `luna` (`python3 -m cosmos estado`, sección «Niveles sin un solo nodo»). Esto **no** es
   un fallo por sí mismo —viven en `ejemplo/` y `GOAL.md` §4 exige nodo «en ninguno de los dos
   árboles», criterio que se cumple, y `tests/test_niveles_vivos.py` lo vigila— pero deja el
   producto sin ningún ejemplo real de un `planeta` con su `luna`, que es la mitad del modelo que
   se vende (proyecto + subagente). Falta un caso real, no un nivel.
9. **`registro/informes/` vacío** (A-14): la carpeta que la spec presenta como la que más tiempo
   ahorra no tiene una sola entrada.

---

# Mejoras, priorizadas

| # | Mejora | Coste | Por qué primero |
|---|---|---|---|
| M1 | Generar la cabecera del índice contando el árbol, en vez de copiar el `resumen` de la galaxia | bajo | Cierra A-01 de raíz en vez de parchear un número, y quita la única mentira del artefacto que se declara incapaz de mentir |
| M2 | `cosmos estado` desglosa `rio` por `momento` y lista nombres | muy bajo | Cierra A-13; el dato ya está calculado |
| M3 | Canario `codigos_comprobados()` ⊆ tabla de `VALIDADOR.md` + reponer las 5 filas | bajo | Cierra A-05 y evita que el siguiente E21 se escape igual |
| M4 | Publicar peor caso de calibración y evaluar E16 contra él | bajo | Un guardarraíl se calibra por su peor caso; hoy el margen vivo (12,8 %) es menor que el error de peor caso (33,6 %) |
| M5 | Magnitud `vista_compilada` en el medidor + `arrancar` compila acotado | medio | Cierra A-02 por el lado medible; es el mayor gasto invisible del sistema |
| M6 | Invariante E21 sobre el contrato de pueblo, con `origen: propio` como escape declarado | medio | Convierte `PUEBLO.md` de exhortación en estructura, que es el corolario 1 |
| M7 | Unificar la semántica de `nichos=None` en catálogo y compilación, con test conjunto | medio | Cierra A-04; hoy el `cosmos.toml` documenta la mitad equivocada |
| M8 | Reescribir §E16 de `VALIDADOR.md` (agua + clave real) y las 2 palabras del README | muy bajo | A-08 y A-09; ambos son minutos y ambos están en documentos de cabecera |
| M9 | Registrar las 4 cifras petrificadas restantes en `test_cifras_de_las_specs.py` | bajo | A-07 |
| M10 | Podar `oceano/descender` a su frase de identidad | bajo | ~90 tok × toda sesión × todo subagente, y quita una petición de buen comportamiento del sitio más caro |
| M11 | Regenerar `PROGRESS.md` y purgar `ciudad` | muy bajo | A-12 |

---

# Lo que verifiqué que sí cumple

Entré a tumbar cada una de estas y no pude. Lo que intenté, con su salida.

**L-01 · La carga perezosa es real, no retórica.** Es la afirmación central del producto
(`GOAL.md` §4: «Lo que **nunca** ocurre: que el contexto inicial contenga el cuerpo de un pueblo,
la descripción de un pueblo de otro sistema solar, o un lago que no moja el path que se está
tocando»). Intenté encontrar aunque fuera un cuerpo colado:

```bash
cd ~/cosmos && python3 - <<'PY'
from pathlib import Path
from cosmos.modelo import cargar_arbol, cargar_configuracion, cuerpo
from cosmos.medir import contexto_inicial
cfg = cargar_configuracion(Path("cosmos.toml"))
arbol = cargar_arbol(cfg.arbol, tambien=(cfg.registro,) if cfg.registro else ())
for sel, etq in [(None, "por defecto"), (["ciberseguridad"], "peor nicho")]:
    ctx = contexto_inicial(arbol, sel)
    pu = [n for n in arbol.nodos if n.cosmos == "pueblo" and len(cuerpo(n)) > 80 and cuerpo(n)[:80] in ctx]
    ll = [n for n in arbol.nodos if n.cosmos == "lluvia" and len(cuerpo(n)) > 50 and cuerpo(n)[:50] in ctx]
    ma = [n for n in arbol.nodos if n.cosmos == "mar"    and len(cuerpo(n)) > 50 and cuerpo(n)[:50] in ctx]
    print(f"  {etq:12s}: cuerpos de pueblo={len(pu)}  lluvia={len(ll)}  mar={len(ma)}  chars={len(ctx)}")
ctx = contexto_inicial(arbol, ["ciberseguridad"])
otros = [n.nombre for n in arbol.nodos if n.cosmos == "pueblo"
         and (n.datos.get("padre") or "").split("/")[0] != "ciberseguridad"
         and n.datos.get("resumen", "") in ctx]
print("  resumenes de pueblos de OTRO nicho en la entrada:", len(otros))
PY
#   por defecto : cuerpos de pueblo=0  lluvia=0  mar=0  chars=4562
#   peor nicho  : cuerpos de pueblo=0  lluvia=0  mar=0  chars=8535
#   resumenes de pueblos de OTRO nicho en la entrada: 0
```

Cero por los cuatro lados. La tesis del proyecto se sostiene.

**L-02 · La regla dura «una herramienta vive en un solo sitio, cero repetidos» se cumple.** Busqué
duplicados por nombre y por URL de repositorio, sobre los 247:

```
pueblos: 247 | nombres repetidos: []
repos GitHub citados por 2+ pueblos: 1  ->  sigmahq/sigma -> ['chainsaw', 'sigma-cli']
```

El único candidato **no es un duplicado**, y lo comprobé abriendo los dos: `chainsaw` cita
`SigmaHQ/sigma` como *corpus de reglas* (`git clone … # el corpus de reglas`) y su herramienta es
`WithSecureLabs/chainsaw`; `sigma-cli` cita el mismo corpus y su herramienta es `SigmaHQ/sigma-cli`.
Dos herramientas distintas compartiendo un conjunto de datos. Cero repetidos de verdad.

**L-03 · Un pueblo nunca promete un fichero que no entrega.** `spec/PUEBLO.md` cierra con «Un
pueblo cuya utilidad depende de un fichero que no está es peor que no tenerlo». Esperaba encontrar
huecos, porque es el tipo de cosa que se rompe al mover directorios:

```bash
cd ~/cosmos && python3 - <<'PY'
import pathlib, re
faltan = ok = 0; malos = []
for skill in sorted(pathlib.Path("galaxia/pueblos").glob("*/SKILL.md")):
    c = skill.read_text(encoding="utf-8")
    for r in set(re.findall(r"`((?:scripts|plantillas|config|templates|assets)/[A-Za-z0-9_\-./]+)`", c)):
        if (skill.parent / r).exists(): ok += 1
        else: faltan += 1; malos.append((skill.parent.name, r))
print(f"referencias a ficheros propios: {ok+faltan}  existen: {ok}  FALTAN: {faltan}", malos)
PY
# referencias a ficheros propios: 75  existen: 75  FALTAN: 0
```

**75 de 75.** Ni una rota.

**L-04 · Los 17 ríos ejecutan de verdad.** Un río es «un comando» y declara su `invoca:`. Los
ejecuté todos (en `bash`, ver Método):

```
exit=0 · cosmos abrir --help · cosmos buscar --help · cosmos estado · cosmos mapa
exit=0 · cosmos acertar --help · cosmos generar --help · cosmos enganchar --help
exit=0 · cosmos desenganchar --help · cosmos saltar --listar
exit=0 · puente.gate --help · puente.lluvia --help · puente.proyectar --help · puente.secretos --help
```

13/13 en verde (los 4 restantes —`validar`, `medir`, `compilar`, `arrancar`— se ejecutaron con
carga real a lo largo del informe). Ningún río nombra un comando que no existe.

**L-05 · El grafo `usa:` es exactamente lo que `COMPOSICION.md` afirma** (salvo el número, A-07):

```
nodos con usa: 22 | aristas: 54
E20 destinos rotos: 0 | auto-referencias: 0
sistemas que nadie cita (terminales): ['juegos']
sistemas CON usa: 22 de 22 | sistemas SIN usa: []
```

`COMPOSICION.md` afirma «quedó un único oficio al que nadie manda, `juegos`, declarado terminal».
Es cierto, medido. E20 no tiene ni un destino roto en 54 aristas.

**L-06 · La válvula de escape cumple sus seis propiedades.** Intenté saltármela por los cuatro
lados que el README declara cerrados, sobre una copia en `/tmp`:

```
saltar E16 --caduca 1d          (sin --motivo)     -> exit 1     [motivo obligatorio]
saltar E16 --motivo x           (sin --caduca)     -> exit 1     [caducidad obligatoria]
saltar E16 --motivo x --caduca 60d                 -> "COSMOS  saltar  rojo"   [máximo 30 días]
saltar todo --motivo x --caduca 1d                 -> "COSMOS  saltar  rojo"   [nunca «todo»]
```

Y la propiedad que el README pone como la que sostiene la confianza —«La palabra "verde" no aparece
nunca sola habiendo saltos activos»— se cumple en los dos veredictos:

```
COSMOS  rojo (1 salto activo: E16, caduca en 1 d)  1 errores
COSMOS  verde (1 salto activo: E16, caduca en 1 d)  0 errores
```

**L-07 · `arrancar` no repara en silencio un índice que miente.** El README lo promete explícitamente
(«**No** regenera el índice: si el índice miente, sale en rojo y te manda a `cosmos generar`. Un
bootstrap que repara en silencio lo que el validador debería denunciar no es un bootstrap, es un
encubrimiento»). Le añadí una línea falsa al índice de una copia:

```
exit=1
COSMOS  rojo  1 errores
E15  …/galaxia/COSMOS.md
     Ejecuta 'cosmos generar'; no edites el índice a mano.
COSMOS  arrancar  rojo
--- el indice se conservo sin tocar? ---  intacto: arrancar no lo toco (bien)
```

Rojo, exit 1, mensaje accionable, y **el índice mentiroso sigue ahí sin tocar**. Exactamente lo
prometido.

**L-08 · El método de medición no puede cambiar un veredicto.** `NUCLEO.md` §4: «`--metodo` en
línea de comandos existe para inspeccionar a mano, y **no** puede cambiar el veredicto de
`cosmos validar`». Estructuralmente cerrado: `cosmos validar --help` no tiene `--metodo`
(sus flags son `--config`, `--json`, `--indice`, `--nicho`). Y `--metodo exacto` falla en voz alta
con exit 1 en vez de caer a `aprox`, que es la otra mitad de la promesa.

**L-09 · La configuración por defecto se anuncia.** `VALIDADOR.md`: «si falta el fichero, se usan
estos valores por defecto y el validador **lo dice en la primera línea de su salida**». Borré el
`cosmos.toml` de una copia:

```
COSMOS  rojo  3 errores (presupuesto por defecto: no hay cosmos.toml)
```

Primera línea, tal cual. «Un umbral silencioso es un umbral que alguien subió sin querer» — aquí
no lo es.

**L-10 · Los mensajes de error dicen qué hacer, no solo qué está mal.** Es un requisito explícito
de `VALIDADOR.md` («Ese último campo —qué hacer— no es cortesía»). Verificado en los cuatro rojos
que provoqué (E05, E15, E19, E16): los cuatro traen línea de remedio. Y E17 cumple su requisito más
duro de `NUCLEO.md` §10 —«El error nombra los dos nodos, el porcentaje y **las dos frases
concretas**»—: el formato del emisor en `cosmos/validar.py` es
`solapamiento {similitud:.1%} entre {primero.referencia} y {segundo.referencia}; «{frase_a}» ≈ «{frase_b}»`.

**L-11 · La optimización de `momento` está aplicada de verdad.** `NUCLEO.md` §2 dice que los ríos
de mantenimiento se **nombran sin describirse**. El catálogo por defecto lo hace: 9 ríos de trabajo
con su resumen, y los 8 de mantenimiento en una sola línea agrupada
(`rio (mantenimiento, 'cosmos abrir rio/x'): acertar, arrancar, compilar, desenganchar, enganchar,
generar, mapa, proyectar`), 240 tokens en total. No están escondidos —`cosmos abrir rio/<n>` los
entrega enteros— que es la otra mitad de lo prometido.

**L-12 · La suite es real y no está contaminada.** `Ran 259 tests in 104.498s — OK (skipped=2)`,
exit 0, ejecutada dos veces con el mismo resultado y sin otro trabajo pesado en la máquina. Los 2
saltados se anuncian en voz alta, como exige `MEDIDOR.md` («saltado automáticamente —y **dicho en
voz alta**, no en silencio— si no hay tokenizador local»):

```
AVISO  SIN TOKENIZADOR: el margen publicado (±5,2 %) NO se ha verificado en esta ejecución.
       Instálalo en un venv temporal (docs/CALIBRACION.md) o exige el fallo con COSMOS_EXIGE_TOKENIZADOR=1.
```

(De paso: ese aviso publica el **±5,2 %** correcto que la salida de `cosmos medir` redondea a
±5 % — ver A-10.)

**L-13 · Los canarios que existen, funcionan.** No me limité a leerlos: `tests/test_spec_al_dia.py`
compara los mares de `spec/UNIVERSO.md` contra `galaxia/agua/mar-*.md` y traduce el cardinal en
letra de la frase «Seis aguas que mojan»; `tests/test_cifras_de_las_specs.py` vigila 4 cifras, que
las retiradas sigan retiradas, que los ejemplos de `FRONTMATTER.md` y `COMPOSICION.md` apunten a
nodos reales, que `criterio` siga siendo mar, y que **toda invariante viva tenga válvula**
(`set(CODIGOS_INVARIANTES) == codigos_comprobados()`). Y `puente/tests/mutaciones.py` mantiene
mutaciones nombradas (M51–M54) que exigen que canarios concretos las maten. Es de lo mejor que hay
en el repo; el problema no es que fallen, es dónde **no** están (A-01, A-05, A-07).

**L-14 · Contención sin huérfanos.** `GOAL.md`: «ningún elemento existe fuera de un padre». Sobre
los 416 nodos, E01/E02/E03 pasan en verde y no hay ningún sólido sin `padre` salvo la galaxia (los
22 sistemas solares declaran `padre: ""`, la raíz, que es lo que fija `NUCLEO.md` §1: «La galaxia
tiene `ruta = ""` y se referencia como `""`»). Lo comprobé creyendo que era un hueco antes de leer
§1; no lo es.

---

## Nota de cierre

De 14 hallazgos, **12 son de documento contra código y solo 2 son de código** (A-02 en su segunda
mitad, y A-04). El código de COSMOS es notablemente más fiel a sus intenciones que las specs a su
código: el validador, el medidor, la válvula, el compilador y los canarios hacen lo que dicen y se
les ha visto fallar. Lo que se ha quedado atrás es la prosa normativa —la tabla de invariantes, las
cifras, el principio del README, `PROGRESS.md`— y lo que falta son guardarraíles para las dos reglas
que hoy solo son párrafos: el contrato del pueblo (A-06) y las cifras de las specs que aún no están
en el canario (A-07).

El hallazgo que yo pondría primero no es el más caro en tokens sino el más caro en crédito: **A-01**.
Un repo cuya tesis es «lo que se genera no puede mentir» tiene una mentira dentro de lo generado, en
la línea que más veces se lee de todo el sistema.
