# F — Seguridad, licencias y honestidad del registro

Revisor F de la auditoría 360 de COSMOS. Ángulo exclusivo: fuga de secretos y datos privados
(árbol **e historia**), el escáner que dice protegerlos, licencias y atribución de lo ajeno,
herramientas ofensivas, superficie de ejecución, y **si lo que afirma el registro se sostiene hoy**.

Premisa de trabajo, por encargo: *este repo filtra algo y su registro se adorna*. Las dos cosas
resultaron ciertas, pero **menos de lo que la premisa sugería y por vías distintas a las esperadas**.
Lo que está limpio va al final, medido, porque un informe que solo publica lo que falla también miente.

---

## Pin de estado

```
$ git -C ~/cosmos rev-parse HEAD
b0c1ebdeb2d9bac7e068d10714213ff2f9eda926
$ git -C ~/cosmos status --porcelain | wc -l
       1          # solo progress/auditoria-360-2026-09-03/ (esta misma auditoría)
```

`main` es el merge de tres padres `048d0866` + `ed970d15` + `4698bed6`.

**Ramas y rango barridos** — no solo `main`:

| Ref | Barrida |
|---|---|
| `main`, `historia-limpia`, `respaldo-antes-reescritura`, `respaldo-main-20260903`, `trabajo-2026-09-02` | sí |
| `origin/main`, `origin/historia-limpia`, `origin/limpia-2026-09-02`, `origin/trabajo-2026-09-02` | sí |
| `refs/original/refs/heads/trabajo-2026-09-02` (respaldo de `filter-branch`) | sí |
| Objetos colgantes (`git fsck --lost-found`) | sí |

**Cobertura**: 133 commits, 3.206 objetos, **todos los blobs de texto alcanzables desde cualquier
ref** — no `git log -S` sobre una lista de patrones, que es lo que deja pasar lo que no se buscó.

**Método**: solo lectura sobre `~/cosmos`. Todo experimento destructivo corrió sobre un clon
`--no-hardlinks` en el scratchpad. Cero commits, cero push, cero reescritura de historia.
Instrumento del barrido: los **propios patrones del repo** (`puente.secretos.PATRONES` +
`_primera_sensible`, para no discutir con su criterio) más tres patrones míos que él no tiene
(ruta absoluta de máquina, IP pública, dominios de la agencia).

**Efecto colateral que declaro** (regla 9 del revisor adversarial: lo que se desvía se dice, no se
niega): ejecutar la suite documentada del repo **creó** `.cosmos/saltos.log`, que no existía al
pinear. Es el hallazgo F-06. Fichero generado y `gitignore`-ado; el árbol versionado no se tocó.

Secretos **censurados**: fichero + tipo + 4 primeros caracteres. Ningún valor entero en este informe.

---

## Hallazgos

### F-01 · CRÍTICO — La lista de excepciones blanquea *(fichero × clase de patrón)* para siempre, no un valor

El escáner es bueno. Su lista de excepciones lo desarma.

`cosmos.guardarrailes.clave_hallazgo` **borra el número de línea** de la clave de comparación, a
propósito y con un motivo razonable escrito al lado (*«mover código no convierte lo viejo en
nuevo»*). El efecto real es que la excepción

```
ruta#db0d46f684d1:550: posible clave secreta AWS
```

se compara como `ruta#db0d46f684d1: posible clave secreta AWS`. Es decir: **ese fichero queda
indultado para esa clase de patrón, en cualquier línea y con cualquier valor, para siempre.**

Lo agrava `escanear_flujo`, que con `reportadas.add(etiqueta)` emite **solo el primer hallazgo de
cada patrón por fichero**. Los dos mecanismos se suman: en un fichero indultado, el primer valor que
aparezca absorbe el indulto y **el resto ni se mira**.

**Reproducción copiable** (sobre un clon, no sobre el repo):

```bash
git clone --no-hardlinks ~/cosmos /tmp/f01 && cd /tmp/f01
python3 -m puente.secretos --todo      # → "limpio de nuevos; 3 hallazgo(s) inventariado(s)", exit 0

python3 - <<'PY'
from pathlib import Path
p = Path('progress/revision-profunda-2026-09-02/INFORME.md')      # fichero indultado
t = p.read_text().splitlines()
t.insert(5, 'AWS_SECRET_ACCESS_KEY=' + 'Kp9Q' + 'Vn2Lt6Zx4Ry8Wc1Md3Bh7Fj0Ns5Tg8Uv2Ae')
p.write_text('\n'.join(t) + '\n')
PY
git add -A && python3 -m puente.secretos --todo; echo "EXIT=$?"
```

Salida medida:

```
CONOCIDO: ruta#25dacd7d542a:350: posible clave AWS
CONOCIDO: ruta#db0d46f684d1:6: posible clave secreta AWS      ← línea 6, NO la 550 inventariada
CONOCIDO: ruta#db0d46f684d1:6: posible secreto asignado
secretos: limpio de nuevos; 3 hallazgo(s) inventariado(s) en secretos-conocidos.txt
EXIT=0
```

