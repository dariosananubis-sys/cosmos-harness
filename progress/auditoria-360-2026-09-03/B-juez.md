# Auditoría 360 COSMOS — Revisor B: el juez y la métrica

**Pregunta:** ¿la nota que se pone COSMOS es honesta?
**Premisa de partida:** la métrica es autocomplaciente y hay que demostrarlo.

## Pin de estado

```
git -C ~/cosmos rev-parse HEAD      -> b0c1ebdeb2d9bac7e068d10714213ff2f9eda926
git -C ~/cosmos status --porcelain | wc -l  -> 0
rama: main
```

Árbol limpio. Todo lo de abajo se midió sobre ese commit.

## Método e intérpretes

- **Repo intacto.** Cero ediciones, cero commits, cero push sobre `~/cosmos`. Lo único
  escrito es este fichero.
- **Los experimentos van sobre copias del scratchpad**, siempre indicado:
  `$SP = <scratchpad>`
  · `$SP/cosmos-copia` y `$SP/cosmos-copia2` (inflado de la nota) · `$SP/sab`, `$SP/sabj`,
  `$SP/sabj2` (sabotajes) · `$SP/sello` (sello roto).
- **Intérpretes, dichos exactos.** `python` a secas **no existe** en esta máquina
  (`which -a python` → nada). Se usa `python3` = `/usr/local/bin/python3`. El repo **no tiene
  `.venv`**.
- **`/tmp/calib/bin/python` que cita el registro NO EXISTE** (`ls` → `No such file or directory`).
  Para poder medir con tokenizador real monté uno nuevo:
  `python3 -m venv $SP/calib && $SP/calib/bin/pip install tiktoken` — software libre, sin tarjeta,
  cero coste. En adelante `PYCAL=$SP/calib/bin/python`.
- **Cero dinero y cero correo.** No se evaluó por API (aparcado por decisión de Darío); el juez
  con modelo se probó solo para comprobar que falla limpio sin servidor.
- Los códigos de salida se capturan **sin tubería** (`cmd > fichero 2>&1; echo $?`): un
  `| head` detrás devuelve el código del `head`, no el del comando.

---

# HALLAZGOS

## B-01 · CRÍTICO — La nota sube de 40 % a 100 % sin mejorar nada, y con TODAS las puertas en verde

Es la pregunta central del encargo y la respuesta es sí, con margen. Reescribí los `resumen:` de los
20 nodos que el holdout espera, pegando las palabras literales de cada consulta y **sin añadir una
sola herramienta ni corregir un solo resumen malo**. Copiar el examen a la chuleta, nada más.

**Reproducción** (sobre copia, nunca el repo):

```bash
SP=<scratchpad>
cp -R ~/cosmos $SP/cosmos-copia2 && rm -rf $SP/cosmos-copia2/.git
cp $SP/control-revisorB.json $SP/cosmos-copia2/pruebas/
cd $SP/cosmos-copia2
python3 $SP/inflar2.py $SP/cosmos-copia2     # lee el holdout con un cat y lo pega a los resumenes
python3 -m cosmos generar >/dev/null 2>&1
python3 -m cosmos validar > $SP/val3.out 2>&1; echo "EXIT_VALIDAR=$?"
python3 -m cosmos acertar
python3 -m cosmos acertar --validacion pruebas/control-revisorB.json
python3 -m cosmos acertar --minimo 95 >/dev/null 2>&1; echo "EXIT_MIN95=$?"
python3 -m cosmos medir
```

**Salida real:**

```
resumenes reescritos: 20/20
EXIT_VALIDAR=0
COSMOS  verde  0 errores

  Ajuste ......... 32/50 (64 %)
  Validación ..... 20/20 (100 %)   escritos aparte; no guían ninguna decisión
  La cifra que vale es 100 %.
  (holdout SELLADO: el detalle por encargo no se enseña, que es lo que quema)
  La validación va por delante: el conjunto de ajuste se ha quedado corto.

--- control independiente (mío, nunca visto por el que ajusta) ---
  Validación ..... 6/20 (30 %)

EXIT_MIN95=0
  Presupuesto ..... 4.000     OK, quedan 658 tokens en el peor caso con agua (ciberseguridad)
```

**Lo que quedó del árbol.** Un ejemplo entre veinte:

