# Calibración de la heurística de conteo

`spec/MEDIDOR.md` exige que el medidor **jamás publique un número sin decir con qué método lo
obtuvo**, y que si nadie ha calibrado nunca diga `±desconocido` en vez de un margen inventado.

Durante todo el desarrollo dijo `±desconocido`. Esto es la medición que lo cierra.

## Qué se midió

**Fecha:** 2026-09-01 · **Referencia:** `tiktoken`, codificación `cl100k_base` · **Corpus:** 78
ficheros de este mismo repositorio, elegidos para cubrir lo que de verdad se cuenta:

| Clase | n | Qué es |
|---|---:|---|
| `spec/es` | 13 | Prosa técnica en castellano con tablas y bloques de código |
| `pueblo` | 40 | Fichas de herramienta: castellano + comandos + URL |
| `codigo` | 15 | Python con docstrings en castellano |
| `agua` | 10 | Prosa corta y densa |

`tiktoken` se instaló **en un entorno virtual temporal, solo para medir**. No es dependencia del
proyecto: `cosmos/medir.py` sigue funcionando con la biblioteca estándar y `tiktoken` sigue siendo
opcional en tiempo de ejecución.

## Resultado

```
clase         n  ratio medio     min     max
agua         10        1.148   1.016   1.265
codigo       15        1.164   0.800   1.575
pueblo       40        1.220   1.078   1.335
spec/es      13        1.246   1.171   1.297

GLOBAL   n=78  ratio medio=1.2043  desv=0.0927
```

**La heurística sin corregir subestimaba un 20,4 %**, y siempre en la misma dirección.

Ese detalle es el que la hace corregible: un sesgo constante no es ruido, es un factor. Contar
palabras y signos ignora que un tokenizador BPE parte las palabras largas y trata los acentos como
piezas aparte — y el castellano tiene de las dos cosas más que el inglés, que es para lo que están
afinados esos tokenizadores.

Aplicando `FACTOR_CALIBRACION` = 1.204:

```
error medio 5,2 %   ·   peor caso 33,6 %
```

## El segundo factor: lo generado no es prosa

Aquella medición usó 78 ficheros de **prosa** y ni una muestra del índice ni del catálogo, que son
justo los dos bloques que forman la entrada. Una lista de `ruta: resumen` no se parece a un párrafo:
cada barra, cada guion y cada acento es una pieza aparte para un tokenizador BPE. Usar ahí el factor
de la prosa fue el fallo **F01**, y no era un matiz — ponía verde un árbol que estaba en rojo.

Medido el 2026-09-02 sobre el índice y el catálogo de los dos árboles del repositorio:

```
`FACTOR_GENERADO` = 1.381        (prosa: 1.204)
```

`cosmos/medir.py` aplica `contar_generado` al índice y al catálogo, y `contar_aprox` a todo lo
demás. Con `--metodo exacto` no hay factores que valgan: cuenta el tokenizador.

## Por qué importaba, y no era cosmético

Antes de esto, el presupuesto de 4.000 tokens era en la práctica un presupuesto de ~4.800: el
medidor decía «1.133» donde había 1.364.

**Un presupuesto que se equivoca a su favor es peor que no tenerlo**, porque da permiso creyendo que
está midiendo. Todas las cifras publicadas antes del 2026-09-01 subestiman en torno a un 20 %.

## El peor caso: código

`codigo` tiene la mayor dispersión (0,800 a 1,575). Un fichero con muchos identificadores largos en
`snake_case` se parte en más piezas de las que cuenta la heurística; uno con mucho símbolo y poca
palabra, en menos.

Es el uso menos preciso, y conviene saberlo: para medir contexto —prosa y fichas— el error ronda el
5 %; para medir un fichero de código suelto, puede irse a un tercio.

## Cómo rehacer esta medición

```bash
python3 -m venv /tmp/calib && /tmp/calib/bin/pip install -q tiktoken
cd <repo> && /tmp/calib/bin/python - <<'PY'
import sys, pathlib, statistics; sys.path.insert(0, '.')
import tiktoken
from cosmos.medir import contar_aprox, FACTOR_CALIBRACION
enc = tiktoken.get_encoding("cl100k_base")
ratios = []
for p in list(pathlib.Path('spec').glob('*.md')) + list(pathlib.Path('galaxia/pueblos').rglob('SKILL.md')):
    t = p.read_text(encoding='utf-8')
    if not t.strip(): continue
    # contar_aprox ya aplica el factor: se deshace para medir la heurística cruda
    crudo = contar_aprox(t) / FACTOR_CALIBRACION
    ratios.append(len(enc.encode(t)) / crudo)
print(f"n={len(ratios)}  ratio={statistics.mean(ratios):.4f}")
PY
```

El guion deshace el factor antes de dividir, así que `ratio` **es** el factor que el corpus pide
hoy: por construcción sale ≈ `FACTOR_CALIBRACION` cuando el factor está sano, no ≈ 1,0. Comparar
con 1,0 —como decía esta sección hasta el 2026-09-02— daba alarma **siempre** (`n=258 ratio=1.2274`
sobre un factor correcto), y un procedimiento que siempre grita no se usa dos veces.

El criterio es:

```
abs(ratio / FACTOR_CALIBRACION - 1) > 0.05   ->  recalibrar
```

**Se actualiza el factor y se actualiza este fichero con su fecha**, nunca uno sin el otro.
`tests/test_medidor.py` ata los tres números publicados aquí a los del módulo, así que un factor
cambiado sin tocar este fichero (o al revés) sale en rojo.

## Verificar el margen de verdad: hace falta el tokenizador

`test_aproximado_y_exacto_respetan_margen_publicado` es la única prueba de la métrica principal, y
**se salta si no hay `tiktoken`**. Durante un día estuvo en verde solo por eso, comparando siete
líneas de juguete que divergían un 19,05 % contra el 5,2 % publicado (fallo **F03**). Ahora el
corpus es el árbol real y el aviso del salto es ruidoso. Para exigir que falle en vez de saltarse:

```bash
python3 -m venv /tmp/calib && /tmp/calib/bin/pip install -q tiktoken
COSMOS_EXIGE_TOKENIZADOR=1 /tmp/calib/bin/python -m unittest discover -s tests -t .
```

### Pendiente: el veredicto exacto sigue en rojo (residuo de F01)

Medido el 2026-09-02 sobre la galaxia, con los factores de arriba:

```
aprox    entrada=2.644  agua=1.346  con_agua=3.990   OK, quedan 10
exacto   entrada=2.778  agua=1.545  con_agua=4.323   ROJO, excede en 323
```

Los dos factores redujeron el error pero no lo cerraron: la prosa real tokeniza hoy a **1,243** y
los bloques generados a **≈1,455**. El árbol **no cabe** en 4.000 con el tokenizador de referencia,
y eso no se arregla calibrando —se arregla decidiendo qué contenido sale, o qué presupuesto es el
bueno—. `tests/test_medidor.py::test_canario_f01_el_veredicto_exacto_sigue_en_rojo` lo vigila: el
día que se cierre, esa prueba se pone roja y se borra con el arreglo.
