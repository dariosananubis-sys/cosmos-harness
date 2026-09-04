---
cosmos: lluvia
nombre: fix-h20-niveles
moja: []
resumen: Seis niveles ya tenian nodo, dos no: ciudad y casa fuera; rio y lluvia usados en la galaxia.
---

# H20 — cada nivel, usado o retirado

**Fecha:** 2026-09-01 · **Arbol al medir:** `HEAD 9b5dc5d`, arbol de trabajo sucio (otra sesion
esta anadiendo pueblos a `galaxia/pueblos/` mientras se escribe esto: 209 → 229 en una hora).
Por eso todo lo que sigue se referencia **por simbolo y por nivel**, nunca por `fichero:linea`.

## La premisa del hallazgo era falsa en seis de los ocho casos

H20 midio `cosmos estado` sobre la galaxia y concluyo que «la mitad de la taxonomia no tiene un
solo nodo vivo» y que eran «spec que nadie ejercita».

`cosmos estado` carga **una** raiz: la de la configuracion que se le pase. Este repositorio tiene
**dos arboles**, y el segundo, `ejemplo/`, es un arbol completo, valido y validado en **cada push**
del CI (`cosmos validar --config ejemplo.toml`) y en `tests/test_validador.py::test_ejemplo_completo_es_verde`.
Contiene nodos de `planeta` (2), `provincia`, `luna`, `lago`, `lluvia` y `rio`.

```
$ grep -h '^cosmos:' $(find ejemplo -name '*.md') | sort | uniq -c
   1 estrella   1 galaxia   1 lago     1 lluvia    1 luna
   1 mar        2 oceano    2 planeta  1 provincia 2 pueblo  1 rio  2 sistema-solar
```

O sea: seis de los ocho **si** se ejercitan, en verde, en cada push. Lo que fallaba no era la
taxonomia: era **el instrumento**, que no puede distinguir «muerto» de «este arbol no lo necesita»
y presenta las dos cosas con la misma frase.

Y la señal util estaba en la misma medida: los dos niveles que **tampoco** estaban en el ejemplo
—`ciudad` y `casa`— son justo los dos que no tenian ningun nodo en ninguna parte. Quien monto el
arbol de muestra para ejercitar la taxonomia los dejo fuera.

## Veredicto nivel por nivel

| Nivel | Veredicto | Argumento |
|---|---|---|
| `lluvia` | **usado** (nuevo en la galaxia) | Estaba escrita y el arbol no la miraba. Ver abajo |
| `rio` | **usado** (nuevo en la galaxia) | 14 comandos reales de COSMOS; la herramienta no se describia a si misma |
| `planeta` | usado, ya | 2 nodos en `ejemplo/`. Ademas es el vocabulario vivo de `puente/proyectar.py`: el repo destino ES el planeta, y su contrato es `planeta.toml`. Retirarlo dejaria 552 lineas hablando de un nivel inexistente |
| `provincia` | usado, ya | `ejemplo/provincias/calidad.md`, agrupando dos pueblos hermanos. En la galaxia no hay ningun pais que necesite subdividirse (42 paises para 229 pueblos): crear una seria el antipatron «nivel de relleno» que la propia spec prohibe |
| `luna` | usado, ya | `ejemplo/adjuntos/luna-taller.md`, orbitando un planeta del ejemplo |
| `lago` | usado, ya | `ejemplo/agua/lago-taller.md`. En la galaxia los cinco mares cubren lo transversal y nadie ha necesitado algo mas local — y un lago inventado seria agua que se cobra sin mojar a nadie |
| `ciudad` | **RETIRADO** | Cero nodos en los dos arboles **y cero tests que crearan uno**. Las 229 skills son un unico `SKILL.md` cada una (la mayor, 3,5 KB). La prueba objetiva que lo separaba de `pueblo` —«¿hay algo que se pueda no cargar?»— no la gano nunca nadie |
| `casa` | **RETIRADO** | Cero nodos en los dos arboles. Solo vivia en tests y en un parrafo de `spec/PUEBLO.md` que, ademas, contradecia a `spec/TAXONOMIA.md`: si un pueblo puede tener partes que se abren aparte, deja de ser «atomico», que es su definicion |

**6 usados, 2 retirados.**

### Donde dudo, y por que lo digo