```
resumen: juego tirones muchos enemigos.                                  <- despues
resumen: Videojuegos 2D y 3D: motor, bucle, fisica, activos y publicacion. <- antes
```

**El marcador completo del sabotaje:**

| Señal | Antes | Después | Lectura |
|---|---:|---:|---|
| `cosmos validar` | verde 0 err | **verde 0 err** | no se entera |
| `cosmos medir`, peor con agua | 3.546 tok | **3.342 tok** | **204 tokens MÁS BARATO** |
| `acertar` ajuste | 66 % | 64 % | −2 |
| `acertar` **validación (la que vale)** | 40 % | **100 %** | **+60** |
| `acertar --minimo 95` | — | **EXIT 0** | pasa |
| **Control independiente (revisor B)** | **45 %** | **30 %** | **−15: el árbol está PEOR** |

El árbol quedó estrictamente peor —los resúmenes ya no describen nada— y **todos los números del
proyecto mejoraron**, incluido el presupuesto: destrozar un resumen lo acorta. Es exactamente el
modo de fallo que el docstring de `cosmos/acertar.py` dice haber venido a cerrar —*«la manera más
barata de pasar el presupuesto es escribir resúmenes peores»*— solo que la defensa se montó
mirando al conjunto de ajuste y el agujero está en el holdout.

**Fix.** Tres piezas, ninguna cosmética:
1. El holdout **sale del repo** (ver B-02) o se guarda cifrado con la clave fuera del árbol.
2. Un **conjunto rotatorio de control** que se regenera cada N commits desde una fuente que el que
   ajusta no controla, y cuyo resultado se publica junto a la validación. La divergencia entre
   ambos es la señal de inflado.
3. Un **canario de destrucción de resumen**: si el `resumen` de un nodo pierde >40 % de sus términos
   distintos respecto al commit anterior *y* la nota sube, el gate sale en rojo pidiendo revisión
   humana. Un resumen que mejora no suele vaciarse.

**Riesgo si no se toca.** Alto y creciente. No hace falta mala fe: basta un agente futuro con la
instrucción «sube la métrica de acierto». Hoy la forma más barata de obedecerla es esta, y ningún
guardarraíl del repo lo impide.

---

## B-02 · CRÍTICO — El sello no sella: el examen está en claro dentro del repo

El registro afirma que el holdout «no se quema». El sello (`pruebas/encargos-validacion.SELLO`,
sha256 del contenido) impide **un** gesto: que el CLI enseñe el detalle por encargo. Eso funciona y
está bien hecho —lo verifiqué, ver «sólido»—. Pero **no impide el gesto que de verdad importa**:

```bash
cat ~/cosmos/pruebas/encargos-validacion.json    # las 20 consultas, en claro, versionadas
```

Lo ejecuté al principio de esta auditoría, sin resistencia, y con eso construí B-01. El fichero está
en git, en texto plano, en el mismo repo que el árbol que evalúa. **Cualquiera que tenga el repo
tiene el examen** — y eso incluye a todo agente que se clone COSMOS, que es precisamente el
público objetivo del proyecto.

El sello protege contra el descuido (mirar el `--detalle`). No protege contra la lectura, que cuesta
un comando. Un holdout que viaja con el sistema que evalúa no es un holdout: es un ejercicio
resuelto.

**Fix.** El fichero de validación sale del árbol versionado: a `~/.cosmos/holdout/` fuera del repo,
o al vault, o cifrado con una clave que no esté en el repo. `acertar` lo busca por ruta configurable
y, si no lo encuentra, dice `validación: NO DISPONIBLE` — nunca un número. Y `.gitignore` con un
test que falle si alguien lo vuelve a añadir.

**Riesgo.** Alto. Es la premisa de la que cuelga toda la honestidad de la cifra.

---

## B-03 · CRÍTICO — La única guarda anti-Goodhart vigila el lado equivocado, y felicita al tramposo

`cosmos/acertar.py:463-473` (`formatear_contraste`) es el mecanismo anti-sobreajuste del proyecto:

```python
if brecha >= 10:      # ajuste muy por encima de validación
    ...  "parte de lo ganado es puntería sobre las preguntas conocidas"
elif brecha <= -5:    # validación por encima de ajuste
    ...  "La validación va por delante: el conjunto de ajuste se ha quedado corto."
```

