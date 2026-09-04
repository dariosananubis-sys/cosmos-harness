# Revisión profunda de COSMOS — tercer revisor, sobre el árbol YA corregido

**Premisa:** entro después de dos revisores y de los arreglos que escribieron. Lo que se arregla
tras una revisión no está revisado, así que el foco está en el código escrito HOY para corregir a
los dos anteriores. De los **11 fallos confirmados** abajo, **7 están dentro de código escrito hoy
para corregir a los dos revisores anteriores** (B01, B02, B04, B05, B06, B07, B08), y dos de esos
siete son literalmente el mismo defecto que el fix dice haber cerrado, mudado una línea más abajo o
al único sitio que lee un humano. A eso se suman **6 sabotajes que la suite entera no ve** y que
dejan sin red la única métrica de calidad del proyecto.

## Pin de estado (obligatorio: el árbol se movió mientras revisaba)

```
$ git rev-parse HEAD                 # al empezar
6a32781be4ffea08821e36caba846a27dcf46deb
$ git status --porcelain | wc -l
       0
$ git rev-parse HEAD                 # al escribir esto
04c3edcb3c74de3047d3e35ece766d690168616d
```

Otro agente estuvo commiteando en paralelo (`939692c`, `04c3edc`: specs y tests de coherencia).
**Ningún fichero de código cambió entre los dos HEAD**, comprobado uno a uno:

```bash
cd ~/cosmos
for f in cosmos/medir.py cosmos/modelo.py cosmos/abrir.py cosmos/acertar.py \
         cosmos/compilar.py cosmos/guardarrailes.py cosmos/validar.py puente/sesion.py; do
  a=$(git show 6a32781:$f | shasum -a 256 | cut -c1-12); b=$(shasum -a 256 $f | cut -c1-12)
  echo "$f  $a  $b  $( [ "$a" = "$b" ] && echo IGUAL || echo CAMBIADO)"
done
```

```
cosmos/medir.py          307d1da19938  307d1da19938  IGUAL
cosmos/modelo.py         57b40e7517bf  57b40e7517bf  IGUAL
cosmos/abrir.py          9b1387cc2658  9b1387cc2658  IGUAL
cosmos/acertar.py        37d3b6e53b93  37d3b6e53b93  IGUAL
cosmos/compilar.py       328770b896f8  328770b896f8  IGUAL
cosmos/guardarrailes.py  88e48450f277  88e48450f277  IGUAL
cosmos/validar.py        93047c0adad5  93047c0adad5  IGUAL
puente/sesion.py         a606309255f3  a606309255f3  IGUAL
```

Todo lo de abajo vale para los dos. **Se referencia por símbolo, nunca por `fichero:línea`.**

## Método e intérpretes

- `python3` (3.14 del sistema) desde la raíz del repo. Tokenizador real: `/tmp/calib/bin/python`
  (`tiktoken 0.14.0`).
- Para no medir sobre un árbol que muta, casi todo se ejecuta sobre un tar congelado de `6a32781`:
  `git archive 6a32781 -o /tmp/rp/pristino.tar`.
- Sabotaje: `progress/revision-profunda-2026-09-02/pruebas/sabotear.py` (copia del arnés usado).
- **No se ha editado ni un fichero del repositorio** salvo este informe y su carpeta.

### Falso rojo cazado en mi propio arnés (se dice porque cambia la lectura)

La primera tanda de sabotajes dio 8/8 «CAZADO» y era mentira: mi arnés hacía `copytree` de un
directorio donde yo ya había ejecutado la suite, y arrastraba `.claude/skills/*` huérfano — los dos
mismos fallos aparecían con y sin sabotaje. Corregido extrayendo el tar limpio en cada mutación y
comparando contra una línea base medida (`M00`), no contra cero:

```
M00 BASE  tests: Ran 175 — OK (skipped=2) | puente: Ran 113 — OK
          validar: COSMOS rojo 1 errores (E19, clon sin 'arrancar': esperado)
          mutaciones: 38/38
```

---

# Resumen

| # | Hallazgo | Dónde | Estado |
|---|---|---|---|
| B01 | Una ruta ajena en un comando `Bash` **apaga G03** en silencio | fix de hoy en `_rutas_del_evento` | CONFIRMADO · crítico |
| B02 | `cosmos medir` **imprime «OK» y sale 1** sobre la misma ejecución | `formatear_casos` | CONFIRMADO · alto |
| B03 | La vista plana huérfana es **irrecuperable**, y el error manda al callejón | `compilar` | CONFIRMADO · alto |
| B04 | `escribir_atomico` **cambia los permisos** del índice de 644 a 600 | fix de hoy (F16) | CONFIRMADO · medio |
| B05 | `ZeroDivisionError` sigue vivo en `acertar`, una línea más abajo del fix de hoy | fix de hoy (caso degradado) | CONFIRMADO · medio |
| B06 | La válvula publica `E00–E20` y **rechaza `E04`** con un mensaje que se contradice | fix de hoy (`_invariantes_vigentes`) | CONFIRMADO · medio |
| B07 | Una barra doble en `--tocando` devuelve **agua distinta y plausible** | fix de hoy (H06) | CONFIRMADO · medio |
| B08 | `cerrojo` no es reentrante: la exclusión se evapora en silencio | fix de hoy (F09) | CONFIRMADO · latente |
| B09 | `acertar` revienta con traceback crudo en el caso de estreno (repo sin encargos) | `cargar_encargos` | CONFIRMADO · medio |
| B10 | `medir` da **verde sobre un árbol que no existe**; el veredicto no es trivalente | `formatear_casos` / `veredicto_de_presupuesto` | CONFIRMADO · medio |
| B11 | G05 **inventa** `exit_code: 0` y un `output` que no existía al reescribir | `despues_de_la_herramienta` | CONFIRMADO · bajo |
| T01–T05 | 5 sabotajes sobrevivieron a la suite entera | ver tabla | CONFIRMADO |
| T06 | 2 ficheros de test pierden 11 pruebas al ejecutarlos directamente | `test_un_solo_veredicto`, `test_cifras_de_las_specs` | CONFIRMADO |
| A01–A06 | Duplicación real y responsabilidades en el módulo equivocado | `cosmos/` ↔ `puente/` | CONFIRMADO |
| C01–C03 | Huecos del catálogo y del grafo `usa:` | galaxia | MEDIDO |

---

# B01 (CRÍTICO) — Una ruta ajena dentro de un comando `Bash` apaga G03, en silencio

Es **el fix de hoy**. El primer revisor encontró (H03) que `Bash` no llevaba la ruta en un campo y
el guard se apagaba con el `cwd` fuera. La corrección añadió a `_rutas_del_evento`:

```python
orden = datos.get("command")
if isinstance(orden, str):
    puntos.extend(Path(t).parent for t in re.findall(r"/[\w./-]+", orden))
```

con el comentario *«una de más solo hace mirar un directorio de más»*. **Es falso.** `decidir` no
mira todos los puntos: se queda con el **primero** que encuentre un `cosmos.toml` subiendo
(`next((c for p in _rutas_del_evento(entrada) if (c := _subiendo(p))), None)`). Así que la primera
ruta absoluta que aparezca en el texto del comando **decide contra qué repositorio se evalúa el
evento entero**, y las demás no se miran nunca.

## Medido

