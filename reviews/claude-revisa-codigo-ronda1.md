# Revisión adversarial — Claude sobre el código de Codex (ronda 1)

**Piezas revisadas**: `cosmos/modelo.py`, `cosmos/medir.py`, `cosmos/generar.py` (578 líneas).
**Premisa**: el código está mal y mi trabajo es demostrarlo.
**Fecha**: 2026-09-01.

Todo hallazgo trae la invocación completa, copiable y ejecutable. Un hallazgo que no se puede
reproducir copiando y pegando no es un hallazgo: es una sospecha con buena presentación.

Preparación común (`validar.py` aún no existe, así que el `__init__` del paquete no importa):

```bash
cd /tmp && rm -rf cosmostest && mkdir -p cosmostest/arbol && cd cosmostest
mkdir cosmos_t && cp /Users/<usuario>/cosmos/cosmos/{modelo,medir,generar}.py cosmos_t/
: > cosmos_t/__init__.py
cat > arbol/galaxia.md <<'EOF'
---
cosmos: galaxia
nombre: prueba
resumen: Galaxia de prueba.
---
EOF
cat > arbol/oceano.md <<'EOF'
---
cosmos: oceano
nombre: seguridad
moja: ["**"]
resumen: No borrar nada sin permiso.
---
Regla corta.
EOF
```

---

## H1 — CONFIRMADO, grave. La descarga puede ser negativa

**Invocación:**

```bash
cd /tmp/cosmostest && python3 -c "
from cosmos_t.modelo import cargar_arbol
from cosmos_t.medir import medir_arbol
a = cargar_arbol('arbol')
r = medir_arbol(a, metodo='aprox')
print('entrada =', r.entrada, '| arbol =', r.arbol, '| descarga =', r.descarga)
"
```

**Salida real:**

```
entrada = 76 | arbol = 49 | descarga = -0.5510204081632653
```

Y por la vía de formateo, `Descarga ........ -55,1 %`.

**Causa raíz** (`medir.py:122`): `descarga = 1 - entrada / total_arbol`, donde `total_arbol` suma
solo `arbol.nodos`. Pero `entrada` (líneas 106-113) incluye dos cosas **que no son nodos**: el
índice generado y el catálogo visible. Numerador y denominador son universos distintos, así que el
cociente no está acotado y `entrada > árbol` es perfectamente alcanzable — de hecho es lo normal en
árboles pequeños, que es justo cuando alguien está probando COSMOS por primera vez.

No es cosmético. La descarga es la métrica de cabecera de `spec/MEDIDOR.md` y se define ahí como
fracción de lo que existe pero no se paga. Un −55 % no significa nada, y el primer contacto de
cualquiera con la herramienta es un número absurdo.

**Fix propuesto**: que el denominador sea el universo completo del que la entrada es subconjunto:

```
total = tokens(árbol) + tokens(índice) + tokens(catálogo)
```

Con eso `entrada ⊆ total` por construcción y `descarga ∈ [0, 1]` siempre. Y merece un test que lo
fije: **ningún árbol produce una descarga fuera de [0, 1]**, con el caso mínimo de arriba como
regresión, porque es el que lo destapó.

## H2 — CONFIRMADO, grave. `metodo="auto"` hace que el veredicto dependa de la máquina

`medir.py:77-79`: con `metodo="auto"` (el valor por defecto de `medir_arbol`), se usa `exacto` si
`tiktoken` está importable y `aprox` si no.

El resultado es que **el mismo árbol da dos números distintos según la máquina**, y como
`spec/VALIDADOR.md` E16 pone en rojo al superar el presupuesto, el mismo árbol puede validar en
verde en el portátil de quien lo escribió y en rojo en CI, o al revés. Sin que nadie haya cambiado
nada. Un validador cuyo veredicto depende de qué paquetes tenga instalada la máquina no es un
validador.

No hace falta medir la diferencia entre los dos métodos para que el argumento se sostenga: si
`aprox` y `exacto` coincidieran, no harían falta dos métodos ni el margen de error que la propia
spec exige publicar. La discrepancia está admitida por diseño; lo que no puede es decidir un
veredicto.

**Lo que sí he medido**, para no afirmar de más:

```bash
cd /tmp/cosmostest && python3 -c "
from cosmos_t.medir import contar_aprox
from pathlib import Path
for f in ['GOAL.md','spec/TAXONOMIA.md']:
    t = Path('/Users/<usuario>/cosmos/'+f).read_text(encoding='utf-8')
    pal = contar_aprox(t); by = len(t.encode())/4
    print(f'{f:22} aprox={pal:6}  bytes/4={by:8.0f}  ratio={by/pal:.2f}')
"
```

```
GOAL.md                aprox=  1648  bytes/4=    1720  ratio=1.04
spec/TAXONOMIA.md      aprox=  1780  bytes/4=    1788  ratio=1.00
```