Segunda prueba, misma mecánica sobre el otro fichero indultado: una `AKIA…` distinta y de forma
válida insertada en `tests/test_guardarrailes.py` sale como `ruta#25dacd7d542a:4: posible clave AWS`
— **CONOCIDO, exit 0**. Dos credenciales nuevas, distintas y no-ejemplo, atravesaron el gate en
silencio. El único rastro es un número de línea que el propio diseño declara irrelevante.

**Por qué es crítico y no medio**: los dos ficheros indultados son exactamente los que un humano no
revisa — un informe de 900 líneas y un fichero de tests. Y el encabezado de `secretos-conocidos.txt`
promete lo que el mecanismo no puede cumplir: *«Solo entran valores que NO son credenciales… Nunca
una credencial real "que ya esta rotada"»*. Esa garantía es sobre **valores**; la clave es sobre
**ficheros**.

**Fix** — la clave de la excepción tiene que incluir el valor, no la ruta:

1. En `_hallazgo`, añadir `sha256(coincidencia.group(0))[:12]` al texto del hallazgo, y que
   `clave_hallazgo` conserve **ese** resumen aunque siga tirando la línea. Un valor distinto = una
   clave distinta = hallazgo nuevo = rojo. Sigue cumpliendo «mover código no lo hace nuevo».
2. Quitar el `reportadas.add(etiqueta)` o acotarlo por valor: hoy un fichero con dos secretos de la
   misma clase solo confiesa uno.
3. Regenerar `secretos-conocidos.txt` con las tres entradas re-expresadas por hash de valor.

**Riesgo si no se toca**: el repo puede publicar una credencial real con el escáner en verde, y el
verde es precisamente lo que hace que nadie mire.

---

### F-02 · ALTO — Un CIF español auténtico sigue vivo en la historia publicada, incluida la rama `historia-limpia`

`galaxia/pueblos/validadores-frontera/SKILL.md` y `cosecha/nif-cif-validator.js` llevaron un
identificador fiscal `B039…` (CIF español de 9 caracteres, **dígito de control correcto**: no es un
relleno) usado como si fuera un ejemplo.

Se **corrigió hacia adelante** — hoy el árbol dice `B00000000`, que sí está en `VALORES_DE_EJEMPLO`
— pero **nunca se purgó la historia**. Sigue alcanzable desde:

```
$ git log --all --oneline -S'B039…'
3a655b5  docs(registro): partes de la tercera pasada y del cierre de H15     ← lo QUITA
4c06e72  fix(secretos): ensenar al escaner en vez de callarlo …              ← lo PROPAGA a un 2º fichero
b05e7a0  chore(cosecha): 86 herramientas genericas, verificadas sin datos de cliente   ← lo INTRODUCE
```

Blob `c71218cf`, alcanzable desde **`origin/main`, `origin/historia-limpia`,
`origin/limpia-2026-09-02`, `origin/trabajo-2026-09-02`** y sus cuatro equivalentes locales, más
`refs/original/`. La reescritura de historia no lo tocó: el juego de rutas que `historia-limpia`
elimina respecto de `respaldo-antes-reescritura` son 162 versiones de ficheros de contenido
ordinario, ningún dato sensible.

**Que es auténtico no es opinión mía**: el propio arnés lo tiene escrito. En
`~/<arnes>/memory/feedback-ensenar-al-escaner-no-callarlo.md:26` —
*«un CIF auténtico (`B039…`) … ese CIF auténtico estaba en el repo disfrazado de ejemplo»*. Y el
valor aparece en los datos de cliente del workspace (`projects/TrueRanker-Ops/progress/omnia-enrich/…`)
junto al nombre de una constructora real y su dominio. **No reproduzco aquí ni el CIF entero ni el
nombre de la empresa**: el puntero al fichero basta para quien tenga que arreglarlo.

**Fix**: el repo es privado hoy, así que hay tiempo, pero el registro declara intención de
compartirlo y esto no se arregla con un commit.

1. Antes de cualquier publicación: `git filter-repo --replace-text` con el valor, sobre **todas**
   las refs, incluidas `refs/original/*` y las cuatro ramas remotas; luego `git push --force` a las
   cinco y borrar las ramas de respaldo del remoto.
2. Borrar `refs/original/refs/heads/trabajo-2026-09-02` y `git reflog expire --expire=now --all &&
   git gc --prune=now` en local, o los objetos siguen vivos en el clon de cada uno.
3. Como el CIF es de un tercero identificable, la decisión de si esto es una brecha RGPD **no es
   mía**: se eleva a Darío. Mientras el repo sea privado, no lo es.

**Riesgo**: publicar el repo tal cual expone el identificador fiscal de una empresa cliente, en un
repositorio cuyo argumento de venta es que sabe detectar exactamente eso.

---

### F-03 · ALTO — 1.400+ líneas de código ajeno redistribuidas sin licencia, sin autor y sin URL

El catálogo tiene una disciplina de atribución **casi perfecta** (medido en F-limpio-5: 208 de 209
fichas con URL + licencia + estrellas + fecha comprobada). Se rompe exactamente donde importa: en
las fichas que no solo *catalogan* una herramienta ajena sino que **redistribuyen su código**.

Comprobado por identidad de bytes, no por parecido:

| Fichero en COSMOS | Origen | Líneas | Atribución en su ficha |
|---|---|---|---|
| `galaxia/pueblos/auditor-de-skills/scripts/skill_security_auditor.py` | `github.com/alirezarezvani/claude-skills` | 1.066 | ninguna |
| `galaxia/pueblos/auditor-de-skills/references/threat-model.md` | idem | 271 | ninguna |
| `galaxia/pueblos/consola-interactiva-tmux/scripts/tmux-wrapper.sh` | skill `using-tmux-for-interactive-commands`, publicada por **Anthropic** | 84 | ninguna |

```bash
diff -q ~/cosmos/galaxia/pueblos/auditor-de-skills/scripts/skill_security_auditor.py \
        ~/<arnes>/.claude/skills/skill-security-auditor/scripts/skill_security_auditor.py
# (sin salida: idénticos)
```

El origen de la primera está documentado en el propio arnés
(`notes/inbox/skill-install-2026-06-13.md`: *«skill-security-auditor | github.com/alirezarezvani/claude-skills»*).

Lo que dice la ficha de COSMOS es:

> *«Rescatado de la skill `skill-security-auditor` de un arnes **propio**.»*

**«De un arnés propio» describe dónde estaba instalada, no de quién es.** La misma fórmula literal se
usa en `extractor-de-curso` (donde sí es de Darío) y aquí, donde no lo es — así que la frase que
debería distinguir lo propio de lo ajeno es justo la que borra la diferencia. Ninguna de las tres
fichas nombra autor, URL ni licencia.

Detalle que lo confirma solo: de las 209 fichas con URL de GitHub, **`auditor-de-skills` es la única
que no trae licencia ni estrellas ni fecha comprobada**. La única ficha sin atribución es la única
que redistribuye código ajeno entero.

**Fix**: en las tres fichas, la misma línea que ya llevan las otras 208 — URL del repo de origen,
licencia leída en su `LICENSE` (no la que reporta la API), autor y fecha de comprobación. Si la
licencia de `alirezarezvani/claude-skills` no permite redistribución, el guion no viaja: se cataloga
y se enlaza, que es lo que hacen las otras 206 fichas sin ningún problema.

**Riesgo**: incumplimiento de licencia en el momento de publicar, en un repo que además tiene una
ficha llamada `cumplimiento--licencias.md`.

---

### F-04 · MEDIO — El repo no declara licencia propia

```bash
$ ls ~/cosmos | grep -iE 'licen|copying|notice'   # nada
$ git ls-files | grep -iE 'licen|copying|notice'
galaxia/paises/cumplimiento--licencias.md          # una ficha del catálogo, no una licencia
```

Sin `LICENSE`, el estado por defecto es «todos los derechos reservados»: **nadie puede reutilizar
COSMOS legalmente**, que es lo contrario de lo que el registro dice querer. Y sin `NOTICE` no hay
dónde acumular las atribuciones que exige F-03 ni la de aider (Apache-2.0).

**Fix**: añadir `LICENSE` (la elección es de Darío) y un `NOTICE` con las tres atribuciones de F-03
más el crédito a aider que hoy solo vive en un comentario de código.

---

### F-05 · MEDIO — Un volcado con datos de terceros, borrado del árbol y vivo en `origin/main`

`research/scratch/q14_analytics.txt` (101 KB, blob `94384193`) ya **no está en el árbol**, pero sigue
alcanzable desde `main` y `origin/main` en el commit `3d75020e`.

Es la salida de `research/scratch/gh_search.sh`. En su línea 13, una de las «descripciones» de repo
capturadas no es una descripción: es **una página HTML completa de GitHub**, con lo que eso arrastra:

| Dato | Muestra censurada |
|---|---|
| Correo de un tercero (no de la agencia) | `kebi…@gmail.com` |
| `csrf-token` de la sesión que hizo la captura | `FL2z…` |
| IP pública | `1.23…` |

Severidad **media y no alta** porque nada de eso es de Darío ni de la agencia, el token de CSRF está
muerto hace días y el correo procede de una página pública de GitHub. Pero es dato personal de un
tercero en un repositorio, y llegó ahí porque **el escáner no mira la historia**: `puente.secretos`
solo recorre `git ls-files --stage`, es decir el índice. Un fichero borrado queda fuera de su vista
para siempre.

**Fix**:
1. Incluir en la purga de F-02 (mismo `filter-repo`, mismo empujón).
2. Añadir un modo `--historia` al escáner que recorra `git rev-list --objects --all`. Cuesta
   ~90 s sobre este repo entero (medido) y se puede colgar de CI en vez del pre-commit.
3. `gh_search.sh` debe truncar cada campo antes de escribirlo: una descripción de repo no ocupa 40 KB.

---

### F-06 · MEDIO — Un test escribe un salto REAL de E16 en el repositorio real, y con concurrencia no lo limpia

`tests/test_toda_puerta_tiene_salida.py:183` registra deliberadamente un salto de **E16** —la
invariante de presupuesto, que `spec/VALIDADOR.md` llama *«el punto entero del proyecto»*— en el
`.cosmos/saltos.log` **del repositorio real**, no en un temporal. El comentario del propio test
explica por qué (un repo en `/tmp` no encuentra la válvula) y confía en un `try/finally` para
deshacerlo.

