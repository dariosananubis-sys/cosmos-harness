---
cosmos: lluvia
nombre: migracion-puente
moja: []
resumen: Cuatro piezas del arnés de origen adaptadas a COSMOS en puente/, con 35 tests y 8 mutaciones en rojo.
---

# El puente — cuatro piezas migradas y adaptadas

**Fecha:** 2026-09-01 · **Escribe:** `puente/` y este parte · **Origen:** `vh-ref` (solo lectura,
verificado intacto: `git status --porcelain` = 0 líneas al terminar).

Decisión que lo ordena: [[cosmos-sobre-vanguardia-harness]] — se construye encima, no se reescribe.
Esto es el «encima»: las cuatro piezas que ese repo tenía escritas y COSMOS no, traídas al
vocabulario de nichos, pueblos y registro, y con las mejoras que se vieron al leerlas enteras.

**1.232 líneas de origen → 1.456 de puente + 734 de pruebas.** Solo biblioteca estándar, cero red,
cero dependencias nuevas.

| Pieza | Origen | Destino | Líneas |
|---|---|---|---|
| Proyección a repo ajeno | `scripts/project.py` (511) | `puente/proyectar.py` | 552 |
| Escáner de secretos | `scripts/secret_scan.py` (361) | `puente/secretos.py` | 424 |
| Etiquetas opacas | `scripts/redaction.py` (13) | `puente/etiquetas.py` | 41 |
| Gate sobre el índice | `scripts/precommit.py` (131) | `puente/gate.py` | 148 |
| Memoria con presupuesto | `scripts/retrieve_memory.py` (216) | `puente/lluvia.py` | 281 |

---

## 1. `proyectar.py` — proyecta COSMOS sobre un repo Git ajeno

Lo que hace, y era su valor: escribe el contexto y las skills en un repositorio que no es suyo
**sin borrar nada de nadie**. Fusiona `settings.json` clave a clave, sustituye solo lo que hay entre
marcadores en `CLAUDE.md`/`AGENTS.md`, y se niega a tocar una skill que no lleve su marca.

### Traducido al vocabulario de COSMOS

| Antes | Ahora | Por qué |
|---|---|---|
| `project.toml` | `planeta.toml` | Un repo de destino **es** un planeta: «un proyecto concreto» |
| `packs = [...]` | `nichos = [...]` | Los packs eran dos niveles planos; aquí manda la taxonomía |
| `skills/*/SKILL.md` + `packs/*/skills` | ciudades y pueblos del árbol | Una sola fuente: el frontmatter |
| `[context] / [boundaries] / [verification]` | `[contexto] / [limites] / [verificacion]` | Un solo idioma en todo el fichero |
| `kind`, `write_paths`, `production` | `tipo`, `rutas_escritura`, `produccion` | Igual |
| `<!-- vanguardia-harness:start -->` | `<!-- cosmos:inicio -->` | Igual |
| `.generated-by-vanguardia` | `.generado-por-cosmos` | Marca de propiedad de lo generado |

### Lo que se quitó por no aplicar

- **`available_packs()` y toda la lectura de `packs/`.** No existe ese nivel: los nichos salen de
  `nombres_nichos(arbol)`, que ya los deduce del árbol.
- **El «núcleo» de skills siempre proyectadas** (`ROOT/skills/*`). En COSMOS no hay skills fuera de
  un nicho — una skill huérfana es un error del sistema, no un caso aceptable. Contrato sin nichos =
  se proyecta el contexto y **cero** skills, que es lo coherente.
- **`harness/policy/core.md`.** Ruta fija a un fichero de política. Ver la mejora 1.
- **`max_root_bytes` y `max_active_skill_description_bytes` de `harness.toml`.** Dos presupuestos en
  bytes que no son los de COSMOS. Ver la mejora 2.

### Lo que se mejoró