```bash
cd ~/cosmos

# A) control — cp a la ruta de veredicto, cwd DENTRO del repo
echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","session_id":"rp",
 "cwd":"~/cosmos",
 "tool_input":{"command":"cp /tmp/x.md ~/cosmos/galaxia/COSMOS.md"}}' \
 | python3 -m puente.sesion --formato exit2; echo "EXIT=$?"

# B) EL MISMO destino y el MISMO cwd; lo único que cambia es que el origen
#    del cp vive en otro checkout de COSMOS
echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","session_id":"rp",
 "cwd":"~/cosmos",
 "tool_input":{"command":"cp /tmp/rp/limpio/README.md ~/cosmos/galaxia/COSMOS.md"}}' \
 | python3 -m puente.sesion --formato exit2; echo "EXIT=$?"
```

```
A) COSMOS  sesion  rojo  escritura a mano sobre una ruta de veredicto
   ~/cosmos/galaxia/COSMOS.md  (protegida: …/galaxia/COSMOS.md)
   EXIT=2                                  <- deniega, correcto

B) <cero bytes de salida>
   EXIT=0                                  <- pasa
```

Repetido con un `cosmos.toml` **válido** copiado a `/tmp/rp/falso/` (sirve cualquier checkout, no
hace falta que sea otro clon del proyecto):

```
D2) cat /tmp/rp/falso/galaxia/galaxia.md > ~/cosmos/galaxia/COSMOS.md
    EXIT=0   salida = 0 bytes
E2) cat /etc/hosts                        > ~/cosmos/galaxia/COSMOS.md
    EXIT=2   COSMOS  sesion  rojo  escritura a mano sobre una ruta de veredicto
```

Depende del **orden**: si la ruta ajena va detrás del destino, el guard vuelve a denegar
(comprobado con `echo hola > …/galaxia/COSMOS.md  # ver /tmp/rp/limpio/spec/NUCLEO.md` → EXIT=2).
Es decir: la autoridad del guard la elige el texto del comando.

Y no es solo G03: la misma desviación se lleva por delante G04 (lecturas exigidas), porque
`antes_de_la_herramienta` recibe la `config` del repositorio equivocado.

Un `cosmos.toml` **roto** sí falla cerrado (probado: deniega con «el guard no pudo evaluar»). El
agujero necesita un `cosmos.toml` **válido**, que es el caso corriente en cuanto hay dos checkouts
—y esta máquina tenía cuatro mientras revisaba.

## Lo que lo hace evitable, y por eso duele

El propio fichero ya tenía, 200 líneas más arriba, un analizador de shell que sabe exactamente qué
escribe una orden. Se reimplementó con una regex en vez de reusarlo:

```bash
python3 -c "
import sys; sys.path.insert(0,'.')
from puente.sesion import ordenes, objetivos_de_escritura, _rutas_del_evento
cmd='cp /tmp/rp/limpio/README.md ~/cosmos/galaxia/COSMOS.md'
print('objetivos_de_escritura:', [objetivos_de_escritura(o) for o in ordenes(cmd)])
print('_rutas_del_evento    :', _rutas_del_evento({'tool_input':{'command':cmd},'cwd':'~/cosmos'}))"
```

```
objetivos_de_escritura: [['~/cosmos/galaxia/COSMOS.md']]     <- exactamente el destino
_rutas_del_evento    : [/tmp/rp/limpio,                                        <- gana este
                        ~/cosmos/galaxia,
                        ~/cosmos]
```

**Arreglo:** en `_rutas_del_evento`, para `Bash`, usar `ordenes()` + `objetivos_de_escritura()` en
lugar de la regex; y en `decidir`, cuando varios puntos resuelvan a repositorios distintos, denegar
por ambigüedad en vez de quedarse con el primero (es la misma doctrina que ya se aplica al
`cosmos.toml` roto). El test que falta es el caso B literal.

---

# B02 (ALTO) — `cosmos medir` imprime «OK, quedan N tokens» y sale 1, en la misma ejecución

El commit `79c502d` se titula *«un solo juez del presupuesto»* y su docstring dice: *«Tres
comparaciones sobre el mismo árbol, publicadas con la misma etiqueta… el juez vive en un solo
sitio»*. Quedó una cuarta, y es **la que lee la persona**: `formatear_casos` calcula su propio
veredicto en línea (`evaluado = evaluada.entrada_con_agua; if evaluado <= evaluada.presupuesto`) y
además lo calcula sobre `evaluada` (= la selección de nichos), mientras `veredicto_de_presupuesto`
—el que decide el código de salida y E16— lo calcula sobre `casos.peor`.

```bash
cd ~/cosmos
# El toml va con rutas ABSOLUTAS: `--config` fuera del repo resuelve `arbol` contra
# el directorio del propio fichero de configuración, no contra el repo (ver B10).
sed -e 's/entrada = 4000/entrada = 3000/' \
    -e 's#arbol = "galaxia"#arbol = "~/cosmos/galaxia"#' \
    -e 's#indice = "galaxia/COSMOS.md"#indice = "~/cosmos/galaxia/COSMOS.md"#' \
    -e 's#registro = "registro"#registro = "~/cosmos/registro"#' \
    cosmos.toml > /tmp/rp/c3000abs.toml

python3 -m cosmos medir --config /tmp/rp/c3000abs.toml --nicho embebidos | grep -E "Peor con agua|Presupuesto"
python3 -m cosmos medir --config /tmp/rp/c3000abs.toml --nicho embebidos >/dev/null 2>&1; echo "EXIT=$?"
```

```
  Peor con agua ... 2.907 tokens   (el nicho activo + agua condicional)
  Presupuesto ..... 3.000     OK, quedan 93 tokens en el nicho activo con agua
EXIT=1
```

Y por la vía que originó el fallo original (`[nichos] activos` en el `cosmos.toml`), sin ningún
flag, sobre HEAD **sin sabotear**:

```bash
cd ~/cosmos    # (ejecutado sobre el tar congelado de 6a32781)
sed 's/entrada = 4000/entrada = 3000/; s/activos = \[\]/activos = ["juegos"]/' cosmos.toml > c-juegos.toml
python3 -m cosmos medir  --config c-juegos.toml | grep Presupuesto
python3 -m cosmos medir  --config c-juegos.toml >/dev/null 2>&1; echo "medir EXIT=$?"
python3 -m cosmos validar --config c-juegos.toml >/dev/null 2>&1; echo "validar EXIT=$?"
```

```
  Presupuesto ..... 3.000     OK, quedan 126 tokens en el nicho activo con agua
medir EXIT=1
validar EXIT=1
```

La línea que dice «OK» y el código de salida que dice «no» salen del mismo proceso. Es literalmente
el defecto que el commit declara cerrado, en el único de los cuatro sitios que un humano lee.

Agravante: la etiqueta miente dos veces. Con `--nicho`, la fila se sigue llamando **«Peor con
agua»** describiendo un nicho que no es el peor, y la fila «Peor nicho» publica `entrada` **sin**
agua mientras el veredicto se cobra **con** agua.

**Arreglo:** `formatear_casos` tiene que llamar a `veredicto_de_presupuesto(resultado, …)` y
publicar su `como_linea()`. Si se quiere además informar del nicho activo, en una fila aparte y con
otro nombre.

---

# B03 (ALTO) — La vista plana huérfana no se puede recuperar, y el mensaje de error empuja al callejón