El `try/finally` es un ciclo leer-modificar-escribir sin exclusión mutua. Reproducido a la primera
iteración sobre un clon:

```bash
cd /tmp/f01 && rm -f .cosmos/saltos.log
( python3 -m unittest tests.test_toda_puerta_tiene_salida.LasDosPuertasDelPresupuestoAbrenIgual & \
  python3 -m unittest tests.test_toda_puerta_tiene_salida.LasDosPuertasDelPresupuestoAbrenIgual & wait )
cat .cosmos/saltos.log
```

```
{"caduca":"…T08:01:45Z","codigo":"E16","creado":"…T08:00:45Z",
 "motivo":"prueba: la puerta del presupuesto tiene que abrir"}
```

Un salto **vivo** de la invariante de presupuesto, dejado en el repo por un test. Ejecutado en
serie el mismo test limpia bien; ejecutado dos veces a la vez, no. Y ocurrió de verdad hoy en
`~/cosmos` (dos entradas, 07:55 y 07:57 UTC) porque otras sesiones de esta misma auditoría estaban
trabajando en el repo a la vez.

**Lo que salva la situación, y lo digo porque es mérito del diseño**: la ventana es de 60 s y
**el salto activo se declara siempre en la cabecera**, no en silencio. Medido:

```
COSMOS  rojo (1 salto activo: E16, caduca en 1 d)  1 errores
```

Por eso es MEDIO y no ALTO: hay estado falso, pero **no hay verde silencioso**.

**Fix**: el test debe apuntar `ruta_saltos` a un repo de usar y tirar (exportar el índice con
`git checkout-index`, como ya hace `puente/gate.py`, que resuelve exactamente este problema), o
tomar el `cerrojo` del repo mientras dura. Añadir además un canario que falle si la suite deja
`.cosmos/saltos.log` tras de sí.

---

### F-07 · MEDIO — El índice que se inyecta en cada sesión dice «Veintiun oficios» y hay 22

```bash
$ grep -cE '^- [a-z-]+:' galaxia/COSMOS.md ; ls galaxia/sistemas | wc -l ; ls galaxia/estrellas | wc -l
22
22
22
$ sed -n 3p galaxia/COSMOS.md
Veintiun oficios, seis mares que los cruzan y cinco oceanos siempre presentes; …
```

Igual en `galaxia/galaxia.md`. El commit `92c8064` (2026-09-02 14:22) —*«rendimiento se parte en dos
oficios»*— actualizó **la lista** de `galaxia/COSMOS.md` y dejó **la prosa** de la línea 3 intacta.

Pesa más de lo que parece por dos razones. Primera: `galaxia/COSMOS.md` es parte de la *entrada
base* (555 tok de 1.343 según `cosmos medir`), o sea que el número equivocado **se inyecta en el
contexto de todos los agentes, en todas las sesiones**. Segunda: es una reincidencia. El registro ya
lo cazó y lo dejó a conciencia —`registro/commits/universo/2026/09/fix-h20-niveles.md:226`:
*«`galaxia/galaxia.md` dice «Veinte oficios» y hay 21 sistemas solares… Cambiarlo obliga a regenerar
el indice y no es de este encargo»*—. Se señaló, no se arregló, y volvió a desincronizarse.

`cosmos validar` sale **verde con 0 errores**: ninguna invariante de E00–E20 compara un número
escrito en prosa con la realidad del árbol.

**Fix**: no corregir el «Veintiun» a mano —volverá a pasar en el siguiente split—. Que el generador
del índice escriba el cardinal, o una invariante nueva (E21) que exija que todo numeral en la línea
`resumen:` de un índice cuadre con lo contado. Es el mismo criterio que ya usa
`tests/test_ejecucion_directa.py`: afirmar sobre la forma, medida, no sobre la intención.

---

### F-08 · MEDIO — Se cataloga un guion que lanza un agente con `--dangerously-skip-permissions`, y la ficha no lo advierte

`galaxia/pueblos/openclaw/scripts/telegram-bridge.py:128-144` (y su gemelo
`cosecha/telegram-bridge.py`) convierte un mensaje de Telegram en:

```python
subprocess.run('claude -p "%_<agencia>_PROMPT%" --output-format text --dangerously-skip-permissions',
               shell=True, cwd=WORKSPACE, env=env, …)
```

Dos cosas, y la segunda es la rara:

**a) El aviso que falta.** La ficha de `openclaw` es cuidadosa: advierte del `curl | bash`, advierte
de que la licencia no tiene SPDX, y advierte de que *«el freno de acciones irreversibles no puede
vivir solo en el prompt»*. No dice ni una palabra de que el guion que ella misma distribuye desactiva
el sistema de permisos. Sí hay allowlist por `ALLOWED_USER_ID` y las credenciales van por entorno
(nada hardcodeado), así que no es explotable por un extraño; pero un catálogo pensado para
compartirse no puede publicar eso sin un párrafo al lado.

**b) `%_<agencia>_PROMPT%` es sintaxis de CMD de Windows.** En el POSIX `sh` que usa `shell=True` en
macOS y Linux **no expande nada**:

```bash
$ _<agencia>_PROMPT="ordendelusuario" sh -c 'echo claude -p "%_<agencia>_PROMPT%"'
claude -p %_<agencia>_PROMPT%
```

El mensaje del usuario nunca llega a `claude`: se le pasa el literal. (El mensaje de error del
propio guion, `set TELEGRAM_BOT_TOKEN=…`, es también sintaxis de CMD, así que el fichero entero
viene de Windows.) Efecto secundario feliz: como no expande, tampoco inyecta. Efecto principal: el
guion **no funciona en la plataforma del repo** y se cataloga como si funcionara.

**Fix**: pasar el prompt como argumento de una lista (`subprocess.run([...])`, sin `shell=True`),
quitar `--dangerously-skip-permissions` o exigirlo por una variable explícita del operador, y añadir
a la ficha el mismo tipo de aviso que ya lleva para el `curl | bash`. Y ejercitar el guion en macOS
antes de que la ficha diga que existe.

---

### F-09 · BAJO — `--no-verify` salta el gate entero (compensado por CI)

Medido sobre el clon con el hook instalado por `cosmos enganchar`:

```
git commit -m "…"                → BLOQUEADO: "ruta#c54b8598fd3e:1: posible token GitHub"
git commit --no-verify -m "…"    → commit creado, secreto dentro
```

Es la limitación estructural de todo pre-commit y el README no promete otra cosa. **Está bien
compensado**: `.github/workflows/cosmos.yml` corre `python3 -m puente.secretos --todo` en `push` y en
`pull_request`, así que un salto local se caza en el servidor. La pega es de orden: en `push` el
secreto ya viajó. **Fix opcional**: mover el escaneo a un `pre-push` además del `pre-commit`.

**Además, y esto no lo cubre el README**: en `~/cosmos` **el hook no está instalado**.
`ls -a .git/hooks` solo tiene los `.sample` y `core.hooksPath` está sin definir. El repo que vende el
gate no lo corre sobre sí mismo; su única red hoy es CI.

---

### F-10 · BAJO — Dos fichas publican `curl | bash` sin el aviso que sí lleva una tercera

| Ficha | usos de `curl \| bash` | aviso |
|---|---|---|
| `openclaw` | 2 | sí — *«ejecuta código remoto sin revisar: para producción, leer el guion antes»* |
| `foundry` | 1 | **no** |
| `rill` | 1 | **no** |

El repo cataloga *pipe-to-shell* como patrón de ataque en su propio material
(`galaxia/pueblos/auditor-de-skills/references/threat-model.md:55`). El aviso de `openclaw` es el
modelo; copiarlo a las otras dos cuesta una línea. `rill` además ya ofrece la alternativa
(`brew install`) sin decir que es la preferible.

---

### F-11 · BAJO — 64 rutas absolutas del Mac de Darío en el árbol; el escáner no tiene patrón para ellas

```bash
$ git grep -c -I '~' | wc -l ; git grep -n -I '~' | wc -l
      10                                            64
```

Concentradas en `progress/revision-profunda-2026-09-02/INFORME.md` (30),
`progress/revision-adversarial-cosmos-2026-09-02/INFORME.md` (22), sus `pruebas/` (9) y
`registro/commits/universo/2026/09/fix-guardarrailes.md` (1). En la historia, 21 blobs.

En su mayoría son legítimas: comandos de reproducción, que **deben** ser copiables (regla 2 y 7 del
revisor adversarial). Pero revelan nombre de usuario y disposición del disco, y hay un commit del
2026-09-01 (`b92006e`, *«fix(seguridad): rutas de la maquina fuera de los ficheros versionados»*) que
prueba que esto se consideró un problema y luego se dejó de vigilar — porque **el escáner no tiene
ningún patrón para `/Users/<algo>/`**, así que nada avisa cuando vuelve a entrar.

**Fix**: patrón `rb'/(?:Users|home)/(?!runner\b)[A-Za-z0-9._-]+/'` en `PATRONES`, más una convención
publicada (`$REPO`, `~/cosmos`) para los comandos de los informes, que siguen siendo copiables sin
nombrar al usuario.

---

### F-12 · BAJO — La reescritura de historia no está registrada, y sus respaldos siguen vivos

`refs/original/refs/heads/trabajo-2026-09-02` existe (respaldo de `filter-branch`), y hay cuatro
ramas de respaldo locales más tres remotas. **En todo `registro/` no hay una sola entrada sobre la
reescritura**, en un repo que documenta hasta el cierre de un fallo menor con 200 líneas.

La operación que decide *qué queda publicado* es la única sin acta. Y como se ve en F-02 y F-05, no
purgó nada sensible: los 162 objetos que `historia-limpia` deja fuera son versiones de ficheros de
contenido ordinario.

**Fix**: acta en `registro/decisiones/universo/` con qué se reescribió, por qué y qué NO se purgó; y
borrar `refs/original/*` y las ramas de respaldo cuando la purga de F-02/F-05 se haya hecho de verdad.

---

## AFIRMACIONES DEL REGISTRO QUE NO SE SOSTIENEN

Cinco. Menos de las que la premisa del encargo anticipaba, y ninguna es una medición inventada.

