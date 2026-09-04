# Revisión adversarial de COSMOS — informe final

**Premisa**: todo esto está mal y mi trabajo era demostrarlo. Lo que aparece como «aguantó» solo
está ahí después de haber intentado tumbarlo y no haber podido, y digo qué intenté.

**Estado auditado** (fijado en cabecera, porque el árbol muta):

```
$ cd <repo> && git rev-parse HEAD && git status --porcelain | wc -l
243ec876d5947cab5b1526f6cbc3cdb713c44174
       0
$ python3 --version   # 3.14.3 ; tiktoken NO instalado
```

Todo lo destructivo se hizo sobre copias en `/tmp/cosmos-adv/`. El repo no se tocó salvo este
fichero.

> **Aviso: el árbol mutó durante la revisión.** Al empezar, `git status --porcelain` daba 0 líneas.
> Al cerrar, otra ventana había añadido cuatro pueblos sin seguimiento —`codigo-al-modelo`,
> `cuentas-del-asistente`, `delegar-generacion`, `ordenes-entre-ventanas`— a las 13:18, y con ellos
> **la galaxia pasó a rojo con 7 errores** (`E19: … no figura en el manifiesto`, ×4). Todas las
> mediciones de este informe son del estado `243ec87` limpio. Comprobado tras la mutación: `Entrada
> base 1.128` y `Peor nicho 1.771 (ciberseguridad)` **no cambian**; `Universo` sube de 19.978 a
> 21.423, y con él la descarga. El rojo se repara con
> `python3 -m cosmos compilar galaxia --config galaxia.toml`, y es una demostración en vivo de H09 y
> H03: nadie lo ejecutó al añadir los pueblos porque nada lo ejecuta.

**Resultado**: de las 10 afirmaciones a desmentir, **4 caen** (1, 2, 6, 8), 6 aguantan (3, 4, 5, 7,
9, 10 — con matices en 5 y 9). **26 hallazgos**, 5 de ellos rompen el sistema.

---

## Resumen por afirmación

| # | Afirmación | Veredicto |
|---|---|---|
| 1 | 20 invariantes y cada una se ha visto fallar | **DESMENTIDA** — E04 es inalcanzable y su test la falsea (H04) |
| 2 | La batería no es decorativa | **PARCIALMENTE DESMENTIDA** — cierto en `cosmos/`, falso en `puente/secretos.escanear()` (H07) |
| 3 | 1.128 / 1.771 / 91,1 % | **AGUANTA** — reproducido byte a byte con una reimplementación independiente |
| 4 | E16 contra el peor nicho | **AGUANTA** — nombra el nicho y el exceso exacto |
| 5 | No hay herramientas repetidas | **AGUANTA** entre pueblos; hay una puerta trasera en los mares (H15) |
| 6 | Cero credenciales y cero datos de cliente | **DESMENTIDA** — el repo no pasa su propio escáner (H06, H18) |
| 7 | `compilar` no borra lo ajeno | **AGUANTA** — dos pasadas, nada ajeno tocado |
| 8 | El índice no puede mentir | **DESMENTIDA** — miente entero y el comando por defecto dice verde (H02) |
| 9 | Las 21 estrellas dicen algo específico | **AGUANTA** en su mayor parte; ~5 frases de 74 son genéricas o duplicadas (H13) |
| 10 | El puente está adaptado, no copiado | **AGUANTA** — 0,24–0,47 de similitud; quedan restos menores (H19) |

---

# Hallazgos, de lo que rompe el sistema a lo cosmético

## H01 · CONFIRMADO · Un clon limpio del repositorio está en ROJO con 189 errores

`.cosmos/compilado-galaxia.json` **está versionado**, pero `.cosmos/vista-galaxia/` está en
`.gitignore`. El manifiesto llega al clon; la vista que describe, no. E19 encuentra 189
desincronizaciones antes de que nadie toque nada.

```
$ cd <repo> && git ls-files | grep -E '^\.cosmos|^\.claude'
.claude/skills/probar-salida
.claude/skills/revisar-formato
.cosmos/compilado-galaxia.json
.cosmos/compilado.json

$ git clone -q <repo> /tmp/clon && cd /tmp/clon
$ python3 -m cosmos validar galaxia --config galaxia.toml | head -4
COSMOS  rojo  189 errores

E19  /private/tmp/clon/.cosmos/vista-galaxia
     vista plana desincronizada: a11y-auditoria-wcag: contenido o enlace distinto del árbol
$ echo $?
1
```

GOAL §1 promete «un repo que se puede clonar sobre cualquier proyecto… con carga perezosa real y
**verificable**». En cualquier máquina que no sea esta, no verifica.

**Se recupera** con un comando, y sin ensuciar el árbol —lo comprobé—, pero nadie lo dice y nada
lo ejecuta:

```
$ cd /tmp/clon && python3 -m cosmos compilar galaxia --config galaxia.toml | head -3
COSMOS  compilar  verde
Creadas 0; actualizadas 189; iguales 0; ajenas respetadas 0; obsoletas eliminadas 0; obsoletas preservadas 0.
$ python3 -m cosmos validar galaxia --config galaxia.toml | head -1
COSMOS  verde  0 errores
$ git status --porcelain | wc -l
       0
```

**Arreglo**: o `.cosmos/compilado-galaxia.json` también se ignora, o la vista se versiona, o E19
distingue «falta la vista, ejecuta compilar» de «la vista miente».

---

## H02 · CONFIRMADO · `cosmos validar` a secas valida el ejemplo de juguete, no la galaxia — y es lo único que corre el gate

`cosmos.toml` apunta a `raiz.arbol = "ejemplo"`. El árbol real necesita `--config galaxia.toml`.
Falsifiqué el índice de la galaxia entero y el comando por defecto siguió en verde:

```
$ cd /tmp/cosmos-adv/repo   # copia
$ printf '%s\n' '<!-- Generado por cosmos generar. No editar a mano. -->' '' \
    '# COSMOS — mentira-total' '' '## Sistemas solares' '' \
    '- `no-existe` — Un oficio inventado que no esta en el arbol.' '' \
    '## Oceanos' '' '- Ninguno' > galaxia/COSMOS.md

$ python3 -m cosmos validar ; echo "EXIT=$?"
COSMOS  verde  0 errores
EXIT=0

$ python3 -m cosmos validar galaxia --config galaxia.toml | head -3
COSMOS  rojo  1 errores
E15  .../galaxia/COSMOS.md
     índice desincronizado
```

Y el único verificador automático del repo usa exactamente esa forma:

```
$ grep -n 'cosmos.*validar' puente/gate.py
80:        [sys.executable, "-m", "cosmos", "validar"],
```

Es decir: **la afirmación «el índice no puede mentir» es cierta para el árbol al que apuntes, y el
gate apunta al de juguete.** E15 funciona; el cableado no.

La causa de fondo está confesada en `galaxia.toml`: `destino` y `manifiesto` son globales, así que
hicieron falta dos configuraciones para dos árboles del mismo repo. Ese parche es el que produce
este agujero.

---

## H03 · CONFIRMADO · Nada ejecuta nada, y el gate que existe no puede instalarse

```
$ ls <repo>/.git/hooks/pre-commit
ls: ...: No such file or directory
$ ls <repo>/.github
ls: ...: No such file or directory
```

No hay hook, no hay CI, no hay workflow. Y el gate escrito para eso **devuelve 1 sobre el propio
repo**, así que instalarlo bloquearía todos los commits:

```
$ cd /tmp/cosmos-adv/mut && python3 -m puente.gate --sin-pruebas ; echo "EXIT=$?"
secretos: limpio
ERROR: ruta#1fae9196a0f8:94: posible teléfono
... (12 líneas)
secretos: 12 hallazgo(s); valores y rutas ocultos
EXIT=1
```

Ni siquiera llega a `cosmos validar`: aborta en el primer paso.

`GOAL.md §7.4` exige «ninguna regla que dependa de que alguien se acuerde». `README.md:52` dice
literalmente «Tres piezas, y ninguna depende de que nadie se acuerde de nada» — y a continuación
lista **cuatro comandos que hay que teclear a mano**. `QUEDA.md §6` ya cita el precedente exacto
(«el detector estaba bien; nadie lo ejecutaba») y COSMOS está hoy en ese mismo sitio.

Lo mismo vale para `puente/tests/mutaciones.py`: existe, funciona (8/8), y no lo invoca nadie.

---

## H04 · CONFIRMADO · E04 (ciclo) es inalcanzable, y su test la falsea con una subclase

**Prueba empírica.** Construí 20 roturas independientes, una por invariante, sobre árboles reales
en disco (`/tmp/cosmos-adv/romper20.py`). 18 saltan. E04 nunca:

```
$ python3 /tmp/cosmos-adv/romper20.py | tail -24
E04   NO    ciclo entre dos paises   -> ['E02']
...
20 roturas, 18 invariantes vistas fallar, 2 NO saltaron
```

(la otra «NO» fue culpa mía: mi cebo de E08 no era válido; con uno correcto E08 sí salta, ver H16.
La cuenta real es **19 de 20 alcanzables**.)

**Prueba formal de por qué E04 no puede saltar nunca.** Para un sólido `n` distinto de la galaxia,
`referencia(n) = padre(n) + "/" + nombre(n)`, y `nombre` cumple `^[a-z0-9-]+$`, luego tiene longitud
≥ 1. Por tanto `len(referencia(n)) > len(padre(n))` **estrictamente**. Si hubiera un ciclo
`n₁→n₂→…→n_k→n₁` en el grafo de padres resueltos, la longitud crecería a lo largo del ciclo y
volvería a su punto de partida: contradicción. Y si el padre **no** resuelve, E02 salta antes y E04
no llega a mirar. El agua no tiene `padre` (E00 lo prohíbe), así que tampoco cierra ciclos.

**El test que dice que E04 se vio fallar no prueba nada** (`tests/test_validador.py:85-97`): define

```python
class NodoCiclico(Nodo):
    @property
    def ruta_cosmos(self) -> str:
        return str(self.datos["ruta-prueba"])
```

es decir, **sustituye la definición de identidad de NUCLEO §1** por un campo `ruta-prueba` que
ningún parser puede producir, y monta el `Arbol` a mano sin pasar por `cargar_arbol`. Es el
antipatrón «un efecto provocado por un atajo no es un efecto reproducible».

**Consecuencia.** El titular «20 invariantes y cada una se ha visto fallar» es falso: son 19
alcanzables y una decorativa. **Y es una buena noticia mal contada**: NUCLEO §1 hizo los ciclos
imposibles por construcción. Lo honesto es borrar E04 y decir en NUCLEO §1 que la ruta completa ya
garantiza aciclicidad, no fingir que se vigila.

---

## H05 · CONFIRMADO · Los 189 «pueblos» no son herramientas: son 189 fichas de prosa

GOAL §1: «herramientas que se ejecutan, no listas de consejos». UNIVERSO, criterio 1 (eliminatorio):
«Se ejecuta». Medido sobre los 189:

```
$ python3 - <<'PY'   # completo en el cuerpo de este informe
...
PY
     0/189  url http(s)
     0/189  bloque de codigo ```
     0/189  comando pip/npm/brew/cargo/go install
    22/189  menciona licencia
     6/189  menciona estrellas/ultimo push
     0/189  menciona que se probo
