---
cosmos: pueblo
nombre: dagster
padre: ingenieria-datos/orquestacion
resumen: Orquesta por tabla producida, no por tarea, y avisa de cual esta vieja o rota antes de usarla.
---

https://github.com/dagster-io/dagster · Apache-2.0 · 16.079★ · último push 2026-09-01 (comprobado por
API de GitHub el 2026-09-01)

```bash
pip install dagster dagster-webserver
```

```python
# definiciones.py
import dagster as dg
import polars as pl

@dg.asset
def ventas_crudas() -> pl.DataFrame:
    return pl.read_csv("datos/ventas.csv")

@dg.asset_check(asset=ventas_crudas, blocking=True)      # bloquea a los que dependen de el
def sin_importes_negativos(ventas_crudas: pl.DataFrame) -> dg.AssetCheckResult:
    malas = ventas_crudas.filter(pl.col("importe") < 0).height
    return dg.AssetCheckResult(passed=malas == 0, metadata={"filas_malas": malas})

@dg.asset(deps=[ventas_crudas])
def resumen_ventas() -> None:
    ...

defs = dg.Definitions(assets=[ventas_crudas, resumen_ventas], asset_checks=[sin_importes_negativos])
```

```bash
dagster dev -f definiciones.py        # panel en http://localhost:3000
```

La unidad no es la tarea sino **el dato que produce**, y esa es la diferencia que importa aquí: un
orquestador de tareas dice «el paso 4 falló»; este dice «la tabla de ventas es de hace tres días y su
comprobación de importes está en rojo», que es la frase que evita construir un cuadro de mando encima
de un dato podrido. `asset_check(blocking=True)` es lo que hace que la detección **pare** en vez de
solo registrarse.

Gana a `apache/airflow` (46.677★, el más instalado) y a `PrefectHQ/prefect` (23.752★, el más ligero)
en lo que pide este oficio: los dos orquestan tareas y ninguno sabe qué tabla quedó vieja sin que se
lo escribas aparte. Airflow además exige base de datos y planificador permanentes; `dagster dev` es un
proceso que se levanta y se baja. Frontera con `snakemake`, que vive en el nicho científico: aquel
encadena ficheros y procesos de cualquier tipo; este encadena tablas y sabe cuándo caducan.

Y lo que no hace bien:

- **Es infraestructura, y se nota.** Para un solo guion con `cron` esto es desproporcionado; entra
  cuando hay varios pasos dependientes y a alguien le importa cuál falló. Montarlo antes es la
  sobreingeniería típica del nicho.
- **`dagster dev` no es producción**: sirve el panel y ejecuta en el mismo proceso. Para que los
  horarios corran de verdad hacen falta el demonio y una base de datos, y ahí ya hay servicio que
  mantener.
- **Las comprobaciones que no escribas no existen.** Un grafo entero en verde solo dice que el código
  terminó; `dbt test` y `pandera` siguen siendo quien mira el dato. Esto es lo que las coloca en el
  sitio correcto del grafo y bloquea aguas abajo.
- La versión de pago del mismo fabricante (Dagster+) es un servicio alojado; todo lo de arriba corre
  en local sin cuenta ni tarjeta.