### 1. `secretos-conocidos.txt` — «Solo entran valores que NO son credenciales… Nunca una credencial real»

**No se sostiene como garantía**, porque la clave de comparación no mira el valor (F-01).

**Matiz obligado, y va a favor del repo**: los **tres** valores inventariados hoy **sí** son
legítimos. Lo verifiqué decodificando las etiquetas opacas, que es lo que la lista no permite hacer
a simple vista:

```bash
python3 -c "
import subprocess,sys; sys.path.insert(0,'.')
from puente.etiquetas import etiqueta_de_ruta
for p in subprocess.run(['git','ls-files','-z'],capture_output=True).stdout.split(b'\0'):
    if p and etiqueta_de_ruta(p) in {'ruta#25dacd7d542a','ruta#db0d46f684d1'}: print(etiqueta_de_ruta(p),p.decode())"
# ruta#db0d46f684d1 -> progress/revision-profunda-2026-09-02/INFORME.md
# ruta#25dacd7d542a -> tests/test_guardarrailes.py
```

Ambos contienen las claves de ejemplo que **AWS publica en su propia documentación** (`AKIA…` que
acaba en `EXAMPLE`, y el secreto `wJal…` que acaba en `EXAMPLEKEY`), exactamente como declara el
encabezado. La lista es honesta; **el mecanismo que la aplica es el que no puede sostener la promesa.**

Efecto lateral de las etiquetas opacas: son la decisión correcta para un diagnóstico, pero convierten
la lista de excepciones en algo que **nadie puede auditar sin escribir código**. Merece un comentario
por entrada con el nombre del fichero en claro.

### 2. Commit `b05e7a0` — «86 herramientas genericas, **verificadas sin datos de cliente**»

Ese mismo commit introdujo el CIF auténtico de F-02.

```bash
$ git show b05e7a0 | grep -E '^\+.*B039'
+// Normaliza un NIF/CIF: mayúsculas + solo alfanumérico. "b-039.72221 " → "B039…".
```

Peor: el commit siguiente que lo toca es `4c06e72`, *«fix(secretos): ensenar al escaner en vez de
callarlo»* — el commit cuyo propósito era cazar justo esta clase de dato — y **lo propaga a un segundo
fichero**. Solo cae dos commits después, en `3a655b5`. La verificación que el mensaje declara no ocurrió.

### 3. `PROGRESS.md:95` — «Contrafactual verificable **sobre el mismo árbol actual**… `4.070` tokens, `127` pueblos, `3.206` de catálogo»

Ejecutado hoy sobre el árbol actual, con los 22 nichos:

```bash
python3 -m cosmos medir --combinacion agentes-ia,analitica,audiovisual,automatizacion,blockchain,\
ciberseguridad,cientifico,cumplimiento,documentos,embebidos,extraccion,infraestructura,\
ingenieria-datos,juegos,modelos-locales,moviles,refactorizacion,rendimiento,saas,trading,visibilidad,web
```

| | Afirmado | Medido hoy |
|---|---|---|
| Combinación total | 4.070 tok | **10.713 tok** |
| Pueblos | 127 | **247** |
| Catálogo | 3.206 tok | **9.645 tok** |

**Atenuante grande, y hay que decirlo**: `PROGRESS.md` lleva `Actualizado: 2026-09-01` en su línea 3
y su último commit es de ese día. No es una cifra inventada: es una cifra **fechada** que envejeció,
exactamente el patrón H11 que el repo ya conoce. Lo que no se sostiene es la palabra **«actual»** en
un documento sin pin de commit — y el propio arnés tiene la regla escrita: *«Un informe sobre un árbol
que muta caduca en minutos… fija el estado en cabecera»*.

**Fix**: `PROGRESS.md` fija su `HEAD` en cabecera y cambia «árbol actual» por «árbol de `<sha>`».

### 4. `galaxia/COSMOS.md` y `galaxia/galaxia.md` — «Veintiun oficios»

Son 22. Detalle en F-07. Es la afirmación falsa que **más veces se lee**, porque viaja en la entrada
base de todas las sesiones.

### 5. `galaxia/pueblos/auditor-de-skills/SKILL.md` — «Rescatado de la skill … de un arnés **propio**»

El guion es de `github.com/alirezarezvani/claude-skills`, documentado en el propio arnés. «De un
arnés propio» describe dónde estaba instalado, no de quién es. Detalle en F-03.

### Afirmaciones que sí se sostienen y que verifiqué por si acaso

Las publico porque la premisa era que el registro se adorna, y en estos cuatro casos **no se adorna**:

- **B04 («`escribir_atomico` cambia los permisos de 644 a 600»), declarado cerrado**: cierto. En un
  clon limpio con `umask 022`, `python3 -m cosmos arrancar` genera `.cosmos/compilado-galaxia.json`
  con `-rw-r--r--`. El `600` que hay en `~/cosmos` es un residuo del 2026-09-02, anterior al fix.
  `cierre-menores.md:110` además admite por su cuenta que *«el arreglo de permisos de B04 solo llegó
  a una de las copias»* — se autodenuncia antes de que llegue nadie.
