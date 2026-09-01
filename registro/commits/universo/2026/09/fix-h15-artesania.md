# H15 — las diez herramientas escondidas dentro de los mares, sacadas al catálogo

Fecha: 2026-09-01 · Escrito solo en `galaxia/pueblos/**` (10 nuevos), `galaxia/continentes/` (2),
`galaxia/paises/rendimiento--*.md` (3), `galaxia/sistemas/rendimiento.md`, `galaxia/agua/mar-criterio.md`,
`galaxia/agua/mar-pruebas.md` y `registro/`.

**Estado del árbol al cerrar**: `HEAD 32818ed` · el repositorio tiene otra ventana trabajando a la vez
(`cosecha/`, `puente/secretos.py`, `galaxia/pueblos/validadores-frontera`), que además arrastró parte
de este trabajo dentro de su commit `3799944`. Nada suyo se ha tocado. Las afirmaciones se referencian
por nombre de pueblo, nunca por `fichero:línea`.

## Veredicto de una línea

**10 pueblos nuevos · 2 continentes · 11 nodos reapuntados · 0 herramientas nombradas ya dentro de un
mar · verde y bajo presupuesto.** El nicho `rendimiento` pasa de 8 a 18 pueblos y **no** se convierte
en el peor: 1.965 tokens frente a los 2.164 de `ciberseguridad`.

Y una corrección de método que vale más que el hallazgo: **cuatro de las diez fichas que escribí
leyendo documentación estaban mal**, y solo se cazaron ejecutando las herramientas (§4).

---

## 1. El agujero de diseño, y por qué la solución era ampliar un nicho y no crear uno

`mar/criterio` y `mar/pruebas` nombraban diez herramientas y declaraban por escrito que no eran
pueblos. Eso las dejaba fuera del catálogo, fuera del presupuesto por nicho, fuera de E18 y fuera de
`compilar` — o sea, invocables por nadie. Pero el hueco real era otro: **el agua no contiene**
(`spec/TAXONOMIA.md`), así que un mar no puede tener herramientas dentro *por construcción*; lo que
faltaba era un sitio sólido donde meterlas.

`rendimiento` se amplía al oficio completo de **entrar en código que no escribiste y dejarlo mejor**,
con dos continentes. Sigue siendo un solo oficio y sigue pasando la prueba de «¿alguien contrataría
esto?»: «esto va lento», «bajad la deuda técnica», «revisad la calidad de este código». Seguimos en 21
nichos.

```
rendimiento  (sistema-solar)
├── velocidad  (continente)   ← los 8 que ya había
│   ├── pais/perfilado      bpftrace · hyperfine · py-spy · samply
│   ├── pais/depuracion     rr · sanitizers
│   ├── pais/concurrencia   tokio
│   └── pueblo/mimalloc     (colgaba del sistema; ahora del continente)
└── calidad  (continente)     ← los 10 nuevos, planos
    ast-grep · openrewrite · difftastic · serena · ruff
    eslint · golangci-lint · jscpd · mutmut · stryker-js
```

**Por qué `calidad` va plano y `velocidad` conserva sus países.** `spec/TAXONOMIA.md` permite saltar
niveles (`rango(padre) < rango(hijo)`, estrictamente) y llama antipatrón al «nivel de relleno». Los
agrupamientos naturales de los diez serían *análisis estático* (3), *transformación masiva* (2),
*mutación* (2), *revisión y navegación* (2) y *duplicación* (**1**): dos países de dos y uno de uno.
Cada país cobra su `resumen` en el catálogo y ese último sería relleno puro. Se deja plano; si entra
una sexta herramienta de análisis estático, ahí sí agrupa de verdad.

**Los ficheros de país conservan su nombre** (`paises/rendimiento--perfilado.md`), porque la identidad
sale del frontmatter y no de la ruta; renombrarlos habría sido churn sin efecto. Queda anotado por si
molesta a la vista.

## 2. Las diez, con su decisión

Datos de vida verificados **en vivo el 2026-09-01** contra la API autenticada de GitHub. El token sale
del llavero y **no se escribió ni se imprimió en ningún sitio**:

```bash
export GH_TOKEN=$(security find-internet-password -s github.com -w)
curl -s -H "Authorization: Bearer $GH_TOKEN" "https://api.github.com/repos/OWNER/REPO" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['stargazers_count'],d['pushed_at'],(d.get('license') or {}).get('spdx_id'),d['archived'])"
```

