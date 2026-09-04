# Revisión adversarial del trabajo de hoy en COSMOS

**Premisa de partida:** el trabajo está mal y hay que demostrarlo. Nada se da por bueno sin haber
intentado tumbarlo primero con un comando copiable.

## Estado del árbol al escribir esto (pin obligatorio)

```
HEAD                          fbde93b78f846a533f54c02a38d1d33da988a650
git status --porcelain | wc -l   0
```

Durante la revisión HEAD pasó de `8479933` a `fbde93b`. El único commit nuevo
(`fbde93b docs(presupuesto)`) añade **solo** `progress/presupuesto-2026-09-02/*`; no toca una
línea de código. Todas las mediciones de abajo valen para los dos.

SHA-256 de los ficheros medidos:

```
df048087…4ef3  cosmos/abrir.py
6f08c702…16fa  cosmos/acertar.py
d54d9c8d…e8d9  puente/sesion.py
43c624c3…9bd0  cosmos/medir.py
a371b520…c370  cosmos/validar.py
d6c0a411…5854  tests/test_escala.py
```

Intérpretes usados, nombrados siempre: `python3` (3.14 del sistema) y `/tmp/calib/bin/python`
(venv con `tiktoken 0.14.0`) donde hace falta el tokenizador real.

---

# Veredicto en una tabla

| # | Afirmación | Veredicto |
|---|---|---|
| 1 | `abrir --tocando` da agua distinta por fichero y ningún mar de más | **Parcial** — el motor de globs es correcto (0 discrepancias en 22.243 comparaciones), pero una ruta **absoluta** devuelve agua vacía en silencio, y 516 de 749 ficheros del propio repo también |
| 2 | La estrella solo se empareja por ruta completa | **Sostenida** |
| 3 | Las fichas citan `scripts/` y todos existen | **Sostenida** (82 citas, 0 rotas, 0 huérfanas) — pero **nada lo guarda**: borré un guion citado y el árbol siguió verde y 140/140 tests en OK |
| 4 | 66 % ajuste, 75 % validación, mínimo sobre validación, `--minimo 80` sale 1 | **Sostenida** — pero el caso degradado revienta o miente (dos hallazgos) |
| 5 | La mejora 50 %→75 % **no** es sobreajuste | **DESMENTIDA. Es sobreajuste, y está medido.** |
| 6 | Los guards no se apagan desde un subdirectorio; `PreToolUse` deniega si no puede evaluar | **Parcial** — la mitad de `PreToolUse` se sostiene; **encontré un `cwd` con el que el guard sigue callando cuando debería denegar** |
| 7 | Los 8 ríos de mantenimiento siguen descubribles | **Sostenida** (los 8, uno a uno) |
| 8 | Árbol verde: validar 0, 140+111 tests, 38/38, 3.929/4.000 | **Sostenida al pie de la letra** — pero **3 de los 5 commits del día no arrancan** |
| 9 | Punto de rotura ~150 oficios, medido antes de aserción | **Sostenida** (pendiente 23,5; rotura 150 en rejilla / 142 real). Ventana de aserción muy ancha |
| 10 | La tabla de E17 sale de la función y el mecanismo descrito es el implementado | **Sostenida** — con un falso negativo y un falso positivo medidos frente a su propio enunciado |

