---
cosmos: pueblo
nombre: vector
padre: infraestructura/vigilancia
resumen: Pipeline de observabilidad en Rust; recoge, transforma y reparte logs/metricas hacia loki y mas.
---

https://github.com/vectordotdev/vector · MPL-2.0 · 22.509★ · último push 2026-09-02 (comprobado 2026-09-03)

```bash
brew tap vectordotdev/brew && brew install vector
```

```bash
# vector.yaml minimo, REAL y ejecutable: genera logs de muestra y los filtra por consola
# (sustituye la fuente 'demo_logs' por 'file' + include: ["RUTA/AL/PROYECTO/*.log"] en produccion,
# y el sink 'console' por 'loki' + endpoint: http://localhost:3100 para mandarlo de verdad)
cat > vector.yaml <<'EOF'
sources:
  app_logs:
    type: demo_logs
    format: json
    interval: 1
transforms:
  solo_error:
    type: filter
    inputs: [app_logs]
    condition: '.message contains "error"'
sinks:
  a_consola:
    type: console
    inputs: [solo_error]
    encoding:
      codec: json
EOF

vector validate vector.yaml   # comprueba el pipeline antes de arrancar
vector --config vector.yaml   # imprime por consola solo las lineas que casan el filtro
```

Es el reparto que falta entre "algo genera logs/métricas" y "`loki`/`victoriametrics` las
reciben": en vez de que cada aplicación hable directo con cada backend, `vector` centraliza el
pipeline (recoger, parsear, filtrar, enriquecer, enrutar) una sola vez para todos los orígenes.
Gana a Logstash/Fluentd en rendimiento — su motor en Rust procesa varios órdenes de magnitud más
eventos por segundo con una fracción de su RAM — y su lenguaje de transformación (VRL) es más
predecible que un DSL basado en plugins sueltos.

Ojo: no es un almacén — sin un `sink` configurado hacia `loki`, `victoriametrics` o similar, los
datos que procesa se pierden. Una transformación VRL mal escrita puede descartar eventos en
silencio si el `condition` no cubre el caso real: `vector tap` deja ver el flujo en vivo para
depurarlo. Y como cualquier pipeline en el camino crítico de logs, si se cae, el productor que
escribe hacia él necesita su propio buffer o pierde eventos mientras tanto.