- **«21 oficios» en `progress/revision-profunda-2026-09-02/INFORME.md:820`**: era **correcto** cuando
  se escribió. El informe se commiteó a las 13:05 y el split a 22 oficios entró a las 14:22 del mismo
  día. No es una cifra falsa; es F-07 vista desde antes.
- **Los cinco commits que los informes usan como pin** (`fbde93b`, `a4f880e`, `6a32781`, `04c3edc`,
  `7fbcb94`) **sobreviven a la reescritura de historia**: `git cat-file -t` devuelve `commit` para los
  cinco. Las reproducciones publicadas siguen siendo anclables.
- **Las pruebas publicadas como evidencia reproducen**: `probe_vocab`, `probe_escala`, `probe_estrella`
  y `probe_e17` corren hoy con exit 0 y salida coherente. `probe_sobreajuste` falla, pero por un
  prerequisito que su propio `LEEME.md` documenta y explica cómo reconstruir (`/tmp/advcosmos/mix`).
  **No es una afirmación falsa**; es una mejora (ver M-4).

---

## Lo que está limpio (medido, no supuesto)

1. **Cero credenciales reales en el árbol y en la historia.** Barridos los 3.206 objetos alcanzables
   desde las 9 refs + colgantes con los patrones del propio repo. Los únicos aciertos de clase
   «secreto» son: las dos claves de ejemplo de AWS (declaradas), los valores sintéticos de
   `puente/tests/test_secretos.py` (clave RSA de juguete, `postgres://usuario:Zx91…`, `api_key = "aB3x…"`,
   IBAN `ES91 2100 0418 45…` = el IBAN de ejemplo canónico), y una `AKIA0123…` (secuencia trivial
   `0123456789…`, no una clave) en un blob colgante. **Ninguna es una credencial**.
2. **Cero teléfonos reales.** Los 40 aciertos del patrón vienen todos del CSS y los `viewBox` de SVG
   del volcado HTML de F-05. Filtrados por fichero, quedan cero.
3. **Cero correos reales.** 15 direcciones distintas en el árbol, **todas** en dominios reservados por
   la RFC 2606/6761 (`ejemplo.test`, `example.invalid`, `dominio.com`). El único correo de persona real
   está en el blob borrado de F-05 y es de un tercero ajeno a la agencia.
4. **Cero credenciales o infraestructura de la agencia.** Ni IPs de producción, ni el <agencia> prod, ni
   nombres de cliente, ni tokens de BWS/IONOS/GitHub. Los 74 guiones de `cosecha/` leen **todo** por
   variable de entorno (`BWS_ACCESS_TOKEN`, `TELEGRAM_BOT_TOKEN`, `MAIL_SMTP_HOST`); lo único con
   sabor a agencia es `smtp.ionos.es` como valor por defecto, que es un nombre de host público.
5. **Atribución del catálogo, casi perfecta.** De 247 pueblos, 209 citan un repo de GitHub: **208
   traen URL + licencia + estrellas + fecha de comprobación**. Los 3 que mi regex marcó como
   incompletos (`n8n`, `raylib`, `ffmpeg-normalize`) son falsos positivos míos — llevan «Sustainable
   Use License», «Zlib» y «MIT leído en su `LICENSE.md`», que mi expresión no reconoció. **El único
   fallo real de atribución es `auditor-de-skills`** (F-03). Varias fichas van más allá de lo exigible
   y distinguen la licencia **leída en el fichero** de la que reporta la API como `NOASSERTION`
   (`metasploit`, `sqlmap`, `impacket`, `pwntools`, `amass`, `ffmpeg-normalize`). Eso es hacerlo bien.
6. **La atribución a aider está en el sitio correcto.** No solo en el registro
   (`registro/commits/universo/2026/09/camino-al-diez.md:16`, que lo llama «robado» sin adornos) sino
   **en el código que la usa**, `cosmos/medir.py:236`, con la URL de la fuente. Es idea, no código: la
   implementación es propia y el registro dice explícitamente qué parte NO se tomó («sin su grafo de
   referencias»). Sin objeción.
7. **Herramientas ofensivas: nada que sobre.** 27 pueblos bajo `ciberseguridad`, 9 bajo
   `ciberseguridad/ofensiva` (`metasploit`, `sqlmap`, `impacket`, `bloodhound`, `amass`, `nuclei`,
   `zaproxy`, `pwntools`, `aflplusplus`). **Todas son herramientas estándar de pentesting con
   distribución pública y licencia libre; ninguna cuyo único uso sea el daño.** 8 de las 9 llevan
   contexto de uso autorizado explícito; `metasploit` es ejemplar (*«solo se usa en auditoría
   contratada, laboratorio y competición, nunca fuera del alcance escrito»*, más el aviso de que un
   `RHOSTS` mal puesto lanza contra una red que no es la del encargo). **Y todos los ejemplos usan
   rangos de documentación de la RFC 5737** (`198.51.100.0/24`, `203.0.113.10`): nadie copió una IP
   de un cliente en un `set RHOSTS`. Única mejora: `aflplusplus` no menciona alcance (ver M-5).
