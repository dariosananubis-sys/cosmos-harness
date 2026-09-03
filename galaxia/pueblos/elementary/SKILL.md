---
cosmos: pueblo
nombre: elementary
padre: ingenieria-datos/calidad
resumen: Pruebas de anomalia sobre la tuberia de transformacion y aviso cuando un valor se sale de su historico.
---

https://github.com/elementary-data/elementary · Apache-2.0 · 2.405★ · último push 2026-09-01
(comprobado por API de GitHub el 2026-09-01)

```bash
pip install "elementary-data[duckdb]"      # el paquete dbt va en packages.yml, ver abajo
```

```yaml
# packages.yml del proyecto de transformacion
packages:
  - package: elementary-data/elementary
    version: [">=0.16.0", "<0.20.0"]
```

```yaml
# models/schema.yml — pruebas que se comparan con el historico, no con un umbral escrito a mano
models:
  - name: ventas_diarias
    tests:
      - elementary.volume_anomalies:
          timestamp_column: fecha
      - elementary.freshness_anomalies:
          timestamp_column: fecha
    columns:
      - name: importe
        tests:
          - elementary.column_anomalies:
              column_anomalies: [null_count, average, zero_count]
```

```bash
dbt test
edr report            # informe HTML local con lo que fallo y su serie historica
edr monitor           # envia el aviso al canal configurado
```

Las pruebas de `dbt test` responden sí o no contra una regla fija —único, no nulo, valores
aceptados—, y eso no ve el fallo más común de un cuadro de mando: que el número **siga siendo válido y
haya cambiado de escala**. Un origen que dejó de enviar la mitad de las filas pasa todas las pruebas
declarativas. Esto guarda el histórico de cada prueba en el propio almacén y avisa cuando el volumen,
la frescura o la media de una columna se salen de su comportamiento anterior.

Gana a montar la misma vigilancia con vistas y una consulta programada, que es lo que se acaba
haciendo: aquello es código propio que nadie mantiene y que no guarda serie histórica. Y frente a
`soda-core`, el rival directo de contratos de datos, entra este porque aquel está bajo **Elastic
License 2.0** —usable pero no libre— y porque este vive dentro del proyecto de `dbt-core` que ya
existe, sin una segunda definición de las mismas tablas.

Y lo que no hace bien:

- **Necesita histórico para servir.** Las primeras ejecuciones no tienen contra qué comparar y no
  detectan nada; hasta que no hay unos cuantos días de datos, esto es decorativo.
- **Vive atado a `dbt-core`.** Sin proyecto dbt no hay pueblo: no es una herramienta suelta.
- **Escribe tablas propias en el almacén** (`elementary` como esquema aparte) y crece con cada
  ejecución. En un almacén de pago eso es coste; en `duckdb` local, disco.
- El fabricante tiene una nube de pago con el mismo nombre; `edr report` y `edr monitor` en local no
  la necesitan, pero la documentación mezcla las dos y es fácil acabar mirando la de pago.
- Las anomalías son estadística, no verdad: una campaña de rebajas dispara el volumen y sale como
  fallo. Hay que excluirlas o subir la sensibilidad, o el aviso se ignora en dos semanas.