1. **El bloque proyectado ya no es un fichero fijo: es `contexto_inicial(árbol, nichos)`.**
   El original pegaba `harness/policy/core.md`, una ruta cableada que nadie garantizaba que fuera lo
   que de verdad se paga al entrar. Ahora se proyecta **exactamente la secuencia normativa de
   NUCLEO §2** —índice, océanos, catálogo del nicho— la misma cadena que tokeniza el medidor. Lo que
   se mide y lo que se proyecta dejan de poder discrepar.

2. **El presupuesto se comprueba en tokens contra `cosmos.toml`, no en bytes contra otro fichero.**
   `presupuesto.entrada` es el único techo. Medido en vivo sobre la galaxia real con `--nicho web`:
   **1.613 tokens de 4.000** (7.754 bytes). Si un contrato se pasa, la proyección falla nombrando el
   exceso en vez de escribir un `CLAUDE.md` que revienta el presupuesto del planeta.

3. **E18 (colisión al aplanar) se aplica también a un repo ajeno, y nombra las dos rutas.**
   El original solo decía `skill inválida o duplicada: <nombre>`. Saber que «revisar está duplicado»
   no arregla nada; saber qué dos rutas chocan se arregla en diez segundos. Es la regla que
   `COMPILACION.md` exige para el árbol, aplicada donde el daño de verdad ocurre.

4. **`comprobar` ya no revienta por presupuesto, informa.** En el original, pasarse de bytes lanzaba
   una excepción **también en modo comprobación**, así que un repo grande no podía ni listar sus
   problemas. Ahora el exceso es un problema más de la lista y se ven todos de una pasada.

5. **La raíz de COSMOS ya no se deduce de dónde está el fichero.** `_git_root` comparaba contra un
   `ROOT` calculado desde `__file__`; ahora entra por `cosmos.toml`, así que un `--config` distinto
   (p. ej. `galaxia.toml`) proyecta el árbol que toca.

---

## 2. `secretos.py` + `etiquetas.py` — escáner sobre blobs del índice

Su valor, y no es un detalle: escanea **los blobs que Git tiene en el índice**, no los ficheros del
disco. Y no imprime ni el valor encontrado ni la ruta: la ruta viaja como etiqueta opaca, así que un
informe de secretos no filtra lo que está diagnosticando.

### Traducido y podado

- `FORBIDDEN_ROOT_DIRS = {.runtime, artifacts, workspaces, progress, src, notes}` → **`{.cosmos}`**.
  Esos seis eran directorios del arnés de origen; en COSMOS `src/` no existe y `registro/` se
  versiona a propósito. Lo único que COSMOS genera y no debe versionarse es `.cosmos/`.
- `FORBIDDEN_EXACT_PATHS`: fuera `harness.local.toml` y `projects/local.toml`, dentro
  `cosmos.local.toml`.
- `FORBIDDEN_PATH_PREFIXES`: `harness/generated/` fuera; quedan `.claude/skills/` y
  `.agents/skills/`, que es la **vista plana** que `cosmos compilar` genera y que nunca se commitea.
- «DNI/NIE/NIF asignado» → **«identificador fiscal asignado»**: la etiqueta describía tres
  documentos de un país concreto en un repo que quiere ser genérico. El patrón no cambia.

### Lo que se mejoró

1. **El ruido, que es lo que mata a estas herramientas.** El patrón «secreto asignado» solo exigía
   veinte caracteres de un alfabeto amplio a la derecha del `=`. Medido contra el original:

   ```
   b'api_key = configuracion.obtener_clave_del_entorno'  -> [('secreto asignado', ...)]
   b'password = get_password_from_vault()'               -> [('secreto asignado', ...)]
   b'secret_key = settings.SECRETO_DE_LA_APLICACION_WEB' -> [('secreto asignado', ...)]
   ```

   Tres falsos positivos en tres líneas de código perfectamente normal. Un gate que grita así se
   desactiva, y desactivado no encuentra secretos: el ruido no es un defecto estético, es el modo de
   fallo real de la pieza. El arreglo **no es otra expresión regular acumulada**, es un filtro sobre
   el valor capturado (`(?P<valor>…)`, grupo nuevo): si tiene forma de expresión del lenguaje
   —`ruta.con.puntos`, `serpiente_en_minusculas`, `GRITO_EN_MAYUSCULAS`— no es un secreto. Los seis
   casos de ruido del test pasan en verde y los seis secretos plantados siguen saltando.