Mismo patrón que el `cerrojo` rancio que hoy se arregló (*«un cerrojo que no se puede abrir no
protege nada, solo rompe el repositorio»*), vivo en `compilar` y sin tocar.

```bash
rm -rf /tmp/rp/orf2 && mkdir -p /tmp/rp/orf2
cd ~/cosmos && git archive 6a32781 | tar -x -C /tmp/rp/orf2
cd /tmp/rp/orf2
python3 -m cosmos compilar --config ejemplo.toml | tail -1   # estado normal
rm -rf .cosmos                                               # se limpia un artefacto generado
python3 -m cosmos validar  --config ejemplo.toml | head -5
python3 -m cosmos compilar --config ejemplo.toml | tail -3
python3 -m cosmos validar  --config ejemplo.toml | head -3
python3 -m cosmos arrancar --config ejemplo.toml | tail -1
```

```
Creadas 2; … ajenas respetadas 0; …
COSMOS  rojo  1 errores
E19  …/.claude/skills
     vista plana desincronizada: falta el manifiesto …/.cosmos/compilado.json
     Ejecuta 'cosmos compilar'; no edites la vista plana a mano.     <- la receta
…
COSMOS  rojo  2 errores                                             <- tras seguirla: PEOR
E19  …/.claude/skills  vista plana desincronizada: probar-salida: no figura en el manifiesto
E19  …/.claude/skills  vista plana desincronizada: revisar-formato: no figura en el manifiesto
COSMOS  arrancar  rojo
```

Sin el manifiesto, `compilar` clasifica sus propias entradas como **ajenas** (`ajenas_nombres =
existentes - set(antiguas)`) y las respeta para siempre; no hay flag de adopción
(`cosmos compilar --help`: `--config --modo --destino --seco --nicho`, ninguno sirve). El único
camino de vuelta es borrar a mano lo que el mensaje prohíbe tocar a mano.

Y se llega solo: **la suite de tests deja ese estado en el repositorio**. Un clon limpio no trae
`.claude/skills` ni `.cosmos`; tras `python3 -m unittest discover -s tests -t .` aparecen los dos
enlaces y `.cosmos/compilado.json`. A partir de ahí, cualquiera que limpie `.cosmos/` (ambos están
en `.gitignore`, así que «son generados, se pueden borrar») deja el repositorio en el callejón.

**Arreglo:** que la ausencia del manifiesto sea un caso distinto del de una entrada ajena — si el
destino existe y no hay manifiesto, `compilar` puede reconstruirlo comparando hashes, o al menos
ofrecer `--adoptar`. Y que la suite no escriba en el árbol de trabajo (`destino` a un temporal).

---

# B04 (MEDIO) — `escribir_atomico` cambia los permisos del índice de 644 a 600

Es el fix F16 de hoy: `escribir_indice` era un `write_text` y pasó a temporal + `fsync` +
`os.replace`. `tempfile.mkstemp` crea con `0600` y `os.replace` **traslada el modo del temporal**,
así que cada regeneración estrecha los permisos del fichero que se commitea.

```bash
rm -rf /tmp/rp/b04 && mkdir -p /tmp/rp/b04
cd ~/cosmos && git archive HEAD | tar -x -C /tmp/rp/b04
cd /tmp/rp/b04
ls -l galaxia/COSMOS.md | awk '{print $1, $NF}'
python3 -m cosmos generar >/dev/null
ls -l galaxia/COSMOS.md | awk '{print $1, $NF}'
```

```
-rw-r--r--@ galaxia/COSMOS.md      <- antes
-rw-------@ galaxia/COSMOS.md      <- después de 'cosmos generar'
```

(El comando es idempotente en el sentido malo: una vez estrechado, se queda así. Por eso la
reproducción parte de un `git archive` limpio.)

```
antes  : 0o644     despues: 0o600     fichero nuevo: 0o600  (con umask normal sería 0o644)
```

Afecta igual al manifiesto de `compilar`, que usa una copia byte a byte de la misma función (ver
A01). `write_text` conservaba el modo; la versión «más segura» lo pierde. En un contenedor de CI
que corre `generar` como root y lee la vista como otro usuario, o en un checkout compartido, el
índice deja de leerse. Ninguna prueba mira el modo: `test_reemplaza_la_entrada_del_directorio_y_no_el_fichero`
comprueba que la escritura atraviesa un destino `0o444`, y no comprueba con qué modo queda.

**Arreglo:** `os.chmod(temporal, 0o666 & ~umask)` o copiar el modo del destino previo si existe,
antes del `os.replace`.

---

# B05 (MEDIO) — El `ZeroDivisionError` que se arregló hoy sigue vivo una línea más abajo

`6a32781` añadió a `formatear_contraste` la guarda de `c.validacion.total`, con el comentario
*«`brecha` y `como_dict` ya comprobaban `.total`; esta era la única de las tres que no»*. El
divisor de la línea siguiente, `c.ajuste.total`, se quedó sin guarda.

```bash
cd ~/cosmos && echo '{}' > /tmp/rp/dict.json
python3 -m cosmos acertar --encargos /tmp/rp/dict.json 2>&1 | tail -3
```

```
    aj = 100 * c.ajuste.aciertos / c.ajuste.total
         ~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~
ZeroDivisionError: division by zero
```

`formatear` (la ruta de un solo conjunto) **sí** lo trata bien («sin encargos que puntuar»): el
módulo conoce el caso y la ruta de contraste no lo usa.

---

# B06 (MEDIO) — La válvula anuncia `E00–E20`, rechaza `E04`, y el mensaje se contradice a sí mismo

El fix de hoy sustituyó `range(20)` por `codigos_comprobados()` para que E20 tuviera válvula. Lo
consiguió, y dejó dos cabos.

```bash
cd ~/cosmos && python3 -c "
from cosmos.validar import rango_comprobado, codigos_comprobados
from cosmos.guardarrailes import normalizar_codigo
print('rango publicado:', rango_comprobado())
print('E04 existe?    :', 'E04' in codigos_comprobados())
for c in ('E20','E04'):
    try: print(c,'->',normalizar_codigo(c))
    except Exception as e: print(c,'-> ERROR:',e)"
```

```
rango publicado: E00–E20
E04 existe?    : False
E20 -> E20
E04 -> ERROR: código desconocido: 'E04'; se esperaba una invariante (E00..E19) o un
              guardarraíl de sesión (G01/G02/G03/G04/G05)
```

Dos cosas, las dos del mismo fix:

1. `rango_comprobado()` publica un **intervalo** sobre un conjunto con hueco (E04 se retiró): la
   ayuda del CLI promete un código que la válvula rechaza.
2. El mensaje de error de `normalizar_codigo` sigue con la cadena **escrita a mano `E00..E19`** —
   exactamente lo que el fix existía para eliminar. Resultado: rechaza `E04` diciendo que esperaba
   algo del rango `E00..E19`, que contiene `E04`; y acepta `E20`, que ese mismo texto no nombra.

**Arreglo:** el mensaje se construye con `codigos_comprobados()`; y para publicar, un enumerado o
un rango con el hueco explícito, no `primero–último`.

---

# B07 (MEDIO) — Una barra doble en `--tocando` devuelve agua distinta, plausible y equivocada

El fix de hoy cerró el caso de la ruta absoluta (H06 del primer revisor) relativizándola contra
`arbol.raiz` y su padre. Quedaron abiertas las demás formas no canónicas, y la peor no devuelve
vacío —que al menos se nota— sino **otra respuesta creíble**.

