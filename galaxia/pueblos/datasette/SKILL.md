---
cosmos: pueblo
nombre: datasette
padre: analitica/cuadros-de-mando
resumen: Convierte un fichero de datos en un sitio navegable con consultas y API, en un solo comando.
---

https://github.com/simonw/datasette · Apache-2.0 · 11.416★ · último push 2026-08-31 (comprobado por
API de GitHub el 2026-09-01)

```bash
pip install datasette sqlite-utils
```

```bash
# de CSV a base consultable, y a sitio, en dos ordenes
sqlite-utils insert datos.db ventas entrada.csv --csv --detect-types
datasette datos.db                      # http://localhost:8001

# publicar solo lectura, con las consultas caras acotadas
datasette datos.db --setting sql_time_limit_ms 3000 --setting max_returned_rows 2000
```

```bash
# y la parte que lo hace util para un agente: la misma consulta, en JSON
curl -s "http://localhost:8001/datos.json?sql=select+categoria,sum(importe)+t+from+ventas+group+by+1"
```

Su hueco es el que hay **antes** de decidir qué informe hacer: alguien manda un fichero y hay que
mirarlo, filtrarlo, ordenarlo y enseñárselo a otro sin escribir nada. Cada tabla, cada filtro y cada
consulta tienen su propia URL, y todas responden también en JSON — así que lo mismo que abre una
persona lo consulta un agente sin volcar el fichero entero al contexto.

Frontera con sus dos vecinos, y es la que decide: `evidence` cuando el informe se **manda** ya
compuesto, `streamlit` cuando hay que **tocar un control** y ver el resultado, y esto cuando lo que
hace falta es **mirar el dato en crudo** sin haber decidido todavía qué se quiere contar. Gana a
abrirlo en una hoja de cálculo —que es lo que se hace de verdad— porque la hoja convierte tipos por su
cuenta y no deja compartir una consulta, solo un fichero.

Y lo que no hace bien:

- **Es SQLite, no un motor analítico.** Para agregar sobre Parquet grandes manda `duckdb`; aquí el
  caso es un fichero mediano que hay que inspeccionar y compartir.
- **No tiene autenticación en el núcleo.** Publicado tal cual, cualquiera con el enlace ejecuta SQL
  arbitrario contra esa base: solo lectura, sí, pero lectura de todo. Hay complementos de permisos, y
  detrás siempre va un proxy con TLS.
- **Y por eso mismo, el aviso que evita el disgusto: lo que subes se lee entero.** Las columnas que no
  deben salir de la agencia se quitan de la base ANTES de servirla, no se ocultan en la vista.
- `sql_time_limit_ms` existe por algo: sin él, una consulta mal escrita bloquea el proceso.