2. **Dominios de ejemplo.** El original solo perdonaba `.invalid`. Añadidos `example.com/.org/.net`
   (RFC 2606), que es lo que usa la documentación de un repo público-limpio.

3. **La raíz se pregunta a Git, no se deduce del fichero.** `raiz_git()` + `--raiz`, de modo que el
   escáner sirve para cualquier repositorio, empezando por la instantánea que monta el gate.

4. **`etiquetas.py`: la etiqueta podía filtrar la ruta que oculta.** Es un fallo latente real, no
   teórico: el resumen es hexadecimal, así que por azar contiene tramos como `dead`, `cafe` o `deb`.
   Buscadas colisiones a la fuerza bruta, aparecen enseguida:

   ```
   ('clientes/deb-cafe/informe.md', 'a7091d3cddeb', ['deb'])
   ('src/ade/deb.py',               '8bedeb3b6733', ['deb'])
   ('bad/dad',                      '81dad15fef5c', ['dad'])
   ```

   La etiqueta de un directorio de cliente enseñando un trozo del nombre del cliente es exactamente
   lo que la pieza existe para impedir. Ahora se comprueba y se vuelve a resumir hasta que no ocurre
   (y, si ni así, se emite en pares separados, forma en la que ningún tramo de tres caracteres cabe).
   **Las tres rutas de arriba son casos del test**: sin el bucle, se pone rojo.

---

## 3. `gate.py` — verificar la instantánea, no el escritorio

El original ya tenía la idea buena y se conserva entera: exporta el índice con `git checkout-index`
a un temporal, hace `git init` allí, y verifica **eso**. La diferencia entre comprobar lo que se va
a commitear y lo que casualmente hay en disco.

### Traducido

- Órdenes: `validate_skills.py` + `compile_context.py` + `audit_harness.py` → **`cosmos validar`**
  (que ya cubre E00–E19) y las dos suites, `tests/` y `puente/tests/`.
- Variables de entorno purgadas: `VANGUARDIA_PACKS` → `COSMOS_NICHOS`, `COSMOS_CONFIG`.

### Lo que se mejoró

1. **El escaneo de secretos se hace también dentro de la instantánea.** El original montaba un
   repositorio Git en el temporal y luego no lo usaba para lo único que necesita un índice: escanear
   blobs. Ahora fuera corre `--indice` (rápido, falla pronto) y dentro `--todo` sobre los bytes
   exactos que se van a commitear. El `git init` deja de ser decorativo.
2. **La raíz se pregunta a Git**, con caída al directorio del paquete si no hay repositorio.
3. **`--sin-pruebas`** para el uso interactivo, sin tocar el camino por defecto.

---

## 4. `lluvia.py` — la memoria que nunca devuelve el cuerpo

Es la `lluvia` de `spec/REGISTRO.md` ya implementada: BM25 por campos con pesos, presupuesto de
bytes de salida, y **la respuesta dice dónde mirar, nunca qué pone**. Una memoria que se devuelve
entera es otra fuga de contexto con mejor nombre.

### Traducido al registro

| Antes (`memory/index.json`) | Ahora (`registro/`) |
|---|---|
| `title`, `aliases` | `nombre` (frontmatter o nombre de fichero) |
| `tags` | `nicho` (sale de `registro/<carpeta>/<nicho>/`) |
| `summary` | `resumen` |
| `kind`, `source` | `carpeta` (`commits`/`lluvia`/`informes`/`decisiones`) |

### Lo que se quitó por no aplicar

- **`related` / `backlinks` y el salto de grafo.** COSMOS no tiene esos campos y el validador
  rechaza cualquier campo que no esté en `CAMPOS_POR_NIVEL` (E00). Inventarlos habría metido un
  segundo vocabulario por la puerta de atrás. **Sustituido por el salto que COSMOS sí tiene**: desde
  las tres entradas más fuertes se expande a sus hermanas de **nicho**, con el mismo factor 0,12.
  Misma intención —una vecina relevante que no comparte palabras—, con la estructura que ya existe.
