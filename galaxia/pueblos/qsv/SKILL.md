---
cosmos: pueblo
nombre: qsv
padre: ingenieria-datos/motor
resumen: Valida y perfila un CSV mal formado antes de cargarlo, en lugar de dejar que el motor lo adivine.
---

https://github.com/dathere/qsv · **MIT**, leído en su fichero `COPYING` el 2026-09-01 (la API de
GitHub lo reporta como `NOASSERTION`; antes era doble licencia con Unlicense) · 3.772★ · último push
2026-09-01 (misma comprobación)

```bash
brew install qsv
```

```bash
# 1. esta bien formado? Sale distinto de cero y escribe los errores con su numero de fila
qsv validate entrada.csv

# 2. y cumple el contrato? Validacion contra un esquema JSON Schema
qsv validate entrada.csv esquema.json

# 3. que hay dentro, sin abrirlo: tipos, minimos, maximos, nulos y cardinalidad
qsv stats entrada.csv --everything | qsv table
qsv frequency entrada.csv --limit 5 | qsv table
```

El fichero que manda un cliente casi nunca es un CSV correcto: comillas sin cerrar, filas con un
campo de más, mezcla de codificaciones, saltos de línea dentro de un campo. `duckdb` y `polars` leen
CSV muy bien y por eso mismo **adivinan**: descartan la fila rara, infieren el tipo del primer bloque
y siguen. Esto hace lo contrario, que es lo que pide este oficio: dice en qué fila y en qué columna
está roto, y devuelve código de salida.

Gana a `csvkit`, el conjunto clásico de utilidades de CSV en Python: aquel resuelve lo mismo pero en
un orden de magnitud más de tiempo sobre ficheros grandes y sin validación contra esquema. Y gana a
abrirlo en una hoja de cálculo, que es lo que se hace de verdad, por el motivo obvio: la hoja de
cálculo **corrige en silencio** —recorta ceros a la izquierda, convierte a fecha lo que no lo es— y
nadie se entera.

Frontera con `pandera`: aquel valida un dataframe ya cargado en memoria; esto valida el fichero antes
de que exista ningún dataframe, que es donde se cazan los errores de formato.

Y lo que no hace bien:

- **`validate` sin esquema solo comprueba la forma** (RFC 4180 y codificación), no el contenido. Un
  CSV impecable lleno de valores absurdos pasa limpio.
- **`stats` recorre el fichero entero**, y con `--everything` calcula percentiles y cardinalidad: en
  un fichero muy grande eso es tiempo, aunque el consumo de memoria se mantenga acotado por su lectura
  en flujo.
- **No lee Excel ni Parquet en el binario base.** Para `.xlsx` hay `qsv excel` en las compilaciones
  con esa característica activada; la de Homebrew no trae todas, y `qsv --version` dice cuáles hay.
- Es una caja de herramientas, no una tubería: transforma con `select`, `search`, `join` y compañía,
  pero para transformación de verdad manda `polars` o `duckdb`.