```bash
cd ~/cosmos
for p in "tests/test_x.py" "tests//test_x.py" "./tests/test_x.py" "~/x.py"; do
  echo -n "[$p] -> "
  python3 -m cosmos abrir web --tocando "$p" --json \
   | python3 -c "import sys,json;print([a['nombre'] for a in json.load(sys.stdin)['agua']])"
done
```

```
[tests/test_x.py]   -> ['mar/criterio', 'mar/pruebas', 'mar/resistencia', 'mar/revision']
[tests//test_x.py]  -> ['mar/pruebas']                       <- pierde 3 de 4 mares
[./tests/test_x.py] -> ['mar/criterio', 'mar/pruebas', 'mar/resistencia', 'mar/revision']
[~/x.py]            -> ['mar/criterio', 'mar/resistencia', 'mar/revision']   <- fichero del HOME, tratado como del proyecto
```

Mecanismo: `_glob_a_regex("**/*.py")` produce `(?:[^/]+/)*[^/]*\.py\Z`, y el componente vacío de
`tests//test_x.py` impide que `[^/]*` llegue al final; `**/tests/**` termina en `.*` y sí casa. Así
que el agua que se pierde es justo la de los criterios de código, y la que queda hace que la
respuesta parezca correcta.

`~/x.py` es el caso simétrico: no empieza por `/`, así que no se relativiza ni se rechaza, y un
fichero del HOME recibe el agua del proyecto.

**Arreglo:** normalizar con `PurePosixPath(...).as_posix()` (o `os.path.normpath`) antes de casar,
y `expanduser()` antes de decidir si es absoluta. Es el mismo principio que ya se aplicó a `./`.

---

# B08 (LATENTE, confirmado) — `cerrojo` no es reentrante: la exclusión desaparece sin decirlo

La condición de robo es `pid is not None and pid != os.getpid() and _proceso_vivo(pid)`. El
`!= os.getpid()` convierte el propio cerrojo en «rancio» para el mismo proceso.

```bash
cd ~/cosmos && python3 -c "
import tempfile, pathlib
from cosmos.modelo import cerrojo
with tempfile.TemporaryDirectory() as t:
    lock = pathlib.Path(t,'x.lock')
    with cerrojo(lock):
        print('exterior lo tiene:', lock.is_file())
        with cerrojo(lock):
            print('  interior TAMBIEN lo tomo:', lock.is_file())
        print('al salir el interior, el exterior se ha quedado sin cerrojo:', not lock.is_file())"
```

```
exterior lo tiene: True
  interior TAMBIEN lo tomo: True
al salir el interior, el exterior se ha quedado sin cerrojo: True
```

Hoy no explota porque los dos llamantes usan rutas distintas (`escribir_indice` →
`.cosmos-generar.lock`, `compilar` → `compilar.lock`). Es una mina: el día que `compilar` llame a
`generar` bajo el mismo cerrojo —o que se unifiquen las dos rutas, que es lo natural— la exclusión
mutua desaparece y **nada se pone rojo** (`test_escritura_segura` no tiene caso reentrante).

Hermano no confirmado del mismo sitio, se declara como **sospecha**: entre `os.open(O_EXCL)` y la
escritura del PID el fichero está vacío, y un fichero vacío se clasifica como rancio
(`test_un_cerrojo_ilegible_tambien_se_retoma` consagra ese comportamiento). Un segundo proceso que
lea en esa ventana roba un cerrojo vivo. No he conseguido provocarlo de forma determinista, así que
va etiquetado: **sospecha, mecanismo leído, no medido**.

---

# B09 (MEDIO) — `cosmos acertar` revienta con traceback crudo en el caso de estreno

`spec/NUCLEO.md` describe COSMOS como algo que se clona sobre otro proyecto, y `rio/acertar` lo
anuncia con `invoca: python3 -m cosmos acertar`. En un proyecto sin `pruebas/encargos.json` —es
decir, en todos menos éste— el río documentado hace esto:

```bash
cd /tmp/rp/vacio && PYTHONPATH=/tmp/rp/limpio python3 -m cosmos acertar 2>&1 | tail -3
```

```
    return io.open(self, mode, buffering, encoding, errors, newline)
FileNotFoundError: [Errno 2] No such file or directory: 'pruebas/encargos.json'
```

La misma familia, medida en el mismo sitio (`cargar_encargos` no valida nada de lo que lee):

```
--encargos con JSON inválido        -> json.decoder.JSONDecodeError (traceback), EXIT=1
--encargos con un dict sin 'espera' -> KeyError: 'espera'          (traceback), EXIT=1
```

Contrasta con el trato que sí recibe el fichero de validación, cuidado hoy y bien:
`--validacion /ruta/que/no/existe --minimo 70` da un mensaje entero y `EXIT=2`, sin caer al
conjunto de ajuste. La lección se aplicó a un fichero de los dos.

---

# B10 (MEDIO) — El presupuesto no distingue «cabe» de «no había nada que medir»

Sobre un árbol sin un solo nodo:

```bash
cd /tmp/rp/vacio && PYTHONPATH=/tmp/rp/limpio python3 -m cosmos medir
```

```
  Entrada base .... 0 tokens
  Universo ........ 0 tokens
  Descarga ........ no_definida                                    <- correcto
  Presupuesto ..... 4.000     OK, quedan 4.000 tokens en el peor caso con agua
```

`descarga` sí es trivalente y publica `no_definida`; `Veredicto.cabe` no, y `0 <= 4000` sale
«OK». Es el modo de fallo que abre el docstring de `acertar.py` —*«la manera más barata de pasar el
presupuesto es escribir resúmenes peores»*, cuyo límite es el árbol vacío— con la métrica del coste
diciendo que todo va bien. El módulo ya conoce el patrón y lo aplica a una cifra y no a la otra.

El caso alcanzable de verdad no es el árbol vacío, es el árbol **que no está**. `--config` con un
fichero fuera del repositorio resuelve `arbol` contra el directorio del propio `.toml`, así que basta
una configuración movida de sitio:

```bash
cd ~/cosmos
sed 's/entrada = 4000/entrada = 3000/' cosmos.toml > /tmp/rp/c3000.toml   # rutas RELATIVAS
ls -d /tmp/rp/galaxia                                                     # no existe
python3 -m cosmos medir   --config /tmp/rp/c3000.toml | grep -E "Peor con agua|Descarga|Presupuesto"
python3 -m cosmos medir   --config /tmp/rp/c3000.toml >/dev/null 2>&1; echo "medir   EXIT=$?"
python3 -m cosmos validar --config /tmp/rp/c3000.toml >/dev/null 2>&1; echo "validar EXIT=$?"
```

```
ls: /tmp/rp/galaxia: No such file or directory
  Peor con agua ... 0 tokens   (el peor caso + agua condicional)
  Descarga ........ no_definida
  Presupuesto ..... 3.000     OK, quedan 3.000 tokens en el peor caso con agua
medir   EXIT=0          <- verde sobre un directorio que no existe
validar EXIT=1
```

`medir` no comprueba `config.arbol.is_dir()` —`puente.sesion.decidir` sí lo hace y lanza
`ErrorSesion`— y publica el veredicto tranquilizador. `validar` discrepa, como en B02.

