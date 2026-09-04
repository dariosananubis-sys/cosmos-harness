---
cosmos: pueblo
nombre: rill
padre: analitica/cuadros-de-mando
resumen: Cuadro de mando explorable en un solo binario, con la metrica definida una vez en un fichero.
---

https://github.com/rilldata/rill · Apache-2.0 · 2.856★ · último push 2026-09-01 (comprobado por API
de GitHub el 2026-09-01)

```bash
curl -fsSL https://rill.sh | sh          # o: brew install rilldata/tap/rill
```

```yaml
# metrics/ventas.yaml — la definicion unica de cada metrica
version: 1
type: metrics_view
model: ventas
timeseries: fecha
dimensions:
  - column: categoria
  - column: pais
measures:
  - name: ingresos
    expression: SUM(importe)
    format_preset: currency_eur
  - name: ticket_medio
    expression: SUM(importe) / NULLIF(COUNT(DISTINCT pedido_id), 0)
```

```bash
rill start .        # http://localhost:9009, con DuckDB embebido y recarga al guardar
```

El fallo que resuelve no es de gráficos, es de gobierno: **la misma métrica calculada en dos sitios
da dos números**, y a partir de ahí nadie se fía del panel. Aquí `ticket_medio` se escribe una vez en
un fichero versionado y todo el panel la consume de ahí; cambiarla es un diff que se revisa.

Gana a `metabase/metabase` y a `apache/superset`, las dos plataformas con servidor que ya quedaron
descartadas en este árbol por peso, exactamente por eso: aquí no hay JVM, ni Postgres, ni Redis, ni un
servicio permanente — es un binario con DuckDB dentro. Y gana a `evidence` cuando lo que hace falta es
**explorar** —cortar por dimensión, cambiar la ventana temporal, comparar con el periodo anterior— en
vez de leer un informe ya compuesto; para mandar el informe, sigue ganando aquel.

Y lo que no hace bien:

- **La capa de métricas es el trabajo, y hay que hacerlo.** Sin los ficheros de definición esto es un
  visor bonito de tablas; el valor entero está en escribirlos, y eso lleva tiempo.
- **La exploración carga la vista en memoria.** Con DuckDB por debajo aguanta mucho más de lo que
  parece, pero un modelo sin filtro de fechas sobre años de datos se nota cuando la memoria anda justa — se acota en el
  modelo, no en el panel.
- **`rill deploy` sube a la nube del fabricante, que es su producto de pago.** Todo lo de arriba corre
  en local sin cuenta ni tarjeta; el despliegue alojado es otra cosa y no se contrata sin orden.
- Proyecto joven al lado de sus rivales (2.856 estrellas frente a decenas de miles): el formato de los
  ficheros de definición ha cambiado entre versiones mayores. Fijar la versión y leer las notas antes
  de actualizar.

Ojo: el instalador por `curl | sh` ejecuta código remoto sin revisar; para producción, leer el guion antes — `brew install rilldata/tap/rill` es la vía preferible.
