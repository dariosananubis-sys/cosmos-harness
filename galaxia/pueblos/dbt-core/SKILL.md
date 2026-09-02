---
cosmos: pueblo
nombre: dbt-core
padre: ingenieria-datos/orquestacion
resumen: Encadena modelos SQL en control de versiones con pruebas declarativas y documentacion generada.
---

https://github.com/dbt-labs/dbt-core · Apache-2.0 · 13.756★ · último push 2026-09-01 (comprobado 2026-09-01)
(comprobado por API de GitHub el 2026-09-01).

```bash
pipx install dbt-core dbt-duckdb        # el adaptador va aparte, uno por motor
```

```sql
-- models/ventas_por_categoria.sql
{{ config(materialized='table') }}
SELECT categoria, count(*) AS n, sum(importe) AS total
FROM {{ ref('ventas_limpias') }}
GROUP BY 1
```

```yaml
# models/schema.yml — aqui esta el motivo de que este pueblo exista
models:
  - name: ventas_por_categoria
    columns:
      - name: categoria
        tests: [not_null, unique]
      - name: total
        tests:
          - dbt_utils.accepted_range: {min_value: 0}
```

```bash
dbt debug          # comprueba la conexion antes de nada
dbt run
dbt test           # AQUI se detecta que el dato esta mal
dbt docs generate && dbt docs serve
```

Lo que convierte una carpeta de consultas sueltas en una tuberia con dependencias, pruebas y linaje:
`ref()` construye el grafo solo, asi que el orden de ejecucion deja de estar en la cabeza de alguien.
Las pruebas declarativas son el motivo de que entre y no otra plantilla de SQL — sin ellas esto es
solo Jinja sobre `.sql`. Frontera con `snakemake`: aquel encadena ficheros y procesos de cualquier
tipo; este encadena modelos dentro de un almacen de datos.

Y lo que no hace bien, que es el falso verde mas caro del nicho: **`dbt run` en verde no dice nada
sobre la calidad del dato.** Significa que el SQL compilo y se ejecuto. El que detecta que el dato
esta mal es `dbt test`, y es un comando aparte que hay que acordarse de correr — en una tuberia
automatica van siempre los dos, y el fallo de `test` tiene que parar el despliegue. Un modelo sin
`tests:` en su `schema.yml` pasa siempre.

Y otro aviso: `dbt-core` es Apache-2.0 y gratis; dbt Cloud, el servicio del mismo fabricante, es de
pago por suscripcion. Todo lo de arriba corre en local sin cuenta ni tarjeta.