El caso de `provincia` es el mas fino. Su unico nodo esta en un arbol de juguete y `cosmos estado`
lo marca ademas como tramo de un solo hijo. Sigue en pie porque **agrupa de verdad** (cuelga dos
pueblos hermanos) y porque el criterio para retirar no puede ser «esta poco usado» sino «no lo usa
nadie»: lo primero es una opinion sobre el tamaño del arbol de hoy, lo segundo es un hecho. Si
manana el ejemplo se recorta, el canario de abajo lo dira solo — que es exactamente lo que se ha
montado para no volver a discutirlo de memoria.

## Que se toco en cada caso

### `lluvia` — estaba escrita y el arbol no la veia

`spec/REGISTRO.md` promete que «el validador tambien las comprueba». Era falso: `cargar_arbol`
recorria **una sola raiz** (`[raiz] arbol` = `galaxia/`) y el registro vive fuera a proposito.
Dos entradas con `cosmos: lluvia` llevaban meses escritas, validas y **sin que nadie las leyera**.
`puente/lluvia.py` si las encontraba —indexa `registro/` por su cuenta—, asi que habia dos lectores
del mismo directorio, uno ciego, y ninguno se contradecia en voz alta.

- `cargar_arbol(..., tambien=(...))` acepta raices hermanas; las rutas de una raiz añadida se
  nombran desde su directorio padre (`registro/lluvia/x.md`, no `lluvia/x.md`).
- `Configuracion.registro` + `[raiz] registro = "registro"` en `cosmos.toml`.
- Tres memorias nuevas y reales en `registro/lluvia/universo/`: el propio fallo de integracion, el
  cobro silencioso del `moja` (abajo) y por que un nivel vacio en un arbol no es un nivel muerto.

Comprobado de punta a punta, no por inspeccion:

```
$ python3 -m puente.lluvia "por que una memoria con moja se cobra" --limite 1
registro/lluvia/universo/lluvia-con-moja-se-cobra.md | ... | puntuacion=24.304
```

### El efecto secundario que encontro el arreglo: 7.700 tokens invisibles

Al conectar el registro, el validador se puso **rojo a la primera**:

```
E16  peor nicho ciberseguridad: entrada 2383 + agua condicional 8700 = 11083 > 4000
     mas caros: lluvia/migracion-puente (6624), lluvia/cosmos-sobre-el-arnes-de-origen (1115)
```

Las dos entradas llevaban `moja` con contenido (`puente/**`, `spec/**`, `cosmos/**`). Segun
`GOAL.md` §4 una lluvia entra **solo por consulta explicita**, asi que ese alcance no la carga
jamas — pero `agua_condicional` (NUCLEO §3) mete en el presupuesto **toda** agua no oceanica con
`moja` no vacio. Resultado: 7.700 tokens cargados a cada sesion que tocara ese terreno, por dos
documentos que no se abren nunca. Y el coste solo se hizo visible **al integrar**; antes estaba
igual de escrito y nadie lo medía.

Arreglo, y no como parrafo: `moja: []` en las dos, y **E10 lo exige ahora** para todo nodo
`lluvia`. La regla dura de `spec/REGISTRO.md` —«el registro nunca entra en el contexto de entrada,
ni una linea»— deja de depender de que alguien se acuerde. Con su test que la ve fallar
(`test_e10_lluvia_con_alcance_se_cobraria_sin_cargarse`), que ademas comprueba que con `moja: []`
la misma memoria pasa: lo que salta es el alcance, no la memoria.

### `rio` — 14 comandos, y la regla que los mantiene completos

Un rio por **cada punto de entrada ejecutable del repositorio**: los diez subcomandos de
`python3 -m cosmos` (`validar`, `medir`, `estado`, `generar`, `compilar`, `arrancar`, `mapa`,
`enganchar`, `desenganchar`, `saltar`) y los cuatro modulos de `puente` con `main()`
(`memoria` → `puente.lluvia`, `proyectar`, `secretos`, `gate`). Viven en `galaxia/agua/rio-*.md`
con `moja: []` e `invoca` con la linea de comando completa.

No es «rellenar el nivel»: es que el catalogo existe para decir **que hay**, y un comando que no se
sabe que existe no se invoca. El caso claro es `rio/memoria`: sin el, un agente no sabe que puede
consultar el registro y re-investiga lo que ya estaba escrito.