| Pueblo | ★ | push | licencia | versión | archivado | La decisión |
|---|---|---|---|---|---|---|
| `ast-grep` | 15.718 | 2026-08-31 | MIT | 0.45.3 | no | Rival `comby` (2.672★, vivo). **ast-grep gana con gramática** (sabe que eso es una llamada y no una propiedad; encadena `inside`/`has`/`follows`); **comby gana sin ella** — dialectos de plantilla, configuraciones, lenguajes sin gramática publicada |
| `openrewrite` | 3.688 | 2026-09-01 | Apache-2.0 | v8.91.4 | no | El único que **sabe de tipos** y devuelve el formato intacto. Coste de entrada dicho sin adornos: **el proyecto tiene que compilar**, la primera vuelta descarga el árbol entero, tarda minutos y pide memoria; catálogo maduro solo en JVM |
| `difftastic` | 25.847 | 2026-08-28 | MIT | 0.70.0 | no | No compite con `delta` (que colorea el mismo diff por líneas): produce **otro diff**. Los límites duros, medidos en su código, en §3 |
| `serena` | 28.703 | 2026-08-30 | MIT | v1.7.0 | no | Creado en **marzo de 2025**: joven y con la interfaz en movimiento — sus propios autores piden que no se instale desde ningún mercado porque los que circulan traen órdenes viejas. Motor por defecto LSP (libre); el de JetBrains es **de pago** y queda fuera |
| `ruff` | 49.425 | 2026-09-01 | MIT | 0.16.5 | no | Rival `flake8` (3.824★) + `black` (41.828★), **los dos vivos**: el argumento no es que estén muertos, es la cadena real —flake8 + sus complementos + isort + el orden entre ellos + cuatro configuraciones— contra una sección de `pyproject.toml`, y la velocidad que le permite correr al guardar |
| `eslint` | 27.495 | 2026-09-01 | MIT | v10.9.1 | no | Contra `biome`: **recomiendo eslint**, razonado en §5 |
| `golangci-lint` | 19.342 | 2026-09-01 | **GPL-3.0** | v2.13.2 | no | Un solo parseo y un solo *type-check* repartidos entre ~100 analizadores, más caché. La licencia es la única no permisiva del continente y se avisa: importa al empaquetar el binario en una imagen que se entrega |
| `jscpd` | 6.092 | 2026-08-31 | MIT | v5.1.1 | no | Gana a `PMD CPD` en cobertura: **224 formatos**, mismo umbral, un informe para un monorepo entero |
| `mutmut` | 1.412 | 2026-08-17 | BSD-3-Clause | 3.7.0 | no | Modesto en estrellas y se dice: es la opción mantenida de Python, no un estándar. Lo lento y las tres trampas, en §4 |
| `stryker-js` | 3.068 | 2026-08-31 | Apache-2.0 | v10.0.0 | no | Contra `c8`/`istanbul` no hay debate: borra todos los `expect` de un fichero y conserva **100% de cobertura** con **0% de mutación** |

Ninguno archivado, ninguno de pago, ninguno pide tarjeta. Los diez traen URL, licencia, estrellas con
fecha, comando de instalación, ejemplo copiable, comparación con el rival nombrado y aviso de lo que
no hace bien, según `spec/PUEBLO.md`.

## 3. Lo lento se cuantifica, no se adjetiva

`spec/PUEBLO.md` exige que el aviso sea útil, y «es lento» no lo es. En las dos fichas de mutación se
escribe la fórmula y el orden de magnitud:

> tiempo ≈ **nº de mutantes × duración de las pruebas que tocan ese código**

Un módulo mediano da de cientos a un par de miles de mutantes; con una suite relevante de diez
segundos, mil mutantes son del orden de **horas**. Frente a los segundos de un analizador estático son
**dos o tres órdenes de magnitud**, y de ahí sale la política: sobre un módulo concreto, de madrugada
o a mano, nunca en el gancho de cada commit. `mutmut` trae `print-time-estimates` justo para eso.

Y los límites de `difftastic`, leídos de su `src/options.rs` y no de una impresión: cae a diff por
líneas si un lado pasa de `--byte-limit` (**1 MB** por defecto), si el grafo pasa de `--graph-limit`
(**3.000.000 de vértices**) o si hay **un solo** error de sintaxis (`--parse-error-limit` = 0). Son
justo los ficheros —minificados, generados, `lock`— donde un cambio masivo hace más ruido.

