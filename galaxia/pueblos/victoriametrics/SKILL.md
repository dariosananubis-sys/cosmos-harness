---
cosmos: pueblo
nombre: victoriametrics
padre: infraestructura/vigilancia
resumen: Almacen de metricas compatible que aguanta series largas con poca memoria y poco disco.
---

https://github.com/VictoriaMetrics/VictoriaMetrics · Apache-2.0 · 17.629★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
brew install victoriametrics        # o el contenedor de abajo
docker run -d --name vm -p 8428:8428 \
  -v "$PWD/vm-data:/victoria-metrics-data" \
  victoriametrics/victoria-metrics:latest

# escribir una metrica y consultarla con el lenguaje estandar
curl -s -X POST 'http://localhost:8428/api/v1/import/prometheus' \
  --data-binary 'copias_correctas{maquina="taller"} 1'
curl -s 'http://localhost:8428/api/v1/query?query=copias_correctas'
```

Se elige por consumo: en una máquina pequeña, el almacén de referencia (`prometheus`) es el primero
que se queda sin memoria cuando las series se acumulan. Este aguanta series largas con bastante menos
RAM y disco, y es **compatible con el lenguaje de consulta estándar y con su API de lectura**, así
que los paneles de Grafana existentes valen sin tocarlos.

Ojo: compatible no es idéntico. `MetricsQL` es un superconjunto y algunas expresiones se comportan
distinto en los bordes (`increase` sobre contadores que se reinician, `subquery` anidada); una alerta
copiada desde Prometheus hay que **verla disparar** antes de fiarse. Y la edición empresarial
(imágenes con sufijo `-enterprise`) tiene funciones que no están en Apache-2.0: para no llevarse
sorpresas, usar la imagen sin sufijo.
