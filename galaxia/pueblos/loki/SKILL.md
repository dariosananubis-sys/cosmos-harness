---
cosmos: pueblo
nombre: loki
padre: infraestructura/vigilancia
resumen: Almacen de logs que indexa solo etiquetas, no el texto; se consulta y pinta desde grafana.
---

https://github.com/grafana/loki · AGPL-3.0 · 28.830★ · último push 2026-09-03 (comprobado 2026-09-03, `.../commits/HEAD.atom`)

```bash
brew install loki promtail logcli
loki -config.file=RUTA/AL/PROYECTO/loki-config.yaml
```

```bash
# promtail manda logs de ficheros a loki con unas pocas etiquetas: config real, escrita a fichero
cat > promtail-config.yaml <<'EOF'
server: {http_listen_port: 9080}
positions: {filename: /tmp/positions.yaml}
clients: [{url: http://localhost:3100/loki/api/v1/push}]
scrape_configs:
  - job_name: app
    static_configs:
      - targets: [localhost]
        labels: {job: mi-app, __path__: RUTA/AL/PROYECTO/*.log}
EOF

promtail -config.file=promtail-config.yaml &

# consulta LogQL desde grafana o logcli (instalado arriba): solo lineas de error, ultima hora
logcli query '{job="mi-app"} |= "ERROR"' --since=1h
```

Es el equivalente de `victoriametrics` pero para **logs**, no métricas, y comparten filosofía:
igual que Prometheus indexa toda la serie, un ELK indexa el texto completo de cada línea — caro en
disco y en CPU. `loki` solo indexa las **etiquetas** (servicio, host, entorno) y guarda el texto
comprimido sin indexar; la búsqueda de texto (`|=`, regex) se hace al leer, no al escribir. Gana a
Elasticsearch en coste de operación para un volumen moderado de logs; pierde en búsqueda de texto
libre muy compleja sobre históricos grandes, donde un índice invertido real sigue siendo más rápido.

Ojo: si se le mete demasiada variedad como etiqueta (un `request_id` único por línea, por
ejemplo) explota en número de streams y el rendimiento se degrada mucho — la etiqueta tiene que
ser de **baja cardinalidad**. Sin `grafana` delante para explorar, `logcli` es funcional pero
incómodo para exploración libre. Y como `victoriametrics`, sin retención y purga configuradas el
disco crece sin límite.
