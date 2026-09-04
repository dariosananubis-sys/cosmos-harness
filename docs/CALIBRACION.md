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

Los dos números se publican en la salida de `cosmos medir` («±5,2 % medio (peor fichero 33,6 %)») y
el **medio** se aplica al veredicto del presupuesto: E16 compara `entrada_con_agua × 1,052` con el
techo, no la estimación desnuda. El peor caso por fichero se publica y **no** se aplica: describe un
fichero de código suelto, no la suma de quinientos ficheros, y el sesgo de una suma está acotado por
el error medio absoluto (desigualdad triangular). Medido el 2026-09-03 sobre la galaxia: aproximado
3.546, exacto 3.654 → desvío agregado **3,0 %**, dentro del margen que se aplica (auditoría A-10).

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
demás.

Re-medido el 2026-09-02 tras pasar el catálogo a árbol indentado: el ratio real sobre la galaxia
(índice + los 22 catálogos por nicho) da 1,369 — un 0,9 % por debajo del factor publicado, del
lado conservador (el aproximado sobreestima el coste). El factor no se toca por eso: solo se
recalibraría si la desviación creciera o cambiara de signo. Con `--metodo exacto` no hay factores que valgan: cuenta el tokenizador.

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
# Fuera de /tmp: el venv que citaba el registro (/tmp/calib) se evaporó con un reinicio y el
# margen llevó días sin verificarse en ninguna instalación (auditoría B-10 / D-08).
python3 -m venv ~/.cosmos/calib && ~/.cosmos/calib/bin/pip install -q -r requirements-dev.txt
cd <repo> && ~/.cosmos/calib/bin/python - <<'PY'
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
python3 -m venv ~/.cosmos/calib && ~/.cosmos/calib/bin/pip install -q -r requirements-dev.txt
COSMOS_EXIGE_TOKENIZADOR=1 ~/.cosmos/calib/bin/python -m unittest discover -s tests -t .
```

Y lo hace alguien sin que haya que acordarse: el trabajo `calibracion` de
`.github/workflows/cosmos.yml` instala el tokenizador en un venv desechable y corre la suite con
`COSMOS_EXIGE_TOKENIZADOR=1`. El trabajo `verificar` sigue sin dependencias: el verde de un clon
recién bajado no necesita red, y el del margen sí tiene auditor.

### Cerrado: el veredicto exacto ya no está en rojo (residuo de F01)

El 2026-09-02, con los factores de arriba, el árbol no cabía con el tokenizador de referencia
(`exacto con_agua=4.323 > 4.000` frente a `aprox 3.990`), y un canario en `tests/test_medidor.py`
afirmaba ese rojo para que no se olvidara. El commit que adelgazó el contenido ese mismo día lo
cerró, y el canario llevó un día pidiendo que lo borraran sin que nadie lo oyera: solo hablaba con
tokenizador (auditoría E-11). **Las cifras de abajo son del árbol de trabajo al cierre del ciclo 2
(2026-09-03, sobre `b0c1ebd`); envejecen con cada alta y la que vale es la que imprime el comando**
(revisión R-49):

```
~/.cosmos/calib/bin/python -m cosmos medir --metodo exacto
  Peor con agua ... 3.817 tokens   (el peor caso + agua condicional)
  Presupuesto ..... 4.000     OK, quedan 183 tokens en el peor caso con agua (ciberseguridad); ≈ 6 herramienta(s) más en ese nicho
python3 -m cosmos medir
  Peor con agua ... 3.701 tokens   (el peor caso + agua condicional)
  Presupuesto ..... 4.000     OK, quedan 106 tokens con el margen calibrado (+5,2 %) en el peor caso con agua (ciberseguridad); ≈ 3 herramienta(s) más en ese nicho
```

El canario se sustituyó por `test_el_veredicto_exacto_y_el_aproximado_coinciden_sobre_la_galaxia`:
los dos métodos tienen que dar el mismo veredicto y el desvío agregado no puede superar el margen
que se aplica. Si divergen, o el contenido creció hasta el borde o la calibración caducó.