ficheros que acompañan a cada pueblo: NINGUNO — los 189 son un único SKILL.md
```

Ni una URL, ni un bloque de código, ni un comando de instalación, ni un fichero ejecutable. Un
pueblo tipo:

```
$ cat galaxia/pueblos/a11y-auditoria-wcag/SKILL.md
resumen: Guiones de navegador para foco, reflow y tamano de objetivo: la mitad que ningun motor detecta.
---
Trae paquete propio con guiones de navegador dedicados a lo que no se automatiza...
Gana a la coleccion de setenta y nueve agentes de accesibilidad de otro proyecto...
```

No dice **cuál** es el paquete. `cosmos compilar` enlaza esto en `.claude/skills/`, donde un agente
que invoque la skill recibe un párrafo que no nombra lo que hay que ejecutar.

El criterio 5 de UNIVERSO («se ha usado una vez… se prueba en un caso real») no tiene evidencia en
ningún pueblo: 0/189.

Las 27 excepciones parciales son las que citan `cosecha/<script>` — pero como ruta **relativa**, que
solo resuelve si el proceso corre desde la raíz de COSMOS; `puente/proyectar.py` no lleva `cosecha/`
al repo destino, así que en un planeta proyectado esas referencias apuntan a la nada.

---

## H06 · CONFIRMADO · El repo no pasa su propio escáner de secretos

```
$ cd <repo> && python3 -m puente.secretos --todo >/dev/null; echo $?
1
```

12 hallazgos. Resueltos a rutas con la propia `etiqueta_de_ruta` (no transcribo ningún valor):

| Etiqueta | Fichero | Tipo |
|---|---|---|
| `ruta#5ce6a04aa376` | `.cosmos/compilado.json` | artefacto generado versionado (su propia regla lo prohíbe) |
| `ruta#6aa717b20a1c` | `.cosmos/compilado-galaxia.json` | ídem |
| `ruta#84ff62e35ff2` | `.claude/skills/revisar-formato` | symlink versionado + vista plana generada |
| `ruta#f5b7ccf5c726` | `.claude/skills/probar-salida` | ídem |
| `ruta#27c57a873808:11` | `cosecha/enviar-correo-smtp.py` | correo de ejemplo en el docstring |
| `ruta#728af2878291:11` | `cosecha/legales-crear-paginas.py` | correo + teléfono de ejemplo |
| `ruta#71fbc2f5da92:11` | `cosecha/legales-texto.py` | identificador fiscal de ejemplo |
| `ruta#581adcbe1e97:277` | `research/HERRAMIENTAS-PROPIAS.md` | identificador fiscal citado |
| `ruta#1fae9196a0f8:94` | `cosecha/patch-claude-mem-hooks.sh` | falso positivo real (`for i in 1 2 3…` leído como teléfono) |

Los seis últimos son **falsos positivos** de documentación (marcadores tipo `<nif>`/`<correo>` en
ejemplos de uso). Los cuatro primeros **no**: son artefactos generados y symlinks versionados que la
propia allowlist del escáner declara no versionables. Da igual la mezcla: el efecto es que el gate
está en rojo permanente y por eso nadie lo instala. Es exactamente el ciclo que el comentario de
`test_secretos.py` describe: «entonces el gate se queda en rojo para siempre o alguien lo silencia».

**Arreglo**: ignorar `.cosmos/` y `.claude/skills/` en git; y para los ejemplos, o marcadores que no
casen con los patrones, o una allowlist con motivo escrito.

---

## H07 · CONFIRMADO · La función pública del escáner de secretos no la prueba nadie

Sabotaje quirúrgico sobre una copia: `escanear()` devuelve «limpio» pase lo que pase.

```
$ cd /tmp/cosmos-adv/sab_p_secretos
# en puente/secretos.py, dentro de escanear(), antes del bucle:
#     return []  # SABOTAJE
$ python3 -m unittest discover -s puente/tests -t . 2>&1 | tail -1
OK
```

**35/35 verde con el escáner ciego.** `test_secretos.py` solo ejercita `escanear_flujo` y
`_hallazgos_de_ruta`; nunca `escanear()`, que es lo que llaman `main()` y el gate. La ruta
«`_candidatas` devuelve lista vacía → limpio» (repo vacío, cwd equivocada, `--diff-filter` sin
coincidencias, regresión en `_entradas_del_indice`) no tiene una sola aserción.

Contrasta con `cosmos/`, donde el sabotaje equivalente **sí** se caza. Cuatro sabotajes más, todos
en rojo:

```
$ # COMPROBACIONES vaciado (validar siempre verde)
  FAILED (failures=26, skipped=1)   de 52
$ # contar_aprox -> 0
  FAILED (failures=7)
$ # peor nicho = caso base (E16 deja de mirar el peor nicho)
  FAILED (failures=4)
$ # catalogo_visible -> ""
  FAILED (failures=5)
$ # descarga fijada a 0.911
  FAILED (failures=5)
$ # etiqueta_de_ruta devuelve la ruta en claro
  FAILED (failures=9)
```

Y `puente/tests/mutaciones.py` da **8/8 en rojo** cuando se ejecuta. La batería no es decorativa —
**salvo en el punto exacto donde más importa**.

---

## H08 · CONFIRMADO · E11 («océano encubierto») se evade con cinco globs distintos

E11 compara con el literal `["**"]`. Cualquier otra forma de mojarlo todo pasa:

```
$ python3 /tmp/cosmos-adv/agua.py
  mar con moja='**/*'     -> VERDE (oceano encubierto no detectado)
  mar con moja='**/**'    -> VERDE
  mar con moja='*'        -> VERDE
  mar con moja='**/*.*'   -> VERDE
  mar con moja='./**'     -> VERDE
```

La invariante existe precisamente para impedir «un párrafo global bienintencionado» disfrazado de
regla regional (GOAL §3), y comprueba una cadena en vez de la cobertura del glob. En el árbol real
ya hay un caso de facto: `mar/criterio` moja **diez** globs de lenguaje (`**/*.py`, `**/*.js`,
`**/*.ts`, `**/*.tsx`, `**/*.php`, `**/*.go`, `**/*.rs`, `**/*.rb`, `**/*.java`, `**/*.sh`), lo que
cubre cualquier trabajo de código que exista.

---

## H09 · CONFIRMADO · El nicho activo vive en un flag, no en configuración: `validar` queda en rojo permanente

`cargar_configuracion()` nunca lee `nichos`; `Configuracion.nichos` es siempre `None` salvo que se
pase `--nicho` en esa invocación concreta.