**Se paga, y se dice cuanto.** Los rios son el unico bloque del catalogo que no se acota por nicho:
se ven siempre. Primera version, con resumenes de 85-100 caracteres: **+390 tokens** de entrada
base. Reescritos a 57-69 caracteres sin perder que distinguen: **+287** (1.322 → 1.609, ~20,5 por
rio). El margen del presupuesto baja de 943 a 656 tokens en el peor caso con agua.

### `ciudad` y `casa` — retirada entera, no a medias

Codigo: fuera de `NIVELES_SOLIDOS`/`RANGOS` (`cosmos/modelo.py`, nueve solidos → siete);
`NIVELES_APLANADOS` pasa de `{ciudad, pueblo}` a `{pueblo}` en `cosmos/compilar.py`,
`cosmos/validar.py` y `puente/proyectar.py`; `con_resumen`/`invocables` en `cosmos/medir.py`;
el conteo por oficio en `cosmos/estado.py`; las dos palabras salen de `PALABRAS_TAXONOMIA` (eran
vocabulario del sistema y ya no lo son); E09 pasa de «16 niveles» a «14»; la ayuda de `compilar`.

Specs: `spec/TAXONOMIA.md` (tabla, frontera ciudad/pueblo, antipatron de cadena de 9→7 niveles),
`spec/FRONTMATTER.md` (rangos), `spec/NUCLEO.md` (§2 catalogo, §5 completo, §10),
`spec/COMPILACION.md`, `spec/MEDIDOR.md`, `spec/PUEBLO.md`, `spec/VALIDADOR.md` (E09, E10 y su
ejemplo de salida), `GOAL.md` §3 y §4, `README.md`.

Tests: los tres que creaban nodos `casa` (dos cadenas de identidad y aciclicidad en
`tests/test_validador.py`, y el fichero de referencia dentro de una skill en
`tests/test_compilar.py`). El de `test_compilar` es el que mejor documenta la retirada: ahora es un
`.md` **sin frontmatter**, y sigue comprobando que `compilar` exporta el directorio entero. Un
fichero de referencia dentro de una skill deja de ser un nodo y pasa a ser lo que siempre fue: un
fichero que viaja con su skill.

**El hueco queda documentado** en `spec/TAXONOMIA.md` §«Lo que se retiro»: por que se quito, y los
tres pasos —el nodo real primero, el nivel despues— para traerlo de vuelta.

## Para que H20 no se pueda volver a levantar mal: `tests/test_niveles_vivos.py`

El fallo de fondo era del instrumento, asi que el arreglo es un instrumento, no una advertencia:

- Cuenta los nodos de **todos** los arboles del repositorio a la vez (`cosmos.toml` + `ejemplo.toml`,
  cada uno con su registro) y exige que **ningun nivel de `NIVELES_VALIDOS` se quede sin nodo**.
- Un segundo test comprueba que el censo mira de verdad las dos fuentes: si solo mirara la galaxia,
  `luna` y `provincia` saldrian muertas.
- **Meta-prueba**: se le quita al censo el ultimo nodo de `luna`, `lago`, `rio` y `lluvia` y se
  exige que el canario los nombre. Un verde que nunca ha dado rojo no se distingue de uno roto.

Que habria cazado H20 en su dia, comprobado ejecutandolo:

```
$ python3 -c "from tests.test_niveles_vivos import *; from cosmos.modelo import NIVELES_VALIDOS; \
  print(niveles_muertos(arboles_del_repositorio(), NIVELES_VALIDOS | {'ciudad','casa'}))"
['casa', 'ciudad']
$ python3 -c "from tests.test_niveles_vivos import *; print(niveles_muertos(arboles_del_repositorio()))"
[]
```

Y `cosmos estado` deja de invitar al error: donde decia «la taxonomia preve mas niveles de los que
un arbol usa» ahora dice que son niveles que **este** arbol no necesita, y apunta al canario.

## Medicion, antes y despues