Bien resuelto, para que conste: `estado` y `mapa` sobre el árbol vacío responden con sentido, y
`validar`/`generar`/`compilar` dan E05 y salen 1.

---

# B11 (BAJO) — G05 inventa campos al reescribir la salida

`despues_de_la_herramienta` reconstruye la respuesta como
`{"output": salida, "exit_code": decision.codigo_salida}` y `_respuesta` toma
`respuesta.get("exit_code", respuesta.get("exitCode", 0))`. Si la respuesta no es un diccionario, o
no traía `exit_code`, el valor por defecto tranquilizador es **0**.

```bash
cd ~/cosmos
echo '{"hook_event_name":"PostToolUse","tool_name":"Bash","session_id":"rp",
 "cwd":"~/cosmos",
 "tool_response":"AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"}' \
 | python3 -m puente.sesion --formato json
```

```
"updatedToolOutput": {"output": "[REDACTADO: clave secreta AWS]", "exit_code": 0}
```

El `exit_code: 0` no lo dijo nadie: lo pone el `.get(..., 0)`. Y con una respuesta que solo traía
`stderr`, la reescritura **crea** un `output` con el texto del stderr, de modo que el modelo lee
como salida estándar algo que fue error. Un `exit_code` real sí se conserva (probado con 1 y 2).

Es la regla 14 del propio arnés: lo que no se ha observado se publica como «no lo sé», nunca con el
valor por defecto cómodo.

---

# Tests que no prueban lo que dicen — 24 sabotajes, 6 supervivientes

Método: sobre un tar limpio de `6a32781` por mutación, se cambia UNA cosa en el código y se corre
la suite entera (`tests`, `puente/tests`, `puente/tests/mutaciones.py`, `cosmos validar`),
comparando contra la línea base `M00`. Arnés copiado en
`progress/revision-profunda-2026-09-02/pruebas/sabotear.py`; se reproduce con
`python3 pruebas/sabotear.py M15`.

| id | Sabotaje | Resultado |
|---|---|---|
| M01 | el juez deja de sumar el agua | CAZADO |
| **M02** | **el juez cobra sobre la selección, no sobre el peor nicho** | **SOBREVIVE** |
| **M03** | **el «peor» nicho pasa a ser el más barato (`max`→`min`)** | **SOBREVIVE** |
| M04 | `escribir_atomico` deja de ser atómico | CAZADO |
| M05 | `escribir_atomico` deja de hacer `fsync` | SOBREVIVE *(honesto: no se puede medir en proceso)* |
| M06 | el cerrojo deja de respetar un proceso vivo | CAZADO |
| M07 | el cerrojo rancio deja de recuperarse | CAZADO |
| M08 | `agua_que_moja` devuelve siempre vacío | CAZADO |
| M09 | ruta fuera del proyecto vuelve a devolver agua vacía | CAZADO |
| M10 | `formatear_contraste` vuelve a dividir por cero | CAZADO |
| M11 | la válvula vuelve a `range(20)` (E20 sin válvula) | CAZADO |
| M12 | `_rutas_del_evento` deja de mirar el comando de `Bash` | CAZADO |
| M13 | `PreToolUse` malformado vuelve a pasar en silencio | CAZADO |
| **M14** | **`acertar` vuelve a puntuar sin los 21 oficios** | **SOBREVIVE** |
| **M15** | **`_acierta` dice que sí a todo** | **SOBREVIVE** |
| **M16** | **se apaga el recorte de sufijos de `_raiz`** | **SOBREVIVE** |
| M17 | índice y catálogo pierden su factor propio (F01) | CAZADO |
| M18 | E20 sale de `COMPROBACIONES` | CAZADO |
| M19 | la estrella vuelve a engancharse por nombre suelto | CAZADO |
| M20 | la lluvia vuelve a inflar la descarga sola | CAZADO |
| M21 | el cerrojo deja de ser exclusivo (`O_EXCL` fuera) | CAZADO |
| M22 | G03 deja de proteger las rutas de veredicto | CAZADO |
| M23 | `rango_comprobado` vuelve a una cadena a mano | CAZADO |
| M24 | el aviso de validación VACÍA desaparece | CAZADO |

**18 cazados, 6 supervivientes.** El grueso de la red está bien tejido; los agujeros están
concentrados en dos sitios, y los dos importan.

## T01 — `cosmos acertar` no tiene NI UNA prueba: puede publicar 100 % y todo sigue verde

M14, M15 y M16 son las tres del mismo módulo. La más contundente:

```bash
cd /tmp/rp/trabajo/M15   # unico cambio: 'def _acierta(...)' -> 'return True'
python3 -m cosmos acertar | head -5
python3 -m unittest discover -s tests -t . 2>&1 | grep -E '^(Ran|OK|FAILED)'
```

```
  Ajuste ......... 50/50 (100 %)   los encargos que SÍ se miran al trabajar
  Validación ..... 20/20 (100 %)   YA MIRADO: es una segunda cifra de ajuste

Ran 175 tests in 46.768s
OK (skipped=2)
```

Y en el otro extremo, con `_lineas_del_catalogo` recortada (M14, que es **el fallo exacto que
`a4f880e` arregló**: «la métrica medía un recorte del árbol»): `0/50 (0 %)` y `0/20 (0 %)`, suite
verde. La contra-métrica —la única cifra de calidad que tiene el proyecto, la que existe para que
Goodhart no se coma el presupuesto— puede decir cualquier número entre 0 y 100 sin que nada chille,
y la regresión que ya ocurrió una vez no tiene canario.

Lo único que hay es `tests/test_acertar_contraste.py`, que cubre el **formateo** del contraste (el
caso quemado y el vacío), no la puntuación.

**Qué falta, y es barato:** un árbol de juguete de 3 nodos con 3 encargos cuya respuesta esté
fijada a mano, y tres aserciones: (1) un encargo cuya palabra solo está en el resumen del oficio
acierta —canario de M14—; (2) un encargo cuya respuesta correcta NO es la primera devuelve
`acierta=False` —canario de M15—; (3) «encuentre»/«encuentren» puntúan igual —canario de M16—.

## T02 — Nada afirma que «el peor nicho» sea el peor

M03 cambia `max` por `min` en `medir_casos` y la suite entera se queda verde. El comando publica:

```
  Peor nicho ...... 1.528 tokens   (juegos, 7 pueblos)     <- el mas BARATO, con etiqueta de peor
  Presupuesto ..... 4.000     OK, quedan 1.126 tokens en el peor caso con agua
```

Las dos pruebas que parecen cubrirlo son tautologías: `test_juzga_el_peor_caso_con_agua_y_no_la_entrada_pelada`
afirma `v.evaluado == casos.peor.entrada_con_agua` y `test_dice_de_que_nicho_habla` afirma
`v.nicho == casos.peor_nicho` — las dos comparan el resultado con la misma variable de la que sale.
Afirman que el código es igual a sí mismo. La propiedad que hay que afirmar es
`peor.entrada >= max(medir_arbol(nicho).entrada for nicho in nichos)`.

Es la regla 13 del arnés («el test afirma lo medido, no lo deseado») en su forma más cara: aquí la
promesa del presupuesto es *«cualquier sesión cabe»*, y sin esa aserción la promesa no está
cubierta por nada.

## T03 — El test del «único juez» no ejercita la configuración que produjo el fallo

