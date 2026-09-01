# COSMOS se verifica solo: enganches, arranque y válvula

Fecha: 2026-09-01 · Árbol: `galaxia/` · Config: **`cosmos.toml`** (ya no `galaxia.toml`) ·
Cierra H01, H02, H03 y H09 de [`../../../../reviews/revision-adversarial-final.md`](../../../../reviews/revision-adversarial-final.md).

**Estado fijado** (el árbol muta mientras se escribe): base `0b82242`, 170 ficheros sucios en el
árbol de trabajo — casi todos de otro agente trabajando a la vez en `cosmos/validar.py`,
`cosmos/medir.py`, `tests/test_validador.py` y `spec/`. Este parte cubre **18 ficheros**, ninguno de
los suyos.

## El fallo de fondo

**Nada ejecutaba nada.** Todo COSMOS dependía de que una persona escribiera `cosmos validar` a mano.
Es literalmente el antipatrón que este proyecto documentó al auditar otro harness
(`spec/GUARDARRAILES.md`): un detector de fugas impecable y una fuga viva de 2.187 tokens por
sesión, porque nadie lo corría. Y ya había vuelto a pasar aquí: durante la revisión otro agente
añadió cuatro pueblos y la galaxia se puso en rojo sin que se enterase nadie.

`spec/GUARDARRAILES.md` estaba escrito y sin implementar. Esto es implementarlo.

## 1. H02 + H09 — el comando por defecto miraba el árbol de juguete

`cosmos.toml` apuntaba a `ejemplo/`. El gate corre `cosmos validar` a secas, así que **el único
verificador automático del repositorio comprobaba el árbol de pruebas**: se podía falsificar el
índice de la galaxia entero y seguía en verde.

Arreglo, tal como sugería el hallazgo:

| Fichero | Antes | Ahora |
|---|---|---|
| `cosmos.toml` | `arbol = "ejemplo"` | `arbol = "galaxia"`, destino `.cosmos/vista-galaxia` |
| `ejemplo.toml` | no existía | `arbol = "ejemplo"`, destino `.claude/skills` |
| `galaxia.toml` | parche para el árbol real | **eliminado**: su papel lo hace `cosmos.toml` |

Dos configuraciones para dos árboles siguen siendo necesarias mientras `destino` y `manifiesto` sean
globales (el arreglo de fondo —derivarlos de la raíz del árbol— sigue pendiente y vive en
`cosmos/compilar.py`, fuera del alcance de este trabajo). Lo que cambia es **cuál es la de por
defecto**: la del árbol que importa.

**Aviso de compatibilidad:** los comandos de los partes anteriores
(`python3 -m cosmos validar galaxia --config galaxia.toml`) ya no funcionan tal cual. El equivalente
es `python3 -m cosmos validar`, sin flags — que es justo el punto.

Y el nicho activo (H09) ha bajado del flag a la configuración:

```toml
[nichos]
activos = []   # lista vacía = todos los sistemas solares
```

Lo lee `cosmos.cli.nichos_de_configuracion` y lo aplican `validar`, `medir` y `compilar`. `--nicho`
queda como override de inspección. Antes, compilar con `--nicho web` dejaba `validar` en rojo
permanente salvo que todo el mundo recordase repetir el mismo flag en cada invocación.

## 2. H01 — un clon limpio ya no está en rojo, y arranca con un comando

`.cosmos/` estaba a medio desversionar: los manifiestos volvían a estar en el índice al empezar
(`git ls-files .cosmos` los listaba), y la vista que describen estaba en `.gitignore`. También
estaban versionados los dos enlaces simbólicos de `.claude/skills/`, que el propio escáner del repo
prohíbe («vista plana generada, no versionable»).

- Fuera del control de versiones: `.cosmos/compilado.json`, `.cosmos/compilado-galaxia.json`,
  `.claude/skills/probar-salida`, `.claude/skills/revisar-formato`.
- `.gitignore` ahora ignora `.cosmos/` y `.claude/skills/` enteros, alineado con
  `DIRECTORIOS_RAIZ_PROHIBIDOS` y `PREFIJOS_PROHIBIDOS` de `puente/secretos.py`.

Con la vista fuera del repositorio, el clon necesita un paso de arranque, y ahora existe:

```
python3 -m cosmos arrancar
```