- **`status: superseded`** y su penalización ×0,25: tampoco es un campo del frontmatter.

### Lo que se mejoró

1. **Ya no hace falta un `index.json` construido por un paso de arranque.** El original moría con
   *«falta memory/index.json; ejecuta scripts/bootstrap.py»*. Aquí **las entradas son los ficheros**:
   una memoria escrita hace un segundo ya se encuentra, y una borrada deja de encontrarse. No hay
   artefacto que sincronizar, así que no hay artefacto que se desincronice.
2. **Indexa también lo que no lleva frontmatter.** Los partes de `registro/commits/` reales no lo
   llevan; el original los habría ignorado. Sin frontmatter, el nombre sale del fichero y el resumen
   del primer encabezado, recortado a los 120 caracteres del presupuesto.
3. **Fuga latente cerrada.** El original serializaba `entry | {"score": score}`: **el objeto entero
   del índice**. Si ese índice ganara algún día un campo `body`, la salida JSON pasaría a devolver el
   cuerpo completo sin que nadie hubiera decidido nada. Ahora se proyecta campo a campo
   (`CAMPOS_PUBLICOS`), así que un campo nuevo no sale por defecto: hay que añadirlo a mano. La
   mutación M6 hace exactamente eso y el test se pone rojo.

---

## 5. Pruebas — 35 en verde y 8 invariantes vistas fallar

`GOAL.md` §7: una pieza no está terminada hasta que se la ha visto fallar a propósito. Un verde que
nunca ha dado rojo no distingue una comprobación que funciona de una rota.

```
$ python3 -m unittest discover -s puente/tests -t .
...................................
----------------------------------------------------------------------
Ran 35 tests in 0.938s

OK
```

Reparto: `test_proyectar` 11 · `test_secretos` 6 · `test_lluvia` 10 · `test_gate` 4 ·
`test_etiquetas` 4.

Y el rojo, reproducible con `python3 -m puente.tests.mutaciones` (rompe una línea, ejecuta la prueba
dueña de esa línea, exige que falle y lo deja todo como estaba):

```
$ python3 -m puente.tests.mutaciones
M1 puente/etiquetas.py: ROJO (correcto) — sin el bucle anticolisión, la etiqueta deja ver un tramo de la ruta
M2 puente/secretos.py: ROJO (correcto) — sin el filtro de expresiones, el escáner grita por cada 'obtener_clave_del_entorno'
M3 puente/secretos.py: ROJO (correcto) — subiendo el umbral del patrón, un secreto plantado deja de detectarse
M4 puente/proyectar.py: ROJO (correcto) — sin la guarda, la proyección pisa una skill que no es suya
M5 puente/proyectar.py: ROJO (correcto) — si el bloque se concatena en vez de sustituirse, la segunda proyección crece
M6 puente/lluvia.py: ROJO (correcto) — un campo de más en la proyección y la consulta devuelve el cuerpo entero
M7 puente/lluvia.py: ROJO (correcto) — sin el corte por bytes, la salida se pasa del presupuesto
M8 puente/gate.py: ROJO (correcto) — verificando en el árbol de trabajo, el gate aprueba lo que no se va a commitear

8/8 invariantes vistas fallar
```

### Prueba en vivo, no solo en laboratorio

Proyección de la galaxia real (129 pueblos, 20 nichos) sobre un repo Git desechable que ya traía su
propio `CLAUDE.md` y una skill ajena:

```
$ python3 -m puente.proyectar --config galaxia.toml iniciar <repo> --tipo web --nicho web
proyección sincronizada · 13 skills · nichos=web
$ python3 -m puente.proyectar --config galaxia.toml comprobar <repo>
proyección correcta · nichos=web            (exit 0)
$ python3 -m puente.proyectar --config galaxia.toml sincronizar <repo>   # segunda vez
proyección sincronizada · 13 skills · nichos=web
$ python3 -m puente.proyectar --config galaxia.toml comprobar <repo>
proyección correcta · nichos=web            (exit 0)
```