M02 cambia `cabe=peor.…` por `cabe=casos.evaluada.…` y sobrevive: las pruebas comparan `.evaluado`
(que no toqué) y nunca `.cabe`, que es el campo que decide el código de salida y E16.

Y `LosTresLlamantesDicenLoMismo.test_validar_y_medir_coinciden_en_el_veredicto` corre con el
`cosmos.toml` del repo, donde `[nichos] activos = []` — o sea, **con la selección desactivada, que
es justo la condición bajo la cual el fallo original no puede aparecer**. Ningún test end-to-end
pone `activos` con contenido:

```bash
grep -rn "activos" tests/ puente/tests/ | grep -v "saltos\|estado_saltos\|nichos_de_configuracion"
```

```
tests/test_un_solo_veredicto.py:8:   (solo el docstring lo menciona)
```

Con `activos = ["juegos"]` y el sabotaje M02, `medir` sale 0 y `validar` sale 1 sobre el mismo
árbol. Es exactamente la divergencia que el commit dice haber eliminado, reintroducible sin poner
un solo test en rojo.

## T04 — El otro grep-como-contrato

`test_el_guard_de_sesion_usa_el_mismo_juez` comprueba que la **cadena**
`"veredicto_de_presupuesto(medicion, config.entrada)"` aparece en el texto de `puente/sesion.py`.
Un grep no distingue «no existe» de «existe con otro nombre» ni de «existe y además hay otro juez
al lado» — y de hecho hay otro juez al lado, en `formatear_casos` (B02), que el test no ve porque
mira otro fichero. Lo que hay que afirmar es la igualdad de veredictos entre los cuatro llamantes
sobre el mismo árbol, no la presencia de una cadena.

## T05 — Dos ficheros pierden 11 pruebas si se ejecutan directamente

`unittest.main()` está escrito **a media altura** del fichero, con clases definidas después:

```bash
cd ~/cosmos
for f in tests/*.py puente/tests/*.py; do
  n=$(grep -n "unittest.main()" $f | cut -d: -f1); u=$(grep -n "^class " $f | tail -1 | cut -d: -f1)
  [ -n "$n" ] && [ "$n" -lt "$u" ] && echo "  $f: main() en $n, ultima clase en $u"
done
```

```
  tests/test_cifras_de_las_specs.py: main() en 133, ultima clase en 245
  tests/test_un_solo_veredicto.py:   main() en 81,  ultima clase en 84
```

(Los números de línea son de `04c3edc`, el HEAD del momento de escribir; `test_cifras_de_las_specs`
creció hoy con las clases de coherencia. El defecto ya estaba en `6a32781` en los dos ficheros.)

Medido, con y sin descubrimiento:

```
PYTHONPATH=. python3 tests/test_un_solo_veredicto.py    -> Ran 5 tests   OK
python3 -m unittest tests.test_un_solo_veredicto        -> Ran 7 tests   OK
PYTHONPATH=. python3 tests/test_cifras_de_las_specs.py  -> Ran 4 tests   OK
python3 -m unittest tests.test_cifras_de_las_specs      -> Ran 13 tests  OK
```

**11 pruebas desaparecen sin decir nada** y las dos invocaciones terminan en `OK`. El CI usa
descubrimiento, así que hoy no oculta un rojo; pero un `python3 tests/test_X.py` —la forma natural
de iterar sobre un test— da un verde que no ha ejercitado dos tercios del fichero. Y el fichero más
afectado es el que existe para que las cifras de las specs no envejezcan.

---

# Arquitectura: duplicación real y responsabilidades en el módulo equivocado

## A01 — Tres escritores atómicos, dos de ellos byte a byte idénticos

El commit de hoy dice de `escribir_atomico`: *«Vivía solo en `compilar`, y el índice lo necesita
igual»*. No se movió: se **copió**.

```bash
cd ~/cosmos && python3 -c "
import re, pathlib, hashlib
def cuerpo(f, n):
    t = pathlib.Path(f).read_text()
    m = re.search(rf'def {n}\(ruta: Path, contenido: str\) -> None:(.*?)\n\ndef ', t, re.S)
    return re.sub(r'^\s*\"\"\".*?\"\"\"\n','',m.group(1),flags=re.S).strip()
a = cuerpo('cosmos/modelo.py','escribir_atomico'); b = cuerpo('cosmos/compilar.py','_escribir_atomico')
print('identicos:', a==b, '|', hashlib.sha256(a.encode()).hexdigest()[:16], hashlib.sha256(b.encode()).hexdigest()[:16])"
```

```
identicos: True | 4d73c212e60358a3 4d73c212e60358a3
```

Y hay un tercero distinto y más flojo, `puente/sesion._escribe_atomico`: sin `fsync`, con
`with_suffix` en lugar de `mkstemp`. Es el que escribe las **marcas de lectura de G04**, o sea, el
estado del que depende un guardarraíl.

Consecuencia inmediata: el arreglo de B04 (permisos) hay que aplicarlo en dos sitios y es seguro que
uno se quedará atrás — que es exactamente cómo nació este hallazgo.

**Propuesta:** una sola función pública en `cosmos/modelo` con firma `(ruta, contenido: str | bytes)`,
usada por `compilar`, `generar` y `puente/sesion`. Coste: ~20 líneas y un import. Rompe si no se
hace: la próxima corrección de escritura segura se aplica al 33 % de los llamantes.

## A02 — Cuatro normalizadores de texto, tres casi iguales

```bash
grep -n "unicodedata.normalize" cosmos/*.py puente/*.py
```

```
cosmos/acertar.py:133   NFKD + lower + [a-z0-9]{2,} + recorte de sufijos
puente/lluvia.py:57     NFKD + lower + [a-z0-9]{2,}                      <- 'normalizar', publica
puente/secretos.py:374  NFKD + lower                                     (uso propio)
cosmos/validar.py:155   NFD  + casefold                                  (devuelve str, otro contrato)
```

`acertar._normalizar` dice en su docstring que usa *«la misma normalización que usa la búsqueda de
memoria»*: es la de `puente/lluvia.normalizar` **más** el recorte de sufijos. La afirmación es medio
verdadera y las tres implementaciones divergirán. `puente/lluvia.normalizar` ya es pública: lo
honesto es `_normalizar = lambda t: [_raiz(p) for p in normalizar(t)]`.

## A03 — El analizador de shell no debería vivir dentro del módulo de guardarraíles

`puente/sesion.py` son 1.125 líneas con cinco guardarraíles, el cableado de hooks, el estado de
sesión **y** un analizador de línea de órdenes (`ordenes`, `_piezas`, `programa`,
`objetivos_de_escritura`, ~150 líneas con su propia tabla de verbos que escriben). Dos consecuencias
medidas:

1. **B01 existe porque no se reusó lo que ya estaba en el mismo fichero.** Quien escribió
   `_rutas_del_evento` no vio `objetivos_de_escritura` 200 líneas más arriba, y resolvió con una
   regex un problema que ya estaba resuelto bien.
2. El analizador es la pieza más fuzzable del proyecto (entrada adversarial por definición) y no se
   puede ejercitar sola sin arrastrar el resto del módulo.

**Propuesta:** `puente/shell.py` con `ordenes`/`programa`/`objetivos_de_escritura` y su tabla, más
un test de propiedades. Coste: un `git mv` de bloques y ~10 imports. Rompe si no se hace: cada
agujero de G03 se vuelve a parchear con una regex nueva al lado, que es como se llegó a «la séptima
forma de esquivar G03» que el propio código nombra.