`brecha = ajuste − validación`. La rama que alarma es la de sobreajustar al conjunto **de ajuste**,
que es el que a nadie le importa proteger: está para mirarlo. La rama del caso grave —sobreajustar
al **holdout**— cae en `brecha <= -5` y devuelve **un piropo**.

Con el árbol inflado de B-01 (ajuste 64, validación 100, brecha −36) el comando imprimió, literal:

```
  La cifra que vale es 100 %.
  (holdout SELLADO: el detalle por encargo no se enseña, que es lo que quema)
  La validación va por delante: el conjunto de ajuste se ha quedado corto.
```

Tres frases y las tres engañan a la vez: bendice el 100 %, sigue afirmando que el holdout está
sellado, y lee el síntoma exacto del fraude como un elogio al conjunto de validación.

**Fix.** Invertir la gravedad. Una brecha muy negativa es la señal MÁS grave que este sistema puede
emitir, no la más tranquilizadora: `brecha <= -15` → aviso rojo, «la validación va muy por encima
del ajuste: o el holdout se filtró, o el ajuste está roto; la cifra NO es publicable». Y `--minimo`
debería salir 1 en ese estado, pase la nota que pase.

**Riesgo.** Alto. Es el detector convertido en cómplice.

---

## B-04 · GRAVE — La regla de corrección no está guardada: aflojarla sube la nota con la suite verde

`_acierta` (`cosmos/acertar.py:226-229`) decide qué cuenta como acierto. Es el criterio de
corrección del examen, y **nada lo fija**. Lo aflojé con un cambio que suena razonable —«llegar al
oficio ya es medio camino», aceptar también el ancestro— en `$SP/sabj2`:

```python
return (elegida == esperada or elegida.startswith(esperada + "/")
        or esperada.startswith(elegida + "/"))   # <- lo añadido
```

```
  Ajuste ......... 35/50 (70 %)     (era 66 %)
  Validación ..... 9/20 (45 %)      (era 40 %)
  La cifra que vale es 45 %.

python3 -m unittest discover -s tests
Ran 259 tests in 83.151s
OK (skipped=2)                      <- EXIT_SUITE=0
```

**259 tests en verde y la nota sube 5 puntos.** Ni la suite ni la batería de mutación tienen una
invariante sobre la severidad del corrector. Contrasta con el sabotaje burdo (`acierta=True`
siempre), que sí se caza — pero solo con **2 tests**, frente a los 57 fallos + 29 errores que
provoca sabotear el validador. El juez está un orden de magnitud peor protegido que lo que juzga.

**Fix.** Mutación dedicada en `puente/tests/mutaciones.py`: aflojar `_acierta` en cada dirección y
exigir rojo. Más un test de tabla que fije el criterio con casos límite explícitos
(`("web", "web") → True`, `("web/formularios", "web") → False`, `("web", "web/formularios") → True`).

**Riesgo.** Alto. Es la palanca más limpia que existe: no toca el árbol, no toca el holdout, no deja
huella en `validar` y sube la cifra publicable.

---

## B-05 · GRAVE — El holdout lo escribió quien ajusta el árbol, y con el árbol delante

El propio registro lo declara, y hay que reconocerle la honestidad
(`registro/commits/universo/2026/09/camino-al-diez.md:57`):

> «Esperas verificadas solo por existencia contra el árbol; escritos sin mirar resúmenes ni ranking
> — el mismo estatus epistémico que los originales, declarado: **quien los escribió ha visto el
> árbol entero hoy**, y por eso el sello importa.»

Eso no es un holdout independiente: es un examen escrito por el profesor que también escribe los
apuntes, el mismo día, con los apuntes delante. «Sin mirar resúmenes» es una promesa de disciplina,
no una garantía estructural — y el commit que creó el holdout (`1f9375c`) tocó **en el mismo
diff** `cosmos/acertar.py` (el motor que puntúa) y `galaxia/agua/rio-buscar.md` (contenido del
árbol). Examen y sistema evaluado, escritos juntos.

Lo que **sí** verifiqué y limpia parcialmente la sospecha: después de sellar (`1f9375c..HEAD`) la
galaxia solo cambió en 40 ficheros con diffs de 2 líneas cada uno, del commit «los límites de la
máquina vieja salen del contenido». Nadie ajustó resúmenes contra el holdout después de verlo.