```
$ cd /tmp/cosmos-adv/repo2
$ python3 -m cosmos validar galaxia --config galaxia.toml | head -1
COSMOS  verde  0 errores

$ python3 -m cosmos compilar galaxia --config galaxia.toml --nicho web | head -3
COSMOS  compilar  verde
Creadas 0; actualizadas 0; iguales 13; ajenas respetadas 0; obsoletas eliminadas 176; obsoletas preservadas 0.

$ python3 -m cosmos validar galaxia --config galaxia.toml | head -4     # lo que hará el gate, el CI y el humano
COSMOS  rojo  1 errores
E19  .../.cosmos/vista-galaxia
     vista plana desincronizada: el manifiesto declara nichos ['web'] y se validan None

$ python3 -m cosmos validar galaxia --config galaxia.toml --nicho web | head -1
COSMOS  verde  0 errores
```

Es decir: **el runtime acotado —la función entera del catálogo por nicho— solo se puede verificar si
todo el mundo recuerda repetir el mismo flag.** Es literalmente el patrón que GOAL §2 corolario 1
prohíbe: una regla que depende de que el modelo se acuerde.

**Arreglo de una línea de spec**: `[nichos] activos = ["web"]` en `cosmos.toml`, leído por
`cargar_configuracion`, y `--nicho` como override de inspección igual que `--metodo`.

---

## H10 · CONFIRMADO · `spec/UNIVERSO.md`, el mapa normativo, contradice el árbol en 5 de 21 nichos

GOAL §1 dice «El mapa está en `spec/UNIVERSO.md`», y GOAL §0 dice «Si algo del repo contradice este
fichero, gana este fichero».

```
$ python3 -c "..."   # comparación tabla de UNIVERSO vs galaxia/sistemas/*.md
en UNIVERSO.md y NO en la galaxia: ['video', 'voz']
en la galaxia y NO en UNIVERSO.md: ['audiovisual', 'documentos', 'rendimiento']
UNIVERSO dice 20 nichos; la galaxia tiene 21
```

El documento normativo describe dos oficios que no existen y desconoce tres que sí. Además, su
sección «El límite que hace que esto no se descontrole» sigue diciendo «66 herramientas montadas:
entrada 2.572 tokens, 1.713 de catálogo» — números de tres commits atrás; hoy son 189 herramientas
y 1.771 en el peor nicho. GOAL §1 repite los mismos 2.572/1.713/66.

---

## H11 · CONFIRMADO · `QUEDA.md`, presentado como «estado medido», es falso en 6 de sus 8 puntos

Su propia cabecera dice «cada línea sale de contar el repo». La conté:

| QUEDA dice | Medido hoy | Comando |
|---|---|---|
| «el árbol está en rojo: entrada 4.070, presupuesto 4.000» | verde; 1.128 base / 1.771 peor | `python3 -m cosmos medir galaxia --config galaxia.toml` |
| «Dieciséis nichos sin estrella» | 0 sin estrella (21 estrellas / 21 sistemas) | `ls galaxia/estrellas \| wc -l` → 21 |
| «64 scripts… y ningún pueblo los referencia» | 79 scripts, 27 ficheros de `galaxia/` los referencian | `ls cosecha \| wc -l`; `grep -rl 'cosecha/' galaxia/ \| wc -l` |
| «Las cuatro piezas de el arnés de origen… ninguna migrada» | `puente/` con 5 módulos, 1.446 líneas, 35 tests | `wc -l puente/*.py` |
| «COSMOS no está en GitHub» | `origin` configurado | `git remote -v` |
| «127 herramientas · 50 países · 47 tests» | 189 · 56 · 52 | conteos por `cosmos:` |

Solo siguen vigentes el punto 5 (`usa:` sin E20 — verificado: E00 lo rechaza con «campo no permitido
para sistema-solar: 'usa'») y el punto 6 (guardarraíles — ver H03).

Esto importa porque QUEDA es el fichero que se lee para saber qué falta: **hoy manda hacer trabajo
ya hecho y calla el que falta de verdad** (H01, H02, H03).

---

## H12 · CONFIRMADO · E17 no mide nada sobre el árbol real

E17 es Jaccard sobre 4-gramas entre nodos siempre cargados. Sobre los cinco océanos reales:

```
$ python3 -c "..."   # _shingles de cosmos.validar, pares de océanos
  descender      irreversible   0.0000
  descender      precedencia    0.0000
  ... (los 10 pares)  0.0000
  umbral E17 = 0.25
```

Cero en los diez pares. Y el solapamiento semántico **real** que sí existe queda fuera de su
alcance, porque E17 solo mira océano contra océano:

```
  solapamiento oceano <-> estrella/mar (fuera del alcance de E17), top 1:
    0.0195  oceano/verificar  vs  mar/pruebas
```

0,0195 contra un umbral de 0,25: doce veces por debajo. Un 4-grama exige cuatro palabras
consecutivas idénticas tras quitar vacías; **cualquier paráfrasis lo esquiva**. El test que la «ve
fallar» usa dos textos que comparten tiradas literales largas, no una paráfrasis.

E17 protege contra copiar y pegar. No protege contra lo que de verdad engorda un prólogo: la misma
política dicha dos veces con otras palabras.

---

## H13 · CONFIRMADO · Política duplicada entre niveles que ninguna invariante mira

Cuatro casos concretos, leídos entero el agua y las 21 estrellas:

1. `oceano/verificar` — «toda comprobación se ve fallar a propósito una vez» ≈ `mar/pruebas` — «Una
   comprobacion que nunca ha dado rojo no se distingue de una rota». **Océano ↔ mar.**
2. `oceano/secretos` — «Datos personales: lo mínimo, y nunca fuera de donde ya estaban» ≈
   `mar/custodia` — «Se recoge lo minimo, se guarda donde ya estaba». El propio mar abre diciendo
   «Distinto del oceano de secretos» y a renglón seguido lo repite. **Océano ↔ mar.**
3. `mar/accesibilidad` — «Estar en el arbol de accesibilidad no es estar disponible: se exige tamano
   y visibilidad reales» ≈ `estrella/web` — «Lo que existe en el árbol del documento no es lo que se
   ve: se exige tamaño y visibilidad reales». Casi literal. **Mar ↔ estrella.**
