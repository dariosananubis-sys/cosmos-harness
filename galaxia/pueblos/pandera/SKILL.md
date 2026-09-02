---
cosmos: pueblo
nombre: pandera
padre: ingenieria-datos/calidad
resumen: Declara tipo, rango y unicidad de cada columna y falla justo donde el dato se rompe.
---

https://github.com/unionai-oss/pandera · MIT · 4.446★ · último push 2026-09-01 (comprobado por API de GitHub el 2026-09-01).

```bash
pip install pandera
```

```python
import pandas as pd
import pandera.pandas as pa

esquema = pa.DataFrameSchema({
    "id":        pa.Column(str,   pa.Check.str_length(1, 40), unique=True),
    "categoria": pa.Column(str,   pa.Check.isin(["a", "b", "c"])),
    "importe":   pa.Column(float, pa.Check.ge(0), nullable=False),
    "fecha":     pa.Column("datetime64[ns]"),
})

df = pd.read_parquet("datos/limpio.parquet")
try:
    esquema.validate(df, lazy=True)          # lazy=True: recoge TODOS los fallos, no solo el primero
except pa.errors.SchemaErrors as e:
    print(e.failure_cases)                   # que fila, que columna, que valor
    raise
```

Ligera y dentro del proceso, sin servidor de documentacion ni dependencias pesadas: encaja con
`duckdb` y `polars` en el mismo guion. Gana a `fivetran/great_expectations` —el estandar mas
conocido de validacion de datos, y el rival real— en este entorno concreto: aquel es mas completo y
trae su propia web de informes, pero es infraestructura para un equipo, no para un portatil de 8 GB.
Si lo que hace falta es que un guion pare cuando el dato viene mal, esto son quince lineas.

Prioridad de este nicho: detectar que el dato esta mal, antes que pintarlo bonito. Por eso este
pueblo entra y varias bibliotecas de graficos no.

Y lo que no hace bien: no valida lo que no declaras. Una columna que no esta en el esquema pasa sin
mirar (salvo `strict=True`), un `Check` mal escrito da verde, y un `DataFrame` vacio cumple casi
cualquier esquema — hay que anadir `pa.Check(lambda df: len(df) > 0, element_wise=False)` a
proposito. El falso verde vive ahi: en el cero que se confunde con "no lo se".

Y sin `lazy=True` corta en el primer fallo, asi que un informe de validacion dice una cosa de mil.