## A04 — `formatear_casos` decide, y no debería

Ya está en B02. La forma general: el módulo de presentación calcula veredictos. Todo lo que en
`medir.py` es `if X <= presupuesto` fuera de `veredicto_de_presupuesto` es, por construcción, un juez
más. Un test de arquitectura de tres líneas lo fija para siempre: `grep` de `<= .*presupuesto` en
`cosmos/` debe dar exactamente una ocurrencia — y sí, aquí un grep vale, porque lo que se afirma es
la ausencia de una forma sintáctica, no la existencia de un comportamiento.

## A05 — La suite escribe en el árbol de trabajo

Correr los tests crea en la raíz del repositorio `.claude/skills/probar-salida`,
`.claude/skills/revisar-formato`, `.cosmos/compilado.json` y `.cosmos/cierres.log` (medido sobre un
clon limpio: antes no existen, después sí). Están en `.gitignore`, así que no ensucian `git status`
— y por eso nadie lo ha visto. Es la causa de B03 y la razón de que el verde local dependa de estado
no versionado.

**Propuesta:** que `tests/test_cli` y `test_validador` compilen contra un `TemporaryDirectory`
(`--destino`), no contra el repo.

## A06 — `acertar` ya contiene el verbo que le falta al producto

`_lineas_del_catalogo` + `_ordenar` es un buscador BM25 sobre índice + catálogo, y funciona. Está
encerrado dentro de la métrica. Ver M01 de la sección siguiente.

---

# Contenido: huecos del catálogo y del grafo `usa:`

Medido con `cosmos.medir.nicho_de_nodo` sobre el árbol real (247 pueblos, 21 oficios).

## C01 — El grafo `usa:` es una estrella, no una malla: 7 oficios no los cita nadie

```
oficio             usa ->                                          salida entrada
rendimiento        ciberseguridad                                       1     9
infraestructura    ciberseguridad, rendimiento                          2     5
cumplimiento       web, extraccion                                      2     4
...
automatizacion, blockchain, cientifico, embebidos, juegos, moviles, trading   ->  entrada 0
```

45 aristas, **23 no recíprocas**. E20 comprueba que el destino existe; nadie comprueba que el
vecindario sea navegable en las dos direcciones, que es lo que un mapa promete. Un agente que
aterriza en `web` nunca será enviado a `moviles`, aunque `moviles` sí apunte a `web`.

## C02 — `web` es el único oficio con herramientas de rendimiento y el único que no enlaza `rendimiento`

`web` tiene `lighthouse` y `unlighthouse`; `rendimiento` recibe `usa:` de `blockchain`,
`cientifico`, `embebidos`, `juegos`, `trading`, `moviles`… y **no de `web`**. Core Web Vitals es el
caso canónico de rendimiento y es el único nicho desconectado de él. Arista que falta:
`web -> rendimiento`.

## C03 — Herramientas en el nicho equivocado, medidas

- **`rendimiento` (18) son dos oficios**: perfilado (`py-spy`, `samply`, `bpftrace`, `hyperfine`,
  `rr`, `sanitizers`, `mimalloc`, `tokio`) y calidad de código (`eslint`, `ruff`, `golangci-lint`,
  `ast-grep`, `jscpd`, `difftastic`, `openrewrite`, `serena`, `mutmut`, `stryker-js`). La prueba de
  `UNIVERSO.md` —*«¿alguien contrataría esto?»*— la pasa «que mi web vaya rápida»; no la pasa «que
  me pases eslint». Y explica la entrada 9: es un cajón de sastre, no un vecino popular.
- **Cuatro de las 22 de `trading` no son de trading**: `hypothesis` (property-based testing),
  `time-machine` (congelar el reloj en tests), `toxiproxy` (inyección de fallos de red) y `tenacity`
  (reintentos). Son herramientas de pruebas genéricas — y existe `mar/pruebas` como agua, además de
  `mutmut`/`stryker-js` en `rendimiento`. Tres sitios distintos para lo mismo.
- **`agentes-ia` (21) es en su mitad el instrumental de esta agencia**, no un oficio contratable:
  `auditar-gasto`, `quota-oficial`, `cuentas-del-asistente`, `ordenes-entre-ventanas`,
  `diario-sin-duplicados`, `captura-recortada`, `playbook-obligatorio`, `medir-contexto`. Por la
  propia prueba de UNIVERSO, eso no es un nicho: es el `rio/` de mantenimiento de COSMOS con forma
  de oficio.
- `playwright` está en `extraccion` mientras `maestro` (E2E móvil) está en `moviles`: el criterio de
  colocación de los E2E no es el mismo en los dos sitios.

---

# Lo que le falta para ser el mejor harness de contexto del mundo

Ordenado por valor real, no por facilidad. Cada uno con coste y con qué se rompe si no se hace.

## 1. El verbo que falta: `cosmos buscar <intención>` — y ya está escrito

COSMOS sabe **decidir** (validar), **medir**, **cargar** (`abrir`) y **aplanar** (`compilar`). No
sabe **encontrar**. Un agente que no conoce el árbol solo puede leer el índice de 21 líneas y
adivinar por qué oficio bajar; si se equivoca, vuelve al `grep` que el proyecto existe para
eliminar. Los otros sistemas de contexto (skills con descripción + carga progresiva, reglas por
glob, mapas de repositorio) resuelven esto con una búsqueda; COSMOS lo tiene implementado y
escondido dentro de la métrica: `acertar._lineas_del_catalogo` + `acertar._ordenar` es un BM25 sobre
índice + catálogo, determinista, sin red y sin coste.

- **Coste:** ~40 líneas (`cosmos/buscar.py` que reusa `acertar`), un subcomando, un `rio-buscar.md`.
  Cero dependencias nuevas.
- **Valor doble:** además de dar el verbo, convierte `acertar` en la evaluación **del camino real**
  en vez de la simulación de un camino que nadie puede recorrer. Hoy el 66 % mide una navegación que
  el producto no ofrece.
- **Si no se hace:** la cifra de acierto seguirá midiendo una función interna, y el agente seguirá
  llegando al nodo correcto por suerte o por `grep`.

## 2. La autoridad del guard se fija al cablear, no se deduce de la entrada

B01 no es un fallo aislado: es la consecuencia de que `puente.sesion` **adivine** a qué repositorio
pertenece un evento leyendo texto que controla el modelo. `cosmos enganchar --sesion` sabe
perfectamente en qué repositorio está instalando el hook y ya acepta `--config`.

- **Coste:** que `enganchar --sesion` escriba `--config <ruta absoluta>` en el comando del hook, y
  que `decidir` prefiera siempre esa ruta. ~10 líneas. `_rutas_del_evento` queda solo como respaldo.
- **Si no se hace:** cada nuevo canal (Bash hoy, MCP mañana) reabre el mismo agujero, y el guard más
  importante del sistema se apaga con una ruta bien colocada.

## 3. Un holdout que no se pueda quemar

Hoy la salida es honesta —dice `quemado` y declara la cifra DESCONOCIDA— pero eso significa que **el
proyecto no tiene ningún número de calidad publicable**, y el mecanismo que lo evita no existe: basta
abrir `--detalle` una vez.

