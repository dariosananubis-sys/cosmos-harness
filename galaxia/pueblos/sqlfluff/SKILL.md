---
cosmos: pueblo
nombre: sqlfluff
padre: ingenieria-datos
resumen: Analiza el SQL por su dialecto y por las plantillas antes de que llegue al almacen a ejecutarse.
---

https://github.com/sqlfluff/sqlfluff · MIT · 9.865★ · último push 2026-09-01 (comprobado por API de
GitHub el 2026-09-01)

```bash
pip install "sqlfluff[dbt]"      # sin el extra tambien vale para .sql sin plantillas
```

```ini
# .sqlfluff en la raiz del proyecto
[sqlfluff]
dialect = duckdb
templater = dbt
max_line_length = 100

[sqlfluff:rules:capitalisation.keywords]
capitalisation_policy = lower
```

```bash
sqlfluff lint models/            # sale distinto de cero si algo falla: sirve de puerta en la tuberia
sqlfluff fix models/ --force     # corrige lo que se puede corregir solo
```

Analiza de verdad: construye el árbol sintáctico **del dialecto concreto** —DuckDB, Postgres, BigQuery,
Snowflake y dos docenas más— después de renderizar las plantillas de Jinja, así que un `ref()` mal
escrito o un paréntesis que solo rompe en ese motor sale aquí y no a mitad de una carga de treinta
minutos.

Gana a `sqlglot` (9.582★), que es la otra biblioteca seria del hueco y ya quedó anotada y fuera del
árbol como traductor de dialectos: aquel es una biblioteca para construir herramientas, no una puerta
de línea de comandos con reglas configurables y código de salida. Y gana al formateador del editor por
lo mismo: aquel alinea texto, este entiende el dialecto y las plantillas.

Frontera con sus vecinos, que es lo que decide cuál usar: esto mira **el SQL**; `dbt test` mira **el
resultado del SQL**; `pandera` mira **el dataframe**. Ninguno sustituye a otro.

Y lo que no hace bien:

- **No sabe si el resultado es correcto.** Un `JOIN` que multiplica filas está perfectamente escrito.
  Esto es análisis estático, no calidad de dato — que es la prioridad de este oficio, y por eso este
  pueblo es el escalón de abajo, no la meta.
- **Con el renderizador de plantillas es lento** y necesita que el proyecto compile: si las
  credenciales del perfil no están, no arranca. Para un repaso rápido, `templater = jinja`.
- **`fix` toca tus ficheros.** Sin control de versiones limpio antes, no se ejecuta.
- El dialecto por defecto es ANSI y **acepta como bueno lo que su motor rechazará**: si no se declara
  el dialecto real, el verde no significa nada.
