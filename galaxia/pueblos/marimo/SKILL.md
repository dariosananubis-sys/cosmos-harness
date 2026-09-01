---
cosmos: pueblo
nombre: marimo
padre: analitica/cuadros-de-mando
resumen: Cuaderno reactivo sin estado oculto: se guarda como codigo y no puede ensenar un valor caducado.
---

https://github.com/marimo-team/marimo · Apache-2.0 · 22.587★ · último push 2026-09-01 (comprobado por
API de GitHub el 2026-09-01)

```bash
pip install "marimo[recommended]"
```

```python
# analisis.py — es un fichero de Python normal, no JSON
import marimo as mo
import duckdb

@app.cell
def _():
    desde = mo.ui.date(label="Desde")
    return (desde,)

@app.cell
def _(desde):
    df = duckdb.execute(
        "SELECT categoria, sum(importe) total FROM 'datos/*.parquet' WHERE fecha >= ? GROUP BY 1",
        [desde.value],
    ).df()
    return (df,)

@app.cell
def _(df):
    mo.ui.table(df)     # se recalcula solo cuando cambia 'desde', no cuando se toca otra celda
```

```bash
marimo edit analisis.py       # cuaderno
marimo run  analisis.py       # la misma cosa servida como aplicacion, sin celdas a la vista
python      analisis.py       # y como guion, para la ejecucion programada
```

Gana a `jupyter` en lo único que decide en este oficio: **el estado oculto**. Un cuaderno clásico
guarda la salida de una celda que se ejecutó con un código que ya no existe, y ese número puede
llevar semanas puesto en un informe sin que nadie lo note. Aquí las celdas forman un grafo de
dependencias: cambiar una recalcula las que dependen de ella y **marca como obsoletas** las que no
puede recalcular. Además se guarda como `.py`, así que un cambio se revisa en un diff en vez de en un
JSON con salidas incrustadas.

Frontera con `streamlit`, que es el vecino y no el rival: aquel es una aplicación desde el minuto
uno y reejecuta el guion entero en cada interacción; este es cuaderno mientras se explora y
aplicación cuando se enseña, con el mismo fichero.

Y lo que no hace bien:

- **Obliga a que cada celda declare lo que usa y lo que devuelve.** Eso es exactamente lo que elimina
  el estado oculto, y también lo que hace que pegar código de un cuaderno de Jupyter no funcione tal
  cual: hay variables globales que hay que ordenar. Es trabajo real de migración, no un `import`.
- **La reactividad se paga.** Una celda cara se vuelve a ejecutar cada vez que cambia algo de lo que
  depende; sin `mo.ui.run_button` o caché, mover un control lanza la consulta pesada.
- **`marimo run` no trae autenticación.** Servido en `0.0.0.0` queda abierto igual que su vecino: eso
  se resuelve con un proxy con TLS delante (`caddy`), nunca publicándolo tal cual.
- Ecosistema más joven que el de Jupyter: menos extensiones, y las salidas ricas de algunas
  bibliotecas todavía se ven peor.