8. **CI correcto.** `.github/workflows/cosmos.yml`: `permissions: contents: read`, **sin
   `pull_request_target`**, sin `secrets`, sin `pip`, sin red, sin acciones de terceros más allá de
   `actions/checkout@v4` pineado por major. Corre el escáner de secretos, las dos suites, el gate y el
   manejador de sesión. No tiene ninguno de los agujeros clásicos de Actions.
9. **Superficie de ejecución mínima.** Un solo `shell=True` en todo el repo (F-08) y su copia; **cero**
   `eval()`, `exec()` u `os.system()` en código ejecutable — los aciertos de grep son el material
   didáctico de `threat-model.md` y las reglas de `semgrep`. Tres `curl | bash`, todos en documentación
   de instalación de la herramienta ajena (F-10). Ningún guion descarga y ejecuta por su cuenta.
10. **El escáner funciona de verdad contra lo que no está indultado.** Con un token de juguete en un
    fichero nuevo bloquea el commit, dice el patrón y **no publica el valor ni la ruta**. El diseño de
    redacción por *forma del dato* en vez de por *nombre del campo* (`redactar_texto`) es más robusto
    que la blocklist de nombres que usa casi todo el mundo, y el razonamiento está escrito al lado.
11. **Las suites pasan hoy**, con el intérprete nombrado:
    `python3 -m unittest discover -s tests -t .` → **`Ran 259 — OK (skipped=2)`** en 81 s;
    `-s puente/tests` → **`Ran 116 — OK`** en 4,7 s. `cosmos validar` → **verde, 0 errores**.
12. **Dos ejemplos de honestidad activa que merecen decirse.** `cosmos medir` avisa por su cuenta:
    *«SIN TOKENIZADOR: el margen publicado (±5,2 %) NO se ha verificado en esta ejecución»* — publica
    que **no** midió en vez de dar el número por bueno, que es exactamente la bandera trivalente que
    pide la regla 14 del revisor adversarial. Y `cosmos validar` nunca dice «verde» a secas habiendo un
    salto vivo: dice `rojo (1 salto activo: E16, caduca en 1 d)`. Es lo que impide que F-06 sea un
    fallo alto.

---

## Mejoras (no son hallazgos)

- **M-1 · Un modo `--historia` en el escáner.** Hoy solo ve el índice; F-02 y F-05 viven donde no
  mira. Barrer los 3.206 objetos con sus propios patrones cuesta ~90 s: cabe en CI perfectamente.
- **M-2 · Un patrón de ruta de máquina.** Cierra F-11 y evita que se repita `b92006e`.
- **M-3 · Comentar `secretos-conocidos.txt` con el fichero en claro.** Las etiquetas opacas son la
  decisión correcta para un diagnóstico y la equivocada para una lista que un humano tiene que
  revisar. Un `# tests/test_guardarrailes.py` por entrada no filtra nada y la vuelve auditable.
- **M-4 · Anclar la evidencia fuera de `/tmp`.** `probe_sobreajuste.py` depende de
  `/tmp/advcosmos/mix`, que no sobrevive a un reinicio; su `LEEME.md` explica cómo reconstruirlo, pero
  la evidencia debería reconstruirse sola (que el propio guion haga el `git archive` si falta el
  directorio). Cuesta cinco líneas y la prueba pasa de «reproducible con instrucciones» a
  «reproducible».
- **M-5 · Alcance en `aflplusplus`.** Es la única de las 9 fichas ofensivas sin una línea de uso
  autorizado. Un fuzzer es menos peligroso que un framework de explotación, pero la coherencia del
  continente vale más que la excepción.
- **M-6 · Un `NOTICE`.** Sitio único donde acumular las atribuciones de F-03 y la de aider, en vez de
  repartirlas entre un comentario de código y una ficha.

---

## Veredicto

**El repo filtra, sí: un identificador fiscal auténtico de una empresa real, vivo en la historia
publicada de cinco ramas — incluida la que se llama `historia-limpia`.** No es una credencial y el
repo es privado, así que hay tiempo; pero no se arregla con un commit, y el registro no tiene acta de
la reescritura que debería haberlo limpiado.

**Y el registro se adorna, pero poco y de una forma concreta**: no inventa mediciones, no falsifica
verdes y se autodenuncia con una frecuencia que no es normal (`cierre-menores.md` confesando que el
fix de B04 solo llegó a una copia; `medir` publicando que no verificó su propio margen). Lo que hace
es **envejecer sin fecharse** —el «árbol actual» de `PROGRESS.md`, el «Veintiun oficios» que ya son
22— y **usar una fórmula ambigua donde hacía falta una precisa**: «de un arnés propio» para código
que es de otro.

El hallazgo que me preocupa más no es ninguno de esos dos. Es **F-01**: la lista de excepciones nació
de una buena decisión —*«enseñar al escáner en vez de callarlo»*— y la implementa indultando ficheros
enteros en vez de valores concretos. Dos credenciales nuevas y distintas atravesaron el gate en
silencio, con exit 0 y el mensaje «limpio de nuevos». Es el fallo más peligroso de un sistema de
seguridad: **el que hace que el verde deje de significar algo.**

---

*Revisor F · 2026-09-03 · sobre `b0c1ebd` · solo lectura, experimentos en clon aparte.*
