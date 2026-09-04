---
cosmos: pueblo
nombre: arrow
padre: ingenieria-datos/motor
resumen: Formato columnar en memoria que polars y duckdb ya hablan por dentro; sirve para pasar datos entre los dos sin copiar.
---

https://github.com/apache/arrow · Apache-2.0 · 17.078★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
pip install pyarrow
```

```python
import pyarrow as pa
import pyarrow.parquet as pq

tabla = pa.table({"categoria": ["a", "b", "a"], "importe": [10.5, 20.0, 5.25]})
pq.write_table(tabla, "datos.parquet")            # Parquet es la serializacion en disco de este formato

# el mismo buffer de memoria, sin copiar, entre dos motores que lo hablan:
import duckdb
duckdb.sql("SELECT categoria, sum(importe) FROM tabla GROUP BY categoria").arrow()
```

No es un motor de consulta — es el **formato columnar en memoria** que ya usan por dentro sus dos
vecinos de este país: `polars` está escrito sobre una implementación Arrow en Rust, y `duckdb` lee y
devuelve tablas Arrow de forma nativa (`.arrow()` en el ejemplo de arriba). Se instala aparte cuando
hace falta **mover datos entre motores sin serializar y deserializar**: el mismo bloque de memoria
columnar pasa de `duckdb` a `polars` a un modelo de scikit-learn sin una copia intermedia — eso es lo
que arreglaron el "protocolo de intercambio Arrow" y el formato Feather.

Gana a serializar a CSV o a JSON entre pasos de una tubería en la única cosa que importa: cero coste
de (de)serialización y tipos exactos conservados (una fecha sigue siendo fecha, no una cadena que hay
que reparsear). Frente a Parquet a secas —el formato en disco, no en memoria—, la relación es
complementaria, no rival: Parquet es como Arrow se guarda cuando el dato descansa; Arrow es como
vive mientras se procesa.

Ojo: por sí solo, `pyarrow` no es donde se escribe lógica de negocio — para consultar o transformar de
verdad se usa `duckdb` o `polars` encima. Y el falso verde de este en concreto: dos procesos pueden
declarar el mismo esquema Arrow y aun así fallar al compartir memoria si las versiones de la
biblioteca no coinciden en el ABI — fijar la misma versión de `pyarrow` en ambos extremos del
intercambio, no asumir que "es Arrow" basta.

Ojo de nombre: `pip install arrow` NO instala esto — instala `arrow-py` (manejo de fechas), otra
herramienta; el paquete correcto de Apache Arrow en Python es `pyarrow`, el de arriba.