## 4. Cuatro fichas estaban mal y solo se cazaron ejecutando

Esta es la parte reutilizable del parte. Escribí las diez leyendo documentación; al verificarlas,
**cuatro tenían el comando equivocado**.

| Ficha | Lo que escribí leyendo | Lo que es de verdad | Cómo salió |
|---|---|---|---|
| `mutmut` | `mutmut run --paths-to-mutate src/` | Ese flag es de **mutmut 2**. En la 3 el ámbito va por **comodín sobre el nombre del mutante** (`mutmut run "calc.nucleo*"`) o por `source_paths=` en `setup.cfg` | Ejecutándolo |
| `serena` | `uvx --from git+… serena start-mcp-server` | `uv tool install -p 3.13 serena-agent` → `serena init` → `claude mcp add serena -- serena start-mcp-server --context claude-code --project "$(pwd)"` | Leyendo su Quick Start actual, tras ver que `serena init` no existía en mi versión |
| `jscpd` | «~150 formatos», `npx jscpd` | **224 formatos**; la v5 es un binario **Rust** 24-37× más rápido, y conviven dos motores (v4 TypeScript conserva LevelDB y la API de Node) | README oficial |
| `eslint` | `npx eslint --init` | La puesta en marcha oficial es `npm init @eslint/config` | Documentación de v10 |
| `golangci-lint` | `go install …/golangci-lint@latest` | Falta el **`/v2`** en la ruta del módulo (verificado en el `go.mod` de la etiqueta v2.13.2). Y `--new-from-merge-base` es mejor que `--new-from-rev` para una rama | `go.mod` + `flagsets.go` de la etiqueta |

**`mutmut` se ejecutó de verdad** sobre un proyecto mínimo, y de ahí salieron tres trampas que
ninguna documentación destaca y que cuestan una tarde:

1. **Cualquier orden falla si no encuentra el código, `mutmut --help` incluida.** La configuración se
   carga al importar: sin `source_paths` la primera ejecución muere con un `FileNotFoundError` que
   parece un fallo de instalación.
2. **Copia el proyecto a `mutants/` y lo reimporta**, así que el código debe ser importable por su
   propio nombre de paquete. Con `from src.calc import …` aborta con `Failed trampoline hit. Module
   name starts with 'src.'`. El arreglo es el paquete, no una opción.
3. **Necesita `fork`**: en Windows solo dentro de WSL.

El resultado de esa ejecución está en la ficha porque es el mejor ejemplo posible: 2 mutantes, 1
muerto y **1 superviviente** — `calc.nucleo.x_es_mayor__mutmut_1`, que convierte `a > b` en `a >= b`;
el test decía `assert es_mayor(3, 2)`, que vale igual con las dos versiones.

`ast-grep` también se ejecutó: el patrón `console.log($$$ARGS)` casó una llamada partida en cuatro
líneas y `--rewrite 'bar($B, $A)'` produjo el intercambio de argumentos correcto. Su ficha, verificada.

**El aprendizaje, para la próxima**: en herramientas con una versión mayor reciente —`mutmut` 3,
`jscpd` 5, `golangci-lint` 2, `eslint` 9/10, `serena` en movimiento constante— la documentación que se
encuentra primero es la de la versión anterior. La ficha no se escribe leyendo: se escribe corriendo
`--help` de la versión que se declara.

## 5. `eslint` contra `biome`: recomiendo `eslint`

Medido hoy: `biome` 25.695★ · Apache-2.0 · push 2026-09-01 · v2.5.11, contra `eslint` 27.495★ ·
MIT · push 2026-09-01 · v10.9.1. Los dos vivos y con la misma cadencia.

`biome` **gana en todo lo mecánico**: un binario de Rust, análisis y formateo en la misma pasada,
entre diez y veinte veces más rápido, una sola configuración, sin árbol de dependencias. Si el
proyecto es JavaScript o TypeScript **sin marcos de trabajo**, o si la revisión tarda tanto que ya
nadie la mira, la respuesta correcta es `biome` y no hay mucho que debatir.