Compila la vista plana y vuelve a validar el árbol entero. **No regenera el índice**: E15 se omite
solo en la comprobación previa a compilar (compilar no toca el índice) y se vuelve a exigir en la
validación final. Un índice que miente sigue saliendo en rojo y te manda a `cosmos generar`. Un
bootstrap que repara en silencio lo que el validador debería denunciar no es un bootstrap: es un
encubrimiento, y sería reabrir H02 por la puerta de atrás.

De paso, `arrancar` destrabó un punto muerto real que tenía el CLI con un árbol **nuevo**: `generar`
exigía E19 (vista compilada) y `compilar` exigía E15 (índice generado), así que ninguno de los dos
podía ir primero. Ahora el orden es `arrancar` → `generar` → `arrancar`.

## 3. H03 — el gate se instala, y bloquea

`cosmos enganchar` escribe `.git/hooks/pre-commit` (preguntando a Git por `core.hooksPath`, no
adivinando la ruta). Reglas:

- **No pisa un pre-commit ajeno**: si hay uno que no lleva la marca `cosmos-enganchar`, lo dice, te
  da la línea para encadenarlo tú y **no toca nada**. Ni al enganchar ni al desenganchar.
- `cosmos desenganchar` lo elimina y deja el repositorio idéntico.
- Reenganchar es idempotente.
- El hook exporta `PYTHONPATH` a la instalación de COSMOS, así que sirve **sobre un repositorio
  ajeno**, que es el caso de uso que promete `GOAL.md` §1.

CI: `.github/workflows/cosmos.yml`, sin dependencias externas ni `pip` — solo `actions/checkout` y
el Python del runner. Corre en cada push y cada PR: arrancar (galaxia y ejemplo), validar los dos
árboles, medir, escanear secretos, las dos suites y **el propio gate**.

### Dos defectos que salieron al probar el hook de verdad

Los dos hacían que el gate mirase al repositorio equivocado, y ninguno se ve sin instalarlo:

1. `puente/gate.py::raiz_repositorio()` anclaba en `Path(__file__).parent.parent`. Enganchado sobre
   otro proyecto vía `PYTHONPATH`, **verificaba el árbol de COSMOS y dejaba pasar el ajeno**.
2. `puente/secretos.py::raiz_git()`, igual — y su propia docstring decía lo contrario
   («preguntada a Git en vez de deducida de este fichero»).

Los dos ahora anclan en el directorio de trabajo, que es donde Git ejecuta un pre-commit.

### El gate ya se puede instalar sobre este repositorio

Antes devolvía 1 sobre el propio COSMOS, así que instalarlo habría bloqueado **todos** los commits.
Dos causas, dos tratamientos distintos:

- Los 4 hallazgos de enlaces simbólicos y vista plana versionada: **arreglados** (punto 2).
- Los 6 hallazgos de datos personales (H18, en `cosecha/` y `research/`): fuera de este boundary.
  Se inventarían en `secretos-conocidos.txt`, con `puente/secretos.py --conocidos`. Los hallazgos
  del inventario se imprimen como `CONOCIDO:` y no bloquean; **cualquier hallazgo que no esté en la
  lista bloquea igual**, y la lista solo se encoge. Sin número de línea, para que mover código no
  convierta deuda vieja en deuda nueva. Estado real sin inventario:
  `python3 -m puente.secretos --todo --sin-conocidos`.

`_ordenes()` del gate ahora corre `cosmos arrancar` en vez de `cosmos validar` —la instantánea del
índice no lleva la vista plana, igual que un clon recién bajado, así que verificar ahí es verificar
que el clon arranca— y omite las suites cuyo directorio no existe, para no romper en repos ajenos.

### El gate dice por qué bloquea

Salió probándolo de verdad: el hook corre `--silencioso`, que pasaba `capture_output=True` y tiraba
la salida. Al bloquear, quien hacía el commit veía **`secretos: limpio` y nada más**. Un gate que
bloquea sin decir por qué se desinstala el mismo día. Ahora, al fallar, publica la salida capturada
entera más el comando exacto para reproducirlo y la línea de la válvula. Lo exige
`test_un_indice_roto_no_llega_a_commit`, que además de comprobar que el commit no ocurre comprueba
que la explicación nombra `E15`.

## 4. La válvula de escape

Obligatoria, no opcional: **todo guardarraíl duro sin válvula acaba desactivado a la fuerza**.
Alguien tiene una urgencia un viernes, el guard le estorba, lo arranca entero y ya no vuelve.