El `CLAUDE.md` del equipo quedó **encima** del bloque, intacto; `skill-del-equipo/` sigue ahí junto a
las 13 proyectadas; `settings.json` conservó su clave `model` propia y corrigió `autoMemoryEnabled`.
Bloque: **1.613 tokens de 4.000**.

---

## 6. Grep de contaminación

```
=== A) negocio, personas, marcas y vocabulario de origen ===
__init__.py:1:"""Puente: piezas migradas desde VanguardIA-Harness y adaptadas a COSMOS.

=== B) credenciales y secretos en claro ===
secretos.py:57:    ("clave Anthropic", re.compile(rb"sk-ant-[A-Za-z0-9_-]{30,}")),
secretos.py:63:            rb"(?!example|change[_-]?me|vault:|\$\{)[A-Za-z0-9/+=]{32,}"
secretos.py:81:            rb"vault:|\$\{)(?P<valor>[A-Za-z0-9_./+\-=]{20,})"
tests/test_secretos.py:32:    b"password = get_password_from_vault()\n"      (falso positivo a proposito)
tests/mutaciones.py:52-53: (las dos versiones del patrón que muta M3)

=== B2) el escaner leyendo los 14 ficheros del puente uno a uno ===
barrido completo: sin hallazgos

=== C) correos y dominios ===
tests/comun.py:69:puente@example.invalid
tests/test_gate.py:18:puente@example.invalid
tests/test_secretos.py:36:alguien@example.com
tests/test_secretos.py:37:nadie@dominio.invalid
(los dos cebos de correo y de URI ya no aparecen enteros: se arman en ejecución)

=== D) rutas absolutas de esta maquina ===
(sin coincidencias)

=== E) el propio escaner sobre los 14 blobs de puente/ ===
secretos: limpio en puente/ (0 hallazgos)
```

Lectura de cada bloque:

- **A** — una sola coincidencia, y es **deliberada**: la línea de procedencia del paquete. Nombra un
  repositorio de herramientas, no una organización ni un cliente, y es el mismo nombre que ya usa
  abiertamente [[cosmos-sobre-vanguardia-harness]]. Se declara aquí para que sea una excepción
  decidida y no un descuido. Todo lo demás del vocabulario de origen —`packs`, `harness.toml`,
  `projects/`, `.runtime`, `workspaces`, `VANGUARDIA_PACKS`— ha desaparecido.
- **B** — solo los patrones del propio detector y un falso positivo puesto a propósito. Los seis
  cebos de secreto **ya no aparecen enteros en el fuente**: se arman en tiempo de ejecución (ver el
  incidente de abajo). Cero credenciales reales.
- **B2** — el escáner leyendo los catorce ficheros del puente uno a uno, contenido completo: nada.
- **C** — solo dominios reservados (RFC 2606 y `.invalid`) y un URI inventado dentro de un cebo.
- **D** — ninguna ruta de esta máquina; todo relativo o por parámetro.
- **E** — el escáner corriendo sobre sí mismo: limpio.

### Hallazgo de regalo, fuera de mi alcance

Al pasar `secretos --todo` sobre el repo entero salieron **12 hallazgos reales** que no son míos y no
he tocado (ninguno vive en `puente/`):

| Fichero | Qué |
|---|---|
| `cosecha/enviar-correo-smtp.py` | correo electrónico |
| `cosecha/legales-crear-paginas.py` | correo y teléfono |
| `cosecha/legales-texto.py` | identificador fiscal asignado |
| `cosecha/patch-claude-mem-hooks.sh` | teléfono |
| `research/HERRAMIENTAS-PROPIAS.md` | identificador fiscal asignado |
| `.cosmos/compilado.json`, `.cosmos/compilado-galaxia.json` | artefacto generado, versionado |
| `.claude/skills/probar-salida`, `…/revisar-formato` | symlinks de la vista plana, versionados |