4. `mar/resistencia` — «el resultado es ausente, no cero» ≈ `estrella/extraccion` — «se anota vacio
   explicito: nunca se rellena con un valor plausible». **Mar ↔ estrella.**

Y frases que valdrían igual en cualquier otro nicho, o que vienen de fuera del oficio:

- `estrella/infraestructura`: «Lo desplegado y lo commiteado nunca divergen» — es una regla de Git,
  cierta en web, saas, móviles y juegos igual.
- `estrella/infraestructura`: «Produccion no se toca sin una vuelta atras escrita» ≈ `estrella/web`:
  «Antes de tocar, un punto de restauracion» ≈ `oceano/irreversible`. Tres sitios.
- `estrella/ciberseguridad`: «Se entra dando por hecho que esta mal» y «Un hallazgo sin reproduccion
  copiable es una sospecha» son la premisa invertida de GOAL §6 y una regla del arnés de origen, no
  algo cierto en ciberseguridad y falso fuera.
- `estrella/rendimiento`: «se descarta la contencion: otra cosa corriendo a la vez explica más rojos
  que una regresion» es un aprendizaje general de CI.

**Cuenta**: ~5 frases de 74 en las 21 estrellas son genéricas o duplicadas. El resto es bueno y
específico de verdad (el backtest sin comisiones de `trading`, el aislamiento demostrado atacándolo
de `saas`, el simulador que miente de `embebidos`, los ocho gigas de `modelos-locales`). Por eso la
afirmación 9 **aguanta**, pero con estas cinco fuera.

---

## H14 · CONFIRMADO · El agua no entra en el presupuesto, y hay 644 tokens que se pagan en cualquier `.py`

`contexto_inicial` (NUCLEO §2) es índice + océanos + catálogo. Los mares no aparecen. Medidos:

```
    298 tok  mar/criterio        moja= 10 globs de lenguaje (.py .js .ts .tsx .php .go .rs .rb .java .sh)
    263 tok  mar/pruebas         moja= tests/, *_test.*, *.spec.*, conftest.py
     89 tok  mar/custodia
     84 tok  mar/accesibilidad
     83 tok  mar/resistencia     moja= .py .js .ts .go .rs .sh .php
  total mares: 817
  entrada peor nicho (1.771) + criterio + resistencia = 2.152 en cualquier fichero .py
  + mar/pruebas dentro de tests/                      = 2.415
```

Formalmente es correcto —el agua entra «por `paths:` que matchea», no al arrancar— pero
`formatear_casos` publica «Entrada base 1.128 (índice + océanos + estructura)» y «quedan 2.229
tokens» sin decir que existen 817 tokens más que se activan en la primera línea de Python que se
toque. El número que decide si algo está en rojo no ve el 32% del coste real de una sesión de
código.

---

## H15 · CONFIRMADO · Diez herramientas escondidas dentro de los mares, esquivando el catálogo

`mar/criterio` y `mar/pruebas` nombran herramientas y **declaran explícitamente que no son pueblos**:

```
    mar/criterio: ast-grep, difftastic, eslint, golangci-lint, jscpd, openrewrite, ruff, serena
    mar/pruebas:  mutmut, stryker-js
```

> «Ninguno es un pueblo: son el mismo criterio aplicado a cada lenguaje.» — `mar/criterio`

Consecuencias, todas contra reglas escritas del propio GOAL:

- **No pagan catálogo**, así que el límite «5 o 6 por nicho» (UNIVERSO) tiene una puerta trasera:
  mete la herramienta en un mar y deja de contar.
- **No las ve E18** (colisión al aplanar) ni `compilar`: no acaban en `.claude/skills/`, así que un
  agente no puede invocarlas como skill.
- **La regla «una herramienta vive en un solo sitio»** deja de ser verificable, porque el validador
  solo cuenta pueblos.

No es «herramienta repetida» (la afirmación 5 aguanta: 0 nombres repetidos, 0 repos de GitHub
compartidos, 0 pares de resúmenes con similitud > 0,70 sobre 189×188/2 comparaciones). Es una vía de
escape al presupuesto, que es peor.

---

## H16 · CONFIRMADO · E08 se salta con dos palabras

La lista de vacías tiene cinco elementos: `{la, de, skill, para, sistema}`.

```
  resumen "La skill de calidad"        (nombre: calidad)  -> ['E08']   salta
  resumen "Calidad."                   (nombre: calidad)  -> ['E08']   salta
  resumen "El pais de calidad"         (nombre: calidad)  -> []        PASA
  resumen "Cosas y mas cosas varias."  (nombre: calidad)  -> []        PASA
```

`«El pais de calidad»` no informa de nada y pasa porque `el` y `pais` no están en la lista.
`«Cosas y mas cosas varias.»` pasa porque no repite el nombre. E08 detecta la tautología literal,
no el resumen vacío — y el resumen es exactamente lo que se paga en el catálogo, en cada sesión.

---

## H17 · CONFIRMADO · Los tokens del presupuesto son una unidad sin calibrar, y `metodo = "exacto"` no se ha ejecutado nunca aquí

```
$ python3 -c "import tiktoken" ; # ModuleNotFoundError
$ python3 -m cosmos medir galaxia --config galaxia.toml | head -3
  Entrada base .... 1.128 tokens   (índice + océanos + estructura, sin pueblos; estimado, ±desconocido, heurística v1)
```

`MARGEN_ERROR = None` en `cosmos/medir.py`, y el formateador lo publica como `±desconocido` — eso es
honesto y hay que reconocerlo. Pero:

- `contar_aprox` cuenta palabras Unicode y signos. Para castellano, un tokenizador BPE real produce
  bastante más por palabra. El presupuesto de **4.000** y el margen de «quedan 2.229» están
  expresados en una unidad cuyo error contra cualquier tokenizador real **no se ha medido nunca**.