**Corroboración independiente.** Escribí mi propio conjunto de 20 consultas
(`$SP/control-revisorB.json`), una por oficio, sin leer ningún resumen del árbol, y da **45 %**
contra el **40 %** del holdout sellado. Las dos cifras concuerdan. **Eso es lo que hace creíble el
40 % como estimación**, mucho más que el sello.

**Fix.** La siguiente tanda de encargos la dicta Darío, o sale de tickets/consultas reales, o la
escribe un agente al que no se le enseña la galaxia. Y se declara la procedencia en el fichero.

**Riesgo.** Medio-alto. Hoy el número resulta ser correcto (lo corroboré), pero la propiedad que lo
haría fiable no existe.

---

## B-06 · GRAVE — n=20: publicar «40 %» es precisión falsa

El holdout tiene 20 encargos, uno por oficio. Cada acierto vale 5 puntos porcentuales.

```bash
python3 -c "
import math
for k,n in ((8,20),(33,50)):
    p=k/n; z=1.96; den=1+z*z/n
    c=(p+z*z/(2*n))/den
    h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    print(f'{k}/{n} = {100*p:.0f}%  IC95 Wilson = [{100*(c-h):.1f}%, {100*(c+h):.1f}%]')"
```

```
8/20 = 40%  IC95 Wilson = [21.9%, 61.3%]
33/50 = 66%  IC95 Wilson = [52.2%, 77.6%]
```

La validación es **40 % ± 20 puntos**. Un solo encargo distinto mueve la cifra 5 puntos. Y los dos
intervalos **se solapan** ([52,2 – 77,6] contra [21,9 – 61,3]): con estos tamaños ni siquiera se
puede afirmar con rigor que ajuste y validación difieran, que es justo la afirmación sobre la que
descansa toda la narrativa de la brecha de 26 puntos.

**Fix.** Publicar siempre `40 % (IC95 22–61, n=20)`. Y subir el holdout a n≥100 — con 5 encargos por
oficio el intervalo baja a ±10.

**Riesgo.** Medio. No engaña a nadie sobre la dirección, pero convierte ruido en narrativa.

---

## B-07 · GRAVE — El aviso de sello roto y el veredicto se contradicen en la misma salida

Edité **una** consulta del holdout en `$SP/sello` (facilitándola) y ejecuté `acertar`:

```
AVISO: el conjunto de validación cambió después de sellarse; su cifra no es publicable
       hasta volver a sellarlo con --sellar.
  Validación ..... 8/20 (40 %)   escritos aparte; no guían ninguna decisión
  La cifra que vale es 40 %.
EXIT=0
```

El aviso dice «no es publicable» y cuatro líneas después el mismo comando dice «**La cifra que
vale** es 40 %», y sale 0. Quien lee de abajo arriba —o quien copia la última línea a un informe—
se lleva la cifra que acaba de declararse inválida. Es el patrón «un valor mostrado no es un valor
conocido»: aquí el sistema *sabe* que no lo sabe y lo publica igual.

**Fix.** Con el sello roto, la línea del veredicto se sustituye por `La cifra de validación NO es
publicable (sello roto)` y `--minimo` sale 1.

**Riesgo.** Medio.

---

## B-08 · MEDIO — La cifra se mueve 10 puntos según una decisión de modelado que nadie ha fijado

El juez puntúa `f"{ruta_completa} {resumen}"`. El agente lee un **árbol indentado** donde el nombre
del ancestro aparece una vez, en la línea del padre, no repetido en cada hijo. El docstring lo
justifica («la información que la indentación le da al agente, dicha en palabras»), y es defendible
— pero no es gratis. Puntuando el texto que el agente **literalmente lee en esa línea**:

```
ajuste      con ruta (lo publicado): 33/50 (66 %)  |  solo lo que el agente ve: 35/50 (70 %)
validacion  con ruta (lo publicado):  8/20 (40 %)  |  solo lo que el agente ve:  6/20 (30 %)
```

En el conjunto que decide, la elección de modelado vale **10 puntos** —una cuarta parte de la
cifra— y va a favor del número publicado. Medido, el juez puntúa un 4,5 % más de palabras que las
que el render enseña (5.704 frente a 5.458, con los mismos nichos activos).

