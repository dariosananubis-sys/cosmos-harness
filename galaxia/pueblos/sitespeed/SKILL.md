---
cosmos: pueblo
nombre: sitespeed
padre: visibilidad/medicion
resumen: Repite la medicion de rendimiento dia tras dia y grafica la tendencia; lighthouse audita un momento, esto seguimiento.
---

https://github.com/sitespeedio/sitespeed.io · MIT · 5.021★ · último push 2026-08-27 (comprobado
2026-09-03)

```bash
docker run --rm -v "$(pwd):/sitespeed.io" sitespeedio/sitespeed.io:latest \
  https://SITIO-DEL-ALCANCE.example --budget.configPath budget.json
```

```json
// budget.json — el build falla si se cruza el umbral, no solo se informa
{ "firstContentfulPaint": 1800, "TimeToInteractive": 3500 }
```

```bash
# guardado en Graphite/InfluxDB para ver la tendencia entre despliegues, no solo el ultimo numero
docker run --rm -v "$(pwd):/sitespeed.io" sitespeedio/sitespeed.io:latest \
  https://SITIO-DEL-ALCANCE.example --graphite.host mi-graphite.example
```

Diferente eje del mismo dato que miden `lighthouse` y `unlighthouse` (ambos en el país vecino
`web/calidad-de-sitio`): aquellos auditan **un momento** y devuelven un informe puntual; `sitespeed.io`
está pensado para correr en cada despliegue y **acumular el histórico**, así que la pregunta que
responde no es "cómo va esta URL hoy" sino "está empeorando desde el despliegue de la semana pasada".
Usa múltiples motores de navegador reales de verdad (vía Browsertime) donde `lighthouse` audita solo
sobre Chrome/Chromium.

Gana a repetir `lighthouse` a mano y guardar el JSON en una carpeta en que el presupuesto de
rendimiento (`--budget`) **falla la build** por umbral cruzado, y el panel de tendencia ya viene
resuelto contra Graphite o InfluxDB sin escribir el agregador aparte. Frente a `matomo` —el otro
vecino de este país—, la frontera es clara: aquel mide **comportamiento de visitantes reales**
(embudos, mapas de calor); esto mide **rendimiento técnico sintético**, sin usuario de por medio.

Ojo: sin un backend de series temporales configurado (Graphite/InfluxDB/Grafana), cada ejecución es
un informe suelto igual que `lighthouse` — el valor de seguimiento histórico **no viene de fábrica en
el comando mínimo**, hay que montar el almacén aparte, y eso es infraestructura permanente, no un
contenedor que se lanza y se olvida. Y como toda medición sintética: un resultado depende de la red y
la máquina donde corre el contenedor — comparar números entre una ejecución en un portátil y otra en
CI sin la misma condición de red es comparar cosas distintas.