**1 afirmación desmentida entera (#5), 2 desmentidas a medias (#1, #6), 7 sostenidas. 11 hallazgos.**

---

# H01 (CRÍTICO) — La mejora de validación **es** sobreajuste al conjunto de validación

Desmiente la afirmación 5 y desmiente el commit `8479933`, que escribe literalmente:

> «Validacion 50% -> 75% y el ajuste se queda en 66%: **la mejora generaliza, no es punteria**.»

La lectura correcta de «validación +25, ajuste +0» es la contraria.

## El experimento que lo aísla

Se ejecuta el **mismo scorer** (código de HEAD) contra dos `galaxia/` distintas. Lo único que
cambia son los 21 resúmenes de oficio que reescribió `8479933`.

```bash
cd ~/cosmos
mkdir -p /tmp/advcosmos/at_a4f880e /tmp/advcosmos/mix
git archive a4f880e | tar -x -C /tmp/advcosmos/at_a4f880e
git archive HEAD    | tar -x -C /tmp/advcosmos/mix
rm -rf /tmp/advcosmos/mix/galaxia
cp -R /tmp/advcosmos/at_a4f880e/galaxia /tmp/advcosmos/mix/galaxia

python3 -m cosmos acertar            # galaxia de HOY
(cd /tmp/advcosmos/mix && python3 -m cosmos acertar)   # galaxia de ANTES, mismo codigo
```

```
galaxia de HOY     Ajuste 33/50 (66 %)   Validacion 15/20 (75 %)
galaxia de ANTES   Ajuste 33/50 (66 %)   Validacion 10/20 (50 %)
```

**El ajuste no se movió ni un acierto. La validación subió 5 de 5 posibles.**
Una mejora real de la calidad de los resúmenes sube las dos. Subir solo la que se declaró
«escrita aparte y que no guía ninguna decisión» solo tiene una explicación: guió decisiones.

## Qué encargos exactos flipearon, y por qué

Invocación completa en `progress/revision-adversarial-cosmos-2026-09-02/pruebas/probe_sobreajuste.py` (compara los dos JSON de
`cosmos acertar --json` y hace la diferencia de conjuntos). Salida literal:

```
--- ajuste: +1 ganados, -1 perdidos ---
   GANADO  «desplegar en un servidor y que no se caiga»  -> infraestructura  (antes 7º)
   PERDIDO «transcribir horas de audio a texto»

--- validacion: +5 ganados, -0 perdidos ---
   GANADO  «necesito que mi web salga en las busquedas de chatgpt»       -> visibilidad  (antes 13º)
   GANADO  «una app que funcione en iphone y android con el mismo codigo»-> moviles      (antes 15º)
   GANADO  «revisar si mi contrato de solidity tiene un fallo de reentrada» -> blockchain (antes 6º)
   GANADO  «escribir el manual de usuario a partir del codigo»           -> documentos   (antes 3º)
   GANADO  «que la tienda no se caiga el dia de mayor venta»             -> infraestructura (antes 6º)
```

Y las palabras que `8479933` **añadió** al resumen del destino esperado, intersecadas con la
petición de validación (misma normalización que usa el scorer, `cosmos.acertar._normalizar`):

```
visibilidad      +['chatgpt']       <- «...las busquedas de chatgpt»
moviles          +['android','codig','iphon'] <- «...iphone y android con el mismo codigo»
blockchain       +['solidity']      <- «...contrato de solidity...»
documentos       +['codig']         <- «...a partir del codigo»
infraestructura  +['caig','no','se']<- «que la tienda no se caiga...»
embebidos        +['leer','plac']   <- «leer sensores... desde una placa»
cumplimiento     +['avis','cooki']  <- «el aviso legal y la politica de cookies»
extraccion       +['escane','pdf']  <- «cientos de pdf escaneados»
cientifico       +['model','que']   <- «un modelo que clasifique fotos»
automatizacion   +['entr']          <- «cuando entre un pedido nuevo»
infraestructura  +['se']            <- «mi contenedor se queda sin memoria»

11/20 encargos de VALIDACION recibieron palabras suyas en el resumen de su destino.
```

## La prueba que no admite explicación inocente

Se puede argüir que `chatgpt` o `solidity` son buenas palabras para ese nicho con independencia
del examen. La forma de zanjarlo es mirar de **dónde solo pueden haber salido**:

```bash
python3 progress/revision-adversarial-cosmos-2026-09-02/pruebas/probe_vocab.py
```

```
palabras nuevas en los 21 resumenes: 42
  en el vocabulario de VALIDACION : 21
  en el vocabulario de AJUSTE     : 20
  en validacion y NO en ajuste    :  6  ['android','chatgpt','cooki','iphon','plac','solidity']
  en ninguno de los dos           : 16
tamano vocabularios: ajuste 204   validacion 125
```

**Seis palabras nuevas aparecen en el conjunto de validación y en ningún otro sitio del conjunto
de ajuste.** No se puede introducir una palabra que solo existe en el holdout sin haber leído el
holdout. El propio commit lo dice sin darse cuenta: *«Los 21 resumenes reescritos con las palabras
de quien pregunta»* — y para esas seis, «quien pregunta» es exclusivamente el examen.

## Agravante: la máquina de honestidad quedó invertida

Con brecha = 66 − 75 = −9, `formatear_contraste` entra en la rama tranquilizadora:

```
La validación va por delante: el conjunto de ajuste se ha quedado corto.
```

El sistema construido para denunciar la puntería ahora felicita al examinando por haber sacado
más nota en el examen que en los deberes. La cifra **75 % no es publicable como validación**: a
partir de `8479933` es una segunda cifra de ajuste. El único número honesto que queda del día es
el 50 % medido sobre la galaxia previa, y para volver a tener holdout hace falta un conjunto
nuevo escrito sin ver los resúmenes actuales.

---

# H02 (CRÍTICO) — Tres de los cinco commits del día no arrancan

`a4f880e` introdujo en `cosmos/cli.py` un import de `rango_comprobado`, y la función no se
definió en `cosmos/validar.py` hasta `8479933`. Los tres commits intermedios están rotos a nivel
de árbol.

```bash
cd ~/cosmos
for c in b45560c a4f880e 15e2727 0b1a533 8479933; do
  echo "$c  def_en_validar=$(git show "${c}:cosmos/validar.py" | grep -c 'def rango_comprobado')" \
       " usado_en_cli=$(git show "${c}:cosmos/cli.py" | grep -c rango_comprobado)"
done
```

```
b45560c  def_en_validar=0  usado_en_cli=0
a4f880e  def_en_validar=0  usado_en_cli=2     <-- se rompe aqui
15e2727  def_en_validar=0  usado_en_cli=2
0b1a533  def_en_validar=0  usado_en_cli=2
8479933  def_en_validar=1  usado_en_cli=2     <-- se arregla aqui
```

Ejecutado sobre el árbol exacto de cada commit (`git archive`, sin `.gitattributes`, sin
`export-ignore`; la diferencia de 709 vs 686 ficheros son los `__pycache__` que generan los
propios tests):

```bash
for c in a4f880e 15e2727 0b1a533; do
  rm -rf /tmp/advcosmos/at_$c && mkdir -p /tmp/advcosmos/at_$c
  git archive $c | tar -x -C /tmp/advcosmos/at_$c
  (cd /tmp/advcosmos/at_$c && python3 -m cosmos validar; echo "  EXIT=$?"
   python3 -m unittest discover -s tests -t . 2>&1 | grep -E '^(Ran|OK|FAILED)')
done
```

```
at_a4f880e   ImportError: cannot import name 'rango_comprobado'   EXIT=1
             Ran 75 tests   FAILED (failures=1, errors=3, skipped=1)
at_15e2727   ImportError: cannot import name 'rango_comprobado'   EXIT=1
             Ran 78 tests   FAILED (failures=1, errors=3, skipped=1)
at_0b1a533   ImportError: cannot import name 'rango_comprobado'   EXIT=1
             Ran 78 tests   FAILED (failures=1, errors=3, skipped=1)
```

Consecuencia directa sobre las afirmaciones del día: el mensaje de `a4f880e` dice
*«validar verde, 24 tests, 3.999/4.000»*. **Esas cifras no salen del árbol de `a4f880e`**, porque
en ese árbol `cosmos validar` no llega ni a importar. Salieron de un directorio de trabajo sucio
que no se commiteó. Es el fallo de «lo verificado y lo commiteado divergen», y aquí lo hicieron
durante tres commits seguidos.

Reproducción del *coste* del fallo: cualquiera que hoy haga `git bisect` en este rango, o que
clone y se sitúe en `0b1a533`, se encuentra un repositorio que no arranca sin ninguna pista de
por qué.

---

# H03 (ALTO) — Un `Bash` que escribe la ruta de veredicto sigue pasando en silencio

Desmiente la mitad de la afirmación 6, y es **el mismo fallo que `0b1a533` dice haber cerrado**,
mudado de `Write` a `Bash`. El docstring de `_rutas_del_evento` (puente/sesion.py) afirma:

> «El `cwd` solo no basta. Un evento que escribe en `<repo>/galaxia/COSMOS.md` con el directorio
> de trabajo en `/tmp` no lo protegía nadie […] lo que hay que mirar es dónde cae el daño, no
> desde dónde se lanza.»

Se arregló mirando `tool_input.file_path` / `notebook_path` / `path`. Para un evento `Bash`, el
destino del daño vive en `tool_input.command`, que `_rutas_del_evento` nunca lee. Así que para
`Bash` se sigue localizando el repositorio **solo por el `cwd`**.

Mismo comando, dos `cwd`:

```bash
cd ~/cosmos

# A) cwd = raiz del repo  -> DENIEGA (control)
echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","session_id":"adv",
 "cwd":"~/cosmos",
 "tool_input":{"command":"echo x > ~/cosmos/galaxia/COSMOS.md"}}' \
 | python3 -m puente.sesion --formato exit2; echo "EXIT=$?"

# B) cwd = ~  (el PADRE real del repo) -> SILENCIO
echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","session_id":"adv",
 "cwd":"~",
 "tool_input":{"command":"echo x > ~/cosmos/galaxia/COSMOS.md"}}' \
 | python3 -m puente.sesion --formato exit2; echo "EXIT=$?"
```

```
A)  COSMOS  sesion  rojo  escritura a mano sobre una ruta de veredicto
    ~/cosmos/galaxia/COSMOS.md  (protegida: …/galaxia/COSMOS.md)
    EXIT=2                       <- bloquea

B)  <sin una sola linea de salida>
    EXIT=0                       <- pasa
```

Reproducido igual con `tee` y con `cp`:

```
D3) echo x | tee ~/cosmos/galaxia/COSMOS.md   cwd=~ -> exit=0, salida VACIA
D5) cp /tmp/falso.md ~/cosmos/galaxia/COSMOS.md  cwd=~ -> exit=0, salida VACIA
```

Y es **silencio total**: la rama `SinCosmos` de `main()` hace `return 0` sin escribir siquiera en
`.cosmos/cierres.log` (a propósito: «escribir un log en el repositorio de otro sería peor»). Con
las palabras del propio módulo: *«un guard que no está no se distingue de uno que aprobó»*.

`cwd=~` no es un caso rebuscado: es el padre del checkout, y es exactamente
donde se sitúa una sesión lanzada desde el home o desde otro repo hermano.

**Contraste honesto:** la mitad de `Write` sí quedó bien cerrada y sí está guardada por un test.
Lo comprobé revirtiendo el fix sobre una copia de HEAD:

```bash
rm -rf /tmp/advcosmos/base && mkdir -p /tmp/advcosmos/base
git archive HEAD | tar -x -C /tmp/advcosmos/base
# (revertir _rutas_del_evento para que mire solo el cwd — script en el scratch)
(cd /tmp/advcosmos/base && python3 -m unittest discover -s puente/tests -t . 2>&1 | tail -3)
```

```
Ran 111 tests   FAILED (failures=1)
```

Es decir: el trozo arreglado tiene red; el trozo que **no** se arregló no tiene ni red ni fallo,
porque nadie escribió el caso. Con `Write` desde `cwd=/tmp` y con `cwd=galaxia/` el guard deniega
correctamente (medido, ambos `deny`).

---

# H04 (ALTO) — `PreToolUse` sí deniega ante config rota, pero calla ante evento malformado

La otra mitad de la afirmación 6 **se sostiene** para todo lo que probé a nivel de configuración:

```bash
# cinco cosmos.toml rotos distintos, evento Write sobre la ruta de veredicto
for c in tipo_malo toml_roto arbol_lista sin_seccion arbol_es_fichero; do … done
```

```
tipo_malo         -> exit2 EXIT=2  COSMOS  sesion  rojo  el guard no pudo evaluar este evento
toml_roto         -> exit2 EXIT=2  idem
arbol_lista       -> exit2 EXIT=2  idem
sin_seccion       -> exit2 EXIT=2  idem
arbol_es_fichero  -> exit2 EXIT=2  idem
```

Pero el mismo principio no se aplica a la entrada:

```bash
printf '%s' '{"hook_event_name":"PreToolUse","tool_name":"Write","cwd":"~/cosmos","tool_input":{"file_path":"galaxia/COSM' \
 | python3 -m puente.sesion --formato exit2; echo "EXIT=$?"
```

```
JSON truncado         -> EXIT=0  (sin salida)
stdin vacio           -> EXIT=0  (sin salida)
entrada no-dict       -> EXIT=0  (sin salida)
sin hook_event_name   -> EXIT=0  (sin salida)
```

`main()` hace `except (ValueError, TypeError): return 0` sobre `json.load(sys.stdin)`. Un evento
truncado es tan «no puedo evaluar» como un `cosmos.toml` roto, y aquí se falla abierto y en
silencio. La regla que el propio módulo declara («`PreToolUse` existe para denegar, y si no puede
decidir, deniega diciendo por qué») se aplica a un lado del contrato y no al otro.

---

# H05 (ALTO) — `cosmos acertar` se auto-califica cuando falta la validación, y revienta si está vacía

La afirmación 4 se sostiene, y la discriminé de verdad en vez de conformarme con que `--minimo 80`
salga 1 (con 66 y 75 los dos están por debajo de 80: ese exit 1 no distingue nada):

```bash
cd ~/cosmos
for m in 66 70 76 80; do python3 -m cosmos acertar --minimo $m >/dev/null 2>&1; echo "--minimo $m -> EXIT=$?"; done
```

```
--minimo 66 -> EXIT=0
--minimo 70 -> EXIT=0     <- ajuste 66 < 70 y aun asi pasa: se cobra sobre validacion (75)
--minimo 76 -> EXIT=1     <- validacion 75 < 76
--minimo 80 -> EXIT=1
```

Confirmado: el mínimo se cobra sobre validación. Pero el caso degradado:

```bash
# a) fichero de validacion INEXISTENTE
python3 -m cosmos acertar --validacion /tmp/advcosmos/no-existe.json --minimo 70 2>&1 | head -6
```

```
acierto 66 % < mínimo exigido 70 %
COSMOS  acertar
  Encargos ........ 50
  Acierta a la 1 .. 33 (66 %)
```

`cli.py` hace `if args.validacion and args.validacion.exists() else None` y luego `juez = val or pun`.
Con una ruta mal escrita, el gate **se cobra sobre el conjunto de ajuste sin decir una palabra** —
literalmente lo que el comentario de tres líneas encima prohíbe: *«cobrar el listón con el conjunto
que se mira al trabajar es dejar que el examinando escriba su propio examen»*. Es un fallback
tranquilizador por defecto: en vez de alarma, el valor cómodo.

```bash
# b) fichero de validacion VACIO
echo '[]' > /tmp/advcosmos/vacio.json
python3 -m cosmos acertar --validacion /tmp/advcosmos/vacio.json --minimo 70 2>&1 | tail -5
```

```
  File "~/cosmos/cosmos/acertar.py", line 306, in formatear_contraste
    va = 100 * c.validacion.aciertos / c.validacion.total
ZeroDivisionError: division by zero
```

`Contraste.brecha` y `Contraste.como_dict` **sí** comprueban `.total`; `formatear_contraste` es la
única de las tres que no. Traceback crudo al usuario.

---

# H06 (MEDIO) — `abrir --tocando` con ruta absoluta devuelve agua vacía en silencio

De la afirmación 1, la parte del motor de globs **se sostiene, y con margen**. Contrasté la
traducción propia (`cosmos.validar._glob_a_regex`) contra `pathlib.PurePosixPath.full_match`
sobre los 29 patrones de mar/lago y 767 rutas (todo el repo + sondas raras: `a.test.js`,
`.env.local`, `x.py/y.txt`, `A.PY`, `a/tests/b/c.txt`…):

```
patrones de mar/lago: 29 | rutas probadas: 767
DISCREPANCIAS motor propio vs pathlib.full_match: 0
```

Ningún mar de más, ninguno de menos. Y sí devuelve agua distinta por fichero:

```bash
python3 -m cosmos abrir ciberseguridad --tocando cosmos/abrir.py --json | …   # 3 mares
python3 -m cosmos abrir ciberseguridad --tocando tests/test_x.py --json | …   # 4 mares
```

**El fallo está en el borde.** `agua_que_moja` solo quita un `./` inicial y luego casa contra un
glob relativo a la raíz. Una ruta absoluta no casa nunca:

```bash
cd ~/cosmos
for f in ~/cosmos/cosmos/abrir.py ./cosmos/abrir.py Makefile "" ; do
  echo -n "$f -> "
  python3 -m cosmos abrir ciberseguridad --tocando "$f" --json \
   | python3 -c "import sys,json;print([a['nombre'] for a in json.load(sys.stdin)['agua']])"
done
```

```
~/cosmos/cosmos/abrir.py -> []          <-- ruta absoluta: VACIO
./cosmos/abrir.py                         -> ['mar/criterio','mar/resistencia','mar/revision']
Makefile                                  -> []
(cadena vacia)                            -> []
```

`spec/NUCLEO.md` §9 define la semántica «sobre rutas POSIX **relativas a la raíz del proyecto**»,
así que la ruta absoluta está fuera de contrato — pero el CLI la acepta y devuelve **exactamente
la misma salida** que «este fichero no tiene agua». Un valor mostrado que no es un valor conocido.
Y en un entorno donde la norma es pasar rutas absolutas, es la forma por defecto de invocarlo.

Agravante medido: la ambigüedad no es teórica, es la mayoría del repo.

```
749 ficheros reales del repo -> 4 conjuntos de agua distintos
   516 ficheros -> (SIN AGUA)          <- 68,9 %
   183 ficheros -> criterio, resistencia, revision
    27 ficheros -> pruebas
    23 ficheros -> criterio, pruebas, resistencia, revision
```

Todo `galaxia/**.md` y todo `spec/**.md` —el contenido que ES el proyecto— cae en «(SIN AGUA)»,
indistinguible del fallo de arriba.

*(Observación menor, por diseño explícito y documentado: el agua no depende del nodo abierto.
`abrir web|ciberseguridad|trading --tocando cosmos/abrir.py` devuelven los tres el mismo trío.)*

---

# H07 (MEDIO) — Nada guarda las citas a `scripts/`

La afirmación 3 **se sostiene hoy**. Mi primer chequeo dio 2 rotas y era **mi** regex el que
estaba mal: `agent-skills/shared/scripts/skillpack-install.mjs` y `zephyr/scripts/requirements.txt`
son rutas de proyectos ajenos citadas dentro de un bloque de código, no guiones locales. Con el
patrón correcto (cita que **empieza** en `scripts/`):

```bash
cd ~/cosmos && python3 - <<'PY'
import re, pathlib
p = re.compile(r'(?<![\w/.-])scripts/[A-Za-z0-9_.\-]+')
ok=rotas=0; pueblos=set()
for s in sorted(pathlib.Path('galaxia/pueblos').glob('*/SKILL.md')):
    for m in sorted(set(p.findall(s.read_text()))):
        pueblos.add(s.parent.name)
        ok, rotas = (ok+1, rotas) if (s.parent/m).exists() else (ok, rotas+1)
print(f"pueblos con cita local: {len(pueblos)} | citas resueltas: {ok} | ROTAS: {rotas}")
huer=[str(d) for d in sorted(pathlib.Path('galaxia/pueblos').glob('*/scripts/*'))
      if f"scripts/{d.name}" not in (d.parent.parent/'SKILL.md').read_text()]
print("scripts en disco NO citados:", len(huer))
PY
grep -rn "cosecha/" galaxia/ | wc -l
```

```
pueblos con cita local: 47 | citas resueltas: 82 | ROTAS: 0
scripts en disco NO citados: 0
0        <- cero citas residuales a cosecha/
```

**Pero es un arreglo sin red.** Borré un guion citado sobre una copia limpia de HEAD:

```bash
rm -rf /tmp/advcosmos/sab && mkdir -p /tmp/advcosmos/sab
git archive HEAD | tar -x -C /tmp/advcosmos/sab
cd /tmp/advcosmos/sab
rm galaxia/pueblos/auditar-gasto/scripts/auditar-gasto.py
python3 -m cosmos validar | head -3
python3 -m unittest discover -s tests -t . 2>&1 | grep -E '^(Ran|OK|FAILED)'
```

```
COSMOS  rojo  1 errores       <- E19 (vista plana del clon fresco), NO la cita rota
Ran 140 tests   OK (skipped=2)
```

Línea base del **mismo** archive sin sabotear: también `1 errores` con el mismo E19. Es decir, el
sabotaje no cambió nada. No hay invariante `Exx` ni test que compruebe que un `scripts/X` citado
existe: `grep -n "script\|guion" cosmos/validar.py` no devuelve ninguna comprobación. El fix de
F20 —84 `SKILL.md` tocadas, 139 líneas `cosecha/`→`scripts/`— puede pudrirse en silencio.

*(Nota de exactitud: la afirmación dice «38 fichas». `git show 6b7ce8c --stat | grep SKILL.md | wc -l`
da **84** ficheros de skill tocados y 139 sustituciones. El «38» del registro se refiere a las que
citaban guiones **inexistentes**, no a las que cambiaron de prefijo.)*

---

# H08 (MEDIO) — El margen ±5,2 % se verifica sobre la cifra que no decide el presupuesto

La afirmación 8 es literalmente cierta y lo verifiqué entera:

```bash
cd ~/cosmos
python3 -m cosmos validar                                   # COSMOS  verde  0 errores   EXIT=0
python3 -m unittest discover -s tests -t . 2>&1      | grep -E '^(Ran|OK)'   # Ran 140  OK (skipped=2)
python3 -m unittest discover -s puente/tests -t . 2>&1 | grep -E '^(Ran|OK)' # Ran 111  OK
python3 puente/tests/mutaciones.py | tail -1                # 38/38 invariantes vistas fallar
python3 -m cosmos medir | grep Presupuesto                  # 4.000  OK, quedan 71 tokens
```

Con el tokenizador real el veredicto se invierte, y eso el commit lo declara ABIERTO (y el
`DIAGNOSTICO.md` de `fbde93b`, escrito por otro agente, lo documenta con las mismas cifras que yo
medí: agua 1.346 vs 1.545). Lo que añado es **dónde falla la red**:

```bash
/tmp/calib/bin/python -m cosmos medir --metodo exacto | grep Presupuesto ; echo "EXIT=$?"
```

```
Presupuesto ..... 4.000     ROJO, excede en 244 tokens en el peor caso con agua
EXIT=1
```

```bash
python3 -c "
a={'entrada':1233,'nicho':2583,'agua':1346,'peor':3929}
e={'entrada':1247,'nicho':2699,'agua':1545,'peor':4244}
for k in a: print(f'{k:8s} aprox={a[k]:5d} exacto={e[k]:5d} error={100*(e[k]-a[k])/e[k]:5.2f} %')"
```

```
entrada  aprox= 1233 exacto= 1247 error= 1.12 %
nicho    aprox= 2583 exacto= 2699 error= 4.30 %
agua     aprox= 1346 exacto= 1545 error=12.88 %   <-- 2,5x el margen publicado
peor     aprox= 3929 exacto= 4244 error= 7.42 %   <-- la cifra que decide E16
```

`tests/test_medidor.test_aproximado_y_exacto_respetan_margen_publicado` afirma el margen sobre
dos cosas: la media por cuerpo, y `contexto_inicial` —o sea **`entrada`, con 1,12 % de error**.
No afirma nada sobre `peor_con_agua`, que es sobre lo que E16 dicta verde o rojo y va al 7,42 %.
El «OK, quedan 71 tokens» es un colchón del 1,8 % delante de un error medido del 7,42 %: **el
veredicto verde está 4,4 veces dentro del ruido de su propio contador**.

Y las dos únicas pruebas que tocan esto se saltan por defecto en la máquina de trabajo:

```
skipped 'SIN TOKENIZADOR: el margen publicado (±5,2 %) NO se ha verificado en esta ejecución.'
skipped 'sin tokenizador no se puede medir el veredicto exacto'
```

Con `/tmp/calib/bin/python -m unittest discover -s tests -t .` salen `Ran 140 — OK` sin skips,
así que no ocultan un rojo. Pero un `OK (skipped=2)` en el que los 2 saltados son exactamente las
pruebas de la métrica principal es un verde que hay que leer con la etiqueta puesta.

**Cifra rancia de propina:** el docstring del canario dice *«el árbol está en 4.323/4.000, mientras
el contador aproximado publica 3.990»*. Hoy son **4.244 / 3.929**. Es un número publicado que no
sale de ejecutar nada — está en prosa, no en una aserción, y por eso no se cayó solo.

---

# H09 (MEDIO) — E17: un falso negativo y un falso positivo contra su propio enunciado

La afirmación 10 **se sostiene en lo que dice**: la tabla la ata `tests/test_e17_limite.py`
comparando lo publicado en la spec con lo que devuelve `solape_de_afirmaciones`, y el mecanismo
descrito (frases de ≥4 palabras con contenido → conjunto sin vacías → Jaccard frase a frase con
≥3 palabras comunes → máximo contra el umbral) es punto por punto el implementado. Verificado
leyendo `_afirmaciones` / `solape_de_afirmaciones` / `_comprobar_e17` y ejecutando el test:
`MINIMO_PALABRAS_AFIRMACION=4`, `MINIMO_PALABRAS_COMPARTIDAS=3`, `umbral 0,25`.

Ataqué el **enunciado normativo**, que es más ancho que la implementación:

> «**E17** — Dos nodos que están simultáneamente en el contexto de entrada no pueden solaparse por
> encima del umbral configurado.»

`_co_cargables` restringe a `NIVELES_CO_CARGABLES = {oceano, mar, lago, estrella}` y compara solo
`cuerpo(nodo)`. Dos consecuencias medidas (`progress/revision-adversarial-cosmos-2026-09-02/pruebas/probe_e17.py`, árboles sintéticos):

```
otro-oceano          la misma frase en dos oceanos                    -> E17 dispara: SI (control, 100.0%)
resumen-de-sistema   la misma frase en un oceano y en el RESUMEN de
                     un oficio (que viaja en el indice, SIEMPRE cargado) -> E17 dispara: NO
dos-estrellas        la misma frase en DOS estrellas de oficios
                     distintos (que NUNCA coinciden en contexto)      -> E17 dispara: SI (100.0%)
```

- **Falso negativo:** `medir._bloques_contexto_inicial` mete el índice y el catálogo en la entrada
  siempre. Un resumen de oficio está simultáneamente en el contexto con todos los océanos, y E17
  no lo mira. La invariante enunciada cubre ese caso; la implementada, no.
- **Falso positivo:** cada nodo tiene como mucho una estrella, así que dos estrellas jamás se
  pagan a la vez. E17 las compara igual y dispararía por una política repetida que no cuesta nada.

Ninguno rompe nada hoy (la galaxia está verde), pero son la distancia entre lo que la spec promete
y lo que el código comprueba, que es justo lo que E17 existe para no dejar pasar en otros.

---

# H10 (BAJO) — La rotura del mapa está bien medida, con una ventana muy ancha

La afirmación 9 se sostiene:

```bash
cd ~/cosmos && python3 progress/revision-adversarial-cosmos-2026-09-02/pruebas/probe_escala.py
```

```
entradas: {10: 913, 40: 1618, 80: 2557}
pendiente_baja=23.500  pendiente_alta=23.475   (docstring dice 'unos 23 tokens por oficio')
  assertGreater(pb,15) -> True   assertAlmostEqual(pa,pb,delta=5) -> True  (|dif|=0.025)
punto de rotura (paso 10) = 150   assertIn(rot, range(100,221)) -> True
punto de rotura exacto (paso 1) = 142
   100 oficios -> 3026 tok    140 -> 3965 tok    150 -> 4200 tok    160 -> 4435 tok
```

Las cifras del docstring salen de la función: 23,5 tok/oficio contra «unos 23», y 150 es la
respuesta correcta en la rejilla de paso 10 que usa el test. Consistente con haber medido primero
y escrito la aserción después.

Dos matices, ambos disciplinados por el propio comentario del test pero que conviene decir:

1. El punto de rotura **real** es 142, no 150; 150 es el redondeo de la rejilla. El docstring dice
   «Medido: 150 oficios», que es cierto de la medición que hace, no del sistema.
2. `assertIn(rotura, range(100, 221))` es una ventana de 120 sobre un valor de 150: la medida
   podría irse a 220 o caer a 100 sin poner el test rojo. Instrumenta más que afirma. El comentario
   lo declara («fija el orden de magnitud»), así que no es deshonesto — pero no es «la aserción
   afirma lo medido» en el sentido fuerte de `mar/pruebas`.
3. `PRESUPUESTO = 4000` está a mano en el test en vez de leerse de `cosmos.toml`, y se mide con el
   contador **aproximado**, el mismo que H08 muestra 7,42 % optimista sobre la cifra compuesta. El
   punto de rotura real con tokenizador está por debajo de 142.

---

# H11 (BAJO) — Recuentos rancios en las specs, fuera del alcance de `test_spec_al_dia`

```bash
cd ~/cosmos
python3 -c "
from cosmos.modelo import cargar_arbol, cargar_configuracion
c=cargar_configuracion('cosmos.toml'); a=cargar_arbol(c.arbol, tambien=(c.registro,))
print('nodos totales:', len(a.nodos))"
python3 -m cosmos estado | sed -n '3,14p'
grep -n "312 nodos" spec/VALIDADOR.md ; grep -n "209 skills" spec/TAXONOMIA.md
```

```
nodos totales: 373
    sistema-solar 21 · continente 6 · pais 42 · pueblo 247 · mar 6 · oceano 5 · rio 16 · estrella 21 · lluvia 8

spec/VALIDADOR.md:62:  «Medido sobre los 312 nodos de la galaxia real»      -> hoy 373
spec/TAXONOMIA.md:129: «las 209 skills montadas son un unico fichero…»      -> hoy 247 pueblos
```

Los dos están en pasado («Medido sobre…»), así que documentan un momento y no mienten sobre el
presente. Pero `tests/test_spec_al_dia.py` existe precisamente para que las specs no publiquen
cifras que el árbol ya desmintió, y solo cubre dos cosas: los mares y un recuento en prosa contra
su tabla (`test_los_mares_de_la_spec_son_los_del_disco`,
`test_el_recuento_escrito_en_prosa_es_el_de_la_tabla`). Estos dos quedan fuera.

---

# Lo que intenté tumbar y aguantó

Se dice explícitamente, porque un revisor que solo publica lo que rompe no informa de lo que
probó.

**Afirmación 2 — la estrella solo por ruta completa.** Construí el árbol que la rompería
(`progress/revision-adversarial-cosmos-2026-09-02/pruebas/probe_estrella.py`): una estrella con `ilumina: calidad` y un país cuya
`referencia` es `web/calidad`; y dos países `calidad` en oficios distintos con una estrella que
ilumina `web/calidad`.

```
A) ilumina='calidad' vs nodo 'web/calidad'  -> estrella: None      (no se engancha por nombre)
B) abrir web/calidad   -> estrella: calidad
   abrir movil/calidad -> estrella: None                           (no se derrama al vecino)
```

**Afirmación 7 — los 8 ríos de mantenimiento.** Comprobados uno a uno, nombrados y con cuerpo:

```
rio (mantenimiento, 'cosmos abrir rio/x'): acertar, arrancar, compilar, desenganchar,
                                           enganchar, generar, mapa, proyectar
NOMBRADOS: los 8   |   NO nombrados: []
rio/arrancar 345 · rio/compilar 344 · rio/desenganchar 165 · rio/acertar 816
rio/generar  259 · rio/enganchar 263 · rio/proyectar   276 · rio/mapa    205   (chars de cuerpo)
```

Y la línea aparece con nicho `None`, `['web']` y `['ciberseguridad']`, así que no desaparece al
acotar el nicho. Matiz de exactitud: aparecen en el **catálogo**, no en el índice —
`galaxia/COSMOS.md` no nombra ningún río, ni de mantenimiento ni de trabajo.

**Motor de globs de `moja`.** 29 patrones × 767 rutas contra `pathlib.full_match`: 0 discrepancias.

**Guards desde subdirectorio, para `Write`.** `cwd=galaxia/` con `file_path` relativo, y `cwd=/tmp`
con `file_path` absoluto: los dos `deny`. Ese fix está bien hecho **y** guardado por un test
(revertirlo pone `puente/tests` en `FAILED (failures=1)`).

**Suites.** `140 OK (skipped=2)`, `111 OK`, `38/38 mutaciones`, `validar` verde: reproducidos
todos. Y con `/tmp/calib/bin/python`, `Ran 140 — OK` sin ningún skip.

---

# Qué haría falta arreglar, por orden

1. **Retirar el 75 % como cifra de validación** (H01). El conjunto está contaminado desde
   `8479933`. Hace falta un holdout nuevo escrito sin ver los resúmenes actuales, y hasta
   entonces la cifra honesta publicable es la de ajuste. Corolario de proceso: los resúmenes y el
   fichero de validación no pueden volver a tocarse en la misma tanda.
2. **`git revert`-proof del rango roto** (H02): dejar constancia de que `a4f880e..0b1a533` no
   arranca, o rehacer el historial. Y no volver a publicar cifras de verificación sin correrlas
   sobre el árbol que se commitea.
3. **Cerrar el agujero de `Bash` en `_rutas_del_evento`** (H03) leyendo también
   `tool_input.command`, con el test que hoy no existe.
4. **`acertar`**: exigir la validación en vez de caer al conjunto de ajuste, y guardar
   `formatear_contraste` contra `total == 0` (H05).
5. **`abrir --tocando`**: aceptar rutas absolutas relativizándolas contra la raíz, o rechazarlas
   con un error — cualquier cosa menos devolver el mismo `[]` que «no hay agua» (H06).
6. **Invariante para las citas `scripts/`** (H07): es un `Exx` de veinte líneas y evita que el
   trabajo de hoy se pudra.
7. **Afirmar el margen sobre `peor_con_agua`**, no solo sobre `entrada` (H08).