Los cinco primeros incumplen `GOAL.md` §5 («cero nombres de cliente, correos, datos personales») y
los cuatro últimos son artefactos generados que no deberían estar en el índice. Se elevan aquí; no
los arreglo porque están fuera de mi frontera y hay tres trabajos más en curso.

### El incidente que solo aparece al commitear: el escáner se denunciaba a sí mismo

Mientras trabajaba, otro trabajo hizo un `git add` que metió `puente/` en el índice. Al volver a
pasar el escáner sobre el repo ya versionado aparecieron **6 hallazgos nuevos, todos en
`puente/tests/test_secretos.py`**: sus propios cebos —clave privada, clave AWS, secreto asignado,
URI con credencial, IBAN, correo— escritos como literales.

No es una curiosidad: es una avería en cadena. El gate escanea el índice, así que en cuanto el
corpus de pruebas se commitea, **el gate se queda en rojo para siempre**, y la salida natural de
quien se lo encuentra es añadir una excepción por ruta — que es abrir un agujero permanente en el
único sitio del repo donde nadie mira.

Arreglo: los seis cebos **se arman en ejecución** (`b"AKIA" + b"IOSFODNN7EXAMPLE"`), así que el
fichero fuente no contiene ningún secreto completo y el test sigue ejercitando la cadena entera. Sin
excepciones, sin allowlist, sin tocar el detector. Comprobado leyendo los catorce ficheros del
puente uno a uno con el propio escáner: **sin hallazgos**.

Lección reutilizable: **un detector cuyo corpus de pruebas vive en el mismo repo que vigila tiene
que armar sus cebos en ejecución.** Si no, o se apaga o se le abre una excepción, y las dos cosas
acaban igual.

---

## 7. Lo que decidí NO migrar

| No migrado | Por qué |
|---|---|
| `compile_context.py` (23 KB) | Es el `contexto_inicial` de COSMOS, y ya está escrito en `cosmos/medir.py`. Migrarlo sería el duplicado que la decisión quería evitar |
| `audit_harness.py` (20 KB) | Su auditor conoce **su** estructura de directorios. Sobre la taxonomía daría falsos positivos; lo que hace de valor ya lo cubren E00–E19 |
| `validate_skills.py` (13 KB) | Mismo caso: valida el esquema de sus packs, no el frontmatter de COSMOS |
| `pack.py`, `doctor.py`, `bootstrap.py` | Atados a `packs/` y a `memory/index.json`, que aquí no existen |
| Salt por sesión en las etiquetas | Haría la etiqueta irreversible por fuerza bruta, pero rompería la comparación entre dos informes del mismo árbol. Se prefiere reproducible; queda anotado por si algún día se comparte un informe fuera |

## 8. Estado y frontera

- Escrito **solo** en `puente/` (14 ficheros nuevos) y en este parte. `cosmos/`, `tests/`,
  `ejemplo/`, `galaxia/`, `cosecha/` y `spec/` sin tocar: al terminar, `git status` muestra en
  `cosmos/` exactamente las mismas cinco modificaciones que ya había al empezar, de otros trabajos.
- `puente/` entró al índice **por un `git add` ajeno** a mitad de trabajo (commit `273350b`, de otro
  trabajo en curso), no por mí. Comprobado que ese commit contiene mi código tal cual
  (`git diff HEAD -- puente` vacío). Bien está: con el puente versionado, `gate.py` ya puede
  ejecutarse sobre la instantánea del índice, que es donde tiene sentido.
- Commiteo **solo mis dos rutas** (`puente/` y este parte), no el trabajo de nadie más: como
  `puente/` ya estaba en `HEAD` por el `add` ajeno, dejar el arreglo del corpus solo en el disco
  habría dejado publicada una versión que pone el gate en rojo.
- **No hago `push`.** El repo tiene remoto (`origin`), pero `main` local arrastra commits de los
  otros tres trabajos en curso; publicarlos no me corresponde. Mi commit queda local y listo para
  el `push` que decida quien coordine.
- `python3 -m puente.<pieza> --help` funciona en las cuatro: `proyectar`, `secretos`, `gate`, `lluvia`.
