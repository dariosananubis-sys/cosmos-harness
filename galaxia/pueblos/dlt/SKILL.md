---
cosmos: pueblo
nombre: dlt
padre: ingenieria-datos
resumen: Carga de origen a destino con contrato de esquema: si la fuente cambia de forma, falla o aparta.
---

https://github.com/dlt-hub/dlt · Apache-2.0 · 5.806★ · último push 2026-09-01 (comprobado por API de
GitHub el 2026-09-01)

```bash
pip install "dlt[duckdb]"
```

```python
import dlt, requests

@dlt.resource(
    name="pedidos",
    write_disposition="merge", primary_key="id",
    schema_contract={"tables": "evolve", "columns": "freeze", "data_type": "freeze"},
)
def pedidos():
    yield requests.get("https://<API_DEL_ORIGEN>/pedidos", timeout=30).json()

tuberia = dlt.pipeline(pipeline_name="ventas", destination="duckdb", dataset_name="crudo")
info = tuberia.run(pedidos())
print(info)                      # filas cargadas, esquema aplicado y trabajos fallidos
```

El motivo de que entre es `schema_contract`, y no la carga: con `columns: "freeze"` una columna nueva
en el origen **para la carga con un error que la nombra**, en vez de aparecer en silencio tres
semanas después en un informe. Los otros modos son igual de explícitos —`evolve` la acepta, `discard_value`
la tira, `discard_row` descarta la fila entera— y la decisión queda escrita en el código, no en la
cabeza de alguien.

Gana a escribir el `requests` + `INSERT` a mano, que es la alternativa real en un encargo pequeño:
ahí no hay esquema, hay lo que la API devolviera ese día. Y gana a `airbytehq/airbyte` en este
entorno por peso: aquel es una plataforma con servicios que mantener; esto es una biblioteca de
Python que se importa dentro del guion que ya existe. Encaja aguas arriba de `dbt-core`: este trae el
dato crudo con su contrato, aquel lo transforma.

Y lo que no hace bien:

- **`evolve` es el modo por defecto de las tablas**, así que si no se escribe el contrato no hay
  contrato: el esquema se adapta solo y el fallo vuelve a ser silencioso. El valor de este pueblo está
  en la línea que casi nadie escribe.
- **No valida contenidos, solo forma.** Que la columna `importe` exista y sea numérica no dice nada de
  si el importe es correcto: eso es `pandera` sobre el dataframe o `dbt test` sobre la tabla.
- **La inferencia de tipos manda en la primera carga.** Si el primer lote trae un entero donde después
  vendrán decimales, el tipo queda fijado y las cargas siguientes chocan contra su propia decisión.
- Los registros fallidos van a un destino de descarte y **el proceso puede terminar con código 0**
  habiendo apartado filas: hay que leer el objeto que devuelve `run()`, no solo el código de salida.
