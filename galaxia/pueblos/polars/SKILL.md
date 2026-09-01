---
cosmos: pueblo
nombre: polars
padre: ingenieria-datos/motor
resumen: Marcos de datos en Rust con modo perezoso: planifica antes de leer y evita cargar de mas.
---

https://github.com/pola-rs/polars - MIT - 39.580 estrellas - ultimo push 2026-09-01 (comprobado por
API de GitHub el 2026-09-01).

```bash
pip install polars
```

```python
import polars as pl

# modo perezoso: planifica antes de leer, y solo lee las columnas y filas que hacen falta
q = (
    pl.scan_parquet("datos/*.parquet")
      .filter(pl.col("fecha") >= pl.date(2026, 1, 1))
      .group_by("categoria")
      .agg(pl.col("importe").mean().alias("media"), pl.len().alias("n"))
      .sort("n", descending=True)
)
print(q.explain())          # el plan, antes de gastar un segundo
print(q.collect().head(10)) # aqui ejecuta

# streaming, cuando el resultado tampoco cabe
q.sink_parquet("salida.parquet", engine="streaming")
```

Entra junto a `duckdb` y no en su lugar porque el modelo mental es distinto: aqui se encadenan
transformaciones tipadas, alli se escribe una consulta. Gana a `pandas` —que es el rival de verdad,
no un rival de paja— en lo que decide en una maquina de 8 GB: `pandas.read_csv` lee el fichero
entero a memoria antes de que puedas filtrarlo; `scan_csv`/`scan_parquet` no lee nada hasta
`collect()` y puede saltarse columnas y grupos de filas completos.

Y una ventaja de correccion, no de velocidad: el esquema se fija al inferirse, asi que una columna
con un valor raro falla en voz alta en vez de convertirse en `object` de texto en silencio, que es
como `pandas` corrompe un analisis sin que nadie se entere.

Y lo que no hace bien: el ecosistema. Media biblioteca cientifica de Python espera un `DataFrame` de
`pandas` — `scikit-learn`, `statsmodels`, casi cualquier libreria de graficos. `df.to_pandas()`
funciona, pero copia todo a memoria y ahi se pierde la ventaja entera. Y la API rompe entre
versiones mayores mas de lo que la gente espera: fijar version.
