---
cosmos: pueblo
nombre: scrapy
padre: extraccion/fuentes-web
resumen: Framework de rastreo con reintentos, tuberias y exportadores para trabajos grandes y repetidos.
---

https://github.com/scrapy/scrapy · BSD-3-Clause · 64.154★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
pip install scrapy
scrapy startproject catalogo && cd catalogo
scrapy genspider fichas example.com
scrapy crawl fichas -O /tmp/fichas.json -s AUTOTHROTTLE_ENABLED=1
```

Cuando el trabajo es un sitio entero y periódico, no una página: spiders, middlewares, tuberías,
exportadores, control de concurrencia y `AutoThrottle` (ajusta la tasa a la latencia del servidor).
`ROBOTSTXT_OBEY = True` viene en la plantilla de `startproject`, así que es respetuoso por defecto y
no por disciplina.

Gana a `unclecode/crawl4ai` (80.657★) por composición: aquel hace esto **más** navegador **más**
extracción de texto en un solo paquete, y aquí esas tres piezas ya están sueltas (`playwright`,
`trafilatura`) y se combinan mejor. `apify/crawlee-python` (9.483★) es la alternativa razonable si se
quiere el pool de sesiones y el almacenamiento ya montados.

Ojo, y es el fallo silencioso caro: si el HTML cambia y un selector CSS/XPath deja de encajar, **Scrapy
no lo sabe** — no valida contra esquema, y el rastreo termina «bien» con un fichero corto que nadie
mira. Se mitiga con un `ITEM_PIPELINES` que rechace items con campos obligatorios vacíos y conectando
las señales `item_dropped`/`spider_error` a una alerta. Los no-200 solo se ven si se declaran en
`handle_httpstatus_list`.