- E16 —la invariante que decide rojo o verde— compara esa unidad con ese presupuesto.
- La rama `exacto` no se ha ejercitado en esta máquina: no hay tokenizador. El test que la cubre es
  el único `skipped=1` de la suite.

**Sospecha, no confirmado** (no puedo medirlo sin instalar nada, y no voy a instalar nada): el
número real en tokens de modelo para el peor nicho estará por encima de 1.771, probablemente en el
entorno de 2.500–3.500. Seguiría cabiendo en 4.000, pero el colchón publicado no es el colchón real.
Etiquetado como `no_medido`, no como aprobado.

---

## H18 · CONFIRMADO · Datos personales en un repo declarado «público-limpio»

GOAL §5: «Este repo es público-limpio y genérico. Fuera de cualquier organización, cliente o
negocio… Cero nombres de cliente, dominios de cliente, datos personales». Con `origin` apuntando a
un GitHub público. Barrí el árbol vivo y `git log -p --all` (44.584 líneas). **No hay ninguna
credencial real**: los únicos patrones duros que aparecen son los cebos del propio
`test_secretos.py` (`AKIA…EXAMPLE`, una cabecera de clave privada sin clave). Eso aguanta.

Lo que sí hay, sin transcribir nada:

1. **Metadatos de commit**: los 19 commits llevan el nombre real y **el correo corporativo de la
   agencia** en una de las identidades, y el **nombre de la máquina** de Darío en la otra
   (`git log --all --format='%an <%ae>'`). Van en cada objeto, no se borran editando ficheros.
2. **Rutas absolutas del usuario**: 12 apariciones de `<inicio>` en 6 ficheros
   versionados (`PROGRESS.md`, `QUEDA.md`, `registro/commits/universo/2026/09/montaje-tanda-1.md`,
   `registro/commits/universo/2026/09/trading-a-fondo.md`, `research/ARNES-DE-ORIGEN.md`,
   `reviews/claude-revisa-codigo-ronda1.md`). `research/HERRAMIENTAS-PROPIAS.md` ya está redactado a
   `/Users/<usuario>` — así que el criterio existe y se aplicó a medias.
3. **Correo personal de un tercero en la historia**: el commit `ef26ad4` añadió
   `research/scratch/q14_analytics.txt`, un volcado de HTML raspado de GitHub que trae una dirección
   Gmail de una persona ajena. El fichero ya no está en el árbol; **el blob sigue siendo alcanzable
   en la historia** (`git log --all -S 'kebi<…>' --oneline` lo devuelve). Tipo: correo personal de un
   tercero, procedente de una página pública. Severidad baja, pero contradice literalmente la
   afirmación 6 tal como está planteada («un secreto en un commit antiguo sigue siendo un secreto»).
4. El commit `b05e7a0` se titula «86 herramientas genericas, **verificadas sin datos de cliente**» y
   es uno de los dos que `-S` señala. La verificación que declara no se hizo sobre la historia.

**Nada de esto es una credencial.** Es identidad y datos personales en un repo que promete no
tenerlos.

---

## H19 · CONFIRMADO · Dos mecanismos para el mismo trabajo, y vocabulario ajeno cableado

La afirmación 10 **aguanta**: el puente está reescrito, no copiado.

```
project.py      (511) vs proyectar.py (552)   ratio=0.337   56/479 líneas idénticas
precommit.py    (131) vs gate.py      (148)   ratio=0.384   36/124
secret_scan.py  (361) vs secretos.py  (424)   ratio=0.469   96/373
retrieve_memory (216) vs lluvia.py    (281)   ratio=0.236   31/244
redaction.py     (13) vs etiquetas.py  (41)   ratio=0.265    5/31
```

Lo que quedó dentro, y es real:

- `puente/proyectar.py:34-35`: `FICHEROS_RAIZ = ("AGENTS.md", "CLAUDE.md")` y
  `DESTINOS = (".agents", ".claude")`. `grep -rn '\.agents\|AGENTS\.md' spec/ GOAL.md README.md
  QUEDA.md PROGRESS.md` → **vacío**. `.agents` es vocabulario de el arnés de origen que COSMOS no
  define en ninguna parte.
- Ese `DESTINOS` está **cableado**, no derivado de `compilacion.destino`. Con `galaxia.toml`
  (`destino = ".cosmos/vista-galaxia"`), `compilar` y `proyectar` escriben en sitios distintos.
- **Duplicación de responsabilidad**: `cosmos compilar` aplana con symlink + manifiesto + hash;
  `puente/proyectar.py` aplana con copia + fichero marca `.generado-por-cosmos`. Dos protocolos de
  propiedad distintos para «no pisar lo ajeno». `QUEDA.md §4` decía que `project.py` «es `compilar`
  bien hecho» — pero se migró **al lado**, no encima. Es exactamente lo que `search-first` prohíbe.

---

## H20 · CONFIRMADO · La mitad de la taxonomía no tiene un solo nodo vivo

```
$ for n in galaxia sistema-solar estrella planeta continente pais provincia ciudad pueblo casa oceano mar lago rio lluvia luna; do \
    printf "%-14s %s\n" "$n" "$(grep -rl "^cosmos: $n$" galaxia/ | wc -l)"; done
galaxia        1     planeta      0     provincia   0     casa   0
sistema-solar 21     continente   4     ciudad      0     lago   0
estrella      21     pais        56     pueblo    189     rio    0
oceano         5     mar          5     lluvia      0     luna   0
```

Ocho de los dieciséis niveles —`planeta`, `provincia`, `ciudad`, `casa`, `lago`, `rio`, `lluvia`,
`luna`— **no existen en el árbol real**. Se ejercitan solo en `ejemplo/` y en los tests sintéticos.
Consecuencias medibles: E13 no se ha probado nunca contra una luna real, E18 nunca contra una
ciudad, y el `rio` —el único nivel que el catálogo publica con resumen **siempre**, sin importar el
nicho— no tiene un solo caso vivo que valide que su coste está acotado.

No es un defecto por sí solo (un árbol joven), pero convierte «la taxonomía funciona» en «la mitad
de la taxonomía compila».

