---
cosmos: pueblo
nombre: grafana
padre: infraestructura/vigilancia
resumen: Dibuja paneles sobre lo que victoriametrics guarda; el visor, no el almacen de metricas.
---

https://github.com/grafana/grafana · AGPL-3.0 · 76.559★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
brew install grafana
brew services start grafana   # UI en http://localhost:3000, admin/admin la primera vez
```

```bash
# datasource de ejemplo, aprovisionado de verdad al arrancar (sin pasar por la UI)
cat > "$(brew --prefix)/etc/grafana/provisioning/datasources/metricas.yaml" <<'EOF'
apiVersion: 1
datasources:
  - name: metricas
    type: prometheus
    url: http://localhost:8428   # puerto por defecto de victoriametrics
    access: proxy
EOF

brew services restart grafana
curl -s -u admin:admin http://localhost:3000/api/datasources/name/metricas   # confirma el alta
```

Frontera con `victoriametrics`, que ya está en este país: aquel **guarda** las series temporales
(scrape, almacenamiento comprimido, motor de consulta PromQL), `grafana` **las dibuja** — paneles,
alertas visuales, dashboards compartibles — y no guarda ningún dato propio de métricas. Son dos
capas del mismo stack, no rivales: sin un almacén detrás, `grafana` no tiene qué pintar. Gana a
construir un dashboard a medida en que ya trae cientos de paneles importables de la comunidad y
soporta más de 150 fuentes de datos (Prometheus, Loki, bases SQL, APIs) desde un único panel.

Ojo: la licencia es **AGPL-3.0 desde 2021** (antes Apache-2.0): si se ofrece Grafana modificado
como servicio a terceros, la AGPL obliga a publicar esos cambios — para uso interno normal no
afecta. Un dashboard bonito con datos mal etiquetados en origen (cardinalidad explosiva, nombres
inconsistentes) no se arregla desde Grafana: el problema de calidad vive en la fuente, no aquí.