- **Coste:** `acertar --sellar` que guarde el SHA-256 del fichero de validación y su resultado en
  `.cosmos/`, y que se niegue a puntuarlo dos veces con el mismo sello; generación de encargos
  nuevos a partir de una plantilla que no mire los resúmenes. ~60 líneas.
- **Si no se hace:** cada tanda de trabajo tiene que elegir entre no medir o quemar el conjunto, y la
  única defensa contra Goodhart depende de que nadie mire.

## 4. Medir lo que de verdad entra al modelo

`Fuera de COSMOS . no_medido (system prompt, tools, MCP)` es honesto y es un agujero: el presupuesto
de 4.000 defiende una fracción desconocida de la ventana real. Y el contador aproximado va un 7,4 %
por debajo del exacto justo en la cifra que decide (ya documentado en `docs/CALIBRACION.md`), con un
margen verde de 65 tokens.

- **Coste:** medio. Leer el transcript de la sesión o la telemetría del harness para publicar
  «COSMOS ocupa X de Y reales»; y hacer que `[medicion] metodo` por defecto sea `exacto` cuando haya
  tokenizador, en vez de que el verde por defecto salga del contador optimista.
- **Si no se hace:** el número que gobierna todo el diseño se compara contra un denominador que nadie
  ha visto.

## 5. `cosmos doctor`: el camino de vuelta

B03 enseña que hay estados —vista plana huérfana— desde los que el sistema no sabe volver, y que el
mensaje de error empuja hacia dentro. Falta un verbo que diagnostique y proponga la acción exacta,
con `--arreglar` para lo reversible.

- **Coste:** bajo; la información ya la tienen `validar` y `compilar`.
- **Si no se hace:** el modo de fallo será «borrar `.claude/skills` a mano», que es justo lo que el
  sistema prohíbe.

## 6. Agua condicionada por lo que se hace, no solo por el fichero que se toca

`moja` es un glob de ficheros. Por eso `oceano/irreversible` tiene que estar cargado siempre: no hay
forma de decir «esto aplica cuando se despliega». Los cinco océanos son 1.590 tokens permanentes en
un presupuesto de 4.000 — la mayor partida fija del sistema y la que menos se puede optimizar.

- **Coste:** una clave `cuando:` en el agua (verbo/acción declarada por el agente al `abrir`), más su
  invariante. Medio, y toca la taxonomía.
- **Si no se hace:** el techo del presupuesto lo fija el agua permanente, y cada regla nueva de
  seguridad compite con el catálogo por el mismo espacio.

## 7. Versión y migración de la taxonomía

`ciudad` y `casa` se retiraron el 2026-09-01 sin ningún mecanismo de migración: funcionó porque no
había nodos. No hay `version:` en el frontmatter ni forma de que un árbol de un cliente sepa contra
qué versión de COSMOS está escrito.

- **Coste:** bajo si se hace ahora (un campo y una comprobación), alto si se hace con árboles de
  clientes ya desplegados.
- **Si no se hace:** el día que COSMOS viva en tres repositorios de cliente, un cambio de nivel es
  irreparable.

## 8. Evaluación con un modelo real (requiere autorización de gasto)

El propio `acertar` declara su límite: *«no es un agente»*. Cerrar el bucle —¿elige bien un modelo,
no solo el BM25?— es la única forma de saber si los resúmenes sirven.

- **Coste: DINERO.** Son llamadas a API por uso. Se deja preparado y **no se ejecuta sin el sí
  explícito de Darío para ese gasto concreto**. Alternativa sin coste nuevo: `modelos-locales` ya
  tiene `ollama`, `llm` y `lm-evaluation-harness` en el catálogo; un juez local es gratis y suficiente
  para comparar dos versiones del árbol entre sí.
- **Si no se hace:** la única métrica de calidad seguirá midiendo coincidencia de palabras.

---

# Lo que intenté tumbar y aguantó

Se dice para que el verde valga algo.

- **Los 18 sabotajes cazados** de la tabla, uno a uno. Destacan tres redes bien puestas: el cerrojo
  (M06, M07, M21 los tres cazados), la escritura atómica (M04), y las invariantes del validador
  (M18, M19, M20).
- **`agua_que_moja` con ruta absoluta**, el fix de hoy: funciona, incluido el rechazo con mensaje de
  una ruta fuera del proyecto (M09 cazado). Lo que falla es la ruta no canónica (B07), no la
  absoluta.
- **`PreToolUse` malformado**: el fix de hoy deniega de verdad, y M13 lo confirma.
  `hook_event_name: PreToolUse` sin `tool_name` → `EXIT=2` con motivo; JSON truncado → paso con
  rastro, que es la decisión declarada y razonada.
- **G05**: tapa el secreto en `output`, en `stderr` y en una respuesta que llega como cadena suelta;
  conserva el `exit_code` real cuando existe (probado con 1 y 2). Lo único que falla es el valor por
  defecto cuando no existe (B11).
- **`acertar --validacion` inexistente**: no cae al conjunto de ajuste, sale 2 y lo explica. El fix
  del primer revisor está bien hecho.
- **El árbol vacío** no revienta en `validar`, `medir`, `estado`, `mapa`, `generar` ni `compilar`.
- **`cosmos arrancar` sobre un clon limpio** cura el E19 de la vista plana y deja `validar` en verde.
- **La suite**: `Ran 175 — OK (skipped=2)` y `Ran 113 — OK` reproducidos sobre el tar limpio de
  `6a32781`; `38/38` mutaciones de `puente`; `cosmos validar` verde en el repo real.
- **El motor de globs** no lo volví a atacar: el primer revisor ya lo contrastó contra
  `pathlib.full_match` con 0 discrepancias, y B07 no es del motor sino de la normalización previa.

# Sospechas, etiquetadas como tales

- **Carrera del cerrojo con el fichero vacío** (ver B08): entre `os.open(O_EXCL)` y la escritura del
  PID hay una ventana en la que el fichero está vacío y por tanto se clasifica como rancio. Mecanismo
  leído, **no provocado de forma determinista**. Se cierra escribiendo el PID con el mismo `os.open`
  antes de ceder el control.

# Nota de proceso

Mientras escribía esto, otro agente commiteó dos veces sobre `trabajo-2026-09-02` (`939692c`,
`04c3edc`). No afectó a las mediciones porque congelé el árbol en un tar y porque ningún fichero de
código cambió, pero **dos agentes escribiendo en el mismo checkout invalidan cualquier informe que
no lleve pin**. Si va a haber revisión y corrección a la vez, la revisión debería correr sobre un
worktree propio.

# Orden de arreglo sugerido

1. **B01** — la autoridad del guard (crítico, y con el arreglo de la propuesta 2 se cierra la clase).
2. **T01** — tres aserciones para `acertar`; la métrica de calidad no puede seguir sin canario.
3. **B02** + **T02/T03** — un solo juez de verdad, afirmado por igualdad entre llamantes y con un
   caso `[nichos] activos` no vacío.
4. **B03** + **A05** — la vía de vuelta, y que la suite deje de escribir en el árbol.
5. **B04**, **B05**, **B06**, **B09** — cuatro arreglos de menos de diez líneas cada uno.
6. **B07**, **B08**, **B10**, **B11** — normalización de rutas, cerrojo reentrante, veredicto
   trivalente, `exit_code` sin inventar.
7. **A01/A02/A03** — desduplicar antes de que los arreglos de arriba se apliquen a la mitad de las
   copias.