**Fix.** Fijar la decisión con un test que compare ambas variantes y publicar la sensibilidad junto
a la cifra, o —mejor— puntuar exactamente la línea renderizada.

**Riesgo.** Medio.

---

## B-09 · MEDIO — El holdout no cubre el árbol entero

```
oficios en el árbol      : 22
oficios en la validación : 20  (uno por oficio)
ausentes                 : rendimiento, visibilidad
```

Dos oficios no se evalúan nunca en el conjunto que decide, y ambos existen en el de ajuste. Un
resumen que empeore ahí no lo ve nadie. Además, 17 de los 20 esperan un oficio de primer nivel: la
profundidad real del árbol (pueblos a 4 niveles) apenas se examina.

**Fix.** Cobertura obligatoria de los 22 oficios y al menos un tercio de encargos que esperen un
nodo de profundidad ≥ 3. Test que falle si un oficio se queda sin encargo.

**Riesgo.** Medio.

---

## B-10 · MEDIO — Las dos pruebas que verifican el medidor no se ejecutan en esta máquina

```
Ran 259 tests in 77.669s
OK (skipped=2)
```

Los dos saltos son el mismo motivo, y son precisamente las que validan lo que el medidor publica:

```
El margen se comprueba sobre lo que el medidor cuenta de verdad. ... skipped
  'SIN TOKENIZADOR: el margen publicado (±5,2 %) NO se ha verificado en esta ejecución.'
CANARIO, no invariante: afirma un defecto abierto ... skipped
  'sin tokenizador no se puede medir el veredicto exacto'
```

**No es un salto silencioso** —avisan con el motivo y hay `COSMOS_EXIGE_TOKENIZADOR=1` para
convertirlo en fallo; eso está bien hecho—. El problema es de operación: `/tmp/calib/bin/python`,
el intérprete que el registro nombra para reproducir la calibración, **ya no existe** (`/tmp` se
vacía). El resultado práctico es que el margen ±5,2 % que aparece en cada salida de `medir` llevaba
sin verificarse desde el reinicio de la máquina.

**Fix.** El venv de calibración fuera de `/tmp` (`~/.cosmos/calib/`), con `docs/CALIBRACION.md`
apuntando ahí, y `COSMOS_EXIGE_TOKENIZADOR=1` en el CI.

**Riesgo.** Medio-bajo: lo recalculé y sale bien (abajo). Pero nadie lo sabía.

---

# LO QUE AGUANTÓ EL ATAQUE — y es mucho

Fui a por estas siete afirmaciones para tumbarlas y no pude. Se sostienen.

**1. El medidor no convierte «no medido» en cero.** La regla de la casa se cumple:

```bash
python3 -m cosmos medir --metodo exacto > $SP/exacto.out 2>&1; echo "EXIT_EXACTO=$?"
```
```
EXIT_EXACTO=1
COSMOS  medir  rojo
se pidió método exacto, pero no hay tokenizador local
```

Falla explícito, sale 1, no inventa un número plausible. Y el `Veredicto` es **trivalente**
(`cabe: bool | None`): sobre un árbol vacío dice «SIN MEDIR», no «OK, quedan 4.000».

**2. La calibración es honesta.** Recalculé los tres factores sobre el corpus de HOY con tiktoken
real (`$SP/recalibrar.py`, 291 + 24 + 50 muestras):

| Clase | n | Medido hoy | Publicado | Desvío |
|---|---:|---:|---:|---:|
| prosa | 291 | 1,227 | 1,204 | +1,9 % |
| generado | 24 | 1,361 | 1,381 | −1,4 % |
| estructura | 50 | 1,321 | 1,314 | +0,5 % |

Los tres dentro del ±2 %. El factor 1,369–1,381 del enunciado se confirma en 1,361. Y contrastando
métodos sobre el árbol real: exacto **3.654** tok contra aproximado **3.546** — el aproximado
subestima un **3,0 %**, dentro del ±5,2 % declarado y en la dirección que el propio código admite.

**3. La portería no se ha movido.** El techo de 4.000 tokens de entrada:

```bash
git log --oneline -S"4000" -- cosmos.toml spec/ GOAL.md
9d4b6e3 feat(cosmos): nucleo normativo, plan maestro y validador funcionando
8265813 feat(cosmos): contrato GOAL + taxonomia y specs de validador y medidor
```

Dos commits, ambos **fundacionales**. Nadie ha subido el techo para que cupiera el contenido. Es
justo lo contrario de lo que buscaba.

**4. La batería de mutación es real, no decorativa.**
`python3 -m puente.tests.mutaciones` → **`59/59 invariantes vistas fallar`**, EXIT=0. Cubre
`acertar`, `medir`, `buscar`, `juez`, `validar`, `cli` y hasta ficheros de la galaxia. M57 y M58 son
específicamente del juez y del holdout.

**5. El meta-test del validador se ve fallar de verdad.** No me fié de leerlo: rompí el validador
en `$SP/sab` (`COMPROBACIONES = ()`, siempre verde) y corrí la suite entera:

```
Ran 254 tests — FAILED (failures=57, errors=29, skipped=2)   EXIT_SUITE=1
```

Un validador siempre verde no sobrevive a la batería.

**6. Render y contra-métrica comparten código de verdad, no coinciden por casualidad.**
`acertar._lineas_del_catalogo` **importa** `medir.nodos_de_catalogo` (`cosmos/acertar.py:43`), la
misma función que llama `medir.catalogo_visible`. Es una sola fuente de selección, no dos caminos.
Verificado en el código y guardado por la mutación M57.

**7. El juez con modelo no gasta dinero y falla limpio.**
`python3 -m cosmos acertar --juez llama3` → `EXIT=2`, «no hay servidor de modelos en
`http://localhost:11434`… Este comando no arranca ninguno». Cero API, cero coste. Y solo corre sobre
el conjunto de ajuste.

**Extras que también aguantaron:** el `--json` redacta el detalle del holdout (comprobado: devuelve
el texto `SELLADO: …` en vez de los resultados). `--minimo` cobra sobre la **validación**, no sobre
el ajuste (`--minimo 39` → 0, `--minimo 41` → 1), que era un defecto de la revisión anterior y está
cerrado. Los tests **no fijan cifras a mano**: `test_cifras_de_las_specs.py` las calcula desde el
repo, así que afirman lo medido y no lo deseado. La suite son **259 tests** hoy (el PROGRESS que
dice 47 está caducado), verde, sin fallos.

---

# VEREDICTO

### ¿Es honesta la nota publicada?

**El 75 % del enunciado es FALSO hoy — y el repo ya lo sabe.** Ese número sale del conjunto
`encargos-validacion-quemada-2026-09-02.json`, contaminado, y el propio comando lo grita al
ejecutarlo: «YA MIRADO: es una segunda cifra de ajuste… la cifra honesta es DESCONOCIDA». Quien
siga citando 66/75 está citando una cifra retirada. La cifra viva es:

```
  Ajuste ......... 33/50 (66 %)
  Validación ..... 8/20 (40 %)
  La cifra que vale es 40 %.
  Y la brecha es de 26 puntos: parte de lo ganado es puntería sobre las preguntas conocidas.
```

**Eso sí es honesto, y hay que decirlo claro:** el proyecto se bajó a sí mismo la nota de 75 a 40,
publicó la brecha de 26 puntos que lo delata, y escribió en el registro «la cifra publicable del
árbol hoy es 40 %, no se maquilla y no se persigue». Es lo contrario de una métrica autocomplaciente
y merece reconocerse. Mi conjunto de control independiente (45 %) lo corrobora.

**Pero el 40 % no es una nota defendible como está**, por tres razones que no arreglan las buenas
intenciones:

1. **El examen viaja dentro del repo** (B-02) y basta un `cat` para tenerlo.
2. **Subirlo al 100 % cuesta un script de 40 líneas** y deja `validar` verde, `medir` más barato y
   `--minimo 95` en 0, mientras el árbol empeora de verdad (B-01). Ninguna puerta lo detiene.
3. **El detector de sobreajuste felicita al que lo hace** (B-03), y la regla de corrección se puede
   aflojar con la suite entera en verde (B-04).