---

## H21 · CONFIRMADO · Números afirmados en los partes que ya no cuadran

Recalculé todos los números de `registro/commits/` y `reviews/`:

- `registro/commits/universo/2026/09/integracion-cosecha.md:266-270` — **cuadra exacto**
  (1.128 / 1.771 / 19.978 / 2.229 / 26 pueblos / 56 países). Es el único parte medido de verdad.
- `registro/commits/universo/2026/09/estrellas.md:7 y :78` — se contradice a sí mismo: «21
  estrellas» en el resumen y «16 estrellas» en el cuerpo.
- `registro/commits/universo/2026/09/estrellas.md:48` — cita «983 tests», que no es ninguna suite de
  este repo (aquí son 52 + 35).
- `registro/commits/universo/2026/09/migracion-puente.md:247` — «129 pueblos, 20 nichos»; hoy 189 y
  21. Es un parte histórico, así que no es un error, pero no lleva marca de «a fecha de».
- `PROGRESS.md:241 y :303` — «47 tests»; `PROGRESS.md:164` — «52 tests». El mismo fichero dice las
  dos cosas. Hoy son 52.
- `PROGRESS.md:24-25` — «4.070 tokens» y «16 estrellas» como estado; ambos superados.

**Verificación cruzada del titular** (afirmación 3): reimplementé `contexto_inicial`, el catálogo,
`resto` y `descarga` desde el texto de NUCLEO §2–§3, sin importar `cosmos.medir`:

```
entrada base      = 1128
peor nicho        = ciberseguridad 1771     (2º: trading 1701)
resto             = 18207
universo          = 19978
descarga          = 0.9114  ->  91.1 %
tokens indice     = 525 ; oceanos = 339 ; catalogo base = 264 ; catalogo peor = 907
cuerpos no-oceano que aparecen literalmente en la entrada (doble conteo): []
resumenes de sistema-solar repetidos en el catalogo: []
```

Coincide dígito a dígito. **Busqué el doble conteo de H3/B2 explícitamente y no está**: el catálogo
excluye galaxia, sistemas solares y océanos, y ningún cuerpo de nodo no-océano aparece dentro de la
cadena de entrada. La afirmación 3 **aguanta**.

---

## H22 · CONFIRMADO · `reorganizar.py` es un huérfano de 238 líneas en la raíz

```
$ grep -rn "reorganizar" --include="*.py" --include="*.toml" . | grep -v "^./reorganizar.py"
(nada)
```

Solo lo menciona `QUEDA.md:65` como sitio donde vive la constante `VECINOS`. No lo importa nadie, no
lo prueba nadie, y su producto (`usa:`) lo rechaza el validador:

```
  codigos: ['E00']
  mensaje: ["campo no permitido para sistema-solar: 'usa'"]
```

En un repo cuyo GOAL dice «se puede clonar sobre cualquier proyecto», un script de migración de un
solo uso en la raíz es superficie que se copia a todas partes.

---

## H23 · CONFIRMADO · `mutaciones.py` muta ficheros del árbol de trabajo real

`RAIZ = Path(__file__).resolve().parent.parent.parent` — la raíz del repo. `main()` hace
`ruta.write_text(mutado)` sobre `puente/secretos.py`, `puente/proyectar.py`, etc., y restaura en un
`finally`. Un `SIGKILL`, un corte de luz o un `Ctrl-C` en el peor milisegundo dejan un fichero
versionado corrompido. Por eso lo ejecuté sobre una copia (`/tmp/cosmos-adv/mut`) y no sobre el
repo. Debería trabajar sobre una instantánea, como hace su hermano `gate.py`.

---

## H24 · CONFIRMADO · Reparto desigual entre nichos: 26 contra 4

```
   26 ciberseguridad   9 infraestructura   7 juegos          6 saas
   22 trading          9 documentos        7 cientifico      6 moviles
   13 web              8 blockchain        7 extraccion      5 modelos-locales
   13 agentes-ia       8 rendimiento       6 cumplimiento    4 ingenieria-datos
   10 automatizacion   8 embebidos                           4 analitica
    7 visibilidad                                            4 audiovisual
```

`QUEDA.md` lo anota como «deuda menor». Con el catálogo por nicho ya no cuesta presupuesto, cierto —
pero sí decide qué oficios están de verdad cubiertos. Un nicho de 4 fichas no pasa el criterio 2 de
UNIVERSO («es el mejor de su hueco») porque no hay huecos suficientes cubiertos para elegir.

---

## H25 · CONFIRMADO · `compilar --nicho` destruye y rehace 176 entradas en cada cambio de nicho

```
Creadas 0; actualizadas 0; iguales 13; ajenas respetadas 0; obsoletas eliminadas 176; obsoletas preservadas 0.
```

Está en la spec (NUCLEO §5 y §7: cambiar de nicho vuelve obsoletas las demás entradas). Pero implica
que alternar entre dos nichos en la misma sesión de trabajo borra y recrea 176 symlinks cada vez, y
deja el árbol en E19 rojo para cualquiera que valide sin el flag (H09). No es un fallo; es un coste
de operación que no está documentado en ningún sitio que el usuario vaya a leer.

---

## H26 · CONFIRMADO · `README.md:52` se contradice consigo mismo dos líneas después

> «Tres piezas, y ninguna depende de que nadie se acuerde de nada:»

seguido de una tabla con **cuatro** filas —`cosmos validar`, `cosmos medir`, `cosmos generar`,
`cosmos compilar`— que son cuatro comandos que hay que teclear. Ni el número ni la afirmación se
sostienen (ver H03).

---

# Lo que intenté y aguantó

Esto es lo que da valor al resto. Cada uno es un intento real de tumbar algo, con lo que hice.

**Afirmación 3 — los números.** Reimplementé `contexto_inicial`, `catalogo`, `resto`, `universo` y
`descarga` desde el texto de NUCLEO, sin tocar `cosmos.medir`, y busqué activamente el doble conteo
que ya había mordido una vez (B2/H3). Coincide dígito a dígito y no hay doble conteo. **Aguanta.**

