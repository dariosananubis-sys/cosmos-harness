---
cosmos: pueblo
nombre: duckdb
padre: ingenieria-datos/motor
resumen: Consulta SQL sobre CSV y Parquet dentro del proceso, derramando a disco cuando no cabe en memoria.
---

https://github.com/duckdb/duckdb - MIT - 40.897 estrellas - ultimo push 2026-09-01 (comprobado por
API de GitHub el 2026-09-01).

```bash
brew install duckdb          # el binario de linea de comandos
pip install duckdb           # la biblioteca de Python, mismo motor
```

```sql
-- consulta directa sobre ficheros, sin cargar ni importar nada
SELECT categoria, count(*) AS n, avg(importe) AS media
FROM 'datos/*.parquet'
WHERE fecha >= DATE '2026-01-01'
GROUP BY 1 ORDER BY n DESC LIMIT 10;

-- y sobre CSV, con el esquema inferido
SELECT * FROM read_csv_auto('datos/ventas.csv') LIMIT 5;
```

```bash
duckdb -c "SET memory_limit='4GB'; SET temp_directory='/tmp/duckdb'; \
           SELECT count(*) FROM 'datos/*.parquet';"
```

Un solo binario, sin servidor, sin proceso que mantener. El derrame a disco es lo que lo hace viable
con 8 GB: una consulta que no cabe en memoria se ralentiza en vez de morir, que es exactamente lo
contrario de lo que hace `pandas.read_csv` sobre un fichero de varios gigas. Frente a SQLite —el
rival obvio— la diferencia es la orientacion: aquel es por filas y esta pensado para transacciones;
este es columnar y esta pensado para agregar millones de filas.

Descartada la capa de portabilidad entre motores (`ibis-project/ibis`) y el traductor de dialectos
SQL: utiles, pero son piezas de este, no huecos propios.

Y lo que no hace bien: es de un solo escritor. No es una base de datos para una aplicacion con
varios usuarios escribiendo a la vez — abrir el mismo fichero `.duckdb` desde dos procesos en
escritura falla. Y el falso verde de memoria: sin `SET memory_limit`, coge por defecto una fraccion
grande de la RAM de la maquina y puede llevarse por delante todo lo demas antes de derramar. En un
Mac de 8 GB se fija a mano, siempre.

Es la base del resto del nicho: `evidence` lo usa por defecto, y `dbt-core` lo tiene como motor.