La heurística de palabras coincide con la vieja regla bytes/4 (ratio ≈ 1,0). Lo que **no** he podido
medir es su error contra un tokenizador BPE real, porque no hay `tiktoken` en esta máquina — así que
no afirmo nada sobre esa desviación. Queda como `no_medido`, que es lo que la propia spec exige
hacer con lo que no se ha observado.

**Fix propuesto**: `aprox` como defecto fijo y reproducible; `exacto` solo cuando se pide
explícitamente. Y E16 se evalúa **siempre con el mismo método**, declarado en `cosmos.toml`, para
que el veredicto sea una propiedad del árbol y no del entorno.

## H3 — CONFIRMADO, medio. Se cuenta como contexto el frontmatter, que no se inyecta

`modelo.py:257` guarda en `Nodo.contenido` el fichero **entero**, frontmatter incluido, y
`medir.py:110` mete ese contenido completo de cada océano en la entrada.

El frontmatter es metadata del propio COSMOS: `cosmos:`, `nombre:`, `moja:`. No es texto que llegue
al contexto del modelo. Contarlo infla el coste declarado de cada océano, y los océanos son
precisamente lo que se paga siempre — o sea, el error cae justo sobre la magnitud más sensible del
sistema.

En el árbol de prueba, el océano son 31 tokens medidos de los que buena parte es su propio
frontmatter. En un árbol real con 7 océanos, el sesgo es sistemático y siempre en la misma
dirección: hace parecer más caro lo que ya se paga, y empuja a recortar contenido que no era el
problema.

**Fix propuesto**: separar `contenido` (fichero entero, para hashes y comparaciones) de `cuerpo`
(lo que va después del frontmatter) y medir **siempre** sobre `cuerpo`.

## H4 — CONFIRMADO, leve. `como_dict` pisa un valor en silencio

`medir.py:43-47`: `como_dict()` reasigna `resultado["fuera_cosmos"] = "no_medido"`
incondicionalmente, después de `asdict`.

La intención es buena y está comentada. El problema es el mecanismo: si algún día ese campo llega a
tener un valor legítimo, se pisa sin avisar y nadie lo nota, porque no hay error, ni aviso, ni
prueba que lo cubra. Es el mismo patrón que produjo los antipatrones medidos en
`research/PATRONES-HARNESS.md`: un valor que se fuerza en un sitio distinto de donde se calcula.

**Fix propuesto**: garantizarlo en el constructor (o con `__post_init__` que **falle** si llega otra
cosa), no en el serializador.

## H5 — leve, cosmético pero visible. El catálogo sale ordenado por alfabeto del nivel

`medir.py:88` y `generar.py:14` ordenan por `(cosmos, nombre, ruta)`. Como `cosmos` es una cadena,
el orden resultante es alfabético: `ciudad, continente, pais, planeta, provincia, pueblo, rio,
sistema-solar`. Es decir, el catálogo que se inyecta en contexto mezcla los niveles en un orden que
no tiene nada que ver con la jerarquía.

`modelo.py:31` ya define `RANGOS`, que es exactamente el orden bueno y está sin usar para esto.

**Fix propuesto**: ordenar por `RANGOS[cosmos]` y dejar el alfabético solo para desempatar.

## Lo que he intentado tumbar y aguanta

Para que la revisión valga algo, también hay que decir dónde no encontré nada tras buscarlo:

- **Árbol vacío.** `generar_indice` devuelve `""` con `arbol.nodos` vacío (`generar.py:21-22`), así
  que `entrada = 0`, y `medir.py:122` da `"no_definida"` en vez de dividir entre cero o publicar un
  100 % triunfal. Cumple el test 4 de `spec/MEDIDOR.md`. Intenté que diera `100 %` y no hay forma.
- **`no_medido` no se convierte en cero.** Es una cadena en el dataclass, en la salida de texto
  (`medir.py:165`) y en el JSON. Busqué una vía por la que acabara sumado como 0 y no la hay.
- **`--metodo exacto` sin tokenizador.** Levanta `MetodoNoDisponible` (`medir.py:75`) en vez de caer
  a `aprox` en silencio, que es lo que la spec exige y el fallo que esperaba encontrar.
- **Detección de ciclos en `generar_mapa`.** Marca `(ciclo)` y corta (`generar.py:69-72`). Intenté
  provocar una recursión infinita con un ciclo padre-hijo y no entra.
- **Determinismo del índice.** Todo va ordenado antes de escribir; dos ejecuciones dan el mismo
  texto, que es lo que hace viable la invariante E15.

## Veredicto

**No aprobada.** H1 y H2 tienen que corregirse antes de que esta pieza cuente como terminada: uno
publica una métrica imposible y el otro hace que el veredicto del validador dependa de la máquina
donde corre. H3 sesga sistemáticamente lo único que se paga siempre. H4 y H5 son menores y pueden
ir en la misma tanda.

El resto del código es sólido, y los cinco puntos que intenté tumbar sin conseguirlo son los que
más fácil habría sido hacer mal.