**Afirmación 4 — E16 contra el peor nicho.** Construí un árbol con dos oficios asimétricos (1 pueblo
contra 12), verifiqué que `base < barato < caro`, puse el presupuesto justo en `barato` —de modo que
el caso base y un nicho quepan y el otro no— y validé:

```
  base=68 barato=86 caro=332
  presupuesto=86 -> ['E16']
  E16: peor nicho caro: contexto de entrada 332 tokens > 86; excede en 246 tokens; más caros: catálogo visible (270), índice de galaxia (62)
```

Nombra el nicho culpable y el exceso exacto. **Aguanta.**

**Afirmación 5 — herramientas repetidas.** Busqué de tres formas sobre los 189 pueblos: nombres
duplicados (0), repositorios de GitHub citados por más de un pueblo (0 — porque no citan ninguno,
ver H05) y **todos** los pares de resúmenes por similitud de secuencia (17.766 comparaciones, umbral
0,70): **0 pares**. **Aguanta**, con la salvedad de H15.

**Afirmación 7 — `compilar` no borra lo ajeno.** Puse en el destino un fichero suelto, una carpeta
entera y —el caso malicioso— un directorio con **el nombre exacto de una skill que iba a compilarse**:

```
  acciones: ('AJENA .../.claude/skills/mia',)
  sobrevive ajena-suelta.md      : True
  sobrevive carpeta-ajena/x.md   : True
  'mia' sigue siendo la ajena    : True
  manifiesto entradas            : []
  validar despues                : ['E19']      <- se niega, no pisa
  2a pasada, sobrevive todo      : True True True
```

No pisa nada, no lo mete en el manifiesto, y pone el árbol en rojo en vez de fingir que compiló.
Repetí la compilación por si la segunda pasada era menos cuidadosa: idéntico. **Aguanta, y bien.**

**Casos degradados.** Árbol vacío, una sola galaxia, sistema sin pueblos, pueblo huérfano solo, un
único océano, resumen de exactamente 120 caracteres, resumen de 1 carácter, nombre con acentos,
resumen con acentos y emoji. **Ninguna excepción no controlada**; `descarga` se mantiene en `[0,1]`
o devuelve `no_definida`; el nombre con acentos lo caza E00. La invariante de NUCLEO §3 («ningún
árbol produce una descarga fuera de [0,1]») aguantó todo lo que le eché.

**La batería, en `cosmos/`.** Cinco sabotajes distintos, los cinco en rojo (H07). Intenté encontrar
un sabotaje silencioso —`peor nicho = caso base`, que es la clase de cambio que un refactor mete sin
querer— y también lo cazan: 4 tests.

**El puente, migrado.** Comparé fichero a fichero contra `<harness-de-referencia>/scripts/` (solo
lectura). Ratios de 0,24 a 0,47: está reescrito. Busqué lógica muerta y vocabulario ajeno con grep
de `arnes-de-origen|harness|pack|AGENTS.md|memory/|\.agents` y solo salieron los dos casos de H19.
**Aguanta.**

**El escáner de secretos, contra sus propios cebos.** Ejecuté `puente/tests/mutaciones.py` completo:
8/8 mutaciones en rojo, incluida M3 (subir el umbral del patrón hasta que un secreto plantado deja de
verse) y M8 (verificar el árbol sucio en vez de la instantánea). Ese trozo está bien hecho. El
agujero está en la función que esas mutaciones no tocan (H07).

**Búsqueda de credenciales reales.** `git log -p --all` completo (44.584 líneas) contra los patrones
duros: clave privada, `ghp_`/`github_pat_`, `sk-ant-`, `sk-proj-`, `AKIA`, `AIza`, `xox[baprs]-`,
`glpat-`, `npm_`, `sk_live`/`rk_test`. **Cero hallazgos reales**: las cuatro coincidencias son los
cebos construidos en tiempo de ejecución de `test_secretos.py`. La parte «cero credenciales» de la
afirmación 6 aguanta; lo que cae es «cero datos personales» (H18).

---

# Qué arreglaría, y en qué orden

1. **H01 + H02 + H09**: derivar destino y manifiesto de la raíz del árbol (la deuda que
   `galaxia.toml` ya confiesa), y meter la selección de nichos en `cosmos.toml`. Los tres agujeros
   son el mismo fallo de spec: el estado del sistema vive fuera de la configuración.
2. **H06 + H03**: `.gitignore` a `.cosmos/` y `.claude/skills/`, allowlist con motivo para los
   ejemplos de `cosecha/`, y entonces instalar el hook. Un gate rojo no es un gate.
3. **H05**: decidir qué es un pueblo. Si es una herramienta, lleva su invocación dentro. Si es una
   ficha de criterio, se llama de otra manera y GOAL deja de prometer que se ejecuta.
4. **H04**: borrar E04 y decir en NUCLEO §1 que la ruta completa ya garantiza aciclicidad. La
   invariante sobra porque el diseño la ganó; fingir que se vigila es peor que no tenerla.
5. **H10 + H11**: regenerar `spec/UNIVERSO.md` y `QUEDA.md` desde el árbol, con el mismo bloque de
   comandos que QUEDA ya trae al final. Un inventario que se escribe a mano se desincroniza — lo
   dice la propia `estrella/documentos`.
6. **H08 + H12 + H16**: las tres invariantes «blandas» (E08, E11, E17) comprueban una cadena donde
   deberían comprobar una propiedad. E11 puede evaluar la cobertura del glob; E17 puede bajar a
   3-gramas y ampliar el alcance a estrellas y mares; E08 necesita una lista de vacías de verdad.

---

*Revisión hecha con premisa invertida: 20 roturas construidas a propósito sobre árboles reales,
7 sabotajes de código sobre copias, 1 clon limpio, recuento independiente de todos los números
publicados, barrido de la historia completa de Git, y comparación fichero a fichero contra el repo
de origen. Todo lo destructivo, en `/tmp/cosmos-adv/`; el repositorio no se modificó.*