```
ANTES                                   DESPUES
pueblo 209                              pueblo 232   (+23 de otra sesion, no de este trabajo)
rio      0                              rio     14
lluvia   0                              lluvia   5
sin nodo: casa, ciudad, lago, lluvia,   sin nodo en LA GALAXIA: lago, luna, planeta, provincia
          luna, planeta, provincia, rio sin nodo en NINGUN arbol: ninguno

Entrada base ....  1.322                1.609   (+287, los 14 rios)
Peor nicho ......  2.096                2.383
Agua condicional     961                  961
Peor con agua ...  3.057                3.344   (presupuesto 4.000; margen 943 → 656)
Descarga ........   98,1 %               98,3 %
```

`Universo` sube de 111.844 a mas de 145.000 tokens, pero **no por este trabajo**: son los pueblos
que otra sesion fue añadiendo mientras tanto (209 → 232 durante la tarea; el numero seguia subiendo
al cerrar). Los cuerpos del registro que ahora cuenta el medidor son marginales y no tocan la
entrada. Los tres numeros que si son de este trabajo —entrada base, peor con agua y margen— no
dependen del recuento de pueblos y estan arriba.

## Verificacion

```
python3 -m cosmos compilar && python3 -m cosmos validar   → COSMOS verde 0 errores
python3 -m cosmos validar --config ejemplo.toml           → COSMOS verde 0 errores
python3 -m cosmos medir                                   → 3.344 / 4.000, OK
python3 -m unittest discover -s tests -t .                → Ran 89, OK (skipped=1)   [antes 85]
python3 -m unittest discover -s puente/tests -t .         → Ran 35, OK
python3 puente/tests/mutaciones.py                        → 8/8 invariantes vistas fallar
python3 -m puente.gate --sin-pruebas                      → exit 0
```

**`cosmos compilar` antes de `validar` no es opcional aqui**: otra sesion esta añadiendo pueblos a
`galaxia/pueblos/` en este momento, y cada uno nuevo pone E19 en rojo hasta que se recompila la
vista plana. La vista es un artefacto generado y gitignorado; no es un cambio de este trabajo.

## Lo que se salio del limite declarado, y por que

El encargo autorizaba specs, `cosmos/modelo.py`, `tests/` y nodos nuevos en `galaxia/`. Retirar un
nivel «de verdad y entero» no cabe ahi: `ciudad` estaba tambien en `cosmos/compilar.py`,
`cosmos/validar.py`, `cosmos/medir.py`, `cosmos/estado.py`, `cosmos/cli.py` y
`puente/proyectar.py`. Dejarlo solo en `modelo.py` habria sido la retirada a medias que el propio
encargo llama peor que no hacer nada. Igual con `cosmos/cli.py` (una linea) y `cosmos.toml` para
que el arbol vea el registro. **No se ha tocado `galaxia/pueblos/` ni `cosecha/`.**

## Lo que he visto y no he tocado

1. **`cosmos/cli.py` dice «comprueba las invariantes E00-E19» y ya existe E20** (lo añadio el
   commit `9b5dc5d`, de otra sesion). Es una linea de ayuda que miente. No la toco porque esa area
   la esta trabajando otro ahora mismo. Por eso el resumen de `rio/validar` dice «todas las
   invariantes» y no un rango: un resumen que caduca cada vez que se añade una invariante es un
   resumen mal escrito.
2. **`galaxia/galaxia.md` dice «Veinte oficios» y hay 21 sistemas solares** (`GOAL.md` §1 tambien).
   Cambiarlo obliga a regenerar el indice y no es de este encargo.
3. **`PLAN-MAESTRO.md` habla de ciudades y de nichos ya retirados** (`medios`, `negocio`,
   `guardia`). Es un plan historico, superado por `spec/UNIVERSO.md`; corregirle una palabra lo
   dejaria mas incoherente, no menos. `PROGRESS.md`, `reviews/` y `registro/commits/` tampoco se
   reescriben: son lo que se dijo entonces.
4. **`rio` con `moja` no vacio tendria el mismo cobro fantasma que tenia `lluvia`.** E10 solo se ha
   endurecido para `lluvia`, porque ahi lo respalda una regla dura escrita (`spec/REGISTRO.md`).
   Para `rio`, `spec/FRONTMATTER.md` dice «`moja: []` permitido», que deja la puerta abierta. Los 14
   rios creados lo llevan vacio; si alguna vez se escribe uno con alcance, se cobrara sin cargarse.
   Queda señalado, no arreglado.
