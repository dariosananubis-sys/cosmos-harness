---
cosmos: pueblo
nombre: sqlmesh
padre: ingenieria-datos/orquestacion
resumen: Plan/apply al estilo Terraform sobre modelos SQL, con entorno de desarrollo aislado sin duplicar el almacen.
---

https://github.com/SQLMesh/sqlmesh · Apache-2.0 · 3.269★ · último push 2026-09-01 (comprobado
2026-09-03). Slug canónico: el repositorio vivía en `TobikoData/sqlmesh` y hoy redirige (301) a
`SQLMesh/sqlmesh` — proyecto de la Linux Foundation.

```bash
pipx install "sqlmesh[duckdb]"        # el adaptador de motor se elige como extra, igual que en dbt
```

```sql
-- models/ventas_por_categoria.sql
MODEL (
  name analitica.ventas_por_categoria,
  kind FULL,
  audits (NOT_NULL(columns = (categoria)))
);

SELECT categoria, count(*) AS n, sum(importe) AS total
FROM analitica.ventas_limpias
GROUP BY categoria
```

```bash
sqlmesh init duckdb                    # crea el proyecto con el motor elegido
sqlmesh plan                           # muestra el impacto EXACTO del cambio antes de aplicarlo
sqlmesh test                           # pruebas unitarias sobre una fila de ejemplo, sin tocar el almacen
sqlmesh run                            # ejecuta segun el cron declarado en cada MODEL
```

Rival declarado del propio proyecto contra `dbt-core`, que es el otro pueblo de este país: la
diferencia que paga el cambio es el flujo **plan/apply al estilo Terraform** — `sqlmesh plan` calcula
y muestra qué modelos aguas abajo cambian antes de tocar nada, con clasificación automática de cambio
disruptivo o no disruptivo (breaking/non-breaking), donde `dbt run` simplemente ejecuta. Y sus
**entornos de desarrollo virtuales** dan una copia lógica del almacén para probar un cambio sin pagar
el coste de duplicar los datos físicamente, que es donde `dbt` con sus esquemas de desarrollo sí gasta
cómputo del almacén.

Frente a `snakemake` —el otro vecino con el que `dbt-core` ya marca frontera—, la misma línea aplica
aquí: aquel encadena ficheros y procesos de cualquier tipo, `sqlmesh` encadena modelos dentro de un
almacén de datos.

Ojo: es un proyecto **joven frente a su rival** (3.269★ contra las 13.756★ de `dbt-core`) y con menos
integraciones de terceros ya escritas — el catálogo de paquetes de la comunidad `dbt` (`dbt_utils` y
similares) no tiene equivalente de ese tamaño aquí todavía. Y el mismo aviso que ya lleva `dbt-core`
aplica igual: un `sqlmesh run` en verde dice que el SQL se ejecutó, no que el dato sea correcto — las
`audits` declaradas en el `MODEL` son las que detectan eso, y un modelo sin ninguna declarada pasa
siempre.