```
python3 -m cosmos saltar E16 --motivo "importando 40 skills, se reorganiza el lunes" --caduca 7d
python3 -m cosmos saltar --listar
```

| Propiedad | Cómo está implementada |
|---|---|
| Acotada | `normalizar_codigo` acepta `E00`..`E19`; `todo`, `todos`, `*` y `all` los rechaza por su nombre |
| Con motivo | `--motivo` obligatorio y no vacío |
| Caducable | `--caduca Nd`, entre `1d` y `30d`. Sin caducidad no hay salto |
| Registrada | `.cosmos/saltos.log`, una línea JSON añadida al final; renovar **añade**, nunca reescribe |
| Visible | `COSMOS  verde (1 salto activo: E16, caduca en 5 d)  0 errores` |
| Ruidosa al caducar | Vuelve el rojo y la salida imprime `SALTO CADUCADO` con el motivo textual |

Detalles de diseño que no son obvios:

- **Solo cuenta la última entrada de cada código.** Renovar es escribir otra línea; la vieja queda
  en el registro como historia.
- **El log es local y no se versiona.** Una urgencia de una persona no puede apagar el CI de todos.
  Pero el hook sí lo respeta: `verificar_instantanea` **copia `saltos.log` dentro de la instantánea
  después del `git add`**, para que no lo escanee el detector de secretos (un `.log` versionado es
  hallazgo por sí solo) y para que el salto llegue igualmente al gate.
- **La válvula vale en todos los comandos, no solo en `validar`.** Primera versión: el salto
  desbloqueaba `validar` y el commit seguía bloqueado, porque el gate corre `arrancar` y la
  validación *posterior* de `compilar` no miraba el registro. Una válvula que no abre donde aprieta
  no es una válvula. Ahora `validar`, `compilar`, `generar` y `arrancar` la respetan, y ninguno de
  los cuatro dice «verde» a secas con un salto vivo — lo exige
  `test_ninguna_salida_dice_verde_a_secas_con_un_salto_vivo`, que recorre los cuatro.
- **Alcance exacto, medido:** la válvula cubre los códigos E00–E19 del validador, también dentro
  del gate. **No silencia las suites de tests.** Comprobado sobre el clon: con `saltar E15` activo y
  el índice falsificado, `cosmos arrancar` pasa dentro del gate y lo que sigue bloqueando es
  `tests/test_validador.py::test_ejemplo_completo_es_verde`, que afirma en duro que el árbol real
  valida. Es lo correcto —un test silenciado por una nota en el portátil de alguien deja de
  significar nada— pero hay que decirlo: si lo que bloquea son las pruebas, la salida es arreglar el
  árbol o `cosmos enganchar --sin-pruebas`, no la válvula. Salida literal del intento:
  `Falló: python3 -m unittest discover -s tests -t .`
- `--json` publica `saltos_activos` (con días restantes) y `saltos_caducados`.

## 5. Verificación

Todo lo de abajo se ejecuta desde `/Users/dariosatino/cosmos` con `python3` (3.11+, solo biblioteca
estándar, cero red).

### El gate completo sobre el índice — verde

```
$ python3 -m puente.gate ; echo "EXIT=$?"
...
Ran 35 tests in 1.132s
OK
EXIT=0
```

### Un clon limpio arranca y valida en verde

```
$ git clone -q /Users/dariosatino/cosmos /tmp/clon-verificacion && cd /tmp/clon-verificacion
$ python3 -m cosmos validar | head -2      # antes de arrancar: rojo, y dice qué falta
COSMOS  rojo  1 errores
E19  ... vista plana desincronizada: falta el manifiesto ...
$ python3 -m cosmos arrancar | tail -3
COSMOS  arrancar  verde
Vista compilada en /private/tmp/clon-verificacion/.cosmos/vista-galaxia
$ python3 -m cosmos validar ; echo "EXIT=$?"
COSMOS  verde  0 errores
EXIT=0
$ git status --porcelain | wc -l
       0
```

### El hook instalado bloquea de verdad

Tres pruebas de extremo a extremo en `tests/test_guardarrailes.py::HookQueBloquea`, sobre un
repositorio Git real y temporal, con `git commit` de verdad:

| Prueba | Qué exige |
|---|---|
| `test_un_commit_sano_pasa` | el hook **no** bloquea lo que está bien (si bloqueara todo, lo demás no probaría nada) |
| `test_un_indice_roto_no_llega_a_commit` | índice falsificado → `git commit` falla y `rev-list --count HEAD` no sube |
| `test_un_fichero_sensible_nuevo_no_llega_a_commit` | un `.env` forzado al índice → commit bloqueado |
| `test_la_valvula_desbloquea_el_paso_de_validacion_del_gate` | mismo commit bloqueado + `saltar E15` → **pasa**; prueba que el registro llega al hook |

Más `Enganche` (no pisa un hook ajeno; `desenganchar` deja huella idéntica de `.git/hooks` y del
árbol; reenganchar es idempotente), `Valvula` y `ValvulaEnLaSalida` (con un salto activo la salida
**nunca** contiene una línea con «verde» sin «salto activo»; un salto caducado no omite nada y
recuerda el motivo) y `NichosEnConfiguracion`. **23 pruebas nuevas**, todas en verde.

### Suites

Sobre el clon limpio, que es el estado que deja este commit:

```
$ cd /tmp/clon-verificacion
$ python3 -m unittest discover -s tests -t .
Ran 75 tests — OK (skipped=1)
$ python3 -m unittest discover -s puente/tests -t .
Ran 35 tests — OK
```

Sobre el árbol de trabajo, que además lleva lo que otro agente está escribiendo a la vez en
`cosmos/validar.py` y `tests/test_validador.py`: `Ran 85 tests — OK (skipped=1)` y
`Ran 35 tests — OK`. A mitad de este trabajo esa suite estuvo en rojo con 3 fallos
(`test_meta_el_canario_de_aciclicidad_salta_si_la_identidad_cambia`,
`test_e08_resumen_que_no_informa_aunque_no_repita_el_nombre`,
`test_meta_bateria_rechaza_validador_siempre_verde`) que **no eran de aquí** —
`tests/test_validador.py` solo importa `cosmos.validar`, `cosmos.medir`, `cosmos.generar` y
`cosmos.modelo`, ninguno tocado en este commit— y el otro agente los cerró mientras tanto. Se anota
porque un informe sobre un árbol que muta caduca en minutos: el número que vale es el del clon.

## 6. Lo que queda abierto, y de quién es

- **H18, datos personales en `cosecha/` y `research/`** (6 hallazgos). Inventariados, no resueltos.
  Quien tenga ese boundary vacía `secretos-conocidos.txt`; el gate volverá a exigirlos solo.
- **`destino` y `manifiesto` globales.** Siguen obligando a dos ficheros de configuración para dos
  árboles. Derivarlos de la raíz del árbol es trabajo de `cosmos/compilar.py`.
- **El enganche de sesión** (`cosmos validar --rapido` al arrancar una sesión de agente) que cita
  `spec/GUARDARRAILES.md`: no implementado. Los otros dos —pre-commit y CI— sí.
- **Los partes y `QUEDA.md` citan `galaxia.toml`**, que ya no existe. Son documentos históricos y no
  se han reescrito; este parte lo declara arriba.

## 7. Cómo diagnosticar rápido la próxima vez

1. **«El gate pasa pero no comprueba nada»** → mira dónde ancla su raíz. Si un módulo calcula el
   repositorio desde `Path(__file__)`, instalado sobre otro proyecto verificará el suyo. La prueba
   barata: `cd` a un repo ajeno, ejecutarlo y ver qué rutas nombra.
2. **«Valida en verde pero el árbol está roto»** → comprueba a qué árbol apunta `[raiz]` de la
   configuración por defecto. Falsifica el índice a propósito y exige el rojo; si sigue verde, el
   comando mira otro sitio.
3. **«Un clon limpio sale en rojo»** → mira qué artefactos generados están versionados y cuáles
   ignorados. Si el manifiesto viaja y la vista no, el clon nace desincronizado. Regla: o viajan los
   dos, o ninguno y hay un `arrancar` documentado.
4. **El escáner oculta las rutas.** Para saber qué fichero es un `ruta#<hash>`:

   ```python
   import subprocess
   from puente.etiquetas import etiqueta_de_ruta
   for r in subprocess.run(['git','ls-files','-z'], capture_output=True).stdout.split(b'\x00'):
       if r and etiqueta_de_ruta(r).endswith('<hash>'):
           print(r.decode())
   ```
