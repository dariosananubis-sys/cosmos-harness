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

Aplicando `FACTOR_CALIBRACION = 1.204`:

```
error medio 5,2 %   ·   peor caso 33,6 %
```

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

Si el ratio se aleja de 1,0, el factor se ha quedado viejo: el corpus cambió, o el tokenizador de
referencia. **Se actualiza el factor y se actualiza este fichero con su fecha**, nunca uno sin el
otro.