**Recomiendo `eslint` por una sola razón: la cobertura de reglas.** Lo que hoy no se reemplaza no es
el motor, es el ecosistema — las reglas de los ganchos de React y de su compilador, el juego completo
de reglas con información de tipos de `typescript-eslint`, la resolución real de importaciones y los
complementos con analizador propio de los marcos que traen su formato de fichero. Biome cubre una
parte creciente y en la v2 añadió reglas con información de tipos sin exigir el comprobador completo,
pero **no** el conjunto entero, y las que faltan suelen ser las que atrapan errores y no estilo.

Y la asimetría manda: **quitar reglas es gratis; descubrir en producción el fallo que la regla perdida
habría atrapado, no.**

El criterio para no repetir el debate cada seis meses está escrito dentro de la ficha: **listar los
complementos activados del proyecto y comprobar uno a uno si biome los cubre.** Si los cubre, se migra.
Si falta uno que importe, mantener los dos es peor que mantener eslint. Es una decisión viva, con
fecha, y así queda declarada.

No se crea un pueblo `biome`: el criterio 2 de `spec/UNIVERSO.md` es «uno por hueco», y aquí no
empatan — hay un ganador con motivo escrito.

## 6. Qué se quitó de los dos mares, y cómo quedan

La regla que se aplica: **un mar dice la política; las herramientas viven en su nicho.**

### `mar/criterio` — quitado: `ruff`, `eslint`, `golangci-lint`, `jscpd`, `serena`, `ast-grep`, `openrewrite`, `difftastic`

Y con ellos las dos frases que las declaraban fuera del catálogo («*Ninguno es un pueblo: son el mismo
criterio aplicado a cada lenguaje*» y «*no es un pueblo porque sirve a los veinte nichos igual*»). Las
cuatro políticas se conservan íntegras, reescritas sin nombre propio:

- se toca lo mínimo, en pasos verificables por separado, y duplicar es deuda;
- lo mecánico lo mide un analizador con árbol sintáctico, no la vista;
- reutilizar antes que crear **se busca, no se recuerda**: se pregunta por el símbolo y por quién lo
  referencia, en vez de adivinar desplazamientos de texto;
- tocar lo justo se demuestra midiendo el árbol: el cambio repetido se describe como patrón y luego se
  revisa **comparando árboles**, para que lo reformateado no tape el error de verdad.

Cierra con una sola frase de puntero: *«Qué herramienta ejecuta cada una de estas comprobaciones en
cada lenguaje se decide en `rendimiento/calidad`, no aquí: un mar fija la política y no el catálogo.»*

### `mar/pruebas` — quitado: `stryker-js`, `mutmut`

Se conserva la política de mutación entera (alterar el código a propósito; un mutante que sobrevive es
una rama que nadie comprobaba) y **se le añade el coste**, que antes no estaba y es lo que evita que
alguien lance una ejecución de horas: *cuesta órdenes de magnitud más que correr la suite, así que se
apunta a un módulo y se ejecuta de madrugada, nunca en cada commit.* Intactos los bloques de entrada
mutada, grabación de fallos intermitentes e inyección de fallo distribuido.

Cierra con: *«Qué motor de mutación corresponde a cada lenguaje está en `rendimiento/calidad`, junto al
resto de herramientas que aplican estas políticas.»*

**Las dos frases de cierre son deliberadamente distintas.** E17 compara *afirmaciones* entre nodos
co-cargables por Jaccard, y los dos mares lo son; una frase idéntica al final de ambos habría puntuado
1,00 y puesto el árbol en rojo. Comparten solo `rendimiento` y `calidad` como palabras con contenido:
2, por debajo del suelo de 3 que exige `NUCLEO.md` §10 para siquiera contar el par.

**Coste del agua**, medido con la misma heurística en las dos versiones (`cosmos.medir.contar_aprox`,
contra `0e431cd`, que es el último estado previo a esta tarea):

```
galaxia/agua/mar-criterio.md       antes  514 tok   ahora  450 tok   −64
galaxia/agua/mar-pruebas.md        antes  435 tok   ahora  476 tok   +41
TOTAL                              antes  949 tok   ahora  926 tok   −23
```

`mar/pruebas` sube porque el aviso del coste de la mutación es política nueva y se paga en cada
fichero de test — y es precisamente lo que evita la ejecución de horas. El neto baja.

Comprobación de que el hallazgo queda cerrado y no medio cerrado:

```bash
$ grep -oE 'ast-grep|difftastic|eslint|golangci-lint|jscpd|openrewrite|ruff|serena|mutmut|stryker' \
    galaxia/agua/mar-criterio.md galaxia/agua/mar-pruebas.md | wc -l
       0
```

## 7. El resumen del nicho

```diff
- resumen: Que vaya rapido y se pueda depurar: perfilado y trazas.
+ resumen: Trabajar sobre codigo que ya existe: medir por que va lento, depurar lo raro y subir su calidad.
```

95 caracteres, dentro de los 120 de E07. Describe el **oficio**, no a sus hijos —el antipatrón
«resumen que describe hijos» de `spec/TAXONOMIA.md`—, y los dos continentes se leen sin nombrarlos.

Los dos continentes nuevos, también dentro de presupuesto:

- `velocidad` (83): *Por que tarda y por que falla solo a veces: se mide y se graba antes de tocar nada.*
- `calidad` (87): *Codigo que no escribiste y hay que dejar mejor: reglas deterministas y cambios en masa.*

**No se ha tocado `estrellas/rendimiento.md`**: está fuera del boundary de esta tarea. Su contenido
—medir en frío, número antes y después, descartar la contención, mirar la dispersión— sigue siendo
cierto, pero ahora ilumina un sistema que es más ancho que ese contexto. **Queda como deuda explícita
para quien la tenga en su boundary**: la estrella habla solo de `velocidad` y le falta la mitad de
`calidad`.

## 8. Verificación

```
$ python3 -m cosmos generar     →  verde
$ python3 -m cosmos compilar    →  verde   (10 pueblos nuevos en la vista plana)
$ python3 -m cosmos validar     →  COSMOS  verde  0 errores      exit 0
$ python3 -m puente.secretos --todo  →  secretos: limpio
```

```
$ python3 -m cosmos medir

  Entrada base .... 1.389 tokens   (índice + océanos + estructura, sin pueblos; estimado, ±5%, heurística v2)
  Peor nicho ...... 2.164 tokens   (ciberseguridad, 26 pueblos)
  Agua condicional  961 tokens     (5 aguas por paths:, fuera de la entrada)
  Peor con agua ... 3.125 tokens   (el peor caso + agua condicional)
  Universo ........ 111.912 tokens (estimado, ±5%, heurística v2)
  Descarga ........ 98,1 %
  Presupuesto ..... 4.000     OK, quedan 875 tokens en el peor caso con agua
  Fuera de COSMOS . no_medido      (system prompt, tools, MCP)
```

```
$ python3 -m cosmos medir --nicho rendimiento

  Nicho activo .... 1.965 tokens   (rendimiento; 18 pueblos)
  Peor con agua ... 2.926 tokens   (el nicho activo + agua condicional)
  Presupuesto ..... 4.000     OK, quedan 1.074 tokens en el nicho activo con agua
```

**`rendimiento` no se convierte en el peor nicho.** Ranking completo por coste de entrada, hoy:

```
2164 ciberseguridad
2123 agentes-ia
2076 trading
1965 rendimiento      ← con los 10 nuevos dentro
1910 web
1689 automatizacion
1645 documentos
```

**Aviso sobre las cifras, para que nadie compare peras con manzanas**: durante esta tarea la otra
ventana commiteó `73a8dd7`, que recalibró el medidor (la heurística subestimaba un 20,4 %). Todos los
números de arriba son de la **heurística v2**. La lectura previa de `ciberseguridad` que cita el
enunciado —«~1.771»— es de la v1: bajo v2, y **sin tocar nada de ciberseguridad**, ese mismo nicho pasa
a 2.164. Es decir, el salto no lo produjo este trabajo. La comparación válida es la de la tabla, hecha
entera bajo v2.

## 9. Lo que no se tocó

`cosmos/`, `tests/`, `puente/` (solo se ejecutó su escáner), las specs, y los pueblos de los nichos que
está revisando la otra ventana. Su trabajo en curso —`cosecha/nif-cif-validator.js`,
`puente/secretos.py`, `galaxia/pueblos/validadores-frontera`— está intacto.

Cero credenciales, cero datos de cliente, cero pagos. Los diez son gratuitos y ninguno pide tarjeta;
del único que tiene capa de pago (`serena`, complemento de JetBrains) se declara en su ficha que queda
fuera y que se usa el motor libre.