Una nota que sube sin que el sistema mejore es peor que no tener nota. Hoy COSMOS tiene esa nota:
no porque la haya inflado —no lo ha hecho—, sino porque **nada le impediría hacerlo, ni se enteraría
si otro lo hace**. La honestidad de la cifra descansa hoy en la disciplina de quien la calcula, no en
el diseño. Y ese es exactamente el fallo que la contra-métrica existía para cerrar.

### Nota defendible hoy

**Acierto del árbol: 40 %, con intervalo de confianza [22 %, 61 %] (n=20)** — y con el asterisco de
que ±10 puntos dependen de una decisión de modelado sin fijar (B-08). Redondeando honestamente:
**«en torno a 4 de cada 10, con margen ancho»**. Mi medición independiente da 45 %, coherente.

**Nota del sistema de evaluación —que es lo que se me pidió juzgar— : 6/10.**
No es un 10, y la distancia al 10 está medida, no opinada. Los instrumentos son de primera (medidor
trivalente, calibración verificada, 59/59 mutaciones, meta-test que se ve fallar, techo intacto): eso
vale un 9. El juez es el eslabón que no aguanta: examen en el repo, inflado trivial, detector
invertido y corrector sin guardas. Como el juez es quien decide si todo lo demás sirve para algo, se
lleva la nota por delante.

**Para llegar al 10** hay que cerrar B-01, B-02, B-03 y B-04. Son cuatro cambios acotados, ninguno
arquitectónico, y los cuatro tienen fix escrito arriba. Con ellos —y con n≥100 (B-06)— la cifra que
publique COSMOS será defendible aunque quien la calcule quiera engañarse.

---

# MEJORAS, en orden de lo que más cierra

1. **Sacar el holdout del repo** (B-02). Ruta configurable fuera del árbol; sin fichero, `validación:
   NO DISPONIBLE`, nunca un número. Test que falle si vuelve a versionarse.
2. **Invertir la gravedad de la brecha** (B-03). `brecha <= -15` es la alarma más grave del sistema,
   no un elogio; y `--minimo` sale 1 en ese estado.
3. **Guardar la regla de corrección** (B-04). Mutaciones que aflojen `_acierta` en las dos
   direcciones + tabla de casos límite.
4. **Canario de destrucción de resumen** (B-01). Si un `resumen` pierde >40 % de sus términos
   distintos y la nota sube, rojo pidiendo revisión humana.
5. **Conjunto de control rotatorio**, regenerado desde una fuente que el que ajusta no controla, con
   su cifra publicada al lado de la validación. La divergencia es el detector.
6. **Publicar siempre el intervalo** (B-06) y subir el holdout a n≥100, cubriendo los 22 oficios y
   con un tercio de encargos a profundidad ≥ 3 (B-09).
7. **Fijar el texto puntuable** (B-08): puntuar la línea renderizada, o publicar la sensibilidad.
8. **Venv de calibración fuera de `/tmp`** y `COSMOS_EXIGE_TOKENIZADOR=1` en CI (B-10).
9. **Arreglar la salida contradictoria del sello roto** (B-07).

---

## Anexo — cómo reproducir todo esto

```bash
SP=<scratchpad>
PYCAL=$SP/calib/bin/python        # venv con tiktoken; python3 -m venv + pip install tiktoken

cd ~/cosmos
python3 -m cosmos validar                                    # verde 0 errores
python3 -m cosmos acertar                                    # 66 % / 40 %, brecha 26
python3 -m cosmos medir                                      # 3.546 tok, OK quedan 454
$PYCAL  -m cosmos medir --metodo exacto                      # 3.654 tok, OK quedan 346
python3 -m cosmos medir --metodo exacto >/dev/null 2>&1; echo $?   # 1, sin tokenizador
python3 -m unittest discover -s tests                        # Ran 259 — OK (skipped=2)
python3 -m puente.tests.mutaciones                           # 59/59 invariantes vistas fallar
$PYCAL  $SP/recalibrar.py                                    # factores de hoy vs publicados
```

Scripts del experimento, todos en `$SP` y todos operando sobre copias:
`inflar.py` / `inflar2.py` (inflado de la nota) · `recalibrar.py` (factores) ·
`control-revisorB.json` (mis 20 consultas independientes).

**Ni un byte de `~/cosmos` fue modificado salvo este informe.** Comprobable:
`git -C ~/cosmos status --porcelain` solo debe listar `progress/auditoria-360-2026-09-03/B-juez.md`.
